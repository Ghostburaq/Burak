# Änderungsliste — Ausbau CH_MiT_Strom_Customer_CEO_CFO_MASTER__2_.xlsx

Grundlage: gelieferter Stand vom 10.08.2026 (Werte-Fingerabdruck 4f9385248d683e19).
Beide unantastbaren Regeln eingehalten: Bandtabelle «⚖️ Wahrscheinlichkeit» B17:D22
unverändert (sechs Bänder, oberstes «100 % · WON» mit Faktor 1.0, darunter
0/0.3/0.5/0.9); keine Marge in irgendeinem Bericht, Kostenspalten J–N bleiben
unausgewertet stehen.

## Block 1 — Nachweis und Klarheit

| Blatt | Bereich | Änderung |
|---|---|---|
| CEO Report | D219–D229 | Neue Spalte «Anzahl» im Abschnitt «5. Qualität & Nachweis»: WON gemeldet / davon belegt / noch zu belegen / Pipeline brutto / bereinigt — je Anzahl UND CHF (1.1). Belegt = PO-Nr. UND Belegdatum UND vollständiger Einstand (Hilfsspalte AT). |
| CEO Report | A253:N260 | Neue Tabelle «7. Vertragsarten — WON-Volumen nach Vertragsart» (1.2): Einzelauftrag, Rahmenvertrag – Abruf bestätigt, Abrufbereitschaft, Option/Reservation, ohne Angabe. «Abrufbereitschaft» und «ohne Angabe» orange (F47B20). TOTAL-Zeile gleicht live gegen «WON gemeldet» ab (rote Warnung bei Abweichung). |
| CEO Report, Dashboard | A8 | Infozeile ergänzt: «Pipeline brutto: … CHF · bereinigt: … CHF» — brutto und bereinigt stehen überall nebeneinander (1.3); im CEO-Abschnitt 5 zusätzlich als eigene Zeilen 224/225 mit Anzahl. |
| 📋 Definitionen & Klärung | Zeilen 15–23 | Unverändert — die live gerechnete Liste der offenen Pflichtangaben (1.4) war vorhanden und wurde nur verifiziert (WON ohne Beleg / ohne Einstand / ohne Zeitraum / ohne Vertragsart / ungeklärte Mehrfachkunden, alles Formeln). |

## Block 2 — Gewichtete Pipeline transparent

| Blatt | Bereich | Änderung |
|---|---|---|
| CEO Report | A215:N217 | Zerlegung der gewichteten Pipeline (2.1): «davon gewonnene Aufträge (Faktor 100 %)» und «davon offene Offerten (Aggreko-Faktoren 0/30/50/90 %)», beide als SUMMENPRODUKT-Formel; Zeile 217 prüft live: Summe der Zerlegung = TOTAL-Zeile (rote Warnung bei Abweichung). |
| CEO Report | A262:N267 | Neuer Abschnitt «8. Kontrollrechnung» (2.2): Weg 1 = SUMME über Spalte Q, Weg 2 = SUMMENPRODUKT über Volumen (numerisch, AL) × Faktor (AJ). Abweichung > CHF 1 → rote, fette Warnzeile (bedingte Formatierung), sonst grüner Bestanden-Text. |
| 📑 Executive PDF | Zeilen 10–45 | Einseiter neu aufgebaut (2.3), A4 hochformat, Druckbereich A1:H49, fitToPage 1×1. Enthält: Auftragseingang (KPI-Kacheln), Pipeline brutto/bereinigt, gewichtete Pipeline mit Zerlegung + Kontrollzeile, Qualität & Nachweis mit Nachweisquote, **Top 5 offene Offerten nach Volumen** (neu, ersetzt die WON-Top-5 — der Auftragseingang bleibt als KPI), offene Punkte (live aus dem Definitionsblatt) mit Gesamturteil. Status-Verteilung und Bandtabellen-Spiegel entfielen (Platz; stehen weiterhin im CEO Report/Dashboard). |
| MiT Strom Pipeline | BD5:BD860 | Neue versteckte Hilfsspalte «_OffertSort» (Rangschlüssel für die Top-Offerten; Formel, kein Festwert). |

## Block 3 — Zeitraum nutzbar machen

