# Lernfuchs 🦊 — Sprachen lernen (Französisch & Englisch mit deutscher Hilfe)

Eine installierbare, offline-fähige Web-App (PWA) zum Sprachenlernen — wie
Duolingo, aber mit eingebautem **Lern-Timer**, **Streak/XP/Level-Gamification**
und mehreren Quiz-Modi. Läuft auf Handy, Tablet und PC und kann **kostenlos
weltweit** veröffentlicht werden.

## Funktionen

- 🇫🇷🇬🇧 **Zwei Kurse** zur Auswahl: Französisch & Englisch — jeweils mit
  deutscher Übersetzung und Aussprache-Hilfe.
- 📚 **Lektionspfad** mit Einheiten, freischaltbaren Lektionen und Sternen.
- 🧠 **3 Quiz-Modi:** Bedeutung wählen, Wort wählen, Antwort eintippen.
- ❤️ **Herzen** pro Lektion (wie Duolingo) für mehr Spannung.
- ⏱️ **Lern-Timer (Pomodoro):** Fokus-/Pausenphasen, anpassbar (25/5, 50/10,
  15/3), Fokus-Minuten zählen auf dein **Tagesziel**.
- 🔥 **Gamification:** Tages-Streak, XP, Level mit Rängen (Fuchswelpe →
  Großmeister) und eine motivierende **Wochen-Liga**.
- 📊 **Statistik:** 7-Tage-XP-Diagramm, Level-Fortschritt, Tagesminuten.
- 🔊 **Aussprache** per Text-to-Speech, 🌙 **Dunkelmodus**.
- 📲 **PWA:** installierbar auf dem Homescreen, funktioniert **offline**.
- 💾 **Lokal-zuerst:** Fortschritt wird im Browser gespeichert, kein Konto nötig.
  Cloud-Sync ist vorbereitet (siehe unten).

## Sofort ausprobieren (lokal)

Da es eine reine Web-App ohne Build-Schritt ist, reicht ein einfacher Webserver
(wegen Service-Worker/PWA nicht per `file://` öffnen):

```bash
cd app
python3 -m http.server 8000
# Browser öffnen: http://localhost:8000
```

## Weltweit veröffentlichen (kostenlos)

Der `app/`-Ordner besteht nur aus statischen Dateien — er lässt sich überall
hosten. Drei einfache Wege:

1. **GitHub Pages:** In den Repo-Einstellungen → *Pages* → Branch wählen und als
   Ordner `/app` (oder `/`) setzen. Nach ein paar Minuten ist die App unter
   `https://<dein-name>.github.io/<repo>/app/` weltweit erreichbar.
2. **Netlify / Vercel:** Repo verbinden, *Publish directory* = `app`. Fertig —
   du bekommst eine HTTPS-URL, die du auf jedem Gerät öffnen kannst.
3. **Drag & Drop:** Den `app/`-Ordner auf <https://app.netlify.com/drop> ziehen.

> Tipp: Auf dem Handy im Browser-Menü „Zum Startbildschirm hinzufügen" wählen —
> dann startet Lernfuchs wie eine echte App im Vollbild.

## Cloud-Sync aktivieren (optional, später)

Standardmäßig speichert die App lokal. Für geräteübergreifende Synchronisation
weltweit eignet sich **Supabase** (kostenloses Kontingent):

1. Kostenloses Projekt auf <https://supabase.com> anlegen.
2. Tabelle `progress` mit Spalten `user_id (uuid)` und `state (jsonb)` erstellen.
3. In `app/js/storage.js` die markierten **HOOK**-Stellen in `save()` und
   `load()` mit Supabase-Aufrufen füllen (Supabase-JS per `<script>` in
   `index.html` einbinden). Der restliche App-Code bleibt unverändert, weil
   jeder Datenzugriff über die `Store`-Schicht läuft.

## Inhalte erweitern

Alle Vokabeln stehen als reine Daten in `app/js/data.js`. Neue Wörter, Lektionen
oder ganze Sprachen lassen sich dort ergänzen, ohne den App-Code zu ändern —
einfach dem vorhandenen Muster (`units → lessons → items {t, de, hint}`) folgen.

## Projektstruktur

```
app/
├─ index.html              # Grundgerüst + Lädt die Skripte
├─ manifest.webmanifest    # PWA-Manifest (Name, Icons, Farben)
├─ sw.js                   # Service Worker (Offline-Cache)
├─ make_icons.py           # Erzeugt die App-Icons (Pillow)
├─ css/styles.css          # komplettes Design-System (inkl. Dark Mode)
├─ icons/                  # generierte App-Icons
└─ js/
   ├─ data.js              # Kursinhalte (FR & EN mit deutscher Hilfe)
   ├─ storage.js           # Speicher-Schicht (local-first, Cloud-ready)
   ├─ gamification.js      # XP, Level, Ränge, Liga
   ├─ timer.js             # Pomodoro-Lern-Timer
   └─ app.js               # UI, Navigation, Lern-Sessions
```
