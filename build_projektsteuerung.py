# -*- coding: utf-8 -*-
"""
Projektsteuerungs-Tool MiT-PWR-WIN-2026-001  (V6 - Vollausbau ohne VBA)
SharePoint-taugliche .xlsx ohne Makros. Schweizer Schreibweise (ss statt scharfes S).
Datum TT.MM.JJJJ, Arial, Navy #1F3A5F (Kopf), Orange #E8740C (Akzente).

17 Registerblaetter:
  Dashboard | Wochenbericht | Terminplan (Wochen-Gantt) | Meilensteine | Aufgaben |
  Termine & Meetings | Personal & Zutritt | Schichtplan | Lieferungen & Logistik |
  Testprotokolle | Fuel-Log | Stopp-Punkte & Risiken | Kommerziell | Trend |
  Dokumente | Kontakte | Aenderungslog & Entscheide

Alle Formeln intern englisch/komma-getrennt (Excel-Standard, deutsch angezeigt).
Nur Basis-Funktionen -> kompatibel inkl. Excel im Browser. Keine CHF-Verkaufspreise.
"""
import datetime
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule, DataBarRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.chart import BarChart, DoughnutChart, LineChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.data_source import AxDataSource, StrRef
from openpyxl.chart.marker import Marker
from openpyxl.drawing.line import LineProperties

# ---------------------------------------------------------------- Farben / Stile
NAVY = "1F3A5F"; ORANGE = "E8740C"; WHITE = "FFFFFF"
LIGHT = "F2F5F9"
GREEN = "C6EFCE"; GREEN_TXT = "006100"
RED = "FFC7CE"; RED_TXT = "9C0006"
ORANGE_FILL = "FCE3C8"; ORANGE_TXT = "9C4A00"
YELLOW = "FFEB9C"; YELLOW_TXT = "9C6500"
GREY = "D9D9D9"; BAR_BLUE = "4F81BD"
TODAY_TINT = "D9E2EE"
C_OFFEN = "8EA9C1"; C_ARBEIT = "F2C230"; C_ERLEDIGT = "70AD47"; C_KRITISCH = "C00000"; C_VERSCH = "E8740C"

FONT_NAME = "Arial"
hdr_font   = Font(name=FONT_NAME, size=10, bold=True, color=WHITE)
hdr_fill   = PatternFill("solid", fgColor=NAVY)
title_font = Font(name=FONT_NAME, size=16, bold=True, color=NAVY)
sub_font   = Font(name=FONT_NAME, size=11, bold=True, color=ORANGE)
label_font = Font(name=FONT_NAME, size=10, bold=True, color=NAVY)
base_font  = Font(name=FONT_NAME, size=10, color="000000")
bold_font  = Font(name=FONT_NAME, size=10, bold=True, color=NAVY)
kpi_num    = Font(name=FONT_NAME, size=18, bold=True, color=NAVY)
kpi_lbl    = Font(name=FONT_NAME, size=9, bold=True, color="404040")
small_it   = Font(name=FONT_NAME, size=8, italic=True, color="808080")
diamond_f  = Font(name=FONT_NAME, size=10, bold=True, color=NAVY)

thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left   = Alignment(horizontal="left", vertical="center", wrap_text=True)
left_top = Alignment(horizontal="left", vertical="top", wrap_text=True)

STATUS_LIST = "offen,in Arbeit,erledigt,verschoben,kritisch"
STATUS_DOK  = "Entwurf,final,signiert,ueberholt"
OWNER_LIST  = ("Burak,Stefan,Markus,Ann-Kathrin,Sarah,Samuel,Stephan Marty,Olli,Aggreko,DPR,MiT,"
               "Burak / Stephan,Burak / Samuel,Stefan / Stephan,Ann-Kathrin & Markus,Aggreko / MiT")

D = lambda m, d, hh=0, mm=0: datetime.datetime(2026, m, d, hh, mm)
wb = Workbook()

# ---------------------------------------------------------------- Hilfsfunktionen
def widths(ws, ws_widths, start=1):
    for i, w in enumerate(ws_widths):
        ws.column_dimensions[get_column_letter(start + i)].width = w

def header_row(ws, row, cols, start=1):
    for i, h in enumerate(cols):
        c = ws.cell(row=row, column=start + i, value=h)
        c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border

def body(ws, r0, r1, ncols, start=1, align=left_top):
    for r in range(r0, r1 + 1):
        for c in range(start, start + ncols):
            cell = ws.cell(row=r, column=c)
            cell.font = base_font; cell.alignment = align; cell.border = border

def make_table(ws, name, r0, r1, ncols, start=1):
    ref = f"{get_column_letter(start)}{r0}:{get_column_letter(start+ncols-1)}{r1}"
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(t)

def page_setup(ws, freeze="A2", title_rows="1:1"):
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    ws.freeze_panes = freeze
    if title_rows:
        ws.print_title_rows = title_rows

def status_cf(ws, col, r0, r1):
    rng = f"{col}{r0}:{col}{r1}"
    for val, fill, txt in [("erledigt", GREEN, GREEN_TXT), ("kritisch", RED, RED_TXT),
                           ("in Arbeit", YELLOW, YELLOW_TXT), ("verschoben", ORANGE_FILL, ORANGE_TXT)]:
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{val}"'],
            fill=PatternFill("solid", fgColor=fill), font=Font(name=FONT_NAME, color=txt)))

def add_dv(ws, items, rng):
    dv = DataValidation(type="list", formula1=f'"{items}"', allow_blank=True)
    dv.error = "Bitte einen Wert aus der Liste waehlen."; dv.errorTitle = "Ungueltige Eingabe"
    dv.prompt = "Wert aus Dropdown waehlen"
    ws.add_data_validation(dv); dv.add(rng)

def ampel_cf(ws, addr):
    for kw, fill in [("KRITISCH", RED_TXT), ("ACHTUNG", ORANGE), ("AUF KURS", GREEN_TXT)]:
        ws.conditional_formatting.add(addr,
            FormulaRule(formula=[f'ISNUMBER(SEARCH("{kw}",${addr.replace(":","").split()[0][0]}${addr[1:].split(":")[0][1:] if ":" in addr else addr[1:]}))'],
                        fill=PatternFill("solid", fgColor=fill)))

AMPEL_FORMULA = ('=IF(SUMPRODUCT((Aufgaben[Status]<>"erledigt")*(Aufgaben[Termin]<>"")*'
                 '(Aufgaben[Termin]<TODAY()))>0,"KRITISCH - ueberfaellige Aufgaben",'
                 'IF(COUNTIF(Meilensteine[Status],"kritisch")+COUNTIF(Aufgaben[Status],"kritisch")>0,'
                 '"ACHTUNG - kritische Punkte offen","AUF KURS - keine Ueberfaelligkeiten"))')

# ================================================================ MEILENSTEIN-DATEN (25)
# (Name, Phase, Plantermin, Verantwortlich, Vorgaenger-Nr, Bemerkung)
MS = [
    ("bSuite-Aufnahme", "Vorbereitung", D(7,16,8,0), "Sarah", None, "08:00, mit Ann-Kathrin & Burak"),
    ("Unterlagenpaket an DPR (Versicherung, HR-Auszug, Zeichnungsberechtigte, Zollprozess)", "Vorbereitung", D(7,16,12,0), "Ann-Kathrin & Markus", None, "12:00 an Roxana Minor"),
    ("Unterschriften Diessenhofen", "Vorbereitung", D(7,16), "Stefan", None, "Nachmittags"),
    ("Abstimmungs-Call Aggreko DE", "Vorbereitung", D(7,17,9,0), "Burak / Stephan", None, "16.07. 14:00 oder 17.07. 09:00"),
    ("PO-Korrekturliste an DPR", "Vorbereitung", D(7,17), "Burak", 4, "49A: 78/110 Tage; 49B: 131/110 Tage"),
    ("RAMS-Abgabe Hammertech", "Vorbereitung", D(7,20), "Samuel", None, "inkl. Personenliste Aggreko"),
    ("Personenliste Aggreko", "Vorbereitung", D(7,20), "Aggreko", None, ""),
    ("NDA MiT-DPR unterzeichnet", "Vorbereitung", D(7,22), "Stefan / Stephan", None, "eigene NDA, Partei MiT AG"),
    ("Entsendemeldung Aggreko-Personal", "Vorbereitung", D(7,24), "Aggreko", 7, "gesetzlich spaetestens 26.07."),
    ("PO 49A/49B final signiert", "Vorbereitung", D(7,24), "Stefan", 5, "nach Korrekturliste; Long-Lead-Frist startet"),
    ("Zollprozess DE-CH schriftlich bestaetigt", "Vorbereitung", D(7,28), "Markus", None, "Equipment vs. Kraftstoff"),
    ("WORKcontrol-Badges + Site Inductions + Kickoff-Meeting DPR", "Vorbereitung", D(7,31), "Ann-Kathrin", 9, "vor 03.08."),
    ("Lieferung Head-Load-Test", "Ausfuehrung", D(8,3), "Aggreko", 12, "54x 200 kW"),
    ("Site Setup & Einweisung Headloads", "Ausfuehrung", D(8,5), "Aggreko / MiT", 13, ""),
    ("Testbeginn Heat-Load", "Ausfuehrung", D(8,10), "Burak / Samuel", 14, ""),
    ("Abruf 3-MW-Block", "Ausfuehrung", D(8,14), "Burak", 15, "Mitte August"),
    ("Lieferung Loadbank 6 MVA", "Ausfuehrung", D(8,17), "Aggreko", 12, ""),
    ("Testbeginn Loadbank", "Ausfuehrung", D(8,19), "Burak / Samuel", 17, ""),
    ("Abruf 5-MW-Block", "Ausfuehrung", D(9,8), "Burak", 16, "2. September-Woche"),
    ("Zwischenstand / Review mit DPR", "Ausfuehrung", D(9,30), "Burak", None, "Quartalsende"),
    ("Mietende Loadbank", "Ausfuehrung", D(11,2), "Burak / Samuel", 18, "Datum strittig - PO-Fehler"),
    ("Closeout-Paket EN+DE an DPR", "Abschluss", D(11,30), "Burak / Stephan", 20, "15 Tage vor Leistungsende"),
    ("Mietende Headloads", "Ausfuehrung", D(12,11), "Burak / Samuel", 15, ""),
    ("Demontage", "Abschluss", D(12,14), "Aggreko / MiT", 23, ""),
    ("Abnahme & Restpunkte mit DPR", "Abschluss", D(12,15), "Burak", 24, ""),
]
N_MS = len(MS)
MS_LAST = N_MS + 1                  # 26
HELP = f"Meilensteine!$L$2:$L${MS_LAST}"   # Hilfsspalte L (eindeutige Termine)

# ================================================================ 1) DASHBOARD
ws = wb.active
ws.title = "Dashboard"
ws.sheet_view.showGridLines = False
widths(ws, [3, 34, 30, 8, 30, 12, 16, 12])

ws["B2"] = "PROJEKTSTEUERUNG"; ws["B2"].font = title_font
ws.merge_cells("B2:D2")
ws["B3"] = "MiT-PWR-WIN-2026-001  |  DPR Construction / Vantage Datacenter ZRH12"
ws["B3"].font = sub_font; ws.merge_cells("B3:H3")

