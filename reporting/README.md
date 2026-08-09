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

**2. Pipeline (Weighted) = Umsatz × Gewichtungsfaktor**

Der Faktor wird aus dem Feld *Effective Probability* abgeleitet:

| Effective Probability | Faktor |
|-----------------------|--------|
| 0 – 44 %              | 0 %    |
| 45 – 59 %             | 30 %   |
| 60 – 89 %             | 50 %   |
| ab 90 %               | 90 %   |

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
| 100 % | 90 % | 90 % | 90 % | 12 | 1'285'698 | 1'285'698 | unverändert |
| **Total** | | | | **66** | **2'203'080** | **1'485'570** | **−717'509** |

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
| **Negative Margen in Spalte I** | Ursache gefunden: die **MwSt war als Kostenposition erfasst** und wurde vom Umsatz abgezogen. Neu gilt `Marge = Nettoumsatz − Einstand`, ohne MwSt auf beiden Seiten. Zusätzlich zeigte sich: bei 36 Zeilen wurde gar nicht kalkuliert, sondern nur der Verkaufspreis in netto + MwSt zerlegt. Dort wird jetzt **bewusst keine Marge ausgewiesen** — mit Begründung in der Spalte «Prüfstatus». |
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
| Aktive Deals ohne Kostenkalkulation | 10 | 606'942 |
| Aktive Deals mit Einstand über Nettoumsatz | 12 | 3'843'342 |
| Kunden mehrfach in der Pipeline, Variante offen | 17 | 3'368'728 |

Sauber kalkuliert sind aktuell **16 von 46** aktiven Deals; darauf beträgt die
Marge **363'396 CHF (17.5 %)**.

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
| `MiT Strom Pipeline` | `Gew.Wert CHF` (Spalte Q) = **Volumen × Aggreko-Faktor**. Spalte S mit Dropdown 0/10/30/60/90 %. Neue Fachspalten Y–AH: Nettoumsatz, Einstand, Abwicklung, Vertragsart, Deal-Gruppe, Variante, Offert-Nr., Auftrag/PO-Nr., Beleg-Datum, Prüfstatus. Spalte N heisst neu «Übrige Kosten» und enthält keine MwSt mehr. Hilfsspalten liegen ausgeblendet ab AJ. |
| `⚖️ Wahrscheinlichkeit` | neu — Aggreko-Bewertungsmodell |
| `📋 Definitionen & Klärung` | neu — beantwortet jede Rückfrage mit Live-Zahl, enthält Annahmen, Margendefinition, Status- und Vertragsartendefinitionen, Variantenregel, Klärungsliste und die Liste der offenen Pflichtangaben |
| `🔍 Herleitung & Formeln` | neu — der Rechenweg in sieben Stufen, zwei komplett durchgerechnete Beispiele, die Herkunft jeder Berichtszahl, das Verzeichnis aller 54 Spalten mit ihren Formeln, die Begründung jedes Designentscheids und ein Funktionslexikon |
| `Dashboard` | Info-Zeile mit gewichteter Pipeline, Abschnitt 4 «Gewichtete Pipeline», Abschnitt 5 «Qualität & Nachweis» |
| `CEO Report` | dito, zusätzlich je Deal die Spalten «Auftrag / PO-Nr.» und «Prüfstatus». Der Prüfstatus zeigt hier den Kurzbefund (⛔ Nachweis fehlt · ⚠ Marge negativ · ⚠ nicht kalkuliert · ○ Einstand offen · ✅ belegt · ✔ kalkuliert); die vollständige Aufzählung aller offenen Punkte einer Zeile steht in der Pipeline in Spalte AH |
| `📄 Report` | KPI-Zeilen «⚖️ Gewichtet» und «📋 WON belegt», Abschnitt «Wahrscheinlichkeits-Bewertung» |
| `📑 Executive PDF` | gewichteter Wert, Bandtabelle und Block «Nachweis & Marge» (WON netto, davon belegt, Marge kalkuliert) |
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

