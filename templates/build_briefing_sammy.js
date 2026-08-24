// Interne Gesprächsvorbereitung: Sammy Baumann · Bericht Gasthaus Kreuz
// VERTRAULICH — kabuu-Master-Look, kompaktes A4-Briefing (4–5 Seiten).

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, HeadingLevel, PageOrientation, BorderStyle,
  Header, Footer, PageNumber, TabStopType, ShadingType, VerticalAlign,
  LevelFormat, convertMillimetersToTwip, LineRuleType, PageBreak,
} = require("docx");

// ---------- Brand ----------
const NAVY   = "0B2545";
const CYAN   = "00B8D9";
const INK    = "0F172A";
const GREY_D = "334155";
const GREY_M = "64748B";
const GREY_L = "E2E8F0";
const PAPER  = "F8FAFC";
const CYAN_S = "EAF7FB";
const RED    = "B91C1C";
const AMBER  = "B45309";
const GREEN  = "047857";

const FONT = "Calibri";

const SENDER = {
  brand:  "kabuu",
  role:   "Netzqualität & EMV Messungen · Engineering",
  name:   "Burak Ücöz",
  street: "Im Abt 9 A",
  city:   "8240 Thayngen",
  phone:  "+41 79 512 98 07",
  email:  "engineering.kabuu@gmail.com",
};

const BRAND_DIR = "/home/user/Burak/assets/brand";
const LOCKUP    = fs.readFileSync(path.join(BRAND_DIR, "kabuu_logo_mono.png"));

// ---------- Helpers ----------
const T = (text, opts = {}) => new TextRun({ font: FONT, size: 20, color: INK, ...opts, text });

function h1(text) {
  return new Paragraph({
    spacing: { before: 220, after: 140 },
    children: [new TextRun({ text, font: FONT, size: 30, bold: true, color: NAVY })],
    heading: HeadingLevel.HEADING_1,
    border: { bottom: { color: CYAN, size: 12, style: BorderStyle.SINGLE, space: 6 } },
  });
}
function h2(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 240, after: 80 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true, color: opts.color || NAVY })],
    heading: HeadingLevel.HEADING_2,
  });
}
function borderNone() {
  const n = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: n, bottom: n, left: n, right: n, insideHorizontal: n, insideVertical: n };
}

// ---------- Header ----------
const header = new Header({
  children: [
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { after: 0 },
      children: [new ImageRun({
        data: LOCKUP,
        transformation: { width: 150, height: 96 },
        type: "png",
      })],
    }),
    new Paragraph({
      spacing: { before: 20, after: 0 },
      alignment: AlignmentType.RIGHT,
      children: [
        new TextRun({ text: "VERTRAULICH · INTERNE GESPRÄCHSVORBEREITUNG", font: FONT, size: 14, color: RED, bold: true, characterSpacing: 60 }),
      ],
    }),
    new Paragraph({
      spacing: { before: 20, after: 0 },
      border: { bottom: { color: CYAN, size: 8, style: BorderStyle.SINGLE, space: 1 } },
      children: [new TextRun({ text: "", size: 2 })],
    }),
  ],
});

// ---------- Footer ----------
const footer = new Footer({
  children: [
    new Paragraph({
      spacing: { before: 0, after: 20 },
      border: { top: { color: GREY_L, size: 6, style: BorderStyle.SINGLE, space: 4 } },
      children: [new TextRun({ text: "", size: 2 })],
    }),
    new Paragraph({
      alignment: AlignmentType.LEFT,
      tabStops: [{ type: TabStopType.RIGHT, position: 9072 }],
      children: [
        new TextRun({ text: `Briefing Sammy Baumann · ${SENDER.brand}`, font: FONT, size: 15, color: NAVY, bold: true }),
        new TextRun({ text: "\tNur intern — nicht weitergeben  ·  Seite ", font: FONT, size: 15, color: RED }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 15, color: NAVY, bold: true }),
        new TextRun({ text: " / ", font: FONT, size: 15, color: RED }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 15, color: NAVY, bold: true }),
      ],
    }),
  ],
});

