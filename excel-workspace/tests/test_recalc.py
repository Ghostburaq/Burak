#!/usr/bin/env python3
"""Recalc-Test: prüft die von LibreOffice berechneten Werte auf Formelfehler."""
import sys
import openpyxl

FILE = sys.argv[1] if len(sys.argv) > 1 else "lo_out/MiT_GESAMTMAPPE_2026.xlsx"
ERRS = ("#REF!", "#NAME?", "#VALUE!", "#DIV/0!", "#N/A", "#NULL!", "#NUM!", "Err:")
wb = openpyxl.load_workbook(FILE, data_only=True)
fehler, leer_formeln, checked = [], 0, 0
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            if v is None:
                continue
            checked += 1
            if isinstance(v, str) and any(v.startswith(e) or e in v[:12] for e in ERRS):
                fehler.append(f"{ws.title}!{c.coordinate} = {v!r}")

# Stichproben: zentrale KPIs müssen numerisch & plausibel sein
def val(sheet, coord):
    return wb[sheet][coord].value

proben = [
    ("02_PIPELINE", "O5", (int, float)),      # Marge-Formel
    ("02_PIPELINE", "Q5", (int, float)),      # Gew.Wert
    ("01_DASHBOARD", "A6", (int, float)),     # WON-Kachel
    ("05_FORECAST", "C6", (int, float)),      # Status-Volumen
    ("06_MONATSREPORT", "A6", (int, float)),  # WON KPI
    ("17_GLOBAL_ANALYTICS", "B6", (int, float)),
    ("07_CEO_REPORT", "A6", (int, float)),
    ("08_DIAGRAMME", "C5", (int, float)),
    ("19_PREISLISTE_CHF", "G5", (int, float)),
    ("21_GEN_RECHNER", "B18", (int, float)),
    ("04_KUNDENKARTEI", "A5", (int, float)),  # Nr.-Formel
]
proben_fail = []
for s, co, typ in proben:
    v = val(s, co)
    if not isinstance(v, typ):
        proben_fail.append(f"{s}!{co} = {v!r} (erwartet {typ})")

print(f"Geprüfte Zellen mit Wert: {checked}")
print(f"Formelfehler: {len(fehler)}")
for f in fehler[:30]:
    print("  ", f)
print(f"KPI-Stichproben fehlgeschlagen: {len(proben_fail)}")
for f in proben_fail:
    print("  ", f)
print("Beispielwerte: WON-Kachel =", val("01_DASHBOARD", "A6"),
      "| Marge O5 =", val("02_PIPELINE", "O5"),
      "| GlobAnalytics B6 =", val("17_GLOBAL_ANALYTICS", "B6"), "| CEO A6 =", val("07_CEO_REPORT", "A6"),
      "| Kartei-Status I5 =", val("04_KUNDENKARTEI", "I5"))
sys.exit(1 if (fehler or proben_fail) else 0)
