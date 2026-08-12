#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout-Nacharbeit: behebt die 10 Befunde der Layoutpruefung —
zu lange Texte kuerzen, zu niedrige Zeilen anheben. Keine Zahl und
keine Rechenlogik aendert sich.
"""
import openpyxl
from ausbau_util import DATEI

wb = openpyxl.load_workbook(DATEI)
ceo = wb['CEO Report']
dash = wb['Dashboard']
pdf = wb['📑 Executive PDF']
diag = wb['📊 Diagramme']
d = wb['📋 Definitionen & Klärung']

# 1) Infozeile A8 (CEO + Dashboard): «Modell: Blatt «⚖️ Wahrscheinlichkeit»»
#    kuerzen, damit die Zeile mit dem brutto/bereinigt-Zusatz in den
#    Verbund passt.
ALT = 'Modell: Blatt «⚖️ Wahrscheinlichkeit»'
NEU = 'Modell: ⚖️'
for blatt in (ceo, dash):
    f = blatt['A8'].value
    assert ALT in f, f'{blatt.title}!A8 ohne Modell-Hinweis: {f[-80:]}'
    blatt['A8'] = f.replace(ALT, NEU)

# 2) Zu lange Labels im CEO Report kuerzen (Inhalt bleibt eindeutig).
assert ceo['A216'].value.startswith('davon offene Offerten')
ceo['A216'] = 'davon offene Offerten (Faktoren 0 – 0.9)'
assert ceo['A220'].value.startswith('WON gemeldet')
ceo['A220'] = 'WON gemeldet (brutto wie erfasst)'
assert ceo['A222'].value.startswith('davon belegt')
ceo['A222'] = 'davon belegt (PO-Nr. + Datum + Einstand)'
assert ceo['E263'].value == 'Gewichtet CHF'
ceo['E263'] = 'Gewichtet'

# 3) Zeilenhoehen anheben, wo umgebrochener Text zwei Zeilen braucht.
ceo.row_dimensions[254].height = 25.5      # Kopf «WON-Volumen CHF»
pdf.row_dimensions[41].height = 26         # offener Punkt mit langem Label
diag.row_dimensions[95].height = 17.25     # Titelzeile Startmonat-Diagramm
d['F81'] = 'Kurzstatus'                    # statt «Kurzstatus (Spalte BB)»

wb.save(DATEI)
print('Layout-Nacharbeit geschrieben.')
