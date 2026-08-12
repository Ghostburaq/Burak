# MiT Strom Schweiz — Sales-Reporting (Master)

**Masterdatei:** [`CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx`](CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx)
&nbsp;·&nbsp; Ansehen ohne Excel: [PDF-Vorschau](vorschau.pdf)

Ab sofort ist **diese Datei die einzige gültige Version**. Alle weiteren
Änderungen fliessen hier ein — die Vorversion liegt nur noch als
[`quelle_stand_vor_update.xlsx`](quelle_stand_vor_update.xlsx) zum Vergleich bei.

---

## Was Aggreko verlangt hat

**1. Probability to Win % — verbindliche Skala**

| Wert | Bedeutung |
|------|-----------|
| 0 %  | Nichts — keine Opportunität. |
| 10 % | «Platzhalter»-Thema: Bedarf/Pain beim Kunden erkannt und für ein späteres Gespräch in der Pipeline geparkt. Ebenfalls 10 % für sehr grosse Opportunitäten, die nicht so stark wie mit 30 % gewichtet werden sollen, sowie für Contingency-Pläne. |
| 30 % | Die Opportunität lebt und ist gesund, es ist aber offen, ob sie tatsächlich on-hire geht. |
| 60 % | Sehr gute Gewinnchance, der Kunde committet sich aber nicht mit einer PO. Das Fleet-Team überwacht die On-/Off-Hire-Daten. |
| 90 % | Auftrag ist sicher, es fehlt nur PO oder dokumentiertes Commitment. Das Fleet-Team erfüllt die Quote in dieser Stufe im OF. |
| **100 %** | **Ergänzung MiT CH, nicht Teil der Aggreko-Liste:** Auftrag erhalten. Unterschriebene Bestellung oder gültige PO liegt vor. Der Auftrag zählt voll und wird nicht mehr abgewertet. Gilt ausschliesslich für Status WON. |

**2. Pipeline (Weighted) = Umsatz × Gewichtungsfaktor**

Der Faktor wird aus dem Feld *Effective Probability* abgeleitet:

| Effective Probability | Faktor |
|-----------------------|--------|
| 0 – 44 %              | 0 %    |
| 45 – 59 %             | 30 %   |
| 60 – 89 %             | 50 %   |
| 90 – 99 %             | 90 %   |
| **100 % (WON)**       | **100 %** |

---

## Umschlüsselung auf die Aggreko-Skala

**Ausgangslage:** In der Liste standen Wahrscheinlichkeiten von 20 %, 50 %, 80 %
und 100 % — Werte, die es auf der Aggreko-Skala (0 / 10 / 30 / 60 / 90 %) nicht
gibt. Alle 66 Zeilen sind jetzt auf eine Skalenstufe gesetzt.

**Leitregel:** Wo eine Skalenstufe denselben Gewichtungsfaktor hat, wird sie
gewählt — der gewichtete Umsatz bleibt dann unverändert. Nur wo das unmöglich
ist, entscheidet die Aggreko-Definition.

| bisher | neu | Faktor bisher | Faktor neu | Zeilen | gewichtet bisher | gewichtet neu | Wirkung |
|--------|-----|---------------|------------|--------|------------------|---------------|---------|
| 0 %   | 0 %  | 0 %  | 0 %  | 21 | 0 | 0 | unverändert |
| 10 %  | 10 % | 0 %  | 0 %  | 1  | 0 | 0 | unverändert |
| 20 %  | 30 % | 0 %  | 0 %  | 6  | 0 | 0 | unverändert |
| **50 %** | **30 %** | **30 %** | **0 %** | **22** | **717'509** | **0** | **Faktor ändert sich** |
| 80 %  | 60 % | 50 % | 50 % | 2  | 134'250 | 134'250 | unverändert |
| 90 %  | 90 % | 90 % | 90 % | 2  | 65'622 | 65'622 | unverändert |
| **100 %** | **100 %** | **90 %** | **100 %** | **12** | **1'285'698** | **1'428'553** | **gewonnener Auftrag zählt voll** |
| **Total** | | | | **66** | **2'203'080** | **1'628'426** | **−574'654** |

### Der strukturelle Befund

**Kein Wert der Skala fällt in das Gewichtungsband 45–59 % (Faktor 30 %).**
Die Skala kennt 0 / 10 / 30 / 60 / 90 — zwischen 45 und 59 liegt keine Stufe.
Wer die Skala einhält, kann dieses Band nie treffen; es ist in der
Aggreko-Vorgabe angelegt, aber nicht erreichbar.

Genau dort lagen die 22 Deals mit 50 %. Deshalb lassen sich **44 der 66 Zeilen
umschlüsseln, ohne dass sich ein gewichteter Umsatz ändert** — die 22 bei 50 %
können es nicht. Für sie gibt es keine Zuordnung, die das Gewicht erhält.

### Warum 50 % → 30 %

Massgebend ist die Definition, nicht der Zahlenabstand:

- **30 %** = «Die Opportunität lebt, wir wissen aber nicht, ob sie on-hire geht.»
  Das beschreibt eine offene Offerte, deren Ausgang beidseitig möglich ist —
  also genau das, was 50 % ausdrücken sollte.
- **60 %** = «Sehr gute Chance» **und** das Fleet-Team überwacht bereits die
  On-/Off-Hire-Daten. Das ist ein deutlich stärkerer Zustand als «könnte so oder
  so ausgehen».

Rein rechnerisch läge 50 % näher bei 60 %. Die Skala ist aber über ihre
Begründungen definiert, nicht über Abstände — und für einen CEO/CFO-Bericht ist
die vorsichtige Zuordnung die richtige Vorgabe.

