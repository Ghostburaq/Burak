# -*- coding: utf-8 -*-
"""
Bewerbungsschreiben (Anschreiben) im Schweizer Format - A4, ss-Schreibweise.
Wiederverwendbare Vorlage: alle veraenderlichen Stellen sind 〈grau hinterlegt〉.
Erzeugt: bewerbung/Anschreiben_Vorlage_Burak_Uecoez.docx
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INK = RGBColor(0x1A, 0x1A, 0x1A)
ACCENT = RGBColor(0x1F, 0x3A, 0x5F)
GREY = RGBColor(0x6E, 0x6E, 0x6E)
FONT = "Calibri"


def set_font(run, size=11, bold=False, color=INK, italic=False, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)


def shade(run, hexcolor="EDE3C8"):
    rPr = run._element.get_or_add_rPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hexcolor)
    rPr.append(shd)


def ph(p, text, size=11):
    r = p.add_run("〈" + text + "〉")
    set_font(r, size=size, color=GREY, italic=True)
    shade(r)
    return r


def no_space(p, before=0, after=0, line=1.15):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def txt(p, s, **kw):
    r = p.add_run(s)
    set_font(r, **kw)
    return r


doc = Document()
sec = doc.sections[0]
sec.page_height = Cm(29.7)
sec.page_width = Cm(21.0)
sec.top_margin = Cm(1.8)
sec.bottom_margin = Cm(1.5)
sec.left_margin = Cm(2.2)
sec.right_margin = Cm(2.2)

st = doc.styles['Normal']
st.font.name = FONT
st.font.size = Pt(11)
st.font.color.rgb = INK

# -------- Absender (oben) --------
p = doc.add_paragraph(); no_space(p, after=0)
txt(p, "Burak Üçöz", bold=True, size=12)
p = doc.add_paragraph(); no_space(p, after=0, line=1.1)
ph(p, "Strasse Nr.", size=10.5)
p = doc.add_paragraph(); no_space(p, after=0, line=1.1)
ph(p, "PLZ Ort", size=10.5)
p = doc.add_paragraph(); no_space(p, after=0, line=1.1)
ph(p, "+41 ...", size=10.5); txt(p, "   ·   ", size=10.5, color=GREY); ph(p, "b.s.uecoez@gmail.com", size=10.5)

# -------- Empfaenger --------
p = doc.add_paragraph(); no_space(p, before=20, after=0)
ph(p, "Firma / Unternehmen", size=11)
p = doc.add_paragraph(); no_space(p, after=0, line=1.1)
txt(p, "z. Hd. ", size=11)
ph(p, "Vorname Name der Kontaktperson", size=11)
hint = doc.add_paragraph(); no_space(hint, after=0)
txt(hint, "Empfänger verifizieren: Inserat nennt Sabrina Zimmerli, Mail gehört Monika Buchwalder – vor dem Senden klären.", size=8, italic=True, color=GREY)
p = doc.add_paragraph(); no_space(p, after=0, line=1.1)
ph(p, "Strasse Nr.", size=11)
p = doc.add_paragraph(); no_space(p, after=0, line=1.1)
ph(p, "PLZ Ort", size=11)

# -------- Ort, Datum (rechtsbuendig) --------
p = doc.add_paragraph(); no_space(p, before=18, after=0)
p.paragraph_format.tab_stops.add_tab_stop(Cm(16.6), WD_TAB_ALIGNMENT.RIGHT)
txt(p, "\t")
ph(p, "Ort", size=11); txt(p, ", "); ph(p, "TT. Monat JJJJ", size=11)

# -------- Betreff --------
p = doc.add_paragraph(); no_space(p, before=18, after=8)
txt(p, "Bewerbung als ", bold=True, size=11)
ph(p, "Stellenbezeichnung exakt aus dem Inserat", size=11)

# -------- Anrede --------
p = doc.add_paragraph(); no_space(p, after=10)
txt(p, "Sehr geehrte Frau ", size=11)
ph(p, "Name", size=11)
txt(p, "  /  Sehr geehrter Herr ", size=11, color=GREY)
ph(p, "Name", size=11)

# -------- Body --------
def para(runs, after=10):
    p = doc.add_paragraph(); no_space(p, after=after, line=1.2)
    for seg in runs:
        if isinstance(seg, tuple) and seg[1] == "ph":
            ph(p, seg[0], size=11)
        else:
            txt(p, seg, size=11)
    return p

# Absatz 1 – Aufhaenger / Motivation
para([
    "Ihre ausgeschriebene Stelle als ", ("Stellenbezeichnung", "ph"),
    " bei ", ("Firma", "ph"),
    " hat mich sofort angesprochen: Sie suchen jemanden, der ein Verkaufsgebiet "
    "eigenverantwortlich führt und konsequent neue Kunden gewinnt – genau das ist "
    "seit Jahren mein Tagesgeschäft. ",
    ("Optional: ein Satz, warum genau dieses Unternehmen / Produkt", "ph"),
])

# Absatz 2 – Beleg / Akquise (auf AGRO Gold kalibriert)
para([
    "In meiner aktuellen Funktion betreue ich ein Verkaufsgebiet mit einem Volumen von rund ",
    "CHF 2,5 Mio. und verantworte dieses von der Akquise bis zum Abschluss. ",
    "Neukundengewinnung ist dabei mein Schwerpunkt: ",
    ("konkrete Neukundenzahl / Beispiel einsetzen", "ph"),
    ". Erklärungsbedürftige, technische Produkte überzeuge ich nicht über den Preis, "
    "sondern über Beratung, Verlässlichkeit und einen Draht zum Kunden, der trägt.",
])

# Absatz 3 – Fit / Reife / Langfristigkeit
para([
    "Ich bringe Führungserfahrung mit, suche aber bewusst die Gebiets- und Kundenverantwortung "
    "im Aussendienst – dort liegt meine Stärke und meine Motivation. Dass ich auf langfristige "
    "Zusammenarbeit setze, zeigt sich an meinem mehrjährigen Engagement bei früheren Arbeitgebern. "
    "Bei ", ("Firma", "ph"),
    " möchte ich genau diese Beständigkeit und meine Abschlussstärke einbringen.",
])

# Absatz 4 – Abschluss / Gehalt / Verfuegbarkeit
para([
    "Über ein persönliches Gespräch freue ich mich sehr. ",
    ("Optional Lohnvorstellung: z. B. „Meine Gehaltsvorstellung liegt bei CHF 120'000 (Grund-/Gesamtlohn klären).“", "ph"),
    " Verfügbar bin ich ab ", ("Datum / per sofort / nach Vereinbarung", "ph"), ".",
])

# -------- Gruss --------
p = doc.add_paragraph(); no_space(p, before=4, after=0)
txt(p, "Freundliche Grüsse", size=11)
p = doc.add_paragraph(); no_space(p, before=22, after=0)
txt(p, "Burak Üçöz", bold=True, size=11)

# -------- Beilagen --------
p = doc.add_paragraph(); no_space(p, before=16, after=0)
txt(p, "Beilagen", bold=True, size=10, color=ACCENT)
for b in ["Lebenslauf", "Arbeitszeugnisse", "Diplome / Zertifikate"]:
    bp = doc.add_paragraph(); no_space(bp, after=0, line=1.05)
    txt(bp, "– " + b, size=10, color=GREY)

doc.save("bewerbung/Anschreiben_Vorlage_Burak_Uecoez.docx")
print("OK Anschreiben gespeichert")
