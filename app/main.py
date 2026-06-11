"""Event- & Vermietungstool fuer mobile Kaelte-, Waerme- und Power-Technik.

Vereint Artikeldatenbank, Bestand/Disposition, Logistik, Vermietungs-Workflows
und Kraftstoffabrechnung in einem Tool (FastAPI + SQLite).
"""
import os
from datetime import date, datetime, timedelta

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import db as database
from .logic import (
    line_total, calc_event, logistics, compatibility_warnings, maintenance_alerts,
)
from .pdf import build_document

BASE = os.path.dirname(__file__)
app = FastAPI(title="Burak Rental Suite")
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE, "templates"))

# Jinja-Filter
RATE_LABEL = {"daily": "Tagesmiete", "weekend": "Wochenende", "weekly": "Wochenmiete", "fixed": "Pauschale"}
STATUS_COLORS = {
    "Anfrage": "slate", "Angebot": "amber", "Bestaetigt": "blue",
    "Laufend": "violet", "Abgeschlossen": "green", "Storniert": "red",
    "verfuegbar": "green", "vermietet": "blue", "defekt": "red",
    "reparatur": "amber", "wartung": "violet",
}


def eur(v):
    try:
        return f"{float(v):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "0,00 €"


templates.env.filters["eur"] = eur
templates.env.filters["line_total"] = line_total
templates.env.globals["RATE_LABEL"] = RATE_LABEL
templates.env.globals["STATUS_COLORS"] = STATUS_COLORS
templates.env.globals["today"] = lambda: date.today().isoformat()


@app.on_event("startup")
def startup():
    database.init_db()


def render(request, name, **ctx):
    return templates.TemplateResponse(request, name, ctx)


def get_settings(conn):
    return conn.execute("SELECT * FROM settings WHERE id=1").fetchone()


# ----------------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    conn = database.get_db()
    today = date.today().isoformat()
    soon = (date.today() + timedelta(days=30)).isoformat()

    upcoming = conn.execute(
        """SELECT e.*, c.company FROM events e LEFT JOIN customers c ON c.id=e.customer_id
           WHERE e.end_date >= ? AND e.status NOT IN ('Abgeschlossen','Storniert')
           ORDER BY e.start_date LIMIT 8""", (today,)).fetchall()
    open_offers = conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE status IN ('Anfrage','Angebot')").fetchone()["n"]
    stats = {
        "events": conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"],
        "customers": conn.execute("SELECT COUNT(*) AS n FROM customers").fetchone()["n"],
        "articles": conn.execute("SELECT COUNT(*) AS n FROM articles").fetchone()["n"],
        "units": conn.execute("SELECT COUNT(*) AS n FROM units").fetchone()["n"],
        "open_offers": open_offers,
        "available": conn.execute("SELECT COUNT(*) AS n FROM units WHERE status='verfuegbar'").fetchone()["n"],
    }

    # Umsatz bestaetigter/laufender Events (Brutto)
    revenue = 0.0
    s = get_settings(conn)
    for ev in conn.execute("SELECT * FROM events WHERE status IN ('Bestaetigt','Laufend','Abgeschlossen')").fetchall():
        items = _event_items_full(conn, ev["id"])
        revenue += calc_event(ev, items, s["vat_rate"])["gross"]

    alerts = maintenance_alerts(conn)
    conn.close()
    return render(request, "dashboard.html", title="Dashboard", upcoming=upcoming,
                  stats=stats, revenue=revenue, alerts=alerts)


# ----------------------------------------------------------------------------
# Kunden
# ----------------------------------------------------------------------------
@app.get("/kunden", response_class=HTMLResponse)
def kunden(request: Request):
    conn = database.get_db()
    rows = conn.execute(
        """SELECT c.*, (SELECT COUNT(*) FROM events e WHERE e.customer_id=c.id) AS event_count
           FROM customers c ORDER BY c.company""").fetchall()
    conn.close()
    return render(request, "kunden.html", title="Kunden", customers=rows)


@app.get("/kunden/neu", response_class=HTMLResponse)
def kunde_neu(request: Request):
    return render(request, "kunde_form.html", title="Neuer Kunde", customer=None)


