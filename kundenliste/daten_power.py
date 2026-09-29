# -*- coding: utf-8 -*-
"""Datenbasis Top-Player Power Schweiz 2027 (Recherche Stand 27.09.2026).

Szenario je Projekt (alles Annahmen, in der Excel änderbar):
  gen_mva, gen_wo   Generator-Leistung in MVA und Mietdauer in Wochen
  lb_mw, lb_wo      Lastbank in MW und Mietdauer in Wochen
  bess_mw, bess_mo  Batteriespeicher in MW und Mietdauer in Monaten
  anteil27          Anteil des Volumens, der ins Jahr 2027 fällt
  p                 Wahrscheinlichkeit, dass MiT den Auftrag gewinnt
"""

RZ, INF, NETZ, SPI, IND, EVT, KAN = ("Rechenzentrum", "Infrastruktur", "Netz / Energie", "Spital",
                                     "Industrie", "Event", "Kanal-Partner")

# Marktrichtwerte (Annahmen-Blatt). Quelle je Wert, Umrechnung mit FX und cos phi im Excel.
RATES = dict(
    fx=0.828,           # USD/CHF 24.09.2026
    cosphi=0.8,
    gen_usd_lo=5000, gen_usd_hi=7800,      # USD pro MW und Woche (500-kW-Klasse x2, US-Richtwert)
    lb_usd_lo=1600, lb_usd_hi=3100,        # USD pro MW und Woche (1-MW-Lastbank, US-Richtwert)
    bess_usd_lo=10000, bess_usd_hi=50000,  # USD pro MW und Monat (Herstellerblog, Bandbreite)
    diesel_lh=145, diesel_chf=2.41,
    cool_usd_month=34666, cool_mw=1.75,
)


def rate_gen(r=RATES):
    return (r["gen_usd_lo"] + r["gen_usd_hi"]) / 2 * r["cosphi"] * r["fx"]


def rate_lb(r=RATES):
    return (r["lb_usd_lo"] + r["lb_usd_hi"]) / 2 * r["fx"]


def rate_bess(r=RATES):
    return (r["bess_usd_lo"] + r["bess_usd_hi"]) / 2 * r["fx"]


