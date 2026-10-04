-- NEXA CRM: Schutz gegen veraltete Browser-Stände (Optimistic Locking)
--
-- ACHTUNG: Das echte Schema von crm_state ist noch nicht bekannt.
-- Annahme: crm_state(id <pk>, data jsonb, updated_at timestamptz).
-- Spaltennamen vor dem Ausführen an das echte Schema anpassen.
--
-- Prinzip: Jede Zeile bekommt eine Versionsnummer. Das CRM speichert nur noch
-- über save_crm_state() und schickt die Version mit, die es geladen hat.
-- Passt sie nicht mehr (anderer Tab/Gerät hat inzwischen gespeichert),
-- wird der Speicherversuch abgelehnt und das CRM lädt neu statt zu überschreiben.

alter table crm_state add column if not exists version bigint not null default 0;

create or replace function save_crm_state(p_id text, p_expected_version bigint, p_data jsonb)
returns bigint language plpgsql security invoker as $$
declare new_version bigint;
begin
  update crm_state
     set data = p_data,
         version = version + 1,
         updated_at = now()
   where id::text = p_id
     and version = p_expected_version
  returning version into new_version;

  if new_version is null then
    raise exception 'crm_state_conflict: Version % ist veraltet', p_expected_version
      using errcode = 'P0409';
  end if;
  return new_version;
end $$;

grant execute on function save_crm_state(text, bigint, jsonb) to authenticated;

-- Danach im Frontend: direkte .update()/.upsert() auf crm_state entfernen und
-- durch supabase.rpc('save_crm_state', {...}) ersetzen (siehe README, Abschnitt Frontend).
-- Optional zusätzlich direkte Updates per RLS sperren, sobald das Frontend umgestellt ist:
--   revoke update on crm_state from authenticated;
