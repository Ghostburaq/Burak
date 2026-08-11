# Aktivitäten-Pipeline

Dateien reinwerfen → strukturierte, sortierte Excel-Liste raus. Jeder weitere
Wurf aktualisiert dieselbe Liste, statt sie neu anzulegen.

```bash
pip install openpyxl
cp meine_termine/*.ics inbox/
python3 src/aktivitaeten/cli.py
# -> output/Aktivitaeten.xlsx  +  output/report.md
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

| Blatt | Inhalt |
|---|---|
| **Aktivitäten** | Alle Einträge, chronologisch, 31 Spalten, Filter + fixierte Kopfzeile |
| **Tagesübersicht** | Pro Tag: Anzahl, erste/letzte Uhrzeit, erfasste Stunden, Themen |
| **Pipeline** | Nur Vertriebsrelevantes, nach Potenzial sortiert, mit Summenzeile |
| **Kontakte** | Pro Firma: Kontaktdaten, erster/letzter Kontakt, offenes Potenzial |
| **Quellen** | Jede eingelesene Datei mit Hash, Grösse, Importzeitpunkt, Anzahl Importe |

Kategorien sind farbcodiert: Akquise, Kundentermin, Beratung,
Partner / Lieferant, Interner Termin, Messe / Event, Interne Arbeit, E-Mail.

## Dedup und Updates

`data/registry.json` ist das Gedächtnis der Pipeline.

* **Gleiche Datei nochmal** → über SHA-256 erkannt, wird übersprungen
  (nur der Zähler im Blatt *Quellen* steigt).
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
| `src/aktivitaeten/felder.py` | Heuristiken für Firma, Kontakt, Beträge, Kategorie |
| `src/aktivitaeten/registry.py` | Dedup, Merge, Persistenz |
| `src/aktivitaeten/excel.py` | Formatierte Mappe |
| `src/aktivitaeten/konfig.py` | Stellschrauben |

## Datenschutz

`inbox/`, `data/` und `output/` sind in `.gitignore` — dieses Repository ist
öffentlich, die Termine enthalten Kundennamen, Mailadressen, Telefonnummern,
Teams-Passcodes und Pipeline-Beträge. Soll das versioniert werden, das
Repository vorher auf *privat* stellen.
