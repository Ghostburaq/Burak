"""Ruhiges Klavier-Wiegenlied (eigene Komposition), 3/4-Takt, 72 BPM, 16 Takte = 40 s.

Nutzung: python3 wiegenlied.py ausgabe.wav
"""

import sys
import wave

import numpy as np

SR = 44100
BPM = 72
BEAT = 60 / BPM
BAR = 3 * BEAT
BARS = 16
TAIL = 4.0  # Ausklingen
total = int((BARS * BAR + TAIL) * SR)
out = np.zeros(total)


def midi_hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def piano(m, dur, vel):
    t = np.arange(int((dur + 2.5) * SR)) / SR
    f = midi_hz(m)
    tone = np.zeros_like(t)
    for k, a in enumerate([1, 0.45, 0.22, 0.12, 0.06, 0.03], 1):
        tone += (
            a
            * np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k))
            * np.exp(-t * (1.2 + 0.9 * k))
        )
    env = np.minimum(t / 0.006, 1) * np.exp(-t * 0.9)
    return vel * tone * env


def pad(ms, dur, vel):
    t = np.arange(int((dur + 1.5) * SR)) / SR
    sig = sum(
        np.sin(2 * np.pi * midi_hz(m) * t)
        + 0.3 * np.sin(2 * np.pi * midi_hz(m) * 2.003 * t)
        for m in ms
    )
    env = np.minimum(t / 1.2, 1) * np.where(t > dur, np.exp(-(t - dur) * 2.5), 1)
    return vel * sig * env


def add(sig, start):
    i = int(start * SR)
    n = min(len(sig), total - i)
    out[i : i + n] += sig[:n]


# Akkorde: Grundton (Bass), Arpeggio-Töne
CH = {
    "Am": (45, [57, 64, 72, 76, 72, 64], [57, 60, 64]),
    "F": (41, [53, 60, 69, 72, 69, 60], [53, 57, 60]),
    "C": (48, [55, 64, 72, 76, 72, 64], [55, 60, 64]),
    "G": (43, [55, 62, 71, 74, 71, 62], [55, 59, 62]),
}
prog = ["Am", "F", "C", "G"] * 3 + ["Am", "F", "G", "C"]

# Melodie: (Takt, Schlag, MIDI, Dauer in Schlägen)
mel = [
    (4, 0, 76, 2),
    (4, 2, 72, 1),
    (5, 0, 69, 2),
    (5, 2, 72, 1),
    (6, 0, 67, 1),
    (6, 1, 72, 1),
    (6, 2, 76, 1),
    (7, 0, 74, 3),
    (8, 0, 76, 1),
    (8, 1, 81, 1),
    (8, 2, 79, 1),
    (9, 0, 77, 2),
    (9, 2, 76, 1),
    (10, 0, 76, 1),
    (10, 1, 74, 1),
    (10, 2, 72, 1),
    (11, 0, 71, 2),
    (11, 2, 74, 1),
    (12, 0, 72, 2),
    (12, 2, 76, 1),
    (13, 0, 81, 2),
    (13, 2, 79, 1),
    (14, 0, 77, 1),
    (14, 1, 76, 1),
    (14, 2, 74, 1),
    (15, 0, 72, 3),
]

for b, name in enumerate(prog):
    bass, arp, padn = CH[name]
    t0 = b * BAR
    last = b == BARS - 1
    add(piano(bass, BAR, 0.28), t0)
    add(pad(padn, BAR, 0.035), t0)
    notes = arp[:1] if last else arp
    for i, m in enumerate(notes):
        add(piano(m, BEAT / 2, 0.11 if i else 0.14), t0 + i * BEAT / 2)
    if last:
        for i, m in enumerate([60, 64, 67, 72]):  # Schlussakkord sanft gebrochen
            add(piano(m, 3, 0.12), t0 + i * 0.12)

for b, s, m, d in mel:
    add(piano(m, d * BEAT, 0.24), b * BAR + s * BEAT)

out /= np.max(np.abs(out)) / 0.8
data = np.int16(np.repeat(out[:, None], 2, axis=1) * 32767)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())
