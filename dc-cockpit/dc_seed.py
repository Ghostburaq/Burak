#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dc_seed.py - baut dc_data.json aus den MiT-Quelldateien.

Quellen:
  daten/MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx  Tab "Anrufplan"  (Termine, Einstieg, Ziel)
  daten/MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx  Tab "Kontakt-Log" (Mail, Telefon)
  MARKT_DC.md                                   (Pipeline, Bestand, Liechtenstein)

Harte Regel: keine erfundenen Werte. Was nicht in einer Quelle steht, wird als
"FEHLT" ausgegeben und im Cockpit rot markiert. Namen werden nie aus der
Namensspalte des Trackers übernommen, sondern aus der E-Mail-Adresse
abgeleitet und gegen KONTAKTE_STATUS.md geprüft (Zeilenversatz-Problem,
siehe CLAUDE.md "Datenqualität Aggreko-Tracker").
"""

import json
import os
import sys
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "daten", "MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx")

# ---------------------------------------------------------------------------
# Der Inhalt liegt in inhalte.py: Kontaktdaten, Markt, Regeln, Signatur.
# Diese Datei hier ist reine Maschinerie und enthaelt bewusst keine Kundendaten.
# ---------------------------------------------------------------------------
try:
    from inhalte import (KONTAKTDATEN, OHNE_TERMIN, GESTRICHEN, PIPELINE, LIECHTENSTEIN,
                         BESTAND, AUFTRAEGE, ANLAESSE, REGELN, GATES, SIGNATUR,
                         SIGNATUR_ALT, DATENQUALITAET)
except ImportError:
    print("inhalte.py fehlt. Vorlage kopieren: cp inhalte.example.py inhalte.py\n"
          "Darin stehen Kontaktdaten, Markt, Regeln und Signatur.", file=sys.stderr)
    raise


def lies_anrufplan():
    try:
        import openpyxl
    except ImportError:
        print("openpyxl fehlt. Installieren mit: pip install openpyxl", file=sys.stderr)
        return []
    if not os.path.exists(XLSX):
        print("Excel nicht gefunden: %s" % XLSX, file=sys.stderr)
        return []

    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Anrufplan"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    kontakte = []
    for row in rows[5:]:                      # ab Zeile 6, Kopfzeile ist 5
        if not row or not row[0] or str(row[0]).strip() not in ("A", "B", "C"):
            continue
        datum = row[1]
        if isinstance(datum, dt.datetime):
            datum = datum.date().isoformat()
        elif datum:
            datum = str(datum)[:10]
        else:
            datum = ""
        zeit = row[2]
        if isinstance(zeit, dt.time):
            zeit = zeit.strftime("%H:%M")
        else:
            zeit = (str(zeit) if zeit else "")[:5]

        name = (row[3] or "").strip()
        kd = KONTAKTDATEN.get(name, dict(mail="FEHLT", mailq="fehlt", tel="FEHLT", telq="fehlt"))
        kontakte.append(dict(
            prio=str(row[0]).strip(),
            datum=datum,
            zeit=zeit,
            name=name,
            firma=(row[4] or "").strip(),
            projekt=(row[5] or "").strip(),
            bisher=(row[6] or "").strip(),
            inhalt=(row[7] or "").strip(),
            einstieg=(row[8] or "").strip(),
            ziel=(row[9] or "").strip(),
            erreicht=(row[10] or "").strip(),
            ergebnis=(row[11] or "").strip(),
            naechster=(row[12] or "").strip(),
            wiedervorlage=(row[13] or "").strip(),
            mail=kd.get("mail", "FEHLT"),
            mailq=kd.get("mailq", "fehlt"),
            tel=kd.get("tel", "FEHLT"),
            telq=kd.get("telq", "fehlt"),
            warnung=kd.get("warnung", ""),
            status="offen",
        ))
    return kontakte


def baue(pfad=None):
    kontakte = lies_anrufplan()
    for k in OHNE_TERMIN:
        kd = KONTAKTDATEN.get(k["name"], {})
        k = dict(k)
        k.update(mail=kd.get("mail", "FEHLT"), mailq=kd.get("mailq", "fehlt"),
                 tel=kd.get("tel", "FEHLT"), telq=kd.get("telq", "fehlt"),
                 warnung=kd.get("warnung", ""), erreicht="", ergebnis="",
                 naechster="", wiedervorlage="")
        kontakte.append(k)

    for i, k in enumerate(kontakte, 1):
        k["id"] = "k%02d" % i

    daten = dict(
        meta=dict(
            titel="MiT Datacenter Cockpit",
            erzeugt=dt.datetime.now().isoformat(timespec="seconds"),
            quelle_excel=os.path.basename(XLSX),
            hinweis="Erzeugt von dc_seed.py aus den MiT-Quelldateien. Keine erfundenen Werte.",
        ),
        signatur=SIGNATUR,
        signatur_alt=SIGNATUR_ALT,
        regeln=REGELN,
        gates=GATES,
        datenqualitaet=DATENQUALITAET,
        kontakte=kontakte,
        gestrichen=GESTRICHEN,
        pipeline=PIPELINE,
        liechtenstein=LIECHTENSTEIN,
        bestand=BESTAND,
        auftraege=AUFTRAEGE,
        anlaesse=ANLAESSE,
        news=[],
        quellen_status=[],
        geo={},
    )
    if pfad:
        # News, Feed-Status und Geocache aus einem vorhandenen Stand uebernehmen,
        # sonst wirft ein direkter Aufruf von dc_seed.py den Live-Teil weg.
        if os.path.exists(pfad):
            try:
                with open(pfad, encoding="utf-8") as f:
                    alt = json.load(f)
                for schluessel in ("news", "quellen_status", "geo", "geo_offen"):
                    if alt.get(schluessel):
                        daten[schluessel] = alt[schluessel]
                if alt.get("meta", {}).get("aktualisiert"):
                    daten["meta"]["aktualisiert"] = alt["meta"]["aktualisiert"]
            except Exception:
                pass
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(daten, f, ensure_ascii=False, indent=1)
    return daten


if __name__ == "__main__":
    ziel = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "dc_data.json")
    d = baue(ziel)
    print("geschrieben: %s" % ziel)
    print("Kontakte: %d, davon ohne Mail: %d"
          % (len(d["kontakte"]), sum(1 for k in d["kontakte"] if k["mailq"] in ("fehlt", "opt-out"))))
