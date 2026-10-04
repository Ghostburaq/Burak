# NEXA Follow-up-Automation

Technische Grundlage für das automatische Nachfassen von Offerten und Leads im bestehenden NEXA CRM (Supabase + Netlify). Kein zweites CRM: Es kommen nur eigene Tabellen und eine Edge Function dazu. Das CRM-Frontend liest daraus.

## Ablauf

```
Tag 0   Erstmail (automatisch gesendet oder manuell gesendet und dokumentiert)
Tag 4   Follow-up 1, im gleichen Thread ("Re: ...")
Tag 9   Follow-up 2, im gleichen Thread
+5 Tage Wartezeit auf Antwort, danach Status "completed"

Sofortiger Stopp bei: Antwort | "kein Interesse" | Bounce | manueller Stopp | Eintrag auf Sperrliste
Abwesenheitsnotizen stoppen nicht, werden aber dokumentiert.
```

- Tage sind Kalendertage ab der Erstmail. Fällt ein Termin auf ein Wochenende oder ausserhalb von 08:00 bis 17:00 (Europe/Zurich), geht die Mail im nächsten Sendefenster raus.
- Unmittelbar vor jedem Versand wird der Thread nochmals auf eine Antwort geprüft.
- Doppelversand ist auf Datenbankebene ausgeschlossen (Unique-Index pro Enrollment und Schritt, atomarer Claim mit `FOR UPDATE SKIP LOCKED`).

## Bausteine

| Datei | Zweck |
|---|---|
| `supabase/migrations/..._followup_core.sql` | Tabellen `sequences`, `sequence_steps`, `enrollments`, `followup_messages`, `followup_events`, `followup_suppression`, `followup_settings`, View `followup_overview`, RPCs `claim_due_enrollments`, `stop_enrollment` |
| `supabase/migrations/..._crm_state_version_guard.sql` | Versionsschutz für `crm_state` (RPC `save_crm_state`). **Vor dem Ausführen an das echte Schema anpassen.** |
| `supabase/migrations/..._cron.sql` | pg_cron ruft den Runner alle 15 Minuten auf |
| `supabase/functions/followup-runner/` | Edge Function: Antworterkennung, Versand im Thread, Klassifizierung |

## Das crm_state-Problem und die Lösung

1. **Automation ausserhalb von `crm_state`.** Alle Scheduler-Daten (nächster Termin, letzte Mail, Status) liegen in eigenen Tabellen. Nur der Runner schreibt sie. Ein alter Browser-Tab kann sie nicht überschreiben, weil das Frontend sie nie als Ganzes zurückschreibt.
2. **Optimistic Locking für `crm_state`.** Speichern nur noch über `save_crm_state(id, erwartete_version, data)`. Hat inzwischen ein anderer Tab gespeichert, kommt ein Fehler `crm_state_conflict` und das CRM lädt neu, statt zu überschreiben.

## Testmodus

Der Testmodus ist standardmässig **an** (`followup_settings.dry_run = true`):

- Mails gehen nur an Adressen in `test_recipients`. Alles andere wird als `dry_run_sent` geloggt, aber nicht versendet.
- Mit `test_day_minutes = 5` dauert ein "Tag" 5 Minuten. Eine komplette Sequenz (Tag 0, 4, 9) läuft so in rund einer Stunde durch.

Scharf schalten erst, wenn ein Testlauf mit eigener Adresse sauber durch ist:

```sql
update followup_settings set dry_run = false, test_day_minutes = null where id = 1;
```

## Einrichtung (einmalig)

