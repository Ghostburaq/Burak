# -*- coding: utf-8 -*-
"""
Projektsteuerungs-Tool MiT-PWR-WIN-2026-001
Erstellt eine SharePoint-taugliche .xlsx (ohne Makros) mit 6 Registerblaettern.
Schweizer Schreibweise (ss statt scharfes S). Farben: Navy #1F3A5F, Orange #E8740C.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.worksheet.formula import ArrayFormula

# ---------------------------------------------------------------- Farben / Stile
NAVY = "1F3A5F"
ORANGE = "E8740C"
WHITE = "FFFFFF"
LIGHT = "F2F5F9"       # helle Zeilenfuellung
GREEN = "C6EFCE"       # erledigt
GREEN_TXT = "006100"
RED = "FFC7CE"         # kritisch / ueberfaellig
RED_TXT = "9C0006"
ORANGE_FILL = "FFE4C4" # ueberfaellig hell
ORANGE_TXT = "9C4A00"
YELLOW = "FFEB9C"      # in Arbeit
YELLOW_TXT = "9C6500"
GREY = "D9D9D9"

FONT_NAME = "Arial"

hdr_font = Font(name=FONT_NAME, size=10, bold=True, color=WHITE)
hdr_fill = PatternFill("solid", fgColor=NAVY)
title_font = Font(name=FONT_NAME, size=16, bold=True, color=NAVY)
sub_font = Font(name=FONT_NAME, size=11, bold=True, color=ORANGE)
label_font = Font(name=FONT_NAME, size=10, bold=True, color=NAVY)
base_font = Font(name=FONT_NAME, size=10, color="000000")
kpi_num_font = Font(name=FONT_NAME, size=20, bold=True, color=NAVY)
kpi_lbl_font = Font(name=FONT_NAME, size=9, bold=True, color="404040")

thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left = Alignment(horizontal="left", vertical="center", wrap_text=True)
left_top = Alignment(horizontal="left", vertical="top", wrap_text=True)

STATUS_LIST = "offen,in Arbeit,erledigt,verschoben,kritisch"
STATUS_DOK = "Entwurf,final,signiert,ueberholt"

wb = Workbook()

# ---------------------------------------------------------------- Hilfsfunktionen
def style_header(ws, row, ncols, start_col=1):
    for c in range(start_col, start_col + ncols):
        cell = ws.cell(row=row, column=c)
        cell.font = hdr_font
        cell.fill = hdr_fill
        cell.alignment = center
        cell.border = border

def style_body(ws, first_row, last_row, ncols, start_col=1, align=left_top):
    for r in range(first_row, last_row + 1):
        for c in range(start_col, start_col + ncols):
            cell = ws.cell(row=r, column=c)
            cell.font = base_font
            cell.alignment = align
            cell.border = border

def set_widths(ws, widths, start_col=1):
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(start_col + i)].width = w

def make_table(ws, name, first_row, last_row, ncols, start_col=1):
    ref = f"{get_column_letter(start_col)}{first_row}:{get_column_letter(start_col+ncols-1)}{last_row}"
    tbl = Table(displayName=name, ref=ref)
    tbl.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False,
        showRowStripes=True, showColumnStripes=False)
    ws.add_table(tbl)

def page_setup(ws, freeze="A1"):
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    ws.freeze_panes = freeze

def status_cond_fmt(ws, col_letter, first, last):
    """Bedingte Formatierung fuer eine Status-Spalte."""
    rng = f"{col_letter}{first}:{col_letter}{last}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"erledigt"'],
        fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"kritisch"'],
        fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, color=RED_TXT)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"in Arbeit"'],
        fill=PatternFill("solid", fgColor=YELLOW), font=Font(name=FONT_NAME, color=YELLOW_TXT)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"verschoben"'],
        fill=PatternFill("solid", fgColor=ORANGE_FILL), font=Font(name=FONT_NAME, color=ORANGE_TXT)))

def add_dv(ws, formula, cell_range):
    dv = DataValidation(type="list", formula1=f'"{formula}"', allow_blank=True)
    dv.error = "Bitte einen Wert aus der Liste waehlen."
    dv.errorTitle = "Ungueltige Eingabe"
    dv.prompt = "Wert aus Dropdown waehlen"
    ws.add_data_validation(dv)
    dv.add(cell_range)
    return dv

# ================================================================ 1) DASHBOARD
ws = wb.active
ws.title = "Dashboard"
ws.sheet_view.showGridLines = False
set_widths(ws, [3, 26, 30, 6, 24, 22, 22, 18])

ws["B2"] = "PROJEKTSTEUERUNG"
ws["B2"].font = title_font
ws["B3"] = "MiT-PWR-WIN-2026-001  |  DPR Construction / Vantage Datacenter ZRH12"
ws["B3"].font = sub_font

# Projektstammdaten
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
    c = ws.cell(row=r, column=3, value=val)
    c.font = base_font
    c.alignment = left
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
    for cc in range(2, 6):
        ws.cell(row=r, column=cc).border = border
    r += 1

# KPI-Zusammenfassung (ZAEHLENWENN auf Aufgaben)
kpi_row = 5
ws.cell(row=kpi_row - 1, column=6, value="AUFGABEN-STATUS").font = sub_font
kpis = [
    ("Offen", '=COUNTIF(Aufgaben[Status],"offen")', LIGHT),
    ("In Arbeit", '=COUNTIF(Aufgaben[Status],"in Arbeit")', YELLOW),
    ("Erledigt", '=COUNTIF(Aufgaben[Status],"erledigt")', GREEN),
    ("Kritisch / blockiert", '=COUNTIF(Aufgaben[Status],"kritisch")', RED),
    ("Ueberfaellig (offen & Termin < heute)",
     '=SUMPRODUCT((Aufgaben[Status]<>"erledigt")*(Aufgaben[Termin]<>"")*(Aufgaben[Termin]<TODAY()))', RED),
]
rr = kpi_row
for lbl, formula, fill in kpis:
    lc = ws.cell(row=rr, column=6, value=lbl)
    lc.font = kpi_lbl_font
    lc.alignment = left
    lc.border = border
    lc.fill = PatternFill("solid", fgColor=fill)
    vc = ws.cell(row=rr, column=7, value=formula)
    vc.font = kpi_num_font
    vc.alignment = center
    vc.border = border
    vc.fill = PatternFill("solid", fgColor=fill)
    rr += 1

# Meilenstein-Ampel
ws.cell(row=rr, column=6, value="MEILENSTEINE").font = sub_font
rr += 1
ms_kpis = [
    ("Meilensteine gesamt", '=COUNTA(Meilensteine[Nr.])'),
    ("davon erledigt", '=COUNTIF(Meilensteine[Status],"erledigt")'),
    ("davon kritisch", '=COUNTIF(Meilensteine[Status],"kritisch")'),
]
for lbl, formula in ms_kpis:
    lc = ws.cell(row=rr, column=6, value=lbl)
    lc.font = kpi_lbl_font; lc.alignment = left; lc.border = border
    vc = ws.cell(row=rr, column=7, value=formula)
    vc.font = Font(name=FONT_NAME, size=12, bold=True, color=NAVY)
    vc.alignment = center; vc.border = border
    rr += 1

# Naechste 3 Meilensteine
next_row = 16
ws.cell(row=next_row, column=2, value="NAECHSTE MEILENSTEINE").font = sub_font
hdrs = ["Plantermin", "Meilenstein", "Status"]
for i, h in enumerate(hdrs):
    c = ws.cell(row=next_row + 1, column=2 + i, value=h)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
ws.merge_cells(start_row=next_row + 1, start_column=3, end_row=next_row + 1, end_column=4)
# Drei kleinste Plantermine >= heute (KKLEINSTE ueber Plantermine), Status noch nicht erledigt
for k in range(1, 4):
    rowi = next_row + 1 + k
    # Plantermin: k-t-kleinster Plantermin, offen und >= heute.
    # AGGREGATE(15=KKLEINSTE, 6=Fehler ignorieren) verarbeitet das Array ohne CSE-Eingabe.
    f_term = ('=IFERROR(AGGREGATE(15,6,Meilensteine!$C$2:$C$17/'
              '((Meilensteine!$E$2:$E$17<>"erledigt")*(Meilensteine!$C$2:$C$17>=TODAY())),%d),"")' % k)
    tc = ws.cell(row=rowi, column=2, value=f_term)
    tc.number_format = "DD.MM.YYYY"; tc.font = base_font; tc.alignment = center; tc.border = border
    # Meilenstein-Bezeichnung via INDEX/VERGLEICH auf diesen Termin
    f_name = ('=IFERROR(INDEX(Meilensteine!$B$2:$B$17,MATCH(B%d,Meilensteine!$C$2:$C$17,0)),"")' % rowi)
    nc = ws.cell(row=rowi, column=3, value=f_name)
    nc.font = base_font; nc.alignment = left; nc.border = border
    ws.merge_cells(start_row=rowi, start_column=3, end_row=rowi, end_column=4)
    ws.cell(row=rowi, column=4).border = border
    f_stat = ('=IFERROR(INDEX(Meilensteine!$E$2:$E$17,MATCH(B%d,Meilensteine!$C$2:$C$17,0)),"")' % rowi)
    sc = ws.cell(row=rowi, column=5, value=f_stat)
    sc.font = base_font; sc.alignment = center; sc.border = border

ws.cell(row=next_row + 6, column=2,
        value="Hinweis: Werte aktualisieren sich automatisch aus den Registerblaettern. "
              "Keine Pivot-Tabellen - reine Formeln (ZAEHLENWENN / INDEX / VERGLEICH).").font = \
    Font(name=FONT_NAME, size=8, italic=True, color="808080")
ws.merge_cells(start_row=next_row + 6, start_column=2, end_row=next_row + 6, end_column=8)

# Array-Formeln in aelteren Engines: als Matrixformel markieren (Plantermin-Suche)
page_setup(ws, freeze="A1")
ws.print_area = "A1:H24"

# ================================================================ 2) MEILENSTEINE
ws = wb.create_sheet("Meilensteine")
cols = ["Nr.", "Meilenstein", "Plantermin", "Ist-Termin", "Status", "Verantwortlich", "Bemerkung"]
widths = [6, 46, 14, 14, 14, 18, 40]
set_widths(ws, widths)
for i, h in enumerate(cols, 1):
    ws.cell(row=1, column=i, value=h)
style_header(ws, 1, len(cols))

# (Plantermin, Ist-Termin sind Datumsobjekte; Jahr 2026)
import datetime
D = lambda m, d, hh=0, mm=0: datetime.datetime(2026, m, d, hh, mm)
ms_data = [
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
for i, (name, term, verant, bem) in enumerate(ms_data, 1):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2, value=name)
    tc = ws.cell(row=r, column=3, value=term)
    tc.number_format = "DD.MM.YYYY" if term.hour == 0 else "DD.MM.YYYY hh:mm"
    ws.cell(row=r, column=4, value=None)  # Ist-Termin
    ws.cell(row=r, column=4).number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=5, value="offen")
    ws.cell(row=r, column=6, value=verant)
    ws.cell(row=r, column=7, value=bem)
    r += 1
last = r - 1
style_body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    ws.cell(row=rr, column=1).alignment = center
    ws.cell(row=rr, column=3).alignment = center
    ws.cell(row=rr, column=4).alignment = center
    ws.cell(row=rr, column=5).alignment = center
make_table(ws, "Meilensteine", 1, last, len(cols))
add_dv(ws, STATUS_LIST, f"E2:E{last}")
status_cond_fmt(ws, "E", 2, last)
# Ueberfaellig: Plantermin < heute und Status <> erledigt -> orange (Spalte Plantermin)
ws.conditional_formatting.add(f"C2:C{last}",
    FormulaRule(formula=['AND($C2<TODAY(),$E2<>"erledigt",$C2<>"")'],
                fill=PatternFill("solid", fgColor=ORANGE_FILL), font=Font(name=FONT_NAME, color=ORANGE_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 3) AUFGABEN
ws = wb.create_sheet("Aufgaben")
cols = ["Nr.", "Aufgabe", "Paket", "Owner", "Termin", "Status", "Prioritaet", "Bemerkung", "Erledigt am"]
widths = [6, 50, 12, 14, 14, 13, 12, 34, 14]
set_widths(ws, widths)
for i, h in enumerate(cols, 1):
    ws.cell(row=1, column=i, value=h)
style_header(ws, 1, len(cols))

# (Aufgabe, Paket, Owner, Termin, Prioritaet, Bemerkung)
auf_data = [
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
for i, (name, paket, owner, term, prio, bem) in enumerate(auf_data, 1):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=paket)
    ws.cell(row=r, column=4, value=owner)
    tc = ws.cell(row=r, column=5, value=term)
    tc.number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=6, value="offen")
    ws.cell(row=r, column=7, value=prio)
    ws.cell(row=r, column=8, value=bem)
    ws.cell(row=r, column=9, value=None).number_format = "DD.MM.YYYY"
    r += 1
last = r - 1
style_body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 5, 6, 7, 9):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Aufgaben", 1, last, len(cols))
add_dv(ws, "Loadbank,Headload,beide,Admin", f"C2:C{last}")
add_dv(ws, "Burak,Stefan,Markus,Ann-Kathrin,Sarah,Samuel,Stephan Marty,Aggreko,DPR", f"D2:D{last}")
add_dv(ws, STATUS_LIST, f"F2:F{last}")
add_dv(ws, "hoch,mittel,niedrig", f"G2:G{last}")
status_cond_fmt(ws, "F", 2, last)
# Prioritaet hoch -> orange Text
ws.conditional_formatting.add(f"G2:G{last}", CellIsRule(operator="equal", formula=['"hoch"'],
    font=Font(name=FONT_NAME, bold=True, color=ORANGE)))
# Ueberfaellige Aufgaben: Termin < heute & nicht erledigt -> ganze Termin-Zelle rot
ws.conditional_formatting.add(f"E2:E{last}",
    FormulaRule(formula=['AND($E2<TODAY(),$F2<>"erledigt",$E2<>"")'],
                fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, color=RED_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 4) OFFENE PUNKTE & RISIKEN
ws = wb.create_sheet("Offene Punkte & Risiken")
cols = ["Nr.", "Typ", "Beschreibung", "Auswirkung", "Owner", "Termin", "Status", "Massnahme"]
widths = [6, 16, 52, 13, 14, 14, 13, 44]
set_widths(ws, widths)
for i, h in enumerate(cols, 1):
    ws.cell(row=1, column=i, value=h)
style_header(ws, 1, len(cols))

risk_data = [
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
for i, (typ, besch, ausw, owner, term, mass) in enumerate(risk_data, 1):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2, value=typ)
    ws.cell(row=r, column=3, value=besch)
    ws.cell(row=r, column=4, value=ausw)
    ws.cell(row=r, column=5, value=owner)
    tc = ws.cell(row=r, column=6, value=term)
    tc.number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=7, value="offen")
    ws.cell(row=r, column=8, value=mass)
    r += 1
last = r - 1
style_body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 2, 4, 6, 7):
        ws.cell(row=rr, column=cc).alignment = center
make_table(ws, "Risiken", 1, last, len(cols))
add_dv(ws, "Risiko,Offener Punkt,Entscheid", f"B2:B{last}")
add_dv(ws, "hoch,mittel,niedrig", f"D2:D{last}")
add_dv(ws, STATUS_LIST, f"G2:G{last}")
status_cond_fmt(ws, "G", 2, last)
ws.conditional_formatting.add(f"D2:D{last}", CellIsRule(operator="equal", formula=['"hoch"'],
    fill=PatternFill("solid", fgColor=RED), font=Font(name=FONT_NAME, bold=True, color=RED_TXT)))
page_setup(ws, freeze="A2")

# ================================================================ 5) DOKUMENTE
ws = wb.create_sheet("Dokumente")
cols = ["Nr.", "Dokument", "Version/Datum", "Quelle", "Ablageort SharePoint", "Status"]
widths = [6, 50, 16, 12, 40, 14]
set_widths(ws, widths)
for i, h in enumerate(cols, 1):
    ws.cell(row=1, column=i, value=h)
style_header(ws, 1, len(cols))

SP = "[SharePoint-Projektordner]"
dok_data = [
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
    ("Einzelanalyse 01", "", "MiT"),
    ("Einzelanalyse 02", "", "MiT"),
    ("Einzelanalyse 03", "", "MiT"),
    ("Einzelanalyse 04", "", "MiT"),
    ("Einzelanalyse 05", "", "MiT"),
    ("Einzelanalyse 06", "", "MiT"),
    ("Einzelanalyse 07", "", "MiT"),
    ("Einzelanalyse 08", "", "MiT"),
    ("Einzelanalyse 09", "", "MiT"),
    ("Einzelanalyse 10", "", "MiT"),
    ("Einzelanalyse 11", "", "MiT"),
    ("Projektdossier (Gesamtuebersicht)", "", "MiT"),
]
r = 2
for i, (name, ver, quelle) in enumerate(dok_data, 1):
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=ver)
    ws.cell(row=r, column=4, value=quelle)
    ws.cell(row=r, column=5, value=SP)
    ws.cell(row=r, column=6, value="Entwurf")
    r += 1
last = r - 1
style_body(ws, 2, last, len(cols))
for rr in range(2, last + 1):
    for cc in (1, 3, 4, 6):
        ws.cell(row=rr, column=cc).alignment = center
    ws.cell(row=rr, column=5).font = Font(name=FONT_NAME, size=10, color="808080", italic=True)
make_table(ws, "Dokumente", 1, last, len(cols))
add_dv(ws, "DPR,Aggreko,MiT", f"D2:D{last}")
add_dv(ws, STATUS_DOK, f"F2:F{last}")
# Status-Formatierung Dokumente
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"signiert"'],
    fill=PatternFill("solid", fgColor=GREEN), font=Font(name=FONT_NAME, color=GREEN_TXT)))
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"final"'],
    fill=PatternFill("solid", fgColor=YELLOW), font=Font(name=FONT_NAME, color=YELLOW_TXT)))
ws.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"ueberholt"'],
    fill=PatternFill("solid", fgColor=GREY), font=Font(name=FONT_NAME, color="808080")))
page_setup(ws, freeze="A2")

# ================================================================ 6) AENDERUNGSLOG
ws = wb.create_sheet("Aenderungslog")
cols = ["Datum", "Wer", "Was geaendert"]
widths = [16, 20, 80]
set_widths(ws, widths)
for i, h in enumerate(cols, 1):
    ws.cell(row=1, column=i, value=h)
style_header(ws, 1, len(cols))
log_seed = [
    (D(7,16), "Burak Uecoez", "Projektsteuerungs-Tool erstellt und mit Projektdaten vorbefuellt."),
]
r = 2
for datum, wer, was in log_seed:
    dc = ws.cell(row=r, column=1, value=datum); dc.number_format = "DD.MM.YYYY"
    ws.cell(row=r, column=2, value=wer)
    ws.cell(row=r, column=3, value=was)
    r += 1
# leere Zeilen fuer kuenftige Eintraege
for _ in range(20):
    ws.cell(row=r, column=1).number_format = "DD.MM.YYYY"
    r += 1
last = r - 1
style_body(ws, 2, last, len(cols))
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
