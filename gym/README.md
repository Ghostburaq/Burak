# Gym Logbuch — Beintraining

Druckoptimiertes Trainingslogbuch als Excel-Arbeitsmappe. Alle Kennzahlen sind
Formeln — sobald im Log Zeilen ergänzt werden, aktualisiert sich alles Weitere
von selbst.

**Datei:** `GymLogbuch_Beine.xlsx` · **PDF-Vorschau:** `GymLogbuch_Beine.pdf`

## Blätter

| Blatt | Zweck | Druck |
|---|---|---|
| `Start` | Anleitung, Legende, offene Punkte aus der Quelle | A4 hoch |
| `Dashboard` | Kennzahlen-Kacheln und vier Diagramme | A4 hoch |
| `Einheiten` | Kopfdaten je Training: Datum, Körpergewicht, Dauer, Schlaf, Gefühl | A4 quer |
| `Log` | Ein Satz pro Zeile, 500 Zeilen vorbereitet | A4 quer, Kopf wiederholt |
| `Auswertung` | Volumen / Top-Gewicht / e1RM je Übung und Einheit (3 Tabellen) | A4 quer, je Tabelle eine Seite |
| `Progression` | Erste gegen letzte Einheit, Abstand zum Bestwert, Trend | A4 quer |
| `Rekorde` | Bestwerte je Übung inkl. Einheit, in der sie fielen | A4 quer |
| `Trainingsblatt` | Leere Vorlage zum Ausdrucken und Mitnehmen | A4 hoch, 2 Seiten |
| `Übungen` | Stammdaten und Planvorgaben; speist Dropdowns, Trainingsblatt und alle Auswertungen | A4 quer |

## Was drucken?

- **Vor dem Training:** `Trainingsblatt` — zwei Seiten (Beine vorne / Beine
  hinten). Pro Übung stehen letztes Gewicht, letzte Wiederholungen, Bestwert
  und ein Zielvorschlag oben in der Kopfzeile, darunter leere Felder zum
  Eintragen mit Stift.
- **Zur Kontrolle:** `Dashboard` und `Progression`, je eine Seite.

Jedes Blatt hat einen festen Druckbereich, A4-Format, wiederholte
Spaltenköpfe, Seitennummerierung in der Fusszeile und ist auf Seitenbreite
skaliert.

## Eingabe

Gelb hinterlegte Zellen sind Eingabefelder, alles andere sind Formeln.

1. Im Blatt `Einheiten` die Einheit anlegen (Nummer, Datum, Rahmendaten). Das
   Datum wandert automatisch ins Log.
2. Im Blatt `Log` je Satz eine Zeile: Einheit, Übung (Dropdown), Satztyp
   (W/A/R), Gewicht, Wiederholungen, optional RPE, Drop-Kette und Notiz.
   Block, Volumen und e1RM rechnen sich selbst.

Satztypen: `W` Warmup · `A` Arbeitssatz (Basis aller Kennzahlen) ·
`R` Reduktions-/Dropsatz.

Neue Übungen im Blatt `Übungen` ergänzen — sie erscheinen dann automatisch im
Dropdown und in Auswertung, Progression und Rekorden. Das `Trainingsblatt`
enthält die aktiven Übungen des Plans; für spontane Zusatzübungen sind die
Notizzeilen am Seitenende gedacht.

### Planvorgaben im Blatt `Übungen`

| Feld | Wirkung |
|---|---|
| `Ziel-Wdh`, `Ziel-Sätze`, `Ziel-RPE` | erscheinen als Vorgabe-Zeile auf dem Trainingsblatt |
| `Start (kg)` | Einstiegsgewicht für Übungen ohne Historie; speist die Plan-Spalte, bis die erste Einheit erfasst ist |
| `Max (kg)` | deckelt den Zielvorschlag, z. B. am Ende des Steckgewichts; das Trainingsblatt weist dann auf Tempo-Progression hin |
| `Aktiv = nein` | Archiv: raus aus dem Trainingsblatt, Historie bleibt in Log, Auswertung, Progression und Rekorden — dort grau und kursiv |

## Kennzahlen

- **Volumen** = Gewicht × Wiederholungen je Satz, nur Arbeitssätze.
- **e1RM (Epley)** = Gewicht × (1 + Wdh / 30). An Maschinen kein echtes 1RM,
  aber ein sauberer Vergleich zwischen Einheiten mit unterschiedlichen
  Wiederholungszahlen.
- **Nächstes Ziel** = letztes Top-Gewicht + 2.5 %, gerundet auf 0.5 kg und
  begrenzt durch `Max (kg)`. Ohne Historie greift `Start (kg)`. Richtwert,
  kein Dogma — an Maschinen bestimmt die Steckplatte den Sprung.

## Plan

Neun aktive Übungen in zwei Blöcken, schwere Grundübung zuerst:

- **Beine vorne:** Hackenschmidt-Kniebeuge · Split Squat · Beinstrecker · Adduktion
- **Beine hinten:** Rumänisches Kreuzheben · Hip Thrust · Beinbeuger · Seitliche Kickbacks · Waden

Lunges und Kickback sind archiviert (redundant zu Split Squat bzw. Hip Thrust
und RDL); ihre Historie bleibt in allen Auswertungen sichtbar.

Hackenschmidt-Kniebeuge und Rumänisches Kreuzheben sind neu und haben noch
keine Historie — bis ein `Start (kg)` eingetragen ist, bleibt ihre Plan-Spalte
auf dem Trainingsblatt leer.

## Datenstand

Einheit 1 bis 4, aufbereitet aus `Loewin_Training_260727.pdf`. Bekannte
Unschärfen der Quelle (fehlende Wiederholungen bei Kickback-Warmups und
Lunges, Hip-Thrust-Dropsätze ohne Absolutgewicht, Adduktion Einheit 4 mit
152.2 statt 152.5 kg) sind im Blatt `Start` dokumentiert und im Log als Notiz
vermerkt.

## Neu erzeugen

```bash
cd gym
python3 build_gymlogbuch.py                                    # xlsx bauen
python3 ~/.claude/skills/xlsx/scripts/recalc.py GymLogbuch_Beine.xlsx 300
soffice --headless --convert-to pdf GymLogbuch_Beine.xlsx      # PDF-Vorschau
```

`daten.py` enthält die Rohdaten aus der Quelle, `build_gymlogbuch.py` erzeugt
Layout, Formeln, Diagramme und Druckeinrichtung.

Die Neuberechnung braucht `libreoffice-calc` (nicht nur `libreoffice-core`),
sonst lässt sich die Datei nicht laden und `recalc.py` läuft in einen Timeout.
