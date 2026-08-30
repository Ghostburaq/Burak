# MiT Strom Schweiz — Vertrieb Rechenzentren

Arbeitsordner für Burak Ücöz, Sales Engineer Power, Mobil in Time AG
(An Aggreko Company).

## Aufbau

```
CLAUDE.md                          Projektanweisung für den ganzen Ordner
.claude/commands/dc-update.md      Slash-Command /dc-update
Datacenter-Radar/
  CLAUDE.md                        Anweisung für das Radar, gilt in diesem Unterordner
  PROMPTS_Claude_Code.md           Prompt-Bibliothek für den Alltag
  MiT_Datacenter_Radar_CH_V1.0.xlsx
  MiT_DC_Radar_Dashboard.html      generierte Web-Ansicht des Radars
  scripts/build_radar.py           Erstaufbau der Datei, nur einmalig
  scripts/update_*.py              dokumentierte schreibende Läufe, je Datum
  scripts/check_radar.py           Prüfung nach jedem schreibenden Lauf
  scripts/eval_dashboard.py        Dashboard-Formeln nachrechnen ohne Excel
  scripts/build_dashboard_html.py  erzeugt die HTML-Ansicht aus der Excel
```

## Web-Dashboard

`python3 scripts/build_dashboard_html.py` liest die Excel und erzeugt
`MiT_DC_Radar_Dashboard.html`: Kennzahlen, die drei offenen Fenster der Woche,
filterbare Projekttabelle mit Quellen je Zeile, Phasen- und Kantonsverteilung,
Changelog. Läuft nur lesend, die Excel bleibt unangetastet.

Die Datei ist als privates Artifact publiziert; der Link bleibt bei jedem
Neu-Publish gleich. In Claude Code öffnet ctrl+] das letzte Artifact,
`/artifacts` listet alle. Nach jedem Montags-Lauf neu generieren und auf
dieselbe URL publizieren (Prompt `DASH:`).

## Wochenlauf

Im Ordner `Datacenter-Radar` in Claude Code:

```
/dc-update
```

oder `DC-Radar Update KW 36`. Der Ablauf steht in `Datacenter-Radar/CLAUDE.md`
Abschnitt 6. Ohne verfügbare Websuche bricht der Lauf ab und die Datei bleibt
unverändert.

## Prüfung nach einem Lauf

```
cd Datacenter-Radar
python3 scripts/check_radar.py      # Struktur, Formeln, Dropdowns, Quellenpflicht
python3 scripts/eval_dashboard.py   # Dashboard-Zahlen nachrechnen
```

`check_radar.py` gibt Exit 1 zurück, wenn etwas kaputt ist. Offene Punkte wie
eine unbelegte Phase oder ein möglicher Dublette stehen als Hinweis darüber und
sind kein Fehler.

## Zwei Konventionen, die nicht in CLAUDE.md stehen

**Unbelegte Dropdown-Felder bleiben leer.** `CLAUDE.md` Regel 2 sagt: was nicht
belegt ist, wird `prüfen`. Für die Spalten G (Phase), K (Kanal_Prio) und N (Prio)
geht das nicht, weil dort eine Dropdown-Prüfung hängt und das Dashboard nach
exakten Werten zählt. Ein `prüfen` in Spalte G würde die Validierung verletzen
und in keiner Phasen-Zählung auftauchen. Deshalb: Zelle leer lassen, Lücke in
Spalte W beschreiben. Das Dashboard hat dafür die Zeile "Phase nicht belegt".
In allen anderen Spalten gilt `prüfen` wie vorgesehen.

**Backups liegen neben der Datei und sind nicht im Git.** Muster
`MiT_Datacenter_Radar_CH_V1.0_backup_JJJJ-MM-TT.xlsx`, maximal vier Stück.
Die Historie steckt im Changelog-Blatt und in den Commits, nicht in den Backups.

## Was das Radar nicht ist

Keine Vollständigkeitsliste des Schweizer Marktes. Es enthält, was belegbar ist,
und macht sichtbar, wo die Belege fehlen. Eine leere Zelle mit einem Eintrag in
Spalte W ist mehr wert als eine plausibel gefüllte.
