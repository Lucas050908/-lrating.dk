# Teknik

## Hjemmesiden

- **Én fil:** `index.html` indeholder CSS, HTML-skabeloner og JavaScript. Der er intet byggetrin, så GitHub Pages serverer filerne direkte.
- **Sider:** routes med hash (`location.hash`). `route()` vælger en visning (`home`, `beerView`, `addView`, `tourView`, `genView` …) og skriver den i `<main id="app">`.
- **Sikkerhed:**
  - Content-Security-Policy i `<meta>`: `script-src 'self' 'unsafe-inline'`. `connect-src` og `img-src` tillader kun siden selv og `https://bbcegrufmzgfgzxazldr.supabase.co`.
  - Al brugertekst sendes gennem `esc()`.
  - Data udefra renses, før de gemmes lokalt: `cleanBeer()` og `cleanRev()` for øl og bedømmelser fra databasen og fra backup-filer, `cleanTour()` og `cleanTast()` for byture og smagninger. De tvinger typer (tal er tal, tekst er tekst), begrænser længder, smider ukendte felter væk og dropper rækker med ugyldigt id. Billedadresser accepteres kun, hvis de peger på sidens eget billedlager.
- **Tema:** Siden er altid mørk. `applyMode()` fjerner `data-mode` fra `<html>`, så reglerne under `[data-mode=light]` ikke bruges. De ligger stadig i koden, hvis et lyst tema skal tilbage som et valg.
- **Farver:** `--gl` (gul) og `--sun` (orange) er accentfarver til flader og ikoner. `--glt` og `--sunt` bruges til farvet *tekst*. I det mørke tema er de ens. I det lyse tema er de mørkere (`#855000` og `#b93a08`), så tekst kan læses på hvid baggrund. Elementer, der altid er mørke (forsidebillede, menu, sidefod, `.sc` m.fl.), sætter `--glt` tilbage til gul.
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
- **Smagning:** `{id, name, host, blind, revealed, beers:[navne], votes:{navn:[karakterer]}}`
- **Delelinks:**
  - Invitation: `#byttur-join-<base64url JSON>`
  - Svar: `#byttur-svar-<base64url {id,name}>`
  - Alt fra links bliver renset i `cleanTour()` med længdegrænser.

### Beregninger i `index.html`
- `enrich()`: alle øl med deres bedømmelser (`rs`) og gennemsnit (`avg`). Resultatet gemmes i `EC`, mens én side bliver tegnet, og nulstilles i `save()`, `route()`, `renderGrid()` og når browseren har tegnet færdig. Hvert kald får sin egen kopi af listen, så den frit kan sorteres.
- `isAf(b)`: alkoholfri, hvis `b.af` er sat, eller alkoholprocenten er over 0 og højst 0,5.
- `forYou(n)`: forslag til øl, brugeren ikke har bedømt. Udgangspunktet er øllens gennemsnit. Der lægges til eller trækkes fra efter, hvor meget brugerens karakterer for samme stil (vægt 0,8) og samme smagsord (vægt 0,6) ligger over eller under brugerens eget gennemsnit.
- `agree()`: enighed med andre i procent: 100 minus den gennemsnitlige forskel i karakter på fælles øl, hvor en forskel på 4 svarer til 0 %.
- `S.follow`: navnene på dem, brugeren følger. Listen bliver på enheden og sendes ikke til databasen.
- `brewMap(L)`: tegner kortet over bryggerier som SVG. `DKMAP` er kystlinjen som få punkter i længde- og breddegrad, og `DKC` er en tabel over byer og deres placering. Byens navn gøres til små bogstaver, og tal og et enkelt bogstav til sidst (som i "København K") fjernes, før der slås op.
- `dupCheck()`: kører 250 ms efter, at brugeren har skrevet i navn, bryggeri eller stregkode på Tilføj øl. Den finder op til tre øl med samme stregkode eller næsten samme navn (`norm()` og `near()`), og viser dem i `#dupHint`.
- `yearData(y)`: tallene bag Årets øl. Bedømmelser med dato i året `y` grupperes pr. øl, bryggeri og stil. `min` er 2, hvis mindst én øl har 2 bedømmelser i året, ellers 1.
- `makeListCard(kick,title,list)`: tegner et billede med op til 5 øl på et canvas. `cardBg()` tegner baggrund og logo, og `shareBlob()` deler billedet, gemmer det i appen eller henter det som fil. `shareTop(t)` og `shareYear(y)` bruger dem til Toplisten og Årets øl.
- `tourOver(t)`: sand, når der er gået 14 timer fra turens første stop. `tourMem(t)` finder de bedømmelser, holdet har givet på turens dato (og dagen efter, hvis turen starter kl. 16 eller senere), og `makeTourCard(t)` tegner mindet som billede.
- `nextEvent()`: nærmeste af J-dag (første fredag i november), påskedag, sankthans, juleaften og nytårsaften.
- `myCounts()`: tal til mærkerne, bl.a. forskellige øl, stilarter, bryggerier, lande og alkoholfri.

