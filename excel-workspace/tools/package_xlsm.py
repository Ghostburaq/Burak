#!/usr/bin/env python3
"""Packt vbaProject.bin in die .xlsx und erzeugt die finale .xlsm."""
import re, shutil, zipfile

SRC = "MiT_GESAMTMAPPE_2026.xlsx"
BIN = "vbaProject.bin"
OUT = "MiT_GESAMTMAPPE_2026.xlsm"

zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED)

for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename == "[Content_Types].xml":
        s = data.decode("utf-8")
        s = s.replace(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
            "application/vnd.ms-excel.sheet.macroEnabled.main+xml")
        assert "macroEnabled" in s
        s = s.replace("</Types>",
                      '<Default Extension="bin" ContentType="application/vnd.ms-office.vbaProject"/></Types>')
        data = s.encode("utf-8")
    elif item.filename == "xl/_rels/workbook.xml.rels":
        s = data.decode("utf-8")
        # freie rId ermitteln
        ids = [int(m) for m in re.findall(r'Id="rId(\d+)"', s)]
        rid = max(ids) + 1 if ids else 1
        rel = (f'<Relationship Id="rId{rid}" '
               f'Type="http://schemas.microsoft.com/office/2006/relationships/vbaProject" '
               f'Target="vbaProject.bin"/>')
        s = s.replace("</Relationships>", rel + "</Relationships>")
        data = s.encode("utf-8")
    elif item.filename == "xl/workbook.xml":
        s = data.decode("utf-8")
        if "<workbookPr" in s:
            s = re.sub(r"<workbookPr", '<workbookPr codeName="ThisWorkbook"', s, count=1)
        else:
            # nach fileVersion einfügen, sonst direkt nach <workbook ...>
            if "</fileVersion>" in s or "<fileVersion" in s:
                s = re.sub(r"(<fileVersion[^>]*/>)", r'\1<workbookPr codeName="ThisWorkbook"/>', s, count=1)
            else:
                s = re.sub(r"(<workbook[^>]*>)", r'\1<workbookPr codeName="ThisWorkbook"/>', s, count=1)
        assert 'codeName="ThisWorkbook"' in s
        data = s.encode("utf-8")
    zout.writestr(item, data)

zout.write(BIN, "xl/vbaProject.bin")
zout.close()
zin.close()
print(f"OK -> {OUT}")

# Verifikation
import openpyxl
wb = openpyxl.load_workbook(OUT, keep_vba=True)
print("openpyxl liest xlsm:", len(wb.sheetnames), "Sheets")
from oletools.olevba import VBA_Parser
p = VBA_Parser(OUT)
mods = [m for (_, _, m, _) in p.extract_all_macros()]
print("olevba findet Module in xlsm:", mods)
assert "Modul_Import" in " ".join(mods)
print("XLSM-PAKET OK")
