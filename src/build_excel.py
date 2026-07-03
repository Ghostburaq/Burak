"""
AVIA VOLT — Vertriebs-Cockpit Generator (Burak Ücöz)

Baut eine voll ausgestattete Excel-Arbeitsmappe für den Vertrieb:
Dashboard mit KPIs & Diagrammen, filterbare Pipeline-Tabelle mit Formeln,
Dropdowns (Datenvalidierung), Ampel-Regeln (bedingte Formatierung),
sowie ein "Live-Daten"-Blatt mit Online-Abruf per Knopfdruck.

100% deterministisch, keine Netzwerkzugriffe beim Bauen.

Run:  pip install openpyxl && python3 src/build_excel.py
Out:  Vertriebs_Cockpit_AVIA_VOLT.xlsx
      data/Live_CHF_Kurse.iqy          (Online-Abruf per Doppelklick/Knopf)
      data/PowerQuery_Vorlagen.m        (M-Code für eigene SQL-/Cloud-DB)
"""
from __future__ import annotations

import os
from datetime import date, timedelta

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, IconSetRule
from openpyxl.styles import (Alignment, Border, Font, PatternFill, Side)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Vertriebs_Cockpit_AVIA_VOLT.xlsx")
DATA = os.path.join(ROOT, "data")

# ---- Design-System (an AVIA VOLT angelehnt) -----------------------------
NAVY = "1B2430"
NAVY_SOFT = "2A3543"
RED = "E2001A"
RED_DK = "B30015"
WHITE = "FFFFFF"
PAPER = "F5F7F9"
CARD = "FFFFFF"
MUTE = "5A6573"
LINE = "E3E8ED"
GREEN = "1E9E5A"
AMBER = "E8A400"
GREY_ROW = "F2F5F8"

FONT = "Calibri"
HEAD_FONT = "Calibri"

thin = Side(style="thin", color=LINE)
med = Side(style="medium", color=NAVY)
box = Border(left=thin, right=thin, top=thin, bottom=thin)


def fill(hex_):
    return PatternFill("solid", fgColor=hex_)


def font(size=11, bold=False, color="1B2430", name=FONT, italic=False):
    return Font(name=name, size=size, bold=bold, color=color, italic=italic)


CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")

# ---------------------------------------------------------------------------
# Stammdaten für Dropdowns / Lookups
# ---------------------------------------------------------------------------
PHASEN = [
    ("Lead", 0.10),
    ("Qualifiziert", 0.25),
    ("Angebot", 0.50),
    ("Verhandlung", 0.75),
    ("Gewonnen", 1.00),
    ("Verloren", 0.00),
]
PRIOS = ["Hoch", "Mittel", "Niedrig"]
REGIONEN = ["Zürich", "Bern", "Waadt", "Genf", "Basel", "Aargau",
            "St. Gallen", "Tessin", "Luzern", "Wallis"]
BRANCHEN = ["Detailhandel", "Logistik", "Immobilien", "Hotellerie",
            "Öffentliche Hand", "Industrie", "Tankstellen", "Flottenbetrieb"]
PRODUKTE = ["AC-Ladestation 22 kW", "DC-Schnelllader 60 kW",
            "DC-HPC 150 kW", "Lastmanagement-System", "Full-Service Betrieb",
            "PV + Speicher Kombi"]
TEAM = ["Burak Ücöz", "S. Meier", "L. Rossi", "N. Keller", "A. Favre"]

# ---------------------------------------------------------------------------
# Beispiel-Pipeline (realistische CH-B2B-Deals, deterministisch)
# ---------------------------------------------------------------------------
T0 = date(2026, 7, 3)


def d(offset_days):
    return T0 + timedelta(days=offset_days)