stamm = [
    ("Projekt-Nr.", "MiT-PWR-WIN-2026-001"),
    ("Kunde / Auftraggeber", "DPR Construction (Abschluss in CHF)"),
    ("Endkunde / Standort", "Vantage Datacenter ZRH12, Fabrikstrasse 10/12, 8404 Winterthur"),
    ("Auftragnehmer", "Mobil in Time AG (Subunternehmer von DPR)"),
    ("Unterlieferant", "Aggreko Deutschland GmbH (Intercompany, Back-to-Back)"),
    ("Paket A", "6-MVA-Loadbank-Test, Angebot P-640380-3, PO E3-A25002-49A"),
    ("Paket B", "8-MW-Heat-Load-Test (54x 200 kW), Angebot P-650395-2, PO E3-A25002-49B"),
    ("Einkaufsvolumen (Referenz)", "EUR 590'840.34 netto (Aggreko; keine CHF-Verkaufspreise hier)"),
    ("Projektleiter", "Burak Uecoez"),
    ("Sprache", "Deutsch (Schweizer Schreibweise)"),
    ("Stand", '=TEXT(TODAY(),"DD.MM.YYYY")'),
]
r = 5
for lbl, val in stamm:
    ws.cell(row=r, column=2, value=lbl).font = label_font
    ws.cell(row=r, column=2).alignment = left
    c = ws.cell(row=r, column=3, value=val); c.font = base_font; c.alignment = left
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    for cc in range(2, 5):
        ws.cell(row=r, column=cc).border = border
    r += 1
STAMM_END = r - 1                    # 15

# ---- KPI Aufgaben (rechts, Zeilen 4-10)
ws.cell(row=4, column=5, value="AUFGABEN-STATUS").font = sub_font
kpi_a = [
    ("Offen", '=COUNTIF(Aufgaben[Status],"offen")', LIGHT),
    ("In Arbeit", '=COUNTIF(Aufgaben[Status],"in Arbeit")', YELLOW),
    ("Erledigt", '=COUNTIF(Aufgaben[Status],"erledigt")', GREEN),
    ("Kritisch / blockiert", '=COUNTIF(Aufgaben[Status],"kritisch")', RED),
    ("Ueberfaellig (offen, Termin < heute)",
     '=SUMPRODUCT((Aufgaben[Status]<>"erledigt")*(Aufgaben[Termin]<>"")*(Aufgaben[Termin]<TODAY()))', RED),
]
rr = 5
for lbl, f, fill in kpi_a:
    lc = ws.cell(row=rr, column=5, value=lbl); lc.font = kpi_lbl; lc.alignment = left
    lc.border = border; lc.fill = PatternFill("solid", fgColor=fill)
    vc = ws.cell(row=rr, column=6, value=f); vc.font = kpi_num; vc.alignment = center
    vc.border = border; vc.fill = PatternFill("solid", fgColor=fill)
    rr += 1
ws.cell(row=10, column=5, value="Fortschritt Aufgaben").font = kpi_lbl
ws.cell(row=10, column=5).alignment = left; ws.cell(row=10, column=5).border = border
pc = ws.cell(row=10, column=6,
    value='=IFERROR(COUNTIF(Aufgaben[Status],"erledigt")/COUNTA(Aufgaben[Nr.]),0)')
pc.number_format = "0%"; pc.font = Font(name=FONT_NAME, bold=True, color=NAVY)
pc.alignment = center; pc.border = border
tb = ws.cell(row=10, column=7,
    value='=REPT("█",ROUND(F10*12,0))&REPT("░",12-ROUND(F10*12,0))')
tb.font = Font(name=FONT_NAME, size=10, color=ORANGE); tb.alignment = left; tb.border = border

# ---- KPI Meilensteine (11-15)
ws.cell(row=11, column=5, value="MEILENSTEINE").font = sub_font
for rr, (lbl, f) in enumerate([
    ("Meilensteine gesamt", '=COUNTA(Meilensteine[Nr.])'),
    ("davon erledigt", '=COUNTIF(Meilensteine[Status],"erledigt")'),
    ("davon kritisch", '=COUNTIF(Meilensteine[Status],"kritisch")')], 12):
    lc = ws.cell(row=rr, column=5, value=lbl); lc.font = kpi_lbl; lc.alignment = left; lc.border = border
    vc = ws.cell(row=rr, column=6, value=f); vc.font = Font(name=FONT_NAME, size=12, bold=True, color=NAVY)
    vc.alignment = center; vc.border = border
ws.cell(row=15, column=5, value="Fortschritt Meilensteine").font = kpi_lbl
ws.cell(row=15, column=5).alignment = left; ws.cell(row=15, column=5).border = border
pm = ws.cell(row=15, column=6,
    value='=IFERROR(COUNTIF(Meilensteine[Status],"erledigt")/COUNTA(Meilensteine[Nr.]),0)')
pm.number_format = "0%"; pm.font = Font(name=FONT_NAME, bold=True, color=NAVY)
pm.alignment = center; pm.border = border
tb2 = ws.cell(row=15, column=7,
    value='=REPT("█",ROUND(F15*12,0))&REPT("░",12-ROUND(F15*12,0))')
tb2.font = Font(name=FONT_NAME, size=10, color=NAVY); tb2.alignment = left; tb2.border = border
ws.conditional_formatting.add("F10", DataBarRule(start_type='num', start_value=0,
    end_type='num', end_value=1, color=ORANGE))
ws.conditional_formatting.add("F15", DataBarRule(start_type='num', start_value=0,
    end_type='num', end_value=1, color=BAR_BLUE))

# ---- Ampel + Woche (17-19)
ws.cell(row=17, column=5, value="PROJEKTSTATUS (AMPEL)").font = sub_font
st = ws.cell(row=18, column=5, value=AMPEL_FORMULA)
st.font = Font(name=FONT_NAME, size=11, bold=True, color=WHITE); st.alignment = center
ws.merge_cells("E18:F18"); ws.cell(row=18, column=6).border = border; st.border = border
for kw, fill in [("KRITISCH", RED_TXT), ("ACHTUNG", ORANGE), ("AUF KURS", GREEN_TXT)]:
    ws.conditional_formatting.add("E18",
        FormulaRule(formula=[f'ISNUMBER(SEARCH("{kw}",$E$18))'],
                    fill=PatternFill("solid", fgColor=fill)))
ws.cell(row=19, column=5, value="Diese Woche faellig (Aufgaben)").font = kpi_lbl
ws.cell(row=19, column=5).alignment = left; ws.cell(row=19, column=5).border = border
wc = ws.cell(row=19, column=6,
    value='=SUMPRODUCT((Aufgaben[Status]<>"erledigt")*(Aufgaben[Termin]>=TODAY())*(Aufgaben[Termin]<TODAY()+7))')
wc.font = Font(name=FONT_NAME, bold=True, color=ORANGE); wc.alignment = center; wc.border = border

# ---- Tests & Lieferungen (20-22)
ws.cell(row=20, column=5, value="TESTS & LIEFERUNGEN").font = sub_font
for ri, lbl, f in [
    (21, "Tests bestanden", '=COUNTIF(Testprotokolle[Ergebnis],"bestanden")'),
    (22, "Lieferungen offen", '=COUNTIF(Logistik[Status],"offen")')]:
    lc = ws.cell(row=ri, column=5, value=lbl); lc.font = kpi_lbl; lc.alignment = left; lc.border = border
    vc = ws.cell(row=ri, column=6, value=f); vc.font = Font(name=FONT_NAME, size=12, bold=True, color=NAVY)
    vc.alignment = center; vc.border = border

# ---- Risiken (23-26)
ws.cell(row=23, column=5, value="STOPP-PUNKTE & RISIKEN (offen)").font = sub_font
for ri, lbl, f, fill, txt in [
    (24, "Auswirkung hoch", '=COUNTIFS(Risiken[Auswirkung],"hoch",Risiken[Status],"<>erledigt")', RED, RED_TXT),
    (25, "Auswirkung mittel", '=COUNTIFS(Risiken[Auswirkung],"mittel",Risiken[Status],"<>erledigt")', YELLOW, YELLOW_TXT),
    (26, "Auswirkung niedrig", '=COUNTIFS(Risiken[Auswirkung],"niedrig",Risiken[Status],"<>erledigt")', LIGHT, "404040")]:
    lc = ws.cell(row=ri, column=5, value=lbl); lc.font = kpi_lbl; lc.alignment = left
    lc.border = border; lc.fill = PatternFill("solid", fgColor=fill)
    vc = ws.cell(row=ri, column=6, value=f)
    vc.font = Font(name=FONT_NAME, size=12, bold=True, color=txt)
    vc.alignment = center; vc.border = border; vc.fill = PatternFill("solid", fgColor=fill)

# ---- Off-Hire-Fristen (27-29)  (WORKDAY = Mo-Fr, ohne Feiertage)
ws.cell(row=27, column=5, value="OFF-HIRE-FRISTEN (5 Arbeitstage vorher)").font = sub_font
cd_fmt = '0" Tage";"ueberfaellig";"heute"'
for ri, lbl, ende in [(28, "Loadbank (Mietende 02.11.) - melden bis", "DATE(2026,11,2)"),
                      (29, "Headloads (Mietende 11.12.) - melden bis", "DATE(2026,12,11)")]:
    lc = ws.cell(row=ri, column=5, value=lbl); lc.font = kpi_lbl; lc.alignment = left; lc.border = border
    vc = ws.cell(row=ri, column=6, value=f'=WORKDAY({ende},-5)-TODAY()')
    vc.number_format = cd_fmt; vc.font = Font(name=FONT_NAME, bold=True, color=NAVY)
    vc.alignment = center; vc.border = border
    dc = ws.cell(row=ri, column=7, value=f'=WORKDAY({ende},-5)')
    dc.number_format = "DD.MM.YYYY"; dc.font = base_font; dc.alignment = center; dc.border = border

# ---- Offene Entscheide (30-32)
ws.cell(row=30, column=5, value="OFFENE ENTSCHEIDE").font = sub_font
ec1 = ws.cell(row=31, column=5, value="offen gesamt"); ec1.font = kpi_lbl; ec1.alignment = left; ec1.border = border
v1 = ws.cell(row=31, column=6, value='=COUNTIFS(Aenderungslog[Typ],"Entscheid",Aenderungslog[Status],"offen")')
v1.font = Font(name=FONT_NAME, size=12, bold=True, color=NAVY); v1.alignment = center; v1.border = border
ec2 = ws.cell(row=32, column=5, value="davon ueberfaellig"); ec2.font = kpi_lbl; ec2.alignment = left
ec2.border = border; ec2.fill = PatternFill("solid", fgColor=RED)
v2 = ws.cell(row=32, column=6,
    value='=SUMPRODUCT((Aenderungslog[Typ]="Entscheid")*(Aenderungslog[Status]="offen")*(Aenderungslog[Termin]<>"")*(Aenderungslog[Termin]<TODAY()))')
v2.font = Font(name=FONT_NAME, size=12, bold=True, color=RED_TXT); v2.alignment = center
v2.border = border; v2.fill = PatternFill("solid", fgColor=RED)

# ---- Countdown (links, 17-22)
CD_TITLE = STAMM_END + 2             # 17
ws.cell(row=CD_TITLE, column=2, value="COUNTDOWN").font = sub_font
NX_FIRST = CD_TITLE + 9              # 26
counts = [
    ("Tage bis naechster Meilenstein", f'=IFERROR(B{NX_FIRST}-TODAY(),"")'),
    ("Tage bis Entsendefrist Aggreko (24.07.)", '=DATE(2026,7,24)-TODAY()'),
    ("Tage bis Lieferung Headloads (03.08.)", '=DATE(2026,8,3)-TODAY()'),
    ("Tage bis Mietende Loadbank (02.11.)", '=DATE(2026,11,2)-TODAY()'),
    ("Tage bis Closeout-Abgabe (30.11.)", '=DATE(2026,11,30)-TODAY()'),
]
r = CD_TITLE + 1
for lbl, f in counts:
    lc = ws.cell(row=r, column=2, value=lbl); lc.font = kpi_lbl; lc.alignment = left; lc.border = border
    vc = ws.cell(row=r, column=3, value=f); vc.number_format = cd_fmt
    vc.font = Font(name=FONT_NAME, bold=True, color=NAVY); vc.alignment = center; vc.border = border
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    ws.cell(row=r, column=4).border = border
    r += 1

