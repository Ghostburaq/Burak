# -*- coding: utf-8 -*-
"""
NEXA Reel 9:16 - "100 kVA sind nicht 100 kW"
Rendert Einzelbilder mit Pillow und schneidet sie per ffmpeg zu einem MP4.

Alle Texte stehen in SCRIPT, alle Farben in der Palette, alle Zeitpunkte in
SCENES. Diese drei Bloecke sind zum Austauschen gedacht, der Rest bleibt gleich.
"""
import math, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT = os.environ.get("OUTFILE", "/home/user/Burak/NEXA_Reel_kVA_vs_kW.mp4")
FRAMES = os.environ.get("FRAMEDIR", "/tmp/reel_frames")

SAFE = 96                 # seitlicher Rand
SAFE_W = W - 2 * SAFE     # nutzbare Breite

# ---------------------------------------------------------------- Palette
BG     = (10, 11, 13)
INK    = (255, 255, 255)
MUTED  = (140, 146, 156)
ACCENT = (0, 224, 198)    # Platzhalter, bis die NEXA-Farben feststehen

FD = "/usr/share/fonts/opentype/inter/InterDisplay-%s.otf"
FT = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
_fc = {}
def font(size, weight="Black", display=True):
    key = (int(size), weight, display)
    if key not in _fc:
        path = (FD if display else FT) % weight
        if not os.path.exists(path):
            path = FT % weight
        _fc[key] = ImageFont.truetype(path, int(size))
    return _fc[key]

_probe = ImageDraw.Draw(Image.new("L", (8, 8)))
def measure(f, s, spacing=14):
    b = _probe.multiline_textbbox((0, 0), s, font=f, spacing=spacing)
    return b[2] - b[0], b[3] - b[1]

def fit(s, max_size, max_w=None, weight="Black", display=True, spacing=14):
    """Groesste Schriftgroesse, bei der der Text noch in die Breite passt."""
    max_w = max_w or SAFE_W
    size = max_size
    while size > 20:
        f = font(size, weight, display)
        if measure(f, s, spacing)[0] <= max_w:
            return f
        size -= 2
    return font(20, weight, display)

