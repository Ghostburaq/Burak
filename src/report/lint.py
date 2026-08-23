#!/usr/bin/env python3
"""Sucht Satzfehler im fertigen Bericht.

    python3 src/report/lint.py

Geprüft wird das gesetzte PDF zusammen mit dem DOCX. Gemeldet werden Dinge,
die man beim Durchblättern übersieht: mitten im Wort umbrochene Zeilen in
Tabellen, verwaiste Schlusszeilen, fast leere Seiten, grosse Löcher im Satz,
Verzeichniseinträge mit falscher Seitenzahl, fehlende Kopf- oder Fusszeilen.
Jeder Befund nennt die Seite, damit er sich nachsehen lässt.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "Schlussbericht_Kreuz_Zuzwil.pdf"
DOCX = ROOT / "Schlussbericht_Kreuz_Zuzwil.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

PAGE_TOP, PAGE_BOTTOM = 70.0, 770.0  # Satzspiegel in PDF-Punkten
GAP_LIMIT = 170.0  # Loch im Satz, ab dem nachgesehen werden sollte
THIN_PAGE = 400  # Zeichen, unter denen eine Seite als fast leer gilt
UNITS = r"kVA|kWh|kW|kHz|Hz|VA|Ohm|mA|ms|min|%|V|A|W|s|h"


def _run(*args: str) -> str:
    return subprocess.run(
        list(args), check=True, capture_output=True, timeout=600
    ).stdout.decode("utf-8", "replace")


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for special, plain in (("‑", "-"), ("‐", "-"), ("’", "'"),
                           (" ", " "), (" ", " ")):
        text = text.replace(special, plain)
    return re.sub(r"\s+", " ", text).strip().lower()


def pages_text() -> list[str]:
    return _run("pdftotext", "-layout", str(PDF), "-").split("\f")[:-1]


def lines_with_boxes() -> list[list[tuple[float, float, str]]]:
    """Je Seite die Zeilen als (Oberkante, Unterkante, Text)."""
    xml = _run("pdftotext", "-bbox-layout", str(PDF), "-")
    pages: list[list[tuple[float, float, str]]] = []
    for page in re.findall(r"<page\b.*?</page>", xml, re.S):
        lines = []
        for line in re.findall(r'<line xMin="[\d.]+" yMin="([\d.]+)" '
                               r'xMax="[\d.]+" yMax="([\d.]+)">(.*?)</line>',
                               page, re.S):
            top, bottom, inner = float(line[0]), float(line[1]), line[2]
            words = re.findall(r"<word[^>]*>(.*?)</word>", inner, re.S)
            lines.append((top, bottom, " ".join(words)))
        pages.append(lines)
    return pages


MIN_FIGURE_PX = 200  # darunter ist es die Bildmarke der Kopfzeile, keine Abbildung


def image_pages() -> dict[int, int]:
    """Je Seite die Anzahl echter Abbildungen.

    pdftotext sieht keine Bilder. Ohne diese Information wäre jede Abbildung
    ein vermeintliches Loch im Satz. Die Bildmarke der Kopfzeile steht auf
    jeder Seite und zählt deshalb nicht mit — sonst wäre keine Seite mehr
    prüfbar.
    """
    listing = _run("pdfimages", "-list", str(PDF))
    counts: dict[int, int] = {}
    for line in listing.splitlines()[2:]:
        parts = line.split()
        if len(parts) < 5 or not parts[0].isdigit():
            continue
        page, kind, width = int(parts[0]), parts[2], int(parts[3])
        if kind != "image" or width < MIN_FIGURE_PX:
            continue
        counts[page] = counts.get(page, 0) + 1
    return counts


def source_hyphens() -> set[str]:
    """Wörter, die schon im Text einen Bindestrich tragen (125-A-Anschluss)."""
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(DOCX) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    text = "".join(t.text or "" for t in root.iter(W + "t"))
    return {w.lower() for w in re.findall(r"\S*-\S*", _norm(text))}


def headings_from_docx() -> list[tuple[int, str]]:
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(DOCX) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out = []
    for p in root.iter(W + "p"):
        pr = p.find(W + "pPr")
        if pr is None:
            continue
        style = pr.find(W + "pStyle")
        if style is None or not style.get(W + "val").startswith("Heading"):
            continue
        text = "".join(t.text or "" for t in p.iter(W + "t"))
        if text.strip():
            out.append((int(style.get(W + "val")[-1]), text.strip()))
    return out


# ------------------------------------------------------------------ Prüfungen --
def check_broken_words(pages: list[str], hyphenated: set[str]) -> list[str]:
    """Zeilen, die mit Bindestrich enden, obwohl dort nicht getrennt werden darf.

    Im Fliesstext ist Trennung erwünscht. In Tabellenzeilen — erkennbar an
    mehreren durch grosse Lücken getrennten Textblöcken — ist sie abgestellt.
    Ein Bindestrich, der schon im Ausgangstext steht (125-A-Anschluss), ist
    keine Trennung und wird nicht gemeldet.
    """
    hits = []
    for n, page in enumerate(pages, 1):
        for line in page.split("\n"):
            stripped = line.rstrip()
            if not stripped.endswith("-"):
                continue
            if not re.search(r"\S {3,}\S", line):  # keine mehrspaltige Zeile
                continue
            tail = stripped.split()[-1].lower()
            if any(tail in word or word.startswith(tail) for word in hyphenated):
                continue  # echter Bindestrich, keine Worttrennung
            hits.append(f"Seite {n}: Trennung in Tabellenzeile — {stripped.strip()[:90]}")
    return hits


def check_thin_pages(pages: list[str], images: dict[int, int]) -> list[str]:
    """Seiten mit sehr wenig Text.

    Ausgenommen sind Bildseiten, die Schlussseite und die letzte Seite eines
    Kapitels: dass ein Kapitelende kurz ausfällt, ist die Folge davon, dass
    jedes Kapitel auf einer neuen Seite beginnt, und kein Satzfehler.
    """
    hits = []
    for n, page in enumerate(pages[:-1], 1):
        if images.get(n):
            continue
        if re.search(r"^\s*KAPITEL\s|^\s*ANHANG\s", pages[n], re.M | re.I):
            continue  # Folgeseite beginnt ein neues Kapitel
        body = re.sub(r"\s+", "", page)
        if len(body) < THIN_PAGE:
            hits.append(f"Seite {n}: nur {len(body)} Zeichen Text")
    return hits


def check_gaps(boxes, images: dict[int, int]) -> list[str]:
    """Grosse Leerräume mitten auf einer Seite, ohne Bild als Erklärung."""
    hits = []
    for n, lines in enumerate(boxes, 1):
        if images.get(n):
            continue
        body = [l for l in lines if PAGE_TOP < l[0] < PAGE_BOTTOM]
        if len(body) < 2:
            continue
        body.sort()
        for (_, bottom, before), (top, _, after) in zip(body, body[1:]):
            gap = top - bottom
            if gap > GAP_LIMIT:
                hits.append(
                    f"Seite {n}: {gap:.0f} pt Leerraum nach «{before.strip()[:52]}»"
                )
    return hits


def check_orphans(boxes) -> list[str]:
    """Seiten, die mit einer einzelnen Restzeile eines Absatzes beginnen."""
    hits = []
    for n, lines in enumerate(boxes[1:], 2):
        body = sorted(l for l in lines if PAGE_TOP < l[0] < PAGE_BOTTOM)
        if len(body) < 2:
            continue
        first, second = body[0], body[1]
        if second[0] - first[1] > 24 and len(first[2].split()) <= 4:
            hits.append(f"Seite {n}: beginnt mit Restzeile «{first[2].strip()[:60]}»")
    return hits


def check_toc(pages: list[str]) -> list[str]:
    """Jede Zeile des Verzeichnisses gegen die tatsächliche Fundstelle prüfen."""
    entries = []
    for page in pages[:6]:
        for line in page.split("\n"):
            m = re.match(r"^\s*(.+?)\.{4,}\s*(\d+)\s*$", line)
            if m:
                entries.append((_norm(m.group(1)), int(m.group(2))))
    if not entries:
        return ["Kein Inhaltsverzeichnis gefunden."]

    normalized = [[_norm(l) for l in p.split("\n")] for p in pages]
    hits = []
    cursor = 0
    for title, printed in entries:
        found = None
        for page in range(cursor, len(normalized)):
            if any(line == title for line in normalized[page]):
                found = page + 1
                cursor = page
                break
        if found is None:
            hits.append(f"Verzeichnis: «{title[:56]}» im Text nicht gefunden")
        elif found != printed:
            hits.append(f"Verzeichnis: «{title[:48]}» zeigt {printed}, steht auf {found}")
    return hits, len(entries)


def check_running_titles(pages: list[str]) -> list[str]:
    hits = []
    for n, page in enumerate(pages, 1):
        lines = [l for l in page.split("\n") if l.strip()]
        if n > 1 and not any("Schlussbericht Netzqualitätsmessung" in l for l in lines[:3]):
            hits.append(f"Seite {n}: Kopfzeile fehlt")
        if not any(re.search(r"Seite\s+\d+\s+von\s+\d+", l) for l in lines[-3:]) and n > 1:
            hits.append(f"Seite {n}: Fusszeile ohne Seitenzahl")
    return hits


def check_headings_order(headings: list[tuple[int, str]]) -> list[str]:
    """Kapitel- und Abschnittsnummern müssen lückenlos aufsteigen."""
    hits = []
    chapter = 0
    section = 0
    for level, text in headings:
        if level == 1:
            m = re.match(r"^(\d+)\.", text)
            if m:
                want = chapter + 1
                if int(m.group(1)) != want:
                    hits.append(f"Kapitel {m.group(1)} folgt auf {chapter}")
                chapter = int(m.group(1))
                section = 0
        elif level == 2:
            m = re.match(r"^(\d+)\.(\d+)", text)
            if m and int(m.group(1)) == chapter:
                if int(m.group(2)) != section + 1:
                    hits.append(f"Abschnitt {text[:40]} folgt auf {chapter}.{section}")
                section = int(m.group(2))
    return hits


def check_structure() -> list[str]:
    """Innerer Zusammenhalt der Word-Datei.

    Ein Verweis ohne Ziel, eine Bildbeziehung ohne Datei oder ein Listenbezug
    ohne Definition öffnet zwar noch, verhält sich in Word aber falsch — und
    fällt beim Durchblättern des PDF nicht auf.
    """
    import xml.etree.ElementTree as ET

    R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    hits = []
    with zipfile.ZipFile(DOCX) as z:
        names = set(z.namelist())
        doc = ET.fromstring(z.read("word/document.xml"))
        rels = {r.get("Id"): r.get("Target")
                for r in ET.fromstring(z.read("word/_rels/document.xml.rels"))}
        numbering = ET.fromstring(z.read("word/numbering.xml"))

    starts = [b.get(W + "name") for b in doc.iter(W + "bookmarkStart")]
    ids = [b.get(W + "id") for b in doc.iter(W + "bookmarkStart")]
    if len(ids) != len(set(ids)):
        hits.append("doppelt vergebene Sprungmarken-Kennungen")
    open_ids = set(ids) - {b.get(W + "id") for b in doc.iter(W + "bookmarkEnd")}
    if open_ids:
        hits.append(f"{len(open_ids)} Sprungmarke(n) ohne Ende")

    targets = set(starts)
    anchors = {h.get(W + "anchor") for h in doc.iter(W + "hyperlink") if h.get(W + "anchor")}
    for missing in sorted(anchors - targets):
        hits.append(f"Verweis ohne Ziel: {missing}")
    instr = "".join(t.text or "" for t in doc.iter(W + "instrText"))
    for missing in sorted(set(re.findall(r"PAGEREF\s+(\S+)", instr)) - targets):
        hits.append(f"Seitenverweis ohne Sprungmarke: {missing}")

    used = {b.get(R + "embed") for b in doc.iter(A + "blip")}
    for rid in sorted(used):
        target = rels.get(rid)
        if not target:
            hits.append(f"Bildbeziehung {rid} fehlt")
        elif "word/" + target.lstrip("/") not in names:
            hits.append(f"Bilddatei fehlt: {target}")
    orphans = [r for r, t in rels.items() if t and t.startswith("media/") and r not in used]
    if orphans:
        hits.append(f"{len(orphans)} Bilddatei(en) im Paket, die niemand verwendet")

    defined = {n.get(W + "numId") for n in numbering.findall(W + "num")}
    referenced = {n.find(W + "numId").get(W + "val")
                  for n in doc.iter(W + "numPr") if n.find(W + "numId") is not None}
    for missing in sorted(referenced - defined):
        hits.append(f"Liste {missing} ohne Definition")
    return hits


def check_figure_order() -> list[str]:
    """Abbildungen müssen in Lesereihenfolge durchnummeriert sein."""
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(DOCX) as z:
        doc = ET.fromstring(z.read("word/document.xml"))
    seen = []
    for p in doc.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t"))
        m = re.match(r"^Abbildung[\s\u00a0]+(\d+):", text)
        if m:
            seen.append(int(m.group(1)))
    expected = list(range(1, len(seen) + 1))
    if seen != expected:
        return [f"Abbildungen stehen als {seen}, erwartet {expected}"]
    return []


def check_typography() -> list[str]:
    """Zahlensatz im DOCX prüfen.

    Nicht im PDF: pdftotext gibt jedes geschützte Leerzeichen als gewöhnliches
    aus, dort wäre jede richtig gesetzte Stelle ein Fehlalarm.
    """
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(DOCX) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    # Rechenblöcke stehen in Festbreitenschrift und richten ihre Spalten über
    # Leerzeichen aus. Dort wird bewusst nichts eingefügt, was die Zeichenzahl
    # ändert — sie gehören deshalb nicht in diese Prüfung.
    parts = []
    for r in root.iter(W + "r"):
        rpr = r.find(W + "rPr")
        fonts = rpr.find(W + "rFonts") if rpr is not None else None
        if fonts is not None and (fonts.get(W + "ascii") or "").startswith("Consolas"):
            continue
        parts.append("".join(t.text or "" for t in r.iter(W + "t")))
    text = "".join(parts)
    hits = []
    loose = re.findall(rf"\d (?:{UNITS})(?![\wäöüÄÖÜß])", text)
    if loose:
        hits.append(f"{len(loose)}× gewöhnliches Leerzeichen vor Einheit, "
                    f"z. B. {loose[0]!r}")
    plain = re.findall(r"\b\d{1,3}'\d{3}\b", text)
    if plain:
        hits.append(f"{len(plain)}× gerades Hochkomma als Tausendertrennung, "
                    f"z. B. {plain[0]!r}")
    unseparated = re.findall(
        rf"(?<![\d’',.])(\d{{4,}})(?=[ \u00a0](?:{UNITS})(?![\wäöüÄÖÜß]))", text
    )
    if unseparated:
        hits.append(f"{len(unseparated)}× Messwert ohne Tausendertrennung, "
                    f"z. B. {sorted(set(unseparated))[:6]}")
    for norm, number in re.findall(r"\b(EN|IEC|DIN|VDE|ISO|SN)[ \u00a0](\S+)", text):
        if "’" in number:
            hits.append(f"Normnummer fälschlich getrennt: {norm} {number}")
    return hits


def main() -> int:
    if not PDF.exists():
        print("PDF fehlt. Zuerst src/report/make.py laufen lassen.")
        return 2

    pages = pages_text()
    boxes = lines_with_boxes()
    headings = headings_from_docx()
    images = image_pages()
    toc_hits, toc_count = check_toc(pages)

    groups = [
        ("Worttrennung in Tabellen", check_broken_words(pages, source_hyphens())),
        ("Fast leere Seiten", check_thin_pages(pages, images)),
        ("Löcher im Satz", check_gaps(boxes, images)),
        ("Verwaiste Restzeilen", check_orphans(boxes)),
        (f"Inhaltsverzeichnis ({toc_count} Einträge)", toc_hits),
        ("Kopf- und Fusszeilen", check_running_titles(pages)),
        ("Kapitelnummerierung", check_headings_order(headings)),
        ("Abbildungsnummerierung", check_figure_order()),
        ("Innerer Zusammenhalt der Datei", check_structure()),
        ("Zahlensatz", check_typography()),
    ]

    print(f"{len(pages)} Seiten · {len(headings)} Überschriften\n")
    total = 0
    for name, hits in groups:
        total += len(hits)
        mark = "ok" if not hits else f"{len(hits)} Befund(e)"
        print(f"{name}: {mark}")
        for hit in hits[:25]:
            print(f"    {hit}")
        if len(hits) > 25:
            print(f"    … und {len(hits) - 25} weitere")
    print(f"\nInsgesamt {total} Befunde.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
