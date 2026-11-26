-- ølrating.dk – tilføjelse 003: enig/uenig på bedømmelser, rigtig konto, mailvalg og mails om opdateringer.
-- Kør hele filen i Supabase → SQL Editor → New query → Run. Den kan køres flere gange uden at gøre skade.

-- ---------------------------------------------------------------------------
-- 1) Enig / uenig på andres bedømmelser (siden "Enig eller uenig?")
-- ---------------------------------------------------------------------------
create table if not exists public.review_votes (
  review text not null references public.reviews(id) on delete cascade,
  owner uuid not null default auth.uid(),
  v smallint not null check (v in (1, -1)),
  updated_at timestamptz not null default now(),
  primary key (review, owner)
);
alter table public.review_votes enable row level security;

-- Man kan kun se sine egne stemmer. Alle kan se, hvor mange der er enige og uenige (viewet nedenfor).
drop policy if exists "egne kan laeses" on public.review_votes;
create policy "egne kan laeses" on public.review_votes for select to authenticated using (owner = auth.uid());
-- Man kan ikke stemme på sin egen bedømmelse.
drop policy if exists "egne kan oprettes" on public.review_votes;
create policy "egne kan oprettes" on public.review_votes for insert to authenticated
  with check (owner = auth.uid() and not exists (select 1 from public.reviews r where r.id = review and r.owner = auth.uid()));
drop policy if exists "egne kan rettes" on public.review_votes;
create policy "egne kan rettes" on public.review_votes for update to authenticated using (owner = auth.uid()) with check (owner = auth.uid());
drop policy if exists "egne kan slettes" on public.review_votes;
create policy "egne kan slettes" on public.review_votes for delete to authenticated using (owner = auth.uid());

create or replace view public.review_vote_counts as
  select review,
         count(*) filter (where v = 1)::int as enig,
         count(*) filter (where v = -1)::int as uenig
  from public.review_votes group by review;
grant select on public.review_vote_counts to anon, authenticated;

-- ---------------------------------------------------------------------------
-- 2) Konto: flyt enhedens øl og bedømmelser over på kontoen, når man logger ind
-- ---------------------------------------------------------------------------
-- Den anonyme bruger på enheden henter et flyttebevis (konto_flyt_start), logger ind med koden fra mailen
-- og afleverer beviset som den rigtige bruger (konto_flyt_slut). Så skifter rækkerne ejer.
create table if not exists public.konto_flyt (
  token uuid primary key default gen_random_uuid(),
  fra uuid not null,
  created_at timestamptz not null default now()
);
alter table public.konto_flyt enable row level security;   -- ingen regler: kun funktionerne herunder kan bruge tabellen

create or replace function public.konto_flyt_start() returns uuid
language plpgsql security definer set search_path = public as $$
declare t uuid;
begin
  if auth.uid() is null or coalesce((auth.jwt()->>'is_anonymous')::boolean, false) is not true then
    raise exception 'kun anonyme brugere kan flytte data';
  end if;
  delete from konto_flyt where fra = auth.uid() or created_at < now() - interval '1 hour';
  insert into konto_flyt (fra) values (auth.uid()) returning token into t;
  return t;
end $$;

create or replace function public.konto_flyt_slut(t uuid) returns integer
language plpgsql security definer set search_path = public as $$
declare f uuid; n integer := 0; c integer;
begin
  if auth.uid() is null or coalesce((auth.jwt()->>'is_anonymous')::boolean, false) then
    raise exception 'log ind foerst';
  end if;
  delete from konto_flyt where token = t and created_at > now() - interval '15 minutes' returning fra into f;
  if f is null then raise exception 'ukendt eller udloebet flyttebevis'; end if;
  if f = auth.uid() then return 0; end if;
  update beers set owner = auth.uid() where owner = f;          get diagnostics c = row_count; n := n + c;
  update reviews set owner = auth.uid() where owner = f;        get diagnostics c = row_count; n := n + c;
  update tours set owner = auth.uid() where owner = f;          get diagnostics c = row_count; n := n + c;
  update tastings set owner = auth.uid() where owner = f;       get diagnostics c = row_count; n := n + c;
  update tour_members set owner = auth.uid() where owner = f;
  update tasting_votes set owner = auth.uid() where owner = f;
  -- stemmer: har kontoen allerede stemt på samme bedømmelse, vinder kontoens stemme
  delete from review_votes a where a.owner = f and exists (select 1 from review_votes b where b.review = a.review and b.owner = auth.uid());
  update review_votes set owner = auth.uid() where owner = f;
  -- man må ikke have en stemme på sin egen bedømmelse
  delete from review_votes a where a.owner = auth.uid() and exists (select 1 from reviews r where r.id = a.review and r.owner = auth.uid());
  delete from auth.users where id = f and is_anonymous;          -- den anonyme bruger er ikke længere i brug
  return n;
