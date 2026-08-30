# CLAUDE.md — Datacenter-Radar Schweiz

Projektanweisung für Claude Code. Diese Datei liegt im Projektordner neben
`MiT_Datacenter_Radar_CH_V1.0.xlsx` und gilt für jede Session in diesem Ordner.

---

## 1. Wer hier arbeitet

Burak Ücöz, Sales Engineer Power bei Mobil in Time AG (An Aggreko Company),
Standort Diessenhofen. Er baut den Schweizer Bereich für mobile Stromlösungen auf
und ist als einziger Power-Spezialist für alle 26 Kantone zuständig.

Portfolio: Stage-V-Generatoren (Diesel/HVO), BESS und Hybrid, USV, mobile
Transformatoren, Mittelspannungsverteilung, Lastbänke, Netzqualitätsmessung.

Differenzierung: einziger Schweizer Vermieter mit PQ-Messung nach
IEC 61000-4-30:2025 Klasse A (LINAX PQ5000-Mobile, METAS-zertifiziert) und
Reporting nach EN 50160.

Ziel dieses Projekts: die Schweizer Rechenzentrums-Pipeline systematisch erfassen
und wöchentlich aktualisieren, damit Burak Projekte im richtigen Zeitfenster
anspricht statt zu spät.

---

## 2. Ton und Sprache

- Deutsch, Du-Form, direkt, wie ein Gespräch unter Fachleuten.
- Schweizer Schreibweise, also ss statt ß.
- Keine Gedankenstriche als Stilmittel. Bindestriche in Komposita sind normal.
- Keine Emojis, kein Konzernsprech, keine Floskeln, keine KI-Disclaimer.
- Kurze Frage bekommt kurze Antwort. Kein Aufblasen der Antwortlänge.
- Wahrheit vor Zustimmung. Ist eine Annahme von Burak falsch, sag es zuerst,
  dann die Lösung.

---

## 3. Absolute Regeln

Diese Regeln gelten in jeder Ausgabe, auch wenn niemand danach fragt.

1. **Quellenpflicht.** Jede Angabe im Radar braucht URL und Datum in Spalte T und U.
   Ohne Quelle kein Eintrag.
2. **Keine erfundenen Werte.** Kapazitäten, Termine, Namen, Normen und Preise
   werden nie geschätzt. Was nicht belegt ist, wird als `prüfen` eingetragen.
   Ein plausibel erfundener Wert ist der teuerste Fehler in diesem Projekt.
3. **Owen-Gate.** Keine Aussage zur Flottenverfügbarkeit ohne schriftliche
   Bestätigung von Owen Farron. Auch nicht intern als Annahme.
4. **CHF-Sperre.** Keine Preise in kundenseitigen Texten. Nur ARM-Tarif-Platzhalter,
   die der Innendienst füllt.
5. **PQ-Pflichtlinie.** LINAX PQ5000-Mobile nach IEC 61000-4-30:2025 Klasse A mit
   EN 50160-Reporting ist Standardposition in jedem Stromangebot, nie Option und
   nie Aufpreis.
6. **Keine kVA-Regel.** Keine Leistungsempfehlung ohne die vollständige
   8-Schritt-Auslegung (Lastliste, kVA-Umrechnung, 80-Prozent-Regel nach
   NIN 2020 / SN 411000, Anlaufkorrektur, Höhen- und Temperatur-Derating,
   Flottenauswahl, Spannungsabfall, Treibstoff und Autonomie).
7. **Namenssperre Innendienst.** Namen von Innendienst-Kolleginnen und -Kollegen
   erscheinen nie in kundenseitigen Dokumenten. Dort steht "Innendienst" oder
   "Back-Office".
8. **Derating.** Auf Aggreko-EU-Equipment gilt der Faktor 0.93 bei 415 V auf 400 V.

---

## 4. Die Datei

`MiT_Datacenter_Radar_CH_V1.0.xlsx`, sieben Blätter. Struktur nicht verändern,
Blattnamen nicht umbenennen, Spalten nicht verschieben. Neue Informationen kommen
in bestehende Spalten oder als neue Zeile, nie als neue Spalte ohne Rückfrage.

### 00_Anleitung
Fliesstext, Bedienungsanleitung und Update-Prompt. Nur anfassen, wenn sich der
Prozess ändert.

### 01_Dashboard
Reine Formelzellen, die auf `02_Projekt_Radar` Zeilen 5 bis 45 zeigen.
**Niemals Werte hineinschreiben.** Wenn das Radar über Zeile 45 hinauswächst,
müssen die Bereiche in allen Dashboard-Formeln mitwachsen. Das ist der einzige
Grund, Dashboard-Formeln anzufassen.

### 02_Projekt_Radar
Kopfzeile in Zeile 4, Daten ab Zeile 5. Spalten:

| Sp. | Kopf | Inhalt |
|---|---|---|
| A | Ref | Projektreferenz `MiT-[TYPE]-[ORT]-[JAHR]-[NNN]`, nur wenn MiT aktiv am Projekt ist |
| B | Projekt / Campus | Name des Projekts. Leeres Feld heisst: Zeile zählt nicht als Projekt |
| C | Betreiber | Eigentümer oder Betreiber |
| D | Standort | Gemeinde |
| E | Kt. | Kantonskürzel |
| F | Kapazitaet_MW | Zahl, nur wenn belegt. Sonst `prüfen` |
| G | Phase | Nur aus Dropdown, siehe unten |
| H | IBN_Ziel | Inbetriebnahme oder RFS laut Quelle |
| I | GU_TU | Generalunternehmer oder Totalunternehmer |
| J | Fachplaner_Elektro | Elektro- oder Gebäudetechnikplaner |
| K | Kanal_Prio | Über welchen Kanal MiT reinkommt, aus Dropdown |
| L | MiT_Chance | Welche Leistung konkret passt |
| M | Ansprache_Fenster | Wann angesprochen wird |
| N | Prio | A, B oder C |
| O | Status_Kontakt | Dropdown, **von Burak gepflegt** |
| P | Letzter_Kontakt | Datum, **von Burak gepflegt** |
| Q | Wiedervorlage | Datum, **von Burak gepflegt** |
| R | Tage_bis_WV | **Formel, nicht anfassen** |
| S | Ampel | **Formel, nicht anfassen** |
| T | Quelle_URL | Pflichtfeld |
| U | Quelle_Stand | Datum der Quelle, Pflichtfeld |
| V | Naechster_Schritt | **von Burak gepflegt**, Vorschläge dürfen ergänzt werden |
| W | Bemerkung | Kontext, Einschränkungen, offene Punkte |

Die gelb hinterlegten Spalten O, P, Q und V gehören Burak. Inhalte dort nur
ergänzen, wenn er es sagt, und nie überschreiben.

Formeln in R und S, jeweils mit der eigenen Zeilennummer:

```
R:  =IF(Q5="","",Q5-TODAY())
S:  =IF(Q5="","-",IF(Q5<TODAY(),"UEBERFAELLIG",IF(Q5-TODAY()<=7,"DIESE WOCHE","ok")))
```

Jede neue Zeile bekommt diese beiden Formeln, das Datumsformat `DD.MM.YYYY` in
P und Q sowie die gelbe Füllung `FFF2CC` in O, P, Q und V.

Dropdown-Werte, exakt so schreiben, sonst zählt das Dashboard falsch:

- **G Phase:** Planung, Bewilligung, Baustart, Rohbau, Fit-out, Commissioning,
  Betrieb, Ausbau, Verzoegert, Gestoppt
- **O Status_Kontakt:** Kalt, Angeschrieben, Erstkontakt, Erstgespraech,
  Qualifiziert, Offerte, Gewonnen, Verloren, Ruhend
- **N Prio:** A, B, C
- **K Kanal_Prio:** Betreiber, GU/TU, Fachplaner, Ausschreibung,
  Elektro-Installateur

### 03_Kontakte
Kopf in Zeile 4, Daten ab 5. Spalten: Firma, Rolle_Funktion, Name, Kanal_Typ,
Projekt_Ref, E-Mail, Telefon, LinkedIn, Beziehungsstatus, Letzter_Kontakt,
Naechster_Touchpoint, Touchpoint_Nr, Notiz.

Regel: pro Projekt mindestens drei Zeilen, also Betreiber, GU/TU und Fachplaner.
Kontaktdaten nur eintragen, wenn sie aus einer öffentlichen Quelle oder von Burak
stammen. Keine E-Mail-Adressen aus Namensmustern ableiten.

### 04_Akquise_Tracker
Touchpoint-Sequenz, statisch. Nur ändern, wenn Burak den Prozess ändert.

### 05_Quellen_Montag
Die feste Recherche-Reihenfolge. Nach jedem Update das Prüfdatum in Spalte F setzen.

### 06_Changelog
Kopf in Zeile 4, Daten ab 5. Spalten: Datum, KW, Projekt, Was hat sich geaendert,
Quelle_URL, Konsequenz fuer MiT. Jede Änderung am Radar bekommt hier eine Zeile.
Ohne Changelog-Eintrag gilt eine Änderung als nicht passiert.
KW-Formel: `=WEEKNUM(DATE(2026,8,29),21)` mit dem jeweiligen Datum.

---

## 5. Technische Ausführung

Python mit `openpyxl`. Nie `pandas.to_excel` auf diese Datei, das zerstört
Formatierung, Dropdowns und Formeln.

**Gotchas, die hier schon Schaden angerichtet haben:**

