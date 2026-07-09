#!/usr/bin/env python3
"""Finale End-to-End-Testsuite für die MiT-Gesamtmappe (.xlsm) in LibreOffice.

A) Import bekannter Blätter (Pipeline + CRM): Zeilen, Duplikate, Aliase, Formeln
B) Import unbekanntes Blatt -> automatisch neues rotes Blatt 'IMP ...'
C) MIT_NeuerMonatsreport -> neue Arbeitsmappe wird automatisch erstellt
"""
import os, subprocess, sys, time
import uno
from com.sun.star.beans import PropertyValue

S = os.path.dirname(os.path.abspath(__file__))
XLSM = os.path.join(S, "MiT_GESAMTMAPPE_2026.xlsm")
FAILS = []

def check(name, cond, info=""):
    status = "OK  " if cond else "FAIL"
    print(f"  [{status}] {name} {info}")
    if not cond:
        FAILS.append(name)

def pv(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v
    return p

# unbekanntes Blatt vorbereiten
import openpyxl
wbu = openpyxl.Workbook()
wsu = wbu.active
wsu.title = "Kraut und Rueben"
wsu["A1"] = "Völlig unbekannte Struktur"
wsu["A2"] = "Spalte X"; wsu["B2"] = "Spalte Y"
wsu["A3"] = 1; wsu["B3"] = "foo"
wbu.save(os.path.join(S, "testunknown.xlsx"))

subprocess.run(["pkill", "-f", "soffice.bin"], capture_output=True)
time.sleep(2)
proc = subprocess.Popen(["soffice", "--headless", "--norestore", "--invisible",
    "--accept=socket,host=localhost,port=2002;urp;"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
local = uno.getComponentContext()
resolver = local.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver", local)
ctx = None
for i in range(60):
    try:
        ctx = resolver.resolve(
            "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
        break
    except Exception:
        time.sleep(1)
smgr = ctx.ServiceManager
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
doc = desktop.loadComponentFromURL("file://" + XLSM, "_blank", 0,
                                   (pv("MacroExecutionMode", 4), pv("Hidden", True)))
sp = doc.getScriptProvider()

def vba(name, args=()):
    sc = sp.getScript(f"vnd.sun.star.script:VBAProject.Modul_Import.{name}?language=Basic&location=document")
    return sc.invoke(args, (), ())

def vbaW(name, args=()):
    sc = sp.getScript(f"vnd.sun.star.script:VBAProject.Modul_Werkzeuge.{name}?language=Basic&location=document")
    return sc.invoke(args, (), ())

print("== A) Import bekannter Blätter (direkter Aufruf mit 2 Argumenten)")
vba("MIT_ImportDatei", (os.path.join(S, "testimport.xlsx"), True))
doc.calculateAll()
sheets = doc.getSheets()
pipe = sheets.getByName("02_PIPELINE")
crm = sheets.getByName("03_KUNDEN_CRM")
imp = sheets.getByName("90_IMPORT")

def cell(sh, col, row):   # 0-basiert
    c = sh.getCellByPosition(col, row)
    s = c.getString()
    return s

def find_row(sh, col, value, r0=4, r1=1300):
    for r in range(r0, r1):
        if cell(sh, col, r) == value:
            return r
    return -1

def find_contains(sh, col, needle, r0=4, r1=1300):
    for r in range(r0, r1):
        if needle in cell(sh, col, r):
            return r
    return -1

# Zeilen dynamisch suchen (Offerten verschieben feste Indizes)
a = find_row(pipe, 1, "TEST Kunde Alpha AG")
check("Alpha in Pipeline", a >= 0, f"-> Zeile {a+1}")
b = find_row(pipe, 1, "TEST Kunde Beta GmbH")
check("Beta in Pipeline", b >= 0, f"-> Zeile {b+1}")
check("Kanton-Alias (Kt.=BE)", a >= 0 and cell(pipe, 2, a) == "BE")
# Duplikat: Ice Hockey darf nur EINMAL vorkommen (kein zweiter Eintrag)
ice = sum(1 for r in range(4, 120) if cell(pipe, 1, r) == "Ice Hockey Championship")
check("kein Ice-Hockey-Duplikat", ice == 1, f"-> {ice}x")
if a >= 0:
    marge = pipe.getCellByPosition(14, a).getValue()   # O: 42000-25800
    check("Marge-Formel (Alpha) rechnet", abs(marge - 16200) < 0.01, f"-> {marge}")
    gew = pipe.getCellByPosition(16, a).getValue()     # Q: 42000*0.6
    check("Gew.Wert-Formel (Alpha)", abs(gew - 25200) < 0.01, f"-> {gew}")
    nr = pipe.getCellByPosition(0, a).getValue()       # A = ROW()-4
    check("Nr.-Formel (Alpha) rechnet", nr == (a + 1 - 4), f"-> {nr}")
g = find_row(crm, 3, "TEST Datacenter Gamma AG")
check("Gamma im CRM", g >= 0, f"-> Zeile {g+1}")
if g >= 0:
    wahr = crm.getCellByPosition(19, g).getValue()
    check("Prozent-Normalisierung (25 -> 0.25)", abs(wahr - 0.25) < 1e-9, f"-> {wahr}")
    gewfc = crm.getCellByPosition(22, g).getValue()
    check("CRM Gew.Forecast rechnet (37500)", abs(gewfc - 37500) < 0.01, f"-> {gewfc}")

print("== D) Offerten-Import -> Register + Auto-Verteilung Pipeline/CRM")
off = sheets.getByName("35_OFFERTEN")
opos = sheets.getByName("36_OFFERTEN_POSITIONEN")
check("Offerte OF-TEST-9001 im Register 35", find_row(off, 1, "OF-TEST-9001") >= 0)
op = find_contains(pipe, 23, "OF-TEST-9001")   # Notiz intern (Spalte X = idx 23)
check("Offerte als Deal in 02_PIPELINE", op >= 0, f"-> Zeile {op+1}")
if op >= 0:
    volp = pipe.getCellByPosition(8, op).getValue()   # Volumen CHF = Netto
    check("Offerten-Deal Volumen = Netto (12345)", abs(volp - 12345) < 0.01, f"-> {volp}")
    check("Offerten-Deal Status offered", cell(pipe, 17, op) == "offered", f"-> {cell(pipe,17,op)!r}")
check("Offerten-Kunde im 03_KUNDEN_CRM", find_row(crm, 3, "TEST Offerten Kunde AG") >= 0)
check("Offerten-Positionen in 36 (>=2)",
      sum(1 for r in range(4, 200) if cell(opos, 1, r) == "OF-TEST-9001") >= 2)
# gebaute 3 Offerten wurden am Ende nicht dupliziert (Dedup)
agro = sum(1 for r in range(4, 120) if cell(pipe, 1, r) == "Eidg. Departement WBF – Agroscope")
check("keine Doppel-Verteilung gebauter Offerten", agro == 1, f"-> {agro}x")
# Protokoll dynamisch finden: Zeile mit "Zeitpunkt" in Spalte A, erste Datenzeile danach
log_hdr = None
for rr in range(19, 80):
    if cell(imp, 0, rr) == "Zeitpunkt":
        log_hdr = rr
        break
check("Protokoll-Kopf gefunden", log_hdr is not None, f"-> Zeile {None if log_hdr is None else log_hdr+1}")
lr = (log_hdr + 1) if log_hdr is not None else 32   # erste Datenzeile (0-basiert)
log1 = cell(imp, 6, lr)  # Aktion
check("Protokoll erste Zeile 'angehängt'", log1 == "angehängt", f"-> {log1!r}")
check("Protokoll Neu=2", cell(imp, 4, lr) == "2")
check("Protokoll Duplikate=1", cell(imp, 5, lr) == "1")

print("== B) Unbekanntes Blatt -> neues Blatt")
n_before = sheets.getCount()
vba("MIT_ImportDatei", (os.path.join(S, "testunknown.xlsx"), True))
n_after = sheets.getCount()
check("neues Blatt angelegt", n_after == n_before + 1, f"{n_before}->{n_after}")
names = list(sheets.getElementNames())
imp_sheets = [n for n in names if n.startswith("IMP ")]
check("Blattname 'IMP ...'", len(imp_sheets) == 1, f"-> {imp_sheets}")
if imp_sheets:
    neu = sheets.getByName(imp_sheets[0])
    check("Inhalt kopiert", neu.getCellByPosition(0, 0).getString().startswith("Völlig"))

print("== C) Monatsreport -> neue Arbeitsmappe")
report = os.path.join(S, f"MiT_Monatsreport_{time.strftime('%Y_%m')}.xlsx")
if os.path.exists(report):
    os.remove(report)
try:
    vbaW("MIT_NeuerMonatsreport")
except Exception as e:
    print("   (Exception beim Aufruf:", str(e)[:120], ")")
time.sleep(2)
check("Monatsreport-Datei erstellt", os.path.exists(report), f"-> {report}")

doc.close(False)
try:
    desktop.terminate()
except Exception:
    pass
try:
    proc.wait(timeout=60)
except Exception:
    pass
# Inhalt prüfen — LO speichert BIFF (in Excel: echtes xlsx); xlrd liest beides nicht,
# daher: BIFF via xlrd
time.sleep(2)
try:
    import xlrd
    wbr = xlrd.open_workbook(report)
    names = wbr.sheet_names()
    check("Report enthält 2 Blätter", sorted(names) == ["01_DASHBOARD", "06_MONATSREPORT"], f"-> {names}")
    wsr = wbr.sheet_by_name("06_MONATSREPORT")
    gross = [wsr.cell_value(r, c) for r in range(min(wsr.nrows, 30)) for c in range(min(wsr.ncols, 10))
             if isinstance(wsr.cell_value(r, c), float) and wsr.cell_value(r, c) > 1000]
    check("Report-KPIs eingefroren (Werte vorhanden)", len(gross) >= 3, f"-> {gross[:4]}")
except Exception as e:
    check("Report lesbar", False, f"-> {e}")

print()
print("ERGEBNIS:", "ALLE TESTS OK" if not FAILS else f"{len(FAILS)} FEHLER: {FAILS}")
sys.exit(1 if FAILS else 0)
