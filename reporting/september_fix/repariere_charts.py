#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagramm-Reparatur nach der LibreOffice-Rundreise.

Befund: LibreOffice berechnet die Mappe korrekt neu, wirft beim Speichern
aber die Diagramm-Formatierung weg (Fuellfarben der Serien und Datenpunkte).
openpyxl wiederum verwirft beim Speichern die berechneten Formelwerte.

Loesung: Die Diagramme werden aus der berechneten Datei heraus mit openpyxl
frisch aufgebaut (Farben, Beschriftungen, Achsen) und die entstandenen
Diagramm-XMLs auf ZIP-Ebene in die berechnete Datei zurueckkopiert.
So bleiben die von LibreOffice gerechneten Werte erhalten UND die
Diagramme tragen das einheitliche Design.

Vor dem Ersetzen wird jede Diagrammnummer verifiziert: Wertebereich und
Balkenrichtung muessen in beiden Dateien uebereinstimmen — sonst Abbruch.
"""
import re
import shutil
import sys
import zipfile
import openpyxl
from openpyxl.chart import BarChart, DoughnutChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.marker import DataPoint
from openpyxl.chart.shapes import GraphicalProperties

F = sys.argv[1] if len(sys.argv) > 1 else 'CH_MiT_Strom_Customer_CEO_CFO_MASTER__2_.xlsx'
TMP = F + '.chartbau.xlsx'

BLAU = '15243A'
ORANGE = 'F47B20'
PALETTE = [ORANGE, BLAU, '3E5C76', '7C93AD', 'B45309', '5A748C',
           '2C425C', 'D98C4A', '8A9BB0', 'C0CCD9']


def baue_diagramme(pfad):
    """Alle 7 Diagramme frisch aufbauen (identisch zu ausbau_block4)."""
    wb = openpyxl.load_workbook(pfad)
    data = wb['_data']
    diag = wb['📊 Diagramme']
    dash = wb['Dashboard']

    def ref(col, r1, r2):
        return Reference(data, min_col=openpyxl.utils.column_index_from_string(col),
                         min_row=r1, max_row=r2)

    def balken(cat_col, cat_r, val_col, val_r, richtung, titel=None, punktfarben=None):
        ch = BarChart()
        ch.type = richtung
        ch.grouping = 'clustered'
        ch.gapWidth = 60
        ch.legend = None
        if titel:
            ch.title = titel
        ch.add_data(ref(val_col, val_r[0], val_r[1]), titles_from_data=False)
        ch.set_categories(ref(cat_col, cat_r[0], cat_r[1]))
        s = ch.series[0]
        s.graphicalProperties = GraphicalProperties(solidFill=BLAU)
        if punktfarben:
            s.data_points = [DataPoint(idx=i, spPr=GraphicalProperties(solidFill=f))
                             for i, f in punktfarben]
        ch.dataLabels = DataLabelList(showVal=True, showLegendKey=False,
                                      showCatName=False, showSerName=False)
        ch.dataLabels.numFmt = '#,##0'
        ch.dataLabels.dLblPos = 'outEnd'
        ch.y_axis.numFmt = '#,##0'
        if richtung == 'bar':
            ch.x_axis.scaling.orientation = 'maxMin'
            ch.y_axis.crosses = 'max'
        return ch

    anker = [ch.anchor for ch in diag._charts]
    assert len(anker) == 5
    diag._charts.clear()
    neue = [balken('R', (2, 33), 'S', (2, 33), 'bar'),
            balken('V', (2, 11), 'W', (2, 11), 'bar'),
            balken('B', (2, 11), 'D', (2, 11), 'col', punktfarben=[(0, ORANGE)]),
            balken('X', (2, 3), 'Y', (2, 3), 'col', punktfarben=[(0, ORANGE)]),
            balken('Z', (2, 13), 'AA', (2, 13), 'col')]
    for ch, a in zip(neue, anker):
        ch.anchor = a
        diag.add_chart(ch)

    anker_d = [ch.anchor for ch in dash._charts]
    assert len(anker_d) == 2
    dash._charts.clear()
    ring = DoughnutChart()
    ring.title = 'Pipeline — Status (Anzahl)'
    ring.add_data(Reference(data, min_col=3, min_row=2, max_row=11),
                  titles_from_data=False)
    ring.set_categories(Reference(data, min_col=2, min_row=2, max_row=11))
    ring.dataLabels = DataLabelList(showVal=True, showLegendKey=False,
                                    showCatName=False, showSerName=False)
    ring.dataLabels.numFmt = '0'
    ring.series[0].data_points = [
        DataPoint(idx=i, spPr=GraphicalProperties(solidFill=PALETTE[i % len(PALETTE)]))
        for i in range(10)]
    ring.legend.position = 'r'
    vol = balken('B', (2, 11), 'D', (2, 11), 'bar',
                 titel='Pipeline — Status nach Volumen CHF', punktfarben=[(0, ORANGE)])
    for ch, a in zip((ring, vol), anker_d):
        ch.anchor = a
        dash.add_chart(ch)

    wb.save(pfad)


def signatur(xml):
    """Wertebereiche + Richtung eines Diagramm-XML — zum Abgleich.
    LibreOffice schreibt mit c:-Praefix, openpyxl mit Default-Namespace —
    die Signatur ist gegen beides tolerant."""
    refs = tuple(sorted({re.sub(r'\d+', '', r.replace("'", ''))
                         for r in re.findall(r'<(?:c:)?f>([^<]+)</(?:c:)?f>', xml)}))
    bar = re.search(r'barDir val="(\w+)"', xml)
    ring = 'doughnutChart' in xml
    return refs, bar.group(1) if bar else ('doughnut' if ring else '?')


shutil.copy(F, TMP)
baue_diagramme(TMP)

with zipfile.ZipFile(TMP) as z:
    frisch = {n: z.read(n) for n in z.namelist()
              if re.match(r'xl/charts/chart\d+\.xml$', n)}

with zipfile.ZipFile(F) as z:
    teile = [(i, z.read(i.filename)) for i in z.infolist()]

ersetzt = 0
for i, (info, daten) in enumerate(teile):
    n = info.filename
    if n in frisch:
        alt_sig = signatur(daten.decode('utf-8'))
        neu_sig = signatur(frisch[n].decode('utf-8'))
        assert alt_sig == neu_sig, (f'{n}: Diagramm-Zuordnung passt nicht — '
                                    f'{alt_sig} vs {neu_sig}')
        teile[i] = (info, frisch[n])
        ersetzt += 1
assert ersetzt == 7, f'{ersetzt} statt 7 Diagramme ersetzt'

tmp2 = F + '.tmp'
with zipfile.ZipFile(tmp2, 'w', zipfile.ZIP_DEFLATED) as z:
    for info, daten in teile:
        z.writestr(info, daten)
shutil.move(tmp2, F)

import os
os.remove(TMP)
print(f'Diagramme repariert: {ersetzt} Diagramm-XMLs mit Design zurückkopiert, '
      f'berechnete Werte unangetastet.')
