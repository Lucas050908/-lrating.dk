-- ølrating.dk – 006: grænser mod spam
-- Køres i Supabase → SQL Editor. Filen afhænger ikke af 003, 004 og 005 og kan køres flere gange uden at gøre skade.
--
-- Hvorfor:
--   Alle kan oprette øl og bedømmelser uden at logge ind (anonymt). Uden en grænse kunne én person med et lille script
--   lægge titusindvis af øl i databasen. Siden henter alle øl og bedømmelser, så det ville gøre siden langsom for alle
--   og fylde lageret i browseren.
--
-- Grænserne (pr. bruger, dvs. pr. enhed eller konto):
--   øl:           højst 40 i timen og 150 i døgnet
--   bedømmelser:  højst 60 i timen og 300 i døgnet
--   Almindelige brugere mærker det ikke, heller ikke på en byttur, hvor man bedømmer mange øl samme aften.
--   At rette noget, man allerede har lavet, tæller ikke med.
--
-- Hvad brugeren ser, hvis grænsen nås:
--   Databasen svarer med fejl 400. Siden beholder øllen på enheden, Min profil siger "kun på denne enhed endnu",
--   og den prøves igen, næste gang siden åbnes.
--
-- Grænserne kan ændres ved at rette tallene i graenser() herunder og køre filen igen.
-- graenser() kan også kaldes udefra. Testen mod den rigtige database bruger den til at se, om filen er kørt.

create or replace function public.graenser() returns jsonb
language sql immutable as $$
  select '{"beers": {"time": 40, "doegn": 150}, "reviews": {"time": 60, "doegn": 300}}'::jsonb
$$;
grant execute on function public.graenser() to anon, authenticated;

create index if not exists beers_owner_created_idx   on public.beers   (owner, created_at);
create index if not exists reviews_owner_created_idx on public.reviews (owner, created_at);

create or replace function public.graense() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  g jsonb := public.graenser() -> tg_table_name; pr_time int; pr_doegn int; n int;
begin
  if g is null then return new; end if;
  pr_time := (g ->> 'time')::int; pr_doegn := (g ->> 'doegn')::int;
  -- En rettelse (upsert af en række, der findes) er ikke en ny række
  execute format('select count(*) from public.%I where id = $1', tg_table_name) into n using new.id;
  if n > 0 then return new; end if;
  execute format('select count(*) from public.%I where owner = $1 and created_at > now() - interval ''1 hour''', tg_table_name) into n using new.owner;
  if n >= pr_time then
    raise exception 'For mange på kort tid: højst % i timen', pr_time using errcode = '23514';
  end if;
  execute format('select count(*) from public.%I where owner = $1 and created_at > now() - interval ''1 day''', tg_table_name) into n using new.owner;
  if n >= pr_doegn then
    raise exception 'For mange på kort tid: højst % i døgnet', pr_doegn using errcode = '23514';
  end if;
  return new;
end $$;
revoke all on function public.graense() from public, anon, authenticated;

drop trigger if exists graense on public.beers;
create trigger graense before insert on public.beers for each row execute function public.graense();
drop trigger if exists graense on public.reviews;
create trigger graense before insert on public.reviews for each row execute function public.graense();
