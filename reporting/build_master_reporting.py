#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baut die MASTER-Version des MiT-Strom-Reportings.

Aggreko-Vorgabe (Basis dieser Aenderung):
  A) "Probability to Win %" - Bewertungsskala 0 / 10 / 30 / 60 / 90 %
  B) "Pipeline (Weighted)"  = total revenue x Gewichtungsfaktor, wobei der
     Faktor aus dem Feld "Effective Probability" abgeleitet wird:
        0-44 %  -> 0 %
       45-59 %  -> 30 %
       60-89 %  -> 50 %
       >= 90 %  -> 90 %
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.pagebreak import Break
from openpyxl.utils import quote_sheetname
from copy import copy

SRC = 'original.xlsx'          # Ausgangsdatei = quelle_stand_vor_update.xlsx
OUT = 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'

PIPE = 'MiT Strom Pipeline'
PROB = '⚖️ Wahrscheinlichkeit'
PQ = f"'{PIPE}'"          # Pipeline quoted
WQ = f"'{PROB}'"          # Wahrscheinlichkeits-Sheet quoted

# Letzte Zeile des Pipeline-Druckbereichs (bleibt eine Querseite)
PRINT_LAST = 90

# Aktiv-Status (identisch zur bestehenden Logik der Mappe)
AKTIV = ["WON", "offered", "to be offered", "on hold",
         "follow-up", "Evaluation", "In evaluation", "tbd"]

# ---------------------------------------------------------------- Farbwelt
DARK      = 'FF0D1117'
SLATE     = 'FF1E293B'
GREEN     = 'FF166534'
GOLD      = 'FFD4A017'
NAVY      = 'FF1F3864'
LIGHT     = 'FFF8FAFC'
LIGHTG    = 'FFF0FDF4'
AMBER     = 'FFFFF3CD'
BAND_FILL = ['FFF1F5F9', 'FFFEF3C7', 'FFDBEAFE', 'FFDCFCE7']

thin = Side(style='thin', color='FFCBD5E1')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def A(sz=10, b=False, color='FF111111'):
    return Font(name='Arial', size=sz, bold=b, color=color)


def C(sz=11, b=False, color=NAVY, name='Calibri'):
    return Font(name=name, size=sz, bold=b, color=color)


def fill(rgb):
    return PatternFill('solid', fgColor=rgb)


def put(ws, coord, value, font=None, fillc=None, fmt=None,
        align=None, valign='center', wrap=None, border=False):
    c = ws[coord]
    c.value = value
    if font:
        c.font = font
    if fillc:
        c.fill = fill(fillc)
    if fmt:
        c.number_format = fmt
    if align or valign or wrap:
        c.alignment = Alignment(horizontal=align, vertical=valign, wrap_text=wrap)
    if border:
        c.border = BOX
    return c


# ================================================================= laden
wb = openpyxl.load_workbook(SRC)
pipe = wb[PIPE]

# ----------------------------------------------------------------- Tempo
# Dashboard und CEO Report zogen ihre Zeilen ueber Ganzspalten-Bezuege
# (INDEX('MiT Strom Pipeline'!$A:$A;...)). Bei rund 4'500 solchen Formeln
# rechnet die Mappe minutenlang. Fachlich identisch, aber um Groessenordnungen
# schneller ist der Bezug auf den tatsaechlich genutzten Bereich bis Zeile 860
# (die Trefferzeile aus MATCH(...)+5 liegt immer zwischen 6 und 860).
import re as _re
_full_col = _re.compile(r"('MiT Strom Pipeline'!\$([A-Z]{1,2})):\$\2(?![0-9])")
_fixed = 0
for _sh in wb.worksheets:
    for _row in _sh.iter_rows():
        for _c in _row:
            if isinstance(_c.value, str) and _c.value.startswith('=') and ':$' in _c.value:
                _new = _full_col.sub(lambda m: f'{m.group(1)}$1:${m.group(2)}$860', _c.value)
                if _new != _c.value:
                    _c.value = _new
                    _fixed += 1
print(f'Ganzspalten-Bezuege begrenzt: {_fixed} Formeln')

# =========================================================================
# 1) NEUES BLATT  "⚖️ Wahrscheinlichkeit"  -- Single Source of Truth
# =========================================================================
ws = wb.create_sheet(PROB, wb.sheetnames.index(PIPE) + 1)
ws.sheet_properties.tabColor = GOLD
ws.sheet_view.showGridLines = False

# Spaltenbreiten so gewaehlt, dass beide Tabellen dieselbe Raster nutzen:
# Skalatabelle spannt die Textspalten (C:E bzw. F:H), die Bandtabelle nutzt
# jede Spalte einzeln.
widths = {'A': 11, 'B': 15, 'C': 16, 'D': 16, 'E': 15, 'F': 16, 'G': 16, 'H': 15,
          'I': 3, 'J': 18}
for col, w in widths.items():
    ws.column_dimensions[col].width = w

# ---- Kopf
ws.merge_cells('A1:H1')
put(ws, 'A1', '⚖️  Bewertungsmodell Wahrscheinlichkeit & gewichteter Umsatz  —  Aggreko-Standard',
    A(13, True, 'FFFFFFFF'), DARK, align='center')
ws.row_dimensions[1].height = 34
ws.merge_cells('A2:H2')
put(ws, 'A2', 'Mobil in Time AG  ·  An Aggreko Company  ·  Burak Ücöz  ·  '
              'Dieses Blatt ist die Steuerzentrale: Skala und Faktoren hier ändern — '
              'Pipeline, Dashboard, CEO Report, Report, Executive PDF und Diagramme rechnen automatisch nach.',
    A(9, False, 'FFAAAAAA'), DARK, align='left', wrap=True)
