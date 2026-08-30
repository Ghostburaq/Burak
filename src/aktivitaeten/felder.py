"""Heuristiken zum Herausziehen von Inhalten aus Freitext.

Alles hier arbeitet rein textbasiert und faellt still auf leere Werte zurueck,
wenn nichts erkannt wird — die Pipeline soll nie an einem Sonderfall haengen.
"""

from __future__ import annotations

import html
import re
import unicodedata

from .konfig import (EIGENE_ADRESSE, EIGENE_DOMAINS, FIRMEN_ALIASE,
                     FIRMEN_STICHWORTE, KATEGORIE_REGELN, PARTNER_DOMAINS,
                     PARTNER_FIRMEN, TECHNISCHE_HOSTS)

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
    ("follow_up", r"Wiedervorlage"),
    ("status", r"Ergebnis"),
]

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# international (+41 …) oder schweizerisch-national (055 254 92 34 / 0552549234)
TEL_RE = re.compile(r"\+\d[\d\s/().-]{7,}\d|\b0\d{1,2}[\s/.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}\b")
URL_RE = re.compile(r"https?://[^\s<>\"']+")
GELD_RE = re.compile(r"(?:CHF|EUR|USD)\s*([\d'’.,\s]+)", re.I)
PROZENT_RE = re.compile(r"(\d{1,3})\s*%")


# Füllzeichen, die Outlook-Tabellen und Formulare mitschleppen
FUELLZEICHEN = str.maketrans({"ㅤ": " ", "​": " ", "﻿": " ",
                              " ": " ", "・": " ", "•": " "})


def _norm(text: str) -> str:
    """Vereinheitlicht Sonderzeichen und loest HTML-Entities auf (&lt; &amp; …)."""
    entschaerft = html.unescape(text or "")
    return unicodedata.normalize("NFC", entschaerft.translate(FUELLZEICHEN))


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
            treffer = re.match(rf"^(?:{label})\s*[:\-]?\s*(.*)$", zeile, re.I)
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
        treffer = re.search(rf"\b(?:{label})\s*[:\-]?\s*([^,;|·\n]{{2,80}})", t, re.I)
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
# Formulare und Kontaktkarten aus Outlook-Terminen
# ---------------------------------------------------------------------------

# Beschriftungen, wie sie in Lead-Formularen und Akquise-Karten vorkommen.
# Der Wert steht entweder direkt dahinter ("OrtZug 6301") oder in der
# nächsten Zeile ("Firma" \n "Gemeinde Hombrechtikon").
FORMULAR_LABELS: list[tuple[str, str]] = [
    ("kontakt", r"Vor-\s*und\s*Nachname|Ansprechpartner(?:in\b)?|Kontaktperson|Name"),
    ("firma", r"Firma|Unternehmen|Kundenname"),
    ("email", r"E-?Mail(?:adresse)?"),
    ("telefon", r"Telefon(?:nummer)?|Tel\.|Mobiltelefon|Handy|Natel"),
    ("ort", r"Objektadresse|Adresse|Standort|Ort"),
    ("funktion", r"Funktion|Position|Rolle"),
    ("hauptprodukt", r"Produkt"),
    ("segment", r"Segment|Branche"),
    ("prioritaet", r"Priorit(?:ä|ae)t"),
    ("kanton", r"Kanton"),
]

# Werte, die nichts aussagen
LEERWERTE = {"—", "-", "–", "✕", "x", "n/a", "keine", "offen?"}


def formularfelder(text: str) -> dict[str, str]:
    """Liest Label/Wert-Paare — verklebt oder über zwei Zeilen verteilt."""
    zeilen = [z.strip(" :\t") for z in re.split(r"[\n|]", _norm(text))]
    zeilen = [z for z in zeilen if z]
    ergebnis: dict[str, str] = {}

    for index, zeile in enumerate(zeilen):
        for feld, label in FORMULAR_LABELS:
            if feld in ergebnis:
                continue
            treffer = re.match(rf"^(?:{label})\s*[:\-]?\s*(.*)$", zeile, re.I)
            if not treffer:
                continue
            wert = treffer.group(1).strip(" :-—·")
            if not wert and index + 1 < len(zeilen):
                # Wert steht in der nächsten Zeile — aber nur, wenn diese
                # nicht selbst wieder eine Beschriftung ist
                naechste = zeilen[index + 1]
                if not any(re.match(rf"^(?:{lb})\b", naechste, re.I)
                           for _, lb in FORMULAR_LABELS):
                    wert = naechste.strip(" :-—·")
            if wert and wert.lower() not in LEERWERTE and _wert_passt(feld, wert):
                ergebnis[feld] = wert
            break
    return ergebnis


