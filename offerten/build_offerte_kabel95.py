# -*- coding: utf-8 -*-
"""
Erzeugt die Offerte für die 95mm²-Kabelpositionen (Excel, .xlsx) – im selben
Layout wie die EKAG-Offerte, aber als Verkaufs-/Richtpreisofferte.

    python3 offerten/build_offerte_kabel95.py
        ->  offerten/Offerte_Kabel_95mm.xlsx

Quelle: "Kabel_Mobil_in_Time_AG.pdf", Abschnitt "Version 95mm² Kabelpreise/100m".
    Total 95/25 = CHF 11'146.50
"""
import os, datetime as _dt
from offerte_lib import build_offerte_workbook, HEADERS_PURCHASE

# Kalkulationsaufschlag: 30 % Marge, verdeckt in die Einzelpreise eingerechnet
# (keine separate Aufschlagszeile -> der Kunde sieht nur die Artikelpreise).
MARKUP = 1.30


def _mk(price):
    return round(price * MARKUP, 2)


# Basis-Einkaufs-/Richtpreise (netto, ohne Aufschlag)
_BASE_POS = [
    (12, "71984 · CB 24-630/95-300 Steckendverschluss Typ C",            "Stk", 234.20,  1),
    (3,  "73643 · XKDT 1-Leiter MS-Polymerkabel 95/25 20/12kV, 6 x 50m", "Set", 2138.70, 1),
    (12, "Regie Arbeit",                                                 "Std", 160.00,  1),
]
_BASE_ART = [
    ("71984 · CB 24-630/95-300 Steckendverschluss Typ C",             "Stk", 234.20),
    ("73643 · XKDT 1-Leiter MS-Polymerkabel 95/25 20/12kV, 6 x 50m",  "Set", 2138.70),
    ("73644 · XKDT 1-Leiter MS-Polymerkabel 150/35 20/12kV, 6 x 50m", "Set", 2811.27),
    ("Regie Arbeit",                                                  "Std", 160.00),
]

# Positionen + Artikelliste mit eingerechnetem Aufschlag (Menge, Beschr., Einheit, Preis, Faktor)
POSITIONS = [(a, d, u, _mk(p), f) for (a, d, u, p, f) in _BASE_POS]
ARTIKEL   = [(d, u, _mk(p)) for (d, u, p) in _BASE_ART]

COMPANY = dict(
    name="Mobil in Time AG", strasse="Mattenstrasse 3", plz="8253 Diessenhofen",
    tel="+41 44 806 13 00", mail="info@mobilintime.com", web="www.mobilintime.com",
    zusatz="Ein Unternehmen der Mobil in Time Gruppe", agb="www.mobilintime.com",
)
SACHBEARBEITER = dict(name="Burak Ücöz", tel="+41 76 202 01 70", mail="uecoez@mobilintime.com")
# Richtpreis netto: kein Rabatt, keine MwSt (wie in der Quelle)
DEFAULTS = dict(rabatt=0.00, mwst=0.00, waehrung="CHF")
TEXTS = dict(
    einleitung=("Wir bedanken uns für Ihr Interesse an einer Zusammenarbeit mit uns. "
                "Gemäss unseren Allgemeinen Geschäftsbedingungen, einsehbar auf {AGB}, "
                "unterbreiten wir Ihnen für die 95mm²-Kabelausrüstung folgendes "
                "Richtpreisangebot (Preise pro 100 m)."),
    gruss="Mit freundlichen Grüssen",
    anmerkung=("Nicht im Angebot enthalten sind Verlegung, Transport, Briden und Montage. "
               "Regie-Arbeit erfolgt gemäss Aufwand. Richtpreise, freibleibend."),
)
# Kunde: Platzhalter zum Ausfüllen
CUSTOMER = ["Herr Mustermann", "Musterfirma AG", "Musterstrasse 1, 8000 Zürich", ""]
META = [
    ("Offerte-Nr.", "RP-95-" + _dt.date.today().strftime("%Y%m%d"), None),
    ("Datum",       _dt.date.today(), "DD.MM.YYYY"),
    ("Version",     "95mm² / Kabelpreise pro 100 m", None),
    ("Gültigkeit",  "30 Tage", None),
]

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "Offerte_Kabel_95mm.xlsx")
    info = build_offerte_workbook(
        out, company=COMPANY, sachbearbeiter=SACHBEARBEITER, defaults=DEFAULTS,
        texts=TEXTS, customer=CUSTOMER, meta=META, positions=POSITIONS,
        artikel=ARTIKEL, headers=HEADERS_PURCHASE,
        subtitle="Preisaufstellung – Version 95mm² (Kabelpreise pro 100 m)",
        n_blank=6,
    )
    print("Gespeichert:", info["out"])
    print(f"Datenzeilen {info['first']}–{info['last']} · Endbetrag-Zeile {info['end']}")
