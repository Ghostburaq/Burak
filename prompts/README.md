# Prompts

Systemprompts für den Arbeitsalltag von Burak Ücöz (Mobil in Time AG, An Aggreko Company).

| Datei | Zweck |
|-------|-------|
| `CLAUDE_Kaltakquise_Maschine.md` | Systemprompt für Kaltakquise-E-Mails: beliebiger Input (LinkedIn, Webseite, News, Messenotiz, Firmenname) rein, zwei sendefertige Varianten plus Follow-up-Plan raus. |

Die Dateien sind so geschrieben, dass sie 1:1 als Systemprompt eingesetzt werden
können (Claude Projects, API-System-Prompt, Custom Instructions). Kein Vorspann,
kein Nachbearbeiten nötig.

Der Systemprompt wird vom Tool im Repo-Root direkt gelesen:

```bash
python3 kaltakquise.py "Firmenname oder Notiz"   # erzeugt und prüft
python3 kaltakquise.py prompt                    # gibt diesen Prompt aus
```
