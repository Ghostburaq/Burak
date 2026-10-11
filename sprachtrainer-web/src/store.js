// Lokaler Speicher im Browser plus Backup-Export und -Import.
const KEY = "sprachtrainer.v1";

export function today() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()}`;
}

export function parseDate(s) {
  const m = /^(\d{2})\.(\d{2})\.(\d{4})/.exec(s || "");
  return m ? new Date(+m[3], +m[2] - 1, +m[1]) : null;
}

export function emptyLang() {
  return { profil: null, plan: "", fehler: [], erledigt: [], wortschatz: [], log: [], tests: [] };
}

function emptyState() {
  return {
    settings: { apiKey: "", model: "claude-opus-5-5", effort: "medium", rate: 0.95, autoRead: false, fallbacks: true },
    langs: { en: emptyLang(), fr: emptyLang(), es: emptyLang(), zh: emptyLang() },
    lastLang: "fr",
    session: null,
  };
}

function merge(base, loaded) {
  const s = { ...base, ...loaded, settings: { ...base.settings, ...(loaded.settings || {}) } };
  s.langs = { ...base.langs };
  for (const k of Object.keys(base.langs)) s.langs[k] = { ...emptyLang(), ...((loaded.langs || {})[k] || {}) };
  return s;
}

export function load() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? merge(emptyState(), JSON.parse(raw)) : emptyState();
  } catch {
    return emptyState();
  }
}

export function save(state) {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
    return true;
  } catch {
    return false;
  }
}

export function exportBackup(state) {
  const { settings, ...rest } = state;
  const { apiKey, ...safeSettings } = settings; // Key nie ins Backup
  return JSON.stringify({ app: "sprachtrainer", version: 1, exportiert: today(), ...rest, settings: safeSettings, session: null }, null, 2);
}

export function importBackup(state, text) {
  const data = JSON.parse(text);
  if (data.app !== "sprachtrainer" || !data.langs) throw new Error("Keine Sprachtrainer-Sicherung");
  const merged = merge(emptyState(), data);
  merged.settings.apiKey = state.settings.apiKey;
  return merged;
}

// Wendet das Nachbereitungs-JSON auf den Sprachstand an.
export function applyWrapup(L, mode, w) {
  const d = today();
  const hit = (id) => L.fehler[Number(String(id).replace(/\D/g, "")) - 1];

  const wieder = new Set(w.fehler_wiederholt.map(hit).filter(Boolean));
  for (const f of wieder) { f.zaehler += 1; f.zuletzt = d; f.korrektInFolge = 0; }
  for (const f of new Set(w.fehler_korrekt.map(hit).filter(Boolean))) {
    if (!wieder.has(f)) f.korrektInFolge = (f.korrektInFolge || 0) + 1;
  }
  const fertig = L.fehler.filter((f) => f.korrektInFolge >= 3);
  L.erledigt.push(...fertig.map((f) => ({ falsch: f.falsch, richtig: f.richtig, am: d })));
  L.fehler = L.fehler.filter((f) => f.korrektInFolge < 3);
  for (const f of w.fehler_neu) {
    const same = L.fehler.find((x) => x.falsch.trim().toLowerCase() === f.falsch.trim().toLowerCase());
    if (same) { same.zaehler += 1; same.zuletzt = d; }
    else L.fehler.push({ ...f, zaehler: 1, zuletzt: d, korrektInFolge: 0 });
  }

  const known = new Set(L.wortschatz.map((x) => x.zielsprache.trim().toLowerCase()));
  for (const v of w.wortschatz_neu) {
    const k = v.zielsprache.trim().toLowerCase();
    if (!k || known.has(k)) continue;
    known.add(k);
    L.wortschatz.push({ ...v, hinzugefuegt: d, exportiert: "nein" });
  }

  const p = (L.profil ||= { planTag: 0, staerken: [], schwaechen: [] });
  for (const k of ["varietaet", "niveau", "ziel", "situation90", "minutenProTag"]) {
    if (w.profil[k]) p[k] = w.profil[k];
  }
  if (w.profil.staerken.length) p.staerken = w.profil.staerken;
  if (w.profil.schwaechen.length) p.schwaechen = w.profil.schwaechen;
  if (mode === "start" && !p.einstufungVom) p.einstufungVom = d;
  if (w.plan_markdown.trim()) { L.plan = w.plan_markdown; p.planTag = 1; p.startdatumPlan = d; }
  else if (w.plan_tag_weiter && L.plan) p.planTag = (p.planTag || 0) + 1;
  p.letzteSession = `${d}, ${mode}`;

  if (w.test.resultat_prozent >= 0) {
    L.tests.push({ datum: d, woche: w.test.woche, resultat: w.test.resultat_prozent, bemerkung: w.test.bemerkung });
  }
  L.log.push({ datum: d, modus: mode, thema: w.log_thema, beobachtung: w.log_beobachtung });
}

export function ankiExport(L) {
  const neu = L.wortschatz.filter((w) => w.exportiert !== "ja");
  const clean = (s) => String(s || "").replace(/[\t\r\n]+/g, " ").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").trim();
  const lines = neu.map((w) => [`${clean(w.zielsprache)}<br><i>${clean(w.beispielsatz)}</i>`, clean(w.deutsch), clean(w.tags)].join("\t"));
  for (const w of neu) w.exportiert = "ja";
  return { count: neu.length, text: "#separator:tab\n#html:true\n" + lines.join("\n") + "\n" };
}