// ---------- Coloured accent box ----------
function accentBox(label, color, paragraphs) {
  return new Table({
    columnWidths: [9360],
    width: { size: 9360, type: WidthType.DXA },
    borders: borderNone(),
    rows: [
      new TableRow({
        children: [new TableCell({
          width: { size: 9360, type: WidthType.DXA },
          margins: { top: 180, bottom: 180, left: 240, right: 240 },
          shading: { type: ShadingType.CLEAR, color: "auto", fill: PAPER },
          borders: {
            top:    { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
            bottom: { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
            left:   { style: BorderStyle.SINGLE, size: 24, color },
            right:  { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
          },
          children: [
            new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: label, font: FONT, size: 14, color, bold: true, allCaps: true, characterSpacing: 60 })] }),
            ...paragraphs,
          ],
        })],
      }),
    ],
  });
}

// ---------- Q&A block ----------
function qaBlock(num, question, answers, tone = "neutral") {
  const kickerColor = tone === "hard" ? RED : (tone === "soft" ? GREEN : CYAN);
  const qKicker = tone === "hard" ? "HARTE FRAGE" : (tone === "soft" ? "EINFACH" : "WAHRSCHEINLICH");

  const answerParas = answers.map(a => new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60, line: 280, lineRule: LineRuleType.AUTO },
    children: Array.isArray(a) ? a : [T(a)],
  }));

  return [
    new Paragraph({
      spacing: { before: 200, after: 40 },
      children: [
        new TextRun({ text: `Q${num}  ·  `, font: FONT, size: 14, color: kickerColor, bold: true }),
        new TextRun({ text: qKicker, font: FONT, size: 14, color: kickerColor, bold: true, characterSpacing: 60 }),
      ],
    }),
    new Paragraph({
      spacing: { after: 80 },
      children: [new TextRun({ text: `„${question}”`, font: FONT, size: 22, bold: true, color: NAVY, italics: true })],
    }),
    new Paragraph({
      spacing: { after: 40 },
      children: [new TextRun({ text: "DEINE ANTWORT", font: FONT, size: 12, color: GREY_M, bold: true, characterSpacing: 60 })],
    }),
    ...answerParas,
  ];
}

// ---------- Facts strip (3 columns) ----------
function factCell(label, body) {
  return new TableCell({
    margins: { top: 140, bottom: 140, left: 180, right: 180 },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: PAPER },
    borders: {
      top:    { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
      left:   { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
      right:  { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
    },
    width: { size: 3120, type: WidthType.DXA },
    children: [
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: label, font: FONT, size: 13, color: CYAN, bold: true, allCaps: true, characterSpacing: 60 })] }),
      new Paragraph({ children: [new TextRun({ text: body, font: FONT, size: 17, color: INK })] }),
    ],
  });
}

const factsRow = new Table({
  columnWidths: [3120, 3120, 3120],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({ children: [
      factCell("KUNDE",   "Sammy Baumann · Baumann Elektrokontrollen GmbH, Gossau"),
      factCell("PROJEKT", "PQ-Messung Gasthaus Kreuz, Zuzwil SG · Flackerursachen"),
      factCell("STATUS",  "Bericht abgeliefert · Nachtrag CHF 800 offen"),
    ]}),
  ],
});

const factsRow2 = new Table({
  columnWidths: [3120, 3120, 3120],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({ children: [
      factCell("MESSMETHODIK", "IEC 61000-4-30 Class A · 3× PQMobile5000 · MP-1/2/3"),
      factCell("MESSZEITRAUM", "05.08.–17.08.2026 · 12 Tage · 1.71 Wochen"),
      factCell("DATENBASIS",   "≈ 345'600 3-Sekunden-Werte je Gerät · EN 50160"),
    ]}),
  ],
});

// ---------- Titel ----------
const cover = [
  new Paragraph({
    spacing: { before: 100, after: 40 },
    children: [new TextRun({ text: "GESPRÄCHSVORBEREITUNG · SAMMY BAUMANN", font: FONT, size: 16, color: CYAN, bold: true, characterSpacing: 80 })],
  }),
  new Paragraph({
    spacing: { after: 200 },
    children: [new TextRun({ text: "Bericht Gasthaus Kreuz — Fragen antizipieren, Antworten parat.", font: FONT, size: 30, bold: true, color: NAVY })],
    border: { bottom: { color: NAVY, size: 8, style: BorderStyle.SINGLE, space: 8 } },
  }),
  factsRow,
  new Paragraph({ spacing: { before: 100 }, children: [new TextRun("")] }),
  factsRow2,
];

