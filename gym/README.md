# Gym Logbuch — Beintraining mit Reha-Modus

Druckoptimiertes Trainingslogbuch als Excel-Arbeitsmappe. Alle Kennzahlen sind
Formeln — sobald im Log Zeilen ergänzt werden, aktualisiert sich alles Weitere
von selbst.

**Datei:** `GymLogbuch_Beine.xlsx` · **PDF-Vorschau:** `GymLogbuch_Beine.pdf`
(29 A4-Seiten)

> Die Reha-Blätter sind eine Gedächtnisstütze für den Alltag, keine ärztliche
> Anweisung. Das schriftliche Nachbehandlungsschema des Operateurs und die
> Ansagen der Physiotherapie haben in jedem Punkt Vorrang.

## Blätter

| Blatt | Zweck | Druck |
|---|---|---|
| `Start` | Anleitung, Legende, offene Punkte | A4 hoch, 2 S. |
| `Dashboard` | 12 Kennzahlen-Kacheln und vier Diagramme | A4 hoch |
| `Reha-Fahrplan` | Phasenplan nach der Schulter-OP: erlaubt, verboten, Meilensteine | A4 quer |
| `Reha-Modus` | Wochen-Ampel je Übung: FREI / GESPERRT plus Ersatzübung | A4 quer, 2 S. |
| `Reha-Log` | Täglich Schmerz und Beweglichkeit, mit Statusblock und Verlaufskurven | A4 quer, 2 S. |
| `Einheiten` | Kopfdaten je Training, 60 Einheiten vorbereitet | A4 quer, 2 S. |
| `Log` | Ein Satz pro Zeile, 1200 Zeilen vorbereitet | A4 quer, Kopf wiederholt |
| `Auswertung` | Volumen / Top-Gewicht / e1RM je Übung und Einheit | A4 quer, je Tabelle eine Seite |
| `Progression` | Erste gegen letzte Einheit, Abstand zum Bestwert, Trend | A4 quer |
| `Rekorde` | Bestwerte je Übung inkl. Einheit, in der sie fielen | A4 quer |
| `Trainingsblatt` | Vorlage zum Ausdrucken und Mitnehmen, **4 Blätter je Block** | A4 hoch, 8 S. |
| `Übungen` | Stammdaten, Planvorgaben und Reha-Freigaben | A4 quer, 2 S. |

## Was drucken?

- **Trainingsblatt** — ein Ausdruck liefert acht Seiten: vier Mal Beine vorne
  und vier Mal Beine hinten. Das deckt rund vier Trainingswochen ab, danach
  einfach neu drucken. Jedes Blatt zeigt pro Übung das letzte Gewicht, den
  Bestwert, den Zielvorschlag mit Aufwärm-Rampe und die Vorgabe
  (Sätze × Wdh @ RPE). In der Reha-Sperrzeit steht dort stattdessen rot der
  Sperrvermerk mit der Ersatzübung.
- **Reha-Modus** — eine Seite an den Spiegel: was diese Woche freigegeben ist.
- **Reha-Fahrplan** — einmal ausdrucken, ins Ablagefach.
- **Dashboard** und **Progression** — zur Kontrolle, je eine Seite.

Jedes Blatt hat einen festen Druckbereich, A4-Format, wiederholte
Spaltenköpfe, Seitennummerierung und ist auf Seitenbreite skaliert.

## Eingabe

Gelb hinterlegte Zellen sind Eingabefelder, alles andere sind Formeln.

1. Blatt `Einheiten`: Einheit anlegen (Nummer, Datum, Rahmendaten). Das Datum
   wandert automatisch ins Log.
2. Blatt `Log`: je Satz eine Zeile — Einheit, Übung (Dropdown), Satztyp
   (W/A/R), Gewicht, Wiederholungen, optional RPE, Drop-Kette und Notiz.
   Block, Volumen und e1RM rechnen sich selbst.
3. Blatt `Reha-Modus`: aktuelle Woche nach OP oben eintragen.
4. Blatt `Reha-Log`: einmal das OP-Datum, danach täglich eine Zeile.

