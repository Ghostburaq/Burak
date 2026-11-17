# -*- coding: utf-8 -*-
"""Erzeugt das HTML fuer die Unity-Eingabetabellen."""
import json, os, sys, html

DATA, OUT = sys.argv[1], sys.argv[2]
S = json.load(open(os.path.join(DATA, 'steps.json')))

TITEL = {
 'ZRH12_P01_Step_Timing_Diagnostic':    ('P01', 'Step Timing Diagnostic', 'Schrittzeit messen. Zuerst fahren.'),
 'ZRH12_P02_Cold_Start_Ramp_Acceptance':('P02', 'Cold Start Ramp Acceptance', 'Die vertraglich geforderte Rampe. Wichtigstes Programm.'),
 'ZRH12_P03_Ramp_and_L3_Transients':    ('P03', 'Ramp and L3 Transients', 'Voller Lauf mit Lastspruengen und thermischer Referenz.'),
 'ZRH12_P04_Overshoot_and_Thermal':     ('P04', 'Overshoot and Thermal', 'Drei Haltephasen, trennt Kabelverlust von Elementtemperatur.'),
 'ZRH12_P05_Step_Load_ISO8528':         ('P05', 'Step Load ISO 8528-5', 'Lastaufschaltung und Lastabwurf nach Norm.'),
 'ZRH12_P06_Full_Load_Heat_Run':        ('P06', 'Full Load Heat Run', 'Dauerlauf ueber zweieinhalb Stunden Lastzeit.'),
}
ORDER = ['ZRH12_P01_Step_Timing_Diagnostic','ZRH12_P02_Cold_Start_Ramp_Acceptance',
         'ZRH12_P03_Ramp_and_L3_Transients','ZRH12_P04_Overshoot_and_Thermal',
         'ZRH12_P05_Step_Load_ISO8528','ZRH12_P06_Full_Load_Heat_Run']