@app.get("/kunden/{cid}", response_class=HTMLResponse)
def kunde_detail(request: Request, cid: int):
    conn = database.get_db()
    customer = conn.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone()
    if not customer:
        raise HTTPException(404)
    events = conn.execute("SELECT * FROM events WHERE customer_id=? ORDER BY start_date DESC", (cid,)).fetchall()
    conn.close()
    return render(request, "kunde_detail.html", title=customer["company"], customer=customer, events=events)


@app.get("/kunden/{cid}/bearbeiten", response_class=HTMLResponse)
def kunde_edit(request: Request, cid: int):
    conn = database.get_db()
    customer = conn.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone()
    conn.close()
    if not customer:
        raise HTTPException(404)
    return render(request, "kunde_form.html", title="Kunde bearbeiten", customer=customer)


@app.post("/kunden/speichern")
def kunde_speichern(cid: str = Form(""), company: str = Form(...), contact: str = Form(""),
                    email: str = Form(""), phone: str = Form(""), street: str = Form(""),
                    zip: str = Form(""), city: str = Form(""), country: str = Form("Deutschland"),
                    notes: str = Form("")):
    conn = database.get_db()
    if cid:
        conn.execute(
            """UPDATE customers SET company=?, contact=?, email=?, phone=?, street=?, zip=?, city=?,
               country=?, notes=? WHERE id=?""",
            (company, contact, email, phone, street, zip, city, country, notes, int(cid)))
        target = int(cid)
    else:
        cur = conn.execute(
            """INSERT INTO customers (company, contact, email, phone, street, zip, city, country, notes, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (company, contact, email, phone, street, zip, city, country, notes,
             datetime.now().isoformat(timespec="seconds")))
        target = cur.lastrowid
    conn.commit()
    conn.close()
    return RedirectResponse(f"/kunden/{target}", status_code=303)


@app.post("/kunden/{cid}/loeschen")
def kunde_loeschen(cid: int):
    conn = database.get_db()
    conn.execute("DELETE FROM customers WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return RedirectResponse("/kunden", status_code=303)


# ----------------------------------------------------------------------------
# Artikel (Technische Spezifikationen & Artikeldatenbank)
# ----------------------------------------------------------------------------
@app.get("/artikel", response_class=HTMLResponse)
def artikel(request: Request, kategorie: str = ""):
    conn = database.get_db()
    if kategorie:
        rows = conn.execute("SELECT * FROM articles WHERE category=? ORDER BY name", (kategorie,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM articles ORDER BY is_accessory, category, name").fetchall()
    cats = [r["category"] for r in conn.execute(
        "SELECT DISTINCT category FROM articles WHERE category IS NOT NULL ORDER BY category").fetchall()]
    # Geraeteanzahl je Artikel
    counts = {r["article_id"]: r["n"] for r in conn.execute(
        "SELECT article_id, COUNT(*) AS n FROM units GROUP BY article_id").fetchall()}
    conn.close()
    return render(request, "artikel.html", title="Artikeldatenbank", articles=rows, cats=cats,
                  kategorie=kategorie, counts=counts)


@app.get("/artikel/neu", response_class=HTMLResponse)
def artikel_neu(request: Request):
    return render(request, "artikel_form.html", title="Neuer Artikel", article=None)


@app.get("/artikel/{aid}", response_class=HTMLResponse)
def artikel_detail(request: Request, aid: int):
    conn = database.get_db()
    article = conn.execute("SELECT * FROM articles WHERE id=?", (aid,)).fetchone()
    if not article:
        raise HTTPException(404)
    units = conn.execute("SELECT * FROM units WHERE article_id=? ORDER BY serial_number", (aid,)).fetchall()
    compat = conn.execute(
        """SELECT a.* FROM compatibility comp JOIN articles a ON a.id=comp.accessory_id
           WHERE comp.article_id=? ORDER BY a.name""", (aid,)).fetchall()
    all_accessories = conn.execute(
        "SELECT * FROM articles WHERE is_accessory=1 ORDER BY name").fetchall()
    conn.close()
    return render(request, "artikel_detail.html", title=article["name"], article=article,
                  units=units, compat=compat, all_accessories=all_accessories)


@app.get("/artikel/{aid}/bearbeiten", response_class=HTMLResponse)
def artikel_edit(request: Request, aid: int):
    conn = database.get_db()
    article = conn.execute("SELECT * FROM articles WHERE id=?", (aid,)).fetchone()
    conn.close()
    if not article:
        raise HTTPException(404)
    return render(request, "artikel_form.html", title="Artikel bearbeiten", article=article)


def _f(v):
    """Form-Wert -> float oder None."""
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


@app.post("/artikel/speichern")
async def artikel_speichern(request: Request):
    form = await request.form()
    fields = ["name", "category", "manufacturer", "model", "cooling_kw", "heating_kw", "power_kva",
              "airflow_m3h", "fuel_consumption_lph", "fuel_type", "voltage", "connector", "weight_kg",
              "length_cm", "width_cm", "height_cm", "volume_m3", "daily_rate", "weekend_rate",
              "weekly_rate", "deposit", "maintenance_interval_days", "notes"]
    num = {"cooling_kw", "heating_kw", "power_kva", "airflow_m3h", "fuel_consumption_lph", "weight_kg",
           "length_cm", "width_cm", "height_cm", "volume_m3", "daily_rate", "weekend_rate",
           "weekly_rate", "deposit", "maintenance_interval_days"}
    data = {f: (_f(form.get(f)) if f in num else (form.get(f) or "")) for f in fields}
    data["needs_maintenance"] = 1 if form.get("needs_maintenance") else 0
    data["is_accessory"] = 1 if form.get("is_accessory") else 0
    aid = form.get("aid", "")

    conn = database.get_db()
    if aid:
        sets = ", ".join(f"{k}=?" for k in data)
        conn.execute(f"UPDATE articles SET {sets} WHERE id=?", (*data.values(), int(aid)))
        target = int(aid)
    else:
        cols = ", ".join(data.keys())
        ph = ", ".join("?" for _ in data)
        cur = conn.execute(f"INSERT INTO articles ({cols}) VALUES ({ph})", tuple(data.values()))
        target = cur.lastrowid
    conn.commit()
    conn.close()
    return RedirectResponse(f"/artikel/{target}", status_code=303)


@app.post("/artikel/{aid}/loeschen")
def artikel_loeschen(aid: int):
    conn = database.get_db()
    conn.execute("DELETE FROM articles WHERE id=?", (aid,))
    conn.commit()
    conn.close()
    return RedirectResponse("/artikel", status_code=303)


@app.post("/artikel/{aid}/kompatibilitaet")
def artikel_kompat(aid: int, accessory_id: int = Form(...)):
    conn = database.get_db()
    conn.execute("INSERT OR IGNORE INTO compatibility (article_id, accessory_id) VALUES (?,?)",
                 (aid, accessory_id))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/artikel/{aid}", status_code=303)


@app.post("/artikel/{aid}/kompatibilitaet/{acc}/entfernen")
def artikel_kompat_del(aid: int, acc: int):
    conn = database.get_db()
    conn.execute("DELETE FROM compatibility WHERE article_id=? AND accessory_id=?", (aid, acc))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/artikel/{aid}", status_code=303)


# ----------------------------------------------------------------------------
# Geraete (Bestand / Seriennummern / Disposition)
# ----------------------------------------------------------------------------
@app.get("/geraete", response_class=HTMLResponse)
def geraete(request: Request, status: str = ""):
    conn = database.get_db()
    q = """SELECT u.*, a.name AS article_name, a.category FROM units u
           JOIN articles a ON a.id=u.article_id"""
    params = ()
    if status:
        q += " WHERE u.status=?"
        params = (status,)
    q += " ORDER BY a.name, u.serial_number"
    rows = conn.execute(q, params).fetchall()
    articles = conn.execute("SELECT id, name FROM articles WHERE is_accessory=0 ORDER BY name").fetchall()
    conn.close()
    return render(request, "geraete.html", title="Bestand & Disposition", units=rows,
                  articles=articles, status=status)


@app.post("/geraete/speichern")
def geraet_speichern(uid: str = Form(""), article_id: int = Form(...), serial_number: str = Form(""),
                     barcode: str = Form(""), status: str = Form("verfuegbar"),
                     operating_hours: str = Form("0"), last_maintenance: str = Form(""),
                     notes: str = Form("")):
    conn = database.get_db()
    art = conn.execute("SELECT maintenance_interval_days FROM articles WHERE id=?", (article_id,)).fetchone()
    interval = art["maintenance_interval_days"] if art else 365
    next_m = None
    if last_maintenance and interval:
        try:
            next_m = (date.fromisoformat(last_maintenance) + timedelta(days=int(interval))).isoformat()
        except ValueError:
            next_m = None
    hrs = _f(operating_hours) or 0
    if uid:
        conn.execute(
            """UPDATE units SET article_id=?, serial_number=?, barcode=?, status=?, operating_hours=?,
               last_maintenance=?, next_maintenance=?, notes=? WHERE id=?""",
            (article_id, serial_number, barcode, status, hrs, last_maintenance or None, next_m, notes, int(uid)))
    else:
        conn.execute(
            """INSERT INTO units (article_id, serial_number, barcode, status, operating_hours,
               last_maintenance, next_maintenance, notes) VALUES (?,?,?,?,?,?,?,?)""",
            (article_id, serial_number, barcode, status, hrs, last_maintenance or None, next_m, notes))
    conn.commit()
    conn.close()
    return RedirectResponse("/geraete", status_code=303)


@app.post("/geraete/{uid}/status")
def geraet_status(uid: int, status: str = Form(...)):
    conn = database.get_db()
    conn.execute("UPDATE units SET status=? WHERE id=?", (status, uid))
    conn.commit()
    conn.close()
    return RedirectResponse("/geraete", status_code=303)


@app.post("/geraete/{uid}/wartung")
def geraet_wartung(uid: int):
    """Wartung als erledigt markieren -> next_maintenance neu berechnen, Status verfuegbar."""
    conn = database.get_db()
    u = conn.execute(
        """SELECT u.*, a.maintenance_interval_days AS interval FROM units u
           JOIN articles a ON a.id=u.article_id WHERE u.id=?""", (uid,)).fetchone()
    if u:
        interval = u["interval"] or 365
        today = date.today()
        nxt = (today + timedelta(days=int(interval))).isoformat()
        conn.execute("UPDATE units SET last_maintenance=?, next_maintenance=?, status='verfuegbar' WHERE id=?",
                     (today.isoformat(), nxt, uid))
        conn.commit()
    conn.close()
    return RedirectResponse(request_referer_or("/wartung"), status_code=303)


def request_referer_or(default):
    return default


@app.post("/geraete/{uid}/loeschen")
def geraet_loeschen(uid: int):
    conn = database.get_db()
    conn.execute("DELETE FROM units WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    return RedirectResponse("/geraete", status_code=303)


# ----------------------------------------------------------------------------
# Wartung & Pruefzyklen (UVV)
# ----------------------------------------------------------------------------
@app.get("/wartung", response_class=HTMLResponse)
def wartung(request: Request):
    conn = database.get_db()
    alerts = maintenance_alerts(conn, horizon_days=60)
    conn.close()
    return render(request, "wartung.html", title="Wartung & UVV-Pruefung", alerts=alerts)


# ----------------------------------------------------------------------------
# Personal & Fuhrpark (Logistik-Ressourcen)
# ----------------------------------------------------------------------------
@app.get("/ressourcen", response_class=HTMLResponse)
def ressourcen(request: Request):
    conn = database.get_db()
    staff = conn.execute("SELECT * FROM staff ORDER BY role, name").fetchall()
    vehicles = conn.execute("SELECT * FROM vehicles ORDER BY name").fetchall()
    conn.close()
    return render(request, "ressourcen.html", title="Personal & Fuhrpark", staff=staff, vehicles=vehicles)


@app.post("/personal/speichern")
def personal_speichern(name: str = Form(...), role: str = Form(""), phone: str = Form(""),
                       notes: str = Form("")):
    conn = database.get_db()
    conn.execute("INSERT INTO staff (name, role, phone, notes) VALUES (?,?,?,?)", (name, role, phone, notes))
    conn.commit()
    conn.close()
    return RedirectResponse("/ressourcen", status_code=303)


@app.post("/personal/{sid}/loeschen")
def personal_loeschen(sid: int):
    conn = database.get_db()
    conn.execute("DELETE FROM staff WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return RedirectResponse("/ressourcen", status_code=303)


@app.post("/fahrzeug/speichern")
def fahrzeug_speichern(name: str = Form(...), license_plate: str = Form(""),
                       payload_kg: str = Form("0"), volume_m3: str = Form("0"), notes: str = Form("")):
    conn = database.get_db()
    conn.execute("INSERT INTO vehicles (name, license_plate, payload_kg, volume_m3, notes) VALUES (?,?,?,?,?)",
                 (name, license_plate, _f(payload_kg) or 0, _f(volume_m3) or 0, notes))
    conn.commit()
    conn.close()
    return RedirectResponse("/ressourcen", status_code=303)


@app.post("/fahrzeug/{vid}/loeschen")
def fahrzeug_loeschen(vid: int):
    conn = database.get_db()
    conn.execute("DELETE FROM vehicles WHERE id=?", (vid,))
    conn.commit()
    conn.close()
    return RedirectResponse("/ressourcen", status_code=303)


# ----------------------------------------------------------------------------
# Events / Mietauftraege
# ----------------------------------------------------------------------------
def _event_items_full(conn, event_id):
    """Positionen inkl. Artikelstammdaten (Gewicht, Volumen, Kaution, is_accessory)."""
    return conn.execute(
        """SELECT ei.*, a.name, a.weight_kg, a.volume_m3, a.deposit, a.is_accessory
           FROM event_items ei LEFT JOIN articles a ON a.id=ei.article_id
           WHERE ei.event_id=? ORDER BY ei.position, ei.id""", (event_id,)).fetchall()


@app.get("/events", response_class=HTMLResponse)
def events(request: Request, status: str = ""):
    conn = database.get_db()
    q = """SELECT e.*, c.company FROM events e LEFT JOIN customers c ON c.id=e.customer_id"""
    params = ()
    if status:
        q += " WHERE e.status=?"
        params = (status,)
    q += " ORDER BY e.start_date DESC"
    rows = conn.execute(q, params).fetchall()
    s = get_settings(conn)
    totals = {}
    for ev in rows:
        items = _event_items_full(conn, ev["id"])
        totals[ev["id"]] = calc_event(ev, items, s["vat_rate"])["gross"]
    conn.close()
    statuses = ["Anfrage", "Angebot", "Bestaetigt", "Laufend", "Abgeschlossen", "Storniert"]
    return render(request, "events.html", title="Events & Mietauftraege", events=rows,
                  totals=totals, status=status, statuses=statuses)


@app.get("/events/neu", response_class=HTMLResponse)
def event_neu(request: Request):
    conn = database.get_db()
    customers = conn.execute("SELECT id, company FROM customers ORDER BY company").fetchall()
    vehicles = conn.execute("SELECT id, name FROM vehicles ORDER BY name").fetchall()
    conn.close()
    return render(request, "event_form.html", title="Neuer Auftrag", event=None,
                  customers=customers, vehicles=vehicles)


@app.get("/events/{eid}/bearbeiten", response_class=HTMLResponse)
def event_edit(request: Request, eid: int):
    conn = database.get_db()
    event = conn.execute("SELECT * FROM events WHERE id=?", (eid,)).fetchone()
    if not event:
        raise HTTPException(404)
    customers = conn.execute("SELECT id, company FROM customers ORDER BY company").fetchall()
    vehicles = conn.execute("SELECT id, name FROM vehicles ORDER BY name").fetchall()
    conn.close()
    return render(request, "event_form.html", title="Auftrag bearbeiten", event=event,
                  customers=customers, vehicles=vehicles)


@app.post("/events/speichern")
def event_speichern(eid: str = Form(""), title: str = Form(...), customer_id: str = Form(""),
                    status: str = Form("Anfrage"), start_date: str = Form(""), end_date: str = Form(""),
                    location: str = Form(""), location_address: str = Form(""), description: str = Form(""),
                    internal_notes: str = Form(""), delivery_window: str = Form(""),
                    vehicle_id: str = Form(""), discount_pct: str = Form("0"), service_fee: str = Form("0")):
    conn = database.get_db()
    cust = int(customer_id) if customer_id else None
    veh = int(vehicle_id) if vehicle_id else None
    vals = (title, cust, status, start_date or None, end_date or None, location, location_address,
            description, internal_notes, delivery_window, veh, _f(discount_pct) or 0, _f(service_fee) or 0)
    if eid:
        conn.execute(
            """UPDATE events SET title=?, customer_id=?, status=?, start_date=?, end_date=?, location=?,
               location_address=?, description=?, internal_notes=?, delivery_window=?, vehicle_id=?,
               discount_pct=?, service_fee=? WHERE id=?""", (*vals, int(eid)))
        target = int(eid)
    else:
        cur = conn.execute(
            """INSERT INTO events (title, customer_id, status, start_date, end_date, location,
               location_address, description, internal_notes, delivery_window, vehicle_id, discount_pct,
               service_fee, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (*vals, datetime.now().isoformat(timespec="seconds")))
        target = cur.lastrowid
    conn.commit()
    conn.close()
    return RedirectResponse(f"/events/{target}", status_code=303)


@app.get("/events/{eid}", response_class=HTMLResponse)
def event_detail(request: Request, eid: int):
    conn = database.get_db()
    event = conn.execute("SELECT * FROM events WHERE id=?", (eid,)).fetchone()
    if not event:
        raise HTTPException(404)
    customer = None
    if event["customer_id"]:
        customer = conn.execute("SELECT * FROM customers WHERE id=?", (event["customer_id"],)).fetchone()
    vehicle = None
    if event["vehicle_id"]:
        vehicle = conn.execute("SELECT * FROM vehicles WHERE id=?", (event["vehicle_id"],)).fetchone()
    items = _event_items_full(conn, eid)
    s = get_settings(conn)
    calc = calc_event(event, items, s["vat_rate"])
    log = logistics(items, vehicle)
    warnings = compatibility_warnings(conn, items)

    articles = conn.execute("SELECT * FROM articles ORDER BY is_accessory, name").fetchall()
    all_staff = conn.execute("SELECT * FROM staff ORDER BY role, name").fetchall()
    assigned = conn.execute(
        """SELECT es.id AS link_id, es.task, s.* FROM event_staff es JOIN staff s ON s.id=es.staff_id
           WHERE es.event_id=?""", (eid,)).fetchall()
    op_records = conn.execute(
        "SELECT * FROM operating_records WHERE event_id=? ORDER BY recorded_at DESC", (eid,)).fetchall()
    units = conn.execute(
        """SELECT u.*, a.name AS article_name FROM units u JOIN articles a ON a.id=u.article_id
           ORDER BY a.name""").fetchall()
    fuel_cost = sum((float(r["hours_end"] or 0) - float(r["hours_start"] or 0)) * 0 +
                    float(r["fuel_liters"] or 0) * float(r["fuel_price_per_l"] or 0) for r in op_records)
    conn.close()
    return render(request, "event_detail.html", title=event["title"], event=event, customer=customer,
                  vehicle=vehicle, items=items, calc=calc, logistics=log, warnings=warnings,
                  articles=articles, all_staff=all_staff, assigned=assigned, op_records=op_records,
                  units=units, fuel_cost=fuel_cost)


@app.post("/events/{eid}/loeschen")
def event_loeschen(eid: int):
    conn = database.get_db()
    conn.execute("DELETE FROM events WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return RedirectResponse("/events", status_code=303)


# --- Positionen ---
@app.post("/events/{eid}/position")
def position_add(eid: int, article_id: str = Form(""), description: str = Form(""),
                 quantity: str = Form("1"), rate_type: str = Form("daily"), days: str = Form("1"),
                 unit_price: str = Form(""), line_discount_pct: str = Form("0")):
    conn = database.get_db()
    art = None
    aid = int(article_id) if article_id else None
    if aid:
        art = conn.execute("SELECT * FROM articles WHERE id=?", (aid,)).fetchone()
    # Preis automatisch aus Tarif vorbelegen, falls leer
    price = _f(unit_price)
    if price is None and art:
        price = {"daily": art["daily_rate"], "weekend": art["weekend_rate"],
                 "weekly": art["weekly_rate"]}.get(rate_type, art["daily_rate"]) or 0
    desc = description or (art["name"] if art else "")
    pos = conn.execute("SELECT COALESCE(MAX(position),-1)+1 AS p FROM event_items WHERE event_id=?",
                       (eid,)).fetchone()["p"]
    conn.execute(
        """INSERT INTO event_items (event_id, article_id, description, quantity, rate_type, days,
           unit_price, line_discount_pct, position) VALUES (?,?,?,?,?,?,?,?,?)""",
        (eid, aid, desc, _f(quantity) or 1, rate_type, _f(days) or 1, price or 0,
         _f(line_discount_pct) or 0, pos))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/events/{eid}#positionen", status_code=303)


@app.post("/events/{eid}/position/{pid}/loeschen")
def position_del(eid: int, pid: int):
    conn = database.get_db()
    conn.execute("DELETE FROM event_items WHERE id=? AND event_id=?", (pid, eid))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/events/{eid}#positionen", status_code=303)


@app.post("/events/{eid}/position/{pid}/update")
def position_update(eid: int, pid: int, quantity: str = Form("1"), rate_type: str = Form("daily"),
                    days: str = Form("1"), unit_price: str = Form("0"), line_discount_pct: str = Form("0")):
    conn = database.get_db()
    conn.execute(
        """UPDATE event_items SET quantity=?, rate_type=?, days=?, unit_price=?, line_discount_pct=?
           WHERE id=? AND event_id=?""",
        (_f(quantity) or 1, rate_type, _f(days) or 1, _f(unit_price) or 0, _f(line_discount_pct) or 0,
         pid, eid))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/events/{eid}#positionen", status_code=303)


# --- Personalzuordnung ---
@app.post("/events/{eid}/personal")
def event_staff_add(eid: int, staff_id: int = Form(...), task: str = Form("")):
    conn = database.get_db()
    conn.execute("INSERT INTO event_staff (event_id, staff_id, task) VALUES (?,?,?)", (eid, staff_id, task))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/events/{eid}#logistik", status_code=303)


@app.post("/events/{eid}/personal/{link_id}/entfernen")
def event_staff_del(eid: int, link_id: int):
    conn = database.get_db()
    conn.execute("DELETE FROM event_staff WHERE id=?", (link_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/events/{eid}#logistik", status_code=303)


# --- Kraftstoff-/Betriebsabrechnung ---
@app.post("/events/{eid}/betrieb")
def betrieb_add(eid: int, unit_id: str = Form(""), hours_start: str = Form("0"),
                hours_end: str = Form("0"), fuel_liters: str = Form("0"),
                fuel_price_per_l: str = Form("0"), notes: str = Form("")):
    conn = database.get_db()
    conn.execute(
        """INSERT INTO operating_records (event_id, unit_id, hours_start, hours_end, fuel_liters,
           fuel_price_per_l, recorded_at, notes) VALUES (?,?,?,?,?,?,?,?)""",
        (eid, int(unit_id) if unit_id else None, _f(hours_start) or 0, _f(hours_end) or 0,
         _f(fuel_liters) or 0, _f(fuel_price_per_l) or 0, date.today().isoformat(), notes))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/events/{eid}#betrieb", status_code=303)


@app.post("/events/{eid}/betrieb/{rid}/loeschen")
def betrieb_del(eid: int, rid: int):
    conn = database.get_db()
    conn.execute("DELETE FROM operating_records WHERE id=?", (rid,))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/events/{eid}#betrieb", status_code=303)


# --- PDF: Angebot / Mietvertrag ---
@app.get("/events/{eid}/pdf")
def event_pdf(eid: int, typ: str = "Angebot"):
    doc_type = "Mietvertrag" if typ.lower().startswith("miet") else "Angebot"
    conn = database.get_db()
    event = conn.execute("SELECT * FROM events WHERE id=?", (eid,)).fetchone()
    if not event:
        raise HTTPException(404)
    customer = None
    if event["customer_id"]:
        customer = conn.execute("SELECT * FROM customers WHERE id=?", (event["customer_id"],)).fetchone()
    items = _event_items_full(conn, eid)
    s = get_settings(conn)
    conn.close()
    pdf_bytes = build_document(s, customer, event, items, doc_type)
    fname = f"{doc_type}_{eid:04d}.pdf"
    return Response(pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{fname}"'})


# ----------------------------------------------------------------------------
# Einstellungen (Firmendaten)
# ----------------------------------------------------------------------------
@app.get("/einstellungen", response_class=HTMLResponse)
def einstellungen(request: Request):
    conn = database.get_db()
    s = get_settings(conn)
    conn.close()
    return render(request, "einstellungen.html", title="Einstellungen", s=s)


@app.post("/einstellungen/speichern")
def einstellungen_speichern(company_name: str = Form(""), address: str = Form(""), phone: str = Form(""),
                            email: str = Form(""), vat_rate: str = Form("19"), tax_id: str = Form(""),
                            bank: str = Form(""), iban: str = Form(""), footer: str = Form("")):
    conn = database.get_db()
    conn.execute(
        """UPDATE settings SET company_name=?, address=?, phone=?, email=?, vat_rate=?, tax_id=?,
           bank=?, iban=?, footer=? WHERE id=1""",
        (company_name, address, phone, email, _f(vat_rate) or 19, tax_id, bank, iban, footer))
    conn.commit()
    conn.close()
    return RedirectResponse("/einstellungen", status_code=303)
