# -*- coding: utf-8 -*-
"""
Projektsteuerungs-Tool MiT-PWR-WIN-2026-001  (erweiterte Version)
SharePoint-taugliche .xlsx ohne Makros. Schweizer Schreibweise (ss statt scharfes S).
Farben: Navy #1F3A5F, Orange #E8740C, Schrift Arial.

9 Registerblaetter:
  Dashboard | Terminplan (Gantt) | Meilensteine | Aufgaben | Personal & Zutritt |
  Offene Punkte & Risiken | Dokumente | Kontakte | Aenderungslog

Alle Formeln sind intern englisch/komma-getrennt gespeichert (Excel-Standard) und
werden in deutschem Excel automatisch lokalisiert angezeigt.
"""
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule, DataBarRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties

# ---------------------------------------------------------------- Farben / Stile
NAVY = "1F3A5F"; ORANGE = "E8740C"; WHITE = "FFFFFF"
LIGHT = "F2F5F9"
GREEN = "C6EFCE"; GREEN_TXT = "006100"
RED = "FFC7CE"; RED_TXT = "9C0006"
ORANGE_FILL = "FCE3C8"; ORANGE_TXT = "9C4A00"
YELLOW = "FFEB9C"; YELLOW_TXT = "9C6500"
GREY = "D9D9D9"; BAR_BLUE = "4F81BD"
GANTT = "E8740C"

FONT_NAME = "Arial"
hdr_font   = Font(name=FONT_NAME, size=10, bold=True, color=WHITE)
hdr_fill   = PatternFill("solid", fgColor=NAVY)
title_font = Font(name=FONT_NAME, size=16, bold=True, color=NAVY)
sub_font   = Font(name=FONT_NAME, size=11, bold=True, color=ORANGE)
label_font = Font(name=FONT_NAME, size=10, bold=True, color=NAVY)
base_font  = Font(name=FONT_NAME, size=10, color="000000")
kpi_num    = Font(name=FONT_NAME, size=18, bold=True, color=NAVY)
kpi_lbl    = Font(name=FONT_NAME, size=9, bold=True, color="404040")
small_it   = Font(name=FONT_NAME, size=8, italic=True, color="808080")

thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left   = Alignment(horizontal="left", vertical="center", wrap_text=True)
left_top = Alignment(horizontal="left", vertical="top", wrap_text=True)

STATUS_LIST = "offen,in Arbeit,erledigt,verschoben,kritisch"
STATUS_DOK  = "Entwurf,final,signiert,ueberholt"

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

# ================================================================ 1) DASHBOARD
ws = wb.active
ws.title = "Dashboard"
ws.sheet_view.showGridLines = False
widths(ws, [3, 34, 30, 8, 30, 12, 16, 12])  # A..H

ws["B2"] = "PROJEKTSTEUERUNG"; ws["B2"].font = title_font
ws.merge_cells("B2:D2")
ws["B3"] = "MiT-PWR-WIN-2026-001  |  DPR Construction / Vantage Datacenter ZRH12"
ws["B3"].font = sub_font; ws.merge_cells("B3:H3")

