#!/usr/bin/env python3
"""mailer.py — Personalisierter E-Mail-Versand aus MiT-CRM-Listen.

Setup (Beispiel Outlook/Office365):
    export SMTP_HOST=smtp.office365.com
    export SMTP_PORT=587
    export SMTP_USER=verkauf@mobilintime.ch
    export SMTP_PASS=********
    export SMTP_FROM="Mobil in Time AG <verkauf@mobilintime.ch>"

Nutzung:
    python -m connectors.mailer kunden.xlsx \\
        --template templates/intro.txt --subject "Lösungen für {{segment}}" \\
        --prio A --limit 10 --dry-run
    python -m connectors.mailer kunden.xlsx \\
        --template templates/intro.html --html \\
        --status "Angebot gesendet"

Platzhalter im Template / Subject:
    {{firma}}              {{ansprechpartner}}    {{funktion}}
    {{segment}}            {{prio}}               {{status}}
    {{ort}} {{plz}} {{kanton}}
    {{hauptprodukt}}       {{bedarf}}
    {{wahrscheinlichkeit}} {{wert_chf}}
"""
from __future__ import annotations

import os
import re
import smtplib
import sys
import time
from email.message import EmailMessage
from pathlib import Path

from .common import Row, load_rows, parse_args_base


def render(template: str, row: Row) -> str:
    mapping = {
        "firma": row.firma or "",
        "ansprechpartner": row.ansprechpartner or "Sehr geehrte Damen und Herren",
        "funktion": row.funktion or "",
        "segment": row.segment or "",
        "prio": row.prio or "",
        "status": row.status or "",
        "ort": row.ort or "",
        "plz": str(row.plz or ""),
        "kanton": row.kanton or "",
        "hauptprodukt": row.hauptprodukt or "",
        "bedarf": row.bedarf or "",
        "wahrscheinlichkeit": str(row.wahrscheinlichkeit or ""),
        "wert_chf": f"{row.wert_chf:,.0f}".replace(",", "'") if row.wert_chf else "",
    }

    def repl(m):
        return mapping.get(m.group(1).strip().lower(), "")

    return re.sub(r"\{\{\s*([a-zA-Z_]+)\s*\}\}", repl, template)


def send(host, port, user, pwd, from_addr, msg: EmailMessage) -> None:
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(user, pwd)
        smtp.send_message(msg)


def main() -> int:
    ap = parse_args_base("Personalisierter E-Mail-Versand")
    ap.add_argument("--template", required=True, help="Pfad zur Template-Datei")
    ap.add_argument("--subject", required=True, help="Betreff (Platzhalter erlaubt)")
    ap.add_argument("--html", action="store_true",
                    help="Template ist HTML statt Plain-Text")
    ap.add_argument("--cc", default="", help="Komma-getrennte CC-Adressen")
    ap.add_argument("--bcc", default="", help="Komma-getrennte BCC-Adressen")
    ap.add_argument("--delay", type=float, default=2.0,
                    help="Sekunden zwischen Mails (Schutz vor Spam-Triggern)")
    args = ap.parse_args()

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"Template nicht gefunden: {template_path}", file=sys.stderr)
        return 2
    template = template_path.read_text(encoding="utf-8")

    rows = load_rows(args.file, only_prio=args.prio, only_status=args.status,
                     only_segment=args.segment)
    rows = [r for r in rows if r.email]
    if args.limit:
        rows = rows[:args.limit]
    print(f"{len(rows)} Empfänger mit E-Mail.")

    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    pwd = os.environ.get("SMTP_PASS")
    from_addr = os.environ.get("SMTP_FROM", user or "")
    if not args.dry_run and not all([host, user, pwd, from_addr]):
        print("SMTP-ENV unvollständig. Setze SMTP_HOST/USER/PASS/FROM "
              "oder nutze --dry-run.", file=sys.stderr)
        return 2

    sent_n = 0
    for row in rows:
        subject = render(args.subject, row)
        body = render(template, row)

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = row.email
        if args.cc:
            msg["Cc"] = args.cc
        if args.bcc:
            msg["Bcc"] = args.bcc
        if args.html:
            msg.set_content("Diese E-Mail benötigt einen HTML-fähigen Client.")
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        if args.dry_run:
            print(f"  [dry] → {row.email} | {subject}")
            print(f"        {body[:120]}…")
        else:
            try:
                send(host, port, user, pwd, from_addr, msg)
                sent_n += 1
                print(f"  ✓ {row.email}")
            except Exception as e:
                print(f"  ✗ {row.email}: {e}", file=sys.stderr)
            time.sleep(args.delay)

    print(f"Fertig. Gesendet: {sent_n}, Empfänger gesamt: {len(rows)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
