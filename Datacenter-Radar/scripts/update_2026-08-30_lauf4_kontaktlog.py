#!/usr/bin/env python3
"""
Lauf 4 vom 30.08.2026, KW 35. Integration des Kontakt-Logs
MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx und drei neue Radar-Projekte
aus dem Aggreko-Tracker, oeffentlich verifiziert:

- GTR CH One, Hausen bei Brugg AG: 24 MW, Campus Reichhold (HIAG),
  Phase 1 2028, Betreiber Global Technical Realty (KKR)
- Vantage Volketswil: bis 70 MW ab Ende 2028, Waermeverbund mit
  Energie 360 fuer ueber 7000 Haushalte
- Kanton Wallis, Sierre: kantonales RZ mit Alarmzentralen, Quelle 2020,
  Stand pruefen

Dazu Wochenplan KW 36 als neues Blatt im Kontakt-Log (nie bestehende
Blaetter ueberschreiben) und Changelog-Eintraege.
"""

import glob
import os
import shutil
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
ORDNER = os.path.dirname(HERE)
RADAR = os.path.join(ORDNER, "MiT_Datacenter_Radar_CH_V1.0.xlsx")
KLOG = os.path.join(ORDNER, "MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx")
HEUTE = "2026-08-30"
STAND = "30.08.2026"
KW_FORMEL = "=WEEKNUM(DATE(2026,8,30),21)"

# Backups beider Dateien
for datei, stamm in ((RADAR, "MiT_Datacenter_Radar_CH_V1.0"),
                     (KLOG, "MiT_DC_Schweiz_Kontakte_Maerz2026")):
    b = os.path.join(ORDNER, f"{stamm}_backup_{HEUTE}.xlsx")
    if not os.path.exists(b):
        shutil.copy2(datei, b)
    alle = sorted(glob.glob(os.path.join(ORDNER, f"{stamm}_backup_*.xlsx")))
    for alt in alle[:-4]:
        os.remove(alt)
print("Backups angelegt.")

text_font = Font(name="Arial", size=10)
duenn = Side(style="thin", color="BFBFBF")
rahmen = Border(left=duenn, right=duenn, top=duenn, bottom=duenn)
gelb_fill = PatternFill("solid", fgColor="FFF2CC")

# ============================== RADAR =======================================
wb = load_workbook(RADAR)
ws = wb["02_Projekt_Radar"]

frei = []
for z in range(5, 46):
    if not ws.cell(row=z, column=2).value:
        frei.append(z)
assert len(frei) >= 3, "Radar waechst ueber Zeile 45, Dashboard-Bereiche anpassen"