# ---- Naechste 5 Meilensteine (24-30)
NX_TITLE = r + 1                     # 24
ws.cell(row=NX_TITLE, column=2, value="NAECHSTE 5 MEILENSTEINE").font = sub_font
for i, h in enumerate(["Plantermin", "Meilenstein", "Status"]):
    col = [2, 3, 5][i]
    c = ws.cell(row=NX_TITLE + 1, column=col, value=h)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
ws.merge_cells(start_row=NX_TITLE + 1, start_column=3, end_row=NX_TITLE + 1, end_column=4)
assert NX_TITLE + 2 == NX_FIRST, "Countdown-Referenz stimmt nicht mit Layout ueberein"
for k in range(1, 6):
    ri = NX_TITLE + 1 + k
    tc = ws.cell(row=ri, column=2, value=f'=IFERROR(INT(SMALL({HELP},{k})),"")')
    tc.number_format = "DD.MM.YYYY"; tc.font = base_font; tc.alignment = center; tc.border = border
    nc = ws.cell(row=ri, column=3,
        value=f'=IFERROR(INDEX(Meilensteine!$B$2:$B${MS_LAST},MATCH(SMALL({HELP},{k}),{HELP},0)),"")')
    nc.font = base_font; nc.alignment = left; nc.border = border
    ws.merge_cells(start_row=ri, start_column=3, end_row=ri, end_column=4)
    ws.cell(row=ri, column=4).border = border
    sc = ws.cell(row=ri, column=5,
        value=f'=IFERROR(INDEX(Meilensteine!$G$2:$G${MS_LAST},MATCH(SMALL({HELP},{k}),{HELP},0)),"")')
    sc.font = base_font; sc.alignment = center; sc.border = border
NX_LAST = NX_TITLE + 6               # 30

note_r = NX_LAST + 2                 # 32 (nur B:D - rechts liegt der Entscheide-Block)
nt = ws.cell(row=note_r, column=2,
    value="Werte aktualisieren sich automatisch. Farben: gruen=ok, gelb=in Arbeit, orange=Achtung, rot=kritisch.")
nt.font = small_it; nt.alignment = left_top
ws.merge_cells(start_row=note_r, start_column=2, end_row=note_r, end_column=4)
ws.row_dimensions[note_r].height = 24

# ---- Owner-Auslastung + Charts (ab 34)
OWN_TITLE = note_r + 2               # 34
ws.cell(row=OWN_TITLE, column=2, value="OFFENE AUFGABEN JE OWNER").font = sub_font
oh = ws.cell(row=OWN_TITLE + 1, column=2, value="Owner"); oh.font = hdr_font; oh.fill = hdr_fill
oh.alignment = center; oh.border = border
ch_ = ws.cell(row=OWN_TITLE + 1, column=3, value="offen"); ch_.font = hdr_font; ch_.fill = hdr_fill
ch_.alignment = center; ch_.border = border
owners = ["Burak", "Stefan", "Markus", "Ann-Kathrin", "Sarah", "Samuel", "Stephan", "Olli", "Aggreko", "DPR"]
r = OWN_TITLE + 2
for o in owners:
    lc = ws.cell(row=r, column=2, value=o); lc.font = base_font; lc.alignment = left; lc.border = border
    vc = ws.cell(row=r, column=3,
        value=f'=SUMPRODUCT(--ISNUMBER(SEARCH($B{r},Aufgaben[Owner])),--(Aufgaben[Status]<>"erledigt"))')
    vc.font = base_font; vc.alignment = center; vc.border = border
    r += 1
own_last = r - 1
ws.conditional_formatting.add(f"C{OWN_TITLE+2}:C{own_last}",
    DataBarRule(start_type='num', start_value=0, end_type='num', end_value=10, color=ORANGE))
ws.cell(row=own_last + 1, column=2,
    value="Gemeinsame Aufgaben (z. B. 'Burak / Stephan') zaehlen bei beiden Owners.").font = small_it
ws.merge_cells(start_row=own_last + 1, start_column=2, end_row=own_last + 1, end_column=4)

ws["J1"] = "Status"; ws["K1"] = "Aufgaben"
for i, (lbl, f) in enumerate([
    ("offen", '=COUNTIF(Aufgaben[Status],"offen")'),
    ("in Arbeit", '=COUNTIF(Aufgaben[Status],"in Arbeit")'),
    ("erledigt", '=COUNTIF(Aufgaben[Status],"erledigt")'),
    ("kritisch", '=COUNTIF(Aufgaben[Status],"kritisch")'),
    ("verschoben", '=COUNTIF(Aufgaben[Status],"verschoben")')], 2):
    ws.cell(row=i, column=10, value=lbl)
    ws.cell(row=i, column=11, value=f)
ws.column_dimensions["J"].hidden = True
ws.column_dimensions["K"].hidden = True

dn = DoughnutChart(holeSize=55)
dn.title = "Aufgaben nach Status"
dn.add_data(Reference(ws, min_col=11, min_row=1, max_row=6), titles_from_data=True)
dn.set_categories(Reference(ws, min_col=10, min_row=2, max_row=6))
dn.series[0].cat = AxDataSource(strRef=StrRef("'Dashboard'!$J$2:$J$6"))
dn.dataLabels = DataLabelList(showPercent=True)
dn.visible_cells_only = False
dn.height = 8; dn.width = 9
dn.series[0].data_points = [DataPoint(idx=i, spPr=GraphicalProperties(solidFill=c))
                            for i, c in enumerate([C_OFFEN, C_ARBEIT, C_ERLEDIGT, C_KRITISCH, C_VERSCH])]
ws.add_chart(dn, f"E{OWN_TITLE}")

bc = BarChart(); bc.type = "bar"
bc.title = "Offene Aufgaben je Owner"
bc.add_data(Reference(ws, min_col=3, min_row=OWN_TITLE + 1, max_row=own_last), titles_from_data=True)
bc.set_categories(Reference(ws, min_col=2, min_row=OWN_TITLE + 2, max_row=own_last))
bc.series[0].cat = AxDataSource(strRef=StrRef(f"'Dashboard'!$B${OWN_TITLE+2}:$B${own_last}"))
bc.dataLabels = DataLabelList(showVal=True)
bc.legend = None
bc.height = 8; bc.width = 11
bc.x_axis.delete = False; bc.y_axis.delete = False
bc.x_axis.tickLblPos = "nextTo"; bc.y_axis.tickLblPos = "nextTo"
bc.x_axis.axPos = "l"; bc.y_axis.axPos = "b"
bc.series[0].graphicalProperties = GraphicalProperties(solidFill=ORANGE)
ws.add_chart(bc, f"H{OWN_TITLE}")

page_setup(ws, freeze="A1", title_rows=None)
ws.print_area = f"A1:M{own_last + 12}"

# ================================================================ 2) WOCHENBERICHT (A4 hoch, druckfertig)
ws = wb.create_sheet("Wochenbericht")
ws.sheet_view.showGridLines = False
widths(ws, [3, 16, 46, 16, 16, 14])
ws["B2"] = "WOCHENBERICHT"; ws["B2"].font = title_font; ws.merge_cells("B2:F2")
ws["B3"] = "MiT-PWR-WIN-2026-001  |  DPR Construction / Vantage ZRH12 Winterthur"
ws["B3"].font = sub_font; ws.merge_cells("B3:F3")
bw = ws.cell(row=4, column=2,
    value='="Berichtswoche: KW "&WEEKNUM(TODAY(),21)&"  |  Stand: "&TEXT(TODAY(),"DD.MM.YYYY")&"  |  PL: Burak Uecoez"')
bw.font = bold_font; ws.merge_cells("B4:F4")

amp = ws.cell(row=6, column=2, value=AMPEL_FORMULA)
amp.font = Font(name=FONT_NAME, size=12, bold=True, color=WHITE); amp.alignment = center
ws.merge_cells("B6:F6")
for cc in range(2, 7): ws.cell(row=6, column=cc).border = border
for kw, fill in [("KRITISCH", RED_TXT), ("ACHTUNG", ORANGE), ("AUF KURS", GREEN_TXT)]:
    ws.conditional_formatting.add("B6",
        FormulaRule(formula=[f'ISNUMBER(SEARCH("{kw}",$B$6))'],
                    fill=PatternFill("solid", fgColor=fill)))

ws.cell(row=8, column=2, value="KENNZAHLEN").font = sub_font
kpis_b = [
    ("Aufgaben offen", '=COUNTIF(Aufgaben[Status],"offen")'),
    ("in Arbeit", '=COUNTIF(Aufgaben[Status],"in Arbeit")'),
    ("erledigt (gesamt)", '=COUNTIF(Aufgaben[Status],"erledigt")'),
    ("kritisch", '=COUNTIF(Aufgaben[Status],"kritisch")'),
    ("ueberfaellig", '=SUMPRODUCT((Aufgaben[Status]<>"erledigt")*(Aufgaben[Termin]<>"")*(Aufgaben[Termin]<TODAY()))'),
    ("davon diese Woche erledigt", '=COUNTIFS(Aufgaben[Erledigt am],">="&(TODAY()-7),Aufgaben[Erledigt am],"<="&TODAY())'),
]
r = 9
for lbl, f in kpis_b:
    lc = ws.cell(row=r, column=2, value=lbl); lc.font = kpi_lbl; lc.alignment = left; lc.border = border
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    ws.cell(row=r, column=3).border = border
    vc = ws.cell(row=r, column=4, value=f); vc.font = bold_font; vc.alignment = center; vc.border = border
    r += 1

ws.cell(row=16, column=2, value="NAECHSTE 5 MEILENSTEINE").font = sub_font
for i, h in enumerate(["Plantermin", "Meilenstein", "Status"]):
    col = [2, 3, 4][i]
    c = ws.cell(row=17, column=col, value=h)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
for k in range(1, 6):
    ri = 17 + k
    tc = ws.cell(row=ri, column=2, value=f'=IFERROR(INT(SMALL({HELP},{k})),"")')
    tc.number_format = "DD.MM.YYYY"; tc.font = base_font; tc.alignment = center; tc.border = border
    nc = ws.cell(row=ri, column=3,
        value=f'=IFERROR(INDEX(Meilensteine!$B$2:$B${MS_LAST},MATCH(SMALL({HELP},{k}),{HELP},0)),"")')
    nc.font = base_font; nc.alignment = left; nc.border = border
    sc = ws.cell(row=ri, column=4,
        value=f'=IFERROR(INDEX(Meilensteine!$G$2:$G${MS_LAST},MATCH(SMALL({HELP},{k}),{HELP},0)),"")')
    sc.font = base_font; sc.alignment = center; sc.border = border
status_cf(ws, "D", 18, 22)

ws.cell(row=24, column=2, value="OFFENE STOPP-PUNKTE & RISIKEN (Auswirkung hoch)").font = sub_font
RH = "'Stopp-Punkte & Risiken'"
for k in range(1, 7):
    ri = 24 + k
    f = (f'=IFERROR(INDEX({RH}!$C$1:$C$50,SMALL({RH}!$K$2:$K$40,{k}))&"   ["&'
         f'INDEX({RH}!$F$1:$F$50,SMALL({RH}!$K$2:$K$40,{k}))&", bis "&'
         f'TEXT(INDEX({RH}!$G$1:$G$50,SMALL({RH}!$K$2:$K$40,{k})),"DD.MM.")&"]","")')
    c = ws.cell(row=ri, column=2, value=f); c.font = base_font; c.alignment = left; c.border = border
    ws.merge_cells(start_row=ri, start_column=2, end_row=ri, end_column=6)
    for cc in range(3, 7): ws.cell(row=ri, column=cc).border = border