// ---------- Kernaussagen (Merksätze) ----------
const kernbotschaften = accentBox("DEINE 5 KERNBOTSCHAFTEN · MERKE DIESE SÄTZE", NAVY, [
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60, line: 280 }, children: [
    new TextRun({ text: "Wir haben nicht geraten, wir haben gemessen. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "Normgerecht nach IEC 61000-4-30 Class A. Der Bericht steht auf 345'600 Werten je Gerät.", font: FONT, size: 20, color: INK }),
  ]}),
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60, line: 280 }, children: [
    new TextRun({ text: "Die PV-Anlage ist raus. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "Konstantleistungstest 16.08. hat sie als Verursacherin ausgeschlossen. Ohne die Verlängerung wäre dieser Nachweis nicht möglich gewesen.", font: FONT, size: 20, color: INK }),
  ]}),
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60, line: 280 }, children: [
    new TextRun({ text: "Muster L2 vor L3 vor L1, an zwei Tagen belegt. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "Das ist kein Einzelfall — das sind wiederkehrende Schaltvorgänge im Netz.", font: FONT, size: 20, color: INK }),
  ]}),
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60, line: 280 }, children: [
    new TextRun({ text: "20 konkrete Massnahmen, priorisiert. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "Sammy und der Restaurantbetreiber wissen, was zuerst zu tun ist — mit oder ohne Netzbetreiber.", font: FONT, size: 20, color: INK }),
  ]}),
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { line: 280 }, children: [
    new TextRun({ text: "Der Nachtrag ist zurückhaltend. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "CHF 800 statt der proportionalen CHF 1'320. Sechs von acht Positionen der Grundrechnung sind gar nicht betroffen.", font: FONT, size: 20, color: INK }),
  ]}),
]);

// =========================================================================
// PART A — Fragen zum BERICHT (fachlich)
// =========================================================================

const A_intro = new Paragraph({
  spacing: { after: 140, line: 300, lineRule: LineRuleType.AUTO },
  children: [T("Sammy ist Elektrokontrolleur — er wird auf Norm, Reproduzierbarkeit und klare Zuständigkeit bohren. Halte die Antworten kurz, quantitativ, prüfbar.")],
});

const A1 = qaBlock(
  "A1",
  "Was ist jetzt die konkrete Ursache des Flackerns?",
  [
    "Die Kurzform: wiederkehrende Schaltvorgänge im Netz, nicht im Restaurant.",
    "Belegt durch zwei Ereignisserien an zwei verschiedenen Tagen mit identischem Phasenmuster L2 vor L3 vor L1.",
    "Was intern beim Gastraum-Licht sichtbar wird, ist die Auswirkung — nicht die Ursache.",
  ],
  "neutral",
);

const A2 = qaBlock(
  "A2",
  "Woher wisst ihr sicher, dass es nicht die PV-Anlage ist?",
  [
    "Konstantleistungstest am 16.08.2026: PV lief in einer stabilen Phase, das Flackerereignis trat trotzdem auf.",
    "Wenn die PV Verursacherin wäre, hätte das Ereignis mit ihrer Leistungsänderung korrelieren müssen — tut es nicht.",
    "Genau dieser Test war der Grund, warum die 5 Extra-Tage wertvoll waren.",
  ],
  "neutral",
);

const A3 = qaBlock(
  "A3",
  "Was heisst „L2 vor L3 vor L1” und was sagt das aus?",
  [
    "Reihenfolge, in der die Spannung auf den drei Phasen einbricht.",
    "Ein zufälliges Ereignis hätte kein Muster. Ein wiederholbares Muster deutet auf eine definierte Schaltquelle im Netz.",
    "Zwei Tage, gleiche Reihenfolge = Muster. Ein Tag alleine wäre Zufall gewesen.",
  ],
  "neutral",
);

