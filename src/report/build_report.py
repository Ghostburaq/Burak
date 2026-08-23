#!/usr/bin/env python3
"""Setzt den Schlussbericht aus dem Inhaltsmodell neu.

Der Bericht wird vollständig aus ``build/content.json`` und dem
Gestaltungssystem in ``design.py`` aufgebaut: Deckblatt, Inhaltsverzeichnis,
Kapitel, Tabellen, Hinweiskästen, Bilddokumentation und Schlussseite.

    python3 src/report/build_report.py            # Bericht bauen
    python3 src/report/build_report.py --template # zusätzlich die Wordvorlage

Das Inhaltsverzeichnis entsteht in zwei Durchgängen: ``make_pdf.py`` liest
die tatsächlichen Seitenzahlen aus dem PDF und schreibt sie nach
``build/toc_pages.json``; beim nächsten Bau stehen sie als Feldergebnis im
Verzeichnis. Word aktualisiert sie mit F9 jederzeit selbst.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import docx
from docx.oxml.ns import qn
from docx.shared import Cm, Emu, Pt
from PIL import Image

from design import (
    ACCENT, ALIGN, BAND, BODY, CONTENT_W, FONT, HAIR, INK, LANG, LINE_BODY,
    LINE_TIGHT, MARGIN_BOT, MARGIN_TOP, MARGIN_X, MONO, NBSP, PAGE_H, PAGE_W,
    PANEL, RULE, STEEL, STEEL_LT, SZ_BODY, SZ_CAPTION, SZ_H1, SZ_H2, SZ_H3,
    SZ_MONO, SZ_SMALL, SZ_TABLE, SZ_TABLE_HEAD, SP_BODY_AFTER, bookmark,
    borders, cell_margins, cell_style, clear_cell, el, field, hyperlink_to,
    looks_numeric, normalize, para, row_rules, run, shade, table_frame, tabs,
    typo,
)

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "build" / "content.json"
TOC_PAGES = ROOT / "build" / "toc_pages.json"
MEDIA = ROOT / "assets" / "report" / "media"
LOGO = ROOT / "assets" / "report" / "logo"
OUT_DOCX = ROOT / "Schlussbericht_Kreuz_Zuzwil.docx"
OUT_DOTX = ROOT / "Vorlage_kabuu_Bericht.dotx"

TITLE = "Netzqualitätsmessung und Ursachenanalyse Lichtflackern"
OBJECT = "Gasthaus Kreuz, Oberdorfstrasse 16, 9524 Zuzwil SG"
SHORT = "Gasthaus Kreuz, Zuzwil SG"
RUNNING_TITLE = "Schlussbericht Netzqualitätsmessung"
STAND = "23.08.2026"
CAMPAIGN = ("Messkampagne 05.08.2026 bis 17.08.2026 · 3 Messpunkte · "
            "IEC 61000-4-30 Ed.3 Class A")
CONTACT = "kabuu · Netzqualität & EMV Messungen · Burak Ücöz"
AUTHOR = "Burak Ücöz"
COMPANY = "kabuu — Netzqualität & EMV Messungen"
REPORT_DATE = datetime(2026, 8, 23)

# Tabellen, deren Kopfzeile keine Spaltentitel enthält, sondern bereits Daten.
HEADER_MAX_CHARS = 40
MIN_COL_TEXT, MIN_COL_NUM = 980, 620
# Bis zu dieser Zeilenzahl wird eine Tabelle nie umbrochen.
ATOMIC_ROWS = 6
# Ab dieser Zellenlänge gilt eine Spalte als Text, nicht als Zahlenspalte.
NUMERIC_MAX_CHARS = 20
# Schreibhöhe für die leeren Zeilen eines Erhebungsblatts.
FORM_ROW_HEIGHT = 420
# Breite der Beschriftungsspalte in der Bilddokumentation.
PHOTO_LABEL_W = 1000
SYMBOLS = {"+", "○", "−", "-", "—", "✓", "–"}
BULLET_NUM = 10
ORDERED_NUMS = tuple(range(20, 44))


# ---------------------------------------------------------------- Grundriss --
def new_document(subject: str = SHORT, stand: str = STAND,
                 running_title: str = RUNNING_TITLE) -> docx.Document:
    doc = docx.Document()
    _purge_body(doc)
    _page_setup(doc)
    _settings(doc)
    _base_styles(doc)
    _numbering_defs(doc)
    _header(doc, running_title, subject, stand)
    _footer(doc, subject)
    return doc


def _purge_body(doc):
    body = doc.element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def _page_setup(doc):
    section = doc.sections[0]
    section.page_width, section.page_height = Emu(PAGE_W * 635), Emu(PAGE_H * 635)
    section.left_margin = section.right_margin = Emu(MARGIN_X * 635)
    section.top_margin, section.bottom_margin = Emu(MARGIN_TOP * 635), Emu(MARGIN_BOT * 635)
    section.header_distance, section.footer_distance = Emu(624 * 635), Emu(624 * 635)
    section.different_first_page_header_footer = True  # Deckblatt bleibt frei


def _settings(doc):
    """Silbentrennung an, Felder beim Öffnen aktualisieren."""
    s = doc.settings.element
    for tag, attrs in (
        ("w:autoHyphenation", {"w:val": "true"}),
        ("w:doNotHyphenateCaps", {"w:val": "true"}),
        ("w:hyphenationZone", {"w:val": "284"}),
        ("w:consecutiveHyphenLimit", {"w:val": "2"}),
        ("w:updateFields", {"w:val": "true"}),
        ("w:evenAndOddHeaders", {"w:val": "false"}),
    ):
        node = s.find(qn(tag))
        if node is None:
            node = doc.settings.element.makeelement(qn(tag), {})
            s.append(node)
        for key, value in attrs.items():
            node.set(qn(key), value)


def _base_styles(doc):
    """Normal-Stil als Basis; alles Weitere wird direkt am Absatz gesetzt."""
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(SZ_BODY / 2)
    rpr = normal.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attr), FONT)
    lang = rpr.makeelement(qn("w:lang"), {qn("w:val"): LANG})
    rpr.append(lang)
    ppr = normal.element.get_or_add_pPr()
    ppr.append(ppr.makeelement(qn("w:spacing"), {
        qn("w:after"): str(SP_BODY_AFTER), qn("w:line"): str(LINE_BODY),
        qn("w:lineRule"): "auto"}))

    # Gliederungsebenen, damit Word ein eigenes Verzeichnis erzeugen kann.
    for name, size, color, outline in (
        ("Heading 1", SZ_H1, INK, 0), ("Heading 2", SZ_H2, INK, 1),
        ("Heading 3", SZ_H3, "3A4048", 2),
    ):
        style = doc.styles[name]
        style.font.name = FONT
        style.font.size = Pt(size / 2)
        style.font.bold = True
        style.font.color.rgb = docx.shared.RGBColor.from_string(color)
        ppr = style.element.get_or_add_pPr()
        for tag in ("w:outlineLvl", "w:numPr"):
            old = ppr.find(qn(tag))
            if old is not None:
                ppr.remove(old)
        ppr.append(ppr.makeelement(qn("w:outlineLvl"), {qn("w:val"): str(outline)}))

    # Die mitgelieferten Kopf-/Fusszeilenstile bringen eigene Tabulatoren mit
    # (Mitte 4513, rechts 9026). Sie würden den rechten Anschlag verschieben,
    # deshalb werden sie durch genau einen Anschlag am Satzspiegelrand ersetzt.
    for name in ("Header", "Footer"):
        ppr = doc.styles[name].element.get_or_add_pPr()
        old = ppr.find(qn("w:tabs"))
        if old is not None:
            ppr.remove(old)
        node = el("tabs")
        node.append(el("tab", val="right", pos=CONTENT_W))
        ppr.append(node)


def _numbering_defs(doc):
    """Eigene Aufzählungs- und Nummerierungsdefinition anlegen."""
    numbering = doc.part.numbering_part.element
    for old in list(numbering):
        numbering.remove(old)

    def add_abstract(aid: int, fmt: str, text: str, font: str | None):
        node = el("abstractNum", abstractNumId=aid)
        node.append(el("multiLevelType", val="hybridMultilevel"))
        for lvl in range(3):
            level = el("lvl", ilvl=lvl)
            level.append(el("start", val=1))
            level.append(el("numFmt", val=fmt))
            level.append(el("lvlText", val=text if fmt == "bullet" else f"%{lvl + 1}."))
            level.append(el("lvlJc", val="left"))
            ppr = el("pPr")
            ind = el("ind", left=340 + lvl * 340, hanging=300)
            ppr.append(ind)
            level.append(ppr)
            if font:
                rpr = el("rPr")
                rpr.append(el("rFonts", ascii=font, hAnsi=font, hint="default"))
                level.append(rpr)
            node.append(level)
        numbering.append(node)

    add_abstract(10, "bullet", "▪", "Arial")
    add_abstract(11, "decimal", "", None)
    node = el("num", numId=BULLET_NUM)
    node.append(el("abstractNumId", val=10))
    numbering.append(node)
    # Jede nummerierte Liste bekommt eine eigene Instanz derselben Definition.
    # Ohne das zählt Word über das ganze Dokument durch und die zweite Liste
    # beginnt dort, wo die erste aufgehört hat.
    for num_id in ORDERED_NUMS:
        node = el("num", numId=num_id)
        node.append(el("abstractNumId", val=11))
        # Eigene Instanz allein genügt nicht: ohne startOverride zählt die
        # Definition über alle Instanzen hinweg weiter.
        for lvl in range(3):
            override = el("lvlOverride", ilvl=lvl)
            override.append(el("startOverride", val=1))
            node.append(override)
        numbering.append(node)


def _properties(doc, *, title: str, subject: str, keywords: str, description: str):
    """Dokumenteigenschaften setzen.

    Word zeigt sie in den Infos, der PDF-Export übernimmt sie als Metadaten.
    Ohne diesen Schritt trägt jede erzeugte Datei „python-docx“ als Verfasser
    — auf einem Bericht, der an einen Auftraggeber geht, ein Fehler.
    """
    core = doc.core_properties
    core.title = title
    core.subject = subject
    core.author = AUTHOR
    core.last_modified_by = AUTHOR
    core.category = "Messbericht"
    core.comments = description
    core.keywords = keywords
    core.revision = 1
    core.created = core.modified = REPORT_DATE

    # Firma und Anwendung stehen in den erweiterten Eigenschaften, die
    # python-docx nicht anfasst — dort also direkt am XML.
    from lxml import etree

    for part in doc.part.package.iter_parts():
        if part.partname != "/docProps/app.xml":
            continue
        root = etree.fromstring(part.blob)
        ns = root.nsmap.get(None, "")
        for tag, value in (("Company", COMPANY),
                           ("Application", "kabuu Berichtssatz"),
                           ("Manager", AUTHOR)):
            node = root.find(f"{{{ns}}}{tag}")
            if node is None:
                node = etree.SubElement(root, f"{{{ns}}}{tag}")
            node.text = value
        part._blob = etree.tostring(
            root, xml_declaration=True, encoding="UTF-8", standalone=True
        )
    return doc


def _finish(doc):
    """Letzter Schliff vor dem Speichern: Elementfolge im ganzen Paket richten."""
    section = doc.sections[0]
    normalize(
        doc.element.body,
        doc.styles.element,
        doc.settings.element,
        *(part._element for part in (
            section.header, section.footer,
            section.first_page_header, section.first_page_footer)),
    )
    # python-docx liefert <w:zoom/> ohne das laut Schema nötige Attribut mit.
    zoom = doc.settings.element.find(qn("w:zoom"))
    if zoom is not None and zoom.get(qn("w:percent")) is None:
        zoom.set(qn("w:percent"), "100")
    return doc


def _logo_run(p, name: str, height_cm: float):
    r = p.add_run()
    path = LOGO / name
    with Image.open(path) as im:
        ratio = im.width / im.height
    r.add_picture(str(path), height=Cm(height_cm), width=Cm(height_cm * ratio))
    return r


def _header(doc, running_title: str, subject: str, stand: str):
    section = doc.sections[0]
    section.first_page_header.paragraphs[0].text = ""  # Deckblatt ohne Kopfzeile
    header = section.header
    for p in list(header.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    p = header.paragraphs[0]
    p.text = ""
    pr = p._p.get_or_add_pPr()
    for tag in ("w:spacing", "w:tabs", "w:pBdr"):
        old = pr.find(qn(tag))
        if old is not None:
            pr.remove(old)
    pr.append(pr.makeelement(qn("w:spacing"), {
        qn("w:after"): "80", qn("w:before"): "0", qn("w:line"): "240",
        qn("w:lineRule"): "auto"}))
    borders(p, bottom=(HAIR, 6, 6))
    _logo_run(p, "logo_mark.png", 0.62)
    run(p, f"   {running_title}", size=16, color=INK, bold=True)
    run(p, f"\t{subject}{NBSP}· Stand {stand}", size=16, color=STEEL)


def _footer(doc, subject: str):
    section = doc.sections[0]
    for target in (section.footer, section.first_page_footer):
        for p in list(target.paragraphs)[1:]:
            p._p.getparent().remove(p._p)
        p = target.paragraphs[0]
        p.text = ""
        pr = p._p.get_or_add_pPr()
        for tag in ("w:spacing", "w:tabs", "w:pBdr"):
            old = pr.find(qn(tag))
            if old is not None:
                pr.remove(old)
        pr.append(pr.makeelement(qn("w:spacing"), {
            qn("w:before"): "80", qn("w:after"): "0", qn("w:line"): "240",
            qn("w:lineRule"): "auto"}))
        borders(p, top=(HAIR, 6, 6))
        if target is section.first_page_footer:
            run(p, CONTACT, size=16, color=STEEL)
            run(p, f"\t{subject}", size=16, color=STEEL)
            continue
        run(p, CONTACT, size=16, color=STEEL)
        run(p, "\tSeite ", size=16, color=STEEL)
        field(p, " PAGE ", "", size=16, color=INK, bold=True)
        run(p, " von ", size=16, color=STEEL)
        field(p, " NUMPAGES ", "", size=16, color=STEEL)


# ------------------------------------------------------------------ Bausteine --
def rule(doc, *, color=RULE, size=6, before=0, after=0):
    p = para(doc, space_before=before, space_after=after, line=120, keep_next=True)
    borders(p, bottom=(color, size, 2))
    return p


def spacer(doc, points: int):
    return para(doc, space_before=0, space_after=0, line=points * 20, keep_next=True)


LEAD_IN_FOLLOWERS = {"table", "figure", "formula", "callout"}


def body_text(doc, text: str, *, leads_into: str | None = None, **kw):
    """Fliesstext. Eine Zeile, die auf einen Doppelpunkt endet und einen
    Block ankündigt, wird an diesen gebunden — sie darf nicht allein am
    Seitenfuss zurückbleiben."""
    lead_in = text.rstrip().endswith(":") and leads_into in LEAD_IN_FOLLOWERS
    p = para(doc, align=ALIGN["justify"], space_after=SP_BODY_AFTER,
             keep_next=lead_in, **kw)
    run(p, typo(text))
    return p


def heading(doc, level: int, text: str, anchor: str | None = None, bid: int = 0,
            new_page: bool = False):
    """Kapitel beginnen auf neuer Seite und tragen eine gesetzte Ordnungszeile."""
    if level == 1:
        kicker = _chapter_kicker(text)
        if kicker:
            k = para(doc, space_before=0, space_after=60, line=240, keep_next=True,
                     page_break=new_page, hyphenate=False)
            run(k, kicker, size=17, color=STEEL_LT, bold=True, spacing=34, caps=True)
        p = para(doc, space_before=0, space_after=220, line=264, keep_next=True,
                 page_break=new_page and not kicker, style="Heading 1",
                 hyphenate=False)
        run(p, typo(text), size=SZ_H1, color=INK, bold=True)
        borders(p, bottom=(INK, 10, 8))
    elif level == 2:
        p = para(doc, space_before=320, space_after=110, line=252, keep_next=True,
                 style="Heading 2", hyphenate=False)
        run(p, typo(text), size=SZ_H2, color=INK, bold=True)
    else:
        p = para(doc, space_before=240, space_after=80, line=252, keep_next=True,
                 style="Heading 3", hyphenate=False)
        run(p, typo(text), size=SZ_H3, color="3A4048", bold=True)
    if anchor:
        bookmark(p, anchor, bid)
    return p


def _chapter_kicker(text: str) -> str:
    m = re.match(r"^(\d+)\.", text)
    if m:
        return f"Kapitel {m.group(1)}"
    m = re.match(r"^Anhang\s+([A-Z])", text)
    if m:
        return f"Anhang {m.group(1)}"
    return ""


def list_item(doc, text: str, *, num_id: int, level: int = 0, last: bool = False):
    p = para(doc, space_before=0, space_after=60 if not last else 140, line=LINE_BODY,
             align=ALIGN["justify"], contextual=True)
    pr = p._p.get_or_add_pPr()
    num = el("numPr")
    num.append(el("ilvl", val=level))
    num.append(el("numId", val=num_id))
    pr.insert(0, num)
    run(p, typo(text))
    return p


def formula(doc, text: str):
    """Rechenweg als abgesetzter Block, Zeichenbreite erhalten."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = para(doc, space_before=140 if i == 0 else 0,
                 space_after=140 if i == len(lines) - 1 else 0,
                 line=252, indent_left=170, keep_next=i < len(lines) - 1)
        shade(p, PANEL)
        borders(p, left=(STEEL_LT, 18, 8))
        run(p, typo(line, insert=False) or " ", font=MONO, size=SZ_MONO,
            color="2A3038")
    return None


