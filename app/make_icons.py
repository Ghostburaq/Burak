#!/usr/bin/env python3
"""Erzeugt die App-Icons für Lernfuchs (PWA).
Generiert ein einfaches, markentaugliches Fuchs-/Sprach-Icon auf grünem Grund.
Aufruf:  python3 make_icons.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT, exist_ok=True)

GREEN = (43, 182, 115)
GREEN_D = (31, 148, 96)


def _font(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make(size, maskable=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Hintergrund: abgerundetes Quadrat (maskable -> Vollfläche mit Sicherheitsrand)
    pad = 0 if maskable else int(size * 0.06)
    radius = int(size * (0.30 if not maskable else 0.0))
    # vertikaler Verlauf
    for y in range(size):
        t = y / size
        r = int(GREEN[0] + (GREEN_D[0] - GREEN[0]) * t)
        g = int(GREEN[1] + (GREEN_D[1] - GREEN[1]) * t)
        b = int(GREEN[2] + (GREEN_D[2] - GREEN[2]) * t)
        d.line([(0, y), (size, y)], fill=(r, g, b, 255))
    if not maskable:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [pad, pad, size - pad, size - pad], radius=radius, fill=255)
        bg = img
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        img.paste(bg, (0, 0), mask)
        d = ImageDraw.Draw(img)
    # Fuchs-Emoji als Zeichen (Fallback: Buchstabe). Emoji-Fonts fehlen oft,
    # daher zeichnen wir ein simples Fuchsgesicht aus Formen.
    cx, cy = size / 2, size * 0.54
    s = size * 0.30
    white = (255, 255, 255, 255)
    dark = (29, 42, 39, 255)
    orange = (255, 255, 255, 255)
    # Ohren
    d.polygon([(cx - s, cy - s * 0.5), (cx - s * 0.45, cy - s),
               (cx - s * 0.2, cy - s * 0.35)], fill=white)
    d.polygon([(cx + s, cy - s * 0.5), (cx + s * 0.45, cy - s),
               (cx + s * 0.2, cy - s * 0.35)], fill=white)
    # Kopf
    d.ellipse([cx - s, cy - s * 0.6, cx + s, cy + s], fill=white)
    # Schnauze
    d.polygon([(cx - s * 0.45, cy + s * 0.1), (cx + s * 0.45, cy + s * 0.1),
               (cx, cy + s)], fill=(244, 247, 245, 255))
    # Augen
    er = s * 0.12
    for ex in (cx - s * 0.4, cx + s * 0.4):
        d.ellipse([ex - er, cy - er, ex + er, cy + er], fill=dark)
    # Nase
    nr = s * 0.13
    d.ellipse([cx - nr, cy + s * 0.55 - nr, cx + nr, cy + s * 0.55 + nr], fill=dark)
    img.save(os.path.join(OUT, "icon-maskable-512.png" if maskable else f"icon-{size}.png"))
    return img


make(192)
make(512)
make(512, maskable=True)
print("Icons erzeugt in", OUT)