neue = [
    dict(z=frei[0], b="GTR CH One, Campus Reichhold", c="Global Technical Realty",
         d="Hausen bei Brugg", e="AG", f=24, g="Planung", h="Phase 1: 2028",
         i="pruefen", j="pruefen", k="Betreiber",
         l="Baustrom und Trocknung ab Baustart, Lastbank und PQ im Cx, Abwaerme-Inbetriebnahme",
         m="jetzt Beziehungsaufbau, Baustart-Fenster beobachten", n="B",
         t="https://www.datacentermap.com/switzerland/zurich/gtr-ch-one/ | https://www.hiag.com/de/portfolio/arealportraits/hausenlupfig/ | https://sdca.ch/de/hiag-ist-neuer-partner-der-sdca/",
         u=STAND,
         v="Kontakte aus dem Log nutzen: HIAG Site Development und GTR Operations, Projektbezug als Vermutung",
         w="24 MW, dreigeschossig, erstes Schweizer Projekt von GTR (getragen von KKR), auf dem "
           "Campus Reichhold von HIAG zwischen Hausen und Lupfig, direkt neben dem Green-Campus "
           "ZRH1. Dachsolar und Abwaermenutzung fuer den ganzen Campus geplant. Aus dem "
           "Aggreko-Tracker uebernommen und oeffentlich verifiziert. GU und Planer nicht belegt."),
    dict(z=frei[1], b="Datacenter-Campus Volketswil", c="Vantage Data Centers",
         d="Volketswil", e="ZH", f=70, g="Planung", h="ab Ende 2028",
         i="pruefen", j="pruefen", k="Betreiber",
         l="Baustrom, Trocknung, spaeter grosses Cx-Volumen, Waermelast-Tests fuer den Verbund",
         m="Planungsphase, Planer- und GU-Vergabe beobachten, Tracker nennt IBN 2028", n="B",
         t="https://www.energie360.ch/de/unternehmen/medieninformationen/energie-360-plant-abwaermenutzung-in-volketswil/ | https://volketswiler-nachrichten.ch/artikel/news/abwraeme/",
         u=STAND,
         v="Vantage-Kontakte aus dem Log ansprechen, Projektbezug als Vermutung formulieren",
         w="Bis 70 MW geplant, Abwaerme soll ab Ende 2028 ueber Energie 360 mehr als 7000 "
           "Haushalte in Volketswil, Greifensee, Schwerzenbach und Effretikon versorgen, "
           "Energiezentrale ab Sommer 2025 gebaut. Groesster geplanter Einzelcampus im Radar. "
           "Aus dem Aggreko-Tracker (VOLKETSWIL GRASSROOT), oeffentlich verifiziert ueber "
           "die Energie-360-Partnerschaft. GU und Planer nicht belegt."),
    dict(z=frei[2], b="Kantonales Rechenzentrum Sierre", c="Kanton Wallis",
         d="Sierre", e="VS", f="pruefen", g="", h="pruefen",
         i="pruefen", j="Urbistondo + Martinez (Architektur), Structurame (Bauingenieur)", k="Ausschreibung",
         l="NEA-Tests und USV-Pruefung fuer Blaulicht-Infrastruktur, PQ-Audit",
         m="oeffentlicher Bauherr, Beschaffung ueber simap.ch beobachten", n="C",
         t="https://www.ictjournal.ch/news/2020-03-26/le-valais-veut-construire-un-deuxieme-datacenter-dans-le-meme-batiment-que-ses",
         u="26.03.2020",
         v="Aktuellen Projektstand ueber vs.ch und simap.ch klaeren, Ansprache auf Franzoesisch",
         w="Hochsicherheitsgebaeude mit den Alarmzentralen 112, 117, 118, 144, kantonaler "
           "Kommandozentrale und zweitem Kantons-RZ als Redundanz zu Sitten. Quelle von 2020, "
           "aktueller Stand unklar, deshalb Phase leer. Aus dem Aggreko-Tracker (SIERRE "
           "GRASSROOT, IBN 2026 laut Tracker). Blaulicht-Umfeld heisst harte "
           "Verfuegbarkeitsanforderungen, gutes NEA-Test-Profil."),
]

for p in neue:
    z = p["z"]
    for spalte, key in ((2, "b"), (3, "c"), (4, "d"), (5, "e"), (6, "f"), (7, "g"),
                        (8, "h"), (9, "i"), (10, "j"), (11, "k"), (12, "l"),
                        (13, "m"), (14, "n"), (20, "t"), (21, "u"), (22, "v"), (23, "w")):
        ws.cell(row=z, column=spalte, value=p[key])
    for spalte in (15, 16, 17, 22):
        ws.cell(row=z, column=spalte).fill = gelb_fill

# Changelog
cl = wb["06_Changelog"]
z = 5
while cl.cell(row=z, column=3).value:
    z += 1
