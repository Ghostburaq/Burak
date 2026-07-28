// Build master template DOCX for Burak Ücöz (Power Quality / EMV).
// A4 · Letterhead with logo · brand accent · placeholder-driven.

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, HeadingLevel, PageOrientation, BorderStyle,
  Header, Footer, PageNumber, TabStopType, TabStopPosition,
  ShadingType, VerticalAlign, LevelFormat, convertMillimetersToTwip,
  ExternalHyperlink, LineRuleType,
} = require("docx");

// ---------- Brand ----------
const NAVY   = "0B2545";
const NAVY_D = "081C34";
const CYAN   = "00B8D9";
const CYAN_L = "00E5FF";
const INK    = "0F172A";
const GREY_D = "334155";
const GREY_M = "64748B";
const GREY_L = "E2E8F0";
const PAPER  = "F8FAFC";

const FONT = "Calibri";
const FONT_H = "Calibri";

// ---------- Assets ----------
const BRAND = "/home/user/Burak/assets/brand";
const LOCKUP = fs.readFileSync(path.join(BRAND, "logo_lockup.png"));
const MARK   = fs.readFileSync(path.join(BRAND, "logo_mark_512.png"));

// ---------- Helpers ----------
const T = (text, opts = {}) => new TextRun({ font: FONT, size: 20, color: INK, ...opts, text });

function p(children, opts = {}) {
  return new Paragraph({
    spacing: { before: 0, after: 80, line: 300, lineRule: LineRuleType.AUTO },
    children: Array.isArray(children) ? children : [children],
    ...opts,
  });
}

function h1(text) {
  return new Paragraph({
    spacing: { before: 260, after: 120 },
    children: [new TextRun({ text, font: FONT_H, size: 34, bold: true, color: NAVY })],
    heading: HeadingLevel.HEADING_1,
    border: { bottom: { color: CYAN, size: 12, style: BorderStyle.SINGLE, space: 6 } },
  });
}

function h2(text) {
  return new Paragraph({
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, font: FONT_H, size: 24, bold: true, color: NAVY })],
    heading: HeadingLevel.HEADING_2,
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bulletList", level: 0 },
    spacing: { after: 60, line: 280 },
    children: [T(text)],
  });
}

function placeholder(text) {
  return new TextRun({ text, font: FONT, size: 20, color: GREY_M, italics: true });
}

function borderNone() {
  return {
    top:    { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    left:   { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    right:  { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    insideHorizontal: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    insideVertical:   { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
  };
}

// ---------- Header ----------
const header = new Header({
  children: [
    // Logo lockup, right-aligned, spans full width
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { after: 0 },
      children: [
        new ImageRun({
          data: LOCKUP,
          transformation: { width: 460, height: 115 },
          type: "png",
        }),
      ],
    }),
    // thin accent rule
    new Paragraph({
      spacing: { before: 40, after: 0 },
      border: { bottom: { color: CYAN, size: 8, style: BorderStyle.SINGLE, space: 1 } },
      children: [new TextRun({ text: "", size: 2 })],
    }),
  ],
});

// ---------- Footer ----------
const footer = new Footer({
  children: [
    new Paragraph({
      spacing: { before: 0, after: 40 },
      border: { top: { color: GREY_L, size: 6, style: BorderStyle.SINGLE, space: 4 } },
      children: [new TextRun({ text: "", size: 2 })],
    }),
    new Paragraph({
      alignment: AlignmentType.LEFT,
      tabStops: [
        { type: TabStopType.CENTER, position: 4536 },
        { type: TabStopType.RIGHT,  position: 9072 },
      ],
      children: [
        new TextRun({ text: "Burak Ücöz  ·  Power Quality / EMV", font: FONT, size: 16, color: NAVY, bold: true }),
        new TextRun({ text: "\t[Strasse Nr.] · [PLZ Ort] · [Telefon] · [E-Mail]", font: FONT, size: 16, color: GREY_M }),
        new TextRun({ text: "\tSeite ", font: FONT, size: 16, color: GREY_M }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: NAVY, bold: true }),
        new TextRun({ text: " / ", font: FONT, size: 16, color: GREY_M }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: NAVY, bold: true }),
      ],
    }),
  ],
});

