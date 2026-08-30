#!/usr/bin/env python3
"""
Lauf 2 vom 29.08.2026, KW 35. Vertiefungsrecherche nach dem Erstaufbau.

Aenderungen:
- ZRH2 Glattfelden: Widerspruch aufgeloest, Phase Betrieb
- ZUR01A Rafz: Phase Betrieb
- ZUR02 Beringen: Amstein + Walthert als beteiligter Planer belegt, Rolle offen
- ZUR3 Glattbrugg: Gruner als beteiligter Planer belegt, Rolle offen
- Neue Zeile: Microsoft KI-Ausbau Schweiz, Standorte offen
- Green Dielsdorf: Zaehlungs-Widerspruch praezisiert
- 03_Kontakte: Fachplaner-Firmen ergaenzt, Namen FEHLT
- 06_Changelog: eine Zeile pro Aenderung
- 05_Quellen_Montag: Pruefdatum LinkedIn weiterhin leer, Fachmedien aktualisiert

Vorgehen nach CLAUDE.md Abschnitt 5: Backup zuerst, laden ohne data_only.
"""

import glob
import os
import shutil
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
ORDNER = os.path.dirname(HERE)
DATEI = os.path.join(ORDNER, "MiT_Datacenter_Radar_CH_V1.0.xlsx")
HEUTE = "2026-08-29"
STAND = "29.08.2026"

# 1. Backup
backup = os.path.join(ORDNER, f"MiT_Datacenter_Radar_CH_V1.0_backup_{HEUTE}.xlsx")
shutil.copy2(DATEI, backup)
backups = sorted(glob.glob(os.path.join(ORDNER, "MiT_Datacenter_Radar_CH_V1.0_backup_*.xlsx")))
for alt in backups[:-4]:
    os.remove(alt)
print(f"Backup: {os.path.basename(backup)}")

wb = load_workbook(DATEI)   # ohne data_only, sonst sind die Formeln weg
ws = wb["02_Projekt_Radar"]

text_font = Font(name="Arial", size=10)
duenn = Side(style="thin", color="BFBFBF")
rahmen = Border(left=duenn, right=duenn, top=duenn, bottom=duenn)
gelb_fill = PatternFill("solid", fgColor="FFF2CC")


def zeile_von(projektname):
    for z in range(5, ws.max_row + 1):
        if ws.cell(row=z, column=2).value == projektname:
            return z
    raise KeyError(projektname)


aenderungen = []   # (Projekt, was, url, konsequenz)

# --- ZRH2 Glattfelden: Widerspruch aufgeloest -------------------------------
z = zeile_von("ZRH2 Glattfelden")
ws.cell(row=z, column=7, value="Betrieb")
ws.cell(row=z, column=8, value="eroeffnet Sommer 2024")
ws.cell(row=z, column=13, value="Betrieb: Wartungsfenster, NEA-Testzyklus, PQ-Audit")
ws.cell(row=z, column=20, value="https://vantage-dc.com/news/vantage-data-centers-expands-emea-portfolio-with-second-zurich-campus-fueled-by-more-than-chf-370-million-investment/ | https://www.datacenterdynamics.com/en/news/vantage-launches-second-data-center-in-switzerland/")
ws.cell(row=z, column=21, value=STAND)
ws.cell(row=z, column=23, value="24 MW kritische IT-Kapazitaet, rund 21000 m2, Investition ueber CHF 370 Mio, "
        "rund 30 km noerdlich von Zuerich, zusammen mit ZRH1 64 MW. Widerspruch vom Erstlauf "
        "aufgeloest: Firmenmeldung und DCD belegen die Eroeffnung im Sommer 2024. Die Meldung "
        "zu einer Eroeffnung im Sommer 2026 bezog sich auf eine weitere Ausbauetappe, "
        "Etappenplan pruefen. N+1-Redundanz, Abwaerme an Hotel und Seminarzentrum.")
