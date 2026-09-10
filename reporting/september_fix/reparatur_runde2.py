#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reparatur Runde 2 — Folgeschaeden der geloeschten Spalte «Wahr. % bisher»
und der Zeilenoperationen in der Pipeline.

B1  Zeile 80 (per Zeilen-Einfuegen entstanden) hat keine einzige Formel:
    alle Formelspalten (G, Q, Y, Z, AH, AI–BC) aus dem Muster der
    Nachbarzeilen neu setzen. Eingabewerte der Zeile bleiben unberuehrt.
B2  Dauer von Hand in G getippt (neue Deals, Zeilen 71–80): Handwert in
    die Handwert-Spalte AV (_DauerErfasst) uebernehmen, G-Formel zurueck —
    die Dauer bleibt sichtbar und rechnet automatisch, sobald
    Projektstart/-ende (O/P) erfasst werden.
B3  Umschluesselungs-Protokoll auf «⚖️» (E52:G58, Totale 59, E62:E64)
    braucht die geloeschte Spalte: einfrieren («—») mit klarem Hinweis.
    Die Live-Kontrolle «aktive Deals ausserhalb der Skala» (E61) bleibt.
B4  Definitionen G12 neu (ohne Bezug auf die geloeschte Spalte) und
    Text C12 angepasst.
B5  Spaltennennungen in Erlaeuterungstexten an die neue Spaltenlage
    angepasst (alles ab AI ist eine Position nach links gerueckt).
