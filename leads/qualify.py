"""Bereinigt und priorisiert die Scraper-Treffer fuer MiT Power.

Google Maps liefert keine Umsatz- oder Projektgroessen. Die Prioritaet ist
deshalb eine Einschaetzung nach Segment (typisches Auftragsvolumen), kein
Beleg fuer >= CHF 50'000. Groesse vor dem Anruf pruefen (Website, Zefix).

    python3 leads/qualify.py /tmp/gmaps-power-output/results.csv
    -> leads/power_leads_ch.csv (Semikolon, Excel-tauglich)
"""
import csv
import sys
from pathlib import Path

# Einschaetzung Auftragspotenzial MiT Power je Segment
PRIO = {
    "DC": "A", "EVU": "A", "SPITAL": "A", "PHARMA": "A",
    "BAU": "B", "INFRA": "B", "EVENT": "B",
}
ANSATZ = {
    "DC": "NEA-Test, USV-Überbrückung, Loadbank, Revisionen",
    "EVU": "Netzersatz bei Umbau/Störung, Trafo, BESS, PQ",
    "SPITAL": "NEA-Test, Überbrückung bei NEA-Revision",
    "PHARMA": "Stillstände/Revisionen, Trafo, PQ-Audit",
    "BAU": "Baustrom Grossbaustelle, Hybrid/BESS, Tunnel",
    "INFRA": "NEA-Ersatz bei Revision, Trafo",
    "EVENT": "Event-Strom, redundante Versorgung",
}
# Kategorien, die auf Kleinbetriebe oder falsche Treffer hindeuten
AUSSCHLUSS = [
    "elektriker", "elektroinstallat", "sanitär", "maler", "gipser", "garten",
    "reinigung", "umzug", "schreiner", "dachdecker", "plattenleger",
    "architekt", "immobilien", "computer", "it-dienst", "handyshop",
    "tankstelle", "restaurant", "hotel", "fitness", "apotheke", "arzt",
    "zahnarzt", "physiotherap", "tierarzt", "baumarkt", "baustoffhandel",
]

FELDER = ["prio", "segment", "firma", "kategorie", "ort_suche", "adresse",
          "telefon", "website", "bewertungen", "maps_link", "ansatz_mit"]


def main(pfad: str) -> None:
    treffer, gesehen, raus = [], set(), 0
    with open(pfad, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            key = r.get("place_id") or r.get("cid") or (r["title"], r["address"])
            if key in gesehen:
                continue
            gesehen.add(key)
            seg, _, ort = (r.get("input_id") or "").partition("|")
            kat = (r.get("category") or "").lower()
            if seg not in PRIO or any(a in kat for a in AUSSCHLUSS) \
                    or "closed" in (r.get("status") or "").lower():
                raus += 1
                continue
            treffer.append({
                "prio": PRIO[seg], "segment": seg, "firma": r["title"],
                "kategorie": r.get("category", ""), "ort_suche": ort,
                "adresse": r.get("complete_address") or r.get("address", ""),
                "telefon": r.get("phone", ""), "website": r.get("website", ""),
                "bewertungen": r.get("review_count", ""),
                "maps_link": r.get("link", ""), "ansatz_mit": ANSATZ[seg],
            })

    treffer.sort(key=lambda t: (t["prio"], t["segment"], t["ort_suche"], t["firma"]))
    ziel = Path(__file__).with_name("power_leads_ch.csv")
    with open(ziel, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FELDER, delimiter=";")
        w.writeheader()
        w.writerows(treffer)
    print(f"{len(treffer)} Leads, {raus} aussortiert -> {ziel}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/gmaps-power-output/results.csv")
