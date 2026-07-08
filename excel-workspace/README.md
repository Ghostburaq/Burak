# MiT × Aggreko — GESAMTMAPPE 2026

**Eine einzige Excel-Arbeitsmappe als Workspace** — ersetzt 15 Einzeldateien.
Deliverable: [`MiT_GESAMTMAPPE_2026.xlsm`](MiT_GESAMTMAPPE_2026.xlsm) (38 Reiter, 12'850+ Formeln, 15 Live-Diagramme, Dark-Executive-Cockpit, 13 Makros).

## Lesbarkeit & Währung korrigiert (v1.5)

- **Kein abgeschnittener Text mehr:** Jede Spalte wird an ihren tatsächlichen Inhalt
  angepasst; sehr lange Texte (z.B. Notizen im Kalender) brechen sauber um statt
  „nur ein paar Buchstaben" zu zeigen. Automatisch geprüft: **0 abgeschnittene Zellen**
  auf allen 38 Reitern (beide Varianten).
- **Sichtbare Währung überall:** Geld-Spalten und KPI-Karten zeigen jetzt explizit
  `1'234'567 CHF` bzw. `… $` (deutsche Komposita wie *Tagespreis / Wochenpreis /
  Monatspreis* wurden zuvor nicht als Geld erkannt — jetzt behoben). Reine Zähler
  (Anzahl Deals, Kontakte …) bleiben bewusst ohne Währung; lokale Fremdwährung
  (Preisliste International, „LC") bleibt neutral.

## Aufbau (38 Reiter, logisch getrennt & verknüpft)

| Bereich | Reiter | Inhalt |
|---|---|---|
| Navigation | `00_START`, `01_DASHBOARD` | Navigation + Live-KPIs über alle Bereiche |
| Vertrieb Strom CH | `02_PIPELINE` … `09_KUNDENANALYSE` | 47 Deals, 798 CRM-Firmen, 1'133 Kontakte, Forecast (+Charts), Monatsreport, **CEO-Report** (befüllt), **Diagramme** |
| Datacenter CH | `10_DC_BETREIBER` … `14_DC_DOSSIERS` | 30 Betreiber, 16 Bauprojekte, 38 Standorte, Kontakte, Dossiers |
| DC-Marktanalyse | `30_DC_MARKTANALYSE` … `34_DC_KONTAKTE_MA` | 14 DC-Projekte mit Prio-Score, Bauphasen-Matrix, Playbook, Wettbewerb/Regulatorik, Kontakte-Tracker |
| Global | `15_GLOBAL_PROJEKTE` … `17_GLOBAL_ANALYTICS` | 10'572 DC-Projekte, 8'502 Kontakte, Live-Analytics |
| Produkte & Preise | `18_KATALOG` … `20_PREISLISTE_INTL` | 466 Produkte, Preislisten CHF + International |
| Werkzeuge | `21_GEN_RECHNER` … `27_AKTIONEN` | Generator-Rechner, Angebotskalkulator, Marktvolumen, Normen, Akquiseplan, **Aktions-Zentrale** |
| System | `90_IMPORT`, `91_LISTEN`, `99_INFO` | Import-Zentrale, Dropdown-Quellen, Doku |

## DC-Marktanalyse (v1.4)

Neue Datei `MiT_Datacenter_Marktanalyse_CH_2026.xlsx` als 5 Reiter eingearbeitet:
- **30_DC_MARKTANALYSE** — 14 CH-DC-Projekte mit Prio-Score, Nähe-Klasse, MiT-Opportunität + Status-Doughnut
- **31_DC_BAUPHASEN** — Matrix: welche MiT-Leistung greift in welcher Bauphase (P1–P6)
- **32_DC_PLAYBOOK** — Lieferspektrum + Networking-Playbook + Ausschreibungs-Kanäle
- **33_DC_WETTBEWERB** — OEM-Festverträge (Marktumfeld) + Regulatorik (Stage V/LRV/PQ)
- **34_DC_KONTAKTE_MA** — Kontakte-Tracker je Projekt mit Fälligkeits-Ampel

Getestet in **Loop-Schleife** (`tests/run_loop.sh`): Struktur + Recalc (beide Varianten) + E2E,
mehrfach wiederholt bis **0 Fehler** (15 Diagramme, 38 Reiter, 12'850+ Formeln).

## Design — Dark Executive Cockpit (v1.3)

- **Dunkle Kopfbänder** mit Bereichs-Akzent, moderne Schrift (Segoe UI)
- **Gefüllte KPI-Karten** in Bereichsfarbe mit weißen Zahlen (Dashboard-Cockpit)
- **Cockpit-Charts** auf dem Dashboard: Doughnut (Pipeline-Status), Top-Segmente, Region-Volumen
- **13 Live-Diagramme** gesamt, In-Zellen-Datenbalken, Ampel-Icons, Farbskalen — auf allen Reitern

## Design & Grafik (v1.2)

- **In-Zellen-Datenbalken** auf allen Wertspalten (Volumen, CHF-Potential, IT-MW, Preise …)
- **Ampel-Icons** auf Wahrscheinlichkeits-Spalten, **Farbskala** auf Marge %
- **Karten-Dashboard** mit farbigem Akzent je Bereich; **8 Live-Diagramme** (Forecast + Diagramme-Reiter)
- Gitternetz aus, druckfertiges Layout (Fit-to-Width, Titelzeilen-Wiederholung) auf **jeder** Seite
- Neuer Reiter **27_AKTIONEN**: bündelt offene Deals, Akquise-Aufgaben und Prio-A-Kunden

## Neue Funktionen (v1.3)

- **28_ZIELE** — Ziel-Tracker: Jahres-/Segmentziele, Ist-WON live, Zielerreichung als **Doughnut-Gauge** + Ziel-vs-Ist-Chart
- **29_KALENDER** — Termin-/Wiedervorlage-Planer mit **Fälligkeits-Ampel** (überfällig/diese Woche), Startzeilen aus aktiver Pipeline
- **Offerten-Generator** — Offerte-Kopf auf 22_ANGEBOT_KALK, Export als PDF, Zähler-Reset für neue Offerte
- **Schnell-Erfassung** — neue Deals/Kunden per Eingabemaske (Makro) statt direkt in die Liste tippen

## Shortcuts / Makros (13 Stück)

`Ctrl+Shift+I` Import · `Ctrl+Shift+M` Monatsreport · `Ctrl+Shift+B` neues Blatt · `Ctrl+Shift+E` Blatt-Export ·
`Ctrl+Shift+F` Suche · `Ctrl+Shift+D` alle Berichte als PDF · `Ctrl+Shift+G` neuer Deal · `Ctrl+Shift+K` neuer Kunde ·
`Ctrl+Shift+W` Wiedervorlage +14 · `Ctrl+Shift+O` Offerte als PDF · `Ctrl+Shift+N` neue Offerte

## Import-Automatik (VBA)

- **Ctrl+Shift+I** (oder Alt+F8 → `MIT_Import`): Excel-/CSV-Datei wählen → jedes Blatt wird
  per Kopfzeilen-Erkennung dem richtigen Reiter zugeordnet und **angehängt**.
  Duplikate werden über Schlüsselspalten erkannt und übersprungen.
  Fremde Headernamen (auch der englische Aggreko-Tracker) werden über die Alias-Tabelle übersetzt.
  Unbekannte Blätter → automatisch **neues rotes Blatt** (`IMP …`).
  Jeder Import wird in `90_IMPORT` protokolliert.
- **Ctrl+Shift+M**: Monatsreport als **neue Arbeitsmappe** (Werte eingefroren) automatisch erstellen & speichern.
- **Ctrl+Shift+B**: neues leeres Listen-Blatt anlegen. **Ctrl+Shift+E**: aktives Blatt als Datei exportieren.
- Regeln/Aliase sind Daten, kein Code: Tabellen auf `90_IMPORT` (erweiterbar ohne VBA-Kenntnisse).

## Technik

- Datenmappe generiert mit `build.py` (openpyxl) aus `extract.py`-Normalisierung der 15 Quelldateien.
- VBA-Projekt von Grund auf gebaut: `ovba_compress.py` (MS-OVBA-Kompression) + `vba_bin.py`
  (MS-CFB-Container + `dir`-Stream) + `package_xlsm.py` (OPC-Packaging).
- VBA-Quellcode: [`vba_src/`](vba_src/) — portabel (Windows/Mac-Excel; ohne `Scripting.Dictionary`).

## Test-Nachweis (alles automatisiert)

| Test | Ergebnis |
|---|---|
| Formel-Syntax + Cross-Sheet-Referenzen (openpyxl-Tokenizer) | 9'003 Formeln, 0 Fehler |
| Neuberechnung LibreOffice, Scan aller 317'843 Werte | 0 Formelfehler (`#REF!`, `#NAME?`, …) |
| VBA-Container (olefile + olevba, unabhängige Parser) | Quellcode 1:1 extrahierbar |
| End-to-End: Import-Makro in LibreOffice ausgeführt | 19/19 Checks OK (Zeilen, Aliase, Duplikate, %-Normalisierung, Formel-Auffüllung, Protokoll) |
| End-to-End: unbekanntes Blatt → neues Blatt | OK |
| End-to-End: Monatsreport → neue Mappe mit eingefrorenen KPIs | OK |

Testsuite: `test_structure.py`, `test_recalc.py`, `test_final.py` (LibreOffice-UNO-Harness).

## Zwei Varianten

| Datei | Zweck |
|---|---|
| `MiT_GESAMTMAPPE_2026.xlsm` | **Vollversion** mit Import-Automatik (Makro-Freigabe nötig, s.u.) |
| `MiT_GESAMTMAPPE_2026_OHNE_MAKROS.xlsx` | **Sofort nutzbar ohne jede Warnung** — alles ausser der Import-/Export-Automatik |
| `MiT_GESAMTMAPPE_2026_Vollversion.zip` | Vollversion als ZIP — mit 7-Zip/WinRAR entpackt entsteht die Sperre oft gar nicht |

## Wichtig: Makro-Freigabe bei heruntergeladenen Dateien

Excel **blockiert Makros** in Dateien aus Downloads/Chats (Mark-of-the-Web). Einmalig freigeben:

**Weg 1 (normaler PC):** Excel schliessen → Explorer → Rechtsklick auf Datei → **Eigenschaften** →
Haken bei **„Zulassen" (Unblock)** → OK → öffnen → **„Inhalt aktivieren"**.

**Weg 2 (Firmen-PC, kein „Zulassen"-Haken):** Excel → Datei → Optionen → **Trust Center** →
Einstellungen → **Vertrauenswürdige Speicherorte** → Ordner hinzufügen (z.B. `C:\MiT`) →
Datei dort ablegen → öffnen. Die Sperre ist dauerhaft weg.

**Weg 3:** Das ZIP mit 7-Zip/WinRAR entpacken — Windows setzt die Internet-Markierung dann meist gar nicht.

Ohne Makros funktioniert trotzdem alles Übrige (Formeln, Verknüpfungen, Dropdowns, Filter, Diagramme) —
nur die Import-/Export-Automatik braucht die Freigabe. Die Anleitung steht auch gross auf `00_START`.
