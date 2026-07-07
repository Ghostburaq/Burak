#!/usr/bin/env python3
"""Baut die MiT-Gesamtmappe (alle Reiter, Formeln, Verknüpfungen, Formate).

Ergebnis: MiT_GESAMTMAPPE_2026.xlsx  (VBA wird separat injiziert -> .xlsm)
Konventionen (wichtig, VBA verlässt sich darauf):
  - Alle Listen-Tabs: Zeile 1 = Titel, Zeile 2 = Navigation, Zeile 4 = Header, Daten ab Zeile 5
  - Header, die mit '_' beginnen, sind Hilfsspalten (Import ignoriert sie)
"""
import os, pickle, re, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import (FormulaRule, DataBarRule, IconSetRule, ColorScaleRule)
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList

D = pickle.load(open("extracted.pkl", "rb"))
OHNE_MAKROS = os.environ.get("OHNE_MAKROS") == "1"
OUT_FILE = "MiT_GESAMTMAPPE_2026_OHNE_MAKROS.xlsx" if OHNE_MAKROS else "MiT_GESAMTMAPPE_2026.xlsx"
HEUTE = "04.07.2026"

# ----------------------------------------------------------------------------
# Farbwelt
# ----------------------------------------------------------------------------
C_NAV   = "262626"   # Start/Dashboard
C_VERT  = "1F4E79"   # Vertrieb (blau)
C_DC    = "206A5D"   # Datacenter CH (petrol)
C_GLOB  = "5B2C6F"   # Global (violett)
C_PROD  = "C55A11"   # Produkte (orange)
C_TOOL  = "7F6000"   # Werkzeuge (oliv)
C_SYS   = "808080"   # System (grau)
ZEBRA   = {C_VERT: "EEF3F9", C_DC: "EAF4F1", C_GLOB: "F3EDF7", C_PROD: "FCF0E4",
           C_TOOL: "F6F3E4", C_SYS: "F2F2F2", C_NAV: "F2F2F2"}

THIN = Side(style="thin", color="BFBFBF")
B_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# In-Zellen-Datenbalken je Bereichsfarbe
BAR = {C_VERT: "9DC3E6", C_DC: "8FD0C2", C_GLOB: "CBA6DE", C_PROD: "F4B183",
       C_TOOL: "DED08A", C_SYS: "C9C9C9", C_NAV: "C9C9C9"}
VALUE_KEYS = ("Volumen CHF", "Wert CHF", "CHF-Potential", "IT-MW", "Total-MW",
              "Marktvolumen", "MiT-Zielumsatz", "Gew.Wert", "Gew. Forecast",
              "Report Value", "Projektwert", "Tagespreis", "Wochenpreis",
              "Monatspreis", "Weekly Median", "Invest. CHF")

def deko_liste(ws, spalten, maxrow, farbe):
    """Datenbalken auf Wertspalten, Ampel-Icons auf Wahrscheinlichkeit, Farbskala auf Marge."""
    bar = BAR.get(farbe, "BFBFBF")
    for i, sp in enumerate(spalten, start=1):
        h = sp["h"]
        if h is None or h.startswith("_"):
            continue
        col = get_column_letter(i)
        rng = f"{col}5:{col}{maxrow}"
        try:
            if h in ("Wahr. %", "Wahrsch. %"):
                ws.conditional_formatting.add(rng, IconSetRule(
                    "3TrafficLights1", "percent", [0, 34, 67], showValue=True))
            elif h == "Marge %":
                ws.conditional_formatting.add(rng, ColorScaleRule(
                    start_type="num", start_value=0, start_color="F8696B",
                    mid_type="num", mid_value=0.15, mid_color="FFEB84",
                    end_type="num", end_value=0.35, end_color="63BE7B"))
            elif h == "kW" or any(k in h for k in VALUE_KEYS):
                ws.conditional_formatting.add(rng, DataBarRule(
                    start_type="min", end_type="max", color=bar))
        except Exception:
            pass

def setup_print(ws, titles="1:4", landscape=True):
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.page_margins.left = ws.page_margins.right = 0.3
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    if titles:
        ws.print_title_rows = titles

ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

def sv(v):
    """Sanitize value."""
    if isinstance(v, str):
        v = ILLEGAL.sub("", v)
    return v

def put(ws, row, col, value, font=None, fill=None, align=None, fmt=None, border=None):
    c = ws.cell(row=row, column=col)
    value = sv(value)
    c.value = value
    if isinstance(value, str) and value.startswith("="):
        pass  # bewusst als Formel
    if font: c.font = font
    if fill:
        c.fill = fill if isinstance(fill, PatternFill) else PatternFill("solid", fgColor=fill)
    if align: c.alignment = align
    if fmt: c.number_format = fmt
    if border: c.border = border
    return c

def put_text(ws, row, col, value, **kw):
    """Wie put, aber erzwingt Text (auch wenn der String mit '=' beginnt)."""
    c = put(ws, row, col, value, **kw)
    if isinstance(c.value, str) and c.value.startswith("="):
        c.data_type = "s"
    return c

# ---- DARK EXECUTIVE COCKPIT ----
FONT = "Segoe UI"          # moderne Windows-Systemschrift
C_DARK = "1A1A1A"          # Titelband (fast schwarz)
C_DARK2 = "2B2B2B"         # zweite dunkle Fläche
C_INK  = "0F0F0F"

def shade(hexcol, f):
    """Helligkeit skalieren (f<1 dunkler, f>1 heller)."""
    r = min(255, int(int(hexcol[0:2], 16) * f))
    g = min(255, int(int(hexcol[2:4], 16) * f))
    b = min(255, int(int(hexcol[4:6], 16) * f))
    return f"{r:02X}{g:02X}{b:02X}"

F_TITLE  = Font(name=FONT, size=17, bold=True, color="FFFFFF")
F_SUB    = Font(name=FONT, size=9, italic=True, color="BFBFBF")
F_HDR    = Font(name=FONT, size=10, bold=True, color="FFFFFF")
F_LINK   = Font(name=FONT, size=10, bold=True, color="4EA1FF", underline="single")
F_KPI_L  = Font(name=FONT, size=9, bold=True, color="D9D9D9")
F_KPI_V  = Font(name=FONT, size=18, bold=True, color="FFFFFF")
F_SECT   = Font(name=FONT, size=11, bold=True, color="FFFFFF")
F_DATA   = Font(name=FONT, size=10, color="222222")
A_CENTER = Alignment(horizontal="center", vertical="center")
A_LEFT   = Alignment(horizontal="left", vertical="center")
A_WRAP   = Alignment(horizontal="left", vertical="top", wrap_text=True)

def titel_zeilen(ws, farbe, titel, untertitel, breite):
    """Dunkles Executive-Titelband + heller Akzent + Marken-Akzentblock links."""
    breite = max(breite, 2)
    ws.merge_cells(start_row=1, start_column=2, end_row=1, end_column=breite)
    # ganze Zeile dunkel
    for col in range(1, breite + 1):
        ws.cell(row=1, column=col).fill = PatternFill("solid", fgColor=C_DARK)
    # Akzentblock in Spalte 1 (Bereichsfarbe)
    put(ws, 1, 1, "", fill=farbe)
    put(ws, 1, 2, titel, font=F_TITLE, fill=C_DARK, align=A_LEFT)
    ws.row_dimensions[1].height = 34
    # Navi-Zeile (dunkel)
    for col in range(1, breite + 1):
        ws.cell(row=2, column=col).fill = PatternFill("solid", fgColor=C_DARK2)
    put(ws, 2, 1, "=HYPERLINK(\"#'00_START'!A1\",\"◄ START\")", font=F_LINK, align=A_CENTER)
    if untertitel:
        ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=breite)
        put(ws, 2, 2, untertitel, font=Font(name=FONT, size=9, italic=True, color="BFBFBF"),
            fill=C_DARK2, align=A_LEFT)
    ws.row_dimensions[2].height = 17
    # heller Akzentbalken (Bereichsfarbe) unter dem Band
    for col in range(1, breite + 1):
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=farbe)
    ws.row_dimensions[3].height = 5

def liste_bauen(wb, name, farbe, titel, untertitel, spalten, zeilen, maxrow,
                freeze="A5", filter_on=True):
    """Generischer Listen-Tab.
    spalten: Liste von Dicts: {h: Header, w: Breite, fmt: Zahlenformat, f: Formel-Template
             (mit {r}), hidden: bool}
    zeilen: Liste von Dicts Header->Wert (Werte; Formelspalten werden ignoriert)
    """
    ws = wb.create_sheet(name)
    ws.sheet_properties.tabColor = farbe
    n = len(spalten)
    titel_zeilen(ws, farbe, titel, untertitel, n)
    # Header (Zeile 4)
    for i, sp in enumerate(spalten, start=1):
        c = put(ws, 4, i, sp["h"], font=F_HDR, fill=farbe, border=B_ALL,
                align=Alignment(horizontal="center", vertical="center", wrap_text=True))
        ws.column_dimensions[get_column_letter(i)].width = sp.get("w", 14)
        if sp.get("hidden"):
            ws.column_dimensions[get_column_letter(i)].hidden = True
    ws.row_dimensions[4].height = 28
    # Daten
    data_end = 4 + max(len(zeilen), 1)
    for r_i, zeile in enumerate(zeilen, start=5):
        for c_i, sp in enumerate(spalten, start=1):
            if "f" in sp:
                continue
            v = zeile.get(sp["h"])
            put_text(ws, r_i, c_i, v, fmt=sp.get("fmt", "General"), border=B_ALL)
    # Formel-Spalten: bis data_end + 200 vorbefüllen
    fill_end = data_end + 200
    for c_i, sp in enumerate(spalten, start=1):
        if "f" not in sp:
            continue
        for r in range(5, fill_end + 1):
            put(ws, r, c_i, sp["f"].format(r=r), fmt=sp.get("fmt", "General"), border=B_ALL)
    # Rahmen/Format für Puffer-Zeilen (ohne Formeln)
    for r in range(5 + len(zeilen), fill_end + 1):
        for c_i, sp in enumerate(spalten, start=1):
            if "f" in sp:
                continue
            cc = ws.cell(row=r, column=c_i)
            cc.border = B_ALL
            if sp.get("fmt"):
                cc.number_format = sp["fmt"]
    ws.freeze_panes = freeze
    if filter_on:
        ws.auto_filter.ref = f"A4:{get_column_letter(n)}{maxrow}"
    # Zebra
    zf = ZEBRA.get(farbe, "F2F2F2")
    anker_col = "$B" if n > 1 else "$A"
    ws.conditional_formatting.add(
        f"A5:{get_column_letter(n)}{maxrow}",
        FormulaRule(formula=[f"AND({anker_col}5<>\"\",MOD(ROW(),2)=0)"],
                    fill=PatternFill("solid", fgColor=zf), stopIfTrue=False))
    # kräftige Trennlinie unter der Kopfzeile
    for i in range(1, n + 1):
        cc = ws.cell(row=4, column=i)
        cc.border = Border(left=THIN, right=THIN, top=THIN,
                           bottom=Side(style="medium", color="FFFFFF"))
    # In-Zellen-Grafik + Druck-Layout + saubere Optik
    deko_liste(ws, spalten, maxrow, farbe)
    ws.sheet_view.showGridLines = False
    setup_print(ws)
    ws.sheet_view.zoomScale = 100
    return ws

def block_sheet(wb, name, farbe, titel, untertitel, bloecke, widths=None):
    """Statischer Wissens-Tab aus Roh-Blöcken (Liste von (Überschrift, block-rows))."""
    ws = wb.create_sheet(name)
    ws.sheet_properties.tabColor = farbe
    breite = max((len(b[1][0]) if b[1] else 1) for b in bloecke)
    breite = max(breite, 6)
    titel_zeilen(ws, farbe, titel, untertitel, breite)
    r = 4
    for ueber, block in bloecke:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=breite)
        put(ws, r, 1, ueber, font=F_SECT, fill=farbe)
        r += 1
        for zeile in block:
            for c_i, v in enumerate(zeile, start=1):
                if v is not None:
                    put_text(ws, r, c_i, v, align=A_WRAP)
            r += 1
        r += 1
    if widths:
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
    else:
        for i in range(1, breite + 1):
            ws.column_dimensions[get_column_letter(i)].width = 22
    return ws

def canon(rows, alias):
    """Kanonisiert Dict-Keys gemäß Alias-Map."""
    out = []
    for d in rows:
        nd = {}
        for k, v in d.items():
            if k is None:
                continue
            nd[alias.get(k, k)] = v
        out.append(nd)
    return out

def pct_fraction(v):
    """'85%' / 85 / 0.85 -> 0.85"""
    if v is None:
        return None
    if isinstance(v, str):
        s = v.replace("%", "").replace(",", ".").strip()
        try:
            v = float(s)
        except ValueError:
            return None
    if isinstance(v, (int, float)):
        return v / 100.0 if v > 1 else float(v)
    return None

wb = openpyxl.Workbook()
wb.remove(wb.active)
# Standard-Schrift der ganzen Mappe modernisieren
try:
    _normal = wb._named_styles["Normal"]
    _normal.font = Font(name=FONT, size=10, color="222222")
except Exception:
    pass

MAXR = {"pipe": 2000, "crm": 3000, "kartei": 5000, "betr": 300, "bau": 300,
        "stand": 300, "dck": 500, "gp": 20000, "gk": 15000, "kat": 2000,
        "pchf": 300, "pintl": 500, "norm": 100, "akq": 500}

NF = "#,##0"          # Zahl
NFD = "#,##0.00"
PCT = "0%"

# ============================================================================
# 02_PIPELINE
# ============================================================================
alias_pipe = {"Kanton": "Kt.", "Equipment CHF": "Equip. CHF", "Treibstoff CHF": "Treibst. CHF",
              "Techniker CHF": "Technik. CHF", "Gew. Wert CHF": "Gew.Wert CHF",
              "Wahrsch. %": "Wahr. %", "Akquis. Typ": "Akquise Typ",
              "USP-Argument (Unique Selling Proposition)": "USP-Argument",
              "Dauer": "Dauer (Tage)"}
pipe_rows = canon(D["pipeline"]["rows"], alias_pipe)
for d in pipe_rows:
    d["Wahr. %"] = pct_fraction(d.get("Wahr. %"))

P = MAXR["pipe"]
sp_pipe = [
    {"h": "Nr.", "w": 5, "f": '=IF($B{r}="","",ROW()-4)'},
    {"h": "Kunde / Unternehmen", "w": 30},
    {"h": "Kt.", "w": 6},
    {"h": "Segment", "w": 21},
    {"h": "Leistung / Fleet", "w": 22},
    {"h": "kW", "w": 8, "fmt": NF},
    {"h": "Dauer (Tage)", "w": 8},
    {"h": "Start", "w": 11},
    {"h": "Volumen CHF", "w": 12, "fmt": NF},
    {"h": "Equip. CHF", "w": 11, "fmt": NF},
    {"h": "Transport CHF", "w": 11, "fmt": NF},
    {"h": "Treibst. CHF", "w": 11, "fmt": NF},
    {"h": "Technik. CHF", "w": 11, "fmt": NF},
    {"h": "Übrige CHF", "w": 11, "fmt": NF},
    {"h": "Marge CHF", "w": 11, "fmt": NF,
     "f": '=IF($B{r}="","",IF(ISNUMBER($I{r}),$I{r}-SUM($J{r}:$N{r}),""))'},
    {"h": "Marge %", "w": 8, "fmt": PCT,
     "f": '=IF(OR($B{r}="",NOT(ISNUMBER($I{r})),$I{r}=0),"",$O{r}/$I{r})'},
    {"h": "Gew.Wert CHF", "w": 12, "fmt": NF,
     "f": '=IF(OR($B{r}="",NOT(ISNUMBER($I{r}))),"",IF($R{r}="WON",$I{r},$I{r}*IF(ISNUMBER($S{r}),$S{r},0)))'},
    {"h": "Status", "w": 12},
    {"h": "Wahr. %", "w": 8, "fmt": PCT},
    {"h": "Akquise Typ", "w": 14},
    {"h": "USP-Argument", "w": 32},
    {"h": "Nächster Schritt", "w": 34},
    {"h": "Follow-Up", "w": 11},
    {"h": "Notiz intern", "w": 32},
    {"h": "_Rang", "w": 6, "hidden": True,
     "f": '=IF($B{r}="","",IF(ISNUMBER($I{r}),$I{r},0)+ROW()/10000000)'},
    # Rang-Spalten je Kategorie (Volumen + eindeutiger Tiebreak) -> LARGE-fähig in Excel UND LibreOffice
    {"h": "_WON", "w": 6, "hidden": True,
     "f": '=IF(AND($B{r}<>"",$R{r}="WON",ISNUMBER($I{r})),$I{r}+ROW()/100000000,"")'},
    {"h": "_OFF", "w": 6, "hidden": True,
     "f": '=IF(AND($B{r}<>"",OR($R{r}="offered",$R{r}="to be offered"),ISNUMBER($I{r})),$I{r}+ROW()/100000000,"")'},
    {"h": "_OPP", "w": 6, "hidden": True,
     "f": '=IF(AND($B{r}<>"",OR($R{r}="follow-up",$R{r}="In evaluation",$R{r}="tbd",$R{r}="on hold"),ISNUMBER($I{r})),$I{r}+ROW()/100000000,"")'},
    {"h": "_LOSTX", "w": 6, "hidden": True,
     "f": '=IF(AND($B{r}<>"",OR($R{r}="LOST",$R{r}="Declined"),ISNUMBER($I{r})),$I{r}+ROW()/100000000,"")'},
    {"h": "_ACT", "w": 6, "hidden": True,
     "f": '=IF(AND($B{r}<>"",$R{r}<>"WON",$R{r}<>"LOST",$R{r}<>"Declined",$R{r}<>"",ISNUMBER($I{r})),$I{r}+ROW()/100000000,"")'},
]
ws = liste_bauen(wb, "02_PIPELINE", C_VERT, "PIPELINE — MiT Strom Schweiz (Master)",
                 f"Alle Deals zentral. Neue Deals hier erfassen oder per Import (Ctrl+Shift+I). Stand: {HEUTE}",
                 sp_pipe, pipe_rows, P)
# Status-Farben
cf_map = [("WON", "C6EFCE", "006100"), ("LOST", "FFC7CE", "9C0006"), ("Declined", "FFC7CE", "9C0006"),
          ("offered", "FFEB9C", "9C6500"), ("to be offered", "FFEB9C", "9C6500"),
          ("follow-up", "DDEBF7", "1F4E79"), ("In evaluation", "DDEBF7", "1F4E79"),
          ("on hold", "EDEDED", "595959"), ("tbd", "EDEDED", "595959")]
for status, fill, fontc in cf_map:
    ws.conditional_formatting.add(
        f"R5:R{P}",
        FormulaRule(formula=[f'EXACT($R5,"{status}")'],
                    fill=PatternFill("solid", fgColor=fill), font=Font(color=fontc, bold=True)))

dv_status = DataValidation(type="list", formula1="='91_LISTEN'!$A$5:$A$13", allow_blank=True,
                           showErrorMessage=False)
