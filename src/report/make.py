#!/usr/bin/env python3
"""Baut beide Fassungen des Berichts, die Wordvorlage und die PDFs.

    python3 src/report/make.py              # beide Fassungen
    python3 src/report/make.py --variante kunde   # nur die Fassung zur Weitergabe

Je Fassung wiederholt der Lauf Bau und PDF-Export, bis die Seitenzahlen im
Inhaltsverzeichnis stabil sind. Nötig ist das, weil das Verzeichnis selbst
seine Länge ändern kann, sobald die Zahlen darin stehen. Zum Schluss laufen
Inhalts- und Satzprüfung über jede Fassung.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import variants

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MAX_PASSES = 5


def step(*args: str) -> None:
    print(f"\n$ {' '.join(Path(a).name if a.endswith('.py') else a for a in args)}")
    subprocess.run(
        [sys.executable, *args], check=True, cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(HERE)},
    )


def build_variant(name: str, with_template: bool) -> None:
    spec = variants.VARIANTS[name]
    print(f"\n{'=' * 72}\n{name}: {spec['label']}\n{'=' * 72}")
    extra = ["--template"] if with_template else []

    previous = None
    for attempt in range(1, MAX_PASSES + 1):
        step(str(HERE / "build_report.py"), "--variante", name, *extra)
        step(str(HERE / "make_pdf.py"), "--variante", name, "--no-preview")
        current = spec["toc"].read_text(encoding="utf-8")
        if current == previous:
            print(f"\nSeitenzahlen stabil nach {attempt} Durchgängen.")
            break
        previous = current
    else:
        print("\nSeitenzahlen nach dem letzten Durchgang übernommen.")

    # Letzter Bau, damit die stabilen Zahlen auch in der Datei stehen.
    step(str(HERE / "build_report.py"), "--variante", name, *extra)
    step(str(HERE / "make_pdf.py"), "--variante", name, "--no-preview")
    step(str(HERE / "lint.py"), "--variante", name)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--variante", choices=sorted(variants.VARIANTS),
        help="nur diese Fassung bauen; ohne Angabe werden beide gebaut",
    )
    args = ap.parse_args()

    step(str(HERE / "extract.py"))
    step(str(HERE / "make_logo.py"))

    # Die Wordvorlage hängt nicht an der Fassung und wird einmal geschrieben.
    names = [args.variante] if args.variante else ["voll", "kunde"]
    for i, name in enumerate(names):
        build_variant(name, with_template=(i == 0))

    # Der Inhaltsvergleich gegen das Original gilt der vollständigen Fassung;
    # der Kundenfassung fehlt Anhang C ja absichtlich.
    if "voll" in names:
        step(str(HERE / "check.py"))

    print(f"\n{'=' * 72}\nFertig.")
    for name in names:
        spec = variants.VARIANTS[name]
        print(f"  {spec['docx'].name}")
        print(f"  {spec['pdf'].name}")


if __name__ == "__main__":
    main()
