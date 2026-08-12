"""Erzeugt Fliesstext aus den Aktivitäten — für das Dashboard und den Report.

Aus den strukturierten Einträgen wird lesbare Prosa: was an einem Tag lief,
worauf der Schwerpunkt lag, was offen blieb.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import date

from .model import Aktivitaet


def chf(betrag: float | None) -> str:
    if not betrag:
        return ""
    return "CHF " + f"{betrag:,.0f}".replace(",", "'")


def satz(text: str) -> str:
    """Setzt genau einen Schlusspunkt — auch nach Abkürzungen wie «u. a.»."""
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else text + "."


def aufzaehlung(teile: list[str], und: str = "und") -> str:
    teile = [t for t in teile if t]
    if not teile:
        return ""
    if len(teile) == 1:
        return teile[0]
    return ", ".join(teile[:-1]) + f" {und} " + teile[-1]


def _bezeichnung(a: Aktivitaet) -> str:
    """Kurzbezeichnung einer Aktivität für den Fliesstext."""
    if a.firma and a.firma.lower() not in a.titel.lower():
        kern = f"{a.titel} ({a.firma})"
    else:
        kern = a.titel
    zusatz = chf(a.potenzial_chf or a.wert_chf)
    return f"{kern} — Potenzial {zusatz}" if zusatz else kern


def tagestext(tag: date, eintraege: list[Aktivitaet]) -> str:
    """Ein bis vier Sätze darüber, was an diesem Tag gelaufen ist."""
    if not eintraege:
        return ""
    geordnet = sorted(eintraege, key=lambda a: a.sortierschluessel())
    anzahl = len(geordnet)
    stunden = sum(a.dauer_h or 0 for a in geordnet)

    saetze: list[str] = []

    kopf = f"{anzahl} {'Aktivität' if anzahl == 1 else 'Aktivitäten'}"
    if stunden:
        kopf += f", {stunden:.1f} Stunden erfasst".replace(".", ",")
    haeufig = Counter(a.kategorie for a in geordnet)
    if len(haeufig) > 1:
        # bei Gleichstand die vertrieblich relevanten Kategorien zuerst nennen
        rang = {"Akquise": 0, "Kundentermin": 1, "Beratung": 2, "Partner / Lieferant": 3}
        sortiert = sorted(haeufig.items(), key=lambda kv: (-kv[1], rang.get(kv[0], 9)))
        gezeigt = sortiert if len(sortiert) <= 4 else sortiert[:3]
        schwerpunkt = aufzaehlung([f"{name} ({zahl})" for name, zahl in gezeigt])
        if len(sortiert) > 4:
            schwerpunkt += " u. a."
        saetze.append(satz(f"{kopf}. Schwerpunkt: {schwerpunkt}"))
    else:
        saetze.append(satz(f"{kopf} — {next(iter(haeufig))}"))

    extern = [a for a in geordnet
              if a.kategorie in ("Akquise", "Kundentermin", "Beratung", "Partner / Lieferant")]
    if extern:
        saetze.append(satz("Nach aussen: " + aufzaehlung([_bezeichnung(a) for a in extern[:4]])))

    # Ein Telefonat mit Ortsangabe ist kein Vor-Ort-Termin
    fern = re.compile(r"\b(telefon|telefonische|call|anruf|video|online|teams)\b", re.I)
    vor_ort = [a for a in geordnet
               if a.ort and "teams" not in a.ort.lower() and not fern.search(a.titel)]
    if vor_ort:
        saetze.append(satz("Vor Ort: " + aufzaehlung(
            [f"{a.titel} in {a.ort.split(',')[0].strip()}" for a in vor_ort[:2]])))

    intern = [a for a in geordnet if a.kategorie == "Interne Arbeit"]
    if intern:
        saetze.append(satz("Intern: " + aufzaehlung([a.titel for a in intern[:3]])))

    offen = [a for a in geordnet if a.naechster_schritt]
    if offen:
        saetze.append(satz("Offen daraus: " + aufzaehlung(
            [f"{a.firma or a.titel} — {a.naechster_schritt}" for a in offen[:3]])))

    return " ".join(saetze)


def gesamttext(eintraege: list[Aktivitaet]) -> str:
    """Ein Absatz über den gesamten erfassten Zeitraum."""
    if not eintraege:
        return "Noch keine Aktivitäten erfasst."
    mit_datum = [a for a in eintraege if a.datum]
    tage = sorted({a.datum for a in mit_datum})
    stunden = sum(a.dauer_h or 0 for a in eintraege)
    firmen = sorted({a.firma for a in eintraege if a.firma})
    potenzial = sum(a.potenzial_chf or a.wert_chf or 0 for a in eintraege)
    offen = [a for a in eintraege if a.naechster_schritt]

    teile = [satz(
        f"{len(eintraege)} Aktivitäten an {len(tage)} Tagen"
        + (f" ({tage[0]:%d.%m.%Y} bis {tage[-1]:%d.%m.%Y})" if tage else "")
        + (f", {stunden:.1f} Stunden erfasst".replace(".", ",") if stunden else "")
    )]
    if firmen:
        teile.append(satz(f"{len(firmen)} Gegenstellen im Kontakt: {aufzaehlung(firmen[:6])}"
                          + (" u. a." if len(firmen) > 6 else "")))
    if potenzial:
        teile.append(f"Erfasstes Potenzial insgesamt {chf(potenzial)}.")
    if offen:
        teile.append(f"{len(offen)} offene nächste Schritte.")
    return " ".join(teile)


def nach_tagen(eintraege: list[Aktivitaet]) -> list[tuple[date, list[Aktivitaet]]]:
    gruppen: dict[date, list[Aktivitaet]] = {}
    for a in eintraege:
        if a.datum:
            gruppen.setdefault(a.datum, []).append(a)
    return [(tag, sorted(gruppen[tag], key=lambda x: x.sortierschluessel()))
            for tag in sorted(gruppen)]