ws.cell(row=32, column=2, value="OFFENE ENTSCHEIDE").font = sub_font
LG = "'Aenderungslog & Entscheide'"
for k in range(1, 5):
    ri = 32 + k
    f = (f'=IFERROR(INDEX({LG}!$D$1:$D$60,SMALL({LG}!$H$2:$H$40,{k}))&"   ["&'
         f'INDEX({LG}!$B$1:$B$60,SMALL({LG}!$H$2:$H$40,{k}))&"]","")')
    c = ws.cell(row=ri, column=2, value=f); c.font = base_font; c.alignment = left; c.border = border
    ws.merge_cells(start_row=ri, start_column=2, end_row=ri, end_column=6)
    for cc in range(3, 7): ws.cell(row=ri, column=cc).border = border

ws.cell(row=38, column=2, value="OFF-HIRE-FRISTEN").font = sub_font
oh1 = ws.cell(row=39, column=2,
    value='="Loadbank: Off-Hire melden bis "&TEXT(WORKDAY(DATE(2026,11,2),-5),"DD.MM.YYYY")&" (noch "&(WORKDAY(DATE(2026,11,2),-5)-TODAY())&" Tage)"')
oh1.font = base_font; ws.merge_cells("B39:F39")
oh2 = ws.cell(row=40, column=2,
    value='="Headloads: Off-Hire melden bis "&TEXT(WORKDAY(DATE(2026,12,11),-5),"DD.MM.YYYY")&" (noch "&(WORKDAY(DATE(2026,12,11),-5)-TODAY())&" Tage)"')
oh2.font = base_font; ws.merge_cells("B40:F40")

ws.cell(row=42, column=2, value="FORTSCHRITT DIESE WOCHE (manuell ausfuellen)").font = sub_font
for ri in range(43, 47):
    ws.merge_cells(start_row=ri, start_column=2, end_row=ri, end_column=6)
    for cc in range(2, 7): ws.cell(row=ri, column=cc).border = border
ws.cell(row=48, column=2, value="PROBLEME & NAECHSTE SCHRITTE (manuell ausfuellen)").font = sub_font
for ri in range(49, 53):
    ws.merge_cells(start_row=ri, start_column=2, end_row=ri, end_column=6)
    for cc in range(2, 7): ws.cell(row=ri, column=cc).border = border
ws.cell(row=54, column=2,
    value="Als PDF exportieren (Datei > Exportieren) und an DPR senden. Enthaelt KEINE EUR-Einkaufspreise.").font = small_it
ws.merge_cells("B54:F54")
page_setup(ws, freeze="A1", title_rows=None)
ws.page_setup.orientation = "portrait"
ws.print_area = "A1:F55"

# ================================================================ 3) TERMINPLAN (WOCHEN-GANTT)
ws = wb.create_sheet("Terminplan")
ws.sheet_view.showGridLines = False
week_starts = []
wk = datetime.datetime(2026, 7, 13)
while wk <= datetime.datetime(2026, 12, 28):
    week_starts.append(wk)
    wk += timedelta(days=7)
NW = len(week_starts)
FIRST_WK_COL = 5
LAST_WK_COL = FIRST_WK_COL + NW - 1
LAST_LETTER = get_column_letter(LAST_WK_COL)

widths(ws, [5, 38, 12, 12] + [4.2] * NW)
ws["A1"] = "TERMINPLAN 2026 - Wochenraster (KW 29-53)"
ws["A1"].font = sub_font
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=10)
for i, h in enumerate(["Nr.", "Phase / Meilenstein", "Start / Termin", "Ende / Status"]):
    c = ws.cell(row=2, column=1 + i, value=h)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
    ws.merge_cells(start_row=2, start_column=1 + i, end_row=3, end_column=1 + i)
    ws.cell(row=3, column=1 + i).border = border
for i, wkd in enumerate(week_starts):
    c1 = ws.cell(row=2, column=FIRST_WK_COL + i, value="KW%d" % wkd.isocalendar()[1])
    c1.font = Font(name=FONT_NAME, size=7, bold=True, color=WHITE)
    c1.fill = hdr_fill; c1.alignment = center; c1.border = border
    c2 = ws.cell(row=3, column=FIRST_WK_COL + i, value=wkd)
    c2.number_format = "DD.MM."
    c2.font = Font(name=FONT_NAME, size=7, color=WHITE)
    c2.fill = hdr_fill; c2.alignment = center; c2.border = border

phasen = [
    ("Vertraege & Compliance", D(7,16), D(7,28)),
    ("Projektvorbereitung & Mobilisierung", D(7,16), D(8,3)),
    ("Heat-Load (Headloads) - Miete", D(8,3), D(12,11)),
    ("Loadbank 6 MVA - Miete", D(8,17), D(11,2)),
    ("Testphase / Inbetriebnahme", D(8,3), D(11,2)),
    ("3-MW-Block (Abruf)", D(8,14), D(9,7)),
    ("5-MW-Block (Abruf)", D(9,8), D(9,30)),
    ("Demontage", D(12,14), D(12,14)),
    ("Closeout & Dokumentation", D(11,30), D(12,31)),
]
P0 = 4
r = P0
for i, (name, s, e) in enumerate(phasen, 1):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2, value=name)
    cs = ws.cell(row=r, column=3, value=s); cs.number_format = "DD.MM.YYYY"
    ce = ws.cell(row=r, column=4, value=e); ce.number_format = "DD.MM.YYYY"
    r += 1
P1 = r - 1
body(ws, P0, P1, 4)
for rr in range(P0, P1 + 1):
    ws.cell(row=rr, column=1).alignment = center
    ws.cell(row=rr, column=3).alignment = center
    ws.cell(row=rr, column=4).alignment = center
    for cc in range(FIRST_WK_COL, LAST_WK_COL + 1):
        ws.cell(row=rr, column=cc).border = border

sec = P1 + 2
sc_ = ws.cell(row=sec, column=1, value="MEILENSTEINE  (◆ = Termin in dieser Woche)")
sc_.font = Font(name=FONT_NAME, size=10, bold=True, color=WHITE); sc_.fill = hdr_fill
sc_.alignment = left
ws.merge_cells(start_row=sec, start_column=1, end_row=sec, end_column=LAST_WK_COL)
M0 = sec + 1
r = M0
for i in range(N_MS):
    msrow = 2 + i
    ws.cell(row=r, column=1, value=f"=Meilensteine!$A${msrow}")
    ws.cell(row=r, column=2, value=f"=Meilensteine!$B${msrow}")
    dc = ws.cell(row=r, column=3, value=f"=Meilensteine!$D${msrow}")
    dc.number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=4, value=f"=Meilensteine!$G${msrow}")
    for j in range(NW):
        cl = get_column_letter(FIRST_WK_COL + j)
        cell = ws.cell(row=r, column=FIRST_WK_COL + j,
            value=f'=IF(AND(Meilensteine!$D${msrow}>={cl}$3,Meilensteine!$D${msrow}<{cl}$3+7),"◆","")')
        cell.font = diamond_f; cell.alignment = center; cell.border = border
    r += 1
M1 = r - 1
body(ws, M0, M1, 4)
for rr in range(M0, M1 + 1):
    ws.cell(row=rr, column=1).alignment = center
    ws.cell(row=rr, column=3).alignment = center
    ws.cell(row=rr, column=4).alignment = center
    for cc in range(FIRST_WK_COL, LAST_WK_COL + 1):
        c = ws.cell(row=rr, column=cc); c.font = diamond_f; c.alignment = center; c.border = border

ws.conditional_formatting.add(f"E{P0}:{LAST_LETTER}{P1}",
    FormulaRule(formula=['AND(E$3<=$D4,E$3+6>=$C4,$C4<>"")'],
                fill=PatternFill("solid", fgColor=ORANGE)))
ws.conditional_formatting.add(f"E{P0}:{LAST_LETTER}{M1}",
    FormulaRule(formula=['AND(TODAY()>=E$3,TODAY()<E$3+7)'],
                fill=PatternFill("solid", fgColor=TODAY_TINT)))
status_cf(ws, "D", M0, M1)
leg = ws.cell(row=M1 + 2, column=2,
    value="◆ = Meilenstein-Termin  |  oranger Balken = aktive Phase  |  "
          "blau hinterlegte Spalte = aktuelle Woche. Zeitachse: Montag der jeweiligen KW.")
leg.font = small_it
ws.merge_cells(start_row=M1 + 2, start_column=2, end_row=M1 + 2, end_column=LAST_WK_COL)
page_setup(ws, freeze="E4", title_rows="2:3")

# ================================================================ 4) MEILENSTEINE
ws = wb.create_sheet("Meilensteine")
cols = ["Nr.", "Meilenstein", "Phase", "Plantermin", "KW", "Ist-Termin", "Status",
        "Verantwortlich", "Countdown (Tage)", "Vorgaenger (Nr.)", "Bemerkung"]
widths(ws, [6, 42, 13, 15, 8, 13, 12, 19, 11, 11, 30])
header_row(ws, 1, cols)
r = 2
for i, (name, phase, term, verant, vorg, bem) in enumerate(MS, 1):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=phase)
    tc = ws.cell(row=r, column=4, value=term)
    tc.number_format = "DD.MM.YYYY" if term.hour == 0 else "DD.MM.YYYY hh:mm"
    ws.cell(row=r, column=5, value=f'=IF($D{r}="","","KW "&WEEKNUM($D{r},21))')
    ws.cell(row=r, column=6).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=7, value="offen")
    ws.cell(row=r, column=8, value=verant)
    cd = ws.cell(row=r, column=9,
        value=f'=IF($G{r}="erledigt","✔",IF($D{r}="","",INT($D{r})-TODAY()))')
    cd.number_format = '0" Tg";-0" Tg"'
    ws.cell(row=r, column=10, value=vorg)
    ws.cell(row=r, column=11, value=bem)
    # Hilfsspalte L: eindeutiger Termin fuer Dashboard/Wochenbericht
    ws.cell(row=r, column=12,
        value=f'=IF(AND($G{r}<>"erledigt",$D{r}<>"",$D{r}>=TODAY()),$D{r}+ROW()/10000,"")')
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 4, 5, 6, 7, 9, 10):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Meilensteine", 1, last, len(cols))
add_dv(ws, "Vorbereitung,Ausfuehrung,Abschluss", f"C2:C{last}")
add_dv(ws, STATUS_LIST, f"G2:G{last}")
add_dv(ws, OWNER_LIST, f"H2:H{last}")
status_cf(ws, "G", 2, last)
for val, fill in [("Vorbereitung", LIGHT), ("Ausfuehrung", ORANGE_FILL), ("Abschluss", GREY)]:
    ws.conditional_formatting.add(f"C2:C{last}", CellIsRule(operator="equal", formula=[f'"{val}"'],
        fill=PatternFill("solid", fgColor=fill)))
ws.conditional_formatting.add(f"D2:D{last}",
    FormulaRule(formula=['AND($D2<TODAY(),$G2<>"erledigt",$D2<>"")'],
                fill=PatternFill("solid", fgColor=ORANGE_FILL), font=Font(name=FONT_NAME, color=ORANGE_TXT)))
ws.conditional_formatting.add(f"I2:I{last}", CellIsRule(operator="lessThanOrEqual", formula=["3"],
    fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, bold=True, color=RED_TXT)))
ws.conditional_formatting.add(f"I2:I{last}", CellIsRule(operator="lessThanOrEqual", formula=["10"],
    fill=PatternFill("solid", fgColor=ORANGE_FILL), font=Font(name=FONT_NAME, color=ORANGE_TXT)))