const A4 = qaBlock(
  "A4",
  "Ist der Bericht norm- und gerichtsverwertbar?",
  [
    "Ja. Messung nach IEC 61000-4-30 Class A, EN-50160-Bewertung über 1.71 Wochen.",
    "Das ist die höchste Genauigkeitsklasse — Class A ist die Ebene, die Netzbetreiber und Gerichte verlangen.",
    "Die Übereinstimmungsberichte je Messpunkt sind separat dokumentiert.",
  ],
  "neutral",
);

const A5 = qaBlock(
  "A5",
  "Welcher Messpunkt zeigt am meisten? Warum drei?",
  [
    "MP-1 Übergabe, MP-2 Restaurant-Beleuchtung, MP-3 Küche/Kälte. Drei Punkte, damit man Ursache und Wirkung trennen kann.",
    "Ohne Übergabe wüssten wir nicht, ob es von aussen kommt. Ohne Beleuchtung wüssten wir nicht, wo es sichtbar wird. Ohne Kälte hätten wir den grössten Hausverbraucher nicht im Bild.",
    "Die zwei Tragen-Ereignisse traten an MP-1 und MP-3 auf — nicht MP-2. Das ist ein weiterer Hinweis: das Flackern kommt nicht aus dem Beleuchtungskreis selbst.",
  ],
  "neutral",
);

const A6 = qaBlock(
  "A6",
  "Was ist mit den Beleuchtungstreibern selbst? Habt ihr die ausgeschlossen?",
  [
    "Wenn es die Treiber wären, müssten die Anomalien am MP-2 (Beleuchtungskreis) am stärksten sein. Sie treten aber an MP-1 und MP-3 auf.",
    "Zusätzlich zeigen die Zeitreihen keine Korrelation mit Ein-/Ausschaltvorgängen im Restaurant.",
    "Das schliesst Treiber-Fehler nicht 100 % aus — es macht sie aber sehr unwahrscheinlich. Für 100 % bräuchte es einen Treibertausch als Konterprobe. Das ist in Massnahme M-12 aufgeführt.",
  ],
  "hard",
);

const A7 = qaBlock(
  "A7",
  "THD? Oberschwingungen? Wie stark ist die Belastung?",
  [
    "Zahlen in den Einzelauswertungen je Messpunkt.",
    "Wenn er es genauer wissen will: „Ich schicke dir die MP-Einzelauswertungen als Anhang, dort sind THDu und THDi je Phase und die 5er/7er/11er-Ordnung tabelliert.”",
    "Nicht auswendig lernen — sagen, wo es steht. Souverän bleiben.",
  ],
  "neutral",
);

const A8 = qaBlock(
  "A8",
  "Was schlägst du dem Restaurant als erstes vor?",
  [
    "Massnahmen M-01 bis M-03 aus dem Katalog: die kostengünstigen, sofort wirksamen Schritte.",
    "Reihenfolge im Massnahmenkatalog ist bewusst nach Kosten/Nutzen sortiert, nicht nach Aufwand.",
    "„Wenn du willst, gehen wir die 20 Massnahmen jetzt zu dritt durch — der Betreiber muss die Priorisierung mittragen.”",
  ],
  "soft",
);

const A9 = qaBlock(
  "A9",
  "Muss der Netzbetreiber eingebunden werden?",
  [
    "Ja. Der Nachweis, dass die Ursache im Netz liegt, ist die Grundlage für ein Gespräch mit dem Netzbetreiber.",
    "Der Schlussbericht ist genau darauf ausgelegt: schriftliche, normkonforme Grundlage.",
    "Ich (Burak) kann bei diesem Gespräch dabei sein, wenn ihr das wollt — das ist ein separates Mandat.",
  ],
  "neutral",
);

const A10 = qaBlock(
  "A10",
  "Was kosten die Massnahmen insgesamt? Wer bezahlt was?",
  [
    "Grobrichtwerte pro Massnahme sind im Katalog. Der Endbetrag hängt vom Setup und den ausgewählten Massnahmen ab.",
    "Zuständigkeiten: Netzbetreiber-Themen (M-14 bis M-20) → Netzbetreiber. Beleuchtungsseite/Steuerungen (M-06 bis M-11) → Betreiber. Prüf- und Nachmessung → Baumann/kabuu.",
    "Klare Aufgabenverteilung ist Teil der Massnahmen-Kurzfassung — genau damit dieses Gespräch nicht mit Fingerzeig endet.",
  ],
  "neutral",
);

