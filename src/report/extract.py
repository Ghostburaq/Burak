#!/usr/bin/env python3
"""Liest den Original-Schlussbericht und schreibt ein strukturiertes Inhaltsmodell.

Der Originalbericht wurde maschinell erzeugt und trägt sein Layout in
Ad-hoc-Formatierungen: farbige Ein-Zellen-Tabellen als Hinweiskästen,
Consolas-Absätze als Formeln, Leerabsätze als Abstandshalter. Dieses Skript
trennt Inhalt von Layout: es liest den Bericht Block für Block, erkennt die
Rolle jedes Blocks und schreibt sie als JSON heraus. Der Aufbau des neuen
Berichts (``build_report.py``) liest ausschliesslich dieses Modell.

    python3 src/report/extract.py

Ergebnis: ``build/content.json`` und die Bilddateien in ``assets/report/media``.
"""

from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DOCX = ROOT / "assets" / "report" / "Schlussbericht_Kreuz_Zuzwil_original.docx"
MEDIA_DIR = ROOT / "assets" / "report" / "media"
OUT_JSON = ROOT / "build" / "content.json"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

# Der Originalbericht kodiert die Rolle eines Hinweiskastens in der Akzentfarbe
# seines linken Rands (und derselben Farbe in der Überschrift der Zelle).
CALLOUT_BY_ACCENT = {
    "2E7D32": "success",  # bestätigtes Ergebnis
    "B9770E": "warning",  # Vorbehalt, Warnung
    "C0392B": "danger",  # interner Hinweis, nicht weitergeben
    "15314F": "info",
}


def _text(el) -> str:
    """Sichtbarer Text eines Elements, Tabulatoren und Umbrüche als Leerzeichen."""
    out = []
    for node in el.iter():
        tag = node.tag
        if tag == W + "t":
            out.append(node.text or "")
        elif tag in (W + "tab", W + "br"):
            out.append(" ")
    return "".join(out)


def _para_style(p) -> str:
    pr = p.find(W + "pPr")
    if pr is None:
        return ""
    st = pr.find(W + "pStyle")
    return st.get(W + "val") if st is not None else ""


def _numbering(p, num_fmt: dict[str, str]) -> dict | None:
    """Listeneigenschaften (numId, Ebene, Aufzählungsart) eines Absatzes."""
    pr = p.find(W + "pPr")
    if pr is None:
        return None
    num_pr = pr.find(W + "numPr")
    if num_pr is None:
        return None
    num_id = num_pr.find(W + "numId")
    ilvl = num_pr.find(W + "ilvl")
    nid = num_id.get(W + "val") if num_id is not None else None
    return {
        "numId": nid,
        "level": int(ilvl.get(W + "val")) if ilvl is not None else 0,
        "ordered": num_fmt.get(nid, "bullet") != "bullet",
    }


