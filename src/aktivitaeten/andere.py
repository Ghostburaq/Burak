"""Fallback-Parser: Screenshots, PDFs, Word-Dateien, Notizen, sonstige Dateien.

Damit landet auch das in der Liste, was kein Kalender- oder Mail-Format hat —
etwa ein Screenshot samt getippter Notiz. Eine Notiz kann auf zwei Wegen
mitgegeben werden:

  1. Sidecar-Datei gleichen Namens mit Endung ``.txt``
     (``screenshot.png`` + ``screenshot.png.txt`` oder ``screenshot.txt``)
  2. Beim Import per ``--notiz "..."`` (gilt fuer alle Dateien des Aufrufs)
"""

from __future__ import annotations

import os
import re
import zipfile
from datetime import datetime
from pathlib import Path

from . import felder
from .model import Aktivitaet

BILD_ENDUNGEN = {".png", ".jpg", ".jpeg", ".gif", ".heic", ".webp", ".bmp", ".tiff"}
TEXT_ENDUNGEN = {".txt", ".md", ".log", ".csv"}

# Datum/Uhrzeit aus typischen Screenshot-Dateinamen
DATEINAME_MUSTER = [
    re.compile(r"(20\d{2})[-_.]?(\d{2})[-_.]?(\d{2})[\sT_-]+(\d{2})[-_.:]?(\d{2})"),
    re.compile(r"(20\d{2})[-_.]?(\d{2})[-_.]?(\d{2})"),
]


def _zeit_aus_dateiname(name: str) -> datetime | None:
    for muster in DATEINAME_MUSTER:
        treffer = muster.search(name)
        if not treffer:
            continue
        teile = [int(g) for g in treffer.groups()]
        try:
            if len(teile) >= 5:
                return datetime(teile[0], teile[1], teile[2], teile[3], teile[4])
            return datetime(teile[0], teile[1], teile[2])
        except ValueError:
            continue
    return None


def _exif_zeit(pfad: Path) -> datetime | None:
    try:
        from PIL import Image  # optional
    except Exception:
        return None
    try:
        with Image.open(pfad) as bild:
            exif = bild.getexif()
            for tag in (36867, 36868, 306):     # DateTimeOriginal, Digitized, DateTime
                wert = exif.get(tag)
                if wert:
                    return datetime.strptime(str(wert)[:19], "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None
    return None


def _docx_text(pfad: Path) -> str:
    try:
        with zipfile.ZipFile(pfad) as archiv:
            roh = archiv.read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return ""
    roh = re.sub(r"</w:p>", "\n", roh)
    return re.sub(r"<[^>]+>", "", roh)


def _pdf_text(pfad: Path) -> str:
    try:
        from pypdf import PdfReader  # optional
    except Exception:
        return ""
    try:
        leser = PdfReader(str(pfad))
        return "\n".join((seite.extract_text() or "") for seite in leser.pages[:10])
    except Exception:
        return ""


def notiz_sidecar(pfad: Path) -> str:
    for kandidat in (pfad.with_suffix(pfad.suffix + ".txt"), pfad.with_suffix(".txt")):
        if kandidat != pfad and kandidat.exists():
            return kandidat.read_text(encoding="utf-8", errors="replace").strip()
    return ""


def parsen(pfad_str: str, roh_bytes: bytes, quelle: str, quelle_hash: str,
           notiz: str = "") -> list[Aktivitaet]:
    pfad = Path(pfad_str)
    endung = pfad.suffix.lower()

    inhalt = ""
    if endung in TEXT_ENDUNGEN:
        inhalt = roh_bytes.decode("utf-8", "replace")
    elif endung == ".docx":
        inhalt = _docx_text(pfad)
    elif endung == ".pdf":
        inhalt = _pdf_text(pfad)

    beschreibung = (notiz or notiz_sidecar(pfad) or "").strip()
    volltext = f"{beschreibung}\n{inhalt}".strip()

    zeitpunkt = (_zeit_aus_dateiname(pfad.name)
                 or (_exif_zeit(pfad) if endung in BILD_ENDUNGEN else None)
                 or datetime.fromtimestamp(os.path.getmtime(pfad)).replace(microsecond=0))

    if endung in BILD_ENDUNGEN:
        typ = "Screenshot / Bild"
    elif endung in TEXT_ENDUNGEN:
        typ = "Notiz"
    elif endung in (".pdf", ".docx", ".doc", ".xlsx", ".pptx"):
        typ = f"Dokument ({endung.lstrip('.')})"
    else:
        typ = f"Datei ({endung.lstrip('.') or 'ohne Endung'})"

    # Titel: erste Zeile der Notiz, sonst aufgeraeumter Dateiname
    erste_zeile = next((z.strip() for z in beschreibung.splitlines() if z.strip()), "")
    titel = erste_zeile[:120] or re.sub(r"[_-]+", " ", pfad.stem).strip()

    a = Aktivitaet(
        id=f"datei:{quelle_hash[:24]}",
        quelle=quelle,
        quelle_hash=quelle_hash,
        typ=typ,
        titel=titel,
        datum=zeitpunkt.date(),
        von=zeitpunkt.time().replace(second=0, microsecond=0),
        notizen=felder.saeubern(volltext)[:2000] or f"Datei ohne Textinhalt: {pfad.name}",
        erfasst_am=zeitpunkt,
        status="Erfasst",
    )
    a.kategorie = felder.kategorie_bestimmen(titel, a.notizen, typ)
    if a.kategorie == "Sonstiges":
        a.kategorie = "Interne Arbeit"

    adressen = felder.emails(volltext)
    a.email = adressen[0] if adressen else ""
    nummern = felder.telefone(volltext)
    a.telefon = nummern[0] if nummern else ""
    a.website = felder.website(volltext)
    a.firma = felder.firma_aus_titel(titel) or (felder.firma_aus_domain(a.email) if a.email else "")

    for schluessel, wert in felder.akquise_felder(volltext).items():
        if hasattr(a, schluessel):
            setattr(a, schluessel, wert)

    return [a]