# ---------------------------------------------------------------- Easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t):   return 1 - (1 - clamp(t)) ** 3
def ease_out_x(t): return 1 - 2 ** (-10 * clamp(t))
def ease_in_out(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
def seg(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else (1.0 if t >= start else 0.0)
def inout(t, start, end, fade=0.32):
    if t < start - 0.01 or t > end + 0.01:
        return 0.0
    return min(ease_out(seg(t, start, fade)),
               1.0 - ease_out(seg(t, end - fade, fade)))

# ---------------------------------------------------------------- Zeichnen
def layer():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)
def put(base, im): return Image.alpha_composite(base, im)
def rgba(c, a): return (c[0], c[1], c[2], int(clamp(a) * 255))

def text(d, xy, s, f, color, a=1.0, anchor="mm", spacing=14):
    if a <= 0.004:
        return
    d.multiline_text(xy, s, font=f, fill=rgba(color, a), anchor=anchor,
                     align="center", spacing=spacing)

# ---------------------------------------------------------------- Hintergrund
def make_glow(radius, color, peak=78):
    size = radius * 2
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for i in range(48, 0, -1):
        r = radius * i / 48
        a = int(peak * (1 - i / 48) ** 2.2)
        gd.ellipse([radius - r, radius - r, radius + r, radius + r],
                   fill=(color[0], color[1], color[2], a))
    return g.filter(ImageFilter.GaussianBlur(radius * 0.18))

GLOW = GRID = VIGN = None
def build_static():
    global GLOW, GRID, VIGN
    GLOW = make_glow(640, ACCENT)
    GRID, gd = layer()
    for x in range(0, W + 1, 120):
        gd.line([(x, 0), (x, H)], fill=rgba(INK, 0.028), width=1)
    for y in range(0, H + 1, 120):
        gd.line([(0, y), (W, y)], fill=rgba(INK, 0.028), width=1)
    VIGN = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(VIGN)
    for i in range(70):
        a = int(70 * (i / 70) ** 2.0)
        vd.rectangle([i * 3, i * 3, W - i * 3, H - i * 3], outline=(0, 0, 0, a), width=3)
    VIGN = VIGN.filter(ImageFilter.GaussianBlur(40))

def background(t, total):
    im = Image.new("RGBA", (W, H), BG + (255,))
    gx = W * 0.5 + math.sin(t * 0.33) * 320
    gy = H * 0.46 + math.cos(t * 0.27) * 400
    im.alpha_composite(GLOW, (int(gx - 640), int(gy - 640)))
    im = Image.alpha_composite(im, GRID)
    im = Image.alpha_composite(im, VIGN)
    pr, pd = layer()
    y = 96                                   # oben, ausserhalb der Bedienleiste
    pd.line([(SAFE, y), (W - SAFE, y)], fill=rgba(INK, 0.12), width=6)
    pd.line([(SAFE, y), (SAFE + SAFE_W * clamp(t / total), y)],
            fill=rgba(ACCENT, 0.9), width=6)
    return put(im, pr)

def kicker(d, s, a, y):
    if a <= 0.004:
        return
    f = font(38, "SemiBold", display=False)
    w, _ = measure(f, s)
    d.ellipse([W / 2 - w / 2 - 44, y - 11, W / 2 - w / 2 - 22, y + 11], fill=rgba(ACCENT, a))
    text(d, (W / 2 + 11, y), s, f, MUTED, a)

# ---------------------------------------------------------------- Texte
SCRIPT = {
 "hook_kicker":    "Der teuerste Rechenfehler in der Auslegung",
 "cost_1":         "Gleiche Zahl.",
 "cost_2":         "20 % weniger Leistung.",
 "defs_kicker":    "Zwei Grössen, zwei Bedeutungen",
 "kva_sub":        "Scheinleistung S",
 "kva_body":       "Was das Aggregat\nliefern kann",
 "kw_sub":         "Wirkleistung P",
 "kw_body":        "Was deine Last\nwirklich umsetzt",
 "defs_note":      "Dazwischen liegt der Leistungsfaktor.",
 "formula_kicker": "Der Zusammenhang",
 "formula":        "P = S × cos φ",
 "cosphi":         "cos φ = 0,8",
 "formula_note":   "Aggregate werden in der Regel\nbei cos φ 0,8 angegeben.",
 "bars_kicker":    "100 kVA, aufgeteilt",
 "bar_s":          "Scheinleistung S",
 "bar_p":          "Wirkleistung P",
 "bar_q":          "Blindleistung Q",
 "bars_note":      "Nutzbar sind 80 kW.\nDer Rest ist Blindleistung.",
 "punch_q":        "Du brauchst 100 kW?",
 "punch_a":        "Dann brauchst du\n125 kVA.",
 "punch_math":     "100 kW ÷ 0,8 = 125 kVA",
 "cta":            "Frag immer nach cos φ.",
 "brand":          "NEXA",
}

# ---------------------------------------------------------------- Szenen
def scene_hook(t, im):
    l, d = layer()
    a1 = inout(t, 0.15, 4.30, 0.28)
    if a1:
        p = ease_out_x(seg(t, 0.15, 0.55))
        text(d, (W / 2, 760 + (1 - p) * 44), "100 kVA",
             fit("100 kVA", 196 + 36 * (1 - p)), INK, a1)
    a2 = inout(t, 1.05, 4.30, 0.22)
    if a2:
        p = ease_out_x(seg(t, 1.05, 0.45))
        text(d, (W / 2, 990), "≠", font(240 * (0.62 + 0.38 * p)), ACCENT, a2)
    a3 = inout(t, 1.55, 4.30, 0.24)
    if a3:
        p = ease_out_x(seg(t, 1.55, 0.55))
        text(d, (W / 2, 1220 - (1 - p) * 44), "100 kW",
             fit("100 kW", 196 + 36 * (1 - p)), INK, a3)
    kicker(d, SCRIPT["hook_kicker"], inout(t, 2.55, 4.30, 0.28), 1430)
    return put(im, l)

def scene_cost(t, im):
    l, d = layer()
    a1 = inout(t, 4.15, 7.70, 0.28)
    if a1:
        p = ease_out(seg(t, 4.15, 0.55))
        text(d, (W / 2, 930 + (1 - p) * 34), SCRIPT["cost_1"],
             fit(SCRIPT["cost_1"], 104), MUTED, a1)
    a2 = inout(t, 4.80, 7.70, 0.24)
    if a2:
        p = ease_out_x(seg(t, 4.80, 0.5))
        text(d, (W / 2, 1090), SCRIPT["cost_2"],
             fit(SCRIPT["cost_2"], 118 * (0.9 + 0.1 * p)), ACCENT, a2)
    return put(im, l)

def card(d, x, y, w, h, title, sub, body, a, accent=False):
    if a <= 0.004:
        return
    col = ACCENT if accent else INK
    d.rounded_rectangle([x, y, x + w, y + h], radius=40,
                        fill=rgba(INK, 0.05 * a), outline=rgba(col, 0.40 * a), width=3)
    text(d, (x + w / 2, y + 108), title, fit(title, 116, w - 60), col, a)
    text(d, (x + w / 2, y + 214), sub, fit(sub, 46, w - 56, "Bold"), INK, a * 0.95)
    text(d, (x + w / 2, y + 320), body,
         fit(body, 38, w - 56, "Medium", display=False, spacing=12),
         MUTED, a * 0.9, spacing=12)

def scene_defs(t, im):
    l, d = layer()
    kicker(d, SCRIPT["defs_kicker"], inout(t, 7.55, 13.50, 0.28), 620)
    w, h, gap = 430, 430, 56
    x0 = (W - (w * 2 + gap)) / 2
    y0 = 760
    a1 = inout(t, 7.70, 13.50, 0.26)
    card(d, x0, y0 + (1 - ease_out(seg(t, 7.70, 0.5))) * 40, w, h,
         "kVA", SCRIPT["kva_sub"], SCRIPT["kva_body"], a1)
    a2 = inout(t, 8.30, 13.50, 0.26)
    card(d, x0 + w + gap, y0 + (1 - ease_out(seg(t, 8.30, 0.5))) * 40, w, h,
         "kW", SCRIPT["kw_sub"], SCRIPT["kw_body"], a2, accent=True)
    a3 = inout(t, 10.40, 13.50, 0.26)
    text(d, (W / 2, 1330), SCRIPT["defs_note"],
         fit(SCRIPT["defs_note"], 50, SAFE_W, "Medium", display=False), INK, a3)
    return put(im, l)

def scene_formula(t, im):
    l, d = layer()
    kicker(d, SCRIPT["formula_kicker"], inout(t, 13.35, 18.70, 0.28), 700)
    a1 = inout(t, 13.50, 18.70, 0.28)
    if a1:
        p = ease_out_x(seg(t, 13.50, 0.6))
        text(d, (W / 2, 900), SCRIPT["formula"],
             fit(SCRIPT["formula"], 124 * (0.88 + 0.12 * p)), INK, a1)
    a2 = inout(t, 14.90, 18.70, 0.26)
    if a2:
        bw, bh = 700, 150
        x, y = (W - bw) / 2, 1030
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=30,
                            outline=rgba(ACCENT, 0.55 * a2), width=3)
        text(d, (W / 2, y + bh / 2), SCRIPT["cosphi"],
             fit(SCRIPT["cosphi"], 64, bw - 80, "Bold"), ACCENT, a2)
    a3 = inout(t, 16.10, 18.70, 0.26)
    text(d, (W / 2, 1300), SCRIPT["formula_note"],
         fit(SCRIPT["formula_note"], 42, SAFE_W, "Medium", display=False), MUTED, a3)
    return put(im, l)

