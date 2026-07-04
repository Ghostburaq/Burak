// === LinkedIn-Post-Generator – vollständig im Browser (kein Server, kein Bild-Generator) ===
// Anthropic (Texte + Websuche) direkt aus dem Browser. Bilder: nur Prompt-Generator.

const form = document.getElementById("generator-form");
const statusBox = document.getElementById("status");
const statusText = document.getElementById("status-text");
const resultBox = document.getElementById("result");
const errorBox = document.getElementById("error");
const cardsBox = document.getElementById("cards");
const sourcesBox = document.getElementById("sources");
const submitBtn = document.getElementById("submit-btn");
const regenBtn = document.getElementById("regen-btn");
const apiKeyInput = document.getElementById("apiKey");
const historySection = document.getElementById("history-section");
const historyBox = document.getElementById("history");
const clearHistoryBtn = document.getElementById("clear-history");
const themeToggle = document.getElementById("theme-toggle");
const ideasBtn = document.getElementById("ideas-btn");
const ideasBox = document.getElementById("ideas-box");
const topicInput = document.getElementById("topic");

const LINKEDIN_LIMIT = 3000;
const HISTORY_KEY = "lpg_history";
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";
let lastData = null;

// ---------- Key & Theme ----------
const savedKey = localStorage.getItem("anthropic_api_key");
if (savedKey) apiKeyInput.value = savedKey;
apiKeyInput.addEventListener("input", () =>
  localStorage.setItem("anthropic_api_key", apiKeyInput.value.trim())
);

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  themeToggle.textContent = theme === "dark" ? "☀️" : "🌙";
}
applyTheme(localStorage.getItem("theme") || "light");
themeToggle.addEventListener("click", () => {
  const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
});

// ---------- System-Prompt: menschlich, kein KI-Sound ----------
const HUMAN_SYSTEM = `Du bist ein erfahrener Ghostwriter für LinkedIn-Posts, die klingen,
als hätte sie ein echter Mensch getippt – niemals wie KI.
SO SCHREIBST DU: natürliche, gesprochene Sprache; stark variierende Satzlängen (auch mal
ein Wort. Oder ein kurzer Satz); echte Meinung; konkrete Details, Zahlen, kleine Anekdoten.
DAS VERMEIDEST DU STRIKT: Floskeln/Buzzwords (in der heutigen schnelllebigen Welt, es ist
kein Geheimnis, lass das sacken, Game-Changer, revolutionär, bahnbrechend, nahtlos, tauche
ein, entfessle); den KI-Aufbau Haken -> exakt 3 Bullet Points -> inspirierender Schluss;
übermäßige Gedankenstriche und Emojis; werbliche Sprache; erfundene Statistiken.`;

// ---------- Prompt-Bausteine ----------
const LENGTH_HINT = {
  kurz: "ca. 50–120 Wörter, knackig",
  mittel: "ca. 120–220 Wörter, ausbalanciert",
  lang: "ca. 220–350 Wörter, ausführlich",
};
const HOOK_HINT = {
  automatisch: "Wähle selbst den stärksten Aufhänger.",
  frage: "Beginne mit einer zugespitzten Frage.",
  statistik: "Beginne mit einer überraschenden, recherchierten Statistik.",
  these: "Beginne mit einer kühnen These.",
  story: "Beginne mit einem kurzen, persönlichen Story-Moment.",
  zitat: "Beginne mit einem prägnanten Zitat.",
};
const CTA_HINT = {
  automatisch: "Wähle den passendsten Call-to-Action.",
  kommentar: "Fordere zum Kommentieren auf.",
  teilen: "Bitte darum, den Beitrag zu teilen.",
  dm: "Lade zu einer DM ein.",
  link: "Leite zu einem Link/Aktion (Platzhalter [LINK]).",
  keine: "Kein expliziter Call-to-Action.",
};
const EMOJI_HINT = {
  keine: "Keine Emojis.",
  dezent: "Emojis sehr sparsam (1–3).",
  viel: "Emojis aktiv, aber nicht übertrieben.",
};
const NATURAL = {
  hoch: "Sehr menschlich und locker, persönliche Stimme, klar Anti-KI.",
  mittel: "Natürlich und professionell, lebendig, ohne KI-Floskeln.",
  fachlich: "Seriös und fachlich präzise, aber menschlich und konkret.",
};

function clampInt(v, min, max, fb) {
  const n = parseInt(v, 10);
  if (Number.isNaN(n)) return fb;
  return Math.min(max, Math.max(min, n));
}