def _wert_passt(feld: str, wert: str) -> bool:
    """Sicherheitsnetz gegen falsch zugeordnete Beschriftungen."""
    if feld == "telefon":
        return len(re.sub(r"\D", "", wert)) >= 9
    if feld == "email":
        return bool(EMAIL_RE.fullmatch(wert.strip()))
    if feld in ("firma", "kontakt", "funktion"):
        # ein ganzer Satz ist kein Firmen- oder Personenname, eine Nummer auch nicht
        if not any(z.isalpha() for z in wert) or TEL_RE.fullmatch(wert.strip()):
            return False
        return len(wert.split()) <= 5 and not wert.endswith((".", "!", "?"))
    return True


KONTAKT_ZEILE = re.compile(r"^\s*Kontakt\s*:\s*(.+)$", re.I | re.M)
KUNDE_ZEILE = re.compile(r"^\s*(?:Kunde|Firma)\s*:\s*(.+)$", re.I | re.M)
ADRESS_HINWEIS = re.compile(r"\d{4}\s|strasse|str\.|weg |gasse|platz|route|rue ", re.I)


def kontaktzeile(text: str) -> dict[str, str]:
    """Zerlegt eine Zeile 'Kontakt: Name, Funktion, Firma'."""
    treffer = KONTAKT_ZEILE.search(_norm(text))
    if not treffer:
        return {}
    teile = [t.strip(" /|") for t in treffer.group(1).split(",") if t.strip(" /|")]
    if not teile:
        return {}

    ergebnis: dict[str, str] = {}
    name = personenname(teile[0]) or (teile[0] if len(teile[0].split()) <= 4 else "")
    if name:
        ergebnis["kontakt"] = name
    if len(teile) > 1:
        ergebnis["funktion"] = teile[1]
    # Firma: erster weiterer Teil, der weder Adresse noch Kontaktdatum ist
    for teil in teile[2:]:
        if ADRESS_HINWEIS.search(teil) or "@" in teil or TEL_RE.search(teil):
            continue
        kandidat = re.sub(r"\s*\(.*?\)\s*", " ", teil).strip(" /|")
        if any(z.isalpha() for z in kandidat):
            ergebnis["firma"] = kandidat
            break

    # "Kunde: EWO Gebäudetechnik AG, Stanserstrasse 8, 6064 Kerns" — der
    # erste Abschnitt ist der Firmenname, der Rest die Adresse
    kunde = KUNDE_ZEILE.search(_norm(text))
    if kunde:
        erster = kunde.group(1).split(",")[0].strip(" /|[]")
        if erster and any(z.isalpha() for z in erster) and not erster.startswith("["):
            ergebnis["firma"] = erster
    return ergebnis


def kontaktkarte(text: str) -> dict[str, str]:
    """Erkennt die Visitenkarten-Form ohne Beschriftungen.

    Funktion / Vorname / Nachname / Telefon / E-Mail stehen jeweils auf einer
    eigenen Zeile, wie es Outlook beim Einfügen aus einem CRM erzeugt:

        Engineering Director
        Carine
        Havet
        +41 228845000
        chavet@stackinfra.com
    """
    zeilen = [z.strip() for z in re.split(r"[\n|]", _norm(text))]
    zeilen = [z for z in zeilen if z]
    blank = lambda z: z.strip().strip("<>()[] ")
    tel_index = next((i for i, z in enumerate(zeilen) if TEL_RE.fullmatch(blank(z))), None)
    mail_index = next((i for i, z in enumerate(zeilen) if EMAIL_RE.fullmatch(blank(z))), None)
    if tel_index is None and mail_index is None:
        return {}

    anker = tel_index if tel_index is not None else mail_index
    ergebnis: dict[str, str] = {}
    if tel_index is not None:
        ergebnis["telefon"] = blank(zeilen[tel_index])
    if mail_index is not None:
        ergebnis["email"] = blank(zeilen[mail_index])

    # Ein bis zwei Namensteile direkt oberhalb der Telefonnummer
    namensteile: list[str] = []
    for zeile in reversed(zeilen[max(anker - 2, 0):anker]):
        if re.fullmatch(r"[A-ZÄÖÜ][\wäöüéèàç'’-]{1,20}", zeile):
            namensteile.insert(0, zeile)
        else:
            break
    if namensteile:
        ergebnis["kontakt"] = " ".join(namensteile)
        davor = anker - len(namensteile) - 1
        if davor >= 0 and len(zeilen[davor].split()) <= 5 and not EMAIL_RE.search(zeilen[davor]):
            ergebnis["funktion"] = zeilen[davor].strip()
    return ergebnis


# Rollen- und Funktionsbezeichnungen — hilfreich, um sie von Firmennamen
# zu unterscheiden.
ROLLENWOERTER = {
    "project", "manager", "director", "architect", "architecte", "architectes",
    "engineer", "engineering", "contractor", "council", "consultant", "owner",
    "developer", "associate", "industrial", "development", "general", "senior",
    "technical", "sales", "chief", "head", "of", "the", "real", "estate",
    "projektleiter", "bauleiter", "inhaber", "leiter", "geschaeftsfuehrer",
}

