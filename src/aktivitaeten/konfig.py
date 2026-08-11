"""Stellschrauben der Pipeline — hier anpassen, nicht im Code weiter unten.

Alles in dieser Datei ist bewusst als einfache Liste/Dict gehalten, damit
Ergänzungen ohne Python-Kenntnisse möglich sind.
"""

from __future__ import annotations

# Eigene Domains: Adressen daraus gelten nie als Gegenstelle/Kunde.
EIGENE_DOMAINS = {"mobilintime.com"}

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
}

# Eigene Kategorie-Regeln. Werden VOR den Standardregeln geprueft.
# Format: (Regex auf "Titel + Notizen", Kategorie)
KATEGORIE_REGELN: list[tuple[str, str]] = [
    # (r"loadbank|cross[- ]hire", "Partner / Lieferant"),
]

# Hosts, deren Links/Adressen technisch sind (Konferenzsysteme, Tracking).
TECHNISCHE_HOSTS = (
    "teams.microsoft.com", "aka.ms", "dialin.teams", "teams.cloud.microsoft",
    "webex.com", "pexip.me", "gleanin.com", "microsoft.com", "vc.aggreko.com",
)
