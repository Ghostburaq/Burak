# OmniRoute — Technische Analyse und Bewertung

**Gegenstand:** [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute) · MIT-Lizenz · npm `omniroute` v3.8.50
**Stand der Analyse:** 6. August 2026 · Commit `ece486d` (`release/v3.8.50`)
**Methode:** Repository geklont, Abhängigkeiten installiert, Instanz lokal gestartet, Gateway per HTTP getestet, Quellcode gelesen, Testsuite ausgeführt.

---

## 1. Was OmniRoute ist

Ein selbst gehostetes **AI-Gateway**. Es stellt einen OpenAI-kompatiblen Endpunkt
(`/v1/chat/completions`) bereit und verteilt eingehende Anfragen auf viele
Upstream-LLM-Anbieter. Der Zweck: kostenlose Kontingente vieler Anbieter bündeln
und bei Erschöpfung oder Fehler automatisch auf den nächsten Anbieter ausweichen.

Clients wie Claude Code, Codex, Cursor, Cline oder Copilot werden auf den lokalen
Endpunkt gezeigt und merken nichts von der Umleitung.

**Technischer Rahmen**

| Aspekt | Wert |
|---|---|
| Stack | Next.js (App Router), TypeScript, Node ≥ 22.22 |
| Persistenz | SQLite (`better-sqlite3`), 134 Migrationen |
| Auslieferung | npm-Paket, Docker-Image, Electron-Desktop-App |
| Umfang | ~11 000 Dateien, 74 Laufzeit- + 50 Dev-Abhängigkeiten, 166 npm-Skripte |
| Reifegrad | Repo angelegt 13.02.2026 — **unter 6 Monate alt** |
| Verbreitung | 41 335 Stars, 5 467 Forks, 521 offene Issues |

---

## 2. Architektur

### 2.1 Der Weg einer Anfrage

Der Hauptpfad liegt in `src/app/api/v1/chat/completions/route.ts` →
`src/sse/handlers/chat.ts` (1 876 Zeilen) → `open-sse/services/combo.ts` (3 019 Zeilen).

```
Client (Claude Code / Cursor / …)
   │
   ▼
route.ts ─── Zod-Grobvalidierung, Prompt-Injection-Guard, Admission Control
   │
   ▼
handleChatImplementation()          src/sse/handlers/chat.ts
   ├─ Backpressure-Prüfung (Verbindungslimit)
   ├─ Body parsen, Reasoning-Parameter normalisieren
   ├─ Frühe Schema-Gates (messages, model, temperature, top_p, max_tokens)
   ├─ Alias-Auflösung: no-think/…, claude/…, X-Route-Model-Header
   ├─ API-Key-Policy: Modell-Allowlist + Budgetgrenzen
   ├─ Guardrails: Prompt-Injection, PII-Maskierung
   ├─ Benutzer-Hooks (Pre-Request)
   ├─ Task-Aware Routing → Websuche-Routing → Reasoning-Routing
   └─ Combo-Auflösung (getComboForModel)
        │
        ▼
handleComboChat()                   open-sse/services/combo.ts
   ├─ Kandidatenpool bauen (Provider × Modell × Zugangsdaten)
   ├─ Vorfilter: Circuit Breaker, Cooldown, Lockout, Quota-Preflight,
   │             Credential Gate, Konkurrenz-Limits
   ├─ Reihenfolge nach Strategie bestimmen (siehe 2.2)
   ├─ Session-Stickiness / Prompt-Cache-Affinität anwenden
   └─ Sequenziell versuchen → bei Fehler klassifizieren → nächster Kandidat
        │
        ▼
   Upstream-Provider (Anthropic, OpenAI, Gemini, DeepSeek, …)
```

### 2.2 Routing-Strategien

`open-sse/services/combo/strategyDispatch.ts` führt **20** Strategien
(das README nennt 19):

`priority` · `weighted` · `round-robin` · `context-relay` · `fill-first` ·
`p2c` · `random` · `least-used` · `cost-optimized` · `reset-aware` ·
`reset-window` · `headroom` · `strict-random` · `auto` · `lkgp` ·
`context-optimized` · `cache-optimized` · `fusion` · `pipeline` · `quota-share`