eintraege = [
    ("GTR CH One, Hausen bei Brugg (Global Technical Realty)",
     "Neu im Radar, aus dem Aggreko-Tracker uebernommen und oeffentlich verifiziert: 24 MW "
     "auf dem Campus Reichhold von HIAG, Phase 1 2028, erstes Schweizer GTR-Projekt.",
     "https://www.datacentermap.com/switzerland/zurich/gtr-ch-one/",
     "Direkt neben dem Green-Campus ZRH1 Lupfig. Ein Gebietstermin deckt beide Campusse ab. "
     "Log-Kontakte bei HIAG und GTR vorhanden, Ansprache als Vermutung formulieren."),
    ("Datacenter-Campus Volketswil (Vantage)",
     "Neu im Radar, aus dem Tracker uebernommen und ueber die Energie-360-Partnerschaft "
     "verifiziert: bis 70 MW ab Ende 2028, Waermeverbund fuer ueber 7000 Haushalte.",
     "https://www.energie360.ch/de/unternehmen/medieninformationen/energie-360-plant-abwaermenutzung-in-volketswil/",
     "Groesster geplanter Campus im Radar. Twei Vantage-Log-Kontakte auf Development-Ebene "
     "vorhanden. Wer jetzt Beziehung aufbaut, sitzt beim 70-MW-Cx am Tisch."),
    ("Kantonales Rechenzentrum Sierre (Kanton Wallis)",
     "Neu im Radar aus dem Tracker, oeffentliche Quelle von 2020: Hochsicherheitsgebaeude "
     "mit Alarmzentralen und zweitem Kantons-RZ. Architektur Urbistondo + Martinez.",
     "https://www.ictjournal.ch/news/2020-03-26/le-valais-veut-construire-un-deuxieme-datacenter-dans-le-meme-batiment-que-ses",
     "Stand veraltet, ueber simap.ch und vs.ch klaeren. Blaulicht-Profil passt zu NEA-Test "
     "und PQ-Audit, Vergabe laeuft oeffentlich."),
    ("Kontakt-Log integriert",
     "MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx liegt jetzt im Projektordner und wird bei "
     "jedem Lauf mitgepflegt. 24 priorisierte Log-Kontakte, 145 CH-Kontakte. Befund "
     "Datenqualitaet: in mehreren Zeilen sind Name, Firma und E-Mail gegeneinander "
     "verschoben, klassischer Tracker-Versatz.",
     "",
     "Wochenplan KW 36 als neues Blatt im Kontakt-Log erstellt, fuenf Kontakte pro Tag. "
     "Vor jedem Mailversand Name gegen Mail-Adresse pruefen, die geflaggten Zeilen "
     "zuerst telefonisch verifizieren."),
]
for i, (projekt, was, url, konsequenz) in enumerate(eintraege):
    zeile = z + i
    cl.cell(row=zeile, column=1, value=STAND)
    cl.cell(row=zeile, column=2, value=KW_FORMEL)
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

wb.save(RADAR)
print(f"Radar: 3 neue Projekte (Zeilen {frei[0]} bis {frei[2]}), {len(eintraege)} Changelog-Zeilen.")

# ============================== WOCHENPLAN ==================================
wk = load_workbook(KLOG)
BLATT = "Wochenplan_KW36"
if BLATT in wk.sheetnames:
    del wk[BLATT]
ws = wk.create_sheet(BLATT)

NAVY, ORANGE, GELB, WEISS = "1F3A5F", "E8740C", "FFF2CC", "FFFFFF"
kopf_font = Font(name="Arial", size=10, bold=True, color=WEISS)
kopf_fill = PatternFill("solid", fgColor=NAVY)
tag_font = Font(name="Arial", size=11, bold=True, color=ORANGE)
warn_fill = PatternFill("solid", fgColor=GELB)

ws["A1"] = "Wochenplan KW 36, 31.08. bis 04.09.2026"
ws["A1"].font = Font(name="Arial", size=14, bold=True, color=NAVY)
ws["A2"] = ("Fuenf Kontakte pro Tag. Reihenfolge innerhalb des Tages ist die Anrufreihenfolge. "
            "DATENQUALITAET PRUEFEN heisst: im Log sind Name, Firma oder E-Mail gegeneinander "
            "verschoben, vor einem Mailversand zuerst telefonisch verifizieren. "
            "Projektbezug immer als Vermutung formulieren.")
ws["A2"].font = Font(name="Arial", size=9, italic=True, color="666666")
ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
ws.row_dimensions[2].height = 40

