"""Erzeugt MiT_CEO_Roadmap_2026_2028.pptx aus der Word-Vorlage."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from copy import deepcopy
from lxml import etree

# Farbpalette
NAVY = RGBColor(0x0B, 0x1F, 0x3A)
TEAL = RGBColor(0x00, 0x8C, 0x8C)
GOLD = RGBColor(0xC9, 0xA2, 0x27)
LIGHT = RGBColor(0xF4, 0xF6, 0xF8)
GREY = RGBColor(0x55, 0x5F, 0x6D)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xB3, 0x1B, 0x1B)
GREEN = RGBColor(0x1E, 0x7E, 0x34)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height

BLANK = prs.slide_layouts[6]


def add_rect(slide, x, y, w, h, fill, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
    shp.shadow.inherit = False
    return shp


def add_text(slide, x, y, w, h, text, size=14, bold=False, color=NAVY,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font="Calibri"):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
    return tb


def add_bullets(slide, x, y, w, h, items, size=14, color=NAVY, bullet_color=TEAL):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(6)
        r1 = p.add_run()
        r1.text = "▍  "
        r1.font.name = "Calibri"
        r1.font.size = Pt(size)
        r1.font.bold = True
        r1.font.color.rgb = bullet_color
        r2 = p.add_run()
        r2.text = item
        r2.font.name = "Calibri"
        r2.font.size = Pt(size)
        r2.font.color.rgb = color
    return tb


def page_chrome(slide, title, subtitle=None, page_num=None, total=None):
    # Top navy band
    add_rect(slide, 0, 0, SW, Inches(0.9), NAVY)
    add_rect(slide, 0, Inches(0.9), Inches(0.35), Inches(0.05), GOLD)
    # Title
    add_text(slide, Inches(0.5), Inches(0.15), SW - Inches(3), Inches(0.5),
             title, size=24, bold=True, color=WHITE)
    if subtitle:
        add_text(slide, Inches(0.5), Inches(0.55), SW - Inches(3), Inches(0.35),
                 subtitle, size=12, color=RGBColor(0xC9, 0xD2, 0xDE))
    # Brand top right
    add_text(slide, SW - Inches(3.0), Inches(0.25), Inches(2.7), Inches(0.4),
             "MiT × Aggreko  |  Datacenter CH", size=11,
             color=RGBColor(0xC9, 0xD2, 0xDE), align=PP_ALIGN.RIGHT)
    # Footer
    add_rect(slide, 0, SH - Inches(0.35), SW, Inches(0.35), LIGHT)
    add_text(slide, Inches(0.5), SH - Inches(0.33), Inches(8), Inches(0.3),
             "MiT CEO Roadmap 2026–2028  ·  Burak Ücöz  ·  27. Mai 2026",
             size=9, color=GREY, anchor=MSO_ANCHOR.MIDDLE)
    if page_num is not None:
        add_text(slide, SW - Inches(2.0), SH - Inches(0.33), Inches(1.5), Inches(0.3),
                 f"{page_num} / {total}", size=9, color=GREY,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def set_notes(slide, text):
    nf = slide.notes_slide.notes_text_frame
    nf.clear()
    lines = text.strip().split("\n")
    for i, line in enumerate(lines):
        p = nf.paragraphs[0] if i == 0 else nf.add_paragraph()
        r = p.add_run()
        r.text = line
        r.font.size = Pt(12)
        r.font.name = "Calibri"


def kpi_card(slide, x, y, w, h, value, label, accent=TEAL, big=44):
    add_rect(slide, x, y, w, h, WHITE, line=RGBColor(0xDD, 0xE2, 0xE8))
    add_rect(slide, x, y, w, Inches(0.08), accent)
    add_text(slide, x + Inches(0.2), y + Inches(0.35), w - Inches(0.4), Inches(0.9),
             value, size=big, bold=True, color=NAVY, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, x + Inches(0.2), y + h - Inches(0.7), w - Inches(0.4), Inches(0.6),
             label, size=12, color=GREY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)


def build_table(slide, x, y, w, h, headers, rows, header_fill=NAVY,
                header_color=WHITE, body_size=10, header_size=11,
                col_widths=None, row_height=None, zebra=True,
                first_col_bold=True, accent_col=None):
    cols = len(headers)
    n = len(rows) + 1
    tbl_shape = slide.shapes.add_table(n, cols, x, y, w, h)
    tbl = tbl_shape.table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = int(w * cw / total)
    # Header
    for j, head in enumerate(headers):
        c = tbl.cell(0, j)
        c.fill.solid()
        c.fill.fore_color.rgb = header_fill
        c.margin_left = Inches(0.08)
        c.margin_right = Inches(0.08)
        c.margin_top = Inches(0.04)
        c.margin_bottom = Inches(0.04)
        tf = c.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = head
        r.font.bold = True
        r.font.size = Pt(header_size)
        r.font.color.rgb = header_color
        r.font.name = "Calibri"
    # Body
    for i, row in enumerate(rows, start=1):
        for j, cell_text in enumerate(row):
            c = tbl.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = LIGHT if (zebra and i % 2 == 0) else WHITE
            c.margin_left = Inches(0.08)
            c.margin_right = Inches(0.08)
            c.margin_top = Inches(0.04)
            c.margin_bottom = Inches(0.04)
            tf = c.text_frame
            tf.clear()
            tf.word_wrap = True
            # support multi-line text via \n
            for k, line in enumerate(str(cell_text).split("\n")):
                p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                p.alignment = PP_ALIGN.LEFT
                r = p.add_run()
                r.text = line
                r.font.size = Pt(body_size)
                r.font.name = "Calibri"
                r.font.color.rgb = NAVY
                if j == 0 and first_col_bold:
                    r.font.bold = True
                if accent_col is not None and j == accent_col:
                    r.font.bold = True
                    r.font.color.rgb = TEAL
    if row_height:
        for i in range(n):
            tbl.rows[i].height = row_height
    return tbl


# ---------------------------------------------------------------------------
# SLIDE 1 — TITELFOLIE
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, NAVY)
# Decorative bands
add_rect(s, 0, Inches(5.4), SW, Inches(0.06), GOLD)
add_rect(s, 0, Inches(5.46), SW, Inches(0.02), TEAL)
# Eyebrow
add_text(s, Inches(0.8), Inches(0.9), Inches(8), Inches(0.4),
         "STRATEGISCHE ROADMAP  ·  2026 – 2028", size=14, bold=True,
         color=GOLD)
# Title
add_text(s, Inches(0.8), Inches(1.5), Inches(11.7), Inches(1.6),
         "Datacenter Schweiz", size=60, bold=True, color=WHITE)
add_text(s, Inches(0.8), Inches(2.7), Inches(11.7), Inches(1.2),
         "Marktlücke nutzen, bevor sie sich schliesst.", size=28,
         color=RGBColor(0xC9, 0xD2, 0xDE))
# Author block
add_rect(s, Inches(0.8), Inches(5.8), Inches(0.08), Inches(1.2), GOLD)
add_text(s, Inches(1.0), Inches(5.85), Inches(8), Inches(0.4),
         "Burak Ücöz", size=16, bold=True, color=WHITE)
add_text(s, Inches(1.0), Inches(6.2), Inches(8), Inches(0.4),
         "Strom-Vertrieb DC Schweiz  ·  Mobil in Time AG × Aggreko",
         size=12, color=RGBColor(0xC9, 0xD2, 0xDE))
add_text(s, Inches(1.0), Inches(6.55), Inches(8), Inches(0.4),
         "Vorlage für den CEO  ·  27. Mai 2026",
         size=12, color=RGBColor(0xC9, 0xD2, 0xDE))
# Right KPI strip
kpi_card(s, Inches(9.6), Inches(5.7), Inches(3.0), Inches(1.4),
         "CHF 4,96 Mio.", "verifizierte A++ Pipeline", accent=GOLD, big=22)

set_notes(s, """Begrüssung des CEO. Diese Roadmap fasst die strategische Marktposition von MiT × Aggreko im Schweizer Datacenter-Markt zusammen.
Kernbotschaft: Wir haben heute eine offene Marktlücke (Aggreko-Infrastruktur + IEC 61000-4-30 Klasse-A Power-Quality-Expertise) – und sie bleibt nur so lange offen, bis Boels oder Ramirent aufwachen.
Ziel des Termins: Fünf konkrete Entscheide, die der CEO heute treffen soll, plus Freigabe für die 90-Tage-Roadmap.
Dauer ca. 25 Minuten Vortrag, danach Diskussion.""")

# ---------------------------------------------------------------------------
# SLIDE 2 — AGENDA
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "Agenda", "Worüber wir heute sprechen", page_num=2, total=17)

agenda = [
    ("01", "Ausgangslage & Marktlücke", "Warum jetzt der Moment ist"),
    ("02", "Sofort-Prioritäten – diese Woche", "6 Deals, CHF 4,76 Mio. Potenzial"),
    ("03", "Bauphasen-Karte", "Wann liefern wir was"),
    ("04", "Team & Cross-Selling", "Rollen, Eskalation, Wärme/Kälte-Hebel"),
    ("05", "90-Tage Operationsplan", "Mai bis Oktober 2026"),
    ("06", "Fünf Entscheide für den CEO", "Heute zu freigeben"),
    ("07", "Zahlenbasis & Quellen", "Vollständige Herleitung"),
]
y = Inches(1.3)
for num, titel, sub in agenda:
    add_rect(s, Inches(0.6), y, Inches(12.2), Inches(0.72), WHITE,
             line=RGBColor(0xDD, 0xE2, 0xE8))
    add_rect(s, Inches(0.6), y, Inches(0.12), Inches(0.72), TEAL)
    add_text(s, Inches(0.95), y + Inches(0.06), Inches(0.9), Inches(0.6),
             num, size=22, bold=True, color=TEAL, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(1.85), y + Inches(0.06), Inches(7), Inches(0.35),
             titel, size=15, bold=True, color=NAVY)
    add_text(s, Inches(1.85), y + Inches(0.4), Inches(10.5), Inches(0.3),
             sub, size=11, color=GREY)
    y += Inches(0.78)

set_notes(s, """Sieben Kapitel. Wir bewegen uns von der Marktanalyse über die operative Umsetzung bis zu den fünf konkreten CEO-Entscheiden.
Im letzten Kapitel ist die vollständige Herleitung aller Zahlen dokumentiert – dort kann der CEO jederzeit nachvollziehen, woher CHF 8–20 Mio. Marktvolumen und CHF 4,96 Mio. Pipeline stammen.""")

# ---------------------------------------------------------------------------
# SLIDE 3 — AUSGANGSLAGE
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "1  Ausgangslage", "Markt Schweiz in drei Zahlen", page_num=3, total=17)

kpi_card(s, Inches(0.6), Inches(1.4), Inches(4.0), Inches(2.0),
         "113", "Datacenter Schweiz", accent=TEAL)
kpi_card(s, Inches(4.8), Inches(1.4), Inches(4.0), Inches(2.0),
         "CHF 8–20 Mio.", "adressierbares Marktvolumen / Jahr",
         accent=GOLD, big=28)
kpi_card(s, Inches(9.0), Inches(1.4), Inches(3.7), Inches(2.0),
         "9", "Neubauprojekte 2026–2028", accent=TEAL)

# Marktlücke Box
add_rect(s, Inches(0.6), Inches(3.7), Inches(12.1), Inches(1.4),
         WHITE, line=RGBColor(0xDD, 0xE2, 0xE8))
add_rect(s, Inches(0.6), Inches(3.7), Inches(0.12), Inches(1.4), GOLD)
add_text(s, Inches(0.95), Inches(3.8), Inches(11.5), Inches(0.4),
         "DIE MARKTLÜCKE", size=11, bold=True, color=GOLD)
add_text(s, Inches(0.95), Inches(4.1), Inches(11.5), Inches(1.0),
         "Kein einziger Strom-Vermieter in der Schweiz kombiniert Aggreko-Infrastruktur "
         "mit IEC 61000-4-30 Klasse-A Power-Quality-Expertise.\n"
         "Das ist unsere Lücke – und sie bleibt nur offen, bis Boels oder Ramirent aufwachen.",
         size=14, color=NAVY)

# Umsatzziel
add_rect(s, Inches(0.6), Inches(5.3), Inches(12.1), Inches(1.6),
         NAVY)
add_text(s, Inches(0.95), Inches(5.45), Inches(11.5), Inches(0.4),
         "UMSATZZIEL JAHR 1", size=11, bold=True, color=GOLD)
add_text(s, Inches(0.95), Inches(5.75), Inches(11.5), Inches(0.55),
         "CHF 500'000+  mit 5 Kernkunden", size=22, bold=True, color=WHITE)
add_text(s, Inches(0.95), Inches(6.3), Inches(11.5), Inches(0.55),
         "Pipeline-Potenzial CHF 4,96 Mio. – ein einziger Grossauftrag "
         "(Vantage Volketswil, CHF 3 Mio.) kippt die Jahresrechnung.",
         size=13, color=RGBColor(0xC9, 0xD2, 0xDE))

set_notes(s, """Drei Marktzahlen – verifiziert Mai 2026:
• 113 kommerzielle Datacenter in der Schweiz (Quelle AlgorithmWatch + SDCA-Bericht 2026).
• Adressierbares Marktvolumen pro Jahr: CHF 8–20 Mio. Bottom-Up gerechnet, Herleitung auf Slide 14.
• 9 verifizierte Neubauprojekte 2026–2028 (Baubewilligungen, Pressemitteilungen, LinkedIn).
Kernbotschaft Marktlücke: Aggreko-Infrastruktur PLUS IEC 61000-4-30 Klasse-A Power-Quality – diese Kombination hat aktuell niemand. Boels und Ramirent sind die nächsten potenziellen Wettbewerber.
Konservatives Jahr-1-Ziel: CHF 500k+ – ein realistischer Wert mit 5 Kernkunden.""")

# ---------------------------------------------------------------------------
# SLIDE 4 — SOFORT-PRIORITÄTEN (Tabelle)
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "2  Sofort-Prioritäten", "Diese Woche aktiv – 6 Ziele, CHF 4,76 Mio. Potenzial",
            page_num=4, total=17)

headers = ["#", "Ziel", "Kontakt / Kanal", "MiT-Produkt", "CHF-Potenzial"]
rows = [
    ["1", "STACK ZUR02 Beringen – Tier-IV Load-Test",
     "Steve Webb, CEO STACK EMEA\nstackinfra.com/leadership",
     "Load-Test 36 MW + PQ Kl. A + Generator Backup",
     "CHF 350'000\n15 km von Thayngen!"],
    ["2", "NorthC uptownBasel – HVO100 (Bau läuft)",
     "Patrik Hofer, MD NorthC CH\nLinkedIn InMail",
     "HVO100-Generator 18 Monate + Commissioning-Lastbank",
     "CHF 180'000\nAngebot bis 30.05."],
    ["3", "Vantage ZRH3 Volketswil – 100 MW Bauphase",
     "Wolfgang Zepf, MD Vantage CH\nLinkedIn InMail",
     "Generator-Fleet + Trafostationen + BESS + Lastbank IBN",
     "CHF 3'000'000\nGRÖSSTER DEAL CH"],
    ["4", "FlexBase Laufenburg – Erstes KI-DC Schweiz",
     "CEO/CTO unbekannt\nzefix.ch SOFORT",
     "Bauphase + BESS 5–10 MWh + PQ GPU-THD bis 50. Harm.",
     "CHF 800'000\nGPU THD 30–50%"],
    ["5", "Roger Semprini (Vaultica) – SDCA-Vorstand",
     "LinkedIn InMail\nEx-Equinix MD Schweiz",
     "PQ-Monitoring + Load-Test GEN02 + SDCA-Netzwerk",
     "Netzwerk-Schlüssel\nzu allen 113 RZ"],
    ["6", "simap + NorthC Hive Genf + Green ZW4",
     "simap.ch 9 Keywords-Alert\nPatrik Hofer / Roger Suess",
     "PQ-Monitoring + HVO100 + Jahresvertrag Lastbank",
     "CHF 430'000\nHive 150k + Green 200k"],
]
build_table(s, Inches(0.4), Inches(1.2), Inches(12.5), Inches(5.5),
            headers, rows, col_widths=[0.5, 3.0, 2.5, 3.5, 2.0],
            body_size=10, header_size=11, accent_col=4)

set_notes(s, """Sechs Sofort-Prioritäten – jede mit verifiziertem Ansprechpartner.
Priorität #2 ist termingebunden: Angebot NorthC uptownBasel muss bis 30.05. raus – das ist diese Woche.
Priorität #3 (Vantage ZRH3) ist der grösste Einzel-Deal CH: CHF 3 Mio. kippt die Jahresrechnung.
Priorität #5 (Roger Semprini) ist KEIN Umsatz – aber der Netzwerk-Schlüssel zu allen 113 RZ in der Schweiz. Strategisch wichtigste Person zum Anrufen.
Priorität #6 ist das simap.ch-Monitoring: nachdem nLighten den CHF 7,68-Mio.-Kanton-Genf-Tender gewonnen hat, ist bewiesen, dass simap-Alerts funktionieren.""")

