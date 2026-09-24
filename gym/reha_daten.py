# -*- coding: utf-8 -*-
# Nachbehandlung für den tatsächlich geplanten Eingriff:
# arthroskopische Subscapularis-Naht mit Bizepstenodese, rechte Schulter,
# Termin 30.09.2026, Ruhigstellung im Gilchrist.
#
# Die frühere Fassung dieses Moduls war für eine ISOLIERTE Bizepstenodese
# ohne Rotatorenmanschetten-Versorgung geschrieben und enthielt selbst die
# Regel: "Rotatorenmanschette oder Labrum mitversorgt - deren Protokoll
# gilt, es ist deutlich restriktiver. Diese Tabelle dann nicht verwenden."
# Genau dieser Fall ist eingetreten: der Subscapularis ist Teil der
# Rotatorenmanschette. Alle Freigabewochen sind deshalb neu gesetzt.
#
# Die Zahlen sind konservative Richtwerte aus dem üblichen Vorgehen nach
# Subscapularis-Naht, keine ärztliche Vorgabe. Sobald das schriftliche
# Nachbehandlungsschema des Operateurs vorliegt, gilt ausschliesslich
# dieses - Abweichungen hier eintragen.

OP_DATEN = [
    ('Eingriff', 'Arthroskopie mit Sehnennaht und Bizepstenodese'),
    ('Diagnose', 'Läsion am Oberrand des Subscapularis mit '
                 'Bizepssehnen-Instabilität'),
    ('Seite', 'rechts'),
    ('Termin', '30.09.2026'),
    ('Ruhigstellung', 'Gilchrist-Bandage'),
    ('Dringlichkeit laut Aufklärung', 'keine - Termin frei wählbar'),
    ('Verbesserungswahrscheinlichkeit laut Aufklärung', 'gut'),
]

FAHRPLAN_TITEL = ('REHA-FAHRPLAN  |  SUBSCAPULARIS-NAHT MIT BIZEPSTENODESE, '
                  'RECHTS')
FAHRPLAN_SUB = (
    'Konservative Richtwerte für die Naht einer Subscapularis-Sehne mit '
    'gleichzeitiger Bizepstenodese. Deutlich strenger und länger als bei '
    'einer isolierten Tenodese, weil eine genähte Sehne am Knochen '
    'einheilen muss. Das schriftliche Nachbehandlungsschema des Operateurs '
    'hat in jedem einzelnen Punkt Vorrang vor dieser Tabelle.')

GRUNDREGELN = [
    ('Warum dieser Plan strenger ist als der alte',
     'Der Subscapularis gehört zur Rotatorenmanschette. Bei einer isolierten '
     'Bizepstenodese ist nur eine Sehne umgesetzt, hier wird zusätzlich eine '
     'gerissene Sehne an den Knochen genäht. Sehne heilt am Knochen langsam '
     'und ist in den ersten Wochen schwächer als die Naht selbst. Alle '
     'Freigaben liegen deshalb rund doppelt so spät wie im vorherigen Plan.'),
    ('Die vier Verbote',
     'Keine aktive Innenrotation gegen Widerstand - das ist die Arbeit des '
     'genähten Muskels. Keine passive Aussenrotation über die Freigabegrenze '
     '- das zieht die Naht auseinander. Keine aktive Ellenbogenbeugung und '
     'keine Supination gegen Widerstand - das belastet die Tenodese. Kein '
     'Stützen, Hängen oder Ziehen über den rechten Arm.'),
    ('Hand hinter den Rücken ist tabu',
     'Die Bewegung kombiniert maximale Innenrotation mit Streckung und ist '
     'die klassische Position, in der eine frische Subscapularis-Naht '
     'versagt. Gilt für Alltag genauso wie fürs Gym: BH schliessen, '
     'Gürtel, Gesässtasche, Rückwärtsgreifen beim Aufsetzen an der '
     'Maschine.'),
    ('Gilchrist konsequent tragen',
     'Nach Vorgabe des Operateurs, üblicherweise 4 bis 6 Wochen Tag und '
     'Nacht. Abgelegt wird sie nur für die freigegebenen Übungen und für '
     'die Körperpflege, und dabei hängt der Arm entspannt am Körper.'),
    ('Die gefährliche Phase',
     'Woche 3 bis 8. Der Schmerz ist weg, die Schlinge fällt, und die '
     'Sehnen-Knochen-Heilung ist zugleich am schwächsten. Die meisten '
     'Re-Rupturen passieren hier, nicht in den ersten Tagen.'),
    ('Schmerz als Grenze',
     'Bewegung bis zum Schmerz, nie darüber hinaus. Schmerz, der nach der '
     'Einheit länger als 2 Stunden anhält, heisst: zu viel gemacht.'),
    ('Wenn zwei Vorgaben sich widersprechen',
     'Immer die strengere nehmen. Das Naht-Protokoll ist bei Bewegung und '
     'Innenrotation führend, das Tenodese-Protokoll bei Ellenbogenbeugung '
     'und Supination. Beide laufen parallel, keines hebt das andere auf.'),
    ('Rechte Seite heisst Alltag mitplanen',
     'Anziehen, Haare, Autofahren, Einkaufstasche, Tür aufhalten. Was mit '
     'der rechten Hand nur unter Zug oder Verdrehung geht, wird in den '
     'ersten Wochen von jemand anderem gemacht oder anders gelöst. Das '
     'vorher besprechen, nicht am ersten Tag improvisieren.'),
]

