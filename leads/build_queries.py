"""Erzeugt die Google-Maps-Suchliste fuer MiT Power (Deutschschweiz).

Jede Zeile bekommt eine Input-ID "SEGMENT|Ort", damit qualify.py die Treffer
spaeter dem Segment zuordnen kann (Syntax des Scrapers: "Suche #!#ID").

    python3 leads/build_queries.py            # -> leads/queries_power_ch.txt
"""
from pathlib import Path

# Segment-Kuerzel -> Suchbegriffe (Google-Maps-Kategorien, Schweizer Schreibweise)
SEGMENTE = {
    "DC":     ["Rechenzentrum"],
    "EVU":    ["Elektrizitätswerk", "Energieversorger"],
    "BAU":    ["Bauunternehmung", "Generalunternehmer", "Tiefbauunternehmung"],
    "SPITAL": ["Spital"],
    "PHARMA": ["Pharmaunternehmen", "Chemieunternehmen"],
    "INFRA":  ["Abwasserreinigungsanlage", "Kehrichtverbrennungsanlage"],
    "EVENT":  ["Messezentrum", "Stadion"],
}

# Zentren der Deutschschweiz; bei Bedarf anpassen
ORTE = [
    "Zürich", "Winterthur", "Baden", "Aarau", "Olten", "Basel", "Liestal",
    "Bern", "Thun", "Biel", "Solothurn", "Luzern", "Zug", "Schwyz",
    "St. Gallen", "Frauenfeld", "Schaffhausen", "Chur", "Wil",
]


def main() -> None:
    zeilen = [
        f"{begriff} in {ort}, Schweiz #!#{seg}|{ort}"
        for seg, begriffe in SEGMENTE.items()
        for begriff in begriffe
        for ort in ORTE
    ]
    ziel = Path(__file__).with_name("queries_power_ch.txt")
    ziel.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    print(f"{len(zeilen)} Suchen -> {ziel}")


if __name__ == "__main__":
    main()
