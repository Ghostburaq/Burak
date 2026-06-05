"""
AVIA VOLT — Pitch-Deck Generator (Bewerbung Vertriebsmanager · Burak Ücöz)

Rebuilds the 10-slide pitch deck slide-by-slide with a refined, fully
consistent design system (dark navy + AVIA red), tasteful generated imagery
and concise German speaker notes ("nur für dich"). 100% deterministic,
no external dependencies at render time.

Run:  python3 src/make_assets.py && python3 src/build_deck.py
Out:  Pitch_Burak_AVIA_VOLT.pptx
"""
from __future__ import annotations

import os
from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICO = os.path.join(ROOT, "assets", "icons_w")
BG = os.path.join(ROOT, "assets", "bg")

# ---- Palette -------------------------------------------------------------
INK = RGBColor(0x1B, 0x24, 0x30)
INK_SOFT = RGBColor(0x2A, 0x35, 0x43)
RED = RGBColor(0xE2, 0x00, 0x1A)
RED_DK = RGBColor(0xB3, 0x00, 0x15)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
CARD_DK = RGBColor(0x22, 0x2E, 0x3C)
INK_TXT = RGBColor(0x1B, 0x24, 0x30)
MUTE = RGBColor(0x5A, 0x65, 0x73)
MUTE_LT = RGBColor(0x93, 0xA0, 0xAE)
LINE_LT = RGBColor(0xE3, 0xE8, 0xED)
LINE_DK = RGBColor(0x3A, 0x46, 0x54)

HEAD = "Trebuchet MS"
BODY = "Calibri"

# ---- Geometry ------------------------------------------------------------
EMU_W, EMU_H = 12161520, 6858000
SW, SH = 13.3, 7.5  # working inches (≈ exact)
MX = 0.72           # outer margin


def IN(v):  # inches -> Emu
    return Emu(int(v * 914400))


# ==========================================================================
#  Low-level helpers
# ==========================================================================
def _no_shadow(shape):
    shape.shadow.inherit = False


def _soft_shadow(shape, blur=0.09, dist=0.05, alpha=78, color="1B2430"):
    """Inject a subtle outer drop shadow for card depth."""
    sp = shape._element.spPr
    for tag in ("a:effectLst",):
        ex = sp.find(qn(tag))
        if ex is not None:
            sp.remove(ex)
    eff = sp.makeelement(qn("a:effectLst"), {})
    sh = eff.makeelement(qn("a:outerShdw"), {
        "blurRad": str(int(blur * 914400)),
        "dist": str(int(dist * 914400)),
        "dir": "5400000", "rotWithShape": "0",
    })
    clr = sh.makeelement(qn("a:srgbClr"), {"val": color})
    a = clr.makeelement(qn("a:alpha"), {"val": str(alpha * 1000)})
    clr.append(a)
    sh.append(clr)
    eff.append(sh)
    sp.append(eff)


def add_bg(slide, name):
    slide.shapes.add_picture(os.path.join(BG, name), 0, 0,
                             Emu(EMU_W), Emu(EMU_H))


def rect(slide, x, y, w, h, fill=None, line=None, line_w=0.75,
         radius=None, shadow=False):
    shp = MSO_SHAPE.ROUNDED_RECTANGLE if radius is not None else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shp, IN(x), IN(y), IN(w), IN(h))
    _no_shadow(s)
    if radius is not None:
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(line_w)
    if shadow:
        _soft_shadow(s)
    return s


def oval(slide, x, y, d, fill, line=None, line_w=1.0):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, IN(x), IN(y), IN(d), IN(d))
    _no_shadow(s)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(line_w)
    return s


def _set_run(r, t, *, sz, color, b=False, i=False, font=BODY, spc=0):
    r.text = t
    f = r.font
    f.name = font; f.size = Pt(sz); f.bold = b; f.italic = i
    f.color.rgb = color
    rPr = r._r.get_or_add_rPr()
    rPr.set(qn("a:spc") if False else "spc", str(int(spc * 100)))
    # ensure complex-script + east-asian use same face
    for tag in ("a:latin", "a:cs"):
        e = rPr.find(qn(tag))
        if e is None:
            e = rPr.makeelement(qn(tag), {}); rPr.append(e)
        e.set("typeface", font)


def text(slide, x, y, w, h, paras, *, anchor="t", wrap=True):
    """paras: list of paragraphs.
       Each paragraph: {'runs':[{...run kwargs incl 't'}],
                        'align','space_after','space_before','line'}"""
    tb = slide.shapes.add_textbox(IN(x), IN(y), IN(w), IN(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE,
                          "b": MSO_ANCHOR.BOTTOM}[anchor]
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    for idx, p in enumerate(paras):
        para = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER,
                          "r": PP_ALIGN.RIGHT}[p.get("align", "l")]
        if "space_after" in p:
            para.space_after = Pt(p["space_after"])
        if "space_before" in p:
            para.space_before = Pt(p["space_before"])
        if "line" in p:
            para.line_spacing = p["line"]
        for rk in p["runs"]:
            rk = dict(rk); t = rk.pop("t")
            _set_run(para.add_run(), t, **rk)
    return tb


