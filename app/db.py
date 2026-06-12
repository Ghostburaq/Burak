"""SQLite-Datenbank: Schema, Verbindung und Seed-Daten.

Deckt alle Kernbereiche des Vermietungstools ab:
- Artikeldatenbank mit technischen Spezifikationen
- Zubehör-Kompatibilitaet (Stuecklisten)
- Geraete mit Seriennummer/Barcode (Disposition)
- Wartungs-/Pruefzyklen (UVV)
- Logistik (Fahrzeuge, Personal)
- Events/Mietauftraege mit Positionen und Preislogik
- Kraftstoff-/Betriebsabrechnung
"""
import sqlite3
import os
from datetime import datetime, date, timedelta

DB_PATH = os.environ.get(
    "DB_PATH", os.path.join(os.path.dirname(__file__), "crm.db")
)


def get_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    contact TEXT,
    email TEXT,
    phone TEXT,
    street TEXT,
    zip TEXT,
    city TEXT,
    country TEXT DEFAULT 'Deutschland',
    notes TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,                 -- Kaelte / Waerme / Power / Zubehoer / Kabel / Verteiler
    manufacturer TEXT,
    model TEXT,
    cooling_kw REAL,              -- Kuehlleistung kW
    heating_kw REAL,             -- Heizleistung kW
    power_kva REAL,              -- Generatorleistung kVA
    airflow_m3h REAL,            -- Luftvolumenstrom m3/h
    fuel_consumption_lph REAL,   -- Kraftstoffverbrauch l/h
    fuel_type TEXT,              -- Diesel / Heizoel / Strom / -
    voltage TEXT,                -- 230V / 400V
    connector TEXT,              -- CEE 32A / CEE 63A / Schuko
    weight_kg REAL DEFAULT 0,
    length_cm REAL,
    width_cm REAL,
    height_cm REAL,
    volume_m3 REAL DEFAULT 0,
    daily_rate REAL DEFAULT 0,
    weekend_rate REAL DEFAULT 0,
    weekly_rate REAL DEFAULT 0,
    deposit REAL DEFAULT 0,       -- Kaution
    needs_maintenance INTEGER DEFAULT 0,
    maintenance_interval_days INTEGER DEFAULT 365,
    is_accessory INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS compatibility (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,       -- Hauptgeraet
    accessory_id INTEGER NOT NULL,     -- passendes Zubehoer
    UNIQUE(article_id, accessory_id),
    FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY(accessory_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    serial_number TEXT,
    barcode TEXT,
    status TEXT DEFAULT 'verfuegbar', -- verfuegbar / vermietet / defekt / reparatur / wartung
    operating_hours REAL DEFAULT 0,
    last_maintenance TEXT,
    next_maintenance TEXT,
    notes TEXT,
    FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT,            -- Fahrer / Techniker / Inbetriebnahme
    phone TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    license_plate TEXT,
    payload_kg REAL DEFAULT 0,    -- Nutzlast
    volume_m3 REAL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    customer_id INTEGER,
    status TEXT DEFAULT 'Anfrage', -- Anfrage / Angebot / Bestaetigt / Laufend / Abgeschlossen / Storniert
    start_date TEXT,
    end_date TEXT,
    location TEXT,
    location_address TEXT,
    description TEXT,
    internal_notes TEXT,
    delivery_window TEXT,         -- Transportzeitfenster
    vehicle_id INTEGER,
    discount_pct REAL DEFAULT 0,
    service_fee REAL DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY(vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS event_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    article_id INTEGER,
    unit_id INTEGER,
    description TEXT,
    quantity REAL DEFAULT 1,
    rate_type TEXT DEFAULT 'daily', -- daily / weekend / weekly / fixed
    days REAL DEFAULT 1,
    unit_price REAL DEFAULT 0,
    line_discount_pct REAL DEFAULT 0,
    position INTEGER DEFAULT 0,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS event_staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    staff_id INTEGER NOT NULL,
    task TEXT,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY(staff_id) REFERENCES staff(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS operating_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    unit_id INTEGER,
    hours_start REAL DEFAULT 0,
    hours_end REAL DEFAULT 0,
    fuel_liters REAL DEFAULT 0,
    fuel_price_per_l REAL DEFAULT 0,
    recorded_at TEXT,
    notes TEXT,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    company_name TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    vat_rate REAL DEFAULT 19,
    tax_id TEXT,
    bank TEXT,
    iban TEXT,
    footer TEXT
);
"""


def init_db(seed=True):
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.commit()

    cur = conn.execute("SELECT COUNT(*) AS n FROM settings")
    if cur.fetchone()["n"] == 0:
        conn.execute(
            """INSERT INTO settings (id, company_name, address, phone, email, vat_rate, tax_id, bank, iban, footer)
               VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "Burak Klima- & Energietechnik GmbH",
                "Industriestrasse 12, 12345 Musterstadt",
                "+49 30 1234567",
                "info@burak-rental.de",
                19,
                "DE123456789",
                "Musterbank",
                "DE00 0000 0000 0000 0000 00",
                "Vielen Dank fuer Ihr Vertrauen. Es gelten unsere AGB.",
            ),
        )
        conn.commit()

    if seed:
        cur = conn.execute("SELECT COUNT(*) AS n FROM articles")
        if cur.fetchone()["n"] == 0:
            _seed(conn)

    conn.close()


def _seed(conn):
    today = date.today()
    # --- Artikel: Hauptgeraete ---
    articles = [
        # name, cat, manu, model, cool, heat, kva, airflow, fuel_lph, fueltype, voltage, connector,
        # weight, L, W, H, vol, daily, weekend, weekly, deposit, needs_maint, maint_int, is_acc
        ("Kaltwassersatz 100 kW", "Kaelte", "Trane", "CGAM100", 100, None, None, 28000, None, "Strom", "400V", "CEE 63A",
         1450, 240, 110, 200, 5.3, 290, 480, 1450, 2000, 1, 365, 0),
        ("Mobile Klimaanlage 14 kW", "Kaelte", "Remko", "RKL490", 14, None, None, 4200, None, "Strom", "230V", "Schuko",
         95, 60, 60, 120, 0.43, 65, 110, 320, 300, 1, 365, 0),
        ("Hallenheizgeraet 80 kW", "Waerme", "Kroll", "M80", None, 80, None, 5500, 7.8, "Heizoel", "230V", "Schuko",
         140, 150, 70, 110, 1.15, 95, 160, 470, 500, 1, 365, 0),
        ("Elektroheizer 30 kW", "Waerme", "Trotec", "TDE95", None, 30, None, 2000, None, "Strom", "400V", "CEE 32A",
         32, 60, 40, 60, 0.14, 45, 75, 220, 200, 0, 365, 0),
        ("Stromgenerator 60 kVA", "Power", "SDMO", "R66", None, None, 60, None, 12.5, "Diesel", "400V", "CEE 63A",
         1320, 250, 110, 150, 4.1, 240, 400, 1200, 1500, 1, 180, 0),
        ("Stromgenerator 20 kVA", "Power", "Pramac", "GSW22", None, None, 20, None, 5.2, "Diesel", "400V", "CEE 32A",
         620, 180, 90, 130, 2.1, 130, 220, 650, 800, 1, 180, 0),
    ]
    # --- Zubehoer / Kabel / Verteiler ---
    accessories = [
        ("Lastkabel CEE 63A 25m", "Kabel", None, None, None, None, None, None, None, "-", "400V", "CEE 63A",
         28, None, None, None, 0.05, 18, 30, 90, 0, 0, 0, 1),
        ("Lastkabel CEE 32A 25m", "Kabel", None, None, None, None, None, None, None, "-", "400V", "CEE 32A",
         16, None, None, None, 0.03, 12, 20, 60, 0, 0, 0, 1),
        ("Stromverteiler 63A->32A/Schuko", "Verteiler", None, None, None, None, None, None, None, "-", "400V", "CEE 63A",
         22, None, None, None, 0.06, 25, 42, 125, 100, 0, 0, 1),
        ("Zulaufschlauch Kaltwasser 2\" 20m", "Zubehoer", None, None, None, None, None, None, None, "-", None, None,
         18, None, None, None, 0.08, 15, 25, 75, 0, 0, 0, 1),
        ("Ablaufschlauch 2\" 20m", "Zubehoer", None, None, None, None, None, None, None, "-", None, None,
         16, None, None, None, 0.08, 15, 25, 75, 0, 0, 0, 1),
        ("Warmluftschlauch 500mm 10m", "Zubehoer", None, None, None, None, None, None, None, "-", None, None,
         9, None, None, None, 0.20, 20, 33, 100, 0, 0, 0, 1),
    ]
    for row in articles + accessories:
        conn.execute(
            """INSERT INTO articles
               (name, category, manufacturer, model, cooling_kw, heating_kw, power_kva, airflow_m3h,
                fuel_consumption_lph, fuel_type, voltage, connector, weight_kg, length_cm, width_cm,
                height_cm, volume_m3, daily_rate, weekend_rate, weekly_rate, deposit, needs_maintenance,
                maintenance_interval_days, is_accessory)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            row,
        )
    conn.commit()

    # --- Kompatibilitaeten ---
    def aid(name):
        return conn.execute("SELECT id FROM articles WHERE name=?", (name,)).fetchone()["id"]

    compat = [
        ("Stromgenerator 60 kVA", "Lastkabel CEE 63A 25m"),
        ("Stromgenerator 60 kVA", "Stromverteiler 63A->32A/Schuko"),
        ("Stromgenerator 20 kVA", "Lastkabel CEE 32A 25m"),
        ("Kaltwassersatz 100 kW", "Lastkabel CEE 63A 25m"),
        ("Kaltwassersatz 100 kW", "Zulaufschlauch Kaltwasser 2\" 20m"),
        ("Kaltwassersatz 100 kW", "Ablaufschlauch 2\" 20m"),
        ("Hallenheizgeraet 80 kW", "Warmluftschlauch 500mm 10m"),
        ("Elektroheizer 30 kW", "Lastkabel CEE 32A 25m"),
    ]
    for main, acc in compat:
        conn.execute("INSERT OR IGNORE INTO compatibility (article_id, accessory_id) VALUES (?,?)",
                     (aid(main), aid(acc)))
    conn.commit()

    # --- Geraete (Seriennummern) ---
    units = [
        ("Stromgenerator 60 kVA", "SN-GEN60-001", "1000001", "verfuegbar", 1200, today - timedelta(days=200), 90),
        ("Stromgenerator 60 kVA", "SN-GEN60-002", "1000002", "verfuegbar", 800, today - timedelta(days=20), 90),
        ("Stromgenerator 20 kVA", "SN-GEN20-001", "1000003", "vermietet", 430, today - timedelta(days=60), 90),
        ("Kaltwassersatz 100 kW", "SN-KWS100-001", "1000004", "verfuegbar", 0, today - timedelta(days=350), 365),
        ("Mobile Klimaanlage 14 kW", "SN-KL14-001", "1000005", "verfuegbar", 0, None, None),
        ("Mobile Klimaanlage 14 kW", "SN-KL14-002", "1000006", "defekt", 0, None, None),
        ("Hallenheizgeraet 80 kW", "SN-HZ80-001", "1000007", "wartung", 0, today - timedelta(days=370), 365),
    ]
    for name, sn, bc, status, hrs, last, interval in units:
        last_str = last.isoformat() if last else None
        next_str = (last + timedelta(days=interval)).isoformat() if (last and interval) else None
        conn.execute(
            """INSERT INTO units (article_id, serial_number, barcode, status, operating_hours,
               last_maintenance, next_maintenance) VALUES (?,?,?,?,?,?,?)""",
            (aid(name), sn, bc, status, hrs, last_str, next_str),
        )
    conn.commit()

    # --- Personal & Fahrzeuge ---
    for name, role, phone in [
        ("Max Mertens", "Fahrer", "+49 170 1111111"),
        ("Jens Kowalski", "Techniker", "+49 170 2222222"),
        ("Sara Demir", "Inbetriebnahme", "+49 170 3333333"),
    ]:
        conn.execute("INSERT INTO staff (name, role, phone) VALUES (?,?,?)", (name, role, phone))
    for name, plate, payload, vol in [
        ("LKW 7,5t Koffer", "M-RT 750", 3000, 22),
        ("Sprinter mit Anhaenger", "M-RT 350", 1400, 14),
    ]:
        conn.execute("INSERT INTO vehicles (name, license_plate, payload_kg, volume_m3) VALUES (?,?,?,?)",
                     (name, plate, payload, vol))
    conn.commit()

    # --- Kunden ---
    customers = [
        ("Eventus Veranstaltungs GmbH", "Lena Brandt", "lena@eventus.de", "+49 30 5550101",
         "Festwiese 1", "10115", "Berlin"),
        ("Bauunternehmen Hoch & Tief AG", "Klaus Roth", "roth@hochtief-bau.de", "+49 89 5550202",
         "Baustrasse 8", "80331", "Muenchen"),
    ]
    for comp, cont, mail, phone, street, zp, city in customers:
        conn.execute(
            """INSERT INTO customers (company, contact, email, phone, street, zip, city, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (comp, cont, mail, phone, street, zp, city, datetime.now().isoformat(timespec="seconds")),
        )
    conn.commit()

    # --- Beispiel-Event mit Positionen ---
    cust_id = conn.execute("SELECT id FROM customers WHERE company LIKE 'Eventus%'").fetchone()["id"]
    veh_id = conn.execute("SELECT id FROM vehicles LIMIT 1").fetchone()["id"]
    conn.execute(
        """INSERT INTO events (title, customer_id, status, start_date, end_date, location, location_address,
           description, delivery_window, vehicle_id, discount_pct, service_fee, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            "Sommerfestival Stromversorgung", cust_id, "Angebot",
            (today + timedelta(days=14)).isoformat(), (today + timedelta(days=17)).isoformat(),
            "Festwiese Tempelhof", "Tempelhofer Damm 1, 12101 Berlin",
            "Stromversorgung Hauptbuehne und Cateringbereich inkl. Verteilung. Aufbau am Vortag, Inbetriebnahme durch Techniker.",
            "Anlieferung Mi 08:00-10:00, Abholung So ab 22:00", veh_id, 5, 350,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    ev_id = conn.execute("SELECT id FROM events ORDER BY id DESC LIMIT 1").fetchone()["id"]
    items = [
        ("Stromgenerator 60 kVA", 1, "daily", 4, 240, 0),
        ("Lastkabel CEE 63A 25m", 4, "daily", 4, 18, 0),
        ("Stromverteiler 63A->32A/Schuko", 2, "daily", 4, 25, 0),
    ]
    for i, (name, qty, rt, days, price, disc) in enumerate(items):
        conn.execute(
            """INSERT INTO event_items (event_id, article_id, description, quantity, rate_type, days,
               unit_price, line_discount_pct, position) VALUES (?,?,?,?,?,?,?,?,?)""",
            (ev_id, aid(name), name, qty, rt, days, price, disc, i),
        )
    conn.commit()


if __name__ == "__main__":
    init_db()
    print("Datenbank initialisiert:", DB_PATH)
