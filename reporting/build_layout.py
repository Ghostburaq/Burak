#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stufe 5: Layout.

Setzt Spaltenbreiten, Umbrueche, Zeilenhoehen und die Seiteneinrichtung so,
dass in der ganzen Mappe kein Text abgeschnitten wird, keine Zahl als ####
erscheint, keine Zeile zu niedrig ist und jedes Blatt lesbar auf sein Papier
druckt.

Vorgehen je Blatt:
  1. Breiten: nur so weit verbreitern, wie es der Inhalt wirklich verlangt.
     Text, der ohnehin in leere Nachbarzellen ragen darf, verlangt nichts.
     Zahlen verlangen immer die volle Breite in ihrer eigenen Spalte, weil
     Excel sie sonst als #### zeigt.
  2. Umbruch: was danach immer noch zu breit ist, wird umgebrochen.
  3. Hoehen: jede Zeile bekommt die Hoehe, die ihre Zeilen brauchen.
  4. Seite: einheitlich A4, und so viele Seiten breit, dass der Ausdruck nicht
     unter 60 % verkleinert werden muss.

Gemessen wird mit layout_modell.py - demselben Lineal, mit dem audit_layout.py
anschliessend nachmisst.
"""
import openpyxl
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter, range_boundaries, column_index_from_string
from openpyxl.worksheet.pagebreak import Break, RowBreak
import layout_modell as L

F = 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'

# Randspalten bleiben schmal.
FEST = {
    '📑 Executive PDF': {'A': 3.0},
    '📋 Definitionen & Klärung': {'A': 3.0},
    '🔍 Herleitung & Formeln': {'A': 3.0},
}

# Bewusst gesetzte Breiten fuer die Spalten mit langen Texten: (Breite, Umbruch).
# Ohne sie zieht die Spalte «Leistung / Fleet» das Blatt so breit, dass der
# Ausdruck auf die Haelfte verkleinert und damit unlesbar wird. Mit Umbruch
# steht der ganze Text da und das Blatt bleibt eine Seite breit.
ZIEL = {
    'CEO Report': {'B': (29.0, True), 'D': (20.0, True), 'F': (26.0, True),
                   'L': (24.0, True), 'M': (15.0, True), 'N': (17.0, True)},
    'Dashboard': {'B': (29.0, True), 'D': (20.0, True), 'F': (26.0, True),
                  'K': (24.0, True)},
    'MiT Strom Pipeline': {'E': (24.0, True), 'V': (45.0, True), 'X': (45.0, True)},
}

# Obergrenze je Spalte. Was breiter waere, wird umgebrochen statt verbreitert.
MAX_SPALTE = {'📑 Executive PDF': 26.0, '📄 Report': 30.0}
MAX_STANDARD = 46.0

# Wie viele Seiten breit darf ein Blatt drucken? Bewusst je Blatt entschieden:
# Berichte gehoeren auf eine Seite, das Arbeitsblatt Pipeline hat 34 Spalten und
# waere auf einer Seite nicht mehr lesbar.
SEITEN_BREIT = {
    '📑 Executive PDF': 1, '📄 Report': 1, 'CEO Report': 1, 'Dashboard': 1,
    '📊 Diagramme': 1, 'MiT Strom Pipeline': 3,
    '📋 Definitionen & Klärung': 1, '🔍 Herleitung & Formeln': 1,
    '⚖️ Wahrscheinlichkeit': 1,
}
# Blaetter, die breiter als eine Seite drucken: Titel linksbuendig, damit sie
# nicht mitten im Wort an der Seitengrenze abreissen, und Kunden-Spalten auf
# jeder Seite wiederholen.
WIEDERHOLEN = {'MiT Strom Pipeline': '$A:$B'}

# Verbundbereiche, die nicht bis an den Rand des Druckbereichs reichten und
# dadurch schief unter den Ueberschriften standen.
VERBUND_KORREKTUR = {
    'CEO Report': [('A1:L1', 'A1:N1'), ('A2:L2', 'A2:N2'), ('A3:L3', 'A3:N3'),
                   ('I6:L6', 'I6:N6'), ('I7:L7', 'I7:N7'), ('A217:L217', 'A217:N217')],
    'MiT Strom Pipeline': [('A1:X1', 'A1:AI1'), ('A2:X2', 'A2:AI2'),
                           ('A3:X3', 'A3:AI3')],
}

# Die fuenf Diagramme lagen ueberlappend und unterschiedlich breit auf dem
# Blatt. Hier steht, wo jedes hingehoert: (Zeile von, Zeile bis, Spalte von,
# Spalte bis) - 0-basiert wie in der Datei. Zwei Reihen zu zweit, das
# Bandbreiten-Diagramm ueber die volle Breite.
DIAGRAMM_RASTER = [(4, 47, 0, 9), (4, 47, 9, 18),
                   (49, 93, 0, 9), (49, 93, 9, 18),
                   (95, 138, 0, 18)]
# Die Beschriftungen der zweiten Reihe wandern mit.
DIAGRAMM_TITEL = [('A28', 'A50'), ('J28', 'J50')]
DIAGRAMM_DRUCK = '$A$1:$R$140' 
# Feste Seitenumbrueche: so faellt der Schnitt zwischen zwei Diagrammreihen
# und nicht mitten durch ein Diagramm.
SEITEN_UMBRUCH = {'📊 Diagramme': [48, 94]}

# Einheitliche Kopf- und Fusszeile fuer jedes Blatt. Vorher hatten drei
# Blaetter gar keine, drei weitere je eine andere.
KOPFZEILE = {
    '📑 Executive PDF': 'MiT Strom Schweiz — Executive Sales Summary',
    '📄 Report': 'MiT Strom Schweiz — Sales-Report',
    'CEO Report': 'MiT Strom Schweiz — CEO Report',
    'Dashboard': 'MiT Strom Schweiz — Sales Dashboard',
    '📊 Diagramme': 'MiT Strom Schweiz — Diagramme und Visualisierungen',
    'MiT Strom Pipeline': 'MiT Strom Schweiz — Pipeline und Deal Tracking',
    '📋 Definitionen & Klärung': 'MiT Strom Schweiz — Definitionen, Kalkulationsregeln und offene Punkte',
    '🔍 Herleitung & Formeln': 'MiT Strom Schweiz — Herleitung und Formeln',
    '⚖️ Wahrscheinlichkeit': 'MiT Strom Schweiz — Bewertungsmodell Wahrscheinlichkeit',
}
FUSS_LINKS = 'Mobil in Time AG · An Aggreko Company'

# Sicherheitszuschlag auf die gemessene Textbreite. Schriften rendern je nach
# System minim unterschiedlich; ohne Reserve steht ein Text, der rechnerisch
# gerade noch passt, in der Praxis eine Spur ueber dem Rand.
SICHERHEIT = 1.05

MIN_SKALIERUNG = 0.60
# Auf eine Seite der Hoehe nach zwingen nur, wenn das nichts kostet - also der
# Massstab dadurch hoechstens um 5 % kleiner wird als er wegen der Breite
# ohnehin schon ist. Sonst quetscht Excel das Blatt zusammen, bis nichts mehr
# lesbar ist.
OHNE_VERLUST = 0.95
DPI = 96.0
A4 = (8.268, 11.693)
RAND = 0.3

bericht = []

wb = openpyxl.load_workbook(F)
V = openpyxl.load_workbook(F, data_only=True)

for ws in wb.worksheets:
    if ws.sheet_state != 'visible':
        continue
    vs = V[ws.title]
    fest = FEST.get(ws.title, {})
    maxsp = MAX_SPALTE.get(ws.title, MAX_STANDARD)

    # -------------------------------------------------- Seiteneinrichtung
    ws.page_setup.paperSize = 9                       # einheitlich A4
    ws.page_margins.left = ws.page_margins.right = RAND
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    ws.page_margins.header = ws.page_margins.footer = 0.25
    # Waagrecht zentriert wirkt aufgeraeumt; senkrecht zentriert schiebt auf
    # mehrseitigen Blaettern den Inhalt in die Seitenmitte und hinterlaesst
    # oben eine leere Bahn - genau das war beim Blatt «Diagramme» zu sehen.
    ws.print_options.horizontalCentered = True
    ws.print_options.verticalCentered = False
    if ws.title in KOPFZEILE:
        ws.oddHeader.left.text = ws.oddHeader.right.text = None
        ws.oddHeader.center.text = KOPFZEILE[ws.title]
        ws.oddHeader.center.size = 10
        ws.oddHeader.center.font = 'Calibri,Bold'
        ws.oddFooter.left.text = FUSS_LINKS
        ws.oddFooter.center.text = 'Stand: &D'
        ws.oddFooter.right.text = 'Seite &P von &N'
        for teil in (ws.oddFooter.left, ws.oddFooter.center, ws.oddFooter.right):
            teil.size = 8

    # ---------------------------------- Diagramme auf ein Raster legen
    if ws.title == '📊 Diagramme' and len(ws._charts) == len(DIAGRAMM_RASTER):
        for alt, neu in DIAGRAMM_TITEL:
            if ws[alt].value is not None and ws[neu].value is None:
                ws[neu].value = ws[alt].value
                ws[neu]._style = ws[alt]._style
                ws[alt].value = None
                bericht.append(f'{ws.title}: Beschriftung {alt} → {neu}')
        if ws.print_area != DIAGRAMM_DRUCK:
            ws.print_area = DIAGRAMM_DRUCK
        for ch, (r1, r2, c1, c2) in zip(ws._charts, DIAGRAMM_RASTER):
            a = getattr(ch, 'anchor', None)
            if a is None or not hasattr(a, 'to'):
                continue
            if (a._from.row, a._from.col, a.to.row, a.to.col) == (r1, c1, r2, c2):
                continue
            bericht.append(f'{ws.title}: Diagramm {a._from.row + 1}/{a._from.col + 1} '
                           f'→ Zeile {r1 + 1}–{r2 + 1}, Spalte {c1 + 1}–{c2 + 1}')
            a._from.row, a._from.col, a._from.rowOff, a._from.colOff = r1, c1, 0, 0
            a.to.row, a.to.col, a.to.rowOff, a.to.colOff = r2, c2, 0, 0

    # ---------------------------------- Ein Deal ist kein «1 Deals»
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.endswith('&" Deals"'):
                bezug = c.value[1:-len('&" Deals"')]
                c.value = f'={bezug}&IF({bezug}=1," Deal"," Deals")'
                bericht.append(f'{ws.title}: {c.coordinate} Einzahl/Mehrzahl')
            elif c.number_format == '0" Deals"':
                # Bedingtes Zahlenformat: erster Abschnitt gilt nur fuer den Wert 1.
                c.number_format = '[=1]0" Deal";0" Deals"'
                bericht.append(f'{ws.title}: {c.coordinate} Einzahl/Mehrzahl (Format)')

    # ---------------------------------- Verbundbereiche geradeziehen
    vorhanden = {str(m) for m in ws.merged_cells.ranges}
    for alt, neu in VERBUND_KORREKTUR.get(ws.title, []):
        if alt in vorhanden and neu not in vorhanden:
            ws.unmerge_cells(alt)
            ws.merge_cells(neu)
            bericht.append(f'{ws.title}: Verbund {alt} → {neu}')

    pa = ws.print_area
    grenze = None
    if pa:
        pa = pa[0] if isinstance(pa, list) else pa
        grenze = range_boundaries(pa.split('!')[-1])
    if grenze is None:
        grenze = (1, 1, ws.max_column, ws.max_row)

    verbund = {}
    for m in ws.merged_cells.ranges:
        for r in range(m.min_row, m.max_row + 1):
            for c in range(m.min_col, m.max_col + 1):
                verbund[(r, c)] = m

    # openpyxl fasst gleich formatierte Spalten zu Gruppen zusammen. Wird dann
    # eine einzelne Spalte der Gruppe verbreitert, entstehen zwei sich
    # ueberlappende Eintraege und die Breite kommt nicht an. Deshalb zuerst
    # jede Spalte einzeln fuehren.
    _gruppen = [(d.min or 1, d.max or (d.min or 1), d) for d in ws.column_dimensions.values()]
    _einzeln = {}
    for _von, _bis, _d in _gruppen:
        for _i in range(_von, _bis + 1):
            _einzeln[_i] = _d
    ws.column_dimensions.clear()
    for _i, _d in sorted(_einzeln.items()):
        _neu = ws.column_dimensions[get_column_letter(_i)]
        _neu.width = _d.width
        _neu.hidden = _d.hidden
        _neu.outlineLevel = _d.outlineLevel
        _neu.collapsed = _d.collapsed
        _neu.bestFit = _d.bestFit
        if getattr(_d, '_style', None) is not None:
            _neu._style = _d._style
        _neu.min = _neu.max = _i

    karte = L.spaltenkarte(ws)

    def breite(col):
        if isinstance(col, str):
            col = column_index_from_string(col)
        return karte.get(col, (L.STANDARD_BREITE, False))[0]

    def versteckt(col):
        if isinstance(col, str):
            col = column_index_from_string(col)
        return karte.get(col, (L.STANDARD_BREITE, False))[1]

    def setze(col, w):
        ws.column_dimensions[col].width = round(w, 2)
        karte[column_index_from_string(col)] = (round(w, 2), False)

    def belegt(r, c):
        if (r, c) in verbund:
            return True
        z = ws.cell(row=r, column=c)
        return L.anzeige(z, vs.cell(row=r, column=c).value) is not None

    def spann(c, ist_zahl):
        """Spaltenbreiten, die dem Zellinhalt tatsaechlich zur Verfuegung stehen."""
        col = get_column_letter(c.column)
        spalten = [breite(col)]
        # Umgebrochener Text bleibt in seiner Zelle, Zahlen ebenfalls - nur
        # einzeiliger Text darf in leere Nachbarzellen ragen.
        if ist_zahl or c.alignment.wrap_text:
            return spalten
        aus = c.alignment.horizontal or 'left'
        if aus in ('left', 'general', 'justify', 'fill', 'center',
                   'centerContinuous', 'distributed'):
            x = c.column + 1
            while (x <= grenze[2] and not belegt(c.row, x)
                   and breite(get_column_letter(x)) > 0):
                spalten.append(breite(get_column_letter(x)))
                x += 1
        if aus in ('right', 'center', 'centerContinuous', 'distributed'):
            x = c.column - 1
            while (x >= grenze[0] and not belegt(c.row, x)
                   and breite(get_column_letter(x)) > 0):
                spalten.append(breite(get_column_letter(x)))
                x -= 1
        return spalten

    # Alle sichtbaren Zellen des Druckbereichs einmal einsammeln
    zellen = []
    for row in ws.iter_rows(min_row=grenze[1], max_row=grenze[3],
                            min_col=grenze[0], max_col=grenze[2]):
        for c in row:
            if c.value is None:
                continue
            if breite(get_column_letter(c.column)) == 0:
                continue
            roh = vs[c.coordinate].value
            t = L.anzeige(c, roh)
            if t is None:
                continue
            m = verbund.get((c.row, c.column))
            if m and (c.row, c.column) != (m.min_row, m.min_col):
                continue
            ist_zahl = isinstance(roh, (int, float)) and not isinstance(roh, bool)
            zellen.append((c, t, ist_zahl, m))

    # ------------------------------- 0a) Innenabstand in jeder Zelle
    # Ohne Einzug klebt jede Zahl am rechten und jeder Text am linken
    # Zellenrahmen; nebeneinander gelesen laufen die Spalten ineinander.
    # Ein Zeichen Abstand trennt sie sauber.
    for row in ws.iter_rows(min_row=grenze[1], max_row=grenze[3],
                            min_col=grenze[0], max_col=grenze[2]):
        for c in row:
            if c.value is None or (c.row, c.column) in verbund:
                continue
            a = c.alignment
            if a.indent:
                continue
            roh = vs[c.coordinate].value
            zahl = isinstance(roh, (int, float)) and not isinstance(roh, bool)
            aus = a.horizontal
            if aus in ('center', 'centerContinuous', 'distributed', 'fill'):
                continue
            if aus is None or aus == 'general':
                aus = 'right' if zahl else 'left'
            if aus not in ('left', 'right'):
                continue
            c.alignment = Alignment(horizontal=aus, vertical=a.vertical,
                                    wrap_text=a.wrap_text, indent=1,
                                    text_rotation=a.text_rotation,
                                    shrink_to_fit=a.shrink_to_fit)

    # ------------------------------- 0) Bewusst gesetzte Breiten und Umbruch
    ziel = ZIEL.get(ws.title, {})
    for col, (w, umbruch) in ziel.items():
        if abs(breite(col) - w) > 0.05:
            bericht.append(f'{ws.title}: Spalte {col} {breite(col):.1f} → {w:.1f} (gesetzt)')
            setze(col, w)
        if not umbruch:
            continue
        i = column_index_from_string(col)
        for r in range(grenze[1], grenze[3] + 1):
            if (r, i) in verbund:
                continue
            z = ws.cell(row=r, column=i)
            if z.value is None or z.alignment.wrap_text:
                continue
            a = z.alignment
            z.alignment = Alignment(horizontal=a.horizontal, vertical=a.vertical or 'top',
                                    wrap_text=True, indent=a.indent,
                                    text_rotation=a.text_rotation, shrink_to_fit=False)

    # ------------------------------------------------------ 1) Breiten
    # Mehrere Runden, weil sich der Ueberlaufplatz mit den Breiten aendert.
    for _runde in range(4):
        wunsch = {}
        for c, t, ist_zahl, m in zellen:
            if m:
                continue                       # Verbund wird umgebrochen, nicht verbreitert
            col = get_column_letter(c.column)
            if col in fest or col in ziel:
                continue
            if c.alignment.wrap_text and not ist_zahl:
                continue                       # darf umbrechen
            noetig = max(L.text_px(x, c.font) for x in t.split('\n')) * SICHERHEIT
            verf = L.nutz_px(spann(c, ist_zahl)) - L.einzug_px(c)
            if noetig <= verf:
                continue
            wunsch[col] = max(wunsch.get(col, 0),
                              breite(col) + (noetig - verf) / L.MDW + 0.3)

        geaendert = False
        for col, neu in sorted(wunsch.items()):
            alt = breite(col)
            neu = min(maxsp, neu)
            if neu > alt + 0.05:
                setze(col, neu)
                bericht.append(f'{ws.title}: Spalte {col} {alt:.1f} → {neu:.1f}')
                geaendert = True
        if not geaendert:
            break

    for col, w in fest.items():
        if abs(breite(col) - w) > 0.05:
            bericht.append(f'{ws.title}: Spalte {col} {breite(col):.1f} → {w:.1f} (fest)')
            setze(col, w)

    # -------------------------------------- 2) Umbruch und 3) Zeilenhoehen
    hoehen = {}
    for c, t, ist_zahl, m in zellen:
        if m:
            spalten = [breite(get_column_letter(x))
                       for x in range(m.min_col, m.max_col + 1)]
            zeilen_im_block = m.max_row - m.min_row + 1
        else:
            spalten = spann(c, ist_zahl)
            zeilen_im_block = 1
        verf = L.nutz_px(spalten) - L.einzug_px(c)
        if verf <= 0:
            continue

        passt = all(L.text_px(x, c.font) * SICHERHEIT <= verf for x in t.split('\n'))
        if not passt and not ist_zahl and not c.alignment.wrap_text:
            a = c.alignment
            c.alignment = Alignment(horizontal=a.horizontal, vertical=a.vertical,
                                    wrap_text=True, indent=a.indent,
                                    text_rotation=a.text_rotation,
                                    shrink_to_fit=False)
            bericht.append(f'{ws.title}: {c.coordinate} umgebrochen')

        if c.alignment.wrap_text and not ist_zahl:
            zeilen = L.zeilen_zahl(t, c.font, verf)
        else:
            zeilen = len(t.split('\n'))
        noetig = L.hoehe_pt(zeilen, c.font)
        # Bei einem Verbund ueber mehrere Zeilen verteilt sich die Hoehe.
        anteil = noetig / zeilen_im_block
        for r in range(c.row, c.row + zeilen_im_block):
            hoehen[r] = max(hoehen.get(r, 0), anteil)

    for r, h in sorted(hoehen.items()):
        aktuell = ws.row_dimensions[r].height or L.STANDARD_HOEHE
        if h > aktuell + 0.2:
            ws.row_dimensions[r].height = round(h, 2)
            bericht.append(f'{ws.title}: Zeile {r} Höhe {aktuell:.0f} → {h:.0f} pt')

    # ------------------------------------------------ 4) Seiteneinrichtung
    gesamt_px = sum(breite(get_column_letter(c)) * L.MDW + 5
                    for c in range(grenze[0], grenze[2] + 1))
    quer = ws.page_setup.orientation == 'landscape'
    platz_b = (A4[1] if quer else A4[0]) * DPI - 2 * RAND * DPI
    platz_h = ((A4[0] if quer else A4[1])
               - (ws.page_margins.top or 0.75) - (ws.page_margins.bottom or 0.75)) * 72

    seiten = SEITEN_BREIT.get(ws.title, 1)
    ws.page_setup.fitToWidth = seiten
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    skala = min(1.0, platz_b * seiten / gesamt_px)

    gesamt_pt = sum(ws.row_dimensions[r].height or L.STANDARD_HOEHE
                    for r in range(grenze[1], grenze[3] + 1))
    # Nur ein Blatt, das auch der Hoehe nach beinahe auf eine Seite passt, darf
    # auf eine Seite gezwungen werden. Sonst quetscht Excel es zusammen, bis
    # nichts mehr lesbar ist - genau das war beim Blatt «Wahrscheinlichkeit»
    # der Fall (25 %).
    skala_hoch = platz_h / gesamt_pt if gesamt_pt else 1.0
    passt_hoch = (min(skala, skala_hoch) >= skala * OHNE_VERLUST
                  and min(skala, skala_hoch) >= MIN_SKALIERUNG)
    ws.page_setup.fitToHeight = 1 if passt_hoch else 0
    if passt_hoch:
        skala = min(skala, skala_hoch)
    umbrueche = SEITEN_UMBRUCH.get(ws.title, [])
    if umbrueche and not passt_hoch:
        ws.row_breaks = RowBreak()
        for r in umbrueche:
            ws.row_breaks.append(Break(id=r))
    bericht.append(f'{ws.title}: Druck {seiten} Seite(n) breit, '
                   f'Massstab {skala:.0%}, Höhe {"1 Seite" if passt_hoch else "fortlaufend"}')

    if seiten > 1:
        if ws.title in WIEDERHOLEN:
            ws.print_title_cols = WIEDERHOLEN[ws.title]
        # Titel linksbuendig, damit sie nicht an der Seitengrenze abreissen.
        for m in list(ws.merged_cells.ranges):
            if m.min_row > 3 or m.max_col - m.min_col < 3:
                continue
            z = ws.cell(row=m.min_row, column=m.min_col)
            if z.alignment.horizontal in (None, 'center'):
                a = z.alignment
                z.alignment = Alignment(horizontal='left', vertical=a.vertical,
                                        wrap_text=a.wrap_text, indent=1)

wb.save(F)
print(f'Layout gesetzt: {len(bericht)} Änderungen')
for b in bericht[:60]:
    print('  ', b)
if len(bericht) > 60:
    print(f'   ... und {len(bericht) - 60} weitere')