def icon(slide, path, x, y, sz):
    slide.shapes.add_picture(os.path.join(ICO, path), IN(x), IN(y), IN(sz), IN(sz))


def badge(slide, cx, cy, d, fill, icon_name, ratio=0.5, line=None):
    oval(slide, cx - d / 2, cy - d / 2, d, fill, line=line, line_w=1.25)
    isz = d * ratio
    icon(slide, f"{icon_name}.png", cx - isz / 2, cy - isz / 2, isz)


# ---- Shared chrome -------------------------------------------------------
def kicker(slide, x, y, label, dark=False):
    rect(slide, x, y + 0.02, 0.34, 0.075, fill=RED)
    text(slide, x + 0.46, y - 0.085, 8.0, 0.34,
         [{"runs": [{"t": label, "sz": 12.5, "color": RED, "b": True,
                     "font": HEAD, "spc": 2.6}]}])


def headline(slide, x, y, w, runs, dark=False):
    text(slide, x, y, w, 1.5,
         [{"runs": runs, "line": 1.04}])


def footer(slide, page, dark=False):
    col = MUTE_LT if dark else MUTE
    line_col = LINE_DK if dark else LINE_LT
    rect(slide, MX, 7.02, SW - 2 * MX, 0.014, fill=line_col)
    text(slide, MX, 7.12, 8.5, 0.3,
         [{"runs": [{"t": "Burak Ücöz", "sz": 9.5, "color": col, "b": True,
                     "font": HEAD, "spc": 0.6},
                    {"t": "   ·   Bewerbung AVIA VOLT Suisse", "sz": 9.5,
                     "color": col, "font": BODY, "spc": 0.6}]}])
    rect(slide, SW - MX - 0.52, 7.16, 0.1, 0.1, fill=RED)
    text(slide, SW - MX - 0.40, 7.10, 0.40, 0.3,
         [{"runs": [{"t": f"{page:02d}", "sz": 11, "color": col, "b": True,
                     "font": HEAD}], "align": "r"}])


def notes(slide, txt):
    slide.notes_slide.notes_text_frame.text = txt


# ==========================================================================
#  Deck
# ==========================================================================
prs = Presentation()
prs.slide_width = Emu(EMU_W)
prs.slide_height = Emu(EMU_H)
BLANK = prs.slide_layouts[6]


def new(bg):
    s = prs.slides.add_slide(BLANK)
    add_bg(s, bg)
    return s


# ---------- SLIDE 1 · Titel ----------
def slide1():
    s = new("hero.png")
    kicker(s, MX, 0.78, "BEWERBUNG · VERTRIEBSMANAGER")
    text(s, MX + 0.46, 1.12, 7.5, 0.4,
         [{"runs": [{"t": "AVIA VOLT Suisse — Frauenfeld", "sz": 13,
                     "color": MUTE_LT, "font": BODY, "spc": 1.0}]}])

    headline(s, MX, 2.35, 8.1, [
        {"t": "Ich erkläre Ladeinfrastruktur nicht.\n", "sz": 35,
         "color": WHITE, "b": True, "font": HEAD},
    ])
    text(s, MX, 3.18, 8.1, 0.9,
         [{"runs": [
             {"t": "Ich ", "sz": 35, "color": WHITE, "b": True, "font": HEAD},
             {"t": "verkaufe", "sz": 35, "color": RED, "b": True, "font": HEAD},
             {"t": " sie.", "sz": 35, "color": WHITE, "b": True, "font": HEAD},
         ]}])

    # red rule
    rect(s, MX + 0.02, 4.22, 1.6, 0.04, fill=RED)

    text(s, MX, 4.55, 7.6, 0.5,
         [{"runs": [{"t": "Burak Ücöz", "sz": 21, "color": WHITE, "b": True,
                     "font": HEAD, "spc": 0.5}]}])
    text(s, MX, 5.06, 7.7, 0.7,
         [{"runs": [{"t": "Vertriebsingenieur · EMV & Power Quality · 10+ Jahre "
                          "technischer B2B-Vertrieb in der Schweiz",
                     "sz": 12.5, "color": MUTE_LT, "font": BODY}], "line": 1.25}])

    # contact row
    cy = 6.35
    for i, (ic, tx) in enumerate([
            ("phone", "+41 79 512 98 07"),
            ("mail", "b.s.uecoez@gmail.com"),
            ("pin", "8240 Thayngen")]):
        bx = MX + 0.20 + i * 2.7
        badge(s, bx, cy, 0.40, RED, ic, ratio=0.5)
        text(s, bx + 0.30, cy - 0.16, 2.4, 0.34,
             [{"runs": [{"t": tx, "sz": 11.5, "color": WHITE, "font": BODY}]}],
             anchor="m")

    # portrait, framed with red accent
    px, py, pd = 9.95, 2.15, 2.75
    rect(s, px - 0.13, py + 0.16, pd, pd, fill=RED, radius=0.10)
    pic = s.shapes.add_picture(os.path.join(ROOT, "assets", "portrait_clean.png"),
                               IN(px), IN(py), IN(pd), IN(pd))
    _soft_shadow(pic, blur=0.14, dist=0.07, alpha=60)
    notes(s,
          "Selbstbewusst öffnen. Nach 'Ich verkaufe sie.' eine kurze Pause — "
          "das ist die Kernbotschaft: Technik UND Abschluss. Namen frei nennen, "
          "nicht ablesen. Ziel der ersten 15 Sekunden: klarmachen, dass ich "
          "beides verbinde. Ruhig und nicht zu schnell.")
    return s