def bar(d, x, y, w, h, frac, color, label, value, a, filled=True):
    if a <= 0.004:
        return
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=rgba(INK, 0.075 * a))
    fw = max(h, w * clamp(frac))
    if filled:
        d.rounded_rectangle([x, y, x + fw, y + h], radius=h // 2, fill=rgba(color, a))
    else:
        d.rounded_rectangle([x, y, x + fw, y + h], radius=h // 2,
                            outline=rgba(color, a), width=4)
    text(d, (x, y - 50), label, font(38, "Bold"), MUTED, a, anchor="lm")
    text(d, (x + w, y - 50), value, font(46, "Bold"), color, a, anchor="rm")

def scene_bars(t, im):
    l, d = layer()
    kicker(d, SCRIPT["bars_kicker"], inout(t, 18.55, 25.30, 0.28), 640)
    x, w, h = SAFE + 40, SAFE_W - 80, 56
    bar(d, x, 840, w, h, ease_in_out(seg(t, 18.70, 0.9)), INK,
        SCRIPT["bar_s"], "100 kVA", inout(t, 18.70, 25.30, 0.26), filled=False)
    bar(d, x, 1020, w, h, 0.80 * ease_in_out(seg(t, 19.70, 0.9)), ACCENT,
        SCRIPT["bar_p"], "80 kW", inout(t, 19.70, 25.30, 0.26))
    bar(d, x, 1200, w, h, 0.60 * ease_in_out(seg(t, 20.50, 0.9)), MUTED,
        SCRIPT["bar_q"], "60 kvar", inout(t, 20.50, 25.30, 0.26))
    a4 = inout(t, 22.10, 25.30, 0.26)
    text(d, (W / 2, 1390), SCRIPT["bars_note"],
         fit(SCRIPT["bars_note"], 46, SAFE_W, "Medium", display=False), INK, a4)
    return put(im, l)

def scene_punch(t, im):
    l, d = layer()
    a1 = inout(t, 25.15, 30.10, 0.28)
    if a1:
        p = ease_out(seg(t, 25.15, 0.5))
        text(d, (W / 2, 800 + (1 - p) * 30), SCRIPT["punch_q"],
             fit(SCRIPT["punch_q"], 86), MUTED, a1)
    a2 = inout(t, 26.10, 30.10, 0.24)
    if a2:
        p = ease_out_x(seg(t, 26.10, 0.55))
        text(d, (W / 2, 1010), SCRIPT["punch_a"],
             fit(SCRIPT["punch_a"], 120 * (0.9 + 0.1 * p)), INK, a2)
    a3 = inout(t, 27.20, 30.10, 0.24)
    if a3:
        bw, bh = 740, 140
        x, y = (W - bw) / 2, 1230
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=28, fill=rgba(ACCENT, a3))
        text(d, (W / 2, y + bh / 2), SCRIPT["punch_math"],
             fit(SCRIPT["punch_math"], 60, bw - 70, "Bold"), BG, a3)
    return put(im, l)

