#!/usr/bin/env python3
"""geocode.py — Reverse-Geocoding für Schweizer PLZ/Ort → Lat/Lng.

Nutzung:
    python geocode.py kunden.xlsx
    python geocode.py kunden.xlsx --out kunden_geo.xlsx --limit 100
    python geocode.py kunden.xlsx --offline       # nur eingebauter Cache, keine API

Quellen:
    1. Lokaler Cache (geocode_cache.json, im Repo persistiert)
    2. Kanton-Hauptort-Fallback (eingebaute Lookup-Tabelle)
    3. Nominatim/OpenStreetMap (frei, kein API-Key, Rate-Limit 1 req/s)

Ergebnis: Spalten 'Lat' und 'Lng' werden in der Datei angefügt
(falls nicht vorhanden). Power BI / Google MyMaps lesen das direkt ein.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import openpyxl

CACHE_PATH = Path(__file__).with_name("geocode_cache.json")
USER_AGENT = "MiT-CRM-Geocoder/1.0 (contact@mobilintime.ch)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Kanton-Hauptorte als Offline-Fallback (Lat, Lng)
KANTON_CENTERS: dict[str, tuple[float, float]] = {
    "ZH": (47.3769, 8.5417),  "BE": (46.9480, 7.4474),
    "LU": (47.0502, 8.3093),  "UR": (46.8721, 8.6356),
    "SZ": (47.0207, 8.6531),  "OW": (46.8980, 8.2435),
    "NW": (46.9590, 8.3826),  "GL": (47.0405, 9.0680),
    "ZG": (47.1662, 8.5155),  "FR": (46.8065, 7.1615),
    "SO": (47.2088, 7.5323),  "BS": (47.5596, 7.5886),
    "BL": (47.4848, 7.7327),  "SH": (47.6970, 8.6346),
    "AR": (47.3791, 9.2790),  "AI": (47.3334, 9.4118),
    "SG": (47.4245, 9.3767),  "GR": (46.6500, 9.5780),
    "AG": (47.3927, 8.0444),  "TG": (47.5586, 9.0556),
    "TI": (46.1944, 9.0167),  "VD": (46.5197, 6.6323),
    "VS": (46.2280, 7.3596),  "NE": (46.9900, 6.9293),
    "GE": (46.2044, 6.1432),  "JU": (47.3650, 7.3431),
}


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2,
                                    sort_keys=True), encoding="utf-8")


def cache_key(plz: str | int | None, ort: str | None, kanton: str | None) -> str:
    return f"{str(plz or '').strip()}|{str(ort or '').strip().lower()}|{str(kanton or '').strip().upper()}"


def query_nominatim(plz, ort, kanton, session) -> tuple[float, float] | None:
    parts = []
    if plz:
        parts.append(str(plz))
    if ort:
        parts.append(str(ort))
    if kanton:
        parts.append(str(kanton))
    parts.append("Switzerland")
    q = ", ".join(parts)
    try:
        r = session.get(NOMINATIM_URL, params={
            "q": q, "format": "json", "limit": 1, "countrycodes": "ch"
        }, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        return None


def geocode_row(plz, ort, kanton, cache, session, offline=False):
    key = cache_key(plz, ort, kanton)
    if key in cache:
        return cache[key], "cache"
    if not offline and session is not None:
        coords = query_nominatim(plz, ort, kanton, session)
        time.sleep(1.05)  # rate limit
        if coords:
            cache[key] = list(coords)
            return list(coords), "nominatim"
    if kanton in KANTON_CENTERS:
        coords = list(KANTON_CENTERS[kanton])
        cache[key] = coords
        return coords, "fallback"
    return None, "none"


def ensure_columns(ws, header_row=3):
    headers = [ws.cell(row=header_row, column=c).value
               for c in range(1, ws.max_column + 1)]
    cols = {h: i + 1 for i, h in enumerate(headers) if h}
    next_col = ws.max_column + 1
    if "Lat" not in cols:
        ws.cell(row=header_row, column=next_col, value="Lat")
        cols["Lat"] = next_col
        next_col += 1
    if "Lng" not in cols:
        ws.cell(row=header_row, column=next_col, value="Lng")
        cols["Lng"] = next_col
    return cols


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--out", help="Ausgabe-Datei (default: <file>_geo.xlsx)")
    ap.add_argument("--limit", type=int, default=0,
                    help="Maximal N neue API-Lookups (0 = unbegrenzt)")
    ap.add_argument("--offline", action="store_true",
                    help="Nur Cache + Kanton-Fallback, keine API")
    args = ap.parse_args()

    src = Path(args.file)
    if not src.exists():
        print(f"Datei nicht gefunden: {src}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else src.with_name(src.stem + "_geo.xlsx")

    wb = openpyxl.load_workbook(src)
    sheet = ("📋 Kunden-Datenbank" if "📋 Kunden-Datenbank" in wb.sheetnames
             else wb.sheetnames[0])
    ws = wb[sheet]

    cols = ensure_columns(ws)
    cache = load_cache()
    session = None
    if not args.offline:
        try:
            import requests
            session = requests.Session()
        except ImportError:
            print("requests nicht installiert — wechsle in Offline-Modus.",
                  file=sys.stderr)
            args.offline = True

    n_total, n_cache, n_api, n_fallback, n_skip = 0, 0, 0, 0, 0
    api_budget = args.limit if args.limit > 0 else 10**9

    for r in range(4, ws.max_row + 1):
        firma = ws.cell(row=r, column=cols.get("Firmenname *", 4)).value
        if not firma:
            continue
        n_total += 1
        plz = ws.cell(row=r, column=cols.get("PLZ", 6)).value
        ort = ws.cell(row=r, column=cols.get("Ort", 5)).value
        kanton = ws.cell(row=r, column=cols.get("Kanton", 7)).value
        # Skip if already populated
        if (ws.cell(row=r, column=cols["Lat"]).value
                and ws.cell(row=r, column=cols["Lng"]).value):
            n_skip += 1
            continue
        if api_budget <= 0:
            offline_only = True
        else:
            offline_only = args.offline
        coords, source = geocode_row(plz, ort, kanton, cache, session,
                                     offline=offline_only)
        if source == "cache":
            n_cache += 1
        elif source == "nominatim":
            n_api += 1
            api_budget -= 1
        elif source == "fallback":
            n_fallback += 1
        if coords:
            ws.cell(row=r, column=cols["Lat"], value=coords[0])
            ws.cell(row=r, column=cols["Lng"], value=coords[1])
        if n_total % 25 == 0:
            print(f"  … {n_total} Zeilen geprüft (api={n_api}, cache={n_cache}, "
                  f"fallback={n_fallback})", file=sys.stderr)

    save_cache(cache)
    wb.save(out)

    print(f"Geocoded {n_total} Zeilen → {out}")
    print(f"  Cache-Hits:      {n_cache}")
    print(f"  API-Lookups:     {n_api}")
    print(f"  Kanton-Fallback: {n_fallback}")
    print(f"  Übersprungen:    {n_skip} (bereits geocodiert)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
