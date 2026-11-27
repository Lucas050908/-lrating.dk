# Ændringslog

Nyeste øverst. Hver ny ting skrives her i samme commit, som den laves i.

## 2026-11-26

## 27-11-2026

### Morgen (07:56–08:08): gennemgang af gårsdagens kode
- **Rettet: Navne kunne få siden til at gå ned.** Hed en smager, et bryggeri, en stil eller et smagsord fx `constructor`, `toString` eller `__proto__`, gik forsiden, Venner og Beer buddies ned for alle. Det skyldtes, at navnene blev brugt som nøgler i almindelige JavaScript-objekter, hvor de navne allerede findes. 15 steder bruger nu objekter uden den slags indbyggede navne (`Object.create(null)`).
- **Rettet: Lykkehjulet.** Blev siden tegnet igen midt i et drej (fx når nye data blev hentet, eller en anden fane gemte), kunne øllene på hjulet skifte, så vinderen ikke var den, pilen pegede på. Nu står øllene stille, mens hjulet drejer, og mens resultatet vises. En øl, der er slettet imens, ryddes væk ved næste drej. Knappen er låst, mens hjulet drejer.
- **Tjekket og i orden:** To faner på samme side gemmer ingenting af sig selv, så de kan ikke skubbe hinanden i en løkke. Billeder til widgets hentes med `crossOrigin`, så de også virker fra databasen.
- **Test:** 2 nye tjek i `test_site.py`. Det ene fejler på den gamle udgave af siden, så det ses, at det fanger fejlen.

### Morgen (06:30–06:32): layout og kontrast også i Safaris motor og Firefox
- **GitHub:** Jobbene for WebKit og Firefox kører nu også `tests/layout.py` og `tests/kontrast.py`. Før blev de to tjek kun kørt i Chromium.
- `tests/kontrast.py` kan nu køre i en anden browser med `BROWSER=webkit` eller `BROWSER=firefox`, ligesom de andre test.
- Alle commits fra torsdag aften er grønne på GitHub i alle tre browsere.

### Aften (22:45–22:46): flere tjek af det, der sker, når noget mangler
- **Test:** 2 nye tjek i `test_site.py`. Med "mindre bevægelse" slået til er der ingen loading screen og intet drys, og lykkehjulet viser resultatet med det samme. Uden besøgstæller i databasen sender siden ingen besøgstal til widgets, og Om viser tre tal i stedet for fem.
- De engelske tekster til Beer buddies, Lykkehjulet, Indstillinger og Siden i tal er læst igennem. Der var ikke noget at rette.

### Aften (22:37–22:39): widgets gennemgået, tjekliste og Store-tekster
- **Android-widgets gennemgået linje for linje.** Rettet: Billedet i *Ugens øl med billede* kunne blive op til 480 × 480 punkter. Android afviser en widget-opdatering på over ca. 1 MB, og så ville widgetten ikke blive opdateret. Billederne er nu højst 288 × 288, som er den størrelse, siden sender. Hjørnerne skaleres med.
- Billederne gemmes nu først i en midlertidig fil og omdøbes bagefter, så en widget aldrig kan læse et halvt skrevet billede.
- Alle id'er, tekster og filer, som koden henviser til, er tjekket mod layout-filerne. Appen er stadig ikke prøvet på en rigtig telefon.
- **Tjekliste på 2 minutter** til at prøve de nye widgets står i `docs/DRIFT.md`.
- **Microsoft Store:** Teksterne på dansk og engelsk i `docs/STORE.md` nævner nu kommatal, Beer buddies, Lykkehjulet, design og farver, og widgetten med billeder.

### Aften (22:12–22:37): små skærme, tastatur og to faner
- **Nyt værktøj, `tests/layout.py`:** Det går 25 sider igennem i 320, 360, 390 og 1280 px, på dansk og engelsk, og finder vandret scroll, knapper oven i hinanden, knapper uden for skærmen og trykflader under 24 × 24 px på telefon (WCAG 2.2).
- **Rettet, fordi det fandt det:** Afkrydsningen *Alkoholfri* på Tilføj øl lå inde i etiketten til alkoholprocenten, så et tryk på teksten flyttede markøren til procentfeltet i stedet for at krydse af. Den har nu sin egen etiket. Skyderne i smagsprofilen var 16 px høje og er nu 28 px. Bryggeri-knappen på en øls side og linket "Se hele toplisten" har fået større trykflade.
- **Tastatur:** Når man trykker på en valgknap (fx en baggrund i Indstillinger eller en gruppe på Lykkehjulet), bliver fokus nu på knappen. Før hoppede det til toppen af siden, fordi siden bliver tegnet igen.
- **To faner:** Har man siden åben i to faner, tager den ene nu de ændringer med, som den anden gemmer. Før kunne den sidste fane, der gemte, slette den andens ændringer, fx en ny ønskeliste.
- **Målt:** Første side vises efter ca. 0,76 sekund på en telefon, der er gjort 4 gange langsommere, mod 0,87 sekund i morges. `index.html` er vokset fra 55 til 96 kB pakket i løbet af dagen på grund af de nye funktioner. Den engelske ordbog hentes kun, når man vælger engelsk.
- **Kendt:** Indtil `supabase/005-besoeg.sql` er kørt, viser browserens konsol én linje med "404" for besøgstælleren, hver gang siden åbnes. Siden virker som den skal. Linjen forsvinder, når filen er kørt.
- **Test:** 2 nye tjek i `test_site.py` og 1 i `test_sync.py`.

### Aften (21:12–21:32): kontrasten er målt i alle 30 kombinationer
- **Nyt værktøj, `tests/kontrast.py`:** Det åbner 14 sider i to skærmstørrelser i hver af de 30 kombinationer af baggrund og farver og måler kontrasten mellem al tekst og dens baggrund mod WCAG AA (4,5:1, og 3:1 for stor tekst).
- **Rettet, fordi målingen fandt det:** Bogstavet i de runde navnemærker stod hvidt på en for lys farve (ned til 2,5:1). Farven er gjort mørkere. Tallet 3 i top 5 på forsiden er gjort fedt. Knappen "På din ønskeliste" har nu mørk tekst på den lyserøde baggrund i stedet for hvid (3,4:1 før).
- **Resultat:** Ingen tekst er under kravet i nogen af de 30 kombinationer.
- **Det måler den ikke:** tekst oven på fotos, og tekst, hvor baggrunden er tegnet med `::before`. Karakter-ringen på en øls side er derfor undtaget.

