# -*- coding: utf-8 -*-
"""Erzeugt Top_Player_Power_Schweiz_2027.xlsx aus daten_power.py."""
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

from daten_power import P, W, COMP, RATES, EVENTS, EVU, PAKETE, PK_SOLAR, PAKET_TOP, TOP_MIN, ZIELROLLE, PRODUKTE, MATRIX, PORTFOLIO, RZ_DETAIL, PLAN, GLOSSAR, rate_gen, rate_lb, rate_bess, RZ, INF, NETZ, SPI, IND, EVT, KAN

OUT = "Top_Player_Power_Schweiz_2027.xlsx"
STAND = "27.09.2026"
RED, GREY, LIGHT, DARK = "E00036", "58595B", "F2F2F2", "3C3C3B"
F = "Arial"
thin = Side(style="thin", color="D6D6D6")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
CHF = "#,##0;-#,##0;-"
SEGS = [RZ, INF, NETZ, SPI, IND, EVT, KAN]


def font(**k):
    k.setdefault("name", F)
    k.setdefault("size", 10)
    return Font(**k)


def fill(c):
    return PatternFill("solid", fgColor=c)


def title(ws, t, sub):
    ws["A1"] = t
    ws["A1"].font = font(size=18, bold=True, color="000000")
    ws["A2"] = sub
    ws["A2"].font = font(size=9, italic=True, color=GREY)


def header(ws, row, labels, col0=1, fc=RED):
    for i, l in enumerate(labels):
        c = ws.cell(row, col0 + i, l)
        c.font = font(bold=True, color="FFFFFF")
        c.fill = fill(fc)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[row].height = 32


def g(e, pot):
    return e


def score(r):
    pot = r[9] * r[10] * rate_gen() + r[11] * r[12] * rate_lb() + r[13] * r[14] * rate_bess()
    return pot * r[15] * r[16]


rows = sorted(P, key=lambda r: -score(r))
wb = Workbook()
st = wb.active
st.title = "Start"
tp = wb.create_sheet("Top-Player")
pl = wb.create_sheet("90-Tage-Plan")
evs_ws = wb.create_sheet("Events 2027")
evu_ws = wb.create_sheet("EVU & Energie 2027")
rzs = wb.create_sheet("Rechenzentren")
pb = wb.create_sheet("Produktbedarf")
pf = wb.create_sheet("Portfolio")
an = wb.create_sheet("Annahmen")
bo = wb.create_sheet("Beobachten")
wt = wb.create_sheet("Wettbewerb")
gl = wb.create_sheet("Glossar")
me = wb.create_sheet("Methode & Quellen")
li = wb.create_sheet("Listen")

# ================================================================= Annahmen
title(an, "Annahmen: Mietsätze und Schwellen", f"Stand {STAND}  |  gelbe Zellen = Eingaben  |  Spalte E «MiT-Satz» überschreibt den Richtwert")
header(an, 4, ["Parameter", "Richtwert", "Einheit", "Quelle / Herleitung", "MiT-Satz (eintragen)", "gilt"])
A = {}  # Name -> Zelle mit gültigem Wert


def arow(r, name, val, unit, src, key=None, fmt="#,##0", editable=True, mit=True):
    an.cell(r, 1, name)
    c = an.cell(r, 2, val)
    c.number_format = fmt
    an.cell(r, 3, unit)
    an.cell(r, 4, src)
    if editable and not (isinstance(val, str) and val.startswith("=")):
        c.font = font(color="0000FF")
        c.fill = fill("FFFF00")
    if mit:
        an.cell(r, 5).fill = fill("FFFF00")
        an.cell(r, 5).font = font(color="0000FF")
        an.cell(r, 5).number_format = fmt
        an.cell(r, 6, f'=IF(E{r}<>"",E{r},B{r})').number_format = fmt
        an.cell(r, 6).font = font(bold=True)
    if key:
        A[key] = f"Annahmen!$F${r}" if mit else f"Annahmen!$B${r}"
    for col in range(1, 7):
        an.cell(r, col).border = BORDER
        an.cell(r, col).alignment = Alignment(wrap_text=True, vertical="top")