kopf = ["Slot", "Name", "Firma", "Rolle laut Log", "Projekt (Vermutung)", "Telefon",
        "Kanal", "Ziel des Kontakts", "Hinweis"]
breiten = [6, 22, 26, 26, 30, 22, 10, 44, 44]
for i, (k, br) in enumerate(zip(kopf, breiten), start=1):
    from openpyxl.utils import get_column_letter
    ws.column_dimensions[get_column_letter(i)].width = br

plan = [
    ("MONTAG 31.08. — Der Multiplikator-Tag: Laufenburg-Planerteam und Green", [
        ("Stefan Walser", "Amstein + Walthert", "Consultant Engineer",
         "FlexBase TZL Laufenburg", "+41 44 305 91 11", "Telefon",
         "Der wichtigste Anruf der Woche. A+W ist belegt an Laufenburg UND Beringen. "
         "Einstieg ueber PQ-Messung Klasse A im Cx, Ziel: Termin.", ""),
        ("Marc Schmid", "ERNE", "Construction Manager",
         "FlexBase TZL Laufenburg", "+41 62 869 43 00", "Telefon",
         "Baustrom und Trocknung fuer 20000 m2 Baufeld, Tiefbau laeuft bereits. "
         "Vorlaufzeit Trocknung rund fuenf Monate nennen.", ""),
        ("Christian Frei", "Frei Architekten", "General Manager",
         "FlexBase TZL Laufenburg", "+41 62 834 90 50", "Telefon",
         "Dritter Laufenburg-Zugang am selben Tag. Frage nach dem Cx-Verantwortlichen "
         "im Planerteam.", ""),
        ("Ivan Hojevac", "Green", "Construction Manager",
         "Green DC4 Lupfig, 12 MW", "+41 56 460 23 80", "Telefon",
         "IBN Anfang 2027, Fit-out minus sechs Monate ist jetzt. Lastbank und "
         "Heat-Load-Test ansprechen, bevor das Cx-Paket im MEP-Vertrag steckt.",
         "Mail im Log: ivan.holjevac@green.ch, Schreibweise Name/Mail differiert, pruefen"),
        ("Martin Sita", "MBA Projektmanagement", "Planer / Engineering",
         "Green Metro-Campus Dielsdorf", "+41 44 515 45 45", "Telefon",
         "MBA plant Dielsdorf, Beringen und ETH HRZ. Ziel: der richtige "
         "DC-Verantwortliche bei MBA, dann Termin.",
         "Log-Mail ist nur info@mbap.ch, Person am Telefon verifizieren"),
    ]),
    ("DIENSTAG 01.09. — Implenia-Tag und Beringen", [
        ("Adrian Eberle", "Implenia Generalunternehmung", "Projektteam Dielsdorf",
         "Green Metro-Campus Dielsdorf", "+41 58 474 74 74", "Telefon",
         "Implenia haelt drei Radar-Baustellen: Lupfig, Dielsdorf, Beringen. "
         "Ziel: Bereichsverantwortlicher Datacenter.",
         "DATENQUALITAET PRUEFEN: Log-Mail lautet Susanne.jobe@implenia.ch"),
        ("Zentrale erfragen", "Implenia, Projekt ZUR02", "Bauleitung Beringen",
         "STACK ZUR02 Beringen, 36 MW", "+41 58 474 76 00", "Telefon",
         "Groesstes Cx-Volumen im Radar, IBN Herbst 2026. Nach der Bauleitung "
         "Beringen fragen, Cx-Paket und Lastbank ansprechen.",
         "Log-Zeile Markus Meier traegt fremde Mail (atrian.wyss@implenia.ch), erst verifizieren"),
        ("Michael Berchtold", "Schmidli AG", "Construction Manager",
         "STACK Beringen Brownfield", "+41 43 422 33 50", "Telefon",
         "Zweiter Beringen-Zugang ueber die Baustelle. Baustrom- und "
         "Wartungsfenster-Themen direkt vor Ort.", ""),
        ("Jennifer Zeltner", "Confirm AG", "Division Manager",
         "Vantage Winterthur ZRH1", "+41 44 269 61 90", "Telefon",
         "Vantage-Campus im Etappenausbau. Frage nach dem Cx-Fenster der "
         "naechsten Gebaeude.", ""),
        ("Silvio Schwarz", "MBA Projektmanagement", "Project Manager",
         "Green Metro-Campus Dielsdorf", "+41 44 515 45 45", "Telefon",
         "Zweiter MBA-Faden, falls Montag ohne Termin endete.",
         "DATENQUALITAET PRUEFEN: Log fuehrt ihn doppelt (MBA und Neukom Marzolo) mit fremden Mails"),
    ]),
    ("MITTWOCH 02.09. — Betreiber-Bauseite: die neuen Tracker-Projekte", [
        ("Alex Roemer", "HIAG Immobilien", "Site Development Manager",
         "GTR CH One, Campus Reichhold Hausen", "+41 61 606 55 00", "Telefon",
         "Arealentwickler des 24-MW-Projekts neben dem Green-Campus. Baustrom "
         "und Bauheizung fuer den ganzen Campus Reichhold ansprechen.", ""),
        ("Neil Grocock", "Global Technical Realty", "Director of Operations",
         "GTR CH One Hausen, 24 MW", "pruefen", "E-Mail",
         "Betreiberseite desselben Projekts, englisch ansprechen, Aggreko in "
         "der ersten Zeile.",
         "Log-Telefonnummer +34 442039355695 ist unplausibel (Laendercode), nur Mail nutzen"),
        ("Edwin Van Velzen", "Vantage Data Centers", "VP Development",
         "Campus Volketswil, bis 70 MW", "+44 1633 988021", "Telefon",
         "Groesster geplanter Campus im Radar. Englisch, Development-Ebene, "
         "Ziel: wer verantwortet Commissioning-Planung.", ""),
        ("Robert Holmans", "Vantage Data Centers", "Site Development Manager",
         "Campus Volketswil", "+44 1633 988021", "E-Mail",
         "Zweiter Volketswil-Faden, nicht am selben Tag anrufen wie Van Velzen, "
         "deshalb Mail mit Anruftermin fuer Donnerstag.", ""),
        ("Gregor Luethi", "Burkhalter Technics", "Project Manager",
         "Green Metro-Campus (Elektro)", "+41 44 432 11 11", "Telefon",
         "Einziger Elektro-Unternehmer im Log. Guenstigster Kontakt ueberhaupt, "
         "preist das Cx-Paket oft selbst ein.",
         "DATENQUALITAET PRUEFEN: Log-Mail gehoert Paolino Bossio, am Telefon verifizieren"),
    ]),
    ("DONNERSTAG 03.09. — Romandie-Tag, auf Franzoesisch", [
        ("Martin Diaz", "CCHE Architecture", "Head of Transformation",
         "NorthC Geneva Brownfield", "+41 21 321 44 66", "Telefon",
         "Planer-Zugang zur Romandie. Vous-Form, PQ-Messung und Lastbank fuer "
         "den Genfer NorthC-Ausbau.", ""),
        ("David Martinez Grande", "Architekturbuero (Sierre)", "Project Architect",
         "Kantonales RZ Sierre", "+41 21 218 56 34", "Telefon",
         "Blaulicht-RZ des Kantons Wallis. NEA-Test und USV-Pruefung als Thema, "
         "Beschaffung laeuft oeffentlich.",
         "Firma im Log FEHLT, vermutlich Urbistondo + Martinez, verifizieren"),
        ("Zentrale erfragen", "NorthC Schweiz", "Projektleitung The Hive / Arlesheim",
         "The Hive Genf und UptownBasel", "pruefen", "Telefon",
         "Zwei NorthC-Projekte im Bau oder in Bewilligung. Nach dem "
         "Projektverantwortlichen Schweiz fragen.", ""),
        ("Luigi Pulieri", "Roth Gruppe", "Project Manager",
         "Green Metro-Campus", "+41 44 880 77 88", "Telefon",
         "Gewerk-Zugang Dielsdorf.",
         "DATENQUALITAET PRUEFEN: Log-Mail gehoert Agron Berisha"),
        ("Remo Vollenweider", "Baltensperger AG", "GU / Bauunternehmung",
         "Green Metro-Campus", "+41 44 872 76 76", "Telefon",
         "Weiterer Bau-Zugang Dielsdorf, Baustrom und Trocknung.",
         "DATENQUALITAET PRUEFEN: Log fuehrt ihn doppelt (auch Implenia), nur Zentrale-Mail"),
    ]),
    ("FREITAG 04.09. — Nachfassen und die Firmen ohne Log-Person", [
        ("Nachfassen Montag", "A+W, ERNE, Frei, Green, MBA", "",
         "Laufenburg, Lupfig, Dielsdorf", "", "E-Mail",
         "Wer Montag nicht erreicht wurde, bekommt heute die Mail mit konkretem "
         "Anruftermin fuer Montag KW 37.", ""),
        ("Zentrale erfragen", "IKON Ingenieure", "Planung ZUR2 und ZUR3",
         "Digital Realty ZUR4 (Kandidat)", "pruefen", "Telefon",
         "Wer ZUR2 und ZUR3 geplant hat, ist der naheliegende ZUR4-Planer. "
         "Nach dem DC-Bereichsleiter fragen.", "Nummer ueber ikon.ch holen"),
        ("Zentrale erfragen", "HRS Real Estate", "GU Vantage ZRH2, Equinix ZH5.4",
         "Vantage / Equinix Ausbauten", "pruefen", "Telefon",
         "GU fuer zwei Betreiber. Nach dem Bereich Datacenter fragen, "
         "Umschalt- und Bridging-Themen.", "Nummer ueber hrs.ch holen"),
        ("Zentrale erfragen", "Drees & Sommer Schweiz", "PM ZUR3",
         "Digital Realty Campus Glattbrugg", "pruefen", "Telefon",
         "Projektsteuerung des Campus, zweiter ZUR4-Faden.", "Nummer ueber dreso.com holen"),
        ("Wochenabschluss", "Kontakt-Log", "", "", "", "Log",
         "Alle Kontakte der Woche ins Log eintragen, Wiedervorlagen setzen, "
         "dann aktualisiere in Claude Code fuer den Wochenplan KW 37.", ""),
    ]),
]