# (segment, projekt, einstieg, ort, kt, region, sprache, anlass, bedarf,
#  gen_mva, gen_wo, lb_mw, lb_wo, bess_mw, bess_mo, anteil27, p, crosssell, schritt, quelle, hinweis)
P = [
# ---------------------------------------------------------------- Rechenzentren
(RZ, "STACK ZUR02 Beringen", "STACK Infrastructure; PM MBA Projektmanagement", "Beringen", "SH", "Ostschweiz", "EN/DE",
 "36 MW IT, Betriebsstart Herbst 2026, neues Unterwerk vom Betreiber finanziert",
 "Lastbank für IST je Data Hall, Generator-Überbrückung falls Unterwerk verzögert, Tankcontainer",
 4, 8, 12, 3, 0, 0, 0.6, 0.30, "Temporäre Kühlung beim IST, falls Kälte nicht fertig",
 "Commissioning-Manager STACK und MBA sofort anfragen: IST-Plan der nächsten Phasen",
 "https://www.stackinfra.com/about/news-press/news/new-data-center-campus-in-beringen-switzerland/",
 "Hot Lead. Phase 1 läuft evtl. schon, Ziel sind Folgephasen 2027."),
(RZ, "Green Zürich West 4 Lupfig", "Green; GU Implenia", "Lupfig", "AG", "Nordwestschweiz", "DE",
 "12 MW IT, Inbetriebnahme 2026 geplant (eine Quelle nennt 2027)",
 "Lastbank für IST, Generator für Tests und Überbrückung",
 2, 4, 6, 4, 0, 0, 0.5, 0.30, "Temporäre Kühlung beim IST",
 "Green Facility/Commissioning und Implenia-Projektleitung kontaktieren",
 "https://implenia.com/medien/artikel/implenia-gewinnt-attraktive-neue-projekte-in-den-bereichen-datacenter-gesundheit-sowie-energie-und-verkehrsinfrastruktur/",
 "Commissioning läuft vermutlich jetzt. Tempo zählt."),
(RZ, "Green Metro-Campus Dielsdorf (nächstes RZ)", "Green; PM MBA Projektmanagement", "Dielsdorf", "ZH", "Zürich", "DE",
 "Baustart weiteres RZ 2026, Campus-Anschluss 50 MW über neues EKZ-UW",
 "Baustrom-Generator, später Lastbank für IST (2028)",
 1, 26, 6, 4, 0, 0, 0.6, 0.25, "Bauheizung und Bautrocknung im Winter",
 "Mit dem Lupfig-Kontakt bei Green gleich mitverhandeln",
 "https://www.baublatt.ch/bauprojekte/green-baut-viertes-rechenzentrum-auf-metro-campus-in-dielsdorf-zh-36395", ""),
(RZ, "Digital Realty ZUR4 Glattbrugg", "Digital Realty (GU noch unbekannt)", "Opfikon-Glattbrugg", "ZH", "Zürich", "EN",
 "15 MW IT, Spatenstich 27.08.2026, Fertigstellung 2028, High-Density/KI",
 "Baustrom 2027, Lastbank für IST 2028 (≈ IT-Last)",
 1, 26, 15, 4, 0, 0, 0.45, 0.20, "Bauheizung Winter 2026/27, Kühlung beim IST",
 "GU/Elektro über Baugesuch und simap ermitteln, dann Baustrom offerieren",
 "https://www.inside-it.ch/spatenstich-fuer-neues-rz-von-digital-reality-in-glattbrugg-20260827",
 "Deck auf Englisch klären."),
(RZ, "Vantage ZRH3 Volketswil", "Vantage Data Centers", "Volketswil", "ZH", "Zürich", "EN",
 "100 bis 150 MW Campus, Phase 1 live 2028, neue Unterwerke nötig, Engpass im Vornetz",
 "Generator/BESS-Überbrückung bis Netzanschluss, später Lastbank-IST",
 5, 26, 0, 0, 1, 6, 0.4, 0.10, "Temporäre Kühlung, Abwärme-Thema mit Energie 360°",
 "Beziehung jetzt aufbauen, Beschaffung oft EMEA-zentral",
 "https://www.datacenterdynamics.com/",
 "Grösstes Einzelpotenzial, tiefe Wahrscheinlichkeit. Quellen: EKZ blue (2025), DCD, Energie 360°; genauen Artikel-Link ergänzen."),
(RZ, "NorthC Arlesheim (uptownBasel)", "NorthC Datacenters", "Arlesheim", "BL", "Nordwestschweiz", "DE/EN",
 "4,5 MW IT (Ausbau 7,5), Betrieb ab Mitte 2027, NEA mit HVO",
 "Lastbank für IST, Generator für Tests",
 1, 12, 4.5, 3, 0, 0, 1.0, 0.30, "HVO-Generatoren passen zum Nachhaltigkeitskonzept",
 "NorthC Projektleitung CH: IST-Termin 2027 und Lastbank-Bedarf klären",
 "https://www.northcdatacenters.com/de/pressemitteilungen/northc-baut-auf-dem-campus-uptownbasel-das-rechenzentrum-der-zukunft/", ""),
(RZ, "NorthC Genf «The Hive»", "NorthC Datacenters", "Kanton Genf", "GE", "West (Romandie)", "FR/EN",
 "4,5 MW IT (3 × 1,5 MW), Baustart Q1 2026, fertig Q2 2028",
 "Baustrom, Lastbank je 1,5-MW-Stufe",
 0.5, 40, 1.5, 3, 0, 0, 0.6, 0.25, "Bauheizung, später Kühlung beim IST",
 "Zusammen mit Arlesheim als Paket anbieten",
 "https://www.northcdatacenters.com/en/press-releases/northc-group-to-build-new-high-tech-data-center-in-geneva-switzerland/", ""),
(RZ, "FlexBase Technologiezentrum Laufenburg", "FlexBase; Bau ERNE Gruppe", "Laufenburg", "AG", "Nordwestschweiz", "DE/EN",
 "KI-RZ plus Redox-Flow-Speicher >800 MW, Vollbetrieb Sommer 2028 (Zeitplan umstritten)",
 "Baustrom über Jahre, später Commissioning",
 2, 26, 0, 0, 0, 0, 0.6, 0.10, "Bauheizung, Bautrocknung",
 "Über ERNE einsteigen, Finanzierung beobachten",
 "https://flexbase.ch/en/project-overview", "Bewilligt ist nur die Gebäudehülle."),
# ---------------------------------------------------------------- Infrastruktur
(INF, "2. Gotthardröhre", "ASTRA; Marti-Gruppe (Hauptlos Süd)", "Göschenen / Airolo", "UR/TI", "Tessin", "DE/IT",
 "CHF 2,14 Mrd., Vortrieb bis ca. 2029/30",
 "Backup-Generatoren für Vortrieb und Lüftung, Lastspitzen",
 2, 52, 0, 0, 0, 0, 1.0, 0.15, "Bauheizung Portalinstallationen",
 "Marti Baustellenleitung Airolo: Backup-Konzept und Wartungsfenster",
 "https://www.astra.admin.ch/astra/de/home/themen/nationalstrassen/baustellen/medienmitteilungen/bellinzona/statolavorigottardo.html", ""),
(INF, "Sisikoner Tunnel (Neue Axenstrasse)", "ARGE Implenia/Frutiger; Bauherr ASTRA", "Sisikon", "UR", "Zentralschweiz", "DE",
 "über CHF 430 Mio., Bau Okt. 2025 bis 2034",
 "Baustrom und Netzersatz für Lüftung",
 1.5, 52, 0, 0, 0, 0, 1.0, 0.20, "Bauheizung, Entfeuchtung im Tunnel",
 "ARGE-Bauleitung: Rahmen für Baustrom-Backup",
 "https://implenia.com/medien/artikel/implenia-erhaelt-zuschlag-fuer-sisikoner-tunnel-herzstueck-der-neuen-axenstrasse-in-der-innerschweiz/", ""),
(INF, "Brüttener Tunnel (MehrSpur Zürich-Winterthur)", "SBB", "Bassersdorf / Dietlikon", "ZH", "Zürich", "DE",
 "Hauptarbeiten ab 2027, TBM ab 2029",
 "Installationsplätze vor Netzanschluss: Baustrom",
 1, 26, 0, 0, 0, 0, 1.0, 0.15, "Bauheizung",
 "SBB Infrastruktur Projekte: Baustrom-Ausschreibung verfolgen (simap)",
 "https://www.tagesanzeiger.ch/bruettener-tunnel-baustart-2026-in-bassersdorf-und-dietlikon-747315398294", "Öffentliche Beschaffung."),
(INF, "Bahnhof Zürich Stadelhofen (4. Gleis)", "SBB", "Zürich", "ZH", "Zürich", "DE",
 "CHF 1,1 Mrd., Baustart 2027, ca. 10 Jahre",
 "Leise BESS für Nachtarbeit, Netzersatz",
 0.5, 26, 0, 0, 0.5, 6, 1.0, 0.15, "Bautrocknung",
 "BESS-Hybrid als leise Lösung für Innenstadt positionieren",
 "https://www.nzz.ch/zuerich/grossprojekt-stadelhofen-was-der-bahnhofsumbau-bedeutet-ld.1884585", "Öffentliche Beschaffung."),
(INF, "Gare de Lausanne (Léman 2030)", "SBB/CFF", "Lausanne", "VD", "West (Romandie)", "FR",
 "Hauptarbeiten ab Ende 2027, viele Nachtschichten",
 "BESS und Generator für Nachtbaustellen",
 0.5, 8, 0, 0, 0.5, 3, 0.3, 0.15, "Bautrocknung",
 "CFF Projektleitung Lausanne, Dokumente auf Französisch",
 "https://company.sbb.ch/fr/developpement-ferroviaire/projets/suisse-romande-valais/leman-2030/nos-projets/gare-lausanne.html", ""),
(INF, "A1 Wankdorf-Schönbühl (8-Spur-Ausbau)", "ASTRA", "Bern / Schönbühl", "BE", "Mittelland/Bern", "DE",
 "CHF 474 Mio., ab 2027, ca. 6 Jahre",
 "Generatoren für Lichtsignale, Beleuchtung, Installationsplätze",
 0.5, 26, 0, 0, 0, 0, 1.0, 0.15, "",
 "Zuschlag an Bau-ARGE abwarten, dann ARGE ansprechen",
 "https://www.srf.ch/news/ausbau-autobahn-a1-zwischen-schoenbuehl-und-wankdorf-gibt-es-mehr-fahrspuren", ""),
(INF, "Stadtautobahn St.Gallen (BSA-Umstellung)", "ASTRA", "St. Gallen", "SG", "Ostschweiz", "DE",
 "ca. CHF 524 Mio., Schlussarbeiten 2027 bis Sommer 2028",
 "Netzersatz für Lüftung und Beleuchtung bei Umstellung",
 1, 12, 0, 0, 0, 0, 1.0, 0.20, "",
 "ASTRA Filiale Winterthur / BSA-Unternehmer: Umschaltplan",
 "https://stadtautobahn.ch/zahlen-fakten/", ""),
(INF, "Flughafen Zürich: neuer Tower", "Flughafen Zürich AG", "Kloten", "ZH", "Zürich", "DE",
 "Tower-Bau ab 2027 (ca. 2 Jahre), Dock A ab 2030 (> CHF 1 Mrd.)",
 "Netzersatz und BESS bei Umschaltungen im 24/7-Betrieb",
 1, 12, 0, 0, 0.5, 6, 0.5, 0.15, "Klima/Kühlung für Provisorien",
 "Flughafen Energie/Technik: Rahmen für Umschaltungen anbieten",
 "https://www.flughafen-zuerich.ch/en/company/flughafen-zuerich/airport-development/current-construction-projects/main-airport-complex-development", ""),
(INF, "Genève Aéroport Cap2030 / Plateforme multimodale", "Genève Aéroport; Losinger Marazzi (LMB)", "Genf", "GE", "West (Romandie)", "FR",
 "ca. CHF 560 bis 640 Mio., Multimodal 2026-2029, Terminal ab 2027",
 "Baustrom und USV/BESS im laufenden Terminalbetrieb",
 1, 26, 0, 0, 0.5, 6, 0.6, 0.15, "Bauheizung, Klima Provisorien",
 "Losinger Marazzi Bauleitung GVA, Französisch",
 "https://gva.blog/les-futurs-grands-chantiers-de-geneve-aeroport-dici-2033/", ""),
(INF, "Pumpspeicherwerk Grimsel 4", "KWO (BKW-Beteiligung)", "Grimsel", "BE", "Mittelland/Bern", "DE",
 "CHF 300 Mio., 2 × 84 MW, Bau Juni 2026 bis 2032",
 "Baustrom und Backup für hochalpine Untertagebaustelle",
 1, 52, 0, 0, 0, 0, 1.0, 0.15, "Bauheizung, Entfeuchtung",
 "KWO Projektleitung: Backup-Konzept Kaverne",
 "https://www.grimselstrom.ch/projekte/pumpspeicherwerk-grimsel-4", "BKW-Nähe: Konkurrenzlage prüfen."),
# ---------------------------------------------------------------- Netz
(NETZ, "Axpo UW Niederurnen (Gesamterneuerung)", "Axpo Grid", "Niederurnen", "GL", "Ostschweiz", "DE",
 "110/16 kV, ab Frühling 2026 ca. 3 Jahre, etappenweise",
 "Netzersatz und Eigenbedarf bei Umschaltungen, mobiler Trafo (Wert fehlt)",
 2, 8, 0, 0, 0, 0, 1.0, 0.25, "",
 "Axpo Grid Projektleitung: Etappenplan 2027",
 "https://www.axpo.com/ch/de/newsroom/medienmitteilungen/2026/gesamterneuerung-des-unterwerks-niederurnen-im-kanton-glarus---a.html",
 "Trafo-Miete nicht eingerechnet."),
(NETZ, "ewz UW Sihlfeld (Erneuerung)", "ewz", "Zürich", "ZH", "Zürich", "DE",
 "Innerstädtisches Unterwerk, 2027-2029",
 "Provisorien: Generator-Netzersatz, mobiler Trafo (Wert fehlt)",
 2, 8, 0, 0, 0, 0, 0.5, 0.20, "",
 "ewz Netzbau: Provisoriumskonzept, IVöB-Verfahren beachten",
 "https://www.stadt-zuerich.ch/de/aktuell/medienmitteilungen/2026/03/ewz-unterwerk-sihlfeld-wird-erneuert.html", "Öffentliche Beschaffung."),
(NETZ, "CKW: UW Sursee und Trafostations-Erneuerung", "CKW", "Sursee / Zentralschweiz", "LU", "Zentralschweiz", "DE",
 "UW Sursee IBN Frühling 2027 (CHF 11 Mio.), ca. 2'500 Trafostationen im Netz",
 "Netzersatz bei Umschaltungen, Generatoren für Trafostations-Tausch",
 1, 18, 0, 0, 0, 0, 1.0, 0.25, "",
 "CKW Netzbau: Rahmen für Netzersatz beim Stationstausch",
 "https://www.luzernerzeitung.ch/zentralschweiz/kanton-luzern/stromnetz-ckw-investiert-11-millionen-franken-in-unterwerk-sursee-ld.2761224",
 "Szenario: UW Sursee 2 MVA × 4 Wo plus Stationstausch 0,5 MVA × 20 Wo = ca. 18 MVA-Wochen."),
(NETZ, "Swissgrid UW Innertkirchen (neue GIS)", "Swissgrid", "Innertkirchen", "BE", "Mittelland/Bern", "DE",
 "ca. CHF 33 Mio., Baustart frühestens 2027",
 "Eigenbedarf und Provisorien während Umschaltung",
 1, 12, 0, 0, 0, 0, 0.3, 0.15, "",
 "Swissgrid Projektleitung, Ausschreibung verfolgen",
 "https://www.plattformj.ch/artikel/164567/", ""),
(NETZ, "Romande Energie: UW-Modernisierung HS/MS", "Romande Energie", "Kanton Waadt", "VD", "West (Romandie)", "FR",
 "Mehrere Unterwerk-Umbauten 2024-2027",
 "Netzersatz, mobiler Trafo (Wert fehlt)",
 1, 12, 0, 0, 0, 0, 1.0, 0.20, "",
 "Romande Energie Netzbau, Französisch",
 "https://www.pme.ch/conseils-dexperts/romande-energie/moderniser-les-postes-electriques-haute-et-moyenne-tension-pour-relever-les-defis/y3npfj2", ""),
# ---------------------------------------------------------------- Spitäler
(SPI, "Kantonsspital Aarau «Dreiklang»", "KSA; TU Implenia", "Aarau", "AG", "Nordwestschweiz", "DE",
 "ca. CHF 750 Mio., Übergabe 15.09.2026, Umzug Jan. 2027, danach Rückbau",
 "NEA-Lasttest mit Lastbank, Netzersatz beim Umzug, Baustrom Rückbau",
 1, 34, 2, 2, 0, 0, 1.0, 0.25, "Klima/Kühlung während Umzug",
 "KSA Technik und Implenia: NEA-Test und Rückbau-Baustrom jetzt anbieten",
 "https://www.ksa.ch/de/kantonsspital-aarau/ueber-uns/die-bauprojekte/neubau-dreiklang", ""),
(SPI, "USZ Campus MITTE1|2", "USZ; b+p baurealisation", "Zürich", "ZH", "Zürich", "DE",
 "CHF 950 Mio., Bau laufend, Betrieb 2031",
 "Netzersatz und BESS bei Umschaltungen im Vollbetrieb",
 1, 12, 0, 0, 0.5, 6, 1.0, 0.15, "Klima/Kühlung Provisorien",
 "USZ Technik: Umschaltkonzept 2027",
 "https://www.usz.ch/standorte/usz-campus/campusmitte/", "Öffentliche Beschaffung."),
(SPI, "Kantonsspital St.Gallen Haus 07B", "HOCH Health Ostschweiz", "St. Gallen", "SG", "Ostschweiz", "DE",
 "Rohbau 2026, Ausbau 2027/28, Übergabe 2029",
 "Baustrom Ausbau, später NEA-Test",
 0.5, 26, 0, 0, 0, 0, 1.0, 0.15, "Bauheizung, Trocknung",
 "HOCH Bau und Technik: Ausbauphase 2027",
 "https://www.kssg.ch/immobilien-und-betrieb/bauprojekte/neubauprojekt-come-together/neubau-haus-07b", ""),
# ---------------------------------------------------------------- Industrie
(IND, "Bachem Werk Sisslerfeld", "Bachem", "Eiken", "AG", "Nordwestschweiz", "DE",
 "über CHF 500 Mio., Greenfield, Bau bis ca. 2030",
 "Baustrom bis Netzanschluss, später Qualifizierung",
 1, 40, 0, 0, 0, 0, 1.0, 0.20, "Bauheizung, Bautrocknung",
 "Bachem Engineering und GU: Baustromkonzept",
 "https://www.bachem.com/wp-content/uploads/2026/07/2026-07-21-Press-Release-BSF-FINAL-DE.pdf", ""),
(IND, "Roche Basel Bau 51 und laufende Bauten", "Roche", "Basel / Kaiseraugst", "BS", "Nordwestschweiz", "DE/EN",
 "Bau 51 CHF 790 Mio. (Grundstein 21.09.2026), ca. CHF 1,4 Mrd. laufende Bauten",
 "Baustrom, später Lastbank/USV bei Qualifizierung",
 1, 26, 0, 0, 0, 0, 1.0, 0.15, "Klima/Reinraum-Provisorien",
 "Zugang über Installateur/FM vor Ort (ETAVIS K+S, Selmoni, CBRE)",
 "https://www.baublatt.ch/bauprojekte/roche-legt-grundstein-fuer-neuen-produktionsbau-in-basel-39630", ""),
(IND, "Lonza Stein Fill & Finish (plus Visp)", "Lonza", "Stein / Visp", "AG/VS", "Nordwestschweiz", "DE/EN",
 "CHF 500 Mio. Anlage Stein operativ ab H1 2027, Ibex Visp im Ramp-up",
 "NEA-Lasttests, temporäre USV, Netzersatz bei Validierung",
 1, 12, 2, 2, 0, 0, 1.0, 0.20, "Kühlung bei Validierung",
 "Lonza Engineering Stein: Inbetriebnahme H1 2027",
 "https://www.bioprocessintl.com/facilities-capacity/lonza-expands-stein-site-again-with-commercial-fill-finish-plant", ""),
(IND, "Novartis Schweizerhalle und Stein", "Novartis", "Pratteln / Stein", "BL/AG", "Nordwestschweiz", "DE/EN",
 "USD 80 Mio. siRNA Schweizerhalle, USD 26 Mio. Sterile Stein, bis ca. 2028",
 "Netzersatz bei Umbauten im GMP-Betrieb",
 1, 12, 0, 0, 0, 0, 1.0, 0.15, "Klima",
 "Novartis Engineering: Umschaltfenster",
 "https://www.novartis.com/ch-de/news/media-releases/novartis-passt-produktionsaktivitaeten-der-schweiz-und-investiert-innovative-herstelltechnologien", ""),
# ---------------------------------------------------------------- Events
(EVT, "WEF Annual Meeting 2027", "World Economic Forum", "Davos", "GR", "Ostschweiz", "EN/DE",
 "18.-22.01.2027, Pavillons und Sicherheit bei knappem Ortsnetz",
 "Generatoren redundant, BESS-Hybrid für leise Zonen",
 4, 3, 0, 0, 1, 1, 1.0, 0.15, "Zeltheizung, Heizzentralen (MiT-Kern)",
 "Offerte für 2027 jetzt, Aufbau startet im Dezember",
 "https://www.davos.ch/en/experience/events/world-economic-forum-annual-meeting-2027", "Szenario-Grösse ist Annahme."),
(EVT, "FIS Ski-WM Crans-Montana 2027", "Swiss-Ski / OK Crans-Montana 2027", "Crans-Montana", "VS", "West (Romandie)", "FR",
 "01.-14.02.2027, zwei Wochen Broadcast, Fan-Zonen, Hospitality",
 "Redundante Generatoren (n+1), BESS für Hospitality",
 3, 4, 0, 0, 0.5, 1, 1.0, 0.20, "Zeltheizung, Heizzentralen",
 "OK Crans-Montana 2027 sofort kontaktieren, Französisch",
 "https://www.cransmontana2027.ch/en/", "Szenario-Grösse ist Annahme."),
(EVT, "ESAF 2028 Thun", "OK ESAF 2028", "Thun", "BE", "Mittelland/Bern", "DE",
 "25.-27.08.2028, Aufbau ab Frühsommer 2028",
 "Arena, Festgelände, Camping: Generatoren und BESS",
 4, 4, 0, 0, 1, 1, 0.0, 0.20, "Kühlung Gastro",
 "Offerte und Konzept 2027, Umsatz 2028",
 "https://www.esaf2028.ch/", "Umsatz fällt 2028 an."),
# ---------------------------------------------------------------- Kanal-Partner
(KAN, "Burkhalter Gruppe (Rahmen)", "Burkhalter Holding, 83 Gesellschaften", "Zürich", "ZH", "Zürich", "DE/FR/IT",
 "5'356 FTE, 169 Standorte (31.12.2025)",
 "Baustrom und NEA-Tests über viele Töchter",
 1, 30, 0, 0, 0, 0, 1.0, 0.20, "Bauheizung, Trocknung über dieselben Baustellen",
 "Zentraler Einkauf: Rahmenvertrag, dann Töchter regional",
 "https://ch.marketscreener.com/boerse-nachrichten/burkhalter-kurzversion-nichtfinanzielle-berichterstattung-2025-ce7e50ded98bf423",
 "Rahmenvolumen (MVA-Wochen) ist Annahme."),
(KAN, "ETAVIS / VINCI Energies (Rahmen)", "VINCI Energies: ETAVIS, Actemium, Gfeller", "Zürich", "ZH", "Zürich", "DE/FR/IT",
 ">2'400 MA ETAVIS; Infrastruktur, RZ, Industrie",
 "Baustrom, Lastbank bei Inbetriebnahmen",
 1, 30, 1, 6, 0, 0, 1.0, 0.20, "Bauheizung",
 "VINCI Einkauf CH: Rahmen für Power",
 "https://www.vinci-energies.ch/unsere-bereiche/etavis/", "Rahmenvolumen ist Annahme."),
(KAN, "Equans Switzerland (Rahmen)", "Bouygues / Equans", "Zürich", "ZH", "Zürich", "DE/FR",
 ">1'600 MA, Energie, Verkehr, Industrie, FM",
 "Netzersatz, NEA-Tests, Baustrom",
 1, 25, 1, 4, 0, 0, 1.0, 0.20, "Heizung/Kühlung im FM-Geschäft",
 "Equans Einkauf und FM-Leitung gemeinsam",
 "https://www.phase5.ch/nun-heisst-es-offiziell-equans-switzerland", "Rahmenvolumen ist Annahme."),
(KAN, "BKW Building Solutions (Rahmen)", "BKW: AEK, ISP, swisspro, Arnold, inelectro", "Ostermundigen", "BE", "Mittelland/Bern", "DE/FR",
 "ca. 4'000 MA in ca. 50 Firmen",
 "Baustrom, Netzersatz (Arnold: Kabelnetzbau)",
 1, 20, 0, 0, 0, 0, 1.0, 0.15, "Bauheizung",
 "BKW BS Einkauf; BKW ist auch Energie-Anbieter",
 "https://www.bkw.com/en/about-us/building-solutions", "Rahmenvolumen ist Annahme."),
(KAN, "CKW Gebäudetechnik und EKZ Eltop (Rahmen)", "Axpo-Gruppe (CKW) / EKZ", "Luzern / Zürich", "LU/ZH", "Zentralschweiz", "DE",
 "ca. 1'400 MA CKW GT, ca. 550 MA EKZ Eltop",
 "Baustrom, BESS",
 1, 20, 0, 0, 0, 0, 1.0, 0.15, "Bauheizung",
 "Getrennt ansprechen, gemeinsam auswerten",
 "https://www.ckw.ch/gebaeudetechnik/elektroinstallationen", "Rahmenvolumen ist Annahme."),
]

