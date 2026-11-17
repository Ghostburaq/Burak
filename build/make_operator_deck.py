# -*- coding: utf-8 -*-
"""Operator-Bedienanleitung Sigma Unity, ZRH12.
Code einfuegen, Code bearbeiten, Test laden, Test starten."""
import sys, os
SKILL = ("/root/.claude/skills/synced/"
         "986ad732-c06e-46ed-b36f-6e48fa5d096e_107254f6-d9db-4589-81cb-fc5752ed387b/"
         "mit-praesentation/assets")
sys.path.insert(0, SKILL)
from mit_deck import (Deck, RED, DARK, DARKER, LIGHT, BLACK, WHITE, SOFT, LINE,
                      F_TITLE, F_BODY, L, R, W, BODY_TOP, BODY_BOTTOM, cols)
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

IMG = "/home/user/Burak/build/op_assets"
OUT = "/home/user/Burak/ZRH12_Unity_Bedienanleitung_Operator.pptx"
MONO = "Consolas"

d = Deck(OUT, footer="MiT Strom · ZRH12 Winterthur · Sigma Unity · 17.11.2026")


def liste(s, x, y, w, items, step=0.80, bs=12.5, hs=13.5, size=0.52):
    """Nummerierte Schrittliste, linksbuendig."""
    for i, (head, body) in enumerate(items):
        yy = y + i * step
        d.badge(s, x, yy, size, str(i + 1), RED, 13)
        tf = d.tb(s, x + size + 0.22, yy - 0.04, w - size - 0.22, 0.42)
        p = tf.paragraphs[0]; p.line_spacing = 1.0
        d.run(p, head, hs, BLACK, F_BODY, bold=True)
        if body:
            tf = d.tb(s, x + size + 0.22, yy + 0.33, w - size - 0.22, 0.46)
            p = tf.paragraphs[0]; p.line_spacing = 1.05
            d.run(p, body, bs, DARK)


def code(s, x, y, w, lines, fs=15, h=None, fill=DARKER):
    """Dunkler Codeblock in Festbreitenschrift."""
    h = h or (0.34 + 0.30 * len(lines))
    d.rect(s, x, y, w, h, fill)
    tf = d.tb(s, x + 0.26, y + 0.17, w - 0.5, h - 0.3)
    for i, ln in enumerate(lines):
        p = d.para(tf, first=(i == 0), space_before=0 if i == 0 else 3, line=1.0)
        d.run(p, ln, fs, WHITE, MONO)
    return h


def pic(s, name, x, y, w=None, h=None):
    kw = {}
    if w: kw['width'] = Inches(w)
    if h: kw['height'] = Inches(h)
    return s.shapes.add_picture(os.path.join(IMG, name), Inches(x), Inches(y), **kw)


# ---------------------------------------------------------------- 1 Titel
d.cover(["Testprogramm einfügen,", "bearbeiten, laden, starten"],
        "Bedienanleitung für den Operator · Sigma Unity",
        eyebrow="Mobil in Time AG · An Aggreko Company · ZRH12 Winterthur",
        author="Burak Ücöz · Project Manager Switzerland · 17.11.2026",
        stats=[("4", "Schritte"), ("10", "Minuten")])

# ---------------------------------------------------------------- 2 Ueberblick
s = d.content("00 · Überblick", "Vier Schritte, mehr ist es nicht")
d.steps(s, [
 ("01", "Code einfügen",  ["Aus der Datei kopieren", "und in Unity einsetzen."]),
 ("02", "Code prüfen",    ["Speichern. Die Fehlerzeile", "unten muss leer bleiben."]),
 ("03", "Test laden",      ["Auf Load wechseln und", "den Automatikmodus wählen."]),
 ("04", "Test starten",    ["Aufzeichnung ein,", "dann den Lauf starten."]),
])
d.band(s, 5.55, "Nie aus einer PDF oder aus Word kopieren. Nur aus der Datei selbst. "
                "Sonst zerbricht das Zeichen im Leistungsfaktor und Unity meldet einen Fehler.",
       bold_prefix="Die eine Regel:", fill=RED, h=1.05, fs=14)
