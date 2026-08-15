# Gym Logbuch — Beintraining, zwei Fassungen

Druckoptimiertes Trainingslogbuch als Excel-Arbeitsmappe. Alle Kennzahlen sind
Formeln — sobald im Log Zeilen ergänzt werden, aktualisiert sich alles Weitere
von selbst.

| Fassung | Datei | Gilt | Umfang |
|---|---|---|---|
| **Vor der OP** | `GymLogbuch_Beine_PreOP.xlsx` | bis 30.09.2026 | 13 Blätter, 30 A4-Seiten |
| **Reha** | `GymLogbuch_Beine.xlsx` | ab dem OP-Tag | 12 Blätter, 29 A4-Seiten |

Beide entstehen aus demselben Generator und sind in `Log`, `Einheiten`,
`Auswertung`, `Progression`, `Rekorde`, `Trainingsblatt` und `Übungen`
identisch aufgebaut.

## Übergabe am OP-Tag

Zeilen aus `Log` und `Einheiten` aus der Vor-OP-Fassung kopieren und in der
Reha-Fassung an derselben Stelle einfügen. Spaltenaufbau und Zeilennummern
stimmen überein, Auswertung, Progression, Rekorde und Dashboard rechnen
sofort weiter. Danach im Blatt `Reha-Modus` die aktuelle Woche nach OP
eintragen und im `Reha-Log` das OP-Datum.

> Die Reha-Blätter sind eine Gedächtnisstütze für den Alltag, keine ärztliche
> Anweisung. Das schriftliche Nachbehandlungsschema des Operateurs und die
> Ansagen der Physiotherapie haben in jedem Punkt Vorrang.

## Blätter der Vor-OP-Fassung

Zusätzlich zu den gemeinsamen Blättern:

| Blatt | Zweck | Druck |
|---|---|---|
| `OP-Countdown` | Tage und Wochen bis zum Termin; je Übung, wie lange sie danach ausfällt und welcher Ersatz einspringt | A4 quer, 2 S. |
| `Vorbereitung` | 25-Punkte-Checkliste: Fragen an Operateur und Physiotherapie, Organisation, Gym-Logistik | A4 hoch |
| `Baseline Schulter` | Ausgangswerte beider Schultern: Beweglichkeit, Schmerz, Curl-Testgewicht | A4 quer |

Das `Trainingsblatt` sperrt vor der OP nichts, vermerkt aber hinter jeder
Übung, wie lange sie nach der OP ausfällt. `Reha-Modus` und `Reha-Log`
entfallen, der `Reha-Fahrplan` ist enthalten — er lohnt sich vorher zu lesen.

### Warum die Baseline wichtig ist

Der Reha-Fahrplan misst zwei Meilensteine am Vergleich zur Gegenseite
(Beugekraft 70 % in Phase 4, 90 % in Phase 5). Ohne einen vor der OP
gemessenen Ausgangswert der gesunden Seite sind diese Prozentwerte später
nicht überprüfbar — und nachholen lässt sich die Messung dann nicht mehr.

## Gemeinsame Blätter

Die Reha-Fassung hat statt `OP-Countdown`, `Vorbereitung` und
`Baseline Schulter` die Blätter `Reha-Modus` und `Reha-Log`.

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
| `Wdh von`, `Wdh bis` | Zielbereich der doppelten Progression |
| `Ziel-Sätze`, `Ziel-RPE` | Vorgabe-Zeile auf dem Trainingsblatt; `Ziel-Sätze` bestimmt auch die Zahl der Satzzeilen |
| `Schritt (kg)` | kleinste sinnvolle Laststufe an diesem Gerät; steuert, wie viel bei einer Gewichtssteigerung draufkommt |
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
### Doppelte Progression

So entsteht der Vorschlag für die nächste Einheit — er rechnet sich nach
jedem Log-Eintrag neu:

**Zielbereich: 5 bis 8 Wiederholungen, für alle Übungen gleich.**
**Immer genau drei Arbeitssätze, absteigend:** Satz 1 schwer (Top-Satz),
Satz 2 mit 95 %, Satz 3 mit 90 % des Zielgewichts. Die leichteren Sätze
dürfen eine bzw. zwei Wiederholungen mehr, nie über 8. Reduktionssätze
entfallen.

Die Progression hängt allein am **Top-Satz** — Satz 2 und 3 sind Volumen,
kein Steuersignal.

1. **Wiederholungen zuerst.** Solange der *schwächste* Arbeitssatz unter 8
   liegt, bleibt das Gewicht stehen und es kommt eine Wiederholung dazu.
