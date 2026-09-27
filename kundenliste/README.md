# Zielkundenliste Schweiz: Mobile Energie

**Datei:** [`Kundenliste_MiT_Schweiz.xlsx`](Kundenliste_MiT_Schweiz.xlsx) (Stand 27.09.2026, VERTRAULICH)

- **Übersicht:** KPIs, Segmentmix Soll/Ist (60/20/20), Regionen x Prio, Gebiet West/Deutschschweiz/Tessin, Kategorien, Kundenstatus. Alles per Formel.
- **Kundenliste:** 125 Firmen, davon Kernliste 70 (42 Installateure / 14 FM-EVU-Planer / 14 GU/TU+Industrie). Score aus Fit, Volumen, Timing, Zugang, daraus Prio A/B/C mit Begründung, Anlass 2025-2027, Quelle, LinkedIn-Suchlinks. Dropdowns für Prio final, Kundenstatus, Verantwortlich.
- **Methodik:** Gewichte und Schwellen (änderbar), Legende, Grenzen der Recherche.

Neu erzeugen: `python build_kundenliste.py` (Daten in `daten.py`).

## Präsentation

**Datei:** [`Zielkunden_Schweiz_Praesentation.pptx`](Zielkunden_Schweiz_Praesentation.pptx), 13 Folien im Original-Master der Mobil in Time AG, mit Sprechernotizen, Diagramme nativ (in PowerPoint editierbar).
Schriften: Alata (Titel) und IBM Plex Sans (Text) müssen installiert sein, sonst Fallback.
Neu erzeugen: `python build_deck_mit.py` (braucht `python-pptx` und die MiT-Assets aus dem Skill `mit-praesentation`, Pfad per `MIT_ASSETS` überschreibbar).