PHASEN_KOPF = ['Phase', 'Woche\nnach OP', 'Ziel der Phase',
               'Schulter: erlaubt', 'Schulter: verboten', 'Beintraining',
               'Meilenstein zum Weitergehen']
PHASEN = [
    ['Phase 1\nSchutz', '0 - 6',
     'Die Naht ungestört einheilen lassen. Wunde zu, Schmerz und Schwellung '
     'runter, Gelenk nicht einsteifen lassen.',
     'Gilchrist Tag und Nacht nach Vorgabe. Passive Bewegung nur im '
     'freigegebenen Bereich, typischerweise Flexion bis etwa 90 Grad, '
     'Abduktion bis etwa 60 Grad, Aussenrotation nur bis zur Neutralstellung '
     '0 Grad. Pendelübungen. Hand, Handgelenk, Ellenbogen und Nacken aktiv '
     'bewegen. Eis mehrmals täglich.',
     'Jede aktive Innenrotation. Jede Aussenrotation über 0 Grad. Aktive '
     'Ellenbogenbeugung und Supination gegen Widerstand. Hand hinter den '
     'Rücken. Heben, Tragen, Stützen, Abstossen aus dem Bett über den '
     'rechten Arm.',
     'Ab Freigabe der Wunde, frühestens Tag 10 bis 14: Beinstrecker, '
     'Adduktion, Beinbeuger sitzend, Waden sitzend. Alles im Sitzen, Arm '
     'bleibt in der Schlinge, Ein- und Aussteigen nur über die linke Seite. '
     'Gehen ab Tag 1.',
     'Wunde trocken und reizlos. Ruheschmerz unter 3 von 10. Passive '
     'Flexion etwa 90 Grad, Aussenrotation bis 0 Grad schmerzfrei. '
     'Ärztliche Freigabe zum Ablegen der Schlinge.'],
    ['Phase 2\nBeweglichkeit', '6 - 12',
     'Schlinge abtrainieren, Beweglichkeit vollständig zurückholen, '
     'Schulterblatt ansteuern.',
     'Schlinge weg. Aktiv-assistive Bewegung zu aktiver Bewegung ohne '
     'Widerstand. Aussenrotation schrittweise über 0 Grad hinaus freigeben. '
     'Schulterblatt-Ansteuerung. Ab Woche 8 bis 10 sanfte submaximale '
     'Isometrie für die Innenrotation, etwa 20 bis 30 Prozent, kurz halten.',
     'Weiterhin keine Innenrotation gegen nennenswerten Widerstand. Keine '
     'Beugung und keine Supination gegen Widerstand. Hebelast maximal 1 kg. '
     'Kein Zug, kein Hängen, keine Stütz-Position. Hand hinter den Rücken '
     'weiterhin nicht.',
     'Zusätzlich ab Woche 6: Beinpresse enger und breiter Stand, Hip & Glute '
     'Maschine, seitliche Kickbacks im Sitzen, Waden stehend ohne '
     'Schulterpolster. Fahrrad ohne Belastung über den Lenker ab Woche 3.',
     'Aktive Flexion mindestens 140 Grad, Abduktion 130 Grad, '
     'Aussenrotation 45 Grad. Bauchpress-Test und Lift-off-Test ohne '
     'Widerstand schmerzfrei möglich.'],
    ['Phase 3\nerste Last', '12 - 16',
     'Innenrotation und Bizeps erstmals wieder unter Last bringen.',
     'Ab Woche 12 leichte Innenrotation gegen Widerstand, Start mit Band in '
     'der kleinsten Stufe. Ab Woche 12 leichte Ellenbogenbeugung und '
     'Supination gegen Widerstand, Start bei 1 bis 2 kg, Steigerung in '
     '0.5 kg-Schritten. Progressive Manschetten- und Schulterblattarbeit. '
     'Leichte geschlossene Kette.',
     'Kein Bankdrücken mit Langhantel, keine Dips, keine Klimmzüge, kein '
     'schweres Rudern. Keine explosiven oder ruckartigen Bewegungen. Keine '
     'maximale Dehnung in Aussenrotation oder am Bizeps.',
     'Ab Woche 12: Hip Thrust mit Stange mit vor der Brust gekreuzten Armen, '
     'Reverse V-Squat mit lockerem Griff, Split Squat in der Multipresse '
     'ohne Zusatzhantel. Beintraining sonst wieder vollständig.',
     'Beweglichkeit seitengleich. Innenrotationskraft etwa 50 Prozent der '
     'Gegenseite, schmerzfrei. Beugung gegen Widerstand schmerzfrei.'],
    ['Phase 4\nAufbau', 'Monat 4 - 6',
     'Kraft für Innenrotation, Beugung und Druckmuster zurückholen.',
     'Innenrotation progressiv mit Band und Kabel. Bizeps-Curls progressiv, '
     'Start leicht und hohe Wiederholungen. Drücken zuerst an der Maschine, '
     'dann Kurzhantel. Latzug im neutralen Griff. Rudern gestützt.',
     'Weiterhin keine Maximallast. Kein schweres Langhantel-Bankdrücken. '
     'Keine Klimmzüge mit Zusatzgewicht. Kein Reissen der Last aus der '
     'Dehnung.',
     'Ab Monat 4: Rumänisches Kreuzheben mit Langhantel leicht wieder '
     'aufnehmen, Technik vor Last. Split Squat mit Kurzhantel ab Monat 4.',
     'Innenrotations- und Beugekraft etwa 70 bis 80 Prozent der Gegenseite. '
     'Kein Schmerz im Sulcus und vorne am Gelenk unter Belastung.'],
    ['Phase 5\nRückkehr', 'Monat 6 - 9',
     'Zurück zur vollen Trainingslast, seitengleiche Kraft.',
     'Progressiver Aufbau aller Muster. Langhantel-Bankdrücken, schweres '
     'Rudern und Klimmzüge frühestens ab Monat 6 bis 7. Maximallast nach '
     'ärztlicher Freigabe.',
     'Nichts pauschal verboten, aber jede neue Belastung mit reduzierter '
     'Last einführen und über 2 bis 3 Wochen steigern.',
     'Beintraining vollständig ohne Einschränkung, alle Übungen wie im '
     'Normalmodus.',
     'Innenrotations- und Beugekraft mindestens 90 Prozent der Gegenseite. '
     'Volle Beweglichkeit. Schmerzfrei über 4 Wochen.'],
]

