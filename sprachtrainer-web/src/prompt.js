// Baut System-Prompt und Nachbereitungs-Auftrag aus den Skill-Dateien.
import skillMd from "../../.claude/skills/sprachtrainer/SKILL.md";
import modiMd from "../../.claude/skills/sprachtrainer/references/modi.md";
import enMd from "../../.claude/skills/sprachtrainer/references/en.md";
import frMd from "../../.claude/skills/sprachtrainer/references/fr.md";
import esMd from "../../.claude/skills/sprachtrainer/references/es.md";
import zhMd from "../../.claude/skills/sprachtrainer/references/zh.md";
import { today } from "./store.js";

export const LANGS = {
  en: { name: "Englisch", short: "EN", ref: enMd },
  fr: { name: "Französisch", short: "FR", ref: frMd },
  es: { name: "Spanisch", short: "ES", ref: esMd },
  zh: { name: "Chinesisch", short: "中文", ref: zhMd },
};

export const MODES = [
  ["heute", "Tagesprogramm", "Programm nach Plan-Tag"],
  ["gespraech", "Gespräch", "Rollenspiel, Korrektur am Ende"],
  ["wortschatz", "Wortschatz", "15 Einheiten mit Test"],
  ["grammatik", "Grammatik", "Eine Regel, Übung, Analyse"],
  ["input", "Lesen", "Text auf Niveau +1"],
  ["immersion", "Immersion", "Ganze Situation in der Zielsprache"],
  ["schreiben", "Schreiben", "Mail schreiben, korrigieren lassen"],
  ["shadowing", "Shadowing", "5 Sätze zum Nachsprechen"],
  ["test", "Wochentest", "10 Aufgaben, Resultat ins Profil"],
  ["plan", "90-Tage-Plan", "Plan erstellen oder neu machen"],
  ["start", "Einstufung", "Niveau, Ziel, Profil anlegen"],
];

function section(md, heading) {
  const start = md.indexOf(heading);
  if (start < 0) return "";
  const rest = md.slice(start + heading.length);
  const next = rest.search(/\n## /);
  return heading + (next < 0 ? rest : rest.slice(0, next));
}

function modeSection(mode) {
  const re = new RegExp(`\\n## ${mode}\\b[^\\n]*`);
  const m = modiMd.match(re);
  return m ? section(modiMd, m[0].trim()) : "";
}

const WEB_CORE = `Du bist Buraks persönlicher Sprachtrainer in einer Web-App. Burak ist deutschsprachig, lebt in der Schweiz (Region Schaffhausen), arbeitet als Area Sales Engineer für mobile Energie (Generatoren, Batteriespeicher, USV, Trafos, Netzqualität). Er lernt als Erwachsener, berufsorientiert, mit wenig Zeit. Training muss im Job verwertbar sein.

## Rahmen der Web-App
- Fortschritt (Profil, Plan, Fehlerjournal, Wortschatz, Log) verwaltet die App. Du siehst ihn unten unter "Aktueller Stand". Du schreibst keine Dateien und kündigst keine Dateiupdates an. Die App macht nach der Session eine eigene Nachbereitung.
- Burak kann deine Antworten vorlesen lassen (Sprachausgabe des Browsers) und per Mikrofon diktieren. Die Spracherkennung ist nur ein grober Hinweis auf die Aussprache, kein Beweis. Du hörst nichts. Aussprachefeedback nur über Hinweise (Betonung, Bindungen, stumme Laute, Töne beschreiben).
- Schreib knapp. Markdown ist erlaubt (fett, Listen, Tabellen).
- Chat-Erklärungen auf Deutsch, DU-Form, Schweizer Schreibweise (ss statt ß), keine Gedankenstriche als Stilmittel. Das Training selbst nach den Regeln unten.
- Datum im Format TT.MM.JJJJ. Heute ist ${"{{HEUTE}}"}.
- Session-Ablauf: Kein "start"-Modus und kein Profil vorhanden: sag, dass zuerst die Einstufung nötig ist, und beginne direkt damit. Sonst bei allen Modi ausser start und plan: Aufwärmen mit den 3 häufigsten offenen Fehlern (max. 2 Min., Burak korrigiert je einen Satz), dann der Modus.
- Steuerwörter: \`hilfe\` gibt einen Satzanfang. \`deutsch\` erklärt deinen letzten Satz auf Deutsch. \`langsamer\` senkt das Niveau um eine halbe Stufe. \`stopp\` beendet die Session (die App übernimmt).`;

function renderState(lang, s) {
  const p = s.profil;
  const lines = [];
  if (!p) {
    lines.push("Noch kein Profil. Einstufung nötig.");
  } else {
    lines.push(
      `- Varietät: ${p.varietaet || "offen"}`,
      `- Niveau: ${p.niveau || "offen"}`,
      `- Ziel: ${p.ziel || "offen"}`,
      `- Wichtigste Situation in 90 Tagen: ${p.situation90 || "offen"}`,
      `- Minuten pro Tag: ${p.minutenProTag || "offen"}`,
      `- Startdatum Plan: ${p.startdatumPlan || "kein Plan"}`,
      `- Plan-Tag: ${p.planTag ?? 0}`,
      `- Letzte Session: ${p.letzteSession || "keine"}`,
      `- Stärken: ${(p.staerken || []).join("; ") || "noch keine"}`,
      `- Schwächen: ${(p.schwaechen || []).join("; ") || "noch keine"}`,
    );
  }
  const offen = [...s.fehler].sort((a, b) => b.zaehler - a.zaehler).slice(0, 10);
  lines.push("", "### Offene Fehler (häufigste zuerst)");
  lines.push(offen.length ? offen.map((f) => `- (${f.zaehler}x) ${f.falsch} → ${f.richtig} | ${f.regel}`).join("\n") : "- keine");
  lines.push("", "### Letzte Sessions");
  lines.push(s.log.length ? s.log.slice(-5).map((l) => `- ${l.datum} ${l.modus} ${l.thema}: ${l.beobachtung}`).join("\n") : "- keine");
  lines.push("", `### Wortschatz (${s.wortschatz.length} Einheiten, die letzten 40)`);
  lines.push(s.wortschatz.slice(-40).map((w) => w.zielsprache).join(" · ") || "leer");
  lines.push("", "### Tests");
  lines.push(s.tests.length ? s.tests.slice(-3).map((t) => `- ${t.datum} ${t.woche}: ${t.resultat}% ${t.bemerkung}`).join("\n") : "- keine");
  lines.push("", "### 90-Tage-Plan");
  lines.push(s.plan || "kein Plan vorhanden");
  return lines.join("\n");
}

export function buildSystem(lang, mode, state) {
  const l = LANGS[lang];
  return [
    WEB_CORE.replace("{{HEUTE}}", today()),
    section(skillMd, "## Trainerregeln"),
    `## Sprache dieser Session: ${l.name} (${lang})\n\n${l.ref}`,
    `## Modus dieser Session: ${mode}\n\n${modeSection(mode)}`,
    `## Aktueller Stand (${l.name})\n\n${renderState(lang, state)}`,
  ].join("\n\n");
}

export function kickoff(mode, topic) {
  return `Modus: ${mode}${topic ? `\nThema: ${topic}` : ""}\nLos geht's.`;
}

export const WRAPUP_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: [
    "fehler_neu", "fehler_wiederholt", "fehler_korrekt", "wortschatz_neu",
    "log_thema", "log_beobachtung", "profil", "plan_markdown", "plan_tag_weiter",
    "test", "rueckmeldung",
  ],
  properties: {
    fehler_neu: {
      type: "array",
      items: {
        type: "object", additionalProperties: false,
        required: ["falsch", "richtig", "regel"],
        properties: { falsch: { type: "string" }, richtig: { type: "string" }, regel: { type: "string" } },
      },
    },
    fehler_wiederholt: { type: "array", items: { type: "string" } },
    fehler_korrekt: { type: "array", items: { type: "string" } },
    wortschatz_neu: {
      type: "array",
      items: {
        type: "object", additionalProperties: false,
        required: ["zielsprache", "deutsch", "beispielsatz", "tags"],
        properties: {
          zielsprache: { type: "string" }, deutsch: { type: "string" },
          beispielsatz: { type: "string" }, tags: { type: "string" },
        },
      },
    },
    log_thema: { type: "string" },
    log_beobachtung: { type: "string" },
    profil: {
      type: "object", additionalProperties: false,
      required: ["varietaet", "niveau", "ziel", "situation90", "minutenProTag", "staerken", "schwaechen"],
      properties: {
        varietaet: { type: "string" }, niveau: { type: "string" }, ziel: { type: "string" },
        situation90: { type: "string" }, minutenProTag: { type: "string" },
        staerken: { type: "array", items: { type: "string" } },
        schwaechen: { type: "array", items: { type: "string" } },
      },
    },
    plan_markdown: { type: "string" },
    plan_tag_weiter: { type: "boolean" },
    test: {
      type: "object", additionalProperties: false,
      required: ["resultat_prozent", "woche", "bemerkung"],
      properties: { resultat_prozent: { type: "integer" }, woche: { type: "string" }, bemerkung: { type: "string" } },
    },
    rueckmeldung: { type: "string" },
  },
};

