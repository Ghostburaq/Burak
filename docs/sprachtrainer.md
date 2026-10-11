# Sprachtrainer für Claude Code (EN / FR / ES / ZH)

## Installation

Im Repo installiert: Skill unter `.claude/skills/sprachtrainer/`, Befehle unter `.claude/commands/`. Jede Claude-Code-Session in diesem Repo (lokal oder Cloud) findet sie automatisch.

Fortschritt liegt unter `sprachen/` im Repo und wird nach jeder Session committet und gepusht. Wichtig in Cloud-Sessions: Der Container ist flüchtig, nur was gepusht ist, bleibt. Neue Session immer auf dem Branch starten, auf dem der letzte Fortschritt liegt, sonst fängst du bei null an.

## Erster Start

```
/fr start
/fr plan
```

Gleiches für `/en`, `/es` und `/zh` (Chinesisch, Mandarin mit Kurzzeichen und Pinyin).

Web-Version für Netlify mit Vorlesen und Diktat: siehe `sprachtrainer-web/README.md`.

## Täglich

```
/fr                       Tagesprogramm nach Plan
/fr gespraech             Rollenspiel (3 Vorschläge zur Auswahl)
/fr gespraech preis-einwand
/en wortschatz lastbanktest im rechenzentrum
/es grammatik ser estar
/zh wortschatz werksbesuch
/fr immersion kundentermin lausanne
/en schreiben follow-up nach messe
/fr shadowing
/fr test                  Wochentest
/sprachen                 Übersicht über alle Sprachen
/fr anki                  Wortschatz als Anki-Import exportieren
```

Steuerwörter während der Session: `stopp`, `hilfe`, `deutsch`, `langsamer`.

## Was gespeichert wird

```
sprachen/<sprache>/
  profil.md        Niveau, Ziel, Plan-Tag, Testresultate
  plan.md          90-Tage-Plan
  fehler.md        Fehlerjournal, wiederkehrende Fehler kommen beim Aufwärmen dran
  wortschatz.csv   alles Gelernte, Anki-kompatibel
  log.md           eine Zeile pro Session
```

## Grenzen

- Claude Code hört dich nicht. Sprechen: laut sprechen und per Diktierfunktion eingeben. Aussprachefeedback gibt es nur zu Betonung, Bindungen und stummen Lauten.
- Hören läuft über echte Quellen (Podcasts, Radio), die das Tagesprogramm empfiehlt.
- Für echtes Aussprache- und Gesprächstraining mit Menschen bleibt iTalki oder Tandem der Hebel. Der Trainer bereitet dich darauf vor.
