# -*- coding: utf-8 -*-
"""Linter fuer Sigma-Testprogramme (.tst). Prueft Syntax, Zeitformate,
Schrittweiten und die im Kopf behaupteten Laufzeiten."""
import re, sys, os, glob

STEP_OVERHEAD = 0.62        # gemessene Schrittausfuehrungszeit minus Delay

RE_LOAD  = re.compile(r'^Load\s+(\d+(?:\.\d+)?)(kw|kW|KW|kva|kVA)\s+'
                      r'(\d+(?:\.\d+)?)cos\xd8\s+(\S+)\s+(Yes|No)\s*$')
RE_DELAY = re.compile(r'^Delay\s+(\S+)\s*$')
RE_HMS   = re.compile(r'^(\d{1,2}):(\d{2}):(\d{2})$')

def hms(v):
    m = RE_HMS.match(v)
    if not m:
        return None
    h, mi, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if mi > 59 or s > 59:
        return ('RANGE', h * 3600 + mi * 60 + s)
    return ('OK', h * 3600 + mi * 60 + s)

def fmt(sec):
    sec = int(round(sec))
    return "%d min %02d s" % (sec // 60, sec % 60)

def lint(path):
    raw = open(path, 'rb').read()
    txt = raw.decode('cp1252')
    lines = txt.split('\r\n')
    if lines and lines[-1] == '':
        lines.pop()

    errs, warns, info = [], [], []

    if b'\xef\xbb\xbf' in raw[:3]:
        errs.append((0, "BOM am Dateianfang"))
    if raw.count(b'\n') != raw.count(b'\r\n'):
        errs.append((0, "gemischte Zeilenenden"))
    for i, l in enumerate(lines, 1):
        if ',' in l and not l.startswith("'"):
            errs.append((i, "Komma in Befehlszeile: %r" % l))
        if l != l.rstrip():
            warns.append((i, "Leerzeichen am Zeilenende"))
        if '\t' in l:
            warns.append((i, "Tabulator in Zeile"))

    loads, delays = [], []
    cmds = []
    for i, l in enumerate(lines, 1):
        if l.startswith("'") or l.strip() == '':
            continue
        head = l.split()[0] if l.split() else ''
        cmds.append((i, head, l))
        if head == 'Load':
            m = RE_LOAD.match(l)
            if not m:
                errs.append((i, "Load-Syntax weicht ab: %r" % l))
                continue
            r = hms(m.group(4))
            if r is None:
                errs.append((i, "Load Parameter 3 ist keine hh:mm:ss Zeit: %r" % m.group(4)))
            elif r[0] == 'RANGE':
                errs.append((i, "Load Parameter 3 ausserhalb des Bereichs: %r" % m.group(4)))
            loads.append((i, float(m.group(1)), m.group(2), float(m.group(3)), m.group(5)))
        elif head == 'Delay':
            m = RE_DELAY.match(l)
            if not m:
                errs.append((i, "Delay-Syntax weicht ab: %r" % l))
                continue
            r = hms(m.group(1))
            if r is None:
                errs.append((i, "Delay ist keine hh:mm:ss Zeit: %r" % m.group(1)))
            elif r[0] == 'RANGE':
                errs.append((i, "Delay ausserhalb des Bereichs (mm oder ss > 59): %r -> %s"
                                % (m.group(1), fmt(r[1]))))
                delays.append((i, r[1]))
            else:
                delays.append((i, r[1]))
        elif head in ('Capture', 'Section', 'Instrumentation', 'WorkIn', 'Reject'):
            pass
        else:
            errs.append((i, "unbekannter Befehl: %r" % l))

    # Struktur
    heads = [c[1] for c in cmds]
    if heads[:1] != ['Capture']:
        warns.append((cmds[0][0] if cmds else 0, "Datei beginnt nicht mit Capture On"))
    if heads[-2:] != ['Reject', 'Capture']:
        warns.append((cmds[-1][0] if cmds else 0, "Datei endet nicht mit Reject + Capture Off"))
    if 'WorkIn' not in heads:
        info.append((0, "kein WorkIn-Befehl (Offenbach-Programm hatte 'WorkIn kW')"))

    # Load ohne folgendes Delay
    for n, (i, h, l) in enumerate(cmds):
        if h == 'Load':
            nxt = cmds[n + 1][1] if n + 1 < len(cmds) else None
            if nxt != 'Delay':
                errs.append((i, "Load ohne folgendes Delay"))

    # cos phi und Einheiten einheitlich?
    units = sorted({u for _, _, u, _, _ in loads})
    pfs   = sorted({p for _, _, _, p, _ in loads})
    flags = sorted({f for _, _, _, _, f in loads})
    if len(units) > 1:
        warns.append((0, "uneinheitliche Einheitenschreibweise: %s" % units))
    if len(pfs) > 1:
        warns.append((0, "unterschiedliche cos phi Werte: %s" % pfs))
    if len(flags) > 1:
        warns.append((0, "unterschiedliche Yes/No Flags: %s" % flags))

    # Laufzeit gegen Kopfangabe
    total_delay = sum(d for _, d in delays)
    calc = total_delay + len(loads) * STEP_OVERHEAD
    claim = None
    for i, l in enumerate(lines, 1):
        m = re.search(r'Expected total run time:\s*(\d+)\s*(?:min|h)\s*(\d+)?\s*s?', l)
        if m and 'min' in l:
            claim = int(m.group(1)) * 60 + int(m.group(2) or 0)
            claim_line = i
    if claim is not None:
        if abs(calc - claim) > 15:
            errs.append((claim_line, "Kopfangabe Laufzeit %s weicht ab, berechnet %s"
                                     % (fmt(claim), fmt(calc))))
        else:
            info.append((claim_line, "Laufzeit Kopf %s, berechnet %s" % (fmt(claim), fmt(calc))))
    else:
        warns.append((0, "keine Laufzeitangabe im Kopf"))

    # Abschnittsnummern in Kommentaren
    secs = [int(m.group(1)) for l in lines
            for m in [re.search(r"^'\s+SECTION\s+(\d+)", l)] if m]
    if secs != sorted(secs) or (secs and secs != list(range(secs[0], secs[0] + len(secs)))):
        warns.append((0, "Abschnittsnummern nicht fortlaufend: %s" % secs))

    return dict(path=path, lines=len(lines), loads=loads, delays=delays,
                total_delay=total_delay, calc=calc, errs=errs, warns=warns, info=info)

if __name__ == '__main__':
    for p in sorted(glob.glob(os.path.join(sys.argv[1], '*.tst'))):
        r = lint(p)
        print("=" * 78)
        print(os.path.basename(p), "| %d Zeilen | %d Load | %d Delay | Haltezeit %s | mit Overhead %s"
              % (r['lines'], len(r['loads']), len(r['delays']),
                 fmt(r['total_delay']), fmt(r['calc'])))
        for tag, items in (("FEHLER", r['errs']), ("WARNUNG", r['warns']), ("INFO", r['info'])):
            for ln, msg in items:
                print("  %-8s %s%s" % (tag, ("Zeile %d: " % ln) if ln else "", msg))
