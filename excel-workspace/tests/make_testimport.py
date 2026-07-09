#!/usr/bin/env python3
"""Erzeugt eine Test-Importdatei:
- Blatt 'Neue Deals': Pipeline-Daten mit FREMDEN Headern (Alias-Test) + 1 Duplikat
- Blatt 'Neue Firmen': CRM-Daten
"""
import openpyxl

wb = openpyxl.Workbook()

ws = wb.active
ws.title = "Neue Deals"
ws["A1"] = "Irgendein Titel — Import-Testdatei"
hdr = ["#", "Kunde / Unternehmen", "Kanton", "Segment", "Leistung / Fleet", "kW",
       "Dauer", "Start", "Volumen CHF", "Equipment CHF", "Transport CHF",
       "Treibstoff CHF", "Techniker CHF", "Übrige CHF", "Status", "Wahrsch. %",
       "Akquis. Typ", "Nächster Schritt"]
for i, h in enumerate(hdr, start=1):
    ws.cell(row=3, column=i, value=h)
rows = [
    # Duplikat: existiert schon in 02_PIPELINE (Kunde+Leistung)
    [99, "Ice Hockey Championship", "ZH", "Events & Sport", "2×600+2×200 kVA", 1600,
     28, "02.05.2026", 310000, 195000, 8000, 12000, 15000, 5000, "WON", 1.0, "Warm – Aggreko", "dup"],
    # Neu 1
    [1, "TEST Kunde Alpha AG", "BE", "Industrie", "500 kVA Generator", 500,
     14, "01.08.2026", 42000, 20000, 1500, 2000, 1800, 500, "offered", 0.6, "Kalt (Burak)", "Offerte senden"],
    # Neu 2
    [2, "TEST Kunde Beta GmbH", "ZH", "Events & Kultur", "2×60 kVA", 120,
     7, "15.09.2026", 9500, 4000, 600, 300, 400, 100, "follow-up", 0.3, "Inbound", "Rückruf KW34"],
]
for r_i, row in enumerate(rows, start=4):
    for c_i, v in enumerate(row, start=1):
        ws.cell(row=r_i, column=c_i, value=v)

ws2 = wb.create_sheet("Neue Firmen")
hdr2 = ["Nr.", "Prio", "Segment", "Firmenname *", "Ort", "PLZ", "Kanton",
        "Ansprechpartner", "E-Mail", "Status", "Wahrsch. %", "Wert CHF"]
for i, h in enumerate(hdr2, start=1):
    ws2.cell(row=1, column=i, value=h)
rows2 = [
    [1, "A", "EVU/Netzbetreiber", "AEW Energie AG", "Aarau", "5001", "AG",
     "Leiter Netzbetrieb", "info@aew.ch", "offen", 10, ""],           # Duplikat
    [2, "A", "Rechenzentrum/IT", "TEST Datacenter Gamma AG", "Zug", "6300", "ZG",
     "CTO", "cto@gamma-dc.ch", "offen", 25, 150000],                  # Neu
]
for r_i, row in enumerate(rows2, start=2):
    for c_i, v in enumerate(row, start=1):
        ws2.cell(row=r_i, column=c_i, value=v)

# Blatt 'Offerte Test': Offerten-Kopf -> 35_OFFERTEN + Auto-Verteilung Pipeline/CRM
ws3 = wb.create_sheet("Offerte Test")
hdr3 = ["Belegnummer", "Datum", "Kunde / Firma", "Ansprechpartner", "Einsatzort",
        "Vertrieb", "Mietbeginn", "Mietende", "Tage", "Netto CHF", "MwSt CHF",
        "Total CHF", "Status"]
for i, h in enumerate(hdr3, start=1):
    ws3.cell(row=1, column=i, value=h)
ws3.append(["OF-TEST-9001", "09.07.2026", "TEST Offerten Kunde AG", "Max Muster",
            "Teststrasse 1, 8000 Zürich", "Burak", "01.09.2026", "10.09.2026", 9,
            12345, 1000, 13345, "offered"])

# Blatt 'Offerte Positionen': -> 36_OFFERTEN_POSITIONEN
ws4 = wb.create_sheet("Offerte Positionen")
hdr4 = ["Belegnummer", "Kunde / Firma", "Pos.", "Artikelnr.", "Bezeichnung",
        "Anzahl", "Einheit", "Dauer", "Einzelpreis CHF", "Rabatt %", "Gesamtpreis CHF"]
for i, h in enumerate(hdr4, start=1):
    ws4.cell(row=1, column=i, value=h)
ws4.append(["OF-TEST-9001", "TEST Offerten Kunde AG", 1, "M-GEN-000012",
            "Generator 300 kVA", 1, "St", "9 KT", 279, 0, 2511])
ws4.append(["OF-TEST-9001", "TEST Offerten Kunde AG", 2, "M-ZUB-000307",
            "Dieseltank 3000 l", 1, "St", "9 KT", 32, 0, 288])

wb.save("testimport.xlsx")
print("OK -> testimport.xlsx")
