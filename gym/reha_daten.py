# -*- coding: utf-8 -*-
# Wortlaut unverändert aus GymLogbuch_Beine_Reha.xlsx übernommen.
FAHRPLAN_TITEL = 'REHA-FAHRPLAN  |  SCHULTERARTHROSKOPIE MIT BIZEPSSEHNEN-TENODESE'
FAHRPLAN_SUB = 'Richtwerte für die isolierte Tenodese ohne Rotatorenmanschetten- oder Labrumversorgung. Das schriftliche Nachbehandlungsschema des Operateurs hat in jedem einzelnen Punkt Vorrang vor dieser Tabelle.'
GRUNDREGELN = [
    ('Die drei Verbote',
     'Keine aktive Ellenbogenbeugung gegen Widerstand, keine Supination gegen Widerstand, kein Hängen oder Ziehen am operierten Arm. Diese drei belasten die Fixation direkt.'),
    ('Die gefährliche Phase',
     'Woche 2 bis 4. Die Fixationsfestigkeit fällt ab, die knöcherne Einheilung trägt noch nicht, und der Arm fühlt sich bereits gut an. Die meisten Versager passieren hier, nicht am ersten Tag.'),
    ('Schmerz als Grenze',
     'Bewegung bis zum Schmerz, nie darüber hinaus. Schmerz nach der Einheit, der länger als 2 Stunden anhält, heisst: zu viel gemacht.'),
    ('Bei Tenotomie statt Tenodese',
     'Wenn die Sehne nur durchtrennt und nicht fixiert wurde, gilt dieser Plan nicht. Dann ist die Beweglichkeit sofort frei, Belastungsaufbau ab Woche 3 bis 4, normale Trainingslast ab Woche 6 bis 8.'),
    ('Wenn zusätzlich operiert wurde',
     'Rotatorenmanschette oder Labrum mitversorgt: deren Protokoll gilt, es ist deutlich restriktiver. Diese Tabelle dann nicht verwenden.'),
]
PHASEN_KOPF = ['Phase', 'Woche\nnach OP', 'Ziel der Phase', 'Schulter: erlaubt', 'Schulter: verboten', 'Beintraining', 'Meilenstein zum Weitergehen']
PHASEN = [
    ['Phase 1\nSchutz', '0 - 2', 'Wunde heilt, Fixation ungestört lassen, Schmerz und Schwellung runter.', 'Schlinge nach Vorgabe. Passive Beweglichkeit im freigegebenen Bereich, Pendelübungen. Hand, Handgelenk und Nacken aktiv bewegen. Ellenbogen passiv strecken und beugen lassen. Eis mehrmals täglich.', 'Jede aktive Ellenbogenbeugung. Jede Supination gegen Widerstand. Heben, Tragen, Stützen mit dem Arm. Arm hinter dem Körper strecken.', 'Ab Freigabe der Wunde, frühestens Tag 7 bis 10: Beinstrecker, Adduktion, Beinbeuger sitzend, Waden sitzend. Alles im Sitzen, Arm in der Schlinge. Gehen ab Tag 1.', 'Wunde trocken und reizlos. Ruheschmerz unter 3 von 10. Passive Flexion etwa 90 Grad.'],
    ['Phase 2\nBeweglichkeit', '2 - 6', 'Schlinge abtrainieren, Beweglichkeit zurückholen, Schulterblatt ansteuern.', 'Schlinge nach Vorgabe abbauen, meist Woche 2 bis 4. Aktiv-assistiv zu aktiv frei. Schulterblatt-Ansteuerung. Ab Woche 4 submaximale Isometrie für die Rotatorenmanschette, etwa 30 bis 50 Prozent, 5 mal 30 Sekunden.', 'Weiterhin keine Beugung und keine Supination gegen Widerstand. Hebelast maximal 1 kg. Kein Zug, kein Hängen, keine Stütz-Position.', 'Zusätzlich ab Woche 2: Hip Thrust Maschine, seitliche Kickbacks. Ab Woche 4: Hip Thrust mit Stange, Arme vor der Brust gekreuzt. Waden stehend. Fahrrad ohne Lenkerbelastung ab Woche 2 bis 3.', 'Aktive Flexion mindestens 140 Grad, Abduktion 130 Grad, Aussenrotation 45 Grad. Schmerzfrei bei aktiver Bewegung.'],
    ['Phase 3\nerste Last', '6 - 12', 'Volle Beweglichkeit erreichen, Bizeps und Manschette wieder unter Last bringen.', 'Ab Woche 6 bis 8 leichte Beugung und Supination gegen Widerstand, Start bei 1 bis 2 kg, Steigerung in 0.5 kg-Schritten. Progressive Manschetten- und Schulterblattarbeit mit Band. Leichte geschlossene Kette.', 'Kein Bankdrücken mit Langhantel, keine Dips, keine Klimmzüge, kein schweres Rudern. Keine explosiven oder ruckartigen Bewegungen. Keine maximale Dehnung des Bizeps.', 'Ab Woche 6: Hackenschmidt-Kniebeuge mit lockerem Griff. Ab Woche 8: Split Squat in der Multipresse ohne Zusatzhantel. Beintraining ansonsten wieder vollständig.', 'Beweglichkeit seitengleich. Beugung gegen Widerstand schmerzfrei mit etwa 30 Prozent der Gegenseite.'],
    ['Phase 4\nAufbau', '12 - 16', 'Muskelaufbau für den Arm zurückholen, Druck- und Zugmuster neu aufbauen.', 'Bizeps-Curls progressiv, Start leicht und hohe Wiederholungen. Drücken zuerst an der Maschine, dann Kurzhantel. Latzug im neutralen Griff ab Woche 12 bis 14. Rudern gestützt.', 'Weiterhin keine Maximallast. Kein Bankdrücken mit Langhantel im schweren Bereich. Keine Klimmzüge mit Zusatzgewicht.', 'Ab Woche 12: Rumänisches Kreuzheben leicht wieder aufnehmen, Technik vor Last. Split Squat mit Kurzhantel ab Woche 12.', 'Beugekraft etwa 70 Prozent der Gegenseite. Kein Schmerz im Sulcus bei Belastung.'],
    ['Phase 5\nRückkehr', 'Monat 4 - 6', 'Zurück zur vollen Trainingslast, seitengleiche Kraft.', 'Progressiver Aufbau aller Muster. Langhantel-Bankdrücken, schweres Rudern und Klimmzüge frühestens ab Monat 5. Maximallast nach Freigabe.', 'Nichts pauschal verboten, aber jede neue Belastung mit reduzierter Last einführen und über 2 bis 3 Wochen steigern.', 'Beintraining vollständig ohne Einschränkung, alle Übungen wie im Normalmodus.', 'Beugekraft mindestens 90 Prozent der Gegenseite. Volle Beweglichkeit. Schmerzfrei über 4 Wochen.'],
]
NOTFALL_TITEL = 'SOFORT ZUM ARZT'
NOTFALL = 'Plötzlicher stechender Schmerz mit hörbarem Knall im Oberarm. Sichtbare Verformung des Bizepsbauchs nach distal (Popeye). Plötzlicher Kraftverlust bei der Beugung. Rötung, Überwärmung, Wundsekret oder Fieber. Zunehmender statt abnehmender Schmerz über mehrere Tage. Taubheit oder Kribbeln in Hand oder Fingern.'
HEILUNG_TITEL = 'WAS DIE HEILUNG MESSBAR BREMST ODER FÖRDERT'
HEILUNG = [
    ('Energieverfügbarkeit', 'bremst stark',
     'Kollagensynthese und Wundheilung brauchen Energie. Bei sehr niedrigem Körperfett und Defizit heilt Sehne und Knochen langsamer. In der Heilungsphase Erhaltungskalorien oder leichter Überschuss, kein Defizit.'),
    ('Protein', 'fördert',
     '2.0 bis 2.5 g pro kg Körpergewicht täglich, gleichmässig auf 4 bis 5 Mahlzeiten. Kollagen entsteht nicht aus dem Nichts.'),
    ('Vitamin C und Vitamin D', 'fördert',
     'Vitamin C ist Kofaktor der Kollagen-Hydroxylierung. Vitamin D für die knöcherne Einheilung, Zielwert im oberen Normbereich. Beides über Blutbild prüfen, nicht raten.'),
    ('Schlaf', 'fördert stark',
     'Der grösste Wachstumshormon-Puls des Tages liegt im ersten Tiefschlafzyklus. 7 bis 9 Stunden sind in der Heilungsphase keine Empfehlung, sondern Teil der Behandlung.'),
    ('NSAR wie Ibuprofen und Diclofenac', 'bremst',
     'Dauerhaft hochdosiert hemmen sie genau die Entzündungsphase, die für die Sehnenheilung nötig ist. Kurzfristig zur Schmerzkontrolle nach Rücksprache, nicht als Wochenprogramm.'),
    ('Nikotin', 'bremst stark',
     'Verschlechtert Durchblutung und Sehnen-Knochen-Heilung deutlich. Wenn irgendwo Verzicht lohnt, dann hier.'),
    ('Hochdosierte Androgene', 'Risiko',
     'Erhöhen Sehnensteifigkeit und senken Elastizität, Kollagen-Crosslinks werden ungünstig verändert. Sehnenrupturen unter Anwendung sind dokumentiert. Gehört vollständig und ungeschönt zum Operateur, weil es die Nachbehandlung verändert.'),
]
MODUS_TITEL = 'BEINTRAINING IM REHA-MODUS'
MODUS_SUB = 'Woche nach OP eintragen, die Ampel zeigt je Übung, was heute erlaubt ist. Die Freigaben stehen im Blatt Übungen und lassen sich dort anpassen.'
MODUS_KOPF = ['Übung', 'Frei ab\nWoche', 'Status heute', 'Sätze', 'Ziel-Wdh', 'Ersatz in der Sperrzeit', 'Hinweis']
MODUS_REGELN_TITEL = 'REGELN FÜR JEDE BEINEINHEIT IN DER REHA-PHASE'
MODUS_REGELN = [
    ('Der Arm arbeitet nicht',
     'Kein Halten, kein Ziehen, kein Abstützen über den operierten Arm. Wo eine Übung nur mit Griff geht, ist sie gesperrt, nicht angepasst.'),
    ('Bauchpresse dosieren',
     'Starkes Pressen erhöht den Druck und den Zug über den Schultergürtel. In den ersten 6 Wochen bei RPE 8 stoppen statt bei RPE 9.'),
    ('Aufsetzen und Absteigen',
     'An Maschinen mit der gesunden Seite abstützen. Beim Hip Thrust die Stange von einer zweiten Person auflegen lassen, nicht selbst über den Arm rollen.'),
    ('Volumen halten, nicht steigern',
     'In Phase 1 und 2 geht es um Erhalt. Zwei Beineinheiten pro Woche mit 60 bis 70 Prozent des gewohnten Volumens genügen, um Muskelmasse zu halten.'),
    ('Cardio',
     'Gehen ab Tag 1. Fahrrad ab Woche 2 bis 3 ohne Belastung über den Lenker. Kein Rudergerät, kein Assault Bike, kein Seilspringen bis Phase 4.'),
    ('Dokumentation',
     'Reha-Sätze ganz normal im Blatt Log erfassen und in der Notizspalte Reha vermerken. So bleibt die Historie durchgehend und du siehst später, was die Pause gekostet hat.'),
]
REHA_UEBUNGEN = {
    'Hackenschmidt-Kniebeuge': (6, 'Beinpresse mit tiefer Fussposition, Hände seitlich abgelegt',
     'Schulterpolster und Griffe. Der Griff ist isometrische Ellenbogenbeugung, deshalb erst nach der Sperrfrist. Ab Freigabe locker greifen, nicht ziehen.'),
    'Split Squat': (8, 'Beinpresse einbeinig, ab Woche 6 Multipresse ohne Zusatzhantel',
     'Kurzhanteln hängen am Arm und ziehen an der frischen Fixation. Kurzhantel-Variante frühestens ab Woche 12. Bis dahin Multipresse oder Gewichtsweste.'),
    'Beinstrecker': (1, 'keiner, ab Freigabe der Wunde nutzbar',
     'Uneingeschränkt. Hände in den Schoss legen oder locker auflegen, nicht an den Griffen ziehen.'),
    'Adduktion': (1, 'keiner, ab Freigabe der Wunde nutzbar',
     'Uneingeschränkt. Arm in der Schlinge belassen, Rumpf bleibt ruhig.'),
    'Rumänisches Kreuzheben': (12, 'Beinbeuger sitzend, Rückenstrecker mit vor der Brust gekreuzten Armen, Kabel-RDL mit Hüftgurt',
     'Griffbelastung plus Zug am hängenden Arm. Die ungünstigste Kombination für eine Bizepsfixation. Ab Woche 12 leicht beginnen, volle Last frühestens Monat 5.'),
    'Hip Thrust': (4, 'Hip Thrust Maschine mit Polster ab Woche 2',
     'Die Stange liegt auf der Hüfte, der Arm stabilisiert nur. Arme vor der Brust kreuzen statt die Stange zu halten. Maschinenvariante deutlich früher frei.'),
    'Beinbeuger': (1, 'keiner, ab Freigabe der Wunde nutzbar',
     'Sitzend. Griffe locker halten oder loslassen, das Polster hält das Bein.'),
    'Seitliche Kickbacks': (2, 'Abduktion an der Maschine im Sitzen',
     'Im Stehen mit der gesunden Seite abstützen. Kein Zug über den operierten Arm.'),
    'Waden': (2, 'Wadenmaschine sitzend ab Woche 1',
     'Sitzend ab Woche 1. Stehende Variante mit Schulterpolster erst ab Woche 4 bis 6, Multipresse-Variante ab Woche 8.'),
    'Lunges': (None, 'archiviert',
     'Nicht im Plan.'),
    'Kickback': (None, 'archiviert',
     'Nicht im Plan.'),
}
REHALOG_TITEL = 'REHA-LOG  |  SCHULTER'
REHALOG_SUB = 'Täglich 60 Sekunden. Beweglichkeit im Stehen messen, immer zur gleichen Tageszeit und mit derselben Methode. Gelbe Spalten ausfüllen.'
REHALOG_KOPF = ['Datum', 'Woche\nnach OP', 'Phase', 'Schmerz\nRuhe 0-10', 'Schmerz\nBelastung 0-10', 'Flexion\nGrad', 'Abduktion\nGrad', 'Aussen-\nrotation Grad', 'Schlinge\ngetragen', 'Reha-Übungen\nerledigt', 'Schlaf\n(h)', 'Auffälligkeit / Notiz']
