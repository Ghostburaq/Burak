---
description: Wöchentlicher Update-Lauf für das Datacenter-Radar Schweiz
---

Führe den Montags-Lauf für das Datacenter-Radar aus. Kalenderwoche: $ARGUMENTS
(ist keine angegeben, nimm die aktuelle ISO-Kalenderwoche).

Arbeitsordner ist `Datacenter-Radar/`. Halte dich an die CLAUDE.md in diesem
Ordner, Abschnitt 6, ohne Abkürzung:

1. `MiT_Datacenter_Radar_CH_V1.0.xlsx` laden, Blatt `02_Projekt_Radar` und
   `06_Changelog` lesen, letzten Update-Stand feststellen und ausgeben.
2. Backup anlegen: `MiT_Datacenter_Radar_CH_V1.0_backup_JJJJ-MM-TT.xlsx`,
   ältere Backups über vier Stück hinaus löschen.
3. Recherche über WebSearch und WebFetch entlang Blatt `05_Quellen_Montag`,
   in der dort festgelegten Reihenfolge. Pro bestehendem Projekt: Phase,
   IBN-Termin, Verzögerung, GU/TU, Fachplaner prüfen. Zusätzlich nach neuen
   Schweizer Rechenzentrums-Projekten suchen.
4. Nur belegte Angaben schreiben. Alles Unbelegte bleibt oder wird `prüfen`.
   Jede Angabe mit Quelle-URL in Spalte T und Quelle-Stand in Spalte U.
5. Formelspalten R und S sowie die gelben Spalten O, P, Q und V nicht
   überschreiben. Neue Zeilen vollständig formatieren, Formeln ergänzen.
6. Prüfdatum in `05_Quellen_Montag` Spalte F setzen.
7. Changelog ergänzen, eine Zeile pro Änderung, mit Konsequenz für MiT.
8. Datei speichern, danach `python3 scripts/check_radar.py` und
   `python3 scripts/eval_dashboard.py` laufen lassen. Prüfen, ob alle sieben Blätter, die
   Dropdowns und die Formeln in R und S intakt sind.
9. Bericht im Terminal exakt im Format aus CLAUDE.md Abschnitt 6, Schritt 6.
   Maximal drei Projekte unter "Fenster offen".

Wenn WebSearch nicht verfügbar ist: abbrechen, Datei unverändert lassen und
das sagen. Kein Update aus dem Gedächtnis.
