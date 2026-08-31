---
description: Kontakt recherchieren, Analyse bauen, zwei Kaltakquise-Mails schreiben
---

Kontakt für die Datacenter-Akquise: $ARGUMENTS

(Name allein reicht. Mehr geht auch: Name, Firma, Funktion, Projekt, Sprache.
Ohne Argument: nach dem Namen fragen und stoppen.)

Arbeitsordner ist `Datacenter-Radar/`. Halte dich an CLAUDE.md dort,
besonders Abschnitt 3 (absolute Regeln) und Abschnitt 9 (Kaltakquise-Texte).
Führe die sechs Schritte in dieser Reihenfolge aus, ohne Abkürzung.

## Schritt 1, Bestand prüfen (vor allem anderen)

Suche den Namen und die Firma in:
- `MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx`, Blätter `Kontakt-Log` und `CH-Kontakte`
- `MiT_Datacenter_Radar_CH_V1.0.xlsx`, Blätter `02_Projekt_Radar` und `03_Kontakte`

Gib zuerst aus, was du gefunden hast: Person bekannt, Firma bekannt, an welchen
Projekten sie hängt, letzter Kontakt, Status. Steht die Person schon mit einem
Status drin, sag es und frage, ob nachgefasst statt neu angeschrieben wird.

**Datenqualität:** Passt der Namensteil der E-Mail-Adresse nicht zum Namen der
Person, ist die Adresse unverifiziert. Dann keine Mail an diese Adresse
vorschlagen, sondern Telefon als ersten Kanal. Sag es ausdrücklich.

## Schritt 2, Recherche

WebSearch auf Person, Firma und das vermutete Projekt. Suche gezielt:
- Rolle und Zuständigkeit der Person auf der Firmenwebsite
- Referenzprojekte der Firma im Rechenzentrumsbau
- aktueller Stand des Projekts: Phase, IBN, Verzögerung, Netzanschluss
- ob die Firma an weiteren Radar-Projekten hängt

Nur belegte Angaben verwenden. Keine Kontaktdaten aus Namensmustern ableiten.
Steht WebSearch nicht zur Verfügung: sagen und nur mit dem Bestand arbeiten.

## Schritt 3, Analyse

Kurz, in dieser Struktur, keine Fliesstext-Wüste:

```
WER            Rolle im Deal: Betreiber, GU/TU, Fachplaner, Elektro oder Einkauf
PROJEKT        Name, Phase laut Radar, IBN, Kapazität, was belegt ist
FENSTER        welche Cx-Phase, was jetzt entschieden wird, was zu spät wäre
MULTIPLIKATOR  an wie vielen Radar-Projekten hängt die Firma
CHANCE         welche MiT-Leistung konkret passt, mit Begründung aus der Phase
RISIKO         was das Gespräch kippen kann
LÜCKE          was nicht belegt ist und im Gespräch zu klären ist
```

Priorisiere nach CLAUDE.md Abschnitt 7: das Zeitfenster entscheidet, nicht die
Projektgrösse. Planer- und GU-Kanal vor Betreiberansprache.

## Schritt 4, zwei Mailvarianten

Variante A zurückhaltend, Variante B offensiv. Je eine Zeile Begründung,
warum die Variante bei dieser Rolle wirkt, danach deine Empfehlung.

Für beide gilt:
- Sprache nach Empfänger: Deutsch Sie-Form, Romandie Französisch vous-Form,
  international Englisch. Schweizer Schreibweise, ss statt ß.
- Betreff konkret, ohne Fragezeichen, mit Projekt- oder Standortbezug
- erste Zeile führt Aggreko, weil Mobil in Time internationalen DC-Bauherren
  nichts sagt
- Projektbezug immer als Vermutung: "soweit ich sehe, sind Sie in X involviert"
- ein echter Fachanker zur Rolle des Empfängers, nicht zum Produkt
- eine Frage nach seinen Projekten, eine Weiterleitungsfrage
- ein Anruftermin mit Datum und Uhrzeit, auf einen Werktag in den nächsten
  zehn Tagen, vormittags
- volle Signatur:

```
Burak Ücöz | Sales Engineer Power
Mobil in Time AG, An Aggreko Company
+41 44 806 13 19 | burak.ucoez@mobilintime.ch
```

Verboten in jeder Mail: CHF-Beträge, Verfügbarkeitszusagen (Owen-Gate),
Innendienst-Namen, Vantage ZRH12 im Klartext (nur anonymisiert als
"Hyperscale-Rechenzentrum im Raum Zürich, 6 MVA elektrische Last,
8 MW Wärmelast"), Gedankenstriche als Stilmittel, Emojis, Floskeln.
Die PQ-Position nach IEC 61000-4-30:2025 Klasse A mit EN 50160 gehört als
Standardposition erwähnt, nie als Option.

## Schritt 5, Outlook-Notiz

```
Titel: MiT Power | [Anruf/Rückruf] [Name], [Firma] | [Projekt] | [TT.MM.JJJJ HH:MM]
```
dann Kontakt, Projekt, Phase, Rolle im Deal, angesprochen am, Inhalt,
Ziel des Anrufs, Wiedervorlage, Gates, Koordinationshinweise.

## Schritt 6, Log-Zeile vorbereiten

Zeige die Zeile, die ins `Kontakt-Log` kommt (Person, Datum, Kanal, Inhalt,
Ergebnis offen, nächster Schritt, Wiedervorlage, Status "angeschrieben").
Schreib sie noch nicht hinein. Erst wenn Burak "LOG" sagt oder bestätigt,
trägst du sie ein, mit Backup vorher und ohne bestehende Zeilen zu überschreiben.

Mails werden hier nie verschickt und keine Termine gebucht. Text ausgeben,
Burak kopiert ihn in Outlook.
