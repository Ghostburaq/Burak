#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C) Unabhaengige Nachrechnung: das gesamte Modell wird in Python neu
implementiert (nur aus den Roheingaben) und Zelle fuer Zelle gegen die
von LibreOffice berechneten Werte der Mappe verglichen.
"""
import openpyxl, sys, datetime
from datetime import date

F = sys.argv[1] if len(sys.argv) > 1 else 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
V = openpyxl.load_workbook(F, data_only=True)
P, W, D, CEO, REP, EX, DAT = (V['MiT Strom Pipeline'], V['⚖️ Wahrscheinlichkeit'],
                              V['Dashboard'], V['CEO Report'], V['📄 Report'],
                              V['📑 Executive PDF'], V['_data'])
LAST = 860
AKTIV = ["WON", "offered", "to be offered", "on hold",
         "follow-up", "Evaluation", "In evaluation", "tbd"]
SKALA = [0, 0.1, 0.3, 0.6, 0.9, 1.0]
BANDS = [(0.00, 0.4499999, 0.00), (0.45, 0.5999999, 0.30),
         (0.60, 0.8999999, 0.50), (0.90, 0.9999999, 0.90),
         (1.00, 1.00, 1.00)]

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
COLS = ('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z '
        'AA AB AC AD AE AF AG AH AI AJ AK AL AM AN AO AP AQ AR AS AT AU AV AW '
        'AX AY AZ BA BB BC').split()
raw = {r: {c: P[f'{c}{r}'].value for c in COLS} for r in range(6, LAST + 1)}

# Die urspruenglich von Hand erfasste Mietdauer steht in der Quelldatei und
# wird beim Bau in die ausgeblendete Spalte AW gesichert - das Modell liest
# sie unabhaengig aus derselben Quelle.
# Die Quelldatei heisst in der Arbeitskopie original.xlsx und im Repository
# quelle_stand_vor_update.xlsx - beide Namen und beide Ordner werden gesucht.
import os as _os
_KANDIDATEN = [_os.path.join(d, n)
               for d in ('.', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
               for n in ('original.xlsx', 'quelle_stand_vor_update.xlsx')]
_QUELLE = next((k for k in _KANDIDATEN if _os.path.exists(k)), None)
assert _QUELLE, f'Quelldatei nicht gefunden, gesucht in: {_KANDIDATEN}'
_Q = openpyxl.load_workbook(_QUELLE, data_only=True)['MiT Strom Pipeline']
dauer_alt = {r: _Q[f'G{r}'].value for r in range(6, LAST + 1)
             if _Q[f'G{r}'].value is not None and _Q[f'B{r}'].value not in (None, '')}

# Annahmezellen ueber die benannten Bereiche holen - keine fixen Zeilennummern
D_ = V['📋 Definitionen & Klärung']


def named(nm):
    ref = V.defined_names[nm].attr_text.split('!')[1].replace('$', '')
    return D_[ref].value


NETTO_FAKTOR = named('Netto_Faktor')
SCHWELLE = named('Schwelle_Aufteilung')
assert isinstance(NETTO_FAKTOR, (int, float)) and NETTO_FAKTOR > 0, NETTO_FAKTOR
assert isinstance(SCHWELLE, (int, float)), SCHWELLE

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

    # Nettoumsatz und Einstand
    netto = I / NETTO_FAKTOR if isnum(I) else ''
    kosten = [d[c] for c in ('J', 'K', 'L', 'M', 'N')]
    einstand = '' if B in (None, '') else ('' if sum(1 for x in kosten if isnum(x)) == 0
                                           else sum(x for x in kosten if isnum(x)))
    # Nachweis und Zeitraum
    ein_ok = 0 if B in (None, '') else (
        1 if (sum(1 for c in 'JKLM' if isnum(d[c])) == 4
              and sum(d[c] for c in 'JKLM' if isnum(d[c])) > 0) else 0)
    von, bis = d['O'], d['P']
    ist_datum = isinstance(von, datetime.datetime) and isinstance(bis, datetime.datetime)
    zeit_ok = 0 if B in (None, '') else (1 if (ist_datum and bis >= von) else 0)
    monat = (datetime.datetime(von.year, von.month, 1) if zeit_ok == 1 else '')
    dauer_erf = dauer_alt.get(r)
    dauer = '' if B in (None, '') else (
        (bis - von).days + 1 if zeit_ok == 1
        else ('' if dauer_erf is None else dauer_erf))
    y = faktor(S) if isnum(S) else 0
    q = I * y if (isnum(I) and isnum(S)) else ('tbd' if (I not in (None, '') or S not in (None, '')) else '')
    aa = I * 1 if isnum(I) else 0
    z = (aa + (861 - r) * 0.000001) if (R == 'WON' and isnum(I)) else ''
    cnt_won += 1 if (R == 'WON' and B not in (None, '')) else 0
    cnt_off += 1 if (R in ('offered', 'to be offered', 'on hold') and B not in (None, '')) else 0
    cnt_opp += 1 if (R in ('follow-up', 'Evaluation', 'tbd', 'In evaluation') and B not in (None, '')) else 0
    ae = 0 if B in (None, '') else (1 if R in AKTIV else 0)
    af = 0 if B in (None, '') else (1 if (isnum(S) and S in SKALA) else 0)
    bel_ok = 0 if B in (None, '') else (
        1 if (d['AF'] not in (None, '') and d['AG'] not in (None, '')) else 0)
    wonb = 1 if (R == 'WON' and bel_ok == 1 and ein_ok == 1) else 0
    zaehlt = 0 if B in (None, '') else (0 if d['AD'] == 'Alternative – zählt nicht' else 1)
    mehrf = 0 if B in (None, '') else (
        1 if sum(1 for x in range(6, LAST + 1) if raw[x]['B'] == B) > 1 else 0)

    # Sammelbefund und Kurzstatus - dieselbe Reihenfolge wie im File.
    if B in (None, ''):
        befunde, kurz = '', ''
    else:
        teile = []
        if R == 'WON' and bel_ok == 0:
            teile.append('⛔ Beleg fehlt')
        if R == 'WON' and ein_ok == 0:
            teile.append('⛔ Einstand fehlt')
        if R != 'WON' and ein_ok == 0:
            teile.append('○ Einstand offen')
        if R == 'WON' and d['AB'] in (None, ''):
            teile.append('⛔ Vertragsart fehlt')
        if ist_datum and bis < von:
            teile.append('⚠ Ende vor Start')
        if R == 'WON' and zeit_ok == 0 and not ist_datum:
            teile.append('⛔ Zeitraum fehlt')
        if R != 'WON' and zeit_ok == 0 and not ist_datum:
            teile.append('○ Zeitraum offen')
        befunde = (' · '.join(teile) + ' · ') if teile else ''
        if R == 'WON' and bel_ok == 0:
            kurz = '⛔ Nachweis fehlt'
        elif ist_datum and bis < von:
            kurz = '⚠ Ende vor Start'
        elif R == 'WON' and zeit_ok == 0:
            kurz = '⛔ Zeitraum fehlt'
        elif ein_ok == 0:
            kurz = '○ Einstand offen'
        elif zeit_ok == 0:
            kurz = '○ Zeitraum offen'
        elif R == 'WON':
            kurz = '✅ belegt'
        else:
            kurz = '✔ erfasst'

    exp[r] = dict(G=dauer, Q=q, Y=netto, Z=einstand, AJ=y, AK=z, AL=aa,
                  AM=cnt_won, AN=cnt_off, AO=cnt_opp, AP=ae, AQ=af,
                  AR=ein_ok, AS=bel_ok, AT=wonb, AU=zaehlt, AV=mehrf,
                  AX=monat, AY=zeit_ok,
                  AZ=(netto if isnum(netto) else 0), BB=kurz)
    for col in ('G', 'Q', 'Y', 'Z', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO',
                'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AX', 'AY', 'AZ', 'BB'):
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
# Zeilen der Bandtabelle und der Kontrollen werden gesucht, damit die Pruefung
# nicht an einer festen Zeilennummer haengt.
BAND0 = next(r for r in range(1, 40) if W[f'A{r}'].value == '0 – 44 %')
BANDT = BAND0 + len(BANDS)
KTRL = next(r for r in range(BANDT, 60)
            if str(W[f'A{r}'].value or '').startswith('Gewichtete Pipeline laut Bandtabelle'))

band_cnt, band_rev, band_wgt = [], [], []
for i, (lo, hi, fk) in enumerate(BANDS):
    rows = [r for r in raw if exp[r]['AP'] == 1 and exp[r]['AJ'] == fk]
    n = len(rows)
    rev = sum(exp[r]['AL'] for r in rows)
    band_cnt.append(n); band_rev.append(rev); band_wgt.append(rev * fk)
    R0 = BAND0 + i
    chk(f'W!D{R0} Faktor', fk, W[f'D{R0}'].value)
    chk(f'W!E{R0} Anzahl', n, W[f'E{R0}'].value)
    chk(f'W!F{R0} Umsatz', rev, W[f'F{R0}'].value)
    chk(f'W!G{R0} gewichtet', rev * fk, W[f'G{R0}'].value)

tot_cnt, tot_rev, tot_wgt = sum(band_cnt), sum(band_rev), sum(band_wgt)
for i in range(len(BANDS)):
    chk(f'W!H{BAND0+i} Anteil', (band_wgt[i] / tot_wgt) if tot_wgt else 0, W[f'H{BAND0+i}'].value)
chk(f'W!E{BANDT} Total Anzahl', tot_cnt, W[f'E{BANDT}'].value)
chk(f'W!F{BANDT} Total Umsatz', tot_rev, W[f'F{BANDT}'].value)
chk(f'W!G{BANDT} Total gewichtet', tot_wgt, W[f'G{BANDT}'].value)
chk(f'W!H{BANDT} Gewichtungsgrad', tot_wgt / tot_rev if tot_rev else 0, W[f'H{BANDT}'].value)

# Kontrollzeilen
gew_aktiv_q = sum(exp[r]['Q'] for r in raw if raw[r]['R'] in AKTIV and isnum(exp[r]['Q']))
chk(f'W!E{KTRL} Bandtabelle', tot_wgt, W[f'E{KTRL}'].value)
chk(f'W!E{KTRL+1} Spalte Q', gew_aktiv_q, W[f'E{KTRL+1}'].value)
chk(f'W!E{KTRL+2} Abweichung', 0, W[f'E{KTRL+2}'].value)
chk(f'W!E{KTRL+3} Status', '✔  Konsistent — alle Blätter rechnen mit demselben Modell',
    W[f'E{KTRL+3}'].value)
offscale = sum(1 for r in raw if exp[r]['AP'] == 1 and exp[r]['AQ'] == 0)
chk(f'W!E{KTRL+4} ausserhalb Skala', offscale, W[f'E{KTRL+4}'].value)
# Die Stufe 100 % gehoert ausschliesslich gewonnenen Auftraegen.
won_ohne = sum(1 for r in raw if raw[r]['B'] not in (None, '')
               and raw[r]['R'] == 'WON' and raw[r]['S'] != 1)
hundert_ohne = sum(1 for r in raw if raw[r]['B'] not in (None, '')
                   and raw[r]['S'] == 1 and raw[r]['R'] != 'WON')
chk(f'W!E{KTRL+8} WON ohne 100 %', won_ohne, W[f'E{KTRL+8}'].value)
chk(f'W!E{KTRL+9} 100 % ohne WON', hundert_ohne, W[f'E{KTRL+9}'].value)
unter = sum(1 for r in raw if r >= 91 and raw[r]['B'] not in (None, ''))
chk(f'W!E{KTRL+6} unter Druckbereich', unter, W[f'E{KTRL+6}'].value)
chk(f'W!E{KTRL+7} Status Druckbereich',
    '✔  Alle Deals liegen im Druckbereich (Zeilen 6–90)' if unter == 0
    else f'⚠  {unter} Deal(s) unterhalb Zeile 90 — Druckbereich der Pipeline erweitern',
    W[f'E{KTRL+7}'].value)
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
    for i in range(len(BANDS)):
        r = 208 + i
        chk(f'{name}!D{r}', BANDS[i][2], sh[f'D{r}'].value)
        chk(f'{name}!E{r}', band_cnt[i], sh[f'E{r}'].value)
        chk(f'{name}!F{r}', band_rev[i], sh[f'F{r}'].value)
        chk(f'{name}!G{r}', band_wgt[i], sh[f'G{r}'].value)
    _rbt = 208 + len(BANDS)
    chk(f'{name}!E{_rbt}', tot_cnt, sh[f'E{_rbt}'].value)
    chk(f'{name}!F{_rbt}', tot_rev, sh[f'F{_rbt}'].value)
    chk(f'{name}!G{_rbt}', tot_wgt, sh[f'G{_rbt}'].value)
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


BLOCKS = [('AM', 11, 72), ('AN', 75, 136), ('AO', 139, 200)]
for sh, name, colmap in (
        (D, 'Dashboard', dict(A='A', B='B', C='C', D='D', E='_von', F='E', G='I', H='Q',
                              I='R', J='S', K='V')),
        (CEO, 'CEO Report', dict(A='A', B='B', C='C', D='D', E='_von', F='_bis', G='I', H='Q',
                                 I='E', J='R', K='S', L='V', M='AF', N='BB'))):
    for key, first, last in BLOCKS:
        for n, xr in enumerate(range(first, last + 1), start=1):
            src = match_row(key, n)
            u = sh[f'U{xr}'].value
            chk(f'{name}!U{xr}', src if src else '', u)
            if not src:
                continue
            for out_col, pipe_col in colmap.items():
                got = sh[f'{out_col}{xr}'].value
                # Projektstart faellt auf die grobe Monatsangabe zurueck,
                # solange kein echtes Datum erfasst ist.
                if pipe_col == '_von':
                    v = raw[src]['O']
                    want = v if isinstance(v, datetime.datetime) else (raw[src]['H'] or '')
                    chk(f'{name}!{out_col}{xr} (Quelle Zeile {src})', want, got)
                    continue
                if pipe_col == '_bis':
                    v = raw[src]['P']
                    want = v if isinstance(v, datetime.datetime) else ''
                    chk(f'{name}!{out_col}{xr} (Quelle Zeile {src})', want, got)
                    continue
                pv = raw[src][pipe_col]
                if out_col in ('A',):
                    want = pv if isnum(pv) else ''
                elif out_col in ('G', 'H'):
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
won_belegt = sum(exp[r]['AL'] for r in raw if exp[r]['AT'] == 1)
chk('Report!B12 WON belegt', won_belegt, REP['B12'].value)
chk('Report!C12 Anzahl belegt', sum(exp[r]['AT'] for r in raw), REP['C12'].value)
_wonbr = sum_status(('WON',))
chk('Report!D12 Anteil', (won_belegt / _wonbr) if _wonbr else 0, REP['D12'].value)
won_netto = sum(exp[r]['AZ'] for r in raw if raw[r]['R'] == 'WON')
akt_brutto = sum(exp[r]['AL'] for r in raw if exp[r]['AP'] == 1)
akt_berein = sum(exp[r]['AL'] for r in raw if exp[r]['AP'] == 1 and exp[r]['AU'] == 1)
akt_cnt = sum(1 for r in raw if exp[r]['AP'] == 1)
zeit_erf = sum(1 for r in raw if exp[r]['AP'] == 1 and exp[r]['AY'] == 1)
zeit_off = sum(1 for r in raw if exp[r]['AP'] == 1 and exp[r]['AY'] == 0)
zeit_vol = sum(exp[r]['AL'] for r in raw if exp[r]['AP'] == 1 and exp[r]['AY'] == 0)
quote = (won_belegt / _wonbr) if _wonbr else 0
chk('ExecPDF!E43 WON netto', won_netto, EX['E43'].value)
chk('ExecPDF!E44 WON belegt', won_belegt, EX['E44'].value)
chk('ExecPDF!E45 Nachweisquote', quote, EX['E45'].value)
chk('ExecPDF!E46 Zeitraum erfasst', f'{zeit_erf} von {akt_cnt}', EX['E46'].value)
for _sh, _nm in ((D, 'Dashboard'), (CEO, 'CEO Report')):
    chk(f'{_nm}!E220 WON brutto', _wonbr, _sh['E220'].value)
    chk(f'{_nm}!E221 WON netto', won_netto, _sh['E221'].value)
    chk(f'{_nm}!E222 WON belegt', won_belegt, _sh['E222'].value)
    chk(f'{_nm}!E223 offen', _wonbr - won_belegt, _sh['E223'].value)
    chk(f'{_nm}!E224 aktiv brutto', akt_brutto, _sh['E224'].value)
    chk(f'{_nm}!E225 aktiv bereinigt', akt_berein, _sh['E225'].value)
    chk(f'{_nm}!E226 Nachweisquote', quote, _sh['E226'].value)
    chk(f'{_nm}!E227 Zeitraum erfasst', zeit_erf, _sh['E227'].value)
    chk(f'{_nm}!E228 Zeitraum offen', zeit_off, _sh['E228'].value)
    chk(f'{_nm}!E229 Volumen ohne Zeitraum', zeit_vol, _sh['E229'].value)
chk('Report!C11', tot_cnt, REP['C11'].value)
_ges = sum_status(('WON',) + OFF + OPP)
chk('Report!D11', (tot_wgt / _ges) if _ges else 0, REP['D11'].value)
for i in range(len(BANDS)):
    r = 45 + i
    chk(f'Report!B{r}', BANDS[i][2], REP[f'B{r}'].value)
    chk(f'Report!C{r}', band_cnt[i], REP[f'C{r}'].value)
    chk(f'Report!D{r}', band_rev[i], REP[f'D{r}'].value)
    chk(f'Report!E{r}', band_wgt[i], REP[f'E{r}'].value)
chk(f'Report!E{45+len(BANDS)}', tot_wgt, REP[f'E{45+len(BANDS)}'].value)

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
zvals = sorted([exp[r]['AK'] for r in raw if isnum(exp[r]['AK'])], reverse=True)
for i in range(10):
    r = 29 + i
    if i < len(zvals):
        v = zvals[i]
        first = next(x for x in range(6, LAST + 1) if exp[x]['AK'] == v)
        chk(f'Report!E{r} Volumen', raw[first]['I'], REP[f'E{r}'].value)
        chk(f'Report!B{r} Kunde', raw[first]['B'], REP[f'B{r}'].value)
        chk(f'Report!C{r} Kanton', raw[first]['C'], REP[f'C{r}'].value)
        # Projektstart: echtes Datum, sonst die bisherige grobe Monatsangabe
        _von = raw[first]['O']
        chk(f'Report!F{r} Projektstart',
            _von if isinstance(_von, datetime.datetime) else (raw[first]['H'] or ''),
            REP[f'F{r}'].value)
        _bis = raw[first]['P']
        chk(f'Report!G{r} Projektende',
            _bis if isinstance(_bis, datetime.datetime) else '', REP[f'G{r}'].value)
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
for i in range(len(BANDS)):
    r = 34 + i
    chk(f'ExecPDF!D{r}', BANDS[i][2], EX[f'D{r}'].value)
    chk(f'ExecPDF!E{r}', band_rev[i], EX[f'E{r}'].value)
    chk(f'ExecPDF!G{r}', band_wgt[i], EX[f'G{r}'].value)
_EXT = 34 + len(BANDS)
chk(f'ExecPDF!E{_EXT}', tot_rev, EX[f'E{_EXT}'].value)
chk(f'ExecPDF!G{_EXT}', tot_wgt, EX[f'G{_EXT}'].value)
for i in range(5):
    r = 14 + i
    if i >= len(zvals):
        chk(f'ExecPDF!C{r} leer', '', EX[f'C{r}'].value)
        continue
    v = zvals[i]
    first = next(x for x in range(6, LAST + 1) if exp[x]['AK'] == v)
    chk(f'ExecPDF!C{r} Kunde', raw[first]['B'], EX[f'C{r}'].value)
    chk(f'ExecPDF!G{r} Volumen', raw[first]['I'], EX[f'G{r}'].value)
    _von = raw[first]['O']
    chk(f'ExecPDF!E{r} Projektstart',
        _von if isinstance(_von, datetime.datetime) else (raw[first]['H'] or ''),
        EX[f'E{r}'].value)
    _bis = raw[first]['P']
    chk(f'ExecPDF!F{r} Projektende',
        _bis if isinstance(_bis, datetime.datetime) else '', EX[f'F{r}'].value)
    chk(f'ExecPDF!H{r} Segment', raw[first]['D'] or '', EX[f'H{r}'].value)

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
for i in range(len(BANDS)):
    r = 2 + i
    chk(f'_data!L{r}', BANDS[i][2], DAT[f'L{r}'].value)
    chk(f'_data!M{r}', band_rev[i], DAT[f'M{r}'].value)
    chk(f'_data!N{r}', band_wgt[i], DAT[f'N{r}'].value)
    chk(f'_data!O{r}', band_cnt[i], DAT[f'O{r}'].value)

# ====================== 6b) Umschluesselung: Skala und Protokoll
SKALA_SET = {0, 0.1, 0.3, 0.6, 0.9, 1.0}
for r in raw:
    if raw[r]['B'] in (None, ''):
        continue
    sv = raw[r]['S']
    # Hinweis: dass jeder Wert auf der Skala liegt, gilt fuer den Auslieferungs-
    # stand und wird in audit_struktur geprueft. Hier nicht, weil die
    # Verhaltenstests bewusst Werte ausserhalb der Skala setzen.
    # Dass die Umschluesselung den Gewichtungsfaktor erhaelt, gilt fuer den
    # Auslieferungsstand. Es wird deshalb in audit_struktur geprueft, nicht
    # hier - die Verhaltenstests aendern Wahrscheinlichkeiten absichtlich.

# Zuordnung bisher -> neu. Gewonnene Auftraege gehen auf 100 %, alle anderen
# auf die naechste Aggreko-Stufe mit demselben Gewichtungsfaktor.
def ziel(alt, status):
    if status == 'WON':
        return 1.0
    return {0.0: 0.0, 0.1: 0.1, 0.2: 0.3, 0.5: 0.3, 0.8: 0.6, 0.9: 0.9, 1.0: 0.9}[alt]


# Das Protokoll steht im File so, wie es beim Bau geschrieben wurde. Verglichen
# wird deshalb gegen die tatsaechlich vorhandenen Paare bisher -> neu.
PAARE = sorted({(round(raw[x]['AI'], 6), raw[x]['S'])
                for x in raw if raw[x]['B'] not in (None, '')
                and isnum(raw[x]['AI']) and isnum(raw[x]['S'])})
prot = find_prot = None
for r in range(1, W.max_row + 1):
    if str(W[f'A{r}'].value or '').startswith('bisher'):
        find_prot = r + 1
        break
assert find_prot, 'Protokolltabelle nicht gefunden'
# Das Protokoll ist eine Momentaufnahme des Baus. Geprueft wird deshalb, dass
# jede Zeile ein zulaessiges Paar bisher -> neu nennt und dass Anzahl und
# Gewichte zu genau diesem Paar passen - live aus der Pipeline gerechnet.
DATEI_PAARE = []
for _i in range(len(PAARE) + 4):
    _a, _b = W[f'A{find_prot + _i}'].value, W[f'B{find_prot + _i}'].value
    if not (isnum(_a) and isnum(_b)):
        break
    DATEI_PAARE.append((round(_a, 6), round(_b, 6)))
# Die Zahl der Zeilen wird bewusst nicht gegen die aktuellen Daten geprueft:
# das Protokoll haelt den Stand des Baus fest, spaetere Aenderungen an einer
# Wahrscheinlichkeit duerfen es nicht rueckwirkend umschreiben.
for i, (alt, neu) in enumerate(DATEI_PAARE):
    r = find_prot + i
    passt = [x for x in raw if raw[x]['B'] not in (None, '') and isnum(raw[x]['AI'])
             and round(raw[x]['AI'], 6) == alt and raw[x]['S'] == neu]
    n = len(passt)
    volsum = sum(exp[x]['AL'] for x in passt)
    if neu not in SKALA_SET:
        fails.append((f'W!B{r} Neuwert liegt nicht auf der Skala', 'Skalenwert', neu))
    checks += 1
    chk(f'W!E{r} Zeilen', n, W[f'E{r}'].value)
    chk(f'W!F{r} gewichtet bisher', volsum * faktor(alt), W[f'F{r}'].value)
    chk(f'W!G{r} gewichtet neu', volsum * faktor(neu), W[f'G{r}'].value)

# ============================== 7) Blatt "Herleitung & Formeln"
E_ = V['🔍 Herleitung & Formeln']


def rowof(name):
    return next(r for r in raw if raw[r]['B'] == name)


def find_rows(text, col='B'):
    """Zeilennummern im Erklaerungsblatt anhand der Beschriftung finden."""
    return [r for r in range(1, E_.max_row + 1)
            if str(E_[f'{col}{r}'].value or '').startswith(text)]


netto_aktiv = sum(exp[r]['AZ'] for r in raw if exp[r]['AP'] == 1)
STUFEN_ERW = {'②': netto_aktiv, '④': zeit_erf,
              '⑤': sum(1 for r in raw if exp[r]['AP'] == 1 and exp[r]['AS'] == 1),
              '⑥': tot_wgt, '⑦': akt_brutto}
for zeichen, erwartet in STUFEN_ERW.items():
    rr = find_rows(zeichen)
    assert len(rr) == 1, (zeichen, rr)
    chk(f'Herleitung Stufe {zeichen}', erwartet, E_[f'E{rr[0]}'].value)

# Die beiden Wasserfall-Beispiele muessen Zelle fuer Zelle der Pipeline entsprechen
starts = find_rows('Volumen wie erfasst')
assert len(starts) == 2, starts
vorhandene = {raw[r]['B'] for r in raw}
SPALTEN = ['I', None, 'Y', 'J', 'K', 'L', 'M', 'N', 'Z', 'O', 'P', 'G', 'S', 'AJ', 'Q', 'AH']
for start, kunde in zip(starts, ('Wincasa Solothurn', 'DPR Heat Loadbank')):
    hinweis = E_[f'E{start + len(SPALTEN)}'].value
    if kunde not in vorhandene:            # Beispielkunde entfernt -> Block muss warnen
        chk(f'Herleitung Hinweis «{kunde}»', '⚠ nicht in der Pipeline', hinweis)
        continue
    chk(f'Herleitung Hinweis «{kunde}»', '✔ gefunden', hinweis)
    src = rowof(kunde)
    for i, col in enumerate(SPALTEN):
        r = start + i
        if col is None:                       # Umrechnungsfaktor
            chk(f'Herleitung!E{r} Netto-Faktor', NETTO_FAKTOR, E_[f'E{r}'].value)
            continue
        want = exp[src][col] if col in exp[src] else raw[src][col]
        # INDEX liefert fuer eine leere Quellzelle 0 - das ist der korrekte Ausweis
        if want in (None, '') and E_[f'E{r}'].value == 0:
            want = 0
        chk(f'Herleitung!E{r} ({kunde}, Spalte {col})', want, E_[f'E{r}'].value)

# ================================================================== Ergebnis
print(f'Geprüfte Zellen/Werte : {checks}')
print(f'Abweichungen          : {len(fails)}')
for lbl, e, a in fails[:60]:
    print(f'   {lbl}\n       erwartet={e!r}\n       gefunden={a!r}')
sys.exit(1 if fails else 0)
