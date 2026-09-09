#!/usr/bin/env python3
"""Ersetzt für den Musterbericht die Bilder, die den Kunden preisgeben.

    python3 src/report/make_placeholders.py

Text lässt sich Wort für Wort anonymisieren, ein Bild nicht. Deshalb gilt hier
eine strenge Regel statt einer Stichwortliste:

    Ein Bild wird nur übernommen, wenn sein vollständig ausgelesener Text
    keine einzige identifizierende Angabe enthält.

Warum so streng: das Übersichtsschema trägt den Betriebsnamen in der
Titelzeile, die Sonnenuntergangs-Grafik die Geokoordinaten des Objekts, und
in einer Fussnote des Schemas steht die Errichterfirma der Photovoltaikanlage.
Die Koordinaten hätte keine Namensliste gefunden. Was diese Prüfung nicht
zweifelsfrei freigibt, wird durch eine gestaltete Platzhalterfläche ersetzt —
gleiche Abmessungen, damit der Satz unverändert bleibt.

Die Aufnahmen der Bilddokumentation zeigen die realen Räume des Betriebs.
Sie werden ausnahmslos ersetzt; anonymisieren lässt sich daran nichts.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import anonymise

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "build" / "content.json"
MEDIA = ROOT / "assets" / "report" / "media"
OUT = ROOT / "build" / "media_muster"
LOGO = ROOT / "assets" / "report" / "logo" / "logo_mark_pale.png"

SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

PANEL = (240, 243, 246)
BORDER = (201, 209, 216)
INK = (27, 36, 48)
STEEL = (107, 116, 128)
STEEL_LT = (151, 160, 171)


def ocr(path: Path) -> str:
    """Kompletter Text eines Bildes, in zwei Segmentierungsmodi gelesen.

    Ein Modus allein übersieht je nach Anordnung Zeilen; die Vereinigung
    beider ist die belastbarere Grundlage für die Freigabe.
    """
    text = []
    for psm in ("6", "11"):
        try:
            out = subprocess.run(
                ["tesseract", str(path), "stdout", "-l", "deu", "--psm", psm],
                check=True, capture_output=True, timeout=300,
            )
            text.append(out.stdout.decode("utf-8", "replace"))
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise SystemExit(
                f"OCR nicht möglich ({exc}). Ohne Textprüfung der Bilder lässt sich "
                "der Musterbericht nicht verantworten — tesseract-ocr installieren."
            ) from exc
    return "\n".join(text)


def _wrap(draw, text: str, font, max_w: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        probe = f"{line} {word}".strip()
        if draw.textlength(probe, font=font) <= max_w or not line:
            line = probe
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def placeholder(size: tuple[int, int], label: str, subject: str) -> Image.Image:
    """Platzhalterfläche im Satzbild des Berichts, in Originalabmessung."""
    w, h = size
    img = Image.new("RGB", size, PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=BORDER, width=max(1, round(w / 700)))

    unit = max(11, round(min(w, h) / 34))
    f_label = ImageFont.truetype(SANS_BOLD, round(unit * 1.35))
    f_subject = ImageFont.truetype(SANS, round(unit * 1.02))
    f_note = ImageFont.truetype(SANS_BOLD, round(unit * 0.72))

    mark_h = round(min(w, h) * 0.17)
    with Image.open(LOGO) as logo:
        ratio = logo.width / logo.height
        mark = logo.convert("RGBA").resize(
            (max(1, round(mark_h * ratio)), mark_h), Image.LANCZOS
        )

    text_w = round(w * 0.74)
    subject_lines = _wrap(d, subject, f_subject, text_w)
    gap = round(unit * 0.85)
    line_h = round(unit * 1.5)
    block_h = (
        mark.height + gap * 2
        + round(unit * 1.35) + gap
        + line_h * len(subject_lines) + gap * 2
        + round(unit * 0.72)
    )
    y = max(round(h * 0.06), (h - block_h) // 2)

    img.paste(mark, ((w - mark.width) // 2, y), mark)
    y += mark.height + gap * 2

    d.text((w / 2, y), label, font=f_label, fill=INK, anchor="ma")
    y += round(unit * 1.35) + gap

    for line in subject_lines:
        d.text((w / 2, y), line, font=f_subject, fill=STEEL, anchor="ma")
        y += line_h

    rule_w = round(w * 0.16)
    rule_y = y + gap
    d.line([(w / 2 - rule_w, rule_y), (w / 2 + rule_w, rule_y)], fill=BORDER, width=1)

    d.text((w / 2, rule_y + gap), "MUSTERBERICHT · OHNE ANLAGENDATEN",
           font=f_note, fill=STEEL_LT, anchor="ma")
    return img


def subjects() -> dict[str, tuple[str, str]]:
    """Zu jedem Bild seine Beschriftung, aus dem Inhaltsmodell gelesen."""
    blocks = json.loads(CONTENT.read_text(encoding="utf-8"))["blocks"]
    out: dict[str, tuple[str, str]] = {}
    figure_no = 0
    for i, block in enumerate(blocks):
        if block["type"] != "figure":
            continue
        following = blocks[i + 1] if i + 1 < len(blocks) else {}
        previous = blocks[i - 1] if i else {}
        if following.get("type") == "caption":
            figure_no += 1
            text = anonymise.apply(following["text"])
            m = re.match(r"^Abbildung\s+\d+:\s*(.*)$", text, re.S)
            out[block["image"]] = (f"Abbildung {figure_no}", m.group(1) if m else text)
        elif previous.get("type") == "photo_title":
            title = anonymise.apply(previous["text"])
            label, _, subject = title.partition("—")
            out[block["image"]] = (label.strip() or "Aufnahme", subject.strip() or title)
        else:
            out[block["image"]] = ("Abbildung", "")
    return out


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    labels = subjects()
    kept, replaced = [], []
    for path in sorted(MEDIA.iterdir()):
        label, subject = labels.get(path.name, ("Abbildung", ""))
        is_photo = path.suffix.lower() in {".jpg", ".jpeg"}

        if is_photo:
            reason = "Aufnahme des Objekts"
        else:
            found = anonymise.residue(ocr(path))
            reason = "im Bild: " + ", ".join(found) if found else ""

        if not reason:
            shutil.copy(path, OUT / path.name)
            kept.append((path.name, label))
            continue

        with Image.open(path) as im:
            size = im.size
        placeholder(size, label, subject).save(OUT / path.name)
        replaced.append((path.name, label, reason))

    print(f"{len(kept)} Bild(er) übernommen:")
    for name, label in kept:
        print(f"  {label:<14s} {name[:12]}…  Textprüfung ohne Befund")
    print(f"\n{len(replaced)} Bild(er) durch Platzhalter ersetzt:")
    for name, label, reason in replaced:
        print(f"  {label:<14s} {name[:12]}…  {reason}")


if __name__ == "__main__":
    sys.exit(main())
