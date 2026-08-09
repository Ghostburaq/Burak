# OFFENE PUNKTE (vor Live-Gang klären)

Zentrale Sammlung aller Luecken. Nichts davon ist erfunden, alles wartet auf eine
Entscheidung, eine Angabe oder eine Prüfung. Sortiert nach Prioritaet.

Kontext: Sitz Schweiz. Rechtsform Einzelunternehmen. Marke Engineering.Kabuu.
Deployment auf Netlify. Sprache Schweizer Schreibweise (ss).

---

## 1. DOMAIN, LOGO, ASSETS

- [ ] **Domain kaufen und in Netlify verbinden.**
      Im Code ist dazu **nichts** mehr einzutragen: Die Site-URL kommt beim
      Build aus der Netlify-Umgebungsvariable `URL` (siehe `astro.config.mjs`).
      Canonical-Links, `sitemap.xml`, `robots.txt` und `og:image` stimmen nach
      dem naechsten Deploy automatisch.
      Nur die Einzeldatei `netlify-single/index.html` braucht zwei Zeilen von
      Hand, sie sind dort im `<head>` als Kommentar hinterlegt.
- [ ] **Logo-Assets prüfen und ggf. durch das Original ersetzen.**
      Das gelieferte Logo-Rendering wurde als Vektor nachgezeichnet, weil die
      Original-Dateien in dieser Session nicht als Datei-Upload vorlagen
      (nur als Bild im Chat sichtbar). Aktuell im Einsatz:
      - `public/logo/mark.svg` &mdash; Bildmarke: Sechseck-Rahmen mit
        Metallverlauf, darin Signalkurve und diagonaler Blitz-Slash.
        Verwendet in Header, Footer, Startseite, Danke-Seite, Favicon.
      - `public/logo/logo-lockup.svg` &mdash; vollstaendiges Lockup mit
        Wortmarke, Untertitel und ENGINEERING-Zeile. Verwendet als `og:image`
        und für externe Zwecke (Offerten, Briefpapier).
      - `src/components/Logo.astro` &mdash; setzt die Wortmarke auf der Website
        als echten Text, damit sie in jeder Grösse scharf bleibt.
      **Zu prüfen:** Die Nachzeichnung ist eine Annaeherung, keine exakte
      Kopie. Sobald die Original-Vektordatei (oder die PNGs
      `kabuu-signet-1024/512/256.png`, `kabuu-signet-flat-512.png`) vorliegt:
      unter `public/logo/` ablegen und die Referenzen in `Logo.astro`,
      `favicon.svg` und `SEO.astro` austauschen.
- [ ] **Schriftart der Wortmarke klären.** Im Rendering ist eine bestimmte
      Sans verwendet. Auf der Website läuft die Wortmarke aktuell in der
      System-Sans der Seite. Falls die Original-Schrift verbindlich ist,
      Lizenz klären und selbst hosten (kein Google-Fonts-CDN, siehe Brief).
- [ ] Favicon-Set generieren (`favicon.ico`, `apple-touch-icon.png`,
      `site.webmanifest`) für aeltere Browser. Aktuell nur SVG-Favicon.
- [x] ~~Social-Preview als PNG (1200x630).~~ Erledigt: `public/og-image.png`,
      erzeugt von `scripts/make-og-image.py` aus derselben Geometrie wie
      `mark.svg`. Eingebunden als `og:image` und `twitter:image` in beiden
      Fassungen. Nach einem Logo-Wechsel neu erzeugen.
- [ ] **GLB (3D-Version) NICHT einbinden** &mdash; bewusst nicht integrieren
      (Bundle-Grösse, Lighthouse). Statische Renderings genügen.

## 2. FIRMENRECHTLICHES

- [ ] **Firmenname prüfen.** Nach Art. 945 OR muss bei einer Einzelfirma der
      Familienname wesentlicher Bestandteil der Firma sein. &laquo;Engineering.Kabuu&raquo;
      ist damit eher Geschäftsbezeichnung/Marke als eingetragene Firma. Mit
      Treuhänder klären, ob und wie die Firma im Handelsregister geführt wird.
      Der entsprechende Abschnitt in `src/pages/impressum.astro` ist derzeit
      entfernt und als Kommentar hinterlegt.
