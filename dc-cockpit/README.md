# MiT Datacenter Cockpit

Arbeitsoberfläche für die Datacenter-Akquise Schweiz und Liechtenstein. Zeigt fällige Anrufe,
Kontaktstand, Neubau-Pipeline, Bestand auf der Karte und Branchen-News in einem Fenster.
Anrufergebnisse werden im Cockpit erfasst und gehen zurück in den Excel-Anrufplan.

## Was live ist, und was nicht

Ehrlich getrennt, damit du dich nicht auf etwas verlässt, das nicht läuft:

| Teil | Wie aktuell | Woher |
|---|---|---|
| Fällige Anrufe, Überfälligkeit, Verzug in Tagen | sekundengenau | gegen die Systemuhr, alle 30 Sekunden neu gerechnet |
| Kontakte, Termine, Gesprächseinstieg, Ziel | bei jedem Updater-Lauf | Tab `Anrufplan` der Excel |
| News | bei jedem Updater-Lauf | RSS-Feeds, gefiltert auf DC-Relevanz mit CH- und FL-Bezug |
| Karte | einmalig geocodiert, dann aus Cache | Nominatim (OpenStreetMap), Kacheln von openstreetmap.org |
| Pipeline, Bestand, Liechtenstein, Aufträge | manuell | aus `MARKT_DC.md` in `inhalte.py` gepflegt |
| Anrufergebnisse | sofort | Browserspeicher, Export nach CSV und zurück in die Excel |

**Nicht live:** Preise, Verfügbarkeiten, Flottendaten. Die stehen bewusst nirgends drin.
CHF-Sperre und Owen-Gate gelten auch für dieses Tool.

## Keys

| Dienst | Key nötig | Bemerkung |
|---|---|---|
| OpenStreetMap Kacheln | nein | freie Nutzung, Attribution ist eingebaut |
| Nominatim Geocoding | nein | verlangt nur eine Kontaktadresse im User-Agent, steht in `config.json` |
| RSS-Feeds | nein | offene Feeds |
| newsapi.org | optional | Feld `newsapi_key` in `config.json`, nur falls du zusätzliche Quellen willst |
| Google Maps | nein | Feld existiert nur als Platzhalter, falls du später wechseln willst |

Das Tool kommt **ohne einen einzigen Key** aus. `config.json` enthält keine Geheimnisse und steht
trotzdem in `.gitignore`, damit dort später nichts Vertrauliches versehentlich ins Git rutscht.

## Einrichten

```
python3 -m pip install openpyxl
```

Mehr braucht es nicht, alles andere ist Standardbibliothek. Getestet mit Python 3.11.

Ordnerstruktur:

```
dc-cockpit/
  MiT_DC_Cockpit.html            das Cockpit, Einzeldatei (wird erzeugt)
  MiT_DC_Cockpit.template.html   Vorlage ohne Daten
  dc_update.py                   Updater: News, Karte, Excel, Server
  dc_seed.py                     Maschinerie, liest die Excel
  inhalte.py                     Kontaktdaten, Markt, Regeln, Signatur (VERTRAULICH)
  inhalte.example.py             Geruest dazu
  config.example.json            Vorlage, nach config.json kopieren
  daten/
    MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx
    Data_Centre_Project_Tracker_March_2026.xlsm
```

Aus einem frischen Checkout:

```
cp inhalte.example.py inhalte.py     # dann mit den echten Daten fuellen
cp config.example.json config.json   # optional, laeuft auch ohne
python3 dc_update.py --once          # erzeugt das Cockpit aus der Vorlage
```

## Starten

**Weg 1, empfohlen.** Server starten, aktualisiert sich selbst:

```
python3 dc_update.py --serve 8777
```

Dann `http://127.0.0.1:8777/MiT_DC_Cockpit.html` im Browser öffnen. Der Updater läuft alle
30 Minuten im Hintergrund, das Cockpit holt sich die neuen Daten von allein. Intervall ändern
mit `--intervall 15`.

**Weg 2.** Einmal aktualisieren, dann die HTML direkt per Doppelklick öffnen:

```
python3 dc_update.py --once
```

`--once` backt den Datenstand fest in die HTML. Die Datei funktioniert danach allein, offline,
und lässt sich per Mail verschicken. Ohne Server kann sie sich allerdings nicht selbst
nachladen, oben rechts steht dann `Einzeldatei`.

**Weg 3.** Nur prüfen, ob die Quellen antworten, ohne etwas zu schreiben:

```
python3 dc_update.py --test-feeds
```

## Automatisch im Hintergrund

**Windows, Aufgabenplanung:** Neue Aufgabe, Trigger täglich 06:45, Aktion
`python.exe` mit Argument `C:\Pfad\dc-cockpit\dc_update.py --once`, Start in `C:\Pfad\dc-cockpit`.

**macOS oder Linux, cron:** `crontab -e`, dann

```
45 6 * * 1-5 cd /Pfad/dc-cockpit && /usr/bin/python3 dc_update.py --once >> lauf.log 2>&1
```

Werktags um 06:45 hast du den aktuellen Stand, bevor der erste Anruf ansteht.

## Feeds reparieren

