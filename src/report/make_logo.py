#!/usr/bin/env python3
"""Erzeugt die kabuu-Logo-Assets für Deckblatt, Kopfzeile und Rückseite.

Das Logo wird hier aus Geometrie und Schrift aufgebaut: Sechseck-Signet mit
Impulsfolge, Blitz und Schwingung, darunter die Wortmarke. So bleibt der
Bericht ohne Bilddatei reproduzierbar.

Liegt die Originaldatei unter ``assets/report/logo/kabuu_logo_original.png``,
wird sie stattdessen verwendet und lediglich in die benötigten Varianten
geschnitten. Damit lässt sich das gezeichnete Signet jederzeit durch das
echte Markenasset ersetzen, ohne den Code zu ändern.

    python3 src/report/make_logo.py
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LOGO_DIR = ROOT / "assets" / "report" / "logo"
ORIGINAL = LOGO_DIR / "kabuu_logo_original.png"

INK = (26, 30, 35)
SUB = (58, 64, 72)
STEEL_LIGHT = (205, 211, 219)
STEEL_DARK = (74, 82, 93)

FONTS = {
    "light": "/usr/share/fonts/truetype/roboto/hinted/Roboto-Light.ttf",
    "regular": "/usr/share/fonts/truetype/roboto/hinted/Roboto-Regular.ttf",
    "medium": "/usr/share/fonts/truetype/roboto/hinted/Roboto-Medium.ttf",
    "bold": "/usr/share/fonts/truetype/roboto/hinted/Roboto-Bold.ttf",
}
SS = 4  # Supersampling-Faktor; alles wird gross gezeichnet und heruntergerechnet


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[weight], size)


def _hexagon(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    """Sechseck mit Spitzen oben und unten."""
    return [
        (cx + r * math.sin(math.radians(60 * i)), cy - r * math.cos(math.radians(60 * i)))
        for i in range(6)
    ]


def _steel_gradient(size: tuple[int, int]) -> Image.Image:
    """Diagonaler Metallverlauf, der dem Signet seine Tiefe gibt."""
    w, h = size
    grad = Image.new("RGB", (w, h))
    px = grad.load()
    for y in range(h):
        for x in range(0, w, 4):
            t = (x / max(w - 1, 1) * 0.45) + (y / max(h - 1, 1) * 0.55)
            # zwei Glanzkanten, damit der Verlauf metallisch statt flach wirkt
            t = min(1.0, max(0.0, t + 0.18 * math.sin(t * math.pi * 2.0)))
            col = tuple(
                round(STEEL_LIGHT[i] + (STEEL_DARK[i] - STEEL_LIGHT[i]) * t) for i in range(3)
            )
            for dx in range(4):
                if x + dx < w:
                    px[x + dx, y] = col
    return grad.filter(ImageFilter.GaussianBlur(2))


# Das Signet in normierten Koordinaten (0..1 über die Signetbreite). Die
# Geometrie steht hier gesammelt, damit sich Proportionen anpassen lassen,
# ohne den Zeichencode anzufassen.
PULSE = [(0.150, 0.470), (0.290, 0.470), (0.290, 0.330), (0.420, 0.330), (0.420, 0.470)]
PULSE_BASE = [(0.150, 0.605), (0.330, 0.605)]
BOLT = [
    (0.688, 0.108),  # obere Spitze, ragt bewusst über das Sechseck hinaus
    (0.345, 0.520),
    (0.505, 0.520),
    (0.312, 0.892),  # untere Spitze
    (0.628, 0.462),
    (0.492, 0.462),
]


def _wave(steps: int = 60) -> list[tuple[float, float]]:
    """Schwingungsbogen unten rechts, als weiches Tal gezeichnet."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        pts.append((0.578 + 0.292 * t, 0.505 + 0.272 * math.sin(math.pi * t)))
    return pts


def draw_mark(size: int = 320, mono: tuple[int, int, int] | None = None) -> Image.Image:
    """Das Sechseck-Signet: Impulsfolge, Blitz und Schwingung."""
    s = size * SS
    mask = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(mask)

    def pt(p: tuple[float, float]) -> tuple[float, float]:
        return (p[0] * s, p[1] * s)

    cx = cy = s / 2
    d.polygon(_hexagon(cx, cy, s * 0.48), outline=255, width=round(s * 0.052))

    lw = round(s * 0.042)
    d.line([pt(p) for p in PULSE], fill=255, width=lw, joint="curve")
    d.line([pt(p) for p in PULSE_BASE], fill=255, width=lw)
    d.line([pt(p) for p in _wave()], fill=255, width=lw, joint="curve")
    d.polygon([pt(p) for p in BOLT], fill=255)

    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    fill = Image.new("RGB", (size, size), mono) if mono else _steel_gradient((size, size))
    out.paste(fill, (0, 0), mask)
    return out


