# Pitch-Deck · Bewerbung Vertriebsmanager — AVIA VOLT Suisse

Code-generiertes, voll markenkonformes Pitch-Deck (10 Slides, Deutsch) für die
Bewerbung von **Burak Ücöz** als Vertriebsmanager bei **AVIA VOLT Suisse**.
Das Deck wird vollständig per Python (`python-pptx`) erzeugt — Slide für Slide,
deterministisch und ohne externe Abhängigkeiten zur Laufzeit.

**Ergebnis:** [`Pitch_Burak_AVIA_VOLT.pptx`](Pitch_Burak_AVIA_VOLT.pptx)
&nbsp;·&nbsp; Ansehen ohne PowerPoint: [PDF-Vorschau](docs/Pitch_Burak_AVIA_VOLT_vorschau.pdf)

![Übersicht aller Slides](docs/preview.png)

## Was drin steckt

- **10 Slides** mit klarem Spannungsbogen: Titel → Auftrag → Warum ich →
  Anforderung/Beweis → Track Record → Unfairer Vorteil → Hausaufgaben →
  Umsatzfelder → 90-Tage-Plan → Call to Action.
- **Speaker-Notes auf jeder Slide — nur für den Vortragenden.** Kurze
  Regie-Hinweise (Betonung, Pausen, Kernsätze), sichtbar in der
  Referentenansicht, nicht für das Publikum.
- **Einheitliches Design-System:** Dunkles Navy `#1B2430` + AVIA-Rot `#E2001A`,
  durchgehende Kicker-/Headline-/Footer-Logik, abgestimmte Karten, Badges und
  Typografie (Trebuchet MS / Calibri).
- **Eigene, immer passende Grafik:** Hintergründe (Energie-/Lade-Motiv, dezenter
  Verlauf, Power-Quality-Welle) werden mit Pillow generiert; die Icons und das
  Portrait werden markenkonform aufbereitet. Keine externen Bild-Hosts → keine
  toten Links, kein Layout-Bruch.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `src/make_assets.py`   | Erzeugt Hintergründe + weiß eingefärbte Icon-Varianten |
| `src/build_deck.py`    | Baut die 10 Slides inkl. Speaker-Notes → `.pptx` |
| `src/render_preview.py`| Rendert die echte `.pptx` zur visuellen Kontrolle (PNG/PDF) |
| `assets/`              | Portrait, Original-Icons, generierte Assets |
| `docs/`                | Vorschaubilder + PDF-Vorschau |
| `src/build_excel.py`   | Baut das Vertriebs-Cockpit → `Vertriebs_Cockpit.xlsx` |
| `data/`                | Online-Abruf: Power-Query-`.m`-Vorlagen (OpenChargeMap, Zefix, eigene DB) |

## Vertriebs-Cockpit (Excel)

Umfangreiche, filterbare Excel-Arbeitsmappe für den Vertrieb (neutral, ohne Firmenbranding) —
**[`Vertriebs_Cockpit.xlsx`](Vertriebs_Cockpit.xlsx)** — code-generiert,
reproduzierbar und sofort einsatzbereit. **9 Blätter, 42 Beispiel-Deals.**

- **Dashboard** — KPIs (Pipeline gesamt, gewichteter Forecast, Win-Rate, Ø Deal-Größe …),
  **Sales-Funnel** sowie Auswertungen nach **Region / Branche / Verantwortlichem** (5 Diagramme).
- **Pipeline** — strukturierte Excel-Tabelle mit **AutoFilter & Sortierung**, **Dropdowns**
  (Datenvalidierung), **Formeln** (Wahrscheinlichkeit per `XLOOKUP` aus der Phase, gewichteter
  Wert, Tage bis Abschluss) und **Ampel-Logik** (bedingte Formatierung 🔴🟡🟢).
- **Aktivitäten** — Aufgaben/Termine mit Fälligkeits-Ampel (überfällig = rot). **Kontakte** — CRM-Liste.
- **Forecast** — gewichteter Umsatz je Monat vs. Ziel (Soll/Ist). **Ziele** — Zielerreichung je Verantwortlicher.
- **Live-Daten (E-Mobilität)** — Online-Abruf **per Knopfdruck (Taste F9)**: öffentliche **Ladeinfrastruktur
  Schweiz** live via **OpenChargeMap** (`WEBSERVICE` + `FILTERXML`, Windows-Desktop-Excel). Für mehr
  Quellen (Handelsregister **Zefix**, **SQL/Cloud**-DB, Google Sheets) fertige **Power-Query-M-Vorlagen**
  in `data/PowerQuery_Vorlagen.m` (auch Mac/Web).
- **Anleitung** — Schritt-für-Schritt-Blatt direkt in der Mappe · druckfertiges Layout · Formelzellen schützbar.

```bash
pip install openpyxl
python3 src/build_excel.py   # -> Vertriebs_Cockpit.xlsx + data/*
```

## Neu bauen

```bash
pip install python-pptx Pillow
python3 src/make_assets.py     # Assets generieren
python3 src/build_deck.py      # Deck erzeugen -> Pitch_Burak_AVIA_VOLT.pptx
python3 src/render_preview.py  # optional: Vorschau-PNGs nach /tmp/preview

# hochaufgeloeste PNGs + PDF-Vorschau erzeugen:
PREVIEW_W=2600 PREVIEW_PDF=docs/Pitch_Burak_AVIA_VOLT_vorschau.pdf \
  python3 src/render_preview.py
```

## Hinweise

- Format 16:9, exakt passend zur Originalvorlage.
- Schriften: Trebuchet MS (Headlines) + Calibri (Fließtext) — Standard-Office-
  Schriften, damit die Datei auf jedem Rechner identisch aussieht.
- Inhaltlich entspricht das Deck dem Original, sprachlich leicht geschärft;
  Layout und Grafik wurden durchgehend angehoben.
