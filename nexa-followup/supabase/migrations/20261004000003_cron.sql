-- Scheduler: pg_cron ruft alle 15 Minuten die Edge Function followup-runner auf.
-- Voraussetzung: Extensions pg_cron und pg_net aktiv (Dashboard > Database > Extensions)
-- und zwei Vault-Secrets angelegt:
--   select vault.create_secret('https://<PROJECT-REF>.supabase.co', 'project_url');
--   select vault.create_secret('<RUNNER_SECRET>', 'runner_secret');
-- RUNNER_SECRET ist ein frei gewählter langer Zufallswert, derselbe wie in den
-- Edge-Function-Secrets (supabase secrets set RUNNER_SECRET=...).

create extension if not exists pg_cron;
create extension if not exists pg_net;

select cron.unschedule('nexa-followup-runner')
where exists (select 1 from cron.job where jobname = 'nexa-followup-runner');

select cron.schedule(
  'nexa-followup-runner',
  '*/15 * * * *',
  $$
  select net.http_post(
    url     := (select decrypted_secret from vault.decrypted_secrets where name = 'project_url')
               || '/functions/v1/followup-runner',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'x-runner-secret', (select decrypted_secret from vault.decrypted_secrets where name = 'runner_secret')
    ),
    body    := '{}'::jsonb,
    timeout_milliseconds := 55000
  );
  $$
);
