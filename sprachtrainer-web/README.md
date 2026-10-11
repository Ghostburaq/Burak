# Sprachtrainer Web (EN / FR / ES / ZH)

Die Web-Version des Claude-Code-Skills `sprachtrainer` als statische Seite für Netlify. Gleiche Regeln, Modi und Sprachprofile: Sie werden beim Build direkt aus `.claude/skills/sprachtrainer/` übernommen.

## Auf Netlify bringen

**Variante A, Drag-and-drop (2 Minuten):**
1. `sprachtrainer-netlify.zip` entpacken.
2. app.netlify.com > Sites > "Deploy manually" bzw. netlify.com/drop öffnen und den entpackten Ordner reinziehen.
3. URL öffnen, API-Key eintragen, fertig.

**Variante B, über GitHub (Updates kommen automatisch):**
1. Netlify > "Import from Git" > dieses Repo wählen.
2. Base directory: `sprachtrainer-web`. Build command und Publish directory kommen aus `netlify.toml`.
3. Branch wählen, auf dem die App liegt.

## API-Key

Die App ruft die Claude-API direkt aus dem Browser auf. Dafür braucht es einen eigenen Anthropic-API-Key (console.anthropic.com). Empfehlung:
- Für die App einen eigenen Key anlegen und in der Console ein monatliches Ausgabenlimit setzen.
- Der Key liegt nur im Browser des Geräts (localStorage). Er wird nicht in die Sicherungsdatei geschrieben und geht nur an api.anthropic.com (per Content-Security-Policy erzwungen).
- Die Seite ist öffentlich erreichbar, aber ohne Key auf dem Gerät nutzlos. Wer die URL kennt, kann deinen Key nicht sehen.

Kosten hängen vom Modell ab. Standard ist Claude Opus 5.5 mit Effort `medium`. Wer sparen will, stellt in den Einstellungen auf `claude-sonnet-5-5` oder Effort `low`.

## Was die App kann

- Alle Modi des Skills: Einstufung, 90-Tage-Plan, Tagesprogramm, Gespräch, Wortschatz, Grammatik, Lesen, Immersion, Schreiben, Shadowing, Wochentest.
- Nachbereitung nach jeder Session: Fehlerjournal mit Zählern (3x korrekt in Folge = erledigt), Wortschatz ohne Duplikate, Log, Profil, Plan-Tag, Testresultate.
- Vorlesen (Sprachausgabe des Browsers, pro Antwort oder automatisch) und Diktat per Mikrofon in der Zielsprache. Gut für Chinesisch, um Töne zu hören.
- Status über alle Sprachen, Anki-Export (nur neue Einträge), Sicherung als JSON exportieren und einlesen.

## Grenzen

- Fortschritt liegt im Browser des Geräts. Handy und Laptop teilen ihn nicht automatisch: Sicherung exportieren und auf dem anderen Gerät einlesen. Wer im Browser die Websitedaten löscht, verliert den Stand ohne Sicherung.
- Claude hört nicht. Die Spracherkennung des Browsers zeigt nur grob, ob du verstanden wirst, besonders bei Tönen im Chinesischen ist das kein verlässliches Feedback.
- Diktat geht in Chrome, Edge und Safari. Firefox hat keine Spracherkennung: dort die Diktierfunktion der Tastatur nutzen.

## Entwicklung

```
npm install
npm run build   # baut dist/
npm run zip     # baut dist/ und sprachtrainer-netlify.zip
```
