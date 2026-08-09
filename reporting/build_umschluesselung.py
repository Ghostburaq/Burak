#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stufe 4: Umschluesselung der Wahrscheinlichkeiten auf die Aggreko-Skala.

Alle Werte ausserhalb 0/10/30/60/90 % werden auf eine Skalenstufe gesetzt.
Leitregel:
  1. Wenn eine Skalenstufe denselben Gewichtungsfaktor hat, wird sie gewaehlt -
     der gewichtete Umsatz bleibt dann unveraendert.
  2. Ist das unmoeglich, entscheidet die Aggreko-Definition der Stufe.
     Das betrifft nur 50 %: kein Skalenwert liegt im Band 45-59 % (Faktor 30 %).

Der bisherige Wert bleibt in der neuen Spalte AI erhalten, damit jede Aenderung
nachvollziehbar ist.
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from copy import copy

F = 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
PIPE, PROB = 'MiT Strom Pipeline', '⚖️ Wahrscheinlichkeit'
PQ, WQ = f"'{PIPE}'", f"'{PROB}'"
LAST, PRINT_LAST = 860, 90

DARK, SLATE, GREEN, GOLD = 'FF0D1117', 'FF1E293B', 'FF166534', 'FFD4A017'
NAVY, LIGHT, AMBER = 'FF1F3864', 'FFF8FAFC', 'FFFFF3CD'
MINT, ROSE, INPUT_FILL = 'FFDCFCE7', 'FFFEE2E2', 'FFFFF9C4'
thin = Side(style='thin', color='FFCBD5E1')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

SKALA = [0.0, 0.1, 0.3, 0.6, 0.9]


def faktor(p):
    """Aggreko-Gewichtungsfaktor eines Wahrscheinlichkeitswerts."""
    p = p if p <= 1 else p / 100
    if p < 0.45:
        return 0.0
    if p < 0.60:
        return 0.30
    if p < 0.90:
        return 0.50
    return 0.90


# Verbindliche Zuordnungstabelle. Die Begruendung steht im File.
UMSCHLUESSELUNG = {
    0.0: (0.0, 'Bereits auf der Skala.'),
    0.1: (0.1, 'Bereits auf der Skala.'),
    0.2: (0.3, 'Gleicher Gewichtungsfaktor (0 %). Von den Stufen mit Faktor 0 % beschreibt 30 % '
               '«lebt, aber offen ob on-hire» eine versendete Offerte am besten — 10 % wäre laut '
               'Aggreko ein blosser Platzhalter.'),
    0.5: (0.3, 'Einzige Stufe, bei der sich der Faktor ändert — es gibt keinen Skalenwert im Band '
               '45–59 %. Massgebend ist deshalb die Definition: 50 % heisst «kann so oder so ausgehen», '
               'und genau das beschreibt Aggreko mit 30 % («lebt, aber wir wissen nicht, ob es on-hire '
               'geht»). 60 % verlangt ausdrücklich «sehr gute Chance» und dass das Fleet-Team die '
               'On-/Off-Hire-Daten überwacht. Je Deal einzeln zu bestätigen.'),
    0.8: (0.6, 'Gleicher Gewichtungsfaktor (50 %). Der gewichtete Umsatz bleibt unverändert.'),
    0.9: (0.9, 'Bereits auf der Skala.'),
    1.0: (0.9, 'Gleicher Gewichtungsfaktor (90 %). Die Skala endet bei 90 % — ein Auftrag, der '
               'bereits erteilt ist, trägt den Status WON und nicht 100 %.'),
}


def A(sz=10, b=False, color='FF111111', italic=False):
    return Font(name='Arial', size=sz, bold=b, color=color, italic=italic)


def fill(rgb):
    return PatternFill('solid', fgColor=rgb)


def put(ws, co, value, font=None, bg=None, fmt=None, align=None, wrap=None, border=True):
    c = ws[co]
    c.value = value
    c.font = font or A(10)
    if bg:
        c.fill = fill(bg)
    if fmt:
        c.number_format = fmt
    c.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap)
    if border:
        c.border = BOX
    return c


wb = openpyxl.load_workbook(F)
pipe = wb[PIPE]
w = wb[PROB]

# =========================================================================
# 1) Spalte AI anlegen und die Umschluesselung anwenden
# =========================================================================
pipe.column_dimensions['AI'].width = 15
pipe.column_dimensions['AI'].hidden = False
pipe['AI5']._style = copy(pipe['S5']._style)
pipe['AI5'].value = 'Wahr. %\nbisher'