aenderungen.append((
    "ZRH2 Glattfelden (Vantage)",
    "Widerspruch aufgeloest: Campus wurde im Sommer 2024 eroeffnet, Firmenmeldung und DCD "
    "stimmen ueberein. Phase von leer auf Betrieb gesetzt, die 2026er-Meldung betrifft eine "
    "weitere Ausbauetappe.",
    "https://www.datacenterdynamics.com/en/news/vantage-launches-second-data-center-in-switzerland/",
    "Fenster ist Betrieb, nicht Neubau: NEA-Testzyklus, Wartungsfenster, PQ-Audit. "
    "Etappenplan fuer weitere Gebaeude erfragen, dort ergibt sich das naechste Cx-Fenster."))

# --- ZUR01A Rafz: in Betrieb ------------------------------------------------
z = zeile_von("ZUR01A Rafz")
ws.cell(row=z, column=7, value="Betrieb")
ws.cell(row=z, column=13, value="Betrieb: Wartungsfenster, NEA-Tests, Bridging bei Umbauten")
ws.cell(row=z, column=20, value="https://www.stackinfra.com/locations/emea/zurich/zur01/ | https://www.datacenters.com/stack-infrastructure-zur01a-zurich")
ws.cell(row=z, column=21, value=STAND)
ws.cell(row=z, column=23, value="10 MW, Industriestrasse 16, 8197 Rafz. Anlage ist kommissioniert und in Betrieb, "
        "keine weitere vermietbare Leistung im Bau gemeldet. Hauptgebaeude mit Datenhalle, "
        "Buerogebaeude, separates Generatorgebaeude. Damit kein Neubaufenster mehr, "
        "sondern Betriebsgeschaeft.")
aenderungen.append((
    "ZUR01A Rafz (STACK)",
    "Status geklaert: Anlage ist kommissioniert und in Betrieb, keine zusaetzliche Leistung "
    "im Bau. Phase von leer auf Betrieb gesetzt.",
    "https://www.stackinfra.com/locations/emea/zurich/zur01/",
    "Aus der Neubau-Liste raus. Rafz laeuft als Betriebsgeschaeft zusammen mit Beringen "
    "ueber denselben Betreiber, ein Ansprechpartner fuer beide Standorte."))

# --- ZUR02 Beringen: Planer belegt ------------------------------------------
z = zeile_von("ZUR02 Beringen")
ws.cell(row=z, column=10, value="Amstein + Walthert (beteiligt, Rolle pruefen)")
ws.cell(row=z, column=20, value="https://www.datacenterdynamics.com/en/news/stack-tops-out-swiss-data-center-completes-construction-in-melbourne/ | https://amstein-walthert.ch/de/projekte/rechenzentrum-beringen-schaffhausen/ | https://algorithmwatch.ch/de/recherche-rechenzentren-schweiz/")
ws.cell(row=z, column=21, value=STAND)
alt_w = ws.cell(row=z, column=23).value or ""
ws.cell(row=z, column=23, value=alt_w.replace(
    "GU und Fachplaner nicht belegt.",
    "GU nicht belegt. Amstein + Walthert fuehrt das RZ Beringen als eigenes Projekt, "
    "genaue Rolle und Gewerk pruefen."))
aenderungen.append((
    "ZUR02 Beringen (STACK)",
    "Amstein + Walthert fuehrt das Rechenzentrum Beringen als Referenzprojekt auf der "
    "eigenen Projektseite. Rolle und Gewerk noch offen, als beteiligter Planer eingetragen.",
    "https://amstein-walthert.ch/de/projekte/rechenzentrum-beringen-schaffhausen/",
    "Erster belegter Planer-Einstieg ins groesste Cx-Volumen im Radar. A+W Zuerich auf das "
    "Projekt ansprechen, ein Planer oeffnet mehr als ein Betreiber."))

