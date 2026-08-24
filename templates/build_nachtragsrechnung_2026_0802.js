// Nachtragsrechnung 2026-0802 · Baumann Elektrokontrollen GmbH
// Verlängerte Messdauer · Netzqualitätsmessung Gasthaus Kreuz, Zuzwil SG
// Aufgesetzt auf dem kabuu-Master-Look (Header, Footer, Meta-Box, Farb-Akzent).

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
const CYAN_S = "EAF7FB";  // soft cyan tint for highlights

const FONT = "Calibri";

// ---------- Static info ----------
const SENDER = {
  brand:   "kabuu",
  role:    "Netzqualität & EMV Messungen · Engineering",
  name:    "Burak Ücöz",
  street:  "Im Abt 9 A",
  city:    "8240 Thayngen",
  phone:   "+41 79 512 98 07",
  email:   "engineering.kabuu@gmail.com",
  iban:    "CH33 0840 1000 0693 4279 2",
};

// ---------- Assets ----------
const BRAND_DIR = "/home/user/Burak/assets/brand";
const LOCKUP    = fs.readFileSync(path.join(BRAND_DIR, "kabuu_logo_mono.png"));

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
    spacing: { before: 300, after: 160 },
    children: [new TextRun({ text, font: FONT, size: 34, bold: true, color: NAVY })],
    heading: HeadingLevel.HEADING_1,
    border: { bottom: { color: CYAN, size: 12, style: BorderStyle.SINGLE, space: 6 } },
  });
}
function h2(text) {
  return new Paragraph({
    spacing: { before: 260, after: 100 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true, color: NAVY })],
    heading: HeadingLevel.HEADING_2,
  });
}
function borderNone() {
  const n = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: n, bottom: n, left: n, right: n, insideHorizontal: n, insideVertical: n };
}
function cellText(text, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: 40, after: 40 },
    children: [new TextRun({
      text, font: FONT,
      size: opts.size || 20,
      color: opts.color || INK,
      bold: !!opts.bold,
      italics: !!opts.italics,
    })],
  });
}

// ---------- Header ----------
const header = new Header({
  children: [
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { after: 0 },
      children: [new ImageRun({
        data: LOCKUP,
        transformation: { width: 190, height: 122 },
        type: "png",
      })],
    }),
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
        new TextRun({ text: `${SENDER.brand}  ·  ${SENDER.role}`, font: FONT, size: 16, color: NAVY, bold: true }),
        new TextRun({ text: `\t${SENDER.street} · ${SENDER.city} · ${SENDER.phone} · ${SENDER.email}`, font: FONT, size: 16, color: GREY_M }),
        new TextRun({ text: "\tSeite ", font: FONT, size: 16, color: GREY_M }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: NAVY, bold: true }),
        new TextRun({ text: " / ", font: FONT, size: 16, color: GREY_M }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: NAVY, bold: true }),
      ],
    }),
  ],
});

// ---------- Sender line + address/meta ----------
const senderLine = new Paragraph({
  spacing: { before: 100, after: 40 },
  children: [
    new TextRun({ text: `${SENDER.brand}  ·  ${SENDER.role}  ·  ${SENDER.name}  ·  `, font: FONT, size: 14, color: GREY_M }),
    new TextRun({ text: `${SENDER.street}, ${SENDER.city}`, font: FONT, size: 14, color: GREY_M }),
  ],
  border: { bottom: { color: GREY_L, size: 4, style: BorderStyle.SINGLE, space: 2 } },
});

function addressAndMeta() {
  return new Table({
    columnWidths: [5400, 3960],
    width: { size: 9360, type: WidthType.DXA },
    borders: borderNone(),
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: 5400, type: WidthType.DXA },
            margins: { top: 120, bottom: 120, left: 0, right: 200 },
            children: [
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "An", font: FONT, size: 14, color: GREY_M, allCaps: true, characterSpacing: 40 })] }),
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Baumann Elektrokontrollen GmbH", font: FONT, size: 22, color: INK, bold: true })] }),
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Herr Sammy Baumann", font: FONT, size: 20, color: INK })] }),
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Hirschenstrasse 17", font: FONT, size: 20, color: INK })] }),
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "9200 Gossau", font: FONT, size: 20, color: INK })] }),
            ],
          }),
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
              new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "NACHTRAGSRECHNUNG", font: FONT, size: 16, color: NAVY, bold: true, characterSpacing: 60 })] }),
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Nr.  ", font: FONT, size: 18, color: GREY_M }), new TextRun({ text: "2026-0802", font: FONT, size: 18, color: INK, bold: true })] }),
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Datum  ", font: FONT, size: 18, color: GREY_M }), new TextRun({ text: "24.08.2026", font: FONT, size: 18, color: INK, bold: true })] }),
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Zahlbar bis  ", font: FONT, size: 18, color: GREY_M }), new TextRun({ text: "07.09.2026", font: FONT, size: 18, color: INK, bold: true })] }),
              new Paragraph({ spacing: { after: 0, before: 60 }, children: [new TextRun({ text: "Sachbearbeiter", font: FONT, size: 14, color: GREY_M, allCaps: true, characterSpacing: 40 })] }),
              new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Burak Ücöz", font: FONT, size: 18, color: INK, bold: true })] }),
              new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: "Netzqualität & EMV Messungen", font: FONT, size: 16, color: NAVY, bold: true })] }),
            ],
          }),
        ],
      }),
    ],
  });
}