R0 = RATES
arow(5, "Wechselkurs USD/CHF", R0["fx"], "CHF je USD", "Stichdatum 24.09.2026: 1 USD = 0,828 CHF (exchangerates.org.uk / Wise)", "fx", "0.000", mit=False)
arow(6, "cos phi (Generator-Nennleistung)", R0["cosphi"], "", "Standard 0,8: 1 MVA ≈ 0,8 MW Wirkleistung", "cos", "0.00", mit=False)
arow(7, "Generator Miete, tief", R0["gen_usd_lo"], "USD pro MW und Woche", "US-Richtwert 500 kW: 2'500-3'900 USD/Woche, hochgerechnet auf 1 MW (dieselfuelhq.com, 2026)", mit=False)
arow(8, "Generator Miete, hoch", R0["gen_usd_hi"], "USD pro MW und Woche", "wie oben", mit=False)
arow(9, "Generator Miete (Modell)", "=AVERAGE(B7:B8)*B6*B5", "CHF pro MVA und Woche", "Mittelwert × cos phi × Kurs. Nur Grössenordnung, durch MiT-Preisliste ersetzen", "gen", editable=False)
arow(10, "Lastbank Miete, tief", R0["lb_usd_lo"], "USD pro MW und Woche", "US-Richtwert 1-MW-Lastbank: 1'600-3'100 USD/Woche (countbricks.com, 2026)", mit=False)
arow(11, "Lastbank Miete, hoch", R0["lb_usd_hi"], "USD pro MW und Woche", "wie oben", mit=False)
arow(12, "Lastbank Miete (Modell)", "=AVERAGE(B10:B11)*B5", "CHF pro MW und Woche", "Mittelwert × Kurs. Ohne Personal/Engineering für IST", "lb", editable=False)
arow(13, "BESS Miete, tief", R0["bess_usd_lo"], "USD pro MW und Monat", "Bandbreite 10'000-50'000 USD/MW/Monat (ritarpower.com, Herstellerblog, nicht belastbar)", mit=False)
arow(14, "BESS Miete, hoch", R0["bess_usd_hi"], "USD pro MW und Monat", "wie oben", mit=False)
arow(15, "BESS Miete (Modell)", "=AVERAGE(B13:B14)*B5", "CHF pro MW und Monat", "Mittelwert × Kurs. Nutzbare Kapazität und C-Rate je Projekt klären", "bess", editable=False)
arow(16, "Mobiler Trafo Miete", "Wert fehlt", "CHF pro Woche", "Öffentlich nicht gefunden: aus MiT-Preisliste ergänzen. Nicht im Potenzial enthalten", fmt="@", editable=False, mit=False)
arow(17, "Transport, Montage, Service", "Wert fehlt", "CHF", "Nicht im Potenzial enthalten: aus MiT-Preisliste ergänzen", fmt="@", editable=False, mit=False)
arow(19, "Dieselverbrauch 1 MVA bei 75 % Last", R0["diesel_lh"], "l/h", "Cummins C1000 D5: 139 l/h Prime, 154 l/h Standby (Datenblatt)", "dl", mit=False)
arow(20, "Dieselpreis Schweiz", R0["diesel_chf"], "CHF/l", "TCS 18.09.2026: 2,41 CHF/l (Tankstelle, Gewerbepreis tiefer)", "dc", "0.00", mit=False)
arow(21, "Treibstoffkosten 1 MVA bei 75 % Last", "=B19*B20", "CHF pro Stunde", "Argument für BESS-Hybrid: jede Stunde Generator-Leerlauf kostet", "fuel", editable=False, mit=False)
arow(22, "Temporäre Kühlung (Cross-Sell)", f"={R0['cool_usd_month']}/{R0['cool_mw']}*B5", "CHF pro MW (therm.) und Monat", "US-Lease 500 t Chiller (ca. 1,75 MW) 34'666 USD/Monat (kwipped.com). Nur Info", "cool", editable=False, mit=False)
arow(24, "Prio A ab Erwartung 2027", 25000, "CHF", "Erwartung = Potenzial × Anteil 2027 × Wahrscheinlichkeit", "pa", mit=False)
arow(25, "Prio B ab Erwartung 2027", 10000, "CHF", "darunter Prio C", "pb", mit=False)
arow(26, "Schwelle Top-Player (Potenzial)", 50000, "CHF", "Vorgabe: Projekte mit mehr als CHF 50'000 Potenzial", "thr", mit=False)
for c in "ABCDEF":
    an.column_dimensions[c].width = {"A": 34, "B": 13, "C": 22, "D": 70, "E": 16, "F": 12}[c]
an.freeze_panes = "A5"

# ================================================================= Top-Player
COLS = [("Rang", 6), ("Prio", 6), ("Segment", 15), ("Projekt / Kunde", 32), ("Einstieg über", 28), ("Ort", 16),
        ("Kt.", 6), ("Region", 15), ("Sprache", 8), ("Anlass und Zeitfenster", 40), ("Power-Bedarf", 38),
        ("Generator MVA", 9), ("Generator Wochen", 9), ("Lastbank MW", 9), ("Lastbank Wochen", 9),
        ("BESS MW", 8), ("BESS Monate", 8), ("Potenzial Power CHF", 13), ("Anteil 2027", 9),
        ("Wahrschein-lichkeit", 10), ("Erwartung 2027 CHF", 13), ("Cross-Sell Wärme / Kälte", 28),
        ("Nächster Schritt", 38), ("Verantwortlich", 13), ("Status MiT (CRM)", 18), ("Zielrolle", 30), ("Ansprechperson (Name)", 22),
        ("Kontakt (Tel. / E-Mail)", 24), ("Letzter Kontakt", 11), ("Nächster Termin", 11), ("Quelle", 9), ("Hinweis / Annahme", 38)]
H = {n: get_column_letter(i + 1) for i, (n, _) in enumerate(COLS)}
title(tp, "Top-Player Power Schweiz 2027",
      f"Stand {STAND}  |  {len(rows)} Projekte mit Potenzial über CHF 50'000  |  sortiert nach Erwartung 2027  |  VERTRAULICH")
tp["A3"] = ("Blaue Zahlen = Szenario-Annahmen, änderbar. Potenzial = Generator (MVA × Wochen × Satz) + Lastbank (MW × Wochen × Satz) "
            "+ BESS (MW × Monate × Satz). Sätze im Blatt «Annahmen».")
tp["A3"].font = font(size=9, color="0000FF")
HR, FR = 4, 5
LR = FR + len(rows) - 1
header(tp, HR, [c for c, _ in COLS])
for i, (_, w) in enumerate(COLS):
    tp.column_dimensions[get_column_letter(i + 1)].width = w
INPUT = {"Generator MVA", "Generator Wochen", "Lastbank MW", "Lastbank Wochen", "BESS MW", "BESS Monate",
         "Anteil 2027", "Wahrschein-lichkeit", "Verantwortlich", "Status MiT (CRM)", "Nächster Schritt",
         "Ansprechperson (Name)", "Kontakt (Tel. / E-Mail)", "Letzter Kontakt", "Nächster Termin"}
WRAP = {"Zielrolle", "Projekt / Kunde", "Einstieg über", "Anlass und Zeitfenster", "Power-Bedarf", "Cross-Sell Wärme / Kälte",
        "Nächster Schritt", "Hinweis / Annahme", "Ort", "Segment"}
