#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formel-Vollabgleich: jede Formel der Nutzerdatei gegen die strukturell
korrekte Referenzdatei (Repo-Stand des Ausbaus).

In der Nutzerdatei wurde die Pipelinespalte AI («Wahr. % bisher»)
geloescht — alle Pipelinespalten ab AJ liegen dort eine Position weiter
links, und Excel hat saemtliche Bezuege nachgezogen. Der Abgleich
uebersetzt deshalb die Referenzformeln mit demselben Versatz und meldet
jede Formel, die darueber hinaus abweicht.

Pipeline-Zeilenformeln werden als Muster verglichen (Zeilennummern
normalisiert), weil die Nutzerdatei andere Datenzeilen traegt.
"""
import re
import sys
import openpyxl
from openpyxl.utils import column_index_from_string, get_column_letter

REF = 'CH_MiT_Strom_Customer_CEO_CFO_MASTER__2_.xlsx'   # Repo-Stand
UP = 'upload_user.xlsx' if len(sys.argv) < 2 else sys.argv[1]
PIPE = 'MiT Strom Pipeline'

AI = column_index_from_string('AI')


def map_col(buchstabe):
    """Pipelinespalte der Referenz -> Spalte in der Nutzerdatei."""
    i = column_index_from_string(buchstabe)
    if i < AI:
        return buchstabe
    if i == AI:
        return None          # geloescht
    return get_column_letter(i - 1)


ZELLBEZUG = re.compile(r"(\$?)([A-Z]{1,3})(\$?)(\d{1,7})")


def uebersetze(formel, auf_pipeline):
    """Referenzformel in die Spaltenwelt der Nutzerdatei uebersetzen.
    Nur Bezuege, die zur Pipeline gehoeren, werden verschoben:
    entweder ausdruecklich ('MiT Strom Pipeline'!...) oder — wenn die
    Formel auf der Pipeline selbst steht — auch nackte Bezuege."""
    teile = re.split(r"('(?:''|[^'])*'!)", formel)
    out = []
    pipeline_kontext = auf_pipeline
    for t in teile:
        if t.startswith("'") and t.endswith("!"):
            pipeline_kontext = (PIPE in t)
            out.append(t)
            continue
        if pipeline_kontext:
            def ersetze(m):
                neu = map_col(m.group(2))
                if neu is None:
                    return m.group(0) + '⟪GELOESCHT⟫'
                return m.group(1) + neu + m.group(3) + m.group(4)
            t = ZELLBEZUG.sub(ersetze, t)
        if not auf_pipeline:
            pipeline_kontext = False
        out.append(t)
    return ''.join(out)


def muster(formel):
    """Zeilennummern neutralisieren (fuer Pipeline-Zeilenformeln)."""
    return re.sub(r'(?<![0-9.])\d{1,3}(?![0-9.%])', 'r', formel)


ref = openpyxl.load_workbook(REF)
up = openpyxl.load_workbook(UP)

befunde = []
geprueft = 0

# ---------------------------------------------- Nicht-Pipeline-Blaetter
for name in ref.sheetnames:
    if name == PIPE:
        continue
    ws_r, ws_u = ref[name], up[name]
    max_r = max(ws_r.max_row, ws_u.max_row)
    max_c = max(ws_r.max_column, ws_u.max_column)
    for r in range(1, max_r + 1):
        for c in range(1, max_c + 1):
            fr = ws_r.cell(row=r, column=c).value
            fu = ws_u.cell(row=r, column=c).value
            fr_f = isinstance(fr, str) and fr.startswith('=')
            fu_f = isinstance(fu, str) and fu.startswith('=')
            if not fr_f and not fu_f:
                continue
            geprueft += 1
            koord = f'{name}!{get_column_letter(c)}{r}'
            if fr_f and not fu_f:
                befunde.append((koord, 'FORMEL FEHLT', str(fr)[:70], str(fu)[:40]))
                continue
            if fu_f and not fr_f:
                befunde.append((koord, 'FORMEL NEU', str(fr)[:40], str(fu)[:70]))
                continue
            soll = uebersetze(fr, auf_pipeline=False)
            if soll != fu:
                befunde.append((koord, 'ABWEICHUNG', soll[:80], fu[:80]))

# ------------------------------------------------------- Pipeline selbst
ws_r, ws_u = ref[PIPE], up[PIPE]
# Formel-Muster je Referenzspalte (aus Zeile 20, einer normalen Datenzeile)
for c in range(1, ws_r.max_column + 1):
    buchst_r = get_column_letter(c)
    buchst_u = map_col(buchst_r)
    if buchst_u is None:
        continue
    fr = ws_r[f'{buchst_r}20'].value
    if not (isinstance(fr, str) and fr.startswith('=')):
        continue
    geprueft += 1
    soll = muster(uebersetze(fr, auf_pipeline=True))
    # Jede Zeile der Nutzerdatei muss diesem Muster folgen.
    falsch = []
    leer = 0
    for r in range(6, 861):
        fu = ws_u[f'{buchst_u}{r}'].value
        if not (isinstance(fu, str) and fu.startswith('=')):
            leer += 1
            continue
        if muster(fu) != soll:
            falsch.append((r, fu[:70]))
    if leer:
        befunde.append((f'{PIPE}!{buchst_u} (Ref {buchst_r})', 'ZEILEN OHNE FORMEL',
                        f'{leer} von 855 Zeilen leer', soll[:60]))
    for r, fu in falsch[:3]:
        befunde.append((f'{PIPE}!{buchst_u}{r}', 'MUSTER-ABWEICHUNG', soll[:70], fu))
    if len(falsch) > 3:
        befunde.append((f'{PIPE}!{buchst_u}', '…', f'{len(falsch)} Zeilen weichen ab', ''))

print(f'Verglichene Formelzellen: {geprueft}')
print(f'Abweichungen: {len(befunde)}')
for koord, art, soll, ist in befunde[:80]:
    print(f'\n[{art}] {koord}')
    print(f'   soll: {soll}')
    print(f'   ist : {ist}')
if len(befunde) > 80:
    print(f'... und {len(befunde) - 80} weitere')
