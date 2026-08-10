/**
 * Regel-Pruefer der Kaltakquise-Maschine, Browser-Fassung.
 *
 * Portierung von src/kaltakquise/pruefer.py. Gleiche Regeln, gleiche
 * Meldungen, gleiche Schweregrade. Aendert sich das Regelwerk, gehoert die
 * Aenderung in beide Dateien; tests/test_web_pruefer.mjs haelt sie deckungsgleich.
 */

export const FEHLER = "fehler";
export const WARNUNG = "warnung";
export const HINWEIS = "hinweis";

const RANG = { [FEHLER]: 0, [WARNUNG]: 1, [HINWEIS]: 2 };

export const KI_MARKER = [
  "ich hoffe, diese e-mail erreicht sie gut",
  "ich hoffe, diese email erreicht sie gut",
  "in der heutigen schnelllebigen zeit",
  "massgeschneiderte lösungen",
  "maßgeschneiderte lösungen",
  "innovativ",
  "ganzheitlich",
  "synergien",
  "mehrwert",
  "gerne stehe ich für rückfragen zur verfügung",
  "zögern sie nicht",
  "revolutionär",
  "einzigartige gelegenheit",
  "ich wollte mich kurz vorstellen",
  "lassen sie uns gemeinsam",
  "auf augenhöhe",
  "am ende des tages",
  "wir freuen uns auf ihre rückmeldung",
  "als ihr verlässlicher partner",
  "spannend",
  "spannende",
  "spannendes",
];

export const SIGNATUR = [
  "Burak Ücöz",
  "Sales Engineer Power",
  "Mobil in Time AG, An Aggreko Company",
  "+41 44 806 13 19",
  "burak.ucoez@mobilintime.ch",
];

export const GRUSSFORMELN = {
  ch: "Freundliche Grüsse",
  de: "Mit freundlichen Grüßen",
  at: "Mit freundlichen Grüßen",
  fr: "Meilleures salutations",
  it: "Cordiali saluti",
  en: "Kind regards",
};

export const REGIONEN = {
  ch: "Deutschschweiz, Hochdeutsch, Sie-Form, ss statt ß",
  de: "Deutschland, Hochdeutsch, Sie-Form, ß nach deutscher Rechtschreibung",
  at: "Österreich, Hochdeutsch, Sie-Form, ß nach deutscher Rechtschreibung",
  fr: "Romandie, Französisch, vous-Form",
  it: "Tessin, Italienisch, Lei-Form",
  en: "Internationaler Empfänger, englische Fassung",
};

const ANREDE_MUSTER =
  /^\s*(guten tag|sehr geehrte[rs]?|bonjour|madame|monsieur|gentile|egregio|dear)\b/i;
const ANREDE_VERBOTEN = "sehr geehrte damen und herren";
const GRUSS_MUSTER =
  /^\s*(freundliche gr(ü|ue)sse|mit freundlichen gr(ü|ue|u)(ss|ß)en|meilleures salutations|cordiali saluti|kind regards|best regards)\s*$/i;
const BETREFF_MUSTER = /^\s*(betreff|subject|objet|oggetto)\s*:\s*(.+)/i;

const BETREFF_MAX_ZEICHEN = 50;
const BETREFF_MIN_WOERTER = 4;
const BETREFF_MAX_WOERTER = 8;
const BETREFF_VERBOTEN = ["angebot", "aw:", "re:", "fwd:", "wg:"];

export const FLIESSTEXT_MIN = 90;
export const FLIESSTEXT_MAX = 150;

const PREIS_MUSTER =
  /(chf|eur|€|fr\.|franken|euro)\s*[\d'’.,]+|[\d'’.,]+\s*(chf|eur|€|franken|euro)|\bpro\s+tag\s+(chf|eur)|\btagesmiete\s+(von|ab|chf|eur)/gi;
const VERFUEGBARKEIT_MUSTER =
  /reservier\w*|\bKW\s?\d{1,2}\b|geblockt|halten wir für sie frei|garantier\w*/i;
