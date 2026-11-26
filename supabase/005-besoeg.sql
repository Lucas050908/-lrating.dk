-- ølrating.dk – 005: besøgstæller
-- Køres i Supabase → SQL Editor. Filen afhænger ikke af 003 og 004 og kan køres flere gange uden at gøre skade.
--
-- Sådan hænger det sammen:
--   Hver gang siden bliver åbnet, kalder den besoeg(). Databasen lægger 1 til dagens tal og svarer med
--   besøg i alt, besøg i dag, besøg de seneste 7 dage og den første dag, der er talt.
-- Der gemmes kun ét tal pr. dag. Ikke hvem der besøger siden, ingen IP-adresse og ingen enhed.
-- Tallet er derfor, hvor mange gange siden er åbnet. Det er ikke antal personer.
-- Alle kan kalde besoeg(), også flere gange. Tallet er til pynt og kan ikke bruges som en præcis måling.

create table if not exists public.site_visits (
  day    date   primary key,
  visits bigint not null default 0 check (visits >= 0)
);
alter table public.site_visits enable row level security;
-- Ingen regler og ingen rettigheder: Tabellen kan hverken læses eller ændres direkte udefra.
-- Det går kun gennem de to funktioner herunder.
revoke all on public.site_visits from public, anon, authenticated;

create or replace function public.besoeg_tal() returns jsonb
language sql stable security definer set search_path = public as $$
  select jsonb_build_object(
    'total', coalesce(sum(visits), 0),
    'today', coalesce(sum(visits) filter (where day = (now() at time zone 'Europe/Copenhagen')::date), 0),
    'week',  coalesce(sum(visits) filter (where day > (now() at time zone 'Europe/Copenhagen')::date - 7), 0),
    'since', min(day))
  from site_visits
$$;

create or replace function public.besoeg() returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  insert into site_visits(day, visits) values ((now() at time zone 'Europe/Copenhagen')::date, 1)
  on conflict (day) do update set visits = site_visits.visits + 1;
  return besoeg_tal();
end $$;

revoke all on function public.besoeg(), public.besoeg_tal() from public;
grant execute on function public.besoeg(), public.besoeg_tal() to anon, authenticated, service_role;
