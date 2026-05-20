# Mini CRM

Ein leichtgewichtiges, vollständig browserbasiertes CRM-Tool. Keine Installation, kein Server, keine Datenbank – alle Daten werden im LocalStorage des Browsers gespeichert.

## Features

- **Dashboard** mit KPIs (Kontakte, Firmen, offene Pipeline, gewonnene Deals) und Pipeline-Übersicht
- **Kontakte** (CRUD) mit Position, E-Mail, Telefon und Firmenzuordnung
- **Firmen** (CRUD) mit Branche, Website, Adresse und Verknüpfungen zu Kontakten/Deals
- **Deal-Pipeline** mit Drag & Drop zwischen den Stadien *Lead → Qualifiziert → Angebot → Gewonnen / Verloren*
- **Aktivitäten/Notizen**: Notizen, Anrufe, Meetings, E-Mails – mit Verknüpfung zu Kontakten und Deals
- **Globale Suche** in der jeweils aktiven Ansicht
- **Import / Export** als JSON
- **Demodaten** auf Knopfdruck
- Responsive (Desktop & Tablet)

## Verwendung

`index.html` einfach im Browser öffnen – fertig.

```bash
# Optional: lokalen Server starten
python3 -m http.server 8000
# dann http://localhost:8000 im Browser öffnen
```

### Demodaten laden

In der Seitenleiste auf **Demodaten** klicken – es werden 3 Firmen, 3 Kontakte, 4 Deals und 3 Aktivitäten angelegt.

### Daten sichern

- **Export**: Lädt den kompletten Datenbestand als JSON herunter
- **Import**: Lädt ein zuvor exportiertes JSON wieder ein
- **Reset**: Löscht alle Daten aus dem LocalStorage

## Dateien

- `index.html` – Markup
- `styles.css` – Styling
- `app.js` – komplette App-Logik (State, Routing, Rendering, Drag & Drop)