ws.add_data_validation(dv_status); dv_status.add(f"R5:R{P}")
dv_seg = DataValidation(type="list", formula1="='91_LISTEN'!$B$5:$B$40", allow_blank=True,
                        showErrorMessage=False)
ws.add_data_validation(dv_seg); dv_seg.add(f"D5:D{P}")
dv_kt = DataValidation(type="list", formula1="='91_LISTEN'!$C$5:$C$33", allow_blank=True,
                       showErrorMessage=False)
ws.add_data_validation(dv_kt); dv_kt.add(f"C5:C{P}")
dv_akq = DataValidation(type="list", formula1="='91_LISTEN'!$D$5:$D$12", allow_blank=True,
                        showErrorMessage=False)
ws.add_data_validation(dv_akq); dv_akq.add(f"T5:T{P}")

# ============================================================================
# 03_KUNDEN_CRM
# ============================================================================
alias_crm = {"Firmenname *": "Firmenname"}
crm_rows = canon(D["crm"]["rows"], alias_crm)
for d in crm_rows:
    d["Wahrsch. %"] = pct_fraction(d.get("Wahrsch. %"))

K = MAXR["crm"]
sp_crm = [
    {"h": "Nr.", "w": 5, "f": '=IF($D{r}="","",ROW()-4)'},
    {"h": "Prio", "w": 6},
    {"h": "Segment", "w": 22},
    {"h": "Firmenname", "w": 32},
    {"h": "Ort", "w": 16},
    {"h": "PLZ", "w": 7},
    {"h": "Kanton", "w": 8},
    {"h": "Ansprechpartner", "w": 22},
    {"h": "Funktion / Titel", "w": 18},
    {"h": "E-Mail", "w": 24},
    {"h": "Telefon", "w": 17},
    {"h": "Website", "w": 18},
    {"h": "Status", "w": 13},
    {"h": "Nächster Schritt", "w": 34},
    {"h": "Bedarf / kVA", "w": 28},
    {"h": "Hauptprodukt", "w": 16},
    {"h": "Follow-up Datum", "w": 13, "fmt": "DD.MM.YYYY"},
    {"h": "Notizen", "w": 34},
    {"h": "Internes", "w": 20},
    {"h": "Wahrsch. %", "w": 9, "fmt": PCT},
    {"h": "Wert CHF", "w": 12, "fmt": NF},
    {"h": "Letzte Aktivität", "w": 13, "fmt": "DD.MM.YYYY"},
    {"h": "Gew. Forecast CHF", "w": 13, "fmt": NF,
     "f": '=IF(OR($D{r}="",$U{r}=""),"",$U{r}*IF($T{r}="",0,$T{r}))'},
]
ws = liste_bauen(wb, "03_KUNDEN_CRM", C_VERT, "KUNDEN-CRM — Zielkunden-Datenbank Schweiz",
                 "Akquise-Datenbank (798 Firmen). Pflege Status/Wert/Wahrsch. -> Forecast rechnet live.",
                 sp_crm, crm_rows, K, freeze="E5")
ws.conditional_formatting.add(f"B5:B{K}", FormulaRule(
    formula=['EXACT($B5,"A")'], fill=PatternFill("solid", fgColor="F8CBAD"),
    font=Font(bold=True, color="833C00")))
dv = DataValidation(type="list", formula1='"A,B,C"', allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"B5:B{K}")
dv = DataValidation(type="list", formula1="='91_LISTEN'!$E$5:$E$20", allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"C5:C{K}")
dv = DataValidation(type="list", formula1="='91_LISTEN'!$F$5:$F$14", allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"M5:M{K}")
dv = DataValidation(type="list", formula1="='91_LISTEN'!$G$5:$G$16", allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"P5:P{K}")

# ============================================================================
# 04_KUNDENKARTEI
# ============================================================================
alias_kartei = {"Kt.": "Kanton", "Telefon": "Tel. Nr", "Status": "Pipeline Status"}
kartei_rows = canon(D["kartei"]["rows"], alias_kartei)
KA = MAXR["kartei"]
sp_kartei = [
    {"h": "Nr.", "w": 5, "f": '=IF($B{r}="","",ROW()-4)'},
    {"h": "Kunde / Unternehmen", "w": 34},
    {"h": "Segment", "w": 22},
    {"h": "Kanton", "w": 8},
    {"h": "Verantwortlicher", "w": 15},
    {"h": "Ansprechperson", "w": 22},
    {"h": "Tel. Nr", "w": 19},
    {"h": "MiT Strom", "w": 9,
     "f": '=IF($B{r}="","",IF(COUNTIF(\'02_PIPELINE\'!$B$5:$B$2000,$B{r})>0,"✓",""))'},
    {"h": "Pipeline Status", "w": 13,
     "f": '=IF($B{r}="","",IFERROR(INDEX(\'02_PIPELINE\'!$R$5:$R$2000,MATCH($B{r},\'02_PIPELINE\'!$B$5:$B$2000,0)),""))'},
    {"h": "E-Mail", "w": 30},
]
ws = liste_bauen(wb, "04_KUNDENKARTEI", C_VERT, "KUNDENKARTEI — CH Customer Overview & Kontakte",
                 "Alle CH-Kunden/Kontakte. ✓ + Status kommen automatisch aus 02_PIPELINE.",
                 sp_kartei, kartei_rows, KA, freeze="C5")
ws.conditional_formatting.add(f"H5:H{KA}", FormulaRule(
    formula=['EXACT($H5,"✓")'], fill=PatternFill("solid", fgColor="C6EFCE"),
    font=Font(bold=True, color="006100")))

# ============================================================================
# 10_DC_BETREIBER
# ============================================================================
alias_betr = {"Code CH": "Standort-Code CH", "Kt": "Kanton", "Prio": "Priorität MiT",
              "Prioritaet MiT": "Priorität MiT", "Vorgaenger": "Vorgänger",
              "Eigentuemer": "Eigentümer", "Kuehlung": "Kühlung"}
betr_rows = canon(D["betreiber"]["rows"], alias_betr)
BT = MAXR["betr"]
sp_betr = [
    {"h": "Betreiber", "w": 24},
    {"h": "Vorgänger", "w": 14},
    {"h": "Typ", "w": 18},
    {"h": "Eigentümer", "w": 26},
    {"h": "Standort-Code CH", "w": 15},
    {"h": "Adressen CH", "w": 34},
    {"h": "Kanton", "w": 8},
    {"h": "IT-MW", "w": 8, "fmt": NF},
    {"h": "Total-MW", "w": 9, "fmt": NF},
    {"h": "Status 2026", "w": 18},
    {"h": "Ausbau 2026-28", "w": 30},
    {"h": "Notstrom-Typ", "w": 30},
    {"h": "Kühlung", "w": 24},
    {"h": "HVO?", "w": 7},
    {"h": "PQ Kl.A?", "w": 8},
    {"h": "Ansprechpartner CH", "w": 22},
    {"h": "Kontakt", "w": 26},
    {"h": "Priorität MiT", "w": 10},
    {"h": "Bemerkung", "w": 40},
    {"h": "Quelle", "w": 20},
]
ws = liste_bauen(wb, "10_DC_BETREIBER", C_DC, "DC-BETREIBER SCHWEIZ — Master-Daten",
                 "Alle Rechenzentrums-Betreiber CH, verifiziert Mai 2026 (30 Einträge).",
                 sp_betr, betr_rows, BT, freeze="B5")
ws.conditional_formatting.add(f"R5:R{BT}", FormulaRule(
    formula=['LEFT($R5,1)="A"'], fill=PatternFill("solid", fgColor="F8CBAD"),
    font=Font(bold=True, color="833C00")))

# ============================================================================
# 11_DC_BAUPROJEKTE  (Hand-Merge aus 3 Quellen)
# ============================================================================
bg = D["bau_gesamt"]["rows"]
bz = [r for r in D["bau_zsf"]["rows"] if r.get("Projekt / Ort")]
bs = D["bau_suite"]["rows"]

bau = []
for i, g in enumerate(bg):
    z = bz[i] if i < len(bz) else {}
    bau.append({
        "Status MiT": g.get("Status MiT"),
        "Abgeschlossen": z.get("Projekt Abgeschlossen JA / NEIN"),
        "Verantwortlich MiT": z.get("Verantwortlich bei MiT AG"),
        "Projekt / Ort": g.get("Projekt / Ort"),
        "Kanton": g.get("Kanton"),
        "Adresse": g.get("Adresse"),
        "Bauherr / Inhaber": g.get("Bauherr / Inhaber"),
        "GU / TU": g.get("GU / TU"),
        "Architektur": g.get("Architektur"),
        "Gebäudetechnik": g.get("Gebaeudetechnik") or z.get("Gebäudetechnik"),
        "Spezialplaner": g.get("Spezialplaner") or z.get("Spezialplaner-> Cooling / Power / Security"),
        "Betreiber": z.get("Betreiber-> Microsoft….."),
        "Typ (Neubau/Ausbau)": g.get("Typ") or z.get("Neubau/Ausbau/Upgrade"),
        "Bedarf": g.get("Bedarf") or z.get("Bedarf-> Wärme / Kälte / Strom / Entfeuchtung"),
        "Baustart": g.get("Geplanter Baustart") or z.get("Geplanter Baustart / Erfolgter Baustart"),
        "IBN geplant": g.get("IBN geplant") or z.get("Inbetriebnahe geplant auf…"),
        "Invest. CHF": g.get("Invest. CHF"),
        "IT-MW": g.get("IT-MW (est.)"),
        "MiT-Produkte": g.get("MiT Produkte"),
        "CHF-Potential MiT": None,
        "Kontakt": g.get("Kontakt MiT"),
        "Prio": g.get("Prio"),
        "Nächste Aktion": None,
        "Anmerkung / Hinweise": " | ".join(x for x in [g.get("Anmerkung"), z.get("Hinweise")] if x),
    })

# Suite-Zeilen: Index-Mapping auf bau[] (None = neue Zeile)
suite_map = [3, 6, None, None, 9, 8, 1, 0, None]  # Reihenfolge wie bs
for j, s in enumerate(bs):
    extra = " | ".join(f"{k}: {s[k]}" for k in
                       ["MiT-Phase", "Gen.-Bedarf", "Lastbank-Test", "BESS-Potential", "Trafo-Bedarf"]
                       if s.get(k))
    tgt = suite_map[j] if j < len(suite_map) else None
    if tgt is not None:
        b = bau[tgt]
        b["CHF-Potential MiT"] = s.get("CHF-Potential MiT")
        b["Nächste Aktion"] = s.get("Naechste Aktion")
        if not b.get("MiT-Produkte"):
            b["MiT-Produkte"] = s.get("MiT-Produkte komplett")
        if extra:
            b["Anmerkung / Hinweise"] = ((b.get("Anmerkung / Hinweise") or "") + " | " + extra).strip(" |")
    else:
        bau.append({
            "Status MiT": "OFFEN",
            "Projekt / Ort": s.get("Projekt / Betreiber"),
            "Kanton": s.get("Kt"),
            "Adresse": s.get("Adresse"),
            "Baustart": s.get("Baustart"),
            "IBN geplant": s.get("Inbetrieb."),
            "Invest. CHF": s.get("Invest. CHF"),
            "IT-MW": s.get("IT-MW"),
            "MiT-Produkte": s.get("MiT-Produkte komplett"),
            "CHF-Potential MiT": s.get("CHF-Potential MiT"),
            "Kontakt": s.get("Kontakt"),
            "Prio": s.get("Prio"),
            "Nächste Aktion": s.get("Naechste Aktion"),
            "Anmerkung / Hinweise": extra or None,
        })

BA = MAXR["bau"]
sp_bau = [
    {"h": "Nr.", "w": 5, "f": '=IF($E{r}="","",ROW()-4)'},
    {"h": "Status MiT", "w": 12},
    {"h": "Abgeschlossen", "w": 12},
    {"h": "Verantwortlich MiT", "w": 16},
    {"h": "Projekt / Ort", "w": 40},
    {"h": "Kanton", "w": 7},
    {"h": "Adresse", "w": 30},
    {"h": "Bauherr / Inhaber", "w": 30},
    {"h": "GU / TU", "w": 26},
    {"h": "Architektur", "w": 22},
    {"h": "Gebäudetechnik", "w": 24},
    {"h": "Spezialplaner", "w": 24},
    {"h": "Betreiber", "w": 18},
    {"h": "Typ (Neubau/Ausbau)", "w": 16},
    {"h": "Bedarf", "w": 26},
    {"h": "Baustart", "w": 18},
    {"h": "IBN geplant", "w": 18},
    {"h": "Invest. CHF", "w": 16},
    {"h": "IT-MW", "w": 10},
    {"h": "MiT-Produkte", "w": 34},
    {"h": "CHF-Potential MiT", "w": 13, "fmt": NF},
    {"h": "Kontakt", "w": 28},
    {"h": "Prio", "w": 7},
    {"h": "Nächste Aktion", "w": 34},
    {"h": "Anmerkung / Hinweise", "w": 44},
]
ws = liste_bauen(wb, "11_DC_BAUPROJEKTE", C_DC, "DC-BAUPROJEKTE SCHWEIZ 2026-2028",
                 "Konsolidiert aus 3 Quellen (Gesamtmappe, Zusammenfassung, DC-Suite). Status pflegen!",
                 sp_bau, bau, BA, freeze="F5")
dv = DataValidation(type="list", formula1='"OFFEN,IN KONTAKT,OFFERIERT,WON,LOST,ABGESCHLOSSEN"',
                    allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"B5:B{BA}")
dv = DataValidation(type="list", formula1='"JA,NEIN"', allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"C5:C{BA}")
ws.conditional_formatting.add(f"W5:W{BA}", FormulaRule(
    formula=['LEFT($W5,1)="A"'], fill=PatternFill("solid", fgColor="F8CBAD"),
    font=Font(bold=True, color="833C00")))

# ============================================================================
# 12_DC_STANDORTE
# ============================================================================
alias_st = {"Standortname": "Standortname / Projekt", "Strasse + Nr.": "Strasse",
            "Kanton": "Kt", "Eroeffn.": "Status", "GPS (approx.)": "GPS",
            "Entfernung Thayngen": "Entf. Thayngen", "Besonderheit": "Besonderheit / GU"}
st_rows = canon(D["standorte"]["rows"], alias_st)
ST = MAXR["stand"]
sp_st = [
    {"h": "Code", "w": 10},
    {"h": "Betreiber", "w": 22},
    {"h": "Standortname / Projekt", "w": 34},
    {"h": "Strasse", "w": 24},
    {"h": "PLZ", "w": 7},
    {"h": "Ort", "w": 18},
    {"h": "Kt", "w": 5},
    {"h": "IT-MW", "w": 8},
    {"h": "Status", "w": 20},
    {"h": "Tier", "w": 10},
    {"h": "Entf. Thayngen", "w": 12},
    {"h": "GPS", "w": 16},
    {"h": "Prio", "w": 7},
    {"h": "Besonderheit / GU", "w": 44},
]
ws = liste_bauen(wb, "12_DC_STANDORTE", C_DC, "DC-STANDORTE / ADRESSBUCH SCHWEIZ",
                 "Alle DC-Standorte inkl. Bauprojekte, Entfernung ab Thayngen.",
                 sp_st, st_rows, ST, freeze="D5")
ws.conditional_formatting.add(f"M5:M{ST}", FormulaRule(
    formula=['LEFT($M5,1)="A"'], fill=PatternFill("solid", fgColor="F8CBAD"),
    font=Font(bold=True, color="833C00")))

# ============================================================================
# 13_DC_KONTAKTE
# ============================================================================
alias_dck = {"E-Mail/Website": "E-Mail / Tel.", "Kontext": "Kontext / Besonderheit"}
dck_rows = canon(D["dc_kontakte"]["rows"], alias_dck)
DK = MAXR["dck"]
sp_dck = [
    {"h": "Unternehmen", "w": 26},
    {"h": "Name", "w": 20},
    {"h": "Funktion", "w": 28},
    {"h": "Segment", "w": 22},
    {"h": "E-Mail / Tel.", "w": 34},
    {"h": "LinkedIn", "w": 28},
    {"h": "Prio", "w": 7},
    {"h": "Status", "w": 17},
    {"h": "Letzter Kontakt", "w": 13},
    {"h": "Produkt-Fokus", "w": 32},
    {"h": "Nächste Aktion", "w": 40},
    {"h": "Kontext / Besonderheit", "w": 44},
]
ws = liste_bauen(wb, "13_DC_KONTAKTE", C_DC, "DC-KONTAKTE CRM — Ansprechpartner Schweiz",
                 "Entscheider bei Betreibern, GUs und Bauprojekten. Status/Nächste Aktion pflegen.",
                 sp_dck, dck_rows, DK, freeze="C5")
dv = DataValidation(type="list",
                    formula1='"Noch kein Kontakt,Kontaktiert,In Gespräch,Termin,Offeriert,Kunde,Kein Bedarf"',
                    allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"H5:H{DK}")
ws.conditional_formatting.add(f"G5:G{DK}", FormulaRule(
    formula=['LEFT($G5,1)="A"'], fill=PatternFill("solid", fgColor="F8CBAD"),
    font=Font(bold=True, color="833C00")))

# ============================================================================
# 15_GLOBAL_PROJEKTE
# ============================================================================
gph = D["global_projekte"]["header"]
gp_rows = [dict(zip(gph, r)) for r in D["global_projekte"]["rows"]]
GP = MAXR["gp"]
sp_gp = [
    {"h": "ID", "w": 12},
    {"h": "Quelle", "w": 11},
    {"h": "Projektname", "w": 44},
    {"h": "Projektwert ($)", "w": 15, "fmt": NF},
    {"h": "Report Value ($)", "w": 15, "fmt": NF},
    {"h": "Sektor", "w": 26},
    {"h": "Phase", "w": 20},
    {"h": "Status", "w": 18},
    {"h": "Land", "w": 16},
    {"h": "Region/Staat", "w": 16},
    {"h": "Aggreko Region", "w": 13},
    {"h": "Baustart-Jahr", "w": 11},
    {"h": "Inbetriebnahme-Jahr", "w": 11},
    {"h": "Zeit-Banding", "w": 16},
    {"h": "Hauptfirma", "w": 30},
    {"h": "Lat", "w": 10, "fmt": "0.0000"},
    {"h": "Lon", "w": 10, "fmt": "0.0000"},
    {"h": "Projektbeschreibung", "w": 60},
]
ws = liste_bauen(wb, "15_GLOBAL_PROJEKTE", C_GLOB, "GLOBALE DC-PROJEKTE — Pipeline-Datenbank",
                 "10'572 aktive Data-Centre-Projekte weltweit (IRR + Global Data, März 2026). Import: neuer Tracker per Ctrl+Shift+I.",
                 sp_gp, gp_rows, GP, freeze="D5")