# Firma, Ansprechpartner, Region, Branche, Produkt, Phase, Prio, Volumen, Erstkontakt, Erw.Abschluss, Verantwortlich, Nächster Schritt
DEALS = [
    ("Migros Ostschweiz", "R. Brunner", "St. Gallen", "Detailhandel", "DC-HPC 150 kW", "Verhandlung", "Hoch", 340000, d(-52), d(24), "Burak Ücöz", "Vertrag final abstimmen"),
    ("Planzer Transport", "M. Planzer", "Zürich", "Logistik", "Lastmanagement-System", "Angebot", "Hoch", 210000, d(-31), d(38), "Burak Ücöz", "Angebot nachfassen"),
    ("SBB Immobilien", "C. Wyss", "Bern", "Immobilien", "DC-Schnelllader 60 kW", "Qualifiziert", "Hoch", 480000, d(-18), d(75), "S. Meier", "Standort-Audit terminieren"),
    ("Coop Mineraloel", "T. Frei", "Aargau", "Tankstellen", "DC-HPC 150 kW", "Verhandlung", "Hoch", 620000, d(-64), d(15), "Burak Ücöz", "Preisstaffel bestätigen"),
    ("Hotel Belvédère", "G. Rossi", "Wallis", "Hotellerie", "AC-Ladestation 22 kW", "Angebot", "Mittel", 48000, d(-22), d(30), "L. Rossi", "Referenzbesuch anbieten"),
    ("Stadt Zürich TAZ", "P. Huber", "Zürich", "Öffentliche Hand", "Full-Service Betrieb", "Qualifiziert", "Hoch", 390000, d(-40), d(90), "N. Keller", "Ausschreibungsunterlagen prüfen"),
    ("Emmi Gruppe", "D. Schmid", "Luzern", "Industrie", "PV + Speicher Kombi", "Lead", "Mittel", 275000, d(-6), d(120), "S. Meier", "Erstgespräch vereinbaren"),
    ("Groupe Mutuel", "J. Favre", "Waadt", "Immobilien", "AC-Ladestation 22 kW", "Angebot", "Mittel", 96000, d(-27), d(42), "A. Favre", "Angebot v2 senden"),
    ("Läderach", "S. Läderach", "Aargau", "Detailhandel", "AC-Ladestation 22 kW", "Gewonnen", "Mittel", 62000, d(-88), d(-4), "Burak Ücöz", "Umsetzung übergeben"),
    ("Post Fleet", "M. Berger", "Bern", "Flottenbetrieb", "Lastmanagement-System", "Verhandlung", "Hoch", 540000, d(-48), d(20), "Burak Ücöz", "Rahmenvertrag verhandeln"),
    ("TCS Genf", "F. Dubois", "Genf", "Öffentliche Hand", "DC-Schnelllader 60 kW", "Qualifiziert", "Mittel", 180000, d(-15), d(66), "A. Favre", "Bedarf konkretisieren"),
    ("IKEA Spreitenbach", "K. Nilsson", "Aargau", "Detailhandel", "DC-HPC 150 kW", "Angebot", "Hoch", 410000, d(-33), d(35), "S. Meier", "Business-Case rechnen"),
    ("Manor AG", "B. Keller", "Basel", "Detailhandel", "DC-Schnelllader 60 kW", "Lead", "Niedrig", 150000, d(-4), d(110), "L. Rossi", "Entscheider identifizieren"),
    ("Kambly SA", "E. Kambly", "Bern", "Industrie", "PV + Speicher Kombi", "Verloren", "Niedrig", 88000, d(-70), d(-10), "N. Keller", "Verloren an Wettbewerb"),
    ("Autogrill Schweiz", "R. Conti", "Tessin", "Tankstellen", "DC-HPC 150 kW", "Angebot", "Hoch", 355000, d(-25), d(28), "Burak Ücöz", "Termin CFO fixieren"),
    ("Bucherer", "V. Huber", "Luzern", "Detailhandel", "AC-Ladestation 22 kW", "Gewonnen", "Mittel", 54000, d(-95), d(-20), "L. Rossi", "Umsetzung läuft"),
    ("Denner AG", "H. Müller", "Zürich", "Detailhandel", "Lastmanagement-System", "Qualifiziert", "Mittel", 230000, d(-12), d(70), "S. Meier", "Standortliste anfordern"),
    ("Flughafen Genf", "P. Girard", "Genf", "Öffentliche Hand", "DC-HPC 150 kW", "Verhandlung", "Hoch", 780000, d(-58), d(18), "Burak Ücöz", "Vertragsentwurf senden"),
    ("Valora / avec", "N. Weber", "St. Gallen", "Detailhandel", "AC-Ladestation 22 kW", "Lead", "Niedrig", 72000, d(-3), d(100), "A. Favre", "Bedarf klären"),
    ("Aldi Suisse", "M. Fischer", "Aargau", "Detailhandel", "DC-Schnelllader 60 kW", "Angebot", "Hoch", 445000, d(-29), d(40), "Burak Ücöz", "Pilotstandort definieren"),
]

# ---------------------------------------------------------------------------
# Spalten der Pipeline
# ---------------------------------------------------------------------------
COLS = [
    ("Deal-ID", 9),
    ("Firma", 22),
    ("Ansprechpartner", 16),
    ("Region", 12),
    ("Branche", 15),
    ("Produkt / Lösung", 22),
    ("Phase", 14),
    ("Priorität", 11),
    ("Volumen (CHF)", 15),
    ("Wahrsch. %", 11),
    ("Gew. Wert (CHF)", 16),
    ("Erstkontakt", 13),
    ("Erw. Abschluss", 14),
    ("Tage bis Abschl.", 15),
    ("Verantwortlich", 15),
    ("Nächster Schritt", 26),
    ("Ampel", 8),
]
# Spalten-Buchstaben-Map
CL = {name: get_column_letter(i + 1) for i, (name, _) in enumerate(COLS)}


