# Projektkontext für Claude

Repo von Burak: MiT-Unterlagen (Präsentationen, Offerten) und NEXA-Content (Video, Animation, Publikation).

## Regeln
- Chat auf Deutsch, Du-Form, direkt. Keine Gedankenstriche als Stilmittel, keine Emojis.
- Schweizer Schreibweise (ss) für Schweizer Dokumente.
- Keine erfundenen Zahlen, Produktdaten oder Preise. Fehlt ein Wert: als Lücke markieren.
- Kundennamen, Einkaufspreise und Margen nie in externe Dokumente.
- Mediendateien (mp4, wav, mp3) nie committen, sie sind per .gitignore ausgeschlossen.

## Struktur
- `.claude/skills/mit-praesentation/` Skill für Decks im MiT-Design
- `studio/bin/` Befehle für Schnitt, Ton, Untertitel, Hook-Clips (Übersicht: `docs/STUDIO.md`)
- `studio/remotion/` Animierte Videos per Code (React). Composition `NexaHook` = 1080x1920
- `content/01_roh` Rohmaterial, `02_schnitt` Zwischenstände, `03_fertig` Upload-fertig
- `content/kalender.csv` Redaktionsplan

## Befehle
- Werkzeuge prüfen: `studio/bin/studio-check`
- Remotion Vorschau: `cd studio/remotion && npm run dev`
- Remotion rendern: `npx remotion render NexaHook out/x.mp4 --props='{"hook":"..","sub":".."}'`
- Python-Code prüfen: `ruff check . && ruff format .`

## Umgebung
- Cloud-Container ohne GPU, 4 Kerne, 15 GB RAM. KI-Video und KI-Musik nur über APIs.
- Remotion nutzt das vorinstallierte Chromium (siehe `remotion.config.ts`).