for n, r in enumerate(rows):
    (seg, proj, ein, ort, kt, reg, spr, anl, bed, gm, gw, lm, lw, bm, bmo, a27, p, cs, step, src, hint) = r
    x = FR + n
    L = lambda c: f"{H[c]}{x}"
    v = {
        "Rang": f"=RANK({L('Erwartung 2027 CHF')},${H['Erwartung 2027 CHF']}${FR}:${H['Erwartung 2027 CHF']}${LR})"
                f"+COUNTIF(${H['Erwartung 2027 CHF']}${FR}:{L('Erwartung 2027 CHF')},{L('Erwartung 2027 CHF')})-1",
        "Prio": f'=IF({L("Erwartung 2027 CHF")}>={A["pa"]},"A",IF({L("Erwartung 2027 CHF")}>={A["pb"]},"B","C"))',
        "Segment": seg, "Projekt / Kunde": proj, "Einstieg über": ein, "Ort": ort, "Kt.": kt, "Region": reg,
        "Sprache": spr, "Anlass und Zeitfenster": anl, "Power-Bedarf": bed,
        "Generator MVA": gm, "Generator Wochen": gw, "Lastbank MW": lm, "Lastbank Wochen": lw,
        "BESS MW": bm, "BESS Monate": bmo,
        "Potenzial Power CHF": f"=ROUND({L('Generator MVA')}*{L('Generator Wochen')}*{A['gen']}"
                               f"+{L('Lastbank MW')}*{L('Lastbank Wochen')}*{A['lb']}"
                               f"+{L('BESS MW')}*{L('BESS Monate')}*{A['bess']},-2)",
        "Anteil 2027": a27, "Wahrschein-lichkeit": p,
        "Erwartung 2027 CHF": f"=ROUND({L('Potenzial Power CHF')}*{L('Anteil 2027')}*{L('Wahrschein-lichkeit')},-2)",
        "Cross-Sell Wärme / Kälte": cs or None, "Nächster Schritt": step, "Verantwortlich": None,
        "Status MiT (CRM)": "Offen: CRM prüfen", "Zielrolle": ZIELROLLE[seg],
        "Ansprechperson (Name)": None, "Kontakt (Tel. / E-Mail)": None, "Letzter Kontakt": None, "Nächster Termin": None,
        "Quelle": "Link", "Hinweis / Annahme": hint or None,
    }
    if proj in PAKETE:
        ds = "EVU & Energie 2027" if proj == PK_SOLAR else "Events 2027"
        sif = lambda col: f"SUMIF('{ds}'!$W$5:$W$200,\"{proj}\",'{ds}'!${col}$5:${col}$200)"
        v["Generator MVA"], v["Generator Wochen"] = 1, "=" + sif("O")
        v["Lastbank MW"], v["Lastbank Wochen"] = 1, "=" + sif("P")
        v["BESS MW"], v["BESS Monate"] = 1, "=" + sif("Q")
        v["Anteil 2027"] = f"=IFERROR({sif('V')}/{sif('R')},0)"
    for i, (c, _) in enumerate(COLS):
        cell = tp.cell(x, i + 1, v[c])
        cell.font = font(size=9, color="0000FF" if c in INPUT else "000000", bold=c in ("Projekt / Kunde", "Erwartung 2027 CHF"))
        cell.alignment = Alignment(wrap_text=c in WRAP, vertical="top",
                                   horizontal="center" if c in ("Rang", "Prio", "Kt.", "Sprache") else None)
        cell.border = BORDER
    for c in ("Potenzial Power CHF", "Erwartung 2027 CHF"):
        tp[L(c)].number_format = CHF
    for c in ("Anteil 2027", "Wahrschein-lichkeit"):
        tp[L(c)].number_format = "0%"
    for c in ("Letzter Kontakt", "Nächster Termin"):
        tp[L(c)].number_format = "DD.MM.YYYY"
    for c in ("Generator MVA", "Lastbank MW", "BESS MW"):
        tp[L(c)].number_format = "0.0"
    tp[L("Quelle")].hyperlink = src
    tp[L("Quelle")].font = font(size=9, color="0563C1", underline="single")
    tp.row_dimensions[x].height = 52
tab = Table(displayName="TopPlayer", ref=f"A{HR}:{get_column_letter(len(COLS))}{LR}")
tab.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
tp.add_table(tab)
tp.freeze_panes = f"{H['Einstieg über']}{FR}"
for c, (bg, fg) in {"A": ("E00036", "FFFFFF"), "B": ("58595B", "FFFFFF"), "C": ("D9D9D9", "000000")}.items():
    tp.conditional_formatting.add(f"{H['Prio']}{FR}:{H['Prio']}{LR}",
                                  CellIsRule(operator="equal", formula=[f'"{c}"'], fill=fill(bg), font=Font(name=F, bold=True, color=fg)))
tp.conditional_formatting.add(f"{H['Potenzial Power CHF']}{FR}:{H['Potenzial Power CHF']}{LR}",
                              CellIsRule(operator="lessThan", formula=[A["thr"]], fill=fill("FFC7CE")))
for c in ("Potenzial Power CHF", "Erwartung 2027 CHF"):
    from openpyxl.formatting.rule import DataBarRule
    tp.conditional_formatting.add(f"{H[c]}{FR}:{H[c]}{LR}", DataBarRule(start_type="min", end_type="max", color="F4A6B8"))