protokoll = {}
unbekannt = []
for r in range(6, LAST + 1):
    if pipe[f'B{r}'].value in (None, ''):
        continue
    s = pipe[f'S{r}'].value
    if not isinstance(s, (int, float)):
        continue
    s = round(float(s), 6)
    if s in UMSCHLUESSELUNG:
        neu = UMSCHLUESSELUNG[s][0]
    else:
        # Nicht vorgesehener Wert: Stufe mit demselben Faktor, sonst die naechste.
        gleich = [x for x in SKALA if abs(faktor(x) - faktor(s)) < 1e-9]
        neu = min(gleich or SKALA, key=lambda x: (abs(x - s), -x))
        unbekannt.append((r, s, neu))
    alt_style = copy(pipe[f'S{r}']._style)
    pipe[f'AI{r}']._style = alt_style
    pipe[f'AI{r}'].value = s
    pipe[f'AI{r}'].number_format = '0%'
    if abs(neu - s) > 1e-9:
        pipe[f'S{r}'].value = neu
        protokoll.setdefault(s, [0, neu])[0] += 1
    else:
        protokoll.setdefault(s, [0, neu])[0] += 0

print('Umschlüsselung angewendet:')
for alt in sorted(protokoll):
    n, neu = protokoll[alt]
    kennz = 'unverändert' if abs(faktor(alt) - faktor(neu)) < 1e-9 else 'FAKTOR ÄNDERT SICH'
    print(f'   {alt:>5.0%} -> {neu:>4.0%}   {n:>3} Zeilen geändert   Gewicht {kennz}')
if unbekannt:
    print('   Nicht vorgesehene Werte automatisch zugeordnet:', unbekannt)

pipe['AI5'].alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
pipe.print_area = f"'{PIPE}'!$A$1:$AI${PRINT_LAST}"

# Bisherige Werte, die abweichen, dezent markieren
pipe.conditional_formatting.add('AI6:AI860', FormulaRule(
    formula=['AND($B6<>"",ISNUMBER($AI6),$AI6<>$S6)'],
    fill=fill('FFF1F5F9'),
    font=Font(name='Arial', size=10, italic=True, color='FF64748B'), stopIfTrue=False))

# =========================================================================
# 2) Protokoll auf dem Blatt "⚖️ Wahrscheinlichkeit"
# =========================================================================
start = max((c.row for row_ in w.iter_rows() for c in row_ if c.value is not None), default=37) + 3
row = start
ALT = f'{PQ}!$AI$6:$AI${LAST}'
NEU = f'{PQ}!$S$6:$S${LAST}'
VOL = f'{PQ}!$I$6:$I${LAST}'
KUN = f'{PQ}!$B$6:$B${LAST}'
AKT = f'{PQ}!$AP$6:$AP${LAST}'
INUM = f'{PQ}!$AL$6:$AL${LAST}'

w.merge_cells(f'A{row}:H{row}')
put(w, f'A{row}', '5️⃣   Umschlüsselung auf die Aggreko-Skala  —  was geändert wurde und was es bewirkt',
    A(11, True, 'FFFFFFFF'), GREEN, align='left', border=False)
w.row_dimensions[row].height = 22
row += 1

w.merge_cells(f'A{row}:H{row}')
put(w, f'A{row}', 'Wichtig: kein Wert der Skala 0/10/30/60/90 % fällt in das Gewichtungsband 45–59 % (Faktor 30 %). '
                  'Wer die Skala einhält, kann dieses Band nie treffen — es ist in der Aggreko-Vorgabe angelegt, '
                  'aber nicht erreichbar. Genau dort lagen bisher die 50 %-Deals.',
    A(9, True, 'FF9A3412'), AMBER, align='left', wrap=True)
w.row_dimensions[row].height = 30
row += 1

for co, t in (('A', 'bisher'), ('B', 'neu'), ('C', 'Faktor bisher'), ('D', 'Faktor neu'),
              ('E', 'Zeilen'), ('F', 'Gewichtet bisher'), ('G', 'Gewichtet neu'), ('H', 'Wirkung')):
    put(w, f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True)
w.row_dimensions[row].height = 26
row += 1
tab_first = row