NOTFALL_TITEL = 'SOFORT ZUM ARZT'
NOTFALL = (
    'Plötzlicher Kraftverlust bei der Innenrotation: die Hand lässt sich '
    'nicht mehr gegen den Bauch drücken, oder sie rutscht beim Versuch weg. '
    'Plötzlicher stechender Schmerz mit hörbarem Knall in Schulter oder '
    'Oberarm. Sichtbare Verformung des Bizepsbauchs nach unten (Popeye). '
    'Plötzlicher Kraftverlust bei der Ellenbogenbeugung. Rötung, '
    'Überwärmung, Wundsekret oder Fieber. Zunehmender statt abnehmender '
    'Schmerz über mehrere Tage. Taubheit oder Kribbeln in Hand oder '
    'Fingern. Ein Ereignis, bei dem der Arm ruckartig nach hinten gerissen '
    'wurde - auch ohne sofortigen Schmerz melden.')

HEILUNG_TITEL = 'WAS DIE HEILUNG MESSBAR BREMST ODER FÖRDERT'
HEILUNG = [
    ('Energieverfügbarkeit', 'bremst stark',
     'Kollagensynthese und Wundheilung brauchen Energie. Bei sehr niedrigem '
     'Körperfett und Defizit heilt Sehne und Knochen langsamer. In der '
     'Heilungsphase Erhaltungskalorien oder leichter Überschuss, kein '
     'Defizit.'),
    ('Protein', 'fördert',
     '2.0 bis 2.5 g pro kg Körpergewicht täglich, gleichmässig auf 4 bis 5 '
     'Mahlzeiten. Kollagen entsteht nicht aus dem Nichts.'),
    ('Vitamin C und Vitamin D', 'fördert',
     'Vitamin C ist Kofaktor der Kollagen-Hydroxylierung. Vitamin D für die '
     'knöcherne Einheilung, Zielwert im oberen Normbereich. Beides über '
     'Blutbild prüfen, nicht raten.'),
    ('Schlaf', 'fördert stark',
     'Der grösste Wachstumshormon-Puls des Tages liegt im ersten '
     'Tiefschlafzyklus. 7 bis 9 Stunden sind in der Heilungsphase keine '
     'Empfehlung, sondern Teil der Behandlung. Mit Gilchrist schläft es '
     'sich schlecht - halb sitzend mit Kissen unter dem Ellenbogen hilft.'),
    ('NSAR wie Ibuprofen und Diclofenac', 'bremst',
     'Dauerhaft hochdosiert hemmen sie genau die Entzündungsphase, die für '
     'die Sehnen-Knochen-Heilung nötig ist. Kurzfristig zur Schmerzkontrolle '
     'nach Rücksprache, nicht als Wochenprogramm.'),
    ('Nikotin', 'bremst stark',
     'Verschlechtert Durchblutung und Sehnen-Knochen-Heilung deutlich. Bei '
     'einer genähten Manschettensehne ist das der grösste einzelne '
     'vermeidbare Risikofaktor für eine Re-Ruptur.'),
    ('Hochdosierte Androgene', 'Risiko',
     'Erhöhen Sehnensteifigkeit und senken Elastizität, Kollagen-Crosslinks '
     'werden ungünstig verändert. Sehnenrupturen unter Anwendung sind '
     'dokumentiert. Gehört vollständig und ungeschönt zum Operateur, weil '
     'es die Nachbehandlung verändert.'),
]