# ============================================================================
# 16_GLOBAL_KONTAKTE
# ============================================================================
gkh = D["global_kontakte"]["header"]
gk_rows = [dict(zip(gkh, r)) for r in D["global_kontakte"]["rows"]]
GK = MAXR["gk"]
sp_gk = [
    {"h": "Projekt-ID", "w": 12},
    {"h": "Projektname", "w": 40},
    {"h": "Titel/Funktion", "w": 30},
    {"h": "Vorname", "w": 14},
    {"h": "Nachname", "w": 16},
    {"h": "Telefon", "w": 17},
    {"h": "E-Mail", "w": 30},
    {"h": "LinkedIn", "w": 34},
    {"h": "Verantwortung", "w": 18},
    {"h": "Firma", "w": 28},
    {"h": "Adresse", "w": 28},
    {"h": "PLZ", "w": 9},
    {"h": "Stadt", "w": 16},
    {"h": "Region", "w": 14},
    {"h": "Land", "w": 14},
]
ws = liste_bauen(wb, "16_GLOBAL_KONTAKTE", C_GLOB, "GLOBALE PROJEKT-KONTAKTE",
                 "8'502 Ansprechpartner zu den globalen DC-Projekten (via Projekt-ID verknüpft mit 15_GLOBAL_PROJEKTE).",
                 sp_gk, gk_rows, GK, freeze="C5")

# ============================================================================
# 18_KATALOG
# ============================================================================
kah = D["katalog"]["header"]
ka_rows = [dict(zip(kah, r)) for r in D["katalog"]["rows"]]
KT = MAXR["kat"]
sp_kat = [
    {"h": "QUELLE", "w": 22},
    {"h": "ITEM CODE / MOVEX", "w": 16},
    {"h": "KATEGORIE", "w": 18},
    {"h": "UNTERKATEGORIE", "w": 20},
    {"h": "BEZEICHNUNG", "w": 40},
    {"h": "SPANNUNG", "w": 10},
    {"h": "STROM (A)", "w": 9},
    {"h": "PHASE", "w": 7},
    {"h": "LEISTUNG (kVA/kW)", "w": 11},
    {"h": "EINGANG", "w": 26},
    {"h": "AUSGANG", "w": 30},
    {"h": "BREITE (mm)", "w": 9},
    {"h": "HÖHE (mm)", "w": 9},
    {"h": "TIEFE/LÄNGE (mm)", "w": 10},
    {"h": "GEWICHT (kg)", "w": 10},
    {"h": "IP-SCHUTZ", "w": 9},
    {"h": "NORM / STANDARD", "w": 15},
    {"h": "HERSTELLER", "w": 12},
    {"h": "ANWENDUNG", "w": 18},
    {"h": "BEMERKUNGEN", "w": 40},
]
ws = liste_bauen(wb, "18_KATALOG", C_PROD, "EQUIPMENT-KATALOG — Aggreko / MiT (466 Produkte)",
                 "Komplette Produktdatenbank, 27 Kategorien. Filtern über Dropdown in Zeile 4.",
                 sp_kat, ka_rows, KT, freeze="E5")

# ============================================================================
# 19_PREISLISTE_CHF
# ============================================================================
pch = D["preis_chf"]["header"]
pc_rows = [dict(zip(pch, r)) for r in D["preis_chf"]["rows"]]
PC = MAXR["pchf"]
sp_pc = [
    {"h": "Product_Line__c", "w": 18},
    {"h": "Description__c", "w": 34},
    {"h": "Produktname", "w": 34},
    {"h": "Nächsthöheres Ersatzprodukt", "w": 30},
    {"h": "Leistung", "w": 12},
    {"h": "Tagespreis", "w": 11, "fmt": NFD},
    {"h": "Wochenpreis (7 Tage)", "w": 12, "fmt": NFD,
     "f": '=IF($F{r}="","",$F{r}*7)'},
    {"h": "Monatspreis (30 Tage)", "w": 12, "fmt": NFD,
     "f": '=IF($F{r}="","",$F{r}*30)'},
]
ws = liste_bauen(wb, "19_PREISLISTE_CHF", C_PROD, "PREISLISTE SCHWEIZ (CHF) — Power",
                 "Tagespreise CHF (Mai 2026). Wochen-/Monatspreis rechnet automatisch. Basis für 22_ANGEBOT_KALK.",
                 sp_pc, pc_rows, PC)

# ============================================================================
# 20_PREISLISTE_INTL
# ============================================================================
pih = D["preis_intl"]["header"]
pi_rows = [dict(zip(pih, r)) for r in D["preis_intl"]["rows"]]
PI = MAXR["pintl"]
sp_pi = []
for h in pih:
    e = {"h": h, "w": 16}
    if "Weekly" in h:
        e["fmt"] = NFD; e["w"] = 14
    if h in ("Description__c",):
        e["w"] = 36
    sp_pi.append(e)
ws = liste_bauen(wb, "20_PREISLISTE_INTL", C_PROD, "PREISLISTE INTERNATIONAL (vertraulich)",
                 "Aggreko Weekly Rates (Floor/Median/Premium, LC + USD) — Referenz Deutschland/Europa.",
                 sp_pi, pi_rows, PI)

# ============================================================================
# 24_NORMEN
# ============================================================================
nh = D["normen"]["header"]
n_rows = [dict(zip(nh, r)) for r in D["normen"]["rows"]]
sp_n = [
    {"h": "Norm / Standard", "w": 22},
    {"h": "Kategorie", "w": 16},
    {"h": "Was sie regelt", "w": 44},
    {"h": "Klassen", "w": 16},
    {"h": "DC-Relevanz", "w": 40},
    {"h": "MiT-Positionierung", "w": 44},
    {"h": "Pflicht/Optional", "w": 16},
    {"h": "Prüf-Frequenz", "w": 24},
]
alias_norm = {"Pflicht?": "Pflicht/Optional", "Pruef-Frequenz": "Prüf-Frequenz"}
n_rows = canon(n_rows, alias_norm)
ws = liste_bauen(wb, "24_NORMEN", C_TOOL, "NORMEN- & COMPLIANCE-MATRIX — DC Schweiz",
                 "17 relevante Standards inkl. MiT-Positionierung (IEC 61000-4-30 Kl.A = USP!).",
                 sp_n, n_rows, MAXR["norm"])

# ============================================================================
# 25_AKQUISE_90T
# ============================================================================
alias_akq = {"Ziel": "Ziel-Unternehmen", "Ziel #2": "Ziel (Ergebnis)",
             "Produkt": "MiT-Produkt", "CHF-Pot.": "CHF-Potential"}
akq_rows = canon(D["akquise"]["rows"], alias_akq)
# Suite-Variante hat 'Ziel' als Ergebnis-Spalte -> dort heißt sie schon 'Ziel'
for d in akq_rows:
    if "Ziel" in d and "Ziel (Ergebnis)" not in d:
        d["Ziel (Ergebnis)"] = d.pop("Ziel")
AQ = MAXR["akq"]
sp_akq = [
    {"h": "Woche", "w": 12},
    {"h": "Aktion", "w": 40},
    {"h": "Ziel-Unternehmen", "w": 26},
    {"h": "Kontaktperson", "w": 22},
    {"h": "Kanal", "w": 20},
    {"h": "MiT-Produkt", "w": 20},
    {"h": "Ziel (Ergebnis)", "w": 30},
    {"h": "Status", "w": 13},
    {"h": "Deadline", "w": 12},
    {"h": "CHF-Potential", "w": 12, "fmt": NF},
    {"h": "Ergebnis", "w": 36},
]
ws = liste_bauen(wb, "25_AKQUISE_90T", C_TOOL, "90-TAGE AKQUISE-PLAN — DC + Strom Schweiz",
                 "Priorisierte Aktionen (Mai-Okt 2026). Status pflegen, Ergebnisse dokumentieren.",
                 sp_akq, akq_rows, AQ)
dv = DataValidation(type="list", formula1='"OFFEN,LÄUFT,ERLEDIGT,VERSCHOBEN,HEUTE!"',
                    allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"H5:H{AQ}")
ws.conditional_formatting.add(f"H5:H{AQ}", FormulaRule(
    formula=['EXACT($H5,"ERLEDIGT")'], fill=PatternFill("solid", fgColor="C6EFCE"),
    font=Font(color="006100", bold=True)))
ws.conditional_formatting.add(f"H5:H{AQ}", FormulaRule(
    formula=['EXACT($H5,"HEUTE!")'], fill=PatternFill("solid", fgColor="FFC7CE"),
    font=Font(color="9C0006", bold=True)))

# ============================================================================
# 23_MARKTVOLUMEN
# ============================================================================
mvh = D["marktvolumen"]["header"]
mv_rows = [dict(zip(mvh, r)) for r in D["marktvolumen"]["rows"]]
for d in mv_rows:
    d["Marktanteil %"] = pct_fraction(d.get("Marktanteil %"))
MV = 60
sp_mv = [
    {"h": "Produktkategorie", "w": 30},
    {"h": "Beschreibung", "w": 44},
    {"h": "DC-Zielkunden CH", "w": 14, "fmt": NF},
    {"h": "Proj./Jahr", "w": 10, "fmt": "0.0"},
    {"h": "Durchschn. CHF/Proj.", "w": 15, "fmt": NF},
    {"h": "Marktvolumen CH/J", "w": 15, "fmt": NF,
     "f": '=IF($A{r}="","",IF(AND(ISNUMBER($D{r}),ISNUMBER($E{r})),$D{r}*$E{r},""))'},
    {"h": "Marktanteil %", "w": 11, "fmt": PCT},
    {"h": "MiT-Zielumsatz/J", "w": 15, "fmt": NF,
     "f": '=IF($A{r}="","",IF(AND(ISNUMBER($F{r}),ISNUMBER($G{r})),$F{r}*$G{r},""))'},
    {"h": "Ramp-Up", "w": 14},
]
ws = liste_bauen(wb, "23_MARKTVOLUMEN", C_TOOL, "MARKTVOLUMEN & MiT-UMSATZPOTENZIAL — DC Schweiz",
                 "Szenario-Modell: Zielkunden/Projekte/Preise anpassen -> Volumen & Zielumsatz rechnen live.",
                 sp_mv, mv_rows, MV)
r_tot = 5 + len(mv_rows) + 1
MV_DATA_LAST = 5 + len(mv_rows) - 1          # letzte Datenzeile (ohne TOTAL)
MV_TOTAL_CHF = f"'23_MARKTVOLUMEN'!$H${r_tot}"
put(ws, r_tot, 5, "TOTAL:", font=Font(bold=True), align=Alignment(horizontal="right"))
put(ws, r_tot, 6, f"=SUM(F5:F{MV_DATA_LAST})", font=Font(bold=True), fmt=NF, border=B_ALL)
put(ws, r_tot, 8, f"=SUM(H5:H{MV_DATA_LAST})", font=Font(bold=True), fmt=NF, border=B_ALL)

# ============================================================================
# 07 / 12 / 24: statische Wissens-Tabs
# ============================================================================
block_sheet(wb, "09_KUNDENANALYSE", C_VERT, "KUNDENANALYSE — Rhomberg Sersa Rail Group (RSRG)",
            "Firmenprofil + Produkt-Opportunity-Matrix (Vorlage für weitere Kundenanalysen).",
            [("FIRMENPROFIL", D["rsrg_profil"]), ("OPPORTUNITY-MATRIX (Produkt-Fit)", D["rsrg_matrix"])],
            widths=[4, 28, 34, 16, 16, 20, 24, 20, 16, 24, 16, 16, 16])

block_sheet(wb, "14_DC_DOSSIERS", C_DC, "DC-DOSSIERS — Implenia (GU-Partner) & FlexBase TZL Laufenburg",
            "Detail-Dossiers zu Schlüssel-Accounts im DC-Baugeschäft.",
            [("IMPLENIA AG — STRATEGISCHER GU-PARTNER (7 RZ Grossraum ZH)", D["implenia"]),
             ("FLEXBASE — TECHNOLOGIEZENTRUM LAUFENBURG (TZL)", D["flexbase"])],
            widths=[26, 26, 12, 26, 24, 16, 16, 16, 26, 30, 16, 26, 14, 14, 14, 14])

block_sheet(wb, "26_SYSTEME_WISSEN", C_TOOL, "SYSTEME-WISSEN — Generator + Lastbank + BESS + Trafo",
            "Technische Auslegung von Kombinationssystemen (IEC 61000-4-30, ISO 8528).",
            [("KOMBINATIONSSYSTEME — TECHNISCHES WISSEN", D["systeme"])],
            widths=[30, 24, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20])

# ============================================================================
# 91_LISTEN (Validierungsquellen + Lookups)
# ============================================================================
ws = wb.create_sheet("91_LISTEN")
ws.sheet_properties.tabColor = C_SYS
titel_zeilen(ws, C_SYS, "LISTEN & LOOKUPS — Quellen für Dropdowns",
             "Neue Werte hier ergänzen -> Dropdowns aktualisieren sich automatisch.", 12)

status_pipe = ["WON", "offered", "to be offered", "follow-up", "In evaluation",
               "on hold", "tbd", "Declined", "LOST"]
seg_union = sorted(set(D["listen"]["pipeline_segment"]) | set(D["listen"]["kartei_segment"]))
kantone = ["AG","AI","AR","BE","BL","BS","FR","GE","GL","GR","JU","LU","NE","NW","OW",
           "SG","SH","SO","SZ","TG","TI","UR","VD","VS","ZG","ZH","FL","CH","tbd"]
akq_typen = ["Kalt (Burak)", "Warm", "Warm – Aggreko", "Warm – CBM", "Inbound", "Ausschreibung", "Partner"]
crm_seg = D["listen"]["crm_segment"]
crm_status = ["offen", "kontaktiert", "Termin vereinbart", "in Gespräch", "Offerte", "WON", "LOST", "on hold", "kein Bedarf"]
crm_prod = D["listen"]["crm_produkt"] + ["Lastbank", "EV-Lader"]
gen_groessen = [30, 45, 60, 100, 125, 150, 200, 250, 300, 320, 400, 500, 650, 800, 1000, 1250]

listen_cols = [
    ("A", "Status Pipeline", status_pipe),
    ("B", "Segmente (Vertrieb)", seg_union),
    ("C", "Kantone", kantone),
    ("D", "Akquise-Typ", akq_typen),
    ("E", "Segmente CRM", crm_seg),
    ("F", "Status CRM", crm_status),
    ("G", "Hauptprodukte", crm_prod),
    ("H", "Generator-Grössen kVA", gen_groessen),
]
for col, name, vals in listen_cols:
    ci = openpyxl.utils.column_index_from_string(col)
    put(ws, 4, ci, name, font=F_HDR, fill=C_SYS, border=B_ALL)
    ws.column_dimensions[col].width = max(18, len(name) + 2)
    for i, v in enumerate(vals, start=5):
        put_text(ws, i, ci, v, border=B_ALL)
# Land -> Aggreko Region (Spalten J/K)
put(ws, 4, 10, "Land", font=F_HDR, fill=C_SYS, border=B_ALL)
put(ws, 4, 11, "Aggreko Region", font=F_HDR, fill=C_SYS, border=B_ALL)
ws.column_dimensions["J"].width = 24
ws.column_dimensions["K"].width = 16
for i, (land, reg) in enumerate(D["land_region"], start=5):
    put_text(ws, i, 10, land, border=B_ALL)
    put_text(ws, i, 11, reg, border=B_ALL)
ws.freeze_panes = "A5"

# ============================================================================
# 21_GEN_RECHNER
# ============================================================================
ws = wb.create_sheet("21_GEN_RECHNER")
ws.sheet_properties.tabColor = C_TOOL
titel_zeilen(ws, C_TOOL, "GENERATOR-AUSLEGUNG — Rechner (NIN/ISO 8528)",
             "Blaue Felder = Eingabe. Alles andere rechnet automatisch.", 8)
F_INPUT = Font(color="0563C1", bold=True)
FILL_IN = PatternFill("solid", fgColor="DDEBF7")
put(ws, 4, 1, "SCHRITT 1 — LASTLISTE (blaue Felder ausfüllen)", font=F_SECT, fill=C_TOOL)
ws.merge_cells("A4:H4")
hdr = ["Verbrauchergruppe", "kW (Nennlast)", "cos φ", "kVA", "Anlauf-Faktor", "Gleichzeitigkeit", "Eff. kVA", ""]
for i, h in enumerate(hdr, start=1):
    if h:
        put(ws, 5, i, h, font=F_HDR, fill=C_TOOL, border=B_ALL,
            align=Alignment(horizontal="center", wrap_text=True))
beispiele = [("IT-Last / Server", 100, 0.95, 1.0, 1.0), ("Kühlung / Chiller", 80, 0.85, 2.5, 0.8),
             ("Beleuchtung", 10, 0.9, 1.0, 0.9), ("Pumpen / Motoren", 30, 0.8, 3.0, 0.7),
             ("", "", "", "", ""), ("", "", "", "", ""), ("", "", "", "", ""), ("", "", "", "", "")]
for i, (grp, kw, cos, anl, glz) in enumerate(beispiele):
    r = 6 + i
    put(ws, r, 1, grp, font=F_INPUT, fill=FILL_IN, border=B_ALL)
    put(ws, r, 2, kw, font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt=NF)
    put(ws, r, 3, cos, font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt="0.00")
    put(ws, r, 4, f'=IF(OR($B{r}="",$C{r}=""),"",$B{r}/$C{r})', fmt="#,##0.0", border=B_ALL)
    put(ws, r, 5, anl, font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt="0.0")
    put(ws, r, 6, glz, font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt="0.0")
    put(ws, r, 7, f'=IF($D{r}="","",$D{r}*IF($E{r}="",1,$E{r})*IF($F{r}="",1,$F{r}))',
        fmt="#,##0.0", border=B_ALL)
put(ws, 14, 6, "Summe eff. kVA:", font=Font(bold=True), align=Alignment(horizontal="right"))
put(ws, 14, 7, "=SUM(G6:G13)", font=Font(bold=True), fmt="#,##0.0", border=B_ALL)
put(ws, 16, 1, "SCHRITT 2 — AUSLEGUNG", font=F_SECT, fill=C_TOOL)
ws.merge_cells("A16:H16")
put(ws, 17, 1, "Reserve-Zuschlag %", border=B_ALL)
put(ws, 17, 2, 0.2, font=F_INPUT, fill=FILL_IN, fmt=PCT, border=B_ALL)
put(ws, 18, 1, "Benötigte Leistung kVA", border=B_ALL)
put(ws, 18, 2, "=ROUND($G$14*(1+$B$17),1)", font=Font(bold=True), fmt="#,##0.0", border=B_ALL)
put(ws, 19, 1, "Empfohlene Generatorgrösse", border=B_ALL)
put(ws, 19, 2, "=IFERROR(INDEX('91_LISTEN'!$H$5:$H$20,COUNTIF('91_LISTEN'!$H$5:$H$20,\"<\"&$B$18)+1)&\" kVA\",\"> 1250 kVA: mehrere Einheiten parallel\")",
    font=Font(bold=True, size=12, color="006100"), border=B_ALL)