### Aften (21:05–21:09): loading screen og værktøj til logoskift
- **Loading screen:** Når siden åbnes, vises navnet og en fadølsbjælke, der fyldes med skum forrest (nr. 7 af de 12 forslag). Den er væk, når første side er tegnet, dog tidligst efter 0,9 sekund, så den ikke bare blinker.
- Den spærrer ikke for tryk, den fjerner sig selv efter 6 sekunder, hvis noget går galt, og den vises ikke for dem, der har bedt om mindre bevægelse.
- **Den valgte baggrund** sættes nu, før siden bliver tegnet, så siden ikke først blinker i den mørkeblå.
- **`tools/logo-ud.py`** sætter ét af de 200 logoer ind alle steder med én kommando: siden, Android-ikonerne (også det runde og det ensfarvede), Windows/Linux og fliserne til Microsoft Store. `--vis` viser resultatet uden at ændre noget. Der er ikke skiftet logo endnu.
- **Test:** 1 nyt tjek i `test_site.py`.

### Aften (20:47–21:01): indstillinger med design og farver, og små effekter
- **Indstillinger** er en ny side (`#indstillinger`, under Mere i menuen, i bunden af siden og fra Min profil). Alt på den gemmes kun på enheden.
- **Design og farver:** Man kan vælge baggrund (Nat, Fjord, Skov, Aften, Stout, Kul), farver (Solnedgang, Hav, Skov, Bær, Guld) og mønster (Ingen, Bobler, Bølger, Stjerner), og man kan slå bobler til, der stiger op bag siden. Siden ser ud som før, indtil man selv vælger noget andet.
- **Tema efter højtid** og **sprog** kan også vælges på Indstillinger. De to valg står stadig i bunden af siden.
- **Små effekter:** Tallene under *Siden i tal* tæller op. Fem stjerner giver et lille drys, og det gør det også at følge en smager. Hjertet på ønskelisten banker, når man trykker, og karakteren på et øl-kort vipper, når man holder musen over. Fem hurtige tryk på logoet giver en hemmelig skål.
- Alle effekter er slået fra, hvis man har bedt sin enhed om mindre bevægelse.
- **Teknik:** Baggrundsfarven i gennemsigtige lag (menuen, forsidebilledet, mærkater) følger nu den valgte baggrund gennem `--nvr`.
- **Test:** 6 nye tjek i `test_site.py`, og Indstillinger er med i tjekket af den engelske udgave. Alle tre test består (179, 85 og 14 tjek).

### Aften (20:26–20:46): widgets med billeder, og siden i tal
- **Billeder i widgets (Android):** Ugens øl, Noget for dig og Seneste bedømmelser viser nu et billede af øllen. Der er en ny widget, **Ugens øl med billede**, med et stort billede.
- **Ny widget: Siden i tal** (Android) med besøg i alt og i dag, antal øl, bedømmelser og smagere.
- **Windows og Linux:** Widgetten viser små billeder af øllene og har en ny fane, **Siden**, med de samme tal. Fanen Seneste hedder nu Nyt, og widgetten er blevet lidt bredere.
- **Besøgstæller:** Siden tæller, hvor mange gange den bliver åbnet. Der gemmes kun ét tal pr. dag, ikke hvem der besøger siden, og ikke noget på den besøgendes enhed. Tallet står under *Siden i tal* på Om, og Privatliv er opdateret.
- **Skal gøres af Lucas:** Kør `supabase/005-besoeg.sql` i Supabase. Tælleren starter på 0 den dag. Indtil da viser Om og widgets ikke noget besøgstal.
- **Apps:** Android-appen og programmet til Windows og Linux skal hentes igen, før de nye widgets er der. De er ikke prøvet på en rigtig telefon eller pc, kun bygget på GitHub.
- **Test:** 3 nye tjek i `test_site.py`, 4 i `test_sync.py` og 5 i `test_sql.js`.

### Aften (20:15–20:40): Lykkehjulet
- **Lykkehjulet** er en ny side (`#hjul`): Kan man ikke vælge, drejer man hjulet, og det vælger én øl, man kan smage og bedømme.
- Man vælger selv, hvilke øl der skal på hjulet: øl man ikke har smagt, alle øl, ønskelisten, toppen (4,0 og derover) eller de alkoholfri. Hjulet viser op til 10 øl ad gangen, og "Nye øl på hjulet" trækker 10 andre.
- Siden starter på "Ikke smagt", så hjulet først og fremmest foreslår noget nyt.
- **Ansvarligt:** Under hjulet står, at det er til at finde noget nyt at smage og ikke til at drikke mere, med Sundhedsstyrelsens anbefalinger, link til Genstand-tælleren og nummeret til Alkolinjen.
- Har man slået bevægelse fra på sin enhed, vælger hjulet uden at dreje.
- Siden ligger i menuen under Mere, i bunden af siden, på forsiden og under Nyt på siden.
- **Test:** 6 nye tjek i `test_site.py`, og siden er med i tjekket af den engelske udgave.

### Aften (20:06–20:14): 200 logoer i fem stilarter
- **Logoer:** `img/logoer/200/` har 200 forslag: 40 motiver, hver tegnet i fem stilarter (nat, solnedgang, lys, guld og fjord). Filerne hedder `001` til `200`, og fem numre i træk er det samme motiv.
- Motiverne er tegnet om, så de bruger de samme få farver, og skummet har en mørk kant på lys og gul baggrund, så det kan ses.
- `tools/logoer.py` tegner alle 200 filer igen: `python3 tools/logoer.py img/logoer/200`.
- De 50 første forslag ligger stadig i `img/logoer/`. Ingen af logoerne er taget i brug endnu.

### Aften (19:57–20:10): 40 forslag mere til logo, 50 i alt
- **Logoer:** `img/logoer/` har nu 50 forslag, nummereret `01` til `50`. De nye er blandt andet flaske, krone, skjold, medalje, tønde, hane, byg, krans, måler, taleboble, lup, dåse, kompas, bølge, drikkehorn, smagebræt, stjernebillede, maskot og stempel.
- Nr. 10, 49 og 50 har tekst i sig. De viser teksten med den skrifttype, enheden har, så de skal laves om til streger, hvis ét af dem bliver valgt.
- Ingen af dem er taget i brug endnu.

