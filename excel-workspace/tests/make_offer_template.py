#!/usr/bin/env python3
"""Erzeugt eine leere Offerten-Import-Vorlage (2 Blätter) für Ctrl+Shift+I.
Der Benutzer füllt die Zeilen und importiert die Datei — Kopf wird automatisch
in 35_OFFERTEN + 02_PIPELINE + 03_KUNDEN_CRM verteilt, Positionen in 36."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

wb = openpyxl.Workbook()
hdrfill = PatternFill("solid", fgColor="7F6000")
hf = Font(name="Segoe UI", bold=True, color="FFFFFF")
note = Font(name="Segoe UI", italic=True, color="7F6000")

ws = wb.active
ws.title = "Offerten"
ws["A1"] = "OFFERTEN-KOPF  —  eine Zeile je Angebot. Ab Zeile 3 ausfüllen, dann in der Gesamtmappe Ctrl+Shift+I."
ws["A1"].font = note
hdr = ["Belegnummer", "Datum", "Kunde / Firma", "Ansprechpartner", "Einsatzort",
       "Segment", "Vertrieb", "Projektleiter", "Mietbeginn", "Mietende", "Tage",
       "Netto CHF", "MwSt CHF", "Total CHF", "Tagespreis CHF", "Status",
       "Vorgangsnr", "Kundennr", "Ihr Beleg", "Bemerkung"]
for i, h in enumerate(hdr, start=1):
    c = ws.cell(row=2, column=i, value=h)
    c.font = hf; c.fill = hdrfill; c.alignment = Alignment(wrap_text=True, horizontal="center")
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = max(12, len(h) + 2)
ws.append(["OF20260901-1234-01", "01.09.2026", "Beispiel Kunde AG", "Vorname Name",
           "Musterstrasse 1, 8000 Zürich", "Events & Kultur", "Ücöz Burak", "Ücöz Burak",
           "01.10.2026", "10.10.2026", 9, 12000, 972, 12972, 333.33, "offered",
           "VK-ANF-20260901-001", "12345", "Mail vom 01.09.2026", "Beispielzeile — überschreiben/löschen"])
ws.row_dimensions[2].height = 28
ws.freeze_panes = "A3"

ws2 = wb.create_sheet("Positionen")
ws2["A1"] = "OFFERTEN-POSITIONEN — Belegnummer identisch zum Kopf. Ab Zeile 3 ausfüllen."
ws2["A1"].font = note
hdr2 = ["Belegnummer", "Kunde / Firma", "Montagebereich", "Pos.", "Artikelnr.",
        "Bezeichnung", "Anzahl", "Einheit", "Dauer", "Einzelpreis CHF", "Rabatt %", "Gesamtpreis CHF", "Bemerkung"]
for i, h in enumerate(hdr2, start=1):
    c = ws2.cell(row=2, column=i, value=h)
    c.font = hf; c.fill = hdrfill; c.alignment = Alignment(wrap_text=True, horizontal="center")
    ws2.column_dimensions[openpyxl.utils.get_column_letter(i)].width = max(12, len(h) + 2)
ws2.append(["OF20260901-1234-01", "Beispiel Kunde AG", "", 1, "M-GEN-000012",
            "Mobiler Generator 300 kVA Stage V", 1, "St", "9 KT", 279, 0.1, 2260, ""])
ws2.row_dimensions[2].height = 28
ws2.freeze_panes = "A3"

wb.save("MiT_Offerten_Import_Vorlage.xlsx")
print("OK -> MiT_Offerten_Import_Vorlage.xlsx")
