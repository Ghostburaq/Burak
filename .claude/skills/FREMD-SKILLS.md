# Übernommene Skills (Drittanbieter, MIT-Lizenz)

Geprüft am 15.11.2026: keine versteckten Befehle, nur dokumentierte Aufrufe öffentlicher APIs.
Hooks, Agenten und Befehle aus ECC wurden bewusst NICHT übernommen (laufen bei jedem Werkzeugaufruf mit).

| Skill | Quelle | Stand |
|---|---|---|
| manim-video, songwriting-and-ai-music, humanizer, youtube-content, meeting-action-items, document-to-action-items, weekly-review-planning, competitor-news-monitor, grounded-citations, creative-ideation, baoyu-comic, fitness-nutrition, one-three-one-rule, decision-questionnaire | github.com/NousResearch/hermes-agent | Commit 4c14d9df |
| video-editing, remotion-video-creation, energy-procurement, article-writing, market-research, frontend-slides | github.com/affaan-m/ECC | Commit d2ef268 |

Hinweise:
- `fitness-nutrition` ruft wger.de und die USDA-API ab. Diese Hosts sind im Netzwerk noch nicht freigegeben; Planungslogik funktioniert ohne.
- `baoyu-comic` erwartet ein Bildgenerierungs-Werkzeug; hier mit `studio/bin/bild` und `studio/bin/comic` kombinieren.
- Aktualisieren: Repo erneut klonen, Ordner ersetzen, Commit-Stand oben anpassen.