# ---------------------------------------------------------------------------
# SLIDE 5 — BAUPHASEN-KARTE
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "3  Bauphasen-Karte", "Wer früh rein ist, bleibt drin",
            page_num=5, total=17)

phases = [
    ("PHASE 1", "Rohbau", "Baustart → Rohbau",
     "Baustellenstrom\nMobile Trafostationen",
     "Stage-V-Generator-Fleet + MS/NS-Trafostation",
     "CHF 50–300k", "Vertragsbeginn Baustart"),
    ("PHASE 2", "Ausbau", "6–18 Mt. vor IBN",
     "Zuverlässiger Dauerstrom\nBESS für Montagespitzen",
     "Langzeit-Mietvertrag 12–36 Mt. + BESS",
     "CHF 100–500k", "wiederkehrend"),
    ("PHASE 3", "Commissioning", "2–4 Wochen vor Eröffnung",
     "ITT-Vollasttest\nTier-Zertifikat\nPQ-Nachweis",
     "Lastbank-Fleet + Wärmelastbank + IEC Kl. A PQ-Protokoll",
     "CHF 80–350k", "einmalig + jährlich"),
    ("PHASE 4", "Betrieb", "Dauerbetrieb ab IBN",
     "Jahrestest NEA\nPQ-Monitoring\nHavarie-Bereitschaft",
     "PQ-Jahresvertrag + Lastbank-Test + Backup-Gen.",
     "CHF 20–200k/J.", "WIEDERKEHREND"),
]
x0 = Inches(0.4)
w = Inches(3.07)
gap = Inches(0.06)
y0 = Inches(1.25)
h = Inches(5.6)
for i, (tag, name, period, need, product, chf, freq) in enumerate(phases):
    x = x0 + (w + gap) * i
    add_rect(s, x, y0, w, h, WHITE, line=RGBColor(0xDD, 0xE2, 0xE8))
    # Header colored
    add_rect(s, x, y0, w, Inches(0.95), NAVY)
    add_text(s, x + Inches(0.15), y0 + Inches(0.1), w - Inches(0.3), Inches(0.3),
             tag, size=10, bold=True, color=GOLD)
    add_text(s, x + Inches(0.15), y0 + Inches(0.36), w - Inches(0.3), Inches(0.4),
             name, size=20, bold=True, color=WHITE)
    add_text(s, x + Inches(0.15), y0 + Inches(0.7), w - Inches(0.3), Inches(0.25),
             period, size=10, color=RGBColor(0xC9, 0xD2, 0xDE))
    # Body
    yy = y0 + Inches(1.1)
    add_text(s, x + Inches(0.15), yy, w - Inches(0.3), Inches(0.25),
             "DC BRAUCHT", size=9, bold=True, color=GREY)
    add_text(s, x + Inches(0.15), yy + Inches(0.25), w - Inches(0.3), Inches(1.1),
             need, size=11, color=NAVY)
    add_text(s, x + Inches(0.15), yy + Inches(1.45), w - Inches(0.3), Inches(0.25),
             "MIT-PRODUKT", size=9, bold=True, color=GREY)
    add_text(s, x + Inches(0.15), yy + Inches(1.7), w - Inches(0.3), Inches(1.3),
             product, size=11, color=NAVY)
    # CHF block
    add_rect(s, x + Inches(0.1), y0 + h - Inches(1.05), w - Inches(0.2),
             Inches(0.9), LIGHT)
    add_text(s, x + Inches(0.15), y0 + h - Inches(1.0), w - Inches(0.3), Inches(0.4),
             chf, size=16, bold=True, color=TEAL)
    add_text(s, x + Inches(0.15), y0 + h - Inches(0.55), w - Inches(0.3), Inches(0.35),
             freq, size=10, color=GREY)

