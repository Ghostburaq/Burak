"""Rebuild MiT CRM template with verified data, dropdowns, conditional
formatting, dashboard and consistent segment taxonomy."""

from copy import copy
from collections import Counter
import re
from datetime import datetime

import openpyxl
from openpyxl.styles import (
    Alignment, Border, Color, Fill, Font, PatternFill, Side,
)
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

SRC = "MiT_CRM_Vorlage_Original.xlsx"
DST = "MiT_CRM_Vorlage_Final.xlsx"

# Canonical taxonomy (used everywhere in the file)
SEGMENTS = [
    "EVU/Netzbetreiber",
    "Spital/Klinik",
    "Pharma/Chemie",
    "Rechenzentrum/IT",
    "Industrie/Maschinenbau",
    "Bau/Infrastruktur",
    "Gemeinde/Öffentlich",
    "Bergbahn/Tourismus",
    "Events/Messen",
    "Elektroplaner/Engineering",
    "Forschung/Bildung",
    "Lebensmittel/Food",
]
SEGMENT_NORMALIZE = {
    "Spital/Gesundheit": "Spital/Klinik",
    "RZ/Telekom": "Rechenzentrum/IT",
    "Elektroplaner": "Elektroplaner/Engineering",
    "Events / Messen": "Events/Messen",
}
PRIOS = ["A", "B", "C"]
STATUS = ["offen", "kontaktiert", "in Gespräch", "Angebot gesendet", "aktiv", "inaktiv"]
PRODUCTS = [
    "Generator", "BESS", "Notstrom/USV", "USV",
    "BESS + Generator", "PQ-Analyse", "Wärme", "Kälte", "Trafo",
    "Mobile MS-Verteilung", "Kabel", "Baustromverteiler",
]
KANTONE = ["ZH","BE","LU","AG","SG","GE","BS","BL","SO","TG","VS","VD",
           "FR","GR","AR","AI","SZ","ZG","TI","NE","UR","OW","NW","GL","SH","JU"]

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# -- Load source -----------------------------------------------------------
src = openpyxl.load_workbook(SRC, data_only=False)
src_ws = src["📋 Kunden-Datenbank"]

raw_rows = []
for r in range(4, src_ws.max_row + 1):
    firma = src_ws.cell(row=r, column=4).value
    if not firma:
        continue
    row = [src_ws.cell(row=r, column=c).value for c in range(1, 20)]
    raw_rows.append(row)

# -- Clean & normalize -----------------------------------------------------
seen = set()
cleaned = []
report = {"input": len(raw_rows), "dupes": 0, "fixed_emails": 0, "renamed_segments": 0}
for row in raw_rows:
    # row indices: 0=Nr, 1=Prio, 2=Segment, 3=Firma, ..., 9=Email
    seg = row[2]
    if seg in SEGMENT_NORMALIZE:
        row[2] = SEGMENT_NORMALIZE[seg]
        report["renamed_segments"] += 1

    email = row[9]
    if email and not EMAIL_RE.match(str(email).strip()):
        row[9] = None
        report["fixed_emails"] += 1

    key = (str(row[3]).strip().lower(), str(row[4] or "").strip().lower(),
           str(row[5] or "").strip())
    if key in seen:
        report["dupes"] += 1
        continue
    seen.add(key)
    cleaned.append(row)

# Renumber Nr.
for i, row in enumerate(cleaned, start=1):
    row[0] = i

report["output"] = len(cleaned)
print("Cleaning report:", report)

# -- Build destination workbook -------------------------------------------
wb = openpyxl.Workbook()
wb.remove(wb.active)

# Styles
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Calibri", size=16, bold=True, color="1F4E78")
SUBTITLE_FONT = Font(name="Calibri", size=10, italic=True, color="595959")
THIN = Side(border_style="thin", color="D0D7DE")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)