const VERFUEGBARKEIT_ERLAUBT = /kläre ich|klaere ich|innert 24|innerhalb von 24/i;
const SUPERLATIVE =
  /\b(beste[rsn]?|führend\w*|fuehrend\w*|weltweit|marktführer\w*|marktfuehrer\w*|modernste[rsn]?|optimal\w*|perfekt\w*|einzigartig\w*)\b/gi;

const NORM_IEC_VOLL = /IEC\s?61000-4-30\s+Klasse\s+A/;
const NORM_IEC_KURZ = /IEC\s?61000-4-30/;
const NORM_KLASSE_A = /\bKlasse\s+A\b/;

const EINHEIT_FALSCH = /\b(KVA|Kva|kva|KWH|Kwh|kwh|kwH|MVa|mva|Mw|mw)\b|\bKW\b(?!\s?\d)/g;

const KUERZEL = {
  BESS: "Batteriespeicher",
  USV: "unterbrechungsfreie",
  NEA: "Netzersatzanlage",
};

const CTA_SIGNALE =
  /\?|ein wort genügt|ein wort genuegt|melde ich mich|schicke ich ihnen|rufe ich sie|passt ihnen|hätten sie|haetten sie/i;
const CTA_SCHWACH = /bei interesse|melden sie sich gerne|freue mich auf ihre antwort/i;

const GEDANKENSTRICH = /[–—]/;
const BULLET_ZEILE = /^\s*([-*•‣]|\d+[.)])\s+/;
const MARKDOWN_MUSTER = /\*\*|__|^#{1,6}\s/m;
const LUECKE_MUSTER = /\[[^\]]{2,}\]/g;

const EMOJI_BEREICHE = [
  [0x2600, 0x27bf],
  [0x2190, 0x21ff],
  [0x2b00, 0x2bff],
];

const STOPP_WOERTER = new Set([
  "eine", "einer", "einem", "einen", "sich", "sind", "wird", "werden", "haben",
  "diese", "dieser", "dieses", "nicht", "auch", "aber", "oder", "wenn", "dann",
  "noch", "schon", "sehr", "mehr", "kann", "muss", "soll", "dass", "über",
  "unter", "nach", "beim", "vom", "zum", "zur", "durch", "gegen", "firma",
  "kunde", "kunden", "neue", "neuer", "neues", "grosse", "grosser",
]);

const istWort = (w) => /[\p{L}\p{N}]/u.test(w);
const woerter = (text) => text.split(/\s+/).filter((w) => w && istWort(w));
const normalisiert = (text) => text.toLowerCase().replace(/\s+/g, " ");

function istEmoji(zeichen) {
  if (/\p{Extended_Pictographic}/u.test(zeichen)) return true;
  const code = zeichen.codePointAt(0);
  return EMOJI_BEREICHE.some(([a, b]) => code >= a && code <= b);
}

/** Zerlegt einen Mailtext. Fehlende Teile bleiben leer, der Prüfer meldet sie. */
export function zerlege(text) {
  const roh = String(text).replace(/\r\n/g, "\n").trim();
  const zeilen = roh.split("\n");

  let betreff = "";
  let start = 0;
  for (let i = 0; i < Math.min(5, zeilen.length); i++) {
    const treffer = zeilen[i].match(BETREFF_MUSTER);
    if (treffer) {
      betreff = treffer[2].trim().replace(/^["„“]|["„“]$/g, "");
      start = i + 1;
      break;
    }
  }

  let anrede = "";
  let anredeIdx = start;
  for (let i = start; i < zeilen.length; i++) {
    if (zeilen[i].trim()) {
      anredeIdx = i;
      if (ANREDE_MUSTER.test(zeilen[i])) anrede = zeilen[i].trim();
      break;
    }
  }

  let gruss = "";
  let grussIdx = zeilen.length;
  for (let i = zeilen.length - 1; i > anredeIdx; i--) {
    if (GRUSS_MUSTER.test(zeilen[i])) {
      gruss = zeilen[i].trim();
      grussIdx = i;
      break;
    }
  }

  const korpusStart = anrede ? anredeIdx + 1 : anredeIdx;
  const fliesstext = zeilen.slice(korpusStart, grussIdx).join("\n").trim();
  const signatur = zeilen.slice(grussIdx + 1).map((z) => z.trim()).filter(Boolean);

  return {
    roh,
    betreff,
    anrede,
    fliesstext,
    gruss,
    signatur,
    wortzahl: woerter(fliesstext).length,
  };
}

