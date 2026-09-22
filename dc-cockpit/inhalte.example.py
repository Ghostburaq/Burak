# -*- coding: utf-8 -*-
"""
inhalte.example.py - Geruest fuer inhalte.py.

Kopieren nach inhalte.py und mit den echten Daten fuellen:

    cp inhalte.example.py inhalte.py

inhalte.py steht in .gitignore, weil dort Kundennamen, Mailadressen,
Projektzuordnungen und interne Rollen liegen. Diese Vorlage hier ist bewusst
leer und enthaelt nur die Struktur.

Harte Regel: kein erfundener Wert. Was nicht belegt ist, bekommt "FEHLT" und
erscheint im Cockpit rot. Eine abgeleitete Adresse wird als solche markiert,
nie als Tatsache ausgegeben.
"""

# ---------------------------------------------------------------------------
# Mail und Telefon je Kontakt. Schluessel ist der Name EXAKT so, wie er in der
# Namensspalte des Tabs "Anrufplan" steht.
#
# mailq / telq:
#   "tracker"     Adresse steht so in der Quelle, belegt
#   "abgeleitet"  Firmenmuster angewendet, NICHT bestaetigt, Bounce-Risiko
#   "fehlt"       keine Quelle, erscheint im Cockpit als FEHLT
#   "opt-out"     darf nicht kalt angeschrieben werden (Werbe-Opt-out im Impressum)
#   "zentrale"    (nur telq) Hauptnummer der Firma, keine Durchwahl
#
# warnung: erscheint als gelber Kasten auf der Anrufkarte. Hier gehoert hin,
# was du vor dem Waehlen wissen musst: kaputte Nummer, ungeklaerte Anrede,
# interne Abstimmung noetig, falsche Rollenzuordnung im Tracker.
# ---------------------------------------------------------------------------
KONTAKTDATEN = {
    "Vorname Nachname": dict(
        mail="vorname.nachname@firma.ch", mailq="tracker",
        tel="+41 44 000 00 00", telq="zentrale",
        warnung="",
    ),
    "Nur Nachname": dict(
        mail="FEHLT", mailq="fehlt",
        tel="FEHLT", telq="fehlt",
        warnung="Vorname FEHLT. Anrede vor Versand klaeren.",
    ),
}

# Kontakte aus KONTAKTE_STATUS.md, die keine Zeile im Anrufplan haben.
OHNE_TERMIN = [
    dict(prio="A", name="Vorname Nachname", firma="Firma AG",
         projekt="Projektname", kanal="Mail", datum="", zeit="",
         bisher="E-Mail TT.MM.", inhalt="", einstieg="", ziel="Termin setzen.",
         status="ohne_termin"),
]

# Nicht anschreiben. Grund und Quelle stehen dabei, damit niemand den Eintrag
# versehentlich reaktiviert.
GESTRICHEN = [
    dict(name="Vorname Nachname", firma="Firma AG",
         grund="Warum gestrichen", quelle="CLAUDE.md"),
]

# Neubauprojekte. mw=None, wenn die Quelle keine Leistung nennt. Dann erscheint
# das Projekt als Liste statt als Nullbalken. ort wird ueber Nominatim geocodiert.
PIPELINE = [
    dict(projekt="Projektname", betreiber="Betreiber", groesse="00 MW", mw=0,
         ibn="2028", beteiligte="GU offen", stand="Prio A", ort="Ort, Schweiz"),
]

# Bestand Liechtenstein, mit vollstaendiger Adresse fuer eine genaue Kartenmarke.
LIECHTENSTEIN = [
    dict(standort="Standortname", betreiber="Betreiber AG",
         adresse="Strasse 1, 9490 Vaduz, Liechtenstein"),
]

# Bestand Schweiz, je Region eine Marke. Einzelstandorte kommen ueber den
# Ablauf MAP aus PROMPTS.md dazu.
BESTAND = [
    dict(region="Region", ort="Hauptort, Schweiz", anzahl="Auszug",
         betreiber="Betreiber, durch Komma getrennt"),
]

# Laufende Auftraege. Keine Preise, keine Fleetzusagen.
AUFTRAEGE = [
    dict(projekt="Projekt", inhalt="Was laeuft", hinweis="Auflage, zum Beispiel Referenz nur anonymisiert"),
]

ANLAESSE = [
    dict(name="Anlass", datum="2026-11-25", ort="Ort", prio="A"),
]

# ---------------------------------------------------------------------------
# Aus CLAUDE.md. Die Regeln erscheinen im Reiter Regeln, die Gates zusaetzlich
# als Checkliste im Dialog beim Anruf-Logging.
# ---------------------------------------------------------------------------
REGELN = [
    "Keine erfundenen Werte. Preise, Leistungsdaten, Normen, Produktdaten nur aus Quelle, sonst 'Wert fehlt'.",
    "Keine erfundenen Kontakte. Kein Name, keine Nummer, keine Mail ohne Beleg. Fehlt etwas: FEHLT.",
]

GATES = [
    dict(id="beispiel", label="Kurzer Satz, was vor dem Kontakt geprueft sein muss"),
]

SIGNATUR = ("Vorname Nachname | Funktion\n"
            "Firma AG\n"
            "+41 00 000 00 00 | mail@firma.com")

# Veraltete Angaben, die vor Versand ersetzt werden muessen.
SIGNATUR_ALT = ["+41 00 000 00 00", "alte.adresse@firma.ch"]

DATENQUALITAET = [
    "Bekannte Schwaeche der Datenquelle, ein Punkt je Zeile.",
]
