# Aktivitäten-Pipeline

Dateien reinwerfen → strukturierte, sortierte Excel-Liste raus. Jeder weitere
Wurf aktualisiert dieselbe Liste, statt sie neu anzulegen.

```bash
pip install openpyxl
cp meine_termine/*.ics inbox/
./aktualisieren.sh                    # oder: python3 src/aktivitaeten/cli.py
# -> output/Aktivitaeten.xlsx  +  output/report.md
```

`./aktualisieren.sh` nimmt auch Pfade direkt entgegen und legt die Dateien
dabei in `inbox/` ab:

```bash
./aktualisieren.sh ~/Downloads/*.ics
```

## Was erkannt wird

| Eingabe | Ergebnis |
|---|---|
| `.ics` (Outlook / Teams / Messe) | Datum, Von/Bis, Dauer, Ort, Organisator, Teilnehmer, Teams-Link |
| `.eml` | Absender, Empfänger, Zeitpunkt, Betreff (ohne `AW:`/`[EXTERNAL]`), Text; Abwesenheitsnotizen inkl. Rückkehrdatum |
| Screenshot / Bild | Zeitpunkt aus Dateiname oder EXIF, Notiz aus Sidecar-Datei |
| `.txt` / `.md` | freie Notiz als eigener Eintrag |
| `.pdf` / `.docx` | Textinhalt, sofern lesbar |

Aus dem Freitext werden zusätzlich gezogen: Firma, Ansprechpartner, E-Mail,
Telefon, Website sowie die CRM-Felder `Status`, `Nächster Schritt`, `Bedarf`,
`Hauptprodukt`, `Wahrscheinlichkeit`, `Wert`, `Potenzial`, `Gew. Forecast`,
`Follow-up`.

Der angehängte Teams-Block (Einwahlnummern, Passcodes, Konferenz-IDs,
Rechtstexte) wird abgeschnitten, bevor Notizen und Kontaktdaten gelesen werden
— sonst landet die Konferenz-Einwahlnummer als Telefonnummer des Kunden in der
Liste.

## Die Excel-Mappe

Drei Blätter — mehr braucht es nicht.

| Blatt | Inhalt |
|---|---|
| **Dashboard** | Kennzahlen, zwei Diagramme, Zusammenfassung und Tagebuch in Fliesstext, Pipeline, offene Schritte |
| **Aktivitäten** | Alle Einträge als echte Excel-Tabelle — 12 sichtbare Spalten, 20 weitere eingeklappt |
| **Eingabe** | Leeres Formular zum Selbst-Eintippen |

### Dashboard

* **Kennzahlen** (Aktivitäten, Tage, Stunden, Kundenkontakte, Potenzial, offene
  Schritte) sind Formeln auf die Aktivitäten-Tabelle — sie rechnen sofort mit,
  wenn dort etwas geändert wird.
* **Diagramme**: Stunden je Kategorie und Aktivitäten je Tag, beide an den
  Auswertungsblöcken darunter hängend.
* **Tagebuch**: zu jedem Tag ein geschriebener Absatz — wie viele Aktivitäten,
  worauf der Schwerpunkt lag, was nach aussen ging, was vor Ort war, was intern
  lief und was offen blieb. Darunter die Einzelvorgänge mit Zeit, Firma,
  Potenzial und nächstem Schritt.

### Aktivitäten

Eine echte Excel-Tabelle (`Aktivitaeten`): Filterknöpfe, Zebrastreifen,
strukturierte Bezüge. Sichtbar sind Pos., Datum, Zeit, Std., Kategorie, Titel,
Firma, Kontakt, Status, Nächster Schritt, Potenzial CHF und Notizen.

**Pos.** ist die laufende Nummer in der chronologischen Liste — dieselbe Nummer
steht im Dashboard beim Tagebuch, in der Pipeline und bei den offenen Schritten,
sodass sich jede Zeile sofort wiederfinden lässt. Kommt ein Termin dazwischen
dazu, wird neu durchnummeriert; der dauerhafte Anker einer Zeile ist die
(eingeklappte) Spalte **ID**.

Die übrigen 20 Spalten (E-Mail, Telefon, Ort, Teilnehmer, Bedarf, Wert,
Wahrscheinlichkeit, Quelle, ID …) sind **eingeklappt, nicht gelöscht** — über
das `+` am Spaltenkopf jederzeit sichtbar. Kategorien sind farbcodiert.

## Excel als Eingabe — selbst eintippen und korrigieren

Die Mappe ist nicht nur Ergebnis, sondern auch Eingabemaske. Beide Wege werden
beim nächsten Lauf automatisch zurückgelesen, *bevor* die Datei neu geschrieben
wird — es geht nichts verloren.

