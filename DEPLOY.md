# Deployment auf Render

Die Burak Rental Suite ist ein FastAPI-Server mit SQLite-Datenbank. Render kann
diesen Stack direkt aus dem GitHub-Repo bauen und betreiben. (Netlify eignet sich
nicht: es hostet nur statische Seiten/kurzlebige Functions, keinen Dauerserver
mit Schreibzugriff auf eine Datenbank.)

## In 5 Minuten online (kostenlos)

1. **Repo zu GitHub pushen** (ist bereits geschehen — Branch
   `claude/friendly-babbage-6ddxks`). Optional vorher in `main` mergen.
2. Auf <https://render.com> mit GitHub anmelden (kostenloser Account).
3. **New → Blueprint** wählen und dieses Repo auswählen.
   Render liest automatisch die mitgelieferte `render.yaml`.
4. **Apply** klicken. Render installiert die Abhängigkeiten und startet die App.
5. Nach ein paar Minuten ist sie unter
   `https://burak-rental-suite.onrender.com` (o. ä.) erreichbar.

Alternativ ohne Blueprint: **New → Web Service → Repo wählen** und manuell setzen:
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Wichtige Hinweise zum kostenlosen Plan

- **Cold Start:** Kostenlose Dienste werden bei Inaktivität pausiert; der erste
  Aufruf danach dauert ~30 Sekunden.
- **Daten nicht dauerhaft:** Das Dateisystem ist flüchtig. Bei jedem Neustart/
  Deploy wird die SQLite-DB neu angelegt und (bei `SEED=1`) mit Demodaten gefüllt.
  Für einen echten Testbetrieb ok — für Echtdaten siehe nächster Abschnitt.

## Persistente Datenbank (für Echtbetrieb)

Damit eingegebene Kunden, Events und Preise dauerhaft erhalten bleiben, braucht
es eine persistente Festplatte (Render-Plan **Starter**, ca. 7 $/Monat):

1. In `render.yaml` den Plan auf `starter` ändern.
2. Den `disk:`-Block am Ende der Datei einkommentieren.
3. Die Umgebungsvariable `DB_PATH` einkommentieren (Wert `/var/data/crm.db`).
4. Erneut deployen.

Die Datenbank liegt dann auf dem gemounteten Volume `/var/data` und übersteht
Neustarts und Deploys.

## Umgebungsvariablen

| Variable        | Default        | Zweck |
|-----------------|----------------|-------|
| `PORT`          | (von Render)   | Port, auf dem der Server lauscht |
| `DB_PATH`       | `app/crm.db`   | Speicherort der SQLite-Datei |
| `SEED`          | `1`            | `0` = ohne Demodaten starten (leere Produktiv-DB) |
| `PYTHON_VERSION`| `3.11.9`       | Python-Version auf Render |

## Firmendaten anpassen

Nach dem ersten Start unter **Einstellungen** im Tool die echten Firmendaten
(Name, Adresse, USt-IdNr., IBAN, MwSt.-Satz) eintragen — sie erscheinen auf
Angeboten und Mietverträgen.
