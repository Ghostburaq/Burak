# -*- coding: utf-8 -*-
"""
Baut die Offerten-Master-Vorlage (Excel, .xlsx) – die wiederverwendbare
Mietofferte nach dem EKAG-Beispiel.

    python3 offerten/build_template.py   ->  offerten/Offerten_Master_Vorlage.xlsx

Aufbau: 3 Blätter (Offerte / Stammdaten / Artikel). Alle Summen, Rabatt, MwSt
und der Mietzeitraum rechnen sich selbst. Layout siehe offerte_lib.py.
"""
import os, datetime as _dt
from offerte_lib import build_offerte_workbook, HEADERS_RENTAL

# Positionen (Anz, Beschreibung, Einheit, Einzelpreis/Woche, Wochen)
POSITIONS = [
    (1,  "6MVA Trafo 16,5kV YNyn0",                                       "Stk",  5409.82,   1),
    (1,  "3MVA Trafo 16,5kV YNyn0",                                       "Stk",  1588.15,   1),
    (2,  "25 Meter x Kabel 32A",                                          "Stk",  13.70/2,   1),
    (1,  "Load Bank 6000 kVA Resistive and Reactive : 400V 3-ph @ 50 Hz", "Stk",  4960.73,   1),
    (1,  "Load Bank 3300 kVA Resistive and Reactive : 400V 3-ph @ 50 Hz", "Stk",  3087.82,   1),
    (63, "10 Meter x Einzeladerkabel 240mm² (Set A)",                     "Stk",  282.47/63, 1),
    (32, "10 Meter x Einzeladerkabel 240mm² (Set B)",                     "Stk",  143.47/32, 1),
    (1,  "25 Meter x Kabel 125A",                                         "Stk",  12.57,     1),
    (1,  "25 Meter x Kabel 63A",                                          "Stk",  9.46,      1),
    (1,  "Umweltschutzpauschale",                                         "Psch", 1085.57,   1),
    (1,  "Befreiung von der Versicherungspflicht",                        "Psch", 1860.98,   1),
]

ARTIKEL = [
    ("6MVA Trafo 16,5kV YNyn0",                                       "Stk",  5409.82),
    ("3MVA Trafo 16,5kV YNyn0",                                       "Stk",  1588.15),
    ("1MVA Trafo 16,5kV YNyn0",                                       "Stk",   850.00),
    ("Load Bank 6000 kVA Resistive and Reactive : 400V 3-ph @ 50 Hz", "Stk",  4960.73),
    ("Load Bank 3300 kVA Resistive and Reactive : 400V 3-ph @ 50 Hz", "Stk",  3087.82),
    ("25 Meter x Kabel 32A",                                          "Stk",     6.85),
    ("25 Meter x Kabel 63A",                                          "Stk",     9.46),
    ("25 Meter x Kabel 125A",                                         "Stk",    12.57),
    ("10 Meter x Einzeladerkabel 240mm² (Set A)",                     "Stk",     4.483651),
    ("10 Meter x Einzeladerkabel 240mm² (Set B)",                     "Stk",     4.483438),
    ("10 Meter x Einzeladerkabel 240mm²",                             "Stk",     4.48),
    ("Umweltschutzpauschale",                                         "Psch", 1085.57),
    ("Befreiung von der Versicherungspflicht",                        "Psch", 1860.98),
    ("Lieferung / Abholung (pauschal)",                               "Psch",  450.00),
    ("Montage / Inbetriebnahme (pro Std.)",                           "Std",   135.00),
]

COMPANY = dict(
    name="Mobil in Time AG", strasse="Mattenstrasse 3", plz="8253 Diessenhofen",
    tel="+41 44 806 13 00", mail="info@mobilintime.com", web="www.mobilintime.com",
    zusatz="Ein Unternehmen der Mobil in Time Gruppe", agb="www.mobilintime.com",
)
SACHBEARBEITER = dict(name="Burak Ücöz", tel="+41 76 202 01 70", mail="uecoez@mobilintime.com")
DEFAULTS = dict(rabatt=0.10, mwst=0.00, waehrung="CHF")
TEXTS = dict(
    einleitung=("Wir bedanken uns für Ihr Interesse an einer Zusammenarbeit mit uns. "
                "Aufgrund der von Ihnen gemachten Angaben und gemäss unseren Allgemeinen "
                "Geschäftsbedingungen, einsehbar auf {AGB}, bieten wir Ihnen folgende "
                "Leistungen freibleibend an."),
    gruss="Mit freundlichen Grüssen",
    anmerkung=("Dieses Budgetangebot ist für beide Parteien unverbindlich. Alle Anmietungen "
               "erfolgen vorbehaltlich der Verfügbarkeit bei Aufgabe der Bestellung und zu den "
               "Preisen, die im offiziellen Angebot aufgeführt sind, sobald die zusätzlichen "
               "Detailinformationen vorliegen, die sich auf Ihr Equipment und Ihren Servicebedarf "
               "beziehen."),
)
CUSTOMER = ["Herr Reto Gloor", "EK AG", "Tel. +41 62 767 80 62", "reto.gloor@ekag.ch"]
META = [
    ("Offerte-Nr.",  "Q663790202605072109", None),
    ("Datum",        _dt.date.today(),      "DD.MM.YYYY"),
    ("Mietbeginn",   _dt.date(2027, 2, 9),  "DD.MM.YYYY"),
    ("Mietende",     _dt.date(2027, 3, 1),  "DD.MM.YYYY"),
    ("Mietzeitraum", '=G11-G10+1&" Tage"',  None),
    ("Mindestmiete", "7 Tage",              None),
]

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "Offerten_Master_Vorlage.xlsx")
    info = build_offerte_workbook(
        out, company=COMPANY, sachbearbeiter=SACHBEARBEITER, defaults=DEFAULTS,
        texts=TEXTS, customer=CUSTOMER, meta=META, positions=POSITIONS,
        artikel=ARTIKEL, headers=HEADERS_RENTAL,
        subtitle="Preisaufstellung – Preise reflektieren Mengen",
    )
    print("Gespeichert:", info["out"])
    print(f"Datenzeilen {info['first']}–{info['last']} · Endbetrag-Zeile {info['end']}")
