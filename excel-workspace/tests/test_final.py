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

check("Alpha in Pipeline Zeile 52", cell(pipe, 1, 51) == "TEST Kunde Alpha AG", f"-> {cell(pipe,1,51)!r}")
check("Beta in Pipeline Zeile 53", cell(pipe, 1, 52) == "TEST Kunde Beta GmbH")
check("Kanton-Alias (Kt.=BE)", cell(pipe, 2, 51) == "BE")
check("kein Ice-Hockey-Duplikat", cell(pipe, 1, 53) == "")
marge = pipe.getCellByPosition(14, 51).getValue()   # O52: 42000-24800
check("Marge-Formel Zeile 52 rechnet", abs(marge - 16200) < 0.01, f"-> {marge}")
gew = pipe.getCellByPosition(16, 51).getValue()     # Q52: 42000*0.6
check("Gew.Wert-Formel Zeile 52", abs(gew - 25200) < 0.01, f"-> {gew}")
nr = pipe.getCellByPosition(0, 51).getValue()       # A52 = 48
check("Nr.-Formel Zeile 52", nr == 48, f"-> {nr}")
check("Gamma im CRM Zeile 803", cell(crm, 3, 802) == "TEST Datacenter Gamma AG")
wahr = crm.getCellByPosition(19, 802).getValue()
check("Prozent-Normalisierung (25 -> 0.25)", abs(wahr - 0.25) < 1e-9, f"-> {wahr}")
gewfc = crm.getCellByPosition(22, 802).getValue()
check("CRM Gew.Forecast rechnet (37500)", abs(gewfc - 37500) < 0.01, f"-> {gewfc}")
log1 = cell(imp, 6, 32)  # G33 Aktion
check("Protokoll Zeile 33 'angehängt'", log1 == "angehängt", f"-> {log1!r}")
check("Protokoll Neu=2", cell(imp, 4, 32) == "2")
check("Protokoll Duplikate=1", cell(imp, 5, 32) == "1")

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
