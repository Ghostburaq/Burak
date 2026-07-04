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

wb.save("testimport.xlsx")
print("OK -> testimport.xlsx")
