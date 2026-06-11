#!/usr/bin/env bash
# Startet das Vermietungstool lokal im Browser.
set -e
cd "$(dirname "$0")"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installiere Abhaengigkeiten..."
    pip3 install -r requirements.txt
fi

echo "Starte Burak Rental Suite auf http://127.0.0.1:8000 ..."
exec python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
