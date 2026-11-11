"""Bild aus Text erzeugen (SD-Turbo, läuft auf CPU, 512x512, ca. 10-30 s).

Nutzung: python3 bild.py "prompt" ausgabe.png [schritte=2] [seed=0]
Stil-Beispiele: "manga style, black and white ink, screentone, ..."
                "comic book style, bold outlines, flat colors, ..."
                "3d render, pixar style, soft lighting, ..."
"""

import sys
import time

import torch
from diffusers import AutoPipelineForText2Image

prompt, out = sys.argv[1], sys.argv[2]
steps = int(sys.argv[3]) if len(sys.argv) > 3 else 2
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0

torch.set_num_threads(4)
t = time.time()
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sd-turbo", torch_dtype=torch.float32)
img = pipe(
    prompt=prompt,
    num_inference_steps=steps,
    guidance_scale=0.0,
    generator=torch.Generator().manual_seed(seed),
).images[0]
img.save(out)
print(f"Fertig: {out} ({time.time() - t:.0f} s)")