PLZ_RE = re.compile(r"^\d{4}$")

LAENDER = {"switzerland", "schweiz", "suisse", "svizzera", "deutschland",
           "germany", "france", "frankreich", "austria", "österreich",
           "italy", "italien", "liechtenstein"}


def crm_block(text: str) -> dict[str, str]:
    """Liest CRM-Exporte, deren Felder nur durch Leerraum getrennt sind.

    Outlook-Termine aus dem Projektsystem sehen so aus — alles in einer
    Zeile, die Felder durch mehrere Leerzeichen abgeteilt:

        300629372   SIERRE GRASSROOT DATA CENTER  Associate Director
        Michael     Melly +41 274562912   Contractor  Melly Constructions SA
        Route de Chippis 99A    3966  Sierre   Valais   Switzerland
    """
    roh = _norm(text).replace("\n", "  ")
    teile = [t.strip() for t in re.split(r"\s{2,}", roh) if t.strip()]
    if len(teile) < 6:
        return {}

    # Strenge Erkennung: ein CRM-Export beginnt mit einer Projektnummer und
    # enthaelt Postleitzahl und Land. Ohne diese Merkmale ist es Fliesstext,
    # und ein Ratespiel auf Fliesstext zerstoert sonst gute Werte.
    hat_projektnummer = teile[0].isdigit() and len(teile[0]) >= 6
    hat_plz = any(PLZ_RE.match(x) for x in teile)
    hat_land = any(x.lower() in LAENDER for x in teile)
    if not (hat_plz and (hat_projektnummer or hat_land)):
        return {}

    ergebnis: dict[str, str] = {}
    tel_index = None
    for index, teil in enumerate(teile):
        treffer = TEL_RE.search(teil)
        if treffer and len(re.sub(r"\D", "", treffer.group())) >= 9:
            ergebnis["telefon"] = treffer.group().strip()
            tel_index = index
            break
    adressen = emails(roh)
    if adressen:
        ergebnis["email"] = adressen[0]
    if not ergebnis:
        return {}

    # Projektbezeichnung: langer Grossbuchstaben-Block am Anfang
    for teil in teile[:3]:
        if len(teil) > 8 and teil == teil.upper() and not teil.isdigit():
            ergebnis["projekt"] = teil
            break

    # Firma: erster mehrwortiger Eintrag nach der Telefonnummer, der nicht
    # nur aus Rollenbezeichnungen besteht
    for teil in teile[(tel_index or 0) + 1:]:
        worte = teil.split()
        if len(worte) < 2 or any(z.isdigit() for z in teil):
            continue
        if "@" in teil or teil.lower().startswith("www"):
            continue
        if all(w.lower().strip(",.") in ROLLENWOERTER for w in worte):
            continue
        # Vorangestellte Rollenbezeichnung abtrennen ("Engineering Structurame Sarl")
        while len(worte) > 2 and worte[0].lower().strip(",.") in ROLLENWOERTER:
            worte.pop(0)
        ergebnis["firma"] = " ".join(worte)
        break

    # Ort steht hinter der Postleitzahl
    for index, teil in enumerate(teile[:-1]):
        if PLZ_RE.match(teil):
            ergebnis["ort"] = f"{teil} {teile[index + 1]}".strip()
            break

    return ergebnis


def name_aus_mail(adresse: str) -> str:
    """'Simon.Meier@ekz.ch' -> 'Simon Meier' (nur bei klarem Vorname.Nachname)."""
    lokal = _norm(adresse).split("@")[0]
    if "." not in lokal:
        return ""
    teile = [t for t in lokal.split(".") if t]
    if not 2 <= len(teile) <= 3 or any(len(t) < 2 or any(c.isdigit() for c in t) for t in teile):
        return ""
    return " ".join(t.capitalize() for t in teile)


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


# Rollenbezeichnungen, die in Notizen hinter dem Namen stehen
ROLLE_ANHANG = re.compile(
    r"\s*(Ansprechpartner(?:in)?|Kontaktperson|Kontakt|AP|Bauleiter|Projektleiter)\s*$", re.I)


def personenname(text: str) -> str:
    """Gibt den Text zurueck, wenn er wie ein Personenname aussieht — sonst ''."""
    kandidat = ROLLE_ANHANG.sub("", _norm(text).strip(" ,;:")).strip()
    return kandidat if PERSONENNAME.fullmatch(kandidat) else ""


