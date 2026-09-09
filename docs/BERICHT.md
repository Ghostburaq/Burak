# Schlussbericht Netzqualitätsmessung — Satz und Wordvorlage

Der Schlussbericht *Gasthaus Kreuz, Zuzwil SG* wird vollständig per Python neu
gesetzt. Inhalt und Gestaltung sind dabei getrennt: `extract.py` liest den
Originalbericht in ein Inhaltsmodell, `build_report.py` setzt daraus das
Dokument nach dem Gestaltungssystem in `design.py`.

## Drei Fassungen

Der Bericht erscheint in drei Fassungen aus derselben Quelle. Was sie
unterscheidet, steht ausschliesslich in `variants.py`.

| Fassung | Datei | Umfang |
|---------|-------|--------|
| Arbeitsfassung, mit Anhang C | [`Schlussbericht_Kreuz_Zuzwil.docx`](../Schlussbericht_Kreuz_Zuzwil.docx) · [PDF](../Schlussbericht_Kreuz_Zuzwil.pdf) | 62 Seiten, 101 Verzeichniseinträge |
| Zur Weitergabe, ohne Anhang C | [`Schlussbericht_Kreuz_Zuzwil_Kundenversion.docx`](../Schlussbericht_Kreuz_Zuzwil_Kundenversion.docx) · [PDF](../Schlussbericht_Kreuz_Zuzwil_Kundenversion.pdf) | 60 Seiten, 96 Verzeichniseinträge |
| Musterbericht, ohne Kundendaten | [`Musterbericht_Netzqualitaetsmessung.docx`](../Musterbericht_Netzqualitaetsmessung.docx) · [PDF](../Musterbericht_Netzqualitaetsmessung.pdf) | 62 Seiten, 101 Verzeichniseinträge |

Dazu die [`Wordvorlage`](../Vorlage_kabuu_Bericht.dotx) für künftige Berichte.

**Zur Weitergabe** fällt Anhang C weg — und mit ihm der Satz auf dem Deckblatt,
der ihn ankündigt; er ginge sonst ins Leere. Eine eigene Prüfung sucht in
dieser Fassung nach Formulierungen, die es nur im internen Anhang gibt, damit
nichts Internes beim Auftraggeber landet.

**Der Musterbericht** trägt den vollständigen Aufbau, gibt aber niemanden
preis. Der Inhalt der Arbeitsfassung ist zeichengenau der des Originals;
Seitenzahlen und Inhaltsverzeichnis werden je Fassung neu gerechnet.

## Wie der Musterbericht anonymisiert wird

Ersetzt wird alles, was Ort, Betrieb, Personen oder beteiligte Firmen benennt
(`anonymise.py`). Die technische Beschreibung, alle Messwerte, Rechenwege und
der Massnahmenkatalog bleiben — sie machen den Musterbericht erst brauchbar
und geben niemanden preis. Der Briefkopf von kabuu bleibt ebenfalls: der
Musterbericht ist ein eigenes Dokument von kabuu. Auf dem Deckblatt steht, was
ersetzt wurde und was nicht.

Ersetzt wird in **einem** Durchgang, längster Treffer zuerst. Das ist keine
Feinheit, sondern nötig: eine Ersetzung von «Kreuz» würde sonst aus
«Kreuzvergleich» «Musterbetriebvergleich» machen, und «Zuzwil» würde die
verschriebene Form «Zuzwill» im internen Anhang zerlegen.

**Bilder lassen sich nicht Wort für Wort anonymisieren.** Deshalb gilt in
`make_placeholders.py` eine strenge Regel statt einer Stichwortliste: ein Bild
wird nur übernommen, wenn sein vollständig ausgelesener Text keine einzige
identifizierende Angabe enthält. Von 18 Bildern besteht genau eines diese
Prüfung. Die übrigen werden durch gestaltete Platzhalterflächen in
Originalabmessung ersetzt, beschriftet mit dem, was sie zeigten.

Dass die Regel streng sein muss, zeigen die Funde: das Übersichtsschema trägt
den Betriebsnamen in der Titelzeile und die Errichterfirma der Photovoltaik in
einer Fussnote, die Sonnenuntergangs-Grafik die **Geokoordinaten des Objekts**.
Die Koordinaten hätte keine Namensliste gefunden. Die Aufnahmen der
Bilddokumentation zeigen die realen Räume des Betriebs; daran lässt sich
nichts anonymisieren.

## Neu bauen

```bash
pip install python-docx Pillow
python3 src/report/make.py                     # alle drei Fassungen
python3 src/report/make.py --variante muster   # nur den Musterbericht
```

Der Lauf macht alles: Inhalt auslesen, Logo und Platzhalter erzeugen,
alle Fassungen setzen,
PDF exportieren, Seitenzahlen ins Inhaltsverzeichnis zurückschreiben,
Wordvorlage schreiben, jede Fassung auf Satzfehler prüfen und den Inhalt der
Arbeitsfassung gegen das Original vergleichen.

| Datei | Zweck |
|-------|-------|
| `src/report/make.py` | Gesamtlauf über beide Fassungen |
| `src/report/extract.py` | Originalbericht → `build/content.json` |
| `src/report/variants.py` | Die drei Fassungen und was sie unterscheidet |
| `src/report/anonymise.py` | Ersetzungstabelle für den Musterbericht |
| `src/report/make_placeholders.py` | Prüft Bilder per Texterkennung, ersetzt was preisgibt |
| `src/report/corrections.py` | Sachliche Korrekturen am Ausgangstext |
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

**Abbildungen.** Im Ausgangsbericht stehen sie als 1, 4, 5, 2, 3 im Text — die
Anhänge wurden nachträglich eingefügt. Da keine Stelle im Text auf eine
Abbildungsnummer verweist, werden sie beim Satz in Lesereihenfolge
durchgezählt. In der Bilddokumentation stehen Messpunkt und Inhalt an einem
Tabulator, sodass die Werte untereinander beginnen.

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
  fehlende Kopf- oder Fusszeilen, Lücken in der Kapitel- und
  Abbildungsnummerierung, Abweichungen im Zahlensatz sowie den inneren
  Zusammenhalt der Datei — Verweise ohne Ziel, Bildbeziehungen ohne Datei,
  Listenbezüge ohne Definition. In der Fassung zur Weitergabe zusätzlich:
  keine Formulierung aus dem internen Anhang. Im Musterbericht zusätzlich:
  keine identifizierende Angabe — im Text **und**, per Texterkennung, in jedem
  eingebetteten Bild.

Zwei Stellen sind bewusst ausgenommen und deshalb in der Prüfung vermerkt: die
letzte Seite eines Kapitels darf kurz ausfallen, weil jedes Kapitel auf einer
neuen Seite beginnt; und in den Rechenblöcken wird nichts eingefügt, was die
Zeichenzahl ändert — dort richten Leerzeichen die Spalten aus.

## Nachgerechnet

Die 18 Rechenblöcke in Kapitel 10 wurden unabhängig nachgerechnet: Anschluss-
und Anlagenleistung, Frequenzordnung der Rundsteuersignale, Netzimpedanz aus
der Spannungsanhebung, Spannungsänderung durch Lastsprünge, Neutralleiterstrom
aus der Schieflast, Resonanzprüfung des Lichtstromkreises und die Strombilanz.
Alle Ergebnisse stimmen. Ebenso alle Querverweise auf Kapitel und Anhänge.

## Dokumenteigenschaften

Titel, Verfasser, Gegenstand, Schlagwörter und Firma stehen in der Datei und
wandern in die PDF-Metadaten. Das PDF trägt zusätzlich ein Lesezeichen je
Überschrift.