# Beobachten: unter CHF 50'000 oder zu unsicher (segment, name, ort, grund, quelle)
W = [
(RZ, "Equinix ZH4 Phase 6", "Zürich", "CHF 40 Mio. Ausbau, fertig 2027. Kleiner Commissioning-Umfang.", "https://www.inside-it.ch/equinix-baut-data-center-in-zuerich-aus-20241112"),
(RZ, "ENKA Rechenzentrum Beringerfeld", "Beringen SH", "Baugesuch in Vorprüfung, starker Widerstand.", "https://www.shn.ch/"),
(RZ, "Microsoft / AWS / Google Cloud-Regionen", "Zürich / Genf", "Standorte nicht öffentlich, meist Colocation: Zugang über Green, Vantage, STACK.", "https://news.microsoft.com/de-ch/"),
(RZ, "Swiss Government Cloud (BIT)", "Bund", "CHF 319 Mio. 2025-2032, Private Cloud in eigenen RZ.", "https://www.bit.admin.ch/"),
(NETZ, "Alpiq BESS Niedergösgen 300 MW / 1,2 GWh", "Niedergösgen SO", "Bau 2027, IBN 2029: Baustrom klein, Partner-Thema BESS.", "https://www.ess-news.com/"),
(NETZ, "BESS Bonaduz 60 MW / 120 MWh", "Bonaduz GR", "COD H1 2027, Commissioning-Support prüfen.", "https://www.energy-storage.news/"),
(SPI, "Spital Sion Erweiterung", "Sion VS", "OP-Bündelung bis Ende 2027, Umfang eher unter CHF 50'000.", "https://www.lenouvelliste.ch/"),
(IND, "Swiss Chip FabLab Dübendorf", "Dübendorf ZH", "Finanzierung offen, Betrieb ab 2028 geplant.", "https://www.itmagazine.ch/artikel/85232/"),
(EVT, "Weltcup Adelboden und Lauberhorn", "Adelboden / Wengen BE", "Je unter CHF 50'000 Miete, zusammen interessant. BKW Sponsor Lauberhorn.", "https://www.lauberhorn.ch/en/races/"),
(EVT, "Sommer-Openairs (St.Gallen, Frauenfeld, Gurten, Paléo, Montreux)", "diverse", "Einzeln meist unter CHF 50'000, als Saisonpaket prüfen.", "https://www.openairsg.ch/"),
(EVT, "Art Basel 2027", "Basel", "Satelliten-Pavillons, Umfang unklar.", "https://www.basel.com/en/events/art-basel"),
(INF, "Zimmerberg-Basistunnel II", "Thalwil-Baar", "Bau ab 2029.", "https://company.sbb.ch/"),
(INF, "Stadion Hardturm Zürich", "Zürich", "Baubeginn frühestens 2027/28.", "https://www.20min.ch/"),
("Facility Manager", "ISS, CBRE, Honegger (NEA-Test-Programme)", "national", "Wiederkehrende NEA-Tests, je Objekt klein: als Rahmen prüfen.", "https://ch.issworld.com/"),
("Elektroplaner", "Amstein + Walthert, HHM, Scherler", "national", "Kaufen nicht selbst, schreiben aber Notstrom und Lastbank-Tests aus.", "https://amstein-walthert.ch/"),
]

COMP = [
("Avesco Rent (Cat)", "Cat-Generatoren, z.B. XQP500 (550 kVA)", "https://www.avescorent.ch/de/mietkategorie/power-system/"),
("Bimex", "Aggregate bis 2'000 kVA, netzparallel", "https://www.bimex.ch/mieten/"),
("GENGA AG", "bis 670 kVA, auf Anfrage bis 2'500 kVA", "https://www.genga.ch/"),
("Kummler+Matter EVT", "Mobile Trafostationen MS/NS (Partner und Wettbewerber)", "https://kuma-evt.ch/de/kompetenzen/energie/energieversorgung/bauprovisorien-mittel-niederspannung"),
("Arag Bau", "Generatoren 20 bis 608 kVA", "https://www.arag-bau.ch/"),
("Loxam CH / Boels CH", "Generatoren bis ca. 150 kVA", "https://www.loxam.ch/"),
("Energyst (Cat Rental Power)", "Generatoren, Trafos, Lastbänke; CH vermutlich über Avesco", "https://www.energyst.com/solutions/"),
]

# ---------------------------------------------------------------- gemeinsam für Excel und Deck
ZIELROLLE = {
    RZ: "Commissioning-Manager, Construction Manager, Critical Facility Ops",
    INF: "Bauleitung ARGE, Baustelleneinrichtung, Einkauf",
    NETZ: "Leiter Netzbau / Unterwerke, Projektleiter UW",
    SPI: "Leiter Technik und Betrieb, TU-Projektleitung",
    IND: "Engineering / Utilities, Technischer Einkauf",
    EVT: "Produktionsleitung, Technische Leitung OK",
    KAN: "Einkauf Gruppe, Bereichsleiter Grossprojekte",
}

