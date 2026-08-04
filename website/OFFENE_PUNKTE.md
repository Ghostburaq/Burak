# OFFENE PUNKTE (vor Live-Gang klaeren)

Zentrale Sammlung aller Luecken. Nichts davon ist erfunden, alles wartet auf eine
Entscheidung, eine Angabe oder eine Pruefung. Sortiert nach Prioritaet.

Kontext: Sitz Schweiz. Rechtsform Einzelunternehmen. Marke Engineering.Kabuu.
Deployment auf Netlify. Sprache Schweizer Schreibweise (ss).

---

## 1. DOMAIN, LOGO, ASSETS

- [ ] **Domain festlegen** und im Netlify-Dashboard sowie in `astro.config.mjs`
      (`SITE_URL`) und `src/lib/site.ts` (`domain`) eintragen.
- [ ] **Logo-Assets pruefen und ggf. durch das Original ersetzen.**
      Das gelieferte Logo-Rendering wurde als Vektor nachgezeichnet, weil die
      Original-Dateien in dieser Session nicht als Datei-Upload vorlagen
      (nur als Bild im Chat sichtbar). Aktuell im Einsatz:
      - `public/logo/mark.svg` &mdash; Bildmarke: Sechseck-Rahmen mit
        Metallverlauf, darin Signalkurve und diagonaler Blitz-Slash.
        Verwendet in Header, Footer, Startseite, Danke-Seite, Favicon.
      - `public/logo/logo-lockup.svg` &mdash; vollstaendiges Lockup mit
        Wortmarke, Untertitel und ENGINEERING-Zeile. Verwendet als `og:image`
        und fuer externe Zwecke (Offerten, Briefpapier).
      - `src/components/Logo.astro` &mdash; setzt die Wortmarke auf der Website
        als echten Text, damit sie in jeder Groesse scharf bleibt.
      **Zu pruefen:** Die Nachzeichnung ist eine Annaeherung, keine exakte
      Kopie. Sobald die Original-Vektordatei (oder die PNGs
      `kabuu-signet-1024/512/256.png`, `kabuu-signet-flat-512.png`) vorliegt:
      unter `public/logo/` ablegen und die Referenzen in `Logo.astro`,
      `favicon.svg` und `SEO.astro` austauschen.
- [ ] **Schriftart der Wortmarke klaeren.** Im Rendering ist eine bestimmte
      Sans verwendet. Auf der Website laeuft die Wortmarke aktuell in der
      System-Sans der Seite. Falls die Original-Schrift verbindlich ist,
      Lizenz klaeren und selbst hosten (kein Google-Fonts-CDN, siehe Brief).
- [ ] Favicon-Set generieren (`favicon.ico`, `apple-touch-icon.png`,
      `site.webmanifest`) fuer aeltere Browser. Aktuell nur SVG-Favicon.
- [ ] **Social-Preview als PNG (1200x630)** erzeugen und in `SEO.astro` als
      `og:image` eintragen. Aktuell zeigt `og:image` auf
      `/logo/logo-lockup.svg`; viele Plattformen rendern SVG nicht.
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

- [ ] Referenzen: nur anonymisiert bis zur schriftlichen Freigabe des Kunden.

### 6.1 Aus UPDATE-01 (Ueber mich)

- [ ] **Wehrtechnik-Nennung freigeben.** Pruefen, ob die Nennung wehrtechnischer
      Anwendungen im Abschnitt &laquo;Hintergrund&raquo; einer Geheimhaltungspflicht
      gegenueber frueheren Auftraggebern oder Arbeitgebern unterliegt. Die
      Formulierung nennt bewusst keine Projekte, Typen oder Auftraggeber. Im
      Zweifel den Halbsatz streichen.
- [ ] **EMV-Liste bestaetigen.** Bestaetigen, dass mit den im Diktat genannten
      Kuerzeln EMI (Stoeraussendung) und EMS (Stoerfestigkeit) gemeint waren.
      Falls stattdessen ESD oder andere Pruefungen gemeint sind, die Liste im
      Abschnitt &laquo;EMV im Detail&raquo; korrigieren.
- [ ] **Pruefnormen.** Falls konkrete Pruefnormen genannt werden sollen, diese
      erst gegen die tatsaechlich angewendeten Fassungen pruefen. Bis dahin
      stehen bewusst keine Normnummern in diesem Abschnitt.
- [ ] **Kalibrierzertifikat.** Falls fuer Gutachten oder Beweissicherung ein
      Kalibrierzertifikat einer akkreditierten Stelle vorliegt, im Abschnitt
      &laquo;Ausstattung&raquo; ergaenzen. Nur eintragen, was vorhanden ist.
- [ ] **Berufshaftpflicht.** Pruefen, ob Versicherer und Deckungssumme genannt
      werden sollen. Viele Auftraggeber aus Industrie und Recht fragen danach;
      eine konkrete Deckungssumme wirkt dort staerker als die blosse Erwaehnung.
      Angabe erst nach Abgleich mit der Police.
- [ ] **Zertifikate und Mitgliedschaften.** Der Block ist auskommentiert und
      damit unsichtbar, bis echte Angaben vorliegen. Struktur je Eintrag:
      Bezeichnung des Zertifikats oder der Qualifikation, ausstellende Stelle,
      Jahr bzw. Gueltigkeit. Nichts erfinden, nichts andeuten. Nach dem Eintragen
      den Block wieder einkommentieren (in `ueber.astro` und in
      `netlify-single/index.html`).