put(ws, 20, 1, "Redundanz N+1 (2. Einheit)", border=B_ALL)
put(ws, 20, 2, "=IF($G$14=0,\"\",\"2× \"&$B$19&\"  (Synchronisation/AMF empfohlen)\")", border=B_ALL)
put(ws, 22, 1, "Hinweis: Lastprofil > 60% Auslastung anstreben; Stage-V-Pflicht in Lärm-/Umweltzonen prüfen (siehe 24_NORMEN).",
    font=Font(italic=True, size=9, color="808080"))
for col, w in zip("ABCDEFGH", [30, 14, 9, 10, 12, 14, 12, 4]):
    ws.column_dimensions[col].width = w

# ============================================================================
# 22_ANGEBOT_KALK
# ============================================================================
ws = wb.create_sheet("22_ANGEBOT_KALK")
ws.sheet_properties.tabColor = C_TOOL
titel_zeilen(ws, C_TOOL, "ANGEBOTS-KALKULATOR — Miete + Nebenkosten",
             "Produkt aus Dropdown wählen (aus 19_PREISLISTE_CHF), Menge/Dauer eingeben — Preise rechnen live.", 9)
put(ws, 4, 1, "A) MIETPOSITIONEN", font=F_SECT, fill=C_TOOL)
ws.merge_cells("A4:G4")
hdr = ["Pos.", "Produkt (Dropdown)", "Menge", "Dauer (Tage)", "Tagespreis CHF", "Rabatt %", "Zeilentotal CHF"]
for i, h in enumerate(hdr, start=1):
    put(ws, 5, i, h, font=F_HDR, fill=C_TOOL, border=B_ALL,
        align=Alignment(horizontal="center", wrap_text=True))
for i in range(6):
    r = 6 + i
    put(ws, r, 1, i + 1, border=B_ALL)
    put(ws, r, 2, "", font=F_INPUT, fill=FILL_IN, border=B_ALL)
    put(ws, r, 3, "", font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt=NF)
    put(ws, r, 4, "", font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt=NF)
    put(ws, r, 5, f"=IF($B{r}=\"\",\"\",IFERROR(INDEX('19_PREISLISTE_CHF'!$F$5:$F$300,MATCH($B{r},'19_PREISLISTE_CHF'!$C$5:$C$300,0)),\"?\"))",
        fmt=NFD, border=B_ALL)
    put(ws, r, 6, "", font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt=PCT)
    put(ws, r, 7, f'=IF(OR($B{r}="",$C{r}="",$D{r}="",$E{r}="?"),"",$C{r}*$D{r}*$E{r}*(1-IF($F{r}="",0,$F{r})))',
        fmt=NFD, border=B_ALL)
