#!/usr/bin/env bash
# Offerte bauen + PDF erzeugen - alles auf einen Schlag.
#   bash offerten/erstelle_offerte.sh [datei.xlsx] [ausgabe.pdf]
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Pakete prüfen"
python3 -c "import openpyxl, fpdf" 2>/dev/null || pip install -q openpyxl fpdf2

echo "==> Master-Vorlage bauen"
python3 offerten/build_template.py

echo "==> PDF erzeugen"
python3 offerten/offerte_to_pdf.py "$@"

echo "==> Fertig."
