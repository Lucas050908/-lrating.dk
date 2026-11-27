# Teknik

## Hjemmesiden

- **Én fil:** `index.html` indeholder CSS, HTML-skabeloner og JavaScript. Der er intet byggetrin, så GitHub Pages serverer filerne direkte.
- **Sider:** routes med hash (`location.hash`). `route()` vælger en visning (`home`, `beerView`, `addView`, `tourView`, `genView` …) og skriver den i `<main id="app">`.
- **Sikkerhed:**
  - Content-Security-Policy i `<meta>`: `script-src 'self' 'unsafe-inline'`. `img-src` tillader kun siden selv, `data:`/`blob:` og `https://bbcegrufmzgfgzxazldr.supabase.co`. `connect-src` tillader siden selv, databasen og de to adresser hos Open Food Facts (`world.openfoodfacts.org` og `images.openfoodfacts.org`) til stregkode-opslaget.
  - Al brugertekst sendes gennem `esc()`.
  - Data udefra renses, før de gemmes lokalt: `cleanBeer()` og `cleanRev()` for øl og bedømmelser fra databasen og fra backup-filer, `cleanTour()` og `cleanTast()` for byture og smagninger. De tvinger typer (tal er tal, tekst er tekst), begrænser længder, smider ukendte felter væk og dropper rækker med ugyldigt id. Billedadresser accepteres kun, hvis de peger på sidens eget billedlager.
- **Tema:** Siden er altid mørk. `applyMode()` fjerner `data-mode` fra `<html>`, så reglerne under `[data-mode=light]` ikke bruges. De ligger stadig i koden, hvis et lyst tema skal tilbage som et valg.
- **Farver:** `--gl` (gul) og `--sun` (orange) er accentfarver til flader og ikoner. `--glt` og `--sunt` bruges til farvet *tekst*. I det mørke tema er de ens. I det lyse tema er de mørkere (`#855000` og `#b93a08`), så tekst kan læses på hvid baggrund. Elementer, der altid er mørke (forsidebillede, menu, sidefod, `.sc` m.fl.), sætter `--glt` tilbage til gul.
- **Skrifttyper:** Inter og Sora ligger lokalt i `fonts/`, så der ikke sendes noget til Google.

### Data på enheden
| Hvor | Nøgle | Indhold |
|---|---|---|
| localStorage | `olrating-v1` | `S = {beers, reviews, me, season, lang, look, wish, units, tours, tast, sh, si, gone, joins, dq, rv, rvq, rvc, rvs, …}` |
| localStorage | `olrating-vis404` | Tidspunkt for sidste 404 fra besøgstælleren. Så spørges der højst én gang i timen, før fil 005 er kørt |
| localStorage | `olrating-konto` | Sat af `#konto-test`, så kontoen kan prøves på én enhed |
| localStorage | `olrating-sb` | Den anonyme Supabase-session |
| IndexedDB | db `olrating`, store `img` | Billeder som Blob, eller som `{t, b: ArrayBuffer}`, hvis browseren ikke kan gemme Blobs (`asBlob()` læser begge). I `S` står de som `idb:<nøgle>`, og `src()` laver dem om til object-URL'er |

- **Øl:** `{id, name, brewery, style, country, city, abv, ibu, color, size, price, place, desc, code, af, img, addedBy, date, edited?, owner?}`
- **Bedømmelse:** `{id, beer, who, date, s:{look,aroma,taste,feel,overall}, prof:{…}|null, tags, again, text, img, edited?, owner?}`. `s` har én decimal (1,0–5,0). `edited` sættes, når den er rettet; datoen ændres ikke.
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
- `rvMine()` lægger stemmerne på ens egne bedømmelser sammen. `S.rvSeen` er tallet, sidst Min profil blev vist, og `rvNew()` er forskellen. `rvDot()` sætter klassen `nyt` på Min profil og menu-knappen efter hver sidevisning og synkronisering. `profileView` viser forskellen og nulstiller den.

