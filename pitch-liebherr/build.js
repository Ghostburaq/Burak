// Pitch Burak Ücöz -> Liebherr Energy Solutions
// Corporate Design: Liebherr Gelb FED000, Anthrazit 1A1D1E, Grauschiefer 37484F
const pptxgen = require("pptxgenjs");

const YELLOW = "FED000";
const YELLOW_D = "D9AE00"; // abgedunkeltes Gelb, nur fuer Text auf Weiss
const INK = "1A1D1E"; // Anthrazit, dunkle Slides
const INK2 = "273034"; // Karte auf dunkel
const SLATE = "37484F"; // Grauschiefer
const MUTED_D = "9AA6AB"; // Sekundaertext auf dunkel
const MUTED_L = "5E6C73"; // Sekundaertext auf hell
const PAPER = "F2F3F3";
const WHITE = "FFFFFF";

const F = "Arial";
const M = 0.75; // Seitenrand
const W = 13.333;
const CW = W - 2 * M; // 11.833

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Burak Ücöz";
pres.title = "Bewerbung IoT & Energy Engineer";

// ---------- Helfer ----------
const shadowLight = () => ({ type: "outer", color: "1A1D1E", blur: 10, offset: 1, angle: 90, opacity: 0.1 });

function card(slide, x, y, w, h, opts = {}) {
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.06,
    fill: { color: opts.fill || WHITE },
    line: opts.line || { type: "none" },
    shadow: opts.shadow === false ? undefined : shadowLight(),
  });
}

function eyebrow(slide, text, dark) {
  slide.addText(text.toUpperCase(), {
    x: M, y: 0.52, w: CW, h: 0.3,
    fontFace: F, fontSize: 10.5, bold: true, charSpacing: 2.6,
    color: dark ? YELLOW : YELLOW_D, isTextBox: true, margin: 0, valign: "middle",
  });
}

function title(slide, text, dark) {
  slide.addText(text, {
    x: M, y: 1.0, w: CW, h: 0.75,
    fontFace: F, fontSize: 33, bold: true,
    color: dark ? WHITE : INK, isTextBox: true, margin: 0, valign: "middle",
  });
}

function lead(slide, text, dark, y = 1.85) {
  slide.addText(text, {
    x: M, y, w: CW - 0.6, h: 0.5,
    fontFace: F, fontSize: 13.5, italic: true,
    color: dark ? MUTED_D : MUTED_L, isTextBox: true, margin: 0, valign: "top",
    lineSpacingMultiple: 1.15,
  });
}

function pageNo(slide, n, dark) {
  slide.addText(String(n).padStart(2, "0"), {
    x: W - M - 0.6, y: 6.82, w: 0.6, h: 0.28,
    fontFace: F, fontSize: 9.5, color: dark ? "5C666B" : "A9B1B5",
    align: "right", isTextBox: true, margin: 0,
  });
}

function badge(slide, x, y, n, size = 0.42, onDark = false) {
  slide.addShape(pres.ShapeType.ellipse, {
    x, y, w: size, h: size,
    fill: { color: YELLOW }, line: { type: "none" },
  });
  slide.addText(String(n), {
    x, y, w: size, h: size,
    fontFace: F, fontSize: size >= 0.5 ? 15 : 13, bold: true, color: INK,
    align: "center", valign: "middle", isTextBox: true, margin: 0,
  });
}

function darkBg(slide) {
  slide.background = { color: INK };
}
function lightBg(slide) {
  slide.background = { color: PAPER };
}

function bar(slide, y, text, opts = {}) {
  const h = opts.h || 0.72;
  slide.addShape(pres.ShapeType.roundRect, {
    x: M, y, w: CW, h, rectRadius: 0.05,
    fill: { color: opts.fill || INK }, line: { type: "none" },
  });
  slide.addText(text, {
    x: M + 0.35, y, w: CW - 0.7, h,
    fontFace: F, fontSize: opts.fontSize || 12.5, bold: opts.bold !== false,
    color: opts.color || WHITE, isTextBox: true, margin: 0, valign: "middle",
    lineSpacingMultiple: 1.1,
  });
}

