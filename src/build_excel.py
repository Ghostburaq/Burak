"""
Vertriebs-Cockpit — Generator

Baut eine umfangreiche, sofort einsatzbereite Excel-Arbeitsmappe für den
Vertrieb (neutral, ohne Firmenbranding).
100% deterministisch, keine Netzwerkzugriffe beim Bauen.

Blätter:
  Dashboard   – KPIs, Funnel, Auswertungen nach Region/Branche, Diagramme
  Pipeline    – filterbare Deal-Tabelle mit Formeln, Dropdowns, Ampel
  Aktivitäten – Aufgaben/Termine mit Fälligkeits-Ampel
  Kontakte    – Firmen & Ansprechpartner (CRM)
  Forecast    – Monats-Forecast Soll/Ist + Diagramm
  Ziele       – Zielerreichung je Verantwortlicher
  Live-Daten  – Online-Abruf per F9 (WEBSERVICE/FILTERXML) + eigene DB
  Listen      – Stammdaten für Dropdowns / Lookups
  Anleitung   – Schritt-für-Schritt

Live-Daten (E-Mobilität/Energie): öffentliche Ladeinfrastruktur Schweiz live
über OpenChargeMap (WEBSERVICE+FILTERXML, Aktualisieren per Taste F9) plus
Power-Query-M-Vorlagen (OpenChargeMap, Handelsregister Zefix, eigene DB) in
data/PowerQuery_Vorlagen.m.

Run:  pip install openpyxl && python3 src/build_excel.py
Out:  Vertriebs_Cockpit.xlsx  +  data/*
"""
from __future__ import annotations

import os
from datetime import date, timedelta

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import (CellIsRule, ColorScaleRule, DataBarRule,
                                      FormulaRule, IconSetRule)
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Vertriebs_Cockpit.xlsx")
DATA = os.path.join(ROOT, "data")

# ---- Design-System (neutral) --------------------------------------------
NAVY, NAVY_SOFT = "1B2430", "2A3543"
RED, RED_DK = "E2001A", "B30015"
WHITE = "FFFFFF"
PAPER = "F5F7F9"
CARD = "FFFFFF"
MUTE = "5A6573"
LINE = "E3E8ED"
GREEN, AMBER = "1E9E5A", "E8A400"
GREY_ROW = "F3F6F9"
FONT = "Calibri"

thin = Side(style="thin", color=LINE)
med = Side(style="medium", color=NAVY)
box = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")
LOCKED = Protection(locked=True)
UNLOCKED = Protection(locked=False)


def fill(hex_):
    return PatternFill("solid", fgColor=hex_)


def font(size=11, bold=False, color=NAVY, name=FONT, italic=False):
    return Font(name=name, size=size, bold=bold, color=color, italic=italic)


def xl(fn_formula):
    """Neuere Funktionen brauchen das _xlfn.-Präfix im Dateiformat."""
    return fn_formula


# ---------------------------------------------------------------------------
# Stammdaten
# ---------------------------------------------------------------------------
PHASEN = [("Lead", 0.10), ("Qualifiziert", 0.25), ("Angebot", 0.50),
          ("Verhandlung", 0.75), ("Gewonnen", 1.00), ("Verloren", 0.00)]
PHASENAMEN = [p for p, _ in PHASEN]
PRIOS = ["Hoch", "Mittel", "Niedrig"]
REGIONEN = ["Zürich", "Bern", "Waadt", "Genf", "Basel", "Aargau",
            "St. Gallen", "Tessin", "Luzern", "Wallis"]
BRANCHEN = ["Detailhandel", "Logistik", "Immobilien", "Hotellerie",
            "Öffentliche Hand", "Industrie", "Tankstellen", "Flottenbetrieb"]
PRODUKTE = ["AC-Ladestation 22 kW", "DC-Schnelllader 60 kW", "DC-HPC 150 kW",
            "Lastmanagement-System", "Full-Service Betrieb", "PV + Speicher Kombi"]
TEAM = ["Burak Ücöz", "S. Meier", "L. Rossi", "N. Keller", "A. Favre"]
AKTIV_TYP = ["Anruf", "E-Mail", "Termin vor Ort", "Web-Demo", "Angebot", "Follow-up"]

T0 = date(2026, 7, 3)


def d(off):
    return T0 + timedelta(days=off)


# Basis-Deals (handverlesen, realistisch) --------------------------------
BASE_DEALS = [
    ("Migros Ostschweiz", "R. Brunner", "St. Gallen", "Detailhandel", "DC-HPC 150 kW", "Verhandlung", "Hoch", 340000, -52, 24, "Burak Ücöz", "Vertrag final abstimmen"),
    ("Planzer Transport", "M. Planzer", "Zürich", "Logistik", "Lastmanagement-System", "Angebot", "Hoch", 210000, -31, 38, "Burak Ücöz", "Angebot nachfassen"),
    ("SBB Immobilien", "C. Wyss", "Bern", "Immobilien", "DC-Schnelllader 60 kW", "Qualifiziert", "Hoch", 480000, -18, 75, "S. Meier", "Standort-Audit terminieren"),
    ("Coop Mineraloel", "T. Frei", "Aargau", "Tankstellen", "DC-HPC 150 kW", "Verhandlung", "Hoch", 620000, -64, 15, "Burak Ücöz", "Preisstaffel bestätigen"),
    ("Hotel Belvédère", "G. Rossi", "Wallis", "Hotellerie", "AC-Ladestation 22 kW", "Angebot", "Mittel", 48000, -22, 30, "L. Rossi", "Referenzbesuch anbieten"),
    ("Stadt Zürich TAZ", "P. Huber", "Zürich", "Öffentliche Hand", "Full-Service Betrieb", "Qualifiziert", "Hoch", 390000, -40, 90, "N. Keller", "Ausschreibung prüfen"),
    ("Emmi Gruppe", "D. Schmid", "Luzern", "Industrie", "PV + Speicher Kombi", "Lead", "Mittel", 275000, -6, 120, "S. Meier", "Erstgespräch vereinbaren"),
    ("Groupe Mutuel", "J. Favre", "Waadt", "Immobilien", "AC-Ladestation 22 kW", "Angebot", "Mittel", 96000, -27, 42, "A. Favre", "Angebot v2 senden"),
    ("Läderach", "S. Läderach", "Aargau", "Detailhandel", "AC-Ladestation 22 kW", "Gewonnen", "Mittel", 62000, -88, -4, "Burak Ücöz", "Umsetzung übergeben"),
    ("Post Fleet", "M. Berger", "Bern", "Flottenbetrieb", "Lastmanagement-System", "Verhandlung", "Hoch", 540000, -48, 20, "Burak Ücöz", "Rahmenvertrag verhandeln"),
    ("TCS Genf", "F. Dubois", "Genf", "Öffentliche Hand", "DC-Schnelllader 60 kW", "Qualifiziert", "Mittel", 180000, -15, 66, "A. Favre", "Bedarf konkretisieren"),
    ("IKEA Spreitenbach", "K. Nilsson", "Aargau", "Detailhandel", "DC-HPC 150 kW", "Angebot", "Hoch", 410000, -33, 35, "S. Meier", "Business-Case rechnen"),
    ("Manor AG", "B. Keller", "Basel", "Detailhandel", "DC-Schnelllader 60 kW", "Lead", "Niedrig", 150000, -4, 110, "L. Rossi", "Entscheider identifizieren"),
    ("Kambly SA", "E. Kambly", "Bern", "Industrie", "PV + Speicher Kombi", "Verloren", "Niedrig", 88000, -70, -10, "N. Keller", "Verloren an Wettbewerb"),
    ("Autogrill Schweiz", "R. Conti", "Tessin", "Tankstellen", "DC-HPC 150 kW", "Angebot", "Hoch", 355000, -25, 28, "Burak Ücöz", "Termin CFO fixieren"),
    ("Bucherer", "V. Huber", "Luzern", "Detailhandel", "AC-Ladestation 22 kW", "Gewonnen", "Mittel", 54000, -95, -20, "L. Rossi", "Umsetzung läuft"),
    ("Denner AG", "H. Müller", "Zürich", "Detailhandel", "Lastmanagement-System", "Qualifiziert", "Mittel", 230000, -12, 70, "S. Meier", "Standortliste anfordern"),
    ("Flughafen Genf", "P. Girard", "Genf", "Öffentliche Hand", "DC-HPC 150 kW", "Verhandlung", "Hoch", 780000, -58, 18, "Burak Ücöz", "Vertragsentwurf senden"),
    ("Valora / avec", "N. Weber", "St. Gallen", "Detailhandel", "AC-Ladestation 22 kW", "Lead", "Niedrig", 72000, -3, 100, "A. Favre", "Bedarf klären"),
    ("Aldi Suisse", "M. Fischer", "Aargau", "Detailhandel", "DC-Schnelllader 60 kW", "Angebot", "Hoch", 445000, -29, 40, "Burak Ücöz", "Pilotstandort definieren"),
]

