# Hochladen auf Netlify

Dieser Ordner ist fertig. Nichts muss vorher bearbeitet werden.

## Inhalt

| Datei | Zweck | Pflicht |
| --- | --- | --- |
| `index.html` | Die komplette Website, eine Datei, keine externen Abhängigkeiten | ja |
| `og-image.png` | Vorschaubild beim Teilen des Links (WhatsApp, LinkedIn, Slack) | nein |
| `_headers` | Security-Header und Content-Security-Policy | nein |
| `DEPLOY.md` | Diese Anleitung. Wird nicht ausgeliefert, stört aber nicht | nein |

## Hochladen

1. Auf [app.netlify.com](https://app.netlify.com) anmelden.
2. **Add new site → Deploy manually**.
3. Diesen **ganzen Ordner** in das Feld ziehen, nicht nur die `index.html`.
   Nur so kommen Vorschaubild und Security-Header mit.
4. Fertig. Netlify vergibt sofort eine Adresse wie `zufallsname.netlify.app`
   inklusive HTTPS.

## Kontaktformular scharf schalten

Das Formular ist bereits als Netlify Form ausgezeichnet und funktioniert nach
dem ersten Deploy automatisch. Eingegangene Anfragen stehen im Dashboard unter
**Forms → kontakt**.

Damit eine Anfrage nicht unbemerkt liegen bleibt, unbedingt einmal einrichten:

**Site configuration → Notifications → Form submission notifications →
Add notification → Email notification** und die eigene Adresse eintragen.

Danach das Formular einmal selbst testen. Nach dem Absenden erscheint der
Bestätigungsblock auf derselben Seite.

## Eigene Domain verbinden

1. **Domain management → Add a domain**, die eigene Domain eintragen.
2. Beim Domain-Anbieter die von Netlify angezeigten DNS-Einträge setzen.
3. Netlify stellt das HTTPS-Zertifikat automatisch aus.
4. Die `netlify.app`-Adresse unter **Domain management** auf die eigene Domain
   weiterleiten lassen, damit die Seite nicht doppelt im Index landet.

### Nach dem Verbinden der Domain: zwei Zeilen ergänzen

In der `index.html` ganz oben im `<head>` steht ein Kommentarblock mit dem
Titel `DOMAIN`. Dort ist beschrieben, welche zwei Zeilen einzufügen sind:

```html
<link rel="canonical" href="https://DEINE-DOMAIN.ch/">
<meta property="og:url" content="https://DEINE-DOMAIN.ch/">
```

Diese Zeilen fehlen bewusst. Eine Adresse einzutragen, die es noch nicht gibt,
wäre schädlicher als gar keine Angabe: Suchmaschinen würden die echte Seite für
eine Kopie halten. Ohne die beiden Zeilen funktioniert die Seite vollständig,
sie werden nur für sauberes SEO nachgetragen.

## Wichtig vor dem öffentlichen Bewerben

Die Rechtstexte (Kontakt/Impressum, Datenschutz, AGB) sind **Entwürfe** und auf
der Seite auch so gekennzeichnet. Sie gehören vor dem Live-Gang durch eine
Fachperson geprüft. Die offenen Punkte stehen in
[`../website/OFFENE_PUNKTE.md`](../website/OFFENE_PUNKTE.md).

## Etwas ändern

Die `index.html` lässt sich in jedem Texteditor bearbeiten. Danach den Ordner
erneut auf Netlify ziehen, das ersetzt die alte Version.

Wer häufiger ändert, fährt mit der Mehrseiten-Fassung unter `../website/`
besser. Sie hängt an Git, baut bei jedem Push automatisch und erzeugt zusätzlich
`sitemap.xml` und `robots.txt`. Anleitung dort im README.