# ---------- SLIDE 2 · Euer Auftrag ----------
def slide2():
    s = new("paper.png")
    kicker(s, MX, 0.72, "EUER AUFTRAG")
    headline(s, MX, 1.06, 11.0, [
        {"t": "Das ist kein Nischenprodukt mehr. ", "sz": 27, "color": INK_TXT,
         "b": True, "font": HEAD},
        {"t": "Das ist Infrastruktur.", "sz": 27, "color": RED, "b": True,
         "font": HEAD}])
    text(s, MX, 1.74, 11.6, 0.8,
         [{"runs": [{"t": "Infrastruktur verkauft niemand, der sie nur erklären "
                          "kann. Ihr sucht jemanden, der die Technik versteht und "
                          "trotzdem abschliesst — genau diese seltene Kombination "
                          "bringe ich mit.", "sz": 13, "color": MUTE,
                     "font": BODY}], "line": 1.3}])

    cards = [
        ("charger", "DC-Schnelllader",
         "Technisch anspruchsvolle Anlagen — Netzanschluss, Leistung, Power Quality."),
        ("handshake", "CPO-Betrieb",
         "Aus Ladepunkten ein tragfähiges Geschäftsmodell machen."),
        ("battery", "Batteriespeicher",
         "Lastspitzen kappen, Netzanschluss entlasten, Wirtschaftlichkeit sichern."),
        ("bolt", "Lastmanagement",
         "Keine Kür, sondern die Voraussetzung für skalierbare Standorte."),
    ]
    cw, gap = 2.79, 0.30
    cx0 = MX
    cy, ch = 3.02, 2.98
    for i, (ic, ttl, body) in enumerate(cards):
        x = cx0 + i * (cw + gap)
        rect(s, x, cy, cw, ch, fill=CARD, line=LINE_LT, radius=0.06, shadow=True)
        rect(s, x, cy, cw, 0.09, fill=RED, radius=0.0)
        badge(s, x + 0.62, cy + 0.78, 0.86, INK, ic, ratio=0.5)
        text(s, x + 0.26, cy + 1.36, cw - 0.5, 0.5,
             [{"runs": [{"t": ttl, "sz": 14.5, "color": INK_TXT, "b": True,
                         "font": HEAD}]}])
        text(s, x + 0.26, cy + 1.86, cw - 0.5, 1.5,
             [{"runs": [{"t": body, "sz": 11, "color": MUTE, "font": BODY}],
               "line": 1.22}])
    footer(s, 2)
    notes(s,
          "Zeigen, dass ich die Stelle verstanden habe. Die vier Felder kurz "
          "antippen, NICHT vorlesen. Kernsatz betonen: 'Infrastruktur verkauft "
          "niemand, der sie nur erklären kann.' Danach Brücke zu Slide 3 — "
          "warum genau ich diese Kombination mitbringe.")
    return s


