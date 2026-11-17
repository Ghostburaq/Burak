# -*- coding: utf-8 -*-
"""Korrigiert die sechs ZRH12-Testprogramme. Jede Ersetzung wird geprueft,
eine nicht gefundene Zeile bricht den Lauf ab."""
import os, sys, io

SRC = sys.argv[1]
DST = sys.argv[2]
os.makedirs(DST, exist_ok=True)

def load(name):
    return open(os.path.join(SRC, name), 'rb').read().decode('cp1252').split('\r\n')

def save(name, lines):
    txt = '\r\n'.join(l.rstrip() for l in lines)
    if not txt.endswith('\r\n'):
        txt += '\r\n'
    open(os.path.join(DST, name), 'wb').write(txt.encode('cp1252'))

def rep(lines, old, new, tag):
    """Ersetzt genau eine Zeile durch eine oder mehrere Zeilen."""
    hits = [i for i, l in enumerate(lines) if l.rstrip() == old.rstrip()]
    assert len(hits) == 1, "%s: %d Treffer fuer %r" % (tag, len(hits), old)
    i = hits[0]
    return lines[:i] + (new if isinstance(new, list) else [new]) + lines[i+1:]

def ins_before(lines, anchor, block, tag):
    hits = [i for i, l in enumerate(lines) if l.rstrip() == anchor.rstrip()]
    assert len(hits) == 1, "%s: %d Treffer fuer Anker %r" % (tag, len(hits), anchor)
    i = hits[0]
    return lines[:i] + block + lines[i:]

changes = []

# ---------------------------------------------------------------- P01
n = 'ZRH12_P01_Step_Timing_Diagnostic.tst'
L = load(n)
L = rep(L, "'      Block A has 12 steps, below the 16 step figure.", [
  "'      Step execution time = delay + a fixed overhead. Read the overhead as",
  "'        overhead = (measured block time - sum of delays) / number of steps",
  "'",
  "'      Block A, 12 steps, 11 delays of 1 s, below the 16 step figure:"], 'P01 blockA')
L = rep(L, "'        about 12 s  -> candidate A, the step limit",
           "'        about 11 to 12 s -> no overhead, candidate A, the step limit", 'P01 a1')
L = rep(L, "'        about 19 s  -> candidate B, the control bus",
           "'        about 18 to 19 s -> overhead 0.6 s, candidate B, the control bus", 'P01 a2')
L = rep(L, "'      Block B has 24 steps, above the figure. Compare against block A.", [
  "'      Block B, 24 steps, 23 delays of 1 s, above the figure:",
  "'        about 23 s       -> no overhead",
  "'        about 38 s       -> overhead 0.6 s",
  "'        An overhead per step that is LARGER in block B than in block A confirms",
  "'        candidate A. An identical overhead in both blocks confirms candidate B."], 'P01 blockB')
L = rep(L, "'      Block C has zero delay and measures the floor of the control system.", [
  "'      Block C, 12 steps, zero delay, measures the floor directly:",
  "'        block time divided by 12 is the bare overhead per step."], 'P01 blockC')
L = rep(L, "'      Place the cursors on the 187 kW plateau and on the 1500 kW plateau of each", [
  "'      Cursor placement, both cursors on a stable plateau:",
  "'        cursor 1 on the LAST sample of the 187 kW plateau, that is immediately",
  "'                 before the first step of the block,",
  "'        cursor 2 on the FIRST sample of the 1500 kW plateau.",
  "'      Do not place a cursor on a rising edge and do not include the 10 s hold at",
  "'      187 kW in the reading."], 'P01 cursor')
L = rep(L, "'      block. Sigma PC also shows elapsed time since the last load was applied in",
           "'      Sigma PC also shows elapsed time since the last load was applied in", 'P01 sigma')
save(n, L); changes.append((n, 'Diagnoseanleitung praezisiert, Cursorsetzung eindeutig'))

# ---------------------------------------------------------------- P02
n = 'ZRH12_P02_Cold_Start_Ramp_Acceptance.tst'
L = load(n)
L = rep(L, "'      Expected with 16 steps of 132 kW: 29.9 s = 70.6 kW/s",
           "'      Expected with 16 steps of about 132 kW: 29.9 s = 70.6 kW/s", 'P02 req')
L = rep(L, "'      therefore take 46.9 s whatever the delay says. 16 steps of 132 kW deliver the",
           "'      therefore take 46.9 s whatever the delay says. 16 steps deliver the", 'P02 why1')
L = rep(L, "'      timed load steps. Four delays are set to 2 s to land on 30 s rather than 26 s.",
           "'      timed load steps. Five delays are set to 2 s to land on 30 s rather than 25 s.", 'P02 why2')
L = ins_before(L, "'    LOAD STEP SIZE", [
  "'    MARGIN CHECK BEFORE THE ACCEPTANCE RUN",
  "'      Ramp time = 16 x overhead + 15 s + n, where n is the number of 2 s delays.",
  "'      This file is set to n = 5, which gives 29.9 s at an overhead of 0.62 s.",
  "'      That is only 0.1 s inside the 30 s requirement, so confirm the overhead",
  "'      with P01 first and set n from the measured value:",
  "'        overhead up to 0.62 s   -> n = 5, ramp 29.0 to 29.9 s",
  "'        overhead 0.63 to 0.68 s -> n = 4, ramp 29.1 to 29.9 s",
  "'        overhead 0.69 to 0.74 s -> n = 3, ramp 29.0 to 29.8 s",
  "'        overhead 0.75 to 0.80 s -> n = 2, ramp 29.0 to 29.8 s",
  "'      Take the 2 s delays out from the end of the ramp first, that is step 14,",
  "'      then 11, then 8, so the early part of the ramp stays unchanged.",
  "'"], 'P02 margin')