dv = DataValidation(type="list", formula1="='19_PREISLISTE_CHF'!$C$5:$C$45",
                    allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add("B6:B11")
put(ws, 13, 1, "B) NEBENKOSTEN", font=F_SECT, fill=C_TOOL)
ws.merge_cells("A13:G13")
neben = [("Transport (pauschal CHF)", ""), ("Treibstoff (Liter)", ""), ("CHF pro Liter", 1.85),
         ("Techniker-Stunden", ""), ("CHF pro Stunde", 145), ("Übrige Kosten CHF", "")]
for i, (label, val) in enumerate(neben):
    r = 14 + i
    put(ws, r, 1, label, border=B_ALL)
    put(ws, r, 2, val, font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt=NFD)
put(ws, 21, 1, "C) TOTAL", font=F_SECT, fill=C_TOOL)
ws.merge_cells("A21:G21")
tot = [
    ("Zwischensumme Miete", "=SUM(G6:G11)"),
    ("Nebenkosten", "=SUM($B$14)+$B$15*$B$16+$B$17*$B$18+$B$19"),
    ("Total netto", "=$B$22+$B$23"),
    ("MwSt. 8.1%", "=ROUND($B$24*0.081,2)"),
    ("TOTAL BRUTTO CHF", "=$B$24+$B$25"),
]
for i, (label, f) in enumerate(tot):
    r = 22 + i
    bold = i >= 2
    put(ws, r, 1, label, border=B_ALL, font=Font(bold=bold))
    put(ws, r, 2, f, border=B_ALL, fmt=NFD,
        font=Font(bold=True, size=12 if i == 4 else 10, color="006100" if i == 4 else "000000"))
# OFFERTE-KOPF (rechts) — Eingaben für den Offerten-Generator (Ctrl+Shift+O = PDF)
put(ws, 4, 8, "OFFERTE-KOPF", font=F_SECT, fill=C_TOOL)
ws.merge_cells("H4:J4")
offkopf = [
    ("Offerte-Nr.", '="OF-"&TEXT(YEAR(TODAY()),"0000")&"-"&TEXT($J$14,"000")'),
    ("Datum", "=TODAY()"),
    ("Gültig bis", "=TODAY()+30"),
    ("Kunde", ""),
    ("Ansprechpartner", ""),
    ("Projekt / Standort", ""),
    ("Sachbearbeiter", "Burak Ücöz"),
]
for i, (label, val) in enumerate(offkopf):
    r = 5 + i
    put(ws, r, 8, label, font=Font(name=FONT, bold=True), border=B_ALL)
    ws.merge_cells(start_row=r, start_column=9, end_row=r, end_column=10)
    if isinstance(val, str) and val.startswith("="):
        put(ws, r, 9, val, border=B_ALL, fmt="DD.MM.YYYY" if label in ("Datum", "Gültig bis") else "General")
    else:
        put(ws, r, 9, val, font=F_INPUT, fill=FILL_IN, border=B_ALL)
put(ws, 13, 8, "Offerten-Zähler:", font=Font(name=FONT, size=8, italic=True, color="808080"))
ws.merge_cells("H13:I13")
put(ws, 14, 8, "laufende Nr.", font=Font(name=FONT, size=8, italic=True, color="808080"))
put(ws, 14, 10, 1, font=F_INPUT, fill=FILL_IN, border=B_ALL, fmt="0")
put(ws, 16, 8, "→ Ctrl+Shift+O: Offerte als PDF   ·   Ctrl+Shift+N: neue Offerte (Zähler +1, Felder leeren)",
    font=Font(name=FONT, size=9, italic=True, color="7F6000"))
ws.merge_cells("H16:J20")
for col, w in zip("ABCDEFGHIJ", [28, 34, 10, 12, 14, 10, 16, 16, 16, 10]):
    ws.column_dimensions[col].width = w

# ============================================================================
# 05_FORECAST (Analytics Vertrieb)
# ============================================================================
ws = wb.create_sheet("05_FORECAST")
ws.sheet_properties.tabColor = C_VERT
titel_zeilen(ws, C_VERT, "FORECAST & ANALYTICS — Vertrieb Strom CH",
             "Live-Auswertung aus 02_PIPELINE und 03_KUNDEN_CRM. Nichts eingeben — alles rechnet automatisch.", 14)
PR = f"'02_PIPELINE'"
put(ws, 4, 1, "PIPELINE NACH STATUS", font=F_SECT, fill=C_VERT); ws.merge_cells("A4:F4")
for i, h in enumerate(["Status", "Anzahl", "Volumen CHF", "Gew. Wert CHF", "Anteil %", ""], start=1):
    if h: put(ws, 5, i, h, font=F_HDR, fill=C_VERT, border=B_ALL)
for i, st in enumerate(status_pipe):
    r = 6 + i
    put_text(ws, r, 1, st, border=B_ALL)
    put(ws, r, 2, f'=COUNTIF({PR}!$R$5:$R$2000,$A{r})', fmt=NF, border=B_ALL)
    put(ws, r, 3, f'=SUMIF({PR}!$R$5:$R$2000,$A{r},{PR}!$I$5:$I$2000)', fmt=NF, border=B_ALL)
    put(ws, r, 4, f'=SUMIF({PR}!$R$5:$R$2000,$A{r},{PR}!$Q$5:$Q$2000)', fmt=NF, border=B_ALL)
    put(ws, r, 5, f'=IFERROR($C{r}/$C$16,"")', fmt=PCT, border=B_ALL)
r = 6 + len(status_pipe)
put(ws, r, 1, "TOTAL", font=Font(bold=True), border=B_ALL)
put(ws, r, 2, f"=SUM(B6:B{r-1})", font=Font(bold=True), fmt=NF, border=B_ALL)
put(ws, r, 3, f"=SUM(C6:C{r-1})", font=Font(bold=True), fmt=NF, border=B_ALL)
put(ws, r, 4, f"=SUM(D6:D{r-1})", font=Font(bold=True), fmt=NF, border=B_ALL)

row0 = r + 2
put(ws, row0, 1, "PIPELINE NACH SEGMENT", font=F_SECT, fill=C_VERT)
ws.merge_cells(start_row=row0, start_column=1, end_row=row0, end_column=6)
for i, h in enumerate(["Segment", "Anzahl", "Volumen CHF", "Gew. Wert CHF", "", "Verteilung"], start=1):
    if h: put(ws, row0 + 1, i, h, font=F_HDR, fill=C_VERT, border=B_ALL)
seg_start = row0 + 2
for i, sg in enumerate(seg_union):
    r = seg_start + i
    put_text(ws, r, 1, sg, border=B_ALL)
    put(ws, r, 2, f'=COUNTIF({PR}!$D$5:$D$2000,$A{r})', fmt=NF, border=B_ALL)
    put(ws, r, 3, f'=SUMIF({PR}!$D$5:$D$2000,$A{r},{PR}!$I$5:$I$2000)', fmt=NF, border=B_ALL)
    put(ws, r, 4, f'=SUMIF({PR}!$D$5:$D$2000,$A{r},{PR}!$Q$5:$Q$2000)', fmt=NF, border=B_ALL)
    put(ws, r, 6, f'=IF($C{r}=0,"",REPT("█",ROUND($C{r}/MAX($C${seg_start}:$C${seg_start+len(seg_union)-1})*20,0)))',
        font=Font(color=C_VERT, size=9), border=B_ALL)
seg_end = seg_start + len(seg_union) - 1

row0 = seg_end + 2
put(ws, row0, 1, "PIPELINE NACH KANTON", font=F_SECT, fill=C_VERT)
ws.merge_cells(start_row=row0, start_column=1, end_row=row0, end_column=6)
for i, h in enumerate(["Kanton", "Anzahl", "Volumen CHF", "davon WON", "", ""], start=1):
    if h: put(ws, row0 + 1, i, h, font=F_HDR, fill=C_VERT, border=B_ALL)
kt_start = row0 + 2
kt_show = [k for k in kantone if k not in ("FL", "CH", "tbd")]
for i, kt in enumerate(kt_show):
    r = kt_start + i
    put_text(ws, r, 1, kt, border=B_ALL)
    put(ws, r, 2, f'=COUNTIF({PR}!$C$5:$C$2000,$A{r})', fmt=NF, border=B_ALL)
    put(ws, r, 3, f'=SUMIF({PR}!$C$5:$C$2000,$A{r},{PR}!$I$5:$I$2000)', fmt=NF, border=B_ALL)
    put(ws, r, 4, f'=SUMIFS({PR}!$I$5:$I$2000,{PR}!$C$5:$C$2000,$A{r},{PR}!$R$5:$R$2000,"WON")', fmt=NF, border=B_ALL)
kt_end = kt_start + len(kt_show) - 1

# --- Diagramme rechts (Spalte N ff.) ---
def _fc_bar(title, cat_lo, cat_hi, data_col, anchor, h=8):
    ch = BarChart(); ch.type = "bar"; ch.title = title; ch.style = 10
    data = Reference(ws, min_col=data_col, min_row=cat_lo - 1, max_row=cat_hi)
    cats = Reference(ws, min_col=1, min_row=cat_lo, max_row=cat_hi)
    ch.add_data(data, titles_from_data=True); ch.set_categories(cats)
    ch.legend = None; ch.width = 13; ch.height = h
    ws.add_chart(ch, anchor)
_fc_bar("Volumen CHF nach Status", 6, 6 + len(status_pipe) - 1, 3, "N4")
_fc_bar("Volumen CHF nach Segment", seg_start, seg_end, 3, "N20", h=11)
_fc_bar("Volumen CHF nach Kanton", kt_start, kt_end, 3, "N38", h=10)

# CRM-Forecast rechts (Spalten H..L)
put(ws, 4, 8, "CRM-FORECAST NACH SEGMENT (aus 03_KUNDEN_CRM)", font=F_SECT, fill=C_VERT)
ws.merge_cells(start_row=4, start_column=8, end_row=4, end_column=13)
CR = f"'03_KUNDEN_CRM'"
for i, h in enumerate(["Segment", "Firmen", "Wert CHF", "Gew. Forecast CHF", "Prio A"], start=8):
    put(ws, 5, i, h, font=F_HDR, fill=C_VERT, border=B_ALL)
for i, sg in enumerate(crm_seg):
    r = 6 + i
    put_text(ws, r, 8, sg, border=B_ALL)
    put(ws, r, 9, f'=COUNTIF({CR}!$C$5:$C$3000,$H{r})', fmt=NF, border=B_ALL)
    put(ws, r, 10, f'=SUMIF({CR}!$C$5:$C$3000,$H{r},{CR}!$U$5:$U$3000)', fmt=NF, border=B_ALL)
    put(ws, r, 11, f'=SUMIF({CR}!$C$5:$C$3000,$H{r},{CR}!$W$5:$W$3000)', fmt=NF, border=B_ALL)
    put(ws, r, 12, f'=COUNTIFS({CR}!$C$5:$C$3000,$H{r},{CR}!$B$5:$B$3000,"A")', fmt=NF, border=B_ALL)
r = 6 + len(crm_seg)
put(ws, r, 8, "TOTAL", font=Font(bold=True), border=B_ALL)
for col in "IJKL":
    ci = openpyxl.utils.column_index_from_string(col)
    put(ws, r, ci, f"=SUM({col}6:{col}{r-1})", font=Font(bold=True), fmt=NF, border=B_ALL)
for col, w in zip(["A","B","C","D","E","F","G","H","I","J","K","L","M"],
                  [24, 9, 13, 13, 9, 24, 3, 26, 9, 13, 15, 8, 8]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A6"

# ============================================================================
# 06_MONATSREPORT
# ============================================================================
ws = wb.create_sheet("06_MONATSREPORT")
ws.sheet_properties.tabColor = C_VERT
titel_zeilen(ws, C_VERT, "MONATSREPORT — MiT Strom Schweiz",
             "Rechnet live aus 02_PIPELINE. Export als eigene Datei: Ctrl+Shift+M (erstellt automatisch neue Arbeitsmappe).", 9)
put(ws, 3, 1, '="Berichtsmonat: "&TEXT(TODAY(),"MMMM YYYY")&"  |  Stand: "&TEXT(TODAY(),"DD.MM.YYYY")',
    font=Font(size=10, bold=True, color="1F4E79"))
ws.merge_cells("A3:I3")
kpis = [
    ("✅ AUFTRAGSEINGANG (WON)", f'=SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$I$5:$I$2000)', NF, "C6EFCE"),
    ("📄 OFFERTEN (laufend)", f'=SUMIF({PR}!$R$5:$R$2000,"offered",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"to be offered",{PR}!$I$5:$I$2000)', NF, "FFEB9C"),
    ("🎯 OPPORTUNITÄTEN", f'=SUMIF({PR}!$R$5:$R$2000,"follow-up",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"In evaluation",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"tbd",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"on hold",{PR}!$I$5:$I$2000)', NF, "DDEBF7"),
]
for i, (label, f, fmt, fill) in enumerate(kpis):
    c1 = 1 + i * 3
    ws.merge_cells(start_row=5, start_column=c1, end_row=5, end_column=c1 + 2)
    put(ws, 5, c1, label, font=Font(bold=True, size=10), fill=fill, align=A_CENTER)
    ws.merge_cells(start_row=6, start_column=c1, end_row=6, end_column=c1 + 2)
    put(ws, 6, c1, f, font=Font(bold=True, size=16), fill=fill, align=A_CENTER, fmt=fmt)
    ws.row_dimensions[6].height = 24
zeile2 = [
    ("Deals aktiv", f'=SUMPRODUCT(({PR}!$R$5:$R$2000<>"")*({PR}!$R$5:$R$2000<>"LOST")*({PR}!$R$5:$R$2000<>"Declined"))'),
    ("Ø Marge %", f'=IFERROR(AVERAGEIF({PR}!$P$5:$P$2000,"<>",{PR}!$P$5:$P$2000),"")'),
    ("Gewichteter Wert offen", f'=SUM({PR}!$Q$5:$Q$2000)-SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$Q$5:$Q$2000)'),
]
for i, (label, f) in enumerate(zeile2):
    c1 = 1 + i * 3
    ws.merge_cells(start_row=8, start_column=c1, end_row=8, end_column=c1 + 2)
    put(ws, 8, c1, label, font=F_KPI_L, align=A_CENTER)
    ws.merge_cells(start_row=9, start_column=c1, end_row=9, end_column=c1 + 2)
    put(ws, 9, c1, f, font=Font(bold=True, size=13), align=A_CENTER,
        fmt=PCT if "Marge" in label else NF)

ws.merge_cells("A10:I10")
put(ws, 10, 1, f'="📊 GESAMT-PIPELINE: "&TEXT(SUMIF({PR}!$R$5:$R$2000,"<>",{PR}!$I$5:$I$2000),"#,##0")&" CHF  ·  "&SUMPRODUCT(({PR}!$R$5:$R$2000<>"")*1)&" Deals erfasst  ·  Druck: Strg+P (Als PDF speichern)"',
    font=Font(bold=True, size=11, color="1F4E79"), align=A_CENTER)
put(ws, 11, 1, "TOP 5 — GEWONNENE AUFTRÄGE", font=F_SECT, fill=C_VERT); ws.merge_cells("A11:D11")
for i, h in enumerate(["#", "Kunde", "Volumen CHF", "Segment"], start=1):
    put(ws, 12, i, h, font=F_HDR, fill=C_VERT, border=B_ALL)
WONR = f"{PR}!$Z$5:$Z$2000"   # _WON-Rangspalte
for k in range(1, 6):
    r = 12 + k
    put(ws, r, 1, k, border=B_ALL)
    put(ws, r, 2, f'=IFERROR(INDEX({PR}!$B$5:$B$2000,MATCH(LARGE({WONR},{k}),{WONR},0)),"–")', border=B_ALL)
    put(ws, r, 3, f'=IFERROR(INT(LARGE({WONR},{k})),"")', fmt=NF, border=B_ALL)
    put(ws, r, 4, f'=IFERROR(INDEX({PR}!$D$5:$D$2000,MATCH(LARGE({WONR},{k}),{WONR},0)),"")', border=B_ALL)

put(ws, 11, 6, "TOP 5 — OFFENE CHANCEN", font=F_SECT, fill=C_VERT)
ws.merge_cells(start_row=11, start_column=6, end_row=11, end_column=9)
for i, h in enumerate(["#", "Kunde", "Volumen CHF", "Status"], start=6):
    put(ws, 12, i, h, font=F_HDR, fill=C_VERT, border=B_ALL)
ACTR = f"{PR}!$AD$5:$AD$2000"  # _ACT-Rangspalte (offene/aktive Deals)
for k in range(1, 6):
    r = 12 + k
    put(ws, r, 6, k, border=B_ALL)
    put(ws, r, 7, f'=IFERROR(INDEX({PR}!$B$5:$B$2000,MATCH(LARGE({ACTR},{k}),{ACTR},0)),"–")', border=B_ALL)
    put(ws, r, 8, f'=IFERROR(INT(LARGE({ACTR},{k})),"")', fmt=NF, border=B_ALL)
    put(ws, r, 9, f'=IFERROR(INDEX({PR}!$R$5:$R$2000,MATCH(LARGE({ACTR},{k}),{ACTR},0)),"")', border=B_ALL)

put(ws, 20, 1, "STATUS-ÜBERSICHT", font=F_SECT, fill=C_VERT); ws.merge_cells("A20:D20")
for i, h in enumerate(["Status", "Anzahl", "Volumen CHF", "Gew. Wert"], start=1):
    put(ws, 21, i, h, font=F_HDR, fill=C_VERT, border=B_ALL)
for i, st in enumerate(status_pipe):
    r = 22 + i
    put_text(ws, r, 1, st, border=B_ALL)
    put(ws, r, 2, f'=COUNTIF({PR}!$R$5:$R$2000,$A{r})', fmt=NF, border=B_ALL)
    put(ws, r, 3, f'=SUMIF({PR}!$R$5:$R$2000,$A{r},{PR}!$I$5:$I$2000)', fmt=NF, border=B_ALL)
    put(ws, r, 4, f'=SUMIF({PR}!$R$5:$R$2000,$A{r},{PR}!$Q$5:$Q$2000)', fmt=NF, border=B_ALL)
for col, w in zip("ABCDEFGHI", [16, 30, 13, 20, 3, 16, 30, 13, 14]):
    ws.column_dimensions[col].width = w

# ============================================================================
# 17_GLOBAL_ANALYTICS
# ============================================================================
ws = wb.create_sheet("17_GLOBAL_ANALYTICS")
ws.sheet_properties.tabColor = C_GLOB
titel_zeilen(ws, C_GLOB, "GLOBAL ANALYTICS — Auswertung der DC-Projektdatenbank",
             "Rechnet live aus 15_GLOBAL_PROJEKTE. Nach Import eines neuen Trackers aktualisiert sich alles automatisch.", 12)
GPS = f"'15_GLOBAL_PROJEKTE'"
regionen = ["NAM", "EUROPE", "ASIA", "AUSPAC", "LAM", "MIDDLE EAST", "AFRICA", "EURASIA"]
stati = ["Planning", "Engineering", "Under Construction"]
put(ws, 4, 1, "REPORT-VOLUMEN (Mrd $) — REGION × STATUS", font=F_SECT, fill=C_GLOB)
ws.merge_cells("A4:F4")
put(ws, 5, 1, "Region", font=F_HDR, fill=C_GLOB, border=B_ALL)
for j, stt in enumerate(stati):
    put(ws, 5, 2 + j, stt, font=F_HDR, fill=C_GLOB, border=B_ALL)
put(ws, 5, 5, "TOTAL", font=F_HDR, fill=C_GLOB, border=B_ALL)
put(ws, 5, 6, "Projekte", font=F_HDR, fill=C_GLOB, border=B_ALL)
for i, reg in enumerate(regionen):
    r = 6 + i
    put_text(ws, r, 1, reg, border=B_ALL)
    for j, stt in enumerate(stati):
        put(ws, r, 2 + j,
            f'=SUMIFS({GPS}!$E$5:$E$20000,{GPS}!$K$5:$K$20000,$A{r},{GPS}!$H$5:$H$20000,"{stt}")/1000000000',
            fmt="#,##0.00", border=B_ALL)
    put(ws, r, 5, f"=SUM(B{r}:D{r})", font=Font(bold=True), fmt="#,##0.00", border=B_ALL)
    put(ws, r, 6, f'=COUNTIF({GPS}!$K$5:$K$20000,$A{r})', fmt=NF, border=B_ALL)
r_tot = 6 + len(regionen)
put(ws, r_tot, 1, "TOTAL", font=Font(bold=True), border=B_ALL)
for col in "BCDEF":
    ci = openpyxl.utils.column_index_from_string(col)
    put(ws, r_tot, ci, f"=SUM({col}6:{col}{r_tot-1})", font=Font(bold=True),
        fmt="#,##0.00" if col != "F" else NF, border=B_ALL)

put(ws, r_tot + 2, 1, "PROJEKTE NACH BAUSTART-JAHR", font=F_SECT, fill=C_GLOB)
ws.merge_cells(start_row=r_tot + 2, start_column=1, end_row=r_tot + 2, end_column=6)
jr_hdr = r_tot + 3
for i, h in enumerate(["Baustart-Jahr", "Projekte", "Report-Vol. Mrd $", "", "Verteilung", ""], start=1):
    if h: put(ws, jr_hdr, i, h, font=F_HDR, fill=C_GLOB, border=B_ALL)
jahre = list(range(2020, 2036)) + ["UNKNOWN"]
for i, jahr in enumerate(jahre):
    r = jr_hdr + 1 + i
    put_text(ws, r, 1, jahr, border=B_ALL)
    put(ws, r, 2, f'=COUNTIF({GPS}!$L$5:$L$20000,$A{r})', fmt=NF, border=B_ALL)
    put(ws, r, 3, f'=SUMIF({GPS}!$L$5:$L$20000,$A{r},{GPS}!$E$5:$E$20000)/1000000000', fmt="#,##0.00", border=B_ALL)
    put(ws, r, 5, f'=IF($B{r}=0,"",REPT("█",ROUND($B{r}/MAX($B${jr_hdr+1}:$B${jr_hdr+len(jahre)})*25,0)))',
        font=Font(color=C_GLOB, size=9))

# Top-Länder (statisch ermittelt, Werte live)
import collections
land_i = gph.index("Land")
val_i = gph.index("Report Value ($)")
cnt = collections.Counter()
for row in D["global_projekte"]["rows"]:
    if row[land_i]:
        cnt[row[land_i]] += 1
top_laender = [l for l, _ in cnt.most_common(15)]
if "Switzerland" not in top_laender:
    top_laender.append("Switzerland")
put(ws, 4, 8, "TOP-LÄNDER (nach Anzahl Projekte)", font=F_SECT, fill=C_GLOB)
ws.merge_cells(start_row=4, start_column=8, end_row=4, end_column=12)
for i, h in enumerate(["Land", "Projekte", "Report-Vol. Mrd $", "Kontakte", ""], start=8):
    if h: put(ws, 5, i, h, font=F_HDR, fill=C_GLOB, border=B_ALL)
GKS = f"'16_GLOBAL_KONTAKTE'"
for i, land in enumerate(top_laender):
    r = 6 + i
    put_text(ws, r, 8, land, border=B_ALL)
    put(ws, r, 9, f'=COUNTIF({GPS}!$I$5:$I$20000,$H{r})', fmt=NF, border=B_ALL)
    put(ws, r, 10, f'=SUMIF({GPS}!$I$5:$I$20000,$H{r},{GPS}!$E$5:$E$20000)/1000000000', fmt="#,##0.00", border=B_ALL)
    put(ws, r, 11, f'=COUNTIF({GKS}!$O$5:$O$15000,$H{r})', fmt=NF, border=B_ALL)
for col, w in zip(["A","B","C","D","E","F","G","H","I","J","K","L"],
                  [14, 13, 13, 16, 26, 10, 3, 18, 10, 15, 10, 8]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A6"


# ============================================================================
# 07_CEO_REPORT (Live-Ansicht wie in CH_MiT_Strom_Customer_CEO_CFO)
# ============================================================================
ws = wb.create_sheet("07_CEO_REPORT")
ws.sheet_properties.tabColor = C_VERT
titel_zeilen(ws, C_VERT, "CEO SALES REPORT — MiT Strom Schweiz",
             "Live aus 02_PIPELINE — Auftragseingang, Offerten, Opportunitäten, Verloren. Druck: Strg+P.", 13)
put(ws, 3, 1, '="Stand: "&TEXT(TODAY(),"DD.MM.YYYY")&"  ·  Mobil in Time AG · An Aggreko Company"',
    font=Font(size=10, italic=True, color="808080"))
ws.merge_cells("A3:M3")
kpi3 = [
    ("✅  AUFTRAGSEINGANG (WON)", f'=SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$I$5:$I$2000)',
     f'=COUNTIF({PR}!$R$5:$R$2000,"WON")&" Deals"', "C6EFCE"),
    ("📄  OFFERTE — laufend", f'=SUMIF({PR}!$R$5:$R$2000,"offered",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"to be offered",{PR}!$I$5:$I$2000)',
     f'=COUNTIF({PR}!$R$5:$R$2000,"offered")+COUNTIF({PR}!$R$5:$R$2000,"to be offered")&" Deals"', "FFEB9C"),
    ("🎯  OPPORTUNITÄT", f'=SUMIF({PR}!$R$5:$R$2000,"follow-up",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"In evaluation",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"tbd",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"on hold",{PR}!$I$5:$I$2000)',
     f'=COUNTIF({PR}!$R$5:$R$2000,"follow-up")+COUNTIF({PR}!$R$5:$R$2000,"In evaluation")+COUNTIF({PR}!$R$5:$R$2000,"tbd")+COUNTIF({PR}!$R$5:$R$2000,"on hold")&" Deals"', "DDEBF7"),
]
for i, (label, f_chf, f_n, fill) in enumerate(kpi3):
    c1 = 1 + i * 4
    ws.merge_cells(start_row=5, start_column=c1, end_row=5, end_column=c1 + 3)
    put(ws, 5, c1, label, font=Font(bold=True, size=11), fill=fill, align=A_CENTER)
    ws.merge_cells(start_row=6, start_column=c1, end_row=6, end_column=c1 + 3)
    put(ws, 6, c1, f_chf, font=Font(bold=True, size=16), fill=fill, align=A_CENTER, fmt=NF)
    ws.merge_cells(start_row=7, start_column=c1, end_row=7, end_column=c1 + 3)
    put(ws, 7, c1, f_n, font=Font(size=10, color="595959"), fill=fill, align=A_CENTER)
ws.row_dimensions[6].height = 24

ceo_cols = ["Nr.", "Kunde / Unternehmen", "Kt.", "Segment", "Start", "Leistung / Fleet",
            "Volumen CHF", "Gew.Wert CHF", "Marge CHF", "Status", "Wahr. %", "Nächster Schritt", "_v"]
ceo_src = {2: "$B", 3: "$C", 4: "$D", 5: "$H", 6: "$E", 7: "$I", 8: "$Q", 9: "$O",
           10: "$R", 11: "$S", 12: "$V"}
# Rang über kategorie-spezifische Hilfsspalten (LARGE -> Excel + LibreOffice)
sektionen = [
    ("1. AUFTRAGSEINGANG (WON) — bestätigte Aufträge", "$Z", 20),
    ("2. OFFERTEN — laufend", "$AA", 30),
    ("3. OPPORTUNITÄTEN — Follow-up / Evaluation / tbd / on hold", "$AB", 30),
    ("4. VERLOREN / ABGESAGT", "$AC", 15),
]
r = 9
for titel_s, rankcol, nrows in sektionen:
    RC = f"{PR}!{rankcol}$5:{rankcol}$2000"
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=13)
    put(ws, r, 1, titel_s, font=F_SECT, fill=C_VERT)
    r += 1
    for i, h in enumerate(ceo_cols, start=1):
        put(ws, r, i, h, font=F_HDR, fill=C_VERT, border=B_ALL,
            align=Alignment(horizontal="center", wrap_text=True))
    hdr_r = r
    r += 1
    for k in range(1, nrows + 1):
        put(ws, r, 13, f'=IFERROR(LARGE({RC},{k}),"")', border=B_ALL)
        put(ws, r, 1, f'=IF($M{r}="","",{k})', border=B_ALL)
        for ci, src in ceo_src.items():
            fmt = "General"
            if ci in (7, 8, 9):
                fmt = NF
            if ci == 11:
                fmt = PCT
            put(ws, r, ci,
                f'=IF($M{r}="","",IFERROR(INDEX({PR}!{src}$5:{src}$2000,MATCH($M{r},{RC},0)),""))',
                fmt=fmt, border=B_ALL)
        r += 1
    r += 1
ws.column_dimensions["M"].hidden = True
for col, w in zip("ABCDEFGHIJKLM", [5, 30, 5, 20, 11, 22, 12, 12, 11, 12, 8, 40, 6]):
    ws.column_dimensions[col].width = w
ws.conditional_formatting.add(f"J10:J{r}", FormulaRule(
    formula=['EXACT($J10,"WON")'], fill=PatternFill("solid", fgColor="C6EFCE"),
    font=Font(color="006100", bold=True)))
ws.conditional_formatting.add(f"J10:J{r}", FormulaRule(
    formula=['OR(EXACT($J10,"LOST"),EXACT($J10,"Declined"))'],
    fill=PatternFill("solid", fgColor="FFC7CE"), font=Font(color="9C0006")))
ws.freeze_panes = "A5"
ws.print_area = f"A1:L{r}"
ws.page_setup.fitToWidth = 1
ws.page_setup.orientation = "landscape"

# ============================================================================
# 08_DIAGRAMME (echte Excel-Charts, live aus 02_PIPELINE)
# ============================================================================
from openpyxl.chart import BarChart, PieChart, Reference

ws = wb.create_sheet("08_DIAGRAMME")
ws.sheet_properties.tabColor = C_VERT
titel_zeilen(ws, C_VERT, "DIAGRAMME — MiT Strom Schweiz",
             "Alle Diagramme aktualisieren sich automatisch aus 02_PIPELINE.", 12)

# Datentabelle 1: nach Status
put(ws, 4, 1, "Status", font=F_HDR, fill=C_VERT, border=B_ALL)
put(ws, 4, 2, "Anzahl", font=F_HDR, fill=C_VERT, border=B_ALL)
put(ws, 4, 3, "Volumen CHF", font=F_HDR, fill=C_VERT, border=B_ALL)
st_start = 5
for i, st in enumerate(status_pipe):
    rr = st_start + i
    put_text(ws, rr, 1, st, border=B_ALL)
    put(ws, rr, 2, f'=COUNTIF({PR}!$R$5:$R$2000,$A{rr})', fmt=NF, border=B_ALL)
    put(ws, rr, 3, f'=SUMIF({PR}!$R$5:$R$2000,$A{rr},{PR}!$I$5:$I$2000)', fmt=NF, border=B_ALL)
st_end = st_start + len(status_pipe) - 1

# Datentabelle 2: Gruppen (für Kreisdiagramm)
g_start = st_end + 3
put(ws, g_start - 1, 1, "Gruppe", font=F_HDR, fill=C_VERT, border=B_ALL)
put(ws, g_start - 1, 2, "Volumen CHF", font=F_HDR, fill=C_VERT, border=B_ALL)
gruppen = [
    ("✅ WON", f'=SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$I$5:$I$2000)'),
    ("📄 Offerte", f'=SUMIF({PR}!$R$5:$R$2000,"offered",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"to be offered",{PR}!$I$5:$I$2000)'),
    ("🎯 Opportunität", f'=SUMIF({PR}!$R$5:$R$2000,"follow-up",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"In evaluation",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"tbd",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"on hold",{PR}!$I$5:$I$2000)'),
    ("❌ Verloren", f'=SUMIF({PR}!$R$5:$R$2000,"LOST",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"Declined",{PR}!$I$5:$I$2000)'),
]
for i, (label, f) in enumerate(gruppen):
    rr = g_start + i
    put_text(ws, rr, 1, label, border=B_ALL)
    put(ws, rr, 2, f, fmt=NF, border=B_ALL)
g_end = g_start + len(gruppen) - 1

# Datentabelle 3: nach Segment
sg_start = g_end + 3
put(ws, sg_start - 1, 1, "Segment", font=F_HDR, fill=C_VERT, border=B_ALL)
put(ws, sg_start - 1, 2, "Volumen CHF", font=F_HDR, fill=C_VERT, border=B_ALL)
for i, sg in enumerate(seg_union):
    rr = sg_start + i
    put_text(ws, rr, 1, sg, border=B_ALL)
    put(ws, rr, 2, f'=SUMIF({PR}!$D$5:$D$2000,$A{rr},{PR}!$I$5:$I$2000)', fmt=NF, border=B_ALL)
sg_end = sg_start + len(seg_union) - 1

# Datentabelle 4: nach Kanton
kt2_start = sg_end + 3
put(ws, kt2_start - 1, 1, "Kanton", font=F_HDR, fill=C_VERT, border=B_ALL)
put(ws, kt2_start - 1, 2, "Volumen CHF", font=F_HDR, fill=C_VERT, border=B_ALL)
for i, kt in enumerate(kt_show):
    rr = kt2_start + i
    put_text(ws, rr, 1, kt, border=B_ALL)
    put(ws, rr, 2, f'=SUMIF({PR}!$C$5:$C$2000,$A{rr},{PR}!$I$5:$I$2000)', fmt=NF, border=B_ALL)
kt2_end = kt2_start + len(kt_show) - 1

def mk_bar(title, data_col, cat_lo, cat_hi, anchor, horizontal=False, w=16, h=8):
    ch = BarChart()
    ch.type = "bar" if horizontal else "col"
    ch.title = title
    ch.style = 10
    data = Reference(ws, min_col=data_col, min_row=cat_lo - 1, max_row=cat_hi)
    cats = Reference(ws, min_col=1, min_row=cat_lo, max_row=cat_hi)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    ch.legend = None
    ch.width = w
    ch.height = h
    ws.add_chart(ch, anchor)

mk_bar("Volumen CHF nach Status", 3, st_start, st_end, "E4")
mk_bar("Anzahl Deals nach Status", 2, st_start, st_end, "N4")
pie = PieChart()
pie.title = "Pipeline-Verteilung (Volumen CHF)"
pie_data = Reference(ws, min_col=2, min_row=g_start - 1, max_row=g_end)
pie_cats = Reference(ws, min_col=1, min_row=g_start, max_row=g_end)
pie.add_data(pie_data, titles_from_data=True)
pie.set_categories(pie_cats)
pie.width = 16
pie.height = 8
ws.add_chart(pie, "E21")
mk_bar("Volumen CHF nach Segment", 2, sg_start, sg_end, "N21", horizontal=True, h=12)
mk_bar("Volumen CHF nach Kanton", 2, kt2_start, kt2_end, "E38", h=10)
for col, w in zip("ABC", [24, 12, 14]):
    ws.column_dimensions[col].width = w

# ============================================================================
# 01_DASHBOARD
# ============================================================================
ws = wb.create_sheet("01_DASHBOARD", 0)
ws.sheet_properties.tabColor = C_NAV
titel_zeilen(ws, C_NAV, "DASHBOARD — Gesamtübersicht Workspace",
             "Alle Kennzahlen live aus den Daten-Reitern. Klick auf Bereichstitel = Sprung zum Reiter.", 12)

TILE_ACCENT = [C_VERT]
TILE_IDX = [0]
WHITE_SIDE = Side(style="medium", color="FFFFFF")
def tile(ws, row, col, label, formula, fmt=NF, span=2, fill=None):
    """Gefüllte Executive-KPI-Karte: Bereichsfarbe, weiße Schrift, weiße Trenner."""
    acc = TILE_ACCENT[0]
    # abwechselnd etwas heller/dunkler für Kartentrennung
    body = shade(acc, 1.0 if TILE_IDX[0] % 2 == 0 else 0.82)
    TILE_IDX[0] += 1
    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + span - 1)
    put(ws, row, col, label, font=Font(name=FONT, size=9, bold=True, color="E8E8E8"),
        fill=body, align=A_CENTER)
    ws.merge_cells(start_row=row + 1, start_column=col, end_row=row + 1, end_column=col + span - 1)
    put(ws, row + 1, col, formula, font=Font(name=FONT, size=16, bold=True, color="FFFFFF"),
        fill=body, align=A_CENTER, fmt=fmt)
    for j in range(span):
        cc = col + j
        left = WHITE_SIDE if j == 0 else None
        right = WHITE_SIDE if j == span - 1 else None
        ws.cell(row=row, column=cc).border = Border(top=WHITE_SIDE, left=left, right=right)
        ws.cell(row=row + 1, column=cc).border = Border(bottom=WHITE_SIDE, left=left, right=right)
    ws.row_dimensions[row].height = 16
    ws.row_dimensions[row + 1].height = 26

TILE_ACCENT[0] = C_VERT; TILE_IDX[0] = 0
put(ws, 4, 1, '=HYPERLINK("#\'02_PIPELINE\'!A1","▶ VERTRIEB STROM CH")', font=Font(bold=True, size=13, color=C_VERT))
tile(ws, 5, 1, "WON Umsatz CHF", f'=SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$I$5:$I$2000)')
tile(ws, 5, 3, "Offene Pipeline CHF",
     f'=SUMIF({PR}!$R$5:$R$2000,"<>",{PR}!$I$5:$I$2000)-SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$I$5:$I$2000)-SUMIF({PR}!$R$5:$R$2000,"LOST",{PR}!$I$5:$I$2000)-SUMIF({PR}!$R$5:$R$2000,"Declined",{PR}!$I$5:$I$2000)')
tile(ws, 5, 5, "Gewichtet offen CHF",
     f'=SUM({PR}!$Q$5:$Q$2000)-SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$Q$5:$Q$2000)')
tile(ws, 5, 7, "Deals aktiv",
     f'=SUMPRODUCT(({PR}!$R$5:$R$2000<>"")*({PR}!$R$5:$R$2000<>"LOST")*({PR}!$R$5:$R$2000<>"Declined"))')
tile(ws, 5, 9, "CRM-Zielkunden", f"=COUNTA({CR}!$D$5:$D$3000)")
tile(ws, 5, 11, "Kunden in Kartei", f"=COUNTA('04_KUNDENKARTEI'!$B$5:$B$5000)")

TILE_ACCENT[0] = C_DC; TILE_IDX[0] = 0
put(ws, 8, 1, '=HYPERLINK("#\'10_DC_BETREIBER\'!A1","▶ DATACENTER SCHWEIZ")', font=Font(bold=True, size=13, color=C_DC))
tile(ws, 9, 1, "DC-Betreiber CH", f"=COUNTA('10_DC_BETREIBER'!$A$5:$A$300)")
tile(ws, 9, 3, "Bauprojekte CH", f"=COUNTA('11_DC_BAUPROJEKTE'!$E$5:$E$300)")
tile(ws, 9, 5, "Standorte", f"=COUNTA('12_DC_STANDORTE'!$A$5:$A$300)")
tile(ws, 9, 7, "DC-Kontakte", f"=COUNTA('13_DC_KONTAKTE'!$A$5:$A$500)")
tile(ws, 9, 9, "CHF-Potential Bau",
     f"=SUM('11_DC_BAUPROJEKTE'!$U$5:$U$300)")
tile(ws, 9, 11, "A-Prio Projekte",
     f'=SUMPRODUCT((LEFT(\'11_DC_BAUPROJEKTE\'!$W$5:$W$300,1)="A")*1)')

TILE_ACCENT[0] = C_GLOB; TILE_IDX[0] = 0
put(ws, 12, 1, '=HYPERLINK("#\'15_GLOBAL_PROJEKTE\'!A1","▶ GLOBAL DATA CENTRE")', font=Font(bold=True, size=13, color=C_GLOB))
tile(ws, 13, 1, "Projekte weltweit", f"=COUNTA({GPS}!$C$5:$C$20000)")
tile(ws, 13, 3, "Report-Vol. Mrd $", f"=SUM({GPS}!$E$5:$E$20000)/1000000000", fmt="#,##0.0")
tile(ws, 13, 5, "Under Construction", f'=COUNTIF({GPS}!$H$5:$H$20000,"Under Construction")')
tile(ws, 13, 7, "EUROPE-Projekte", f'=COUNTIF({GPS}!$K$5:$K$20000,"EUROPE")')
tile(ws, 13, 9, "Globale Kontakte", f"=COUNTA({GKS}!$E$5:$E$15000)")
tile(ws, 13, 11, "Schweiz-Projekte", f'=COUNTIF({GPS}!$I$5:$I$20000,"Switzerland")')

TILE_ACCENT[0] = C_PROD; TILE_IDX[0] = 0
put(ws, 16, 1, '=HYPERLINK("#\'18_KATALOG\'!A1","▶ PRODUKTE && PREISE")', font=Font(bold=True, size=13, color=C_PROD))
tile(ws, 17, 1, "Katalog-Produkte", f"=COUNTA('18_KATALOG'!$E$5:$E$2000)")
tile(ws, 17, 3, "Kategorien", "=SUMPRODUCT(('91_LISTEN'!$B$5:$B$40<>\"\")*0)+27")
tile(ws, 17, 5, "Preisliste CHF", f"=COUNTA('19_PREISLISTE_CHF'!$C$5:$C$300)")
tile(ws, 17, 7, "Preisliste INTL", f"=COUNTA('20_PREISLISTE_INTL'!$F$5:$F$500)")
tile(ws, 17, 9, "Akquise-Aktionen offen",
     f'=COUNTIF(\'25_AKQUISE_90T\'!$H$5:$H$500,"OFFEN")+COUNTIF(\'25_AKQUISE_90T\'!$H$5:$H$500,"HEUTE!")')
tile(ws, 17, 11, "Marktpotenzial CH/J Mio", f"={MV_TOTAL_CHF}/1000000", fmt='#,##0.0" Mio"')

# ---- Cockpit-Diagramme (Doughnut-Gauge + Bars) ----
from openpyxl.chart import DoughnutChart
from openpyxl.chart.series import DataPoint
from openpyxl.drawing.fill import PatternFillProperties, ColorChoice

put(ws, 20, 1, "COCKPIT — LIVE-ANALYSE", font=Font(name=FONT, bold=True, size=12, color=C_NAV))
# Hilfsdaten weit rechts (ausgeblendet)
HB = 40   # Spalte AN
put(ws, 4, HB, "Status", font=F_KPI_L)
put(ws, 4, HB + 1, "Volumen", font=F_KPI_L)
gruppen_dash = [
    ("WON", f'=SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$I$5:$I$2000)'),
    ("Offerte", f'=SUMIF({PR}!$R$5:$R$2000,"offered",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"to be offered",{PR}!$I$5:$I$2000)'),
    ("Opportunität", f'=SUMIF({PR}!$R$5:$R$2000,"follow-up",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"In evaluation",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"tbd",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"on hold",{PR}!$I$5:$I$2000)'),
    ("Verloren", f'=SUMIF({PR}!$R$5:$R$2000,"LOST",{PR}!$I$5:$I$2000)+SUMIF({PR}!$R$5:$R$2000,"Declined",{PR}!$I$5:$I$2000)'),
]
for i, (lab, f) in enumerate(gruppen_dash):
    put_text(ws, 5 + i, HB, lab); put(ws, 5 + i, HB + 1, f, fmt=NF)
# Segmente Top (aus Forecast-Bereich): eigene kleine Tabelle
put(ws, 11, HB, "Segment", font=F_KPI_L); put(ws, 11, HB + 1, "Volumen", font=F_KPI_L)
seg_top = seg_union[:10]
for i, sg in enumerate(seg_top):
    put_text(ws, 12 + i, HB, sg)
    put(ws, 12 + i, HB + 1, f'=SUMIF({PR}!$D$5:$D$2000,{get_column_letter(HB)}{12+i},{PR}!$I$5:$I$2000)', fmt=NF)
seg_top_end = 12 + len(seg_top) - 1
for cc in range(HB, HB + 5):
    ws.column_dimensions[get_column_letter(cc)].width = 11

col_HB = get_column_letter(HB)
# Doughnut: Pipeline nach Status
dn = DoughnutChart(); dn.title = "Pipeline nach Status (CHF)"; dn.holeSize = 58; dn.height = 7.0; dn.width = 7.4
dref = Reference(ws, min_col=HB + 1, min_row=4, max_row=8)
dcat = Reference(ws, min_col=HB, min_row=5, max_row=8)
dn.add_data(dref, titles_from_data=True); dn.set_categories(dcat)
# Segmentfarben
for idx, col in enumerate(["70AD47", "FFC000", "4472C4", "C00000"]):
    pt = DataPoint(idx=idx); pt.graphicalProperties.solidFill = col
    dn.series[0].data_points.append(pt)
ws.add_chart(dn, "A21")

# Bar: Top-Segmente
bc = BarChart(); bc.type = "bar"; bc.title = "Top-Segmente nach Volumen CHF"; bc.height = 7.0; bc.width = 7.4; bc.legend = None
bref = Reference(ws, min_col=HB + 1, min_row=11, max_row=seg_top_end)
bcat = Reference(ws, min_col=HB, min_row=12, max_row=seg_top_end)
bc.add_data(bref, titles_from_data=True); bc.set_categories(bcat)
bc.series[0].graphicalProperties.solidFill = C_VERT
ws.add_chart(bc, "E21")

# Bar: DC-Report-Volumen nach Region (aus Global Analytics-Datenbasis, live)
rc = BarChart(); rc.type = "col"; rc.title = "Global Report-Vol. (Mrd $) je Region"; rc.height = 7.0; rc.width = 7.4; rc.legend = None
put(ws, 11, HB + 3, "Region", font=F_KPI_L); put(ws, 11, HB + 4, "Mrd$", font=F_KPI_L)
regs_dash = ["NAM", "EUROPE", "ASIA", "AUSPAC", "LAM", "MIDDLE EAST", "AFRICA"]
for i, rg in enumerate(regs_dash):
    put_text(ws, 12 + i, HB + 3, rg)
    put(ws, 12 + i, HB + 4, f'=SUMIF({GPS}!$K$5:$K$20000,{get_column_letter(HB+3)}{12+i},{GPS}!$E$5:$E$20000)/1000000000', fmt="#,##0.0")
reg_end = 12 + len(regs_dash) - 1
# Helferspalten sichtbar (Charts brauchen sichtbare Quellzellen)
rref = Reference(ws, min_col=HB + 4, min_row=11, max_row=reg_end)
rcat = Reference(ws, min_col=HB + 3, min_row=12, max_row=reg_end)
rc.add_data(rref, titles_from_data=True); rc.set_categories(rcat)
rc.series[0].graphicalProperties.solidFill = C_GLOB
ws.add_chart(rc, "I21")

put(ws, 36, 1, "SCHNELLZUGRIFF", font=Font(name=FONT, bold=True, size=12, color=C_NAV))
links = [("02_PIPELINE", "Pipeline"), ("03_KUNDEN_CRM", "CRM / Zielkunden"),
         ("05_FORECAST", "Forecast"), ("06_MONATSREPORT", "Monatsreport"),
         ("07_CEO_REPORT", "CEO-Report"), ("27_AKTIONEN", "Aktions-Zentrale"),
         ("28_ZIELE", "Ziel-Tracker"), ("29_KALENDER", "Kalender / Wiedervorlage"),
         ("22_ANGEBOT_KALK", "Angebot / Offerte"), ("11_DC_BAUPROJEKTE", "DC-Bauprojekte"),
         ("15_GLOBAL_PROJEKTE", "Globale Projekte"), ("90_IMPORT", "Daten importieren")]
for i, (tab, label) in enumerate(links):
    r, c = 37 + i // 3, 1 + (i % 3) * 4
    ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + 3)
    put(ws, r, c, f'=HYPERLINK("#\'{tab}\'!A1","→ {label}")', font=F_LINK)
