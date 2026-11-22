# Kalorien

Schlanke Kalorien- und Makro-Tracking-App mit Expo (React Native). Läuft auf iOS, Android und im Browser. Alle Daten bleiben lokal auf dem Gerät (AsyncStorage), kein Konto, kein Server.

## Funktionen

- **Tag:** Einträge nach Frühstück, Mittag, Abend, Snacks. Gegessen, Übrig, Balken für kcal, Protein, KH, Fett gegen das Tagesziel. Mit ‹ › durch die Tage blättern.
- **Eintrag:** Bezeichnung, Makros in g, kcal optional (leer = berechnet aus 4/4/9 kcal pro g). Mengenfaktor (z.B. 1,5 ×). Warnung, wenn eingetragene kcal mehr als 15 % von den Makros abweichen.
- **Vorlagen:** Häufige Gerichte als Vorlage speichern, später mit einem Tipp übernehmen. Unter "Verwalten" löschen.
- **Woche:** Balken pro Tag (Mo bis So, ISO-KW) mit Ziellinie, Schnitt nur über erfasste Tage.
- **Ziele:** kcal und Makros frei einstellbar. Startwerte 2000 kcal / 150 g P / 200 g KH / 70 g F sind Platzhalter, keine Empfehlung.

Bewusst keine eingebaute Lebensmitteldatenbank: Nährwerte kommen von dir (Verpackung, Waage), nicht aus geratenen Werten.

## Starten

```bash
cd kalorien-app
npm install
npx expo start        # QR-Code mit Expo Go scannen (iPhone: Kamera, Android: Expo-Go-App)
npx expo start --web  # im Browser
```

## Prüfen

```bash
npm test           # Rechenlogik (kcal, KW, Wochenschnitt, Zahleneingabe)
npm run typecheck
```

## Aufbau

| Datei | Inhalt |
|---|---|
| `App.tsx` | Zustand, Tab-Leiste, Plus-Button |
| `src/logic.ts` | Reine Rechenlogik, ohne React testbar |
| `src/storage.ts` | Laden/Speichern in AsyncStorage |
| `src/screens.tsx` | Tag, Woche, Ziele |
| `src/EntryModal.tsx` | Eintrag erfassen/bearbeiten, Vorlagen |
| `src/ui.tsx`, `src/theme.ts` | Bausteine und Farben |
