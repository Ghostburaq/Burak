# Nexa·CRM

Dein eigenes Akquise-CRM — abgeleitet aus dem MiT-Tool, komplett umgebaut für **euer**
Business. Eine einzige Datei (`Nexa-CRM.html`), kein Server, keine Installation:
einfach im Browser öffnen. Alle Daten bleiben lokal im Browser (localStorage).

## Öffnen
`Nexa-CRM.html` doppelklicken oder in Chrome/Edge/Firefox ziehen. Fertig.

## Was drin ist (1:1 wie gewohnt)
- **Heute** – Tagesfokus, KPIs, Hot Leads, fällige Wiedervorlagen
- **Kontakte** – Liste, Suche, Filter nach Berater/Segment
- **Pipeline** – Drag & Drop, Win/Loss-Gründe
- **Wiedervorlagen** – überfällig / heute / diese Woche
- **Aktivitäten** – Verlauf, Logging
- **Kalender** – Termine & Wiedervorlagen
- **KI-Assist** – Email-Generator, Anruf-Talking-Points, Einwand-Strategien (nutzt euer Firmenprofil)
- **Analytics** – Forecast, Funnel, Win-Rate, Kategorie-Matrix
- **Wochenbericht** – automatischer Report an einen frei wählbaren Empfänger
- **Excel-/CSV-/JSON-Import & -Export**, Visitenkarten-Scan, KI-Dokument-Import

## Was geändert wurde
- **Turbo-Modus komplett entfernt** (Bulk-Abarbeitung + Vorlagen + Schnell-Nachfass-Button).
  Das normale „Log"/„+7d" und die Wiedervorlagen bleiben unverändert.
- **Umbenannt auf „Nexa·CRM"** – oben links, im Browser-Tab und in allen Exporten/PDFs.
- **Firmenprofil frei konfigurierbar** (Einstellungen → *Branding & Firmenprofil*):
  Name, Untertitel, Firmenname, Pitch und Wochenbericht-Empfänger.
  Die KI-Texte (Email/Anruf/Einwand) nutzen automatisch euren Pitch statt der alten
  Energie-/Aggreko-Texte.
- **Branche/Kategorie** ist jetzt frei (kein fixes Energie-Dropdown mehr) — Vorschläge
  kommen aus euren eigenen importierten Segmenten.

## Listen importieren
Einstellungen → **CRM-Import (.xlsx / .json)** oder das ✦ KI-Import für PDFs.

Erkannte Spalten (Header-Zeile, sprach-/schreibvariantentolerant):
`Firma` / `Name`, `Kontaktperson`, `Ort`/`PLZ`/`Strasse`, `Telefon`,
`E-Mail`/`Mail_1`, `Kategorie`/`Branche`/`Segment`, `Status`, `CHF`/`Betrag`,
`Wiedervorlage`, `Nächster Schritt`.

Beim Import gilt laut Vorgabe:
- **Duplikate** (gleiche Firma + Kontaktperson) werden automatisch übersprungen —
  jeder Kontakt nur **einmal**, auch über mehrere Listen hinweg.
- **Notizen-Spalten werden bewusst NICHT übernommen.**
- **Kategorien/Branchen** aus euren Listen (z. B. „Architekten", „Unternehmen")
  werden 1:1 übernommen.
- Eine reine Firmenliste mit Spalte **„Name"** statt „Firma" wird korrekt als
  Firmenverzeichnis erkannt.

> Feintuning der Spalten-Zuordnung machen wir, sobald deine echten Listen da sind —
> schick sie einfach rein.

## 🎯 Vertriebs-Playbook (Sidebar / Taste 9)
Dein Spickzettel fürs Telefon – fertig aufbereitet und mit dem CRM verzahnt:
- **Telefon-Opener** (mit deinem Namen/Firma aus den Einstellungen) → 📋 Kopieren
- **Einwandbehandlung**: 5 typische Einwände + schlagfertige Antworten →
  📋 Kopieren oder **✦ KI** (öffnet KI-Assist und übernimmt den Einwand für 3 Antwortvarianten)
- **Preismodell** (Setup / SaaS / KI), **Verkaufsprozess** (Calendly → Zoom → Vor Ort) und **USPs**
- Button **📅 Erstgespräch buchen** direkt im Playbook

## 📅 Beratung buchen (Calendly)
Für das kostenlose **30-Min-Erstgespräch per Teams/Zoom**:
1. Einstellungen → *Branding & Firmenprofil* → **Calendly-Buchungslink** eintragen
   (z. B. `https://calendly.com/dein-name/30min`; Calendly „Free" genügt).
2. Nutzen:
   - Sidebar **„📅 Beratung buchen"** → eingebetteter Kalender im Tool
   - Im Kontakt: Button **„📅 30-Min Erstgespräch"** → fertige Einladungs-Mail mit Link
   - KI-Email: Häkchen **„30-Min-Erstgespräch anbieten"** hängt den Buchungslink an
   - Schnellsuche (Ctrl/⌘+K) → „Beratung buchen"

## KI-Assist aktivieren (optional)
Einstellungen → **Anthropic API-Key** eintragen (nur lokal gespeichert).
Key: console.anthropic.com/settings/keys