def hms(sec):
    sec=int(sec); return "%02d:%02d:%02d" % (sec//3600,(sec%3600)//60,sec%60)

def tabelle(rows):
    """Zweispaltig, Abschnittswechsel als Zwischenzeile."""
    half = (len(rows)+1)//2
    cols = [rows[:half], rows[half:]]
    out = '<div class="twocol">'
    for col in cols:
        out += '<table class="st"><tr><th>Nr</th><th>kW</th><th>%</th><th>cos&nbsp;&#966;</th><th>Haltezeit</th></tr>'
        last = None
        for nr, sec, kw, pc, pf, hold in col:
            if sec != last:
                out += '<tr class="sec"><td colspan="5">%s</td></tr>' % html.escape(sec or '-')
                last = sec
            out += ('<tr><td class="nr">%d</td><td class="b">%s</td><td>%s</td>'
                    '<td>%s</td><td class="m">%s</td></tr>' % (nr, kw, pc, pf, hold))
        out += '</table>'
    return out + '</div>'

pages = []
for key in ORDER:
    d = S[key]; nr, name, zweck = TITEL[key]
    warn = ''
    if d['steps'] > 16:
        warn = ('<div class="box warn"><h4>Mehr als 16 Schritte</h4><p style="margin:0">'
                'Dieses Programm hat <b>%d Schritte</b>. Die Sigma-Dokumentation nennt fuer den '
                'automatischen Testlauf 16 zeitgesteuerte Laststufen. Falls der Editor in Unity '
                'bei 16 abriegelt, das Programm in Bloecke aufteilen und nacheinander fahren. '
                'Die Schrittgrenzen stehen in der Spalte Abschnitt.</p></div>' % d['steps'])
    pages.append("""
<div class="page">
  <h2>%s &nbsp;%s</h2>
  <p class="lead">%s</p>
  <table class="kopf">
    <tr><td class="k">Schritte</td><td>%d</td><td class="k">Summe Haltezeit</td><td>%s</td>
        <td class="k">Hoechste Last</td><td>%g kW</td></tr>
    <tr><td class="k">cos &#966;</td><td>1,00 durchgehend</td><td class="k">Bezug 100 %%</td><td>2750 kW</td>
        <td class="k">Lastart</td><td>nur Wirklast</td></tr>
  </table>
  %s
  %s
</div>""" % (nr, html.escape(name), html.escape(zweck), d['steps'], hms(d['hold']),
             d['maxkw'], warn, tabelle(d['rows'])))

HTML = """<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">
<title>ZRH12 Eingabetabellen Sigma Unity</title><style>
@page{ size:A4; margin:14mm 13mm 12mm 13mm; }
:root{ --red:#E00036; --ink:#141619; --grey:#5F6670; --line:#DCDFE4; --bg:#F5F6F8; --green:#2E8B48; }
*{box-sizing:border-box} html,body{margin:0;padding:0}
body{font-family:'Inter',Arial,sans-serif;color:var(--ink);font-size:9pt;line-height:1.45;
     -webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{page-break-after:always} .page:last-child{page-break-after:auto}
h1{font-size:26pt;line-height:1.1;margin:0;font-weight:800;letter-spacing:-.4pt}
h2{font-size:14pt;margin:0 0 2mm 0;font-weight:800;color:var(--red);
   border-bottom:1.5pt solid var(--red);padding-bottom:1.4mm}
h3{font-size:10pt;margin:4mm 0 1.4mm 0;font-weight:700}
h4{font-size:8.2pt;margin:0 0 1mm 0;font-weight:700;color:var(--red);
   text-transform:uppercase;letter-spacing:.7pt}
p{margin:0 0 2mm 0} ul,ol{margin:0 0 2mm 0;padding-left:4.5mm} li{margin-bottom:1mm}
.lead{font-size:9.4pt;color:var(--grey);margin-bottom:2.5mm}
.small{font-size:7.8pt;color:var(--grey)}
.mono{font-family:'DejaVu Sans Mono',monospace;font-size:8pt}
table{width:100%;border-collapse:collapse;margin:0 0 2.5mm 0}
th{background:var(--red);color:#fff;font-size:7.4pt;font-weight:700;text-align:left;padding:1.2mm 1.4mm}
td{padding:1.2mm 1.4mm;border-bottom:.5pt solid var(--line);vertical-align:top;font-size:8.4pt}
td.k{font-weight:700;color:var(--grey);font-size:7.6pt;text-transform:uppercase;letter-spacing:.4pt}
table.kopf td{border:none;padding:.9mm 1.4mm;background:var(--bg)}
.twocol{display:grid;grid-template-columns:1fr 1fr;gap:0 5mm}
table.st td{font-size:7.4pt;padding:.75mm 1.2mm;text-align:right}
table.st th{font-size:6.8pt;padding:1mm 1.2mm;text-align:right}
table.st th:first-child,table.st td.nr{text-align:left}
table.st td.b{font-weight:700}
table.st td.m{font-family:'DejaVu Sans Mono',monospace;font-size:7pt}
tr.sec td{background:#EFF1F4;font-weight:700;font-size:6.9pt;text-align:left;color:var(--grey);
          text-transform:uppercase;letter-spacing:.4pt;padding:1.1mm 1.2mm}
.box{border-left:3pt solid var(--red);background:var(--bg);padding:2.4mm 3mm;margin:0 0 3mm 0}
.box.warn{border-left-color:#C00028;background:#FDF0F3}
.box.ok{border-left-color:var(--green);background:#F1F8F3}
.box.warn h4{color:#C00028} .box.ok h4{color:var(--green)}
.cover{background:var(--red);color:#fff;padding:10mm 9mm 11mm 9mm;margin:4mm 0 0 0}
.cover .kick{font-size:8.4pt;letter-spacing:2.2pt;text-transform:uppercase;opacity:.9;margin-bottom:4mm}
.cover .sub{font-size:12pt;margin-top:5mm;font-weight:500;line-height:1.4}
.meta{display:grid;grid-template-columns:1fr 1fr;gap:0 8mm;margin-top:6mm}
.meta div{border-top:.8pt solid var(--line);padding:1.6mm 0;font-size:8.3pt}
.meta span{color:var(--grey);display:block;font-size:7.1pt;text-transform:uppercase;letter-spacing:.6pt}
.step{display:flex;gap:3mm;margin-bottom:2.4mm}
.sn{flex:0 0 6.6mm;height:6.6mm;border-radius:50%;background:var(--red);color:#fff;
    font-size:9pt;font-weight:800;display:flex;align-items:center;justify-content:center}
.st2{flex:1} .st2 b{display:block;font-size:9.4pt;margin-bottom:.5mm}
.fill{border-bottom:.8pt solid var(--grey);display:inline-block;min-width:40mm}
</style></head><body>

<div class="page">
  <div style="font-size:7.8pt;letter-spacing:2pt;text-transform:uppercase;color:var(--grey);font-weight:700">
    Mobil in Time AG &nbsp;&#183;&nbsp; An Aggreko Company</div>
  <div class="cover">
    <div class="kick">Eingabetabellen und Vorgehen</div>
    <h1>ZRH12 Testprogramme<br>f&#252;r SIGMA Unity</h1>
    <div class="sub">Die sechs Programme als Schritttabellen,<br>
      unabh&#228;ngig vom Dateiformat der Software.</div>
  </div>
  <div class="meta">
    <div><span>Projekt</span>ZRH12 Winterthur, Eneria CAT 3516</div>
    <div><span>Bezug 100 Prozent</span>2750 kW am Lastbank</div>
    <div><span>Dokument</span>TAB-MIT-ZRH12-001, Rev. 1</div>
    <div><span>Quelle</span>P01 bis P06, Fassung vom 17.11.2026</div>
    <div><span>Erstellt von</span>Burak &#220;c&#246;z</div>
    <div><span>Stand</span>__DATUM__</div>
  </div>

  <div class="box warn" style="margin-top:8mm">
    <h4>Warum keine fertigen Unity-Dateien beiliegen</h4>
    <p>Das Skriptformat von SIGMA Unity ist in keiner &#246;ffentlichen Unterlage beschrieben.
    Gepr&#252;ft wurden Brosch&#252;re, Produktseite, FAQ, Tutorienliste und die Handb&#252;cher der
    Lastbankserien. Auch das Installationspaket der Software gibt das Format nicht her.</p>
    <p style="margin-bottom:0"><b>Ein geratenes Format w&#252;rde auf der Baustelle genauso
    scheitern wie die .tst-Dateien.</b> Deshalb enth&#228;lt dieses Dokument die Programme als
    Schritttabellen, die sich in jeden Testeditor eintippen lassen, und auf Seite 2 steht,
    was gebraucht wird, um die Dateien doch noch automatisch zu erzeugen.</p>
  </div>
  <div class="box ok">
    <h4>Zus&#228;tzlich im Ordner</h4>
    <p style="margin-bottom:0">Zu jedem Programm liegt eine CSV-Datei bei, Trennzeichen
    Semikolon, mit denselben Spalten wie die Tabellen hier. Falls Unity einen Import f&#252;r
    Tabellen hat, ist das der schnellste Weg.</p>
  </div>
</div>

<div class="page">
  <h2>1 &nbsp;Erst diese f&#252;nf Minuten, bevor irgendwas abgetippt wird</h2>
  <p class="lead">Es kann sein, dass das Problem klein ist. Diese Punkte in dieser Reihenfolge pr&#252;fen.</p>

  <div class="step"><div class="sn">1</div><div class="st2">
    <b>Welchen Dateityp bietet der &#214;ffnen-Dialog an?</b>
    In Unity den Dialog zum Laden eines Testprogramms &#246;ffnen und das Auswahlfeld f&#252;r den
    Dateityp aufklappen. Dort stehen die Endungen, die Unity erwartet.
    <b>Diese Endungen notieren und mir schicken.</b> Steht dort .tst, liegt das Problem im
    Inhalt. Steht etwas anderes dort, liegt es an der Endung.<br>
    Notiert: <span class="fill" style="min-width:120mm"></span></div></div>

  <div class="step"><div class="sn">2</div><div class="st2">
    <b>Gibt es eine Importfunktion f&#252;r alte Programme?</b>
    In den Men&#252;s Setup und Settings nach Import, Legacy, Migrate oder SIGMA PC suchen.
    Unity fasst PC Basic, Network Pro und PC System zusammen, eine &#220;bernahme ist denkbar.</div></div>

  <div class="step"><div class="sn">3</div><div class="st2">
    <b>Wo legt Unity seine eigenen Programme ab?</b>
    Ein kleines Testprogramm mit drei Schritten in Unity anlegen und speichern. Dann im
    Dateisystem suchen, wohin es gespeichert wurde. Typische Orte sind der Installationsordner,
    ProgramData oder Dokumente.</div></div>

  <div class="step"><div class="sn">4</div><div class="st2">
    <b>Die mitgelieferten Vorlagen ansehen</b>
    Der Hersteller nennt als Merkmal <i>in-built load test templates</i>. Diese Vorlagen liegen
    als Dateien auf dem Rechner. Ordner suchen und Inhalt ansehen.</div></div>

  <div class="box warn">
    <h4>Das Eine, was alles l&#246;st</h4>
    <p>Schick mir <b>eine einzige in Unity gespeicherte Testdatei</b>, egal wie klein, oder den
    Inhalt des Vorlagenordners. Damit kann ich das Format Zeichen f&#252;r Zeichen nachbilden und
    alle sechs Programme in einem Durchgang erzeugen, so wie bei den .tst-Dateien.</p>
    <p style="margin-bottom:0">Ebenfalls hilfreich: ein Bildschirmfoto des &#214;ffnen-Dialogs mit
    aufgeklapptem Dateityp, und ein Foto der Fehlermeldung, die beim Laden einer .tst-Datei
    erscheint. Der genaue Wortlaut der Meldung sagt, woran es scheitert.</p>
  </div>

  <h3>Wenn nichts davon hilft</h3>
  <p>Avtron Support fragen, mit der konkreten Frage: <i>Can SIGMA Unity import load test
  programs created in SIGMA PC, file extension .tst? If not, what is the native test script
  format and is there a documented structure?</i><br>
  customercare@avtronpower.com, +44 1780 480033. Software-Version V1.04.89 angeben.</p>

  <h3>Reihenfolge beim Abtippen</h3>
  <p>Falls alles von Hand eingegeben werden muss, nicht alle sechs auf einmal.
  <b>P02 zuerst</b>, 23 Schritte, das ist die vertraglich geforderte Rampe und der Kern der
  Beanstandung. Danach <b>P01</b> f&#252;r die Schrittzeitmessung. Der Rest kann warten, bis das
  Format steht.</p>

  <div class="box">
    <h4>Beim Eintippen beachten</h4>
    <ul style="margin-bottom:0">
      <li>Arbeitsgr&#246;ssen auf <b>kW und cos &#966;</b> stellen, nicht auf Prozent. Die Sollwerte
        sind krumm, zum Beispiel 2298 kW.</li>
      <li>cos &#966; ist in allen Programmen durchgehend <b>1,00</b>.</li>
      <li>Die Spalte Prozent ist nur zur Kontrolle da, bezogen auf 2750 kW.</li>
      <li>Haltezeit ist die Zeit <b>nach</b> dem Schaltbefehl, bis der n&#228;chste Schritt kommt.</li>
      <li>Supply on Test vorher eintragen, sonst stimmen die Prozentwerte der Software nicht.</li>
    </ul>
  </div>
</div>
__PAGES__
</body></html>"""
HTML = HTML.replace('__DATUM__', '17.11.2026').replace('__PAGES__', ''.join(pages))

open(OUT, 'w', encoding='utf-8').write(HTML)
print("HTML geschrieben:", OUT, len(HTML), "Zeichen")