### Konto
- `KONTO` (konstant i `index.html`) slår kontoen til for alle. `kontoOn()` er også sand, når `localStorage['olrating-konto']` er `1`, og det sætter adressen `#konto-test`.
- **Ny konto:** `acctSend(mail)` kalder `PUT /auth/v1/user` med mailen på den anonyme bruger. Supabase sender en kode, og `acctVerify(kode)` bekræfter den med `POST /auth/v1/verify` (`type: email_change`). Brugeren beholder sit id.
- **Mailen findes i forvejen:** `PUT` svarer 422, og der bedes i stedet om en login-kode (`POST /auth/v1/otp`, `type: email`). Før koden bekræftes, henter den anonyme bruger et flyttebevis (`konto_flyt_start`), og bagefter afleverer kontoen det (`konto_flyt_slut`), så databasen skifter ejer på enhedens rækker.
- `isAcct()` er sand, når sessionen har en mail og ikke er anonym. `acctOut()` logger ud, og enheden får en ny anonym bruger ved næste synkronisering. `acctDel()` kalder `konto_slet`.
- **Det, der følger kontoen (`sbKonto()`):** Navn, ønskeliste og følger ligger som én JSON-række pr. konto i `konto_data`, som kun kontoen selv kan læse. Funktionen kører sidst i hver synkronisering, når man er logget ind. Hver gemning får et tilfældigt mærke (`e`). Enheden husker det mærke, den sidst så (`S.kde`), og et aftryk af sine egne data (`S.kdh`). Har kun den anden enhed gemt, tages dens data. Har kun denne enhed ændret noget, gemmes de. Har begge, eller er enheden ny på kontoen (`S.kdu`), lægges listerne sammen. Der bruges ikke klokkeslæt, så et ur, der går forkert, betyder ikke noget. Mangler tabellen (ældre udgave af 003), springes det over.
- **Mailvalg:** `acctPrefs()` og `acctSavePrefs()` læser og skriver brugerens række i `mail_prefs`. Navn, sprog og (hvis mails om venner er slået til) hvem man følger, sendes med og opdateres af `acctTouch()`, når de ændres.

### Mails
- **Loft:** `mail_plads(bruger)` er sand, så længe brugeren har under 200 ventende rækker. Triggerne spørger den, før de lægger noget i kø.
- **Kø:** Triggere i databasen (`supabase/003`) lægger en række i `mail_queue`, når der kommer en bedømmelse, en tilmelding til en byttur eller en stemme i en smagning, som en bruger har bedt om mail om. En nyhed (`mail_news`) lægges i kø til alle med nyheder slået til, når ejerne sætter flueben i `send` (`supabase/004`).
- **Udsendelse:** `pg_cron` kalder hvert 10. minut funktionen `mails` (`supabase/functions/mails/index.ts`) gennem `pg_net`, men kun når køen ikke er tom. Kaldet har en nøgle med (`x-cron-key`), som kun står i tabellen `mail_state`. Uden den rigtige nøgle sker der ingenting.
- **Reglerne står i databasen,** så de kan testes: `mail_hent(nøgle)` giver én samlet mail pr. bruger, højst én i timen, "ven har bedømt" højst én gang om dagen (dansk dato), og sletter det, brugeren har slået fra. Rækkerne mærkes som taget (`taken_at`), og `mail_faerdig(nøgle, ids, r)` kvitterer: `1` sendt, `0` prøv igen næste gang, `-1` afvist (prøv igen om en time). Taget, men ikke kvitteret inden for 30 minutter, bliver frigivet. Usendt i 3 dage bliver slettet.
- **Funktionen er tynd:** den henter, bygger mailen (dansk eller engelsk, HTML og ren tekst, alt brugerindhold bliver escapet) og sender den gennem Resends API. Den bruger ingen pakker, så den kan kopieres ind i Supabase. Nøglen til Resend er en hemmelighed i Supabase (`RESEND_API_KEY`) og står ikke i repoet. `MAIL_FROM` og `MAIL_REPLY_TO` er valgfri hemmeligheder til afsender og svar-adresse. `Idempotency-Key` gør, at den samme mail ikke sendes to gange.
- **Afmelding:** Linket i mailen går til `#afmeld-<nøgle>` på siden (`unsubView`, svaret huskes i `UNS`, så det overlever en gentegning). Først når man trykker på knappen, kaldes `mail_afmeld(nøgle)`, som alle må kalde, fordi nøglen (`mail_prefs.unsub`) er tilfældig og kun står i brugerens egne mails. Mailprogrammers egen afmeld-knap (`List-Unsubscribe`) rammer funktionen med `POST ?unsub=`. En Edge Function kan ikke vise HTML, så `GET ?unsub=` sender bare videre til siden.
- Opsætningen trin for trin står i `docs/KONTO.md`.

