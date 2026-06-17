# Deployment auf Render

Die Burak Rental Suite ist ein FastAPI-Server mit SQLite-Datenbank. Render kann
diesen Stack direkt aus dem GitHub-Repo bauen und betreiben. (Netlify eignet sich
nicht: es hostet nur statische Seiten/kurzlebige Functions, keinen Dauerserver
mit Schreibzugriff auf eine Datenbank.)

## Schritt für Schritt online (mit dauerhafter Datenbank)

Die mitgelieferte `render.yaml` ist bereits für den **Echtbetrieb** konfiguriert:
persistente Disk (`/var/data/crm.db`), Plan `starter`, ohne Demodaten (`SEED=0`).

1. **Repo ist bereits auf GitHub** — Branch `claude/friendly-babbage-6ddxks`.
   Du musst nichts manuell hochladen; Render holt sich den Code direkt von GitHub.
2. Auf <https://render.com> mit deinem **GitHub-Account anmelden** (Render fragt
   nach Zugriff auf deine Repos — bestätigen).
3. Oben rechts **New +** → **Blueprint** klicken.
4. Das Repo **`ghostburaq/burak`** auswählen → Render erkennt automatisch die
   `render.yaml` und zeigt den Service „burak-rental-suite" an.
5. **Apply** klicken. Render
   - installiert die Abhängigkeiten (`pip install -r requirements.txt`),
   - legt die persistente Disk an (`/var/data`, 1 GB),
   - startet den Server (`uvicorn …`).
6. Nach ~2–3 Minuten ist die App unter
   `https://burak-rental-suite.onrender.com` (o. ä.) erreichbar. Die genaue URL
   steht oben im Render-Dashboard.

> **Kosten:** Der Plan `starter` mit persistenter Disk ist kostenpflichtig
> (ca. 7 $/Monat). Render fragt dafür beim ersten Apply nach einer Zahlungsart.

Alternativ ohne Blueprint: **New → Web Service → Repo wählen** und manuell setzen:
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Disk im Tab **Disks** hinzufügen (Mount Path `/var/data`, 1 GB) und
  Umgebungsvariable `DB_PATH=/var/data/crm.db` setzen.

## Kostenlos testen (ohne dauerhafte Daten)

Wer erst gratis testen will, ändert in `render.yaml`:
- `plan: starter` → `plan: free`
- den `disk:`-Block auskommentieren und die `DB_PATH`-Variable entfernen
- optional `SEED` auf `"1"` setzen (Demodaten beim Start)

Achtung: Auf dem Free-Plan ist das Dateisystem flüchtig — die DB wird bei jedem
Neustart/Deploy zurückgesetzt. Außerdem gibt es einen **Cold Start** (~30 s nach
Inaktivität).

## Umgebungsvariablen

| Variable        | Default        | Zweck |
|-----------------|----------------|-------|
| `PORT`          | (von Render)   | Port, auf dem der Server lauscht |
| `DB_PATH`       | `/var/data/crm.db` | Speicherort der SQLite-Datei (auf persistenter Disk) |
| `SEED`          | `0`            | `1` = einmalig mit Demodaten starten; `0` = leere Produktiv-DB |
| `PYTHON_VERSION`| `3.11.9`       | Python-Version auf Render |

## Firmendaten anpassen

Nach dem ersten Start unter **Einstellungen** im Tool die echten Firmendaten
(Name, Adresse, USt-IdNr., IBAN, MwSt.-Satz) eintragen — sie erscheinen auf
Angeboten und Mietverträgen.