- [ ] **Berufsbezeichnung.** Klaeren, ob die Bezeichnung &laquo;Ingenieur&raquo;
      gefuehrt werden darf und wie sie geschrieben wird. Der sichtbare Platzhalter
      auf der Seite wurde entfernt; die Frage lebt nur noch hier.

### 6.2 Aus UPDATE-01 (Haeufige Fragen)

Vier Fragen haben noch keine Antwort und stehen deshalb **nicht** auf der Seite,
damit dort kein sichtbarer Platzhalter erscheint. Sobald eine Antwort vorliegt,
in `src/pages/faq.astro` (Array `faq`) und in `netlify-single/index.html`
(Abschnitt `#faq`) ergaenzen.

- [ ] **Muss die Anlage dafuer abgeschaltet werden?** Diese Frage entscheidet bei
      Industriekunden haeufig ueber die Anfrage. Formulieren, unter welchen
      Bedingungen der Messaufbau im laufenden Betrieb moeglich ist und wann eine
      Freischaltung durch eine Elektrofachkraft noetig wird.
- [ ] **Was kostet eine Messung?** Keine Preisliste noetig, aber eine Aussage zur
      Preislogik (Fixpreis pro Messkampagne, Aufwand nach Zeit, Reisekosten
      separat) senkt die Hemmschwelle deutlich. Mit Treuhaender abstimmen, bevor
      Zahlen genannt werden. Beachten: auf der Website stehen weiterhin keine Preise.
- [ ] **Wie schnell ist ein Messtermin moeglich?** Realistische Vorlaufzeit
      angeben, abhaengig von der Geraeteverfuegbarkeit.
- [ ] **In welchem Gebiet sind Sie im Einsatz?** Einsatzradius und Regelung zu
      Reisekosten festlegen.

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

---

## AENDERUNGSPROTOKOLL

### UPDATE-01

Geaendert wurden beide Fassungen: die Astro-Seite unter `website/` und die
Einzeldatei `netlify-single/index.html`.

| Abschnitt | Was geaendert wurde |
| --- | --- |
| Umlaute | Alle ASCII-Umschreibungen durch echte Umlaute ersetzt (ueber 130 Woerter). Der Name lautet jetzt durchgehend **Burak Ücöz**. IDs, Anker, Routen und ARIA-Referenzen bleiben bewusst ASCII, damit keine internen Links brechen. |
| A | Herstellernennung restlos entfernt: Fabrikat und Typenbezeichnung stehen nirgends mehr, auch nicht in Meta-Tags, Alt-Texten oder strukturierten Daten. Startseite, Leistungen, Ablauf Schritt 03 und Ausstattung neu formuliert. |
| B | `ueber.astro`: Abschnitt &laquo;Hintergrund&raquo; mit dem gelieferten Text gefuellt, TODO-Platzhalter entfernt. |
| C | `ueber.astro`: neuer Abschnitt &laquo;EMV im Detail&raquo; mit sechs Disziplinen und Abschlusssatz. Bewusst ohne Normnummern. |
| D | `ueber.astro`: Abschnitt &laquo;Ausstattung&raquo; vollstaendig ersetzt. Kalibrierintervall und Verzicht auf Fabrikatsnennung neu drin. |
| E | `ueber.astro`: neuer Abschnitt &laquo;Absicherung&raquo; (Berufshaftpflichtversicherung). |
| F | &laquo;Zertifikate und Mitgliedschaften&raquo; auskommentiert statt geloescht, mit Struktur zum spaeteren Ausfuellen. Der Platzhalter ist damit oeffentlich unsichtbar. |
| G | Sichtbarer TODO-Platzhalter zur Berufsbezeichnung entfernt. Die Frage steht nur noch hier. |
| H | `kontakt.astro`: neuer Einleitungstext ueber dem Formular. Drei zusaetzliche, freiwillige Felder ergaenzt: Standort der Anlage, Spannungsebene, Dringlichkeit. Alle mit verknuepften Labels. |
| I | Neue Seite `faq.astro` (in der Einzeldatei: Abschnitt `#faq`), eingehaengt zwischen Ablauf und Ueber mich, auch in der Navigation. Zwei Fragen sind beantwortet, vier stehen offen und wurden bewusst weggelassen statt als Platzhalter gezeigt (siehe 6.2). |
| J | Startseite: neuer Vertrauensblock &laquo;Woher die Einschaetzung kommt&raquo; unterhalb von &laquo;Fuer wen&raquo;. |
| K | Firmen-&laquo;wir&raquo; entfernt. Startseite auf &laquo;Gemeinsam legen wir einen Messplan fest&raquo; umgestellt, Impressum auf &laquo;die Anbieterin&raquo;. In den Rechtstexten bleibt &laquo;die Anbieterin&raquo; als juristischer Begriff. |

Unveraendert gueltig: keine erfundenen Fakten, keine Preise auf der Website,
keine Normgrenzwerte als Zahlenwerte, keine Kundennamen, keine UID oder
MWST-Nummer.
