"""Druckvoller Hip-Hop/Trap-Beat für Fitness- und Mindset-Clips (eigene Komposition).

100 BPM, 4/4, 10 Takte = 24 s + Ausklang. c-Moll: Cm Ab Eb Bb.
Takt 0-1: Intro (dunkles Pad, Glocken-Melodie), Snare-Wirbel am Ende von Takt 1.
Takt 2-7: Drop (Kick, harte Snare, Hi-Hat-Rolls, 808-Bass mit Gleiten, Glocken-Hook).
Takt 8-9: Endkarte (Pad + Bass, Schlussschlag auf Takt 9).

Nutzung: python3 power_beat.py ausgabe.wav
"""

import sys
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
BARS = 10
N = int((BARS * BAR + 3) * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(11)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    n = min(len(sig), N - i)
    if n > 0:
        L[i : i + n] += gain * sig[:n] * np.sqrt(0.5 * (1 - pan))
        R[i : i + n] += gain * sig[:n] * np.sqrt(0.5 * (1 + pan))


def filt(x, fc, kind="low", order=2):
    if isinstance(fc, (list, tuple)):
        wn = [f / (SR / 2) for f in fc]
    else:
        wn = min(fc, SR / 2 - 100) / (SR / 2)
    b, a = butter(order, wn, kind)
    return lfilter(b, a, x)


def t_arr(d):
    return np.arange(int(d * SR)) / SR


def kick():
    t = t_arr(0.5)
    f = 45 + 140 * np.exp(-t * 35)
    k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    click = filt(rng.standard_normal(len(t)), 3000, "high") * np.exp(-t * 300) * 0.3
    return np.tanh((k + click) * 1.8)


def snare():
    t = t_arr(0.35)
    noise = filt(rng.standard_normal(len(t)), [1500, 8000], "band") * np.exp(-t * 14)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.6
    return np.tanh((noise + body) * 1.5)


def hat(d=0.05):
    t = t_arr(d)
    return filt(rng.standard_normal(len(t)), 8000, "high") * np.exp(-t * 70)


def bass808(m_from, m_to, dur):
    t = t_arr(dur)
    glide = np.clip(t / 0.08, 0, 1)
    f = hz(m_from) * (1 - glide) + hz(m_to) * glide
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(t / 0.005, 1) * np.exp(-t * 1.2)
    return np.tanh(s * env * 2.2)


def bell(m, dur=0.9):
    t = t_arr(dur)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(
        -t * 6
    )
    s += 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10)
    return s * np.exp(-t * 3.5) * np.minimum(t / 0.003, 1)


def pad(notes, dur):
    t = t_arr(dur)
    s = np.zeros_like(t)
    for m in notes:
        for d in (-0.1, 0.1):
            s += ((t * hz(m) * 2 ** (d / 12)) % 1) * 2 - 1
    env = np.minimum(t / 0.6, 1) * np.minimum((dur - t) / 0.4, 1)
    return filt(s * env, 1400) / len(notes)


CH = {"Cm": [48, 51, 55], "Ab": [44, 48, 51], "Eb": [46, 51, 55], "Bb": [46, 50, 53]}
ROOT = {"Cm": 36, "Ab": 32, "Eb": 39, "Bb": 34}
prog = ["Cm", "Ab", "Eb", "Bb"] * 3
# Glocken-Hook (Achtel-Positionen 0-7, MIDI)
HOOK = [(0, 72), (1.5, 75), (3, 79), (4, 77), (5.5, 75), (6, 74)]

for b in range(BARS):
    t0 = b * BAR
    name = prog[b]
    drop = 2 <= b < 8
    add(pad([n + 12 for n in CH[name]], BAR), t0, 0, 0.09 if not drop else 0.06)
    if b < 9:
        for pos, m in HOOK:
            mm = m - (0 if name in ("Cm", "Eb") else 1 if name == "Bb" else 0)
            add(bell(mm), t0 + pos * BEAT / 2, 0.25, 0.10 if drop else 0.08)
    if drop:
        # Kick-Pattern (Viertel-Positionen)
        for k in (0, 1.75, 2.5):
            add(kick(), t0 + k * BEAT, 0, 0.8)
        for s in (1, 3):
            add(snare(), t0 + s * BEAT, 0, 0.45)
        # Hi-Hats in Achteln, Rolls in Takt 5 und 7
        steps = 32 if b in (5, 7) else 8
        for h in range(steps):
            if steps == 32 and h < 16:
                continue
            pos = h * (4 / steps) if steps == 8 else 2 + (h - 16) * (2 / 16)
            add(
                hat(),
                t0 + pos * BEAT,
                0.3 if h % 2 else -0.3,
                0.16 if steps == 8 else 0.1,
            )
        # 808 folgt dem Grundton, mit Gleiten vom vorherigen Takt
        prev = ROOT[prog[b - 1]] if b > 0 else ROOT[name]
        add(bass808(prev, ROOT[name], BAR * 0.95), t0, 0, 0.55)

# Snare-Wirbel vor dem Drop
for i in range(16):
    t = BAR + 2 * BEAT + i * (2 * BEAT / 16)
    add(snare(), t, 0, 0.08 + 0.25 * i / 16)
# Endkarte: Bass und Schlussschlag
add(bass808(ROOT["Cm"], ROOT["Cm"], BAR * 2), 8 * BAR, 0, 0.45)
add(kick(), 9 * BAR, 0, 0.9)
add(snare(), 9 * BAR, 0, 0.4)
for m in (60, 63, 67, 72):
    add(bell(m, 2.5), 9 * BAR, 0, 0.09)

mix = np.stack([L, R], 1)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.5) * 0.9
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(np.int16(mix * 32767).tobytes())
print("Fertig:", sys.argv[1])