"""
import copy
import re
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

F = 'BURAK_MASTER_FIX.xlsx'
P = "'MiT Strom Pipeline'!"
wb = openpyxl.load_workbook(F)
p = wb['MiT Strom Pipeline']
w = wb['⚖️ Wahrscheinlichkeit']
d = wb['📋 Definitionen & Klärung']
ceo = wb['CEO Report']
h = wb['🔍 Herleitung & Formeln']

# ---------------------------------------------------------- B2 vor B1:
# Dauer-Handwerte sichern, bevor G-Formeln gesetzt werden.
uebernommen = []
for r in range(6, 861):
    g = p[f'G{r}'].value
    if g is None or (isinstance(g, str) and g.startswith('=')):
        continue
    # Handwert: in AV uebernehmen (nur wenn dort nichts steht).
    if p[f'AV{r}'].value in (None, ''):
        p[f'AV{r}'] = g
    uebernommen.append((r, g))

# ---------------------------------------------------------- B1: Zeile 80
# (und B2: G-Formeln) — Muster aus Zeile 20, Zeilenbezuege umschreiben.
FORMELSPALTEN = ['G', 'Q', 'Y', 'Z', 'AH'] + \
                [get_column_letter(c) for c in range(35, 56) if get_column_letter(c) != 'AV']
BEZUG_20 = re.compile(r'(?<=[A-Z$])20\b')

def formel_fuer(col, r):
    m = p[f'{col}20'].value
    assert isinstance(m, str) and m.startswith('='), f'{col}20 ist keine Formel'
    return BEZUG_20.sub(str(r), m)

gesetzt = 0
for col in FORMELSPALTEN:
    for r in range(6, 861):
        v = p[f'{col}{r}'].value
        if isinstance(v, str) and v.startswith('='):
            continue
        neu = formel_fuer(col, r)
        z = p[f'{col}{r}']
        z.value = neu
        z._style = copy.copy(p[f'{col}20']._style)
        gesetzt += 1

# ---------------------------------------------------------- B3: ⚖️ einfrieren
GRAU = Font(name='Calibri', size=10, color='FF888888')
for r in range(52, 60):
    for col in ('E', 'F', 'G'):
        z = w[f'{col}{r}']
        z.value = '—'
        z.font = GRAU
        z.alignment = Alignment(horizontal='center', vertical='center')
        z.number_format = 'General'
assert w['H59'].value and 'G59' in str(w['H59'].value)
w['H59'] = None
for koord in ('E62', 'E63', 'E64'):
    z = w[koord]
    z.value = '—'
    z.font = GRAU
    z.alignment = Alignment(horizontal='center', vertical='center')
    z.number_format = 'General'

assert w['A60'].value is None
z = w['A60']
z.value = ('ℹ️  Protokoll eingefroren: Die Spalte «Wahr. % bisher» wurde am '
           '10.09.2026 aus der Pipeline entfernt — die Zählung je '
           'Umschlüsselungspaar ist seither nicht mehr live rechenbar. '
           'Massgeblich bleibt die Kontrolle unten: aktive Deals ausserhalb '
           'der Skala müssen 0 sein.')
z.font = Font(name='Calibri', size=9, italic=True, color='FFB45309')
z.alignment = Alignment(horizontal='left', vertical='center')
w.row_dimensions[60].height = 13.5

# ---------------------------------------------------------- B4: Definitionen
alt = d['G12'].value
assert '#REF!' in alt
d['G12'] = ('="Noch ausserhalb der Skala: "&SUMPRODUCT(' + P + '$AO$6:$AO$860,'
            '--(' + P + '$AP$6:$AP$860=0))&"  ·  Umschlüsselung abgeschlossen '
            '(die Protokollspalte «Wahr. % bisher» wurde entfernt)  ·  '
            'gewichtete Pipeline: "&TEXT(\'⚖️ Wahrscheinlichkeit\'!$G$22,'
            '"#,##0")&" CHF"')

d['C12'] = ('Alle Zeilen sind auf die Skala 0/10/30/60/90/100 % umgeschlüsselt. '
            'Die Protokollspalte mit den Ursprungswerten («Wahr. % bisher») '
            'wurde im September 2026 aus der Pipeline entfernt; die '
            'Vergleichszählung auf dem Blatt «⚖️ Wahrscheinlichkeit» ist '
            'seither eingefroren. Ob ein aktiver Deal ausserhalb der Skala '
            'steht, wird weiterhin live geprüft (rechts).')

# ---------------------------------------------------------- B5: Textstellen
ERSATZ = [
    (ceo, 'F222', 'Hilfsspalte AT', 'Hilfsspalte AS'),
    (d, 'C50', 'Spalte AW', 'Spalte AV'),
    (d, 'C52', 'Spalte AX', 'Spalte AW'),
    (h, 'D65', 'Spalte AZ', 'Spalte AY'),
    (h, 'D66', 'Spalte AT', 'Spalte AS'),
    (h, 'D67', 'Spalte AP', 'Spalte AO'),
    (h, 'D68', 'Spalte AU', 'Spalte AT'),
    (h, 'D71', 'Spalte AY', 'Spalte AX'),
    (h, 'D72', 'Spalte AX', 'Spalte AW'),
    (h, 'D73', 'Spalte AK', 'Spalte AJ'),
]
for blatt, koord, von, nach in ERSATZ:
    t = blatt[koord].value
    assert isinstance(t, str) and von in t, f'{blatt.title}!{koord}: {t!r}'
    blatt[koord] = t.replace(von, nach)

# Scan: weitere Alt-Spaltennennungen (AI..BD) in Doku-Texten melden.
TOKEN = re.compile(r'\b(A[I-Z]|B[A-D])\b')
print('--- Verbleibende Nennungen AI..BD in Texten (bitte pruefen): ---')
for ws in (h, d, ceo, wb['Dashboard'], wb['📑 Executive PDF']):
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and not c.value.startswith('='):
                treffer = TOKEN.findall(c.value)
                if treffer:
                    print(f'  {ws.title}!{c.coordinate}: {sorted(set(treffer))} '
                          f'| {c.value[:70]}')

wb.save(F)
print(f'\nRunde 2: {gesetzt} Formeln gesetzt (inkl. Zeile 80), '
      f'{len(uebernommen)} Dauer-Handwerte nach AV übernommen: {uebernommen}')