# Weitere Firmen für zusätzliche, deterministisch erzeugte Deals ----------
MORE_FIRMEN = [
    ("Lidl Schweiz", "T. Wagner"), ("Galenica", "S. Baumann"), ("Swisscom Immobilien", "R. Meier"),
    ("Kuoni Reisen", "L. Steiner"), ("Hilti AG", "M. Anliker"), ("Geberit", "D. Frei"),
    ("Ricola", "P. Richterich"), ("Victorinox", "C. Elsener"), ("Stadler Rail", "F. Ahlburg"),
    ("Mobility Carsharing", "A. Suter"), ("Migrol AG", "B. Lehmann"), ("Tamoil", "N. Rossi"),
    ("Hotel Bellevue Bern", "G. Wyss"), ("Kongresshaus Zürich", "V. Keller"), ("Universität Basel", "H. Roth"),
    ("Kantonsspital Aarau", "E. Bosshard"), ("Feldschlösschen", "R. Amrein"), ("Bell Food Group", "S. Zünd"),
    ("Zweifel Pomy-Chips", "M. Zweifel"), ("Maerki Baumann", "L. Baumann"), ("EWZ", "P. Graf"),
    ("SIG Group", "D. Meister"),
]


def build_all_deals():
    deals = []
    for row in BASE_DEALS:
        (f, ap, reg, br, prod, ph, prio, vol, dk, da, verant, nx) = row
        deals.append(dict(firma=f, ap=ap, region=reg, branche=br, produkt=prod,
                          phase=ph, prio=prio, vol=vol, dk=d(dk), da=d(da),
                          verant=verant, nx=nx))
    # deterministisch erweitern
    for i, (f, ap) in enumerate(MORE_FIRMEN):
        prod = PRODUKTE[(i * 5) % len(PRODUKTE)]
        reg = REGIONEN[(i * 3 + 1) % len(REGIONEN)]
        br = BRANCHEN[(i * 7) % len(BRANCHEN)]
        phase = PHASENAMEN[(i * 2 + 1) % 5]              # 0..4, kein "Verloren" per Default
        if i % 9 == 4:
            phase = "Verloren"
        prio = PRIOS[(i) % 3]
        vol = 40000 + ((i * 37) % 60) * 8000             # 40k..512k, deterministisch
        dk = d(-(8 + (i * 11) % 90))
        da = d(((i * 13) % 120) - 15)
        nx = ["Erstgespräch planen", "Angebot erstellen", "Nachfassen",
              "Standort prüfen", "Entscheider treffen", "Abschluss vorbereiten"][(i) % 6]
        deals.append(dict(firma=f, ap=ap, region=reg, branche=br, produkt=prod,
                          phase=phase, prio=prio, vol=vol, dk=dk, da=da,
                          verant=TEAM[i % len(TEAM)], nx=nx))
    return deals


DEALS = build_all_deals()

# ---------------------------------------------------------------------------
# Pipeline-Spalten
# ---------------------------------------------------------------------------
COLS = [
    ("Deal-ID", 9), ("Firma", 22), ("Ansprechpartner", 16), ("Region", 12),
    ("Branche", 15), ("Produkt / Lösung", 22), ("Phase", 14), ("Priorität", 11),
    ("Volumen (CHF)", 15), ("Wahrsch. %", 11), ("Gew. Wert (CHF)", 16),
    ("Erstkontakt", 13), ("Erw. Abschluss", 14), ("Tage bis Abschl.", 15),
    ("Verantwortlich", 15), ("Nächster Schritt", 26), ("Ampel", 8),
]
CL = {name: get_column_letter(i + 1) for i, (name, _) in enumerate(COLS)}
FD = 5  # erste Datenzeile Pipeline
LD = FD + len(DEALS) - 1


# ===========================================================================
def build():
    wb = Workbook()
    ws_dash = wb.active
    ws_dash.title = "Dashboard"
    ws_pipe = wb.create_sheet("Pipeline")
    ws_akt = wb.create_sheet("Aktivitäten")
    ws_kont = wb.create_sheet("Kontakte")
    ws_fc = wb.create_sheet("Forecast")
    ws_ziel = wb.create_sheet("Ziele")
    ws_live = wb.create_sheet("Live-Daten")
    ws_list = wb.create_sheet("Listen")
    ws_help = wb.create_sheet("Anleitung")

    _listen(ws_list)
    _pipeline(ws_pipe)
    _aktivitaeten(ws_akt)
    _kontakte(ws_kont)
    _forecast(ws_fc)
    _ziele(ws_ziel)
    _dashboard(ws_dash)
    _live(ws_live)
    _help(ws_help)

    for ws in (ws_dash, ws_live, ws_help, ws_fc, ws_ziel):
        ws.sheet_view.showGridLines = False
    wb.active = 0

    _print_setup(wb)
    wb.save(OUT)
    print(f"OK  {os.path.relpath(OUT, ROOT)}  ({len(DEALS)} Deals, {len(wb.sheetnames)} Blätter)")


