#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stufe 2 des Masterfiles: Marge, Auftragsnachweis, Varianten, Definitionen.

Setzt die Anpassungen um, die aus den Rueckfragen zum Reporting entstanden sind:
  1. Marge = Nettoumsatz minus Einstand (Equipment, Transport, Treibstoff,
     Personal, Uebrige) - ohne MwSt auf beiden Seiten.
  2. Fixe Statusdefinition: WON nur mit Offert-/Auftragsnummer und Belegdatum.
  3. Varianten-Kennzeichnung, damit derselbe Entscheid nur einmal ins Volumen laeuft.
  4. Sperre: WON ohne vollstaendig erfassten Einstand ist nicht berichtsfaehig.
  5. Neues Blatt, das jede Rueckfrage mit einer Live-Zahl beantwortet.
"""
import openpyxl, re
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.comments import Comment
from copy import copy

F = 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
PIPE, PROB, DEF = 'MiT Strom Pipeline', '⚖️ Wahrscheinlichkeit', '📋 Definitionen & Klärung'
PQ, WQ, DQ = f"'{PIPE}'", f"'{PROB}'", f"'{DEF}'"
LAST, PRINT_LAST = 860, 90
AKTIV = ["WON", "offered", "to be offered", "on hold",
         "follow-up", "Evaluation", "In evaluation", "tbd"]

DARK, SLATE, GREEN, GOLD = 'FF0D1117', 'FF1E293B', 'FF166534', 'FFD4A017'
NAVY, LIGHT, AMBER = 'FF1F3864', 'FFF8FAFC', 'FFFFF3CD'
RED, ROSE, MINT, INPUT_FILL = 'FF991B1B', 'FFFEE2E2', 'FFDCFCE7', 'FFFFF9C4'
thin = Side(style='thin', color='FFCBD5E1')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def A(sz=10, b=False, color='FF111111', italic=False):
    return Font(name='Arial', size=sz, bold=b, color=color, italic=italic)


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


def band(ws, r, first='A', last='H', text='', bg=GREEN, h=22):
    ws.merge_cells(f'{first}{r}:{last}{r}')
    put(ws, f'{first}{r}', text, A(11, True, 'FFFFFFFF'), bg, align='left')
    ws.row_dimensions[r].height = h


wb = openpyxl.load_workbook(F)
pipe = wb[PIPE]

# =========================================================================
# 1) Hilfsspalten nach rechts (Y..AF -> AJ..AQ), Platz fuer Fachspalten
# =========================================================================
MOVE = {'Y': 'AJ', 'Z': 'AK', 'AA': 'AL', 'AB': 'AM',
        'AC': 'AN', 'AD': 'AO', 'AE': 'AP', 'AF': 'AQ'}
_pat = re.compile(r'(?<![A-Z0-9_$])(\$?)(AA|AB|AC|AD|AE|AF|Y|Z)(\$?)(\d+)(?![0-9])')


def remap(f):
    return _pat.sub(lambda m: f'{m.group(1)}{MOVE[m.group(2)]}{m.group(3)}{m.group(4)}', f)


moved = 0
for old, new in MOVE.items():
    for r in range(5, LAST + 1):
        src = pipe[f'{old}{r}']
        if src.value is None:
            continue
        dst = pipe[f'{new}{r}']
        dst.value = remap(src.value) if isinstance(src.value, str) and src.value.startswith('=') else src.value
        dst._style = copy(src._style)
        moved += 1
    pipe.column_dimensions[new].hidden = True
    pipe.column_dimensions[new].width = 13
for old in MOVE:
    for r in range(1, LAST + 1):
        pipe[f'{old}{r}'].value = None
    pipe.column_dimensions[old].hidden = False

_xref = re.compile(r"('MiT Strom Pipeline'!\$?)(AA|AB|AC|AD|AE|AF|Y|Z)(\$?\d+)")
_xref2 = re.compile(r"(?<=:)(\$?)(AA|AB|AC|AD|AE|AF|Y|Z)(\$?\d+)")
rew = 0
for ws in wb.worksheets:
    if ws.title == PIPE:
        continue
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            if not (isinstance(v, str) and v.startswith('=') and PIPE in v):
                continue
            n = _xref.sub(lambda m: f'{m.group(1)}{MOVE[m.group(2)]}{m.group(3)}', v)
            n = _xref2.sub(lambda m: f'{m.group(1)}{MOVE[m.group(2)]}{m.group(3)}', n)
            if n != v:
                c.value = n
                rew += 1
# d) Restliche Pipeline-Formeln (Spalten A-X) zeigen teils ebenfalls auf die
#    alten Hilfsspalten - vor allem "Gew.Wert = Volumen x Faktor". Auch die
#    muessen mitziehen, sonst rechnen sie gegen die neuen Fachspalten.
inner = 0
for row_ in pipe.iter_rows(min_col=1, max_col=24):
    for c in row_:
        v = c.value
        if isinstance(v, str) and v.startswith('='):
            n = remap(v)
            if n != v:
                c.value = n
                inner += 1
print(f'Hilfsspalten verschoben: {moved} Zellen, {rew} Formeln in Berichten, '
      f'{inner} Formeln in der Pipeline nachgezogen')

# =========================================================================
# 2) Blatt "📋 Definitionen & Klärung"
# =========================================================================
d = wb.create_sheet(DEF, wb.sheetnames.index(PIPE) + 1)
d.sheet_properties.tabColor = RED
d.sheet_view.showGridLines = False
for col, w in {'A': 3, 'B': 30, 'C': 34, 'D': 16, 'E': 16, 'F': 16,
               'G': 34, 'H': 16, 'I': 3}.items():
    d.column_dimensions[col].width = w

d.merge_cells('A1:H1')
put(d, 'A1', '📋  Definitionen, Kalkulationsregeln und offene Punkte',
    A(13, True, 'FFFFFFFF'), DARK, align='center')
d.row_dimensions[1].height = 34
d.merge_cells('A2:H2')
put(d, 'A2', 'Mobil in Time AG · An Aggreko Company · Burak Ücöz  —  Antwort auf die Rückfragen zum Reporting. '
             'Jede Zahl auf diesem Blatt rechnet live aus der Pipeline und bleibt damit auch nach Datenänderungen richtig.',
    A(9, False, 'FFAAAAAA'), DARK, align='left', wrap=True)
d.row_dimensions[2].height = 24

# Zellbezuege der Hilfsspalten (nach dem Umzug)
FAK, WON_S, INUM = f'{PQ}!$AJ$6:$AJ${LAST}', f'{PQ}!$AK$6:$AK${LAST}', f'{PQ}!$AL$6:$AL${LAST}'
AKT = f'{PQ}!$AP$6:$AP${LAST}'
VOL, STA, KUN = f'{PQ}!$I$6:$I${LAST}', f'{PQ}!$R$6:$R${LAST}', f'{PQ}!$B$6:$B${LAST}'
ABW, VART, VARI = f'{PQ}!$AA$6:$AA${LAST}', f'{PQ}!$AB$6:$AB${LAST}', f'{PQ}!$AD$6:$AD${LAST}'
EINOK = f'{PQ}!$AR$6:$AR${LAST}'
BELOK, WONB = f'{PQ}!$AS$6:$AS${LAST}', f'{PQ}!$AT$6:$AT${LAST}'
ZAEHLT, MEHRF = f'{PQ}!$AU$6:$AU${LAST}', f'{PQ}!$AV$6:$AV${LAST}'
MONAT, ZEITOK = f'{PQ}!$AX$6:$AX${LAST}', f'{PQ}!$AY$6:$AY${LAST}'
NETTN = f'{PQ}!$AZ$6:$AZ${LAST}'
VON, BIS = f'{PQ}!$O$6:$O${LAST}', f'{PQ}!$P$6:$P${LAST}'
OFFNR, AUFNR = f'{PQ}!$AE$6:$AE${LAST}', f'{PQ}!$AF$6:$AF${LAST}'
ALTW, SKOK = f'{PQ}!$AI$6:$AI${LAST}', f'{PQ}!$AQ$6:$AQ${LAST}'
IST_OFFERTE = f'--(({STA}="offered")+({STA}="to be offered")>0)'

row = 4

# ---- 1) Antworten auf die Rueckfragen ----------------------------------
band(d, row, text='1️⃣   Antworten auf die Rückfragen  —  mit Live-Zahlen aus der Pipeline')
row += 1
for co, t in (('B', 'Rückfrage'), ('C', 'Antwort / Regel'), ('G', 'Live-Zahl')):
    put(d, f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True, border=True)
for co in 'DEFH':
    put(d, f'{co}{row}', None, fillc=SLATE, border=True)
d.merge_cells(f'C{row}:F{row}')
d.merge_cells(f'G{row}:H{row}')
row += 1

ANTWORT = [
    ('Margenplanung: warum keine Marge mehr im Bericht steht',
     'Die negativen Margen kamen daher, dass die MwSt als Kostenposition erfasst und vom Umsatz abgezogen '
     'wurde, und dass bei einem Teil der Zeilen gar nicht kalkuliert, sondern nur der Verkaufspreis in netto '
     'und MwSt aufgeteilt wurde. Auf dieser Datengrundlage stiftet eine ausgewiesene Marge mehr '
     'Verunsicherung als Klarheit. Die Marge ist deshalb aus dem gesamten Reporting entfernt — Spalten, '
     'Kennzahlen, Diagramme und Prüfstatus-Meldungen. Die Kostenspalten J–N bleiben in der Pipeline als '
     'Arbeitsgrundlage erhalten, werden aber in keinem Bericht mehr ausgewertet. Der Bericht zeigt '
     'stattdessen Volumen, Status, Nachweis und Projektzeitraum.',
     f'="Kostenspalten weiterhin gepflegt: "&SUMPRODUCT({AKT},{EINOK})&" von "&SUM({AKT})'
     f'&" aktiven Deals  ·  Marge im Bericht: nicht ausgewiesen"'),
    ('Verantwortung der Kalkulation',
     'Der Einstand wird vom zuständigen Verkäufer erfasst und vor dem Statuswechsel auf WON durch den '
     'Innendienst gegengeprüft. Die Spalte «Prüfstatus» (AH in der Pipeline) zeigt für jede Zeile, ob das '
     'erfolgt ist.',
     f'="Deals mit vollständigem Einstand: "&SUMPRODUCT({AKT},{EINOK})&" von "&SUM({AKT})'),
    ('Laufen alle Projekte über MiT CH?',
     'Ja — MiT CH ist die Standardabwicklung dieser Pipeline. Jede Abweichung wird in der neuen Spalte '
     '«Abwicklung» (AA) erfasst: Aggreko (intl.) oder Partner / Dritte. Eine leere Zelle bedeutet also '
     'ausdrücklich MiT CH und nicht «unbekannt».',
     f'="Abweichend von MiT CH erfasst: "&SUMPRODUCT({AKT},--({ABW}<>""),--({ABW}<>"MiT CH"))'
     f'&" Deals  ·  "&TEXT(SUMPRODUCT({AKT},--({ABW}<>""),--({ABW}<>"MiT CH"),{INUM}),"#,##0")'
     f'&" CHF  ·  über MiT CH: "&TEXT(SUMPRODUCT({AKT},{INUM})-SUMPRODUCT({AKT},--({ABW}<>""),--({ABW}<>"MiT CH"),{INUM}),"#,##0")&" CHF"'),
    ('Wie ist das WON-Volumen zu verstehen?',
     'Es ist die Summe der Volumen aller Zeilen mit Status WON — brutto inkl. MwSt, wie erfasst. Neu wird '
     'daneben ausgewiesen: netto (ohne MwSt) und wie viel davon durch eine Auftrags-/PO-Nummer mit Datum '
     'belegt ist. Nur belegtes WON ist berichtsfähig.',
     f'="WON brutto: "&TEXT(SUMIFS({VOL},{STA},"WON"),"#,##0")&" CHF  ·  netto: "'
     f'&TEXT(SUMPRODUCT(--({STA}="WON"),{NETTN}),"#,##0")&" CHF  ·  davon belegt: "'
     f'&TEXT(SUMPRODUCT({WONB},{INUM}),"#,##0")&" CHF"'),
    ('Datacenter: 660 oder 330 kCHF?',
     'Das entscheidet die neue Variantenlogik. Gehören zwei Zeilen zum selben Kundenentscheid, bekommen sie '
     'dieselbe Deal-Gruppe (AC); die nicht führende Zeile wird als «Alternative – zählt nicht» markiert (AD) '
     'und fällt aus dem bereinigten Volumen. Unten stehen alle Kunden, die mehrfach vorkommen und noch '
     'zugeordnet werden müssen.',
     f'="Brutto: "&TEXT(SUMPRODUCT({AKT},{INUM}),"#,##0")&" CHF  ·  bereinigt: "'
     f'&TEXT(SUMPRODUCT({AKT},{ZAEHLT},{INUM}),"#,##0")&" CHF  ·  Zeilen mit Mehrfachkunde: "'
     f'&SUMPRODUCT({AKT},{MEHRF})'),
    ('Wurden Offerten erstellt bzw. liegen Aufträge vor?',
     'Das steht neu nicht mehr im Kommentar, sondern in eigenen Spalten: AE «Offert-Nr.» belegt die '
     'versendete Offerte, AF «Auftrag / PO-Nr.» und AG «Beleg-Datum» den erteilten Auftrag. Die Spalte '
     'AH «Prüfstatus» zeigt je Zeile, was davon vorliegt und was fehlt.',
     f'="Offerten mit Offert-Nr.: "&SUMPRODUCT({IST_OFFERTE},--({OFFNR}<>""))&" von "'
     f'&SUMPRODUCT({IST_OFFERTE})&"  ·  Aufträge mit PO-Nr. und Datum: "'
     f'&SUMPRODUCT({WONB})&" von "&COUNTIF({STA},"WON")'),
    ('Wahrscheinlichkeiten ausserhalb der Aggreko-Skala (50 %)',
     'Alle Zeilen sind auf die Skala 0/10/30/60/90 % umgeschlüsselt; der bisherige Wert bleibt in der '
     'neuen Spalte AI erhalten. Leitregel: wo eine Skalenstufe denselben Gewichtungsfaktor hat, wird sie '
     'gewählt — der gewichtete Umsatz bleibt dann unverändert (20→30, 80→60, 100→90). Die Deals mit 50 % '
     'können das nicht: kein Skalenwert fällt in das Gewichtungsband 45–59 % (Faktor 30 %). Sie stehen '
     'nach Aggreko-Definition auf 30 % und sind einzeln zu bestätigen — namentliche Liste und Protokoll '
     'im Blatt «⚖️ Wahrscheinlichkeit».',
     f'="Noch ausserhalb der Skala: "&SUMPRODUCT({AKT},--({SKOK}=0))&"  ·  umgeschlüsselt: "'
     f'&SUMPRODUCT(--({KUN}<>""),--({ALTW}<>""),--({ALTW}<>{PQ}!$S$6:$S${LAST}))'
     f'&"  ·  davon mit Gewichtsänderung: "'
     f'&SUMPRODUCT(--({KUN}<>""),--(ROUND({ALTW},6)=0.5))&"  ·  gewichtete Pipeline: "'
     f'&TEXT({WQ}!$G$20,"#,##0")&" CHF"'),
    ('Was heisst «Abrufbereitschaft»?',
     'Kapazität ist für den Kunden reserviert, ein bestätigter Abruf liegt aber NICHT vor. Der Umsatz '
     'entsteht erst mit dem Abruf. Solche Deals gehören deshalb in die Offert-Pipeline, nicht in WON. '
     'Die neue Spalte «Vertragsart» (AB) macht das je Zeile sichtbar; Abschnitt 6 definiert alle Arten.',
     f'="Als WON mit Abrufbereitschaft (muss 0 sein): "&SUMPRODUCT(--({STA}="WON"),--({VART}="Abrufbereitschaft"))'
     f'&"  ·  Vertragsart noch offen: "&SUMPRODUCT({AKT},--({VART}=""))'),
]
for q, a, live in ANTWORT:
    put(d, f'B{row}', q, A(10, True, NAVY), LIGHT, align='left', wrap=True, border=True)
    put(d, f'C{row}', a, A(9), LIGHT, align='left', wrap=True, border=True)
    for co in 'DEF':
        put(d, f'{co}{row}', None, fillc=LIGHT, border=True)
    put(d, f'G{row}', live, A(9, True, NAVY), AMBER, align='left', wrap=True, border=True)
    put(d, f'H{row}', None, fillc=AMBER, border=True)
    d.merge_cells(f'C{row}:F{row}')
    d.merge_cells(f'G{row}:H{row}')
    d.row_dimensions[row].height = 62
    row += 1

row += 1
# ---- 2) Offene Punkte ---------------------------------------------------
band(d, row, text='2️⃣   Offene Punkte  —  was noch erfasst werden muss, bevor die Zahlen belastbar sind')
row += 1
for co, t in (('B', 'Punkt'), ('C', 'Anzahl'), ('D', 'Volumen CHF'), ('G', 'Status')):
    put(d, f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True, border=True)
for co in 'EFH':
    put(d, f'{co}{row}', None, fillc=SLATE, border=True)
d.merge_cells(f'D{row}:F{row}')
d.merge_cells(f'G{row}:H{row}')
row += 1
GAP_FIRST = row

GAPS = [
    ('WON ohne Auftrags-/PO-Nummer und Datum',
     f'=SUMPRODUCT(--({STA}="WON"),--({BELOK}=0))',
     f'=SUMPRODUCT(--({STA}="WON"),--({BELOK}=0),{INUM})'),
    ('WON ohne vollständigen Einstand',
     f'=SUMPRODUCT(--({STA}="WON"),--({EINOK}=0))',
     f'=SUMPRODUCT(--({STA}="WON"),--({EINOK}=0),{INUM})'),
    ('Aktive Deals ohne erfassten Projektzeitraum',
     f'=SUMPRODUCT({AKT},--({ZEITOK}=0))', f'=SUMPRODUCT({AKT},--({ZEITOK}=0),{INUM})'),
    ('WON ohne erfassten Projektzeitraum',
     f'=SUMPRODUCT(--({STA}="WON"),--({ZEITOK}=0))',
     f'=SUMPRODUCT(--({STA}="WON"),--({ZEITOK}=0),{INUM})'),
    ('WON ohne Vertragsart (Einzelauftrag / Rahmenabruf / Abrufbereitschaft)',
     f'=SUMPRODUCT(--({STA}="WON"),--({VART}=""))',
     f'=SUMPRODUCT(--({STA}="WON"),--({VART}=""),{INUM})'),
    ('Kunden mehrfach in der Pipeline, Variante noch nicht geklärt',
     f'=SUMPRODUCT({AKT},{MEHRF},--({VARI}=""))',
     f'=SUMPRODUCT({AKT},{MEHRF},--({VARI}=""),{INUM})'),
]
for label, cnt, vol in GAPS:
    put(d, f'B{row}', label, A(10), LIGHT, align='left', wrap=True, border=True)
    put(d, f'C{row}', cnt, A(11, True, NAVY), LIGHT, fmt='0', align='center', border=True)
    put(d, f'D{row}', vol, A(10, True, NAVY), LIGHT, fmt='#,##0', align='right', border=True)
    for co in 'EF':
        put(d, f'{co}{row}', None, fillc=LIGHT, border=True)
    put(d, f'G{row}', f'=IF(C{row}=0,"✔ erledigt","⚠ offen")', A(10, True), AMBER,
        align='center', border=True)
    put(d, f'H{row}', None, fillc=AMBER, border=True)
    d.merge_cells(f'D{row}:F{row}')
    d.merge_cells(f'G{row}:H{row}')
    d.row_dimensions[row].height = 22
    row += 1
GAP_LAST = row - 1
put(d, f'B{row}', 'Gesamturteil', A(11, True, 'FFFFFFFF'), DARK, align='left', border=True)
put(d, f'C{row}', f'=SUM(C{GAP_FIRST}:C{GAP_LAST})', A(11, True, GOLD), DARK, fmt='0',
    align='center', border=True)
put(d, f'D{row}', f'=IF(C{row}=0,"Alle Pflichtangaben vollständig — Reporting ist belastbar.",'
                  f'"Noch "&C{row}&" offene Einträge. Bis dahin gilt: WON-Volumen nur als «gemeldet», nicht als «belegt» lesen.")',
    A(10, True, 'FFFFFFFF'), DARK, align='left', border=True)
for co in 'EFGH':
    put(d, f'{co}{row}', None, fillc=DARK, border=True)
d.merge_cells(f'D{row}:H{row}')
d.row_dimensions[row].height = 24
GESAMT_ROW = row          # Zelle mit der Zahl der offenen Pflichtangaben
row += 2

# ---- 2b) Konkret angesprochene Positionen ------------------------------
band(d, row, text='2️⃣b  Konkret angesprochene Positionen  —  was hier einzutragen ist, damit die Zahl eindeutig wird')
row += 1
for co, t in (('B', 'Position'), ('C', 'Was zu tun ist'), ('G', 'Live-Stand')):
    put(d, f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True, border=True)
for co in 'DEFH':
    put(d, f'{co}{row}', None, fillc=SLATE, border=True)
d.merge_cells(f'C{row}:F{row}')
d.merge_cells(f'G{row}:H{row}')
row += 1

GRP = f'{PQ}!$AC$6:$AC${LAST}'


def name_grp(n):
    """Deal-Gruppe der Zeile mit diesem Kundennamen."""
    return f'IFERROR(INDEX({GRP},MATCH("{n}",{KUN},0)),"")'


PUNKT = [
    ('Datacenter — DPR Loadbank (2 Zeilen)',
     'Beide Zeilen betreffen Loadbank-Tests beim selben Endkunden. Wenn es EIN Kundenentscheid ist: bei beiden '
     'dieselbe Deal-Gruppe (Spalte AC) eintragen und die nicht führende Zeile auf «Alternative – zählt nicht» '
     'setzen (AD). Dann zählt statt der Summe nur noch die führende Variante.',
     f'="Summe beider Zeilen: "&TEXT(SUMIF({KUN},"DPR Heat Loadbank",{VOL})+SUMIF({KUN},"DPR Generator Loadbank Test",{VOL}),"#,##0")'
     f'&" CHF  ·  "&IF(AND({name_grp("DPR Heat Loadbank")}<>"",'
     f'{name_grp("DPR Heat Loadbank")}={name_grp("DPR Generator Loadbank Test")}),'
     f'"✔ als ein Entscheid zugeordnet","⚠ Deal-Gruppe noch nicht gesetzt")'),
    ('Event Flums — Murg Flums Energie',
     'Start ist «Auf Abruf». Vertragsart (Spalte AB) setzen: «Rahmenvertrag – Abruf bestätigt» wenn der Abruf '
     'terminiert ist — dann zählt der Betrag ins WON. «Abrufbereitschaft» wenn nur Kapazität reserviert ist — '
     'dann gehört der Deal nicht in WON, sondern in die Offert-Pipeline.',
     f'="Volumen: "&TEXT(SUMIF({KUN},"Murg Flums Energie",{VOL}),"#,##0")&" CHF  ·  Vertragsart: "'
     f'&IF(IFERROR(INDEX({VART},MATCH("Murg Flums Energie",{KUN},0)),"")="","⚠ noch nicht gesetzt",'
     f'IFERROR(INDEX({VART},MATCH("Murg Flums Energie",{KUN},0)),""))'),
]
for label, todo, live in PUNKT:
    put(d, f'B{row}', label, A(10, True, NAVY), AMBER, align='left', wrap=True, border=True)
    put(d, f'C{row}', todo, A(9), AMBER, align='left', wrap=True, border=True)
    for co in 'DEF':
        put(d, f'{co}{row}', None, fillc=AMBER, border=True)
    put(d, f'G{row}', live, A(9, True, NAVY), AMBER, align='left', wrap=True, border=True)
    put(d, f'H{row}', None, fillc=AMBER, border=True)
    d.merge_cells(f'C{row}:F{row}')
    d.merge_cells(f'G{row}:H{row}')
    d.row_dimensions[row].height = 56
    row += 1

# Kunden, die mehrfach in der Pipeline stehen - Namen beim Bauen ermittelt,
# Zahlen bleiben live. Neu hinzukommende Faelle zaehlt die Gap-Liste oben mit.
from collections import Counter
_names = Counter()
for _r in range(6, LAST + 1):
    _b = pipe[f'B{_r}'].value
    if _b and not (isinstance(_b, str) and _b.startswith('=')):
        _names[str(_b)] += 1
_dups = sorted([n for n, c in _names.items() if c > 1])
if _dups:
    put(d, f'B{row}', 'Kunde mehrfach in der Pipeline', A(9, True, 'FFFFFFFF'), SLATE,
        align='center', border=True)
    put(d, f'C{row}', 'Zeilen', A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
    put(d, f'D{row}', 'Volumen brutto CHF', A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
    put(d, f'F{row}', 'davon zählend CHF', A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
    put(d, f'G{row}', 'Deal-Gruppe gesetzt?', A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
    for co in 'EH':
        put(d, f'{co}{row}', None, fillc=SLATE, border=True)
    d.merge_cells(f'D{row}:E{row}')
    d.merge_cells(f'G{row}:H{row}')
    row += 1
    for n in _dups:
        esc = n.replace('"', '""')
        put(d, f'B{row}', n, A(10), LIGHT, align='left', border=True)
        put(d, f'C{row}', f'=COUNTIF({KUN},"{esc}")', A(10), LIGHT, fmt='0', align='center', border=True)
        put(d, f'D{row}', f'=SUMIF({KUN},"{esc}",{VOL})', A(10), LIGHT, fmt='#,##0',
            align='right', border=True)
        put(d, f'E{row}', None, fillc=LIGHT, border=True)
        put(d, f'F{row}', f'=SUMPRODUCT(--({KUN}="{esc}"),{ZAEHLT},{INUM})', A(10, True, NAVY),
            LIGHT, fmt='#,##0', align='right', border=True)
        put(d, f'G{row}', f'=IF(SUMPRODUCT(--({KUN}="{esc}"),--({GRP}<>""))=COUNTIF({KUN},"{esc}"),'
                          f'"✔ zugeordnet","⚠ offen")', A(10, True), AMBER, align='center', border=True)
        put(d, f'H{row}', None, fillc=AMBER, border=True)
        d.merge_cells(f'D{row}:E{row}')
        d.merge_cells(f'G{row}:H{row}')
        row += 1

row += 2

# ---- 3) Grundannahmen ---------------------------------------------------
band(d, row, text='3️⃣   Grundannahmen  —  gelb hinterlegte Zellen sind die Stellschrauben')
row += 1
for co, t in (('B', 'Annahme'), ('C', 'Wert'), ('D', 'Begründung / Quelle')):
    put(d, f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
for co in 'EFGH':
    put(d, f'{co}{row}', None, fillc=SLATE, border=True)
d.merge_cells(f'D{row}:H{row}')
row += 1
ANN_ROW = row
ANN = [
    ('Volumen «CHF» ist erfasst als', 'brutto inkl. MwSt', 'General',
     'Aus den Daten belegt: bei 36 Zeilen ergibt Equipment + Transport + Personal exakt Volumen ÷ 1.081, '
     'und die Spalte «Übrige» enthielt genau den MwSt-Betrag. Auf «netto exkl. MwSt» umstellen, falls die '
     'Erfassung ändert — alle Blätter rechnen automatisch nach.'),
    ('MwSt-Satz', 0.081, '0.0%', 'Schweizer Normalsatz seit 01.01.2024.'),
    ('Schwelle «Preis-Aufteilung»', 0.005, '0.0%',
     'Ohne Bedeutung für die Berichte, seit die Marge nicht mehr ausgewiesen wird. Der Wert bleibt '
     'als Annahme dokumentiert, falls die Margenbetrachtung später wieder aufgenommen wird.'),
]
for label, val, fmt, why in ANN:
    put(d, f'B{row}', label, A(10, True, NAVY), LIGHT, align='left', border=True)
    put(d, f'C{row}', val, A(11, True, NAVY), INPUT_FILL, fmt=fmt, align='center', border=True)
    put(d, f'D{row}', why, A(9, italic=True, color='FF64748B'), LIGHT, align='left', wrap=True, border=True)
    for co in 'EFGH':
        put(d, f'{co}{row}', None, fillc=LIGHT, border=True)
    d.merge_cells(f'D{row}:H{row}')
    d.row_dimensions[row].height = 40
    row += 1

put(d, f'B{row}', 'Umrechnungsfaktor auf netto', A(10, True, NAVY), LIGHT, align='left', border=True)
put(d, f'C{row}', f'=IF($C${ANN_ROW}="brutto inkl. MwSt",1+$C${ANN_ROW+1},1)',
    A(11, True, NAVY), LIGHT, fmt='0.000', align='center', border=True)
put(d, f'D{row}', 'Nettoumsatz = Volumen ÷ Umrechnungsfaktor. Bei «netto exkl. MwSt» ist der Faktor 1.',
    A(9, italic=True, color='FF64748B'), LIGHT, align='left', wrap=True, border=True)
for co in 'EFGH':
    put(d, f'{co}{row}', None, fillc=LIGHT, border=True)
d.merge_cells(f'D{row}:H{row}')
FAKTOR_ROW = row
row += 2

dv_b = DataValidation(type='list', formula1='"brutto inkl. MwSt,netto exkl. MwSt"',
                      allow_blank=False, showErrorMessage=True)
d.add_data_validation(dv_b)
dv_b.add(f'C{ANN_ROW}')
wb.defined_names.add(DefinedName('MwSt_Satz', attr_text=f'{DQ}!$C${ANN_ROW+1}'))
wb.defined_names.add(DefinedName('Schwelle_Aufteilung', attr_text=f'{DQ}!$C${ANN_ROW+2}'))
wb.defined_names.add(DefinedName('Netto_Faktor', attr_text=f'{DQ}!$C${FAKTOR_ROW}'))

# ---- 4) Projektzeitraum --------------------------------------------------
band(d, row, text='4️⃣   Projektzeitraum  —  wie Start, Ende und Dauer erfasst und gerechnet werden')
row += 1
MARGE = [
    ('Projektstart (Spalte O)', 'Erster Tag des Projekts als echtes Datum TT.MM.JJJJ. Kein Text, keine '
                                'Monatsangabe — die Zelle ist als Datum geprüft, damit sich damit rechnen '
                                'und sortieren lässt.'),
    ('Projektende (Spalte P)', 'Letzter Tag des Projekts, ebenfalls als echtes Datum.'),
    ('⇒ Dauer (Spalte G)', 'Projektende − Projektstart + 1 Kalendertag; beide Tage zählen mit. '
                           'Beispiel: 01.08.2026 bis 10.08.2026 ergibt 10 Tage.'),
    ('Solange kein Datum steht', 'Steht nur eines der beiden Daten oder keines, bleibt der bisher von Hand '
                                 'erfasste Dauerwert unverändert stehen (gesichert in der ausgeblendeten '
                                 'Spalte AW). Überschrieben wird nichts.'),
    ('«Auf Abruf» und «tbd»', 'Dort bleiben beide Datumsfelder leer, und der Prüfstatus meldet den fehlenden '
                              'Zeitraum. Erst wenn der Abruf terminiert ist, werden die Daten erfasst.'),
    ('Auswertung', 'Aus dem Projektstart wird der Monatsanfang gebildet (ausgeblendete Spalte AX). '
                   'Darauf beruht die Auswertung nach Monat und Quartal in den Berichten.'),
]
for k, v in MARGE:
    put(d, f'B{row}', k, A(10, True, NAVY), LIGHT, align='left', wrap=True, border=True)
    put(d, f'C{row}', v, A(9), LIGHT, align='left', wrap=True, border=True)
    for co in 'DEFGH':
        put(d, f'{co}{row}', None, fillc=LIGHT, border=True)
    d.merge_cells(f'C{row}:H{row}')
    d.row_dimensions[row].height = 32
    row += 1
row += 1

# ---- 5) Statusdefinition ------------------------------------------------
band(d, row, text='5️⃣   Statusdefinition  —  wann ein Deal welchen Status trägt')
row += 1
for co, t in (('B', 'Status'), ('C', 'Bedeutung — verbindlich'), ('G', 'Nachweis zwingend')):
    put(d, f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True, border=True)
for co in 'DEFH':
    put(d, f'{co}{row}', None, fillc=SLATE, border=True)
d.merge_cells(f'C{row}:F{row}')
d.merge_cells(f'G{row}:H{row}')
row += 1
STATUS = [
    ('WON', 'Auftrag erteilt. Unterschriebene Bestellung oder gültige PO liegt vor.',
     'Auftrags-/PO-Nr. + Belegdatum + vollständiger Einstand', MINT),
    ('offered', 'Offerte versendet, Entscheid des Kunden offen.', 'Offert-Nr.', LIGHT),
    ('to be offered', 'Bedarf geklärt, Offerte in Arbeit.', '—', LIGHT),
    ('on hold', 'Projekt besteht, ist aber zeitlich sistiert.', '—', LIGHT),
    ('follow-up', 'Qualifizierter Lead, noch keine Offerte.', '—', LIGHT),
    ('Evaluation / In evaluation', 'Kunde prüft die technische Lösung.', '—', LIGHT),
    ('tbd', 'Noch nicht qualifiziert.', '—', LIGHT),
    ('LOST', 'Auftrag an den Wettbewerb verloren.', '—', ROSE),
    ('Declined', 'Von uns abgelehnt oder nicht weiterverfolgt.', '—', ROSE),
]
for st, mean, proof, bg in STATUS:
    put(d, f'B{row}', st, A(10, True, NAVY), bg, align='left', border=True)
    put(d, f'C{row}', mean, A(9), bg, align='left', wrap=True, border=True)
    for co in 'DEF':
        put(d, f'{co}{row}', None, fillc=bg, border=True)
    put(d, f'G{row}', proof, A(9, st == 'WON'), bg, align='left', wrap=True, border=True)
    put(d, f'H{row}', None, fillc=bg, border=True)
    d.merge_cells(f'C{row}:F{row}')
    d.merge_cells(f'G{row}:H{row}')
    d.row_dimensions[row].height = 20
    row += 1
row += 1

# ---- 6) Vertragsarten ---------------------------------------------------
band(d, row, text='6️⃣   Vertragsarten  —  was «Abrufbereitschaft» im Reporting bedeutet')
row += 1
for co, t in (('B', 'Vertragsart'), ('C', 'Bedeutung'), ('G', 'Zählt ins WON-Volumen?')):
    put(d, f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True, border=True)
for co in 'DEFH':
    put(d, f'{co}{row}', None, fillc=SLATE, border=True)
d.merge_cells(f'C{row}:F{row}')
d.merge_cells(f'G{row}:H{row}')
row += 1
VERTRAG = [
    ('Einzelauftrag', 'Fester Auftrag über eine konkrete Leistung und Menge. Bestellung oder PO liegt vor.',
     'Ja — voller Betrag', MINT),
    ('Rahmenvertrag – Abruf bestätigt', 'Rahmenvertrag besteht, der konkrete Abruf ist bestätigt und terminiert.',
     'Ja — Betrag des Abrufs', MINT),
    ('Abrufbereitschaft', 'Kapazität ist für den Kunden reserviert, ein bestätigter Abruf liegt NICHT vor. '
                          'Der Umsatz entsteht erst mit dem Abruf. Vertraglich gebunden ist die Bereitstellung, '
                          'nicht die Ausführung.',
     'Nein — gehört in die Offert-Pipeline', AMBER),
    ('Option / Reservation', 'Unverbindliche Reservation ohne Vertrag.', 'Nein', AMBER),
]
for vt, mean, cnt, bg in VERTRAG:
    put(d, f'B{row}', vt, A(10, True, NAVY), bg, align='left', wrap=True, border=True)
    put(d, f'C{row}', mean, A(9), bg, align='left', wrap=True, border=True)
    for co in 'DEF':
        put(d, f'{co}{row}', None, fillc=bg, border=True)
    put(d, f'G{row}', cnt, A(9, True), bg, align='left', wrap=True, border=True)
    put(d, f'H{row}', None, fillc=bg, border=True)
    d.merge_cells(f'C{row}:F{row}')
    d.merge_cells(f'G{row}:H{row}')
    d.row_dimensions[row].height = 34
    row += 1
row += 1

# ---- 7) Varianten -------------------------------------------------------
band(d, row, text='7️⃣   Varianten  —  damit derselbe Kundenentscheid nur einmal ins Volumen läuft')
row += 1
VAR = [
    ('Deal-Gruppe (Spalte AC)', 'Frei wählbarer Schlüssel. Alle Zeilen, über die der Kunde EINEN Entscheid fällt, '
                                'bekommen denselben Schlüssel — z. B. drei Leistungsvarianten desselben Projekts.'),
    ('Variante (Spalte AD)', '«Führend» = zählt ins Volumen. «Alternative – zählt nicht» = derselbe Entscheid, '
                             'wird nicht mitgezählt. Leer = zählt (Einzeldeal).'),
    ('Bereinigtes Volumen', 'Summe ohne die als Alternative markierten Zeilen. Steht in Dashboard und CEO Report '
                            'der Bruttosumme gegenüber, damit beide Zahlen sichtbar bleiben.'),
    ('Sicherheitsregel', 'Nur ausdrücklich als Alternative markierte Zeilen fallen weg. Eine vergessene Markierung '
                         'kann also nie Volumen verschwinden lassen.'),
]
for k, v in VAR:
    put(d, f'B{row}', k, A(10, True, NAVY), LIGHT, align='left', wrap=True, border=True)
    put(d, f'C{row}', v, A(9), LIGHT, align='left', wrap=True, border=True)
    for co in 'DEFGH':
        put(d, f'{co}{row}', None, fillc=LIGHT, border=True)
    d.merge_cells(f'C{row}:H{row}')
    d.row_dimensions[row].height = 32
    row += 1

d.print_area = f'{DQ}!$A$1:$H${row}'
d.page_setup.orientation = 'landscape'
d.page_setup.fitToWidth = 1
d.page_setup.fitToHeight = 0
d.sheet_properties.pageSetUpPr.fitToPage = True
DEF_LAST_ROW = row


# =========================================================================
# 3) Pipeline: neue Fachspalten, korrigierte Marge, Pruefstatus
# =========================================================================
def m_ok(bereich, zeile):
    return bereich.min_row == zeile


hdr_style = copy(pipe['X5']._style)
data_style = copy(pipe['X6']._style)
num_style = copy(pipe['I6']._style)

NEU = [
    ('Y',  'Nettoumsatz\nCHF',      13, '#,##0'),
    ('Z',  'Einstand\nCHF',         13, '#,##0'),
    ('AA', 'Abwicklung',            18, 'General'),
    ('AB', 'Vertragsart',           26, 'General'),
    ('AC', 'Deal-Gruppe',           18, 'General'),
    ('AD', 'Variante',              22, 'General'),
    ('AE', 'Offert-Nr.',            15, 'General'),
    ('AF', 'Auftrag / PO-Nr.',      17, 'General'),
    ('AG', 'Beleg-Datum',           13, 'DD.MM.YYYY'),
    ('AH', 'Prüfstatus',            46, 'General'),
]
for col, title, width, fmt in NEU:
    pipe.column_dimensions[col].width = width
    pipe.column_dimensions[col].hidden = False
    h = pipe[f'{col}5']
    h._style = copy(hdr_style)
    h.value = title

# MwSt-Formeln in Spalte N waren keine Kosten, sondern die herausgerechnete
# MwSt des Verkaufspreises. Sie werden geleert; die Spalte heisst neu
# "Uebrige Kosten" und enthaelt ausschliesslich echte Kostenpositionen.
mwst_rows = []
for r in range(6, LAST + 1):
    v = pipe[f'N{r}'].value
    if isinstance(v, str) and v.startswith('=') and '1.081' in v.replace(',', '.'):
        mwst_rows.append(r)
        pipe[f'N{r}'].value = None
pipe['N5'].value = 'Übrige Kosten\nCHF'
print(f'MwSt-Formeln aus Spalte N entfernt: {len(mwst_rows)} Zeilen')

# --- Spalte O und P: aus Marge CHF / Marge % wird der Projektzeitraum.
# Die Kostenspalten J bis N bleiben als Arbeitsgrundlage stehen, ausgewertet
# wird die Marge nirgends mehr.
ZEIT = [('O', 'Projektstart', 14), ('P', 'Projektende', 14)]
for col, title, breite in ZEIT:
    pipe.column_dimensions[col].width = breite
    pipe.column_dimensions[col].hidden = False
    h = pipe[f'{col}5']
    h._style = copy(hdr_style)
    h.value = title
    h.comment = None

# Die bisher von Hand erfasste Mietdauer wird gesichert, bevor Spalte G zur
# Formel wird - sie bleibt stehen, solange kein Zeitraum erfasst ist.
dauer_alt = {}
for r in range(6, LAST + 1):
    v = pipe[f'G{r}'].value
    if (pipe[f'B{r}'].value not in (None, '') and v is not None
            and not (isinstance(v, str) and v.startswith('='))):
        dauer_alt[r] = v

SCHW = 'Schwelle_Aufteilung'
for r in range(6, LAST + 1):
    # --- sichtbare Fachspalten
    pipe[f'Y{r}'] = f'=IF(ISNUMBER(I{r}),I{r}/Netto_Faktor,"")'
    pipe[f'Z{r}'] = f'=IF(B{r}="","",IF(COUNT(J{r}:N{r})=0,"",SUM(J{r}:N{r})))'
    # Sammelt ALLE Befunde einer Zeile - ein WON ohne Beleg darf ein
    # Margenproblem in derselben Zeile nicht verdecken.
    # Sammelt ALLE Befunde einer Zeile - ein fehlender Beleg darf einen
    # fehlenden Zeitraum in derselben Zeile nicht verdecken.
    pipe[f'BA{r}'] = (f'=IF(B{r}="","",'
                      f'IF(AND(R{r}="WON",AS{r}=0),"⛔ Beleg fehlt · ","")'
                      f'&IF(AND(R{r}="WON",AR{r}=0),"⛔ Einstand fehlt · ","")'
                      f'&IF(AND(R{r}<>"WON",AR{r}=0),"○ Einstand offen · ","")'
                      f'&IF(AND(R{r}="WON",AB{r}=""),"⛔ Vertragsart fehlt · ","")'
                      f'&IF(AND(ISNUMBER(O{r}),ISNUMBER(P{r})),IF(P{r}<O{r},"⚠ Ende vor Start · ",""),"")'
                      f'&IF(AND(R{r}="WON",AY{r}=0,NOT(AND(ISNUMBER(O{r}),ISNUMBER(P{r})))),"⛔ Zeitraum fehlt · ","")'
                      f'&IF(AND(R{r}<>"WON",AY{r}=0,NOT(AND(ISNUMBER(O{r}),ISNUMBER(P{r})))),"○ Zeitraum offen · ",""))')
    pipe[f'BB{r}'] = (f'=IF(B{r}="","",'
                      f'IF(AND(R{r}="WON",AS{r}=0),"⛔ Nachweis fehlt",'
                      f'IF(AND(ISNUMBER(O{r}),ISNUMBER(P{r}),P{r}<O{r}),"⚠ Ende vor Start",'
                      f'IF(AND(R{r}="WON",AY{r}=0),"⛔ Zeitraum fehlt",'
                      f'IF(AR{r}=0,"○ Einstand offen",'
                      f'IF(AY{r}=0,"○ Zeitraum offen",'
                      f'IF(R{r}="WON","✅ belegt","✔ erfasst")))))))')
    pipe[f'AH{r}'] = (f'=IF(B{r}="","",IF(BA{r}="",'
                      f'IF(R{r}="WON","✅ belegt & vollständig","✔ vollständig"),'
                      f'LEFT(BA{r},LEN(BA{r})-3)))')
    # --- Projektzeitraum: Eingabefelder, keine Formeln
    pipe[f'O{r}'] = None
    pipe[f'P{r}'] = None
    # --- Mietdauer: gerechnet, sobald beide Daten stehen. Sonst bleibt der
    #     bisher von Hand erfasste Wert stehen (gesichert in AW).
    pipe[f'G{r}'] = (f'=IF(B{r}="","",IF(AY{r}=1,P{r}-O{r}+1,'
                     f'IF(AW{r}="","",AW{r})))')
    # --- Hilfsspalten
    pipe[f'AR{r}'] = f'=IF(B{r}="",0,IF(AND(COUNT(J{r}:M{r})=4,SUM(J{r}:M{r})>0),1,0))'
    pipe[f'AS{r}'] = f'=IF(B{r}="",0,IF(AND(AF{r}<>"",AG{r}<>""),1,0))'
    pipe[f'AT{r}'] = f'=IF(AND(R{r}="WON",AS{r}=1,AR{r}=1),1,0)'
    pipe[f'AU{r}'] = f'=IF(B{r}="",0,IF(AD{r}="Alternative – zählt nicht",0,1))'
    pipe[f'AV{r}'] = f'=IF(B{r}="",0,IF(COUNTIF($B$6:$B${LAST},B{r})>1,1,0))'
    pipe[f'AW{r}'] = dauer_alt.get(r)
    # Monatsanfang des Projektstarts - Grundlage der zeitlichen Auswertung.
    pipe[f'AX{r}'] = f'=IF(AY{r}=1,DATE(YEAR(O{r}),MONTH(O{r}),1),"")'
    pipe[f'AY{r}'] = (f'=IF(B{r}="",0,IF(AND(ISNUMBER(O{r}),ISNUMBER(P{r})),'
                      f'IF(P{r}>=O{r},1,0),0))')
    pipe[f'AZ{r}'] = f'=IF(ISNUMBER(Y{r}),Y{r},0)'
    for _co in ('O', 'P'):
        _c = pipe[f'{_co}{r}']
        _c._style = copy(num_style)
        _c.number_format = 'DD.MM.YYYY'
        _c.alignment = Alignment(horizontal='center', vertical='center')
        _c.fill = fill(INPUT_FILL)
    pipe[f'AX{r}'].number_format = 'MMM YYYY'
    # --- Formate der neuen sichtbaren Spalten
    for col, _t, _w, fmt in NEU:
        c = pipe[f'{col}{r}']
        c._style = copy(num_style if fmt != 'General' else data_style)
        c.number_format = fmt
        if col in ('AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AH'):
            c.alignment = Alignment(horizontal='left', vertical='center')

for col in ('AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ', 'BA', 'BB'):
    pipe.column_dimensions[col].hidden = True
    pipe.column_dimensions[col].width = 12
# Spalte BC trug fruher den Kurzstatus. Mit dem Wegfall der Margen-Hilfsspalten
# ruecken alle Hilfsspalten auf; BC wird geleert, damit keine Reste bleiben.
for r in range(5, LAST + 1):
    pipe[f'BC{r}'] = None
pipe.column_dimensions['BC'].hidden = True
HELP_HDR = {'AR': '_EinstandOK', 'AS': '_BelegOK', 'AT': '_WONbelegt', 'AU': '_Zaehlt',
            'AV': '_Mehrfachkunde', 'AW': '_DauerErfasst', 'AX': '_MonatStart',
            'AY': '_ZeitraumOK', 'AZ': '_NettoNum', 'BA': '_Befunde',
            'BB': '_KurzStatus'}
for col, t in HELP_HDR.items():
    pipe[f'{col}5']._style = copy(pipe['AK5']._style)
    pipe[f'{col}5'].value = t

# --- Dropdowns
DVS = [
    ('AA6:AA860', '"MiT CH,Aggreko (intl.),Partner / Dritte"'),
    ('AB6:AB860', '"Einzelauftrag,Rahmenvertrag – Abruf bestätigt,Abrufbereitschaft,Option / Reservation"'),
    ('AD6:AD860', '"Führend,Alternative – zählt nicht"'),
]
for rng, f1 in DVS:
    dv = DataValidation(type='list', formula1=f1, allow_blank=True,
                        showErrorMessage=True, errorStyle='stop')
    dv.error = 'Bitte einen Wert aus der Liste wählen. Die Definitionen stehen im Blatt «📋 Definitionen & Klärung».'
    dv.errorTitle = 'Wert nicht zulässig'
    pipe.add_data_validation(dv)
    dv.add(rng)

dv_dat = DataValidation(type='date', operator='greaterThan', formula1='DATE(2000,1,1)',
                        allow_blank=True, showErrorMessage=True, errorStyle='stop')
dv_dat.error = 'Bitte ein gültiges Datum erfassen (Datum der Bestellung bzw. der PO).'
dv_dat.errorTitle = 'Belegdatum'
pipe.add_data_validation(dv_dat)
dv_dat.add('AG6:AG860')

# Projektstart und Projektende sind echte Datumsfelder - Text wird abgewiesen,
# damit sich damit rechnen und sortieren laesst.
dv_zeit = DataValidation(type='date', operator='greaterThan', formula1='DATE(2000,1,1)',
                         allow_blank=True, showErrorMessage=True, errorStyle='stop')
dv_zeit.error = ('Bitte ein echtes Datum im Format TT.MM.JJJJ erfassen — keine Monatsangabe '
                 'und kein «tbd». Ist der Zeitraum noch offen, das Feld leer lassen; '
                 'der Prüfstatus meldet ihn dann als fehlend.')
dv_zeit.errorTitle = 'Projektzeitraum'
pipe.add_data_validation(dv_zeit)
dv_zeit.add('O6:O860')
dv_zeit.add('P6:P860')

# --- Bedingte Formatierung auf den Pruefstatus und die Marge
pipe.conditional_formatting.add('AH6:AH860', FormulaRule(
    formula=['LEFT($AH6,1)="⛔"'], fill=fill('FFFECACA'),
    font=Font(name='Arial', size=10, bold=True, color=RED), stopIfTrue=True))
pipe.conditional_formatting.add('AH6:AH860', FormulaRule(
    formula=['LEFT($AH6,1)="⚠"'], fill=fill('FFFEF3C7'),
    font=Font(name='Arial', size=10, bold=True, color='FF92400E'), stopIfTrue=True))
pipe.conditional_formatting.add('AH6:AH860', FormulaRule(
    formula=['LEFT($AH6,1)="✅"'], fill=fill(MINT),
    font=Font(name='Arial', size=10, bold=True, color=GREEN), stopIfTrue=True))
# Ende vor Start ist ein Erfassungsfehler und wird rot markiert.
pipe.conditional_formatting.add('O6:P860', FormulaRule(
    formula=['AND(ISNUMBER($O6),ISNUMBER($P6),$P6<$O6)'], fill=fill('FFFECACA'),
    font=Font(name='Arial', size=10, bold=True, color=RED), stopIfTrue=True))
# Aktive Zeile ohne Zeitraum bleibt dezent markiert, bis das Datum steht.
pipe.conditional_formatting.add('O6:P860', FormulaRule(
    formula=['AND($B6<>"",$O6="")'], fill=fill('FFFEF3C7'), stopIfTrue=False))

# --- Kopfzeile: Hinweis auf die neue Margendefinition
pipe['A2'] = ('  ✏️  Nur in diesem Sheet Daten erfassen.   ⚖️  Wahrscheinlichkeit (S) nach Aggreko-Skala '
              '0/10/30/60/90 %, gewonnene Aufträge auf 100 %.   '
              '📅  Projektstart (O) und Projektende (P) als echtes Datum TT.MM.JJJJ — die Dauer (G) rechnet sich daraus.   '
              '📋  WON verlangt Auftrags-/PO-Nr. (AF) und Belegdatum (AG) — Definitionen im Blatt «📋 Definitionen & Klärung».')
pipe['O5'].comment = Comment('Erster Tag des Projekts als echtes Datum (TT.MM.JJJJ).\n'
                            'Solange leer, meldet der Prüfstatus den fehlenden Zeitraum.\n'
                            'Aus Projektstart und Projektende rechnet sich die Dauer in Spalte G.',
                            'Reporting')
pipe['P5'].comment = Comment('Letzter Tag des Projekts als echtes Datum (TT.MM.JJJJ).\n'
                            'Dauer = Projektende − Projektstart + 1, beide Tage zählen mit.',
                            'Reporting')
pipe['G5'].value = 'Dauer\nTage'
pipe['G5'].comment = Comment('Kalendertage, gerechnet als Projektende − Projektstart + 1.\n'
                            'Solange kein Zeitraum erfasst ist, steht hier der bisher von Hand\n'
                            'eingetragene Wert (gesichert in der ausgeblendeten Spalte AW).',
                            'Reporting')

pipe.print_area = f"'{PIPE}'!$A$1:$AH${PRINT_LAST}"
pipe.page_setup.fitToWidth = 2


# =========================================================================
# 4) Kennzahlen "Qualität & Nachweis" in den Berichten
# =========================================================================
WON_BRUTTO = f'SUMIFS({VOL},{STA},"WON")'
WON_NETTO = f'SUMPRODUCT(--({STA}="WON"),{NETTN})'
WON_BELEGT = f'SUMPRODUCT({WONB},{INUM})'
AKT_BRUTTO = f'SUMPRODUCT({AKT},{INUM})'
AKT_BEREIN = f'SUMPRODUCT({AKT},{ZAEHLT},{INUM})'
AKT_CNT = f'SUMPRODUCT({AKT})'
NACHWEISQUOTE = f'IFERROR({WON_BELEGT}/{WON_BRUTTO},0)'
ZEIT_ERF = f'SUMPRODUCT({AKT},{ZEITOK})'
ZEIT_OFFEN = f'SUMPRODUCT({AKT},--({ZEITOK}=0))'
ZEIT_VOL = f'SUMPRODUCT({AKT},--({ZEITOK}=0),{INUM})'

KENN = [
    ('WON gemeldet (Status = WON, brutto wie erfasst)', f'={WON_BRUTTO}', '#,##0',
     'Summe aller Zeilen mit Status WON — inkl. MwSt, so wie erfasst.'),
    ('WON netto (ohne MwSt)', f'={WON_NETTO}', '#,##0',
     'Der Umsatz, der uns tatsächlich zusteht — ohne MwSt.'),
    ('davon belegt (Auftrags-/PO-Nr. + Datum + Einstand)', f'={WON_BELEGT}', '#,##0',
     'Nur dieser Teil ist im Sinne der Statusdefinition berichtsfähig.'),
    ('noch zu belegen', f'={WON_BRUTTO}-{WON_BELEGT}', '#,##0',
     'Fehlende Nachweise sind in der Pipeline in Spalte AH markiert.'),
    ('Aktive Pipeline brutto', f'={AKT_BRUTTO}', '#,##0',
     'Alle aktiven Status, ohne LOST und Declined.'),
    ('Aktive Pipeline bereinigt um Varianten', f'={AKT_BEREIN}', '#,##0',
     'Ohne Zeilen, die als «Alternative – zählt nicht» markiert sind.'),
    ('Nachweisquote des Auftragseingangs', f'={NACHWEISQUOTE}', '0.0%',
     'Belegtes WON im Verhältnis zum gemeldeten WON.'),
    ('Deals mit erfasstem Projektzeitraum', f'={ZEIT_ERF}', '0',
     'Projektstart und Projektende stehen als echtes Datum in den Spalten O und P.'),
    ('Deals ohne Projektzeitraum', f'={ZEIT_OFFEN}', '0',
     'Ohne Zeitraum lässt sich weder planen noch nach Monat auswerten.'),
    ('Volumen ohne Projektzeitraum', f'={ZEIT_VOL}', '#,##0',
     'Dieser Teil der Pipeline ist zeitlich noch nicht eingeordnet.'),
]


MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
          'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']


def monat_formeln(jahr, m):
    """Anzahl, Volumen und Anteil der aktiven Deals mit Start in diesem Monat."""
    treffer = f'{AKT},--({MONAT}=DATE({jahr},{m},1))'
    return (f'=SUMPRODUCT({treffer})',
            f'=SUMPRODUCT({treffer},{INUM})',
            f'=IFERROR(SUMPRODUCT({treffer},{INUM})/{AKT_BRUTTO},0)')


def monat_rest(jahr):
    """Zeilen ausserhalb des Bezugsjahrs und Zeilen ohne Zeitraum."""
    ausser = (f'{AKT},{ZEITOK},--({MONAT}<DATE({jahr},1,1))+--({MONAT}>DATE({jahr},12,1))')
    ohne = f'{AKT},--({ZEITOK}=0)'
    return [('andere Jahre', '—',
             f'=SUMPRODUCT({ausser})', f'=SUMPRODUCT({ausser},{INUM})',
             f'=IFERROR(SUMPRODUCT({ausser},{INUM})/{AKT_BRUTTO},0)'),
            ('ohne erfassten Zeitraum', '—',
             f'=SUMPRODUCT({ohne})', f'=SUMPRODUCT({ohne},{INUM})',
             f'=IFERROR(SUMPRODUCT({ohne},{INUM})/{AKT_BRUTTO},0)')]


def qualitaetsblock(sheet, lastcol, start, footer_from):
    """Setzt den Block 'Qualitaet & Nachweis' und verschiebt die Fusszeile."""
    sh = wb[sheet]
    old_merge = [str(m) for m in sh.merged_cells.ranges if m.min_row == footer_from]
    for m in old_merge:
        sh.unmerge_cells(m)
    foot_val = sh[f'A{footer_from}'].value
    foot_style = copy(sh[f'A{footer_from}']._style)
    sh[f'A{footer_from}'].value = None

    r = start
    put(sh, f'A{r}', '📋  5. QUALITÄT & NACHWEIS — Auftragsstatus, Nachweis und Projektzeitraum',
        A(11, True, 'FFFFFFFF'), GREEN, align='left', border=True)
    sh.merge_cells(f'A{r}:{lastcol}{r}')
    sh.row_dimensions[r].height = 24
    r += 1
    for co, t in ((f'A{r}', 'Kennzahl'), (f'E{r}', 'Wert'), (f'F{r}', 'Erläuterung')):
        put(sh, co, t, A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
    for co in 'BCD':
        put(sh, f'{co}{r}', None, fillc=SLATE, border=True)
    for co in [chr(x) for x in range(ord('G'), ord(lastcol) + 1)]:
        put(sh, f'{co}{r}', None, fillc=SLATE, border=True)
    sh.merge_cells(f'A{r}:D{r}')
    sh.merge_cells(f'F{r}:{lastcol}{r}')
    sh.row_dimensions[r].height = 20
    r += 1
    for label, formula, fmt, hint in KENN:
        bg = AMBER if 'belegt' in label or 'ohne' in label or 'über' in label else LIGHT
        put(sh, f'A{r}', label, A(10), bg, align='left', border=True)
        for co in 'BCD':
            put(sh, f'{co}{r}', None, fillc=bg, border=True)
        put(sh, f'E{r}', formula, A(11, True, NAVY), bg, fmt=fmt, align='right', border=True)
        put(sh, f'F{r}', hint, A(9, italic=True, color='FF64748B'), bg, align='left', border=True)
        for co in [chr(x) for x in range(ord('G'), ord(lastcol) + 1)]:
            put(sh, f'{co}{r}', None, fillc=bg, border=True)
        sh.merge_cells(f'A{r}:D{r}')
        sh.merge_cells(f'F{r}:{lastcol}{r}')
        sh.row_dimensions[r].height = 18
        r += 1
    put(sh, f'A{r}', '="Offene Pflichtangaben: "&' + DQ + '!$C$' + str(GESAMT_ROW) +
        '&"   ·   Definitionen, Kalkulationsregeln und offene Punkte: Blatt «📋 Definitionen & Klärung»"',
        A(9, italic=True, color='FF64748B'), align='left')
    sh.merge_cells(f'A{r}:{lastcol}{r}')
    sh.row_dimensions[r].height = 16
    r += 2

    # --- 6. Zeitliche Verteilung nach Monat des Projektstarts ------------
    put(sh, f'A{r}', '📅  6. ZEITLICHE VERTEILUNG — aktive Pipeline nach Monat des Projektstarts',
        A(11, True, 'FFFFFFFF'), GREEN, align='left', border=True)
    sh.merge_cells(f'A{r}:{lastcol}{r}')
    sh.row_dimensions[r].height = 24
    r += 1
    jahr_row = r
    put(sh, f'A{r}', 'Bezugsjahr', A(10, True, NAVY), LIGHT, align='left', border=True)
    for co in 'BC':
        put(sh, f'{co}{r}', None, fillc=LIGHT, border=True)
    sh.merge_cells(f'A{r}:C{r}')
    put(sh, f'D{r}', '=YEAR(TODAY())', A(11, True, NAVY), INPUT_FILL, fmt='0',
        align='center', border=True)
    put(sh, f'E{r}', 'Jahr hier ändern, die Tabelle rechnet nach.',
        A(9, italic=True, color='FF64748B'), LIGHT, align='left', border=True)
    for co in [chr(x) for x in range(ord('F'), ord(lastcol) + 1)]:
        put(sh, f'{co}{r}', None, fillc=LIGHT, border=True)
    sh.merge_cells(f'E{r}:{lastcol}{r}')
    sh.row_dimensions[r].height = 18
    r += 1
    for co, t in ((f'A{r}', 'Monat'), (f'D{r}', 'Quartal'), (f'E{r}', 'Anzahl'),
                  (f'F{r}', 'Volumen CHF'), (f'G{r}', 'Anteil')):
        put(sh, co, t, A(9, True, 'FFFFFFFF'), SLATE, align='center', border=True)
    for co in 'BC':
        put(sh, f'{co}{r}', None, fillc=SLATE, border=True)
    for co in [chr(x) for x in range(ord('H'), ord(lastcol) + 1)]:
        put(sh, f'{co}{r}', None, fillc=SLATE, border=True)
    sh.merge_cells(f'A{r}:C{r}')
    sh.merge_cells(f'G{r}:{lastcol}{r}')
    sh.row_dimensions[r].height = 20
    r += 1
    monat_first = r
    jahr = f'$D${jahr_row}'
    zeilen = [(MONATE[m - 1], f'Q{(m - 1) // 3 + 1}') + monat_formeln(jahr, m)
              for m in range(1, 13)] + monat_rest(jahr)
    for name, quartal, anz, vol, ant in zeilen:
        bg = AMBER if quartal == '—' else LIGHT
        put(sh, f'A{r}', name, A(10), bg, align='left', border=True)
        for co in 'BC':
            put(sh, f'{co}{r}', None, fillc=bg, border=True)
        put(sh, f'D{r}', quartal, A(10), bg, align='center', border=True)
        put(sh, f'E{r}', anz, A(10, True, NAVY), bg, fmt='0', align='center', border=True)
        put(sh, f'F{r}', vol, A(10, True, NAVY), bg, fmt='#,##0', align='right', border=True)
        put(sh, f'G{r}', ant, A(10), bg, fmt='0.0%', align='center', border=True)
        for co in [chr(x) for x in range(ord('H'), ord(lastcol) + 1)]:
            put(sh, f'{co}{r}', None, fillc=bg, border=True)
        sh.merge_cells(f'A{r}:C{r}')
        sh.merge_cells(f'G{r}:{lastcol}{r}')
        sh.row_dimensions[r].height = 17
        r += 1
    put(sh, f'A{r}', 'TOTAL aktive Pipeline', A(11, True, 'FFFFFFFF'), DARK, align='left', border=True)
    for co in 'BCD':
        put(sh, f'{co}{r}', None, fillc=DARK, border=True)
    sh.merge_cells(f'A{r}:D{r}')
    put(sh, f'E{r}', f'=SUM(E{monat_first}:E{r-1})', A(11, True, 'FFFFFFFF'), DARK,
        fmt='0', align='center', border=True)
    put(sh, f'F{r}', f'=SUM(F{monat_first}:F{r-1})', A(12, True, GOLD), DARK,
        fmt='#,##0', align='right', border=True)
    put(sh, f'G{r}', f'=SUM(G{monat_first}:G{r-1})', A(11, True, 'FFFFFFFF'), DARK,
        fmt='0.0%', align='center', border=True)
    for co in [chr(x) for x in range(ord('H'), ord(lastcol) + 1)]:
        put(sh, f'{co}{r}', None, fillc=DARK, border=True)
    sh.merge_cells(f'G{r}:{lastcol}{r}')
    sh.row_dimensions[r].height = 22
    r += 2
    sh[f'A{r}'].value = foot_val
    sh[f'A{r}']._style = foot_style
    sh.merge_cells(f'A{r}:{lastcol}{r}')
    sh.row_dimensions[r].height = 13.5
    sh.print_area = f"'{sheet}'!$A$1:${lastcol}${r}"
    return r


qualitaetsblock('Dashboard', 'K', 218, 216)
qualitaetsblock('CEO Report', 'L', 218, 216)

# --- CEO Report: Projektzeitraum, Nachweis und Prüfstatus je Deal --------
# Die Margenspalte faellt weg. An ihre Stelle rueckt «Leistung / Fleet»,
# und die beiden Datumsspalten stehen direkt hinter dem Segment.
ceo = wb['CEO Report']
CEO_SPALTEN = [
    ('E', 'Projektstart', 'zeit_von'),
    ('F', 'Projektende', 'zeit_bis'),
    ('I', 'Leistung / Fleet', '$E'),
    ('M', 'Auftrag / PO-Nr.', '$AF'),
    ('N', 'Prüfstatus', '$BB'),
]
for blk in (10, 74, 138):
    for co, t, _src in CEO_SPALTEN:
        ceo[f'{co}{blk}']._style = copy(ceo[f'L{blk}']._style)
        ceo[f'{co}{blk}'].value = t


def zeilenformel(src, xr):
    """Wert der Pipeline-Spalte src fuer die im Block referenzierte Zeile."""
    if src == 'zeit_von':
        # Solange kein echtes Datum erfasst ist, bleibt die bisherige grobe
        # Monatsangabe sichtbar - der Bericht verliert keine Information.
        return (f'=IF($U{xr}="","",IF(ISNUMBER(INDEX({PQ}!$O$1:$O${LAST},$U{xr})),'
                f'INDEX({PQ}!$O$1:$O${LAST},$U{xr}),'
                f'IF(INDEX({PQ}!$H$1:$H${LAST},$U{xr})="","",INDEX({PQ}!$H$1:$H${LAST},$U{xr}))))')
    if src == 'zeit_bis':
        return (f'=IF($U{xr}="","",IF(ISNUMBER(INDEX({PQ}!$P$1:$P${LAST},$U{xr})),'
                f'INDEX({PQ}!$P$1:$P${LAST},$U{xr}),""))')
    return (f'=IF($U{xr}="","",IF(INDEX({PQ}!{src}$1:{src}${LAST},$U{xr})="","",'
            f'INDEX({PQ}!{src}$1:{src}${LAST},$U{xr})))')


for first, last in ((11, 72), (75, 136), (139, 200)):
    for xr in range(first, last + 1):
        for co, _t, src in CEO_SPALTEN:
            c = ceo[f'{co}{xr}']
            c._style = copy(ceo[f'L{xr}']._style)
            c.value = zeilenformel(src, xr)
            if src in ('zeit_von', 'zeit_bis'):
                c.number_format = 'DD.MM.YYYY'
                c.alignment = Alignment(horizontal='center', vertical='center')
ceo.print_area = ceo.print_area.replace('$L$', '$N$')
for r in (5, 8, 9, 73, 137, 201, 202, 203, 204, 206, 214):
    for m in [str(x) for x in ceo.merged_cells.ranges if x.min_row == r and x.max_col == 12]:
        ceo.unmerge_cells(m)
        ceo.merge_cells(m.replace('L', 'N'))

# --- Dashboard: aus «Start» wird der Projektstart ------------------------
dash = wb['Dashboard']
for blk in (10, 74, 138):
    dash[f'E{blk}'].value = 'Projektstart'
for first, last in ((11, 72), (75, 136), (139, 200)):
    for xr in range(first, last + 1):
        c = dash[f'E{xr}']
        c.value = zeilenformel('zeit_von', xr)
        c.number_format = 'DD.MM.YYYY'
        c.alignment = Alignment(horizontal='center', vertical='center')


# --- 📑 Executive PDF: Nachweis und Projektzeitraum ----------------------
# Die Bandtabelle hat eine Zeile mehr (Stufe 100 %), deshalb ruecken die
# folgenden Bloecke um eine Zeile nach unten.
ex = wb['📑 Executive PDF']
EX_BLOCK = 42
if f'A{EX_BLOCK}:H{EX_BLOCK}' in [str(m) for m in ex.merged_cells.ranges]:
    ex.unmerge_cells(f'A{EX_BLOCK}:H{EX_BLOCK}')
ex_foot = ex[f'A{EX_BLOCK}'].value
ex_foot_style = copy(ex[f'A{EX_BLOCK}']._style)
ex[f'A{EX_BLOCK}'].value = None

ex[f'B{EX_BLOCK}']._style = copy(ex['B32']._style)
ex[f'B{EX_BLOCK}'].value = '📋  Nachweis & Zeitraum — wie die Zahlen zu lesen sind'
ex.merge_cells(f'B{EX_BLOCK}:G{EX_BLOCK}')

EX_KENN = [
    ('WON netto (ohne MwSt)', f'={WON_NETTO}', '#,##0'),
    ('davon durch Auftrag/PO belegt', f'={WON_BELEGT}', '#,##0'),
    ('Nachweisquote', f'={NACHWEISQUOTE}', '0.0%'),
    ('Deals mit erfasstem Projektzeitraum', f'={ZEIT_ERF}&" von "&{AKT_CNT}', 'General'),
]
body = copy(ex['D23']._style)
for i, (label, formula, fmt) in enumerate(EX_KENN):
    r = EX_BLOCK + 1 + i
    for co, val, f_ in ((f'B{r}', label, 'General'), (f'E{r}', formula, fmt)):
        c = ex[co]
        c._style = copy(body)
        c.value = val
        c.number_format = f_
        c.fill = fill(LIGHT if i < 2 else MINT)
    for co in ('C', 'D', 'F', 'G', 'H'):
        ex[f'{co}{r}']._style = copy(body)
        ex[f'{co}{r}'].fill = fill(LIGHT if i < 2 else MINT)
    ex[f'B{r}'].alignment = Alignment(horizontal='left', vertical='center')
    ex.merge_cells(f'B{r}:D{r}')
    ex.merge_cells(f'E{r}:F{r}')
    ex.merge_cells(f'G{r}:H{r}')

EX_HINWEIS = EX_BLOCK + 5
ex[f'B{EX_HINWEIS}'] = (f'="Offene Pflichtangaben: "&{DQ}!$C${GESAMT_ROW}'
                       f'&"  ·  Definitionen und offene Punkte: Blatt «📋 Definitionen & Klärung»"')
ex[f'B{EX_HINWEIS}'].font = Font(name='Cambria', size=9, italic=True, color='FF808080')
ex.merge_cells(f'B{EX_HINWEIS}:H{EX_HINWEIS}')
EX_ENDE = EX_BLOCK + 7
ex[f'A{EX_ENDE}'].value = ex_foot
ex[f'A{EX_ENDE}']._style = ex_foot_style
ex.merge_cells(f'A{EX_ENDE}:H{EX_ENDE}')
ex.print_area = f"'📑 Executive PDF'!$A$1:$H${EX_ENDE}"

# --- 📑 Executive PDF: Top-5-Liste mit Projektzeitraum statt Marge -------
# Spalte E zeigte den groben Startmonat, Spalte H die Marge. Neu stehen dort
# Projektstart und Projektende; fehlt das Datum, bleibt der Monat sichtbar.
ex['E13'].value = 'Projektstart'
ex['H13'].value = 'Projektende'
for i in range(1, 6):
    xr = 13 + i
    # Leere Zellen liefern über INDEX eine 0 - mit Datumsformat stuende dort
    # sonst der 00.01.1900. Deshalb jede Rueckgabe ausdruecklich auf leer pruefen.
    ziel = f'MATCH(LARGE({PQ}!$AK$6:$AK${LAST},{i}),{PQ}!$AK$6:$AK${LAST},0)'
    dat = f'INDEX({PQ}!$O$6:$O${LAST},{ziel})'
    grob = f'INDEX({PQ}!$H$6:$H${LAST},{ziel})'
    von = f'=IFERROR(IF(ISNUMBER({dat}),{dat},IF({grob}="","",{grob})),"")'
    ende = f'INDEX({PQ}!$P$6:$P${LAST},{ziel})'
    bis = f'=IFERROR(IF(ISNUMBER({ende}),{ende},""),"")'
    for co, formel in ((f'E{xr}', von), (f'H{xr}', bis)):
        c = ex[co]
        c.value = formel
        c.number_format = 'DD.MM.YYYY'
        c.alignment = Alignment(horizontal='center', vertical='center')

# --- 📄 Report: KPI-Zeilen und Top-WON-Liste -----------------------------
rp = wb['📄 Report']
for co, src in (('A12', 'A11'), ('B12', 'B11'), ('C12', 'C11'), ('D12', 'D11')):
    rp[co]._style = copy(rp[src]._style)
rp['A12'] = '📋 WON belegt'
rp['B12'] = f'={WON_BELEGT}'
rp['C12'] = f'=SUMPRODUCT({WONB})'
rp['D12'] = f'=IFERROR({WON_BELEGT}/SUMIFS({VOL},{STA},"WON"),0)'
rp['A12'].font = Font(name='Calibri', size=11, bold=True, color=NAVY)
rp['E12'] = f'={NACHWEISQUOTE}'
rp['E12']._style = copy(rp['E11']._style)
rp['E12'].number_format = '0.0%'

# Spalte F zeigte die Marge, Spalte G den groben Startmonat.
rp['F28'].value = 'Projektstart'
rp['G28'].value = 'Projektende'
for i in range(1, 11):
    xr = 28 + i
    # Leere Zellen liefern über INDEX eine 0 - mit Datumsformat stuende dort
    # sonst der 00.01.1900. Deshalb jede Rueckgabe ausdruecklich auf leer pruefen.
    ziel = f'MATCH(LARGE({PQ}!$AK$6:$AK${LAST},{i}),{PQ}!$AK$6:$AK${LAST},0)'
    dat = f'INDEX({PQ}!$O$6:$O${LAST},{ziel})'
    grob = f'INDEX({PQ}!$H$6:$H${LAST},{ziel})'
    von = f'=IFERROR(IF(ISNUMBER({dat}),{dat},IF({grob}="","",{grob})),"")'
    ende = f'INDEX({PQ}!$P$6:$P${LAST},{ziel})'
    bis = f'=IFERROR(IF(ISNUMBER({ende}),{ende},""),"")'
    for co, formel in ((f'F{xr}', von), (f'G{xr}', bis)):
        c = rp[co]
        c.value = formel
        c.number_format = 'DD.MM.YYYY'
        c.alignment = Alignment(horizontal='center', vertical='center')

# --- 📄 Report: zeitliche Verteilung nach Monat des Projektstarts --------
# Die Bandtabelle endet mit der Totalzeile; die Fussnote stand bisher direkt
# darunter und wandert ans Ende des neuen Blocks.
RPT_ROW = 50            # Totalzeile der Bandtabelle im Report
RP_FOOT_ALT = 53
for m in [str(x) for x in rp.merged_cells.ranges if m_ok(x, RP_FOOT_ALT)]:
    rp.unmerge_cells(m)
rp_foot = rp[f'A{RP_FOOT_ALT}'].value
rp_foot_style = copy(rp[f'A{RP_FOOT_ALT}']._style)
rp[f'A{RP_FOOT_ALT}'].value = None

r = RP_FOOT_ALT
rp[f'A{r}'] = '📅 Zeitliche Verteilung nach Monat des Projektstarts'
rp[f'A{r}']._style = copy(rp['A27']._style)
rp.merge_cells(f'A{r}:G{r}')
r += 1
jahr_row = r
rp[f'A{r}'] = 'Bezugsjahr'
rp[f'A{r}']._style = copy(rp['A28']._style)
rp[f'B{r}'] = '=YEAR(TODAY())'
rp[f'B{r}']._style = copy(rp['B29']._style)
rp[f'B{r}'].number_format = '0'
for co in 'CDE':
    rp[f'{co}{r}']._style = copy(rp[f'{co}29']._style)
r += 1
for co, t in (('A', 'Monat'), ('B', 'Quartal'), ('C', 'Anzahl'),
              ('D', 'Volumen CHF'), ('E', 'Anteil')):
    rp[f'{co}{r}'] = t
    rp[f'{co}{r}']._style = copy(rp[f'{co}28']._style)
r += 1
rp_first = r
jahr = f'$B${jahr_row}'
for name, quartal, anz, vol, ant in ([(MONATE[m - 1], f'Q{(m - 1) // 3 + 1}') + monat_formeln(jahr, m)
                                      for m in range(1, 13)] + monat_rest(jahr)):
    for co, val, fmt in (('A', name, 'General'), ('B', quartal, 'General'), ('C', anz, '0'),
                         ('D', vol, '#,##0" CHF"'), ('E', ant, '0.0%')):
        c = rp[f'{co}{r}']
        c._style = copy(rp[f'{co}29']._style)
        c.value = val
        c.number_format = fmt
    r += 1
for co, val, fmt in (('A', 'TOTAL aktiv', 'General'), ('B', None, 'General'),
                     ('C', f'=SUM(C{rp_first}:C{r-1})', '0'),
                     ('D', f'=SUM(D{rp_first}:D{r-1})', '#,##0" CHF"'),
                     ('E', f'=SUM(E{rp_first}:E{r-1})', '0.0%')):
    c = rp[f'{co}{r}']
    c._style = copy(rp[f'{co}{RPT_ROW}']._style)
    c.value = val
    c.number_format = fmt
r += 2
rp[f'A{r}'].value = rp_foot
rp[f'A{r}']._style = rp_foot_style
rp.merge_cells(f'A{r}:H{r}')
rp.print_area = f"'📄 Report'!$A$1:$G${r}"

wb.save(F)
print('Berichtsblöcke gesetzt')