# Produktbedarf je Segment: 3 Kernbedarf, 2 häufig, 1 gelegentlich, 0 kaum (Einschätzung aus den Szenarien)
PRODUKTE = ["Generator", "Lastbank", "BESS", "Mobiler Trafo", "NEA-Test / USV", "Tank / HVO"]
MATRIX = {
    RZ: [3, 3, 2, 1, 3, 2],
    INF: [3, 0, 2, 1, 0, 3],
    NETZ: [3, 0, 1, 3, 1, 1],
    SPI: [2, 2, 2, 1, 3, 1],
    IND: [3, 1, 1, 1, 2, 1],
    EVT: [3, 0, 3, 0, 0, 2],
    KAN: [3, 1, 1, 1, 2, 1],
}

PORTFOLIO = [  # Produkt, Wofür, Typische Kunden, Kennwerte / Hinweis, Quelle
    ("Generator", "Baustrom, Netzersatz, Events, Überbrückung bis Netzanschluss",
     "GU/TU, Tunnel, RZ im Bau, Events, Netzbetreiber",
     "Aggreko CH: 30 bis 2'100 kVA, Diesel, Gas, HVO, Stage V. Immer klären: Prime (Dauer) oder Standby (Notstrom).",
     "aggreko.com/de-ch/products/generators"),
    ("Lastbank", "Künstliche Last für NEA-Tests und RZ-Commissioning (IST)",
     "RZ, Spitäler, Pharma, Facility Manager",
     "Aggreko: 100 bis 6'250 kW, Commissioning Level L1 bis L5, flüssigkeitsgekühlte Varianten für KI-RZ.",
     "aggreko.com (Data Centre Commissioning, Load Banks)"),
    ("BESS", "Leise, emissionsfreie Versorgung, Lastspitzen kappen, Hybrid mit Generator",
     "Events, Nachtbaustellen, Innenstadt, Spitäler",
     "Beispiel Aggreko: 1 MW / 1,2 MWh. Immer nutzbare Kapazität (kWh) und C-Rate angeben, nicht Nennkapazität.",
     "aggreko.com"),
    ("Mobiler Trafo", "Provisorische Einspeisung MS/NS bei Unterwerk- und Stationsumbau",
     "Netzbetreiber, Industrie, Grossbaustellen",
     "Bei MiT nicht belegt, über Aggreko prüfen. Mietsatz: Wert fehlt, aus Preisliste ergänzen.",
     "aggreko.com"),
    ("NEA-Test und Messung", "Netzersatzanlage unter Last prüfen, Netzqualität vor und nach Umschaltung messen",
     "Spitäler, Industrie, RZ, Facility Manager",
     "Messung nach EN 50160 (Spannungsmerkmale) mit Geräten nach IEC 61000-4-30 Klasse A.",
     "eigene Fachkompetenz"),
    ("Tankcontainer / HVO", "Treibstoff-Logistik für Dauerbetrieb, erneuerbarer Diesel",
     "Tunnel, RZ-Überbrückung, Events",
     "1 MVA bei 75 % Last: ca. 139 bis 154 l/h (Cummins C1000 D5), rund CHF 350 pro Stunde bei 2,41 CHF/l.",
     "Cummins-Datenblatt; TCS 18.09.2026"),
    ("Cross-Sell Wärme / Kälte", "Bauheizung, Trocknung, temporäre Kühlung, Zeltheizung, Entfeuchtung",
     "Winterbaustellen, RZ-IST, Spital-Umzug, WEF, Ski-WM",
     "MiT-Kerngeschäft. Kühlung Richtwert ca. CHF 16'400 pro MW (therm.) und Monat (US-Lease, umgerechnet).",
     "mobilintime.com; kwipped.com"),
]

RZ_DETAIL = [  # Betreiber/Projekt, Standort, IT-MW, Zeitplan, GU/PM, Netzanschluss, Status für uns, Quelle
    ("STACK ZUR02", "Beringen SH", "36", "Aufrichte 2025, Betriebsstart Herbst 2026", "PM MBA Projektmanagement",
     "neues Unterwerk vom Betreiber finanziert, ca. 350 GWh/a", "Hot Lead: Folgephasen-IST 2027", "stackinfra.com; shn.ch 12.02.2026"),
    ("Green Zürich West 4", "Lupfig AG", "12", "Baustart 01/2025, IBN 2026 (eine Quelle: 2027)", "GU Implenia (> CHF 150 Mio.)",
     "Abwärme ins Netz IBB", "Hot Lead: Commissioning läuft", "implenia.com 27.03.2025"),
    ("Green Metro-Campus", "Dielsdorf ZH", "Campus-Anschluss 50 MW", "RZ2/RZ3 im Bau, weiteres RZ Baustart 2026", "PM MBA Projektmanagement",
     "EKZ-UW Dielsdorf (CHF 14 Mio., 50 MW) seit 09/2025", "Baustrom 2027, IST 2028", "baublatt.ch; ekz.ch"),
    ("Digital Realty ZUR4", "Opfikon-Glattbrugg ZH", "15", "Spatenstich 27.08.2026, fertig 2028", "unbekannt: simap / Baugesuch prüfen",
     "unbekannt", "Baustrom 2027, IST 2028", "investor.digitalrealty.com 27.08.2026"),
    ("Vantage ZRH3", "Volketswil ZH", "100 bis 150", "Phase 1 live 2028", "unbekannt",
     "neue Unterwerke nötig, Engpass Vornetz Axpo/Swissgrid", "Beziehung aufbauen, EMEA-Beschaffung", "ekz.ch/blue 2025; datacenterdynamics.com"),
    ("NorthC Arlesheim", "Arlesheim BL", "4,5 (Ausbau 7,5)", "Betrieb ab Mitte 2027", "unbekannt",
     "6 MVA, NEA mit HVO", "IST 2027", "northcdatacenters.com 11.09.2025"),
    ("NorthC «The Hive»", "Kanton Genf", "4,5 (3 × 1,5)", "Baustart Q1 2026, fertig Q2 2028", "unbekannt",
     "NEA mit HVO, Direct-to-Chip", "Baustrom 2027, IST 2028", "northcdatacenters.com"),
    ("FlexBase TZL", "Laufenburg AG", "bis ca. 500 (technisch, ?)", "Spatenstich 05.05.2025, Vollbetrieb Sommer 2028 (umstritten)", "ERNE Gruppe",
     "Swissgrid Phase 1 bewilligt, 800 MW", "Beobachten, über ERNE", "flexbase.ch; srf.ch"),
    ("Equinix ZH4 Phase 6", "Zürich", "?", "CHF 40 Mio., fertig 2027", "?", "?", "Beobachten (unter CHF 50'000)", "inside-it.ch 12.11.2024"),
    ("NTT Zurich 1", "Rümlang ZH", "20", "in Betrieb, keine Erweiterung gefunden", "–", "–", "NEA-Tests wiederkehrend", "datacentermap.com"),
    ("ENKA Beringerfeld", "Beringen SH", "?", "Baugesuch in Vorprüfung, Widerstand", "ENKA İnşaat", "unklar", "Beobachten", "shaz.ch 10.08.2026"),
]

PLAN = [  # Monat, Termin, Aufgabe, Projekt
    ("Oktober", "16.10.2026", "Commissioning-Manager kontaktieren, IST-Plan der Folgephasen klären", "STACK ZUR02 Beringen"),
    ("Oktober", "16.10.2026", "IST-Termin und Lastbank-Bedarf mit Green und Implenia klären", "Green Zürich West 4 Lupfig"),
    ("Oktober", "23.10.2026", "NEA-Lasttest Umzug Jan. 2027 und Rückbau-Baustrom offerieren", "Kantonsspital Aarau «Dreiklang»"),
    ("Oktober", "23.10.2026", "OK kontaktieren, Bedarf abfragen (Unterlagen Französisch)", "FIS Ski-WM Crans-Montana 2027"),
    ("Oktober", "30.10.2026", "Arlesheim und Genf als Paket anbieten", "NorthC Arlesheim (uptownBasel) / NorthC Genf «The Hive»"),
    ("November", "13.11.2026", "Rahmengespräch Einkauf Gruppe", "Burkhalter Gruppe (Rahmen)"),
    ("November", "13.11.2026", "Rahmengespräch Einkauf VINCI Energies CH", "ETAVIS / VINCI Energies (Rahmen)"),
    ("November", "20.11.2026", "Rahmengespräch Einkauf und FM-Leitung", "Equans Switzerland (Rahmen)"),
    ("November", "20.11.2026", "Offerte abgeben, Aufbau startet im Dezember", "WEF Annual Meeting 2027"),
    ("November", "27.11.2026", "GU/Elektro über simap und Baugesuch ermitteln, Baustrom offerieren", "Digital Realty ZUR4 Glattbrugg"),
    ("Dezember", "04.12.2026", "MiT-Mietsätze im Blatt «Annahmen» Spalte E eintragen", "alle"),
    ("Dezember", "11.12.2026", "Kundenstatus aus CRM für alle Top-Player eintragen", "alle"),
    ("Dezember", "18.12.2026", "Backup-Rahmen mit Baustellenleitung besprechen", "2. Gotthardröhre / Sisikoner Tunnel (Neue Axenstrasse)"),
    ("Januar", "15.01.2027", "Review im Team, Pipeline neu rechnen, Prio anpassen", "alle"),
    ("Januar", "22.01.2027", "Beziehung aufbauen, RZ 2028 aufgleisen", "Vantage ZRH3 Volketswil"),
]

GLOSSAR = [
    ("BESS", "Battery Energy Storage System, Batteriespeicher"),
    ("NEA", "Netzersatzanlage (Notstromaggregat)"),
    ("USV", "Unterbrechungsfreie Stromversorgung"),
    ("IST / L1-L5", "Integrated Systems Test, RZ-Gesamttest = Level 5"),
    ("kVA / MVA", "Scheinleistung (Nennleistung Generator)"),
    ("kW / MW", "Wirkleistung; bei cos phi 0,8: 1 MVA ≈ 0,8 MW"),
    ("IT-MW", "Elektrische Leistung der Server im RZ"),
    ("UW / GIS", "Unterwerk / gasisolierte Schaltanlage"),
    ("HS / MS / NS", "Hoch-, Mittel-, Niederspannung"),
    ("HVO", "Hydriertes Pflanzenöl, erneuerbarer Diesel"),
    ("TBM / BSA", "Tunnelbohrmaschine / Tunnel-Sicherheitstechnik"),
    ("RZ", "Rechenzentrum"),
    ("GU / TU / ARGE", "General-, Totalunternehmer / Arbeitsgemeinschaft"),
    ("IBN / PM", "Inbetriebnahme / Projektmanagement"),
    ("IVöB / simap", "Beschaffungsrecht / Ausschreibungsportal"),
    ("EMEA", "Europa, Nahost, Afrika: zentraler Einkauf"),
    ("GMP", "Good Manufacturing Practice (Pharma-Regeln)"),
    ("ASTRA / SBB", "Bundesamt für Strassen / Schweizerische Bundesbahnen"),
    ("EKZ / ewz / CKW / IWB", "Stromversorger Kt. Zürich, Stadt Zürich, Zentralschweiz, Basel"),
    ("KWO / KSA / USZ / KSSG", "Kraftwerke Oberhasli; Spitäler Aarau, Zürich, St.Gallen"),
    ("WEF / FIS / ESAF", "World Economic Forum / Ski-Weltverband / Schwingfest"),
    ("CRM / FX", "Kundendatenbank / Wechselkurs"),
]