| Blatt | Bereich | Änderung |
|---|---|---|
| MiT Strom Pipeline | BC5:BC860 | Neue versteckte Hilfsspalte «_ZeitOffenNr»: laufende Nummer je aktivem Deal ohne Zeitraum (AY=0). |
| 📋 Definitionen & Klärung | A79:H131 | Neuer Abschnitt «8. Erfassungsliste Projektzeitraum» (3.1): live gerechnete Liste aller aktiven Deals ohne Start-/Enddatum (Kunde, Status, Volumen, Kurzstatus), 50 Plätze, schrumpft automatisch beim Nachtragen. Kopfzeile zeigt «Noch offen: X von Y aktiven Deals». |
| CEO Report | A250:N250 | Hinweiszeile unter der Startmonat-Tabelle (3.2): «⚠ Zeiträume noch nicht erfasst: X von Y aktiven Deals offen» — verschwindet automatisch (leere Zeile), sobald alle Zeiträume erfasst sind. Die Tabelle selbst (Zeilen 232–249, auf Hilfsspalte AX) war vorhanden und blieb unverändert. |
| MiT Strom Pipeline | BB | Nur geprüft (3.3): der Kurzstatus meldet «⚠ Ende vor Start», wenn Projektende vor Projektstart liegt — im Verhaltenstest bestätigt. |

## Block 4 — Diagramme (Design: Dunkelblau 15243A, Akzent Orange F47B20, keine 3D, Datenbeschriftung am Balken, Tausendertrennzeichen, keine Legende wo eine Farbe reicht)

| Blatt | Diagramm | Änderung |
|---|---|---|
| 📊 Diagramme | oben links (4.1) | Balken horizontal: **aktive Pipeline nach Segment, absteigend** (grösster Balken oben). Quelle: _data!R2:S30 — sortiert per Formel (LARGE/INDEX/MATCH). |
| 📊 Diagramme | oben rechts (4.2) | Balken horizontal: **aktive Pipeline nach Kanton, Top 10**. Quelle: _data!V2:W11. |
| 📊 Diagramme | Mitte links (4.3) | Säulen: **Volumen nach Status**, WON-Säule in Orange. Quelle: _data!B2:D11. |
| 📊 Diagramme | Mitte rechts (4.4) | Säulen: **gewichtete Pipeline zerlegt** — gewonnene Aufträge (orange) und offene Offerten (dunkelblau). Quelle: _data!X2:Y3. |
| 📊 Diagramme | unten (4.5) | Säulen: **Volumen nach Startmonat** (vorbereitet; füllt sich, sobald Zeiträume erfasst sind). Quelle: _data!Z2:AA13, Bezugsjahr = aktuelles Jahr. |
| Dashboard | 2 Diagramme | Gleiches Design: Ring «Status (Anzahl)» mit fester Farbpalette (WON orange), Balken «Status nach Volumen» dunkelblau mit WON in Orange. |
| _data (versteckt) | G28:G29, J–AA | Segmentliste um «Datacenter» und «Elektroplaner» ergänzt — **Fund:** beide kamen in der Pipeline vor, fehlten aber in der Liste, das alte Segment-Diagramm zeigte deshalb CHF 1'072'286 zu wenig. Neu zusätzlich eine Wachhund-Zeile: fehlt künftig ein Segment, erscheint im Diagramm ein eigener Balken «Übrige (Segment fehlt in der Liste)» statt still zu wenig. Alle Diagrammquellen sind Formelbereiche ≤ Zeile 864, keine statischen Wertelisten, keine Ganzspaltenbezüge. |

## Kontrollen

- **K1 Kernzahlen** nach jedem Block und am Ende exakt: 66 Datenzeilen · WON 12 Deals / CHF 1'428'553.13 · aktive Pipeline 46 Deals / CHF 6'862'149.23 · gewichtet CHF 1'628'425.59. Zerlegung: WON 1'428'553.13 + offene Offerten 199'872.46 = 1'628'425.59. Beide Kontrollwege (SUMME Q, SUMMENPRODUKT I×AJ) identisch, Abweichung 0.00.
- **K2** Fehlerwert-Scan (data_only) über alle Blätter: 0 Treffer.
- **K3** Kein Ganzspaltenbezug, alle Bereiche ≤ Zeile 864 (Formel-Scan über alle Blätter).
- **K4** Keine XVERWEIS/FILTER/EINDEUTIG/SORTIEREN/TEXTVERKETTEN/LET-Funktionen — nur SUMMENPRODUKT, SUMMEWENN(S), ZÄHLENWENN(S), INDEX/VERGLEICH, KGRÖSSTE, VERWEIS.
- **Verhaltenstest** (Wegwerfkopie, je mit LibreOffice-Neuberechnung): Zeitraum nachtragen → Erfassungsliste 46→45, CEO-Hinweis «45 von 46», Monatstabelle August zählt den Deal, Dauer = 10 Kalendertage, Startmonat-Diagramm zeigt das Volumen. Ende vor Start → «⚠ Ende vor Start», zählt nirgends. PO+Datum+Vertragsart setzen → Vertragsarten-Tabelle und Nachweis reagieren korrekt.
- **K5 Rundreise** LibreOffice öffnen+speichern, danach K1/K2 wiederholt: unverändert. Danach Dateibereinigung (doppelte benannte Bereiche) und Excel-Verträglichkeitsprüfung auf ZIP/XML-Ebene: 0 Befunde.