**Diese 22 Deals sind einzeln zu bestätigen.** Sie stehen namentlich auf dem
Blatt `⚖️ Wahrscheinlichkeit` mit Volumen und aktuellem Wert. Wo das Fleet-Team
die Daten bereits überwacht, gehört der Deal auf 60 % — eine Zelle in Spalte S,
alles Weitere rechnet nach. Das Blatt zeigt live, wie viele noch auf der Vorgabe
stehen und was die gewichtete Pipeline wäre, wenn alle auf 60 % gingen
(**2'681'419 CHF**).

Der bisherige Wert bleibt in der neuen Spalte **AI «Wahr. % bisher»** erhalten,
damit jede Änderung nachvollziehbar ist.

---

## Rückfragen — was daraus im File wurde

Alle acht Rückfragen von Maria und Oliver sind im Blatt
**`📋 Definitionen & Klärung`** beantwortet, jede mit einer Live-Zahl. Die Regeln
stehen dort, nicht in einer Mail. Ein eigener Test (`tests/audit_fragen.py`)
stellt sicher, dass keine Frage ohne Antwort und ohne rechnende Zahl bleibt.

| Rückfrage | Was im File passiert |
|-----------|----------------------|
| **Negative Margen in Spalte I** | Ursache gefunden: die **MwSt war als Kostenposition erfasst** und wurde vom Umsatz abgezogen. Zusätzlich zeigte sich: bei 36 Zeilen wurde gar nicht kalkuliert, sondern nur der Verkaufspreis in netto + MwSt zerlegt. Auf dieser Datengrundlage trägt keine Margenzahl — **die Marge ist inzwischen ganz aus dem Reporting genommen** (siehe «Was in dieser Runde geändert wurde»). Die Kostenspalten bleiben in der Pipeline erfasst. |
| **Wer verantwortet die Kalkulation?** | Der Einstand wird vom Verkäufer erfasst und vor dem Statuswechsel auf WON vom Innendienst gegengeprüft. Die Regel steht im Definitionsblatt, der Erfüllungsstand pro Zeile in Spalte AH. |
| **Laufen alle Projekte über MiT CH?** | Ja — MiT CH ist die Standardabwicklung. Abweichungen werden in der neuen Spalte **AA «Abwicklung»** erfasst (Aggreko intl. / Partner–Dritte). Eine leere Zelle heisst ausdrücklich MiT CH, nicht «unbekannt». |
| **Wie ist das WON-Volumen zu verstehen?** | Neu dreifach ausgewiesen: **brutto wie erfasst**, **netto ohne MwSt**, und **davon belegt** — belegt heisst Auftrags-/PO-Nr. + Belegdatum + vollständiger Einstand. Aktuell: 1'428'553 brutto, 1'321'511 netto, **0 belegt**. |
| **Datacenter: 660 oder 330 kCHF?** | Entscheidet die neue Variantenlogik: gleiche **Deal-Gruppe (AC)** setzen, die nicht führende Zeile auf **«Alternative – zählt nicht» (AD)**. Dann zählt nur die führende Variante. Die beiden DPR-Zeilen stehen namentlich auf der Klärungsliste. |
| **Wurden Offerten erstellt bzw. liegen Verträge vor?** | Steht nicht mehr im Kommentar, sondern in eigenen Spalten: **AE «Offert-Nr.»** für die versendete Offerte, **AF «Auftrag / PO-Nr.»** und **AG «Beleg-Datum»** für den erteilten Auftrag. Spalte AH «Prüfstatus» zeigt je Zeile, was vorliegt und was fehlt. Aktuell: 0 von 29 Offerten mit Offert-Nr., 0 von 12 Aufträgen mit PO-Nr. und Datum. |
| **Was heisst «Abrufbereitschaft»?** | Neue Spalte **AB «Vertragsart»** mit vier definierten Werten. «Abrufbereitschaft» = Kapazität reserviert, **kein bestätigter Abruf** → gehört nicht in WON, sondern in die Offert-Pipeline. Murg Flums Energie steht namentlich auf der Klärungsliste. |

### Die vier Anpassungen im Detail

1. **Marge** = Nettoumsatz − Einstand (Equipment, Transport, Treibstoff, Personal, Übrige), ohne MwSt. Marge % neu auf den Nettoumsatz bezogen.
2. **Statusdefinition fix**: WON verlangt unterschriebene Bestellung oder gültige PO — mit Offert-Nr. (AE), Auftrags-/PO-Nr. (AF) und Belegdatum (AG) in eigenen Spalten.
3. **Varianten-Kennzeichnung**: Deal-Gruppe + Variante, damit derselbe Entscheid nur einmal ins Volumen läuft. Sicherheitsregel: nur ausdrücklich als Alternative markierte Zeilen fallen weg — eine vergessene Markierung kann nie Volumen verschwinden lassen.
4. **Sperre**: WON ohne vollständigen Einstand oder ohne Beleg fliesst **nicht** in die Kennzahl «belegtes WON». Statt eines Dialogfensters, das ein Import umgeht, wirkt die Sperre über die Zahl selbst — und die Lücke steht offen im Bericht.

### Stand der offenen Punkte

| Punkt | Anzahl | Volumen CHF |
|-------|--------|-------------|
| WON ohne Auftrags-/PO-Nr. und Datum | 12 | 1'428'553 |
| WON ohne vollständigen Einstand | 2 | 10'000 |
| WON ohne Vertragsart | 12 | 1'428'553 |
| Aktive Deals ohne erfassten Projektzeitraum | 46 | 6'862'149 |
| WON ohne erfassten Projektzeitraum | 12 | 1'428'553 |
| Kunden mehrfach in der Pipeline, Variante offen | 17 | 3'368'728 |

Insgesamt **101 offene Pflichtangaben**. Bis sie erfasst sind, ist das
WON-Volumen als «gemeldet» zu lesen, nicht als «belegt» — die Nachweisquote
steht aktuell bei **0 %**.

---

