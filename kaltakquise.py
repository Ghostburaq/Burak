#!/usr/bin/env python3
"""
Starter für die Kaltakquise-Maschine.

  python3 kaltakquise.py "Implenia baut in Beringen ein Rechenzentrum, 36 MW"
  python3 kaltakquise.py pruefen entwurf.txt
  python3 kaltakquise.py prompt
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from kaltakquise.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
