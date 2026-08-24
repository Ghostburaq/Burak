#!/usr/bin/env python3
"""Prüft den neu gesetzten Bericht gegen das Original.

    python3 src/report/check.py

Verglichen wird der sichtbare Text. Erlaubt sind ausschliesslich die bewusst
gesetzten typografischen Änderungen — geschützte Leerzeichen, Hochkomma als
Tausendertrennung, geschützter Bindestrich. Alles andere gilt als
Inhaltsverlust und lässt die Prüfung fehlschlagen.
"""

from __future__ import annotations

import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import corrections
import variants

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "assets" / "report" / "Schlussbericht_Kreuz_Zuzwil_original.docx"
REBUILT = variants.VARIANTS[variants.DEFAULT]["docx"]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Texte, die es im Original nicht gab: Verzeichnis, Kopf-/Fusszeile, Kicker.
ADDED = [
    "Verzeichnis der Kapitel und Abschnitte. In Word mit F9 aktualisierbar.",
    "Nach dem Öffnen in Word mit F9 aktualisieren.",
    "Schlussbericht",
]


def visible_text(path: Path) -> str:
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    return "".join(t.text or "" for t in root.iter(W + "t"))


def canonical(text: str) -> str:
    """Vergleichsform: typografische Feinheiten auf die Ausgangsform zurück."""
    # NFKC bildet den geschützten Bindestrich U+2011 auf U+2010 ab, nicht auf
    # den gewöhnlichen — beide Formen müssen zurückgeführt werden.
    text = unicodedata.normalize("NFKC", text)
    for special, plain in (
        ("\u2011", "-"), ("\u2010", "-"), ("\u2019", "'"),
        ("\u00a0", " "), ("\u202f", " "),
    ):
        text = text.replace(special, plain)
    # Die Abbildungen stehen im Ausgangsbericht als 1, 4, 5, 2, 3 im Text und
    # werden beim Satz in Lesereihenfolge durchgezählt. Für den Vergleich
    # zählt die Legende, nicht ihre Nummer.
    text = re.sub(r"Abbildung[\s\u00a0]+\d+", "Abbildung#", text)
    # Die drei berichtigten Querverweise stehen in corrections.py; das
    # Original wird für den Vergleich auf dieselbe Form gebracht.
    text = corrections.normalize(text)
    # Grossschreibung ist im neuen Bericht eine Auszeichnung (w:caps), keine
    # Texteigenschaft — für den Inhaltsvergleich also ohne Belang.
    text = re.sub(r"\s+", "", text).casefold()
    for phrase in ADDED:
        text = text.replace(re.sub(r"\s+", "", phrase).casefold(), "")
    return text


def _missing(before: str, after: str, chunk: int = 4000) -> list[str]:
    """Stellen des Originals, die im neuen Dokument fehlen.

    Der Vergleich läuft abschnittsweise: ein Zeichenvergleich über 80'000
    Zeichen am Stück dauert Minuten, in Blöcken von wenigen tausend Zeichen
    Sekunden — bei gleichem Ergebnis, weil der Text in derselben Reihenfolge
    steht und die Blockgrenze nach jedem Abschnitt neu ausgerichtet wird.
    """
    import difflib

    gaps: list[str] = []
    pos = 0
    while pos < len(before):
        window = before[pos:pos + chunk]
        start = after.find(window[:60])
        segment = after[start:start + chunk * 2] if start >= 0 else after
        matcher = difflib.SequenceMatcher(None, window, segment, autojunk=False)
        blocks = matcher.get_matching_blocks()
        covered = 0
        for block in blocks:
            if block.a > covered:
                gaps.append(window[covered:block.a])
            covered = max(covered, block.a + block.size)
        pos += covered or chunk
    return [g for g in gaps if g]


def main() -> int:
    if not REBUILT.exists():
        print("Der gesetzte Bericht fehlt. Zuerst src/report/make.py laufen lassen.")
        return 2

    before = canonical(visible_text(ORIGINAL))
    after = canonical(visible_text(REBUILT))

    # Die Kapitelzeilen ("Kapitel 6") und das Verzeichnis stehen zusätzlich im
    # neuen Dokument. Geprüft wird deshalb, dass nichts aus dem Original fehlt.
    missing = _missing(before, after)

    print(f"Original {len(before)} Zeichen · gesetzt {len(after)} Zeichen")
    if missing:
        print(f"FEHLT ({sum(len(m) for m in missing)} Zeichen):")
        for chunk in missing[:20]:
            print(f"  {chunk[:160]!r}")
        return 1
    print("Vollständig: kein Zeichen des Originals ist verloren gegangen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