# ================================================================ Erweiterung 29.09.2026: Events und EVU 2027
# Events: (name, kategorie, ort, region, datum, groesse, warum, gen_mva, gen_wo, bess_mw, bess_mo, anteil27, paket, quelle)
PK_SOM, PK_ROM, PK_WIN, PK_VOLK, PK_SPORT, PK_MARKT = (
    "Paket Sommer-Festivals 2027", "Paket Sommer-Festivals 2027",
    "Paket Winter-Sport 2026/27", "Paket Schwing- und Volksfeste 2027",
    "Paket Sport-Grossanlässe 2027", "Paket Märkte, Messen, Fasnacht, Zirkus")
EVENTS = [
    ("Greenfield Festival", "Musik", "Interlaken BE", "Mittelland/Bern", "10.-12.06.2027", "ca. 30'000/Tag, 3 Tage", "Flugplatz ohne Netz: Bühnen, Camping, Gastro", 3, 1.5, 0.5, 0.5, 1, PK_SOM, "https://www.interlaken.swiss/planen/events/top-events/greenfield-festival"),
    ("Open Air Gampel", "Musik", "Gampel-Bratsch VS", "West (Romandie)", "18.-22.08.2027", "bis 25'000/Tag, 4 Tage", "Offenes Gelände, mehrere Bühnen, Camping", 2.5, 1.5, 0, 0, 1, PK_SOM, "https://www.openairgampel.ch/en/home"),
    ("Heitere Open Air", "Musik", "Zofingen AG", "Nordwestschweiz", "06.-08.08.2027", "3 Tage", "Hügelplateau mit begrenzter Netzkapazität", 1.5, 1, 0, 0, 1, PK_SOM, "https://heitere.ch/"),
    ("Seaside Festival", "Musik", "Spiez BE", "Mittelland/Bern", "27.-28.08.2027", "2 Tage", "Temporäres Seeufer-Gelände", 1, 1, 0, 0, 1, PK_SOM, "https://www.seasidefestival.ch/"),
    ("SummerDays Festival", "Musik", "Arbon TG", "Ostschweiz", "27.-28.08.2027", "ca. 24'000 Besucher", "Seeufer-Gelände, Bühne, Foodcourt", 1, 1, 0, 0, 1, PK_SOM, "https://summerdays.ch/"),
    ("Lakelive Festival", "Musik/Kultur", "Biel/Nidau BE", "Mittelland/Bern", "Ende Juli 2027 (?)", "ca. 10 Tage", "Lange Laufzeit auf Brachgelände: BESS/Hybrid", 0.5, 2, 0.3, 0.5, 1, PK_SOM, "https://www.nidau.ch/"),
    ("Luzern Live", "Musik", "Luzern LU", "Zentralschweiz", "Juli 2027 (?)", "ca. 10 Tage, Seebühnen", "Innenstadt mit Lärmauflagen: BESS", 0.5, 2, 0.3, 0.5, 1, PK_SOM, "https://www.luzern-live.ch/"),
    ("Openair Lumnezia", "Musik", "Degen GR", "Ostschweiz", "22.-24.07.2027", "ca. 18'000 Besucher", "Abgelegenes Berggelände, schwaches Netz", 1, 1, 0, 0, 1, PK_SOM, "https://openair-lumnezia.ch/"),
    ("Zermatt Unplugged", "Musik", "Zermatt VS", "West (Romandie)", "06.-10.04.2027", "17 Bühnen, 5 Tage", "Bühnen am Berg, Zelte mit Heizbedarf", 1, 1.5, 0, 0, 1, PK_SOM, "https://zermatt-unplugged.ch/en/news/zermatt-unplugged-2027/"),
    ("Caribana Festival", "Musik", "Crans-près-Céligny VD", "West (Romandie)", "Mitte Juni 2027 (?)", "ca. 30'000, 4 Tage", "Hafengelände ohne ausreichende Einspeisung", 1.5, 1, 0, 0, 1, PK_ROM, "https://fr.wikipedia.org/wiki/Caribana_Festival_de_Crans"),
    ("Festi'neuch", "Musik", "Neuchâtel NE", "West (Romandie)", "10.-13.06.2027", "4 Tage", "Uferpark, mehrere Bühnen", 1, 1, 0, 0, 1, PK_ROM, "https://www.festivalabroad.com/festivals/festineuch"),
    ("Sion sous les étoiles", "Musik", "Sion VS", "West (Romandie)", "14.-17.07.2027", "4 Tage", "Freifläche beim Stadion", 1, 1, 0, 0, 1, PK_ROM, "https://www.valais.ch/en/events/sion-sous-les-etoiles"),
    ("JazzAscona", "Musik", "Ascona TI", "Tessin", "24.06.-03.07.2027", "10 Tage", "Mehrere Open-Air-Bühnen an der Promenade", 0.5, 2, 0, 0, 1, PK_ROM, "https://www.ticino.ch/en/events/details/jazzascona-2027/10042.html"),
    ("Estival Jazz Lugano", "Musik", "Lugano TI", "Tessin", "ca. 08.-10.07.2027 (?)", "3 Abende", "Platzbühne in der Stadt", 0.3, 1, 0, 0, 1, PK_ROM, "https://www.carnifest.com/estival-festival-jazz-in-lugano-2027/"),
    ("Polymanga", "Pop-Kultur", "Montreux VD", "West (Romandie)", "26.-29.03.2027", "über 50'000 Besucher", "Aussengelände Parc Vernex: Zelte, Heizung", 0.5, 1, 0, 0, 1, PK_ROM, "https://www.20min.ch/fr/story/lausanne-vd-succes-pour-polymanga-de-retour-en-2027-a-montreux-103542173"),
    ("LAAX OPEN", "Snowboard-Weltcup", "Laax GR", "Ostschweiz", "13.-16.01.2027", "ca. 250 Athleten, Konzerte", "Pipe am Berg, Bühne, beheizte Zelte", 1.5, 1.5, 0, 0, 1, PK_WIN, "https://www.graubuenden.ch/en/events/laax-open-2027"),
    ("Ski-Weltcup Frauen Lenzerheide", "Ski alpin", "Lenzerheide GR", "Ostschweiz", "19.-21.02.2027", "Weltcup-Comeback", "Zielarena, TV-Compound, Zelte", 1.5, 1.5, 0, 0, 1, PK_WIN, "https://www.weltcup-lenzerheide.ch/en"),
    ("Davos Nordic", "Langlauf-Weltcup", "Davos GR", "Ostschweiz", "11.-13.12.2026", "3 Renntage", "Stadion, TV, Wachskabinen", 0.5, 1, 0, 0, 0, PK_WIN, "https://www.davosnordic.ch/en"),
    ("Skisprung-Weltcup Engelberg", "Skispringen", "Engelberg OW", "Zentralschweiz", "18.-20.12.2026", "grösste Naturschanze", "Zielarena, TV, Zelte", 0.5, 1, 0, 0, 0, PK_WIN, "https://www.weltcup-engelberg.ch/en/"),
    ("Engadin Skimarathon", "Breitensport", "Maloja-S-chanf GR", "Ostschweiz", "07.-14.03.2027", "grösster CH-Breitensportanlass", "Start/Ziel über 42 km, Heizzelte", 1, 1.5, 0, 0, 1, PK_WIN, "https://www.engadin.ch/en/events/engadin-marathon-week-2027"),
    ("White Turf St. Moritz", "Pferdesport", "St. Moritz GR", "Ostschweiz", "07./14./21.02.2027", "3 Renntage, 120 Jahre", "Kein Netz auf dem See: alles mobil", 1, 4, 0, 0, 1, PK_WIN, "https://www.whiteturf.ch/en/"),
    ("Snow Polo St. Moritz", "Polo", "St. Moritz GR", "Ostschweiz", "22.-24.01.2027", "3 Tage", "VIP-Zelte und Heizung auf dem See", 0.5, 1, 0, 0, 1, PK_WIN, "https://www.snowpolo-stmoritz.com/tournament-2027/"),
    ("Eidg. Volksmusikfest", "Eidg. Fest", "Altstätten SG", "Ostschweiz", "09.-12.09.2027", "50'000-60'000 Besucher", "Festzelte und Bühnen in der Altstadt", 1.5, 1.5, 0, 0, 1, PK_VOLK, "https://www.swissinfo.ch/ger/eidg%C3%B6ssisches-volksmusikfest-2027-findet-in-altst%C3%A4tten-sg-statt/92042182"),
    ("Westschweizer Jodlerfest", "Regionalfest", "Château-d'Oex VD", "West (Romandie)", "02.-04.07.2027", "3 Tage", "Festzelte im Bergdorf", 0.5, 1, 0, 0, 1, PK_VOLK, "https://www.alphornpuma.ch/n%C3%A4chstejodlerfeste"),
    ("Bernisch-Kantonales Schwingfest", "Schwingen", "Thun BE", "Mittelland/Bern", "August 2027 (?)", "Teilverbandsfest", "Arena, Festzelte; Probelauf vor ESAF 2028", 1, 1, 0, 0, 1, PK_VOLK, "https://bksf2027.ch/"),
    ("Nordwestschweizer Schwingfest", "Schwingen", "Sissach BL", "Nordwestschweiz", "03.-04.07.2027", "119. Ausgabe", "Arena, Festzelt", 0.5, 1, 0, 0, 1, PK_VOLK, "https://www.nws2027.ch/"),
    ("Innerschweizer Schwingfest", "Schwingen", "Giswil OW", "Zentralschweiz", "04.07.2027", "Teilverbandsfest", "Arena auf offenem Feld", 0.5, 1, 0, 0, 1, PK_VOLK, "https://isaf2027.ch/"),
    ("Knabenschiessen", "Volksfest", "Zürich ZH", "Zürich", "11.-13.09.2027", "grosse Chilbi", "Lunapark, Spitzenlast und Backup", 1, 1, 0, 0, 1, PK_VOLK, "https://calendarena.com/schweiz/knabenschiessen/"),
    ("Sechseläuten (Gastkanton LU)", "Brauchtum", "Zürich ZH", "Zürich", "16.-19.04.2027", "4 Tage", "Gastkanton-Zelte auf dem Platz", 0.3, 1, 0, 0, 1, PK_VOLK, "https://www.limmattalerzeitung.ch/limmattal/zuerich/sechselaeuten-2027-luzern-ist-gastkanton-ld.4019514"),
    ("Ruder-WM Luzern", "Sport-WM", "Luzern (Rotsee) LU", "Zentralschweiz", "23.-29.08.2027", "über 40'000 Zuschauer, 70 Nationen", "TV-Compound, Tribünen, Zielturm: Redundanz", 2, 2, 0.5, 1, 1, PK_SPORT, "https://lucerne2027.com/"),
    ("Beachvolleyball-EM", "Sport-EM", "Gstaad BE", "Mittelland/Bern", "30.06.-04.07.2027", "5 Tage", "Temporäres Stadion, TV, Flutlicht", 1, 1.5, 0, 0, 1, PK_SPORT, "https://www.beachgstaad.ch/en/news-articles/em-2027"),
    ("CSIO St.Gallen", "Pferdesport", "St. Gallen SG", "Ostschweiz", "03.-06.06.2027", "4 Tage", "Freigelände, Tribünen, Hospitality, TV", 1, 1.5, 0, 0, 1, PK_SPORT, "https://www.csio.ch/de/Programm/Programm.html"),
    ("Swiss Open Gstaad", "Tennis", "Gstaad BE", "Mittelland/Bern", "10.-18.07.2027", "9 Tage", "Tribünen, Hospitality, TV", 0.5, 2, 0, 0, 1, PK_SPORT, "https://swissopengstaad.ch/?lang=en"),
    ("IRONMAN Switzerland", "Ausdauersport", "Thun BE", "Mittelland/Bern", "04.07.2027", "Langdistanz", "Wechselzone, Zielarena, Zeitmessung", 0.5, 1, 0, 0, 1, PK_SPORT, "https://www.finishers.com/en/event/ironman-switzerland-thun"),
    ("Tour de Suisse", "Radsport", "Etappenorte CH", "national", "16.-20.06.2027", "5 Tage", "Start/Ziel-Zonen mit TV, täglich neuer Ort", 1, 1.5, 0, 0, 1, PK_SPORT, "https://www.tourdesuisse.ch/en/"),
    ("Tour de Romandie", "Radsport", "Romandie", "West (Romandie)", "27.04.-02.05.2027", "6 Tage", "Start/Ziel-Zonen mit TV", 0.5, 1.5, 0, 0, 1, PK_SPORT, "https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/tour-de-romandie-etape-romont/"),
    ("Weltklasse Zürich", "Leichtathletik", "Zürich ZH", "Zürich", "25.-26.08.2027", "Diamond League", "Stadtwettkampf, TV, Hospitality", 0.5, 1, 0, 0, 1, PK_SPORT, "https://www.trackathletes.ie/meeting/weltklasse-zurich-zurich-diamond-league_2027/"),
    ("Athletissima", "Leichtathletik", "Lausanne VD", "West (Romandie)", "August 2027 (?)", "1-2 Tage", "Hospitality, TV, Backup", 0.3, 1, 0, 0, 1, PK_SPORT, "https://athletissima.ch/en/"),
    ("OL-EM 2027", "Sport-EM", "Thun BE", "Mittelland/Bern", "28.09.-03.10.2027", "Stadt-Sprints", "Arena, Zeitmessung, TV", 0.3, 1, 0, 0, 1, PK_SPORT, "https://www.swiss-orienteering.ch/de/news/verband/3075-ol-europameisterschaften-2027-in-der-schweiz.html"),
    ("Eiskunstlauf-EM", "Sport-EM", "Lausanne VD", "West (Romandie)", "27.-31.01.2027", "Halle", "Nur TV-Compound, Aussenzelte, Backup", 0.3, 1, 0, 0, 1, PK_SPORT, "https://vaudoisearena.ch/en/events/isu-figure-skating-european-championships-2027"),
    ("CHI Genève", "Pferdesport", "Genève GE", "West (Romandie)", "09.-13.12.2026", "Rolex Grand Slam", "Stallzelte, Aussenbereiche, Backup", 0.5, 1.5, 0, 0, 0, PK_SPORT, "https://horserizon.com/chi-geneve-100-ans/"),
    ("Grand-Prix von Bern / Frauenlauf", "Laufsport", "Bern BE", "Mittelland/Bern", "15.05. / 13.06.2027", "bis 15'000 Teilnehmende", "Start/Ziel-Arena, Zeitmessung", 0.3, 1, 0, 0, 1, PK_SPORT, "https://gpbern.ch/"),
    ("Circus Knie Tournee", "Zirkus", "ganze Schweiz", "national", "ab März 2027 (?)", "neues Zelt 2027", "Einspeisung oder Backup je Gastspiel", 0.5, 20, 0, 0, 1, PK_MARKT, "https://www.knie.ch/circus/tournee-2027"),
    ("BEA", "Messe", "Bern BE", "Mittelland/Bern", "30.04.-09.05.2027", "10 Tage", "Aussengelände, Zelte, Gastro", 0.5, 2, 0, 0, 1, PK_MARKT, "https://www.myswitzerland.com/de-ch/erlebnisse/veranstaltungen/bea-2027/"),
    ("LUGA", "Messe", "Luzern LU", "Zentralschweiz", "30.04.-09.05.2027", "10 Tage", "Aussenzelte, Chilbi", 0.3, 2, 0, 0, 1, PK_MARKT, "https://www.luga.ch/de"),
    ("OLMA", "Messe", "St. Gallen SG", "Ostschweiz", "Oktober 2027 (?)", "11 Tage", "Aussengelände, Arena, Zelte", 0.5, 2, 0, 0, 1, PK_MARKT, "https://www.olma-messen.ch/"),
    ("Tier&Technik", "Agrarmesse", "St. Gallen SG", "Ostschweiz", "25.-28.02.2027", "4 Tage", "Tierzelte im Winter, Heizung", 0.3, 1, 0, 0, 1, PK_MARKT, "https://www.ufarevue.ch/agenda/tier-technik-2027"),
    ("AGRAMA", "Landtechnik-Messe", "Bern BE", "Mittelland/Bern", "26.-30.11.2026", "5 Tage", "Zelte im November, Heizung", 0.3, 1, 0, 0, 0, PK_MARKT, "https://agrama.ch/"),
    ("Montreux Noël", "Weihnachtsmarkt", "Montreux VD", "West (Romandie)", "20.11.-24.12.2026", "über 170 Chalets", "5 Wochen Chalets, Licht, Heizung", 0.5, 5, 0, 0, 0, PK_MARKT, "https://www.montreuxriviera.com/en/E1141/montreux-riviera-noel"),
    ("Bellevue Noël (neu)", "Weihnachtsmarkt", "Zürich ZH", "Zürich", "19.11.-23.12.2026", "1. Ausgabe, neuer Betreiber", "Neues Stromkonzept: Einstiegschance", 0.5, 5, 0, 0, 0, PK_MARKT, "https://www.nume.ch/wienachtsdorf-zuerich-2026-heisst-neu-bellevue-noel-termine/"),
    ("Basler Weihnachtsmarkt", "Weihnachtsmarkt", "Basel BS", "Nordwestschweiz", "26.11.-23.12.2026", "ca. 150 Chalets", "Zusatzlast und Backup", 0.3, 4, 0, 0, 0, PK_MARKT, "https://www.bs.ch/pd/marketing/messenundmaerkte/weihnachtsmarkt"),
    ("Murten Licht-Festival", "Lichtfestival", "Murten FR", "West (Romandie)", "20.-31.01.2027", "12 Tage", "Leise BESS für Lichtinstallationen", 0.2, 2, 0.2, 0.5, 1, PK_MARKT, "https://www.murtenlichtfestival.ch/"),
    ("Basler Fasnacht", "Brauchtum", "Basel BS", "Nordwestschweiz", "15.-18.02.2027", "72 Stunden", "Beizen, Bühnen, Laternen", 0.5, 1, 0, 0, 1, PK_MARKT, "https://www.bazonline.ch/morgestraich-2027-basler-fasnacht-startet-in-377-tagen-797546696425"),
    ("Luzerner Fasnacht", "Brauchtum", "Luzern LU", "Zentralschweiz", "04.-09.02.2027", "6 Tage", "Bühnen, Barzelte, Beleuchtung", 0.5, 1, 0, 0, 1, PK_MARKT, "https://www.lfk.ch/informationen/fasnachtstermine-bis-2060"),
    ("Rabadan Bellinzona", "Carnevale", "Bellinzona TI", "Tessin", "04.-09.02.2027", "6 Tage", "Festzelte mit Heizung", 0.5, 1, 0, 0, 1, PK_MARKT, "https://www.bellinzonaevalli.ch/en/events/details/rabadan-carnival-in-bellinzona/11276.html"),
    ("Geneva AI Summit 2027", "Konferenz", "Genève GE", "West (Romandie)", "21.-22.06.2027", "über 100 Länder", "Hohe Sicherheitsstufe: Netzersatz und USV", 2, 2, 0.5, 1, 1, "einzeln", "https://www.bakom.admin.ch/en/geneva-ai-summit-2027-international-summit-on-artificial-intelligence-in-geneva"),
]
EV_P = 0.15   # Gewinnchance für Event-Pakete
EV_PAKETE = [PK_WIN, PK_SOM, PK_VOLK, PK_SPORT, PK_MARKT]
TOP_MIN = 50000   # Schwelle Top-Player

