# Schlussbericht Netzqualitätsmessung — Satz und Wordvorlage

Der Schlussbericht *Gasthaus Kreuz, Zuzwil SG* wird vollständig per Python neu
gesetzt. Inhalt und Gestaltung sind dabei getrennt: `extract.py` liest den
Originalbericht in ein Inhaltsmodell, `build_report.py` setzt daraus das
Dokument nach dem Gestaltungssystem in `design.py`.

**Ergebnis:**
[`Schlussbericht_Kreuz_Zuzwil.docx`](../Schlussbericht_Kreuz_Zuzwil.docx) ·
[`Schlussbericht_Kreuz_Zuzwil.pdf`](../Schlussbericht_Kreuz_Zuzwil.pdf) ·
[`Vorlage_kabuu_Bericht.dotx`](../Vorlage_kabuu_Bericht.dotx)

62 Seiten, 101 Verzeichniseinträge, Inhalt zeichengenau wie im Original.

## Neu bauen

```bash
pip install python-docx Pillow
python3 src/report/make.py
```

Der Lauf macht alles: Inhalt auslesen, Logo erzeugen, Bericht setzen,
PDF exportieren, Seitenzahlen ins Inhaltsverzeichnis zurückschreiben,
Wordvorlage schreiben und den Inhalt gegen das Original prüfen.
`python3 src/report/lint.py` sucht anschliessend nach Satzfehlern.

| Datei | Zweck |
|-------|-------|
| `src/report/make.py` | Gesamtlauf, wiederholt bis die Seitenzahlen stabil sind |
| `src/report/extract.py` | Originalbericht → `build/content.json` |
| `src/report/design.py` | Farben, Masse, Typografie, OOXML-Werkzeug |
| `src/report/build_report.py` | Satz des Berichts und der Wordvorlage |
| `src/report/make_logo.py` | kabuu-Logo in allen benötigten Varianten |
| `src/report/make_pdf.py` | PDF-Export, Seitenzahlen, Seitenvorschau |
| `src/report/check.py` | Prüft, dass kein Zeichen des Originals fehlt |
| `src/report/lint.py` | Sucht Satzfehler im fertigen PDF |

## Was am Satz gemacht wurde

**Deckblatt.** Bildmarke, Berichtsart, Titel, Objekt und Messkampagne in einer
klaren Ordnung, darunter die Eckdaten und der Verwendungshinweis. Kopf- und
Fusszeile bleiben auf dem Deckblatt weg.

**Inhaltsverzeichnis.** Ein echtes Word-Verzeichnis über die Ebenen 1 und 2,
mit Punktführung, Sprungmarken und hinterlegten Seitenzahlen. Die Zahlen
stimmen im PDF wie in Word sofort; mit F9 rechnet Word sie jederzeit neu.
Ermittelt werden sie in zwei Durchgängen aus dem gesetzten PDF.

**Abstände.** Jeder Absatz trägt seine Abstände aus dem Gestaltungssystem
statt aus Leerzeilen. Überschriften hängen am folgenden Text, Bilder an ihrer
Legende, Tabellenzeilen brechen nicht mitten durch, Kopfzeilen von Tabellen
wiederholen sich auf jeder Folgeseite. Jedes Kapitel beginnt auf neuer Seite.

**Zahlenabstände.** Zwischen Zahl und Einheit steht ein geschütztes
Leerzeichen (`230 V`, `50 Hz`, `2,40 %`), Tausender werden mit Hochkomma
getrennt (`86’600 VA`), Bezeichner wie `MP‑1` und Verweise wie `Kapitel 11`
oder `EN 50160` brechen nicht um. In Tabellen stehen Zahlenspalten rechtsbündig
unter ihrem ebenfalls rechtsbündigen Spaltentitel, Symbolspalten zentriert.

**Tabellen.** Feste Spaltenbreiten, aus dem Inhalt gerechnet und nie schmaler
als das längste unteilbare Wort — kein Spaltentitel bricht mehr mitten im Wort.
Dunkle Kopfzeile, Zebrastreifen, Haarlinien statt Gitter, ruhige Innenränder.

**Hinweiskästen.** Vier Rollen mit fester Bedeutung: bestätigtes Ergebnis
(grün), Vorbehalt (amber), interner Hinweis (rot), Einordnung (blau).

**Logo.** Bildmarke auf dem Deckblatt, in der Kopfzeile jeder Seite und auf der
Schlussseite.

> **Logo austauschen:** Das Signet ist in `make_logo.py` aus Geometrie und
> Schrift nachgebaut, damit der Bericht ohne Bilddatei reproduzierbar bleibt.
> Wer das Originalasset einsetzen will, legt es als
> `assets/report/logo/kabuu_logo_original.png` ab — `make_logo.py` verwendet
> dann diese Datei und der Rest des Laufs bleibt unverändert.

## Wordvorlage

`Vorlage_kabuu_Bericht.dotx` trägt dieselbe Gestaltung ohne den Berichtsinhalt:
Deckblatt mit Platzhaltern, Kopf- und Fusszeile mit Bildmarke, die drei
Überschriftenebenen, eine Beispieltabelle, alle vier Hinweiskästen, Aufzählung,
nummerierte Liste und Formelblock. Doppelklick legt in Word ein neues Dokument
in diesem Look an.

## Prüfungen

Drei Prüfungen, alle grün:

- **Schema.** Beide Dateien bestehen die XSD-Prüfung gegen das OOXML-Schema —
  inklusive der vorgeschriebenen Reihenfolge der Eigenschaftselemente, an der
  Word streng ist und LibreOffice nicht.
- **Inhalt.** `check.py` vergleicht den sichtbaren Text mit dem Original und
  lässt nur die bewusst gesetzten typografischen Änderungen zu.
- **Satz.** `lint.py` liest das fertige PDF und meldet, was beim Durchblättern
  untergeht: Worttrennung in Tabellenzellen, verwaiste Restzeilen, fast leere
  Seiten, Löcher im Satz, Verzeichniseinträge mit falscher Seitenzahl,
  fehlende Kopf- oder Fusszeilen, Lücken in der Kapitelnummerierung und
  Abweichungen im Zahlensatz.

Zwei Stellen sind bewusst ausgenommen und deshalb in der Prüfung vermerkt: die
letzte Seite eines Kapitels darf kurz ausfallen, weil jedes Kapitel auf einer
neuen Seite beginnt; und in den Rechenblöcken wird nichts eingefügt, was die
Zeichenzahl ändert — dort richten Leerzeichen die Spalten aus.

## Dokumenteigenschaften

Titel, Verfasser, Gegenstand, Schlagwörter und Firma stehen in der Datei und
wandern in die PDF-Metadaten. Das PDF trägt zusätzlich 123 Lesezeichen, eines
je Überschrift.