# Abhaengigkeits-Warnung: Vorgaenger kritisch/verschoben -> Name + Vorgaenger-Zelle markieren
dep_rule = (f'AND($J2<>"",IFERROR(OR(INDEX($G$2:$G${last},MATCH($J2,$A$2:$A${last},0))="kritisch",'
            f'INDEX($G$2:$G${last},MATCH($J2,$A$2:$A${last},0))="verschoben"),FALSE))')
for colrange in (f"B2:B{last}", f"J2:J{last}"):
    ws.conditional_formatting.add(colrange,
        FormulaRule(formula=[dep_rule], fill=PatternFill("solid", fgColor=RED),
                    font=Font(name=FONT_NAME, bold=True, color=RED_TXT)))
ws.column_dimensions["L"].hidden = True
ws.cell(row=1, column=12, value="(Hilfsspalte)").font = small_it
page_setup(ws, freeze="A2")

# ================================================================ 5) AUFGABEN
ws = wb.create_sheet("Aufgaben")
cols = ["Nr.", "Aufgabe", "Paket", "Owner", "Termin", "Status", "Prioritaet", "Bemerkung", "Erledigt am"]
widths(ws, [6, 52, 12, 18, 14, 13, 12, 36, 14])
header_row(ws, 1, cols)
au = [
    ("Versicherungsnachweis via Finance beschaffen", "Admin", "Markus", D(7,16), "hoch", ""),
    ("Zollprozess DE-CH schriftlich klaeren (Kostentraeger; Equipment voruebergehende Verwendung vs. Kraftstoff definitive Einfuhr)", "Admin", "Markus", D(7,17), "hoch", ""),
    ("Deckungssummen bei Roxana Minor erfragen", "Admin", "Markus", D(7,17), "mittel", ""),
    ("HR-Auszug nachfassen", "Admin", "Ann-Kathrin", D(7,16), "hoch", ""),
    ("Beide Angebote im MiT-Layout aufbereiten", "beide", "Ann-Kathrin", D(7,17), "mittel", "P-640380-3 / P-650395-2"),
    ("WORKcontrol-Registrierung MiT", "Admin", "Ann-Kathrin", D(7,24), "hoch", "vor Badges; CHF 25/Person Erstanmeldung"),
    ("Versand Gesamtpaket an Roxana Minor (Tanya cc)", "Admin", "Ann-Kathrin", D(7,16,12,0), "hoch", ""),
    ("Unterschriften leisten (Diessenhofen)", "Admin", "Stefan", D(7,16), "hoch", "Donnerstag nachmittags"),
    ("Entscheid EUR/CHF-Kurs und Absicherung mit Olli", "Admin", "Stefan", D(7,17), "hoch", "FX-Risiko"),
    ("Verhandlungslinie Korrekturliste festlegen", "beide", "Stefan", D(7,17), "hoch", ""),
    ("bSuite-Anlage + Intercompany-Beauftragung Aggreko (Back-to-Back)", "beide", "Sarah", D(7,16), "hoch", ""),
    ("RAMS-Praxischeck: Anlieferung/8-t-Kranhub, Installation, Testbetrieb, Betankung/Leckage, Demobilisierung", "beide", "Samuel", D(7,20), "hoch", "5 Taetigkeiten, Hammertech"),
    ("PO-Korrekturliste erstellen und einreichen", "beide", "Burak / Stephan", D(7,17), "hoch", "49A 78/110 Tage; 49B 131/110 Tage"),
    ("Schriftliche Aggreko-Terminbestaetigung 03.08. / 17.08. einholen", "beide", "Burak", D(7,20), "hoch", ""),
    ("Staffelungs-Fakturierung klaeren (5-MW-Block ab Abruf oder Mietbeginn?)", "beide", "Burak", D(7,24), "mittel", ""),
    ("PL-Benennung Aggreko DE + englischsprachiger Supervisor", "beide", "Burak", D(7,20), "mittel", ""),
    ("Schwerlast-Strombedarf bei DPR einreichen", "beide", "Burak", D(7,24), "hoch", "Monatsfrist laeuft"),
    ("NDA MiT-DPR anstossen", "Admin", "Burak", D(7,17), "hoch", "eigene NDA; vor Unterzeichnung 22.07."),
    ("Kranfrage / Lift Plan / Rigger klaeren", "beide", "Burak", D(7,28), "mittel", ""),
    ("24/7-Kontaktkette beidseitig aufstellen", "beide", "Burak", D(7,31), "mittel", "vor Lieferung 03.08.; 01.08. = Bundesfeier"),
    ("Tank-Standort mit 110%-Auffangwanne im Logistikplan festlegen", "Headload", "Burak", D(7,30), "hoch", ""),
    ("Haftpflichtnachweis Aggreko einfordern", "Admin", "Burak", D(7,21), "hoch", ""),
    ("Long-Lead-Liste vorbereiten", "beide", "Burak", D(7,23), "hoch", "3-Tage-Frist ab Vertragsunterzeichnung!"),
    ("Winterbetrieb ab Oktober in Offerte aufnehmen", "beide", "Burak", D(7,22), "mittel", ""),
]
r = 2
for i, (name, pk, ow, term, prio, bem) in enumerate(au, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=pk); ws.cell(row=r, column=4, value=ow)
    tc = ws.cell(row=r, column=5, value=term)
    tc.number_format = "DD.MM.YYYY" if term.hour == 0 else "DD.MM.YYYY hh:mm"
    ws.cell(row=r, column=6, value="offen"); ws.cell(row=r, column=7, value=prio)
    ws.cell(row=r, column=8, value=bem); ws.cell(row=r, column=9).number_format = "DD.MM.YYYY"
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 5, 6, 7, 9):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Aufgaben", 1, last, len(cols))
add_dv(ws, "Loadbank,Headload,beide,Admin", f"C2:C{last}")
add_dv(ws, OWNER_LIST, f"D2:D{last}")
add_dv(ws, STATUS_LIST, f"F2:F{last}")
add_dv(ws, "hoch,mittel,niedrig", f"G2:G{last}")
status_cf(ws, "F", 2, last)
ws.conditional_formatting.add(f"G2:G{last}", CellIsRule(operator="equal", formula=['"hoch"'],
    font=Font(name=FONT_NAME, bold=True, color=ORANGE)))
ws.conditional_formatting.add(f"E2:E{last}",
    FormulaRule(formula=['AND($E2<TODAY(),$F2<>"erledigt",$E2<>"")'],
                fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, color=RED_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 6) TERMINE & MEETINGS
ws = wb.create_sheet("Termine & Meetings")
cols = ["Nr.", "Meeting", "Rhythmus", "Dauer", "Teilnahmepflicht", "Status", "Bemerkung"]
widths(ws, [6, 34, 20, 10, 34, 13, 28])
header_row(ws, 1, cols)
meet = [
    ("Kickoff-Meeting DPR", "einmalig (vor 03.08.)", "2 h", "PL, Foreman, Safety Manager (Pflicht)", "aus Supplemental Conditions r2"),
    ("Safety Orientation", "einmalig je Person", "1 h", "alle vor Ort Taetigen", "vor erstem Zutritt"),
    ("Subcontractor Progress Meeting", "woechentlich", "1 h", "PL", ""),
    ("BIM-Meeting", "woechentlich", "2 h", "nach Anforderung DPR", ""),
    ("EHS-Meeting", "woechentlich", "1 h", "Safety / PL", ""),
    ("Pull Planning", "woechentlich", "2 h", "PL / Foreman", ""),
    ("DABS (Daily Activity Briefing)", "taeglich", "30 Min", "Crew vor Ort", ""),
    ("Long-Lead-Status-Reporting", "14-taeglich", "-", "PL", "Bericht an DPR (siehe Wochenbericht)"),
    ("Record Drawings", "monatlich", "-", "PL", "Stand der Dokumentation"),
]
r = 2
for i, (name, rhy, dur, pflicht, bem) in enumerate(meet, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=rhy); ws.cell(row=r, column=4, value=dur)
    ws.cell(row=r, column=5, value=pflicht); ws.cell(row=r, column=6, value="offen")
    ws.cell(row=r, column=7, value=bem)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 4, 6):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Meetings", 1, last, len(cols))
add_dv(ws, "offen,geplant,laufend,erledigt", f"F2:F{last}")
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"erledigt"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"laufend"'],
    fill=PatternFill("solid", fgColor=YELLOW), font=Font(name=FONT_NAME, color=YELLOW_TXT)))
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"geplant"'],
    fill=PatternFill("solid", fgColor=LIGHT)))
page_setup(ws, freeze="A2")

# ================================================================ 7) PERSONAL & ZUTRITT
ws = wb.create_sheet("Personal & Zutritt")
cols = ["Nr.", "Name", "Firma", "Funktion", "Entsendemeldung", "WORKcontrol-Ausweis (Status/Nr.)",
        "Site Induction", "Status", "Bemerkung"]
widths(ws, [6, 26, 12, 22, 16, 22, 15, 13, 30])
header_row(ws, 1, cols)
pers = [
    ("Uecoez, Burak", "MiT", "Projektleiter", "n.a.", "n.a.", None, "in Arbeit", "Gesamtkoordination"),
    ("N.N. (PL Aggreko DE)", "Aggreko", "Projektleiter", "offen", "offen", None, "offen", "Benennung ausstehend"),
    ("N.N. Supervisor (englischsprachig)", "Aggreko", "Supervisor", "offen", "offen", None, "offen", "Anforderung DPR"),
    ("N.N. Servicetechniker 1", "Aggreko", "Techniker", "offen", "offen", None, "offen", "Entsendefrist 24.07."),
    ("N.N. Servicetechniker 2", "Aggreko", "Techniker", "offen", "offen", None, "offen", "Entsendefrist 24.07."),
    ("N.N. Servicetechniker 3", "Aggreko", "Techniker", "offen", "offen", None, "offen", "Entsendefrist 24.07."),
    ("N.N. Servicetechniker 4", "Aggreko", "Techniker", "offen", "offen", None, "offen", "Entsendefrist 24.07."),
    ("N.N. DPR Site Contact", "DPR", "Bauleitung", "n.a.", "n.a.", None, "offen", "Ansprechpartner vor Ort"),
]
r = 2
for i, (name, firma, rolle, ents, badge, indu, stat, bem) in enumerate(pers, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=firma); ws.cell(row=r, column=4, value=rolle)
    ws.cell(row=r, column=5, value=ents); ws.cell(row=r, column=6, value=badge)
    ws.cell(row=r, column=7, value=indu).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=8, value=stat); ws.cell(row=r, column=9, value=bem)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 5, 6, 7, 8):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Personal", 1, last, len(cols))