// ---------- Place / date on top-right style line ----------
const dateLine = new Paragraph({
  spacing: { before: 200, after: 0 },
  alignment: AlignmentType.RIGHT,
  children: [new TextRun({ text: "Thayngen, 24.08.2026", font: FONT, size: 18, color: GREY_D })],
});

// ---------- Subject block ----------
const subjectKicker = new Paragraph({
  spacing: { before: 260, after: 40 },
  children: [new TextRun({ text: "NACHTRAGSRECHNUNG · 2026-0802", font: FONT, size: 16, color: CYAN, bold: true, characterSpacing: 80 })],
});
const subjectLine = new Paragraph({
  spacing: { before: 0, after: 240 },
  children: [new TextRun({ text: "Verlängerte Messdauer — Netzqualitätsmessung Gasthaus Kreuz, Zuzwil SG", font: FONT, size: 30, bold: true, color: NAVY })],
  border: { bottom: { color: NAVY, size: 8, style: BorderStyle.SINGLE, space: 8 } },
});

// ---------- Meta-facts row (Bezug / Objekt / Zeitraum) ----------
function fact(label, body) {
  return new TableCell({
    margins: { top: 160, bottom: 160, left: 200, right: 200 },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: PAPER },
    borders: {
      top:    { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
      left:   { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
      right:  { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
    },
    width: { size: 3120, type: WidthType.DXA },
    children: [
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: label, font: FONT, size: 14, color: CYAN, bold: true, allCaps: true, characterSpacing: 60 })] }),
      new Paragraph({ children: [new TextRun({ text: body, font: FONT, size: 18, color: INK })] }),
    ],
  });
}

const factsRow = new Table({
  columnWidths: [3120, 3120, 3120],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({
      children: [
        fact("BEZUG",             "Rechnung 2026-0801 vom 04.08.2026 über CHF 1'850.00"),
        fact("OBJEKT",            "Gasthaus Kreuz, Oberdorfstrasse 16, 9524 Zuzwil SG"),
        fact("LEISTUNGSZEITRAUM", "05.08.2026 bis 17.08.2026 (verlängerte Messdauer)"),
      ],
    }),
  ],
});

// ---------- Salutation + intro ----------
const salutation = new Paragraph({
  spacing: { before: 280, after: 140 },
  children: [new TextRun({ text: "Sehr geehrter Herr Baumann, lieber Sammy", font: FONT, size: 22, color: INK })],
});
const intro = new Paragraph({
  spacing: { after: 160, line: 300, lineRule: LineRuleType.AUTO },
  children: [T("Die Messkampagne im Gasthaus Kreuz lief vom 05.08. bis 17.08.2026 und damit über 12 statt der vereinbarten 7 Tage. Grund war die Ferienabwesenheit vor Ort; der Abbau war früher nicht möglich. Auf deinen Wunsch verrechne ich den daraus entstandenen Mehraufwand nach. Die Herleitung findest du auf der zweiten Seite, sie stützt sich ausschliesslich auf die Ansätze der bestehenden Rechnung.")],
});

