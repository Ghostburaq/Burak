"""
Asset generator for the AVIA VOLT pitch deck.

Produces 100% on-brand, deterministic imagery so the deck never depends on
external image hosts (which guarantees "Bilder die immer passen, ohne Bugs"):

  * White-recoloured icon variants (placed inside coloured badges in the deck)
  * Premium dark hero / section backgrounds with a subtle energy + charging
    motif (vertical gradient, diagonal current lines, dotted grid, red glow)
  * A soft light "paper" gradient for the content slides
  * A cleanly framed portrait crop

Run:  python3 src/make_assets.py
"""
from __future__ import annotations

import math
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_SRC = os.path.join(ROOT, "assets", "icons")
ICON_W = os.path.join(ROOT, "assets", "icons_w")
BG = os.path.join(ROOT, "assets", "bg")
os.makedirs(ICON_W, exist_ok=True)
os.makedirs(BG, exist_ok=True)

# ---- Brand palette -------------------------------------------------------
INK = (27, 36, 48)        # 1B2430  main dark
INK_DEEP = (20, 26, 36)   # 141A24  deepest
RED = (226, 0, 26)        # E2001A  AVIA red

# Semantic name -> source icon file (all are solid-colour on transparent).
ICONS = {
    "charger":  "image-2-1.png",
    "handshake": "image-2-2.png",
    "battery":  "image-2-3.png",
    "bolt":     "image-2-4.png",
    "chip":     "image-3-1.png",
    "check":    "image-4-1.png",
    "wave":     "image-6-1.png",
    "truck":    "image-8-1.png",
    "retail":   "image-8-2.png",
    "industry": "image-8-3.png",
    "gov":      "image-8-4.png",
    "building": "image-8-5.png",
    "phone":    "image-10-2.png",
    "mail":     "image-10-3.png",
    "pin":      "image-10-4.png",
}


def recolour(src: str, dst: str, rgb=(255, 255, 255)) -> None:
    """Replace the RGB of a solid icon while preserving its alpha mask."""
    im = Image.open(src).convert("RGBA")
    r, g, b, a = im.split()
    solid = Image.new("RGBA", im.size, rgb + (0,))
    solid.putalpha(a)
    solid.save(dst)


def make_icons() -> None:
    for name, fn in ICONS.items():
        recolour(os.path.join(ICON_SRC, fn), os.path.join(ICON_W, f"{name}.png"))
    print(f"icons: wrote {len(ICONS)} white variants -> {ICON_W}")


# ---- Background helpers --------------------------------------------------
W, H = 2560, 1444  # ~16:9 matching the deck aspect (1.773)


def _vgrad(w, h, top, bot):
    base = Image.new("RGB", (w, h), top)
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        px_row = (
            int(top[0] + (bot[0] - top[0]) * t),
            int(top[1] + (bot[1] - top[1]) * t),
            int(top[2] + (bot[2] - top[2]) * t),
        )
        for x in range(w):
            px[x, y] = px_row
    return base


def _radial_glow(w, h, cx, cy, radius, rgb, max_alpha):
    layer = Image.new("RGBA", (w, h), rgb + (0,))
    d = ImageDraw.Draw(layer)
    steps = 60
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(max_alpha * (1 - i / steps) ** 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb + (a,))
    return layer.filter(ImageFilter.GaussianBlur(40))


def _dotted_grid(w, h, step=64, rgb=(255, 255, 255), alpha=10):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(step, h, step):
        for x in range(step, w, step):
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=rgb + (alpha,))
    return layer


def _current_lines(w, h, rgb, alpha, n=7):
    """Subtle diagonal 'current' streaks."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(n):
        off = int(w * (i / n)) - w // 4
        d.line([(off, h), (off + w // 2, 0)], fill=rgb + (alpha,), width=2)
    return layer.filter(ImageFilter.GaussianBlur(1))


def _energy_wave(w, h, cx, cy, scale, rgb, alpha, width=6):
    """A faint power-quality sine waveform as the hero's signature motif."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = []
    span = int(1.4 * scale)
    for x in range(-span, span):
        y = cy + math.sin(x / scale * 3.14159 * 2) * scale * 0.32
        pts.append((cx + x, y))
    d.line(pts, fill=rgb + (alpha,), width=width, joint="curve")
    return layer.filter(ImageFilter.GaussianBlur(2))


def make_hero(path, *, glow=True, wave=True):
    img = _vgrad(W, H, INK_DEEP, INK).convert("RGBA")
    img.alpha_composite(_current_lines(W, H, (255, 255, 255), 6))
    img.alpha_composite(_dotted_grid(W, H))
    if wave:
        img.alpha_composite(_energy_wave(W, H, int(W * 0.74), int(H * 0.52),
                                         190, RED, 60, width=7))
        img.alpha_composite(_energy_wave(W, H, int(W * 0.74), int(H * 0.52),
                                         190, (255, 255, 255), 22, width=3))
    if glow:
        img.alpha_composite(_radial_glow(W, H, int(W * 0.08), int(H * 0.96),
                                         int(W * 0.42), RED, 70))
        img.alpha_composite(_radial_glow(W, H, int(W * 1.02), int(H * 0.04),
                                         int(W * 0.30), (90, 120, 160), 26))
    img.convert("RGB").save(path)
    print("bg:", os.path.basename(path))


def make_section(path):
    """Quieter dark background for the stats break slide."""
    img = _vgrad(W, H, INK_DEEP, INK).convert("RGBA")
    img.alpha_composite(_dotted_grid(W, H, step=72, alpha=8))
    img.alpha_composite(_radial_glow(W, H, int(W * 0.5), int(H * 1.05),
                                     int(W * 0.55), RED, 34))
    img.convert("RGB").save(path)
    print("bg:", os.path.basename(path))


def make_paper(path):
    """Very soft light gradient for content slides + faint corner tint."""
    img = _vgrad(W, H, (247, 249, 252), (237, 241, 246)).convert("RGBA")
    img.alpha_composite(_radial_glow(W, H, int(W * 1.04), int(H * -0.05),
                                     int(W * 0.34), RED, 14))
    img.convert("RGB").save(path)
    print("bg:", os.path.basename(path))


def make_portrait(path):
    """Clean square crop of the portrait (source already has rounded mask)."""
    im = Image.open(os.path.join(ROOT, "assets", "portrait.png")).convert("RGBA")
    im.save(path)
    print("portrait ready")


if __name__ == "__main__":
    make_icons()
    make_hero(os.path.join(BG, "hero.png"))
    make_section(os.path.join(BG, "section.png"))
    make_paper(os.path.join(BG, "paper.png"))
    make_portrait(os.path.join(ROOT, "assets", "portrait_clean.png"))
    print("all assets generated.")
