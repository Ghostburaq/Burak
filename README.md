# NEXA — Website

Statische Firmen-Website für **NEXA** (KI-Automation, CRM & Web-/App-Entwicklung
für KMU im DACH-Raum). Reines HTML, CSS und minimales Vanilla-JavaScript –
kein Framework, keine Build-Kette. Einfach öffnen oder hochladen.

## Struktur

```
index.html          Startseite (One-Pager)
impressum.html      Impressum (Rechtsseite)
datenschutz.html    Datenschutzerklärung (Rechtsseite)
assets/
  styles.css        Zentrales Stylesheet für alle Seiten
  script.js         Scroll-Animationen + Nav-Verhalten (progressive enhancement)
  logo.svg          Logo (N aus Netzknoten, "NEXUS"-Konzept)
  favicon.svg       Favicon (vereinfachtes N)
README.md           Diese Datei
```

## Lokal öffnen

Doppelklick auf `index.html` genügt – die Seite läuft ohne Server.

Wer sie wie im Web ausliefern will (empfohlen, damit relative Pfade und
Fonts sauber laden), startet einen kleinen lokalen Server:

```bash
# Python (auf den meisten Systemen vorinstalliert)
python3 -m http.server 8000
# dann im Browser: http://localhost:8000
```

## Texte anpassen

Alle Inhalte stehen direkt im HTML – keine Datenbank, kein CMS.

- **Startseite:** `index.html` – Headlines, Leistungen, Ablauf, Kontakt.
- **Kontakt-Button:** In `index.html` die Zeile mit
  `mailto:kontakt@nexa.ch` auf deine echte Adresse oder einen Buchungslink
  (z. B. Cal.com / Calendly) ändern. Ist im Code als Platzhalter kommentiert.
- **Impressum:** `impressum.html` – alle Platzhalter in eckigen Klammern
  `[…]` mit deinen echten Angaben ersetzen (Adresse, E-Mail, ggf. UID/MWST).
- **Datenschutz:** `datenschutz.html` – Platzhalter ersetzen, besonders
  Hosting-Anbieter (Ziffer 5) und Stand (Ziffer 10).
  Hinweis: Die Rechtstexte sind eine Vorlage, **keine Rechtsberatung** –
  vor Live-Gang prüfen lassen.
- **Farben / Schrift:** zentral in `assets/styles.css` ganz oben unter
  `:root` (CSS-Variablen). Eine Akzentfarbe (`--accent`), sonst nur
  Grautöne des Design-Systems.

## Deployen

### Variante A — Netlify (am schnellsten)

1. Auf [app.netlify.com/drop](https://app.netlify.com/drop) gehen.
2. Den **gesamten Projektordner** ins Browserfenster ziehen.
3. Fertig – du bekommst sofort eine Live-URL.
4. Eigene Domain (z. B. `nexa.ch`) unter *Domain settings* verbinden.

Alternativ mit Git-Anbindung: Repo mit Netlify verknüpfen, *Build command*
leer lassen, *Publish directory* auf das Projekt-Root setzen. Jeder Push
ist dann automatisch live.

### Variante B — GitHub Pages

1. Projekt in ein GitHub-Repository pushen.
2. Im Repo: *Settings → Pages*.
3. Unter *Build and deployment* → *Source*: **Deploy from a branch**.
4. Branch wählen (z. B. `main`), Ordner `/ (root)`, **Save**.
5. Nach kurzer Zeit ist die Seite unter
   `https://<username>.github.io/<repo>/` erreichbar.

> Liegt die Website nicht im Repo-Root, sondern in einem Unterordner,
> muss dieser Ordner als Quelle gewählt werden (oder die Dateien ins Root
> verschoben werden), damit `index.html` gefunden wird.

## Technisches

- Semantisches HTML5, ein `<h1>` pro Seite, `lang="de-CH"`.
- Meta-Tags (title, description, viewport) je Seite, Open Graph auf der Startseite.
- Google Fonts (Space Grotesk + Inter) via `<link preconnect>`.
- Barrierefrei: sichtbarer Tastatur-Fokus, Skip-Link, `prefers-reduced-motion`
  wird respektiert.
- Läuft auch **ohne JavaScript** vollständig – Animationen sind reine
  progressive Verbesserung, das Mobile-Menü hat einen `:target`-Fallback.
- Keine externen Bilder, keine Libraries, kein Tracking.
