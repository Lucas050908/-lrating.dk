# Teknik

## Hjemmesiden

- **Én fil:** `index.html` indeholder CSS, HTML-skabeloner og JavaScript. Der er intet byggetrin, så GitHub Pages serverer filerne direkte.
- **Sider:** routes med hash (`location.hash`). `route()` vælger en visning (`home`, `beerView`, `addView`, `tourView`, `genView` …) og skriver den i `<main id="app">`.
- **Sikkerhed:**
  - Content-Security-Policy i `<meta>`: `script-src 'self' 'unsafe-inline'`. `connect-src` og `img-src` tillader kun siden selv og `https://bbcegrufmzgfgzxazldr.supabase.co`.
  - Al brugertekst sendes gennem `esc()`.
- **Skrifttyper:** Inter og Sora ligger lokalt i `fonts/`, så der ikke sendes noget til Google.

### Data på enheden
| Hvor | Nøgle | Indhold |
|---|---|---|
| localStorage | `olrating-v1` | `S = {beers, reviews, me, season, wish, mode, units, tours, sh, si, gone, joins, dq}` |
| localStorage | `olrating-sb` | Den anonyme Supabase-session |
| IndexedDB | db `olrating`, store `img` | Billeder som Blob. I `S` står de som `idb:<nøgle>`, og `src()` laver dem om til object-URL'er |

- **Øl:** `{id, name, brewery, style, country, city, abv, ibu, color, size, price, place, serve, code, img, addedBy, date}`
- **Bedømmelse:** `{id, beer, who, date, s:{look,aroma,taste,feel,overall}, p:{sweet,bitter,sour,body,roast}, tags, text, img}`
- **Genstand:** `{t: tidsstempel, g: genstande, n: navn}`
- **Byttur:** `{id, name, date, meet, note, host, stops:[{name,time,addr}], members:[{name}]}`
- **Delelinks:**
  - Invitation: `#byttur-join-<base64url JSON>`
  - Svar: `#byttur-svar-<base64url {id,name}>`
  - Alt fra links bliver renset i `cleanTour()` med længdegrænser.

### Beregninger i `index.html`
- `isAf(b)`: alkoholfri, hvis `b.af` er sat, eller alkoholprocenten er over 0 og højst 0,5.
- `forYou(n)`: forslag til øl, brugeren ikke har bedømt. Udgangspunktet er øllens gennemsnit. Der lægges til eller trækkes fra efter, hvor meget brugerens karakterer for samme stil (vægt 0,8) og samme smagsord (vægt 0,6) ligger over eller under brugerens eget gennemsnit.
- `agree()`: enighed med andre i procent: 100 minus den gennemsnitlige forskel i karakter på fælles øl, hvor en forskel på 4 svarer til 0 %.
- `nextEvent()`: nærmeste af J-dag (første fredag i november), påskedag, sankthans, juleaften og nytårsaften.
- `myCounts()`: tal til mærkerne, bl.a. forskellige øl, stilarter, bryggerier, lande og alkoholfri.

### Offline
- `sw.js` gemmer app-skallen.
- **Husk at hæve `const V='olrating-vNN'` ved hver udgivelse**, ellers ser brugerne den gamle version.

## Broen mellem side og apps

Siden kalder `window.OlratingApp`, hvis den findes. Det gør den i Android-appen og i desktop-appen.

| Metode | Hvem kalder | Hvad |
|---|---|---|
| `updateWidget(json)` | Siden, efter hver `save()` og ved start | Sender data til widgets (se nedenfor) |
| `takeUnits()` | Siden ved start, når appen kommer i forgrunden, og hvert 5. sekund | Henter genstande lagt til fra widget (JSON-liste med tidsstempler) og tømmer listen |
| `saveImage(dataUrl, navn)` | Siden (kun Android) | Gemmer delekort i Billeder |
| `isApp()` | Siden | `true` |

Widget-data, som `syncApp()` sender:
```json
{"week":{"name","brewery","score"},"top":[{"name","score"}],
 "latest":[{"name","who","score"}],
 "me":{"name","count","beers","avg","style"},
 "units":{"today","week","todayN","weekN"},"beers":12,"reviews":31}
```

## Android (`android/`)
- **Opsætning:** Gradle med plugin 8.5.2, compileSdk 34, minSdk 24, pakke `dk.olrating.app`.
- **`MainActivity`:**
  - WebView med DOM storage, filvælger, kamera-tilladelse og tilbage-knap.
  - Links til andre sider åbnes i browseren. Egne værter er `xn--lrating-p1a.dk`, `www.` og den gamle github.io-sti.
  - `onNewIntent` håndterer tryk fra widgets, når appen allerede kører.
- **`Bridge`:** JavaScript-broen. Den gemmer data i SharedPreferences `olrating_widget` og opdaterer alle widgets.
- **Ikon:** Adaptivt ikon i `res/mipmap-anydpi-v26/` med `ic_launcher_foreground.png` (motivet i fuld flade, 108 dp) og `ic_launcher_mono.png` til tema-ikoner. `ic_launcher.png` og `ic_launcher_round.png` er til Android 7.
- **Widgets:** `TopWidget`, `QuickWidget`, `LatestWidget`, `StatsWidget` og `UnitsWidget`. +1 er en broadcast `dk.olrating.app.ADD_UNIT`, der lægger et tidsstempel i `pending_units`.
- **Byg:** `.github/workflows/android.yml` kører ved push til `android/**`.
  - Den bygger `assembleRelease` og lægger `olrating.apk` på udgivelsen `android-app`.
  - Den signerer med secrets, hvis de findes (se DRIFT.md). Ellers bruger den en midlertidig nøgle.

