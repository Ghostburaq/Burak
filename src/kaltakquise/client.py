"""
Anbindung an die Claude API.

Der Systemprompt kommt unveraendert aus prompts/CLAUDE_Kaltakquise_Maschine.md.
Nach jeder Antwort laeuft der Pruefer; findet er Fehler, geht die Mail mit den
Befunden zurueck ans Modell, bis sie sauber ist oder die Runden aufgebraucht sind.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from .mail import extrahiere_varianten
from .pruefer import Befund, hat_fehler, pruefe

MODELL = "claude-opus-5"
MAX_TOKENS = 16000

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROMPT_PFAD = os.path.join(ROOT, "prompts", "CLAUDE_Kaltakquise_Maschine.md")

REGIONEN = {
    "ch": "Deutschschweiz, Hochdeutsch, Sie-Form, ss statt ß",
    "de": "Deutschland, Hochdeutsch, Sie-Form, ß nach deutscher Rechtschreibung",
    "at": "Österreich, Hochdeutsch, Sie-Form, ß nach deutscher Rechtschreibung",
    "fr": "Romandie, Französisch, vous-Form",
    "it": "Tessin, Italienisch, Lei-Form",
    "en": "Internationaler Empfänger, englische Fassung",
}


class GeneratorFehler(RuntimeError):
    """Alles, was den Generator stoppt, mit einer Meldung für die Konsole."""


@dataclass
class Variante:
    name: str
    text: str
    befunde: list[Befund] = field(default_factory=list)


@dataclass
class Ergebnis:
    ausgabe: str
    varianten: list[Variante]
    runden: int
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0

    @property
    def sauber(self) -> bool:
        return bool(self.varianten) and not any(hat_fehler(v.befunde) for v in self.varianten)


def lies_prompt(pfad: str = PROMPT_PFAD) -> str:
    try:
        with open(pfad, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        raise GeneratorFehler(f"Systemprompt nicht gefunden: {pfad}") from e


def _client():
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover - Umgebungsfrage
        raise GeneratorFehler(
            "Das Paket 'anthropic' fehlt. Installation: pip install anthropic"
        ) from e
    try:
        return anthropic.Anthropic()
    except Exception as e:  # pragma: no cover - Umgebungsfrage
        raise GeneratorFehler(
            "Kein API-Zugang gefunden. ANTHROPIC_API_KEY setzen oder 'ant auth login' "
            f"ausführen. Ursprüngliche Meldung: {e}"
        ) from e


_AUTH_SIGNALE = ("authentication", "api_key", "auth_token", "credentials", "401")


def _uebersetze(e: Exception) -> GeneratorFehler:
    meldung = str(e)
    if any(s in meldung.lower() for s in _AUTH_SIGNALE):
        return GeneratorFehler(
            "Kein API-Zugang gefunden. ANTHROPIC_API_KEY setzen oder 'ant auth login' "
            "ausführen. Offline funktioniert weiterhin: kaltakquise.py pruefen <datei>"
        )
    return GeneratorFehler(f"API-Aufruf fehlgeschlagen: {meldung}")


def _text_aus(antwort) -> str:
    return "\n".join(b.text for b in antwort.content if b.type == "text").strip()


def _auftrag(quelle: str, region: str) -> str:
    return (
        f"Sprachregister: {REGIONEN.get(region, REGIONEN['ch'])}.\n\n"
        "Input:\n"
        "<<<\n"
        f"{quelle.strip()}\n"
        ">>>"
    )


def _korrekturauftrag(varianten: list[Variante]) -> str:
    zeilen = [
        "Die Prüfung gegen das Regelwerk hat Verstösse gefunden. "
        "Schreibe beide Varianten neu, bis alle Punkte erfüllt sind.",
        "",
    ]
    for v in varianten:
        fehler = [b for b in v.befunde if b.schwere == "fehler"]
        if not fehler:
            continue
        zeilen.append(f"{v.name}:")
        zeilen += [f"- {b.regel}: {b.text}" for b in fehler]
        zeilen.append("")
    zeilen.append(
        "Gib erneut die vollständige Ausgabe im festgelegten Format aus. "
        "Keine Erklärung, was du geändert hast."
    )
    return "\n".join(zeilen)


def erzeuge(
    quelle: str,
    *,
    region: str = "ch",
    modell: str = MODELL,
    effort: str = "high",
    runden: int = 2,
    prompt_pfad: str = PROMPT_PFAD,
    klient=None,
) -> Ergebnis:
    """Erzeugt eine geprüfte Kaltakquise-Mail zum Input."""
    if not quelle.strip():
        raise GeneratorFehler("Leerer Input.")

    client = klient or _client()
    systemprompt = lies_prompt(prompt_pfad)
    nachrichten: list[dict] = [{"role": "user", "content": _auftrag(quelle, region)}]

    ergebnis = Ergebnis(ausgabe="", varianten=[], runden=0)

    for runde in range(1, max(1, runden) + 1):
        try:
            antwort = client.messages.create(
                model=modell,
                max_tokens=MAX_TOKENS,
                system=[
                    {
                        "type": "text",
                        "text": systemprompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                thinking={"type": "adaptive"},
                output_config={"effort": effort},
                messages=nachrichten,
            )
        except GeneratorFehler:
            raise
        except Exception as e:  # SDK-Fehler in eine lesbare Meldung übersetzen
            raise _uebersetze(e) from e

        if antwort.stop_reason == "refusal":
            raise GeneratorFehler(
                "Die Anfrage wurde abgelehnt (stop_reason: refusal). Input prüfen."
            )

        ausgabe = _text_aus(antwort)
        varianten = [
            Variante(name, text, pruefe(text, region=region, quelle=quelle))
            for name, text in extrahiere_varianten(ausgabe)
        ]

        ergebnis.ausgabe = ausgabe
        ergebnis.varianten = varianten
        ergebnis.runden = runde
        ergebnis.input_tokens += antwort.usage.input_tokens
        ergebnis.output_tokens += antwort.usage.output_tokens
        ergebnis.cache_read_tokens += getattr(antwort.usage, "cache_read_input_tokens", 0) or 0

        if not varianten:
            korrektur = (
                "Die Ausgabe enthielt keine erkennbaren Blöcke 'Variante A' und "
                "'Variante B'. Halte dich exakt an das vorgegebene Ausgabeformat."
            )
        elif ergebnis.sauber:
            break
        else:
            korrektur = _korrekturauftrag(varianten)

        if runde == max(1, runden):
            break

        nachrichten.append({"role": "assistant", "content": antwort.content})
        nachrichten.append({"role": "user", "content": korrektur})

    return ergebnis
