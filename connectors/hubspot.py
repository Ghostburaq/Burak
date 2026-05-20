#!/usr/bin/env python3
"""HubSpot-Sync: legt Companies + Contacts aus MiT-CRM Vorlage an.

Setup:
    export HUBSPOT_TOKEN=pat-na1-xxx   # Private App Access Token

Nutzung:
    python -m connectors.hubspot kunden.xlsx --dry-run
    python -m connectors.hubspot kunden.xlsx --prio A --limit 50

Idempotenz: Firma wird per Name gesucht (Suche /crm/v3/objects/companies/search),
existierende Companies werden geupdated, neue angelegt. Gleiches für Contacts
per E-Mail.
"""
from __future__ import annotations

import os
import sys
import time

from .common import Row, load_rows, parse_args_base

API = "https://api.hubapi.com"


def _client(token: str):
    import requests
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}",
                      "Content-Type": "application/json"})
    return s


def find_company(s, name: str):
    body = {"filterGroups": [{"filters": [
        {"propertyName": "name", "operator": "EQ", "value": name}
    ]}], "properties": ["name"], "limit": 1}
    r = s.post(f"{API}/crm/v3/objects/companies/search", json=body, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("results"):
        return data["results"][0]["id"]
    return None


def upsert_company(s, row: Row, dry_run: bool) -> str | None:
    props = {
        "name": row.firma,
        "city": row.ort or "",
        "zip": str(row.plz or ""),
        "state": row.kanton or "",
        "country": "Switzerland",
        "industry": row.segment or "",
        "website": row.website or "",
        "phone": row.telefon or "",
        "description": row.notizen or "",
        "hs_lead_status": row.status or "OPEN",
        "mit_prio": row.prio or "",
        "mit_segment": row.segment or "",
        "mit_hauptprodukt": row.hauptprodukt or "",
    }
    if dry_run:
        print(f"  [dry] company upsert: {row.firma}")
        return None
    cid = find_company(s, row.firma)
    if cid:
        s.patch(f"{API}/crm/v3/objects/companies/{cid}",
                json={"properties": props}, timeout=15)
    else:
        r = s.post(f"{API}/crm/v3/objects/companies",
                   json={"properties": props}, timeout=15)
        if r.status_code in (200, 201):
            cid = r.json()["id"]
    return cid


def upsert_contact(s, row: Row, company_id: str | None, dry_run: bool):
    if not row.email:
        return
    name_parts = (row.ansprechpartner or "").strip().split(" ", 1)
    first = name_parts[0] if name_parts else ""
    last = name_parts[1] if len(name_parts) > 1 else ""
    props = {
        "email": row.email,
        "firstname": first,
        "lastname": last,
        "jobtitle": row.funktion or "",
        "phone": row.telefon or "",
        "company": row.firma,
    }
    if dry_run:
        print(f"  [dry] contact upsert: {row.email}")
        return
    r = s.post(f"{API}/crm/v3/objects/contacts",
               json={"properties": props}, timeout=15)
    if r.status_code == 409:
        # Existiert — Update via E-Mail-Lookup
        rg = s.get(f"{API}/crm/v3/objects/contacts/{row.email}",
                   params={"idProperty": "email"}, timeout=15)
        if rg.status_code == 200:
            cid = rg.json()["id"]
            s.patch(f"{API}/crm/v3/objects/contacts/{cid}",
                    json={"properties": props}, timeout=15)
            if company_id:
                s.put(f"{API}/crm/v3/objects/contacts/{cid}/associations/"
                      f"companies/{company_id}/contact_to_company", timeout=15)


def main() -> int:
    ap = parse_args_base("HubSpot-Sync für MiT-CRM-Listen")
    args = ap.parse_args()
    token = os.environ.get("HUBSPOT_TOKEN")
    if not token and not args.dry_run:
        print("ENV HUBSPOT_TOKEN fehlt. Setze ihn oder nutze --dry-run.",
              file=sys.stderr)
        return 2
    try:
        s = _client(token) if token else None
    except ImportError:
        print("requests fehlt (pip install requests).", file=sys.stderr)
        return 2

    rows = load_rows(args.file, only_prio=args.prio, only_status=args.status,
                     only_segment=args.segment)
    if args.limit:
        rows = rows[:args.limit]
    print(f"{len(rows)} Datensätze zu syncen …")
    for i, row in enumerate(rows, 1):
        cid = upsert_company(s, row, args.dry_run)
        upsert_contact(s, row, cid, args.dry_run)
        if not args.dry_run:
            time.sleep(0.12)  # ~8 req/s, HubSpot limit ~10/s
        if i % 25 == 0:
            print(f"  … {i}/{len(rows)}")
    print("Fertig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
