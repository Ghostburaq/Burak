# PDF-Knopf in Excel einrichten (einmalig, ca. 2 Minuten)

So bekommen Sie in Excel selbst eine Schaltfläche **„Offerte als PDF“**, die
das Blatt *Offerte* mit einem Klick als PDF speichert.

## 1. Mappe als .xlsm speichern
`Datei ▸ Speichern unter ▸ Dateityp:` **Excel-Arbeitsmappe mit Makros (*.xlsm)**.
(PDF-Schaltflächen brauchen Makros – die laufen nur in `.xlsm`.)

## 2. Makro importieren
- Tastenkombination **Alt + F11** (öffnet den VBA-Editor).
- Menü **Datei ▸ Datei importieren…** → `PdfButton.bas` auswählen.
- VBA-Editor schließen.

## 3. Entwicklertools einblenden (falls nicht sichtbar)
`Datei ▸ Optionen ▸ Menüband anpassen` → rechts **Entwicklertools** anhaken.

## 4. Schaltfläche einfügen
- Reiter **Entwicklertools ▸ Einfügen ▸ Formularsteuerelemente ▸ Schaltfläche**.
- Auf dem Blatt *Offerte* (z. B. neben den Kopf) aufziehen.
- Im Dialog das Makro **`Offerte_Als_PDF`** auswählen → OK.
- Beschriftung in z. B. „📄 PDF erstellen“ ändern (Rechtsklick ▸ Text bearbeiten).

## Fertig
Ein Klick erzeugt `<Offerte-Nr>.pdf` im Ordner der Arbeitsmappe und öffnet es.
Der Dateiname kommt automatisch aus Zelle **G8** (Offerte-Nr.).

---

### Mac-Hinweis
Auf macOS funktioniert `ExportAsFixedFormat` ebenfalls; der Speicherort ist der
Ordner der Mappe. Lässt eine Mac-Excel-Version das Makro nicht zu, nutzen Sie
`Datei ▸ Exportieren ▸ PDF` und wählen vorher das Blatt *Offerte*.

### Ohne Makros / ohne Excel
Alternativ erzeugt das Skript `offerte_to_pdf.py` aus der ausgefüllten Mappe
ein markenkonformes PDF:

```bash
python3 offerten/offerte_to_pdf.py
```