# ===== Kunden-Datenbank =====
ws = wb.create_sheet("📋 Kunden-Datenbank")
ws["A1"] = "MiT CRM — Kunden-Datenbank Vorlage  |  Mobil in Time AG"
ws["A1"].font = TITLE_FONT
ws.merge_cells("A1:S1")
ws["A2"] = ("→ Diese Datei direkt in MiT CRM importieren: Header > "
            "'📥 Importieren' > Datei wählen. Spalten werden automatisch erkannt.")
ws["A2"].font = SUBTITLE_FONT
ws.merge_cells("A2:S2")

HEADERS = ["Nr.", "Prio", "Segment", "Firmenname *", "Ort", "PLZ", "Kanton",
           "Ansprechpartner", "Funktion / Titel", "E-Mail", "Telefon", "Website",
           "Status", "Nächster Schritt", "Bedarf / kVA", "Hauptprodukt",
           "Follow-up Datum", "Notizen", "Internes"]
for c, h in enumerate(HEADERS, start=1):
    cell = ws.cell(row=3, column=c, value=h)
    cell.font = HEADER_FONT
    cell.fill = HEADER_FILL
    cell.alignment = ALIGN_CENTER
    cell.border = BORDER

for i, row in enumerate(cleaned, start=4):
    if row[12] is None:
        row[12] = "offen"
    for c, val in enumerate(row, start=1):
        cell = ws.cell(row=i, column=c, value=val)
        cell.alignment = ALIGN_LEFT
        cell.border = BORDER

LAST_ROW = 3 + len(cleaned)
EXTRA_ROWS = 100  # space for future entries with validations applied
TOTAL_ROW = LAST_ROW + EXTRA_ROWS

# Column widths
widths = {"A": 5, "B": 6, "C": 22, "D": 38, "E": 18, "F": 7, "G": 7,
          "H": 22, "I": 22, "J": 28, "K": 18, "L": 28, "M": 16, "N": 36,
          "O": 36, "P": 18, "Q": 14, "R": 38, "S": 18}
for col, w in widths.items():
    ws.column_dimensions[col].width = w
ws.row_dimensions[3].height = 28
ws.freeze_panes = "D4"
ws.auto_filter.ref = f"A3:S{LAST_ROW}"
ws.sheet_view.showGridLines = False

# Data validations (apply across data + buffer rows)
def add_dv(formula, col_letter, allow_blank=True):
    dv = DataValidation(type="list", formula1=formula, allow_blank=allow_blank,
                        showErrorMessage=True, errorTitle="Ungültiger Wert",
                        error="Bitte einen Wert aus der Dropdown-Liste wählen.")
    dv.add(f"{col_letter}4:{col_letter}{TOTAL_ROW}")
    ws.add_data_validation(dv)

def list_formula(values):
    return '"' + ",".join(values) + '"'

add_dv(list_formula(PRIOS), "B")
add_dv(list_formula(SEGMENTS), "C")
add_dv(list_formula(KANTONE), "G")
add_dv(list_formula(STATUS), "M")
add_dv(list_formula(PRODUCTS), "P")

# Email validation (regex via formula)
dv_email = DataValidation(
    type="custom",
    formula1=f'=OR(ISBLANK(J4),AND(ISNUMBER(SEARCH("@",J4)),ISNUMBER(SEARCH(".",J4))))',
    allow_blank=True, showErrorMessage=True,
    errorTitle="Ungültige E-Mail", error="E-Mail muss '@' und '.' enthalten.")
dv_email.add(f"J4:J{TOTAL_ROW}")
ws.add_data_validation(dv_email)

# Date validation
dv_date = DataValidation(type="date", allow_blank=True,
                         showErrorMessage=True, errorTitle="Datum",
                         error="Bitte gültiges Datum eintragen.")
dv_date.add(f"Q4:Q{TOTAL_ROW}")
ws.add_data_validation(dv_date)

# Conditional formatting
def fill(hex_): return PatternFill("solid", fgColor=hex_)