# Listen + Validierung
for col, (nm, vals) in {"A": ("Segment", SEGS), "B": ("Team", ["Burak", "Mauro", "Jörg", "Roberto"]),
                        "C": ("Status", ["Offen: CRM prüfen", "A-Kunde", "Bestandskunde mit Potenzial", "Verlorener Kunde", "Potenzial / Aufbau"])}.items():
    li[f"{col}1"] = nm
    for i, v_ in enumerate(vals):
        li[f"{col}{i + 2}"] = v_
li.sheet_state = "hidden"
for rng, f in ((H["Segment"], "=Listen!$A$2:$A$8"), (H["Verantwortlich"], "=Listen!$B$2:$B$5"), (H["Status MiT (CRM)"], "=Listen!$C$2:$C$6")):
    d = DataValidation(type="list", formula1=f, allow_blank=True)
    tp.add_data_validation(d)
    d.add(f"{rng}{FR}:{rng}{LR + 50}")
for c in ("Anteil 2027", "Wahrschein-lichkeit"):
    d = DataValidation(type="decimal", operator="between", formula1="0", formula2="1", allow_blank=True)
    d.error = "Wert zwischen 0 % und 100 %"
    tp.add_data_validation(d)
    d.add(f"{H[c]}{FR}:{H[c]}{LR + 50}")

# ================================================================= Start
title(st, "Top-Player Power Schweiz 2027", f"Mobil in Time AG · Strom Schweiz  |  Stand {STAND}  |  VERTRAULICH, intern")
expl = [
    "So liest du die Liste",
    "1. Nur Projekte, bei denen Power-Mieten über CHF 50'000 möglich sind. Schwerpunkt Rechenzentren, dazu Tunnel, Netz, Spitäler, Industrie, Events.",
    "2. Potenzial = was das Projekt an Generator-, Lastbank- und BESS-Miete bringen kann (Szenario, blau, änderbar).",
    "3. Erwartung 2027 = Potenzial × Anteil, der 2027 anfällt × Wahrscheinlichkeit, dass MiT gewinnt. Das ist die realistische Zahl.",
    "4. Sätze sind Markt-Richtwerte (US, umgerechnet), keine MiT-Preise. Im Blatt «Annahmen» Spalte E eure Sätze eintragen: alles rechnet neu.",
    "5. Trafo-Miete, Transport, Service und Treibstoff sind nicht eingerechnet: das Potenzial ist konservativ.",
]
for i, t in enumerate(expl):
    c = st.cell(4 + i, 1, t)
    c.font = font(size=11 if i else 12, bold=(i == 0), color=RED if i == 0 else "000000")
TPR = lambda c: f"'Top-Player'!${H[c]}${FR}:${H[c]}${LR}"
kpis = [("Top-Player", f"=COUNTA({TPR('Projekt / Kunde')})", "0"),
        ("Potenzial brutto CHF", f"=SUM({TPR('Potenzial Power CHF')})", CHF),
        ("Erwartung 2027 CHF", f"=SUM({TPR('Erwartung 2027 CHF')})", CHF),
        ("davon Rechenzentren", f'=SUMIF({TPR("Segment")},"{RZ}",{TPR("Erwartung 2027 CHF")})', CHF),
        ("Prio A", f'=COUNTIF({TPR("Prio")},"A")', "0")]
for i, (lab, f, fmt) in enumerate(kpis):
    col = 1 + i * 2
    a_ = st.cell(11, col, lab)
    b_ = st.cell(12, col, f)
    st.merge_cells(start_row=11, start_column=col, end_row=11, end_column=col + 1)
    st.merge_cells(start_row=12, start_column=col, end_row=12, end_column=col + 1)
    a_.font = font(size=9, color="FFFFFF", bold=True)
    b_.font = font(size=18, bold=True, color="FFFFFF")
    b_.number_format = fmt
    for rr in (11, 12):
        for cc in (col, col + 1):
            st.cell(rr, cc).fill = fill(RED if i == 2 else GREY)
            st.cell(rr, cc).alignment = Alignment(horizontal="center", vertical="center")
st.row_dimensions[12].height = 36

st.cell(14, 1, "Nach Segment").font = font(size=12, bold=True, color=RED)
header(st, 15, ["Segment", "Anzahl", "Potenzial brutto CHF", "Erwartung 2027 CHF", "Anteil an Erwartung"])
for i, sgm in enumerate(SEGS):
    r = 16 + i
    st.cell(r, 1, sgm)
    st.cell(r, 2, f'=COUNTIF({TPR("Segment")},A{r})')
    st.cell(r, 3, f'=SUMIF({TPR("Segment")},A{r},{TPR("Potenzial Power CHF")})').number_format = CHF
    st.cell(r, 4, f'=SUMIF({TPR("Segment")},A{r},{TPR("Erwartung 2027 CHF")})').number_format = CHF
    st.cell(r, 5, f"=IF(SUM($D$16:$D$22)=0,0,D{r}/SUM($D$16:$D$22))").number_format = "0%"
st.cell(23, 1, "Total").font = font(bold=True)
for c in (2, 3, 4):
    L_ = get_column_letter(c)
    st.cell(23, c, f"=SUM({L_}16:{L_}22)").number_format = CHF if c > 2 else "0"
    st.cell(23, c).font = font(bold=True)
for row in st.iter_rows(min_row=16, max_row=23, max_col=5):
    for c in row:
        c.border = BORDER
        if c.font.bold is not True:
            c.font = font()

