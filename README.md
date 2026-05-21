# MiT CRM Pro · Mobil in Time AG

Professionelles, vollständig browserbasiertes CRM in einer einzigen HTML-Datei. Keine Installation, kein Server, kein Build-Schritt – einfach `MiT_CRM_Pro.html` im Browser öffnen.

## Funktionen

**Übersicht**
- Dashboard mit KPIs (Pipeline CHF, Gewonnen, Kontakte, Anrufe, Win Rate) und Aktivitäts-Charts (Chart.js)
- **Heute / KI-Cockpit**: Tages-Briefing, „Wen heute anrufen?" (Top-Kandidaten per Lead-Score, optional mit KI-Begründung) und Auto-Enrichment fehlender Felder (Branche, kVA-Schätzung)
- **Lead-Scoring**: automatischer 0–100-Score je Kontakt (Priorität, Status, Erreichbarkeit, kVA-Potenzial, offener Deal-Wert, Aktivitäts-Aktualität) – Kontaktliste sortierbar nach Score / Firma / Priorität (offline, ohne API-Key)
- **PWA**: installierbar (Manifest inline), Theme-Color, Add-to-Home-Screen
- **Auto-Backup**: automatische Snapshots in IndexedDB (letzte 20 Stände) mit Wiederherstellung über das 🗄️-Menü, plus Export-Erinnerung nach 7 Tagen ohne Backup
- Pipeline (Kanban: Prospecting → Qualified → Proposal → Negotiation → Won/Lost)
- Kontakte mit Such- und Branchenfilter, XLSX-Export
- Schweiz-Karte (Leaflet + Cluster) mit Kunden, Deals, Kantons-Heatmap
- Kantons-Übersicht CH (alle 26 Kantone)
- Forecast / Ziele mit Fortschrittsbalken

**Akquise**
- Kaltakquise-Dialer mit Timer, Tages-Stats und KI-Coach (Skripte, Einwand-Behandlung)
- E-Mail-Generator (Kalt, Follow-Up, Nach Angebot, Reaktivierung) mit Tonalitäts-Steuerung
- 5-Schritte-Follow-Up-Sequenzgenerator
- WhatsApp-Sender mit Vorlagen (Erstkontakt, Nach Meeting, Angebot, Bestätigung)
- KI-Firmen-Recherche

**Engineering**
- Produkt-Datenbank (Generatoren, BESS, Power Quality, Wärme/Kälte, Zubehör)
- Angebots-Generator mit Positionen, KI-Text, PDF-Export (jsPDF)
- ROI-Rechner: Ausfallkosten, THD/PQ, Diesel vs BESS, Miet-TCO
- Engineering-Toolbox: Generator-Dimensionierung, Kabel NIN 2020, BESS IEC 62619, Parallelschaltung IEC 60034-3, Baustromverteiler, Kombisystem-KI, Lastliste, USV IEC 62040, Schallpegel ISO 3744 / LSV CH, IBC Tank ADR
- CO₂ / Stage V mit ESG-Argument
- Notstrom NIV Art.13

**Tools**
- Aufgaben mit Prioritäten und Fälligkeit
- simap.ch-Radar inkl. PDF-Analyse von Ausschreibungen (Claude Vision)
- Wettbewerbs-Analyse (SWOT pro Konkurrent)
- TIGORZ Content-Studio (LinkedIn / TikTok / YouTube)
- Tagesrapport mit Doughnut-Chart und PDF-Export
- Notizen mit Suche und Kategorien

**Datenmanagement**
- Excel/CSV-Import mit automatischer Spaltenerkennung (Firmenname, Ansprechpartner, Telefon, E-Mail, Kanton, Status, Prio, kVA, Produkt etc.) – verteilt auf Kontakte, Karte, Pipeline, Aufgaben
- Drag-&-Drop-Import
- JSON-Backup Export/Import
- Volltext-Suche (Ctrl+K)
- Light/Dark-Theme
- Anthropic Claude API für alle KI-Funktionen

## Verwendung

```bash
# Datei direkt im Browser öffnen
open MiT_CRM_Pro.html
# oder
xdg-open MiT_CRM_Pro.html

# Optional: lokaler Server
python3 -m http.server 8000
```

Beim ersten Start: API-Key oben rechts eintragen (`sk-ant-…`), dann Excel/CSV importieren oder Demo-Daten manuell anlegen.

## Daten

Alle Daten werden im `localStorage` unter dem Key `mit_crm_v2` gespeichert. Backup jederzeit über den Export-Button (JSON) möglich.

## Dateien im Repo

- `MiT_CRM_Pro.html` – **die Haupt-App** (alles inline)
- `mini-crm.html` – schlanker Vorgänger (für einfache CRM-Anwendungen)
- `index.html` / `styles.css` / `app.js` – Quell-Variante des Mini-CRM (separate Dateien)
