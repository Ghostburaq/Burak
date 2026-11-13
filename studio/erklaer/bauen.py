"""Stimme pro Satz erzeugen und Zeitplan für Remotion schreiben.

Nutzung: python3 bauen.py skript.json ausgabeordner [piper|klon]
Erzeugt: ausgabeordner/stimme.wav und studio/remotion/src/erklaer-zeitplan.ts
"""

import json
import os
import subprocess
import sys
import wave

skript, out = sys.argv[1], sys.argv[2]
modus = sys.argv[3] if len(sys.argv) > 3 else "piper"
bin_dir = os.path.join(os.path.dirname(__file__), "..", "bin")
os.makedirs(out, exist_ok=True)
with open(skript, encoding="utf-8") as fh:
    cfg = json.load(fh)

START, PAUSE = 0.6, 0.45
zeit, teile, plan = START, [], []
for i, s in enumerate(cfg["saetze"]):
    wav = os.path.join(out, f"satz_{i}.wav")
    cmd = "meine-stimme" if modus == "klon" else "sprechen"
    subprocess.run(
        [os.path.join(bin_dir, cmd), s["sprich"], wav], check=True, capture_output=True
    )
    roh = os.path.join(out, f"satz_{i}_48k.wav")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", wav, "-ar", "48000", "-ac", "1", roh],
        check=True,
    )
    with wave.open(roh) as w:
        dauer = w.getnframes() / w.getframerate()
    plan.append(
        {
            "szene": s["szene"],
            "text": s["text"],
            "start": round(zeit, 3),
            "dauer": round(dauer, 3),
        }
    )
    teile.append((zeit, roh))
    zeit += dauer + PAUSE
gesamt = zeit + 1.5

# Stimme zu einer Spur zusammensetzen
inputs, filt = [], ""
for i, (t, f) in enumerate(teile):
    inputs += ["-i", f]
    filt += f"[{i}]adelay={int(t * 1000)}:all=1[a{i}];"
filt += (
    "".join(f"[a{i}]" for i in range(len(teile)))
    + f"amix=inputs={len(teile)}:normalize=0,apad=whole_dur={gesamt}[v]"
)
stimme = os.path.join(out, "stimme.wav")
subprocess.run(
    [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        *inputs,
        "-filter_complex",
        filt,
        "-map",
        "[v]",
        "-ar",
        "48000",
        stimme,
    ],
    check=True,
)

ts = os.path.join(
    os.path.dirname(__file__), "..", "remotion", "src", "erklaer-zeitplan.ts"
)
with open(ts, "w", encoding="utf-8") as fh:
    fh.write("// automatisch erzeugt von studio/erklaer/bauen.py\n")
    fh.write(f"export const TITEL = {json.dumps(cfg['titel'], ensure_ascii=False)};\n")
    fh.write(f"export const GESAMT = {round(gesamt, 3)};\n")
    fh.write(f"export const PLAN = {json.dumps(plan, ensure_ascii=False, indent=2)};\n")
print(f"Fertig: {stimme} ({gesamt:.1f} s), Zeitplan: {ts}")
