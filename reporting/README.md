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
| `MiT Strom Pipeline` | `Gew.Wert CHF` (Spalte Q) = **Volumen × Aggreko-Faktor** statt Volumen × Wahrscheinlichkeit. Spalte S mit Dropdown 0/10/30/60/90 % und oranger Markierung bei abweichenden Werten. Faktor je Deal in der ausgeblendeten Hilfsspalte Y. |
| `⚖️ Wahrscheinlichkeit` | neu (siehe oben) |
| `Dashboard` | Info-Zeile mit gewichteter Pipeline unter den KPI-Kacheln, Abschnitt 4 «Gewichtete Pipeline» mit Bandtabelle |
| `CEO Report` | dito |
| `📄 Report` | KPI-Zeile «⚖️ Gewichtet» und Abschnitt «Wahrscheinlichkeits-Bewertung» |
| `📑 Executive PDF` | gewichteter Wert in der Pipeline-Zeile, Bandtabelle auf der Seite |
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
| `audit_static.py` | jede der 15'509 Formeln: Funktionsnamen, Blattbezüge, Anführungszeichen, externe Verweise, Fehlerwerte | 0 Befunde |
| `audit_values.py` | rechnet **das gesamte Modell unabhängig in Python nach** — nur aus den Roheingaben — und vergleicht Zelle für Zelle | 11'255 Werte, 0 Abweichungen |
| `audit_struktur.py` | benannte Bereiche, Dropdowns, bedingte Formatierung, Diagrammquellen, Druckbereiche, verbundene Zellen, Zahlenformate, Schriften | 0 Befunde |
| `audit_behaviour.py` | 12 Szenarien mit veränderten Daten (neuer Deal, Statuswechsel, fehlende Wahrscheinlichkeit, Prozent als 60 statt 0.6, alle Bandgrenzen, leere Pipeline, Text im Volumen, Deal ohne Status, betragsgleiche Deals, letzte Zeile 860, Deal unter dem Druckbereich, LOST mit 90 %) | 12 / 12 bestanden |

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
python3 build_master_reporting.py    # erwartet original.xlsx im selben Ordner
```

Danach in LibreOffice/Excel einmal neu berechnen lassen, damit die
zwischengespeicherten Werte stimmen.