for i in range(1, 13):
    ws.column_dimensions[get_column_letter(i)].width = 12.5
for rr in (4, 8, 12, 16):
    ws.row_dimensions[rr].height = 20
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 100
setup_print(ws, titles=None)
ws.print_area = "A1:M44"

# ============================================================================
# 00_START
# ============================================================================
ws = wb.create_sheet("00_START", 0)
ws.sheet_properties.tabColor = C_NAV
ws.sheet_view.showGridLines = False
for col, w in zip("ABCDEFG", [3, 22, 34, 58, 13, 13, 3]):
    ws.column_dimensions[col].width = w
ws.merge_cells("B2:F2")
put(ws, 2, 2, "MiT × AGGREKO — GESAMTMAPPE 2026", font=Font(size=22, bold=True, color="FFFFFF"),
    fill=C_NAV, align=A_CENTER)
ws.row_dimensions[2].height = 40
ws.merge_cells("B3:F3")
put(ws, 3, 2, "Ein Workspace statt 1000 Dateien  ·  Vertrieb Strom CH  ·  Datacenter CH & Global  ·  Produkte & Preise  ·  Werkzeuge",
    font=Font(size=11, color="D9D9D9"), fill=C_NAV, align=A_CENTER)
ws.row_dimensions[3].height = 20
put(ws, 5, 2, "NAVIGATION", font=Font(size=13, bold=True, color="262626"))
nav = [
    ("VERTRIEB STROM CH", C_VERT, [
        ("01_DASHBOARD", "Alle Kennzahlen auf einen Blick (live)"),
        ("02_PIPELINE", "Deals & Forecast — hier neue Aufträge erfassen"),
        ("03_KUNDEN_CRM", "Zielkunden-Datenbank Schweiz (798 Firmen)"),
        ("04_KUNDENKARTEI", "Alle CH-Kunden & Kontakte (1'100+), verknüpft mit Pipeline"),
        ("05_FORECAST", "Auswertung nach Status / Segment / Kanton (live)"),
        ("06_MONATSREPORT", "Monatsbericht — per Ctrl+Shift+M als neue Mappe exportieren"),
        ("07_CEO_REPORT", "CEO Sales Report — WON/Offerte/Opportunität als Druckansicht"),
        ("08_DIAGRAMME", "Diagramme (Status, Segmente, Kantone) — aktualisieren sich automatisch"),
        ("09_KUNDENANALYSE", "Kundenanalyse RSRG (Vorlage)"),
    ]),
    ("DATACENTER SCHWEIZ", C_DC, [
        ("10_DC_BETREIBER", "30 DC-Betreiber CH — Master-Daten"),
        ("11_DC_BAUPROJEKTE", "Bauprojekte 2026-28, konsolidiert aus 3 Quellen"),
        ("12_DC_STANDORTE", "Adressbuch aller DC-Standorte"),
        ("13_DC_KONTAKTE", "Entscheider-CRM Datacenter"),
        ("14_DC_DOSSIERS", "Dossiers Implenia & FlexBase TZL"),
    ]),
    ("GLOBAL", C_GLOB, [
        ("15_GLOBAL_PROJEKTE", "10'572 DC-Projekte weltweit"),
        ("16_GLOBAL_KONTAKTE", "8'502 Ansprechpartner weltweit"),
        ("17_GLOBAL_ANALYTICS", "Region × Status × Jahr — live"),
    ]),
    ("PRODUKTE & PREISE", C_PROD, [
        ("18_KATALOG", "466 Produkte Aggreko/MiT"),
        ("19_PREISLISTE_CHF", "Tagespreise Schweiz + Wochen-/Monatspreis"),
        ("20_PREISLISTE_INTL", "Aggreko Weekly Rates (vertraulich)"),
    ]),
    ("WERKZEUGE", C_TOOL, [
        ("21_GEN_RECHNER", "Generator-Auslegung (Lastliste → Empfehlung)"),
        ("22_ANGEBOT_KALK", "Angebots-Kalkulator mit Preisliste-Dropdown"),
        ("23_MARKTVOLUMEN", "Marktvolumen-Szenarien DC Schweiz"),
        ("24_NORMEN", "Normen & Compliance (17 Standards)"),
        ("25_AKQUISE_90T", "90-Tage-Akquiseplan"),
        ("26_SYSTEME_WISSEN", "Technik-Wissen Kombinationssysteme"),
        ("27_AKTIONEN", "Aktions-Zentrale — offene To-Dos & Follow-ups gebündelt"),
        ("28_ZIELE", "Ziel-Tracker — Soll/Ist, Zielerreichung als Gauge"),
        ("29_KALENDER", "Kalender & Wiedervorlagen — Fälligkeits-Ampel, +14-Tage-Makro"),
    ]),
    ("SYSTEM", C_SYS, [
        ("90_IMPORT", "IMPORT-ZENTRALE — neue Dateien automatisch verteilen"),
        ("91_LISTEN", "Dropdown-Quellen & Lookups"),
        ("99_INFO", "Dokumentation der Gesamtmappe"),
    ]),
]
r = 6
for bereich, farbe, tabs in nav:
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    put(ws, r, 2, bereich, font=F_SECT, fill=farbe)
    r += 1
    for tab, desc in tabs:
        put(ws, r, 2, f'=HYPERLINK("#\'{tab}\'!A1","{tab}")', font=F_LINK)
        put(ws, r, 3, desc, font=Font(size=10, color="404040"))
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
        r += 1
r += 1
ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
if OHNE_MAKROS:
    put(ws, r, 2, "ℹ MAKROFREIE VERSION (.xlsx) — läuft ohne jede Sicherheitswarnung", font=F_SECT, fill="1F4E79")
else:
    put(ws, r, 2, "⚠ FALLS EXCEL MELDET: 'Ein potenziell gefährliches Makro wurde blockiert'", font=F_SECT, fill="C00000")
r += 1
if OHNE_MAKROS:
    motw = [
        "Diese Version enthält KEINE Makros — Excel zeigt keine Warnung, alles ist sofort nutzbar:",
        "Alle 30 Reiter, sämtliche Formeln, Verknüpfungen, Dropdowns, Filter, Diagramme, Berichte — 100% funktionsfähig.",
        "Nur die Automatik-Funktionen (Ctrl+Shift+I Import, Ctrl+Shift+M Monatsreport-Export) gibt es ausschliesslich",
        "in der Vollversion 'MiT_GESAMTMAPPE_2026.xlsm' (Freischaltung: siehe Reiter 99_INFO).",
        "Neue Daten kannst du hier ganz normal von Hand anhängen: unten in der jeweiligen Liste weiterschreiben oder einfügen.",
    ]