Die interessanteste ist `auto` — ein gewichtetes Scoring über zwölf Faktoren
(`src/lib/combos/intelligentRouting.ts`): Quota, Health, Kosten, Latenz,
Task-Fit, Stabilität, Tier-Priorität, Tier-Affinität, Spezifität,
Kontext-Affinität, Cache-Hit-Affinität, Reset-Fenster.

`p2c` (power of two choices) und `lkgp` (last known good provider) sind
Standardverfahren aus dem Load-Balancing — sauber übertragen.

### 2.3 Fallback-Logik

`open-sse/services/accountFallback.ts` klassifiziert Upstream-Fehler in Klassen,
die *unterschiedlich* behandelt werden — das ist der eigentliche Kern des Systems:

- `ACCOUNT_DEACTIVATED_SIGNALS` — Konto tot, dauerhaft ausschließen
- `CREDITS_EXHAUSTED_SIGNALS` — Guthaben leer, bis Reset sperren
- `OAUTH_INVALID_TOKEN_SIGNALS` — Token-Refresh anstoßen
- `RATE_LIMIT_TEXT_PATTERNS` — Cooldown mit `Retry-After`
- `CONTEXT_OVERFLOW_PATTERNS` — Modell mit größerem Fenster wählen
- `MODEL_ACCESS_DENIED_PATTERNS` — nur dieses Modell sperren, nicht den Anbieter
- `MALFORMED_REQUEST_PATTERNS` / `PARAM_VALIDATION_PATTERNS` — Client-Fehler,
  **kein** Fallback (sonst würde man denselben Fehler 11× wiederholen)

Ergänzt um Circuit Breaker pro Verbindung, Failure-Decay, Lockout-Cooldowns und
Rate-Limit-Semaphoren. Diese Differenzierung ist das, was das Projekt von einem
naiven „try next on error“-Proxy unterscheidet.

### 2.4 Token-Kompression

Zwei gestapelte Engines unter `open-sse/services/compression/`:

**RTK** (`engines/rtk/`) komprimiert **Tool-Ergebnisse** — Shell-Ausgaben,
Build-Logs, Testläufe. Befehlsspezifische Filter, Deduplizierung wiederholter
Zeilen, Gruppierung ähnlicher Zeilen, intelligentes Kürzen, Code-Stripping.
Technisch sauber und semantisch risikoarm: Log-Rauschen wegzuwerfen kostet
selten Bedeutung. Bemerkenswert ist die Sorgfalt bei `cache_control`-Markern —
Blöcke mit Prompt-Cache-Breakpoint werden byteweise erhalten, damit der
Anbieter-Cache nicht bei jedem Turn invalidiert wird.

**Caveman** (`caveman.ts`, `cavemanRules.ts`) komprimiert **Prosa** lexikalisch:
Höflichkeitsfloskeln, Hedging („it seems like“, „I think that“), höfliche
Rahmung („could you please“) und redundante Direktiven werden entfernt.

> **Das ist der Teil, den man verstehen muss, bevor man ihn einschaltet.**
> Caveman schreibt den *Prompt des Nutzers* um. Die eingesparten Tokens sind real,
> aber die Annahme „Höflichkeit trägt keine Bedeutung“ stimmt nicht immer — bei
> Instruktionen, in denen Nuancen oder Abstufungen zählen, kann das Verhalten
> kippen. Es gibt Schutzmechanismen (`fidelityGate.ts`, `preservation.ts`,
> `riskGate/`, `validation.ts`), aber die Angabe „~89 % Ersparnis im Schnitt“
> ist ein Aggregat, kein Versprechen pro Anfrage.

RTK allein zu aktivieren und Caveman wegzulassen ist die konservative Konfiguration.

---

## 3. Praxistest — lokal aufgesetzt

Vollständig durchgeführt auf Node 22.22.2 / pnpm 10.33.0.

