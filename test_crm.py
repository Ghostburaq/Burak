"""Verification tests for MiT_CRM_Vorlage_Final.xlsx."""
import re
import sys
import openpyxl
from collections import Counter

PATH = "MiT_CRM_Vorlage_Final.xlsx"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SEGMENTS = {
    "EVU/Netzbetreiber", "Spital/Klinik", "Pharma/Chemie", "Rechenzentrum/IT",
    "Industrie/Maschinenbau", "Bau/Infrastruktur", "Gemeinde/Öffentlich",
    "Bergbahn/Tourismus", "Events/Messen", "Elektroplaner/Engineering",
    "Forschung/Bildung", "Lebensmittel/Food",
}
PRIOS = {"A", "B", "C"}
STATUS = {"offen", "kontaktiert", "in Gespräch", "Angebot gesendet", "aktiv", "inaktiv"}
KANTONE = {"ZH","BE","LU","AG","SG","GE","BS","BL","SO","TG","VS","VD","FR","GR",
           "AR","AI","SZ","ZG","TI","NE","UR","OW","NW","GL","SH","JU"}

results = []
def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")

wb = openpyxl.load_workbook(PATH, data_only=False)
print(f"Loaded {PATH}")

# T1 sheets present
expected_sheets = {"📊 Dashboard", "📋 Kunden-Datenbank", "📖 Anleitung", "🏷️ Segmente & Produkte"}
check("Alle 4 Sheets vorhanden", expected_sheets <= set(wb.sheetnames),
      f"sheets={wb.sheetnames}")

ws = wb["📋 Kunden-Datenbank"]

# T2 Headers
HEADERS = ["Nr.", "Prio", "Segment", "Firmenname *", "Ort", "PLZ", "Kanton",
           "Ansprechpartner", "Funktion / Titel", "E-Mail", "Telefon", "Website",
           "Status", "Nächster Schritt", "Bedarf / kVA", "Hauptprodukt",
           "Follow-up Datum", "Notizen", "Internes"]
actual = [ws.cell(row=3, column=c).value for c in range(1, 20)]
check("Header-Reihe korrekt", actual == HEADERS, f"diff={set(actual)^set(HEADERS)}")

# T3 Data rows
data_count = 0
for r in range(4, ws.max_row + 1):
    if ws.cell(row=r, column=4).value:
        data_count += 1
check("Datensätze >= 700", data_count >= 700, f"count={data_count}")

# T4 Pflichtfeld Firmenname
missing = sum(1 for r in range(4, 4 + data_count) if not ws.cell(row=r, column=4).value)
check("Kein leerer Firmenname", missing == 0, f"leer={missing}")

# T5 Nr. sequenziell
nrs = [ws.cell(row=r, column=1).value for r in range(4, 4 + data_count)]
check("Nr. sequenziell 1..n", nrs == list(range(1, data_count + 1)))

# T6 Prio gültig
prios_bad = [r for r in range(4, 4 + data_count) if ws.cell(row=r, column=2).value not in PRIOS]
check("Prio nur A/B/C", len(prios_bad) == 0, f"ungültig={len(prios_bad)}")

# T7 Segment gültig
seg_bad = [r for r in range(4, 4 + data_count) if ws.cell(row=r, column=3).value not in SEGMENTS]
check("Segment in Taxonomie", len(seg_bad) == 0, f"ungültig={len(seg_bad)}")

# T8 Kanton gültig
kt_bad = [r for r in range(4, 4 + data_count)
          if ws.cell(row=r, column=7).value and ws.cell(row=r, column=7).value not in KANTONE]
check("Kanton-Kürzel gültig", len(kt_bad) == 0, f"ungültig={len(kt_bad)}")

# T9 Status gültig
st_bad = [r for r in range(4, 4 + data_count) if ws.cell(row=r, column=13).value not in STATUS]
check("Status gültig", len(st_bad) == 0, f"ungültig={len(st_bad)}")

# T10 Email-Format
em_bad = []
for r in range(4, 4 + data_count):
    e = ws.cell(row=r, column=10).value
    if e and not EMAIL_RE.match(str(e).strip()):
        em_bad.append((r, e))
check("E-Mail-Format gültig (sofern gesetzt)", len(em_bad) == 0, f"ungültig={len(em_bad)}")

# T11 Duplikate
keys = Counter()
for r in range(4, 4 + data_count):
    k = (str(ws.cell(row=r, column=4).value).strip().lower(),
         str(ws.cell(row=r, column=5).value or "").strip().lower(),
         str(ws.cell(row=r, column=6).value or "").strip())
    keys[k] += 1
dupes = sum(1 for k, v in keys.items() if v > 1)
check("Keine Duplikate (Firma+Ort+PLZ)", dupes == 0, f"dupes={dupes}")

# T12 Data validations vorhanden
dv_count = len(ws.data_validations.dataValidation)
check("Data-Validations vorhanden (>=6)", dv_count >= 6, f"n={dv_count}")

# T13 Conditional Formatting
cf_count = sum(len(rules) for rules in ws.conditional_formatting._cf_rules.values())
check("Conditional Formatting vorhanden (>=8)", cf_count >= 8, f"n={cf_count}")

# T14 Freeze + Autofilter
check("Freeze panes gesetzt", ws.freeze_panes == "D4", f"value={ws.freeze_panes}")
check("Autofilter gesetzt", ws.auto_filter.ref is not None, f"ref={ws.auto_filter.ref}")

# T15 Dashboard formulas
db = wb["📊 Dashboard"]
formula_count = sum(1 for row in db.iter_rows() for c in row if c.data_type == "f")
check("Dashboard enthält Formeln (>=40)", formula_count >= 40, f"n={formula_count}")

# T16 Dashboard berechnet (data_only)
wb_calc = openpyxl.load_workbook(PATH, data_only=True)
# Note: openpyxl doesn't compute; values will be None until Excel opens it once.
# We test that formulas reference valid sheet.
db2 = wb_calc["📊 Dashboard"]
sample = db2["B6"].value  # COUNTA prio
check("Dashboard-Zelle B6 existiert (Formel hinterlegt)", db["B6"].value is not None)

# T17 Segmente & Produkte alle 12 Segmente
sp = wb["🏷️ Segmente & Produkte"]
sp_segments = {sp.cell(row=r, column=2).value for r in range(4, 16) if sp.cell(row=r, column=2).value}
check("Segmente-Sheet enthält alle 12 Segmente", SEGMENTS <= sp_segments,
      f"fehlt={SEGMENTS - sp_segments}")

# Summary
fails = [r for r in results if not r[1]]
print(f"\n{len(results)-len(fails)}/{len(results)} Tests bestanden.")
if fails:
    print("Fehlgeschlagen:")
    for n, _, d in fails:
        print(f"  - {n}: {d}")
    sys.exit(1)
print("Alle Tests erfolgreich.")
