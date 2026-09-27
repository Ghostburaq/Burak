# Zielkundenliste Schweiz: Mobile Energie

**Datei:** [`Kundenliste_MiT_Schweiz.xlsx`](Kundenliste_MiT_Schweiz.xlsx) (Stand 27.09.2026, VERTRAULICH)

- **Übersicht:** KPIs, Segmentmix Soll/Ist (60/20/20), Regionen x Prio, Gebiet West/Deutschschweiz/Tessin, Kategorien, Kundenstatus. Alles per Formel.
- **Kundenliste:** 125 Firmen, davon Kernliste 70 (42 Installateure / 14 FM-EVU-Planer / 14 GU/TU+Industrie). Score aus Fit, Volumen, Timing, Zugang, daraus Prio A/B/C mit Begründung, Anlass 2025-2027, Quelle, LinkedIn-Suchlinks. Dropdowns für Prio final, Kundenstatus, Verantwortlich.
- **Methodik:** Gewichte und Schwellen (änderbar), Legende, Grenzen der Recherche.

Neu erzeugen: `python build_kundenliste.py` (Daten in `daten.py`).

## Präsentation

**Datei:** [`Zielkunden_Schweiz_Praesentation.pptx`](Zielkunden_Schweiz_Praesentation.pptx), 12 Folien mit Sprechernotizen, Diagramme nativ (in PowerPoint editierbar).
Neu erzeugen: `node build_deck.js` (benötigt `pptxgenjs`, `react-icons`, `react`, `react-dom`, `sharp`).