- `load_workbook(data_only=True)` liefert Werte ohne Formeln. Wird eine so
  geladene Datei gespeichert, sind **alle Formeln unwiderruflich weg**.
  Zum Schreiben immer ohne `data_only` laden.
- openpyxl schreibt Formeln ohne zwischengespeicherte Werte. Direkt nach dem
  Speichern liest jedes Tool `None` in Formelzellen. Excel rechnet beim Öffnen
  neu, das ist normal und kein Fehler. Für eine Prüfung im Terminal einmal mit
  LibreOffice neu rechnen lassen, falls installiert:
  `soffice --headless --convert-to xlsx --outdir tmp datei.xlsx`
- `ISOWEEKNUM`, `XLOOKUP`, `FILTER`, `UNIQUE` und `SORT` nicht verwenden.
  Stattdessen `WEEKNUM(...;21)` und `INDEX`/`MATCH`.
- Vor jedem schreibenden Lauf eine Kopie anlegen:
  `MiT_Datacenter_Radar_CH_V1.0_backup_JJJJ-MM-TT.xlsx`. Maximal die letzten
  vier Backups behalten, ältere löschen.
- Zeilen werden **nie gelöscht**. Ein totes Projekt bekommt Phase `Gestoppt`
  und eine Bemerkung, damit die Historie erhalten bleibt.
- Dubletten prüfen vor dem Anlegen: Abgleich über Betreiber plus Standort, nicht
  über den Projektnamen, weil Betreiber ihre Anlagen umbenennen.

---

## 6. Der Montags-Lauf

Auslöser ist `/dc-update` oder ein Satz wie "DC-Radar Update KW xx".
Ablauf in dieser Reihenfolge, ohne Abkürzung:

**Schritt 1, Bestand lesen.**
Radar und Changelog laden, letzten Update-Stand aus dem Changelog holen.
Kurz ausgeben, wie viele Projekte drin sind und wann zuletzt aktualisiert wurde.

**Schritt 2, Recherche.**
WebSearch und WebFetch entlang Blatt `05_Quellen_Montag`, in dieser Reihenfolge:
netzwoche.ch, it-markt.ch, inside-it.ch, itreseller.ch, datacenter-insider.de,
simap.ch, baublatt.ch, amtsblattportal.ch sowie die kantonalen Portale von ZH,
AG, SH, SG, BS und GE, LinkedIn-Seiten der Betreiber (Vantage, Green, Digital
Realty, NorthC, STACK, Equinix, FlexBase), LinkedIn-Seiten von GU und Planern
(Implenia, ERNE, Steiner, Halter, Amstein + Walthert, HKG Engineering, Gruner),
die Firmen-Newsrooms selbst, regionale Zeitungen für Einsprachen und
Verzögerungen, dazu EVU-Meldungen von EKZ, EKS, AEW, IWB und ewz.

Pro bestehendem Projekt prüfen: Phase, IBN-Termin, Verzögerung, GU/TU,
Fachplaner. Zusätzlich nach neuen Projekten suchen.

Stehen die Websuch-Werkzeuge nicht zur Verfügung, den Lauf abbrechen und
sagen, dass ohne Recherche kein Update entsteht. Nicht aus dem Gedächtnis füllen.

**Schritt 3, bewerten.**
Firmenmeldung schlägt Fachmedium, Fachmedium schlägt Regionalzeitung,
Regionalzeitung schlägt Aggregator. Widersprechen sich zwei Quellen, kommt der
Widerspruch in Spalte W und beide URLs in T. Nicht selbst entscheiden, welche
Quelle recht hat.

**Schritt 4, schreiben.**
Radar aktualisieren, Quelle und Quellendatum mitschreiben, Formeln und gelbe
Spalten unangetastet lassen. Neue Zeilen vollständig formatieren.
Prüfdaten in `05_Quellen_Montag` Spalte F setzen.

**Schritt 5, Changelog.**
Eine Zeile pro Änderung, mit Konsequenz für MiT. "Fit-out gestartet" ist keine
Konsequenz. "Lastbank-Entscheid fällt jetzt, Fachplaner ansprechen" ist eine.

**Schritt 6, Bericht im Terminal.**
Genau dieses Format, nicht länger:

```
DC-RADAR KW xx | Stand TT.MM.JJJJ

NEU IM RADAR
  <Projekt, Betreiber, Ort, MW, Phase, Quelle>

VERAENDERT
  <Projekt: was vorher, was jetzt, Konsequenz>

FENSTER OFFEN, DIESE WOCHE HANDELN
  1. <Projekt> | <Kanal> | <konkreter erster Schritt>
  2. ...
  3. ...

WIEDERVORLAGEN UEBERFAELLIG
  <Projekt, Datum, letzter Kontakt>

LUECKEN
  <was nicht belegbar war und beim naechsten Lauf zu klaeren ist>
```

