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

## Rückfragen von Maria — was daraus im File wurde

Jede Rückfrage ist im neuen Blatt **`📋 Definitionen & Klärung`** mit einer
Live-Zahl beantwortet. Die Regeln stehen dort, nicht in einer Mail.

| Rückfrage | Was im File passiert |
|-----------|----------------------|
| **Negative Margen in Spalte I** | Ursache gefunden: die **MwSt war als Kostenposition erfasst** und wurde vom Umsatz abgezogen. Neu gilt `Marge = Nettoumsatz − Einstand`, ohne MwSt auf beiden Seiten. Zusätzlich zeigte sich: bei 36 Zeilen wurde gar nicht kalkuliert, sondern nur der Verkaufspreis in netto + MwSt zerlegt. Dort wird jetzt **bewusst keine Marge ausgewiesen** — mit Begründung in der Spalte «Prüfstatus». |
| **Wer verantwortet die Kalkulation?** | Der Einstand wird vom Verkäufer erfasst und vor dem Statuswechsel auf WON vom Innendienst gegengeprüft. Die Regel steht im Definitionsblatt, der Erfüllungsstand pro Zeile in Spalte AH. |
| **Laufen alle Projekte über MiT CH?** | Ja — MiT CH ist die Standardabwicklung. Abweichungen werden in der neuen Spalte **AA «Abwicklung»** erfasst (Aggreko intl. / Partner–Dritte). Eine leere Zelle heisst ausdrücklich MiT CH, nicht «unbekannt». |
| **Wie ist das WON-Volumen zu verstehen?** | Neu dreifach ausgewiesen: **brutto wie erfasst**, **netto ohne MwSt**, und **davon belegt** — belegt heisst Auftrags-/PO-Nr. + Belegdatum + vollständiger Einstand. Aktuell: 1'428'553 brutto, 1'321'511 netto, **0 belegt**. |
| **Datacenter: 660 oder 330 kCHF?** | Entscheidet die neue Variantenlogik: gleiche **Deal-Gruppe (AC)** setzen, die nicht führende Zeile auf **«Alternative – zählt nicht» (AD)**. Dann zählt nur die führende Variante. Die beiden DPR-Zeilen stehen namentlich auf der Klärungsliste. |
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
     − 272 000 Einstand = **88 777 Marge (24.6 %)**. Wahrscheinlichkeit 50 % →
     Faktor 30 % → 117 000 gewichtet.
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
| `CEO Report` | dito, zusätzlich je Deal die Spalten «Auftrag / PO-Nr.» und «Prüfstatus» |
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
| Abgeschnittene Beschriftungen in Executive PDF und Report | | Spaltenbreiten und Texte angepasst |

### Prüfung

Die Skripte in [`tests/`](tests/) prüfen die Mappe vollständig:

| Skript | Was es prüft | Ergebnis |
|--------|--------------|----------|
| `audit_static.py` | jede der 27'302 Formeln: Funktionsnamen, Blattbezüge, Anführungszeichen, externe Verweise, Fehlerwerte | 0 Befunde |
| `audit_values.py` | rechnet **das gesamte Modell unabhängig in Python nach** — nur aus den Roheingaben — und vergleicht Zelle für Zelle | 21'772 Werte, 0 Abweichungen |
| `audit_struktur.py` | benannte Bereiche, Dropdowns, bedingte Formatierung, Diagrammquellen, Druckbereiche, verbundene Zellen, Zahlenformate, Schriften | 0 Befunde |
| `audit_behaviour.py` | 17 Szenarien mit veränderten Daten — u. a. neuer Deal, Statuswechsel, fehlende Wahrscheinlichkeit, alle Bandgrenzen, leere Pipeline, betragsgleiche Deals, LOST mit 90 %, **WON vollständig belegen**, **Variante ausschliessen**, **MwSt-Schalter auf netto**, **unvollständiger Einstand** | 17 / 17 bestanden |

```bash
cd reporting/tests && python3 audit_static.py && python3 audit_values.py \
  && python3 audit_struktur.py && python3 audit_behaviour.py
```

Die Mappe enthält zusätzlich eine **eingebaute Selbstkontrolle** (⚖️-Blatt,
Abschnitt 3): sie rechnet die gewichtete Pipeline auf zwei unabhängigen Wegen
und meldet jede Abweichung — auch nachdem jemand Daten geändert hat.

---

## Stand der Zahlen

Bei 46 aktiven Deals mit 6'862'149 CHF Umsatz:

| Band | Faktor | Deals | Umsatz CHF | Gewichtet CHF |
|------|--------|-------|------------|---------------|
| 0 – 44 %  | 0 %  | 8  | 2'700'484 | 0 |
| 45 – 59 % | 30 % | 22 | 2'391'698 | 717'509 |
| 60 – 89 % | 50 % | 2  | 268'500 | 134'250 |
| ab 90 %   | 90 % | 14 | 1'501'467 | 1'351'320 |
| **Total** |      | **46** | **6'862'149** | **2'203'080** |

Gewichtungsgrad 32.1 %. Nach der alten Rechnung (Umsatz × Wahrscheinlichkeit)
waren es 3'294'922 CHF.

> **Offen fürs Bewertungs-Meeting:** 42 der 46 aktiven Deals stehen auf Werten,
> die es in der neuen Skala nicht gibt (50 %, 80 %, 20 %, 100 %). Diese Werte
> wurden bewusst **nicht** automatisch umgesetzt — die Neubewertung ist eine
> Vertriebsentscheidung. Die Faktor-Logik funktioniert trotzdem korrekt, weil
> sie das Feld als *Effective Probability* behandelt und über die Bänder
> abbildet. In der Pipeline sind die betroffenen Zellen orange markiert.

---

## Datei neu erzeugen

```bash
./build_all.sh      # erwartet original.xlsx (= quelle_stand_vor_update.xlsx) im selben Ordner
```

Danach in LibreOffice/Excel einmal neu berechnen lassen, damit die
zwischengespeicherten Werte stimmen.
