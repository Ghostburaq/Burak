import Anthropic from "@anthropic-ai/sdk";
import { LANGS, MODES, buildSystem, kickoff, wrapupPrompt, WRAPUP_SCHEMA } from "./prompt.js";
import { load, save, today, parseDate, applyWrapup, ankiExport, exportBackup, importBackup } from "./store.js";
import { md, plain } from "./markdown.js";
import { speak, stopSpeaking, listen, canSpeak, canListen } from "./speech.js";

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

let state = load();
let lang = state.lastLang in LANGS ? state.lastLang : "fr";
let busy = false;
let recognizer = null;
let currentStream = null;
let installEvt = null;
const isAbort = (e) => e?.name === "APIUserAbortError" || (Anthropic.APIUserAbortError && e instanceof Anthropic.APIUserAbortError);

function persist() {
  if (!save(state)) toast("Speichern im Browser fehlgeschlagen. Sicherung exportieren!");
}

function toast(text) {
  const t = $("#toast");
  t.textContent = text;
  t.hidden = false;
  clearTimeout(toast.t);
  toast.t = setTimeout(() => (t.hidden = true), 4000);
}

function download(name, text, type = "text/plain") {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// ---------- Claude ----------

function client() {
  return new Anthropic({ apiKey: state.settings.apiKey, dangerouslyAllowBrowser: true, maxRetries: 2 });
}

function baseParams() {
  const p = {
    model: state.settings.model,
    max_tokens: 32000,
    output_config: { effort: state.settings.effort },
  };
  if (state.settings.fallbacks) {
    p.betas = ["server-side-fallback-2026-07-01"];
    p.fallbacks = "default";
  }
  return p;
}

async function streamCall(params, onText) {
  const run = async () => {
    const stream = client().beta.messages.stream({ ...baseParams(), ...params });
    currentStream = stream;
    if (onText) stream.on("text", (_delta, snapshot) => onText(snapshot));
    return stream.finalMessage();
  };
  try {
    return await run();
  } catch (e) {
    // Falls das Konto die Fallback-Beta nicht kennt: einmal ohne versuchen.
    if (state.settings.fallbacks && e?.status === 400 && /fallback/i.test(e.message || "")) {
      state.settings.fallbacks = false;
      persist();
      return run();
    }
    throw e;
  }
}

function errorText(e) {
  if (!state.settings.apiKey) return "Kein API-Key hinterlegt. Unter Einstellungen eintragen.";
  if (e?.status === 401) return "API-Key ungültig (401). Unter Einstellungen prüfen.";
  if (e?.status === 429) return "Rate-Limit erreicht (429). Kurz warten und nochmals senden.";
  if (e?.status === 529 || e?.status >= 500) return `Claude ist gerade überlastet (${e.status}). Nochmals senden.`;
  return `Fehler: ${e?.message || e}`;
}

const textOf = (content) => content.filter((b) => b.type === "text").map((b) => b.text).join("\n");

// ---------- Session ----------

function startSession(mode, topic) {
  const L = state.langs[lang];
  if (!state.settings.apiKey) { openSettings(); toast("Zuerst den API-Key eintragen."); return; }
  if (!L.profil && mode !== "start") mode = "start";
  state.session = {
    lang, mode, topic,
    system: buildSystem(lang, mode, L),
    messages: [{ role: "user", content: kickoff(mode, topic) }],
    view: [],
  };
  persist();
  render();
  sendTurn();
}

async function sendTurn() {
  const s = state.session;
  busy = true;
  renderChat();
  const live = addBubble("assistant", "");
  live.classList.add("pending");
  let partial = "";
  try {
    const msg = await streamCall(
      {
        system: [{ type: "text", text: s.system, cache_control: { type: "ephemeral" } }],
        messages: s.messages,
      },
      (snap) => { partial = snap; live.querySelector(".body").innerHTML = md(snap); scrollChat(); },
    );
    s.messages.push({ role: "assistant", content: msg.content });
    let text = textOf(msg.content);
    if (msg.stop_reason === "refusal") text = (text ? text + "\n\n" : "") + "_Claude hat diese Antwort abgelehnt. Formuliere die letzte Nachricht anders._";
    if (msg.stop_reason === "max_tokens") text += "\n\n_(Antwort abgeschnitten, schreib \"weiter\".)_";
    s.view.push({ role: "assistant", text });
    persist();
    if (state.settings.autoRead) speak(plain(text), s.lang, state.settings.rate);
  } catch (e) {
    if (isAbort(e) && partial.trim()) {
      // Abgebrochene Antwort behalten, damit das Gespräch nahtlos weitergeht.
      s.messages.push({ role: "assistant", content: [{ type: "text", text: partial }] });
      s.view.push({ role: "assistant", text: `${partial}\n\n_(gestoppt)_` });
    } else {
      // Fehlgeschlagene User-Nachricht zurücknehmen, damit die Rollen sauber abwechseln.
      if (s.messages.at(-1)?.role === "user" && s.messages.length > 1) {
        const lost = s.messages.pop();
        s.view.pop();
        $("#input").value = typeof lost.content === "string" ? lost.content : "";
      } else if (s.messages.length === 1) {
        state.session = null;
      }
      toast(isAbort(e) ? "Abgebrochen." : errorText(e));
    }
    persist();
  } finally {
    busy = false;
    currentStream = null;
    render();
  }
}

function sendUser() {
  const input = $("#input");
  const text = input.value.trim();
  if (!text || busy || !state.session) return;
  stopDictation();
  if (/^stopp[.!]?$/i.test(text)) { input.value = ""; endSession(); return; }
  input.value = "";
  state.session.messages.push({ role: "user", content: text });
  state.session.view.push({ role: "user", text });
  persist();
  sendTurn();
}

function transcript(s) {
  return s.messages
    .map((m) => `${m.role === "user" ? "BURAK" : "TRAINER"}: ${typeof m.content === "string" ? m.content : textOf(m.content)}`)
    .join("\n\n");
}

async function endSession() {
  const s = state.session;
  if (!s || busy) return;
  if (s.messages.length < 3) { state.session = null; persist(); render(); toast("Session ohne Inhalt verworfen."); return; }
  busy = true;
  render();
  $("#status-line").textContent = "Nachbereitung läuft: Fehlerjournal, Wortschatz, Profil …";
  try {
    const L = state.langs[s.lang];
    const msg = await streamCall({
      messages: [{ role: "user", content: wrapupPrompt(s.lang, s.mode, L, transcript(s)) }],
      output_config: { effort: "low", format: { type: "json_schema", schema: WRAPUP_SCHEMA } },
    });
    if (msg.stop_reason === "refusal") throw new Error("Nachbereitung abgelehnt");
    const w = JSON.parse(textOf(msg.content));
    applyWrapup(L, s.mode, w);
    state.session = null;
    persist();
    busy = false;
    render();
    showSummary(s.lang, w);
  } catch (e) {
    busy = false;
    render();
    toast(`Nachbereitung fehlgeschlagen, Session bleibt offen. ${errorText(e)}`);
  }
}

function discardSession() {
  if (!confirm("Session ohne Nachbereitung verwerfen?")) return;
  state.session = null;
  persist();
  render();
}

// ---------- Diktat ----------

function toggleDictation() {
  if (recognizer) { stopDictation(); return; }
  const input = $("#input");
  const before = input.value ? input.value.trim() + " " : "";
  recognizer = listen(state.session?.lang || lang, (t) => { input.value = before + t; }, () => { recognizer = null; $("#mic")?.classList.remove("on"); });
  if (recognizer) $("#mic").classList.add("on");
}

function stopDictation() {
  if (recognizer) { recognizer.stop(); recognizer = null; $("#mic")?.classList.remove("on"); }
}

// ---------- Rendering ----------

function render() {
  document.querySelectorAll(".lang-tab").forEach((b) => {
    b.setAttribute("aria-selected", b.dataset.lang === (state.session?.lang || lang));
    b.disabled = !!state.session;
  });
  const inSession = !!state.session;
  $("#home").hidden = inSession;
  $("#chat").hidden = !inSession;
  if (inSession) renderChat();
  else renderHome();
}

function renderHome() {
  const L = state.langs[lang];
  const p = L.profil;
  const name = LANGS[lang].name;
  const offen = L.fehler.length;
  $("#profile").innerHTML = p
    ? `<div class="stats">
        <div><span>Niveau</span><b>${esc(p.niveau || "offen")}</b></div>
        <div><span>Plan-Tag</span><b>${L.plan ? esc(p.planTag) + " / 90" : "kein Plan"}</b></div>
        <div><span>Wortschatz</span><b>${L.wortschatz.length}</b></div>
        <div><span>Offene Fehler</span><b>${offen}</b></div>
      </div>
      <p class="muted">Ziel: ${esc(p.ziel || "noch offen")} · Letzte Session: ${esc(p.letzteSession || "keine")}</p>`
    : `<div class="empty"><p><b>${name}</b> ist noch nicht eingestuft.</p><p class="muted">Die Einstufung dauert rund 10 Minuten: Ziel, Zeitbudget, ein paar Aufgaben. Danach gibt es einen 90-Tage-Plan.</p></div>`;

  const modes = p ? MODES : MODES.filter(([m]) => m === "start");
  const main = !p ? "start" : L.plan ? "heute" : "plan";
  $("#modes").innerHTML = modes
    .map(([m, label, hint]) => `<button class="mode${m === main ? " primary" : ""}" data-mode="${m}"><b>${label}</b><span>${hint}</span></button>`)
    .join("");
  renderBanner();
  $("#topic-row").hidden = !p;
  if (p && !L.plan) $("#hint").innerHTML = `Noch kein Plan. Tipp: zuerst <b>90-Tage-Plan</b>.`;
  else $("#hint").textContent = "";
}

function daysSince(dateStr) {
  const d = parseDate(dateStr);
  return d ? Math.floor((Date.now() - d.getTime()) / 864e5) : null;
}

function renderBanner() {
  const b = $("#banner");
  const hasData = Object.values(state.langs).some((L) => L.profil || L.wortschatz.length);
  const days = daysSince(state.lastBackup);
  if (!hasData || (days !== null && days < 7)) { b.hidden = true; return; }
  b.hidden = false;
  b.innerHTML = `<span>${days === null ? "Noch keine Sicherung." : `Letzte Sicherung vor ${days} Tagen.`} Der Fortschritt liegt nur in diesem Browser.</span><button id="banner-backup">Jetzt sichern</button>`;
}

function doBackup() {
  download(`sprachtrainer_sicherung_${today()}.json`, exportBackup(state), "application/json");
  state.lastBackup = today();
  persist();
  if (!state.session) renderBanner();
}

function bubbleHtml(role, text) {
  const tools = role === "assistant" && canSpeak ? `<button class="say" title="Vorlesen" aria-label="Vorlesen">▶</button>` : "";
  return `<div class="body">${role === "assistant" ? md(text) : esc(text).replace(/\n/g, "<br>")}</div>${tools}`;
}

function addBubble(role, text) {
  const el = document.createElement("div");
  el.className = `msg ${role}`;
  el.innerHTML = bubbleHtml(role, text);
  el.dataset.text = text;
  $("#log").appendChild(el);
  scrollChat();
  return el;
}

function renderChat() {
  const s = state.session;
  const L = LANGS[s.lang];
  const modeLabel = (MODES.find(([m]) => m === s.mode) || [, s.mode])[1];
  $("#chat-title").textContent = `${L.name} · ${modeLabel}${s.topic ? " · " + s.topic : ""}`;
  $("#log").innerHTML = "";
  for (const v of s.view) addBubble(v.role, v.text);
  $("#send").hidden = busy;
  $("#stop").hidden = !busy;
  $("#end").disabled = busy;
  $("#mic").hidden = !canListen;
  $("#status-line").textContent = busy ? "Trainer schreibt …" : "";
}

function scrollChat() {
  const log = $("#log");
  log.scrollTop = log.scrollHeight;
}

function showSummary(l, w) {
  const neuF = w.fehler_neu.length, neuW = w.wortschatz_neu.length;
  $("#summary-body").innerHTML = `${md(w.rueckmeldung)}<p class="muted">${LANGS[l].name}: ${neuF} neue Fehler im Journal, ${neuW} neue Einheiten im Wortschatz${w.test.resultat_prozent >= 0 ? `, Test ${w.test.resultat_prozent}%` : ""}.</p>`;
  $("#summary").showModal();
}

function renderStatus() {
  const rows = Object.entries(LANGS).map(([k, l]) => {
    const L = state.langs[k];
    const cutoff = Date.now() - 14 * 864e5;
    const sessions = L.log.filter((x) => (parseDate(x.datum)?.getTime() || 0) >= cutoff).length;
    const t = L.tests.at(-1);
    return `<tr><td>${l.name}</td><td>${esc(L.profil?.niveau || "–")}</td><td>${L.plan ? esc(L.profil?.planTag) : "–"}</td><td>${sessions}</td><td>${L.wortschatz.length}</td><td>${t ? `${t.resultat}% (${esc(t.datum)})` : "–"}</td></tr>`;
  });
  const top = Object.entries(LANGS)
    .filter(([k]) => state.langs[k].fehler.length)
    .map(([k, l]) => {
      const f = [...state.langs[k].fehler].sort((a, b) => b.zaehler - a.zaehler).slice(0, 5);
      return `<h4>${l.name}: Top-Fehler</h4><ul>${f.map((x) => `<li>${esc(x.zaehler)}× <del>${esc(x.falsch)}</del> → <b>${esc(x.richtig)}</b> <span class="muted">${esc(x.regel)}</span></li>`).join("")}</ul>`;
    })
    .join("");
  $("#status-body").innerHTML = `<div class="tbl"><table><thead><tr><th>Sprache</th><th>Niveau</th><th>Plan-Tag</th><th>Sessions 14 T.</th><th>Wortschatz</th><th>Letzter Test</th></tr></thead><tbody>${rows.join("")}</tbody></table></div>${top || '<p class="muted">Noch keine Fehler im Journal.</p>'}
  <div class="row-btns">${Object.entries(LANGS).filter(([k]) => state.langs[k].wortschatz.length).map(([k, l]) => `<button data-anki="${k}">Anki-Export ${l.short}</button>`).join("")}
    <button data-plan="${lang}">Plan ${LANGS[lang].short} anzeigen</button></div>`;
}

function openSettings() {
  const s = state.settings;
  $("#set-key").value = s.apiKey;
  $("#set-model").value = s.model;
  $("#set-effort").value = s.effort;
  $("#set-rate").value = s.rate;
  $("#set-auto").checked = s.autoRead;
  updateInstallUi();
  updatePersistUi();
  $("#settings").showModal();
}

// ---------- Events ----------

document.addEventListener("click", (e) => {
  const t = e.target.closest("button");
  if (!t) return;
  if (t.id === "banner-backup") doBackup();
  else if (t.classList.contains("lang-tab")) { lang = t.dataset.lang; state.lastLang = lang; persist(); render(); }
  else if (t.dataset.mode) startSession(t.dataset.mode, $("#topic").value.trim());
  else if (t.classList.contains("say")) speak(plain(t.closest(".msg").dataset.text), state.session?.lang || lang, state.settings.rate);
  else if (t.dataset.anki) {
    const res = ankiExport(state.langs[t.dataset.anki]);
    if (!res.count) { toast("Keine neuen Einträge seit dem letzten Export."); return; }
    persist();
    download(`anki_${t.dataset.anki}_${today()}.txt`, res.text);
    toast(`${res.count} Karten exportiert. In Anki: Datei > Importieren.`);
  } else if (t.dataset.plan) {
    const L = state.langs[t.dataset.plan];
    $("#status-body").innerHTML = L.plan ? md(L.plan) : "<p>Noch kein Plan.</p>";
  }
});

$("#send").addEventListener("click", sendUser);
$("#input").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); sendUser(); }
});
$("#mic").addEventListener("click", toggleDictation);
$("#end").addEventListener("click", endSession);
$("#discard").addEventListener("click", discardSession);
$("#open-settings").addEventListener("click", openSettings);
$("#open-status").addEventListener("click", () => { renderStatus(); $("#status").showModal(); });
$("#settings-form").addEventListener("submit", () => {
  const s = state.settings;
  s.apiKey = $("#set-key").value.trim();
  s.model = $("#set-model").value.trim() || "claude-opus-5-5";
  s.effort = $("#set-effort").value;
  s.rate = Number($("#set-rate").value) || 1;
  s.autoRead = $("#set-auto").checked;
  s.fallbacks = true;
  persist();
  toast("Einstellungen gespeichert.");
});
$("#backup-export").addEventListener("click", doBackup);
$("#stop").addEventListener("click", () => currentStream?.abort());
$("#install").addEventListener("click", async () => {
  if (!installEvt) return;
  installEvt.prompt();
  await installEvt.userChoice.catch(() => {});
  installEvt = null;
  updateInstallUi();
});
$("#backup-import").addEventListener("change", async (e) => {
  const f = e.target.files[0];
  if (!f) return;
  try {
    if (!confirm("Sicherung einlesen? Der aktuelle Stand im Browser wird ersetzt.")) return;
    state = importBackup(state, await f.text());
    persist();
    render();
    toast("Sicherung eingelesen.");
  } catch (err) {
    toast(`Import fehlgeschlagen: ${err.message}`);
  } finally {
    e.target.value = "";
  }
});
window.addEventListener("pagehide", stopSpeaking);

