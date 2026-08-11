"""Datensatz-Definition fuer eine einzelne Aktivitaet."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import date, datetime, time
from typing import Any

# Alle Zeitangaben werden in dieser Zone ausgegeben.
ZEITZONE = "Europe/Zurich"

# Reihenfolge = Spaltenreihenfolge in der Excel-Tabelle.
SPALTEN: list[tuple[str, str, int]] = [
    # (Feldname, Excel-Ueberschrift, Spaltenbreite)
    ("nr", "Nr.", 6),
    ("datum", "Datum", 12),
    ("wochentag", "Wochentag", 12),
    ("von", "Von", 8),
    ("bis", "Bis", 8),
    ("dauer_h", "Dauer (h)", 10),
    ("kategorie", "Kategorie", 18),
    ("titel", "Titel", 42),
    ("firma", "Firma / Gegenstelle", 26),
    ("kontakt", "Kontakt", 22),
    ("email", "E-Mail", 30),
    ("telefon", "Telefon", 20),
    ("ort", "Ort", 30),
    ("status", "Status", 14),
    ("naechster_schritt", "Nächster Schritt", 34),
    ("bedarf", "Bedarf", 30),
    ("hauptprodukt", "Hauptprodukt", 22),
    ("wahrscheinlichkeit", "Wahrsch.", 10),
    ("wert_chf", "Wert CHF", 14),
    ("potenzial_chf", "Potenzial CHF", 14),
    ("forecast_chf", "Gew. Forecast CHF", 16),
    ("follow_up", "Follow-up", 16),
    ("organisator", "Organisator", 24),
    ("teilnehmer", "Teilnehmer", 34),
    ("meeting_link", "Meeting-Link", 26),
    ("website", "Website", 26),
    ("notizen", "Notizen / Inhalt", 60),
    ("typ", "Typ", 20),
    ("quelle", "Quelldatei", 40),
    ("erfasst_am", "Erfasst am", 18),
    ("id", "ID", 26),
]

FELDNAMEN = [s[0] for s in SPALTEN]
UEBERSCHRIFTEN = [s[1] for s in SPALTEN]
BREITEN = [s[2] for s in SPALTEN]

# Kategorien mit Farbcode (Excel-Fuellung) und Sortierrang fuer Auswertungen.
KATEGORIEN: dict[str, str] = {
    "Akquise": "FFE2001A",
    "Kundentermin": "FF1F6FB2",
    "Beratung": "FF2E8B57",
    "Partner / Lieferant": "FF0F766E",
    "Interner Termin": "FF6B5B95",
    "Messe / Event": "FFB8860B",
    "Interne Arbeit": "FF5A6472",
    "E-Mail": "FF8A6D3B",
    "Sonstiges": "FF808080",
}


@dataclass
class Aktivitaet:
    """Eine Zeile der Auswertung."""

    id: str = ""                      # stabiler Schluessel (UID / Message-ID / Hash)
    quelle: str = ""                  # urspruenglicher Dateiname
    quelle_hash: str = ""             # SHA-256 der Quelldatei
    typ: str = ""                     # Termin (Kalender), E-Mail, Datei ...
    kategorie: str = "Sonstiges"

    datum: date | None = None
    von: time | None = None
    bis: time | None = None
    enddatum: date | None = None      # bei mehrtaegigen Terminen
    ganztags: bool = False
    dauer_h: float | None = None

    titel: str = ""
    ort: str = ""
    notizen: str = ""

    firma: str = ""
    kontakt: str = ""
    email: str = ""
    telefon: str = ""
    website: str = ""

    organisator: str = ""
    teilnehmer: str = ""
    meeting_link: str = ""

    status: str = ""
    naechster_schritt: str = ""
    bedarf: str = ""
    hauptprodukt: str = ""
    follow_up: str = ""
    wahrscheinlichkeit: float | None = None   # 0..1
    wert_chf: float | None = None
    potenzial_chf: float | None = None
    forecast_chf: float | None = None

    erfasst_am: datetime | None = None
    aktualisiert_am: datetime | None = None
    revision: int = 1

    # nur zur Laufzeit gesetzt (laufende Nummer in der Ausgabe)
    nr: int = 0

    @property
    def wochentag(self) -> str:
        if not self.datum:
            return ""
        return ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                "Freitag", "Samstag", "Sonntag"][self.datum.weekday()]

    def sortierschluessel(self) -> tuple:
        return (
            self.datum or date.min,
            self.von or time.min,
            self.titel.lower(),
        )

    # -- Serialisierung ---------------------------------------------------
    def to_json(self) -> dict[str, Any]:
        roh = asdict(self)
        roh.pop("nr", None)
        for key, wert in list(roh.items()):
            if isinstance(wert, datetime):
                roh[key] = wert.isoformat()
            elif isinstance(wert, date):
                roh[key] = wert.isoformat()
            elif isinstance(wert, time):
                roh[key] = wert.isoformat(timespec="minutes")
        return roh

    @classmethod
    def from_json(cls, roh: dict[str, Any]) -> "Aktivitaet":
        typen = {f.name: f.type for f in fields(cls)}
        werte: dict[str, Any] = {}
        for key, wert in roh.items():
            if key not in typen:
                continue
            if wert in (None, ""):
                werte[key] = wert
                continue
            deklariert = str(typen[key])
            if key in ("erfasst_am", "aktualisiert_am"):
                werte[key] = datetime.fromisoformat(wert)
            elif key in ("datum", "enddatum"):
                werte[key] = date.fromisoformat(wert)
            elif key in ("von", "bis"):
                werte[key] = time.fromisoformat(wert)
            elif "float" in deklariert and not isinstance(wert, bool):
                werte[key] = float(wert)
            else:
                werte[key] = wert
        return cls(**werte)


def leere_felder(a: Aktivitaet) -> int:
    """Anzahl gefuellter Felder — entscheidet bei Konflikten, welche Version gewinnt."""
    return sum(1 for f in fields(a) if getattr(a, f.name) not in (None, "", 0, False))
