#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C) Unabhaengige Nachrechnung: das gesamte Modell wird in Python neu
implementiert (nur aus den Roheingaben) und Zelle fuer Zelle gegen die
von LibreOffice berechneten Werte der Mappe verglichen.
"""
import openpyxl, sys
from datetime import date

F = sys.argv[1] if len(sys.argv) > 1 else 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
V = openpyxl.load_workbook(F, data_only=True)
P, W, D, CEO, REP, EX, DAT = (V['MiT Strom Pipeline'], V['⚖️ Wahrscheinlichkeit'],
                              V['Dashboard'], V['CEO Report'], V['📄 Report'],
                              V['📑 Executive PDF'], V['_data'])
LAST = 860
AKTIV = ["WON", "offered", "to be offered", "on hold",
         "follow-up", "Evaluation", "In evaluation", "tbd"]
SKALA = [0, 0.1, 0.3, 0.6, 0.9]
BANDS = [(0.00, 0.4499999, 0.00), (0.45, 0.5999999, 0.30),
         (0.60, 0.8999999, 0.50), (0.90, 1.00, 0.90)]

fails, checks = [], 0


def eq(a, b, tol=1e-6):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol * max(1.0, abs(a), abs(b))
    if a is None and (b == '' or b is None):
        return True
    if b is None and (a == '' or a is None):
        return True
    return a == b


def chk(label, expect, actual, tol=1e-6):
    global checks
    checks += 1
    if not eq(expect, actual, tol):
        fails.append((label, expect, actual))


def isnum(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


# ---------------------------------------------------------------- Rohdaten
raw = {}
for r in range(6, LAST + 1):
    raw[r] = {c: P[f'{c}{r}'].value for c in
              ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
               'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
               'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF')}

# N-Spalte enthaelt teils Formeln (MwSt) - der berechnete Wert steht drin.


def faktor(s):
    """Aggreko-Gewichtungsfaktor aus der effektiven Wahrscheinlichkeit."""
    if not isnum(s):
        return 0
    p = s if s <= 1 else s / 100
    best = 0
    for lo, hi, fk in BANDS:          # LOOKUP: groesste Untergrenze <= p
        if p >= lo:
            best = fk
    return best


# =================================================== 1) Pipeline-Zeilenlogik
cnt_won = cnt_off = cnt_opp = 0
exp = {}
for r in range(6, LAST + 1):
    d = raw[r]
    I, S, R, B = d['I'], d['S'], d['R'], d['B']

    o = I - sum(x for x in (d['J'], d['K'], d['L'], d['M'], d['N']) if isnum(x)) if isnum(I) else ''
    p = (o / I) if (isnum(o) and isnum(I) and I != 0) else ''
    y = faktor(S) if isnum(S) else 0
    q = I * y if (isnum(I) and isnum(S)) else ('tbd' if (I not in (None, '') or S not in (None, '')) else '')
    aa = I * 1 if isnum(I) else 0
    z = (aa + (861 - r) * 0.000001) if (R == 'WON' and isnum(I)) else ''
    cnt_won += 1 if (R == 'WON' and B not in (None, '')) else 0
    cnt_off += 1 if (R in ('offered', 'to be offered', 'on hold') and B not in (None, '')) else 0
    cnt_opp += 1 if (R in ('follow-up', 'Evaluation', 'tbd', 'In evaluation') and B not in (None, '')) else 0
    ae = 0 if B in (None, '') else (1 if R in AKTIV else 0)
    af = 0 if B in (None, '') else (1 if (isnum(S) and S in SKALA) else 0)

    exp[r] = dict(O=o, P=p, Q=q, Y=y, Z=z, AA=aa, AB=cnt_won, AC=cnt_off, AD=cnt_opp, AE=ae, AF=af)
    for col in ('O', 'P', 'Q', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF'):
        chk(f'Pipeline!{col}{r}', exp[r][col], d[col])

# Kopfzeilen der Pipeline
won_sum = sum(raw[r]['I'] for r in raw if raw[r]['R'] == 'WON' and isnum(raw[r]['I']))
aktiv_cnt = sum(1 for r in raw if raw[r]['R'] in AKTIV)
offen_sum = sum(raw[r]['I'] for r in raw
                if raw[r]['R'] in ('offered', 'to be offered', 'on hold') and isnum(raw[r]['I']))
gew_sum = sum(exp[r]['Q'] for r in raw
              if raw[r]['R'] in AKTIV and isnum(exp[r]['Q']))
chk('Pipeline!C4 WON-Umsatz', won_sum, P['C4'].value)
chk('Pipeline!I4 Anzahl aktiv', aktiv_cnt, P['I4'].value)
chk('Pipeline!O4 offene Pipeline', offen_sum, P['O4'].value)
chk('Pipeline!U4 gewichtet', gew_sum, P['U4'].value)

# ========================================== 2) Blatt "Wahrscheinlichkeit"
band_cnt, band_rev, band_wgt = [], [], []
for i, (lo, hi, fk) in enumerate(BANDS):
    rows = [r for r in raw if exp[r]['AE'] == 1 and exp[r]['Y'] == fk]
    n = len(rows)
    rev = sum(exp[r]['AA'] for r in rows)
    band_cnt.append(n); band_rev.append(rev); band_wgt.append(rev * fk)
    R0 = 16 + i
    chk(f'W!D{R0} Faktor', fk, W[f'D{R0}'].value)
    chk(f'W!E{R0} Anzahl', n, W[f'E{R0}'].value)
    chk(f'W!F{R0} Umsatz', rev, W[f'F{R0}'].value)
    chk(f'W!G{R0} gewichtet', rev * fk, W[f'G{R0}'].value)

tot_cnt, tot_rev, tot_wgt = sum(band_cnt), sum(band_rev), sum(band_wgt)
for i in range(4):
    chk(f'W!H{16+i} Anteil', (band_wgt[i] / tot_wgt) if tot_wgt else 0, W[f'H{16+i}'].value)
chk('W!E20 Total Anzahl', tot_cnt, W['E20'].value)
chk('W!F20 Total Umsatz', tot_rev, W['F20'].value)
chk('W!G20 Total gewichtet', tot_wgt, W['G20'].value)
chk('W!H20 Gewichtungsgrad', tot_wgt / tot_rev if tot_rev else 0, W['H20'].value)

# Kontrollzeilen
gew_aktiv_q = sum(exp[r]['Q'] for r in raw if raw[r]['R'] in AKTIV and isnum(exp[r]['Q']))
chk('W!E24 Bandtabelle', tot_wgt, W['E24'].value)
chk('W!E25 Spalte Q', gew_aktiv_q, W['E25'].value)
chk('W!E26 Abweichung', 0, W['E26'].value)
chk('W!E27 Status', '✔  Konsistent — alle Blätter rechnen mit demselben Modell', W['E27'].value)
offscale = sum(1 for r in raw if exp[r]['AE'] == 1 and exp[r]['AF'] == 0)
chk('W!E28 ausserhalb Skala', offscale, W['E28'].value)
unter = sum(1 for r in raw if r >= 91 and raw[r]['B'] not in (None, ''))
chk('W!E30 unter Druckbereich', unter, W['E30'].value)
chk('W!E31 Status Druckbereich',
    '✔  Alle Deals liegen im Druckbereich (Zeilen 6–90)' if unter == 0
    else f'⚠  {unter} Deal(s) unterhalb Zeile 90 — Druckbereich der Pipeline erweitern',
    W['E31'].value)
# Skala-Werte im Blatt
for i, v in enumerate(SKALA):
    chk(f'W!B{6+i} Skalenwert', v, W[f'B{6+i}'].value)

# =========================================== 3) Dashboard / CEO Report
def sum_status(states):
    return sum(raw[r]['I'] for r in raw if raw[r]['R'] in states and isnum(raw[r]['I']))


def cnt_status(states):
    return sum(1 for r in raw if raw[r]['R'] in states)


def sumq_status(states):
    return sum(exp[r]['Q'] for r in raw if raw[r]['R'] in states and isnum(exp[r]['Q']))


OFF = ('offered', 'to be offered', 'on hold')
OPP = ('follow-up', 'Evaluation', 'tbd', 'In evaluation')
DASH_OFF_KPI = ('offered', 'to be offered')      # Dashboard D6 zaehlt on hold NICHT mit

chk('Dashboard!A6 WON', sum_status(('WON',)), D['A6'].value)
chk('Dashboard!A7 WON#', cnt_status(('WON',)), D['A7'].value)
chk('Dashboard!D6 Offerte', sum_status(OFF), D['D6'].value)
chk('Dashboard!D7 Offerte#', cnt_status(OFF), D['D7'].value)
chk('Dashboard!G6 Opp', sum_status(OPP), D['G6'].value)
chk('Dashboard!G7 Opp#', cnt_status(OPP), D['G7'].value)
chk('Dashboard!I6 Gesamt', sum_status(('WON',) + OFF + OPP), D['I6'].value)
chk('Dashboard!I7 Gesamt#', cnt_status(('WON',) + OFF + OPP), D['I7'].value)
chk('Dashboard!F201', sum_status(('WON',) + OFF + OPP), D['F201'].value)
chk('Dashboard!F202', sum_status(('WON',)), D['F202'].value)
chk('Dashboard!F203', sum_status(OFF), D['F203'].value)
chk('Dashboard!F204', sum_status(OPP), D['F204'].value)

for sh, name, lastcol in ((D, 'Dashboard', 'K'), (CEO, 'CEO Report', 'L')):
    for i in range(4):
        r = 208 + i
        chk(f'{name}!D{r}', BANDS[i][2], sh[f'D{r}'].value)
        chk(f'{name}!E{r}', band_cnt[i], sh[f'E{r}'].value)
        chk(f'{name}!F{r}', band_rev[i], sh[f'F{r}'].value)
        chk(f'{name}!G{r}', band_wgt[i], sh[f'G{r}'].value)
    chk(f'{name}!E212', tot_cnt, sh['E212'].value)
    chk(f'{name}!F212', tot_rev, sh['F212'].value)
    chk(f'{name}!G212', tot_wgt, sh['G212'].value)
    txt = sh['A8'].value or ''
    for needle in (f'{sumq_status(AKTIV):,.0f}'.replace(',', ','), 'Aggreko-Faktoren'):
        if needle not in txt:
            fails.append((f'{name}!A8 Infozeile', needle, txt))
        checks += 1

# Detailzeilen der drei Bloecke (INDEX/MATCH ueber die Laufzaehler)
def match_row(counter_key, k):
    for r in range(6, LAST + 1):
        if exp[r][counter_key] == k:
            return r
    return None


BLOCKS = [('AB', 11, 72), ('AC', 75, 136), ('AD', 139, 200)]
for sh, name, colmap in (
        (D, 'Dashboard', dict(A='A', B='B', C='C', D='D', E='H', F='E', G='I', H='Q', I='R', J='S', K='V')),
        (CEO, 'CEO Report', dict(A='A', B='B', C='C', D='D', E='H', F='E', G='I', H='Q', I='O', J='R', K='S', L='V'))):
    for key, first, last in BLOCKS:
        for n, xr in enumerate(range(first, last + 1), start=1):
            src = match_row(key, n)
            u = sh[f'U{xr}'].value
            chk(f'{name}!U{xr}', src if src else '', u)
            if not src:
                continue
            for out_col, pipe_col in colmap.items():
                got = sh[f'{out_col}{xr}'].value
                pv = raw[src][pipe_col]
                if out_col in ('A',):
                    want = pv if isnum(pv) else ''
                elif out_col in ('G', 'H') or (name == 'CEO Report' and out_col == 'I'):
                    src_val = exp[src][pipe_col] if pipe_col in exp[src] else pv
                    want = src_val if isnum(src_val) else 0
                elif pipe_col == 'S':
                    want = pv if isnum(pv) else ''
                elif pipe_col == 'V':
                    want = str(pv)[:55] if pv not in (None, '') else ''
                elif pipe_col == 'R':
                    want = pv
                else:
                    want = pv if pv not in (None, '') else ''
                chk(f'{name}!{out_col}{xr} (Quelle Zeile {src})', want, got)

# ================================================== 4) 📄 Report
chk('Report!B7', sum_status(('WON',)), REP['B7'].value)
chk('Report!B8', sum_status(OFF), REP['B8'].value)
chk('Report!B9', sum_status(OPP), REP['B9'].value)
chk('Report!B10', sum_status(('WON',) + OFF + OPP), REP['B10'].value)
chk('Report!B11 gewichtet', tot_wgt, REP['B11'].value)
chk('Report!C11', tot_cnt, REP['C11'].value)
_ges = sum_status(('WON',) + OFF + OPP)
chk('Report!D11', (tot_wgt / _ges) if _ges else 0, REP['D11'].value)
for i in range(4):
    r = 45 + i
    chk(f'Report!B{r}', BANDS[i][2], REP[f'B{r}'].value)
    chk(f'Report!C{r}', band_cnt[i], REP[f'C{r}'].value)
    chk(f'Report!D{r}', band_rev[i], REP[f'D{r}'].value)
    chk(f'Report!E{r}', band_wgt[i], REP[f'E{r}'].value)
chk('Report!E49', tot_wgt, REP['E49'].value)

# Kantons-Ranking
KT = [REP[f'J{r}'].value for r in range(14, 40)]
vol = {k: sum(raw[r]['I'] for r in raw if raw[r]['C'] == k and isnum(raw[r]['I'])) for k in KT}
rankkey = {k: vol[k] + (26 - (14 + i)) * 0.0001 for i, k in enumerate(KT)}
order = sorted(KT, key=lambda k: -rankkey[k])
for i in range(10):
    r = 15 + i
    k = order[i]
    chk(f'Report!B{r} Kanton', k, REP[f'B{r}'].value)
    chk(f'Report!C{r} Volumen', vol[k], REP[f'C{r}'].value)
    chk(f'Report!D{r} Anzahl', sum(1 for x in raw if raw[x]['C'] == k), REP[f'D{r}'].value)
    n = sum(1 for x in raw if raw[x]['C'] == k)
    wonn = sum(1 for x in raw if raw[x]['C'] == k and raw[x]['R'] == 'WON')
    chk(f'Report!E{r} WON-Rate', (wonn / n) if n else '', REP[f'E{r}'].value)

# Top-WON (LARGE ueber Z)
zvals = sorted([exp[r]['Z'] for r in raw if isnum(exp[r]['Z'])], reverse=True)
for i in range(10):
    r = 29 + i
    if i < len(zvals):
        v = zvals[i]
        first = next(x for x in range(6, LAST + 1) if exp[x]['Z'] == v)
        chk(f'Report!E{r} Volumen', raw[first]['I'], REP[f'E{r}'].value)
        chk(f'Report!B{r} Kunde', raw[first]['B'], REP[f'B{r}'].value)
        chk(f'Report!C{r} Kanton', raw[first]['C'], REP[f'C{r}'].value)
        chk(f'Report!F{r} Marge', exp[first]['O'], REP[f'F{r}'].value)
    else:
        chk(f'Report!B{r} leer', '', REP[f'B{r}'].value)

# ================================================== 5) 📑 Executive PDF
chk('ExecPDF!B6', sum_status(('WON',)), EX['B6'].value)
chk('ExecPDF!E6', sum_status(OFF), EX['E6'].value)
chk('ExecPDF!G6', sum_status(OPP), EX['G6'].value)
gesamt = sum_status(('WON',) + OFF + OPP)
STAT = [('WON',), ('offered', 'to be offered'), ('follow-up',),
        ('Evaluation', 'In evaluation'), ('on hold',), ('tbd',), ('LOST',), ('Declined',)]
for i, st in enumerate(STAT):
    r = 23 + i
    chk(f'ExecPDF!D{r}', cnt_status(st), EX[f'D{r}'].value)
    chk(f'ExecPDF!E{r}', sum_status(st), EX[f'E{r}'].value)
    chk(f'ExecPDF!G{r}', sum_status(st) / gesamt if gesamt else 0, EX[f'G{r}'].value)
for i in range(4):
    r = 34 + i
    chk(f'ExecPDF!D{r}', BANDS[i][2], EX[f'D{r}'].value)
    chk(f'ExecPDF!E{r}', band_rev[i], EX[f'E{r}'].value)
    chk(f'ExecPDF!G{r}', band_wgt[i], EX[f'G{r}'].value)
chk('ExecPDF!E38', tot_rev, EX['E38'].value)
chk('ExecPDF!G38', tot_wgt, EX['G38'].value)
for i in range(5):
    r = 14 + i
    if i >= len(zvals):
        chk(f'ExecPDF!C{r} leer', '', EX[f'C{r}'].value)
        continue
    v = zvals[i]
    first = next(x for x in range(6, LAST + 1) if exp[x]['Z'] == v)
    chk(f'ExecPDF!C{r} Kunde', raw[first]['B'], EX[f'C{r}'].value)
    chk(f'ExecPDF!G{r} Volumen', raw[first]['I'], EX[f'G{r}'].value)
    chk(f'ExecPDF!H{r} Marge', exp[first]['O'], EX[f'H{r}'].value)

# ================================================== 6) _data
for r in range(2, 12):
    key = DAT[f'A{r}'].value
    chk(f'_data!C{r}', cnt_status((key,)), DAT[f'C{r}'].value)
    chk(f'_data!D{r}', sum_status((key,)), DAT[f'D{r}'].value)
for r in range(2, 28):
    seg = DAT[f'G{r}'].value
    if seg is None:
        continue
    chk(f'_data!H{r}', sum(raw[x]['I'] for x in raw if raw[x]['D'] == seg and isnum(raw[x]['I'])),
        DAT[f'H{r}'].value)
    chk(f'_data!I{r}', sum(1 for x in raw if raw[x]['D'] == seg), DAT[f'I{r}'].value)
for r in range(14, 40):
    k = DAT[f'A{r}'].value
    chk(f'_data!B{r}', vol.get(k, 0), DAT[f'B{r}'].value)
    chk(f'_data!C{r}', sum(1 for x in raw if raw[x]['C'] == k), DAT[f'C{r}'].value)
    chk(f'_data!D{r}', sum(1 for x in raw if raw[x]['C'] == k and raw[x]['R'] == 'WON'),
        DAT[f'D{r}'].value)
for i in range(4):
    r = 2 + i
    chk(f'_data!L{r}', BANDS[i][2], DAT[f'L{r}'].value)
    chk(f'_data!M{r}', band_rev[i], DAT[f'M{r}'].value)
    chk(f'_data!N{r}', band_wgt[i], DAT[f'N{r}'].value)
    chk(f'_data!O{r}', band_cnt[i], DAT[f'O{r}'].value)

# ================================================================== Ergebnis
print(f'Geprüfte Zellen/Werte : {checks}')
print(f'Abweichungen          : {len(fails)}')
for lbl, e, a in fails[:60]:
    print(f'   {lbl}\n       erwartet={e!r}\n       gefunden={a!r}')
sys.exit(1 if fails else 0)
