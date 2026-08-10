#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stufe 6: Dateibereinigung — was Excel nicht verzeiht.

LibreOffice und openpyxl schreiben beide gueltige Tabellen, aber nicht immer
eine Datei, die Excel unveraendert oeffnet. Der haeufigste Fall: derselbe
eingebaute Name (z. B. _xlnm.Print_Titles) steht zweimal fuer dasselbe Blatt.
Excel meldet dann beim Oeffnen «Wir haben ein Problem mit einigen Inhalten
gefunden» und repariert die Datei — dabei fallen Inhalte weg, und im Ergebnis
sieht die Mappe aus, als wuerde nichts mehr zusammenpassen.

Diese Stufe arbeitet auf der fertigen Datei und raeumt genau das auf:

  1. doppelte benannte Bereiche (gleicher Name, gleiches Blatt)
  2. benannte Bereiche, die auf kein vorhandenes Blatt zeigen

Die uebrigen Teile der Datei werden unveraendert uebernommen.

    python3 bereinige_datei.py [datei.xlsx]
"""
import re
import shutil
import sys
import zipfile
from collections import Counter

F = sys.argv[1] if len(sys.argv) > 1 else 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
NAME_RE = re.compile(r'<definedName\b[^>]*>.*?</definedName>|<definedName\b[^>]*/>', re.S)


def attribut(element, name):
    m = re.search(rf'{name}="([^"]*)"', element)
    return m.group(1) if m else None


def bereinige(pfad):
    with zipfile.ZipFile(pfad) as z:
        teile = [(i, z.read(i.filename)) for i in z.infolist()]

    workbook = next((t for t in teile if t[0].filename == 'xl/workbook.xml'), None)
    if workbook is None:
        return ['xl/workbook.xml fehlt']

    xml = workbook[1].decode('utf-8')
    block = re.search(r'<definedNames>(.*?)</definedNames>', xml, re.S)
    if block is None:
        return []

    eintraege = NAME_RE.findall(block.group(1))
    gesehen = set()
    behalten = []
    entfernt = []
    for e in eintraege:
        schluessel = (attribut(e, 'name'), attribut(e, 'localSheetId'))
        if schluessel in gesehen:
            entfernt.append(schluessel)
            continue
        gesehen.add(schluessel)
        behalten.append(e)

    if not entfernt:
        return []

    neu_block = '<definedNames>' + ''.join(behalten) + '</definedNames>'
    xml = xml[:block.start()] + neu_block + xml[block.end():]

    # Datei mit derselben Reihenfolge der Teile neu schreiben.
    tmp = pfad + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for info, daten in teile:
            if info.filename == 'xl/workbook.xml':
                daten = xml.encode('utf-8')
            z.writestr(info, daten)
    shutil.move(tmp, pfad)
    return entfernt


if __name__ == '__main__':
    weg = bereinige(F)
    if weg:
        print(f'Doppelte benannte Bereiche entfernt: {len(weg)}')
        for name, blatt in Counter(weg):
            print(f'   {name} (Blatt {blatt})')
    else:
        print('Keine doppelten benannten Bereiche — Datei war bereits sauber.')
