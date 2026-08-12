#!/usr/bin/env bash
# Alles einlesen, was in inbox/ liegt, und die Excel-Mappe aktualisieren.
#
#   ./aktualisieren.sh                  -> inbox/ verarbeiten
#   ./aktualisieren.sh ~/Downloads/*.ics -> einzelne Dateien zusätzlich
#   ./aktualisieren.sh --neu-aufbauen   -> alles von Grund auf neu einlesen
#
# Die Mappe muss dabei in Excel geschlossen sein.

set -euo pipefail
cd "$(dirname "$0")"

python3 -c "import openpyxl" 2>/dev/null || {
    echo "openpyxl fehlt — wird installiert…"
    pip install --quiet openpyxl
}

# Übergebene Dateien zuerst in die inbox legen, damit sie dauerhaft erfasst sind
dateien=()
for arg in "$@"; do
    if [[ -f "$arg" ]]; then
        cp -n "$arg" inbox/ 2>/dev/null || true
    else
        dateien+=("$arg")
    fi
done

python3 src/aktivitaeten/cli.py "${dateien[@]+"${dateien[@]}"}"

echo
echo "Fertig. Mappe öffnen:  output/Aktivitaeten.xlsx"