# ---------- SLIDE 3 · Warum ich ----------
def slide3():
    s = new("paper.png")
    kicker(s, MX, 0.72, "WARUM ICH")
    headline(s, MX, 1.06, 11.0, [
        {"t": "Drei Dinge, die ", "sz": 27, "color": INK_TXT, "b": True,
         "font": HEAD},
        {"t": "selten zusammenkommen.", "sz": 27, "color": RED, "b": True,
         "font": HEAD}])

    items = [
        ("01", "chip", "Technische Tiefe",
         "Dipl.-Ingenieur Elektrotechnik (B.Eng.), EMV- und Power-Quality-Experte. "
         "Ich verstehe, was an einem 360-kW-Lader wirklich passiert — und erkläre "
         "es einem Entscheider in einem Satz."),
        ("02", "handshake", "Verkaufs-Biss",
         "Über 10 Jahre Investitionsgüter-Vertrieb im Aussendienst: "
         "Neukundengewinnung, Key Accounts, Angebot, Verhandlung, Abschluss. "
         "Als Unternehmer selbst Kundenstämme von 200+ aufgebaut."),
        ("03", "bolt", "Energie & Speicher",
         "Batteriespeicher, Lastmanagement, Smart Grid und E-Mobility sind mein "
         "Tagesgeschäft, nicht meine Lernkurve. Ich bin am Tag eins einsatzbereit."),
    ]
    cw, gap = 3.78, 0.33
    cy, ch = 2.42, 3.70
    for i, (num, ic, ttl, body) in enumerate(items):
        x = MX + i * (cw + gap)
        rect(s, x, cy, cw, ch, fill=CARD, line=LINE_LT, radius=0.05, shadow=True)
        text(s, x + 0.32, cy + 0.26, 1.6, 0.9,
             [{"runs": [{"t": num, "sz": 38, "color": LINE_LT, "b": True,
                         "font": HEAD}]}])
        badge(s, x + cw - 0.78, cy + 0.66, 0.80, RED, ic, ratio=0.5)
        rect(s, x + 0.34, cy + 1.30, 0.7, 0.045, fill=RED)
        text(s, x + 0.34, cy + 1.48, cw - 0.66, 0.5,
             [{"runs": [{"t": ttl, "sz": 16, "color": INK_TXT, "b": True,
                         "font": HEAD}]}])
        text(s, x + 0.34, cy + 2.04, cw - 0.66, 1.9,
             [{"runs": [{"t": body, "sz": 11.5, "color": MUTE, "font": BODY}],
               "line": 1.28}])
    footer(s, 3)
    notes(s,
          "Mein roter Faden: Technik – Vertrieb – Energie. Bei '200+ "
          "Kundenstamm' kurz innehalten, das ist der Abschluss-Beweis. Tempo: "
          "ein Punkt = ein Atemzug. Nicht alle Details vorlesen, die Überschriften "
          "führen.")
    return s


# ---------- SLIDE 4 · Anforderung trifft Beweis ----------
def slide4():
    s = new("paper.png")
    kicker(s, MX, 0.66, "ANFORDERUNG TRIFFT BEWEIS")
    headline(s, MX, 1.00, 11.0, [
        {"t": "Was ihr sucht — ", "sz": 26, "color": INK_TXT, "b": True,
         "font": HEAD},
        {"t": "und womit ich es belege.", "sz": 26, "color": RED, "b": True,
         "font": HEAD}])

    rows = [
        ("DC-Ladeinfrastruktur, technisch anspruchsvoll",
         "Elektrotechnik-Ingenieur mit EMV/PQ-Tiefe — Netzanschluss, "
         "Oberschwingungen, Leistung."),
        ("CPO-Betrieb als Geschäftsmodell",
         "10+ Jahre Investitionsgüter-Vertrieb: Pipeline, Forecast, Marge, "
         "Abschluss."),
        ("Batteriespeicher",
         "Aktiv im Verkauf von Speicher- und Hybridlösungen, inkl. "
         "Pufferbatterien an HPC-Standorten."),
        ("Energie- und Lastmanagement",
         "Tagesgeschäft: Lastspitzen, Lastmanagement, Energiemonitoring."),
        ("Technischer Verkauf, Freude am Kundenkontakt",
         "Aussendienst pur — Neukundengewinnung, Beratung von Planung bis "
         "Inbetriebnahme."),
        ("Standort Frauenfeld, 100 %",
         "Wohnhaft in Thayngen, rund 30 Minuten entfernt. Lokal verankert in der "
         "Ostschweiz."),
    ]
    tx, ty, tw = MX, 1.92, SW - 2 * MX
    colA = 4.9
    # header band
    rect(s, tx, ty, tw, 0.46, fill=INK, radius=0.04)
    text(s, tx + 0.55, ty + 0.045, colA, 0.36,
         [{"runs": [{"t": "AVIA VOLT sucht", "sz": 12, "color": MUTE_LT,
                     "b": True, "font": HEAD, "spc": 1.6}]}], anchor="m")
    text(s, tx + colA + 0.55, ty + 0.045, tw - colA - 0.8, 0.36,
         [{"runs": [{"t": "BURAK ÜCÖZ BRINGT", "sz": 12, "color": WHITE,
                     "b": True, "font": HEAD, "spc": 1.6}]}], anchor="m")

    rh = 0.715
    y = ty + 0.46
    for i, (req, proof) in enumerate(rows):
        if i % 2 == 1:
            rect(s, tx, y, tw, rh, fill=RGBColor(0xF2, 0xF5, 0xF8))
        badge(s, tx + 0.30, y + rh / 2, 0.34, RED, "check", ratio=0.52)
        text(s, tx + 0.58, y, colA - 0.2, rh,
             [{"runs": [{"t": req, "sz": 12, "color": INK_TXT, "b": True,
                         "font": HEAD}], "line": 1.1}], anchor="m")
        # divider
        rect(s, tx + colA + 0.32, y + 0.12, 0.014, rh - 0.24, fill=LINE_LT)
        text(s, tx + colA + 0.55, y, tw - colA - 0.78, rh,
             [{"runs": [{"t": proof, "sz": 11, "color": MUTE, "font": BODY}],
               "line": 1.12}], anchor="m")
        y += rh
    rect(s, tx, ty, tw, 0.46 + rh * 6, line=LINE_LT, radius=0.0)
    footer(s, 4)
    notes(s,
          "Die Beweis-Slide. Links Anforderung, rechts mein Beleg. NICHT alle "
          "vorlesen — 2 bis 3 stärkste herausgreifen: DC-/EMV-Tiefe, "
          "Batteriespeicher, Standort 30 Minuten. Jedes Häkchen heisst: erfüllt. "
          "Souverän durchgehen, das Format spricht für sich.")
    return s