def callout(doc, variant: str, title: str, body: list[str]):
    accent = ACCENT.get(variant, ACCENT["info"])
    table = doc.add_table(rows=1, cols=1)
    table_frame(table, [CONTENT_W])
    row_rules(table.rows[0], cant_split=False)
    cell = clear_cell(table.rows[0].cells[0])
    cell_style(cell, width=CONTENT_W, fill=accent["tint"],
               left=(accent["line"], 24), top=(accent["line"], 2),
               bottom=(accent["line"], 2), right=(accent["line"], 2))
    cell_margins(cell, top=150, bottom=150, left=200, right=180)

    if title:
        p = para(cell, space_before=0, space_after=90 if body else 0, line=252,
                 keep_next=bool(body))
        run(p, typo(title), size=SZ_BODY, color=accent["line"], bold=True)
    for i, text in enumerate(body):
        p = para(cell, space_before=0, space_after=0 if i == len(body) - 1 else 90,
                 line=LINE_BODY, align=ALIGN["justify"])
        run(p, typo(text), size=SZ_SMALL)
    _after_block(doc)
    return table


def _after_block(doc, points: int = 7):
    """Luft nach einem Tabellenblock — Word setzt Tabellen sonst bündig."""
    return para(doc, space_before=0, space_after=0, line=points * 20)


