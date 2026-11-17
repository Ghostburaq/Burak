# -*- coding: utf-8 -*-
"""Erzeugt Erkennungstests fuer Sigma Unity.
Das Foto vom 17.11. beweist: Capture, Section, Instrumentation, Delay mit
hh:mm:ss, Reject und Capture Off werden von Unity akzeptiert, auf diesen
Zeilen steht kein Fehler. Beanstandet werden ausschliesslich die Load-Zeilen.
Deshalb variiert diese Testreihe nur die Load-Zeile."""
import os, re, sys
OUT = sys.argv[1]
O = 'Ø'

for d in ('A_Erkennungstest', 'B_P02_Varianten'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

MICRO = [(0, 10), (187, 10), (375, 10), (0, 10)]          # hoechstens 375 kW

def hms(s):
    s = int(s); return '%02d:%02d:%02d' % (s//3600, (s%3600)//60, s%60)

def bau(steps, pf, p4, kopf=None):
    """pf: Text des dritten Parameters. p4: 'zeit' oder 'null'."""
    L = list(kopf or [])
    L += ['Capture  On', 'Section  Heatrun', 'Instrumentation  Full']
    for kw, h in steps:
        vier = '00:00:00' if p4 == 'zeit' else '0'
        L += ['Load  %gkw %s %s No' % (kw, pf, vier), 'Delay  %s' % hms(h)]
    L += ['Reject', 'Capture  Off']
    return L

def schreib(pfad, lines, enc='cp1252', bom=False):
    data = ('\r\n'.join(lines) + '\r\n').encode(enc)
    if bom and enc == 'utf-8':
        data = b'\xef\xbb\xbf' + data
    open(pfad, 'wb').write(data); return len(data)

TESTS = [
 ('T1_Zeichen_repariert.tst',   '1cos'+O,   'zeit', 'cp1252', False,
  'Genau wie bisher, nur das Zeichen O-strich richtig. Aendert sonst nichts.'),
 ('T2_vierter_Parameter_Null.tst','1cos'+O,  'null', 'cp1252', False,
  'Wie T1, aber vierter Parameter 0 statt 00:00:00. Wahrscheinlichster Treffer.'),
 ('T3_pf_als_1Punkt0.tst',      '1.0cos'+O, 'null', 'cp1252', False,
  'Wie T2, aber 1.0 statt 1 beim Leistungsfaktor.'),
 ('T4_pf_1Punkt0_Zeit.tst',     '1.0cos'+O, 'zeit', 'cp1252', False,
  'Wie T3, aber vierter Parameter wieder 00:00:00.'),
 ('T5_wie_T2_als_UTF8.tst',     '1cos'+O,   'null', 'utf-8', False,
  'Inhalt wie T2, Datei aber UTF-8 ohne BOM. Nur falls T1 bis T4 scheitern.'),
 ('T6_wie_T2_als_UTF8_BOM.tst', '1cos'+O,   'null', 'utf-8', True,
  'Inhalt wie T2, UTF-8 mit BOM.'),
]

print('=== A  Erkennungstests, hoechstens 375 kW, rund eine Minute ===')
for name, pf, p4, enc, bom, zweck in TESTS:
    n = schreib(os.path.join(OUT, 'A_Erkennungstest', name), bau(MICRO, pf, p4), enc, bom)
    print('  %-32s %4d B  %-11s %s' % (name, n, enc + (' BOM' if bom else ''), zweck))

# ---------------------------------------------------------------- P02
SRC = '/home/user/Burak/ZRH12_Testprogramme/ZRH12_P02_Cold_Start_Ramp_Acceptance.tst'
RE_L = re.compile(r'^Load\s+(\d+(?:\.\d+)?)kw', re.I)
RE_D = re.compile(r'^Delay\s+(\d{1,2}):(\d{2}):(\d{2})')
steps, cur = [], None
for l in open(SRC, 'rb').read().decode('cp1252').split('\r\n'):
    if l.startswith("'"): continue
    m = RE_L.match(l)
    if m: cur = [float(m.group(1)), 0]; steps.append(cur); continue
    m = RE_D.match(l)
    if m and cur: cur[1] += int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3))

KOPF = ["'    ZRH12 P02 - COLD START RAMP ACCEPTANCE",
        "'    Rampe 187 auf 2298 kW in 30 s, 16 Schritte, fuenf Delays mit 2 s",
        "'    Mobil in Time AG - B. Uecoez"]
print()
print('=== B  P02 in den beiden wahrscheinlichsten Formen, %d Schritte ===' % len(steps))
for name, pf, p4 in [('P02_Form_T1_Zeit.tst', '1cos'+O, 'zeit'),
                     ('P02_Form_T2_Null.tst', '1cos'+O, 'null')]:
    n = schreib(os.path.join(OUT, 'B_P02_Varianten', name), bau(steps, pf, p4, KOPF))
    print('  %-26s %4d B' % (name, n))

print()
print('Kontrolle: %d Schritte, erster %g kW / %g s, letzter %g kW / %g s, Summe %g s'
      % (len(steps), steps[0][0], steps[0][1], steps[-1][0], steps[-1][1],
         sum(b for _, b in steps)))
