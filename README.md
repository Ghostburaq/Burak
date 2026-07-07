# NEXA — Website

Statische Firmen-Website für **NEXA** (KI-Automation, CRM & Web-/App-Entwicklung
für KMU im DACH-Raum). Reines HTML, CSS und minimales Vanilla-JavaScript –
kein Framework, keine Build-Kette. **Schriften werden lokal gehostet** (DSGVO),
nicht über Google-Server geladen.

## Struktur

```
index.html          Startseite (One-Pager)
impressum.html      Impressum (§ 5 DDG)
datenschutz.html    Datenschutzerklärung (DSGVO + revDSG-Hinweis)
danke.html          Bestätigungsseite nach dem Kontaktformular
404.html            Fehlerseite im Markendesign
robots.txt · sitemap.xml · site.webmanifest · _headers
assets/
  styles.css        Zentrales Stylesheet (inkl. @font-face)
  script.js         Scroll-Animationen, Nav-Verhalten, Mobile-Menü
  logo.svg          Logo (N aus Netzknoten, "NEXUS"-Konzept)
  favicon.svg       Favicon (vereinfachtes N)
  og-image.png      Vorschaubild fürs Teilen (1200×630)
  fonts/            Lokale Schriftdateien (woff2)
README.md           Diese Datei
```

## Schriften (lokal, DSGVO)

Die Seite lädt **keine** Schriften von `fonts.googleapis.com`. Stattdessen liegen
die Dateien lokal in `assets/fonts/` und werden per `@font-face` in `styles.css`
eingebunden (`font-display: swap`, sauberer System-Fallback).

**Bereits enthalten** (Variable Fonts, je eine Datei pro Subset):
```
space-grotesk-latin.woff2      space-grotesk-latin-ext.woff2
inter-latin.woff2              inter-latin-ext.woff2
```
Damit funktioniert die Seite out of the box. Es ist nichts weiter zu tun.

**Falls du die Schriften erneuern/austauschen willst** (z. B. weitere Subsets):
1. Auf **google-webfonts-helper** (`gwfh.mranftl.com`) gehen.
2. *Space Grotesk* (Weights 500/600/700) und *Inter* (Weights 400/500/600) wählen,
   Subsets `latin` + `latin-ext`, Format **woff2**.
3. Die woff2-Dateien nach `assets/fonts/` legen.
4. In `styles.css` unter Abschnitt „0. LOKALE SCHRIFTEN" die `src`-Pfade und
   `unicode-range`-Angaben prüfen/anpassen.

Fehlen die Font-Dateien, bleibt die Seite dank System-Fallback voll lesbar.

## Lokal öffnen

Am besten über einen kleinen Server (damit `@font-face` und relative Pfade
sauber laden):

```bash
python3 -m http.server 8000
# dann im Browser: http://localhost:8000
```
Ein Doppelklick auf `index.html` funktioniert auch, dann greift ggf. der
System-Font-Fallback statt der lokalen Schriften.

## Texte anpassen

Alle Inhalte stehen direkt im HTML – keine Datenbank, kein CMS.

- **Team:** In `index.html` (Abschnitt „5. TEAM") Lucas **Nachname** und
  **Kurztext** eintragen (Platzhalter `[…]`). LinkedIn-Links sind gesetzt.
- **Kontaktformular (Netlify Forms):** Wird beim Deploy automatisch erkannt
  (`data-netlify="true"`). Anfragen erscheinen im Netlify-Dashboard unter
  *Forms*. Für sofortige Mail-Benachrichtigung: Netlify → *Forms → Notifications
  → Add notification → Email* und deine Adresse eintragen. Es muss **keine**
  eigene E-Mail-Adresse existieren und **nichts** gehostet werden.
- **Direkte E-Mail:** aktuell `engineering.kabuu@gmail.com` (Kontaktbereich +
  Impressum + Datenschutz). Bei eigener Domain später z. B. `kontakt@nexa.ch`.
- **Impressum:** `impressum.html` – Rechtsform-Variante wählen (GbR **oder**
  UG/GmbH), Nachname, Telefon, USt-Variante, ggf. Registerdaten ausfüllen.
- **Datenschutz:** `datenschutz.html` – Rechtsform in Ziffer 1, Hosting in
  Ziffer 4 und Stand in Ziffer 13 prüfen.
  Hinweis: Die Rechtstexte sind eine **Vorlage, keine Rechtsberatung** –
  vor Live-Gang durch Anwalt oder geprüften Generator kontrollieren lassen.
- **Farben:** zentral in `assets/styles.css` unter `:root`. Eine Akzentfarbe
  (`--accent`), sonst nur die Grautöne des Design-Systems.

## Deployen

### Variante A — Netlify (am schnellsten)

1. Auf [app.netlify.com/drop](https://app.netlify.com/drop) gehen.
2. Den **gesamten Projektordner** (inkl. `assets/fonts/`) ins Fenster ziehen.
3. Fertig – du bekommst sofort eine Live-URL.
4. *Forms → Notifications* einrichten (siehe oben).
5. Eigene Domain (z. B. `nexa.ch`) unter *Domain settings* verbinden. Danach die
   `netlify.app`-URLs in `canonical`, Open Graph, `robots.txt`, `sitemap.xml`
   und der JSON-LD auf die neue Domain ändern.

Alternativ mit Git-Anbindung: Repo mit Netlify verknüpfen, *Build command* leer
lassen, *Publish directory* auf das Projekt-Root setzen. Jeder Push ist dann live.

### Variante B — GitHub Pages

1. Projekt in ein GitHub-Repository pushen.
2. Im Repo: *Settings → Pages*.
3. *Source*: **Deploy from a branch**, Branch wählen, Ordner `/ (root)`, **Save**.
4. Erreichbar unter `https://<username>.github.io/<repo>/`.

> Hinweis: Das Kontaktformular nutzt **Netlify Forms** und funktioniert nur auf
> Netlify. Auf GitHub Pages bleibt die direkte E-Mail als Kontaktweg.

## Technisches

- Semantisches HTML5, ein `<h1>` pro Seite, `lang="de"`.
- Meta-Tags (title, description, viewport) je Seite, Open Graph (`og:locale`
  `de_CH`) + Twitter Card + JSON-LD auf der Startseite.
- Schriften lokal via `@font-face` – keine Verbindung zu Google-Servern.
- Barrierefrei: sichtbarer Tastatur-Fokus, Skip-Link, `prefers-reduced-motion`.
- Läuft auch **ohne JavaScript** vollständig – Animationen sind progressive
  Verbesserung, das Mobile-Menü hat einen `:target`-Fallback.
- Keine externen Bilder, keine externen Skripte, keine Libraries, kein Tracking.
