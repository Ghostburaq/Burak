# -*- coding: utf-8 -*-
"""Prueft die Rampenbloecke der ZRH12-Programme gegen die Behauptungen im Kopf."""
import re, sys, os, glob

OVH = 0.62
RE_L = re.compile(r'^Load\s+(\d+(?:\.\d+)?)kw', re.I)
RE_D = re.compile(r'^Delay\s+(\d{1,2}):(\d{2}):(\d{2})')

def parse(path):
    lines = open(path, 'rb').read().decode('cp1252').split('\r\n')
    seq = []
    for i, l in enumerate(lines, 1):
        if l.startswith("'"):
            continue
        m = RE_L.match(l)
        if m:
            seq.append((i, 'L', float(m.group(1))))
            continue
        m = RE_D.match(l)
        if m:
            seq.append((i, 'D', int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3))))
    return lines, seq

def ramps(seq, min_steps=4):
    """Zusammenhaengende Bloecke steigender Last mit kurzen Delays."""
    out, cur = [], []
    for k in range(len(seq)):
        if seq[k][1] != 'L':
            continue
        nxt = seq[k+1] if k+1 < len(seq) else None
        d = nxt[2] if nxt and nxt[1] == 'D' else None
        if cur and seq[k][2] > cur[-1][1] and cur[-1][2] is not None and cur[-1][2] <= 3:
            cur.append((seq[k][0], seq[k][2], d))
        else:
            if len(cur) >= min_steps:
                out.append(cur)
            cur = [(seq[k][0], seq[k][2], d)]
    if len(cur) >= min_steps:
        out.append(cur)
    return out

for p in sorted(glob.glob(os.path.join(sys.argv[1], '*.tst'))):
    lines, seq = parse(p)
    print("=" * 78)
    print(os.path.basename(p))
    for blk in ramps(seq):
        start, end = blk[0][1], blk[-1][1]
        steps = len(blk) - 1
        diffs = [round(blk[i+1][1] - blk[i][1], 1) for i in range(steps)]
        # Zeit vom ersten bis zum letzten Sollwert
        t = sum(blk[i][2] for i in range(steps) if blk[i][2] is not None) + steps * OVH
        uniq = sorted(set(diffs))
        dl = sorted(set(blk[i][2] for i in range(steps)))
        print("  Zeile %-4d %7.1f -> %7.1f kW | %2d Schritte | Sprung %s | Delays %s"
              % (blk[0][0], start, end, steps,
                 ("%g" % uniq[0]) if len(uniq) == 1 else "%g..%g" % (uniq[0], uniq[-1]), dl))
        print("       Spanne %.1f kW, Mittel %.2f kW/Schritt, Rampenzeit %.2f s = %.1f kW/s"
              % (end - start, (end - start) / steps, t, (end - start) / t if t else 0))
        two = [blk[i][2] for i in range(steps)].count(2)
        if two:
            print("       davon %d Delays mit 2 s" % two)
