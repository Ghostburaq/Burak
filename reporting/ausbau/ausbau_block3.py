#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLOCK 3 — Zeitraum nutzbar machen.

3.1  Erfassungsliste im Definitionsblatt (neuer Abschnitt 8): alle aktiven
     Deals ohne erfassten Projektzeitraum (AY = 0), mit Kunde, Status und
     Volumen. Live gerechnet ueber die neue versteckte Hilfsspalte BC
     (_ZeitOffenNr) — die Liste schrumpft automatisch, sobald in den
     Spalten O und P Daten nachgetragen werden.
3.2  Der CEO Report traegt die Tabelle «Volumen nach Startmonat» bereits
     (Abschnitt 6, Zeilen 232–249, auf Hilfsspalte AX). Neu: Hinweiszeile
     «Zeiträume noch nicht erfasst: X von Y aktiven Deals offen» direkt
     unter der Tabelle — sie verschwindet automatisch, sobald alle
     Zeitraeume erfasst sind.
3.3  Pruefen (nicht aendern): Ende-vor-Start wird im Kurzstatus BB als
     «⚠ Ende vor Start» gemeldet.
"""
import copy
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.formatting.rule import FormulaRule
from ausbau_util import DATEI, merge, sp

wb = openpyxl.load_workbook(DATEI)
pipe = wb['MiT Strom Pipeline']
ceo = wb['CEO Report']
d = wb['📋 Definitionen & Klärung']

# ---------------------------------------------------------------- 3.3 pruefen
bb = pipe['BB6'].value
assert isinstance(bb, str) and 'Ende vor Start' in bb, \
    f'3.3: Kurzstatus BB meldet Ende-vor-Start nicht: {bb!r}'
assert 'P6<O6' in bb.replace(' ', ''), '3.3: BB prueft nicht P<O'

# ------------------------------------------- Hilfsspalte BC (_ZeitOffenNr)
assert pipe['BC5'].value is None and pipe['BC6'].value is None
pipe['BC5'] = '_ZeitOffenNr'
pipe['BC5']._style = copy.copy(pipe['AK5']._style)
for r in range(6, 861):
    pipe[f'BC{r}'] = (f'=IF(AND(AP{r}=1,AY{r}=0),'
                      f'SUMPRODUCT($AP$6:AP{r},--($AY$6:AY{r}=0)),"")')
pipe.column_dimensions['BC'].hidden = True

# ------------------------------------------------- 3.1 Erfassungsliste (Def)
assert d['A73'].value.startswith('7️⃣'), 'Abschnitt 7 nicht an Zeile 73'
for r in range(78, 135):
    for c in range(1, 9):
        assert d.cell(row=r, column=c).value is None, f'Def {r},{c} belegt'

SLOTS = 50
ANZ_OFFEN = f'SUMPRODUCT({sp("AP")},--({sp("AY")}=0))'
ANZ_AKTIV = f'SUMPRODUCT({sp("AP")})'

t = d['A79']
t.value = '8️⃣   Erfassungsliste Projektzeitraum  —  aktive Deals ohne Start-/Enddatum'
t._style = copy.copy(d['A73']._style)
d.row_dimensions[79].height = (d.row_dimensions[73].height or 20)

z = d['B80']
z.value = ('="Noch offen: "&' + ANZ_OFFEN + '&" von "&' + ANZ_AKTIV +
           '&" aktiven Deals. Projektstart (Spalte O) und Projektende (Spalte P) '
           'in «MiT Strom Pipeline» als Datum TT.MM.JJJJ nachtragen — '
           'die Liste schrumpft automatisch."')
z.font = Font(name=d['B74'].font.name or 'Calibri', size=10, italic=True,
              color='FFB45309')
z.alignment = Alignment(horizontal='left', vertical='center')
merge(d, 'B80:H80')
d.row_dimensions[80].height = 15

for koord, text in (('B81', 'Kunde / Unternehmen'), ('C81', 'Status'),
                    ('D81', 'Volumen CHF'), ('F81', 'Kurzstatus (Spalte BB)')):
    z = d[koord]
    z.value = text
    z._style = copy.copy(d['B16']._style)
d.row_dimensions[81].height = (d.row_dimensions[16].height or 15)

BC = sp('BC')
for i in range(SLOTS):
    r = 82 + i
    k = f'ROW()-81'
    treffer = f'MATCH({k},{BC},0)'
    d[f'B{r}'] = f'=IFERROR(INDEX({sp("B")},{treffer}),"")'
    d[f'C{r}'] = f'=IFERROR(INDEX({sp("R")},{treffer}),"")'
    d[f'D{r}'] = f'=IF($B{r}="","",INDEX({sp("AL")},{treffer}))'
    d[f'F{r}'] = f'=IFERROR(INDEX({sp("BB")},{treffer}),"")'
    for col, harmon, fmt in (('B', 'left', 'General'), ('C', 'left', 'General'),
                             ('D', 'right', '#,##0'), ('F', 'left', 'General')):
        z = d[f'{col}{r}']
        z.font = Font(name='Calibri', size=10)
        z.number_format = fmt
        z.alignment = Alignment(horizontal=harmon, vertical='center')
    d.row_dimensions[r].height = 14.25

d.print_area = "'📋 Definitionen & Klärung'!$A$1:$H$132"

# --------------------------------------------- 3.2 Hinweiszeile (CEO, 250)
assert ceo['A232'].value.startswith('📅') and ceo['A249'].value == 'TOTAL aktive Pipeline'
assert ceo['A250'].value is None and ceo['A251'].value is None

z = ceo['A250']
z.value = ('=IF(' + ANZ_OFFEN + '=0,"",'
           '"⚠  Zeiträume noch nicht erfasst: "&' + ANZ_OFFEN + '&" von "&' +
           ANZ_AKTIV + '&" aktiven Deals offen — die Monatstabelle füllt sich, '
           'sobald Projektstart und Projektende in der Pipeline stehen '
           '(Erfassungsliste: Blatt «📋 Definitionen & Klärung», Abschnitt 8).")')
z.font = Font(name='Arial', size=10, bold=True, color='FFB45309')
z.alignment = Alignment(horizontal='left', vertical='center')
merge(ceo, 'A250:N250')
ceo.row_dimensions[250].height = 15.75

wb.save(DATEI)
print('Block 3 geschrieben: Hilfsspalte BC, Erfassungsliste (Definitionen 79–131), '
      'Hinweiszeile Startmonat (CEO 250), BB-Prüfung bestanden.')