// ============================================================
// 01 Titel
// ============================================================
{
  const s = pres.addSlide();
  darkBg(s);

  s.addText("GESPRÄCH · 8. SEPTEMBER 2026 · BADEN", {
    x: M, y: 0.52, w: 8, h: 0.3,
    fontFace: F, fontSize: 10.5, bold: true, charSpacing: 2.6, color: YELLOW,
    isTextBox: true, margin: 0, valign: "middle",
  });

  s.addText("Burak Ücöz", {
    x: M, y: 2.25, w: 7.6, h: 1.0,
    fontFace: F, fontSize: 52, bold: true, color: WHITE,
    isTextBox: true, margin: 0, valign: "middle",
  });
  s.addText("Elektroingenieur · Messtechnik, Inbetriebnahme, technischer Vertrieb", {
    x: M, y: 3.32, w: 7.4, h: 0.4,
    fontFace: F, fontSize: 14, color: MUTED_D,
    isTextBox: true, margin: 0, valign: "top",
  });

  s.addText("BEWERBUNG ALS", {
    x: M, y: 4.28, w: 6, h: 0.28,
    fontFace: F, fontSize: 10, bold: true, charSpacing: 2.4, color: MUTED_D,
    isTextBox: true, margin: 0, valign: "middle",
  });
  s.addText("IoT & Energy Engineer", {
    x: M, y: 4.6, w: 7.5, h: 0.55,
    fontFace: F, fontSize: 26, bold: true, color: YELLOW,
    isTextBox: true, margin: 0, valign: "middle",
  });

  // Rechte Spalte: vier Perspektiven
  const items = ["Messen", "In Betrieb nehmen", "Verkaufen", "Bereitstellen"];
  const x0 = 9.05;
  const y0 = 2.42;
  const step = 0.72;
  s.addShape(pres.ShapeType.line, {
    x: x0 + 0.075, y: y0 + 0.08, w: 0, h: step * 3,
    line: { color: SLATE, width: 1.25 },
  });
  items.forEach((t, i) => {
    s.addShape(pres.ShapeType.ellipse, {
      x: x0, y: y0 + i * step - 0.075, w: 0.16, h: 0.16,
      fill: { color: YELLOW }, line: { type: "none" },
    });
    s.addText(t, {
      x: x0 + 0.45, y: y0 + i * step - 0.17, w: 3.2, h: 0.35,
      fontFace: F, fontSize: 13.5, color: WHITE,
      isTextBox: true, margin: 0, valign: "middle",
    });
  });

  s.addNotes(
    "Nicht vorlesen. Dieses Deck ist Vorbereitung und stilles Backup, kein Vortrag. Nur zeigen, wenn ein Moment entsteht, in dem es passt."
  );
}