# ---------- SLIDE 5 · Track Record (dunkel) ----------
def slide5():
    s = new("section.png")
    kicker(s, MX, 0.85, "TRACK RECORD", dark=True)
    headline(s, MX, 1.22, 11.0, [
        {"t": "Substanz, ", "sz": 30, "color": WHITE, "b": True, "font": HEAD},
        {"t": "keine Versprechen.", "sz": 30, "color": RED, "b": True,
         "font": HEAD}])

    stats = [
        ("10+", "Jahre B2B-Vertrieb technischer Investitionsgüter"),
        ("26", "Kantone Marktüberblick — die Schweiz als Ganzes gedacht"),
        ("899", "Key Accounts in eigener CRM-Datenbank aufgebaut"),
        ("4", "Sprachen: Deutsch, Französisch, Englisch, Türkisch"),
    ]
    cw, gap = 2.79, 0.30
    cy, ch = 2.55, 2.45
    for i, (big, lab) in enumerate(stats):
        x = MX + i * (cw + gap)
        rect(s, x, cy, cw, ch, fill=CARD_DK, line=LINE_DK, radius=0.06, shadow=True)
        rect(s, x + 0.32, cy + 0.34, 0.55, 0.05, fill=RED)
        text(s, x + 0.28, cy + 0.46, cw - 0.5, 1.1,
             [{"runs": [{"t": big, "sz": 50, "color": WHITE, "b": True,
                         "font": HEAD}]}])
        text(s, x + 0.30, cy + 1.52, cw - 0.56, 0.9,
             [{"runs": [{"t": lab, "sz": 11.5, "color": MUTE_LT, "font": BODY}],
               "line": 1.24}])
    text(s, MX, 5.45, SW - 2 * MX, 0.6,
         [{"runs": [{"t": "Vom Erstkontakt bis zur Inbetriebnahme — ", "sz": 15,
                     "color": MUTE_LT, "font": BODY},
                    {"t": "ein Ansprechpartner, durchgehend.", "sz": 15,
                     "color": WHITE, "b": True, "font": HEAD}]}], anchor="m")
    footer(s, 5, dark=True)
    notes(s,
          "Zahlen wirken lassen — nach jeder eine kurze Pause. 899 Key Accounts "
          "ist der Wow-Wert, hier kurz stehen bleiben. Schlusszeile betonen: ein "
          "Ansprechpartner vom Erstkontakt bis zur Inbetriebnahme. Nichts "
          "relativieren, die Substanz spricht.")
    return s


