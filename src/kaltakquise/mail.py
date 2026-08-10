"""
Zerlegt einen Mailtext in seine Bestandteile und schneidet Modellausgaben
in einzelne Varianten.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import regeln


@dataclass
class Mail:
    """Eine zerlegte Kaltakquise-Mail."""

    roh: str
    betreff: str = ""
    anrede: str = ""
    fliesstext: str = ""
    gruss: str = ""
    signatur: list[str] = field(default_factory=list)

    @property
    def wortzahl(self) -> int:
        return len(_woerter(self.fliesstext))


def _woerter(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text) if any(c.isalnum() for c in w)]


def zerlege(text: str) -> Mail:
    """Zerlegt einen Mailtext. Fehlende Teile bleiben leer, der Pruefer meldet sie."""
    roh = text.replace("\r\n", "\n").strip()
    zeilen = roh.split("\n")

    betreff = ""
    start = 0
    for i, zeile in enumerate(zeilen[:5]):
        treffer = re.match(r"\s*(betreff|subject|objet|oggetto)\s*:\s*(.+)", zeile, re.I)
        if treffer:
            betreff = treffer.group(2).strip().strip('"„“')
            start = i + 1
            break

    # Anrede: erste nicht leere Zeile nach dem Betreff.
    anrede = ""
    anrede_idx = start
    for i in range(start, len(zeilen)):
        if zeilen[i].strip():
            anrede_idx = i
            if regeln.ANREDE_MUSTER.match(zeilen[i]):
                anrede = zeilen[i].strip()
            break

    # Grussformel: letzte passende Zeile.
    gruss = ""
    gruss_idx = len(zeilen)
    for i in range(len(zeilen) - 1, anrede_idx, -1):
        if regeln.GRUSS_MUSTER.match(zeilen[i]):
            gruss = zeilen[i].strip()
            gruss_idx = i
            break

    korpus_start = anrede_idx + 1 if anrede else anrede_idx
    fliesstext = "\n".join(zeilen[korpus_start:gruss_idx]).strip()
    signatur = [z.strip() for z in zeilen[gruss_idx + 1 :] if z.strip()]

    return Mail(
        roh=roh,
        betreff=betreff,
        anrede=anrede,
        fliesstext=fliesstext,
        gruss=gruss,
        signatur=signatur,
    )


_VARIANTEN_KOPF = re.compile(
    r"^\s*\**\s*Variante\s+([A-Z])\b[^\n]*$", re.IGNORECASE | re.MULTILINE
)
_WARUM_ZEILE = re.compile(r"^\s*\*[^*].*wirkt.*\*\s*$", re.IGNORECASE | re.MULTILINE)
_ABSCHNITT_ENDE = re.compile(
    r"^\s*\**\s*(Follow-up|Annahme|Analyse)\b", re.IGNORECASE | re.MULTILINE
)


def extrahiere_varianten(ausgabe: str) -> list[tuple[str, str]]:
    """Schneidet aus der Modellausgabe die Bloecke 'Variante A/B' heraus."""
    treffer = list(_VARIANTEN_KOPF.finditer(ausgabe))
    if not treffer:
        return []

    varianten: list[tuple[str, str]] = []
    for i, kopf in enumerate(treffer):
        ende = treffer[i + 1].start() if i + 1 < len(treffer) else len(ausgabe)
        block = ausgabe[kopf.end() : ende]

        schluss = _ABSCHNITT_ENDE.search(block)
        if schluss:
            block = block[: schluss.start()]
        block = _WARUM_ZEILE.sub("", block)

        # Codefences und Trennlinien entfernen, sie gehoeren nicht in die Mail.
        block = re.sub(r"^\s*```.*$", "", block, flags=re.MULTILINE)
        block = re.sub(r"^\s*-{3,}\s*$", "", block, flags=re.MULTILINE)
        block = block.strip().strip('"')

        varianten.append((f"Variante {kopf.group(1).upper()}", block.strip()))

    return varianten
