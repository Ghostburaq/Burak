"""Trauerlied "Für immer bei uns" (eigene Komposition).

a-Moll, 66 BPM, 4/4, 16 Takte. Klavier, Streicher, Cello, gesummte Stimme
(Summen -> "ooh" -> "aah") und leiser Chor auf dem Höhepunkt.
Alles per Klangsynthese erzeugt, keine Samples, keine Fremdrechte.

Nutzung: python3 trauerlied.py ausgabe.wav [ausgabe.mid]
"""

import sys
import wave

import numpy as np
from scipy.signal import lfilter

SR = 44100
BPM = 66
BEAT = 60 / BPM
BAR = 4 * BEAT
BARS = 16
TAIL = 7.0
N = int((BARS * BAR + TAIL) * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(7)


def hz(m):
    return 440.0 * 2 ** ((np.asarray(m) - 69) / 12)


def add(sig, start, pan=0.0):
    i = int(start * SR)
    n = min(len(sig), N - i)
    if n <= 0:
        return
    L[i : i + n] += sig[:n] * np.sqrt(0.5 * (1 - pan))
    R[i : i + n] += sig[:n] * np.sqrt(0.5 * (1 + pan))


# ---------------------------------------------------------------- Klavier
def piano(m, vel):
    dur = 4.5
    t = np.arange(int(dur * SR)) / SR
    f = hz(m)
    sig = np.zeros_like(t)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.00025 * k * k)
        if fk > 9000:
            break
        a = (1 / k**1.6) * (0.6 + 0.4 * vel)
        sig += a * np.sin(2 * np.pi * fk * t) * np.exp(-t * (0.7 + 0.55 * k + f / 900))
    env = np.minimum(t / 0.008, 1) * (
        0.75 * np.exp(-t * 0.8) + 0.25 * np.exp(-t * 0.25)
    )
    return vel * sig * env


# ---------------------------------------------------------------- Streicher
def strings(notes, start, dur, vel, bright=2200):
    n = int((dur + 2.5) * SR)
    t = np.arange(n) / SR
    env = np.minimum(t / 1.6, 1) ** 2 * np.where(t > dur, np.exp(-(t - dur) * 1.6), 1)
    for m in notes:
        for side, cents in ((-1, -7), (1, 7), (0, 0)):
            f = hz(m) * 2 ** (cents / 1200)
            vib = 1 + 0.0025 * np.sin(
                2 * np.pi * (4.8 + rng.random()) * t + rng.random() * 6
            )
            ph = 2 * np.pi * f * np.cumsum(vib) / SR
            sig = np.zeros(n)
            for k in range(1, 30):
                if f * k > 6000:
                    break
                sig += (1 / k) * np.exp(-k * f / bright) * np.sin(k * ph)
            add(vel * sig * env, start, pan=0.55 * side)


# ---------------------------------------------------------------- Stimme
VOWELS = {
    "mm": [(260, 70, 1.0), (1000, 200, 0.03), (2300, 250, 0.01)],
    "oo": [(330, 80, 1.0), (820, 100, 0.45), (2300, 160, 0.08)],
    "aa": [(720, 90, 1.0), (1150, 110, 0.65), (2650, 170, 0.22)],
}


def formant_gain(freq, mix):
    """mix: Array [N,3] Gewichte für mm, oo, aa."""
    g = np.zeros_like(freq)
    for vi, name in enumerate(("mm", "oo", "aa")):
        for F, B, A in VOWELS[name]:
            g += mix[:, vi] * A / (1 + ((freq - F) / B) ** 2)
    return g


def voice_render(f0, amp, mix, breath=0.015):
    ph = 2 * np.pi * np.cumsum(f0) / SR
    out = np.zeros(len(f0))
    for k in range(1, 28):
        fk = f0 * k
        g = formant_gain(fk, mix) / k**1.1
        g[fk > 7500] = 0
        out += g * np.sin(k * ph)
    noise = lfilter([1, -0.6], [1], rng.standard_normal(len(f0)))
    out += breath * noise * mix[:, 1:].sum(axis=1)
    return out * amp


def smooth(x, tau):
    a = np.exp(-1 / (tau * SR))
    return lfilter([1 - a], [1, -a], x, zi=[x[0] * a])[0]


