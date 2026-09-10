#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout-Nacharbeit auf der reparierten Nutzerdatei.

1. Herleitungsblatt: Die nachgetragene Hilfsspalten-Doku (BB/BC) hatte
   den Abschnittstitel «7️⃣» ueberlagert — zwei Zeilen einfuegen, Doku
   sauber in 131/132, Titel rueckt nach 134.
2. Zeilenhoehen: die neuen, laengeren Texte des Nutzers brauchen mehr
   Platz — alle «ZEILE ZU NIEDRIG»-Befunde der Layoutpruefung beheben.
3. Drei Einzelfaelle: Dashboard-Infozeile kuerzen, ⚖️-Hinweis kuerzen,
   ⚖️-Spalte B verbreitern, Datumsformat in Pipeline!W72/W73.
"""
import copy
import re
import subprocess
import sys
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

F = 'BURAK_MASTER_FIX.xlsx'
wb = openpyxl.load_workbook(F)
h = wb['🔍 Herleitung & Formeln']
p = wb['MiT Strom Pipeline']
dash = wb['Dashboard']
w = wb['⚖️ Wahrscheinlichkeit']

# ------------------------------------------------ 1) Herleitung entflechten
assert str(h['A132'].value).startswith('7️⃣')
bc_doku = [h['B132'].value, h['C132'].value, h['F132'].value]
assert bc_doku[0] == 'BC  ·  _OffertSort'
for m in [str(m) for m in h.merged_cells.ranges if m.min_row == 132]:
    h.unmerge_cells(m)
for col in ('B', 'C', 'F'):
    h[f'{col}132'] = None

h.insert_rows(132, 2)
assert str(h['A134'].value).startswith('7️⃣'), h['A134'].value

# BC-Doku in die neue Zeile 132 (Stil/Merges wie Zeile 131)
m131 = [m for m in h.merged_cells.ranges if m.min_row == 131 and m.max_row == 131]
for m in m131:
    von, bis = get_column_letter(m.min_col), get_column_letter(m.max_col)
    h.merge_cells(f'{von}132:{bis}132')
for col, wert in (('B', bc_doku[0]), ('C', bc_doku[1]), ('F', bc_doku[2])):
    z = h[f'{col}132']
    z.value = wert
    z._style = copy.copy(h[f'{col}131']._style)
h.row_dimensions[132].height = h.row_dimensions[131].height
h.row_dimensions[133].height = 6
h.print_area = "'🔍 Herleitung & Formeln'!$A$1:$F$167"

# ------------------------------------------------ 2) Zeilenhoehen aus Befunden
r = subprocess.run([sys.executable, 'audit_layout.py', F],
                   capture_output=True, text=True)
MUSTER = re.compile(r'\[ZEILE ZU NIEDRIG\s*\] ([^!]+)!([A-Z]+)(\d+): \d+ Zeile\(n\) '
                    r'brauchen (\d+) pt')
gesetzt = 0
for blatt, col, zeile, noetig in MUSTER.findall(r.stdout):
    ws = wb[blatt.strip()]
    zeile, noetig = int(zeile), float(noetig)
    if (ws.row_dimensions[zeile].height or 0) < noetig + 1:
        ws.row_dimensions[zeile].height = noetig + 1
        gesetzt += 1

# ------------------------------------------------ 3) Einzelfaelle
a8 = dash['A8'].value
ALT = 'Gewichtete Pipeline (Aggreko-Faktoren 0 / 30 / 50 / 90 %):'
assert ALT in a8
dash['A8'] = a8.replace(ALT, 'Gewichtete Pipeline (Faktoren 0/30/50/90 %):')

w['A60'] = ('ℹ️  Protokoll eingefroren — Spalte «Wahr. % bisher» wurde entfernt. '
            'Massgeblich: Kontrolle unten (ausserhalb Skala = 0).')
w.column_dimensions['B'].width = 19.5

for koord in ('W72', 'W73'):
    z = p[koord]
    if hasattr(z.value, 'year'):
        z.number_format = 'DD.MM.YYYY'

wb.save(F)
print(f'Layout-Nacharbeit: Herleitung entflochten, {gesetzt} Zeilenhöhen angehoben, '
      f'3 Einzelfälle behoben.')