# ---------- SLIDE 6 · Unfairer Vorteil ----------
def slide6():
    s = new("paper.png")
    kicker(s, MX, 0.72, "MEIN UNFAIRER VORTEIL")
    headline(s, MX, 1.06, 11.5, [
        {"t": "Schnelllader belasten das Netz. ", "sz": 26, "color": INK_TXT,
         "b": True, "font": HEAD},
        {"t": "Ich spreche ihre Sprache.", "sz": 26, "color": RED, "b": True,
         "font": HEAD}])
    text(s, MX, 1.74, 11.7, 0.9,
         [{"runs": [{"t": "Jeder HPC-Lader zieht hohe Leistung, erzeugt "
                          "Oberschwingungen und belastet den Netzanschluss. Wer "
                          "das versteht, verkauft nicht nur ein Gerät — er löst das "
                          "Problem dahinter. Genau das unterscheidet mich von einem "
                          "reinen Verkäufer.", "sz": 13, "color": MUTE,
                     "font": BODY}], "line": 1.32}])

    items = [
        ("wave", "Power Quality nach Norm",
         "EN 50160 und IEC 61000-4-30 Klasse A sind für mich Alltag, nicht "
         "Theorie. Ich erkenne Netzprobleme, bevor sie zu Reklamationen werden."),
        ("battery", "Speicher als Argument",
         "Pufferbatterien machen 600-kW-Standorte am schwachen Netz erst möglich. "
         "Ich rechne dem Kunden vor, warum sich das lohnt."),
        ("bolt", "Technik wird zu ROI",
         "Ich übersetze Kilowatt und Oberschwingungen in Wirtschaftlichkeit — "
         "die Sprache, die der Entscheider unterschreibt."),
    ]
    cw, gap = 3.78, 0.33
    cy, ch = 3.12, 3.18
    for i, (ic, ttl, body) in enumerate(items):
        x = MX + i * (cw + gap)
        rect(s, x, cy, cw, ch, fill=CARD, line=LINE_LT, radius=0.05, shadow=True)
        badge(s, x + 0.62, cy + 0.70, 0.80, RED, ic, ratio=0.52)
        text(s, x + 0.34, cy + 1.28, cw - 0.66, 0.6,
             [{"runs": [{"t": ttl, "sz": 15, "color": INK_TXT, "b": True,
                         "font": HEAD}], "line": 1.05}])
        text(s, x + 0.34, cy + 1.92, cw - 0.66, 1.5,
             [{"runs": [{"t": body, "sz": 11.5, "color": MUTE, "font": BODY}],
               "line": 1.26}])
    footer(s, 6)
    notes(s,
          "Mein Alleinstellungsmerkmal: ich spreche die Netz-Sprache. Die Normen "
          "(EN 50160 / IEC 61000-4-30) nur EINMAL nennen — Kompetenz zeigen, nicht "
          "dozieren. Pointe ist die dritte Karte: Technik wird zu ROI. Das ist die "
          "Sprache, die der Entscheider unterschreibt.")
    return s


