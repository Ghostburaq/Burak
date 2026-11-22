# Kalorien

Kalorien- und Makro-Tracker mit Expo (React Native) für iOS, Android und Browser. Die App berechnet deinen Bedarf und passt ihn an deine echten Daten an. Alle Daten bleiben lokal auf dem Gerät (AsyncStorage), ohne Konto und ohne Server.

## Funktionen

**Bedarf und Ziele (Profil)**
- Modus *Berechnen*: Grundumsatz nach Mifflin-St Jeor aus Geschlecht, Geburtsjahr, Grösse und Gewicht, multipliziert mit dem Aktivitätsfaktor (1,2 bis 1,9).
- Ziel Abnehmen, Halten oder Aufbauen, Tempo 0,25 bis 1 kg pro Woche. Rechenbasis: 7700 kcal pro kg als Näherung.
- Makros: Protein in g pro kg Körpergewicht, Fett in % der kcal, Kohlenhydrate füllen den Rest.
- Zuschlag an Trainingstagen in kcal, geht komplett auf die Kohlenhydrate. Den Trainingstag markierst du in der Tagesansicht.
- Warnungen, wenn das Ziel unter dem Grundumsatz liegt, das Tempo mehr als 1 % Körpergewicht pro Woche beträgt, der Fettanteil unter 20 % fällt oder Protein und Fett das Kalorienziel übersteigen.
- Modus *Manuell*: feste Ziele für kcal und Makros.
- Live-Ergebnis mit Grundumsatz, Gesamtumsatz, Defizit bzw. Überschuss und Zielen für Ruhe- und Trainingstag.

**Mehr als Yazio**
- **Echter Verbrauch:** Aus Essensprotokoll und Gewichtsverlauf der letzten 21 Tage zurückgerechnet. Formel: Ø Zufuhr minus Gewichtsänderung × 7700 kcal, die Gewichtsänderung kommt aus einer linearen Regression. Voraussetzung: mindestens 10 erfasste Tage und 4 Wiegungen, die mindestens 10 Tage auseinanderliegen. Den Wert übernimmst du mit einem Tipp, er ersetzt dann die Formel.
- **Trendgewicht:** gleitender 7-Tage-Schnitt statt Tageswert, Verlauf über 6 Wochen, Veränderung über 7 und 30 Tage. Für die Makros wird mit dem Trendgewicht gerechnet.
- **Protein als Mindestziel:** Über dem Ziel wird es nicht rot. Bei kcal, Kohlenhydraten und Fett wird es rot ab 5 % über dem Ziel.
- **Wochenbilanz:** Summe der Abweichung vom Ziel über die erfassten Tage. Trainingstage werden mit ihrem eigenen Ziel verglichen.

**Erfassen**
- Mahlzeiten Frühstück, Mittag, Abend, Snacks. Die kcal sind optional und werden sonst aus den Makros berechnet (4/4/9). Mengenfaktor, Warnung bei mehr als 15 % Abweichung zwischen kcal und Makros.
- Vorlagen, *Zuletzt gegessen* (die 12 neuesten) und *Wie gestern* pro Mahlzeit.
- Wasser mit Ziel. Ohne eigenen Wert gilt die Faustregel 35 ml pro kg.

**Backup**
- Export als JSON: im Browser als Download, auf dem Handy über das Teilen-Menü. Import per Einfügen, ersetzt alle Daten nach einer Bestätigung.

Bewusst keine eingebaute Lebensmitteldatenbank: Die Nährwerte kommen von dir (Verpackung, Waage), nicht aus geschätzten Werten.

## Starten

```bash
cd kalorien-app
npm install
npx expo start        # QR-Code im Terminal mit Expo Go scannen (iPhone: Kamera, Android: Expo-Go-App)
npx expo start --web  # im Browser
```

## Prüfen

```bash
npm test           # Rechenlogik: Bedarf, Makros, Warnungen, Trend, adaptiver Verbrauch, KW, Wochenschnitt
npm run typecheck
```

## Aufbau

| Datei | Inhalt |
|---|---|
| `App.tsx` | Zustand, Tabs, Plus-Button |
| `src/nutrition.ts` | Bedarf, Makroverteilung, Warnungen, Gewichtstrend, adaptiver Verbrauch |
| `src/logic.ts` | Datum, KW, Summen, Wochenschnitt |
| `src/storage.ts` | Laden/Speichern, Migration, Backup |
| `src/screens.tsx` | Tag, Woche |
| `src/WeightScreen.tsx` | Gewicht, Trend, echter Verbrauch |
| `src/ProfileScreen.tsx` | Profil, Ziele, Backup |
| `src/EntryModal.tsx` | Eintrag erfassen/bearbeiten, Vorlagen, Zuletzt gegessen |
| `src/ui.tsx`, `src/theme.ts` | Bausteine und Farben |
