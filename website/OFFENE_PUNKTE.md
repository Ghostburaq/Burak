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
- [ ] **Lizenzklasse Amateurfunk verifizieren.** Auf der Seite steht bewusst
      Variante 1 ohne Klassenangabe: &laquo;Amateurfunkzeugnis, Rufzeichen
      DO1BUU.&raquo; Erst nach Pruefung auf Variante 2 wechseln
      (&laquo;Amateurfunkzeugnis Klasse A und Klasse E, Rufzeichen DO1BUU.&raquo;).
      In Deutschland ist das Rufzeichenpraefix DO der Klasse E zugeordnet; beim
      Erwerb der Klasse A wird in der Regel ein Rufzeichen mit anderem Praefix
      zugeteilt. Angabe im Amateurfunkzeugnis bzw. in der Zulassungsurkunde
      pruefen. Eine falsche Klassenangabe faellt im Fachumfeld sofort auf.
- [ ] **Weitere Qualifikationen ergaenzen.** Der Block &laquo;Qualifikationen&raquo;
      ist seit UPDATE-02 sichtbar und enthaelt bisher nur den Amateurfunk. Weitere
      Zertifikate, Qualifikationen und Mitgliedschaften eintragen, sobald die
      Angaben feststehen. Struktur je Eintrag: Bezeichnung, ausstellende Stelle,
      Jahr bzw. Gueltigkeit. Nichts erfinden, nichts andeuten.
- [ ] **Berufsbezeichnung.** Klaeren, ob die Bezeichnung &laquo;Ingenieur&raquo;
      gefuehrt werden darf und wie sie geschrieben wird. Der sichtbare Platzhalter
      auf der Seite wurde entfernt; die Frage lebt nur noch hier.

### 6.2 Haeufige Fragen

Seit UPDATE-02 sind fuenf Fragen beantwortet und sichtbar. Eine Frage bleibt offen
und steht deshalb **nicht** auf der Seite, damit dort kein sichtbarer Platzhalter
erscheint. Sobald die Antwort vorliegt, in `src/pages/faq.astro` (Array `faq`) und
in `netlify-single/index.html` (Abschnitt `#faq`) ergaenzen.

- [ ] **Wie schnell ist ein Messtermin moeglich?** Realistische Vorlaufzeit
      festlegen, abhaengig von der Geraeteverfuegbarkeit, und die Frage danach
      wieder aufnehmen. Eine konkrete Angabe wie &laquo;in der Regel innert zwei
      bis drei Wochen&raquo; wirkt stark, wenn sie eingehalten wird.
- [ ] **Erstgespraech kostenlos bestaetigen.** Die Antwort auf &laquo;Was kostet
      eine Messung?&raquo; enthaelt den Satz &laquo;Das Erstgespraech selbst ist
      kostenlos.&raquo; Bestaetigen, dass das tatsaechlich so angeboten wird.
      Falls nicht, den Satz in beiden Fassungen streichen.

### 6.3 Noch fehlende Inhalte (aus UPDATE-02 Abschnitt H)

- [ ] **Foto der Person** fuer den Abschnitt &laquo;Ueber mich&raquo;.
- [ ] **Anonymisierter Musterbericht als PDF.** Senkt die Hemmschwelle stark,
      weil Interessenten sehen, was sie am Ende bekommen. Vor Veroeffentlichung
      auf Kundendaten pruefen.

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

### UPDATE-02

| Abschnitt | Was geaendert wurde |
| --- | --- |
| A | &laquo;Qualifikationen&raquo; sichtbar geschaltet und mit dem Amateurfunk-Block gefuellt. Bewusst **Variante 1** ohne Klassenangabe: &laquo;Amateurfunkzeugnis, Rufzeichen DO1BUU.&raquo; Variante 2 erst nach Verifikation der Lizenzklasse. |
| B | FAQ-Antwort &laquo;Muss die Anlage dafuer abgeschaltet werden?&raquo; ergaenzt. |
| C | FAQ-Antwort &laquo;Was kostet eine Messung?&raquo; ergaenzt. Weiterhin keine Preise auf der Seite. |
| D | FAQ-Antwort &laquo;In welchem Gebiet sind Sie im Einsatz?&raquo; ergaenzt. |
| E | Frage zur Vorlaufzeit bleibt aus dem sichtbaren Bereich draussen, siehe 6.2. |
| F | Startseite, Block &laquo;Woher die Einschaetzung kommt&raquo;: Satz um &laquo;Lizenzierter Funkamateur.&raquo; ergaenzt. |
| G.1 | **Alle sichtbaren `TODO:`-Texte aus dem Kundenbereich entfernt**, auch aus den Rechtstexten. Sie liegen jetzt als HTML-Kommentar an der betroffenen Stelle und hier in dieser Datei. Details unten. |

**Zu G.1 im Detail.** Bis UPDATE-01 trugen Impressum, Datenschutz und AGB
sichtbare `TODO:`-Hinweise, wie es der urspruengliche BRIEF Abschnitt 7 verlangte.
UPDATE-02 Punkt G.1 verlangt das Gegenteil. Aufgeloest wurde das so:

- Der `DraftBanner` bleibt auf allen drei Rechtsseiten stehen. Er kennzeichnet
  die Texte weiterhin sichtbar als Entwurf mit Pruefvorbehalt, verwendet aber
  nicht das Wort `TODO`. Damit ist die Vorgabe aus BRIEF Abschnitt 7 weiterhin
  erfuellt.
- Wo ein `TODO` mitten im Satz stand, wurde der Satz vervollstaendigt statt
  gekuerzt. AGB Ziffer 11 lautet jetzt &laquo;Der Gerichtsstand wird vor
  Inkraftsetzung dieser Geschaeftsbedingungen festgelegt.&raquo; statt eines
  abgebrochenen Satzes.
- Die Zeilen &laquo;Stand: TODO&raquo; lauten jetzt &laquo;Stand: Entwurf.&raquo;
  mit dem Zusatz, dass der Text erst nach Pruefung in Kraft gesetzt wird.
- Zwei Abschnitte, deren einziger Inhalt ein TODO war, sind ganz entfallen:
  &laquo;Firmenname und Handelsregister&raquo; im Impressum (der BRIEF verlangt
  in Abschnitt 7.1 ohnehin kein Handelsregister-Feld) und &laquo;EU-Kunden und
  DSGVO&raquo; in der Datenschutzerklaerung. Beide Fragen leben als Kommentar im
  Code und hier weiter. Die Datenschutzerklaerung hat dadurch elf statt zwoelf
  Ziffern; die Nummerierung wurde durchgehend korrigiert.
- `robots.txt` enthaelt weiterhin einen technischen `TODO`-Kommentar zur
  Site-URL. Das ist eine Maschinendatei, kein Kundenbereich.