# ===========================================================================
def build():
    wb = Workbook()

    ws_dash = wb.active
    ws_dash.title = "Dashboard"
    ws_pipe = wb.create_sheet("Pipeline")
    ws_live = wb.create_sheet("Live-Daten")
    ws_list = wb.create_sheet("Listen")
    ws_help = wb.create_sheet("Anleitung")

    _build_listen(ws_list)
    n_rows = _build_pipeline(ws_pipe)
    _build_dashboard(ws_dash, n_rows)
    _build_live(ws_live)
    _build_help(ws_help)

    # Ansicht: Dashboard zuerst, Gitternetz aus wo sinnvoll
    wb.active = 0
    for ws in (ws_dash, ws_live, ws_help):
        ws.sheet_view.showGridLines = False

    wb.save(OUT)
    print(f"OK  {os.path.relpath(OUT, ROOT)}  ({n_rows} Deals)")


# ---------------------------------------------------------------------------
def _build_listen(ws):
    """Lookup-Tabellen für Dropdowns und XLOOKUP (Wahrscheinlichkeit)."""
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Stammdaten / Lookups"
    ws["A1"].font = font(13, bold=True, color=NAVY)
    ws["A2"] = "Diese Werte speisen die Dropdowns und die automatische Wahrscheinlichkeit."
    ws["A2"].font = font(9, italic=True, color=MUTE)

    # Phase -> Wahrscheinlichkeit (für XLOOKUP)
    ws["A4"] = "Phase"
    ws["B4"] = "Wahrsch."
    for c in ("A4", "B4"):
        ws[c].font = font(10, bold=True, color=WHITE)
        ws[c].fill = fill(NAVY)
        ws[c].alignment = CENTER
    for i, (name, p) in enumerate(PHASEN):
        ws.cell(5 + i, 1, name).border = box
        cell = ws.cell(5 + i, 2, p)
        cell.number_format = "0%"
        cell.border = box
        cell.alignment = CENTER
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 11

    # weitere Listen in Spalten D..I
    lists = [("D", "Prioritäten", PRIOS), ("E", "Regionen", REGIONEN),
             ("F", "Branchen", BRANCHEN), ("G", "Produkte", PRODUKTE),
             ("H", "Team", TEAM), ("I", "Phasen", [p[0] for p in PHASEN])]
    for col, title, vals in lists:
        ws[f"{col}4"] = title
        ws[f"{col}4"].font = font(10, bold=True, color=WHITE)
        ws[f"{col}4"].fill = fill(NAVY)
        ws[f"{col}4"].alignment = CENTER
        for i, v in enumerate(vals):
            cc = ws[f"{col}{5 + i}"]
            cc.value = v
            cc.border = box
        ws.column_dimensions[col].width = 16


