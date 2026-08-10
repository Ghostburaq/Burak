#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fuenf vollstaendige Durchgaenge: Datei jedes Mal von der Quelle neu bauen,
neu berechnen und alle Pruefungen laufen lassen. Zusaetzlich wird geprueft, ob
jeder Durchgang exakt dieselben Zahlen liefert (Determinismus) und ob ein
zweites Neuberechnen nichts mehr veraendert (Idempotenz).
"""
import subprocess, sys, shutil, json, hashlib, os, openpyxl

F = 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
# Neuberechnung braucht LibreOffice. Pfad zum Hilfsskript per Umgebungsvariable
# RECALC ueberschreibbar, damit der Lauf auch auf einem anderen Rechner geht.
RECALC = os.environ.get('RECALC', '/root/.claude/skills/xlsx/scripts/recalc.py')
# build_layout.py braucht die gerechneten Werte (es misst, was in der Zelle
# steht) - deshalb wird vorher einmal neu berechnet und danach noch einmal.
STUFEN = ['build_master.py', 'build_governance.py',
          'build_erklaerung.py', 'build_umschluesselung.py']
LAYOUT = 'build_layout.py'
PRUEF = ['audit_static.py', 'audit_values.py', 'audit_struktur.py',
         'audit_fragen.py', 'audit_layout.py', 'audit_abnahme.py']
PASSES = 5
BEHAVIOUR_IN = {1, PASSES}          # der lange Verhaltenslauf im ersten und letzten Durchgang

fehler = []
fingerprints = []


def run(cmd, timeout=900):
    r = subprocess.run([sys.executable] + cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def fingerprint(datei):
    """Hash ueber alle berechneten Werte - unabhaengig von Formatierung."""
    v = openpyxl.load_workbook(datei, data_only=True)
    h = hashlib.sha256()
    for ws in v.worksheets:
        h.update(ws.title.encode())
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    h.update(f'{c.coordinate}={c.value!r};'.encode())
    return h.hexdigest()[:16]


for p in range(1, PASSES + 1):
    print(f'\n{"=" * 74}\nDURCHGANG {p} von {PASSES}\n{"=" * 74}')

    # --- neu bauen
    for stufe in STUFEN:
        rc, out, err = run([stufe])
        if rc != 0:
            fehler.append(f'D{p}: {stufe} fehlgeschlagen: {err.strip()[-300:]}')
            print(f'  ✗ {stufe}')
            break
        print(f'  ✔ {stufe}')
    else:
        def neu_berechnen(runde):
            rc_, out_, err_ = run([RECALC, F, '400'])
            try:
                j_ = json.loads(out_)
            except Exception:
                j_ = {'status': 'PARSE-FEHLER', 'raw': out_[-200:]}
            if j_.get('status') != 'success':
                fehler.append(f'D{p}: Neuberechnung {runde}: {json.dumps(j_)[:300]}')
                print(f'  ✗ Neuberechnung {runde}: {j_.get("status")}')
                return False
            print(f'  ✔ Neuberechnung {runde} — {j_["total_formulas"]} Formeln, '
                  f'{j_["total_errors"]} Fehler')
            return True

        neu_berechnen(1)
        rc, out, err = run([LAYOUT])
        if rc != 0:
            fehler.append(f'D{p}: {LAYOUT} fehlgeschlagen: {err.strip()[-300:]}')
            print(f'  ✗ {LAYOUT}')
        else:
            print(f'  ✔ {LAYOUT}')
        neu_berechnen(2)

        # --- Pruefungen
        for pruef in PRUEF:
            rc, out, err = run([pruef])
            kurz = [l for l in out.splitlines() if l.strip()][-1] if out.strip() else '(keine Ausgabe)'
            if rc != 0:
                fehler.append(f'D{p}: {pruef}: {out.strip()[-400:]}')
                print(f'  ✗ {pruef}: {kurz}')
            else:
                print(f'  ✔ {pruef}: {kurz}')

        if p in BEHAVIOUR_IN:
            rc, out, err = run(['audit_behaviour.py'], timeout=1800)
            kurz = [l for l in out.splitlines() if l.strip()][-1] if out.strip() else '?'
            if rc != 0:
                fehler.append(f'D{p}: audit_behaviour.py: {out.strip()[-600:]}')
                print(f'  ✗ audit_behaviour.py: {kurz}')
            else:
                print(f'  ✔ audit_behaviour.py: {kurz}')

        fp = fingerprint(F)
        fingerprints.append(fp)
        print(f'  · Fingerabdruck der berechneten Werte: {fp}')

# --- Determinismus
print(f'\n{"=" * 74}\nDETERMINISMUS\n{"=" * 74}')
if len(set(fingerprints)) == 1:
    print(f'  ✔ Alle {len(fingerprints)} Durchgänge liefern identische Zahlen ({fingerprints[0]})')
else:
    fehler.append(f'Durchgänge liefern unterschiedliche Zahlen: {fingerprints}')
    print(f'  ✗ Abweichende Fingerabdrücke: {fingerprints}')

# --- Idempotenz: nochmals neu berechnen darf nichts aendern
print(f'\n{"=" * 74}\nIDEMPOTENZ\n{"=" * 74}')
shutil.copy(F, 'idem.xlsx')
rc, out, err = run([RECALC, 'idem.xlsx', '400'])
fp2 = fingerprint('idem.xlsx')
if fp2 == fingerprints[-1]:
    print(f'  ✔ Zweites Neuberechnen ändert nichts ({fp2})')
else:
    fehler.append(f'Idempotenz verletzt: {fingerprints[-1]} -> {fp2}')
    print(f'  ✗ Werte ändern sich beim zweiten Neuberechnen: {fingerprints[-1]} -> {fp2}')
os.remove('idem.xlsx')

print(f'\n{"=" * 74}')
if fehler:
    print(f'{len(fehler)} BEFUNDE:')
    for f_ in fehler:
        print('  ', f_)
else:
    print(f'ALLE {PASSES} DURCHGÄNGE FEHLERFREI — deterministisch und idempotent.')
print('=' * 74)
sys.exit(1 if fehler else 0)