### Beer buddies
- `buddies()` samler alle bedømmelser pr. navn (uden forskel på store og små bogstaver) og sammenligner med brugerens egne (`S.me`). Den bruger `tot(r)`, altså den samlede karakter for en bedømmelse.
- Match = `Math.round(100 - gennemsnitlig forskel / 4 * 100)`. Den returnerer `{match, rest}`: `match` er dem med mindst to fælles øl, sorteret efter procent, og `rest` er op til 12 andre.
- `buddyView()` tegner siden på ruten `#buddies`. Klasserne hedder `bud…` (`budtop`, `budh`, `budp`, `budn`, `budb`, `budl`, `budk`), fordi korte navne som `.top` og `.pill` allerede var brugt til andet i stilarket.
- Alt regnes ud på enheden ud fra de bedømmelser, der allerede er hentet. Der er ingen nye tabeller i databasen.

### Lykkehjulet
- Tilstanden ligger i `HJ` (`src` gruppe, `ids` øllene på hjulet, `rot` grader, `win` vinderen). Den gemmes ikke, så hjulet starter forfra, når siden åbnes igen.
- `hjPool(src)` finder øllene i en gruppe, og `hjFill()` blander dem og tager de første 10.
- `hjWheel()` tegner hjulet som SVG. Felt nr. `i` går fra `i × 360/n` til `(i+1) × 360/n` grader med uret fra toppen, hvor pilen sidder.
- `hjSpin()` trækker vinderen først og regner så ud, hvor langt hjulet skal dreje: fem hele omgange plus det, der skal til, for at vinderens felt ender under pilen. Selve drejningen er en CSS-overgang på `#hjG`. Når den er slut, tegnes siden igen med `softRoute()`, og resultatet står i `#hjRes`.
- Med `prefers-reduced-motion` er der ingen overgang, og resultatet vises med det samme.

### Karakterer med kommatal
- `rateRow(k, navn, værdi)` bygger én række: fem stjerneknapper (`data-star`, hele tal) og en gruppe med − og + (`data-step`, trin på 0,1) omkring et `<output class="rnv">`. Rækken bruges både i bedømmelsen af en øl og i smagninger.
- `rateSet(række, værdi)` er det eneste sted, værdien ændres: den afrunder til én decimal, holder den mellem 1 og 5, sætter `data-v`, og markerer stjernerne. Hele stjerner får klassen `on`. Den stjerne, der kun er delvist fyldt, får `part` og `--f` (fx `70%`), og en CSS-maske tegner den fyldte del.
- `cleanRev()` gemmer nu én decimal i stedet for at afrunde til hele tal. Databasen gemmer karaktererne som JSON, så den skulle ikke ændres.
- Tallet vises med komma på dansk og punktum på engelsk (`fmt`). `setLang` kalder `rateSet` igen, så tal, der allerede er valgt, følger sproget.