// =========================================================================
// PART B — Fragen zum NACHTRAG (Rechnung, Geld)
// =========================================================================

const B_intro = new Paragraph({
  spacing: { after: 140, line: 300, lineRule: LineRuleType.AUTO },
  children: [T("Sammy zahlt. Erwartung: er wird jeden Franken hinterfragen. Rechne mit den harten Formulierungen. Bleibe faktenbasiert — die Herleitung im Nachtrag ist deine stärkste Waffe.")],
});

const B1 = qaBlock(
  "B1",
  "Warum CHF 800 zusätzlich? Wir hatten doch 7 Tage vereinbart.",
  [
    "Weil die Kampagne 12 statt 7 Tage lief — Ferienabwesenheit vor Ort, Abbau vorher nicht möglich.",
    "Verursacht durch die Baustellenlogistik, nicht durch uns — wir haben die Geräte gebunden und die Zeit investiert.",
    "Der Nachtrag umfasst nur die Positionen, die von der Verlängerung betroffen waren: 5 der 8 Rechnungspositionen ändern sich gar nicht.",
  ],
  "hard",
);

const B2 = qaBlock(
  "B2",
  "Warum habt ihr nicht früher gesagt, dass es länger dauert?",
  [
    "Fair — Punkt annehmen: „Die Kommunikation hätten wir früher aktivieren können, das nehme ich mit.”",
    "Fakten dazu: die Verlängerung war eine Reaktion auf die Situation vor Ort. Der Abbau wurde erst am 17.08. möglich.",
    "Wichtig: wir haben die Geräte nicht endlos laufen lassen — wir haben sofort abgebaut, sobald der Zugang da war.",
  ],
  "hard",
);

const B3 = qaBlock(
  "B3",
  "CHF 300 Tagessatz — warum nicht der Preis aus Rechnung 2026-0801?",
  [
    "Der Preis in der Grundrechnung ist ein Paketpreis für 7 Tage — Rüstzeit, Kalibrierung, Ausfallreserve auf 7 Tage verteilt.",
    "Für Zusatzarbeit ohne Paket-Struktur ist der reguläre Tagessatz korrekt. Der Ansatz CHF 300 liegt im Marktbereich für Class-A-Messtechniker.",
    "Wichtig: bei der Gerätebereitstellung (grösste Position, CHF 535.71) haben wir bewusst den Grundrechnungs-Tagessatz CHF 107.14 verwendet — nicht CHF 300. Das ist zurückhaltend gerechnet.",
  ],
  "hard",
);

const B4 = qaBlock(
  "B4",
  "Ist die Rechnung nicht doppelt? Fernüberwachung war doch in Pos 4 der Grundrechnung.",
  [
    "Die Fern-Überwachung in Pos 4 deckt die 7 vereinbarten Tage.",
    "Was hier verrechnet wird, sind die 5 Zusatzkontrollen (0.15 Tag / CHF 45) — nur die zusätzlichen Tage, nicht die ursprünglichen.",
    "Beim Gerätepreis dasselbe: 5 × 107.14 = CHF 535.71 sind exakt die zusätzlichen Tage. Doppelt wäre nichts.",
  ],
  "hard",
);

const B5 = qaBlock(
  "B5",
  "Warum berechnest du dir Auswertung extra, wenn der Bericht sowieso geschrieben wird?",
  [
    "Die Zusatzereignisse vom 16.08.2026 haben eine zusätzliche Analyse-Runde ausgelöst, die in der 7-Tage-Kalkulation nicht enthalten war.",
    "Das ist eine reine Arbeitszeitposition — 0.25 Tag = 2 Stunden. Nicht kalkulierte Zeit, die entstand, weil die Kampagne länger lief.",
    "Ohne diese Extra-Analyse hätten wir den PV-Entlastungsbeweis nicht — der ist ein zentraler Wert des Berichts.",
  ],
  "neutral",
);

