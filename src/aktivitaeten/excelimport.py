"""Excel zurücklesen — die Mappe ist Ausgabe *und* Eingabe.

Zwei Wege führen aus Excel zurück in die Pipeline:

1. **Blatt «Eingabe»** — von Hand getippte Zeilen werden zu neuen Einträgen.
2. **Blatt «Aktivitäten»** — wird dort eine Zelle geändert, merkt sich die
   Pipeline das als *Korrektur* zu dieser ID. Die Korrektur überlebt jeden
   weiteren Import derselben Quelldatei; die Automatik überschreibt sie nicht.

Eine leere Zelle gilt als "nicht angefasst". Wer ein Feld bewusst leeren will,
schreibt ein einzelnes ``-`` hinein.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, time
from pathlib import Path

from openpyxl import load_workbook

from .model import (EDITIERBAR, EINGABE_SPALTEN, FELDNAMEN, UEBERSCHRIFTEN,
                    Aktivitaet, wert_konvertieren)

EINGABE_BLATT = "Eingabe"
HAUPT_BLATT = "Aktivitäten"
LEEREN = "-"


def _schluessel(text: object) -> str:
    """Ueberschrift -> vergleichbarer Schluessel (ohne Umlaute, Sternchen, Fussnoten)."""
    roh = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", roh.lower())


# Ueberschrift -> Feldname, fuer beide Blaetter und tolerant gegen Umbenennungen
_UEBERSCHRIFT_ZU_FELD: dict[str, str] = {}
for _feld, _titel, _ in EINGABE_SPALTEN:
    _UEBERSCHRIFT_ZU_FELD[_schluessel(_titel)] = _feld
for _feld, _titel in zip(FELDNAMEN, UEBERSCHRIFTEN):
    _UEBERSCHRIFT_ZU_FELD.setdefault(_schluessel(_titel), _feld)


def _kopf_lesen(blatt, zeile: int) -> dict[int, str]:
    zuordnung: dict[int, str] = {}
    for spalte in range(1, blatt.max_column + 1):
        feld = _UEBERSCHRIFT_ZU_FELD.get(_schluessel(blatt.cell(row=zeile, column=spalte).value))
        if feld:
            zuordnung[spalte] = feld
    return zuordnung


def _zelle(wert):
    if isinstance(wert, str):
        wert = wert.strip()
        return wert or None
    return wert


def _normalisieren(feld: str, wert):
    """Excel-Wert in den Typ des Feldes bringen; None bei leer/unlesbar."""
    if wert is None:
        return None
    if isinstance(wert, str) and wert.strip() == LEEREN:
        return ""
    try:
        wert = wert_konvertieren(feld, wert)
    except (ValueError, TypeError):
        return None
    # "40" in der Spalte "Wahrsch. %" meint 40 %, "0.4" meint dasselbe
    if feld == "wahrscheinlichkeit" and isinstance(wert, float) and wert > 1:
        wert = round(wert / 100, 4)
    return wert


def _vergleichbar(wert):
    """Damit 0.5 == 0.50 und datetime == date beim Vergleich nicht auseinanderfallen."""
    if isinstance(wert, datetime):
        return wert.replace(second=0, microsecond=0)
    if isinstance(wert, time):
        return wert.replace(second=0, microsecond=0)
    if isinstance(wert, float):
        return round(wert, 4)
    if isinstance(wert, str):
        return wert.strip()
    return wert


# ---------------------------------------------------------------------------

def eingabezeilen_lesen(pfad: Path) -> list[Aktivitaet]:
    """Neue, von Hand getippte Zeilen aus dem Blatt «Eingabe»."""
    if not pfad.exists():
        return []
    mappe = load_workbook(pfad, data_only=True)
    if EINGABE_BLATT not in mappe.sheetnames:
        return []
    blatt = mappe[EINGABE_BLATT]
    zuordnung = _kopf_lesen(blatt, zeile=2)
    if not zuordnung:
        return []

    neue: list[Aktivitaet] = []
    for zeile in range(3, blatt.max_row + 1):
        werte: dict[str, object] = {}
        for spalte, feld in zuordnung.items():
            wert = _normalisieren(feld, _zelle(blatt.cell(row=zeile, column=spalte).value))
            if wert not in (None, ""):
                werte[feld] = wert
        if not werte.get("titel") and not werte.get("datum"):
            continue                                    # leere Zeile

        a = Aktivitaet(
            quelle="Excel-Eingabe",
            typ="Manuell erfasst",
            titel=str(werte.get("titel") or "(ohne Titel)"),
            erfasst_am=datetime.now().replace(microsecond=0),
        )
        for feld, wert in werte.items():
            if feld != "id" and hasattr(a, feld):
                setattr(a, feld, wert)

        a.id = str(werte.get("id") or _manuelle_id(a))
        if not a.kategorie or a.kategorie == "Sonstiges":
            from . import felder
            a.kategorie = felder.kategorie_bestimmen(a.titel, a.notizen, a.typ, a.ort)
            if a.kategorie == "Sonstiges":
                a.kategorie = "Kundentermin" if a.firma else "Interne Arbeit"
        if not a.status:
            a.status = "Offen"
        if a.von and a.bis and a.dauer_h is None:
            beginn = datetime.combine(a.datum or date.today(), a.von)
            ende = datetime.combine(a.datum or date.today(), a.bis)
            if ende > beginn:
                a.dauer_h = round((ende - beginn).total_seconds() / 3600, 2)
        if a.wert_chf is not None and a.wahrscheinlichkeit is not None and a.forecast_chf is None:
            a.forecast_chf = round(a.wert_chf * a.wahrscheinlichkeit, 2)
        neue.append(a)
    return neue


def _manuelle_id(a: Aktivitaet) -> str:
    import hashlib
    roh = f"{a.datum}|{a.von}|{a.titel.lower().strip()}"
    return "manuell:" + hashlib.sha256(roh.encode("utf-8")).hexdigest()[:16]


def korrekturen_lesen(pfad: Path, bestand: dict[str, Aktivitaet]) -> dict[str, dict]:
    """Von Hand geänderte Zellen im Blatt «Aktivitäten» als Korrekturen erfassen."""
    if not pfad.exists():
        return {}
    mappe = load_workbook(pfad, data_only=True)
    if HAUPT_BLATT not in mappe.sheetnames:
        return {}
    blatt = mappe[HAUPT_BLATT]
    zuordnung = _kopf_lesen(blatt, zeile=1)
    id_spalte = next((s for s, f in zuordnung.items() if f == "id"), None)
    if id_spalte is None:
        return {}

    gefunden: dict[str, dict] = {}
    for zeile in range(2, blatt.max_row + 1):
        kennung = _zelle(blatt.cell(row=zeile, column=id_spalte).value)
        if not kennung or str(kennung) not in bestand:
            continue
        original = bestand[str(kennung)]
        for spalte, feld in zuordnung.items():
            if feld not in EDITIERBAR:
                continue
            neu = _normalisieren(feld, _zelle(blatt.cell(row=zeile, column=spalte).value))
            if neu is None:                     # leere Zelle = nicht angefasst
                continue
            if _vergleichbar(neu) == _vergleichbar(getattr(original, feld, None)):
                continue
            gefunden.setdefault(str(kennung), {})[feld] = neu
    return gefunden


def fremde_mappe_lesen(pfad: Path) -> list[Aktivitaet]:
    """Beliebige .xlsx aus der inbox: erstes Blatt mit passenden Ueberschriften."""
    mappe = load_workbook(pfad, data_only=True)
    for name in mappe.sheetnames:
        blatt = mappe[name]
        for kopfzeile in (1, 2):
            zuordnung = _kopf_lesen(blatt, zeile=kopfzeile)
            if {"titel", "datum"} <= set(zuordnung.values()):
                return _zeilen_lesen(blatt, zuordnung, kopfzeile + 1, pfad.name)
    return []


def _zeilen_lesen(blatt, zuordnung: dict[int, str], erste: int, quelle: str) -> list[Aktivitaet]:
    eintraege: list[Aktivitaet] = []
    for zeile in range(erste, blatt.max_row + 1):
        werte = {}
        for spalte, feld in zuordnung.items():
            wert = _normalisieren(feld, _zelle(blatt.cell(row=zeile, column=spalte).value))
            if wert not in (None, ""):
                werte[feld] = wert
        if not werte.get("titel"):
            continue
        a = Aktivitaet(quelle=quelle, typ="Import (Excel)",
                       erfasst_am=datetime.now().replace(microsecond=0))
        for feld, wert in werte.items():
            if feld != "id" and hasattr(a, feld):
                setattr(a, feld, wert)
        a.id = str(werte.get("id") or _manuelle_id(a))
        if not a.status:
            a.status = "Offen"
        eintraege.append(a)
    return eintraege