add_dv(ws, "Aggreko,MiT,DPR", f"C2:C{last}")
add_dv(ws, "offen,eingereicht,bestaetigt,n.a.", f"E2:E{last}")
add_dv(ws, "offen,beantragt,erhalten,n.a.", f"F2:F{last}")
add_dv(ws, "offen,in Arbeit,bereit", f"H2:H{last}")
for col in ("E", "F"):
    ws.conditional_formatting.add(f"{col}2:{col}{last}", CellIsRule(operator="equal", formula=['"offen"'],
        fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, color=RED_TXT)))
    ws.conditional_formatting.add(f"{col}2:{col}{last}", CellIsRule(operator="equal", formula=['"bestaetigt"'],
        fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
    ws.conditional_formatting.add(f"{col}2:{col}{last}", CellIsRule(operator="equal", formula=['"erhalten"'],
        fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.conditional_formatting.add(f"H2:H{last}", CellIsRule(operator="equal", formula=['"bereit"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
hint = ws.cell(row=last + 2, column=2,
    value="WICHTIG: Frist Entsendemeldung 24.07. (gesetzlich spaetestens 26.07.). "
          "Ohne validierten WORKcontrol-Ausweis kein Zutritt. Kosten CHF 25/Person Erstanmeldung.")
hint.font = Font(name=FONT_NAME, size=9, bold=True, color=RED_TXT)
ws.merge_cells(start_row=last + 2, start_column=2, end_row=last + 2, end_column=9)
page_setup(ws, freeze="A2")

# ================================================================ 8) SCHICHTPLAN
ws = wb.create_sheet("Schichtplan")
cols = ["Nr.", "Datum", "KW", "Name", "Firma", "Funktion", "Von", "Bis", "Vor Ort", "Bemerkung"]
widths(ws, [6, 14, 9, 26, 12, 20, 9, 9, 10, 30])
header_row(ws, 1, cols)
r = 2
for i in range(1, 21):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=3, value=f'=IF($B{r}="","","KW "&WEEKNUM($B{r},21))')
    ws.cell(row=r, column=7).number_format = "hh:mm"
    ws.cell(row=r, column=8).number_format = "hh:mm"
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 2, 3, 5, 7, 8, 9):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Schichtplan", 1, last, len(cols))
add_dv(ws, "Aggreko,MiT,DPR", f"E2:E{last}")
add_dv(ws, "ja,nein", f"I2:I{last}")
ws.conditional_formatting.add(f"I2:I{last}", CellIsRule(operator="equal", formula=['"ja"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.cell(row=last + 2, column=2,
    value="Anwesenheit vor Ort je Tag erfassen (DABS-Pflicht, 24/7-Kette siehe Kontakte). KW berechnet sich automatisch.").font = small_it
ws.merge_cells(start_row=last + 2, start_column=2, end_row=last + 2, end_column=10)
page_setup(ws, freeze="A2")

# ================================================================ 9) LIEFERUNGEN & LOGISTIK
ws = wb.create_sheet("Lieferungen & Logistik")
cols = ["Nr.", "Lieferung / Gegenstand", "Paket", "Anlieferung geplant", "Ort",
        "Kran/Lift", "Tank/Containment", "Verantwortlich", "Status", "Bemerkung"]
widths(ws, [6, 30, 12, 18, 22, 12, 18, 15, 13, 28])
header_row(ws, 1, cols)
logi = [
    ("Headloads (54x 200 kW)", "Headload", D(8,3), "ZRH12 Winterthur", "ja", "-", "Aggreko", "offen", "Lift Plan + Rigger; 8-t-Kranhub"),
    ("Loadbank 6 MVA", "Loadbank", D(8,17), "ZRH12 Winterthur", "ja", "-", "Aggreko", "offen", "Kranfrage klaeren"),
    ("Tank / Betankung", "Headload", "vor Testbeginn", "ZRH12 Winterthur", "nein", "110%-Auffangwanne", "Burak", "offen", "Standort im Logistikplan Rev. C04"),
    ("Kabel- & Anschlussmaterial", "beide", "vor Testbeginn", "ZRH12 Winterthur", "nein", "-", "Aggreko", "offen", ""),
    ("Ruecktransport Loadbank", "Loadbank", D(11,2), "ab ZRH12", "ja", "-", "Aggreko", "offen", "Off-Hire 5 Arbeitstage vorher melden"),
    ("Ruecktransport Headloads", "Headload", D(12,11), "ab ZRH12", "ja", "-", "Aggreko", "offen", "Off-Hire 5 Arbeitstage vorher melden"),
    ("Demontage & Abtransport", "beide", D(12,14), "ZRH12 Winterthur", "ja", "-", "Aggreko", "offen", ""),
]
r = 2
for i, (geg, pk, dat, ort, kran, tank, verant, stat, bem) in enumerate(logi, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=geg)
    ws.cell(row=r, column=3, value=pk)
    dc = ws.cell(row=r, column=4, value=dat)
    if isinstance(dat, datetime.datetime): dc.number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=5, value=ort); ws.cell(row=r, column=6, value=kran)
    ws.cell(row=r, column=7, value=tank); ws.cell(row=r, column=8, value=verant)
    ws.cell(row=r, column=9, value=stat); ws.cell(row=r, column=10, value=bem)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 4, 6, 8, 9):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Logistik", 1, last, len(cols))
add_dv(ws, "Loadbank,Headload,beide", f"C2:C{last}")
add_dv(ws, "ja,nein,offen", f"F2:F{last}")
add_dv(ws, "Burak,Markus,Aggreko,DPR,MiT", f"H2:H{last}")
add_dv(ws, "offen,geplant,geliefert,zurueck,verschoben", f"I2:I{last}")
for val, fill, txt in [("geliefert", GREEN, GREEN_TXT), ("zurueck", GREEN, GREEN_TXT),
                       ("verschoben", ORANGE_FILL, ORANGE_TXT), ("geplant", YELLOW, YELLOW_TXT)]:
    ws.conditional_formatting.add(f"I2:I{last}", CellIsRule(operator="equal", formula=[f'"{val}"'],
        fill=PatternFill("solid", fgColor=fill), font=Font(name=FONT_NAME, color=txt)))
page_setup(ws, freeze="A2")

# ================================================================ 10) TESTPROTOKOLLE
ws = wb.create_sheet("Testprotokolle")
cols = ["Nr.", "Test / Messung", "Paket", "Datum", "Sollwert", "Istwert", "Einheit",
        "Ergebnis", "Pruefer", "Foto/Nachweis", "Bemerkung"]
widths(ws, [6, 34, 12, 13, 11, 11, 9, 15, 13, 13, 26])
header_row(ws, 1, cols)
tests = [
    ("Sichtpruefung & Anschlusskontrolle", "Loadbank", "i.O.", "-"),
    ("Isolationspruefung", "Loadbank", "", "MOhm"),
    ("Lastschritt 25% (1.5 MVA)", "Loadbank", 1.5, "MVA"),
    ("Lastschritt 50% (3.0 MVA)", "Loadbank", 3.0, "MVA"),
    ("Lastschritt 75% (4.5 MVA)", "Loadbank", 4.5, "MVA"),
    ("Lastschritt 100% (6.0 MVA)", "Loadbank", 6.0, "MVA"),
    ("Frequenzstabilitaet", "Loadbank", 50, "Hz"),
    ("Sichtpruefung Headloads", "Headload", "i.O.", "-"),
    ("Lastschritt 2 MW", "Headload", 2.0, "MW"),
    ("Lastschritt 3 MW (Abruf-Block)", "Headload", 3.0, "MW"),
    ("Lastschritt 4 MW", "Headload", 4.0, "MW"),
    ("Lastschritt 5 MW (Abruf-Block)", "Headload", 5.0, "MW"),
    ("Lastschritt 6 MW", "Headload", 6.0, "MW"),
    ("Lastschritt 8 MW (Volllast)", "Headload", 8.0, "MW"),
    ("Waermeabfuhr-Nachweis (Dauerlauf)", "Headload", "-", "-"),
    ("Not-Aus / Sicherheitskette", "beide", "i.O.", "-"),
]
r = 2
for i, (name, pk, soll, einh) in enumerate(tests, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=pk)
    ws.cell(row=r, column=4).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=5, value=soll)
    ws.cell(row=r, column=6, value=None)
    ws.cell(row=r, column=7, value=einh)
    ws.cell(row=r, column=8, value="offen")
    ws.cell(row=r, column=9, value="")
    ws.cell(row=r, column=10, value="offen")
    ws.cell(row=r, column=11, value="")
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 4, 5, 6, 7, 8, 9, 10):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Testprotokolle", 1, last, len(cols))
add_dv(ws, "Loadbank,Headload,beide", f"C2:C{last}")
add_dv(ws, "bestanden,nicht bestanden,offen,n.a.", f"H2:H{last}")
add_dv(ws, "Samuel,Burak,Aggreko,MiT,DPR", f"I2:I{last}")
add_dv(ws, "ja,nein,offen", f"J2:J{last}")
ws.conditional_formatting.add(f"H2:H{last}", CellIsRule(operator="equal", formula=['"bestanden"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.conditional_formatting.add(f"H2:H{last}", CellIsRule(operator="equal", formula=['"nicht bestanden"'],
    fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, color=RED_TXT)))
ws.conditional_formatting.add(f"J2:J{last}", CellIsRule(operator="equal", formula=['"ja"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.cell(row=last + 2, column=2,
    value="Istwerte, Datum, Pruefer und Foto-Nachweis vor Ort eintragen. Ergebnis = Basis fuer das Closeout-Paket. Keine Fotos nach aussen (NDA).").font = small_it
ws.merge_cells(start_row=last + 2, start_column=2, end_row=last + 2, end_column=11)
page_setup(ws, freeze="A2")

# ================================================================ 11) FUEL-LOG
ws = wb.create_sheet("Fuel-Log")
cols = ["Nr.", "Datum", "Menge (Liter)", "Lieferschein-Nr.", "Zoll-Kategorie",
        "Auffangwanne geprueft", "Erfasst von", "Bemerkung"]
widths(ws, [6, 14, 14, 18, 20, 18, 14, 34])
header_row(ws, 1, cols)
r = 2
for i in range(1, 16):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=3).number_format = "#'##0\" l\""
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 2, 3, 4, 5, 6, 7):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "FuelLog", 1, last, len(cols))
add_dv(ws, "definitive Einfuhr,Rueckfuhr", f"E2:E{last}")
add_dv(ws, "ja,nein", f"F2:F{last}")
add_dv(ws, "Burak,Samuel,Aggreko,MiT", f"G2:G{last}")
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"nein"'],
    fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, bold=True, color=RED_TXT)))
tl = ws.cell(row=last + 2, column=2, value="Total Liter"); tl.font = bold_font
ts = ws.cell(row=last + 2, column=3, value="=SUM(FuelLog[Menge (Liter)])")
ts.font = bold_font; ts.number_format = "#'##0\" l\""; ts.border = border
ws.cell(row=last + 3, column=2,
    value="Kraftstoff = definitive Einfuhr (Zoll!). Fuel Unreturned wird mit EUR 2.20/l belastet. "
          "Betankung nur am Standort mit 110%-Auffangwanne.").font = small_it
ws.merge_cells(start_row=last + 3, start_column=2, end_row=last + 3, end_column=8)
page_setup(ws, freeze="A2")