# ---- Stammdaten (links, Zeilen 5-14)
stamm = [
    ("Projekt-Nr.", "MiT-PWR-WIN-2026-001"),
    ("Kunde / Auftraggeber", "DPR Construction"),
    ("Endkunde / Standort", "Vantage Datacenter ZRH12, Fabrikstrasse 10/12, 8404 Winterthur"),
    ("Auftragnehmer", "Mobil in Time AG (Subunternehmer von DPR)"),
    ("Unterlieferant", "Aggreko Deutschland GmbH"),
    ("Paket 1", "6-MVA-Loadbank-Test (Generatoren)"),
    ("Paket 2", "8-MW-Heat-Load-Test (54x 200 kW)"),
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

# ---- KPI Aufgaben (rechts, Spalten E/F, Zeilen 4-11)
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
# Fortschritt Aufgaben (Datenbalken)
ws.cell(row=10, column=5, value="Fortschritt Aufgaben").font = kpi_lbl
ws.cell(row=10, column=5).alignment = left; ws.cell(row=10, column=5).border = border
pc = ws.cell(row=10, column=6,
    value='=IFERROR(COUNTIF(Aufgaben[Status],"erledigt")/COUNTA(Aufgaben[Nr.]),0)')
pc.number_format = "0%"; pc.font = Font(name=FONT_NAME, bold=True, color=NAVY)
pc.alignment = center; pc.border = border

# ---- KPI Meilensteine (Zeilen 12-16)
ws.cell(row=11, column=5, value="MEILENSTEINE").font = sub_font
kpi_m = [
    ("Meilensteine gesamt", '=COUNTA(Meilensteine[Nr.])'),
    ("davon erledigt", '=COUNTIF(Meilensteine[Status],"erledigt")'),
    ("davon kritisch", '=COUNTIF(Meilensteine[Status],"kritisch")'),
]
rr = 12
for lbl, f in kpi_m:
    lc = ws.cell(row=rr, column=5, value=lbl); lc.font = kpi_lbl; lc.alignment = left; lc.border = border
    vc = ws.cell(row=rr, column=6, value=f); vc.font = Font(name=FONT_NAME, size=12, bold=True, color=NAVY)
    vc.alignment = center; vc.border = border
    rr += 1
ws.cell(row=15, column=5, value="Fortschritt Meilensteine").font = kpi_lbl
ws.cell(row=15, column=5).alignment = left; ws.cell(row=15, column=5).border = border
pm = ws.cell(row=15, column=6,
    value='=IFERROR(COUNTIF(Meilensteine[Status],"erledigt")/COUNTA(Meilensteine[Nr.]),0)')
pm.number_format = "0%"; pm.font = Font(name=FONT_NAME, bold=True, color=NAVY)
pm.alignment = center; pm.border = border
# Datenbalken
bar = DataBarRule(start_type='num', start_value=0, end_type='num', end_value=1, color=GANTT)
ws.conditional_formatting.add("F10", bar)
ws.conditional_formatting.add("F15", DataBarRule(start_type='num', start_value=0,
    end_type='num', end_value=1, color=BAR_BLUE))

# ---- Projektstatus-Ampel + Diese Woche (Zeilen 17-19 rechts)
ws.cell(row=17, column=5, value="PROJEKTSTATUS").font = sub_font
st = ws.cell(row=18, column=5,
    value=('=IF(SUMPRODUCT((Aufgaben[Status]<>"erledigt")*(Aufgaben[Termin]<>"")*'
           '(Aufgaben[Termin]<TODAY()))>0,"KRITISCH - ueberfaellige Aufgaben",'
           'IF(COUNTIF(Meilensteine[Status],"kritisch")+COUNTIF(Aufgaben[Status],"kritisch")>0,'
           '"ACHTUNG - kritische Punkte offen","AUF KURS - keine Ueberfaelligkeiten"))'))
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

# ---- Countdown (links, Zeilen 16-21)
ws.cell(row=16, column=2, value="COUNTDOWN").font = sub_font
cd_fmt = '0" Tage";"ueberfaellig";"heute"'
counts = [
    ("Tage bis naechster Meilenstein", '=IFERROR(B25-TODAY(),"")'),
    ("Tage bis Entsendefrist Aggreko (24.07.)", '=DATE(2026,7,24)-TODAY()'),
    ("Tage bis Lieferung Headloads (03.08.)", '=DATE(2026,8,3)-TODAY()'),
    ("Tage bis Mietende Loadbank (02.11.)", '=DATE(2026,11,2)-TODAY()'),
    ("Tage bis Closeout (15.12.)", '=DATE(2026,12,15)-TODAY()'),
]
r = 17
for lbl, f in counts:
    lc = ws.cell(row=r, column=2, value=lbl); lc.font = kpi_lbl; lc.alignment = left; lc.border = border
    vc = ws.cell(row=r, column=3, value=f); vc.number_format = cd_fmt
    vc.font = Font(name=FONT_NAME, bold=True, color=NAVY); vc.alignment = center; vc.border = border
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    ws.cell(row=r, column=4).border = border
    r += 1

# ---- Naechste Meilensteine (links, Zeilen 24-27)
ws.cell(row=23, column=2, value="NAECHSTE MEILENSTEINE").font = sub_font
for i, h in enumerate(["Plantermin", "Meilenstein", "Status"]):
    col = [2, 3, 5][i]
    c = ws.cell(row=24, column=col, value=h)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
ws.merge_cells("C24:D24")
for k in range(1, 4):
    ri = 24 + k
    f_term = ('=IFERROR(AGGREGATE(15,6,Meilensteine!$C$2:$C$17/'
              '((Meilensteine!$E$2:$E$17<>"erledigt")*(Meilensteine!$C$2:$C$17>=TODAY())),%d),"")' % k)
    tc = ws.cell(row=ri, column=2, value=f_term); tc.number_format = "DD.MM.YYYY"
    tc.font = base_font; tc.alignment = center; tc.border = border
    nc = ws.cell(row=ri, column=3,
        value='=IFERROR(INDEX(Meilensteine!$B$2:$B$17,MATCH(B%d,Meilensteine!$C$2:$C$17,0)),"")' % ri)
    nc.font = base_font; nc.alignment = left; nc.border = border
    ws.merge_cells(start_row=ri, start_column=3, end_row=ri, end_column=4)
    ws.cell(row=ri, column=4).border = border
    sc = ws.cell(row=ri, column=5,
        value='=IFERROR(INDEX(Meilensteine!$E$2:$E$17,MATCH(B%d,Meilensteine!$C$2:$C$17,0)),"")' % ri)
    sc.font = base_font; sc.alignment = center; sc.border = border

ws.cell(row=29, column=2,
    value="Alle Werte aktualisieren sich automatisch aus den Registerblaettern (Formeln, keine Pivots). "
          "Farben: gruen = erledigt/ok, gelb = in Arbeit, orange = Achtung/verschoben, rot = kritisch/ueberfaellig.").font = small_it
ws.merge_cells("B29:H29")
page_setup(ws, freeze="A1", title_rows=None)
ws.print_area = "A1:H30"

# ================================================================ 2) TERMINPLAN (GANTT)
ws = wb.create_sheet("Terminplan")
ws.sheet_view.showGridLines = False
widths(ws, [5, 40, 12, 12, 9, 9, 9, 9, 9, 9])
# Kopf: A1..D1 Text, E1..J1 Monats-Daten
for i, h in enumerate(["Nr.", "Phase / Meilenstein", "Start", "Ende"]):
    c = ws.cell(row=1, column=1 + i, value=h)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
for i, mth in enumerate(range(7, 13)):
    c = ws.cell(row=1, column=5 + i, value=D(mth, 1))
    c.number_format = "MMM"; c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
gantt = [
    ("Projektvorbereitung & Mobilisierung", D(7,16), D(8,3)),
    ("Loadbank 6 MVA - Miete", D(8,17), D(11,2)),
    ("Heat-Load (Headloads) - Miete", D(8,3), D(12,11)),
    ("5-MW-Block (Abruf)", D(9,1), D(9,30)),
    ("Testphase / Inbetriebnahme", D(8,3), D(11,2)),
    ("Demontage", D(12,14), D(12,14)),
    ("Closeout & Dokumentation", D(12,15), D(12,31)),
]
r = 2
for i, (name, s, e) in enumerate(gantt, 1):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2, value=name)
    cs = ws.cell(row=r, column=3, value=s); cs.number_format = "DD.MM.YYYY"
    ce = ws.cell(row=r, column=4, value=e); ce.number_format = "DD.MM.YYYY"
    r += 1