set_notes(s, """Vier Bauphasen, vier unterschiedliche Bedürfnisse. Wer in Phase 1 reinkommt, sichert sich Phase 2–4 automatisch mit.
Phase 1 (Rohbau): Stage-V-Generator + mobile Trafostation, CHF 50–300k.
Phase 2 (Ausbau): Langzeit-Mietvertrag 12–36 Monate + BESS, wiederkehrend.
Phase 3 (Commissioning): Lastbank-Fleet + IEC Klasse-A-PQ-Protokoll – hier sitzt unsere stärkste technische Differenzierung.
Phase 4 (Betrieb): Jahresvertrag PQ + Lastbank-Test + Havarie-Backup – das ist das nachhaltige Geschäftsmodell.
Strategie: Wo immer möglich Einstieg in Phase 1 oder 2 sichern.""")

# ---------------------------------------------------------------------------
# SLIDE 6 — PROJEKTSTATUS HEUTE
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "3  Projektstatus heute", "Wer steht wo – und was passiert diese Woche",
            page_num=6, total=17)

headers = ["Projekt", "Phase", "Deadline", "Sofortaktion"]
rows = [
    ["NorthC uptownBasel BL", "Phase 2 aktiv", "Angebot 30.05.",
     "HVO100-Generator-Offerte heute starten → Innendienst"],
    ["STACK ZUR02 Beringen SH", "Phase 3 SOFORT", "E-Mail KW21",
     "Steve Webb kontaktieren – Tier-IV Load-Test anbieten"],
    ["Green DC ZW4 Lupfig AG", "Phase 3 / 4", "Angebot sofort",
     "PQ-Monitoring als Einstiegsprodukt – Roger Suess (SDCA-Präs.)"],
    ["FlexBase KI-DC Laufenburg AG", "Phase 1 Planung", "Recherche HEUTE",
     "zefix.ch: CEO/CTO identifizieren – GPU THD 30–50% = unser Argument"],
    ["Vantage ZRH3 Volketswil ZH", "Phase 1 Planung", "LinkedIn KW21",
     "Wolfgang Zepf – Frühkontakt sichert Bauphase-Strom-Auftrag 2027"],
    ["NorthC The Hive Genf GE", "Phase 1 / 2", "Q3 / 2026",
     "Patrik Hofer – HVO100 + D2C-PQ, Westschweiz-Präsenz aufbauen"],
]
build_table(s, Inches(0.4), Inches(1.3), Inches(12.5), Inches(5.3),
            headers, rows, col_widths=[3.2, 2.0, 1.8, 5.5],
            body_size=11, header_size=12)

