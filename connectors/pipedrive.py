#!/usr/bin/env python3
"""Pipedrive-Sync: erzeugt Organizations + Persons + (optional) Deals.

Setup:
    export PIPEDRIVE_TOKEN=xxxxxxxxxxxxxxxx
    export PIPEDRIVE_DOMAIN=mycompany     # https://mycompany.pipedrive.com

Nutzung:
    python -m connectors.pipedrive kunden.xlsx --prio A --create-deals
    python -m connectors.pipedrive kunden.xlsx --dry-run

Idempotenz: Organizations werden per exact-name match gesucht.
"""
from __future__ import annotations

import os
import sys
import time

from .common import Row, load_rows, parse_args_base

PRIO_LABEL = {"A": 1, "B": 2, "C": 3}


def main() -> int:
    ap = parse_args_base("Pipedrive-Sync für MiT-CRM-Listen")
    ap.add_argument("--create-deals", action="store_true",
                    help="Aus jeder Zeile mit Wert > 0 einen Deal anlegen")
    args = ap.parse_args()

    token = os.environ.get("PIPEDRIVE_TOKEN")
    domain = os.environ.get("PIPEDRIVE_DOMAIN", "api")
    if not token and not args.dry_run:
        print("ENV PIPEDRIVE_TOKEN/PIPEDRIVE_DOMAIN setzen oder --dry-run.",
              file=sys.stderr)
        return 2

    try:
        import requests
    except ImportError:
        print("requests fehlt (pip install requests).", file=sys.stderr)
        return 2

    base = f"https://{domain}.pipedrive.com/api/v1"
    s = requests.Session() if token else None
    auth = {"api_token": token} if token else {}

    rows = load_rows(args.file, only_prio=args.prio, only_status=args.status,
                     only_segment=args.segment)
    if args.limit:
        rows = rows[:args.limit]
    print(f"{len(rows)} Datensätze zu syncen …")

    def find_org(name: str):
        r = s.get(f"{base}/organizations/search",
                  params={**auth, "term": name, "exact_match": "true"},
                  timeout=15)
        items = r.json().get("data", {}).get("items", []) if r.status_code == 200 else []
        return items[0]["item"]["id"] if items else None

    def find_person(email: str):
        r = s.get(f"{base}/persons/search",
                  params={**auth, "term": email, "fields": "email"},
                  timeout=15)
        items = r.json().get("data", {}).get("items", []) if r.status_code == 200 else []
        return items[0]["item"]["id"] if items else None

    for i, row in enumerate(rows, 1):
        if args.dry_run:
            print(f"  [dry] {row.firma} ({row.email or '—'}) "
                  f"Wert={row.wert_chf} Wahrsch={row.wahrscheinlichkeit}")
            continue

        # Organization
        oid = find_org(row.firma)
        org_payload = {
            "name": row.firma,
            "address": f"{row.ort or ''} {row.plz or ''} {row.kanton or ''}".strip(),
            "label_ids": [PRIO_LABEL[row.prio]] if row.prio in PRIO_LABEL else [],
        }
        if oid:
            s.put(f"{base}/organizations/{oid}", params=auth,
                  json=org_payload, timeout=15)
        else:
            r = s.post(f"{base}/organizations", params=auth,
                       json=org_payload, timeout=15)
            oid = r.json().get("data", {}).get("id")

        # Person
        pid = None
        if row.email:
            pid = find_person(row.email)
            person_payload = {
                "name": row.ansprechpartner or row.email.split("@")[0],
                "email": [{"value": row.email, "primary": "true"}],
                "phone": [{"value": row.telefon, "primary": "true"}] if row.telefon else [],
                "org_id": oid,
                "job_title": row.funktion or "",
            }
            if pid:
                s.put(f"{base}/persons/{pid}", params=auth,
                      json=person_payload, timeout=15)
            else:
                r = s.post(f"{base}/persons", params=auth,
                           json=person_payload, timeout=15)
                pid = r.json().get("data", {}).get("id")

        # Deal
        if args.create_deals and row.wert_chf:
            deal_payload = {
                "title": f"{row.firma} — {row.hauptprodukt or 'Opportunity'}",
                "value": row.wert_chf,
                "currency": "CHF",
                "probability": row.wahrscheinlichkeit or 10,
                "org_id": oid,
                "person_id": pid,
            }
            s.post(f"{base}/deals", params=auth, json=deal_payload, timeout=15)

        time.sleep(0.1)
        if i % 25 == 0:
            print(f"  … {i}/{len(rows)}")
    print("Fertig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
