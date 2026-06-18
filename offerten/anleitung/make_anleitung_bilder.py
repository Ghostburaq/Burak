# -*- coding: utf-8 -*-
"""
Erzeugt die bebilderte Schritt-für-Schritt-Anleitung "Excel -> PDF".
Zeichnet schematische, klar beschriftete Excel-Abbildungen (kein echtes
Excel nötig) mit Pillow.

    python3 offerten/anleitung/make_anleitung_bilder.py
        -> offerten/anleitung/schritt1..7.png

Die Bilder sind bewusst vereinfachte Nachbauten der Excel-Oberfläche
(Windows). Sie zeigen, wo geklickt wird – Beschriftungen auf Deutsch.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 800

# ---- Farben
EXCEL   = (33, 115, 70)      # Excel-Grün
EXCEL_D = (21, 90, 53)
RIBBON  = (243, 242, 241)
WHITE   = (255, 255, 255)
GRIDC   = (217, 220, 224)
TEXT    = (31, 41, 51)
GREY    = (123, 135, 148)
LGREY   = (235, 237, 240)
ORANGE  = (226, 98, 10)      # Markenfarbe / Hervorhebung
BLUE    = (0, 120, 212)      # Windows-Button-Blau
SHADOW  = (0, 0, 0)

F = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FB if bold else F, size)


def canvas(bg=(232, 234, 237)):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)


def rounded(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def text(d, xy, s, f, fill=TEXT, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def center(d, box, s, f, fill=TEXT):
    x = (box[0] + box[2]) / 2
    y = (box[1] + box[3]) / 2
    d.text((x, y), s, font=f, fill=fill, anchor="mm")


def badge(d, xy, n, r=26, color=ORANGE):
    x, y = xy
    d.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=WHITE, width=3)
    if n == "check":
        w = max(4, r // 6)
        d.line([(x - r * 0.42, y), (x - r * 0.08, y + r * 0.38),
                (x + r * 0.45, y - r * 0.40)], fill=WHITE, width=w, joint="curve")
    else:
        d.text((x, y), str(n), font=font(int(r * 1.1), True), fill=WHITE, anchor="mm")


def draw_x(d, xy, s, color=GREY, width=2):
    x, y = xy
    d.line([(x - s, y - s), (x + s, y + s)], fill=color, width=width)
    d.line([(x - s, y + s), (x + s, y - s)], fill=color, width=width)


def callout(d, box, color=ORANGE, width=5):
    rounded(d, box, 10, outline=color, width=width)


def arrow(d, start, end, color=ORANGE, width=6):
    d.line([start, end], fill=color, width=width)
    import math
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    L = 18
    for da in (math.radians(150), math.radians(-150)):
        x = end[0] + L * math.cos(ang + da)
        y = end[1] + L * math.sin(ang + da)
        d.line([end, (x, y)], fill=color, width=width)


def hint(d, box, s, color=ORANGE):
    """Beschriftungsfähnchen unten."""
    rounded(d, box, 8, fill=color)
    center(d, box, s, font(19, True), WHITE)


# --------------------------------------------------------------- Bausteine
def window(d, title="Offerte_Kabel_95mm.xlsx  -  Excel", file_tab=False):
    # Fensterrahmen
    rounded(d, [40, 30, W - 40, H - 30], 12, fill=WHITE, outline=(200, 203, 208), width=2)
    # Titelleiste (grün)
    d.rounded_rectangle([40, 30, W - 40, 78], radius=12, fill=EXCEL)
    d.rectangle([40, 60, W - 40, 78], fill=EXCEL)
    text(d, (70, 54), title, font(17, True), WHITE, anchor="lm")
    # Fenster-Buttons (Minimieren / Maximieren / Schließen)
    d.line([(W - 152, 54), (W - 140, 54)], fill=WHITE, width=2)
    d.rectangle([W - 116, 48, W - 104, 60], outline=WHITE, width=2)
    draw_x(d, (W - 70, 54), 6, WHITE, 2)


def ribbon(d, active="Datei"):
    tabs = ["Datei", "Start", "Einfügen", "Seitenlayout", "Formeln",
            "Daten", "Überprüfen", "Ansicht"]
    y = 78
    d.rectangle([40, y, W - 40, y + 38], fill=EXCEL_D if False else RIBBON)
    x = 70
    for t in tabs:
        f = font(16, t == active)
        w = d.textlength(t, font=f)
        col = ORANGE if t == "Datei" else TEXT
        if t == "Datei":
            d.rounded_rectangle([x - 12, y + 4, x + w + 12, y + 34], radius=6, fill=ORANGE)
            text(d, (x, y + 19), t, font(16, True), WHITE, anchor="lm")
        else:
            text(d, (x, y + 19), t, f, col, anchor="lm")
        x += w + 34
    # Ribbon-Befehlsband
    d.rectangle([40, y + 38, W - 40, y + 120], fill=RIBBON)
    return y + 120


def worksheet(d, top):
    """Mini-Offerte als Tabellenblatt."""
    # Spaltenköpfe
    d.rectangle([40, top, W - 40, top + 26], fill=LGREY)
    cols = ["A", "B", "C", "D", "E", "F", "G"]
    cw = [60, 70, 470, 120, 150, 90, 150]
    x = 60
    for c, w in zip(cols, cw):
        center(d, [x, top, x + w, top + 26], c, font(13, True), GREY)
        x += w
    # Inhalt
    text(d, (70, top + 55), "MOBIL IN TIME", font(28, True), ORANGE, anchor="lm")
    text(d, (70, top + 90), "Mobil in Time AG · 8253 Diessenhofen", font(13), GREY, anchor="lm")
    # Tabellenkopf
    th = top + 130
    d.rectangle([60, th, W - 70, th + 30], fill=(31, 41, 51))
    heads = ["Pos", "Menge", "Beschreibung", "Einheit", "Einzelpreis", "Total"]
    hx = [60, 130, 230, 700, 830, 1010]
    for hh, xx in zip(heads, hx):
        text(d, (xx + 8, th + 15), hh, font(13, True), WHITE, anchor="lm")
    rows = [
        ("1", "12", "Steckendverschluss Typ C", "Stk", "304.46", "3'653.52"),
        ("2", "3", "Kabel 95/25 20/12kV, 6 x 50m", "Set", "2'780.31", "8'340.93"),
        ("3", "12", "Regie Arbeit", "Std", "208.00", "2'496.00"),
    ]
    ry = th + 30
    for i, row in enumerate(rows):
        if i % 2:
            d.rectangle([60, ry, W - 70, ry + 30], fill=(244, 246, 248))
        for val, xx, al in zip(row, hx, ["l", "l", "l", "l", "r", "r"]):
            ax = xx + 8 if al == "l" else xx + 150
            anc = "lm" if al == "l" else "rm"
            text(d, (ax, ry + 15), val, font(13), TEXT, anchor=anc)
        ry += 30
    # Endbetrag
    d.rectangle([60, ry + 6, W - 70, ry + 40], fill=(252, 238, 227))
    text(d, (700, ry + 23), "Endbetrag (CHF)", font(14, True), TEXT, anchor="lm")
    text(d, (1160, ry + 23), "14'490.45", font(15, True), TEXT, anchor="rm")
    return top


def backstage(d, active="Exportieren"):
    """Datei-Menü (Backstage)."""
    d.rounded_rectangle([40, 30, W - 40, H - 30], 12, fill=WHITE, outline=(200, 203, 208), width=2)
    # grüner Seitenstreifen
    d.rounded_rectangle([40, 30, 320, H - 30], 12, fill=EXCEL)
    d.rectangle([300, 30, 320, H - 30], fill=EXCEL)
    text(d, (70, 70), "← ", font(26, True), WHITE, anchor="lm")
    items = ["Informationen", "Neu", "Öffnen", "Speichern",
             "Speichern unter", "Drucken", "Exportieren", "Schließen"]
    y = 150
    for it in items:
        if it == active:
            d.rectangle([40, y - 6, 320, y + 38], fill=WHITE)
            text(d, (75, y + 16), it, font(18, True), EXCEL, anchor="lm")
        else:
            text(d, (75, y + 16), it, font(17), WHITE, anchor="lm")
        y += 56
    return 40 + 280  # rechter Bereich beginnt bei x=320


def main():
    os.makedirs(HERE, exist_ok=True)

    # ===== Schritt 1: Datei-Tab anklicken
    img, d = canvas()
    window(d)
    top = ribbon(d, active="Datei")
    worksheet(d, top)
    callout(d, [56, 80, 132, 116])
    badge(d, (300, 200), 1)
    arrow(d, (300, 170), (110, 120))
    hint(d, [150, 720, 1130, 762],
         "Schritt 1:  Oben links auf den Reiter „Datei“ klicken")
    img.save(os.path.join(HERE, "schritt1.png"))

    # ===== Schritt 2: Exportieren wählen
    img, d = canvas()
    rx = backstage(d, active="Exportieren")
    text(d, (rx + 30, 150), "Exportieren", font(26, True), TEXT, anchor="lm")
    # rechte Auswahl
    d.rounded_rectangle([rx + 30, 210, rx + 470, 320], 10, fill=LGREY, outline=GRIDC, width=2)
    text(d, (rx + 55, 245), "Adobe-PDF erstellen", font(17, True), TEXT, anchor="lm")
    text(d, (rx + 55, 278), "PDF/XPS-Dokument erstellen", font(17, True), TEXT, anchor="lm")
    d.rounded_rectangle([rx + 30, 340, rx + 470, 420], 10, fill=LGREY, outline=GRIDC, width=2)
    text(d, (rx + 55, 380), "Dateityp ändern", font(17, True), TEXT, anchor="lm")
    callout(d, [44, 372, 320, 414])
    badge(d, (470, 393), 2)
    arrow(d, (450, 393), (325, 393))
    hint(d, [150, 720, 1130, 762],
         "Schritt 2:  Im Menü „Exportieren“ anklicken")
    img.save(os.path.join(HERE, "schritt2.png"))

    # ===== Schritt 3: PDF/XPS-Dokument erstellen
    img, d = canvas()
    rx = backstage(d, active="Exportieren")
    text(d, (rx + 30, 150), "Exportieren", font(26, True), TEXT, anchor="lm")
    d.rounded_rectangle([rx + 30, 210, rx + 470, 320], 10, fill=(230, 244, 236),
                        outline=EXCEL, width=2)
    text(d, (rx + 55, 245), "PDF/XPS-Dokument erstellen", font(18, True), EXCEL, anchor="lm")
    text(d, (rx + 55, 280), "• Layout, Schrift und Bilder bleiben erhalten",
         font(14), GREY, anchor="lm")
    # großer Button
    d.rounded_rectangle([rx + 540, 250, rx + 720, 340], 10, fill=EXCEL)
    center(d, [rx + 540, 250, rx + 720, 340], "PDF/XPS\nerstellen", font(18, True), WHITE)
    callout(d, [rx + 534, 244, rx + 726, 346], color=ORANGE)
    badge(d, (rx + 760, 200), 3)
    arrow(d, (rx + 740, 220), (rx + 720, 270))
    hint(d, [150, 720, 1130, 762],
         "Schritt 3:  „PDF/XPS-Dokument erstellen“ wählen und auf den Button „PDF/XPS erstellen“ klicken")
    img.save(os.path.join(HERE, "schritt3.png"))

    # ===== Schritt 4: Veröffentlichen-Dialog
    img, d = canvas((210, 213, 218))
    # Dialogfenster
    dx0, dy0, dx1, dy1 = 230, 120, 1050, 660
    d.rectangle([dx0 + 8, dy0 + 8, dx1 + 8, dy1 + 8], fill=(170, 173, 178))  # Schatten
    d.rectangle([dx0, dy0, dx1, dy1], fill=WHITE, outline=(150, 153, 158), width=2)
    d.rectangle([dx0, dy0, dx1, dy0 + 44], fill=(245, 246, 248))
    text(d, (dx0 + 20, dy0 + 22), "Als PDF oder XPS veröffentlichen", font(18, True), TEXT, anchor="lm")
    draw_x(d, (dx1 - 26, dy0 + 22), 7, GREY, 2)
    # Dateiname
    text(d, (dx0 + 30, dy0 + 110), "Dateiname:", font(16), TEXT, anchor="lm")
    d.rectangle([dx0 + 180, dy0 + 92, dx1 - 40, dy0 + 128], fill=WHITE, outline=GREY, width=1)
    text(d, (dx0 + 192, dy0 + 110), "Offerte_Kabel_95mm", font(16), TEXT, anchor="lm")
    # Dateityp
    text(d, (dx0 + 30, dy0 + 160), "Dateityp:", font(16), TEXT, anchor="lm")
    d.rectangle([dx0 + 180, dy0 + 142, dx1 - 40, dy0 + 178], fill=WHITE, outline=GREY, width=1)
    text(d, (dx0 + 192, dy0 + 160), "PDF (*.pdf)", font(16, True), TEXT, anchor="lm")
    text(d, (dx1 - 60, dy0 + 160), "▼", font(14), GREY, anchor="mm")
    callout(d, [dx0 + 176, dy0 + 138, dx1 - 36, dy0 + 182])
    # Optimieren
    d.ellipse([dx0 + 30, dy0 + 230, dx0 + 46, dy0 + 246], outline=TEXT, width=2)
    d.ellipse([dx0 + 34, dy0 + 234, dx0 + 42, dy0 + 242], fill=BLUE)
    text(d, (dx0 + 56, dy0 + 238), "Standard (Onlineveröffentlichung und Drucken)", font(15), TEXT, anchor="lm")
    # Optionen-Button
    d.rounded_rectangle([dx0 + 30, dy0 + 290, dx0 + 170, dy0 + 330], 6, fill=LGREY, outline=GREY, width=1)
    center(d, [dx0 + 30, dy0 + 290, dx0 + 170, dy0 + 330], "Optionen…", font(15, True), TEXT)
    badge(d, (dx0 + 100, dy0 + 390), 4, r=22)
    arrow(d, (dx0 + 100, dy0 + 365), (dx0 + 100, dy0 + 332))
    # Veröffentlichen / Abbrechen
    d.rounded_rectangle([dx1 - 320, dy1 - 60, dx1 - 180, dy1 - 20], 6, fill=BLUE)
    center(d, [dx1 - 320, dy1 - 60, dx1 - 180, dy1 - 20], "Veröffentlichen", font(15, True), WHITE)
    d.rounded_rectangle([dx1 - 160, dy1 - 60, dx1 - 40, dy1 - 20], 6, fill=LGREY, outline=GREY, width=1)
    center(d, [dx1 - 160, dy1 - 60, dx1 - 40, dy1 - 20], "Abbrechen", font(15), TEXT)
    callout(d, [dx1 - 326, dy1 - 66, dx1 - 174, dy1 - 14])
    hint(d, [150, 720, 1130, 762],
         "Schritt 4:  Dateityp = PDF, Name vergeben, optional „Optionen…“ – dann „Veröffentlichen“")
    img.save(os.path.join(HERE, "schritt4.png"))

    # ===== Schritt 5: Optionen-Dialog (was wird gespeichert)
    img, d = canvas((210, 213, 218))
    dx0, dy0, dx1, dy1 = 350, 140, 930, 640
    d.rectangle([dx0 + 8, dy0 + 8, dx1 + 8, dy1 + 8], fill=(170, 173, 178))
    d.rectangle([dx0, dy0, dx1, dy1], fill=WHITE, outline=(150, 153, 158), width=2)
    d.rectangle([dx0, dy0, dx1, dy0 + 44], fill=(245, 246, 248))
    text(d, (dx0 + 20, dy0 + 22), "Optionen", font(18, True), TEXT, anchor="lm")
    text(d, (dx0 + 30, dy0 + 80), "Veröffentlichen:", font(16, True), TEXT, anchor="lm")
    opts = [("Auswahl", False),
            ("Aktive(s) Blatt(Blätter)", True),
            ("Gesamte Arbeitsmappe", False),
            ("Tabelle", False)]
    y = dy0 + 120
    for label, sel in opts:
        d.ellipse([dx0 + 40, y, dx0 + 58, y + 18], outline=TEXT, width=2)
        if sel:
            d.ellipse([dx0 + 44, y + 4, dx0 + 54, y + 14], fill=BLUE)
        text(d, (dx0 + 70, y + 9), label, font(16, sel), TEXT, anchor="lm")
        y += 40
    callout(d, [dx0 + 34, dy0 + 114, dx1 - 40, dy0 + 152])
    text(d, (dx0 + 30, y + 20), "Tipp: „Aktive Blätter“ exportiert nur das Blatt", font(14), GREY, anchor="lm")
    text(d, (dx0 + 30, y + 44), "„Offerte“ – dank gesetztem Druckbereich genau", font(14), GREY, anchor="lm")
    text(d, (dx0 + 30, y + 68), "eine saubere A4-Seite.", font(14), GREY, anchor="lm")
    d.rounded_rectangle([dx1 - 220, dy1 - 56, dx1 - 120, dy1 - 20], 6, fill=BLUE)
    center(d, [dx1 - 220, dy1 - 56, dx1 - 120, dy1 - 20], "OK", font(15, True), WHITE)
    d.rounded_rectangle([dx1 - 110, dy1 - 56, dx1 - 20, dy1 - 20], 6, fill=LGREY, outline=GREY, width=1)
    center(d, [dx1 - 110, dy1 - 56, dx1 - 20, dy1 - 20], "Abbr.", font(14), TEXT)
    hint(d, [150, 720, 1130, 762],
         "Schritt 5 (optional):  Im Optionen-Dialog „Aktive Blätter“ wählen → OK")
    img.save(os.path.join(HERE, "schritt5.png"))

    # ===== Schritt 6: Fertig – PDF geöffnet
    img, d = canvas((90, 94, 100))
    # PDF-Viewer
    d.rectangle([300, 60, 980, H - 40], fill=WHITE, outline=(40, 40, 40), width=2)
    d.rectangle([300, 60, 980, 96], fill=(60, 63, 68))
    text(d, (320, 78), "Offerte_Kabel_95mm.pdf", font(15, True), WHITE, anchor="lm")
    # Inhalt (verkleinert)
    text(d, (330, 140), "MOBIL IN TIME", font(24, True), ORANGE, anchor="lm")
    d.rectangle([330, 200, 950, 226], fill=(31, 41, 51))
    text(d, (340, 213), "Pos   Menge   Beschreibung", font(12, True), WHITE, anchor="lm")
    yy = 226
    for r in range(3):
        if r % 2:
            d.rectangle([330, yy, 950, yy + 26], fill=(244, 246, 248))
        yy += 26
    d.rectangle([330, yy + 10, 950, yy + 44], fill=(252, 238, 227))
    text(d, (700, yy + 27), "Endbetrag (CHF)", font(13, True), TEXT, anchor="lm")
    text(d, (940, yy + 27), "14'490.45", font(14, True), TEXT, anchor="rm")
    # grüner Haken
    badge(d, (980, 120), "check", r=34, color=(46, 160, 90))
    hint(d, [150, 720, 1130, 762],
         "Fertig!  Das PDF wird gespeichert und geöffnet – versandfertig.", color=(46, 160, 90))
    img.save(os.path.join(HERE, "schritt6.png"))

    # ===== Alternative: Drucken -> Als PDF speichern
    img, d = canvas()
    rx = backstage(d, active="Drucken")
    text(d, (rx + 30, 150), "Drucken", font(26, True), TEXT, anchor="lm")
    text(d, (rx + 30, 210), "Drucker", font(15, True), GREY, anchor="lm")
    d.rounded_rectangle([rx + 30, 236, rx + 470, 280], 8, fill=WHITE, outline=GREY, width=2)
    text(d, (rx + 48, 258), "Microsoft Print to PDF", font(16, True), TEXT, anchor="lm")
    text(d, (rx + 440, 258), "▼", font(14), GREY, anchor="mm")
    callout(d, [rx + 24, 230, rx + 476, 286])
    # Druck-Button
    d.rounded_rectangle([rx + 30, 320, rx + 150, 364], 8, fill=EXCEL)
    center(d, [rx + 30, 320, rx + 150, 364], "Drucken", font(16, True), WHITE)
    badge(d, (rx + 520, 258), "A", r=22, color=BLUE)
    # Vorschau rechts
    d.rectangle([rx + 560, 210, rx + 760, 500], fill=WHITE, outline=GREY, width=2)
    text(d, (rx + 575, 240), "MOBIL IN TIME", font(13, True), ORANGE, anchor="lm")
    hint(d, [120, 720, 1160, 762],
         "Alternative:  Datei ▸ Drucken ▸ Drucker „Microsoft Print to PDF“ ▸ Drucken", color=BLUE)
    img.save(os.path.join(HERE, "alternative_drucken.png"))

    print("Bilder erzeugt in", HERE)
    for f in sorted(os.listdir(HERE)):
        if f.endswith(".png"):
            print("  -", f)


if __name__ == "__main__":
    main()