### Aften (19:49–20:00): 10 forslag til nyt logo
- **Logoer:** Der ligger 10 forslag til logo som SVG i `img/logoer/` (stjernekapsel, Ø-mærke, krus, solnedgang i glasset, fem stjerner, humle, skål, ølnål, sekskant og ordmærke). De er tegnet i sidens egne farver.
- Ingen af dem er taget i brug endnu. Siden og apps bruger stadig det nuværende logo, indtil ét er valgt.

### Aften (19:30–19:56): Beer buddies
- **Beer buddies** er en ny side (`#buddies`), der finder dem, der smager som dig. Den sammenligner dine karakterer med de andres på de øl, I begge har bedømt, og viser jeres match i procent.
- Hvert match viser, hvor mange øl I har til fælles, hvilken øl I er mest enige om, hvilken I er mest uenige om, og et tip: en øl, din buddy kan lide, som du ikke har bedømt.
- Der skal mindst to fælles øl til et match. Dem, du ikke har nok til fælles med endnu, står under "Flere smagere" med et forslag til, hvilken øl du kan bedømme.
- Man kan følge en buddy direkte fra siden. Siden ligger i menuen under Mere, i bunden af siden, på forsiden og som link fra Venner.
- **Test:** 4 nye tjek i `test_site.py`, og siden er med i tjekket af den engelske udgave.

### Aften (19:26–19:44): karakterer med kommatal
- **Kommatal:** Man kan nu give fx 3,7 i en kategori. Et tryk på en stjerne giver et helt tal, og med − og + retter man i trin på 0,1. Den sidste stjerne bliver delvist fyldt, og tallet står ved siden af.
- Det virker i bedømmelsen af en øl, når man retter en bedømmelse, og når man stemmer i en smagning.
- På mobil står tallet og knapperne på linjen med navnet, og stjernerne på linjen under.
- **Test:** 4 nye tjek i `test_site.py` og 1 i `test_sync.py`.

### Aften (17:34–17:42): Resend er forbundet, og domænet er oprettet
- **Resend:** Lucas har forbundet Resend, og domænet `xn--lrating-p1a.dk` er oprettet dér i region EU. Resend tog imod domænet med ø, så det usikre punkt i guiden er væk.
- **Guiden (`docs/KONTO.md`)**, punkt 1.2, er rettet: Der er 4 DNS-linjer, som skal ind hos one.com, før domænet bliver godkendt.

### Eftermiddag (15:00–15:13): status ved dagens afslutning
- **Den rigtige database kl. 15:00:** 22 af 22 tjek bestod. Der ligger 1 øl og 1 bedømmelse. Siden svarer på https, og versionen på nettet er den samme som i koden (v51). `003`, `004` og funktionen `mails` er ikke sat op endnu.
- **Browsere kl. 15:25:** Chrome, Safaris motor (WebKit) og Firefox består alle tre test på GitHub. Ét tjek fejlede først i Firefox (flere stemmer på samme telefon i en smagning). Stemmen nåede ikke frem inden for testens ventetid. Efter at testen venter længere, består det. I Firefox springes tjekket uden net over.
- **Guiden (`docs/KONTO.md`)** siger tydeligere, at konto og mails kun er prøvet mod en efterligning, og at `003` skal køres i den nyeste udgave.
- **Rettet her i loggen:** Testen mod den rigtige database har 22 tjek, ikke 23.
- **README** nævner flaget til sprogskift og funktionen, der sender mails.

### Eftermiddag (14:54–14:57): Firefox består
- **Firefox:** Efter rettelserne i testen var der to ting tilbage, og begge ligger i testværktøjet: Firefox afviser al navigation uden net, før service workeren bliver spurgt, så det tjek springes over i Firefox, og en afbrudt forbindelse giver en besked med en anden ordlyd end i Chrome.
- **Status for browsere:** Chrome, Safaris motor (WebKit) og Firefox kører alle tre test på GitHub ved hver ændring.

### Eftermiddag (14:32–14:41): første kørsel i Firefox
- **Resultat:** `test_en.py` bestod alt i Firefox. `test_site.py` og `test_sync.py` fejlede kun på to ting, som begge ligger i testen: testens eget billede var et afkortet JPEG, som Firefox melder fejl om, og tjekket uden net fejlede ved genindlæsning.
- **Rettet i testene:** Testbilledet er nu et gyldigt JPEG. Tjekket uden net prøver både at genindlæse og at åbne siden igen og skriver, hvad der skete.
- **Den rigtige database kl. 14:22:** 22 af 22 tjek bestod. Der ligger 1 øl og 1 bedømmelse. `003`, `004` og funktionen `mails` er ikke sat op endnu.

### Eftermiddag (14:09–14:18): også Firefox, og fejl i andre browsere kan ses
- **Safaris motor:** Efter rettelsen består alle tre test i WebKit, også tjekket ved 360 og 320 px.
- **Firefox:** De tre test kører nu også i Firefox på GitHub.
- **Synlige fejl:** Fejler noget i WebKit eller Firefox, bliver det job rødt, men resten af kørslen fortsætter.

### Eftermiddag (13:56–14:05): de smalleste telefoner
- **320 px:** To knapper gjorde siden for bred på de smalleste telefoner: "Swipe på andres bedømmelser" på Min profil og knappen på Afmeld mails på engelsk. De knækker nu over to linjer.
- **Test:** `test_en.py` tjekker nu alle hovedsider for vandret scroll ved 390, 360 og 320 px på engelsk og ved 320 px på dansk (14 tjek).

### Eftermiddag (13:25–13:55): fejl fundet i Safaris motor og småting på små skærme
- **Tilføj øl kunne få vandret scroll i Safari:** Det skjulte filfelt til billedet lå for enden af hjælpeteksten, og Safari regnede dets indhold med i sidens bredde. Nu ligger det i hjørnet af billedfeltet og fylder 1 px. Fejlen blev fundet af den nye test i WebKit og kunne ikke ses i Chrome.
- **Billedfeltet viser nu en ramme,** når man kommer til det med tastaturet.
- **Sidefoden:** Mailadressen stak ud af sin kolonne på mobil. Nu knækker den.
- **Meget smalle telefoner (320 px):** Logoet er lidt mindre, og sprogknappen viser kun flaget, så de ikke støder sammen.
- **Test:** `test_sync.py` og `test_site.py` består nu alle tjek i WebKit. `test_en.py` skriver, hvilket element der gør siden for bred. Det engelske tjek køres først i WebKit-jobbet.

