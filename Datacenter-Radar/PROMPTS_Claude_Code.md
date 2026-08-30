# Prompt-Bibliothek Claude Code — MiT Strom Datacenter

Alle Prompts setzen voraus, dass `CLAUDE.md` im Projektordner liegt.
Kopieren, eckige Klammern ersetzen, absenden.

---

## 0 — Einmalig: Setup

```
Lies CLAUDE.md und fasse mir in fünf Zeilen zusammen, welche Regeln du
ab jetzt in jedem Output einhältst. Danach liste die Dateien im Ordner
auf und sag mir, welche du lesen kannst und welche fehlen.
```

---

## 1 — Neuen Tracker auswerten

Wenn ein neuer Data Centre Project Tracker kommt.

```
In diesem Ordner liegt [DATEINAME].xlsm, der Aggreko Data Centre Project
Tracker. Werte ihn auf die Schweiz aus:

1. Tab "Combined Project - Graph Data": alle Projekte mit Country = Switzerland.
2. Tab "Contacts Link": alle Kontakte, die entweder an einem dieser Projekte
   hängen ODER deren CMP_CNTRY Switzerland ist.
3. Dedupliziere auf Person plus Projekt.
4. Leite je Kontakt eine Rollen-Kategorie ab aus Titel und Firma:
   Betreiber, Betreiber-Bauseite, Betrieb, GU/Bauunternehmung, GU/Bauleitung,
   Planer/Engineering, Elektro-Unternehmer, Einkauf, Behörde, Geschäftsleitung,
   Projektleitung offen, Rolle unklar.
   Markiere die Kategorie ausdrücklich als abgeleitet, nicht als Quellwert.
5. Prio A = Bau- oder Planerseite an einem Projekt mit IBN 2027 bis 2029.
   Prio B = Betreiberseite oder IBN ausserhalb dieses Fensters.
   Prio C = Einkauf, Behörde, unklare Rolle.
6. Wo CMP_NAME leer ist, nimm die E-Mail-Domain als Firmenhinweis und
   kennzeichne das als Hinweis, nicht als bestätigten Firmennamen.

Baue daraus eine Excel mit den Tabs: CH-Kontakte, CH-Projekte, Auswertung,
Legende. Fehlende Werte als FEHLT auf gelbem Grund. Erfinde nichts.
Sag mir am Schluss, wie viele Projekte und Kontakte es sind und wie sich
die Rollen verteilen.
```

---

## 2 — Mail und Notiz für einen Kontakt

Der Standard-Prompt, den du am häufigsten brauchst.

```
Neuer Kontakt für die Datacenter-Akquise:

Name: [Vorname Nachname]
Funktion: [Titel oder "unbekannt"]
Firma: [Firma]
Ort: [Ort]
Telefon: [Nummer oder FEHLT]
E-Mail: [Adresse]
Projekt: [Projektname oder "keines bekannt"]
Projektphase: [im Bau / Planung / unbekannt], Baustart [Jahr], IBN [Jahr]
Quelle: [Tracker / Empfehlung von X / LinkedIn / Outlook]
Vorgeschichte: [ein Satz oder "keine"]
Sprache: [DE / EN / FR]

Prüfe zuerst im Kontakt-Log, ob die Person oder die Firma schon vorkommt,
und sag es mir, bevor du schreibst.

Dann drei Mailvarianten, ausgerichtet auf die Phase des Projekts:
- Bau läuft und IBN ist weit weg: Variante auf Baustelle, Baustrom,
  Heizung, Trocknung, Vorlaufzeiten
- IBN in ein bis drei Jahren: Variante auf Abnahmetests und Terminrisiko
- immer eine Variante mit einem echten Fachanker zur Rolle des Empfängers

Jede Variante: konkreter Betreff ohne Fragezeichen, Projektbezug als
Vermutung formuliert, eine Frage nach seinen Projekten, eine
Weiterleitungsfrage, ein Anruftermin mit Datum und Uhrzeit, volle Signatur.
Danach je eine Zeile, warum die Variante wirkt, und deine Empfehlung.

Zum Schluss die Notiz für Outlook im Format:
Titel: MiT Power | [Anruf/Rückruf] [Name], [Firma] | [Projekt] | [TT.MM.JJJJ HH:MM]
dann Kontakt, Projekt, Phase, Rolle im Deal, angesprochen am, Inhalt,
Ziel des Anrufs, Wiedervorlage, Gates, Koordinationshinweise.
```

---

## 3 — Kontakt-Log fortschreiben

```
Trag in MiT_DC_Schweiz_Kontakte_Maerz2026.xlsx, Tab Kontakt-Log, folgendes ein.
Wenn die Person schon drin steht, aktualisiere die Zeile statt eine neue anzulegen.

Person: [Name], [Firma]
Datum Kontakt: [TT.MM.JJJJ]
Kanal: [E-Mail / Telefon / LinkedIn / Baustelle / Messe / Empfehlung / Termin vor Ort]
Was gesagt oder geschrieben: [ein Satz]
Ergebnis: [keine Reaktion / Rückruf zugesagt / Gespräch geführt / Termin vereinbart /
  Unterlagen gewünscht / Anfrage erhalten / kein Bedarf / falscher Ansprechpartner]
Nächster Schritt: [konkret]
Wiedervorlage: [TT.MM.JJJJ]
Status: [offen / angeschrieben / im Gespräch / Termin fix / Anfrage aktiv / ruht / verloren]

Formatierung und Dropdowns beibehalten. Sag mir danach, wie viele Zeilen
im Log stehen und wie viele davon offen sind.
```