// ---------- Position table (Rechnung) ----------
function headerCell(text, w, align) {
  return new TableCell({
    shading: { type: ShadingType.CLEAR, color: "auto", fill: NAVY },
    margins: { top: 120, bottom: 120, left: 140, right: 140 },
    verticalAlign: VerticalAlign.CENTER,
    width: { size: w, type: WidthType.DXA },
    children: [new Paragraph({ alignment: align || AlignmentType.LEFT, children: [new TextRun({ text, font: FONT, size: 18, color: "FFFFFF", bold: true, characterSpacing: 40 })] })],
  });
}
function bodyCell(text, w, opts = {}) {
  return new TableCell({
    shading: opts.zebra ? { type: ShadingType.CLEAR, color: "auto", fill: PAPER } : undefined,
    margins: { top: 90, bottom: 90, left: 140, right: 140 },
    verticalAlign: VerticalAlign.CENTER,
    width: { size: w, type: WidthType.DXA },
    children: [new Paragraph({ alignment: opts.align || AlignmentType.LEFT, children: [new TextRun({ text, font: FONT, size: opts.size || 20, color: opts.color || INK, bold: !!opts.bold, italics: !!opts.italics })] })],
  });
}
function totalCell(text, w, opts = {}) {
  return new TableCell({
    shading: { type: ShadingType.CLEAR, color: "auto", fill: opts.strong ? NAVY : CYAN_S },
    margins: { top: 120, bottom: 120, left: 140, right: 140 },
    verticalAlign: VerticalAlign.CENTER,
    width: { size: w, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: opts.strong ? 12 : 6, color: opts.strong ? NAVY : CYAN },
      bottom: { style: BorderStyle.SINGLE, size: opts.strong ? 12 : 6, color: opts.strong ? NAVY : CYAN },
      left: { style: BorderStyle.SINGLE, size: 4, color: opts.strong ? NAVY : CYAN },
      right: { style: BorderStyle.SINGLE, size: 4, color: opts.strong ? NAVY : CYAN },
    },
    children: [new Paragraph({ alignment: opts.align || AlignmentType.LEFT, children: [new TextRun({ text, font: FONT, size: opts.strong ? 22 : 20, color: opts.strong ? "FFFFFF" : NAVY, bold: true })] })],
  });
}

// Column widths for main invoice table
const CI_POS = 700, CI_DESC = 5200, CI_RATE = 1800, CI_AMT = 1660;
const CI_TOTAL = CI_POS + CI_DESC + CI_RATE + CI_AMT;

function invRow(pos, desc, rate, amt, zebra) {
  return new TableRow({
    children: [
      bodyCell(pos,  CI_POS,  { align: AlignmentType.CENTER, color: GREY_M, bold: true, zebra }),
      bodyCell(desc, CI_DESC, { zebra }),
      bodyCell(rate, CI_RATE, { align: AlignmentType.RIGHT, color: GREY_D, zebra }),
      bodyCell(amt,  CI_AMT,  { align: AlignmentType.RIGHT, zebra, bold: true }),
    ],
  });
}

const invoiceTable = new Table({
  columnWidths: [CI_POS, CI_DESC, CI_RATE, CI_AMT],
  width: { size: CI_TOTAL, type: WidthType.DXA },
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
        headerCell("POS",      CI_POS,  AlignmentType.CENTER),
        headerCell("LEISTUNG", CI_DESC),
        headerCell("ANSATZ",   CI_RATE, AlignmentType.RIGHT),
        headerCell("CHF",      CI_AMT,  AlignmentType.RIGHT),
      ],
    }),
    invRow("1", "Gerätebereitstellung 3× PQMobile5000 Class A, 5 zusätzliche Messtage, inkl. Fernüberwachung", "5 × 107.14", "535.71", false),
    invRow("2", "Auswertung, dauerabhängiger Anteil bei 12 statt 7 Tagen Datenbasis", "350 × 40 % × 5/7", "100.00", true),
    // Zwischensumme
    new TableRow({
      children: [
        totalCell("",              CI_POS),
        totalCell("Zwischensumme", CI_DESC),
        totalCell("",              CI_RATE),
        totalCell("635.71",        CI_AMT, { align: AlignmentType.RIGHT }),
      ],
    }),
    // Rundung
    new TableRow({
      children: [
        bodyCell("",         CI_POS),
        bodyCell("Rundung",  CI_DESC, { color: GREY_D }),
        bodyCell("",         CI_RATE),
        bodyCell("−0.71",    CI_AMT,  { align: AlignmentType.RIGHT, color: GREY_D }),
      ],
    }),
    // Total
    new TableRow({
      children: [
        totalCell("",                    CI_POS,  { strong: true }),
        totalCell("TOTAL OHNE MWST",     CI_DESC, { strong: true }),
        totalCell("",                    CI_RATE, { strong: true }),
        totalCell("CHF  635.00",         CI_AMT,  { align: AlignmentType.RIGHT, strong: true }),
      ],
    }),
  ],
});