// ---------- Sender / recipient meta block ----------
// Small "sender line" above the address window (Swiss standard)
const senderLine = new Paragraph({
  spacing: { before: 100, after: 40 },
  children: [
    new TextRun({ text: "Burak Ücöz  ·  Power Quality / EMV  ·  ", font: FONT, size: 14, color: GREY_M }),
    new TextRun({ text: "[Strasse Nr.], [PLZ Ort]", font: FONT, size: 14, color: GREY_M }),
  ],
  border: { bottom: { color: GREY_L, size: 4, style: BorderStyle.SINGLE, space: 2 } },
});

// Recipient block (left) + meta box (right) as a 2-col table
const addressAndMeta = new Table({
  columnWidths: [5400, 3960],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({
      children: [
        // Recipient
        new TableCell({
          width: { size: 5400, type: WidthType.DXA },
          margins: { top: 120, bottom: 120, left: 0, right: 200 },
          children: [
            new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "An", font: FONT, size: 14, color: GREY_M, allCaps: true, characterSpacing: 40 })] }),
            new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "[Firma / Anrede]", font: FONT, size: 22, color: INK, bold: true })] }),
            new Paragraph({ spacing: { after: 40 }, children: [placeholder("[Kontaktperson]")] }),
            new Paragraph({ spacing: { after: 40 }, children: [placeholder("[Strasse Nr.]")] }),
            new Paragraph({ spacing: { after: 40 }, children: [placeholder("[PLZ Ort]")] }),
          ],
        }),
        // Meta box with brand accent
        new TableCell({
          width: { size: 3960, type: WidthType.DXA },
          margins: { top: 180, bottom: 180, left: 240, right: 240 },
          shading: { type: ShadingType.CLEAR, color: "auto", fill: PAPER },
          borders: {
            top:    { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
            bottom: { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
            left:   { style: BorderStyle.SINGLE, size: 24, color: CYAN },
            right:  { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
          },
          children: [
            new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "ANGEBOT", font: FONT, size: 16, color: NAVY, bold: true, characterSpacing: 60 })] }),
            new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Nr.  ", font: FONT, size: 18, color: GREY_M }), new TextRun({ text: "[####]", font: FONT, size: 18, color: INK, bold: true })] }),
            new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Datum  ", font: FONT, size: 18, color: GREY_M }), new TextRun({ text: "[TT.MM.JJJJ]", font: FONT, size: 18, color: INK, bold: true })] }),
            new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Gültig bis  ", font: FONT, size: 18, color: GREY_M }), new TextRun({ text: "[TT.MM.JJJJ]", font: FONT, size: 18, color: INK, bold: true })] }),
            new Paragraph({ spacing: { after: 0, before: 60 }, children: [new TextRun({ text: "Sachbearbeiter", font: FONT, size: 14, color: GREY_M, allCaps: true, characterSpacing: 40 })] }),
            new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Burak Ücöz", font: FONT, size: 18, color: INK, bold: true })] }),
            new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: "Power Quality / EMV", font: FONT, size: 16, color: CYAN, bold: true })] }),
          ],
        }),
      ],
    }),
  ],
});

// ---------- Subject block (large, brand accent) ----------
const subject = new Paragraph({
  spacing: { before: 320, after: 40 },
  children: [new TextRun({ text: "ANGEBOT", font: FONT_H, size: 16, color: CYAN, bold: true, characterSpacing: 80 })],
});
const subjectLine = new Paragraph({
  spacing: { before: 0, after: 240 },
  children: [new TextRun({ text: "[Titel des Angebots — z. B. Netzanalyse und Beurteilung der Spannungsqualität]", font: FONT_H, size: 32, bold: true, color: NAVY })],
  border: { bottom: { color: NAVY, size: 8, style: BorderStyle.SINGLE, space: 8 } },
});

// ---------- Salutation + intro ----------
const salutation = p([new TextRun({ text: "Sehr geehrte/r [Anrede Nachname]", font: FONT, size: 22, color: INK })], { spacing: { before: 120, after: 160 } });
const intro = p([placeholder("[Ein bis zwei Sätze Einstieg: Bezugnahme auf Gespräch/Anfrage, Dank für Vertrauen, Ziel des Angebots.]")]);

// ---------- Section 1: Ausgangslage ----------
const s1 = [
  h1("1  Ausgangslage"),
  p([placeholder("[Kurze, präzise Beschreibung der Situation beim Kunden: was beobachtet wurde, wann, wo, unter welchen Bedingungen. Ursachen bleiben offen — sie werden erst gemessen.]")]),
];

