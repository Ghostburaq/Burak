#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finalisierungskette — laeuft nach JEDEM openpyxl-Schreibzugriff:

1. LibreOffice-Neuberechnung (stellt alle Werte her; Rundreise-Beweis).
2. Diagramm-Reparatur (LibreOffice wirft Diagrammfarben weg — die
   openpyxl-gebauten Diagramm-XMLs werden auf ZIP-Ebene zurueckkopiert,
   die berechneten Werte bleiben unangetastet).
3. Dateibereinigung (doppelte benannte Bereiche — sonst «repariert»
   Excel die Datei und wirft Inhalte weg).
4. fullCalcOnLoad in calcPr setzen und leeres workbookProtection
   entfernen (beides verwirft LibreOffice beim Speichern).
"""
import re
import shutil
import subprocess
import sys
import zipfile

F = sys.argv[1] if len(sys.argv) > 1 else 'BURAK_MASTER_FIX.xlsx'
RECALC = '/mnt/skills/public/xlsx/scripts/recalc.py'

subprocess.run(['pkill', '-9', '-f', 'soffice[.]bin'], capture_output=True)
r = subprocess.run([sys.executable, RECALC, F, '600'], capture_output=True, text=True)
assert '"status": "success"' in r.stdout, (r.stdout + r.stderr)[-600:]
print('1/4 Neuberechnung: success')

r = subprocess.run([sys.executable, 'repariere_charts.py', F],
                   capture_output=True, text=True)
assert 'repariert' in r.stdout, (r.stdout + r.stderr)[-600:]
print('2/4', r.stdout.strip().splitlines()[-1])

r = subprocess.run([sys.executable, 'bereinige_datei.py', F],
                   capture_output=True, text=True)
print('3/4', r.stdout.strip().splitlines()[-1])

with zipfile.ZipFile(F) as z:
    teile = [(i, z.read(i.filename)) for i in z.infolist()]
for idx, (info, daten) in enumerate(teile):
    if info.filename == 'xl/workbook.xml':
        xml = daten.decode('utf-8').replace('<workbookProtection/>', '')
        m = re.search(r'<calcPr\b[^>]*/>', xml)
        assert m, 'kein calcPr'
        if 'fullCalcOnLoad' not in m.group(0):
            xml = xml.replace(m.group(0), m.group(0)[:-2] + ' fullCalcOnLoad="1"/>')
        teile[idx] = (info, xml.encode('utf-8'))
with zipfile.ZipFile(F + '.tmp', 'w', zipfile.ZIP_DEFLATED) as z:
    for info, daten in teile:
        z.writestr(info, daten)
shutil.move(F + '.tmp', F)
print('4/4 fullCalcOnLoad gesetzt, workbookProtection bereinigt.')