def scene_outro(t, im):
    l, d = layer()
    a1 = inout(t, 29.95, 33.00, 0.30)
    if a1:
        p = ease_out(seg(t, 29.95, 0.6))
        text(d, (W / 2, 920 + (1 - p) * 26), SCRIPT["cta"],
             fit(SCRIPT["cta"], 88), INK, a1)
    a2 = inout(t, 30.80, 33.00, 0.28)
    if a2:
        f = fit(SCRIPT["brand"], 104)
        wd, _ = measure(f, SCRIPT["brand"])
        text(d, (W / 2, 1140), SCRIPT["brand"], f, INK, a2)
        d.line([(W / 2 - wd / 2 - 12, 1215), (W / 2 + wd / 2 + 12, 1215)],
               fill=rgba(ACCENT, a2), width=6)
    return put(im, l)

SCENES = [(0.00, 4.35, scene_hook), (4.10, 7.75, scene_cost),
          (7.50, 13.55, scene_defs), (13.30, 18.75, scene_formula),
          (18.50, 25.35, scene_bars), (25.10, 30.15, scene_punch),
          (29.90, 33.00, scene_outro)]
TOTAL = 33.0

# ---------------------------------------------------------------- Render
def render():
    os.makedirs(FRAMES, exist_ok=True)
    for f in os.listdir(FRAMES):
        os.remove(os.path.join(FRAMES, f))
    build_static()
    n = int(TOTAL * FPS)
    for i in range(n):
        t = i / FPS
        im = background(t, TOTAL)
        for start, end, fn in SCENES:
            if start <= t <= end:
                im = fn(t, im)
        im.convert("RGB").save(os.path.join(FRAMES, "f%05d.png" % i))
        if i % 150 == 0:
            print("  frame %d/%d" % (i, n), flush=True)
    return n

def encode():
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS),
                    "-i", os.path.join(FRAMES, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT],
                   check=True, capture_output=True)

if __name__ == "__main__":
    n = render()
    encode()
    print("OK ->", OUT, os.path.getsize(OUT), "bytes,", n, "frames")
