"""Stellschrauben der Pipeline — hier anpassen, nicht im Code weiter unten.

Alles in dieser Datei ist bewusst als einfache Liste/Dict gehalten, damit
Ergänzungen ohne Python-Kenntnisse möglich sind.
"""

from __future__ import annotations

# Eigene Domains: Adressen daraus gelten nie als Gegenstelle/Kunde.
EIGENE_DOMAINS = {"mobilintime.com"}

# Die eigene Adresse — wird aus Teilnehmerlisten herausgefiltert.
EIGENE_ADRESSE = "uecoez@mobilintime.com"

# Firmennamen, die als Partner/Lieferant gelten — Rechnungspruefung und
# Bestellwesen mit ihnen ist keine reine Bueroarbeit.
PARTNER_FIRMEN = {"Aggreko"}

# Domains von Partnern, Lieferanten und Konzerngesellschaften.
# Termine mit diesen Gegenstellen werden als "Partner / Lieferant" gefuehrt,
# nicht als Kundentermin.
PARTNER_DOMAINS = {"aggreko.de", "aggreko.com"}

# Saubere Firmennamen je Mail-Domain (erste Ebene vor dem Punkt).
# Steht hier ein Eintrag, gewinnt er gegen den aus dem Termintitel geratenen Namen.
FIRMEN_ALIASE = {
    "zuerich": "Stadt Zürich",
    "agroscope": "Agroscope (WBF)",
    "admin": "Bundesverwaltung",
    "stackinfra": "STACK Infrastructure",
    "aggreko": "Aggreko",
    "green": "Green Datacenter AG",
    "smartec": "Smartec AG",
    "hombrechtikon": "Gemeinde Hombrechtikon",
    "vzug": "V-Zug AG",
    "ei-ag": "Elektro-Installationen EI AG",
    "emmi": "Emmi Schweiz AG",
    "amag": "AMAG",
    "ekz": "EKZ Elektrizitätswerke Kanton Zürich",
    "implenia": "Implenia",
    "hiag": "HIAG Immobilien",
    "einsgruppe": "eins Gruppe AG",
    "roth": "Roth Gruppe AG",
    "pamax": "Pamax AG",
    "pbpag": "pbp ag engineering",
}

# Firmennamen, die auch ohne Rechtsform im Termintitel erkannt werden sollen.
FIRMEN_STICHWORTE = {
    "smartec": "Smartec AG",
    "smartec ag": "Smartec AG",
    "digital realty": "Digital Realty Switzerland",
    "green datacenter": "Green Datacenter AG",
    "stack": "STACK Infrastructure",
    "beringen": "STACK Infrastructure",
    "sierre": "Ville de Sierre / Kanton VS",
    "hombrechtikon": "Gemeinde Hombrechtikon",
    "emmi": "Emmi Schweiz AG",
    "v-zug": "V-Zug AG",
    "amag": "AMAG",
    "aggreko": "Aggreko",
    "dpr": "DPR / Vantage ZRH12",
    "gampel": "Rock Hock Verein Gampel",
    "rock hock": "Rock Hock Verein Gampel",
    "ekz": "EKZ Elektrizitätswerke Kanton Zürich",
    "ekt": "EKT (Kanton Thurgau)",
    "enastra": "Enastra AG",
    "flexbase": "FlexBase Laufenburg",
    "axpo": "Axpo",
    "agroscope": "Agroscope (WBF)",
    "aggroscope": "Agroscope (WBF)",
    "ewo": "EWO Gebäudetechnik AG",
    "lidl": "Lidl Schweiz",
    "erne": "Erne AG Bauunternehmung",
    "gtr": "Global Technical Realty",
    "global technical realty": "Global Technical Realty",
    "amstein": "Amstein + Walthert",
    "amstein+walthert": "Amstein + Walthert",
    "drost": "Amstein + Walthert",
    "hiag": "HIAG Immobilien",
    "einsgruppe": "eins Gruppe AG",
    "eins gruppe": "eins Gruppe AG",
    "roth": "Roth Gruppe AG",
    "pamax": "Pamax AG",
    "pbp": "pbp ag engineering",
    "pbpag": "pbp ag engineering",
    "crans-montana": "Crans-Montana 2027 (FIS Ski-WM)",
}

# Eigene Kategorie-Regeln. Werden VOR den Standardregeln geprueft.
# Format: (Regex auf "Titel + Notizen", Kategorie)
KATEGORIE_REGELN: list[tuple[str, str]] = [
    (r"\b(amag|skoda)\b", "Privat"),                 # eigenes Auto
    (r"\b(dpr|vantage)\b", "Projekt"),               # Projekt ZRH12
    (r"\bekt\b", "Akquise"),                         # EKT Basadingen, Offerte laeuft
    # (r"loadbank|cross[- ]hire", "Partner / Lieferant"),
]

# Hosts, deren Links/Adressen technisch sind (Konferenzsysteme, Tracking).
TECHNISCHE_HOSTS = (
    "teams.microsoft.com", "aka.ms", "dialin.teams", "teams.cloud.microsoft",
    "webex.com", "pexip.me", "gleanin.com", "microsoft.com", "vc.aggreko.com",
)