st.cell(25, 1, "Top 10 nach Erwartung 2027").font = font(size=12, bold=True, color=RED)
header(st, 26, ["Rang", "Projekt / Kunde", "Segment", "Erwartung 2027 CHF", "Potenzial CHF", "Prio"])
for k in range(1, 11):
    r = 26 + k
    m = f"MATCH({k},{TPR('Rang')},0)"
    st.cell(r, 1, k)
    st.cell(r, 2, f"=INDEX({TPR('Projekt / Kunde')},{m})")
    st.cell(r, 3, f"=INDEX({TPR('Segment')},{m})")
    st.cell(r, 4, f"=INDEX({TPR('Erwartung 2027 CHF')},{m})").number_format = CHF
    st.cell(r, 5, f"=INDEX({TPR('Potenzial Power CHF')},{m})").number_format = CHF
    st.cell(r, 6, f"=INDEX({TPR('Prio')},{m})")
    for c in range(1, 7):
        st.cell(r, c).border = BORDER
        st.cell(r, c).font = font()
for c, w in zip("ABCDEFGHIJ", (34, 34, 18, 18, 16, 10, 12, 12, 12, 12)):
    st.column_dimensions[c].width = w

ch = BarChart()
ch.type = "bar"
ch.title = "Erwartung 2027 nach Segment (CHF)"
ch.add_data(Reference(st, min_col=4, min_row=15, max_row=22), titles_from_data=True)
ch.set_categories(Reference(st, min_col=1, min_row=16, max_row=22))
ch.series[0].graphicalProperties.solidFill = RED
ch.legend = None
ch.y_axis.majorGridlines = None
ch.y_axis.numFmt = "#,##0"
ch.height, ch.width = 8, 15
ch.dataLabels = DataLabelList()
ch.dataLabels.showVal = True
st.add_chart(ch, "H14")
ch2 = BarChart()
ch2.type = "bar"
ch2.title = "Top 10: Erwartung 2027 (CHF)"
ch2.add_data(Reference(st, min_col=4, min_row=26, max_row=36), titles_from_data=True)
ch2.set_categories(Reference(st, min_col=2, min_row=27, max_row=36))
ch2.series[0].graphicalProperties.solidFill = GREY
ch2.legend = None
ch2.y_axis.majorGridlines = None
ch2.x_axis.scaling.orientation = "maxMin"
ch2.height, ch2.width = 9, 15
st.add_chart(ch2, "H31")
st.cell(39, 1, "Blätter in dieser Datei").font = font(size=12, bold=True, color=RED)
nav = [("Top-Player", f"Die {len(rows)} Projekte und Pakete über CHF 50'000 mit Szenario, Kontakt, nächstem Schritt"),
       ("Events 2027", f"{len(EVENTS)} Anlässe 2026/27 einzeln, gebündelt in Saisonpakete"),
       ("EVU & Energie 2027", "Weitere Netz-, Kraftwerks-, Solar- und Fernwärmeprojekte"),
       ("90-Tage-Plan", "Aufgaben Okt. 2026 bis Jan. 2027 mit Status zum Abhaken"),
       ("Rechenzentren", "Alle RZ-Projekte 2026-2028 mit MW, Zeitplan, GU, Netzanschluss"),
       ("Produktbedarf", "Welches Segment welches Power-Produkt braucht"),
       ("Portfolio", "Was wir vermieten, Kennwerte, Cross-Sell"),
       ("Annahmen", "Mietsätze, Kurs, Schwellen: hier MiT-Sätze eintragen"),
       ("Beobachten", "Unter CHF 50'000 oder noch zu unsicher"),
       ("Wettbewerb", "Anbieter mobiler Power in der Schweiz"),
       ("Glossar", "Alle Abkürzungen"),
       ("Methode & Quellen", "Wie gerechnet wurde und woher die Fakten stammen")]
for i, (sh_, t_) in enumerate(nav):
    c = st.cell(40 + i, 1, sh_)
    c.hyperlink = f"#'{sh_}'!A1"
    c.font = font(color="0563C1", underline="single", bold=True)
    st.cell(40 + i, 2, t_).font = font()
PLR = f"'90-Tage-Plan'!$H$5:$H${4 + len(PLAN)}"
st.cell(51, 1, "Stand 90-Tage-Plan").font = font(size=12, bold=True, color=RED)
for i, stt in enumerate(("offen", "in Arbeit", "erledigt", "verschoben")):
    st.cell(52 + i, 1, stt).font = font()
    st.cell(52 + i, 2, f'=COUNTIF({PLR},A{52 + i})').font = font(bold=True)
st.sheet_view.showGridLines = False


# ================================================================ 90-Tage-Plan
import datetime as _dt
from openpyxl.formatting.rule import ColorScaleRule
title(pl, "90-Tage-Plan Oktober 2026 bis Januar 2027", "Vorschlag, im Team bestätigen. Status per Dropdown, überfällige Termine werden rot.")
header(pl, 4, ["Nr.", "Monat", "Termin", "Aufgabe", "Projekt / Kunde", "Erwartung 2027 CHF", "Verantwortlich", "Status", "Ergebnis / Notiz"])
for i, (mon, dat, task, proj) in enumerate(PLAN):
    r = 5 + i
    dd_, mm_, yy_ = map(int, dat.split("."))
    vals = [i + 1, mon, _dt.date(yy_, mm_, dd_), task, proj,
            ("" if proj == "alle" else "=" + "+".join(
                f'IFERROR(INDEX({TPR("Erwartung 2027 CHF")},MATCH("{pt}",{TPR("Projekt / Kunde")},0)),0)'
                for pt in proj.split(" / "))), None, "offen", None]
    for j, v_ in enumerate(vals):
        c = pl.cell(r, j + 1, v_)
        c.font = font(size=10, bold=(j == 4), color="0000FF" if j in (6, 7, 8) else "000000")
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BORDER
    pl.cell(r, 3).number_format = "DD.MM.YYYY"
    pl.cell(r, 6).number_format = CHF
    pl.row_dimensions[r].height = 32
