#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt GymLogbuch_Beine.xlsx - Trainingslogbuch Beine, druckoptimiert.

Neun Blätter: Start, Dashboard, Einheiten, Log, Auswertung, Progression,
Rekorde, Trainingsblatt, Übungen. Alle Kennzahlen sind Formeln, keine
hartcodierten Ergebnisse. Jedes Blatt hat ein fertiges A4-Druck-Layout mit
Druckbereich, wiederholtem Spaltenkopf und Seitennummerierung.

Rohdaten (Einheit 1-4) stammen aus Löwin_Training_260727.pdf und liegen in
daten.py.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.pagebreak import Break
from openpyxl.formatting.rule import ColorScaleRule, FormulaRule
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment

from daten import ROWS

# --------------------------------------------------------------------------
# Konfiguration
# --------------------------------------------------------------------------
QUELLE = "Löwin_Training_260727.pdf"
STAND = "31.07.2026"

SESSIONS = 16          # ausgewertete Einheiten in der Auswertung
EX_SLOTS = 14          # Übungs-Slots im Stammblatt (9 belegt)
SESSION_SLOTS = 24     # vorbereitete Zeilen im Blatt 'Einheiten'
LOG_ROWS = 500         # vorbereitete Satzzeilen im Log

# Alle Blätter: Zeile 1/2 Titelbalken, Zeile 3 Spaltenkopf, ab Zeile 4 Daten
LOG_FIRST, LOG_LAST = 4, 3 + LOG_ROWS
UEB_FIRST, UEB_LAST = 4, 3 + EX_SLOTS
EINH_FIRST, EINH_LAST = 4, 3 + SESSION_SLOTS
REK_FIRST, REK_LAST = 4, 3 + EX_SLOTS

UEB = "'Übungen'"       # Blattname mit Umlaut -> in Formeln immer quoten

# Aktueller Plan. Reihenfolge = Reihenfolge in allen Auswertungen und auf dem
# Trainingsblatt: schwere Grundübung zuerst, Isolation danach.
# letzter: Satztyp des letzten Arbeitssatzes ("A" oder "R" = Reduktionssatz).
# start:   Startgewicht für Übungen ohne Historie. None = im Blatt 'Übungen'
#          einzutragen; ohne Wert bleibt die Plan-Spalte leer.
# max:     Lastobergrenze, z.B. das Ende des Steckgewichts. Der
#          Zielvorschlag steigt nie darüber hinaus. None = keine Grenze.
UEBUNGEN = [
    dict(name="Hackenschmidt-Kniebeuge", maxlast=None, block="Beine vorne",
         geraet="Hackenschmidt / Pendel", wdh="6-10", saetze=3, rpe="8-9",
         start=None, letzter="A", aktiv=True,
         notiz="Ersetzt Lunges. Schwere Grundübung zuerst, Quadrizeps unter "
               "Last in der gedehnten Position, Rücken gestützt. Ohne "
               "Maschine: Pendelkniebeuge, sonst Beinpresse mit tiefer "
               "Fussposition."),
    dict(name="Split Squat", maxlast=None, block="Beine vorne",
         geraet="Multipresse / Hantel", wdh="8-10", saetze=3, rpe="8",
         start=None, letzter="A", aktiv=True,
         notiz="Wdh-Bereich von 5-8 auf 8-10 je Bein. Limiter soll der "
               "Muskel sein, nicht die Stabilität."),
    dict(name="Beinstrecker", maxlast=None, block="Beine vorne", geraet="Maschine",
         wdh="12-15", saetze=3, rpe="9", start=None, letzter="R", aktiv=True,
         notiz="Dritter Arbeitssatz läuft als Reduktionssatz aus."),
    dict(name="Adduktion", maxlast=152.5, block="Beine vorne", geraet="Maschine",
         wdh="15-20", saetze=3, rpe="9", start=None, letzter="R", aktiv=True,
         notiz="152.5 kg ist Stackende. Progression ab jetzt über 3 s "
               "Exzentrik und 1 s Pause in der gedehnten Position, nicht "
               "über Last."),
    dict(name="Rumänisches Kreuzheben", maxlast=None, block="Beine hinten",
         geraet="Langhantel", wdh="8-10", saetze=3, rpe="8", start=None,
         letzter="A", aktiv=True,
         notiz="Ersetzt Kickback. Schliesst die Lücke Hüftstreckung bei "
               "gestrecktem Knie, Ischiokrurale und Gluteus in der Dehnung."),
    dict(name="Hip Thrust", maxlast=None, block="Beine hinten", geraet="Langhantel",
         wdh="8-12", saetze=3, rpe="8-9", start=None, letzter="A",
         aktiv=True,
         notiz="Gesamtgewicht inkl. Stange notieren, auch bei "
               "Reduktionssätzen."),
    dict(name="Beinbeuger", maxlast=None, block="Beine hinten", geraet="Maschine, sitzend",
         wdh="10-12", saetze=3, rpe="9", start=None, letzter="R", aktiv=True,
         notiz="Sitzend statt liegend: Hüfte gebeugt, Ischiokrurale "
               "vorgedehnt, mehr Reiz pro Satz. Dritter Satz als "
               "Reduktionssatz."),
    dict(name="Seitliche Kickbacks", maxlast=None, block="Beine hinten", geraet="Kabel",
         wdh="15-20", saetze=3, rpe="9", start=None, letzter="A", aktiv=True,
         notiz="Gluteus medius, relevant für die Silhouette von vorne."),
    dict(name="Waden", maxlast=None, block="Beine hinten", geraet="Maschine", wdh="10-15",
         saetze=3, rpe="9", start=None, letzter="A", aktiv=True,
         notiz="In jede Beineinheit, bisher nur in jeder zweiten."),
    # Archiv: raus aus der Planung, Historie bleibt in Log und Auswertung.
    dict(name="Lunges", maxlast=None, block="Beine vorne", geraet="Kurzhantel",
         wdh="10-12", saetze=None, rpe=None, start=None, letzter="A",
         aktiv=False,
         notiz="Archiv. Redundant zum Split Squat, Historie bleibt in den "
               "Auswertungen sichtbar."),
    dict(name="Kickback", maxlast=None, block="Beine hinten", geraet="Maschine / Kabel",
         wdh="10-15", saetze=None, rpe=None, start=None, letzter="A",
         aktiv=False,
         notiz="Archiv. Von Hip Thrust und RDL abgedeckt, Historie bleibt "
               "erhalten."),
]
BLOCKS = ["Beine vorne", "Beine hinten"]

# Aufwärm-Rampe für das Trainingsblatt: Anteil vom Zielgewicht je Warmup
WARMUP_FAKTOR = [0.45, 0.70]

# --------------------------------------------------------------------------
# Design
# --------------------------------------------------------------------------
FONT = "Arial"
NAVY = "1F3A5F"
NAVY_D = "142A44"
STEEL = "3D6288"
LIGHT = "EDF1F6"
INPUT = "FFF6D5"
CALC = "F7F9FC"
AMBER = "B45309"
GREEN = "15803D"
RED = "B91C1C"
GRID = "AEBACA"

thin = Side(style="thin", color=GRID)
med = Side(style="medium", color=NAVY)
B_ALL = Border(left=thin, right=thin, top=thin, bottom=thin)

F_TITLE = Font(name=FONT, size=16, bold=True, color="FFFFFF")
F_SUB = Font(name=FONT, size=9, color="FFFFFF")
F_H1 = Font(name=FONT, size=11, bold=True, color="FFFFFF")
F_BODY = Font(name=FONT, size=10)
F_SMALL = Font(name=FONT, size=8.5, color="4A5568")
F_BOLD = Font(name=FONT, size=10, bold=True)
F_KPI = Font(name=FONT, size=18, bold=True, color=NAVY)

FILL_TITLE = PatternFill("solid", fgColor=NAVY_D)
FILL_HEAD = PatternFill("solid", fgColor=NAVY)
FILL_SUB = PatternFill("solid", fgColor=STEEL)
FILL_LIGHT = PatternFill("solid", fgColor=LIGHT)
FILL_INPUT = PatternFill("solid", fgColor=INPUT)
FILL_CALC = PatternFill("solid", fgColor=CALC)
FILL_WHITE = PatternFill("solid", fgColor="FFFFFF")
FILL_WORK = PatternFill("solid", fgColor="E7F2EA")

C = Alignment(horizontal="center", vertical="center")
L = Alignment(horizontal="left", vertical="center")
LW = Alignment(horizontal="left", vertical="top", wrap_text=True)
CW = Alignment(horizontal="center", vertical="center", wrap_text=True)
L_IND = Alignment(horizontal="left", vertical="center", indent=1)