def _text_image(
    parts: list[tuple[str, str, int, tuple[int, int, int], int]],
    gap: int,
    align: str = "center",
) -> Image.Image:
    """Setzt Textzeilen (Text, Gewicht, Grösse, Farbe, Sperrung) untereinander."""
    rendered = []
    for text, weight, size, color, tracking in parts:
        f = font(weight, size * SS)
        widths = [f.getlength(ch) for ch in text]
        w = round(sum(widths) + tracking * SS * (len(text) - 1)) + 4
        asc, desc = f.getmetrics()
        h = asc + desc
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        x = 2.0
        for ch, cw in zip(text, widths):
            d.text((x, 0), ch, font=f, fill=color + (255,))
            x += cw + tracking * SS
        rendered.append(img)

    width = max(img.width for img in rendered)
    height = sum(img.height for img in rendered) + gap * SS * (len(rendered) - 1)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    y = 0
    for img in rendered:
        x = 0 if align == "left" else (width - img.width) // 2
        canvas.alpha_composite(img, (x, y))
        y += img.height + gap * SS
    return canvas.resize(
        (max(1, canvas.width // SS), max(1, canvas.height // SS)), Image.LANCZOS
    )


def _trim(img: Image.Image, pad: int = 0) -> Image.Image:
    box = img.getbbox()
    if not box:
        return img
    img = img.crop(box)
    if pad:
        out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
        out.alpha_composite(img, (pad, pad))
        return out
    return img


def _stack(top: Image.Image, bottom: Image.Image, gap: int) -> Image.Image:
    width = max(top.width, bottom.width)
    out = Image.new("RGBA", (width, top.height + gap + bottom.height), (0, 0, 0, 0))
    out.alpha_composite(top, ((width - top.width) // 2, 0))
    out.alpha_composite(bottom, ((width - bottom.width) // 2, top.height + gap))
    return out


def build_lockup(ink=INK, sub=SUB, mono=None) -> Image.Image:
    """Vollständige Bildmarke: Signet über Wortmarke, wie auf dem Briefpapier."""
    mark = draw_mark(300, mono=mono)
    words = _text_image(
        [
            ("kabuu", "light", 116, ink, -2),
            ("Netzqualität & EMV Messungen", "regular", 34, sub, 0),
            ("ENGINEERING", "bold", 30, ink, 6),
        ],
        gap=10,
    )
    return _trim(_stack(_trim(mark), _trim(words), 26))


def build_wordmark(ink=INK, sub=SUB) -> Image.Image:
    """Schmale Variante für die Kopfzeile: Wortmarke plus Claim, einzeilig gesetzt."""
    return _trim(
        _text_image(
            [("kabuu", "light", 84, ink, -1), ("NETZQUALITÄT & EMV MESSUNGEN", "medium", 19, sub, 4)],
            gap=4,
        )
    )


def main() -> None:
    LOGO_DIR.mkdir(parents=True, exist_ok=True)

    if ORIGINAL.exists():
        print(f"Originaldatei gefunden: {ORIGINAL.relative_to(ROOT)} — wird verwendet.")
        src = _trim(Image.open(ORIGINAL).convert("RGBA"))
        src.save(LOGO_DIR / "logo_lockup.png")
        src.save(LOGO_DIR / "logo_wordmark.png")
    else:
        build_lockup().save(LOGO_DIR / "logo_lockup.png")
        build_wordmark().save(LOGO_DIR / "logo_wordmark.png")

    _trim(draw_mark(300)).save(LOGO_DIR / "logo_mark.png")
    _trim(draw_mark(300, mono=(255, 255, 255))).save(LOGO_DIR / "logo_mark_white.png")
    _trim(draw_mark(300, mono=(214, 219, 225))).save(LOGO_DIR / "logo_mark_pale.png")
    build_lockup(ink=(255, 255, 255), sub=(214, 219, 225), mono=(255, 255, 255)).save(
        LOGO_DIR / "logo_lockup_white.png"
    )

    for path in sorted(LOGO_DIR.glob("*.png")):
        with Image.open(path) as im:
            print(f"  {path.name:26s} {im.size[0]:4d} x {im.size[1]:4d}")


if __name__ == "__main__":
    main()
