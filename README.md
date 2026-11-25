# ølrating.dk

Danske øl, bedømt af dem der drikker dem.

**Ejere:** Lucas Valentin Ottesen og Magnus Birkgaard Froberg

**Fejl og forslag:** andersenlucas84@gmail.com

En statisk hjemmeside uden server og uden byggetrin: `index.html` plus billeder, skrifttyper og et par små filer. Den kører på GitHub Pages: https://ølrating.dk (xn--lrating-p1a.dk). Domænet ligger hos one.com; før det virkede, kørte den på lucas050908.github.io/-lrating.dk – **ølrating.dk** er klar hos Simply.

## Hvad siden kan

- Tilføj øl med billede, navn, stregkode og bedømmelse i fem kategorier plus smagsprofil
- Side for hver øl, toplisten, galleri, stilguide, bryggerier, ølkalender, øl til maden og sammenlign to øl
- Min profil med mærker, ønskeliste, øl-dagbog ("Dit år i øl") og backup
- Sæsontemaer (jul, J-dag, nytår, fastelavn, påske, sankthans, halloween) og lyst/mørkt tema
- Kan installeres som app på telefonen (PWA) og virker uden net

## Filer

| Fil | Hvad |
|---|---|
| `index.html` | Hele siden: design, sider og logik |
| `sw.js`, `manifest.webmanifest` | Gør siden installerbar og brugbar offline |
| `img/` | Fotos fra Limfjorden, app-ikoner og delingsbillede (`og.jpg`) |
| `fonts/` | Inter og Sora (SIL Open Font License), ligger lokalt så intet sendes til Google |
| `404.html` | Vises ved forkerte adresser og sender videre til forsiden |
| `CNAME`, `robots.txt`, `sitemap.xml`, `.nojekyll` | Domæne og søgemaskiner |

## Hosting

1. **GitHub Pages:** Settings → Pages → "Deploy from a branch" → `main` / `(root)`.
2. **Custom domain (når Simply-kontoen virker):** skriv `xn--lrating-p1a.dk` (= ølrating.dk) under Settings → Pages, og skift adressen `lucas050908.github.io/-lrating.dk` tilbage til `xn--lrating-p1a.dk` i `index.html`, `robots.txt`, `sitemap.xml` og `404.html`. Slå "Enforce HTTPS" til, når certifikatet er klar.
3. **DNS hos Simply.com** (DNS-indstillinger for ølrating.dk):

| Type | Navn | Værdi |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | lucas050908.github.io |

Slet andre A-records på @ (fx Simplys standard-parkeringsside). Det kan tage op til et par timer, før domænet og HTTPS virker.

## Android-app

Mappen `android/` er en lille Android-app, der viser siden i fuld skærm med billed-upload og kamera.
GitHub Actions (`.github/workflows/android.yml`) bygger den og lægger `olrating.apk` på udgivelsen **android-app**.
Hjemmesiden linker til `releases/download/android-app/olrating.apk`.

For at nye versioner kan installeres oven i de gamle, skal appen signeres med samme nøgle hver gang. Læg nøglen som secrets under Settings → Secrets and variables → Actions:

- `ANDROID_KEYSTORE_BASE64`: keystore-filen, base64-kodet
- `ANDROID_KEYSTORE_PASSWORD`: adgangskoden til den

Uden dem laver bygningen en midlertidig nøgle, og så skal appen afinstalleres før en opdatering.

## Data

Lige nu gemmes øl og bedømmelser i den enkelte browser (`localStorage`). Næste skridt er en fælles database (Supabase), så alle kan se hinandens øl, og Android-appen og widgets kan bruge de samme data. Husk da at tilføje Supabase-adressen i `connect-src` i Content-Security-Policy øverst i `index.html`.

Fotos: Lucas, Limfjorden.
