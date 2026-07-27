# OFFENE PUNKTE (vor Live-Gang klaeren)

Diese Datei sammelt alle Luecken. Nichts davon ist erfunden, alles wartet auf eine
Entscheidung, eine Angabe oder eine Pruefung. Sortiert nach Prioritaet.

Sprachhinweis: Diese Datei ist Arbeitskommunikation und in Schweizer Schreibweise
(ss). Die Rechtstexte (Impressum, Datenschutz, AGB) folgen bewusst deutscher
Rechtschreibung, siehe Abschnitt Rechtstexte.

---

## 1. FAKTEN (unbedingt, sonst Platzhalter live)

- [ ] Firmenname / Absendermarke: aktuell "Kabuu Engineering" als Annahme.
      Wenn anders gewuenscht, in `src/lib/site.ts` (`brand`) aendern und in
      Header, Footer, Impressum, Datenschutz, AGB pruefen.
- [ ] Ladungsfaehige Anschrift in Deutschland (Strasse, PLZ, Ort). Kein Postfach.
      Aendern in `src/lib/site.ts` (`address`).
- [ ] Geschaeftliche E-Mail (nicht privat, wenn moeglich eigene Domain).
- [ ] Telefonnummer (mit Landesvorwahl).
- [ ] Domain (nach Registrierung eintragen in `astro.config.mjs` -> `SITE_URL`
      und in `src/lib/site.ts` -> `domain`).
- [ ] Logo: aktuell wird ein SVG-Sinuskurven-Icon verwendet. Falls ein echtes
      Logo vorliegt, in `public/` ablegen und in `Header.astro`/`Footer.astro`
      einbinden.
- [ ] Portrait fuer die Seite "Ueber mich" optional.

## 2. STEUER / MWST (heikel, mit Treuhaender/Steuerberater klaeren)

- [ ] Umsatzsteuerstatus in Deutschland: Kleinunternehmer nach Paragraf 19 UStG
      bestaetigt oder nicht? Keine pauschale Behauptung ohne Pruefung.
- [ ] USt-IdNr. vorhanden? Wenn ja, in Impressum eintragen. Wenn nein, Abschnitt
      im Impressum ersatzlos streichen (nicht erfinden).
- [ ] Wirtschafts-Identifikationsnummer (W-IdNr.): nur eintragen, wenn tatsaechlich
      vergeben.
- [ ] B2B-Leistungen an Schweizer Kunden: Leistungsort liegt in der Regel in der
      Schweiz (Paragraf 3a Abs. 2 UStG). Der pauschale Paragraf-19-Vermerk
      passt inhaltlich nicht auf diese Umsaetze. Klaerung erforderlich, wie
      Rechnungen korrekt gestellt werden.
- [ ] Schweizer MWST-Registrierungspflicht pruefen. Ankntuepfung u.a.:
      weltweiter Umsatz ab CHF 100'000 UND Leistungen in der Schweiz. Bei
      Registrierungspflicht: Schweizer Steuervertreter noetig.
- [ ] Rechnungs- und Offertenvorlagen erst erstellen, wenn die Punkte oben
      geklaert sind. Auf der Website stehen daher bewusst keine Preise und
      kein pauschaler MwSt-Satz.

## 3. RECHTSTEXTE (Entwuerfe, durch Anwalt/Fachperson pruefen lassen)

Alle drei Texte sind mit `DraftBanner` als Entwurf gekennzeichnet und folgen
deutscher Rechtschreibung.

- [ ] Impressum (Paragraf 5 DDG) durchgehen:
      - Umsatzsteuer-Angaben je nach Fakten-Block einsetzen oder streichen.
      - Berufsrechtliche Angaben zur Bezeichnung "Ingenieur" pruefen (je Bundesland
        Ingenieurkammer/Ingenieurgesetz). Falls die Bezeichnung nicht gefuehrt
        wird, Abschnitt ersatzlos streichen.
      - Streitbeilegungshinweis auf aktuelle Rechtslage pruefen. Die EU-OS-
        Plattform wurde 2025 eingestellt, kein alter OS-Link mehr.