| Schritt | Ergebnis |
|---|---|
| `pnpm install` | ✅ 1 min 28 s, 4,2 GB `node_modules` |
| `.env` mit generierten Secrets | ✅ (JWT, API-Key-Secret, Storage-Encryption-Key) |
| `pnpm run dev` | ✅ Start sauber, 134 Migrationen angewendet |
| `GET /` ohne Login | ✅ 307 → Login (Auth ist Default) |
| `GET /api/health` ohne Login | ✅ 401 `AUTH_001` |
| Login `POST /api/auth/login` | ✅ 200, Passwort zu bcrypt migriert |
| `GET /dashboard` | ✅ 200 |
| `GET /v1/models` ohne Key | ✅ 401 |
| Gateway-Key anlegen | ✅ 201 |
| `GET /v1/models` mit Key | ✅ **115 Modelle** ohne jede Provider-Konfiguration |
| `POST /v1/chat/completions` | ⚠️ 403 — siehe unten |

**Zum 403:** Die Anfrage an `auto/best-coding` durchlief die Routing-Maschinerie
korrekt — Pool von 11 Kandidaten gebaut, zwei in Reihenfolge versucht
(`opencode/oc/big-pickle`, dann `felo-web/felo/felo-chat`), beide mit HTTP 403
vom Upstream. Die Antwort enthielt strukturierte Diagnostik mit Versuchsreihenfolge,
Ausschlussgründen und Recovery-Hinweis.

Die 403 stammen **nicht von OmniRoute**: Ein direkter `curl` auf `felo.ai` und
`opencode.ai` aus derselben Umgebung scheitert mit `CONNECT tunnel failed,
response 403` — der Egress-Proxy dieser Sandbox blockiert die Hosts. Das Gateway
selbst funktioniert; die Upstream-Erreichbarkeit war umgebungsbedingt nicht gegeben.
**Ein echter End-to-End-Durchstich bis zu einer LLM-Antwort steht damit aus** und
müsste in einer Umgebung mit freiem Egress nachgeholt werden.

---

## 4. Sicherheits- und Eignungsbewertung

### 4.1 Positiv

**Verschlüsselung der Anbieter-Zugangsdaten.** `apiKey`, `accessToken`,
`refreshToken` und `idToken` der Provider-Verbindungen werden feldweise mit
**AES-256-GCM** verschlüsselt (`src/lib/db/encryption.ts`, `src/lib/db/providers.ts`)
und nur lazy entschlüsselt. Der GCM-Auth-Tag ist auf volle 16 Byte gepinnt, was
Tag-Truncation-Forgery ausschließt. Der `STORAGE_ENCRYPTION_KEY` wird beim ersten
echten CLI-Start automatisch generiert und in `~/.omniroute/.env` persistiert.

**Auth ist Default.** Dashboard und Gateway verlangen ohne Konfiguration
Authentifizierung. `INITIAL_PASSWORD` wird beim Start zu bcrypt gehasht.

**Kein Phone-Home in der Standardkonfiguration.** `CLOUD_URL` ist leer
voreingestellt; Cloud-Sync ist Opt-in. Seit v3.8.6 überschreibt der Sync
standardmäßig **keine** Zugangsdaten mehr, sondern nur Metadaten — ein
fehlkonfiguriertes oder feindliches `CLOUD_URL` kann keine OAuth-Tokens
austauschen. Antworten werden per HMAC-SHA256 signiert und mit
`crypto.timingSafeEqual` geprüft. Der einzige beobachtete ausgehende Verkehr im
Leerlauf ist die anonyme Telemetrie von Next.js selbst.

**Ernstzunehmende Qualitätsinfrastruktur.** 24 CI-Workflows: CodeQL, Semgrep,
OSSF Scorecard, DAST-Smoke, nightly LLM-Security, Mutation Testing (Stryker),
Property-Tests, Schemathesis, Resilienz-Tests. Dazu vier ESLint-Konfigurationen
inklusive Komplexitäts-Ratchets, gitleaks, trivy, zizmor, Socket.dev, SonarQube.
Der Code enthält durchgängig Kommentare, die konkrete Issue-Nummern und
Regressionsursachen benennen — ein Zeichen echter Betriebserfahrung, nicht
generierter Fassade.