set_notes(s, """Sechs aktive Projekte – jedes mit konkreter Sofortaktion und Deadline.
Wichtigste Termine: NorthC uptownBasel Angebot bis 30.05. (in 3 Tagen) und FlexBase-Recherche heute.
STACK ZUR02 ist Phase 3 SOFORT – das heisst, der Load-Test ist in den nächsten Wochen fällig. Wer jetzt nicht angreift, verliert den Tier-IV-Test.""")

# ---------------------------------------------------------------------------
# SLIDE 7 — TEAM
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "4  Team – Wer macht was", "Klare Rollen, klare Eskalation",
            page_num=7, total=17)

headers = ["Person", "Konkrete Aufgaben", "Eskalation bei"]
rows = [
    ["Burak Ücöz\n(Strom-Vertrieb)",
     "Alle A++/A+-Kundenkontakte; techn. Qualifizierung; "
     "Angebots-Briefing; LinkedIn-Akquise; Powertage 16.–18. Juni",
     "CEO bei Deal > CHF 500k\nOwen bei Flottenengpass"],
    ["Innendienst\n(Back-Office)",
     "Formalangebote < 24h Turnaround; Auftragsverarbeitung; "
     "VSE-Anzeige koordinieren; Rahmenvertrags-Administration",
     "Burak bei techn. Fragen\nCEO bei Sonderkonditionen"],
    ["Stephan Marty\n(Projektleitung)",
     "Projektstart nach Abschluss; Koordination Logistik + Techniker; "
     "Baustellenleiter-Kommunikation; Meilenstein-Tracking",
     "Burak bei Kundeneskalation\nCEO bei Projektrisiko"],
    ["Sarah / Samuel\n(Feldtechniker)",
     "Generator-Aufbau IBN; PQ-Messung IEC Kl. A vor Ort; "
     "Lastbank-Test + Protokoll; techn. Kundenkontakt Baustelle",
     "Burak bei Sonderwunsch\nStephan bei Logistik"],
    ["Owen Farron\n(Aggreko Fleet)",
     "BESS-Verfügbarkeit bestätigen; Generator-Sondergrössen; "
     "Priority-Allocation CH-DC-Pipeline – VOR Angebotsversand",
     "Burak bei Engpass\nCEO für strat. Allokation"],
]
build_table(s, Inches(0.4), Inches(1.3), Inches(12.5), Inches(5.3),
            headers, rows, col_widths=[2.2, 7.0, 3.3],
            body_size=10, header_size=12)

set_notes(s, """Fünf klar abgegrenzte Rollen. Wichtig:
• Burak ist Single Point of Contact für alle A++/A+-Kunden.
• Innendienst garantiert 24h-Turnaround – das ist unser operatives Differenzierungsmerkmal gegenüber Boels/Ramirent.
• Owen Farron muss VOR Angebotsversand die Fleet-Verfügbarkeit bestätigen. Ohne diese Bestätigung kein Angebot – kein Auftrag.
Eskalationspfade sind explizit definiert: > CHF 500k landet immer beim CEO.""")

# ---------------------------------------------------------------------------
# SLIDE 8 — CROSS-SELLING
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "4.2  Cross-Selling Wärme / Kälte → Strom",
            "Drei direkte Hebel – heute schon nutzbar",
            page_num=8, total=17)

headers = ["DC-Kunde", "MiT-Verbindung", "Strom-Produkt", "Cross-Sell"]
rows = [
    ["Vantage Volketswil ZRH3",
     "Energie360 = Abwärme-Partner ab 2028",
     "Bauphase-Generator + BESS",
     "Mobile Kühlung Bauphase"],
    ["Green DC Dielsdorf",
     "Energie360 = Abwärme 11'500 Haushalte",
     "PQ-Monitoring + Gen.-Backup",
     "Kälte-Sommerspitze + Chiller-Miete"],
    ["CoolWorld Dielsdorf (bestehend)",
     "Bestehender MiT-Kältekunde!",
     "600 kVA Generator (offen)",
     "Kälte-Beziehung als Türöffner"],
]
build_table(s, Inches(0.4), Inches(1.3), Inches(12.5), Inches(2.4),
            headers, rows, col_widths=[2.7, 3.5, 3.0, 3.3],
            body_size=11, header_size=12)

