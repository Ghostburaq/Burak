-- NEXA Follow-up-Automation: Kern-Schema
-- Bewusst NICHT in crm_state. Scheduler-Daten leben in eigenen Tabellen,
-- damit ein alter Browser-Stand sie nie überschreiben kann.
-- Ausführen: Supabase SQL-Editor oder `supabase db push`.

-- ---------------------------------------------------------------
-- Einstellungen (eine Zeile). Testmodus ist standardmässig AN.
-- ---------------------------------------------------------------
create table if not exists followup_settings (
  id              int primary key default 1 check (id = 1),
  dry_run         boolean not null default true,          -- true = nichts geht an echte Kunden
  test_recipients text[]  not null default '{}',          -- Whitelist im Testmodus
  send_window_start time  not null default '08:00',
  send_window_end   time  not null default '17:00',
  timezone        text    not null default 'Europe/Zurich',
  sender_email    text,
  sender_name     text,
  test_day_minutes int,                                   -- nur Testmodus: 1 "Tag" = N Minuten (z.B. 5)
  grace_days      int     not null default 5,             -- nach letztem Follow-up noch auf Antwort warten
  -- Pflicht-Fusszeile in jeder automatischen Mail (Absender + Abmeldehinweis,
  -- CH: Art. 3 Abs. 1 lit. o UWG, DE: § 7 UWG / Art. 21 DSGVO, AT: § 174 TKG)
  footer          text    not null default E'\n\n--\nNEXA\nWenn Sie keine weiteren Nachrichten zu diesem Thema wünschen, antworten Sie kurz mit "Abmelden".',
  updated_at      timestamptz not null default now()
);
insert into followup_settings (id) values (1) on conflict do nothing;

-- ---------------------------------------------------------------
-- Kampagnen / Sequenzen
-- ---------------------------------------------------------------
create table if not exists sequences (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  kind        text not null default 'offer_followup'
              check (kind in ('offer_followup', 'lead_followup', 'acquisition')),
  active      boolean not null default true,
  created_at  timestamptz not null default now()
);

-- Schritt 0 = Erstmail, 1 = Follow-up 1 (Tag 4), 2 = Follow-up 2 (Tag 9)
create table if not exists sequence_steps (
  sequence_id     uuid not null references sequences(id) on delete cascade,
  step_no         int  not null check (step_no >= 0),
  offset_days     int  not null check (offset_days >= 0),   -- Kalendertage ab Erstmail
  subject_tpl     text,                                     -- null = "Re: <Original-Betreff>"
  body_tpl        text not null,                            -- Platzhalter: {{vorname}}, {{firma}}, {{offerte_nr}}
  primary key (sequence_id, step_no)
);

-- ---------------------------------------------------------------
-- Enrollment = ein Lead/Kontakt in einer Kampagne
-- lead_ref verweist auf die ID im bestehenden CRM (crm_state), ohne FK,
-- weil crm_state ein JSON-Gesamtzustand ist.
-- ---------------------------------------------------------------
create table if not exists enrollments (
  id              uuid primary key default gen_random_uuid(),
  sequence_id     uuid not null references sequences(id),
  lead_ref        text not null,
  contact_email   text not null,
  contact_name    text,
  company         text,
  vars            jsonb not null default '{}'::jsonb,       -- Template-Variablen
  status          text not null default 'active'
                  check (status in ('active','replied','not_interested','bounced',
                                    'stopped_manual','completed','error')),
  stop_reason     text,
  reply_class     text check (reply_class in ('interessiert','kein_interesse','unklar')),
  reply_class_confirmed boolean not null default false,     -- Mensch hat bestätigt
  current_step    int  not null default -1,                 -- zuletzt gesendeter Schritt (-1 = Erstmail noch offen,
                                                            --  0 = Erstmail draussen, manuell oder automatisch)
  subject         text,                                     -- Betreff der Erstmail (Follow-ups: "Re: ...")
  started_at      timestamptz,                              -- Versand Erstmail
  last_sent_at    timestamptz,
  next_run_at     timestamptz,                              -- null = nichts mehr geplant
  thread_id       text,                                     -- Gmail threadId / Graph conversationId
  last_message_id text,                                     -- RFC Message-ID für In-Reply-To
  locked_until    timestamptz,                              -- Runner-Lock
  attempts        int  not null default 0,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  unique (sequence_id, lead_ref)
);
create index if not exists enrollments_due_idx
  on enrollments (next_run_at) where status = 'active';

-- ---------------------------------------------------------------
-- Jede gesendete/empfangene Mail. Unique (enrollment, step, direction=out)
-- verhindert Doppelversand, auch wenn der Cron zweimal läuft.
-- ---------------------------------------------------------------
create table if not exists followup_messages (
  id              uuid primary key default gen_random_uuid(),
  enrollment_id   uuid not null references enrollments(id) on delete cascade,
  step_no         int,
  direction       text not null check (direction in ('out','in')),
  dry_run         boolean not null default false,
  provider_msg_id text,
  rfc_message_id  text,
  thread_id       text,
  to_email        text,
  subject         text,
  body            text,
  sent_at         timestamptz not null default now()
);
create unique index if not exists followup_messages_once_per_step
  on followup_messages (enrollment_id, step_no) where direction = 'out';
