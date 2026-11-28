# Drift

## Domæne
- **ølrating.dk** (`xn--lrating-p1a.dk`) ejes af Lucas (Punktum bruger-id LVO64-DK) og udløber 24-11-2027.
- **Forhandler: one.com** (flyttet fra Simply.com den 25-11-2026, fordi Simply-kontoen ikke kunne kobles til Lucas' login).
- Navneservere: one.com (`ns01.one.com` og `ns02.one.com`), bekræftet hos .dk den 26-11-2026 kl. 00:00.
- **Huskeliste:** Ret registrantens navn til "Lucas Valentin Ottesen" og by til "Nørresundby" hos one.com/Punktum.

### DNS hos one.com
DNS → DNS records:

| Type | Navn | Værdi |
|---|---|---|
| A | (tom) | 185.199.108.153 |
| A | (tom) | 185.199.109.153 |
| A | (tom) | 185.199.110.153 |
| A | (tom) | 185.199.111.153 |
| CNAME | www | lucas050908.github.io |

Under "Standard DNS-indstillinger" er A for domænet og A for www **slået fra**. MX er slået til.
DNSSEC er slået fra under flytningen og kan slås til hos one.com, når alt kører stabilt.

### Tjek hvor domænet peger hen
Workflowet **Tjek domæne** (`.github/workflows/domaene.yml`) kan startes under Actions på GitHub. Det viser navneserverne hos .dk, hvad forhandlerens navneservere svarer, hvad de store DNS-tjenester ser, og om https virker. Til sidst tjekker det de fire DNS-linjer, Resend skal bruge til mails (`resend._domainkey`, MX og TXT på `send`, CNAME på `rsend`), og skriver OK eller MANGLER ud for hver. 28-11 kl. 15.35 sagde Resend: DKIM (`resend._domainkey`) er godkendt, de tre andre mangler.

## GitHub Pages
- Settings → Pages → Deploy from a branch → `main` / root.
- Filen `CNAME` indeholder `xn--lrating-p1a.dk`. Det kobler domænet på.
- **HTTPS:** Når certifikatet er udstedt, skal der være hak i **Enforce HTTPS** under Settings → Pages.
- Adresser i `index.html`, `robots.txt`, `sitemap.xml`, `404.html`, Android (`MainActivity`, `TopWidget`) og desktop (`main.js`) peger på `https://xn--lrating-p1a.dk/`.

## Fælles database (Supabase)
- **Konto:** Lucas, logger ind med GitHub. Organisation "olrating", gratis plan, projekt i EU.
- **Opsætning (gjort 25-11-2026 kl. 22:49–22:50):**
  1. SQL Editor → New query → indsæt `supabase/schema.sql` → Run.
  2. Authentication → Sign In / Providers → slå **Allow anonymous sign-ins** til.
- `supabase/002-slet-billeder.sql` er kørt (bekræftet af testen mod den rigtige database den 26-11-2026: billedet forsvinder, når en øl slettes).
- `supabase/003-konto-mails-enig.sql` (stemmer i "Enig eller uenig?", konto og mailvalg) er kørt (testen mod den rigtige database siger "kørt" 28-11-2026).
- **Mangler at blive kørt:** `supabase/004-mails.sql` (udsendelse af mails, se `docs/KONTO.md`) og `supabase/006-graenser.sql` (grænser mod spam).
- **Grænser mod spam:** `supabase/006-graenser.sql` gør, at én bruger højst kan oprette 40 øl i timen og 150 i døgnet, og 60 bedømmelser i timen og 300 i døgnet. Rettelser tæller ikke. Den anbefales, fordi alle kan skrive i databasen uden at logge ind, og siden henter alle øl. Kør den: Supabase → SQL Editor → indsæt hele filen → Run. Den kan køres flere gange. Testen mod den rigtige database skriver bagefter "supabase/006 (grænser mod spam): kørt".
- **Besøgstæller:** `supabase/005-besoeg.sql` slår tælleren til. Den er kørt (27-11-2026). Den kan køres igen uden skade: Supabase → SQL Editor → indsæt hele filen → Run.
- **Konto og mails:** Kræver en mailtjeneste (Resend), DNS-linjer hos one.com, to mailskabeloner og en funktion i Supabase. Hele opsætningen står trin for trin i `docs/KONTO.md`. Nøglen fra Resend må kun stå hos Resend og i Supabase.
- **Tjek at det virker:** Åbn ølrating.dk → Min profil. Nederst skal der stå "● Forbundet". Tilføj en øl på én enhed, og se den dukke op på en anden inden for et halvt minut.
- **Max rows (Supabase → Project Settings → Data API):** Skal stå på 1000 (det er standard) eller mere. Siden henter øl og bedømmelser 1000 ad gangen og stopper, når et svar har færre end 1000. Sættes tallet lavere, tror siden, at den har fået det hele.
- **Moderation:** Alle kan tilføje øl. Brugere kan trykke "Anmeld" på andres øl og bedømmelser. Det sender en mail til fejlrapport-adressen med et id. Upassende indhold slettes i Supabase → Table Editor (`beers`, `reviews`, søg på id) eller Storage (`billeder`).
- Gratis-planen holder til 500 MB database og 1 GB billeder. Et projekt uden aktivitet i 7 dage bliver sat på pause og skal vækkes i dashboardet.

## Android-signering
For at opdateringer kan installeres oven i den gamle app, skal appen signeres med samme nøgle hver gang. Læg disse under Settings → Secrets and variables → Actions:
- `ANDROID_KEYSTORE_BASE64`: keystore-filen, base64-kodet
- `ANDROID_KEYSTORE_PASSWORD`: adgangskoden
- **Nøglen må aldrig committes.** `.gitignore` udelukker `*.keystore` og `*.jks`.

## Prøv de nye widgets på telefonen (2 minutter)
1. Afinstallér den gamle app. Hent `olrating.apk` fra GitHub-udgivelsen `android-app`, og installér den.
2. Åbn appen én gang, og vent til forsiden er vist. Så får widgets data og billeder.
3. Hold fingeren på hjemmeskærmen → Widgets → ølrating. Tilføj **Ugens øl med billede** og **Siden i tal**.
4. Tjek: Ugens øl viser et billede, hvis øllen har et. Siden i tal viser øl, bedømmelser og smagere. Besøg viser tallet fra databasen (`supabase/005-besoeg.sql` er kørt). En streg betyder, at appen ikke har hentet tallet endnu: åbn appen.
5. Tryk på hver widget. Ugens øl åbner øllen, og Siden i tal åbner Om.
6. Virker noget ikke, så tag et skærmbillede og send det. Skriv, hvilken telefon det er.

## Microsoft Store
Se [STORE.md](STORE.md) for trin for trin, tekster og skærmbilleder.
- Lucas har en Microsoft-udviklerkonto.
- **Det mangler:** Reservér navnet i Partner Center, og send de tre værdier fra *Produktidentitet* til udvikleren:
  - `Package/Identity/Name`
  - `Package/Identity/Publisher` (CN=…)
  - `PublisherDisplayName`
- **Derefter:** Desktop-workflowet bygger en `.appx`/`.msix`. Lucas uploader pakken i Partner Center og udfylder aldersvurdering (alkohol, 18+), privatlivspolitik (`https://ølrating.dk/#privatliv`) og skærmbilleder.

## Historik for hosting
- 25-11-2026 kl. 20:32: Siden kørte midlertidigt på `lucas050908.github.io/-lrating.dk`.
- 25-11-2026 ca. 22:00: Domænet blev flyttet til one.com. DNS virkede ca. kl. 22:03, og `CNAME` blev tilføjet kl. 22:04.

## Støtte og kontakter
- **Fejlrapporter:** andersenlucas84@gmail.com
- **one.com:** chat i kontrolpanelet, døgnåben
- **Simply.com:** ticket #862316 (gammel, kan lukkes)

## Besøgstælleren før og efter 005
005 blev kørt fredag 27-11-2026 kl. 14.50.
Før `supabase/005-besoeg.sql` er kørt, prøver hver enhed højst én gang i timen (husket i `localStorage` under `olrating-vis404`). Efter kørslen begynder tællingen derfor senest en time efter på enheder, der har prøvet før. Vil du se det med det samme på din egen telefon, så slet sidens data eller vent en time.

## Test på GitHub: tjek hvert job
Jobbene for Safaris motor (WebKit) og Firefox må fejle uden at stoppe resten (`continue-on-error`). Så kan hele kørslen stå som grøn, selv om et af dem er rødt. Kig derfor på hvert job:
`gh run view <id> --json jobs -q '.jobs[]|"\(.name) \(.conclusion)"'`