function signalwoerter(quelle) {
  const gefunden = quelle.match(/[\p{L}\p{N}.\-]{3,}/gu) || [];
  const signale = [];
  for (const wort of gefunden) {
    const rein = wort.replace(/^[.\-]+|[.\-]+$/g, "");
    if (!rein || STOPP_WOERTER.has(rein.toLowerCase())) continue;
    const hatZiffer = /\d/.test(rein);
    const istName = rein[0] === rein[0].toUpperCase() && /\p{L}/u.test(rein[0]) && rein.length >= 4;
    if (hatZiffer || istName) signale.push(rein);
  }
  return [...new Set(signale)];
}

/** Prüft eine Mail und liefert alle Befunde, schwerste zuerst. */
export function pruefe(text, { region = "ch", quelle = null } = {}) {
  const mail = typeof text === "string" ? zerlege(text) : text;
  const befunde = [];
  const melde = (schwere, regel, meldung) => befunde.push({ schwere, regel, text: meldung });

  const roh = mail.roh;
  const flach = normalisiert(roh);

  // --- Betreff -----------------------------------------------------------
  if (!mail.betreff) {
    melde(FEHLER, "Betreff", "Kein Betreff gefunden (erste Zeile 'Betreff: ...').");
  } else {
    const anzahl = mail.betreff.split(/\s+/).filter(Boolean).length;
    if (mail.betreff.length > BETREFF_MAX_ZEICHEN) {
      melde(WARNUNG, "Betreff",
        `${mail.betreff.length} Zeichen, maximal ${BETREFF_MAX_ZEICHEN} (sonst auf dem Handy abgeschnitten).`);
    }
    if (anzahl < BETREFF_MIN_WOERTER || anzahl > BETREFF_MAX_WOERTER) {
      melde(WARNUNG, "Betreff",
        `${anzahl} Wörter, vorgesehen sind ${BETREFF_MIN_WOERTER} bis ${BETREFF_MAX_WOERTER}.`);
    }
    if (mail.betreff.includes("?") || mail.betreff.includes("!")) {
      melde(FEHLER, "Betreff", "Kein Frage- oder Ausrufezeichen im Betreff.");
    }
    for (const verboten of BETREFF_VERBOTEN) {
      if (mail.betreff.toLowerCase().includes(verboten)) {
        melde(FEHLER, "Betreff", `Verbotenes Wort im Betreff: '${verboten}'.`);
      }
    }
  }

  // --- Anrede ------------------------------------------------------------
  if (!mail.anrede) melde(FEHLER, "Anrede", "Keine Anrede gefunden.");
  if (flach.includes(ANREDE_VERBOTEN)) {
    melde(FEHLER, "Anrede",
      "'Sehr geehrte Damen und Herren' ist in der Kaltakquise verboten, Namen recherchieren oder Lücke markieren.");
  }

  // --- Einstieg ----------------------------------------------------------
  const erstesWort = (mail.fliesstext.split(/\s+/)[0] || "").replace(/[,.:;]+$/, "");
  if (erstesWort.toLowerCase() === "ich") {
    melde(FEHLER, "Einstieg", "Der erste Satz darf nicht mit 'Ich' beginnen.");
  }

  // --- Länge -------------------------------------------------------------
  if (!mail.fliesstext) {
    melde(FEHLER, "Fliesstext", "Kein Fliesstext gefunden.");
  } else if (mail.wortzahl < FLIESSTEXT_MIN) {
    melde(WARNUNG, "Länge",
      `${mail.wortzahl} Wörter Fliesstext, Ziel sind ${FLIESSTEXT_MIN} bis ${FLIESSTEXT_MAX}.`);
  } else if (mail.wortzahl > FLIESSTEXT_MAX) {
    melde(FEHLER, "Länge",
      `${mail.wortzahl} Wörter Fliesstext, Maximum ist ${FLIESSTEXT_MAX}. Kalt heisst kurz.`);
  }

  // --- Grussformel und Signatur -----------------------------------------
  if (!mail.gruss) {
    melde(FEHLER, "Grussformel", "Keine Grussformel gefunden.");
  } else {
    const erwartet = GRUSSFORMELN[region];
    if (erwartet && mail.gruss.toLowerCase() !== erwartet.toLowerCase()) {
      melde(WARNUNG, "Grussformel",
        `'${mail.gruss}' passt nicht zur Region '${region}', erwartet: '${erwartet}'.`);
    }
  }
  for (const zeile of SIGNATUR) {
    if (!flach.includes(zeile.toLowerCase())) {
      melde(FEHLER, "Signatur", `Signaturzeile fehlt: '${zeile}'.`);
    }
  }

  // --- Sprachregister ----------------------------------------------------
  if (["ch", "fr", "it"].includes(region) && roh.includes("ß")) {
    melde(FEHLER, "Orthografie", "Schweizer Empfänger: ss statt ß.");
  }

  // --- Preise ------------------------------------------------------------
  for (const treffer of roh.matchAll(PREIS_MUSTER)) {
    melde(FEHLER, "Preise", `Preisangabe im Erstkontakt: '${treffer[0].trim()}'.`);
  }

  // --- Verfügbarkeit -----------------------------------------------------
  for (const satz of roh.split(/(?<=[.!?])\s+/)) {
    const treffer = satz.match(VERFUEGBARKEIT_MUSTER);
    if (treffer && !VERFUEGBARKEIT_ERLAUBT.test(satz)) {
      melde(FEHLER, "Verfügbarkeit",
        `Verfügbarkeit zugesagt ohne Freigabe: '${treffer[0].trim()}'.`);
    }
  }

  // --- KI-Marker ---------------------------------------------------------
  for (const marker of KI_MARKER) {
    if (flach.includes(marker)) {
      melde(FEHLER, "KI-Marker", `Blacklist-Formulierung: '${marker}'.`);
    }
  }

  // --- Superlative -------------------------------------------------------
  for (const treffer of roh.matchAll(SUPERLATIVE)) {
    melde(WARNUNG, "Superlativ",
      `Superlativ ohne Beleg: '${treffer[0]}'. Erlaubt ist nur die Tatsachenbehauptung 'als einziger Vermieter'.`);
  }

  // --- Formatierung ------------------------------------------------------
  if (GEDANKENSTRICH.test(roh)) {
    melde(FEHLER, "Formatierung", "Gedankenstriche sind als Stilmittel verboten.");
  }
  if (MARKDOWN_MUSTER.test(roh)) {
    melde(FEHLER, "Formatierung", "Kein Markdown im Mailtext (**, __, #).");
  }
  for (const zeile of mail.fliesstext.split("\n")) {
    if (BULLET_ZEILE.test(zeile)) {
      melde(FEHLER, "Formatierung",
        `Aufzählung im Mailtext, Kaltakquise ist Fliesstext: '${zeile.trim().slice(0, 40)}'.`);
      break;
    }
  }
  const emojis = [...new Set([...roh].filter(istEmoji))].sort();
  if (emojis.length) {
    melde(FEHLER, "Formatierung", `Emojis im Mailtext: ${emojis.join(" ")}.`);
  }

  // --- Normen ------------------------------------------------------------
  const voll = roh.match(NORM_IEC_VOLL);
  const kurz = roh.match(NORM_IEC_KURZ);
  const klasseA = roh.match(NORM_KLASSE_A);
  if (kurz && !voll) {
    melde(FEHLER, "Normen",
      "IEC 61000-4-30 beim ersten Nennen unvollständig, korrekt ist 'IEC 61000-4-30 Klasse A'.");
  }
  if (klasseA && voll && klasseA.index < voll.index) {
    melde(FEHLER, "Normen",
      "'Klasse A' steht vor der vollständigen Nennung von IEC 61000-4-30 Klasse A.");
  }
  if (klasseA && !kurz) {
    melde(FEHLER, "Normen",
      "'Klasse A' ohne Norm-Bezug, beim ersten Nennen IEC 61000-4-30 ausschreiben.");
  }

  // --- Einheiten ---------------------------------------------------------
  for (const treffer of roh.matchAll(EINHEIT_FALSCH)) {
    melde(FEHLER, "Einheiten",
      `Falsche Einheitenschreibweise: '${treffer[0]}' (kVA, kW, kWh, MVA sauber trennen).`);
  }

  // --- Fachkürzel --------------------------------------------------------
  for (const [kuerzel, aufloesung] of Object.entries(KUERZEL)) {
    if (new RegExp(`\\b${kuerzel}\\b`).test(roh) && !flach.includes(aufloesung.toLowerCase())) {
      melde(WARNUNG, "Fachkürzel",
        `'${kuerzel}' wird nicht aufgelöst, beim ersten Nennen '${aufloesung}' ausschreiben.`);
    }
  }

  // --- Call-to-Action ----------------------------------------------------
  if (mail.fliesstext) {
    if (!CTA_SIGNALE.test(mail.fliesstext)) {
      melde(FEHLER, "Call-to-Action",
        "Kein konkreter nächster Schritt erkennbar (Zeitfenster, Frage oder konkretes Angebot).");
    }
    const schwach = mail.fliesstext.match(CTA_SCHWACH);
    if (schwach) {
      melde(FEHLER, "Call-to-Action", `Weicher Abschluss statt konkretem Schritt: '${schwach[0]}'.`);
    }
  }

  // --- Lücken ------------------------------------------------------------
  for (const treffer of roh.matchAll(LUECKE_MUSTER)) {
    melde(HINWEIS, "Lücke", `Markierte Lücke vor dem Versand füllen: '${treffer[0]}'.`);
  }

  // --- Personalisierung --------------------------------------------------
  if (quelle && quelle.trim()) {
    const signale = signalwoerter(quelle);
    const getroffen = signale.filter((s) => flach.includes(s.toLowerCase()));
    if (signale.length && !getroffen.length) {
      melde(FEHLER, "Personalisierung",
        "Kein einziges Detail aus dem Input in der Mail. Diese Mail könnte an jede andere Firma gehen.");
    } else if (signale.length >= 4 && getroffen.length < 2) {
      melde(WARNUNG, "Personalisierung",
        `Nur ein Detail aus dem Input übernommen (${getroffen[0]}). Spezifischer werden.`);
    }
  }

  befunde.sort((a, b) => RANG[a.schwere] - RANG[b.schwere] || a.regel.localeCompare(b.regel, "de"));
  return befunde;
}