Die Feed-URLs in `config.example.json` sind **Kandidaten und ungeprüft**. Sie konnten beim Bau
nicht getestet werden, weil die Umgebung den Zugriff auf Nachrichtenseiten blockiert hat.
Der erste Lauf auf deinem Rechner testet jede URL, schaltet tote Quellen ab und schreibt das
Ergebnis in `config.json`. Im Reiter **Quellen** siehst du pro Feed, was los ist.

Eine tote URL ersetzt du in `config.json` unter `feeds` und setzt `"aktiv": true`. Die richtige
Adresse steht meist auf der Feed-Seite des Mediums, bei der Netzwoche zum Beispiel unter
`netzwoche.ch/RSS-Feeds`. Danach `--test-feeds` laufen lassen.

Antwortet **kein einziger** Feed, liegt es fast sicher am Firmenproxy. Dann in `config.json`
das Feld `proxy` auf `http://proxy.deinefirma.ch:8080` setzen.

## Anrufergebnis erfassen und zurückschreiben

1. Im Cockpit auf **Anruf loggen**, Ergebnis, nächsten Schritt und Wiedervorlage eintragen, Gates abhaken.
2. Reiter **Log**, Knopf **CSV für Excel**. Die Datei landet in den Downloads.
3. Datei als `anruf_log.csv` in den Ordner `dc-cockpit` legen.
4. `python3 dc_update.py --merge-log`

Das Skript legt vorher automatisch eine Sicherung der Mappe an
(`..._backup_JJJJMMTT_HHMMSS.xlsx`) und lädt die Datei **ohne** `data_only`, damit keine Formeln
verloren gehen. Zugeordnet wird über die Namensspalte im Tab `Anrufplan`.

Für KONTAKTE_STATUS.md gibt es daneben den Knopf **Markdown**, der die Tabelle im Format
deiner Statusdatei ausgibt.

## Kalender

Knopf **Kalender (.ics)** im Cockpit erzeugt alle offenen Anruftermine als Kalenderdatei mit
Erinnerung 15 Minuten vorher. In Outlook über Datei, Öffnen und Exportieren, Importieren.
Gesprächseinstieg, Ziel, Kontaktdaten und die Gates stehen im Termintext.

Wer das Cockpit offen lässt, kann stattdessen **Hinweise** einschalten, dann meldet sich der
Browser 15 Minuten vor jedem Anruf.

## Datenregeln, die eingebaut sind

- Kein erfundener Wert. Fehlt eine Mailadresse oder Telefonnummer, steht **FEHLT** in Rot.
- Abgeleitete Adressen (Firmenmuster angewendet, nicht bestätigt) stehen orange mit dem Vermerk
  *abgeleitet, unbestätigt*. Das Bounce-Risiko ist real, im aktuellen Stand betrifft das einen Kontakt.
- Namen stammen nie aus der Namensspalte des Aggreko-Trackers, sondern sind über die
  E-Mail-Adresse zugeordnet. Der Tracker hat im Green-Block einen Zeilenversatz.
- Jeder Kontakt mit bekanntem Datenproblem trägt einen Warnkasten: kaputte Telefonnummer,
  ungeklärte Anrede, Werbe-Opt-out im Impressum, nötige interne Abstimmung.
- Gestrichene Kontakte stehen mit Grund und Quelle in einer eigenen Tabelle, damit sie nicht
  versehentlich reaktiviert werden.
- Die Signatur ist im Reiter **Regeln** hinterlegt, die alte Nummer und die alte .ch-Adresse
  stehen als ausdrücklich falsch daneben.

## Vertraulichkeit

`inhalte.py`, `daten/`, `dc_data.json`, `anruf_log.csv`, `config.json` und `geo_cache.json`
stehen in `.gitignore`. `dc_seed.py` und `dc_update.py` sind reine Maschinerie ohne Kundendaten.
Kundennamen, Projektzuordnungen und der Aggreko-Tracker gehören nicht in ein Repository. Im Git liegt nur das Werkzeug, nicht dein Bestand.

Die ausgelieferte `MiT_DC_Cockpit.html` enthält dagegen den eingebackenen Datenstand mit
Kontaktnamen. Sie ist ein internes Dokument. Nicht an Kunden weitergeben.

## Grenzen

- Die Kartenmarken sitzen auf dem Ortsnamen oder der Adresse aus der Quelle, nicht auf der
  Bauparzelle. Für die Anfahrt taugen sie nicht.
- Der Bestand ist eine Regionsmarke je Region, keine Einzelstandorte. Die Einzelstandorte
  kommen erst über den Ablauf `MAP` aus `PROMPTS.md` dazu.
- Pipeline und Bestand sind ein Stand vom September 2026 aus öffentlichen Quellen und werden
  nicht automatisch aktualisiert. Sie leben in `inhalte.py` und werden dort gepflegt.
- Texte aus dem Anrufplan erscheinen so, wie sie in der Excel stehen, also mit ae, oe und ue
  statt Umlauten. Das ist deine Quelldatei, das Tool ändert sie nicht eigenmächtig.
- Der Browserspeicher hängt am Browser und am Rechner. Wer das Log sichern will, exportiert die
  CSV und schreibt sie in die Excel zurück.