# Woerter, die vor einem Firmennamen stehen koennen, aber nicht dazugehoeren
# ("Offerte Green Datacenter AG versendet").
VORWORTE = {
    "offerte", "angebot", "anfrage", "auftrag", "bestellung", "rechnung",
    "termin", "besuch", "meeting", "besprechung", "mail", "e-mail", "telefon",
    "telefonat", "anruf", "call", "kontakt", "notiz", "screenshot", "info",
    "akquise", "beratung", "nachfassen", "follow-up", "protokoll", "projekt",
    "ort", "besuch", "vor",
}


def firma_aus_stichwort(titel: str) -> str:
    """Gepflegter Firmenname, wenn ein Stichwort im Titel vorkommt."""
    klein = _norm(titel).lower()
    for stichwort, name in sorted(FIRMEN_STICHWORTE.items(), key=lambda kv: -len(kv[0])):
        if stichwort in klein:
            return name
    return ""


# Begriffe, die nach dem Praefix stehen koennen, aber keine Gegenstelle sind
GENERISCH = {"data center", "datacenter", "rechenzentrum", "kunden", "kunde",
             "diverse", "allgemein", "verschiedene", "offen", "intern"}


def firma_aus_titel(titel: str) -> str:
    t = _norm(titel).strip()

    # 0. Gepflegtes Stichwort im Titel schlaegt jede Heuristik.
    gepflegt = firma_aus_stichwort(t)
    if gepflegt:
        return gepflegt

    # 1. Eine Rechtsform im Titel ist das staerkste Signal.
    treffer = re.search(rf"\b([A-ZÄÖÜ][\w&.\-]*(?:\s[A-ZÄÖÜ][\w&.\-]*)*\s{RECHTSFORMEN})\b", t)
    if treffer:
        worte = KONTAKT_PRAEFIXE.sub("", treffer.group(1)).strip(" —–-:·|").split()
        while len(worte) > 1 and worte[0].lower().strip(":,") in VORWORTE:
            worte.pop(0)
        return " ".join(worte)

    # 2. Nach "Telefon/Call/Anruf" folgt in der Regel die Gegenstelle.
    rest = KONTAKT_PRAEFIXE.sub("", t).strip(" —–-:·|")
    rest = re.sub(r"^\((.*)\)$", r"\1", rest).strip()
    if (rest and rest.lower() != t.lower() and len(rest.split()) <= 3
            and rest.lower() not in GENERISCH and any(z.isalpha() for z in rest)):
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

    # Eigene Regeln greifen bewusst nur auf den Titel — sonst zieht ein
    # beilaeufig erwaehnter Projektname in der Notiz die Kategorie um.
    for muster, kategorie in KATEGORIE_REGELN:
        if re.search(muster, titel_klein, re.I):
            return kategorie

    if re.search(r"\b(werkstatt|garage|arzt|zahnarzt|ferien|urlaub|privat|"
                 r"geburtstag|umzug)\b", titel_klein):
        return "Privat"
    if typ.startswith("E-Mail"):
        return "E-Mail"
    if re.search(r"\b(akquise|kaltakquise|erstkontakt|cold call)\b", gesamt) \
            or re.search(r"\b(offerten?|richtofferten?|angebote?|ausschreibung|"
                         r"ausarbeitung|auslegung|kontaktiert|erstkontakt)\b",
                         titel_klein):
        return "Akquise"
    if re.search(r"\b(messe|fair|kongress|expo)\b", gesamt) or "maintenance schweiz" in gesamt:
        return "Messe / Event"
    # Interne Arbeit nur aus dem Titel ableiten — sonst schlagen Signaturen
    # und Mail-Domains (z. B. "…@agroscope.admin.ch") faelschlich an.
    if re.search(r"\b(home ?office|nachfassen|nachbearbeitung|liste|admin(istration)?|"
                 r"reporting|ablage|planung)\b", titel_klein):
        return "Interne Arbeit"
    if re.search(r"(teamsitzung|sitzung|jour fixe|weekly|daily|standup)\b", titel_klein):
        return "Interner Termin"
    # Abwicklung eines laufenden Auftrags — weder Akquise noch reine Büroarbeit
    if re.search(r"(projekt|abwicklung|koordination|disposition|transport|"
                 r"anlieferung|aufbau|abbau|montage|messung|\bibn\b|"
                 r"inbetriebnahme)\b", titel_klein):
        return "Projekt"
    if "beratung" in titel_klein:
        return "Beratung"
    # ohne fuehrende Wortgrenze, damit auch Zusammensetzungen greifen
    # ("Baustellenbegehung", "Kundentermin", "Projektbesprechung")
    if re.search(r"(besprechung|meeting|termin|begehung|workshop|abnahme|inbetriebnahme)\b",
                 titel_klein):
        return "Kundentermin"
    if re.search(r"\b(telefon|call|anruf)\b", titel_klein):
        return "Beratung"
    return "Sonstiges"
