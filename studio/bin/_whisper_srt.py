import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

src, dst, model, lang = sys.argv[1:5]

# Ton per ffmpeg dekodieren (16 kHz mono), unabhängig von PyAV-Versionen
raw = subprocess.run(
    [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        src,
        "-f",
        "s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-",
    ],
    check=True,
    capture_output=True,
).stdout
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def ts(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s % 1) * 1000):03}"


segs, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(
    audio, language=lang, vad_filter=True
)
with open(dst, "w", encoding="utf-8") as f:
    f.writelines(
        f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n"
        for i, s in enumerate(segs, 1)
    )
