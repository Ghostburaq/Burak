#!/usr/bin/env python3
"""
Lauf 3 vom 30.08.2026, KW 35. Partner-Recherche: GU, Planer, Architekten,
Projektsteuerer je Radar-Projekt, nur belegte Zuordnungen.

Kernbefunde:
- Implenia baut auch STACK ZUR02 Beringen (Core and Shell), IBN Herbst 2026
- HRS: GU fuer Vantage ZRH2 und fuer die Equinix-Erweiterung ZH5.4
- IKON Ingenieure: Planung ZUR2 und ZUR3, ZUR3 mit 24 MW IT im Endausbau
- Drees & Sommer: Projektmanagement ZUR3
- MBA Projektmanagement: Green Metro-Campus, ZUR02 Beringen, ETH HRZ, SCS ZH-Herdern
- FlexBase TZL: Planerteam Frei Architekten, Amstein + Walthert, Schnetzer
  Puskas, Koch + Partner; Equans und Georg Fischer fuer die Batterie-Integration
- NorthC UptownBasel: Standort Arlesheim BL, 2500 m2, 6 MVA, IBN Mitte 2027
- ETH HRZ: Generalplaner-Team mit Architekt Penzel Valier

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
HEUTE = "2026-08-30"
STAND = "30.08.2026"
KW_FORMEL = "=WEEKNUM(DATE(2026,8,30),21)"

backup = os.path.join(ORDNER, f"MiT_Datacenter_Radar_CH_V1.0_backup_{HEUTE}.xlsx")
shutil.copy2(DATEI, backup)
backups = sorted(glob.glob(os.path.join(ORDNER, "MiT_Datacenter_Radar_CH_V1.0_backup_*.xlsx")))
for alt in backups[:-4]:
    os.remove(alt)
print(f"Backup: {os.path.basename(backup)}")

wb = load_workbook(DATEI)
ws = wb["02_Projekt_Radar"]

text_font = Font(name="Arial", size=10)
duenn = Side(style="thin", color="BFBFBF")
rahmen = Border(left=duenn, right=duenn, top=duenn, bottom=duenn)


def zeile_von(name):
    for z in range(5, 46):
        if ws.cell(row=z, column=2).value == name:
            return z
    raise KeyError(name)


def setze(z, spalte, wert):
    ws.cell(row=z, column=spalte, value=wert)


aend = []

# --- ZUR02 Beringen: Implenia als GU, MBA als Gesamtleitung -----------------
z = zeile_von("ZUR02 Beringen")
setze(z, 9, "Implenia (Core and Shell)")
setze(z, 8, "Herbst 2026")
setze(z, 20, "https://implenia.com/medien/artikel/implenia-gewinnt-attraktive-hochbau-auftraege-in-der-schweiz-und-in-deutschland/ | https://amstein-walthert.ch/de/projekte/rechenzentrum-beringen-schaffhausen/ | https://mbap.ch/de/referenzen/datacenter-zur2,-beringen/ | https://www.datacenterdynamics.com/en/news/stack-tops-out-swiss-data-center-completes-construction-in-melbourne/")
setze(z, 21, STAND)
setze(z, 23, "36 MW, Areal des ehemaligen SIG-Tennisclubs. GU ist Implenia, Core and Shell, "
      "achtes Datacenter von Implenia in der Schweiz seit 2020. IBN laut Implenia Herbst 2026. "
      "MBA Projektmanagement fuehrt ZUR02 als Referenz: Hauptgebaeude, Buerogebaeude, mehrere "
      "Kuehlanlagen, zwei Generatorgebaeude mit Tankraeumen, Rolle pruefen. Amstein + Walthert "
      "beteiligt, Rolle pruefen. Kanton baut neues Unterwerk, finanziert vom Betreiber, "
      "Netzanschluss-Termin ist der Hebel fuer Bridging Power.")
aend.append((
    "ZUR02 Beringen (STACK)",
    "GU belegt: Implenia baut ZUR02 als Core and Shell, IBN Herbst 2026 laut Implenia. "
    "MBA Projektmanagement fuehrt das Projekt ebenfalls als Referenz, inklusive "
    "Generatorgebaeude und Kuehlanlagen.",
    "https://implenia.com/medien/artikel/implenia-gewinnt-attraktive-hochbau-auftraege-in-der-schweiz-und-in-deutschland/",
    "Implenia haelt damit drei Radar-Projekte gleichzeitig: Lupfig, Dielsdorf und Beringen. "
    "Ein Implenia-Kontakt auf Bereichsebene Datacenter oeffnet alle drei Baustellen."))

# --- TZL Laufenburg: Planerteam belegt --------------------------------------
z = zeile_von("Technologiezentrum Laufenburg (TZL)")
setze(z, 10, "Amstein + Walthert (im Planerteam)")
setze(z, 20, "https://www.erne-gruppe.ch/de/news/newsdetail/ernenews/medienmitteilung-flexbase/ | https://flexbase.ch/en/project-overview | https://www.frei-architekten.ch/projekte/technologiezentrum-flexbase-2 | https://www.datacenter-insider.de/flexbase-errichtet-technologiezentrum-mit-480-mw-ki-rechenzentrum-a-befea6134cb5045aba28a650a2ef6206/")
setze(z, 21, STAND)
setze(z, 23, "Baufreigabe erteilt, ERNE ist GU in strategischer Partnerschaft mit FlexBase. "
      "Planerteam laut FlexBase-Projektuebersicht: Frei Architekten, Amstein + Walthert, "
      "Schnetzer Puskas (Tragwerk), Koch + Partner. Equans Schweiz und Georg Fischer planen "
      "die Integration der Megabatterie und den Netzanschluss. KI-Rechenzentrum bis 480 MW "
      "Rechenleistung auf rund 12000 m2 IT-Netzflaeche, Redox-Flow-Speicher ueber 1.6 GWh, "
      "direkt beim Unterwerk Stern von Laufenburg. 480 MW ist Rechenleistung laut Quelle, "
      "nicht als elektrische Anschlussleistung uebernehmen. IBN Sommer 2028.")
aend.append((
    "Technologiezentrum Laufenburg (FlexBase)",
    "Planerteam belegt: Frei Architekten, Amstein + Walthert, Schnetzer Puskas, Koch + "
    "Partner. Equans und Georg Fischer fuer Batterie-Integration und Netzanschluss.",
    "https://flexbase.ch/en/project-overview",
    "Amstein + Walthert sitzt jetzt belegt an zwei Radar-Projekten, Beringen und Laufenburg. "
    "Das A+W-Gespraech deckt beide ab und ist damit der wertvollste Planertermin im Radar."))

# --- Metro-Campus Dielsdorf N und O: Campus-Planerteam ----------------------
z = zeile_von("Metro-Campus Zuerich, Datacenter N und O")
setze(z, 20, "https://www.presseportal.de/pm/152183/5635701 | https://mbap.ch/de/referenzen/metro-campus-zurich/ | https://www.einsarchitekten.ch/projekte/metro-campus-green | https://www.emchberger.ch/de/neubau-metro-campus-zuerich-dielsdorf-digitalisierung-zwischen-energieeffizienz-und-nachhaltigkeit?division=76")
setze(z, 21, STAND)
setze(z, 23, "Zwei Gebaeude, zusammen 35 MW, rund 4000 Racks auf 11600 m2, Campus 46000 m2. "
      "GU Implenia. Campus-Planung: MBA Projektmanagement als Generalplaner fuer drei "
      "Datacenter und drei Buerogebaeude, Eins Architekten als Architekturpartner, "
      "Emch+Berger beteiligt laut eigener Referenz, Rollen im Detail pruefen. Vollausbau "
      "laut Architekt: 27 USV-Anlagen, 24 Kaeltemaschinen, 33 MW Kaelteleistung, 15000 m2 "
      "Whitespace. Abwaermenutzung durch Energie 360. IBN-Termin und Fachplaner Elektro "
      "nicht belegt.")
aend.append((
    "Metro-Campus Dielsdorf N und O (Green)",
    "Campus-Planerteam belegt: MBA Projektmanagement als Generalplaner, Eins Architekten, "
    "Emch+Berger. Vollausbau 27 USV, 24 Kaeltemaschinen, 33 MW Kaelte, 15000 m2 Whitespace.",
    "https://mbap.ch/de/referenzen/metro-campus-zurich/",
    "33 MW Kaelteleistung heisst grosse Heat-Load-Tests im Cx. MBA plant den ganzen Campus, "
    "ein Termin dort deckt N, O und das kommende vierte Gebaeude ab."))

# --- Green weiteres Datacenter Dielsdorf: gleiche Partner -------------------
z = zeile_von("Metro-Campus Zuerich, weiteres Datacenter")
alt = ws.cell(row=z, column=23).value or ""
setze(z, 23, alt + " Campus-Planerteam wie N und O: MBA Projektmanagement, Eins Architekten, "
      "Emch+Berger, siehe deren Referenzseiten.")
setze(z, 21, STAND)

# --- ZRH2 Glattfelden: HRS als GU -------------------------------------------
z = zeile_von("ZRH2 Glattfelden")
setze(z, 9, "HRS (GU laut Fachpresse)")
setze(z, 20, "https://vantage-dc.com/news/vantage-data-centers-expands-emea-portfolio-with-second-zurich-campus-fueled-by-more-than-chf-370-million-investment/ | https://www.immobilienbusiness.ch/en/regionen/2024-04-24/glattfelden-neuer-datencenter-campus-auf-zwei-hektaren/ | https://www.datacenterdynamics.com/en/news/vantage-launches-second-data-center-in-switzerland/")
setze(z, 21, STAND)
alt = ws.cell(row=z, column=23).value or ""
setze(z, 23, alt + " GU des Baus war HRS laut Immobilien Business.")
aend.append((
    "ZRH2 Glattfelden (Vantage)",
    "GU nachgetragen: HRS hat den Campus gebaut, Quelle Immobilien Business.",
    "https://www.immobilienbusiness.ch/en/regionen/2024-04-24/glattfelden-neuer-datencenter-campus-auf-zwei-hektaren/",
    "HRS baut fuer Vantage und fuer Equinix. Zweiter GU-Multiplikator neben Implenia, "
    "Kontakt auf HRS-Bereichsebene Datacenter suchen."))

# --- Equinix ZH4: HRS-Referenz ZH5.4 ----------------------------------------
z = zeile_von("ZH4 Zuerich, sechste Ausbauphase")
setze(z, 20, "https://www.inside-it.ch/equinix-baut-data-center-in-zuerich-aus-20241112 | https://www.hrs.ch/de/projekte/equinix-rechenzentren | https://www.netzwoche.ch/news/2024-11-13/equinix-baut-zuercher-rechenzentrum-aus")
setze(z, 21, STAND)
alt = ws.cell(row=z, column=23).value or ""
setze(z, 23, alt + " HRS war GU der Equinix-Erweiterung ZH5.4 in Oberengstringen, Bauzeit "
      "Dezember 2020 bis Februar 2022, rund CHF 23 Mio, Architekt Itten + Brechbuehl. "
      "Kandidat auch fuer den ZH4-Ausbau, pruefen.")
aend.append((
    "ZH4 Zuerich (Equinix)",
    "HRS als bisheriger Equinix-GU belegt: Erweiterung ZH5.4 Oberengstringen, CHF 23 Mio, "
    "Architekt Itten + Brechbuehl. GU des laufenden ZH4-Ausbaus weiter offen.",
    "https://www.hrs.ch/de/projekte/equinix-rechenzentren",
    "Wer den ZH4-Ausbau baut, vergibt auch die temporaere Versorgung waehrend der "
    "Umschaltungen. HRS zuerst fragen, die kennen beide Betreiber."))

# --- ZUR3 Glattbrugg: IKON, Drees & Sommer, 24 MW ---------------------------
z = zeile_von("ZUR3 Glattbrugg")
setze(z, 6, 24)
setze(z, 10, "IKON Ingenieure (alle Phasen)")
setze(z, 20, "https://www.ikon.ch/referenzprojekte/neubau-rechenzentrum-digital-realty-zuerich-zur3-vormals-interxion-zur3 | https://www.dreso.com/ch/projekte/details/datacenter-zur3-zuerich-campus-interxion | https://www.netzwoche.ch/news/2026-06-03/so-praesentiert-sich-der-schweizer-markt-fuer-rechenzentren")
setze(z, 21, STAND)
setze(z, 23, "Groesstes RZ der Schweiz nach Flaeche, 11400 m2 Whitespace, 24 MW IT-Last im "
      "Endausbau laut IKON, gebaut in drei Etappen, schwieriger Baugrund mit Grundwasser "
      "bis Terrain. IKON Ingenieure planten alle Phasen bis Bauleitung, auch schon ZUR2. "
      "Drees & Sommer fuehrte das Projektmanagement. Liegt auf demselben Campus wie der "
      "ZUR4-Neubau, derselbe Planerkreis ist dort der naheliegende Kandidat.")
aend.append((
    "ZUR3 Glattbrugg (Digital Realty)",
    "Planer belegt: IKON Ingenieure alle Phasen (auch ZUR2), Drees & Sommer "
    "Projektmanagement. Kapazitaet belegt: 24 MW IT im Endausbau laut IKON.",
    "https://www.ikon.ch/referenzprojekte/neubau-rechenzentrum-digital-realty-zuerich-zur3-vormals-interxion-zur3",
    "IKON kennt den Campus Glattbrugg aus zwei Neubauten. Fuer den ZUR4-Cx ist IKON der "
    "direkteste Planer-Zugang, vor dem LV ansprechen."))

# --- ZUR4 Glattbrugg: Kandidaten-Hinweis ------------------------------------
z = zeile_von("ZUR4 Glattbrugg")
alt = ws.cell(row=z, column=23).value or ""
setze(z, 23, alt + " Planerkreis der Vorgaengerbauten ZUR2 und ZUR3: IKON Ingenieure und "
      "Drees & Sommer, Kandidaten fuer ZUR4, nicht belegt.")
setze(z, 21, STAND)

# --- UptownBasel: Standort und Termin belegt --------------------------------
z = zeile_von("UptownBasel Campus")
setze(z, 4, "Arlesheim")
setze(z, 5, "BL")
setze(z, 7, "Bewilligung")
setze(z, 8, "Mitte 2027")
setze(z, 11, "Fachplaner")
setze(z, 13, "Bewilligungsphase, Planer- und Baustrom-Fenster oeffnet mit der Baufreigabe")
setze(z, 20, "https://www.itreseller.ch/Artikel/103958/NorthC_baut_Rechenzentrum_auf_dem_Campus_UptownBasel.html | https://netzpalaver.de/2025/09/11/northc-baut-auf-dem-campus-uptownbasel-das-rechenzentrum-der-zukunft/ | https://www.netzwoche.ch/news/2026-06-03/so-praesentiert-sich-der-schweizer-markt-fuer-rechenzentren")
setze(z, 21, STAND)
setze(z, 23, "Erste Etappe 2500 m2 auf dem Innovationscampus UptownBasel in Arlesheim BL, "
      "Anschluss 6 MVA, rund 5.5 MW nutzbare Leistung, davon 4.5 MW IT laut Netzwoche, "
      "kVA und kW hier sauber auseinanderhalten. Bauzeit rund 18 Monate ab Baubewilligung, "
      "Betrieb ab Mitte 2027, Notstrom mit HVO-Diesel, Abwaerme ins regionale Waermenetz. "
      "Erweitert die NorthC-Standorte Muenchenstein 1 und 2. GU und Fachplaner nicht belegt.")
aend.append((
    "UptownBasel Campus (NorthC)",
    "Standort und Termin belegt: Arlesheim BL, erste Etappe 2500 m2, 6 MVA Anschluss, "
    "rund 5.5 MW nutzbar, Bauzeit 18 Monate ab Bewilligung, Betrieb Mitte 2027. "
    "Phase auf Bewilligung gesetzt.",
    "https://netzpalaver.de/2025/09/11/northc-baut-auf-dem-campus-uptownbasel-das-rechenzentrum-der-zukunft/",
    "Betrieb Mitte 2027 heisst Cx Anfang 2027, das Fenster fuer den Planer-Einstieg ist "
    "jetzt. HVO-Notstrom passt exakt zum MiT-Portfolio, Stage V und HVO."))

# --- ETH HRZ: Generalplaner-Team --------------------------------------------
z = zeile_von("Rechenzentrum Hoenggerberg (HRZ)")
setze(z, 20, "https://www.inside-it.ch/bald-ist-baubeginn-fuer-das-49-millionen-rechenzentrum-der-eth-zuerich-20230908 | https://ethz.ch/en/campus/development/construction-projects/hrz-projekt.html | https://mbap.ch/de/referenzen/hrz-eth-zuerich/")
setze(z, 21, STAND)
setze(z, 23, "Fuenfgeschossig, ueber 4000 m2, Baukosten rund CHF 49 Mio, Spatenstich April "
      "2024, IT-Betrieb ab Anfang 2026 geplant. Generalplaner-Team ueber offenes "
      "GATT/WTO-Verfahren, Architektur Penzel Valier. MBA Projektmanagement fuehrt HRZ als "
      "eigene Referenz, Rolle pruefen. Oeffentlicher Bauherr, Beschaffung ueber simap.ch, "
      "aktueller Baustand verifizieren.")
aend.append((
    "Rechenzentrum Hoenggerberg (ETH)",
    "Planerseite belegt: Generalplaner-Team aus offenem Verfahren, Architektur Penzel "
    "Valier, MBA Projektmanagement mit HRZ-Referenz.",
    "https://ethz.ch/en/campus/development/construction-projects/hrz-projekt.html",
    "MBA taucht damit beim dritten Radar-Projekt auf, Dielsdorf, Beringen und ETH. "
    "MBA ist der still meistvernetzte Player im Schweizer DC-Bau."))

# --- 03_Kontakte: Partnerfirmen ---------------------------------------------
kt = wb["03_Kontakte"]
fehlt_fill = PatternFill("solid", fgColor="FFF2CC")

start = 5
while kt.cell(row=start, column=1).value:
    start += 1

partner = [
    ("Implenia AG", "GU/TU Datacenter (Bereich Buildings)", "GU/TU",
     "Lupfig DC4, Dielsdorf N+O, ZUR02 Beringen (alle im Radar)",
     "Drei laufende Radar-Projekte gleichzeitig, achtes Schweizer DC seit 2020. "
     "Der wichtigste GU-Kontakt im Radar. Quelle: implenia.com Medienmitteilungen."),
    ("HRS Real Estate AG", "GU/TU Datacenter", "GU/TU",
     "ZRH2 Glattfelden (Vantage), Equinix ZH5.4 Oberengstringen",
     "GU fuer Vantage ZRH2 und die Equinix-Erweiterung ZH5.4 (CHF 23 Mio, 2020 bis 2022). "
     "Quelle: hrs.ch/de/projekte/equinix-rechenzentren, immobilienbusiness.ch."),
    ("MBA Projektmanagement AG", "Generalplanung, Projektmanagement DC", "Fachplaner",
     "Green Metro-Campus Dielsdorf, ZUR02 Beringen, ETH HRZ, SCS ZH-Herdern",
     "Vier belegte DC-Referenzen, davon drei im Radar. Meistvernetzter Planer-Kontakt. "
     "Quelle: mbap.ch/de/referenzen/."),
    ("IKON Ingenieure AG", "Planung und Bauleitung DC", "Fachplaner",
     "ZUR2 und ZUR3 Glattbrugg (Digital Realty), Kandidat ZUR4",
     "Alle Phasen bei zwei Glattbrugg-Neubauten. Direktester Zugang zum ZUR4-Cx. "
     "Quelle: ikon.ch Referenzprojekte."),
    ("Drees & Sommer Schweiz AG", "Projektmanagement DC", "Fachplaner",
     "ZUR3 Glattbrugg (Digital Realty)",
     "Projektmanagement ZUR3 Campus. Quelle: dreso.com/ch/projekte."),
    ("Eins Architekten AG", "Architektur DC", "Fachplaner",
     "Green Metro-Campus Dielsdorf",
     "Architekturpartner von MBA fuer drei Datacenter und drei Buerogebaeude. "
     "Quelle: einsarchitekten.ch/projekte/metro-campus-green."),
    ("Emch+Berger AG", "Ingenieurleistungen DC", "Fachplaner",
     "Green Metro-Campus Dielsdorf",
     "Beteiligt laut eigener Referenzseite, Rolle pruefen. Quelle: emchberger.ch."),
    ("ERNE AG Bauunternehmung", "GU Technologiezentrum", "GU/TU",
     "Technologiezentrum Laufenburg (FlexBase)",
     "Strategische Partnerschaft mit FlexBase, Tiefbau laeuft. Quelle: erne-gruppe.ch."),
    ("Frei Architekten AG", "Architektur", "Fachplaner",
     "Technologiezentrum Laufenburg (FlexBase)",
     "Im Planerteam laut FlexBase-Projektuebersicht. Quelle: frei-architekten.ch."),
    ("Schnetzer Puskas Ingenieure", "Tragwerksplanung", "Fachplaner",
     "Technologiezentrum Laufenburg (FlexBase)",
     "Im Planerteam laut FlexBase-Projektuebersicht. Quelle: flexbase.ch/en/project-overview."),
    ("Koch + Partner", "Rolle pruefen", "Fachplaner",
     "Technologiezentrum Laufenburg (FlexBase)",
     "Im Planerteam genannt, Disziplin nicht belegt. Quelle: flexbase.ch/en/project-overview."),
    ("Equans Schweiz AG", "Technik, Batterie-Integration", "Elektro-Installateur",
     "Technologiezentrum Laufenburg (FlexBase)",
     "Plant mit Georg Fischer die Integration der Megabatterie und den Netzanschluss. "
     "Quelle: flexbase.ch/en/project-overview."),
    ("Georg Fischer AG", "Industriepartner Batterie", "Fachplaner",
     "Technologiezentrum Laufenburg (FlexBase)",
     "Mit Equans fuer Batterie-Integration und Netzanschluss genannt. "
     "Quelle: flexbase.ch/en/project-overview."),
    ("Itten + Brechbuehl AG", "Architektur", "Fachplaner",
     "Equinix ZH5.4 Oberengstringen",
     "Architekt der Equinix-Erweiterung ZH5.4 unter GU HRS. Quelle: hrs.ch."),
    ("Penzel Valier AG", "Architektur, Generalplanung", "Fachplaner",
     "Rechenzentrum Hoenggerberg (ETH Zuerich)",
     "Architektur im Generalplaner-Team des HRZ. Quelle: ethz.ch Bauprojekte."),
    ("Emch+Berger / DPR Construction", "GU Gebaeude 1 ZRH1", "GU/TU",
     "ZRH1 Winterthur (Vantage)",
     "DPR Construction baute Gebaeude 1 auf dem ZRH1-Campus. Quelle: dpr.com/projects. "
     "Zeile korrigieren: Firma ist DPR Construction, Emch+Berger hier streichen."),
]
# Die letzte Zeile oben waere doppelt verwirrend, DPR sauber eintragen:
partner[-1] = (
    "DPR Construction", "GU Gebaeude 1 ZRH1", "GU/TU",
    "ZRH1 Winterthur (Vantage)",
    "Baute Gebaeude 1 (ZRH11) auf dem Vantage-Campus Winterthur. Quelle: dpr.com/projects.")

for i, (firma, rolle, kanal, ref, notiz) in enumerate(partner):
    z = start + i
    werte = [firma, rolle, "FEHLT", kanal, ref, "FEHLT", "FEHLT", "FEHLT",
             "Kalt", None, None, 0, notiz]
    for j, wert in enumerate(werte, start=1):
        c = kt.cell(row=z, column=j, value=wert)
        c.font = text_font
        c.border = rahmen
        c.alignment = Alignment(vertical="top", wrap_text=j in (2, 5, 13))
        if wert == "FEHLT":
            c.fill = fehlt_fill
    kt.cell(row=z, column=10).number_format = "DD.MM.YYYY"
    kt.cell(row=z, column=11).number_format = "DD.MM.YYYY"

# Bestehende A+W-Zeile um Laufenburg ergaenzen
for z in range(5, kt.max_row + 1):
    if kt.cell(row=z, column=1).value == "Amstein + Walthert AG":
        kt.cell(row=z, column=5, value="ZUR02 Beringen (STACK) | Technologiezentrum Laufenburg (FlexBase)")
        alt = kt.cell(row=z, column=13).value or ""
        kt.cell(row=z, column=13, value=alt + " Zusaetzlich im Planerteam des FlexBase TZL "
                "Laufenburg belegt, flexbase.ch/en/project-overview. Zwei Radar-Projekte.")
        break

aend.append((
    "03_Kontakte, Partner-Netz",
    "16 Partnerfirmen mit belegten Projektzuordnungen ergaenzt: Implenia, HRS, MBA, IKON, "
    "Drees & Sommer, Eins Architekten, Emch+Berger, ERNE, Frei Architekten, Schnetzer "
    "Puskas, Koch + Partner, Equans, Georg Fischer, Itten + Brechbuehl, Penzel Valier, "
    "DPR Construction. Personen und Kontaktdaten als FEHLT.",
    "https://mbap.ch/de/referenzen/",
    "Das Partner-Netz steht. Drei Multiplikatoren stechen heraus: Implenia (drei Projekte), "
    "MBA (drei Projekte), HRS (zwei Betreiber). Diese drei zuerst."))

# --- Changelog ---------------------------------------------------------------
cl = wb["06_Changelog"]
z = 5
while cl.cell(row=z, column=3).value:
    z += 1
for i, (projekt, was, url, konsequenz) in enumerate(aend):
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

wb.save(DATEI)
print(f"{len(aend)} Radar-/Kontakt-Aenderungen, {len(partner)} Partnerfirmen geschrieben.")