## Wie die Rechnung entsteht

Das Blatt **`🔍 Herleitung & Formeln`** schlüsselt alles auf:

1. **Der Rechenweg in sieben Stufen** — Erfassung → netto machen → Einstand bilden →
   Marge rechnen → Kalkulation prüfen → gewichten → verdichten. Jede Stufe mit
   Live-Wert und Begründung, warum sie so gebaut ist.
2. **Zwei durchgerechnete Beispiele** — Zeile für Zeile, jeder Wert live aus der
   Pipeline geholt:
   - *Wincasa Solothurn* (sauber kalkuliert): 390 000 brutto ÷ 1.081 = 360 777 netto,
     − 272 000 Einstand = **88 777 Marge (24.6 %)**. Wahrscheinlichkeit nach der
     Umschlüsselung 30 % → Band 0–44 % → Faktor 0 % → **0 gewichtet**.
   - *DPR Heat Loadbank* (die Datacenter-Position): 333 790 brutto = 308 779 netto,
     Equipment ebenfalls 333 790 → **−25 011**. Kein Rechenfehler: die Zeile sagt
     Einkauf = Verkauf.
3. **Landkarte der Verknüpfungen** — für jede Kennzahl im Bericht: wie sie gebildet
   wird, aus welcher Spalte, mit welchem Filter.
4. **Spaltenverzeichnis** — alle 54 Spalten mit Formel, Typ, Sichtbarkeit und Zweck.
   Automatisch aus der Mappe erzeugt, kann also nicht veralten.
5. **Warum es so gebaut ist** — zwölf Entscheide, jeweils mit der verworfenen
   Alternative und der Begründung.
6. **Funktionslexikon** — jede verwendete Excel-Funktion, was sie tut, und welche
   bewusst nicht verwendet wurden (XVERWEIS, FILTER, EINDEUTIG — damit die Mappe
   auch in älterem Excel und in LibreOffice rechnet).

### Was die Umstellung zahlenmässig bewirkt

| Fall | Zeilen | Wirkung |
|------|--------|---------|
| **A** — Spalte N enthielt die MwSt | 36 | Betrag bleibt gleich (brutto − MwSt = netto). Geändert hat sich, dass die Zeile jetzt korrekt als «Kosten über Umsatz» oder «nur Preis-Aufteilung» markiert wird statt als geplante Negativmarge dazustehen. |
| **B** — Spalte N war eine echte Kostenposition | 30 | Marge sinkt um die MwSt, weil der Umsatz jetzt netto ist. Beispiel Wincasa: 118 000 → 88 777, Differenz 29 223 = MwSt auf 390 000. Die alte Zahl war zu hoch. |

---

## Wie es umgesetzt ist

Neues Blatt **`⚖️ Wahrscheinlichkeit`** — die Steuerzentrale der Mappe:

1. Skala inkl. Begründungen (DE + englisches Original)
2. Bandtabelle mit den Gewichtungsfaktoren **und** der Live-Auswertung
   (Anzahl Deals, Umsatz, gewichteter Umsatz, Anteil je Band)
3. Selbstkontrolle: rechnet die Bandtabelle dasselbe wie die Pipeline-Spalte Q?
   Plus Zähler für Deals ausserhalb der Skala
4. Änderungsprotokoll

Skala und Faktoren werden **nur dort** gepflegt. Alle Formeln zeigen darauf —
es gibt keine fest eingetippten Prozentsätze in den Berichtsblättern.

### Änderungen je Blatt

| Blatt | Änderung |
|-------|----------|
| `MiT Strom Pipeline` | `Gew.Wert CHF` (Spalte Q) = **Volumen × Aggreko-Faktor**. Spalte S mit Dropdown 0/10/30/60/90 %, gewonnene Aufträge 100 %. Spalten O/P neu «Projektstart» und «Projektende» als echtes Datum, Spalte G rechnet daraus die Dauer. Neue Fachspalten Y–AH: Nettoumsatz, Einstand, Abwicklung, Vertragsart, Deal-Gruppe, Variante, Offert-Nr., Auftrag/PO-Nr., Beleg-Datum, Prüfstatus. Spalte N heisst neu «Übrige Kosten» und enthält keine MwSt mehr. Hilfsspalten liegen ausgeblendet ab AJ. |
| `⚖️ Wahrscheinlichkeit` | neu — Aggreko-Bewertungsmodell |
| `📋 Definitionen & Klärung` | neu — beantwortet jede Rückfrage mit Live-Zahl, enthält Annahmen, Margendefinition, Status- und Vertragsartendefinitionen, Variantenregel, Klärungsliste und die Liste der offenen Pflichtangaben |
| `🔍 Herleitung & Formeln` | neu — der Rechenweg in sieben Stufen, zwei komplett durchgerechnete Beispiele, die Herkunft jeder Berichtszahl, das Verzeichnis aller 54 Spalten mit ihren Formeln, die Begründung jedes Designentscheids und ein Funktionslexikon |
| `Dashboard` | Info-Zeile mit gewichteter Pipeline, Abschnitt 4 «Gewichtete Pipeline», Abschnitt 5 «Qualität & Nachweis», Abschnitt 6 «Zeitliche Verteilung» |
| `CEO Report` | dito, zusätzlich je Deal die Spalten «Auftrag / PO-Nr.» und «Prüfstatus». Der Prüfstatus zeigt hier den Kurzbefund (⛔ Nachweis fehlt · ⚠ Marge negativ · ⚠ nicht kalkuliert · ○ Einstand offen · ✅ belegt · ✔ kalkuliert); die vollständige Aufzählung aller offenen Punkte einer Zeile steht in der Pipeline in Spalte AH |
| `📄 Report` | KPI-Zeilen «⚖️ Gewichtet» und «📋 WON belegt» mit Nachweisquote, Abschnitt «Wahrscheinlichkeits-Bewertung», Block «Zeitliche Verteilung nach Monat des Projektstarts» |
| `📑 Executive PDF` | gewichteter Wert, Bandtabelle und Block «Nachweis & Zeitraum» (WON netto, davon belegt, Nachweisquote, Deals mit Projektzeitraum) |
| `📊 Diagramme` | neues Diagramm «Umsatz vs. gewichtet je Band» |
| `_data` | Bandtabelle als Diagramm-Quelle |

