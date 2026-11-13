"""Text mit einer geklonten Stimme sprechen (Chatterbox Multilingual, MIT-Lizenz, CPU).

Nutzung (im venv /opt/stimmklon):
  python klon.py referenz.wav "Text oder Pfad zu .txt" ausgabe.wav [sprache=de] [ausdruck=0.5]

Lange Texte werden in Sätze geteilt, einzeln erzeugt und mit kurzen Pausen verbunden.
Hinweis: Chatterbox setzt ein unhörbares Wasserzeichen (Perth) in jede Ausgabe.
"""

import os
import re
import sys

import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ref, text, out = sys.argv[1:4]
lang = sys.argv[4] if len(sys.argv) > 4 else "de"
expr = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
if os.path.isfile(text):
    with open(text, encoding="utf-8") as fh:
        text = fh.read()

saetze = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
# kurze Sätze zusammenfassen, damit die Betonung natürlich bleibt
teile, akt = [], ""
for s in saetze:
    if len(akt) + len(s) < 180:
        akt = f"{akt} {s}".strip()
    else:
        teile.append(akt)
        akt = s
if akt:
    teile.append(akt)

torch.set_num_threads(os.cpu_count() or 4)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
pause = torch.zeros(1, int(m.sr * 0.35))
stuecke = []
for i, t in enumerate(teile, 1):
    print(f"[{i}/{len(teile)}] {t[:60]}", flush=True)
    stuecke += [
        m.generate(t, language_id=lang, audio_prompt_path=ref, exaggeration=expr),
        pause,
    ]
torchaudio.save(out, torch.cat(stuecke, dim=1), m.sr)
print("Fertig:", out)
