# -*- coding: utf-8 -*-
"""Schreibt die ZRH12-Programme im Format, das Sigma Unity selbst erzeugt.

Beleg aus den Fotos vom 23.11.: im selben Skript gehen die Zeilen
    Load  2000.0kW 1.00cos<phi> 00:00:00 No
fehlerfrei durch, waehrend
    Load  14kw 1cos<phi> 00:00:00 No
Error 6 und Error 7 ausloesen. Unterschied: Dezimalstelle beim Lastwert,
grosses W in der Einheit, zwei Dezimalstellen beim Leistungsfaktor.
Alles andere ist in beiden Zeilen gleich und damit bestaetigt.
"""
import os, re, sys, glob

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
PHI = 'Ø'                      # Byte D8 in ANSI, Unity stellt es als phi dar

RE_L = re.compile(r'^Load\s+(\d+(?:\.\d+)?)kw\s+(\d+(?:\.\d+)?)cos', re.I)
RE_D = re.compile(r'^Delay\s+(\d{1,2}):(\d{2}):(\d{2})')
RE_C = re.compile(r'^(Capture|Section|Instrumentation|Reject|WorkIn|Averaging)\b', re.I)

def hms(s):
    s = int(s); return '%02d:%02d:%02d' % (s//3600, (s%3600)//60, s%60)

for p in sorted(glob.glob(os.path.join(SRC, '*.tst'))):
    name = os.path.basename(p).replace('.tst', '')
    lines = open(p, 'rb').read().decode('cp1252').split('\r\n')
    out, nload, ndelay = [], 0, 0
    for l in lines:
        if not l.strip() or l.startswith("'"):
            continue                                  # Kommentare raus
        m = RE_L.match(l)
        if m:
            kw, pf = float(m.group(1)), float(m.group(2))
            out.append('Load  %.1fkW %.2fcos%s 00:00:00 No' % (kw, pf, PHI))
            nload += 1; continue
        m = RE_D.match(l)
        if m:
            out.append('Delay  %s' % hms(int(m.group(1))*3600 +
                                        int(m.group(2))*60 + int(m.group(3))))
            ndelay += 1; continue
        if RE_C.match(l):
            out.append(re.sub(r'\s+', '  ', l.strip()))
            continue
        raise SystemExit('unbekannte Zeile in %s: %r' % (name, l))

    data = ('\r\n'.join(out) + '\r\n').encode('cp1252')
    dst = os.path.join(OUT, name.replace('ZRH12_', 'ZRH12_Unity_') + '.tst')
    open(dst, 'wb').write(data)
    print('%-46s %3d Load | %3d Delay | %5d B' %
          (os.path.basename(dst), nload, ndelay, len(data)))

# Kleiner Test, ob Unity Kommentare mit Hochkomma akzeptiert
t = ["'    Test ob Unity diese Kommentarzeile akzeptiert",
     'Capture  On', 'Section  Heatrun', 'Instrumentation  Full',
     'Load  0.0kW 1.00cos%s 00:00:00 No' % PHI, 'Delay  00:00:10',
     'Load  187.0kW 1.00cos%s 00:00:00 No' % PHI, 'Delay  00:00:10',
     'Load  0.0kW 1.00cos%s 00:00:00 No' % PHI, 'Delay  00:00:10',
     'Reject', 'Capture  Off']
open(os.path.join(OUT, 'TEST_Kommentar_erlaubt.tst'), 'wb').write(
    ('\r\n'.join(t) + '\r\n').encode('cp1252'))
print('\nTEST_Kommentar_erlaubt.tst  geschrieben, pruefft ob Zeile 1 mit Hochkomma durchgeht')
