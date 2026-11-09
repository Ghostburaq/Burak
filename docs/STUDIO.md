# NEXA Studio: Spickzettel

Alles läuft in dieser Claude-Code-Session. Du hast zwei Wege:

1. **Mir sagen, was du willst** (empfohlen). Beispiel: "Schneid `content/01_roh/clip3.mp4`, Hochformat, Untertitel, Musik drunter, Hook 'XY' davor."
2. **Selbst im Terminal tippen.** Mit `!` vor dem Befehl führst du ihn direkt aus, z.B. `! studio/bin/studio-check`.

Ablauf für Video: Datei in `content/01_roh/` hochladen, bearbeiten, Ergebnis landet in `content/03_fertig/`.

## Video und Ton (`studio/bin/`)

| Befehl | Was er macht | Beispiel |
|---|---|---|
| `schnitt` | Pausen und Stille rausschneiden (Jump-Cut) | `studio/bin/schnitt roh.mp4` |
| `hochformat` | 16:9 auf 9:16 (1080x1920), Blur-Hintergrund oder `crop` | `studio/bin/hochformat clip.mp4 out.mp4 crop` |
| `entrauschen` | Rauschen und Brummen aus der Stimme | `studio/bin/entrauschen clip.mp4` |
| `lautheit` | Lautheit auf -14 LUFS normalisieren | `studio/bin/lautheit clip.mp4` |
| `musik-drunter` | Musik unterlegen, wird leiser wenn du sprichst | `studio/bin/musik-drunter clip.mp4 content/musik/beat.mp3` |
| `untertitel` | Whisper erkennt Sprache, SRT + eingebrannte Untertitel | `studio/bin/untertitel clip.mp4 small ja de` |
| `hook-clip` | Animierter Text-Hook, 3 s, Hochformat | `studio/bin/hook-clip "Hook" "Auflösung" hook.mp4` |
| `zusammenfuegen` | Clips aneinanderhängen | `studio/bin/zusammenfuegen final.mp4 hook.mp4 clip.mp4` |
| `studio-check` | Prüft, ob alle Werkzeuge da sind | `studio/bin/studio-check` |

Typische Kette für einen TikTok-Clip:

```
schnitt -> hochformat -> entrauschen -> lautheit -> untertitel -> musik-drunter -> hook-clip + zusammenfuegen
```

## Animation

- **Remotion** (`studio/remotion/`): Videos als React-Code. Ideal für wiederkehrende Formate (Hook-Intros, Zahlen-Animationen, Lower Thirds). Neue Formate einfach bei mir bestellen.
  Lizenz: kostenlos für Einzelpersonen und Teams bis 3 Personen. Für MiT als Firma vorher die Lizenz prüfen.
- **Manim**: Technische Animationen (Sinuskurven, Oberschwingungen, Zeigerdiagramme). Perfekt für Elektrotechnik-Content.
- **ImageMagick** (`convert`): Thumbnails, Bildformate, Text auf Bild.

## Programmieren

| Werkzeug | Wofür |
|---|---|
| Python 3.13 + `uv` | Skripte, Datenauswertung, Automatisierung. `uv pip install --system paket` |
| `ruff` | Python prüfen und formatieren |
| Node 22, `pnpm`, `tsc`, `tsx` | Web, TypeScript, Remotion |
| `python-pptx`, `python-docx`, `openpyxl` | PowerPoint, Word, Excel per Code (Offerten, Decks) |
| `pandas`, `matplotlib` | Messdaten auswerten, Diagramme (z.B. PQ-Messungen) |
| `anthropic` | Eigene KI-Automationen mit der Claude API (braucht API-Key) |
| Playwright + Chromium | Webseiten automatisieren, Screenshots, Scraping |
| `yt-dlp` | Eigene Videos oder Referenzen herunterladen (nur mit Rechten) |
| `docker` | Fremde Tools isoliert laufen lassen |
| `git` + GitHub | Versionierung, alles landet im Repo `ghostburaq/burak` |

## Was noch nicht geht und was es braucht

| Funktion | Status | Was fehlt |
|---|---|---|
| Untertitel (Whisper) | Läuft, getestet mit deutscher Sprache | Nichts. Modelle: `small` (Standard), `medium` genauer aber langsamer auf CPU |
| Publizieren LinkedIn, TikTok, YouTube | Noch nicht verbunden | Postiz-Konto oder je Plattform API-Zugang |
| KI-Video, KI-Musik, KI-Stimme | Nur über API möglich (keine GPU) | API-Key je Dienst (z.B. ElevenLabs, Runway, Suno) |

## Claude Code besser nutzen

- **CLAUDE.md** im Repo-Root: mein Gedächtnis für dieses Projekt. Was dort steht, weiss ich in jeder neuen Session. Regeln, die du mir öfter sagst, kommen dort rein.
- **Skills** (`.claude/skills/`): wiederholbare Abläufe, z.B. `mit-praesentation`. Neue Skills baue ich dir auf Zuruf: "Mach daraus einen Skill."
- **Plan-Modus**: Bei grossen Aufgaben zuerst den Plan prüfen lassen, dann ausführen (Shift+Tab im Terminal, in der App über das Modus-Menü).
- **`/`-Befehle**: `/code-review`, `/simplify`, `/loop` (wiederkehrende Aufgaben), `/init`.
- **Geplante Aufgaben**: Ich kann Aufgaben zeitgesteuert starten, z.B. jeden Montag 07:30 den Redaktionsplan der Woche vorbereiten.
- **Setup-Script**: Diese Installation ist in der Cloud-Umgebung gespeichert, jede neue Session startet fertig eingerichtet.
