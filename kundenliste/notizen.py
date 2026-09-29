# -*- coding: utf-8 -*-
"""Sprechernotizen je Folie: Botschaft, Formulierung, Rückfragen, Abkürzungen.
Zahlen kommen aus build_deck_power.py (Parameter n), damit Notizen und Folien übereinstimmen."""


def build_notes(n):
    def blk(botschaft, sagen, fragen, abk):
        out = ["BOTSCHAFT", botschaft, "", "SO SAGST DU ES", sagen]
        if fragen:
            out += ["", "WENN GEFRAGT WIRD"] + [f"F: {q}\nA: {a}" for q, a in fragen]
        if abk:
            out += ["", "ABKÜRZUNGEN AUF DIESER FOLIE", abk]
        return "\n".join(out)

    return [
        # 1 Cover
        blk("Wir haben den Schweizer Markt für mobile Power ab CHF 50'000 pro Projekt neu vermessen.",
            f"«Ich zeige euch {n['n']} Projekte mit zusammen {n['pot']} CHF Mietpotenzial. Realistisch für 2027 sind "
            f"{n['exp']} CHF. Jede Zahl steckt in der Excel und rechnet mit unseren Sätzen neu.»",
            [("Woher kommen die Zahlen?", "Öffentliche Quellen (Medienmitteilungen, Baublatt, Betreiber), Stand 27.09.2026. Mietsätze sind Markt-Richtwerte, keine MiT-Preise.")],
            "MiT = Mobil in Time AG. CHF-Beträge sind Miete ohne Transport, Service, Treibstoff."),
        # 2 Kurzfassung
        blk("Brutto ist das Maximum, die Erwartung ist die Planzahl.",
            "«Erwartung heisst: Potenzial mal Anteil, der 2027 anfällt, mal unsere Gewinnchance. "
            f"{n['na']} Projekte liegen über CHF 25'000 Erwartung, das ist Prio A.»",
            [("Warum so tief gegenüber brutto?", "Weil wir nicht alles gewinnen und manches erst 2028 abgerechnet wird. Die Gewinnchancen liegen je Projekt zwischen 10 und 30 %."),
             ("Was fehlt im Potenzial?", "Trafo-Miete, Transport, Montage, Service und Treibstoff. Die Zahl ist also eher zu tief.")],
            "Prio A = Erwartung 2027 ab CHF 25'000. Prio B = ab CHF 10'000. RZ = Rechenzentrum."),
        # 3 Treiber
        blk("Rechenzentren wachsen schneller als das Stromnetz. Die Lücke füllen wir.",
            "«EKZ hat über 100 Anschlussanfragen von Rechenzentren. Die Gebäude stehen, bevor das Unterwerk fertig ist. "
            "Und jedes RZ muss vor dem Start unter Volllast getestet werden: Das ist unser Lastbank-Geschäft.»",
            [("Was ist ein IST konkret?", "Integrated Systems Test: Strom, Kühlung und Notstrom laufen gemeinsam auf Design-Last, das Netz wird getrennt, Fehler werden simuliert. Typisch 4 bis 6 Wochen."),
             ("Wer bestellt die Lastbank?", "Meist der Commissioning-Manager des Betreibers oder der GU, selten der Elektroinstallateur.")],
            "RZ = Rechenzentrum. UW = Unterwerk. BESS = Batteriespeicher. IST = Integrated Systems Test. "
            "MW = Megawatt (Wirkleistung). Vornetz = übergeordnetes Netz von Axpo/Swissgrid."),
        # 4 Portfolio
        blk("Fünf Produkte, jedes mit einem klaren Einsatzfeld.",
            "«Generator ist der Türöffner, Lastbank ist das RZ-Produkt, BESS gewinnt überall, wo es leise sein muss, "
            "der mobile Trafo ist das Netzprodukt. Den NEA-Test verkaufen wir an Spitäler, Industrie und Facility Manager.»",
            [("Trafos haben wir?", "Bei MiT nicht belegt, über Aggreko verfügbar. Vor Zusage intern klären."),
             ("Prime oder Standby?", "Bei jeder Generator-Anfrage klären: Prime = Dauerbetrieb, Standby = Notstrom mit begrenzten Stunden.")],
            "kVA/MVA = Scheinleistung, kW/MW = Wirkleistung (bei cos phi 0,8: 1'000 kVA ≈ 800 kW). "
            "HVO = erneuerbarer Diesel. NEA = Netzersatzanlage. MS/NS = Mittel-/Niederspannung. "
            "BESS: immer nutzbare Kapazität (kWh) und C-Rate angeben, nicht Nennkapazität."),
        # 5 Pipeline
        blk("Rechenzentren haben das grösste Potenzial, Infrastruktur die höchste Erwartung.",
            f"«Rechenzentren bringen brutto {n['rz_pot']} CHF, aber viele kaufen zentral für Europa ein. "
            f"Infrastruktur liefert {n['inf_exp']} CHF Erwartung, weil Tunnel-Backups ein ganzes Jahr laufen.»",
            [("Warum Kanal-Partner als Segment?", "Burkhalter, VINCI, Equans, BKW und CKW/EKZ-Töchter kaufen über viele Baustellen. Ein Rahmen bringt Volumen ohne Einzelakquise.")],
            "UW = Unterwerk. EMEA = Europa, Naher Osten, Afrika (zentrale Beschaffung). k = Tausend CHF."),
        # 6 RZ-Zeitstrahl
        blk("Die RZ-Welle ist planbar: jetzt STACK und Green, 2028 Digital Realty und Vantage.",
            "«Die Kreisgrösse zeigt die IT-Leistung. Wer beim Bau schon Baustrom liefert, sitzt beim Commissioning am Tisch. "
            "Deshalb gehen wir bei Digital Realty und Vantage schon 2027 rein.»",
            [("Wie gross muss die Lastbank sein?", "Etwa so gross wie die IT-Last der Data Hall, die getestet wird, getestet in Stufen 25/50/75/100 %."),
             ("Sprache?", "Hyperscaler und internationale Betreiber: Unterlagen auf Englisch vorbereiten.")],
            "IT-MW = elektrische Leistung der Server. IST = Integrated Systems Test. Q2 = zweites Quartal. "
            "Hyperscaler = Cloud-Konzerne wie Microsoft, AWS, Google."),
        # 7 Top 10
        blk(f"Die Top 10 machen {n['top10']} der Erwartung aus. Dort zuerst.",
            "«Rot sind Rechenzentren. Die Tunnel führen, weil sie ein ganzes Jahr laufen. "
            "Vantage hat das grösste Einzelpotenzial, aber nur 10 % Gewinnchance.»",
            [("Warum KSA so weit oben?", "Umzug Januar 2027 mit NEA-Lasttest, danach Rückbau-Baustrom: fixe Termine, TU Implenia als Einstieg.")],
            "KSA = Kantonsspital Aarau. STACK/Green/Vantage = RZ-Betreiber. VINCI = Mutter von ETAVIS und Actemium."),
        # 8 Produktbedarf
        blk("Generator überall, Lastbank im RZ, Trafo im Netz, BESS bei Events und Nachtbaustellen.",
            "«Rot heisst Kernbedarf. Daraus leiten wir ab, mit welchem Produkt wir die Tür öffnen: im RZ die Lastbank, "
            "im Netz der Trafo, bei Events der Hybrid aus BESS und Generator.»",
            [], "NEA = Netzersatzanlage. USV = Unterbrechungsfreie Stromversorgung. HVO = erneuerbarer Diesel. UW = Unterwerk."),
        # 9 Rechenweg
        blk("Die Methode ist einfach und nachprüfbar, die Sätze sind noch Richtwerte.",
            "«Generator: MVA mal Wochen mal Satz. Lastbank: MW mal Wochen mal Satz. BESS: MW mal Monate mal Satz. "
            "Das Beispiel STACK zeigt es. Sobald wir unsere Preise einsetzen, rechnet die Excel alles neu.»",
            [("Woher kommen die Sätze?", "US-Richtwerte (dieselfuelhq, countbricks, ritarpower), umgerechnet mit 0,828 CHF/USD per 24.09.2026. Öffentliche CH-Preise ab 100 kVA gibt es nicht."),
             ("Wo trage ich unsere Preise ein?", "Excel, Blatt «Annahmen», Spalte E «MiT-Satz».")],
            "MVA = Megavoltampere (Scheinleistung). FX = Wechselkurs. Anteil 2027 = Teil des Volumens, der 2027 anfällt."),
        # 10 Cross-Sell
        blk("Mit Power rein, mit Wärme und Kälte ausbauen.",
            f"«Auf Winterbaustellen braucht es Bauheizung, beim RZ-Test oft Kühlung, WEF und Ski-WM brauchen Zeltheizung. "
            f"Und der Diesel: 1 MVA bei 75 % Last kostet rund {n['fuel']} CHF pro Stunde. Der BESS-Hybrid spart Laufzeit.»",
            [("Woher kommt der Dieselwert?", "Cummins C1000 D5: 139 l/h Prime, 154 l/h Standby bei 75 %. Dieselpreis TCS 18.09.2026: 2,41 CHF/l (Tankstelle).")],
            "HVO = Hydrotreated Vegetable Oil (erneuerbarer Diesel). IST = Integrated Systems Test. BESS = Batteriespeicher."),
        # 11 Infra/Spital/Industrie
        blk("Das sichere Volumen: lange Laufzeiten und fixe Termine.",
            "«Gotthard, Sisikon und Grimsel laufen das ganze Jahr. Bei KSA und Lonza sind die Termine 2027 fix. "
            "Bei ASTRA, SBB und USZ läuft es über öffentliche Ausschreibungen, also früh auf simap schauen.»",
            [("Wie kommen wir an ASTRA-Aufträge?", "Selten direkt. Meist über die Bau-ARGE, die den Zuschlag hat (z.B. Marti, Implenia/Frutiger).")],
            "ASTRA = Bundesamt für Strassen. ARGE = Arbeitsgemeinschaft. TU = Totalunternehmer. KWO = Kraftwerke Oberhasli. "
            "IVöB = öffentliches Beschaffungsrecht. simap = Ausschreibungsplattform."),
        # 12 EVU und Energie
        blk("Netzumbau, Reservekraftwerke und alpine Solaranlagen: 2027 ist Bauzeit bei den EVU.",
            f"«{n['n_netz']} Netz- und Energieprojekte liegen über CHF 50'000. Am konkretesten: Poste Galmiz von Groupe E, "
            "UW Laax von Repower mit Skigebiet am Netz, die GETEC-Reservekraftwerke mit Lastbank-Abnahme Anfang 2027 "
            "und sechs alpine Solar-Baustellen ohne Netzanschluss.»",
            [("Warum KKW-Revisionen?", "Jede Revision braucht Baustrom für Revisionsdörfer und Ersatz für Hilfssysteme. Termine 2027 noch nicht publiziert, Muster: Beznau März bis Mai und ab August, Leibstadt April/Mai, Gösgen Ende Mai. Nuklearbereich mit strengen Auflagen."),
             ("Wer bestellt bei Swissgrid?", "Meist der Generalunternehmer des Unterwerks oder der Leitungsbauer, selten Swissgrid direkt.")],
            "UW = Unterwerk. GIS = gasisolierte Schaltanlage. HVO = erneuerbarer Diesel. KKW = Kernkraftwerk. "
            "IBN = Inbetriebnahme. Solar-Express = Förderprogramm des Bundes für alpine Solaranlagen."),
        # 13 Events
        blk("Einzelne Events sind zu klein, als Saisonpaket werden sie interessant.",
            f"«Wir haben {n['n_ev']} Anlässe für 2026/27 gesammelt. Einzeln liegen fast alle unter CHF 50'000, weil sie nur Tage dauern. "
            "Gebündelt als Sommer-Festivals, Sport-Grossanlässe oder Märkte mit Zirkus Knie lohnt es sich. "
            "Dringend: Ski-WM, WEF und der neue Weihnachtsmarkt Bellevue Noël in Zürich.»",
            [("Sind die Event-Grössen belegt?", "Termine ja, die Leistungsgrössen sind Annahmen. Vor Offerte Bedarf beim OK abfragen."),
             ("Was ist mit der Ruder-WM Luzern?", "23. bis 29.08.2027, über 40'000 Zuschauer, TV-Compound mit Redundanz: das grösste Einzelevent im Paket Sport.")],
            "WEF = World Economic Forum. FIS = Internationaler Skiverband. ESAF = Eidg. Schwing- und Älplerfest. "
            "OK = Organisationskomitee. BESS = Batteriespeicher."),
        # 13 Wettbewerb
        blk("Viele vermieten Generatoren, kaum jemand liefert das komplette Commissioning-Paket.",
            "«Unser Unterschied: Lastbänke bis 6,25 MW, Commissioning Level 1 bis 5, BESS, Kühlung und Heizung aus einer Hand, "
            "mit der Aggreko-Flotte im Rücken.»",
            [("Und Kummler+Matter?", "Vermietet mobile Trafostationen: bei Netzprojekten Partner oder Wettbewerber, je nach Fall.")],
            "L1-L5 = Commissioning-Stufen von Werksabnahme bis Gesamttest. Cat = Caterpillar. kVA = Scheinleistung."),
        # 14 90 Tage
        blk("Oktober bis Januar: von der Liste zu den ersten Aufträgen.",
            "«Im Oktober die heissen Leads, im November die Rahmen mit den Installateur-Gruppen, im Dezember unsere Preise "
            "ins Modell und den CRM-Status eintragen, im Januar Review im Team.»",
            [("Wer macht was?", "Vorschlag: Burak RZ und Netz, Mauro und Jörg Kanal-Partner und CRM-Abgleich, Roberto Review. Im Team festlegen.")],
            "CRM = Kundendatenbank. RZ = Rechenzentrum. WEF = World Economic Forum."),
        # 15 Glossar
        blk("Nachschlagen, nicht vortragen.",
            "Folie nur zeigen, wenn Fragen zu Kürzeln kommen.", [], ""),
        # 16 Schluss
        blk("Rechenzentren früh im Bau besetzen, nicht erst beim Test.",
            "«Wer den Baustrom liefert, kennt die Leute und die Anlage, wenn das Commissioning kommt. "
            "Dort liegen die grossen Tickets.»",
            [], "IST = Integrated Systems Test."),
    ]