# Prozess
add_rect(s, Inches(0.4), Inches(4.0), Inches(12.5), Inches(2.5), NAVY)
add_text(s, Inches(0.7), Inches(4.15), Inches(12), Inches(0.4),
         "PROZESS  –  Keine Kaltakquise. Volle Glaubwürdigkeit.",
         size=12, bold=True, color=GOLD)

steps = [
    ("1", "Wärme / Kälte-Kollege", "stellt Burak per E-Mail vor"),
    ("2", "Burak qualifiziert", "Strom-Bedarf im 30-Min.-Call"),
    ("3", "Innendienst liefert", "Angebot < 24h"),
]
xc = Inches(0.7)
for i, (n, who, what) in enumerate(steps):
    bx = xc + Inches(4.05) * i
    add_rect(s, bx, Inches(4.7), Inches(3.85), Inches(1.65), WHITE)
    add_rect(s, bx, Inches(4.7), Inches(3.85), Inches(0.08), GOLD)
    add_text(s, bx + Inches(0.2), Inches(4.85), Inches(0.7), Inches(0.7),
             n, size=36, bold=True, color=TEAL)
    add_text(s, bx + Inches(1.0), Inches(4.95), Inches(2.8), Inches(0.4),
             who, size=13, bold=True, color=NAVY)
    add_text(s, bx + Inches(1.0), Inches(5.35), Inches(2.8), Inches(0.8),
             what, size=11, color=GREY)

set_notes(s, """Cross-Selling ist der schnellste Weg zu Umsatz, weil wir nicht kalt akquirieren müssen.
Drei konkrete Hebel: Vantage, Green DC und CoolWorld – bei allen dreien hat MiT bereits eine Wärme- oder Kälte-Beziehung.
Der Prozess ist bewusst leichtgewichtig: E-Mail-Intro → 30-Min.-Call → 24h-Angebot. Keine Kaltakquise, volle Glaubwürdigkeit, schnelle Konversion.""")

# ---------------------------------------------------------------------------
# SLIDE 9 — 90-TAGE PLAN
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "5  90-Tage Operationsplan", "Mai bis Oktober 2026",
            page_num=9, total=17)

headers = ["Zeitraum", "Aktion", "Verantwortlich", "CHF-Ziel"]
rows = [
    ["KW21–22\nMAI",
     "• simap.ch-Alert einrichten\n• Steve Webb kontaktieren (STACK)\n"
     "• LinkedIn: Zepf, Hofer, Semprini\n• NorthC uptownBasel HVO100-Angebot finalisieren\n"
     "• FlexBase: zefix.ch Betreiber identifizieren",
     "Burak (Akquise)\nInnendienst (Angebot NorthC)",
     "CHF 530'000\nErstangebote raus"],
    ["KW23–24\nJUNI",
     "• Powertage 2026 (16.–18.06., Zürich)\n• SDCA-Mitgliedschaft anfragen (R. Suess)\n"
     "• Aggreko EMEA Koordination (Digital Realty + Fleet)\n• nLighten CH: PQ-Angebot",
     "Burak (Messe + SDCA)\nOwen Farron (Fleet)",
     "5–10 neue DC-Kontakte\nCHF 80'000 nLighten"],
    ["JULI 2026",
     "• NorthC uptownBasel: VERTRAGSABSCHLUSS (erstes Referenzprojekt)\n"
     "• Green ZW4: PQ-Monitoring-Angebot\n• STACK ZUR02: Load-Test formell",
     "Burak → Stephan Übergabe\nInnendienst",
     "CHF 300'000\nErstes Referenzprojekt"],
    ["AUGUST 2026",
     "• STACK ZUR02: Load-Test-Auftrag\n• Vantage Volketswil: Bauphase-Strom-Offerte\n"
     "• NorthC The Hive Genf: HVO100 + D2C-PQ",
     "Burak + Owen (Fleet)\nInnendienst",
     "CHF 350'000\nSTACK Load-Test"],
    ["SEPT.–OKT.",
     "• Green DC: PQ-Rahmenvertrag + Cross-Sell Wärme\n"
     "• NorthC DACH: Rahmenvertrag alle 6 CH-Standorte\n"
     "• FlexBase: Bauphase-Angebot\n• Vantage ZRH1+2: Jahresvertrag Lastbank",
     "Burak + Wärme/Kälte-Kollege\nInnendienst + Stephan",
     "CHF 500'000+\nwiederkehrend"],
]
build_table(s, Inches(0.4), Inches(1.3), Inches(12.5), Inches(5.4),
            headers, rows, col_widths=[1.6, 6.5, 2.4, 2.0],
            body_size=10, header_size=12, accent_col=3)

set_notes(s, """Fünf Etappen über 90 Tage – jede mit konkretem CHF-Ziel.
Meilenstein 1: Juli – NorthC uptownBasel ist unser erstes Referenzprojekt. Dieser Vertragsabschluss legitimiert alle weiteren Akquise-Gespräche.
Meilenstein 2: August – STACK Load-Test als technischer Proof-of-Concept Tier-IV.
Meilenstein 3: September/Oktober – Übergang in wiederkehrendes Geschäft (Rahmenverträge, Jahresverträge). Das ist der Wechsel vom Projekt- zum Plattform-Geschäftsmodell.""")

# ---------------------------------------------------------------------------
# SLIDE 10 — 5 ENTSCHEIDE
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "6  Fünf Entscheide für den CEO", "Heute zu freigeben",
            page_num=10, total=17)

decisions = [
    ("1", "SDCA-Mitgliedschaft genehmigen",
     "CHF 2'000–5'000 / Jahr · Zugang zu allen 113 CH-DC-Betreibern über "
     "Roger Suess (SDCA-Präsident / Green DC CEO) und Roger Semprini (SDCA-Vorstand / Vaultica CCO). "
     "Günstigster Netzwerkkanal im Markt."),
    ("2", "Aggreko Fleet-Priorität CH-DC sichern",
     "Owen Farron muss Priority-Allocation für CH-Pipeline bestätigen, bevor wir Angebote abgeben. "
     "Ohne Flottenbestätigung kein Angebot, kein Auftrag. CEO-Level-Anfrage an Aggreko EMEA nötig."),
    ("3", "ARM-Kalkulationstool für Burak + Samuel",
     "Ohne ARM-Tool (Aggreko Rate Matrix) kostet jede Preisanfrage Tage. "
     "Bei 10 parallelen Projekten = Flaschenhals. Sofort-Anfrage an Aggreko."),
    ("4", "Powertage 2026 – MiT-Strom-Auftritt planen",
     "16.–18. Juni, Messe Zürich. Burak tritt als MiT-Strom-Gesicht auf (nicht mehr CBM). "
     "Budget CHF 2'000–5'000. Signal an den Markt: Wir sind da."),
    ("5", "Depot-Entscheid Diessenhofen",
     "Stagelight-Equipment (Frauenfeld Juli) nicht zurück nach Holland. "
     "In Diessenhofen einlagern und direkt nach Gampel (August). "
     "Spart Transportkosten, baut lokale Lagerpräsenz auf."),
]
y = Inches(1.3)
for n, titel, body in decisions:
    add_rect(s, Inches(0.4), y, Inches(12.5), Inches(1.0), WHITE,
             line=RGBColor(0xDD, 0xE2, 0xE8))
    add_rect(s, Inches(0.4), y, Inches(0.85), Inches(1.0), NAVY)
    add_text(s, Inches(0.4), y, Inches(0.85), Inches(1.0),
             n, size=36, bold=True, color=GOLD,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(1.45), y + Inches(0.1), Inches(11.2), Inches(0.35),
             titel, size=14, bold=True, color=NAVY)
    add_text(s, Inches(1.45), y + Inches(0.42), Inches(11.2), Inches(0.55),
             body, size=10, color=GREY)
    y += Inches(1.06)

