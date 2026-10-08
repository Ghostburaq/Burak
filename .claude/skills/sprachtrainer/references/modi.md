# Modi im Detail

## start (Einstufung)

Ziel: Profil in max. 10 Minuten anlegen.

1. Frag in EINER Nachricht: Ziel (Beruf, Reisen, Beides), Minuten pro Tag, Startniveau-Selbsteinschätzung, wichtigste Situation in 90 Tagen (z.B. "Kundentermin in Lausanne").
2. Einstufung in 3 Stufen, jeweils 2 Aufgaben, Abbruch sobald Burak klar scheitert:
   - A2: Sich und den Job in 4 Sätzen vorstellen. Eine einfache Frage beantworten.
   - B1: Ein Problem aus dem letzten Projekt erklären (Vergangenheit). Einen Kurztext (80 Wörter) lesen und 2 Fragen beantworten.
   - B2: Einen Einwand eines Kunden schriftlich entkräften. Eine Meinung begründen mit Konnektoren.
3. Einstufung ehrlich und mit Begründung (welche Strukturen sassen, welche fehlten). Niveau als A1, A2, A2+, B1, B1+, B2, C1.
4. `sprachen/<sprache>/` aus `templates/` anlegen, Profil befüllen, erste Fehler eintragen.
5. Anbieten: `plan` als nächster Schritt.

## plan (90 Tage)

1. Rechne offen: Minuten/Tag × 90 = Stunden. Richtwert: rund 150 bis 200 geführte Lernstunden pro GER-Stufe. Sag ehrlich, was in 90 Tagen realistisch ist.
2. Lege ein konkretes Handlungsziel fest (z.B. "15-Minuten-Kundengespräch ohne Ausweichen ins Deutsche"), nicht nur ein Niveau.
3. Drei Blöcke à 30 Tage, je mit: Kommunikationsziel, Wortschatzfelder, max. 3 Grammatikthemen (aus der Progression in `references/<sprache>.md`), Messpunkt.
4. Pro Woche: ein Satz "Am Ende der Woche kannst du ...", plus Wochentest am letzten Tag.
5. Tagesstruktur nach Zeitbudget, Standard bei 45 Min.: 10 Wortschatz/Wiederholung, 15 Hören (Input), 15 Sprechen (gespraech oder immersion), 5 Shadowing.
6. In `sprachen/<sprache>/plan.md` schreiben. Plan-Tag im Profil auf 1.

## heute

1. Plan-Tag aus Profil, passende Woche aus `plan.md`.
2. Kein Plan vorhanden: zuerst `plan` anbieten, sonst Standardtag.
3. Programm in 3 Zeilen ankündigen, dann direkt mit Block 1 starten. Zwischen den Blöcken nicht fragen "weiter?", sondern weitermachen, bis Burak `stopp` sagt oder der Tag durch ist.
4. Hörblock: Claude kann kein Audio abspielen. Gib eine konkrete Hörempfehlung (Quelle aus `references/<sprache>.md`, Dauer, worauf achten) und 2 Fragen, die Burak danach beantwortet.

## gespraech [szenario]

1. Szenario fehlt: 3 Vorschläge aus `references/<sprache>.md` (Abschnitt Szenarien) passend zum Plan-Tag, Burak wählt mit Zahl.
2. Rolle in 2 Zeilen setzen (wer du bist, was du willst, ein verdeckter Einwand). Dann direkt in der Zielsprache starten.
3. Realistisch: Rückfragen, Unterbrechungen, ein Einwand (Preis, Termin, Zuständigkeit). Schwierigkeit steigern, wenn Burak 3 Turns sauber schafft.
4. Max. 3 Sätze pro Turn.
5. Ende nach ca. 10 bis 15 Turns oder bei `stopp`:
   - Die 3 wichtigsten Fehler (Format aus SKILL.md).
   - 3 Wendungen, die ein Muttersprachler an Buraks Stelle genutzt hätte.
   - Note für Verständlichkeit und Professionalität je 1 bis 5, ein Satz Begründung.

## wortschatz [situation]

