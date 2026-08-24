#!/usr/bin/env python3
"""Die zwei Fassungen des Berichts und was sie unterscheidet.

Der Bericht erscheint in zwei Fassungen aus derselben Quelle:

``voll``
    Die Arbeitsfassung mit Anhang C, den internen Hinweisen. Sie bleibt im
    eigenen Ablage- und Arbeitsbestand.

``kunde``
    Die Fassung zur Weitergabe. Anhang C fällt weg, ebenso der Satz auf dem
    Deckblatt, der ihn ankündigt — er ginge sonst ins Leere.

Beide Fassungen entstehen im selben Lauf und mit denselben Prüfungen. Der
Unterschied steht ausschliesslich hier, damit er sich an einer Stelle
nachlesen und ändern lässt.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Überschrift des Anhangs, der nur intern ist, und das Stichwort, mit dem der
# Deckblatt-Hinweis auf ihn verweist.
INTERNAL_APPENDIX = "Anhang C"
COVER_NOTE_TITLE = "Hinweis zur Verwendung dieses Berichts"

VARIANTS = {
    "voll": {
        "label": "Arbeitsfassung mit Anhang C",
        "docx": ROOT / "Schlussbericht_Kreuz_Zuzwil.docx",
        "pdf": ROOT / "Schlussbericht_Kreuz_Zuzwil.pdf",
        "toc": ROOT / "build" / "toc_pages.json",
    },
    "kunde": {
        "label": "Fassung zur Weitergabe, ohne Anhang C",
        "docx": ROOT / "Schlussbericht_Kreuz_Zuzwil_Kundenversion.docx",
        "pdf": ROOT / "Schlussbericht_Kreuz_Zuzwil_Kundenversion.pdf",
        "toc": ROOT / "build" / "toc_pages_kunde.json",
    },
}
DEFAULT = "voll"


def add_argument(parser) -> None:
    parser.add_argument(
        "--variante", choices=sorted(VARIANTS), default=DEFAULT,
        help="voll: mit Anhang C · kunde: ohne Anhang C",
    )


def select(blocks: list[dict], variant: str) -> list[dict]:
    """Die Blöcke, die in dieser Fassung gesetzt werden."""
    if variant != "kunde":
        return blocks

    closing = blocks[-4:]  # Schlussseite, sie bleibt in beiden Fassungen
    head = blocks[:-4]

    cut = next(
        (
            i
            for i, b in enumerate(head)
            if b["type"] == "heading"
            and b["level"] == 1
            and b["text"].startswith(INTERNAL_APPENDIX)
        ),
        None,
    )
    if cut is None:
        raise SystemExit(
            f"«{INTERNAL_APPENDIX}» nicht gefunden — die Kundenfassung liesse "
            "sich nicht sicher abgrenzen."
        )
    head = head[:cut]

    # Der Deckblatt-Hinweis kündigt Anhang C an. Ohne den Anhang muss auch
    # dieser Satz weg, sonst verweist der Bericht auf etwas, das fehlt.
    trimmed = []
    for block in head:
        if block["type"] == "callout" and block["title"] == COVER_NOTE_TITLE:
            block = dict(block)
            block["body"] = [s for s in block["body"] if INTERNAL_APPENDIX not in s]
        trimmed.append(block)
    return trimmed + closing
