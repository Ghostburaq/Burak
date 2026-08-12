#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kernzahlen- und Regelkontrolle (K1 bis K4) — laeuft nach jedem Block.

K1  Kernzahlen exakt: 66 Datenzeilen, WON 12 / 1'428'553.13,
    aktiv 46 / 6'862'149.23, gewichtet 1'628'425.59.
K2  Keine Fehlerwerte (#BEZUG!/#WERT!/#NV/#DIV/0!/#NAME?) — data_only-Scan.
K3  Keine Ganzspaltenbezuege, kein Bereich ueber Zeile 864.
K4  Keine XVERWEIS-, FILTER-, EINDEUTIG-, SORTIEREN-, TEXTVERKETTEN-
    oder LET-Funktionen (gespeichert als XLOOKUP/_xlfn.FILTER/UNIQUE/
    SORT/SORTBY/TEXTJOIN/LET).
R1  Bandtabelle unveraendert: sechs Baender, oberstes «100 %  ·  WON»
    mit Faktor 1.0, Aggreko-Faktoren 0/0.3/0.5/0.9 darunter.
R2  Keine Marge in einem Berichtsblatt (Textscan).
"""
import re
import sys
import openpyxl

F = sys.argv[1] if len(sys.argv) > 1 else 'CH_MiT_Strom_Customer_CEO_CFO_MASTER__2_.xlsx'
fehler = []

wb = openpyxl.load_workbook(F)
V = openpyxl.load_workbook(F, data_only=True)
p = V['MiT Strom Pipeline']

# ---------------------------------------------------------------- K1
n = won_n = akt_n = 0
won = akt = gew = 0.0
for r in range(6, 865):
    if p[f'B{r}'].value in (None, ''):
        continue
    n += 1
    vol = p[f'I{r}'].value
    if not isinstance(vol, (int, float)):
        vol = p[f'AL{r}'].value or 0
    st = p[f'R{r}'].value
    fak = p[f'AJ{r}'].value or 0
    if st == 'WON':
        won_n += 1
        won += vol
    if p[f'AP{r}'].value == 1:
        akt_n += 1
        akt += vol
        gew += vol * fak

SOLL = [('Datenzeilen', n, 66), ('WON Anzahl', won_n, 12),
        ('WON CHF', round(won, 2), 1428553.13),
        ('Aktiv Anzahl', akt_n, 46), ('Aktiv CHF', round(akt, 2), 6862149.23),
        ('Gewichtet CHF', round(gew, 2), 1628425.59)]
for name, ist, soll in SOLL:
    if abs(ist - soll) > 0.005:
        fehler.append(f'K1 {name}: ist {ist}, soll {soll}')

# ---------------------------------------------------------------- K2
FEHLERWERTE = ('#REF!', '#VALUE!', '#N/A', '#DIV/0!', '#NAME?', '#NUM!', '#NULL!',
               '#BEZUG!', '#WERT!', '#NV', '#ZAHL!')
k2 = 0
for ws in V.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value in FEHLERWERTE:
                k2 += 1
                if k2 <= 8:
                    fehler.append(f'K2 {ws.title}!{c.coordinate}: {c.value}')
if k2 > 8:
    fehler.append(f'K2 ... und {k2 - 8} weitere Fehlerwerte')

# ---------------------------------------------------------------- K3 + K4
GANZSPALTE = re.compile(r"(?<![A-Z0-9_.$])\$?[A-Z]{1,3}:\$?[A-Z]{1,3}(?![A-Z0-9_(])")
BEREICH = re.compile(r"\$?[A-Z]{1,3}\$?(\d+):\$?[A-Z]{1,3}\$?(\d+)")
VERBOTEN_FN = re.compile(r"\b(XLOOKUP|_xlfn\.FILTER|UNIQUE|SORTBY|SORT|TEXTJOIN|LET)\s*\(")
k3 = k4 = 0
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            f = c.value
            if not isinstance(f, str) or not f.startswith('='):
                continue
            if GANZSPALTE.search(f):
                k3 += 1
                if k3 <= 5:
                    fehler.append(f'K3 Ganzspaltenbezug {ws.title}!{c.coordinate}: {f[:70]}')
            for m in BEREICH.finditer(f):
                if int(m.group(1)) > 864 or int(m.group(2)) > 864:
                    k3 += 1
                    if k3 <= 5:
                        fehler.append(f'K3 Bereich ueber 864 {ws.title}!{c.coordinate}: {f[:70]}')
            if VERBOTEN_FN.search(f):
                k4 += 1
                if k4 <= 5:
                    fehler.append(f'K4 verbotene Funktion {ws.title}!{c.coordinate}: {f[:70]}')

# ---------------------------------------------------------------- R1 Bandtabelle
w = wb['⚖️ Wahrscheinlichkeit']
BAND_SOLL = [('0 – 44 %', 0, 0.4499999, 0), ('45 – 59 %', 0.45, 0.5999999, 0.3),
             ('60 – 89 %', 0.6, 0.8999999, 0.5), ('90 – 99 %', 0.9, 0.9999999, 0.9),
             ('100 %  ·  WON', 1, 1, 1)]
for i, (label, von, bis, fak) in enumerate(BAND_SOLL):
    r = 17 + i
    ist = (w[f'A{r}'].value, w[f'B{r}'].value, w[f'C{r}'].value, w[f'D{r}'].value)
    if ist != (label, von, bis, fak):
        fehler.append(f'R1 Bandtabelle Zeile {r}: {ist} statt {(label, von, bis, fak)}')
if w['A22'].value != 'TOTAL aktiv':
    fehler.append('R1 Bandtabelle: Totalzeile 22 fehlt')

# --------------------------------------- D1 Diagrammdaten decken alles ab
dt = V['_data']
if dt['S2'].value is not None:      # erst nach Block 4 vorhanden
    seg = sum(v for v in (dt[f'S{r}'].value for r in range(2, 31))
              if isinstance(v, (int, float)))
    if abs(seg - akt) > 0.01:
        fehler.append(f'D1 Segment-Diagramm deckt {seg:,.2f} statt {akt:,.2f} ab')
    kant = sum(v for v in (dt[f'T{r}'].value for r in range(14, 40))
               if isinstance(v, (int, float)))
    if abs(kant - akt) > 0.01:
        fehler.append(f'D1 Kanton-Daten decken {kant:,.2f} statt {akt:,.2f} ab')
    zer = (dt['Y2'].value or 0) + (dt['Y3'].value or 0)
    if abs(zer - gew) > 0.01:
        fehler.append(f'D1 Zerlegungs-Diagramm {zer:,.2f} statt {gew:,.2f}')

# ---------------------------------------------------------------- R2 Marge
BERICHTE = ['📑 Executive PDF', '📄 Report', 'CEO Report', 'Dashboard', '📊 Diagramme']
MARGE = re.compile(r'\bMarge\b|\bDeckungsbeitrag\b|Margen[- ]?%|DB1|DB2', re.I)
ERLAUBT = re.compile(r'nicht mehr|entfernt|keine Marge|ohne Marge|nicht ausgewiesen', re.I)
for name in BERICHTE:
    for row in wb[name].iter_rows():
        for c in row:
            if isinstance(c.value, str) and MARGE.search(c.value) and not ERLAUBT.search(c.value):
                fehler.append(f'R2 Marge im Bericht {name}!{c.coordinate}: {c.value[:60]}')

print(f'K1: {n} Zeilen · WON {won_n}/{won:,.2f} · aktiv {akt_n}/{akt:,.2f} · gewichtet {gew:,.2f}')
print(f'Befunde: {len(fehler)}')
for f in fehler[:30]:
    print('  ', f)
sys.exit(1 if fehler else 0)