1. 15 Einheiten, bevorzugt Chunks (ganze Wendungen) statt Einzelwörter. Mischung: 8 Alltag/Kommunikation, 7 Fach, wenn Situation beruflich.
2. Pro Einheit: Zielsprache, Deutsch, ein Beispielsatz aus Buraks Alltag, Merkhilfe nur wo sie wirklich hilft (Eselsbrücke, Wortfamilie, falscher Freund).
3. Kurzer Test: 5 Lücken, 3 Übersetzungen DE nach Zielsprache, 2 freie Sätze.
4. Auswertung, Fehler ins Journal, alle 15 Einheiten in `wortschatz.csv`.

## grammatik [thema]

1. Thema fehlt: nächstes Thema der Progression, das im Fehlerjournal am häufigsten auftaucht.
2. Genau EINE Regel. Form, Gebrauch, Vergleich mit Deutsch (wo das Deutsche hilft und wo es in die Irre führt).
3. 3 Beispiele aus Vertrieb und Technik.
4. 6 Übungssätze aufsteigend schwer: 2 Umformen, 2 Lücken, 2 frei.
5. Jeden Fehler erklären. Bei mehr als 2 Fehlern: 3 weitere Sätze zum selben Punkt.

## input [thema]

1. Text oder Dialog, 150 bis 300 Wörter, Niveau +1, Thema aus Buraks Interessen (Technik, Energie, Sport, Business, Schweiz).
2. Keine Übersetzung mitliefern. Neue Wörter fett.
3. 4 Fragen: 2 Global, 1 Detail, 1 Meinung (Antwort in der Zielsprache).
4. Danach Glossar der fetten Wörter.

## immersion [szenario]

1. Ganze Situation von Anfang bis Ende (z.B. Anreise zum Kunden, Empfang, Besprechung, Mittagessen, Verabschiedung).
2. Deutsch-Anteil nach Niveau: A2 Stützen in Klammern, B1 nur bei `hilfe`, B2+ gar nicht.
3. Wortschatz natürlich einbauen, Fragen stellen, Burak handeln lassen.
4. Pro Szene am Ende eine Zeile Feedback, Gesamtkorrektur erst am Schluss.

## schreiben [aufgabe]

1. Aufgabe fehlt: berufliche Mail aus dem aktuellen Plan-Block vorschlagen.
2. Burak schreibt. Korrektur in 3 Schichten: Fehler (mit Grund), Register/Höflichkeit, Stil (wie ein Muttersprachler es formulieren würde).
3. Saubere Endfassung als kopierbarer Text.

## shadowing

1. 5 Sätze, natürlich gesprochen, Berufsbezug.
2. Pro Satz: Betonung markieren (GROSS), Bindungen/Verschleifungen anzeigen, stumme Buchstaben durchstreichen mit ~~x~~, wo relevant.
3. Anleitung: Satz lesen, laut 3-mal nachsprechen, dann frei. Echte Audioquelle aus `references/<sprache>.md` für Shadowing mit Ton empfehlen.

## test

1. 10 Aufgaben aus Wochenzielen und offenen Fehlern: 3 Wortschatz, 3 Grammatik, 2 Übersetzung, 1 Lesen, 1 freie Antwort.
2. Punkte pro Aufgabe, Gesamt in Prozent.
3. Resultat mit Datum in `profil.md` unter "Tests". Unter 60 Prozent: Woche wiederholen vorschlagen.

## status

1. Aus allen Dateien: Niveau, Plan-Tag, Sessions der letzten 14 Tage, Wortschatzgrösse, letzte 3 Testresultate.
2. Top-5 offene Fehler.
3. Ein Satz Einschätzung und der eine Hebel mit dem grössten Impact.
4. Mehrere Sprachen aktiv: kurzer Vergleich in einer Tabelle.

## anki

1. `wortschatz.csv` lesen. Datei `sprachen/<sprache>/anki_import.txt` schreiben: Tab-getrennt, Feld 1 Zielsprache plus Beispielsatz, Feld 2 Deutsch, Feld 3 Tags.
2. Import-Hinweis: In Anki "Datei > Importieren", Trennzeichen Tab, Felder zuordnen.
3. Nur Einträge seit dem letzten Export (Spalte `exportiert` auf `ja` setzen).