# ---------------------------------------------------------------------------
def _build_pipeline(ws):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"

    # Titelzeile
    ws.merge_cells("A1:Q1")
    ws["A1"] = "VERTRIEBS-PIPELINE  ·  AVIA VOLT Suisse"
    ws["A1"].font = font(16, bold=True, color=WHITE)
    ws["A1"].fill = fill(NAVY)
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 30
    ws.merge_cells("A2:Q2")
    ws["A2"] = ("Tipp: Filtern über die Pfeile in der Kopfzeile · Phase/Priorität/Region per Dropdown · "
                "Wahrscheinlichkeit, gewichteter Wert, Tage bis Abschluss & Ampel rechnen automatisch.")
    ws["A2"].font = font(9, italic=True, color=MUTE)
    ws["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[2].height = 16

    header_row = 4
    first_data = header_row + 1

    # Kopfzeile
    for i, (name, width) in enumerate(COLS):
        c = ws.cell(header_row, i + 1, name)
        c.font = font(10, bold=True, color=WHITE)
        c.fill = fill(NAVY)
        c.alignment = CENTER
        c.border = Border(left=thin, right=thin, top=med, bottom=med)
        ws.column_dimensions[get_column_letter(i + 1)].width = width
    ws.row_dimensions[header_row].height = 26

    # Datenzeilen
    for r, deal in enumerate(DEALS):
        row = first_data + r
        (firma, ap, region, branche, produkt, phase, prio,
         vol, dk, da, verant, naechst) = deal
        deal_id = f"D-{1001 + r}"
        vals = {
            "Deal-ID": deal_id,
            "Firma": firma,
            "Ansprechpartner": ap,
            "Region": region,
            "Branche": branche,
            "Produkt / Lösung": produkt,
            "Phase": phase,
            "Priorität": prio,
            "Volumen (CHF)": vol,
            "Erstkontakt": dk,
            "Erw. Abschluss": da,
            "Verantwortlich": verant,
            "Nächster Schritt": naechst,
        }
        for name, _ in COLS:
            col = CL[name]
            cell = ws[f"{col}{row}"]
            if name in vals:
                cell.value = vals[name]
            cell.border = box
            cell.font = font(10)
            if r % 2 == 1:
                cell.fill = fill(GREY_ROW)

        # Formeln --------------------------------------------------------
        pcol, phcol, volcol, gwcol = CL["Phase"], CL["Wahrsch. %"], CL["Volumen (CHF)"], CL["Gew. Wert (CHF)"]
        dacol, tcol, ampcol = CL["Erw. Abschluss"], CL["Tage bis Abschl."], CL["Ampel"]

        # Wahrscheinlichkeit automatisch aus Phase (XLOOKUP -> Fallback VLOOKUP)
        ws[f"{phcol}{row}"] = (
            f'=IFERROR(XLOOKUP({pcol}{row},Listen!$A$5:$A$10,Listen!$B$5:$B$10),'
            f'VLOOKUP({pcol}{row},Listen!$A$5:$B$10,2,FALSE))'
        )
        ws[f"{phcol}{row}"].number_format = "0%"
        ws[f"{phcol}{row}"].alignment = CENTER

        # Gewichteter Wert
        ws[f"{gwcol}{row}"] = f"={volcol}{row}*{phcol}{row}"
        ws[f"{gwcol}{row}"].number_format = '#,##0'
        # Volumen Format
        ws[f"{volcol}{row}"].number_format = '#,##0'
        ws[f"{volcol}{row}"].alignment = RIGHT
        ws[f"{gwcol}{row}"].alignment = RIGHT

        # Datumsformate
        for dc in (CL["Erstkontakt"], CL["Erw. Abschluss"]):
            ws[f"{dc}{row}"].number_format = "DD.MM.YYYY"
            ws[f"{dc}{row}"].alignment = CENTER

        # Tage bis Abschluss (nur wenn nicht Gewonnen/Verloren)
        ws[f"{tcol}{row}"] = (
            f'=IF(OR({pcol}{row}="Gewonnen",{pcol}{row}="Verloren"),"—",{dacol}{row}-TODAY())'
        )
        ws[f"{tcol}{row}"].alignment = CENTER

        # Ampel (Emoji je nach Dringlichkeit/Phase)
        ws[f"{ampcol}{row}"] = (
            f'=IF({pcol}{row}="Gewonnen","✅",'
            f'IF({pcol}{row}="Verloren","⬛",'
            f'IF({tcol}{row}<=14,"🔴",'
            f'IF({tcol}{row}<=45,"🟡","🟢"))))'
        )
        ws[f"{ampcol}{row}"].alignment = CENTER
        ws[f"{ampcol}{row}"].font = font(12)

        ws.row_dimensions[row].height = 20

    last_data = first_data + len(DEALS) - 1

    # Als Excel-Tabelle (AutoFilter, sortierbar) -------------------------
    ref = f"A{header_row}:{CL['Ampel']}{last_data}"
    tbl = Table(displayName="Pipeline", ref=ref)
    tbl.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showRowStripes=False,
        showFirstColumn=False, showLastColumn=False, showColumnStripes=False)
    ws.add_table(tbl)

    # Datenvalidierung (Dropdowns) --------------------------------------
    def dv(formula, col):
        v = DataValidation(type="list", formula1=formula, allow_blank=True)
        v.error = "Bitte einen Wert aus der Liste wählen."
        v.errorTitle = "Ungültige Eingabe"
        v.prompt = "Aus Dropdown wählen"
        ws.add_data_validation(v)
        v.add(f"{col}{first_data}:{col}{last_data}")

    dv("=Listen!$I$5:$I$10", CL["Phase"])
    dv("=Listen!$D$5:$D$7", CL["Priorität"])
    dv("=Listen!$E$5:$E$14", CL["Region"])
    dv("=Listen!$F$5:$F$12", CL["Branche"])
    dv("=Listen!$G$5:$G$10", CL["Produkt / Lösung"])
    dv("=Listen!$H$5:$H$9", CL["Verantwortlich"])

    # Bedingte Formatierung ---------------------------------------------
    vol_range = f"{CL['Volumen (CHF)']}{first_data}:{CL['Volumen (CHF)']}{last_data}"
    ws.conditional_formatting.add(vol_range, ColorScaleRule(
        start_type="min", start_color="FDE7E9",
        mid_type="percentile", mid_value=50, mid_color="FBD5A5",
        end_type="max", end_color="C6E7D0"))

    prio_range = f"{CL['Priorität']}{first_data}:{CL['Priorität']}{last_data}"
    ws.conditional_formatting.add(prio_range, CellIsRule(
        operator="equal", formula=['"Hoch"'], fill=fill("FADBD8"),
        font=font(10, bold=True, color=RED_DK)))

    phase_range = f"{CL['Phase']}{first_data}:{CL['Phase']}{last_data}"
    ws.conditional_formatting.add(phase_range, CellIsRule(
        operator="equal", formula=['"Gewonnen"'], fill=fill("D5F0DE"),
        font=font(10, bold=True, color=GREEN)))
    ws.conditional_formatting.add(phase_range, CellIsRule(
        operator="equal", formula=['"Verloren"'], fill=fill("EDEFF1"),
        font=font(10, color=MUTE)))

    # Summenzeile -------------------------------------------------------
    sr = last_data + 1
    ws[f"{CL['Firma']}{sr}"] = "Σ Summe / Forecast"
    ws[f"{CL['Firma']}{sr}"].font = font(11, bold=True, color=NAVY)
    for col in (CL["Volumen (CHF)"], CL["Gew. Wert (CHF)"]):
        c = ws[f"{col}{sr}"]
        c.value = f"=SUBTOTAL(109,{col}{first_data}:{col}{last_data})"
        c.number_format = '#,##0 "CHF"'
        c.font = font(11, bold=True, color=NAVY)
        c.fill = fill("EEF2F5")
        c.alignment = RIGHT
        c.border = Border(top=med, bottom=med)
    ws.row_dimensions[sr].height = 22

    return len(DEALS)


