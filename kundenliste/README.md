# Top-Player Power Schweiz 2027

Stand 27.09.2026 · VERTRAULICH, intern

- **[`Top_Player_Power_Schweiz_2027.xlsx`](Top_Player_Power_Schweiz_2027.xlsx)**: 38 Projekte mit mehr als CHF 50'000 Power-Potenzial (Rechenzentren, Infrastruktur, Netz, Spitäler, Industrie, Events, Kanal-Partner). Blätter: Start (Erklärung, Kennzahlen, Top 10), Top-Player, Annahmen (Sätze, gelb = änderbar, Spalte E = MiT-Satz), Beobachten, Wettbewerb, Methode & Quellen.
- **[`Top_Player_Power_Praesentation.pptx`](Top_Player_Power_Praesentation.pptx)**: 14 Folien im MiT-Master, Diagramme nativ, Sprechernotizen.

Rechenlogik: Potenzial = Generator (MVA × Wochen × Satz) + Lastbank (MW × Wochen × Satz) + BESS (MW × Monate × Satz).
Erwartung 2027 = Potenzial × Anteil 2027 × Gewinnwahrscheinlichkeit. Sätze sind US-Markt-Richtwerte (umgerechnet 0,828 CHF/USD, 24.09.2026), keine MiT-Preise.

Neu erzeugen (Daten in `daten_power.py`):
- `python build_top_player.py` (openpyxl; danach Formeln mit LibreOffice neu berechnen)
- `python build_deck_power.py` (python-pptx, MiT-Assets aus dem Skill `mit-praesentation`, Pfad per `MIT_ASSETS`)