last = r - 1
body(ws, 2, last, 10)
for rr in range(2, last + 1):
    ws.cell(row=rr, column=1).alignment = center
    ws.cell(row=rr, column=3).alignment = center
    ws.cell(row=rr, column=4).alignment = center
    ws.cell(row=rr, column=2).alignment = left
# Gantt-Balken via bedingter Formatierung: Monat ueberlappt [Start,Ende]?
ws.conditional_formatting.add(f"E2:J{last}",
    FormulaRule(formula=['AND(E$1<=$D2,EOMONTH(E$1,0)>=$C2,$C2<>"")'],
                fill=PatternFill("solid", fgColor=GANTT)))
ws.auto_filter.ref = f"A1:D{last}"
ws.cell(row=last + 2, column=2,
    value="Orange = Phase/Miete aktiv im jeweiligen Monat. Balken berechnen sich aus Start/Ende.").font = small_it
ws.merge_cells(start_row=last + 2, start_column=2, end_row=last + 2, end_column=10)
page_setup(ws, freeze="E2", title_rows="1:1")

# ================================================================ 3) MEILENSTEINE
ws = wb.create_sheet("Meilensteine")
cols = ["Nr.", "Meilenstein", "Plantermin", "Ist-Termin", "Status", "Verantwortlich", "Bemerkung"]
widths(ws, [6, 46, 15, 14, 14, 18, 40])
header_row(ws, 1, cols)
ms = [
    ("bSuite-Aufnahme", D(7,16,8,0), "Sarah", "Aufnahme 08:00"),
    ("Unterlagenpaket an DPR (Versicherung, HR-Auszug, Zeichnungsberechtigte, Zollprozess)", D(7,16,12,0), "Ann-Kathrin", "Abgabe 12:00"),
    ("Unterschriften Stefan", D(7,16), "Stefan", "Nachmittags"),
    ("Alignment-Call Aggreko DE", D(7,17), "Burak", "16./17.07."),
    ("PO-Redlines an DPR", D(7,17), "Burak", ""),
    ("RAMS-Abgabe Hammertech", D(7,20), "Samuel", ""),
    ("Personenliste Aggreko", D(7,20), "Aggreko", ""),
    ("Entsendemeldung Aggreko-Personal", D(7,24), "Aggreko", "Frist beachten"),
    ("WORKcontrol-Badges + Site Inductions", D(8,3), "Ann-Kathrin", "vor 03.08."),
    ("Lieferung Headloads", D(8,3), "Aggreko", "54x 200 kW"),
    ("Lieferung Loadbank 6 MVA", D(8,17), "Aggreko", ""),
    ("Abruf 5-MW-Block", D(9,1), "Burak", "September"),
    ("Mietende Loadbank", D(11,2), "Burak", ""),
    ("Mietende Headloads", D(12,11), "Burak", ""),
    ("Demontage", D(12,14), "Aggreko", ""),
    ("Closeout-Paket EN+DE an DPR", D(12,15), "Burak", "Dezember"),
]
r = 2
for i, (name, term, verant, bem) in enumerate(ms, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    tc = ws.cell(row=r, column=3, value=term)
    tc.number_format = "DD.MM.YYYY" if term.hour == 0 else "DD.MM.YYYY hh:mm"
    ws.cell(row=r, column=4).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=5, value="offen")
    ws.cell(row=r, column=6, value=verant); ws.cell(row=r, column=7, value=bem)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 4, 5):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Meilensteine", 1, last, len(cols))
