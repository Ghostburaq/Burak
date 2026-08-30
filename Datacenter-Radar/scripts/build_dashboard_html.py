#!/usr/bin/env python3
"""
Generiert MiT_DC_Radar_Dashboard.html aus MiT_Datacenter_Radar_CH_V1.0.xlsx.

Liest nur, schreibt nie in die Excel. Nach jedem Montags-Lauf einmal
ausfuehren, dann ist die HTML-Ansicht aktuell. Die Ampel-Logik (Tage bis
Wiedervorlage) wird hier in Python gerechnet, weil openpyxl keine
Formelwerte liefert.

Aufruf:  python3 scripts/build_dashboard_html.py
"""

import datetime
import html
import json
import os
from openpyxl import load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
ORDNER = os.path.dirname(HERE)
QUELLE = os.path.join(ORDNER, "MiT_Datacenter_Radar_CH_V1.0.xlsx")
ZIEL = os.path.join(ORDNER, "MiT_DC_Radar_Dashboard.html")

HEUTE = datetime.date.today()
KW = HEUTE.isocalendar()[1]

wb = load_workbook(QUELLE, read_only=True)
ws = wb["02_Projekt_Radar"]


def txt(v):
    if v is None:
        return ""
    if isinstance(v, datetime.datetime):
        return v.strftime("%d.%m.%Y")
    if isinstance(v, datetime.date):
        return v.strftime("%d.%m.%Y")
    return str(v).strip()


def datum(v):
    if isinstance(v, (datetime.datetime, datetime.date)):
        return datetime.date(v.year, v.month, v.day)
    if isinstance(v, str):
        try:
            t, m, j = v.strip().split(".")
            return datetime.date(int(j), int(m), int(t))
        except (ValueError, AttributeError):
            return None
    return None


projekte = []
for row in ws.iter_rows(min_row=5, max_row=45, max_col=23, values_only=True):
    if not row[1]:
        continue
    q = datum(row[16])
    tage = (q - HEUTE).days if q else None
    if q is None:
        ampel = "-"
    elif tage < 0:
        ampel = "UEBERFAELLIG"
    elif tage <= 7:
        ampel = "DIESE WOCHE"
    else:
        ampel = "ok"
    mw = row[5]
    projekte.append({
        "projekt": txt(row[1]), "betreiber": txt(row[2]), "standort": txt(row[3]),
        "kt": txt(row[4]),
        "mw": float(mw) if isinstance(mw, (int, float)) else None,
        "mw_txt": txt(mw) if mw is not None else "",
        "phase": txt(row[6]) or "offen", "ibn": txt(row[7]),
        "gu": txt(row[8]), "planer": txt(row[9]), "kanal": txt(row[10]),
        "chance": txt(row[11]), "fenster": txt(row[12]), "prio": txt(row[13]) or "-",
        "status": txt(row[14]), "wv": txt(row[16]), "tage": tage, "ampel": ampel,
        "quellen": [u.strip() for u in txt(row[19]).split("|") if u.strip()],
        "stand": txt(row[20]), "schritt": txt(row[21]), "bemerkung": txt(row[22]),
    })

cl_ws = wb["06_Changelog"]
changelog = []
for row in cl_ws.iter_rows(min_row=5, max_col=6, values_only=True):
    if not row[2]:
        continue
    changelog.append({
        "datum": txt(row[0]), "projekt": txt(row[2]), "was": txt(row[3]),
        "url": txt(row[4]), "konsequenz": txt(row[5]),
    })
changelog.reverse()   # neueste zuoberst

kt_ws = wb["03_Kontakte"]
kontakte_total, kontakte_offen = 0, 0
planer_firmen = []
for row in kt_ws.iter_rows(min_row=5, max_col=13, values_only=True):
    if not row[0]:
        continue
    kontakte_total += 1
    if txt(row[2]) in ("", "FEHLT"):
        kontakte_offen += 1
    if txt(row[3]) == "Fachplaner" and txt(row[0]) not in ("", "FEHLT"):
        eintrag = {"firma": txt(row[0]), "ref": txt(row[4]), "notiz": txt(row[12])}
        if eintrag["firma"] not in [p["firma"] for p in planer_firmen]:
            planer_firmen.append(eintrag)
wb.close()