### Eftermiddag (13:10–13:21): første kørsel i Safaris motor
- **Resultat:** `test_site.py` bestod alle 143 tjek i WebKit. `test_en.py` fandt én ting: siden Tilføj øl får vandret scroll på mobil på engelsk i WebKit. Testen skriver nu, hvilket element der stikker ud, så det kan rettes.
- **Rettet i testene:** `test_sync.py` kørte med service worker slået til. I WebKit gik kald fra siden så uden om den efterlignede database og ud på nettet. Nu er service workeren slået fra i den test, og i den ene test, hvor den skal være med (offline), tror siden, at den er offline, og synkroniserer ikke.

### Eftermiddag (13:02–13:02): test i Safaris motor
- **Ny test på GitHub:** De tre test af siden kan nu køre i WebKit, som er motoren i Safari på iPhone (`BROWSER=webkit`). Jobbet "Siden i Safaris motor" kører ved hver ændring og stopper ikke resten, hvis noget fejler. Det er første skridt mod at vide, om siden virker på iPhone uden at have en i hånden.

### Eftermiddag (12:55–13:01): loft over mail-køen og småting
- **Databasen (`supabase/003`):** Højst 200 ventende mails pr. bruger, så ingen kan fylde en andens kø og indbakke op. Bedømmelsen eller tilmeldingen bliver gemt som altid.
- **Min profil:** "Flest uenige" bliver ikke vist, når det er den samme bedømmelse som "Flest enige".
- **Nyt på siden** nævner prikken ved nye stemmer.
- **Test:** 2 nye tjek i `test_sql.js` (81 i alt).

### Middag (12:36–12:52): se når nogen har stemt på dine bedømmelser
- **Gul prik ved nye stemmer:** Har nogen swipet på dine bedømmelser, siden du sidst kiggede, får Min profil en lille prik. På mobil sidder den også på menu-knappen.
- **Boksen "Er andre enige med dig?"** viser nu "+3 nye stemmer siden sidst" og hvilken af dine bedømmelser flest er enige i, og hvilken flest er uenige i, med link til øllen.
- **Test:** 2 nye tjek i `test_sync.py`.

### Middag (12:26–12:33): knapperne på Enig eller uenig?
- **Knapperne Uenig, Spring over og Enig** står nu på én linje også på små skærme. Før knækkede "👎 Uenig" over to linjer på en telefon. Tjekket på 390 og 320 px på dansk og engelsk.

### Middag (12:25–12:25): svar-adresse på mails
- **Funktionen `mails`** kan få en valgfri svar-adresse (`MAIL_REPLY_TO` under Secrets i Supabase), så svar på en mail havner i en indbakke, nogen læser. Guiden er opdateret, og `test_sql.js` tjekker det (79 tjek).

### Middag (12:12–12:24): navn, ønskeliste og følger følger med kontoen
- **Kontoen har mere med:** Logger man ind på en ny telefon, kommer ens navn, ønskeliste og dem, man følger, med. Det, der lå på den nye enhed i forvejen, bliver lagt til. Fjerner man noget på én enhed, forsvinder det også på de andre. Genstand-tælleren bliver på enheden.
- **Databasen:** `supabase/003-konto-mails-enig.sql` har fået tabellen `konto_data` (én række pr. konto, som kun kontoen selv kan læse). Er 003 kørt før kl. 12:24 i dag, skal den køres igen.
- **Privatliv** og teksten i Konto-boksen fortæller, hvad der gemmes på kontoen.
- **Test:** 4 nye tjek i `test_sync.py` med to enheder på samme konto og 7 nye i `test_sql.js` (78 i alt). Testen mod den rigtige database skriver nu også, hvis 003 er kørt i en ældre udgave.
- **Drift:** `002-slet-billeder.sql` er kørt. Det er bekræftet af testen mod den rigtige database kl. 12:00 (22 af 22 tjek).

### Middag (12:00–12:08): småting efter mail-delen
- **Afmeld-siden husker svaret,** hvis man fx skifter sprog, efter man har afmeldt.
- **Flueben** ved lange tekster (mailvalg på Min profil) blev klemt og var ikke lige store. De har nu alle samme størrelse.
- **Guiden (`docs/KONTO.md`)** har fået en genvej: Login kan prøves med ens egen mail, før mailtjenesten er sat op.

### Middag (11:35–11:57): mails om opdateringer
- **Mails er bygget (skjult, indtil de er sat op):** Brugere med konto kan få mail, når nogen bedømmer deres øl, når en, de følger, bedømmer en øl, når nogen melder sig til deres byttur eller stemmer i deres smagning, og når der er nyt om siden. Sker der flere ting, samles de i én mail. Man får højst én mail i timen, og "ven har bedømt" højst én gang om dagen.
- **Mailen** er på dansk eller engelsk efter brugerens sprog, har links til øllen, turen eller smagningen, og findes både med og uden formatering.
- **Afmeld mails (`#afmeld-…`):** Ny side, som linket nederst i hver mail fører til. Et tryk slår alle mails fra, også uden login. Der sker først noget, når man trykker, så et mailprogram, der åbner linket for at tjekke det, ikke afmelder nogen ved en fejl.
- **Nyheder fra ejerne:** Skriv en række i tabellen `mail_news` i Supabase, læs den igennem, og sæt flueben i `send`. Så går den til alle, der har slået nyheder til.
- **Databasen (`supabase/004-mails.sql`):** Reglerne for udsendelsen står i databasen (`mail_hent`, `mail_faerdig`, `mail_afmeld`), og et job kalder funktionen hvert 10. minut, når der er noget at sende. Kaldet har en nøgle med, som kun databasen kender.
- **Funktionen (`supabase/functions/mails/index.ts`):** Sender gennem mailtjenesten Resend. Nøglen til Resend ligger som hemmelighed i Supabase og ikke i repoet.
- **Guide (`docs/KONTO.md`):** Hele opsætningen trin for trin: mailtjeneste, DNS-linjer hos one.com, mailskabelon med kode (`supabase/mail-skabelon.html`), indstillinger i Supabase og hvordan det prøves.
- **Test:** `tests/test_sql.js` afprøver nu også 004 og selve funktionen mod en rigtig Postgres i hukommelsen (71 tjek mod 32 før). `test_sync.py` tjekker afmeld-siden, og `test_en.py` går nu også konto-boksen og afmeld-siden igennem på engelsk.
- **Testen mod den rigtige database** (`e2e_supabase.py`) tjekker nu enig-stemmer, når 003 er kørt, og skriver, om 003, 004 og funktionen `mails` er sat op.
- **Oprydning:** Pythons mellemfiler (`__pycache__`) lå ved en fejl i repoet og er fjernet.
- **Rettet i testen:** `test_sync.py` kunne fejle på GitHub, fordi en anden åben enhed synkroniserede, mens databasen blev efterlignet uden tilføjelsen. Nu oplever kun den ene bruger det.