add_dv(ws, STATUS_LIST, f"E2:E{last}")
status_cf(ws, "E", 2, last)
ws.conditional_formatting.add(f"C2:C{last}",
    FormulaRule(formula=['AND($C2<TODAY(),$E2<>"erledigt",$C2<>"")'],
                fill=PatternFill("solid", fgColor=ORANGE_FILL), font=Font(name=FONT_NAME, color=ORANGE_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 4) AUFGABEN
ws = wb.create_sheet("Aufgaben")
cols = ["Nr.", "Aufgabe", "Paket", "Owner", "Termin", "Status", "Prioritaet", "Bemerkung", "Erledigt am"]
widths(ws, [6, 50, 12, 14, 14, 13, 12, 34, 14])
header_row(ws, 1, cols)
au = [
    ("Versicherungsnachweis via Finance beschaffen", "Admin", "Markus", D(7,16), "hoch", ""),
    ("Zollprozess DE-CH schriftlich klaeren (Kostentraeger, Equipment vs. Kraftstoff)", "Admin", "Markus", D(7,17), "hoch", ""),
    ("Deckungssummen bei DPR erfragen", "Admin", "Markus", D(7,17), "mittel", ""),
    ("HR-Auszug bereitstellen", "Admin", "Ann-Kathrin", D(7,16), "hoch", ""),
    ("Beide Angebote in MiT-Layout bringen", "beide", "Ann-Kathrin", D(7,17), "mittel", "P-640380-3 / P-650395-2"),
    ("WORKcontrol-Registrierung MiT", "Admin", "Ann-Kathrin", D(7,25), "hoch", "vor Badges"),
    ("Versand Gesamtpaket an DPR", "Admin", "Ann-Kathrin", D(7,16,12,0), "hoch", ""),
    ("Entscheid CHF-Kurs / Absicherung mit Olli", "Admin", "Stefan", D(7,17), "hoch", "FX EUR/CHF"),
    ("Redline-Linie festlegen", "beide", "Stefan", D(7,17), "hoch", ""),
    ("Unterschriften leisten", "Admin", "Stefan", D(7,16), "hoch", "Nachmittags"),
    ("bSuite + Intercompany-Schiene Aggreko aufsetzen", "beide", "Sarah", D(7,16), "hoch", ""),
    ("RAMS-Praxischeck durchfuehren", "beide", "Samuel", D(7,20), "hoch", "Hammertech"),
    ("PO-Redlines erstellen und einreichen", "beide", "Burak", D(7,17), "hoch", "Rechenfehler pruefen"),
    ("Aggreko-Terminbestaetigung 03.08. / 17.08. schriftlich einholen", "beide", "Burak", D(7,20), "hoch", ""),
    ("Staffelungs-Fakturierung klaeren", "beide", "Burak", D(7,24), "mittel", ""),
    ("PL-Benennung Aggreko DE anfordern", "beide", "Burak", D(7,20), "mittel", ""),
    ("Heavy-Duty-Strombedarf bei DPR einreichen", "beide", "Burak", D(7,24), "hoch", ""),
    ("NDA MiT-DPR anstossen", "Admin", "Burak", D(7,18), "hoch", "eigene NDA"),
    ("Kranfrage / Lift Plan klaeren", "beide", "Burak", D(7,28), "mittel", ""),
    ("24/7-Kontaktkette aufstellen", "beide", "Burak", D(8,1), "mittel", ""),
    ("Tank-Standort mit 110%-Containment festlegen", "Headload", "Burak", D(7,30), "hoch", ""),
]
r = 2
for i, (name, pk, ow, term, prio, bem) in enumerate(au, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=pk); ws.cell(row=r, column=4, value=ow)
    ws.cell(row=r, column=5, value=term).number_format = "DD.MM.YYYY"
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
add_dv(ws, "Burak,Stefan,Markus,Ann-Kathrin,Sarah,Samuel,Stephan Marty,Aggreko,DPR", f"D2:D{last}")
add_dv(ws, STATUS_LIST, f"F2:F{last}")
add_dv(ws, "hoch,mittel,niedrig", f"G2:G{last}")
status_cf(ws, "F", 2, last)
ws.conditional_formatting.add(f"G2:G{last}", CellIsRule(operator="equal", formula=['"hoch"'],
    font=Font(name=FONT_NAME, bold=True, color=ORANGE)))
ws.conditional_formatting.add(f"E2:E{last}",
    FormulaRule(formula=['AND($E2<TODAY(),$F2<>"erledigt",$E2<>"")'],
                fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, color=RED_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 5) PERSONAL & ZUTRITT
ws = wb.create_sheet("Personal & Zutritt")
cols = ["Nr.", "Name", "Firma", "Rolle", "Entsendemeldung", "WORKcontrol-Badge",
        "Site Induction", "Status", "Bemerkung"]
widths(ws, [6, 26, 12, 22, 16, 18, 15, 13, 30])
header_row(ws, 1, cols)
pers = [
    ("Uecoez, Burak", "MiT", "Projektleiter", "n.a.", "n.a.", None, "in Arbeit", "Gesamtkoordination"),
    ("N.N. (PL Aggreko DE)", "Aggreko", "Projektleiter", "offen", "offen", None, "offen", "Benennung ausstehend"),
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
# Ampel: offene Pflichtschritte rot, erledigt gruen
for col in ("E", "F"):
    ws.conditional_formatting.add(f"{col}2:{col}{last}", CellIsRule(operator="equal", formula=['"offen"'],
        fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, color=RED_TXT)))
    ws.conditional_formatting.add(f"{col}2:{col}{last}", CellIsRule(operator="equal", formula=['"bestaetigt"'],
        fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
    ws.conditional_formatting.add(f"{col}2:{col}{last}", CellIsRule(operator="equal", formula=['"erhalten"'],
        fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.conditional_formatting.add(f"H2:H{last}", CellIsRule(operator="equal", formula=['"bereit"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 6) OFFENE PUNKTE & RISIKEN
ws = wb.create_sheet("Offene Punkte & Risiken")
cols = ["Nr.", "Typ", "Beschreibung", "Auswirkung", "Owner", "Termin", "Status", "Massnahme"]
widths(ws, [6, 16, 52, 13, 14, 14, 13, 44])
header_row(ws, 1, cols)
rk = [
    ("Risiko", "PO-Rechenfehler: 78 vs. 110 Tage (ca. EUR 87'700 Differenz)", "hoch", "Burak", D(7,17), "Redline an DPR mit korrigierter Tagesberechnung"),
    ("Risiko", "PO-Rechenfehler: 131 vs. 110 Tage, Enddatum 02.11. falsch abgeleitet", "hoch", "Burak", D(7,17), "Enddatum und Tageszahl in PO korrigieren"),
    ("Offener Punkt", "Parteien auf Mobil in Time AG umschreiben + eigene NDA", "hoch", "Burak", D(7,18), "PO-Parteien anpassen, NDA MiT-DPR anstossen"),
    ("Entscheid", "Festpreis DPR vs. Aufwandspreise Aggreko - Margen-/Modellrisiko", "hoch", "Stefan", D(7,18), "Preismodell final abstimmen"),
    ("Risiko", "FX-Risiko EUR/CHF (Einkauf EUR, Verkauf CHF)", "mittel", "Stefan", D(7,17), "Kurs/Absicherung mit Olli entscheiden"),
    ("Offener Punkt", "Keine schriftliche Aggreko-Terminbestaetigung 03.08. / 17.08.", "hoch", "Burak", D(7,20), "Schriftliche Bestaetigung einholen"),
    ("Risiko", "Entsendefrist Aggreko-Personal 24.07.", "hoch", "Aggreko", D(7,24), "Entsendemeldung fristgerecht einreichen"),
    ("Offener Punkt", "Waermeabfuhr 8 MW als DPR-Verantwortung klaeren", "hoch", "DPR", D(7,24), "Schriftliche Bestaetigung DPR-Verantwortung"),
    ("Risiko", "NDA-Sperre: kein Vantage-Kontakt, keine Aussenkommunikation", "hoch", "Burak", D(7,16), "Kommunikation ausschliesslich ueber DPR"),
]
r = 2
for i, (typ, besch, ausw, ow, term, mass) in enumerate(rk, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=typ)
    ws.cell(row=r, column=3, value=besch); ws.cell(row=r, column=4, value=ausw)
    ws.cell(row=r, column=5, value=ow)
    ws.cell(row=r, column=6, value=term).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=7, value="offen"); ws.cell(row=r, column=8, value=mass)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 2, 4, 6, 7):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Risiken", 1, last, len(cols))
add_dv(ws, "Risiko,Offener Punkt,Entscheid", f"B2:B{last}")
add_dv(ws, "hoch,mittel,niedrig", f"D2:D{last}")
add_dv(ws, STATUS_LIST, f"G2:G{last}")
status_cf(ws, "G", 2, last)
ws.conditional_formatting.add(f"D2:D{last}", CellIsRule(operator="equal", formula=['"hoch"'],
    fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, bold=True, color=RED_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 7) DOKUMENTE
ws = wb.create_sheet("Dokumente")
cols = ["Nr.", "Dokument", "Version/Datum", "Quelle", "Ablageort SharePoint", "Status"]
widths(ws, [6, 50, 16, 12, 40, 14])
header_row(ws, 1, cols)
SP = "[SharePoint-Projektordner]"
dok = [
    ("Angebot Aggreko P-640380-3 (Loadbank 6 MVA)", "", "Aggreko"),
    ("Angebot Aggreko P-650395-2 (Headload 8 MW)", "", "Aggreko"),
    ("Purchase Order 49A (Loadbank)", "", "DPR"),
    ("Purchase Order 49B (Headload)", "", "DPR"),
    ("NDA MiT-DPR", "", "MiT"),
    ("Versicherungsnachweis", "", "MiT"),
    ("Logistikplan", "", "MiT"),
    ("Supplemental Conditions", "", "DPR"),
    ("Compliance-Unterlagen", "", "DPR"),
    ("EHS-Plan Rev. 4", "Rev. 4", "DPR"),
]
dok += [("Einzelanalyse %02d" % k, "", "MiT") for k in range(1, 12)]
dok += [("Projektdossier (Gesamtuebersicht)", "", "MiT")]
r = 2
for i, (name, ver, q) in enumerate(dok, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=ver); ws.cell(row=r, column=4, value=q)
    ws.cell(row=r, column=5, value=SP); ws.cell(row=r, column=6, value="Entwurf")
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

# ================================================================ 8) KONTAKTE
ws = wb.create_sheet("Kontakte")
cols = ["Nr.", "Funktion", "Name", "Firma", "Telefon", "E-Mail", "Verfuegbarkeit", "Bemerkung"]
widths(ws, [6, 30, 24, 12, 20, 28, 16, 30])
header_row(ws, 1, cols)
kon = [
    ("Projektleiter MiT", "Burak Uecoez", "MiT", "[eintragen]", "[eintragen]", "Buerozeiten", "Gesamtverantwortung"),
    ("DPR Bauleitung / Site Contact", "N.N.", "DPR", "[eintragen]", "[eintragen]", "Buerozeiten", "Hauptauftraggeber"),
    ("Projektleiter Aggreko DE", "N.N.", "Aggreko", "[eintragen]", "[eintragen]", "Buerozeiten", "Benennung ausstehend"),
    ("Aggreko Service-Hotline", "-", "Aggreko", "[eintragen]", "-", "24/7", "Technische Stoerungen"),
    ("MiT Notfall / Bereitschaft", "N.N.", "MiT", "[eintragen]", "-", "Bereitschaft", "24/7-Kontaktkette"),
    ("EHS / Sicherheit DPR", "N.N.", "DPR", "[eintragen]", "[eintragen]", "Buerozeiten", "EHS-Plan Rev. 4"),
]
r = 2
for i, (funk, name, firma, tel, mail, verf, bem) in enumerate(kon, 1):
    ws.cell(row=r, column=1, value=i); ws.cell(row=r, column=2, value=funk)
    ws.cell(row=r, column=3, value=name); ws.cell(row=r, column=4, value=firma)
    ws.cell(row=r, column=5, value=tel); ws.cell(row=r, column=6, value=mail)
    ws.cell(row=r, column=7, value=verf); ws.cell(row=r, column=8, value=bem)
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 4, 7):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Kontakte", 1, last, len(cols))
add_dv(ws, "Aggreko,MiT,DPR", f"D2:D{last}")
add_dv(ws, "24/7,Buerozeiten,Bereitschaft", f"G2:G{last}")
ws.conditional_formatting.add(f"G2:G{last}", CellIsRule(operator="equal", formula=['"24/7"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, bold=True, color=GREEN_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 9) AENDERUNGSLOG
ws = wb.create_sheet("Aenderungslog")
cols = ["Datum", "Wer", "Was geaendert"]
widths(ws, [16, 20, 80])
header_row(ws, 1, cols)
log = [
    (D(7,15), "Burak Uecoez", "Projektsteuerungs-Tool erstellt und mit Projektdaten vorbefuellt."),
    (D(7,15), "Burak Uecoez", "Erweiterung: Terminplan (Gantt), Personal & Zutritt, Kontakte, Dashboard-Kennzahlen (Fortschritt, Countdowns, Ampel)."),
]
r = 2
for datum, wer, was in log:
    ws.cell(row=r, column=1, value=datum).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=2, value=wer); ws.cell(row=r, column=3, value=was)
    r += 1
for _ in range(20):
    ws.cell(row=r, column=1).number_format = "DD.MM.YYYY"
    r += 1
last = r - 1
body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    ws.cell(row=rr, column=1).alignment = center
make_table(ws, "Aenderungslog", 1, last, len(cols))
page_setup(ws, freeze="A2")

# ---------------------------------------------------------------- Speichern
wb.properties.creator = "Mobil in Time AG"
wb.properties.title = "Projektsteuerung MiT-PWR-WIN-2026-001"
wb.properties.subject = "DPR / Vantage ZRH12 Winterthur"
out = "/home/user/Burak/Projektsteuerung_MiT-PWR-WIN-2026-001.xlsx"
wb.save(out)
print("Gespeichert:", out)
print("Blaetter:", wb.sheetnames)