// ---------- Gesamtprojekt comparison strip ----------
function projStripCell(label, amount, opts = {}) {
  const fill = opts.total ? NAVY : PAPER;
  const color = opts.total ? "FFFFFF" : NAVY;
  const labelColor = opts.total ? "B5D5E0" : GREY_M;
  return new TableCell({
    width: { size: 3120, type: WidthType.DXA },
    margins: { top: 200, bottom: 200, left: 220, right: 220 },
    shading: { type: ShadingType.CLEAR, color: "auto", fill },
    borders: {
      top:    { style: BorderStyle.SINGLE, size: opts.total ? 12 : 4, color: opts.total ? NAVY : GREY_L },
      bottom: { style: BorderStyle.SINGLE, size: opts.total ? 12 : 4, color: opts.total ? NAVY : GREY_L },
      left:   { style: BorderStyle.SINGLE, size: opts.total ? 12 : 4, color: opts.total ? NAVY : GREY_L },
      right:  { style: BorderStyle.SINGLE, size: opts.total ? 12 : 4, color: opts.total ? NAVY : GREY_L },
    },
    children: [
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: label, font: FONT, size: 14, color: labelColor, bold: true, allCaps: true, characterSpacing: 60 })] }),
      new Paragraph({ children: [new TextRun({ text: amount, font: FONT, size: 26, color, bold: true })] }),
    ],
  });
}

const projStrip = new Table({
  columnWidths: [3120, 3120, 3120],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({
      children: [
        projStripCell("Rechnung 2026-0801", "CHF 1'850.00"),
        projStripCell("Nachtrag 2026-0802", "CHF 635.00"),
        projStripCell("Gesamtsumme Projekt", "CHF 2'485.00", { total: true }),
      ],
    }),
  ],
});

// ---------- MWST + IBAN ----------
const mwstNote = new Paragraph({
  spacing: { before: 200, after: 60 },
  children: [
    new TextRun({ text: "Nicht MWST-pflichtig ", font: FONT, size: 18, color: NAVY, bold: true }),
    new TextRun({ text: "gemäss Art. 10 Abs. 2 MWSTG.", font: FONT, size: 18, color: GREY_D }),
  ],
});

function ibanBlock() {
  return new Table({
    columnWidths: [9360],
    width: { size: 9360, type: WidthType.DXA },
    borders: borderNone(),
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: 9360, type: WidthType.DXA },
            margins: { top: 220, bottom: 220, left: 260, right: 260 },
            shading: { type: ShadingType.CLEAR, color: "auto", fill: PAPER },
            borders: {
              top:    { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
              bottom: { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
              left:   { style: BorderStyle.SINGLE, size: 24, color: NAVY },
              right:  { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
            },
            children: [
              new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "ZAHLUNG", font: FONT, size: 14, color: NAVY, bold: true, allCaps: true, characterSpacing: 60 })] }),
              new Paragraph({ spacing: { after: 40 }, children: [
                new TextRun({ text: "Zahlbar innert 14 Tagen auf ", font: FONT, size: 18, color: INK }),
                new TextRun({ text: `IBAN ${SENDER.iban}`, font: FONT, size: 18, color: NAVY, bold: true }),
                new TextRun({ text: `, lautend auf ${SENDER.name}, ${SENDER.city}.`, font: FONT, size: 18, color: INK }),
              ]}),
              new Paragraph({ children: [new TextRun({ text: "Der Zahlteil auf der letzten Seite kann im E-Banking gescannt werden.", font: FONT, size: 16, color: GREY_D, italics: true })] }),
            ],
          }),
        ],
      }),
    ],
  });
}

// ---------- Closing ----------
const closing = [
  new Paragraph({
    spacing: { before: 260, after: 120, line: 300, lineRule: LineRuleType.AUTO },
    children: [T("Besten Dank für das Vertrauen und die unkomplizierte Zusammenarbeit. Freundliche Grüsse")],
  }),
  new Paragraph({
    spacing: { before: 240, after: 0 },
    children: [new TextRun({ text: "Burak Ücöz", font: FONT, size: 22, bold: true, color: NAVY })],
  }),
  new Paragraph({
    spacing: { before: 0, after: 100 },
    children: [new TextRun({ text: "kabuu — Netzqualität & EMV Messungen · Engineering", font: FONT, size: 18, color: NAVY, bold: true })],
  }),
];

// ---------- PAGE 2 · Herleitung ----------
const pageBreak = new Paragraph({ children: [new PageBreak()] });

const herleitungIntro = new Paragraph({
  spacing: { after: 200, line: 300, lineRule: LineRuleType.AUTO },
  children: [T("Damit die Nachforderung nachvollziehbar bleibt, ist sie nicht neu kalkuliert, sondern vollständig aus den Ansätzen der Rechnung 2026-0801 abgeleitet.")],
});

// ---- Generic table builder ----
function makeTable(columnWidths, headerCells, dataRows) {
  const totalW = columnWidths.reduce((a, b) => a + b, 0);
  return new Table({
    columnWidths,
    width: { size: totalW, type: WidthType.DXA },
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
        children: headerCells.map(({ text, align }, i) => headerCell(text, columnWidths[i], align)),
      }),
      ...dataRows.map((row, ri) => new TableRow({
        children: row.map((c, ci) => bodyCell(c.text, columnWidths[ci], {
          align: c.align,
          bold: c.bold,
          color: c.color,
          zebra: ri % 2 === 1,
        })),
      })),
    ],
  });
}