# ---------------------------------------------------------------------------
def _build_dashboard(ws, n_rows):
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    for col in "BCDEFGH":
        ws.column_dimensions[col].width = 17

    # Kopf
    ws.merge_cells("B2:H2")
    ws["B2"] = "VERTRIEBS-COCKPIT"
    ws["B2"].font = font(22, bold=True, color=NAVY)
    ws.merge_cells("B3:H3")
    ws["B3"] = "AVIA VOLT Suisse  ·  Pipeline-Steuerung & Forecast  ·  Burak Ücöz"
    ws["B3"].font = font(11, color=RED, bold=True)
    ws.row_dimensions[2].height = 30

    fd, ld = 5, 5 + n_rows - 1  # Datenzeilen auf Pipeline
    P = "Pipeline!"
    vol = f"{P}{CL['Volumen (CHF)']}{fd}:{CL['Volumen (CHF)']}{ld}"
    gw = f"{P}{CL['Gew. Wert (CHF)']}{fd}:{CL['Gew. Wert (CHF)']}{ld}"
    ph = f"{P}{CL['Phase']}{fd}:{CL['Phase']}{ld}"
    verant = f"{P}{CL['Verantwortlich']}{fd}:{CL['Verantwortlich']}{ld}"

    # KPI-Kacheln -------------------------------------------------------
    kpis = [
        ("Pipeline gesamt", f"=SUM({vol})", '#,##0 "CHF"', NAVY),
        ("Gewichteter Forecast", f"=SUM({gw})", '#,##0 "CHF"', RED),
        ("Offene Deals", f'=COUNTIFS({ph},"<>Gewonnen",{ph},"<>Verloren")', '0', NAVY_SOFT),
        ("Gewonnen (YTD)", f'=SUMIFS({vol},{ph},"Gewonnen")', '#,##0 "CHF"', GREEN),
        ("Win-Rate", f'=IFERROR(COUNTIF({ph},"Gewonnen")/(COUNTIF({ph},"Gewonnen")+COUNTIF({ph},"Verloren")),0)', '0%', NAVY),
        ("Ø Deal-Größe", f"=IFERROR(AVERAGE({vol}),0)", '#,##0 "CHF"', NAVY_SOFT),
    ]
    r = 5
    positions = [("B", "C"), ("D", "E"), ("F", "G")]
    for idx, (label, formula, numfmt, color) in enumerate(kpis):
        rowbase = r + (idx // 3) * 4
        c0, c1 = positions[idx % 3]
        ws.merge_cells(f"{c0}{rowbase}:{c1}{rowbase}")
        ws[f"{c0}{rowbase}"] = label.upper()
        ws[f"{c0}{rowbase}"].font = font(9, bold=True, color=MUTE)
        ws[f"{c0}{rowbase}"].alignment = Alignment(horizontal="left", indent=1, vertical="center")
        ws.merge_cells(f"{c0}{rowbase + 1}:{c1}{rowbase + 1}")
        vcell = ws[f"{c0}{rowbase + 1}"]
        vcell.value = formula
        vcell.number_format = numfmt
        vcell.font = font(20, bold=True, color=color)
        vcell.alignment = Alignment(horizontal="left", indent=1, vertical="center")
        ws.row_dimensions[rowbase + 1].height = 30
        # Kachel-Rahmen
        for rr in (rowbase, rowbase + 1):
            for cc in (c0, c1):
                cur = ws[f"{cc}{rr}"]
                top = med if rr == rowbase else None
                bottom = med if rr == rowbase + 1 else None
                cur.fill = fill(CARD)
                cur.border = Border(
                    top=Side(style="thin", color=LINE) if rr == rowbase else None,
                    bottom=Side(style="thin", color=LINE) if rr == rowbase + 1 else None,
                    left=Side(style="thin", color=LINE) if cc == c0 else None,
                    right=Side(style="thin", color=LINE) if cc == c1 else None)

    # Aggregationstabelle Phase (für Diagramm) --------------------------
    agg_row = 15
    ws[f"B{agg_row}"] = "Pipeline nach Phase"
    ws[f"B{agg_row}"].font = font(12, bold=True, color=NAVY)
    ws[f"B{agg_row + 1}"] = "Phase"
    ws[f"C{agg_row + 1}"] = "Volumen (CHF)"
    for cc in ("B", "C"):
        ws[f"{cc}{agg_row + 1}"].font = font(10, bold=True, color=WHITE)
        ws[f"{cc}{agg_row + 1}"].fill = fill(NAVY)
        ws[f"{cc}{agg_row + 1}"].alignment = CENTER
    for i, (pname, _) in enumerate(PHASEN):
        rr = agg_row + 2 + i
        ws[f"B{rr}"] = pname
        ws[f"B{rr}"].border = box
        cc = ws[f"C{rr}"]
        cc.value = f'=SUMIFS({vol},{ph},B{rr})'
        cc.number_format = '#,##0'
        cc.border = box
        cc.alignment = RIGHT
    phase_last = agg_row + 1 + len(PHASEN)

    # Aggregation Verantwortlich ----------------------------------------
    t_row = agg_row
    ws[f"E{t_row}"] = "Gew. Forecast je Verantwortlich"
    ws[f"E{t_row}"].font = font(12, bold=True, color=NAVY)
    ws[f"E{t_row + 1}"] = "Verantwortlich"
    ws[f"F{t_row + 1}"] = "Gew. Wert (CHF)"
    for cc in ("E", "F"):
        ws[f"{cc}{t_row + 1}"].font = font(10, bold=True, color=WHITE)
        ws[f"{cc}{t_row + 1}"].fill = fill(NAVY)
        ws[f"{cc}{t_row + 1}"].alignment = CENTER
    for i, member in enumerate(TEAM):
        rr = t_row + 2 + i
        ws[f"E{rr}"] = member
        ws[f"E{rr}"].border = box
        cc = ws[f"F{rr}"]
        cc.value = f'=SUMIFS({gw},{verant},E{rr})'
        cc.number_format = '#,##0'
        cc.border = box
        cc.alignment = RIGHT
    team_last = t_row + 1 + len(TEAM)

    # Balkendiagramm Phase ----------------------------------------------
    bar = BarChart()
    bar.type = "col"
    bar.title = "Pipeline nach Phase (CHF)"
    bar.style = 10
    bar.height = 7.5
    bar.width = 13
    data = Reference(ws, min_col=3, min_row=agg_row + 1, max_row=phase_last)
    cats = Reference(ws, min_col=2, min_row=agg_row + 2, max_row=phase_last)
    bar.add_data(data, titles_from_data=True)
    bar.set_categories(cats)
    bar.legend = None
    bar.dataLabels = DataLabelList()
    bar.dataLabels.showVal = True
    ws.add_chart(bar, f"B{phase_last + 3}")

    # Balkendiagramm Verantwortlich -------------------------------------
    bar2 = BarChart()
    bar2.type = "bar"
    bar2.title = "Gew. Forecast je Verantwortlich (CHF)"
    bar2.style = 12
    bar2.height = 7.5
    bar2.width = 13
    data2 = Reference(ws, min_col=6, min_row=t_row + 1, max_row=team_last)
    cats2 = Reference(ws, min_col=5, min_row=t_row + 2, max_row=team_last)
    bar2.add_data(data2, titles_from_data=True)
    bar2.set_categories(cats2)
    bar2.legend = None
    ws.add_chart(bar2, f"E{team_last + 3}")

    # Hinweis auf Live-Daten --------------------------------------------
    note_r = 4
    ws.merge_cells(f"B{note_r}:H{note_r}")


# ---------------------------------------------------------------------------
def _build_live(ws):
    ws.sheet_view.showGridLines = False
    for col, w in (("A", 2), ("B", 20), ("C", 16), ("D", 16), ("E", 16), ("F", 30)):
        ws.column_dimensions[col].width = w

    ws.merge_cells("B2:F2")
    ws["B2"] = "LIVE-DATEN  ·  Online-Abruf per Knopfdruck"
    ws["B2"].font = font(18, bold=True, color=NAVY)
    ws.merge_cells("B3:F3")
    ws["B3"] = ("Aktuelle CHF-Wechselkurse & frei konfigurierbare Datenbank-Anbindung. "
                "Aktualisieren mit  Daten ▸ Alle aktualisieren  (Strg+Alt+F5).")
    ws["B3"].font = font(10, italic=True, color=MUTE)

    # "Button"-Optik ----------------------------------------------------
    ws.merge_cells("B5:D5")
    btn = ws["B5"]
    btn.value = "🔄  LIVE-DATEN JETZT AKTUALISIEREN"
    btn.font = font(12, bold=True, color=WHITE)
    btn.fill = fill(RED)
    btn.alignment = CENTER
    ws.row_dimensions[5].height = 30
    for cc in ("B5", "C5", "D5"):
        ws[cc].fill = fill(RED)
    ws.merge_cells("E5:F5")
    ws["E5"] = "→  Menüband: Daten ▸ Alle aktualisieren  ·  oder Strg+Alt+F5"
    ws["E5"].font = font(9, italic=True, color=MUTE)
    ws["E5"].alignment = LEFT

    # Vorlage-Tabelle für die abgerufenen Kurse -------------------------
    ws["B7"] = "Referenzwährung"
    ws["C7"] = "CHF"
    ws["B7"].font = font(10, bold=True, color=NAVY)
    headers = ["Währung", "Kurs (1 CHF =)", "Stand", "Quelle"]
    for i, h in enumerate(headers):
        c = ws.cell(9, 2 + i, h)
        c.font = font(10, bold=True, color=WHITE)
        c.fill = fill(NAVY)
        c.alignment = CENTER
        c.border = box
    seed = [("EUR", "", "", "frankfurter.app"),
            ("USD", "", "", "frankfurter.app"),
            ("GBP", "", "", "frankfurter.app")]
    for r, row in enumerate(seed):
        for i, v in enumerate(row):
            c = ws.cell(10 + r, 2 + i, v)
            c.border = box
            c.alignment = CENTER if i != 3 else LEFT
    ws["B14"] = ("Hinweis: Diese Tabelle füllt sich nach dem ersten Einrichten der Web-Abfrage automatisch. "
                 "Schritt-für-Schritt in Blatt „Anleitung“.")
    ws["B14"].font = font(9, italic=True, color=MUTE)
    ws.merge_cells("B14:F15")
    ws["B14"].alignment = LEFT

    # Platz für eigene Datenbank ----------------------------------------
    ws["B17"] = "Eigene Datenbank (SQL / Cloud) anbinden"
    ws["B17"].font = font(12, bold=True, color=NAVY)
    ws["B18"] = ("Power Query ▸ Daten abrufen ▸ Aus Datenbank (SQL Server / MySQL / PostgreSQL) "
                 "oder ▸ Aus dem Web / SharePoint / Google Sheets. Fertige M-Vorlagen in data/PowerQuery_Vorlagen.m.")
    ws.merge_cells("B18:F20")
    ws["B18"].font = font(9, color=MUTE)
    ws["B18"].alignment = LEFT


# ---------------------------------------------------------------------------
def _build_help(ws):
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 100

    lines = [
        ("So arbeitest du perfekt mit diesem Cockpit", 16, True, NAVY),
        ("", 6, False, MUTE),
        ("1 · Dashboard", 12, True, RED),
        ("KPIs (Pipeline, gewichteter Forecast, Win-Rate …) und Diagramme rechnen automatisch.", 10, False, "1B2430"),
        ("Alles aktualisiert sich, sobald du in der Pipeline etwas änderst.", 10, False, "1B2430"),
        ("", 6, False, MUTE),
        ("2 · Pipeline (Herzstück)", 12, True, RED),
        ("• Filtern: Pfeile in der blauen Kopfzeile → nach Region, Phase, Verantwortlich … filtern & sortieren.", 10, False, "1B2430"),
        ("• Dropdowns: Phase, Priorität, Region, Branche, Produkt, Verantwortlich – nur gültige Werte.", 10, False, "1B2430"),
        ("• Automatik: Wahrscheinlichkeit folgt der Phase; Gew. Wert = Volumen × Wahrsch.;", 10, False, "1B2430"),
        ("  Tage bis Abschluss & Ampel (🔴≤14 T, 🟡≤45 T, 🟢 sonst) rechnen selbst.", 10, False, "1B2430"),
        ("• Neue Zeile: einfach unter der letzten Zeile weiterschreiben – die Tabelle wächst automatisch mit.", 10, False, "1B2430"),
        ("", 6, False, MUTE),
        ("3 · Live-Daten online abrufen (per Knopfdruck)", 12, True, RED),
        ("Einmal einrichten – danach genügt „Alle aktualisieren“ (Strg+Alt+F5):", 10, False, "1B2430"),
        ("  a) Daten ▸ Daten abrufen ▸ Aus Datei ▸ Web-Abfrage (.iqy)  →  data/Live_CHF_Kurse.iqy wählen.", 10, False, "1B2430"),
        ("     (oder Doppelklick auf die .iqy-Datei – Excel öffnet die Abfrage direkt.)", 10, False, "1B2430"),
        ("  b) Zielbereich = Blatt „Live-Daten“, Zelle B10.  Fertig.", 10, False, "1B2430"),
        ("  c) Eigene Datenbank: Daten ▸ Aus Datenbank (SQL/MySQL/PostgreSQL) oder Aus dem Web –", 10, False, "1B2430"),
        ("     M-Code-Vorlagen liegen in data/PowerQuery_Vorlagen.m (Server/Zugangsdaten eintragen).", 10, False, "1B2430"),
        ("", 6, False, MUTE),
        ("4 · Automatisch aktualisieren", 12, True, RED),
        ("Rechtsklick auf die Abfrage ▸ Eigenschaften ▸ „Aktualisieren beim Öffnen“ / alle X Minuten.", 10, False, "1B2430"),
        ("", 6, False, MUTE),
        ("Farbwelt: AVIA-Navy #1B2430 + AVIA-Rot #E2001A. Reproduzierbar via  python3 src/build_excel.py.", 9, False, MUTE),
    ]
    r = 2
    for text, size, bold, color in lines:
        ws.cell(r, 2, text).font = font(size, bold=bold, color=color)
        ws.cell(r, 2).alignment = LEFT
        r += 1


# ===========================================================================
def write_companions():
    """Begleitdateien für den Online-Abruf."""
    os.makedirs(DATA, exist_ok=True)

    # Web-Abfrage (.iqy): CHF-Kurse als CSV von frankfurter.app
    iqy = (
        "WEB\r\n1\r\n"
        "https://api.frankfurter.app/latest?from=CHF&to=EUR,USD,GBP\r\n"
        "\r\nSelection=EntirePage\r\nFormatting=None\r\n"
        "PreFormattedTextToColumns=True\r\nConsecutiveDelimitersAsOne=True\r\n"
        "SingleBlockTextImport=False\r\nDisableDateRecognition=False\r\n"
        "DisableRedirections=False\r\n"
    )
    with open(os.path.join(DATA, "Live_CHF_Kurse.iqy"), "w", newline="") as f:
        f.write(iqy)

    # Power-Query-M-Vorlagen
    m = r'''// ============================================================
// Power-Query-Vorlagen für das Vertriebs-Cockpit
// Einfügen über:  Daten ▸ Daten abrufen ▸ Leere Abfrage ▸ Erweiterter Editor
// ============================================================

// --- 1) LIVE CHF-WECHSELKURSE (Web-API, ohne Zugangsdaten) ---------------
let
    Quelle   = Json.Document(Web.Contents("https://api.frankfurter.app/latest?from=CHF&to=EUR,USD,GBP")),
    Datum    = Quelle[date],
    Kurse    = Quelle[rates],
    AlsTab   = Record.ToTable(Kurse),
    Umbenannt= Table.RenameColumns(AlsTab, {{"Name","Waehrung"}, {"Value","Kurs"}}),
    MitDatum = Table.AddColumn(Umbenannt, "Stand", each Datum, type text)
in
    MitDatum

// --- 2) EIGENE SQL-DATENBANK (Server/DB anpassen) -----------------------
// let
//     Quelle = Sql.Database("SERVERNAME", "DATENBANK",
//                 [Query="SELECT firma, region, phase, volumen FROM deals"])
// in
//     Quelle

// --- 3) MySQL / PostgreSQL ----------------------------------------------
// MySQL:       Quelle = MySQL.Database("host:3306", "db")
// PostgreSQL:  Quelle = PostgreSQL.Database("host", "db")

// --- 4) GOOGLE SHEETS / SHAREPOINT (per Freigabe-CSV-Link) ---------------
// let
//     Quelle = Csv.Document(Web.Contents("https://.../export?format=csv"),
//                 [Delimiter=",", Encoding=65001]),
//     Kopf   = Table.PromoteHeaders(Quelle, [PromoteAllScalars=true])
// in
//     Kopf
'''
    with open(os.path.join(DATA, "PowerQuery_Vorlagen.m"), "w") as f:
        f.write(m)

    print("OK  data/Live_CHF_Kurse.iqy")
    print("OK  data/PowerQuery_Vorlagen.m")


if __name__ == "__main__":
    build()
    write_companions()