PL_LAST = 4 + len(PLAN)
for c_, w_ in zip("ABCDEFGHI", (5, 11, 11, 58, 34, 14, 13, 12, 36)):
    pl.column_dimensions[c_].width = w_
d_ = DataValidation(type="list", formula1='"offen,in Arbeit,erledigt,verschoben"', allow_blank=True)
pl.add_data_validation(d_)
d_.add(f"H5:H{PL_LAST + 30}")
d_ = DataValidation(type="list", formula1="=Listen!$B$2:$B$5", allow_blank=True)
pl.add_data_validation(d_)
d_.add(f"G5:G{PL_LAST + 30}")
pl.conditional_formatting.add(f"H5:H{PL_LAST}", CellIsRule(operator="equal", formula=['"erledigt"'], fill=fill("C6EFCE")))
pl.conditional_formatting.add(f"H5:H{PL_LAST}", CellIsRule(operator="equal", formula=['"in Arbeit"'], fill=fill("FFEB9C")))
pl.conditional_formatting.add(f"C5:C{PL_LAST}", FormulaRule(formula=['AND(C5<TODAY(),H5<>"erledigt")'], fill=fill("FFC7CE")))
pl.freeze_panes = "A5"

# ================================================================ Rechenzentren
title(rzs, "Rechenzentren Schweiz 2026-2028", "Fakten aus öffentlichen Quellen, Stand 27.09.2026. (?) = unsicher. Potenzial nur für Top-Player (Blatt «Top-Player»).")
header(rzs, 4, ["Betreiber / Projekt", "Standort", "IT-Leistung MW", "Zeitplan", "GU / PM", "Netzanschluss", "Für uns", "Quelle"])
for i, row in enumerate(RZ_DETAIL):
    r = 5 + i
    for j, v_ in enumerate(row):
        c = rzs.cell(r, j + 1, v_)
        c.font = font(size=10, bold=(j == 0), color=RED if (j == 6 and v_.startswith("Hot")) else "000000")
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BORDER
    rzs.row_dimensions[r].height = 42
rr = 6 + len(RZ_DETAIL)
rzs.cell(rr, 1, "Commissioning (IST) in Kürze").font = font(size=12, bold=True, color=RED)
facts = ["IST Level 5: Strom, Kälte und Notstrom laufen gemeinsam auf Design-Last, Netz wird getrennt, Fehler werden simuliert.",
         "Lastbank-Leistung ≈ Design-IT-Last der getesteten Data Hall, dazu Heizlastbänke im White Space.",
         "Laststufen 25 / 50 / 75 / 100 %, danach mehrere Stunden Volllast.",
         "IST-Fenster typisch 4 bis 6 Wochen; 8 bis 16 Wochen von erster Energisierung bis IST-Abschluss je Data Hall.",
         "Mängel im IST erzwingen Re-Tests und damit erneute Lastbank-Miete.",
         "Quellen: anvilfield.com (IST Field Guide), sunbeltsolomon.com, hillstone.co.uk (US/UK-Fachquellen)."]
for i, f_ in enumerate(facts):
    rzs.cell(rr + 1 + i, 1, f_).font = font(size=10, italic=(i == len(facts) - 1))
for c_, w_ in zip("ABCDEFGH", (24, 20, 16, 36, 28, 36, 28, 32)):
    rzs.column_dimensions[c_].width = w_
rzs.freeze_panes = "B5"

# ================================================================ Produktbedarf
title(pb, "Produktbedarf je Segment", "3 = Kernbedarf, 2 = häufig, 1 = gelegentlich, 0 = kaum. Einschätzung aus den Szenarien, änderbar.")
header(pb, 4, ["Segment"] + PRODUKTE + ["Top-Player", "Erwartung 2027 CHF"])
for i, (sg, vals) in enumerate(MATRIX.items()):
    r = 5 + i
    pb.cell(r, 1, sg).font = font(bold=True)
    for j, v_ in enumerate(vals):
        c = pb.cell(r, 2 + j, v_)
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.font = font(bold=True, color="0000FF")
    pb.cell(r, 8, f'=COUNTIF({TPR("Segment")},A{r})')
    pb.cell(r, 9, f'=SUMIF({TPR("Segment")},A{r},{TPR("Erwartung 2027 CHF")})').number_format = CHF
    for j in range(1, 10):
        pb.cell(r, j).border = BORDER
    pb.row_dimensions[r].height = 26
pb.conditional_formatting.add(f"B5:G{4 + len(MATRIX)}", ColorScaleRule(start_type="num", start_value=0, start_color="F2F2F2",
                                                                    mid_type="num", mid_value=1.5, mid_color="BDBDBD",
                                                                    end_type="num", end_value=3, end_color="E00036"))
for c_, w_ in zip("ABCDEFGHI", (20, 12, 12, 12, 14, 15, 13, 11, 17)):
    pb.column_dimensions[c_].width = w_
pb.cell(6 + len(MATRIX), 1, "Lesart: Generator ist überall Türöffner, Lastbank im RZ, Trafo im Netz, BESS bei Events und Nachtbaustellen.").font = font(italic=True)

# ================================================================ Portfolio
title(pf, "Portfolio Power und Cross-Sell", "Was wir vermieten, wofür, an wen. Kennwerte laut Quelle; fehlende Werte als Lücke markiert.")
header(pf, 4, ["Produkt", "Wofür", "Typische Kunden", "Kennwerte / Hinweis", "Quelle"])
for i, row in enumerate(PORTFOLIO):
    r = 5 + i
    for j, v_ in enumerate(row):
        c = pf.cell(r, j + 1, v_)
        c.font = font(size=10, bold=(j == 0), color=RED if "Wert fehlt" in str(v_) else "000000")
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BORDER
    pf.row_dimensions[r].height = 48