const B6 = qaBlock(
  "B6",
  "Der Bericht ist ja auch viel dicker geworden, das rechnest du ja gar nicht.",
  [
    "Stimmt — und das ist Absicht. Der Schlussbericht ist von 20+ auf 61 Seiten gewachsen, dazu drei Einzelauswertungen, Bilddoku, Kurzfassung, Präsentation.",
    "Alles das ist mit Position 6 der Grundrechnung abgegolten. Nicht ein Franken davon steht in der Nachtragsrechnung.",
    "Die letzte Sektion der Herleitung listet das transparent auf — genau damit ihr seht: die Nachforderung ist zurückhaltend, nicht ausgereizt.",
  ],
  "soft",
);

const B7 = qaBlock(
  "B7",
  "Können wir uns auf CHF 500 einigen?",
  [
    "Fallback-Position, wenn er unbedingt verhandeln will:",
    "1. Erste Verteidigungslinie: CHF 800 halten — die Herleitung ist bereits konservativ. „Ich habe schon auf CHF 300 verzichtet, indem ich die Geräte zum Grundrechnungs-Tagessatz eingesetzt habe.”",
    "2. Wenn Beziehung wichtig: „Rundung auf CHF 750” (Rundung neu −55.71). Nicht darunter — CHF 700 wäre unter dem Selbstkostenpunkt.",
    "3. NIE unter CHF 700. Lieber Rechnung stehen lassen und Gespräch verschieben.",
  ],
  "hard",
);

// =========================================================================
// PART C — Wenn Sammy Widerstand zeigt
// =========================================================================

const C_intro = new Paragraph({
  spacing: { after: 140, line: 300, lineRule: LineRuleType.AUTO },
  children: [T("Für die schwierigen Momente. Nicht auswendig lernen — die Haltung merken.")],
});

const C_haltung = accentBox("HALTUNG · IMMER DIESELBE", CYAN, [
  new Paragraph({ spacing: { after: 60, line: 280 }, children: [
    new TextRun({ text: "Sachlich, nicht defensiv. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "Du hast eine normkonforme Messung geliefert. Der Bericht steht. Das ist keine Verhandlungsposition — das ist Fakt.", font: FONT, size: 20, color: INK }),
  ]}),
  new Paragraph({ spacing: { after: 60, line: 280 }, children: [
    new TextRun({ text: "Nie „ich glaube” oder „ich vermute”. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "Immer „die Daten zeigen”, „der Bericht dokumentiert”, „gemessen am”.", font: FONT, size: 20, color: INK }),
  ]}),
  new Paragraph({ spacing: { after: 60, line: 280 }, children: [
    new TextRun({ text: "Kein Deal auf CHF-Ebene ohne Grundlage. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "Wenn Sammy runter will, muss er einen Grund nennen — dann diskutiert ihr die Position, nicht den Betrag.", font: FONT, size: 20, color: INK }),
  ]}),
  new Paragraph({ spacing: { line: 280 }, children: [
    new TextRun({ text: "Persönliches trennen. ", font: FONT, size: 20, bold: true, color: NAVY }),
    new TextRun({ text: "„Lieber Sammy” bleibt lieber Sammy. Rechnung ist Rechnung. Beide Seiten sind Profis.", font: FONT, size: 20, color: INK }),
  ]}),
]);

const C_notaus = accentBox("NOT-AUS · WENN ES ESKALIERT", RED, [
  new Paragraph({ spacing: { after: 60, line: 280 }, children: [T("Wenn Sammy die Rechnung frontal ablehnt oder das Gespräch persönlich wird:")] }),
  new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 }, children: [T("„Sammy, ich will das heute nicht auf dem Rücken der Zusammenarbeit ausmachen. Ich lasse dir die Herleitung nochmal in Ruhe, wir sprechen am [Wochenende] wieder darüber.”")] }),
  new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 }, children: [T("Vertagen ist besser als ein schlechter Deal aus Frust.")] }),
  new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { line: 280 }, children: [T("Die Rechnung ist nicht ans Datum 07.09.2026 gebunden — hierbei bist du in der Zeitfrage flexibel.")] }),
]);

// =========================================================================
// Kompakter Gesprächs-Fahrplan
// =========================================================================