### Nebenbei behoben

Beim vollständigen Audit gefunden und korrigiert:

| Fund | Wirkung | Behoben durch |
|------|---------|---------------|
| **Druckbereich Pipeline** endete bei Zeile 48 | Deals ab Zeile 49 fehlten im Ausdruck — kommentarlos | Druckbereich auf Zeile 90 (quer, Seitenbreite). Zusätzlich Kontrolle auf dem ⚖️-Blatt, die Alarm schlägt, sobald ein Deal darunter erfasst wird |
| **Verwaiste Restformeln** in Pipeline `Q862`/`Q864` | Summierten eine handverlesene Zeilenauswahl, von nichts referenziert — hätten Fehlerwerte erzeugt, sobald einer dieser Deals keinen numerischen Gew.Wert mehr hat | Entfernt (Inhalt im Änderungsprotokoll dokumentiert) |
| **Top-WON-Ranglisten** bei betragsgleichen Deals | Derselbe Deal erschien zweimal, ein anderer fiel aus der Liste (in Report und Executive PDF) | Sortier-Zuschlag in `_WON_Sort`; Volumen wird direkt aus der Volumenspalte geholt |
| **`U4` (Kopfzeile Pipeline)** summierte alle Zeilen inkl. LOST/Declined | Zwei Zellen mit demselben Namen «gewichtete Pipeline» konnten verschiedene Zahlen zeigen | Gleiche Abgrenzung wie überall sonst: nur aktive Status |
| **Skala-Kontrolle** zählte Deals *ohne* Wahrscheinlichkeit als skalenkonform | `COUNTIF` liest eine leere Bezugszelle als 0 — und 0 % steht ja in der Skala | `ISNUMBER`-Wächter; ein Deal ohne Wahrscheinlichkeit gilt jetzt korrekt als offen |
| **Ganzspalten-Bezüge** in Dashboard/CEO Report | 4'278 Formeln über je 1 Mio. Zeilen | Auf Zeile 860 begrenzt — fachlich identisch, spürbar schneller |
| **Abgeschnittene Texte, ####-Zahlen und zu niedrige Zeilen** auf allen Blättern | 149 Stellen, u. a. Kundennamen, «Nächster Schritt», «Prüfstatus», Margenbeträge | Neue Stufe 5 (Layout), siehe unten |
| **Blatt «⚖️ Wahrscheinlichkeit» druckte auf 25 % verkleinert** | 93 Zeilen wurden auf eine Seite gezwungen — unlesbar | Höhe nur noch dann auf eine Seite zwingen, wenn es den Massstab nicht kostet |
| **Diagramme überlappten sich** und lagen teils ausserhalb des Druckbereichs | Diagramm 3 und 5 überschnitten sich um drei Zeilen | Festes Raster: zwei Reihen zu zweit, das Band-Diagramm über die volle Breite |
| **Excel stufte die Datei als beschädigt ein und reparierte sie** | Der eingebaute Name `_xlnm.Print_Titles` stand zweimal für die Pipeline. Excel meldet «Wir haben ein Problem mit einigen Inhalten gefunden», repariert — und wirft dabei die **benannten Bereiche** weg. Danach liefern `Netto_Faktor` und `Wahrscheinlichkeit_Skala` `#NAME?`, und mit ihnen bricht jede Kennzahl, die darauf rechnet. In LibreOffice fiel das nie auf, weil LibreOffice den Doppeleintrag stillschweigend hinnimmt | Neue Stufe 6 [`bereinige_datei.py`](bereinige_datei.py) räumt Doppeleinträge aus der fertigen Datei; neue Prüfung [`tests/audit_excel.py`](tests/audit_excel.py) lässt sie nie wieder durch |
| **Autofilter deckten nur einen Teil der Tabelle ab** | Pipeline `A5:X860` statt bis AI, CEO Report `A10:L72` statt bis N — beim Filtern wären die übrigen Spalten stehen geblieben und die Zeilen auseinandergelaufen | Filterbereich wird auf die tatsächliche Tabellenbreite gesetzt |

### Prüfung

Die Skripte in [`tests/`](tests/) prüfen die Mappe vollständig:

| Skript | Was es prüft | Ergebnis |
|--------|--------------|----------|
| `audit_static.py` | jede der 25'847 Formeln: Funktionsnamen, Blattbezüge, Anführungszeichen, externe Verweise, Fehlerwerte | 0 Befunde |
| `audit_values.py` | rechnet **das gesamte Modell unabhängig in Python nach** — nur aus den Roheingaben — und vergleicht Zelle für Zelle | 20'099 Werte, 0 Abweichungen |
| `audit_struktur.py` | benannte Bereiche, Dropdowns, bedingte Formatierung, Diagrammquellen, Druckbereiche, verbundene Zellen, Zahlenformate, Schriften | 0 Befunde |
| `audit_fragen.py` | prüft, ob **jede** Rückfrage von Maria und Oliver eine Antwortzeile mit einer Live-Zahl hat und ob die Antwort die zugesagten Begriffe nennt | 8 / 8 abgedeckt |
| `audit_layout.py` | misst **jede sichtbare Zelle**: passt der Text in die Spalte, passt die Zahl (sonst zeigt Excel `####`), reicht die Zeilenhöhe, und druckt das Blatt lesbar auf sein Papier | 0 Befunde |
| `audit_excel.py` | prüft die **Datei selbst**, nicht das Rechenmodell: öffnet Excel sie unverändert? Doppelte benannte Bereiche, Namen auf nicht vorhandene Blätter, überlappende Verbundbereiche, Werte in überdeckten Zellen, Zeilenhöhen über 409.5 pt, Blattnamen, `_xlfn`-Präfixe, Verweise auf unbekannte Blätter, Diagrammbezüge | 28'570 Prüfungen, 0 Befunde |
| `audit_abnahme.py` | nimmt die Umstellung selbst ab, mit eigenen Rechenwegen: sind Projektstart/Projektende **echte Datumszellen** mit Datumsprüfung, rechnet die **Dauer** aus dem Zeitraum (sonst der erfasste Wert), ist die **Marge** in allen Berichten verschwunden, gibt es **leere Spalten** oder Lücken in den Hilfsspalten, stimmen die **Berichtssummen mit der Summe der Pipeline-Zeilen**, steht jeder gewonnene Auftrag auf **100 %** | 13'894 Prüfungen, 0 Befunde |
| `audit_behaviour.py` | 21 Szenarien mit veränderten Daten — u. a. **neuer Deal mit Projektzeitraum**, Statuswechsel, fehlende Wahrscheinlichkeit, **alle Bandgrenzen inkl. 100 %**, leere Pipeline, betragsgleiche Deals, LOST mit 90 %, **WON vollständig belegen (PO, Datum, Vertragsart, Zeitraum)**, **Variante ausschliessen**, **MwSt-Schalter auf netto**, **unvollständiger Einstand**, **Projektzeiträume erfassen (Monat, Quartal, Dauer)**, **nur Startdatum erfasst**, **Bezugsjahr umstellen**, **gewonnener Auftrag auf 90 %** | 21 / 21 bestanden |

```bash
cd reporting/tests && python3 run_durchgaenge.py
```

`run_durchgaenge.py` baut die Datei **fünfmal** komplett neu, berechnet sie jedes
Mal neu und lässt alle Prüfungen laufen. Zusätzlich prüft es zwei Eigenschaften,
die einzelne Läufe nicht zeigen:

- **Determinismus** — alle fünf Durchgänge müssen exakt dieselben Zahlen liefern
  (Vergleich über einen Hash aller berechneten Werte).
- **Idempotenz** — ein zweites Neuberechnen der fertigen Datei darf nichts mehr
  verändern.

Letzter Lauf: **5 / 5 Durchgänge fehlerfrei**, identischer Fingerabdruck
`4f9385248d683e19`, idempotent — 0 Fehlerwerte in 25'847 Formeln, 20'038
unabhängig nachgerechnete Werte ohne Abweichung, 21 / 21 Verhaltenstests,
28'570 Excel-Prüfungen ohne Befund.

Die Stufe «Dateibereinigung» meldet in **jedem** Durchgang denselben
Doppeleintrag — der Werkzeugweg erzeugt ihn reproduzierbar, und die Stufe
entfernt ihn ebenso reproduzierbar. Deshalb ist sie fester Teil der Kette
und keine einmalige Reparatur.

Die Mappe enthält zusätzlich eine **eingebaute Selbstkontrolle** (⚖️-Blatt,
Abschnitt 3): sie rechnet die gewichtete Pipeline auf zwei unabhängigen Wegen
und meldet jede Abweichung — auch nachdem jemand Daten geändert hat.

---

## Was in dieser Runde geändert wurde

Drei Dinge: der Projektzeitraum wird neu als echtes Datum erfasst, die Marge
verschwindet aus dem gesamten Reporting, und gewonnene Aufträge stehen auf
100 %.

### 1. Projektzeitraum als echte Daten

Bisher stand in Spalte H nur eine grobe Monatsangabe wie «Aug» oder «Auf Abruf».
Damit lässt sich weder rechnen noch sortieren.

| Spalte | Was drin steht |
|--------|----------------|
| **O «Projektstart»** | Erster Tag als echtes Datum TT.MM.JJJJ. Die Zelle ist als Datum geprüft — Text und Monatsangaben werden abgewiesen. |
| **P «Projektende»** | Letzter Tag, ebenfalls als echtes Datum. |
| **G «Dauer Tage»** | Neu eine Formel: Projektende − Projektstart + 1. Beide Tage zählen mit — 01.08.2026 bis 10.08.2026 ergibt 10 Tage. |
| AW `_DauerErfasst` (ausgeblendet) | Steht nur eines der beiden Daten oder keines, zeigt Spalte G unverändert den **bisher von Hand erfassten Wert**. Überschrieben wird nichts. |
| AX `_MonatStart` (ausgeblendet) | Monatsanfang des Projektstarts — Grundlage der Auswertung nach Monat und Quartal. |
| AY `_ZeitraumOK` (ausgeblendet) | 1, wenn beide Daten echte Datumswerte sind und das Ende nicht vor dem Start liegt. |

Wo «Auf Abruf» oder «tbd» steht, bleiben beide Datumsfelder leer und der
Prüfstatus meldet den fehlenden Zeitraum: **⛔ Zeitraum fehlt** bei WON,
**○ Zeitraum offen** bei allen anderen. Liegt das Ende vor dem Start, meldet er
**⚠ Ende vor Start**, die Dauer fällt auf den erfassten Wert zurück und die Zeile
zählt nicht in die Monatsauswertung. Die grobe Monatsangabe in Spalte H bleibt
stehen und erscheint in den Berichten als Anhaltspunkt, solange kein Datum
erfasst ist.

Aktuell hat **kein einziger** der 46 aktiven Deals einen Zeitraum — die Spalten
sind neu und müssen gefüllt werden. Genau das steht im Bericht: 46 Deals über
6'862'149 CHF unter «ohne erfassten Zeitraum».