end $$;

-- Slet sin egen konto (login og mailvalg). Øl og bedømmelser bliver stående, men kan slettes først fra Min profil.
create or replace function public.konto_slet() returns void
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then raise exception 'ikke logget ind'; end if;
  delete from auth.users where id = auth.uid();
end $$;

revoke all on function public.konto_flyt_start() from public, anon;
revoke all on function public.konto_flyt_slut(uuid) from public, anon;
revoke all on function public.konto_slet() from public, anon;
grant execute on function public.konto_flyt_start() to authenticated;
grant execute on function public.konto_flyt_slut(uuid) to authenticated;
grant execute on function public.konto_slet() to authenticated;

-- ---------------------------------------------------------------------------
-- 2b) Personlige ting, der følger kontoen: navn, ønskeliste og hvem man følger.
--     Én række pr. konto, som kun kontoen selv kan læse og rette. Slettes sammen med kontoen.
-- ---------------------------------------------------------------------------
create table if not exists public.konto_data (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  data jsonb not null default '{}'::jsonb check (jsonb_typeof(data) = 'object' and length(data::text) < 60000),
  updated_at timestamptz not null default now()
);
alter table public.konto_data enable row level security;
drop policy if exists "egne kan laeses" on public.konto_data;
create policy "egne kan laeses" on public.konto_data for select to authenticated using (user_id = auth.uid());
drop policy if exists "egne kan oprettes" on public.konto_data;
create policy "egne kan oprettes" on public.konto_data for insert to authenticated
  with check (user_id = auth.uid() and coalesce((auth.jwt()->>'is_anonymous')::boolean, false) is not true);
drop policy if exists "egne kan rettes" on public.konto_data;
create policy "egne kan rettes" on public.konto_data for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists "egne kan slettes" on public.konto_data;
create policy "egne kan slettes" on public.konto_data for delete to authenticated using (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- 3) Mailvalg på kontoen
-- ---------------------------------------------------------------------------
create table if not exists public.mail_prefs (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  news boolean not null default false,       -- nyheder om siden
  my_beer boolean not null default false,    -- nogen bedømmer en øl, jeg har tilføjet
  friends boolean not null default false,    -- en, jeg følger, bedømmer en øl (højst én mail om dagen)
  events boolean not null default false,     -- nogen melder sig til min byttur eller stemmer i min smagning
  name text check (length(name) <= 40),
  lang text not null default 'da' check (lang in ('da', 'en')),
  follows text[] not null default '{}' check (cardinality(follows) <= 200),
  unsub uuid not null default gen_random_uuid(),   -- bruges i afmeld-linket nederst i hver mail
  last_sent timestamptz,
  friends_sent date,
  updated_at timestamptz not null default now()
);
alter table public.mail_prefs enable row level security;
-- Kun rigtige konti (ikke anonyme) kan have mailvalg, og man kan kun se og rette sine egne.
drop policy if exists "egne kan laeses" on public.mail_prefs;
create policy "egne kan laeses" on public.mail_prefs for select to authenticated using (user_id = auth.uid());
drop policy if exists "egne kan oprettes" on public.mail_prefs;
create policy "egne kan oprettes" on public.mail_prefs for insert to authenticated
  with check (user_id = auth.uid() and coalesce((auth.jwt()->>'is_anonymous')::boolean, false) is not true);
drop policy if exists "egne kan rettes" on public.mail_prefs;
create policy "egne kan rettes" on public.mail_prefs for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists "egne kan slettes" on public.mail_prefs;
create policy "egne kan slettes" on public.mail_prefs for delete to authenticated using (user_id = auth.uid());
-- Brugeren må kun røre sine valg, ikke afmeld-nøglen eller tidspunkterne for sidste mail.
revoke insert, update on public.mail_prefs from authenticated;
grant insert (news, my_beer, friends, events, name, lang, follows, updated_at) on public.mail_prefs to authenticated;
grant update (news, my_beer, friends, events, name, lang, follows, updated_at) on public.mail_prefs to authenticated;