// Section 1: Sachverhalt
const S1_W = [2600, 3200, 3560];
const s1Table = makeTable(
  S1_W,
  [{ text: "ANGABE" }, { text: "VEREINBART" }, { text: "TATSÄCHLICH" }],
  [
    [{ text: "Messdauer", bold: true }, { text: "7 Tage" }, { text: "12 Tage" }],
    [{ text: "Zeitraum",  bold: true }, { text: "—", color: GREY_M }, { text: "05.08. bis 17.08.2026" }],
    [{ text: "Mehrdauer", bold: true }, { text: "—", color: GREY_M }, { text: "5 Tage (entspricht 71 %)" }],
    [{ text: "Grund",     bold: true }, { text: "—", color: GREY_M }, { text: "Ferienabwesenheit vor Ort, Abbau früher nicht möglich" }],
    [{ text: "Veranlassung", bold: true }, { text: "—", color: GREY_M }, { text: "nicht durch den Auftraggeber" }],
  ]
);

// Section 2: Betroffene Positionen
const S2_W = [700, 4200, 1400, 3060];
const s2Table = makeTable(
  S2_W,
  [{ text: "POS", align: AlignmentType.CENTER }, { text: "LEISTUNG AUS RECHNUNG 2026-0801" }, { text: "BETROFFEN", align: AlignmentType.CENTER }, { text: "BEGRÜNDUNG" }],
  [
    [{ text: "1", align: AlignmentType.CENTER, color: GREY_M, bold: true }, { text: "Augenschein vom 24.06.2026" }, { text: "nein",  align: AlignmentType.CENTER, color: GREY_D }, { text: "fand vor der Messung statt" }],
    [{ text: "2", align: AlignmentType.CENTER, color: GREY_M, bold: true }, { text: "Messplanung und Konfiguration" }, { text: "nein", align: AlignmentType.CENTER, color: GREY_D }, { text: "einmalig vor Messbeginn" }],
    [{ text: "3", align: AlignmentType.CENTER, color: GREY_M, bold: true }, { text: "Installation an drei Messpunkten" }, { text: "nein", align: AlignmentType.CENTER, color: GREY_D }, { text: "einmalig, unverändert" }],
    [{ text: "4", align: AlignmentType.CENTER, color: GREY_M, bold: true }, { text: "Messkampagne 7 Tage, 3 Geräte, inkl. Fernüberwachung" }, { text: "ja", align: AlignmentType.CENTER, color: NAVY, bold: true }, { text: "12 statt 7 Tage" }],
    [{ text: "5", align: AlignmentType.CENTER, color: GREY_M, bold: true }, { text: "Abbau der Messtechnik" }, { text: "nein", align: AlignmentType.CENTER, color: GREY_D }, { text: "einmalig, nur später ausgeführt" }],
    [{ text: "6", align: AlignmentType.CENTER, color: GREY_M, bold: true }, { text: "Auswertung und Bericht" }, { text: "ja", align: AlignmentType.CENTER, color: NAVY, bold: true }, { text: "12 statt 7 Tage Datenbasis" }],
    [{ text: "7", align: AlignmentType.CENTER, color: GREY_M, bold: true }, { text: "Besprechung der Ergebnisse" }, { text: "nein", align: AlignmentType.CENTER, color: GREY_D }, { text: "unverändert" }],
    [{ text: "8", align: AlignmentType.CENTER, color: GREY_M, bold: true }, { text: "Anfahrten Pauschale" }, { text: "nein", align: AlignmentType.CENTER, color: GREY_D }, { text: "keine zusätzliche Fahrt erforderlich" }],
  ]
);

// Section 3: Position 4 Herleitung
const S3_W = [4400, 2500, 2460];
const s3Table = makeTable(
  S3_W,
  [{ text: "SCHRITT" }, { text: "RECHNUNG", align: AlignmentType.RIGHT }, { text: "ERGEBNIS", align: AlignmentType.RIGHT }],
  [
    [{ text: "Ansatz aus Rechnung 2026-0801, Pos. 4" }, { text: "7 Tage, 3 Geräte", align: AlignmentType.RIGHT, color: GREY_D }, { text: "CHF 750.00", align: AlignmentType.RIGHT, bold: true }],
    [{ text: "Daraus abgeleiteter Tagessatz für alle drei Geräte" }, { text: "750 ÷ 7", align: AlignmentType.RIGHT, color: GREY_D }, { text: "CHF 107.14", align: AlignmentType.RIGHT, bold: true }],
    [{ text: "Je Gerät und Tag" }, { text: "107.14 ÷ 3", align: AlignmentType.RIGHT, color: GREY_D }, { text: "CHF 35.71", align: AlignmentType.RIGHT, bold: true }],
    [{ text: "Mehrdauer" }, { text: "5 Tage", align: AlignmentType.RIGHT, color: GREY_D }, { text: "—", align: AlignmentType.RIGHT, color: GREY_M }],
    [{ text: "Mehraufwand Position 4", bold: true, color: NAVY }, { text: "5 × 107.14", align: AlignmentType.RIGHT, color: NAVY, bold: true }, { text: "CHF 535.71", align: AlignmentType.RIGHT, color: NAVY, bold: true }],
  ]
);