### Middag (11:12–11:32): Enig eller uenig? og konto
- **Enig eller uenig? (`#swipe`):** Ny side, hvor man swiper på andres bedømmelser som på Tinder. Til højre for enig, til venstre for uenig. Knapper og piletaster virker også, og der er Spring over og Fortryd.
- **Se hvem der er enige med dig:** Ved hver bedømmelse står der nu, hvor mange der er enige og uenige, og Min profil har boksen "Er andre enige med dig?" med den samlede procent.
- **Konto med kode på mail (skjult indtil videre):** Frivillig konto på Min profil. Man skriver sin mail, får en kode på 6 tal og er logget ind. Ens øl følger med på ny telefon, og man kan slå fire slags mails til. Den vises først for alle, når mail-delen er sat op. Den kan prøves på `#konto-test`.
- **Databasen (`supabase/003-konto-mails-enig.sql`):** Nye tabeller til stemmer, mailvalg og en kø med mails, og funktioner til at flytte data til en konto og slette en konto. Filen skal køres i Supabase.
- **Test:** 27 nye tjek i `test_sync.py` af swipe og konto på to enheder, og en ny test (`tests/test_sql.js`, 32 tjek), der afprøver SQL-filen i en rigtig Postgres i hukommelsen. Den kører også på GitHub.

### Formiddag (10:50–10:48): flere byer på kortet
- **Kortet over bryggerier** kender nu 310 danske byer og bydele mod 71 før, så langt flere bryggerier kan få en prik. Bl.a. Sæby, Støvring, Hvide Sande, Assens, Sorø, Gilleleje, Nexø og bydelene i København og Aarhus.
- **Nyt på siden** fortæller nu om dansk og engelsk.
- **Test:** Nyt tjek af, at alle byer i tabellen ligger inden for Danmark.

### Formiddag (10:27–10:38): bedre sprogskift
- **Ny sprogvælger:** Knappen i topmenuen viser nu et flag og DA eller EN og åbner en lille menu med Dansk og English.
- **Skiftet sker med det samme.** Før blev hele siden hentet igen, og man røg op til toppen. Nu skifter teksten på stedet med en blød overgang, og man bliver stående, hvor man var. Tekst, man er ved at skrive i en formular, bliver stående.
- **Vink til udlændinge:** Har browseren et andet sprog end dansk, norsk eller svensk, viser knappen det engelske flag og "English?".
- **Test:** Sprogskiftet bliver nu prøvet på 13 sider: uden genindlæsning, samme sted på siden, og tilbage til præcis den samme danske tekst.

### Formiddag (10:22–10:27): tre små ting
- **Smagning som billede:** Når resultatet er afsløret, kan det deles som et billede med aftenens vinder og resten af ranglisten.
- **Smagning ud fra ønskelisten:** Knappen "Brug min ønskeliste" fylder dine ønskede øl ind, når du opretter en smagning.
- **Min profil:** Egne bedømmelser vises 15 ad gangen med "Vis flere", så siden ikke bliver uendelig lang.

### Formiddag (10:21–10:22): Microsoft Store på engelsk
- **Tekster til Store på engelsk** står nu i `docs/STORE.md`, og de danske tekster nævner Årets øl, minder og de to sprog.
- **Nye skærmbilleder** på dansk (`store/`) og engelsk (`store/en/`), nu 7 af hver, med Årets øl og sprogknappen. De laves af `store/lav-skaermbilleder.py` og kan laves om, når siden ændrer sig. Eksemplerne er stadig opdigtede.

### Formiddag (10:15–10:13): hurtigere og pænere
- **Hurtigere med mange øl:** Min profil tog over et halvt sekund at åbne med 400 øl og 1.200 bedømmelser. Nu tager den omkring en fjerdedel af tiden. Listen over øl med gennemsnit bliver regnet ud én gang pr. side i stedet for én gang pr. bedømmelse.
- **Byttur:** Felterne til et nyt stop var så smalle på pc, at teksten i dem blev skåret af. De står nu i to rækker.
- **Ølkalender:** Mærket "I dag" stod oven i månedens navn og blev skåret af i kanten på mobil. Det står nu over månederne.
- **Widgets på engelsk:** Begrundelsen i widgetten "Noget for dig" følger nu sidens sprog. Resten af teksten i widgets er stadig dansk.
- Rettet i dokumentationen: Android-appen har 6 widgets, ikke 7.

### Formiddag (10:05–10:02): tilgængelighed i temaerne
- **Juletemaet var svært at læse:** Mørk tekst på de røde knapper og rød tekst på mørk baggrund havde for lav kontrast. Den røde farve er gjort lysere, så teksten kan læses. Det samme er rettet i en enkelt farve i temaerne J-dag, fastelavn og halloween og i ølkalenderens bjælke for juleøl.
- **Automatisk tjek af tilgængelighed** (axe, WCAG 2 A og AA) er kørt igen på 22 sider på dansk og engelsk, pc og mobil, og på 11 sider i alle 7 sæsontemaer. Der er ingen fund tilbage.
- **Forsiden:** Årets øl har fået sin egen flise under "Mere at udforske".
- **Test:** Den engelske test fejlede på GitHub, fordi ét browser-vindue i testen nåede den rigtige database. Nu bruger alle vinduer i de tre test den efterlignede database.

