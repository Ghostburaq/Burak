"""Persistenter Speicher aller erfassten Aktivitaeten.

Aufgaben:
  * Dedup auf Dateiebene  — identische Datei zweimal reingeworfen = kein Duplikat
  * Dedup auf Eventebene  — gleiche Kalender-UID / Message-ID = ein Eintrag
  * Update-Erkennung      — geaenderte Version desselben Termins ueberschreibt
                            die alte und erhoeht die Revision
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from .model import Aktivitaet, leere_felder


def datei_hash(pfad: Path) -> str:
    hasher = hashlib.sha256()
    with open(pfad, "rb") as datei:
        for block in iter(lambda: datei.read(1 << 16), b""):
            hasher.update(block)
    return hasher.hexdigest()


class Registry:
    def __init__(self, pfad: Path):
        self.pfad = pfad
        self.eintraege: dict[str, Aktivitaet] = {}
        self.quellen: dict[str, dict] = {}       # hash -> Metadaten der Quelldatei
        if pfad.exists():
            self._laden()

    # -- Laden / Speichern ------------------------------------------------
    def _laden(self) -> None:
        daten = json.loads(self.pfad.read_text(encoding="utf-8"))
        self.quellen = daten.get("quellen", {})
        for roh in daten.get("eintraege", []):
            a = Aktivitaet.from_json(roh)
            self.eintraege[a.id] = a

    def speichern(self) -> None:
        self.pfad.parent.mkdir(parents=True, exist_ok=True)
        daten = {
            "schema": 1,
            "aktualisiert": datetime.now().isoformat(timespec="seconds"),
            "quellen": self.quellen,
            "eintraege": [a.to_json() for a in self.sortiert()],
        }
        self.pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")

    # -- Import -----------------------------------------------------------
    def quelle_bekannt(self, hash_wert: str) -> bool:
        return hash_wert in self.quellen

    def quelle_vermerken(self, hash_wert: str, name: str, typ: str, anzahl: int,
                         groesse: int) -> None:
        vorhanden = self.quellen.get(hash_wert)
        if vorhanden:
            namen = set(vorhanden.get("dateinamen", []))
            namen.add(name)
            vorhanden["dateinamen"] = sorted(namen)
            vorhanden["importe"] = vorhanden.get("importe", 1) + 1
            return
        self.quellen[hash_wert] = {
            "dateinamen": [name],
            "typ": typ,
            "eintraege": anzahl,
            "groesse_bytes": groesse,
            "importiert_am": datetime.now().isoformat(timespec="seconds"),
            "importe": 1,
        }

    def aufnehmen(self, neu: Aktivitaet) -> str:
        """Fuegt einen Eintrag hinzu. Rueckgabe: 'neu' | 'aktualisiert' | 'unveraendert'."""
        jetzt = datetime.now().replace(microsecond=0)
        alt = self.eintraege.get(neu.id)
        if alt is None:
            neu.aktualisiert_am = jetzt
            neu.erfasst_am = neu.erfasst_am or jetzt
            self.eintraege[neu.id] = neu
            return "neu"

        if alt.quelle_hash == neu.quelle_hash:
            return "unveraendert"

        # Gleicher Termin, andere Quelldatei: die inhaltsreichere Version gewinnt.
        gewinner, verlierer = (neu, alt) if leere_felder(neu) >= leere_felder(alt) else (alt, neu)
        zusammen = Aktivitaet(**{**gewinner.__dict__})
        for feld, wert in verlierer.__dict__.items():
            if getattr(zusammen, feld) in (None, "", 0) and wert not in (None, "", 0):
                setattr(zusammen, feld, wert)
        zusammen.revision = max(alt.revision, neu.revision) + 1
        zusammen.aktualisiert_am = jetzt
        zusammen.erfasst_am = alt.erfasst_am or neu.erfasst_am
        zusammen.quelle = f"{alt.quelle}; {neu.quelle}" if alt.quelle != neu.quelle else alt.quelle
        self.eintraege[neu.id] = zusammen
        return "aktualisiert"

    # -- Abfrage ----------------------------------------------------------
    def sortiert(self) -> list[Aktivitaet]:
        liste = sorted(self.eintraege.values(), key=lambda a: a.sortierschluessel())
        for nummer, eintrag in enumerate(liste, start=1):
            eintrag.nr = nummer
        return liste