export const hatFehler = (befunde) => befunde.some((b) => b.schwere === FEHLER);

export function bilanz(befunde) {
  const z = { [FEHLER]: 0, [WARNUNG]: 0, [HINWEIS]: 0 };
  befunde.forEach((b) => (z[b.schwere] += 1));
  return z;
}

const VARIANTEN_KOPF = /^[ \t]*\**[ \t]*Variante[ \t]+([A-Z])\b[^\n]*$/gim;
const WARUM_ZEILE = /^\s*\*[^*].*wirkt.*\*\s*$/gim;
const ABSCHNITT_ENDE = /^\s*\**\s*(Follow-up|Annahme|Analyse)\b/im;

/** Schneidet aus der Modellausgabe die Blöcke 'Variante A/B' heraus. */
export function extrahiereVarianten(ausgabe) {
  const treffer = [...String(ausgabe).matchAll(VARIANTEN_KOPF)];
  if (!treffer.length) return [];

  return treffer.map((kopf, i) => {
    const von = kopf.index + kopf[0].length;
    const bis = i + 1 < treffer.length ? treffer[i + 1].index : ausgabe.length;
    let block = ausgabe.slice(von, bis);

    const schluss = block.match(ABSCHNITT_ENDE);
    if (schluss) block = block.slice(0, schluss.index);

    block = block
      .replace(WARUM_ZEILE, "")
      .replace(/^\s*```.*$/gm, "")
      .replace(/^\s*-{3,}\s*$/gm, "")
      .trim()
      .replace(/^"|"$/g, "");

    return { name: `Variante ${kopf[1].toUpperCase()}`, text: block.trim() };
  });
}
