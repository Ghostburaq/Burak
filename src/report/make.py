#!/usr/bin/env python3
"""Baut den gesamten Bericht: Inhalt, Logo, DOCX, Seitenzahlen, PDF, Vorlage.

    python3 src/report/make.py

Der Lauf wiederholt Bau und PDF-Export, bis die Seitenzahlen im
Inhaltsverzeichnis stabil sind. Nötig ist das, weil das Verzeichnis selbst
seine Länge ändern kann, sobald die Zahlen darin stehen.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TOC_PAGES = ROOT / "build" / "toc_pages.json"
MAX_PASSES = 5


def step(*args: str) -> None:
    print(f"\n$ {' '.join(args)}")
    env = {"PYTHONPATH": str(HERE)}
    subprocess.run([sys.executable, *args], check=True, cwd=ROOT, env={**_env(), **env})


def _env() -> dict:
    import os

    return dict(os.environ)


def main() -> None:
    step(str(HERE / "extract.py"))
    step(str(HERE / "make_logo.py"))

    previous = None
    for attempt in range(1, MAX_PASSES + 1):
        step(str(HERE / "build_report.py"), "--template")
        step(str(HERE / "make_pdf.py"), "--no-preview")
        current = TOC_PAGES.read_text(encoding="utf-8")
        if current == previous:
            print(f"\nSeitenzahlen stabil nach {attempt} Durchgängen.")
            break
        previous = current
    else:
        print("\nSeitenzahlen nach dem letzten Durchgang übernommen.")

    # Letzter Bau, damit die stabilen Zahlen auch in der Datei stehen.
    step(str(HERE / "build_report.py"), "--template")
    step(str(HERE / "make_pdf.py"), "--no-preview")
    step(str(HERE / "check.py"))
    pages = json.loads(TOC_PAGES.read_text(encoding="utf-8"))
    print(f"\nFertig. {len(pages)} Verzeichniseinträge mit Seitenzahl.")


if __name__ == "__main__":
    main()