const s3Note = new Paragraph({
  spacing: { before: 120, after: 0, line: 300, lineRule: LineRuleType.AUTO },
  children: [
    T("Die Fernüberwachung ist im Ansatz der Position 4 enthalten und wird deshalb nicht separat verrechnet — sie ist über die fünf zusätzlichen Tage anteilig abgedeckt.", { color: GREY_D, italics: true }),
  ],
});

// Section 4: Position 6 breakdown
const S4A_W = [4680, 4680];
const s4aTable = makeTable(
  S4A_W,
  [{ text: "VON DER DAUER UNABHÄNGIG" }, { text: "MIT DER DAUER WACHSEND" }],
  [
    [{ text: "Gerätekonfiguration einlesen" }, { text: "Sichtung der Zeitreihen, 12 statt 7 Tage" }],
    [{ text: "95-Perzentil-Lauf je Bewertungsgrösse" }, { text: "Prüfung und Zuordnung der Ereignisse" }],
    [{ text: "Normvergleich nach EN 50160" }, { text: "Plausibilisierung je Messpunkt" }],
    [{ text: "Berichtsstruktur, Kapitel, Grafiken" }, { text: "Datenexport und Aufbereitung" }],
    [{ text: "Anlagenbeschreibung und Schema" }, { text: "—", color: GREY_M }],
  ]
);

const s4bTable = makeTable(
  S3_W,
  [{ text: "SCHRITT" }, { text: "RECHNUNG", align: AlignmentType.RIGHT }, { text: "ERGEBNIS", align: AlignmentType.RIGHT }],
  [
    [{ text: "Ansatz aus Rechnung 2026-0801, Pos. 6" }, { text: "—", align: AlignmentType.RIGHT, color: GREY_M }, { text: "CHF 350.00", align: AlignmentType.RIGHT, bold: true }],
    [{ text: "Geschätzter dauerabhängiger Anteil" }, { text: "40 %", align: AlignmentType.RIGHT, color: GREY_D }, { text: "CHF 140.00", align: AlignmentType.RIGHT, bold: true }],
    [{ text: "Davon anteilig für 5 zusätzliche Tage" }, { text: "× 5/7", align: AlignmentType.RIGHT, color: GREY_D }, { text: "CHF 100.00", align: AlignmentType.RIGHT, bold: true }],
    [{ text: "Mehraufwand Position 6", bold: true, color: NAVY }, { text: "—", align: AlignmentType.RIGHT, color: GREY_M }, { text: "CHF 100.00", align: AlignmentType.RIGHT, color: NAVY, bold: true }],
  ]
);

const s4WhyBox = new Table({
  columnWidths: [9360],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({
      children: [new TableCell({
        width: { size: 9360, type: WidthType.DXA },
        margins: { top: 200, bottom: 200, left: 260, right: 260 },
        shading: { type: ShadingType.CLEAR, color: "auto", fill: PAPER },
        borders: {
          top:    { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
          bottom: { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
          left:   { style: BorderStyle.SINGLE, size: 24, color: CYAN },
          right:  { style: BorderStyle.SINGLE, size: 4, color: GREY_L },
        },
        children: [
          new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "WARUM NICHT PROPORTIONAL", font: FONT, size: 14, color: NAVY, bold: true, allCaps: true, characterSpacing: 60 })] }),
          new Paragraph({ spacing: { after: 60, line: 300, lineRule: LineRuleType.AUTO }, children: [T("Die Datenmenge wuchs um 71 %, von rund 201'600 auf rund 345'600 Drei-Sekunden-Werte je Gerät. Ein proportionaler Zuschlag von 71 % auf die gesamte Position ergäbe CHF 250.00. Das wäre nicht gerechtfertigt, weil der Perzentil-Lauf und die Berichtsstruktur unabhängig von der Messdauer sind.")] }),
          new Paragraph({ children: [
            new TextRun({ text: "Verrechnet wird deshalb nur der dauerabhängige Anteil, anteilig für fünf Tage: ", font: FONT, size: 18, color: INK }),
            new TextRun({ text: "CHF 100.00 statt CHF 250.00.", font: FONT, size: 18, color: NAVY, bold: true }),
          ]}),
        ],
      })],
    }),
  ],
});