### Formiddag (09:25–09:42): lange ord og finpudsning af engelsk
- **Lange ord uden mellemrum** (fx et ølnavn på 45 tegn, som en anden bruger har skrevet) kunne gøre 14 af siderne bredere end skærmen på mobil. Nu bliver ordet delt, og overskrifter får en rigtig bindestreg, hvor telefonen kan.
- **Ugens øl på mobil:** Billedet og karakteren er lidt mindre, så lange navne som "Limfjordsporter" kan stå på én linje.
- **Enighed på Min profil** står nu i to linjer på smalle skærme, så navnet ikke bliver klemt.
- **Årets øl:** "den ene bedømmelse" og "1 øl" i stedet for "de 1 bedømmelse" og "1 forskellige øl".
- **Engelsk:** Flere tekster er oversat (bl.a. lysboksen, Vis flere, installér-knappen og slettede øl), og pladsholderen i tekstfelter bliver nu også oversat.
- **Test:** Nyt tjek med lange ord på alle sider (pc og mobil).

### Formiddag (08:45–09:19): engelsk version
- **Hele siden findes nu på engelsk.** Knappen EN i topmenuen skifter sprog, og valget kan også ændres i sidefoden. Dansk er stadig standard.
- Oversættelsen ligger i en ordbog for sig selv (`js/en.js`, ca. 700 tekster og 110 mønstre), som kun hentes, når man vælger engelsk. Den danske side er uændret.
- På engelsk skrives tal med punktum, datoer på engelsk og priser som DKK. Delebillederne bliver også engelske. Det, brugerne selv har skrevet, bliver ikke oversat.
- **Ny test (`tests/test_en.py`):** Går over 80 sider og tilstande igennem på begge sprog og fejler, hvis en tekst ikke er oversat. Den kører også på GitHub.
- Reglen om sprog i `CLAUDE.md` er opdateret: ny tekst skal også i den engelske ordbog.
- Formularerne gemmer nu stilart, størrelse og land med faste værdier, så data er ens på begge sprog.

### Formiddag (08:35–08:37): klar til Microsoft Store
- **Pakke til Microsoft Store:** GitHub bygger nu også en `.appx`-pakke af Windows-programmet. Den mangler kun de tre værdier fra Partner Center, som skal stå i `desktop/store.json`. Indtil da bygges en prøvepakke, der viser, at bygningen virker.
- **Ikoner til Store** i de størrelser, Microsoft kræver, ligger i `desktop/build/appx/`.
- `docs/STORE.md` er opdateret med, hvordan pakken bygges, og hvad der skal svares om `runFullTrust`.

### Formiddag (08:26–08:30): byttur som minde
- **Minder:** Når en byttur er slut, bliver den til et minde. Siden for turen viser "Sådan gik turen" med ruten, hvem der var med, og de øl, holdet bedømte den dag, med turens bedste øl øverst.
- **Del mindet som billede:** Et billede med dato, rute, hold og turens bedste øl.
- **Oversigten** over byture er delt i kommende ture og minder. Gamle ture er ikke længere grå.
- Mindet tæller kun øl, der er smagt og bedømt, og ikke hvor meget nogen har drukket.
- **Test:** 4 nye tjek af minder.

### Formiddag (08:11–08:18): Årets øl og topliste som billede
- **Årets øl:** Ny side (`#aarets`) med årets vinder, de næste på listen, årets bryggeri, årets stil, årets alkoholfri og årets nykommer. Kun bedømmelser fra året tæller, og en øl skal have mindst 2 bedømmelser for at være med, når der er øl, der har det. Siden ligger under Mere, i sidefoden og som link på Toplisten.
- **Del toplisten som billede:** Ny knap på Toplisten og på Årets øl, der laver et billede med de 5 bedste øl. Det deles på samme måde som delekortet for en enkelt øl.
- **Test:** 4 nye tjek af Årets øl og de to billeder.

### Morgen (07:48): altid mørk
- **Siden er nu altid mørk.** Før skiftede den selv til et lyst tema mellem kl. 7 og 17. Valget "Udseende" i sidefoden er fjernet, og et lyst tema, der var valgt tidligere, bliver ignoreret.

### Morgen (06:15–06:22): sidste test
- **Fuld test:** Begge testpakker er grønne, lokalt og på GitHub. Android-appen (med genveje og 6 widgets) og programmerne til Windows og Linux er bygget uden fejl og ligger klar til download.
- **Forhåndsvisningen i Claude** er opdateret til samme version som ølrating.dk. Download af backup og delekort virker ikke i forhåndsvisningen, kun på den rigtige side.
- Status over det, der venter, står i `docs/IDEER.md`.

### Nat (04:55–04:57)
- **Findes den allerede?** Når du skriver navnet på en ny øl, foreslår siden øl, der ligner og allerede findes, så du kan bedømme dem i stedet for at oprette en dublet. Den tåler stavefejl og kender også stregkoden.
- **Nyt på siden:** Ny side (`#nyt`) med en kort oversigt over de nyeste funktioner og links til dem. Der er link i sidefoden under "Om".

### Nat (04:53): idéliste
- **`docs/IDEER.md`:** En samlet liste over det, der venter på Lucas, større idéer der kræver en beslutning (engelsk version, scan af etiket, smartwatch, iPhone-app, login), og mindre idéer til senere.
- **Test mod den rigtige database kl. 05:00:** 21 af 22 tjek bestået. Det sidste venter stadig på `supabase/002-slet-billeder.sql`.

### Nat (04:40–04:42): sikkerhed
- **Data udefra bliver renset:** Alle kan skrive til den fælles database, så siden stoler ikke længere på det, den henter. Øl og bedømmelser fra databasen og fra backup-filer får nu tjekket typer, længder og felter, før de bruges. Ugyldige id'er bliver droppet, og billeder må kun komme fra sidens eget billedlager.
- **Ny test med fjendtlige data:** Testen lægger øl, bedømmelser, byture og smagninger med indlejret kode og forkerte typer i databasen og går 17 sider igennem. Ingen kode bliver kørt, ingen side går ned, og almindelige øl vises stadig.