set_notes(s, """Fünf konkrete Entscheide, die heute fallen müssen:
1. SDCA-Mitgliedschaft – günstigster Netzwerkhebel, Sofortzugang zu 113 Betreibern.
2. Fleet-Priorität – kritisch, sonst können wir keine verbindlichen Angebote abgeben.
3. ARM-Tool – ohne diese Kalkulationsgrundlage skaliert das Geschäft nicht.
4. Powertage – Signalmoment am Markt. Burak als MiT-Strom-Gesicht.
5. Depot-Entscheid – kleiner operativer Punkt mit lokaler Logistikwirkung.
Ich brauche heute zu allen fünf Punkten ein Go oder No-Go.""")

# ---------------------------------------------------------------------------
# SLIDE 11 — MARKT-BASIS 113 RZ
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "7.1  Marktbasis", "113 Rechenzentren · 850 MW · 9 Neubauten",
            page_num=11, total=17)

headers = ["Zahl", "Quelle", "Bedeutung"]
rows = [
    ["113 Rechenzentren\nSchweiz",
     "AlgorithmWatch + SDCA-Bericht 2026 (öffentlich)",
     "Alle kommerziellen DC-Betreiber CH, verifiziert Mai 2026. "
     "Basis jeder Marktanteilsrechnung."],
    ["850 MW installierte\nKapazität",
     "SDCA 2026 / Energiemonitoring CH",
     "Gesamte IT-Leistung aller 113 RZ. "
     "Prognose 2031: 950+ MW durch KI-Boom."],
    ["9 bestätigte Neubau-\nprojekte 2026–2028",
     "Baubewilligungen, Pressemitteilungen, LinkedIn (Mai 2026)",
     "STACK ZUR02, Vantage ZRH3, NorthC uptownBasel, NorthC Hive GE, "
     "FlexBase Laufenburg, Green ZW4, Green Dielsdorf MC3, Digital Realty ZUR4, Vaultica GEN02."],
    ["CHF 7,68 Mio.\nKanton Genf Tender",
     "simap.ch Ausschreibungsdatenbank CH (April 2026)",
     "Öffentliche Ausschreibung, gewonnen von nLighten. "
     "Beweis: simap.ch-Monitoring funktioniert."],
]
build_table(s, Inches(0.4), Inches(1.3), Inches(12.5), Inches(5.3),
            headers, rows, col_widths=[2.5, 3.8, 6.2],
            body_size=11, header_size=12)

set_notes(s, """Die Marktgrundlage steht auf vier öffentlich nachvollziehbaren Zahlen.
Wichtig für den CEO: Wir argumentieren ausschliesslich mit verifizierten öffentlichen Quellen. Keine geschätzten Werte ohne Beleg.
Der CHF 7,68 Mio. Genf-Tender ist der Lakmus-Test: Er wurde an nLighten vergeben – ohne simap-Alert wäre er an uns vorbeigegangen. Deshalb ist Sofort-Priorität #6 das Aufsetzen des Alerts.""")

# ---------------------------------------------------------------------------
# SLIDE 12 — CHF 8–20 Mio. Marktvolumen
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "7.2  Adressierbares Marktvolumen", "Bottom-Up CHF 8–20 Mio. / Jahr",
            page_num=12, total=17)

headers = ["Produktkategorie", "Kunden", "×/J", "Ø CHF", "Gesamt", "MiT-%", "MiT-Potenzial"]
rows = [
    ["Load-Test + PQ (Jahrestest)", "113", "1×", "18'000", "2'034'000", "28 %", "CHF 570'000"],
    ["Generator Bauphase Neubau", "9", "3×", "280'000", "7'560'000", "22 %", "CHF 1'663'000"],
    ["Wartungs-Backup / Revision", "80", "2×", "24'000", "3'840'000", "18 %", "CHF 691'000"],
    ["PQ-Monitoring Dauerbetrieb", "50", "5×", "30'000", "7'500'000", "32 %", "CHF 2'400'000"],
    ["BESS Peak-Shaving DC", "20", "2×", "300'000", "12'000'000", "12 %", "CHF 1'440'000"],
    ["Havariefall / Notfall 24h", "113", "0,5×", "45'000", "2'543'000", "38 %", "CHF 966'000"],
    ["Langzeit-Notstrom (> 1 J.)", "20", "2×", "160'000", "6'400'000", "15 %", "CHF 960'000"],
    ["Mobile Kühlung + Lastbank + Trafo", "60/9/10", "mix", "mix", "5'460'000", "21 %", "CHF 1'131'000"],
    ["TOTAL", "", "", "", "47'337'000", "~21 %", "CHF 9'821'000"],
]
build_table(s, Inches(0.4), Inches(1.25), Inches(12.5), Inches(4.4),
            headers, rows, col_widths=[3.8, 1.0, 0.7, 1.3, 1.7, 1.0, 1.8],
            body_size=10, header_size=11, accent_col=6)

add_rect(s, Inches(0.4), Inches(5.85), Inches(12.5), Inches(1.15),
         LIGHT, line=RGBColor(0xDD, 0xE2, 0xE8))
add_rect(s, Inches(0.4), Inches(5.85), Inches(0.12), Inches(1.15), GOLD)
add_text(s, Inches(0.7), Inches(5.95), Inches(12), Inches(0.3),
         "WARUM CHF 8–20 MIO. UND NICHT CHF 9,8 MIO.?",
         size=11, bold=True, color=GOLD)