d.notes(s, "Reihenfolge einhalten. Schritt 2 nicht ueberspringen.")

# ---------------------------------------------------------------- 3 Einfuegen
s = d.content("01 · Code einfügen", "Aus der Datei nach Unity, in sechs Handgriffen")
pic(s, "editor.png", 9.02, 2.08, w=3.35)
liste(s, L, 2.18, 8.35, [
 ("ZIP entpacken", "Rechtsklick, Alle extrahieren. Nicht im ZIP arbeiten."),
 ("Datei in Notepad öffnen", "Rechtsklick auf die .tst, Öffnen mit, Editor."),
 ("Alles markieren und kopieren", "Strg + A, dann Strg + C."),
 ("In Unity: Setup, dann Create/Edit Test Script", "Der Editor liegt im Menü Setup."),
 ("Namen vergeben und Code einsetzen", "Im Feld Script den Namen tippen. Dann ins grosse "
  "Feld klicken, Strg + A, Strg + V."),
 ("Speichern", "Diskettensymbol rechts neben dem Feld Script."),
])
d.notes(s, "Strg+A im grossen Feld ersetzt den alten Inhalt vollstaendig.")

# ---------------------------------------------------------------- 4 Bearbeiten
s = d.content("02 · Code bearbeiten", "Jede Zeile ist ein Befehl, eine Zeile pro Schritt")
h = code(s, L, 2.15, 7.30, ["Load  187kw 1cosØ 00:00:00 No",
                            "Delay  00:00:17"], fs=17)
yy = 2.15 + h + 0.28
for lab, txt in [("187kw", "Laststufe in kW. Diese Zahl änderst du, wenn die Last anders sein soll."),
                 ("1cosØ", "Leistungsfaktor. Bei allen ZRH12-Programmen immer 1."),
                 ("00:00:00", "Rampenzeit des Schritts. Bleibt auf null."),
                 ("No", "Lastkorrektur aus. Bleibt auf No."),
                 ("Delay 00:00:17", "Haltezeit danach, Stunden:Minuten:Sekunden.")]:
    tf = d.tb(s, L, yy, 2.05, 0.34)
    d.run(tf.paragraphs[0], lab, 13, RED, MONO, bold=True)
    tf = d.tb(s, L + 2.15, yy, 5.15, 0.40)
    p = tf.paragraphs[0]; p.line_spacing = 1.05
    d.run(p, txt, 12, DARK)
    yy += 0.52

d.rect(s, 8.00, 2.15, 4.40, 4.30, LIGHT)
tf = d.tb(s, 8.30, 2.42, 3.80, 0.44)
d.run(tf.paragraphs[0], "So änderst du etwas", 15, BLACK, F_BODY, bold=True)
liste(s, 8.30, 3.05, 3.80, [
 ("Zeile anklicken", "Direkt im grossen Feld tippen."),
 ("Zahl ändern", "Nur die Zahl, nicht die Einheit."),
 ("Speichern", "Diskettensymbol drücken."),
 ("Fehlerzeile lesen", "Leer heisst: in Ordnung."),
], step=0.80, size=0.44, hs=12.5, bs=11)
d.notes(s, "Einheiten und Leerzeichen nie anfassen. Nur Zahlen aendern.")

# ---------------------------------------------------------------- 5 Befehle
s = d.content("02 · Code bearbeiten", "Die sieben Befehle, die vorkommen")
d.table(s, [
 ["Zeile", "Was sie macht", "Darf geändert werden"],
 ["Capture  On", "Aufzeichnung einschalten. Immer die erste Zeile.", "nein"],
 ["Section  Heatrun", "Name des Abschnitts im Bericht.", "Name ja"],
 ["Instrumentation  Full", "Alle Messwerte aufzeichnen.", "nein"],
 ["Load  187kw 1cosØ 00:00:00 No", "Last anlegen. Zahl vor kw ist die Laststufe.",
  "nur die Laststufe"],
 ["Delay  00:00:17", "Haltezeit, bis der nächste Schritt kommt.", "ja"],
 ["Reject", "Last abwerfen. Steht am Ende.", "nein"],
 ["Capture  Off", "Aufzeichnung aus. Immer die letzte Zeile.", "nein"],
 ["' Text", "Kommentar. Wird nicht ausgeführt.", "ja"],
], colw=[3.5, 5.6, 2.3], y=2.05, h=3.70, fs=11.5)
d.band(s, 5.95, "Zwischen Befehl und Wert stehen zwei Leerzeichen, zwischen den Werten eines. "
                "Diese Abstände nicht verändern.", fill=LIGHT, h=0.80, fs=13)