1. **Migrationen ausführen**: SQL-Editor oder `supabase db push`. Migration 2 vorher an das echte `crm_state`-Schema anpassen.
2. **Gmail-Zugang**: In der Google Cloud Console einen OAuth-Client anlegen (Gmail API aktivieren, Scope `gmail.modify`). Für das Absender-Postfach einmalig einen Refresh-Token erzeugen.
3. **Secrets setzen** (niemals ins Repo oder in den Chat):
   ```bash
   supabase secrets set RUNNER_SECRET=<langer-zufallswert> \
     GMAIL_CLIENT_ID=... GMAIL_CLIENT_SECRET=... GMAIL_REFRESH_TOKEN=... \
     ANTHROPIC_API_KEY=...        # optional, für die Antwort-Klassifizierung
   supabase functions deploy followup-runner --no-verify-jwt
   ```
4. **Vault-Secrets für den Cron** (`project_url`, `runner_secret`), siehe Kommentar in der Cron-Migration.
5. **Einstellungen setzen**:
   ```sql
   update followup_settings set sender_email = 'info@nexa.ch', sender_name = 'NEXA',
     test_recipients = '{deine@adresse.ch}', test_day_minutes = 5 where id = 1;
   ```
   Die Absenderadresse ist ein Platzhalter und muss durch eure echte ersetzt werden.

## Anbindung im CRM-Frontend

```js
// Lead in Kampagne aufnehmen, Erstmail sendet der Runner
await supabase.from('enrollments').insert({
  sequence_id, lead_ref: lead.id, contact_email: lead.email,
  contact_name: lead.name, company: lead.firma, vars: { offerte_nr: 'NX-2026-014' },
  next_run_at: new Date().toISOString(),
});

// Erstmail wurde manuell aus Gmail gesendet: nur dokumentieren, Follow-ups automatisch
await supabase.from('enrollments').insert({
  sequence_id, lead_ref: lead.id, contact_email: lead.email,
  current_step: 0, started_at: gesendetAm, thread_id: gmailThreadId,
  next_run_at: new Date().toISOString(),
});

// Übersicht: Kampagne, letzte Mail, nächstes Follow-up, Status
const { data } = await supabase.from('followup_overview').select('*').eq('lead_ref', lead.id);

// Timeline
const { data: events } = await supabase.from('followup_events')
  .select('*').eq('enrollment_id', id).order('created_at', { ascending: false });

// Manueller Stopp
await supabase.rpc('stop_enrollment', { p_id: id, p_reason: 'manual' });
```

Die Antwort-Klassifizierung (interessiert, kein Interesse, unklar) ist ein Vorschlag. Im CRM bestätigt ein Mensch per Klick (`reply_class_confirmed = true`).

## Recht (Kurzfassung, keine Rechtsberatung)

- Jede automatische Mail enthält eine Fusszeile mit Absender und Abmeldehinweis (`followup_settings.footer`).
- Abmeldungen, Absagen und Bounces landen auf der Sperrliste und gelten über alle Kampagnen.
- **CH:** Die Lauterkeitskommission (SLK 172/20) stellt bei Art. 3 Abs. 1 lit. o UWG auf die Automatisierung ab, nicht auf die Anzahl. Nachfassen auf eine angefragte Offerte ist vertretbar. Automatisierte Kaltakquise ohne Einwilligung ist riskant.
- **DE** (§ 7 Abs. 2 Nr. 2 UWG) und **AT** (§ 174 TKG 2021): E-Mail-Werbung braucht auch im B2B eine vorherige Einwilligung.
- Die Texte der Sequenzen vor dem Livegang von einem Anwalt prüfen lassen.

## Offen

- [ ] Echten CRM-Code anbinden (Repo fehlt noch). Danach UI für Kampagnen, Timeline und Stopp-Button.
- [ ] Migration 2 an das echte `crm_state`-Schema anpassen und Frontend auf `save_crm_state` umstellen.
- [ ] Microsoft-365-Provider (Graph API), falls Kunden Outlook nutzen. Gmail ist umgesetzt.
- [ ] Feiertage (CH, kantonal) im Sendefenster.

## Tests

```bash
cd supabase/functions/followup-runner
deno test schedule_test.ts   # Zeitlogik inkl. Wochenende und Zeitumstellung
deno check index.ts
```
