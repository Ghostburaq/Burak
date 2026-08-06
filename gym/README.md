# Gym Logbuch — Beintraining

Trainingslogbuch als Excel-Arbeitsmappe, druckoptimiert. Zwei Fassungen aus
demselben Generator, gleicher Aufbau — am OP-Tag wechselst du einfach die
Datei.

| Fassung | Datei | Gilt |
|---|---|---|
| **Vor der OP** | `GymLogbuch_Beine_PreOP.xlsx` | bis 30.09.2026 |
| **Reha** | `GymLogbuch_Beine.xlsx` | ab dem OP-Tag |

## Vier Blätter, vier Aufgaben

| Blatt | wofür | wie oft |
|---|---|---|
| **Plan** | steuern und nachschauen — eine Zeile je Übung | vor dem Training kurz draufschauen |
| **Trainingsblatt** | ausdrucken und mitnehmen, 8 Seiten = 4 Wochen | alle vier Wochen neu drucken |
| **Log** | eintragen, was du gemacht hast | nach jedem Training |
| **Verlauf** | Volumen je Übung und Einheit | ab und zu |

Dazu je Fassung ein Reha-Teil:
`Reha` (Phasenplan) und `Reha-Log` (täglich Schmerz und Beweglichkeit) in der
Reha-Fassung, `Vor der OP` (Countdown, Checkliste, Ausgangswerte) in der
Vor-OP-Fassung.

19 bzw. 18 A4-Seiten insgesamt, davon 8 Trainingsblätter.

## So läuft eine Woche

1. **Plan** öffnen, Spalte *HEUTE* anschauen: dort steht Gewicht × Wdh je
   Übung.
2. **Trainingsblatt** aus dem Stapel nehmen — die Werte stehen schon drauf.
3. Trainieren, mit Stift eintragen.
4. Zeilen ins **Log** tippen. Fertig — der Plan rechnet den nächsten Schritt
   sofort neu.

Gelb = deine Eingabe. Hellblau = rechnet sich selbst. Grün = womit du heute
startest.

## Wie gesteigert wird

Doppelte Progression, in einem Satz: **erst Wiederholungen, dann Gewicht.**

- Schwächster Arbeitssatz unter `Wdh bis` → Gewicht bleibt, **eine Wdh mehr**
- Alle Sätze am oberen Ende → **eine Laststufe drauf**, Wdh zurück auf
  `Wdh von`
- Noch unter `Wdh von` → **Gewicht halten**, bis die untere Grenze steht
- Am `Max (kg)` → Last bleibt, weiter über Tempo und Pausen

Beispiel Split Squat, Bereich 8–10: nach 80 kg × 8/8/8 kommt *Wdh +1 auf 9*,
nach 80 kg × 10/10/10 kommt *Gewicht +5 kg, Wdh zurück auf 8*.

Bezug ist immer der **schwächste** Satz, nicht der beste.

## Die Stellschrauben im Blatt `Plan`

| Feld | Wirkung |
|---|---|
| `Wdh von` / `Wdh bis` | Zielbereich der Progression |
| `Sätze` | Zahl der Arbeitssätze, auch auf dem Trainingsblatt |
| `Schritt (kg)` | kleinste Laststufe an diesem Gerät |
| `Start (kg)` | Einstiegsgewicht für Übungen ohne Historie |
| `Max (kg)` | Deckel, z. B. Ende des Steckgewichts |
| `Aktiv = nein` | Archiv: raus aus dem Trainingsblatt, Historie bleibt |
| `frei ab Woche` | Reha-Freigabe; steuert Status und Sperrvermerk |
| `Woche nach OP` (Zelle C3) | eine Zahl ändern, alles zieht nach |

Rechts neben dem Druckbereich stehen der Hinweistext je Übung und drei
Hilfsspalten für die Progression. Nicht löschen, aber auch nicht nötig.

## Plan

- **Beine vorne:** Beinpresse · Split Squat · Beinstrecker · Adduktion
- **Beine hinten:** Rumänisches Kreuzheben · Hip Thrust · Beinbeuger ·
  Seitliche Kickbacks · Waden

Lunges und Kickback stehen im Archiv, ihre Historie bleibt sichtbar.
Beinpresse und Rumänisches Kreuzheben sind neu und brauchen ein
`Start (kg)`, sonst bleibt die Plan-Spalte leer.

> Die Reha-Angaben sind eine Gedächtnisstütze, keine ärztliche Anweisung. Das
> Nachbehandlungsschema des Operateurs und die Ansagen der Physiotherapie
> haben Vorrang. Die Freigabe der Beinpresse ab Woche 2 ist aus dem eigenen
> Plan abgeleitet und steht als Frage in der Checkliste.

## Übergabe am OP-Tag

Zeilen aus `Log` kopieren und in der Reha-Fassung an derselben Stelle
einfügen. Danach im `Plan` die Woche nach OP setzen und im `Reha-Log` das
OP-Datum. Alles andere rechnet weiter.

## Datenstand

Einheit 1 bis 4 aus `Loewin_Training_260727.pdf`. Fehlende Wiederholungen bei
Lunges und Kickback-Warmups sowie die Hip-Thrust-Dropsätze ohne
Absolutgewicht stehen als Notiz im Log.

## Neu erzeugen

```bash
cd gym
python3 build_gymlogbuch.py reha        # GymLogbuch_Beine.xlsx
python3 build_gymlogbuch.py preop       # GymLogbuch_Beine_PreOP.xlsx
python3 ~/.claude/skills/xlsx/scripts/recalc.py GymLogbuch_Beine.xlsx 500
soffice --headless --convert-to pdf GymLogbuch_Beine.xlsx
```

`daten.py` enthält die Rohdaten, `reha_daten.py` den Wortlaut der
Reha-Inhalte, `build_gymlogbuch.py` Layout, Formeln und Druckeinrichtung.
Umfang steuern die Konstanten `LOG_ROWS`, `EINHEITEN` und `BLATT_KOPIEN`.

Die Neuberechnung braucht `libreoffice-calc`, nicht nur `libreoffice-core`.