### Nat (04:30–04:40): Android-appen
- **Genveje på app-ikonet:** Hold fingeren på ølrating-ikonet for at gå direkte til Bedøm en øl, Genstand-tæller, Smagning med venner eller Planlæg en bytur.
- **Sikkerhed:** Appen åbner nu kun adresser på ølrating.dk. Før kunne en anden app på telefonen bede ølrating-appen om at vise en fremmed side, som så ville få adgang til appens widgets og til at gemme billeder.

### Nat (03:22–03:28): anmeld indhold
- **Anmeld:** Øl og bedømmelser, som andre har lavet, har nu et "Anmeld"-link. Det åbner en mail til ejerne med link og id, så upassende indhold kan blive slettet.

### Nat (03:05–03:22): tilgængelighed
- **Automatisk tjek af tilgængelighed** (axe, WCAG 2 A og AA) på 18 sider i begge temaer og på pc og mobil. Antallet af fund faldt fra 341 til 43, og de sidste ligger lige under grænsen for kontrast.
- **Rettet:**
  - Menuen i det lyse tema var grå og svær at læse øverst på siden. Den er nu mørk.
  - Knappen "+ Tilføj øl" mistede sin orange farve, når man stod på siden Tilføj øl.
  - Orange overskrifter og tal er mørkere i det lyse tema.
  - Grå hjælpetekst, datoer på bedømmelser og låste mærker er blevet tydeligere.
  - Billedlinks på Sammenlign har fået navn til skærmlæsere, og kortet over bryggerier kan bruges med tastatur.

### Nat (03:00–03:05): lyst tema
- **Bedre læsbarhed i det lyse tema:** Gule tal og links på hvid baggrund var svære at læse. De er nu mørk rav i det lyse tema (karakterer, toplisten, nedtælling, links). På mørke flader som forsidebilledet, menuen og karakter-mærket på øl-kortene er farven stadig gul.
- "✓ Du er med" på en byttur og "● Forbundet" på Min profil er nu mørkegrønne i det lyse tema.

### Nat (02:50–03:00): design
- **Øl-siden:** Knapperne er ryddet op. "Bedøm den" er nu den tydelige orange knap sammen med "Vil smage" og "+ Genstand". Del, Del som billede, Sammenlign, Ret oplysninger og Slet øl står som mindre knapper nedenunder.
- **Øl-kort på mobil:** Bunden af kortet viser "2 bed." i stedet for "2 bedømmelser", så teksten ikke knækker over to linjer.

### Nat (02:30–02:50)
- **Kort over bryggerier:** Stilguiden har fået et forenklet Danmarkskort med en prik for hver by med et bryggeri. Prikken er gul, hvis du har bedømt en øl derfra. Tryk på en prik for at se bryggeriet eller byens øl. Kortet kender ca. 70 danske byer. Bryggerier i andre byer står på en liste under kortet.
- **Ny Android-widget "Noget for dig":** Viser et forslag til en øl, du ikke har bedømt, og nedtælling til næste øl-dag. Tryk åbner øllen i appen.
- **Desktop-widget:** Fanen "Mig" viser nu også et forslag ("Prøv: …").

### Nat (01:10–01:30)
- **Menuen "Mere":** Topmenuen har fået en undermenu med Smagning med venner, Venner, Genstand-tæller, Stilguide, Ølkalender, Øl til maden og Min øl-dagbog. På mobil vises alle sider i én liste.
- **Microsoft Store:** `docs/STORE.md` med trin for trin, færdige tekster til butikssiden og seks skærmbilleder i `store/`. Skærmbillederne bruger opdigtede eksempler.
- **Byttur:** Knappen "Send svar til værten" vises ikke længere for værten selv, og heller ikke når tilmeldingen allerede er gemt i databasen.

### Nat (00:55–01:10)
- **Venner:** Ny side, hvor du følger andre smagere og ser deres nyeste bedømmelser samlet. "Find smagere" foreslår dem, du er mest enig med. Hvem du følger, gemmes kun på din egen enhed.
- **Smagerside:** Hvert navn i en bedømmelse er nu et link til en side med personens bedømmelser, gennemsnit, yndlingsstil og jeres enighed i procent.

### Nat (00:45–00:55)
- **Smagning med venner:** Ny side, hvor værten skriver 2 til 12 øl, og alle giver karakter på deres egen telefon.
  - Med blindsmagning hedder øllene "Øl A, B, C", indtil værten afslører resultatet.
  - Gæster er med via link, QR-kode eller kode. Flere kan også stemme på samme telefon.
  - Når værten trykker "Afslør resultatet", vises ranglisten hos alle, nedefra og op, med vinderen til sidst.
  - Værten kan åbne for flere stemmer igen og slette smagningen for alle.
- **Hurtigere opdatering:** På en byttur- eller smagningsside hentes nyt hvert 6. sekund i stedet for hvert 30.
- **Forsiden:** "Mere at udforske" har fået genveje til Smagning med venner, Byttur og Genstand-tæller.

### Nat (00:30–00:45)
- **Noget for dig:** Forsiden og Min profil foreslår øl, du ikke har bedømt, ud fra de stilarter og smagsord, du selv har givet høje karakterer. Hvert forslag har en kort begrundelse.
- **Du er mest enig med:** Min profil viser, hvem du er mest enig med, i procent, ud fra de øl I begge har bedømt.
- **Alkoholfri øl:** Nyt felt "Alkoholfri" når en øl tilføjes, mærkat på kortene, filteret "Kun alkoholfri" og en egen fane på toplisten. En alkoholfri øl på 0 % giver ingen genstand i tælleren.
- **Mærker for variation:** Fire nye mærker: Stilkender (10 stilarter), Bryggerirunde (5 bryggerier), Globetrotter (3 lande) og Klart hoved (en alkoholfri øl). Stamgæst og Ølkender tæller nu forskellige øl og ikke antal bedømmelser.
- **Nedtælling på forsiden** til næste øl-dag (J-dag, påske, sankthans, jul eller nytår) med link til ølkalenderen.
- Teksten om backup på Min profil er rettet, så den passer til den fælles database.

## 2026-11-25

