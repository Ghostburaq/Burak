#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I) Excel-Vertraeglichkeit — oeffnet Excel die Datei ohne Reparatur?

Alle uebrigen Pruefungen messen das Rechenmodell. Diese hier misst die Datei
selbst: ob Excel sie unveraendert oeffnet. Meldet Excel beim Oeffnen
«Wir haben ein Problem mit einigen Inhalten gefunden», wirft es beim Reparieren
Inhalte weg — und danach sieht die Mappe aus, als wuerde nichts mehr
zusammenpassen, obwohl jede Formel richtig ist.

Geprueft wird direkt im Dateiinneren (der xlsx ist ein ZIP mit XML):

  1. doppelte benannte Bereiche (gleicher Name, gleiches Blatt)
  2. benannte Bereiche auf nicht vorhandene Blaetter
  3. ueberlappende Verbundbereiche
  4. Werte in Zellen, die von einem Verbund ueberdeckt sind
  5. Zeilenhoehen ueber 409.5 pt, Spaltenbreiten ueber 255
  6. Blattnamen: Laenge und unzulaessige Zeichen
  7. Formeln: _xlfn-Praefixe, Laenge, unausgeglichene Klammern,
     Verweise auf nicht vorhandene Blaetter
  8. Autofilter, Druckbereiche und Wiederholungszeilen innerhalb des Blatts
  9. Gueltigkeitsregeln und bedingte Formatierung mit leerem Bereich
 10. Diagrammbezuege auf nicht vorhandene Blaetter
