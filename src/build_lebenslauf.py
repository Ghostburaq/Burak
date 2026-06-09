# -*- coding: utf-8 -*-
"""
Lebenslauf (CV) im Schweizer Format - A4, nuechtern, ss-Schreibweise.
Erzeugt: bewerbung/Lebenslauf_Burak_Uecoez.docx

Platzhalter sind grau hinterlegt und in 〈spitzen Klammern〉 - das sind die
Stellen, die nur Burak selbst verifizieren/fuellen kann (LinkedIn-deckungsgleich).
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---- Farben (nuechtern, Schweizer Stil) ----
INK = RGBColor(0x1A, 0x1A, 0x1A)      # fast schwarz
ACCENT = RGBColor(0x1F, 0x3A, 0x5F)   # gedecktes Dunkelblau
GREY = RGBColor(0x6E, 0x6E, 0x6E)     # Sekundaertext
RULE = "BFBFBF"                        # Linienfarbe

FONT = "Calibri"


def set_font(run, size=10.5, bold=False, color=INK, name=FONT, italic=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    # Ostasiatische Schrift mitsetzen (sonst Fallback)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)


def shade(run, hexcolor="D9D9D9"):
    """Grau hinterlegen -> markiert Platzhalter."""
    rPr = run._element.get_or_add_rPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hexcolor)
    rPr.append(shd)


def ph(paragraph, text, size=10.5, color=None):
    """Platzhalter-Run: grau hinterlegt, dunkelgrau."""
    r = paragraph.add_run("〈" + text + "〉")
    set_font(r, size=size, color=color or GREY, italic=True)
    shade(r, "EDE3C8")  # zartes Sandgelb -> faellt auf, druckt aber dezent
    return r


def add_bottom_border(paragraph, color=RULE, size=6):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), str(size))
    bottom.set(qn('w:space'), '4')
    bottom.set(qn('w:color'), color)
    pbdr.append(bottom)
    pPr.append(pbdr)


def no_space(p, before=0, after=0, line=1.0):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def section_title(doc, text):
    p = doc.add_paragraph()
    no_space(p, before=10, after=4)
    r = p.add_run(text.upper())
    set_font(r, size=11, bold=True, color=ACCENT)
    # Sperrung (letter spacing) fuer ruhigen Stil
    rPr = r._element.get_or_add_rPr()
    spc = OxmlElement('w:spacing')
    spc.set(qn('w:val'), '20')
    rPr.append(spc)
    add_bottom_border(p)
    return p


# ====================================================================
doc = Document()

# A4 + Raender
sec = doc.sections[0]
sec.page_height = Cm(29.7)
sec.page_width = Cm(21.0)
sec.top_margin = Cm(1.6)
sec.bottom_margin = Cm(1.5)
sec.left_margin = Cm(2.0)
sec.right_margin = Cm(2.0)

# Basisstil
style = doc.styles['Normal']
style.font.name = FONT
style.font.size = Pt(10.5)
style.font.color.rgb = INK

# -------------------- KOPF: Name + Titel --------------------
h = doc.add_paragraph()
no_space(h, after=0)
r = h.add_run("Burak ")
set_font(r, size=24, bold=True, color=INK)
r = h.add_run("Üçöz")
set_font(r, size=24, bold=True, color=ACCENT)

sub = doc.add_paragraph()
no_space(sub, after=2)
r = sub.add_run("Technischer Vertrieb im Aussendienst · Gebietsverkauf · Neukundenakquise")
set_font(r, size=11.5, color=GREY)

# Kontaktzeile (Tab-getrennt, Platzhalter)
add_bottom_border(doc.add_paragraph())  # duenne Trennlinie oben

contact = doc.add_paragraph()
no_space(contact, before=4, after=2)
def kv(p, label, placeholder):
    r = p.add_run(label + " ")
    set_font(r, size=9.5, bold=True, color=ACCENT)
    ph(p, placeholder, size=9.5)
    r = p.add_run("    ")
    set_font(r, size=9.5)

kv(contact, "Adresse:", "Strasse Nr., PLZ Ort")
kv(contact, "Tel:", "+41 ...")
contact2 = doc.add_paragraph()
no_space(contact2, before=0, after=2)
kv(contact2, "E-Mail:", "b.s.uecoez@gmail.com")
kv(contact2, "LinkedIn:", "linkedin.com/in/...")
contact3 = doc.add_paragraph()
no_space(contact3, before=0, after=4)
kv(contact3, "Geburtsdatum:", "TT.MM.JJJJ")
kv(contact3, "Nationalität:", "...")
kv(contact3, "Bürgerort/Bewilligung:", "...")
add_bottom_border(doc.add_paragraph())

note = doc.add_paragraph()
no_space(note, before=2, after=6)
r = note.add_run("Hinweis: Alle Kontaktangaben müssen deckungsgleich mit LinkedIn sein – das wird vor dem Gespräch geprüft.")
set_font(r, size=8, italic=True, color=GREY)

# -------------------- KURZPROFIL --------------------
section_title(doc, "Kurzprofil")
p = doc.add_paragraph()
no_space(p, after=6, line=1.15)
r = p.add_run(
    "Technischer Vertriebsprofi mit Schwerpunkt Aussendienst und Gebietsverkauf erklärungs"
    "bedürftiger Produkte. Eigenverantwortung für ein Gebietsbudget von rund "
)
set_font(r)
r = p.add_run("CHF 2,5 Mio.")
set_font(r, bold=True)
r = p.add_run(
    " Stärken in Neukundenakquise, technischer Beratung und langfristiger Kundenbindung. "
    "Führungserfahrung vorhanden und als persönliche Reife eingebracht – der Fokus bleibt "
    "klar auf Gebiets- und Kundenverantwortung. Verlässlich, abschlussstark und auf "
    "nachhaltige Geschäftsbeziehungen ausgerichtet."
)
set_font(r)

# -------------------- BERUFSERFAHRUNG --------------------
section_title(doc, "Berufserfahrung")

def job(company, role_default, location, period_ph, bullets, anchor=False):
    # Zeile 1: Rolle ........ Zeitraum (rechtsbuendig)
    p = doc.add_paragraph()
    no_space(p, before=6, after=0)
    # Tab-Stop rechts
    p.paragraph_format.tab_stops.add_tab_stop(Cm(17.0), WD_TAB_ALIGNMENT.RIGHT)
    r = p.add_run(role_default)
    set_font(r, size=11, bold=True, color=INK)
    r = p.add_run("\t")
    set_font(r, size=10)
    ph(p, period_ph, size=10)
    # Zeile 2: Firma · Ort
    p2 = doc.add_paragraph()
    no_space(p2, before=0, after=2)
    r = p2.add_run(company)
    set_font(r, size=10.5, bold=True, color=ACCENT)
    r = p2.add_run("  ·  ")
    set_font(r, size=10.5, color=GREY)
    ph(p2, location, size=10)
    if anchor:
        r = p2.add_run("   ")
        set_font(r, size=9)
        r = p2.add_run("◆ Ankerstation")
        set_font(r, size=8.5, bold=True, color=ACCENT)
    # Bullets
    for b in bullets:
        bp = doc.add_paragraph(style=None)
        bp.paragraph_format.left_indent = Cm(0.5)
        bp.paragraph_format.first_line_indent = Cm(-0.5)
        no_space(bp, before=0, after=1, line=1.1)
        rr = bp.add_run("–  ")
        set_font(rr, size=10)
        # Bullet kann Platzhalter enthalten -> als Liste von (text, is_ph)
        for seg, is_ph in b:
            if is_ph:
                ph(bp, seg, size=10)
            else:
                rr = bp.add_run(seg)
                set_font(rr, size=10)

def T(s):  # normaler Textteil
    return (s, False)
def P(s):  # Platzhalter
    return (s, True)

# Cortexia – aktuellste/aktuelle Station (Gebiets-Profi nach vorne)
job(
    "Cortexia SA",
    "Gebietsverkaufsleiter / Area Sales Manager",
    "Region / Ort",
    "MM.JJJJ – heute",
    [
        [T("Eigenverantwortliche Betreuung und Entwicklung des Verkaufsgebiets mit einem "),
         T("Budgetvolumen von rund CHF 2,5 Mio.")],
        [T("Neukundenakquise und Ausbau bestehender Kundenbeziehungen; gewonnen: "),
         P("Anzahl Neukunden / Volumen einsetzen")],
        [T("Technische Beratung erklärungsbedürftiger Produkte von der Erstansprache bis zum Abschluss.")],
        [P("Konkretes Ergebnis / Projekt aus der Cortexia-Zeit ergänzen")],
    ],
    anchor=True,
)

# Camille Bauer – Akquise-Beleg (fuer AGRO Gold besonders relevant)
job(
    "Camille Bauer Metrawatt AG",
    "Aussendienst / Technischer Verkauf",
    "Region / Ort",
    "MM.JJJJ – MM.JJJJ",
    [
        [T("Betreuung eines definierten Verkaufsgebiets im technischen B2B-Umfeld.")],
        [T("Neukundengewinnung: "), P("echte Neukundenzahl einsetzen"),
         T(" – belastbare Zahl statt Prozentangabe.")],
        [P("Umsatzentwicklung / Marktsituation ergänzen (z. B. Umsatz im rückläufigen Markt gehalten und ausgebaut)")],
    ],
)

# Weitere Stationen – Geruest mit Platzhaltern (lueckenlos, LinkedIn-deckungsgleich)
job("MRK", "Funktion / Titel", "Ort", "MM.JJJJ – MM.JJJJ",
    [[P("Kernaufgabe und ein messbares Ergebnis ergänzen")]])
job("Manz", "Funktion / Titel", "Ort", "MM.JJJJ – MM.JJJJ",
    [[P("Kernaufgabe und ein messbares Ergebnis ergänzen")]])
job("Anadolu", "Funktion / Titel", "Ort", "MM.JJJJ – MM.JJJJ",
    [[P("Kernaufgabe und ein messbares Ergebnis ergänzen")]])
job("Pflitsch", "Funktion / Titel", "Ort", "MM.JJJJ – MM.JJJJ",
    [[P("Kernaufgabe und ein messbares Ergebnis ergänzen")]])

# Kabuu – Beleg fuer Langfristigkeit (gegen Wechselmuster)
job("Kabuu", "Funktion / Titel", "Ort", "MM.JJJJ – MM.JJJJ",
    [[T("Langjähriges Engagement – Beleg für Beständigkeit und nachhaltige Kundenbeziehungen.")],
     [P("Tätigkeit konkretisieren")]])

# Freelance-Phase
job("Selbständig / Freelance", "Selbständige Tätigkeit", "Ort", "MM.JJJJ – MM.JJJJ",
    [[P("Schwerpunkt und Reihenfolge der Freelance-Phase einordnen")]])

# -------------------- AUSBILDUNG --------------------
section_title(doc, "Ausbildung")
p = doc.add_paragraph()
no_space(p, before=4, after=0)
p.paragraph_format.tab_stops.add_tab_stop(Cm(17.0), WD_TAB_ALIGNMENT.RIGHT)
ph(p, "Abschluss / Titel", size=10.5)
r = p.add_run("\t")
set_font(r)
ph(p, "JJJJ – JJJJ", size=10)
p2 = doc.add_paragraph()
no_space(p2, before=0, after=4)
ph(p2, "Fachrichtung", size=10)
r = p2.add_run("  ·  ")
set_font(r, color=GREY)
ph(p2, "Hochschule / Institution, Ort", size=10)

# -------------------- SPRACHEN --------------------
section_title(doc, "Sprachen")
langs = [("Deutsch", "Muttersprache / Niveau"),
         ("Französisch", "Niveau (z. B. B2)"),
         ("Englisch", "Niveau (z. B. B2/C1)"),
         ("Türkisch", "Niveau"),
         ("Weitere", "Sprache / Niveau")]
for name, lvl in langs:
    p = doc.add_paragraph()
    no_space(p, before=0, after=1)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(4.0), WD_TAB_ALIGNMENT.LEFT)
    r = p.add_run(name)
    set_font(r, size=10, bold=True)
    r = p.add_run("\t")
    set_font(r, size=10)
    ph(p, lvl, size=10)

# -------------------- IT / WEITERE --------------------
section_title(doc, "IT-Kenntnisse & Weiteres")
for label, val in [("EDV / CRM", "z. B. MS Office, CRM-System einsetzen"),
                   ("Führerausweis", "Kat. B (für Aussendienst relevant)"),
                   ("Militärdienst", "Funktion / Grad / abgeschlossen")]:
    p = doc.add_paragraph()
    no_space(p, before=0, after=1)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(4.0), WD_TAB_ALIGNMENT.LEFT)
    r = p.add_run(label)
    set_font(r, size=10, bold=True)
    r = p.add_run("\t")
    set_font(r, size=10)
    ph(p, val, size=10)

# -------------------- REFERENZEN --------------------
section_title(doc, "Referenzen")
p = doc.add_paragraph()
no_space(p, before=2, after=0)
r = p.add_run("Auf Anfrage gerne.")
set_font(r, size=10, color=GREY)

doc.save("bewerbung/Lebenslauf_Burak_Uecoez.docx")
print("OK Lebenslauf gespeichert")