-- ---------------------------------------------------------------------------
-- 4) Kø med mails, der skal sendes. Funktionen "mails" (supabase/functions/mails) tømmer køen.
-- ---------------------------------------------------------------------------
create table if not exists public.mail_queue (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  kind text not null check (kind in ('my_beer', 'friends', 'events')),
  data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  sent_at timestamptz
);
create index if not exists mail_queue_unsent_idx on public.mail_queue (user_id) where sent_at is null;
alter table public.mail_queue enable row level security;   -- ingen regler: kun serveren kan læse køen

-- Nyheder om siden: ejerne skriver en række her (Table Editor), så sendes den til alle, der har slået nyheder til.
create table if not exists public.mail_news (
  id bigint generated always as identity primary key,
  subject_da text not null check (length(subject_da) between 3 and 120),
  body_da text not null check (length(body_da) between 10 and 4000),
  subject_en text check (length(subject_en) <= 120),
  body_en text check (length(body_en) <= 4000),
  created_at timestamptz not null default now(),
  sent_at timestamptz
);
alter table public.mail_news enable row level security;    -- ingen regler: kun ejerne (i Supabase) og serveren

-- Loft: højst 200 ventende rækker pr. bruger, så ingen kan fylde en andens kø (og indbakke) op.
create or replace function public.mail_plads(u uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select (select count(*) from mail_queue q where q.user_id = u and q.sent_at is null) < 200
$$;
revoke all on function public.mail_plads(uuid) from public, anon, authenticated;

-- Ny bedømmelse: besked til den, der har tilføjet øllen, og til dem, der følger smageren.
create or replace function public.mail_ny_bedoemmelse() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; d jsonb;
begin
  select id, name, owner into b from beers where id = new.beer;
  if b.id is null then return new; end if;
  d := jsonb_build_object('who', new.who, 'beer', b.name, 'id', b.id, 's', new.data->'s');
  if b.owner <> new.owner then
    insert into mail_queue (user_id, kind, data)
      select p.user_id, 'my_beer', d from mail_prefs p where p.user_id = b.owner and p.my_beer and mail_plads(p.user_id);
  end if;
  insert into mail_queue (user_id, kind, data)
    select p.user_id, 'friends', d from mail_prefs p
    where p.friends and p.user_id <> new.owner and mail_plads(p.user_id)
      and exists (select 1 from unnest(p.follows) f where lower(f) = lower(new.who));
  return new;
exception when others then return new;   -- en fejl i mail-køen må aldrig forhindre en bedømmelse i at blive gemt
end $$;
drop trigger if exists mail_ny_bedoemmelse on public.reviews;
create trigger mail_ny_bedoemmelse after insert on public.reviews for each row execute function public.mail_ny_bedoemmelse();

-- Ny tilmelding til en byttur: besked til værten.
create or replace function public.mail_ny_tilmelding() returns trigger
language plpgsql security definer set search_path = public as $$
declare t record;
begin
  select id, owner, data->>'name' as name into t from tours where id = new.tour;
  if t.id is not null and t.owner <> new.owner then
    insert into mail_queue (user_id, kind, data)
      select p.user_id, 'events', jsonb_build_object('type', 'tour', 'who', new.name, 'name', t.name, 'id', t.id)
      from mail_prefs p where p.user_id = t.owner and p.events and mail_plads(p.user_id);
  end if;
  return new;
exception when others then return new;
end $$;
drop trigger if exists mail_ny_tilmelding on public.tour_members;
create trigger mail_ny_tilmelding after insert on public.tour_members for each row execute function public.mail_ny_tilmelding();

-- Ny stemme i en smagning: besked til værten.
create or replace function public.mail_ny_stemme() returns trigger
language plpgsql security definer set search_path = public as $$
declare t record;
begin
  select id, owner, data->>'name' as name into t from tastings where id = new.tasting;
  if t.id is not null and t.owner <> new.owner then
    insert into mail_queue (user_id, kind, data)
      select p.user_id, 'events', jsonb_build_object('type', 'tasting', 'who', new.who, 'name', t.name, 'id', t.id)
      from mail_prefs p where p.user_id = t.owner and p.events and mail_plads(p.user_id);
  end if;
  return new;
exception when others then return new;
end $$;
drop trigger if exists mail_ny_stemme on public.tasting_votes;
create trigger mail_ny_stemme after insert on public.tasting_votes for each row execute function public.mail_ny_stemme();

-- Triggerfunktionerne skal ikke kunne kaldes udefra.
revoke all on function public.mail_ny_bedoemmelse() from public, anon, authenticated;
revoke all on function public.mail_ny_tilmelding() from public, anon, authenticated;
revoke all on function public.mail_ny_stemme() from public, anon, authenticated;
