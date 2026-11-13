---
name: meine-stimme
description: Spricht Texte mit Buraks geklonter Originalstimme ein (Chatterbox, lokal) oder richtet die Stimme aus einer neuen Aufnahme ein. Trigger bei "mit meiner Stimme", "sprich das ein", "Voice-over mit mir", Upload einer Sprachaufnahme zum Klonen.
---

# Meine Stimme

## Einrichten (einmalig, oder bei neuer Aufnahme)
1. Aufnahme von Burak: 15-30 s, ruhiger Raum, normal gesprochen, Handy nah am Mund.
2. `studio/bin/stimme-vorbereiten aufnahme.m4a` -> `content/stimme/referenz.wav` (nie committen)

## Einsprechen
- `studio/bin/meine-stimme "Text" out.wav` oder `studio/bin/meine-stimme skript.txt out.wav`
- Ausdruck: dritter Wert 0.3 (ruhig) bis 0.8 (lebhaft), Standard 0.5
- Dauer: ca. 1 min Rechenzeit pro 10 s Sprache (CPU)
- Kontrolle: `untertitel out.wav small nein de` und SRT mit Skript vergleichen

## Regeln
- Nur Buraks eigene Stimme klonen. Keine fremden Stimmen ohne deren Zustimmung.
- Ausgaben tragen ein unhörbares Wasserzeichen (Perth) von Chatterbox.
- Stimme nie für Aussagen nutzen, die Burak nicht freigegeben hat.