**Ehrliche ToS-Dokumentation.** `docs/reference/FREE_TIERS.md` führt eine
explizite „ToS attention table“ mit 17 namentlich gelisteten Anbietern, deren
Nutzungsbedingungen Proxy-, Weiterverkaufs- oder Nicht-kommerziell-Klauseln
enthalten — inklusive wörtlicher Zitate der einschlägigen Paragraphen. Ein
Projekt, das seine eigenen rechtlichen Grauzonen so offenlegt, ist selten.

### 4.2 Befunde

**Gateway-API-Keys liegen im Klartext in der Datenbank.** Verifiziert: Die
Tabelle `api_keys` führt sowohl `key` als auch `key_hash`; der Lookup lautet
`WHERE key = ? OR key_hash = ?`. Der von mir angelegte Schlüssel stand im
Klartext in `storage.sqlite` — **auch bei gesetztem `STORAGE_ENCRYPTION_KEY`**,
da `apiKeys.ts` die Feldverschlüsselung nicht verwendet. Vermutlicher Grund:
Das Dashboard soll den Schlüssel später noch anzeigen können. Praktische Folge:
Wer Lesezugriff auf die SQLite-Datei bekommt, hat funktionsfähige Gateway-Keys.
Der Schaden ist begrenzt (es sind selbst ausgestellte Keys, nicht die
Anbieter-Zugangsdaten), aber die Datei gehört entsprechend geschützt.

**Kein `pnpm-lock.yaml` im Repository.** Die Dokumentation weist pnpm als
Paketmanager aus (`pnpm-workspace.yaml`, `pnpm.json` sind vorhanden), committet
ist aber nur `package-lock.json`. Wer der Anleitung folgt und `pnpm install`
ausführt, löst alle Abhängigkeiten **frisch auf** statt gepinnt — bei 124
direkten und mehreren tausend transitiven Paketen ist das eine reale
Supply-Chain-Lücke. Für reproduzierbare Installationen: `npm ci` verwenden oder
den selbst erzeugten pnpm-Lockfile festhalten.

**`STORAGE_ENCRYPTION_KEY` leer = Klartext.** Die Verschlüsselung fällt
kommentarlos in einen Passthrough-Modus, wenn der Schlüssel fehlt. Beim CLI-Start
wird er automatisch bereitgestellt — beim Start aus dem Quellcode oder in Docker
ohne gesetzte Variable **nicht**. Dann liegen sämtliche Anbieter-OAuth-Tokens
unverschlüsselt in der SQLite-Datei. Die Variable ist beim Deployment
verpflichtend zu setzen.

**Toter Import im heißen Pfad.** `route.ts` importiert
`callCloudWithMachineId` — eine Funktion, die den Request-Body an eine externe
Cloud-URL weiterreicht — ruft sie aber nirgends auf. Harmlos in der Wirkung,
aber in genau der Datei, in der man so etwas am wenigsten sehen will. Ein
Aufräumen wäre angebracht.

**Reifegrad vs. Verbreitung.** 41 000 Stars in unter sechs Monaten bei einem
Projekt mit einem einzelnen Maintainer als Namensgeber. Der Default-Branch ist
`release/v3.8.50` — ein Release-Branch als Default ist unüblich und erschwert
das Nachvollziehen der Hauptentwicklungslinie. 521 offene Issues. Die
Qualitätsinfrastruktur ist echt, aber sie ist jung, und die Codebasis wächst
schneller, als eine Person sie prüfen kann.

**ToS-Risiko ist keine Theorie.** Von den zwei Anbietern, die mein Testaufruf
in der Standardkonfiguration ansteuerte, steht `opencode` namentlich in der
ToS-Warntabelle des Projekts selbst: Die Bedingungen beschränken die Nutzung auf
„your own internal use, and not on behalf of or for the benefit of any third
party“. Das Zero-Config-Setup routet also ohne Zutun auf Anbieter mit
einschlägigen Klauseln. Für den privaten Einzelgebrauch mag das vertretbar sein
— **für einen geschäftlichen Einsatz ist es das nicht**, und die Prüfung lässt
sich nicht delegieren.

**Ein Ort für alle Schlüssel.** Das Produkt sammelt konstruktionsbedingt
sämtliche LLM-Zugangsdaten an einer Stelle, inklusive per OAuth importierter
Sitzungen aus anderen CLIs (`/api/oauth/[provider]` unterstützt Codex, Cursor,
Kiro, Trae, Copilot). Das ist kein Fehler, sondern der Zweck — aber es macht
die Instanz zu einem Ziel mit hohem Ertrag. Sie gehört nicht ins offene Netz.

