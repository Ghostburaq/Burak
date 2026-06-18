# -*- coding: utf-8 -*-
"""
Baut aus den Schritt-Bildern eine fertige, teilbare PDF-Anleitung.

    python3 offerten/anleitung/make_anleitung_pdf.py
        -> offerten/anleitung/Anleitung_Excel_zu_PDF.pdf
"""
import os
from fpdf import FPDF

HERE = os.path.dirname(os.path.abspath(__file__))
ORANGE = (226, 98, 10)
DARK = (31, 41, 51)
GREY = (123, 135, 148)
GREEN = (33, 115, 70)


def _t(s):
    repl = {"–": "-", "—": "-", "‘": "'", "’": "'",
            "‚": "'", "“": '"', "”": '"', "„": '"',
            "…": "...", " ": " ", "•": "-", "→": ">"}
    for a, b in repl.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


STEPS = [
    ("schritt1.png", "Schritt 1 – Reiter „Datei“ öffnen",
     "Öffne die Offerte in Excel und klicke oben links auf den Reiter Datei."),
    ("schritt2.png", "Schritt 2 – „Exportieren“ wählen",
     "Klicke im linken Menü auf Exportieren."),
    ("schritt3.png", "Schritt 3 – „PDF/XPS-Dokument erstellen“",
     "Wähle PDF/XPS-Dokument erstellen und klicke auf den Button PDF/XPS erstellen."),
    ("schritt4.png", "Schritt 4 – Speichern & veröffentlichen",
     "Dateiname vergeben, Dateityp = PDF (*.pdf), dann auf Veröffentlichen klicken. "
     "Optional vorher auf Optionen... (Schritt 5)."),
    ("schritt5.png", "Schritt 5 (optional) – nur das Offerten-Blatt",
     "Im Optionen-Fenster „Aktive Blätter“ wählen und mit OK bestätigen. "
     "So kommt nur das Blatt Offerte ins PDF."),
    ("schritt6.png", "Fertig!",
     "Das PDF wird gespeichert und geöffnet – versandfertig."),
    ("alternative_drucken.png", "Alternative – „Drucken“ als PDF",
     "Datei > Drucken > Drucker „Microsoft Print to PDF“ > Drucken. "
     "Auf dem Mac: Drucken > PDF > „Als PDF sichern“."),
]


class Guide(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*ORANGE)
        self.set_y(8)
        self.cell(0, 5, "MOBIL IN TIME  -  Anleitung: Aus Excel ein PDF erstellen", align="L")
        self.set_draw_color(*ORANGE); self.set_line_width(0.3)
        self.line(15, 15, 195, 15)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 5, f"Seite {self.page_no()}", align="C")


def build():
    pdf = Guide(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(True, margin=15)
    pdf.set_margins(15, 14, 15)

    # ---- Titelseite
    pdf.add_page()
    pdf.set_fill_color(*GREEN); pdf.rect(0, 0, 210, 60, style="F")
    pdf.set_xy(15, 18)
    pdf.set_font("Helvetica", "B", 26); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Aus Excel ein PDF erstellen", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(15); pdf.set_font("Helvetica", "", 13)
    pdf.cell(0, 8, _t("Schritt-für-Schritt-Anleitung mit Bildern"))
    pdf.ln(28)
    pdf.set_text_color(*DARK); pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(180, 7, _t(
        "Diese Anleitung zeigt drei Wege, wie aus der Offerte (oder jeder "
        "Excel-Datei) ein PDF wird:"))
    pdf.ln(2)
    for t in ["Weg A  -  Datei > Exportieren > PDF/XPS  (empfohlen, ohne Makros)",
              "Weg B  -  Datei > Drucken > „Microsoft Print to PDF“  (Alternative)",
              "Weg C  -  PDF auf einen Klick per Schaltflaeche  (siehe vba/PDF_Knopf_Anleitung.md)"]:
        pdf.set_x(20); pdf.set_font("Helvetica", "B", 12); pdf.set_text_color(*ORANGE)
        pdf.cell(6, 7, ">")
        pdf.set_text_color(*DARK); pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(170, 7, _t(t))
        pdf.ln(1)
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 11); pdf.set_text_color(*GREY)
    pdf.multi_cell(180, 6, _t(
        "Tipp: In den Vorlagen ist der Druckbereich bereits gesetzt (Blatt "
        "Offerte, DIN A4) - das PDF wird automatisch eine saubere Seite."))

    # ---- Schritt-Seiten (2 pro Seite)
    for i, (img, title, desc) in enumerate(STEPS):
        if i % 2 == 0:
            pdf.add_page()
            y = 22
        else:
            y = 158
        pdf.set_xy(15, y)
        pdf.set_font("Helvetica", "B", 14); pdf.set_text_color(*DARK)
        pdf.cell(0, 8, _t(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(15); pdf.set_font("Helvetica", "", 11); pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(180, 5.5, _t(desc))
        path = os.path.join(HERE, img)
        # Bild 1280x800 -> Breite 170 mm, Hoehe ~106 mm
        pdf.image(path, x=20, y=pdf.get_y() + 2, w=170)

    out = os.path.join(HERE, "Anleitung_Excel_zu_PDF.pdf")
    pdf.output(out)
    print("PDF-Anleitung erstellt:", out)
    return out


if __name__ == "__main__":
    build()
