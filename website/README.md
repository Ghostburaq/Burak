# Homepage — Kabuu Engineering (PQ & EMV)

Statische Homepage fuer einen unabhaengigen Ingenieur fuer Power Quality
(Netzqualitaet) und EMV. Firmensitz Deutschland, Kundschaft Schweiz.

- Framework: **Astro** (statisch) mit **Tailwind CSS**
- Deutsch als einzige aktive Sprache beim Launch (`fr/`, `it/` sind vorbereitet
  aber noch nicht angelegt)
- Kein Blog, kein Shop, keine Tracker, kein Cookie-Banner
- Alle Rechtstexte (Impressum, Datenschutz, AGB) sind pruefungsbeduerftige
  **Entwuerfe**

Sprachregel: Chat und Arbeitskommunikation in Schweizer Schreibweise (ss).
Website-Inhalte fuer Schweizer Kunden ebenfalls in Schweizer Schreibweise.
Rechtstexte fuer die deutsche Firma folgen deutscher Rechtschreibung.

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

Das Verzeichnis enthaelt bereits eine `netlify.toml`.

- **Base directory**: `website`
- **Build command**: `npm run build`
- **Publish directory**: `website/dist`
- **Node version**: 22 (via `NODE_VERSION` in `netlify.toml`)

Nach Registrierung der Domain:

1. Domain in `astro.config.mjs` bei `SITE_URL` eintragen.
2. Domain in `src/lib/site.ts` bei `domain` eintragen.
3. Neu deployen. Sitemap wird automatisch mit korrekten URLs erzeugt.

## Umgebungsvariablen

Nur eine Variable, siehe `.env.example`:

- `PUBLIC_CONTACT_ENDPOINT` — Endpoint fuer das Kontaktformular
  (Netlify Forms / Formspree / eigene Function). Ohne Wert greift ein
  `mailto:`-Fallback (Notloesung, im Formular sichtbar markiert).

## Wo Inhalte editiert werden

| Inhalt                          | Datei                                                  |
| ------------------------------- | ------------------------------------------------------ |
| Firmen- und Kontaktdaten        | `src/lib/site.ts`                                      |
| Navigation                      | `src/lib/site.ts` (`nav`, `legalNav`)                  |
| Startseite (Hero, Teaser, CTA)  | `src/pages/index.astro`                                |
| Leistungen (6 Bloecke)          | `src/pages/leistungen.astro`                           |
| Ablauf/Methodik (6 Schritte)    | `src/pages/ablauf.astro`                               |
| Ueber mich                      | `src/pages/ueber.astro`                                |
| Kontaktseite + Formular         | `src/pages/kontakt.astro`                              |
| Impressum                       | `src/pages/impressum.astro`                            |
| Datenschutz                     | `src/pages/datenschutz.astro`                          |
| AGB                             | `src/pages/agb.astro`                                  |
| Design-Tokens (Farben, Fonts)   | `src/styles/global.css`, `tailwind.config.mjs`         |
| Layout / Header / Footer        | `src/layouts/BaseLayout.astro`, `src/components/`      |
| Robots, Favicon                 | `public/`                                              |

## Offene Punkte

**Alle** offenen Fragen (Fakten, Steuer/MwSt-Klaerung, Rechtstext-Freigabe,
Formular-Dienst, Domain, Logo) sind zentral in [`OFFENE_PUNKTE.md`](./OFFENE_PUNKTE.md)
gesammelt. Zusaetzlich sind Luecken im Code als `TODO:` markiert.

## Grundhaltung

- Nichts wird erfunden. Keine Kundennamen, keine Preise, keine Zertifikate,
  keine Normgrenzwerte ohne belegte Quelle. Alles Unbelegte ist `TODO:`.
- Norm-Bezug klar: das **Messgeraet** (Camille Bauer Metrawatt PQMobile5000)
  erfuellt Klasse A nach IEC 61000-4-30. Nicht die Person "ist Class A".
- Referenzen bleiben anonymisiert, bis eine explizite Namensfreigabe vorliegt.
