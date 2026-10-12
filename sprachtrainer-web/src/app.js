import Anthropic from "@anthropic-ai/sdk";
import { LANGS, MODES, buildSystem, kickoff, wrapupPrompt, WRAPUP_SCHEMA } from "./prompt.js";
import { load, save, today, parseDate, applyWrapup, ankiExport, exportBackup, importBackup } from "./store.js";
import { md, plain } from "./markdown.js";
import { speak, stopSpeaking, listen, canSpeak, canListen } from "./speech.js";
import { fetchBlob, decryptKey } from "./crypto.js";

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

let state = load();
let lang = state.lastLang in LANGS ? state.lastLang : "fr";
let busy = false;
let busyKind = null; // "reply" | "wrapup"
let recognizer = null;
let currentStream = null;
let installEvt = null;
let keyBlob = null;

const isAbort = (e) => e?.name === "APIUserAbortError" || (Anthropic.APIUserAbortError && e instanceof Anthropic.APIUserAbortError);
const finePointer = matchMedia("(pointer: fine)").matches;

function persist() {
  if (!save(state)) toast("Speichern im Browser fehlgeschlagen. Sicherung exportieren!");
}

function toast(text, ms = 4500) {
  const t = $("#toast");
  t.textContent = text;
  t.hidden = false;
  try { t.showPopover?.(); } catch { /* schon offen */ }
  clearTimeout(toast.t);
  toast.t = setTimeout(() => {
    try { t.hidePopover?.(); } catch { /* ignorieren */ }
    t.hidden = true;
  }, ms);
}

function download(name, text, type = "text/plain") {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
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
  if (e?.status === 401) return "API-Key ungültig (401). Unter Einstellungen den Key entfernen und neu entsperren.";
  if (e?.status === 403) return "Zugriff verweigert (403). Key oder Modell in der Anthropic-Console prüfen.";
  if (e?.status === 429) return "Rate-Limit erreicht (429). Kurz warten und nochmals senden.";
  if (e?.status === 529 || e?.status >= 500) return `Claude ist gerade überlastet (${e.status}). Nochmals senden.`;
  if (e instanceof TypeError || /network|fetch/i.test(e?.message || "")) return "Keine Verbindung zu Claude. Internet prüfen.";
  return `Fehler: ${e?.message || e}`;
}

const textOf = (content) => content.filter((b) => b.type === "text").map((b) => b.text).join("\n");

// ---------- Zugang (verschlüsselter Key) ----------

async function ensureAccess() {
  if (state.settings.apiKey) return true;
  keyBlob ||= await fetchBlob();
  if (keyBlob) openUnlock();
  else openSettings();
  return false;
}

function openUnlock() {
  $("#unlock-err").textContent = "";
  $("#unlock-pass").value = "";
  if (!$("#unlock").open) $("#unlock").showModal();
  setTimeout(() => $("#unlock-pass").focus(), 50);
}

async function submitUnlock(e) {
  e.preventDefault();
  const btn = $("#unlock-go");
  const err = $("#unlock-err");
  const pass = $("#unlock-pass").value;
  if (!pass.trim()) { err.textContent = "Bitte Passwort eingeben."; return; }
  btn.disabled = true;
  btn.textContent = "Prüfe …";
  err.textContent = "";
  try {
    state.settings.apiKey = await decryptKey(keyBlob, pass);
    persist();
    $("#unlock").close();
    $("#unlock-pass").value = "";
    toast("Entsperrt. Los geht's.");
  } catch {
    err.textContent = "Passwort stimmt nicht.";
  } finally {
    btn.disabled = false;
    btn.textContent = "Entsperren";
  }
}

// ---------- Session ----------

