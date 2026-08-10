#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stufe 3: Blatt "🔍 Herleitung & Formeln".

Schluesselt die gesamte Rechnung auf: Stufe fuer Stufe, mit durchgerechneten
Beispielen aus den echten Daten, der Herkunft jeder Berichtszahl, einem
vollstaendigen Spalten- und Funktionsverzeichnis und der Begruendung jedes
Designentscheids.
"""
import openpyxl, re
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from copy import copy

F = 'CH_MiT_Strom_Customer_CEO_CFO_MASTER.xlsx'
PIPE, PROB, DEF = 'MiT Strom Pipeline', '⚖️ Wahrscheinlichkeit', '📋 Definitionen & Klärung'
ERK = '🔍 Herleitung & Formeln'
PQ, WQ, DQ = f"'{PIPE}'", f"'{PROB}'", f"'{DEF}'"
LAST = 860

DARK, SLATE, GREEN, GOLD = 'FF0D1117', 'FF1E293B', 'FF166534', 'FFD4A017'
NAVY, LIGHT, AMBER = 'FF1F3864', 'FFF8FAFC', 'FFFFF3CD'
BLUE, MINT, ROSE = 'FF1D4ED8', 'FFDCFCE7', 'FFFEE2E2'
STEP = 'FFE0E7FF'
thin = Side(style='thin', color='FFCBD5E1')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def A(sz=10, b=False, color='FF111111', italic=False):
    return Font(name='Arial', size=sz, bold=b, color=color, italic=italic)


def MONO(sz=9, color='FF7C2D12'):
    return Font(name='Consolas', size=sz, color=color)


def fill(rgb):
    return PatternFill('solid', fgColor=rgb)


wb = openpyxl.load_workbook(F)
pipe = wb[PIPE]
# Totalzeile der Bandtabelle suchen statt fest eintragen - sie haengt an der
# Zahl der Gewichtungsbaender.
RT = next(r for r in range(1, 40) if wb[PROB][f'A{r}'].value == 'TOTAL aktiv')
if ERK in wb.sheetnames:
    del wb[ERK]
e = wb.create_sheet(ERK, wb.sheetnames.index(DEF) + 1)
e.sheet_properties.tabColor = BLUE
e.sheet_view.showGridLines = False
WIDTH = {'A': 3, 'B': 34, 'C': 46, 'D': 13, 'E': 16, 'F': 56, 'G': 3}
for c, w in WIDTH.items():
    e.column_dimensions[c].width = w

KUN = f'{PQ}!$B$6:$B${LAST}'


def cell(co, value, font=None, bg=None, fmt=None, align=None, wrap=None, border=True):
    c = e[co]
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


row = 1
e.merge_cells('A1:F1')
cell('A1', '🔍  Herleitung: wie jede Zahl entsteht — Rechenweg, Beispiele, Formeln und Begründungen',
     A(13, True, 'FFFFFFFF'), DARK, align='center', border=False)
e.row_dimensions[1].height = 34
e.merge_cells('A2:F2')
cell('A2', 'Mobil in Time AG · An Aggreko Company · Burak Ücöz  —  Dieses Blatt erklärt das Reporting von der '
           'Eingabe bis zur Kennzahl. Alle Zahlen darin rechnen live mit; die Beispiele suchen ihre Zeile über den '
           'Kundennamen und bleiben deshalb auch nach Umsortieren richtig.',
     A(9, False, 'FFAAAAAA'), DARK, align='left', wrap=True, border=False)
e.row_dimensions[2].height = 26
row = 4


def band(text, bg=GREEN):
    global row
    e.merge_cells(f'A{row}:F{row}')
    cell(f'A{row}', text, A(11, True, 'FFFFFFFF'), bg, align='left', border=False)
    e.row_dimensions[row].height = 22
    row += 1


def header(cols):
    global row
    for co, t in cols:
        cell(f'{co}{row}', t, A(9, True, 'FFFFFFFF'), SLATE, align='center', wrap=True)
    e.row_dimensions[row].height = 20
    row += 1


# =========================================================================
band('1️⃣   Der Rechenweg in sieben Stufen  —  von der Eingabe bis zur Kennzahl')
header([('B', 'Stufe'), ('C', 'Was passiert'), ('D', 'Ergebnis in'), ('E', 'Live-Wert'), ('F', 'Warum so')])

STUFEN = [
    ('① Erfassung',
     'Der Verkäufer trägt Volumen (I) und die vier Kostenarten Equipment (J), '
     'Transport (K), Treibstoff (L), Personal/Technik (M) ein, dazu Übrige Kosten (N).',
     'Spalte I–N', None, None,
     'Nur hier wird getippt. Alles Weitere rechnet die Mappe — so kann eine Zahl nicht an zwei '
     'Stellen unterschiedlich gepflegt werden.'),
    ('② Netto machen',
     'Nettoumsatz = Volumen ÷ Umrechnungsfaktor.',
     'Spalte Y', f'=SUMPRODUCT({PQ}!$AP$6:$AP${LAST},{PQ}!$AZ$6:$AZ${LAST})', '#,##0',
     'Die MwSt gehört weder in den Umsatz noch in die Kosten. Der Faktor steht als eine einzige '
     'Zelle im Definitionsblatt — umschaltbar, falls künftig netto erfasst wird.'),
    ('③ Einstand bilden',
     'Einstand = Equipment + Transport + Treibstoff + Personal + Übrige.',
     'Spalte Z', None, None,
     'Die Kosten bleiben als Arbeitsgrundlage in der Pipeline erfasst und als Summe sichtbar. '
     'Ausgewertet wird daraus im Bericht nichts mehr — die Marge ist bewusst nicht Teil des Reportings.'),
    ('④ Projektzeitraum',
     'Projektstart (O) und Projektende (P) als echtes Datum.   Dauer (G) = Ende − Start + 1 Tag.',
     'Spalte O / P / G', f'=SUMPRODUCT({PQ}!$AP$6:$AP${LAST},{PQ}!$AY$6:$AY${LAST})', '0',
     'Eine Monatsangabe wie «Aug» lässt sich weder sortieren noch summieren. Mit echten Daten '
     'entsteht die zeitliche Verteilung von selbst; der Live-Wert zeigt, wie viele aktive Deals '
     'einen Zeitraum haben.'),
    ('⑤ Nachweis prüfen',
     'Liegt Auftrags-/PO-Nummer mit Belegdatum vor? Ist der Einstand erfasst? Steht der Zeitraum? '
     'Jeder offene Punkt landet im Prüfstatus.',
     'Spalte AH', f'=SUMPRODUCT({PQ}!$AP$6:$AP${LAST},{PQ}!$AS$6:$AS${LAST})', '0',
     'Ein gemeldeter Auftrag ohne Beleg ist keine Zahl, auf die man planen kann. Der Prüfstatus '
     'nennt für jede Zeile, was fehlt — statt die Lücke im Bericht verschwinden zu lassen.'),
    ('⑥ Wahrscheinlichkeit gewichten',
     'Effektive Wahrscheinlichkeit (S) → Aggreko-Faktor über die Bandtabelle → '
     'Gew.Wert = Volumen × Faktor.',
     'Spalte Q', f'={WQ}!$G${RT}', '#,##0',
     'Der Faktor kommt aus einer Tabelle, nicht aus verschachtelten Bedingungen. Ändert Aggreko '
     'die Bänder, ist es eine Zeile im Blatt «⚖️ Wahrscheinlichkeit» und keine Formelarbeit.'),
    ('⑦ Verdichten',
     'Summen je Status, je Band, je Kanton, je Segment — plus die Nachweisquote.',
     'Berichte', f'=SUMPRODUCT({PQ}!$AP$6:$AP${LAST},{PQ}!$AL$6:$AL${LAST})', '#,##0',
     'Jede Verdichtung filtert über dieselben Hilfsspalten. Damit können zwei Berichte nicht '
     'unterschiedliche Antworten auf dieselbe Frage geben.'),
]
for nr, was, wo, live, fmt, warum in STUFEN:
    cell(f'B{row}', nr, A(10, True, NAVY), STEP, align='left', wrap=True)
    cell(f'C{row}', was, A(9), STEP, align='left', wrap=True)
    cell(f'D{row}', wo, A(9, True), STEP, align='center', wrap=True)
    cell(f'E{row}', live if live else '—', A(10, True, NAVY), AMBER if live else STEP,
         fmt=fmt, align='right' if live else 'center')
    cell(f'F{row}', warum, A(9, italic=True, color='FF475569'), STEP, align='left', wrap=True)
    e.row_dimensions[row].height = 42
    row += 1
cell(f'B{row}', 'Die Live-Werte oben sind: Nettoumsatz aktiv · Deals mit Projektzeitraum · Deals mit Beleg · '
                'gewichtete Pipeline · aktives Volumen brutto.',
     A(9, italic=True, color='FF64748B'), align='left', wrap=True, border=False)
e.merge_cells(f'B{row}:F{row}')
row += 2


# =========================================================================
def wasserfall(titel, kunde, farbe, extra=None):
    """Durchgerechnetes Beispiel: jede Stufe einzeln mit Live-Wert."""
    global row
    band(titel, farbe)
    header([('B', 'Rechenschritt'), ('C', 'Formel im File'), ('D', 'Spalte'),
            ('E', 'Wert CHF'), ('F', 'Erklärung')])

    def liv(col, fmt='#,##0'):
        # INDEX auf eine leere Zelle liefert 0 - bei einer Datumsspalte stuende
        # dort sonst der 00.01.1900. Deshalb ausdruecklich auf leer pruefen.
        idx = f'INDEX({PQ}!${col}$6:${col}${LAST},MATCH("{kunde}",{KUN},0))'
        return f'=IFERROR(IF({idx}="","",{idx}),"")'

    SCHRITTE = [
        ('Volumen wie erfasst (brutto)', 'Eingabe', 'I', liv('I'), '#,##0',
         'So steht es in der Offerte gegenüber dem Kunden — inklusive MwSt.'),
        ('÷ Umrechnungsfaktor', 'Volumen ÷ Netto_Faktor', 'Y', '=Netto_Faktor', '0.000',
         'Der Faktor ist 1 + MwSt-Satz, solange brutto erfasst wird.'),
        ('⇒ Nettoumsatz', 'Y = I ÷ Netto_Faktor', 'Y', liv('Y'), '#,##0',
         'Das ist der Umsatz, der uns tatsächlich zusteht.'),
        ('Equipment', 'Eingabe', 'J', liv('J'), '#,##0', 'Miete bzw. Einstand der Anlage.'),
        ('Transport', 'Eingabe', 'K', liv('K'), '#,##0', 'An- und Rücktransport.'),
        ('Treibstoff', 'Eingabe', 'L', liv('L'), '#,##0', 'Diesel bzw. Energie.'),
        ('Personal / Technik', 'Eingabe', 'M', liv('M'), '#,##0', 'Montage, Service, Bereitschaft.'),
        ('Übrige Kosten', 'Eingabe', 'N', liv('N'), '#,##0',
         'Alles Weitere — neu ohne MwSt, die Spalte hiess früher «Übrige / MwSt».'),
        ('⇒ Einstand', 'Z = SUMME(J:N)', 'Z', liv('Z'), '#,##0', 'Die Summe aller Kostenarten.'),
        ('Projektstart', 'Eingabe', 'O', liv('O'), 'DD.MM.YYYY',
         'Echtes Datum. Leer, solange der Zeitraum nicht feststeht.'),
        ('Projektende', 'Eingabe', 'P', liv('P'), 'DD.MM.YYYY', 'Echtes Datum.'),
        ('⇒ Dauer in Tagen', 'G = P − O + 1', 'G', liv('G'), '0',
         'Beide Tage zählen mit. Ohne Zeitraum bleibt der bisher erfasste Wert stehen.'),
        ('Wahrscheinlichkeit', 'Eingabe', 'S', liv('S'), '0%',
         'Aggreko-Skala 0/10/30/60/90 %, gewonnene Aufträge 100 %.'),
        ('→ Gewichtungsfaktor', 'AJ = LOOKUP über die Bandtabelle', 'AJ', liv('AJ'), '0%',
         'Band 0–44 → 0 %, 45–59 → 30 %, 60–89 → 50 %, 90–99 → 90 %, 100 % → 100 %.'),
        ('⇒ Gewichteter Wert', 'Q = I × AJ', 'Q', liv('Q'), '#,##0',
         'Bewusst auf das Volumen, nicht auf den Nettoumsatz — so verlangt es die Aggreko-Vorgabe.'),
        ('Prüfstatus', 'AH = Sammelbefund der Zeile', 'AH', liv('AH'), 'General',
         'Nennt jeden offenen Punkt der Zeile, nicht nur den ersten.'),
    ]
    for i, (label, formel, sp, val, fmt, erkl) in enumerate(SCHRITTE):
        bg = STEP if label.startswith(('⇒', '→')) else LIGHT
        cell(f'B{row}', label, A(10, label.startswith(('⇒', '→')), NAVY), bg, align='left', wrap=True)
        cell(f'C{row}', formel, MONO(), bg, align='left', wrap=True)
        cell(f'D{row}', sp, A(9), bg, align='center')
        cell(f'E{row}', val, A(10, True, NAVY), AMBER, fmt=fmt,
             align='left' if fmt == 'General' else 'right')
        cell(f'F{row}', erkl, A(9, italic=True, color='FF475569'), bg, align='left', wrap=True)
        e.row_dimensions[row].height = 20
        row += 1
    # Hinweis, falls der Beispielkunde umbenannt oder entfernt wurde -
    # sonst waere der ganze Block stillschweigend leer.
    cell(f'B{row}', 'Bezug des Beispiels', A(9, True, NAVY), LIGHT, align='left', wrap=True)
    cell(f'C{row}', f'Sucht die Zeile über den Kundennamen «{kunde}».', A(9), LIGHT,
         align='left', wrap=True)
    cell(f'D{row}', 'Spalte B', A(9), LIGHT, align='center')
    cell(f'E{row}', f'=IF(ISNUMBER(MATCH("{kunde}",{KUN},0)),"✔ gefunden",'
                    f'"⚠ nicht in der Pipeline")', A(9, True), AMBER, align='left')
    cell(f'F{row}', 'Steht hier eine Warnung, wurde der Kunde umbenannt oder entfernt — dann den Namen '
                    'in diesem Block anpassen.', A(9, italic=True, color='FF475569'), LIGHT,
         align='left', wrap=True)
    e.row_dimensions[row].height = 26
    row += 1

    if extra:
        for label, val, fmt, erkl in extra:
            cell(f'B{row}', label, A(10, True, 'FFFFFFFF'), NAVY, align='left', wrap=True)
            cell(f'C{row}', '', A(9), NAVY)
            cell(f'D{row}', '', A(9), NAVY)
            cell(f'E{row}', val, A(10, True, GOLD), NAVY, fmt=fmt, align='right')
            cell(f'F{row}', erkl, A(9, italic=True, color='FFCBD5E1'), NAVY, align='left', wrap=True)
            e.row_dimensions[row].height = 30
            row += 1
    row += 1


wasserfall('2️⃣   Beispiel A: laufende Offerte  —  «Wincasa Solothurn»', 'Wincasa Solothurn', GREEN,
           extra=[('Warum hier keine Marge steht', None, 'General',
                   'Die Kostenspalten sind erfasst und bleiben als Arbeitsgrundlage stehen. Ausgewertet '
                   'werden sie im Bericht nicht: auf der heutigen Datengrundlage stiftet eine ausgewiesene '
                   'Marge mehr Verunsicherung als Klarheit. Der Bericht zeigt Volumen, Status, Nachweis '
                   'und Zeitraum.')])

wasserfall('3️⃣   Beispiel B: gewonnener Auftrag  —  «DPR Heat Loadbank» (die Datacenter-Position)',
           'DPR Heat Loadbank', NAVY,
           extra=[('Was diese Zeile noch braucht', None, 'General',
                   'Status WON steht, damit gehört die Zeile auf 100 % und zählt mit dem vollen Volumen. '
                   'Fehlen Auftrags-/PO-Nummer, Belegdatum oder der Projektzeitraum, nennt der Prüfstatus '
                   'jeden dieser Punkte einzeln — und die Zeile zählt nicht zum belegten Auftragseingang.')])


# =========================================================================
band('4️⃣   Was die Umstellung zahlenmässig bewirkt  —  zwei Fälle, zwei Wirkungen')
header([('B', 'Fall'), ('C', 'Was vorher passierte'), ('D', 'Zeilen'), ('E', 'Wirkung'), ('F', 'Warum')])
FAELLE = [
    ('A — Spalte N enthielt die MwSt',
     'Vom Bruttoumsatz wurden die Kosten UND die MwSt abgezogen. Die MwSt war also doppelt drin: '
     'einmal im Bruttoumsatz enthalten, einmal als Kostenposition abgezogen.',
     36, 'Einstand bleibt gleich',
     'Brutto minus MwSt ergibt netto — rechnerisch dasselbe. Geändert hat sich, dass die MwSt nicht mehr '
     'als Kostenposition mitläuft: der Einstand in Spalte Z enthält jetzt ausschliesslich echte Kosten.'),
    ('B — Spalte N war eine echte Kostenposition',
     'Der Bruttoumsatz wurde als Umsatz behandelt, obwohl darin 8.1 % MwSt stecken.',
     30, 'Nettoumsatz sinkt um die MwSt',
     'Das ist die eigentliche Korrektur. Beispiel Wincasa: 390 000 brutto sind 360 777 netto, die Differenz '
     'von 29 223 ist exakt die MwSt. Der Umsatz war um diesen Betrag zu hoch angesetzt.'),
]
for fall, vorher, n, wirkung, warum in FAELLE:
    cell(f'B{row}', fall, A(10, True, NAVY), LIGHT, align='left', wrap=True)
    cell(f'C{row}', vorher, A(9), LIGHT, align='left', wrap=True)
    cell(f'D{row}', n, A(11, True, NAVY), LIGHT, fmt='0', align='center')
    cell(f'E{row}', wirkung, A(10, True), AMBER, align='center', wrap=True)
    cell(f'F{row}', warum, A(9, italic=True, color='FF475569'), LIGHT, align='left', wrap=True)
    e.row_dimensions[row].height = 62
    row += 1
row += 1


# =========================================================================
band('5️⃣   Woher jede Berichtszahl kommt  —  Landkarte der Verknüpfungen')
header([('B', 'Kennzahl im Bericht'), ('C', 'Wie sie gebildet wird'), ('D', 'Quelle'),
        ('E', 'Live-Wert'), ('F', 'Filter / Abgrenzung')])

AKT = f'{PQ}!$AP$6:$AP${LAST}'
INUM = f'{PQ}!$AL$6:$AL${LAST}'
KPI = [
    ('WON Umsatz', 'Summe Volumen über alle Zeilen mit Status WON',
     'Spalte I + R', f'=SUMIFS({PQ}!$I$6:$I${LAST},{PQ}!$R$6:$R${LAST},"WON")', '#,##0',
     'Brutto wie erfasst. Ohne Nachweisprüfung — deshalb daneben immer «davon belegt».'),
    ('WON netto', 'Summe der Nettoumsätze der WON-Zeilen',
     'Spalte AZ', f'=SUMPRODUCT(--({PQ}!$R$6:$R${LAST}="WON"),{PQ}!$AZ$6:$AZ${LAST})', '#,##0',
     'AZ ist der Nettoumsatz als reine Zahl (leere Zellen werden 0), damit SUMMENPRODUKT nicht über Text stolpert.'),
    ('WON belegt', 'Summe Volumen der Zeilen, die WON sind UND Beleg UND Einstand haben',
     'Spalte AT', f'=SUMPRODUCT({PQ}!$AT$6:$AT${LAST},{INUM})', '#,##0',
     'AT ist 1 nur wenn alle drei Bedingungen zugleich erfüllt sind.'),
    ('Aktive Pipeline', 'Summe Volumen über alle aktiven Status',
     'Spalte AP', f'=SUMPRODUCT({AKT},{INUM})', '#,##0',
     'Aktiv = die acht Status ohne LOST und Declined. Die Liste steht ausgeblendet im Blatt «⚖️ Wahrscheinlichkeit».'),
    ('Bereinigt um Varianten', 'wie oben, aber ohne als Alternative markierte Zeilen',
     'Spalte AU', f'=SUMPRODUCT({AKT},{PQ}!$AU$6:$AU${LAST},{INUM})', '#,##0',
     'AU ist 0 nur bei ausdrücklicher Markierung «Alternative – zählt nicht».'),
    ('Gewichtete Pipeline', 'Summe der Gew.Werte über die aktiven Status',
     'Spalte Q', f'={WQ}!$G${RT}', '#,##0',
     'Wird auf zwei Wegen gerechnet und im Blatt «⚖️ Wahrscheinlichkeit» gegeneinander geprüft.'),
    ('Nachweisquote', 'belegtes WON ÷ gemeldetes WON',
     'AT ÷ I', f'=IFERROR(SUMPRODUCT({PQ}!$AT$6:$AT${LAST},{INUM})/'
               f'SUMIFS({PQ}!$I$6:$I${LAST},{PQ}!$R$6:$R${LAST},"WON"),0)', '0.0%',
     'Zähler und Nenner über dieselbe Statusauswahl — die Quote sagt, wie viel des gemeldeten '
     'Auftragseingangs wirklich durch Auftrag oder PO gestützt ist.'),
    ('Deals mit Projektzeitraum', 'aktive Zeilen mit Projektstart UND Projektende',
     'Spalte AY', f'=SUMPRODUCT({AKT},{PQ}!$AY$6:$AY${LAST})', '0',
     'AY ist 1, wenn beide Daten echte Datumswerte sind und das Ende nicht vor dem Start liegt.'),
    ('Auswertung nach Monat', 'Volumen und Anzahl je Monat des Projektstarts',
     'Spalte AX', None, None,
     'AX ist der Monatsanfang des Projektstarts. Darüber gruppieren die Berichte nach Monat und Quartal.'),
    ('Top-Listen WON', 'GRÖSSTE über den Sortierschlüssel, dann Zeile über VERGLEICH holen',
     'Spalte AK', None, None,
     'AK trägt einen winzigen zeilenabhängigen Zuschlag, damit zwei betragsgleiche Deals nicht beide '
     'auf dieselbe Zeile treffen und einer doppelt erscheint.'),
    ('Kantone / Segmente', 'SUMMEWENN über Kanton bzw. Segment',
     'Spalte C / D', None, None,
     'Die Rangfolge nutzt denselben Zuschlag-Trick wie die Top-Listen.'),
]
for name, wie, quelle, live, fmt, filt in KPI:
    cell(f'B{row}', name, A(10, True, NAVY), LIGHT, align='left', wrap=True)
    cell(f'C{row}', wie, A(9), LIGHT, align='left', wrap=True)
    cell(f'D{row}', quelle, A(9), LIGHT, align='center', wrap=True)
    cell(f'E{row}', live if live else '—', A(10, True, NAVY), AMBER if live else LIGHT,
         fmt=fmt, align='right' if live else 'center')
    cell(f'F{row}', filt, A(9, italic=True, color='FF475569'), LIGHT, align='left', wrap=True)
    e.row_dimensions[row].height = 34
    row += 1
row += 1

# =========================================================================
band('6️⃣   Spaltenverzeichnis der Pipeline  —  jede Spalte, ihre Formel und wozu sie da ist')
header([('B', 'Spalte'), ('C', 'Formel in Zeile 6, ohne führendes «=» (Muster für alle Zeilen)'), ('D', 'Typ'),
        ('E', 'Sichtbar'), ('F', 'Wozu')])

ZWECK = {
    'A': 'Laufnummer aus dem Quellsystem.',
    'B': 'Kunde. Steuert alles: eine leere Zelle heisst «keine Zeile».',
    'C': 'Kanton — Grundlage der Kantonsauswertung.',
    'D': 'Segment — Grundlage der Segmentauswertung.',
    'E': 'Was geliefert wird.',
    'F': 'Leistung in kW.',
    'G': 'Mietdauer in Kalendertagen. Gerechnet als Projektende − Projektstart + 1, sobald beide '
         'Daten stehen; sonst der bisher von Hand erfasste Wert aus AW.',
    'H': 'Grobe Monatsangabe aus der Alterfassung. Bleibt als Anhaltspunkt stehen, solange kein '
         'echtes Datum erfasst ist.',
    'I': 'Volumen brutto, wie gegenüber dem Kunden offeriert. Die zentrale Eingabe.',
    'J': 'Einstand Equipment.',
    'K': 'Einstand Transport.',
    'L': 'Einstand Treibstoff.',
    'M': 'Einstand Personal / Technik.',
    'N': 'Übrige Kosten. Enthielt früher die MwSt — die ist entfernt.',
    'O': 'Projektstart als echtes Datum TT.MM.JJJJ. Eingabefeld, als Datum geprüft.',
    'P': 'Projektende als echtes Datum TT.MM.JJJJ. Eingabefeld, als Datum geprüft.',
    'Q': 'Gewichteter Wert nach Aggreko-Faktor.',
    'R': 'Status. Bestimmt, ob die Zeile aktiv ist und in welchem Block sie erscheint.',
    'S': 'Effektive Wahrscheinlichkeit. Dropdown mit der Aggreko-Skala; 100 % ist gewonnenen '
         'Aufträgen vorbehalten.',
    'T': 'Akquisetyp.',
    'U': 'USP-Argument.',
    'V': 'Nächster Schritt.',
    'W': 'Follow-Up.',
    'X': 'Interne Notiz.',
    'Y': 'Nettoumsatz — Volumen ohne MwSt.',
    'Z': 'Einstand — Summe der fünf Kostenarten.',
    'AA': 'Abwicklungsgesellschaft. Leer bedeutet MiT CH.',
    'AB': 'Vertragsart — entscheidet, ob ein Betrag ins WON gehört.',
    'AC': 'Deal-Gruppe — klammert Varianten desselben Entscheids.',
    'AD': 'Variante — «Alternative» fällt aus dem bereinigten Volumen.',
    'AE': 'Offert-Nummer.',
    'AF': 'Auftrags- bzw. PO-Nummer. Pflicht für WON.',
    'AG': 'Belegdatum. Pflicht für WON.',
    'AH': 'Prüfstatus — sammelt alle offenen Punkte der Zeile.',
    'AJ': 'Gewichtungsfaktor aus der Bandtabelle.',
    'AK': 'Sortierschlüssel der WON-Ranglisten, mit Zuschlag gegen Doppelnennungen.',
    'AL': 'Volumen als reine Zahl — 0 statt Text, damit Summen nicht brechen.',
    'AM': 'Laufender Zähler der WON-Zeilen — steuert den WON-Block der Berichte.',
    'AN': 'Laufender Zähler der Offert-Zeilen.',
    'AO': 'Laufender Zähler der Opportunitäts-Zeilen.',
    'AP': '1 = zählt zur aktiven Pipeline.',
    'AQ': '1 = Wahrscheinlichkeit liegt auf der Aggreko-Skala.',
    'AR': '1 = alle vier Kostenarten sind erfasst und die Summe ist grösser als null.',
    'AS': '1 = Auftrags-/PO-Nummer und Belegdatum vorhanden.',
    'AT': '1 = WON und belegt und Einstand erfasst.',
    'AU': '1 = zählt ins bereinigte Volumen.',
    'AV': '1 = dieser Kunde kommt mehrfach in der Pipeline vor.',
    'AW': 'Bisher von Hand erfasste Mietdauer. Bleibt stehen, solange kein Zeitraum erfasst ist.',
    'AX': 'Monatsanfang des Projektstarts — Grundlage der Auswertung nach Monat und Quartal.',
    'AY': '1 = Projektstart und Projektende sind erfasst und das Ende liegt nicht vor dem Start.',
    'AZ': 'Nettoumsatz als reine Zahl für die Summenbildung.',
    'BA': 'Sammeltext der Befunde, aus dem der Prüfstatus gebildet wird.',
    'BB': 'Kurzform des Prüfstatus für den CEO Report.',
}
for idx in range(1, 55):
    col = get_column_letter(idx)
    kopf = pipe[f'{col}5'].value
    if kopf is None and col not in ZWECK:
        continue
    f6 = pipe[f'{col}6'].value
    is_f = isinstance(f6, str) and f6.startswith('=')
    hid = pipe.column_dimensions[col].hidden
    bg = 'FFF1F5F9' if hid else (STEP if is_f else MINT)
    cell(f'B{row}', f'{col}  ·  {str(kopf).replace(chr(10), " ") if kopf else ""}',
         A(10, True, NAVY), bg, align='left', wrap=True)
    # Ohne fuehrendes "=", sonst wertet Excel den Text als Formel aus statt ihn zu zeigen
    cell(f'C{row}', (f6[1:181] if is_f else '—  (Eingabefeld)'), MONO(8), bg, align='left', wrap=True)
    cell(f'D{row}', 'Formel' if is_f else 'Eingabe', A(9), bg, align='center')
    cell(f'E{row}', 'ausgeblendet' if hid else 'ja', A(9), bg, align='center')
    cell(f'F{row}', ZWECK.get(col, ''), A(9, italic=True, color='FF475569'), bg, align='left', wrap=True)
    e.row_dimensions[row].height = 30
    row += 1
row += 1

# =========================================================================
band('7️⃣   Warum es so gebaut ist  —  die Entscheide und ihre Begründung')
header([('B', 'Entscheid'), ('C', 'Alternative, die verworfen wurde'), ('E', 'Begründung')])
e.merge_cells(f'C{row-1}:D{row-1}')
e.merge_cells(f'E{row-1}:F{row-1}')

WARUM = [
    ('Brutto/netto als umschaltbare Zelle statt fest verdrahtet',
     'Den Faktor 1.081 direkt in die Formeln schreiben.',
     'Die Erfassungsart ist eine Annahme, keine Naturkonstante. Sie steht jetzt an einer Stelle, ist '
     'begründet, und eine Umstellung ist ein Zellwert statt einer Formelrunde durch 855 Zeilen.'),
    ('Gewichtungsfaktor über eine Bandtabelle statt verschachtelter Bedingungen',
     'WENN(S<0.45;0;WENN(S<0.6;0.3;…)) in jeder Zeile.',
     'Ändert Aggreko die Bänder, ist es eine Zeile in der Tabelle. Verschachtelte Bedingungen müsste '
     'man in jeder Zeile anfassen — und jede Änderung wäre eine neue Fehlerquelle.'),
    ('Hilfsspalten statt langer Formeln in den Kennzahlen',
     'Die ganze Logik in jede Summenformel schreiben.',
     'Eine Bedingung wird einmal je Zeile gerechnet und danach nur noch multipliziert. Das ist schneller, '
     'und vor allem: jede Kennzahl filtert nachweislich über dieselbe Bedingung. Zwei Berichte können '
     'nicht auseinanderlaufen.'),
    ('Marge ganz aus dem Reporting genommen',
     'Die Marge weiter ausweisen und die Prüffälle daneben markieren.',
     'Bei einem Teil der Zeilen wurde nicht kalkuliert, sondern nur der Verkaufspreis aufgeteilt. Auf '
     'dieser Datengrundlage trägt keine Margenzahl. Die Kostenspalten bleiben als Arbeitsgrundlage in der '
     'Pipeline stehen — im Bericht steht dafür, was belastbar ist: Volumen, Status, Nachweis und Zeitraum.'),
    ('Projektzeitraum als zwei echte Datumsfelder',
     'Die grobe Monatsangabe beibehalten und daraus ein Datum ableiten.',
     'Aus «Aug» lässt sich kein Zeitraum rechnen und keine Dauer prüfen. Zwei geprüfte Datumsfelder '
     'liefern Dauer, Monat und Quartal von selbst — und ein leeres Feld ist eine ehrliche Aussage, '
     'während ein erfundenes Datum eine falsche wäre.'),
    ('Gewonnene Aufträge auf 100 %',
     'Gewonnene Aufträge weiter mit 90 % gewichten, wie es die Aggreko-Skala vorgibt.',
     'Ein unterschriebener Auftrag ist keine Wahrscheinlichkeit mehr, sondern ein Fakt. Die Aggreko-Skala '
     'endet bei 90 %, weil sie offene Opportunitäten bewertet. Die Stufe 100 % ist als Ergänzung '
     'gekennzeichnet und gilt ausschliesslich für Status WON.'),
    ('Keine harte Sperre auf dem Statusfeld',
     'Eine Gültigkeitsregel, die WON ohne Beleg blockiert.',
     'Eine Gültigkeitsprüfung greift nur beim Tippen — nicht beim Einfügen und nicht beim Import. Die '
     'Sperre wirkt deshalb über die Zahl: unbelegtes WON fällt aus der Kennzahl «belegt» und steht als '
     'offener Punkt im Bericht. Das lässt sich nicht umgehen.'),
    ('Nur ausdrücklich markierte Alternativen fallen weg',
     'Automatisch pro Deal-Gruppe nur die grösste Zeile zählen.',
     'Automatik würde bei einer vergessenen Gruppenzuordnung Volumen verschwinden lassen. So kann eine '
     'fehlende Markierung nie Umsatz kosten — sie erscheint stattdessen als offener Punkt.'),
    ('Zuschlag im Sortierschlüssel der Ranglisten',
     'Direkt nach dem Volumen sortieren.',
     'Bei zwei betragsgleichen WON-Deals trifft VERGLEICH beide Male dieselbe Zeile: einer stünde doppelt '
     'in der Top-Liste, ein anderer fiele heraus. Der Zuschlag liegt bei unter einem Rappen und macht '
     'jeden Schlüssel eindeutig.'),
    ('Gew.Wert auf das Volumen, nicht auf den Nettoumsatz',
     'Gewichtung auf den Nettoumsatz rechnen.',
     'Die Aggreko-Vorgabe lautet «total revenue × probability». Wir folgen ihr wörtlich, damit die Zahl '
     'mit der Gruppenauswertung vergleichbar bleibt.'),
    ('MwSt-Formeln aus Spalte N entfernt statt stehen gelassen',
     'Die Spalte unverändert lassen.',
     'Sonst wäre die MwSt weiterhin im Einstand enthalten und würde doppelt wirken. Die Spalte heisst '
     'jetzt «Übrige Kosten» und enthält ausschliesslich echte Kosten.'),
    ('Ganzspalten-Bezüge auf Zeile 860 begrenzt',
     'INDEX über die ganze Spalte laufen lassen.',
     'Rund 4 300 Formeln über je eine Million Zeilen. Fachlich identisch, aber spürbar langsamer — '
     'die Trefferzeile liegt ohnehin immer zwischen 6 und 860.'),
    ('Zwei Rechenwege für die gewichtete Pipeline',
     'Einmal rechnen und darauf vertrauen.',
     'Die Bandtabelle und die Spalte «Gew.Wert» rechnen unabhängig voneinander. Weichen sie ab, meldet '
     'das Blatt «⚖️ Wahrscheinlichkeit» es sofort — auch nachdem jemand Daten geändert hat.'),
]
for entscheid, alt, warum in WARUM:
    cell(f'B{row}', entscheid, A(10, True, NAVY), LIGHT, align='left', wrap=True)
    cell(f'C{row}', alt, A(9, italic=True, color='FF991B1B'), LIGHT, align='left', wrap=True)
    cell(f'D{row}', None, bg=LIGHT)
    cell(f'E{row}', warum, A(9), LIGHT, align='left', wrap=True)
    cell(f'F{row}', None, bg=LIGHT)
    e.merge_cells(f'C{row}:D{row}')
    e.merge_cells(f'E{row}:F{row}')
    e.row_dimensions[row].height = 48
    row += 1
row += 1

# =========================================================================
band('8️⃣   Funktionslexikon  —  jede verwendete Funktion und warum gerade sie')
header([('B', 'Funktion'), ('C', 'Was sie tut'), ('E', 'Wo im File')])
e.merge_cells(f'C{row-1}:D{row-1}')
e.merge_cells(f'E{row-1}:F{row-1}')

FUNK = [
    ('WENN / IF', 'Fallunterscheidung.',
     'Überall. Wichtig: WENN prüft nur den zutreffenden Zweig — anders als UND.'),
    ('UND / AND, ODER / OR', 'Mehrere Bedingungen verknüpfen.',
     'Statusprüfungen. Achtung: UND rechnet ALLE Argumente, auch die unzutreffenden. Deshalb sind die '
     'Zahlenprüfungen geschachtelt statt in ein UND gepackt — sonst rechnet die Formel mit Text weiter.'),
    ('ISTZAHL / ISNUMBER', 'Prüft, ob eine Zelle wirklich eine Zahl enthält.',
     'Vor jeder Rechnung. «tbd» oder «Sponsoring» im Volumenfeld darf keine Formel sprengen.'),
    ('SUMMEWENNS / SUMIFS', 'Summe mit Bedingungen.',
     'Alle Status-Summen. Ignoriert Text automatisch — deshalb stört ein «tbd» im Gew.Wert nicht.'),
    ('ZÄHLENWENN / COUNTIF', 'Zählt Treffer in einem Bereich.',
     'Statuszähler, Skalenprüfung, Mehrfachkunden. Achtung: eine leere Bezugszelle wird als 0 gelesen — '
     'deshalb steht vor der Skalenprüfung ein ISTZAHL.'),
    ('SUMMENPRODUKT / SUMPRODUCT', 'Multipliziert Spalten zeilenweise und summiert.',
     'Jede Auswertung mit mehreren Bedingungen. Arbeitet mit den 0/1-Hilfsspalten — dadurch kurz und '
     'schnell statt einer langen Bedingungskette.'),
    ('VERWEIS / LOOKUP', 'Sucht den grössten Wert, der nicht über dem Suchwert liegt.',
     'Die Zuordnung Wahrscheinlichkeit → Gewichtungsfaktor. Genau richtig für Bänder, weil die '
     'Untergrenzen aufsteigend sortiert sind.'),
    ('INDEX + VERGLEICH / MATCH', 'Holt den Wert aus Zeile n eines Bereichs.',
     'Alle Detailzeilen in Dashboard und CEO Report sowie die Ranglisten.'),
    ('GRÖSSTE / LARGE', 'Der n-grösste Wert eines Bereichs.',
     'Top-WON und Top-Kantone.'),
    ('WENNFEHLER / IFERROR', 'Fängt Fehlerwerte ab.',
     'Um jede Suche und jede Division. Eine leere Rangliste zeigt leere Zellen statt Fehlermeldungen.'),
    ('TEXT, LINKS / LEFT, LÄNGE / LEN', 'Zahlen formatieren, Texte zusammensetzen und kürzen.',
     'Die Hinweiszeilen und der Prüfstatus.'),
    ('RUNDEN / ROUND, ABS', 'Runden, Betrag ohne Vorzeichen.',
     'Die Abweichungskontrolle und die Schwellenprüfung.'),
    ('ZEILE / ROW', 'Zeilennummer.',
     'Der Zuschlag in den Sortierschlüsseln.'),
    ('HEUTE / TODAY', 'Tagesdatum.',
     'Die Kopf- und Fusszeilen.'),
    ('Bewusst NICHT verwendet', 'XVERWEIS, FILTER, EINDEUTIG, SORTIEREN, TEXTVERKETTEN.',
     'Diese Funktionen gibt es erst in neueren Excel-Versionen. Die Mappe soll auch in älterem Excel '
     'und in LibreOffice ohne Anpassung rechnen — deshalb durchgehend INDEX/VERGLEICH.'),
]
for fn, was, wo in FUNK:
    bg = AMBER if fn.startswith('Bewusst') else LIGHT
    cell(f'B{row}', fn, A(10, True, NAVY), bg, align='left', wrap=True)
    cell(f'C{row}', was, A(9), bg, align='left', wrap=True)
    cell(f'D{row}', None, bg=bg)
    cell(f'E{row}', wo, A(9, italic=True, color='FF475569'), bg, align='left', wrap=True)
    cell(f'F{row}', None, bg=bg)
    e.merge_cells(f'C{row}:D{row}')
    e.merge_cells(f'E{row}:F{row}')
    e.row_dimensions[row].height = 34
    row += 1

# ---------------------------------------------------------------- Waechter
# Ein Text, der mit "=" beginnt, wird von Excel als Formel gelesen. Beim Bauen
# faellt das sonst erst beim Neuberechnen auf.
# Auf diesem Blatt sind Formeln ausschliesslich in Spalte E vorgesehen (die
# Live-Werte). Alles andere ist Beschriftung - beginnt sie mit "=", wuerde
# Excel sie auswerten statt anzeigen.
verdaechtig = [f'{_c.coordinate}: {_c.value[:50]}'
               for _r in e.iter_rows() for _c in _r
               if isinstance(_c.value, str) and _c.value.startswith('=')
               and _c.column_letter != 'E']
if verdaechtig:
    raise SystemExit('Text wird als Formel gelesen: ' + '; '.join(verdaechtig))

e.print_area = f"'{ERK}'!$A$1:$F${row}"
e.page_setup.orientation = 'landscape'
e.page_setup.fitToWidth = 1
e.page_setup.fitToHeight = 0
e.sheet_properties.pageSetUpPr.fitToPage = True
e.freeze_panes = 'A4'

wb.save(F)
print(f'Blatt "{ERK}" angelegt, {row} Zeilen')