export function wrapupPrompt(lang, mode, state, transcript) {
  const ids = state.fehler.map((f, i) => `F${i + 1}: ${f.falsch} → ${f.richtig}`).join("\n") || "keine";
  return `Nachbereitung einer Sprachtraining-Session (${LANGS[lang].name}, Modus ${mode}). Werte das Transkript aus und liefere das JSON.

Regeln:
- fehler_neu: Fehler von Burak, die NICHT schon im Journal stehen. Max. 5, die wichtigsten (Verständnis vor Register vor Kosmetik). Kurz: falsch, richtig, Regel in einem Satz auf Deutsch.
- fehler_wiederholt: IDs (z.B. "F3") von Journal-Fehlern, die Burak in dieser Session wieder gemacht hat.
- fehler_korrekt: IDs von Journal-Fehlern, die Burak in dieser Session korrekt verwendet hat (z.B. beim Aufwärmen).
- wortschatz_neu: neu eingeführte Einheiten, keine Duplikate zum bestehenden Wortschatz. Bei Chinesisch zielsprache als "发电机 (fādiànjī)". tags: Leerzeichen-getrennt, z.B. "fach generator".
- log_thema: Thema in wenigen Wörtern. log_beobachtung: eine Zeile Kernbeobachtung.
- profil: nur Felder füllen, die sich in dieser Session ergeben oder geändert haben (bei Einstufung alle). Sonst "" bzw. leere Liste. niveau als A1, A2, A2+, B1, B1+, B2 oder C1.
- plan_markdown: nur wenn in dieser Session ein 90-Tage-Plan erstellt wurde, den vollständigen Plan als Markdown. Sonst "".
- plan_tag_weiter: true, wenn ein Tagesprogramm (Modus heute) wesentlich durchgearbeitet wurde.
- test: nur bei Wochentest das Resultat in Prozent, sonst resultat_prozent -1 und leere Strings.
- rueckmeldung: max. 3 Zeilen auf Deutsch (Schweizer Schreibweise): was sass, was nicht, was als nächstes dran ist.

Fehlerjournal (offen):
${ids}

Bestehender Wortschatz:
${state.wortschatz.map((w) => w.zielsprache).join(" · ") || "leer"}

Transkript:
${transcript}`;
}