for alt in sorted(UMSCHLUESSELUNG):
    neu, _ = UMSCHLUESSELUNG[alt]
    gleich = abs(faktor(alt) - faktor(neu)) < 1e-9
    bg = MINT if gleich else ROSE
    put(w, f'A{row}', alt, A(10, True, NAVY), bg, fmt='0%', align='center')
    put(w, f'B{row}', neu, A(10, True, NAVY), bg, fmt='0%', align='center')
    put(w, f'C{row}', faktor(alt), A(10), bg, fmt='0%', align='center')
    put(w, f'D{row}', faktor(neu), A(10), bg, fmt='0%', align='center')
    # Nur Zeilen mit Kunde zaehlen - sonst wuerden die leeren Vorratszeilen
    # beim Wert 0 % mitgezaehlt (leer wird zu 0 gerundet).
    put(w, f'E{row}', f'=SUMPRODUCT(--({KUN}<>""),--({ALT}<>""),--(ROUND({ALT},6)={alt}))',
        A(10), bg, fmt='0', align='center')
    put(w, f'F{row}', f'=SUMPRODUCT(--({KUN}<>""),--({ALT}<>""),--(ROUND({ALT},6)={alt}),{INUM})*{faktor(alt)}',
        A(10), bg, fmt='#,##0', align='right')
    put(w, f'G{row}', f'=SUMPRODUCT(--({KUN}<>""),--({ALT}<>""),--(ROUND({ALT},6)={alt}),{INUM})*{faktor(neu)}',
        A(10, True), bg, fmt='#,##0', align='right')
    put(w, f'H{row}', 'unverändert' if gleich else 'Faktor ändert sich',
        A(9, True, GREEN if gleich else 'FF991B1B'), bg, align='center', wrap=True)
    w.row_dimensions[row].height = 18
    row += 1
tab_last = row - 1

put(w, f'A{row}', 'TOTAL', A(10, True, 'FFFFFFFF'), DARK, align='center')
for co in 'BCD':
    put(w, f'{co}{row}', None, bg=DARK)
w.merge_cells(f'A{row}:D{row}')
put(w, f'E{row}', f'=SUM(E{tab_first}:E{tab_last})', A(10, True, 'FFFFFFFF'), DARK, fmt='0', align='center')
put(w, f'F{row}', f'=SUM(F{tab_first}:F{tab_last})', A(11, True, GOLD), DARK, fmt='#,##0', align='right')
put(w, f'G{row}', f'=SUM(G{tab_first}:G{tab_last})', A(11, True, GOLD), DARK, fmt='#,##0', align='right')
put(w, f'H{row}', f'=TEXT(G{row}-F{row},"+#,##0;-#,##0")', A(10, True, 'FFFFFFFF'), DARK, align='center')
w.row_dimensions[row].height = 22
row += 2

# ---- Kontrollzeilen zur Umschluesselung ---------------------------------
KONTROLLE = [
    ('Aktive Deals ausserhalb der Skala (muss 0 sein)',
     f'=SUMPRODUCT({AKT},--({PQ}!$AQ$6:$AQ${LAST}=0))', '0'),
    ('Zeilen, deren gewichteter Wert sich durch die Umschlüsselung geändert hat',
     f'=SUMPRODUCT(--({KUN}<>""),--({ALT}<>""),--(ROUND({ALT},6)=0.5))', '0'),
    ('davon noch auf der Vorgabe 30 % — je Deal zu bestätigen',
     f'=SUMPRODUCT(--({KUN}<>""),--({ALT}<>""),--(ROUND({ALT},6)=0.5),--({NEU}=0.3))', '0'),
    ('bereits auf 60 % hochgestuft',
     f'=SUMPRODUCT(--({KUN}<>""),--({ALT}<>""),--(ROUND({ALT},6)=0.5),--({NEU}=0.6))', '0'),
    ('Volumen der noch zu bestätigenden Deals',
     f'=SUMPRODUCT(--({KUN}<>""),--({ALT}<>""),--(ROUND({ALT},6)=0.5),--({NEU}=0.3),{INUM})', '#,##0'),
    ('Gewichtete Pipeline, wenn alle davon auf 60 % gehen',
     f'={WQ}!$G$20+SUMPRODUCT(--({KUN}<>""),--({ALT}<>""),--(ROUND({ALT},6)=0.5),--({NEU}=0.3),{INUM})*0.5', '#,##0'),
]
for label, formel, fmt in KONTROLLE:
    put(w, f'A{row}', label, A(10), LIGHT, align='left', wrap=True)
    for co in 'BCD':
        put(w, f'{co}{row}', None, bg=LIGHT)
    put(w, f'E{row}', formel, A(10, True, NAVY), AMBER, fmt=fmt, align='left')
    for co in 'FGH':
        put(w, f'{co}{row}', None, bg=AMBER)
    w.merge_cells(f'A{row}:D{row}')
    w.merge_cells(f'E{row}:H{row}')
    w.row_dimensions[row].height = 18
    row += 1
