# OFFENE PUNKTE (vor Live-Gang klaeren)

Zentrale Sammlung aller Luecken. Nichts davon ist erfunden, alles wartet auf eine
Entscheidung, eine Angabe oder eine Pruefung. Sortiert nach Prioritaet.

Kontext: Sitz Schweiz. Rechtsform Einzelunternehmen. Marke Engineering.Kabuu.
Deployment auf Netlify. Sprache Schweizer Schreibweise (ss).

---

## 1. DOMAIN, LOGO, ASSETS

- [ ] **Domain festlegen** und im Netlify-Dashboard sowie in `astro.config.mjs`
      (`SITE_URL`) und `src/lib/site.ts` (`domain`) eintragen.
- [ ] **Logo-Assets.** Aktuell im Einsatz sind zwei selbst gezeichnete
      Vektor-Fassungen des Motivs:
      - `public/logo/signet.svg` (breit, waveform ueber alle drei Zonen &mdash;
        rot transient, magenta einschwingend, blau/violett stabil, Stahl-Balken
        als Messreferenz). Wird auf der Startseite als Motiv verwendet.
      - `public/logo/mark.svg` (kompakt, quadratisch). Wird in Header, Footer
        und Favicon verwendet.
      Die im Brief genannten 3D-Renderings (`kabuu-signet-1024/512/256.png`
      und `kabuu-signet-flat-512.png`) wurden zwar visuell im Chat gezeigt,
      liegen in der Session aber nicht als Dateien vor. Wenn die Original-PNGs
      oder das offizielle Vektor-Logo vorliegen, unter `public/logo/` ablegen
      und Header/Footer/Favicon-Referenzen entsprechend austauschen.
- [ ] Favicon-Set generieren (`favicon.ico`, `apple-touch-icon.png`,
      `site.webmanifest`) fuer aeltere Browser. Aktuell nur SVG-Favicon.
- [ ] **GLB (3D-Version) NICHT einbinden** &mdash; bewusst nicht integrieren
      (Bundle-Groesse, Lighthouse). Statische Renderings genuegen.

## 2. FIRMENRECHTLICHES

- [ ] **Firmenname pruefen.** Nach Art. 945 OR muss bei einer Einzelfirma der
      Familienname wesentlicher Bestandteil der Firma sein. &laquo;Engineering.Kabuu&raquo;
      ist damit eher Geschaeftsbezeichnung/Marke als eingetragene Firma. Mit
      Treuhaender klaeren, ob und wie die Firma im Handelsregister gefuehrt wird.
      Danach Abschnitt &laquo;Firmenname und Handelsregister&raquo; in
      `src/pages/impressum.astro` anpassen oder streichen.
- [ ] **Berufsbezeichnung &laquo;Ingenieur&raquo;.** Klaeren, ob die Bezeichnung
      gefuehrt werden darf und wie sie geschrieben wird, bevor sie auf der Seite
      verwendet wird. Bis dahin steht ein TODO auf `src/pages/ueber.astro`.

## 3. MWST / STEUERN (mit Treuhaender)

