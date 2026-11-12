"""Energetischer Elektro-Beat für Kurzvideos (eigene Komposition).

120 BPM, 4/4, 10 Takte = 20 s + Ausklang. a-Moll: Am F C G.
Aufbau: 2 Takte Intro (Pad + gefiltertes Arpeggio), 2 Takte mit Kick und Bass,
Riser, Drop ab Takt 4, ab Takt 8 Outro mit Schlussschlag.

Nutzung: python3 beat.py ausgabe.wav
"""

import sys
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
BEAT = 0.5
BAR = 2.0
BARS = 10
N = int((BARS * BAR + 2.5) * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(3)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    n = min(len(sig), N - i)
    if n > 0:
        L[i : i + n] += gain * sig[:n] * np.sqrt(0.5 * (1 - pan))
        R[i : i + n] += gain * sig[:n] * np.sqrt(0.5 * (1 + pan))


def lp(x, fc, order=2):
    b, a = butter(order, min(fc, SR / 2 - 100) / (SR / 2))
    return lfilter(b, a, x)


def saw(f, dur, detune=0.0):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for d in (-detune, 0, detune):
        ph = (t * f * 2 ** (d / 1200)) % 1
        out += 2 * ph - 1
    return out / 3


def kick():
    t = np.arange(int(0.45 * SR)) / SR
    f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)


def hat(dur=0.06):
    n = rng.standard_normal(int(dur * SR))
    b, a = butter(2, 7000 / (SR / 2), "high")
    return lfilter(b, a, n) * np.exp(-np.arange(len(n)) / SR * 60)


def clap():
    n = rng.standard_normal(int(0.25 * SR))
    b, a = butter(2, [900 / (SR / 2), 3500 / (SR / 2)], "band")
    env = np.exp(-np.arange(len(n)) / SR * 18)
    return lfilter(b, a, n) * env


CH = {"Am": [57, 60, 64], "F": [53, 57, 60], "C": [55, 60, 64], "G": [55, 59, 62]}
ROOT = {"Am": 33, "F": 29, "C": 36, "G": 31}
prog = ["Am", "F", "C", "G"] * 3

for b in range(BARS):
    t0 = b * BAR
    name = prog[b]
    full = 4 <= b < 8
    # Pad
    pad = sum(saw(hz(m), BAR, 12) for m in CH[name])
    env = np.minimum(np.arange(len(pad)) / SR / 0.3, 1)
    add(lp(pad * env, 1200 if b < 4 else 2200), t0, 0, 0.05 if not full else 0.04)
    # Arpeggio (16tel), Filter öffnet sich im Intro
    arp = CH[name] + [CH[name][0] + 12]
    cutoff = 600 + 3000 * min(b / 4, 1) if b < 4 else 4500
    for i in range(16 if b < 9 else 4):
        m = arp[[0, 1, 2, 3, 2, 1, 2, 3][i % 8]] + 12
        n = saw(hz(m), 0.12, 8) * np.exp(-np.arange(int(0.12 * SR)) / SR * 22)
        add(lp(n, cutoff), t0 + i * BEAT / 4, 0.35 if i % 2 else -0.35, 0.09)
    # Kick, Bass, Hats, Clap
    if 2 <= b < 9:
        for k in range(4):
            add(kick(), t0 + k * BEAT, 0, 0.75)
            bn = saw(hz(ROOT[name]), BEAT * 0.9) * np.exp(
                -np.arange(int(BEAT * 0.9 * SR)) / SR * 3
            )
            add(lp(bn, 300 if full else 180, 4), t0 + k * BEAT + 0.25, 0, 0.5)
            add(hat(), t0 + k * BEAT + 0.25, 0.2, 0.18)
            if full:
                add(hat(0.03), t0 + k * BEAT + 0.125, -0.2, 0.08)
                add(hat(0.03), t0 + k * BEAT + 0.375, -0.2, 0.08)
        if full:
            add(clap(), t0 + BEAT, 0, 0.35)
            add(clap(), t0 + 3 * BEAT, 0, 0.35)

# Riser vor dem Drop (Takt 3) und Schlussschlag (Takt 9)
r = rng.standard_normal(int(BAR * SR))
tt = np.arange(len(r)) / SR
riser = np.zeros_like(r)
for seg in range(16):
    a, e = seg * len(r) // 16, (seg + 1) * len(r) // 16
    riser[a:e] = lp(r[a:e], 500 + seg * 400)
add(riser * (tt / BAR) ** 2, 3 * BAR, 0, 0.22)
add(kick(), 4 * BAR, 0, 0.9)
for m in [45, 57, 64, 69]:
    hit = saw(hz(m), 2.5, 15) * np.exp(-np.arange(int(2.5 * SR)) / SR * 1.5)
    add(lp(hit, 2500), 9 * BAR, 0, 0.12)
add(kick(), 9 * BAR, 0, 0.9)

mix = np.stack([L, R], 1)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) * 0.9
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(np.int16(mix * 32767).tobytes())
print("Fertig:", sys.argv[1])