### 4.3 Nuance zum Cloud-Sync

Wird Cloud-Sync aktiviert (`CLOUD_URL` gesetzt), werden auch die
**Gateway-API-Keys** an die Cloud übertragen — `syncKeysToCloudIfEnabled()` in
`src/app/api/keys/route.ts` läuft bei jeder Key-Erstellung und -Änderung, gated
auf `isCloudEnabled()`. In der Standardkonfiguration passiert nichts. Wer
Cloud-Sync einschaltet, sollte wissen, dass damit nicht nur Einstellungen die
Maschine verlassen.

---

## 5. Fazit

**Handwerklich besser als erwartet.** Die Fehlerklassifikation im Fallback-Pfad,
die Prompt-Cache-Behandlung in RTK und die Sorgfalt der Verschlüsselung sind
Arbeit von jemandem, der die Probleme im Betrieb erlebt hat. Das ist kein
Wochenend-Wrapper.

**Wofür es sich eignet:** privater Einzelgebrauch, Experimentierumgebungen,
Kostenreduktion bei eigenen Entwicklungs-Workflows. Der Nutzen — Ausfallsicherheit
über Anbietergrenzen hinweg und Token-Ersparnis bei Tool-Ergebnissen — ist real
und schwer selbst nachzubauen.

**Wofür nicht, ohne vorherige Prüfung:** produktive oder geschäftliche Nutzung.
Nicht wegen der Codequalität, sondern wegen dreier Punkte, die unabhängig
davon bestehen: die ToS-Lage bei einem relevanten Teil der Anbieter, die
Konzentration aller Zugangsdaten in einer Instanz, und ein Projektalter von
unter sechs Monaten bei sehr hoher Änderungsrate.

**Empfehlung bei Einsatz:**

1. `STORAGE_ENCRYPTION_KEY` explizit setzen — nicht auf Auto-Provisionierung verlassen.
2. Installation über `npm ci` (gepinnter Lockfile), nicht `pnpm install`.
3. Nur an `127.0.0.1` binden, kein Reverse-Proxy ins Netz.
4. `storage.sqlite` mit restriktiven Dateirechten versehen (Gateway-Keys im Klartext).
5. Anbieter bewusst auswählen — die ToS-Warntabelle des Projekts durchgehen,
   statt die Zero-Config-Voreinstellung zu übernehmen.
6. Kompression: mit RTK beginnen, Caveman erst nach eigener Qualitätsprüfung.
7. Version pinnen und Updates gezielt einspielen — bei dieser Änderungsrate ist
   automatisches Aktualisieren riskant.

---

## Nachtrag: Testsuite-Ergebnis

Das Projekt enthält **3 922 Unit-Testdateien**. Ein vollständiger Durchlauf war
in dieser Umgebung nicht möglich — nach 25 Minuten war die Suite alphabetisch
erst bei den `chat-*`-Dateien angelangt (561 Tests bis dahin, 0 Fehlschläge).
Der Lauf wurde abgebrochen und durch gezielte Teilsuiten ersetzt, die für die
Bewertung oben relevant sind:

| Teilsuite | Dateien | Tests | Bestanden | Fehlgeschlagen |
|---|---:|---:|---:|---:|
| `security` + `auth` + `authz` + `combo` | 42 | 416 | **416** | **0** |
| `compression` | 212 | 1 374 | **1 374** | **0** |

Beide Läufe mit Exit-Code 0. Das ist kein Beleg für die Gesamtsuite, aber die
beiden Bereiche, auf die sich die Bewertung in Abschnitt 2.4 und 4 stützt, sind
dicht und grün getestet.

---

*Erstellt am 6. August 2026. Alle Angaben beruhen auf eigener Ausführung und
Quellcode-Lektüre des Commits `ece486d`, nicht auf den Angaben des Projekts.
Behauptungen aus dem README (Anzahl freier Tokens, durchschnittliche
Kompressionsrate) wurden nicht nachgerechnet und sind hier nicht bestätigt.*
