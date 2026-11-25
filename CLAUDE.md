# Regler for arbejde i dette repo

- **Dokumentation hver gang:** Hver ændring opdaterer `CHANGELOG.md` (nyeste øverst, med dato og tidsrum) og det relevante dokument i `docs/` (`FUNKTIONER.md`, `TEKNIK.md`, `DRIFT.md`) i samme commit.
- **Service worker:** Hæv `const V='olrating-vNN'` i `sw.js` ved hver ændring af siden.
- **Ingen hemmeligheder i repoet:** Det gælder keystore-filer, adgangskoder, Supabase secret/service_role-nøgler og tokens. Den offentlige Supabase-nøgle (`sb_publishable_…`) må gerne stå i koden.
- **Download-links** skal pege på faste tags (`android-app`, `desktop-app`), ikke `latest`.
- **Test før push:** Kør siden lokalt (`python3 -m http.server`) og tjek på desktop og mobil (390 px), at der ikke er JS-fejl og ingen vandret scroll.
- **Sprog:** Brugerflader og dokumentation skrives på dansk.
- **Alkohol:** Funktioner om drikkeri skal være ansvarlige. Henvis til Sundhedsstyrelsens anbefalinger og Alkolinjen, og belønnér variation frem for mængde.
