# Homepage — Engineering.Kabuu (PQ &amp; EMV)

Statische Homepage für einen unabhaengigen Ingenieur für Power Quality
(Netzqualität) und EMV. Sitz Schweiz.

- Framework: **Astro** (statisch) mit **Tailwind CSS**
- Deutsch, Schweizer Schreibweise (ss)
- Kein Blog, kein Shop, keine Tracker, kein Cookie-Banner
- Rechtstexte (Kontakt/Impressum, Datenschutz nach revDSG, AGB nach OR) sind
  **pruefungsbeduerftige Entwuerfe**
- Hosting: **Netlify** (Netlify Forms für das Kontaktformular)

---

## Lokal starten

Node LTS (>= 20) benoetigt.

```bash
cd website
npm install
npm run dev       # http://localhost:4321
npm run build     # produziert dist/
npm run preview   # rendert dist/ lokal
```

## Deployment auf Netlify

Die `netlify.toml` im Projekt-Root ist bereits konfiguriert. Zwei Wege:

### Weg 1 (empfohlen): Git verbinden

1. In Netlify: **Add new site → Import an existing project**
2. Repository verbinden (Ghostburaq/Burak), Branch waehlen
3. Netlify übernimmt aus der `netlify.toml`:
   - **Base directory**: `website`
   - **Build command**: `npm run build`
   - **Publish directory**: `website/dist`
   - **Node version**: 22
4. Deploy starten. Jeder weitere Push auf den Hauptbranch loest einen neuen Deploy
   aus. Feature-Branches erzeugen automatisch Deploy-Previews.

### Weg 2: Netlify CLI (einmalig)

```bash
npm install -g netlify-cli
netlify login
cd website
npm run build
netlify deploy --prod --dir=dist
```

### Domain verbinden

1. **Domain kaufen** (siehe `OFFENE_PUNKTE.md` &sect; 1).
2. In Netlify unter **Domain management → Add custom domain** die Domain
   hinterlegen. Netlify erstellt automatisch ein Let's-Encrypt-Zertifikat.
3. DNS beim Domain-Anbieter auf Netlify zeigen lassen (A-Record oder ANAME/CNAME
   auf die Netlify-Adresse).
4. In den Domain-Einstellungen die `netlify.app`-Subdomain auf die eigene Domain
   weiterleiten lassen (verhindert doppelten Inhalt).

**Es muss nichts im Code eingetragen werden.** Die Site-URL kommt beim Build aus
der Netlify-Umgebungsvariable `URL`, siehe `astro.config.mjs`. Canonical-Links,
`sitemap.xml`, `robots.txt` und `og:image` zeigen nach dem nächsten Deploy
automatisch auf die richtige Adresse. Lokal wird auf `http://localhost:4321`
zurückgefallen.

## Netlify Forms

Das Kontaktformular ist als statisches Netlify-Formular ausgezeichnet
(`data-netlify="true"`, verstecktes `form-name`-Feld, Honeypot `bot-field`,
`action="/danke"`). Es ist kein Formular-Dienstleister ausser Netlify eingebunden.

- Formulareingaenge stehen im Netlify-Dashboard unter **Forms → kontakt**.
- **E-Mail-Benachrichtigung** aktivieren: Netlify-Dashboard → Site → Forms → Settings
  and usage → Form notifications → Add notification (siehe `OFFENE_PUNKTE.md`).
- Kein reCAPTCHA und kein Tracking-Captcha eingebunden.

## Wo Inhalte editiert werden

| Inhalt                          | Datei                                                  |
| ------------------------------- | ------------------------------------------------------ |
| Firmen- und Kontaktdaten        | `src/lib/site.ts`                                      |
| Navigation                      | `src/lib/site.ts` (`nav`, `legalNav`)                  |
| Startseite (Hero, Teaser, CTA)  | `src/pages/index.astro`                                |
| Leistungen (6 Bloecke)          | `src/pages/leistungen.astro`                           |
| Ablauf/Methodik (6 Schritte)    | `src/pages/ablauf.astro`                               |
| Häufige Fragen                  | `src/pages/faq.astro`                                  |
| Über mich                       | `src/pages/ueber.astro`                                |
| Kontaktseite + Netlify-Formular | `src/pages/kontakt.astro`                              |
| Danke-Seite                     | `src/pages/danke.astro`                                |
| Kontakt/Impressum               | `src/pages/impressum.astro`                            |
| Datenschutz (revDSG)            | `src/pages/datenschutz.astro`                          |
| AGB (OR, CHF)                   | `src/pages/agb.astro`                                  |
| Design-Tokens (Farben, Fonts)   | `src/styles/global.css`, `tailwind.config.mjs`         |
| Layout / Header / Footer        | `src/layouts/BaseLayout.astro`, `src/components/`      |
| Logo-Komponente (Lockup)        | `src/components/Logo.astro`                            |
| Vorschaubild (Social)           | `scripts/make-og-image.py` → `public/og-image.png`     |
| robots.txt (dynamisch)          | `src/pages/robots.txt.ts`                              |
| Favicon, Logo-Dateien           | `public/`, `public/logo/`                              |
| Security-Header und CSP         | `netlify.toml`                                         |

## Farbtokens (aus dem Logo)

| Rolle           | Hex       | Verwendung                                         |
| --------------- | --------- | -------------------------------------------------- |
| signal-violett  | `#3317E9` | Primaerer Akzent (Links, Buttons, aktive Zustaende) |
| signal-magenta  | `#900B6F` | Sekundaer, sparsam                                 |
| signal-rot      | `#E2081B` | Nur Warn-/Stoerungsbezug                            |
| rahmen-stahl    | `#959AAF` | Nur dekorativ (Trenner, Rahmen). Nie für Text.     |
| anthrazit       | `#12151A` | Fliesstext und Ueberschriften                      |

## Vorschaubild neu erzeugen

`public/og-image.png` (1200x630) wird beim Teilen des Links angezeigt. Es wird
aus derselben Geometrie gezeichnet wie `public/logo/mark.svg`:

```bash
pip install Pillow
python3 scripts/make-og-image.py
```

## Einzeldatei-Fassung

Neben dieser Astro-Fassung liegt unter [`../netlify-single/`](../netlify-single/)
dieselbe Website als **eine einzelne HTML-Datei** zum Hochladen per
Drag-and-drop. Anleitung dort in `DEPLOY.md`. Beide Fassungen werden parallel
gepflegt und haben denselben Inhalt.

## Offene Punkte

**Alle** offenen Fragen (Domain, SVG-Logo, Handelsregister-Frage, Netlify-DPA,
MWST-Klärung, Rechtstext-Freigabe) sind zentral in
[`OFFENE_PUNKTE.md`](./OFFENE_PUNKTE.md) gesammelt. Zusaetzlich sind Luecken als
`TODO:`-Kommentare im Code markiert. Im ausgelieferten HTML ist kein sichtbares
`TODO:` mehr enthalten.

## Grundhaltung

- Nichts wird erfunden. Keine Kundennamen, keine Preise, keine Zertifikate,
  keine Normgrenzwerte ohne belegte Quelle. Alles Unbelegte ist `TODO:`.
- Norm-Bezug klar: das **Messgerät** erfüllt die Genauigkeitsklasse A nach
  IEC 61000-4-30. Nicht die Person &laquo;ist Class A zertifiziert&raquo;.
  Fabrikate und Typenbezeichnungen werden bewusst nirgends genannt.
- Referenzen bleiben anonymisiert bis zur schriftlichen Freigabe.
- Rechtstexte sind Schweizer Recht (revDSG, OR). Keine deutschen Rechtsbegriffe.