Satztypen: `W` Warmup · `A` Arbeitssatz (Basis aller Kennzahlen) ·
`R` Reduktions-/Dropsatz.

### Steuerfelder im Blatt `Übungen`

| Feld | Wirkung |
|---|---|
| `Ziel-Wdh`, `Ziel-Sätze`, `Ziel-RPE` | Vorgabe-Zeile auf dem Trainingsblatt; `Ziel-Sätze` bestimmt auch die Zahl der Satzzeilen |
| `Start (kg)` | Einstiegsgewicht für Übungen ohne Historie; speist die Plan-Spalte, bis die erste Einheit erfasst ist |
| `Max (kg)` | deckelt den Zielvorschlag, z. B. am Ende des Steckgewichts; das Trainingsblatt weist dann auf Tempo-Progression hin |
| `Aktiv = nein` | Archiv: raus aus Trainingsblatt und Reha-Modus, Historie bleibt in Log, Auswertung, Progression und Rekorden — dort grau und kursiv |
| `Reha frei ab Woche` | steuert die Ampel im `Reha-Modus` und den Sperrvermerk auf dem Trainingsblatt |
| `Ersatz in der Sperrzeit` | erscheint automatisch, solange die Übung gesperrt ist |

## Kapazität

| | vorbereitet | reicht für |
|---|---|---|
| Log | 1200 Sätze | rund 60 Einheiten |
| Einheiten | 60 | etwa 30 Wochen bei 2 Beineinheiten |
| Reha-Log | 240 Tage | rund 8 Monate täglich |
| Übungen | 14 Slots | 11 belegt |

Die `Auswertung` zeigt 16 Einheiten nebeneinander. Mit der Zahl in Zelle `B3`
verschiebt sich das Fenster (z. B. `17` zeigt Einheit 17 bis 32) — die
Gesamtspalte rechts rechnet unabhängig davon immer über alle Einheiten. So
bleibt das Blatt druckbar, egal wie lang die Historie wird.

## Kennzahlen

- **Volumen** = Gewicht × Wiederholungen je Satz, nur Arbeitssätze.
- **e1RM (Epley)** = Gewicht × (1 + Wdh / 30). An Maschinen kein echtes 1RM,
  aber ein sauberer Vergleich zwischen Einheiten mit unterschiedlichen
  Wiederholungszahlen.
- **Nächstes Ziel** = letztes Top-Gewicht + 2.5 %, gerundet auf 0.5 kg und
  begrenzt durch `Max (kg)`. Ohne Historie greift `Start (kg)`.

## Plan

Neun aktive Übungen in zwei Blöcken, schwere Grundübung zuerst:

- **Beine vorne:** Hackenschmidt-Kniebeuge · Split Squat · Beinstrecker · Adduktion
- **Beine hinten:** Rumänisches Kreuzheben · Hip Thrust · Beinbeuger · Seitliche Kickbacks · Waden

Lunges und Kickback sind archiviert; ihre Historie bleibt in allen
Auswertungen sichtbar.

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
python3 ~/.claude/skills/xlsx/scripts/recalc.py GymLogbuch_Beine.xlsx 600
soffice --headless --convert-to pdf GymLogbuch_Beine.xlsx      # PDF-Vorschau
```

- `daten.py` — Rohdaten der Einheiten 1 bis 4 aus der Quelle
- `reha_daten.py` — Wortlaut der Reha-Inhalte, unverändert übernommen
- `build_gymlogbuch.py` — Layout, Formeln, Diagramme, Druckeinrichtung

Kapazität und Umfang stehen als Konstanten oben in `build_gymlogbuch.py`
(`LOG_ROWS`, `SESSION_SLOTS`, `REHALOG_ROWS`, `BLATT_KOPIEN`, `SESSIONS`).
`BLATT_KOPIEN` bestimmt, wie viele Trainingsblätter je Block gedruckt werden.

Die Neuberechnung braucht `libreoffice-calc` (nicht nur `libreoffice-core`),
sonst lässt sich die Datei nicht laden und `recalc.py` läuft in einen Timeout.
