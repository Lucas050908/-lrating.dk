-- ølrating.dk – 004: udsendelse af mails
-- Køres i Supabase → SQL Editor, EFTER 003-konto-mails-enig.sql og efter at funktionen "mails" er oprettet
-- (se docs/KONTO.md). Filen kan køres flere gange uden at gøre skade.
--
-- Sådan hænger det sammen:
--   1. Triggerne fra 003 lægger en række i mail_queue, når der sker noget, en bruger vil have mail om.
--   2. Hvert 10. minut kalder databasen selv funktionen "mails" (supabase/functions/mails), hvis køen ikke er tom.
--   3. Funktionen henter det, der skal sendes, med mail_hent(), sender det gennem mailtjenesten og kvitterer med mail_faerdig().
-- Alle regler (højst én mail i timen, venner højst én gang om dagen, fravalg) står her i databasen, så de kan testes.

-- ---------------------------------------------------------------------------
-- 1) Køen kan også rumme nyheder, og en række kan være "taget" af en udsendelse, der er i gang.
-- ---------------------------------------------------------------------------
alter table public.mail_queue drop constraint if exists mail_queue_kind_check;
alter table public.mail_queue add constraint mail_queue_kind_check check (kind in ('my_beer', 'friends', 'events', 'news'));
alter table public.mail_queue add column if not exists taken_at timestamptz;

-- ---------------------------------------------------------------------------
-- 2) En nøgle, som kun databasen kender. Det planlagte job sender den med, så ingen udefra kan sætte en udsendelse i gang.
-- ---------------------------------------------------------------------------
create table if not exists public.mail_state (
  id int primary key default 1 check (id = 1),
  cron_key uuid not null default gen_random_uuid(),
  last_run timestamptz
);
alter table public.mail_state enable row level security;   -- ingen regler: kun serveren
revoke all on public.mail_state from anon, authenticated;
insert into public.mail_state (id) values (1) on conflict (id) do nothing;

-- ---------------------------------------------------------------------------
-- 3) Nyheder om siden. Skriv en række i mail_news (Table Editor), læs den igennem, og sæt så flueben i "send".
--    Så bliver den lagt i kø til alle, der har slået nyheder til. Den kan ikke fortrydes, når fluebenet er sat.
-- ---------------------------------------------------------------------------
alter table public.mail_news add column if not exists send boolean not null default false;
create or replace function public.mail_nyhed() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.send and new.sent_at is null then
    insert into mail_queue (user_id, kind, data)
      select p.user_id, 'news', jsonb_build_object('news', new.id) from mail_prefs p where p.news;
    new.sent_at := now();
  end if;
  return new;
end $$;
drop trigger if exists mail_nyhed on public.mail_news;
create trigger mail_nyhed before insert or update on public.mail_news for each row execute function public.mail_nyhed();

-- ---------------------------------------------------------------------------
-- 4) mail_hent: giver funktionen "mails" det, der skal sendes nu – én samlet mail pr. bruger.
--    Regler: højst én mail i timen pr. bruger, "venner bedømmer" højst én gang om dagen (dansk dato),
--    typer, brugeren har slået fra, bliver slettet, og rækkerne mærkes som taget, så de ikke sendes to gange.
-- ---------------------------------------------------------------------------
create or replace function public.mail_hent(k uuid, n int default 20) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  st record; u record; res jsonb := '[]'::jsonb; ids bigint[]; items jsonb;
  today date := (now() at time zone 'Europe/Copenhagen')::date;
begin
  select * into st from mail_state where id = 1 for update;   -- kun én udsendelse ad gangen
  if st.cron_key is null or k is null or st.cron_key <> k then
    raise exception 'forkert nøgle' using errcode = '42501';
  end if;
  update mail_state set last_run = now() where id = 1;

  -- oprydning: gamle rækker væk, og rækker fra en udsendelse, der gik i stå, bliver frigivet
  delete from mail_queue where sent_at is not null and sent_at < now() - interval '7 days';
  delete from mail_queue where sent_at is null and created_at < now() - interval '3 days';
  update mail_queue set taken_at = null where sent_at is null and taken_at < now() - interval '30 minutes';
  -- det, brugeren har slået fra siden sidst, skal ikke sendes
  delete from mail_queue q using mail_prefs p
    where q.sent_at is null and q.taken_at is null and p.user_id = q.user_id
      and not (case q.kind when 'news' then p.news when 'my_beer' then p.my_beer when 'friends' then p.friends else p.events end);
  delete from mail_queue q where q.sent_at is null and not exists (select 1 from mail_prefs p where p.user_id = q.user_id);

  for u in
    select p.user_id, p.name, p.lang, p.unsub, p.friends_sent, a.email
    from mail_prefs p join auth.users a on a.id = p.user_id
    where a.email is not null and coalesce(a.is_anonymous, false) = false
      and (p.last_sent is null or p.last_sent < now() - interval '1 hour')
      and not exists (select 1 from mail_queue q where q.user_id = p.user_id and q.sent_at is null and q.taken_at is not null)
      and exists (select 1 from mail_queue q where q.user_id = p.user_id and q.sent_at is null and q.taken_at is null
                  and (q.kind <> 'friends' or p.friends_sent is distinct from today))
    order by (select min(q.id) from mail_queue q where q.user_id = p.user_id and q.sent_at is null)
    limit greatest(1, least(coalesce(n, 20), 50))
  loop
    with c as (
      select q.id from mail_queue q
      where q.user_id = u.user_id and q.sent_at is null and q.taken_at is null
        and (q.kind <> 'friends' or u.friends_sent is distinct from today)
      order by q.id limit 40
    ), t as (
      update mail_queue q set taken_at = now() from c where q.id = c.id returning q.id, q.kind, q.data
    )
    select array_agg(t.id order by t.id),
           jsonb_agg(jsonb_build_object('kind', t.kind, 'data',
             case when t.kind = 'news' then (
               select jsonb_build_object(
                 'subject', case when u.lang = 'en' and coalesce(m.subject_en, '') <> '' and coalesce(m.body_en, '') <> '' then m.subject_en else m.subject_da end,
                 'body',    case when u.lang = 'en' and coalesce(m.subject_en, '') <> '' and coalesce(m.body_en, '') <> '' then m.body_en else m.body_da end)
               from mail_news m where m.id = (t.data->>'news')::bigint)
             else t.data end) order by t.id)
      into ids, items from t;
    if ids is not null then
      res := res || jsonb_build_object('user', u.user_id, 'email', u.email, 'name', u.name, 'lang', u.lang,
                                       'unsub', u.unsub, 'ids', to_jsonb(ids), 'items', items);
    end if;
  end loop;
  return res;