# ---------- SLIDE 7 · Hausaufgaben ----------
def slide7():
    s = new("paper.png")
    kicker(s, MX, 0.72, "ICH HABE MEINE HAUSAUFGABEN GEMACHT")
    headline(s, MX, 1.06, 11.5, [
        {"t": "Ich kenne euer Geschäft — ", "sz": 26, "color": INK_TXT, "b": True,
         "font": HEAD},
        {"t": "und sehe die Verkaufschancen.", "sz": 26, "color": RED, "b": True,
         "font": HEAD}])

    items = [
        ("bolt", "50 Mio. CHF bis 2035",
         "Ihr baut ein flächendeckendes Schnelllader-Netz auf. Wachstum braucht "
         "jemanden, der Standorte verkauft, nicht nur plant."),
        ("charger", "360 bis 600 kW",
         "Vom Netz bis zum Truck-Hypercharger mit Stützbatterie. Je höher die "
         "Leistung, desto wichtiger Speicher und Lastmanagement — mein Feld."),
        ("chip", "Plug'n Roll, ABB, Etrel",
         "Mit der Übernahme habt ihr Portfolio und Ladepunkte stark erweitert. "
         "Mehr Hardware heisst mehr Beratungsbedarf beim Kunden."),
        ("handshake", "Full Service, alles aus einer Hand",
         "Ladestation, Lastmanagement, Abrechnung. Genau dieses Bündel verkaufe "
         "ich gerne — ein Ansprechpartner, eine Lösung."),
    ]
    cw, gap = 5.78, 0.34
    ch, gv = 1.88, 0.28
    x0, y0 = MX, 2.10
    for i, (ic, ttl, body) in enumerate(items):
        x = x0 + (i % 2) * (cw + gap)
        y = y0 + (i // 2) * (ch + gv)
        rect(s, x, y, cw, ch, fill=CARD, line=LINE_LT, radius=0.05, shadow=True)
        rect(s, x, y, 0.09, ch, fill=RED)
        badge(s, x + 0.78, y + ch / 2, 0.92, INK, ic, ratio=0.5)
        text(s, x + 1.42, y + 0.28, cw - 1.7, 0.5,
             [{"runs": [{"t": ttl, "sz": 16, "color": RED, "b": True,
                         "font": HEAD}]}])
        text(s, x + 1.42, y + 0.78, cw - 1.7, 1.0,
             [{"runs": [{"t": body, "sz": 11.5, "color": MUTE, "font": BODY}],
               "line": 1.26}])
    footer(s, 7)
    notes(s,
          "Beweisen, dass ich AVIA VOLT recherchiert habe: 50 Mio. bis 2035, "
          "360–600 kW, die Übernahme von Plug'n Roll / ABB / Etrel. Signal an die "
          "Runde: ich denke schon wie ein Mitarbeiter, nicht wie ein Bewerber. "
          "Konkrete Zahlen ruhig nennen, sie zeigen Vorbereitung.")
    return s


# ---------- SLIDE 8 · Wo ich Umsatz hole ----------
def slide8():
    s = new("paper.png")
    kicker(s, MX, 0.72, "WO ICH UMSATZ HOLE")
    headline(s, MX, 1.06, 11.5, [
        {"t": "Fünf Jagdgründe, ", "sz": 27, "color": INK_TXT, "b": True,
         "font": HEAD},
        {"t": "vom ersten Tag an.", "sz": 27, "color": RED, "b": True,
         "font": HEAD}])

    items = [
        ("truck", "Logistik & Flotten",
         "Depot-Laden und Truck-Hypercharger. Hohe Leistung, klarer Business "
         "Case, wiederkehrender Bedarf."),
        ("retail", "Gewerbe & Retail",
         "Tankstellen, Detailhandel, Park-and-Charge. Standorte, die Frequenz in "
         "Strom umwandeln."),
        ("industry", "Industrie & KMU",
         "Firmenflotten plus Speicher zur Lastspitzenkappung. Genau meine "
         "Bestandskunden-Welt."),
        ("gov", "Gemeinden & Städte",
         "Öffentliche Ladeinfrastruktur, Ausschreibungen, Versorgungsauftrag. "
         "Vertrauensgeschäft."),
        ("building", "Immobilien & Verwaltungen",
         "Mehrfamilienhäuser und Geschäftsgebäude mit Lastmanagement vom Keller "
         "bis zur Tiefgarage."),
    ]
    cw, gap = 2.19, 0.225
    cy, ch = 2.30, 4.05
    for i, (ic, ttl, body) in enumerate(items):
        x = MX + i * (cw + gap)
        rect(s, x, cy, cw, ch, fill=CARD, line=LINE_LT, radius=0.06, shadow=True)
        rect(s, x, cy, cw, 0.09, fill=RED)
        badge(s, x + cw / 2, cy + 0.86, 0.96, INK, ic, ratio=0.5)
        text(s, x + 0.20, cy + 1.52, cw - 0.40, 0.85,
             [{"runs": [{"t": ttl, "sz": 13.5, "color": INK_TXT, "b": True,
                         "font": HEAD}], "line": 1.05, "align": "c"}])
        text(s, x + 0.20, cy + 2.34, cw - 0.40, 1.6,
             [{"runs": [{"t": body, "sz": 10.5, "color": MUTE, "font": BODY}],
               "line": 1.24, "align": "c"}])
    footer(s, 8)
    notes(s,
          "Fünf konkrete Jagdgründe — zeigt, dass ich am Tag 1 weiss, wo ich "
          "anrufe. Bei 'Industrie & KMU' betonen: das ist meine Bestandskunden-"
          "Welt. Mit Energie vortragen, das ist die Macher-Slide. Reihenfolge = "
          "Priorität.")
    return s


# ---------- SLIDE 9 · Mein Plan (90 Tage) ----------
def slide9():
    s = new("paper.png")
    kicker(s, MX, 0.72, "MEIN PLAN")
    headline(s, MX, 1.06, 11.5, [
        {"t": "Was ich in den ersten ", "sz": 27, "color": INK_TXT, "b": True,
         "font": HEAD},
        {"t": "90 Tagen liefere.", "sz": 27, "color": RED, "b": True,
         "font": HEAD}])

    phases = [
        ("1", "Tag 1–30", "Eintauchen",
         "Portfolio, Technik und Preise intern durchdringen. Mitfahrten im "
         "Aussendienst, Gebiet und Pipeline aufnehmen, Wunschkundenprofil "
         "schärfen."),
        ("2", "Tag 31–60", "Pipeline aufbauen",
         "Konkrete Zielkundenliste für CPO, Gewerbe und Logistik. Erste Termine, "
         "erste Angebote, klare Abschlusslogik."),
        ("3", "Tag 61–90", "Liefern",
         "Erste unterschriebene Abschlüsse und Rahmengespräche. Forecast steht. "
         "Erste Referenz-Story für den Markt."),
    ]
    cw, gap = 3.78, 0.33
    cy, ch = 2.55, 3.7
    # connecting timeline
    rect(s, MX + 0.4, cy - 0.02, (cw + gap) * 2 + 0.0, 0.03, fill=LINE_LT)
    for i, (num, span, ttl, body) in enumerate(phases):
        x = MX + i * (cw + gap)
        oval(s, x + 0.10, cy - 0.40, 0.78, RED)
        text(s, x + 0.10, cy - 0.40, 0.78, 0.78,
             [{"runs": [{"t": num, "sz": 26, "color": WHITE, "b": True,
                         "font": HEAD}], "align": "c"}], anchor="m")
        rect(s, x, cy + 0.62, cw, ch - 0.62, fill=CARD, line=LINE_LT,
             radius=0.05, shadow=True)
        text(s, x + 0.34, cy + 0.92, cw - 0.66, 0.4,
             [{"runs": [{"t": span, "sz": 12, "color": RED, "b": True,
                         "font": HEAD, "spc": 1.2}]}])
        text(s, x + 0.34, cy + 1.34, cw - 0.66, 0.6,
             [{"runs": [{"t": ttl, "sz": 20, "color": INK_TXT, "b": True,
                         "font": HEAD}]}])
        rect(s, x + 0.36, cy + 1.92, 0.7, 0.045, fill=RED)
        text(s, x + 0.34, cy + 2.12, cw - 0.66, 1.5,
             [{"runs": [{"t": body, "sz": 11.5, "color": MUTE, "font": BODY}],
               "line": 1.28}])
    footer(s, 9)
    notes(s,
          "Struktur signalisiert Verlässlichkeit. Drei Phasen sauber benennen: "
          "Eintauchen – Pipeline – Liefern. Klar machen: an Tag 90 stehen erste "
          "Abschlüsse UND ein Forecast. Konkret bleiben, nicht vage. Das ist mein "
          "Versprechen an den Vorgesetzten.")
    return s


# ---------- SLIDE 10 · Lass uns reden ----------
def slide10():
    s = new("hero.png")
    kicker(s, MX, 0.95, "LASS UNS REDEN", dark=True)
    text(s, MX, 1.55, 11.6, 1.8,
         [{"runs": [
             {"t": "Ihr sucht jemanden mit technischem Verständnis, Freude am "
                   "Kundenkontakt und ", "sz": 30, "color": WHITE, "b": True,
              "font": HEAD},
             {"t": "Biss", "sz": 30, "color": RED, "b": True, "font": HEAD},
             {"t": ".", "sz": 30, "color": WHITE, "b": True, "font": HEAD},
         ], "line": 1.12}])
    text(s, MX, 3.45, 11.0, 1.2,
         [{"runs": [{"t": "Genau das bringe ich mit. Seit über zehn Jahren, auf "
                          "dem Schweizer Markt, mit der Technik im Rücken. Gebt mir "
                          "das Gebiet — ", "sz": 14, "color": MUTE_LT,
                     "font": BODY},
                    {"t": "ich gebe der Energiewende ein Geschäftsmodell.",
                     "sz": 14, "color": WHITE, "b": True, "font": HEAD}],
           "line": 1.4}])

    rect(s, MX + 0.02, 4.85, 1.6, 0.04, fill=RED)

    contacts = [
        ("phone", "TELEFON", "+41 79 512 98 07"),
        ("mail", "E-MAIL", "b.s.uecoez@gmail.com"),
        ("pin", "STANDORT", "8240 Thayngen, Schweiz"),
    ]
    cw, gap = 3.78, 0.33
    cy, ch = 5.25, 1.25
    for i, (ic, lab, val) in enumerate(contacts):
        x = MX + i * (cw + gap)
        rect(s, x, cy, cw, ch, fill=CARD_DK, line=LINE_DK, radius=0.10)
        badge(s, x + 0.62, cy + ch / 2, 0.66, RED, ic, ratio=0.5)
        text(s, x + 1.06, cy + 0.27, cw - 1.3, 0.3,
             [{"runs": [{"t": lab, "sz": 9.5, "color": MUTE_LT, "b": True,
                         "font": HEAD, "spc": 1.8}]}])
        text(s, x + 1.06, cy + 0.58, cw - 1.3, 0.5,
             [{"runs": [{"t": val, "sz": 13.5, "color": WHITE, "b": True,
                         "font": HEAD}]}])
    text(s, MX, 6.95, SW - 2 * MX, 0.35,
         [{"runs": [{"t": "Burak Ücöz · Vertriebsingenieur · EMV & Power Quality",
                     "sz": 10.5, "color": MUTE_LT, "font": BODY, "spc": 0.8}]}])
    notes(s,
          "Abschluss = klarer Call to Action. Den letzten Satz langsam sprechen: "
          "'Gebt mir das Gebiet — ich gebe der Energiewende ein Geschäftsmodell.' "
          "Danach kurz Stille wirken lassen. Kontaktkarten stehen lassen, "
          "freundlich und selbstsicher abschliessen. Lächeln, Augenkontakt.")
    return s


for fn in (slide1, slide2, slide3, slide4, slide5,
           slide6, slide7, slide8, slide9, slide10):
    fn()

cp = prs.core_properties
cp.title = "Bewerbung Vertriebsmanager — AVIA VOLT Suisse"
cp.author = "Burak Ücöz"
cp.subject = "Pitch-Deck · Vertriebsmanager DC-Ladeinfrastruktur"
cp.keywords = "AVIA VOLT, Vertrieb, Ladeinfrastruktur, EMV, Power Quality"
cp.category = "Bewerbung"
cp.comments = "Speaker-Notes pro Slide nur für den Vortragenden."

OUT = os.path.join(ROOT, "Pitch_Burak_AVIA_VOLT.pptx")
prs.save(OUT)
print("saved:", OUT, "| slides:", len(prs.slides._sldIdLst))
