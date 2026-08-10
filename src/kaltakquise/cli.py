"""
Kommandozeile der Kaltakquise-Maschine.

  mail     Input rein, geprüfte Mail raus (braucht API-Zugang)
  pruefen  Bestehenden Mailtext gegen das Regelwerk prüfen (offline)
  prompt   Systemprompt ausgeben
"""
from __future__ import annotations

import argparse
import json
import sys

from . import client, pruefer
from .mail import zerlege

BEFEHLE = {"mail", "pruefen", "prompt"}


def _lies_eingabe(text: str | None, datei: str | None) -> str:
    if datei:
        if datei == "-":
            return sys.stdin.read()
        with open(datei, encoding="utf-8") as f:
            return f.read()
    if text:
        return text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def _befund_json(b: pruefer.Befund) -> dict:
    return {"schwere": b.schwere, "regel": b.regel, "text": b.text}


def _drucke_bericht(name: str, befunde: list[pruefer.Befund]) -> None:
    kopf = f"{name}: {pruefer.bilanz(befunde)}"
    print(kopf)
    print("-" * len(kopf))
    if not befunde:
        print("Keine Beanstandungen.")
    for b in befunde:
        print(f"  {b}")
    print()


# ---- Befehl: mail --------------------------------------------------------
def befehl_mail(args: argparse.Namespace) -> int:
    quelle = _lies_eingabe(args.text, args.datei)
    if not quelle.strip():
        print("Kein Input. Text als Argument, über --datei oder per stdin übergeben.",
              file=sys.stderr)
        return 2

    try:
        ergebnis = client.erzeuge(
            quelle,
            region=args.region,
            modell=args.modell,
            effort=args.effort,
            runden=args.runden,
        )
    except client.GeneratorFehler as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "ausgabe": ergebnis.ausgabe,
                    "runden": ergebnis.runden,
                    "sauber": ergebnis.sauber,
                    "tokens": {
                        "input": ergebnis.input_tokens,
                        "output": ergebnis.output_tokens,
                        "cache_read": ergebnis.cache_read_tokens,
                    },
                    "varianten": [
                        {
                            "name": v.name,
                            "text": v.text,
                            "befunde": [_befund_json(b) for b in v.befunde],
                        }
                        for v in ergebnis.varianten
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if ergebnis.sauber else 1

    print(ergebnis.ausgabe)
    print()
    print("=" * 72)
    print(f"PRÜFBERICHT (Runden: {ergebnis.runden}, Modell: {args.modell})")
    print("=" * 72)
    print()
    if not ergebnis.varianten:
        print("Keine Varianten erkannt, Ausgabeformat prüfen.")
        return 1
    for v in ergebnis.varianten:
        _drucke_bericht(v.name, v.befunde)

    if ergebnis.sauber:
        print("Beide Varianten sind regelkonform und sendefertig.")
        return 0
    print("Es sind Fehler offen. Vor dem Versand korrigieren.")
    return 1


# ---- Befehl: pruefen -----------------------------------------------------
def befehl_pruefen(args: argparse.Namespace) -> int:
    text = _lies_eingabe(args.text, args.datei)
    if not text.strip():
        print("Kein Mailtext. Datei angeben oder Text per stdin übergeben.", file=sys.stderr)
        return 2

    quelle = None
    if args.quelle:
        with open(args.quelle, encoding="utf-8") as f:
            quelle = f.read()

    befunde = pruefer.pruefe(text, region=args.region, quelle=quelle)

    if args.json:
        print(
            json.dumps(
                {
                    "sauber": not pruefer.hat_fehler(befunde),
                    "befunde": [_befund_json(b) for b in befunde],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1 if pruefer.hat_fehler(befunde) else 0

    mail = zerlege(text)
    print(f"Betreff: {mail.betreff or '(fehlt)'}")
    print(f"Fliesstext: {mail.wortzahl} Wörter")
    print()
    _drucke_bericht("Prüfung", befunde)
    return 1 if pruefer.hat_fehler(befunde) else 0


# ---- Befehl: prompt ------------------------------------------------------
def befehl_prompt(args: argparse.Namespace) -> int:
    try:
        print(client.lies_prompt())
    except client.GeneratorFehler as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 2
    return 0


def baue_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kaltakquise",
        description="Kaltakquise-Maschine: Input rein, geprüfte Mail raus.",
    )
    unter = p.add_subparsers(dest="befehl", required=True)

    m = unter.add_parser("mail", help="Mail erzeugen und prüfen")
    m.add_argument("text", nargs="?", help="Input als Text (LinkedIn, News, Firmenname)")
    m.add_argument("-d", "--datei", help="Input aus Datei, '-' für stdin")
    m.add_argument("-r", "--region", default="ch", choices=sorted(client.REGIONEN),
                   help="Sprachregister (Standard: ch)")
    m.add_argument("--modell", default=client.MODELL, help="Modell-ID")
    m.add_argument("--effort", default="high",
                   choices=["low", "medium", "high", "xhigh", "max"],
                   help="Denktiefe (Standard: high)")
    m.add_argument("--runden", type=int, default=2,
                   help="Maximale Korrekturrunden bei Regelverstössen (Standard: 2)")
    m.add_argument("--json", action="store_true", help="Maschinenlesbare Ausgabe")
    m.set_defaults(fn=befehl_mail)

    v = unter.add_parser("pruefen", help="Bestehenden Mailtext prüfen (offline)")
    v.add_argument("datei", nargs="?", help="Datei mit dem Mailtext, '-' für stdin")
    v.add_argument("--text", help="Mailtext direkt als Argument")
    v.add_argument("-r", "--region", default="ch", choices=sorted(client.REGIONEN))
    v.add_argument("-q", "--quelle", help="Datei mit dem Input, prüft die Personalisierung")
    v.add_argument("--json", action="store_true", help="Maschinenlesbare Ausgabe")
    v.set_defaults(fn=befehl_pruefen)

    s = unter.add_parser("prompt", help="Systemprompt ausgeben")
    s.set_defaults(fn=befehl_prompt)

    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # Ohne Befehl gilt der Normalfall: Input rein, Mail raus.
    if argv and argv[0] not in BEFEHLE and not argv[0].startswith("-"):
        argv.insert(0, "mail")
    elif not argv:
        argv = ["mail"]

    args = baue_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
