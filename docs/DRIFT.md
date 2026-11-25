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
Workflowet **Tjek domæne** (`.github/workflows/domaene.yml`) kan startes under Actions på GitHub. Det viser navneserverne hos .dk, hvad forhandlerens navneservere svarer, hvad de store DNS-tjenester ser, og om https virker.

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
- **Mangler at blive kørt:** `supabase/002-slet-billeder.sql` (SQL Editor → New query → Run). Uden den bliver billedet liggende i lageret, når en øl slettes.
- **Tjek at det virker:** Åbn ølrating.dk → Min profil. Nederst skal der stå "● Forbundet". Tilføj en øl på én enhed, og se den dukke op på en anden inden for et halvt minut.
- **Moderation:** Alle kan tilføje øl. Upassende indhold slettes i Supabase → Table Editor (`beers`, `reviews`) eller Storage (`billeder`).
- Gratis-planen holder til 500 MB database og 1 GB billeder. Et projekt uden aktivitet i 7 dage bliver sat på pause og skal vækkes i dashboardet.

## Android-signering
For at opdateringer kan installeres oven i den gamle app, skal appen signeres med samme nøgle hver gang. Læg disse under Settings → Secrets and variables → Actions:
- `ANDROID_KEYSTORE_BASE64`: keystore-filen, base64-kodet
- `ANDROID_KEYSTORE_PASSWORD`: adgangskoden
- **Nøglen må aldrig committes.** `.gitignore` udelukker `*.keystore` og `*.jks`.

## Microsoft Store
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