### 2. Marge vollständig aus dem Reporting entfernt

| Wo | Was weg ist |
|----|-------------|
| Pipeline | Spalten O «Marge CHF» und P «Marge %» — an ihrer Stelle stehen jetzt Projektstart und Projektende. Hilfsspalten `_Kalkuliert`, `_Aufteilung`, `_KostenUeber`, `_MargeNum`. |
| CEO Report | Spalte «Marge CHF» |
| 📄 Report | Spalte «Marge CHF» in der Top-WON-Liste |
| 📑 Executive PDF | Spalte «Marge» in der Top-5-Liste, Kennzahlen «Marge aus kalkulierten Deals» und «Marge % darauf» |
| Dashboard + CEO Report | Kennzahlen «Marge aus sauber kalkulierten Deals», «Marge % auf diesen Deals», «Deals ohne Kostenkalkulation», «Deals mit Einstand über Nettoumsatz» |
| Prüfstatus | Meldungen «⚠ Kosten über Umsatz», «⚠ nur Preis-Aufteilung», «⚠ Marge negativ», «⚠ nicht kalkuliert» |
| 📋 Definitionen | Abschnitt «Margendefinition», die beiden margenbezogenen offenen Punkte |
| 🔍 Herleitung | Stufe «Marge rechnen», Stufe «Kalkulation prüfen», die Margenzeilen beider Beispiele, die Margen-Kennzahlen der Landkarte |
| Diagramme | keine Änderung nötig — es gab keine Margenreihe |

**Die Kostenspalten J–N bleiben in der Pipeline** als Arbeitsgrundlage erhalten,
ebenso der Einstand in Spalte Z. Ausgewertet wird daraus im Bericht nichts mehr.

Es bleiben keine leeren Spalten und keine Lücken: die beiden Margenspalten sind
durch die beiden Datumsspalten ersetzt, die Hilfsspalten rücken lückenlos auf
(AR–BB), Spalte BC ist geleert. Nach dem Umbau rechnet die Mappe mit **0
Fehlerwerten** — kein `#BEZUG!`, kein `#WERT!`.

Warum die Marge nicht einfach korrigiert wurde, steht weiterhin im File: die
Antwort auf Marias Rückfrage ist nicht gelöscht, sondern ersetzt worden. Sie
erklärt jetzt, dass die MwSt als Kostenposition erfasst war, dass bei einem Teil
der Zeilen nur der Verkaufspreis aufgeteilt wurde — und dass auf dieser
Datengrundlage keine Margenzahl trägt.

### 3. Gewonnene Aufträge auf 100 %

Ein unterschriebener Auftrag ist keine Wahrscheinlichkeit mehr, sondern ein
Fakt. Die Aggreko-Skala endet bei 90 %, weil sie offene Opportunitäten bewertet.
Die Stufe **100 %** ist als Ergänzung von MiT CH gekennzeichnet und gilt
ausschliesslich für Status WON.

Das Blatt prüft beide Richtungen laufend: **WON ohne 100 %** und **100 % ohne
WON** — beide müssen 0 sein.

Wirkung auf die Kennzahl: die gewichtete Pipeline steigt von **1'485'570 CHF**
auf **1'628'426 CHF**. Die Differenz von 142'855 CHF ist genau der Anteil, mit
dem die zwölf gewonnenen Aufträge (1'428'553 CHF) bisher abgewertet wurden.

Die Liste der gewonnenen Aufträge steht neu auf dem Blatt `⚖️ Wahrscheinlichkeit`
als Abschnitt 6 — mit Volumen, Wahrscheinlichkeit, **Projektstart und
Projektende** je Auftrag. Dieselben beiden Datumsspalten stehen jetzt auch im
CEO Report, in der Top-WON-Liste des 📄 Reports und in der Top-5-Liste des
📑 Executive PDF.

### 4. Was der Bericht stattdessen zeigt

| Bereich | Wo |
|---------|-----|
| Auftragseingang und Pipeline nach Status | unverändert in allen Berichten |
| **Nachweisquote** — wie viel des Auftragseingangs durch PO-Nummer und Belegdatum gestützt ist | neue Kennzahl in Dashboard, CEO Report, 📄 Report und 📑 Executive PDF |
| Auswertung nach Kanton und Segment | unverändert |
| **Auswertung nach Monat des Projektstarts** | neuer Abschnitt 6 in Dashboard und CEO Report, neuer Block im 📄 Report: zwölf Monate eines wählbaren Bezugsjahrs, dazu «andere Jahre» und «ohne erfassten Zeitraum», je mit Anzahl, Volumen und Anteil |
| Offene Pflichtangaben mit Anzahl und Volumen | erweitert um «Aktive Deals ohne erfassten Projektzeitraum» und «WON ohne erfassten Projektzeitraum» |

### Spaltenübersicht der Änderung

**Entfernt**

| Blatt | Spalte |
|-------|--------|
| MiT Strom Pipeline | O «Marge CHF», P «Marge %» |
| MiT Strom Pipeline | Hilfsspalten `_Kalkuliert`, `_Aufteilung`, `_KostenUeber`, `_MargeNum` |
| CEO Report | «Marge CHF» |
| 📄 Report | «Marge CHF» |
| 📑 Executive PDF | «Marge» |

**Neu angelegt**

| Blatt | Spalte |
|-------|--------|
| MiT Strom Pipeline | O «Projektstart» (Datum), P «Projektende» (Datum) |
| MiT Strom Pipeline | Hilfsspalten `_DauerErfasst`, `_MonatStart`, `_ZeitraumOK` |
| CEO Report | «Projektstart», «Projektende» |
| Dashboard | «Projektstart» (ersetzt «Start») |
| 📄 Report | «Projektstart», «Projektende» in der Top-WON-Liste |
| 📑 Executive PDF | «Projektstart», «Projektende» in der Top-5-Liste |
| ⚖️ Wahrscheinlichkeit | Abschnitt 6 «Gewonnene Aufträge (WON)» mit Zeitraum |

