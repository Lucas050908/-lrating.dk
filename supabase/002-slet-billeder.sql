-- ølrating.dk – tilføjelse 002: gør det muligt at slette sine egne billeder fra lageret.
-- Kør i Supabase → SQL Editor → New query → Run. Er allerede med i schema.sql for nye installationer.

drop policy if exists "egne billeder kan ses" on storage.objects;
create policy "egne billeder kan ses" on storage.objects for select to authenticated
  using (bucket_id = 'billeder' and (storage.foldername(name))[1] = auth.uid()::text);