NF_KG = '#,##0.0;-#,##0.0;"–"'
NF_INT = '#,##0;-#,##0;"–"'
NF_PCT = '+0.0%;-0.0%;"–"'
NF_DATE = "DD.MM.YYYY"

wb = Workbook()
wb.remove(wb.active)


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------
def sheet(name):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    return ws


def titelbalken(ws, first_col, last_col, titel, untertitel, row=1):
    for r, txt, fnt in ((row, titel, F_TITLE), (row + 1, untertitel, F_SUB)):
        ws.merge_cells(start_row=r, start_column=first_col,
                       end_row=r, end_column=last_col)
        c = ws.cell(r, first_col, txt)
        c.font, c.fill, c.alignment = fnt, FILL_TITLE, L_IND
        for col in range(first_col, last_col + 1):
            ws.cell(r, col).fill = FILL_TITLE
    ws.row_dimensions[row].height = 30
    ws.row_dimensions[row + 1].height = 15


def kopfzeile(ws, row, first_col, labels, widths=None, height=26):
    for i, lab in enumerate(labels):
        c = ws.cell(row, first_col + i, lab)
        c.font, c.fill, c.alignment, c.border = F_H1, FILL_HEAD, CW, B_ALL
    ws.row_dimensions[row].height = height
    if widths:
        for i, w in enumerate(widths):
            ws.column_dimensions[get_column_letter(first_col + i)].width = w


def abschnitt(ws, row, first_col, last_col, text):
    ws.merge_cells(start_row=row, start_column=first_col,
                   end_row=row, end_column=last_col)
    c = ws.cell(row, first_col, text)
    c.font, c.fill, c.alignment = F_H1, FILL_SUB, L_IND
    for col in range(first_col, last_col + 1):
        ws.cell(row, col).fill = FILL_SUB
    ws.row_dimensions[row].height = 20


def druck(ws, area, landscape=False, titles=None, fit_h=0, margins=None,
          fussnote=None):
    """A4-Druckeinrichtung: Breite fixieren, Kopf- und Fusszeile setzen."""
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = fit_h
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_area = area
    if titles:
        ws.print_title_rows = titles
    ws.print_options.horizontalCentered = True
    m = margins or (0.5, 0.4, 0.7, 0.6)
    ws.page_margins.left, ws.page_margins.right = m[0], m[1]
    ws.page_margins.top, ws.page_margins.bottom = m[2], m[3]
    ws.page_margins.header, ws.page_margins.footer = 0.3, 0.3
    ws.oddHeader.left.text = "Gym Logbuch  |  Beintraining"
    ws.oddHeader.left.size, ws.oddHeader.left.color = 8, "808080"
    ws.oddHeader.right.text = ws.title
    ws.oddHeader.right.size, ws.oddHeader.right.color = 8, "808080"
    ws.oddFooter.left.text = fussnote or ("Quelle: %s" % QUELLE)
    ws.oddFooter.left.size, ws.oddFooter.left.color = 8, "808080"
    ws.oddFooter.right.text = "Seite &P von &N"
    ws.oddFooter.right.size, ws.oddFooter.right.color = 8, "808080"