add_text(s, Inches(0.7), Inches(6.25), Inches(12), Inches(0.75),
         "(1) Marktanteile = Schätzungen aus Aggreko DACH/UK-Erfahrungswerten. "
         "Bei schlechterer Quote = CHF 8 Mio., bei optimaler = CHF 20 Mio.   "
         "(2) BESS schwankt stark je nach Flottenverfügbarkeit.   "
         "(3) Havariefall per Definition nicht planbar.\n"
         "Mittelpunkt CHF 9,8 Mio. · Minimum CHF 8 Mio. · Optimum CHF 20 Mio. (inkl. Vantage Volketswil allein CHF 3 Mio.)",
         size=10, color=NAVY)

set_notes(s, """Diese Tabelle ist die vollständige Bottom-Up-Herleitung des adressierbaren Marktvolumens.
Acht Produktkategorien, jeweils: Anzahl Kunden × Einsätze pro Jahr × Durchschnittsauftragswert = Gesamtmarkt CH. Davon nehmen wir den realistischen Marktanteil basierend auf Aggreko-Erfahrung in DACH/UK.
Ergebnis: CHF 9,82 Mio. – das ist der Mittelpunkt der Spanne CHF 8–20 Mio.
Wichtigste Treiber: PQ-Monitoring Dauerbetrieb (CHF 2,4 Mio.) und Generator Bauphase Neubau (CHF 1,66 Mio.). Beide Felder sind genau dort, wo unsere Marktlücke (Aggreko + IEC Kl. A) am stärksten greift.""")

# ---------------------------------------------------------------------------
# SLIDE 13 — A++ Pipeline CHF 4,96 Mio.
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "7.3  A++ Pipeline – CHF 4,96 Mio.",
            "Nur verifizierte Projekte mit Kontaktperson",
            page_num=13, total=17)

headers = ["Projekt", "CHF", "Basis der Schätzung", "Quelle"]
rows = [
    ["Vantage ZRH3 Volketswil\n100 MW", "3'000'000",
     "32× Generator à 3'500 CHF/Tag × 270 Tage + 5× Trafostation + BESS 15 MWh + Lastbank IBN 100 MW",
     "vantage-dc.com + Interview W. Zepf + EKZ-Unterwerk-Ankündigung"],
    ["STACK ZUR02 Beringen\n36 MW", "350'000",
     "12× Lastbank-Unit à 1'500 CHF/Tag × 3 Tage + PQ-Kl.A-Protokoll + Techniker + Backup-Gen.",
     "stackinfra.com/beringen + Aggreko Load-Test-Erfahrungswert UK/DACH"],
    ["FlexBase Laufenburg KI-DC\n20 MW", "800'000",
     "7× Generator Bauphase + BESS 5 MWh + GPU-THD-PQ-Monitoring Langzeitvertrag",
     "flexbase.ch + Handelsregister AG + GPU-THD-Hyperscaler-Referenzwerte"],
    ["NorthC uptownBasel + Hive Genf", "330'000",
     "HVO100-Gen. 18 Mt. × 8'500 CHF/Mt. = 153k + Lastbank Commissioning 27k × 2",
     "northc.com/ch + HVO100-Pflicht öffentlich kommuniziert"],
    ["Vaultica PQ + Load-Test GEN02", "480'000",
     "PQ-Monitoring 2 Standorte 15k/Mt. × 12 + Load-Test 40 MW GEN02 Gland 120k",
     "vaultica.com + LinkedIn R. Semprini (März 2026) + SDCA-Verzeichnis"],
    ["TOTAL A++-Pipeline", "4'960'000",
     "Nur identifizierte, verifizierte Projekte mit Kontaktpersonen",
     "Alle in Sheet 04 CH PIPELINE der DC Suite"],
]
build_table(s, Inches(0.4), Inches(1.3), Inches(12.5), Inches(5.4),
            headers, rows, col_widths=[2.6, 1.4, 4.5, 4.0],
            body_size=10, header_size=11, accent_col=1)

set_notes(s, """CHF 4,96 Mio. sind keine Wunschzahlen – jeder Einzelposten hat eine verifizierte Quelle und eine namentlich identifizierte Kontaktperson.
Der grösste Hebel ist Vantage Volketswil (CHF 3 Mio.) – ein einziger Deal, der die Jahresrechnung kippt.
Die anderen vier Projekte zusammen ergeben rund CHF 2 Mio. – mit deutlich geringerem Risiko, weil sie weiter im Verkaufsprozess sind oder kürzere Vorlaufzeiten haben (STACK, NorthC).""")

# ---------------------------------------------------------------------------
# SLIDE 14 — Weitere Quellen
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "7.4  Alle weiteren Zahlen und ihre Quellen",
            "Vollständige Nachvollziehbarkeit",
            page_num=14, total=17)

headers = ["Aussage / Zahl", "Quelle", "Methode / Kommentar"]
rows = [
    ["CHF 500k+ Umsatzziel Jahr 1",
     "MiT-interne GL-Zielvorgabe (Sheet 10 DC Suite)",
     "Konservativster Wert aus Szenarienanalyse. Erreichbar mit 5 Kernkunden à Ø CHF 100k."],
    ["15 km Thayngen → STACK Beringen",
     "Google Maps (verifiziert)",
     "MiT-Depot Thayngen SH → Beringen SH. Entscheidend für Reaktionszeit und Logistikkosten."],
    ["GPU THD 30–50 % bei FlexBase / KI-DC",
     "IEC 61000-3-2 + Aggreko-Messpraxis UK + öffentl. IEEE-Papers",
     "GPU-Gleichrichter (Switch-Mode-Netzteile) erzeugen typisch 25–50 % THD-I. IEC 61000-4-30 Kl. A ist deshalb Pflicht."],
    ["HVO100 = Pflicht NorthC (alle 6 CH-RZ)",
     "northc.com/sustainability + SDCA-Konferenz 2025",
     "NorthC hat HVO100 als verbindlichen Standard für alle EU-Standorte kommuniziert."],
    ["Roger Semprini = Schlüssel zu 113 RZ",
     "LinkedIn März 2026 + SDCA-Liste + equinix.ch Archiv",
     "Ex-Equinix MD Schweiz (10+ J.). Heute CCO Vaultica + SDCA-Vorstand. Kennt alle Betreiber persönlich."],
    ["Szenarien Jahr 1–3 (25 / 50 / 25 %)",
     "Sheet 10 MARKTVOLUMEN MiT × Aggreko DC Intelligence Suite 2026",
     "Min: 2 Kunden, 4 Aufträge. Realistisch: 5 Kunden, 10 Aufträge. Optimal: 12 Kunden, 25 Aufträge."],
]
build_table(s, Inches(0.4), Inches(1.3), Inches(12.5), Inches(5.3),
            headers, rows, col_widths=[3.5, 4.0, 5.0],
            body_size=10, header_size=11)

set_notes(s, """Für jede zentrale Aussage im Dokument ist die Quelle dokumentiert.
Alle Rohdaten liegen in der MiT × Aggreko DC Intelligence Suite 2026 (Excel, 18 Sheets, 10'572 globale DC-Projekte, 8'502 Kontakte, 26 CH-Betreiber). Auf Anfrage des CEO jederzeit verfügbar.""")