L = rep(L, "'      Cursor 1 on the 187 kW plateau, cursor 2 on the 2298 kW plateau in section 3.", [
  "'      Cursor 1 on the LAST sample of the 187 kW plateau in section 1, that is",
  "'      immediately before the first ramp step. Cursor 2 on the FIRST sample of the",
  "'      2298 kW plateau at the end of section 2."], 'P02 cursor')
L = rep(L, "'      on a rising edge.", [
  "'      on a rising edge.",
  "'      The 17 s hold at 187 kW is settling time, not part of the ramp. If cursor 1",
  "'      is placed at the START of that plateau the reading comes out 17 s too long",
  "'      and the ramp appears to fail when it does not."], 'P02 trap')
L = rep(L, "'      16 steps of 132 kW. Steps 2, 5, 8, 11, 14 carry a 2 s delay.", [
  "'      16 steps, 15 of 132 kW and one of 131 kW, to land exactly on 2298 kW.",
  "'      Steps 2, 5, 8, 11, 14 carry a 2 s delay, five in total."], 'P02 sec2')
L = rep(L, "'    SECTION 4 - controlled return to zero",
           "'    SECTION 3 - controlled return to zero", 'P02 s4')
L = rep(L, "'    SECTION 5 - cool-down", "'    SECTION 4 - cool-down", 'P02 s5')
save(n, L); changes.append((n, 'Vier/fuenf 2-s-Delays korrigiert, Abschnitte 3 und 4, Cursorfalle, Margentabelle'))

# ---------------------------------------------------------------- P03
n = 'ZRH12_P03_Ramp_and_L3_Transients.tst'
L = load(n)
L = rep(L, "'      1. Ramp section rebuilt from 30 steps to 16 steps of 132 kW. Measured step",
           "'      1. Ramp section rebuilt from 30 steps to 16 steps of about 132 kW. Measured", 'P03 c1')
L = rep(L, "'         bank fully warm. The difference against the section 5 reading at 0 s is the",
           "'         bank fully warm. The difference against the section 4 reading at 0 s is the", 'P03 c4')
L = rep(L, "'      16 steps of 132 kW, four delays at 2 s. Expected 29.9 s against 30 s.", [
  "'      16 steps, 15 of 132 kW and one of 131 kW, to land exactly on 2298 kW.",
  "'      Steps 2, 5, 8, 11, 14 carry a 2 s delay, five in total.",
  "'      Expected 29.9 s against the required 30 s.",
  "'      Cursor 1 on the LAST sample of the 187 kW plateau, cursor 2 on the FIRST",
  "'      sample of the 2298 kW plateau. The 17 s hold in section 1 is settling time",
  "'      and is not part of the ramp. Placing cursor 1 at the start of that plateau",
  "'      makes the reading 17 s too long."], 'P03 sec2')
for old, new, tag in [
    ("'    SECTION 4 - continue to 2721 kW",        "'    SECTION 3 - continue to 2721 kW", 's4'),
    ("'    SECTION 5 - main plateau 2721 kW, 180 s","'    SECTION 4 - main plateau 2721 kW, 180 s", 's5'),
    ("'    SECTION 6 - controlled return to zero",  "'    SECTION 5 - controlled return to zero", 's6'),
    ("'    SECTION 7 - L3 step transients",         "'    SECTION 6 - L3 step transients", 's7'),
    ("'    SECTION 8 - thermal reference step",     "'    SECTION 7 - thermal reference step", 's8'),
    ("'    SECTION 9 - cool-down",                  "'    SECTION 8 - cool-down", 's9'),
    ("'      Same 2721 kW as section 5, bank now fully warm after the transient block.",
     "'      Same 2721 kW as section 4, bank now fully warm after the transient block.", 'ref1'),
    ("'      Difference against the section 5 reading at 0 s is the full temperature",
     "'      Difference against the section 4 reading at 0 s is the full temperature", 'ref2'),
    ("'      RevA held only 45 s and hid this effect.",
     "'      RevA held only 45 s and hid this effect.", 'noop')]:
    if tag != 'noop':
        L = rep(L, old, new, 'P03 ' + tag)
save(n, L); changes.append((n, 'Vier/fuenf 2-s-Delays, Abschnitte 3 bis 8 durchnummeriert, Querverweise, Cursorfalle'))

# ---------------------------------------------------------------- P04 / P05
for n in ('ZRH12_P04_Overshoot_and_Thermal.tst', 'ZRH12_P05_Step_Load_ISO8528.tst'):
    save(n, load(n)); changes.append((n, 'nur Leerzeichen am Zeilenende entfernt'))

# ---------------------------------------------------------------- P06
n = 'ZRH12_P06_Full_Load_Heat_Run.tst'
L = load(n)
L = rep(L, "Delay  00:60:00", "Delay  01:00:00", 'P06 delay')
save(n, L); changes.append((n, 'Delay 00:60:00 auf 01:00:00 korrigiert'))

print("Korrigiert:")
for a, b in changes:
    print("  %-42s %s" % (a, b))
