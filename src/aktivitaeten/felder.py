"""Heuristiken zum Herausziehen von Inhalten aus Freitext.

Alles hier arbeitet rein textbasiert und faellt still auf leere Werte zurueck,
wenn nichts erkannt wird — die Pipeline soll nie an einem Sonderfall haengen.
"""

from __future__ import annotations

import re
import unicodedata

from .konfig import (EIGENE_DOMAINS, FIRMEN_ALIASE, KATEGORIE_REGELN,
                     PARTNER_DOMAINS, TECHNISCHE_HOSTS)

# ---------------------------------------------------------------------------
# Rauschen, das in Outlook-/Teams-Einladungen immer mitkommt
# ---------------------------------------------------------------------------

# Ab hier beginnt in Einladungen der maschinelle Anhang (Teams-Block,
# Rechtstexte). Alles davor ist der von Menschen geschriebene Teil.
KERN_ENDE = re.compile(
    r"(_{10,}"
    r"|\bMicrosoft Teams[- ](?:Besprechung|meeting)\b"
    r"|\bConfidentiality Notice\b"
    r"|\bVertraulichkeitshinweis\b)", re.I)

RAUSCH_MUSTER = [
    re.compile(r"_{10,}"),
    re.compile(r"^(Microsoft Teams[- ](Besprechung|meeting)|Teams Meeting)\s*$", re.I | re.M),
    re.compile(r"^(Teilnehmen|Join|Besprechungs-ID|Meeting ID|Passcode|Benötigen\s+Sie Hilfe|"
               r"Need\s+help|Systemreferenz|System reference|Per Telefon einwählen|Dial in by phone|"
               r"Suchen\s+einer lokalen Rufnummer|Find\s+a local number|Telefonkonferenz-ID|"
               r"Phone conference ID|Mit einem Gerät für Videokonferenzen teilnehmen|"
               r"Join on a video conferencing device|Mandantenschlüssel|Tenant key|Video-ID|Video ID|"
               r"Weitere\s+Informationen|More\s+info|Für Organisatoren|For organizers|"
               r"Besprechungsoptionen|Meeting\s+options|Zurücksetzen der Einwahl-PIN|"
               r"Reset dial-in PIN)\b.*$", re.I | re.M),
    re.compile(r"Confidentiality Notice:.*", re.I | re.S),
    re.compile(r"Vertraulichkeitshinweis:.*", re.I | re.S),
    re.compile(r"^\s*\d[\d\s]{8,}#?\s*$", re.M),          # nackte Konferenz-IDs
    re.compile(r"^\s*https?://\S+\s*$", re.M),            # nackte Links auf eigener Zeile
    re.compile(r"^\s*\+\d[\d\s,#().-]{6,}\s*$", re.M),    # nackte Einwahlnummern
]

# Strukturierte Akquise-Felder, wie sie aus der CRM-Notiz kommen
# ("Statusoffen", "Wahrscheinlichkeit10%", "WertCHF 0", ...).
AKQUISE_LABELS: list[tuple[str, str]] = [
    ("naechster_schritt", r"N(?:ä|ae)chster\s+Schritt"),
    ("hauptprodukt", r"Hauptprodukt"),
    ("wahrscheinlichkeit", r"Wahrscheinlichkeit"),
    ("forecast_chf", r"Gew\.?\s*Forecast"),
    ("follow_up", r"Follow[-\s]?up"),
    ("bedarf", r"Bedarf"),
    ("status", r"Status"),
    ("wert_chf", r"Wert"),
    ("notiz_extra", r"Notizen"),
    ("website", r"Website"),
]

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
TEL_RE = re.compile(r"\+\d[\d\s/().-]{7,}\d")
URL_RE = re.compile(r"https?://[^\s<>\"']+")
GELD_RE = re.compile(r"(?:CHF|EUR|USD)\s*([\d'’.,\s]+)", re.I)
PROZENT_RE = re.compile(r"(\d{1,3})\s*%")


