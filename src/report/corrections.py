#!/usr/bin/env python3
"""Sachliche Korrekturen am Text des Ausgangsberichts.

Hier steht jede Stelle, an der der gesetzte Bericht inhaltlich vom Original
abweicht — vollständig und mit Begründung. Alles andere wird zeichengenau
übernommen; ``check.py`` erzwingt das.

Aufgenommen wird nur, was nachweislich falsch ist und wo die richtige Angabe
aus dem Bericht selbst hervorgeht. Alles, was eine fachliche Entscheidung
verlangt, gehört nicht hierher, sondern in eine Rückfrage an den Verfasser.

Gefunden wurden die Verweise, indem jeder ``Kapitel N``-Verweis gegen die
Überschrift seines Ziels gehalten wurde: die drei zeigen auf Kapitel, die
etwas anderes behandeln. Sie stammen erkennbar aus einer früheren Gliederung.
"""

from __future__ import annotations

# (falsch, richtig, Begründung)
CROSS_REFERENCES = [
    (
        "Die Aufnahmen sind in Kapitel 13 enthalten.",
        "Die Aufnahmen sind in Kapitel 15 enthalten.",
        "Kapitel 13 ist «Weiteres Vorgehen». Die Bilddokumentation ist "
        "Kapitel 15.",
    ),
    (
        "Der dafür nötige Schritt ist in Kapitel 12 beschrieben",
        "Der dafür nötige Schritt ist in Kapitel 13.1 beschrieben",
        "Kapitel 12 ist «Annahmen, Unsicherheiten und Belastbarkeit». Der "
        "Schritt steht in 13.1 — so verweist auch der gleichlautende Satz im "
        "Massnahmenkatalog.",
    ),
    (
        "Nicht ausgewertet. Siehe Kapitel 12.2.",
        "Nicht ausgewertet. Siehe Kapitel 12.3.",
        "Kapitel 12.2 behandelt die Messunsicherheit der Geräte. Die "
        "Supraharmonischen stehen in 12.3, «Was diese Messung nicht "
        "beantworten kann».",
    ),
]


def apply(text: str) -> str:
    for wrong, right, _ in CROSS_REFERENCES:
        text = text.replace(wrong, right)
    return text


def normalize(text: str) -> str:
    """Beide Fassungen auf die korrigierte Form bringen — für den Vergleich."""
    return apply(text)


def report() -> str:
    lines = ["Korrigierte Stellen gegenüber dem Ausgangsbericht:"]
    for wrong, right, why in CROSS_REFERENCES:
        lines.append(f"  «{wrong}»")
        lines.append(f"  → «{right}»")
        lines.append(f"    {why}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
