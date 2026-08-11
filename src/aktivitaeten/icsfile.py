"""Parser fuer iCalendar-Dateien (.ics) — Outlook / Teams / Messe-Exporte."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from . import felder
from .model import ZEITZONE, Aktivitaet

LOKAL = ZoneInfo(ZEITZONE)


# ---------------------------------------------------------------------------
# Low-Level: Zeilen entfalten und in (Name, Parameter, Wert) zerlegen
# ---------------------------------------------------------------------------

def _entfalten(text: str) -> list[str]:
    """RFC 5545: Fortsetzungszeilen beginnen mit Leerzeichen oder Tab."""
    zeilen: list[str] = []
    for roh in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if roh[:1] in (" ", "\t") and zeilen:
            zeilen[-1] += roh[1:]
        else:
            zeilen.append(roh)
    return zeilen


def _wert_entkoden(wert: str) -> str:
    ergebnis = []
    i = 0
    while i < len(wert):
        z = wert[i]
        if z == "\\" and i + 1 < len(wert):
            folge = wert[i + 1]
            ergebnis.append({"n": "\n", "N": "\n", ",": ",", ";": ";", "\\": "\\"}.get(folge, folge))
            i += 2
        else:
            ergebnis.append(z)
            i += 1
    return "".join(ergebnis)


def _zerlegen(zeile: str) -> tuple[str, dict[str, str], str] | None:
    trenner = zeile.find(":")
    if trenner < 0:
        return None
    kopf, wert = zeile[:trenner], zeile[trenner + 1:]
    teile = kopf.split(";")
    name = teile[0].upper()
    params: dict[str, str] = {}
    for p in teile[1:]:
        if "=" in p:
            schluessel, inhalt = p.split("=", 1)
            params[schluessel.upper()] = inhalt.strip('"')
    return name, params, _wert_entkoden(wert)


def _zeitpunkt(wert: str, params: dict[str, str]) -> tuple[datetime | None, bool]:
    """Gibt (lokale Zeit, ganztags?) zurueck."""
    wert = wert.strip()
    if re.fullmatch(r"\d{8}", wert) or params.get("VALUE") == "DATE":
        return datetime.strptime(wert[:8], "%Y%m%d"), True
    treffer = re.fullmatch(r"(\d{8})T(\d{6})(Z?)", wert)
    if not treffer:
        return None, False
    roh = datetime.strptime(treffer.group(1) + treffer.group(2), "%Y%m%d%H%M%S")
    if treffer.group(3) == "Z":
        return roh.replace(tzinfo=timezone.utc).astimezone(LOKAL).replace(tzinfo=None), False
    if params.get("TZID"):
        try:
            quelle = ZoneInfo(params["TZID"])
            return roh.replace(tzinfo=quelle).astimezone(LOKAL).replace(tzinfo=None), False
        except Exception:
            pass
    return roh, False


def _person(params: dict[str, str], wert: str) -> tuple[str, str]:
    """(Name, E-Mail) aus ORGANIZER/ATTENDEE."""
    adresse = re.sub(r"^mailto:", "", wert, flags=re.I).strip()
    return params.get("CN", "").strip(), adresse


# ---------------------------------------------------------------------------
# Hauptfunktion
# ---------------------------------------------------------------------------

def parsen(pfad: str, roh_text: str, quelle: str, quelle_hash: str) -> list[Aktivitaet]:
    ereignisse: list[Aktivitaet] = []
    aktuell: dict | None = None

    for zeile in _entfalten(roh_text):
        zerlegt = _zerlegen(zeile)
        if not zerlegt:
            continue
        name, params, wert = zerlegt

        if name == "BEGIN" and wert.upper() == "VEVENT":
            aktuell = {"attendees": [], "kalender": {}}
            continue
        if name == "END" and wert.upper() == "VEVENT":
            if aktuell is not None:
                ereignisse.append(_bauen(aktuell, quelle, quelle_hash))
            aktuell = None
            continue
        if aktuell is None:
            continue

        if name == "ATTENDEE":
            aktuell["attendees"].append(_person(params, wert))
        elif name == "ORGANIZER":
            aktuell["organizer"] = _person(params, wert)
        elif name in ("DTSTART", "DTEND", "DTSTAMP"):
            aktuell[name] = _zeitpunkt(wert, params)
        elif name in ("UID", "SUMMARY", "LOCATION", "DESCRIPTION", "STATUS", "CATEGORIES"):
            aktuell[name] = wert
        elif name == "X-ALT-DESC" and "DESCRIPTION" not in aktuell:
            aktuell["DESCRIPTION"] = re.sub(r"<[^>]+>", " ", wert)

    return ereignisse


def _bauen(roh: dict, quelle: str, quelle_hash: str) -> Aktivitaet:
    start, start_ganztags = roh.get("DTSTART", (None, False))
    ende, _ = roh.get("DTEND", (None, False))
    stempel, _ = roh.get("DTSTAMP", (None, False))

    titel = (roh.get("SUMMARY") or "(ohne Titel)").strip()
    beschreibung_roh = roh.get("DESCRIPTION", "")
    ort = felder.saeubern(roh.get("LOCATION", ""))
    if ort.lower() in ("microsoft teams meeting", "microsoft teams-besprechung"):
        ort = "Microsoft Teams (online)"

    a = Aktivitaet(
        id=(roh.get("UID") or f"{quelle_hash[:16]}-{titel[:20]}").strip(),
        quelle=quelle,
        quelle_hash=quelle_hash,
        typ="Termin (Kalender)",
        titel=titel,
        ort=ort,
        ganztags=start_ganztags,
        erfasst_am=stempel,
    )

    if start:
        a.datum = start.date()
        if not start_ganztags:
            a.von = start.time().replace(second=0, microsecond=0)
    if ende:
        if start_ganztags:
            # DTEND ist bei Ganztagsterminen exklusiv
            a.enddatum = (ende - timedelta(days=1)).date()
        else:
            a.bis = ende.time().replace(second=0, microsecond=0)
            a.enddatum = ende.date()
    if start and ende and not start_ganztags:
        a.dauer_h = round((ende - start).total_seconds() / 3600, 2)
    elif start_ganztags and start and ende:
        tage = max((ende.date() - start.date()).days, 1)
        a.dauer_h = None
        if tage > 1:
            a.notizen = f"Ganztägig, {tage} Tage"

    # Personen
    organisator_name, organisator_mail = roh.get("organizer", ("", ""))
    a.organisator = organisator_name or organisator_mail
    externe = [(n, m) for n, m in roh["attendees"]
               if m.split("@")[-1].lower() not in felder.EIGENE_DOMAINS]
    a.teilnehmer = ", ".join(n or m for n, m in roh["attendees"]
                             if m.split("@")[-1].lower() not in felder.EIGENE_DOMAINS)

    # Der Teams-Block am Ende der Einladung wird fuer Notizen und Kontaktdaten
    # abgeschnitten — sonst landen Einwahlnummern und Passcodes in der Liste.
    kern = felder.kerntext(beschreibung_roh)
    notiz = felder.saeubern(kern)

    # Akquise-/CRM-Felder
    for schluessel, wert in felder.akquise_felder(kern).items():
        if schluessel == "notiz_extra":
            notiz = f"{notiz} | {wert}" if notiz else str(wert)
        elif hasattr(a, schluessel):
            setattr(a, schluessel, wert)

    if a.notizen:
        notiz = f"{a.notizen} | {notiz}" if notiz else a.notizen
    a.notizen = notiz[:2000]

    # Kontaktdaten — bewusst nur aus dem menschlichen Teil
    adressen = felder.emails(f"{titel}\n{kern}")
    a.email = adressen[0] if adressen else (externe[0][1] if externe else "")
    nummern = felder.telefone(kern)
    a.telefon = nummern[0] if nummern else ""
    a.website = a.website or felder.website(kern)
    a.meeting_link = felder.teams_link(beschreibung_roh) or felder.teams_link(roh.get("LOCATION", ""))

    # Firma: gepflegter Alias schlaegt den aus dem Titel geratenen Namen
    aus_titel = felder.firma_aus_titel(titel)
    aus_domain = felder.firma_aus_domain(a.email or (externe[0][1] if externe else ""))
    gepflegt = aus_domain and aus_domain in felder.FIRMEN_ALIASE.values()
    a.firma = aus_domain if gepflegt else (aus_titel or aus_domain)

    eigener_termin = not externe and (organisator_mail.split("@")[-1].lower()
                                      in felder.EIGENE_DOMAINS or not organisator_mail)
    if externe:
        a.kontakt = externe[0][0] or externe[0][1]
    elif not eigener_termin:
        a.kontakt = organisator_name
    else:
        # Bei selbst gesetzten Terminen steht der Ansprechpartner oft als erste
        # Zeile der Notiz (kopierte Signatur / Visitenkarte).
        erste = next((z for z in kern.splitlines() if z.strip()), "")
        a.kontakt = felder.personenname(erste)

    a.kategorie = felder.kategorie_bestimmen(titel, notiz, a.typ, ort)
    if a.kategorie == "Sonstiges":
        a.kategorie = "Kundentermin" if externe else "Interne Arbeit"
    if externe and felder.ist_partner([m for _, m in externe]) \
            and a.kategorie in ("Kundentermin", "Beratung", "Sonstiges"):
        a.kategorie = "Partner / Lieferant"

    if not a.status:
        a.status = (roh.get("STATUS") or "").capitalize().replace("Confirmed", "Bestätigt")

    if a.wert_chf is not None and a.wahrscheinlichkeit is not None and a.forecast_chf is None:
        a.forecast_chf = round(a.wert_chf * a.wahrscheinlichkeit, 2)

    return a
