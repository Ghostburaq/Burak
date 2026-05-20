#!/usr/bin/env python3
"""Airtable-Sync: schreibt Kunden in eine Airtable Base.

Setup:
    export AIRTABLE_TOKEN=patXXXXXXXXXX
    export AIRTABLE_BASE=appXXXXXXXXXX
    export AIRTABLE_TABLE=Kunden          # Tab-Name in Airtable

Nutzung:
    python -m connectors.airtable kunden.xlsx --dry-run
    python -m connectors.airtable kunden.xlsx --prio A

Idempotenz: Match per Feld 'Firma' (lege Feld an, falls fehlt).
Bulk-Upsert in Batches à 10 (Airtable API-Limit).
"""
from __future__ import annotations

import os
import sys
import time

from .common import Row, load_rows, parse_args_base

API = "https://api.airtable.com/v0"


def row_to_fields(row: Row) -> dict:
    return {
        "Firma": row.firma,
        "Prio": row.prio,
        "Segment": row.segment,
        "Ort": row.ort,
        "PLZ": str(row.plz) if row.plz is not None else None,
        "Kanton": row.kanton,
        "Ansprechpartner": row.ansprechpartner,
        "Funktion": row.funktion,
        "E-Mail": row.email,
        "Telefon": row.telefon,
        "Website": row.website,
        "Status": row.status,
        "Hauptprodukt": row.hauptprodukt,
        "Notizen": row.notizen,
        "Wahrscheinlichkeit %": row.wahrscheinlichkeit,
        "Wert CHF": row.wert_chf,
    }


def main() -> int:
    ap = parse_args_base("Airtable-Sync für MiT-CRM-Listen")
    args = ap.parse_args()

    token = os.environ.get("AIRTABLE_TOKEN")
    base = os.environ.get("AIRTABLE_BASE")
    table = os.environ.get("AIRTABLE_TABLE", "Kunden")
    if not (token and base) and not args.dry_run:
        print("ENV AIRTABLE_TOKEN/AIRTABLE_BASE setzen oder --dry-run.",
              file=sys.stderr)
        return 2

    try:
        import requests
    except ImportError:
        print("requests fehlt (pip install requests).", file=sys.stderr)
        return 2

    rows = load_rows(args.file, only_prio=args.prio, only_status=args.status,
                     only_segment=args.segment)
    if args.limit:
        rows = rows[:args.limit]
    print(f"{len(rows)} Datensätze zu syncen …")

    if args.dry_run:
        for row in rows[:5]:
            print(f"  [dry] {row_to_fields(row)}")
        if len(rows) > 5:
            print(f"  … ({len(rows)} total)")
        return 0

    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}",
                      "Content-Type": "application/json"})
    url = f"{API}/{base}/{table}"
    batch = []
    sent = 0
    for row in rows:
        batch.append({"fields": {k: v for k, v in row_to_fields(row).items()
                                  if v is not None}})
        if len(batch) == 10:
            r = s.patch(url, json={"performUpsert":
                                   {"fieldsToMergeOn": ["Firma"]},
                                   "records": batch}, timeout=30)
            if r.status_code >= 300:
                print(f"  ! Fehler {r.status_code}: {r.text[:200]}",
                      file=sys.stderr)
            sent += len(batch)
            batch = []
            time.sleep(0.25)  # 5 req/s
    if batch:
        s.patch(url, json={"performUpsert":
                           {"fieldsToMergeOn": ["Firma"]},
                           "records": batch}, timeout=30)
        sent += len(batch)
    print(f"Synced {sent} Records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
