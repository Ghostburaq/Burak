---
name: nexa-clip
description: Macht aus einem Rohvideo einen fertigen Kurzclip für TikTok, Reels oder Shorts (Jump-Cut, Hochformat, Ton säubern, Untertitel, Musik, Hook-Intro). Trigger bei "mach daraus einen Clip", "schneid das für TikTok", "Reel aus diesem Video", Upload eines Videos mit Wunsch nach Social-Media-Version.
---

# NEXA-Clip

Ziel: Rohclip in `content/01_roh/` wird zu einem upload-fertigen 9:16-Clip in `content/03_fertig/`.

## Ablauf
1. Eingang prüfen: `ffprobe` (Dauer, Format, Ton vorhanden). Fehlt Ton: Untertitel und Ducking überspringen.
2. `studio/bin/schnitt IN content/02_schnitt/a.mp4` (Pausen raus)
3. `studio/bin/hochformat ... b.mp4` (Blur-Hintergrund; `crop`, wenn die Person mittig steht)
4. `studio/bin/entrauschen` dann `studio/bin/lautheit` (-14 LUFS)
5. `studio/bin/untertitel b.mp4 small ja de`, SRT kurz gegenlesen und Fachbegriffe korrigieren (Normen, Einheiten: kVA, kW, EN 50160)
6. Optional Musik: `studio/bin/musik-drunter clip.mp4 content/musik/X.mp3` (Musik nur eigene oder lizenzfreie)
7. Hook: `studio/bin/hook-clip "Hook" "Auflösung" hook.mp4` und `studio/bin/zusammenfuegen final.mp4 hook.mp4 clip.mp4`
8. Kontrolle: 3 Standbilder ansehen, Lautheit messen, dann Datei senden.

## Regeln
- Hook in den ersten 2 Sekunden. Keine erfundenen Zahlen im Hook.
- Keine Emojis in Untertiteln. Schweizer Schreibweise (ss).
- Mediendateien nie committen.