else:
    motw = [
        "Das ist Microsofts Standard-Sperre für Dateien aus dem Internet. DREI Wege, sie EINMALIG zu lösen:",
        "WEG 1 (normaler PC):  Excel schliessen → Explorer → RECHTSKLICK auf die Datei → Eigenschaften →",
        "     unten Haken bei „Zulassen / Unblock“ setzen → OK → Datei öffnen → „Inhalt aktivieren“ klicken.",
        "WEG 2 (Firmen-PC / kein 'Zulassen'-Haken sichtbar):  Excel → Datei → Optionen → Trust Center →",
        "     Einstellungen für das Trust Center → Vertrauenswürdige Speicherorte → Neuen Speicherort hinzufügen →",
        "     deinen Ordner (z.B. C:\\MiT) wählen → OK. Datei in diesen Ordner legen → öffnen. Sperre weg — dauerhaft.",
        "WEG 3:  Die Datei als ZIP erhalten und mit 7-Zip/WinRAR entpacken — dann setzt Windows die Sperre gar nicht erst.",
        "Auch OHNE Makros funktioniert alles Übrige zu 100%: alle Reiter, Formeln, Verknüpfungen, Dropdowns, Filter, Diagramme.",
        "Zusätzlich liegt eine komplett makrofreie Version bei: MiT_GESAMTMAPPE_2026_OHNE_MAKROS.xlsx (keinerlei Warnung).",
    ]
for h in motw:
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    put(ws, r, 2, h, font=Font(size=10, bold=h.startswith("Excel"), color="9C0006"))
    r += 1
r += 1
ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
put(ws, r, 2, "IMPORT & AUTOMATIK (nach Makro-Freigabe)", font=F_SECT, fill="C00000")
r += 1
hinweise = [
    "Ctrl+Shift+I  →  Excel-Datei importieren: Inhalte werden erkannt und automatisch auf die richtigen Reiter verteilt.",
    "Unbekannte Blätter werden automatisch als neues rotes Blatt (IMP ...) angelegt — nichts geht verloren.",
    "Ctrl+Shift+M  →  Monatsreport als NEUE Arbeitsmappe erzeugen (automatisch gespeichert).",
    "Ctrl+Shift+B  →  Neues leeres Listen-Blatt anlegen.",
    "Alternativ: Alt+F8 → Makro 'MIT_Import' / 'MIT_NeuerMonatsreport' / 'MIT_NeuesBlatt' starten.",
    "Details & Protokoll: Reiter 90_IMPORT.",
]
for h in hinweise:
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    put(ws, r, 2, "•  " + h, font=Font(size=10, color="404040"))
    r += 1

# ============================================================================
# 90_IMPORT
# ============================================================================
ws = wb.create_sheet("90_IMPORT")
ws.sheet_properties.tabColor = C_SYS
titel_zeilen(ws, C_SYS, "IMPORT-ZENTRALE — neue Dateien automatisch verteilen",
             "Steuerung der automatischen Import-Funktion (VBA). Erkennungsregeln unten anpassbar.", 11)
anleitung = [
    "SO FUNKTIONIERT DER IMPORT:",
    "1.  Ctrl+Shift+I drücken (oder Alt+F8 → 'MIT_Import') und die neue Excel-Datei wählen.",
    "2.  Jedes Blatt der Datei wird geprüft: Passt die Kopfzeile zu einer Regel unten, werden die Zeilen",
    "     an den Ziel-Reiter ANGEHÄNGT. Duplikate (gleicher Schlüssel) werden übersprungen.",
    "3.  Spalten werden über die Kopfzeilen-Namen zugeordnet (Alias-Tabelle rechts: fremde Namen → unsere Namen).",
    "4.  Unbekannte Blätter werden automatisch als NEUES BLATT (rot, 'IMP ...') in diese Mappe kopiert.",
    "5.  Jeder Import wird unten im Protokoll dokumentiert.",
]
for i, t in enumerate(anleitung):
    put(ws, 4 + i, 1, t, font=Font(size=10, bold=(i == 0), color="404040"))
    ws.merge_cells(start_row=4 + i, start_column=1, end_row=4 + i, end_column=8)

put(ws, 11, 1, "ERKENNUNGSREGELN (Zeile 12 ff. — VBA liest diese Tabelle)", font=F_SECT, fill=C_SYS)
ws.merge_cells("A11:H11")
map_hdr = ["Aktiv", "Erkennung 1 (Headertext)", "Erkennung 2 (Headertext)", "Ziel-Reiter",
           "Schlüssel-Spalten (Dedup, ;-getrennt)", "Formel-Spalten (;-getrennt)", "Modus", "Hinweis"]
for i, h in enumerate(map_hdr, start=1):
    put(ws, 12, i, h, font=F_HDR, fill=C_SYS, border=B_ALL,
        align=Alignment(horizontal="center", wrap_text=True))
regeln = [
    ("JA", "Kunde / Unternehmen", "Volumen", "02_PIPELINE", "Kunde / Unternehmen;Leistung / Fleet", "A;O;P;Q;Y", "Anhängen", "Strom-Pipeline (alle Varianten)"),
    ("JA", "Firmenname", "Prio", "03_KUNDEN_CRM", "Firmenname", "A;W", "Anhängen", "CRM-Zielkunden"),
    ("JA", "Kunde / Unternehmen", "Ansprechperson", "04_KUNDENKARTEI", "Kunde / Unternehmen", "A;H;I", "Anhängen", "Kundenkartei / Customer Overview"),
    ("JA", "Betreiber", "IT-MW", "10_DC_BETREIBER", "Betreiber", "", "Anhängen", "DC-Betreiber"),
    ("JA", "Projekt / Ort", "GU / TU", "11_DC_BAUPROJEKTE", "Projekt / Ort", "A", "Anhängen", "Bauprojekte"),
    ("JA", "Code", "Standortname", "12_DC_STANDORTE", "Code", "", "Anhängen", "DC-Standorte"),
    ("JA", "Unternehmen", "Produkt-Fokus", "13_DC_KONTAKTE", "Unternehmen;Name", "", "Anhängen", "DC-Kontakte"),
    ("JA", "Projektname", "Report Value", "15_GLOBAL_PROJEKTE", "ID", "", "Anhängen", "Globale Projekte (deutsch)"),
    ("JA", "Project Name", "Country", "15_GLOBAL_PROJEKTE", "ID", "", "Anhängen", "Globale Projekte (engl. Tracker)"),
    ("JA", "Projekt-ID", "Nachname", "16_GLOBAL_KONTAKTE", "Projekt-ID;Nachname;E-Mail", "", "Anhängen", "Globale Kontakte (deutsch)"),
    ("JA", "Project ID", "Contact First Name", "16_GLOBAL_KONTAKTE", "Projekt-ID;Nachname;E-Mail", "", "Anhängen", "Globale Kontakte (engl. Tracker)"),
    ("JA", "ITEM CODE / MOVEX", "KATEGORIE", "18_KATALOG", "ITEM CODE / MOVEX;BEZEICHNUNG", "", "Anhängen", "Produktkatalog"),
    ("JA", "Produktname", "Tagespreis", "19_PREISLISTE_CHF", "Produktname", "G;H", "Anhängen", "Preisliste CHF"),
    ("JA", "Generic_Code__c", "Weekly Floor", "20_PREISLISTE_INTL", "Generic_Code__c;Division Name", "", "Anhängen", "Preisliste International"),
    ("JA", "Woche", "Kanal", "25_AKQUISE_90T", "Woche;Aktion", "", "Anhängen", "Akquise-Plan"),
    ("JA", "Norm", "DC-Relevanz", "24_NORMEN", "Norm / Standard", "", "Anhängen", "Normen-Matrix"),
]
for i, regel in enumerate(regeln):
    r = 13 + i
    for j, v in enumerate(regel, start=1):
        put_text(ws, r, j, v, border=B_ALL)
dv = DataValidation(type="list", formula1='"JA,NEIN"', allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"A13:A40")

put(ws, 11, 10, "ALIAS-TABELLE (fremder Header → unser Header)", font=F_SECT, fill=C_SYS)
ws.merge_cells(start_row=11, start_column=10, end_row=11, end_column=11)
put(ws, 12, 10, "Fremder Header", font=F_HDR, fill=C_SYS, border=B_ALL)
put(ws, 12, 11, "Unser Header", font=F_HDR, fill=C_SYS, border=B_ALL)
aliase = [
    # Pipeline-Varianten
    ("Kanton", "Kt."), ("Equipment CHF", "Equip. CHF"), ("Treibstoff CHF", "Treibst. CHF"),
    ("Techniker CHF", "Technik. CHF"), ("Gew. Wert CHF", "Gew.Wert CHF"), ("Wahrsch. %", "Wahr. %"),
    ("Akquis. Typ", "Akquise Typ"), ("USP-Argument (Unique Selling Proposition)", "USP-Argument"),
    ("Dauer", "Dauer (Tage)"), ("#", "Nr."),
    # CRM
    ("Firmenname *", "Firmenname"),
    # Kartei
    ("Kt.", "Kanton"), ("Telefon", "Tel. Nr"), ("Status", "Pipeline Status"),
    # Global Tracker (englisch)
    ("Source", "Quelle"), ("Project Name", "Projektname"), ("Project Value ($)", "Projektwert ($)"),
    ("Report Value", "Report Value ($)"), ("Sectors", "Sektor"), ("Revised Status", "Status"),
    ("Country", "Land"), ("State", "Region/Staat"), ("Construction Start Year", "Baustart-Jahr"),
    ("Comissioning Year", "Inbetriebnahme-Jahr"), ("Main Company", "Hauptfirma"),
    ("Latitude", "Lat"), ("Longitude", "Lon"), ("Project Summary", "Projektbeschreibung"),
    ("Project ID", "Projekt-ID"), ("CONT_TITLE", "Titel/Funktion"),
    ("Contact First Name", "Vorname"), ("Contact Second Name", "Nachname"),
    ("CONT_PHONE", "Telefon"), ("CONT_EMAIL", "E-Mail"), ("LINKEDIN", "LinkedIn"),
    ("Project Responsibility", "Verantwortung"), ("CMP_NAME", "Firma"), ("CMP_ADDR1", "Adresse"),
    ("CMP_ZIP", "PLZ"), ("CMP_CITY", "Stadt"), ("CMP_STATE", "Region"), ("CMP_CNTRY", "Land"),
    # Betreiber / Standorte / Kontakte / Akquise
    ("Code CH", "Standort-Code CH"), ("Kt", "Kanton"), ("Prioritaet MiT", "Priorität MiT"),
    ("Vorgaenger", "Vorgänger"), ("Eigentuemer", "Eigentümer"), ("Kuehlung", "Kühlung"),
    ("Standortname", "Standortname / Projekt"), ("Strasse + Nr.", "Strasse"),
    ("Eroeffn.", "Status"), ("GPS (approx.)", "GPS"), ("Entfernung Thayngen", "Entf. Thayngen"),
    ("Besonderheit", "Besonderheit / GU"),
    ("E-Mail/Website", "E-Mail / Tel."), ("Kontext", "Kontext / Besonderheit"),
    ("Ziel", "Ziel-Unternehmen"), ("Produkt", "MiT-Produkt"), ("CHF-Pot.", "CHF-Potential"),
    ("Naechste Aktion", "Nächste Aktion"), ("Pruef-Frequenz", "Prüf-Frequenz"),
    ("Pflicht?", "Pflicht/Optional"),
]
for i, (a, b) in enumerate(aliase):
    put_text(ws, 13 + i, 10, a, border=B_ALL)
    put_text(ws, 13 + i, 11, b, border=B_ALL)

log_r = 13 + len(regeln) + 2
put(ws, log_r, 1, "IMPORT-PROTOKOLL (VBA schreibt hier automatisch)", font=F_SECT, fill=C_SYS)
ws.merge_cells(start_row=log_r, start_column=1, end_row=log_r, end_column=8)
for i, h in enumerate(["Zeitpunkt", "Datei", "Blatt", "Ziel-Reiter", "Neu", "Duplikate", "Aktion", ""], start=1):
    if h:
        put(ws, log_r + 1, i, h, font=F_HDR, fill=C_SYS, border=B_ALL)
