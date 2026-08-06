#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt das Gym-Logbuch Beintraining in zwei Fassungen.

    python3 build_gymlogbuch.py preop  ->  GymLogbuch_Beine_PreOP.xlsx
    python3 build_gymlogbuch.py reha   ->  GymLogbuch_Beine.xlsx

Bewusst schlank gehalten: vier gemeinsame Blätter plus ein Reha-Teil.
'Plan' ist das einzige Blatt zum Steuern, 'Trainingsblatt' das einzige zum
Ausdrucken, 'Log' das einzige zum Eintragen, 'Verlauf' die Kontrolle.

Rohdaten der Einheiten 1-4 stehen in daten.py, die Reha-Texte in
reha_daten.py.
"""

import datetime
import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.pagebreak import Break
from openpyxl.formatting.rule import FormulaRule, ColorScaleRule
from openpyxl.chart import BarChart, LineChart, Reference

from daten import ROWS
import reha_daten as RD

MODUS = sys.argv[1] if len(sys.argv) > 1 else "reha"
if MODUS not in ("reha", "preop"):
    raise SystemExit("Aufruf: build_gymlogbuch.py [reha|preop]")
PREOP = MODUS == "preop"
OP_DATUM = datetime.date(2026, 9, 30)
DATEI = "GymLogbuch_Beine_PreOP.xlsx" if PREOP else "GymLogbuch_Beine.xlsx"

LOG_ROWS = 900          # Satzzeilen, rund 60 Einheiten
EINHEITEN = 12          # Spalten im Verlauf
MAX_EINHEIT = 60        # Obergrenze für Einheit-Nummern in Formeln
BLATT_KOPIEN = 4        # Trainingsblätter je Block auf Vorrat
REHALOG_ROWS = 180

LOG_FIRST, LOG_LAST = 4, 3 + LOG_ROWS
WARMUP_FAKTOR = [0.45, 0.70]

# --------------------------------------------------------------------------
# Übungen. Reihenfolge = Reihenfolge überall im Logbuch.
# --------------------------------------------------------------------------
UEBUNGEN = [
    dict(name="Beinpresse", block="Beine vorne", von=8, bis=12, saetze=3,
         schritt=5, start=None, maxlast=None, letzter="A", aktiv=True,
         reha_ab=2,
         hinweis="Tiefe Fussposition, Hände seitlich ablegen statt an den "
                 "Griffen ziehen. Ersetzt Hackenschmidt und Lunges."),
    dict(name="Split Squat", block="Beine vorne", von=8, bis=10, saetze=3,
         schritt=5, start=None, maxlast=None, letzter="A", aktiv=True,
         reha_ab=8,
         hinweis="Je Bein. Ersatz in der Sperrzeit: Beinpresse einbeinig."),
    dict(name="Beinstrecker", block="Beine vorne", von=12, bis=15, saetze=3,
         schritt=5, start=None, maxlast=None, letzter="R", aktiv=True,
         reha_ab=1,
         hinweis="Dritter Satz als Reduktionssatz. Hände in den Schoss."),
    dict(name="Adduktion", block="Beine vorne", von=15, bis=20, saetze=3,
         schritt=2.5, start=None, maxlast=152.5, letzter="R", aktiv=True,
         reha_ab=1,
         hinweis="152.5 kg ist Stackende. Weiter über 3 s Exzentrik und 1 s "
                 "Pause in der Dehnung, nicht über Last."),
    dict(name="Rumänisches Kreuzheben", block="Beine hinten", von=8, bis=10,
         saetze=3, schritt=2.5, start=None, maxlast=None, letzter="A",
         aktiv=True, reha_ab=12,
         hinweis="Ersetzt Kickback. Ersatz in der Sperrzeit: Beinbeuger "
                 "sitzend."),
    dict(name="Hip Thrust", block="Beine hinten", von=8, bis=12, saetze=3,
         schritt=10, start=None, maxlast=None, letzter="A", aktiv=True,
         reha_ab=4,
         hinweis="Gesamtgewicht inkl. Stange notieren. Ersatz: Hip Thrust "
                 "Maschine ab Woche 2."),
    dict(name="Beinbeuger", block="Beine hinten", von=10, bis=12, saetze=3,
         schritt=5, start=None, maxlast=None, letzter="R", aktiv=True,
         reha_ab=1,
         hinweis="Sitzend. Dritter Satz als Reduktionssatz."),
    dict(name="Seitliche Kickbacks", block="Beine hinten", von=15, bis=20,
         saetze=3, schritt=5, start=None, maxlast=None, letzter="A",
         aktiv=True, reha_ab=2,
         hinweis="Gluteus medius. Ersatz: Abduktion an der Maschine "
                 "sitzend."),
    dict(name="Waden", block="Beine hinten", von=10, bis=15, saetze=3,
         schritt=5, start=None, maxlast=None, letzter="A", aktiv=True,
         reha_ab=2,
         hinweis="Sitzend ab Woche 1, stehend ab Woche 4."),
    dict(name="Lunges", block="Beine vorne", von=10, bis=12, saetze=None,
         schritt=None, start=None, maxlast=None, letzter="A", aktiv=False,
         reha_ab=None, hinweis="Archiv. Redundant zum Split Squat."),
    dict(name="Kickback", block="Beine hinten", von=10, bis=15, saetze=None,
         schritt=None, start=None, maxlast=None, letzter="A", aktiv=False,
         reha_ab=None, hinweis="Archiv. Von Hip Thrust und RDL abgedeckt."),
]
BLOCKS = ["Beine vorne", "Beine hinten"]
EX_SLOTS = len(UEBUNGEN) + 3

# --------------------------------------------------------------------------
# Design
# --------------------------------------------------------------------------
FONT = "Arial"
NAVY, NAVY_D, STEEL = "1F3A5F", "142A44", "3D6288"
LIGHT, INPUT, CALC = "EDF1F6", "FFF6D5", "F5F8FB"
AMBER, GREEN, RED, GRID = "B45309", "15803D", "B91C1C", "AEBACA"

thin = Side(style="thin", color=GRID)
med = Side(style="medium", color=NAVY)
B_ALL = Border(left=thin, right=thin, top=thin, bottom=thin)

F_TITLE = Font(name=FONT, size=16, bold=True, color="FFFFFF")
F_SUB = Font(name=FONT, size=9, color="FFFFFF")
F_H1 = Font(name=FONT, size=10, bold=True, color="FFFFFF")
F_BODY = Font(name=FONT, size=10)
F_SMALL = Font(name=FONT, size=8.5, color="4A5568")
F_BOLD = Font(name=FONT, size=10, bold=True)
F_KPI = Font(name=FONT, size=18, bold=True, color=NAVY)
F_GRUEN = Font(name=FONT, size=12, bold=True, color=GREEN)

FILL_TITLE = PatternFill("solid", fgColor=NAVY_D)
FILL_HEAD = PatternFill("solid", fgColor=NAVY)
FILL_SUB = PatternFill("solid", fgColor=STEEL)
FILL_LIGHT = PatternFill("solid", fgColor=LIGHT)
FILL_INPUT = PatternFill("solid", fgColor=INPUT)
FILL_CALC = PatternFill("solid", fgColor=CALC)
FILL_WHITE = PatternFill("solid", fgColor="FFFFFF")
FILL_WORK = PatternFill("solid", fgColor="E7F2EA")
FILL_ROT = PatternFill("solid", fgColor="F8D7D7")

C = Alignment(horizontal="center", vertical="center")
L = Alignment(horizontal="left", vertical="center")
RE = Alignment(horizontal="right", vertical="center")
LW = Alignment(horizontal="left", vertical="top", wrap_text=True)
CW = Alignment(horizontal="center", vertical="center", wrap_text=True)
L_IND = Alignment(horizontal="left", vertical="center", indent=1)

NF_KG = '#,##0.0;-#,##0.0;"–"'
NF_INT = '#,##0;-#,##0;"–"'
NF_DATE = "DD.MM.YYYY"

wb = Workbook()
wb.remove(wb.active)


def sheet(name):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    return ws


def titel(ws, last_col, text, untertitel, first_col=1):
    for r, txt, fnt in ((1, text, F_TITLE), (2, untertitel, F_SUB)):
        ws.merge_cells(start_row=r, start_column=first_col, end_row=r,
                       end_column=last_col)
        c = ws.cell(r, first_col, txt)
        c.font, c.fill, c.alignment = fnt, FILL_TITLE, L_IND
        for col in range(first_col, last_col + 1):
            ws.cell(r, col).fill = FILL_TITLE
    ws.row_dimensions[1].height = 28
    ws.row_dimensions[2].height = 14


def kopf(ws, row, labels, widths=None, first_col=1, height=28):
    for i, lab in enumerate(labels):
        c = ws.cell(row, first_col + i, lab)
        c.font, c.fill, c.alignment, c.border = F_H1, FILL_HEAD, CW, B_ALL
    ws.row_dimensions[row].height = height
    if widths:
        for i, w in enumerate(widths):
            ws.column_dimensions[get_column_letter(first_col + i)].width = w


def balken(ws, row, first_col, last_col, text, fill=FILL_SUB):
    ws.merge_cells(start_row=row, start_column=first_col, end_row=row,
                   end_column=last_col)
    c = ws.cell(row, first_col, text)
    c.font, c.fill, c.alignment = F_H1, fill, L_IND
    for col in range(first_col, last_col + 1):
        ws.cell(row, col).fill = fill
    ws.row_dimensions[row].height = 18


def hoehe(text, breite=100, zeile=12.5, minimum=16):
    return max(minimum, max(1, -(-len(text) // breite)) * zeile + 5)


def infozeile(ws, row, last_col, text, fett=False):
    ws.merge_cells(start_row=row, start_column=1, end_row=row,
                   end_column=last_col)
    c = ws.cell(row, 1, text)
    c.font = F_BOLD if fett else F_SMALL
    c.alignment = LW
    ws.row_dimensions[row].height = hoehe(text, breite=last_col * 9)
    return row + 1


def druck(ws, area, quer=False, titles=None, rand=None, fuss=None):
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "landscape" if quer else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_area = area
    if titles:
        ws.print_title_rows = titles
    ws.print_options.horizontalCentered = True
    m = rand or (0.45, 0.35, 0.55, 0.5)
    ws.page_margins.left, ws.page_margins.right = m[0], m[1]
    ws.page_margins.top, ws.page_margins.bottom = m[2], m[3]
    ws.page_margins.header, ws.page_margins.footer = 0.25, 0.25
    ws.oddHeader.left.text = "Gym Logbuch  |  Beine"
    ws.oddHeader.left.size, ws.oddHeader.left.color = 8, "909090"
    ws.oddHeader.right.text = ws.title
    ws.oddHeader.right.size, ws.oddHeader.right.color = 8, "909090"
    if fuss:
        ws.oddFooter.left.text = fuss
        ws.oddFooter.left.size, ws.oddFooter.left.color = 8, "909090"
    ws.oddFooter.right.text = "Seite &P von &N"
    ws.oddFooter.right.size, ws.oddFooter.right.color = 8, "909090"


# Log: A Datum · B Einheit · C Übung · D Satz · E kg · F Wdh · G Volumen
def LR(col):
    return "Log!$%s$%d:$%s$%d" % (col, LOG_FIRST, col, LOG_LAST)


B_, C_, D_, E_, F_, G_ = (LR("B"), LR("C"), LR("D"), LR("E"), LR("F"),
                          LR("G"))

# ==========================================================================
# PLAN  -  das einzige Steuerblatt
# ==========================================================================
wsp = sheet("Plan")
SPALTEN = [
    ("Übung", 24), ("Wdh\nvon", 7), ("Wdh\nbis", 7), ("Sätze", 7),
    ("Schritt\n(kg)", 8), ("Start\n(kg)", 8), ("Max\n(kg)", 8),
    ("Aktiv", 7), ("frei ab\nWoche", 8),
    ("Status\nheute", 11), ("zuletzt", 15), ("HEUTE\n(kg)", 10),
    ("× Wdh", 8), ("Nächster Schritt", 32), ("gleiche\nLast seit", 9),
    # ab hier ausserhalb des Druckbereichs
    ("Hinweis", 44), ("Hilfsspalten →", 9), ("", 9), ("", 9),
]
LAST, DRUCK_LAST = len(SPALTEN), 15
titel(wsp, LAST, "PLAN  |  ALLES AUF EINEN BLICK",
      "Gelb sind deine Vorgaben, hellblau rechnet sich aus dem Log. Die "
      "grünen HEUTE-Spalten sagen, womit du die nächste Einheit startest.")

wsp.merge_cells(start_row=3, start_column=1, end_row=3, end_column=2)
wsp.cell(3, 1, "Woche nach OP" if not PREOP else "OP-Datum").font = F_BOLD
wsp.cell(3, 1).alignment = RE
wsp.merge_cells(start_row=3, start_column=3, end_row=3, end_column=4)
c = wsp.cell(3, 3, 1 if not PREOP else OP_DATUM)
c.font = Font(name=FONT, size=12, bold=True, color=NAVY)
c.fill, c.alignment, c.border = FILL_INPUT, C, B_ALL
c.number_format = NF_INT if not PREOP else NF_DATE
wsp.cell(3, 4).fill, wsp.cell(3, 4).border = FILL_INPUT, B_ALL
WOCHE = "'Plan'!$C$3"
wsp.merge_cells(start_row=3, start_column=5, end_row=3, end_column=DRUCK_LAST)
if PREOP:
    hint = ('="Noch "&MAX(0,$C$3-TODAY())&" Tage bis zur OP. Bis dahin läuft '
            'alles normal - die Spalte \'frei ab Woche\' zeigt schon jetzt, '
            'wie lange jede Übung danach ausfällt."')
else:
    hint = ('="Phase "&IF($C$3<=2,"1 Schutz",IF($C$3<=6,"2 Beweglichkeit",'
            'IF($C$3<=12,"3 erste Last",IF($C$3<=16,"4 Aufbau",'
            '"5 Rückkehr"))))&". Woche links anpassen - Status und '
            'Trainingsblatt ziehen sofort nach."')
c = wsp.cell(3, 5, hint)
c.font, c.alignment, c.fill = F_BODY, L_IND, FILL_CALC
wsp.row_dimensions[3].height = 22

balken(wsp, 4, 1, 9, "Deine Vorgaben  ·  hier änderst du den Plan")
balken(wsp, 4, 10, DRUCK_LAST, "Stand aus dem Log  ·  rechnet sich selbst")
kopf(wsp, 5, [x[0] for x in SPALTEN], [x[1] for x in SPALTEN], height=30)
for col in range(DRUCK_LAST + 1, LAST + 1):
    wsp.cell(5, col).fill = PatternFill("solid", fgColor="8A94A0")

PF = 6
PLAN_ROW = {}


def p(sp, row):
    return "$%s%d" % (sp, row)


row = PF
gruppen = [("Beine vorne", [u for u in UEBUNGEN
                            if u["block"] == "Beine vorne" and u["aktiv"]]),
           ("Beine hinten", [u for u in UEBUNGEN
                             if u["block"] == "Beine hinten" and u["aktiv"]]),
           ("Archiv  ·  nicht mehr im Plan, Historie bleibt erhalten",
            [u for u in UEBUNGEN if not u["aktiv"]])]
for gruppe, liste in gruppen:
    balken(wsp, row, 1, LAST, gruppe, FILL_LIGHT)
    wsp.cell(row, 1).font = Font(name=FONT, size=10, bold=True, color=NAVY)
    row += 1
    for u in liste + ([None] if gruppe.startswith("Beine") else []):
        PLAN_ROW[u["name"] if u else "_leer%d" % row] = row
        ex = p("A", row)
        werte = ([u["name"], u["von"], u["bis"], u["saetze"], u["schritt"],
                  u["start"], u["maxlast"], "ja" if u["aktiv"] else "nein",
                  u["reha_ab"]] if u else [None] * 9)
        for j, v in enumerate(werte):
            c = wsp.cell(row, 1 + j, v)
            c.font, c.fill, c.border = F_BODY, FILL_INPUT, B_ALL
            c.alignment = L if j == 0 else C
            if j in (4, 5, 6):
                c.number_format = NF_KG

        # Hilfsspalten Q/R/S: letzte Einheit, Top-Gewicht, schwächster Satz
        letzte = "SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*%s))" % (C_, ex, D_, B_)
        wsp.cell(row, 17, "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))"
                 % (ex, letzte, letzte))
        zuletzt = ("SUMPRODUCT(MAX((%s=%s)*(%s=%s)*(%s=\"A\")*(%s<>\"\")"
                   "*%s))" % (C_, ex, B_, p("Q", row), D_, E_, E_))
        wsp.cell(row, 18, "=IF(%s=\"\",\"\",%s)" % (p("Q", row), zuletzt))
        minwdh = ("SUMPRODUCT(MIN((%s=%s)*(%s=%s)*(%s=\"A\")*(%s=%s)*%s"
                  "+((%s<>%s)+(%s<>%s)+(%s<>\"A\")+(%s<>%s)+(%s=\"\")>0)"
                  "*999))"
                  % (C_, ex, B_, p("Q", row), D_, E_, p("R", row), F_,
                     C_, ex, B_, p("Q", row), D_, E_, p("R", row), F_))
        wsp.cell(row, 19, "=IF(%s=\"\",\"\",IF(%s>=999,\"\",%s))"
                 % (p("R", row), minwdh, minwdh))
        for col in (17, 18, 19):
            cc = wsp.cell(row, col)
            cc.font, cc.alignment = F_SMALL, C
            cc.number_format = NF_KG if col == 18 else NF_INT

        # J  Status heute
        if PREOP:
            wsp.cell(row, 10, "=IF(%s=\"\",\"\",IF(%s=\"ja\","
                              "\"läuft\",\"Archiv\"))"
                     % (ex, p("H", row)))
        else:
            wsp.cell(row, 10,
                     "=IF(%s=\"\",\"\",IF(%s<>\"ja\",\"Archiv\","
                     "IF(OR(%s=\"\",%s>=%s),\"FREI\",\"GESPERRT\")))"
                     % (ex, p("H", row), p("I", row), WOCHE, p("I", row)))
        # K  zuletzt als Klartext
        wsp.cell(row, 11,
                 "=IF(%s=\"\",\"\",TEXT(%s,\"0.#\")&\" kg × \"&"
                 "IF(%s=\"\",\"?\",%s)&\" Wdh\")"
                 % (p("R", row), p("R", row), p("S", row), p("S", row)))
        # L / M / N  doppelte Progression
        von, bis = p("B", row), p("C", row)
        schritt, start, maxl = p("E", row), p("F", row), p("G", row)
        lastkg, minw = p("R", row), p("S", row)
        hoch = "%s+IF(%s=\"\",0,%s)" % (lastkg, schritt, schritt)
        gedeckelt = "IF(%s=\"\",%s,MIN(%s,%s))" % (maxl, hoch, hoch, maxl)
        reif = "AND(%s<>\"\",%s<>\"\",%s>=%s)" % (minw, bis, minw, bis)
        wsp.cell(row, 12,
                 "=IF(%s=\"\",\"\",IF(%s=\"\",IF(%s=\"\",\"\",%s),"
                 "IF(%s,%s,%s)))"
                 % (ex, lastkg, start, start, reif, gedeckelt, lastkg))
        ziel = p("L", row)
        wsp.cell(row, 13,
                 "=IF(OR(%s=\"\",%s=\"\"),\"\",IF(%s=\"\",%s,"
                 "IF(%s,%s,IF(OR(%s=\"\",%s<%s),%s,MIN(%s,%s+1)))))"
                 % (von, ziel, lastkg, von, reif, von, minw, minw, von, von,
                    bis, minw))
        wsp.cell(row, 14,
                 "=IF(%s=\"\",\"\",IF(%s=\"\",\"Startgewicht "
                 "eintragen und loslegen\",IF(AND(%s,%s>%s),\"Gewicht +\"&"
                 "TEXT(%s-%s,\"0.#\")&\" kg, Wdh zurück auf \"&%s,"
                 "IF(%s,\"Obergrenze - über Tempo und Pausen steigern\","
                 "IF(OR(%s=\"\",%s<%s),\"Gewicht halten, erst \"&%s&"
                 "\" Wdh schaffen\",\"Wdh +1 auf \"&%s)))))"
                 % (ziel, lastkg, reif, ziel, lastkg, ziel, lastkg, von,
                    reif, minw, minw, von, von, p("M", row)))
        # O  wie lange läuft diese Last schon
        stagn = ("SUMPRODUCT((COUNTIFS(%s,%s,%s,\"A\",%s,%s,%s,"
                 "ROW($1:$%d))>0)*1)"
                 % (C_, ex, D_, E_, lastkg, B_, MAX_EINHEIT))
        wsp.cell(row, 15, "=IF(%s=\"\",\"\",%s)" % (lastkg, stagn))
        if u:
            c = wsp.cell(row, 16, u["hinweis"])
            c.font, c.alignment = F_SMALL, LW

        for col in range(10, DRUCK_LAST + 1):
            cc = wsp.cell(row, col)
            cc.border = B_ALL
            cc.font, cc.alignment, cc.fill = F_BODY, C, FILL_CALC
        for col, nf in ((12, NF_KG), (13, NF_INT), (15, NF_INT)):
            wsp.cell(row, col).number_format = nf
        for col in (12, 13):
            wsp.cell(row, col).font = F_GRUEN
            wsp.cell(row, col).fill = FILL_WORK
        wsp.cell(row, 10).font = F_BOLD
        wsp.cell(row, 14).alignment = LW
        wsp.cell(row, 14).font = Font(name=FONT, size=9, color=NAVY)
        wsp.row_dimensions[row].height = 26
        row += 1
PL = row - 1

dv_aktiv = DataValidation(type="list", formula1='"ja,nein"', allow_blank=True)
wsp.add_data_validation(dv_aktiv)
dv_aktiv.add("H%d:H%d" % (PF, PL))

bereich = "A%d:%s%d" % (PF, get_column_letter(DRUCK_LAST), PL)
wsp.conditional_formatting.add(bereich, FormulaRule(
    formula=['$J%d="Archiv"' % PF],
    font=Font(name=FONT, size=10, italic=True, color="8A94A0")))
if not PREOP:
    wsp.conditional_formatting.add(bereich, FormulaRule(
        formula=['$J%d="GESPERRT"' % PF],
        fill=PatternFill("solid", bgColor="F8D7D7")))
    wsp.conditional_formatting.add("J%d:J%d" % (PF, PL), FormulaRule(
        formula=['$J%d="GESPERRT"' % PF],
        font=Font(name=FONT, size=10, bold=True, color=RED)))
    wsp.conditional_formatting.add("J%d:J%d" % (PF, PL), FormulaRule(
        formula=['$J%d="FREI"' % PF],
        font=Font(name=FONT, size=10, bold=True, color=GREEN)))
wsp.conditional_formatting.add("O%d:O%d" % (PF, PL), FormulaRule(
    formula=['AND($O%d<>"",$O%d>=4)' % (PF, PF)],
    fill=PatternFill("solid", bgColor="FCE8C0"),
    font=Font(name=FONT, size=10, bold=True, color=AMBER)))

r = PL + 2
r = infozeile(wsp, r, DRUCK_LAST,
              "Doppelte Progression: Solange der schwächste Arbeitssatz "
              "unter 'Wdh bis' liegt, bleibt das Gewicht stehen und es kommt "
              "eine Wiederholung dazu. Schaffen alle Sätze das obere Ende, "
              "kommt eine Laststufe drauf und die Wiederholungen fangen bei "
              "'Wdh von' wieder an. 'Max (kg)' deckelt das Ganze, "
              "'Start (kg)' gilt für Übungen ohne Historie. 'gleiche Last "
              "seit' wird ab vier Einheiten gelb - dann steht die Übung.")
r = infozeile(wsp, r, DRUCK_LAST,
              "Rechts neben dem Druckbereich stehen der Hinweistext je Übung "
              "und drei Hilfsspalten, aus denen die Progression rechnet. "
              "Nicht löschen, aber auch nicht nötig zum Arbeiten.")
wsp.freeze_panes = "B6"
druck(wsp, "A1:%s%d" % (get_column_letter(DRUCK_LAST), r), quer=True,
      titles="1:5", fuss="Grün = womit du heute startest")


def plan_ref(sp, exref):
    """Wert aus dem Blatt 'Plan' zur Übung in exref, ohne führendes =."""
    return ("IFERROR(INDEX('Plan'!$%s$%d:$%s$%d,MATCH(%s,'Plan'!$A$%d:$A$%d,"
            "0)),\"\")" % (sp, PF, sp, PL, exref, PF, PL))


# ==========================================================================
# TRAININGSBLATT  -  zum Ausdrucken und Mitnehmen
# ==========================================================================
wst = sheet("Trainingsblatt")
# Die breite Notizspalte bestimmt über die Breitenanpassung den Zoom -
# so passt ein Block sicher auf eine A4-Seite.
for col, w in zip("ABCDEFGHI", [5, 8, 11, 8, 13, 9, 8, 6, 50]):
    wst.column_dimensions[col].width = w

row = 1
blaetter = [(b, k) for k in range(1, BLATT_KOPIEN + 1) for b in BLOCKS]
for nr, (block, kopie) in enumerate(blaetter):
    wst.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
    c = wst.cell(row, 1, "%s        Blatt %d von %d"
                 % (block.upper(), kopie, BLATT_KOPIEN))
    c.font, c.fill, c.alignment = F_TITLE, FILL_TITLE, L_IND
    for col in range(1, 10):
        wst.cell(row, col).fill = FILL_TITLE
    wst.row_dimensions[row].height = 26
    row += 1

    for lab, col, span in (("Datum", 1, 2), ("Einheit Nr.", 3, 1),
                           ("Körpergewicht", 4, 2), ("Start / Ende", 6, 2),
                           ("Schlaf (h)", 8, 2)):
        c = wst.cell(row, col, lab)
        c.font = F_SMALL
        c.alignment = Alignment(horizontal="left", vertical="bottom")
        if span > 1:
            wst.merge_cells(start_row=row, start_column=col, end_row=row,
                            end_column=col + span - 1)
            wst.merge_cells(start_row=row + 1, start_column=col,
                            end_row=row + 1, end_column=col + span - 1)
        for j in range(span):
            wst.cell(row + 1, col + j).border = Border(
                bottom=Side("medium", color=NAVY))
    wst.row_dimensions[row].height = 12
    wst.row_dimensions[row + 1].height = 18
    row += 3

    for i, u in [(i, u) for i, u in enumerate(UEBUNGEN)
                 if u["block"] == block and u["aktiv"]]:
        prow = PLAN_ROW[u["name"]]
        exref = "'Plan'!$A$%d" % prow
        ziel, zielwdh = plan_ref("L", exref), plan_ref("M", exref)
        schritt = plan_ref("N", exref)
        status = plan_ref("J", exref)
        gesperrt = "%s=\"GESPERRT\"" % status
        satzmuster = (["W"] * len(WARMUP_FAKTOR)
                      + ["A"] * (u["saetze"] - 1) + [u["letzter"]])

        wst.merge_cells(start_row=row, start_column=1, end_row=row,
                        end_column=9)
        c = wst.cell(row, 1, "=%s" % exref)
        c.font, c.fill, c.alignment = F_H1, FILL_HEAD, L_IND
        for col in range(1, 10):
            wst.cell(row, col).fill = FILL_HEAD
            wst.cell(row, col).border = B_ALL
        wst.row_dimensions[row].height = 18
        row += 1

        # Zeile 1: was heute ansteht
        wst.merge_cells(start_row=row, start_column=1, end_row=row,
                        end_column=9)
        c = wst.cell(row, 1,
                     "=IF(%s,\"GESPERRT bis Woche \"&%s&\" nach OP\","
                     "IF(%s=\"\",\"Startgewicht im Blatt 'Plan' eintragen\","
                     "\"HEUTE:  \"&TEXT(%s,\"0.#\")&\" kg × \"&%s&\" Wdh\"))"
                     "&\"     ·     \"&%s&\" Sätze\""
                     % (gesperrt, plan_ref("I", exref), ziel, ziel,
                        zielwdh, plan_ref("D", exref)))
        c.font = Font(name=FONT, size=10, bold=True, color=NAVY)
        c.fill, c.alignment = FILL_LIGHT, L_IND
        for col in range(1, 10):
            wst.cell(row, col).fill = FILL_LIGHT
            wst.cell(row, col).border = B_ALL
        wst.row_dimensions[row].height = 16
        row += 1

        # Zeile 2: Rückblick und Schritt
        wst.merge_cells(start_row=row, start_column=1, end_row=row,
                        end_column=9)
        c = wst.cell(row, 1,
                     "=IF(%s=\"\",\"\",\"zuletzt \"&%s&\"     ·     \")"
                     "&IF(%s=\"\",\"\",%s)"
                     % (plan_ref("K", exref), plan_ref("K", exref),
                        schritt, schritt))
        c.font = Font(name=FONT, size=9, color="4A5568")
        c.alignment = L_IND
        for col in range(1, 10):
            wst.cell(row, col).border = B_ALL
        wst.row_dimensions[row].height = 14
        row += 1

        for j, lab in enumerate(["#", "Typ", "Plan (kg)", "Ziel\nWdh",
                                 "Gewicht (kg)", "Wdh", "RPE", "OK",
                                 "Notiz"]):
            c = wst.cell(row, 1 + j, lab)
            c.font = Font(name=FONT, size=8.5, bold=True, color=NAVY)
            c.fill, c.alignment, c.border = FILL_CALC, CW, B_ALL
        wst.row_dimensions[row].height = 18
        row += 1

        for s, typ in enumerate(satzmuster):
            wst.cell(row, 1, s + 1).font = F_SMALL
            wst.cell(row, 1).alignment = C
            c = wst.cell(row, 2, typ)
            c.font, c.alignment = F_BOLD, C
            if typ == "A":
                c.fill = FILL_WORK
            fak = (WARMUP_FAKTOR[s] if s < len(WARMUP_FAKTOR)
                   else (1.0 if typ == "A" else None))
            if fak is not None:
                c = wst.cell(row, 3, "=IF(OR(%s,%s=\"\"),\"\","
                                     "ROUND(%s*%s*2,0)/2)"
                             % (gesperrt, ziel, ziel, fak))
                c.font = Font(name=FONT, size=10, color="4A5568")
                c.alignment, c.number_format = C, NF_KG
            if typ == "A":
                c = wst.cell(row, 4, "=IF(OR(%s,%s=\"\"),\"\",%s)"
                             % (gesperrt, zielwdh, zielwdh))
                c.font = Font(name=FONT, size=10, bold=True, color=GREEN)
                c.alignment, c.number_format = C, NF_INT
            for col in range(5, 10):
                wst.cell(row, col).fill = FILL_WHITE
            for col in range(1, 10):
                wst.cell(row, col).border = B_ALL
            wst.row_dimensions[row].height = 18
            row += 1
        row += 1

    balken(wst, row, 1, 9, "Notizen zur Einheit")
    row += 1
    for _ in range(2):
        wst.merge_cells(start_row=row, start_column=1, end_row=row,
                        end_column=9)
        for col in range(1, 10):
            wst.cell(row, col).border = Border(bottom=thin)
        wst.row_dimensions[row].height = 17
        row += 1

    if nr < len(blaetter) - 1:
        wst.row_breaks.append(Break(id=row - 1))
        row += 1

wst.conditional_formatting.add("A1:I%d" % (row - 1), FormulaRule(
    formula=['LEFT($A1,8)="GESPERRT"'], fill=FILL_ROT,
    font=Font(name=FONT, size=10, bold=True, color=RED)))
druck(wst, "A1:I%d" % (row - 1), rand=(0.45, 0.35, 0.45, 0.45),
      fuss="Plan (kg): Aufwärmen 45 % / 70 %, Arbeitssätze auf HEUTE")

# ==========================================================================
# LOG
# ==========================================================================
wsl = sheet("Log")
titel(wsl, 8, "LOG  |  EIN SATZ PRO ZEILE",
      "Nur die gelben Spalten. Volumen rechnet sich selbst, alles andere "
      "zieht das Blatt 'Plan' daraus.")
kopf(wsl, 3, ["Datum", "Einheit", "Übung", "Satz", "Gewicht\n(kg)", "Wdh",
              "Volumen\n(kg)", "Notiz"],
     [13, 9, 24, 7, 11, 8, 11, 46], height=30)

for i in range(LOG_ROWS):
    row = LOG_FIRST + i
    d = ROWS[i] if i < len(ROWS) else None
    werte = [None, d[0] if d else None, d[2] if d else None,
             d[3] if d else None, d[4] if d else None, d[5] if d else None]
    for j, v in enumerate(werte):
        c = wsl.cell(row, 1 + j, v)
        c.font, c.fill, c.border = F_BODY, FILL_INPUT, B_ALL
        c.alignment = L if j == 2 else C
    wsl.cell(row, 1).number_format = NF_DATE
    wsl.cell(row, 5).number_format = NF_KG
    wsl.cell(row, 6).number_format = NF_INT
    wsl.cell(row, 4).font = F_BOLD
    c = wsl.cell(row, 7, "=IF(AND(ISNUMBER($E%d),ISNUMBER($F%d),"
                         "$D%d<>\"R\"),$E%d*$F%d,\"\")"
                 % (row, row, row, row, row))
    c.font, c.alignment, c.fill, c.border = F_BODY, C, FILL_CALC, B_ALL
    c.number_format = NF_INT
    notiz = None
    if d and d[7]:
        notiz = d[7]
    elif d and d[6]:
        notiz = "Drop: %s" % d[6]
    c = wsl.cell(row, 8, notiz)
    c.font, c.alignment, c.fill, c.border = F_BODY, L, FILL_INPUT, B_ALL
    wsl.row_dimensions[row].height = 16

dv_ueb = DataValidation(type="list",
                        formula1="='Plan'!$A$%d:$A$%d" % (PF, PL),
                        allow_blank=True)
dv_ueb.errorTitle, dv_ueb.error = "Übung", "Bitte eine Übung aus dem Plan."
wsl.add_data_validation(dv_ueb)
dv_ueb.add("C%d:C%d" % (LOG_FIRST, LOG_LAST))
dv_satz = DataValidation(type="list", formula1='"W,A,R"', allow_blank=True)
dv_satz.errorTitle = "Satztyp"
dv_satz.error = "W = Warmup, A = Arbeitssatz, R = Reduktionssatz"
wsl.add_data_validation(dv_satz)
dv_satz.add("D%d:D%d" % (LOG_FIRST, LOG_LAST))

rng = "A%d:H%d" % (LOG_FIRST, LOG_LAST)
wsl.conditional_formatting.add(rng, FormulaRule(
    formula=['$D%d="A"' % LOG_FIRST],
    fill=PatternFill("solid", bgColor="E7F2EA")))
wsl.freeze_panes = "C4"
wsl.auto_filter.ref = "A3:H%d" % LOG_LAST
druck(wsl, "A1:H%d" % (LOG_FIRST + len(ROWS) + 34), quer=True, titles="1:3",
      fuss="W = Warmup · A = Arbeitssatz (zählt) · R = Reduktionssatz")

# ==========================================================================
# VERLAUF
# ==========================================================================
wsv = sheet("Verlauf")
VLAST = 2 + EINHEITEN + 1
titel(wsv, VLAST, "VERLAUF  |  ARBEITSVOLUMEN JE ÜBUNG UND EINHEIT",
      "Gewicht × Wdh, nur Arbeitssätze. Leer = in dieser Einheit nicht "
      "trainiert.")
wsv.column_dimensions["A"].width = 24
for i in range(EINHEITEN):
    wsv.column_dimensions[get_column_letter(2 + i)].width = 9
wsv.column_dimensions[get_column_letter(VLAST - 1)].width = 12
wsv.column_dimensions[get_column_letter(VLAST)].width = 12

wsv.cell(3, 1, "Ab Einheit").font = F_BOLD
wsv.cell(3, 1).alignment = RE
c = wsv.cell(3, 2, 1)
c.font = Font(name=FONT, size=11, bold=True, color=NAVY)
c.fill, c.alignment, c.border, c.number_format = FILL_INPUT, C, B_ALL, "0"
wsv.merge_cells(start_row=3, start_column=3, end_row=3, end_column=VLAST)
c = wsv.cell(3, 3, '="zeigt Einheit "&$B$3&" bis "&($B$3+%d)&'
                   '".  Zahl links ändern, um weiterzublättern."'
             % (EINHEITEN - 1))
c.font, c.alignment, c.fill = F_SMALL, L_IND, FILL_CALC
wsv.row_dimensions[3].height = 18

labels = ["Übung"] + [None] * EINHEITEN + ["Gesamt (kg)", "Ø je Einheit"]
kopf(wsv, 4, labels, height=22)
for i in range(EINHEITEN):
    c = wsv.cell(4, 2 + i, "=$B$3" if i == 0
                 else "=%s4+1" % get_column_letter(1 + i))
    c.font, c.fill, c.alignment, c.border = F_H1, FILL_HEAD, CW, B_ALL
    c.number_format = "0"

VF = 5
UEB_ZEILEN = [PLAN_ROW[u["name"]] for u in UEBUNGEN]
for k, prow in enumerate(UEB_ZEILEN):
    row = VF + k
    ex = "$A%d" % row
    zebra = FILL_LIGHT if k % 2 == 0 else PatternFill()
    c = wsv.cell(row, 1, "=IF('Plan'!$A%d=\"\",\"\",'Plan'!$A%d)"
                 % (prow, prow))
    c.font, c.alignment, c.border, c.fill = F_BOLD, L, B_ALL, zebra
    for s in range(EINHEITEN):
        col = 2 + s
        kopfz = "%s$4" % get_column_letter(col)
        f = "SUMIFS(%s,%s,%s,%s,%s,%s,\"A\")" % (G_, C_, ex, B_, kopfz, D_)
        cc = wsv.cell(row, col, "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))"
                      % (ex, f, f))
        cc.font, cc.alignment, cc.border = F_BODY, C, B_ALL
        cc.number_format, cc.fill = NF_INT, zebra
    ges = "SUMIFS(%s,%s,%s,%s,\"A\")" % (G_, C_, ex, D_)
    cc = wsv.cell(row, VLAST - 1, "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))"
                  % (ex, ges, ges))
    cc.font, cc.alignment, cc.border = F_BOLD, C, B_ALL
    cc.number_format, cc.fill = NF_INT, FILL_CALC
    einh = ("SUMPRODUCT((COUNTIFS(%s,%s,%s,\"A\",%s,ROW($1:$%d))>0)*1)"
            % (C_, ex, D_, B_, MAX_EINHEIT))
    cc = wsv.cell(row, VLAST, "=IF(OR(%s=\"\",%s=0),\"\",%s/%s)"
                  % (ex, einh, ges, einh))
    cc.font, cc.alignment, cc.border = F_BODY, C, B_ALL
    cc.number_format, cc.fill = NF_INT, FILL_CALC
    wsv.row_dimensions[row].height = 17
VL = VF + len(UEB_ZEILEN) - 1

wsv.conditional_formatting.add(
    "B%d:%s%d" % (VF, get_column_letter(VLAST - 2), VL),
    ColorScaleRule(start_type="min", start_color="FFFFFF",
                   end_type="max", end_color="9EC5E8"))

srow = VL + 1
wsv.cell(srow, 1, "Summe je Einheit").font = F_BOLD
wsv.cell(srow, 1).alignment = L
for col in range(2, VLAST):
    sp = get_column_letter(col)
    c = wsv.cell(srow, col, "=IF(COUNT(%s%d:%s%d)=0,\"\",SUM(%s%d:%s%d))"
                 % (sp, VF, sp, VL, sp, VF, sp, VL))
    c.font, c.alignment, c.number_format = F_BOLD, C, NF_INT
for col in range(1, VLAST + 1):
    wsv.cell(srow, col).border = Border(top=med)
    wsv.cell(srow, col).fill = FILL_LIGHT

ch = BarChart()
ch.type, ch.style = "col", 10
ch.title = "Arbeitsvolumen je Einheit (kg)"
ch.y_axis.scaling.min = 0
ch.add_data(Reference(wsv, min_col=2, min_row=srow, max_col=VLAST - 2,
                      max_row=srow), from_rows=True)
ch.set_categories(Reference(wsv, min_col=2, min_row=4, max_col=VLAST - 2))
ch.height, ch.width, ch.legend = 7.5, 22, None
wsv.add_chart(ch, "A%d" % (srow + 2))

ende = srow + 18
druck(wsv, "A1:%s%d" % (get_column_letter(VLAST), ende), quer=True,
      titles="1:4")

# ==========================================================================
# REHA-FASSUNG:  Fahrplan + tägliches Log
# ==========================================================================
if not PREOP:
    wsf = sheet("Reha")
    for col, w in zip("ABCDEFG", [20, 10, 28, 34, 30, 34, 30]):
        wsf.column_dimensions[col].width = w
    titel(wsf, 7, RD.FAHRPLAN_TITEL, RD.FAHRPLAN_SUB)
    wsf.row_dimensions[2].height = 26
    wsf.cell(2, 1).alignment = LW

    r = 4
    balken(wsf, r, 1, 7, "Grundregeln über die gesamte Zeit")
    r += 1
    for lab, txt in RD.GRUNDREGELN:
        wsf.cell(r, 1, lab).font = F_BOLD
        wsf.cell(r, 1).alignment = LW
        wsf.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
        c = wsf.cell(r, 2, txt)
        c.font, c.alignment = F_BODY, LW
        for col in range(1, 8):
            wsf.cell(r, col).border = B_ALL
        wsf.row_dimensions[r].height = hoehe(txt, breite=150)
        r += 1

    r += 1
    balken(wsf, r, 1, 7, "Phasenplan")
    r += 1
    for i, lab in enumerate(RD.PHASEN_KOPF):
        c = wsf.cell(r, 1 + i, lab)
        c.font, c.fill, c.alignment, c.border = F_H1, FILL_HEAD, CW, B_ALL
    wsf.row_dimensions[r].height = 28
    r += 1
    for k, phase in enumerate(RD.PHASEN):
        for i, txt in enumerate(phase):
            c = wsf.cell(r, 1 + i, txt)
            c.font = F_BOLD if i == 0 else F_BODY
            c.alignment = CW if i in (0, 1) else LW
            c.border = B_ALL
            if k % 2 == 0:
                c.fill = FILL_LIGHT
        wsf.row_dimensions[r].height = max(
            hoehe(str(t), breite=40) for t in phase[2:])
        r += 1

    r += 1
    balken(wsf, r, 1, 7, RD.NOTFALL_TITEL, PatternFill("solid",
                                                       fgColor="B91C1C"))
    r += 1
    wsf.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    c = wsf.cell(r, 1, RD.NOTFALL)
    c.font = Font(name=FONT, size=10, bold=True, color=RED)
    c.alignment = LW
    for col in range(1, 8):
        wsf.cell(r, col).fill = FILL_ROT
        wsf.cell(r, col).border = B_ALL
    wsf.row_dimensions[r].height = hoehe(RD.NOTFALL, breite=150)
    r += 2

    balken(wsf, r, 1, 7, RD.HEILUNG_TITEL)
    r += 1
    for lab, wirkung, txt in RD.HEILUNG:
        wsf.cell(r, 1, lab).font = F_BOLD
        wsf.cell(r, 1).alignment = LW
        c = wsf.cell(r, 2, wirkung)
        c.alignment = CW
        c.font = Font(name=FONT, size=9, bold=True,
                      color=RED if ("bremst" in str(wirkung)
                                    or "Risiko" in str(wirkung)) else GREEN)
        wsf.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        c = wsf.cell(r, 3, txt)
        c.font, c.alignment = F_BODY, LW
        for col in range(1, 8):
            wsf.cell(r, col).border = B_ALL
        wsf.row_dimensions[r].height = hoehe(txt, breite=140)
        r += 1
    r = infozeile(wsf, r + 1, 7,
                  "Diese Seite ist eine Gedächtnisstütze, keine ärztliche "
                  "Anweisung. Bei jedem Widerspruch zum "
                  "Nachbehandlungsschema des Operateurs oder zur Ansage der "
                  "Physiotherapie gilt deren Vorgabe.")
    wsf.cell(r - 1, 1).font = Font(name=FONT, size=9, bold=True, color=AMBER)
    druck(wsf, "A1:G%d" % (r - 1), quer=True, titles="1:2")

    # --- tägliches Reha-Log -------------------------------------------
    wsr = sheet("Reha-Log")
    for col, w in zip("ABCDEFGH", [13, 9, 12, 12, 11, 11, 12, 40]):
        wsr.column_dimensions[col].width = w
    titel(wsr, 8, "REHA-LOG  |  TÄGLICH 60 SEKUNDEN",
          "Schmerz und Beweglichkeit. Der Statusblock zeigt, ob es "
          "vorwärtsgeht - das ist die Grundlage für den Physio-Termin.")
    wsr.cell(3, 1, "OP-Datum").font = F_BOLD
    wsr.cell(3, 1).alignment = RE
    c = wsr.cell(3, 2, OP_DATUM)
    c.fill, c.border, c.alignment = FILL_INPUT, B_ALL, C
    c.number_format, c.font = NF_DATE, F_BOLD
    OP = "$B$3"
    wsr.merge_cells(start_row=3, start_column=3, end_row=3, end_column=8)
    c = wsr.cell(3, 3, '="Heute ist Woche "&MAX(1,ROUNDDOWN((TODAY()-'
                       '%s)/7,0)+1)&" nach OP."' % OP)
    c.font, c.alignment, c.fill = F_BODY, L_IND, FILL_CALC
    wsr.row_dimensions[3].height = 20

    RF = 12
    RL = RF + REHALOG_ROWS - 1
    RA = "$A$%d:$A$%d" % (RF, RL)

    def rl(sp):
        return "$%s$%d:$%s$%d" % (sp, RF, sp, RL)

    balken(wsr, 4, 1, 8, "Status")
    kacheln = [
        ("Einträge", "=COUNT(%s)" % RA, NF_INT),
        ("letzter Eintrag", "=IF(COUNT(%s)=0,\"\",MAX(%s))" % (RA, RA),
         NF_DATE),
        ("Flexion aktuell", "E", None), ("Flexion Bestwert", "Emax", None),
        ("Abduktion aktuell", "F", None),
        ("Aussenrotation aktuell", "G", None),
        ("Schmerz Ruhe Ø 14 T.", "Cavg", None),
        ("Schmerz Last Ø 14 T.", "Davg", None),
    ]
    for n, (lab, spez, nf) in enumerate(kacheln):
        br, bc = 5 + n // 2, 1 + (n % 2) * 4
        if spez in ("E", "F", "G"):
            formel = ("=IF(COUNT(%s)=0,\"\",IFERROR(INDEX(%s,MATCH(MAX(%s),"
                      "%s,0)),\"\"))" % (RA, rl(spez), RA, RA))
            nf = NF_INT
        elif spez == "Emax":
            formel = "=IF(COUNT(%s)=0,\"\",MAX(%s))" % (rl("E"), rl("E"))
            nf = NF_INT
        elif spez in ("Cavg", "Davg"):
            sp = spez[0]
            formel = ("=IF(COUNT(%s)=0,\"\",IFERROR(AVERAGEIFS(%s,%s,\">=\"&"
                      "MAX(%s)-13),\"\"))" % (RA, rl(sp), RA, RA))
            nf = NF_KG
        else:
            formel = spez
        wsr.merge_cells(start_row=br, start_column=bc, end_row=br,
                        end_column=bc + 1)
        c = wsr.cell(br, bc, lab)
        c.font, c.alignment, c.fill = F_BODY, L_IND, FILL_LIGHT
        wsr.cell(br, bc + 1).fill = FILL_LIGHT
        wsr.merge_cells(start_row=br, start_column=bc + 2, end_row=br,
                        end_column=bc + 3)
        c = wsr.cell(br, bc + 2, formel)
        c.font = Font(name=FONT, size=12, bold=True, color=NAVY)
        c.alignment, c.number_format, c.fill = C, nf, FILL_CALC
        wsr.cell(br, bc + 3).fill = FILL_CALC
        for col in range(bc, bc + 4):
            wsr.cell(br, col).border = B_ALL
        wsr.row_dimensions[br].height = 19

    kopf(wsr, RF - 1, ["Datum", "Woche", "Schmerz\nRuhe 0-10",
                       "Schmerz\nLast 0-10", "Flexion\nGrad",
                       "Abduktion\nGrad", "Aussen-\nrotation Grad",
                       "Notiz"], height=30)
    for row in range(RF, RL + 1):
        c = wsr.cell(row, 1)
        c.fill, c.number_format, c.alignment = FILL_INPUT, NF_DATE, C
        wsr.cell(row, 2, "=IF(OR($A%d=\"\",%s=\"\"),\"\","
                         "ROUNDDOWN(($A%d-%s)/7,0)+1)" % (row, OP, row, OP))
        wsr.cell(row, 2).fill = FILL_CALC
        for col in range(3, 9):
            wsr.cell(row, col).fill = FILL_INPUT
        for col in range(1, 9):
            c = wsr.cell(row, col)
            c.border, c.font = B_ALL, F_BODY
            c.alignment = L if col == 8 else C
            if col in range(2, 8):
                c.number_format = NF_INT
        wsr.row_dimensions[row].height = 16
    dv_s = DataValidation(type="decimal", operator="between", formula1=0,
                          formula2=10, allow_blank=True)
    wsr.add_data_validation(dv_s)
    dv_s.add("C%d:D%d" % (RF, RL))
    wsr.conditional_formatting.add("C%d:D%d" % (RF, RL), FormulaRule(
        formula=['AND($C%d<>"",$C%d>=6)' % (RF, RF)], fill=FILL_ROT,
        font=Font(name=FONT, size=10, bold=True, color=RED)))

    ch2 = LineChart()
    ch2.title = "Beweglichkeit (Grad)"
    ch2.y_axis.scaling.min = 0
    for col in (5, 6, 7):
        ch2.add_data(Reference(wsr, min_col=col, min_row=RF - 1, max_row=RL),
                     titles_from_data=True)
    ch2.set_categories(Reference(wsr, min_col=1, min_row=RF, max_row=RL))
    ch2.height, ch2.width = 6.5, 13
    ch2.legend.position = "b"
    wsr.add_chart(ch2, "A%d" % (RL + 2))

    ch3 = LineChart()
    ch3.title = "Schmerz (0-10)"
    ch3.y_axis.scaling.min = 0
    ch3.y_axis.scaling.max = 10
    for col in (3, 4):
        ch3.add_data(Reference(wsr, min_col=col, min_row=RF - 1, max_row=RL),
                     titles_from_data=True)
    ch3.set_categories(Reference(wsr, min_col=1, min_row=RF, max_row=RL))
    ch3.height, ch3.width = 6.5, 13
    ch3.legend.position = "b"
    wsr.add_chart(ch3, "E%d" % (RL + 2))
    wsr.freeze_panes = "C%d" % RF
    druck(wsr, "A1:H%d" % (RF + 32), quer=True, titles="1:2",
          fuss="Immer gleich messen: gleiche Position, gleiche Tageszeit")

# ==========================================================================
# VOR-OP-FASSUNG:  Countdown, Checkliste, Baseline auf einem Blatt
# ==========================================================================
if PREOP:
    wsc = sheet("Vor der OP")
    for col, w in zip("ABCDEFGH", [30, 12, 12, 13, 13, 34, 14, 26]):
        wsc.column_dimensions[col].width = w
    titel(wsc, 8, "VOR DER OP  |  COUNTDOWN, CHECKLISTE, AUSGANGSWERTE",
          "Das OP-Datum steht im Blatt 'Plan'. Diese Seiten gelten bis "
          "dahin, danach die Reha-Fassung des Logbuchs verwenden.")

    r = 3
    wsc.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    c = wsc.cell(r, 1, '="Noch "&MAX(0,\'Plan\'!$C$3-TODAY())&" Tage bis '
                       'zur OP am "&TEXT(\'Plan\'!$C$3,"TT.MM.JJJJ")&"."')
    c.font = Font(name=FONT, size=13, bold=True, color=AMBER)
    c.alignment, c.fill = L_IND, FILL_CALC
    for col in range(1, 9):
        wsc.cell(r, col).fill = FILL_CALC
        wsc.cell(r, col).border = B_ALL
    wsc.row_dimensions[r].height = 24
    r += 2

    balken(wsc, r, 1, 8,
           "Was nach der OP wegfällt - und was du jetzt einüben solltest")
    r += 1
    for i, lab in enumerate(["Übung", "gesperrt bis\nWoche", "Ausfall\n"
                             "(Wochen)", "frei ab etwa", "schon getestet?",
                             "Ersatz und Hinweis", "Arbeitsgewicht\nErsatz",
                             "Notiz"]):
        c = wsc.cell(r, 1 + i, lab)
        c.font, c.fill, c.alignment, c.border = F_H1, FILL_HEAD, CW, B_ALL
    wsc.row_dimensions[r].height = 30
    r += 1
    CF = r
    for k, u in enumerate(UEBUNGEN):
        row = CF + k
        prow = PLAN_ROW[u["name"]]
        aktiv = "'Plan'!$H%d" % prow
        wsc.cell(row, 1, "=IF(%s<>\"ja\",\"\",'Plan'!$A%d)" % (aktiv, prow))
        wsc.cell(row, 2, "=IF(%s<>\"ja\",\"\",'Plan'!$I%d)" % (aktiv, prow))
        wsc.cell(row, 3, "=IF($B%d=\"\",\"\",MAX(0,$B%d-1))" % (row, row))
        wsc.cell(row, 4, "=IF($B%d=\"\",\"\",'Plan'!$C$3+($B%d-1)*7)"
                 % (row, row))
        c = wsc.cell(row, 5)
        c.fill, c.alignment = FILL_INPUT, C
        wsc.cell(row, 6, "=IF($A%d=\"\",\"\",IF($C%d<=0,\"kein Ausfall, "
                         "läuft durch\",'Plan'!$P%d))" % (row, row, prow))
        for col in (7, 8):
            wsc.cell(row, col).fill = FILL_INPUT
        for col in range(1, 9):
            cc = wsc.cell(row, col)
            cc.border = B_ALL
            cc.font = F_BOLD if col == 1 else F_BODY
            cc.alignment = LW if col in (6, 8) else (L if col == 1 else C)
        wsc.cell(row, 4).number_format = NF_DATE
        wsc.cell(row, 7).number_format = NF_KG
        wsc.row_dimensions[row].height = 26
    CL = CF + len(UEBUNGEN) - 1
    dv_t = DataValidation(type="list", formula1='"ja,teilweise,nein"',
                          allow_blank=True)
    wsc.add_data_validation(dv_t)
    dv_t.add("E%d:E%d" % (CF, CL))
    wsc.conditional_formatting.add("A%d:H%d" % (CF, CL), FormulaRule(
        formula=['AND($C%d<>"",$C%d>=4)' % (CF, CF)], fill=FILL_ROT))
    r = CL + 1
    r = infozeile(wsc, r, 8,
                  "Rot sind die Übungen, die einen Monat oder länger "
                  "ausfallen. Genau für die lohnt es sich, den Ersatz jetzt "
                  "einzuarbeiten und das Arbeitsgewicht einzutragen - dann "
                  "steht der Startwert nach der OP schon fest.")
    r += 1

    balken(wsc, r, 1, 8, "Checkliste bis zum OP-Tag")
    r += 1
    for i, lab in enumerate(["Aufgabe", "erledigt", "bis wann",
                             "Antwort / Notiz"]):
        c = wsc.cell(r, 1 + i if i == 0 else 1 + i, lab)
        c.font = Font(name=FONT, size=8.5, bold=True, color=NAVY)
        c.fill, c.alignment, c.border = FILL_CALC, C, B_ALL
    wsc.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
    for col in range(4, 9):
        wsc.cell(r, col).fill = FILL_CALC
        wsc.cell(r, col).border = B_ALL
    wsc.row_dimensions[r].height = 14
    r += 1
    CHECK_FIRST = r
    CHECKLISTE = [
        "Tenodese oder Tenotomie - welche Technik ist geplant? Der "
        "Reha-Fahrplan gilt nur für die Tenodese.",
        "Wird zusätzlich an Rotatorenmanschette oder Labrum gearbeitet? "
        "Dann gilt deren Protokoll.",
        "Wie lange Schlinge, und ab wann darf sie abgebaut werden?",
        "Ab wann ist Beintraining im Sitzen wieder erlaubt?",
        "Ab wann ist die Beinpresse erlaubt? Im Logbuch steht Woche 2 als "
        "abgeleiteter Wert, nicht als ärztliche Freigabe.",
        "Ab wann darf der Arm wieder Hebelast tragen, und wie viel?",
        "Ab wann Bizeps-Curls gegen Widerstand?",
        "Welches schriftliche Nachbehandlungsschema bekomme ich mit?",
        "Erster Physiotermin vereinbart, Verordnung da?",
        "OP-Termin, Anreise und Begleitung für den Heimweg geklärt",
        "Arbeitsausfall angemeldet, Krankschreibung besprochen",
        "Schlinge, Kühlpackungen, Verbandsmaterial und Knopfhemden bereit",
        "Schlafplatz halbsitzend vorbereitet",
        "Einkäufe und Haushalt für die erste Woche vorbereitet",
        "Ersatzübungen oben durchgespielt und Arbeitsgewichte eingetragen",
        "Baseline unten gemessen, beide Seiten, mindestens zwei Termine",
        "Trainingsblätter der Reha-Fassung ausgedruckt und bereitgelegt",
    ]
    for punkt in CHECKLISTE:
        c = wsc.cell(r, 1, punkt)
        c.font, c.alignment = F_BODY, LW
        for col in (2, 3):
            wsc.cell(r, col).fill = FILL_INPUT
            wsc.cell(r, col).alignment = C
        wsc.cell(r, 3).number_format = NF_DATE
        wsc.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
        for col in range(4, 9):
            wsc.cell(r, col).fill = FILL_INPUT
        for col in range(1, 9):
            wsc.cell(r, col).border = B_ALL
        wsc.row_dimensions[r].height = hoehe(punkt, breite=42, minimum=18)
        r += 1
    CHECK_LAST = r - 1
    dv_ok = DataValidation(type="list", formula1='"ja,offen,entfällt"',
                           allow_blank=True)
    wsc.add_data_validation(dv_ok)
    dv_ok.add("B%d:B%d" % (CHECK_FIRST, CHECK_LAST))
    wsc.conditional_formatting.add(
        "A%d:H%d" % (CHECK_FIRST, CHECK_LAST),
        FormulaRule(formula=['$B%d="ja"' % CHECK_FIRST],
                    font=Font(name=FONT, size=10, italic=True,
                              color="8A94A0")))
    wsc.cell(r, 1, "Noch offen").font = F_BOLD
    wsc.cell(r, 1).alignment = RE
    c = wsc.cell(r, 2, "=%d-COUNTIF($B$%d:$B$%d,\"ja\")-"
                       "COUNTIF($B$%d:$B$%d,\"entfällt\")"
                 % (len(CHECKLISTE), CHECK_FIRST, CHECK_LAST, CHECK_FIRST,
                    CHECK_LAST))
    c.font = Font(name=FONT, size=12, bold=True, color=AMBER)
    c.alignment, c.fill, c.border, c.number_format = (C, FILL_CALC, B_ALL,
                                                      NF_INT)
    wsc.cell(r, 3, "von %d" % len(CHECKLISTE)).font = F_SMALL
    r += 2
    wsc.row_breaks.append(Break(id=r - 2))

    balken(wsc, r, 1, 8, "Ausgangswerte Schulter  ·  beide Seiten messen")
    r += 1
    r = infozeile(wsc, r, 8,
                  "Der Reha-Fahrplan misst zwei Meilensteine am Vergleich "
                  "zur Gegenseite: Beugekraft etwa 70 Prozent in Phase 4, "
                  "mindestens 90 Prozent in Phase 5. Ohne einen vor der OP "
                  "gemessenen Wert der gesunden Seite sind diese Prozente "
                  "später nicht überprüfbar - und nachholen lässt sich die "
                  "Messung nicht. Immer gleiche Position, gleiche Tageszeit, "
                  "gleiche Methode. Curl-Testgewicht heisst: das Gewicht, "
                  "mit dem eine feste Wiederholungszahl sauber gelingt.")
    BL_KOPF = ["Datum", "Seite", "Flexion\nGrad", "Abduktion\nGrad",
               "Aussen-\nrotation Grad", "Curl-Testgewicht (kg) und Wdh",
               "Schmerz\n0-10", "Notiz"]
    for i, lab in enumerate(BL_KOPF):
        c = wsc.cell(r, 1 + i, lab)
        c.font, c.fill, c.alignment, c.border = F_H1, FILL_HEAD, CW, B_ALL
    wsc.row_dimensions[r].height = 28
    r += 1
    BF = r
    for _ in range(16):
        for col in range(1, 9):
            c = wsc.cell(r, col)
            c.fill, c.border, c.font = FILL_INPUT, B_ALL, F_BODY
            c.alignment = LW if col in (6, 8) else C
            if col == 1:
                c.number_format = NF_DATE
            elif col in (3, 4, 5, 7):
                c.number_format = NF_INT
        wsc.row_dimensions[r].height = 17
        r += 1
    BL = r - 1
    dv_seite = DataValidation(type="list", formula1='"operiert,gesund"',
                              allow_blank=True)
    wsc.add_data_validation(dv_seite)
    dv_seite.add("B%d:B%d" % (BF, BL))
    wsc.conditional_formatting.add("A%d:H%d" % (BF, BL), FormulaRule(
        formula=['$B%d="gesund"' % BF], fill=FILL_LIGHT))

    r += 1
    for i, lab in enumerate(["Vergleich", "operiert", "gesund", "Anteil"]):
        c = wsc.cell(r, 1 + i, lab)
        c.font, c.fill, c.alignment, c.border = F_H1, FILL_HEAD, CW, B_ALL
    r += 1
    for lab, sp in (("Flexion (Grad)", "C"), ("Abduktion (Grad)", "D"),
                    ("Aussenrotation (Grad)", "E")):
        wsc.cell(r, 1, lab).font = F_BOLD
        wsc.cell(r, 1).alignment = L_IND
        for j, seite in enumerate(("operiert", "gesund")):
            f = ("SUMPRODUCT(MAX(($B$%d:$B$%d=\"%s\")*($%s$%d:$%s$%d<>\"\")"
                 "*$%s$%d:$%s$%d))"
                 % (BF, BL, seite, sp, BF, sp, BL, sp, BF, sp, BL))
            c = wsc.cell(r, 2 + j, "=IF(%s=0,\"\",%s)" % (f, f))
            c.font, c.alignment, c.fill = F_BODY, C, FILL_CALC
            c.number_format = NF_INT
        c = wsc.cell(r, 4, "=IF(OR($B%d=\"\",$C%d=\"\",$C%d=0),\"\","
                           "$B%d/$C%d)" % (r, r, r, r, r))
        c.font, c.alignment, c.fill = F_BOLD, C, FILL_CALC
        c.number_format = "0.0%"
        for col in range(1, 5):
            wsc.cell(r, col).border = B_ALL
        wsc.row_dimensions[r].height = 18
        r += 1
    druck(wsc, "A1:H%d" % (r - 1), quer=True, titles="1:2")

# ==========================================================================
# Reihenfolge und Speichern
# ==========================================================================
ORDER = (["Plan", "Trainingsblatt", "Log", "Verlauf", "Vor der OP"] if PREOP
         else ["Plan", "Trainingsblatt", "Log", "Verlauf", "Reha",
               "Reha-Log"])
wb._sheets = [wb[n] for n in ORDER]
wb.active = 0
for s in wb.worksheets:
    s.sheet_view.tabSelected = (s.title == "Plan")

wb.save(DATEI)
print("geschrieben: %s  (%d Blätter)" % (DATEI, len(wb.worksheets)))