# --- ZUR3 Glattbrugg: Planer belegt -----------------------------------------
z = zeile_von("ZUR3 Glattbrugg")
ws.cell(row=z, column=10, value="Gruner (beteiligt, Rolle pruefen)")
ws.cell(row=z, column=20, value="https://www.netzwoche.ch/news/2026-06-03/so-praesentiert-sich-der-schweizer-markt-fuer-rechenzentren | https://www.grunerfriends.com/projects/data-center-zur3-zurich | https://www.ikon.ch/referenzprojekte/neubau-rechenzentrum-digital-realty-zuerich-zur3-vormals-interxion-zur3")
ws.cell(row=z, column=21, value=STAND)
alt_w = ws.cell(row=z, column=23).value or ""
ws.cell(row=z, column=23, value=alt_w + " Gruner nennt ZUR3 als Projekt im eigenen Portfolio, "
        "Rolle pruefen. Gleicher Planer-Kreis koennte beim ZUR4-Neubau wieder drin sein.")
aenderungen.append((
    "ZUR3 Glattbrugg (Digital Realty)",
    "Gruner nennt ZUR3 als eigenes Projekt. Als beteiligter Planer eingetragen, Rolle offen.",
    "https://www.grunerfriends.com/projects/data-center-zur3-zurich",
    "Wer ZUR3 geplant hat, sitzt womoeglich auch bei ZUR4 am Tisch. Gruner auf beide "
    "Campus-Bauten ansprechen, bevor das ZUR4-LV geschrieben ist."))

# --- Green Dielsdorf: Zaehlung praezisiert ----------------------------------
z = zeile_von("Metro-Campus Zuerich, weiteres Datacenter")
ws.cell(row=z, column=23, value="Zaehlung eingeordnet: Der Campus umfasst die Gebaeude M (Betrieb seit Anfang 2023) "
        "sowie N und O (im Bau). Das hier gemeldete weitere Datacenter waere das vierte "
        "Gebaeude. Baublatt zaehlt es als viertes, Netzwoche als drittes mit Baustart 2026 "
        "und 5800 m2, je nachdem ob N und O einzeln gezaehlt werden. Beide URLs in T. "
        "Kapazitaet, IBN, GU und Fachplaner nicht belegt. Green investiert laut "
        "Tages-Anzeiger insgesamt rund CHF 500 Mio in den Campus.")
ws.cell(row=z, column=20, value="https://www.baublatt.ch/bauprojekte/green-baut-viertes-rechenzentrum-auf-metro-campus-in-dielsdorf-zh-36395 | https://www.netzwoche.ch/news/2026-06-03/so-praesentiert-sich-der-schweizer-markt-fuer-rechenzentren | https://www.tagesanzeiger.ch/millionen-campus-in-dielsdorf-der-bau-von-zwei-weiteren-rechenzentren-hat-begonnen-440633753636")
ws.cell(row=z, column=21, value=STAND)
aenderungen.append((
    "Metro-Campus Dielsdorf, weiteres Datacenter (Green)",
    "Zaehlungs-Widerspruch eingeordnet: Campus ist M plus N plus O, das gemeldete neue "
    "Gebaeude waere das vierte. Die Quellen zaehlen unterschiedlich, weil N und O teils "
    "zusammengefasst werden.",
    "https://www.tagesanzeiger.ch/millionen-campus-in-dielsdorf-der-bau-von-zwei-weiteren-rechenzentren-hat-begonnen-440633753636",
    "Planungsphase bestaetigt. Fachplaner-Kanal, und zwar derselbe Zugang wie fuer N und O, "
    "ein Gespraech deckt drei Gebaeude ab."))

# --- Neue Zeile: Microsoft KI-Ausbau ----------------------------------------
neue_zeile = None
for zz in range(5, 46):
    if not ws.cell(row=zz, column=2).value:
        neue_zeile = zz
        break
assert neue_zeile is not None and neue_zeile <= 45, "Radar waechst ueber Zeile 45, Dashboard-Bereiche anpassen"

