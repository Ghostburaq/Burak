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
- **Universal Drop-Zone** – beliebige Dateien (`.xlsx`, `.csv`, `.pdf`, `.docx`, `.json`) ablegen, alles wird automatisch auf die richtigen Tabs verteilt:
  - **Pipeline-XLSX** (Spalten Kunde/Segment/kW/Status/Volumen): → Deals + Kontakte
  - **Aggregatliste-XLSX** (Generator/Standort): → Lastliste + Aufgaben
  - **Kontakte-XLSX** (Firmenname/Ansprechpartner/...): → Kontakte
  - **Bestellung/Rechnung-PDF** (Feliton-Format etc.): → Deal + Angebotspositionen + Kontakt + Aufgabe
  - **Ausschreibung-PDF**: → simap-Eintrag + Notiz
  - **Projekt-Word** (GAM-Stil mit Zonen-/Bestellungstabellen): → Deal + Lastliste + Angebotspositionen + Aufgaben (Lieferung/Demontage)
  - **JSON-Backup**: → komplettes Restore
- Live-Vorschau zeigt, was importiert wird (Counts pro Kategorie), bevor man bestätigt
- Drag-&-Drop oder Klick
- IndexedDB-Auto-Backup mit Wiederherstellung (siehe oben)
- **Live-Excel-Sync** (Dashboard-Panel + Header-Button „🔄 Sync"): Excel-Pipeline-Datei einmal verbinden (File System Access API, Chrome/Edge), danach genügt ein Klick, um die Datei neu einzulesen und Deals/Kontakte/Dashboards **bidirektional** abzugleichen — bestehende Deals werden aktualisiert (idempotent, keine Duplikate), neue hinzugefügt. „→ Pipeline nach Excel schreiben" exportiert den aktuellen Stand zurück in dieselbe Datei (oder als Download). Browser ohne die API fallen automatisch auf den Datei-Dialog zurück.
  - **Sync-Vorschau**: vor dem Übernehmen zeigt ein Dialog genau, was sich ändert (Wert/Phase/Wahrscheinlichkeit pro Deal, neue Deals, neue Kontakte) — kein stilles Überschreiben.
  - **Konfliktschutz**: manuell im Tool geänderte Deals (Marker ✎) werden beim Sync nicht blind überschrieben, sondern als Konflikt angezeigt — optional gezielt überschreibbar.
  - **Auto-Sync** alle 10 Minuten (optional, nur bei erteilter Dateifreigabe).
- **Deal-Detailansicht**: Klick auf einen Deal (Kanban/Dashboard) öffnet eine Vollansicht mit allen Feldern, verknüpftem Kontakt (inkl. Lead-Score), Aufgaben und Aktivitäts-Timeline.
- **Dashboard-Auswertungen**: Volumen nach Segment (Doughnut), Volumen nach Kanton (Top 8), und Pipeline-Verlauf über Zeit (offene Pipeline + kumuliert Gewonnen, aus den IndexedDB-Snapshots).
- **Scan-PDF-OCR**: gescannte Bestell-/Rechnungs-PDFs ohne Textebene werden per Claude Vision automatisch ausgelesen (Kunde, Positionen, Total) und verteilt — benötigt API-Key.
- **Margin-Watchdog**: liest Equip/Transport/Treibstoff/Technik/Übrige/Marge-Spalten aus dem Pipeline-Excel mit, zeigt Ø-Marge als KPI, listet Risiko-Deals unter konfigurierbarer Schwelle (Default 15 %) und zeigt die Margen-Aufschlüsselung in der Deal-Detailansicht; der Sync-Diff flaggt auch Margen-Änderungen.
- **Document Library**: an jeden Deal beliebig viele Dateien anhängen (PDF/DOCX/Excel/Bilder/Text), gespeichert in IndexedDB (Blob + Metadaten + extrahiertem Volltext bei PDF/DOCX/Text); Inline-Liste in der Detailansicht mit Drop-Zone, Download, Löschen. **Globale Suche durchsucht auch den extrahierten Volltext aller Anhänge.**
- **Slack/Teams-Webhook**: einmal Webhook-URL oben rechts eintragen → automatische Posts bei *WON*-Übergang, neuer simap-Ausschreibung und größeren Sync-Änderungen. Funktioniert mit Slack-Incoming-Webhooks und Teams-Connector-URLs.
- **Voice-Notes**: 🎙-Button auf der Heute-Page → Web Speech API (Chrome/Edge) nimmt auf, Claude fasst zusammen und schreibt es als Aktivitätsnotiz; perfekt für Notizen im Auto nach einem Termin.
- **Quick-Hotkeys**: `g d/p/c/k/m/f/t/x/s/e/r/n` springt zu Dashboard/Pipeline/Kontakte/Kantone/Karte/Forecast/Heute/Aufgaben/simap/E-Mail/Rapport/Notizen, `n d/t/n/c/a` legt Deal/Task/Notiz/Kontakt/Ausschreibung an, `Ctrl+K` Suche, `Esc` schließt.
- **Visitenkarten-Scan**: 📇-Button (Kontakte) → Foto/Kamera → Claude Vision liest Name/Firma/Tel/Mail/Kanton → Kontaktformular vorausgefüllt.
- **Kalender (.ics)**: Aufgaben + Liefertermine als `.ics` exportieren (Outlook/Google/Apple), externe `.ics` read-only importieren — alles im Planung-Tab.
- **Verfügbarkeits-Tracker** (Planung-Tab): erkennt zeitliche Geräte-Doppelbuchungen (Start + Dauer + kVA überlappend) und zeigt eine 60-Tage-Terminliste.
- **Geo-Tourenplanung** (Karte): „🚗 Tour planen" ordnet Kontakte per Nearest-Neighbour und öffnet eine Google-Maps-Mehrstopp-Route ab Zürich HB.
- **Angebots-Vorlagen + Versionierung**: vorbereitete Positions-Bausteine (Event Single/Twin, Notstrom Spital, BESS Hybrid) + eigene Vorlagen; jedes Angebot als Version sichern und wiederherstellen.
- **Cloud-Backup (GitHub Gist)**: privates Gist als Off-Site-Backup — Token eintragen, ⬆ sichern / ⬇ laden.
- **Read-only-Snapshot**: eigenständige HTML-Pipeline-Übersicht exportieren und mit Innendienst/Vorgesetzten teilen.
- **Gamification** (Heute): Tages-Streak 🔥, Calls-heute-Ziel mit Fortschritt, 7-Tage-Aktivitäten.
- **Mobile-Touch**: ausklappbares Menü (☰), Swipe der Deal-Karten zwischen Phasen (+◀▶-Buttons), Floating-Call-Button, responsives Layout.
- **Eingebettete Stand-alone-Tools** (eigene Sidebar-Einträge, laufen in eigenem iframe — keine Kollision mit dem CRM):
  - **✉️ E-Mail Studio**: vollwertige KI-Email-Suite (Generator · Lead-Datenbank · Produkt-Portfolio · Statistik) — die Netlify-Variante 1:1 eingebettet, eigene Tabs, eigene Datenbank, eigener API-Key.
  - **🛠️ Power Platform**: 14-Module-Engineering-Workspace (Generator/BESS/Trafo/Lastbank/Kabel/Parallel/USV/IBC/ROI/PQ-Check/Angebot/Schall/Notstrom/Emissionen) mit ISO-3046-Derating, AVR-Klassen, Lastliste, ergänzt das CRM-Engineering.
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