# ---------------------------------------------------------------- 6 Fehlerzeile
s = d.content("02 · Code bearbeiten", "Die rote Zeile unten sagt, was klemmt")
pic(s, "fehler.png", L, 2.10, w=11.93)
d.cards(s, [
 ("expected units", ["Das Zeichen im Leistungsfaktor ist falsch.",
                     "Datei frisch aus dem ZIP holen,",
                     "nicht aus einer PDF kopieren."], RED),
 ("expected number", ["An einer Stelle steht keine Zahl.",
                      "Zeile mit der angegebenen Nummer",
                      "mit der Vorlage vergleichen."]),
 ("Keine rote Zeile", ["Alles in Ordnung.",
                       "Speichern und weiter",
                       "zu Schritt 3."]),
], cols_n=3, y=3.55, h=2.20)
d.notes(s, "Die Zeilennummer in der Meldung zaehlt ab der ersten Zeile der Datei.")

# ---------------------------------------------------------------- 7 Laden
s = d.content("03 · Test laden", "Auf die Seite Load wechseln und Automatik wählen")
pic(s, "modus.png", 10.75, 2.10, h=3.55)
liste(s, L, 2.22, 9.90, [
 ("Oben auf Load klicken", "Der Arbeitsplatz während des Tests."),
 ("Rechte Leiste: Symbol A", "A steht für den automatischen Lauf. Darunter das Symbol "
  "für Skript, ganz unten M für Motoranlauf."),
 ("Gespeichertes Skript wählen", "Den Namen, den du in Schritt 1 vergeben hast."),
 ("Supply on Test kontrollieren", "3,5 MVA, 2800 kW, cos φ 0,8, 400 V, 50 Hz. "
  "Steht oben rechts neben der Uhr."),
], step=0.90)
d.band(s, 6.05, "Stimmt der Supply on Test nicht, stimmen alle Prozentwerte nicht und der "
                "Bericht ist unbrauchbar.", bold_prefix="Vor dem Start prüfen:",
       fill=DARK, h=0.65, fs=12.5)

# ---------------------------------------------------------------- 8 Starten
s = d.content("04 · Test starten", "Erst aufzeichnen, dann fahren")
pic(s, "aufnahme.png", L, 2.15, w=5.60)
pic(s, "startstop.png", 6.45, 2.15, w=4.60)
liste(s, L, 4.38, 5.80, [
 ("Aufzeichnung einschalten", "Der runde Knopf oben. Die Uhr daneben muss laufen."),
 ("Fluke parallel starten", "Ohne Zweitmessung kein anerkannter Nachweis."),
], step=0.78)
liste(s, 6.45, 4.38, 5.90, [
 ("Lauf starten", "Grünes I. Das Programm läuft die Schritte selbst ab."),
 ("Abbruch jederzeit", "Rotes O. Last ist sofort weg. Lüfter weiterlaufen lassen."),
], step=0.78)
d.band(s, 5.98, "Beide roten O nehmen die Last sofort weg. Vor dem Start dem zweiten "
                "Mann zeigen, wo sie liegen.",
       bold_prefix="Notfall:", fill=RED, h=0.72, fs=13)

# ---------------------------------------------------------------- 9 Schluss
d.closing("Die Reihenfolge",
          ["Einfügen. Prüfen.", "Laden. Starten.",
           "Nie aus Word kopieren."],
          ["Burak Ücöz · Project Manager Switzerland",
           "Mobil in Time AG · An Aggreko Company"])

d.save(title="Sigma Unity Bedienanleitung fuer den Operator, ZRH12",
       author="Burak Ücöz")
print("PPTX geschrieben:", OUT, os.path.getsize(OUT), "Bytes")
