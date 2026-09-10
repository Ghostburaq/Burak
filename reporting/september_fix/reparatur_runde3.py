#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runde 3 — damit es nicht wieder passiert.

C1  Excel rechnet beim Oeffnen ALLES neu (fullCalcOnLoad): egal in
    welchem Zustand die Datei gespeichert wurde, beim Oeffnen stimmen
    alle Verknuepfungen sofort.
C2  Leitplanken-Blattschutz OHNE Passwort:
    - «MiT Strom Pipeline»: alle Eingabespalten (A–F, H–P, R–X, AA–AG)
      bleiben frei beschreibbar; die Formelspalten G, Q, Y, Z, AH und
      die versteckten Hilfsspalten AI–BC sind gesperrt. Spalten/Zeilen
      einfuegen oder loeschen ist gesperrt — genau das hat die Mappe
      zerlegt. Neue Deals kommen in die naechste freie Zeile
      (vorbereitet bis Zeile 860); der AutoFilter bleibt nutzbar.
    - Berichtsblaetter (Dashboard, CEO, Report, ExecPDF, Diagramme,
      ⚖️, Herleitung, _data): komplett gesperrt — sie sind reine
      Ausgabe.
    - Definitionen: gesperrt bis auf die gelben Stellschrauben C41:C43.
    Der Schutz traegt KEIN Passwort: «Überprüfen → Blattschutz
    aufheben» genuegt, wenn ein struktureller Eingriff wirklich
    gewollt ist.
C3  Leeres <workbookProtection/>-Element (LibreOffice-Artefakt)
    entfernen, falls vorhanden (auf ZIP-Ebene in Runde 4).
"""
import openpyxl
from openpyxl.worksheet.protection import SheetProtection
from openpyxl.styles import Protection
from openpyxl.utils import column_index_from_string, get_column_letter

F = 'BURAK_MASTER_FIX.xlsx'
wb = openpyxl.load_workbook(F)

# ---------------------------------------------------------------- C1
wb.calculation.fullCalcOnLoad = True

# ---------------------------------------------------------------- C2
def schutz(ws, autofilter_frei=False):
    ws.protection = SheetProtection(
        sheet=True, password=None,
        selectLockedCells=False, selectUnlockedCells=False,
        formatCells=False, formatColumns=False, formatRows=False,
        insertColumns=True, insertRows=True, insertHyperlinks=True,
        deleteColumns=True, deleteRows=True,
        sort=True, autoFilter=not autofilter_frei,
        pivotTables=True, objects=True, scenarios=True)

p = wb['MiT Strom Pipeline']
FREI = [c for c in range(1, column_index_from_string('AG') + 1)
        if get_column_letter(c) not in ('G', 'Q', 'Y', 'Z', 'AH')]
entsperrt = 0
for r in range(6, 861):
    for c in FREI:
        z = p.cell(row=r, column=c)
        z.protection = Protection(locked=False)
        entsperrt += 1
schutz(p, autofilter_frei=True)

for name in ('Dashboard', 'CEO Report', '📄 Report', '📑 Executive PDF',
             '📊 Diagramme', '⚖️ Wahrscheinlichkeit',
             '🔍 Herleitung & Formeln', '_data'):
    schutz(wb[name], autofilter_frei=(name in ('Dashboard', 'CEO Report')))

d = wb['📋 Definitionen & Klärung']
for koord in ('C41', 'C42', 'C43'):
    d[koord].protection = Protection(locked=False)
schutz(d)

wb.save(F)
print(f'Runde 3: fullCalcOnLoad gesetzt, Leitplanken-Schutz auf allen '
      f'Blättern (ohne Passwort), {entsperrt} Eingabezellen frei.')
