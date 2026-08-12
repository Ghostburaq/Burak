"""Einstiegspunkt: Dateien einlesen, Registry pflegen, Excel + Report schreiben.

    python3 src/aktivitaeten/cli.py                      # alles aus inbox/ verarbeiten
    python3 src/aktivitaeten/cli.py datei1.ics datei2.eml
    python3 src/aktivitaeten/cli.py bild.png --notiz "Angebot X versendet"
    python3 src/aktivitaeten/cli.py --neu-aufbauen      # Registry verwerfen und neu lesen
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):                     # Direktaufruf ohne -m
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from aktivitaeten import (andere, bericht, emlfile, excel,              # type: ignore
                              excelimport, icsfile)
    from aktivitaeten.model import Aktivitaet                                # type: ignore
    from aktivitaeten.registry import Registry, datei_hash                   # type: ignore
else:
    from . import andere, bericht, emlfile, excel, excelimport, icsfile
    from .model import Aktivitaet
    from .registry import Registry, datei_hash

WURZEL = Path(__file__).resolve().parents[2]
INBOX = WURZEL / "inbox"
ARCHIV = WURZEL / "inbox" / "verarbeitet"
REGISTRY = WURZEL / "data" / "registry.json"
EXCEL = WURZEL / "output" / "Aktivitaeten.xlsx"
REPORT = WURZEL / "output" / "report.md"

UNTERSTUETZT_TEXT = {".ics", ".ical", ".eml", ".txt", ".md", ".log", ".csv"}
IGNORIEREN = {".gitkeep", ".ds_store", "readme.md", "thumbs.db", "desktop.ini"}


def dateien_sammeln(argumente: list[str]) -> list[Path]:
    pfade: list[Path] = []
    for eintrag in argumente:
        pfad = Path(eintrag).expanduser()
        if pfad.is_dir():
            pfade.extend(sorted(p for p in pfad.rglob("*") if p.is_file()))
        elif pfad.is_file():
            pfade.append(pfad)
        else:
            print(f"  ! nicht gefunden: {pfad}")
    if not argumente and INBOX.exists():
        pfade = sorted(p for p in INBOX.rglob("*")
                       if p.is_file() and ARCHIV not in p.parents)
    return [p for p in pfade
            if p.name.lower() not in IGNORIEREN and not p.name.startswith(".")]


def datei_verarbeiten(pfad: Path, notiz: str = "") -> tuple[list[Aktivitaet], str]:
    endung = pfad.suffix.lower()
    hash_wert = datei_hash(pfad)
    roh_bytes = pfad.read_bytes()

    if endung in (".ics", ".ical"):
        text = roh_bytes.decode("utf-8", "replace")
        return icsfile.parsen(str(pfad), text, pfad.name, hash_wert), "Kalender"
    if endung == ".eml":
        text = roh_bytes.decode("utf-8", "replace")
        return emlfile.parsen(str(pfad), text, pfad.name, hash_wert), "E-Mail"
    if endung in (".xlsx", ".xlsm"):
        return excelimport.fremde_mappe_lesen(pfad), "Excel-Import"
    if endung == ".txt":
        # "bild.png.txt" oder "bild.txt" neben "bild.png" ist eine Notiz zur Datei
        geschwister = [p for p in pfad.parent.iterdir()
                       if p.is_file() and p != pfad
                       and (p.name == pfad.stem or p.stem == pfad.stem)]
        if geschwister:
            return [], "Sidecar-Notiz"
    return andere.parsen(str(pfad), roh_bytes, pfad.name, hash_wert, notiz), "Datei"


def report_schreiben(ziel: Path, eintraege: list[Aktivitaet], quellen: dict,
                     bilanz: dict[str, int]) -> None:
    from collections import Counter
    from datetime import datetime

    zeilen: list[str] = []
    zeilen.append("# Aktivitäten-Report\n")
    zeilen.append(f"_Stand: {datetime.now():%d.%m.%Y %H:%M} · "
                  f"{len(eintraege)} Einträge aus {len(quellen)} Quelldateien_\n")

    zeilen.append("## Lauf\n")
    zeilen.append(f"- neu erfasst: **{bilanz['neu']}**")
    zeilen.append(f"- aktualisiert: **{bilanz['aktualisiert']}**")
    zeilen.append(f"- manuelle Korrekturen aus Excel: **{bilanz.get('korrekturen', 0)}**")
    zeilen.append(f"- unverändert (Duplikat): **{bilanz['unveraendert']}**")
    zeilen.append(f"- übersprungene Dateien (identisch bereits importiert): "
                  f"**{bilanz['dateien_doppelt']}**\n")

    kategorien = Counter(a.kategorie for a in eintraege)
    zeilen.append("## Verteilung nach Kategorie\n")
    zeilen.append("| Kategorie | Einträge | Stunden |")
    zeilen.append("|---|---:|---:|")
    for name, anzahl in kategorien.most_common():
        stunden = sum(a.dauer_h or 0 for a in eintraege if a.kategorie == name)
        zeilen.append(f"| {name} | {anzahl} | {stunden:.2f} |")
    zeilen.append("")

    zeilen.append("## Zusammenfassung\n")
    zeilen.append(bericht.gesamttext(eintraege) + "\n")

    zeilen.append("## Tagebuch\n")
    for tag, gruppe in bericht.nach_tagen(eintraege):
        zeilen.append(f"\n### {tag:%d.%m.%Y} · {gruppe[0].wochentag}\n")
        zeilen.append(bericht.tagestext(tag, gruppe) + "\n")
        for a in gruppe:
            betrag = bericht.chf(a.potenzial_chf or a.wert_chf)
            zusatz = "".join([
                f" · {a.firma}" if a.firma else "",
                f" · Potenzial {betrag}" if betrag else "",
                f" · nächster Schritt: {a.naechster_schritt}" if a.naechster_schritt else "",
            ])
            zeilen.append(f"- **Pos. {a.nr}** · `{a.zeit or '—'}` **{a.titel}** "
                          f"— {a.kategorie}{zusatz}")

    offen = [a for a in eintraege if a.naechster_schritt or a.follow_up]
    if offen:
        zeilen.append("\n## Offene nächste Schritte\n")
        for a in offen:
            schritt = a.naechster_schritt or f"Follow-up: {a.follow_up}"
            zeilen.append(f"- **{a.firma or a.titel}** — {schritt}")

    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text("\n".join(zeilen) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dateien einlesen und die Aktivitäten-Excel aktualisieren.")
    parser.add_argument("dateien", nargs="*", help="Dateien oder Ordner (Standard: inbox/)")
    parser.add_argument("--notiz", default="", help="Notiz für alle Dateien dieses Laufs")
    parser.add_argument("--neu-aufbauen", action="store_true",
                        help="Registry verwerfen und alles neu einlesen")
    parser.add_argument("--excel", default=str(EXCEL), help="Zielpfad der Excel-Datei")
    parser.add_argument("--registry", default=str(REGISTRY), help="Pfad der Registry-JSON")
    parser.add_argument("--ohne-excel-rueckimport", action="store_true",
                        help="Blatt «Eingabe» und manuelle Korrekturen nicht zurücklesen")
    argumente = parser.parse_args(argv)

    registry_pfad = Path(argumente.registry)
    excel_pfad = Path(argumente.excel)
    if argumente.neu_aufbauen and registry_pfad.exists():
        registry_pfad.unlink()
    registry = Registry(registry_pfad)
    bilanz = {"neu": 0, "aktualisiert": 0, "unveraendert": 0,
              "dateien_doppelt": 0, "korrekturen": 0}

    # Zuerst zurücklesen, was in der bestehenden Mappe von Hand eingetragen
    # oder korrigiert wurde — sonst wäre es nach dem Neuschreiben weg.
    if excel_pfad.exists() and not argumente.ohne_excel_rueckimport:
        try:
            korrekturen = excelimport.korrekturen_lesen(excel_pfad, registry.eintraege)
            bilanz["korrekturen"] = registry.korrekturen_uebernehmen(korrekturen)
            if bilanz["korrekturen"]:
                print(f"  ✎ {bilanz['korrekturen']} manuelle Korrektur(en) "
                      f"aus Blatt «Aktivitäten» übernommen")
            for eintrag in excelimport.eingabezeilen_lesen(excel_pfad):
                ergebnis = registry.aufnehmen(eintrag)
                bilanz[ergebnis] += 1
                if ergebnis != "unveraendert":
                    datum = f"{eintrag.datum:%d.%m.%Y}" if eintrag.datum else "ohne Datum"
                    print(f"  ✎ {datum}  {eintrag.titel[:60]}  (Blatt «Eingabe»)")
        except Exception as fehler:
            print(f"  ! Excel-Rückimport übersprungen: {type(fehler).__name__}: {fehler}")

    dateien = dateien_sammeln(argumente.dateien)
    if not dateien and not registry.eintraege:
        print("Keine Dateien gefunden. Lege etwas in inbox/ ab oder gib Pfade an.")

    for pfad in dateien:
        hash_wert = datei_hash(pfad)
        if registry.quelle_bekannt(hash_wert):
            registry.quelle_vermerken(hash_wert, pfad.name, "", 0, pfad.stat().st_size)
            bilanz["dateien_doppelt"] += 1
            print(f"  = {pfad.name}  (identisch bereits erfasst)")
            continue

        try:
            eintraege, typ = datei_verarbeiten(pfad, argumente.notiz)
        except Exception as fehler:                      # eine kaputte Datei stoppt nichts
            print(f"  ! {pfad.name}: {type(fehler).__name__}: {fehler}")
            continue

        if not eintraege:
            print(f"  – {pfad.name}  ({typ}, kein eigener Eintrag)")
            continue

        registry.quelle_vermerken(hash_wert, pfad.name, typ, len(eintraege),
                                  pfad.stat().st_size)
        for eintrag in eintraege:
            ergebnis = registry.aufnehmen(eintrag)
            bilanz[ergebnis] += 1
            zeichen = {"neu": "+", "aktualisiert": "~", "unveraendert": "="}[ergebnis]
            datum = f"{eintrag.datum:%d.%m.%Y}" if eintrag.datum else "ohne Datum"
            print(f"  {zeichen} {datum}  {eintrag.titel[:60]}")

    registry.speichern()
    eintraege = registry.sortiert()
    try:
        ziel = excel.schreiben(excel_pfad, eintraege, registry.quellen)
    except PermissionError:
        print(f"\n! {excel_pfad} lässt sich nicht schreiben — die Datei ist "
              f"vermutlich noch in Excel geöffnet.\n"
              f"  Excel schliessen und den Befehl erneut ausführen. "
              f"Die eingelesenen Daten sind bereits gesichert.")
        return 1
    report_schreiben(REPORT, eintraege, registry.quellen, bilanz)

    print(f"\n{len(eintraege)} Einträge gesamt "
          f"(neu {bilanz['neu']}, aktualisiert {bilanz['aktualisiert']}, "
          f"Korrekturen {bilanz['korrekturen']}, "
          f"Duplikate {bilanz['unveraendert'] + bilanz['dateien_doppelt']})")
    print(f"Excel:    {ziel}")
    print(f"Report:   {REPORT}")
    print(f"Registry: {registry_pfad}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