# Kennzahlen
mw_belegt = sum(p["mw"] for p in projekte if p["mw"])
prio_a = sum(1 for p in projekte if p["prio"] == "A")
phase_offen = sum(1 for p in projekte if p["phase"] == "offen")
planer_fehlt = sum(1 for p in projekte if p["planer"] in ("", "pruefen", "prüfen", "FEHLT"))
ueberfaellig = [p for p in projekte if p["ampel"] == "UEBERFAELLIG"]
diese_woche = [p for p in projekte if p["ampel"] == "DIESE WOCHE"]

BAU = ("Baustart", "Rohbau")
CX = ("Fit-out", "Commissioning")
phasen_reihenfolge = ["Planung", "Bewilligung", "Baustart", "Rohbau", "Fit-out",
                      "Commissioning", "Betrieb", "Ausbau", "Verzoegert", "Gestoppt", "offen"]
phasen_count = {ph: sum(1 for p in projekte if p["phase"] == ph) for ph in phasen_reihenfolge}
phasen_count = {k: v for k, v in phasen_count.items() if v}

kantone = {}
for p in projekte:
    k = p["kt"] or "?"
    kantone.setdefault(k, {"n": 0, "mw": 0.0})
    kantone[k]["n"] += 1
    if p["mw"]:
        kantone[k]["mw"] += p["mw"]
kantone = dict(sorted(kantone.items(), key=lambda kv: -kv[1]["mw"]))

# Fenster offen: dieselbe Logik wie der Bericht, maximal drei.
# Prio A zuerst, dann Bauphase vor allem anderen, dann Cx.
def fenster_score(p):
    s = 0
    if p["prio"] == "A":
        s += 100
    if p["phase"] in CX:
        s += 50
    if p["phase"] in BAU:
        s += 40
    if p["phase"] in ("Planung", "Bewilligung"):
        s += 10
    return -s

fenster_offen = sorted([p for p in projekte if p["prio"] == "A"], key=fenster_score)[:3]

DATA = {
    "stand": HEUTE.strftime("%d.%m.%Y"), "kw": KW,
    "projekte": projekte, "changelog": changelog[:14],
    "planer_firmen": planer_firmen,
}

kpis = [
    ("Projekte im Radar", str(len(projekte)), ""),
    ("Belegte Kapazitaet", f"{mw_belegt:.0f}", "MW"),
    ("Prio A", str(prio_a), f"von {len(projekte)}"),
    ("Bau laeuft", str(sum(1 for p in projekte if p["phase"] in BAU)), "Baustart + Rohbau"),
    ("Fachplaner offen", str(planer_fehlt), "grösste Lücke"),
    ("Ohne Wiedervorlage", str(sum(1 for p in projekte if not p["wv"])), "Spalte Q leer"),
]
kpi_html = "\n".join(
    f'<div class="kpi"><span class="kpi-label">{html.escape(l)}</span>'
    f'<span class="kpi-wert">{html.escape(w)}</span>'
    f'<span class="kpi-sub">{html.escape(s)}</span></div>'
    for l, w, s in kpis)

fenster_html = ""
for i, p in enumerate(fenster_offen, 1):
    fenster_html += f'''
    <article class="fenster-karte">
      <div class="fenster-nr">{i}</div>
      <h3>{html.escape(p["projekt"])}</h3>
      <p class="fenster-meta">{html.escape(p["betreiber"])} · {html.escape(p["standort"])} {html.escape(p["kt"])}
        · {html.escape((p["mw_txt"] + " MW") if p["mw"] is not None else "MW pruefen")} · <span class="chip chip-phase">{html.escape(p["phase"])}</span>
        · Kanal {html.escape(p["kanal"] or "offen")}</p>
      <p class="fenster-schritt">{html.escape(p["schritt"] or p["fenster"])}</p>
    </article>'''

max_ph = max(phasen_count.values())
phasen_html = "\n".join(
    f'<div class="balken-zeile"><span class="balken-label">{html.escape(ph)}</span>'
    f'<span class="balken-spur"><span class="balken" style="width:{n / max_ph * 100:.0f}%"></span></span>'
    f'<span class="balken-wert">{n}</span></div>'
    for ph, n in phasen_count.items())

max_mw = max((v["mw"] for v in kantone.values()), default=1) or 1
kanton_html = "\n".join(
    f'<div class="balken-zeile"><span class="balken-label">{html.escape(k)}</span>'
    f'<span class="balken-spur"><span class="balken" style="width:{max(v["mw"] / max_mw * 100, 2):.0f}%"></span></span>'
    f'<span class="balken-wert">{v["mw"]:.0f} MW · {v["n"]} Proj.</span></div>'
    for k, v in kantone.items())

