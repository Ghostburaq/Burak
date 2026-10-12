# Sprachtrainer Web (EN / FR / ES / ZH)

Die Web-Version des Claude-Code-Skills `sprachtrainer` als installierbare App (PWA) für Desktop und Handy, ausgeliefert als statische Seite über Netlify. Regeln, Modi und Sprachprofile werden beim Build direkt aus `.claude/skills/sprachtrainer/` übernommen.

## Auf Netlify bringen (fertige ZIP)

1. `sprachtrainer-netlify.zip` entpacken. Den **Inhalt** deployen (index.html, app.js, keyblob.json, …), nicht einen Ordner darin.
2. netlify.com/drop öffnen und den entpackten Ordner reinziehen. Netlify liest `_headers` automatisch.
3. URL öffnen, einmal das Passwort eingeben, fertig. Danach läuft alles automatisch.
4. Optional als App installieren (siehe unten).

Netlify liefert HTTPS. Nur damit funktionieren Installation, Offline-Start und Mikrofon.

## Wie der API-Key eingebaut ist

Ein Key im Klartext in einer öffentlichen Seite kann von jedem ausgelesen werden, der die URL kennt. Darum steckt er **verschlüsselt** in `keyblob.json` (AES-256-GCM, Schlüssel per PBKDF2 mit 600 000 Runden aus einem Passwort). Ohne das Passwort ist der Block wertlos.

- Beim ersten Öffnen auf einem Gerät fragt die App nach dem Passwort, entschlüsselt den Key im Browser und merkt ihn sich lokal. Danach ist nichts mehr einzugeben.
- Der Key geht ausschliesslich an api.anthropic.com (per Content-Security-Policy erzwungen) und steht nie in der Sicherungsdatei.
- Einstellungen > «Key von diesem Gerät entfernen» (z.B. bei einem geteilten Gerät). Beim nächsten Öffnen fragt die App wieder nach dem Passwort.
- Restrisiko: Wer die Seite UND das Passwort hat, hat den Key. Passwort nicht weitergeben. In der Anthropic-Console für den Key ein monatliches Ausgabenlimit setzen. Bei Verdacht den Key dort löschen und neu bauen.

## Neu bauen (neuer Key oder neues Passwort)

Key und Passwort kommen nur aus Umgebungsvariablen, nie ins Repo:

```
npm install
ANTHROPIC_API_KEY=sk-ant-... APP_PASSPHRASE=XXXX-XXXX-XXXX-XXXX-XXXX npm run zip
```

Das Passwort braucht mindestens 16 Zeichen (A-Z, 0-9, Bindestriche und Gross/Klein egal). Ohne `ANTHROPIC_API_KEY` baut `npm run build` eine App ohne eingebauten Key, die dann in den Einstellungen nach dem Key fragt.

**Deploy über GitHub statt ZIP:** In Netlify > Site configuration > Environment variables `ANTHROPIC_API_KEY` und `APP_PASSPHRASE` setzen. Base directory `sprachtrainer-web`, Build command und Publish directory stehen in `netlify.toml`. Netlify baut dann bei jedem Push mit verschlüsseltem Key.

## Als App installieren

- **Desktop (Chrome, Edge):** Installations-Symbol in der Adresszeile oder Einstellungen > «Als App installieren».
- **Android (Chrome):** Menü > «App installieren».
- **iPhone und iPad (Safari):** Teilen > «Zum Home-Bildschirm».
- Nach der Installation startet die App auch ohne Netz (Profil, Status, Sicherung). Für Trainingssessions braucht es Internet.
- Updates: Nach einem neuen Deploy lädt die App die neue Version im Hintergrund und nutzt sie beim nächsten Öffnen.

## Was die App kann

- Alle Modi des Skills: Einstufung, 90-Tage-Plan, Tagesprogramm, Gespräch, Wortschatz, Grammatik, Lesen, Immersion, Schreiben, Shadowing, Wochentest.
- Nachbereitung nach jeder Session: Fehlerjournal mit Zählern (3x korrekt in Folge = erledigt), Wortschatz ohne Duplikate, Log, Profil, Plan-Tag, Testresultate.
- Vorlesen (Sprachausgabe des Browsers) und Diktat per Mikrofon in der Zielsprache. Gut für Chinesisch, um Töne zu hören.
- Schnellbefehle (hilfe, deutsch, langsamer, stopp), Stopp-Taste während einer Antwort.
- Wiederaufnahme: Wird die Seite mitten in einer Antwort neu geladen, steht die letzte Nachricht wieder im Eingabefeld.
- Status über alle Sprachen, Anki-Export (nur neue Einträge), Sicherung als JSON, Erinnerung nach 7 Tagen ohne Sicherung.
- Hell und dunkel, Handy hoch und quer, Tablet, Desktop.

## Grenzen

- Der Fortschritt liegt im Browser des Geräts. Handy und Laptop teilen ihn nicht automatisch: Sicherung exportieren und auf dem anderen Gerät einlesen. Werden die Websitedaten gelöscht, ist der Stand ohne Sicherung weg.
- Claude hört nicht. Die Spracherkennung des Browsers zeigt nur grob, ob du verstanden wirst, bei Tönen im Chinesischen ist das kein verlässliches Feedback.
- Diktat geht in Chrome, Edge und Safari. Firefox hat keine Spracherkennung. Datenschutz: Chrome und Edge schicken die Aufnahme zur Texterkennung an Server des Browserherstellers. Für vertrauliche Inhalte (Kunden, Projekte) nicht diktieren.
- Standardmodell ist Claude Opus 5.5 mit Denktiefe `medium`. Günstiger: in den Einstellungen `claude-sonnet-5-5` oder Denktiefe `low`.

## Entwicklung

```
npm install
npm run build   # baut dist/
npm run zip     # baut dist/ und sprachtrainer-netlify.zip
```