# ================================================================ 12) STOPP-PUNKTE & RISIKEN
ws = wb.create_sheet("Stopp-Punkte & Risiken")
cols = ["Nr.", "Typ", "Beschreibung", "Auswirkung", "Wahrscheinlichkeit", "Owner", "Termin", "Status", "Massnahme"]
widths(ws, [6, 14, 50, 12, 15, 16, 13, 12, 40])
header_row(ws, 1, cols)
rk = [
    ("Stopp-Punkt", "PO 49A: 78 statt 110 Tage berechnet, Differenz ca. EUR 87'700", "hoch", "hoch", "Burak", D(7,17), "Korrekturliste an DPR mit korrigierter Tagesberechnung"),
    ("Stopp-Punkt", "PO 49B: 131 statt 110 Tage, Vertragsende 02.11. falsch, englische Anlagenliste nennt falsches Angebot", "hoch", "hoch", "Burak", D(7,17), "Korrekturliste an DPR; Anlagenliste ersetzen"),
    ("Stopp-Punkt", "Parteien auf MiT AG umschreiben + eigene NDA; DPR-Entitaet AG vs. GmbH klaeren", "hoch", "hoch", "Stefan / Stephan", D(7,20), "PO-Parteien anpassen, NDA MiT-DPR anstossen"),
    ("Entscheid", "Festpreis DPR vs. Aufwandspreise Aggreko (Transport/Techniker)", "hoch", "mittel", "Stefan", D(7,20), "Preismodell final abstimmen; Puffer einrechnen"),
    ("Stopp-Punkt", "Preisformel in POs nennt nur Tagesmiete, Total enthaelt aber Einmalkosten", "mittel", "hoch", "Burak", D(7,17), "In Korrekturliste aufnehmen"),
    ("Risiko", "FX-Risiko EUR-Einkauf vs. CHF-Verkauf", "mittel", "mittel", "Stefan", D(7,17), "Kurs/Absicherung mit Olli entscheiden"),
    ("Risiko", "Keine schriftliche Aggreko-Terminbestaetigung 03.08. / 17.08.", "hoch", "mittel", "Burak", D(7,20), "Schriftliche Bestaetigung einholen"),
    ("Risiko", "Hochsaison-Verfuegbarkeit Equipment/Personal Aggreko", "mittel", "mittel", "Aggreko", D(7,20), "Fruehzeitige Fixierung, Terminbestaetigung"),
    ("Risiko", "Entsende-/Bewilligungsfristen (24.07., gesetzlich 26.07.)", "hoch", "mittel", "Aggreko", D(7,24), "Entsendemeldung fristgerecht einreichen"),
    ("Stopp-Punkt", "Waermeabfuhr 8 MW als DPR-Verantwortung schriftlich fixieren", "hoch", "mittel", "DPR", D(7,24), "Schriftliche Bestaetigung DPR einholen"),
    ("Risiko", "DPR-Kuendigungsrecht jederzeit kostenlos vs. Aggreko-Storno 30/100%", "hoch", "mittel", "Stefan", D(7,24), "Back-to-Back-Regelung in Intercompany-Order"),
    ("Risiko", "NDA-Sperre: kein Vantage-Kontakt, keine Aussenkommunikation, keine Fotos", "hoch", "niedrig", "Burak", D(7,16), "Team briefen; Kommunikation nur ueber DPR"),
]
r = 2
for i, (typ, besch, ausw, wahr, ow, term, mass) in enumerate(rk, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=typ)
    ws.cell(row=r, column=3, value=besch); ws.cell(row=r, column=4, value=ausw)
    ws.cell(row=r, column=5, value=wahr); ws.cell(row=r, column=6, value=ow)
    ws.cell(row=r, column=7, value=term).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=8, value="offen"); ws.cell(row=r, column=9, value=mass)
    # Hilfsspalte K fuer Wochenbericht: Zeilen-Nr., wenn offen & Auswirkung hoch
    ws.cell(row=r, column=11, value=f'=IF(AND($H{r}<>"erledigt",$D{r}="hoch"),ROW(),"")')
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 2, 4, 5, 7, 8):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Risiken", 1, last, len(cols))
add_dv(ws, "Stopp-Punkt,Risiko,Entscheid", f"B2:B{last}")
add_dv(ws, "hoch,mittel,niedrig", f"D2:D{last}")
add_dv(ws, "hoch,mittel,niedrig", f"E2:E{last}")
add_dv(ws, OWNER_LIST, f"F2:F{last}")
add_dv(ws, STATUS_LIST, f"H2:H{last}")
status_cf(ws, "H", 2, last)
ws.conditional_formatting.add(f"D2:D{last}", CellIsRule(operator="equal", formula=['"hoch"'],
    fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, bold=True, color=RED_TXT)))
ws.conditional_formatting.add(f"E2:E{last}", CellIsRule(operator="equal", formula=['"hoch"'],
    fill=PatternFill("solid", fgColor=ORANGE_FILL), font=Font(name=FONT_NAME, bold=True, color=ORANGE_TXT)))
ws.conditional_formatting.add(f"B2:B{last}", CellIsRule(operator="equal", formula=['"Stopp-Punkt"'],
    font=Font(name=FONT_NAME, bold=True, color=RED_TXT)))
ws.column_dimensions["K"].hidden = True
ws.cell(row=1, column=11, value="(Hilfsspalte)").font = small_it
page_setup(ws, freeze="A2")

# ================================================================ 13) KOMMERZIELL
ws = wb.create_sheet("Kommerziell")
cols = ["Nr.", "Position", "Paket", "EUR-Wert (Einkauf, Referenz)", "Rechnungsstatus",
        "Zahlungsziel", "CHF Verkauf", "Bemerkung"]
widths(ws, [6, 40, 12, 20, 15, 12, 16, 40])
header_row(ws, 1, cols)
EUR_FMT = "#'##0.00\" EUR\""
kom = [
    ("Angebot P-640380-3 - Loadbank 6 MVA (Miete + Einmalkosten)", "Loadbank", 310328.50, "offen", "30 Tage", "PO E3-A25002-49A; Basis 110 Tage"),
    ("Angebot P-650395-2 - Headload 8 MW (Miete + Einmalkosten)", "Headload", 280511.84, "offen", "30 Tage", "PO E3-A25002-49B; Basis 110 Tage"),
    ("Einkaufsvolumen total", "beide", "=D2+D3", None, "-", "Summe beider Angebote"),
    ("Transport (Schaetzposition)", "beide", None, "offen", "30 Tage", "nach Aufwand gemaess Angebot"),
    ("Technikereinsaetze (Schaetzposition)", "beide", None, "offen", "30 Tage", "nach Aufwand gemaess Angebot"),
    ("Fuel Unreturned", "Headload", 2.20, "offen", "30 Tage", "EUR 2.20 pro Liter; Mengen siehe Fuel-Log"),
    ("Off-Hire-Fristen", "beide", None, None, "-", "Abmeldung 5 Arbeitstage im Voraus, sonst Weiterberechnung"),
    ("Rate 1 (Staffelungs-Fakturierung)", "beide", None, "offen", "30 Tage", "Staffelung klaeren: 5-MW ab Abruf oder Mietbeginn?"),
    ("Rate 2 (Staffelungs-Fakturierung)", "beide", None, "offen", "30 Tage", ""),
    ("Schlussrechnung", "beide", None, "offen", "30 Tage", "nach Abnahme / Closeout"),
]
r = 2
for i, (pos, pk, eur, stat, ziel, bem) in enumerate(kom, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=pos)
    ws.cell(row=r, column=3, value=pk)
    ec = ws.cell(row=r, column=4, value=eur)
    ec.number_format = "#'##0.00\" EUR/l\"" if pos == "Fuel Unreturned" else EUR_FMT
    ws.cell(row=r, column=5, value=stat)
    ws.cell(row=r, column=6, value=ziel)
    ws.cell(row=r, column=7, value="[Innendienst/ARM]")
    ws.cell(row=r, column=8, value=bem)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 4, 5, 6, 7):
        ws.cell(row=rr, column=cc).alignment = center
for cc in range(1, len(cols) + 1):
    ws.cell(row=4, column=cc).font = bold_font
make_table(ws, "Kommerziell", 1, last, len(cols))
add_dv(ws, "Loadbank,Headload,beide", f"C2:C{last}")
add_dv(ws, "offen,gestellt,bezahlt,geprueft", f"E2:E{last}")
for val, fill, txt in [("bezahlt", GREEN, GREEN_TXT), ("geprueft", GREEN, GREEN_TXT),
                       ("gestellt", YELLOW, YELLOW_TXT)]:
    ws.conditional_formatting.add(f"E2:E{last}", CellIsRule(operator="equal", formula=[f'"{val}"'],
        fill=PatternFill("solid", fgColor=fill), font=Font(name=FONT_NAME, color=txt)))
ws.cell(row=last + 2, column=2,
    value="Nur EUR-Einkaufsreferenzen (Aggreko). CHF-Verkaufspreise ausschliesslich via Innendienst/ARM - "
          "hier bewusst NICHT gefuehrt (Vertraulichkeit/Marge).").font = small_it
ws.merge_cells(start_row=last + 2, start_column=2, end_row=last + 2, end_column=8)
page_setup(ws, freeze="A2")

# ================================================================ 14) TREND
ws = wb.create_sheet("Trend")
ws.sheet_view.showGridLines = False
widths(ws, [8, 14, 16, 20, 30])
ws["A1"] = "TREND - offene Aufgaben & erledigte Meilensteine (jeden Freitag eintragen)"
ws["A1"].font = sub_font
ws.merge_cells("A1:E1")
lc = ws.cell(row=2, column=1, value="Aktueller Stand (zum Uebertragen):"); lc.font = kpi_lbl
ws.merge_cells("A2:B2")
c1 = ws.cell(row=2, column=3, value='=COUNTA(Aufgaben[Nr.])-COUNTIF(Aufgaben[Status],"erledigt")')
c1.font = bold_font; c1.alignment = center; c1.border = border
c2 = ws.cell(row=2, column=4, value='=COUNTIF(Meilensteine[Status],"erledigt")')
c2.font = bold_font; c2.alignment = center; c2.border = border
cols = ["KW", "Datum (Fr)", "Aufgaben offen", "Meilensteine erledigt", "Bemerkung"]
header_row(ws, 4, cols)
r = 5
fri = datetime.datetime(2026, 7, 17)
while fri <= datetime.datetime(2026, 12, 31):
    ws.cell(row=r, column=1, value="KW%d" % fri.isocalendar()[1])
    dc = ws.cell(row=r, column=2, value=fri); dc.number_format = "DD.MM.YYYY"
    r += 1
    fri += timedelta(days=7)
last = r - 1
body(ws, 5, last, len(cols))
for rr in range(5, last + 1):
    for cc in (1, 2, 3, 4):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Trend", 4, last, len(cols))
ws.cell(row=last + 2, column=1,
    value="Jeden Freitag die beiden Werte aus Zeile 2 als ZAHL eintragen (kopieren > Werte einfuegen). "
          "So entsteht der Verlauf - ganz ohne Makros.").font = small_it
ws.merge_cells(start_row=last + 2, start_column=1, end_row=last + 2, end_column=5)

lch = LineChart()
lch.title = "Projekt-Trend 2026"
lch.add_data(Reference(ws, min_col=3, min_row=4, max_row=last), titles_from_data=True)
lch.add_data(Reference(ws, min_col=4, min_row=4, max_row=last), titles_from_data=True)
lch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=last))
for s in lch.series:
    s.cat = AxDataSource(strRef=StrRef(f"'Trend'!$A$5:$A${last}"))
    s.smooth = False
    s.marker = Marker(symbol="circle", size=6)
lch.series[0].graphicalProperties = GraphicalProperties(ln=LineProperties(solidFill=ORANGE, w=22000))
lch.series[1].graphicalProperties = GraphicalProperties(ln=LineProperties(solidFill=NAVY, w=22000))
lch.x_axis.delete = False; lch.y_axis.delete = False
lch.x_axis.tickLblPos = "nextTo"; lch.y_axis.tickLblPos = "nextTo"
lch.height = 9; lch.width = 16
ws.add_chart(lch, "G4")
page_setup(ws, freeze="A5", title_rows="4:4")