werte = {
    2: "KI-Infrastruktur-Ausbau Schweiz", 3: "Microsoft", 4: "pruefen", 5: "pruefen",
    6: "pruefen", 7: "Planung", 8: "pruefen",
    9: "pruefen", 10: "pruefen", 11: "Betreiber",
    12: "Lastbank und PQ bei Erweiterungen in den Partner-Rechenzentren, Bridging bei Kapazitaetsengpaessen",
    13: "frueh, zuerst klaeren in welchen Colocation-Standorten ausgebaut wird",
    14: "B",
    20: "https://www.datacenter-insider.de/microsoft-baut-ki-infrastruktur-in-der-schweiz-aus-a-60195c56e70961bf22a9eb82c859339b/ | https://news.microsoft.com/de-ch/2024/08/29/5-jahre-microsoft-rechenzentren-in-der-schweiz-500-lokale-services-50000-kunden/",
    21: STAND,
    22: "Klaeren, in welchen Colocation-Standorten der Ausbau physisch stattfindet",
    23: "Microsoft investiert 400 Mio US-Dollar in der Schweiz, Ausbau der Rechenzentren "
        "bei Zuerich und Genf fuer KI-Workloads. Vier bestehende Standorte, Switzerland North "
        "war zeitweise nur fuer Bestandskunden verfuegbar, also Kapazitaetsdruck. Microsoft "
        "baut in der Schweiz ueblicherweise in Partner-Rechenzentren, der physische Ausbau "
        "landet also vermutlich bei einem Colocation-Betreiber im Radar. Standorte pruefen.",
}
for spalte, wert in werte.items():
    ws.cell(row=neue_zeile, column=spalte, value=wert)
# Formeln und Formate stehen seit dem Erstaufbau bis Zeile 200 bereit,
# trotzdem pruefen wir sie hier explizit fuer die neue Zeile:
r_soll = f'=IF(Q{neue_zeile}="","",Q{neue_zeile}-TODAY())'
if ws.cell(row=neue_zeile, column=18).value != r_soll:
    ws.cell(row=neue_zeile, column=18, value=r_soll)
    ws.cell(row=neue_zeile, column=19,
            value=f'=IF(Q{neue_zeile}="","-",IF(Q{neue_zeile}<TODAY(),"UEBERFAELLIG",'
                  f'IF(Q{neue_zeile}-TODAY()<=7,"DIESE WOCHE","ok")))')
for spalte in (15, 16, 17, 22):
    ws.cell(row=neue_zeile, column=spalte).fill = gelb_fill
aenderungen.append((
    "KI-Infrastruktur-Ausbau Schweiz (Microsoft)",
    "Neu im Radar. 400 Mio US-Dollar Investition, Ausbau bei Zuerich und Genf fuer "
    "KI-Workloads, Kapazitaetsdruck in Switzerland North belegt.",
    "https://www.datacenter-insider.de/microsoft-baut-ki-infrastruktur-in-der-schweiz-aus-a-60195c56e70961bf22a9eb82c859339b/",
    "Der physische Ausbau landet vermutlich in Partner-Rechenzentren, die schon im Radar "
    "stehen. Wer die Colocation-Standorte kennt, weiss wo als naechstes Cx-Last anfaellt."))

# --- 03_Kontakte: Fachplaner-Firmen ergaenzen -------------------------------
kt = wb["03_Kontakte"]
fehlt_fill = PatternFill("solid", fgColor="FFF2CC")
naechste = kt.max_row + 1
for z in range(5, kt.max_row + 2):
    if not kt.cell(row=z, column=1).value:
        naechste = z
        break