row += 1

# ---- Liste der einzeln zu bestaetigenden Deals --------------------------
w.merge_cells(f'A{row}:H{row}')
put(w, f'A{row}', 'Diese Deals standen auf 50 % und sind nach Aggreko-Definition auf 30 % gesetzt. '
                  'Wo das Fleet-Team die On-/Off-Hire-Daten bereits überwacht und die Chance sehr gut ist, '
                  'gehört der Deal auf 60 % — dann in Spalte S der Pipeline ändern, alles Weitere rechnet nach.',
    A(9, True, NAVY), AMBER, align='left', wrap=True)
w.row_dimensions[row].height = 30
row += 1
for co, t in (('A', 'Zeile'), ('B', 'Kunde'), ('E', 'Status'), ('F', 'Volumen CHF'),
              ('G', 'jetzt'), ('H', 'gewichtet')):
    put(w, f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True)
for co in 'CD':
    put(w, f'{co}{row}', None, bg=SLATE)
w.merge_cells(f'B{row}:D{row}')
w.row_dimensions[row].height = 18
row += 1

fuenfzig = [r for r in range(6, LAST + 1)
            if isinstance(pipe[f'AI{r}'].value, (int, float))
            and abs(pipe[f'AI{r}'].value - 0.5) < 1e-9]
for r in fuenfzig:
    put(w, f'A{row}', r, A(9, color='FF64748B'), LIGHT, fmt='0', align='center')
    put(w, f'B{row}', f'=INDEX({KUN},{r}-5)', A(10), LIGHT, align='left')
    for co in 'CD':
        put(w, f'{co}{row}', None, bg=LIGHT)
    put(w, f'E{row}', f'=INDEX({PQ}!$R$6:$R${LAST},{r}-5)', A(9), LIGHT, align='center')
    put(w, f'F{row}', f'=INDEX({VOL},{r}-5)', A(10), LIGHT, fmt='#,##0', align='right')
    put(w, f'G{row}', f'=INDEX({NEU},{r}-5)', A(10, True, NAVY), INPUT_FILL, fmt='0%', align='center')
    put(w, f'H{row}', f'=INDEX({PQ}!$Q$6:$Q${LAST},{r}-5)', A(10), LIGHT, fmt='#,##0', align='right')
    w.merge_cells(f'B{row}:D{row}')
    w.row_dimensions[row].height = 16
    row += 1

put(w, f'A{row}', 'Summe', A(10, True, 'FFFFFFFF'), DARK, align='center')
for co in 'BCDE':
    put(w, f'{co}{row}', None, bg=DARK)
w.merge_cells(f'A{row}:E{row}')
put(w, f'F{row}', f'=SUM(F{row-len(fuenfzig)}:F{row-1})', A(11, True, GOLD), DARK, fmt='#,##0', align='right')
put(w, f'G{row}', None, bg=DARK)
put(w, f'H{row}', f'=SUM(H{row-len(fuenfzig)}:H{row-1})', A(11, True, GOLD), DARK, fmt='#,##0', align='right')
w.row_dimensions[row].height = 20
row += 1

# Begruendungen der Zuordnung
row += 1
w.merge_cells(f'A{row}:H{row}')
put(w, f'A{row}', 'Begründung je Zuordnung', A(11, True, 'FFFFFFFF'), SLATE, align='left', border=False)
w.row_dimensions[row].height = 20
row += 1
for alt in sorted(UMSCHLUESSELUNG):
    neu, grund = UMSCHLUESSELUNG[alt]
    if abs(neu - alt) < 1e-9 and 'Skala' in grund:
        continue
    put(w, f'A{row}', f'{alt:.0%} → {neu:.0%}', A(10, True, NAVY), LIGHT, align='center')
    put(w, f'B{row}', grund, A(9), LIGHT, align='left', wrap=True)
    for co in 'CDEFGH':
        put(w, f'{co}{row}', None, bg=LIGHT)
    w.merge_cells(f'B{row}:H{row}')
    w.row_dimensions[row].height = 46
    row += 1

w.print_area = f"{WQ}!$A$1:$H${row}"
wb.save(F)
print(f'Protokoll auf «{PROB}» ab Zeile {start} geschrieben, Blatt endet bei {row}')
print(f'50-%-Deals zur Einzelbestätigung: {len(fuenfzig)}')
