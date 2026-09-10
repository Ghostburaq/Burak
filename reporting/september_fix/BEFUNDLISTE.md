# Befundliste — Bugfix-Durchgänge September 2026

Grundlage: Ihre hochgeladene Arbeitsdatei `CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx`
(von Excel gespeichert, 75 Deals — 9 neue seit August, Status geändert).
Alle Ihre Daten wurden unverändert übernommen; repariert wurde ausschliesslich
die Rechenstruktur.

## Warum «alle Mappen nicht mehr klappten» — die drei Ursachen

**U1 — Eine Zeile wurde gelöscht (Bereich der alten Zeile 13).**
Die drei versteckten Laufzähler-Spalten (`_cnt_won`, `_cnt_offerte`, `_cnt_opp`)
sind Kettenformeln: jede Zeile baut auf der Zeile darüber auf. Nach dem Löschen
stand in Zeile 13 `N(#REF!)`, und der Fehler pflanzte sich durch **847 Folgezeilen
pro Spalte** fort (2'541 Fehlerzellen). Über genau diese Zähler finden die
Listen in CEO Report und Dashboard ihre Einträge — deshalb war überall
«WON / LOST / Offerte» leer oder falsch. → **Behoben** (Runde 1): Kettenanfang
in Zeile 13 neu verankert; alle 847 Zeilen je Spalte rechnen wieder.

**U2 — Die Spalte «Wahr. % bisher» (AI) wurde gelöscht.**
Excel hat fast alle Bezüge automatisch nachgezogen (alle Hilfsspalten liegen
jetzt eine Position weiter links: `_GewFaktor` = AI … `_OffertSort` = BC).
Direkt zerbrochen sind die Stellen, die die Spalte selbst brauchten:
das Umschlüsselungs-Protokoll auf «⚖️ Wahrscheinlichkeit» (E52:G58, E62:E64 —
27 `#REF!`-Formeln) und die Live-Zeile G12 im Definitionsblatt.
→ **Behoben** (Runde 2): Protokoll sichtbar eingefroren («—» + Hinweis, die
Ursprungswerte existieren nicht mehr); die Live-Kontrolle «aktive Deals
ausserhalb der Skala» rechnet weiter; G12 neu formuliert. Zusätzlich wurden
**alle** Spaltennennungen in den Erläuterungstexten (CEO, Definitionen,
Herleitung inkl. der kompletten Hilfsspalten-Dokumentation) auf die neue
Spaltenlage umgeschrieben — verifiziert per Wort-Diff gegen den Vorher-Stand.

**U3 — Zeile 80 (Axpo Power AG) wurde per «Zeile einfügen» erstellt.**
Eine eingefügte Zeile hat keine der 26 Formelspalten — der Deal existierte
für keine Auswertung. Ausserdem wurde bei den 10 neuen Deals die Dauer direkt
in Spalte G getippt und hat dort die Formel überschrieben.
→ **Behoben** (Runde 2): Zeile 80 trägt wieder alle Formeln; die 10
Dauer-Handwerte (214/14/7/7/7/7/13/8/5/120 Tage) wurden in die dafür
vorgesehene Handwert-Spalte übernommen — sie bleiben sichtbar und werden
automatisch ersetzt, sobald Projektstart/-ende als Datum erfasst sind.

## Verifikation «jede einzelne Formel»

- **Formel-Vollabgleich** (6'584 Formelzellen) jeder Formel Ihrer Datei gegen
  den strukturell korrekten August-Stand, unter Berücksichtigung der
  Spaltenverschiebung: nach den Reparaturen bleiben ausschliesslich die
  beabsichtigten Abweichungen (eingefrorenes Protokoll).
- **Unabhängige Nachrechnung** aller Kernverknüpfungen (Dashboard-Kacheln,
  CEO-Abschnitte inkl. Zerlegung/Kontrollrechnung/Vertragsarten, Executive
  PDF, ⚖️-Bandtabelle, Diagrammdaten, Erfassungsliste) gegen ein
  Python-Modell der Pipeline-Rohdaten.
- **Verhaltenstest** mit LibreOffice-Neuberechnung: neuer Deal in freier
  Zeile → alle Blätter folgen; Zeitraum nachtragen → Dauer/Monatstabelle/
  Erfassungsliste reagieren; Ende vor Start → Warnung; WON→LOST → alle
  Zahlen fallen korrekt zurück.
- Fehlerwert-Scan, Bereichs-/Funktions-Kompatibilität (≤ Zeile 864, keine
  XVERWEIS/FILTER/…), Bandtabellen-Regel (100 % · WON), Marge-Regel,
  Excel-Verträglichkeit auf ZIP/XML-Ebene, LibreOffice-Rundreise.

## Damit es nicht wieder passiert (Runde 3)

1. **Neuberechnung beim Öffnen erzwungen** (`fullCalcOnLoad`): Excel rechnet
   beim Öffnen grundsätzlich alles neu — «Zahlen bewegen sich nicht» kann
   nicht mehr am gespeicherten Zustand liegen.
2. **Leitplanken-Blattschutz ohne Passwort:** Alle Eingabespalten der
   Pipeline (A–F, H–P, R–X, AA–AG, Zeilen 6–860) bleiben frei beschreibbar,
   der AutoFilter bleibt nutzbar. Gesperrt sind nur die Formelspalten, die
   versteckten Hilfsspalten und das Einfügen/Löschen von Zeilen und
   Spalten — exakt die drei Aktionen, die die Mappe zerlegt haben.
   Neue Deals: einfach in die nächste freie Zeile schreiben (vorbereitet
   bis Zeile 860). Berichtsblätter sind reine Ausgabe und komplett gesperrt;
   im Definitionsblatt bleiben die gelben Stellschrauben offen.
   Der Schutz hat **kein Passwort** — «Überprüfen → Blattschutz aufheben»
   genügt, wenn ein struktureller Eingriff wirklich gewollt ist.