ws.row_dimensions[2].height = 26
ws.merge_cells('A3:H3')
put(ws, 'A3', '="Stand: "&TEXT(TODAY(),"DD.MM.YYYY")&"   ·   Quelle: Vorgabe Aggreko (Reporting-Update «Probability to Win» / «Pipeline (Weighted)»)"',
    A(9, True, 'FF64748B'), 'FFFFFFFF', align='left')

# ---- 1) Skala -----------------------------------------------------------
ws.merge_cells('A4:H4')
put(ws, 'A4', '1️⃣   Probability to Win %  —  verbindliche Bewertungsskala',
    A(11, True, 'FFFFFFFF'), GREEN, align='left')
ws.row_dimensions[4].height = 22

hdr = [('A5', '#'), ('B5', 'Probability\nto Win %'), ('C5', 'Begründung / Einsatz (DE)'),
       ('D5', ''), ('E5', ''), ('F5', 'Reason (EN, Original Aggreko)'), ('G5', ''), ('H5', '')]
for co, t in hdr:
    put(ws, co, t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True, border=True)
ws.merge_cells('C5:E5')
ws.merge_cells('F5:H5')
ws.row_dimensions[5].height = 30

SKALA = [
    (1, 0.00,
     'Nichts — keine Opportunität.',
     'Nothing, no Opportunity'),
    (2, 0.10,
     'Die Opportunität ist ein «Platzhalter» für ein Thema, das wir beim Kunden erkannt haben. '
     'Ein Bedarf oder ein Pain, der besprochen wurde und den wir als Platzhalter für ein späteres '
     'Gespräch in der Pipeline führen wollen. 10 % ebenfalls für sehr grosse Opportunitäten, die wir '
     'nicht so stark gewichten wollen wie mit 30 %; 10 % kann zudem für Contingency-Pläne verwendet werden.',
     'The opportunity is a used for "placeholder" themes that we have uncovered with a customer. A need or a pain '
     'that has been discussed and we want to plug it into the pipeline as a placeholder for a future conversation. '
     'Also use 10% for very large opportunities that we don\'t want to weight as heavily as 30%; and 10% can also be '
     'used for contingency plans.'),
    (3, 0.30,
     'Die Opportunität lebt und ist gesund, wir wissen aber nicht, ob sie tatsächlich on-hire geht.',
     'The opportunity is alive and well, but we do not know if it will actually go on-hire or not.'),
    (4, 0.60,
     'Wir haben sehr gute Chancen, die Opportunität zu gewinnen, der Kunde committet sich aber nicht mit '
     'einer PO. Das Fleet-Team hat den Fall auf dem Radar und überwacht die On-/Off-Hire-Daten.',
     'We have a very good chance of winning the opportunity but the customer is not comitting with a PO, the fleet '
     'team have this on their radar monitoring on/off hire dates.'),
    (5, 0.90,
     'Wir sind sicher, dass wir den Auftrag erhalten, warten aber noch auf die PO oder ein dokumentiertes '
     'Commitment. Das Fleet-Team erfüllt die Quote auf dieser Stufe im OF.',
     'We are sure that we will get the order but wating on PO or documented commitment. The fleet team will fulfil '
     'the Quote at this stage in OF.'),
]
for i, (nr, val, de, en) in enumerate(SKALA):
    r = 6 + i
    put(ws, f'A{r}', nr, A(9, False, 'FF64748B'), LIGHT, align='center', border=True)
    put(ws, f'B{r}', val, A(14, True, NAVY), AMBER, fmt='0%', align='center', border=True)
    put(ws, f'C{r}', de, A(9), LIGHT, align='left', wrap=True, border=True)
    put(ws, f'D{r}', None, fillc=LIGHT, border=True)
    put(ws, f'E{r}', None, fillc=LIGHT, border=True)
    put(ws, f'F{r}', en, Font(name='Arial', size=8, italic=True, color='FF64748B'),
        LIGHT, align='left', wrap=True, border=True)
    put(ws, f'G{r}', None, fillc=LIGHT, border=True)
    put(ws, f'H{r}', None, fillc=LIGHT, border=True)
    ws.merge_cells(f'C{r}:E{r}')
    ws.merge_cells(f'F{r}:H{r}')
    ws.row_dimensions[r].height = {0: 18, 1: 76, 2: 30, 3: 56, 4: 56}[i]

put(ws, 'A11', 'ℹ️  Diese fünf Werte stehen in «MiT Strom Pipeline», Spalte S (Effektive Wahrscheinlichkeit) '
               'als Dropdown zur Verfügung. Abweichende Werte werden dort orange markiert.',
    Font(name='Arial', size=9, italic=True, color='FF64748B'), align='left')
ws.merge_cells('A11:H11')

# ---- 2) Gewichtungsfaktoren + Live-Auswertung ---------------------------
ws.merge_cells('A13:H13')
put(ws, 'A13', '2️⃣   Pipeline (Weighted)  —  Gewichtungsfaktoren und Live-Auswertung',
    A(11, True, 'FFFFFFFF'), GREEN, align='left')
ws.row_dimensions[13].height = 22

put(ws, 'A14', 'Pipeline (Weighted) = Umsatz («total revenue») × Gewichtungsfaktor. '
               'Der Faktor wird aus dem Feld «Effective Probability» abgeleitet:',
    Font(name='Arial', size=9, italic=True, color='FF64748B'), align='left')
ws.merge_cells('A14:H14')

bh = [('A15', 'Band'), ('B15', 'Effective\nProbability von'), ('C15', 'bis'),
      ('D15', 'Gewichtungs-\nfaktor'), ('E15', 'Anzahl\nDeals'),
      ('F15', 'Umsatz CHF'), ('G15', 'Gewichtet CHF'), ('H15', 'Anteil am\ngew. Total')]