async function startSession(mode, topic) {
  if (!(await ensureAccess())) return;
  const L = state.langs[lang];
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

function finishBubble(el, text) {
  el.classList.remove("pending");
  el.dataset.text = text;
  el.innerHTML = bubbleHtml("assistant", text);
  scrollChat();
}

async function sendTurn() {
  const s = state.session;
  busy = true;
  busyKind = "reply";
  updateChat();
  const live = addBubble("assistant", "", true);
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
    finishBubble(live, text);
    persist();
    if (state.settings.autoRead) speak(plain(text), s.lang, state.settings.rate);
  } catch (e) {
    if (isAbort(e) && partial.trim()) {
      // Abgebrochene Antwort behalten, damit das Gespräch nahtlos weitergeht.
      s.messages.push({ role: "assistant", content: [{ type: "text", text: partial }] });
      const text = `${partial}\n\n_(gestoppt)_`;
      s.view.push({ role: "assistant", text });
      finishBubble(live, text);
    } else {
      live.remove();
      // Fehlgeschlagene User-Nachricht zurücknehmen, damit die Rollen sauber abwechseln.
      if (s.messages.at(-1)?.role === "user" && s.messages.length > 1) {
        const lost = s.messages.pop();
        s.view.pop();
        [...document.querySelectorAll("#log .msg.user")].at(-1)?.remove();
        $("#input").value = typeof lost.content === "string" ? lost.content : "";
        autosize();
      } else if (s.messages.length === 1) {
        state.session = null;
      }
      toast(isAbort(e) ? "Abgebrochen." : errorText(e));
    }
    persist();
  } finally {
    busy = false;
    busyKind = null;
    currentStream = null;
    if (state.session) updateChat();
    else render();
  }
}

function sendUser() {
  const input = $("#input");
  const text = input.value.trim();
  if (!text || busy || !state.session) return;
  stopDictation();
  if (/^stopp[.!]?$/i.test(text)) { input.value = ""; autosize(); endSession(); return; }
  input.value = "";
  autosize();
  state.session.messages.push({ role: "user", content: text });
  state.session.view.push({ role: "user", text });
  addBubble("user", text);
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
  busyKind = "wrapup";
  updateChat("Nachbereitung läuft: Fehlerjournal, Wortschatz, Profil …");
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
    busyKind = null;
    render();
    showSummary(s.lang, w);
  } catch (e) {
    busy = false;
    busyKind = null;
    updateChat();
    toast(`Nachbereitung fehlgeschlagen, die Session bleibt offen. ${errorText(e)}`);
  } finally {
    currentStream = null;
  }
}

function discardSession() {
  if (!confirm("Session ohne Nachbereitung verwerfen?")) return;
  state.session = null;
  persist();
  render();
}

// Nach Neuladen mitten in einer Antwort: sauber weitermachen statt hängen bleiben.
function recoverSession() {
  const s = state.session;
  if (!s) return;
  if (s.messages.at(-1)?.role !== "user") return;
  if (s.messages.length === 1) { sendTurn(); return; }
  const lost = s.messages.pop();
  s.view.pop();
  persist();
  render();
  $("#input").value = typeof lost.content === "string" ? lost.content : "";
  autosize();
  toast("Die letzte Antwort wurde unterbrochen. Deine Nachricht steht wieder im Eingabefeld.");
}

// ---------- Diktat ----------

function toggleDictation() {
  if (recognizer) { stopDictation(); return; }
  const input = $("#input");
  const before = input.value ? input.value.trim() + " " : "";
  recognizer = listen(
    state.session?.lang || lang,
    (t) => { input.value = before + t; autosize(); },
    () => { recognizer = null; $("#mic").classList.remove("on"); },
  );
  if (recognizer) $("#mic").classList.add("on");
}

function stopDictation() {
  if (recognizer) { recognizer.stop(); recognizer = null; $("#mic").classList.remove("on"); }
}

function autosize() {
  const t = $("#input");
  t.style.height = "auto";
  t.style.height = `${Math.min(t.scrollHeight, 160)}px`;
}

// ---------- Rendering ----------

function render() {
  const inSession = !!state.session;
  document.querySelectorAll(".seg button").forEach((b) => {
    b.setAttribute("aria-selected", String(b.dataset.lang === (state.session?.lang || lang)));
    b.disabled = inSession;
  });
  $("#home").hidden = inSession;
  $("#chat").hidden = !inSession;
  if (inSession) renderChat();
  else renderHome();
}