### Sprog (dansk og engelsk)
- Al tekst i `index.html` er dansk. Valget gemmes i `S.lang` (`da` eller `en`) og skiftes i sprogvælgeren i topmenuen (`#langBtn`, `#langdd`) eller under "Sprog · Language" i sidefoden. Begge kalder `setLang()`.
- **Skift uden genindlæsning (`setLang`):** Til engelsk hentes ordbogen, siden tegnes forfra (`softRoute`, så tal og datoer følger sproget) og oversættes. Til dansk lægger `trBack()` den danske tekst tilbage. Den blev gemt på hvert element, da det blev oversat (`__o` for tekst, `__oa` for attributter, `__sk` for sætninger). Er brugeren ved at skrive i en formular, tegnes siden ikke forfra, så det skrevne bliver stående. Hvor browseren kan (`document.startViewTransition`), sker skiftet med en blød overgang.
- `langUI()` sætter flag, kode og markering i menuen. Har browseren et andet sprog end dansk, norsk eller svensk, og er der ikke valgt sprog (`S.langSet`), viser knappen "English?".
- Ved engelsk hentes `js/en.js` (ligger også i service workerens cache). Den sætter `window.EN_DATA = {x, r}`:
  - `x`: faste tekster, dansk → engelsk.
  - `r`: mønstre (regulære udtryk) til tekster med tal og navne, fx "3 bedømmelser" eller "Bedøm Limfjordsporter".
- **Oversættelsen sker i DOM'en.** `trEl()` går et element igennem og oversætter tekst og attributterne `placeholder`, `aria-label`, `title` og `alt`. En `MutationObserver` (`trObs`) oversætter alt nyt, der lander på siden, før det bliver vist. Derfor skal de enkelte sider ikke kende til sprog.
  - `trS(t)`: oversætter én tekst. Mellemrum og prikker (·) i enderne bevares. Findes hele teksten ikke, prøves hver del mellem " · " for sig.
  - `trSkel(el)`: en sætning med fed skrift eller links i oversættes samlet. De små elementer skrives som `<1>…</1>`, `<2>…</2>` i nøglen og i oversættelsen, og `trFill()` lægger teksten tilbage i de samme elementer.
  - Elementer med `data-notr` bliver ikke oversat. Indhold, brugerne selv har skrevet, står ikke i ordbogen og bliver derfor ikke ændret.
- `fmt()` og `gFmt()` skriver decimalpunktum på engelsk og komma på dansk. `LOC()` giver `en-GB` eller `da-DK` til datoer.
- `confirm()` og `prompt()` er pakket ind, så teksten bliver oversat. Tekst på delebilleder oversættes i `trCtx()`.
- Valgmulighederne i formularer har faste danske værdier (`value`), så data gemmes ens på begge sprog. Stilarter, smagsord, lande og størrelser gemmes altid på dansk og oversættes kun, når de vises.
- **Ikke oversat:** adresserne (`#toplisten` osv.), widgets i Android-appen og i programmet til Windows og Linux, og beskrivelsen i søgemaskiner.

### Enig eller uenig (stemmer på bedømmelser)
- `S.rv` er egne stemmer (`{bedømmelse: 1 eller -1}`), `S.rvq` er stemmer, der venter på at blive sendt, `S.rvc` er tallene fra databasen (`{bedømmelse: [enige, uenige]}`), og `S.rvs` er dem, der er sprunget over.
- `sbVotes()` kører sidst i hver synkronisering. Den sender køen til tabellen `review_votes` og henter tallene fra viewet `review_vote_counts` og ens egne stemmer. Svarer databasen 404, sættes `rvOk=false`, og der prøves først igen ved næste indlæsning.
- `swipeDeck()` vælger kortene, `swAct(id, v)` gemmer en stemme (eller et spring over) og lader kortet flyve ud, og `swipeWire()` står for trækket med fingeren eller musen.
- `rvC(id)` giver tallene til visning. En stemme, der ikke er sendt endnu, tælles med.

