# Anleitung: Was du hier alles machen kannst

## 1. KI-Modelle

| Modell | Wo | Wofür | Wie |
|---|---|---|---|
| Claude Opus 5.5 | Diese Session | Komplexes: Offerten, Code, Videos, Analysen | Standard hier. Wechseln: `/model` im Terminal oder Modell-Auswahl in der App |
| Claude Sonnet 5.5 | Diese Session | Schnell und gut für Alltag, Texte, E-Mails | `/model sonnet` |
| Claude Haiku 5.5 | Diese Session | Sehr schnell, einfache Aufgaben | `/model haiku` |
| Claude Fable 5.1 | Diese Session | Weiteres Claude-Modell | `/model` und auswählen |
| Whisper (lokal) | Hier installiert | Sprache zu Text, Untertitel | `studio/bin/untertitel clip.mp4` oder mir sagen |
| Suno, Udio | Extern, eigenes Konto | Lieder mit echtem Gesang | Text von mir, dort generieren, Datei zurück an mich |
| ElevenLabs | Extern, API-Key | Stimme, Voice-over, Stimmklon | Key über das sichere Formular, dann mache ich es |
| Runway, Veo | Extern, API-Key | KI-Video aus Text oder Bild | Wie ElevenLabs |

Kein lokales Bild-, Video- oder Musik-KI-Modell: Der Container hat keine GPU.

## 2. Verbundene Dienste (Connectors)

| Dienst | Was ich damit tun kann |
|---|---|
| Gmail | Mails suchen, lesen, Entwürfe schreiben, Antworten vorbereiten |
| Google Kalender | Termine lesen, anlegen, freie Zeiten finden |
| Google Drive | Dateien suchen, lesen, anlegen |
| GitHub | Dein Repo `ghostburaq/burak`: Code, Branches, Pull Requests |
| Spotify | Musik suchen, Playlists erstellen |
| Semrush | SEO und Wettbewerbs-Daten (für NEXA-Website) |
| Indeed | Stellen und Firmendaten suchen |
| Claude Docs | Dokumente, die man weiter bearbeiten kann |
| Artifacts | Webseiten, Dashboards, Abspielseiten wie bei Mia |

Viele weitere Plugins sind installiert, verbinden sich aber nicht (Netzwerk blockiert). Bei Bedarf freischalten.

## 3. Eigene Skills (wiederholbare Abläufe)

| Skill | Auslöser |
|---|---|
| mit-praesentation | "Mach mir ein Deck für ..." |
| mit-anfrage-intake | "NEU: ...", "NOTFALL: ..." |
| mit-offerten-fabrik | "3DOC für ..." |
| verhandlung-closing | "Bereite mich auf den Termin vor" |
| personal-branding, NEXA-Content | "LinkedIn-Post über ..." |
| elektrotechnik-emv-sales | Fachfragen PQ, EMV, Auslegung |
| docx, pptx, xlsx, pdf | Word, PowerPoint, Excel, PDF erstellen |

## 4. Studio (Video, Musik, Animation)

Details: `docs/STUDIO.md`. Kurz: Datei in `content/01_roh/` hochladen und sagen, was du willst.

## 5. So arbeitest du am besten mit mir

1. Sag das Ergebnis, nicht den Weg: "TikTok-Clip, 30 s, Untertitel, Hook X".
2. Dateien hochladen statt beschreiben.
3. Bei Grossem: "Mach zuerst einen Plan" (Plan-Modus).
4. Wiederholt sich etwas: "Mach daraus einen Skill".
5. Regelmässig: "Jeden Montag 07:30 ..." (geplante Aufgabe).
6. Wichtiges bleibt: Alles Fertige wird ins Repo gepusht, Medien liegen in `content/`.