Maximal drei Projekte unter "Fenster offen". Wer neun Prioritäten hat, hat keine.

---

## 7. Wie priorisiert wird

Das Zeitfenster entscheidet, nicht die Projektgrösse.

- **Planung und Bewilligung:** zu früh für Lastbank. Richtig für Beziehungsaufbau
  beim Fachplaner.
- **Baustart und Rohbau:** Baustrom, Bridging, Trocknung. Kanal ist der GU.
- **Fit-out minus sechs Monate:** hier fällt der Entscheid über den
  Commissioning-Lasttest. Das ist das wichtigste Fenster im ganzen Radar.
- **Commissioning:** Lastbank, Heat-Load-Test, Generator-Abnahme, USV-Test.
  Wer erst jetzt anruft, ist meist zu spät, weil die Leistung im MEP-Vertrag steckt.
- **Betrieb:** Wartungsfenster, Netzanschlussarbeiten des EVU, Batterietausch,
  Bridging Power, PQ-Audit.

**Drei-Kanal-Regel.** Der Betreiber entscheidet über Budget, der GU vergibt in der
Bauphase, der Fachplaner schreibt aus. Ein Planer ist zehn Projekte, ein Betreiber
ist eines. Bei Vorschlägen für den nächsten Schritt immer zuerst den Planer- und
GU-Kanal prüfen, bevor eine Betreiberansprache vorgeschlagen wird.

**Verzögerung ist eine Chance.** Meldet eine Quelle Netzverzug, Einsprache oder
verschobene Inbetriebnahme, ist das ein Signal für Bridging Power und gehört
sofort in den Bericht, nicht nur ins Radar.

---

## 8. Was Claude Code hier nicht tut

- Keine Kundenmails verschicken oder Termine buchen.
- Keine Preise, Margen oder Einkaufskonditionen in Dateien schreiben, die den
  Ordner verlassen könnten.
- Keine Kundennamen oder Projektreferenzen in externe Texte übernehmen. In
  Angeboten werden Referenzen anonymisiert, zum Beispiel "Rechenzentrum in der
  Ostschweiz", bis Burak die Freigabe bestätigt.
- Keine Kontaktdaten aus Namensmustern konstruieren.
- Keine Zusammenfassung eines Artikels, die den Originaltext ersetzt. Kurz
  paraphrasieren und verlinken.

---

## 9. Weitere Aufgaben in diesem Ordner

Neben dem Wochenlauf kann hier anfallen:

- **Kaltakquise-Texte** für den Commissioning-Kanal. Immer zwei Varianten,
  zurückhaltend und offensiv, je mit einer Zeile Begründung. Betreff konkret,
  ohne Fragezeichen. Absender führt Aggreko in der ersten Zeile, weil
  Mobil in Time internationalen DC-Bauherren nichts sagt.
- **Gesprächsvorbereitung.** Vor jedem wichtigen Termin die drei
  wahrscheinlichsten Einwände mit je einer Antwort.
- **Auswertungen** aus dem Radar, zum Beispiel Kapazität nach Kanton oder
  Projekte nach Phase. Ergebnis als neues Blatt oder als Terminal-Ausgabe,
  nie als Überschreiben bestehender Blätter.

Am Ende komplexer Themen: der eine Hebel mit dem grössten Wirkungsgrad,
nicht zehn Optionen.

---

## 10. Der Aktualisiere-Trigger und die Kontakte-Datei

Sagt Burak "aktualisiere" (auch "aktualisiere, recherchiere und mache weiter"),
laeuft der volle Montags-Lauf aus Abschnitt 6, plus:

1. `MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx` mitpflegen: neue Erkenntnisse aus
   der Recherche als neue Zeilen, nie bestehende Eintraege von Burak
   ueberschreiben. Blaetter nie loeschen oder umbauen, Auswertungen nur als
   neues Blatt.
2. Wochenplan als neues Blatt `Wochenplan_KWxx` in die Kontakte-Datei:
   fuenf Kontakte pro Tag, Montag bis Freitag, kuratiert nach Radar-Fenster.
   Bereits kontaktierte Personen (Status im Kontakt-Log) rotieren nach hinten,
   Wiedervorlagen haben Vorrang vor Neukontakten.
3. Dashboard regenerieren und auf die bestehende Artifact-URL publizieren.
4. Alles committen und pushen.

**Datenqualitaet Kontakt-Log:** Im Log aus dem Aggreko-Tracker sind in
mehreren Zeilen Name, Firma und E-Mail gegeneinander verschoben. Jede
E-Mail-Adresse, deren Namensteil nicht zum Kontaktnamen passt, gilt als
unverifiziert: erst telefonisch klaeren, nie auf die Log-Mail schreiben.
Im Wochenplan sind solche Zeilen mit DATENQUALITAET PRUEFEN markiert.
