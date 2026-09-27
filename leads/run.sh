#!/usr/bin/env bash
# Komplettlauf MiT Power Leads: Suchliste bauen, scrapen, qualifizieren.
# Voraussetzung: Docker laeuft, Google Maps erreichbar.
set -euo pipefail
cd "$(dirname "$0")/.."
SKILL_DIR=.claude/skills/google-maps-scraper
OUT=/tmp/gmaps-power-output

python3 leads/build_queries.py
bash "$SKILL_DIR/scripts/run-local.sh" \
  --queries leads/queries_power_ch.txt --output-dir "$OUT" --depth 1 --lang de

echo "Scraper laeuft im Hintergrund. Status:"
until node "$SKILL_DIR/scripts/status-local.mjs" --output "$OUT/results.csv" --format csv \
      | tee /dev/stderr | grep -q '"exited"'; do
  sleep 60
done
python3 leads/qualify.py "$OUT/results.csv"