for c_, w_ in zip("ABCDE", (22, 40, 34, 60, 30)):
    pf.column_dimensions[c_].width = w_

# ================================================================ Glossar
title(gl, "Glossar: Abkürzungen", "Gleiche Liste wie im Anhang der Präsentation.")
header(gl, 4, ["Kürzel", "Bedeutung"])
for i, (k_, v_) in enumerate(GLOSSAR):
    for j, t_ in enumerate((k_, v_)):
        c = gl.cell(5 + i, j + 1, t_)
        c.font = font(bold=(j == 0))
        c.border = BORDER
gl.column_dimensions["A"].width, gl.column_dimensions["B"].width = 26, 70


# ================================================================ Events 2027 / EVU & Energie 2027
DH = ["Nr.", "Name", "Kategorie", "Ort", "Region", "Datum / Zeitfenster", "Grösse", "Warum Strombedarf",
      "Generator MVA", "Generator Wochen", "Lastbank MW", "Lastbank Wochen", "BESS MW", "BESS Monate",
      "MVA-Wochen", "Lastbank MW-Wochen", "BESS MW-Monate", "Potenzial CHF", "Anteil 2027", "Wahrschein-lichkeit",
      "Erwartung 2027 CHF", "Potenzial × Anteil", "Paket / Zuordnung", "Quelle"]
DW = (5, 30, 16, 20, 15, 20, 22, 38, 9, 9, 9, 9, 8, 8, 9, 9, 9, 12, 9, 10, 12, 11, 34, 9)


def detail_sheet(ws, ttl, sub, items, pakete, note):
    title(ws, ttl, sub)
    header(ws, 4, DH)
    for c_, w_ in enumerate(DW):
        ws.column_dimensions[get_column_letter(c_ + 1)].width = w_
    for i, it in enumerate(items):
        r = 5 + i
        vals = [i + 1] + list(it["txt"]) + [it["gm"], it["gw"], it["lm"], it["lw"], it["bm"], it["bmo"],
                f"=I{r}*J{r}", f"=K{r}*L{r}", f"=M{r}*N{r}",
                f"=ROUND(O{r}*{A['gen']}+P{r}*{A['lb']}+Q{r}*{A['bess']},-2)", it["a27"], it["p"],
                f"=ROUND(R{r}*S{r}*T{r},-2)", f"=R{r}*S{r}", it["pk"], "Link"]
        for j, v_ in enumerate(vals):
            c = ws.cell(r, j + 1, v_)
            c.font = font(size=9, bold=(j == 1), color="0000FF" if 8 <= j <= 13 or j in (18, 19) else "000000")
            c.alignment = Alignment(wrap_text=j in (1, 3, 6, 7, 22), vertical="top")
            c.border = BORDER
        for col in "RUV":
            ws[f"{col}{r}"].number_format = CHF
        for col in "ST":
            ws[f"{col}{r}"].number_format = "0%"
        ws[f"X{r}"].hyperlink = it["src"]
        ws[f"X{r}"].font = font(size=9, color="0563C1", underline="single")
        ws.row_dimensions[r].height = 36
    last = 4 + len(items)
    ws.freeze_panes = "C5"
    ws.conditional_formatting.add(f"R5:R{last}", CellIsRule(operator="greaterThanOrEqual", formula=[A["thr"]], fill=fill("F4A6B8")))
    r0 = last + 2
    ws.cell(r0, 2, "Pakete").font = font(size=12, bold=True, color=RED)
    header(ws, r0 + 1, ["", "Paket", "Anzahl", "Potenzial CHF", "Erwartung 2027 CHF", "In Top-Player"], col0=1)
    for i, pk in enumerate(pakete):
        r = r0 + 2 + i
        ws.cell(r, 2, pk).font = font(bold=True)
        ws.cell(r, 3, f'=COUNTIF($W$5:$W${last},B{r})')
        ws.cell(r, 4, f'=SUMIF($W$5:$W${last},B{r},$R$5:$R${last})').number_format = CHF
        ws.cell(r, 5, f'=SUMIF($W$5:$W${last},B{r},$U$5:$U${last})').number_format = CHF
        ws.cell(r, 6, f'=IF(D{r}>={A["thr"]},"Ja","Nein, unter Schwelle")')
        for c_ in range(2, 7):
            ws.cell(r, c_).border = BORDER
    ws.cell(r0 + 3 + len(pakete), 2, note).font = font(italic=True, size=9)


ev_items = [dict(txt=(e[0], e[1], e[2], e[3], e[4], e[5], e[6]), gm=e[7], gw=e[8], lm=0, lw=0, bm=e[9], bmo=e[10],
                 a27=e[11], p=0.15, pk=e[12], src=e[13]) for e in EVENTS]
ev_pk = list(dict.fromkeys(e[12] for e in EVENTS))
detail_sheet(evs_ws, "Events 2026/27", f"{len(EVENTS)} Anlässe mit Strombedarf. Szenario je Anlass (blau) ist Annahme. "
             "Pakete ab CHF 50'000 erscheinen im Blatt «Top-Player» und rechnen per Formel aus diesem Blatt.",
             ev_items, ev_pk, "Einzelne Events dauern Tage, darum meist unter CHF 50'000. Bündeln lohnt sich: ein Ansprechpartner pro Saison, "
             "gleiche Logistik. Termine mit (?) vor der Akquise beim Veranstalter prüfen.")
evu_items = [dict(txt=(e[0], e[1], e[2], e[3], e[4], e[5], e[6]), gm=e[7], gw=e[8], lm=e[9], lw=e[10], bm=e[11], bmo=e[12],
                  a27=e[13], p=e[14], pk=(e[15] or "nur hier"), src=e[16]) for e in EVU if e[15] != "Top"]