### Forslag til logo (`img/logoer/`)
- **1000 logoer:** `img/logoer/1000/` (filnavne `0001-…svg`). `nr(n)` i `tools/logoer.py` giver motiv og stil for nr. 1–1000: 1–200 er de 5 første stilarter, `(motiv-1)*5+stil`; 201–1000 er `STIL2` (20 stilarter), `200+(motiv-1)*20+stil`. Formerne er `sq` (afrundet firkant), `ci` (cirkel) og `hx` (sekskant, motivet skaleret til 80 %). Nr. 1001–10000 er `STIL3` (225 pr. motiv: `PAL25` × `FORM5` × med/uden ring, minus dem, der findes i 1–1000), `1000+(motiv-1)*225+stil`. Formerne `oc` (ottekant) og `sk` (skjold) og ringen (`…r`, fx `sqr`) tegnes i `build()`. De 10.000 gemmes ikke i repoet; kør `python3 tools/logoer.py <mappe> --10000`.
- Mappen har 50 forslag som SVG, nummereret `01` til `50`. Nr. 10, 49 og 50 bruger `<text>` og er derfor afhængige af enhedens skrifttyper. De bruger sidens farver: nat `#0f1d36`, sol `#ff7a3d`, aften `#f0566b` og guld `#ffc85a`.
- `img/logoer/200/` har 200 forslag mere: 40 motiver i fem stilarter. Nummeret er `(motiv − 1) × 5 + stil`, hvor stil 1 er nat, 2 solnedgang, 3 lys, 4 guld og 5 fjord.
- `tools/logoer.py` tegner dem. Hvert motiv er en funktion (`m01` til `m40`), der får en palet (`p.m` hovedfarve, `p.b` øl, `p.a` detalje, `p.c` udskæring, `p.f` skum med mere), og `build()` lægger baggrunden under. Scriptet skriver også `index.json` og `ark.html` i mappen, man peger på. De to filer ligger ikke i repoet.
- Filerne bruges ikke af siden endnu. Når ét er valgt, skal det ind som `img/favicon.svg`, og `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` og ikonerne i `android/` og `desktop/` skal laves ud fra det.

### Lange ord
- `#app{overflow-wrap:anywhere}` lader lange ord uden mellemrum knække, så brugerindhold ikke kan gøre siden bredere end skærmen. Knapper, mærkater og formularfelter er undtaget.
- Overskrifter har `hyphens:auto`, så lange sammensatte ord får bindestreg, hvor browseren har en ordbog til sproget.
- **Skjulte filfelter:** `.drop input` og `.sr` har `padding:0`, `min-height:0` og `overflow:hidden`, og filfeltet i billedfeltet ligger i feltets hjørne (`left:0;top:0`). Safari regner ellers filfeltets indbyggede knaptekst med i sidens bredde, hvis feltet tilfældigvis står tæt på højre kant.

### Offline
- `sw.js` gemmer app-skallen.
- Når siden åbnes, hentes den fra nettet først. Kun selve forsiden (`/` eller `/index.html`) med status 200 gemmes som den udgave, der bruges uden net, så en fejlside aldrig tager dens plads.
- Billeder, ikoner, skrifttyper og scripts tages fra lageret først.
- De store forsidebilleder til pc (`fjord1.jpg` osv.) er ikke med i `SHELL`, fordi telefoner kun bruger de små (`-m`). De gemmes, første gang de bliver vist.
- **Husk at hæve `const V='olrating-vNN'` ved hver udgivelse**, ellers ser brugerne den gamle version.

## Broen mellem side og apps

Siden kalder `window.OlratingApp`, hvis den findes. Det gør den i Android-appen og i desktop-appen.

| Metode | Hvem kalder | Hvad |
|---|---|---|
| `updateWidget(json)` | Siden, efter hver `save()` og ved start | Sender data til widgets (se nedenfor) |
| `updateImages(json)` | Siden, når de øl, widgets viser, eller deres billeder har ændret sig | Sender små billeder: `{"øl-id":"data:image/jpeg;base64,…"}`, højst 10 øl, 288 × 288 px |
| `takeUnits()` | Siden ved start, når appen kommer i forgrunden, og hvert 5. sekund | Henter genstande lagt til fra widget (JSON-liste med tidsstempler) og tømmer listen |
| `saveImage(dataUrl, navn)` | Siden (kun Android) | Gemmer delekort i Billeder |
| `isApp()` | Siden | `true` |

Widget-data, som `syncApp()` sender:
```json
{"week":{"id","name","brewery","score"},"top":[{"id","name","score"}],
 "latest":[{"id","name","who","score"}],
 "me":{"name","count","beers","avg","style"},
 "rec":{"id","name","why","score"}, "next":{"n","date"},
 "units":{"today","week","todayN","weekN"},"beers":12,"reviews":31,
 "site":{"visits":1234,"today":17,"tasters":9}}
```
`site.visits` og `site.today` er `null`, indtil besøgstælleren har svaret (se Besøgstæller).