def _norm(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def kerntext(text: str) -> str:
    """Nur der menschlich geschriebene Teil einer Einladung/Notiz.

    Schneidet den angehaengten Teams-Block samt Einwahlnummern, Passcodes und
    Rechtstexten ab — sonst landen Konferenz-Telefonnummern als Kontaktdaten
    in der Liste.
    """
    t = _norm(text).replace(" ", " ").replace("&nbsp;", " ")
    treffer = KERN_ENDE.search(t)
    return t[:treffer.start()].strip() if treffer else t.strip()


def saeubern(text: str) -> str:
    """Entfernt Teams-/Rechtstext-Rauschen und normalisiert Leerraum."""
    t = _norm(text).replace(" ", " ").replace("&nbsp;", " ")
    for muster in RAUSCH_MUSTER:
        t = muster.sub("", t)
    zeilen = [z.strip() for z in t.splitlines()]
    zeilen = [z for z in zeilen if z and z not in {"|", "-", "—"}]
    # Doppelte Folgezeilen zusammenfassen
    entdoppelt: list[str] = []
    for z in zeilen:
        if not entdoppelt or entdoppelt[-1] != z:
            entdoppelt.append(z)
    return " | ".join(entdoppelt).strip(" |")


def geld(text: str) -> float | None:
    """'CHF 825'000' -> 825000.0 ; nimmt den groessten Betrag im Text."""
    betraege: list[float] = []
    for treffer in GELD_RE.finditer(_norm(text)):
        roh = treffer.group(1)
        roh = re.split(r"[^\d'’.,]", roh.strip())[0] if roh.strip() else ""
        roh = roh.replace("'", "").replace("’", "").replace(" ", "")
        if roh.count(",") and roh.count("."):
            roh = roh.replace(".", "").replace(",", ".")
        elif roh.count(",") == 1 and len(roh.split(",")[-1]) <= 2:
            roh = roh.replace(",", ".")
        else:
            roh = roh.replace(",", "")
        try:
            betraege.append(float(roh))
        except ValueError:
            continue
    return max(betraege) if betraege else None


def prozent(text: str) -> float | None:
    treffer = PROZENT_RE.search(_norm(text))
    return int(treffer.group(1)) / 100 if treffer else None


def emails(text: str, ohne_eigene: bool = True) -> list[str]:
    gefunden: list[str] = []
    for adr in EMAIL_RE.findall(_norm(text)):
        adr = adr.rstrip(".,;)")
        domain = adr.split("@")[-1].lower()
        if ohne_eigene and domain in EIGENE_DOMAINS:
            continue
        if any(h in domain for h in ("vc.aggreko.com", "m.webex.com")):
            continue          # Videokonferenz-Mandantenschluessel, keine Personen
        if adr not in gefunden:
            gefunden.append(adr)
    return gefunden


def telefone(text: str) -> list[str]:
    gefunden: list[str] = []
    for nr in TEL_RE.findall(_norm(text)):
        nr = re.sub(r"[,#]+.*$", "", nr).strip()
        nr = re.sub(r"\s{2,}", " ", nr)
        if len(re.sub(r"\D", "", nr)) < 9:
            continue
        if nr not in gefunden:
            gefunden.append(nr)
    return gefunden


def website(text: str) -> str:
    for url in URL_RE.findall(_norm(text)):
        if any(host in url for host in TECHNISCHE_HOSTS):
            continue
        return url.rstrip(".,;)")
    # auch 'www.agroscope.ch' ohne Schema erkennen
    treffer = re.search(r"\bwww\.[\w.-]+\.\w{2,}", _norm(text))
    return treffer.group(0) if treffer else ""


def teams_link(text: str) -> str:
    for url in URL_RE.findall(_norm(text)):
        if "teams.microsoft.com/meet" in url or "meetup-join" in url:
            return url.rstrip(".,;)")
    return ""


def akquise_felder(text: str) -> dict[str, object]:
    """Zieht die CRM-Felder aus der Terminnotiz (Label und Wert sind verklebt)."""
    ergebnis: dict[str, object] = {}
    t = _norm(text).replace(" ", " ").replace("&nbsp;", " ")
    for zeile in re.split(r"[\n|]", t):
        zeile = zeile.strip()
        if not zeile:
            continue
        for feld, label in AKQUISE_LABELS:
            treffer = re.match(rf"^{label}\s*[:\-]?\s*(.*)$", zeile, re.I)
            if not treffer:
                continue
            wert = treffer.group(1).strip(" :-—")
            if not wert or wert == "—":
                break
            if feld == "wahrscheinlichkeit":
                ergebnis[feld] = prozent(wert)
            elif feld in ("wert_chf", "forecast_chf"):
                ergebnis[feld] = geld(wert)
            else:
                ergebnis[feld] = wert
            break
    # Zweiter Durchgang: handgetippte Notizen haben die Labels mitten im Satz
    # ("... Wert CHF 120'000, Wahrscheinlichkeit 40%"). Der Wert endet hier am
    # naechsten Trennzeichen, damit nicht der halbe Satz mitgenommen wird.
    for feld, label in AKQUISE_LABELS:
        if feld in ergebnis:
            continue
        treffer = re.search(rf"\b{label}\s*[:\-]?\s*([^,;|\n]{{2,80}})", t, re.I)
        if not treffer:
            continue
        wert = treffer.group(1).strip(" :-—.")
        if not wert:
            continue
        if feld == "wahrscheinlichkeit":
            ergebnis[feld] = prozent(wert)
        elif feld in ("wert_chf", "forecast_chf"):
            ergebnis[feld] = geld(wert)
        else:
            ergebnis[feld] = wert

    # "Potenzial rund CHF 825'000" steht frei im Aufhaenger-Text
    pot = re.search(r"Potenzial[^|]{0,20}?((?:CHF|EUR)\s*[\d'’.,\s]+)", t, re.I)
    if pot:
        ergebnis["potenzial_chf"] = geld(pot.group(1))
    return {k: v for k, v in ergebnis.items() if v not in (None, "")}


# ---------------------------------------------------------------------------
# Firma / Kategorie
# ---------------------------------------------------------------------------

# Praefixe, nach denen im Titel typischerweise die Gegenstelle folgt
# ("Telefon Akquise — Green Datacenter AG").
KONTAKT_PRAEFIXE = re.compile(
    r"^(Telefon(ische[rn]?)?(\s+(Akquise|Beratung|Termin))?|Telefonat|Call|Anruf|"
    r"Video(call)?)\b[\s—–\-:·|]*", re.I)

# Praefixe, nach denen meist ein Thema folgt, keine Firma
# ("Besprechung Stromversorgung Sanierung Wasserbecken").
THEMEN_PRAEFIXE = re.compile(
    r"^(Termin|Besprechung|Meeting|Workshop|Begehung|Teams)\b[\s—–\-:·|]*", re.I)

RECHTSFORMEN = r"(AG|GmbH|SA|S[àa]rl|SARL|Ltd|Inc|KG|OHG|e\.V\.|Group|Holding|SE)"

PERSONENNAME = re.compile(
    r"^[A-ZÄÖÜ][a-zäöüß]+(?:[-\s][A-ZÄÖÜ][a-zäöüß]+){1,2}$")


def personenname(text: str) -> str:
    """Gibt den Text zurueck, wenn er wie ein Personenname aussieht — sonst ''."""
    kandidat = _norm(text).strip(" ,;:")
    return kandidat if PERSONENNAME.fullmatch(kandidat) else ""


# Woerter, die vor einem Firmennamen stehen koennen, aber nicht dazugehoeren
# ("Offerte Green Datacenter AG versendet").
VORWORTE = {
    "offerte", "angebot", "anfrage", "auftrag", "bestellung", "rechnung",
    "termin", "besuch", "meeting", "besprechung", "mail", "e-mail", "telefon",
    "telefonat", "anruf", "call", "kontakt", "notiz", "screenshot", "info",
    "akquise", "beratung", "nachfassen", "follow-up", "protokoll", "projekt",
}


def firma_aus_titel(titel: str) -> str:
    t = _norm(titel).strip()

    # 1. Eine Rechtsform im Titel ist das staerkste Signal.
    treffer = re.search(rf"\b([A-ZÄÖÜ][\w&.\-]*(?:\s[A-ZÄÖÜ][\w&.\-]*)*\s{RECHTSFORMEN})\b", t)
    if treffer:
        worte = KONTAKT_PRAEFIXE.sub("", treffer.group(1)).strip(" —–-:·|").split()
        while len(worte) > 1 and worte[0].lower().strip(":,") in VORWORTE:
            worte.pop(0)
        return " ".join(worte)

    # 2. Nach "Telefon/Call/Anruf" folgt in der Regel die Gegenstelle.
    rest = KONTAKT_PRAEFIXE.sub("", t).strip(" —–-:·|")
    if rest and rest.lower() != t.lower() and len(rest.split()) <= 3:
        return rest

    # 3. Nach "Besprechung/Termin/Meeting" folgt ein Thema -> keine Firma raten.
    return ""


def firma_aus_domain(adresse: str) -> str:
    if "@" not in adresse:
        return ""
    domain = adresse.split("@")[-1].lower()
    if domain in EIGENE_DOMAINS or any(h in domain for h in TECHNISCHE_HOSTS):
        return ""
    kern = domain.split(".")[0]
    return FIRMEN_ALIASE.get(kern, kern.capitalize())


def ist_partner(adressen: list[str]) -> bool:
    domains = {a.split("@")[-1].lower() for a in adressen if "@" in a}
    return bool(domains) and domains <= PARTNER_DOMAINS


def kategorie_bestimmen(titel: str, notizen: str, typ: str, ort: str = "") -> str:
    titel_klein = _norm(titel).lower()
    gesamt = f"{titel} {notizen} {ort}".lower()

    for muster, kategorie in KATEGORIE_REGELN:
        if re.search(muster, gesamt, re.I):
            return kategorie

    if typ.startswith("E-Mail"):
        return "E-Mail"
    if re.search(r"\b(akquise|kaltakquise|erstkontakt|cold call)\b", gesamt) \
            or re.search(r"\b(offerte|angebot|ausschreibung)\b", titel_klein):
        return "Akquise"
    if re.search(r"\b(messe|fair|kongress|expo)\b", gesamt) or "maintenance schweiz" in gesamt:
        return "Messe / Event"
    # Interne Arbeit nur aus dem Titel ableiten — sonst schlagen Signaturen
    # und Mail-Domains (z. B. "…@agroscope.admin.ch") faelschlich an.
    if re.search(r"\b(home ?office|nachfassen|nachbearbeitung|liste|admin(istration)?|"
                 r"reporting|ablage|planung)\b", titel_klein):
        return "Interne Arbeit"
    if "beratung" in titel_klein:
        return "Beratung"
    if re.search(r"\b(besprechung|meeting|termin|begehung|workshop|abnahme)\b", titel_klein):
        return "Kundentermin"
    if re.search(r"\b(telefon|call|anruf)\b", titel_klein):
        return "Beratung"
    return "Sonstiges"
