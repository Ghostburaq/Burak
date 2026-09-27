# -*- coding: utf-8 -*-
"""
mit_deck - Baukasten fuer Praesentationen im Design der Mobil in Time AG.

Setzt auf assets/mit_vorlage.pptx auf. Diese Datei enthaelt den Original-Master
der MiT-Vorlage: Hintergrundgrafiken (roter Keil, roter Streifen, graues
Dreieck, rotes Parallelogramm), das Logo oben rechts und die Theme-Schriften
Alata (Titel) und IBM Plex Sans (Fliesstext).

Benutzung:

    from mit_deck import Deck
    d = Deck("out.pptx", footer="MiT Strom · Projekt X · 27.09.2026")
    d.cover("Titel der Praesentation", "Untertitel",
            eyebrow="Mobil in Time AG · An Aggreko Company",
            author="Burak Ücöz · Sales Engineer Power · 27.09.2026",
            stats=[("29", "Projekte"), ("145", "Kontakte")])
    s = d.content("01 · Ausgangslage", "Worum es geht")
    d.cards(s, [("Titel A", ["Text"]), ("Titel B", ["Text"])], cols=2)
    d.closing("Der eine Hebel", ["Satz 1.", "Satz 2."], "Burak Ücöz")
    d.save()

Alle Masse in Zoll. Folie ist 13.33 x 7.5 (16:9).
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "mit_vorlage.pptx")

# ---------------------------------------------------------------- Designwerte
RED = RGBColor(0xE0, 0x00, 0x36)      # MiT-Rot, Signalfarbe
DARK = RGBColor(0x58, 0x59, 0x5B)     # Kachelgrau / Fliesstext
DARKER = RGBColor(0x3C, 0x3C, 0x3B)   # zweite Grauabstufung
BLACK = RGBColor(0x00, 0x00, 0x00)    # Titel
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xE6, 0xE6, 0xE6)     # Text auf dunklen Kacheln
LIGHT = RGBColor(0xF2, 0xF2, 0xF2)    # helle Kachel / Statement-Band
LINE = RGBColor(0xD6, 0xD6, 0xD6)
ROW_A = RGBColor(0xFF, 0xFF, 0xFF)
ROW_B = RGBColor(0xF4, 0xF4, 0xF4)

F_TITLE = "Alata"            # Major-Font des Masters
F_BODY = "IBM Plex Sans"     # Minor-Font des Masters

# Raster: linker Rand 0.47, rechter Rand 12.40 (danach beginnt das graue Dreieck),
# Titelzone ab 1.74 (rechts vom roten Streifen, endet vor dem Logo bei 10.69).
L, R = 0.47, 12.40
W = R - L
T_L, T_W = 1.74, 8.95
BODY_TOP = 2.05        # oberste Kante des Inhaltsbereichs
BODY_BOTTOM = 6.70     # unterste Kante, darunter die Fusszeile
FOOT_Y = 6.95

NOSTYLE = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'


def cols(n, gap=0.22, left=L, width=W):
    """Spaltenraster: gibt (x-Liste, Spaltenbreite) zurueck."""
    w = (width - gap * (n - 1)) / n
    return [left + i * (w + gap) for i in range(n)], w


class Deck(object):
    def __init__(self, path, footer="", template=TEMPLATE):
        self.path = path
        self.footer_text = footer
        self.prs = Presentation(template)
        lst = self.prs.slides._sldIdLst
        for sld in list(lst):                 # Template ist leer, sicherheitshalber
            self.prs.part.drop_rel(sld.get(qn('r:id')))
            lst.remove(sld)
        self._lay = {l.name: l for l in self.prs.slide_masters[0].slide_layouts}
        self.page = 0

    # ------------------------------------------------------------- Primitive
    def _slide(self, layout_name):
        s = self.prs.slides.add_slide(self._lay[layout_name])
        for ph in list(s.placeholders):       # Platzhalter raus, wir setzen selbst
            ph._element.getparent().remove(ph._element)
        return s

    def tb(self, s, x, y, w, h, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
        box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = anchor
        tf.paragraphs[0].alignment = align
        return tf

    def run(self, p, text, size, color, font=F_BODY, bold=False, spc=None, caps=False):
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.name = font
        r.font.bold = bold
        rPr = r._r.get_or_add_rPr()
        if spc is not None:
            rPr.set('spc', str(int(spc * 100)))   # Laufweite in Punkt
        if caps:
            rPr.set('cap', 'all')
        return r

    def para(self, tf, first=False, space_before=0, space_after=0, line=None, align=None):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        p.space_before = Pt(space_before)
        p.space_after = Pt(space_after)
        if line:
            p.line_spacing = line
        if align:
            p.alignment = align
        return p

    def rect(self, s, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE):
        sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
        sh.line.fill.background()
        sh.shadow.inherit = False
        sh.text_frame.word_wrap = True
        return sh

    def badge(self, s, x, y, size, label, fill=RED, fs=16, fg=WHITE,
              shape=MSO_SHAPE.RECTANGLE):
        """Quadratisches Nummernfeld. shape=MSO_SHAPE.OVAL fuer Kreis."""
        sh = self.rect(s, x, y, size, size, fill, shape)
        tf = sh.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        self.run(p, label, fs, fg, F_TITLE)
        return sh

    # ---------------------------------------------------------- Folientypen
    def cover(self, title, subtitle="", eyebrow="", author="", stats=None):
        """Titelfolie. Text steht rechts vom roten Keil, stats stehen im Keil.
        title darf eine Liste von Zeilen sein. stats = [(Zahl, Label), ...]."""
        s = self._slide('Titelfolie')
        if eyebrow:
            tf = self.tb(s, 4.55, 1.55, 7.60, 0.30)
            self.run(tf.paragraphs[0], eyebrow, 10.5, DARK, F_BODY,
                     bold=True, spc=1.6, caps=True)
        lines = title if isinstance(title, (list, tuple)) else [title]
        tf = self.tb(s, 4.55, 2.05, 7.80, 1.90)
        for i, t in enumerate(lines):
            p = self.para(tf, first=(i == 0), line=0.95)
            self.run(p, t, 40, BLACK, F_TITLE)
        self.rect(s, 4.55, 4.12, 1.40, 0.05, RED)
        if subtitle:
            tf = self.tb(s, 4.55, 4.42, 7.60, 0.45)
            self.run(tf.paragraphs[0], subtitle, 17, DARK)
        if author:
            tf = self.tb(s, 4.55, 6.30, 7.60, 0.30)
            self.run(tf.paragraphs[0], author, 11.5, DARK)
        if stats:
            tf = self.tb(s, 0.62, 2.85, 2.20, 1.70)
            for i, (val, lab) in enumerate(stats[:2]):
                p = self.para(tf, first=(i == 0), space_before=0 if i == 0 else 12, line=0.90)
                self.run(p, val, 34, WHITE, F_TITLE)
                p = self.para(tf, space_before=1, line=1.0)
                self.run(p, lab, 11, WHITE)
        self.page = 1
        return s

    def content(self, eyebrow, title, page=None):
        """Inhaltsfolie mit Eyebrow (rot, gesperrt), Titel und rotem Strich.
        Titelgroesse passt sich der Laenge an. Gibt die Folie zurueck."""
        s = self._slide('Titel und Inhalt')
        tf = self.tb(s, T_L, 0.40, T_W, 0.30)
        self.run(tf.paragraphs[0], eyebrow, 10.5, RED, F_BODY,
                 bold=True, spc=1.6, caps=True)
        size = 28 if len(title) <= 34 else (26 if len(title) <= 46 else 22)
        tf = self.tb(s, T_L, 0.72, T_W, 1.00)
        p = tf.paragraphs[0]
        p.line_spacing = 0.94
        self.run(p, title, size, BLACK, F_TITLE)
        self.rect(s, T_L, 1.72, 1.10, 0.045, RED)
        self.page += 1
        self.footer(s, page if page is not None else self.page)
        return s

    def section(self, title, lines=None):
        """Abschnittstrenner auf dem roten Parallelogramm."""
        s = self._slide('Nur Titel')
        tf = self.tb(s, 4.60, 2.60, 5.45, 0.32)
        self.run(tf.paragraphs[0], title, 12, WHITE, F_BODY, bold=True, spc=1.8, caps=True)
        tf = self.tb(s, 4.60, 3.10, 5.45, 1.80)
        for i, t in enumerate(lines or []):
            p = self.para(tf, first=(i == 0), space_before=0 if i == 0 else 10, line=1.0)
            self.run(p, t, 24, WHITE, F_TITLE)
        self.page += 1
        return s

    def closing(self, eyebrow, lines, signature=None):
        """Schlussfolie auf dem roten Parallelogramm.
        Zeilen bleiben unter ca. 30 Zeichen, sonst brechen sie um."""
        s = self._slide('Nur Titel')
        tf = self.tb(s, 4.60, 1.90, 5.45, 0.32)
        self.run(tf.paragraphs[0], eyebrow, 12, WHITE, F_BODY, bold=True, spc=1.8, caps=True)
        tf = self.tb(s, 4.60, 2.42, 5.45, 2.30)
        for i, t in enumerate(lines):
            p = self.para(tf, first=(i == 0), space_before=0 if i == 0 else 12, line=1.0)
            self.run(p, t, 24, WHITE, F_TITLE)
        self.rect(s, 4.60, 4.85, 1.20, 0.05, WHITE)
        if signature:
            sig = signature if isinstance(signature, (list, tuple)) else [signature]
            tf = self.tb(s, 4.60, 5.15, 4.40, 0.60)
            for i, t in enumerate(sig):
                p = self.para(tf, first=(i == 0), space_before=0 if i == 0 else 3)
                self.run(p, t, 11.5, WHITE)
        self.page += 1
        return s

    # -------------------------------------------------------------- Bausteine
    def footer(self, s, num):
        if self.footer_text:
            tf = self.tb(s, T_L, FOOT_Y, 8.60, 0.28)
            self.run(tf.paragraphs[0], self.footer_text, 8.5, DARK)
        tf = self.tb(s, 11.10, FOOT_Y, 1.00, 0.28, align=PP_ALIGN.RIGHT)
        self.run(tf.paragraphs[0], str(num), 8.5, DARK)

    def cards(self, s, items, cols_n=3, y=BODY_TOP + 0.10, h=None, rows=1,
              gap_y=0.25, numbered=False, hs=16, bs=12.5):
        """Kachelraster. items = [(Titel, [Textzeilen], fill?) ...].
        fill ist optional, Standard DARK. Mit numbered=True bekommt jede Kachel
        ein rotes Nummernfeld. Rote Kacheln fuer das, was hervorstechen soll."""
        xs, cw = cols(cols_n)
        if h is None:
            h = (BODY_BOTTOM - y - gap_y * (rows - 1)) / rows
        for i, item in enumerate(items):
            head, body = item[0], item[1]
            fill = item[2] if len(item) > 2 else DARK
            x = xs[i % cols_n]
            yy = y + (i // cols_n) * (h + gap_y)
            self.rect(s, x, yy, cw, h, fill)
            ty = yy + 0.32
            if numbered:
                self.badge(s, x + 0.35, yy + 0.32, 0.62, str(i + 1),
                           WHITE if fill == RED else RED, 16,
                           RED if fill == RED else WHITE)
                tf = self.tb(s, x + 1.15, yy + 0.40, cw - 1.45, 0.50)
                self.run(tf.paragraphs[0], head, hs, WHITE, F_BODY, bold=True)
                ty = yy + 1.22
            else:
                tf = self.tb(s, x + 0.32, ty, cw - 0.64, 0.50)
                p = tf.paragraphs[0]
                p.line_spacing = 0.95
                self.run(p, head, hs, WHITE, F_BODY, bold=True)
                ty = yy + 0.90
            tf = self.tb(s, x + 0.32, ty, cw - 0.64, h - (ty - yy) - 0.25)
            for j, line in enumerate(body):
                p = self.para(tf, first=(j == 0), space_before=0 if j == 0 else 4, line=1.05)
                self.run(p, line, bs, WHITE if fill == RED else SOFT)

    def kpis(self, s, items, y=BODY_TOP + 0.10):
        """Kennzahlenreihe: items = [(Wert, Label), ...], maximal sechs."""
        xs, cw = cols(len(items))
        for (val, lab), x in zip(items, xs):
            self.rect(s, x, y, 0.70, 0.045, RED)
            tf = self.tb(s, x, y + 0.25, cw, 0.95)
            p = tf.paragraphs[0]
            p.line_spacing = 0.90
            self.run(p, val, 40, BLACK, F_TITLE)
            tf = self.tb(s, x, y + 1.30, cw - 0.25, 0.90)
            p = tf.paragraphs[0]
            p.line_spacing = 1.05
            self.run(p, lab, 11.5, DARK)

    def steps(self, s, items, y=2.68):
        """Prozesskette mit Nummernfeldern und Verbindungslinie.
        items = [(Nummer, Titel, [Textzeilen]), ...]"""
        xs, cw = cols(len(items))
        self.rect(s, xs[0] + 0.42, y + 0.38, xs[-1] - xs[0] + 0.02, 0.02, LINE)
        for (num, head, body), x in zip(items, xs):
            self.badge(s, x, y, 0.84, num, RED, 18)
            tf = self.tb(s, x, y + 1.17, cw - 0.30, 0.50)
            self.run(tf.paragraphs[0], head, 17, BLACK, F_BODY, bold=True)
            tf = self.tb(s, x, y + 1.77, cw - 0.30, 1.40)
            for j, line in enumerate(body):
                p = self.para(tf, first=(j == 0), space_before=0 if j == 0 else 2, line=1.1)
                self.run(p, line, 12, DARK)

    def band(self, s, y, text, bold_prefix="", fill=DARK, h=1.25, fs=15):
        """Aussagen-Band ueber die volle Breite. fill=LIGHT fuer die helle Variante."""
        self.rect(s, L, y, W, h, fill)
        tf = self.tb(s, L + 0.45, y + 0.27, W - 0.90, h - 0.5)
        p = tf.paragraphs[0]
        p.line_spacing = 1.05
        fg = DARK if fill == LIGHT else WHITE
        if bold_prefix:
            self.run(p, bold_prefix + " ", fs, fg, F_BODY, bold=True)
        self.run(p, text, fs, DARK if fill == LIGHT else SOFT)

    def table(self, s, rows, colw, y=BODY_TOP, h=4.20, fs=11, head_fs=11,
              head_fill=RED, x=L, w=W):
        """Tabelle im MiT-Look: roter Kopf, weisse Typo, Zebrazeilen.
        rows = Liste von Zeilen (erste Zeile ist der Kopf), colw = Spaltengewichte."""
        gt = s.shapes.add_table(len(rows), len(colw), Inches(x), Inches(y),
                                Inches(w), Inches(h))
        tbl = gt.table
        tblPr = tbl._tbl.find(qn('a:tblPr'))
        for e in tblPr.findall(qn('a:tableStyleId')):
            tblPr.remove(e)
        sid = tblPr.makeelement(qn('a:tableStyleId'), {})
        sid.text = NOSTYLE
        tblPr.append(sid)
        tbl.first_row = False
        tbl.horz_banding = False
        total = float(sum(colw))
        for i, c in enumerate(colw):
            tbl.columns[i].width = Emu(int(Inches(w) * c / total))
        head_h = 0.42
        row_h = max(0.32, (h - head_h) / max(1, len(rows) - 1))
        for ri, rowdata in enumerate(rows):
            tbl.rows[ri].height = Inches(head_h if ri == 0 else row_h)
            for ci, val in enumerate(rowdata):
                cell = tbl.cell(ri, ci)
                cell.margin_left = Inches(0.12)
                cell.margin_right = Inches(0.10)
                cell.margin_top = Inches(0.05)
                cell.margin_bottom = Inches(0.05)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                cell.fill.solid()
                cell.fill.fore_color.rgb = (head_fill if ri == 0
                                            else (ROW_A if ri % 2 else ROW_B))
                p = cell.text_frame.paragraphs[0]
                cell.text_frame.word_wrap = True
                p.line_spacing = 1.0
                self.run(p, val, head_fs if ri == 0 else fs,
                         WHITE if ri == 0 else DARK, F_BODY,
                         bold=(ri == 0 or ci == 0))
        return tbl

    def notes(self, s, text):
        s.notes_slide.notes_text_frame.text = text

    def save(self, title=None, author=None, subject=None):
        cp = self.prs.core_properties
        if title:
            cp.title = title
        if author:
            cp.author = author
        if subject:
            cp.subject = subject
        self.prs.save(self.path)
        return self.path