tops = [e[0] for e in EVU if e[15] == "Top"]
detail_sheet(evu_ws, "EVU & Energie 2026-2028", "Netz, Kraftwerke, Batteriespeicher, alpine Solar, Fernwärme. Szenario (blau) ist Annahme.",
             evu_items, [PK_SOLAR, "nur hier"],
             f"Einzeln im Blatt «Top-Player» (Segment Netz / Energie), nicht hier: " + "; ".join(tops) + ".")

# ================================================================ Beobachten
title(bo, "Beobachten", "Unter CHF 50'000, zu früh oder zu unsicher. Quartalsweise prüfen, bei neuem Anlass in «Top-Player» übernehmen.")
header(bo, 4, ["Segment", "Projekt / Kunde", "Ort", "Warum (noch) nicht Top", "Quelle"])
for i, (sg, nm, ort, grund, src) in enumerate(W):
    r = 5 + i
    for j, v_ in enumerate((sg, nm, ort, grund, "Link")):
        c = bo.cell(r, j + 1, v_)
        c.font = font(size=9, bold=(j == 1))
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BORDER
    bo.cell(r, 5).hyperlink = src
    bo.cell(r, 5).font = font(size=9, color="0563C1", underline="single")
for c, w in zip("ABCDE", (18, 40, 20, 70, 9)):
    bo.column_dimensions[c].width = w

# ================================================================= Wettbewerb
title(wt, "Wettbewerb mobiler Strom Schweiz", "Aus Websuche, Angaben auf der verlinkten Seite prüfen.")
header(wt, 4, ["Anbieter", "Angebot", "Quelle"])
for i, (nm, off, src) in enumerate(COMP):
    r = 5 + i
    for j, v_ in enumerate((nm, off, "Link")):
        c = wt.cell(r, j + 1, v_)
        c.font = font(size=10, bold=(j == 0))
        c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical="top")
    wt.cell(r, 3).hyperlink = src
    wt.cell(r, 3).font = font(color="0563C1", underline="single")
wt.column_dimensions["A"].width, wt.column_dimensions["B"].width, wt.column_dimensions["C"].width = 30, 60, 9

# ================================================================= Methode
title(me, "Methode und Quellen", f"Stand {STAND}")
txt = [
    ("Auswahl", "Websuche 27.09.2026 zu Rechenzentren, Grossbaustellen, Unterwerken, Spitälern, Pharma und Events 2026-2028 in der Schweiz."),
    ("", "Aufgenommen, wenn das Power-Szenario mehr als CHF 50'000 Miete ergibt. Alles andere steht in «Beobachten»."),
    ("Szenario", "Je Projekt: Generator MVA × Wochen, Lastbank MW × Wochen, BESS MW × Monate. Grössen sind eigene Annahmen aus den öffentlichen Fakten"),
    ("", "(z.B. Lastbank für IST ≈ IT-Last einer Data Hall, 3-4 Wochen; Tunnel-Backup 52 Wochen). Blaue Zellen anpassen, sobald ihr mehr wisst."),
    ("Sätze", "Öffentliche Listenpreise ab 100 kVA gibt es in CH/DE/AT nicht (nur auf Anfrage). Genutzt werden US-Richtwerte, umgerechnet 0,828 CHF/USD (24.09.2026)."),
    ("", "Diese Werte sind Grössenordnung, keine Offertenbasis. MiT-Sätze in «Annahmen» Spalte E eintragen."),
    ("Anteil 2027", "Welcher Teil des Volumens ins Kalenderjahr 2027 fällt (Bau- bzw. Eventtermine aus den Quellen)."),
    ("Pakete", "Events und alpine Solar-Baustellen sind einzeln meist unter CHF 50'000. Sie sind zu Paketen gebündelt; ein Paket steht in «Top-Player», "),
    ("", "wenn es über CHF 50'000 liegt. Paketwerte rechnen per Formel aus den Blättern «Events 2027» und «EVU & Energie 2027»."),
    ("Erweiterung", "29.09.2026: 56 Events und 47 EVU-/Energieprojekte ergänzt (Websuche, Quellen je Zeile)."),
    ("Wahrscheinlichkeit", "Chance, dass MiT den Auftrag gewinnt: 10 % (EMEA-Beschaffung, unsicherer Zeitplan) bis 30 % (konkreter Anlass, Region nah)."),
    ("Commissioning", "Integrated Systems Test (Level 5): Last ≈ Design-IT-Last, Stufen 25/50/75/100 %, IST-Fenster 4-6 Wochen (anvilfield.com, sunbeltsolomon.com)."),
    ("Netzengpass", "EKZ: über 100 Anschlussanfragen von RZ, 6 von 9 neuen Unterwerken entstehen für RZ, Engpass im Vornetz Axpo/Swissgrid (ekz.ch, 2025)."),
    ("Nicht enthalten", "Trafo-Miete, Transport, Montage, Service, Treibstoff: Potenzial ist bewusst konservativ."),
    ("Kundenstatus", "MiT-Status (Bestand, verloren, Aufbau) ist nicht öffentlich: Spalte «Status MiT (CRM)» aus dem CRM füllen."),
    ("Vertraulich", "Interne Arbeitsliste. Keine Weitergabe an Kunden."),
]
for i, (k, t) in enumerate(txt):
    me.cell(4 + i, 1, k).font = font(bold=True, color=RED)
    me.cell(4 + i, 2, t).font = font()
me.column_dimensions["A"].width, me.column_dimensions["B"].width = 20, 140

st.sheet_properties.tabColor = RED
tp.sheet_properties.tabColor = RED
an.sheet_properties.tabColor = "FFC000"
wb.save(OUT)
print(OUT, len(rows))
