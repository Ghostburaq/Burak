// ============================================================
// Power-Query-Vorlagen — Vertriebs-Cockpit AVIA VOLT
// Einfügen: Daten ▸ Daten abrufen ▸ Leere Abfrage ▸ Erweiterter Editor
// Danach genügt „Alle aktualisieren“ (Strg+Alt+F5) als Knopfdruck.
// ============================================================

// --- 1) LIVE CHF-WECHSELKURSE (ECB, ohne Zugangsdaten) ------------------
let
    Xml      = Xml.Tables(Web.Contents("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml")),
    Cube     = Xml{0}[Cube]{0}[Cube],
    Tabelle  = Table.SelectColumns(Cube, {"Attribute:currency", "Attribute:rate"}),
    Umbenannt= Table.RenameColumns(Tabelle, {{"Attribute:currency","Waehrung"}, {"Attribute:rate","Kurs_pro_EUR"}})
in
    Umbenannt

// --- 2) EIGENE SQL-DATENBANK (Server/DB anpassen) ----------------------
// let
//     Quelle = Sql.Database("SERVERNAME", "DATENBANK",
//                 [Query="SELECT firma, region, phase, volumen, erw_abschluss FROM deals"])
// in
//     Quelle

// --- 3) MySQL / PostgreSQL ---------------------------------------------
// MySQL:       Quelle = MySQL.Database("host:3306", "db", [Query="SELECT * FROM deals"])
// PostgreSQL:  Quelle = PostgreSQL.Database("host", "db", [Query="SELECT * FROM deals"])

// --- 4) GOOGLE SHEETS / SHAREPOINT (Freigabe-CSV-Link) -----------------
// let
//     Quelle = Csv.Document(Web.Contents("https://.../export?format=csv"),
//                 [Delimiter=",", Encoding=65001]),
//     Kopf   = Table.PromoteHeaders(Quelle, [PromoteAllScalars=true])
// in
//     Kopf