### Konto
- `KONTO` (konstant i `index.html`) slår kontoen til for alle. `kontoOn()` er også sand, når `localStorage['olrating-konto']` er `1`, og det sætter adressen `#konto-test`.
- **Ny konto:** `acctSend(mail)` kalder `PUT /auth/v1/user` med mailen på den anonyme bruger. Supabase sender en kode, og `acctVerify(kode)` bekræfter den med `POST /auth/v1/verify` (`type: email_change`). Brugeren beholder sit id.
- **Mailen findes i forvejen:** `PUT` svarer 422, og der bedes i stedet om en login-kode (`POST /auth/v1/otp`, `type: email`). Før koden bekræftes, henter den anonyme bruger et flyttebevis (`konto_flyt_start`), og bagefter afleverer kontoen det (`konto_flyt_slut`), så databasen skifter ejer på enhedens rækker.
- `isAcct()` er sand, når sessionen har en mail og ikke er anonym. `acctOut()` logger ud, og enheden får en ny anonym bruger ved næste synkronisering. `acctDel()` kalder `konto_slet`.
- **Mailvalg:** `acctPrefs()` og `acctSavePrefs()` læser og skriver brugerens række i `mail_prefs`. Navn, sprog og (hvis mails om venner er slået til) hvem man følger, sendes med og opdateres af `acctTouch()`, når de ændres.

### Mails
- **Kø:** Triggere i databasen (`supabase/003`) lægger en række i `mail_queue`, når der kommer en bedømmelse, en tilmelding til en byttur eller en stemme i en smagning, som en bruger har bedt om mail om. En nyhed (`mail_news`) lægges i kø til alle med nyheder slået til, når ejerne sætter flueben i `send` (`supabase/004`).
- **Udsendelse:** `pg_cron` kalder hvert 10. minut funktionen `mails` (`supabase/functions/mails/index.ts`) gennem `pg_net`, men kun når køen ikke er tom. Kaldet har en nøgle med (`x-cron-key`), som kun står i tabellen `mail_state`. Uden den rigtige nøgle sker der ingenting.
- **Reglerne står i databasen,** så de kan testes: `mail_hent(nøgle)` giver én samlet mail pr. bruger, højst én i timen, "ven har bedømt" højst én gang om dagen (dansk dato), og sletter det, brugeren har slået fra. Rækkerne mærkes som taget (`taken_at`), og `mail_faerdig(nøgle, ids, r)` kvitterer: `1` sendt, `0` prøv igen næste gang, `-1` afvist (prøv igen om en time). Taget, men ikke kvitteret inden for 30 minutter, bliver frigivet. Usendt i 3 dage bliver slettet.
- **Funktionen er tynd:** den henter, bygger mailen (dansk eller engelsk, HTML og ren tekst, alt brugerindhold bliver escapet) og sender den gennem Resends API. Den bruger ingen pakker, så den kan kopieres ind i Supabase. Nøglen til Resend er en hemmelighed i Supabase (`RESEND_API_KEY`) og står ikke i repoet. `Idempotency-Key` gør, at den samme mail ikke sendes to gange.
- **Afmelding:** Linket i mailen går til `#afmeld-<nøgle>` på siden (`unsubView`, svaret huskes i `UNS`, så det overlever en gentegning). Først når man trykker på knappen, kaldes `mail_afmeld(nøgle)`, som alle må kalde, fordi nøglen (`mail_prefs.unsub`) er tilfældig og kun står i brugerens egne mails. Mailprogrammers egen afmeld-knap (`List-Unsubscribe`) rammer funktionen med `POST ?unsub=`. En Edge Function kan ikke vise HTML, så `GET ?unsub=` sender bare videre til siden.
- Opsætningen trin for trin står i `docs/KONTO.md`.

### Lange ord
- `#app{overflow-wrap:anywhere}` lader lange ord uden mellemrum knække, så brugerindhold ikke kan gøre siden bredere end skærmen. Knapper, mærkater og formularfelter er undtaget.
- Overskrifter har `hyphens:auto`, så lange sammensatte ord får bindestreg, hvor browseren har en ordbog til sproget.

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
 "rec":{"id","name","why","score"}, "next":{"n","date"},
 "units":{"today","week","todayN","weekN"},"beers":12,"reviews":31}