const s4NotBilled = [
  new Paragraph({
    spacing: { before: 220, after: 60 },
    children: [new TextRun({ text: "NICHT VERRECHNET", font: FONT, size: 14, color: CYAN, bold: true, allCaps: true, characterSpacing: 60 })],
  }),
  new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 40 },
    children: [T("Zusätzliche Anfahrt für den späteren Abbau — es war keine zusätzliche Fahrt nötig.")],
  }),
  new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 40 },
    children: [T("Mehraufwand für die drei Geräteauswertungen, die drei Übereinstimmungsberichte und die Bilddokumentation.")],
  }),
  new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 40 },
    children: [T("Die Positionen 1 bis 3, 5, 7 und 8 der Rechnung 2026-0801 bleiben unverändert.")],
  }),
];

// Section 5: Zusammenzug
const S5_W = [5000, 2500, 1860];
const s5Table = makeTable(
  S5_W,
  [{ text: "POSITION" }, { text: "ANSATZ", align: AlignmentType.RIGHT }, { text: "CHF", align: AlignmentType.RIGHT }],
  [
    [{ text: "Position 4 · Gerätebereitstellung 5 zusätzliche Tage" }, { text: "5 × 107.14", align: AlignmentType.RIGHT, color: GREY_D }, { text: "535.71", align: AlignmentType.RIGHT, bold: true }],
    [{ text: "Position 6 · Auswertung, dauerabhängiger Anteil" }, { text: "350 × 40 % × 5/7", align: AlignmentType.RIGHT, color: GREY_D }, { text: "100.00", align: AlignmentType.RIGHT, bold: true }],
  ]
);

// Small totals under s5Table using totalCell logic manually
const s5Totals = new Table({
  columnWidths: S5_W,
  width: { size: S5_W.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({
      children: [
        totalCell("Zwischensumme", S5_W[0]),
        totalCell("",              S5_W[1]),
        totalCell("635.71",        S5_W[2], { align: AlignmentType.RIGHT }),
      ],
    }),
    new TableRow({
      children: [
        bodyCell("Rundung", S5_W[0], { color: GREY_D }),
        bodyCell("",        S5_W[1]),
        bodyCell("−0.71",   S5_W[2], { align: AlignmentType.RIGHT, color: GREY_D }),
      ],
    }),
    new TableRow({
      children: [
        totalCell("TOTAL NACHTRAG OHNE MWST", S5_W[0], { strong: true }),
        totalCell("",                          S5_W[1], { strong: true }),
        totalCell("CHF 635.00",                S5_W[2], { align: AlignmentType.RIGHT, strong: true }),
      ],
    }),
  ],
});

// Section 6: Einordnung
const S6_W = [4400, 2800, 2160];
const s6Table = makeTable(
  S6_W,
  [{ text: "GRÖSSE" }, { text: "BETRAG", align: AlignmentType.RIGHT }, { text: "ANTEIL", align: AlignmentType.RIGHT }],
  [
    [{ text: "Rechnung 2026-0801" }, { text: "CHF 1'850.00", align: AlignmentType.RIGHT }, { text: "100 %", align: AlignmentType.RIGHT, color: GREY_D }],
    [{ text: "Nachtrag 2026-0802" }, { text: "CHF 635.00",   align: AlignmentType.RIGHT }, { text: "34.3 %", align: AlignmentType.RIGHT, color: GREY_D }],
    [{ text: "Gesamtsumme Projekt", bold: true, color: NAVY }, { text: "CHF 2'485.00", align: AlignmentType.RIGHT, bold: true, color: NAVY }, { text: "134.3 %", align: AlignmentType.RIGHT, bold: true, color: NAVY }],
  ]
);

const s6Note = new Paragraph({
  spacing: { before: 120, after: 0, line: 300, lineRule: LineRuleType.AUTO },
  children: [T("Bezogen auf die tatsächliche Messdauer von 12 statt 7 Tagen (also +71 %) liegt der Nachtrag mit +34.3 % deutlich unter einer proportionalen Fortschreibung. Der Grund: sechs von acht Positionen sind von der Verlängerung nicht betroffen.", { color: GREY_D })],
});

// Section 7: Zusatzleistungen
const s7Intro = new Paragraph({
  spacing: { after: 160, line: 300, lineRule: LineRuleType.AUTO },
  children: [T("Zur Transparenz, ohne Forderung: Im Rahmen der Auswertung sind Dokumente entstanden, die über die Position 6 der ursprünglichen Rechnung hinausgehen.")],
});