**Geändert**

| Blatt | Spalte |
|-------|--------|
| MiT Strom Pipeline | G «Dauer Tage» — war Eingabe, ist neu eine Formel aus dem Zeitraum |
| MiT Strom Pipeline | S «Effektive Wahr. %» — Dropdown neu mit 100 % für gewonnene Aufträge |
| MiT Strom Pipeline | AH «Prüfstatus» — margenbezogene Meldungen raus, Zeitraum-Meldungen rein |

### Zwei Punkte, die offen geblieben sind

- Der **Umrechnungsfaktor** steht weiterhin auf 1.081. Er wirkt nur noch auf die
  Spalte «Nettoumsatz» und auf die Kennzahl «WON netto», nicht mehr auf eine
  Kernzahl. Die Umstellung bleibt eine Zelle im Definitionsblatt.
- Die **grobe Monatsangabe** in Spalte H bleibt vorerst stehen, damit die
  Berichte nicht ohne jede Zeitangabe dastehen, solange keine Daten erfasst
  sind. Sie kann entfallen, sobald der Zeitraum flächendeckend gepflegt ist.

---

## Layout und Druckbild

Nach dem inhaltlichen Aufbau kam eine eigene Stufe dazu, die **nur** das
Erscheinungsbild macht: [`build_layout.py`](build_layout.py). Sie ändert keine
einzige Zahl und keine einzige Formel — sie setzt Spaltenbreiten, Umbrüche,
Zeilenhöhen, Innenabstände und die Seiteneinrichtung.

Der Grund: In der Vorversion waren an **149 Stellen** Texte abgeschnitten,
Zahlen zu breit für ihre Spalte (Excel zeigt dann `####`) oder Zeilen zu
niedrig für ihren umgebrochenen Inhalt. Das fiel niemandem als Fehler auf, weil
Excel nicht warnt — es zeigt einfach weniger an, als in der Zelle steht.

### Was die Stufe tut

| Schritt | Was passiert |
|---------|--------------|
| **Innenabstand** | Jede Zahl bekommt rechts, jeder Text links ein Zeichen Abstand. Ohne das klebt der Betrag am Rahmen und läuft optisch in die Nachbarspalte — «116 526 CHF Mai» statt «116 526 CHF │ Mai». |
| **Breiten** | Jede Spalte wird nur so weit verbreitert, wie ihr Inhalt es verlangt. Text, der ohnehin in eine leere Nachbarzelle ragen darf, verlangt nichts. Zahlen verlangen immer die volle Breite, weil sie nicht überlaufen können. |
| **Umbruch** | Die langen Textspalten (Kunde, Segment, Leistung / Fleet, Nächster Schritt, Prüfstatus) bekommen eine feste Breite und brechen um, statt das Blatt in die Breite zu ziehen. |
| **Zeilenhöhen** | Jede Zeile bekommt genau die Höhe, die ihr umgebrochener Inhalt braucht — Wort für Wort nachgerechnet, wie Excel selbst umbricht. |
| **Seiten** | Je Blatt bewusst festgelegt, wie viele Seiten breit gedruckt wird, und ob die Höhe auf eine Seite gezwungen werden darf. Einheitlich A4, gleiche Ränder, gleiche Kopf- und Fusszeile auf jedem Blatt. |
| **Diagramme** | Die fünf Diagramme liegen auf einem festen Raster statt sich zu überlappen, mit Seitenumbrüchen zwischen den Reihen. |

### Massstab im Ausdruck

| Blatt | Seiten breit | Massstab | Höhe |
|-------|--------------|----------|------|
| 📑 Executive PDF | 1 | 97 % | 1 Seite |
| 📄 Report | 1 | 81 % | 2 Seiten (Monatsauswertung auf Seite 2) |
| CEO Report | 1 | 72 % | fortlaufend |
| Dashboard | 1 | 78 % | fortlaufend |
| 📊 Diagramme | 1 | 72 % | 3 Seiten |
| MiT Strom Pipeline | 3 | 74 % | fortlaufend |
| 📋 Definitionen & Klärung | 1 | 84 % | fortlaufend |
| 🔍 Herleitung & Formeln | 1 | 75 % | fortlaufend |
| ⚖️ Wahrscheinlichkeit | 1 | 100 % | fortlaufend |

Vorher stand der CEO Report auf 53 % und das Blatt «⚖️ Wahrscheinlichkeit» auf
**25 %** — beides im Ausdruck nicht mehr lesbar. Die beiden breiten Textspalten
des CEO Reports («Leistung / Fleet» 79 Zeichen, «Nächster Schritt» 53 Zeichen)
sind jetzt 26 bzw. 24 Zeichen breit und brechen um; dadurch passt das Blatt mit
allen 14 Spalten auf eine Seitenbreite und ist um die Hälfte grösser gedruckt.

### Warum es eine eigene Stufe «Dateibereinigung» gibt

Alle anderen Prüfungen messen das **Rechenmodell**: stimmen die Formeln, stimmen
die Werte, passt das Layout. Keine von ihnen beantwortet die Frage, ob **Excel
die Datei überhaupt unverändert öffnet**. Genau dort lag der Fehler: die Mappe
rechnete in jeder Prüfung richtig, aber Excel stufte sie beim Öffnen als
beschädigt ein, reparierte sie — und im reparierten Zustand fehlten die
benannten Bereiche. Für den Anwender sah es aus, als würde nichts mehr
zusammenpassen.

Deshalb gibt es jetzt zwei Dinge:

- **Stufe 6 `bereinige_datei.py`** läuft als Letztes über die fertige Datei und
  entfernt doppelte benannte Bereiche. Sie fasst sonst nichts an.