# EVU / Energie: (name, betreiber, ort, region, zeitfenster, groesse, warum, gen_mva, gen_wo, lb_mw, lb_wo, bess_mw, bess_mo, anteil27, p, gruppe, quelle)
# gruppe: "Top" = einzeln in Top-Player, PK_SOLAR = Paket, "" = nur EVU-Blatt
PK_SOLAR = "Paket Alpine Solar-Baustellen 2027"
EVU = [
    ("UW Mörel (380-kV-GIS, neuer Trafo)", "Swissgrid", "Mörel VS", "West (Romandie)", "Umbau ab 2027", "380/220 kV", "Baustrom im Bergtal, Eigenbedarf, Lastbank für Trafo/GIS-Tests", 1, 26, 2, 2, 0, 0, 0.6, 0.15, "Top", "https://www.swissgrid.ch/en/home/projects/project-overview/moerel-ulrichen.html"),
    ("Leitung Innertkirchen-Ulrichen (Grimseltunnel)", "Swissgrid", "Oberhasli BE / Goms VS", "Mittelland/Bern", "Bau frühestens 2027, fertig 2034", "220 auf 380 kV, 27 km", "Baustrom an Tunnel- und Leitungsbaustellen ohne Netz", 1, 20, 0, 0, 0, 0, 0.3, 0.10, "Top", "https://www.swissgrid.ch/en/home/projects/project-overview/innertkirchen-ulrichen.html"),
    ("Poste Galmiz (Neubau, Verkabelung 125 kV)", "Groupe E / Swissgrid", "Galmiz FR", "West (Romandie)", "Bau ab H2 2025, IBN Ende 2028", "CHF 53 Mio., 220/125 kV", "Netzersatz und mobiler Trafo bei Umschaltungen, Baustrom", 2, 10, 0, 0, 0, 0, 1.0, 0.20, "Top", "https://www.groupe-e.ch/fr/decouvrir-groupe-e/medias/communiques-de-presse/renouvellement-poste-galmiz"),
    ("UW Laax (Gesamterneuerung)", "Repower", "Laax GR", "Ostschweiz", "07/2025 bis Ende 2027", "CHF 8,4 Mio.", "Skigebiet hängt am UW: Netzersatz im Winter kritisch", 2, 8, 0, 0, 0, 0, 1.0, 0.20, "Top", "https://www.repower.com/ch/medienmitteilungen/uwlaax"),
    ("Neues UW Aarau", "Eniwa", "Aarau AG", "Nordwestschweiz", "Bau ab 11/2025, Umschaltung Sommer 2029", "110/16 kV, ca. 40'000 Einwohner", "Etappenumschaltungen, mobiler Trafo, Baustrom", 2, 6, 0, 0, 0, 0, 0.5, 0.20, "Top", "https://netzbetreiberinfo.ch/unternehmen/projekte/eniwa-spatenstich-neues-unterwerk-aarau-bis-2029"),
    ("Ersatzneubau UW Steinachstrasse", "St.Galler Stadtwerke", "St. Gallen SG", "Ostschweiz", "Baustart Anfang 2027, IBN Ende 2030", "Innenstadt-UW", "Provisorien und Netzersatz beim Rückbau, Baustrom", 1, 16, 0, 0, 0, 0, 0.5, 0.20, "Top", "https://www.stadt.sg.ch/news/stsg_medienmitteilungen/2025/06/ersatzneubau-unterwerk-steinachstrasse--wettbewerbssieger-gekuer.html"),
    ("Kraftwerk Ritom (Neubau)", "SBB / AET", "Quinto TI", "Tessin", "IBN 2027", "2 × 60 MW Turbinen, CHF 250 Mio.", "Eigenbedarf und Tests bei der IBN, Baustrom", 1, 12, 0, 0, 0, 0, 1.0, 0.15, "Top", "https://company.sbb.ch/de/bahnentwicklung/projekte/tessin/ritom.html"),
    ("Reservekraftwerk Sisslerfeld 1 und Stein (HVO)", "GETEC", "Eiken / Stein AG", "Nordwestschweiz", "IBN Eiken Anfang 2027, Stein 2028", "13 MW + 44 MW", "Lastbank für Abnahme- und Leistungstests, Baustrom", 0.5, 8, 13, 2, 0, 0, 0.8, 0.20, "Top", "https://www.getec.swiss/de/media/news/getec-schweiz-macht-die-energieversorgung-nachhaltig-sicher.php"),
    ("KKW-Revisionen 2027 (Beznau, Leibstadt, Gösgen)", "Axpo / KKL / KKG", "Döttingen, Leibstadt AG; Däniken SO", "Nordwestschweiz", "Beznau März-Mai und ab Aug., Leibstadt Apr.-Mai, Gösgen Ende Mai-Juni (Muster, Termine 2027 offen)", "2 × 365 MW, 1'200 MW, 1'010 MW", "Baustrom für Revisionsdörfer, Ersatz für Hilfssysteme (strenge Auflagen)", 1, 27, 0, 0, 0, 0, 1.0, 0.10, "Top", "https://www.axpo.com/ch/de/newsroom/medienmitteilungen/2026/das-kernkraftwerk-beznau-hat-die-revision-von-block-1-fristgerecht-beendet.html"),
    ("CoolCity: Energiezentrale UW Selnau, Microtunnel", "ewz", "Zürich ZH", "Zürich", "Microtunnel ab 2027, Hauptphase 2027-2032", "ca. CHF 300 Mio.", "Baustrom für Tunnelbohrmaschine, Umbau im Bestand", 1.5, 26, 0, 0, 0, 0, 0.5, 0.15, "Top", "https://www.ewz.ch/de/geschaeftskunden/immobilien/referenzen-projekte/seewasserverbunde-zuerichsee/coolcity.html"),
    ("Madrisa Solar", "Repower / EKZ / Klosters", "Klosters GR", "Ostschweiz", "voll Ende 2027", "11 MWp", "Baustrom auf 2'000 m ohne Netz", 0.5, 20, 0, 0, 0, 0, 1.0, 0.15, PK_SOLAR, "https://www.repower.com/ch/ueber-uns/unsere-projekte/madrisa-solar-alpines-solarkraftwerk"),
    ("Sedrun Solar", "Axpo u.a. (?)", "Tujetsch GR", "Ostschweiz", "80 % Ende 2027", "19,3 MW", "Baustrom über die Bausaison", 0.5, 20, 0, 0, 0, 0, 1.0, 0.15, PK_SOLAR, "https://sedrun-solar.ch/"),
    ("NalpSolar", "Axpo", "Lai da Nalps GR", "Ostschweiz", "Bau bis 12/2028", "ca. 8 MW", "Baustrom", 0.3, 20, 0, 0, 0, 0, 1.0, 0.15, PK_SOLAR, "https://www.axpo.com/ch/de/energie/produktion-und-verteilung/solarenergie/nalpsolar.html"),
    ("Solarkraftwerk Samedan", "Energia Solara Engiadinaisa", "Samedan GR", "Ostschweiz", "Baustart Frühling 2027", "18,8 GWh/a", "Baustrom, Neustart ideal für Akquise", 0.5, 20, 0, 0, 0, 0, 1.0, 0.15, PK_SOLAR, "https://www.ee-news.ch/de/article/57584/solarkraftwerk-samedan-baubewilligung-liegt-vor-flache-wiehalbiert"),
    ("Grengiols Solar (mit UW Heiligkreuz)", "Grengiols Solar (EnBAG/FMV/IWB)", "Saflischtal VS", "West (Romandie)", "Etappen 2026-2027+ (?)", "redimensioniert (?)", "Baustrom, UW-IBN", 0.5, 20, 0, 0, 0, 0, 1.0, 0.15, PK_SOLAR, "https://www.grengiols-solar.ch/de/umsetzung"),
    ("Belalp Solar", "Naters / EnBAG / FMV / Alpiq", "Naters VS", "West (Romandie)", "Bau 2026/27 (?)", "12 GWh/a", "Baustrom im Hochgebirge", 0.3, 16, 0, 0, 0, 0, 1.0, 0.15, PK_SOLAR, "https://www.baublatt.ch/bauprojekte/photovoltaikanlage-belalp-solar-erhaelt-zustimmung-36813"),
    ("Leitung Obfelden-Samstagern", "Swissgrid", "Thalwil/Obfelden ZH", "Zürich", "Bau läuft, Spannungserhöhung ab 2027", "150 auf 220 kV", "Baustrom Mastbau, Netzersatz", 0.5, 20, 0, 0, 0, 0, 1.0, 0.15, "", "https://www.swissgrid.ch/en/home/projects/project-overview/obfelden-samstagern.html"),
    ("UW Niederwil und Leitung Niederwil-Obfelden", "Swissgrid", "Niederwil AG", "Nordwestschweiz", "UW-Bau läuft (?), Leitung ab 2028", "CHF 97 Mio., 380 kV", "Eigenbedarf bei UW-Umschaltung", 0.5, 12, 0, 0, 0, 0, 1.0, 0.15, "", "https://www.swissgrid.ch/en/home/projects/project-overview/niederwil-obfelden.html"),
    ("Bickigen-Chippis (Gemmileitung)", "Swissgrid", "BE/VS", "Mittelland/Bern", "Bauplan offen (?)", "106 km, 380 kV", "Baustrom an abgelegenen Masten", 0.5, 20, 0, 0, 0, 0, 0.5, 0.10, "", "https://www.swissgrid.ch/en/home/projects/project-overview/bickigen-chippis.html"),
    ("Poste Puidoux (Totalumbau)", "Romande Energie", "Puidoux VD", "West (Romandie)", "2024-2027", "40 auf 80 MVA", "Mobiler Trafo oder Netzersatz beim Trafotausch", 1, 8, 0, 0, 0, 0, 1.0, 0.20, "", "https://www.romande-energie.ch/blog/moderniser-les-postes-electriques-haute-et-moyenne-tension-pour-relever-les-defis-energetiques"),
    ("Sous-station Sion (Ronquoz 21)", "OIKEN", "Sion VS", "West (Romandie)", "Umschaltung ab Anfang 2027", "CHF 20 Mio.", "Netzersatz und Lastbank bei IBN", 1.5, 6, 1, 1, 0, 0, 1.0, 0.20, "", "https://oiken.ch/medias/nouvelle-sous-station-electrique-de-sion-debut-des-travaux-dans-le-nouveau-quartier-de-ronquoz-21/"),
    ("Poste Collex-Bossy (Auflage 09/2026)", "SIG", "Collex-Bossy GE", "West (Romandie)", "Bau 2027/28 (?)", "unbekannt", "Baustrom, Umschaltung", 1, 6, 0, 0, 0, 0, 0.3, 0.15, "", "https://collex-bossy.ch/fr/actualites/enquete-publique-nouveau-poste-de-transformation-electrique-2684"),
    ("UW Thun (Ersatzneubau)", "Energie Thun", "Thun BE", "Mittelland/Bern", "Bau 2027+ (?)", "unbekannt", "Provisorium beim Rückbau", 1, 8, 0, 0, 0, 0, 0.3, 0.15, "", "https://konkurado.ch/de/unterwerk-thun-planungsarbeiten-inkl-bim-ab-phase-32"),
    ("110-kV-Kabel Freienbach-Altendorf", "Axpo Grid", "Freienbach SZ", "Zentralschweiz", "Bau ab 05/2026", "8,1 km", "Netzersatz bei Umschaltung", 1, 6, 0, 0, 0, 0, 1.0, 0.15, "", "https://www.axpo.com/ch/de/newsroom/medienmitteilungen/2026/start-of-construction-of-underground-cable-line-from-freienbach-.html"),
    ("UW Beznau (50 auf 110 kV)", "Axpo Grid", "Döttingen AG", "Nordwestschweiz", "läuft (?)", "50 auf 110 kV", "Eigenbedarf, Netzersatz", 1, 6, 0, 0, 0, 0, 1.0, 0.15, "", "https://amreinbau.ch/referenzen/axpo-uw-beznau-doettingen/"),
    ("UW Mettlen (2. 800-MVA-Trafo)", "Swissgrid", "Eschenbach LU", "Zentralschweiz", "Restarbeiten 2027 (?)", "2 × 800 MVA", "Lastbank oder Eigenbedarf bei Tests", 1, 2, 2, 1, 0, 0, 1.0, 0.15, "", "https://www.swissgrid.ch/en/home/newsroom/newsfeed/20221020-01.html"),
    ("UW Bözingenfeld", "ESB", "Biel BE", "Mittelland/Bern", "IBN 2026 (Verzug?)", "Industriequartier", "Lastbank bei IBN", 1, 2, 1, 1, 0, 0, 0.5, 0.15, "", "https://www.esb.ch/de/esb/projekte/unterwerk-bozingenfeld/"),
    ("BESS UW Fadenbrücke Buochs", "EWN", "Buochs NW", "Zentralschweiz", "IBN Spätsommer 2027", "12,5 MW / 25 MWh", "Tests bei IBN, Baustrom", 0.5, 8, 2, 1, 0, 0, 1.0, 0.15, "", "https://www.ewn.ch/baustart-grossbatteriespeicher"),
    ("BESS UW Grosshöchstetten", "BKW", "Grosshöchstetten BE", "Mittelland/Bern", "IBN Q3 2027", "20 MW / 50 MWh", "Tests bei IBN, Baustrom", 0.5, 8, 2, 1, 0, 0, 1.0, 0.15, "", "https://www.bkw.ch/de/ueber-uns/aktuell/medien/medienmitteilungen/bkw-sichert-netzkapazitaet-von-400-mw-fuer-grossbatterieprojekt-in-muehleberg"),
    ("BESS Bubikon", "EKZ (?)", "Bubikon ZH", "Zürich", "Betrieb 07/2027", "4,5 MW / ca. 10 MWh", "Tests bei IBN", 0.3, 6, 1, 1, 0, 0, 1.0, 0.15, "", "https://bess-bubikon.ch/dokumente/BESS-Bubikon_Faktenblatt.pdf"),
    ("Grossbatterie Mühleberg", "BKW", "Mühleberg BE", "Mittelland/Bern", "Bau ca. 2028/29, IBN 2030", "400 MW / 800 MWh", "Baustrom, IBN-Tests (später)", 1, 26, 0, 0, 0, 0, 0.0, 0.10, "", "https://www.bkw.ch/de/ueber-uns/aktuell/medien/medienmitteilungen/bkw-sichert-netzkapazitaet-von-400-mw-fuer-grossbatterieprojekt-in-muehleberg"),
    ("KW Reckingen (Maschinengruppen)", "Kraftwerk Reckingen AG", "Reckingen AG", "Nordwestschweiz", "1. Gruppe ab 04/2027", "Rheinkraftwerk", "Eigenbedarf bei Stillständen", 1, 8, 0, 0, 0, 0, 1.0, 0.15, "", "https://www.andritz.com/hydro-en/about-andritz-hydro/locations/switzerland/switzerland-de/local-news-switzerlande-de"),
    ("Wasserkraftwerk Mühleberg (Erneuerung)", "BKW", "Mühleberg BE", "Mittelland/Bern", "Bau ab 2028", "CHF 120 Mio.", "Baustrom (später)", 1, 20, 0, 0, 0, 0, 0.0, 0.10, "", "https://www.schweiz.biz/2025/09/04/wasserkraftwerk-muehleberg-mehr-leistung-bessere-umweltvertraeglichkeit/"),
    ("Reserve-Prüfstand GT26 Birr", "Ansaldo Energia / Bund", "Birr AG", "Nordwestschweiz", "bereit ab 02/2027", "250 MW", "Hilfsaggregate, Tests (?)", 1, 4, 0, 0, 0, 0, 1.0, 0.10, "", "https://www.bfe.admin.ch/de/newnsb/Nk4rqyiPm12q3-ya39iPf"),
    ("Reservekraftwerk Sisslerfeld 2 (HVO)", "Sidewinder", "Eiken AG", "Nordwestschweiz", "IBN 2027-2030 (?)", "180 MW", "Lastbank für Abnahme (unsicher)", 0.5, 8, 20, 2, 0, 0, 0.2, 0.10, "", "https://www.news.admin.ch/de/newnsb/yNgfnQ6o9l7doYlqLOqF5"),
    ("Reservekraftwerk Auhafen (HVO)", "Axpo", "Muttenz BL", "Nordwestschweiz", "Bau 2028-2030", "291 MW", "Baustrom, Lastbank (später)", 1, 26, 0, 0, 0, 0, 0.0, 0.10, "", "https://www.cash.ch/news/axpo-unterzeichnet-vertrag-fur-reservekraftwerk-in-muttenz-944930"),
    ("GuD Forsthaus als Reserve", "ewb", "Bern BE", "Mittelland/Bern", "Reserve ab Winter 2026/27", "50 MW el.", "Tests (?)", 0.5, 2, 0, 0, 0, 0, 1.0, 0.10, "", "https://www.bfe.admin.ch/de/newnsb/iDoyQnC8QMyfYoJMgJG61"),
    ("Fernwärmezentrale Zollikon", "Werke am Zürichsee / Energie 360°", "Zollikon ZH", "Zürich", "IBN Frühling 2027", "Seewasser-Wärmepumpe", "Baustrom, Überbrückung; Cross-Sell mobile Heizung", 0.5, 8, 0, 0, 0, 0, 1.0, 0.15, "", "https://www.zollikon.ch/aktuellesinformationen/2815189"),
    ("Fernwärme Kleinbasel / Heizzentrale Dellen", "IWB", "Basel BS", "Nordwestschweiz", "bis Ende 2027", "60 km Ausbau bis 2037", "Baustrom; Cross-Sell mobile Heizzentralen (MiT-Kern)", 0.5, 8, 0, 0, 0, 0, 1.0, 0.15, "", "https://www.iwb.ch/servicecenter/bau-anlagenprojekte/fernwaermeausbau-wettstein"),
    ("GeniLac Rive / Eaux-Vives", "SIG", "Genève GE", "West (Romandie)", "2025 bis Frühling 2028", "Seewassernetz", "Baustrom in der Innenstadt", 0.5, 12, 0, 0, 0, 0, 1.0, 0.15, "", "https://www.swissinfo.ch/fre/les-sig-d%C3%A9marrent-une-nouvelle-%C3%A9tape-du-chantier-genilac-%C3%A0-rive/90897660"),
    ("Elektrolyse Stahl Gerlafingen", "Alpiq / Stahl Gerlafingen", "Gerlafingen SO", "Mittelland/Bern", "frühestens 2027, Entscheid offen (?)", "bis 30 MW", "Tests bei IBN (unsicher)", 0.5, 6, 2, 1, 0, 0, 0.3, 0.10, "", "https://www.energate-messenger.ch/news/240452/alpiq-und-stahl-gerlafingen-mit-gemeinsamem-wasserstoffprojekt"),
]


