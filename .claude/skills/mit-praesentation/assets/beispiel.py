# -*- coding: utf-8 -*-
"""Beispieldeck: zeigt jeden Baustein einmal. Als Startpunkt kopieren."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mit_deck import Deck, RED, DARK, LIGHT

d = Deck("beispiel.pptx", footer="MiT Strom · Beispielprojekt · 27.09.2026")

d.cover(["Titelzeile eins,", "Titelzeile zwei"], "Untertitel der Praesentation",
        eyebrow="Mobil in Time AG · An Aggreko Company · Strom Schweiz",
        author="Burak Ücöz · Sales Engineer Power · 27.09.2026",
        stats=[("29", "Projekte"), ("145", "Kontakte")])

s = d.content("01 · Kacheln", "Drei Kacheln, eine davon rot")
d.cards(s, [("Kachel A", ["Erste Zeile.", "Zweite Zeile."]),
            ("Kachel B", ["Text."]),
            ("Kachel C", ["Das ist der Punkt."], RED)], cols_n=3)
d.notes(s, "Sprechnotiz zur Kachelfolie.")

s = d.content("02 · Kennzahlen", "Zahlen und Aussage")
d.kpis(s, [("29", "Projekte im Tracker"), ("145", "Kontakte"),
           ("68", "Bau- und Planerseite"), ("43 %", "Datensaetze mit Maengeln")])
d.band(s, 5.05, "Das ist die Folgerung aus den Zahlen.",
       bold_prefix="Kernaussage:", fill=DARK)

s = d.content("03 · Prozess", "Vier Schritte")
d.steps(s, [("01", "Datenbasis", ["Tracker gefiltert und priorisiert."]),
            ("02", "Recherche", ["Handelsregister und Leistungsbild."]),
            ("03", "Ansprache", ["Aufhaenger nach Bauphase."]),
            ("04", "Nachfassen", ["Anruf mit Datum angekuendigt."])])

s = d.content("04 · Tabelle", "Tabelle im MiT-Look")
d.table(s, [["Firma", "Typ", "Region", "Stand"],
            ["Beispiel AG", "GU", "national", "Kunde"],
            ["Muster GmbH", "Planer", "Zuerich", "angeschrieben"],
            ["Test SA", "TU", "Romandie", "neu"]],
        colw=[3.0, 2.9, 3.2, 3.0], h=2.4)
d.band(s, 5.00, "Kurzer Hinweis unter der Tabelle.", fill=LIGHT, h=0.85, fs=13.5)

d.closing("Der eine Hebel", ["Erste Aussage.", "Zweite Aussage.", "Dritte Aussage."],
          ["Burak Ücöz · Sales Engineer Power", "Mobil in Time AG · An Aggreko Company"])

print(d.save(title="Beispieldeck", author="Burak Ücöz"))