function buildPrompt(d) {
  const lang = d.language || "Deutsch";
  const variants = clampInt(d.variants, 1, 5, 3);
  const hashtags = clampInt(d.hashtags, 0, 8, 4);
  const perspective =
    { ich: "Ich-Form (persönlich)", wir: "Wir-Form (Team/Firma)", neutral: "neutrale Perspektive" }[
      d.perspective
    ] || "Ich-Form (persönlich)";
  const draftBlock =
    d.draft && d.draft.trim()
      ? `\nWICHTIG: Optimiere DIESEN Entwurf in den Varianten (Stil, Hook, Struktur):\n"""\n${d.draft.trim()}\n"""\n`
      : "";
  const styleBlock =
    d.styleSamples && d.styleSamples.trim()
      ? `\nSTIL NACHAHMEN (Tonfall, Satzbau, Wortwahl, nicht den Inhalt):\n"""\n${d.styleSamples.trim().slice(0, 4000)}\n"""\n`
      : "";
  const research = d.webSearch
    ? `1. Recherchiere mit der Websuche aktuelle Fakten/Zahlen${d.region ? `, Fokus Markt/Region: ${d.region}` : ""}. Zitiere.`
    : `1. Nutze dein Wissen. Keine erfundenen Statistiken.`;

  return `Du bist ein erfahrener LinkedIn-Ghostwriter.

ANGABEN:
- Name: ${d.name || "(k. A.)"}
- Rolle: ${d.role || "(k. A.)"}
- Branche: ${d.industry || "(k. A.)"}
- Thema: ${d.topic || "(k. A.)"}
- Ziel: ${d.goal || "(k. A.)"}
- Zielgruppe: ${d.audience || "(k. A.)"}
- Tonfall: ${d.tone || "professionell, nahbar"}
- Sprache: ${lang}
- Markt/Region: ${d.region || "(k. A.)"}
- Perspektive: ${perspective}
${draftBlock}${styleBlock}
VORGABEN JE POST:
- Natürlichkeit: ${NATURAL[d.naturalness] || NATURAL.hoch}
- Länge: ${LENGTH_HINT[d.length] || LENGTH_HINT.mittel}
- Hook: ${HOOK_HINT[d.hook] || HOOK_HINT.automatisch}
- CTA: ${CTA_HINT[d.cta] || CTA_HINT.automatisch}
- Emojis: ${EMOJI_HINT[d.emoji] || EMOJI_HINT.dezent}
- Hashtags: ${hashtags === 0 ? "keine" : `genau ${hashtags} am Ende`}
- Kurze Absätze, gute Lesbarkeit.

AUFGABE:
${research}
2. Schreibe ${variants} unterschiedliche Varianten in "${lang}" (verschiedene Ansätze).
3. Bewerte jeden Post ehrlich und schlage eine Bild-Idee vor.
4. Danach kurze Empfehlungen.

FORMAT (Markdown), exakt:
## Post 1: <Stil-Kurzname>
<Postinhalt inkl. Hashtags>
[META] Score: <0-100> | Hook: <0-100> | Lesbarkeit: <0-100> | CTA: <0-100> | Bild: <kurze Bildidee>

(usw. bis Post ${variants}, jede mit genau EINER [META]-Zeile)

## 📊 Empfehlungen
- Welche Variante wofür (mit Begründung)
- 2 alternative Hooks
- Beste Posting-Zeit (mit Begründung)
[META] nur bei Posts. Copy-paste-fertig, keine Vorbemerkungen.`;
}

function buildIdeasPrompt(d) {
  const seed = d.topic && d.topic.trim();
  return `Du bist LinkedIn-Stratege. Profil: Rolle ${d.role || "-"}, Branche ${d.industry || "-"},
Zielgruppe ${d.audience || "-"}, Markt ${d.region || "-"}.
${seed ? `Eingabe: "${seed}". Schlage 10 verwandte, zugespitzte Themen vor.` : "Schlage 10 konkrete Themen vor."}
${d.webSearch ? "Nutze die Websuche für aktuelle Aufhänger." : "Nutze dein Wissen."}
Antworte in "${d.language || "Deutsch"}". FORMAT: nummerierte Liste, eine Idee pro Zeile, max. 90 Zeichen.`;
}