def _pot(gm, gw, lm, lw, bm, bmo):
    return gm * gw * rate_gen() + lm * lw * rate_lb() + bm * bmo * rate_bess()


def _paket_row(name, members, seg, reg, bed, cs, step, hint, src, p):
    """Paket als Top-Player-Zeile: 1 MVA × Summe MVA-Wochen, 1 MW × Summe BESS-Monate, gewichteter Anteil 2027."""
    mvaw = sum(m["gm"] * m["gw"] for m in members)
    lbw = sum(m["lm"] * m["lw"] for m in members)
    bmo = sum(m["bm"] * m["bmo"] for m in members)
    pots = [(_pot(m["gm"], m["gw"], m["lm"], m["lw"], m["bm"], m["bmo"]), m["a27"]) for m in members]
    tot = sum(x for x, _ in pots)
    a27 = round(sum(x * a for x, a in pots) / tot, 3) if tot else 0
    anl = f"{len(members)} Anlässe/Baustellen: " + ", ".join(m["name"] for m in members)
    return (seg, name, "mehrere, siehe Detailblatt", "diverse", "div.", reg, "DE/FR/IT", anl, bed,
            1, round(mvaw, 2), 1 if lbw else 0, round(lbw, 2), 1 if bmo else 0, round(bmo, 2), a27, p, cs, step, src, hint)