function renderHome() {
  const L = state.langs[lang];
  const p = L.profil;
  const name = LANGS[lang].name;
  $("#profile").innerHTML = p
    ? `<div class="card-title"><b>${esc(name)}</b><span>${esc(p.varietaet || "")}</span></div>
       <div class="stats">
         <div class="stat"><span>Niveau</span><b>${esc(p.niveau || "offen")}</b></div>
         <div class="stat"><span>Plan-Tag</span><b>${L.plan ? `${esc(p.planTag)} / 90` : "kein Plan"}</b></div>
         <div class="stat"><span>Wortschatz</span><b>${L.wortschatz.length}</b></div>
         <div class="stat"><span>Offene Fehler</span><b>${L.fehler.length}</b></div>
       </div>
       <p class="note">Ziel: ${esc(p.ziel || "noch offen")}<br>Letzte Session: ${esc(p.letzteSession || "keine")}</p>`
    : `<div class="card-title"><b>${esc(name)}</b></div>
       <p>Noch nicht eingestuft.</p>
       <p class="note">Die Einstufung dauert rund 10 Minuten: Ziel, Zeitbudget, ein paar Aufgaben. Danach gibt es einen 90-Tage-Plan.</p>`;

  const modes = p ? MODES : MODES.filter(([m]) => m === "start");
  const main = !p ? "start" : L.plan ? "heute" : "plan";
  $("#modes").innerHTML = modes
    .map(([m, label, hint]) => `<button type="button" class="mode${m === main ? " primary" : ""}" data-mode="${m}"><b>${esc(label)}</b><span>${esc(hint)}</span></button>`)
    .join("");
  $("#topic-row").hidden = !p;
  const hint = $("#hint");
  hint.hidden = !(p && !L.plan);
  hint.innerHTML = hint.hidden ? "" : "Noch kein Plan. Tipp: zuerst <b>90-Tage-Plan</b>.";
  renderBanner();
}

function daysSince(dateStr) {
  const d = parseDate(dateStr);
  return d ? Math.floor((Date.now() - d.getTime()) / 864e5) : null;
}

function renderBanner() {
  const b = $("#banner");
  const hasData = Object.values(state.langs).some((L) => L.profil || L.wortschatz.length);
  const days = daysSince(state.lastBackup);
  if (!hasData || (days !== null && days < 7)) { b.hidden = true; b.innerHTML = ""; return; }
  b.hidden = false;
  b.innerHTML = `<span>${days === null ? "Noch keine Sicherung." : `Letzte Sicherung vor ${days} Tagen.`} Der Fortschritt liegt nur in diesem Browser.</span><button type="button" class="btn" id="banner-backup">Jetzt sichern</button>`;
}

function doBackup() {
  download(`sprachtrainer_sicherung_${today()}.json`, exportBackup(state), "application/json");
  state.lastBackup = today();
  persist();
  if (!state.session) renderBanner();
}

function bubbleHtml(role, text) {
  const actions = role === "assistant" && canSpeak && text ? `<div class="msg-actions"><button type="button" class="say" aria-label="Vorlesen">▶ Vorlesen</button></div>` : "";
  return `<div class="body">${role === "assistant" ? md(text) : esc(text).replace(/\n/g, "<br>")}</div>${actions}`;
}

function addBubble(role, text, pending = false) {
  const el = document.createElement("div");
  el.className = `msg ${role}${pending ? " pending" : ""}`;
  el.innerHTML = bubbleHtml(role, text);
  el.dataset.text = text;
  $("#log").appendChild(el);
  scrollChat();
  return el;
}

function renderChat() {
  const s = state.session;
  const modeLabel = (MODES.find(([m]) => m === s.mode) || [, s.mode])[1];
  $("#chat-title").textContent = `${LANGS[s.lang].name} · ${modeLabel}${s.topic ? " · " + s.topic : ""}`;
  $("#log").innerHTML = "";
  for (const v of s.view) addBubble(v.role, v.text);
  updateChat();
}

function updateChat(statusText) {
  $("#send").hidden = busy;
  $("#stop").hidden = busyKind !== "reply";
  $("#end").disabled = busy;
  $("#discard").disabled = busy;
  document.querySelectorAll(".chip").forEach((c) => (c.disabled = busy));
  $("#mic").hidden = !canListen;
  $("#status-line").textContent = statusText || (busy ? "Trainer schreibt …" : "");
}