def zeilenhoehe(text, breite=92, zeile=12.5, minimum=16):
    """Zeilenhöhe aus der Textlänge schätzen, damit nichts abgeschnitten wird.

    breite = Zeichen pro Zeile im umbrochenen Bereich, grosszügig geschätzt.
    """
    zeilen = max(1, -(-len(text) // breite))
    return max(minimum, zeilen * zeile + 5)


def archiv_grau(ws, first_col, last_col, first_row, last_row):
    """Archivierte Übungen (Aktiv = nein) grau und kursiv darstellen.

    Die Zeilen der Auswertungsblätter liegen deckungsgleich zu den Zeilen im
    Blatt 'Übungen', deshalb genügt der Zeilenversatz als Bezug.
    """
    versatz = UEB_FIRST - first_row
    ws.conditional_formatting.add(
        "%s%d:%s%d" % (get_column_letter(first_col), first_row,
                       get_column_letter(last_col), last_row),
        FormulaRule(formula=['%s!$I%d="nein"' % (UEB, first_row + versatz)],
                    font=Font(name=FONT, size=10, italic=True,
                              color="8A94A0")))


# Begrenzte Bereichsreferenzen - SUMPRODUCT verträgt keine ganzen Spalten
def LR(col):
    return "Log!$%s$%d:$%s$%d" % (col, LOG_FIRST, col, LOG_LAST)


D_, B_, E_, F_, G_, I_ = (LR("D"), LR("B"), LR("E"), LR("F"), LR("G"),
                          LR("I"))


def f_volumen(ex, sess):
    s = "SUMIFS(%s,%s,%s,%s,%s,%s,\"A\")" % (I_, D_, ex, B_, sess, E_)
    return "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))" % (ex, s, s)


def f_topgewicht(ex, sess):
    s = ("SUMPRODUCT(MAX((%s=%s)*(%s=%s)*(%s=\"A\")*(%s<>\"\")*%s))"
         % (D_, ex, B_, sess, E_, F_, F_))
    return "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))" % (ex, s, s)


def f_e1rm(ex, sess):
    s = ("SUMPRODUCT(MAX((%s=%s)*(%s=%s)*(%s=\"A\")*(%s<>\"\")*(%s<>\"\")"
         "*%s*(1+%s/30)))" % (D_, ex, B_, sess, E_, F_, G_, F_, G_))
    return "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))" % (ex, s, s)


# ==========================================================================
# START
# ==========================================================================
ws = sheet("Start")
for col, w in zip("ABCDEF", [2, 24, 30, 22, 22, 2]):
    ws.column_dimensions[col].width = w

titelbalken(ws, 2, 5, "GYM LOGBUCH  |  BEINTRAINING",
            "Quelle: %s   ·   aufbereitet am %s" % (QUELLE, STAND))

r = 4
abschnitt(ws, r, 2, 5, "Kurzübersicht")
r += 1
for lab, formel, nf in [
    ("Einheiten erfasst",
     "=COUNT(Einheiten!$I$%d:$I$%d)" % (EINH_FIRST, EINH_LAST), NF_INT),
    ("Sätze gesamt", "=COUNTA(%s)" % E_, NF_INT),
    ("Gesamtvolumen (t)", "=IFERROR(SUM(%s)/1000,0)" % I_, NF_KG),
    ("Schwerster Arbeitssatz (kg)",
     "=SUMPRODUCT(MAX((%s=\"A\")*(%s<>\"\")*%s))" % (E_, F_, F_), NF_KG),
]:
    ws.cell(r, 2, lab).font = F_BODY
    ws.cell(r, 2).alignment = L
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
    c = ws.cell(r, 3, formel)
    c.font = Font(name=FONT, size=11, bold=True, color=NAVY)
    c.alignment, c.number_format, c.fill = L, nf, FILL_CALC
    for col in (4, 5):
        ws.cell(r, col).fill = FILL_CALC
    for col in range(2, 6):
        ws.cell(r, col).border = B_ALL
    r += 1

r += 1
abschnitt(ws, r, 2, 5, "So arbeitest du damit")
r += 1
for lab, txt in [
    ("Blatt 'Einheiten'",
     "Zuerst hier die Einheit anlegen: Nummer, Datum, Körpergewicht, Dauer, "
     "Schlaf, Gefühl. Das Datum zieht sich automatisch ins Log, du trägst es "
     "nur einmal ein."),
    ("Blatt 'Log'",
     "Eine Zeile pro Satz. Nur die gelben Spalten ausfüllen: Einheit, Übung, "
     "Satztyp, Gewicht, Wdh, optional RPE und Notiz. Block, Volumen und "
     "e1RM rechnen sich selbst."),
    ("Blatt 'Trainingsblatt'",
     "Ausdrucken und mitnehmen. Zeigt je Übung, was du zuletzt gemacht hast, "
     "dazu einen Zielvorschlag inklusive Aufwärm-Rampe und leere Felder zum "
     "Eintragen mit Stift. Enthält die neun Übungen des Plans - für spontane "
     "Zusatzübungen sind die Notizzeilen am Seitenende da."),
    ("Blatt 'Auswertung'",
     "Volumen, Top-Gewicht und bester e1RM je Übung und Einheit. Drei "
     "Tabellen, jede auf einer eigenen Druckseite."),
    ("Blatt 'Progression'",
     "Erste gegen letzte Einheit: Veränderung in kg und Prozent, Abstand zum "
     "eigenen Bestwert, Trendbewertung."),
    ("Blatt 'Rekorde'",
     "Bestwerte je Übung über alle Einheiten, inklusive der Einheit, in der "
     "der Rekord gefallen ist."),
    ("Blatt 'Dashboard'",
     "Kennzahlen und vier Diagramme auf einer Seite. Gut zum Aufhängen."),
    ("Blatt 'Übungen'",
     "Stammdaten und Planvorgaben: Ziel-Wdh, Ziel-Sätze, Ziel-RPE und "
     "Startgewicht je Übung. Neue Übung hier ergänzen - sie erscheint "
     "automatisch in den Dropdowns und in allen Auswertungen. 'Aktiv = "
     "nein' archiviert eine Übung: raus aus der Planung, Historie bleibt."),
]:
    ws.cell(r, 2, lab).font = F_BOLD
    ws.cell(r, 2).alignment = Alignment(horizontal="left", vertical="top")
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
    c = ws.cell(r, 3, txt)
    c.font, c.alignment = F_BODY, LW
    for col in range(2, 6):
        ws.cell(r, col).border = B_ALL
    ws.row_dimensions[r].height = zeilenhoehe(txt)
    r += 1

r += 1
abschnitt(ws, r, 2, 5, "Legende")
r += 1
gelb_zeile = r
for lab, txt in [
    ("Gelbe Zellen", "Deine Eingabe. Nur hier tippen."),
    ("Weisse / graue Zellen", "Formeln. Nicht überschreiben."),
    ("Satztyp W", "Warmup. Zählt nicht ins Arbeitsvolumen."),
    ("Satztyp A",
     "Arbeitssatz. Basis für Volumen, Top-Gewicht und e1RM."),
    ("Satztyp R",
     "Reduktions- bzw. Dropsatz. Kette in der Spalte 'Drop-Kette' notieren, "
     "z.B. 110 / 72.5 / 35. Zählt nicht ins Arbeitsvolumen, weil die Wdh je "
     "Stufe fehlen."),
    ("Volumen",
     "Gewicht × Wdh je Satz. Der ehrlichste Fortschrittswert an "
     "Maschinen."),
    ("e1RM (Epley)",
     "Gewicht × (1 + Wdh / 30). An Maschinen kein echtes 1RM, aber ein "
     "sauberer Vergleich zwischen Einheiten mit unterschiedlichen "
     "Wiederholungszahlen."),
    ("RPE",
     "Anstrengung 6 bis 10. 10 = keine Wiederholung mehr möglich. Optional, "
     "aber sehr hilfreich für die Steuerung. Die Zielwerte je Übung stehen "
     "im Blatt 'Übungen'."),
    ("Archiv",
     "Übung im Blatt 'Übungen' auf Aktiv = nein setzen. Sie verschwindet aus "
     "dem Trainingsblatt, bleibt in Log, Auswertung, Progression und "
     "Rekorden aber sichtbar - dort grau und kursiv."),
]:
    ws.cell(r, 2, lab).font = F_BOLD
    ws.cell(r, 2).alignment = Alignment(horizontal="left", vertical="top")
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
    c = ws.cell(r, 3, txt)
    c.font, c.alignment = F_BODY, LW
    for col in range(2, 6):
        ws.cell(r, col).border = B_ALL
    ws.row_dimensions[r].height = zeilenhoehe(txt)
    r += 1
ws.cell(gelb_zeile, 2).fill = FILL_INPUT

r += 1
abschnitt(ws, r, 2, 5, "Offene Punkte aus der Originalquelle")
r += 1
for lab, txt in [
    ("Kickback, Warmups",
     "Im Original stehen zwei Gewichte statt Gewicht plus Wdh (z.B. 35 kg / "
     "49 kg). Als zwei Warmup-Sätze ohne Wdh erfasst."),
    ("Adduktion, Einheit 4",
     "Original 152.2 kg, überall sonst 152.5 kg. Als Tippfehler auf 152.5 "
     "korrigiert und im Log vermerkt. War es ein anderes Gerät, die beiden "
     "Zeilen im Log anpassen."),
    ("Beinstrecker, Einheit 2",
     "Zeile 'W 10 kg 20 kg 5-6 Wdh' als zwei Warmups ohne Wdh erfasst."),
    ("Hip Thrust, R-Sätze",
     "'-25 kg je Seite' ohne Absolutgewicht. Beim nächsten Mal das "
     "Gesamtgewicht eintragen, sonst ist der Satz nicht vergleichbar."),
    ("Lunges",
     "Nur Gewichte, keine Wdh und keine Satzstruktur. Als je ein Arbeitssatz "
     "in Einheit 1 bis 3 erfasst - deshalb bleibt das Volumen dort leer. "
     "Übung ist inzwischen archiviert."),
    ("Datum",
     "In der Quelle nicht enthalten. Im Blatt 'Einheiten' nachtragen, falls "
     "du die Termine noch weisst."),
    ("Stackende Adduktion",
     "152.5 kg ist das Ende des Steckgewichts. Im Blatt 'Übungen' als 'Max "
     "(kg)' hinterlegt, damit der Zielvorschlag dort stehen bleibt statt "
     "eine Last zu fordern, die die Maschine nicht hergibt. Weitersteigern "
     "über Tempo und Pausen."),
    ("Startgewichte fehlen",
     "Hackenschmidt-Kniebeuge und Rumänisches Kreuzheben sind neu im Plan "
     "und haben keine Historie. Trag im Blatt 'Übungen' unter 'Start (kg)' "
     "ein Einstiegsgewicht ein, dann füllt sich die Plan-Spalte des "
     "Trainingsblatts. Aus den bisherigen Daten lässt sich dafür kein "
     "seriöser Wert ableiten - das entscheidest du im ersten Satz."),
]:
    ws.cell(r, 2, lab).font = Font(name=FONT, size=10, bold=True, color=AMBER)
    ws.cell(r, 2).alignment = Alignment(horizontal="left", vertical="top")
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
    c = ws.cell(r, 3, txt)
    c.font, c.alignment = F_BODY, LW
    for col in range(2, 6):
        ws.cell(r, col).border = B_ALL
    ws.row_dimensions[r].height = zeilenhoehe(txt)
    r += 1

r += 1
ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
ws.cell(r, 2, "Alle Kennzahlen sind Formeln. Sobald du im Log Zeilen "
              "ergänzt, aktualisieren sich Auswertung, Progression, Rekorde "
              "und Dashboard von selbst.").font = F_SMALL
druck(ws, "B1:E%d" % r)

# ==========================================================================
# ÜBUNGEN (Stammdaten)
# ==========================================================================
wsu = sheet("Übungen")
titelbalken(wsu, 1, 10, "ÜBUNGEN  |  STAMMDATEN UND PLANVORGABEN",
            "Neue Übung hier ergänzen - Dropdowns, Trainingsblatt und "
            "Auswertungen ziehen automatisch nach. Aktiv = nein heisst "
            "Archiv: die Übung verschwindet aus der Planung, ihre Historie "
            "bleibt in Log und Auswertung erhalten.")
kopfzeile(wsu, 3, 1,
          ["Übung", "Block", "Gerät / Variante", "Ziel-Wdh", "Ziel-\nSätze",
           "Ziel-\nRPE", "Start (kg)", "Max (kg)", "Aktiv", "Notiz"],
          [26, 15, 22, 10, 8, 8, 10, 10, 8, 46], height=30)

for i in range(EX_SLOTS):
    row = UEB_FIRST + i
    u = UEBUNGEN[i] if i < len(UEBUNGEN) else None
    werte = [None] * 10
    if u:
        werte = [u["name"], u["block"], u["geraet"], u["wdh"], u["saetze"],
                 u["rpe"], u["start"], u["maxlast"],
                 "ja" if u["aktiv"] else "nein", u["notiz"]]
    for j, v in enumerate(werte):
        c = wsu.cell(row, 1 + j, v)
        c.font, c.fill, c.border = F_BODY, FILL_INPUT, B_ALL
        if j == 9:
            c.alignment = LW
        elif j in (0, 1, 2):
            c.alignment = L
        else:
            c.alignment = C
        if j in (6, 7):
            c.number_format = NF_KG
    if u and not u["aktiv"]:
        for j in range(10):
            wsu.cell(row, 1 + j).font = Font(name=FONT, size=10,
                                             color="8A94A0", italic=True)
    wsu.row_dimensions[row].height = 46 if u else 18

dv_block = DataValidation(type="list", formula1='"%s"' % ",".join(BLOCKS),
                          allow_blank=True)
wsu.add_data_validation(dv_block)
dv_block.add("B%d:B%d" % (UEB_FIRST, UEB_LAST))

dv_aktiv = DataValidation(type="list", formula1='"ja,nein"', allow_blank=True)
dv_aktiv.errorTitle = "Aktiv"
dv_aktiv.error = ("ja = Teil der Planung, nein = Archiv. Die Historie bleibt "
                  "in beiden Fällen erhalten.")
wsu.add_data_validation(dv_aktiv)
dv_aktiv.add("I%d:I%d" % (UEB_FIRST, UEB_LAST))

hinweis = UEB_LAST + 2
wsu.merge_cells(start_row=hinweis, start_column=1, end_row=hinweis,
                end_column=10)
c = wsu.cell(hinweis, 1,
             "Reihenfolge hier = Reihenfolge in allen Auswertungen und auf "
             "dem Trainingsblatt.   ·   'Start (kg)' braucht nur eine Übung "
             "ohne Historie: solange keine Arbeitssätze im Log stehen, "
             "speist dieser Wert die Plan-Spalte des Trainingsblatts. Sobald "
             "die erste Einheit erfasst ist, rechnet das Logbuch aus den "
             "echten Werten weiter.   ·   'Max (kg)' begrenzt den "
             "Zielvorschlag nach oben, etwa am Ende des Steckgewichts - "
             "darüber steigerst du über Tempo, Pausen und Wiederholungen "
             "statt über Last.   ·   Archivierte Übungen erscheinen grau und "
             "tauchen im Trainingsblatt nicht mehr auf.")
c.font, c.alignment = F_SMALL, LW
wsu.row_dimensions[hinweis].height = 40
wsu.freeze_panes = "B4"
druck(wsu, "A1:J%d" % hinweis, landscape=True, titles="1:3")

# ==========================================================================
# EINHEITEN
# ==========================================================================
wse = sheet("Einheiten")
titelbalken(wse, 1, 11, "EINHEITEN  |  KOPFDATEN JE TRAINING",
            "Gelb ausfüllen. Das Datum wandert automatisch ins Log; Sätze, "
            "Volumen und Tonnage rechnen sich aus dem Log.")
kopfzeile(wse, 3, 1,
          ["Einheit", "Datum", "Fokus", "Körper-\ngewicht (kg)",
           "Dauer\n(min)", "Schlaf\n(h)", "Gefühl\n1-5", "Arbeits-\nsätze",
           "Arbeits-\nvolumen (kg)", "Tonnage\ngesamt (kg)", "Notiz"],
          [9, 13, 17, 12, 9, 9, 9, 10, 14, 13, 38], height=32)

for i in range(SESSION_SLOTS):
    row = EINH_FIRST + i
    c = wse.cell(row, 1, i + 1)
    c.font, c.alignment, c.fill, c.border = F_BOLD, C, FILL_INPUT, B_ALL
    for col, nf in ((2, NF_DATE), (3, None), (4, NF_KG), (5, NF_INT),
                    (6, NF_KG), (7, NF_INT), (11, None)):
        c = wse.cell(row, col)
        c.font, c.fill, c.border = F_BODY, FILL_INPUT, B_ALL
        c.alignment = L if col in (3, 11) else C
        if nf:
            c.number_format = nf
    wse.cell(row, 8, "=IF(COUNTIFS(%s,$A%d,%s,\"A\")=0,\"\","
                     "COUNTIFS(%s,$A%d,%s,\"A\"))"
             % (B_, row, E_, B_, row, E_))
    wse.cell(row, 9, "=IF($H%d=\"\",\"\",SUMIFS(%s,%s,$A%d,%s,\"A\"))"
             % (row, I_, B_, row, E_))
    wse.cell(row, 10, "=IF($H%d=\"\",\"\",SUMIFS(%s,%s,$A%d))"
             % (row, I_, B_, row))
    for col in (8, 9, 10):
        c = wse.cell(row, col)
        c.font, c.alignment, c.fill, c.border = F_BODY, C, FILL_CALC, B_ALL
        c.number_format = NF_INT
    wse.row_dimensions[row].height = 18

dv_fokus = DataValidation(
    type="list",
    formula1='"%s,Beine komplett"' % ",".join(BLOCKS), allow_blank=True)
wse.add_data_validation(dv_fokus)
dv_fokus.add("C%d:C%d" % (EINH_FIRST, EINH_LAST))

srow = EINH_LAST + 1
wse.cell(srow, 1, "Summe").font = F_BOLD
wse.cell(srow, 1).alignment = C
for col in (8, 9, 10):
    L_ = get_column_letter(col)
    c = wse.cell(srow, col, "=SUM(%s%d:%s%d)" % (L_, EINH_FIRST, L_,
                                                 EINH_LAST))
    c.font, c.alignment, c.number_format = F_BOLD, C, NF_INT
for col in range(1, 12):
    wse.cell(srow, col).border = Border(top=med)
    wse.cell(srow, col).fill = FILL_LIGHT

wse.cell(srow + 2, 1, "Ohne Datum funktioniert alles weiter - das Datum ist "
                      "reine Dokumentation.").font = F_SMALL
wse.freeze_panes = "B4"
druck(wse, "A1:K%d" % (srow + 2), landscape=True, titles="1:3")

# ==========================================================================
# LOG
# ==========================================================================
wsl = sheet("Log")
titelbalken(wsl, 1, 12, "TRAININGSLOG  |  EIN SATZ PRO ZEILE",
            "Gelbe Spalten ausfüllen. Datum, Block, Volumen und e1RM rechnen "
            "automatisch.")
kopfzeile(wsl, 3, 1,
          ["Datum", "Einheit", "Block", "Übung", "Satz", "Gewicht\n(kg)",
           "Wdh", "RPE", "Volumen\n(kg)", "e1RM\n(kg)", "Drop-Kette",
           "Notiz"],
          [12, 9, 14, 22, 7, 10, 7, 7, 11, 10, 24, 34], height=32)

for i in range(LOG_ROWS):
    row = LOG_FIRST + i
    data = ROWS[i] if i < len(ROWS) else None
    # 0 abfangen: ein leeres Datumsfeld liefert ueber INDEX sonst 0
    # und damit den 30.12.1899.
    idx = ("INDEX(Einheiten!$B$%d:$B$%d,MATCH($B%d,Einheiten!$A$%d:$A$%d,0))"
           % (EINH_FIRST, EINH_LAST, row, EINH_FIRST, EINH_LAST))
    c = wsl.cell(row, 1, "=IFERROR(IF($B%d=\"\",\"\",IF(%s=0,\"\",%s)),\"\")"
                 % (row, idx, idx))
    c.font, c.alignment, c.fill, c.number_format = (F_BODY, C, FILL_CALC,
                                                    NF_DATE)
    c = wsl.cell(row, 2, data[0] if data else None)
    c.font, c.alignment, c.fill = F_BODY, C, FILL_INPUT
    c = wsl.cell(row, 3, "=IFERROR(IF($D%d=\"\",\"\",INDEX(%s!$B$%d:$B$%d,"
                         "MATCH($D%d,%s!$A$%d:$A$%d,0))),\"\")"
                 % (row, UEB, UEB_FIRST, UEB_LAST, row, UEB, UEB_FIRST,
                    UEB_LAST))
    c.font, c.alignment, c.fill = F_BODY, L, FILL_CALC
    c = wsl.cell(row, 4, data[2] if data else None)
    c.font, c.alignment, c.fill = F_BODY, L, FILL_INPUT
    c = wsl.cell(row, 5, data[3] if data else None)
    c.font, c.alignment, c.fill = F_BOLD, C, FILL_INPUT
    c = wsl.cell(row, 6, data[4] if data else None)
    c.font, c.alignment, c.fill, c.number_format = F_BODY, C, FILL_INPUT, NF_KG
    c = wsl.cell(row, 7, data[5] if data else None)
    c.font, c.alignment, c.fill, c.number_format = (F_BODY, C, FILL_INPUT,
                                                    NF_INT)
    c = wsl.cell(row, 8)
    c.font, c.alignment, c.fill, c.number_format = F_BODY, C, FILL_INPUT, NF_KG
    c = wsl.cell(row, 9, "=IF(AND(ISNUMBER($F%d),ISNUMBER($G%d),$E%d<>\"R\"),"
                         "$F%d*$G%d,\"\")" % (row, row, row, row, row))
    c.font, c.alignment, c.fill, c.number_format = (F_BODY, C, FILL_CALC,
                                                    NF_INT)
    c = wsl.cell(row, 10, "=IF(AND($E%d=\"A\",ISNUMBER($F%d),ISNUMBER($G%d)),"
                          "$F%d*(1+$G%d/30),\"\")" % (row, row, row, row, row))
    c.font, c.alignment, c.fill, c.number_format = F_BODY, C, FILL_CALC, NF_KG
    c = wsl.cell(row, 11, data[6] if data else None)
    c.font, c.alignment, c.fill = F_BODY, L, FILL_INPUT
    c = wsl.cell(row, 12, data[7] if data else None)
    c.font, c.alignment, c.fill = F_BODY, L, FILL_INPUT
    for col in range(1, 13):
        wsl.cell(row, col).border = B_ALL
    wsl.row_dimensions[row].height = 16

wsl.cell(LOG_FIRST + 15, 12).comment = Comment(
    "Original 152.2 kg. Überall sonst steht 152.5 kg, daher als Tippfehler "
    "gewertet.", "Logbuch")

dv_ueb = DataValidation(type="list",
                        formula1="=%s!$A$%d:$A$%d" % (UEB, UEB_FIRST,
                                                      UEB_LAST),
                        allow_blank=True)
dv_ueb.errorTitle = "Unbekannte Übung"
dv_ueb.error = "Bitte eine Übung aus dem Blatt 'Übungen' wählen."
wsl.add_data_validation(dv_ueb)
dv_ueb.add("D%d:D%d" % (LOG_FIRST, LOG_LAST))

dv_satz = DataValidation(type="list", formula1='"W,A,R"', allow_blank=True)
dv_satz.errorTitle = "Satztyp"
dv_satz.error = "W = Warmup, A = Arbeitssatz, R = Reduktionssatz"
wsl.add_data_validation(dv_satz)
dv_satz.add("E%d:E%d" % (LOG_FIRST, LOG_LAST))

dv_rpe = DataValidation(type="decimal", operator="between", formula1=5,
                        formula2=10, allow_blank=True)
dv_rpe.errorTitle = "RPE"
dv_rpe.error = "RPE zwischen 5 und 10 eintragen."
wsl.add_data_validation(dv_rpe)
dv_rpe.add("H%d:H%d" % (LOG_FIRST, LOG_LAST))

rng = "A%d:L%d" % (LOG_FIRST, LOG_LAST)
wsl.conditional_formatting.add(rng, FormulaRule(
    formula=['$E%d="A"' % LOG_FIRST],
    fill=PatternFill("solid", bgColor="E7F2EA")))
wsl.conditional_formatting.add(rng, FormulaRule(
    formula=['$E%d="R"' % LOG_FIRST],
    fill=PatternFill("solid", bgColor="F0EBF6")))

wsl.freeze_panes = "C4"
wsl.auto_filter.ref = "A3:L%d" % LOG_LAST
druck(wsl, "A1:L%d" % (LOG_FIRST + len(ROWS) + 39), landscape=True,
      titles="1:3",
      fussnote="Grün = Arbeitssatz · Violett = Reduktionssatz")

# ==========================================================================
# AUSWERTUNG
# ==========================================================================
wsa = sheet("Auswertung")
LASTCOL = 2 + SESSIONS
titelbalken(wsa, 1, LASTCOL, "AUSWERTUNG  |  JE ÜBUNG UND EINHEIT",
            "Nur Arbeitssätze (A). Leere Zelle = Übung in dieser Einheit "
            "nicht trainiert. Drei Tabellen, je eine Druckseite.")
wsa.column_dimensions["A"].width = 24
for i in range(SESSIONS):
    wsa.column_dimensions[get_column_letter(2 + i)].width = 8.5
wsa.column_dimensions[get_column_letter(LASTCOL)].width = 12


def auswertungstabelle(start, titel, formelbau, nf, spaltentitel, aggregat):
    abschnitt(wsa, start, 1, LASTCOL, titel)
    hrow = start + 1
    # Einheit-Nummern als Zahl, nicht als Text - sonst greifen die Vergleiche
    # gegen die numerische Log-Spalte B in SUMPRODUCT nicht.
    labels = ["Übung"] + list(range(1, SESSIONS + 1)) + [spaltentitel]
    for i, lab in enumerate(labels):
        c = wsa.cell(hrow, 1 + i, lab)
        c.font, c.fill, c.alignment, c.border = F_H1, FILL_HEAD, CW, B_ALL
    wsa.row_dimensions[hrow].height = 22
    first = hrow + 1
    for k in range(EX_SLOTS):
        row = first + k
        zebra = FILL_LIGHT if k % 2 == 0 else PatternFill()
        c = wsa.cell(row, 1, "=IF(%s!$A%d=\"\",\"\",%s!$A%d)"
                     % (UEB, UEB_FIRST + k, UEB, UEB_FIRST + k))
        c.font, c.alignment, c.border, c.fill = F_BOLD, L, B_ALL, zebra
        for s in range(SESSIONS):
            col = 2 + s
            cc = wsa.cell(row, col,
                          formelbau("$A%d" % row,
                                    "%s$%d" % (get_column_letter(col), hrow)))
            cc.font, cc.alignment, cc.border = F_BODY, C, B_ALL
            cc.number_format, cc.fill = nf, zebra
        span = "B%d:%s%d" % (row, get_column_letter(LASTCOL - 1), row)
        cc = wsa.cell(row, LASTCOL,
                      "=IF(COUNT(%s)=0,\"\",%s(%s))" % (span, aggregat, span))
        cc.font, cc.alignment, cc.border = F_BOLD, C, B_ALL
        cc.number_format, cc.fill = nf, FILL_CALC
        wsa.row_dimensions[row].height = 17
    last = first + EX_SLOTS - 1
    archiv_grau(wsa, 1, 1, first, last)
    wsa.conditional_formatting.add(
        "B%d:%s%d" % (first, get_column_letter(LASTCOL - 1), last),
        ColorScaleRule(start_type="min", start_color="FFFFFF",
                       end_type="max", end_color="9EC5E8"))
    return last


e1 = auswertungstabelle(
    4, "1  Arbeitsvolumen (kg)  ·  Gewicht × Wdh, nur Arbeitssätze",
    f_volumen, NF_INT, "Summe", "SUM")
start2 = e1 + 3
e2 = auswertungstabelle(
    start2, "2  Top-Gewicht (kg)  ·  schwerster Arbeitssatz der Einheit",
    f_topgewicht, NF_KG, "Bestwert", "MAX")
start3 = e2 + 3
e3 = auswertungstabelle(
    start3, "3  Bester e1RM (kg)  ·  Epley: Gewicht × (1 + Wdh / 30)",
    f_e1rm, NF_KG, "Bestwert", "MAX")

wsa.row_breaks.append(Break(id=start2 - 1))
wsa.row_breaks.append(Break(id=start3 - 1))
wsa.freeze_panes = "B5"
druck(wsa, "A1:%s%d" % (get_column_letter(LASTCOL), e3 + 1), landscape=True,
      titles="1:2")

# ==========================================================================
# PROGRESSION
# ==========================================================================
wsp = sheet("Progression")
titelbalken(wsp, 1, 11, "PROGRESSION  |  ERSTE GEGEN LETZTE EINHEIT",
            "Richtung und Grösse der Veränderung je Übung sowie der Abstand "
            "zum eigenen Bestwert.")
kopfzeile(wsp, 3, 1,
          ["Übung", "Erste\nEinheit", "Volumen\nerste (kg)",
           "Letzte\nEinheit", "Volumen\nletzte (kg)", "Veränderung\n(kg)",
           "Veränderung\n(%)", "Top-Gewicht\nzuletzt (kg)",
           "Bestes Top-\nGewicht (kg)", "Abstand zum\nBestwert (kg)",
           "Trend"],
          [24, 9, 13, 9, 13, 13, 13, 13, 13, 14, 14], height=34)

PROG_FIRST = 4
for k in range(EX_SLOTS):
    row = PROG_FIRST + k
    ex = "$A%d" % row
    c = wsp.cell(row, 1, "=IF(%s!$A%d=\"\",\"\",%s!$A%d)"
                 % (UEB, UEB_FIRST + k, UEB, UEB_FIRST + k))
    c.font, c.alignment = F_BOLD, L
    erste = ("SUMPRODUCT(MIN((%s=%s)*(%s=\"A\")*%s+((%s<>%s)+(%s<>\"A\")>0)"
             "*9999))" % (D_, ex, E_, B_, D_, ex, E_))
    letzte = "SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*%s))" % (D_, ex, E_, B_)
    wsp.cell(row, 2, "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))"
             % (ex, letzte, erste))
    wsp.cell(row, 4, "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))"
             % (ex, letzte, letzte))
    wsp.cell(row, 3, "=IF($B%d=\"\",\"\",SUMIFS(%s,%s,%s,%s,$B%d,%s,\"A\"))"
             % (row, I_, D_, ex, B_, row, E_))
    wsp.cell(row, 5, "=IF($D%d=\"\",\"\",SUMIFS(%s,%s,%s,%s,$D%d,%s,\"A\"))"
             % (row, I_, D_, ex, B_, row, E_))
    wsp.cell(row, 6, "=IF(OR($C%d=\"\",$E%d=\"\"),\"\",$E%d-$C%d)"
             % (row, row, row, row))
    wsp.cell(row, 7, "=IF(OR($C%d=\"\",$E%d=\"\",$C%d=0),\"\",$E%d/$C%d-1)"
             % (row, row, row, row, row))
    top_letzt = ("SUMPRODUCT(MAX((%s=%s)*(%s=$D%d)*(%s=\"A\")*(%s<>\"\")*%s))"
                 % (D_, ex, B_, row, E_, F_, F_))
    top_best = ("SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*(%s<>\"\")*%s))"
                % (D_, ex, E_, F_, F_))
    wsp.cell(row, 8, "=IF($D%d=\"\",\"\",IF(%s=0,\"\",%s))"
             % (row, top_letzt, top_letzt))
    wsp.cell(row, 9, "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))"
             % (ex, top_best, top_best))
    wsp.cell(row, 10, "=IF(OR($H%d=\"\",$I%d=\"\"),\"\",$H%d-$I%d)"
             % (row, row, row, row))
    wsp.cell(row, 11, "=IF($G%d=\"\",\"\",IF($G%d>0.05,\"steigend\","
                      "IF($G%d<-0.05,\"fallend\",\"stabil\")))"
             % (row, row, row))
    fmts = {2: NF_INT, 3: NF_INT, 4: NF_INT, 5: NF_INT, 6: NF_INT,
            7: NF_PCT, 8: NF_KG, 9: NF_KG, 10: NF_KG}
    for col in range(1, 12):
        cc = wsp.cell(row, col)
        cc.border = B_ALL
        if col > 1:
            cc.font, cc.alignment = F_BODY, C
        if col in fmts:
            cc.number_format = fmts[col]
        if k % 2 == 0:
            cc.fill = FILL_LIGHT
    wsp.row_dimensions[row].height = 18

PROG_LAST = PROG_FIRST + EX_SLOTS - 1
for bereich, bedingung, farbe in (
        ("F%d:G%d" % (PROG_FIRST, PROG_LAST),
         'AND($G%d<>"",$G%d>0.05)' % (PROG_FIRST, PROG_FIRST), GREEN),
        ("F%d:G%d" % (PROG_FIRST, PROG_LAST),
         'AND($G%d<>"",$G%d<-0.05)' % (PROG_FIRST, PROG_FIRST), RED),
        ("K%d:K%d" % (PROG_FIRST, PROG_LAST),
         '$K%d="steigend"' % PROG_FIRST, GREEN),
        ("K%d:K%d" % (PROG_FIRST, PROG_LAST),
         '$K%d="fallend"' % PROG_FIRST, RED)):
    wsp.conditional_formatting.add(
        bereich, FormulaRule(formula=[bedingung],
                             font=Font(name=FONT, size=10, bold=True,
                                       color=farbe)))

archiv_grau(wsp, 1, 11, PROG_FIRST, PROG_LAST)

hin = PROG_LAST + 2
wsp.merge_cells(start_row=hin, start_column=1, end_row=hin, end_column=11)
c = wsp.cell(hin, 1,
             "Lesehilfe: Volumen schwankt mit der Wiederholungszahl. "
             "Fallendes Volumen bei steigendem Top-Gewicht ist kein "
             "Rückschritt, sondern eine Verschiebung Richtung Kraft. "
             "Schwelle für steigend / fallend: 5 Prozent.")
c.font, c.alignment = F_SMALL, LW
wsp.row_dimensions[hin].height = 26
wsp.freeze_panes = "B4"
druck(wsp, "A1:K%d" % hin, landscape=True, titles="1:3")

# ==========================================================================
# REKORDE
# ==========================================================================
wsr = sheet("Rekorde")
titelbalken(wsr, 1, 14, "REKORDE  |  BESTWERTE JE ÜBUNG",
            "Über alle erfassten Einheiten, nur Arbeitssätze (A).")
kopfzeile(wsr, 3, 1,
          ["Übung", "Block", "Ein-\nheiten", "Arbeits-\nsätze",
           "Gesamt-\nvolumen (kg)", "Top-Gewicht\n(kg)", "in\nEinheit",
           "Bester e1RM\n(kg)", "in\nEinheit", "Bestes Satz-\nvolumen (kg)",
           "Letzte\nEinheit", "Top-Gewicht\nzuletzt (kg)", "Wdh\ndazu",
           "Nächstes\nZiel (kg)"],
          [24, 14, 8, 9, 13, 12, 8, 12, 8, 13, 9, 12, 8, 11], height=34)

for k in range(EX_SLOTS):
    row = REK_FIRST + k
    ex = "$A%d" % row
    c = wsr.cell(row, 1, "=IF(%s!$A%d=\"\",\"\",%s!$A%d)"
                 % (UEB, UEB_FIRST + k, UEB, UEB_FIRST + k))
    c.font, c.alignment = F_BOLD, L
    c = wsr.cell(row, 2, "=IF(%s!$B%d=\"\",\"\",%s!$B%d)"
                 % (UEB, UEB_FIRST + k, UEB, UEB_FIRST + k))
    c.font, c.alignment = F_BODY, L
    saetze = "COUNTIFS(%s,%s,%s,\"A\")" % (D_, ex, E_)
    wsr.cell(row, 4, "=IF(%s=\"\",\"\",IF(%s=0,\"\",%s))"
             % (ex, saetze, saetze))
    # Anzahl verschiedener Einheiten: je Einheit prüfen, ob ein A-Satz da ist
    einh = ("SUMPRODUCT((COUNTIFS(%s,%s,%s,\"A\",%s,Einheiten!$A$%d:$A$%d)"
            ">0)*1)" % (D_, ex, E_, B_, EINH_FIRST, EINH_LAST))
    wsr.cell(row, 3, "=IF($D%d=\"\",\"\",%s)" % (row, einh))
    wsr.cell(row, 5, "=IF($D%d=\"\",\"\",SUMIFS(%s,%s,%s,%s,\"A\"))"
             % (row, I_, D_, ex, E_))
    top = "SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*(%s<>\"\")*%s))" % (D_, ex, E_,
                                                                 F_, F_)
    wsr.cell(row, 6, "=IF($D%d=\"\",\"\",IF(%s=0,\"\",%s))" % (row, top, top))
    wsr.cell(row, 7, "=IF($F%d=\"\",\"\",SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*"
                     "(%s=$F%d)*%s)))" % (row, D_, ex, E_, F_, row, B_))
    e1rm = ("SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*(%s<>\"\")*(%s<>\"\")*%s*"
            "(1+%s/30)))" % (D_, ex, E_, F_, G_, F_, G_))
    wsr.cell(row, 8, "=IF($D%d=\"\",\"\",IF(%s=0,\"\",%s))"
             % (row, e1rm, e1rm))
    wsr.cell(row, 9, "=IF($H%d=\"\",\"\",SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*"
                     "(%s<>\"\")*(%s<>\"\")*(ROUND(%s*(1+%s/30),6)="
                     "ROUND($H%d,6))*%s)))"
             % (row, D_, ex, E_, F_, G_, F_, G_, row, B_))
    satzvol = ("SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*(%s<>\"\")*(%s<>\"\")*%s*"
               "%s))" % (D_, ex, E_, F_, G_, F_, G_))
    wsr.cell(row, 10, "=IF($D%d=\"\",\"\",IF(%s=0,\"\",%s))"
             % (row, satzvol, satzvol))
    letzte = "SUMPRODUCT(MAX((%s=%s)*(%s=\"A\")*%s))" % (D_, ex, E_, B_)
    wsr.cell(row, 11, "=IF($D%d=\"\",\"\",IF(%s=0,\"\",%s))"
             % (row, letzte, letzte))
    toplast = ("SUMPRODUCT(MAX((%s=%s)*(%s=$K%d)*(%s=\"A\")*(%s<>\"\")*%s))"
               % (D_, ex, B_, row, E_, F_, F_))
    wsr.cell(row, 12, "=IF($K%d=\"\",\"\",IF(%s=0,\"\",%s))"
             % (row, toplast, toplast))
    wdh = ("SUMPRODUCT(MAX((%s=%s)*(%s=$K%d)*(%s=\"A\")*(%s=$L%d)*%s))"
           % (D_, ex, B_, row, E_, F_, row, G_))
    wsr.cell(row, 13, "=IF($L%d=\"\",\"\",IF(%s=0,\"\",%s))"
             % (row, wdh, wdh))
    # Mit Historie: letztes Top-Gewicht plus 2.5 %, gedeckelt durch die
    # Lastobergrenze. Ohne Historie greift das Startgewicht.
    ueb_row = UEB_FIRST + k
    steig = "ROUND($L%d*1.025*2,0)/2" % row
    wsr.cell(row, 14, "=IF($L%d<>\"\",IF(%s!$H%d=\"\",%s,"
                      "MIN(%s,%s!$H%d)),IF(%s!$G%d=\"\",\"\",%s!$G%d))"
             % (row, UEB, ueb_row, steig, steig, UEB, ueb_row, UEB, ueb_row,
                UEB, ueb_row))
    fmts = {3: NF_INT, 4: NF_INT, 5: NF_INT, 6: NF_KG, 7: NF_INT, 8: NF_KG,
            9: NF_INT, 10: NF_INT, 11: NF_INT, 12: NF_KG, 13: NF_INT,
            14: NF_KG}
    for col in range(1, 15):
        cc = wsr.cell(row, col)
        cc.border = B_ALL
        if col > 2:
            cc.font, cc.alignment = F_BODY, C
        if col in fmts:
            cc.number_format = fmts[col]
        if k % 2 == 0:
            cc.fill = FILL_LIGHT
    for col in (6, 8, 14):
        wsr.cell(row, col).font = Font(name=FONT, size=10, bold=True,
                                       color=AMBER)
    wsr.row_dimensions[row].height = 18

archiv_grau(wsr, 1, 14, REK_FIRST, REK_LAST)

note = REK_LAST + 2
wsr.merge_cells(start_row=note, start_column=1, end_row=note, end_column=14)
c = wsr.cell(note, 1,
             "Nächstes Ziel = letztes Top-Gewicht plus 2.5 Prozent, gerundet "
             "auf 0.5 kg, begrenzt durch 'Max (kg)' aus dem Blatt 'Übungen'. "
             "Ohne Historie greift stattdessen das Startgewicht. Richtwert, "
             "keine Vorgabe - an Maschinen bestimmt die Steckplatte den "
             "Sprung.   ·   Graue, kursive Zeilen sind archivierte Übungen: "
             "nicht mehr im Plan, Historie bleibt.")
c.font, c.alignment = F_SMALL, LW
wsr.row_dimensions[note].height = 30
wsr.freeze_panes = "C4"
druck(wsr, "A1:N%d" % note, landscape=True, titles="1:3")

# ==========================================================================
# TRAININGSBLATT (Druckvorlage zum Mitnehmen)
# ==========================================================================
wst = sheet("Trainingsblatt")
for col, w in zip("ABCDEFGH", [5, 9, 13, 13, 10, 8, 7, 30]):
    wst.column_dimensions[col].width = w


def rek(spalte, exref):
    """Wert aus dem Blatt 'Rekorde' zur Übung in exref (ohne führendes =)."""
    return ("IFERROR(INDEX(Rekorde!$%s$%d:$%s$%d,MATCH(%s,Rekorde!$A$%d:"
            "$A$%d,0)),\"\")" % (spalte, REK_FIRST, spalte, REK_LAST, exref,
                                 REK_FIRST, REK_LAST))


row = 1
for bi, block in enumerate(BLOCKS):
    wst.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    c = wst.cell(row, 1, "TRAININGSBLATT  |  %s" % block.upper())
    c.font, c.fill, c.alignment = F_TITLE, FILL_TITLE, L_IND
    for col in range(1, 9):
        wst.cell(row, col).fill = FILL_TITLE
    wst.row_dimensions[row].height = 28
    row += 1

    # Kopffelder zum Ausfüllen: Label darüber, Linie darunter
    felder = [("Datum", 1, 2), ("Einheit Nr.", 3, 1), ("Körpergewicht", 4, 1),
              ("Start / Ende", 5, 2), ("Schlaf (h)", 7, 2)]
    for lab, col, span in felder:
        c = wst.cell(row, col, lab)
        c.font = F_SMALL
        c.alignment = Alignment(horizontal="left", vertical="bottom")
        if span > 1:
            wst.merge_cells(start_row=row, start_column=col, end_row=row,
                            end_column=col + span - 1)
            wst.merge_cells(start_row=row + 1, start_column=col,
                            end_row=row + 1, end_column=col + span - 1)
        for k in range(span):
            wst.cell(row + 1, col + k).border = Border(
                bottom=Side("medium", color=NAVY))
    wst.row_dimensions[row].height = 13
    wst.row_dimensions[row + 1].height = 20
    row += 3

    # Nur aktive Übungen aufs Blatt - Archiv bleibt aussen vor.
    aktive = [(i, u) for i, u in enumerate(UEBUNGEN)
              if u["block"] == block and u["aktiv"]]
    for i, u in aktive:
        exref = "%s!$A$%d" % (UEB, UEB_FIRST + i)
        wdhref = "%s!$D$%d" % (UEB, UEB_FIRST + i)
        saetzeref = "%s!$E$%d" % (UEB, UEB_FIRST + i)
        rperef = "%s!$F$%d" % (UEB, UEB_FIRST + i)
        ziel = rek("N", exref)
        # Satzschema aus den Planvorgaben: zwei Warmups, dann die
        # Ziel-Arbeitssätze, der letzte optional als Reduktionssatz.
        satzmuster = (["W"] * len(WARMUP_FAKTOR)
                      + ["A"] * (u["saetze"] - 1) + [u["letzter"]])

        wst.merge_cells(start_row=row, start_column=1, end_row=row,
                        end_column=8)
        c = wst.cell(row, 1, "=%s" % exref)
        c.font, c.fill, c.alignment = F_H1, FILL_HEAD, L_IND
        for col in range(1, 9):
            wst.cell(row, col).fill = FILL_HEAD
            wst.cell(row, col).border = B_ALL
        wst.row_dimensions[row].height = 19
        row += 1

        wst.merge_cells(start_row=row, start_column=1, end_row=row,
                        end_column=8)
        # Vorgabe-Teil steht immer, der Historien-Teil nur wenn es ihn gibt.
        vorgabe = ("\"Vorgabe: \"&%s&\" × \"&%s&\" Wdh @ RPE \"&%s"
                   % (saetzeref, wdhref, rperef))
        historie = ("\"Zuletzt: \"&TEXT(%s,\"0.#\")&\" kg × \"&"
                    "IF(%s=\"\",\"?\",TEXT(%s,\"0\"))&\" Wdh     ·     "
                    "Bestwert: \"&TEXT(%s,\"0.#\")&\" kg     ·     \""
                    % (rek("L", exref), rek("M", exref), rek("M", exref),
                       rek("F", exref)))
        neu = ("IF(%s=\"\",\"Neu im Plan - Startgewicht im Blatt 'Übungen' "
               "eintragen     ·     \",\"Neu im Plan     ·     Start: \"&"
               "TEXT(%s,\"0.#\")&\" kg     ·     \")" % (ziel, ziel))
        maxref = "%s!$H$%d" % (UEB, UEB_FIRST + i)
        # Am Stackende steht der Zielwert still - das gehoert aufs Blatt,
        # sonst widerspricht der Vorschlag der Planvorgabe.
        deckel = ("IF(AND(%s<>\"\",%s<>\"\",%s>=%s),\"Stackende, über "
                  "Tempo und Pausen steigern     ·     \",\"\")"
                  % (maxref, ziel, ziel, maxref))
        ziel_teil = ("IF(%s=\"\",\"\",\"Ziel heute: \"&TEXT(%s,\"0.#\")&"
                     "\" kg     ·     \")&%s" % (ziel, ziel, deckel))
        c = wst.cell(row, 1,
                     "=IF(%s=\"\",%s,%s&%s)&%s"
                     % (rek("L", exref), neu, historie, ziel_teil, vorgabe))
        c.font = Font(name=FONT, size=9, color=NAVY)
        c.fill, c.alignment = FILL_LIGHT, L_IND
        for col in range(1, 9):
            wst.cell(row, col).fill = FILL_LIGHT
            wst.cell(row, col).border = B_ALL
        wst.row_dimensions[row].height = 15
        row += 1

        for j, lab in enumerate(["#", "Typ", "Plan (kg)", "Gewicht (kg)",
                                 "Wdh", "RPE", "OK", "Notiz"]):
            c = wst.cell(row, 1 + j, lab)
            c.font = Font(name=FONT, size=8.5, bold=True, color=NAVY)
            c.fill, c.alignment, c.border = FILL_CALC, C, B_ALL
        wst.row_dimensions[row].height = 14
        row += 1

        for s, typ in enumerate(satzmuster):
            c = wst.cell(row, 1, s + 1)
            c.font, c.alignment = F_SMALL, C
            c = wst.cell(row, 2, typ)
            c.font, c.alignment = F_BOLD, C
            if typ == "A":
                c.fill = FILL_WORK
            # Warmups nach Rampe, Arbeitssätze auf Zielgewicht,
            # Reduktionssatz bleibt offen.
            fak = (WARMUP_FAKTOR[s] if s < len(WARMUP_FAKTOR)
                   else (1.0 if typ == "A" else None))
            if fak is not None:
                c = wst.cell(row, 3, "=IF(%s=\"\",\"\",ROUND(%s*%s*2,0)/2)"
                             % (ziel, ziel, fak))
                c.font = Font(name=FONT, size=10, color="4A5568")
                c.alignment, c.number_format = C, NF_KG
            for col in range(4, 9):
                wst.cell(row, col).fill = FILL_WHITE
            for col in range(1, 9):
                wst.cell(row, col).border = B_ALL
            wst.row_dimensions[row].height = 20
            row += 1
        row += 1

    wst.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    c = wst.cell(row, 1, "Notizen zur Einheit")
    c.font, c.fill, c.alignment = F_H1, FILL_SUB, L_IND
    for col in range(1, 9):
        wst.cell(row, col).fill = FILL_SUB
    wst.row_dimensions[row].height = 16
    row += 1
    for _ in range(3):
        wst.merge_cells(start_row=row, start_column=1, end_row=row,
                        end_column=8)
        for col in range(1, 9):
            wst.cell(row, col).border = Border(bottom=thin)
        wst.row_dimensions[row].height = 18
        row += 1

    if bi < len(BLOCKS) - 1:
        wst.row_breaks.append(Break(id=row - 1))
        row += 1

druck(wst, "A1:H%d" % (row - 1), margins=(0.5, 0.4, 0.5, 0.5),
      fussnote="Plan (kg) = Aufwärm-Rampe 45 % / 70 %, dann Zielgewicht aus "
               "dem Blatt 'Rekorde'")

# ==========================================================================
# DASHBOARD
# ==========================================================================
wsd = sheet("Dashboard")
for col, w in zip("ABCDEFGHIJ", [2, 21, 13, 2, 21, 13, 2, 21, 13, 5]):
    wsd.column_dimensions[col].width = w
titelbalken(wsd, 1, 10, "DASHBOARD  |  BEINTRAINING AUF EINEN BLICK",
            "Alle Werte rechnen sich aus dem Log.")

kacheln = [
    ("Einheiten", "=COUNT(Einheiten!$I$%d:$I$%d)" % (EINH_FIRST, EINH_LAST),
     NF_INT),
    ("Sätze gesamt", "=COUNTA(%s)" % E_, NF_INT),
    ("Arbeitssätze", "=COUNTIF(%s,\"A\")" % E_, NF_INT),
    ("Gesamtvolumen (t)", "=SUM(%s)/1000" % I_, NF_KG),
    ("Arbeitsvolumen (t)", "=SUMIF(%s,\"A\",%s)/1000" % (E_, I_), NF_KG),
    ("Volumen je Einheit (kg)",
     "=IFERROR(SUMIF(%s,\"A\",%s)/COUNT(Einheiten!$I$%d:$I$%d),\"\")"
     % (E_, I_, EINH_FIRST, EINH_LAST), NF_INT),
    ("Schwerster Satz (kg)",
     "=SUMPRODUCT(MAX((%s=\"A\")*(%s<>\"\")*%s))" % (E_, F_, F_), NF_KG),
    ("Bester e1RM (kg)",
     "=MAX(Rekorde!$H$%d:$H$%d)" % (REK_FIRST, REK_LAST), NF_KG),
    ("Übungen im Plan",
     "=COUNTA(%s!$A$%d:$A$%d)" % (UEB, UEB_FIRST, UEB_LAST), NF_INT),
]
r0 = 4
for n, (lab, formel, nf) in enumerate(kacheln):
    br = r0 + (n // 3) * 3
    bc = 2 + (n % 3) * 3
    wsd.merge_cells(start_row=br, start_column=bc, end_row=br,
                    end_column=bc + 1)
    c = wsd.cell(br, bc, lab)
    c.font = Font(name=FONT, size=9, bold=True, color="FFFFFF")
    c.fill, c.alignment = FILL_HEAD, L_IND
    wsd.cell(br, bc + 1).fill = FILL_HEAD
    wsd.row_dimensions[br].height = 16
    wsd.merge_cells(start_row=br + 1, start_column=bc, end_row=br + 1,
                    end_column=bc + 1)
    c = wsd.cell(br + 1, bc, formel)
    c.font, c.number_format, c.fill = F_KPI, nf, FILL_CALC
    c.alignment = Alignment(horizontal="center", vertical="center")
    wsd.cell(br + 1, bc + 1).fill = FILL_CALC
    for col in (bc, bc + 1):
        wsd.cell(br, col).border = B_ALL
        wsd.cell(br + 1, col).border = B_ALL
    wsd.row_dimensions[br + 1].height = 30

chart_top = r0 + 9
abschnitt(wsd, chart_top, 2, 10, "Verlauf und Vergleich")


def balken(titel, ref_ws, spalten, kopfzeile_nr, erste, letzte, kat_ws,
           kat_col, kat_first, kat_last, typ="bar", legende=False):
    ch = BarChart()
    ch.type, ch.style, ch.title = typ, 10, titel
    ch.gapWidth = 60
    for col in spalten:
        ch.add_data(Reference(ref_ws, min_col=col, min_row=kopfzeile_nr,
                              max_row=letzte), titles_from_data=True)
    ch.set_categories(Reference(kat_ws, min_col=kat_col, min_row=kat_first,
                                max_row=kat_last))
    ch.y_axis.scaling.min = 0
    # Breite so gewaehlt, dass zwei Diagramme nebeneinander in den
    # Druckbereich A:J passen und beim Skalieren nicht abgeschnitten werden.
    ch.height, ch.width = 9.4, 9.8
    if legende:
        ch.legend.position = "b"
    else:
        ch.legend = None
    return ch


ch1 = balken("Arbeitsvolumen je Einheit (kg)", wse, [9], 3, EINH_FIRST,
             EINH_LAST, wse, 1, EINH_FIRST, EINH_LAST, typ="col")
ch1.x_axis.title = "Einheit"
wsd.add_chart(ch1, "B%d" % (chart_top + 1))

EX_LAST = REK_FIRST + len(UEBUNGEN) - 1
ch2 = balken("Top-Gewicht: zuletzt vs. Bestwert (kg)", wsr,
             [12, 6], 3, REK_FIRST, EX_LAST, wsr, 1, REK_FIRST, EX_LAST,
             legende=True)
wsd.add_chart(ch2, "F%d" % (chart_top + 1))

chart2_top = chart_top + 20
ch3 = balken("Gesamtvolumen je Übung (kg)", wsr, [5], 3, REK_FIRST, EX_LAST,
             wsr, 1, REK_FIRST, EX_LAST)
wsd.add_chart(ch3, "B%d" % chart2_top)

ch4 = balken("Bester e1RM je Übung (kg)", wsr, [8], 3, REK_FIRST, EX_LAST,
             wsr, 1, REK_FIRST, EX_LAST)
wsd.add_chart(ch4, "F%d" % chart2_top)

ende = chart2_top + 20
wsd.cell(ende, 2, "Noch nicht trainierte Einheiten und Übungen erscheinen in "
                  "den Diagrammen ohne Balken.").font = F_SMALL
druck(wsd, "A1:J%d" % ende)

# --------------------------------------------------------------------------
# Blattreihenfolge und Speichern
# --------------------------------------------------------------------------
ORDER = ["Start", "Dashboard", "Einheiten", "Log", "Auswertung",
         "Progression", "Rekorde", "Trainingsblatt", "Übungen"]
wb._sheets = [wb[n] for n in ORDER]
wb.active = 0
for s in wb.worksheets:
    s.sheet_view.tabSelected = (s.title == "Start")

wb.save("GymLogbuch_Beine.xlsx")
print("geschrieben: GymLogbuch_Beine.xlsx  (%d Blätter)" % len(wb.worksheets))