// ---------- Section 2: Vorgehen ----------
const s2 = [
  h1("2  Vorgehen"),
  p([placeholder("[Beschreibung der Methode. Standard-Textbaustein z. B.:]")]),
  p([T("Normgerechte Messung der Spannungsqualität nach ", { color: INK }),
     T("IEC 61000-4-30 Class A", { bold: true, color: NAVY }),
     T(". [N] Messgeräte zeichnen über [X] Tage gleichzeitig an folgenden Messpunkten auf:")]),
  bullet("[Messpunkt 1 — z. B. Übergabepunkt]"),
  bullet("[Messpunkt 2 — z. B. Verbraucher / Stromkreis]"),
  bullet("[Messpunkt 3 — z. B. grösserer Einzelverbraucher]"),
  p([placeholder("[Fernüberwachung während der Messung, Auswertung, schriftlicher Bericht mit Befund und Empfehlung.]")]),
];

// ---------- Section 3: Leistungsumfang & Preis (styled table) ----------
function money(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.RIGHT,
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: FONT, size: 20, color: INK, ...opts })],
  });
}
function cell(text, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: FONT, size: 20, color: opts.color || INK, bold: !!opts.bold })],
  });
}

function headerCell(text, opts = {}) {
  return new TableCell({
    shading: { type: ShadingType.CLEAR, color: "auto", fill: NAVY },
    margins: { top: 120, bottom: 120, left: 140, right: 140 },
    verticalAlign: VerticalAlign.CENTER,
    width: opts.width,
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({ text, font: FONT, size: 18, color: "FFFFFF", bold: true, characterSpacing: 40 })],
    })],
  });
}

function bodyCell(text, opts = {}) {
  return new TableCell({
    shading: opts.zebra ? { type: ShadingType.CLEAR, color: "auto", fill: PAPER } : undefined,
    margins: { top: 90, bottom: 90, left: 140, right: 140 },
    verticalAlign: VerticalAlign.CENTER,
    width: opts.width,
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({ text, font: FONT, size: 20, color: opts.color || INK, bold: !!opts.bold })],
    })],
  });
}

function totalCell(text, opts = {}) {
  return new TableCell({
    shading: { type: ShadingType.CLEAR, color: "auto", fill: opts.strong ? NAVY : "EAF7FB" },
    margins: { top: 120, bottom: 120, left: 140, right: 140 },
    verticalAlign: VerticalAlign.CENTER,
    width: opts.width,
    borders: {
      top: { style: BorderStyle.SINGLE, size: opts.strong ? 12 : 6, color: opts.strong ? NAVY : CYAN },
      bottom: { style: BorderStyle.SINGLE, size: opts.strong ? 12 : 6, color: opts.strong ? NAVY : CYAN },
      left: { style: BorderStyle.SINGLE, size: 4, color: opts.strong ? NAVY : CYAN },
      right: { style: BorderStyle.SINGLE, size: 4, color: opts.strong ? NAVY : CYAN },
    },
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({ text, font: FONT, size: opts.strong ? 22 : 20, color: opts.strong ? "FFFFFF" : NAVY, bold: true })],
    })],
  });
}

const COL_POS   = 700;
const COL_DESC  = 6660;
const COL_PRICE = 2000;
const TABLE_W   = COL_POS + COL_DESC + COL_PRICE;

function itemRow(pos, desc, price, zebra) {
  return new TableRow({
    children: [
      bodyCell(pos,   { width: { size: COL_POS,   type: WidthType.DXA }, align: AlignmentType.CENTER, color: GREY_M, bold: true, zebra }),
      bodyCell(desc,  { width: { size: COL_DESC,  type: WidthType.DXA }, zebra }),
      bodyCell(price, { width: { size: COL_PRICE, type: WidthType.DXA }, align: AlignmentType.RIGHT, zebra }),
    ],
  });
}

