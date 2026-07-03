// ============================================================
// Power-Query-Vorlagen für das Vertriebs-Cockpit
// Einfügen über:  Daten ▸ Daten abrufen ▸ Leere Abfrage ▸ Erweiterter Editor
// ============================================================

// --- 1) LIVE CHF-WECHSELKURSE (Web-API, ohne Zugangsdaten) ---------------
let
    Quelle   = Json.Document(Web.Contents("https://api.frankfurter.app/latest?from=CHF&to=EUR,USD,GBP")),
    Datum    = Quelle[date],
    Kurse    = Quelle[rates],
    AlsTab   = Record.ToTable(Kurse),
    Umbenannt= Table.RenameColumns(AlsTab, {{"Name","Waehrung"}, {"Value","Kurs"}}),
    MitDatum = Table.AddColumn(Umbenannt, "Stand", each Datum, type text)
in
    MitDatum

// --- 2) EIGENE SQL-DATENBANK (Server/DB anpassen) -----------------------
// let
//     Quelle = Sql.Database("SERVERNAME", "DATENBANK",
//                 [Query="SELECT firma, region, phase, volumen FROM deals"])
// in
//     Quelle

// --- 3) MySQL / PostgreSQL ----------------------------------------------
// MySQL:       Quelle = MySQL.Database("host:3306", "db")
// PostgreSQL:  Quelle = PostgreSQL.Database("host", "db")

// --- 4) GOOGLE SHEETS / SHAREPOINT (per Freigabe-CSV-Link) ---------------
// let
//     Quelle = Csv.Document(Web.Contents("https://.../export?format=csv"),
//                 [Delimiter=",", Encoding=65001]),
//     Kopf   = Table.PromoteHeaders(Quelle, [PromoteAllScalars=true])
// in
//     Kopf
