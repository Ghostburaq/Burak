# Angebot · Master-Vorlage

Master-Vorlage für Kunden-Angebote unter dem persönlichen Brand
**Burak Ücöz · Power Quality / EMV**.

| Datei | Zweck |
|-------|-------|
| `Angebot_Master_Vorlage.docx` | Fertige Word-Vorlage mit Logo, Kopf-/Fusszeile, Adressblock, Meta-Box, Sektionen 1–6, Angebotstabelle, Nutzen-Kacheln, Signaturblock. |
| `build_template.js`           | Node-Script (docx-js), das die `.docx` deterministisch neu baut. |

## Neu bauen

```bash
npm install docx
node templates/build_template.js
```

## Brand-Farben

| Rolle | Hex |
|-------|-----|
| Navy (Primary) | `#0B2545` |
| Signal Cyan (Accent) | `#00B8D9` |
| Ink | `#0F172A` |
| Paper | `#F8FAFC` |
| Grey Light | `#E2E8F0` |

## Logo

Die Logo-Assets liegen unter `assets/brand/`:

- `logo_mark.svg` / `logo_mark_{256,512,1024}.png` — quadratische Marke (BÜ)
- `logo_lockup.svg` / `logo_lockup.png` — horizontale Marke + Wordmark

## Platzhalter

Alle variablen Stellen sind als `[Platzhalter]` markiert (grau, kursiv) —
einfach in Word öffnen, mit **Suchen & Ersetzen** durchgehen oder direkt
überschreiben.