// ---------- App-Installation, Speicherschutz, Offline ----------

const standalone = () => matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); installEvt = e; updateInstallUi(); });
window.addEventListener("appinstalled", () => { installEvt = null; updateInstallUi(); toast("App installiert."); });

function updateInstallUi() {
  const btn = $("#install");
  const txt = $("#install-text");
  btn.hidden = !installEvt;
  if (standalone()) txt.textContent = "Du nutzt gerade die installierte App.";
  else if (installEvt) txt.textContent = "Die App läuft dann in einem eigenen Fenster, hat ein Icon und startet auch offline (Profil, Status, Sicherung).";
  else if (isIos) txt.textContent = "iPhone und iPad: in Safari auf Teilen tippen, dann «Zum Home-Bildschirm».";
  else txt.textContent = "Installieren: in Chrome oder Edge das Installations-Symbol in der Adresszeile nutzen, auf Android im Menü «App installieren».";
}

async function updatePersistUi() {
  const el = $("#persist-text");
  try {
    let ok = await navigator.storage?.persisted?.();
    if (!ok) ok = await navigator.storage?.persist?.();
    el.textContent = ok ? "Speicher ist vom Browser als dauerhaft markiert." : "Der Browser kann den Speicher bei Platzmangel löschen. Sicherung exportieren.";
  } catch {
    el.textContent = "";
  }
}

if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}

// Deep-Link aus den App-Verknüpfungen: ?lang=zh
const qLang = new URLSearchParams(location.search).get("lang");
if (qLang && qLang in LANGS) { lang = qLang; state.lastLang = lang; }

$("#tabs").innerHTML = Object.entries(LANGS).map(([k, l]) => `<button class="lang-tab" role="tab" data-lang="${k}" title="${l.name}">${l.short}</button>`).join("");
render();
if (!state.settings.apiKey) openSettings();
