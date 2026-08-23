#!/usr/bin/env python3
"""Erzeugt das PDF, liest die Seitenzahlen der Überschriften und rendert Vorschauen.

    python3 src/report/make_pdf.py            # PDF + Seitenzahlen + Vorschau
    python3 src/report/make_pdf.py --pages 3 7 12   # nur diese Seiten rendern

Die gefundenen Seitenzahlen landen in ``build/toc_pages.json``. Der nächste
Aufruf von ``build_report.py`` schreibt sie als Feldergebnis in das
Inhaltsverzeichnis — so stimmen die Zahlen auch ohne Feldaktualisierung.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "Schlussbericht_Kreuz_Zuzwil.docx"
PDF = ROOT / "Schlussbericht_Kreuz_Zuzwil.pdf"
CONTENT = ROOT / "build" / "content.json"
TOC_PAGES = ROOT / "build" / "toc_pages.json"
PREVIEW = ROOT / "build" / "preview"
PROFILE = ROOT / "build" / ".soffice"


def to_pdf() -> Path:
    """LibreOffice-Export. Eigenes Benutzerprofil, damit der Lauf reproduzierbar ist."""
    out = ROOT / "build" / "pdf"
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "soffice", f"-env:UserInstallation=file://{PROFILE}",
            "--headless", "--norestore", "--convert-to", "pdf",
            "--outdir", str(out), str(DOCX),
        ],
        check=True, capture_output=True, timeout=900,
    )
    produced = out / (DOCX.stem + ".pdf")
    shutil.move(produced, PDF)
    return PDF


def _norm(text: str) -> str:
    """Vergleichsform: ohne geschützte Zeichen, ohne Mehrfachleerzeichen."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("‑", "-").replace("’", "'")
    return re.sub(r"\s+", " ", text).strip().lower()


def heading_pages(entries: list[tuple[int, str, str]]) -> dict[str, str]:
    """Sucht jede Überschrift im PDF-Text und merkt sich ihre Seite.

    Gesucht wird eine Zeile, die genau der Überschrift entspricht. Im
    Inhaltsverzeichnis steht hinter demselben Text die Punktführung und die
    Seitenzahl — solche Zeilen fallen damit von selbst heraus. Zusätzlich
    läuft die Suche vorwärts: eine Überschrift steht nie vor der vorherigen.
    """
    dump = subprocess.run(
        ["pdftotext", "-layout", str(PDF), "-"],
        check=True, capture_output=True, timeout=300,
    ).stdout.decode("utf-8", "replace")
    pages = [[_norm(line) for line in page.split("\n")] for page in dump.split("\f")]

    found: dict[str, str] = {}
    cursor = 0
    for _, text, anchor in entries:
        needle = _norm(text)
        for page in range(cursor, len(pages)):
            if any(line == needle for line in pages[page]):
                found[anchor] = str(page + 1)
                cursor = page
                break
    return found


def render(pages: list[int] | None, dpi: int = 70) -> list[Path]:
    if PREVIEW.exists():
        shutil.rmtree(PREVIEW)
    PREVIEW.mkdir(parents=True)
    if pages:
        for n in pages:
            subprocess.run(
                ["pdftoppm", "-jpeg", "-r", str(dpi), "-f", str(n), "-l", str(n),
                 str(PDF), str(PREVIEW / f"s{n:03d}")],
                check=True, capture_output=True,
            )
    else:
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", str(dpi), str(PDF), str(PREVIEW / "p")],
            check=True, capture_output=True, timeout=600,
        )
    return sorted(PREVIEW.glob("*.jpg"))


def page_count() -> int:
    info = subprocess.run(
        ["pdfinfo", str(PDF)], check=True, capture_output=True
    ).stdout.decode()
    m = re.search(r"Pages:\s+(\d+)", info)
    return int(m.group(1)) if m else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pages", type=int, nargs="*", help="nur diese Seiten rendern")
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--dpi", type=int, default=70)
    args = ap.parse_args()

    to_pdf()
    print(f"{PDF.relative_to(ROOT)}  ·  {page_count()} Seiten")

    blocks = json.loads(CONTENT.read_text(encoding="utf-8"))["blocks"]
    entries, bid = [], 1000
    for block in blocks[6:-4]:
        if block["type"] == "heading" and block["level"] <= 2:
            bid += 1
            if block["text"] != "Inhaltsverzeichnis":
                entries.append((block["level"], block["text"], f"_Toc9{bid}"))
    found = heading_pages(entries)
    TOC_PAGES.write_text(json.dumps(found, ensure_ascii=False, indent=1), encoding="utf-8")
    missing = [t for _, t, a in entries if a not in found]
    print(f"Seitenzahlen: {len(found)}/{len(entries)}"
          + (f" — nicht gefunden: {missing}" if missing else ""))

    if not args.no_preview:
        shots = render(args.pages, args.dpi)
        print(f"Vorschau: {len(shots)} Seiten in {PREVIEW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