# ---------------------------------------------------------------- Harmonie
CH = {
    "Am": (45, [57, 60, 64]),
    "F": (41, [53, 57, 60]),
    "C": (48, [55, 60, 64]),
    "G": (43, [55, 59, 62]),
    "E": (40, [56, 59, 64]),
    "Em": (40, [55, 59, 64]),
    "Dm": (38, [57, 62, 65]),
}
prog = [
    "Am",
    "F",
    "Am",
    "F",
    "C",
    "G",
    "Am",
    "E",
    "F",
    "G",
    "Em",
    "Am",
    "Dm",
    "E",
    "F",
    "Am",
]

# Melodie (Takt, Schlag, MIDI, Dauer in Schlägen), Takte ab 0
mel = [
    (2, 0, 76, 2),
    (2, 2, 74, 1),
    (2, 3, 72, 1),
    (3, 0, 72, 3),
    (3, 3, 69, 1),
    (4, 0, 67, 2),
    (4, 2, 72, 1),
    (4, 3, 76, 1),
    (5, 0, 74, 3.5),
    (6, 0, 76, 2),
    (6, 2, 74, 1),
    (6, 3, 72, 1),
    (7, 0, 71, 3),
    (7, 3, 68, 0.8),
    (8, 0, 69, 2),
    (8, 2, 72, 1),
    (8, 3, 77, 1),
    (9, 0, 76, 2),
    (9, 2, 74, 1.8),
    (10, 0, 71, 2),
    (10, 2, 76, 1),
    (10, 3, 79, 1),
    (11, 0, 81, 4),
    (12, 0, 77, 2),
    (12, 2, 76, 1),
    (12, 3, 74, 1),
    (13, 0, 76, 2),
    (13, 2, 68, 1),
    (13, 3, 71, 1),
    (14, 0, 72, 3),
    (14, 3, 71, 1),
    (15, 0, 69, 4),
]

# ---------------------------------------------------------------- Klavier spielen
for b, name in enumerate(prog):
    bass, ch = CH[name]
    t0 = b * BAR
    soft = 0.55 if b < 2 or b >= 14 else 0.8
    add(piano(bass, 0.45 * soft), t0, -0.2)
    add(piano(bass + 12, 0.25 * soft), t0 + 0.01, -0.2)
    tones = [ch[0], ch[1], ch[2], ch[0] + 12, ch[1] + 12]
    pattern = [0, 1, 2, 3, 4, 3, 2, 1]
    if b == BARS - 1:
        pattern = [0, 1, 2, 3, 4]  # Schluss: einmal aufsteigend, dann ausklingen
    for i, p in enumerate(pattern):
        m = tones[p]
        jitter = rng.normal(0, 0.008)
        add(
            piano(m, (0.16 if i % 4 else 0.2) * soft),
            t0 + i * BEAT / 2 * (1.25 if b == BARS - 1 else 1) + jitter,
            (m - 62) / 30,
        )
add(piano(76, 0.12), (BARS - 1) * BAR + 3.2, 0.4)  # letzter hoher Ton

# ---------------------------------------------------------------- Streicher und Cello
for b, name in enumerate(prog):
    if 2 <= b <= 14:
        bass, ch = CH[name]
        vel = 0.010 if b < 6 else 0.016 if b < 10 else 0.022
        strings([n + 12 for n in ch] if b >= 10 else ch, b * BAR, BAR, vel)
        if b >= 6:
            strings([bass + 12], b * BAR, BAR, 0.03, bright=1200)  # Cello

# ---------------------------------------------------------------- Gesummte Melodie
f_step = np.full(N, hz(69))
amp = np.zeros(N)
mix = np.zeros((N, 3))
since = np.zeros(N)
for bar, beat, m, d in mel:
    s = int((bar * BAR + beat * BEAT) * SR)
    e = int((bar * BAR + (beat + d) * BEAT) * SR)
    f_step[s:] = hz(m)
    seg = np.arange(e - s) / SR
    swell = np.minimum(seg / 0.18, 1) * (0.85 + 0.15 * np.minimum(seg / (d * BEAT), 1))
    tail = np.minimum((e - s - np.arange(e - s)) / (0.08 * SR), 1)
    amp[s:e] = np.maximum(amp[s:e], swell * tail)
    since[s:e] = seg
    # Klangfarbe: Takte 2-5 Summen, 6-9 "ooh", 10-13 "aah", danach zurück zu Summen
    v = 0 if bar < 6 or bar >= 14 else 1 if bar < 10 else 2
    mix[s:e, v] = 1
