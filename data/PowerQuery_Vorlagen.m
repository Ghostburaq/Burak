// ============================================================
// Power-Query-Vorlagen — Vertriebs-Cockpit (E-Mobilität / Energie)
// Einfügen: Daten ▸ Daten abrufen ▸ Leere Abfrage ▸ Erweiterter Editor
// Danach genügt „Alle aktualisieren“ (Strg+Alt+F5) als Knopfdruck.
// Funktioniert auch auf Mac / Excel im Web (anders als WEBSERVICE).
// ============================================================

// --- 1) LADEINFRASTRUKTUR SCHWEIZ (OpenChargeMap, JSON) ----------------
// Kostenlosen API-Key holen: openchargemap.org ▸ Profil ▸ API Key
let
    Key      = "HIER-DEINEN-KOSTENLOSEN-KEY",
    Url      = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=CH&maxresults=500&compact=true&verbose=false&key=" & Key,
    Quelle   = Json.Document(Web.Contents(Url)),
    AlsTab   = Table.FromList(Quelle, Splitter.SplitByNothing(), {"POI"}),
    Erweitert= Table.ExpandRecordColumn(AlsTab, "POI", {"AddressInfo","OperatorInfo","NumberOfPoints"}),
    Adr      = Table.ExpandRecordColumn(Erweitert, "AddressInfo", {"Title","Town","StateOrProvince"}, {"Standort","Ort","Kanton"}),
    Betr     = Table.ExpandRecordColumn(Adr, "OperatorInfo", {"Title"}, {"Betreiber"})
in
    Betr

// Auswertung z. B.: Anzahl Ladepunkte je Kanton
// = Table.Group(Betr, {"Kanton"}, {{"Ladepunkte", each List.Sum([NumberOfPoints]), type number}})

// --- 2) FIRMENDATEN ANREICHERN (Handelsregister Zefix) ----------------
// Sucht eine Firma und liefert UID / Rechtsform / Sitz.
(FirmenName as text) =>
let
    Body   = "{""name"":""" & FirmenName & """,""languageKey"":""de""}",
    Quelle = Json.Document(Web.Contents("https://www.zefix.ch/ZefixREST/api/v1/firm/search.json",
                [Headers=[#"Content-Type"="application/json"], Content=Text.ToBinary(Body)])),
    AlsTab = Table.FromList(Quelle, Splitter.SplitByNothing(), {"Firma"}),
    Feld   = Table.ExpandRecordColumn(AlsTab, "Firma", {"name","uidFormatted","legalForm","legalSeat"})
in
    Feld

// --- 3) EIGENE SQL-DATENBANK (Server/DB anpassen) ----------------------
// let
//     Quelle = Sql.Database("SERVERNAME", "DATENBANK",
//                 [Query="SELECT firma, region, phase, volumen, erw_abschluss FROM deals"])
// in
//     Quelle

// --- 4) MySQL / PostgreSQL ---------------------------------------------
// MySQL:       Quelle = MySQL.Database("host:3306", "db", [Query="SELECT * FROM deals"])
// PostgreSQL:  Quelle = PostgreSQL.Database("host", "db", [Query="SELECT * FROM deals"])

// --- 5) GOOGLE SHEETS / SHAREPOINT (Freigabe-CSV-Link) -----------------
// let
//     Quelle = Csv.Document(Web.Contents("https://.../export?format=csv"),
//                 [Delimiter=",", Encoding=65001]),
//     Kopf   = Table.PromoteHeaders(Quelle, [PromoteAllScalars=true])
// in
//     Kopf
