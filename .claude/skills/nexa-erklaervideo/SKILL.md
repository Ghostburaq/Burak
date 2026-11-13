---
name: nexa-erklaervideo
description: Erstellt ein animiertes Erklärvideo zu einem Technikthema (Netzqualität, Oberschwingungen, BESS, Generatoren, EMV) mit Sprecherstimme, Manim-Animation, Remotion-Titeln und Musik. Trigger bei "Erklärvideo", "erklär das animiert", "mach ein Video über Oberschwingungen", NEXA-Fachcontent als Video.
---

# NEXA-Erklärvideo

## Ablauf
1. Skript schreiben: 60-90 s, Hook zuerst, ein Kernpunkt, eine Zahl mit Quelle oder keine. Fachlich prüfen (Normen beim ersten Nennen voll: EN 50160, IEC 61000-4-30 Klasse A).
2. Stimme:
   - Mit Buraks Stimme: `studio/bin/meine-stimme skript.txt voice.wav` (braucht `content/stimme/referenz.wav`)
   - Sonst neutral: `studio/bin/sprechen skript.txt voice.wav`
   - Zahlen und Normen im Sprechtext ausschreiben. Danach mit `untertitel` gegenprüfen (Whisper).
3. Visuals pro Satz: Manim für Kurven und Diagramme (Vorlage `studio/showcase/welle.py`), Blender für 3D-Objekte (`studio/showcase/blitz3d.py`), KI-Bilder nur als Stimmung (`studio/bin/bild`, dann `hochskalieren`).
4. Schnitt in Remotion (Vorlage `studio/remotion/src/Showcase.tsx`): Szenen auf Satzgrenzen der Stimme legen.
5. Musik leise drunter (`studio/showcase/beat.py` ruhiger einstellen oder `studio/musik/trauerlied.py` als Basis), Ducking unter der Stimme.
6. Untertitel einbrennen, Lautheit -14 LUFS, Standbilder prüfen, senden.

## Regeln
- Fakten vor Effekt. Keine erfundenen Werte. Bei Unsicherheit Lücke markieren.
- Kundennamen nie im Video.
