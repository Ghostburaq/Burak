#!/usr/bin/env python3
"""Ersetzt alle identifizierenden Angaben durch Muster- und Beispielangaben.

Der Musterbericht zeigt Aufbau, Vorgehen und Satz eines kabuu-Berichts, ohne
zu verraten, um welches Objekt es ging. Ersetzt wird deshalb alles, was Ort,
Betrieb, Personen oder beteiligte Firmen benennt. Die technische Beschreibung
bleibt: sie macht den Musterbericht erst brauchbar und gibt niemanden preis.

Nicht ersetzt werden die Angaben des Verfassers — Name, Firma, Anschrift und
Kontakt von kabuu. Der Musterbericht ist ein eigenes Dokument von kabuu und
trägt dessen Briefkopf.

    python3 src/report/anonymise.py     # Ersetzungstabelle anzeigen
"""

from __future__ import annotations

import re

# Objekt, Betreiber, Auftraggeber, Netzbetreiber, beigezogene Firmen.
# Reihenfolge spielt hier keine Rolle: ersetzt wird in einem Durchgang, und
# der längste passende Eintrag gewinnt. Genau deshalb steht «Gasthaus Kreuz»
# in der Tabelle und «Kreuz» nicht — sonst würde aus «Kreuzvergleich»
# «Musterbetriebvergleich».
REPLACEMENTS = {
    # Objekt und Betreiber
    "Gasthaus Kreuz": "Gasthaus Muster",
    "P. Züger": "M. Muster",
    "Züger": "Muster",
    "Oberdorfstrasse 16": "Musterstrasse 16",
    "Oberdorfstrasse": "Musterstrasse",
    # Auftraggeber
    "Baumann Elektrokontrollen GmbH": "Beispiel Elektrokontrollen GmbH",
    "Baumann Elektrokontrollen": "Beispiel Elektrokontrollen",
    "Hirschenstrasse 17": "Beispielstrasse 17",
    "9200 Gossau": "0000 Beispielstadt",
    # Netzbetreiber und dessen Anschrift
    "Elektrizitätswerks Zuzwil": "Elektrizitätswerks Musterhausen",
    "Elektrizitätswerk Zuzwil": "Elektrizitätswerk Musterhausen",
    "EW Zuzwil": "EW Musterhausen",
    "Hinterdorfstrasse 3": "Musterweg 3",
    # Errichter der Photovoltaikanlage
    "Elektro Jung AG": "Beispiel Elektro AG",
    # Raumbezeichnung, die den Betrieb beschreibt
    "Weinkeller": "Untergeschoss",
    # Technische Beratung des Netzbetreibers
    "IBG Engineering AG": "Beispiel Engineering AG",
    "Sandackerstrasse 24": "Beispielweg 24",
    "9245 Oberbüren": "0000 Beispieldorf",
    # Ortsangaben. Die verschriebenen Formen stammen aus Anhang C, wo gerade
    # diese Tippfehler der Geräteberichte aufgelistet sind — sie bleiben als
    # Tippfehler erhalten, nur eben am Musterort.
    "9524 Zuzwil SG": "0000 Musterhausen",
    "9524 Zuzwil": "0000 Musterhausen",
    "9542 Zuzwil": "0090 Musterhausen",
    "Zuzwill SG": "Musterhusen",
    "Zuzwill": "Musterhusen",
    "Zuzwil SG": "Musterhausen",
    "Zuzwil": "Musterhausen",
    # Regionaler Netzbetreiber, im Bericht nur als Kürzel genannt
    "SAK": "Beispielwerk AG",
}

# Ein einziger Durchgang, längster Treffer zuerst. So kann keine Ersetzung
# das Ergebnis einer anderen noch einmal treffen.
_PATTERN = re.compile(
    "|".join(re.escape(k) + r"\b" for k in sorted(REPLACEMENTS, key=len, reverse=True))
)

# Begriffe, die im Musterbericht nirgends mehr vorkommen dürfen — im Text
# wie in den Bildern. Grundlage der Prüfung in ``lint.py``.
FORBIDDEN = (
    "Kreuz,", "Züger", "Zuzwil", "Zuzwill", "Oberdorfstrasse", "9524", "9542",
    "Baumann", "Hirschenstrasse", "Gossau", "9200",
    "IBG", "Sandackerstrasse", "Oberbüren", "9245", "Hinterdorfstrasse",
    "SAK", "Elektro Jung", "47,48", "9,17", "Weinkeller",
)


def apply(text: str) -> str:
    return _PATTERN.sub(lambda m: REPLACEMENTS[m.group(0)], text)


def blocks(content: list[dict]) -> list[dict]:
    """Das Inhaltsmodell anonymisiert zurückgeben."""
    out = []
    for block in content:
        block = dict(block)
        if "text" in block:
            block["text"] = apply(block["text"])
        if block.get("type") == "callout":
            block["title"] = apply(block["title"])
            block["body"] = [apply(s) for s in block["body"]]
        if block.get("type") == "table":
            block["rows"] = [
                [{**c, "text": apply(c["text"])} for c in row] for row in block["rows"]
            ]
        out.append(block)
    return out


def residue(text: str) -> list[str]:
    """Welche verbotenen Begriffe stehen noch im Text."""
    return sorted({t for t in FORBIDDEN if t in text})


if __name__ == "__main__":
    width = max(len(k) for k in REPLACEMENTS)
    print(f"{len(REPLACEMENTS)} Ersetzungen:\n")
    for key in sorted(REPLACEMENTS, key=len, reverse=True):
        print(f"  {key:<{width}}  →  {REPLACEMENTS[key]}")
    print(f"\n{len(FORBIDDEN)} Begriffe, die danach nirgends mehr vorkommen dürfen:")
    print("  " + " · ".join(FORBIDDEN))