// ---------- Anthropic ----------
async function callAnthropic(apiKey, { model, max_tokens, prompt, system, useWebSearch, maxUses }) {
  const body = { model, max_tokens, system: system || HUMAN_SYSTEM, messages: [{ role: "user", content: prompt }] };
  if (useWebSearch) body.tools = [{ type: "web_search_20250305", name: "web_search", max_uses: maxUses || 5 }];
  let res;
  try {
    res = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": ANTHROPIC_VERSION,
        "anthropic-dangerous-direct-browser-access": "true",
      },
      body: JSON.stringify(body),
    });
  } catch (e) {
    throw new Error("Netzwerkfehler beim Aufruf von Anthropic: " + e.message);
  }
  const json = await res.json().catch(() => null);
  if (!res.ok) throw new Error(json?.error?.message || `Anthropic-Fehler (${res.status}).`);
  return json;
}
function textFrom(content) {
  return (content || []).filter((b) => b.type === "text").map((b) => b.text).join("\n");
}
function extractSources(content) {
  const byUrl = new Map();
  const add = (url, title) => url && !byUrl.has(url) && byUrl.set(url, { url, title: title || url });
  for (const block of content || []) {
    if (block.type === "text" && Array.isArray(block.citations)) for (const c of block.citations) add(c.url, c.title);
    if (block.type === "web_search_tool_result" && Array.isArray(block.content))
      for (const r of block.content) if (r.type === "web_search_result") add(r.url, r.title);
  }
  return [...byUrl.values()];
}
async function quickGen(prompt, max_tokens, useWebSearch) {
  const d = lastData || collectData();
  const apiKey = (d.apiKey || "").trim();
  if (!apiKey) throw new Error("Bitte zuerst den Anthropic API-Key eintragen.");
  const json = await callAnthropic(apiKey, { model: d.model || "claude-sonnet-4-6", max_tokens, prompt, useWebSearch: !!useWebSearch, maxUses: 4 });
  return { text: textFrom(json.content).trim(), sources: extractSources(json.content) };
}
function withBusy(btn, fn) {
  const orig = btn.textContent;
  btn.disabled = true;
  btn.textContent = "⏳ …";
  return Promise.resolve().then(fn).catch((err) => {
    errorBox.textContent = "⚠️ " + err.message;
    errorBox.classList.remove("hidden");
  }).finally(() => {
    btn.disabled = false;
    btn.textContent = orig;
  });
}