function scrollChat() {
  const log = $("#log");
  log.scrollTop = log.scrollHeight;
}

function showSummary(l, w) {
  const neuF = w.fehler_neu.length, neuW = w.wortschatz_neu.length;
  $("#summary-body").innerHTML = `<div class="msg-plain">${md(w.rueckmeldung)}</div><p class="note">${esc(LANGS[l].name)}: ${neuF} neue Fehler im Journal, ${neuW} neue Einheiten im Wortschatz${w.test.resultat_prozent >= 0 ? `, Test ${esc(w.test.resultat_prozent)}%` : ""}.</p>`;
  $("#summary").showModal();
}

function renderStatus() {
  $("#status-title").textContent = "Status";
  const cutoff = Date.now() - 14 * 864e5;
  const cards = Object.entries(LANGS).map(([k, l]) => {
    const L = state.langs[k];
    const sessions = L.log.filter((x) => (parseDate(x.datum)?.getTime() || 0) >= cutoff).length;
    const t = L.tests.at(-1);
    return `<div class="lang-card"><h4><span>${esc(l.name)}</span><span>${esc(L.profil?.niveau || "–")}</span></h4>
      <dl><dt>Plan-Tag</dt><dd>${L.plan ? `${esc(L.profil?.planTag)} / 90` : "–"}</dd>
      <dt>Sessions (14 Tage)</dt><dd>${sessions}</dd>
      <dt>Wortschatz</dt><dd>${L.wortschatz.length}</dd>
      <dt>Letzter Test</dt><dd>${t ? `${esc(t.resultat)}%` : "–"}</dd></dl></div>`;
  }).join("");
  const top = Object.entries(LANGS)
    .filter(([k]) => state.langs[k].fehler.length)
    .map(([k, l]) => {
      const f = [...state.langs[k].fehler].sort((a, b) => b.zaehler - a.zaehler).slice(0, 5);
      return `<h4>${esc(l.name)}: häufigste Fehler</h4><ul>${f.map((x) => `<li>${esc(x.zaehler)}× <del>${esc(x.falsch)}</del> → <b>${esc(x.richtig)}</b><br><span class="note">${esc(x.regel)}</span></li>`).join("")}</ul>`;
    })
    .join("");
  const exports = Object.entries(LANGS).filter(([k]) => state.langs[k].wortschatz.length).map(([k, l]) => `<button type="button" class="btn" data-anki="${k}">Anki-Export ${esc(l.short)}</button>`).join("");
  const plans = Object.entries(LANGS).filter(([k]) => state.langs[k].plan).map(([k, l]) => `<button type="button" class="btn" data-plan="${k}">Plan ${esc(l.short)}</button>`).join("");
  $("#status-body").innerHTML = `<div class="status-grid">${cards}</div>
    <div class="errors">${top || '<p class="note">Noch keine Fehler im Journal.</p>'}</div>
    ${exports || plans ? `<div class="row">${exports}${plans}</div>` : ""}`;
}

function showPlan(k) {
  $("#status-title").textContent = `90-Tage-Plan ${LANGS[k].name}`;
  $("#status-body").innerHTML = `<div class="plan">${md(state.langs[k].plan)}</div><div class="row"><button type="button" class="btn" id="plan-back">Zurück zum Status</button></div>`;
}

function openSettings() {
  const s = state.settings;
  $("#set-key").value = "";
  $("#set-model").value = s.model;
  $("#set-effort").value = s.effort;
  $("#set-rate").value = s.rate;
  $("#set-auto").checked = s.autoRead;
  $("#key-state").textContent = s.apiKey ? `Key auf diesem Gerät gespeichert (…${s.apiKey.slice(-4)}).` : "Auf diesem Gerät ist noch kein Key gespeichert.";
  $("#key-remove").hidden = !s.apiKey;
  updateInstallUi();
  updatePersistUi();
  if (!$("#settings").open) $("#settings").showModal();
}

// ---------- Ereignisse ----------

