#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLOCK 2 — Gewichtete Pipeline transparent.

2.1  Im CEO Report (Abschnitt 4, gewichtete Bandtabelle) wird die
     gewichtete Pipeline zerlegt: «davon gewonnene Aufträge (Faktor
     100 %)» und «davon offene Offerten (Aggreko-Faktoren)» — beide als
     Formel; ihre Summe muss die TOTAL-Zeile ergeben (Statuszeile).
2.2  Kontrollrechnung: die gewichtete Summe zweimal unabhängig —
     SUMME über Spalte Q und SUMMENPRODUKT über Volumen und Faktor.
     Weicht das Ergebnis um mehr als CHF 1 ab, erscheint im CEO Report
     eine rote Warnung (bedingte Formatierung, keine Handpflege).
2.3  Executive PDF als Einseiter (A4 hoch): Auftragseingang, gewichtete
     Pipeline mit Zerlegung, Nachweisquote, Top-5-Offerten nach Volumen,
     offene Punkte. Dafuer neue versteckte Hilfsspalte BD (_OffertSort)
     in der Pipeline — Formeln, keine Festwerte.

Regel 1 bleibt unberuehrt: die Bandtabelle B17:D22 wird nicht angefasst.
"""
import copy
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from ausbau_util import DATEI, merge, unmerge_bereich, raum_leeren, sp

wb = openpyxl.load_workbook(DATEI)
ceo = wb['CEO Report']
pdf = wb['📑 Executive PDF']
pipe = wb['MiT Strom Pipeline']

WON_GEW = f'=SUMPRODUCT({sp("AP")},--({sp("R")}="WON"),{sp("AJ")},{sp("AL")})'
OFF_GEW = f'=SUMPRODUCT({sp("AP")},--({sp("R")}<>"WON"),{sp("AJ")},{sp("AL")})'
WON_N = f'=SUMPRODUCT({sp("AP")},--({sp("R")}="WON"))'
OFF_N = f'=SUMPRODUCT({sp("AP")},--({sp("R")}<>"WON"))'
WON_UMS = f'=SUMIFS({sp("I")},{sp("R")},"WON")'
OFF_UMS = f'=SUMPRODUCT({sp("AP")},--({sp("R")}<>"WON"),{sp("AL")})'

# ================================================= Hilfsspalte BD (Pipeline)
assert pipe['BD5'].value is None and pipe['BD6'].value is None
kopf_muster = pipe['AK5']
pipe['BD5'] = '_OffertSort'
pipe['BD5']._style = copy.copy(kopf_muster._style)
for r in range(6, 861):
    pipe[f'BD{r}'] = (f'=IF(AND(ISNUMBER(I{r}),OR(R{r}="offered",R{r}="to be offered")),'
                      f'AL{r}+(861-ROW())*0.000001,"")')
pipe.column_dimensions['BD'].hidden = True
pipe.column_dimensions['BD'].width = 13.0

# ============================================ 2.1 Zerlegung (CEO, 215–217)
assert ceo['A206'].value.startswith('⚖️') and ceo['A213'].value == 'TOTAL aktive Pipeline'
for r in (215, 216, 217):
    for c in range(1, 15):
        assert ceo.cell(row=r, column=c).value is None

DUENN = Side(style='thin', color='FFB8C2CC')
RAHMEN = Border(left=DUENN, right=DUENN, top=DUENN, bottom=DUENN)
ZEILE = PatternFill('solid', fgColor='FFF8FAFC')
TOTAL = PatternFill('solid', fgColor='FFDDE5EF')

def wert(ws, koord, inhalt, fmt='General', fett=False, farbe='FF111111',
         fuellung=ZEILE, horizontal='left', groesse=10, wrap=False, font='Arial'):
    z = ws[koord]
    z.value = inhalt
    z.font = Font(name=font, size=groesse, bold=fett, color=farbe)
    z.fill = fuellung
    z.number_format = fmt
    z.alignment = Alignment(horizontal=horizontal, vertical='center', wrap_text=wrap)
    z.border = RAHMEN
    return z

ZERLEGUNG = [
    (215, 'davon gewonnene Aufträge (Faktor 100 %)', '1.0', WON_N, WON_UMS, WON_GEW),
    (216, 'davon offene Offerten (Aggreko-Faktoren 0 / 30 / 50 / 90 %)', '0 – 0.9',
     OFF_N, OFF_UMS, OFF_GEW),
]
for r, label, faktor, f_n, f_u, f_g in ZERLEGUNG:
    wert(ceo, f'A{r}', label, fett=True); merge(ceo, f'A{r}:C{r}')
    wert(ceo, f'D{r}', faktor, horizontal='center')
    wert(ceo, f'E{r}', f_n, fmt='0', horizontal='center')
    wert(ceo, f'F{r}', f_u, fmt='#,##0', horizontal='right')
    wert(ceo, f'G{r}', f_g, fmt='#,##0', fett=True, farbe='FF1F3864', horizontal='right')
    merge(ceo, f'G{r}:H{r}')
    wert(ceo, f'I{r}', f'=IFERROR(G{r}/$G$213,0)', fmt='0.0%', horizontal='right')
    ceo.row_dimensions[r].height = 18

wert(ceo, 'A217', 'Summe der Zerlegung — muss die TOTAL-Zeile ergeben',
     fett=True, fuellung=TOTAL)
merge(ceo, 'A217:F217')
wert(ceo, 'G217', '=G215+G216', fmt='#,##0', fett=True, farbe='FF1F3864',
     fuellung=TOTAL, horizontal='right')
merge(ceo, 'G217:H217')
wert(ceo, 'I217',
     '=IF(ROUND(G215+G216-G213,2)=0,"✔  Zerlegung = TOTAL","⛔  Abweichung: "'
     '&TEXT(G215+G216-G213,"#,##0.00")&" CHF")',
     groesse=9, fett=True, fuellung=TOTAL, wrap=True)
merge(ceo, 'I217:N217')
ceo.row_dimensions[217].height = 18
ceo.conditional_formatting.add(
    'I217', FormulaRule(formula=['ABS($G$215+$G$216-$G$213)>0.005'], stopIfTrue=True,
                        font=Font(name='Arial', size=9, bold=True, color='FFFFFFFF'),
                        fill=PatternFill('solid', bgColor='FFC00000')))

# ==================================== 2.2 Kontrollrechnung (CEO, 262–267)
fuss = ceo['A262'].value
assert isinstance(fuss, str) and fuss.startswith('="Stand: ')
fuss_font = copy.copy(ceo['A262'].font)
fuss_align = copy.copy(ceo['A262'].alignment)
ceo.unmerge_cells('A262:L262')
ceo['A262'] = None

GRUEN = PatternFill('solid', fgColor='FF166534')
KOPF = PatternFill('solid', fgColor='FF1E273A')

z = ceo['A262']
z.value = '🧮  8. KONTROLLRECHNUNG — gewichtete Summe zweimal unabhängig'
z.font = Font(name='Arial', size=11, bold=True, color='FFFFFFFF')
z.fill = GRUEN
z.alignment = Alignment(horizontal='left', vertical='center')
merge(ceo, 'A262:N262')
ceo.row_dimensions[262].height = 24

for koord, text, harmon in (('A263', 'Rechenweg', 'left'),
                            ('E263', 'Gewichtet CHF', 'center'),
                            ('F263', 'Erläuterung', 'left')):
    z = ceo[koord]
    z.value = text
    z.font = Font(name='Arial', size=9, bold=True, color='FFFFFFFF')
    z.fill = KOPF
    z.alignment = Alignment(horizontal=harmon, vertical='center')
merge(ceo, 'A263:D263')
merge(ceo, 'F263:L263')
ceo.row_dimensions[263].height = 19.5

KONTROLLE = [
    (264, 'Weg 1 — SUMME über die gewichtete Spalte Q',
     f'=SUM({sp("Q")})',
     'Addiert die fertig gerechneten Gewichtungswerte der Pipeline (Spalte Q «Gew.Wert»).'),
    (265, 'Weg 2 — SUMMENPRODUKT über Volumen × Faktor',
     f'=SUMPRODUCT({sp("AL")},{sp("AJ")})',
     'Rechnet unabhängig davon: Volumen (Spalte I, numerisch als AL) mal Gewichtungsfaktor (AJ) — ohne die Spalte Q zu benutzen.'),
    (266, 'Abweichung (muss 0 sein)',
     '=ROUND(E264-E265,2)',
     'Beide Wege müssen denselben Betrag ergeben; erlaubte Toleranz: CHF 1.'),
]
for r, label, f, erkl in KONTROLLE:
    wert(ceo, f'A{r}', label, fett=(r == 266)); merge(ceo, f'A{r}:D{r}')
    wert(ceo, f'E{r}', f, fmt='#,##0.00', fett=True, farbe='FF1F3864',
         horizontal='right')
    wert(ceo, f'F{r}', erkl, groesse=9, farbe='FF555555', wrap=True)
    merge(ceo, f'F{r}:L{r}')
    ceo.row_dimensions[r].height = 19.5

wert(ceo, 'A267',
     '=IF(ABS(E266)>1,"⛔  WARNUNG: Die gewichtete Summe weicht zwischen den beiden '
     'Rechenwegen um "&TEXT(ABS(E266),"#,##0.00")&" CHF ab — Ursache suchen, niemals '
     'die Zahl anpassen.","✔  Kontrolle bestanden: beide Rechenwege ergeben denselben '
     'Betrag — die gewichtete Pipeline ist konsistent.")',
     groesse=10, fett=True, fuellung=TOTAL)
merge(ceo, 'A267:N267')
ceo.row_dimensions[267].height = 18
ceo.conditional_formatting.add(
    'A267', FormulaRule(formula=['ABS($E$266)>1'], stopIfTrue=True,
                        font=Font(name='Arial', size=10, bold=True, color='FFFFFFFF'),
                        fill=PatternFill('solid', bgColor='FFC00000')))

ceo['A269'] = fuss
ceo['A269'].font = fuss_font
ceo['A269'].alignment = fuss_align
merge(ceo, 'A269:L269')
ceo.row_dimensions[269].height = 13.5
ceo.print_area = "'CEO Report'!$A$1:$N$269"

# ========================================= 2.3 Executive PDF — Einseiter
# Zeilen 12–47 werden neu aufgebaut; Kopf (1–10) und Fusszeile (49) bleiben.
unmerge_bereich(pdf, 11, 48)
raum_leeren(pdf, 11, 48, 1, 9)

TITELBLAU = 'FF1F3864'
P_KOPF = PatternFill('solid', fgColor=TITELBLAU)
P_ZEILE = PatternFill('solid', fgColor='FFF8FAFC')
P_ORANGE = PatternFill('solid', fgColor='FFF47B20')

def p_titel(koord, text):
    z = pdf[koord]
    z.value = text
    z.font = Font(name='Calibri', size=13, bold=True, color=TITELBLAU)
    z.alignment = Alignment(horizontal='left', vertical='center')

def p_kopf(koord, text, horizontal='center'):
    z = pdf[koord]
    z.value = text
    z.font = Font(name='Cambria', size=10, bold=True, color='FFFFFFFF')
    z.fill = P_KOPF
    z.alignment = Alignment(horizontal=horizontal, vertical='center')

def p_wert(koord, inhalt, fmt='General', fett=False, farbe='FF111111',
           fuellung=P_ZEILE, horizontal='left', groesse=11, wrap=False):
    z = pdf[koord]
    z.value = inhalt
    z.font = Font(name='Calibri', size=groesse, bold=fett, color=farbe)
    if fuellung is not None:
        z.fill = fuellung
    z.number_format = fmt
    z.alignment = Alignment(horizontal=horizontal, vertical='center', wrap_text=wrap)
    return z

# Kopfzeile 10: brutto und bereinigt nebeneinander (1.3), gewichtet folgt unten.
pdf['B10'] = ('="📊  PIPELINE brutto: "&TEXT(SUMPRODUCT(' + sp('AP') + ',' + sp('AL') +
              '),"#,##0")&" CHF  ·  bereinigt: "&TEXT(SUMPRODUCT(' + sp('AP') + ',' +
              sp('AU') + ',' + sp('AL') + '),"#,##0")&" CHF  ·  "&SUMPRODUCT(' +
              sp('AP') + ')&" Deals"')
pdf['B10'].font = Font(name='Calibri', size=12, bold=True, color='FFFFFFFF')
merge(pdf, 'B10:H10')

# --- ⚖️ Gewichtete Pipeline — Zerlegung -------------------------- 12–17
p_titel('B12', '⚖️  Gewichtete Pipeline — Zerlegung (Aggreko-Faktoren)')
merge(pdf, 'B12:G12')
pdf.row_dimensions[12].height = 16.5
p_kopf('B13', 'Position', 'left'); merge(pdf, 'B13:E13')
p_kopf('F13', 'Deals')
p_kopf('G13', 'Gewichtet CHF'); merge(pdf, 'G13:H13')
PDF_ZER = [
    (14, 'Gewichtete Pipeline TOTAL (aktiv)', f"='⚖️ Wahrscheinlichkeit'!$E$22",
     f"='⚖️ Wahrscheinlichkeit'!$G$22", True),
    (15, 'davon gewonnene Aufträge (Faktor 100 %)', WON_N, WON_GEW, False),
    (16, 'davon offene Offerten (Faktoren 0 / 30 / 50 / 90 %)', OFF_N, OFF_GEW, False),
]
for r, label, f_n, f_g, fett in PDF_ZER:
    p_wert(f'B{r}', label, fett=fett); merge(pdf, f'B{r}:E{r}')
    p_wert(f'F{r}', f_n, fmt='0', horizontal='center')
    p_wert(f'G{r}', f_g, fmt='#,##0', fett=True, farbe=TITELBLAU, horizontal='right')
    merge(pdf, f'G{r}:H{r}')
    pdf.row_dimensions[r].height = 15
p_wert('B17',
       '=IF(ROUND(G15+G16-G14,2)=0,"✔  Kontrolle: WON + offene Offerten = TOTAL — '
       'die Zerlegung geht exakt auf.","⛔  Kontrolle verletzt: Zerlegung weicht um "'
       '&TEXT(G15+G16-G14,"#,##0.00")&" CHF vom TOTAL ab — Ursache klären.")',
       groesse=10, farbe='FF166534', fuellung=None)
merge(pdf, 'B17:H17')
pdf.row_dimensions[17].height = 15
pdf.conditional_formatting.add(
    'B17', FormulaRule(formula=['ABS($G$15+$G$16-$G$14)>0.005'], stopIfTrue=True,
                       font=Font(name='Calibri', size=10, bold=True, color='FFFFFFFF'),
                       fill=PatternFill('solid', bgColor='FFC00000')))

# --- 📋 Qualität & Nachweis --------------------------------------- 19–26
p_titel('B19', '📋  Qualität & Nachweis — WON gemeldet vs. belegt')
merge(pdf, 'B19:G19')
pdf.row_dimensions[19].height = 16.5
p_kopf('B20', 'Kennzahl', 'left'); merge(pdf, 'B20:E20')
p_kopf('F20', 'Anzahl')
p_kopf('G20', 'CHF'); merge(pdf, 'G20:H20')
PDF_QN = [
    (21, 'WON gemeldet (brutto, wie erfasst)',
     f'=COUNTIF({sp("R")},"WON")', WON_UMS, '#,##0', True),
    (22, 'davon belegt (PO-Nr. + Belegdatum + vollst. Einstand)',
     f'=SUMPRODUCT({sp("AT")})',
     f'=SUMPRODUCT({sp("AT")},{sp("AL")})', '#,##0', False),
    (23, 'noch zu belegen',
     '=F21-F22', '=G21-G22', '#,##0', False),
    (24, 'Nachweisquote (CHF)', '', '=IFERROR(G22/G21,0)', '0.0%', True),
    (25, 'Deals mit erfasstem Projektzeitraum',
     '', f'=SUMPRODUCT({sp("AP")},{sp("AY")})&" von "&SUMPRODUCT({sp("AP")})',
     'General', False),
]
for r, label, f_n, f_g, fmt, fett in PDF_QN:
    p_wert(f'B{r}', label, fett=fett); merge(pdf, f'B{r}:E{r}')
    p_wert(f'F{r}', f_n if f_n else None, fmt='0', horizontal='center')
    p_wert(f'G{r}', f_g, fmt=fmt, fett=fett, farbe=TITELBLAU, horizontal='right')
    merge(pdf, f'G{r}:H{r}')
    pdf.row_dimensions[r].height = 15

# --- 🏆 Top 5 offene Offerten ------------------------------------- 27–33
p_titel('B27', '🏆  Top 5 offene Offerten (nach Volumen)')
merge(pdf, 'B27:G27')
pdf.row_dimensions[27].height = 16.5
for koord, text, harmon in (('B28', '#', 'center'), ('C28', 'Kunde', 'left'),
                            ('D28', 'Kt.', 'center'), ('E28', 'Projektstart', 'center'),
                            ('F28', 'Projektende', 'center'), ('G28', 'Volumen', 'right'),
                            ('H28', 'Segment', 'left')):
    p_kopf(koord, text, harmon)
pdf.row_dimensions[28].height = 15

BD = f"{sp('BD')}"
def top(col_bereich, k):
    return (f"IFERROR(INDEX({col_bereich},MATCH(LARGE({BD},{k}),{BD},0)),\"\")")

for k in range(1, 6):
    r = 28 + k
    p_wert(f'B{r}', k, horizontal='center')
    p_wert(f'C{r}', '=' + top(sp('B'), k))
    p_wert(f'D{r}', '=' + top(sp('C'), k), horizontal='center')
    idx_o = f"INDEX({sp('O')},MATCH(LARGE({BD},{k}),{BD},0))"
    idx_h = f"INDEX({sp('H')},MATCH(LARGE({BD},{k}),{BD},0))"
    idx_p = f"INDEX({sp('P')},MATCH(LARGE({BD},{k}),{BD},0))"
    p_wert(f'E{r}', f'=IFERROR(IF(ISNUMBER({idx_o}),{idx_o},IF({idx_h}="","",{idx_h})),"")',
           fmt='DD.MM.YYYY', horizontal='center')
    p_wert(f'F{r}', f'=IFERROR(IF(ISNUMBER({idx_p}),{idx_p},""),"")',
           fmt='DD.MM.YYYY', horizontal='center')
    p_wert(f'G{r}', '=' + top(sp('I'), k), fmt='#,##0', horizontal='right')
    p_wert(f'H{r}', '=' + top(sp('D'), k), groesse=10)
    pdf.row_dimensions[r].height = 15

# --- ⚠ Offene Punkte ---------------------------------------------- 35–43
p_titel('B35', '⚠  Offene Punkte — bevor die Zahlen belastbar sind')
merge(pdf, 'B35:G35')
pdf.row_dimensions[35].height = 16.5
p_kopf('B36', 'Punkt', 'left'); merge(pdf, 'B36:E36')
p_kopf('F36', 'Anzahl')
p_kopf('G36', 'Volumen CHF'); merge(pdf, 'G36:H36')
pdf.row_dimensions[36].height = 15
DEF = "'📋 Definitionen & Klärung'!"
for i in range(6):
    r = 37 + i
    q = 17 + i
    p_wert(f'B{r}', f"={DEF}$B${q}", groesse=10, wrap=True); merge(pdf, f'B{r}:E{r}')
    p_wert(f'F{r}', f"={DEF}$C${q}", fmt='0', horizontal='center')
    p_wert(f'G{r}', f"={DEF}$D${q}", fmt='#,##0', horizontal='right')
    merge(pdf, f'G{r}:H{r}')
    pdf.row_dimensions[r].height = 15
p_wert('B43', f"={DEF}$D$23", groesse=10, fett=True, farbe='FFB45309', fuellung=None,
       wrap=True)
merge(pdf, 'B43:H43')
pdf.row_dimensions[43].height = 24

p_wert('B45', '="Offene Pflichtangaben: "&' + DEF + '$C$23&'
       '"  ·  Details und Erfassungslisten: Blatt «📋 Definitionen & Klärung»"',
       groesse=9, farbe='FF888888', fuellung=None)
merge(pdf, 'B45:H45')
pdf.row_dimensions[45].height = 13.5

# Druck: eine A4-Seite hochformat.
pdf.print_area = "'📑 Executive PDF'!$A$1:$H$49"
pdf.page_setup.orientation = 'portrait'
pdf.page_setup.fitToWidth = 1
pdf.page_setup.fitToHeight = 1

wb.save(DATEI)
print('Block 2 geschrieben: Zerlegung (CEO 215–217), Kontrollrechnung (CEO 262–267), '
      'Executive PDF neu als Einseiter, Hilfsspalte BD.')
