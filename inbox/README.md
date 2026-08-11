# inbox/ — hier alles reinwerfen

Alles, was in diesen Ordner kommt, wird beim nächsten Lauf eingelesen:

| Format | wird gelesen als |
|---|---|
| `.ics` / `.ical` | Kalendertermin (Outlook, Teams, Messe-Export) |
| `.eml` | E-Mail inkl. Absender, Datum, Text, Abwesenheitserkennung |
| `.png`, `.jpg`, … | Screenshot — Zeitpunkt aus Dateiname oder EXIF |
| `.txt`, `.md` | freie Notiz |
| `.pdf`, `.docx` | Dokument (Text wird gelesen, wenn möglich) |
| `.xlsx` | Excel-Liste mit Spalten `Datum` und `Titel` |

Danach:

```bash
python3 src/aktivitaeten/cli.py
```

**Notiz zu einem Screenshot** — Textdatei mit gleichem Namen daneben legen:

```
inbox/screenshot_2026-08-11_1420.png
inbox/screenshot_2026-08-11_1420.txt      <- "Offerte Green Datacenter versendet"
```

oder direkt beim Import:

```bash
python3 src/aktivitaeten/cli.py inbox/screenshot.png --notiz "Offerte versendet"
```

Dieselbe Datei mehrfach einwerfen ist unproblematisch — sie wird über ihren
Hash erkannt und nicht doppelt gezählt.

**Ohne Datei erfassen:** direkt im Blatt «Eingabe» der Mappe
`output/Aktivitaeten.xlsx` tippen — Datum und Titel genügen. Beim nächsten Lauf
wandert die Zeile in die Hauptliste. Korrekturen an bestehenden Zeilen einfach
im Blatt «Aktivitäten» überschreiben; sie bleiben dauerhaft erhalten.
Details: [`docs/aktivitaeten.md`](../docs/aktivitaeten.md).

> Der Inhalt dieses Ordners wird **nicht** eingecheckt (siehe `.gitignore`),
> weil das Repository öffentlich ist.
