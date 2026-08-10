"""
Regelwerk der Kaltakquise-Maschine, maschinenlesbar.

Alles hier ist eine 1:1-Abbildung von prompts/CLAUDE_Kaltakquise_Maschine.md.
Wird der Prompt geaendert, gehoert die Aenderung auch hierher, sonst prueft
das Tool gegen ein anderes Regelwerk als das Modell schreibt.
"""
from __future__ import annotations

import re

# ---- KI-Marker-Blacklist -------------------------------------------------
# Kleingeschrieben, Vergleich erfolgt auf normalisiertem Kleintext.
KI_MARKER = [
    "ich hoffe, diese e-mail erreicht sie gut",
    "ich hoffe, diese email erreicht sie gut",
    "in der heutigen schnelllebigen zeit",
    "massgeschneiderte loesungen",
    "massgeschneiderte losungen",
    "massgeschneiderte lösungen",
    "maßgeschneiderte lösungen",
    "innovativ",
    "ganzheitlich",
    "synergien",
    "mehrwert",
    "gerne stehe ich für rückfragen zur verfügung",
    "gerne stehe ich fuer rueckfragen zur verfuegung",
    "zögern sie nicht",
    "zoegern sie nicht",
    "revolutionär",
    "revolutionaer",
    "einzigartige gelegenheit",
    "ich wollte mich kurz vorstellen",
    "lassen sie uns gemeinsam",
    "auf augenhöhe",
    "auf augenhoehe",
    "am ende des tages",
    "wir freuen uns auf ihre rückmeldung",
    "wir freuen uns auf ihre rueckmeldung",
    "als ihr verlässlicher partner",
    "als ihr verlaesslicher partner",
    "spannend",
    "spannende",
    "spannendes",
]

# ---- Signatur ------------------------------------------------------------
SIGNATUR = [
    "Burak Ücöz",
    "Sales Engineer Power",
    "Mobil in Time AG, An Aggreko Company",
    "+41 44 806 13 19",
    "burak.ucoez@mobilintime.ch",
]

# ---- Anrede und Grussformel ---------------------------------------------
ANREDE_MUSTER = re.compile(
    r"^\s*(guten tag|sehr geehrte[rs]?|bonjour|madame|monsieur|gentile|egregio|dear)\b",
    re.IGNORECASE,
)
ANREDE_VERBOTEN = "sehr geehrte damen und herren"

GRUSSFORMELN = {
    "ch": "Freundliche Grüsse",
    "de": "Mit freundlichen Grüßen",
    "at": "Mit freundlichen Grüßen",
    "fr": "Meilleures salutations",
    "it": "Cordiali saluti",
    "en": "Kind regards",
}
GRUSS_MUSTER = re.compile(
    r"^\s*(freundliche gr(ü|ue)sse|mit freundlichen gr(ü|ü|ue|u)(ss|ß)en"
    r"|meilleures salutations|cordiali saluti|kind regards|best regards)\s*$",
    re.IGNORECASE,
)

# ---- Betreff -------------------------------------------------------------
BETREFF_MAX_ZEICHEN = 50
BETREFF_MIN_WOERTER = 4
BETREFF_MAX_WOERTER = 8
BETREFF_VERBOTEN = ["angebot", "aw:", "re:", "fwd:", "wg:"]

# ---- Laenge --------------------------------------------------------------
FLIESSTEXT_MIN = 90
FLIESSTEXT_MAX = 150

# ---- Preise --------------------------------------------------------------
PREIS_MUSTER = re.compile(
    r"(chf|eur|€|fr\.|franken|euro)\s*[\d'’.,]+"
    r"|[\d'’.,]+\s*(chf|eur|€|franken|euro)"
    r"|\bpro\s+tag\s+(chf|eur)"
    r"|\btagesmiete\s+(von|ab|chf|eur)",
    re.IGNORECASE,
)

# ---- Verfuegbarkeit zusagen ---------------------------------------------
VERFUEGBARKEIT_MUSTER = re.compile(
    r"reservier\w*|\bKW\s?\d{1,2}\b|geblockt|halten wir für sie frei|garantier\w*",
    re.IGNORECASE,
)
VERFUEGBARKEIT_ERLAUBT = re.compile(
    r"kläre ich|klaere ich|innert 24|innerhalb von 24", re.IGNORECASE
)

# ---- Superlative ---------------------------------------------------------
SUPERLATIVE = re.compile(
    r"\b(beste[rsn]?|führend\w*|fuehrend\w*|weltweit|marktführer\w*|marktfuehrer\w*"
    r"|modernste[rsn]?|optimal\w*|perfekt\w*|einzigartig\w*)\b",
    re.IGNORECASE,
)

# ---- Normen und Einheiten ------------------------------------------------
NORM_IEC_VOLL = re.compile(r"IEC\s?61000-4-30\s+Klasse\s+A")
NORM_IEC_KURZ = re.compile(r"IEC\s?61000-4-30")
NORM_KLASSE_A = re.compile(r"\bKlasse\s+A\b")
NORM_EN = re.compile(r"EN\s?50160")

# Falschschreibungen der Einheiten. "KW" nur, wenn keine Kalenderwoche folgt.
EINHEIT_FALSCH = re.compile(r"\b(KVA|Kva|kva|KWH|Kwh|kwh|kwH|MVa|mva|Mw|mw)\b|\bKW\b(?!\s?\d)")

# ---- Fachkuerzel ---------------------------------------------------------
KUERZEL = {
    "BESS": "Batteriespeicher",
    "USV": "unterbrechungsfreie",
    "NEA": "Netzersatzanlage",
}

# ---- Call-to-Action ------------------------------------------------------
CTA_SIGNALE = re.compile(
    r"\?|ein wort genügt|ein wort genuegt|melde ich mich|schicke ich ihnen"
    r"|rufe ich sie|passt ihnen|hätten sie|haetten sie",
    re.IGNORECASE,
)
CTA_SCHWACH = re.compile(
    r"bei interesse|melden sie sich gerne|freue mich auf ihre antwort", re.IGNORECASE
)

# ---- Formatierung --------------------------------------------------------
GEDANKENSTRICH = re.compile(r"[–—]")
BULLET_ZEILE = re.compile(r"^\s*([-*•‣]|\d+[.)])\s+")
MARKDOWN_MUSTER = re.compile(r"\*\*|__|^#{1,6}\s", re.MULTILINE)
LUECKE_MUSTER = re.compile(r"\[[^\]]{2,}\]")

# Emoji- und Symbolbereiche (grob, deckt die gaengigen Bloecke ab).
EMOJI_BEREICHE = [
    (0x1F300, 0x1FAFF),
    (0x2600, 0x27BF),
    (0xFE0F, 0xFE0F),
    (0x2190, 0x21FF),
    (0x2B00, 0x2BFF),
]

# Woerter, die bei der Personalisierungspruefung nicht als Signal zaehlen.
STOPP_WOERTER = {
    "eine", "einer", "einem", "einen", "sich", "sind", "wird", "werden", "haben",
    "diese", "dieser", "dieses", "nicht", "auch", "aber", "oder", "wenn", "dann",
    "noch", "schon", "sehr", "mehr", "kann", "muss", "soll", "dass", "dass",
    "über", "unter", "nach", "beim", "vom", "zum", "zur", "durch", "gegen",
    "firma", "kunde", "kunden", "neue", "neuer", "neues", "grosse", "grosser",
}
