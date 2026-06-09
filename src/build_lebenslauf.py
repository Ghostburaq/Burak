# -*- coding: utf-8 -*-
"""
Lebenslauf Burak Üçöz - MODERNES Design, Schweizer Format (A4, ss-Schreibweise).
Zweispaltiges Layout: farbige Sidebar (Kontakt/Skills/Sprachen) + Hauptspalte
(Profil/Erfahrung/Ausbildung). Header-Band mit Akzentfarbe.

Platzhalter bleiben dezent 〈markiert〉 - nur Burak kann sie verifizieren.
Erzeugt: bewerbung/Lebenslauf_Burak_Uecoez.docx
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------- Palette (edel, zurückhaltend) ----------
NAVY   = RGBColor(0x16, 0x2A, 0x43)   # Header-Band, Akzent dunkel
STEEL  = RGBColor(0x2C, 0x5F, 0x8A)   # Sekundärakzent
INK    = RGBColor(0x22, 0x26, 0x2B)   # Fliesstext
GREY   = RGBColor(0x6B, 0x72, 0x80)   # Sekundärtext
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xE8, 0xEC, 0xF1)   # helle Schrift auf Navy
PH_COL = RGBColor(0x9A, 0x7A, 0x2E)   # Platzhalter-Text (gedämpftes Gold)

NAVY_HEX  = "162A43"
SIDE_HEX  = "EEF2F6"   # Sidebar-Hintergrund
PH_FILL   = "FBF1D8"   # Platzhalter-Highlight (zart)
LINE_HEX  = "C9D2DC"

FONT = "Calibri"
FONT_H = "Calibri"   # einheitlich, ruhig


# ================= Low-level Helfer =================
def set_font(run, size=10.5, bold=False, color=INK, name=FONT, italic=False, spacing=None, caps=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rF = rPr.find(qn('w:rFonts'))
    if rF is None:
        rF = OxmlElement('w:rFonts'); rPr.append(rF)
    rF.set(qn('w:ascii'), name); rF.set(qn('w:hAnsi'), name)
    if spacing is not None:
        sp = OxmlElement('w:spacing'); sp.set(qn('w:val'), str(spacing)); rPr.append(sp)
    if caps:
        c = OxmlElement('w:caps'); c.set(qn('w:val'), 'true'); rPr.append(c)


def shade_run(run, hexcolor):
    rPr = run._element.get_or_add_rPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor)
    rPr.append(shd)


def sp(p, before=0, after=0, line=1.12):
    pf = p.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after)
    pf.line_spacing = line


def run(p, text, **kw):
    r = p.add_run(text); set_font(r, **kw); return r


def ph(p, text, size=10, color=None):
    r = p.add_run("〈" + text + "〉")
    set_font(r, size=size, color=color or PH_COL, italic=True)
    shade_run(r, PH_FILL)
    return r


def cell_bg(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)


def cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    m = OxmlElement('w:tcMar')
    for tag, val in (('top', top), ('bottom', bottom), ('start', left),
                     ('end', right), ('left', left), ('right', right)):
        e = OxmlElement('w:' + tag); e.set(qn('w:w'), str(val)); e.set(qn('w:type'), 'dxa')
        m.append(e)
    tcPr.append(m)


def no_borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement('w:' + edge); e.set(qn('w:val'), 'none'); e.set(qn('w:sz'), '0')
        borders.append(e)
    tblPr.append(borders)


def set_w(cell, cm):
    cell.width = Cm(cm)
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.find(qn('w:tcW'))
    if tcW is None:
        tcW = OxmlElement('w:tcW'); tcPr.append(tcW)
    tcW.set(qn('w:w'), str(int(cm * 567))); tcW.set(qn('w:type'), 'dxa')


def fixed_layout(table):
    tblPr = table._tbl.tblPr
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)


def hrule(p, color=LINE_HEX, size=6):
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), str(size))
    b.set(qn('w:space'), '3'); b.set(qn('w:color'), color)
    pbdr.append(b); pPr.append(pbdr)


# ================= Dokument =================
doc = Document()
s = doc.sections[0]
s.page_height = Cm(29.7); s.page_width = Cm(21.0)
s.top_margin = Cm(0); s.bottom_margin = Cm(1.1)
s.left_margin = Cm(1.3); s.right_margin = Cm(1.3)
s.header_distance = Cm(0); s.footer_distance = Cm(0.6)

st = doc.styles['Normal']
st.font.name = FONT; st.font.size = Pt(10.5); st.font.color.rgb = INK
st.paragraph_format.space_after = Pt(0)
st.paragraph_format.line_spacing = 1.12

USABLE = 21.0 - 1.3 - 1.3   # 18.4 cm
SIDE_W = 6.0
MAIN_W = USABLE - SIDE_W

# -------- HEADER-BAND (volle Breite, Navy) --------
htbl = doc.add_table(rows=1, cols=1)
htbl.alignment = WD_TABLE_ALIGNMENT.CENTER
fixed_layout(htbl)
hc = htbl.cell(0, 0)
set_w(hc, USABLE)
cell_bg(hc, NAVY_HEX)
cell_margins(hc, top=300, bottom=260, left=360, right=360)
# Name
p = hc.paragraphs[0]; sp(p, after=2, line=1.0)
run(p, "BURAK ", size=27, bold=True, color=WHITE, spacing=10)
run(p, "ÜÇÖZ", size=27, bold=True, color=RGBColor(0x8F, 0xB4, 0xD9), spacing=10)
# Titel
p = hc.add_paragraph(); sp(p, before=2, after=0, line=1.0)
run(p, "Technischer Vertrieb im Aussendienst", size=11.5, color=LIGHT, spacing=14, caps=True)
p = hc.add_paragraph(); sp(p, before=1, after=0, line=1.0)
run(p, "Gebietsverkauf  ·  Neukundenakquise  ·  Key-Account", size=10, color=RGBColor(0x9F,0xB2,0xC7), spacing=10)

# kleiner Abstand unter Band
spacer = doc.add_paragraph(); sp(spacer, before=0, after=4, line=0.5)

# -------- ZWEISPALTIGES BODY --------
body = doc.add_table(rows=1, cols=2)
body.alignment = WD_TABLE_ALIGNMENT.CENTER
fixed_layout(body); no_borders(body)
left = body.cell(0, 0); right = body.cell(0, 1)
set_w(left, SIDE_W); set_w(right, MAIN_W)
left.vertical_alignment = WD_ALIGN_VERTICAL.TOP
right.vertical_alignment = WD_ALIGN_VERTICAL.TOP
cell_bg(left, SIDE_HEX)
cell_margins(left, top=240, bottom=240, left=240, right=240)
cell_margins(right, top=240, bottom=240, left=360, right=200)


# ---------- SIDEBAR-Bausteine ----------
def side_title(cell, text, first=False):
    p = cell.add_paragraph(); sp(p, before=(0 if first else 14), after=5, line=1.0)
    run(p, text, size=10.5, bold=True, color=NAVY, spacing=24, caps=True)
    hrule(p, color="C9D2DC", size=6)
    return p


def side_line(cell, label, value_ph, val_real=None):
    p = cell.add_paragraph(); sp(p, before=0, after=3, line=1.05)
    if label:
        run(p, label + "\n", size=8.5, bold=True, color=STEEL, spacing=8, caps=True)
    if val_real:
        run(p, val_real, size=9.5, color=INK)
    else:
        ph(p, value_ph, size=9.5)
    return p


# Foto-Platzhalter
p = left.paragraphs[0]; sp(p, before=0, after=8, line=1.0)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = run(p, "  Foto  ", size=10, color=GREY, italic=True)
# Foto-Box: gerahmtes leeres Feld
pPr = p._p.get_or_add_pPr()
pbdr = OxmlElement('w:pBdr')
for edge in ('top','bottom','left','right'):
    e = OxmlElement('w:'+edge); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'6')
    e.set(qn('w:space'),'18'); e.set(qn('w:color'),'B7C2CE'); pbdr.append(e)
pPr.append(pbdr)
cap = left.add_paragraph(); sp(cap, before=0, after=10, line=1.0); cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
run(cap, "optional · CH-üblich", size=7.5, italic=True, color=GREY)

# KONTAKT
side_title(left, "Kontakt", first=False)
side_line(left, "Adresse", "Strasse Nr.\nPLZ Ort")
side_line(left, "Telefon", "+41 ...")
side_line(left, "E-Mail", None, "b.s.uecoez@gmail.com")
side_line(left, "LinkedIn", "linkedin.com/in/...")

# PERSÖNLICH
side_title(left, "Persönliches")
side_line(left, "Geburtsdatum", "TT.MM.JJJJ")
side_line(left, "Nationalität", "...")
side_line(left, "Bewilligung / Bürgerort", "...")
side_line(left, "Führerausweis", "Kat. B")

# SPRACHEN
side_title(left, "Sprachen")
for name, lvl in [("Deutsch","Muttersprache / Niveau"),("Französisch","z. B. B2"),
                  ("Englisch","z. B. B2/C1"),("Türkisch","Niveau")]:
    p = left.add_paragraph(); sp(p, before=0, after=4, line=1.0)
    run(p, name, size=9.5, bold=True, color=INK)
    run(p, "   ", size=9.5)
    ph(p, lvl, size=8.5)

# KOMPETENZEN
side_title(left, "Kompetenzen")
for skill in ["Neukundenakquise","Gebiets- & Budgetverantwortung","Technische Beratung",
              "Verhandlung & Abschluss","CRM / MS Office"]:
    p = left.add_paragraph(); sp(p, before=0, after=3, line=1.05)
    run(p, "▪ ", size=9, color=STEEL)
    if skill == "CRM / MS Office":
        run(p, "CRM ", size=9.5, color=INK); ph(p, "System", size=8.5); run(p, " · MS Office", size=9.5, color=INK)
    else:
        run(p, skill, size=9.5, color=INK)

# MILITÄR
side_title(left, "Militärdienst")
p = left.add_paragraph(); sp(p, before=0, after=0, line=1.05)
ph(p, "Funktion / Grad / abgeschlossen", size=9)


# ---------- HAUPTSPALTE-Bausteine ----------
def main_title(cell, text, first=False):
    p = cell.add_paragraph(); sp(p, before=(0 if first else 12), after=5, line=1.0)
    run(p, text, size=12.5, bold=True, color=NAVY, spacing=18, caps=True)
    hrule(p, color=NAVY_HEX, size=10)
    return p


def T(x): return (x, False)
def PP(x): return (x, True)

def job(cell, role, company, loc_ph, period_ph, bullets, anchor=False):
    # Rolle + Zeitraum (rechts)
    p = cell.add_paragraph(); sp(p, before=8, after=0, line=1.05)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(MAIN_W-0.56), WD_TAB_ALIGNMENT.RIGHT)
    run(p, role, size=11, bold=True, color=INK)
    run(p, "\t", size=9.5)
    ph(p, period_ph, size=9)
    # Firma · Ort
    p2 = cell.add_paragraph(); sp(p2, before=0, after=3, line=1.0)
    run(p2, company, size=10, bold=True, color=STEEL)
    run(p2, "   ·   ", size=9.5, color=GREY)
    ph(p2, loc_ph, size=9)
    if anchor:
        run(p2, "    ", size=8)
        rr = run(p2, " Ankerstation ", size=7.5, bold=True, color=WHITE)
        shade_run(rr, "2C5F8A")
    for segs in bullets:
        bp = cell.add_paragraph(); sp(bp, before=0, after=2, line=1.1)
        bp.paragraph_format.left_indent = Cm(0.42)
        bp.paragraph_format.first_line_indent = Cm(-0.42)
        run(bp, "▪  ", size=9, color=STEEL)
        for seg, is_ph in segs:
            if is_ph: ph(bp, seg, size=9.5)
            else: run(bp, seg, size=9.5)

# KURZPROFIL
main_title(right, "Kurzprofil", first=True)
p = right.add_paragraph(); sp(p, before=0, after=2, line=1.18)
run(p, "Technischer Vertriebsprofi mit Schwerpunkt Aussendienst und Gebietsverkauf "
       "erklärungsbedürftiger Produkte. Eigenverantwortung für ein Gebietsbudget von rund ", size=9.8)
run(p, "CHF 2,5 Mio.", size=9.8, bold=True, color=NAVY)
run(p, " Stärken in Neukundenakquise, technischer Beratung und langfristiger Kundenbindung. "
       "Führungserfahrung vorhanden und als persönliche Reife eingebracht – der Fokus bleibt klar "
       "auf Gebiets- und Kundenverantwortung. Verlässlich, abschlussstark und auf nachhaltige "
       "Geschäftsbeziehungen ausgerichtet.", size=9.8)

# BERUFSERFAHRUNG
main_title(right, "Berufserfahrung")
job(right, "Gebietsverkaufsleiter / Area Sales Manager", "Cortexia SA", "Region / Ort", "MM.JJJJ – heute",
    [[T("Eigenverantwortliche Entwicklung des Verkaufsgebiets mit Budgetvolumen von rund "), T("CHF 2,5 Mio.")],
     [T("Neukundenakquise und Ausbau bestehender Kunden; gewonnen: "), PP("Anzahl Neukunden / Volumen")],
     [T("Technische Beratung erklärungsbedürftiger Produkte – Erstansprache bis Abschluss.")],
     [PP("Konkretes Ergebnis / Projekt aus der Cortexia-Zeit")]], anchor=True)

job(right, "Aussendienst / Technischer Verkauf", "Camille Bauer Metrawatt AG", "Region / Ort", "MM.JJJJ – MM.JJJJ",
    [[T("Betreuung eines definierten Verkaufsgebiets im technischen B2B-Umfeld.")],
     [T("Neukundengewinnung: "), PP("echte Neukundenzahl"), T(" – belastbare Zahl statt Prozent.")],
     [PP("Umsatzentwicklung / Marktsituation (z. B. Umsatz im rückläufigen Markt gehalten und ausgebaut)")]])

for comp in ["MRK", "Manz", "Anadolu", "Pflitsch"]:
    job(right, "Funktion / Titel", comp, "Ort", "MM.JJJJ – MM.JJJJ",
        [[PP("Kernaufgabe und ein messbares Ergebnis")]])

job(right, "Funktion / Titel", "Kabuu", "Ort", "MM.JJJJ – MM.JJJJ",
    [[T("Langjähriges Engagement – Beleg für Beständigkeit und nachhaltige Kundenbeziehungen.")],
     [PP("Tätigkeit konkretisieren")]])

job(right, "Selbständige Tätigkeit", "Selbständig / Freelance", "Ort", "MM.JJJJ – MM.JJJJ",
    [[PP("Schwerpunkt und Reihenfolge der Freelance-Phase einordnen")]])

# AUSBILDUNG
main_title(right, "Ausbildung")
p = right.add_paragraph(); sp(p, before=2, after=0, line=1.05)
p.paragraph_format.tab_stops.add_tab_stop(Cm(MAIN_W-0.56), WD_TAB_ALIGNMENT.RIGHT)
ph(p, "Abschluss / Titel", size=10); run(p, "\t"); ph(p, "JJJJ – JJJJ", size=9)
p = right.add_paragraph(); sp(p, before=0, after=0, line=1.0)
ph(p, "Fachrichtung", size=9.5); run(p, "   ·   ", size=9.5, color=GREY); ph(p, "Hochschule / Institution, Ort", size=9.5)

# REFERENZEN
main_title(right, "Referenzen")
p = right.add_paragraph(); sp(p, before=2, after=0, line=1.0)
run(p, "Auf Anfrage gerne.", size=9.5, color=GREY)

doc.save("bewerbung/Lebenslauf_Burak_Uecoez.docx")
print("OK modernes Layout gespeichert")
