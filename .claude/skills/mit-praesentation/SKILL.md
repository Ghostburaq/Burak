---
name: mit-praesentation
description: Erstellt PowerPoint-Präsentationen im offiziellen Design der Mobil in Time AG (An Aggreko Company). Diesen Skill IMMER aktivieren, wenn Burak eine Präsentation, ein Deck, Folien, eine Kundenpräsentation, ein Briefing, ein Pitch-Deck, eine Schulungsunterlage oder eine PPTX für Mobil in Time, MiT, Aggreko oder den Bereich Strom Schweiz verlangt. Auch triggern bei "mach mir Folien dazu", "pack das in eine Präsentation", "Deck für den Kunden", "Folien für den Termin", "im Firmendesign", "MiT-Design", "mit unserer Vorlage", oder wenn ein bestehendes Deck ins MiT-Design überführt werden soll. Vor dem allgemeinen pptx-Skill verwenden, sobald es um MiT-Inhalte geht.
---

# MiT-Präsentation

Baut Decks auf dem Original-Master der Mobil in Time AG. Nie ein Deck von Null
gestalten und nie Farben oder Schriften erfinden: Der Master in
`assets/mit_vorlage.pptx` bringt Hintergrundgrafiken, Logo und Theme-Schriften
mit, `assets/mit_deck.py` bringt die fertigen Bausteine.

## Vorgehen

1. **Inhalt zuerst klären.** Wer ist das Publikum (Kunde, Aggreko, intern, EVU,
   Rechenzentrum)? Was ist die eine Botschaft? Ohne das keine Folien bauen.
   Fehlt eine Pflichtangabe, genau eine gezielte Rückfrage stellen.
2. **Storyline in Stichworten** an Burak geben, bevor gebaut wird, wenn das Deck
   länger als sechs Folien wird. Bei kurzen Decks direkt bauen.
3. **Deck mit `mit_deck.py` generieren.** Skript in den Scratchpad schreiben,
   `assets/` daneben legen oder per `sys.path` einbinden.
4. **Visuell prüfen.** Wenn LibreOffice Impress verfügbar ist: nach PDF wandeln,
   Folien als PNG rendern und selbst anschauen. Umbrüche, Überläufe und
   Kollisionen mit dem Logo oder dem grauen Dreieck korrigieren, bevor
   ausgeliefert wird. Ist Impress nicht installiert:
   `apt-get update -q && apt-get install -y -q libreoffice-impress`.
5. **Ausliefern** als .pptx, PDF nur als Kontrollbeilage.

## Bausteine

```python
import sys; sys.path.insert(0, "<pfad>/assets")
from mit_deck import Deck, RED, DARK, LIGHT, cols

d = Deck("out.pptx", footer="MiT Strom · Projekt · 27.09.2026")

d.cover(["Zeile eins,", "Zeile zwei"], "Untertitel",
        eyebrow="Mobil in Time AG · An Aggreko Company · Strom Schweiz",
        author="Burak Ücöz · Sales Engineer Power · 27.09.2026",
        stats=[("29", "Projekte"), ("145", "Kontakte")])   # stats stehen im roten Keil

s = d.content("01 · Ausgangslage", "Titel der Folie")      # setzt Fusszeile und Nummer selbst
d.cards(s, [("Kachel A", ["Text."]), ("Kachel B", ["Text."], RED)], cols_n=3)
d.kpis(s, [("29", "Projekte"), ("43 %", "mit Mängeln")])
d.steps(s, [("01", "Datenbasis", ["Text."]), ("02", "Recherche", ["Text."])])
d.table(s, rows, colw=[3.0, 2.9, 3.2, 3.0], y=2.05, h=4.2)
d.band(s, 5.05, "Aussage.", bold_prefix="Kernaussage:", fill=DARK)
d.notes(s, "Sprechnotiz.")

d.section("Kapitel", ["Abschnittstitel"])                   # rotes Parallelogramm
d.closing("Der eine Hebel", ["Satz eins.", "Satz zwei."],
          ["Burak Ücöz · Sales Engineer Power", "Mobil in Time AG · An Aggreko Company"])
d.save(title="...", author="Burak Ücöz")
```

`assets/beispiel.py` baut ein Deck, das jeden Baustein einmal zeigt. Als
Startpunkt kopieren.

## Designregeln

Details und Masse stehen in `reference/design.md`. Das Wichtigste:

- **Rot E00036 ist Signalfarbe, kein Dekor.** Pro Folie höchstens ein rotes
  Element mehr als nötig. Rote Kacheln nur für das, worauf der Blick soll.
- **Kacheln sind dunkelgrau 58595B**, Text darauf weiss. Helle Bänder F2F2F2
  für Randbemerkungen.
- **Titel in Alata, Fliesstext in IBM Plex Sans.** Nie überschreiben, das sind
  die Theme-Schriften des Masters.
- **Raster:** Inhalt von 0.47" bis 12.40", Titelzone ab 1.74" (rechts vom roten
  Streifen, endet vor dem Logo bei 10.69"). Unten rechts liegt ein graues
  Dreieck, deshalb nichts über 12.40" und nichts unter 6.70" platzieren.
- **Eine Aussage pro Folie**, im Titel als Satz. Keine Bulletfriedhöfe.
- Keine Emojis, keine Gedankenstriche als Stilmittel, Schweizer Schreibweise
  (ss statt ß). Deutschland und Österreich: ß nach deutscher Rechtschreibung.

## Inhaltliche Leitplanken

- **Keine erfundenen Produktdaten.** Leistungswerte, Verbrauchszahlen und
  Mietpreise nur aus einer gelieferten Quelle. Sonst als Lücke markieren:
  "Wert fehlt, aus Datenblatt ergänzen".
- **kVA und kW sauber trennen**, bei Generatoren Prime oder Standby angeben,
  bei BESS C-Rate und nutzbare Kapazität statt Nennkapazität.
- **Normen beim ersten Nennen vollständig** (EN 50160, IEC 61000-4-30 Klasse A,
  SN 411000/NIN), danach Kurzform.
- **Kundennamen, Einkaufspreise und Margen** gehören nicht in externe Decks.
  Referenzprojekte anonymisieren ("EVU in der Ostschweiz"), bis Burak freigibt.
- Kunden aus der Romandie oder dem Tessin: Deck auf Französisch bzw.
  Italienisch. Rechenzentren und internationale Konzerne: fragen, ob Englisch.

## Fallstricke

- **Laufzeitlänge der Titel:** über 46 Zeichen schaltet `content()` auf 22 pt.
  Titel über zwei Zeilen kollidieren nicht mit dem roten Strich, sehen aber
  gedrängt aus. Kürzer formulieren schlägt kleiner setzen.
- **Schlussfolie:** Text sitzt im roten Parallelogramm. Zeilen über rund
  30 Zeichen brechen um und zerstören den Rhythmus.
- **Tabellen:** ab zehn Zeilen auf 11 pt gehen, ab zwölf Zeilen auf 10.5 pt und
  Zeilenhöhe 0.375". Mehr als zwölf Zeilen: splitten.
- **Schriften:** Alata und IBM Plex Sans müssen auf dem Zielrechner installiert
  sein. In der Server-PDF-Vorschau fehlen sie, das ist nur ein Vorschauartefakt.
  Falls Burak sie nicht hat, im ganzen Deck auf Calibri umstellen.
