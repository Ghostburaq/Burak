"""
Deterministischer Regel-Pruefer.

Prueft eine Mail gegen die harten Regeln des Systemprompts. Kein Modell,
kein Netz: gleiche Eingabe, gleiches Urteil. Damit ist "keine Fehler" eine
Zusicherung und keine Hoffnung.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from . import regeln
from .mail import Mail, zerlege

FEHLER = "fehler"
WARNUNG = "warnung"
HINWEIS = "hinweis"

_RANG = {FEHLER: 0, WARNUNG: 1, HINWEIS: 2}


@dataclass(frozen=True)
class Befund:
    schwere: str
    regel: str
    text: str

    def __str__(self) -> str:  # pragma: no cover - reine Darstellung
        marke = {FEHLER: "FEHLER ", WARNUNG: "WARNUNG", HINWEIS: "HINWEIS"}[self.schwere]
        return f"[{marke}] {self.regel}: {self.text}"


def _normalisiert(text: str) -> str:
    """Kleinschreibung, Umlaute erhalten, Whitespace vereinheitlicht."""
    return re.sub(r"\s+", " ", text.lower())


def _ist_emoji(zeichen: str) -> bool:
    code = ord(zeichen)
    if unicodedata.category(zeichen) == "So":
        return True
    return any(start <= code <= ende for start, ende in regeln.EMOJI_BEREICHE)


def _signalwoerter(quelle: str) -> list[str]:
    """Eigennamen, Orte und Zahlen aus dem Input, an denen Personalisierung haengt."""
    signale: list[str] = []
    for wort in re.findall(r"\b[\wÄÖÜäöüß.-]{3,}\b", quelle):
        rein = wort.strip(".-")
        if not rein or rein.lower() in regeln.STOPP_WOERTER:
            continue
        if any(c.isdigit() for c in rein) or (rein[0].isupper() and len(rein) >= 4):
            signale.append(rein)
    # Reihenfolge erhalten, Duplikate entfernen
    return list(dict.fromkeys(signale))


def pruefe(
    text: str | Mail,
    *,
    region: str = "ch",
    quelle: str | None = None,
) -> list[Befund]:
    """Prueft eine Mail und liefert alle Befunde, schwerste zuerst."""
    mail = text if isinstance(text, Mail) else zerlege(text)
    befunde: list[Befund] = []

    def melde(schwere: str, regel: str, meldung: str) -> None:
        befunde.append(Befund(schwere, regel, meldung))

    roh = mail.roh
    flach = _normalisiert(roh)

    # --- Betreff ---------------------------------------------------------
    if not mail.betreff:
        melde(FEHLER, "Betreff", "Kein Betreff gefunden (erste Zeile 'Betreff: ...').")
    else:
        betreff_woerter = [w for w in mail.betreff.split() if w.strip()]
        if len(mail.betreff) > regeln.BETREFF_MAX_ZEICHEN:
            melde(
                WARNUNG,
                "Betreff",
                f"{len(mail.betreff)} Zeichen, maximal {regeln.BETREFF_MAX_ZEICHEN} "
                "(sonst auf dem Handy abgeschnitten).",
            )
        if not regeln.BETREFF_MIN_WOERTER <= len(betreff_woerter) <= regeln.BETREFF_MAX_WOERTER:
            melde(
                WARNUNG,
                "Betreff",
                f"{len(betreff_woerter)} Wörter, vorgesehen sind "
                f"{regeln.BETREFF_MIN_WOERTER} bis {regeln.BETREFF_MAX_WOERTER}.",
            )
        if "?" in mail.betreff or "!" in mail.betreff:
            melde(FEHLER, "Betreff", "Kein Frage- oder Ausrufezeichen im Betreff.")
        for verboten in regeln.BETREFF_VERBOTEN:
            if verboten in mail.betreff.lower():
                melde(FEHLER, "Betreff", f"Verbotenes Wort im Betreff: '{verboten}'.")

    # --- Anrede ----------------------------------------------------------
    if not mail.anrede:
        melde(FEHLER, "Anrede", "Keine Anrede gefunden.")
    if regeln.ANREDE_VERBOTEN in flach:
        melde(
            FEHLER,
            "Anrede",
            "'Sehr geehrte Damen und Herren' ist in der Kaltakquise verboten, "
            "Namen recherchieren oder Lücke markieren.",
        )

    # --- Einstieg --------------------------------------------------------
    erstes_wort = (mail.fliesstext.split() or [""])[0].strip(",.:;")
    if erstes_wort.lower() == "ich":
        melde(FEHLER, "Einstieg", "Der erste Satz darf nicht mit 'Ich' beginnen.")

    # --- Laenge ----------------------------------------------------------
    if not mail.fliesstext:
        melde(FEHLER, "Fliesstext", "Kein Fliesstext gefunden.")
    else:
        wortzahl = mail.wortzahl
        if wortzahl < regeln.FLIESSTEXT_MIN:
            melde(
                WARNUNG,
                "Länge",
                f"{wortzahl} Wörter Fliesstext, Ziel sind "
                f"{regeln.FLIESSTEXT_MIN} bis {regeln.FLIESSTEXT_MAX}.",
            )
        elif wortzahl > regeln.FLIESSTEXT_MAX:
            melde(
                FEHLER,
                "Länge",
                f"{wortzahl} Wörter Fliesstext, Maximum ist {regeln.FLIESSTEXT_MAX}. "
                "Kalt heisst kurz.",
            )

    # --- Grussformel und Signatur ----------------------------------------
    if not mail.gruss:
        melde(FEHLER, "Grussformel", "Keine Grussformel gefunden.")
    else:
        erwartet = regeln.GRUSSFORMELN.get(region)
        if erwartet and mail.gruss.lower() != erwartet.lower():
            melde(
                WARNUNG,
                "Grussformel",
                f"'{mail.gruss}' passt nicht zur Region '{region}', erwartet: '{erwartet}'.",
            )

    for zeile in regeln.SIGNATUR:
        if zeile.lower() not in flach:
            melde(FEHLER, "Signatur", f"Signaturzeile fehlt: '{zeile}'.")

    # --- Sprachregister --------------------------------------------------
    if region in ("ch", "fr", "it") and "ß" in roh:
        melde(FEHLER, "Orthografie", "Schweizer Empfänger: ss statt ß.")

    # --- Preise ----------------------------------------------------------
    for treffer in regeln.PREIS_MUSTER.finditer(roh):
        melde(
            FEHLER,
            "Preise",
            f"Preisangabe im Erstkontakt: '{treffer.group(0).strip()}'.",
        )

    # --- Verfuegbarkeit --------------------------------------------------
    for satz in re.split(r"(?<=[.!?])\s+", roh):
        treffer = regeln.VERFUEGBARKEIT_MUSTER.search(satz)
        if treffer and not regeln.VERFUEGBARKEIT_ERLAUBT.search(satz):
            melde(
                FEHLER,
                "Verfügbarkeit",
                f"Verfügbarkeit zugesagt ohne Freigabe: '{treffer.group(0).strip()}'.",
            )

    # --- KI-Marker -------------------------------------------------------
    for marker in regeln.KI_MARKER:
        if marker in flach:
            melde(FEHLER, "KI-Marker", f"Blacklist-Formulierung: '{marker}'.")

    # --- Superlative -----------------------------------------------------
    for treffer in regeln.SUPERLATIVE.finditer(roh):
        melde(
            WARNUNG,
            "Superlativ",
            f"Superlativ ohne Beleg: '{treffer.group(0)}'. "
            "Erlaubt ist nur die Tatsachenbehauptung 'als einziger Vermieter'.",
        )

    # --- Formatierung ----------------------------------------------------
    if regeln.GEDANKENSTRICH.search(roh):
        melde(FEHLER, "Formatierung", "Gedankenstriche sind als Stilmittel verboten.")
    if regeln.MARKDOWN_MUSTER.search(roh):
        melde(FEHLER, "Formatierung", "Kein Markdown im Mailtext (**, __, #).")
    for zeile in mail.fliesstext.split("\n"):
        if regeln.BULLET_ZEILE.match(zeile):
            melde(
                FEHLER,
                "Formatierung",
                f"Aufzählung im Mailtext, Kaltakquise ist Fliesstext: '{zeile.strip()[:40]}'.",
            )
            break
    emojis = sorted({z for z in roh if _ist_emoji(z)})
    if emojis:
        melde(FEHLER, "Formatierung", f"Emojis im Mailtext: {' '.join(emojis)}.")

    # --- Normen ----------------------------------------------------------
    voll = regeln.NORM_IEC_VOLL.search(roh)
    kurz = regeln.NORM_IEC_KURZ.search(roh)
    klasse_a = regeln.NORM_KLASSE_A.search(roh)
    if kurz and not voll:
        melde(
            FEHLER,
            "Normen",
            "IEC 61000-4-30 beim ersten Nennen unvollständig, korrekt ist "
            "'IEC 61000-4-30 Klasse A'.",
        )
    if klasse_a and voll and klasse_a.start() < voll.start():
        melde(
            FEHLER,
            "Normen",
            "'Klasse A' steht vor der vollständigen Nennung von IEC 61000-4-30 Klasse A.",
        )
    if klasse_a and not kurz:
        melde(
            FEHLER,
            "Normen",
            "'Klasse A' ohne Norm-Bezug, beim ersten Nennen IEC 61000-4-30 ausschreiben.",
        )

    # --- Einheiten -------------------------------------------------------
    for treffer in regeln.EINHEIT_FALSCH.finditer(roh):
        melde(
            FEHLER,
            "Einheiten",
            f"Falsche Einheitenschreibweise: '{treffer.group(0)}' "
            "(kVA, kW, kWh, MVA sauber trennen).",
        )

    # --- Fachkuerzel -----------------------------------------------------
    for kuerzel, aufloesung in regeln.KUERZEL.items():
        if re.search(rf"\b{kuerzel}\b", roh) and aufloesung.lower() not in flach:
            melde(
                WARNUNG,
                "Fachkürzel",
                f"'{kuerzel}' wird nicht aufgelöst, beim ersten Nennen "
                f"'{aufloesung}' ausschreiben.",
            )

    # --- Call-to-Action --------------------------------------------------
    if mail.fliesstext:
        if not regeln.CTA_SIGNALE.search(mail.fliesstext):
            melde(
                FEHLER,
                "Call-to-Action",
                "Kein konkreter nächster Schritt erkennbar (Zeitfenster, Frage "
                "oder konkretes Angebot).",
            )
        schwach = regeln.CTA_SCHWACH.search(mail.fliesstext)
        if schwach:
            melde(
                FEHLER,
                "Call-to-Action",
                f"Weicher Abschluss statt konkretem Schritt: '{schwach.group(0)}'.",
            )

    # --- Luecken ---------------------------------------------------------
    for treffer in regeln.LUECKE_MUSTER.finditer(roh):
        melde(
            HINWEIS,
            "Lücke",
            f"Markierte Lücke vor dem Versand füllen: '{treffer.group(0)}'.",
        )

    # --- Personalisierung ------------------------------------------------
    if quelle:
        signale = _signalwoerter(quelle)
        getroffen = [s for s in signale if s.lower() in flach]
        if signale and not getroffen:
            melde(
                FEHLER,
                "Personalisierung",
                "Kein einziges Detail aus dem Input in der Mail. Diese Mail könnte "
                "an jede andere Firma gehen.",
            )
        elif len(signale) >= 4 and len(getroffen) < 2:
            melde(
                WARNUNG,
                "Personalisierung",
                f"Nur ein Detail aus dem Input übernommen ({getroffen[0]}). "
                "Spezifischer werden.",
            )

    befunde.sort(key=lambda b: (_RANG[b.schwere], b.regel))
    return befunde


def hat_fehler(befunde: list[Befund]) -> bool:
    return any(b.schwere == FEHLER for b in befunde)


def bilanz(befunde: list[Befund]) -> str:
    zahl = {FEHLER: 0, WARNUNG: 0, HINWEIS: 0}
    for b in befunde:
        zahl[b.schwere] += 1
    return (
        f"{zahl[FEHLER]} Fehler, {zahl[WARNUNG]} Warnungen, {zahl[HINWEIS]} Hinweise"
    )