const S7_W = [5600, 3760];
const s7Table = makeTable(
  S7_W,
  [{ text: "DOKUMENT" }, { text: "UMFANG" }],
  [
    [{ text: "Schlussbericht mit Massnahmenkatalog" }, { text: "61 Seiten, 15 Kapitel, 20 Massnahmen" }],
    [{ text: "Einzelauswertungen der drei Messpunkte" }, { text: "3 Dokumente" }],
    [{ text: "Auswertung der drei Übereinstimmungsberichte" }, { text: "3 Dokumente" }],
    [{ text: "Bilddokumentation" }, { text: "19 Seiten, 14 Bilder" }],
    [{ text: "Massnahmen-Kurzfassung und Vollständigkeitsbericht" }, { text: "2 Dokumente" }],
    [{ text: "Kundenpräsentation" }, { text: "12 Folien mit Sprechernotizen" }],
  ]
);

const s7Note = new Table({
  columnWidths: [9360],
  width: { size: 9360, type: WidthType.DXA },
  borders: borderNone(),
  rows: [
    new TableRow({
      children: [new TableCell({
        width: { size: 9360, type: WidthType.DXA },
        margins: { top: 200, bottom: 200, left: 260, right: 260 },
        shading: { type: ShadingType.CLEAR, color: "auto", fill: CYAN_S },
        borders: {
          top:    { style: BorderStyle.SINGLE, size: 4, color: CYAN },
          bottom: { style: BorderStyle.SINGLE, size: 4, color: CYAN },
          left:   { style: BorderStyle.SINGLE, size: 24, color: CYAN },
          right:  { style: BorderStyle.SINGLE, size: 4, color: CYAN },
        },
        children: [
          new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "HINWEIS", font: FONT, size: 14, color: NAVY, bold: true, allCaps: true, characterSpacing: 60 })] }),
          new Paragraph({ children: [T("Diese Leistungen sind mit der Position 6 der Rechnung 2026-0801 abgegolten und werden nicht nachverrechnet. Sie sind hier nur aufgeführt, damit der Umfang der erbrachten Arbeit erkennbar ist.")] }),
        ],
      })],
    }),
  ],
});

// ---------- Assemble ----------
const doc = new Document({
  creator: "Burak Ücöz",
  title: "Nachtragsrechnung 2026-0802 · Baumann Elektrokontrollen GmbH",
  description: "Nachtragsrechnung · kabuu · Netzqualität & EMV Messungen · Engineering",
  styles: { default: { document: { run: { font: FONT, size: 20, color: INK } } } },
  numbering: {
    config: [{
      reference: "bullets",
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
      addressAndMeta(),
      dateLine,
      subjectKicker,
      subjectLine,
      factsRow,
      salutation,
      intro,
      invoiceTable,
      new Paragraph({ spacing: { before: 220 }, children: [new TextRun({ text: "GESAMTSUMME PROJEKT", font: FONT, size: 14, color: CYAN, bold: true, allCaps: true, characterSpacing: 80 })] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun("")] }),
      projStrip,
      mwstNote,
      ibanBlock(),
      ...closing,

      // PAGE 2
      pageBreak,
      h1("Herleitung des Mehraufwands"),
      herleitungIntro,

      h2("1  Sachverhalt"),
      s1Table,

      h2("2  Welche Positionen betroffen sind"),
      s2Table,

      h2("3  Position 4 · Gerätebereitstellung"),
      s3Table,
      s3Note,

      h2("4  Position 6 · Auswertung"),
      new Paragraph({ spacing: { before: 100, after: 140, line: 300, lineRule: LineRuleType.AUTO },
        children: [T("Der Auswertungsaufwand steigt nicht proportional zur Datenmenge. Ein Teil der Arbeit ist von der Messdauer unabhängig.")] }),
      s4aTable,
      new Paragraph({ spacing: { before: 220 }, children: [new TextRun("")] }),
      s4bTable,
      new Paragraph({ spacing: { before: 220 }, children: [new TextRun("")] }),
      s4WhyBox,
      ...s4NotBilled,

      h2("5  Zusammenzug"),
      s5Table,
      new Paragraph({ spacing: { before: 40 }, children: [new TextRun("")] }),
      s5Totals,

      h2("6  Einordnung"),
      s6Table,
      s6Note,

      h2("7  Was zusätzlich geleistet und nicht verrechnet wurde"),
      s7Intro,
      s7Table,
      new Paragraph({ spacing: { before: 220 }, children: [new TextRun("")] }),
      s7Note,
    ],
  }],
});

const outDir = "/home/user/Burak/dokumente";
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, "Nachtragsrechnung_2026-0802_Baumann.docx");

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(outPath, buf);
  console.log("wrote", outPath, buf.length, "bytes");
});