// ---------- Text-Helfer ----------
function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function stripMarkdown(s) {
  return s.replace(/\*\*(.+?)\*\*/g, "$1").replace(/^#{1,6}\s+/gm, "").trim();
}
function formatBody(s) {
  return escapeHtml(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}
function toUnicodeBold(str) {
  let out = "";
  for (const ch of str) {
    const c = ch.codePointAt(0);
    if (c >= 65 && c <= 90) out += String.fromCodePoint(0x1d5d4 + (c - 65));
    else if (c >= 97 && c <= 122) out += String.fromCodePoint(0x1d5ee + (c - 97));
    else if (c >= 48 && c <= 57) out += String.fromCodePoint(0x1d7ec + (c - 48));
    else out += ch;
  }
  return out;
}
function getPlain(bodyEl) {
  return bodyEl.innerText.trim();
}
function getBoldFromDom(bodyEl) {
  let out = "";
  bodyEl.childNodes.forEach((n) => {
    out += n.nodeType === 1 && n.tagName === "STRONG" ? toUnicodeBold(n.textContent) : n.textContent;
  });
  return out.trim();
}
function parseMeta(bodyText) {
  const out = [];
  let meta = null;
  for (const line of bodyText.split("\n")) {
    if (line.trim().startsWith("[META]")) {
      meta = {};
      line.replace(/^\s*\[META\]/, "").split("|").forEach((part) => {
        const i = part.indexOf(":");
        if (i > -1) meta[part.slice(0, i).trim().toLowerCase()] = part.slice(i + 1).trim();
      });
    } else out.push(line);
  }
  return { meta, clean: out.join("\n").trim() };
}
function splitSections(text) {
  const sections = [];
  let cur = null;
  for (const line of text.split("\n")) {
    const m = line.match(/^##\s+(.*)$/);
    if (m) {
      if (cur) sections.push(cur);
      cur = { title: m[1].trim(), body: [] };
    } else if (cur) cur.body.push(line);
    else if (line.trim() !== "") cur = { title: "Post", body: [line] };
  }
  if (cur) sections.push(cur);
  return sections.map((s) => ({ title: s.title, body: s.body.join("\n").trim() }));
}
function downloadText(filename, text, mime) {
  const blob = new Blob([text], { type: (mime || "text/plain") + ";charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
async function shareToLinkedIn(text) {
  try { await navigator.clipboard.writeText(text); } catch {}
  window.open("https://www.linkedin.com/feed/?shareActive=true", "_blank", "noopener");
  alert("Text kopiert ✅\nIm LinkedIn-Fenster mit Strg+V (⌘+V) einfügen.");
}
function miniButton(label, handler) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "mini";
  b.textContent = label;
  b.addEventListener("click", () => handler(b));
  return b;
}
function copyButton(label, getText) {
  return miniButton(label, async (b) => {
    await navigator.clipboard.writeText(typeof getText === "function" ? getText() : getText);
    const o = b.textContent;
    b.textContent = "✅ Kopiert!";
    setTimeout(() => (b.textContent = o), 1400);
  });
}
function scoreBadges(meta) {
  const wrap = document.createElement("div");
  wrap.className = "badges";
  for (const [label, val] of [["Score", meta.score], ["Hook", meta.hook], ["Lesbarkeit", meta.lesbarkeit], ["CTA", meta.cta]]) {
    if (val == null) continue;
    const n = parseInt(val, 10);
    const span = document.createElement("span");
    span.className = "badge " + (Number.isNaN(n) ? "mid" : n >= 80 ? "good" : n >= 60 ? "mid" : "low");
    span.textContent = `${label}: ${val}`;
    wrap.appendChild(span);
  }
  return wrap;
}

// ---------- Interaktiver Assistent + Werkzeuge ----------
const REFINE_PRESETS = [
  ["✍️ Menschlicher", "Mach den Post deutlich menschlicher und natürlicher, weg von jeder KI-Floskel."],
  ["✂️ Kürzer", "Kürze spürbar, behalte Kernaussage und Hook."],
  ["📖 Mehr Story", "Bau eine kurze, glaubwürdige persönliche Anekdote ein."],
  ["🎯 Anderer Hook", "Schreibe einen komplett anderen, stärkeren ersten Satz."],
  ["📊 Mehr Substanz", "Mach es konkreter: echte Zahlen und Beispiele."],
];
function buildRefinePrompt(postText, instruction, d) {
  return `LinkedIn-Post (Sprache "${d.language || "Deutsch"}" behalten):
"""
${postText}
"""
Überarbeite ihn nach: "${instruction}". Natürlich, menschlich, keine KI-Floskeln.
Gib NUR den Post zurück, danach:
[META] Score: <0-100> | Hook: <0-100> | Lesbarkeit: <0-100> | CTA: <0-100> | Bild: <kurze Bildidee>`;
}
async function refinePost(sec, instruction, cardEl, btn) {
  const d = lastData || collectData();
  const apiKey = (d.apiKey || "").trim();
  if (!apiKey) { showErr("Bitte zuerst den Anthropic API-Key eintragen."); return; }
  if (!instruction || !instruction.trim()) return;
  cardEl.classList.add("working");
  await withBusy(btn, async () => {
    const base = parseMeta(sec.body).clean;
    const json = await callAnthropic(apiKey, { model: d.model || "claude-sonnet-4-6", max_tokens: 2000, prompt: buildRefinePrompt(base, instruction.trim(), d) });
    const text = textFrom(json.content).trim();
    if (!text) throw new Error("Leere Antwort erhalten.");
    cardEl.replaceWith(buildCard({ title: sec.title, body: text }));
  });
  cardEl.classList.remove("working");
}
async function generateMore(sec, card, btn) {
  await withBusy(btn, async () => {
    const d = lastData || collectData();
    const base = parseMeta(sec.body).clean;
    const { text } = await quickGen(`LinkedIn-Post (Sprache "${d.language || "Deutsch"}"):
"""
${base}
"""
Schreibe EINE weitere frische Variante in derselben Richtung, inhaltlich neu (anderer Einstieg/Beispiele). Menschlich.
FORMAT:
## ${sec.title} (Variante)
<Inhalt inkl. Hashtags>
[META] Score: <0-100> | Hook: <0-100> | Lesbarkeit: <0-100> | CTA: <0-100> | Bild: <kurze Bildidee>`, 2000);
    const s = splitSections(text)[0] || { title: sec.title + " (Variante)", body: text };
    card.after(buildCard(s));
  });
}
async function translatePost(sec, lang, card, btn) {
  await withBusy(btn, async () => {
    const base = parseMeta(sec.body).clean;
    const { text } = await quickGen(`Übersetze diesen LinkedIn-Post idiomatisch nach ${lang} (Stil, Hook, Hashtags sinngemäß):
"""
${base}
"""
Nur den Post, danach:
[META] Score: <0-100> | Hook: <0-100> | Lesbarkeit: <0-100> | CTA: <0-100> | Bild: <kurze Bildidee>`, 2000);
    card.after(buildCard({ title: `${sec.title} → ${lang}`, body: text }));
  });
}
async function multiLang(sec, card, btn) {
  await withBusy(btn, async () => {
    let anchor = card;
    for (const lang of ["Englisch", "Türkisch"]) {
      const base = parseMeta(sec.body).clean;
      const { text } = await quickGen(`Übersetze idiomatisch nach ${lang}:
"""
${base}
"""
Nur den Post, danach:
[META] Score: <0-100> | Hook: <0-100> | Lesbarkeit: <0-100> | CTA: <0-100> | Bild: <kurze Bildidee>`, 2000);
      const nc = buildCard({ title: `${sec.title} → ${lang}`, body: text });
      anchor.after(nc);
      anchor = nc;
    }
  });
}
async function makeCarousel(sec, extra, btn) {
  await withBusy(btn, async () => {
    const base = parseMeta(sec.body).clean;
    const { text } = await quickGen(`Wandle diesen Post in ein Karussell aus 6 Slides: Slide 1 Titel/Hook, 2–5 je ein Kernpunkt, 6 CTA.
"""
${base}
"""
FORMAT: pro Zeile "Slide N: <Text>". Keine Einleitung.`, 1500);
    renderList(extra, "🎠 Karussell-Slides", text.split("\n").map((l) => l.trim()).filter((l) => /^slide/i.test(l)), (l) => l.replace(/^slide\s*\d+:\s*/i, ""));
  });
}
async function makeHooks(sec, extra, btn) {
  await withBusy(btn, async () => {
    const base = parseMeta(sec.body).clean;
    const { text } = await quickGen(`Schreibe 5 alternative starke Hooks (Frage, Statistik, These, Story, Kontrast) für:
"""
${base}
"""
FORMAT: nummerierte Liste, ein Hook pro Zeile.`, 800);
    renderList(extra, "📈 Hook-Varianten", text.split("\n").map((l) => l.replace(/^\s*\d+[.)]\s*/, "").trim()).filter((l) => l.length > 3));
  });
}
async function makeHashtags(sec, extra, btn) {
  await withBusy(btn, async () => {
    const d = lastData || collectData();
    const base = parseMeta(sec.body).clean;
    const { text } = await quickGen(`Optimale Hashtag-Mischung (3 groß, 3 mittel, 3 Nische) für Branche ${d.industry || "-"}, Markt ${d.region || "-"}:
"""
${base}
"""
FORMAT: nur die Hashtags in einer Zeile.`, 400, d.webSearch);
    const tags = (text.match(/#[^\s#]+/g) || []).join(" ") || text;
    renderList(extra, "🏷️ Hashtag-Vorschlag", [tags]);
  });
}
async function makeImagePrompt(sec, meta, extra, btn) {
  await withBusy(btn, async () => {
    const base = parseMeta(sec.body).clean;
    const idea = meta && meta.bild ? meta.bild : base.slice(0, 200);
    const { text } = await quickGen(`Erstelle einen detaillierten BILD-PROMPT auf Englisch für KI-Bildtools (Midjourney, DALL·E, Gemini),
passend zu diesem LinkedIn-Post. Beschreibe Motiv, Stil, Licht, Komposition, Farben, Stimmung.
Kein Text/Logo im Bild, LinkedIn-Querformat.
Bild-Idee: "${idea}"
Post:
"""
${base.slice(0, 1200)}
"""
Gib NUR den Prompt zurück (1 Absatz Englisch), am Ende " --ar 1.91:1".`, 600);
    extra.innerHTML = "<div class='extra-title'>🖼️ Bild-Prompt (kopieren &amp; in dein Bild-Tool einfügen)</div>";
    const box = document.createElement("div");
    box.className = "prompt-box";
    box.textContent = text;
    extra.appendChild(box);
    extra.appendChild(copyButton("📋 Prompt kopieren", () => text));
  });
}
function renderList(extra, title, items, transform) {
  extra.innerHTML = `<div class='extra-title'>${title}</div>`;
  items.forEach((it) => {
    const row = document.createElement("div");
    row.className = "slide-item";
    const span = document.createElement("span");
    span.textContent = it;
    row.appendChild(span);
    row.appendChild(copyButton("📋", () => (transform ? transform(it) : it)));
    extra.appendChild(row);
  });
}
function showErr(msg) {
  errorBox.textContent = "⚠️ " + msg;
  errorBox.classList.remove("hidden");
}

const TRANSLATE_LANGS = ["Englisch", "Französisch", "Italienisch", "Spanisch", "Türkisch", "Deutsch"];

// ---------- Karte ----------
function buildCard(sec, opts = {}) {
  const isReco = /empfehl|recommend|öneri/i.test(sec.title);
  const { meta, clean } = isReco ? { meta: null, clean: sec.body } : parseMeta(sec.body);

  const card = document.createElement("div");
  card.className = "post-card" + (isReco ? " reco" : "") + (opts.isBest ? " best" : "");

  const head = document.createElement("div");
  head.className = "card-head";
  const h3 = document.createElement("h3");
  h3.textContent = (isReco ? "" : "📝 ") + sec.title + (opts.isBest ? "  ⭐" : "");
  head.appendChild(h3);

  const actions = document.createElement("div");
  actions.className = "card-actions";
  const body = document.createElement("div");
  body.className = "post-body";
  body.innerHTML = formatBody(clean);

  let count = null;
  if (!isReco) {
    count = document.createElement("span");
    count.className = "char-count";
    actions.appendChild(count);
  }
  const updateCount = () => {
    if (!count) return;
    const len = getPlain(body).length;
    count.textContent = `${len} / ${LINKEDIN_LIMIT}`;
    count.classList.toggle("over", len > LINKEDIN_LIMIT);
  };

  actions.appendChild(copyButton("📋 Kopieren", () => (isReco ? stripMarkdown(clean) : getPlain(body))));
  if (!isReco) actions.appendChild(copyButton("𝗙𝗲𝘁𝘁", () => getBoldFromDom(body)));
  head.appendChild(actions);
  card.appendChild(head);

  if (meta) card.appendChild(scoreBadges(meta));

  if (!isReco) {
    body.contentEditable = "true";
    body.spellcheck = false;
    body.title = "Direkt bearbeitbar";
    body.addEventListener("input", updateCount);
  }
  card.appendChild(body);
  updateCount();

  const extra = document.createElement("div");
  extra.className = "card-extra";

  if (meta && meta.bild) {
    const idea = document.createElement("div");
    idea.className = "image-idea";
    idea.innerHTML = "🖼️ <strong>Bild-Idee:</strong> " + escapeHtml(meta.bild);
    idea.appendChild(document.createElement("br"));
    idea.appendChild(miniButton("🖼️ Bild-Prompt erstellen", (b) => makeImagePrompt(sec, meta, extra, b)));
    card.appendChild(idea);
  }

  if (!isReco) {
    // Interaktiver Assistent (sichtbar – Hauptnutzen)
    const refine = document.createElement("div");
    refine.className = "refine";
    const rt = document.createElement("div");
    rt.className = "refine-title";
    rt.textContent = "🤖 Schnell anpassen:";
    refine.appendChild(rt);
    const chips = document.createElement("div");
    chips.className = "refine-chips";
    REFINE_PRESETS.forEach(([label, instr]) => chips.appendChild(miniButton(label, (b) => refinePost(sec, instr, card, b))));
    refine.appendChild(chips);
    const row = document.createElement("div");
    row.className = "refine-row";
    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Eigene Anweisung … z. B. mehr Zahlen, Frage am Ende";
    const send = miniButton("✨ Anpassen", () => refinePost(sec, input.value, card, send));
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); refinePost(sec, input.value, card, send); } });
    row.appendChild(input);
    row.appendChild(send);
    refine.appendChild(row);
    card.appendChild(refine);

    // Erweiterte Werkzeuge (eingeklappt = übersichtlich)
    const more = document.createElement("details");
    more.className = "more";
    const sum = document.createElement("summary");
    sum.textContent = "🛠️ Mehr Werkzeuge";
    more.appendChild(sum);
    const tools = document.createElement("div");
    tools.className = "card-tools";
    tools.appendChild(miniButton("➕ Mehr davon", (b) => generateMore(sec, card, b)));
    const langSel = document.createElement("select");
    langSel.className = "lang-mini";
    TRANSLATE_LANGS.forEach((l) => { const o = document.createElement("option"); o.textContent = l; langSel.appendChild(o); });
    tools.appendChild(langSel);
    tools.appendChild(miniButton("🌍 Übersetzen", (b) => translatePost(sec, langSel.value, card, b)));
    tools.appendChild(miniButton("🌐 EN+TR", (b) => multiLang(sec, card, b)));
    tools.appendChild(miniButton("🎠 Karussell", (b) => makeCarousel(sec, extra, b)));
    tools.appendChild(miniButton("📈 Hooks", (b) => makeHooks(sec, extra, b)));
    tools.appendChild(miniButton("🏷️ Hashtags", (b) => makeHashtags(sec, extra, b)));
    tools.appendChild(miniButton("⬇️ .txt", () => downloadText("linkedin-post.txt", getPlain(body))));
    tools.appendChild(miniButton("in LinkedIn", () => shareToLinkedIn(getPlain(body))));
    more.appendChild(tools);
    card.appendChild(more);
  }

  card.appendChild(extra);
  return card;
}

// ---------- Rendering ----------
function renderCards(text) {
  cardsBox.innerHTML = "";
  const sections = splitSections(text);
  let bestIdx = -1, bestScore = -1;
  sections.forEach((s, i) => {
    if (/empfehl|recommend|öneri/i.test(s.title)) return;
    const sc = parseInt((parseMeta(s.body).meta || {}).score, 10);
    if (!Number.isNaN(sc) && sc > bestScore) { bestScore = sc; bestIdx = i; }
  });
  if (!sections.length) {
    cardsBox.innerHTML = `<div class="post-card"><div class="post-body">${formatBody(text)}</div></div>`;
    return;
  }
  sections.forEach((sec, i) => cardsBox.appendChild(buildCard(sec, { isBest: i === bestIdx })));
}
function renderSources(sources) {
  if (sources && sources.length) {
    sourcesBox.innerHTML = "<h3>🔗 Quellen aus der Live-Recherche</h3><ol>" +
      sources.map((s) => `<li><a href="${s.url}" target="_blank" rel="noopener">${escapeHtml(s.title || s.url)}</a></li>`).join("") + "</ol>";
    sourcesBox.classList.remove("hidden");
  } else sourcesBox.classList.add("hidden");
}

// ---------- Verlauf ----------
function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; } catch { return []; }
}
function saveToHistory(item) {
  const list = loadHistory();
  list.unshift(item);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(list.slice(0, 15)));
  renderHistory();
}
function renderHistory() {
  const list = loadHistory();
  if (!list.length) { historySection.classList.add("hidden"); return; }
  historySection.classList.remove("hidden");
  historyBox.innerHTML = "";
  for (const item of list) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "history-item";
    const date = new Date(item.ts).toLocaleString("de-DE", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
    row.textContent = `${date} · ${item.label}`;
    row.addEventListener("click", () => {
      renderCards(item.text);
      renderSources(item.sources);
      resultBox.classList.remove("hidden");
      resultBox.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    historyBox.appendChild(row);
  }
}
clearHistoryBtn.addEventListener("click", () => { localStorage.removeItem(HISTORY_KEY); renderHistory(); });

// ---------- Hauptablauf ----------
function collectData() {
  const data = Object.fromEntries(new FormData(form).entries());
  data.webSearch = document.getElementById("webSearch").checked;
  return data;
}
async function generate(data) {
  errorBox.classList.add("hidden");
  resultBox.classList.add("hidden");
  statusBox.classList.remove("hidden");
  statusText.textContent = "Recherchiere & schreibe deine Posts …";
  submitBtn.disabled = true;
  try {
    const json = await callAnthropic(data.apiKey.trim(), {
      model: data.model || "claude-sonnet-4-6",
      max_tokens: 8000,
      prompt: buildPrompt(data),
      useWebSearch: data.webSearch,
      maxUses: data.depth === "tief" ? 10 : 5,
    });
    const text = textFrom(json.content);
    const sources = extractSources(json.content);
    renderCards(text);
    renderSources(sources);
    resultBox.classList.remove("hidden");
    resultBox.scrollIntoView({ behavior: "smooth", block: "start" });
    const label = (data.topic && data.topic.trim()) || (data.draft && "Entwurf") || "Post";
    saveToHistory({ ts: Date.now(), label: label.slice(0, 60), text, sources });
  } catch (err) {
    showErr(err.message);
  } finally {
    statusBox.classList.add("hidden");
    submitBtn.disabled = false;
  }
}

ideasBtn.addEventListener("click", async () => {
  const data = collectData();
  if (!data.apiKey || !data.apiKey.trim()) { showErr("Bitte zuerst den Anthropic API-Key eintragen."); return; }
  errorBox.classList.add("hidden");
  await withBusy(ideasBtn, async () => {
    const json = await callAnthropic(data.apiKey.trim(), { model: data.model || "claude-sonnet-4-6", max_tokens: 1500, prompt: buildIdeasPrompt(data), useWebSearch: data.webSearch, maxUses: 4 });
    const ideas = textFrom(json.content).split("\n").map((l) => l.replace(/^\s*\d+[.)]\s*/, "").replace(/^[-*]\s*/, "").trim()).filter((l) => l.length > 3 && l.length < 160);
    renderChips("💡 Klicke eine Idee, um sie als Thema zu übernehmen:", ideas, (t) => t);
  });
});
document.getElementById("plan-btn").addEventListener("click", async (e) => {
  const data = collectData();
  if (!data.apiKey || !data.apiKey.trim()) { showErr("Bitte zuerst den Anthropic API-Key eintragen."); return; }
  errorBox.classList.add("hidden");
  await withBusy(e.currentTarget, async () => {
    const { text } = await quickGen(`14-Tage-LinkedIn-Content-Plan für Rolle ${data.role || "-"}, Branche ${data.industry || "-"}, Zielgruppe ${data.audience || "-"}, Markt ${data.region || "-"}. Pro Tag ein konkretes Thema, abwechslungsreiche Formate.
FORMAT: "Tag N: <Thema>", eine Zeile pro Tag, max. 90 Zeichen.`, 1500, data.webSearch);
    const days = text.split("\n").map((l) => l.trim()).filter((l) => /^tag/i.test(l));
    renderChips("📅 Klicke einen Tag, um das Thema zu übernehmen:", days, (l) => l.replace(/^tag\s*\d+:\s*/i, ""));
  });
});
function renderChips(title, items, transform) {
  ideasBox.innerHTML = `<p class='ideas-title'>${title}</p>`;
  const wrap = document.createElement("div");
  wrap.className = "ideas-chips";
  items.forEach((it) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = it;
    chip.addEventListener("click", () => {
      topicInput.value = transform ? transform(it) : it;
      topicInput.focus();
      topicInput.scrollIntoView({ behavior: "smooth", block: "center" });
    });
    wrap.appendChild(chip);
  });
  ideasBox.appendChild(wrap);
  ideasBox.classList.remove("hidden");
}