MODUS_TITEL = 'BEINTRAINING IM REHA-MODUS'
MODUS_SUB = ('Woche nach OP eintragen, die Ampel zeigt je Übung, was heute '
             'erlaubt ist. Die Freigaben stehen im Blatt Übungen und lassen '
             'sich dort anpassen, sobald das Schema des Operateurs vorliegt.')
MODUS_KOPF = ['Übung', 'Frei ab\nWoche', 'Status heute', 'Sätze', 'Ziel-Wdh',
              'Ersatz in der Sperrzeit', 'Hinweis']
MODUS_REGELN_TITEL = 'REGELN FÜR JEDE BEINEINHEIT IN DER REHA-PHASE'
MODUS_REGELN = [
    ('Der rechte Arm arbeitet nicht',
     'Kein Halten, kein Ziehen, kein Abstützen über den operierten Arm. Wo '
     'eine Übung nur mit Griff geht, ist sie gesperrt, nicht angepasst.'),
    ('Nicht nach hinten greifen',
     'Beim Aufsetzen an der Maschine nicht rückwärts nach der Lehne oder '
     'dem Sitz greifen. Das ist Aussenrotation plus Streckung und damit die '
     'Position, die die Naht am stärksten belastet. Immer erst hinsetzen, '
     'dann den Arm ablegen.'),
    ('Bauchpresse dosieren',
     'Starkes Pressen erhöht Druck und Zug über den Schultergürtel. In den '
     'ersten 12 Wochen bei RPE 8 stoppen statt bei RPE 9.'),
    ('Aufsetzen und Absteigen',
     'An Maschinen ausschliesslich mit der linken Seite abstützen. Beim Hip '
     'Thrust die Stange von einer zweiten Person auflegen lassen, nicht '
     'selbst über den Arm rollen.'),
    ('Volumen halten, nicht steigern',
     'In Phase 1 und 2 geht es um Erhalt. Zwei Beineinheiten pro Woche mit '
     '60 bis 70 Prozent des gewohnten Volumens genügen, um Muskelmasse zu '
     'halten.'),
    ('Cardio',
     'Gehen ab Tag 1. Fahrrad ab Woche 3 ohne Belastung über den Lenker, '
     'am besten auf einem Ergometer mit Lehne. Kein Rudergerät, kein '
     'Assault Bike, kein Seilspringen bis Phase 4.'),
    ('Dokumentation',
     'Reha-Sätze ganz normal im Blatt Log erfassen und in der Notizspalte '
     'Reha vermerken. So bleibt die Historie durchgehend und du siehst '
     'später, was die Pause gekostet hat.'),
]

