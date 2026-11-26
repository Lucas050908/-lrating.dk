# Regler for arbejde i dette repo

- **Dokumentation hver gang:** Hver ændring opdaterer `CHANGELOG.md` (nyeste øverst, med dato og tidsrum) og det relevante dokument i `docs/` (`FUNKTIONER.md`, `TEKNIK.md`, `DRIFT.md`) i samme commit.
- **Service worker:** Hæv `const V='olrating-vNN'` i `sw.js` ved hver ændring af siden.
- **Ingen hemmeligheder i repoet:** Det gælder keystore-filer, adgangskoder, Supabase secret/service_role-nøgler og tokens. Den offentlige Supabase-nøgle (`sb_publishable_…`) må gerne stå i koden.
- **Download-links** skal pege på faste tags (`android-app`, `desktop-app`), ikke `latest`.
- **Test før push:** Kør siden lokalt (`python3 -m http.server 8811 &`) og derefter `python3 tests/test_site.py`, `python3 tests/test_sync.py` og `python3 tests/test_en.py`. Alle tre skal ende med ALL PASS. Nye funktioner får et tjek i en af dem. Ændres noget i `supabase/`, køres også `node tests/test_sql.js` (kræver `npm install --no-save @electric-sql/pglite`). Skriv `[database-test]` i commit-beskeden, når noget ved databasen er ændret, så testen mod den rigtige database kører på GitHub.
- **Commits:** Brug navnet `Lucas050908` og GitHubs noreply-adresse `Lucas050908@users.noreply.github.com`. Skriv ikke private mailadresser i kommandoer eller scripts.
- **Sprog:** Brugerflader skrives på dansk i `index.html`, og dokumentation skrives på dansk. Hver ny eller ændret synlig tekst skal også have en engelsk oversættelse i `js/en.js`. `tests/test_en.py` fejler, hvis en tekst mangler.
- **Alkohol:** Funktioner om drikkeri skal være ansvarlige. Henvis til Sundhedsstyrelsens anbefalinger og Alkolinjen, og belønnér variation frem for mængde.