# ================================================================ 15) DOKUMENTE
ws = wb.create_sheet("Dokumente")
cols = ["Nr.", "Dokument", "Version/Datum", "Quelle", "SharePoint-Link", "Status", "Bemerkung"]
widths(ws, [6, 44, 18, 12, 30, 13, 32])
header_row(ws, 1, cols)
SP = "[SharePoint-Projektordner]"
dok = [
    ("Angebot P-640380-3 (Loadbank 6 MVA)", "30.04.2026", "Aggreko", "final", ""),
    ("Proposal P-650395-2 (Headload 8 MW)", "30.04.2026", "Aggreko", "final", ""),
    ("PO E3-A25002-49A (Loadbank)", "V0", "DPR", "Entwurf", "Korrekturliste laeuft"),
    ("PO E3-A25002-49B (Headload)", "V0", "DPR", "Entwurf", "Korrekturliste laeuft"),
    ("NDA (Partei Aggreko)", "unsigniert", "DPR", "ueberholt", "bei MiT-Konstellation ueberholt - neue NDA MiT-DPR noetig"),
    ("Anlage Versicherung", "-", "DPR", "Entwurf", "Deckungssummen offen"),
    ("Logistikplan Phase 2", "Rev. C04", "DPR", "final", "Tank-Standort ergaenzen"),
    ("Supplemental Conditions", "r2", "DPR", "final", "Meeting-Pflichten siehe Blatt Termine & Meetings"),
    ("Compliance WORKcontrol", "-", "DPR", "final", ""),
    ("EHS-Plan", "Rev. 4 / 22.01.2026", "DPR", "final", ""),
]
dok += [("Einzelanalyse %02d" % k, "-", "MiT", "final", "") for k in range(1, 12)]
dok += [
    ("Projektdossier INTERN", "-", "MiT", "final", "vertraulich - nicht an DPR"),
    ("MiT-Offerten (Layout)", "in Arbeit", "MiT", "Entwurf", "Ann-Kathrin"),
    ("Intercompany-Order Aggreko", "offen", "MiT", "Entwurf", "Back-to-Back, Sarah/bSuite"),
    ("RAMS-Paket", "offen", "MiT", "Entwurf", "Abgabe 20.07. Hammertech"),
    ("Long-Lead-Liste", "offen", "MiT", "Entwurf", "3-Tage-Frist ab Vertragsunterzeichnung"),
    ("Wochenbericht (PDF-Export)", "laufend", "MiT", "Entwurf", "aus Blatt Wochenbericht"),
]
r = 2
for i, (name, ver, q, stat, bem) in enumerate(dok, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=ver); ws.cell(row=r, column=4, value=q)
    ws.cell(row=r, column=5, value=SP); ws.cell(row=r, column=6, value=stat)
    ws.cell(row=r, column=7, value=bem)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 4, 6):
        ws.cell(row=rr, column=cc).alignment = center
    ws.cell(row=rr, column=5).font = small_it
make_table(ws, "Dokumente", 1, last, len(cols))
add_dv(ws, "DPR,Aggreko,MiT", f"D2:D{last}")
add_dv(ws, STATUS_DOK, f"F2:F{last}")
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"signiert"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"final"'],
    fill=PatternFill("solid", fgColor=YELLOW), font=Font(name=FONT_NAME, color=YELLOW_TXT)))
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"ueberholt"'],
    fill=PatternFill("solid", fgColor=GREY), font=Font(name=FONT_NAME, color="808080")))
page_setup(ws, freeze="A2")

# ================================================================ 16) KONTAKTE
ws = wb.create_sheet("Kontakte")
cols = ["Nr.", "Name", "Firma", "Rolle", "Telefon", "E-Mail", "24/7", "Bemerkung"]
widths(ws, [6, 26, 14, 30, 22, 28, 8, 30])
header_row(ws, 1, cols)
kon = [
    ("Roxana Minor", "DPR", "Vertrag / Einkauf (Hauptkontakt)", "[eintragen]", "[eintragen]", "nein", "Hauptkontakt neu"),
    ("Gavin Stanbury", "DPR", "Projekt", "[eintragen]", "[eintragen]", "nein", ""),
    ("Lee Robertson", "DPR", "Projekt", "[eintragen]", "[eintragen]", "nein", ""),
    ("Martin Wendsche", "DPR", "Managing Director / Unterschrift", "[eintragen]", "[eintragen]", "nein", ""),
    ("N.N. DPR-Superintendent", "DPR", "Bauleitung vor Ort", "[eintragen]", "[eintragen]", "nein", "offen"),
    ("N.N. DPR EHS", "DPR", "Sicherheit / EHS", "[eintragen]", "[eintragen]", "nein", "offen"),
    ("Tanya Hoffmann", "Aggreko", "Vertrieb DE", "[eintragen]", "[eintragen]", "nein", "cc bei Versand Gesamtpaket"),
    ("N.N. (PL Aggreko DE)", "Aggreko", "Projektleiter", "[eintragen]", "[eintragen]", "nein", "wird benannt"),
    ("Johannes Schepp", "Aggreko", "Projekt / Technik", "[eintragen]", "[eintragen]", "nein", ""),
    ("Mike Kutsch", "Aggreko", "Projekt / Technik", "[eintragen]", "[eintragen]", "nein", ""),
    ("Alexej Soltow", "Aggreko", "Projekt / Technik", "[eintragen]", "[eintragen]", "nein", ""),
    ("Burak Uecoez", "MiT", "Projektleiter", "[eintragen]", "[eintragen]", "nein", "Gesamtverantwortung"),
    ("Stefan", "MiT", "GL / Unterschriften", "[eintragen]", "[eintragen]", "nein", ""),
    ("Markus", "MiT", "Finance / Versicherung / Zoll", "[eintragen]", "[eintragen]", "nein", ""),
    ("Ann-Kathrin", "MiT", "Backoffice / Angebote", "[eintragen]", "[eintragen]", "nein", ""),
    ("Sarah", "MiT", "bSuite / Intercompany", "[eintragen]", "[eintragen]", "nein", ""),
    ("Samuel", "MiT", "RAMS / Sicherheit", "[eintragen]", "[eintragen]", "nein", ""),
    ("Stephan Marty", "MiT", "Vertrag / Support PL", "[eintragen]", "[eintragen]", "nein", ""),
    ("Olli", "MiT", "FX / Finanzen", "[eintragen]", "[eintragen]", "nein", "Kursabsicherung"),
    ("WORKcontrol Suisse AG", "Sonstige", "Zutritt / Badges", "+41 44 512 88 11", "contact@workcontrol.ch", "nein", "CHF 25/Person Erstanmeldung"),
    ("24/7-Notfallnummer MiT", "MiT", "Notfall / Bereitschaft", "[eintragen]", "-", "ja", "offen - Kontaktkette"),
    ("24/7-Notfallnummer Aggreko", "Aggreko", "Notfall / Service", "[eintragen]", "-", "ja", "offen - Kontaktkette"),
]
r = 2
for i, (name, firma, rolle, tel, mail, s247, bem) in enumerate(kon, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=firma); ws.cell(row=r, column=4, value=rolle)
    ws.cell(row=r, column=5, value=tel); ws.cell(row=r, column=6, value=mail)
    ws.cell(row=r, column=7, value=s247); ws.cell(row=r, column=8, value=bem)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 7):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Kontakte", 1, last, len(cols))
add_dv(ws, "DPR,Aggreko,MiT,Sonstige", f"C2:C{last}")
add_dv(ws, "ja,nein", f"G2:G{last}")
ws.conditional_formatting.add(f"G2:G{last}", CellIsRule(operator="equal", formula=['"ja"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, bold=True, color=GREEN_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 17) AENDERUNGSLOG & ENTSCHEIDE
ws = wb.create_sheet("Aenderungslog & Entscheide")
cols = ["Datum", "Wer", "Typ", "Was", "Auswirkung", "Termin", "Status"]
widths(ws, [14, 18, 13, 56, 22, 13, 12])
header_row(ws, 1, cols)
log = [
    (D(7,15), "Burak Uecoez", "Aenderung", "Projektaufsetzung, Aufgabenverteilung.", "-", None, None),
    (D(7,15), "Stefan / Olli", "Entscheid", "EUR/CHF-Kurs und Absicherung festlegen.", "FX-Risiko", D(7,17), "offen"),
    (D(7,15), "Stefan", "Entscheid", "Verhandlungslinie / Redline-Linie Korrekturliste.", "PO-Korrektur", D(7,17), "offen"),
    (D(7,15), "Stefan", "Entscheid", "MiT-Vertragskonstellation final (Parteien, NDA).", "Vertraege", D(7,20), "offen"),
    (D(7,15), "Burak Uecoez", "Aenderung", "Tool erstellt und vorbefuellt; Erweiterungen: Gantt, Personal, Kontakte, Logistik, Testprotokolle, Kommerziell.", "-", None, None),
    (D(7,16), "Burak Uecoez", "Aenderung", "V2-Aenderungen uebernommen; Kalender 2026 gegen ISO-Kalender geprueft; Samstag-Termine korrigiert.", "-", None, None),
    (D(7,16), "Burak Uecoez", "Aenderung", "V5: EUR-Werte + PO-Nummern, Termine & Meetings, Kommerziell, Wahrscheinlichkeit, Kontakte, naechste 5 Meilensteine; Diagramm-Fixes.", "-", None, None),
    (D(7,16), "Burak Uecoez", "Aenderung", "V6: Wochenbericht, Schichtplan, Fuel-Log, Trend, Vorgaenger-Abhaengigkeiten, Off-Hire-Countdown, Entscheidungs-Tracker.", "-", None, None),
]
r = 2
for datum, wer, typ, was, ausw, term, stat in log:
    ws.cell(row=r, column=1, value=datum).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=2, value=wer); ws.cell(row=r, column=3, value=typ)
    ws.cell(row=r, column=4, value=was); ws.cell(row=r, column=5, value=ausw)
    tc = ws.cell(row=r, column=6, value=term)
    tc.number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=7, value=stat)
    ws.cell(row=r, column=8, value=f'=IF(AND($C{r}="Entscheid",$G{r}="offen"),ROW(),"")')
    r += 1
first_empty = r
for _ in range(20):
    ws.cell(row=r, column=1).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=6).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=8, value=f'=IF(AND($C{r}="Entscheid",$G{r}="offen"),ROW(),"")')
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 6, 7):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Aenderungslog", 1, last, len(cols))
add_dv(ws, "Aenderung,Entscheid", f"C2:C{last}")
add_dv(ws, "offen,entschieden", f"G2:G{last}")
ws.conditional_formatting.add(f"C2:C{last}", CellIsRule(operator="equal", formula=['"Entscheid"'],
    fill=PatternFill("solid", fgColor=ORANGE_FILL), font=Font(name=FONT_NAME, bold=True, color=ORANGE_TXT)))
ws.conditional_formatting.add(f"F2:F{last}",
    FormulaRule(formula=['AND($G2="offen",$F2<>"",$F2<TODAY())'],
                fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, bold=True, color=RED_TXT)))
ws.conditional_formatting.add(f"G2:G{last}", CellIsRule(operator="equal", formula=['"entschieden"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.column_dimensions["H"].hidden = True
ws.cell(row=1, column=8, value="(Hilfsspalte)").font = small_it
page_setup(ws, freeze="A2")

# ---------------------------------------------------------------- Reihenfolge + Tabfarben
order = ["Dashboard", "Wochenbericht", "Terminplan", "Meilensteine", "Aufgaben",
         "Termine & Meetings", "Personal & Zutritt", "Schichtplan",
         "Lieferungen & Logistik", "Testprotokolle", "Fuel-Log",
         "Stopp-Punkte & Risiken", "Kommerziell", "Trend", "Dokumente", "Kontakte",
         "Aenderungslog & Entscheide"]
wb._sheets.sort(key=lambda s: order.index(s.title))
tab_colors = {"Dashboard": NAVY, "Wochenbericht": NAVY, "Terminplan": ORANGE,
              "Meilensteine": ORANGE, "Aufgaben": ORANGE,
              "Stopp-Punkte & Risiken": "C00000", "Kommerziell": "70AD47", "Trend": "70AD47"}
for s in wb.worksheets:
    s.sheet_properties.tabColor = tab_colors.get(s.title, "8EA9C1")

# ---------------------------------------------------------------- Speichern
wb.properties.creator = "Mobil in Time AG"
wb.properties.title = "Projektsteuerung MiT-PWR-WIN-2026-001"
wb.properties.subject = "DPR / Vantage ZRH12 Winterthur"
out = "/home/user/Burak/Projektsteuerung_MiT-PWR-WIN-2026-001.xlsx"
wb.save(out)
print("Gespeichert:", out)
print("Blaetter (%d):" % len(wb.sheetnames), wb.sheetnames)
print("Meilensteine:", N_MS, "| Gantt-Wochen:", NW)
