# Konto og mails – sådan slås det til

Koden er færdig, men den er **skjult på siden**, indtil tingene her er sat op. Den er testet mod en efterligning af databasen og mailtjenesten, ikke mod de rigtige. Derfor er sidste punkt i hvert trin at prøve det. Det er ting, kun ejerne kan gøre,
fordi de kræver login hos Supabase, one.com og en mailtjeneste.

Der er to trin. **Trin 1** giver login med kode på mail. **Trin 2** giver mails om opdateringer. Trin 2 kræver trin 1.

> **Vigtigt om nøgler:** En nøgle fra mailtjenesten er en adgangskode. Den må kun stå hos Resend og hos Supabase.
> Send den aldrig i en chat, og læg den aldrig på GitHub.

## Det skal du bruge
- Login til [Supabase](https://supabase.com/dashboard) (projektet til ølrating.dk)
- Login til one.com (for at tilføje DNS-linjer)
- En gratis konto hos [Resend](https://resend.com). Gratis er nok til 100 mails om dagen og 3.000 om måneden.

---

## Trin 1: Login med kode på mail

> **Genvej, hvis du bare vil se det virke først:** Lav 1.1, 1.4 og 1.5, og spring 1.2 og 1.3 over. Så sender Supabase selv koden,
> men kun til den mailadresse, du selv bruger hos Supabase (den fra din GitHub), og højst 2 mails i timen.
> Det er nok til at prøve 1.6. Resend (1.2 og 1.3) skal til, før andre end dig kan få en kode.

### 1.1 Kør database-filen 003 (hvis du ikke allerede har gjort det)
1. Åbn filen: <https://raw.githubusercontent.com/Lucas050908/-lrating.dk/main/supabase/003-konto-mails-enig.sql>
2. Markér alt, og kopiér.
3. Supabase → **SQL Editor** → sæt ind → **Run**. Kommer der en advarsel om "Potential issues", så tryk Run alligevel.

Filen er sidst ændret den 26-11-2026 kl. 13:01. Har du kørt den før det, så kør den igen. Den kan køres flere gange uden at gøre skade.

### 1.2 Domænet hos Resend og DNS-linjerne
Kontoen hos Resend er oprettet, og domænet `xn--lrating-p1a.dk` blev oprettet dér den 26-11-2026 i region EU (Irland).
Resend tog imod domænet med ø uden problemer.

Tilbage er DNS:
1. Resend → **Domains** → klik på domænet. Der står 4 DNS-linjer (1 MX, 2 TXT og 1 CNAME).
2. one.com → **DNS → DNS records**. Opret hver linje præcis, som Resend viser den (type, navn og værdi).
   Navnene er `resend._domainkey`, `send` (to linjer) og `rsend`. De rører ikke ved selve siden.
3. Tilbage i Resend: tryk **Verify**. Det kan tage fra et par minutter til nogle timer, før den bliver grøn.

### 1.3 Kobl Resend til Supabase
1. Resend → **Settings → Integrations → Supabase → Connect**.
2. Vælg projektet til ølrating.dk og domænet. Afsender: navn `ølrating.dk`, adresse `hej@xn--lrating-p1a.dk`.
3. Resend udfylder selv mail-indstillingerne i Supabase. Du skal ikke kopiere nogen nøgle.

Tjek bagefter i Supabase → **Authentication → Emails → SMTP Settings**, at "Enable Custom SMTP" er slået til.

<details><summary>Hvis koblingen ikke virker: udfyld selv</summary>

Resend → **API Keys → Create API Key** (Sending access). Kopiér nøglen direkte over i Supabase → Authentication → Emails → SMTP Settings:

| Felt | Værdi |
|---|---|
| Sender email | `hej@xn--lrating-p1a.dk` |
| Sender name | `ølrating.dk` |
| Host | `smtp.resend.com` |
| Port | `465` |
| Username | `resend` |
| Password | nøglen fra Resend |
</details>

### 1.4 Få mailen til at vise en kode
Supabase → **Authentication → Emails → Templates**. Der skal rettes to skabeloner: **Change Email Address** og **Magic Link**.

For hver af de to:
1. Emne (Subject): `Din kode til ølrating.dk`
2. Indhold (Body): slet det, der står, og sæt indholdet af denne fil ind:
   <https://raw.githubusercontent.com/Lucas050908/-lrating.dk/main/supabase/mail-skabelon.html>
3. Gem.

Det vigtige er, at der står `{{ .Token }}` i indholdet. Det er det sted, koden bliver sat ind.

### 1.5 Tre indstillinger i Supabase
Supabase → **Authentication → Sign In / Providers**:
1. **Allow manual linking**: slå til. (Det er det, der lader en enhed uden login blive til en konto.)
2. Under **Email**: tjek at **Email OTP Length** er `6`. Siden har et felt til præcis 6 tal.
3. **Allow anonymous sign-ins** skal stadig være slået til (det er den i forvejen).

### 1.6 Prøv det
1. Åbn <https://ølrating.dk/#konto-test> på din telefon. Det slår konto til på netop den enhed.
2. Gå til **Min profil**. Der er nu en boks, der hedder **Konto**.
3. Skriv din mail, og tryk på knappen. Der skal komme en mail med 6 tal inden for et minut.
4. Skriv tallene. Der skal nu stå "Logget ind som …".
5. Prøv også på en anden enhed med samme mail. Så skal øllene fra begge enheder kunne rettes fra begge.

**Virker det:** skriv "login virker" til Claude. Så bliver konto slået til for alle (`KONTO=true` i `index.html`).

**Virker det ikke:**
| Det sker | Prøv |
|---|---|
| Der kommer ingen mail | Resend → **Emails**: står mailen der? Hvis nej: tjek 1.3. Hvis ja med fejl: tjek at domænet er grønt (1.2). |
| Mailen har et link i stedet for en kode | Skabelonen mangler `{{ .Token }}` (1.4). |
| Koden har 8 tal | Email OTP Length skal være 6 (1.5). |
| "Koden passer ikke", selvom den er rigtig | Skriv det til Claude. Login er kun prøvet mod en efterligning af Supabase, så her kan der være noget, der skal rettes i koden. |
| "Der er sendt for mange mails" | Supabase → Authentication → **Rate Limits** → hæv "Rate limit for sending emails". |

---

## Trin 2: Mails om opdateringer

En bruger med konto kan slå fire slags mails til: nyheder om siden, når nogen bedømmer en øl man har tilføjet,
når en man følger bedømmer en øl, og når nogen melder sig til ens byttur eller stemmer i ens smagning.

### 2.1 Opret funktionen
1. Åbn filen: <https://raw.githubusercontent.com/Lucas050908/-lrating.dk/main/supabase/functions/mails/index.ts>. Markér alt, og kopiér.
2. Supabase → **Edge Functions → Deploy a new function → Via Editor**.
3. Navn: `mails` (præcis sådan, med små bogstaver).
4. Slet det, der står i editoren, sæt indholdet ind, og tryk **Deploy**.
5. Åbn funktionen → fanen **Details** → slå **Verify JWT with legacy secret** **fra** → gem.
   (Tjek den igen, hvis du senere retter funktionen. Nogle har oplevet, at den slår sig til igen.)

### 2.2 Giv funktionen en nøgle til Resend
1. Resend → **API Keys → Create API Key**. Navn: `mails`. Permission: **Sending access**.
2. Kopiér nøglen. Supabase → **Edge Functions → Secrets** → ny hemmelighed:
   - Navn: `RESEND_API_KEY`
   - Værdi: nøglen
3. Gem. Nøglen skal ikke gemmes andre steder.

To valgfri hemmeligheder samme sted:
- `MAIL_REPLY_TO`: en mailadresse, som svar på mailene skal havne i. Uden den ender svar hos `hej@…`, som ingen læser, medmindre I laver den postkasse hos one.com.
- `MAIL_FROM`: hvis mails skal komme fra en anden adresse, fx `ølrating.dk <nyt@xn--lrating-p1a.dk>`.

### 2.3 Kør database-filen 004
1. Åbn filen: <https://raw.githubusercontent.com/Lucas050908/-lrating.dk/main/supabase/004-mails.sql>
2. Markér alt, kopiér, sæt ind i Supabase → **SQL Editor** → **Run**.

Filen sætter et job op, så databasen selv kalder funktionen hvert 10. minut, men kun når der er noget at sende.

### 2.4 Prøv det
1. Log ind på din konto på siden, og sæt flueben ved **Nyheder om siden**.
2. Supabase → **Table Editor → mail_news → Insert row**. Udfyld `subject_da` (emne) og `body_da` (tekst). Gem.
3. Læs rækken igennem. Sæt så feltet **send** til `TRUE` (flueben), og gem.
4. Inden for 10 minutter skal mailen komme. Nederst i mailen er der et link til at afmelde.

Kommer den ikke: Supabase → Edge Functions → mails → **Logs**, og Resend → **Emails**.

---

## Sådan sender I en nyhed senere
Det er det samme som 2.4: Ny række i `mail_news`, læs den igennem, og sæt `send` til `TRUE`.

- `subject_en` og `body_en` er den engelske udgave. Er de tomme, får alle den danske.
- Teksten er almindelig tekst. En tom linje giver et nyt afsnit. Links, der starter med `https://`, bliver klikbare.
- **Den kan ikke fortrydes,** når fluebenet er sat. Den går til alle, der har slået nyheder til.

## Regler, som systemet selv holder
- En bruger får højst **én mail i timen**. Sker der flere ting, bliver de samlet i én mail.
- "En, jeg følger, har bedømt en øl" kommer højst **én gang om dagen**.
- Slår brugeren en slags mail fra, bliver det, der venter, slettet.
- Hver mail har et afmeld-link. Det virker uden login. Mailprogrammer som Gmail kan også vise deres egen afmeld-knap.
- Ingen får mail uden selv at have slået det til.

## Hvor ligger hvad
| Hvad | Hvor |
|---|---|
| Mailadresser og valg | Supabase (EU), tabellen `mail_prefs` og Supabases egne login-tabeller |
| Navn, ønskeliste og følger på kontoen | Supabase, tabellen `konto_data` (kun kontoen selv kan læse sin række) |
| Køen med mails | Supabase, tabellen `mail_queue` (ryddes selv op) |
| Udsendelsen | Supabase Edge Function `mails` (`supabase/functions/mails/index.ts`) |
| Selve afsendelsen | Resend |
| Teknisk forklaring | `docs/TEKNIK.md`, afsnittet Konto og afsnittet Mails |