mix = np.stack([smooth(mix[:, i], 0.4) for i in range(3)], axis=1)
mix /= np.maximum(mix.sum(axis=1, keepdims=True), 1e-6)
logf = smooth(np.log(f_step), 0.05)
t = np.arange(N) / SR
vib_depth = 0.22 * np.clip((since - 0.3) / 0.5, 0, 1)
vib = vib_depth * np.sin(2 * np.pi * 5.2 * t + 0.4 * np.sin(2 * np.pi * 0.3 * t))
f0 = np.exp(logf) * 2 ** (vib / 12)
amp = smooth(amp, 0.03)
voice = voice_render(f0, amp, mix)
dyn = np.interp(
    t,
    [0, 6 * BAR, 10 * BAR, 12 * BAR, 14 * BAR, BARS * BAR],
    [0.55, 0.65, 0.8, 1.0, 0.7, 0.5],
)
add(voice * dyn * 0.09, 0, 0.0)


# ---------------------------------------------------------------- Chor auf dem Höhepunkt
def choir_note(m, start, dur, vel):
    n = int((dur + 2) * SR)
    tt = np.arange(n) / SR
    env = np.minimum(tt / 1.2, 1) ** 2 * np.where(
        tt > dur, np.exp(-(tt - dur) * 1.8), 1
    )
    for side, cents in ((-1, -9), (1, 8), (0, 2)):
        ff = (
            hz(m)
            * 2 ** (cents / 1200)
            * 2 ** (0.12 * np.sin(2 * np.pi * (4.6 + rng.random()) * tt) / 12)
        )
        mx = np.zeros((n, 3))
        mx[:, 2 if m < 66 else 1] = 1
        add(vel * voice_render(ff, env, mx, breath=0.03), start, 0.6 * side)


for b in range(9, 14):
    _, ch = CH[prog[b]]
    for m in ch:
        choir_note(m, b * BAR, BAR, 0.012 if b == 9 else 0.02)

# ---------------------------------------------------------------- Ausgabe
mixdown = np.stack([L, R], axis=1)
mixdown = np.tanh(mixdown / np.max(np.abs(mixdown)) * 1.2) * 0.85
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(np.int16(mixdown * 32767).tobytes())

# Optional: MIDI-Export für GarageBand, FL Studio, Logic
if len(sys.argv) > 2:
    import mido

    mid = mido.MidiFile(ticks_per_beat=480)

    def track(name, events, program):
        tr = mido.MidiTrack()
        tr.append(mido.MetaMessage("track_name", name=name))
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)))
        tr.append(mido.Message("program_change", program=program))
        evs = []
        for start, dur, m, v in events:
            evs += [
                (int(start * 480), "on", m, v),
                (int((start + dur) * 480), "off", m, 0),
            ]
        evs.sort(key=lambda e: (e[0], e[1] == "on"))
        last = 0
        for tick, kind, m, v in evs:
            tr.append(
                mido.Message(
                    "note_on" if kind == "on" else "note_off",
                    note=m,
                    velocity=v,
                    time=tick - last,
                )
            )
            last = tick
        mid.tracks.append(tr)

    track("Melodie (Stimme)", [(b * 4 + s, d, m, 80) for b, s, m, d in mel], 53)
    pno = []
    for b, name in enumerate(prog):
        bass, ch = CH[name]
        tones = [ch[0], ch[1], ch[2], ch[0] + 12, ch[1] + 12]
        pno.append((b * 4, 4, bass, 70))
        pno += [
            (b * 4 + i * 0.5, 0.5, tones[p], 60)
            for i, p in enumerate([0, 1, 2, 3, 4, 3, 2, 1])
        ]
    track("Klavier", pno, 0)
    track(
        "Streicher",
        [
            (b * 4, 4, n, 50)
            for b, nm in enumerate(prog)
            if 2 <= b <= 14
            for n in CH[nm][1]
        ],
        48,
    )
    mid.save(sys.argv[2])
