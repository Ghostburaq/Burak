"""Geschaeftslogik: Preiskalkulation, Logistik, Kompatibilitaet, Wartung."""
import math
from datetime import date


def line_total(item):
    """Berechnet die Positionssumme abhaengig vom Tarifmodell.

    item: dict/Row mit quantity, rate_type, days, unit_price, line_discount_pct
    """
    qty = float(item["quantity"] or 0)
    days = float(item["days"] or 1)
    price = float(item["unit_price"] or 0)
    rate = item["rate_type"] or "daily"

    if rate == "daily":
        base = price * qty * days
    elif rate == "weekend":          # pauschaler Wochenendtarif
        base = price * qty
    elif rate == "weekly":           # je angefangene Woche
        weeks = max(1, math.ceil(days / 7))
        base = price * qty * weeks
    else:                            # fixed / Pauschale
        base = price * qty

    disc = float(item["line_discount_pct"] or 0)
    return round(base * (1 - disc / 100), 2)


def calc_event(event, items, vat_rate):
    """Gesamtkalkulation eines Events inkl. Rabatt, Servicegebuehr, MwSt., Kaution."""
    subtotal = sum(line_total(i) for i in items)
    discount_pct = float(event["discount_pct"] or 0)
    discount_amount = round(subtotal * discount_pct / 100, 2)
    service_fee = float(event["service_fee"] or 0)
    net = round(subtotal - discount_amount + service_fee, 2)
    vat = round(net * float(vat_rate) / 100, 2)
    gross = round(net + vat, 2)
    deposit = round(sum(float(i["deposit"] or 0) * float(i["quantity"] or 0) for i in items), 2)
    return {
        "subtotal": round(subtotal, 2),
        "discount_pct": discount_pct,
        "discount_amount": discount_amount,
        "service_fee": round(service_fee, 2),
        "net": net,
        "vat_rate": float(vat_rate),
        "vat": vat,
        "gross": gross,
        "deposit": deposit,
    }


def logistics(items, vehicle=None):
    """Summiert Gewicht und Volumen und prueft Fahrzeugkapazitaet."""
    total_weight = sum(float(i["weight_kg"] or 0) * float(i["quantity"] or 0) for i in items)
    total_volume = sum(float(i["volume_m3"] or 0) * float(i["quantity"] or 0) for i in items)
    result = {
        "weight_kg": round(total_weight, 1),
        "volume_m3": round(total_volume, 2),
        "vehicle": vehicle["name"] if vehicle else None,
        "weight_ok": True,
        "volume_ok": True,
        "payload_kg": None,
        "vehicle_volume": None,
    }
    if vehicle:
        result["payload_kg"] = float(vehicle["payload_kg"] or 0)
        result["vehicle_volume"] = float(vehicle["volume_m3"] or 0)
        result["weight_ok"] = total_weight <= result["payload_kg"] or result["payload_kg"] == 0
        result["volume_ok"] = total_volume <= result["vehicle_volume"] or result["vehicle_volume"] == 0
    return result


def compatibility_warnings(conn, items):
    """Warnt, wenn Zubehoer/Kabel keinem Hauptgeraet im Auftrag zugeordnet werden kann."""
    main_ids = set()
    accessory_items = []
    for i in items:
        if i["article_id"] is None:
            continue
        if i["is_accessory"]:
            accessory_items.append(i)
        else:
            main_ids.add(i["article_id"])

    warnings = []
    for acc in accessory_items:
        rows = conn.execute(
            "SELECT article_id FROM compatibility WHERE accessory_id=?", (acc["article_id"],)
        ).fetchall()
        compatible_mains = {r["article_id"] for r in rows}
        if compatible_mains and not (compatible_mains & main_ids):
            warnings.append(
                f"'{acc['description'] or acc['name']}' passt zu keinem der gewaehlten Hauptgeraete im Auftrag."
            )
        elif not compatible_mains:
            # Zubehoer ohne hinterlegte Kompatibilitaet -> nur Hinweis
            pass
    return warnings


def maintenance_alerts(conn, horizon_days=30):
    """Geraete mit faelliger oder bald faelliger Wartung/UVV sowie Defekte."""
    today = date.today().isoformat()
    rows = conn.execute(
        """SELECT u.*, a.name AS article_name FROM units u
           JOIN articles a ON a.id = u.article_id
           ORDER BY u.next_maintenance IS NULL, u.next_maintenance""",
    ).fetchall()
    overdue, soon, broken = [], [], []
    from datetime import datetime, timedelta
    limit = (date.today() + timedelta(days=horizon_days)).isoformat()
    for u in rows:
        if u["status"] in ("defekt", "reparatur"):
            broken.append(u)
        nm = u["next_maintenance"]
        if nm:
            if nm < today:
                overdue.append(u)
            elif nm <= limit:
                soon.append(u)
    return {"overdue": overdue, "soon": soon, "broken": broken}