planer_html = "\n".join(
    f'<li><strong>{html.escape(p["firma"])}</strong>: {html.escape(p["ref"] if p["ref"] != "FEHLT" else "noch keinem Projekt zugeordnet")}</li>'
    for p in planer_firmen) or "<li>Noch keine Planerfirma belegt.</li>"

seite = """<title>MiT Datacenter-Radar</title>
<meta name="color-scheme" content="light dark">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --navy:#1F3A5F; --orange:#E8740C;
  --ground:#F4F5F7; --surface:#FFFFFF; --surface2:#EDEFF3;
  --ink:#1D2734; --ink2:#4C5866; --ink3:#7C8794;
  --linie:#D9DDE3; --bar:#1F3A5F;
  --pruefen-bg:#FFF2CC; --pruefen-ink:#6B5A16;
  --rot:#B3372B; --gruen:#2E6E4E;
  --chip-bau:#DEE7F2; --chip-bau-ink:#274B75;
  --chip-cx:#F8E3CC; --chip-cx-ink:#8A4A0C;
  --chip-betrieb:#E4E7EB; --chip-betrieb-ink:#4C5866;
  --chip-frueh:#E3EDE7; --chip-frueh-ink:#2E6E4E;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --navy:#8FB0D9; --orange:#F0954A;
    --ground:#12161D; --surface:#1A2029; --surface2:#222935;
    --ink:#E7EBF1; --ink2:#AEB8C4; --ink3:#79838F;
    --linie:#303945; --bar:#6E93C4;
    --pruefen-bg:#3B3418; --pruefen-ink:#E4CF7B;
    --rot:#E2725F; --gruen:#6FBF97;
    --chip-bau:#243A50; --chip-bau-ink:#B9CFEA;
    --chip-cx:#453020; --chip-cx-ink:#F2C089;
    --chip-betrieb:#2A323D; --chip-betrieb-ink:#AEB8C4;
    --chip-frueh:#22382E; --chip-frueh-ink:#8FD1AF;
  }
}
:root[data-theme="dark"]{
  --navy:#8FB0D9; --orange:#F0954A;
  --ground:#12161D; --surface:#1A2029; --surface2:#222935;
  --ink:#E7EBF1; --ink2:#AEB8C4; --ink3:#79838F;
  --linie:#303945; --bar:#6E93C4;
  --pruefen-bg:#3B3418; --pruefen-ink:#E4CF7B;
  --rot:#E2725F; --gruen:#6FBF97;
  --chip-bau:#243A50; --chip-bau-ink:#B9CFEA;
  --chip-cx:#453020; --chip-cx-ink:#F2C089;
  --chip-betrieb:#2A323D; --chip-betrieb-ink:#AEB8C4;
  --chip-frueh:#22382E; --chip-frueh-ink:#8FD1AF;
}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);margin:0;
  font-family:"Source Sans 3","Helvetica Neue",Arial,sans-serif;font-size:15px;line-height:1.5}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 60px}
header.top{border-bottom:3px solid var(--orange);background:var(--surface);
  position:sticky;top:0;z-index:5;box-shadow:0 1px 0 var(--linie)}
.top-inner{max-width:1180px;margin:0 auto;padding:14px 20px;display:flex;
  align-items:baseline;gap:14px;flex-wrap:wrap}
h1{font-family:Archivo,"Arial Narrow",Arial,sans-serif;font-weight:700;
  font-size:1.35rem;margin:0;letter-spacing:.01em}
h1 small{color:var(--ink3);font-weight:500}
.stand{font-family:"IBM Plex Mono",monospace;font-size:.8rem;color:var(--ink2)}
.intern{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:.7rem;
  letter-spacing:.12em;color:var(--rot);border:1px solid currentColor;
  padding:2px 8px;border-radius:3px}
h2{font-family:Archivo,Arial,sans-serif;font-weight:600;font-size:1.02rem;
  letter-spacing:.05em;text-transform:uppercase;color:var(--ink2);
  margin:38px 0 14px;text-wrap:balance}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-top:26px}
.kpi{background:var(--surface);border:1px solid var(--linie);border-radius:6px;
  padding:12px 14px;display:flex;flex-direction:column;gap:2px}
.kpi-label{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink3)}
.kpi-wert{font-family:"IBM Plex Mono",monospace;font-size:1.7rem;font-weight:500;
  font-variant-numeric:tabular-nums;color:var(--navy)}
.kpi-sub{font-size:.75rem;color:var(--ink3)}
.fenster{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px}
.fenster-karte{background:var(--surface);border:1px solid var(--linie);
  border-left:4px solid var(--orange);border-radius:6px;padding:16px 18px;position:relative}
.fenster-nr{position:absolute;top:12px;right:14px;font-family:"IBM Plex Mono",monospace;
  color:var(--orange);font-size:1rem}
.fenster-karte h3{font-family:Archivo,Arial,sans-serif;font-size:1.05rem;margin:0 0 6px;padding-right:26px}
.fenster-meta{font-size:.82rem;color:var(--ink2);margin:0 0 10px}
.fenster-schritt{margin:0;font-size:.92rem}
.chip{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:.7rem;
  padding:1px 7px;border-radius:9px;white-space:nowrap}
.chip-bau{background:var(--chip-bau);color:var(--chip-bau-ink)}
.chip-cx{background:var(--chip-cx);color:var(--chip-cx-ink)}
.chip-betrieb{background:var(--chip-betrieb);color:var(--chip-betrieb-ink)}
.chip-frueh{background:var(--chip-frueh);color:var(--chip-frueh-ink)}
.chip-pruefen{background:var(--pruefen-bg);color:var(--pruefen-ink)}
.chip-prio-A{background:var(--orange);color:#fff}
:root[data-theme="dark"] .chip-prio-A{color:#1A1208}
.filterzeile{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center}
.filterzeile input[type=search]{background:var(--surface);border:1px solid var(--linie);
  color:var(--ink);border-radius:5px;padding:6px 10px;font:inherit;font-size:.88rem;min-width:200px}
.fbtn{background:var(--surface);border:1px solid var(--linie);color:var(--ink2);
  border-radius:14px;padding:4px 12px;font:inherit;font-size:.8rem;cursor:pointer}
.fbtn[aria-pressed=true]{background:var(--navy);border-color:var(--navy);color:var(--ground)}
.fbtn:focus-visible,.zeile:focus-visible{outline:2px solid var(--orange);outline-offset:2px}
.tabelle-huelle{overflow-x:auto;background:var(--surface);border:1px solid var(--linie);border-radius:6px}
table{border-collapse:collapse;width:100%;min-width:900px;font-size:.86rem}
th{font-family:Archivo,Arial,sans-serif;font-size:.7rem;text-transform:uppercase;
  letter-spacing:.07em;color:var(--ink3);text-align:left;padding:10px 12px;
  border-bottom:2px solid var(--linie);white-space:nowrap}
td{padding:9px 12px;border-bottom:1px solid var(--linie);vertical-align:top}
tr.zeile{cursor:pointer}
tr.zeile:hover td{background:var(--surface2)}
tr.detail td{background:var(--surface2);font-size:.85rem;padding:14px 16px 16px}
tr.detail p{margin:.25em 0}
tr.detail a{color:var(--navy);word-break:break-all}
td.num{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums;white-space:nowrap}
.pruefen{background:var(--pruefen-bg);color:var(--pruefen-ink);
  font-family:"IBM Plex Mono",monospace;font-size:.72rem;padding:1px 6px;border-radius:3px}
.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.panel{background:var(--surface);border:1px solid var(--linie);border-radius:6px;padding:16px 18px}
.panel h2{margin-top:0}
.balken-zeile{display:grid;grid-template-columns:110px 1fr auto;gap:10px;
  align-items:center;padding:3px 0}
.balken-label{font-size:.82rem;color:var(--ink2)}
.balken-spur{height:14px;background:var(--surface2);border-radius:4px;overflow:hidden}
.balken{display:block;height:100%;background:var(--bar);border-radius:0 4px 4px 0;min-width:2px}
.balken-wert{font-family:"IBM Plex Mono",monospace;font-size:.76rem;
  color:var(--ink2);font-variant-numeric:tabular-nums;white-space:nowrap}
.panel ul{margin:0;padding-left:18px}
.panel li{margin:.35em 0;font-size:.88rem}
.log{border-left:2px solid var(--linie);padding-left:18px;display:flex;flex-direction:column;gap:14px}
.log-eintrag{position:relative}
.log-eintrag::before{content:"";position:absolute;left:-23px;top:6px;width:8px;height:8px;
  border-radius:50%;background:var(--navy)}
.log-datum{font-family:"IBM Plex Mono",monospace;font-size:.72rem;color:var(--ink3)}
.log-eintrag h3{font-size:.92rem;margin:2px 0 4px;font-family:Archivo,Arial,sans-serif}
.log-eintrag p{margin:0;font-size:.86rem;color:var(--ink2)}
.log-eintrag .kons{color:var(--ink);margin-top:3px}
.log-eintrag .kons::before{content:"Konsequenz: ";font-weight:600;color:var(--orange)}
footer{margin-top:50px;padding-top:16px;border-top:1px solid var(--linie);
  font-size:.75rem;color:var(--ink3);display:flex;gap:16px;flex-wrap:wrap}
@media (prefers-reduced-motion: no-preference){
  .balken{transition:width .5s ease}
}
</style>

<header class="top"><div class="top-inner">
  <h1>MiT Datacenter-Radar <small>Schweiz</small></h1>
  <span class="stand">KW __KW__ · Stand __STAND__</span>
  <span class="intern">INTERN VERTRAULICH</span>
</div></header>

<div class="wrap">
  <section class="kpis" aria-label="Kennzahlen">__KPIS__</section>

  <h2>Fenster offen, diese Woche handeln</h2>
  <section class="fenster">__FENSTER__</section>

  <h2>Projekt-Radar</h2>
  <div class="filterzeile" role="group" aria-label="Filter">
    <input type="search" id="suche" placeholder="Suche Projekt, Betreiber, Ort" aria-label="Suche">
    <button class="fbtn" data-f="alle" aria-pressed="true">Alle</button>
    <button class="fbtn" data-f="bau" aria-pressed="false">Bau laeuft</button>
    <button class="fbtn" data-f="cx" aria-pressed="false">Cx-Fenster</button>
    <button class="fbtn" data-f="frueh" aria-pressed="false">Frueh</button>
    <button class="fbtn" data-f="betrieb" aria-pressed="false">Betrieb</button>
    <button class="fbtn" data-f="prioA" aria-pressed="false">Nur Prio A</button>
    <button class="fbtn" data-f="luecken" aria-pressed="false">Mit Luecken</button>
  </div>
  <div class="tabelle-huelle">
    <table id="radar">
      <thead><tr>
        <th>Projekt</th><th>Betreiber</th><th>Ort</th><th>Kt.</th><th>MW</th>
        <th>Phase</th><th>IBN</th><th>GU/TU</th><th>Fachplaner</th><th>Kanal</th><th>Prio</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <p style="font-size:.78rem;color:var(--ink3)">Zeile anklicken fuer Chance, naechsten Schritt, Bemerkung und Quellen.
  Gelb markierte Werte sind nicht belegt und beim naechsten Lauf zu klaeren.</p>

  <div class="panels">
    <div class="panel"><h2>Projekte nach Phase</h2>__PHASEN__</div>
    <div class="panel"><h2>Belegte Kapazitaet nach Kanton</h2>__KANTONE__
      <p style="font-size:.75rem;color:var(--ink3);margin-bottom:0">Nur belegte MW-Werte. Projekte mit Kapazitaet "pruefen" zaehlen hier nicht mit.</p></div>
    <div class="panel"><h2>Fachplaner-Kanal</h2>
      <ul>__PLANER__</ul>
      <p style="font-size:.8rem;color:var(--ink2)">Ein Planer ist zehn Projekte, ein Betreiber ist eines.
      Naechster Schritt je Firma: DC-Verantwortlichen ueber die Firmenwebsite identifizieren.</p></div>
  </div>

  <h2>Changelog</h2>
  <div class="log" id="log"></div>

  <footer>
    <span>INTERN VERTRAULICH. Keine Preise, keine Fleetzusagen. Owen-Gate und CHF-Sperre gelten.</span>
    <span>Quelle: MiT_Datacenter_Radar_CH_V1.0.xlsx, Blatt 02, 03, 06.</span>
  </footer>
</div>

<script>
const DATA = __DATA__;
const BAU = ["Baustart","Rohbau"], CX = ["Fit-out","Commissioning"],
      FRUEH = ["Planung","Bewilligung"], BETRIEB = ["Betrieb","Ausbau"];
const tb = document.querySelector("#radar tbody");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function phaseChip(ph){
  let k = "chip-betrieb";
  if (BAU.includes(ph)) k = "chip-bau";
  else if (CX.includes(ph)) k = "chip-cx";
  else if (FRUEH.includes(ph)) k = "chip-frueh";
  else if (ph === "offen" || ph === "Verzoegert" || ph === "Gestoppt") k = "chip-pruefen";
  return `<span class="chip ${k}">${esc(ph)}</span>`;
}
const zelle = v => (v === "" || v === "pruefen" || v === "prüfen" || v === "FEHLT")
  ? `<span class="pruefen">${v === "" ? "offen" : "pruefen"}</span>` : esc(v);

function hatLuecke(p){
  return [p.mw_txt, p.phase === "offen" ? "" : "x", p.ibn, p.gu, p.planer]
    .some(v => v === "" || v === "pruefen" || v === "prüfen") ;
}

function render(filter, suchtext){
  tb.innerHTML = "";
  DATA.projekte.forEach((p, i) => {
    if (filter === "bau" && !BAU.includes(p.phase)) return;
    if (filter === "cx" && !CX.includes(p.phase)) return;
    if (filter === "frueh" && !FRUEH.includes(p.phase)) return;
    if (filter === "betrieb" && !BETRIEB.includes(p.phase)) return;
    if (filter === "prioA" && p.prio !== "A") return;
    if (filter === "luecken" && !hatLuecke(p)) return;
    if (suchtext){
      const heu = (p.projekt + " " + p.betreiber + " " + p.standort + " " + p.gu + " " + p.planer).toLowerCase();
      if (!heu.includes(suchtext)) return;
    }
    const tr = document.createElement("tr");
    tr.className = "zeile"; tr.tabIndex = 0;
    tr.setAttribute("aria-expanded", "false");
    tr.innerHTML = `<td><strong>${esc(p.projekt)}</strong></td><td>${esc(p.betreiber)}</td>
      <td>${zelle(p.standort)}</td><td>${zelle(p.kt)}</td>
      <td class="num">${p.mw !== null ? p.mw : `<span class="pruefen">pruefen</span>`}</td>
      <td>${phaseChip(p.phase)}</td><td>${zelle(p.ibn)}</td>
      <td>${zelle(p.gu)}</td><td>${zelle(p.planer)}</td><td>${zelle(p.kanal)}</td>
      <td>${p.prio === "A" ? `<span class="chip chip-prio-A">A</span>` : esc(p.prio)}</td>`;
    const det = document.createElement("tr");
    det.className = "detail"; det.hidden = true;
    det.innerHTML = `<td colspan="11">
      <p><strong>MiT-Chance:</strong> ${esc(p.chance)}</p>
      <p><strong>Fenster:</strong> ${esc(p.fenster)}</p>
      ${p.schritt ? `<p><strong>Naechster Schritt:</strong> ${esc(p.schritt)}</p>` : ""}
      <p><strong>Bemerkung:</strong> ${esc(p.bemerkung)}</p>
      <p><strong>Quellen (Stand ${esc(p.stand)}):</strong> ${
        p.quellen.map(u => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u)}</a>`).join("<br>")}</p>
    </td>`;
    const toggle = () => { det.hidden = !det.hidden; tr.setAttribute("aria-expanded", String(!det.hidden)); };
    tr.addEventListener("click", toggle);
    tr.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }});
    tb.append(tr, det);
  });
}

let aktFilter = "alle";
document.querySelectorAll(".fbtn").forEach(b => b.addEventListener("click", () => {
  aktFilter = b.dataset.f;
  document.querySelectorAll(".fbtn").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
  render(aktFilter, document.getElementById("suche").value.trim().toLowerCase());
}));
document.getElementById("suche").addEventListener("input", e =>
  render(aktFilter, e.target.value.trim().toLowerCase()));

document.getElementById("log").innerHTML = DATA.changelog.map(c => `
  <div class="log-eintrag">
    <span class="log-datum">${esc(c.datum)}</span>
    <h3>${esc(c.projekt)}</h3>
    <p>${esc(c.was)}</p>
    <p class="kons">${esc(c.konsequenz)}</p>
  </div>`).join("");

render("alle", "");
</script>
"""

seite = (seite
         .replace("__KW__", str(KW))
         .replace("__STAND__", HEUTE.strftime("%d.%m.%Y"))
         .replace("__KPIS__", kpi_html)
         .replace("__FENSTER__", fenster_html)
         .replace("__PHASEN__", phasen_html)
         .replace("__KANTONE__", kanton_html)
         .replace("__PLANER__", planer_html)
         .replace("__DATA__", json.dumps(DATA, ensure_ascii=False)))

with open(ZIEL, "w", encoding="utf-8") as f:
    f.write(seite)
print(f"geschrieben: {ZIEL}")
print(f"{len(projekte)} Projekte, {len(DATA['changelog'])} Changelog-Eintraege, "
      f"{len(planer_firmen)} Planerfirmen, Fenster offen: {len(fenster_offen)}")