const fahrplanTable = new Table({
  columnWidths: [1500, 3000, 4860],
  width: { size: 9360, type: WidthType.DXA },
  borders: {
    top:    { style: BorderStyle.SINGLE, size: 4, color: NAVY },
    bottom: { style: BorderStyle.SINGLE, size: 4, color: NAVY },
    left:   { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    right:  { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: GREY_L },
    insideVertical:   { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
  },
  rows: [
    new TableRow({
      tableHeader: true,
      children: ["MIN", "PHASE", "WAS DU TUST"].map((t, i) => new TableCell({
        shading: { type: ShadingType.CLEAR, color: "auto", fill: NAVY },
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        width: { size: [1500, 3000, 4860][i], type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: t, font: FONT, size: 16, color: "FFFFFF", bold: true, characterSpacing: 40 })] })],
      })),
    }),
    ...[
      ["0–2",   "Warm-up",                "Persönliche Ebene, keine Fachthemen. Kaffee, Wetter, Familie."],
      ["2–5",   "Anker setzen",           "„Der Bericht steht. 20 Massnahmen, alle prüfbar. Wir haben die Ursache aus dem Restaurant raus verlagert.” Kernbotschaft 1 + 2."],
      ["5–15",  "Fachliche Fragen",       "Antworte präzise, verweise auf die Einzelauswertungen. Antworten aus Teil A."],
      ["15–20", "Übergang zur Rechnung",  "„Zu deinen Fragen zur Nachtragsrechnung — die habe ich transparent hergeleitet, gehen wir Position für Position durch.” "],
      ["20–30", "Rechnung",               "Herleitung als Leitfaden. Antworten aus Teil B. Nicht auf CHF verhandeln — auf Positionen."],
      ["30+",   "Nächste Schritte",       "Termin für Gespräch mit Restaurant-Betreiber und Netzbetreiber-Anschreiben festhalten."],
    ].map((row, ri) => new TableRow({
      children: row.map((c, ci) => new TableCell({
        margins: { top: 90, bottom: 90, left: 140, right: 140 },
        shading: ri % 2 === 1 ? { type: ShadingType.CLEAR, color: "auto", fill: PAPER } : undefined,
        width: { size: [1500, 3000, 4860][ci], type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: c, font: FONT, size: 18, color: ci === 0 ? CYAN : INK, bold: ci <= 1 })] })],
      })),
    })),
  ],
});

// ---------- Assemble ----------
const doc = new Document({
  creator: "kabuu · Burak Ücöz",
  title: "Briefing · Gespräch Sammy Baumann · Bericht Gasthaus Kreuz",
  description: "VERTRAULICH · Interne Gesprächsvorbereitung",
  styles: { default: { document: { run: { font: FONT, size: 20, color: INK } } } },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 240 } }, run: { color: CYAN, bold: true } },
        }],
      },
      {
        reference: "num",
        levels: [{
          level: 0,
          format: LevelFormat.DECIMAL,
          text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 300 } }, run: { color: CYAN, bold: true } },
        }],
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297), orientation: PageOrientation.PORTRAIT },
        margin: {
          top: convertMillimetersToTwip(38),
          bottom: convertMillimetersToTwip(22),
          left: convertMillimetersToTwip(22),
          right: convertMillimetersToTwip(22),
          header: convertMillimetersToTwip(10),
          footer: convertMillimetersToTwip(10),
        },
      },
    },
    headers: { default: header },
    footers: { default: footer },
    children: [
      ...cover,
      h1("Kernbotschaften"),
      kernbotschaften,

      h1("Fahrplan · 30 Minuten"),
      fahrplanTable,

      new Paragraph({ children: [new PageBreak()] }),
      h1("A · Fragen zum Bericht (fachlich)"),
      A_intro,
      ...A1, ...A2, ...A3, ...A4, ...A5, ...A6, ...A7, ...A8, ...A9, ...A10,

      new Paragraph({ children: [new PageBreak()] }),
      h1("B · Fragen zur Nachtragsrechnung"),
      B_intro,
      ...B1, ...B2, ...B3, ...B4, ...B5, ...B6, ...B7,

      new Paragraph({ children: [new PageBreak()] }),
      h1("C · Wenn Sammy Widerstand zeigt"),
      C_intro,
      C_haltung,
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun("")] }),
      C_notaus,
    ],
  }],
});

const outDir = "/home/user/Burak/dokumente";
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, "Briefing_Gespraech_Sammy_Baumann.docx");

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(outPath, buf);
  console.log("wrote", outPath, buf.length, "bytes");
});
