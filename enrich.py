#!/usr/bin/env python3
"""enrich.py — Anreicherung von CRM-Listen mit Website + Geo-Koordinaten.

Nutzung:
    python enrich.py kunden.xlsx --limit 20
    python enrich.py kunden.xlsx --out kunden_enriched.xlsx
    python enrich.py kunden.xlsx --skip-website     # nur Geocoding
    python enrich.py kunden.xlsx --skip-geo         # nur Website-Suche

Strategie pro Firma (Spalte L 'Website' leer):
    1. Slug-Heuristik:   firmenname → kleinbuchstaben, ohne Sonderzeichen
                         → probiere <slug>.ch / <slug>.com / www.<slug>.ch
                         → HEAD-Request, akzeptiere wenn 200/301/302
    2. DuckDuckGo HTML-Endpoint (kein API-Key) als Fallback
    3. Manuell: bleibt leer, Hinweis im Report

Geo: ruft geocode.py auf (Nominatim + Cache + Kanton-Fallback).

Datenquellen:
    - DuckDuckGo HTML (https://duckduckgo.com/html/) — keine Auth nötig
    - Nominatim/OSM — kostenlos, 1 req/s Rate-Limit
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs

import openpyxl

USER_AGENT = ("Mozilla/5.0 (compatible; MiT-CRM-Enricher/1.0; "
              "+https://mobilintime.ch)")
COMMON_TLDS = [".ch", ".com", ".swiss", ".eu"]
SOCIAL_BLOCK = ("linkedin.com", "facebook.com", "twitter.com", "x.com",
                "instagram.com", "youtube.com", "wikipedia.org",
                "moneyhouse", "zefix.ch", "tel.local.ch", "search.ch",
                "tutti.ch", "ricardo.ch")


def slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"\b(ag|sa|gmbh|holding|group|werk|werke|inc|llc|ltd|"
               r"corp|company|kg|co|the|der|die|das|den|of|of the)\b", "", s)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def try_slug(firma: str, session) -> str | None:
    base = slug(firma)
    if not base or len(base) < 3:
        return None
    candidates = []
    for tld in COMMON_TLDS:
        candidates.append(f"https://www.{base}{tld}")
        candidates.append(f"https://{base}{tld}")
    for url in candidates:
        try:
            r = session.head(url, timeout=5, allow_redirects=True,
                             headers={"User-Agent": USER_AGENT})
            if 200 <= r.status_code < 400:
                return r.url.rstrip("/")
        except Exception:
            continue
    return None


class DDGParser(HTMLParser):
    """Parses DuckDuckGo HTML result page, collects result links."""

    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self._capture = False

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs_d = dict(attrs)
        cls = attrs_d.get("class", "")
        href = attrs_d.get("href")
        if not href:
            return
        if "result__a" in cls or "result__url" in cls:
            self.links.append(href)


def ddg_search(firma: str, ort: str | None, session) -> str | None:
    q = firma
    if ort:
        q += f" {ort}"
    q += " Schweiz site:.ch OR site:.com"
    try:
        r = session.get("https://duckduckgo.com/html/",
                        params={"q": q, "kl": "ch-de"},
                        headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return None
    except Exception:
        return None
    parser = DDGParser()
    parser.feed(r.text)
    for link in parser.links:
        # DDG redirect URLs: //duckduckgo.com/l/?uddg=<encoded>
        if link.startswith("//duckduckgo.com/l/"):
            qs = parse_qs(urlparse("https:" + link).query)
            u = qs.get("uddg", [None])[0]
            if u:
                link = unquote(u)
        host = urlparse(link).netloc.lower()
        if not host:
            continue
        if any(b in host for b in SOCIAL_BLOCK):
            continue
        return link.rstrip("/")
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=0,
                    help="Maximal N Firmen anreichern (0 = alle)")
    ap.add_argument("--skip-website", action="store_true")
    ap.add_argument("--skip-geo", action="store_true")
    ap.add_argument("--delay", type=float, default=1.5,
                    help="Sekunden zwischen Web-Requests (default 1.5)")
    args = ap.parse_args()

    src = Path(args.file)
    if not src.exists():
        print(f"Datei nicht gefunden: {src}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else src.with_name(src.stem + "_enriched.xlsx")

    try:
        import requests
    except ImportError:
        print("Benötigt 'requests' (pip install requests).", file=sys.stderr)
        return 2
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    wb = openpyxl.load_workbook(src)
    sheet = ("📋 Kunden-Datenbank" if "📋 Kunden-Datenbank" in wb.sheetnames
             else wb.sheetnames[0])
    ws = wb[sheet]

    headers = [ws.cell(row=3, column=c).value for c in range(1, ws.max_column + 1)]
    cols = {h: i + 1 for i, h in enumerate(headers) if h}
    col_firma = cols.get("Firmenname *", 4)
    col_ort = cols.get("Ort", 5)
    col_web = cols.get("Website", 12)

    found, skipped, missed = 0, 0, 0
    budget = args.limit if args.limit > 0 else 10**9

    if not args.skip_website:
        for r in range(4, ws.max_row + 1):
            firma = ws.cell(row=r, column=col_firma).value
            if not firma:
                continue
            current = ws.cell(row=r, column=col_web).value
            if current:
                skipped += 1
                continue
            if budget <= 0:
                break
            budget -= 1
            url = try_slug(firma, session)
            if not url:
                url = ddg_search(firma, ws.cell(row=r, column=col_ort).value, session)
            if url:
                ws.cell(row=r, column=col_web, value=url)
                found += 1
                print(f"  ✓ row {r}: {firma[:40]} → {url}")
            else:
                missed += 1
                print(f"  ✗ row {r}: {firma[:40]} (kein Treffer)")
            time.sleep(args.delay)

    wb.save(out)
    print(f"\nWebsite-Anreicherung: {found} gefunden, {missed} ohne Treffer, "
          f"{skipped} bereits gesetzt → {out}")

    if not args.skip_geo:
        print("\nGeo-Codierung läuft …")
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).with_name("geocode.py")),
                        str(out), "--out", str(out)], check=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
