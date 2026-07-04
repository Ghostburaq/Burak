# MiT × Aggreko — GESAMTMAPPE 2026

**Eine einzige Excel-Arbeitsmappe als Workspace** — ersetzt 15 Einzeldateien.
Deliverable: [`MiT_GESAMTMAPPE_2026.xlsm`](MiT_GESAMTMAPPE_2026.xlsm) (28 Reiter, 9'003 Formeln, VBA-Import-Automatik).

## Aufbau (28 Reiter, logisch getrennt & verknüpft)

| Bereich | Reiter | Inhalt |
|---|---|---|
| Navigation | `00_START`, `01_DASHBOARD` | Navigation + Live-KPIs über alle Bereiche |
| Vertrieb Strom CH | `02_PIPELINE` … `07_KUNDENANALYSE` | 47 Deals (aus 3 Versionen dedupliziert), 798 CRM-Firmen, 1'133 Kundenkontakte, Forecast, Monatsreport |
| Datacenter CH | `08_DC_BETREIBER` … `12_DC_DOSSIERS` | 30 Betreiber, 16 Bauprojekte (3 Quellen gemerged), 38 Standorte, Kontakte, Dossiers |
| Global | `13_GLOBAL_PROJEKTE` … `15_GLOBAL_ANALYTICS` | 10'572 DC-Projekte, 8'502 Kontakte, Live-Analytics |
| Produkte & Preise | `16_KATALOG` … `18_PREISLISTE_INTL` | 466 Produkte, Preislisten CHF + International |
| Werkzeuge | `19_GEN_RECHNER` … `24_SYSTEME_WISSEN` | Generator-Rechner, Angebotskalkulator, Marktvolumen, Normen, Akquiseplan |
| System | `90_IMPORT`, `91_LISTEN`, `99_INFO` | Import-Zentrale, Dropdown-Quellen, Doku |

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

## Hinweis

Beim ersten Öffnen in Excel: **„Inhalt aktivieren"** klicken (Makros), sonst funktionieren
Import & Shortcuts nicht — alle Formeln/Verknüpfungen laufen auch ohne Makros.
