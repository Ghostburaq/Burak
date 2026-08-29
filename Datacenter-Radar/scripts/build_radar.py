#!/usr/bin/env python3
"""
Baut MiT_Datacenter_Radar_CH_V1.0.xlsx neu auf.

Nur fuer den Erstaufbau der Struktur gedacht. Der Montags-Lauf schreibt
danach mit openpyxl in die bestehende Datei, nicht mit diesem Skript.
Siehe CLAUDE.md Abschnitt 5.

Wichtig: Die Datei wird ohne data_only geschrieben, damit Formeln erhalten
bleiben. openpyxl legt keine zwischengespeicherten Werte ab, Excel rechnet
beim Oeffnen neu.
"""

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(os.path.dirname(HERE), "MiT_Datacenter_Radar_CH_V1.0.xlsx")

# Branding aus CLAUDE.md
NAVY = "1F3A5F"
ORANGE = "E8740C"
GELB = "FFF2CC"          # Spalten O, P, Q, V gehoeren Burak
GRAU = "F2F2F2"
WEISS = "FFFFFF"

DATENZEILE_START = 5
DATENZEILE_ENDE = 45      # Bereich, auf den das Dashboard zeigt
FORMATZEILE_ENDE = 200    # so weit werden Formate, Formeln und Dropdowns vorbereitet

kopf_font = Font(name="Arial", size=10, bold=True, color=WEISS)
kopf_fill = PatternFill("solid", fgColor=NAVY)
titel_font = Font(name="Arial", size=14, bold=True, color=NAVY)
sub_font = Font(name="Arial", size=9, italic=True, color="666666")
text_font = Font(name="Arial", size=10)
label_font = Font(name="Arial", size=10, bold=True, color=NAVY)
gelb_fill = PatternFill("solid", fgColor=GELB)
grau_fill = PatternFill("solid", fgColor=GRAU)
duenn = Side(style="thin", color="BFBFBF")
rahmen = Border(left=duenn, right=duenn, top=duenn, bottom=duenn)

wb = Workbook()
wb.remove(wb.active)


def kopfzeile(ws, kopf, zeile=4, breiten=None):
    for i, wert in enumerate(kopf, start=1):
        c = ws.cell(row=zeile, column=i, value=wert)
        c.font = kopf_font
        c.fill = kopf_fill
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        c.border = rahmen
    ws.row_dimensions[zeile].height = 30
    if breiten:
        for i, b in enumerate(breiten, start=1):
            ws.column_dimensions[get_column_letter(i)].width = b


def titelblock(ws, titel, untertitel):
    ws["A1"] = titel
    ws["A1"].font = titel_font
    ws["A2"] = untertitel
    ws["A2"].font = sub_font
    ws.row_dimensions[1].height = 22


# ---------------------------------------------------------------- 00_Anleitung
ws = wb.create_sheet("00_Anleitung")
ws.column_dimensions["A"].width = 4
ws.column_dimensions["B"].width = 118
ws.sheet_view.showGridLines = False

anleitung = [
    ("titel", "MiT Datacenter-Radar Schweiz V1.0"),
    ("sub", "Mobil in Time AG, An Aggreko Company. Sales Engineer Power, Burak Ucoez."),
    ("leer", ""),
    ("h", "Wofuer diese Datei da ist"),
    ("p", "Die Schweizer Rechenzentrums-Pipeline an einem Ort, woechentlich nachgefuehrt. "
          "Ziel ist nicht Vollstaendigkeit, sondern das richtige Zeitfenster. Ein Projekt im "
          "falschen Moment anzusprechen kostet gleich viel Zeit wie eines gar nicht zu kennen."),
    ("leer", ""),
    ("h", "Die sieben Blaetter"),
    ("p", "00_Anleitung   Diese Seite. Nur anfassen, wenn sich der Prozess aendert."),
    ("p", "01_Dashboard   Reine Formelzellen auf 02_Projekt_Radar, Zeilen 5 bis 45. "
          "Niemals Werte hineinschreiben. Waechst das Radar ueber Zeile 45, muessen die "
          "Bereiche in allen Dashboard-Formeln mitwachsen."),
    ("p", "02_Projekt_Radar   Das Herz. Kopfzeile in Zeile 4, Daten ab Zeile 5. "
          "Spalten R und S sind Formeln. Spalten O, P, Q und V sind gelb und gehoeren Burak."),
    ("p", "03_Kontakte   Pro Projekt mindestens drei Zeilen: Betreiber, GU/TU, Fachplaner. "
          "Kontaktdaten nur aus oeffentlicher Quelle. Keine E-Mail aus Namensmustern ableiten."),
    ("p", "04_Akquise_Tracker   Die Touchpoint-Sequenz. Statisch."),
    ("p", "05_Quellen_Montag   Feste Recherche-Reihenfolge. Pruefdatum in Spalte F."),
    ("p", "06_Changelog   Eine Zeile pro Aenderung. Ohne Changelog-Eintrag gilt eine "
          "Aenderung als nicht passiert."),
    ("leer", ""),
    ("h", "Der Montags-Lauf"),
    ("p", "In Claude Code im Projektordner: /dc-update    oder    DC-Radar Update KW 36"),
    ("p", "Der Lauf legt zuerst ein Backup an, recherchiert dann entlang 05_Quellen_Montag, "
          "schreibt nur belegte Angaben mit URL und Quellendatum, ergaenzt das Changelog und "
          "gibt am Schluss einen kurzen Bericht im Terminal aus. Steht die Websuche nicht zur "
          "Verfuegung, bricht der Lauf ab und die Datei bleibt unveraendert."),
    ("leer", ""),
    ("h", "Die vier Regeln, die hier weh tun, wenn man sie bricht"),
    ("p", "1. Quellenpflicht. Jede Angabe braucht URL in Spalte T und Datum in Spalte U."),
    ("p", "2. Keine erfundenen Werte. Was nicht belegt ist, steht als prueefen drin oder "
          "bleibt leer. Ein plausibel erfundener Wert ist der teuerste Fehler in diesem Projekt."),
    ("p", "3. Zeilen werden nie geloescht. Ein totes Projekt bekommt Phase Gestoppt und eine "
          "Bemerkung, damit die Historie bleibt."),
    ("p", "4. Gelbe Spalten und Formelspalten nie ueberschreiben."),
    ("leer", ""),
    ("h", "Konvention fuer unbelegte Dropdown-Felder"),
    ("p", "Spalte G Phase, Spalte N Prio und Spalte K Kanal_Prio haengen an Dropdowns. "
          "Ist der Wert nicht belegt, bleibt die Zelle leer und die Luecke steht in Spalte W. "
          "So bleibt die Dropdown-Pruefung sauber und das Dashboard zaehlt nicht falsch."),
    ("leer", ""),
    ("h", "Wo das Verkaufsfenster liegt"),
    ("p", "Planung und Bewilligung: zu frueh fuer Lastbank, richtig fuer Beziehungsaufbau beim Fachplaner."),
    ("p", "Baustart und Rohbau: Baustrom, Bridging, Trocknung. Kanal ist der GU."),
    ("p", "Fit-out minus sechs Monate: hier faellt der Entscheid ueber den Commissioning-Lasttest. "
          "Das wichtigste Fenster im ganzen Radar."),
    ("p", "Commissioning: Lastbank, Heat-Load-Test, Generator-Abnahme, USV-Test. Wer erst jetzt "
          "anruft, ist meist zu spaet, weil die Leistung im MEP-Vertrag steckt."),
    ("p", "Betrieb: Wartungsfenster, Netzanschlussarbeiten des EVU, Batterietausch, Bridging Power, PQ-Audit."),
    ("leer", ""),
    ("h", "Drei-Kanal-Regel"),
    ("p", "Der Betreiber entscheidet ueber Budget, der GU vergibt in der Bauphase, der Fachplaner "
          "schreibt aus. Ein Planer ist zehn Projekte, ein Betreiber ist eines. Zuerst Planer- und "
          "GU-Kanal pruefen, erst dann eine Betreiberansprache vorschlagen."),
]

