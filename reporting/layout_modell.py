#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemeinsames Mass-Modell fuer Layout-Bau (build_layout.py) und Layout-Pruefung
(audit_layout.py).

Beide muessen mit demselben Lineal messen, sonst baut die eine Seite etwas, das
die andere Seite anschliessend beanstandet.

Grundlagen:
  * Excel misst Spaltenbreiten in Vielfachen der Breite der Ziffer 0 der
    Standardschrift (Calibri 11 -> 7 px bei 96 dpi).
  * Die Pixelbreite einer Spalte ist  Breite * 7 + 5  (2 px Innenabstand links,
    2 px rechts, 1 px Gitternetzlinie). Fuer Text nutzbar sind davon  Breite * 7.
  * Die Zeilenhoehe fuer eine Textzeile betraegt  Schriftgrad * 1.34 pt
    (11 pt -> 14.7 ~ 15 pt, 14 pt -> 18.8 ~ 18.75 pt) - genau das, was Excel
    beim automatischen Anpassen der Zeilenhoehe einstellt.
"""
import math

MDW = 7.0          # px, Breite der Ziffer 0 in Calibri 11

# Zeilenhoehe in pt, die Excel beim automatischen Anpassen fuer eine Textzeile
# des jeweiligen Schriftgrads einstellt (Calibri). Dazwischen wird interpoliert.
AUTOFIT = {8: 11.25, 9: 12.0, 10: 12.75, 11: 15.0, 12: 15.75, 13: 16.5,
           14: 18.75, 16: 21.0, 18: 23.25, 20: 26.25, 22: 28.5, 24: 30.75,
           28: 36.0, 36: 45.75}

# Zeichenbreiten Calibri 11 in Pixeln (96 dpi). Andere Schriften werden ueber
# einen Faktor angenaehert.
_B = {
    ' ': 3, '!': 4, '"': 5, '#': 7, '$': 7, '%': 11, '&': 10, "'": 3,
    '(': 4, ')': 4, '*': 6, '+': 7, ',': 3, '-': 4, '.': 3, '/': 6,
    ':': 3, ';': 3, '<': 7, '=': 7, '>': 7, '?': 6, '@': 12,
    '[': 4, '\\': 6, ']': 4, '^': 7, '_': 6, '`': 5,
    '{': 4, '|': 3, '}': 4, '~': 7,
    'A': 8, 'B': 7, 'C': 8, 'D': 9, 'E': 7, 'F': 6, 'G': 9, 'H': 9, 'I': 4,
    'J': 4, 'K': 7, 'L': 6, 'M': 13, 'N': 9, 'O': 10, 'P': 7, 'Q': 10,
    'R': 8, 'S': 7, 'T': 7, 'U': 9, 'V': 8, 'W': 13, 'X': 7, 'Y': 7, 'Z': 7,
    'a': 6, 'b': 7, 'c': 6, 'd': 7, 'e': 7, 'f': 4, 'g': 7, 'h': 7, 'i': 3,
    'j': 3, 'k': 6, 'l': 3, 'm': 11, 'n': 7, 'o': 7, 'p': 7, 'q': 7, 'r': 5,
    's': 6, 't': 5, 'u': 7, 'v': 6, 'w': 10, 'x': 6, 'y': 6, 'z': 6,
}
for _z in '0123456789':
    _B[_z] = 7
for _gross, _klein in (('ÄÖÜ', 'AOU'), ('äöü', 'aou'), ('ÀÁÂÃ', 'AAAA'),
                       ('àáâãå', 'aaaaa'), ('èéêë', 'eeee'), ('ìíîï', 'iiii'),
                       ('òóôõ', 'oooo'), ('ùúûü', 'uuuu'), ('çÇñÑ', 'cCnN')):
    for _a, _b in zip(_gross, _klein):
        _B[_a] = _B[_b]
_B['ß'] = 7
_B['€'] = 7
_B['·'] = 4
_B['–'] = 7      # Halbgeviertstrich
_B['—'] = 11     # Geviertstrich
_B['«'] = 6
_B['»'] = 6
_B['„'] = 5
_B['“'] = 5
_B['”'] = 5
_B['…'] = 11
_B[' '] = 3   # geschuetztes Leerzeichen
_B[' '] = 2   # schmales Leerzeichen

STANDARD_ZEICHEN = 7      # unbekanntes lateinisches Zeichen
SYMBOL_ZEICHEN = 12       # Pfeile, mathematische Zeichen, Dingbats
EMOJI_ZEICHEN = 15        # Farbemoji: rund ein Geviert breit

# Schriftfaktoren bezogen auf Calibri
SCHRIFT_FAKTOR = {'Calibri': 1.00, 'Arial': 1.07, 'Helvetica': 1.07,
                  'Cambria': 1.04, 'Consolas': 1.10, 'Courier New': 1.15,
                  'Times New Roman': 0.98, 'Verdana': 1.16, 'Segoe UI': 1.03}

STANDARD_BREITE = 8.43    # Excel-Standardspaltenbreite
STANDARD_HOEHE = 15.0     # pt


def _zeichen_px(ch):
    if ch in _B:
        return _B[ch]
    o = ord(ch)
    if o in (0xFE0F, 0xFE0E, 0x200D):     # Variantenselektor / Verbinder
        return 0
    if o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x2B50, 0x2B55):
        return EMOJI_ZEICHEN
    if 0x2000 <= o <= 0x2BFF:
        return SYMBOL_ZEICHEN
    return STANDARD_ZEICHEN


# Arial/Helvetica ist deutlich breiter als Calibri und im File die zweit-
# haeufigste Schrift. Ein blosser Umrechnungsfaktor traf um bis zu 9 % daneben -
# deshalb die Originalbreiten (Tausendstel Geviert), wie sie auch Liberation
# Sans verwendet.
_ARIAL = {
    ' ': 278, '!': 278, '"': 355, '#': 556, '$': 556, '%': 889, '&': 667,
    "'": 191, '(': 333, ')': 333, '*': 389, '+': 584, ',': 278, '-': 333,
    '.': 278, '/': 278, ':': 278, ';': 278, '<': 584, '=': 584, '>': 584,
    '?': 556, '@': 1015, '[': 278, '\\': 278, ']': 278, '^': 469, '_': 556,
    '`': 333, '{': 334, '|': 260, '}': 334, '~': 584,
    'A': 667, 'B': 667, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778,
    'H': 722, 'I': 278, 'J': 500, 'K': 667, 'L': 556, 'M': 833, 'N': 722,
    'O': 778, 'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722,
    'V': 667, 'W': 944, 'X': 667, 'Y': 667, 'Z': 611,
    'a': 556, 'b': 556, 'c': 500, 'd': 556, 'e': 556, 'f': 278, 'g': 556,
    'h': 556, 'i': 222, 'j': 222, 'k': 500, 'l': 222, 'm': 833, 'n': 556,
    'o': 556, 'p': 556, 'q': 556, 'r': 333, 's': 500, 't': 278, 'u': 556,
    'v': 500, 'w': 722, 'x': 500, 'y': 500, 'z': 500,
}
for _z in '0123456789':
    _ARIAL[_z] = 556
for _gross, _klein in (('ÄÖÜ', 'AOU'), ('äöü', 'aou'), ('ÀÁÂÃÅ', 'AAAAA'),
                       ('àáâãå', 'aaaaa'), ('èéêë', 'eeee'), ('ìíîï', 'iiii'),
                       ('òóôõ', 'oooo'), ('ùúûü', 'uuuu'), ('çÇñÑ', 'cCnN')):
    for _a, _b in zip(_gross, _klein):
        _ARIAL[_a] = _ARIAL[_b]
_ARIAL.update({'ß': 611, '€': 556, '·': 278, '–': 556, '—': 1000, '«': 556,
               '»': 556, '„': 333, '“': 333, '”': 333, '…': 1000,
               ' ': 278, ' ': 200})
_ARIAL_UNBEKANNT = 556
_ARIAL_SYMBOL = 800
_ARIAL_EMOJI = 1100

ARIAL_FAMILIE = {'Arial', 'Helvetica', 'Liberation Sans', 'Arial Narrow'}


def _arial_px(text, size):
    summe = 0
    for ch in text:
        if ch in _ARIAL:
            summe += _ARIAL[ch]
            continue
        o = ord(ch)
        if o in (0xFE0F, 0xFE0E, 0x200D):
            continue
        if o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x2B50, 0x2B55):
            summe += _ARIAL_EMOJI
        elif 0x2000 <= o <= 0x2BFF:
            summe += _ARIAL_SYMBOL
        else:
            summe += _ARIAL_UNBEKANNT
    return summe / 1000.0 * size * (96.0 / 72.0)


def text_px(text, font=None):
    """Breite einer Textzeile in Pixeln."""
    size = 11.0
    name = 'Calibri'
    fett = False
    if font is not None:
        size = font.size or 11.0
        name = font.name or 'Calibri'
        fett = bool(font.bold)
    if name in ARIAL_FAMILIE:
        breite = _arial_px(text, size)
        if fett:
            breite *= 1.07
        return breite
    f = SCHRIFT_FAKTOR.get(name, 1.05) * (size / 11.0)
    if fett:
        f *= 1.04
    return sum(_zeichen_px(c) for c in text) * f


def einzug_px(cell):
    """Platz, den ein eingestellter Einzug am Zellenrand wegnimmt."""
    stufen = (cell.alignment.indent or 0)
    beidseitig = 2 if cell.alignment.horizontal == 'center' else 1
    return stufen * MDW * beidseitig


def nutz_px(breiten):
    """Fuer Text nutzbare Pixel einer Spalte oder einer Spaltenfolge (Verbund).

    Eine einzelne Spalte der Breite b ist b*7+5 px breit, davon 5 px
    Innenabstand. Bei mehreren Spalten faellt der Innenabstand nur einmal an.
    """
    if not isinstance(breiten, (list, tuple)):
        breiten = [breiten]
    breiten = [b for b in breiten if b and b > 0]      # ausgeblendete zaehlen nicht
    if not breiten:
        return 0.0
    return max(0.0, sum(b * MDW + 5 for b in breiten) - 5)


def breite_fuer_px(px):
    """Spaltenbreite, die die angegebene Pixelzahl fuer Text bereitstellt."""
    return max(0.0, px / MDW)


def zeilen_zahl(text, font, verf_px):
    """Wieviele Bildschirmzeilen braucht der Text bei Umbruch?

    Excel bricht an Wortgrenzen um, nicht mitten im Wort. Deshalb wird der
    Umbruch hier Wort fuer Wort nachgestellt - eine Rechnung ueber die reine
    Textlaenge zaehlt sonst regelmaessig eine Zeile zu wenig.
    """
    verf_px = max(1.0, verf_px)
    n = 0
    for absatz in text.split('\n'):
        if not absatz.strip():
            n += 1
            continue
        zeile = 0.0
        n += 1
        for wort in absatz.split(' '):
            w = text_px(wort, font)
            leer = text_px(' ', font)
            if zeile == 0.0:
                gebraucht = w
            else:
                gebraucht = zeile + leer + w
            if gebraucht <= verf_px:
                zeile = gebraucht
                continue
            # Wort passt nicht mehr in diese Zeile
            if w <= verf_px:
                n += 1
                zeile = w
            else:
                # Einzelnes Wort ist breiter als die Spalte: Excel bricht es hart
                if zeile > 0:
                    n += 1
                stuecke = math.ceil(w / verf_px)
                n += stuecke - 1
                zeile = w - (stuecke - 1) * verf_px
    return n


def zeilenhoehe(size):
    """Hoehe einer Textzeile in pt - wie Excels automatische Zeilenhoehe."""
    size = float(size or 11)
    if size in AUTOFIT:
        return AUTOFIT[size]
    stufen = sorted(AUTOFIT)
    if size < stufen[0]:
        return round(size * AUTOFIT[stufen[0]] / stufen[0], 2)
    if size > stufen[-1]:
        return round(size * AUTOFIT[stufen[-1]] / stufen[-1], 2)
    for a, b in zip(stufen, stufen[1:]):
        if a < size < b:
            anteil = (size - a) / (b - a)
            return round(AUTOFIT[a] + anteil * (AUTOFIT[b] - AUTOFIT[a]), 2)
    return round(size * 1.34, 2)


def hoehe_pt(zeilen, font=None):
    size = (font.size if font is not None and font.size else 11.0)
    return round(zeilen * zeilenhoehe(size), 2)


def spaltenkarte(ws):
    """Breite und Sichtbarkeit je Spaltennummer.

    openpyxl fasst gleichartige Spalten zu Gruppen zusammen ('J' steht dann
    stellvertretend fuer J:L). Ein Zugriff ueber den einzelnen Buchstaben legt
    still eine neue, sichtbare Spalte an - deshalb wird die Gruppe hier
    aufgeloest, statt sie einzeln abzufragen.
    """
    karte = {}
    for d in ws.column_dimensions.values():
        von = d.min or 1
        bis = d.max or von
        for i in range(von, bis + 1):
            karte[i] = (0.0 if d.hidden else (d.width if d.width else STANDARD_BREITE),
                        bool(d.hidden))
    return karte


def formatiert(v, fmt):
    """Wie erscheint ein Zahlenwert mit seinem Zahlenformat?"""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    f = (fmt or 'General').split(';')[0].strip()
    suffix = ''
    if '"' in f:
        teile = f.split('"')
        if len(teile) >= 3:
            suffix = teile[1]
        f = teile[0]
    try:
        if '%' in f:
            nk = len(f.split('.')[1].split('%')[0]) if '.' in f else 0
            t = f'{v * 100:.{nk}f}'.replace('.', ',') + '%'
        elif f in ('', 'General'):
            t = f'{v:g}' if v != int(v) else f'{int(v)}'
        else:
            nk = len(f.split('.')[1]) if '.' in f else 0
            if ',' in f or "'" in f:
                t = f'{v:,.{nk}f}'.replace(',', "'")
            else:
                t = f'{v:.{nk}f}'
            t = t.replace('.', ',') if nk else t
    except Exception:
        t = f'{v:g}'
    return t + suffix


def anzeige(cell, wert):
    """Der Text, den die Zelle zeigt - Formelergebnis und Zahlenformat beruecksichtigt."""
    v = cell.value
    if isinstance(v, str) and v.startswith('='):
        v = wert
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return formatiert(v, cell.number_format)
    if isinstance(v, str):
        return v if v.strip() else None
    return str(v)
