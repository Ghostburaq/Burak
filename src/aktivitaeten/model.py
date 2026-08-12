"""Datensatz-Definition fuer eine einzelne Aktivitaet."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import date, datetime, time
from typing import Any

# Alle Zeitangaben werden in dieser Zone ausgegeben.
ZEITZONE = "Europe/Zurich"

# Reihenfolge = Spaltenreihenfolge in der Excel-Tabelle.
# Die ersten elf Spalten sind sichtbar, der Rest ist eingeklappt (Gruppierung
# in Excel aufklappbar) — so bleibt die Tabelle schmal, ohne dass Daten
# verloren gehen.
SPALTEN: list[tuple[str, str, int, bool]] = [
    # (Feldname, Excel-Ueberschrift, Spaltenbreite, sichtbar)
    ("nr", "Pos.", 6, True),
    ("datum", "Datum", 12, True),
    ("zeit", "Zeit", 14, True),
    ("dauer_h", "Std.", 7, True),
    ("kategorie", "Kategorie", 19, True),
    ("titel", "Titel", 46, True),
    ("firma", "Firma / Gegenstelle", 26, True),
    ("kontakt", "Kontakt", 22, True),
    ("status", "Status", 17, True),
    ("naechster_schritt", "Nächster Schritt", 34, True),
    ("potenzial_chf", "Potenzial CHF", 14, True),
    ("notizen", "Notizen", 58, True),
    # --- ab hier eingeklappt -------------------------------------------
    ("wochentag", "Wochentag", 12, False),
    ("von", "Von", 8, False),
    ("bis", "Bis", 8, False),
    ("email", "E-Mail", 28, False),
    ("telefon", "Telefon", 18, False),
    ("ort", "Ort", 28, False),
    ("teilnehmer", "Teilnehmer", 30, False),
    ("organisator", "Organisator", 22, False),
    ("website", "Website", 24, False),
    ("meeting_link", "Meeting-Link", 24, False),
    ("bedarf", "Bedarf", 28, False),
    ("hauptprodukt", "Hauptprodukt", 20, False),
    ("wahrscheinlichkeit", "Wahrsch.", 10, False),
    ("wert_chf", "Wert CHF", 13, False),
    ("forecast_chf", "Gew. Forecast CHF", 16, False),
    ("follow_up", "Follow-up", 15, False),
    ("typ", "Typ", 20, False),
    ("quelle", "Quelldatei", 34, False),
    ("erfasst_am", "Erfasst am", 17, False),
    ("id", "ID", 24, False),
]

FELDNAMEN = [s[0] for s in SPALTEN]
UEBERSCHRIFTEN = [s[1] for s in SPALTEN]
BREITEN = [s[2] for s in SPALTEN]
SICHTBAR = [s[3] for s in SPALTEN]

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

    @property
    def zeit(self) -> str:
        """Eine Spalte statt Von/Bis: '08:30–09:00', '09:05' oder 'ganztägig'."""
        if self.ganztags:
            if self.enddatum and self.datum and self.enddatum > self.datum:
                return f"ganztägig, bis {self.enddatum:%d.%m.}"
            return "ganztägig"
        if self.von and self.bis:
            return f"{self.von:%H:%M}–{self.bis:%H:%M}"
        if self.von:
            return f"{self.von:%H:%M}"
        return ""

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
    ("potenzial_chf", "Potenzial CHF", 14),
    ("notizen", "Notizen", 50),
    ("id", "ID (leer lassen)", 24),
]

STATUS_AUSWAHL = ["Offen", "In Arbeit", "Wiedervorlage", "Erledigt", "Bestätigt",
                  "Abgesagt", "Kein Interesse", "Angebot draussen"]


def leere_felder(a: Aktivitaet) -> int:
    """Anzahl gefuellter Felder — entscheidet bei Konflikten, welche Version gewinnt."""
    return sum(1 for f in fields(a) if getattr(a, f.name) not in (None, "", 0, False))
