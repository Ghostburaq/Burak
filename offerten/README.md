# Offerten-Tool · Master-Vorlage + PDF auf Knopfdruck

Ein komplettes, sofort einsatzbereites Werkzeug zum **Schreiben von Offerten**
in Excel und zum **Erzeugen druckfertiger PDFs auf Knopfdruck** – nachgebaut
und markenkonform an der Mobil-in-Time-Offerte.

```
offerten/
├── offerte_lib.py                 ← gemeinsamer Baukasten (Layout/Formeln)
├── Offerten_Master_Vorlage.xlsx   ← Miet-Vorlage (öffnen & ausfüllen)
├── build_template.py              ← erzeugt die Miet-Vorlage
├── Offerte_Kabel_95mm.xlsx        ← Offerte 95mm²-Kabel (Verkauf/Richtpreis)
├── build_offerte_kabel95.py       ← erzeugt die 95mm²-Offerte
├── offerte_to_pdf.py              ← Excel → PDF (ohne Excel/LibreOffice)
├── erstelle_offerte.sh            ← Vorlage bauen + PDF in einem Schritt
├── Q663790202605072109.pdf        ← Beispiel-PDF (EKAG-Miete nachgebaut)
├── Offerte_Kabel_95mm.pdf         ← Beispiel-PDF (95mm²-Kabel)
└── vba/
    ├── PdfButton.bas              ← „PDF erstellen“-Knopf für Excel
    └── PDF_Knopf_Anleitung.md     ← Einbau in 4 Schritten
```

## Zwei Offerten-Typen, ein Baukasten

`offerte_lib.py` baut beide Offerten im identischen Layout – nur die Daten
unterscheiden sich. `offerte_to_pdf.py` liest die Spaltenköpfe dynamisch und
passt das PDF automatisch an (Miet- *oder* Verkaufslayout).

| Offerte | Spalten | Summe |
|---------|---------|-------|
| **EKAG-Miete** (Master-Vorlage) | Pos · Anz · Beschreibung · Einh. · Preis/Wo. · Wochen · Position | 16'609.27 nach 10 % Rabatt |
| **95mm²-Kabel** (Verkauf) | Pos · Menge · Beschreibung · Einheit · Einzelpreis · Total | **11'146.50** (Richtpreis, netto) |

So baust du die 95mm²-Offerte neu:
```bash
python3 offerten/build_offerte_kabel95.py        # -> Offerte_Kabel_95mm.xlsx
python3 offerten/offerte_to_pdf.py offerten/Offerte_Kabel_95mm.xlsx
```

## Die Excel-Mappe (3 Blätter)

| Blatt | Zweck |
|-------|-------|
| **Offerte**    | Das druckfertige Dokument (DIN A4). Hier füllen Sie aus. |
| **Stammdaten** | Firma, Sachbearbeiter, Standard-Rabatt/MwSt, Textbausteine. Wird per Formel in die Offerte gezogen – einmal pflegen, überall aktuell. |
| **Artikel**    | Preisliste. Speist das Dropdown in der Spalte *Beschreibung* und den automatischen Preis-Lookup. |

**Was sich von selbst rechnet:**
- **Position** = Anzahl × Preis/Woche × Wochen
- **Zwischentotal** = Summe aller Positionen
- **Rabatt** und **MwSt** aus den Stammdaten (Prozentwerte)
- **Endbetrag** = Total nach Rabatt + MwSt
- **Mietzeitraum** automatisch aus Mietbeginn/Mietende
- In leeren Zeilen füllt die Auswahl eines Artikels aus dem **Dropdown**
  automatisch Einheit und Preis (VLOOKUP gegen das Blatt *Artikel*).

Zahlen erscheinen im Schweizer Format (`18'454.74`).

## PDF auf Knopfdruck – zwei Wege

### A) In Excel (echter Knopf)
Mappe als **.xlsm** speichern, das Makro `vba/PdfButton.bas` importieren und
einer Schaltfläche zuweisen → ein Klick speichert das Blatt *Offerte* als PDF
(Dateiname = Offerte-Nr. aus Zelle G8). Schritt-für-Schritt:
[`vba/PDF_Knopf_Anleitung.md`](vba/PDF_Knopf_Anleitung.md).

### B) Per Skript (ohne Excel, ohne LibreOffice)
```bash
python3 offerten/offerte_to_pdf.py            # nutzt die Master-Vorlage
python3 offerten/offerte_to_pdf.py meine.xlsx ausgabe.pdf
```
Liest die ausgefüllte Mappe, löst Artikelpreise auf, rechnet alle Summen und
rendert ein markenkonformes PDF.

## Schnellstart

```bash
pip install openpyxl fpdf2          # einmalig
python3 offerten/build_template.py  # Vorlage erzeugen
python3 offerten/offerte_to_pdf.py  # Beispiel-PDF erzeugen
# oder beides zusammen:
bash offerten/erstelle_offerte.sh
```

## Eigene Offerte schreiben

1. `Offerten_Master_Vorlage.xlsx` öffnen.
2. Blatt **Stammdaten**: Firma/Sachbearbeiter prüfen, Standard-Rabatt & MwSt
   setzen (z. B. MwSt `8.1%` für die Schweiz, oder `0%` für ein Budgetangebot).
3. Blatt **Artikel**: eigene Positionen + Wochenpreise pflegen.
4. Blatt **Offerte**: Kundendaten, Offerte-Nr., Daten und Positionen erfassen
   (Beschreibung per Dropdown – Preis kommt automatisch). Eigene Texte sind
   jederzeit möglich.
5. PDF erzeugen – Weg A oder B.

## Hinweise
- Der Endbetrag des Beispiels (`16'609.27`) weicht um **1 Rappen** vom Original
  (`16'609.26`) ab – ein Rundungsartefakt der Quelle; hier wird konsistent
  kaufmännisch gerundet.
- Die Vorlage ist deterministisch aus `build_template.py` reproduzierbar.