# -------------------------------------------------------------------- Tabellen --
def _column_widths(rows: list[list[str]], numeric: list[bool], centered: list[bool]) -> list[int]:
    """Spaltenbreiten nach Inhaltslänge, mit Untergrenzen je Spaltenart."""
    ncols = len(rows[0])
    weights = []
    for c in range(ncols):
        longest = max((len(r[c]) for r in rows), default=1)
        typical = sorted(len(r[c]) for r in rows)[len(rows) // 2]
        weight = min(max(0.65 * longest + 0.35 * typical, 6), 62)
        if numeric[c] or centered[c]:
            weight = min(weight, 13)
        weights.append(weight)

    # Erst die Untergrenzen sichern, dann den Rest nach Inhaltsmenge verteilen.
    # In dieser Reihenfolge kann keine Spalte unter die Breite ihres längsten
    # Worts fallen — nur so bleibt jedes Wort unzertrennt.
    floors = [
        max(MIN_COL_NUM if numeric[c] or centered[c] else MIN_COL_TEXT,
            _word_floor(rows, c))
        for c in range(ncols)
    ]
    if sum(floors) >= CONTENT_W:
        scale = CONTENT_W / sum(floors)
        widths = [int(f * scale) for f in floors]
    else:
        extra = CONTENT_W - sum(floors)
        total = sum(weights)
        widths = [floors[c] + int(extra * weights[c] / total) for c in range(ncols)]
    widths[-1] += CONTENT_W - sum(widths)
    return widths


def _word_floor(rows: list[list[str]], col: int) -> int:
    """Breite des längsten unteilbaren Worts der Spalte, plus Zellenrand.

    Ohne diese Untergrenze bricht Word ein Wort wie „Rang“ in einer schmalen
    Spalte mitten durch — der auffälligste Satzfehler überhaupt.
    """
    longest = 0
    for row in rows:
        for word in re.split(r"[\s\u00a0]+", row[col]):
            longest = max(longest, len(word))
    return min(int(longest * 118) + 260, 3400)


def _classify(rows: list[list[str]], has_header: bool):
    body = rows[1:] if has_header else rows
    ncols = len(rows[0])
    numeric, centered = [], []
    for c in range(ncols):
        values = [r[c].strip() for r in body if r[c].strip()]
        if not values:
            numeric.append(False)
            centered.append(False)
            continue
        centered.append(all(v in SYMBOLS for v in values))
        # Eine Spalte ist nur dann eine Zahlenspalte, wenn ihre Werte auch
        # kurz sind. Ein ganzer Satz, der zufällig mit einer Ziffer beginnt
        # ("94,0 bis 104,0 %, 100 % einer Woche"), gehört linksbündig.
        compact_enough = max(len(v) for v in values) <= NUMERIC_MAX_CHARS
        numeric.append(
            not centered[-1]
            and compact_enough
            and sum(looks_numeric(v) for v in values) >= 0.7 * len(values)
        )
    return numeric, centered


def render_table(doc, grid: list[list[dict]], *, force_header: bool | None = None):
    ncols = max(len(row) for row in grid)
    rows = [[c["text"] for c in row] + [""] * (ncols - len(row)) for row in grid]
    if force_header is None:
        has_header = (
            len(rows) > 1
            and all(len(c) <= HEADER_MAX_CHARS and "\n" not in c for c in rows[0])
            and any(c.strip() for c in rows[0])
        )
    else:
        has_header = force_header

    numeric, centered = _classify(rows, has_header)
    widths = _column_widths(rows, numeric, centered)
    compact = all(len(c) <= 55 for row in rows for c in row)

    table = doc.add_table(rows=len(rows), cols=ncols)
    table_frame(table, widths)

    for r, values in enumerate(rows):
        is_head = has_header and r == 0
        row_rules(table.rows[r], header=is_head, cant_split=True)
        body_index = r - (1 if has_header else 0)
        fill = INK if is_head else (BAND if body_index % 2 == 1 else None)
        bind = _binds_to_next(r, len(rows), has_header)
        if not any(v.strip() for v in values):
            # Leerzeile eines Erhebungsblatts: sie soll von Hand ausgefüllt
            # werden und braucht dafür Schreibhöhe statt einer Textzeile.
            trPr = table.rows[r]._tr.get_or_add_trPr()
            trPr.append(el("trHeight", val=FORM_ROW_HEIGHT, hRule="atLeast"))
        for c, text in enumerate(values):
            cell = clear_cell(table.rows[r].cells[c])
            cell_style(
                cell, width=widths[c], fill=fill,
                top=(HAIR, 4) if not is_head and r else None,
                bottom=(RULE, 6) if r == len(rows) - 1 else None,
                valign="center" if compact else "top",
            )
            cell_margins(cell, top=95 if is_head else 85, bottom=95 if is_head else 85,
                         left=115, right=115)
            _fill_cell(cell, text, is_head=is_head, numeric=numeric[c],
                       centered=centered[c], label=(c == 0 and not has_header),
                       keep_next=bind)
    _after_block(doc)
    return table


def _binds_to_next(row: int, total: int, has_header: bool) -> bool:
    """Welche Tabellenzeile darf nicht von der folgenden getrennt werden.

    Drei Fälle, die im Satz sonst regelmässig unschön auffallen: eine
    Kopfzeile allein am Seitenfuss, eine einzelne Datenzeile allein auf der
    Folgeseite, und eine kurze Tabelle, die überhaupt umbricht.
    """
    if row == total - 1:
        return False  # letzte Zeile bindet nichts, sonst klebt die Tabelle am Text
    if total <= ATOMIC_ROWS:
        return True
    if has_header and row == 0:
        return True
    return row >= total - 3


def _fill_cell(cell, text: str, *, is_head: bool, numeric: bool, centered: bool,
               label: bool, keep_next: bool = False):
    lines = text.split("\n") if text else [""]
    # Kopfzeile folgt der Ausrichtung ihrer Spalte, sonst stehen Titel und
    # Werte nicht übereinander.
    align = "center" if centered else ("right" if numeric else "left")
    for i, line in enumerate(lines):
        p = para(cell, space_before=0, space_after=0 if i == len(lines) - 1 else 70,
                 line=LINE_TIGHT, align=ALIGN[align], keep_lines=False,
                 hyphenate=False, keep_next=keep_next)
        if not line:
            continue
        run(p, typo(line),
            size=SZ_TABLE_HEAD if is_head else SZ_TABLE,
            color="FFFFFF" if is_head else BODY,
            bold=is_head or label)


# ----------------------------------------------------------- Bilder und Legenden --
def figure(doc, name: str, *, max_w_cm=16.6, max_h_cm=15.6, keep_next=True):
    path = MEDIA / name
    with Image.open(path) as im:
        w_px, h_px = im.size
    width = max_w_cm
    height = width * h_px / w_px
    if height > max_h_cm:
        height = max_h_cm
        width = height * w_px / h_px
    p = para(doc, space_before=120, space_after=80, line=240,
             align=ALIGN["center"], keep_next=keep_next)
    p.add_run().add_picture(str(path), width=Cm(width), height=Cm(height))
    return p


CAPTION_RE = re.compile(r"^Abbildung\s+(\d+):\s*(.*)$", re.S)


def caption(doc, text: str, number: int | None = None):
    """Bildlegende. ``number`` setzt die Nummer in Lesereihenfolge neu.

    Im Ausgangsbericht stehen die Abbildungen als 1, 4, 5, 2, 3 im Text —
    die Anhänge wurden nachträglich eingefügt. Da keine Stelle im Text auf
    eine Abbildungsnummer verweist, werden sie beim Satz durchgezählt.
    """
    p = para(doc, space_before=0, space_after=200, line=252, align=ALIGN["center"],
             indent_left=300, indent_right=300, hyphenate=False)
    m = CAPTION_RE.match(text)
    if m:
        label = f"Abbildung {number if number else m.group(1)}:"
        run(p, typo(label) + " ", size=SZ_CAPTION, color=INK, bold=True)
        run(p, typo(m.group(2)), size=SZ_CAPTION, color=STEEL)
    else:
        run(p, typo(text), size=SZ_CAPTION, color=STEEL)
    return p


def photo_block(doc, title: str, image: str, info: list[list[dict]]):
    """Bilddokumentation: Titelzeile, Aufnahme, darunter die Zuordnung."""
    p = para(doc, space_before=260, space_after=80, line=252, keep_next=True)
    run(p, typo(title), size=SZ_BODY, color=INK, bold=True)
    figure(doc, image, max_w_cm=12.4, max_h_cm=9.4)
    # Beschriftung und Wert stehen in zwei Spalten. Ohne Tabulator beginnen
    # die Werte je nach Länge der Beschriftung an verschiedenen Stellen.
    box = para(doc, space_before=0, space_after=200, line=LINE_TIGHT,
               indent_left=560, indent_right=560, hanging=PHOTO_LABEL_W,
               align=ALIGN["left"], hyphenate=False)
    borders(box, top=(HAIR, 4, 6))
    tabs(box, [(560 + PHOTO_LABEL_W, "left", "none")])
    for i, row in enumerate(info):
        if i:
            box.add_run().add_break()
        label = row[0]["text"] if row else ""
        value = row[1]["text"] if len(row) > 1 else ""
        run(box, typo(label), size=SZ_CAPTION, color=INK, bold=True)
        run(box, "\t" + typo(value), size=SZ_CAPTION, color=STEEL)
    return box


# ------------------------------------------------------------------- Deckblatt --
def cover(doc, meta_rows, note, *, title=TITLE, object_line=OBJECT, campaign=CAMPAIGN):
    p = para(doc, space_before=0, space_after=440, line=240, keep_next=True)
    _logo_run(p, "logo_lockup.png", 4.4)

    rule(doc, color=INK, size=14, after=0)
    p = para(doc, space_before=180, space_after=60, line=240, keep_next=True)
    run(p, "Schlussbericht", size=19, color=STEEL, bold=True, spacing=54, caps=True)

    p = para(doc, space_before=0, space_after=90, line=276, keep_next=True)
    run(p, typo(title), size=44, color=INK, bold=True)
    p = para(doc, space_before=0, space_after=140, line=264, keep_next=True)
    run(p, typo(object_line), size=25, color="3A4048")
    rule(doc, color=HAIR, size=6, after=0)
    p = para(doc, space_before=110, space_after=420, line=252, keep_next=True)
    run(p, typo(campaign), size=SZ_SMALL, color=STEEL)

    render_table(doc, meta_rows, force_header=False)
    spacer(doc, 6)
    callout(doc, note["variant"], note["title"], note["body"])

    p = para(doc, space_before=0, space_after=0, line=240, page_break=True)
    return p


# --------------------------------------------------------- Inhaltsverzeichnis --
def table_of_contents(doc, entries, pages: dict[str, str]):
    """Echtes Word-Verzeichnis mit hinterlegten Seitenzahlen und Punktführung."""
    p = para(doc, space_before=0, space_after=240, line=252)
    run(p, "Verzeichnis der Kapitel und Abschnitte. In Word mit F9 aktualisierbar.",
        size=SZ_SMALL, color=STEEL)

    last = len(entries) - 1
    for i, (level, text, anchor) in enumerate(entries):
        entry = para(
            doc,
            space_before=90 if level == 1 and i else 0,
            space_after=0,
            line=252,
            indent_left=0 if level == 1 else 400,
            indent_right=560,
            keep_lines=False,
            hyphenate=False,
        )
        tabs(entry, [(CONTENT_W - 560, "right", "dot")])
        run(entry, typo(text), size=SZ_BODY if level == 1 else SZ_SMALL,
            color=INK if level == 1 else "3A4048", bold=level == 1)
        run(entry, "\t", size=SZ_SMALL, color=STEEL)
        field(entry, f" PAGEREF {anchor} \\h ", pages.get(anchor, ""),
              size=SZ_BODY if level == 1 else SZ_SMALL,
              color=INK if level == 1 else STEEL, bold=level == 1)
        hyperlink_to(entry, anchor)
        if i == 0:
            _wrap_field_begin(entry, ' TOC \\o "1-2" \\h \\z \\u ')
        if i == last:
            _wrap_field_end(entry)


def _wrap_field_begin(p, instruction: str):
    begin = el("r")
    begin.append(el("fldChar", fldCharType="begin"))
    instr_run = el("r")
    node = el("instrText")
    node.set(qn("xml:space"), "preserve")
    node.text = instruction
    instr_run.append(node)
    sep = el("r")
    sep.append(el("fldChar", fldCharType="separate"))
    for i, node in enumerate((begin, instr_run, sep)):
        p._p.insert(i + 1, node)


def _wrap_field_end(p):
    end = el("r")
    end.append(el("fldChar", fldCharType="end"))
    p._p.append(end)


# ----------------------------------------------------------------- Schlussseite --
def closing(doc, lines: list[str]):
    para(doc, space_before=0, space_after=0, line=240, page_break=True, keep_next=True)
    spacer(doc, 150)
    p = para(doc, space_before=0, space_after=280, line=240, align=ALIGN["center"],
             keep_next=True)
    _logo_run(p, "logo_lockup.png", 3.9)
    rule(doc, color=HAIR, size=6, after=0)
    p = para(doc, space_before=160, space_after=260, line=264, align=ALIGN["center"],
             keep_next=True)
    run(p, typo(lines[0]), size=SZ_SMALL, color=STEEL)
    p = para(doc, space_before=0, space_after=40, line=252, align=ALIGN["center"],
             keep_next=True)
    run(p, typo(lines[1]), size=SZ_H3, color=INK, bold=True)
    for text in lines[2:]:
        p = para(doc, space_before=0, space_after=40, line=252, align=ALIGN["center"])
        run(p, typo(text), size=SZ_SMALL, color="3A4048")


# ---------------------------------------------------------------------- Aufbau --
def build(blocks, pages: dict[str, str]):
    doc = new_document()

    meta_rows = blocks[4]["rows"]
    cover(doc, meta_rows, blocks[5])

    anchors, entries = {}, []
    bid = 1000
    for block in blocks[6:-4]:
        if block["type"] == "heading" and block["level"] <= 2:
            bid += 1
            anchor = f"_Toc9{bid}"
            anchors[id(block)] = (anchor, bid)
            if block["text"] != "Inhaltsverzeichnis":
                entries.append((block["level"], block["text"], anchor))

    body = blocks[6:-4]
    figure_numbers = {
        id(b): n
        for n, b in enumerate(
            (b for b in body if b["type"] == "caption" and CAPTION_RE.match(b["text"])),
            start=1,
        )
    }
    i, ordered_seq, in_list = 0, -1, False
    while i < len(body):
        block = body[i]
        kind = block["type"]
        if kind != "listitem":
            in_list = False

        if kind == "heading":
            anchor, node_id = anchors.get(id(block), (None, 0))
            heading(doc, block["level"], block["text"], anchor, node_id,
                    new_page=block["level"] == 1 and block["text"] != "Inhaltsverzeichnis")
            if block["text"] == "Inhaltsverzeichnis":
                table_of_contents(doc, entries, pages)
                i += 2  # der Hinweis auf F9 steht jetzt im Verzeichnis selbst
                continue
            i += 1
            continue

        if kind == "photo_title" and i + 2 < len(body) and body[i + 1]["type"] == "figure" \
                and body[i + 2]["type"] == "table":
            photo_block(doc, block["text"], body[i + 1]["image"], body[i + 2]["rows"])
            i += 3
            continue

        if kind == "figure":
            has_caption = i + 1 < len(body) and body[i + 1]["type"] == "caption"
            figure(doc, block["image"], keep_next=has_caption)
            if has_caption:
                nxt = body[i + 1]
                caption(doc, nxt["text"], figure_numbers.get(id(nxt)))
                i += 2
                continue
            i += 1
            continue

        if kind == "caption":
            caption(doc, block["text"], figure_numbers.get(id(block)))
        elif kind == "paragraph":
            following = body[i + 1]["type"] if i + 1 < len(body) else None
            body_text(doc, block["text"], leads_into=following)
        elif kind == "listitem":
            nxt = body[i + 1] if i + 1 < len(body) else None
            if not in_list and block["ordered"]:
                ordered_seq += 1
            in_list = True
            list_item(doc, block["text"], level=block["level"],
                      num_id=ORDERED_NUMS[ordered_seq] if block["ordered"] else BULLET_NUM,
                      last=not (nxt and nxt["type"] == "listitem"))
        elif kind == "formula":
            formula(doc, block["text"])
        elif kind == "callout":
            callout(doc, block["variant"], block["title"], block["body"])
        elif kind == "table":
            render_table(doc, block["rows"])
        i += 1

    closing(doc, [b["text"] for b in blocks[-4:]])
    _properties(
        doc,
        title=f"Schlussbericht {TITLE} — {SHORT}",
        subject=CAMPAIGN,
        keywords="Netzqualität, EN 50160, Flicker, Rundsteuerung, "
                 "IEC 61000-4-30, Photovoltaik, Zuzwil",
        description="Netzqualitätsmessung an drei Messpunkten mit Ursachenanalyse "
                    "des Lichtflackerns und Massnahmenkatalog.",
    )
    _finish(doc)
    return doc, entries


TEMPLATE_NOTE = {
    "variant": "info",
    "title": "So arbeiten Sie mit dieser Vorlage",
    "body": [
        "Die Vorlage trägt die vollständige kabuu-Gestaltung: Deckblatt, Kopf- und "
        "Fusszeile mit Bildmarke, Überschriftenebenen, Tabellenlook, Hinweiskästen "
        "und Bildlegenden. Ersetzen Sie die Platzhalter und schreiben Sie den "
        "Bericht in den vorbereiteten Ebenen weiter.",
        "Überschrift 1 beginnt ein Kapitel auf neuer Seite, Überschrift 2 und 3 "
        "gliedern darunter. Das Inhaltsverzeichnis aktualisieren Sie mit F9.",
        "Zahlen werden nach Schweizer Satz gesetzt: Tausender mit Hochkomma, "
        "zwischen Zahl und Einheit ein geschütztes Leerzeichen.",
    ],
}


def build_template():
    """Leere Vorlage mit derselben Gestaltung, aber ohne Berichtsinhalt."""
    doc = new_document(subject="Objekt, Ort", stand="TT.MM.JJJJ",
                       running_title="Berichtstitel")

    meta = [
        [{"text": "Objekt", "span": 1}, {"text": "Objektname, Strasse, PLZ Ort", "span": 1}],
        [{"text": "Betreiber", "span": 1}, {"text": "Name des Betreibers", "span": 1}],
        [{"text": "Auftraggeber", "span": 1}, {"text": "Firma, Adresse", "span": 1}],
        [{"text": "Netzbetreiber", "span": 1}, {"text": "Werk · 230/400 V · 50 Hz", "span": 1}],
        [{"text": "Anlass", "span": 1}, {"text": "Beschwerdebild in einem Satz", "span": 1}],
        [{"text": "Messmittel", "span": 1}, {"text": "Gerätetyp, Anzahl, Norm", "span": 1}],
        [{"text": "Messzeitraum", "span": 1}, {"text": "TT.MM.JJJJ bis TT.MM.JJJJ", "span": 1}],
        [{"text": "Verfasser", "span": 1},
         {"text": "Burak Ücöz, kabuu — Netzqualität & EMV Messungen", "span": 1}],
        [{"text": "Berichtsstand", "span": 1}, {"text": "TT.MM.JJJJ", "span": 1}],
    ]
    cover(doc, meta, TEMPLATE_NOTE,
          title="Titel der Messung und der Fragestellung",
          object_line="Objektname, Strasse, PLZ Ort",
          campaign="Messkampagne TT.MM.JJJJ bis TT.MM.JJJJ · n Messpunkte · "
                   "IEC 61000-4-30 Ed.3 Class A")

    heading(doc, 1, "Inhaltsverzeichnis", "_TocTpl0", 900)
    p = para(doc, space_before=0, space_after=240, line=252)
    run(p, "Hier das Inhaltsverzeichnis einfügen: Referenzen · Inhaltsverzeichnis · "
           "Ebenen 1 bis 2. Mit F9 aktualisieren.", size=SZ_SMALL, color=STEEL)

    heading(doc, 1, "1. Kapitelüberschrift", "_TocTpl1", 901, new_page=True)
    body_text(doc, "Fliesstext im Blocksatz mit Silbentrennung. Zahlen und Einheiten "
                   "bleiben zusammen, etwa 230 V, 50 Hz oder 2,40 %. Tausender werden "
                   "mit Hochkomma gesetzt, etwa 86'600 VA.")
    heading(doc, 2, "1.1 Abschnittsüberschrift")
    body_text(doc, "Unter einer Abschnittsüberschrift steht der erläuternde Text, "
                   "darunter die Tabelle mit den Werten.")
    render_table(doc, [
        [{"text": "Grösse", "span": 1}, {"text": "Minimum", "span": 1},
         {"text": "Mittel", "span": 1}, {"text": "Maximum", "span": 1},
         {"text": "Grenzwert", "span": 1}],
        [{"text": "U1N", "span": 1}, {"text": "226,45 V", "span": 1},
         {"text": "234,73 V", "span": 1}, {"text": "239,46 V", "span": 1},
         {"text": "207 bis 253 V", "span": 1}],
        [{"text": "THD U1", "span": 1}, {"text": "1,11 %", "span": 1},
         {"text": "1,72 %", "span": 1}, {"text": "2,40 %", "span": 1},
         {"text": "8,0 %", "span": 1}],
    ])
    for variant, title in (
        ("success", "Bestätigtes Ergebnis"),
        ("warning", "Vorbehalt oder Einschränkung"),
        ("danger", "Interner Hinweis, vor Weitergabe entfernen"),
        ("info", "Einordnung und Hintergrund"),
    ):
        callout(doc, variant, title,
                ["Kurzer Absatz, der die Aussage trägt. Die Farbe steht für die Rolle "
                 "des Kastens, nicht für Gestaltung."])
    heading(doc, 3, "1.1.1 Unterabschnitt")
    body_text(doc, "Die dritte Ebene gliedert innerhalb eines Abschnitts, etwa je "
                   "Massnahme oder je Messpunkt.")
    list_item(doc, "Aufzählung für gleichrangige Punkte.", num_id=BULLET_NUM)
    list_item(doc, "Zweiter Punkt derselben Aufzählung.", num_id=BULLET_NUM, last=True)
    list_item(doc, "Nummerierte Liste für Abläufe in fester Reihenfolge.",
              num_id=ORDERED_NUMS[0])
    list_item(doc, "Zweiter Schritt.", num_id=ORDERED_NUMS[0], last=True)
    formula(doc, "S = U_LL * I * Wurzel(3)\nS = 400 V * 125 A * 1,732 = 86'600 VA")

    closing(doc, [
        "Ende des Berichts. Erstellt am TT.MM.JJJJ durch Burak Ücöz, "
        "kabuu — Netzqualität & EMV Messungen.",
        "Burak Ücöz",
        "kabuu — Netzqualität & EMV Messungen · Im Abt 9 A · 8240 Thayngen",
        "+41 79 512 98 07 · engineering.kabuu@gmail.com",
    ])
    _properties(
        doc,
        title="kabuu — Vorlage Messbericht",
        subject="Wordvorlage für Berichte von kabuu Netzqualität & EMV Messungen",
        keywords="Vorlage, Messbericht, Netzqualität, kabuu",
        description="Leere Berichtsvorlage mit Deckblatt, Überschriftenebenen, "
                    "Tabellenlook, Hinweiskästen und Bildlegenden.",
    )
    _finish(doc)
    return doc


def _as_template(path: Path, out: Path):
    """Als .dotx auszeichnen — Word legt daraus neue Dokumente an."""
    import zipfile

    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    ct = parts["[Content_Types].xml"].decode("utf-8").replace(
        "wordprocessingml.document.main+xml",
        "wordprocessingml.template.main+xml",
    )
    parts["[Content_Types].xml"] = ct.encode("utf-8")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", action="store_true", help="zusätzlich .dotx schreiben")
    args = ap.parse_args()

    blocks = json.loads(CONTENT.read_text(encoding="utf-8"))["blocks"]
    pages = json.loads(TOC_PAGES.read_text(encoding="utf-8")) if TOC_PAGES.exists() else {}
    doc, entries = build(blocks, pages)
    doc.save(OUT_DOCX)
    print(f"{OUT_DOCX.relative_to(ROOT)}  ·  {len(entries)} Verzeichniseinträge"
          f"  ·  {'Seitenzahlen gesetzt' if pages else 'Seitenzahlen noch offen'}")

    if args.template:
        skeleton = ROOT / "build" / "vorlage.docx"
        skeleton.parent.mkdir(parents=True, exist_ok=True)
        build_template().save(skeleton)
        _as_template(skeleton, OUT_DOTX)
        print(f"{OUT_DOTX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
