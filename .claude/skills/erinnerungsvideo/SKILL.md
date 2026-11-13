---
name: erinnerungsvideo
description: Macht aus einem Foto oder Bild ein warmes, animiertes Erinnerungsvideo mit eigener, rechtefreier Musik (z.B. für ein verstorbenes Haustier oder einen Menschen). Trigger bei "mach daraus was Schönes", "Erinnerungsvideo", "mit einem Lied dazu", Trauer- oder Gedenk-Kontext.
---

# Erinnerungsvideo

Vorlage: Komposition `ErinnerungWarm` in `studio/remotion/src/ErinnerungWarm.tsx` (Mia-Video).

## Ablauf
1. Bild nach `studio/remotion/public/katzen.png` (oder neuen Namen), Hintergrund vorblurren:
   `convert bild.png -resize 1920x1920 -blur 0x40 -modulate 55,110 bg.jpg`
2. Positionen anpassen: Heiligenschein, Herz oder andere Lichtpunkte im Bild (Prozentwerte im Code).
3. Musik: `studio/musik/trauerlied.py` (Klavier, Streicher, Summen, Chor). Warm mastern: `sox ... bass +3 120 treble -4 5000 reverb ...`, Lautheit -14 LUFS.
4. Texte: Name nur, wenn der Nutzer ihn nennt. Nichts erfinden.
5. Rendern, dann drei Fassungen: HD, WhatsApp (720p), ohne Musik (für lizenzierte Musik in Instagram oder TikTok).
6. Wiedergabe sicherstellen: zusätzlich Abspielseite als Artifact mit "Mit Ton abspielen"-Knopf.

## Regeln
- Geschützte Lieder nie selbst unterlegen. Gesang mit Text: Suno oder In-App-Musik der Plattform.
- Einfühlsam, kein Kitsch.
