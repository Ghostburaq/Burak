"""
Hilfsprogramm für den Paritätstest: liest Proben als JSON von stdin und gibt
die Befunde des Python-Prüfers als JSON aus.

  echo '[{"text": "...", "region": "ch", "quelle": null}]' | python3 tests/parity_helper.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from kaltakquise import pruefer  # noqa: E402


def main() -> int:
    proben = json.load(sys.stdin)
    ergebnis = []
    for probe in proben:
        befunde = pruefer.pruefe(
            probe["text"],
            region=probe.get("region", "ch"),
            quelle=probe.get("quelle"),
        )
        ergebnis.append(
            [{"schwere": b.schwere, "regel": b.regel, "text": b.text} for b in befunde]
        )
    json.dump(ergebnis, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
