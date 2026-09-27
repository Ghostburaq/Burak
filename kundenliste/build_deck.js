// Erzeugt Zielkunden_Schweiz_Praesentation.pptx (Daten aus Kundenliste_MiT_Schweiz.xlsx, Stand 27.09.2026)
const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const C = {
  ink: "1F2328", ink2: "2E343B", body: "3A4048", muted: "6B7280", line: "D9DDE2",
  bg: "FFFFFF", soft: "F3F4F6", amber: "F2A900", amberSoft: "FFF4D6",
  A: "1F7A4D", B: "F2A900", Cc: "9AA0A6", white: "FFFFFF",
};
const HF = "Arial", BF = "Calibri";
const FOOT = "Mobil In Time  ·  Zielkunden Schweiz 2026/27  ·  intern";

async function icon(Comp, color, size = 256) {
  const svg = renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const I = {};
  const need = { bolt: fa.FaBolt, bullseye: fa.FaBullseye, list: fa.FaListUl, check: fa.FaCheck, chart: fa.FaChartBar,
    plug: fa.FaPlug, building: fa.FaBuilding, industry: fa.FaIndustry, server: fa.FaServer, hardhat: fa.FaHardHat,
    user: fa.FaUserTie, map: fa.FaMapMarkedAlt, warn: fa.FaExclamationTriangle, ban: fa.FaBan, handshake: fa.FaHandshake,
    gavel: fa.FaGavel, flag: fa.FaFlag, arrow: fa.FaArrowRight, pen: fa.FaPencilRuler, bolt2: fa.FaChargingStation,
    sync: fa.FaSyncAlt, phone: fa.FaPhoneAlt, users: fa.FaUsers, search: fa.FaSearch };
  for (const [k, v] of Object.entries(need)) { I[k] = await icon(v, C.ink); I[k + "W"] = await icon(v, C.white); }

  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10 x 5.625
  pres.author = "Burak Ücöz";
  pres.title = "Zielkunden Schweiz 2026/27";

  let page = 0;
  const footer = (s, dark = false) => {
    page++;
    s.addText(FOOT, { x: 0.5, y: 5.25, w: 6, h: 0.25, fontFace: BF, fontSize: 8, color: dark ? "9AA0A6" : C.muted, margin: 0, isTextBox: true });
    s.addText(String(page), { x: 9.0, y: 5.25, w: 0.5, h: 0.25, fontFace: BF, fontSize: 8, color: dark ? "9AA0A6" : C.muted, align: "right", margin: 0, isTextBox: true });
  };
  const kicker = (s, t, dark = false) => s.addText(t.toUpperCase(), { x: 0.5, y: 0.35, w: 9, h: 0.25, fontFace: HF, fontSize: 9, bold: true, charSpacing: 3, color: dark ? C.amber : "B07B00", margin: 0, isTextBox: true });
  const title = (s, t, dark = false) => s.addText(t, { x: 0.5, y: 0.6, w: 9, h: 0.6, fontFace: HF, fontSize: 24, bold: true, color: dark ? C.white : C.ink, margin: 0, valign: "top", isTextBox: true });
  const iconCircle = (s, key, x, y, d = 0.5, fill = C.amber) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
    const p = d * 0.5;
    s.addImage({ data: I[key], x: x + (d - p) / 2, y: y + (d - p) / 2, w: p, h: p });
  };
  const card = (s, x, y, w, h, fill = C.soft) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08 });
  const txt = (s, t, o) => s.addText(t, Object.assign({ fontFace: BF, fontSize: 11, color: C.body, margin: 0, valign: "top", isTextBox: true }, o));

  // ---------------------------------------------------------------- 1 Titel
  {
    const s = pres.addSlide(); s.background = { color: C.ink };
    s.addText("INTERN  ·  VERTRAULICH", { x: 0.6, y: 0.6, w: 5, h: 0.3, fontFace: HF, fontSize: 10, bold: true, charSpacing: 4, color: C.amber, margin: 0, isTextBox: true });
    s.addText("Zielkunden Schweiz 2026/27", { x: 0.6, y: 1.2, w: 6, h: 1.4, fontFace: HF, fontSize: 38, bold: true, color: C.white, margin: 0, valign: "top", isTextBox: true });
    s.addText("Mobile Energie: Generator, BESS, USV, Trafo, NEA-Test, PQ-Audit, Baustrom, Event", { x: 0.6, y: 2.75, w: 5.6, h: 0.6, fontFace: BF, fontSize: 14, color: "D1D5DB", margin: 0, valign: "top", isTextBox: true });
    s.addText("Kundenliste nach Vorgabe 60/20/20  ·  Stand 27.09.2026  ·  Burak Ücöz", { x: 0.6, y: 4.5, w: 6, h: 0.3, fontFace: BF, fontSize: 11, color: "9AA0A6", margin: 0, isTextBox: true });
    // Kennzahlenblock rechts
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.9, y: 1.2, w: 2.5, h: 3.2, fill: { color: C.ink2 }, line: { color: C.ink2 }, rectRadius: 0.1 });
    iconCircle(s, "bolt", 7.85, 1.45, 0.6);
    s.addText("125", { x: 6.9, y: 2.15, w: 2.5, h: 0.75, fontFace: HF, fontSize: 44, bold: true, color: C.amber, align: "center", margin: 0, isTextBox: true });
    s.addText("Firmen recherchiert", { x: 6.9, y: 2.9, w: 2.5, h: 0.3, fontFace: BF, fontSize: 11, color: "D1D5DB", align: "center", margin: 0, isTextBox: true });
    s.addText("70", { x: 6.9, y: 3.25, w: 2.5, h: 0.6, fontFace: HF, fontSize: 32, bold: true, color: C.white, align: "center", margin: 0, isTextBox: true });
    s.addText("in der Kernliste", { x: 6.9, y: 3.85, w: 2.5, h: 0.3, fontFace: BF, fontSize: 11, color: "D1D5DB", align: "center", margin: 0, isTextBox: true });
    page++;
    s.addNotes("Einstieg: Roberto und ich haben die Vorgabe gemacht, hier ist die Umsetzung für die ganze Schweiz. 125 Firmen recherchiert, 70 davon als Kernliste im Verhältnis 60/20/20. Alles liegt in der Excel, die Folien zeigen die Essenz.");
  }

  // ---------------------------------------------------------------- 2 Auftrag
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "Auftrag und Umsetzung"); title(s, "Die Vorgabe ist 1:1 umgesetzt, und etwas mehr");
    const col = (x, head, ic, items, fill) => {
      card(s, x, 1.45, 4.2, 3.55, fill);
      iconCircle(s, ic, x + 0.3, 1.7, 0.5);
      txt(s, head, { x: x + 0.95, y: 1.78, w: 3, h: 0.4, fontFace: HF, fontSize: 15, bold: true, color: C.ink });
      txt(s, items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
        { x: x + 0.3, y: 2.45, w: 3.7, h: 2.4, fontSize: 12, paraSpaceAfter: 7 });
    };
    col(0.5, "Vorgabe", "list", [
      "50 bis 70 Kunden mit Namen",
      "Mix: Installateure 60 %, FM / Stadtwerke / Planer 20 %, GU/TU + Industrie 20 %",
      "Status: Bestandskunde, verlorener Kunde, Potenzial / Aufbau",
      "Lieber mehr als weniger, damit wir priorisieren können",
    ], C.soft);
    s.addImage({ data: I.arrow, x: 4.8, y: 3.05, w: 0.35, h: 0.35 });
    col(5.3, "Umgesetzt", "check", [
      "125 Firmen recherchiert, alle mit Quelle",
      "Kernliste 70: exakt 42 / 14 / 14",
      "Score aus 4 Kriterien, Prio A/B/C mit Begründung",
      "Status-Spalte vorbereitet: CRM-Abgleich offen",
    ], C.amberSoft);
    footer(s);
    s.addNotes("Links die Vorgabe, rechts was drin ist. Wichtig: Den MiT-Kundenstatus kann keine Webrecherche liefern. Die Spalte ist vorbereitet, alle stehen auf 'Offen: CRM prüfen'. Das ist der Teil, den wir gemeinsam machen müssen.");
  }

  // ---------------------------------------------------------------- 3 Zahlen
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "Auf einen Blick"); title(s, "36 Firmen sind jetzt reif für den Erstkontakt");
    const stats = [["125", "Firmen gesamt", C.ink], ["70", "Kernliste 60/20/20", C.ink], ["36", "Prio A", C.A], ["7", "Regionen, 3 Sprachen", C.ink]];
    stats.forEach(([n, l, col], i) => {
      const x = 0.5 + i * 2.3;
      card(s, x, 1.5, 2.1, 1.55);
      txt(s, n, { x, y: 1.65, w: 2.1, h: 0.8, fontFace: HF, fontSize: 40, bold: true, color: col, align: "center" });
      txt(s, l, { x, y: 2.5, w: 2.1, h: 0.35, fontSize: 11, color: C.muted, align: "center" });
    });
    s.addChart(pres.charts.DOUGHNUT, [{ name: "Prio", labels: ["A", "B", "C"], values: [36, 69, 20] }], {
      x: 0.5, y: 3.2, w: 2.6, h: 1.95, holeSize: 55, chartColors: [C.A, C.B, C.Cc], showLegend: false,
      showValue: true, showPercent: false, dataLabelColor: C.white, dataLabelFontSize: 10, dataLabelFontBold: true,
    });
    txt(s, [
      { text: "A (36): ", options: { bold: true, color: C.A } }, { text: "Score ab 4,0. Jetzt angehen, Termin in 6 Wochen.", options: { breakLine: true } },
      { text: "B (69): ", options: { bold: true, color: "B07B00" } }, { text: "Score ab 3,0. Im Quartal angehen, Anlass beobachten.", options: { breakLine: true } },
      { text: "C (20): ", options: { bold: true, color: C.muted } }, { text: "Beobachten, über Partner oder Töchter abdecken." },
    ], { x: 3.4, y: 3.55, w: 6.1, h: 1.4, fontSize: 13, paraSpaceAfter: 8 });
    footer(s);
    s.addNotes("36 A, 69 B, 20 C. Die A-Firmen haben entweder einen konkreten Anlass 2026/27 oder sind Konzerne mit Rahmenvertrags-Hebel.");
  }

  // ---------------------------------------------------------------- 4 Segmentmix
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "Segmentmix"); title(s, "Mix 60/20/20 erfüllt, A-Dichte bei GU/TU + Industrie");
    s.addChart(pres.charts.BAR, [
      { name: "Prio A", labels: ["Installateure", "FM / EVU / Planer", "GU/TU + Industrie"], values: [11, 7, 18] },
      { name: "Prio B", labels: ["Installateure", "FM / EVU / Planer", "GU/TU + Industrie"], values: [20, 25, 24] },
      { name: "Prio C", labels: ["Installateure", "FM / EVU / Planer", "GU/TU + Industrie"], values: [11, 3, 6] },
    ], {
      x: 0.4, y: 1.4, w: 5.6, h: 3.7, barDir: "bar", barGrouping: "stacked", chartColors: [C.A, C.B, C.Cc],
      showValue: true, dataLabelPosition: "ctr", dataLabelColor: C.white, dataLabelFontSize: 10, dataLabelFontBold: true,
      showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: BF,
      catAxisLabelColor: C.body, catAxisLabelFontSize: 11, catAxisLabelFontFace: BF, valAxisHidden: true,
      valGridLine: { style: "none" }, catGridLine: { style: "none" }, barGapWidthPct: 50,
    });
    const rows = [["Installateure", "42", "42", "60 %"], ["FM / EVU / Planer", "35", "14", "20 %"], ["GU/TU + Industrie", "48", "14", "20 %"], ["Total", "125", "70", "100 %"]];
    const hdr = ["Segment", "Gesamt", "Kern", "Anteil"].map(t => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.ink } } }));
    s.addTable([hdr, ...rows.map((r, i) => r.map((t, j) => ({ text: t, options: { bold: i === 3, align: j ? "center" : "left" } })))], {
      x: 6.2, y: 1.5, w: 3.3, colW: [1.2, 0.85, 0.55, 0.7], fontFace: BF, fontSize: 9.5, color: C.body,
      border: { type: "solid", pt: 0.5, color: C.line }, rowH: 0.3,
    });
    txt(s, "Die Hälfte aller A-Firmen sitzt im kleinsten Kernsegment. Dort liegen die konkreten Anlässe: Rechenzentren, Pharma-Neubauten, Tunnel, Flughäfen.",
      { x: 6.2, y: 3.55, w: 3.3, h: 1.4, fontSize: 12, color: C.ink });
    footer(s);
    s.addNotes("Kernliste exakt 42/14/14. Die Reserve (55 Firmen) ist vor allem bei EVU/Planer und GU/Industrie, weil es dort mehr relevante Namen gibt als Plätze.");
  }

  // ---------------------------------------------------------------- 5 Scoring
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "Methodik"); title(s, "Vier Kriterien entscheiden die Prio");
    const crit = [["30 %", "Fit", "Passt der Bedarf zum MiT-Portfolio?", "plug"], ["30 %", "Volumen", "Mietvolumen pro Jahr, Hebel über Töchter und Rahmenverträge", "chart"],
      ["25 %", "Timing", "Konkreter Anlass 2025 bis 2027: Bau, UW-Umbau, Commissioning, Event", "flag"], ["15 %", "Zugang", "Regional erreichbar? Entscheid lokal oder Konzern? Öffentliche Beschaffung?", "handshake"]];
    crit.forEach(([w, h, d, ic], i) => {
      const x = 0.5 + i * 2.3;
      card(s, x, 1.45, 2.1, 2.45);
      iconCircle(s, ic, x + 0.2, 1.65, 0.45);
      txt(s, w, { x: x + 0.75, y: 1.65, w: 1.25, h: 0.45, fontFace: HF, fontSize: 22, bold: true, color: C.ink, valign: "middle" });
      txt(s, h, { x: x + 0.2, y: 2.25, w: 1.8, h: 0.35, fontFace: HF, fontSize: 13, bold: true, color: C.ink });
      txt(s, d, { x: x + 0.2, y: 2.6, w: 1.75, h: 1.2, fontSize: 11 });
    });
    const th = [["A", "Score ≥ 4,0", C.A], ["B", "Score ≥ 3,0", C.B], ["C", "Score < 3,0", C.Cc]];
    th.forEach(([p, t, col], i) => {
      const x = 0.5 + i * 2.3;
      s.addShape(pres.shapes.OVAL, { x, y: 4.2, w: 0.5, h: 0.5, fill: { color: col }, line: { color: col } });
      txt(s, p, { x, y: 4.2, w: 0.5, h: 0.5, fontFace: HF, fontSize: 16, bold: true, color: C.white, align: "center", valign: "middle" });
      txt(s, t, { x: x + 0.6, y: 4.2, w: 1.5, h: 0.5, fontSize: 12, bold: true, color: C.ink, valign: "middle" });
    });
    txt(s, "Skala je Kriterium 1 bis 5. Gewichte und Schwellen sind in der Excel änderbar, Score und Prio rechnen neu. «Prio final» übersteuert den Vorschlag.",
      { x: 7.4, y: 4.1, w: 2.1, h: 0.95, fontSize: 9, color: C.muted });
    footer(s);
    s.addNotes("Das Scoring ist transparent und diskutierbar. Wenn ihr eine Firma anders seht: Prio final setzen, dann gilt eure Einschätzung.");
  }

  // ---------------------------------------------------------------- 6 Regionen
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "Regionen"); title(s, "Zürich und Nordwestschweiz tragen 22 der 36 A-Firmen");
    const regs = ["Tessin", "Zentralschweiz", "Ostschweiz", "Mittelland/Bern", "West (Romandie)", "Nordwestschweiz", "Zürich"];
    const A = [1, 3, 2, 4, 4, 11, 11], B = [6, 4, 8, 9, 17, 10, 15], Cv = [6, 3, 1, 3, 6, 1, 0];
    s.addChart(pres.charts.BAR, [{ name: "Prio A", labels: regs, values: A }, { name: "Prio B", labels: regs, values: B }, { name: "Prio C", labels: regs, values: Cv }], {
      x: 0.4, y: 1.35, w: 5.6, h: 3.8, barDir: "bar", barGrouping: "stacked", chartColors: [C.A, C.B, C.Cc],
      showValue: true, dataLabelPosition: "ctr", dataLabelColor: C.white, dataLabelFontSize: 9, dataLabelFontBold: true,
      showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: BF, catAxisLabelColor: C.body, catAxisLabelFontSize: 10,
      catAxisLabelFontFace: BF, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, barGapWidthPct: 40,
    });
    const pts = [["Zürich 26 / NWCH 22", "RZ-Cluster, Pharma Basel, Konzernzentralen: hier entscheidet sich das Jahr."],
      ["West 27, aber nur 4 A", "Aufbaugebiet: viele Namen, wenig Anlass-Treffer. Französisch ist Pflicht."],
      ["Tessin 13, 1 A", "Kleine Installateure, Gotthard und Events. Über Partner und Marti bedienen."]];
    pts.forEach(([h, d], i) => {
      const y = 1.45 + i * 1.2;
      card(s, 6.3, y, 3.2, 1.05, i === 0 ? C.amberSoft : C.soft);
      txt(s, h, { x: 6.45, y: y + 0.1, w: 2.95, h: 0.3, fontFace: HF, fontSize: 12, bold: true, color: C.ink });
      txt(s, d, { x: 6.45, y: y + 0.42, w: 2.95, h: 0.6, fontSize: 10.5 });
    });
    footer(s);
    s.addNotes("Die Region folgt dem Hauptsitz bzw. der relevanten Baustelle. Lonza Visp zählt zu West, ist aber Oberwallis und deutschsprachig.");
  }

  // ---------------------------------------------------------------- 7 Installateure
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "Installateure  ·  60 %"); title(s, "Rahmenverträge mit Gruppen schlagen Einzelbaustellen");
    const rows = [
      ["Burkhalter Gruppe", "Zürich", "4,45", "83 Gesellschaften, ein Rahmen für Dutzende Töchter"],
      ["ETAVIS AG (VINCI)", "Zürich", "4,45", "Infrastruktur und RZ, Tür zu Actemium, Gfeller"],
      ["Equans Switzerland", "Zürich", "4,45", "Energie, Verkehr, Industrie, FM unter einem Dach"],
      ["BKW Building Solutions", "Bern", "4,20", "Dach von AEK, ISP, swisspro, Arnold, inelectro"],
      ["Actemium Schweiz", "Bern", "4,15", "Shutdowns, Inbetriebnahmen, Lastbanktests"],
      ["Arnold AG (BKW)", "Bern", "4,15", "HS-/Kabelnetzbau: Trafo-Miete, Netzersatz"],
      ["CKW Gebäudetechnik", "Zentral-CH", "4,15", "Grösster Installateur Zentralschweiz"],
      ["EKZ Eltop", "Zürich", "4,15", "Ganzer Kanton ZH, PV und Speicher"],
      ["ETAVIS Kriegel+Schaffner", "Basel", "4,15", "Pharma-Grossprojekte Basel"],
      ["Selmoni Gruppe", "Basel", "4,15", "Life Sciences: USV und NEA bei Shutdowns"],
      ["Egg-Telsa", "Genf", "4,15", "Grösster Unabhängiger Genf, Cap2030 GVA"],
    ];
    const hdr = ["Prio A", "Region", "Score", "Hebel"].map(t => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.ink } } }));
    s.addTable([hdr, ...rows.map(r => r.map((t, j) => ({ text: t, options: { bold: j === 0, align: j === 2 ? "center" : "left" } })))], {
      x: 0.5, y: 1.3, w: 6.6, colW: [1.95, 0.8, 0.65, 3.2], fontFace: BF, fontSize: 9, color: C.body,
      border: { type: "solid", pt: 0.5, color: C.line }, rowH: 0.27,
    });
    card(s, 7.35, 1.3, 2.15, 3.55, C.amberSoft);
    iconCircle(s, "users", 7.55, 1.5, 0.5);
    txt(s, "42 Installateure", { x: 7.55, y: 2.2, w: 2, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: C.ink });
    txt(s, [
      { text: "11 A, 20 B, 11 C", options: { bold: true, breakLine: true } },
      { text: "Burkhalter, VINCI und BKW decken zusammen über 15 Firmen der Liste ab. Einkauf zentral klären, dann Töchter regional bearbeiten.", options: {} },
    ], { x: 7.55, y: 2.55, w: 1.8, h: 2.2, fontSize: 10.5, paraSpaceAfter: 6 });
    footer(s);
    s.addNotes("Hebel: Gruppen zuerst. Burkhalter-Töchter in der Liste: Sedelec, Mérinat, Grichting & Valterio, EAGB, Hufschmid, Celio. VINCI: ETAVIS-Töchter, Gfeller, Actemium. BKW: AEK, ISP, swisspro, Arnold, inelectro.");
  }

  // ---------------------------------------------------------------- 8 FM / EVU / Planer
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "FM / Stadtwerke / Planer  ·  20 %"); title(s, "Netzumbau braucht Trafos, Planer schreiben uns aus");
    const cols = [
      ["Stadtwerke / EVU", "bolt2", [["CKW", "ca. 2'500 Trafostationen"], ["EKZ", "17'187 km Netz in Erneuerung"], ["ewz", "Unterwerke, z.B. Oerlikon"], ["IWB", "Netzknoten Basel verstärkt"]]],
      ["Facility Manager", "building", [["CBRE GWS", "Pharmamandate Basel, NEA-Lasttests"], ["Equans FM", "Fusion 02/2026: Lieferanten werden neu gewählt"]]],
      ["Elektroplaner", "pen", [["Amstein + Walthert", ">1'100 MA, legt NEA/USV für Spitäler und RZ fest"]]],
    ];
    cols.forEach(([h, ic, items], i) => {
      const x = 0.5 + i * 3.05;
      card(s, x, 1.5, 2.85, 3.0);
      iconCircle(s, ic, x + 0.2, 1.7, 0.45);
      txt(s, h, { x: x + 0.8, y: 1.73, w: 2, h: 0.4, fontFace: HF, fontSize: 13, bold: true, color: C.ink, valign: "middle" });
      const runs = [];
      items.forEach(([n, d], j) => {
        runs.push({ text: n, options: { bold: true, color: C.ink, breakLine: true } });
        runs.push({ text: d, options: { breakLine: j < items.length - 1 } });
      });
      txt(s, runs, { x: x + 0.2, y: 2.35, w: 2.5, h: 2.1, fontSize: 10.5, paraSpaceAfter: 5 });
    });
    txt(s, "7 A-Firmen im Segment. Planer kaufen nicht selbst: Ziel ist die Nennung von Mietlösungen in NEA-, USV- und Provisoriums-Ausschreibungen.",
      { x: 0.5, y: 4.62, w: 9, h: 0.5, fontSize: 11.5, color: C.ink, italic: true });
    footer(s);
    s.addNotes("EVU-Beschaffung ist teils öffentlich (IVöB), das braucht Vorlauf. Bei den Planern zählt Präsenz in der Projektierung, nicht der Preis.");
  }

  // ---------------------------------------------------------------- 9 RZ-Welle Timeline
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "Rechenzentren und Grossprojekte"); title(s, "Die Commissioning-Welle 2026 bis 2028 ist planbar");
    s.addShape(pres.shapes.LINE, { x: 0.7, y: 2.2, w: 8.6, h: 0, line: { color: C.line, width: 2 } });
    const years = [
      ["2026", [["STACK Beringen", "36 MW, Eröffnung geplant, eigenes UW"], ["Green Lupfig", "12 MW, Start 2026"], ["NorthC Genf", "Baustart Q1 2026"], ["Cap2030 GVA", "Etappe 1 ab 2026 (LMB)"]]],
      ["2027", [["NorthC Arlesheim", "fertig Mitte 2027"], ["Flughafen Zürich", "Tower-Bau ab 2027"], ["USZ MITTE1|2", "Rohbau bis Anfang 2027, Gebäudetechnik bis 2031"]]],
      ["2028", [["Digital Realty ZUR4", "15 MW, Eröffnung 2028"], ["FlexBase Laufenburg", "IBN Sommer 2028, Zeitplan umstritten"], ["Vantage ZRH2", "24 MW Glattfelden"]]],
    ];
    years.forEach(([y, items], i) => {
      const x = 0.5 + i * 3.05;
      s.addShape(pres.shapes.OVAL, { x: x + 1.2, y: 2.0, w: 0.4, h: 0.4, fill: { color: C.amber }, line: { color: C.white, width: 2 } });
      txt(s, y, { x, y: 1.45, w: 2.8, h: 0.45, fontFace: HF, fontSize: 20, bold: true, color: C.ink, align: "center" });
      card(s, x, 2.6, 2.8, 2.45);
      const runs = [];
      items.forEach(([n, d], j) => { runs.push({ text: n, options: { bold: true, color: C.ink, breakLine: true } }); runs.push({ text: d, options: { breakLine: j < items.length - 1 } }); });
      txt(s, runs, { x: x + 0.2, y: 2.75, w: 2.45, h: 2.2, fontSize: 10.5, paraSpaceAfter: 4 });
    });
    footer(s);
    s.addNotes("Jedes neue RZ braucht Lastbanktests und NEA-Commissioning. Wer im Bau schon Baustrom liefert, sitzt beim Commissioning am Tisch. Einstieg über GU (Implenia bei Green, ERNE bei FlexBase) oder direkt beim Betreiber. Hyperscaler sprechen oft Englisch, Beschaffung teils EMEA.");
  }

  // ---------------------------------------------------------------- 10 GU/TU + Industrie A
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "GU/TU + Industrie  ·  20 %"); title(s, "18 A-Firmen mit belegtem Anlass");
    const rows = [
      ["Implenia", "GU", "4,70", "GU Green-RZ Lupfig/Dielsdorf, Sisikoner Tunnel bis 2034"],
      ["Digital Realty", "RZ", "4,70", "Spatenstich ZUR4 am 26.08.2026"],
      ["Green Datacenter", "RZ", "4,70", "Lupfig Start 2026, Dielsdorf RZ 3"],
      ["STACK Infrastructure", "RZ", "4,55", "Beringen SH, 36 MW"],
      ["Losinger Marazzi", "GU", "4,45", "Terminal GVA Cap2030, ca. 600 Mio."],
      ["Marti-Gruppe", "GU", "4,45", "2. Gotthardröhre, Hauptlos Süd"],
      ["ERNE / Frutiger", "GU", "4,40", "FlexBase Laufenburg / Sisikoner Tunnel"],
      ["NorthC", "RZ", "4,40", "Arlesheim und Genf parallel im Bau"],
      ["Bachem", "Industrie", "4,40", "Bau K Ramp-up, Werk Sisslerfeld 750 Mio."],
      ["Roche / Lonza", "Industrie", "4,30 / 4,00", "Bau 12 Basel / Ibex Visp Ramp-up 2026"],
      ["FlexBase / Vantage", "RZ", "4,30", "BESS 1,6 GWh + KI-RZ / ZRH2 24 MW"],
      ["USZ, GVA, SBB Energie, OASG", "div.", "4,00-4,15", "Spital-Umbau, Flughafen, Umformer, Openair"],
    ];
    const hdr = ["Firma", "Typ", "Score", "Anlass (Quelle in Excel)"].map(t => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.ink } } }));
    s.addTable([hdr, ...rows.map(r => r.map((t, j) => ({ text: t, options: { bold: j === 0, align: j === 2 ? "center" : "left" } })))], {
      x: 0.5, y: 1.3, w: 9, colW: [2.3, 0.85, 0.95, 4.9], fontFace: BF, fontSize: 9.5, color: C.body,
      border: { type: "solid", pt: 0.5, color: C.line }, rowH: 0.29,
    });
    footer(s);
    s.addNotes("Hier sind die Fakten mit Quelle belegt, siehe Spalte 'Anlass' und 'Quelle' in der Excel. Industrie-Einkauf läuft oft zentral: Zugang über Installateur oder FM vor Ort (ETAVIS K+S, Selmoni, CBRE).");
  }

  // ---------------------------------------------------------------- 11 Korrekturen / Risiken
  {
    const s = pres.addSlide(); s.background = { color: C.bg };
    kicker(s, "Was die Recherche korrigiert"); title(s, "Sechs Punkte, bevor wir anrufen");
    const items = [
      ["ban", "Steiner AG raus", "Nachlassstundung, kein TU-Neugeschäft in der Deutschschweiz seit 2023."],
      ["search", "Compagnoni unabhängig", "Elektro Compagnoni ist keine Burkhalter-Tochter, sondern Familienfirma."],
      ["handshake", "Kummler+Matter", "Vermietet eigene mobile Trafostationen: Partner und Wettbewerber zugleich."],
      ["industry", "Stahl bewusst C", "Gerlafingen und Swiss Steel laufen mit Staatshilfe: Bonität prüfen."],
      ["gavel", "Öffentliche Beschaffung", "ewz, USZ, SBB, CSCS: IVöB-Verfahren und Fristen einplanen."],
      ["warn", "BKW am Lauberhorn", "BKW ist Sponsor: Konkurrenzlage vor der Ansprache klären."],
    ];
    items.forEach(([ic, h, d], i) => {
      const x = 0.5 + (i % 3) * 3.05, y = 1.4 + Math.floor(i / 3) * 1.85;
      card(s, x, y, 2.85, 1.65);
      iconCircle(s, ic, x + 0.2, y + 0.2, 0.45);
      txt(s, h, { x: x + 0.8, y: y + 0.22, w: 1.95, h: 0.45, fontFace: HF, fontSize: 12, bold: true, color: C.ink, valign: "middle" });
      txt(s, d, { x: x + 0.2, y: y + 0.8, w: 2.5, h: 0.8, fontSize: 10.5 });
    });
    footer(s);
    s.addNotes("Zusätzlich: Mitarbeiterzahlen teils aus Sekundärquellen, mit 'prüfen' markiert. Ansprechpersonen bewusst nicht erfunden, die LinkedIn-Spalten öffnen nur die Suche.");
  }

  // ---------------------------------------------------------------- 12 Nächste Schritte
  {
    const s = pres.addSlide(); s.background = { color: C.ink };
    kicker(s, "Nächste Schritte (Vorschlag)", true); title(s, "Vom Ranking zur Telefonliste in sechs Wochen", true);
    const steps = [
      ["KW 40-41", "28.09.-09.10.", "CRM-Abgleich", "Kundenstatus eintragen: A-Kunde, Bestand, verloren (mit Datum), Aufbau.", "sync"],
      ["KW 41", "bis 09.10.", "Zuteilung", "Verantwortliche und Prio final je Firma setzen.", "users"],
      ["KW 42-45", "12.10.-06.11.", "Erstkontakt A", "Alle 36 A-Firmen: Ansprechperson verifizieren, Termin anfragen.", "phone"],
      ["KW 46", "ab 09.11.", "Review", "Pipeline-Stand, B-Firmen mit neuem Anlass hochstufen.", "chart"],
    ];
    steps.forEach(([kw, d, h, t, ic], i) => {
      const x = 0.5 + i * 2.3;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.45, w: 2.1, h: 2.55, fill: { color: C.ink2 }, line: { color: C.ink2 }, rectRadius: 0.08 });
      iconCircle(s, ic, x + 0.2, 1.65, 0.45);
      txt(s, kw, { x: x + 0.75, y: 1.62, w: 1.3, h: 0.28, fontFace: HF, fontSize: 12, bold: true, color: C.amber });
      txt(s, d, { x: x + 0.75, y: 1.9, w: 1.3, h: 0.25, fontSize: 9, color: "9AA0A6" });
      txt(s, h, { x: x + 0.2, y: 2.35, w: 1.8, h: 0.35, fontFace: HF, fontSize: 13, bold: true, color: C.white });
      txt(s, t, { x: x + 0.2, y: 2.72, w: 1.75, h: 1.2, fontSize: 10.5, color: "D1D5DB" });
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.2, w: 9, h: 0.8, fill: { color: C.amber }, line: { color: C.amber }, rectRadius: 0.08 });
    txt(s, [{ text: "Der eine Hebel: ", options: { bold: true } }, { text: "der CRM-Abgleich. Erst mit dem echten Kundenstatus wird aus A/B/C eine Reihenfolge, nach der wir telefonieren." }],
      { x: 0.75, y: 4.2, w: 8.5, h: 0.8, fontSize: 13, color: C.ink, valign: "middle" });
    footer(s, true);
    s.addNotes("Termine sind ein Vorschlag. Konkret brauche ich von Mauro und Jörg bis 09.10.2026 den Status je Firma aus dem CRM und bei verlorenen Kunden das Datum und den Grund, falls bekannt.");
  }

  await pres.writeFile({ fileName: "Zielkunden_Schweiz_Praesentation.pptx" });
  console.log("ok");
})();