**Billeder til widgets:** `wImgs()` finder de øl, widgets viser (ugens øl, top 3, forslaget og de 4 seneste), og `wThumb()` tegner hvert billede ned til 288 × 288 px JPEG. Der sendes kun igen, når listen eller et billede har ændret sig. Android gemmer dem som filer i appens egen mappe (`files/wimg/<id>.jpg`, klassen `WImg`) og sletter dem, der ikke bruges længere. Desktop gemmer dem i `widget-images.json` i brugerens datamappe. Begge steder tjekkes id, type og størrelse, før noget gemmes.

### Objekter med navne som nøgler
- Bruges et navn, som nogen har skrevet (smager, bryggeri, stil, smagsord), som nøgle i et objekt, skal objektet laves med `Object.create(null)` og ikke `{}`. Ellers findes `constructor`, `toString` og `__proto__` allerede i objektet, og `o[k]=o[k]||…` giver forkerte værdier eller får siden til at gå ned. `test_site.py` har et tjek med de navne.

### Lykkehjulet, når siden tegnes igen
- `HJ.ids` ændres ikke, mens hjulet drejer (`HJ.busy`), eller mens resultatet står (`HJ.win`). Vinderen gemmes, når drejet starter. Slettede øl ryddes væk i starten af næste drej.

### Indstillinger og udseende
- `S.look` har `bg`, `acc`, `pat` og `fx`. Mulighederne står i `LOOK`, og `lookOf(k)` giver det gyldige valg eller standarden. `applyLook()` sætter `data-bg`, `data-acc` og `data-pat` på `<html>` og farven i `theme-color`. Standardvalget fjerner attributten, så siden uden valg er præcis som før.
- **Baggrund:** Hver `[data-bg=…]`-regel sætter `--nv`, `--nv2`, `--nv3`, `--sky`, `--ln` og `--nvr` (baggrundsfarven som tre tal). Reglen gælder også inde i `.hero`, `.bar`, `.nav` med flere, som ellers låser farverne. Gennemsigtige lag skrives som `rgb(var(--nvr)/.55)`.
- **Farver:** `[data-acc=…]` sætter `--sun`, `--pk` og `--gl` og står efter højtidernes regler, så et valg vinder over højtiden.
- **Mønster:** `[data-pat=…] body` lægger et svagt mønster som `background-image`.
- **Bobler:** `fx` er en ny slags, `bubbles`, i den samme motor som sne og konfetti (`spawn`, `tick`). Højtidens egen effekt går forud.
- `settingsView()` tegner siden. Knapperne bruger `data-look="bg:skov"`, `data-seas` og `data-setlang`. De hedder ikke `data-season` og `data-lang`, fordi de navne allerede bruges af stilarket og sprogmenuen.
- `cuRun()` får tal med `data-cu` til at tælle op, når en side vises første gang. `burst(x, y, n)` kan nu lave et lille drys med få prikker.

### Ingen hop under indlæsning (CLS)
- `#app` har `min-height:100svh`, så sidefoden ikke står øverst, før første side er tegnet.
- `history.scrollRestoration="manual"` sættes i det lille script i `<head>`. `route()` scroller selv: til toppen, eller til `#alle` to billeder efter, at indholdet er tegnet.
- `test_site.py` måler CLS på fem sider med en telefon, der er gjort 4 gange langsommere, og kræver under 0,1.

### Loading screen
- `#load` står først i `<body>`, så den bliver vist, før scriptet er læst. `loadDone()` kaldes efter første `route()` og fjerner den, tidligst 0,9 sekund efter at siden blev åbnet.
- Den har `pointer-events:none`, og en CSS-animation skjuler den efter 6 sekunder, hvis scriptet skulle fejle.
- Et lille script lige efter stilarket læser `look` fra `localStorage` og sætter `data-bg`, `data-acc` og `data-pat`, før noget bliver tegnet. `applyLook()` sætter dem igen senere.
- Skal en anden loading screen bruges, skiftes kun `#load`, klasserne `ld…` og de to keyframes `ldtap` og `ldud`.

