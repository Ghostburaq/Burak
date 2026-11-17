# -*- coding: utf-8 -*-
"""Vergleicht ausschliesslich die Befehlszeilen von Original und Korrektur."""
import os, sys, glob
A, B = sys.argv[1], sys.argv[2]
def cmds(p):
    return [l.rstrip() for l in open(p, 'rb').read().decode('cp1252').split('\r\n')
            if l.strip() and not l.startswith("'")]
ok = True
for p in sorted(glob.glob(os.path.join(A, '*.tst'))):
    n = os.path.basename(p)
    a, b = cmds(p), cmds(os.path.join(B, n))
    if a == b:
        print("  %-42s %3d Befehle identisch" % (n, len(a)))
    else:
        ok = False
        print("  %-42s ABWEICHUNG" % n)
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                print("      Befehl %d:  %r  ->  %r" % (i + 1, x, y))
        if len(a) != len(b):
            print("      Anzahl: %d -> %d" % (len(a), len(b)))
print("\nTestsubstanz unveraendert:" , "ja" if ok else "NEIN, siehe oben")
