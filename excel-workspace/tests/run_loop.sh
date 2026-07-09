#!/bin/bash
# Vollständige Test-Schleife: baut beide Varianten, konvertiert via LibreOffice,
# scannt auf Formelfehler, prüft Struktur, läuft E2E. Wiederholt RUNS-mal.
# Bricht mit Exit 1 ab, sobald irgendein Test fehlschlägt.
set -u
cd "$(dirname "$0")"
RUNS="${1:-3}"
FAIL=0

echo "=================================================================="
echo " BUILD: beide Varianten + xlsm packen"
echo "=================================================================="
python3 extract.py >/dev/null 2>&1 || { echo "extract FAILED"; exit 1; }
python3 make_testimport.py >/dev/null 2>&1 || { echo "make_testimport FAILED"; exit 1; }
python3 make_rawoffer.py   >/dev/null 2>&1 || { echo "make_rawoffer FAILED"; exit 1; }
python3 build.py            >/dev/null 2>&1 || { echo "build xlsm-Basis FAILED"; exit 1; }
OHNE_MAKROS=1 python3 build.py >/dev/null 2>&1 || { echo "build xlsx FAILED"; exit 1; }
python3 vba_bin.py         >/dev/null 2>&1 || { echo "vba_bin FAILED"; exit 1; }
python3 package_xlsm.py    >/dev/null 2>&1 || { echo "package FAILED"; exit 1; }
echo "Build OK"

for i in $(seq 1 "$RUNS"); do
  echo ""
  echo "############### DURCHLAUF $i / $RUNS ###############"

  echo "--- [1] Struktur (xlsm)"
  python3 test_structure.py MiT_GESAMTMAPPE_2026.xlsm 2>&1 | tail -1
  python3 test_structure.py MiT_GESAMTMAPPE_2026.xlsm >/dev/null 2>&1 || FAIL=1

  echo "--- [2] Recalc xlsm (LibreOffice, alle Werte)"
  rm -rf lo_a && mkdir lo_a
  timeout 600 soffice --headless --convert-to xlsx --outdir lo_a MiT_GESAMTMAPPE_2026.xlsm >/dev/null 2>&1
  python3 test_recalc.py lo_a/MiT_GESAMTMAPPE_2026.xlsx 2>&1 | grep -E "Formelfehler|Stichproben"
  python3 test_recalc.py lo_a/MiT_GESAMTMAPPE_2026.xlsx >/dev/null 2>&1 || FAIL=1

  echo "--- [3] Recalc xlsx makrofrei"
  rm -rf lo_b && mkdir lo_b
  timeout 600 soffice --headless --convert-to xlsx --outdir lo_b MiT_GESAMTMAPPE_2026_OHNE_MAKROS.xlsx >/dev/null 2>&1
  python3 test_recalc.py lo_b/MiT_GESAMTMAPPE_2026_OHNE_MAKROS.xlsx 2>&1 | grep -E "Formelfehler|Stichproben"
  python3 test_recalc.py lo_b/MiT_GESAMTMAPPE_2026_OHNE_MAKROS.xlsx >/dev/null 2>&1 || FAIL=1

  echo "--- [4] E2E-Makrosuite (Import/Duplikate/Blatt/Monatsreport)"
  timeout 500 python3 test_final.py 2>&1 | grep -E "ERGEBNIS"
  timeout 500 python3 test_final.py >/dev/null 2>&1 || FAIL=1

  if [ "$FAIL" -ne 0 ]; then
    echo ">>> DURCHLAUF $i: FEHLER GEFUNDEN — Schleife stoppt."
    exit 1
  fi
  echo ">>> DURCHLAUF $i: ALLES GRÜN"
done

echo ""
echo "=================================================================="
echo " ALLE $RUNS DURCHLÄUFE 100% FEHLERFREI"
echo "=================================================================="