for co, t in bh:
    put(ws, co, t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True, border=True)
ws.row_dimensions[15].height = 32

BANDS = [('0 – 44 %', 0.00, 0.4499999, 0.00),
         ('45 – 59 %', 0.45, 0.5999999, 0.30),
         ('60 – 89 %', 0.60, 0.8999999, 0.50),
         ('≥ 90 %', 0.90, 1.00, 0.90)]

R0 = 16                      # erste Bandzeile
RT = R0 + len(BANDS)         # Totalzeile  = 20

# Aktiv-Status-Liste (Systemliste, rechts daneben)
put(ws, 'J15', 'Aktiv-Status (System)', A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
for i, s in enumerate(AKTIV):
    put(ws, f'J{16+i}', s, A(9, False, 'FF64748B'), LIGHT, align='center', border=True)
ws.column_dimensions['J'].hidden = True

JR = f'$J${R0}:$J${R0+len(AKTIV)-1}'      # $J$16:$J$23
# Aktiv-Kennzeichen wird zeilenweise in der Pipeline (Spalte AE) gerechnet -
# das haelt die Auswertung hier schnell und nachvollziehbar.
AKTIV_MASK = f'{PQ}!$AE$6:$AE$860'

for i, (label, lo, hi, fak) in enumerate(BANDS):
    r = R0 + i
    put(ws, f'A{r}', label, A(10, True, NAVY), BAND_FILL[i], align='center', border=True)
    put(ws, f'B{r}', lo, A(10), BAND_FILL[i], fmt='0%', align='center', border=True)
    put(ws, f'C{r}', hi, A(10), BAND_FILL[i], fmt='0%', align='center', border=True)
    put(ws, f'D{r}', fak, A(12, True, NAVY), AMBER, fmt='0%', align='center', border=True)
    put(ws, f'E{r}', f'=SUMPRODUCT({AKTIV_MASK},--({PQ}!$Y$6:$Y$860=$D{r}))',
        A(10), BAND_FILL[i], fmt='0', align='center', border=True)
    put(ws, f'F{r}', f'=SUMPRODUCT({AKTIV_MASK},--({PQ}!$Y$6:$Y$860=$D{r}),{PQ}!$AA$6:$AA$860)',
        A(10), BAND_FILL[i], fmt='#,##0', align='right', border=True)
    put(ws, f'G{r}', f'=F{r}*$D{r}', A(10, True), BAND_FILL[i], fmt='#,##0',
        align='right', border=True)
    put(ws, f'H{r}', f'=IFERROR(G{r}/$G${RT},0)', A(10), BAND_FILL[i], fmt='0.0%',
        align='center', border=True)
    ws.row_dimensions[r].height = 20

put(ws, f'A{RT}', 'TOTAL aktiv', A(10, True, 'FFFFFFFF'), DARK, align='center', border=True)
ws.merge_cells(f'A{RT}:D{RT}')
put(ws, f'E{RT}', f'=SUM(E{R0}:E{RT-1})', A(11, True, 'FFFFFFFF'), DARK, fmt='0',
    align='center', border=True)
put(ws, f'F{RT}', f'=SUM(F{R0}:F{RT-1})', A(12, True, GOLD), DARK, fmt='#,##0',
    align='right', border=True)
put(ws, f'G{RT}', f'=SUM(G{R0}:G{RT-1})', A(12, True, GOLD), DARK, fmt='#,##0',
    align='right', border=True)
put(ws, f'H{RT}', f'=IFERROR(G{RT}/F{RT},0)', A(11, True, 'FFFFFFFF'), DARK, fmt='0.0%',
    align='center', border=True)
ws.row_dimensions[RT].height = 24

put(ws, f'A{RT+1}', 'ℹ️  «Anteil am gew. Total» je Band; in der Totalzeile steht der '
                    'Gewichtungsgrad der Gesamtpipeline (gewichtet ÷ Umsatz).',
    Font(name='Arial', size=9, italic=True, color='FF64748B'), align='left')
ws.merge_cells(f'A{RT+1}:H{RT+1}')

# ---- 3) Kontrollen ------------------------------------------------------
RC = RT + 3                                        # 23
ws.merge_cells(f'A{RC}:H{RC}')
put(ws, f'A{RC}', '3️⃣   Selbstkontrolle & Datenqualität', A(11, True, 'FFFFFFFF'),
    GREEN, align='left')
ws.row_dimensions[RC].height = 22

# Summe der gewichteten Werte direkt aus der Pipeline-Spalte Q
sumq = '+'.join([f'SUMIFS({PQ}!$Q$6:$Q$860,{PQ}!$R$6:$R$860,"{s}")' for s in AKTIV])

checks = [
    ('Gewichtete Pipeline laut Bandtabelle (Spalte G)', f'=G{RT}', '#,##0'),
    ('Gewichtete Pipeline laut Pipeline-Spalte Q (Gew.Wert)', f'={sumq}', '#,##0'),
    ('Abweichung (muss 0 sein)', f'=ROUND(E{RC+1}-E{RC+2},2)', '#,##0.00'),
    ('Status Formelprüfung',
     f'=IF(ABS(E{RC+3})<0.01,"✔  Konsistent — alle Blätter rechnen mit demselben Modell",'
     f'"⚠  Abweichung — Bandtabelle und Spalte Q prüfen")', 'General'),
    ('Aktive Deals mit Wahrscheinlichkeit ausserhalb der Aggreko-Skala',
     f'=SUMPRODUCT({AKTIV_MASK},--({PQ}!$AF$6:$AF$860=0))', '0'),
    ('Handlungsbedarf Skala',
     f'=IF(E{RC+5}=0,"✔  Alle aktiven Deals sind auf der Skala 0/10/30/60/90 %",'
     f'"⚠  "&E{RC+5}&" Deal(s) auf einen Skalenwert setzen — orange markiert in Spalte S der Pipeline")',
     'General'),
    (f'Deals unterhalb des Pipeline-Druckbereichs (ab Zeile {PRINT_LAST+1})',
     f'=SUMPRODUCT(--({PQ}!$B${PRINT_LAST+1}:$B$860<>""))', '0'),
    ('Status Druckbereich',
     f'=IF(E{RC+7}=0,"✔  Alle Deals liegen im Druckbereich (Zeilen 6–{PRINT_LAST})",'
     f'"⚠  "&E{RC+7}&" Deal(s) unterhalb Zeile {PRINT_LAST} — Druckbereich der Pipeline erweitern")',
     'General'),
]
# Beschriftung ueber A:D, Ergebnis ueber E:H
for i, (label, formula, fmt) in enumerate(checks):
    r = RC + 1 + i
    put(ws, f'A{r}', label, A(10), LIGHT, align='left', border=True)
    for col in 'BCD':
        put(ws, f'{col}{r}', None, fillc=LIGHT, border=True)
    put(ws, f'E{r}', formula, A(10, True, NAVY), AMBER, fmt=fmt, align='left', border=True)
    for col in 'FGH':
        put(ws, f'{col}{r}', None, fillc=AMBER, border=True)
    ws.row_dimensions[r].height = 18
    ws.merge_cells(f'A{r}:D{r}')
    ws.merge_cells(f'E{r}:H{r}')

# ---- 4) Aenderungsprotokoll --------------------------------------------
RL = RC + len(checks) + 3
ws.merge_cells(f'A{RL}:H{RL}')
put(ws, f'A{RL}', '4️⃣   Was wurde umgestellt', A(11, True, 'FFFFFFFF'), GREEN, align='left')
ws.row_dimensions[RL].height = 22

LOG = [
    ('Skala', 'Probability to Win % neu verbindlich 0 / 10 / 30 / 60 / 90 % (Dropdown in Pipeline Spalte S, '
              'Begründungen siehe Abschnitt 1).'),
    ('Gewichtung', 'Gew.Wert CHF (Pipeline Spalte Q) = Volumen × Aggreko-Faktor statt Volumen × Wahrscheinlichkeit. '
                   'Faktor: 0–44 % → 0 %, 45–59 % → 30 %, 60–89 % → 50 %, ab 90 % → 90 %.'),
    ('Datenbestand', 'Die bestehenden Wahrscheinlichkeiten der einzelnen Deals wurden NICHT verändert — sie sind die '
                     '«Effective Probability». Abweichungen von der Skala sind markiert und im Bewertungs-Meeting zu setzen.'),
    ('Berichte', 'Dashboard, CEO Report, 📄 Report, 📑 Executive PDF und 📊 Diagramme zeigen zusätzlich die gewichtete '
                 'Pipeline und die Verteilung über die vier Gewichtungsbänder.'),
    ('Technik', 'Der Faktor je Deal steht in der ausgeblendeten Hilfsspalte Y der Pipeline (bei Bedarf einblenden), '
                'die Systemkennzeichen in AE/AF. Ganzspalten-Bezüge in Dashboard und CEO Report wurden auf Zeile 860 '
                'begrenzt, der Druckbereich der Pipeline auf Zeile 80 erweitert (vorher Zeile 48 — Deals fehlten im Ausdruck).'),
    ('Bereinigt', 'Verwaiste Restformeln in Pipeline Q862 (Summe von Q9, Q10, Q12, Q13, Q14, Q22, Q60, Q61, Q62, Q63) '
                  'und Q864 (Summe von Q10, Q12, Q60, Q61) entfernt — von nichts referenziert, aber Auslöser für '
                  'Fehlerwerte, sobald einer dieser Deals keinen numerischen Gew.Wert mehr hat. '
                  'Die WON-Ranglisten haben neu einen Sortier-Zuschlag, damit betragsgleiche Deals nicht doppelt '
                  'erscheinen. Ein Deal ohne Wahrscheinlichkeit gilt jetzt korrekt als «ausserhalb der Skala».'),
]
for i, (k, v) in enumerate(LOG):
    r = RL + 1 + i
    put(ws, f'A{r}', k, A(10, True, NAVY), LIGHT, align='left', border=True)
    put(ws, f'B{r}', v, A(9), LIGHT, align='left', wrap=True, border=True)
    for col in 'CDEFGH':
        put(ws, f'{col}{r}', None, fillc=LIGHT, border=True)
    ws.merge_cells(f'B{r}:H{r}')
    ws.row_dimensions[r].height = 32

ws.print_area = f'A1:H{RL + len(LOG) + 1}'
ws.page_setup.orientation = 'landscape'
ws.page_setup.fitToWidth = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True

# Benannter Bereich fuer das Dropdown
wb.defined_names.add(DefinedName('Wahrscheinlichkeit_Skala',
                                 attr_text=f'{WQ}!$B$6:$B$10'))

# =========================================================================
# 2) PIPELINE  --  Faktor-Helfer Y, neue Q-Formel, Dropdown, Markierung
# =========================================================================
BAND_LO = f'{WQ}!$B${R0}:$B${R0+3}'
BAND_FK = f'{WQ}!$D${R0}:$D${R0+3}'

for col, title in (('Y', '_GewFaktor'), ('AE', '_Aktiv'), ('AF', '_SkalaOK')):
    pipe[f'{col}5']._style = copy(pipe['Z5']._style)
    pipe[f'{col}5'].value = title

AKTIV_LIST = f'{WQ}!$J${R0}:$J${R0+len(AKTIV)-1}'
SKALA_LIST = f'{WQ}!$B$6:$B$10'

for r in range(6, 861):
    # Gewichtungsfaktor gemaess Bandtabelle (Aggreko)
    pipe[f'Y{r}'] = (f'=IF(ISNUMBER(S{r}),'
                     f'IFERROR(LOOKUP(IF(S{r}<=1,S{r},S{r}/100),{BAND_LO},{BAND_FK}),0),0)')
    pipe[f'Y{r}'].number_format = '0%'
    # Pipeline (Weighted) = Umsatz x Faktor
    pipe[f'Q{r}'] = (f'=IF(AND(ISNUMBER(I{r}),ISNUMBER(S{r})),I{r}*Y{r},'
                     f'IF(OR(I{r}<>"",S{r}<>""),"tbd",""))')
    # 1 = zaehlt zur aktiven Pipeline
    pipe[f'AE{r}'] = f'=IF(B{r}="",0,IF(COUNTIF({AKTIV_LIST},R{r})>0,1,0))'
    # 1 = Wahrscheinlichkeit liegt auf der Aggreko-Skala.
    # ISNUMBER-Waechter ist zwingend: COUNTIF wertet eine leere Bezugszelle
    # als 0 aus und wuerde einen Deal OHNE Wahrscheinlichkeit sonst als
    # "skalenkonform" zaehlen (die 0-%-Stufe steht ja in der Liste).
    pipe[f'AF{r}'] = (f'=IF(B{r}="",0,'
                      f'IF(AND(ISNUMBER(S{r}),COUNTIF({SKALA_LIST},S{r})>0),1,0))')
    # Sortierschluessel der WON-Ranglisten: winziger zeilenabhaengiger Zuschlag,
    # damit zwei betragsgleiche WON-Deals nicht beide auf dieselbe Zeile
    # matchen und ein Deal doppelt in der Top-Liste erscheint.
    pipe[f'Z{r}'] = f'=IF(AND(R{r}="WON",ISNUMBER(I{r})),AA{r}+(861-ROW())*0.000001,"")'

# Kopfzeilen praezisieren
pipe['Q5'] = 'Gew.Wert CHF\n(Aggreko)'
pipe['S5'] = 'Effektive\nWahr. %'
pipe['S4'] = '⚖️  Gew. Pipeline (Aggreko)'
# U4 summierte bisher ALLE Zeilen (inkl. LOST/Declined) und konnte damit von
# der gewichteten Pipeline in Dashboard, Report und Blatt "Wahrscheinlichkeit"
# abweichen, sobald ein verlorener Deal seine Wahrscheinlichkeit behaelt.
# Neu identische Abgrenzung wie ueberall sonst: nur aktive Status.
pipe['U4'] = '=' + '+'.join(
    [f'SUMIFS(Q$6:Q$860,R$6:R$860,"{s}")' for s in AKTIV])
pipe['A2'] = ('  ✏️  Nur in diesem Sheet Daten erfassen — Dashboard, CEO Report, Report, Executive PDF und '
              'Diagramme aktualisieren sich automatisch.   ⚖️  Wahrscheinlichkeit (Spalte S) nach '
              'Aggreko-Skala 0/10/30/60/90 % setzen — Modell siehe Blatt «⚖️ Wahrscheinlichkeit».')

# Verwaiste Restformeln weit unterhalb der Daten (Zeilen 862/864). Sie summierten
# eine handverlesene Auswahl von Gew.Wert-Zellen, werden von nichts referenziert,
# liegen ausserhalb jedes Druckbereichs und ergeben #VALUE!, sobald einer der
# genannten Deals keinen numerischen Gew.Wert mehr hat. Inhalt zur Dokumentation:
#   Q862 = Q9+Q10+Q12+Q13+Q14+Q22+Q60+Q61+Q62+Q63
#   Q864 = Q10+Q12+Q60+Q61
for _co in ('Q862', 'Q864'):
    pipe[_co].value = None

# Druckbereich reichte nur bis Zeile 48 - die Pipeline ist inzwischen laenger,
# beim Ausdruck fehlten die Deals ab Zeile 49. Neu deckt er genau den
# Druckbereich auf Zeile 90 - das bleibt eine Querseite und laesst Platz fuer
# rund 20 weitere Deals. Wird darunter erfasst, schlaegt die Kontrolle auf dem
# Blatt "Wahrscheinlichkeit" Alarm (statt wie bisher stillschweigend zu kappen).
pipe.print_area = f"'{PIPE}'!$A$1:$Y${PRINT_LAST}"
pipe.page_setup.orientation = 'landscape'
pipe.page_setup.fitToWidth = 1
pipe.page_setup.fitToHeight = 0
pipe.sheet_properties.pageSetUpPr.fitToPage = True

# Dropdown auf S (Warnung statt harter Sperre, damit Altwerte erhalten bleiben)
dv = DataValidation(type='list', formula1='Wahrscheinlichkeit_Skala',
                    allow_blank=True, showErrorMessage=True, errorStyle='warning')
dv.error = ('Aggreko-Standard: 0 %, 10 %, 30 %, 60 % oder 90 %.\n'
            'Andere Werte sind möglich (z. B. Salesforce-Import), werden aber orange markiert.')
dv.errorTitle = 'Wahrscheinlichkeit ausserhalb der Skala'
dv.prompt = ('0 % = keine Opportunität · 10 % = Platzhalter/Contingency · 30 % = lebt, on-hire offen · '
             '60 % = sehr gute Chance, keine PO · 90 % = sicher, PO/Commitment ausstehend')
dv.promptTitle = 'Probability to Win %'
dv.showInputMessage = True
pipe.add_data_validation(dv)
dv.add('S6:S860')

# Markierung: Wahrscheinlichkeit nicht auf der Aggreko-Skala.
# Werte hier bewusst ausgeschrieben - bedingte Formatierung soll ohne
# Blattverweis funktionieren (aeltere Excel-Versionen, Web-Excel).
pipe.conditional_formatting.add(
    'S6:S860',
    FormulaRule(formula=['AND($B6<>"",ISNUMBER($S6),$S6<>0,$S6<>0.1,$S6<>0.3,$S6<>0.6,$S6<>0.9)'],
                fill=fill('FFFFE0B2'), font=Font(name='Arial', size=10, bold=True, color='FF9A3412'),
                stopIfTrue=False))

# =========================================================================
# 3) _data  --  Bandtabelle als Chart-Quelle
# =========================================================================
d = wb['_data']
for co, t in [('K1', 'Wahrsch.-Band'), ('L1', 'Faktor'), ('M1', 'Umsatz CHF'),
              ('N1', 'Gewichtet CHF'), ('O1', 'Anzahl')]:
    d[co] = t
for i in range(4):
    r = 2 + i
    d[f'K{r}'] = f'={WQ}!$A${R0+i}'
    d[f'L{r}'] = f'={WQ}!$D${R0+i}'
    d[f'M{r}'] = f'={WQ}!$F${R0+i}'
    d[f'N{r}'] = f'={WQ}!$G${R0+i}'
    d[f'O{r}'] = f'={WQ}!$E${R0+i}'

# =========================================================================
# 4) DIAGRAMME  --  neues Chart "Umsatz vs. gewichtet je Band"
# =========================================================================
dia = wb['📊 Diagramme']
# Die Kanton-Grafik daruber ueberdeckt jede Zellenueberschrift in diesem
# Bereich - der Titel steht deshalb in der Grafik selbst.

ch = BarChart()
ch.type = 'col'
ch.grouping = 'clustered'
ch.gapWidth = 60
ch.height = 8.5
ch.width = 24
data = Reference(d, min_col=13, max_col=14, min_row=1, max_row=5)   # M:N inkl. Header
cats = Reference(d, min_col=11, min_row=2, max_row=5)               # K2:K5
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
ch.y_axis.numFmt = '#,##0'
ch.y_axis.title = 'CHF'
ch.title = '⚖️  Pipeline nach Wahrscheinlichkeits-Band — Umsatz vs. gewichtet (Aggreko)'
dia.add_chart(ch, 'A56')
dia.print_area = "'📊 Diagramme'!$A$1:$R$75"

# =========================================================================
# 5) DASHBOARD  &  CEO REPORT
# =========================================================================
GEW_AKTIV = sumq
GEW_WON = f'SUMIFS({PQ}!$Q$6:$Q$860,{PQ}!$R$6:$R$860,"WON")'
GEW_OFF = '+'.join([f'SUMIFS({PQ}!$Q$6:$Q$860,{PQ}!$R$6:$R$860,"{s}")'
                    for s in ("offered", "to be offered", "on hold")])
GEW_OPP = '+'.join([f'SUMIFS({PQ}!$Q$6:$Q$860,{PQ}!$R$6:$R$860,"{s}")'
                    for s in ("follow-up", "Evaluation", "In evaluation", "tbd")])


def upgrade_report(sheet_name, last_col, foot_merge_old):
    sh = wb[sheet_name]
    lc = last_col                                   # 'K' oder 'L'

    # --- Info-Zeile 8 -----------------------------------------------------
    info = ('="⚖️  Gewichtete Pipeline (Aggreko-Faktoren 0 / 30 / 50 / 90 %): "'
            f'&TEXT({GEW_AKTIV},"#,##0")&" CHF   ·   davon Offerte: "'
            f'&TEXT({GEW_OFF},"#,##0")&" CHF   ·   Opportunität: "'
            f'&TEXT({GEW_OPP},"#,##0")&" CHF   ·   Modell: Blatt «⚖️ Wahrscheinlichkeit»"')
    sh.merge_cells(f'A8:{lc}8')
    put(sh, 'A8', info, A(10, True, GOLD), DARK, align='center')
    sh.row_dimensions[8].height = 22

    # --- Fussnote von 206 nach 214 verschieben ---------------------------
    if foot_merge_old in [str(m) for m in sh.merged_cells.ranges]:
        sh.unmerge_cells(foot_merge_old)
    foot_val = sh['A206'].value
    foot_style = copy(sh['A206']._style)
    sh['A206'].value = None

    # --- Abschnitt 4: gewichtete Pipeline (Zeilen 206-212) ---------------
    sh.merge_cells(f'A206:{lc}206')
    put(sh, 'A206', '⚖️  4. GEWICHTETE PIPELINE — Bewertungsmodell Aggreko',
        A(11, True, 'FFFFFFFF'), GREEN, align='left', border=True)
    sh.row_dimensions[206].height = 24

    heads = [('A', 'Wahrscheinlichkeits-Band'), ('D', 'Faktor'), ('E', 'Anzahl'),
             ('F', 'Umsatz CHF'), ('G', 'Gewichtet CHF'), ('I', 'Anteil')]
    sh.merge_cells('A207:C207')
    sh.merge_cells('G207:H207')
    for col, t in heads:
        put(sh, f'{col}207', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
    sh.row_dimensions[207].height = 20

    for i in range(4):
        r = 208 + i
        sh.merge_cells(f'A{r}:C{r}')
        sh.merge_cells(f'G{r}:H{r}')
        put(sh, f'A{r}', f'={WQ}!$A${R0+i}', A(10, True, NAVY), BAND_FILL[i],
            align='left', border=True)
        put(sh, f'D{r}', f'={WQ}!$D${R0+i}', A(10, True, NAVY), BAND_FILL[i],
            fmt='0%', align='center', border=True)
        put(sh, f'E{r}', f'={WQ}!$E${R0+i}', A(10), BAND_FILL[i], fmt='0',
            align='center', border=True)
        put(sh, f'F{r}', f'={WQ}!$F${R0+i}', A(10), BAND_FILL[i], fmt='#,##0',
            align='right', border=True)
        put(sh, f'G{r}', f'={WQ}!$G${R0+i}', A(10, True), BAND_FILL[i], fmt='#,##0',
            align='right', border=True)
        put(sh, f'I{r}', f'={WQ}!$H${R0+i}', A(10), BAND_FILL[i], fmt='0.0%',
            align='center', border=True)
        sh.row_dimensions[r].height = 18

    sh.merge_cells('A212:C212')
    sh.merge_cells('G212:H212')
    put(sh, 'A212', 'TOTAL aktive Pipeline', A(11, True, 'FFFFFFFF'), DARK,
        align='left', border=True)
    put(sh, 'D212', '', A(10), DARK, border=True)
    put(sh, 'E212', f'={WQ}!$E${RT}', A(11, True, 'FFFFFFFF'), DARK, fmt='0',
        align='center', border=True)
    put(sh, 'F212', f'={WQ}!$F${RT}', A(12, True, 'FFFFFFFF'), DARK, fmt='#,##0',
        align='right', border=True)
    put(sh, 'G212', f'={WQ}!$G${RT}', A(13, True, GOLD), DARK, fmt='#,##0',
        align='right', border=True)
    put(sh, 'I212', f'={WQ}!$H${RT}', A(11, True, 'FFFFFFFF'), DARK, fmt='0.0%',
        align='center', border=True)
    sh.row_dimensions[212].height = 26

    sh.merge_cells(f'A213:{lc}213')
    put(sh, 'A213',
        f'="Gewichtungsgrad der Gesamtpipeline: "&TEXT({WQ}!$H${RT},"0.0%")'
        f'&"   ·   Faktoren: 0–44 % → 0 %  |  45–59 % → 30 %  |  60–89 % → 50 %  |  ab 90 % → 90 %"',
        Font(name='Arial', size=9, italic=True, color='FF64748B'), align='left')
    sh.row_dimensions[213].height = 16

    # Fussnote neu
    sh.merge_cells(f'A215:{lc}215')
    sh['A215'].value = foot_val
    sh['A215']._style = foot_style
    sh.row_dimensions[215].height = 13.5

    # Der neue Abschnitt soll nicht mitten auf einer Seite beginnen.
    sh.row_breaks.append(Break(id=205))
    sh.print_area = f"'{sheet_name}'!$A$1:${lc}$215"


upgrade_report('Dashboard', 'K', 'A206:J206')
upgrade_report('CEO Report', 'L', 'A206:K206')

# =========================================================================
# 6) 📄 REPORT
# =========================================================================
rep = wb['📄 Report']
# Die Top-WON-Tabelle zeigte das Volumen ueber LARGE(_WON_Sort;n). Da der
# Sortierschluessel jetzt einen winzigen Zuschlag traegt, wird der Betrag
# direkt aus der Volumenspalte geholt - so steht dort immer der exakte Wert.
for _i in range(1, 11):
    _r = 28 + _i
    rep[f'E{_r}'] = (f"=IFERROR(INDEX({PQ}!$I$6:$I$860,"
                     f"MATCH(LARGE({PQ}!$Z$6:$Z$860,{_i}),{PQ}!$Z$6:$Z$860,0)),\"\")")

for co, src in [('A11', 'A10'), ('B11', 'B10'), ('C11', 'C10'), ('D11', 'D10')]:
    rep[co]._style = copy(rep[src]._style)
rep['A11'] = '⚖️ Gewichtet'
rep['B11'] = f'={WQ}!$G${RT}'
rep['C11'] = f'={WQ}!$E${RT}'
rep['D11'] = f'=IFERROR(B11/$B$10,0)'
rep['A11'].font = C(11, True, NAVY)
rep.row_dimensions[11].height = 15

# Fussnote «Strg+P» von 41 nach 52
if 'A41:H41' in [str(m) for m in rep.merged_cells.ranges]:
    rep.unmerge_cells('A41:H41')
foot_val = rep['A41'].value
foot_style = copy(rep['A41']._style)
rep['A41'].value = None

rep.merge_cells('A43:G43')
rep['A43'] = '⚖️ Wahrscheinlichkeits-Bewertung (Aggreko-Modell)'
rep['A43']._style = copy(rep['A13']._style)
rep['A43'].value = '⚖️ Wahrscheinlichkeits-Bewertung (Aggreko-Modell)'

for col, t in [('A', 'Band'), ('B', 'Faktor'), ('C', 'Anzahl Deals'),
               ('D', 'Umsatz CHF'), ('E', 'Gewichtet CHF')]:
    rep[f'{col}44'] = t
    rep[f'{col}44']._style = copy(rep['A14']._style)
    rep[f'{col}44'].value = t

for i in range(4):
    r = 45 + i
    rep[f'A{r}'] = f'={WQ}!$A${R0+i}'
    rep[f'B{r}'] = f'={WQ}!$D${R0+i}'
    rep[f'C{r}'] = f'={WQ}!$E${R0+i}'
    rep[f'D{r}'] = f'={WQ}!$F${R0+i}'
    rep[f'E{r}'] = f'={WQ}!$G${R0+i}'
    for col, fmt in (('A', 'General'), ('B', '0%'), ('C', '0'),
                     ('D', '#,##0" CHF"'), ('E', '#,##0" CHF"')):
        c = rep[f'{col}{r}']
        c.font = C(11)
        c.number_format = fmt
        c.alignment = Alignment(horizontal='center', vertical='center')
        c.border = BOX
        c.fill = fill(BAND_FILL[i])

rep['A49'] = 'TOTAL aktiv'
rep['B49'] = ''
rep['C49'] = f'={WQ}!$E${RT}'
rep['D49'] = f'={WQ}!$F${RT}'
rep['E49'] = f'={WQ}!$G${RT}'
for col, fmt in (('A', 'General'), ('B', '0%'), ('C', '0'),
                 ('D', '#,##0" CHF"'), ('E', '#,##0" CHF"')):
    c = rep[f'{col}49']
    c.font = C(11, True, 'FFFFFFFF')
    c.number_format = fmt
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = BOX
    c.fill = fill(NAVY)
rep['A49'].alignment = Alignment(horizontal='left', vertical='center')

rep.merge_cells('A50:G50')
rep['A50'] = (f'="Faktoren: 0–44 % → 0 %  |  45–59 % → 30 %  |  60–89 % → 50 %  |  ab 90 % → 90 %.   '
              f'Gewichtungsgrad gesamt: "&TEXT({WQ}!$H${RT},"0.0%")&"   ·   Modell: Blatt «⚖️ Wahrscheinlichkeit»"')
rep['A50'].font = Font(name='Calibri', size=9, italic=True, color='FF808080')

rep.merge_cells('A52:H52')
rep['A52'].value = foot_val
rep['A52']._style = foot_style
rep.print_area = "'📄 Report'!$A$1:$G$52"

# =========================================================================
# 7) 📑 EXECUTIVE PDF
# =========================================================================
ex = wb['📑 Executive PDF']
# Zeile war auf B10:G10 verbunden - mit der Zusatzangabe reicht die Breite nicht mehr.
if 'B10:G10' in [str(m) for m in ex.merged_cells.ranges]:
    ex.unmerge_cells('B10:G10')
ex.merge_cells('B10:H10')
ex['B10'] = ('="📊  PIPELINE: "&TEXT(Dashboard!I6,"#,##0")&" CHF  ·  "&Dashboard!I7'
             f'&" Deals  ·  ⚖️ GEWICHTET: "&TEXT({WQ}!$G${RT},"#,##0")&" CHF"')
# Kundenname in der Top-5-Tabelle wurde abgeschnitten; Breite von der
# grosszuegigen Margenspalte umverteilt (Seitenbreite bleibt gleich).
ex.column_dimensions['C'].width = 22
ex.column_dimensions['H'].width = 16

# Fussnote von 35 nach 40
if 'A35:H35' in [str(m) for m in ex.merged_cells.ranges]:
    ex.unmerge_cells('A35:H35')
foot_val = ex['A35'].value
foot_style = copy(ex['A35']._style)
ex['A35'].value = None

ex.merge_cells('B32:G32')
ex['B32']._style = copy(ex['B21']._style)
ex['B32'].value = '⚖️  Gewichtete Pipeline nach Aggreko-Bewertung'

hdr_style = copy(ex['B22']._style)
ex.merge_cells('B33:C33')
ex.merge_cells('E33:F33')
ex.merge_cells('G33:H33')
for co, t in [('B33', 'Wahrsch.-Band'), ('D33', 'Faktor'),
              ('E33', 'Umsatz CHF'), ('G33', 'Gewichtet CHF')]:
    ex[co]._style = copy(hdr_style)
    ex[co].value = t

body_style = copy(ex['D23']._style)
for i in range(4):
    r = 34 + i
    ex.merge_cells(f'B{r}:C{r}')
    ex.merge_cells(f'E{r}:F{r}')
    ex.merge_cells(f'G{r}:H{r}')
    for co, formula, fmt in [(f'B{r}', f'={WQ}!$A${R0+i}', 'General'),
                             (f'D{r}', f'={WQ}!$D${R0+i}', '0%'),
                             (f'E{r}', f'={WQ}!$F${R0+i}', '#,##0'),
                             (f'G{r}', f'={WQ}!$G${R0+i}', '#,##0')]:
        c = ex[co]
        c._style = copy(body_style)
        c.value = formula
        c.number_format = fmt
        c.fill = fill(BAND_FILL[i])

ex.merge_cells('B38:C38')
ex.merge_cells('E38:F38')
ex.merge_cells('G38:H38')
for co, formula, fmt in [('B38', 'TOTAL aktiv', 'General'),
                         ('D38', '', 'General'),
                         ('E38', f'={WQ}!$F${RT}', '#,##0'),
                         ('G38', f'={WQ}!$G${RT}', '#,##0')]:
    c = ex[co]
    c._style = copy(body_style)
    c.value = formula
    c.number_format = fmt
    c.font = Font(name='Cambria', size=11, bold=True, color='FFFFFFFF')
    c.fill = fill(NAVY)

ex.merge_cells('B39:H39')
ex['B39'] = (f'="Faktoren: 0–44 % → 0 %  |  45–59 % → 30 %  |  60–89 % → 50 %  |  ab 90 % → 90 %   ·   '
             f'Gewichtungsgrad: "&TEXT({WQ}!$H${RT},"0.0%")')
ex['B39'].font = Font(name='Cambria', size=9, italic=True, color='FF808080')

ex.merge_cells('A41:H41')
ex['A41'].value = foot_val
ex['A41']._style = foot_style
ex.print_area = "'📑 Executive PDF'!$A$1:$H$41"
ex.page_setup.fitToHeight = 1
ex.page_setup.fitToWidth = 1
ex.sheet_properties.pageSetUpPr.fitToPage = True

wb.save(OUT)
print('gespeichert:', OUT)