_ev = [dict(name=e[0], gm=e[7], gw=e[8], lm=0, lw=0, bm=e[9], bmo=e[10], a27=e[11], pk=e[12]) for e in EVENTS]
_pk_info = {
    PK_WIN: ("Ostschweiz", "Generatoren und Heizung am Berg, Zelte, TV", "Zeltheizung, Heizzentralen", "Weisse Arena (Laax), OK Lenzerheide, White Turf jetzt kontaktieren: Aufbau Dez./Jan."),
    PK_SOM: ("national", "Generatoren und BESS-Hybrid für Bühnen, Camping, Gastro", "Kühlung Gastro", "Veranstalter im Winter ansprechen, Offerten bis März; Romandie/Tessin auf FR/IT"),
    PK_VOLK: ("national", "Festzelte, Arenen, Chilbi: Generatoren und Backup", "Zeltheizung im September", "OKs Altstätten, Thun, Sissach, Giswil ab Q1 2027"),
    PK_SPORT: ("national", "TV-Compounds mit Redundanz, Tribünen, Hospitality", "Klima Hospitality", "Ruder-WM Luzern zuerst (TV-Redundanz), dann Gstaad, CSIO"),
    PK_MARKT: ("national", "Chalets, Zelte, Chilbi, Zirkus: Backup und Zusatzlast", "Zeltheizung, Heizung Chalets", "Bellevue Noël (neuer Betreiber) sofort, Knie für Saison 2027"),
}
PAKET_TOP = {}
for _pk in EV_PAKETE:
    _m = [x for x in _ev if x["pk"] == _pk]
    reg, bed, cs, step = _pk_info[_pk]
    _row = (_paket_row(_pk, _m, EVT, reg, bed, cs, step, "Paket-Szenario = Summe der Einzel-Events im Blatt «Events 2027».",
                        "https://lucerne2027.com/" if _pk == PK_SPORT else EVENTS[[e[0] for e in EVENTS].index(_m[0]["name"])][13], EV_P))
    _pt = _pot(1, _row[10], _row[11], _row[12], _row[13], _row[14])
    PAKET_TOP[_pk] = _pt >= TOP_MIN
    if PAKET_TOP[_pk]:
        P.append(_row)

for e in EVU:
    if e[15] == "Top":
        P.append((NETZ, e[0], e[1], e[2], "", e[3], "DE/FR/IT", f"{e[4]}. {e[5]}", e[6],
                  e[7], e[8], e[9], e[10], e[11], e[12], e[13], e[14], "", "Projektleitung kontaktieren, Umschalt- bzw. Bauplan 2027 klären", e[16], ""))
_sol = [dict(name=e[0], gm=e[7], gw=e[8], lm=e[9], lw=e[10], bm=e[11], bmo=e[12], a27=e[13]) for e in EVU if e[15] == PK_SOLAR]
P.append(_paket_row(PK_SOLAR, _sol, NETZ, "Ostschweiz", "Baustrom auf 2'000 bis 2'700 m ohne Netz, ganze Bausaison",
                    "Bauheizung, Trocknung", "Bauherren und GU der Solar-Express-Anlagen ab Q1 2027 ansprechen",
                    "Paket-Szenario = Summe der Solar-Baustellen im Blatt «EVU & Energie 2027».",
                    "https://www.repower.com/ch/ueber-uns/unsere-projekte/madrisa-solar-alpines-solarkraftwerk", 0.15))
PAKET_TOP[PK_SOLAR] = True
PAKETE = [k for k in EV_PAKETE + [PK_SOLAR] if PAKET_TOP[k]]

PLAN += [
    ("Oktober", "09.10.2026", "Neuer Betreiber, Stromkonzept und Backup anbieten (Start 19.11.)", "Paket Märkte, Messen, Fasnacht, Zirkus"),
    ("Oktober", "16.10.2026", "Netzersatz für Winter 2026/27 anbieten (Skigebiet hängt am UW)", "UW Laax (Gesamterneuerung)"),
    ("Oktober", "23.10.2026", "Laax Open, Lenzerheide, White Turf kontaktieren: Aufbau Dez./Jan. (Paket knapp unter CHF 50'000)", "alle"),
    ("November", "06.11.2026", "Groupe E Netzbau: Umschaltplan 2027 und Trafo-/Netzersatzbedarf", "Poste Galmiz (Neubau, Verkabelung 125 kV)"),
    ("November", "13.11.2026", "Lastbank für Abnahmetests Anfang 2027 offerieren", "Reservekraftwerk Sisslerfeld 1 und Stein (HVO)"),
    ("November", "27.11.2026", "OK kontaktieren: TV-Compound, Redundanz, Hospitality", "Paket Sport-Grossanlässe 2027"),
    ("Januar", "29.01.2027", "Festival-Veranstalter für Saison 2027 ansprechen", "Paket Sommer-Festivals 2027"),
]
