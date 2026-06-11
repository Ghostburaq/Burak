# Burak Rental Suite — Event- & Vermietungstool

Ein webbasiertes ERP/CRM-Tool für die Vermietung **mobiler Kälte-, Wärme- und
Power-Generatoren** (HVAC/R und Strom). Vereint die Kernfunktionen etablierter
Branchenlösungen (Rentman, MCS Rental Software, Eventworx) in **einem** Tool —
zugeschnitten auf technisch anspruchsvolles, hochpreisiges Mietequipment.

Gebaut mit **FastAPI + SQLite + Jinja2** (Frontend) und **reportlab** (PDF).
Alle Daten werden manuell gepflegt; nichts ist an externe Dienste gebunden.

## Schnellstart

```bash
pip install -r requirements.txt
./run.sh                     # oder:
python3 -m uvicorn app.main:app --reload
```

Dann im Browser öffnen: <http://127.0.0.1:8000>
Beim ersten Start legt das Tool eine SQLite-Datei (`app/crm.db`) mit
realistischen Beispieldaten an (Generatoren, Kälte-/Wärmegeräte, Kabel,
Geräte mit Seriennummern, Kunden, ein Beispiel-Event).

## Funktionsumfang

### 1. Technische Spezifikationen & Artikeldatenbank
- Leistungsdaten je Artikel: **kW Kälte/Wärme, kVA, Luftvolumenstrom,
  Kraftstoffverbrauch (l/h)**, Spannung, Anschluss/Stecker, Maße/Gewicht/Volumen.
- **Stücklisten/Zubehör-Kompatibilität:** Hauptgeräten lässt sich passendes
  Zubehör (Lastkabel, Verteiler, Zu-/Ablaufschläuche, CEE-Stecker) zuordnen.
- **Kompatibilitätsprüfung:** Beim Anlegen eines Auftrags warnt das Tool, wenn
  gewähltes Zubehör zu keinem Hauptgerät im Auftrag passt.

### 2. Disposition & Bestandsmanagement
- **Seriennummern- und Barcode-Tracking** für jedes einzelne Gerät.
- **Status je Gerät:** verfügbar / vermietet / defekt / in Reparatur / Wartung.
- **Wartungs- & Prüfzyklen (UVV):** automatische Anzeige fälliger Intervalle,
  „Wartung erledigt“ setzt das nächste Fälligkeitsdatum.
- **Defekt-Management:** Rückläufer als defekt/Reparatur markieren — sie werden
  in der Disposition entsprechend ausgewiesen.

### 3. Logistik & Transportplanung
- **Automatische Gewichts- und Volumenberechnung** der gesamten Ladung.
- **Fahrzeugdisposition** mit Kapazitätsprüfung (Warnung bei Überladung).
- **Personaldisposition:** Fahrer, Techniker, Inbetriebnahme-Spezialisten je
  Auftrag mit Aufgabe einteilen.
- **Transportzeitfenster** je Auftrag hinterlegbar.

### 4. Vermietungsspezifische Workflows
- **Angebote & Mietverträge** als PDF (mit Firmendaten, Positionen, Kaution,
  Servicegebühr, MwSt.).
- **Preislogik:** Tagesmiete, Wochenend-Pauschale, Wochenmiete, Festpreis —
  inkl. Positions- und Gesamtrabatt.
- **Kraftstoff- & Betriebsabrechnung:** Betriebsstunden und verbrauchter
  Diesel/Heizöl je Gerät erfassen und abrechnen.

### 5. Übersicht
- **Dashboard** mit kommenden Events, offenen Angeboten, Bestand und
  Wartungswarnungen.

## Projektstruktur

| Datei | Zweck |
|-------|-------|
| `app/main.py`   | FastAPI-App, alle Routen (CRUD, PDF) |
| `app/db.py`     | SQLite-Schema + Seed-Daten |
| `app/logic.py`  | Preiskalkulation, Logistik, Kompatibilität, Wartung |
| `app/pdf.py`    | Angebot/Mietvertrag als PDF (reportlab) |
| `app/templates/`| Jinja2-Oberflächen |
| `app/static/`   | CSS |

## Hinweise
- Die Datenbank `app/crm.db` ist bewusst aus der Versionskontrolle ausgeschlossen
  (siehe `.gitignore`), damit Echtdaten nicht im Repo landen.
- Firmendaten für die Dokumente werden unter **Einstellungen** gepflegt.
