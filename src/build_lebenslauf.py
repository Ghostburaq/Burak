# -*- coding: utf-8 -*-
"""
Lebenslauf Burak S. Üçöz - modernes zweispaltiges Design, Schweizer Format.
Echte, aus den Quellen verifizierte Daten eingesetzt; NUR Datumsfelder bleiben
als dezente 〈Platzhalter〉 (auf Wunsch des Nutzers).
Erzeugt: bewerbung/Lebenslauf_Burak_Uecoez.docx
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY   = RGBColor(0x16, 0x2A, 0x43)
STEEL  = RGBColor(0x2C, 0x5F, 0x8A)
INK    = RGBColor(0x22, 0x26, 0x2B)
GREY   = RGBColor(0x6B, 0x72, 0x80)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xE8, 0xEC, 0xF1)
PH_COL = RGBColor(0x9A, 0x7A, 0x2E)
ACC    = RGBColor(0x8F, 0xB4, 0xD9)

NAVY_HEX = "162A43"; SIDE_HEX = "EEF2F6"; PH_FILL = "FBF1D8"; LINE_HEX = "C9D2DC"
FONT = "Calibri"


def set_font(run, size=10.5, bold=False, color=INK, name=FONT, italic=False, spacing=None, caps=False):
    run.font.name = name; run.font.size = Pt(size); run.font.bold = bold
    run.font.italic = italic; run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rF = rPr.find(qn('w:rFonts'))
    if rF is None:
        rF = OxmlElement('w:rFonts'); rPr.append(rF)
    rF.set(qn('w:ascii'), name); rF.set(qn('w:hAnsi'), name)
    if spacing is not None:
        s = OxmlElement('w:spacing'); s.set(qn('w:val'), str(spacing)); rPr.append(s)
    if caps:
        c = OxmlElement('w:caps'); c.set(qn('w:val'), 'true'); rPr.append(c)


def shade_run(run, hexcolor):
    rPr = run._element.get_or_add_rPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor); rPr.append(shd)


def sp(p, before=0, after=0, line=1.12):
    pf = p.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = line


def run(p, text, **kw):
    r = p.add_run(text); set_font(r, **kw); return r


def ph(p, text, size=10, color=None):
    r = p.add_run("〈" + text + "〉")
    set_font(r, size=size, color=color or PH_COL, italic=True); shade_run(r, PH_FILL); return r


def cell_bg(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor); tcPr.append(shd)


def cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr(); m = OxmlElement('w:tcMar')
    for tag, val in (('top', top), ('bottom', bottom), ('start', left),
                     ('end', right), ('left', left), ('right', right)):
        e = OxmlElement('w:' + tag); e.set(qn('w:w'), str(val)); e.set(qn('w:type'), 'dxa'); m.append(e)
    tcPr.append(m)


def no_borders(table):
    b = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement('w:' + edge); e.set(qn('w:val'), 'none'); e.set(qn('w:sz'), '0'); b.append(e)
    table._tbl.tblPr.append(b)


def set_w(cell, cm):
    cell.width = Cm(cm)
    tcPr = cell._tc.get_or_add_tcPr(); tcW = tcPr.find(qn('w:tcW'))
    if tcW is None:
        tcW = OxmlElement('w:tcW'); tcPr.append(tcW)
    tcW.set(qn('w:w'), str(int(cm * 567))); tcW.set(qn('w:type'), 'dxa')


def fixed_layout(table):
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); table._tbl.tblPr.append(lay)


def hrule(p, color=LINE_HEX, size=6):
    pPr = p._p.get_or_add_pPr(); pbdr = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), str(size)); b.set(qn('w:space'), '3'); b.set(qn('w:color'), color)
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
st.paragraph_format.space_after = Pt(0); st.paragraph_format.line_spacing = 1.12

USABLE = 21.0 - 1.3 - 1.3
SIDE_W = 6.0
MAIN_W = USABLE - SIDE_W

# -------- HEADER-BAND --------
htbl = doc.add_table(rows=1, cols=1); htbl.alignment = WD_TABLE_ALIGNMENT.CENTER; fixed_layout(htbl)
hc = htbl.cell(0, 0); set_w(hc, USABLE); cell_bg(hc, NAVY_HEX)
cell_margins(hc, top=300, bottom=260, left=360, right=360)
p = hc.paragraphs[0]; sp(p, after=2, line=1.0)
run(p, "BURAK ", size=27, bold=True, color=WHITE, spacing=10)
run(p, "ÜÇÖZ", size=27, bold=True, color=ACC, spacing=10)
p = hc.add_paragraph(); sp(p, before=2, after=0, line=1.0)
run(p, "Sales Engineer · Technischer Vertrieb", size=11.5, color=LIGHT, spacing=12, caps=True)
p = hc.add_paragraph(); sp(p, before=1, after=0, line=1.0)
run(p, "Investitionsgüter  ·  Neukundenakquise  ·  Gebietsverantwortung", size=10, color=RGBColor(0x9F,0xB2,0xC7), spacing=8)

doc.add_paragraph();
spacer = doc.paragraphs[-1]; sp(spacer, before=0, after=4, line=0.5)

# -------- BODY (zweispaltig) --------
body = doc.add_table(rows=1, cols=2); body.alignment = WD_TABLE_ALIGNMENT.CENTER
fixed_layout(body); no_borders(body)
left = body.cell(0, 0); right = body.cell(0, 1)
set_w(left, SIDE_W); set_w(right, MAIN_W)
left.vertical_alignment = WD_ALIGN_VERTICAL.TOP; right.vertical_alignment = WD_ALIGN_VERTICAL.TOP
cell_bg(left, SIDE_HEX)
cell_margins(left, top=240, bottom=240, left=240, right=240)
cell_margins(right, top=240, bottom=240, left=360, right=200)


def side_title(cell, text, first=False):
    p = cell.add_paragraph(); sp(p, before=(0 if first else 14), after=5, line=1.0)
    run(p, text, size=10.5, bold=True, color=NAVY, spacing=24, caps=True)
    hrule(p, color="C9D2DC", size=6); return p


def side_field(cell, label, real=None, placeholder=None):
    p = cell.add_paragraph(); sp(p, before=0, after=3, line=1.05)
    run(p, label.upper() + "\n", size=8.5, bold=True, color=STEEL, spacing=8)
    if real is not None:
        run(p, real, size=9.5, color=INK)
    else:
        ph(p, placeholder, size=9.5)
    return p


sx = SIDE_W  # nur für Bezug
# Foto-Box
p = left.paragraphs[0]; sp(p, before=0, after=8, line=1.0); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run(p, "  Foto  ", size=10, color=GREY, italic=True)
pPr = p._p.get_or_add_pPr(); pbdr = OxmlElement('w:pBdr')
for edge in ('top','bottom','left','right'):
    e = OxmlElement('w:'+edge); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'6')
    e.set(qn('w:space'),'18'); e.set(qn('w:color'),'B7C2CE'); pbdr.append(e)
pPr.append(pbdr)
cap = left.add_paragraph(); sp(cap, before=0, after=10, line=1.0); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
run(cap, "optional · CH-üblich", size=7.5, italic=True, color=GREY)

# KONTAKT (echt)
side_title(left, "Kontakt")
side_field(left, "Adresse", real="Im Abt 9a, 8240 Thayngen")
side_field(left, "Telefon", real="+41 76 202 01 70")
side_field(left, "E-Mail", real="b.s.uecoez@gmail.com")
side_field(left, "LinkedIn", placeholder="Profil-URL ergänzen")

# PERSÖNLICH (echt)
side_title(left, "Persönliches")
side_field(left, "Geburtsdatum", real="29.03.1986")
side_field(left, "Nationalität", real="deutsch")
side_field(left, "Aufenthalt CH", placeholder="Ausweis C / B ergänzen")
side_field(left, "Führerausweis", real="Kat. B")

# SPRACHEN (echt)
side_title(left, "Sprachen")
for name, lvl in [("Deutsch", "Muttersprache"), ("Englisch", "verhandlungssicher"),
                  ("Französisch", "gute Kenntnisse"), ("Türkisch", "fliessend"),
                  ("Schweizerdeutsch", "gutes Verständnis")]:
    p = left.add_paragraph(); sp(p, before=0, after=0, line=1.0)
    run(p, name, size=9.5, bold=True, color=INK)
    p2 = left.add_paragraph(); sp(p2, before=0, after=4, line=1.0)
    run(p2, lvl, size=8.5, color=GREY)

# KOMPETENZEN (aus Profil)
side_title(left, "Kompetenzen")
for sk in ["Technischer Vertrieb Investitionsgüter", "Aktive Neukundenakquise (Hunter)",
           "Consultative / Beratungsverkauf", "Angebots- & Projektabwicklung",
           "Verhandlung & Abschluss", "CRM · MS Office"]:
    p = left.add_paragraph(); sp(p, before=0, after=3, line=1.05)
    run(p, "▪ ", size=9, color=STEEL); run(p, sk, size=9.5, color=INK)

# ZUSATZQUALIFIKATIONEN (echt)
side_title(left, "Zusatzqualifikationen")
for q in ["EMV-Fachkraft", "Elektrofachkraft", "BetrSichV", "DGUV"]:
    p = left.add_paragraph(); sp(p, before=0, after=2, line=1.05)
    run(p, "▪ ", size=9, color=STEEL); run(p, q, size=9.5, color=INK)


# ---------- HAUPTSPALTE ----------
def main_title(cell, text, first=False):
    p = cell.add_paragraph(); sp(p, before=(0 if first else 12), after=5, line=1.0)
    run(p, text, size=12.5, bold=True, color=NAVY, spacing=18, caps=True)
    hrule(p, color=NAVY_HEX, size=10); return p


def T(x): return (x, False)
def PP(x): return (x, True)


def job(cell, role, company, location, period_ph, bullets, badge=None):
    p = cell.add_paragraph(); sp(p, before=8, after=0, line=1.05)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(MAIN_W - 0.56), WD_TAB_ALIGNMENT.RIGHT)
    run(p, role, size=11, bold=True, color=INK)
    run(p, "\t", size=9.5); ph(p, period_ph, size=9)
    p2 = cell.add_paragraph(); sp(p2, before=0, after=3, line=1.0)
    run(p2, company, size=10, bold=True, color=STEEL)
    run(p2, "   ·   ", size=9.5, color=GREY); run(p2, location, size=9.5, color=GREY)
    if badge:
        run(p2, "    ", size=8)
        rr = run(p2, " " + badge + " ", size=7.5, bold=True, color=WHITE); shade_run(rr, "2C5F8A")
    for segs in bullets:
        bp = cell.add_paragraph(); sp(bp, before=0, after=2, line=1.1)
        bp.paragraph_format.left_indent = Cm(0.42); bp.paragraph_format.first_line_indent = Cm(-0.42)
        run(bp, "▪  ", size=9, color=STEEL)
        for seg, is_ph in segs:
            if is_ph: ph(bp, seg, size=9.5)
            else: run(bp, seg, size=9.5)


# KURZPROFIL (echte Formulierung aus Profil)
main_title(right, "Kurzprofil", first=True)
p = right.add_paragraph(); sp(p, before=0, after=2, line=1.18)
run(p, "Erfahrener Sales Engineer mit ", size=9.8)
run(p, "über 10 Jahren B2B-Erfahrung", size=9.8, bold=True, color=NAVY)
run(p, " im technischen Vertrieb erklärungsbedürftiger Investitionsgüter. Fundierte technische "
       "Basis (Elektrotechnik B.Eng., EMV, Mess- & Analysesysteme) kombiniert mit ausgeprägter "
       "Hunter-Mentalität in der aktiven Neukundenakquise. Stärken im consultativen Verkauf "
       "komplexer Systeme, in der Angebots- und Projektabwicklung bis zur Inbetriebnahme sowie "
       "im Aufbau langfristiger Kundenbeziehungen. Verlässlich, abschlussstark und gewohnt, "
       "Verkaufsgebiete eigenverantwortlich zu führen.", size=9.8)

# BERUFSERFAHRUNG (echte Timeline, Mobil in Time ausgelassen)
main_title(right, "Berufserfahrung")

job(right, "Sales Engineer · Technischer Vertrieb", "Camille Bauer Metrawatt AG", "Wohlen AG",
    "MM.JJJJ – MM.JJJJ",
    [[T("Technischer Vertrieb von Mess- und Analysesystemen (u. a. Sineax, Messwandler / Signalumformer) im B2B-Umfeld.")],
     [T("Eigenverantwortliche Betreuung und Entwicklung von Kunden über mehrere Kantone.")],
     [T("Aktive Neukundenakquise und Ausbau bestehender Kundenbeziehungen.")],
     [PP("Konkretes Ergebnis / Neukundenzahl einsetzen")]],
    badge="Aktuellste Position")

job(right, "Gebietsverkaufsleiter / Area Sales Manager", "Cortexia SA", "Westschweiz",
    "MM.JJJJ – MM.JJJJ",
    [[T("Eigenverantwortliche Entwicklung des Verkaufsgebiets mit einem Budgetvolumen von rund "), T("CHF 2,5 Mio.")],
     [T("Neukundenakquise und technische Beratung – von der Erstansprache bis zum Abschluss.")],
     [PP("Konkretes Ergebnis / Projekt aus der Cortexia-Zeit ergänzen")]])

for comp in ["MRK", "Manz", "Pflitsch"]:
    job(right, "Funktion / Titel ergänzen", comp, "Ort", "MM.JJJJ – MM.JJJJ",
        [[T("Technischer Vertrieb / Aussendienst – "), PP("Kernaufgabe und ein messbares Ergebnis ergänzen")]])

job(right, "Selbständige Ingenieur- & Vertriebstätigkeit", "Kabuu Engineering", "Hagen (DE)",
    "MM.JJJJ – MM.JJJJ",
    [[T("Selbständige Tätigkeit im technischen Engineering- und Vertriebsumfeld (Freelance).")],
     [PP("Schwerpunkt / Projekte konkretisieren")]])

job(right, "Mithilfe Familienbetrieb", "Anadolu", "Ort",
    "MM.JJJJ – MM.JJJJ",
    [[PP("Optional – nur aufnehmen, falls relevant; sonst diese Station löschen")]])

# AUSBILDUNG (echt, Jahre als Platzhalter)
main_title(right, "Ausbildung")
p = right.add_paragraph(); sp(p, before=2, after=0, line=1.05)
p.paragraph_format.tab_stops.add_tab_stop(Cm(MAIN_W - 0.56), WD_TAB_ALIGNMENT.RIGHT)
run(p, "Bachelor of Engineering (B.Eng.) – Elektrotechnik", size=10, bold=True, color=INK)
run(p, "\t"); ph(p, "JJJJ – JJJJ", size=9)
p = right.add_paragraph(); sp(p, before=0, after=0, line=1.0)
run(p, "Hochschule Bochum, Deutschland", size=9.5, color=GREY)

# WEITERBILDUNG
main_title(right, "Weiterbildung & Zertifikate")
p = right.add_paragraph(); sp(p, before=2, after=0, line=1.1)
run(p, "EMV-Fachkraft · Elektrofachkraft · Betriebssicherheitsverordnung (BetrSichV) · DGUV", size=9.5, color=INK)

# REFERENZEN
main_title(right, "Referenzen")
p = right.add_paragraph(); sp(p, before=2, after=0, line=1.0)
run(p, "Auf Anfrage gerne.", size=9.5, color=GREY)

doc.save("bewerbung/Lebenslauf_Burak_Uecoez.docx")
print("OK CV mit echten Daten gespeichert")
