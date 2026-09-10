#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verhaltenstest (Spaltenlage September, ohne «Wahr. % bisher») auf einer
Wegwerfkopie — beweist, dass jedes Blatt live folgt, egal was eingetragen
oder geaendert wird.

A  Neuer Deal in der naechsten freien Zeile (81): WON, 50'000 CHF, ZH,
   neues Segment «Testsegment».
   A1 Dashboard-WON-Kachel steigt um 50'000, Zaehler +1.
   A2 CEO-WON-Liste zeigt den neuen Kunden.
   A3 ⚖️-Bandtabelle: 100-%-Band +1 Deal.
   A4 Segment-Diagrammdaten: Wachhund zeigt «Testsegment» NICHT als Loch —
      neues Segment erscheint als Restbalken «Übrige …».
   A5 Vertragsarten «ohne Angabe» +1.
B  Zeitraum nachtragen (01.08.2026–10.08.2026) beim neuen Deal:
   B1 Dauer G = 10.  B2 Erfassungsliste schrumpft um 1.
   B3 Monatstabelle August zaehlt +1.
C  Ende vor Start: Kurzstatus (BA) meldet «⚠ Ende vor Start».
D  Status WON -> LOST beim Testdeal: alle WON-Zahlen fallen zurueck,
   Deal verschwindet aus aktiver Pipeline.
"""
import datetime
import shutil
import subprocess
import sys
import openpyxl

QUELLE = 'BURAK_MASTER_FIX.xlsx'
K = 'test_kopie.xlsx'
RECALC = '/mnt/skills/public/xlsx/scripts/recalc.py'
fehler = []


def pruef(name, bedingung, detail=''):
    print(('  ✔ ' if bedingung else '  ✘ ') + name + (f'  [{detail}]' if detail else ''))
    if not bedingung:
        fehler.append(name)


def recalc():
    subprocess.run(['pkill', '-9', '-f', 'soffice[.]bin'], capture_output=True)
    r = subprocess.run([sys.executable, RECALC, K, '520'],
                       capture_output=True, text=True)
    assert '"status": "success"' in r.stdout, (r.stdout + r.stderr)[-500:]


def lade():
    return openpyxl.load_workbook(K, data_only=True)


basis = openpyxl.load_workbook(QUELLE, data_only=True)
b_dash = basis['Dashboard']
WON0, WONN0 = b_dash['A6'].value, b_dash['A7'].value
b_def = basis['📋 Definitionen & Klärung']
LISTE0 = sum(1 for r in range(82, 132) if b_def[f'B{r}'].value not in (None, ''))
b_w = basis['⚖️ Wahrscheinlichkeit']
BAND100_0 = b_w['E21'].value

# ---------------------------------------------------------------- A
shutil.copy(QUELLE, K)
wb = openpyxl.load_workbook(K)
p = wb['MiT Strom Pipeline']
R = 81
assert p[f'B{R}'].value in (None, ''), f'Zeile {R} nicht frei'
p[f'B{R}'] = 'TESTKUNDE Verhaltenstest'
p[f'C{R}'] = 'ZH'
p[f'D{R}'] = 'Testsegment'
p[f'I{R}'] = 50000
p[f'R{R}'] = 'WON'
p[f'S{R}'] = 1
wb.save(K)
recalc()
Vt = lade()
dash, ceo, w, dt = Vt['Dashboard'], Vt['CEO Report'], Vt['⚖️ Wahrscheinlichkeit'], Vt['_data']
print('Szenario A (neuer WON-Deal in Zeile 81):')
pruef('A1 Dashboard WON +50000 / +1',
      abs(dash['A6'].value - (WON0 + 50000)) < 0.01 and dash['A7'].value == WONN0 + 1,
      f"{dash['A6'].value} / {dash['A7'].value}")
namen = {ceo[f'B{r}'].value for r in range(11, 73)}
pruef('A2 CEO-WON-Liste zeigt den Testkunden', 'TESTKUNDE Verhaltenstest' in namen)
pruef('A3 ⚖️ 100-%-Band +1', w['E21'].value == BAND100_0 + 1, str(w['E21'].value))
rest = [(dt[f'R{r}'].value, dt[f'S{r}'].value) for r in range(2, 34)
        if dt[f'R{r}'].value not in (None, '')]
wach = [x for x in rest if 'Übrige' in str(x[0])]
pruef('A4 Wachhund-Restbalken für neues Segment',
      len(wach) == 1 and abs(wach[0][1] - 50000) < 0.01, str(wach))
pruef('A5 Vertragsarten «ohne Angabe» zählt den Deal',
      ceo['D259'].value is not None and ceo['E260'].value is not None
      and abs(ceo['E260'].value - dash['A6'].value) < 0.01,
      f"Total {ceo['E260'].value}")

# ---------------------------------------------------------------- B
wb = openpyxl.load_workbook(K)
p = wb['MiT Strom Pipeline']
p[f'O{R}'] = datetime.date(2026, 8, 1)
p[f'P{R}'] = datetime.date(2026, 8, 10)
wb.save(K)
recalc()
Vt = lade()
vp, vd, vceo = Vt['MiT Strom Pipeline'], Vt['📋 Definitionen & Klärung'], Vt['CEO Report']
liste1 = sum(1 for r in range(82, 132) if vd[f'B{r}'].value not in (None, ''))
print('Szenario B (Zeitraum nachgetragen):')
pruef('B1 Dauer = 10 Kalendertage', vp[f'G{R}'].value == 10, str(vp[f'G{R}'].value))
# neuer Deal kam ohne Zeitraum dazu (+1), Zeitraum erfasst (-1) -> = LISTE0
pruef('B2 Erfassungsliste = Ausgangsstand', liste1 == min(LISTE0, 50), f'{liste1} vs {LISTE0}')
pruef('B3 Monatstabelle August zählt den Deal',
      (vceo['E242'].value or 0) >= 1 and (vceo['F242'].value or 0) >= 50000,
      f"{vceo['E242'].value} / {vceo['F242'].value}")

# ---------------------------------------------------------------- C
wb = openpyxl.load_workbook(K)
p = wb['MiT Strom Pipeline']
p[f'R{R}'] = 'offered'
p[f'O{R}'] = datetime.date(2026, 8, 10)
p[f'P{R}'] = datetime.date(2026, 8, 1)
wb.save(K)
recalc()
Vt = lade()
vp = Vt['MiT Strom Pipeline']
print('Szenario C (Ende vor Start):')
pruef('C1 Kurzstatus BA meldet «Ende vor Start»',
      'Ende vor Start' in str(vp[f'BA{R}'].value), str(vp[f'BA{R}'].value))

# ---------------------------------------------------------------- D
wb = openpyxl.load_workbook(K)
p = wb['MiT Strom Pipeline']
p[f'R{R}'] = 'LOST'
wb.save(K)
recalc()
Vt = lade()
dash, w = Vt['Dashboard'], Vt['⚖️ Wahrscheinlichkeit']
print('Szenario D (WON -> LOST):')
pruef('D1 WON-Kachel zurück auf Ausgangswert',
      abs(dash['A6'].value - WON0) < 0.01 and dash['A7'].value == WONN0,
      f"{dash['A6'].value} / {dash['A7'].value}")
pruef('D2 100-%-Band zurück', w['E21'].value == BAND100_0, str(w['E21'].value))

print(f'\nVerhaltenstest: {len(fehler)} Fehler')
sys.exit(1 if fehler else 0)
