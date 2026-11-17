# -*- coding: utf-8 -*-
"""Setzt nummerierte Marken neben die Bedienelemente der Unity-Screenshots."""
import sys
from PIL import Image, ImageDraw, ImageFont
W = sys.argv[1]
RED = (224, 0, 54)

def mark(im, pts, rel_r):
    d = ImageDraw.Draw(im, 'RGBA')
    r = int(im.width * rel_r)
    f = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', int(r*1.25))
    for n, (fx, fy) in enumerate(pts, 1):
        x, y = fx*im.width, fy*im.height
        d.ellipse([x-r-3, y-r-3, x+r+3, y+r+3], fill=(255,255,255,245))
        d.ellipse([x-r, y-r, x+r, y+r], fill=RED+(255,))
        d.text((x, y+1), str(n), font=f, fill=(255,255,255,255), anchor='mm')
    return im

jobs = [
 ('screen.png', 'screen_a.png', 0.018, [
   (0.225, 0.062), (0.805, 0.045), (0.944, 0.045), (0.468, 0.176),
   (0.688, 0.233), (0.688, 0.520), (0.962, 0.172), (0.048, 0.745), (0.948, 0.845)]),
 ('bottom.png', 'bottom_a.png', 0.0135, [
   (0.100, 0.125), (0.072, 0.605), (0.252, 0.165),
   (0.233, 0.690), (0.624, 0.235), (0.905, 0.280)]),
]
for src, dst, rr, pts in jobs:
    im = Image.open(W+'/'+src).convert('RGB')
    mark(im, pts, rr).save(W+'/'+dst, quality=95)
    print('%-16s %s  %d Marken' % (dst, im.size, len(pts)))
