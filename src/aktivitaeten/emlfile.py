"""Parser fuer E-Mail-Dateien (.eml / .msg-Export als Text)."""

from __future__ import annotations

import re
from email import message_from_string, policy
from email.utils import getaddresses, parsedate_to_datetime
from zoneinfo import ZoneInfo

from . import felder
from .model import ZEITZONE, Aktivitaet

LOKAL = ZoneInfo(ZEITZONE)

ABWESENHEIT = re.compile(
    r"(automatische antwort|automatic reply|réponse automatique|out of office|"
    r"abwesenheitsnotiz|annual leave|ferienabwesenheit)", re.I)


def _text_extrahieren(nachricht) -> str:
    if nachricht.is_multipart():
        for teil in nachricht.walk():
            if teil.get_content_type() == "text/plain":
                try:
                    return teil.get_content()
                except Exception:
                    nutzlast = teil.get_payload(decode=True) or b""
                    return nutzlast.decode(teil.get_content_charset() or "utf-8", "replace")
        for teil in nachricht.walk():
            if teil.get_content_type() == "text/html":
                nutzlast = teil.get_payload(decode=True) or b""
                html = nutzlast.decode(teil.get_content_charset() or "utf-8", "replace")
                return re.sub(r"<[^>]+>", " ", html)
        return ""
    try:
        return nachricht.get_content()
    except Exception:
        nutzlast = nachricht.get_payload(decode=True) or b""
        return nutzlast.decode(nachricht.get_content_charset() or "utf-8", "replace")


def parsen(pfad: str, roh_text: str, quelle: str, quelle_hash: str) -> list[Aktivitaet]:
    nachricht = message_from_string(roh_text, policy=policy.default)

    betreff_roh = str(nachricht.get("Subject", "")).strip()
    betreff = betreff_roh
    praefix = re.compile(
        r"^\s*(\[EXTERNAL\]|\[EXTERN\]|AW|RE|WG|FW|FWD|Antw|Automatische Antwort|"
        r"Automatic reply|R[ée]ponse automatique)\s*[:\s]\s*", re.I)
    for _ in range(6):                       # Ketten wie "AW: RE: [EXTERNAL] ..."
        gekuerzt = praefix.sub("", betreff, count=1).strip()
        if gekuerzt == betreff:
            break
        betreff = gekuerzt

    absender = getaddresses([str(nachricht.get("From", ""))])
    empfaenger = getaddresses([str(nachricht.get("To", ""))])
    von_name, von_mail = (absender[0] if absender else ("", ""))

    zeitpunkt = None
    if nachricht.get("Date"):
        try:
            zeitpunkt = parsedate_to_datetime(str(nachricht["Date"])).astimezone(LOKAL)
        except Exception:
            zeitpunkt = None

    koerper = felder.saeubern(felder.kerntext(_text_extrahieren(nachricht)))
    auto = str(nachricht.get("Auto-Submitted", "")).lower().startswith("auto") \
        or ABWESENHEIT.search(betreff_roh + " " + koerper) is not None

    eigen = von_mail.split("@")[-1].lower() in felder.EIGENE_DOMAINS
    richtung = "ausgehend" if eigen else "eingehend"

    a = Aktivitaet(
        id=str(nachricht.get("Message-ID", "")).strip("<> ") or f"{quelle_hash[:24]}",
        quelle=quelle,
        quelle_hash=quelle_hash,
        typ="E-Mail (Auto-Antwort)" if auto else "E-Mail",
        kategorie="E-Mail",
        titel=betreff or "(ohne Betreff)",
        organisator=von_name or von_mail,
        kontakt=von_name or von_mail,
        email=von_mail,
        teilnehmer=", ".join(n or m for n, m in empfaenger),
        notizen=f"{richtung.capitalize()} · {koerper}"[:2000],
    )

    if zeitpunkt:
        a.datum = zeitpunkt.date()
        a.von = zeitpunkt.time().replace(second=0, microsecond=0)
        a.erfasst_am = zeitpunkt.replace(tzinfo=None)

    a.firma = felder.firma_aus_domain(von_mail) or felder.firma_aus_titel(betreff)
    nummern = felder.telefone(koerper)
    a.telefon = nummern[0] if nummern else ""
    a.website = felder.website(koerper)

    if auto:
        rueckkehr = re.search(
            r"(back on|zurück am|wieder (?:da|erreichbar) am)\s+([^.,;|]{3,40})", koerper, re.I)
        if rueckkehr:
            a.follow_up = rueckkehr.group(2).strip()
            a.naechster_schritt = f"Erneut kontaktieren nach {a.follow_up}"
        a.status = "Abwesend / keine Antwort"
    else:
        a.status = "Bestätigt"

    return [a]