### Skift af logo (`tools/logo-ud.py`)
- `python3 tools/logo-ud.py 56` tegner logo nr. 56 med `tools/logoer.py` og skriver `img/favicon.svg`, `img/logo.svg`, `img/icon-192.png`, `img/icon-512.png`, `img/icon-maskable.png`, `img/apple-touch-icon.png`, Androids `mipmap-*/ic_launcher*.png`, farven `icon_bg` i `values/styles.xml`, `desktop/build/icon.png` og fliserne i `desktop/build/appx/`.
- `--vis` skriver det hele til `/tmp/logo-vis` og laver et samlet billede, `ark.png`, uden at røre repoet.
- Det ensfarvede Android-ikon laves ved at tegne motivet i hvidt på sort og bruge lysstyrken som gennemsigtighed.
- Bagefter skal versionen i `sw.js` hæves, og apps skal bygges igen.

### Besøgstæller
- `sbVisit()` kalder `besoeg()` i databasen én gang, hver gang siden åbnes. Et sideskift inde på siden tæller ikke. Svaret ligger i `VIS` (i alt, i dag, første dag) og gemmes ikke på enheden. Svarer databasen 404 (005 ikke kørt), gemmes tidspunktet i `olrating-vis404`, og der spørges ikke igen den næste time.
- `supabase/005-besoeg.sql` laver tabellen `site_visits` (én række pr. dag) og funktionerne `besoeg()` (læg 1 til og svar) og `besoeg_tal()` (kun læs). Tabellen kan ikke læses eller ændres direkte. Dagen regnes i dansk tid.
- Findes funktionen ikke, sker der ingenting: Om viser tre tal i stedet for fem, og widgets viser en streg.
- Alle kan kalde `besoeg()`, så tallet kan pustes op. Det er et tal til pynt, ikke en måling.

## Android (`android/`)
- **Links ud af appen:** `shouldOverrideUrlLoading` åbner kun `https:`, `http:`, `mailto:`, `geo:` og `tel:`, og kun i apps med `CATEGORY_BROWSABLE`.
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
- **Links ud af programmet:** `openOut()` åbner kun `https:`, `http:` og `mailto:` i systemet. Andre slags links bliver ignoreret.
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
- **Filnavne i lageret:** `sbImg(v, oid)` bruger nøglen fra IndexedDB (`i…`), når billedet ligger der. Ligger billedet som tekst (`data:`), fordi IndexedDB ikke virker, bygges navnet af billedets indhold plus `oid` (øllens eller bedømmelsens id). Uden id ville to ting med samme billede dele én fil, og sletning af den ene ville fjerne den andens billede.
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

**Tilgængelighed (`tests/axe.py`):** Kører axe-core over 25 sider på telefon og pc, på dansk og engelsk, efter WCAG 2.2 AA og axe's egne gode råd. Kræver `npm install --no-save axe-core@4`. Kontrast er slået fra dér, fordi `kontrast.py` dækker den. Kører på GitHub ved hver ændring.

**Overskriftsniveauer:** `headLevels()` køres efter hver `route()`. Springer en side et niveau over (fx fra `h1` direkte til `h3`), får overskriften det rigtige niveau med `aria-level`. Bokse ved siden af hinanden får samme niveau.

**Klik på alt (`tests/klik.py`):** Lægger samme eksempeldata ind som den engelske test og åbner 27 sider på telefon. På hver side trykkes én gang på hver slags knap (knapper med samme `id` eller samme `data-`felter tælles som én), hver gang på en frisk side. Giver et tryk en fejl i JavaScript eller i konsollen, står siden og knappen på listen. Fanger knapper, som ingen anden test trykker på (fx filtrene, Sammenlign, lysboksen og Overrask mig). Tager omkring fire minutter og kører på GitHub ved hver ændring.

**Layout (`tests/layout.py`):** Køres, når noget på siderne flyttes. 25 sider i 320, 360, 390 og 1280 px, på dansk og engelsk: vandret scroll, knapper oven i hinanden (hver linje af et link for sig), knapper uden for skærmen og trykflader under 24 × 24 px på telefon. Undtaget er links midt i en sætning, felter med en større etiket og knapper i en række, der kan swipes til siden. Tager omkring tre minutter.