- [ ] Datenschutz (DSGVO + revDSG):
      - Hoster benennen, AVV/SCC, Speicherort/Drittlandbezug.
      - Formular-Dienstleister benennen, AVV, Datenhaltung.
      - Zustaendige Landesdatenschutzbehoerde nach Sitz einsetzen.
      - Pruefen, ob nach Art. 14 revDSG eine Vertretung in der Schweiz
        erforderlich ist (fuer eine kleine Beratungs-Website mit Kontaktformular
        i.d.R. nicht, aber Pruefung dokumentieren).
      - "Stand: TODO" durch tatsaechliches Datum ersetzen.
- [ ] AGB (Entwurf):
      - Rechtswahl und Gerichtsstand mit Anwalt festlegen (deutsches Recht ODER
        Schweizer Recht, nicht mischen).
      - Haftungsbegrenzung finalisieren (Hoehe, Ausschluss Folgeschaeden,
        Verjaehrung).
      - Frist und Aufwandspauschale bei Terminabsage konkretisieren.

## 4. FORMULAR-DIENST

Der Formular-Endpoint ist zentral in `.env` als `PUBLIC_CONTACT_ENDPOINT`
gekapselt und wird in `src/pages/kontakt.astro` verwendet. Ohne Endpoint greift
ein `mailto:`-Fallback (Notloesung, im Formular sichtbar markiert).

- [ ] Anbieter auswaehlen. Vorschlaege mit Datenhaltung in EU/CH:
      - **Netlify Forms** (falls Hosting auf Netlify): einfach, Formulare landen
        im Netlify-Dashboard, Datenhaltung siehe Netlify-DPA.
      - **Formspree** (EU-Region moeglich).
      - **Basin** / **Getform** (Alternativen).
      - Eigene Serverless Function beim Hoster (mehr Kontrolle, mehr Aufwand).
- [ ] AVV mit dem gewaehlten Anbieter abschliessen und in der
      Datenschutzerklaerung eintragen.
- [ ] Spam-Schutz waehlen (Honeypot-Feld, Cloudflare Turnstile, hCaptcha).
      Aktuell ist kein Spam-Schutz aktiv.

## 5. INHALTLICHES (freischalten oder nachschaerfen)

- [ ] "Ueber mich"-Kurzprofil: Ausbildung, Stationen, Praxisschwerpunkt.
      Nur belegbare Angaben, frueherer Arbeitgeber nur nach Freigabe.
- [ ] Berufsbezeichnung: pruefen, ob "Ingenieur" gefuehrt werden darf.
- [ ] Referenzen: bleiben anonymisiert, bis eine schriftliche Namensfreigabe des
      jeweiligen Kunden vorliegt.
- [ ] Zertifikate/Mitgliedschaften: nur eintragen, wenn tatsaechlich vorhanden.
- [ ] Zusatz-Messmittel (Thermografie, Oszilloskop, EMV-Nahfeldsonden) auflisten,
      sofern verfuegbar.

## 6. TECHNISCHES

- [ ] Site-URL in `astro.config.mjs` nach Domain-Wahl setzen (wichtig fuer
      Sitemap und Canonical-Links).
- [ ] Falls spaeter Analytics gewuenscht: nur cookielose, datensparsame Loesung
      (z.B. Plausible EU, Umami self-hosted). Andernfalls TDDDG-Konformitaet
      und Cookie-Banner beachten und Datenschutztext erweitern.
- [ ] Lighthouse-Check nach dem ersten Live-Deploy: Ziel gruen in allen vier
      Kategorien.
- [ ] Screen-Reader-Test der Formular-Labels und Fokus-Zustaende.

## 7. STRUKTUR I18N (spaeter)

Verzeichnisse `fr/` und `it/` sind noch nicht angelegt, weil Deutsch beim Launch
die einzige aktive Sprache ist. Wenn spaeter erweitert werden soll:
- Struktur `src/pages/{de,fr,it}/...` einfuehren
- Sprachumschalter im Header
- `hreflang`-Tags in `SEO.astro`