## Windows og Linux (`desktop/`)
- **Electron 33:**
  - `main.js` styrer hovedvinduet, widget-vinduet, ikonet ved uret og at der kun kører én instans.
  - `preload.js` udstiller `OlratingApp` til siden. `widget-preload.js` udstiller `W` til widgetten.
  - Sikkerhed: `contextIsolation`, `sandbox` og ingen `nodeIntegration`.
- **Widget:** `widget.html` med egen CSP. Placering, "altid øverst", sidste data og ventende genstande gemmes i `userData/widget.json`.
- **Byg:** `.github/workflows/desktop.yml` kører ved push til `desktop/**`.
  - Den bygger `olrating-windows.exe` (portable) på Windows og `olrating-linux.AppImage` på Ubuntu.
  - Begge lægges på udgivelsen `desktop-app`.

## Udgivelser
- Links peger altid på et fast tag (`releases/download/android-app/…` og `releases/download/desktop-app/…`), aldrig på `latest`. Ellers ville den ene app overskrive linket til den anden.

## Fælles database (Supabase)
- **Projekt:** `https://bbcegrufmzgfgzxazldr.supabase.co`, region EU.
- **Offentlig nøgle:** `sb_publishable_mf5v3jp_xYx7wJj1lgCr-Q_JUFuzXOY`. Den er lavet til at stå i koden. Secret- og service_role-nøglen må **aldrig** i repoet.
- **Skema:** `supabase/schema.sql` med tabellerne `beers`, `reviews`, `tours`, `tour_members`, `tastings` og `tasting_votes`, plus storage-bucket `billeder`.
- **Sikkerhed:** Row Level Security.
  - Alle kan læse.
  - Kun indloggede kan oprette, og kun med `owner = auth.uid()`.
  - Man kan kun rette og slette sine egne ting.
  - Billeder uploades til `billeder/<uid>/…`.
- **Login:** Anonymt. Hver enhed får sin egen usynlige bruger, så ingen skal oprette konto. Sessionen ligger i localStorage under `olrating-sb`.

### Synkronisering (`sb*`-funktionerne i `index.html`)
- Der bruges ikke noget bibliotek. `sbFetch()` kalder Supabase direkte: `/auth/v1/signup` og `/auth/v1/token`, `/rest/v1/<tabel>` og `/storage/v1/object/billeder/…`.
- `sbSync()` kører ved start, 1,5 sekund efter hver `save()`, hvert 30. sekund og når siden bliver synlig igen. Rækkefølgen er `sbAuth` → `sbPush` → `sbPull` → `sbTours`.
- **Push:** Egne objekter, der er ændret siden sidst, sendes som upsert. `S.sh[id]` gemmer en hash af det, der sidst blev synkroniseret. Billeder uploades først, og `img` skifter fra `idb:…` til den offentlige adresse, når rækken er gemt.
- **Pull:** Alle øl og bedømmelser hentes og flettes. Egne ændringer, der ikke er sendt endnu, vinder. Alt andet erstattes af databasens udgave. Objekter, der er slettet i databasen, fjernes lokalt.
- **Sletning:** Et id, der findes i `S.sh`, men ikke længere lokalt, lægges i `S.gone` og slettes i databasen efter 9 sekunder. Det giver plads til fortryd. `S.si[id]` husker stien til eget billede, så det kan slettes fra lageret sammen med rækken, eller når billedet skiftes ud.
- **Kø til sletning af ture:** `dq(sti)` lægger en DELETE i `S.dq`, som `sbTours()` udfører med op til 10 forsøg. Bruges, når værten sletter en tur, og når en deltager melder fra.
- **Ejerskab:** `mineObj(o)` er sand, når `o.owner` er enhedens bruger-id. Afviser databasen en skrivning (403/409), markeres objektet som en andens og erstattes ved næste pull.
- **Visning:** Ændrer et pull data, tegnes siden om med `softRoute()`, som beholder scroll og fokus. Det sker ikke, mens brugeren skriver i et felt eller har rørt en formular.
- **Byttur:** Værten gemmer turen i `tours`. Tilmeldinger lægges i køen `S.joins` og indsættes i `tour_members`. `sbFindTour(kode)` henter en tur ud fra dens id.

## Test (`tests/`)
Alle test bruger Playwright og en lokal server: `python3 -m http.server 8811 &`.

| Fil | Hvad | Rører den rigtige database? |
|---|---|---|
| `test_site.py` | Hele siden klikket igennem på pc (1280 px) og mobil (390 px): tilføj øl med foto, bedøm, ret, søg, del, delekort, genstande, temaer, backup, slet med fortryd, ryd alt, gendan, offline, filer og links | Nej |
| `test_sync.py` | To enheder deler data: øl, billeder, afvist redigering af andres øl, offline-kø, ingen gentegning mens man skriver, sletning med fortryd, byttur | Nej |
| `mock_supabase.py` | Efterligning af Supabase i hukommelsen, som de to test ovenfor bruger | Nej |
| `e2e_supabase.py` | Det samme forløb mod den rigtige database, inkl. forsøg på at rette andres data direkte gennem API'et. Opretter data med TEST i navnet og sletter dem igen | **Ja** |

- **GitHub Actions (`test.yml`):** `test_site.py` og `test_sync.py` kører ved hver ændring af siden. `e2e_supabase.py` kører kun ved manuel start eller når commit-beskeden indeholder `[database-test]`.
- Byggemiljøet, hvor koden skrives, kan ikke selv nå Supabase. Derfor køres testen mod den rigtige database på GitHub.
