"""
Faithful preview renderer for verification.

Reads the ACTUAL saved .pptx (shape geometry, fills, lines, pictures and text
runs) and rasterises each slide with Pillow. Because positions come from the
file — not from the build script — this reliably surfaces real layout bugs
(overflow, overlap, off-slide elements). Fonts use Liberation Sans, the same
metric substitute an Office renderer applies to Trebuchet/Calibri.

Run:  python3 src/render_preview.py
Out:  /tmp/preview/slideNN.png  + contact sheet
"""
from __future__ import annotations
import os
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PPTX = os.path.join(ROOT, "Pitch_Burak_AVIA_VOLT.pptx")
OUT = "/tmp/preview"
os.makedirs(OUT, exist_ok=True)

FREG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FBLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
_cache = {}


def font(sz, bold):
    k = (int(sz), bool(bold))
    if k not in _cache:
        _cache[k] = ImageFont.truetype(FBLD if bold else FREG, max(6, int(sz)))
    return _cache[k]


prs = Presentation(PPTX)
EW, EH = prs.slide_width, prs.slide_height
OW = int(os.environ.get("PREVIEW_W", "1422"))
SCALE = OW / EW
OH = int(EH * SCALE)
PT2PX = 12700 * SCALE  # pt -> device px


def sx(e): return int(e * SCALE)


def rgb(color_obj):
    try:
        c = color_obj.rgb
        return (c[0], c[1], c[2])
    except Exception:
        return None


def wrap_runs(draw, runs, max_w):
    """runs: list of (text,fnt,fill). Returns list of lines, each a list of
    (word, fnt, fill, width)."""
    tokens = []
    for txt, fnt, fill in runs:
        # keep explicit newlines
        parts = txt.split("\n")
        for pi, part in enumerate(parts):
            if pi > 0:
                tokens.append(("\n", fnt, fill))
            for w in part.split(" "):
                tokens.append((w, fnt, fill))
                tokens.append((" ", fnt, fill))
    lines, cur, cw = [], [], 0
    space_pending = None
    for tok, fnt, fill in tokens:
        if tok == "\n":
            lines.append(cur); cur, cw = [], 0; continue
        w = draw.textlength(tok, font=fnt)
        if tok == " ":
            cur.append((tok, fnt, fill, w)); cw += w; continue
        if cw + w > max_w and cur:
            # drop trailing space
            while cur and cur[-1][0] == " ":
                cw -= cur[-1][3]; cur.pop()
            lines.append(cur); cur, cw = [], 0
        cur.append((tok, fnt, fill, w)); cw += w
    if cur:
        lines.append(cur)
    return lines