# ---------------------------------------------------------------------------
# SLIDE 15 — Risiken & Annahmen (kurze Reflexion)
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "Risiken & Annahmen", "Was unser Plan kippen könnte",
            page_num=15, total=17)

cols = [
    ("RISIKEN", RED, [
        "Boels oder Ramirent bauen PQ-Kl.-A-Kompetenz auf",
        "Aggreko Fleet-Engpass → Angebote ohne Fleet-Bestätigung",
        "Vantage ZRH3 verschiebt Bauphase 2027 → Cashflow-Risiko",
        "Keine SDCA-Mitgliedschaft = keine Netzwerk-Reichweite",
    ]),
    ("ANNAHMEN", TEAL, [
        "Marktanteile 12–38 % aus DACH/UK skalieren auf CH",
        "HVO100-Pflicht bleibt für NorthC verbindlich",
        "KI-Boom treibt PQ-Bedarf (GPU-THD)",
        "9 Neubauprojekte werden wie angekündigt umgesetzt",
    ]),
    ("HEBEL", GOLD, [
        "Erstes Referenzprojekt (NorthC uptownBasel) bis Juli",
        "Powertage-Auftritt Juni 2026 als Marktsignal",
        "Cross-Selling über Wärme/Kälte (3 Live-Hebel)",
        "Roger Semprini öffnet 113-RZ-Netzwerk",
    ]),
]
xw = Inches(4.1)
for i, (label, color, items) in enumerate(cols):
    x = Inches(0.4) + (xw + Inches(0.1)) * i
    add_rect(s, x, Inches(1.3), xw, Inches(5.3), WHITE,
             line=RGBColor(0xDD, 0xE2, 0xE8))
    add_rect(s, x, Inches(1.3), xw, Inches(0.55), color)
    add_text(s, x + Inches(0.2), Inches(1.32), xw - Inches(0.4), Inches(0.5),
             label, size=14, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
    add_bullets(s, x + Inches(0.2), Inches(2.0), xw - Inches(0.4), Inches(4.5),
                items, size=12, bullet_color=color)

set_notes(s, """Drei Spalten – ehrliche Sicht auf das, was schiefgehen kann, was wir annehmen, und welche Hebel wir aktiv ziehen.
Wichtigstes Risiko: Wettbewerb baut PQ-Kompetenz auf. Deshalb das Tempo – wir müssen die Lücke besetzen, bevor sie zugemacht wird.
Wichtigste Annahme: Marktanteile aus DACH/UK skalieren. Falls nicht, landen wir am unteren Ende der CHF-8-Mio.-Spanne.""")

# ---------------------------------------------------------------------------
# SLIDE 16 — Zusammenfassung
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
page_chrome(s, "Zusammenfassung", "Worauf es ankommt", page_num=16, total=17)

points = [
    ("Marktlücke besetzen, solange sie offen ist",
     "Aggreko + IEC 61000-4-30 Kl. A – diese Kombination hat aktuell niemand."),
    ("CHF 500k+ Jahr 1 ist realistisch",
     "5 Kernkunden à Ø CHF 100k aus einer Pipeline von CHF 4,96 Mio."),
    ("Sechs Sofort-Deals diese Woche aktiv",
     "Termingebunden: NorthC uptownBasel-Angebot bis 30.05."),
    ("Fünf Entscheide vom CEO heute",
     "SDCA · Fleet-Priorität · ARM-Tool · Powertage · Depot Diessenhofen."),
    ("Wiederkehrend ab Q4",
     "Rahmenverträge und Jahresverträge bilden die nachhaltige Basis."),
]
y = Inches(1.4)
for titel, sub in points:
    add_rect(s, Inches(0.5), y, Inches(0.4), Inches(0.85), TEAL)
    add_text(s, Inches(0.5), y, Inches(0.4), Inches(0.85),
             "✓", size=22, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(1.1), y + Inches(0.05), Inches(11.5), Inches(0.4),
             titel, size=16, bold=True, color=NAVY)
    add_text(s, Inches(1.1), y + Inches(0.45), Inches(11.5), Inches(0.4),
             sub, size=12, color=GREY)
    y += Inches(1.0)

set_notes(s, """Fünf Punkte zum Mitnehmen.
Schlüsselbotschaft an den CEO: Wir haben das Wissen, die Pipeline und die Roadmap. Was wir heute brauchen, sind die fünf Entscheide.""")

# ---------------------------------------------------------------------------
# SLIDE 17 — SCHLUSSFOLIE (ZITAT)
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, NAVY)
add_rect(s, 0, Inches(3.2), SW, Inches(0.04), GOLD)

add_text(s, Inches(1.5), Inches(1.4), Inches(10.3), Inches(0.5),
         "SUN TZU", size=12, bold=True, color=GOLD,
         align=PP_ALIGN.CENTER)
add_text(s, Inches(1.5), Inches(2.0), Inches(10.3), Inches(1.2),
         "„Der Feldherr, der siegt, errechnet viele Vorteile,\nbevor der Kampf beginnt.\"",
         size=28, color=WHITE, align=PP_ALIGN.CENTER)

add_text(s, Inches(1.5), Inches(3.7), Inches(10.3), Inches(1.0),
         "Wir haben gerechnet.\nDie Lücke ist offen. Jetzt müssen wir springen.",
         size=22, bold=True, color=GOLD, align=PP_ALIGN.CENTER)

add_text(s, Inches(1.5), Inches(5.5), Inches(10.3), Inches(0.4),
         "DANKE.", size=18, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER)
add_text(s, Inches(1.5), Inches(6.0), Inches(10.3), Inches(0.4),
         "Fragen, Diskussion, Entscheide.", size=14,
         color=RGBColor(0xC9, 0xD2, 0xDE), align=PP_ALIGN.CENTER)

add_text(s, Inches(0.5), SH - Inches(0.45), Inches(12.3), Inches(0.3),
         "Burak Ücöz  ·  Mobil in Time AG × Aggreko  ·  27. Mai 2026",
         size=10, color=RGBColor(0x8E, 0x97, 0xA5),
         align=PP_ALIGN.CENTER)

set_notes(s, """Schlussbild mit dem Sun-Tzu-Zitat aus dem Originaldokument.
Übergang zur Diskussion. Drei mögliche Fragen, auf die ich vorbereitet bin:
1. Wie schnell können wir Fleet-Allocation für die Top-3-Projekte garantieren?
2. Welcher Deal hat das geringste Closing-Risiko? – NorthC uptownBasel.
3. Was passiert, wenn Vantage 2027 sich verschiebt? – Dann basieren wir Jahr 1 auf STACK + NorthC + Green + FlexBase = ca. CHF 1,7 Mio. Pipeline.""")

# ---------------------------------------------------------------------------
out = "/home/user/Burak/output/MiT_CEO_Roadmap_2026_2028.pptx"
prs.save(out)
print(f"OK -> {out}")
print(f"Slides: {len(prs.slides)}")