create unique index if not exists followup_messages_inbound_once
  on followup_messages (provider_msg_id) where direction = 'in';

-- ---------------------------------------------------------------
-- Sperrliste: wer abgemeldet hat, abgesagt hat oder gebounced ist,
-- bekommt nie wieder eine automatische Mail (gilt über alle Kampagnen).
-- ---------------------------------------------------------------
create table if not exists followup_suppression (
  email       text primary key,
  reason      text not null,      -- opt_out, not_interested, bounce, manual
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------
-- Audit-Log: alles, was passiert, für die CRM-Timeline
-- ---------------------------------------------------------------
create table if not exists followup_events (
  id             bigint generated always as identity primary key,
  enrollment_id  uuid references enrollments(id) on delete cascade,
  type           text not null,  -- enrolled, sent, dry_run_sent, reply_detected, bounce_detected,
                                 -- classified, stopped, completed, error, skipped_window
  detail         jsonb not null default '{}'::jsonb,
  created_at     timestamptz not null default now()
);
create index if not exists followup_events_enr_idx on followup_events (enrollment_id, created_at desc);

-- ---------------------------------------------------------------
-- Übersicht fürs CRM-UI: welche Kampagne läuft, letzte Mail, nächstes Follow-up
-- ---------------------------------------------------------------
create or replace view followup_overview with (security_invoker = true) as
select
  e.id, e.lead_ref, e.company, e.contact_name, e.contact_email,
  s.name as sequence_name, e.status, e.stop_reason, e.reply_class, e.reply_class_confirmed,
  e.current_step, e.last_sent_at, e.next_run_at,
  (select max(ss.step_no) from sequence_steps ss where ss.sequence_id = e.sequence_id) as last_step
from enrollments e
join sequences s on s.id = e.sequence_id;

-- updated_at pflegen
create or replace function touch_updated_at() returns trigger language plpgsql as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists enrollments_touch on enrollments;
create trigger enrollments_touch before update on enrollments
  for each row execute function touch_updated_at();

-- ---------------------------------------------------------------
-- Runner holt fällige Enrollments atomar (kein Doppel-Run bei parallelen Aufrufen)
-- ---------------------------------------------------------------
create or replace function claim_due_enrollments(batch int default 20, lock_minutes int default 10)
returns setof enrollments language plpgsql security definer as $$
begin
  return query
  update enrollments e set locked_until = now() + make_interval(mins => lock_minutes),
                           attempts = e.attempts + 1
  where e.id in (
    select id from enrollments
    where status = 'active'
      and next_run_at is not null and next_run_at <= now()
      and (locked_until is null or locked_until < now())
    order by next_run_at
    limit batch
    for update skip locked
  )
  returning e.*;
end $$;

-- Manueller Stopp aus dem CRM (ein Klick)
create or replace function stop_enrollment(p_id uuid, p_reason text default 'manual')
returns void language plpgsql security definer as $$
begin
  update enrollments set status = 'stopped_manual', stop_reason = p_reason,
                         next_run_at = null, locked_until = null
  where id = p_id and status = 'active';
  insert into followup_events (enrollment_id, type, detail)
  values (p_id, 'stopped', jsonb_build_object('reason', p_reason));
end $$;

-- ---------------------------------------------------------------
-- RLS: nur eingeloggte Nutzer lesen; Schreiben macht der Runner (service_role)
-- Falls das CRM ohne Supabase-Auth läuft: Policies an das CRM anpassen.
-- ---------------------------------------------------------------
alter table followup_settings enable row level security;
alter table sequences         enable row level security;
alter table sequence_steps    enable row level security;
alter table enrollments       enable row level security;
alter table followup_messages enable row level security;
alter table followup_events   enable row level security;
alter table followup_suppression enable row level security;

do $$
declare t text;
begin
  foreach t in array array['followup_settings','sequences','sequence_steps','enrollments',
                           'followup_messages','followup_events','followup_suppression']
  loop
    execute format('drop policy if exists %I_read on %I', t, t);
    execute format('create policy %I_read on %I for select to authenticated using (true)', t, t);
  end loop;
end $$;

-- Sequenzen/Steps/Enrollments anlegen und bearbeiten darf das CRM (authenticated)
create policy sequences_write on sequences for all to authenticated using (true) with check (true);
create policy steps_write     on sequence_steps for all to authenticated using (true) with check (true);
create policy enr_insert      on enrollments for insert to authenticated with check (status = 'active');
create policy suppression_add on followup_suppression for insert to authenticated with check (true);
-- Testmodus umschalten und Einstellungen pflegen
create policy settings_write  on followup_settings for update to authenticated using (true) with check (true);
-- Status-Änderungen am Enrollment nur über stop_enrollment() oder den Runner
grant execute on function stop_enrollment(uuid, text) to authenticated;