---

## 4 — Was ist heute fällig

Der Prompt für den Wochenstart.

```
Lies den Tab Kontakt-Log. Zeig mir alle Zeilen mit einer Wiedervorlage bis
einschliesslich [TT.MM.JJJJ], sortiert nach Datum. Pro Zeile: Name, Firma,
Projekt, was zuletzt lief, was der nächste Schritt ist, Uhrzeit.

Danach getrennt: alle Zeilen ohne Wiedervorlagedatum. Das sind die
verlorenen Kontakte, die will ich sehen.
```

---

## 5 — Nachfassen ohne Reaktion

```
Auf meine Mail an [Name], [Firma] vom [TT.MM.JJJJ] kam keine Reaktion.
Ich habe am [TT.MM.JJJJ] angerufen und [niemanden erreicht / auf die Mailbox
gesprochen / mit dem Sekretariat gesprochen].

Bau mir zwei Nachfassvarianten: eine kurze, die nur an den Termin erinnert,
und eine mit einem neuen inhaltlichen Anlass statt einer Erinnerung.
Kein Vorwurf, kein "ich wollte nur nachfragen". Neuer Anruftermin mit
Datum und Uhrzeit. Danach die aktualisierte Log-Zeile.
```

---

## 6 — Reaktion verarbeiten

```
Hier die Antwort von [Name], [Firma]:

"""
[Antworttext einfügen]
"""

Sag mir zuerst, was das für den Vorgang bedeutet und ob ich etwas übersehe.
Dann drei Antwortvarianten, passend zum Ton der Nachricht. Nach einer Absage
maximal eine einzige Frage, kein Nachbohren. Danach die aktualisierte
Log-Zeile mit Status und Wiedervorlage.
```

---

## 7 — Standort-Dossier

Wenn mehrere Kontakte auf demselben Projekt sitzen.

```
Für den Standort [Ort / Projektname]: Zieh mir aus dem Kontakt-Log und aus
den CH-Projekten alles zusammen, was wir dort haben.

Pro Person: Name, Firma, Rolle, welche Lose, Stand, nächster Termin.
Pro Los: Bezeichnung, Phase, Baustart, IBN, Projekt-ID.
Dazu: wo MiT bereits liefert oder offeriert hat, und wer intern zuständig ist.

Am Schluss: welche Rolle am Standort fehlt uns noch, und über wen kommen
wir am wahrscheinlichsten dran.
```

---

## 8 — Meeting-Briefing

```
Bau mir ein HTML-Briefing für ein Meeting mit Bereichsleitung und
Vertriebsleitung, Stand [TT.MM.JJJJ].

Inhalt:
1. Die drei Fragen, die kommen werden, mit je einer Antwort in einem Satz
2. Testfenster nach IBN-Jahr, was verloren ist und was erreichbar
3. Statusblock je laufendem Vorgang: wo stehe ich, worauf warte ich, warum
4. Wie ich vorgehe, in fünf bis sechs Punkten
5. Laufende Termine mit Datum
6. Was ich aus dem Meeting brauche, maximal drei Entscheidungen

Zahlen ausschliesslich aus der Excel und aus dem, was ich dir gesagt habe.
Keine Preise, keine Fleetzusagen. Vermerk INTERN VERTRAULICH in der Fusszeile.
Kompakt, eine Bildschirmseite pro Abschnitt, druckbar.
```

---

## 9 — Datenqualität prüfen

```
Prüfe den Tab CH-Kontakte auf Probleme:
- Personen, die mehrfach mit unterschiedlichen Projekten vorkommen
- Firmen, die an mehreren Projekten hängen, sortiert nach Anzahl
- Telefonnummern mit unplausibler Ländervorwahl oder Länge
- Projekte ohne einen einzigen Kontakt
- Kontakte ohne E-Mail und ohne Telefon

Gib mir eine Liste, was ich korrigieren oder verifizieren muss,
sortiert nach Aufwand pro Nutzen. Ändere nichts ohne meine Freigabe.
```

---

## 10 — Firmen mit Mehrfachprojekten

Der Prompt, der die wertvollsten Kontakte findet.

```
Zeig mir aus dem Tab CH-Kontakte alle Firmen, die an mehr als einem
Schweizer Projekt hängen. Pro Firma: Anzahl Projekte, Rollen-Kategorie,
die Namen der Ansprechpartner, die IBN-Jahre.

Sortiere nach Anzahl Projekte absteigend und markiere, welche davon
Planer oder GU sind. Das sind meine Multiplikatoren.
```

---

## 11 — Angebot vorbereiten

Wenn ein Mengengerüst kommt.