### Sen aften (23:55)
- **Tjek domæne:** Nyt workflow på GitHub, der viser, hvor ølrating.dk peger hen (navneservere, DNS-svar og https).
- **Resultat kl. 00:00:** .dk peger på one.coms navneservere (ns01 og ns02.one.com). Google, Cloudflare, Quad9 og OpenDNS ser alle de fire GitHub-adresser. https svarer med gyldigt certifikat til 23-02-2027, og www sender videre til ølrating.dk. http sender endnu ikke videre til https, fordi "Enforce HTTPS" ikke er slået til.
- **Commits** bruger fra nu af GitHubs noreply-adresse i stedet for en privat mail.

### Sen aften (23:10–23:45): stor test og rettelser
- **Automatiske test** ligger nu i `tests/` og kører på GitHub ved hver ændring af siden:
  - Hele siden klikket igennem på pc og mobil (72 tjek).
  - To enheder, der deler data mod en efterligning af databasen (34 tjek).
  - En test mod den rigtige database, som opretter og sletter sine egne testdata.
- **Resultat mod den rigtige database (kl. 23:40):** 18 af 19 tjek bestået: login, deling af øl, bedømmelser og billeder mellem to enheder, afvisning af forsøg på at rette andres data, byttur med tilmelding og sletning. Det sidste tjek, sletning af billedfilen, venter på `supabase/002-slet-billeder.sql`. https virker på ølrating.dk, men "Enforce HTTPS" er ikke slået til endnu.
- **Fejl fundet i testen og rettet:**
  - Slettede øl efterlod deres billede i lageret. Nu slettes billedet også. Det kræver den lille tilføjelse `supabase/002-slet-billeder.sql`.
  - Backup tog ikke billeder med, når de først var delt. Nu ligger billederne i backup-filen, og en gendannelse lægger dem op igen.
  - Indlæste øl fra en backup bliver nu dine egne, hvis de ikke findes i databasen i forvejen.
  - Karakteren på en øl-side talte op forfra, hver gang der kom nyt fra databasen. Nu opdateres siden roligt uden animation.
  - Billeder caches 1 time i stedet for 1 år, så et slettet billede forsvinder hurtigt for alle.
- **Byttur:** Værten kan slette turen for alle. Deltagere kan fjerne turen fra deres liste og bliver så meldt fra. En tur, værten har slettet, forsvinder hos deltagerne.

### Aften (22:00–23:30)
- **Fælles database koblet på:**
  - Øl, bedømmelser og billeder deles nu mellem alle enheder via Supabase. Siden henter nyt hvert 30. sekund og når den åbnes.
  - Hver enhed får en anonym bruger, så kun den, der har lavet noget, kan rette og slette det.
  - Virker også uden net: ændringer gemmes på enheden og sendes, når forbindelsen er tilbage.
  - Byttur: tilmelding sker automatisk hos alle, og en tur kan findes med en kode. Svar-linket bruges kun, hvis databasen ikke kan nås.
  - Privatlivssiden er skrevet om, så det står klart, hvad der er offentligt.
- **App-ikon:** Android-appen har fået et adaptivt ikon, hvor fjord-motivet fylder hele fladen. Den store hvide kant er væk. Der er også et ensfarvet ikon til Androids tema-ikoner, og web-appens maskable-ikon bruger samme motiv.
- **Dokumentation:** README, `docs/FUNKTIONER.md`, `docs/TEKNIK.md`, `docs/DRIFT.md` og denne ændringslog.
- **Fælles database:** Supabase-projekt oprettet. `supabase/schema.sql` med tabeller, Row Level Security og billed-bucket.
- **Byttur:**
  - Opret en tur med rute og stop, og del den med link eller QR-kode.
  - Vennerne melder sig til med "Jeg er med", og der vises "Vi er her nu" og næste stop.
  - "Kom sikkert hjem" har genvej til genstand-tæller, Rejseplanen og taxa.
- **iPhone:** Fuld skærm med safe areas. Genvej til genstand-tælleren i app-ikonets menu.
- **Genstand-tæller:**
  - Ny side og knappen "+ Genstand" på hver øl. Sundhedsstyrelsens anbefalinger og Alkolinjen.
  - Android-widget med +1, der virker uden at åbne appen, og en Genst.-fane i desktop-widgetten.
- **Domæne:** ølrating.dk er flyttet til one.com, DNS peger på GitHub Pages, og `CNAME` er tilføjet. Alle adresser peger nu på `xn--lrating-p1a.dk`.
- **Nye widgets:**
  - Seneste bedømmelser og Min statistik på Android.
  - Fanerne Top/Seneste/Mig i desktop-widgetten.
- **Windows og Linux:**
  - Electron-program med ikon ved uret og en widget, der kan ligge øverst.
  - Bygges automatisk til `.exe` og `.AppImage`.
- **Downloads:** Faste links til `android-app`- og `desktop-app`-udgivelserne. iPhone-guide til "Føj til hjemmeskærm".

### Aften (20:30–21:05)
- **Del som billede:** Delekort på 1080×1350. Android-appen gemmer det i Billeder.
- **Bryggerisider:**
  - Søgning tåler stavefejl og æ/ø/å.
  - "Vis flere" med 24 ad gangen.
- **Android-widgets:** Ugens øl + top 3 og Bedøm-knap. JavaScript-bro mellem side og app.
- **Billeder i IndexedDB:** Plads til langt flere billeder. Fortryd ved sletning. Billeder kommer med i backup.
- **Android-app:**
  - WebView-app bygget i GitHub Actions og downloadbar fra siden.
  - Ejere og fejlrapport-mail på siden.
- **Bedre øl-oplysninger:**
  - Felter: alkohol- og IBU-målere, farve, størrelse, pris pr. liter, servering og stregkode.
  - "Ret oplysninger" til den, der har tilføjet øllen.
- Alle eksempeløl og eksempelanmeldelser er fjernet.
- "Sammenlign" er tilføjet i topmenuen.
- **Nyt logo:** Fjord-mærket.
- Hosting midlertidigt på `lucas050908.github.io/-lrating.dk`.

### Eftermiddag
- **Første version af hjemmesiden:**
  - Limfjorden-design med Lucas' fotos.
  - Tilføj og bedøm øl, toplisten, galleri, stilguide, profil, ølkalender og øl til maden.
  - Sæsontemaer, lyst og mørkt tema. Siden virker offline og kan installeres som app.
