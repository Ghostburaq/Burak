# Kaltakquise-Maschine · Web

Die Seite für Netlify. Zwei Teile:

- **Prüfer** — läuft vollständig im Browser, ohne Server, ohne Schlüssel, ohne
  Netz. Das ist der Teil, der auch bei reinem Drag-and-drop sofort funktioniert.
- **Erzeuger** — ruft die Netlify-Funktion `/.netlify/functions/mail` auf. Nur
  dieser Teil braucht einen API-Schlüssel, und der liegt ausschliesslich auf
  dem Server.

## Dateien

| Datei | Zweck |
|-------|-------|
| `index.html` | Die Seite: Prüfen, Erzeugen, Systemprompt |
| `pruefer.js` | Regel-Prüfer, Portierung von `src/kaltakquise/pruefer.py` |
| `prompt.md` | Systemprompt zum Anzeigen (erzeugt aus `prompts/`) |
| `netlify/functions/mail.mjs` | Serverseitiger Modellaufruf |
| `netlify/functions/prompt.mjs` | Systemprompt für die Funktion (erzeugt aus `prompts/`) |
| `netlify.toml` | Publish-Verzeichnis, Funktionen, Security-Header |
| `package.json` | Abhängigkeit für die Funktion (`@anthropic-ai/sdk`) |

Nach jeder Änderung am Systemprompt: `python3 src/sync_web.py` im Repo-Root.
Das schreibt `prompt.md` und `prompt.mjs` neu.

## Deployen

### Variante 1: Drag-and-drop (schnell, nur Prüfer)

Den Ordner `web/` auf [app.netlify.com/drop](https://app.netlify.com/drop)
ziehen. Die Seite ist sofort online, der Prüfer funktioniert vollständig.
Die Erzeugung meldet, dass die Funktion nicht erreichbar ist, weil bei
Drag-and-drop keine Abhängigkeiten installiert werden.

Wichtig: `node_modules` vorher **nicht** mit hochladen.

### Variante 2: Netlify CLI (alles, inklusive Erzeugung)

```bash
npm install -g netlify-cli
cd web
netlify deploy --build --prod
netlify env:set ANTHROPIC_API_KEY sk-ant-...
```

### Variante 3: Git (empfohlen für dauerhaften Betrieb)

In Netlify **Add new site → Import an existing project**, das Repository
verbinden und setzen:

- Base directory: `web`
- Publish directory: `web`
- Functions directory: `web/netlify/functions`

Danach unter **Site configuration → Environment variables**:

| Variable | Pflicht | Zweck |
|----------|---------|-------|
| `ANTHROPIC_API_KEY` | ja | Schlüssel für den Modellaufruf |
| `ZUGANG` | nein | Wenn gesetzt, verlangt die Funktion diesen Wert im Feld "Zugangswort" |

## Zum Missbrauchsschutz

Eine öffentlich erreichbare Funktion mit hinterlegtem Schlüssel ist ein offenes
Tor: wer die URL kennt, kann auf deine Rechnung Anfragen stellen. Solange die
Site nur du kennst, ist das Risiko klein. Sobald die URL herumgeht, setze
`ZUGANG` auf ein Wort deiner Wahl. Die Funktion begrenzt zusätzlich die
Eingabelänge und die Zahl der Korrekturrunden pro Anfrage.

## Lokal ansehen

```bash
cd web && python3 -m http.server 8899   # Prüfer und Systemprompt
netlify dev                             # zusätzlich mit der Funktion
```

Ein Doppelklick auf `index.html` reicht nicht: die Seite lädt `pruefer.js` und
`prompt.md` nach, das blockiert der Browser im Dateisystem.

## Tests

```bash
node --test tests/test_web_pruefer.mjs    # Regeln, inkl. Paritätstest gegen Python
node --test tests/test_web_funktion.mjs   # Funktion: Methode, Zugang, Grenzen
```

Der Paritätstest schickt dieselben Proben durch `src/kaltakquise/pruefer.py`
und vergleicht Befund für Befund. Damit kann die Browser-Fassung nicht
unbemerkt vom Regelwerk abdriften.