document.addEventListener("click", (e) => {
  const t = e.target.closest("button");
  if (!t) return;
  if (t.id === "banner-backup") doBackup();
  else if (t.dataset.lang) { lang = t.dataset.lang; state.lastLang = lang; persist(); render(); }
  else if (t.dataset.mode) startSession(t.dataset.mode, $("#topic").value.trim());
  else if (t.classList.contains("say")) speak(plain(t.closest(".msg").dataset.text), state.session?.lang || lang, state.settings.rate);
  else if (t.dataset.anki) {
    const res = ankiExport(state.langs[t.dataset.anki]);
    if (!res.count) { toast("Keine neuen Einträge seit dem letzten Export."); return; }
    persist();
    download(`anki_${t.dataset.anki}_${today()}.txt`, res.text);
    toast(`${res.count} Karten exportiert. In Anki: Datei > Importieren.`);
  } else if (t.dataset.plan) showPlan(t.dataset.plan);
  else if (t.id === "plan-back") renderStatus();
  else if (t.dataset.close) $(`#${t.dataset.close}`).close();
});

$("#send").addEventListener("click", sendUser);
$("#input").addEventListener("input", autosize);
$("#input").addEventListener("keydown", (e) => {
  // Am Handy ist Enter ein Zeilenumbruch, gesendet wird mit dem Knopf.
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing && finePointer) { e.preventDefault(); sendUser(); }
});
$("#chips").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-cmd]");
  if (!b || busy) return;
  $("#input").value = b.dataset.cmd;
  sendUser();
});
$("#mic").addEventListener("click", toggleDictation);
$("#end").addEventListener("click", endSession);
$("#discard").addEventListener("click", discardSession);
$("#stop").addEventListener("click", () => currentStream?.abort());
$("#open-settings").addEventListener("click", openSettings);
$("#open-status").addEventListener("click", () => { renderStatus(); $("#status").showModal(); });
$("#unlock-form").addEventListener("submit", submitUnlock);
$("#unlock-manual").addEventListener("click", () => { $("#unlock").close(); openSettings(); });
$("#unlock").addEventListener("cancel", (e) => { if (!state.settings.apiKey) e.preventDefault(); });
$("#key-remove").addEventListener("click", () => {
  state.settings.apiKey = "";
  persist();
  $("#settings").close();
  toast("Key von diesem Gerät entfernt.");
});
$("#settings-form").addEventListener("submit", () => {
  const s = state.settings;
  const key = $("#set-key").value.trim();
  if (key) s.apiKey = key;
  s.model = $("#set-model").value.trim() || "claude-opus-5-5";
  s.effort = $("#set-effort").value;
  s.rate = Number($("#set-rate").value) || 1;
  s.autoRead = $("#set-auto").checked;
  s.fallbacks = true;
  persist();
  toast("Einstellungen gespeichert.");
});
$("#install").addEventListener("click", async () => {
  if (!installEvt) return;
  installEvt.prompt();
  await installEvt.userChoice.catch(() => {});
  installEvt = null;
  updateInstallUi();
});
$("#backup-export").addEventListener("click", doBackup);
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
  const txt = $("#install-text");
  $("#install").hidden = !installEvt;
  if (standalone()) txt.textContent = "Du nutzt gerade die installierte App.";
  else if (installEvt) txt.textContent = "Die App läuft dann in einem eigenen Fenster, hat ein Icon und startet auch offline (Profil, Status, Sicherung).";
  else if (isIos) txt.textContent = "iPhone und iPad: in Safari auf Teilen tippen, dann «Zum Home-Bildschirm».";
  else txt.textContent = "Chrome und Edge: Installations-Symbol in der Adresszeile. Android: Menü, dann «App installieren».";
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

// ---------- Start ----------

// Verknüpfung aus dem App-Symbol: ?lang=zh
const qLang = new URLSearchParams(location.search).get("lang");
if (qLang && qLang in LANGS) { lang = qLang; state.lastLang = lang; }

$("#tabs").innerHTML = Object.entries(LANGS)
  .map(([k, l]) => `<button type="button" role="tab" data-lang="${k}" title="${esc(l.name)}">${esc(l.short)}</button>`)
  .join("");
render();
autosize();
ensureAccess().then((ok) => ok && recoverSession());