def _num_formats(numbering_xml: bytes) -> dict[str, str]:
    """numId -> Aufzählungsart, aufgelöst über die abstrakte Definition."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(numbering_xml)
    fmt_by_abstract = {}
    for abstract in root.findall(W + "abstractNum"):
        lvl = abstract.find(W + "lvl")
        node = lvl.find(W + "numFmt") if lvl is not None else None
        if node is not None:
            fmt_by_abstract[abstract.get(W + "abstractNumId")] = node.get(W + "val")
    out = {}
    for num in root.findall(W + "num"):
        ref = num.find(W + "abstractNumId")
        if ref is not None:
            out[num.get(W + "numId")] = fmt_by_abstract.get(ref.get(W + "val"), "bullet")
    return out


def _runs(p) -> list[dict]:
    """Textläufe mit den Auszeichnungen, die inhaltlich Bedeutung tragen."""
    runs = []
    for run in p.findall(W + "r"):
        txt = "".join(t.text or "" for t in run.findall(W + "t"))
        if not txt:
            continue
        rpr = run.find(W + "rPr")
        bold = italic = False
        mono = False
        if rpr is not None:
            bold = rpr.find(W + "b") is not None
            italic = rpr.find(W + "i") is not None
            fonts = rpr.find(W + "rFonts")
            mono = fonts is not None and (fonts.get(W + "ascii") or "").startswith("Consolas")
        if runs and runs[-1]["bold"] == bold and runs[-1]["italic"] == italic and runs[-1]["mono"] == mono:
            runs[-1]["text"] += txt
        else:
            runs.append({"text": txt, "bold": bold, "italic": italic, "mono": mono})
    return runs


def _is_mono(p) -> bool:
    runs = _runs(p)
    return bool(runs) and all(r["mono"] for r in runs)


def _image_rels(p, rels: dict[str, str]) -> list[str]:
    """Dateinamen aller in diesem Absatz eingebetteten Bilder."""
    names = []
    for blip in p.iter(A + "blip"):
        rid = blip.get(R + "embed")
        target = rels.get(rid)
        if target:
            names.append(Path(target).name)
    return names


def _cell_accent(tc) -> str:
    """Akzentfarbe einer Hinweiskasten-Zelle, aus dem linken Rand gelesen."""
    pr = tc.find(W + "tcPr")
    if pr is None:
        return ""
    borders = pr.find(W + "tcBorders")
    if borders is None:
        return ""
    left = borders.find(W + "left")
    return (left.get(W + "color") or "").upper() if left is not None else ""


def _grid_span(tc) -> int:
    pr = tc.find(W + "tcPr")
    if pr is None:
        return 1
    span = pr.find(W + "gridSpan")
    return int(span.get(W + "val")) if span is not None else 1


def _parse_table(tbl, rels):
    """Ein-Zellen-Tabellen sind Hinweiskästen, alles andere sind Datentabellen."""
    rows = tbl.findall(W + "tr")
    if len(rows) == 1 and len(rows[0].findall(W + "tc")) == 1:
        return _parse_callout(rows[0].findall(W + "tc")[0])

    grid = []
    for tr in rows:
        cells = []
        for tc in tr.findall(W + "tc"):
            paras = [_text(p).strip() for p in tc.findall(W + "p")]
            paras = [p for p in paras if p]
            cells.append({"text": "\n".join(paras), "span": _grid_span(tc)})
        grid.append(cells)
    return {"type": "table", "rows": grid}


def _parse_callout(tc):
    accent = _cell_accent(tc)
    paras = tc.findall(W + "p")
    title = ""
    body: list[str] = []
    for i, p in enumerate(paras):
        txt = _text(p).strip()
        if not txt:
            continue
        runs = _runs(p)
        if i == 0 and runs and all(r["bold"] for r in runs):
            title = txt
        else:
            body.append(txt)
    return {
        "type": "callout",
        "variant": CALLOUT_BY_ACCENT.get(accent, "info"),
        "title": title,
        "body": body,
    }


def extract() -> dict:
    with zipfile.ZipFile(SRC_DOCX) as z:
        import xml.etree.ElementTree as ET

        doc = ET.fromstring(z.read("word/document.xml"))
        rel_root = ET.fromstring(z.read("word/_rels/document.xml.rels"))
        rels = {
            rel.get("Id"): rel.get("Target")
            for rel in rel_root
            if rel.get("Type", "").endswith("/image")
        }
        num_fmt = _num_formats(z.read("word/numbering.xml"))
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        for name in z.namelist():
            # Der Verzeichniseintrag «word/media/» selbst steht ebenfalls in der
            # Liste; ohne diese Prüfung entstünde daraus eine leere Datei.
            if name.startswith("word/media/") and not name.endswith("/"):
                with z.open(name) as fh, (MEDIA_DIR / Path(name).name).open("wb") as out:
                    shutil.copyfileobj(fh, out)

    body = doc.find(W + "body")
    blocks: list[dict] = []

    for el in body:
        tag = el.tag
        if tag == W + "tbl":
            blocks.append(_parse_table(el, rels))
            continue
        if tag != W + "p":
            continue

        style = _para_style(el)
        text = _text(el).strip()
        images = _image_rels(el, rels)

        if images:
            for name in images:
                blocks.append({"type": "figure", "image": name})
            continue
        if not text:
            continue  # Leerabsätze waren Abstandshalter; Abstand macht jetzt der Stil
        if style.startswith("Heading"):
            blocks.append({"type": "heading", "level": int(style[-1]), "text": text})
            continue
        if re.match(r"^Abbildung\s+\d+\s*:", text):
            blocks.append({"type": "caption", "text": text})
            continue
        if re.match(r"^Bild\s+\d+\s+—", text):
            blocks.append({"type": "photo_title", "text": text})
            continue
        if _is_mono(el):
            blocks.append({"type": "formula", "text": _text(el).rstrip()})
            continue
        num = _numbering(el, num_fmt)
        if style == "ListParagraph" or num:
            blocks.append(
                {
                    "type": "listitem",
                    "text": text,
                    "level": num["level"] if num else 0,
                    "numId": num["numId"] if num else None,
                    "ordered": bool(num and num["ordered"]),
                }
            )
            continue
        blocks.append({"type": "paragraph", "text": text, "runs": _runs(el)})

    return {"blocks": _merge_runs(blocks)}


def _merge_runs(blocks: list[dict]) -> list[dict]:
    """Aufeinanderfolgende Formelzeilen zu einem Block zusammenfassen."""
    merged: list[dict] = []
    for block in blocks:
        if (
            block["type"] == "formula"
            and merged
            and merged[-1]["type"] == "formula"
        ):
            merged[-1]["text"] += "\n" + block["text"]
        else:
            merged.append(block)
    return merged


def main() -> None:
    model = extract()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(model, ensure_ascii=False, indent=1), encoding="utf-8")

    counts: dict[str, int] = {}
    for block in model["blocks"]:
        counts[block["type"]] = counts.get(block["type"], 0) + 1
    print(f"{len(model['blocks'])} Blöcke -> {OUT_JSON.relative_to(ROOT)}")
    for kind, n in sorted(counts.items()):
        print(f"  {kind:12s} {n:4d}")


if __name__ == "__main__":
    main()
