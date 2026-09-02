# Pitch Burak Ücöz – Liebherr Energy Solutions

Bewerbungs-Deck für das Gespräch am 8. September 2026 in Baden.
Rolle: IoT & Energy Engineer.

## Dateien

| Datei | Inhalt |
|---|---|
| `Pitch_Burak_Uecoez_Liebherr.pptx` | Aktuelle Fassung im Liebherr-Corporate-Design |
| `Pitch_Burak_Uecoez_Liebherr_ORIGINAL.pptx` | Ausgangsfassung vor der Überarbeitung |
| `build.js` | Generator (pptxgenjs), erzeugt das Deck reproduzierbar |

## Farbschema

| Rolle | Hex | Bemerkung |
|---|---|---|
| Liebherr Gelb | `FED000` | Akzent: Badges, Kette, Kernaussagen |
| Gelb abgedunkelt | `D9AE00` | nur für Text auf hellem Grund (Kontrast) |
| Anthrazit | `1A1D1E` | dunkle Folien, Kernaussagen-Balken |
| Karte auf dunkel | `273034` | |
| Grauschiefer | `37484F` | Sekundärflächen |
| Papier | `F2F3F3` | helle Folien |

Gelb wird nie als Kleintext auf Weiss gesetzt (Kontrast), sondern als Fläche
oder als Text auf Anthrazit.

## Neu bauen

```bash
npm install pptxgenjs
node build.js Pitch_Burak_Uecoez_Liebherr.pptx
```

## Offen

- Telefonnummer und LinkedIn-Profil auf Folie 15 eintragen.
- Jahreszahlen im Werdegang (Folie 3) gegen CV und LinkedIn prüfen,
  insbesondere die Lücke zwischen 2023 und 2024.
- Schreibweise: durchgehend Schweizer `ss`. Falls das Deck an einen
  deutschen Standort geht, auf `ß` umstellen.
