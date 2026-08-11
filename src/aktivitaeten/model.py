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
        werte = {key: wert_konvertieren(key, wert) for key, wert in roh.items()
                 if key in {f.name for f in fields(cls)}}
        return cls(**werte)


_TYPEN = {f.name: str(f.type) for f in fields(Aktivitaet)}


def wert_konvertieren(feld: str, wert: Any) -> Any:
    """Bringt einen Wert (aus JSON oder Excel) in den Typ des Feldes."""
    if wert in (None, ""):
        return wert
    if feld in ("erfasst_am", "aktualisiert_am"):
        return wert if isinstance(wert, datetime) else datetime.fromisoformat(str(wert))
    if feld in ("datum", "enddatum"):
        if isinstance(wert, datetime):
            return wert.date()
        return wert if isinstance(wert, date) else date.fromisoformat(str(wert))
    if feld in ("von", "bis"):
        if isinstance(wert, datetime):
            return wert.time().replace(second=0, microsecond=0)
        return wert if isinstance(wert, time) else time.fromisoformat(str(wert))
    if "float" in _TYPEN.get(feld, "") and not isinstance(wert, bool):
        if isinstance(wert, str):
            wert = wert.replace("'", "").replace("’", "").replace("%", "").replace(" ", "")
            wert = wert.replace(",", ".") if wert.count(",") == 1 else wert.replace(",", "")
        return float(wert)
    if "int" in _TYPEN.get(feld, "") and not isinstance(wert, bool):
        return int(wert)
    if "bool" in _TYPEN.get(feld, ""):
        return bool(wert) if not isinstance(wert, str) else wert.strip().lower() in ("ja", "wahr", "true", "x", "1")
    return str(wert).strip() if not isinstance(wert, str) else wert.strip()


# Felder, die in Excel geaendert werden duerfen und beim naechsten Lauf als
# manuelle Korrektur erhalten bleiben.
EDITIERBAR = [
    "datum", "von", "bis", "dauer_h", "kategorie", "titel", "firma", "kontakt",
    "email", "telefon", "ort", "status", "naechster_schritt", "bedarf",
    "hauptprodukt", "wahrscheinlichkeit", "wert_chf", "potenzial_chf",
    "forecast_chf", "follow_up", "organisator", "teilnehmer", "website", "notizen",
]

# Spalten des Eingabeblatts: (Feldname, Ueberschrift, Breite)
EINGABE_SPALTEN: list[tuple[str, str, int]] = [
    ("datum", "Datum *", 12),
    ("von", "Von", 8),
    ("bis", "Bis", 8),
    ("kategorie", "Kategorie", 20),
    ("titel", "Titel *", 40),
    ("firma", "Firma / Gegenstelle", 26),
    ("kontakt", "Kontakt", 22),
    ("email", "E-Mail", 28),
    ("telefon", "Telefon", 18),
    ("ort", "Ort", 24),
    ("status", "Status", 18),
    ("naechster_schritt", "Nächster Schritt", 32),
    ("bedarf", "Bedarf", 26),
    ("hauptprodukt", "Hauptprodukt", 20),
    ("wahrscheinlichkeit", "Wahrsch. %", 11),
    ("wert_chf", "Wert CHF", 13),
    ("potenzial_chf", "Potenzial CHF", 14),
    ("follow_up", "Follow-up", 16),
    ("notizen", "Notizen", 50),
    ("id", "ID (leer lassen)", 24),
]

STATUS_AUSWAHL = ["Offen", "In Arbeit", "Wiedervorlage", "Erledigt", "Bestätigt",
                  "Abgesagt", "Kein Interesse", "Angebot draussen"]


def leere_felder(a: Aktivitaet) -> int:
    """Anzahl gefuellter Felder — entscheidet bei Konflikten, welche Version gewinnt."""
    return sum(1 for f in fields(a) if getattr(a, f.name) not in (None, "", 0, False))