```

## Android (`android/`)
- **Opsætning:** Gradle med plugin 8.5.2, compileSdk 34, minSdk 24, pakke `dk.olrating.app`.
- **`MainActivity`:**
  - WebView med DOM storage, filvælger, kamera-tilladelse og tilbage-knap.
  - Links til andre sider åbnes i browseren. Egne værter er `xn--lrating-p1a.dk`, `www.` og den gamle github.io-sti.
  - `onNewIntent` håndterer tryk fra widgets og genveje, når appen allerede kører.
  - `isOwn(Uri)` afgør, om en adresse må vises i appen: kun https på ølrating.dk (og den gamle github.io-sti). Det gælder også adresser, der kommer udefra i en intent, så en fremmed side aldrig får adgang til `OlratingApp`-broen.
  - Genvejene på app-ikonet står i `res/xml/shortcuts.xml`.
- **`Bridge`:** JavaScript-broen. Den gemmer data i SharedPreferences `olrating_widget` og opdaterer alle widgets.
- **Ikon:** Adaptivt ikon i `res/mipmap-anydpi-v26/` med `ic_launcher_foreground.png` (motivet i fuld flade, 108 dp) og `ic_launcher_mono.png` til tema-ikoner. `ic_launcher.png` og `ic_launcher_round.png` er til Android 7.
- **Widgets:** `TopWidget`, `QuickWidget`, `LatestWidget`, `StatsWidget`, `SuggestWidget` og `UnitsWidget`. `SuggestWidget` regner selv dagene til `next.date` ud, så nedtællingen passer, selv om appen ikke har været åbnet. +1 er en broadcast `dk.olrating.app.ADD_UNIT`, der lægger et tidsstempel i `pending_units`.
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
  - **Microsoft Store:** `npm run dist:store` (`store-build.js`) bygger en `.appx`-pakke ud fra `store.json`. Uden værdier bygges en prøvepakke. Se `docs/STORE.md`.

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
- **Smagning:** `S.tast` holder smagningerne, og `S.vq` er køen af stemmer, der skal sendes. `sbTast()` gemmer værtens smagning i `tastings`, sender stemmer til `tasting_votes` (én række pr. smagning og navn) og henter alles stemmer. Er et navn allerede brugt fra en anden enhed, afvises stemmen, og brugeren får besked. Når `revealed` skifter til sand, tegnes siden om med animation hos alle.
- **Hurtig opdatering:** På `#byttur-…` og `#smagning-…` kører `sbSync()` hvert 6. sekund.
- **Byttur:** Værten gemmer turen i `tours`. Tilmeldinger lægges i køen `S.joins` og indsættes i `tour_members`. `sbFindTour(kode)` henter en tur ud fra dens id.

## Test (`tests/`)
Tilgængelighed er tjekket med axe-core (WCAG 2 A og AA) på alle sider i begge temaer. Det tjek ligger ikke i repoet, fordi det kræver en ekstra pakke, men kan gentages med `npm install axe-core` og Playwrights `add_script_tag`.

Alle test bruger Playwright og en lokal server: `python3 -m http.server 8811 &`.

| Fil | Hvad | Rører den rigtige database? |
|---|---|---|
| `test_site.py` | Hele siden klikket igennem på pc (1280 px) og mobil (390 px): tilføj øl med foto, bedøm, ret, søg, del, delekort, genstande, temaer, backup, slet med fortryd, ryd alt, gendan, offline, filer og links | Nej |
| `test_sync.py` | To enheder deler data: øl, billeder, afvist redigering af andres øl, offline-kø, ingen gentegning mens man skriver, sletning med fortryd, byttur, smagning og fjendtlige data i databasen (indlejret kode og forkerte typer) | Nej |
| `test_en.py` | Den engelske version: alle sider og tilstande gås igennem på dansk og engelsk med stillestående ur. Testen fejler, hvis en tekst er ens i de to udgaver eller stadig har danske bogstaver, hvis en besked i koden (toast, confirm, prompt) mangler i ordbogen, hvis brugernes eget indhold bliver oversat, eller hvis en side får vandret scroll på mobil | Nej |
| `test_sql.js` | `supabase/003-konto-mails-enig.sql` og `004-mails.sql` afprøvet i en rigtig Postgres i hukommelsen (PGlite): hvem der må stemme, at man kun ser sine egne stemmer, flytning af data til en konto, mailvalg og køen med mails. Funktionen `supabase/functions/mails` køres mod den samme database med en efterlignet mailtjeneste: indhold på dansk og engelsk, højst én mail i timen, venner én gang om dagen, nyheder, fejl hos mailtjenesten og afmelding. Kræver `npm install --no-save @electric-sql/pglite` | Nej |
| `mock_supabase.py` | Efterligning af Supabase i hukommelsen, som de to test ovenfor bruger | Nej |
| `e2e_supabase.py` | Det samme forløb mod den rigtige database, inkl. forsøg på at rette andres data direkte gennem API'et. Opretter data med TEST i navnet og sletter dem igen | **Ja** |

- **GitHub Actions (`test.yml`):** `test_site.py`, `test_sync.py` og `test_en.py` kører ved hver ændring af siden. `e2e_supabase.py` kører kun ved manuel start eller når commit-beskeden indeholder `[database-test]`.
- Byggemiljøet, hvor koden skrives, kan ikke selv nå Supabase. Derfor køres testen mod den rigtige database på GitHub.