end $$;

-- ---------------------------------------------------------------------------
-- 5) mail_faerdig: funktionen kvitterer for hver mail.
--    r =  1: sendt.  r = 0: prøv igen ved næste kørsel (mailtjenesten er optaget).  r = -1: afvist, prøv igen om en time.
-- ---------------------------------------------------------------------------
create or replace function public.mail_faerdig(k uuid, ids bigint[], r int) returns void
language plpgsql security definer set search_path = public as $$
declare today date := (now() at time zone 'Europe/Copenhagen')::date;
begin
  if k is null or not exists (select 1 from mail_state where id = 1 and cron_key = k) then
    raise exception 'forkert nøgle' using errcode = '42501';
  end if;
  if r = 1 then
    update mail_prefs p set last_sent = now(),
      friends_sent = case when exists (select 1 from mail_queue q where q.id = any(ids) and q.user_id = p.user_id and q.kind = 'friends')
                          then today else p.friends_sent end
      where p.user_id in (select q.user_id from mail_queue q where q.id = any(ids));
    update mail_queue set sent_at = now() where id = any(ids) and sent_at is null;
  else
    if r < 0 then
      update mail_prefs p set last_sent = now() where p.user_id in (select q.user_id from mail_queue q where q.id = any(ids));
    end if;
    update mail_queue set taken_at = null where id = any(ids) and sent_at is null;
  end if;
end $$;

-- ---------------------------------------------------------------------------
-- 6) mail_afmeld: linket nederst i hver mail. Nøglen i linket er tilfældig og kan ikke gættes.
--    Slår alle fire slags mails fra og tømmer det, der venter i køen. Svarer true, hvis nøglen fandtes.
-- ---------------------------------------------------------------------------
create or replace function public.mail_afmeld(u uuid) returns boolean
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  if u is null then return false; end if;
  delete from mail_queue q using mail_prefs p where p.unsub = u and q.user_id = p.user_id and q.sent_at is null;
  update mail_prefs set news = false, my_beer = false, friends = false, events = false, updated_at = now() where unsub = u;
  get diagnostics n = row_count;
  return n > 0;
end $$;

-- Hvem må kalde hvad: afmelding må alle (nøglen er adgangen), resten kun serveren.
revoke all on function public.mail_nyhed() from public, anon, authenticated;
revoke all on function public.mail_hent(uuid, int) from public, anon, authenticated;
revoke all on function public.mail_faerdig(uuid, bigint[], int) from public, anon, authenticated;
grant execute on function public.mail_hent(uuid, int) to service_role;
grant execute on function public.mail_faerdig(uuid, bigint[], int) to service_role;
grant execute on function public.mail_afmeld(uuid) to anon, authenticated, service_role;

-- ---------------------------------------------------------------------------
-- 7) Det planlagte job: hvert 10. minut kalder databasen funktionen "mails", men kun hvis der ligger noget i køen.
--    Kræver udvidelserne pg_cron og pg_net, som Supabase har. Findes de ikke (fx i en test), springes jobbet over.
-- ---------------------------------------------------------------------------
do $$
begin
  if exists (select 1 from pg_available_extensions where name = 'pg_cron')
     and exists (select 1 from pg_available_extensions where name = 'pg_net') then
    create extension if not exists pg_cron;
    create extension if not exists pg_net;
    perform cron.schedule('olrating-mails', '*/10 * * * *', $job$
      select net.http_post(
        url := 'https://bbcegrufmzgfgzxazldr.supabase.co/functions/v1/mails',
        headers := jsonb_build_object('Content-Type', 'application/json',
                                      'x-cron-key', (select cron_key::text from public.mail_state where id = 1)),
        body := '{"action":"send"}'::jsonb,
        timeout_milliseconds := 60000)
      where exists (select 1 from public.mail_queue where sent_at is null)
    $job$);
  else
    raise notice 'pg_cron eller pg_net findes ikke her. Det planlagte job er ikke oprettet.';
  end if;
end $$;