for col, w in zip("ABCDEFGHIJK", [8, 26, 24, 20, 34, 22, 12, 34, 3, 38, 26]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A4"

# ============================================================================
# 99_INFO
# ============================================================================
ws = wb.create_sheet("99_INFO")
ws.sheet_properties.tabColor = C_SYS
titel_zeilen(ws, C_SYS, "DOKUMENTATION — MiT Gesamtmappe 2026", f"Version 1.0 · erstellt {HEUTE}", 3)
info = [
    ("KONZEPT", ""),
    ("", "Diese Mappe ersetzt alle Einzeldateien: 15 Quelldateien wurden zusammengeführt, dedupliziert und logisch auf Reiter verteilt."),
    ("", "Eingabe-Reiter (Daten pflegen): 02, 03, 04, 10, 11, 12, 13, 18, 19, 20, 23, 25."),
    ("", "Auswertungs-Reiter (nur lesen, rechnet live): 00, 01, 05, 06, 07, 08, 17."),
    ("", "Wissens-Reiter (statisch): 09, 14, 24, 26."),
    ("DATENFLÜSSE", ""),
    ("", "02_PIPELINE → 01_DASHBOARD, 05_FORECAST, 06_MONATSREPORT, 07_CEO_REPORT, 08_DIAGRAMME, 04_KUNDENKARTEI."),
    ("", "03_KUNDEN_CRM → 05_FORECAST (CRM-Forecast), 01_DASHBOARD."),
    ("", "15_GLOBAL_PROJEKTE + 16_GLOBAL_KONTAKTE → 17_GLOBAL_ANALYTICS, 01_DASHBOARD."),
    ("", "19_PREISLISTE_CHF → 22_ANGEBOT_KALK (Dropdown + Tagespreis-Lookup)."),
    ("", "91_LISTEN → alle Dropdowns (Status, Segmente, Kantone, Produkte, Generator-Grössen)."),
    ("IMPORT", ""),
    ("", "Ctrl+Shift+I: Datei wählen → Blätter werden per Kopfzeilen-Erkennung den Ziel-Reitern zugeordnet und angehängt."),
    ("", "Duplikate werden über Schlüssel-Spalten erkannt und übersprungen (Regeln: Reiter 90_IMPORT)."),
    ("", "Unbekannte Blätter → automatisch neues rotes Blatt 'IMP ...' (nichts geht verloren)."),
    ("", "Ctrl+Shift+M: Monatsreport als neue Arbeitsmappe (Werte eingefroren) im gleichen Ordner speichern."),
    ("", "Ctrl+Shift+B: neues leeres Listen-Blatt.  ·  Ctrl+Shift+F: Suche über die ganze Mappe."),
    ("", "Ctrl+Shift+D: alle Berichte als EIN PDF.  ·  Ctrl+Shift+G: neuer Deal (Maske).  ·  Ctrl+Shift+K: neuer Kunde (Maske)."),
    ("", "Ctrl+Shift+W: markierte Kalenderzeilen auf +14 Tage.  ·  Ctrl+Shift+O: Offerte als PDF.  ·  Ctrl+Shift+N: neue Offerte."),
    ("KONVENTIONEN", ""),
    ("", "Alle Listen-Reiter: Zeile 1 Titel, Zeile 2 Navigation, Zeile 4 Kopfzeile, Daten ab Zeile 5."),
    ("", "Spalten mit '_' (z.B. _Rang) sind interne Hilfsspalten — nicht löschen, sind ausgeblendet."),
    ("", "Formel-Spalten (Marge, Gew.Wert, Nr., ✓, Wochen-/Monatspreis) nicht überschreiben — sie füllen sich selbst."),
    ("", "Blaue Felder in 21_GEN_RECHNER und 22_ANGEBOT_KALK sind Eingabefelder."),
    ("QUELLDATEIEN (in dieser Mappe aufgegangen)", ""),
]
quellen = [
    "Aggreko_MiT_Master_Katalog_v1.xlsx → 18_KATALOG (466 Produkte)",
    "MiT_CRM_Vorlage_Final.xlsx (2 Versionen, gemerged) → 03_KUNDEN_CRM (798 Firmen)",
    "CH_Customer_Monthly_Report_Mai_26.xlsx → 04_KUNDENKARTEI, 02_PIPELINE (Merge), 06_MONATSREPORT",
    "CH_MiT_Strom_Customer.xlsx + CEO_CFO (2 Versionen) → 02_PIPELINE (47 Deals, dedupliziert)",
    "Datacenter.xlsx + MiT_Aggreko_DC_Suite_2026.xlsx → 13/14/15_GLOBAL_*, 08/10/11_DC_*",
    "Data_Centre_Project_Tracker_March_2026_Final.xlsm → gleiche Datenbasis wie DC-Suite (10'572 Projekte)",
    "MiT_DC_GESAMTMAPPE_2026_FIXED.xlsx → 11_DC_BAUPROJEKTE, 14_DC_DOSSIERS, 23_MARKTVOLUMEN u.a.",
    "Zusammenfassung_Bauprojekte.xlsx → 11_DC_BAUPROJEKTE (Merge, inkl. Abgeschlossen/Verantwortlich)",
    "202605_MIT_PriceList_CHF.xlsx → 19_PREISLISTE_CHF · MIT_PriceList_Confidential.xlsx → 20_PREISLISTE_INTL",
    "RSRG_Kundenanalyse_MiT_2026.xlsx → 09_KUNDENANALYSE",
]
r = 4
for a, b in info:
    if a:
        put(ws, r, 1, a, font=F_SECT, fill=C_SYS)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
    else:
        put(ws, r, 2, b, font=Font(size=10, color="404040"))
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    r += 1
for q in quellen:
    put(ws, r, 2, "• " + q, font=Font(size=10, color="404040"))
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    r += 1
ws.column_dimensions["A"].width = 4
ws.column_dimensions["B"].width = 120

# ============================================================================
# 27_AKTIONEN  (Aktions-Zentrale — was ist als Nächstes zu tun?)
# ============================================================================
ws = wb.create_sheet("27_AKTIONEN")
ws.sheet_properties.tabColor = C_TOOL
titel_zeilen(ws, C_TOOL, "AKTIONS-ZENTRALE — To-Do & Follow-ups",
             "Bündelt offene Deals, Akquise-Aufgaben und Prio-A-Kunden. Alles live aus den Daten-Reitern.", 12)
AK = "'25_AKQUISE_90T'"
active_cond = (f'({PR}!$R$5:$R$2000<>"WON")*({PR}!$R$5:$R$2000<>"LOST")'
               f'*({PR}!$R$5:$R$2000<>"Declined")*({PR}!$R$5:$R$2000<>"")')

TILE_ACCENT[0] = C_TOOL; TILE_IDX[0] = 0
tile(ws, 4, 1, "Aktive Deals", f'=SUMPRODUCT({active_cond})')
tile(ws, 4, 3, "Offerten offen",
     f'=COUNTIF({PR}!$R$5:$R$2000,"offered")+COUNTIF({PR}!$R$5:$R$2000,"to be offered")')
tile(ws, 4, 5, "Akquise offen/heute",
     f'=COUNTIF({AK}!$H$5:$H$500,"OFFEN")+COUNTIF({AK}!$H$5:$H$500,"HEUTE!")+COUNTIF({AK}!$H$5:$H$500,"LÄUFT")')
tile(ws, 4, 7, "Prio-A CRM offen",
     f'=COUNTIFS({CR}!$B$5:$B$3000,"A",{CR}!$M$5:$M$3000,"offen")')
tile(ws, 4, 9, "Offene Pipeline CHF",
     f'=SUMIF({PR}!$R$5:$R$2000,"<>",{PR}!$I$5:$I$2000)-SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$I$5:$I$2000)-SUMIF({PR}!$R$5:$R$2000,"LOST",{PR}!$I$5:$I$2000)-SUMIF({PR}!$R$5:$R$2000,"Declined",{PR}!$I$5:$I$2000)')
tile(ws, 4, 11, "DC-Bauprojekte offen",
     f'=COUNTIF(\'11_DC_BAUPROJEKTE\'!$B$5:$B$300,"OFFEN")+COUNTIF(\'11_DC_BAUPROJEKTE\'!$B$5:$B$300,"IN KONTAKT")')

# Block A: aktive Pipeline-Deals (nach Volumen)
r0 = 7
ws.merge_cells(start_row=r0, start_column=1, end_row=r0, end_column=8)
put(ws, r0, 1, "AKTIVE PIPELINE-DEALS — nach Volumen (Top 30)", font=F_SECT, fill=C_TOOL)
a_hdr = ["#", "Kunde / Unternehmen", "Kt.", "Status", "Volumen CHF", "Wahr. %",
         "Nächster Schritt", "Follow-Up", "_v"]
for i, h in enumerate(a_hdr, start=1):
    put(ws, r0 + 1, i, h, font=F_HDR, fill=C_TOOL, border=B_ALL,
        align=Alignment(horizontal="center", wrap_text=True))
YR2 = f"{PR}!$AD$5:$AD$2000"   # _ACT-Rangspalte
a_first = r0 + 2
for k in range(1, 31):
    r = a_first + k - 1
    put(ws, r, 9, f'=IFERROR(LARGE({YR2},{k}),"")', border=B_ALL)
    put(ws, r, 1, f'=IF($I{r}="","",{k})', border=B_ALL)
    m = f'MATCH($I{r},{YR2},0)'
    put(ws, r, 2, f'=IF($I{r}="","",IFERROR(INDEX({PR}!$B$5:$B$2000,{m}),""))', border=B_ALL)
    put(ws, r, 3, f'=IF($I{r}="","",IFERROR(INDEX({PR}!$C$5:$C$2000,{m}),""))', border=B_ALL, align=A_CENTER)
    put(ws, r, 4, f'=IF($I{r}="","",IFERROR(INDEX({PR}!$R$5:$R$2000,{m}),""))', border=B_ALL)
    put(ws, r, 5, f'=IF($I{r}="","",IFERROR(INDEX({PR}!$I$5:$I$2000,{m}),""))', fmt=NF, border=B_ALL)
    put(ws, r, 6, f'=IF($I{r}="","",IFERROR(INDEX({PR}!$S$5:$S$2000,{m}),""))', fmt=PCT, border=B_ALL)
    put(ws, r, 7, f'=IF($I{r}="","",IFERROR(INDEX({PR}!$V$5:$V$2000,{m}),""))', border=B_ALL)
    put(ws, r, 8, f'=IF($I{r}="","",IFERROR(INDEX({PR}!$W$5:$W$2000,{m}),""))', border=B_ALL)
a_last = a_first + 29
ws.conditional_formatting.add(f"E{a_first}:E{a_last}",
    DataBarRule(start_type="min", end_type="max", color=BAR[C_TOOL]))
ws.conditional_formatting.add(f"F{a_first}:F{a_last}",
    IconSetRule("3TrafficLights1", "percent", [0, 34, 67], showValue=True))
ws.conditional_formatting.add(f"D{a_first}:D{a_last}", FormulaRule(
    formula=['EXACT($D'+str(a_first)+',"offered")'],
    fill=PatternFill("solid", fgColor="FFEB9C"), font=Font(color="9C6500", bold=True)))

# Block B: Akquise-Aufgaben (Mirror, nur nicht-erledigte)
b0 = a_last + 2
ws.merge_cells(start_row=b0, start_column=1, end_row=b0, end_column=8)
put(ws, b0, 1, "AKQUISE-AUFGABEN — offen / heute / läuft (aus 25_AKQUISE_90T)", font=F_SECT, fill=C_TOOL)
b_hdr = ["Woche", "Aktion", "Kanal", "MiT-Produkt", "Deadline", "Status", "CHF-Potential", "Ziel"]
for i, h in enumerate(b_hdr, start=1):
    put(ws, b0 + 1, i, h, font=F_HDR, fill=C_TOOL, border=B_ALL,
        align=Alignment(horizontal="center", wrap_text=True))
b_first = b0 + 2
srcmap = [1, 2, 5, 6, 9, 8, 10, 7]  # Spalten in 25_AKQUISE_90T
for idx in range(30):
    src = 5 + idx
    r = b_first + idx
    cond = f'OR({AK}!$H{src}="ERLEDIGT",{AK}!$H{src}="",{AK}!$B{src}="")'
    for ci, sc in enumerate(srcmap, start=1):
        col = get_column_letter(sc)
        fmt = NF if sc == 10 else "General"
        put(ws, r, ci, f'=IF({cond},"",{AK}!${col}{src})', fmt=fmt, border=B_ALL,
            align=A_CENTER if ci in (1, 5, 6) else None)
b_last = b_first + 29
ws.conditional_formatting.add(f"F{b_first}:F{b_last}", FormulaRule(
    formula=['EXACT($F'+str(b_first)+',"HEUTE!")'],
    fill=PatternFill("solid", fgColor="FFC7CE"), font=Font(color="9C0006", bold=True)))
ws.conditional_formatting.add(f"G{b_first}:G{b_last}",
    DataBarRule(start_type="min", end_type="max", color=BAR[C_TOOL]))

ws.column_dimensions["I"].hidden = True
for col, w in zip("ABCDEFGHI", [5, 32, 6, 14, 12, 9, 40, 13, 6]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A5"
ws.sheet_view.showGridLines = False
setup_print(ws)

# ============================================================================
# 28_ZIELE  (Ziel-Tracker: Soll/Ist + Gauge)
# ============================================================================
from openpyxl.chart import DoughnutChart as _Doughnut
ws = wb.create_sheet("28_ZIELE")
ws.sheet_properties.tabColor = C_TOOL
titel_zeilen(ws, C_TOOL, "ZIEL-TRACKER — Soll / Ist & Zielerreichung",
             "Blaue Felder = Ziel eingeben. Ist-Umsatz (WON) kommt automatisch aus 02_PIPELINE.", 12)
F_INP = Font(name=FONT, color="0563C1", bold=True)
FILL_INP = PatternFill("solid", fgColor="DDEBF7")
IST_WON = f'SUMIF({PR}!$R$5:$R$2000,"WON",{PR}!$I$5:$I$2000)'
# Eingabe Jahresziel
put(ws, 4, 1, "Jahresziel CHF (Eingabe)", font=Font(name=FONT, bold=True))
ws.merge_cells("A4:B4")
put(ws, 4, 3, 3000000, font=F_INP, fill=FILL_INP, fmt=NF, border=B_ALL)
ws.merge_cells("C4:D4")
# KPI-Karten
TILE_ACCENT[0] = C_TOOL; TILE_IDX[0] = 0
tile(ws, 6, 1, "Jahresziel CHF", "=$C$4")
tile(ws, 6, 3, "Ist WON CHF", f"={IST_WON}")
tile(ws, 6, 5, "Erreicht %", f"=IFERROR({IST_WON}/$C$4,0)", fmt="0.0%")
tile(ws, 6, 7, "Rest bis Ziel CHF", f"=MAX($C$4-{IST_WON},0)")
tile(ws, 6, 9, "Ø Marge % (WON)",
     f'=IFERROR(AVERAGEIFS({PR}!$P$5:$P$2000,{PR}!$R$5:$R$2000,"WON"),0)', fmt="0.0%")
tile(ws, 6, 11, "Deals gewonnen", f'=COUNTIF({PR}!$R$5:$R$2000,"WON")')
# Gauge-Daten (versteckt)
GH = 30
put(ws, 5, GH, "Erreicht", font=F_KPI_L); put(ws, 5, GH + 1, f"=MIN({IST_WON},$C$4)", fmt=NF)
put(ws, 6, GH, "Rest", font=F_KPI_L); put(ws, 6, GH + 1, f"=MAX($C$4-{IST_WON},0)", fmt=NF)
# Gauge-Helferspalten sichtbar (sonst plottet der Doughnut nicht)
gg = _Doughnut(); gg.title = "Zielerreichung"; gg.holeSize = 62; gg.height = 7.5; gg.width = 11
gref = Reference(ws, min_col=GH + 1, min_row=5, max_row=6)
gcat = Reference(ws, min_col=GH, min_row=5, max_row=6)
gg.add_data(gref, titles_from_data=False); gg.set_categories(gcat)
for idx, col in enumerate(["70AD47", "E0E0E0"]):
    pt = DataPoint(idx=idx); pt.graphicalProperties.solidFill = col
    gg.series[0].data_points.append(pt)
ws.add_chart(gg, "A9")

# Ziel je Segment
put(ws, 9, 5, "ZIEL JE SEGMENT (Ziel blau eingeben — Ist & % rechnen automatisch)", font=F_SECT, fill=C_TOOL)
ws.merge_cells(start_row=9, start_column=5, end_row=9, end_column=12)
zhdr = ["Segment", "Ziel CHF", "Ist WON CHF", "Erreicht %", "Balken"]
for i, h in enumerate(zhdr, start=5):
    put(ws, 10, i, h, font=F_HDR, fill=C_TOOL, border=B_ALL, align=A_CENTER)
zseg = seg_union
z_first = 11
for i, sg in enumerate(zseg):
    r = z_first + i
    put_text(ws, r, 5, sg, border=B_ALL)
    put(ws, r, 6, 0, font=F_INP, fill=FILL_INP, fmt=NF, border=B_ALL)
    put(ws, r, 7, f'=SUMIFS({PR}!$I$5:$I$2000,{PR}!$D$5:$D$2000,$E{r},{PR}!$R$5:$R$2000,"WON")', fmt=NF, border=B_ALL)
    put(ws, r, 8, f'=IFERROR($G{r}/$F{r},"")' if False else f'=IF($F{r}=0,"",IFERROR($G{r}/$F{r},0))', fmt="0.0%", border=B_ALL)
    put(ws, r, 9, f'=IF($F{r}=0,"",REPT("|",MIN(ROUND(IFERROR($G{r}/$F{r},0)*20,0),40)))',
        font=Font(name=FONT, color=C_TOOL), border=B_ALL)
z_last = z_first + len(zseg) - 1
put(ws, z_last + 1, 5, "TOTAL", font=Font(name=FONT, bold=True), border=B_ALL)
put(ws, z_last + 1, 6, f"=SUM(F{z_first}:F{z_last})", font=Font(name=FONT, bold=True), fmt=NF, border=B_ALL)
put(ws, z_last + 1, 7, f"=SUM(G{z_first}:G{z_last})", font=Font(name=FONT, bold=True), fmt=NF, border=B_ALL)
ws.conditional_formatting.add(f"H{z_first}:H{z_last}", ColorScaleRule(
    start_type="num", start_value=0, start_color="F8696B",
    mid_type="num", mid_value=0.5, mid_color="FFEB84",
    end_type="num", end_value=1, end_color="63BE7B"))
# Ziel-vs-Ist Balkendiagramm
zc = BarChart(); zc.type = "bar"; zc.title = "Ziel vs. Ist je Segment"; zc.height = 9; zc.width = 16
zc.grouping = "clustered"
d1 = Reference(ws, min_col=6, min_row=10, max_row=z_last)
d2 = Reference(ws, min_col=7, min_row=10, max_row=z_last)
zcat = Reference(ws, min_col=5, min_row=z_first, max_row=z_last)
zc.add_data(d1, titles_from_data=True); zc.add_data(d2, titles_from_data=True); zc.set_categories(zcat)
zc.series[0].graphicalProperties.solidFill = "BFBFBF"
zc.series[1].graphicalProperties.solidFill = C_TOOL
ws.add_chart(zc, "A26")
for col, w in zip("ABCDEFGHIJKL", [16, 10, 12, 12, 24, 13, 14, 11, 22, 4, 4, 4]):
    ws.column_dimensions[col].width = w
ws.sheet_view.showGridLines = False
setup_print(ws, titles=None)
ws.print_area = "A1:L45"

# ============================================================================
# 29_KALENDER  (Termin- / Wiedervorlage-Planer mit Fälligkeits-Ampel)
# ============================================================================
ws = wb.create_sheet("29_KALENDER")
ws.sheet_properties.tabColor = C_TOOL
titel_zeilen(ws, C_TOOL, "KALENDER — Termine & Wiedervorlagen",
             "Fällig am eingeben → Ampel automatisch. Ctrl+Shift+W = markierte Zeilen auf +14 Tage. Startzeilen aus aktiver Pipeline.", 8)
KL = 3000
DR = 7   # erste Datenzeile (KPI-Karten belegen 4-5, Kopf 6)
# Zähler-Karten
TILE_ACCENT[0] = C_TOOL; TILE_IDX[0] = 0
tile(ws, 4, 1, "Überfällig", f'=SUMPRODUCT((A{DR}:A{KL}<>"")*(A{DR}:A{KL}<TODAY()))', span=2)
tile(ws, 4, 3, "Heute", f'=SUMPRODUCT((A{DR}:A{KL}=TODAY())*1)', span=2)
tile(ws, 4, 5, "Diese Woche", f'=SUMPRODUCT((A{DR}:A{KL}>=TODAY())*(A{DR}:A{KL}<=TODAY()+7))', span=2)
tile(ws, 4, 7, "Offen gesamt", f'=SUMPRODUCT((A{DR}:A{KL}<>"")*1)-SUMPRODUCT((UPPER(F{DR}:F{KL})="ERLEDIGT")*1)', span=1)
kl_hdr = ["Fällig am", "Prio", "Kunde / Thema", "Nächster Schritt / Notiz", "Kanal", "Status", "Verantwortlich", "Quelle"]
for i, h in enumerate(kl_hdr, start=1):
    put(ws, 6, i, h, font=F_HDR, fill=C_TOOL, border=B_ALL, align=A_CENTER)
# Startzeilen aus aktiver Pipeline (statisch, editierbar)
aktive = [d for d in pipe_rows
          if str(d.get("Status") or "").strip() not in ("WON", "LOST", "Declined", "")]
kl_row = DR
for d in aktive[:60]:
    put(ws, kl_row, 1, None, fmt="DD.MM.YYYY", border=B_ALL)  # Datum: User füllt
    prio = "A" if str(d.get("Status")) in ("offered", "to be offered") else "B"
    put_text(ws, kl_row, 2, prio, border=B_ALL, align=A_CENTER)
    put_text(ws, kl_row, 3, d.get("Kunde / Unternehmen"), border=B_ALL)
    put_text(ws, kl_row, 4, d.get("Nächster Schritt"), border=B_ALL)
    put_text(ws, kl_row, 5, d.get("Akquise Typ"), border=B_ALL)
    put_text(ws, kl_row, 6, "offen", border=B_ALL, align=A_CENTER)
    put_text(ws, kl_row, 7, "Burak", border=B_ALL, align=A_CENTER)
    put_text(ws, kl_row, 8, "Pipeline", border=B_ALL, align=A_CENTER)
    kl_row += 1
# leere editierbare Zeilen mit Rahmen
for r in range(kl_row, kl_row + 40):
    for c in range(1, 9):
        cc = ws.cell(row=r, column=c); cc.border = B_ALL
        if c == 1:
            cc.number_format = "DD.MM.YYYY"
kl_last = kl_row + 39
# Ampel auf 'Fällig am'
ws.conditional_formatting.add(f"A{DR}:A{kl_last}", FormulaRule(
    formula=[f'AND($A{DR}<>"",$A{DR}<TODAY(),UPPER($F{DR})<>"ERLEDIGT")'],
    fill=PatternFill("solid", fgColor="FFC7CE"), font=Font(color="9C0006", bold=True)))
ws.conditional_formatting.add(f"A{DR}:A{kl_last}", FormulaRule(
    formula=[f'AND($A{DR}<>"",$A{DR}>=TODAY(),$A{DR}<=TODAY()+7,UPPER($F{DR})<>"ERLEDIGT")'],
    fill=PatternFill("solid", fgColor="FFEB9C"), font=Font(color="9C6500", bold=True)))
ws.conditional_formatting.add(f"A{DR}:A{kl_last}", FormulaRule(
    formula=[f'AND($A{DR}<>"",$A{DR}>TODAY()+7)'],
    fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(color="006100")))
ws.conditional_formatting.add(f"F{DR}:F{kl_last}", FormulaRule(
    formula=[f'EXACT($F{DR},"erledigt")'], fill=PatternFill("solid", fgColor="E2EFDA"),
    font=Font(color="375623", italic=True)))
dv = DataValidation(type="list", formula1='"offen,in Arbeit,erledigt,verschoben"', allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f"F{DR}:F{kl_last}")
dv2 = DataValidation(type="list", formula1='"A,B,C"', allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv2); dv2.add(f"B{DR}:B{kl_last}")
ws.freeze_panes = f"A{DR}"
ws.auto_filter.ref = f"A6:H{kl_last}"
for col, w in zip("ABCDEFGH", [12, 6, 32, 44, 16, 12, 13, 10]):
    ws.column_dimensions[col].width = w
ws.sheet_view.showGridLines = False
setup_print(ws)

# ============================================================================
# Reihenfolge der Reiter korrigieren + definierte Namen
# ============================================================================
order = ["00_START", "01_DASHBOARD", "02_PIPELINE", "03_KUNDEN_CRM", "04_KUNDENKARTEI",
         "05_FORECAST", "06_MONATSREPORT", "07_CEO_REPORT", "08_DIAGRAMME",
         "09_KUNDENANALYSE", "10_DC_BETREIBER",
         "11_DC_BAUPROJEKTE", "12_DC_STANDORTE", "13_DC_KONTAKTE", "14_DC_DOSSIERS",
         "15_GLOBAL_PROJEKTE", "16_GLOBAL_KONTAKTE", "17_GLOBAL_ANALYTICS", "18_KATALOG",
         "19_PREISLISTE_CHF", "20_PREISLISTE_INTL", "21_GEN_RECHNER", "22_ANGEBOT_KALK",
         "23_MARKTVOLUMEN", "24_NORMEN", "25_AKQUISE_90T", "26_SYSTEME_WISSEN",
         "27_AKTIONEN", "28_ZIELE", "29_KALENDER",
         "90_IMPORT", "91_LISTEN", "99_INFO"]
wb._sheets = [wb[n] for n in order]
wb.active = 0

# Globaler Feinschliff: Gridlines aus + druckfertig auf JEDER Seite
for ws in wb.worksheets:
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 100
    if ws.page_setup.orientation is None:
        ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)

wb.save(OUT_FILE)
print(f"OK -> {OUT_FILE}")
print(f"Sheets: {len(wb.sheetnames)}")