document.getElementById("poll-btn").addEventListener("click", async (e) => {
  const data = lastData || collectData();
  if (!data.apiKey || !data.apiKey.trim()) { showErr("Bitte zuerst Posts generieren oder den API-Key eintragen."); return; }
  await withBusy(e.currentTarget, async () => {
    const { text } = await quickGen(`Erstelle eine LinkedIn-Umfrage zum Thema "${data.topic || "mein Fachgebiet"}" (Branche ${data.industry || "-"}). FORMAT:
Frage: <kurze Frage>
- Option 1
- Option 2
- Option 3
- Option 4
Dann 2–3 Sätze Begleittext.`, 800);
    resultBox.classList.remove("hidden");
    cardsBox.prepend(buildCard({ title: "📊 Umfrage", body: text }));
    resultBox.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});
document.getElementById("ics-btn").addEventListener("click", () => {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1);
  const pad = (n) => String(n).padStart(2, "0");
  const day = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`;
  const ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//LPG//DE", "BEGIN:VEVENT", `UID:${Date.now()}@lpg`, `DTSTART:${day}T090000`, `DTEND:${day}T091500`, "SUMMARY:LinkedIn-Post veröffentlichen", "DESCRIPTION:Erinnerung: vorbereiteten Post posten.", "END:VEVENT", "END:VCALENDAR"].join("\r\n");
  downloadText("linkedin-erinnerung.ics", ics, "text/calendar");
});
document.getElementById("export-all").addEventListener("click", () => {
  const bodies = [...cardsBox.querySelectorAll(".post-card:not(.reco) .post-body")];
  if (!bodies.length) return;
  downloadText("linkedin-posts.txt", bodies.map((b, i) => `=== Post ${i + 1} ===\n${getPlain(b)}`).join("\n\n----------\n\n"));
});
document.getElementById("repurpose-btn").addEventListener("click", async (e) => {
  const data = collectData();
  if (!data.apiKey || !data.apiKey.trim()) { showErr("Bitte zuerst den Anthropic API-Key eintragen."); return; }
  const src = document.getElementById("repurpose-input").value.trim();
  if (!src) return;
  errorBox.classList.add("hidden");
  await withBusy(e.currentTarget, async () => {
    const { text, sources } = await quickGen(`Aus folgendem Text 3 eigenständige LinkedIn-Posts (verschiedene Blickwinkel), menschlich, Sprache "${data.language || "Deutsch"}":
"""
${src.slice(0, 8000)}
"""
FORMAT pro Post:
## Post 1: <Stil>
<Inhalt inkl. Hashtags>
[META] Score: <0-100> | Hook: <0-100> | Lesbarkeit: <0-100> | CTA: <0-100> | Bild: <kurze Bildidee>`, 6000);
    lastData = data;
    renderCards(text);
    renderSources(sources);
    resultBox.classList.remove("hidden");
    resultBox.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

// Stil merken
const styleSamplesEl = document.getElementById("styleSamples");
const savedStyle = localStorage.getItem("lpg_style");
if (savedStyle && styleSamplesEl) styleSamplesEl.value = savedStyle;
document.getElementById("save-style").addEventListener("click", (e) => {
  localStorage.setItem("lpg_style", styleSamplesEl.value.trim());
  e.currentTarget.textContent = "✅ Stil gemerkt";
  setTimeout(() => (e.currentTarget.textContent = "💾 Stil dauerhaft merken"), 1800);
});

// Kommentar-Helfer
const commentBtn = document.getElementById("comment-btn");
commentBtn.addEventListener("click", async () => {
  const d = collectData();
  if (!d.apiKey || !d.apiKey.trim()) { showErr("Bitte zuerst den Anthropic API-Key eintragen."); return; }
  const comment = document.getElementById("comment-input").value.trim();
  if (!comment) return;
  const out = document.getElementById("comment-out");
  errorBox.classList.add("hidden");
  out.innerHTML = "<div class='spinner small'></div>";
  await withBusy(commentBtn, async () => {
    const { text } = await quickGen(`Jemand kommentierte meinen LinkedIn-Beitrag:
"""
${comment}
"""
Mein Profil: Rolle ${d.role || "-"}, Branche ${d.industry || "-"}, Tonfall ${d.tone || "professionell"}.
Schlage 3 kurze, menschliche Antworten vor (Sprache "${d.language || "Deutsch"}"). FORMAT: nummerierte Liste.`, 800);
    const replies = text.split("\n").map((l) => l.replace(/^\s*\d+[.)]\s*/, "").replace(/^[-*]\s*/, "").trim()).filter((l) => l.length > 2);
    out.innerHTML = "";
    renderList(out, "💬 Antwort-Vorschläge", replies);
  });
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const data = collectData();
  if (!data.apiKey || !data.apiKey.trim()) { showErr("Bitte trage zuerst deinen Anthropic API-Key ein."); return; }
  if ((!data.topic || !data.topic.trim()) && (!data.draft || !data.draft.trim())) { showErr("Bitte wähle ein Thema oder füge einen Entwurf ein."); return; }
  lastData = data;
  generate(data);
});
regenBtn.addEventListener("click", () => { if (lastData) generate(lastData); });

renderHistory();