r = 1
for art, wert in anleitung:
    c = ws.cell(row=r, column=2, value=wert)
    if art == "titel":
        c.font = titel_font
        ws.row_dimensions[r].height = 22
    elif art == "sub":
        c.font = sub_font
    elif art == "h":
        c.font = label_font
    else:
        c.font = text_font
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = max(14, 14 * (len(wert) // 105 + 1))
    r += 1


# ------------------------------------------------------------ 02_Projekt_Radar
ws = wb.create_sheet("02_Projekt_Radar")
titelblock(ws, "02 Projekt-Radar Schweiz",
           "Kopfzeile Zeile 4, Daten ab Zeile 5. R und S sind Formeln. O, P, Q, V gehoeren Burak.")

radar_kopf = [
    "Ref", "Projekt / Campus", "Betreiber", "Standort", "Kt.", "Kapazitaet_MW", "Phase",
    "IBN_Ziel", "GU_TU", "Fachplaner_Elektro", "Kanal_Prio", "MiT_Chance",
    "Ansprache_Fenster", "Prio", "Status_Kontakt", "Letzter_Kontakt", "Wiedervorlage",
    "Tage_bis_WV", "Ampel", "Quelle_URL", "Quelle_Stand", "Naechster_Schritt", "Bemerkung",
]
radar_breiten = [16, 34, 20, 16, 6, 13, 14, 14, 22, 22, 15, 34, 22, 6,
                 16, 15, 14, 11, 14, 52, 13, 34, 60]
kopfzeile(ws, radar_kopf, 4, radar_breiten)

STAND = "29.08.2026"

# Belegte Projekte. Reihenfolge grob nach Verkaufsfenster.
# Leeres Feld in G, K oder N heisst: nicht belegt, Luecke steht in W.
projekte = [
    # A  Ref, B Projekt, C Betreiber, D Standort, E Kt, F MW, G Phase, H IBN,
    # I GU/TU, J Fachplaner, K Kanal, L Chance, M Fenster, N Prio,
    # T Quelle, U Stand, W Bemerkung
    dict(
        b="Metro-Campus Zuerich West, Datacenter 4", c="Green (green.ch)", d="Lupfig", e="AG",
        f=12, g="Rohbau", h="Anfang 2027",
        i="Implenia (Shell and Core)", j="pruefen", k="GU/TU",
        l="Commissioning-Lastbank, Heat-Load-Test, Bautrocknung im Ausbau, PQ-Messung Klasse A",
        m="jetzt, Fit-out minus sechs Monate",
        n="A",
        t="https://www.aargauerzeitung.ch/aargau/brugg/lupfig-green-startet-mit-dem-bau-seines-vierten-datencenters-in-der-gemeinde-2026-soll-es-in-betrieb-genommen-werden-ld.2660374 | https://implenia.com/medien/artikel/implenia-gewinnt-attraktive-neue-projekte-in-den-bereichen-datacenter-gesundheit-sowie-energie-und-verkehrsinfrastruktur/",
        u=STAND,
        v="Implenia Bauleitung ueber Cx-Paket und Lastbank ansprechen, Fachplaner Elektro ueber Implenia erfragen",
        w="12 MW IT-Leistung fuer Kundensysteme, 5526 m2 Datacenter-Flaeche, 2000 m2 Buero. "
          "Rohbau 30 m hoch in zehn Monaten erstellt. Widerspruch: Aargauer Zeitung meldet "
          "Inbetriebnahme 2026, Green und Implenia nennen Anfang 2027. Auftragsvolumen "
          "Implenia ueber CHF 150 Mio. Fachplaner Elektro nicht belegt.",
    ),
    dict(
        b="ZUR02 Beringen", c="STACK Infrastructure", d="Beringen", e="SH",
        f=36, g="Rohbau", h="2026",
        i="pruefen", j="pruefen", k="GU/TU",
        l="Lastbank Voll- und Teillast im IST, Generator-Abnahme, USV-Test, PQ-Audit Klasse A",
        m="jetzt, Aufrichte gemeldet, Cx-Vergabe laeuft",
        n="A",
        t="https://www.datacenterdynamics.com/en/news/stack-tops-out-swiss-data-center-completes-construction-in-melbourne/ | https://algorithmwatch.ch/de/recherche-rechenzentren-schweiz/",
        u=STAND,
        v="Cx-Verantwortlichen ueber GU suchen, EKS wegen Unterwerk-Termin kontaktieren",
        w="36 MW, gebaut auf dem Areal des ehemaligen SIG-Tennisclubs. Kanton musste ein "
          "neues Unterwerk bauen, finanziert vom Betreiber. Netzanschluss-Termin ist der "
          "Hebel fuer Bridging Power. Baubewilligung in rund drei Monaten erteilt. "
          "GU und Fachplaner nicht belegt.",
    ),
    dict(
        b="ZUR4 Glattbrugg", c="Digital Realty", d="Glattbrugg (Opfikon)", e="ZH",
        f=15, g="Baustart", h="2028",
        i="pruefen", j="pruefen", k="GU/TU",
        l="Baustrom aus Generator, Bauheizung, Bautrocknung, spaeter Lastbank im Cx",
        m="jetzt fuer Baustrom und Trocknung, Cx-Ansprache ab 2027",
        n="A",
        t="https://www.inside-it.ch/spatenstich-fuer-neues-rz-von-digital-reality-in-glattbrugg-20260827 | https://www.globenewswire.com/news-release/2026/08/27/3351782/0/en/digital-realty-breaks-ground-on-new-state-of-the-art-data-center-in-switzerland.html",
        u="27.08.2026",
        v="GU des Spatenstichs ueber Baublatt oder Gemeinde Opfikon identifizieren, dann Baustrom anbieten",
        w="Spatenstich am 26.08.2026. 15 MW IT-Leistung auf rund 6300 m2, sechs Datenhallen. "
          "Fertigstellung 2028, danach rund 60 MW Campus-Gesamtleistung. Abwaermenetz "
          "zusammen mit der Gemeinde Opfikon. Vorlaufzeit Trocknung rund fuenf Monate, "
          "das Fenster ist jetzt. GU und Fachplaner nicht belegt.",
    ),
    dict(
        b="Metro-Campus Zuerich, Datacenter N und O", c="Green (green.ch)", d="Dielsdorf", e="ZH",
        f=35, g="Rohbau", h="pruefen",
        i="Implenia", j="pruefen", k="GU/TU",
        l="Bautrocknung, temporaere Klimatisierung im Ausbau, Lastbank im Cx, PQ-Messung",
        m="Cx-Entscheid faellt in den naechsten Monaten, jetzt Planer- und GU-Kanal aufbauen",
        n="A",
        t="https://www.presseportal.de/pm/152183/5635701 | https://www.baublatt.ch/bauprojekte/baustart-fuer-zwei-neue-datacenter-auf-metro-campus-in-dielsdorf-erfolgt-35044",
        u=STAND,
        v="Implenia Projektleitung Dielsdorf ansprechen, Abwaerme-Zeitplan mit Energie 360 abgleichen",
        w="Zwei Gebaeude, zusammen 35 MW, rund 4000 Racks auf 11600 m2. Campus 46000 m2. "
          "Implenia hat auf dem Campus bereits zwei Datacenter und ein Buerogebaeude gebaut. "
          "Abwaermenutzung durch Energie 360. IBN-Termin nicht belegt, Fachplaner nicht belegt.",
    ),
    dict(
        b="The Hive Campus Genf", c="NorthC", d="Genf", e="GE",
        f=4.5, g="Baustart", h="Q2 2028",
        i="pruefen", j="pruefen", k="Fachplaner",
        l="Baustrom, Bautrocknung, spaeter Lastbank und PQ-Messung im Cx",
        m="jetzt Planer-Kanal, Cx-Ansprache ab 2027",
        n="B",
        t="https://www.northcdatacenters.com/en/press-releases/northc-group-to-build-new-high-tech-data-center-in-geneva-switzerland/ | https://www.netzwoche.ch/news/2026-01-13/northc-errichtet-sechstes-rechenzentrum-in-der-schweiz",
        u="13.01.2026",
        v="Fachplaner Elektro ueber NorthC Schweiz erfragen, Romandie-Ansprache auf Franzoesisch",
        w="Sechstes NorthC-Rechenzentrum in der Schweiz. Baustart Q1 2026, rund 4.5 MW "
          "IT-Leistung auf 5400 m2, Fertigstellung Q2 2028. Direct-to-Chip-Fluessigkuehlung "
          "vorgesehen. Ansprache auf Franzoesisch, vous-Form. GU und Fachplaner nicht belegt.",
    ),
    dict(
        b="Technologiezentrum Laufenburg (TZL)", c="FlexBase", d="Laufenburg", e="AG",
        f="pruefen", g="Bewilligung", h="Sommer 2028",
        i="ERNE Gruppe (GU)", j="pruefen", k="GU/TU",
        l="Baustrom, Bautrocknung, Bridging Power bis Netzanschluss, spaeter Lastbank im Cx",
        m="jetzt, GU steht fest und Bauvorbereitung laeuft",
        n="A",
        t="https://www.erne-gruppe.ch/de/news/newsdetail/ernenews/medienmitteilung-flexbase/ | https://www.zhk.ch/de/wirtschaft-und-politik/news/flexbase-erhaelt-baufreigabe-fuer-technologiezentrum.html | https://www.datacenter-insider.de/flexbase-errichtet-technologiezentrum-mit-480-mw-ki-rechenzentrum-a-befea6134cb5045aba28a650a2ef6206/",
        u=STAND,
        v="ERNE Gruppe direkt ansprechen, Baustrom und Trocknung fuer 20000 m2 Baufeld",
        w="Baufreigabe erteilt. KI-Rechenzentrum mit bis zu 480 MW Rechenleistung auf rund "
          "12000 m2 IT-Netzflaeche, dazu Redox-Flow-Speicher mit ueber 1.6 GWh und ueber "
          "800 MW auf rund 20000 m2, direkt beim Unterwerk Stern von Laufenburg. "
          "480 MW ist Rechenleistung laut Quelle, nicht als elektrische Anschlussleistung "
          "uebernehmen, deshalb Spalte F auf pruefen. Inbetriebnahme Sommer 2028.",
    ),
    dict(
        b="Metro-Campus Zuerich, weiteres Datacenter", c="Green (green.ch)", d="Dielsdorf", e="ZH",
        f="pruefen", g="Planung", h="pruefen",
        i="pruefen", j="pruefen", k="Fachplaner",
        l="frueher Planer-Kontakt, damit Lastbank und PQ-Messung ins LV kommen",
        m="Planungsphase, Beziehungsaufbau beim Fachplaner",
        n="B",
        t="https://www.baublatt.ch/bauprojekte/green-baut-viertes-rechenzentrum-auf-metro-campus-in-dielsdorf-zh-36395 | https://www.netzwoche.ch/news/2026-06-03/so-praesentiert-sich-der-schweizer-markt-fuer-rechenzentren",
        u="03.06.2026",
        v="Green Bauherrenvertretung nach dem Fachplaner Elektro fragen",
        w="Widerspruch in der Zaehlung: Baublatt meldet ein viertes Rechenzentrum auf dem "
          "Metro-Campus Dielsdorf, Netzwoche meldet fuer 2026 den Baustart eines dritten "
          "Datacenters in Dielsdorf mit 5800 m2 Nutzflaeche. Beide URLs stehen in Spalte T. "
          "Nicht selbst entscheiden, beim naechsten Lauf ueber green.ch klaeren. "
          "Kapazitaet, IBN, GU und Fachplaner nicht belegt.",
    ),
    dict(
        b="ZH4 Zuerich, sechste Ausbauphase", c="Equinix", d="Zuerich", e="ZH",
        f="pruefen", g="Ausbau", h="2027",
        i="pruefen", j="pruefen", k="Betreiber",
        l="Bridging Power im laufenden Betrieb, temporaere Kaelte, PQ-Audit bei Umschaltungen",
        m="Ausbau im laufenden Betrieb, Wartungs- und Umschaltfenster",
        n="B",
        t="https://www.inside-it.ch/equinix-baut-data-center-in-zuerich-aus-20241112 | https://www.netzwoche.ch/news/2024-11-13/equinix-baut-zuercher-rechenzentrum-aus",
        u="13.11.2024",
        v="Site-Verantwortlichen ZH4 zum Umschaltkonzept ansprechen, Quelle ist aelter als ein Jahr, Stand pruefen",
        w="Sechste Ausbauphase, Investition rund CHF 40 Mio, Abschluss 2027. Rund 680 m2 "
          "zusaetzlicher Whitespace und rund 200 neue Cabinets. Ausbau im laufenden Betrieb, "
          "deshalb Betreiber-Kanal statt GU. Quelle vom November 2024, aktuelleren Stand suchen.",
    ),
    dict(
        b="UptownBasel Campus", c="NorthC", d="pruefen", e="pruefen",
        f=4.5, g="", h="2027",
        i="pruefen", j="pruefen", k="",
        l="Lastbank im Cx, PQ-Messung Klasse A, spaeter Wartungsfenster",
        m="Cx-Fenster vermutlich 2026 bis 2027, Termin verifizieren",
        n="B",
        t="https://www.netzwoche.ch/news/2026-06-03/so-praesentiert-sich-der-schweizer-markt-fuer-rechenzentren | https://www.datacenter-insider.de/northc-plant-sechstes-schweizer-rechenzentrum-in-basel-a-d051a0a594bcb4f730589892caf8a25f/",
        u="03.06.2026",
        v="Standort und Kanton ueber northcdatacenters.com verifizieren, danach Kanal festlegen",
        w="4.5 MW IT-Leistung, Betrieb ab 2027 gemeldet. Der Campus UptownBasel ist in den "
          "Quellen nur als Campusname belegt, Gemeinde und Kanton stehen dort nicht. "
          "Deshalb Standort und Kt. auf pruefen, Phase und Kanal leer. "
          "Beim naechsten Lauf ueber die Betreiberseite aufloesen.",
    ),
    dict(
        b="ZRH1 Winterthur", c="Vantage Data Centers", d="Winterthur", e="ZH",
        f=40, g="Ausbau", h="pruefen",
        i="DPR Construction (Gebaeude 1)", j="pruefen", k="Betreiber",
        l="Lastbank fuer die noch nicht gebauten Gebaeude, Bridging und PQ-Audit im Bestand",
        m="Campus im Etappenausbau, Fenster je Gebaeude pruefen",
        n="B",
        t="https://vantage-dc.com/data-center-locations/emea/zurich-i-switzerland/ | https://www.dpr.com/projects/vantage-data-centers-zurich-campus-building-1-zrh11",
        u=STAND,
        v="Etappenplan der Gebaeude 2 bis 4 erfragen, dann Cx-Fenster je Gebaeude setzen",
        w="Vier Gebaeude auf rund sieben Acres, im Vollausbau 40 MW. Erstes Gebaeude im "
          "Dezember 2021 eroeffnet, Landkauf Februar 2020. Adresse Fabrikstrasse 12, "
          "Winterthur. Betreiberseiten ohne Datum, Abrufdatum 29.08.2026. "
          "Termine der Folgegebaeude nicht belegt.",
    ),
    dict(
        b="ZRH2 Glattfelden", c="Vantage Data Centers", d="Glattfelden", e="ZH",
        f=24, g="", h="pruefen",
        i="pruefen", j="pruefen", k="Betreiber",
        l="wiederkehrende NEA-Tests, Wartungsfenster, Bridging Power, PQ-Audit",
        m="abhaengig vom Betriebsstatus, zuerst Widerspruch aufloesen",
        n="C",
        t="https://vantage-dc.com/news/vantage-data-centers-expands-emea-portfolio-with-second-zurich-campus-fueled-by-more-than-chf-370-million-investment/ | https://www.datacenterdynamics.com/en/news/vantage-to-launch-second-swiss-data-center-campus-outside-zurich/",
        u=STAND,
        v="Betriebsstatus ueber vantage-dc.com verifizieren, erst danach Phase setzen",
        w="24 MW kritische IT-Kapazitaet, rund 21000 m2, Investition ueber CHF 370 Mio, "
          "rund 30 km noerdlich von Zuerich. Zusammen mit ZRH1 dann 64 MW. "
          "Widerspruch: eine Quelle nennt die Eroeffnung im Sommer 2024, eine zweite eine "
          "Eroeffnung im Sommer 2026. Beide URLs stehen in T, Phase bleibt leer bis geklaert.",
    ),
    dict(
        b="ZUR01A Rafz", c="STACK Infrastructure", d="Rafz", e="ZH",
        f=10, g="", h="pruefen",
        i="pruefen", j="pruefen", k="",
        l="Baustrom und Trocknung falls noch im Bau, sonst Lastbank im Cx",
        m="Bauphase unklar, zuerst Status klaeren",
        n="C",
        t="https://www.datacentermap.com/switzerland/zurich/stack-infrastructure-zur01a/ | https://www.stackinfra.com/about/news-press/news/new-data-center-campus-in-beringen-switzerland/",
        u=STAND,
        v="Bau- oder Betriebsstatus ueber Gemeinde Rafz und stackinfra.com klaeren",
        w="10 MW, Industriestrasse, 8197 Rafz. Anlage besteht aus Hauptgebaeude mit Datenhalle, "
          "Buerogebaeude und separatem Generatorgebaeude. Eine Quelle bezeichnet Rafz als im "
          "Bau, ohne Termin. Aggregator-Quelle, deshalb schwach. Phase bleibt leer.",
    ),
    dict(
        b="ZUR03 Niederweningen", c="STACK Infrastructure", d="Niederweningen", e="ZH",
        f=30, g="", h="pruefen",
        i="pruefen", j="pruefen", k="",
        l="Lastbank im Cx, Bridging Power, PQ-Audit",
        m="Status unklar, zuerst verifizieren",
        n="C",
        t="https://baxtel.com/data-center/stack-zur03",
        u=STAND,
        v="Ueber stackinfra.com oder das kantonale Baugesuchsportal ZH verifizieren",
        w="30 MW Hyperscale-Campus auf rund sieben Acres, ein Gebaeude. Nur Aggregator-Quelle, "
          "kein Firmen- oder Fachmedien-Beleg. Phase und Termine nicht belegt. "
          "Beim naechsten Lauf entweder belegen oder Zeile auf Gestoppt setzen.",
    ),
    dict(
        b="ZUR3 Glattbrugg", c="Digital Realty", d="Glattbrugg (Opfikon)", e="ZH",
        f="pruefen", g="Betrieb", h="pruefen",
        i="pruefen", j="pruefen", k="Betreiber",
        l="Wartungsfenster, NEA-Test, Bridging Power waehrend Campus-Bauarbeiten ZUR4",
        m="waehrend der ZUR4-Bauphase, Bestand und Baustelle auf einem Campus",
        n="B",
        t="https://www.netzwoche.ch/news/2026-06-03/so-praesentiert-sich-der-schweizer-markt-fuer-rechenzentren | https://www.ikon.ch/referenzprojekte/neubau-rechenzentrum-digital-realty-zuerich-zur3-vormals-interxion-zur3",
        u="03.06.2026",
        v="Zusammen mit ZUR4 ansprechen, ein Ansprechpartner fuer Bestand und Neubau",
        w="Eines der flaechenmaessig groessten Rechenzentren der Schweiz, 11400 m2 Nutzflaeche, "
          "frueher Interxion ZUR3. Liegt auf demselben Campus wie der ZUR4-Neubau. "
          "Kapazitaet in MW nicht belegt.",
    ),
    dict(
        b="Rechenzentrum Hoenggerberg (HRZ)", c="ETH Zuerich", d="Zuerich", e="ZH",
        f="pruefen", g="", h="Anfang 2026",
        i="pruefen", j="pruefen", k="Betreiber",
        l="NEA-Test, Wartungsfenster, PQ-Audit nach Inbetriebnahme",
        m="nach Betriebsaufnahme, Wartungs- und Testzyklus",
        n="C",
        t="https://www.inside-it.ch/bald-ist-baubeginn-fuer-das-49-millionen-rechenzentrum-der-eth-zuerich-20230908",
        u="08.09.2023",
        v="Aktuellen Stand ueber ethz.ch pruefen, Quelle ist drei Jahre alt",
        w="Fuenfgeschossig, ueber 4000 m2, Baukosten rund CHF 49 Mio. Spatenstich April 2024, "
          "Bauarbeiten bis Ende 2025 geplant, IT-Betrieb ab Anfang 2026. Quelle von 2023, "
          "aktueller Stand nicht belegt, deshalb Phase leer. Oeffentlicher Bauherr, "
          "Beschaffung laeuft ueber simap.ch.",
    ),
    dict(
        b="Rechenzentrum Bonvillars", c="Swisscom", d="Bonvillars", e="VD",
        f="pruefen", g="Betrieb", h="pruefen",
        i="pruefen", j="pruefen", k="Betreiber",
        l="Wartungsfenster, NEA-Test, Bridging Power bei Umbauten",
        m="Betrieb, Rahmenvertrag statt Projektgeschaeft",
        n="C",
        t="https://www.netzwoche.ch/news/2026-06-03/so-praesentiert-sich-der-schweizer-markt-fuer-rechenzentren",
        u="03.06.2026",
        v="Ueber Swisscom Facility Management den Rahmenvertragsweg pruefen, Ansprache auf Franzoesisch",
        w="Elftes Swisscom-Rechenzentrum, Ende 2024 von Philip Morris uebernommen, "
          "1100 m2 Nutzflaeche. Kleinvolumen, aber Tuer zu den zehn weiteren Swisscom-Standorten. "
          "Ansprache Romandie auf Franzoesisch, vous-Form.",
    ),
]

for idx, p in enumerate(projekte):
    zeile = DATENZEILE_START + idx
    ws.cell(row=zeile, column=1, value=p.get("a", ""))
    ws.cell(row=zeile, column=2, value=p["b"])
    ws.cell(row=zeile, column=3, value=p["c"])
    ws.cell(row=zeile, column=4, value=p["d"])
    ws.cell(row=zeile, column=5, value=p["e"])
    ws.cell(row=zeile, column=6, value=p["f"])
    ws.cell(row=zeile, column=7, value=p["g"])
    ws.cell(row=zeile, column=8, value=p["h"])
    ws.cell(row=zeile, column=9, value=p["i"])
    ws.cell(row=zeile, column=10, value=p["j"])
    ws.cell(row=zeile, column=11, value=p["k"])
    ws.cell(row=zeile, column=12, value=p["l"])
    ws.cell(row=zeile, column=13, value=p["m"])
    ws.cell(row=zeile, column=14, value=p["n"])
    # O bis Q bleiben leer, die gehoeren Burak
    ws.cell(row=zeile, column=20, value=p["t"])
    ws.cell(row=zeile, column=21, value=p["u"])
    ws.cell(row=zeile, column=22, value=p.get("v", ""))
    ws.cell(row=zeile, column=23, value=p["w"])

# Formeln, Formate, gelbe Spalten bis FORMATZEILE_ENDE vorbereiten
for zeile in range(DATENZEILE_START, FORMATZEILE_ENDE + 1):
    ws.cell(row=zeile, column=18,
            value=f'=IF(Q{zeile}="","",Q{zeile}-TODAY())')
    ws.cell(row=zeile, column=19,
            value=f'=IF(Q{zeile}="","-",IF(Q{zeile}<TODAY(),"UEBERFAELLIG",'
                  f'IF(Q{zeile}-TODAY()<=7,"DIESE WOCHE","ok")))')
    for spalte in (15, 16, 17, 22):          # O, P, Q, V
        ws.cell(row=zeile, column=spalte).fill = gelb_fill
    for spalte in (16, 17):                  # P, Q
        ws.cell(row=zeile, column=spalte).number_format = "DD.MM.YYYY"
    for spalte in range(1, 24):
        c = ws.cell(row=zeile, column=spalte)
        c.font = text_font
        c.border = rahmen
        c.alignment = Alignment(vertical="top",
                                wrap_text=spalte in (12, 13, 20, 22, 23))
    ws.cell(row=zeile, column=6).number_format = "0.0"

ws.freeze_panes = "C5"
ws.auto_filter.ref = f"A4:W{FORMATZEILE_ENDE}"

# Dropdowns
dropdowns = {
    7: '"Planung,Bewilligung,Baustart,Rohbau,Fit-out,Commissioning,Betrieb,Ausbau,Verzoegert,Gestoppt"',
    15: '"Kalt,Angeschrieben,Erstkontakt,Erstgespraech,Qualifiziert,Offerte,Gewonnen,Verloren,Ruhend"',
    14: '"A,B,C"',
    11: '"Betreiber,GU/TU,Fachplaner,Ausschreibung,Elektro-Installateur"',
}
for spalte, formel in dropdowns.items():
    dv = DataValidation(type="list", formula1=formel, allow_blank=True, showDropDown=False)
    dv.error = "Nur Werte aus der Liste. Ist der Wert nicht belegt, Zelle leer lassen und die Luecke in Spalte W notieren."
    dv.errorTitle = "Wert nicht zulaessig"
    ws.add_data_validation(dv)
    L = get_column_letter(spalte)
    dv.add(f"{L}{DATENZEILE_START}:{L}{FORMATZEILE_ENDE}")


# --------------------------------------------------------------- 01_Dashboard
ws = wb.create_sheet("01_Dashboard", 1)
titelblock(ws, "01 Dashboard",
           "Reine Formelzellen auf 02_Projekt_Radar Zeilen 5 bis 45. Niemals Werte hineinschreiben.")
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 34
ws.column_dimensions["C"].width = 14
ws.column_dimensions["D"].width = 3
ws.column_dimensions["E"].width = 34
ws.column_dimensions["F"].width = 14
ws.sheet_view.showGridLines = False

R = "'02_Projekt_Radar'"
S, E = DATENZEILE_START, DATENZEILE_ENDE


def block(spalte_label, spalte_wert, start, titel, zeilen):
    r = start
    c = ws.cell(row=r, column=spalte_label, value=titel)
    c.font = Font(name="Arial", size=11, bold=True, color=WEISS)
    c.fill = PatternFill("solid", fgColor=NAVY)
    ws.cell(row=r, column=spalte_wert).fill = PatternFill("solid", fgColor=NAVY)
    r += 1
    for label, formel in zeilen:
        lc = ws.cell(row=r, column=spalte_label, value=label)
        lc.font = text_font
        lc.fill = grau_fill
        lc.border = rahmen
        wc = ws.cell(row=r, column=spalte_wert, value=formel)
        wc.font = Font(name="Arial", size=10, bold=True, color=NAVY)
        wc.border = rahmen
        wc.alignment = Alignment(horizontal="center")
        r += 1
    return r + 1


phasen = ["Planung", "Bewilligung", "Baustart", "Rohbau", "Fit-out",
          "Commissioning", "Betrieb", "Ausbau", "Verzoegert", "Gestoppt"]
status = ["Kalt", "Angeschrieben", "Erstkontakt", "Erstgespraech",
          "Qualifiziert", "Offerte", "Gewonnen", "Verloren", "Ruhend"]
kantone = ["ZH", "AG", "SH", "SG", "BS", "BL", "GE", "VD", "BE", "TG", "LU", "ZG"]

r = block(2, 3, 4, "UEBERBLICK", [
    ("Projekte im Radar", f"=COUNTA({R}!B{S}:B{E})"),
    ("Kapazitaet total MW (belegt)", f"=SUM({R}!F{S}:F{E})"),
    ("Prio A", f'=COUNTIF({R}!N{S}:N{E},"A")'),
    ("Prio B", f'=COUNTIF({R}!N{S}:N{E},"B")'),
    ("Prio C", f'=COUNTIF({R}!N{S}:N{E},"C")'),
    ("Phase nicht belegt", f"=COUNTA({R}!B{S}:B{E})-COUNTA({R}!G{S}:G{E})"),
    ("ohne Quelle_URL", f"=COUNTA({R}!B{S}:B{E})-COUNTA({R}!T{S}:T{E})"),
])

r = block(2, 3, r, "WIEDERVORLAGEN", [
    ("ueberfaellig", f'=COUNTIF({R}!S{S}:S{E},"UEBERFAELLIG")'),
    ("diese Woche", f'=COUNTIF({R}!S{S}:S{E},"DIESE WOCHE")'),
    ("ok", f'=COUNTIF({R}!S{S}:S{E},"ok")'),
    ("ohne Wiedervorlage", f"=COUNTA({R}!B{S}:B{E})-COUNT({R}!Q{S}:Q{E})"),
])

r = block(2, 3, r, "VERKAUFSFENSTER", [
    ("Bau laeuft (Baustart + Rohbau)",
     f'=COUNTIF({R}!G{S}:G{E},"Baustart")+COUNTIF({R}!G{S}:G{E},"Rohbau")'),
    ("Cx-Fenster (Fit-out + Commissioning)",
     f'=COUNTIF({R}!G{S}:G{E},"Fit-out")+COUNTIF({R}!G{S}:G{E},"Commissioning")'),
    ("frueh (Planung + Bewilligung)",
     f'=COUNTIF({R}!G{S}:G{E},"Planung")+COUNTIF({R}!G{S}:G{E},"Bewilligung")'),
    ("Bestand (Betrieb + Ausbau)",
     f'=COUNTIF({R}!G{S}:G{E},"Betrieb")+COUNTIF({R}!G{S}:G{E},"Ausbau")'),
    ("Verzoegert (Bridging-Chance)", f'=COUNTIF({R}!G{S}:G{E},"Verzoegert")'),
])

r2 = block(5, 6, 4, "PHASEN", [(p, f'=COUNTIF({R}!G{S}:G{E},"{p}")') for p in phasen])
r2 = block(5, 6, r2, "STATUS KONTAKT", [(s, f'=COUNTIF({R}!O{S}:O{E},"{s}")') for s in status])
r2 = block(5, 6, r2, "KANTONE", [(k, f'=COUNTIF({R}!E{S}:E{E},"{k}")') for k in kantone])

hinweis = ws.cell(row=max(r, r2) + 1, column=2,
                  value="Hinweis: openpyxl schreibt Formeln ohne zwischengespeicherte Werte. "
                        "Direkt nach dem Speichern zeigen Fremdtools None. Excel rechnet beim "
                        "Oeffnen neu. Das ist kein Fehler.")
hinweis.font = sub_font


# ---------------------------------------------------------------- 03_Kontakte
ws = wb.create_sheet("03_Kontakte")
titelblock(ws, "03 Kontakte",
           "Pro Projekt mindestens drei Zeilen: Betreiber, GU/TU, Fachplaner. "
           "Keine E-Mail aus Namensmustern ableiten. Unbekannt heisst FEHLT.")
kontakt_kopf = ["Firma", "Rolle_Funktion", "Name", "Kanal_Typ", "Projekt_Ref", "E-Mail",
                "Telefon", "LinkedIn", "Beziehungsstatus", "Letzter_Kontakt",
                "Naechster_Touchpoint", "Touchpoint_Nr", "Notiz"]
kopfzeile(ws, kontakt_kopf, 4,
          [26, 26, 20, 20, 34, 26, 18, 26, 18, 15, 18, 13, 50])

# Fuer jedes Projekt drei Zeilen. Firma steht nur dort, wo sie belegt ist.
kontakt_zeilen = []
for p in projekte:
    ref = f'{p["b"]} ({p["c"]})'
    kontakt_zeilen.append([p["c"], "Betreiber, Bauherrenvertretung", "FEHLT", "Betreiber",
                           ref, "FEHLT", "FEHLT", "FEHLT", "Kalt", "", "", 0,
                           "Aus dem Radar uebernommen. Name und Kontaktdaten offen."])
    gu = p["i"] if p["i"] not in ("pruefen", "") else "FEHLT"
    kontakt_zeilen.append([gu, "GU/TU, Bauleitung oder Projektleitung", "FEHLT", "GU/TU",
                           ref, "FEHLT", "FEHLT", "FEHLT", "Kalt", "", "", 0,
                           "GU laut Radar Spalte I." if gu != "FEHLT"
                           else "GU im Radar nicht belegt, zuerst identifizieren."])
    kontakt_zeilen.append(["FEHLT", "Fachplaner Elektro/MEP", "FEHLT", "Fachplaner",
                           ref, "FEHLT", "FEHLT", "FEHLT", "Kalt", "", "", 0,
                           "Hoechster Multiplikatorwert. Entscheidet, ob Lastbank und "
                           "PQ-Messung im LV stehen."])

fehlt_fill = PatternFill("solid", fgColor=GELB)
for i, row in enumerate(kontakt_zeilen):
    zeile = DATENZEILE_START + i
    for j, wert in enumerate(row, start=1):
        c = ws.cell(row=zeile, column=j, value=wert)
        c.font = text_font
        c.border = rahmen
        c.alignment = Alignment(vertical="top", wrap_text=j in (2, 5, 13))
        if wert == "FEHLT":
            c.fill = fehlt_fill
    ws.cell(row=zeile, column=10).number_format = "DD.MM.YYYY"
    ws.cell(row=zeile, column=11).number_format = "DD.MM.YYYY"

dv = DataValidation(type="list", allow_blank=True, showDropDown=False,
                    formula1='"Betreiber,GU/TU,Fachplaner,Ausschreibung,Elektro-Installateur,Behoerde,EVU"')
ws.add_data_validation(dv)
dv.add(f"D{DATENZEILE_START}:D{FORMATZEILE_ENDE}")
dv2 = DataValidation(type="list", allow_blank=True, showDropDown=False,
                     formula1='"Kalt,Angeschrieben,Erstkontakt,Erstgespraech,Qualifiziert,Offerte,Gewonnen,Verloren,Ruhend"')
ws.add_data_validation(dv2)
dv2.add(f"I{DATENZEILE_START}:I{FORMATZEILE_ENDE}")
ws.freeze_panes = "C5"
ws.auto_filter.ref = f"A4:M{FORMATZEILE_ENDE}"


# --------------------------------------------------------- 04_Akquise_Tracker
ws = wb.create_sheet("04_Akquise_Tracker")
titelblock(ws, "04 Akquise-Tracker",
           "Touchpoint-Sequenz. Statisch. Nur aendern, wenn Burak den Prozess aendert.")
kopfzeile(ws, ["Touchpoint", "Zeitpunkt", "Kanal", "Ziel", "Inhalt", "Abbruchkriterium"], 4,
          [12, 22, 20, 30, 56, 34])

touchpoints = [
    (1, "Tag 0", "E-Mail", "Aufmerksamkeit und Rollenklaerung",
     "Betreff konkret, ohne Fragezeichen. Aggreko in der ersten Zeile, weil Mobil in Time "
     "internationalen DC-Bauherren nichts sagt. Projektbezug als Vermutung formulieren. "
     "Eine Frage nach seinen Projekten, eine Weiterleitungsfrage, ein Anruftermin mit Datum und Uhrzeit.",
     "keine, Sequenz laeuft weiter"),
    (2, "Tag 3 bis 5", "Telefon",
     "Erstkontakt, richtige Person finden",
     "Auf die im Mail genannte Zeit anrufen. Kommt das Sekretariat, nach dem "
     "Commissioning-Verantwortlichen fragen, nicht nach dem Einkauf.",
     "falscher Ansprechpartner, dann Zeile umhaengen"),
    (3, "Tag 10 bis 14", "E-Mail",
     "Nachfassen mit neuem Anlass",
     "Kein ich wollte nur nachfragen. Neuer inhaltlicher Anlass statt Erinnerung, zum "
     "Beispiel eine Meldung zum Projekt oder ein Normenpunkt zur Rolle des Empfaengers.",
     "zweimal keine Reaktion, dann Touchpoint 4"),
    (4, "Tag 21", "LinkedIn",
     "zweiter Kanal, Sichtbarkeit",
     "Vernetzungsanfrage mit einer Zeile Bezug zum Projekt. Kein Pitch in der Anfrage.",
     "keine Annahme innerhalb 14 Tagen"),
    (5, "Tag 30 bis 40", "Telefon",
     "letzter aktiver Versuch in dieser Runde",
     "Konkreter Aufhaenger aus dem Radar, zum Beispiel Fit-out-Start oder ein "
     "gemeldeter Netzverzug. Ziel ist ein Termin, nicht ein Gespraech.",
     "kein Bedarf, dann Status Ruhend und Wiedervorlage in sechs Monaten"),
    (6, "Fit-out minus 6 Monate", "E-Mail oder Telefon",
     "das wichtigste Fenster im Radar",
     "Ansprache auf den Commissioning-Lasttest. Hier faellt der Entscheid, ob Lastbank "
     "und PQ-Messung im Leistungsverzeichnis stehen. Ausloeser ist die Phase im Radar, "
     "nicht der Kalender.",
     "Cx-Paket bereits vergeben, dann Nachunternehmer-Weg pruefen"),
    (7, "nach RFS, halbjaehrlich", "E-Mail",
     "Bestand halten",
     "Wartungsfenster, wiederkehrende NEA-Tests, Batterietausch, PQ-Audit nach EN 50160. "
     "Jetzt ist der Betreiber der richtige Ansprechpartner, vorher nicht.",
     "keines, laeuft dauerhaft"),
]

for i, tp in enumerate(touchpoints):
    zeile = DATENZEILE_START + i
    for j, wert in enumerate(tp, start=1):
        c = ws.cell(row=zeile, column=j, value=wert)
        c.font = text_font
        c.border = rahmen
        c.alignment = Alignment(vertical="top", wrap_text=j >= 4)
    ws.row_dimensions[zeile].height = 62

hinweis = ws.cell(row=DATENZEILE_START + len(touchpoints) + 1, column=1,
                  value="Vorschlag aus CLAUDE.md Abschnitt 7 abgeleitet, von Burak zu bestaetigen. "
                        "Bis zur Bestaetigung ist das kein verbindlicher Prozess.")
hinweis.font = sub_font


# --------------------------------------------------------- 05_Quellen_Montag
ws = wb.create_sheet("05_Quellen_Montag")
titelblock(ws, "05 Quellen Montag",
           "Feste Recherche-Reihenfolge fuer den Montags-Lauf. Pruefdatum in Spalte F.")
kopfzeile(ws, ["Nr", "Quelle", "URL", "Typ", "Was wird geprueft", "Pruefdatum"], 4,
          [6, 30, 46, 20, 52, 14])

quellen = [
    ("netzwoche.ch", "https://www.netzwoche.ch/tags/rechenzentrum", "Fachmedium",
     "neue Projekte, Baustart, Inbetriebnahme, Marktuebersicht"),
    ("it-markt.ch", "https://www.it-markt.ch", "Fachmedium",
     "Betreibermeldungen, Ausbauschritte"),
    ("inside-it.ch", "https://www.inside-it.ch", "Fachmedium",
     "Spatenstiche, Investitionen, Verzoegerungen"),
    ("itreseller.ch", "https://www.itreseller.ch", "Fachmedium",
     "Betreibermeldungen Schweiz"),
    ("datacenter-insider.de", "https://www.datacenter-insider.de", "Fachmedium",
     "DACH-Sicht, technische Details, Kuehlung und Leistung"),
    ("simap.ch", "https://www.simap.ch", "Ausschreibung",
     "oeffentliche Ausschreibungen, Cx-Pakete, Lastbank im LV"),
    ("baublatt.ch", "https://www.baublatt.ch", "Baumedium",
     "Baugesuche, Baustart, GU und TU, Bauetappen"),
    ("amtsblattportal.ch", "https://www.amtsblattportal.ch", "Amtlich",
     "Baupublikationen, Einsprachen"),
    ("Kanton ZH Baugesuche", "https://www.zh.ch", "Amtlich",
     "Baugesuche und Bewilligungen ZH"),
    ("Kanton AG Baugesuche", "https://www.ag.ch", "Amtlich",
     "Baugesuche und Bewilligungen AG"),
    ("Kanton SH Baugesuche", "https://sh.ch", "Amtlich",
     "Baugesuche und Bewilligungen SH"),
    ("Kanton SG Baugesuche", "https://www.sg.ch", "Amtlich",
     "Baugesuche und Bewilligungen SG"),
    ("Kanton BS Baugesuche", "https://www.bs.ch", "Amtlich",
     "Baugesuche und Bewilligungen BS"),
    ("Kanton GE Baugesuche", "https://www.ge.ch", "Amtlich",
     "Baugesuche und Bewilligungen GE"),
    ("LinkedIn Betreiber", "https://www.linkedin.com", "LinkedIn",
     "Vantage, Green, Digital Realty, NorthC, STACK, Equinix, FlexBase"),
    ("LinkedIn GU und Planer", "https://www.linkedin.com", "LinkedIn",
     "Implenia, ERNE, Steiner, Halter, Amstein + Walthert, HKG Engineering, Gruner"),
    ("Newsroom Vantage", "https://vantage-dc.com/news/", "Firmenmeldung",
     "Campus-Etappen, Eroeffnungen, Termine"),
    ("Newsroom Green", "https://www.green.ch", "Firmenmeldung",
     "Metro-Campus Zuerich und Campus ZRH1 Lupfig"),
    ("Newsroom Digital Realty", "https://www.digitalrealty.com", "Firmenmeldung",
     "ZUR3, ZUR4, Campus Glattbrugg"),
    ("Newsroom NorthC", "https://www.northcdatacenters.com", "Firmenmeldung",
     "Genf The Hive, UptownBasel, Winterthur"),
    ("Newsroom STACK", "https://www.stackinfra.com", "Firmenmeldung",
     "Beringen, Rafz, Niederweningen, Genfer Cluster"),
    ("Newsroom Equinix", "https://www.equinix.ch", "Firmenmeldung",
     "ZH2, ZH4, ZH5, GV1, GV2"),
    ("Newsroom FlexBase", "https://www.flexbase.swiss", "Firmenmeldung",
     "Technologiezentrum Laufenburg"),
    ("Regionalzeitungen", "https://www.aargauerzeitung.ch", "Regionalzeitung",
     "Einsprachen, Verzoegerungen, Gemeindeentscheide"),
    ("EVU EKZ", "https://www.ekz.ch", "EVU",
     "Netzanschluss, Unterwerke, Netzverstaerkung ZH"),
    ("EVU EKS", "https://www.eks.ch", "EVU",
     "Netzanschluss und Unterwerk Beringen SH"),
    ("EVU AEW", "https://www.aew.ch", "EVU",
     "Netzanschluss AG, Laufenburg und Lupfig"),
    ("EVU IWB", "https://www.iwb.ch", "EVU",
     "Netzanschluss BS und BL"),
    ("EVU ewz", "https://www.ewz.ch", "EVU",
     "Netzanschluss Stadt Zuerich"),
]

for i, (name, url, typ, pruefung) in enumerate(quellen):
    zeile = DATENZEILE_START + i
    ws.cell(row=zeile, column=1, value=i + 1)
    ws.cell(row=zeile, column=2, value=name)
    ws.cell(row=zeile, column=3, value=url)
    ws.cell(row=zeile, column=4, value=typ)
    ws.cell(row=zeile, column=5, value=pruefung)
    ws.cell(row=zeile, column=6, value="29.08.2026" if typ in
            ("Fachmedium", "Firmenmeldung", "Regionalzeitung", "Baumedium") else "")
    for j in range(1, 7):
        c = ws.cell(row=zeile, column=j)
        c.font = text_font
        c.border = rahmen
        c.alignment = Alignment(vertical="top", wrap_text=j == 5)

hinweis = ws.cell(row=DATENZEILE_START + len(quellen) + 1, column=2,
                  value="Erstlauf KW 35: die amtlichen Portale, simap.ch, LinkedIn und die "
                        "EVU-Meldungen wurden nicht geprueft, weil in dieser Umgebung nur die "
                        "Websuche und kein direkter Seitenabruf zur Verfuegung stand. "
                        "Pruefdatum dort bewusst leer.")
hinweis.font = sub_font
hinweis.alignment = Alignment(wrap_text=True, vertical="top")
ws.row_dimensions[DATENZEILE_START + len(quellen) + 1].height = 46


# --------------------------------------------------------------- 06_Changelog
ws = wb.create_sheet("06_Changelog")
titelblock(ws, "06 Changelog",
           "Eine Zeile pro Aenderung. Ohne Changelog-Eintrag gilt eine Aenderung als nicht passiert.")
kopfzeile(ws, ["Datum", "KW", "Projekt", "Was hat sich geaendert", "Quelle_URL",
               "Konsequenz fuer MiT"], 4, [13, 8, 38, 56, 50, 60])

DATUM = "29.08.2026"
KW_FORMEL = "=WEEKNUM(DATE(2026,8,29),21)"

changelog = [
    ("Radar V1.0 aufgebaut",
     "Datei mit sieben Blaettern neu erstellt, 16 belegte Projekte aus der Erstrecherche "
     "eingetragen, Dropdowns, Formeln in R und S und die gelben Spalten gesetzt.",
     "",
     "Pipeline steht. Ab jetzt laeuft der Montags-Lauf gegen einen Bestand statt gegen ein leeres Blatt."),
    ("Metro-Campus Zuerich West, Datacenter 4 (Green, Lupfig)",
     "Neu im Radar. 12 MW IT-Leistung, 5526 m2, Rohbau in zehn Monaten erstellt, "
     "Inbetriebnahme Anfang 2027. GU ist Implenia, Shell and Core.",
     "https://www.aargauerzeitung.ch/aargau/brugg/lupfig-green-startet-mit-dem-bau-seines-vierten-datencenters-in-der-gemeinde-2026-soll-es-in-betrieb-genommen-werden-ld.2660374",
     "IBN Anfang 2027 heisst Cx-Entscheid faellt jetzt. Implenia Bauleitung diese Woche "
     "auf das Cx-Paket ansprechen, sonst steckt die Lastbank im MEP-Vertrag."),
    ("ZUR02 Beringen (STACK)",
     "Neu im Radar. 36 MW, Aufrichte gemeldet, Eroeffnung 2026. Kanton musste ein neues "
     "Unterwerk bauen, finanziert vom Betreiber.",
     "https://www.datacenterdynamics.com/en/news/stack-tops-out-swiss-data-center-completes-construction-in-melbourne/",
     "Groesstes Cx-Volumen im Radar und der Termin ist nah. Netzanschluss ueber ein neues "
     "Unterwerk ist ein Bridging-Power-Signal, EKS-Termin klaeren."),
    ("ZUR4 Glattbrugg (Digital Realty)",
     "Neu im Radar. Spatenstich am 26.08.2026, 15 MW auf 6300 m2, sechs Datenhallen, "
     "Fertigstellung 2028, Campus danach rund 60 MW.",
     "https://www.inside-it.ch/spatenstich-fuer-neues-rz-von-digital-reality-in-glattbrugg-20260827",
     "Drei Tage alter Spatenstich. Baustrom, Bauheizung und Trocknung werden jetzt "
     "disponiert, Vorlaufzeit Trocknung rund fuenf Monate. GU identifizieren."),
    ("Metro-Campus Zuerich, Datacenter N und O (Green, Dielsdorf)",
     "Neu im Radar. Baustart erfolgt, zusammen 35 MW, rund 4000 Racks auf 11600 m2. "
     "Implenia hat auf dem Campus bereits gebaut.",
     "https://www.presseportal.de/pm/152183/5635701",
     "Bekannter GU auf bekanntem Campus. Einstieg ueber Implenia statt ueber Green, "
     "der GU vergibt in der Bauphase."),
    ("Technologiezentrum Laufenburg (FlexBase)",
     "Neu im Radar. Baufreigabe erteilt, ERNE ist GU, Inbetriebnahme Sommer 2028. "
     "KI-Rechenzentrum bis 480 MW Rechenleistung, Redox-Flow-Speicher ueber 1.6 GWh.",
     "https://www.erne-gruppe.ch/de/news/newsdetail/ernenews/medienmitteilung-flexbase/",
     "Groesstes Einzelprojekt im Radar. ERNE jetzt ansprechen, solange die Baustellen"
     "logistik fuer 20000 m2 Baufeld noch offen ist. Elektrische Anschlussleistung ist "
     "nicht belegt, keine Auslegung darauf stuetzen."),
    ("The Hive Campus Genf (NorthC)",
     "Neu im Radar. Baustart Q1 2026, 4.5 MW auf 5400 m2, Fertigstellung Q2 2028, "
     "Direct-to-Chip-Fluessigkuehlung vorgesehen.",
     "https://www.northcdatacenters.com/en/press-releases/northc-group-to-build-new-high-tech-data-center-in-geneva-switzerland/",
     "Romandie, Ansprache auf Franzoesisch. Fluessigkuehlung heisst hohe Leistungsdichte, "
     "der Lasttest wird anspruchsvoller und damit unser Thema."),
    ("ZH4 Zuerich (Equinix)",
     "Neu im Radar. Sechste Ausbauphase, rund CHF 40 Mio, 680 m2 Whitespace, Abschluss 2027.",
     "https://www.inside-it.ch/equinix-baut-data-center-in-zuerich-aus-20241112",
     "Ausbau im laufenden Betrieb. Umschaltungen brauchen Bridging Power und eine "
     "PQ-Messung. Quelle ist vom November 2024, Stand verifizieren."),
    ("ZRH2 Glattfelden (Vantage)",
     "Neu im Radar mit offenem Widerspruch: eine Quelle nennt die Eroeffnung im Sommer 2024, "
     "eine zweite im Sommer 2026. Beide URLs in Spalte T, Phase bleibt leer.",
     "https://vantage-dc.com/news/vantage-data-centers-expands-emea-portfolio-with-second-zurich-campus-fueled-by-more-than-chf-370-million-investment/",
     "Solange der Betriebsstatus offen ist, keine Ansprache. Erst Status klaeren, "
     "sonst laufen wir in ein falsches Fenster."),
    ("Metro-Campus Zuerich, weiteres Datacenter (Green, Dielsdorf)",
     "Neu im Radar mit offenem Widerspruch in der Zaehlung: Baublatt meldet ein viertes "
     "Datacenter in Dielsdorf, Netzwoche fuer 2026 den Baustart eines dritten mit 5800 m2.",
     "https://www.baublatt.ch/bauprojekte/green-baut-viertes-rechenzentrum-auf-metro-campus-in-dielsdorf-zh-36395",
     "Planungsphase, also Fachplaner-Kanal. Wer jetzt beim Planer sitzt, steht spaeter im LV."),
    ("STACK Rafz und Niederweningen",
     "Neu im Radar, aber nur ueber Aggregator-Quellen belegt. 10 MW Rafz, 30 MW "
     "Niederweningen, Phase und Termine offen.",
     "https://baxtel.com/data-center/stack-zur03",
     "Zwei potenziell grosse Objekte ohne belastbaren Stand. Naechster Lauf: ueber "
     "stackinfra.com und die Gemeinden belegen oder die Zeilen auf Gestoppt setzen."),
    ("ETH Rechenzentrum Hoenggerberg",
     "Neu im Radar. CHF 49 Mio, ueber 4000 m2, IT-Betrieb ab Anfang 2026 geplant. "
     "Einzige Quelle ist von 2023.",
     "https://www.inside-it.ch/bald-ist-baubeginn-fuer-das-49-millionen-rechenzentrum-der-eth-zuerich-20230908",
     "Oeffentlicher Bauherr, Beschaffung ueber simap.ch. Wiederkehrende NEA-Tests laufen "
     "dort ueber Ausschreibung, nicht ueber Beziehung."),
    ("Blatt 05_Quellen_Montag",
     "Pruefdatum nur bei Fachmedien, Firmenmeldungen, Baumedien und Regionalzeitungen "
     "gesetzt. Amtliche Portale, simap.ch, LinkedIn und EVU blieben ungeprueft.",
     "",
     "Luecke ist bewusst und sichtbar. Der naechste Lauf muss dort anfangen, dort liegen "
     "die Ausschreibungen und die Netzanschlusstermine."),
]

for i, (projekt, was, url, konsequenz) in enumerate(changelog):
    zeile = DATENZEILE_START + i
    ws.cell(row=zeile, column=1, value=DATUM)
    ws.cell(row=zeile, column=2, value=KW_FORMEL)
    ws.cell(row=zeile, column=3, value=projekt)
    ws.cell(row=zeile, column=4, value=was)
    ws.cell(row=zeile, column=5, value=url)
    ws.cell(row=zeile, column=6, value=konsequenz)
    for j in range(1, 7):
        c = ws.cell(row=zeile, column=j)
        c.font = text_font
        c.border = rahmen
        c.alignment = Alignment(vertical="top", wrap_text=j in (3, 4, 5, 6))
    ws.cell(row=zeile, column=2).alignment = Alignment(horizontal="center", vertical="top")

ws.freeze_panes = "A5"

# Blattreihenfolge festzurren
wb.move_sheet("00_Anleitung", offset=-wb.sheetnames.index("00_Anleitung"))
reihenfolge = ["00_Anleitung", "01_Dashboard", "02_Projekt_Radar", "03_Kontakte",
               "04_Akquise_Tracker", "05_Quellen_Montag", "06_Changelog"]
wb._sheets = [wb[name] for name in reihenfolge]
wb.active = 0

wb.save(TARGET)
print(f"geschrieben: {TARGET}")
print(f"Blaetter: {wb.sheetnames}")
print(f"Projekte im Radar: {len(projekte)}")
print(f"Kontaktzeilen: {len(kontakt_zeilen)}")
print(f"Changelog-Zeilen: {len(changelog)}")
print(f"Quellen: {len(quellen)}")
