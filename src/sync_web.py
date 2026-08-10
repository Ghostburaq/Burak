"""
Hält die Web-Kopien des Systemprompts deckungsgleich mit dem Original.

Quelle ist immer prompts/CLAUDE_Kaltakquise_Maschine.md. Erzeugt werden:
  web/prompt.md                        (Anzeige im Browser)
  web/netlify/functions/prompt.mjs     (Systemprompt für die Netlify-Funktion)

Run:  python3 src/sync_web.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(ROOT, "prompts", "CLAUDE_Kaltakquise_Maschine.md")
ZIEL_MD = os.path.join(ROOT, "web", "prompt.md")
ZIEL_MJS = os.path.join(ROOT, "web", "netlify", "functions", "prompt.mjs")

KOPF = (
    "// Erzeugt von src/sync_web.py aus prompts/CLAUDE_Kaltakquise_Maschine.md.\n"
    "// Nicht von Hand bearbeiten.\n"
)


def main() -> int:
    with open(QUELLE, encoding="utf-8") as f:
        prompt = f.read()

    os.makedirs(os.path.dirname(ZIEL_MD), exist_ok=True)
    os.makedirs(os.path.dirname(ZIEL_MJS), exist_ok=True)

    with open(ZIEL_MD, "w", encoding="utf-8") as f:
        f.write(prompt)

    # json.dumps liefert ein gültiges JS-String-Literal.
    with open(ZIEL_MJS, "w", encoding="utf-8") as f:
        f.write(f"{KOPF}export const SYSTEMPROMPT = {json.dumps(prompt, ensure_ascii=False)};\n")

    print(f"geschrieben: {os.path.relpath(ZIEL_MD, ROOT)}")
    print(f"geschrieben: {os.path.relpath(ZIEL_MJS, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
