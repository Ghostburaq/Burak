"""
Apple-style rebuild of MiT Strom QuickDive Marketing deck.
Generates BOTH light and dark variants.
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# --- Slide geometry (16:9) ---
SLIDE_W = Emu(12192000)
SLIDE_H = Emu(6858000)

# --- Apple-style typography stack ---
# SF Pro isn't reliably installed; Helvetica Neue is the classic Apple substitute.
FONT_DISPLAY = "Helvetica Neue"
FONT_TEXT    = "Helvetica Neue"
FONT_MONO    = "SF Mono"

# ---- THEMES ----
LIGHT = {
    "name": "light",
    "bg":        RGBColor(0xF5, 0xF5, 0xF7),   # Apple.com page bg
    "surface":   RGBColor(0xFF, 0xFF, 0xFF),
    "surface2":  RGBColor(0xEC, 0xEC, 0xEE),
    "hairline":  RGBColor(0xD2, 0xD2, 0xD7),
    "ink":       RGBColor(0x1D, 0x1D, 0x1F),
    "ink2":      RGBColor(0x6E, 0x6E, 0x73),
    "ink3":      RGBColor(0x86, 0x86, 0x8B),
    "accent":    RGBColor(0x00, 0x71, 0xE3),   # Apple blue
    "accent2":   RGBColor(0xBF, 0x5A, 0xF2),   # violet
    "accent3":   RGBColor(0x34, 0xC7, 0x59),   # green
    "warn":      RGBColor(0xFF, 0x9F, 0x0A),
    "grad_from": RGBColor(0x00, 0x71, 0xE3),
    "grad_to":   RGBColor(0xBF, 0x5A, 0xF2),
}
DARK = {
    "name": "dark",
    "bg":        RGBColor(0x00, 0x00, 0x00),
    "surface":   RGBColor(0x1C, 0x1C, 0x1E),
    "surface2":  RGBColor(0x2C, 0x2C, 0x2E),
    "hairline":  RGBColor(0x3A, 0x3A, 0x3C),
    "ink":       RGBColor(0xF5, 0xF5, 0xF7),
    "ink2":      RGBColor(0xAE, 0xAE, 0xB2),
    "ink3":      RGBColor(0x8E, 0x8E, 0x93),
    "accent":    RGBColor(0x0A, 0x84, 0xFF),
    "accent2":   RGBColor(0xBF, 0x5A, 0xF2),
    "accent3":   RGBColor(0x30, 0xD1, 0x58),
    "warn":      RGBColor(0xFF, 0x9F, 0x0A),
    "grad_from": RGBColor(0x0A, 0x84, 0xFF),
    "grad_to":   RGBColor(0xBF, 0x5A, 0xF2),
}

# ---------- Low-level helpers ----------

def solid_fill(shape, rgb: RGBColor):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb

def no_line(shape):
    shape.line.fill.background()

def line(shape, rgb: RGBColor, width_pt=0.75):
    shape.line.color.rgb = rgb
    shape.line.width = Pt(width_pt)

def add_bg(slide, T):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    solid_fill(r, T["bg"])
    no_line(r)
    return r

def add_rect(slide, x, y, w, h, fill=None, radius=None, line_rgb=None, line_w=0.75):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape_type, x, y, w, h)
    if radius is not None:
        # adjust corner radius
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        s.fill.background()
    else:
        solid_fill(s, fill)
    if line_rgb is None:
        no_line(s)
    else:
        line(s, line_rgb, line_w)
    return s

A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
def add_gradient_rect(slide, x, y, w, h, from_rgb, to_rgb, angle_deg=45, radius=None):
    s = add_rect(slide, x, y, w, h, radius=radius)
    sp = s.element
    # spPr lives in the a: namespace for shape elements in DrawingML,
    # but for pptx sp elements the spPr is in the p: namespace with a: children.
    # Try both, prefer whichever we find.
    spPr = sp.find('.//{'+A_NS+'}spPr')
    if spPr is None:
        # p:sp has p:spPr child
        for child in sp:
            if child.tag.endswith('}spPr'):
                spPr = child; break
    if spPr is None:
        return s
    # remove existing fills
    for child in list(spPr):
        tag = etree.QName(child).localname
        if tag in ('solidFill','gradFill','noFill','blipFill','pattFill'):
            spPr.remove(child)
    grad = etree.SubElement(spPr, '{'+A_NS+'}gradFill',
                            attrib={'flip':'none', 'rotWithShape':'1'})
    gsLst = etree.SubElement(grad, '{'+A_NS+'}gsLst')
    for pos, col in ((0, from_rgb), (100000, to_rgb)):
        gs = etree.SubElement(gsLst, '{'+A_NS+'}gs', attrib={'pos': str(pos)})
        etree.SubElement(gs, '{'+A_NS+'}srgbClr',
            attrib={'val': '{:02X}{:02X}{:02X}'.format(col[0], col[1], col[2])})
    etree.SubElement(grad, '{'+A_NS+'}lin',
                     attrib={'ang': str(angle_deg * 60000), 'scaled': '1'})
    etree.SubElement(grad, '{'+A_NS+'}tileRect')
    # Move grad before ln if present
    ln = None
    for child in spPr:
        if etree.QName(child).localname == 'ln':
            ln = child; break
    if ln is not None:
        spPr.remove(grad)
        spPr.insert(list(spPr).index(ln), grad)
    return s

def add_ellipse(slide, x, y, w, h, fill=None):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        solid_fill(s, fill)
    no_line(s)
    return s

def add_text(slide, x, y, w, h, text, *,
             font=FONT_TEXT, size=14, bold=False, color=None,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             letter_spacing=None, line_spacing=1.15, italic=False):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else text
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = ln
        f = r.font
        f.name = font
        f.size = Pt(size)
        f.bold = bold
        f.italic = italic
        if color is not None:
            f.color.rgb = color
        # letter spacing (spc attr in hundredths of a point)
        if letter_spacing is not None:
            rPr = r._r.get_or_add_rPr()
            rPr.set('spc', str(int(letter_spacing * 100)))
    return tb

# ---------- Layout building blocks ----------

def add_header(slide, T, eyebrow=None, page_num=None, total=40):
    """Top eyebrow with brand and small right-side page counter."""
    if eyebrow:
        add_text(slide, Inches(0.6), Inches(0.35), Inches(10), Inches(0.3),
                 eyebrow.upper(), size=9, bold=True, color=T["ink3"],
                 letter_spacing=2)
    if page_num is not None:
        add_text(slide, Inches(12.0), Inches(0.35), Inches(1.2), Inches(0.3),
                 f"{page_num:02d} — {total:02d}", size=9, bold=False,
                 color=T["ink3"], align=PP_ALIGN.RIGHT, letter_spacing=1)

def add_footer(slide, T, page_num=None):
    add_text(slide, Inches(0.6), Inches(7.05), Inches(8), Inches(0.3),
             "Mobil in Time AG   ·   Strom Quick Dive   ·   Marketing",
             size=8.5, color=T["ink3"], letter_spacing=1)
    if page_num is not None:
        add_text(slide, Inches(12.1), Inches(7.05), Inches(1.1), Inches(0.3),
                 f"{page_num:02d}", size=8.5, color=T["ink3"],
                 align=PP_ALIGN.RIGHT)

def add_divider(slide, T, y, x1=Inches(0.6), x2=Inches(12.73)):
    ln = slide.shapes.add_connector(1, x1, y, x2, y)
    ln.line.color.rgb = T["hairline"]
    ln.line.width = Pt(0.75)

P_NS   = 'http://schemas.openxmlformats.org/presentationml/2006/main'
P14_NS = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
MC_NS  = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
def set_transition(slide, kind="morph"):
    """Add smooth transition. 'morph' or 'fade'."""
    xml = slide._element
    for t in list(xml):
        if etree.QName(t).localname == 'transition':
            xml.remove(t)
    if kind == "morph":
        # Use mc:AlternateContent for the modern morph transition
        alt_xml = f'''<mc:AlternateContent xmlns:mc="{MC_NS}" xmlns:p="{P_NS}" xmlns:p14="{P14_NS}">
          <mc:Choice xmlns:p14="{P14_NS}" Requires="p14">
            <p:transition spd="med" p14:dur="1000">
              <p14:morph option="byObject"/>
            </p:transition>
          </mc:Choice>
          <mc:Fallback>
            <p:transition spd="med">
              <p:fade/>
            </p:transition>
          </mc:Fallback>
        </mc:AlternateContent>'''
        node = etree.fromstring(alt_xml)
        xml.append(node)
    else:
        node = etree.fromstring(f'<p:transition xmlns:p="{P_NS}" spd="med"><p:fade/></p:transition>')
        xml.append(node)

# ---------- SLIDE BUILDERS ----------

def slide_cover(prs, T):
    s = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    add_bg(s, T)
    # Decorative gradient blob top-right
    add_gradient_rect(s, Inches(7.0), Inches(-2.0), Inches(9.0), Inches(9.0),
                      T["grad_from"], T["grad_to"], angle_deg=135, radius=1.0)
    # Overlay tint to soften
    overlay = add_rect(s, Inches(7.0), Inches(-2.0), Inches(9.0), Inches(9.0),
                       fill=T["bg"])
    overlay.fill.transparency = 0  # can't set on solid easily; ignore
    # Instead: reduce blob opacity via alpha on gradFill (complex). Skip.

    # Eyebrow
    add_text(s, Inches(0.7), Inches(0.6), Inches(10), Inches(0.4),
             "MOBIL IN TIME AG   ·   AN AGGREKO COMPANY",
             size=10, bold=True, color=T["ink2"], letter_spacing=3)

    # Big display title
    add_text(s, Inches(0.7), Inches(2.2), Inches(11), Inches(1.6),
             "Strom.",
             font=FONT_DISPLAY, size=140, bold=True, color=T["ink"],
             line_spacing=1.0, letter_spacing=-3)
    add_text(s, Inches(0.7), Inches(3.6), Inches(11), Inches(1.6),
             "Ohne Fachchinesisch.",
             font=FONT_DISPLAY, size=76, bold=True,
             color=T["ink2"], line_spacing=1.0, letter_spacing=-2)

    # Subtitle
    add_text(s, Inches(0.7), Inches(5.4), Inches(9), Inches(0.9),
             "Quick Dive für das Marketing-Team. So erklärt, dass es hängen bleibt — auch ohne Elektro-Ausbildung.",
             size=18, color=T["ink2"], line_spacing=1.35)

    # Presenter card
    add_divider(s, T, Inches(6.55))
    add_text(s, Inches(0.7), Inches(6.7), Inches(6), Inches(0.35),
             "Burak Ücöz", size=13, bold=True, color=T["ink"])
    add_text(s, Inches(0.7), Inches(6.98), Inches(6), Inches(0.35),
             "Sales Engineer Power   ·   22. Juli 2026",
             size=11, color=T["ink2"])
    add_text(s, Inches(11.7), Inches(6.85), Inches(1.5), Inches(0.35),
             "01", size=13, bold=True, color=T["ink2"],
             align=PP_ALIGN.RIGHT)
    set_transition(s, "fade")
    return s

def slide_agenda(prs, T):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    add_header(s, T, "Ablauf", 2)

    add_text(s, Inches(0.6), Inches(0.9), Inches(11), Inches(1.4),
             "Vier Blöcke.\nEine Stunde. Keine Formeln.",
             font=FONT_DISPLAY, size=54, bold=True, color=T["ink"],
             line_spacing=1.05, letter_spacing=-1.5)

    items = [
        ("01", "Grundlagen Strom",              "Die vier Begriffe, die alles erklären", "20 Min"),
        ("02", "Zielgruppen & Einsatzgebiete",  "Wer ruft an und warum",                 "15 Min"),
        ("03", "Anlagentypen & Unterschiede",   "Sechs Bausteine, mehr gibt es nicht",   "20 Min"),
        ("04", "Aufstellung auf der Baustelle", "Was vor Ort wirklich zählt",            "15 Min"),
        ("05", "Was das fürs Marketing heisst", "Wörter, Bilder, Pitch, Fallstricke",    "10 Min"),
    ]
    y = Inches(3.3)
    row_h = Inches(0.65)
    for num, title, sub, dur in items:
        add_divider(s, T, y)
        add_text(s, Inches(0.6), y + Inches(0.13), Inches(0.8), Inches(0.4),
                 num, size=14, bold=True, color=T["accent"], letter_spacing=1)
        add_text(s, Inches(1.5), y + Inches(0.08), Inches(6.5), Inches(0.45),
                 title, size=18, bold=True, color=T["ink"])
        add_text(s, Inches(7.4), y + Inches(0.15), Inches(4.5), Inches(0.4),
                 sub, size=13, color=T["ink2"])
        add_text(s, Inches(11.7), y + Inches(0.15), Inches(1.5), Inches(0.4),
                 dur, size=13, color=T["ink2"], align=PP_ALIGN.RIGHT)
        y += row_h
    add_divider(s, T, y)

    add_text(s, Inches(0.6), Inches(6.75), Inches(12), Inches(0.4),
             "Alles, was tiefer geht, kommt in einen zweiten Termin. Heute geht es um das Fundament.",
             size=12, italic=True, color=T["ink2"])
    add_footer(s, T, 2)
    set_transition(s)
    return s

def slide_quote(prs, T, quote, footnote, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    add_header(s, T, "Kernbotschaft", page)
    # Big quote mark
    add_text(s, Inches(0.6), Inches(1.0), Inches(2), Inches(2.5),
             "“", font=FONT_DISPLAY, size=280, color=T["accent"],
             line_spacing=1.0)
    # Quote
    add_text(s, Inches(0.6), Inches(2.6), Inches(12.2), Inches(3.2),
             quote, font=FONT_DISPLAY, size=44, bold=True,
             color=T["ink"], line_spacing=1.15, letter_spacing=-1)
    add_divider(s, T, Inches(6.05))
    add_text(s, Inches(0.6), Inches(6.2), Inches(12), Inches(0.6),
             footnote, size=14, color=T["ink2"], line_spacing=1.35)
    add_footer(s, T, page)
    set_transition(s)
    return s

def slide_section(prs, T, num, title, sub, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    add_header(s, T, f"Kapitel {num}", page)
    # huge number
    add_text(s, Inches(0.6), Inches(0.8), Inches(6), Inches(4.5),
             num, font=FONT_DISPLAY, size=380, bold=True,
             color=T["ink"], line_spacing=1.0, letter_spacing=-10)
    # accent bar
    bar = add_rect(s, Inches(7.4), Inches(2.6), Inches(0.06), Inches(2.6),
                   fill=T["accent"])
    # Title
    add_text(s, Inches(7.7), Inches(2.5), Inches(5.5), Inches(1.2),
             title, font=FONT_DISPLAY, size=44, bold=True,
             color=T["ink"], line_spacing=1.05, letter_spacing=-1)
    add_text(s, Inches(7.7), Inches(4.0), Inches(5.5), Inches(1.6),
             sub, size=16, color=T["ink2"], line_spacing=1.4)
    add_footer(s, T, page)
    set_transition(s)
    return s

def slide_title_block(slide, T, eyebrow, title, page):
    add_header(slide, T, eyebrow, page)
    add_text(slide, Inches(0.6), Inches(0.9), Inches(12), Inches(1.4),
             title, font=FONT_DISPLAY, size=44, bold=True,
             color=T["ink"], line_spacing=1.05, letter_spacing=-1.2)

def card(slide, T, x, y, w, h, elev=True):
    fill = T["surface"]
    c = add_rect(slide, x, y, w, h, fill=fill, radius=0.045,
                 line_rgb=T["hairline"], line_w=0.75)
    return c

# ---- Slide 5: Grundlagen 1 - Wasser im Rohr ----
def slide_g1_water(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Grundlagen · 1 von 7",
                      "Strom ist wie Wasser im Rohr.", page)
    add_text(s, Inches(0.6), Inches(2.2), Inches(11), Inches(0.6),
             "Drei Begriffe. Ein Bild. Danach klickt es.",
             size=17, color=T["ink2"])

    items = [
        ("Spannung",  "Volt (V)",       "Der Druck im Rohr. Je höher der Druck, desto weiter kommt das Wasser."),
        ("Strom",     "Ampere (A)",     "Wie viel Wasser tatsächlich durch das Rohr fliesst."),
        ("Leistung",  "Watt (W)",       "Was hinten rauskommt und Arbeit macht — Druck mal Durchfluss."),
    ]
    x = Inches(0.6)
    y = Inches(3.2)
    w = Inches(4.05)
    h = Inches(2.6)
    accents = [T["accent"], T["accent2"], T["accent3"]]
    for i,(t,u,d) in enumerate(items):
        cx = x + Inches(i*(4.15))
        card(s, T, cx, y, w, h)
        add_text(s, cx + Inches(0.4), y + Inches(0.35), w - Inches(0.8), Inches(0.3),
                 u.upper(), size=10, bold=True, color=accents[i], letter_spacing=2)
        add_text(s, cx + Inches(0.4), y + Inches(0.75), w - Inches(0.8), Inches(0.6),
                 t, font=FONT_DISPLAY, size=28, bold=True, color=T["ink"],
                 letter_spacing=-0.5)
        add_text(s, cx + Inches(0.4), y + Inches(1.55), w - Inches(0.8), Inches(1.0),
                 d, size=13, color=T["ink2"], line_spacing=1.4)

    # Merksatz strip
    strip_y = Inches(6.05)
    strip = add_rect(s, Inches(0.6), strip_y, Inches(12.15), Inches(0.75),
                     fill=T["surface2"], radius=0.06)
    add_text(s, Inches(0.9), strip_y + Inches(0.19), Inches(2.0), Inches(0.4),
             "Merksatz", size=11, bold=True, color=T["accent"], letter_spacing=2)
    add_text(s, Inches(2.6), strip_y + Inches(0.2), Inches(10), Inches(0.4),
             "Wer 400 V sagt, meint den Druck. Wer 300 kVA sagt, meint die Leistung.",
             size=13, color=T["ink"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 6: Leistung ≠ Energie ----
def slide_g2_power(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Grundlagen · 2 von 7", "Leistung ist nicht Energie.", page)

    # Two big tiles
    for i,(k, name, txt, col) in enumerate([
        ("kW",  "Leistung", "Wie weit der Wasserhahn gerade aufgedreht ist. Eine Momentaufnahme.", T["accent"]),
        ("kWh", "Energie",  "Wie viel Wasser am Ende im Eimer ist. Leistung mal Zeit.", T["accent2"]),
    ]):
        x = Inches(0.6 + i*6.1)
        y = Inches(2.4)
        w = Inches(5.9); h = Inches(2.8)
        card(s, T, x, y, w, h)
        add_text(s, x + Inches(0.5), y + Inches(0.4), Inches(4), Inches(1.4),
                 k, font=FONT_DISPLAY, size=80, bold=True, color=col,
                 line_spacing=1.0, letter_spacing=-2)
        add_text(s, x + Inches(0.5), y + Inches(1.8), Inches(5), Inches(0.5),
                 name, size=16, bold=True, color=T["ink"], letter_spacing=1)
        add_text(s, x + Inches(0.5), y + Inches(2.2), Inches(5), Inches(0.6),
                 txt, size=13, color=T["ink2"], line_spacing=1.4)

    # Example strip
    y2 = Inches(5.4)
    add_text(s, Inches(0.6), y2, Inches(3), Inches(0.35),
             "BEISPIEL ZUM MERKEN", size=10, bold=True,
             color=T["accent"], letter_spacing=3)
    add_text(s, Inches(0.6), y2 + Inches(0.4), Inches(12), Inches(0.5),
             "Ein Haarföhn = 2 kW. Läuft er 1 h → 2 kWh. Läuft er 2 h → 4 kWh.",
             size=17, bold=True, color=T["ink"], line_spacing=1.3)
    add_text(s, Inches(0.6), y2 + Inches(0.95), Inches(12), Inches(0.5),
             "Die Leistung entscheidet, welche Maschine wir hinstellen. Die Energie entscheidet, was der Kunde zahlt.",
             size=13, color=T["ink2"], line_spacing=1.4)
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 7: kVA vs kW - Bierglas ----
def slide_g3_beer(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Grundlagen · 3 von 7", "kVA und kW: das Bierglas.", page)

    # Left: Glass visualization
    gx, gy, gw, gh = Inches(0.9), Inches(2.4), Inches(4.5), Inches(4.2)
    # glass outline
    glass = add_rect(s, gx + Inches(1.3), gy, Inches(2.0), gh, radius=0.15,
                     fill=None, line_rgb=T["hairline"], line_w=1.5)
    # beer (bottom 70%)
    beer = add_rect(s, gx + Inches(1.35), gy + Inches(1.3), Inches(1.9), Inches(2.85),
                    fill=T["warn"])
    # foam (top part)
    foam = add_rect(s, gx + Inches(1.35), gy + Inches(0.05), Inches(1.9), Inches(1.3),
                    fill=T["ink3"] if T["name"]=="dark" else RGBColor(0xE9,0xE9,0xEB))
    # labels + leader lines
    add_text(s, gx, gy + Inches(0.3), Inches(1.25), Inches(0.4),
             "SCHAUM", size=10, bold=True, color=T["ink2"], letter_spacing=2,
             align=PP_ALIGN.RIGHT)
    add_text(s, gx, gy + Inches(0.6), Inches(1.25), Inches(0.35),
             "= kVA", size=13, bold=True, color=T["ink"], align=PP_ALIGN.RIGHT)
    add_text(s, gx + Inches(3.4), gy + Inches(2.5), Inches(1.1), Inches(0.4),
             "BIER", size=10, bold=True, color=T["ink2"], letter_spacing=2)
    add_text(s, gx + Inches(3.4), gy + Inches(2.8), Inches(1.1), Inches(0.35),
             "= kW", size=13, bold=True, color=T["ink"])

    # Right: explanation
    rx = Inches(6.2); rw = Inches(6.6)
    add_text(s, rx, Inches(2.4), rw, Inches(0.4),
             "SCHEINLEISTUNG", size=10, bold=True, color=T["accent"], letter_spacing=2)
    add_text(s, rx, Inches(2.75), rw, Inches(0.6),
             "Das ganze Glas — kVA",
             font=FONT_DISPLAY, size=24, bold=True, color=T["ink"])
    add_text(s, rx, Inches(3.35), rw, Inches(1.0),
             "Bier plus Schaum. So heisst die Zahl auf unseren Maschinen. Der Schaum braucht Platz — macht aber niemanden satt.",
             size=13, color=T["ink2"], line_spacing=1.45)

    add_text(s, rx, Inches(4.55), rw, Inches(0.4),
             "WIRKLEISTUNG", size=10, bold=True, color=T["accent2"], letter_spacing=2)
    add_text(s, rx, Inches(4.9), rw, Inches(0.6),
             "Der trinkbare Teil — kW",
             font=FONT_DISPLAY, size=24, bold=True, color=T["ink"])
    add_text(s, rx, Inches(5.5), rw, Inches(1.0),
             "Was wirklich Arbeit leistet — Kran heben, Licht machen, Server laufen lassen. Das, was der Kunde will.",
             size=13, color=T["ink2"], line_spacing=1.45)

    # bottom formula strip
    strip = add_rect(s, Inches(0.6), Inches(6.5), Inches(12.15), Inches(0.55),
                     fill=T["surface2"], radius=0.08)
    add_text(s, Inches(0.6), Inches(6.6), Inches(12.15), Inches(0.4),
             "kVA × cos φ = kW      ·      Faustregel: 100 kVA Glas ≈ 80 kW Bier",
             size=13, bold=True, color=T["ink"], align=PP_ALIGN.CENTER)
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 8: Drehstrom ----
def slide_g4_three_phase(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Grundlagen · 4 von 7",
                      "Warum es drei Kabel sind. Nicht eines.", page)

    tiles = [
        ("Strom schwingt", "50 Hertz",
         "Er fliesst nicht gerade durch, sondern wechselt 50-mal pro Sekunde die Richtung. Der Herzschlag des Netzes."),
        ("Drei Phasen", "Statt einer",
         "Drei Leitungen, zeitlich versetzt. Wie drei Personen, die abwechselnd in die Pedale treten — nie eine Lücke."),
        ("Schweizer Werte", "400 V · 230 V",
         "400 V zwischen den Phasen für Maschinen und Kräne. 230 V für die Steckdose. Beides aus demselben Kabel."),
    ]
    accents = [T["accent"], T["accent2"], T["accent3"]]
    y = Inches(2.6); h = Inches(3.4); w = Inches(4.05)
    for i,(t, big, d) in enumerate(tiles):
        x = Inches(0.6 + i*4.15)
        card(s, T, x, y, w, h)
        add_text(s, x + Inches(0.4), y + Inches(0.4), Inches(3.5), Inches(0.4),
                 t.upper(), size=10, bold=True, color=accents[i], letter_spacing=2)
        add_text(s, x + Inches(0.4), y + Inches(0.85), w - Inches(0.8), Inches(1.2),
                 big, font=FONT_DISPLAY, size=42, bold=True,
                 color=T["ink"], line_spacing=1.0, letter_spacing=-1.5)
        add_text(s, x + Inches(0.4), y + Inches(2.2), w - Inches(0.8), Inches(1.1),
                 d, size=13, color=T["ink2"], line_spacing=1.45)

    add_text(s, Inches(0.6), Inches(6.35), Inches(12), Inches(0.4),
             "Für euch reicht: Drehstrom ist der Normalfall bei allem, was wir vermieten. «400 V» heisst genau das.",
             size=12, italic=True, color=T["ink2"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 9: Netz vs Insel ----
def slide_g5_grid(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Grundlagen · 5 von 7", "Am Netz — oder auf der Insel.", page)

    for i,(title, sub, body, img, col) in enumerate([
        ("Netzbetrieb", "Der Rhein",
         "Der Strom kommt vom EW. Das Netz ist riesig und träge. Springt eine grosse Maschine an, merkt es das Netz kaum.",
         "🌊", T["accent"]),
        ("Inselbetrieb", "Der Gartenteich",
         "Unser Generator ist das Kraftwerk. Er macht Spannung und Frequenz selbst. Jede Last spürt er sofort.",
         "◐",  T["accent2"]),
    ]):
        x = Inches(0.6 + i*6.1); y = Inches(2.5)
        w = Inches(5.9); h = Inches(3.5)
        card(s, T, x, y, w, h)
        add_text(s, x + Inches(0.5), y + Inches(0.4), Inches(4.5), Inches(0.4),
                 title.upper(), size=10, bold=True, color=col, letter_spacing=2)
        add_text(s, x + Inches(0.5), y + Inches(0.85), Inches(5), Inches(0.7),
                 title, font=FONT_DISPLAY, size=32, bold=True, color=T["ink"], letter_spacing=-0.8)
        add_text(s, x + Inches(0.5), y + Inches(1.7), Inches(5), Inches(0.45),
                 f"Bild: {sub}.", size=13, italic=True, color=T["ink2"])
        add_text(s, x + Inches(0.5), y + Inches(2.2), w - Inches(1), Inches(1.2),
                 body, size=14, color=T["ink2"], line_spacing=1.45)

    add_text(s, Inches(0.6), Inches(6.3), Inches(12), Inches(0.6),
             "Deshalb ist unsere Arbeit anspruchsvoller als «Maschine hinstellen»: Auf der Insel muss die Anlage zur Last passen.",
             size=13, italic=True, color=T["ink2"], line_spacing=1.4)
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 10: Sauberer / schmutziger Strom ----
def slide_g6_clean(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Grundlagen · 6 von 7",
                      "Sauberer Strom. Schmutziger Strom.", page)

    add_text(s, Inches(0.6), Inches(2.3), Inches(12), Inches(1.0),
             "Aus dem Wasserhahn kann klares Wasser kommen — oder Brühe mit Sand. Beides ist Wasser. Nur eines brauchbar. Beim Strom sieht man es dem Kabel nicht an.",
             size=15, color=T["ink2"], line_spacing=1.4)

    # Two columns
    x1 = Inches(0.6); x2 = Inches(6.7); y = Inches(3.85); w = Inches(6.05); h = Inches(2.4)
    card(s, T, x1, y, w, h)
    add_text(s, x1 + Inches(0.4), y + Inches(0.35), Inches(3), Inches(0.4),
             "SAUBER HEISST", size=10, bold=True, color=T["accent3"], letter_spacing=2)
    for i, line_txt in enumerate([
        "Spannung bleibt stabil",
        "Schwingung hat eine saubere Form",
        "Frequenz stimmt und wackelt nicht",
    ]):
        add_text(s, x1 + Inches(0.4), y + Inches(0.85 + i*0.4), Inches(5.2), Inches(0.4),
                 f"·   {line_txt}", size=14, color=T["ink"])

    card(s, T, x2, y, w, h)
    add_text(s, x2 + Inches(0.4), y + Inches(0.35), Inches(3), Inches(0.4),
             "SCHMUTZIG HEISST", size=10, bold=True, color=T["warn"], letter_spacing=2)
    for i, line_txt in enumerate([
        "Steuerungen steigen ohne Grund aus",
        "Motoren werden heiss und halten kürzer",
        "Server starten neu, LED flackert, Audio brummt",
    ]):
        add_text(s, x2 + Inches(0.4), y + Inches(0.85 + i*0.4), Inches(5.4), Inches(0.4),
                 f"·   {line_txt}", size=14, color=T["ink"])

    # Norms strip
    y3 = Inches(6.5)
    add_text(s, Inches(0.6), y3, Inches(12), Inches(0.45),
             "EN 50160 sagt, welche Qualität das Netz liefern muss.     IEC 61000-4-30 Klasse A sagt, wie man richtig misst.",
             size=12, color=T["ink2"], align=PP_ALIGN.LEFT)
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 11: Differenzierung ----
def slide_g7_differentiation(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Das unterscheidet uns", "", page)
    add_text(s, Inches(0.6), Inches(1.5), Inches(12), Inches(2.4),
             "Jeder kann einen Generator hinstellen.\nWir beweisen schwarz auf weiss, dass der Strom sauber war.",
             font=FONT_DISPLAY, size=42, bold=True, color=T["ink"],
             line_spacing=1.1, letter_spacing=-1.2)

    tiles = [
        ("Messgerät der höchsten Klasse",
         "Zertifiziert vom eidgenössischen Institut für Metrologie. Kein Bastelgerät."),
        ("Immer dabei, nie ein Aufpreis",
         "Bei jedem Stromauftrag Standard. Nicht als Option, die man wegverhandelt."),
        ("Ein Bericht, den man vorzeigen kann",
         "Ein Dokument für Auditor, Versicherung oder Geschäftsleitung."),
    ]
    y = Inches(4.5); h = Inches(1.85); w = Inches(4.05)
    for i,(t, d) in enumerate(tiles):
        x = Inches(0.6 + i*4.15)
        card(s, T, x, y, w, h)
        # small number
        add_text(s, x + Inches(0.4), y + Inches(0.3), Inches(0.6), Inches(0.4),
                 f"0{i+1}", size=10, bold=True, color=T["accent"], letter_spacing=2)
        add_text(s, x + Inches(0.4), y + Inches(0.65), w - Inches(0.8), Inches(0.7),
                 t, size=15, bold=True, color=T["ink"], line_spacing=1.2)
        add_text(s, x + Inches(0.4), y + Inches(1.15), w - Inches(0.8), Inches(0.7),
                 d, size=11.5, color=T["ink2"], line_spacing=1.4)

    add_text(s, Inches(0.6), Inches(6.6), Inches(12), Inches(0.4),
             "Kein anderer mobiler Stromvermieter in der Schweiz bietet das im Standardumfang. Unser stärkstes Argument.",
             size=12, italic=True, color=T["accent"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 13: 3 Gründe ----
def slide_z1_reasons(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Zielgruppen · 1 von 5",
                      "Es gibt nur drei Gründe für einen Anruf.", page)
    items = [
        ("1", "Es gibt hier gar keinen Strom",
         "Baustelle auf der grünen Wiese, Festival auf der Alp, Tunnel, abgelegene Anlage. Keine Steckdose da.",
         T["accent"]),
        ("2", "Es gibt zu wenig Strom",
         "Der Anschluss reicht nicht: Umbau, zusätzliche Maschine, Spitzenlast im Winter, Erweiterung.",
         T["accent2"]),
        ("3", "Der Strom darf nie ausfallen",
         "Spital, Rechenzentrum, laufende Produktion. Hier geht es um Existenzsicherung.",
         T["accent3"]),
    ]
    y = Inches(2.6); h = Inches(3.5); w = Inches(4.05)
    for i,(num,t,d,col) in enumerate(items):
        x = Inches(0.6 + i*4.15)
        card(s, T, x, y, w, h)
        add_text(s, x + Inches(0.5), y + Inches(0.4), Inches(2), Inches(1.4),
                 num, font=FONT_DISPLAY, size=90, bold=True, color=col,
                 line_spacing=1.0, letter_spacing=-3)
        add_text(s, x + Inches(0.5), y + Inches(1.75), w - Inches(1), Inches(0.9),
                 t, font=FONT_DISPLAY, size=19, bold=True, color=T["ink"],
                 line_spacing=1.15)
        add_text(s, x + Inches(0.5), y + Inches(2.7), w - Inches(1), Inches(0.9),
                 d, size=12.5, color=T["ink2"], line_spacing=1.45)

    add_text(s, Inches(0.6), Inches(6.4), Inches(12), Inches(0.4),
             "Grund 1 und 2 sind Termindruck. Grund 3 ist Angst. Beides verkauft — aber man spricht anders darüber.",
             size=13, italic=True, color=T["ink2"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 14: Wer ruft an ----
def slide_z2_who(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Zielgruppen · 2 von 5", "Wer bei uns anruft.", page)
    tiles = [
        ("Bau & Infrastruktur", "Baustrom, Kran, Trocknung, Beleuchtung"),
        ("Events & Festivals", "Bühne, Licht, Ton, Gastronomie, Camping"),
        ("Industrie & Produktion", "Umbau, Wartung, Spitzenlast, Ausfallschutz"),
        ("Rechenzentren & Telecom", "Test vor Inbetriebnahme, Überbrückung, Wartung"),
        ("Spitäler & kritische Infrastruktur", "Gesetzlich vorgeschriebene Notversorgung"),
        ("Städte, Gemeinden, EVU", "Netzarbeiten, Anlässe, Blackout-Vorsorge"),
    ]
    y = Inches(2.4); w = Inches(4.05); h = Inches(1.85); gap = Inches(0.15)
    for idx,(t, d) in enumerate(tiles):
        col = idx % 3; row = idx // 3
        x = Inches(0.6) + col*(w + gap)
        yy = y + row*(h + gap)
        card(s, T, x, yy, w, h)
        # small dot
        add_ellipse(s, x + Inches(0.4), yy + Inches(0.4), Inches(0.18), Inches(0.18),
                    fill=T["accent"])
        add_text(s, x + Inches(0.4), yy + Inches(0.75), w - Inches(0.8), Inches(0.55),
                 t, size=15, bold=True, color=T["ink"], line_spacing=1.15)
        add_text(s, x + Inches(0.4), yy + Inches(1.3), w - Inches(0.8), Inches(0.5),
                 d, size=12, color=T["ink2"], line_spacing=1.4)

    add_text(s, Inches(0.6), Inches(6.5), Inches(12), Inches(0.4),
             "Dazu der wichtigste Kanal überhaupt: unsere eigenen Wärme- und Kältekunden. Gleich mehr.",
             size=12, italic=True, color=T["accent"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 15: Nachts wach ----
def slide_z3_nightmare(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Zielgruppen · 3 von 5",
                      "Was den Kunden nachts wach hält.", page)

    rows = [
        ("Baustelle",     "Kran steht still, Termin platzt, Vertragsstrafe droht", "Am Montag um sieben läuft alles."),
        ("Festival",      "Die Bühne fällt aus, 20 000 Leute im Dunkeln",           "Kritische Zonen bekommen ihre eigene Maschine."),
        ("Industrie",     "Produktion steht, jede Stunde kostet fünfstellig",       "Umschaltung ohne Produktionsstopp."),
        ("Rechenzentrum", "Server fallen aus, Kundenverträge werden gebrochen",     "Keine einzige Millisekunde Lücke."),
        ("Spital",        "Gesetzliche Pflicht, Behörde und Haftung im Nacken",     "Prüfung normkonform und dokumentiert."),
    ]
    # Header row
    y = Inches(2.6)
    add_text(s, Inches(0.6), y, Inches(2.2), Inches(0.35),
             "WER", size=10, bold=True, color=T["ink3"], letter_spacing=2)
    add_text(s, Inches(3.0), y, Inches(5.5), Inches(0.35),
             "SEIN ALBTRAUM", size=10, bold=True, color=T["ink3"], letter_spacing=2)
    add_text(s, Inches(8.8), y, Inches(4.4), Inches(0.35),
             "UNSERE ANTWORT", size=10, bold=True, color=T["accent"], letter_spacing=2)
    y += Inches(0.4)
    row_h = Inches(0.7)
    for i,(who, pain, ans) in enumerate(rows):
        add_divider(s, T, y)
        yy = y + Inches(0.18)
        add_text(s, Inches(0.6), yy, Inches(2.2), Inches(0.5),
                 who, size=14, bold=True, color=T["ink"])
        add_text(s, Inches(3.0), yy + Inches(0.02), Inches(5.5), Inches(0.5),
                 pain, size=12.5, color=T["ink2"], line_spacing=1.35)
        add_text(s, Inches(8.8), yy + Inches(0.02), Inches(4.4), Inches(0.5),
                 ans, size=12.5, bold=True, color=T["accent"], line_spacing=1.35)
        y += row_h
    add_divider(s, T, y)

    add_text(s, Inches(0.6), Inches(6.55), Inches(12), Inches(0.4),
             "Reihenfolge in jedem Text: erst den Schmerz benennen, dann die Lösung. Nie umgekehrt.",
             size=12, italic=True, color=T["ink2"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 16: Grössenordnungen ----
def slide_z4_sizes(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Zielgruppen · 4 von 5", "Grössenordnungen zum Anfassen.", page)
    items = [
        ("17 kVA",     "Ein Einfamilienhaus"),
        ("60 kVA",     "Kleine Baustelle, Marktareal, Quartierfest"),
        ("300 kVA",    "Baustelle mit Kran und Bautrocknung"),
        ("1 000 kVA",  "Grosses Open-Air-Areal"),
        ("6 000 kVA",  "Belastungstest eines Rechenzentrums"),
    ]
    y = Inches(2.6); row_h = Inches(0.72)
    add_divider(s, T, y)
    y += Inches(0.05)
    for i,(size, desc) in enumerate(items):
        yy = y + Inches(0.15)
        # progress bar
        max_bar = Inches(6.0)
        # log-ish scale for visual
        import math
        vals = [17, 60, 300, 1000, 6000]
        rel = math.log(vals[i]) / math.log(6000)
        bw = Inches(0.5 + rel * 5.5)
        bar_bg = add_rect(s, Inches(6.9), yy + Inches(0.18), max_bar, Inches(0.18),
                          fill=T["surface2"], radius=0.5)
        bar_fg = add_rect(s, Inches(6.9), yy + Inches(0.18), bw, Inches(0.18),
                          fill=T["accent"], radius=0.5)
        add_text(s, Inches(0.6), yy, Inches(3), Inches(0.55),
                 size, font=FONT_DISPLAY, size=26, bold=True, color=T["ink"],
                 letter_spacing=-0.5)
        add_text(s, Inches(3.7), yy + Inches(0.12), Inches(3.1), Inches(0.4),
                 desc, size=13, color=T["ink2"])
        y += row_h
        add_divider(s, T, y)

    add_text(s, Inches(0.6), Inches(6.55), Inches(12), Inches(0.4),
             "Grobe Faustzahlen für ein Gefühl. Nicht für ein Angebot. Die richtige Grösse rechnet immer ein Ingenieur.",
             size=12, italic=True, color=T["warn"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 17: Bestandskunden ----
def slide_z5_existing(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Zielgruppen · 5 von 5",
                      "Der günstigste Kunde ist der, den wir schon haben.", page)
    for i,(t, d, col) in enumerate([
        ("Was wir schon haben",
         "Hunderte Kunden vertrauen uns bei Wärme und Kälte. Sie kennen unsere Leute und wissen: Wir liefern, wenn es eilt.",
         T["accent"]),
        ("Was daraus wird",
         "Jeder dieser Kunden ist ein warmer Kontakt für Strom. Kein Kaltanruf. Kein Vertrauensaufbau von null. Keine neue Freigabe.",
         T["accent2"]),
    ]):
        x = Inches(0.6 + i*6.1); y = Inches(2.5); w = Inches(5.9); h = Inches(2.6)
        card(s, T, x, y, w, h)
        add_text(s, x + Inches(0.5), y + Inches(0.4), Inches(3), Inches(0.4),
                 f"0{i+1}", size=10, bold=True, color=col, letter_spacing=2)
        add_text(s, x + Inches(0.5), y + Inches(0.8), w - Inches(1), Inches(0.7),
                 t, font=FONT_DISPLAY, size=24, bold=True, color=T["ink"])
        add_text(s, x + Inches(0.5), y + Inches(1.5), w - Inches(1), Inches(1.4),
                 d, size=13, color=T["ink2"], line_spacing=1.5)

    # Quote strip
    q_y = Inches(5.4)
    strip = add_rect(s, Inches(0.6), q_y, Inches(12.15), Inches(1.35),
                     fill=T["surface2"], radius=0.05)
    add_text(s, Inches(0.9), q_y + Inches(0.15), Inches(1.5), Inches(0.4),
             "DER SATZ", size=10, bold=True, color=T["accent"], letter_spacing=2)
    add_text(s, Inches(0.9), q_y + Inches(0.5), Inches(11.5), Inches(0.9),
             "«Ihr kennt uns für Wärme und Kälte. Jetzt gibt es auch den Strom dazu. Eine Nummer, ein Ansprechpartner, eine Rechnung.»",
             font=FONT_DISPLAY, size=18, bold=True, color=T["ink"], italic=True, line_spacing=1.3)
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 19: 6 Bausteine Überblick ----
def slide_a_overview(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Anlagentypen · Überblick",
                      "Sechs Bausteine. Mehr gibt es nicht.", page)
    tiles = [
        ("Generator",        "Kraftwerk auf Rädern",   T["accent"]),
        ("Batteriespeicher", "Riesige Powerbank",      T["accent3"]),
        ("Hybrid",           "Beides kombiniert",      T["accent2"]),
        ("USV",              "Der Fallschirm",         T["warn"]),
        ("Transformator",    "Der Übersetzer",         T["accent"]),
        ("Verteilung & Kabel","Die Steckdosenleiste",  T["accent2"]),
    ]
    y = Inches(2.5); w = Inches(4.05); h = Inches(1.85); gap = Inches(0.15)
    for idx,(t, sub, col) in enumerate(tiles):
        c = idx % 3; r = idx // 3
        x = Inches(0.6) + c*(w + gap)
        yy = y + r*(h + gap)
        card(s, T, x, yy, w, h)
        # accent chip
        chip = add_rect(s, x + Inches(0.4), yy + Inches(0.4), Inches(0.35), Inches(0.35),
                        fill=col, radius=0.5)
        add_text(s, x + Inches(0.85), yy + Inches(0.42), Inches(2), Inches(0.4),
                 f"0{idx+1}", size=11, bold=True, color=T["ink2"], letter_spacing=1)
        add_text(s, x + Inches(0.4), yy + Inches(0.9), w - Inches(0.8), Inches(0.55),
                 t, font=FONT_DISPLAY, size=20, bold=True, color=T["ink"])
        add_text(s, x + Inches(0.4), yy + Inches(1.35), w - Inches(0.8), Inches(0.4),
                 sub, size=13, color=T["ink2"])

    add_text(s, Inches(0.6), Inches(6.55), Inches(12), Inches(0.4),
             "Plus ein Sonderfall: die Lastbank. Am Ende dieses Blocks.",
             size=12, italic=True, color=T["ink2"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Anlagentyp Detail Template ----
def slide_anlage_detail(prs, T, page, eyebrow, title, lead, blocks, footnote):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, eyebrow, title, page)
    add_text(s, Inches(0.6), Inches(2.2), Inches(12), Inches(0.9),
             lead, size=16, color=T["ink2"], line_spacing=1.4, italic=True)

    accents = [T["accent"], T["accent2"], T["accent3"], T["warn"]]
    y = Inches(3.5); w = Inches(2.95); h = Inches(2.7); gap = Inches(0.1)
    for i,(t, d) in enumerate(blocks[:4]):
        x = Inches(0.6) + i*(w + gap)
        card(s, T, x, y, w, h)
        add_ellipse(s, x + Inches(0.35), y + Inches(0.4), Inches(0.22), Inches(0.22),
                    fill=accents[i])
        add_text(s, x + Inches(0.35), y + Inches(0.8), w - Inches(0.7), Inches(0.5),
                 t, size=13, bold=True, color=T["ink"], line_spacing=1.2)
        add_text(s, x + Inches(0.35), y + Inches(1.3), w - Inches(0.7), Inches(1.35),
                 d, size=11.5, color=T["ink2"], line_spacing=1.45)

    if footnote:
        add_text(s, Inches(0.6), Inches(6.5), Inches(12), Inches(0.4),
                 footnote, size=12, italic=True, color=T["accent"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 27: Wann was ----
def slide_a_summary(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Anlagentypen · Zusammenfassung", "Wann was: die Kurzfassung.", page)

    rows = [
        ("Strom über Wochen, egal wo",             "Generator",         T["accent"]),
        ("Tagsüber Vollgas, nachts still",         "Hybrid",            T["accent2"]),
        ("Kurz, leise, drinnen oder im Wohngebiet","Batteriespeicher",  T["accent3"]),
        ("Keine einzige Millisekunde Lücke",       "USV",               T["warn"]),
        ("Die Spannung passt nicht zusammen",      "Transformator",     T["accent"]),
        ("Anlage testen, bevor sie scharf geht",   "Lastbank",          T["accent2"]),
    ]
    y = Inches(2.6); row_h = Inches(0.62)
    add_divider(s, T, y)
    for i,(cond, ans, col) in enumerate(rows):
        yy = y + Inches(0.15)
        add_text(s, Inches(0.6), yy, Inches(7.5), Inches(0.45),
                 cond, size=15, color=T["ink"])
        arrow = add_rect(s, Inches(8.2), yy + Inches(0.18), Inches(0.6), Inches(0.03),
                         fill=T["hairline"])
        add_text(s, Inches(9.0), yy, Inches(4), Inches(0.45),
                 ans, size=15, bold=True, color=col)
        y += row_h
        add_divider(s, T, y)

    add_text(s, Inches(0.6), Inches(6.55), Inches(12), Inches(0.4),
             "In der Praxis ist es fast immer eine Kombination. Genau das ist unsere Arbeit.",
             size=12, italic=True, color=T["ink2"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 29: 6 Fragen ----
def slide_b1_questions(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Baustelle · 1 von 5", "Sechs Fragen vor jeder Aufstellung.", page)

    items = [
        ("Kommt der Lastwagen hin?",  "Zufahrt, Engstellen, Torbreite, Tragfähigkeit. Kran nötig?"),
        ("Hält der Boden?",           "Ein grosses Aggregat wiegt Tonnen. Kein Schlamm, kein Rasen, keine Tiefgarage."),
        ("Ist genug Platz?",          "Nicht nur die Maschine — rundherum Platz für Arbeit und freie Luft."),
        ("Wie weit zum Verbraucher?", "Der Kabelweg. Je länger, desto teurer, desto dicker. Immer in Metern."),
        ("Wer ist der Nachbar?",      "Lärm und Abgase. Wohnhaus in 20 m verändert die ganze Lösung."),
        ("Wo steht der Tank?",        "Menge, Auffangwanne, Zufahrt für den Tankwagen, Abstand zu Gewässern."),
    ]
    y = Inches(2.5); w = Inches(4.05); h = Inches(1.85); gap = Inches(0.15)
    for i,(t, d) in enumerate(items):
        col = i % 3; row = i // 3
        x = Inches(0.6) + col*(w + gap)
        yy = y + row*(h + gap)
        card(s, T, x, yy, w, h)
        add_text(s, x + Inches(0.4), yy + Inches(0.35), Inches(1), Inches(0.4),
                 f"0{i+1}", size=11, bold=True, color=T["accent"], letter_spacing=1)
        add_text(s, x + Inches(0.4), yy + Inches(0.75), w - Inches(0.8), Inches(0.55),
                 t, size=15, bold=True, color=T["ink"], line_spacing=1.15)
        add_text(s, x + Inches(0.4), yy + Inches(1.3), w - Inches(0.8), Inches(0.5),
                 d, size=11.5, color=T["ink2"], line_spacing=1.4)

    add_text(s, Inches(0.6), Inches(6.55), Inches(12), Inches(0.4),
             "Zwei Minuten am Telefon. Ganze Tage später gespart.",
             size=12, italic=True, color=T["accent"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 30: Lärm & Abgase ----
def slide_b2_noise(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Baustelle · 2 von 5", "Lärm und Abgase — die häufigsten Stolpersteine.", page)

    for i,(t, val, subval, body, norm, col) in enumerate([
        ("Lärm", "≈ 70 dB", "in 7 m Abstand",
         "Ein modernes gekapseltes Aggregat — etwa wie ein Staubsauger im Nebenzimmer. Doppelter Abstand = deutlich leiser.",
         "Lärmschutz-Verordnung (LSV)", T["accent"]),
        ("Abgase", "Stage V", "strengste Stufe",
         "In Städten, bei öffentlichen Bauherren und in Wohnquartieren zunehmend Pflicht. Wer nicht liefert, ist draussen.",
         "Luftreinhalte-Verordnung (LRV)", T["accent2"]),
    ]):
        x = Inches(0.6 + i*6.1); y = Inches(2.4); w = Inches(5.9); h = Inches(3.5)
        card(s, T, x, y, w, h)
        add_text(s, x + Inches(0.5), y + Inches(0.35), Inches(3), Inches(0.4),
                 t.upper(), size=10, bold=True, color=col, letter_spacing=2)
        add_text(s, x + Inches(0.5), y + Inches(0.75), Inches(4), Inches(1.3),
                 val, font=FONT_DISPLAY, size=60, bold=True, color=T["ink"],
                 line_spacing=1.0, letter_spacing=-2)
        add_text(s, x + Inches(0.5), y + Inches(2.0), Inches(4), Inches(0.4),
                 subval, size=13, italic=True, color=T["ink2"])
        add_text(s, x + Inches(0.5), y + Inches(2.4), w - Inches(1), Inches(0.9),
                 body, size=12.5, color=T["ink2"], line_spacing=1.4)
        add_text(s, x + Inches(0.5), y + Inches(3.05), Inches(5), Inches(0.35),
                 "Regelwerk:  " + norm, size=10.5, color=T["ink3"])

    add_text(s, Inches(0.6), Inches(6.15), Inches(12), Inches(0.65),
             "«72 dB» sagt nichts. «72 dB in 7 m» ist eine Aussage. Ohne Abstand keine Zahl.",
             size=13, italic=True, color=T["warn"], line_spacing=1.4)
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 31: Treibstoff ----
def slide_b3_fuel(prs, T, page):
    return slide_anlage_detail(prs, T, page,
        "Baustelle · 3 von 5", "Treibstoff — mehr Regelwerk als erwartet.",
        "Tanks sind doppelwandig, Überfüllsicherung, Auffangwanne. Kein Extra — Gesetz.",
        [
            ("Doppelwandig & aufgefangen", "Doppelwandiger Tank, Überfüllsicherung, Auffangwanne. Nicht optional."),
            ("Gewässerschutz ist ernst",   "Bei Ölunfall haftet auch die Person vor Ort persönlich — nicht nur die Firma."),
            ("Autonomie planen",           "Wie viele Stunden ohne Nachtanken? Daraus ergibt sich Tankgrösse und Rhythmus."),
            ("Für Marketing",              "Tankservice und Gewässerschutz sind ein Verkaufsargument. Kunde kümmert sich um nichts."),
        ],
        None)

# ---- Slide 32: Sicherheit ----
def slide_b4_safety(prs, T, page):
    return slide_anlage_detail(prs, T, page,
        "Baustelle · 4 von 5", "Sicherheit auf dem Platz.", "",
        [
            ("Absperrung",     "Niemand steht ungeschützt neben der Anlage. Heisse Teile, drehende Teile, Spannung."),
            ("Feuerlöscher",   "Griffbereit, geprüft, für jeden erreichbar. Fluchtwege bleiben frei."),
            ("Erdung",         "Verbindung in den Boden. Im Fehlerfall löst der Schutzschalter aus — nicht ein Mensch."),
            ("Nur Fachpersonal","Anschluss und Inbetriebnahme immer durch ausgebildete Fachperson."),
        ],
        "Bei Fotos für Social Media prüfen: Absperrung sichtbar, Helm auf, keine offenen Schaltschränke im Bild.")

# ---- Slide 33: Ablauf ----
def slide_b5_flow(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Baustelle · 5 von 5", "So läuft ein Auftrag ab.", page)

    steps = [
        ("Anfrage",     "Kunde meldet sich, Eckdaten erfasst"),
        ("Klärung",     "Rückfragen, oft ein Vor-Ort-Termin"),
        ("Auslegung",   "Ingenieur rechnet, Offerte geht raus"),
        ("Anlieferung", "Transport, Aufstellung, Inbetriebnahme"),
        ("Betrieb",     "Service, Tankung, Überwachung"),
        ("Rückbau",     "Abholung und Bericht zur Netzqualität"),
    ]
    y = Inches(3.0)
    step_w = Inches(2.0); gap = Inches(0.05)
    total_w = 6*step_w + 5*gap
    start_x = Inches(0.6) + (Inches(12.15) - total_w) / 2

    # baseline
    ln = s.shapes.add_connector(1, start_x + Inches(0.6), y + Inches(0.4),
                                 start_x + total_w - Inches(0.6), y + Inches(0.4))
    ln.line.color.rgb = T["hairline"]
    ln.line.width = Pt(1)

    for i,(t, d) in enumerate(steps):
        x = start_x + i*(step_w + gap)
        # circle with number
        c = add_ellipse(s, x + step_w/2 - Inches(0.35), y + Inches(0.05),
                        Inches(0.7), Inches(0.7), fill=T["accent"])
        add_text(s, x + step_w/2 - Inches(0.35), y + Inches(0.14),
                 Inches(0.7), Inches(0.5),
                 str(i+1), font=FONT_DISPLAY, size=22, bold=True,
                 color=RGBColor(0xFF,0xFF,0xFF), align=PP_ALIGN.CENTER)
        add_text(s, x, y + Inches(1.0), step_w, Inches(0.4),
                 t, size=14, bold=True, color=T["ink"], align=PP_ALIGN.CENTER)
        add_text(s, x, y + Inches(1.4), step_w, Inches(1.0),
                 d, size=11, color=T["ink2"], align=PP_ALIGN.CENTER, line_spacing=1.35)

    add_text(s, Inches(0.6), Inches(6.2), Inches(12), Inches(0.7),
             "Zwischen Anfrage und Anlieferung: Tage bis Wochen. Notfälle gehen schneller — kosten mehr.",
             size=13, italic=True, color=T["ink2"], line_spacing=1.4)
    add_text(s, Inches(0.6), Inches(6.6), Inches(12), Inches(0.4),
             "Bitte nie am Telefon einen Termin zusagen.",
             size=12, italic=True, color=T["warn"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 35: Wörter ----
def slide_m1_words(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Marketing · 1 von 5",
                      "Wörter, die funktionieren — und Wörter, die schaden.", page)

    good = [
        "Versorgungssicherheit",
        "Kein Produktionsstopp",
        "Planbar und dokumentiert",
        "Leise, emissionsarm, HVO",
        "Aus einer Hand",
        "Kurzfristig verfügbar",
        "Nachweis der Netzqualität",
    ]
    bad = [
        "Günstig, billig, Schnäppchen",
        "Weltmarktführer, Superlative",
        "«Notstrom» (klingt nach Panik)",
        "Lösungen ohne Bild dahinter",
        "Abkürzungen ohne Erklärung",
        "Zahlen ohne Bezugsgrösse",
    ]

    for i,(title, items, col, symbol) in enumerate([
        ("VERWENDEN", good, T["accent3"], "✓"),
        ("VERMEIDEN", bad,  T["warn"],    "✕"),
    ]):
        x = Inches(0.6 + i*6.1); y = Inches(2.4); w = Inches(5.9); h = Inches(3.9)
        card(s, T, x, y, w, h)
        add_text(s, x + Inches(0.5), y + Inches(0.35), Inches(3), Inches(0.4),
                 title, size=10, bold=True, color=col, letter_spacing=2)
        for j, it in enumerate(items):
            row_y = y + Inches(0.9 + j*0.42)
            add_text(s, x + Inches(0.5), row_y, Inches(0.4), Inches(0.35),
                     symbol, size=14, bold=True, color=col)
            add_text(s, x + Inches(0.85), row_y, w - Inches(1.3), Inches(0.35),
                     it, size=13, color=T["ink"])

    add_text(s, Inches(0.6), Inches(6.5), Inches(12), Inches(0.4),
             "Schweizer Kunden reagieren auf Superlative mit Misstrauen. Understatement mit Belegen wirkt stärker.",
             size=12, italic=True, color=T["ink2"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 36: Bilder ----
def slide_m2_images(prs, T, page):
    return slide_anlage_detail(prs, T, page,
        "Marketing · 2 von 5", "Bildsprache — was funktioniert.", "",
        [
            ("Zeigt das",             "Maschinen im echten Einsatz. Umgebung drumherum. Menschen im Bild. Kabelwege, Verteiler, Baustelle bei Nacht mit Licht."),
            ("Zeigt das nicht",       "Freigestellte Maschinen auf Weiss. Stockfotos mit Glühbirnen. Steckdosen-Klischees. Blitze im Himmel."),
            ("Freigabe zuerst",       "Vor jeder Veröffentlichung. Ohne Ausnahme, auch bei harmlosen Bildern. Sicherheitsstandorte: oft Fotoverbot."),
            ("Echt schlägt perfekt",  "Ein echtes Baustellenbild schlägt jedes Stockfoto. Auch wenn es weniger perfekt aussieht."),
        ],
        None)

# ---- Slide 37: Fünf Sätze ----
def slide_m3_sentences(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Marketing · 3 von 5", "Fünf Sätze, die immer stimmen.", page)

    sents = [
        "Wir vermieten mobile Stromversorgung — von der Baustellensteckdose bis zum Megawatt.",
        "Alles aus einer Hand: Wärme, Kälte und Strom. Ein Ansprechpartner, eine Nummer.",
        "Wir liefern nicht nur Strom — wir weisen nach, dass er sauber war.",
        "Die Aggreko-Flotte im Rücken, ein Schweizer Team davor.",
        "Wenn es schnell gehen muss, geht es schnell.",
    ]
    y = Inches(2.6); row_h = Inches(0.72)
    add_divider(s, T, y)
    for i, sent in enumerate(sents):
        yy = y + Inches(0.18)
        add_text(s, Inches(0.6), yy, Inches(0.8), Inches(0.4),
                 f"0{i+1}", size=12, bold=True, color=T["accent"], letter_spacing=1)
        # Highlight sentence 3
        col = T["accent"] if i == 2 else T["ink"]
        bold = i == 2
        add_text(s, Inches(1.5), yy - Inches(0.02), Inches(11.5), Inches(0.6),
                 sent, size=17, bold=bold, color=col, line_spacing=1.3)
        y += row_h
        add_divider(s, T, y)

    add_text(s, Inches(0.6), Inches(6.55), Inches(12), Inches(0.4),
             "Satz 03 kann kein Wettbewerber in der Schweiz sagen. Gehört in jeden längeren Text.",
             size=12, italic=True, color=T["accent"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 38: 5 Fragen ----
def slide_m4_questions(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    slide_title_block(s, T, "Marketing · 4 von 5", "Die fünf Fragen, die euch gestellt werden.", page)

    items = [
        ("«Was kostet so ein Generator?»",         "Kommt auf Leistung, Dauer und Ort an. Diese drei Angaben sammeln — weitergeben."),
        ("«Habt ihr das morgen verfügbar?»",       "Prüft immer die Disposition. Nie selbst zusagen — auch nicht ungefähr."),
        ("«Ist das nicht sehr laut?»",              "Moderne Anlagen sind gekapselt und mit Abstand unproblematisch. Zahl aus dem Datenblatt."),
        ("«Ist das umweltfreundlich?»",             "Mit HVO und Hybrid deutlich, ja. Konkrete Zahlen liefert das Projektteam mit Zertifikat."),
        ("«Wie gross muss die Anlage sein?»",       "Rechnet ein Ingenieur anhand einer Lastliste. Niemals schätzen. Auch nicht als Hausnummer."),
    ]
    y = Inches(2.55); row_h = Inches(0.7)
    add_divider(s, T, y)
    for q, a in items:
        yy = y + Inches(0.14)
        add_text(s, Inches(0.6), yy, Inches(5.5), Inches(0.5),
                 q, size=14, bold=True, color=T["ink"])
        add_text(s, Inches(6.4), yy + Inches(0.03), Inches(6.8), Inches(0.55),
                 a, size=12.5, color=T["ink2"], line_spacing=1.4)
        y += row_h
        add_divider(s, T, y)

    add_text(s, Inches(0.6), Inches(6.5), Inches(12), Inches(0.4),
             "Goldene Regel: Im Zweifel keine Zahl nennen. Eine sauber weitergegebene Frage schlägt jede falsche Antwort.",
             size=12, italic=True, color=T["warn"])
    add_footer(s, T, page)
    set_transition(s)
    return s

# ---- Slide 39: Was ich brauche ----
def slide_m5_asks(prs, T, page):
    return slide_anlage_detail(prs, T, page,
        "Marketing · 5 von 5", "Was ich konkret von euch brauche.", "",
        [
            ("Bestandskunden-Kampagne", "Alle Wärme- und Kältekunden für eine Strom-Ansprache aufbereiten. Schnellster Weg zu den ersten Aufträgen."),
            ("Zwei Referenzstories",    "Eine Baustelle, ein Event. Mit echten Bildern, echten Zahlen und Freigabe des Kunden."),
            ("Einheitliche Sprache",    "Begriffe aus diesem Termin in allen Kanälen gleich verwenden. Wortliste kommt von mir."),
            ("Kurze Gegenlesung",       "Zwei Minuten Blick auf jeden Text mit technischem Inhalt. Spart uns Korrekturen danach."),
        ],
        "Wenn wir das aufgleisen: bis Herbst eine Strom-Kommunikation, die sitzt.")

# ---- Slide 40: Danke / Ausblick ----
def slide_thanks(prs, T, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, T)
    # Gradient bar left
    add_gradient_rect(s, Inches(-2), Inches(-1), Inches(8), Inches(9),
                      T["grad_from"], T["grad_to"], angle_deg=135, radius=0.5)

    add_text(s, Inches(0.7), Inches(0.6), Inches(6), Inches(0.4),
             "DANKE", size=11, bold=True,
             color=RGBColor(0xFF,0xFF,0xFF), letter_spacing=4)

    add_text(s, Inches(0.7), Inches(2.4), Inches(6), Inches(2),
             "Fragen?\nImmer her damit.",
             font=FONT_DISPLAY, size=64, bold=True,
             color=RGBColor(0xFF,0xFF,0xFF), line_spacing=1.05, letter_spacing=-2)

    add_text(s, Inches(0.7), Inches(5.4), Inches(6), Inches(1.2),
             "Es gibt keine dumme Frage zu Strom.\nNur Texte, die falsch werden, weil niemand gefragt hat.",
             size=15, color=RGBColor(0xFF,0xFF,0xFF), line_spacing=1.45)

    add_text(s, Inches(0.7), Inches(6.85), Inches(6), Inches(0.4),
             "Burak Ücöz   ·   Sales Engineer Power   ·   Mobil in Time AG",
             size=11, color=RGBColor(0xFF,0xFF,0xFF), letter_spacing=1)

    # Right column: Vorschlag zweiter Termin
    rx = Inches(7.5); rw = Inches(5.3)
    add_text(s, rx, Inches(0.6), rw, Inches(0.4),
             "VORSCHLAG · ZWEITER TERMIN",
             size=10, bold=True, color=T["accent"], letter_spacing=3)
    add_text(s, rx, Inches(1.05), rw, Inches(1.0),
             "Was als Nächstes kommt.",
             font=FONT_DISPLAY, size=32, bold=True, color=T["ink"], letter_spacing=-1)

    topics = [
        "Netzqualität im Detail und was wir damit verkaufen",
        "Nachhaltigkeit: HVO, Hybrid und die Zahlen dahinter",
        "Rechenzentren als Wachstumsmarkt Schweiz",
        "Referenzprojekte zum Anfassen: Gampel, Baustellen, Industrie",
    ]
    y = Inches(2.6); row_h = Inches(0.85)
    add_divider(s, T, y, x1=rx, x2=rx+rw)
    for i, t in enumerate(topics):
        yy = y + Inches(0.2)
        add_text(s, rx, yy, Inches(0.6), Inches(0.4),
                 f"0{i+1}", size=12, bold=True, color=T["accent"])
        add_text(s, rx + Inches(0.7), yy - Inches(0.02), rw - Inches(0.7), Inches(0.6),
                 t, size=14, color=T["ink"], line_spacing=1.3)
        y += row_h
        add_divider(s, T, y, x1=rx, x2=rx+rw)

    add_text(s, rx, Inches(6.85), rw, Inches(0.35),
             "40 / 40   ·   Ende der Session",
             size=10, color=T["ink3"], letter_spacing=2)
    set_transition(s, "fade")
    return s

# ============= BUILD =============

def build_deck(T, out_path):
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    p = 1
    slide_cover(prs, T);                                            # 1
    slide_agenda(prs, T);                                            # 2
    slide_quote(prs, T,
        "«Wir vermieten keine Maschinen.\nWir vermieten die Garantie, dass nichts stehen bleibt.»",
        "Wenn ihr aus dieser Stunde nur einen Satz mitnehmt — dann diesen. Alles Weitere ist Technik, die diesen Satz belegt.",
        3)
    slide_section(prs, T, "01", "Grundlagen Strom",
        "Vier Begriffe. Ein Bild. Danach versteht ihr jede Kundenanfrage.", 4)
    slide_g1_water(prs, T, 5)
    slide_g2_power(prs, T, 6)
    slide_g3_beer(prs, T, 7)
    slide_g4_three_phase(prs, T, 8)
    slide_g5_grid(prs, T, 9)
    slide_g6_clean(prs, T, 10)
    slide_g7_differentiation(prs, T, 11)

    slide_section(prs, T, "02", "Zielgruppen & Einsatzgebiete",
        "Wer bei uns anruft, warum er anruft und was ihn nachts wach hält.", 12)
    slide_z1_reasons(prs, T, 13)
    slide_z2_who(prs, T, 14)
    slide_z3_nightmare(prs, T, 15)
    slide_z4_sizes(prs, T, 16)
    slide_z5_existing(prs, T, 17)

    slide_section(prs, T, "03", "Anlagentypen & Unterschiede",
        "Sechs Bausteine. Mehr gibt es nicht. Jeder hat genau eine Aufgabe.", 18)
    slide_a_overview(prs, T, 19)
    slide_anlage_detail(prs, T, 20,
        "Anlagentypen · 1 von 7", "Generator — das Kraftwerk auf Rädern.",
        "Ein Dieselmotor treibt einen Stromerzeuger an. Rein Treibstoff, raus Strom.",
        [
            ("Wofür",           "Über Stunden, Wochen, Monate. Das Arbeitspferd — rund 80 % unserer Aufträge."),
            ("Was zu wissen ist","Braucht Treibstoff, macht Geräusch, macht Abgase, braucht Platz und Zufahrt."),
            ("Stage V",         "Strengste EU-Abgasnorm für solche Motoren. In Städten zunehmend Pflicht."),
            ("HVO",             "Treibstoff aus Rest- und Abfallstoffen statt Erdöl. Gleiche Leistung, deutlich weniger CO₂."),
        ],
        "Stage V betrifft den Motor. HVO den Treibstoff. Beides zusammen ist die sauberste Variante.")
    slide_anlage_detail(prs, T, 21,
        "Anlagentypen · 2 von 7", "Batteriespeicher — die riesige Powerbank.",
        "Ein grosser Akku im Container. Wird geladen, gibt Strom ab. Fachbegriff: BESS.",
        [
            ("Stärken",     "Absolut leise, keine Abgase, keine Vibration. Reagiert in Millisekunden."),
            ("Die Grenze",  "Er hat ein Ende. Ist er leer, ist er leer. Für tagelangen Dauerbetrieb allein nicht wirtschaftlich."),
            ("Wofür",       "Nachtbetrieb, Innenräume, kurze Überbrückung, Abfangen von Lastspitzen."),
            ("Für Texte",   "Unsere sichtbarste Nachhaltigkeitsgeschichte. Leise und emissionsfrei versteht jeder."),
        ],
        "Ehrlich bleiben: Batterie ersetzt keinen Generator über Wochen. Wer das behauptet, wird zerlegt.")
    slide_anlage_detail(prs, T, 22,
        "Anlagentypen · 3 von 7", "Hybrid — das Beste aus beidem.",
        "Generator und Batterie arbeiten zusammen. Sie teilen sich die Schicht.",
        [
            ("Wie es funktioniert","Batterie übernimmt die ruhigen Stunden. Wird mehr gebraucht, springt der Generator an und lädt gleich mit."),
            ("Das Ergebnis",       "Weniger Motorlaufstunden, weniger Treibstoff, weniger Abgase. Nachts ist es still."),
            ("Typischer Einsatz",  "Baustellen im Wohngebiet, Festivals mit Nachtruhe, Projekte mit Öko-Auflagen."),
            ("Für Texte",          "Unsere beste Nachhaltigkeitsstory — mit echten Zahlen dahinter, nicht nur grüner Farbe."),
        ],
        "Wenn eine Ausschreibung von Lärm- oder CO₂-Auflagen spricht: Hybrid ist fast immer die Antwort.")
    slide_anlage_detail(prs, T, 23,
        "Anlagentypen · 4 von 7", "USV — der Fallschirm.",
        "Ein Generator braucht 10–15 s zum Hochlaufen. Für einen Server ist das eine Ewigkeit.",
        [
            ("Was sie macht", "Hängt dauerhaft zwischen Netz und Verbraucher. Überbrückt völlig unterbrechungsfrei. Null Lücke."),
            ("Das Bild",      "Ein Fallschirm. Immer dabei, meistens nutzlos. An dem einen Tag ist er alles."),
            ("Wofür",         "Rechenzentren, Serverräume, medizinische Geräte, Steuerungen — überall wo Neustart teuer ist."),
            ("Für Texte",     "Nicht über die Technik schreiben — über die Folge: kein Datenverlust, kein Produktionsabbruch."),
        ], None)
    slide_anlage_detail(prs, T, 24,
        "Anlagentypen · 5 von 7", "Transformator — der Übersetzer.",
        "Das Netz liefert Mittelspannung, z.B. 16 000 V. Maschinen wollen 400 V. Der Trafo übersetzt.",
        [
            ("Wie er arbeitet",   "Keine Elektronik, keine beweglichen Teile. Nur Kupfer und Eisen. Extrem zuverlässig."),
            ("Wofür",             "Grosse Baustellen, Industrieareale, Rechenzentren, Netzarbeiten — überall wo Mittelspannung anliegt."),
            ("Warum wichtig",     "Ohne Trafo kein Zugang zu grossen Leistungen. Ab ~1 MW geht praktisch nichts ohne."),
            ("Für Texte",         "Unspektakulär, aber mit Hebelwirkung. Nicht ins Zentrum stellen — nie vergessen zu erwähnen."),
        ],
        "Achtung: Mittelspannung ist Lebensgefahr. Daran arbeitet ausschliesslich speziell ausgebildetes Personal.")
    slide_anlage_detail(prs, T, 25,
        "Anlagentypen · 6 von 7", "Verteilung & Kabel — die Steckdosenleiste.",
        "Aus einem dicken Kabel werden viele kleine. Verteiler, Kabel, Steckverbindungen.",
        [
            ("Klingt banal",    "Ist es nicht. Der Kabelweg entscheidet oft über Preis und Machbarkeit."),
            ("Kostentreiber",   "200 m Kabel können mehr kosten als der halbe Generator. Je länger, desto dicker."),
            ("Die eine Frage",  "Wie weit ist es vom Aufstellort bis zum Verbraucher? Diese Antwort spart uns Stunden."),
            ("Für Texte",       "Der unsichtbare Teil unserer Leistung. In Referenzstories sichtbar machen."),
        ], None)
    slide_anlage_detail(prs, T, 26,
        "Anlagentypen · 7 von 7", "Lastbank — der Hometrainer.",
        "Eine Maschine, die Strom in Wärme umwandelt. Sie tut so, als wäre sie ein echter Verbraucher.",
        [
            ("Wofür",              "Notstromanlage oder neues Rechenzentrum unter Volllast testen — bevor echte Kunden dranhängen."),
            ("Zweiter Zweck",      "Generatoren, die zu wenig zu tun haben, verrussen. Die Lastbank hält sie gesund."),
            ("Warum wichtig",      "Unser Türöffner in den Rechenzentrumsmarkt. Wer den Test macht, ist beim nächsten Projekt schon im Haus."),
            ("Für Texte",          "Erklärungsbedürftig. Am besten über die Frage: Woher weisst du, dass dein Notstrom wirklich funktioniert?"),
        ], None)
    slide_a_summary(prs, T, 27)

    slide_section(prs, T, "04", "Aufstellung auf der Baustelle",
        "Wo die Maschine steht, entscheidet über Kosten, Termin und Bewilligung.", 28)
    slide_b1_questions(prs, T, 29)
    slide_b2_noise(prs, T, 30)
    slide_b3_fuel(prs, T, 31)
    slide_b4_safety(prs, T, 32)
    slide_b5_flow(prs, T, 33)

    slide_section(prs, T, "05", "Was das fürs Marketing heisst",
        "Wörter, Bilder, Pitch — und die Fallen, in die man nur einmal tritt.", 34)
    slide_m1_words(prs, T, 35)
    slide_m2_images(prs, T, 36)
    slide_m3_sentences(prs, T, 37)
    slide_m4_questions(prs, T, 38)
    slide_m5_asks(prs, T, 39)

    slide_thanks(prs, T, 40)

    prs.save(out_path)
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    build_deck(LIGHT, "/tmp/claude-0/-home-user-Burak/4a218ee5-c0dd-540b-a282-84fbba805c45/scratchpad/MiT_Strom_QuickDive_Apple_Light.pptx")
    build_deck(DARK,  "/tmp/claude-0/-home-user-Burak/4a218ee5-c0dd-540b-a282-84fbba805c45/scratchpad/MiT_Strom_QuickDive_Apple_Dark.pptx")