// ============================================================
// 02 Vier Perspektiven
// ============================================================
{
  const s = pres.addSlide();
  lightBg(s);
  eyebrow(s, "Wer ich bin", false);
  title(s, "Vier Perspektiven auf dieselbe Sache", false);
  lead(s, "Elektrische Energie, über zehn Jahre aus vier Richtungen angefasst. Bei euch laufen sie zum ersten Mal zusammen.", false);

  const data = [
    ["Messen", "EMV, Prüffeld, Netzqualität nach EN 50160 und IEC 61000-4-30 Klasse A."],
    ["In Betrieb nehmen", "Aufbau, Verkabelung, Parametrierung, Anbindung, Fehlersuche im Feld."],
    ["Verkaufen", "Technischer Vertrieb an EVU, Industrie, Gemeinden und Städte."],
    ["Bereitstellen", "Mobile Energie: Generatoren, Batteriespeicher, Hybrid, Baustrom."],
  ];
  const cw = 2.72, gap = 0.32, cy = 2.62, ch = 2.62;
  data.forEach(([h, b], i) => {
    const cx = M + i * (cw + gap);
    card(s, cx, cy, cw, ch);
    badge(s, cx + 0.32, cy + 0.32, i + 1, 0.44);
    s.addText(h, {
      x: cx + 0.32, y: cy + 0.95, w: cw - 0.64, h: 0.5,
      fontFace: F, fontSize: 14.5, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.05,
    });
    s.addText(b, {
      x: cx + 0.32, y: cy + 1.48, w: cw - 0.64, h: 1.0,
      fontFace: F, fontSize: 11, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
  });

  bar(s, 5.62, "Jede Station hat eine Perspektive dazugelegt. Was fehlt, ist die fünfte: das System selbst mitbauen.");
  pageNo(s, 2, false);
}

// ============================================================
// 03 Werdegang
// ============================================================
{
  const s = pres.addSlide();
  lightBg(s);
  eyebrow(s, "Werdegang", false);
  title(s, "Der Weg, Station für Station", false);
  lead(s, "Messen, ausführen, verkaufen, liefern. Jeder Schritt hat eine Schicht dazugelegt.", false);

  const rows = [
    ["2015", "Werkstudent · Messtechnik", "EMV-Prüffeld, Messaufbauten, Störungssuche"],
    ["2016–2018", "Anadolu Ingenieure", "Elektrotechnik und Projektarbeit"],
    ["2018–2020", "Selbstständig", "Akquise, Angebot, Ausführung, alles selbst"],
    ["2020–2022", "MRK Engineering", "Maschinen- und Anlagenbau, Projekte bis IBN"],
    ["2022–2023", "Cortexia SA", "Service Engineer: Aufbau, IBN, Anbindung, Feld"],
    ["2024–2025", "Camille Bauer Metrawatt", "Netzqualität, IBN, Vertrieb ganze Schweiz"],
    ["heute", "Mobil In Time", "Mobile Energie: Auslegung, Baustelle, Kunde"],
  ];
  const y0 = 2.72, step = 0.6, dx = M + 0.1;
  s.addShape(pres.ShapeType.line, {
    x: dx + 0.075, y: y0 + 0.075, w: 0, h: step * (rows.length - 1),
    line: { color: "C8CED1", width: 1.5 },
  });
  rows.forEach(([yr, org, txt], i) => {
    const last = i === rows.length - 1;
    const yy = y0 + i * step;
    s.addShape(pres.ShapeType.ellipse, {
      x: dx, y: yy, w: 0.15, h: 0.15,
      fill: { color: last ? YELLOW : SLATE }, line: { type: "none" },
    });
    if (last) {
      s.addShape(pres.ShapeType.ellipse, {
        x: dx - 0.09, y: yy - 0.09, w: 0.33, h: 0.33,
        fill: { type: "none" }, line: { color: YELLOW, width: 1.25 },
      });
    }
    s.addText(yr, {
      x: dx + 0.55, y: yy - 0.14, w: 1.35, h: 0.42,
      fontFace: F, fontSize: 11, bold: last, color: last ? INK : MUTED_L,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(org, {
      x: dx + 1.95, y: yy - 0.14, w: 3.4, h: 0.42,
      fontFace: F, fontSize: 12.5, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(txt, {
      x: dx + 5.5, y: yy - 0.14, w: 5.6, h: 0.42,
      fontFace: F, fontSize: 12, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "middle",
    });
  });
  pageNo(s, 3, false);
  s.addNotes("Jahreszahlen vor dem Termin gegen CV und LinkedIn prüfen. Lücke 2023 bis 2024 vorbereiten.");
}

// ============================================================
// 04 Passung
// ============================================================
{
  const s = pres.addSlide();
  lightBg(s);
  eyebrow(s, "Passung", false);
  title(s, "Drei Dinge, die ich mitbringe", false);
  lead(s, "Kein Profil aus dem Stelleninserat, sondern das, was auf der Baustelle den Unterschied macht.", false);

  const rows = [
    ["Beide Seiten der Ablösung", "Ich lege heute Diesel und Batterie aus und verkaufe beides. Ich kann sagen, wo der Speicher gewinnt und wo der Kunde noch zum Aggregat greift."],
    ["Messen statt behaupten", "Aus der Messtechnik: EMV, Netzqualität, EN 50160, IEC 61000-4-30 Klasse A. Der Unterschied zwischen einer Zahl und einer belastbaren Zahl."],
    ["Kunde und Technik in einer Person", "Rahmenbedingungen aufnehmen, auslegen, in Betrieb nehmen, und dem Bauführer erklären, warum es so und nicht anders geht."],
  ];
  const y0 = 2.58, h = 1.24, gap = 0.2;
  rows.forEach(([t, b], i) => {
    const y = y0 + i * (h + gap);
    card(s, M, y, CW, h);
    badge(s, M + 0.42, y + (h - 0.5) / 2, i + 1, 0.5);
    s.addText(t, {
      x: M + 1.15, y: y + 0.22, w: 3.5, h: h - 0.44,
      fontFace: F, fontSize: 14.5, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle", lineSpacingMultiple: 1.05,
    });
    s.addText(b, {
      x: M + 4.85, y: y + 0.22, w: CW - 5.35, h: h - 0.44,
      fontFace: F, fontSize: 11.5, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "middle", lineSpacingMultiple: 1.2,
    });
  });
  pageNo(s, 4, false);
}

// ============================================================
// 05 Ehrlich gesagt
// ============================================================
{
  const s = pres.addSlide();
  darkBg(s);
  eyebrow(s, "Ehrlich gesagt", true);
  title(s, "Was ich kann, und was nicht", true);
  lead(s, "Eine Selbsteinschätzung, die ihr nachprüfen könnt.", true);

  const kann = [
    "Systeme aufbauen, verkabeln, in Betrieb nehmen",
    "Parametrieren und über Modbus anbinden",
    "Fehler im Feld eingrenzen, auch ohne Handbuch",
    "Auslegen: Leistung, Energie, Nachladung, Schutz",
    "Beim Kunden stehen und Technik übersetzen",
  ];
  const nicht = [
    "Embedded Systems: keine Tiefe",
    "TwinCAT: keine Praxis",
    "MQTT: Prinzip klar, Anwendung neu",
    "Softwareentwicklung ist nicht mein Handwerk",
  ];

  const cw = (CW - 0.4) / 2, cy = 2.6, ch = 2.95;
  const cols = [
    { x: M, head: "Das kann ich", items: kann, color: YELLOW, txt: WHITE },
    { x: M + cw + 0.4, head: "Das kann ich nicht", items: nicht, color: MUTED_D, txt: MUTED_D },
  ];
  cols.forEach((c) => {
    s.addShape(pres.ShapeType.roundRect, {
      x: c.x, y: cy, w: cw, h: ch, rectRadius: 0.05,
      fill: { color: INK2 }, line: { type: "none" },
    });
    s.addText(c.head, {
      x: c.x + 0.4, y: cy + 0.32, w: cw - 0.8, h: 0.35,
      fontFace: F, fontSize: 15, bold: true, color: c.color,
      isTextBox: true, margin: 0, valign: "middle",
    });
    c.items.forEach((t, i) => {
      const yy = cy + 0.92 + i * 0.4;
      s.addShape(pres.ShapeType.rect, {
        x: c.x + 0.4, y: yy + 0.115, w: 0.1, h: 0.1,
        fill: { color: c.color === YELLOW ? YELLOW : SLATE }, line: { type: "none" },
      });
      s.addText(t, {
        x: c.x + 0.72, y: yy, w: cw - 1.12, h: 0.34,
        fontFace: F, fontSize: 12, color: c.txt,
        isTextBox: true, margin: 0, valign: "middle",
      });
    });
  });

  s.addText("Sagt mir, wie tief ihr das braucht, dann sage ich euch, wie lange ich dafür brauche.", {
    x: M, y: 5.85, w: CW, h: 0.45,
    fontFace: F, fontSize: 14, italic: true, bold: true, color: YELLOW,
    isTextBox: true, margin: 0, valign: "middle",
  });
  pageNo(s, 5, true);
}

// ============================================================
// 06 Liebherr Energy Solutions
// ============================================================
{
  const s = pres.addSlide();
  lightBg(s);
  eyebrow(s, "Was ich über euch weiss", false);
  title(s, "Liebherr Energy Solutions", false);
  lead(s, "Gegründet Februar 2026, hervorgegangen aus dem Produktsegment Liebherr-Komponenten.", false);

  const items = [
    ["Das Ziel", "Energieverbrauch und CO₂ auf Baustellen senken und die Elektrifizierung von Bau- und Nutzfahrzeugen vorantreiben."],
    ["Das Portfolio", "Hardware, Software und künftig Energiedienstleistungen aus einer Hand, statt einzelner Produkte."],
    ["Die Hardware", "Liduro Power Port: mobiler, batteriebasierter Speicher für lokal emissionsfreie Versorgung der ganzen Baustelle."],
    ["Die Software", "Energy Planner: browserbasierte Planung von Leistungs- und Energiebedarf über die einzelnen Bauphasen."],
  ];
  const cw = (CW - 0.34) / 2, ch = 1.4, gx = 0.34, gy = 0.28, y0 = 2.6;
  items.forEach(([h, b], i) => {
    const cx = M + (i % 2) * (cw + gx);
    const cy = y0 + Math.floor(i / 2) * (ch + gy);
    card(s, cx, cy, cw, ch);
    s.addShape(pres.ShapeType.rect, {
      x: cx + 0.36, y: cy + 0.36, w: 0.11, h: 0.11,
      fill: { color: YELLOW }, line: { type: "none" },
    });
    s.addText(h.toUpperCase(), {
      x: cx + 0.62, y: cy + 0.26, w: cw - 1.0, h: 0.3,
      fontFace: F, fontSize: 10, bold: true, charSpacing: 1.8, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(b, {
      x: cx + 0.36, y: cy + 0.66, w: cw - 0.72, h: 0.62,
      fontFace: F, fontSize: 12, color: INK,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
  });

  bar(s, 5.95, "Corporate Venture: Startup-Tempo mit dem Rückhalt der Liebherr-Gruppe.");
  pageNo(s, 6, false);
}

// ============================================================
// 07 Markt
// ============================================================
{
  const s = pres.addSlide();
  lightBg(s);
  eyebrow(s, "Der Markt, wie ich ihn sehe", false);
  title(s, "Warum die Baustelle elektrisch wird", false);
  lead(s, "Drei Treiber, die sich gegenseitig verstärken.", false);

  const data = [
    ["Regulatorik und Vergabe", "Emissionsauflagen und Lärmschutz in Städten, zunehmend auch als Kriterium in der Ausschreibung."],
    ["Elektrische Maschinen", "Bagger, Kran und Lader kommen batteriebetrieben. Sie brauchen Ladeleistung dort, wo sie stehen."],
    ["Der Netzanschluss", "Der Anschluss wächst nicht mit. Speicher und Lastmanagement füllen die Lücke, bis das Netz nachzieht."],
  ];
  const cw = (CW - 0.64) / 3, cy = 2.58, ch = 2.2;
  data.forEach(([h, b], i) => {
    const cx = M + i * (cw + 0.32);
    card(s, cx, cy, cw, ch);
    badge(s, cx + 0.36, cy + 0.34, i + 1, 0.44);
    s.addText(h, {
      x: cx + 0.36, y: cy + 0.95, w: cw - 0.72, h: 0.34,
      fontFace: F, fontSize: 14, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(b, {
      x: cx + 0.36, y: cy + 1.3, w: cw - 0.72, h: 0.8,
      fontFace: F, fontSize: 11.5, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 5.0, w: CW, h: 1.25, rectRadius: 0.05,
    fill: { color: INK }, line: { type: "none" },
  });
  s.addText("WAS ICH TÄGLICH SEHE", {
    x: M + 0.4, y: 5.24, w: 6, h: 0.3,
    fontFace: F, fontSize: 10, bold: true, charSpacing: 1.8, color: YELLOW,
    isTextBox: true, margin: 0, valign: "middle",
  });
  s.addText("Der Bedarf ist da. Was Projekte aufhält, ist selten die Batterie, sondern der Aufstellort, der Anschluss und die Frage, wer die Anlage bedient.", {
    x: M + 0.4, y: 5.6, w: CW - 0.8, h: 0.5,
    fontFace: F, fontSize: 12.5, color: WHITE,
    isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.15,
  });
  pageNo(s, 7, false);
}

// ============================================================
// 08 Rolle
// ============================================================
{
  const s = pres.addSlide();
  darkBg(s);
  eyebrow(s, "Mein Aufgabenbereich", true);
  title(s, "Die Rolle, wie ich sie verstehe", true);
  lead(s, "An der Schnittstelle zwischen Hardware, Software und Energie. Und zwar dort, wo sie sich trifft: im Feld.", true);

  // Venn
  const r = 1.55;
  const cx = 3.35, cy = 4.35;
  const circles = [
    { x: cx - r - 0.34, y: cy - r - 0.28, label: "Hardware", lx: cx - r - 0.34, ly: cy - r + 0.35 },
    { x: cx + 0.34 - r, y: cy - r - 0.28, label: "Software", lx: cx + 0.34 - r, ly: cy - r + 0.35 },
    { x: cx - r, y: cy - r + 0.62, label: "Energie", lx: cx - r, ly: cy + r + 0.05 },
  ];
  // Positionen: zwei oben, eines unten mittig
  const pos = [
    { x: cx - 1.72, y: cy - 1.78, label: "Hardware", tx: cx - 1.72, ty: cy - 1.35 },
    { x: cx - 0.32, y: cy - 1.78, label: "Software", tx: cx + 0.42, ty: cy - 1.35 },
    { x: cx - 1.02, y: cy - 0.62, label: "Energie", tx: cx - 1.02, ty: cy + 0.72 },
  ];
  pos.forEach((p) => {
    s.addShape(pres.ShapeType.ellipse, {
      x: p.x, y: p.y, w: 2.04, h: 2.04,
      fill: { color: SLATE, transparency: 35 },
      line: { color: YELLOW, width: 1 },
    });
  });
  pos.forEach((p) => {
    s.addText(p.label, {
      x: p.tx, y: p.ty, w: 1.3, h: 0.3,
      fontFace: F, fontSize: 12, bold: true, color: WHITE,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
  });
  s.addShape(pres.ShapeType.ellipse, {
    x: cx - 0.52, y: cy - 0.68, w: 1.04, h: 1.04,
    fill: { color: YELLOW }, line: { type: "none" },
  });
  s.addText("FELD", {
    x: cx - 0.52, y: cy - 0.68, w: 1.04, h: 1.04,
    fontFace: F, fontSize: 12.5, bold: true, color: INK, charSpacing: 1,
    align: "center", valign: "middle", isTextBox: true, margin: 0,
  });

  const tasks = [
    "Rahmenbedingungen beim Kunden aufnehmen und auslegen",
    "Hardware aufbauen, verkabeln, in Betrieb nehmen",
    "Konnektivität herstellen und Systeme anbinden",
    "Einsatz vor Ort begleiten, DACH und Frankreich",
    "Was im Feld nicht funktioniert, zurück ins Produkt spielen",
  ];
  const tx = 7.15;
  s.addShape(pres.ShapeType.roundRect, {
    x: tx - 0.4, y: 2.7, w: CW - (tx - 0.4 - M), h: 3.0, rectRadius: 0.05,
    fill: { color: INK2 }, line: { type: "none" },
  });
  tasks.forEach((t, i) => {
    const yy = 2.98 + i * 0.5;
    s.addShape(pres.ShapeType.rect, {
      x: tx, y: yy + 0.17, w: 0.1, h: 0.1, fill: { color: YELLOW }, line: { type: "none" },
    });
    s.addText(t, {
      x: tx + 0.32, y: yy, w: 4.6, h: 0.44,
      fontFace: F, fontSize: 12, color: WHITE,
      isTextBox: true, margin: 0, valign: "middle",
    });
  });
  pageNo(s, 8, true);
}

// ============================================================
// 09 Speicherkette
// ============================================================
{
  const s = pres.addSlide();
  darkBg(s);
  eyebrow(s, "Fachlich", true);
  title(s, "Ein Speicher ist keine Batterie", true);
  lead(s, "Er ist eine Kette. Auf der Baustelle entscheidet fast nie die Zelle, sondern das Ende der Kette.", true);

  const chain = ["Zelle", "Modul", "BMS", "DC-Schutz", "Wechselrichter", "Schutz & Anschluss", "Last"];
  const bw = 1.41, gap = 0.32, by = 2.62, bh = 0.9;
  chain.forEach((t, i) => {
    const bx = M + i * (bw + gap);
    const hot = i >= 4;
    s.addShape(pres.ShapeType.roundRect, {
      x: bx, y: by, w: bw, h: bh, rectRadius: 0.07,
      fill: { color: hot ? YELLOW : INK2 }, line: { type: "none" },
    });
    s.addText(t, {
      x: bx + 0.06, y: by, w: bw - 0.12, h: bh,
      fontFace: F, fontSize: 10.5, bold: true, color: hot ? INK : WHITE,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
      lineSpacingMultiple: 1.0,
    });
    if (i < chain.length - 1) {
      s.addText("›", {
        x: bx + bw, y: by, w: gap, h: bh,
        fontFace: F, fontSize: 15, color: MUTED_D,
        align: "center", valign: "middle", isTextBox: true, margin: 0,
      });
    }
  });
  s.addText("Hier arbeite ich", {
    x: M + 4 * (bw + gap), y: by + bh + 0.1, w: bw * 3 + gap * 2, h: 0.3,
    fontFace: F, fontSize: 10.5, bold: true, charSpacing: 1.6, color: YELLOW,
    align: "center", valign: "middle", isTextBox: true, margin: 0,
  });

  const cols = [
    ["BMS", "Überwacht Spannung, Temperatur, Strom. Rechnet SOC und SOH, balanciert die Zellen, schaltet im Fehlerfall ab."],
    ["Thermik", "Kühlung und Heizung. Kälte kostet Leistung, Hitze kostet Lebensdauer. Bei einem Gerät im Freien kein Randthema."],
    ["Sicherheit", "DC-Trennung, Brandmeldung, Notabschaltung. In der Praxis oft der Punkt, an dem der Aufstellort verhandelt wird."],
  ];
  const cw = (CW - 0.64) / 3, cy = 4.25;
  cols.forEach(([h, b], i) => {
    const cxx = M + i * (cw + 0.32);
    s.addShape(pres.ShapeType.roundRect, {
      x: cxx, y: cy, w: cw, h: 1.9, rectRadius: 0.05,
      fill: { color: INK2 }, line: { type: "none" },
    });
    s.addText(h, {
      x: cxx + 0.34, y: cy + 0.3, w: cw - 0.68, h: 0.32,
      fontFace: F, fontSize: 14, bold: true, color: YELLOW,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(b, {
      x: cxx + 0.34, y: cy + 0.72, w: cw - 0.68, h: 0.95,
      fontFace: F, fontSize: 11.5, color: MUTED_D,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
  });
  pageNo(s, 9, true);
}

// ============================================================
// 10 Auslegung
// ============================================================
{
  const s = pres.addSlide();
  lightBg(s);
  eyebrow(s, "Auslegung", false);
  title(s, "Zwei Grenzen, nicht eine", false);
  lead(s, "Ein Speicher kann genug Energie für den Tag haben und den Krananlauf trotzdem nicht schaffen.", false);

  const cards = [
    ["kVA", "Leistung", "Wie viel auf einmal.", "Spitzenlast, Anlaufströme, cos phi, C-Rate. Der Turmdrehkran ist der Sonderfall: hoher Anlaufstrom beim Heben, Rückspeisung beim Senken."],
    ["kWh", "Energie", "Wie lange.", "Tagesbedarf, nutzbare Kapazität statt Nennkapazität. Und die Frage, die am häufigsten vergessen wird: Reicht der Netzanschluss, um über Nacht nachzuladen?"],
  ];
  const cw = (CW - 0.4) / 2, cy = 2.6, ch = 2.5;
  cards.forEach(([unit, h, sub, b], i) => {
    const cx = M + i * (cw + 0.4);
    card(s, cx, cy, cw, ch);
    s.addShape(pres.ShapeType.roundRect, {
      x: cx + 0.36, y: cy + 0.34, w: 1.55, h: 0.82, rectRadius: 0.06,
      fill: { color: YELLOW }, line: { type: "none" },
    });
    s.addText(unit, {
      x: cx + 0.36, y: cy + 0.34, w: 1.55, h: 0.82,
      fontFace: F, fontSize: 26, bold: true, color: INK,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(h, {
      x: cx + 2.12, y: cy + 0.4, w: cw - 2.5, h: 0.36,
      fontFace: F, fontSize: 16, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(sub, {
      x: cx + 2.12, y: cy + 0.76, w: cw - 2.5, h: 0.32,
      fontFace: F, fontSize: 12.5, italic: true, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(b, {
      x: cx + 0.36, y: cy + 1.42, w: cw - 0.72, h: 0.92,
      fontFace: F, fontSize: 11.5, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
  });

  bar(s, 5.5, "Reicht beides nicht: Hybridbetrieb mit Aggregat, Lastmanagement oder Netzverstärkung. Was geht, entscheidet der Bauablauf, nicht die Technik.", { h: 0.8 });
  pageNo(s, 10, false);
}

// ============================================================
// 11 Energiemanagement
// ============================================================
{
  const s = pres.addSlide();
  lightBg(s);
  eyebrow(s, "Energiemanagement", false);
  title(s, "Warum Software den Unterschied macht", false);
  lead(s, "Der Speicher liefert Energie. Erst die Steuerung macht daraus eine Versorgung, die trägt.", false);

  const data = [
    ["VORHER", "Planen", "Leistungs- und Energiebedarf über die Bauphasen prognostizieren. Aus einer Schätzung wird eine Dimensionierung."],
    ["IM BETRIEB", "Steuern", "Lade- und Entladefahrpläne, Spitzen kappen, Nachladen wenn es günstig ist, Quellen im Hybridbetrieb koordinieren."],
    ["DANACH", "Messen", "Verbrauch und Zustand erfassen, Abweichung gegen die Planung, und daraus die nächste Auslegung verbessern."],
  ];
  const cw = (CW - 0.7) / 3, cy = 2.6, ch = 2.1;
  data.forEach(([eb, h, b], i) => {
    const cx = M + i * (cw + 0.35);
    card(s, cx, cy, cw, ch);
    s.addText(eb, {
      x: cx + 0.34, y: cy + 0.3, w: cw - 0.68, h: 0.28,
      fontFace: F, fontSize: 10, bold: true, charSpacing: 1.8, color: YELLOW_D,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(h, {
      x: cx + 0.34, y: cy + 0.62, w: cw - 0.68, h: 0.44,
      fontFace: F, fontSize: 20, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(b, {
      x: cx + 0.34, y: cy + 1.14, w: cw - 0.68, h: 0.8,
      fontFace: F, fontSize: 11.5, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
    if (i < 2) {
      s.addText("›", {
        x: cx + cw, y: cy, w: 0.35, h: ch,
        fontFace: F, fontSize: 17, bold: true, color: YELLOW_D,
        align: "center", valign: "middle", isTextBox: true, margin: 0,
      });
    }
  });

  bar(s, 5.15, "Die Schleife von der Planung über den Betrieb zurück in die Planung ist der Teil, den ich mitbringen kann: Ich sehe im Feld, wo die Prognose danebenlag.", { h: 0.85 });
  pageNo(s, 11, false);
}

// ============================================================
// 12 Drei Fragen aus dem Feld
// ============================================================
{
  const s = pres.addSlide();
  darkBg(s);
  eyebrow(s, "Was ich einbringe", true);
  title(s, "Drei Fragen aus dem Feld", true);
  lead(s, "Nicht aus dem Lehrbuch, sondern von Baustellen, auf denen ich stand.", true);

  const data = [
    ["Selektivität", "Ein Wechselrichter liefert im Kurzschluss deutlich weniger Strom als Netz oder Generator, weil er strombegrenzt arbeitet. Lösen die Schutzorgane im Baustromverteiler dann noch sauber und selektiv aus?"],
    ["Netzbildend oder folgend", "Auf der Baustelle ist Inselbetrieb der Normalfall, der Wechselrichter muss Spannung und Frequenz selbst stellen. Wie wird zwischen Insel, Netzparallel und Hybrid umgeschaltet, und unterbrechungsfrei?"],
    ["Der erste Morgen", "Wer schliesst an, wer schaltet ein, und was passiert bei der ersten Störung um sieben Uhr, wenn niemand von uns vor Ort ist? Daran entscheidet sich, ob nachbestellt wird."],
  ];
  const cw = (CW - 0.64) / 3, cy = 2.58, ch = 3.05;
  data.forEach(([h, b], i) => {
    const cx = M + i * (cw + 0.32);
    s.addShape(pres.ShapeType.roundRect, {
      x: cx, y: cy, w: cw, h: ch, rectRadius: 0.05,
      fill: { color: INK2 }, line: { type: "none" },
    });
    badge(s, cx + 0.36, cy + 0.34, i + 1, 0.44);
    s.addText(h, {
      x: cx + 0.36, y: cy + 0.94, w: cw - 0.72, h: 0.36,
      fontFace: F, fontSize: 14.5, bold: true, color: YELLOW,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(b, {
      x: cx + 0.36, y: cy + 1.34, w: cw - 0.72, h: 1.5,
      fontFace: F, fontSize: 11.5, color: MUTED_D,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
  });

  s.addText("Ich habe gelernt, einer Messung mehr zu trauen als einer Meinung.", {
    x: M, y: 5.9, w: CW, h: 0.45,
    fontFace: F, fontSize: 14, italic: true, bold: true, color: YELLOW,
    isTextBox: true, margin: 0, valign: "middle",
  });
  pageNo(s, 12, true);
}

// ============================================================
// 13 Erste 90 Tage
// ============================================================
{
  const s = pres.addSlide();
  lightBg(s);
  eyebrow(s, "Wenn ihr mich nehmt", false);
  title(s, "Die ersten 90 Tage", false);
  lead(s, "Kein Einarbeitungsplan aus dem Handbuch, sondern drei Ergebnisse, an denen ihr mich messen könnt.", false);

  const data = [
    ["TAG 1–30", "Selbst anfassen", "Mit auf die Baustelle. Ein System eigenhändig aufbauen und in Betrieb nehmen, bis ich es blind kann."],
    ["TAG 31–60", "Fehlerbilder sammeln", "Die drei häufigsten Probleme aus dem Feld dokumentieren, mit Ursache und Behebung, nicht nur als Symptom."],
    ["TAG 61–90", "Zurückspielen", "Aus den Fehlerbildern konkrete Verbesserungen ableiten und eine Inbetriebnahme-Routine hinterlassen, die auch andere anwenden können."],
  ];
  const cw = (CW - 0.64) / 3, cy = 2.72, ch = 2.35;
  data.forEach(([eb, h, b], i) => {
    const cx = M + i * (cw + 0.32);
    card(s, cx, cy, cw, ch);
    // Grosse Ziffer als Motiv
    s.addShape(pres.ShapeType.ellipse, {
      x: cx + 0.34, y: cy - 0.3, w: 0.6, h: 0.6,
      fill: { color: YELLOW }, line: { color: PAPER, width: 3 },
    });
    s.addText(String(i + 1), {
      x: cx + 0.34, y: cy - 0.3, w: 0.6, h: 0.6,
      fontFace: F, fontSize: 17, bold: true, color: INK,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(eb, {
      x: cx + 0.34, y: cy + 0.5, w: cw - 0.68, h: 0.28,
      fontFace: F, fontSize: 10, bold: true, charSpacing: 1.8, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(h, {
      x: cx + 0.34, y: cy + 0.82, w: cw - 0.68, h: 0.4,
      fontFace: F, fontSize: 17, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(b, {
      x: cx + 0.34, y: cy + 1.3, w: cw - 0.68, h: 0.9,
      fontFace: F, fontSize: 11.5, color: MUTED_L,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
  });

  bar(s, 5.5, "Nach 90 Tagen möchte ich derjenige sein, den ihr anruft, wenn draussen etwas klemmt.");
  pageNo(s, 13, false);
}

// ============================================================
// 14 Vier Fragen an euch
// ============================================================
{
  const s = pres.addSlide();
  darkBg(s);
  eyebrow(s, "Was mich interessiert", true);
  title(s, "Vier Fragen an euch", true);
  lead(s, "Damit ich am Ende des Gesprächs weiss, ob ich der Richtige für euch bin.", true);

  const qs = [
    "Was muss in zwölf Monaten passiert sein, damit ihr sagt, die Einstellung hat sich gelohnt?",
    "Wie viel Liebherr steckt im Alltag: Konzernprozesse oder wirklich Venture-Tempo?",
    "Was ist heute die häufigste Rückmeldung von der Baustelle zum Liduro Power Port?",
    "Wie kommen Werkzeug und Messtechnik zum Einsatzort, und wo ist der Arbeitsort?",
  ];
  const cw = (CW - 0.34) / 2, ch = 1.5, y0 = 2.72;
  qs.forEach((q, i) => {
    const cx = M + (i % 2) * (cw + 0.34);
    const cy = y0 + Math.floor(i / 2) * (ch + 0.3);
    s.addShape(pres.ShapeType.roundRect, {
      x: cx, y: cy, w: cw, h: ch, rectRadius: 0.05,
      fill: { color: INK2 }, line: { type: "none" },
    });
    s.addShape(pres.ShapeType.ellipse, {
      x: cx + 0.38, y: cy + (ch - 0.62) / 2, w: 0.62, h: 0.62,
      fill: { color: YELLOW }, line: { type: "none" },
    });
    s.addText("?", {
      x: cx + 0.38, y: cy + (ch - 0.62) / 2, w: 0.62, h: 0.62,
      fontFace: F, fontSize: 22, bold: true, color: INK,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(q, {
      x: cx + 1.2, y: cy + 0.26, w: cw - 1.58, h: ch - 0.52,
      fontFace: F, fontSize: 12.5, color: WHITE,
      isTextBox: true, margin: 0, valign: "middle", lineSpacingMultiple: 1.2,
    });
  });
  pageNo(s, 14, true);
}

// ============================================================
// 15 Danke
// ============================================================
{
  const s = pres.addSlide();
  darkBg(s);
  eyebrow(s, "Danke", true);

  s.addText("Ihr habt Hardware, Software\nund den Konzern im Rücken.", {
    x: M, y: 1.95, w: 10.5, h: 1.4,
    fontFace: F, fontSize: 32, bold: true, color: WHITE,
    isTextBox: true, margin: 0, valign: "middle", lineSpacingMultiple: 1.25,
  });

  s.addText(
    "Was auf der Baustelle darüber entscheidet, ob gekauft wird, sind meistens Kleinigkeiten:\nwo das Gerät steht, wer es anschliesst, und was bei der ersten Störung passiert.",
    {
      x: M, y: 3.55, w: 10.8, h: 0.9,
      fontFace: F, fontSize: 14, color: MUTED_D,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.3,
    }
  );
  s.addText("Das ist die Seite, die ich mitbringe.", {
    x: M, y: 4.5, w: 10.8, h: 0.4,
    fontFace: F, fontSize: 14, bold: true, color: YELLOW,
    isTextBox: true, margin: 0, valign: "top",
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 5.45, w: CW, h: 1.0, rectRadius: 0.05,
    fill: { color: INK2 }, line: { type: "none" },
  });
  s.addText("Burak Ücöz", {
    x: M + 0.4, y: 5.62, w: 5, h: 0.34,
    fontFace: F, fontSize: 14.5, bold: true, color: WHITE,
    isTextBox: true, margin: 0, valign: "middle",
  });
  s.addText("Elektroingenieur · Messtechnik, Inbetriebnahme, technischer Vertrieb", {
    x: M + 0.4, y: 5.96, w: 6.5, h: 0.3,
    fontFace: F, fontSize: 11.5, color: MUTED_D,
    isTextBox: true, margin: 0, valign: "middle",
  });
  s.addText("b.s.uecoez@gmail.com   ·   [Telefon eintragen]   ·   [LinkedIn eintragen]", {
    x: CW + M - 6.4, y: 5.45, w: 6.0, h: 1.0,
    fontFace: F, fontSize: 12, color: YELLOW,
    align: "right", isTextBox: true, margin: 0, valign: "middle",
  });

  s.addNotes("Telefonnummer und LinkedIn-Profil vor dem Termin eintragen.");
}

pres.writeFile({ fileName: process.argv[2] || "Pitch_Burak_Uecoez_Liebherr.pptx" }).then((f) =>
  console.log("geschrieben:", f)
);