### Prüfung

Die Skripte in [`tests/`](tests/) prüfen die Mappe vollständig:

| Skript | Was es prüft | Ergebnis |
|--------|--------------|----------|
| `audit_static.py` | jede der 28'159 Formeln: Funktionsnamen, Blattbezüge, Anführungszeichen, externe Verweise, Fehlerwerte | 0 Befunde |
| `audit_values.py` | rechnet **das gesamte Modell unabhängig in Python nach** — nur aus den Roheingaben — und vergleicht Zelle für Zelle | 22'627 Werte, 0 Abweichungen |
| `audit_struktur.py` | benannte Bereiche, Dropdowns, bedingte Formatierung, Diagrammquellen, Druckbereiche, verbundene Zellen, Zahlenformate, Schriften | 0 Befunde |
| `audit_fragen.py` | prüft, ob **jede** Rückfrage von Maria und Oliver eine Antwortzeile mit einer Live-Zahl hat und ob die Antwort die zugesagten Begriffe nennt | 8 / 8 abgedeckt |
| `audit_layout.py` | misst **jede sichtbare Zelle**: passt der Text in die Spalte, passt die Zahl (sonst zeigt Excel `####`), reicht die Zeilenhöhe, und druckt das Blatt lesbar auf sein Papier | 0 Befunde |
| `audit_behaviour.py` | 17 Szenarien mit veränderten Daten — u. a. neuer Deal, Statuswechsel, fehlende Wahrscheinlichkeit, alle Bandgrenzen, leere Pipeline, betragsgleiche Deals, LOST mit 90 %, **WON vollständig belegen**, **Variante ausschliessen**, **MwSt-Schalter auf netto**, **unvollständiger Einstand** | 17 / 17 bestanden |

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
`8dc530b5c5d2f5ec`, idempotent.

Die Mappe enthält zusätzlich eine **eingebaute Selbstkontrolle** (⚖️-Blatt,
Abschnitt 3): sie rechnet die gewichtete Pipeline auf zwei unabhängigen Wegen
und meldet jede Abweichung — auch nachdem jemand Daten geändert hat.

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
| 📑 Executive PDF | 1 | 99 % | 1 Seite |
| 📄 Report | 1 | 82 % | 1 Seite |
| CEO Report | 1 | 72 % | fortlaufend |
| Dashboard | 1 | 79 % | fortlaufend |
| 📊 Diagramme | 1 | 72 % | 3 Seiten |
| MiT Strom Pipeline | 3 | 76 % | fortlaufend |
| 📋 Definitionen & Klärung | 1 | 87 % | fortlaufend |
| 🔍 Herleitung & Formeln | 1 | 75 % | fortlaufend |
| ⚖️ Wahrscheinlichkeit | 1 | 100 % | fortlaufend |

Vorher stand der CEO Report auf 53 % und das Blatt «⚖️ Wahrscheinlichkeit» auf
**25 %** — beides im Ausdruck nicht mehr lesbar. Die beiden breiten Textspalten
des CEO Reports («Leistung / Fleet» 79 Zeichen, «Nächster Schritt» 53 Zeichen)
sind jetzt 26 bzw. 24 Zeichen breit und brechen um; dadurch passt das Blatt mit
allen 14 Spalten auf eine Seitenbreite und ist um die Hälfte grösser gedruckt.

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
| 0 – 44 %  | 0 %  | 30 | 5'092'182 | 0 |
| 45 – 59 % | 30 % | 0  | 0 | 0 |
| 60 – 89 % | 50 % | 2  | 268'500 | 134'250 |
| ab 90 %   | 90 % | 14 | 1'501'467 | 1'351'320 |
| **Total** |      | **46** | **6'862'149** | **1'485'570** |

Gewichtungsgrad **21.6 %**. Vor der Umschlüsselung waren es 2'203'080 CHF
(32.1 %), nach der alten Rechnung (Umsatz × Wahrscheinlichkeit) 3'294'922 CHF.

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
