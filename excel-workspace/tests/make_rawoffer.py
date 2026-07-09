#!/usr/bin/env python3
"""Erzeugt eine ROH eingefügte Offerte im echten Angebots-Layout
(Label:Wert-Kopf-Block + Positionstabelle + Summen), so wie sie aus dem
Mobil-in-Time-System als Excel herausfällt. Dient als Import-Nachweis:
Kopf + Positionen werden erkannt und in 35/36/Pipeline/CRM verteilt."""
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Angebot"

# Absender + Empfängerblock (oben links)
ws["A1"] = "Mobil in Time AG - Mattenstrasse 3 - 8253 Diessenhofen"
ws["A2"] = "Muster Bau & Energie AG"          # <- Kunde (erste Empfängerzeile)
ws["A3"] = "Herr Reto Beispiel"               # <- Ansprechpartner
ws["A4"] = "Beispielweg 12"
ws["A5"] = "CH-3600 Thun"

# Info-Box oben rechts (Label:Wert)
box = [("Angebot", ""), ("Vorgangsnummer", "VK-ANF-20260709-099"),
       ("Belegnummer", "OF-ROH-TEST-777"), ("Datum", "09.07.2026"),
       ("Kundennummer", "55555"), ("Bearbeiter", "Judith Schranz"),
       ("Vertrieb", "Curreli Mauro"), ("Projektleiter", "Ücöz Burak")]
for i, (lab, val) in enumerate(box, start=1):
    ws.cell(row=i, column=6, value=lab)
    if val:
        ws.cell(row=i, column=7, value=val)

# Einsatzort-Box
ws["A10"] = "Einsatzort:"; ws["B10"] = "Baustelle Thun Süd, 3600 Thun"
ws["A11"] = "Ihr Beleg:"; ws["B11"] = "Mail vom 09.07.2026"

# Positionstabelle
ws["A14"] = "Pos."; ws["B14"] = "Artikelnr."; ws["C14"] = "Bezeichnung"
ws["D14"] = "Anzahl"; ws["E14"] = "Dauer"; ws["F14"] = "Einzelpreis"
ws["G14"] = "Rabatt"; ws["H14"] = "Gesamtpreis"
pos = [
    [1, "M-GEN-000012", "Mobiler Generator - 300 kVA Stage V", 1, "7 KT", 279.00, "10%", 1757.70],
    [2, "M-ZUB-000307", "Mobiler Dieseltank - 3000 l & 380 l AdBlue", 1, "7 KT", 32.00, "10%", 201.60],
    [3, "V-TRP-000009", "Transport Pauschale LKW mit Kran", 1, "", 1400.00, "", 1400.00],
]
for i, row in enumerate(pos, start=15):
    for j, v in enumerate(row, start=1):
        ws.cell(row=i, column=j, value=v)

# Summenblock (Label links, Betrag rechts)
ws["G19"] = "Zwischensumme CHF"; ws["H19"] = 3359.30
ws["G20"] = "zzgl. MwSt. 8.10 %"; ws["H20"] = 272.10
ws["G21"] = "Endsumme inkl. vRG CHF"; ws["H21"] = 3631.40
ws["A23"] = "Mietpreis pro Tag exkl. MwSt. 285.30 CHF"

wb.save("demo_rawoffer.xlsx")
print("OK -> demo_rawoffer.xlsx")