```
Für [Projekt] liegt jetzt ein Mengengerüst vor:
[Angaben einfügen]

Geh den 8-Schritt-Rechenweg durch: Lastliste, kVA-Umrechnung,
80-Prozent-Regel, Anlaufstromkorrektur, Höhen- und Temperaturderating,
Flottenauswahl, Spannungsfall, Verbrauch und Autonomie.

Sag mir bei jedem Schritt, welche Angabe fehlt, statt sie anzunehmen.
Keine Fleetzusage, keine Preise. Die PQ-Position nach IEC 61000-4-30
Klasse A gehört als Standardposition rein, nicht als Option.
Am Schluss die offenen Punkte für den Innendienst und für Owen.
```

---

## Kürzel für den Alltag

- `NEU:` gefolgt vom Kontaktblock startet Prompt 2
- `LOG:` gefolgt vom Ergebnisblock startet Prompt 3
- `FÄLLIG:` startet Prompt 4
- `NACHFASSEN:` startet Prompt 5
- `ANTWORT:` gefolgt vom Text startet Prompt 6
- `STANDORT:` gefolgt vom Ort startet Prompt 7

---

## 12 — Fachplaner-Mapping (der Multiplikator-Prompt)

Der wichtigste neue Prompt. Ein Planer ist zehn Projekte.

```
Nimm das Blatt 03_Kontakte und alle Radar-Projekte ohne belegten
Fachplaner. Recherchiere pro Planerfirma (Amstein + Walthert, Gruner,
HKG Engineering, AFRY, plus was du findest) die oeffentlich belegten
Datacenter-Referenzen und ordne sie den Radar-Projekten zu.

Regeln: Nur Zuordnungen mit URL-Beleg. Eine Referenz auf der
Planer-Website zaehlt als "beteiligt, Rolle pruefen", nie als
"Fachplaner Elektro bestaetigt". Personennamen nur, wenn sie auf der
Firmenwebsite oeffentlich mit Funktion stehen. Keine E-Mail-Adressen
aus Namensmustern.

Ergebnis: aktualisierte Zeilen fuer 02_Projekt_Radar Spalte J und
03_Kontakte, dazu pro Firma ein Satz, warum sie fuer MiT relevant ist.
```

---

## 13 — Planer-Erstansprache

Wenn eine Planerfirma einem Projekt zugeordnet ist.

```
Erstansprache an [Planerfirma] zum Projekt [Radar-Projekt].

Kontext aus dem Radar uebernehmen (Phase, IBN, was belegt ist).
Zwei Varianten, zurueckhaltend und offensiv, je eine Zeile Begruendung.

Kernbotschaft: Lastbank und PQ-Messung gehoeren ins LV, nicht in den
Nachtrag. Fachanker: IEC 61000-4-30:2025 Klasse A, EN 50160-Reporting,
Abnahmen unter definierter Last. Aggreko in der ersten Zeile.
Projektbezug als Vermutung. Betreff konkret, ohne Fragezeichen.
Kein CHF-Wert. Anruftermin mit Datum und Uhrzeit, volle Signatur.
```

---

## 14 — Campus-Doppelspiel Bestand plus Neubau

Fuer Standorte wie Glattbrugg, wo Betrieb und Baustelle nebeneinander liegen.

```
Am Standort [Ort] betreibt [Betreiber] Bestandsbauten und baut gleichzeitig
neu. Bau mir die Argumentation fuer ein einziges Gespraech, das beides
abdeckt: Wartungsfenster und NEA-Tests im Bestand, Baustrom und Trocknung
auf der Baustelle, Lastbank im kommenden Cx.

Dazu: welcher Ansprechpartner-Typ deckt beides ab, und welcher der beiden
Einstiege ist der leichtere. Kein erfundener Name, keine Preise.
```

---

## 15 — Dashboard-Refresh

Nach jedem Montags-Lauf.

```
Fuehre python3 scripts/build_dashboard_html.py aus und publiziere die
HTML-Datei neu auf die bestehende Artifact-URL. Danach in einer Zeile:
was sich im Dashboard gegenueber letzter Woche sichtbar geaendert hat.
```

---

## 16 — Einwand-Matrix Commissioning

Vor jedem Cx-Gespraech.

```
Gespraech mit [Rolle] bei [Firma] zum Projekt [Projekt], Phase laut
Radar: [Phase]. Gib mir die drei wahrscheinlichsten Einwaende mit je
einer Antwort in zwei, drei Saetzen.

Typische Kandidaten: "Lastbank stellt der Elektriker", "ist im
MEP-Vertrag drin", "zu frueh", "zu teuer", "machen wir mit dem
Generator-Lieferanten". Antworten aus der MiT-Logik: L4 durchgehetzt
heisst teurer IST, PQ-Messung Klasse A als Differenzierung, Vorlaufzeiten.
Keine Preise, keine Fleetzusagen.
```

---

## Kürzel, erweitert

- `PLANER:` gefolgt von Firma startet Prompt 12 oder 13
- `CAMPUS:` gefolgt vom Ort startet Prompt 14
- `DASH:` startet Prompt 15
- `EINWAND:` gefolgt von Firma und Projekt startet Prompt 16
