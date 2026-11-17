# -*- coding: utf-8 -*-
"""Liest die ZRH12-Testprogramme und erzeugt Eingabetabellen:
   Schritt, Abschnitt, Last in kW, Last in Prozent, cos phi, Haltezeit.
   Aufeinanderfolgende Delay-Zeilen werden zur Haltezeit eines Schritts summiert."""
import re, os, sys, glob, csv, json

REF = 2750.0                      # Bezugsleistung 100 Prozent
RE_L = re.compile(r'^Load\s+(\d+(?:\.\d+)?)kw\s+(\d+(?:\.\d+)?)cos', re.I)
RE_D = re.compile(r'^Delay\s+(\d{1,2}):(\d{2}):(\d{2})')
RE_S = re.compile(r"^'\s+SECTION\s+(\d+)\s*-\s*(.+?)\s*$")

def hms(sec):
    sec = int(round(sec))
    return "%02d:%02d:%02d" % (sec//3600, (sec%3600)//60, sec%60)

def parse(path):
    lines = open(path, 'rb').read().decode('cp1252').split('\r\n')
    steps, sec, cur = [], '', None
    for l in lines:
        m = RE_S.match(l)
        if m:
            sec = "%s %s" % (m.group(1), m.group(2)); continue
        if l.startswith("'"):
            continue
        m = RE_L.match(l)
        if m:
            cur = dict(sec=sec, kw=float(m.group(1)), pf=float(m.group(2)), hold=0.0)
            steps.append(cur); continue
        m = RE_D.match(l)
        if m and cur is not None:
            cur['hold'] += int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3))
    return steps

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
summary = {}
for p in sorted(glob.glob(os.path.join(SRC, '*.tst'))):
    name = os.path.basename(p).replace('.tst', '')
    steps = parse(p)
    rows = []
    for i, s in enumerate(steps, 1):
        rows.append([i, s['sec'], ('%g' % s['kw']),
                     ('%.1f' % (s['kw']/REF*100)).replace('.0', ''),
                     ('%.2f' % s['pf']), hms(s['hold'])])
    with open(os.path.join(OUT, name + '.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['Schritt', 'Abschnitt', 'Last kW', 'Last % von 2750 kW', 'cos phi', 'Haltezeit hh:mm:ss'])
        w.writerows(rows)
    total = sum(s['hold'] for s in steps)
    summary[name] = dict(steps=len(steps), hold=total, rows=rows,
                         maxkw=max(s['kw'] for s in steps))
    print("%-44s %3d Schritte | Haltezeit %s | max %g kW"
          % (name, len(steps), hms(total), summary[name]['maxkw']))
json.dump(summary, open(os.path.join(OUT, 'steps.json'), 'w'), ensure_ascii=False)
