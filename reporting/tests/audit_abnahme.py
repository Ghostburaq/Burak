#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H) Abnahmepruefung der Umstellung.

Prueft genau das, was in dieser Runde verlangt war - unabhaengig von den
uebrigen Pruefungen und mit eigenen Rechenwegen:

  1. Projektstart und Projektende sind echte Datumsfelder, kein Text.
  2. Die Dauer rechnet sich aus dem Zeitraum, sonst bleibt der erfasste Wert.
  3. Die Marge ist aus allen Berichten verschwunden.
  4. Keine leeren Spalten und keine Luecken in den Hilfsspalten.
  5. Die Summen der Berichte stimmen mit der Summe der Pipeline-Zeilen ueberein.
  6. Gewonnene Auftraege stehen auf 100 %, sonst niemand.
  7. Keine Fehlerwerte.
"""
import openpyxl
import sys
import datetime
from openpyxl.utils import get_column_letter, range_boundaries

F = sys.argv[1] if len(sys.argv) > 1 else 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
PIPE = 'MiT Strom Pipeline'
LAST = 860
AKTIV = {'WON', 'offered', 'to be offered', 'on hold',
         'follow-up', 'Evaluation', 'In evaluation', 'tbd'}
FEHLERWERTE = ('#DIV/0!', '#N/A', '#NAME?', '#NULL!', '#NUM!', '#REF!', '#VALUE!')

wb = openpyxl.load_workbook(F)
V = openpyxl.load_workbook(F, data_only=True)
p, vp = wb[PIPE], V[PIPE]
bad = []
geprueft = 0


def note(art, text):
    bad.append(f'[{art}] {text}')


def zahl(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


zeilen = [r for r in range(6, LAST + 1) if vp[f'B{r}'].value not in (None, '')]

# ---------------------------------------------------------- 1) Datumsfelder
for co, titel in (('O', 'Projektstart'), ('P', 'Projektende')):
    if p[f'{co}5'].value != titel:
        note('SPALTE', f'{co}5 heisst {p[f"{co}5"].value!r} statt «{titel}»')
    geprueft += 1
    for r in zeilen:
        c, v = p[f'{co}{r}'], vp[f'{co}{r}'].value
        geprueft += 1
        if v is None:
            continue
        if not isinstance(v, (datetime.datetime, datetime.date)):
            note('DATUM', f'{co}{r} ist kein Datum, sondern {type(v).__name__}: {v!r}')
        fmt = (c.number_format or '').replace('\\', '').upper()
        if 'YYYY' not in fmt and 'JJJJ' not in fmt:
            note('DATUM', f'{co}{r} hat kein Datumsformat: {c.number_format!r}')

pruefungen = {str(dv.sqref): dv.type for dv in p.data_validations.dataValidation}
if not any(t == 'date' and 'O6' in bereich for bereich, t in pruefungen.items()):
    note('DATUM', 'Für O/P fehlt die Datumsprüfung (Gültigkeit)')
geprueft += 1

# ------------------------------------------------------------- 2) Dauer
quelle = openpyxl.load_workbook('original.xlsx', data_only=True)[PIPE]
for r in zeilen:
    von, bis, dauer = vp[f'O{r}'].value, vp[f'P{r}'].value, vp[f'G{r}'].value
    geprueft += 1
    if isinstance(von, datetime.datetime) and isinstance(bis, datetime.datetime) and bis >= von:
        soll = (bis - von).days + 1
        if dauer != soll:
            note('DAUER', f'G{r} erwartet {soll} Tage, ist {dauer!r}')
    else:
        alt = quelle[f'G{r}'].value
        soll = None if alt is None else alt
        if (dauer if dauer != '' else None) != soll:
            note('DAUER', f'G{r} müsste den erfassten Wert {soll!r} zeigen, ist {dauer!r}')

# -------------------------------------------------------------- 3) Marge
BERICHTE = ['📑 Executive PDF', '📄 Report', 'CEO Report', 'Dashboard', '📊 Diagramme']
for blatt in BERICHTE:
    ws, vs = wb[blatt], V[blatt]
    for row in ws.iter_rows():
        for c in row:
            w = vs[c.coordinate].value
            for text in (c.value, w):
                if isinstance(text, str) and ('marge' in text.lower()
                                              or 'deckungsbeitrag' in text.lower()):
                    note('MARGE', f'{blatt}!{c.coordinate}: {text[:70]!r}')
            geprueft += 1
for co in ('O', 'P'):
    for r in zeilen:
        if isinstance(p[f'{co}{r}'].value, str) and p[f'{co}{r}'].value.startswith('='):
            note('MARGE', f'{co}{r} enthält noch eine Formel — die Spalte ist ein Eingabefeld')

# --------------------------------------- 4) Leere Spalten und Hilfsspalten
for ws in wb.worksheets:
    if ws.sheet_state != 'visible' or not ws.print_area:
        continue
    pa = ws.print_area[0] if isinstance(ws.print_area, list) else ws.print_area
    g = range_boundaries(pa.split('!')[-1])
    vs = V[ws.title]
    # Eine Spalte gilt als benutzt, wenn sie Werte traegt, von einem
    # Verbundbereich ueberdeckt wird oder unter einem Diagramm liegt.
    belegt_durch_verbund = set()
    for m in ws.merged_cells.ranges:
        if V[ws.title].cell(row=m.min_row, column=m.min_col).value not in (None, ''):
            belegt_durch_verbund.update(range(m.min_col, m.max_col + 1))
    belegt_durch_bild = set()
    for ch in getattr(ws, '_charts', []):
        a = getattr(ch, 'anchor', None)
        if a is not None and hasattr(a, 'to'):
            belegt_durch_bild.update(range(a._from.col + 1, a.to.col + 2))
    for ci in range(g[0], g[2] + 1):
        if ci in belegt_durch_verbund or ci in belegt_durch_bild:
            continue
        d = ws.column_dimensions.get(get_column_letter(ci))
        if d is not None and d.hidden:
            continue
        if any(vs.cell(row=r, column=ci).value not in (None, '')
               for r in range(g[1], g[3] + 1)):
            continue
        # Eine schmale Randspalte ist Gestaltung, keine Luecke.
        breite = d.width if d is not None and d.width else 8.43
        if breite > 5:
            note('LEER', f'{ws.title}: Spalte {get_column_letter(ci)} im Druckbereich '
                         f'ist vollständig leer (Breite {breite:.1f})')
        geprueft += 1

HELFER = ['_EinstandOK', '_BelegOK', '_WONbelegt', '_Zaehlt', '_Mehrfachkunde',
          '_DauerErfasst', '_MonatStart', '_ZeitraumOK', '_NettoNum',
          '_Befunde', '_KurzStatus']
for i, name in enumerate(HELFER):
    co = get_column_letter(44 + i)          # AR = 44
    if p[f'{co}5'].value != name:
        note('HILFSSPALTE', f'{co}5 erwartet «{name}», ist {p[f"{co}5"].value!r}')
    geprueft += 1
rest = get_column_letter(44 + len(HELFER))  # erste Spalte nach den Helfern
if any(p[f'{rest}{r}'].value is not None for r in range(1, LAST + 1)):
    note('HILFSSPALTE', f'Spalte {rest} müsste leer sein, enthält aber noch Werte')
geprueft += 1

# ------------------------------------------- 5) Summen Bericht ↔ Pipeline
def summe(stati):
    return sum(vp[f'I{r}'].value for r in zeilen
               if vp[f'R{r}'].value in stati and zahl(vp[f'I{r}'].value))


def anzahl(stati):
    return sum(1 for r in zeilen if vp[f'R{r}'].value in stati)


OFF = {'offered', 'to be offered', 'on hold'}
OPP = {'follow-up', 'Evaluation', 'In evaluation', 'tbd'}
gew = sum(vp[f'Q{r}'].value for r in zeilen
          if vp[f'R{r}'].value in AKTIV and zahl(vp[f'Q{r}'].value))

SUMMEN = [
    ('Dashboard!A6 WON', V['Dashboard']['A6'].value, summe({'WON'})),
    ('Dashboard!D6 Offerte', V['Dashboard']['D6'].value, summe(OFF)),
    ('Dashboard!G6 Opportunität', V['Dashboard']['G6'].value, summe(OPP)),
    ('Dashboard!I6 Gesamt', V['Dashboard']['I6'].value, summe(AKTIV)),
    ('CEO Report!A6 WON', V['CEO Report']['A6'].value, summe({'WON'})),
    ('Report!B7 WON', V['📄 Report']['B7'].value, summe({'WON'})),
    ('Report!B10 Total', V['📄 Report']['B10'].value, summe(AKTIV)),
    ('Report!B11 gewichtet', V['📄 Report']['B11'].value, gew),
    ('ExecPDF!B6 WON', V['📑 Executive PDF']['B6'].value, summe({'WON'})),
    ('Pipeline!C4 WON', vp['C4'].value, summe({'WON'})),
    ('Pipeline!I4 Anzahl aktiv', vp['I4'].value, anzahl(AKTIV)),
    ('Pipeline!U4 gewichtet', vp['U4'].value, gew),
]
W = V['⚖️ Wahrscheinlichkeit']
tot = next(r for r in range(1, 40) if W[f'A{r}'].value == 'TOTAL aktiv')
SUMMEN += [
    ('Bandtabelle Umsatz', W[f'F{tot}'].value, summe(AKTIV)),
    ('Bandtabelle gewichtet', W[f'G{tot}'].value, gew),
    ('Bandtabelle Anzahl', W[f'E{tot}'].value, anzahl(AKTIV)),
]
for name, ist, soll in SUMMEN:
    geprueft += 1
    if abs((ist or 0) - (soll or 0)) > 0.01:
        note('SUMME', f'{name}: Bericht {ist!r}, Summe der Pipeline-Zeilen {soll!r}')

# Monatsauswertung: die Totalzeile muss die aktive Pipeline treffen
for blatt in ('Dashboard', 'CEO Report'):
    vs = V[blatt]
    zeile = next((r for r in range(200, 260)
                  if str(vs[f'A{r}'].value or '').startswith('TOTAL aktive Pipeline')), None)
    if zeile is None:
        note('MONAT', f'{blatt}: Totalzeile der Monatsauswertung fehlt')
        continue
    geprueft += 1
    if abs((vs[f'F{zeile}'].value or 0) - summe(AKTIV)) > 0.01:
        note('MONAT', f'{blatt}!F{zeile}: {vs[f"F{zeile}"].value!r} statt {summe(AKTIV)!r}')
    if (vs[f'E{zeile}'].value or 0) != anzahl(AKTIV):
        note('MONAT', f'{blatt}!E{zeile}: {vs[f"E{zeile}"].value!r} statt {anzahl(AKTIV)!r}')

# -------------------------------------------------------- 6) 100-%-Regel
for r in zeilen:
    st, s_ = vp[f'R{r}'].value, vp[f'S{r}'].value
    geprueft += 1
    if st == 'WON' and s_ != 1:
        note('HUNDERT', f'Zeile {r}: WON, aber S={s_!r} statt 100 %')
    if s_ == 1 and st != 'WON':
        note('HUNDERT', f'Zeile {r}: 100 %, aber Status {st!r} statt WON')
    if st == 'WON' and zahl(vp[f'I{r}'].value):
        if abs((vp[f'Q{r}'].value or 0) - vp[f'I{r}'].value) > 0.01:
            note('HUNDERT', f'Zeile {r}: Gew.Wert {vp[f"Q{r}"].value!r} '
                            f'statt vollem Volumen {vp[f"I{r}"].value!r}')

# ---------------------------------------------------------- 7) Fehlerwerte
for ws in V.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith(FEHLERWERTE):
                note('FEHLERWERT', f'{ws.title}!{c.coordinate}: {c.value}')

print(f'Abnahmeprüfungen : {geprueft}')
print(f'Befunde          : {len(bad)}')
if bad:
    print()
    for b in bad[:60]:
        print('  ', b)
    if len(bad) > 60:
        print(f'   ... und {len(bad) - 60} weitere')
else:
    print()
    print('Abnahme in Ordnung — Datumsfelder echt, Dauer gerechnet, Marge überall raus,')
    print('keine leeren Spalten, Berichtssummen gleich der Summe der Pipeline-Zeilen,')
    print('gewonnene Aufträge auf 100 %, keine Fehlerwerte.')
sys.exit(1 if bad else 0)