**To faner:** `addEventListener('storage', …)` tager det, en anden fane gemmer, ind i `S`, så den næste `save()` ikke overskriver det. Skriver man i en formular (`dirty`), tegnes siden ikke igen før næste sideskift.

**Fokus efter et valg:** `softRoute()` sætter fokus tilbage på den knap, der blev trykket på: efter `id`, ellers efter knappens første `data-`felt.

**Kontrast (`tests/kontrast.py`):** Køres, når farver, baggrunde eller temaer ændres. Den går 14 sider igennem i 390 og 1280 px i alle 30 kombinationer af baggrund og farver og finder for hver tekst den nærmeste baggrundsfarve, også gennem gennemsigtige lag. Den ender med `ALT OK` eller en liste med `SVAG`. `python3 tests/kontrast.py nat std` måler kun én kombination. Den er ikke med i de tre faste test, fordi den tager omkring fem minutter. På GitHub kører den sammen med `layout.py` i jobbene for WebKit og Firefox, og begge kan køres med `BROWSER=webkit` eller `BROWSER=firefox`.

Tilgængelighed er tjekket med axe-core (WCAG 2 A og AA) på alle sider i begge temaer. Det tjek ligger ikke i repoet, fordi det kræver en ekstra pakke, men kan gentages med `npm install axe-core` og Playwrights `add_script_tag`.

Alle test bruger Playwright og en lokal server: `python3 -m http.server 8811 &`.

| Fil | Hvad | Rører den rigtige database? |
|---|---|---|
| `test_site.py` | Hele siden klikket igennem på pc (1280 px) og mobil (390 px): tilføj øl med foto, bedøm, ret, søg, del, delekort, genstande, temaer, backup, slet med fortryd, ryd alt, gendan, offline, filer og links | Nej |
| `test_sync.py` | To enheder deler data: øl, billeder, afvist redigering af andres øl, offline-kø, ingen gentegning mens man skriver, sletning med fortryd, byttur, smagning og fjendtlige data i databasen (indlejret kode og forkerte typer) | Nej |
| `test_en.py` | Den engelske version: alle sider og tilstande gås igennem på dansk og engelsk med stillestående ur. Testen fejler, hvis en tekst er ens i de to udgaver eller stadig har danske bogstaver, hvis en besked i koden (toast, confirm, prompt) mangler i ordbogen, hvis brugernes eget indhold bliver oversat, eller hvis en side får vandret scroll på mobil (390, 360 og 320 px) | Nej |
| `test_sql.js` | `supabase/003-konto-mails-enig.sql` og `004-mails.sql` afprøvet i en rigtig Postgres i hukommelsen (PGlite): hvem der må stemme, at man kun ser sine egne stemmer, flytning af data til en konto, mailvalg og køen med mails. Funktionen `supabase/functions/mails` køres mod den samme database med en efterlignet mailtjeneste: indhold på dansk og engelsk, højst én mail i timen, venner én gang om dagen, nyheder, fejl hos mailtjenesten og afmelding. Kræver `npm install --no-save @electric-sql/pglite` | Nej |
| `mock_supabase.py` | Efterligning af Supabase i hukommelsen, som de to test ovenfor bruger | Nej |
| `e2e_supabase.py` | Det samme forløb mod den rigtige database, inkl. forsøg på at rette andres data direkte gennem API'et. Opretter data med TEST i navnet og sletter dem igen | **Ja** |

- **Service worker i test:** Playwright kan ikke altid fange netværkskald fra en side, der styres af en service worker (set i WebKit). Derfor kører alle test med `service_workers='block'`. Den ene undtagelse er offline-tjekket i `test_site.py`, hvor siden får at vide, at den er offline, så den ikke prøver at synkronisere.
- **Andre browsere:** `BROWSER=webkit python3 tests/test_site.py` kører testen i Safaris motor (kræver `python -m playwright install webkit`). På GitHub kører alle tre test også i WebKit og i Firefox (`BROWSER=firefox`). De to job bliver røde, hvis noget fejler, men stopper ikke resten af kørslen, fordi browserne på Linux ikke er helt de samme som på en telefon. I Firefox springes tjekket uden net over, fordi testværktøjet dér afviser navigation uden net, før service workeren bliver spurgt.
- **GitHub Actions (`test.yml`):** `test_site.py`, `test_sync.py` og `test_en.py` kører ved hver ændring af siden. `e2e_supabase.py` kører kun ved manuel start eller når commit-beskeden indeholder `[database-test]`.
- Byggemiljøet, hvor koden skrives, kan ikke selv nå Supabase. Derfor køres testen mod den rigtige database på GitHub.