# Freigabewoche, Ersatzübung in der Sperrzeit, Hinweis.
# Alle Wochen sind konservativ abgeleitet für die Subscapularis-Naht mit
# Tenodese und NICHT ärztlich bestätigt.
REHA_UEBUNGEN = {
    'Beinstrecker': (
        2, 'keiner, ab Freigabe der Wunde nutzbar',
        'Sitzend, Arm bleibt in der Schlinge im Schoss. Nicht an den '
        'Griffen ziehen. Frühester sinnvoller Start Tag 10 bis 14.'),
    'Adduktion': (
        2, 'keiner, ab Freigabe der Wunde nutzbar',
        'Sitzend, Arm bleibt in der Schlinge, Rumpf ruhig. Achtung: die '
        'Adduktoren-Zerrung links ist erst seit September verheilt - hier '
        'mit reduzierter Last wieder einsteigen.'),
    'Beinbeuger': (
        2, 'keiner, ab Freigabe der Wunde nutzbar',
        'Sitzend. Griffe loslassen, das Polster hält das Bein.'),
    'Waden': (
        2, 'Wadenmaschine sitzend',
        'Sitzend ab Woche 2. Stehende Variante ohne Schulterpolster ab '
        'Woche 6, mit Schulterpolster oder in der Multipresse erst ab '
        'Woche 12.'),
    'Beinpresse eng': (
        6, 'Beinstrecker und Beinbeuger sitzend, beide ab Woche 2 frei',
        'Erst nach Ablegen der Schlinge. Ein- und Aussteigen über die linke '
        'Seite, Hände im Schoss ablegen statt an den Griffen zu ziehen. '
        'Tiefe Fussposition. Woche mit Operateur bestätigen.'),
    'Beinpresse breit': (
        6, 'Beinstrecker und Beinbeuger sitzend, beide ab Woche 2 frei',
        'Wie die enge Variante ab Woche 6. Zusätzlich beachten: breiter '
        'Stand zieht die Adduktoren in die Dehnung, deshalb links '
        'vorsichtig einsteigen.'),
    'Hip & Glute': (
        6, 'Beinbeuger sitzend, ab Woche 2 frei',
        'Arme vor der Brust kreuzen, nicht am Gerät abstützen. Vorher '
        'wäre die Ein- und Ausstiegsbewegung das Problem, nicht die Übung '
        'selbst.'),
    'Seitliche Kickbacks': (
        6, 'Abduktion an der Maschine im Sitzen',
        'Nur mit der linken Seite abstützen. Kein Zug über den rechten '
        'Arm, auch nicht zum Ausbalancieren.'),
    'Hip Thrust': (
        12, 'Hip & Glute Maschine ab Woche 6',
        'Die Stange muss aufgelegt und abgenommen werden - genau das geht '
        'mit einer frischen Naht nicht. Ab Woche 12 nur mit zweiter Person '
        'und vor der Brust gekreuzten Armen.'),
    'Reverse V-Squat': (
        12, 'Beinpresse enger Stand ab Woche 6',
        'Die Polster liegen auf Schulter und Nacken, die Last geht direkt '
        'über den Schultergürtel. Ab Woche 12 mit lockerem Griff, nicht '
        'ziehen. Woche mit Operateur bestätigen.'),
    'Split Squat': (
        12, 'Beinpresse einbeinig ab Woche 6, Multipresse ohne Zusatzlast '
            'ab Woche 12',
        'Kurzhanteln hängen am Arm und ziehen an Naht und Tenodese '
        'zugleich. Kurzhantel-Variante frühestens ab Monat 4. Bis dahin '
        'Multipresse oder Gewichtsweste.'),
    'Rumänisches Kreuzheben': (
        16, 'Beinbeuger sitzend, Rückenstrecker mit vor der Brust '
            'gekreuzten Armen, Kabel-RDL mit Hüftgurt',
        'Griffbelastung plus Dauerzug am hängenden Arm - die ungünstigste '
        'Kombination für Naht und Tenodese. Ab Monat 4 leicht beginnen, '
        'volle Last frühestens Monat 6.'),
    'Rumänisches Kreuzheben KH': (
        16, 'Beinbeuger sitzend, Rückenstrecker mit vor der Brust '
            'gekreuzten Armen, Kabel-RDL mit Hüftgurt',
        'Wie die Langhantel-Variante, eher noch ungünstiger: die Hantel '
        'hängt direkt am Arm und zieht durchgehend an Naht und Tenodese. '
        'Ab Monat 4 leicht beginnen.'),
    'Squat Maschine Bülach': (
        12, 'Beinpresse enger Stand ab Woche 6',
        'Wie der Reverse V-Squat: Last über Schulter und Nacken. Woche mit '
        'Operateur bestätigen.'),
    'Hip Thrust Bülach': (
        12, 'Hip & Glute Maschine ab Woche 6',
        'Angesetzt wie die Langhantel-Variante. Ist es eine Maschine mit '
        'Hüftpolster ohne Hantelhandhabung, geht Woche 6 - dann im Blatt '
        'Übungen ändern.'),
    'Beinbeuger Bülach': (
        2, 'keiner, ab Freigabe der Wunde nutzbar',
        'Liegend und sitzend beide unkritisch, solange die Griffe nur '
        'locker aufliegen. Bei der liegenden Variante das Aufstehen über '
        'die linke Seite.'),
    'Hackenschmidt-Kniebeuge': (
        12, 'Beinpresse mit tiefer Fussposition ab Woche 6',
        'Archiviert, Wert nur noch für die Historie hinterlegt.'),
    'Lunges': (None, 'archiviert', 'Nicht im Plan.'),
    'Kickback': (None, 'archiviert', 'Nicht im Plan.'),
}

REHALOG_TITEL = 'REHA-LOG  |  SCHULTER RECHTS'
REHALOG_SUB = ('Täglich 60 Sekunden. Beweglichkeit im Stehen messen, immer '
               'zur gleichen Tageszeit und mit derselben Methode. Gelbe '
               'Spalten ausfüllen.')
REHALOG_KOPF = ['Datum', 'Woche\nnach OP', 'Phase', 'Schmerz\nRuhe 0-10',
                'Schmerz\nBelastung 0-10', 'Flexion\nGrad', 'Abduktion\nGrad',
                'Aussen-\nrotation Grad', 'Schlinge\ngetragen',
                'Reha-Übungen\nerledigt', 'Schlaf\n(h)',
                'Auffälligkeit / Notiz']