- [ ] **MWST-Warnhinweis.** Die Befreiung von der MWST-Pflicht (Umsatz unter
      CHF 100'000 nach MWSTG) entfaellt, sobald der weltweite Jahresumsatz die
      Schwelle erreicht. Dann besteht Anmeldepflicht und die Preise sind neu zu
      kalkulieren. Rechtzeitig ueberwachen und Offerten-/Rechnungsvorlagen anpassen.
- [ ] **Leistungen an Kunden im Ausland.** Steuerliche Behandlung mit Treuhaender
      klaeren, bevor Offerten- und Rechnungsvorlagen erstellt werden.
- [ ] **Status einer allenfalls bestehenden Registrierung in Deutschland.**
      Vollstaendigkeit pruefen. Auf der Website steht bewusst keine deutsche
      Rechtsterminologie (§ 19 UStG etc.); die Formulierung in den AGB ist auf
      Schweizer Recht abgestellt.

## 4. NETLIFY / HOSTING / DATENSCHUTZ

- [ ] **DPA mit Netlify.** Auftragsbearbeitungsvertrag (Data Processing Addendum)
      abschliessen bzw. die Annahme dokumentieren. In der Datenschutzerklaerung
      unter Ziffer 4 eingetragen als TODO.
- [ ] **Grundlage der Bekanntgabe ins Ausland** (u.a. USA) nach revDSG konkret
      benennen (z.B. Standardvertragsklauseln, anerkannte Angemessenheitsentscheidung).
      Aktuellen Stand abklaeren. In `src/pages/datenschutz.astro` Ziffer 5 einsetzen.
- [ ] **Aufbewahrungsdauer** der Formulareingaenge festlegen und in
      `src/pages/datenschutz.astro` Ziffer 6 eintragen.
- [ ] **E-Mail-Benachrichtigung** fuer Formulareingaenge im Netlify-Dashboard
      aktivieren.
- [ ] **Netlify-Formular-Limits** im gewaehlten Plan pruefen (aktuelle Kontingente
      koennen sich aendern).
- [ ] **CSP-Header** nach dem ersten Live-Deploy im Browser (DevTools -> Console)
      auf Verstoesse pruefen. Aktuell schlank gesetzt in `netlify.toml`.
- [ ] **EU-Kunden / DSGVO.** Pruefen, ob durch gezielte Ansprache von EU-Kunden
      zusaetzlich die DSGVO greift und die Datenschutzerklaerung ergaenzt werden muss.

## 5. RECHTSTEXTE (durch Anwalt pruefen lassen)

Alle drei Texte sind mit `DraftBanner` als Entwurf gekennzeichnet und in Schweizer
Schreibweise verfasst.

- [ ] **Kontakt/Impressum:** Abschnitt Firmenname/Handelsregister nach Klaerung
      anpassen oder streichen.
- [ ] **Datenschutz:** siehe Abschnitt 4 (Netlify, Bekanntgabe, Aufbewahrung, DSGVO).
      &laquo;Stand: TODO&raquo; durch tatsaechliches Datum ersetzen.
- [ ] **AGB:** Haftungshoechstsumme, Verjaehrung, Frist bei Terminabsage,
      Gerichtsstand, Aufbewahrungsfrist Messdaten mit Anwalt finalisieren.

## 6. INHALTLICHES

- [ ] Kurzprofil auf `src/pages/ueber.astro` (Abschnitt &laquo;Hintergrund&raquo;)
      ausfuellen. Nur belegbare Angaben. Frueherer Arbeitgeber nur nach
      ausdruecklicher Freigabe.
- [ ] Zertifikate / Mitgliedschaften nur eintragen, wenn tatsaechlich vorhanden.
- [ ] Zusatz-Messmittel (Thermografie, Oszilloskop, EMV-Nahfeldsonden) auflisten,
      sofern vorhanden.
- [ ] Referenzen: nur anonymisiert bis zur schriftlichen Freigabe des Kunden.

## 7. QUALITAETSSICHERUNG

- [ ] Lighthouse nach erstem Live-Deploy in allen vier Kategorien pruefen. Ziel: gruen.
- [ ] Screen-Reader-Test der Formular-Labels und Fokus-Zustaende.
- [ ] Farb-Kontraste stichprobenartig in DevTools pruefen (WCAG 2.1 AA).
- [ ] Robots.txt und sitemap.xml nach Domain-Setzung auf korrekte URLs pruefen.

## 8. SPRACHERWEITERUNG (spaeter)

Verzeichnisse `fr/` und `it/` sind noch nicht angelegt. Beim Launch ist Deutsch die
einzige aktive Sprache. Fuer spaetere Erweiterung:
- `src/pages/{de,fr,it}/...`-Struktur einfuehren
- Sprachumschalter im Header
- `hreflang`-Tags in `SEO.astro`