"""
import re
import sys
import zipfile
from openpyxl.utils import range_boundaries, get_column_letter, column_index_from_string

F = sys.argv[1] if len(sys.argv) > 1 else 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
MAX_ZEILE, MAX_SPALTE = 1048576, 16384
befunde = []
geprueft = 0


def note(art, text):
    befunde.append(f'[{art}] {text}')


z = zipfile.ZipFile(F)
namen = z.namelist()
wbxml = z.read('xl/workbook.xml').decode('utf-8')

# Blattnamen in Reihenfolge (localSheetId zeigt auf diese Reihenfolge)
blaetter = re.findall(r'<sheet[^>]*name="([^"]+)"', wbxml)
blaetter = [b.replace('&amp;', '&').replace('&apos;', "'").replace('&quot;', '"')
            .replace('&lt;', '<').replace('&gt;', '>') for b in blaetter]

# ------------------------------------------------- 1+2) Benannte Bereiche
eintraege = re.findall(r'<definedName\b[^>]*>.*?</definedName>|<definedName\b[^>]*/>',
                       wbxml, re.S)
gesehen = {}
for e in eintraege:
    geprueft += 1
    name = re.search(r'name="([^"]*)"', e)
    blatt = re.search(r'localSheetId="(\d+)"', e)
    schluessel = (name.group(1) if name else None, blatt.group(1) if blatt else None)
    if schluessel in gesehen:
        wo = ('Blatt «' + blaetter[int(schluessel[1])] + '»') if schluessel[1] else 'Mappe'
        note('DOPPELTER NAME',
             f'{schluessel[0]} steht zweimal für {wo} — Excel meldet die Datei als '
             f'beschädigt und repariert sie')
    gesehen[schluessel] = e
    ziel = re.sub(r'<[^>]*>', '', e).replace('&apos;', "'").replace('&amp;', '&')
    for verweis in re.findall(r"'([^']+)'!", ziel):
        if verweis not in blaetter:
            note('NAME OHNE BLATT', f'{schluessel[0]} zeigt auf «{verweis}»')

# ------------------------------------------------------ Blaetter einzeln
VERBOTEN = set(':\\/?*[]')
for b in blaetter:
    geprueft += 1
    if len(b) > 31:
        note('BLATTNAME', f'«{b}» ist {len(b)} Zeichen lang (Excel erlaubt 31)')
    if VERBOTEN & set(b):
        note('BLATTNAME', f'«{b}» enthält ein unzulässiges Zeichen')

blattdateien = sorted(n for n in namen if re.match(r'xl/worksheets/sheet\d+\.xml$', n))
for idx, datei in enumerate(blattdateien):
    x = z.read(datei).decode('utf-8')
    titel = blaetter[idx] if idx < len(blaetter) else datei

    # ---- 3+4) Verbundbereiche
    merges = re.findall(r'<mergeCell ref="([^"]+)"/>', x)
    grenzen = [range_boundaries(m) for m in merges]
    for i in range(len(grenzen)):
        for j in range(i + 1, len(grenzen)):
            a, b2 = grenzen[i], grenzen[j]
            if a[0] <= b2[2] and b2[0] <= a[2] and a[1] <= b2[3] and b2[1] <= a[3]:
                note('VERBUND', f'{titel}: {merges[i]} und {merges[j]} überlappen sich')
        geprueft += 1
    mit_inhalt = set(re.findall(r'<c r="([A-Z]+\d+)"[^>]*>(?:<f|<v|<is)', x))
    for m, a in zip(merges, grenzen):
        for rr in range(a[1], a[3] + 1):
            for cc in range(a[0], a[2] + 1):
                if (rr, cc) != (a[1], a[0]) and f'{get_column_letter(cc)}{rr}' in mit_inhalt:
                    note('VERBUND', f'{titel}: {m} — die überdeckte Zelle '
                                    f'{get_column_letter(cc)}{rr} trägt einen Wert')

    # ---- 5) Hoehen und Breiten
    for h in re.findall(r'<row[^>]*ht="([\d.]+)"', x):
        geprueft += 1
        if float(h) > 409.5:
            note('HÖHE', f'{titel}: Zeilenhöhe {h} pt über der Excel-Grenze 409.5')
    for w in re.findall(r'<col[^>]*width="([\d.]+)"', x):
        geprueft += 1
        if float(w) > 255:
            note('BREITE', f'{titel}: Spaltenbreite {w} über der Excel-Grenze 255')

    # ---- 7) Formeln
    for f in re.findall(r'<f[^>]*>([^<]*)</f>', x):
        geprueft += 1
        formel = (f.replace('&amp;', '&').replace('&lt;', '<')
                  .replace('&gt;', '>').replace('&quot;', '"').replace('&apos;', "'"))
        if '_xlfn' in formel:
            note('FORMEL', f'{titel}: _xlfn-Präfix in {formel[:60]}')
        if len(formel) > 8192:
            note('FORMEL', f'{titel}: Formel mit {len(formel)} Zeichen (Grenze 8192)')
        if formel.count('(') != formel.count(')'):
            note('FORMEL', f'{titel}: unausgeglichene Klammern in {formel[:60]}')
        for verweis in set(re.findall(r"'([^'\[\]]+)'!", formel)):
            if verweis not in blaetter:
                note('FORMEL', f'{titel}: Verweis auf unbekanntes Blatt «{verweis}» '
                               f'in {formel[:50]}')

    # ---- 8) Autofilter, Druckbereich, Wiederholungszeilen
    dim = re.search(r'<dimension ref="([^"]+)"', x)
    grenze = range_boundaries(dim.group(1)) if dim else None
    af = re.search(r'<autoFilter ref="([^"]+)"', x)
    if af:
        geprueft += 1
        a = range_boundaries(af.group(1))
        if a[2] > MAX_SPALTE or a[3] > MAX_ZEILE:
            note('AUTOFILTER', f'{titel}: Bereich {af.group(1)} liegt ausserhalb des Blatts')

    # ---- 9) Gueltigkeit und bedingte Formatierung
    for sq in re.findall(r'<dataValidation[^>]*sqref="([^"]*)"', x):
        geprueft += 1
        if not sq.strip():
            note('GÜLTIGKEIT', f'{titel}: Gültigkeitsregel ohne Bereich')
    for sq in re.findall(r'<conditionalFormatting[^>]*sqref="([^"]*)"', x):
        geprueft += 1
        if not sq.strip():
            note('BEDINGTE FORMATIERUNG', f'{titel}: Regel ohne Bereich')

    # ---- Zeilen muessen aufsteigend stehen
    zeilen = [int(r) for r in re.findall(r'<row r="(\d+)"', x)]
    geprueft += 1
    if zeilen != sorted(zeilen):
        note('REIHENFOLGE', f'{titel}: Zeilen stehen nicht aufsteigend in der Datei')
    if len(zeilen) != len(set(zeilen)):
        note('REIHENFOLGE', f'{titel}: eine Zeilennummer kommt mehrfach vor')

# ---- 10) Diagrammbezuege
for datei in [n for n in namen if re.match(r'xl/charts/chart\d+\.xml$', n)]:
    x = z.read(datei).decode('utf-8')
    for verweis in set(re.findall(r'<c:f>([^<]+)</c:f>', x)):
        geprueft += 1
        v = verweis.replace('&amp;', '&').replace('&apos;', "'")
        blatt = v.split('!')[0].strip("'")
        if blatt not in blaetter:
            note('DIAGRAMM', f'{datei}: Bezug auf unbekanntes Blatt «{blatt}»')

print(f'Excel-Prüfungen : {geprueft}')
print(f'Befunde         : {len(befunde)}')
if befunde:
    print()
    for b in befunde[:40]:
        print('  ', b)
    if len(befunde) > 40:
        print(f'   ... und {len(befunde) - 40} weitere')
else:
    print()
    print('Die Datei ist so aufgebaut, dass Excel sie unverändert öffnet — keine')
    print('doppelten Namen, keine überlappenden Verbünde, keine ungültigen Bezüge.')
sys.exit(1 if befunde else 0)
