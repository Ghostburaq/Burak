# Injektions-Tracker

Persönlicher Tracker für Burak 🐯 und Aileen 🦁 — pro Eintrag eine Zeile
Testosteron und eine Zeile Primobolan, mit Countdown bis zur nächsten
Injektion.

## Funktionen

- **Countdown pro Person** — zeigt Restzeit, Datum/Uhrzeit der nächsten
  Injektion und den Fortschritt im laufenden Intervall.
  Status: *Im Plan* (grün) → *Bald* (letzte 12 Std, gelb) → *Fällig* (rot).
- **Intervall umschaltbar**: 2 / 2,5 / 3 / 3,5 / 4 Tage. Voreingestellt sind
  3 Tage; weil Uhrzeiten mitgespeichert werden, rechnet z. B. 2,5 Tage exakt
  mit 60 Stunden.
- **Eintragen** mit Datum, Uhrzeit, ml je Substanz, Injektionsstelle
  (für die Rotation) und Notiz. Voreingestellte Mengen:
  Burak 1,5 ml Testosteron / 1 ml Primobolan, Aileen 1 ml / 1 ml.
- **Verlauf** je Person, jeweils mit dem tatsächlichen Abstand zum
  vorherigen Eintrag (z. B. „+3,1 Tage“).
- **Summen**: Testosteron und Primobolan der letzten 7 Tage, Gesamtmenge der
  letzten 30 Tage.
- **JSON kopieren / einfügen** zum Sichern oder Umziehen der Daten.

## Dateien

| Datei | Zweck |
| --- | --- |
| `tracker.html` | Quelle (Artifact-Format, ohne `<html>`-Rahmen) — hier wird bearbeitet |
| `index.html` | daraus gebaute, eigenständige Seite zum lokalen Öffnen |
| `build.sh` | erzeugt `index.html` aus `tracker.html` |

Nach jeder Änderung an `tracker.html`:

```sh
./build.sh
```

## Speicherung

Die Einträge liegen im `localStorage` des Browsers. Wird die Seite als
Artifact auf claude.ai geöffnet, speichert sie zusätzlich über die
`artifact`-Capability jede Änderung als neue Version — dadurch sind die
Daten auch auf anderen Geräten vorhanden. Der Startbestand (28.08.2026)
steht im `<script id="app-state">`-Block.