# Prio colors
ws.conditional_formatting.add(f"B4:B{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"A"'], fill=fill("F8CBAD"), font=Font(bold=True, color="9C0006")))
ws.conditional_formatting.add(f"B4:B{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"B"'], fill=fill("FFE699"), font=Font(bold=True, color="7F6000")))
ws.conditional_formatting.add(f"B4:B{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"C"'], fill=fill("C6E0B4"), font=Font(bold=True, color="375623")))

# Status colors
ws.conditional_formatting.add(f"M4:M{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"offen"'], fill=fill("D9E1F2")))
ws.conditional_formatting.add(f"M4:M{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"kontaktiert"'], fill=fill("BDD7EE")))
ws.conditional_formatting.add(f"M4:M{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"in Gespräch"'], fill=fill("FFE699")))
ws.conditional_formatting.add(f"M4:M{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"Angebot gesendet"'], fill=fill("F4B084")))
ws.conditional_formatting.add(f"M4:M{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"aktiv"'], fill=fill("A9D08E"), font=Font(bold=True, color="375623")))
ws.conditional_formatting.add(f"M4:M{TOTAL_ROW}",
    CellIsRule(operator="equal", formula=['"inaktiv"'], fill=fill("D9D9D9")))

# Follow-up overdue highlight
ws.conditional_formatting.add(f"Q4:Q{TOTAL_ROW}",
    FormulaRule(formula=[f"AND(ISNUMBER(Q4),Q4<TODAY(),Q4<>\"\")"],
                fill=fill("F8CBAD"), font=Font(bold=True, color="9C0006")))

# Missing Firma flag (red border) - via formula rule
ws.conditional_formatting.add(f"D4:D{TOTAL_ROW}",
    FormulaRule(formula=[f"AND(ROW()<= {LAST_ROW},D4=\"\")"],
                fill=fill("FFC7CE"), font=Font(color="9C0006", bold=True)))

# ===== Anleitung =====
an = wb.create_sheet("📖 Anleitung")
an.sheet_view.showGridLines = False
an.column_dimensions["A"].width = 2
an.column_dimensions["B"].width = 28
an.column_dimensions["C"].width = 80
an["B1"] = "MiT CRM — Import-Anleitung & Feldbeschreibungen"
an["B1"].font = TITLE_FONT
an.merge_cells("B1:C1")

an_rows = [
    ("  🚀  Import-Schritte", ""),
    ("  Schritt 1", "Daten in Tabelle 'Kunden-Datenbank' eintragen"),
    ("  Schritt 2", "Datei speichern als .xlsx oder .csv"),
    ("  Schritt 3", "MiT CRM öffnen → Header-Button '📥 Importieren' klicken"),
    ("  Schritt 4", "Datei hineinziehen oder auswählen"),
    ("  Schritt 5", "KI erkennt Spalten automatisch — Vorschau prüfen"),
    ("  Schritt 6", "'Importieren' klicken → Daten verteilen sich auf alle Tabs"),
    ("", ""),
    ("  📋  Pflichtfelder & Dropdown-Werte", ""),
    ("  Firmenname *", "Pflichtfeld — Import schlägt fehl wenn leer"),
    ("  Prio", "Werte: " + " · ".join(PRIOS) + " (A=hoch, B=mittel, C=niedrig)"),
    ("  Segment", " · ".join(SEGMENTS)),
    ("  Kanton", "Zweistelliges Kürzel: " + ", ".join(KANTONE)),
    ("  Status", " · ".join(STATUS)),
    ("  Hauptprodukt", " · ".join(PRODUCTS)),
    ("  Follow-up Datum", "Format: TT.MM.JJJJ — überfällige Termine werden rot markiert"),
    ("", ""),
    ("  🗺️  Karte: Standort-Koordinaten", ""),
    ("  Ort (Stadt)", "→ Karte zeigt exakten Stadtpin statt Kantonshauptort"),
    ("  PLZ", "→ Feinere Geocodierung bei mehreren Firmen in einer Stadt"),
    ("  Kanton", "→ Fallback wenn Ort nicht erkannt wird"),
    ("  Tipp", "Je mehr Felder ausgefüllt, desto präziser die Kartenposition"),
    ("", ""),
    ("  ⚡  Auto-Verteilung auf CRM-Tabs", ""),
    ("  👥 Kontakte", "Alle importierten Zeilen als Kontakte"),
    ("  🗺️ Karte", "Pins an exakter Stadt-Position"),
    ("  🏔️ Kantone", "26 Kantone mit Kontakt-Anzahl befüllt"),
    ("  🎯 Pipeline", "Prio A+B mit Nächstem Schritt → Deals"),
    ("  ✅ Aufgaben", "Nächster Schritt + Follow-up Datum → Aufgaben"),
    ("  🏷️ Tags", "Segment + Prio automatisch als Tags"),
    ("  📞 Dialer", "Alle Kontakte mit Telefon → Kaltakquise Queue"),
    ("", ""),
    ("  🛡️  Eingebaute Validierung", ""),
    ("  Dropdowns", "Prio, Segment, Kanton, Status, Hauptprodukt sind Dropdown-gesteuert"),
    ("  Farbcodes", "Prio A/B/C, Status und überfällige Follow-ups werden automatisch eingefärbt"),
    ("  Dashboard", "Tab '📊 Dashboard' enthält Live-Auswertungen aller Stammdaten"),
]
r = 3
for label, val in an_rows:
    if label == "" and val == "":
        r += 1
        continue
    an.cell(row=r, column=2, value=label)
    an.cell(row=r, column=3, value=val)
    if label.startswith("  🚀") or label.startswith("  📋") or label.startswith("  🗺️") \
       or label.startswith("  ⚡") or label.startswith("  🛡️"):
        an.cell(row=r, column=2).font = Font(bold=True, color="1F4E78", size=12)
    else:
        an.cell(row=r, column=2).font = Font(bold=True)
    an.cell(row=r, column=2).alignment = ALIGN_LEFT
    an.cell(row=r, column=3).alignment = ALIGN_LEFT
    r += 1

# ===== Segmente & Produkte =====
sp = wb.create_sheet("🏷️ Segmente & Produkte")
sp.sheet_view.showGridLines = False
sp.column_dimensions["A"].width = 2
sp.column_dimensions["B"].width = 28
sp.column_dimensions["C"].width = 50
sp.column_dimensions["D"].width = 50
sp.column_dimensions["E"].width = 14
sp["B1"] = "Segment-Referenz & Produkt-Matrix"
sp["B1"].font = TITLE_FONT
sp.merge_cells("B1:E1")

sp_headers = ["Segment", "Unterbereich (Beispiele)", "Empfohlene MiT-Produkte", "Prio-Tendenz"]
for c, h in enumerate(sp_headers, start=2):
    cell = sp.cell(row=3, column=c, value=h)
    cell.font = HEADER_FONT
    cell.fill = HEADER_FILL
    cell.alignment = ALIGN_CENTER

SEGMENT_INFO = [
    ("EVU/Netzbetreiber", "Kantonale EVU, Stadtwerke, Verteilnetzbetreiber",
     "Generator, Mobile MS-Verteilung, BESS, PQ-Analyse", "A"),
    ("Spital/Klinik", "Akutspitäler, Kliniken, Pflegeheime, Reha",
     "Notstrom NIV Art.13, USV, Generator, BESS", "A"),
    ("Pharma/Chemie", "Wirkstoff, Galenik, Biotech, Labore",
     "Generator Stage V, BESS, PQ-Monitoring Kl.A", "A"),
    ("Rechenzentrum/IT", "Colocation, Enterprise RZ, Telekom-Infra",
     "BESS + Generator, USV, PQ-Analyse IEC 61000-4-30", "A"),
    ("Industrie/Maschinenbau", "CNC-Fertigung, Giesserei, Automobilzulieferer",
     "Generator, Parallelschaltung, Kabel, Trafo", "B"),
    ("Bau/Infrastruktur", "Hochbau, Tiefbau, Tunnel, Sanierung",
     "Generator, Baustromverteiler, Kabel, IBC Tank", "B"),
    ("Gemeinde/Öffentlich", "Gemeinden, Kantone, Wasserversorgung, Kläranlage",
     "Generator, Notstrom, BESS", "B"),
    ("Bergbahn/Tourismus", "Ski-Resorts, Hotels, Seilbahnen, Events",
     "Generator, Wärme, Kälte, BESS", "B"),
    ("Events/Messen", "Messen, Festivals, Grossevents, Konzerte",
     "Generator, Kälte, Wärme, Kabel, Verteiler", "B/C"),
    ("Elektroplaner/Engineering", "Ingenieurbüros, TGA-Planer, Architekten",
     "Alle Produkte (Planungsunterstützung)", "C"),
    ("Forschung/Bildung", "ETH/EPFL, Fachhochschulen, Forschungsinstitute",
     "USV, BESS, Generator, PQ-Analyse", "B"),
    ("Lebensmittel/Food", "Molkereien, Fleischverarbeitung, Bäckereien",
     "Generator, Kälte, BESS", "B"),
]
for i, (a, b, c, d) in enumerate(SEGMENT_INFO, start=4):
    sp.cell(row=i, column=2, value=a).alignment = ALIGN_LEFT
    sp.cell(row=i, column=3, value=b).alignment = ALIGN_LEFT
    sp.cell(row=i, column=4, value=c).alignment = ALIGN_LEFT
    sp.cell(row=i, column=5, value=d).alignment = ALIGN_CENTER
    for col in range(2, 6):
        sp.cell(row=i, column=col).border = BORDER

# ===== Dashboard =====
db = wb.create_sheet("📊 Dashboard")
db.sheet_view.showGridLines = False
db["A1"] = "MiT CRM — Live Dashboard"
db["A1"].font = TITLE_FONT
db.merge_cells("A1:F1")
db["A2"] = "Auswertungen werden bei jeder Datenänderung in 'Kunden-Datenbank' automatisch aktualisiert."
db["A2"].font = SUBTITLE_FONT
db.merge_cells("A2:F2")

KB = "'📋 Kunden-Datenbank'"
DATA_RANGE_D = f"{KB}!$D$4:$D${TOTAL_ROW}"  # Firma
DATA_RANGE_B = f"{KB}!$B$4:$B${TOTAL_ROW}"  # Prio
DATA_RANGE_C = f"{KB}!$C$4:$C${TOTAL_ROW}"  # Segment
DATA_RANGE_G = f"{KB}!$G$4:$G${TOTAL_ROW}"  # Kanton
DATA_RANGE_M = f"{KB}!$M$4:$M${TOTAL_ROW}"  # Status
DATA_RANGE_P = f"{KB}!$P$4:$P${TOTAL_ROW}"  # Produkt
DATA_RANGE_Q = f"{KB}!$Q$4:$Q${TOTAL_ROW}"  # Follow-up
DATA_RANGE_K = f"{KB}!$K$4:$K${TOTAL_ROW}"  # Telefon
DATA_RANGE_J = f"{KB}!$J$4:$J${TOTAL_ROW}"  # Email

# KPI cards row
db["A4"] = "📈  Kennzahlen"
db["A4"].font = Font(bold=True, size=13, color="1F4E78")

kpis = [
    ("Kontakte gesamt", f"=COUNTA({DATA_RANGE_D})"),
    ("Prio A", f'=COUNTIF({DATA_RANGE_B},"A")'),
    ("Prio B", f'=COUNTIF({DATA_RANGE_B},"B")'),
    ("Prio C", f'=COUNTIF({DATA_RANGE_B},"C")'),
    ("Mit E-Mail", f'=COUNTIF({DATA_RANGE_J},"?*@?*.?*")'),
    ("Mit Telefon", f"=COUNTA({DATA_RANGE_K})"),
]
for i, (label, formula) in enumerate(kpis):
    col = 1 + i
    db.cell(row=5, column=col, value=label).font = Font(bold=True, color="595959", size=10)
    cell = db.cell(row=6, column=col, value=formula)
    cell.font = Font(bold=True, size=18, color="1F4E78")
    cell.alignment = ALIGN_CENTER
    db.column_dimensions[get_column_letter(col)].width = 18
    db.cell(row=5, column=col).fill = PatternFill("solid", fgColor="E7EEF7")
    db.cell(row=6, column=col).fill = PatternFill("solid", fgColor="E7EEF7")
    db.cell(row=5, column=col).alignment = ALIGN_CENTER

# Segment breakdown
db["A8"] = "🏷️  Segment-Verteilung"
db["A8"].font = Font(bold=True, size=13, color="1F4E78")
db["A9"] = "Segment"
db["B9"] = "Anzahl"
db["C9"] = "% Anteil"
for c in ["A9", "B9", "C9"]:
    db[c].font = HEADER_FONT
    db[c].fill = HEADER_FILL
    db[c].alignment = ALIGN_CENTER
for i, seg in enumerate(SEGMENTS, start=10):
    db.cell(row=i, column=1, value=seg)
    db.cell(row=i, column=2, value=f'=COUNTIF({DATA_RANGE_C},A{i})')
    db.cell(row=i, column=3, value=f'=IFERROR(B{i}/COUNTA({DATA_RANGE_D}),0)')
    db.cell(row=i, column=3).number_format = "0.0%"

# Kanton breakdown
row0 = 10 + len(SEGMENTS) + 2
db.cell(row=row0-1, column=1, value="🏔️  Kanton-Verteilung").font = Font(bold=True, size=13, color="1F4E78")
db.cell(row=row0, column=1, value="Kanton").font = HEADER_FONT
db.cell(row=row0, column=2, value="Anzahl").font = HEADER_FONT
db.cell(row=row0, column=1).fill = HEADER_FILL
db.cell(row=row0, column=2).fill = HEADER_FILL
for i, k in enumerate(KANTONE, start=row0+1):
    db.cell(row=i, column=1, value=k)
    db.cell(row=i, column=2, value=f'=COUNTIF({DATA_RANGE_G},A{i})')

# Status pipeline
row1 = row0 + len(KANTONE) + 3
db.cell(row=row1-1, column=4, value="🎯  Pipeline-Status").font = Font(bold=True, size=13, color="1F4E78")
db.cell(row=row1, column=4, value="Status").font = HEADER_FONT
db.cell(row=row1, column=5, value="Anzahl").font = HEADER_FONT
db.cell(row=row1, column=4).fill = HEADER_FILL
db.cell(row=row1, column=5).fill = HEADER_FILL
for i, s in enumerate(STATUS, start=row1+1):
    db.cell(row=i, column=4, value=s)
    db.cell(row=i, column=5, value=f'=COUNTIF({DATA_RANGE_M},D{i})')

# Overdue follow-ups
db.cell(row=row1, column=7, value="⏰  Follow-ups").font = HEADER_FONT
db.cell(row=row1+1, column=7, value="Überfällig")
db.cell(row=row1+1, column=8, value=f'=SUMPRODUCT(({DATA_RANGE_Q}<TODAY())*({DATA_RANGE_Q}<>""))')
db.cell(row=row1+2, column=7, value="Diese Woche")
db.cell(row=row1+2, column=8, value=f'=SUMPRODUCT(({DATA_RANGE_Q}>=TODAY())*({DATA_RANGE_Q}<=TODAY()+7))')
db.cell(row=row1+3, column=7, value="Nächste 30 Tage")
db.cell(row=row1+3, column=8, value=f'=SUMPRODUCT(({DATA_RANGE_Q}>=TODAY())*({DATA_RANGE_Q}<=TODAY()+30))')

# Sheet ordering — put dashboard first
order = ["📊 Dashboard", "📋 Kunden-Datenbank", "📖 Anleitung", "🏷️ Segmente & Produkte"]
wb._sheets = [wb[n] for n in order]

wb.active = 0

wb.save(DST)
print(f"Saved: {DST}")
print("Final segment distribution after normalization:")
seg_count = Counter(r[2] for r in cleaned)
for s, n in seg_count.most_common():
    print(f"  {s}: {n}")
