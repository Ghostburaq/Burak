"""Erzeugt die formatierte Excel-Mappe aus den erfassten Aktivitaeten."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.worksheet import Worksheet

from .model import (BREITEN, EINGABE_SPALTEN, FELDNAMEN, KATEGORIEN,
                    STATUS_AUSWAHL, UEBERSCHRIFTEN, Aktivitaet)

EINGABE_BLATT = "Eingabe"
LEERE_EINGABEZEILEN = 40

# Farbwelt (an das bestehende Deck-Design angelehnt)
NAVY = "FF1B2430"
ROT = "FFE2001A"
HELLGRAU = "FFF4F6F8"
WEISS = "FFFFFFFF"
RAHMEN = "FFD8DEE4"

KOPF_SCHRIFT = Font(name="Calibri", size=11, bold=True, color=WEISS)
KOPF_FUELLUNG = PatternFill("solid", fgColor=NAVY)
TITEL_SCHRIFT = Font(name="Calibri", size=16, bold=True, color=NAVY)
KLEIN = Font(name="Calibri", size=9, color="FF5A6472")
DUENN = Side(style="thin", color=RAHMEN)
GITTER = Border(left=DUENN, right=DUENN, top=DUENN, bottom=DUENN)

GELD_FORMAT = '#,##0;[Red]-#,##0;"—"'
DATUM_FORMAT = "DD.MM.YYYY"
ZEIT_FORMAT = "HH:MM"

GELDFELDER = {"wert_chf", "potenzial_chf", "forecast_chf"}


def _aufhellen(argb: str, anteil: float = 0.82) -> str:
    """Mischt eine Farbe Richtung Weiss — fuer dezente Zellfuellungen."""
    r, g, b = int(argb[2:4], 16), int(argb[4:6], 16), int(argb[6:8], 16)
    mische = lambda k: int(k + (255 - k) * anteil)
    return f"FF{mische(r):02X}{mische(g):02X}{mische(b):02X}"


KATEGORIE_FUELLUNG = {
    name: PatternFill("solid", fgColor=_aufhellen(farbe)) for name, farbe in KATEGORIEN.items()
}
KATEGORIE_SCHRIFT = {
    name: Font(name="Calibri", size=10, bold=True, color=farbe) for name, farbe in KATEGORIEN.items()
}


def _kopfzeile(blatt: Worksheet, ueberschriften: list[str], breiten: list[int],
               zeile: int = 1) -> None:
    for spalte, text in enumerate(ueberschriften, start=1):
        zelle = blatt.cell(row=zeile, column=spalte, value=text)
        zelle.font = KOPF_SCHRIFT
        zelle.fill = KOPF_FUELLUNG
        zelle.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        zelle.border = GITTER
    for spalte, breite in enumerate(breiten, start=1):
        blatt.column_dimensions[get_column_letter(spalte)].width = breite
    blatt.row_dimensions[zeile].height = 30


def _abschliessen(blatt: Worksheet, spalten: int, zeilen: int, kopfzeile: int = 1) -> None:
    if zeilen > kopfzeile:
        blatt.auto_filter.ref = f"A{kopfzeile}:{get_column_letter(spalten)}{zeilen}"
    blatt.freeze_panes = blatt.cell(row=kopfzeile + 1, column=4)
    blatt.sheet_view.showGridLines = False


# ---------------------------------------------------------------------------
# Blatt 1: Aktivitaeten
# ---------------------------------------------------------------------------

def _blatt_aktivitaeten(mappe: Workbook, eintraege: list[Aktivitaet]) -> None:
    blatt = mappe.active
    blatt.title = "Aktivitäten"
    _kopfzeile(blatt, UEBERSCHRIFTEN, BREITEN)

    for index, eintrag in enumerate(eintraege):
        zeile = index + 2
        gerade = index % 2 == 1
        for spalte, feld in enumerate(FELDNAMEN, start=1):
            wert = getattr(eintrag, feld, "")
            if feld == "wochentag":
                wert = eintrag.wochentag
            if isinstance(wert, datetime):
                wert = wert.replace(tzinfo=None)
            zelle = blatt.cell(row=zeile, column=spalte, value=wert if wert not in (None, "") else None)
            zelle.border = GITTER
            zelle.alignment = Alignment(vertical="top", wrap_text=feld in ("titel", "notizen",
                                                                          "naechster_schritt",
                                                                          "bedarf", "teilnehmer"))
            zelle.font = Font(name="Calibri", size=10)
            if gerade:
                zelle.fill = PatternFill("solid", fgColor=HELLGRAU)

            if feld == "datum":
                zelle.number_format = DATUM_FORMAT
            elif feld in ("von", "bis"):
                zelle.number_format = ZEIT_FORMAT
                zelle.alignment = Alignment(horizontal="center", vertical="top")
            elif feld == "dauer_h":
                zelle.number_format = '0.00;;"—"'
                zelle.alignment = Alignment(horizontal="center", vertical="top")
            elif feld in GELDFELDER:
                zelle.number_format = GELD_FORMAT
            elif feld == "wahrscheinlichkeit":
                zelle.number_format = '0%;;"—"'
                zelle.alignment = Alignment(horizontal="center", vertical="top")
            elif feld == "erfasst_am":
                zelle.number_format = "DD.MM.YYYY HH:MM"
            elif feld == "nr":
                zelle.alignment = Alignment(horizontal="center", vertical="top")
                zelle.font = Font(name="Calibri", size=10, color="FF7A828C")
            elif feld == "titel":
                zelle.font = Font(name="Calibri", size=10, bold=True, color=NAVY)
            elif feld == "kategorie":
                zelle.fill = KATEGORIE_FUELLUNG.get(eintrag.kategorie,
                                                    PatternFill("solid", fgColor=HELLGRAU))
                zelle.font = KATEGORIE_SCHRIFT.get(eintrag.kategorie, Font(size=10))
                zelle.alignment = Alignment(horizontal="center", vertical="center")
            elif feld in ("id", "quelle"):
                zelle.font = Font(name="Consolas", size=8, color="FF7A828C")
            elif feld in ("meeting_link", "website") and wert:
                zelle.hyperlink = wert if str(wert).startswith("http") else f"https://{wert}"
                zelle.font = Font(name="Calibri", size=9, color="FF1F6FB2", underline="single")
        blatt.row_dimensions[zeile].height = 34

    _abschliessen(blatt, len(FELDNAMEN), len(eintraege) + 1)


# ---------------------------------------------------------------------------
# Blatt 2: Eingabe (haendisch tippen, wird beim naechsten Lauf eingelesen)
# ---------------------------------------------------------------------------

def _blatt_eingabe(mappe: Workbook) -> None:
    blatt = mappe.create_sheet(EINGABE_BLATT, index=1)
    feldnamen = [s[0] for s in EINGABE_SPALTEN]
    kopf = [s[1] for s in EINGABE_SPALTEN]
    breiten = [s[2] for s in EINGABE_SPALTEN]
    letzte = get_column_letter(len(kopf))

    # Hinweiszeile ueber den Ueberschriften
    blatt.merge_cells(f"A1:{letzte}1")
    hinweis = blatt.cell(row=1, column=1, value=(
        "Hier Aktivitäten von Hand eintippen — eine Zeile pro Vorgang. "
        "Pflicht sind nur Datum und Titel. Beim nächsten Lauf von "
        "«python3 src/aktivitaeten/cli.py» werden die Zeilen übernommen, "
        "erscheinen im Blatt «Aktivitäten» und dieses Blatt ist wieder leer. "
        "ID-Spalte leer lassen — die vergibt das Tool."))
    hinweis.font = Font(name="Calibri", size=10, bold=True, color=WEISS)
    hinweis.fill = PatternFill("solid", fgColor=ROT)
    hinweis.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    blatt.row_dimensions[1].height = 32

    _kopfzeile(blatt, kopf, breiten, zeile=2)

    erste_datenzeile = 3
    letzte_datenzeile = erste_datenzeile + LEERE_EINGABEZEILEN - 1

    kategorie_auswahl = DataValidation(
        type="list", allow_blank=True,
        formula1='"' + ",".join(KATEGORIEN.keys()) + '"',
        prompt="Kategorie wählen (oder leer lassen — dann rät das Tool)",
        promptTitle="Kategorie")
    status_auswahl = DataValidation(
        type="list", allow_blank=True,
        formula1='"' + ",".join(STATUS_AUSWAHL) + '"',
        prompt="Status wählen oder frei eintippen", promptTitle="Status")
    blatt.add_data_validation(kategorie_auswahl)
    blatt.add_data_validation(status_auswahl)

    for zeile in range(erste_datenzeile, letzte_datenzeile + 1):
        for spalte, feld in enumerate(feldnamen, start=1):
            zelle = blatt.cell(row=zeile, column=spalte)
            zelle.border = GITTER
            zelle.font = Font(name="Calibri", size=10)
            zelle.alignment = Alignment(vertical="top",
                                        wrap_text=feld in ("titel", "notizen",
                                                           "naechster_schritt", "bedarf"))
            if zeile % 2 == 0:
                zelle.fill = PatternFill("solid", fgColor=HELLGRAU)
            if feld == "datum":
                zelle.number_format = DATUM_FORMAT
            elif feld in ("von", "bis"):
                zelle.number_format = ZEIT_FORMAT
                zelle.alignment = Alignment(horizontal="center", vertical="top")
            elif feld in ("wert_chf", "potenzial_chf"):
                zelle.number_format = GELD_FORMAT
            elif feld == "wahrscheinlichkeit":
                zelle.number_format = "0"
                zelle.alignment = Alignment(horizontal="center", vertical="top")
            elif feld == "id":
                zelle.font = Font(name="Consolas", size=8, color="FFB0B6BD")
        blatt.row_dimensions[zeile].height = 22

    spalte_kategorie = get_column_letter(feldnamen.index("kategorie") + 1)
    spalte_status = get_column_letter(feldnamen.index("status") + 1)
    kategorie_auswahl.add(f"{spalte_kategorie}{erste_datenzeile}:"
                          f"{spalte_kategorie}{letzte_datenzeile}")
    status_auswahl.add(f"{spalte_status}{erste_datenzeile}:{spalte_status}{letzte_datenzeile}")

    blatt.freeze_panes = "B3"
    blatt.sheet_view.showGridLines = False


# ---------------------------------------------------------------------------
# Blatt 3: Tagesuebersicht
# ---------------------------------------------------------------------------

def _blatt_tage(mappe: Workbook, eintraege: list[Aktivitaet]) -> None:
    blatt = mappe.create_sheet("Tagesübersicht")
    kopf = ["Datum", "Wochentag", "Einträge", "Erste", "Letzte", "Stunden erfasst",
            "Kategorien", "Themen des Tages"]
    _kopfzeile(blatt, kopf, [12, 12, 10, 8, 8, 15, 34, 80])

    pro_tag: dict[date, list[Aktivitaet]] = defaultdict(list)
    for eintrag in eintraege:
        if eintrag.datum:
            pro_tag[eintrag.datum].append(eintrag)

    zeile = 1
    for tag in sorted(pro_tag):
        zeile += 1
        gruppe = sorted(pro_tag[tag], key=lambda a: a.sortierschluessel())
        zeiten = [a.von for a in gruppe if a.von]
        endzeiten = [a.bis for a in gruppe if a.bis]
        stunden = sum(a.dauer_h or 0 for a in gruppe)
        kategorien = sorted({a.kategorie for a in gruppe})
        themen = " · ".join(a.titel for a in gruppe)

        werte = [tag, gruppe[0].wochentag, len(gruppe),
                 min(zeiten) if zeiten else None,
                 max(endzeiten) if endzeiten else (max(zeiten) if zeiten else None),
                 round(stunden, 2) if stunden else None,
                 ", ".join(kategorien), themen]
        for spalte, wert in enumerate(werte, start=1):
            zelle = blatt.cell(row=zeile, column=spalte, value=wert)
            zelle.border = GITTER
            zelle.font = Font(name="Calibri", size=10)
            zelle.alignment = Alignment(vertical="top", wrap_text=spalte >= 7)
            if zeile % 2 == 1:
                zelle.fill = PatternFill("solid", fgColor=HELLGRAU)
        blatt.cell(row=zeile, column=1).number_format = DATUM_FORMAT
        blatt.cell(row=zeile, column=1).font = Font(name="Calibri", size=10, bold=True, color=NAVY)
        for spalte in (4, 5):
            blatt.cell(row=zeile, column=spalte).number_format = ZEIT_FORMAT
        blatt.cell(row=zeile, column=6).number_format = '0.00;;"—"'
        blatt.row_dimensions[zeile].height = 30

    if zeile > 1:
        blatt.conditional_formatting.add(
            f"F2:F{zeile}",
            DataBarRule(start_type="num", start_value=0, end_type="max", color="1F6FB2"))
    _abschliessen(blatt, len(kopf), zeile)


# ---------------------------------------------------------------------------
# Blatt 3: Pipeline
# ---------------------------------------------------------------------------

def _blatt_pipeline(mappe: Workbook, eintraege: list[Aktivitaet]) -> None:
    blatt = mappe.create_sheet("Pipeline")
    kopf = ["Datum", "Firma / Gegenstelle", "Titel", "Status", "Bedarf", "Hauptprodukt",
            "Nächster Schritt", "Wahrsch.", "Wert CHF", "Potenzial CHF", "Gew. Forecast CHF",
            "Kontakt", "E-Mail", "Telefon"]
    _kopfzeile(blatt, kopf, [12, 26, 34, 16, 30, 22, 34, 10, 14, 15, 17, 22, 28, 18])

    relevant = [a for a in eintraege
                if a.kategorie in ("Akquise", "Kundentermin", "Beratung")
                or any(v for v in (a.wert_chf, a.potenzial_chf, a.forecast_chf))]
    relevant.sort(key=lambda a: (-(a.potenzial_chf or a.wert_chf or 0), a.sortierschluessel()))

    zeile = 1
    for eintrag in relevant:
        zeile += 1
        werte = [eintrag.datum, eintrag.firma, eintrag.titel, eintrag.status, eintrag.bedarf,
                 eintrag.hauptprodukt, eintrag.naechster_schritt, eintrag.wahrscheinlichkeit,
                 eintrag.wert_chf, eintrag.potenzial_chf, eintrag.forecast_chf,
                 eintrag.kontakt, eintrag.email, eintrag.telefon]
        for spalte, wert in enumerate(werte, start=1):
            zelle = blatt.cell(row=zeile, column=spalte, value=wert if wert not in ("", None) else None)
            zelle.border = GITTER
            zelle.font = Font(name="Calibri", size=10)
            zelle.alignment = Alignment(vertical="top", wrap_text=spalte in (3, 5, 7))
            if zeile % 2 == 1:
                zelle.fill = PatternFill("solid", fgColor=HELLGRAU)
        blatt.cell(row=zeile, column=1).number_format = DATUM_FORMAT
        blatt.cell(row=zeile, column=2).font = Font(name="Calibri", size=10, bold=True, color=NAVY)
        blatt.cell(row=zeile, column=8).number_format = '0%;;"—"'
        for spalte in (9, 10, 11):
            blatt.cell(row=zeile, column=spalte).number_format = GELD_FORMAT
        blatt.row_dimensions[zeile].height = 30

    if zeile > 1:
        zeile += 1
        blatt.cell(row=zeile, column=1, value="Summe").font = Font(bold=True, color=WEISS)
        for spalte in range(1, len(kopf) + 1):
            zelle = blatt.cell(row=zeile, column=spalte)
            zelle.fill = PatternFill("solid", fgColor=NAVY)
            zelle.font = Font(name="Calibri", size=11, bold=True, color=WEISS)
        for spalte in (9, 10, 11):
            buchstabe = get_column_letter(spalte)
            zelle = blatt.cell(row=zeile, column=spalte,
                               value=f"=SUM({buchstabe}2:{buchstabe}{zeile - 1})")
            zelle.number_format = GELD_FORMAT
            zelle.font = Font(name="Calibri", size=11, bold=True, color=WEISS)
    _abschliessen(blatt, len(kopf), zeile - 1)


# ---------------------------------------------------------------------------
# Blatt 4: Kontakte
# ---------------------------------------------------------------------------

def _blatt_kontakte(mappe: Workbook, eintraege: list[Aktivitaet]) -> None:
    blatt = mappe.create_sheet("Kontakte")
    kopf = ["Firma / Gegenstelle", "Kontakt", "E-Mail", "Telefon", "Website",
            "Kontakte gesamt", "Erster Kontakt", "Letzter Kontakt", "Offenes Potenzial CHF",
            "Letzter Stand"]
    _kopfzeile(blatt, kopf, [28, 24, 30, 20, 30, 14, 14, 14, 20, 46])

    gruppen: dict[str, list[Aktivitaet]] = defaultdict(list)
    for eintrag in eintraege:
        schluessel = eintrag.firma or eintrag.kontakt
        if schluessel:
            gruppen[schluessel].append(eintrag)

    zeile = 1
    for firma in sorted(gruppen, key=lambda f: f.lower()):
        gruppe = sorted(gruppen[firma], key=lambda a: a.sortierschluessel())
        zeile += 1
        letzter = gruppe[-1]
        werte = [
            firma,
            next((a.kontakt for a in reversed(gruppe) if a.kontakt), ""),
            next((a.email for a in reversed(gruppe) if a.email), ""),
            next((a.telefon for a in reversed(gruppe) if a.telefon), ""),
            next((a.website for a in reversed(gruppe) if a.website), ""),
            len(gruppe),
            gruppe[0].datum,
            gruppe[-1].datum,
            max((a.potenzial_chf or a.wert_chf or 0) for a in gruppe) or None,
            letzter.naechster_schritt or letzter.status or letzter.titel,
        ]
        for spalte, wert in enumerate(werte, start=1):
            zelle = blatt.cell(row=zeile, column=spalte, value=wert if wert not in ("", None) else None)
            zelle.border = GITTER
            zelle.font = Font(name="Calibri", size=10)
            zelle.alignment = Alignment(vertical="top", wrap_text=spalte == 10)
            if zeile % 2 == 1:
                zelle.fill = PatternFill("solid", fgColor=HELLGRAU)
        blatt.cell(row=zeile, column=1).font = Font(name="Calibri", size=10, bold=True, color=NAVY)
        for spalte in (7, 8):
            blatt.cell(row=zeile, column=spalte).number_format = DATUM_FORMAT
        blatt.cell(row=zeile, column=9).number_format = GELD_FORMAT
        blatt.row_dimensions[zeile].height = 28

    _abschliessen(blatt, len(kopf), zeile)


# ---------------------------------------------------------------------------
# Blatt 5: Quellen
# ---------------------------------------------------------------------------

def _blatt_quellen(mappe: Workbook, quellen: dict[str, dict]) -> None:
    blatt = mappe.create_sheet("Quellen")
    kopf = ["Dateiname(n)", "Typ", "Einträge", "Importe", "Grösse (KB)",
            "Importiert am", "SHA-256"]
    _kopfzeile(blatt, kopf, [56, 14, 10, 10, 13, 20, 68])

    zeile = 1
    for hash_wert, meta in sorted(quellen.items(),
                                  key=lambda kv: kv[1].get("importiert_am", "")):
        zeile += 1
        werte = [", ".join(meta.get("dateinamen", [])), meta.get("typ", ""),
                 meta.get("eintraege", 0), meta.get("importe", 1),
                 round(meta.get("groesse_bytes", 0) / 1024, 1),
                 meta.get("importiert_am", "").replace("T", " "), hash_wert]
        for spalte, wert in enumerate(werte, start=1):
            zelle = blatt.cell(row=zeile, column=spalte, value=wert)
            zelle.border = GITTER
            zelle.font = Font(name="Calibri", size=10)
            zelle.alignment = Alignment(vertical="top", wrap_text=spalte == 1)
            if zeile % 2 == 1:
                zelle.fill = PatternFill("solid", fgColor=HELLGRAU)
        blatt.cell(row=zeile, column=7).font = Font(name="Consolas", size=8, color="FF7A828C")
        if (meta.get("importe", 1) or 1) > 1:
            zelle = blatt.cell(row=zeile, column=4)
            zelle.font = Font(name="Calibri", size=10, bold=True, color=ROT)
        blatt.row_dimensions[zeile].height = 26

    _abschliessen(blatt, len(kopf), zeile)


# ---------------------------------------------------------------------------
# Einstieg
# ---------------------------------------------------------------------------

def schreiben(ziel: Path, eintraege: list[Aktivitaet], quellen: dict[str, dict]) -> Path:
    mappe = Workbook()
    mappe.properties.title = "Aktivitäten-Übersicht"
    mappe.properties.creator = "Aktivitaeten-Pipeline"

    _blatt_aktivitaeten(mappe, eintraege)
    _blatt_eingabe(mappe)
    _blatt_tage(mappe, eintraege)
    _blatt_pipeline(mappe, eintraege)
    _blatt_kontakte(mappe, eintraege)
    _blatt_quellen(mappe, quellen)

    ziel.parent.mkdir(parents=True, exist_ok=True)
    mappe.save(ziel)
    return ziel