2. **Dann Gewicht.** Schaffen alle Arbeitssätze 8, kommt eine Laststufe
   (`Schritt (kg)`) drauf und die Wiederholungen fangen bei 5 wieder an.
3. **Unter 5 Wdh** bleibt das Gewicht stehen, bis die untere Grenze steht.
4. **Am Deckel** (`Max (kg)`) steigt die Last nicht weiter — der Hinweis
   verweist auf Tempo und Pausen.

Beispiel: Beinpresse, zuletzt 290 kg × 5/5/5 → *Wdh +1 auf 6*. Nach
290 kg × 8/8/8 → *Gewicht +10 kg, Wdh zurück auf 5*.

### Umstellungsphase

Der Bereich wechselt von 10–20 auf 5–8 Wiederholungen, die bisherigen
Gewichte sind dafür zu leicht. Liegt der schwächste Satz deutlich über 8 Wdh,
springt der Vorschlag entsprechend grösser — rund 2.5 % je Wiederholung
darüber, höchstens 15 % pro Einheit. Nach zwei bis drei Einheiten bist du im
Bereich, danach läuft die normale Progression. Solche Sprünge sind auf dem
Trainingsblatt mit *(Umstellung auf den neuen Bereich)* gekennzeichnet.

Das Blatt `Rekorde` zeigt je Übung `Nächstes Ziel (kg)`, `Ziel-Wdh nächste
Einheit` und den Schritt im Klartext; das `Trainingsblatt` übernimmt beides.
`Progression` zählt zusätzlich, wie viele Einheiten die aktuelle Last schon
steht — ab vier wird die Zeile gelb.

## Plan

Neun aktive Übungen in zwei Blöcken, schwere Grundübung zuerst:

- **Beine vorne:** Beinpresse · Split Squat · Beinstrecker · Adduktion
- **Beine hinten:** Rumänisches Kreuzheben · Hip Thrust · Beinbeuger · Seitliche Kickbacks · Waden

Lunges und Kickback sind archiviert; ihre Historie bleibt in allen
Auswertungen sichtbar.

Beinpresse und Rumänisches Kreuzheben sind neu und haben noch keine Historie —
bis ein `Start (kg)` eingetragen ist, bleibt ihre Plan-Spalte auf dem
Trainingsblatt leer.

Die Beinpresse hat die Hackenschmidt-Kniebeuge ersetzt. Sie war bisher als
Ersatzübung für deren Sperrzeit hinterlegt, war also vor Woche 6 nutzbar —
daraus ist die Freigabe ab Woche 2 abgeleitet. Dieser Wert ist eine Ableitung
aus dem eigenen Plan, keine ärztliche Freigabe, und steht als offener Punkt
auf dem Blatt `Start` sowie als Frage in der Vorbereitungs-Checkliste.

## Datenstand

Einheit 1 bis 4, aufbereitet aus `Loewin_Training_260727.pdf`. Bekannte
Unschärfen der Quelle (fehlende Wiederholungen bei Kickback-Warmups und
Lunges, Hip-Thrust-Dropsätze ohne Absolutgewicht, Adduktion Einheit 4 mit
152.2 statt 152.5 kg) sind im Blatt `Start` dokumentiert und im Log als Notiz
vermerkt.

## Neu erzeugen

```bash
cd gym
python3 build_gymlogbuch.py reha                               # Reha-Fassung
python3 build_gymlogbuch.py preop                              # Vor-OP-Fassung
python3 ~/.claude/skills/xlsx/scripts/recalc.py GymLogbuch_Beine.xlsx 700
soffice --headless --convert-to pdf GymLogbuch_Beine.xlsx      # PDF-Vorschau
```

Ohne Argument wird die Reha-Fassung gebaut. Das OP-Datum steht als Konstante
`OP_DATUM` oben im Skript.

- `daten.py` — Rohdaten der Einheiten 1 bis 4 aus der Quelle
- `reha_daten.py` — Wortlaut der Reha-Inhalte, unverändert übernommen
- `build_gymlogbuch.py` — Layout, Formeln, Diagramme, Druckeinrichtung

Kapazität und Umfang stehen als Konstanten oben in `build_gymlogbuch.py`
(`LOG_ROWS`, `SESSION_SLOTS`, `REHALOG_ROWS`, `BLATT_KOPIEN`, `SESSIONS`).
`BLATT_KOPIEN` bestimmt, wie viele Trainingsblätter je Block gedruckt werden.

Die Neuberechnung braucht `libreoffice-calc` (nicht nur `libreoffice-core`),
sonst lässt sich die Datei nicht laden und `recalc.py` läuft in einen Timeout.