- [ ] **Berufsbezeichnung &laquo;Ingenieur&raquo;.** Klären, ob die Bezeichnung
      geführt werden darf und wie sie geschrieben wird, bevor sie auf der Seite
      verwendet wird. Auf der Seite steht dazu nichts, die Frage lebt nur hier.

## 3. MWST / STEUERN (mit Treuhänder)

- [ ] **MWST-Warnhinweis.** Die Befreiung von der MWST-Pflicht (Umsatz unter
      CHF 100'000 nach MWSTG) entfaellt, sobald der weltweite Jahresumsatz die
      Schwelle erreicht. Dann besteht Anmeldepflicht und die Preise sind neu zu
      kalkulieren. Rechtzeitig ueberwachen und Offerten-/Rechnungsvorlagen anpassen.
- [ ] **Leistungen an Kunden im Ausland.** Steuerliche Behandlung mit Treuhänder
      klären, bevor Offerten- und Rechnungsvorlagen erstellt werden.
- [ ] **Status einer allenfalls bestehenden Registrierung in Deutschland.**
      Vollständigkeit prüfen. Auf der Website steht bewusst keine deutsche
      Rechtsterminologie (§ 19 UStG etc.); die Formulierung in den AGB ist auf
      Schweizer Recht abgestellt.

## 4. NETLIFY / HOSTING / DATENSCHUTZ

- [ ] **DPA mit Netlify.** Auftragsbearbeitungsvertrag (Data Processing Addendum)
      abschliessen bzw. die Annahme dokumentieren. In `datenschutz.astro`
      Ziffer 4 als HTML-Kommentar hinterlegt.
- [ ] **Grundlage der Bekanntgabe ins Ausland** (u.a. USA) nach revDSG konkret
      benennen (z.B. Standardvertragsklauseln, anerkannte Angemessenheitsentscheidung).
      Aktuellen Stand abklären. In `src/pages/datenschutz.astro` Ziffer 5 einsetzen.
- [ ] **Aufbewahrungsdauer** der Formulareingaenge festlegen und in
      `src/pages/datenschutz.astro` Ziffer 6 eintragen.
- [ ] **E-Mail-Benachrichtigung** für Formulareingaenge im Netlify-Dashboard
      aktivieren.
- [ ] **Netlify-Formular-Limits** im gewählten Plan prüfen (aktuelle Kontingente
      können sich aendern).
- [ ] **CSP-Header** nach dem ersten Live-Deploy im Browser (DevTools -> Console)
      auf Verstoesse prüfen. Aktuell schlank gesetzt in `netlify.toml`.
- [ ] **EU-Kunden / DSGVO.** Prüfen, ob durch gezielte Ansprache von EU-Kunden
      zusätzlich die DSGVO greift und die Datenschutzerklärung ergänzt werden muss.

## 5. RECHTSTEXTE (durch Anwalt prüfen lassen)

Alle drei Texte sind mit `DraftBanner` als Entwurf gekennzeichnet und in Schweizer
Schreibweise verfasst.

- [ ] **Kontakt/Impressum:** Der Abschnitt Firmenname/Handelsregister ist
      entfernt (BRIEF 7.1 verlangt kein Handelsregister-Feld). Nach Klärung mit
      dem Treuhänder entscheiden, ob doch eine Angabe nötig ist.
- [ ] **Datenschutz:** siehe Abschnitt 4 (Netlify, Bekanntgabe, Aufbewahrung, DSGVO).
      &laquo;Stand: Entwurf&raquo; beim Inkraftsetzen durch das Datum ersetzen.
- [ ] **AGB:** Haftungshöchstsumme, Verjährung, Frist bei Terminabsage,
      Gerichtsstand, Aufbewahrungsfrist Messdaten mit Anwalt finalisieren.

## 6. INHALTLICHES

- [ ] Referenzen: nur anonymisiert bis zur schriftlichen Freigabe des Kunden.

### 6.1 Aus UPDATE-01 (Über mich)

- [ ] **Wehrtechnik-Nennung freigeben.** Prüfen, ob die Nennung wehrtechnischer
      Anwendungen im Abschnitt &laquo;Hintergrund&raquo; einer Geheimhaltungspflicht
      gegenueber frueheren Auftraggebern oder Arbeitgebern unterliegt. Die
      Formulierung nennt bewusst keine Projekte, Typen oder Auftraggeber. Im
      Zweifel den Halbsatz streichen.
- [ ] **EMV-Liste bestätigen.** Bestaetigen, dass mit den im Diktat genannten
      Kuerzeln EMI (Stoeraussendung) und EMS (Stoerfestigkeit) gemeint waren.
      Falls stattdessen ESD oder andere Pruefungen gemeint sind, die Liste im
      Abschnitt &laquo;EMV im Detail&raquo; korrigieren.
- [ ] **Pruefnormen.** Falls konkrete Pruefnormen genannt werden sollen, diese
      erst gegen die tatsächlich angewendeten Fassungen prüfen. Bis dahin
      stehen bewusst keine Normnummern in diesem Abschnitt.
- [ ] **Kalibrierzertifikat.** Falls für Gutachten oder Beweissicherung ein
      Kalibrierzertifikat einer akkreditierten Stelle vorliegt, im Abschnitt
      &laquo;Ausstattung&raquo; ergänzen. Nur eintragen, was vorhanden ist.
- [ ] **Berufshaftpflicht.** Prüfen, ob Versicherer und Deckungssumme genannt
      werden sollen. Viele Auftraggeber aus Industrie und Recht fragen danach;
      eine konkrete Deckungssumme wirkt dort staerker als die blosse Erwaehnung.
      Angabe erst nach Abgleich mit der Police.
- [ ] **Lizenzklasse Amateurfunk verifizieren.** Auf der Seite steht bewusst
      Variante 1 ohne Klassenangabe: &laquo;Amateurfunkzeugnis, Rufzeichen
      DO1BUU.&raquo; Erst nach Prüfung auf Variante 2 wechseln
      (&laquo;Amateurfunkzeugnis Klasse A und Klasse E, Rufzeichen DO1BUU.&raquo;).
      In Deutschland ist das Rufzeichenpraefix DO der Klasse E zugeordnet; beim
      Erwerb der Klasse A wird in der Regel ein Rufzeichen mit anderem Praefix
      zugeteilt. Angabe im Amateurfunkzeugnis bzw. in der Zulassungsurkunde
      prüfen. Eine falsche Klassenangabe faellt im Fachumfeld sofort auf.
- [ ] **Weitere Qualifikationen ergänzen.** Der Block &laquo;Qualifikationen&raquo;
      ist seit UPDATE-02 sichtbar und enthaelt bisher nur den Amateurfunk. Weitere
      Zertifikate, Qualifikationen und Mitgliedschaften eintragen, sobald die
      Angaben feststehen. Struktur je Eintrag: Bezeichnung, ausstellende Stelle,
      Jahr bzw. Gueltigkeit. Nichts erfinden, nichts andeuten.
- [ ] **Berufsbezeichnung.** Klären, ob die Bezeichnung &laquo;Ingenieur&raquo;
      geführt werden darf und wie sie geschrieben wird. Der sichtbare Platzhalter
      auf der Seite wurde entfernt; die Frage lebt nur noch hier.

### 6.2 Haeufige Fragen

Seit UPDATE-02 sind fünf Fragen beantwortet und sichtbar. Eine Frage bleibt offen
und steht deshalb **nicht** auf der Seite, damit dort kein sichtbarer Platzhalter
erscheint. Sobald die Antwort vorliegt, in `src/pages/faq.astro` (Array `faq`) und
in `netlify-single/index.html` (Abschnitt `#faq`) ergänzen.

- [ ] **Wie schnell ist ein Messtermin moeglich?** Realistische Vorlaufzeit
      festlegen, abhaengig von der Geraeteverfuegbarkeit, und die Frage danach
      wieder aufnehmen. Eine konkrete Angabe wie &laquo;in der Regel innert zwei
      bis drei Wochen&raquo; wirkt stark, wenn sie eingehalten wird.
- [ ] **Erstgespräch kostenlos bestätigen.** Die Antwort auf &laquo;Was kostet
      eine Messung?&raquo; enthaelt den Satz &laquo;Das Erstgespräch selbst ist
      kostenlos.&raquo; Bestaetigen, dass das tatsächlich so angeboten wird.
      Falls nicht, den Satz in beiden Fassungen streichen.

### 6.3 Noch fehlende Inhalte (aus UPDATE-02 Abschnitt H)

- [ ] **Foto der Person** für den Abschnitt &laquo;Über mich&raquo;.
- [ ] **Anonymisierter Musterbericht als PDF.** Senkt die Hemmschwelle stark,
      weil Interessenten sehen, was sie am Ende bekommen. Vor Veröffentlichung
      auf Kundendaten prüfen.

## 7. QUALITAETSSICHERUNG

- [ ] Lighthouse nach erstem Live-Deploy in allen vier Kategorien prüfen. Ziel: gruen.
- [ ] Screen-Reader-Test der Formular-Labels und Fokus-Zustaende.
- [ ] Farb-Kontraste stichprobenartig in DevTools prüfen (WCAG 2.1 AA).
- [ ] Robots.txt und sitemap.xml nach Domain-Setzung auf korrekte URLs prüfen.

## 8. SPRACHERWEITERUNG (später)

Verzeichnisse `fr/` und `it/` sind noch nicht angelegt. Beim Launch ist Deutsch die
einzige aktive Sprache. Für spaetere Erweiterung:
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
| Umlaute | Alle ASCII-Umschreibungen durch echte Umlaute ersetzt (über 130 Woerter). Der Name lautet jetzt durchgehend **Burak Ücöz**. IDs, Anker, Routen und ARIA-Referenzen bleiben bewusst ASCII, damit keine internen Links brechen. |
| A | Herstellernennung restlos entfernt: Fabrikat und Typenbezeichnung stehen nirgends mehr, auch nicht in Meta-Tags, Alt-Texten oder strukturierten Daten. Startseite, Leistungen, Ablauf Schritt 03 und Ausstattung neu formuliert. |
| B | `ueber.astro`: Abschnitt &laquo;Hintergrund&raquo; mit dem gelieferten Text gefuellt, TODO-Platzhalter entfernt. |
| C | `ueber.astro`: neuer Abschnitt &laquo;EMV im Detail&raquo; mit sechs Disziplinen und Abschlusssatz. Bewusst ohne Normnummern. |
| D | `ueber.astro`: Abschnitt &laquo;Ausstattung&raquo; vollstaendig ersetzt. Kalibrierintervall und Verzicht auf Fabrikatsnennung neu drin. |
| E | `ueber.astro`: neuer Abschnitt &laquo;Absicherung&raquo; (Berufshaftpflichtversicherung). |
| F | &laquo;Zertifikate und Mitgliedschaften&raquo; auskommentiert statt gelöscht, mit Struktur zum spaeteren Ausfuellen. Der Platzhalter ist damit oeffentlich unsichtbar. |
| G | Sichtbarer TODO-Platzhalter zur Berufsbezeichnung entfernt. Die Frage steht nur noch hier. |
| H | `kontakt.astro`: neuer Einleitungstext über dem Formular. Drei zusaetzliche, freiwillige Felder ergänzt: Standort der Anlage, Spannungsebene, Dringlichkeit. Alle mit verknuepften Labels. |
| I | Neue Seite `faq.astro` (in der Einzeldatei: Abschnitt `#faq`), eingehaengt zwischen Ablauf und Über mich, auch in der Navigation. Zwei Fragen sind beantwortet, vier stehen offen und wurden bewusst weggelassen statt als Platzhalter gezeigt (siehe 6.2). |
| J | Startseite: neuer Vertrauensblock &laquo;Woher die Einschätzung kommt&raquo; unterhalb von &laquo;Für wen&raquo;. |
| K | Firmen-&laquo;wir&raquo; entfernt. Startseite auf &laquo;Gemeinsam legen wir einen Messplan fest&raquo; umgestellt, Impressum auf &laquo;die Anbieterin&raquo;. In den Rechtstexten bleibt &laquo;die Anbieterin&raquo; als juristischer Begriff. |

Unveraendert gueltig: keine erfundenen Fakten, keine Preise auf der Website,
keine Normgrenzwerte als Zahlenwerte, keine Kundennamen, keine UID oder
MWST-Nummer.

### UPDATE-02

| Abschnitt | Was geaendert wurde |
| --- | --- |
| A | &laquo;Qualifikationen&raquo; sichtbar geschaltet und mit dem Amateurfunk-Block gefuellt. Bewusst **Variante 1** ohne Klassenangabe: &laquo;Amateurfunkzeugnis, Rufzeichen DO1BUU.&raquo; Variante 2 erst nach Verifikation der Lizenzklasse. |
| B | FAQ-Antwort &laquo;Muss die Anlage dafuer abgeschaltet werden?&raquo; ergänzt. |
| C | FAQ-Antwort &laquo;Was kostet eine Messung?&raquo; ergänzt. Weiterhin keine Preise auf der Seite. |
| D | FAQ-Antwort &laquo;In welchem Gebiet sind Sie im Einsatz?&raquo; ergänzt. |
| E | Frage zur Vorlaufzeit bleibt aus dem sichtbaren Bereich draussen, siehe 6.2. |
| F | Startseite, Block &laquo;Woher die Einschätzung kommt&raquo;: Satz um &laquo;Lizenzierter Funkamateur.&raquo; ergänzt. |
| G.1 | **Alle sichtbaren `TODO:`-Texte aus dem Kundenbereich entfernt**, auch aus den Rechtstexten. Sie liegen jetzt als HTML-Kommentar an der betroffenen Stelle und hier in dieser Datei. Details unten. |

**Zu G.1 im Detail.** Bis UPDATE-01 trugen Impressum, Datenschutz und AGB
sichtbare `TODO:`-Hinweise, wie es der urspruengliche BRIEF Abschnitt 7 verlangte.
UPDATE-02 Punkt G.1 verlangt das Gegenteil. Aufgeloest wurde das so:

- Der `DraftBanner` bleibt auf allen drei Rechtsseiten stehen. Er kennzeichnet
  die Texte weiterhin sichtbar als Entwurf mit Pruefvorbehalt, verwendet aber
  nicht das Wort `TODO`. Damit ist die Vorgabe aus BRIEF Abschnitt 7 weiterhin
  erfüllt.
- Wo ein `TODO` mitten im Satz stand, wurde der Satz vervollstaendigt statt
  gekuerzt. AGB Ziffer 11 lautet jetzt &laquo;Der Gerichtsstand wird vor
  Inkraftsetzung dieser Geschäftsbedingungen festgelegt.&raquo; statt eines
  abgebrochenen Satzes.
- Die Zeilen &laquo;Stand: TODO&raquo; lauten jetzt &laquo;Stand: Entwurf.&raquo;
  mit dem Zusatz, dass der Text erst nach Prüfung in Kraft gesetzt wird.
- Zwei Abschnitte, deren einziger Inhalt ein TODO war, sind ganz entfallen:
  &laquo;Firmenname und Handelsregister&raquo; im Impressum (der BRIEF verlangt
  in Abschnitt 7.1 ohnehin kein Handelsregister-Feld) und &laquo;EU-Kunden und
  DSGVO&raquo; in der Datenschutzerklärung. Beide Fragen leben als Kommentar im
  Code und hier weiter. Die Datenschutzerklärung hat dadurch elf statt zwoelf
  Ziffern; die Nummerierung wurde durchgehend korrigiert.
- `robots.txt` enthaelt weiterhin einen technischen `TODO`-Kommentar zur
  Site-URL. Das ist eine Maschinendatei, kein Kundenbereich.