def render_slide(slide, idx):
    img = Image.new("RGB", (OW, OH), (255, 255, 255))
    d = ImageDraw.Draw(img, "RGBA")
    for shp in slide.shapes:
        L, T, W, H = sx(shp.left or 0), sx(shp.top or 0), sx(shp.width or 0), sx(shp.height or 0)
        # picture
        if shp.shape_type == MSO_SHAPE_TYPE.PICTURE:
            try:
                import io
                pim = Image.open(io.BytesIO(shp.image.blob)).convert("RGBA")
                pim = pim.resize((max(1, W), max(1, H)))
                img.paste(pim, (L, T), pim)
            except Exception as e:
                d.rectangle([L, T, L + W, T + H], outline=(255, 0, 255))
            continue
        # autoshape fill/line
        is_oval = False
        radius = 0
        try:
            from pptx.enum.shapes import MSO_SHAPE
            ast = shp.auto_shape_type
            if ast == MSO_SHAPE.OVAL:
                is_oval = True
            elif ast == MSO_SHAPE.ROUNDED_RECTANGLE:
                try:
                    radius = int(min(W, H) * float(shp.adjustments[0]))
                except Exception:
                    radius = int(min(W, H) * 0.1)
        except Exception:
            pass
        fillc = None
        try:
            if shp.fill.type is not None and shp.fill.type == 1:  # solid
                fillc = rgb(shp.fill.fore_color)
        except Exception:
            fillc = None
        linec = None
        lw = 1
        try:
            lc = rgb(shp.line.color)
            if lc is not None:
                linec = lc
                lw = max(1, int((shp.line.width or 9525) * SCALE))
        except Exception:
            pass
        if shp.has_text_frame and not shp.text_frame.text.strip():
            # pure shape (no text)
            pass
        if fillc or linec:
            box = [L, T, L + W, T + H]
            if is_oval:
                d.ellipse(box, fill=fillc, outline=linec, width=lw if linec else 1)
            elif radius:
                d.rounded_rectangle(box, radius=radius, fill=fillc,
                                    outline=linec, width=lw if linec else 1)
            else:
                d.rectangle(box, fill=fillc, outline=linec, width=lw if linec else 1)
        # text
        if shp.has_text_frame and shp.text_frame.text.strip():
            tf = shp.text_frame
            # vertical anchor
            anchor = tf.vertical_anchor
            paras = []
            total_h = 0
            for p in tf.paragraphs:
                runs = []
                maxsz = 12
                for r in p.runs:
                    sz = (r.font.size.pt if r.font.size else 12)
                    maxsz = max(maxsz, sz)
                    fc = rgb(r.font.color) or (20, 20, 20)
                    runs.append((r.text, font(sz * PT2PX, r.font.bold), fc))
                if not runs:
                    paras.append((None, [], 0, p.alignment)); total_h += int(maxsz * PT2PX * 1.2); continue
                lines = wrap_runs(d, runs, W if W else OW)
                ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.15
                lh = int(maxsz * PT2PX * (ls if ls else 1.15))
                sb = int((p.space_before.pt if p.space_before else 0) * PT2PX)
                sa = int((p.space_after.pt if p.space_after else 0) * PT2PX)
                paras.append((lines, lh, sb, sa, p.alignment, maxsz))
                total_h += sb + sa + lh * max(1, len(lines))
            # starting y by anchor
            if anchor == MSO_ANCHOR.MIDDLE:
                y = T + (H - total_h) // 2
            elif anchor == MSO_ANCHOR.BOTTOM:
                y = T + (H - total_h)
            else:
                y = T
            for item in paras:
                if item[0] is None:
                    y += item[2] if len(item) > 2 else 14
                    continue
                lines, lh, sb, sa, align, maxsz = item
                y += sb
                for line in lines:
                    lw_total = sum(w for _, _, _, w in line)
                    if align == PP_ALIGN.CENTER:
                        x = L + (W - lw_total) // 2
                    elif align == PP_ALIGN.RIGHT:
                        x = L + (W - lw_total)
                    else:
                        x = L
                    for tok, fnt, fill, w in line:
                        d.text((x, y), tok, font=fnt, fill=fill)
                        x += w
                    y += lh
                y += sa
    img.save(os.path.join(OUT, f"slide{idx:02d}.png"))
    return img


imgs = []
for i, slide in enumerate(prs.slides, 1):
    imgs.append(render_slide(slide, i))
print("rendered", len(imgs), "slides ->", OUT)

# contact sheet 2 cols x 5 rows
cols, rows = 2, 5
pad = 16
tw = cols * OW + (cols + 1) * pad
th = rows * OH + (rows + 1) * pad
sheet = Image.new("RGB", (tw, th), (60, 66, 74))
for i, im in enumerate(imgs):
    r, c = divmod(i, cols)
    sheet.paste(im, (pad + c * (OW + pad), pad + r * (OH + pad)))
sheet.save(os.path.join(OUT, "_contact.png"))
sheet.resize((tw // 2, th // 2)).save(os.path.join(OUT, "_contact_half.png"))
print("contact sheet ->", os.path.join(OUT, "_contact.png"))

# optional PDF (one slide per page) for viewing without PowerPoint
pdf_path = os.environ.get("PREVIEW_PDF")
if pdf_path:
    imgs[0].save(pdf_path, "PDF", resolution=150.0, save_all=True,
                 append_images=imgs[1:])
    print("pdf ->", pdf_path)