const offerTable = new Table({
  columnWidths: [COL_POS, COL_DESC, COL_PRICE],
  width: { size: TABLE_W, type: WidthType.DXA },
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
      children: [
        headerCell("POS",       { width: { size: COL_POS,   type: WidthType.DXA }, align: AlignmentType.CENTER }),
        headerCell("LEISTUNG",  { width: { size: COL_DESC,  type: WidthType.DXA } }),
        headerCell("CHF",       { width: { size: COL_PRICE, type: WidthType.DXA }, align: AlignmentType.RIGHT }),
      ],
    }),
    itemRow("1", "[Leistung 1 — z. B. Vorbesprechung und Augenschein vor Ort]", "[inkl.]", false),
    itemRow("2", "[Leistung 2 — z. B. Messplanung und Vorbereitung]",           "[    0]", true),
    itemRow("3", "[Leistung 3 — z. B. Installation Messtechnik]",               "[    0]", false),
    itemRow("4", "[Leistung 4 — z. B. Messung über X Tage, Class A]",           "[    0]", true),
    itemRow("5", "[Leistung 5 — z. B. Abbau Messtechnik]",                      "[    0]", false),
    itemRow("6", "[Leistung 6 — z. B. Auswertung und schriftlicher Bericht]",   "[    0]", true),
    itemRow("7", "[Leistung 7 — z. B. Ergebnisbesprechung]",                    "[inkl.]", false),
    itemRow("8", "[Leistung 8 — z. B. Anfahrten]",                              "[    0]", true),
    // Subtotal
    new TableRow({
      children: [
        totalCell("",                  { width: { size: COL_POS, type: WidthType.DXA } }),
        totalCell("Zwischensumme netto", { width: { size: COL_DESC, type: WidthType.DXA } }),
        totalCell("[0.00]",            { width: { size: COL_PRICE, type: WidthType.DXA }, align: AlignmentType.RIGHT }),
      ],
    }),
    // MWST
    new TableRow({
      children: [
        bodyCell("", { width: { size: COL_POS, type: WidthType.DXA } }),
        bodyCell("MWST 8,1 %", { width: { size: COL_DESC, type: WidthType.DXA }, color: GREY_D }),
        bodyCell("[0.00]", { width: { size: COL_PRICE, type: WidthType.DXA }, align: AlignmentType.RIGHT, color: GREY_D }),
      ],
    }),
    // Grand total
    new TableRow({
      children: [
        totalCell("",  { width: { size: COL_POS, type: WidthType.DXA },   strong: true }),
        totalCell("TOTAL INKL. MWST", { width: { size: COL_DESC, type: WidthType.DXA }, strong: true }),
        totalCell("CHF  [0.00]", { width: { size: COL_PRICE, type: WidthType.DXA }, align: AlignmentType.RIGHT, strong: true }),
      ],
    }),
  ],
});

const s3 = [
  h1("3  Leistungsumfang und Preis"),
  offerTable,
  new Paragraph({
    spacing: { before: 160, after: 40 },
    children: [
      new TextRun({ text: "Pauschal-Festpreis. ", font: FONT, size: 18, color: NAVY, bold: true }),
      new TextRun({ text: "Alle Beträge in CHF, Preise exkl. MWST; die gesetzliche MWST von 8,1 % ist separat ausgewiesen.", font: FONT, size: 18, color: GREY_D }),
    ],
  }),
];

// ---------- Section 4: Nutzen (2-col benefit tiles) ----------
function benefitTile(label, body) {
  return new TableCell({
    margins: { top: 200, bottom: 200, left: 220, right: 220 },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: PAPER },
    borders: {
      top:    { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
      left:   { style: BorderStyle.SINGLE, size: 24, color: CYAN },
      right:  { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
    },
    width: { size: 4680, type: WidthType.DXA },
    children: [
      new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: label, font: FONT, size: 22, bold: true, color: NAVY })] }),
      new Paragraph({ children: [new TextRun({ text: body, font: FONT, size: 18, color: GREY_D })] }),
    ],
  });
}

const benefits = new Table({
  columnWidths: [4680, 4680],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({
      children: [
        benefitTile("Normgerecht", "Objektiver Befund nach IEC 61000-4-30 Class A — statt Vermutungen."),
        benefitTile("Belastbar", "Schriftliche Grundlage, verwendbar auch gegenüber dem Netzbetreiber."),
      ],
    }),
    new TableRow({
      children: [
        benefitTile("Faktenbasiert", "Kein Einbau von Komponenten auf Verdacht: zuerst Fakten, dann Entscheid."),
        benefitTile("Kostentransparent", "Fixer Pauschalpreis mit voller Kostentransparenz."),
      ],
    }),
  ],
});

const s4 = [
  h1("4  Ihr Nutzen"),
  new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "" })] }),
  benefits,
];

