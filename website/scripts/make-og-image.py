#!/usr/bin/env python3
"""Erzeugt public/og-image.png (1200x630) fuer Social-Previews.

Die Bildmarke wird aus derselben Geometrie gezeichnet wie public/logo/mark.svg
(viewBox 200x210), damit PNG und SVG deckungsgleich bleiben. Wird das SVG
geaendert, hier die Koordinaten mitziehen.

Neu erzeugen:  python3 scripts/make-og-image.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
SS = 3  # Supersampling fuer weiche Kanten

STAHL     = (149, 154, 175)
ANTHRAZIT = (18, 21, 26)
BOLT      = (42, 47, 58)
INK_700   = (58, 63, 75)
INK_500   = (96, 103, 117)
INK_200   = (217, 219, 225)
VIOLETT   = (51, 23, 233)
BG        = (247, 248, 250)

FONTS = "/usr/share/fonts/truetype/liberation/"

# --- Abbildung SVG-Koordinaten (viewBox 200x210) auf die PNG-Flaeche ---
SVG_CX, SVG_CY, SVG_R = 100.0, 105.0, 91.0   # Sechseck im SVG
CX, CY, R = 252.0, 315.0, 156.0              # Sechseck im PNG
SCALE = R / SVG_R


def tp(x: float, y: float) -> tuple[float, float]:
    """SVG-Punkt -> PNG-Punkt (bereits supersampled)."""
    return ((CX + (x - SVG_CX) * SCALE) * SS,
            (CY + (y - SVG_CY) * SCALE) * SS)


def tw(w: float) -> int:
    """SVG-Strichbreite -> PNG-Strichbreite (supersampled)."""
    return max(1, round(w * SCALE * SS))


def bezier(p0, p1, p2, p3, n: int = 24) -> list[tuple[float, float]]:
    """Kubische Bezierkurve abtasten."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((
            u**3 * p0[0] + 3 * u*u*t * p1[0] + 3 * u*t*t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u*u*t * p1[1] + 3 * u*t*t * p2[1] + t**3 * p3[1],
        ))
    return pts


def signalkurve() -> list[tuple[float, float]]:
    """Entspricht dem Pfad in mark.svg."""
    pts: list[tuple[float, float]] = [(30, 106), (52, 106)]
    for seg in [
        ((52, 106), (57, 106), (58, 93),  (63, 93)),
        ((63, 93),  (68, 93),  (69, 106), (74, 106)),
    ]:
        pts += bezier(*seg)[1:]
    pts.append((80, 106))
    for seg in [
        ((80, 106),  (87, 106),  (88, 58),   (97, 58)),
        ((97, 58),   (106, 58),  (107, 112), (113, 126)),
        ((113, 126), (119, 140), (123, 152), (130, 152)),
        ((130, 152), (136, 152), (138, 122), (144, 122)),
        ((144, 122), (150, 122), (152, 146), (158, 146)),
    ]:
        pts += bezier(*seg)[1:]
    return pts


def hexagon() -> list[tuple[float, float]]:
    return [(100, 14), (176, 58), (176, 152), (100, 196), (24, 152), (24, 58)]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS + name, size)


def main() -> None:
    img = Image.new("RGB", (W * SS, H * SS), BG)
    d = ImageDraw.Draw(img)
    s = lambda v: v * SS  # noqa: E731

    # Sechseck-Rahmen
    d.line([tp(*p) for p in hexagon()] + [tp(*hexagon()[0])],
           fill=STAHL, width=tw(11), joint="curve")

    # Signalkurve
    d.line([tp(*p) for p in signalkurve()],
           fill=ANTHRAZIT, width=tw(7.5), joint="curve")

    # Blitz-Slash
    d.polygon([tp(*p) for p in
               [(157, 40), (116, 116), (131, 121), (84, 184), (103, 118), (90, 113)]],
              fill=BOLT)

    # Trennlinie
    d.line([(s(470), s(178)), (s(470), s(452))], fill=INK_200, width=tw(1.4))

    # Wortmarke
    x0 = 532
    f_wort  = font("LiberationSans-Bold.ttf",    round(s(94)))
    f_claim = font("LiberationSans-Regular.ttf", round(s(30)))
    f_sub   = font("LiberationSans-Bold.ttf",    round(s(21)))
    f_tag   = font("LiberationSans-Regular.ttf", round(s(26)))

    d.text((s(x0), s(200)), "kabuu", font=f_wort, fill=ANTHRAZIT)
    d.text((s(x0), s(306)), "Netzqualität & EMV Messungen", font=f_claim, fill=INK_700)

    x = s(x0)
    for ch in "ENGINEERING":
        d.text((x, s(352)), ch, font=f_sub, fill=INK_500)
        x += d.textlength(ch, font=f_sub) + s(5.5)

    d.line([(s(x0), s(410)), (s(x0 + 62), s(410))], fill=VIOLETT, width=tw(2.4))
    d.text((s(x0), s(430)), "Messen, bevor investiert wird.", font=f_tag, fill=ANTHRAZIT)

    out = Path(__file__).resolve().parent.parent / "public" / "og-image.png"
    img.resize((W, H), Image.LANCZOS).save(out, "PNG", optimize=True)
    print(f"{out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
