import sys
from faster_whisper import WhisperModel

src, dst, model, lang = sys.argv[1:5]

def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s % 1) * 1000):03}"

segs, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(
    src, language=lang, vad_filter=True)
with open(dst, "w", encoding="utf-8") as f:
    for i, s in enumerate(segs, 1):
        f.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n")
