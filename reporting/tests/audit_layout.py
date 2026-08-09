#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G) Layoutpruefung - passt jede Zelle in ihr Feld?

Geprueft wird jede sichtbare Zelle innerhalb des Druckbereichs:

  ABGESCHNITTEN      Text ist breiter als der Platz und kann auch nicht in
                     leere Nachbarzellen ragen.
  ZAHL ZU BREIT      Zahl passt nicht in ihre Spalte - Excel zeigt ####.
  ZEILE ZU NIEDRIG   umgebrochener Text braucht mehr Zeilen, als die
                     Zeilenhoehe hergibt.
  DRUCK ZU SCHMAL    Blatt insgesamt so breit, dass der Ausdruck staerker als
                     auf 60 % verkleinert werden muesste.

Gemessen wird mit demselben Modell, das build_layout.py zum Setzen der Breiten
und Hoehen benutzt (layout_modell.py).
"""
import openpyxl, sys, os
from collections import Counter
from openpyxl.utils import get_column_letter, range_boundaries, column_index_from_string

# layout_modell liegt neben den Bau-Skripten - auch wenn diese Pruefung aus
# dem Unterordner tests/ gestartet wird.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import layout_modell as L

F = sys.argv[1] if len(sys.argv) > 1 else 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
wb = openpyxl.load_workbook(F)
V = openpyxl.load_workbook(F, data_only=True)

TOLERANZ_PX = 2.0
TOLERANZ_PT = 1.0
MIN_SKALIERUNG = 0.60
DPI = 96.0
BLATT_ZOLL = {9: (8.268, 11.693), 1: (8.5, 11.0)}     # A4, Letter

befunde = []


for ws in wb.worksheets:
    if ws.sheet_state != 'visible':
        continue
    vs = V[ws.title]
    karte = L.spaltenkarte(ws)

    def breite(_ws, col):
        if isinstance(col, str):
            col = column_index_from_string(col)
        return karte.get(col, (L.STANDARD_BREITE, False))[0]

    pa = ws.print_area
    grenze = None
    if pa:
        pa = pa[0] if isinstance(pa, list) else pa
        grenze = range_boundaries(pa.split('!')[-1])

    verbund = {}
    for m in ws.merged_cells.ranges:
        for r in range(m.min_row, m.max_row + 1):
            for c in range(m.min_col, m.max_col + 1):
                verbund[(r, c)] = m

    def belegt(r, c):
        """Steht in der Nachbarzelle etwas, das den Ueberlauf blockiert?"""
        if (r, c) in verbund:
            return True
        z = ws.cell(row=r, column=c)
        return L.anzeige(z, vs.cell(row=r, column=c).value) is not None

    # ------------------------------------------------- Massstab des Ausdrucks
    if grenze:
        gesamt_px = sum(breite(ws, get_column_letter(c)) * L.MDW + 5
                        for c in range(grenze[0], grenze[2] + 1))
        gesamt_pt = sum(ws.row_dimensions[r].height or L.STANDARD_HOEHE
                        for r in range(grenze[1], grenze[3] + 1))
        b, h = BLATT_ZOLL.get(ws.page_setup.paperSize or 9, BLATT_ZOLL[9])
        quer = ws.page_setup.orientation == 'landscape'
        platz_b = ((h if quer else b)
                   - (ws.page_margins.left or 0) - (ws.page_margins.right or 0)) * DPI
        platz_h = ((b if quer else h)
                   - (ws.page_margins.top or 0.75) - (ws.page_margins.bottom or 0.75)) * 72
        breit = max(1, int(ws.page_setup.fitToWidth or 1))
        hoch = int(ws.page_setup.fitToHeight or 0)
        skala = min(1.0, platz_b * breit / gesamt_px)
        if hoch:
            skala = min(skala, platz_h * hoch / gesamt_pt)
        if skala < MIN_SKALIERUNG:
            befunde.append((ws.title, 'Blatt', 'DRUCK ZU KLEIN',
                            f'Ausdruck auf {skala:.0%} verkleinert '
                            f'({breit} Seite(n) breit, Höhe auf '
                            f'{hoch if hoch else "fortlaufend"}) — Inhalt {gesamt_px:.0f} px '
                            f'× {gesamt_pt:.0f} pt'))

    # ---------------------------------------------------------- Zellen
    for row in ws.iter_rows():
        for c in row:
            if c.value is None:
                continue
            if grenze and not (grenze[0] <= c.column <= grenze[2]
                               and grenze[1] <= c.row <= grenze[3]):
                continue
            col = get_column_letter(c.column)
            if breite(ws, col) == 0:
                continue
            roh = vs[c.coordinate].value
            t = L.anzeige(c, roh)
            if t is None:
                continue
            ist_zahl = isinstance(roh, (int, float)) and not isinstance(roh, bool)

            m = verbund.get((c.row, c.column))
            if m:
                if (c.row, c.column) != (m.min_row, m.min_col):
                    continue
                spalten = [breite(ws, get_column_letter(x))
                           for x in range(m.min_col, m.max_col + 1)]
                verf = L.nutz_px(spalten)
                zeilen_im_block = m.max_row - m.min_row + 1
            else:
                spalten = [breite(ws, col)]
                zeilen_im_block = 1
                # Ohne Verbund darf einzeiliger Text in leere Nachbarzellen
                # ragen. Zahlen nicht (Excel zeigt dann ####), umgebrochener
                # Text auch nicht - der bleibt in seiner Zelle.
                if not ist_zahl and not c.alignment.wrap_text:
                    aus = (c.alignment.horizontal or 'left')
                    if aus in ('left', 'general', 'justify', 'fill', 'center',
                               'centerContinuous', 'distributed'):
                        x = c.column + 1
                        while (x <= ws.max_column and not belegt(c.row, x)
                               and not (grenze and x > grenze[2])
                               and breite(ws, get_column_letter(x)) > 0):
                            spalten.append(breite(ws, get_column_letter(x)))
                            x += 1
                    if aus in ('right', 'center', 'centerContinuous', 'distributed'):
                        x = c.column - 1
                        while (x >= 1 and not belegt(c.row, x)
                               and not (grenze and x < grenze[0])
                               and breite(ws, get_column_letter(x)) > 0):
                            spalten.append(breite(ws, get_column_letter(x)))
                            x -= 1
                verf = L.nutz_px(spalten)

            verf -= L.einzug_px(c)
            if verf <= 0:
                continue

            teile = t.split('\n')
            if c.alignment.wrap_text and not ist_zahl:
                zeilen = L.zeilen_zahl(t, c.font, verf)
            else:
                zeilen = len(teile)
                zu_breit = max(L.text_px(x, c.font) for x in teile)
                if zu_breit > verf + TOLERANZ_PX:
                    art = 'ZAHL ZU BREIT' if ist_zahl else 'ABGESCHNITTEN'
                    befunde.append((ws.title, c.coordinate, art,
                                    f'braucht {zu_breit:.0f} px, hat {verf:.0f} px  «{t[:60]}»'))
                    continue

            hoehe = sum(ws.row_dimensions[r].height or L.STANDARD_HOEHE
                        for r in range(c.row, c.row + zeilen_im_block))
            noetig = L.hoehe_pt(zeilen, c.font)
            if noetig > hoehe + TOLERANZ_PT:
                befunde.append((ws.title, c.coordinate, 'ZEILE ZU NIEDRIG',
                                f'{zeilen} Zeile(n) brauchen {noetig:.0f} pt, '
                                f'Zeile ist {hoehe:.0f} pt  «{t[:50]}»'))

print(f'Layoutbefunde: {len(befunde)}')
for blatt, n in Counter(b[0] for b in befunde).most_common():
    print(f'   {blatt:<30} {n}')
if befunde:
    print()
    for b in befunde[:70]:
        print(f'  [{b[2]:<16}] {b[0]}!{b[1]}: {b[3]}')
    if len(befunde) > 70:
        print(f'  ... und {len(befunde) - 70} weitere')
else:
    print('Jede Zelle passt in ihr Feld — keine abgeschnittenen Texte, keine ####,')
    print('keine zu niedrigen Zeilen, jedes Blatt druckt lesbar auf sein Papier.')
sys.exit(1 if befunde else 0)