## Manifest-id og genveje
`manifest.webmanifest` har `"id": "./"`, så browseren kender den installerede app igen, selv hvis `start_url` ændres. Genvejene (hold fingeren på ikonet) er: Tilføj øl, Toplisten, Genstand-tæller og Lykkehjulet.

## Stregkode-opslag (Open Food Facts)
`offLookup(code)` i `index.html` kører, når en stregkode scannes (`#scanAdd`), skrives i `#bCode` (600 ms efter sidste tast) eller kommer fra scanneren på forsiden (`F.code`). Den spørger kun, når kontrolcifret passer (`eanOk`), når øllen ikke allerede findes med den kode, og én gang pr. nummer. Kaldet er `GET https://world.openfoodfacts.org/api/v2/product/<kode>.json?fields=…`. Kun tomme felter udfyldes. Stil gættes ud fra `categories_tags` (`offStyle`), størrelse ud fra `quantity` og `packaging_tags` (`offSize`). Billedet hentes fra `images.openfoodfacts.org` og gøres mindre med `resize()` som et billede, man selv har valgt. `pending.bImgOff` husker, at billedet kom derfra, og øllen gemmes med `imgBy:'off'` (bevares af `cleanBeer`). Øllens side viser så kredit og link. Vælger man selv et billede, slettes mærket. CSP'ens `connect-src` tillader de to adresser. Alt fra svaret sættes som `value`/`textContent`, aldrig som HTML.

## Hvem må rette en bedømmelse
`myRev(r)` er sand, når bedømmelsen er lavet på enheden (`mineObj`: ingen `owner` endnu, eller `owner` er enhedens bruger-id) og enten står under dit navn eller har dit bruger-id som `owner`. Den styrer Ret/Slet i `revRow()`, linjen "Du har allerede bedømt den" på øllens side og listen på Min profil (`myList`). Databasen tillader stadig kun ændringer fra ejeren (RLS), så knapperne er kun en hjælp.

## Scanneren
`scanCode()` åbner kameraet i `#scan`. Har browseren `BarcodeDetector` med `ean_13` (Android, Chrome på Mac), bruges den. Ellers hentes `js/scan.js` (`loadScanLib()`), som giver `window.olScan(imageData)`: hvert 150. ms tegnes et billede fra videoen (højst 800 px bredt) på et canvas og læses. Koden renses til cifre. `scanDone` nulstilles, før `stopScan()` kaldes, ellers svarer løftet `null` (det var fejlen, der gjorde, at scanneren aldrig virkede).

`js/scan.js` bygges med `sh tools/byg-scanner.sh` (Node): esbuild samler læserne `MultiFormatUPCEANReader` og `Code128Reader` fra `@zxing/library` 0.23.0 (Apache-2.0). Kun de filer kommer med, så den er 70 kB i stedet for 360 kB. Testen bruger Chromiums falske kamera (`--use-file-for-fake-video-capture`) med en Y4M-video, som `ean_y4m()` i `test_site.py` laver.

## Sprog i widgets
- **Android:** Alle tekster i widgets ligger i `res/values/strings.xml` (dansk) og `res/values-en/strings.xml` (engelsk), også teksterne i layoutfilerne. Android vælger selv efter telefonens sprog. Tekster med tal bruger pladsholdere (`%1$s`, `%1$d`), fx `w_footer`.
- **Windows og Linux:** Siden sender `lang` med i widget-data. `desktop/widget.html` har en lille ordbog (`EN`) og `T()`, der bruges, når `lang` er `en`. Tal skrives med punktum på engelsk.
