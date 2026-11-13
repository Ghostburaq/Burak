"""Comic-/Manga-Seite aus Bildern und Sprechblasen bauen.

Nutzung: python3 comic.py seite.json ausgabe.png
seite.json:
{
  "titel": "Mia und der Herbst",
  "manga": false,               # true = schwarz-weiss mit Rasterpunkten
  "panels": [
    {"bild": "panel1.png", "text": "Wo bin ich?"},
    {"bild": "panel2.png", "text": "Im goldenen Wald.", "unten": true}
  ]
}
Layout: 1 Panel = ganze Seite, 2 = untereinander, 3-4 = 2x2, 5-6 = 3x2.
"""

import json
import math
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H, RAND, ABST = 1600, 2260, 60, 28
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def manga_look(img):
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g, cutoff=2)
    # Rasterpunkte für Mitteltöne
    return g.convert("1", dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")


def blase(d, box, text, unten=False):
    x0, y0, _x1, y1 = box
    f = font(44)
    zeilen = textwrap.wrap(text, 22)
    lh = 54
    tw_max = max(d.textlength(z, font=f) for z in zeilen)
    bw = tw_max / 0.74  # Text muss ins Innere der Ellipse passen
    bh = (lh * len(zeilen)) / 0.68
    bx = x0 + 30
    by = y1 - bh - 70 if unten else y0 + 30
    # Schwanz der Sprechblase
    sx = bx + bw * 0.3
    sy = by if unten else by + bh
    tip = (sx + 40, sy - 70) if unten else (sx + 40, sy + 70)
    d.polygon([(sx, sy), (sx + 50, sy), tip], fill="white", outline="black")
    d.ellipse([bx, by, bx + bw, by + bh], fill="white", outline="black", width=5)
    d.line([(sx + 4, sy), (sx + 46, sy)], fill="white", width=8)
    for i, z in enumerate(zeilen):
        tw = d.textlength(z, font=f)
        d.text(
            (bx + (bw - tw) / 2, by + (bh - lh * len(zeilen)) / 2 + i * lh),
            z,
            font=f,
            fill="black",
        )


def main():
    with open(sys.argv[1], encoding="utf-8") as fh:
        cfg = json.load(fh)
    panels = cfg["panels"]
    n = len(panels)
    cols = 1 if n <= 2 else 2
    rows = math.ceil(n / cols)
    seite = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(seite)
    top = RAND
    if cfg.get("titel"):
        f = font(78)
        tw = d.textlength(cfg["titel"], font=f)
        d.text(((W - tw) / 2, RAND - 10), cfg["titel"], font=f, fill="black")
        top += 110
    pw = (W - 2 * RAND - (cols - 1) * ABST) / cols
    ph = (H - top - RAND - (rows - 1) * ABST) / rows
    for i, p in enumerate(panels):
        r, c = divmod(i, cols)
        if i == n - 1 and n % cols:  # letztes Panel über volle Breite
            w = W - 2 * RAND
        else:
            w = pw
        x0 = RAND + c * (pw + ABST)
        y0 = top + r * (ph + ABST)
        box = (int(x0), int(y0), int(x0 + w), int(y0 + ph))
        img = ImageOps.fit(
            Image.open(p["bild"]).convert("RGB"), (box[2] - box[0], box[3] - box[1])
        )
        if cfg.get("manga"):
            img = manga_look(img)
        seite.paste(img, box[:2])
        d.rectangle(box, outline="black", width=8)
        if p.get("text"):
            blase(d, box, p["text"], p.get("unten", False))
    seite.save(sys.argv[2])
    print("Fertig:", sys.argv[2])


if __name__ == "__main__":
    main()