fachplaner_neu = [
    ("Amstein + Walthert AG", "Fachplaner Elektro/Gebaeudetechnik",
     "ZUR02 Beringen (STACK Infrastructure)",
     "Fuehrt das RZ Beringen als eigenes Projekt, Rolle pruefen. Weitere DC-Referenzen: "
     "Raiffeisen St. Gallen (USV-Ersatz), ETH LEE, Accarda Bruettisellen. "
     "Quelle: amstein-walthert.ch/de/projekte/rechenzentrum-beringen-schaffhausen/"),
    ("Gruner AG", "Fachplaner/Engineering",
     "ZUR3 Glattbrugg (Digital Realty)",
     "Nennt ZUR3 im eigenen Portfolio, Rolle pruefen. Plant nach eigenen Angaben seit "
     "ueber 20 Jahren Datacenter, Referenz auch Suva Luzern RZ-Ersatz. "
     "Quelle: grunerfriends.com/projects/data-center-zur3-zurich"),
    ("HKG Engineering AG", "Fachplaner Elektro",
     "FEHLT",
     "DC-Referenz Post-RZ Ritex Zofingen. Sucht aktuell Datacenter-Projektleiter "
     "Elektroplanung, baut das Feld also aus. Noch keinem Radar-Projekt zugeordnet. "
     "Quelle: hkg.ch/referenzen/detail/rechenzentrum-ritex-gebaeude-zofingen/"),
    ("AFRY Schweiz", "Fachplaner/Engineering",
     "FEHLT",
     "Fuehrt ein Datacenter-Projekt Suisse romande als Referenz, Projekt und Rolle "
     "pruefen. Kandidat fuer den Romandie-Kanal, NorthC The Hive. "
     "Quelle: afry.com/fr-ch/projet/datacenter-suisse-romande"),
]
for i, (firma, rolle, ref, notiz) in enumerate(fachplaner_neu):
    z = naechste + i
    zeilenwerte = [firma, rolle, "FEHLT", "Fachplaner", ref, "FEHLT", "FEHLT",
                   "FEHLT", "Kalt", None, None, 0, notiz]
    for j, wert in enumerate(zeilenwerte, start=1):
        c = kt.cell(row=z, column=j, value=wert)
        c.font = text_font
        c.border = rahmen
        c.alignment = Alignment(vertical="top", wrap_text=j in (2, 5, 13))
        if wert == "FEHLT":
            c.fill = fehlt_fill
    kt.cell(row=z, column=10).number_format = "DD.MM.YYYY"
    kt.cell(row=z, column=11).number_format = "DD.MM.YYYY"
aenderungen.append((
    "03_Kontakte, Fachplaner-Kanal",
    "Vier Planerfirmen mit belegten DC-Referenzen ergaenzt: Amstein + Walthert (Beringen), "
    "Gruner (ZUR3), HKG (Ritex Zofingen, baut Datacenter-Team aus), AFRY (Suisse romande). "
    "Personennamen und Kontaktdaten stehen als FEHLT, nichts abgeleitet.",
    "https://amstein-walthert.ch/de/projekte/rechenzentrum-beringen-schaffhausen/",
    "Die groesste Luecke des Erstlaufs beginnt sich zu schliessen. Naechster Schritt: "
    "pro Firma den DC-Bereichsleiter ueber die Firmenwebsite identifizieren, nicht raten."))

# --- 06_Changelog -----------------------------------------------------------
cl = wb["06_Changelog"]
z = cl.max_row + 1
for zz in range(5, cl.max_row + 2):
    if not cl.cell(row=zz, column=3).value:
        z = zz
        break
for i, (projekt, was, url, konsequenz) in enumerate(aenderungen):
    zeile = z + i
    cl.cell(row=zeile, column=1, value=STAND)
    cl.cell(row=zeile, column=2, value="=WEEKNUM(DATE(2026,8,29),21)")
    cl.cell(row=zeile, column=3, value=projekt)
    cl.cell(row=zeile, column=4, value=was)
    cl.cell(row=zeile, column=5, value=url)
    cl.cell(row=zeile, column=6, value=konsequenz)
    for j in range(1, 7):
        c = cl.cell(row=zeile, column=j)
        c.font = text_font
        c.border = rahmen
        c.alignment = Alignment(vertical="top", wrap_text=j in (3, 4, 5, 6))
    cl.cell(row=zeile, column=2).alignment = Alignment(horizontal="center", vertical="top")

wb.save(DATEI)
print(f"{len(aenderungen)} Aenderungen geschrieben, neue Radar-Zeile {neue_zeile}.")
