# Arbeitsanweisungen für dieses Repository

## Stehender Auftrag: Aktivitäten-Tracker

**Immer wenn Burak Dateien in den Chat wirft — Outlook-Kalendereinträge
(`.ics`), E-Mails (`.eml`), Screenshots, Notizen, PDFs, Excel-Listen — ohne
weitere Anweisung Folgendes tun:**

1. Dateien nach `inbox/` kopieren.
2. `python3 src/aktivitaeten/cli.py` ausführen.
3. Die aktualisierte `output/Aktivitaeten.xlsx` mit `SendUserFile` zurückschicken.
4. Kurz zusammenfassen, **was neu dazukam** — Position, Datum, Titel, Kategorie,
   Gegenstelle, Potenzial — und was als Duplikat erkannt wurde.

Nicht nachfragen, ob er das will. Das ist der Normalfall. Nachfragen nur, wenn
eine Datei inhaltlich unklar ist (z. B. ein Screenshot ohne erkennbaren Bezug —
dann fragen, was darauf zu sehen ist, und die Antwort als Notiz mitgeben).

Wenn er mehrfach dieselbe Datei schickt: kommentarlos einlesen, die Pipeline
erkennt Duplikate über den SHA-256 selbst.

### Was dabei automatisch passiert

Jeder Eintrag wird einsortiert nach Datum und Uhrzeit, bekommt eine
**Positionsnummer**, wird einer Kategorie zugeordnet (Akquise, Kundentermin,
Beratung, Partner / Lieferant, Interner Termin, Messe / Event, Interne Arbeit,
E-Mail) und taucht überall auf: in der Tabelle, im Dashboard, im Tagebuch, bei
Bedarf in Pipeline und offenen Schritten. Details: `docs/aktivitaeten.md`.

### Grenzen, die einzuhalten sind

* **Das Repository ist öffentlich.** `inbox/`, `data/` und `output/` stehen in
  `.gitignore` und dürfen dort bleiben — die Termine enthalten Kundennamen,
  Mailadressen, Telefonnummern, Teams-Passcodes und Pipeline-Beträge. Diese
  Daten niemals committen, solange das Repository nicht auf *privat* steht.
* Nur den Code committen, nicht die Auswertung.
* Manuelle Korrekturen aus der Excel-Mappe niemals überschreiben — sie liegen
  in `data/registry.json` unter `korrekturen` und gewinnen immer.

## Sprache

Antworten und alle Dokumente auf Deutsch, Schweizer Schreibweise (ss statt ß).