zeile = 4
for tag, slots in plan:
    ws.cell(row=zeile, column=1, value=tag).font = tag_font
    zeile += 1
    for i, k in enumerate(kopf, start=1):
        c = ws.cell(row=zeile, column=i, value=k)
        c.font = kopf_font
        c.fill = kopf_fill
        c.border = rahmen
    zeile += 1
    for nr, (name, firma, rolle, projekt, tel, kanal, ziel, hinweis) in enumerate(slots, 1):
        werte = [nr, name, firma, rolle, projekt, tel, kanal, ziel, hinweis]
        for j, wert in enumerate(werte, start=1):
            c = ws.cell(row=zeile, column=j, value=wert)
            c.font = text_font
            c.border = rahmen
            c.alignment = Alignment(vertical="top", wrap_text=j in (4, 5, 8, 9))
        if hinweis:
            ws.cell(row=zeile, column=9).fill = warn_fill
        ws.row_dimensions[zeile].height = 44
        zeile += 1
    zeile += 1

fuss = ws.cell(row=zeile + 1, column=1,
               value="Gates: Owen-Gate und CHF-Sperre gelten in jedem Gespraech. Keine "
                     "Verfuegbarkeitszusagen, keine Preise. PQ-Position Klasse A ist "
                     "Standardposition. Vor Kontakt zu Kunden, die bei einem Kollegen "
                     "laufen, intern abstimmen.")
fuss.font = Font(name="Arial", size=9, italic=True, color="B3372B")
fuss.alignment = Alignment(wrap_text=True, vertical="top")

wk.save(KLOG)
print(f"Wochenplan KW 36 als Blatt '{BLATT}' geschrieben, 5 Tage x 5 Slots.")