// ---------- Section 5: Termin ----------
const s5 = [
  h1("5  Termin und nächste Schritte"),
  p([placeholder("[Terminvorschlag inkl. Datum, Uhrzeit, Dauer. Hinweis auf Bestätigung durch den Kunden. Ablauf ausserhalb der Stosszeiten.]")]),
];

// ---------- Section 6: Konditionen ----------
const s6 = [
  h1("6  Konditionen"),
  bullet("Gültigkeit dieses Angebots: bis [TT.MM.JJJJ]."),
  bullet("Preise exkl. MWST, in CHF. Zahlbar innert 30 Tagen netto nach Schlussrechnung."),
  bullet("Arbeiten an der elektrischen Anlage erfolgen fachgerecht nach den geltenden Schweizer Vorschriften (NIN, NIV, ESTI)."),
  bullet("[Weitere Konditionen bei Bedarf.]"),
];

// ---------- Closing + signature ----------
const closing = [
  new Paragraph({
    spacing: { before: 300, after: 120 },
    children: [T("Für Fragen stehe ich Ihnen gerne zur Verfügung. Ich freue mich darauf, das Vorhaben für Sie sauber zu klären.")],
  }),
  new Paragraph({
    spacing: { before: 120, after: 40 },
    children: [T("Freundliche Grüsse")],
  }),
  new Paragraph({
    spacing: { before: 240, after: 0 },
    children: [new TextRun({ text: "Burak Ücöz", font: FONT, size: 22, bold: true, color: NAVY })],
  }),
  new Paragraph({
    spacing: { before: 0, after: 200 },
    children: [new TextRun({ text: "Power Quality / EMV", font: FONT, size: 18, color: CYAN, bold: true })],
  }),
];

// ---------- Signature block table ----------
const signBlock = new Table({
  columnWidths: [4680, 4680],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({
      children: [
        new TableCell({
          width: { size: 4680, type: WidthType.DXA },
          margins: { top: 400, bottom: 60, left: 0, right: 200 },
          borders: {
            top:    { style: BorderStyle.SINGLE, size: 8, color: NAVY },
            bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            left:   { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            right:  { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
          },
          children: [
            new Paragraph({ children: [new TextRun({ text: "Auftrag erteilt (Ort, Datum)", font: FONT, size: 16, color: GREY_M, allCaps: true, characterSpacing: 40 })] }),
          ],
        }),
        new TableCell({
          width: { size: 4680, type: WidthType.DXA },
          margins: { top: 400, bottom: 60, left: 200, right: 0 },
          borders: {
            top:    { style: BorderStyle.SINGLE, size: 8, color: NAVY },
            bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            left:   { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            right:  { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
          },
          children: [
            new Paragraph({ children: [new TextRun({ text: "Unterschrift Auftraggeber", font: FONT, size: 16, color: GREY_M, allCaps: true, characterSpacing: 40 })] }),
          ],
        }),
      ],
    }),
  ],
});

const signHint = new Paragraph({
  spacing: { before: 80, after: 0 },
  children: [new TextRun({ text: "Bitte unterschrieben zurück an: ", font: FONT, size: 16, color: GREY_M }),
             new TextRun({ text: "[E-Mail-Adresse]", font: FONT, size: 16, color: NAVY, bold: true })],
});

// ---------- Assemble ----------
const doc = new Document({
  creator: "Burak Ücöz",
  title: "Angebot — Master-Vorlage",
  description: "Master-Vorlage Angebot · Power Quality / EMV",
  styles: {
    default: {
      document: { run: { font: FONT, size: 20, color: INK } },
    },
  },
  numbering: {
    config: [{
      reference: "bulletList",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 240 } }, run: { color: CYAN, bold: true } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297), orientation: PageOrientation.PORTRAIT },
        margin: {
          top: convertMillimetersToTwip(38),
          bottom: convertMillimetersToTwip(24),
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
      senderLine,
      addressAndMeta,
      subject,
      subjectLine,
      salutation,
      intro,
      ...s1,
      ...s2,
      ...s3,
      ...s4,
      ...s5,
      ...s6,
      ...closing,
      signBlock,
      signHint,
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const out = "/tmp/claude-0/-home-user-Burak/46ddb8f6-3a80-5bec-8750-09b482cd88ea/scratchpad/Angebot_Master_Vorlage.docx";
  fs.writeFileSync(out, buf);
  console.log("wrote", out, buf.length, "bytes");
});
