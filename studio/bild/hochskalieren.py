"""Bild 4-fach hochskalieren (Real-ESRGAN via spandrel, CPU, in Kacheln).

Nutzung: python3 hochskalieren.py eingang.png ausgang.png [foto|anime]
"""

import sys

import numpy as np
import torch
from PIL import Image
from spandrel import ModelLoader

M = "/root/.local/share/modelle/"
src, dst = sys.argv[1], sys.argv[2]
art = sys.argv[3] if len(sys.argv) > 3 else "foto"
datei = "RealESRGAN_x4plus_anime_6B.pth" if art == "anime" else "RealESRGAN_x4plus.pth"

torch.set_num_threads(4)
model = ModelLoader().load_from_file(M + datei).eval()
img = np.asarray(Image.open(src).convert("RGB"), dtype=np.float32) / 255
x = torch.from_numpy(img).permute(2, 0, 1)[None]

KACHEL, RAND = 256, 16
_, _, h, w = x.shape
out = torch.zeros(1, 3, h * 4, w * 4)
with torch.no_grad():
    for y0 in range(0, h, KACHEL):
        for x0 in range(0, w, KACHEL):
            ya, xa = max(y0 - RAND, 0), max(x0 - RAND, 0)
            yb, xb = min(y0 + KACHEL + RAND, h), min(x0 + KACHEL + RAND, w)
            r = model(x[:, :, ya:yb, xa:xb])
            ye, xe = min(y0 + KACHEL, h), min(x0 + KACHEL, w)
            out[:, :, y0 * 4 : ye * 4, x0 * 4 : xe * 4] = r[
                :, :, (y0 - ya) * 4 : (ye - ya) * 4, (x0 - xa) * 4 : (xe - xa) * 4
            ]
res = (out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)
Image.fromarray(res).save(dst)
print("Fertig:", dst, f"{w}x{h} -> {w * 4}x{h * 4}")
