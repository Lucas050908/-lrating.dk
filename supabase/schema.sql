-- ølrating.dk – fælles database (Supabase)
-- Kør hele filen i Supabase → SQL Editor → New query → Run.
-- Alle kan læse. Man skal være logget ind (anonymt, automatisk) for at skrive,
-- og man kan kun rette/slette det, man selv har lavet.

create table if not exists public.beers (
  id text primary key check (length(id) <= 40),
  owner uuid not null default auth.uid(),
  name text not null check (length(name) between 1 and 120),
  brewery text check (length(brewery) <= 120),
  data jsonb not null default '{}'::jsonb check (pg_column_size(data) < 20000),
  img text check (length(img) <= 400),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.reviews (
  id text primary key check (length(id) <= 40),
  beer text not null references public.beers(id) on delete cascade,
  owner uuid not null default auth.uid(),
  who text not null check (length(who) between 1 and 40),
  data jsonb not null default '{}'::jsonb check (pg_column_size(data) < 20000),
  img text check (length(img) <= 400),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists reviews_beer_idx on public.reviews(beer);

create table if not exists public.tours (
  id text primary key check (length(id) <= 40),
  owner uuid not null default auth.uid(),
  data jsonb not null default '{}'::jsonb check (pg_column_size(data) < 20000),
  updated_at timestamptz not null default now()
);

create table if not exists public.tour_members (
  tour text not null references public.tours(id) on delete cascade,
  name text not null check (length(name) between 1 and 40),
  owner uuid not null default auth.uid(),
  created_at timestamptz not null default now(),
  primary key (tour, name)
);

create table if not exists public.tastings (
  id text primary key check (length(id) <= 40),
  owner uuid not null default auth.uid(),
  data jsonb not null default '{}'::jsonb check (pg_column_size(data) < 20000),
  updated_at timestamptz not null default now()
);

create table if not exists public.tasting_votes (
  tasting text not null references public.tastings(id) on delete cascade,
  who text not null check (length(who) between 1 and 40),
  owner uuid not null default auth.uid(),
  data jsonb not null default '{}'::jsonb check (pg_column_size(data) < 8000),
  updated_at timestamptz not null default now(),
  primary key (tasting, who)
);

-- Sikkerhed (Row Level Security)
do $$
declare t text;
begin
  foreach t in array array['beers','reviews','tours','tour_members','tastings','tasting_votes'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists "alle kan laese" on public.%I', t);
    execute format('drop policy if exists "egne kan oprettes" on public.%I', t);
    execute format('drop policy if exists "egne kan rettes" on public.%I', t);
    execute format('drop policy if exists "egne kan slettes" on public.%I', t);
    execute format('create policy "alle kan laese" on public.%I for select to anon, authenticated using (true)', t);
    execute format('create policy "egne kan oprettes" on public.%I for insert to authenticated with check (owner = auth.uid())', t);
    execute format('create policy "egne kan rettes" on public.%I for update to authenticated using (owner = auth.uid()) with check (owner = auth.uid())', t);
    execute format('create policy "egne kan slettes" on public.%I for delete to authenticated using (owner = auth.uid())', t);
  end loop;
end $$;

-- Værten af en byttur/smagning må også fjerne andres tilmeldinger
drop policy if exists "vaert kan slette medlemmer" on public.tour_members;
create policy "vaert kan slette medlemmer" on public.tour_members for delete to authenticated
  using (exists (select 1 from public.tours t where t.id = tour and t.owner = auth.uid()));

-- Billeder
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('billeder', 'billeder', true, 2097152, array['image/jpeg','image/png','image/webp'])
on conflict (id) do update set public = true, file_size_limit = 2097152, allowed_mime_types = array['image/jpeg','image/png','image/webp'];

drop policy if exists "billeder kan uploades" on storage.objects;
create policy "billeder kan uploades" on storage.objects for insert to authenticated
  with check (bucket_id = 'billeder' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "egne billeder kan slettes" on storage.objects;
create policy "egne billeder kan slettes" on storage.objects for delete to authenticated
  using (bucket_id = 'billeder' and (storage.foldername(name))[1] = auth.uid()::text);

drop policy if exists "egne billeder kan ses" on storage.objects;
create policy "egne billeder kan ses" on storage.objects for select to authenticated
  using (bucket_id = 'billeder' and (storage.foldername(name))[1] = auth.uid()::text);

-- Live-opdateringer (fx når nogen melder sig til en byttur)
do $$ begin
  begin alter publication supabase_realtime add table public.beers, public.reviews, public.tour_members, public.tasting_votes;
  exception when others then null; end;
end $$;