# ---------------------------------------------------------------------------
def _header(ws, cell, text, span_last, sub=None):
    col0 = cell[0]
    ws.merge_cells(f"{col0}1:{span_last}1")
    ws[f"{col0}1"] = text
    ws[f"{col0}1"].font = font(16, bold=True, color=WHITE)
    ws[f"{col0}1"].fill = fill(NAVY)
    ws[f"{col0}1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 30
    if sub:
        ws.merge_cells(f"{col0}2:{span_last}2")
        ws[f"{col0}2"] = sub
        ws[f"{col0}2"].font = font(9, italic=True, color=MUTE)
        ws[f"{col0}2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)


def _thead(ws, row, names, start_col=1, widths=None):
    for i, name in enumerate(names):
        c = ws.cell(row, start_col + i, name)
        c.font = font(10, bold=True, color=WHITE)
        c.fill = fill(NAVY)
        c.alignment = CENTER
        c.border = Border(left=thin, right=thin, top=med, bottom=med)
        if widths:
            ws.column_dimensions[get_column_letter(start_col + i)].width = widths[i]
    ws.row_dimensions[row].height = 24


# ---------------------------------------------------------------------------
def _listen(ws):
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Stammdaten / Lookups"
    ws["A1"].font = font(13, bold=True, color=NAVY)
    ws["A2"] = "Speist Dropdowns & automatische Wahrscheinlichkeit. Werte hier pflegen."
    ws["A2"].font = font(9, italic=True, color=MUTE)

    ws["A4"], ws["B4"] = "Phase", "Wahrsch."
    for c in ("A4", "B4"):
        ws[c].font = font(10, bold=True, color=WHITE)
        ws[c].fill = fill(NAVY)
        ws[c].alignment = CENTER
    for i, (name, p) in enumerate(PHASEN):
        ws.cell(5 + i, 1, name).border = box
        cc = ws.cell(5 + i, 2, p)
        cc.number_format = "0%"
        cc.border = box
        cc.alignment = CENTER
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 11

    lists = [("D", "Prioritäten", PRIOS), ("E", "Regionen", REGIONEN),
             ("F", "Branchen", BRANCHEN), ("G", "Produkte", PRODUKTE),
             ("H", "Team", TEAM), ("I", "Phasen", PHASENAMEN),
             ("J", "Aktivitätstyp", AKTIV_TYP), ("K", "Status", ["Offen", "Erledigt"])]
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
def _pipeline(ws):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"
    _header(ws, "A", "VERTRIEBS-PIPELINE", CL["Ampel"],
            sub="Filtern über die Kopfzeilen-Pfeile · Dropdowns für Phase/Priorität/Region/… · "
                "Wahrscheinlichkeit, gew. Wert, Tage bis Abschluss & Ampel rechnen automatisch.")
    hr = 4
    for i, (name, width) in enumerate(COLS):
        c = ws.cell(hr, i + 1, name)
        c.font = font(10, bold=True, color=WHITE)
        c.fill = fill(NAVY)
        c.alignment = CENTER
        c.border = Border(left=thin, right=thin, top=med, bottom=med)
        ws.column_dimensions[get_column_letter(i + 1)].width = width
    ws.row_dimensions[hr].height = 26

    pcol, phcol = CL["Phase"], CL["Wahrsch. %"]
    volcol, gwcol = CL["Volumen (CHF)"], CL["Gew. Wert (CHF)"]
    dacol, tcol, ampcol = CL["Erw. Abschluss"], CL["Tage bis Abschl."], CL["Ampel"]

    for r, deal in enumerate(DEALS):
        row = FD + r
        vals = {
            "Deal-ID": f"D-{1001 + r}", "Firma": deal["firma"],
            "Ansprechpartner": deal["ap"], "Region": deal["region"],
            "Branche": deal["branche"], "Produkt / Lösung": deal["produkt"],
            "Phase": deal["phase"], "Priorität": deal["prio"],
            "Volumen (CHF)": deal["vol"], "Erstkontakt": deal["dk"],
            "Erw. Abschluss": deal["da"], "Verantwortlich": deal["verant"],
            "Nächster Schritt": deal["nx"],
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
            # Eingabespalten entsperren, Formeln gesperrt lassen
            if name in ("Wahrsch. %", "Gew. Wert (CHF)", "Tage bis Abschl.", "Ampel", "Deal-ID"):
                cell.protection = LOCKED
            else:
                cell.protection = UNLOCKED

        ws[f"{phcol}{row}"] = (
            f'=IFERROR(_xlfn.XLOOKUP({pcol}{row},Listen!$A$5:$A$10,Listen!$B$5:$B$10),'
            f'VLOOKUP({pcol}{row},Listen!$A$5:$B$10,2,FALSE))')
        ws[f"{phcol}{row}"].number_format = "0%"
        ws[f"{phcol}{row}"].alignment = CENTER
        ws[f"{gwcol}{row}"] = f"={volcol}{row}*{phcol}{row}"
        ws[f"{gwcol}{row}"].number_format = '#,##0'
        ws[f"{gwcol}{row}"].alignment = RIGHT
        ws[f"{volcol}{row}"].number_format = '#,##0'
        ws[f"{volcol}{row}"].alignment = RIGHT
        for dc in (CL["Erstkontakt"], CL["Erw. Abschluss"]):
            ws[f"{dc}{row}"].number_format = "DD.MM.YYYY"
            ws[f"{dc}{row}"].alignment = CENTER
        ws[f"{tcol}{row}"] = (
            f'=IF(OR({pcol}{row}="Gewonnen",{pcol}{row}="Verloren"),"—",{dacol}{row}-TODAY())')
        ws[f"{tcol}{row}"].alignment = CENTER
        ws[f"{ampcol}{row}"] = (
            f'=IF({pcol}{row}="Gewonnen","✅",IF({pcol}{row}="Verloren","⬛",'
            f'IF({tcol}{row}<=14,"🔴",IF({tcol}{row}<=45,"🟡","🟢"))))')
        ws[f"{ampcol}{row}"].alignment = CENTER
        ws[f"{ampcol}{row}"].font = font(12)
        ws.row_dimensions[row].height = 20

    ref = f"A{hr}:{CL['Ampel']}{LD}"
    tbl = Table(displayName="Pipeline", ref=ref)
    tbl.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=False)
    ws.add_table(tbl)

    def dv(formula, col):
        v = DataValidation(type="list", formula1=formula, allow_blank=True)
        v.error, v.errorTitle = "Bitte aus der Liste wählen.", "Ungültige Eingabe"
        v.prompt = "Aus Dropdown wählen"
        ws.add_data_validation(v)
        v.add(f"{col}{FD}:{col}{LD}")

    dv("=Listen!$I$5:$I$10", CL["Phase"])
    dv("=Listen!$D$5:$D$7", CL["Priorität"])
    dv("=Listen!$E$5:$E$14", CL["Region"])
    dv("=Listen!$F$5:$F$12", CL["Branche"])
    dv("=Listen!$G$5:$G$10", CL["Produkt / Lösung"])
    dv("=Listen!$H$5:$H$9", CL["Verantwortlich"])

    vol_range = f"{volcol}{FD}:{volcol}{LD}"
    ws.conditional_formatting.add(vol_range, DataBarRule(
        start_type="min", end_type="max", color=RED, showValue=True))
    prio_range = f"{CL['Priorität']}{FD}:{CL['Priorität']}{LD}"
    ws.conditional_formatting.add(prio_range, CellIsRule(
        operator="equal", formula=['"Hoch"'], fill=fill("FADBD8"),
        font=font(10, bold=True, color=RED_DK)))
    phase_range = f"{pcol}{FD}:{pcol}{LD}"
    ws.conditional_formatting.add(phase_range, CellIsRule(
        operator="equal", formula=['"Gewonnen"'], fill=fill("D5F0DE"),
        font=font(10, bold=True, color=GREEN)))
    ws.conditional_formatting.add(phase_range, CellIsRule(
        operator="equal", formula=['"Verloren"'], fill=fill("EDEFF1"),
        font=font(10, color=MUTE)))

    sr = LD + 1
    ws[f"{CL['Firma']}{sr}"] = "Σ Summe / Forecast"
    ws[f"{CL['Firma']}{sr}"].font = font(11, bold=True, color=NAVY)
    for col in (volcol, gwcol):
        c = ws[f"{col}{sr}"]
        c.value = f"=SUBTOTAL(109,{col}{FD}:{col}{LD})"
        c.number_format = '#,##0 "CHF"'
        c.font = font(11, bold=True, color=NAVY)
        c.fill = fill("EEF2F5")
        c.alignment = RIGHT
        c.border = Border(top=med, bottom=med)
    ws.row_dimensions[sr].height = 22


# ---------------------------------------------------------------------------
def _aktivitaeten(ws):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"
    _header(ws, "A", "AKTIVITÄTEN & AUFGABEN", "H",
            sub="Fällige/überfällige Aufgaben werden farblich markiert. Status per Dropdown.")
    names = ["Datum", "Firma", "Typ", "Beschreibung", "Fällig am", "Status", "Verantwortlich", "Ampel"]
    widths = [13, 22, 15, 32, 13, 12, 15, 8]
    hr = 4
    _thead(ws, hr, names, widths=widths)
    first = 5
    # 1-2 Aktivitäten je aktivem Deal, deterministisch
    rows = []
    for i, deal in enumerate(DEALS):
        if deal["phase"] in ("Gewonnen", "Verloren"):
            continue
        typ = AKTIV_TYP[i % len(AKTIV_TYP)]
        faellig = d(((i * 9) % 40) - 8)     # teils überfällig
        status = "Erledigt" if i % 4 == 0 else "Offen"
        rows.append((d(-(i % 20)), deal["firma"], typ, deal["nx"], faellig, status, deal["verant"]))
    for r, (dt, firma, typ, besch, faellig, status, verant) in enumerate(rows):
        row = first + r
        data = [dt, firma, typ, besch, faellig, status, verant]
        for i, v in enumerate(data):
            c = ws.cell(row, 1 + i, v)
            c.border = box
            c.font = font(10)
            if r % 2 == 1:
                c.fill = fill(GREY_ROW)
            if i in (0, 4):
                c.number_format = "DD.MM.YYYY"
                c.alignment = CENTER
        # Ampel: erledigt=✅, überfällig & offen=🔴, in 7T=🟡, sonst 🟢
        ampel = (f'=IF(F{row}="Erledigt","✅",IF(E{row}<TODAY(),"🔴",'
                 f'IF(E{row}<=TODAY()+7,"🟡","🟢")))')
        ac = ws.cell(row, 8, ampel)
        ac.alignment = CENTER
        ac.font = font(12)
        ac.border = box
        ws.row_dimensions[row].height = 20
    last = first + len(rows) - 1

    tbl = Table(displayName="Aktivitaeten", ref=f"A{hr}:H{last}")
    tbl.tableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showRowStripes=False)
    ws.add_table(tbl)

    v = DataValidation(type="list", formula1="=Listen!$K$5:$K$6", allow_blank=True)
    ws.add_data_validation(v)
    v.add(f"F{first}:F{last}")
    vt = DataValidation(type="list", formula1="=Listen!$J$5:$J$10", allow_blank=True)
    ws.add_data_validation(vt)
    vt.add(f"C{first}:C{last}")

    # überfällige & offene Zeilen rot hinterlegen
    ws.conditional_formatting.add(
        f"A{first}:H{last}",
        FormulaRule(formula=[f'AND($F{first}="Offen",$E{first}<TODAY())'],
                    fill=fill("FDECEA")))
    ws.conditional_formatting.add(
        f"F{first}:F{last}",
        CellIsRule(operator="equal", formula=['"Erledigt"'],
                   font=font(10, color=GREEN), fill=fill("E7F6EE")))


# ---------------------------------------------------------------------------
def _kontakte(ws):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"
    _header(ws, "A", "KONTAKTE & FIRMEN (CRM)", "H",
            sub="Alle Firmen & Ansprechpartner. E-Mail/Telefon deterministisch generiert (Demo).")
    names = ["Firma", "Ansprechpartner", "Rolle", "E-Mail", "Telefon", "Region", "Branche", "Letzter Kontakt"]
    widths = [24, 18, 16, 30, 16, 12, 15, 15]
    hr = 4
    _thead(ws, hr, names, widths=widths)
    first = 5
    seen = set()
    uniq = []
    for deal in DEALS:
        if deal["firma"] in seen:
            continue
        seen.add(deal["firma"])
        uniq.append(deal)
    rollen = ["Geschäftsführung", "Einkauf", "Facility Management", "Fuhrpark", "Nachhaltigkeit"]
    for r, deal in enumerate(uniq):
        row = first + r
        slug = "".join(ch for ch in deal["firma"].lower() if ch.isalnum())[:14]
        mail = f"{deal['ap'].split('.')[-1].strip().lower()}@{slug}.ch"
        tel = f"+41 {44 + (r % 40):02d} {200 + (r * 7) % 700:03d} {10 + (r % 89):02d} {(r * 3) % 100:02d}"
        letzt = d(-(3 + (r * 5) % 60))
        data = [deal["firma"], deal["ap"], rollen[r % len(rollen)], mail, tel,
                deal["region"], deal["branche"], letzt]
        for i, v in enumerate(data):
            c = ws.cell(row, 1 + i, v)
            c.border = box
            c.font = font(10)
            if r % 2 == 1:
                c.fill = fill(GREY_ROW)
            if i == 7:
                c.number_format = "DD.MM.YYYY"
                c.alignment = CENTER
        ws.row_dimensions[row].height = 20
    last = first + len(uniq) - 1
    tbl = Table(displayName="Kontakte", ref=f"A{hr}:H{last}")
    tbl.tableStyleInfo = TableStyleInfo(name="TableStyleMedium4", showRowStripes=False)
    ws.add_table(tbl)


# ---------------------------------------------------------------------------
def _forecast(ws):
    ws.sheet_view.showGridLines = False
    _header(ws, "B", "MONATS-FORECAST  ·  Soll / Ist", "H",
            sub="Gewichteter Forecast & gewonnener Umsatz je Monat. Ziel (Soll) editierbar.")
    ws.column_dimensions["A"].width = 2
    P = "Pipeline!"
    gw = f"{P}{CL['Gew. Wert (CHF)']}{FD}:{CL['Gew. Wert (CHF)']}{LD}"
    vol = f"{P}{CL['Volumen (CHF)']}{FD}:{CL['Volumen (CHF)']}{LD}"
    ph = f"{P}{CL['Phase']}{FD}:{CL['Phase']}{LD}"
    da = f"{P}{CL['Erw. Abschluss']}{FD}:{CL['Erw. Abschluss']}{LD}"

    hr = 4
    _thead(ws, hr, ["Monat", "Monatsanfang", "Monatsende", "Gew. Forecast",
                    "Gewonnen (Ist)", "Ziel (Soll)", "Zielerreichung"],
           start_col=2, widths=[14, 14, 14, 16, 16, 14, 15])
    ws.column_dimensions["C"].hidden = False
    months = [(2026, m) for m in range(7, 13)]
    ziele = [700000, 750000, 800000, 850000, 900000, 950000]
    first = 5
    for i, (yy, mm) in enumerate(months):
        row = first + i
        ws.cell(row, 2, date(yy, mm, 1).strftime("%b %Y")).border = box
        ws.cell(row, 2).font = font(10, bold=True)
        anf = ws.cell(row, 3, date(yy, mm, 1))
        end = ws.cell(row, 4, date(yy, mm, 28) + timedelta(days=4)
                      - timedelta(days=(date(yy, mm, 28) + timedelta(days=4)).day))
        for c in (anf, end):
            c.number_format = "DD.MM.YYYY"
            c.alignment = CENTER
            c.border = box
        fcast = ws.cell(row, 5,
                        f'=SUMIFS({gw},{da},">="&C{row},{da},"<="&D{row},{ph},"<>Gewonnen",{ph},"<>Verloren")')
        ist = ws.cell(row, 6,
                      f'=SUMIFS({vol},{da},">="&C{row},{da},"<="&D{row},{ph},"Gewonnen")')
        soll = ws.cell(row, 7, ziele[i])
        soll.protection = UNLOCKED
        err = ws.cell(row, 8, f'=IFERROR((E{row}+F{row})/G{row},0)')
        err.number_format = "0%"
        for c in (fcast, ist, soll):
            c.number_format = '#,##0'
            c.alignment = RIGHT
        for c in (fcast, ist, soll, err):
            c.border = box
        ws.row_dimensions[row].height = 20
    last = first + len(months) - 1

    ws.conditional_formatting.add(
        f"H{first}:H{last}",
        ColorScaleRule(start_type="num", start_value=0, start_color="F8C9C4",
                       mid_type="num", mid_value=0.8, mid_color="FCE9B8",
                       end_type="num", end_value=1.2, end_color="C6E7D0"))

    # Diagramm Forecast vs. Ziel
    ch = BarChart()
    ch.type = "col"
    ch.title = "Gew. Forecast + Gewonnen vs. Ziel (CHF)"
    ch.style = 10
    ch.height, ch.width = 8, 17
    data = Reference(ws, min_col=5, max_col=7, min_row=hr, max_row=last)
    cats = Reference(ws, min_col=2, min_row=first, max_row=last)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    ws.add_chart(ch, f"B{last + 3}")


# ---------------------------------------------------------------------------
def _ziele(ws):
    ws.sheet_view.showGridLines = False
    _header(ws, "B", "ZIELE  ·  Zielerreichung je Verantwortlicher", "H",
            sub="Jahresziel editierbar. Ist = gewonnener Umsatz, Pipeline = gewichteter Wert.")
    ws.column_dimensions["A"].width = 2
    P = "Pipeline!"
    gw = f"{P}{CL['Gew. Wert (CHF)']}{FD}:{CL['Gew. Wert (CHF)']}{LD}"
    vol = f"{P}{CL['Volumen (CHF)']}{FD}:{CL['Volumen (CHF)']}{LD}"
    ph = f"{P}{CL['Phase']}{FD}:{CL['Phase']}{LD}"
    vr = f"{P}{CL['Verantwortlich']}{FD}:{CL['Verantwortlich']}{LD}"
    hr = 4
    _thead(ws, hr, ["Verantwortlich", "Jahresziel", "Gewonnen (Ist)",
                    "Gew. Pipeline", "Zielerreichung"],
           start_col=2, widths=[18, 15, 16, 16, 15])
    first = 5
    ziele = [2500000, 1500000, 1200000, 1200000, 1000000]
    for i, member in enumerate(TEAM):
        row = first + i
        ws.cell(row, 2, member).border = box
        ws.cell(row, 2).font = font(10, bold=True)
        z = ws.cell(row, 3, ziele[i])
        z.protection = UNLOCKED
        ist = ws.cell(row, 4, f'=SUMIFS({vol},{vr},B{row},{ph},"Gewonnen")')
        pipe = ws.cell(row, 5, f'=SUMIFS({gw},{vr},B{row})')
        err = ws.cell(row, 6, f'=IFERROR((D{row}+E{row})/C{row},0)')
        err.number_format = "0%"
        for c in (z, ist, pipe):
            c.number_format = '#,##0'
            c.alignment = RIGHT
        for c in (z, ist, pipe, err):
            c.border = box
        ws.row_dimensions[row].height = 20
    last = first + len(TEAM) - 1
    ws.conditional_formatting.add(f"F{first}:F{last}", DataBarRule(
        start_type="num", start_value=0, end_type="num", end_value=1.2, color=GREEN))

    ch = BarChart()
    ch.type = "bar"
    ch.title = "Zielerreichung je Verantwortlicher"
    ch.style = 12
    ch.height, ch.width = 7, 15
    data = Reference(ws, min_col=6, min_row=hr, max_row=last)
    cats = Reference(ws, min_col=2, min_row=first, max_row=last)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    ch.legend = None
    ws.add_chart(ch, f"B{last + 3}")


# ---------------------------------------------------------------------------
def _dashboard(ws):
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    for col in "BCDEFGH":
        ws.column_dimensions[col].width = 17
    ws.merge_cells("B2:H2")
    ws["B2"] = "VERTRIEBS-COCKPIT"
    ws["B2"].font = font(22, bold=True, color=NAVY)
    ws.merge_cells("B3:H3")
    ws["B3"] = "Pipeline-Steuerung  ·  Forecast  ·  Live-Marktdaten"
    ws["B3"].font = font(11, color=RED, bold=True)
    ws.row_dimensions[2].height = 30

    P = "Pipeline!"
    vol = f"{P}{CL['Volumen (CHF)']}{FD}:{CL['Volumen (CHF)']}{LD}"
    gw = f"{P}{CL['Gew. Wert (CHF)']}{FD}:{CL['Gew. Wert (CHF)']}{LD}"
    ph = f"{P}{CL['Phase']}{FD}:{CL['Phase']}{LD}"
    reg = f"{P}{CL['Region']}{FD}:{CL['Region']}{LD}"
    br = f"{P}{CL['Branche']}{FD}:{CL['Branche']}{LD}"
    verant = f"{P}{CL['Verantwortlich']}{FD}:{CL['Verantwortlich']}{LD}"

    kpis = [
        ("Pipeline gesamt", f"=SUM({vol})", '#,##0 "CHF"', NAVY),
        ("Gewichteter Forecast", f"=SUM({gw})", '#,##0 "CHF"', RED),
        ("Offene Deals", f'=COUNTIFS({ph},"<>Gewonnen",{ph},"<>Verloren")', '0', NAVY_SOFT),
        ("Gewonnen (YTD)", f'=SUMIFS({vol},{ph},"Gewonnen")', '#,##0 "CHF"', GREEN),
        ("Win-Rate", f'=IFERROR(COUNTIF({ph},"Gewonnen")/(COUNTIF({ph},"Gewonnen")+COUNTIF({ph},"Verloren")),0)', '0%', NAVY),
        ("Ø Deal-Größe", f"=IFERROR(AVERAGE({vol}),0)", '#,##0 "CHF"', NAVY_SOFT),
    ]
    positions = [("B", "C"), ("D", "E"), ("F", "G")]
    r0 = 5
    for idx, (label, formula, numfmt, color) in enumerate(kpis):
        rb = r0 + (idx // 3) * 4
        c0, c1 = positions[idx % 3]
        ws.merge_cells(f"{c0}{rb}:{c1}{rb}")
        ws[f"{c0}{rb}"] = label.upper()
        ws[f"{c0}{rb}"].font = font(9, bold=True, color=MUTE)
        ws[f"{c0}{rb}"].alignment = Alignment(horizontal="left", indent=1, vertical="center")
        ws.merge_cells(f"{c0}{rb + 1}:{c1}{rb + 1}")
        v = ws[f"{c0}{rb + 1}"]
        v.value = formula
        v.number_format = numfmt
        v.font = font(20, bold=True, color=color)
        v.alignment = Alignment(horizontal="left", indent=1, vertical="center")
        ws.row_dimensions[rb + 1].height = 30
        for rr in (rb, rb + 1):
            for cc in (c0, c1):
                cur = ws[f"{cc}{rr}"]
                cur.fill = fill(CARD)
                cur.border = Border(
                    top=Side(style="thin", color=LINE) if rr == rb else None,
                    bottom=Side(style="thin", color=LINE) if rr == rb + 1 else None,
                    left=Side(style="thin", color=LINE) if cc == c0 else None,
                    right=Side(style="thin", color=LINE) if cc == c1 else None)

    # --- Hilfstabellen für Diagramme (Phase-Funnel, Region, Branche) ----
    ar = 15
    ws[f"B{ar}"] = "Funnel — Pipeline nach Phase (CHF)"
    ws[f"B{ar}"].font = font(12, bold=True, color=NAVY)
    _thead(ws, ar + 1, ["Phase", "Volumen"], start_col=2, widths=[16, 14])
    funnel_order = ["Lead", "Qualifiziert", "Angebot", "Verhandlung", "Gewonnen"]
    for i, pnm in enumerate(funnel_order):
        rr = ar + 2 + i
        ws.cell(rr, 2, pnm).border = box
        c = ws.cell(rr, 3, f'=SUMIFS({vol},{ph},B{rr})')
        c.number_format = '#,##0'
        c.border = box
        c.alignment = RIGHT
    fun_last = ar + 1 + len(funnel_order)

    # Region-Tabelle
    ws[f"E{ar}"] = "Nach Region (gew. Wert)"
    ws[f"E{ar}"].font = font(12, bold=True, color=NAVY)
    _thead(ws, ar + 1, ["Region", "Gew. Wert"], start_col=5, widths=[14, 14])
    top_reg = REGIONEN
    for i, rg in enumerate(top_reg):
        rr = ar + 2 + i
        ws.cell(rr, 5, rg).border = box
        c = ws.cell(rr, 6, f'=SUMIFS({gw},{reg},E{rr})')
        c.number_format = '#,##0'
        c.border = box
        c.alignment = RIGHT
    reg_last = ar + 1 + len(top_reg)

    # Branche-Tabelle
    bcol = ar + 2 + len(top_reg) + 1
    ws[f"E{bcol}"] = "Nach Branche (gew. Wert)"
    ws[f"E{bcol}"].font = font(12, bold=True, color=NAVY)
    _thead(ws, bcol + 1, ["Branche", "Gew. Wert"], start_col=5, widths=[14, 14])
    for i, bn in enumerate(BRANCHEN):
        rr = bcol + 2 + i
        ws.cell(rr, 5, bn).border = box
        c = ws.cell(rr, 6, f'=SUMIFS({gw},{br},E{rr})')
        c.number_format = '#,##0'
        c.border = box
        c.alignment = RIGHT
    br_last = bcol + 1 + len(BRANCHEN)

    # Verantwortlich-Tabelle
    ws[f"H{ar}"] = "Gew. Forecast je Verantwortlicher"
    ws[f"H{ar}"].font = font(12, bold=True, color=NAVY)
    _thead(ws, ar + 1, ["Verantwortlich", "Gew. Wert"], start_col=8, widths=[16, 14])
    for i, m in enumerate(TEAM):
        rr = ar + 2 + i
        ws.cell(rr, 8, m).border = box
        c = ws.cell(rr, 9, f'=SUMIFS({gw},{verant},H{rr})')
        c.number_format = '#,##0'
        c.border = box
        c.alignment = RIGHT
    team_last = ar + 1 + len(TEAM)

    # --- Diagramme ------------------------------------------------------
    funnel = BarChart()
    funnel.type = "bar"
    funnel.title = "Sales-Funnel (CHF nach Phase)"
    funnel.style = 10
    funnel.height, funnel.width = 8, 13
    funnel.add_data(Reference(ws, min_col=3, min_row=ar + 1, max_row=fun_last), titles_from_data=True)
    funnel.set_categories(Reference(ws, min_col=2, min_row=ar + 2, max_row=fun_last))
    funnel.legend = None
    funnel.dataLabels = DataLabelList()
    funnel.dataLabels.showVal = True
    ws.add_chart(funnel, f"B{max(br_last, team_last) + 3}")

    pie = PieChart()
    pie.title = "Gew. Wert nach Region"
    pie.height, pie.width = 8, 12
    pie.add_data(Reference(ws, min_col=6, min_row=ar + 1, max_row=reg_last), titles_from_data=True)
    pie.set_categories(Reference(ws, min_col=5, min_row=ar + 2, max_row=reg_last))
    ws.add_chart(pie, f"F{max(br_last, team_last) + 3}")

    bar_br = BarChart()
    bar_br.type = "col"
    bar_br.title = "Gew. Wert nach Branche"
    bar_br.style = 12
    bar_br.height, bar_br.width = 8, 13
    bar_br.add_data(Reference(ws, min_col=6, min_row=bcol + 1, max_row=br_last), titles_from_data=True)
    bar_br.set_categories(Reference(ws, min_col=5, min_row=bcol + 2, max_row=br_last))
    bar_br.legend = None
    ws.add_chart(bar_br, f"B{max(br_last, team_last) + 20}")


# ---------------------------------------------------------------------------
def _live(ws):
    ws.sheet_view.showGridLines = False
    for col, w in (("A", 2), ("B", 26), ("C", 16), ("D", 12), ("E", 20), ("F", 14)):
        ws.column_dimensions[col].width = w
    ws.merge_cells("B2:F2")
    ws["B2"] = "LIVE-DATEN  ·  E-Mobilität & Markt (per F9)"
    ws["B2"].font = font(18, bold=True, color=NAVY)
    ws.merge_cells("B3:F3")
    ws["B3"] = ("Öffentliche Ladeinfrastruktur Schweiz live via OpenChargeMap. "
                "Aktualisieren = Taste F9 (Neu berechnen). Windows-Desktop-Excel.")
    ws["B3"].font = font(10, italic=True, color=MUTE)

    ws.merge_cells("B5:D5")
    btn = ws["B5"]
    btn.value = "🔄  F9 DRÜCKEN = LIVE AKTUALISIEREN"
    btn.font = font(12, bold=True, color=WHITE)
    for cc in ("B5", "C5", "D5"):
        ws[cc].fill = fill(RED)
    btn.alignment = CENTER
    ws.row_dimensions[5].height = 30
    ws.merge_cells("E5:F5")
    ws["E5"] = "→ WEBSERVICE holt den Feed; FILTERXML liest die Werte."
    ws["E5"].font = font(9, italic=True, color=MUTE)
    ws["E5"].alignment = LEFT

    # Optionaler (kostenloser) OpenChargeMap-API-Key --------------------
    ws["B6"] = "OpenChargeMap API-Key (optional, gratis):"
    ws["B6"].font = font(9, bold=True, color=MUTE)
    keyc = ws["C6"]
    keyc.value = ""       # hier eigenen Key eintragen (openchargemap.org/site/loginprovider)
    keyc.fill = fill("FFF7D6")
    keyc.border = box
    keyc.protection = UNLOCKED
    ws.merge_cells("C6:F6")

    # Roh-Feed (WEBSERVICE) ---------------------------------------------
    ws["B7"] = "Roh-Feed (WEBSERVICE):"
    ws["B7"].font = font(9, bold=True, color=MUTE)
    ocm = ("https://api.openchargemap.io/v3/poi/?output=xml&countrycode=CH"
           "&maxresults=12&compact=true&verbose=false&key=")
    ws["C7"] = f'=IFERROR(_xlfn.WEBSERVICE("{ocm}"&$C$6),"")'
    ws["C7"].font = font(8, color=MUTE)
    ws.merge_cells("C7:F7")
    ws.row_dimensions[7].height = 14
    RAW = "$C$7"

    def poi(i, path):
        return (f'=IFERROR(_xlfn.FILTERXML({RAW},'
                f'"(//*[local-name()=\'POI\'])[{i}]{path}"),"—")')

    # Tabelle: aktuelle Ladestandorte -----------------------------------
    ws["B9"] = "Öffentliche Ladestandorte Schweiz (live)"
    ws["B9"].font = font(12, bold=True, color=NAVY)
    _thead(ws, 10, ["Standort", "Ort", "Kanton", "Betreiber", "Ladepkt."],
           start_col=2, widths=[26, 16, 12, 20, 14])
    N = 8
    for i in range(1, N + 1):
        row = 10 + i
        title = ws.cell(row, 2, poi(i, "/*[local-name()='AddressInfo']/*[local-name()='Title']"))
        town = ws.cell(row, 3, poi(i, "/*[local-name()='AddressInfo']/*[local-name()='Town']"))
        kanton = ws.cell(row, 4, poi(i, "/*[local-name()='AddressInfo']/*[local-name()='StateOrProvince']"))
        op = ws.cell(row, 5, poi(i, "/*[local-name()='OperatorInfo']/*[local-name()='Title']"))
        pts = ws.cell(row, 6, poi(i, "/*[local-name()='NumberOfPoints']"))
        for c in (title, town, kanton, op, pts):
            c.border = box
            c.font = font(10)
            if i % 2 == 0:
                c.fill = fill(GREY_ROW)
        title.alignment = LEFT
        pts.alignment = CENTER
        ws.row_dimensions[row].height = 19
    last = 10 + N

    ws[f"B{last + 1}"] = "Angezeigte Standorte:"
    ws[f"B{last + 1}"].font = font(9, bold=True, color=MUTE)
    cnt = ws.cell(last + 1, 3, f'=SUMPRODUCT(--($B$11:$B${last}<>"—"),--($B$11:$B${last}<>""))')
    cnt.font = font(11, bold=True, color=NAVY)
    cnt.alignment = CENTER

    ws.merge_cells(f"B{last + 3}:F{last + 4}")
    ws[f"B{last + 3}"] = ("Zeigt es „—“: einmal F9 drücken. Für Dauerbetrieb einen kostenlosen "
                          "OpenChargeMap-API-Key oben in C6 eintragen (openchargemap.org). "
                          "WEBSERVICE/FILTERXML gibt es nur in Excel für Windows (Desktop) — "
                          "auf Mac/Web stattdessen die Power-Query-Vorlagen unten nutzen.")
    ws[f"B{last + 3}"].font = font(9, italic=True, color=MUTE)
    ws[f"B{last + 3}"].alignment = LEFT

    # Weitere Online-Quellen & eigene Datenbank -------------------------
    base = last + 6
    ws[f"B{base}"] = "Weitere Online-Quellen & eigene Datenbank — Power Query"
    ws[f"B{base}"].font = font(12, bold=True, color=NAVY)
    steps = [
        "• Ladeinfrastruktur (voll): Daten ▸ Aus dem Web ▸ OpenChargeMap-JSON — filtern/aggregieren nach Kanton/Betreiber.",
        "• Firmendaten anreichern: Handelsregister Zefix-API (UID, Adresse, Rechtsform) per Firma abrufen.",
        "• Eigene DB: Daten ▸ Aus Datenbank (SQL Server / MySQL / PostgreSQL) — Server & Zugangsdaten eintragen.",
        "• Google Sheets / SharePoint: Freigabe-CSV-Link als Quelle.",
        "Fertige M-Vorlagen: data/PowerQuery_Vorlagen.m  ·  danach „Alle aktualisieren“ (Strg+Alt+F5).",
    ]
    for i, s in enumerate(steps):
        r = base + 1 + i
        ws[f"B{r}"] = s
        ws[f"B{r}"].font = font(9, color=NAVY if s.startswith("•") else MUTE)
        ws.merge_cells(f"B{r}:F{r}")
        ws[f"B{r}"].alignment = LEFT


# ---------------------------------------------------------------------------
def _help(ws):
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 110
    L = [
        ("So arbeitest du perfekt mit diesem Cockpit", 16, True, NAVY),
        ("", 6, False, MUTE),
        ("1 · Dashboard", 12, True, RED),
        ("KPIs, Sales-Funnel und Auswertungen nach Region/Branche/Verantwortlichem rechnen automatisch —", 10, False, NAVY),
        ("alles aktualisiert sich, sobald du in der Pipeline etwas änderst.", 10, False, NAVY),
        ("", 6, False, MUTE),
        ("2 · Pipeline (Herzstück)", 12, True, RED),
        ("• Filtern/Sortieren über die Pfeile in der blauen Kopfzeile (Region, Phase, Verantwortlich …).", 10, False, NAVY),
        ("• Datenschnitte (Klick-Filter): Tabelle anklicken ▸ Menüband „Tabellenentwurf“ ▸ Datenschnitt einfügen.", 10, False, NAVY),
        ("• Dropdowns für Phase/Priorität/Region/Branche/Produkt/Verantwortlich (nur gültige Werte).", 10, False, NAVY),
        ("• Automatik: Wahrscheinlichkeit folgt der Phase; Gew. Wert = Volumen × Wahrsch.;", 10, False, NAVY),
        ("  Tage bis Abschluss & Ampel (🔴 ≤14 T, 🟡 ≤45 T, 🟢 sonst, ✅ gewonnen).", 10, False, NAVY),
        ("• Neue Zeile einfach unter der letzten schreiben – Tabelle & Dashboard wachsen automatisch mit.", 10, False, NAVY),
        ("", 6, False, MUTE),
        ("3 · Aktivitäten · Kontakte · Forecast · Ziele", 12, True, RED),
        ("Aktivitäten: Aufgaben mit Fälligkeits-Ampel (überfällig = rot). Kontakte: Firmen-/CRM-Liste.", 10, False, NAVY),
        ("Forecast: gewichteter Umsatz je Monat vs. Ziel. Ziele: Zielerreichung je Verantwortlicher.", 10, False, NAVY),
        ("", 6, False, MUTE),
        ("4 · Live-Daten online abrufen — per Knopfdruck (F9)", 12, True, RED),
        ("Blatt „Live-Daten“: öffentliche Ladestandorte Schweiz live via OpenChargeMap (WEBSERVICE + FILTERXML).", 10, False, NAVY),
        ("Aktualisieren = Taste F9 (Windows-Desktop-Excel). Gratis-API-Key in Zelle C6 für Dauerbetrieb.", 10, False, NAVY),
        ("Mehr Quellen/eigene Datenbank (SQL/Zefix/Google Sheets): M-Vorlagen in data/PowerQuery_Vorlagen.m.", 10, False, NAVY),
        ("", 6, False, MUTE),
        ("5 · Formelzellen schützen (optional)", 12, True, RED),
        ("Formel-/Berechnungszellen sind als „gesperrt“ markiert, Eingabefelder als „frei“.", 10, False, NAVY),
        ("Aktivieren mit: Überprüfen ▸ Blatt schützen (ohne Passwort bestätigen). Eingaben bleiben möglich.", 10, False, NAVY),
        ("", 6, False, MUTE),
        ("Reproduzierbar: python3 src/build_excel.py  ·  Farbwelt Navy #1B2430 + Akzent-Rot #E2001A.", 9, False, MUTE),
    ]
    r = 2
    for text, size, bold, color in L:
        ws.cell(r, 2, text).font = font(size, bold=bold, color=color)
        ws.cell(r, 2).alignment = LEFT
        r += 1


# ---------------------------------------------------------------------------
def _print_setup(wb):
    for ws in wb.worksheets:
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_options.horizontalCentered = True
        ws.oddHeader.left.text = "Vertriebs-Cockpit"
        ws.oddHeader.right.text = "&D"
        ws.oddFooter.left.text = "Vertraulich"
        ws.oddFooter.right.text = "Seite &P von &N"
    # Wiederholzeilen für Tabellenblätter
    for name in ("Pipeline", "Aktivitäten", "Kontakte"):
        wb[name].print_title_rows = "4:4"


# ===========================================================================
def write_companions():
    os.makedirs(DATA, exist_ok=True)

    m = r'''// ============================================================
// Power-Query-Vorlagen — Vertriebs-Cockpit (E-Mobilität / Energie)
// Einfügen: Daten ▸ Daten abrufen ▸ Leere Abfrage ▸ Erweiterter Editor
// Danach genügt „Alle aktualisieren“ (Strg+Alt+F5) als Knopfdruck.
// Funktioniert auch auf Mac / Excel im Web (anders als WEBSERVICE).
// ============================================================

// --- 1) LADEINFRASTRUKTUR SCHWEIZ (OpenChargeMap, JSON) ----------------
// Kostenlosen API-Key holen: openchargemap.org ▸ Profil ▸ API Key
let
    Key      = "HIER-DEINEN-KOSTENLOSEN-KEY",
    Url      = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=CH&maxresults=500&compact=true&verbose=false&key=" & Key,
    Quelle   = Json.Document(Web.Contents(Url)),
    AlsTab   = Table.FromList(Quelle, Splitter.SplitByNothing(), {"POI"}),
    Erweitert= Table.ExpandRecordColumn(AlsTab, "POI", {"AddressInfo","OperatorInfo","NumberOfPoints"}),
    Adr      = Table.ExpandRecordColumn(Erweitert, "AddressInfo", {"Title","Town","StateOrProvince"}, {"Standort","Ort","Kanton"}),
    Betr     = Table.ExpandRecordColumn(Adr, "OperatorInfo", {"Title"}, {"Betreiber"})
in
    Betr

// Auswertung z. B.: Anzahl Ladepunkte je Kanton
// = Table.Group(Betr, {"Kanton"}, {{"Ladepunkte", each List.Sum([NumberOfPoints]), type number}})

// --- 2) FIRMENDATEN ANREICHERN (Handelsregister Zefix) ----------------
// Sucht eine Firma und liefert UID / Rechtsform / Sitz.
(FirmenName as text) =>
let
    Body   = "{""name"":""" & FirmenName & """,""languageKey"":""de""}",
    Quelle = Json.Document(Web.Contents("https://www.zefix.ch/ZefixREST/api/v1/firm/search.json",
                [Headers=[#"Content-Type"="application/json"], Content=Text.ToBinary(Body)])),
    AlsTab = Table.FromList(Quelle, Splitter.SplitByNothing(), {"Firma"}),
    Feld   = Table.ExpandRecordColumn(AlsTab, "Firma", {"name","uidFormatted","legalForm","legalSeat"})
in
    Feld

// --- 3) EIGENE SQL-DATENBANK (Server/DB anpassen) ----------------------
// let
//     Quelle = Sql.Database("SERVERNAME", "DATENBANK",
//                 [Query="SELECT firma, region, phase, volumen, erw_abschluss FROM deals"])
// in
//     Quelle

// --- 4) MySQL / PostgreSQL ---------------------------------------------
// MySQL:       Quelle = MySQL.Database("host:3306", "db", [Query="SELECT * FROM deals"])
// PostgreSQL:  Quelle = PostgreSQL.Database("host", "db", [Query="SELECT * FROM deals"])

// --- 5) GOOGLE SHEETS / SHAREPOINT (Freigabe-CSV-Link) -----------------
// let
//     Quelle = Csv.Document(Web.Contents("https://.../export?format=csv"),
//                 [Delimiter=",", Encoding=65001]),
//     Kopf   = Table.PromoteHeaders(Quelle, [PromoteAllScalars=true])
// in
//     Kopf
'''
    with open(os.path.join(DATA, "PowerQuery_Vorlagen.m"), "w") as f:
        f.write(m)
    print("OK  data/PowerQuery_Vorlagen.m")


if __name__ == "__main__":
    build()
    write_companions()