- **`tests/audit_excel.py`** öffnet die Datei als ZIP und prüft ihr Inneres
  gegen die Regeln, an denen Excel eine Datei ablehnt.

### Nachgemessen wird mit demselben Lineal

[`build_layout.py`](build_layout.py) und [`tests/audit_layout.py`](tests/audit_layout.py)
rechnen beide mit [`layout_modell.py`](layout_modell.py) — den echten
Zeichenbreiten von Calibri und Arial in Pixeln, den Zeilenhöhen, die Excel beim
automatischen Anpassen einstellt, und einem Wort-für-Wort-Umbruch. Sonst würde
die eine Seite etwas bauen, das die andere anschliessend beanstandet.

Die Prüfung meldet drei Arten von Fehlern, die alle bei **0** stehen:
abgeschnittener Text, zu breite Zahl (`####`) und zu niedrige Zeile — dazu ein
Blatt, das nur noch unter 60 % verkleinert auf sein Papier passt.

---

## Stand der Zahlen

Bei 46 aktiven Deals mit 6'862'149 CHF Umsatz — nach der Umschlüsselung auf die
Aggreko-Skala:

| Band | Faktor | Deals | Umsatz CHF | Gewichtet CHF |
|------|--------|-------|------------|---------------|
| 0 – 44 %  | 0 %   | 30 | 5'092'182 | 0 |
| 45 – 59 % | 30 %  | 0  | 0 | 0 |
| 60 – 89 % | 50 %  | 2  | 268'500 | 134'250 |
| 90 – 99 % | 90 %  | 2  | 72'914 | 65'622 |
| 100 % (WON) | 100 % | 12 | 1'428'553 | 1'428'553 |
| **Total** |       | **46** | **6'862'149** | **1'628'426** |

Gewichtungsgrad **23.7 %**. Mit gewonnenen Aufträgen zu 90 % wären es
1'485'570 CHF, vor der Umschlüsselung 2'203'080 CHF, nach der alten Rechnung
(Umsatz × Wahrscheinlichkeit) 3'294'922 CHF.

Das Band 45–59 % ist leer, und das bleibt es: **keine Stufe der Aggreko-Skala
fällt in dieses Band.** Die Zeile steht trotzdem in der Tabelle, weil sie zur
Vorgabe gehört — und weil sofort sichtbar wäre, wenn jemand einen Wert dazwischen
einträgt.

> **Zur Bestätigung im Bewertungs-Meeting:** Die 22 Deals, die auf 50 % standen,
> sind auf 30 % gesetzt — die einzige Stufe, deren Begründung «Ausgang offen»
> trifft. Sie stehen namentlich auf dem Blatt `⚖️ Wahrscheinlichkeit`. Wo das
> Fleet-Team die On-/Off-Hire-Daten bereits überwacht, gehört der Deal auf 60 %:
> eine Zelle in Spalte S ändern, alles Weitere rechnet nach. Gingen alle 22 auf
> 60 %, läge die gewichtete Pipeline bei **2'681'419 CHF**.

---

## Datei neu erzeugen

```bash
./build_all.sh      # erwartet original.xlsx (= quelle_stand_vor_update.xlsx) im selben Ordner
```

Das Skript führt Stufe 1 bis 4 aus. Danach die Datei einmal in Excel oder
LibreOffice neu berechnen lassen und speichern — erst dann stehen in den
Formelzellen auch Ergebnisse. Anschliessend:

```bash
python3 build_layout.py     # Stufe 5: Breiten, Umbrüche, Höhen, Seiten
```

und noch einmal neu berechnen und speichern. Die Layoutstufe braucht die
gerechneten Werte, weil sie misst, was in der Zelle tatsächlich steht.

Die Prüfungen laufen mit:

```bash
cd tests && RECALC=/pfad/zu/recalc.py python3 run_durchgaenge.py
```

`RECALC` zeigt auf ein Hilfsskript, das eine Mappe über LibreOffice neu rechnet;
ohne Angabe wird der Standardpfad der Arbeitsumgebung verwendet.

## Ausbau vom 12.08.2026 — `CH_MiT_Strom_Customer_CEO_CFO_MASTER__2_.xlsx`

Der Ausbau (Blöcke 1–4: Nachweis, gewichtete Zerlegung, Zeitraum,
Diagramme) arbeitet direkt auf der ausgelieferten Datei — nicht über die
Baukette. Skripte und die vollständige Änderungsliste liegen in
`ausbau/` (`AENDERUNGSLISTE.md`).

Reihenfolge bei Änderungen an dieser Datei:

```bash
cd ausbau
python3 ausbau_block1.py … ausbau_block4.py   # je Block, dann neu berechnen
python3 kontrolle.py DATEI                     # K1–K4 nach jedem Block
python3 repariere_charts.py DATEI              # nach der LETZTEN Neuberechnung
python3 ../bereinige_datei.py DATEI            # danach immer
python3 ../tests/audit_excel.py DATEI          # Schlusskontrolle
```

Zwei Funde aus diesem Ausbau, die auch die Baukette betreffen:

1. **LibreOffice wirft Diagrammfarben weg.** Beim Neuberechnen über
   LibreOffice verlieren alle Diagramme ihre Füllfarben. Deshalb läuft
   `repariere_charts.py` nach der letzten Neuberechnung: es baut die
   Diagramme mit openpyxl neu und kopiert nur die Diagramm-XMLs auf
   ZIP-Ebene zurück — die berechneten Werte bleiben unangetastet.
2. **Segmentliste in `_data` war unvollständig.** «Datacenter» und
   «Elektroplaner» fehlten; das Segment-Diagramm zeigte CHF 1'072'286
   zu wenig. Ergänzt, plus Wachhund-Zeile «Übrige (Segment fehlt in
   der Liste)», die künftige Lücken sichtbar macht.