### 1. Neue Aktivität von Hand: Blatt «Eingabe»

Eine Zeile pro Vorgang, Pflicht sind nur **Datum** und **Titel**. Für Kategorie
und Status gibt es Auswahllisten, die ID-Spalte bleibt leer (vergibt das Tool).

```bash
python3 src/aktivitaeten/cli.py
```

Die Zeile wandert ins Blatt «Aktivitäten», das Eingabeblatt ist wieder leer.
`Potenzial CHF` versteht `240000` genauso wie `240'000`. Felder, die im
Eingabeblatt fehlen (Bedarf, Wert, Wahrscheinlichkeit …), lassen sich danach in
den eingeklappten Spalten der Tabelle nachtragen.

### 2. Bestehende Zeile korrigieren: direkt im Blatt «Aktivitäten»

Zelle überschreiben, speichern, Tool laufen lassen. Die Änderung wird als
**Korrektur zur ID** gespeichert und liegt ab dann über den automatisch
gelesenen Daten — auch wenn dieselbe Einladung später nochmal importiert wird.
Die Automatik überschreibt eine Korrektur nie.

* Leere Zelle = *nicht angefasst* (überschreibt nichts).
* Ein einzelnes `-` in der Zelle = Feld bewusst leeren.
* Die Spalte **ID** ist der Anker — nicht löschen und nicht ändern.
* Das Dashboard ist berechnet; Änderungen dort werden nicht gelesen und beim
  nächsten Lauf überschrieben.

### 3. Fremde Excel-Liste importieren

Eine beliebige `.xlsx` in `inbox/` legen: das erste Blatt, dessen Kopfzeile
mindestens `Datum` und `Titel` enthält, wird eingelesen. Die Spaltennamen dürfen
denen der Mappe entsprechen — Gross-/Kleinschreibung, Umlaute und `*` sind egal.

> Die Datei muss beim Lauf in Excel **geschlossen** sein, sonst lässt sie sich
> nicht neu schreiben. Das Tool sagt es, falls es passiert.
> Rückimport abschalten: `--ohne-excel-rueckimport`.

## Dedup und Updates

`data/registry.json` ist das Gedächtnis der Pipeline.

* **Gleiche Datei nochmal** → über SHA-256 erkannt, wird übersprungen
  (im Dashboard unter *Datenherkunft* mitgezählt).
* **Gleicher Termin, andere Datei** (z. B. aktualisierte Einladung) → wird über
  die Kalender-UID bzw. `Message-ID` zusammengeführt. Die inhaltsreichere
  Version gewinnt, fehlende Felder werden aus der anderen ergänzt, `revision`
  zählt hoch.
* **Neu einlesen** von Grund auf: `--neu-aufbauen`.

## Anpassen

Alle Stellschrauben liegen in `src/aktivitaeten/konfig.py`:

```python
EIGENE_DOMAINS   = {"mobilintime.com"}          # gilt nie als Gegenstelle
PARTNER_DOMAINS  = {"aggreko.de"}               # -> Kategorie "Partner / Lieferant"
FIRMEN_ALIASE    = {"zuerich": "Stadt Zürich"}  # sauberer Name je Mail-Domain
KATEGORIE_REGELN = [(r"loadbank", "Partner / Lieferant")]   # eigene Regeln zuerst
```

## Aufbau

| Datei | Zweck |
|---|---|
| `src/aktivitaeten/cli.py` | Einstieg: einlesen, Registry pflegen, schreiben |
| `src/aktivitaeten/icsfile.py` | iCalendar-Parser (Zeilenentfaltung, Zeitzonen, Ganztagstermine) |
| `src/aktivitaeten/emlfile.py` | E-Mail-Parser |
| `src/aktivitaeten/andere.py` | Screenshots, Notizen, PDF/Word |
| `src/aktivitaeten/excelimport.py` | Rückweg: Blatt «Eingabe» und manuelle Korrekturen |
| `src/aktivitaeten/felder.py` | Heuristiken für Firma, Kontakt, Beträge, Kategorie |
| `src/aktivitaeten/registry.py` | Dedup, Merge, Persistenz |
| `src/aktivitaeten/excel.py` | Dashboard, Tabelle, Eingabeblatt |
| `src/aktivitaeten/bericht.py` | Erzeugt den Fliesstext (Zusammenfassung, Tagebuch) |
| `src/aktivitaeten/konfig.py` | Stellschrauben |

## Datenschutz

`inbox/`, `data/` und `output/` sind in `.gitignore` — dieses Repository ist
öffentlich, die Termine enthalten Kundennamen, Mailadressen, Telefonnummern,
Teams-Passcodes und Pipeline-Beträge. Soll das versioniert werden, das
Repository vorher auf *privat* stellen.
