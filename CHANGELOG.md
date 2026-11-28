# Ændringslog

Nyeste øverst. Hver ny ting skrives her i samme commit, som den laves i.

## 2026-11-28

### Eftermiddag (15:40–16:11): login, dobbelttryk, datoer efter midnat, blokeret lager, ødelagte links, sorte PNG-billeder og grænser mod spam
- **Fundet:** Alle kan skrive i databasen uden at logge ind, og der er ingen grænse for, hvor meget. Et lille script kunne lægge titusindvis af øl ind, og fordi siden nu henter alle øl (rettelsen kl. 15.39), ville det gøre siden langsom for alle og fylde lageret i browseren.
- **`supabase/006-graenser.sql` (ny, ikke kørt):** Højst 40 nye øl i timen og 150 i døgnet pr. bruger, og 60 bedømmelser i timen og 300 i døgnet. Rettelser tæller ikke. Lucas skal køre den i Supabase. `test_sql.js` tester den (95 tjek), og testen mod den rigtige database skriver, om den er kørt.
- **Siden henter højst 20.000 rækker** pr. tabel. Er listen ikke slut dér, fjerner siden ikke noget lokalt.
- **Test:** `test_sync.py` har en tabel, der aldrig slutter (siden stopper efter 20 sider og beholder egne øl), og en ny øl, der afvises med 400 (som når grænsen er nået), bliver på enheden.
- **`DRIFT.md` var forkert:** Der stod, at 003 ikke var kørt. Testen mod den rigtige database siger, at den er kørt.
- **Bedømmelser efter midnat fik gårsdagens dato:** Datoen blev taget i UTC (`toISOString`), så en bedømmelse mellem kl. 00 og 01 (om sommeren 00–02) fik gårsdagens dato. Det ramte fx bedømmelser sent på en byttur og "nye bedømmelser i dag" på forsiden. Nu bruges dansk (lokal) tid overalt (`dstr()`). `test_sync.py` bedømmer en øl kl. 00.30.
- **Siden gik i stå, når browseren ikke må gemme data** (alle cookies og data blokeret, fx i Safari eller Chrome): Første forsøg på at læse lageret gav en fejl, og intet virkede. Nu bruges et lager i hukommelsen (`LS`), siden virker, og den siger, at det, man laver, forsvinder, når siden lukkes. `test_site.py` prøver det.
- **To faner åbne i over en time gav en ny bruger:** Login fornyes cirka hver time med et refresh-token, der kun kan bruges én gang. Havde den ene fane fornyet, prøvede den anden med det gamle token, blev afvist og fik en ny bruger. Så kunne man ikke længere rette sine egne øl i den fane, og efter en genindlæsning heller ikke i den første. Nu tager siden den nyeste session fra lageret, før den fornyer. `test_sync.py` åbner to faner med et login, der kun gælder 75 sekunder, og efterligner Supabase, hvor et token kun virker én gang.
- **Login blev skiftet ud ved en serverfejl:** Når den usynlige login skulle fornyes, og Supabase svarede med en fejl (fx 503 under en driftsforstyrrelse), fik enheden en helt ny bruger. Så stod alle ens egne øl og bedømmelser som en andens, og man kunne ikke rette dem. Nu får man kun en ny bruger, når Supabase klart siger nej (400, 401, 403). Ved serverfejl eller uden net prøves der igen senere. `test_sync.py` tester det med et 503-svar.
- **Dobbelttryk på Gem:** To hurtige tryk på "Gem bedømmelse" eller "Tilføj øl" gemte to gange (to ens bedømmelser eller to ens øl). Siden skifter først 0,6 sekund efter et gem, så der var tid til et tryk mere. Nu er formularen låst, mens den gemmer, og 1,5 sekund efter. Mangler der noget (fx stjerner), kan man trykke igen med det samme. Gælder alle formularer. `test_site.py` trykker tre gange hurtigt.
- **Ødelagte links:** En adresse som `#smager-100%` (et %, der ikke er kodet, fx fordi en besked-app har ændret linket) gav en fejl, og siden blev ikke tegnet. Nu vises siden med teksten, som den står. `test_site.py` prøver 12 ødelagte eller tomme adresser.
- **Gennemsigtige PNG-billeder** (fx et logo eller et produktbillede uden baggrund) blev lavet om til JPEG med sort baggrund. Nu får de hvid bund.
- **Test:** `test_site.py` lægger et gennemsigtigt PNG ind og tjekker, at midten er hvid. Den prøver også en tekstfil kaldt .jpg, en tom fil og en .txt-fil: alle tre giver beskeden "Det billede kunne ikke læses" og ingen fejl (det virkede allerede).

### Eftermiddag (15:25–15:39): dage talt forkert omkring sommertid, "1 dage" og flere felter i sikkerhedstesten
- **Nedtællinger i Ølkalenderen:** Antal dage blev regnet som timer delt med 24 og rundet op. Når sommertiden slutter i oktober, har et døgn 25 timer, så fra april til slutningen af oktober stod der én dag for meget til J-dag og nytårsaften (fx 18 dage i stedet for 17 den 20. oktober). Nu tælles hele kalenderdage.
- **"1 dage":** Dagen før J-dag stod der "1 dage". Nu står der "I morgen".
- **Bedømmelser:** "for 2 dage siden" kunne stå om en bedømmelse fra i går sent på aftenen, når sommertiden skiftede. Rettet på samme måde.
- **Byttur:** En tur i morgen aften (fx 25 timer væk) stod som "om 2 dage". Nu står der "i morgen".
- **Målt med mange data:** 2.000 øl og 8.000 bedømmelser: alle sider tegnes på under 0,1 sekund. Grænsen er lageret i browseren (cirka 5 MB): 6.000 øl og 24.000 bedømmelser kan ikke gemmes. Der er langt dertil, men det står nu i `IDEER.md` med en løsning.
- **Tjek domæne** (GitHub) er kørt: https virker, certifikatet gælder til 23-02-2027, og alle store DNS-tjenester peger på GitHub Pages. Workflowet tjekker nu også de fire DNS-linjer til Resend og skriver OK eller MANGLER. Resend siger lige nu: DKIM er godkendt, MX og TXT på `send` og CNAME på `rsend` mangler.
- **Tests:** `test_sync.py` kører nu siden i dansk tid på bestemte datoer: kalenderen 20. oktober og 5. november, en bedømmelse natten efter sommertidens slut, en tur dagen før, og alle sider nytårsnat, på skuddagen 2028 og i de to timer, hvor sommertiden skifter. `test_site.py`s test af kode i brugernes tekst dækker nu også sted, beskrivelse, størrelse, land, ture, stop, mødested, rettelse af en øl og siderne Genstande, Mad og Byttur. Den fandt ingen huller.

### Eftermiddag (14:54–15:39): tre måder, data kunne forsvinde eller sidde fast ved deling
Lucas bad om, at alt bliver testet til kl. 23. Første fund kom fra at læse synkroniseringen igennem og skrive tests for det, der kan gå galt.
- **Et billede, der ikke kan gemmes, stoppede al deling:** Afviste billedlageret et billede (fx for stort), gik hele synkroniseringen i stå, også hentning af andres øl, og Min profil sagde "Ikke forbundet". Nu bliver kun den ene øl på enheden, og resten deles som normalt. Den prøves igen, næste gang siden åbnes.
- **En ny øl, som databasen afviste, blev slettet fra enheden:** Ved svar 403 eller 409 blev øllen markeret som delt, og ved næste hentning blev den fjernet, fordi den ikke lå i databasen. Nu gælder det kun noget, der allerede er delt. En ny øl bliver på enheden og prøves igen senere.
- **Over 1000 øl eller bedømmelser:** Supabase giver højst 1000 rækker pr. svar. Siden bad om 2000 og 5000 og fik kun 1000. Havde databasen flere, ville egne øl længere nede være blevet fjernet fra enheden. Nu hentes der 1000 ad gangen, til alt er hentet.
- **Langsomt net:** Blev en øl gemt, mens en synkronisering kørte, ventede den til næste runde 30 sekunder senere. Nu køres en ny synkronisering lige efter.
- **Man kan se, hvad der ikke er delt:** Min profil siger fx "Forbundet – men 1 af dine øl eller bedømmelser er kun på denne enhed endnu", og en egen øl, der ikke er delt, siger det på sin side. Det havde forklaret forvirringen om "Julemandens Classic" fredag.
- **Tests:** `test_sync.py` har nu en efterlignet database, der kan afvise billeder og rækker og højst giver 1000 rækker pr. svar. Den tjekker fejlene, beskederne, en øl gemt midt i en langsom synkronisering, 1151 øl (hentes alle, og søgning virker), og at data fra den allerførste udgave af siden virker på alle sider.

## 2026-11-27

### Aften (20:23–20:32): et skjult filter på forsiden
- **Problemet (fundet med Lucas' skærmbillede):** Trykker man "Se juleøl" i Ølkalenderen eller en stil i Stilguiden, viser forsiden kun den stil. Knappen med stilen lå langt ude til højre i rækken af stilarter, så man ikke kunne se, at et filter var slået til. Det så ud, som om øl var forsvundet.
- **Rettet:** Når et filter er slået til, står der nu under stilarterne fx "Viser kun: Juleøl (1 af 3 øl). Vis alle øl", og knappen for stilen rulles ind, så den kan ses. "Vis alle øl" slår alle filtre fra.
- **Test:** `test_site.py` går fra Stilguiden til forsiden og tjekker linjen, at knappen kan ses, og at "Vis alle øl" viser alle øl igen.
- **Databasen er tjekket:** Testen mod den rigtige database består (anonymt login, øl, bedømmelser og billeder gemmes og ses fra en anden enhed). Øllen "Julemandens Classic", som Lucas mener at have tilføjet, ligger ikke i databasen. Årsagen er ikke fundet endnu.

### Eftermiddag (15:31–15:32): blok 6 – docs og ændringslog kontrolleret
- **Ændringsloggen:** 14 af dagens tidsrum passede ikke med tidspunkterne for de tilhørende commits (nogle sluttede før de begyndte). De er rettet.
- **Docs læst mod koden:** `DRIFT.md` og `FUNKTIONER.md` sagde stadig, at 005 ikke var kørt. `IDEER.md` havde fil 003 på listen over det, der venter på Lucas, selv om den er kørt torsdag; nu står logo, loading screen, Ølspil og scanneren på telefonen der i stedet. `README.md` nævner nu `byg-scanner.sh`.
- **Firefox på GitHub:** Den engelske test fejlede igen én gang, nu på knappen "Spring over" under swipe, der ikke var tegnet endnu. Alle testens klik med kode venter nu på knappen først (højst 8 sekunder). Safaris motor fejlede én gang på en melding om en fil, der ikke kunne hentes, under synkroniseringstesten; den bestod i kørslen lige efter og er ikke forklaret endnu.

### Eftermiddag (14:48–14:52): besøgstælleren er i gang
- Lucas har kørt `supabase/005-besoeg.sql`. Testen mod den rigtige database (startet med hånden på GitHub) siger: "kørt, 5 besøg i alt". Fil 004 og funktionen `mails` er stadig ikke sat op.

### Eftermiddag (14:16–14:47): 1000 logoer, plakater, og tilbage til profilen efter en rettelse
- **1000 logoer:** `tools/logoer.py` har 20 nye stilarter: 10 farvesæt (skov, bær, kobber, hav, kul, creme, rød, mint, lavendel, sort-hvid) i to former hver, nu også sekskant. Sammen med de 5 gamle giver de 40 motiver × 25 stilarter = 1000 logoer i `img/logoer/1000/` (`python3 tools/logoer.py img/logoer/1000 --1000`). Nr. 1–200 er de samme som før, så et nummer, man har valgt, gælder stadig. Nr. 201–1000 = 200 + (motiv − 1) × 20 + stil.
- **`tools/logo-ud.py`** tager nu et nummer fra 1 til 1000 og kan tegne sekskanten.
- **Plakat:** Et design med alle 1000 på én plakat i A1, og de samme logoer på fem A4-sider med 200 på hver. Logoerne ligger i plakaten som vektor, så de bliver skarpe, også når den printes stort.
- **10.000 logoer:** Nr. 1001–10000 er de 40 motiver i 25 farvesæt (de 15 ovenfor og 10 nye: nordlys, citron, vin, is, sand, oliven, koral, blåbær, grafit, rosa), 5 former (firkant, cirkel, sekskant, ottekant, skjold) og med eller uden en tynd ring. Kombinationer, der allerede findes i nr. 1–1000, er sprunget over, så hvert motiv har 225 nye: nr. = 1000 + (motiv − 1) × 225 + stil. De ligger ikke som filer i repoet (det ville være 44 MB), men tegnes af `python3 tools/logoer.py <mappe> --10000`, og `tools/logo-ud.py` kan sætte ethvert af dem ind. Ærligt sagt: forskellen mellem nr. 1001 og 10000 er farve og form, ikke nye motiver.
- **Plakat med 10.000:** én plakat i A0, 100 × 100 logoer. Rækkerne står med deres første nummer og kolonnerne 1–100, så nummeret er rækkens tal + kolonnen − 1. Logoerne er tegnet i dobbelt opløsning, så de er skarpe i A0.
- **Ret fra Min profil:** Når man retter en bedømmelse fra Min profil og gemmer eller fortryder, kommer man nu tilbage til Min profil i stedet for at blive stående på øllens side.
- **Test:** `test_site.py` tjekker, at man kommer tilbage til Min profil efter både Gem og Fortryd.
- **Test af logoerne:** `test_site.py` tjekker nu, at nr. 1, 200, 201, 1000, 1001 og 10000 peger på de rigtige motiver og stilarter, at filnavnene i `img/logoer/1000` passer med numrene, at alle fem former (også med ring) giver gyldig SVG, og at et nummer over 10000 afvises.
- **Plakaten med 10.000:** Blokken med logoerne var blevet trukket over på A4-side 3 på lærredet, så A0-plakaten stod uden logoer. Den er lagt tilbage, og logoerne er nu låst på alle plakaterne, så de ikke kan trækkes væk ved et uheld. Plakaterne er også sendt som PDF.

### Eftermiddag (14:03–14:15): tilføj øllen direkte fra søgningen
- **Søger man på en stregkode,** som ingen øl har, står der nu "Tilføj øl med stregkode …". Knappen åbner Tilføj øl med koden udfyldt, og siden henter navn og billede fra Open Food Facts.
- **Søger man på et navn,** der ikke findes, åbner "Tilføj øl" nu med navnet udfyldt, så man ikke skal skrive det igen.
- **Klik på alt** (`tests/klik.py`) kørt igen efter dagens nye knapper: 73 tryk på 27 sider, ingen fejl. Tilgængelighed (axe) også uden fejl.
- **Test:** `test_site.py` tjekker begge veje fra søgningen.
- **Microsoft Store:** Teksterne til butikssiden (`docs/STORE.md`) nævner nu scanneren, på dansk og engelsk. Funktionslisten har 9 punkter; Store tillader op til 20.

### Eftermiddag (13:54–14:02): scan og bedøm med det samme
- Scanner man en øl fra forsiden, som allerede findes på siden, åbner øllens side nu direkte ved **Bedøm**, med fokus på den første stjerne. Før landede man øverst og skulle rulle ned.
- **Test:** `test_site.py` scanner (med efterlignet læser) en kendt øl og tjekker, at Bedøm står på skærmen.

### Eftermiddag (13:39–13:53): alkoholfri fra stregkoden, og målinger
- **Alkoholfri:** Står en øl i Open Food Facts som alkoholfri (kategori), men uden alkoholtal, får den nu alligevel hak i "Alkoholfri". Under feltet står "alkoholfri" blandt det hentede.
- **Kontrast målt igen** efter dagens nye knapper og bokse: alle 30 kombinationer af baggrund og farver er i orden på de 14 sider.
- **Vægt og starttid (krav 9 i planen):** `index.html` er 101 KB pakket mod 96 KB fredag kl. 6.32. Stigningen er dagens nye funktioner: opslag i Open Food Facts, scanner med fokus og råd, rettelse af bedømmelser og billeder, egne øl på profilen. `js/scan.js` (17 KB pakket) hentes kun på enheder uden indbygget stregkodelæser. Starttiden er uændret: klar efter 61 ms mod 64 ms i morges (Chrome, telefonstørrelse, median af 7).
- **Test:** `test_site.py` tjekker hakket i Alkoholfri med en efterlignet vare uden alkoholtal.

### Eftermiddag (13:29–13:38): billeder i browsere, der ikke kan gemme dem på den normale måde
- **Problemet:** Nogle browsere (fx Safaris motor i et privat vindue, som i testene på GitHub) kan ikke gemme et billede som en "Blob" i browserens database (IndexedDB). Så blev billedet gemt som tekst i den lille lokale lagerplads (localStorage, ca. 5 MB), som hurtigt bliver fuld ("Lageret er fuldt").
- **Rettet:** Billedet gemmes i stedet som rå data (ArrayBuffer) i IndexedDB, der har meget mere plads, og laves om til et billede igen, når det skal vises eller sendes. Bevist: med den gamle kode lander billedet som tekst i localStorage, med den nye i IndexedDB.
- **Test:** `test_site.py` efterligner en browser, der afviser Blobs, tilføjer en øl med billede og tjekker, at billedet ligger i IndexedDB og vises efter genindlæsning.

### Middag og eftermiddag (12:52–13:20): dine egne øl på Min profil
- **Øl, du har tilføjet:** Min profil har en ny boks med de øl, du har tilføjet (de 20 nyeste), hver med en **Ret**-knap, der åbner øllens oplysninger. Før skulle man finde øllen først. Skærmlæsere hører, hvilken øl knappen retter.
- **Test:** `test_site.py` tjekker boksen og at Ret åbner den rigtige øl.
- På små telefoner (under 420 px) skjules karakteren i den liste, så navnene har plads. Knappen er gjort lidt mindre.
- **Nyt på siden** (`#nyt`) har fået to nye punkter øverst: "Scan stregkoden" og "Ret dine bedømmelser".

### Middag (12:32–12:51): Safaris motor og Firefox på GitHub gennemgået
- **Gennemgået:** Alle kørsler siden i morges, job for job. Udover fejlen med det delte billede (rettet 12.33) fejlede Safaris motor af og til på meldinger om forespørgsler, der blev afbrudt, fordi testen skiftede side midt i en synkronisering ("… due to access control checks"). Det er ikke en fejl på siden: Chromium og Firefox melder intet i samme situation. Testene ser nu bort fra netop den melding i Safaris motor.
- **Firefox:** Den engelske test fejlede én gang, fordi den trykkede på sprogknappen, før den var tegnet. Nu venter testen på knappen. En konto-test fejlede også én gang: den ventede et fast sekund på svaret fra den efterlignede database. Nu venter den på, at feltet til koden kommer frem (højst 8 sekunder).
- **Lille rettelse:** Når et gammelt billede slettes fra lageret i baggrunden, og det fejler, giver det ikke længere en ubehandlet fejl i konsollen. Det gjaldt to steder (når et billede skiftes, og når en øl er slettet på en anden enhed).
- **Rettelse af tidligere status:** "Grøn i alle tre browsere" i morges passede ikke helt. Kørslen var grøn, men jobbet for Safaris motor var rødt flere gange. Fremover tjekker jeg hvert job, ikke kun kørslen.

### Middag (12:10–12:31): et billede kunne slette et andet billede
- **Fejl fundet i Safaris motor:** Siden 10.07 har ét tjek fejlet på GitHub i Safaris motor (WebKit). Jobbet må fejle uden at stoppe resten, så hele kørslen stod som grøn, og det overså jeg. Statussen om "grøn i alle tre browsere" har derfor ikke passet siden kl. 10.
- **Årsagen var en rigtig fejl:** Kan browseren ikke gemme billeder i IndexedDB (fx Safaris private vindue), gemmes de som tekst. Så fik filen i lageret et navn ud fra selve billedet. Brugte en øl og en bedømmelse samme billede, delte de én fil. Fjernede man billedet fra bedømmelsen, forsvandt det også fra øllen. Bevist med den gamle kode: efter at fotoet er fjernet fra bedømmelsen, er øllens billede væk.
- **Rettet:** Filnavnet indeholder nu også øllens eller bedømmelsens id, så to ting aldrig deler en fil.
- **Test:** `test_site.py` slår IndexedDB fra, giver en øl og en bedømmelse samme billede, fjerner det ene og tjekker, at det andet er der endnu.

### Middag (11:59–12:09): widgets på engelsk
- **Android:** Alle tekster i de 8 widgets og genvejene ligger nu i sprogfiler. Er telefonen sat til engelsk, står widgets og genveje på engelsk ("Beer of the week", "Latest ratings", "units today" osv.). Ellers dansk som før. Det står på listen over idéer som "engelske widgets", og er nu slettet derfra.
- **Windows og Linux:** Widgetten følger sidens sprog. Vælger man English på siden, skifter widgetten også.
- **Test:** `test_site.py` åbner desktop-widgetten med efterlignede data og tjekker dansk og engelsk. Android-appen bliver bygget på GitHub, men er **ikke prøvet på en telefon**.

### Formiddag (11:39–11:58): scanneren og tastaturet
- Når scanneren åbner, flytter fokus til **Luk**, så den kan lukkes med Enter eller Mellemrum (Esc virkede i forvejen). Når den lukker, kommer fokus tilbage til den knap, der åbnede den. Det hjælper dem, der bruger tastatur eller skærmlæser.
- **Test:** `test_site.py` tjekker, hvor fokus står før og efter.
- **Stregkodelæseren i alle browsere:** `test_site.py` læser nu en stregkode direkte med `js/scan.js` i den browser, testen kører i. På GitHub sker det også i Safaris motor (som på iPhone) og Firefox, hvor det falske kamera ikke findes.
- **Ustabile test rettet:** `test_en.py` lagde eksempeldata ind, mens siden var åben, og siden kunne nå at gemme sine egne data oven i, når maskinen var travl. Det gav sjældne fejl (en side uden årstal og "tilbage til dansk" med anden rækkefølge). Nu lægges data ind fra en side uden sidens kode (`robots.txt` på samme adresse), og det samme i `klik.py`.

### Formiddag (11:25–11:38): scanneren hjælper, når den ikke kan læse koden
- Har scanneren ikke fundet en kode efter 12 sekunder, skifter teksten til et råd: hold telefonen lidt længere væk, eller luk og skriv tallene under stregkoden.
- Når en kode er læst, vibrerer telefonen kort (hvis den kan).
- **Test:** `test_site.py` tjekker rådet med et falsk ur og at Luk lukker kameraet uden at udfylde noget.

### Formiddag (11:15–11:24): ny test, der trykker på alle knapper
- **`tests/klik.py`:** 23 knapper blev ikke trykket på af nogen test (bl.a. filtrene, Sammenlign, lysboksen, Overrask mig, Vis flere, del en tur og genåbn en smagning). Den nye test åbner 27 sider med eksempeldata og trykker på hver slags knap én gang, hver gang på en frisk side, og melder fejl i JavaScript og i konsollen. Første kørsel: 72 tryk, ingen fejl.
- Den kører på GitHub ved hver ændring, sammen med tilgængelighed og layout.
- **`tests/test_en.py`:** Tjekket "tilbage til dansk giver præcis den samme tekst" fejlede én gang i formiddags uden at vise forskellen (samme tekster, kun en anden rækkefølge eller et andet antal). Det bestod de næste to gange. Testen skriver nu, hvor de to udgaver begynder at være forskellige, så årsagen kan findes, hvis det sker igen.

### Formiddag (11:00–11:14): scanneren virker nu, også på iPhone
- **Alvorlig fejl rettet:** Scanneren har aldrig givet en stregkode tilbage. Når den fandt koden, lukkede den kameraet på en måde, der svarede "ingen kode", før koden nåede frem. Så skete der ingenting, hverken på forsiden eller under Tilføj øl. Fejlen har været der siden første udgave. Bevist: med den gamle kode og en efterlignet scanner forbliver feltet tomt. Med den nye kommer koden frem.
- **Scanner på iPhone og i Firefox:** De browsere har ikke den indbyggede stregkodelæser (BarcodeDetector), så Scan-knappen var skjult. Nu hentes en lille læser (`js/scan.js`, 70 kB, 17 kB pakket), når man trykker Scan. Den læser billedet fra kameraet ca. 6 gange i sekundet. Den hentes kun på de enheder, der mangler den indbyggede, og den virker også uden net.
- **Læseren** er bygget af det åbne bibliotek ZXing (`@zxing/library`, Apache-2.0) med kun de dele, der læser stregkoder på varer (EAN, UPC og Code 128). `tools/byg-scanner.sh` bygger den igen fra `tools/scanner-entry.js`.
- **Test:** `test_site.py` starter Chromium med et falsk kamera, der viser en stregkode (lavet i testen), og tjekker, at koden bliver læst, at felterne bliver udfyldt fra Open Food Facts (efterlignet), og at scanneren på forsiden åbner Tilføj øl med koden. En anden test efterligner den indbyggede læser på Android.
- **Ikke prøvet:** en rigtig iPhone og en rigtig Android-telefon.

### Formiddag (10:50–10:59): kredit til Open Food Facts, og ændringsloggen ryddet op
- **Kredit:** Billeder fra Open Food Facts må bruges, når der står, hvor de kommer fra (licensen CC BY-SA). En øl, hvis billede er hentet derfra, viser nu "Billede: Open Food Facts (CC BY-SA)" med link til varen. Vælger man selv et andet billede, forsvinder linjen. Om-siden nævner Open Food Facts og licenserne.
- **Ændringsloggen:** Fredagens punkter stod under en forkert dato ("27-11-2026"), og torsdag aftens punkter var havnet under fredag. Datoerne og rækkefølgen er rettet, og tidsrummene for formiddagens punkter passer nu med tidspunkterne for de tilhørende commits.
- **Test:** `test_site.py` gemmer en øl med billede fra (efterlignet) Open Food Facts og tjekker, at linjen med kredit og link står på øllens side.

### Formiddag (10:08–10:49): gamle bedømmelser under et andet navn, og docs gennemgået
- **Bedømmelser under et gammelt navn:** Har man skiftet navn, forsvandt de gamle bedømmelser fra Min profil, og de kunne ikke rettes. Nu viser Min profil alle bedømmelser, der er lavet på enheden (databasen ved, hvilke der er dine), også under et andet navn. Der står, hvor mange der har et andet navn, og de kan rettes og slettes som de andre.
- **Ret og Slet** vises nu ved alle bedømmelser, der er lavet på enheden, også når to har bedømt på samme telefon. Det passer med reglen i dokumentationen: den enhed, der har lavet noget, kan rette og slette det. Andre enheder kan stadig ikke (tjekket i `test_sync.py`).
- **Rettet:** At gemme en rettelse ændrede dit navn til navnet på bedømmelsen. Nu bliver dit navn stående.
- **Docs læst mod koden:** `FUNKTIONER.md` manglede Beer buddies, Lykkehjulet og Indstillinger i tabellen og i menuen, og sagde, at besøgstælleren intet gemmer på enheden. `TEKNIK.md` havde en gammel liste over data i `S`, et forkert navn for smagsprofilen (`p` i stedet for `prof`) og manglede `olrating-vis404`, `olrating-konto` og Open Food Facts i CSP. Alt er rettet.
- **Test:** `test_site.py` skifter navn og tjekker, at de gamle bedømmelser står der og kan rettes, og at navnet ikke skifter ved en rettelse. Tjekket af knapper på øllens side forventer nu begge bedømmelser fra samme telefon.

### Formiddag (09:57–10:07): stregkoden henter selv oplysninger om øllen
- **Scan og få felterne udfyldt:** Når man scanner eller skriver en stregkode under Tilføj øl, slår siden nummeret op i **Open Food Facts**, en åben og gratis database over varer. Kendes øllen, udfyldes navn, bryggeri, alkohol %, stil, størrelse og billede, og alkoholfri bliver sat, hvis den er det. Kun tomme felter bliver udfyldt, så det, man selv har skrevet, bliver stående. Under feltet står, hvad der blev hentet, og at man skal tjekke det.
- Det virker også, når man scanner fra forsiden og øllen ikke findes på ølrating.dk endnu.
- Findes øllen allerede på siden, spørges der ikke. Så vises "Findes den allerede?" som før.
- Kun selve nummeret bliver sendt, og kun hvis kontrolcifret passer. Privatlivssiden siger det nu.
- **Privatliv rettet:** Siden sagde, at besøgstælleren ikke gemmer noget på enheden. Efter rettelsen i formiddags husker enheden i en time, hvis tælleren ikke svarer. Det står der nu.
- **Sikkerhed:** Sidens sikkerhedsregel (CSP) tillader nu kun de to adresser hos Open Food Facts ud over databasen.
- **Test:** `test_site.py` efterligner Open Food Facts og tjekker, at felterne bliver udfyldt, at et forkert nummer ikke bliver slået op, at et ukendt nummer siger det, at det man selv har skrevet bliver stående, og at konsollen er uden fejl. Testen rører aldrig den rigtige tjeneste.
- **Ikke prøvet:** et rigtigt opslag hos Open Food Facts og en rigtig scanning med telefonen. Herfra kan jeg ikke nå den rigtige tjeneste.

### Formiddag (09:53–10:07): foto, når man retter, og README
- **Foto i en rettet bedømmelse:** Når man retter en bedømmelse med foto, vises fotoet nu i feltet, og der er et link **Fjern foto**. Før var feltet tomt, så man kunne tro, at fotoet var væk, og det kunne ikke fjernes. Vælger man et nyt foto, erstatter det det gamle. Det gamle foto slettes også fra databasens lager.
- **README:** Android-appen har 8 widgets (ikke 6). Mapperne `tools/` og `img/logoer/` og de nye tjek i `tests/` er nævnt.
- **Test:** `test_site.py` lægger et foto på en bedømmelse, retter den, fjerner fotoet og tjekker, at det er væk både fra bedømmelsen og fra lageret.

### Formiddag (09:47–09:52): øllens side husker din bedømmelse
- **Har du bedømt øllen før,** står det nu over formularen på øllens side, med den karakter du gav, og et link: **Ret din bedømmelse**. Så kommer man ikke til at skrive en ny bedømmelse, når man bare ville rette den gamle. Man kan stadig skrive en ny.
- Engelsk: "You have already rated it and gave it 4.5. Edit your rating or write a new one below."
- **Test:** `test_site.py` tjekker, at linjen står der, og at linket åbner rettelsen.

### Formiddag (09:40–09:46): blok 3 i planen – vægt, starttid og besøgstælleren
- **Besøgstælleren:** Indtil `supabase/005-besoeg.sql` er kørt, svarer databasen "404". Før kom den linje i konsollen ved hver eneste åbning. Nu husker siden svaret og prøver højst én gang i timen. Når filen er kørt, begynder tælleren at tælle senest en time efter på hver enhed.
- **Målt (Chrome, telefonstørrelse, median af 7 åbninger, uden net til databasen):** Torsdag morgen (c4edea8): klar efter 65 ms, færdig efter 132 ms. Nu: klar efter 70 ms, færdig efter 106 ms. Siden er ikke blevet langsommere at starte.
- **Vægt:** `index.html` er 97 KB pakket (torsdag morgen 67 KB). Forskellen er de nye funktioner (Beer buddies, Lykkehjulet, Indstillinger, loading screen, widgets). Der er ingen indlejrede billeder eller anden fyld. Engelsk (`js/en.js`) og QR-koder (`js/qr.js`) hentes stadig kun, når de bruges.
- **To faner og uden net:** Allerede rettet og testet tidligere (se torsdag aften og fredag morgen).
- **Test:** `test_sync.py` tjekker, at siden ikke spørger igen ved næste åbning, når tælleren mangler, og at den tæller, når den findes.

### Formiddag (09:25–09:39): ret dine gamle bedømmelser fra profilen
- **Ret gamle bedømmelser:** Under Min profil → Mine bedømmelser har hver bedømmelse nu knapperne **Ret** og **Slet**. Ret åbner øllens side med alt udfyldt (karakterer, tekst, smagsnoter, smagsprofil og "køber igen"), så man bare retter og trykker Gem ændringer. Bedømmelsen beholder sin dato og får mærket "rettet".
- **Fortryd ændringer:** Mens man retter, er der en knap til at droppe ændringerne igen.
- Testen tjekker at Ret åbner den rigtige bedømmelse, at Fortryd ikke gemmer noget, og at en rettelse gemmes med samme id og dato.

### Formiddag (09:19–09:25): konto, manifest og genveje
- **Konto (skjult indtil videre):** Koden til login er læst igennem. Én lille ting er sikret: Gav bekræftelsen af koden ingen ny session, og var der ingen i forvejen, gik det galt. Resten er dækket af testene.
- **Webappens manifest** har fået et fast `id`, så en telefon kan kende appen igen, selv hvis adressen en dag ændrer sig.
- **Genveje:** Holder man fingeren på ølrating-ikonet på en Android-telefon, er Lykkehjulet nu med blandt genvejene.

### Formiddag (08:52–09:19): siden hopper ikke længere, mens den indlæses
- **Målt:** Forsiden og de fleste sider "hoppede" kraftigt, mens de blev indlæst. Google måler det som Cumulative Layout Shift (CLS), og det var 0,88 på telefon og 0,62 på pc. Google kalder alt over 0,25 dårligt, og det kan trække siden ned i søgeresultaterne.
- **Grunden:** Sidefoden stod øverst, indtil indholdet var tegnet, og blev så skubbet ned. Ved genindlæsning prøvede browseren desuden at scrolle tilbage, før indholdet var der, og "Alle øl" scrollede ned i samme billede, som indholdet blev tegnet.
- **Rettet:** Indholdet fylder mindst en hel skærm fra starten. Browserens egen scroll ved genindlæsning er slået fra, fordi siden alligevel selv scroller ved hvert sideskift. "Alle øl" scroller først, når indholdet er tegnet.
- **Nu:** CLS er 0 på 10 sider på telefon og pc, også når man genindlæser midt nede på en side. Målt med en telefon, der er gjort 4 gange langsommere.
- **Test:** Et nyt tjek i `test_site.py` måler CLS på fem sider og fejler over 0,1.

### Morgen (08:35–08:51): backup-filer renses, lykkehjulet og en slettet øl, og fejlsiden på engelsk
- **Rettet:** Når man indlæste en backup-fil, blev ønskelisten og navnet fra filen ikke renset. Var navnet ikke tekst, blev det gemt og fik siden til at gå ned, hver gang den blev åbnet. Nu tages kun gyldige øl-id'er med på ønskelisten (højst 500), og navnet bruges kun, hvis det er tekst (højst 30 tegn).
- **Test:** To nye tjek. Det ene indlæser en ondsindet backup-fil med forkerte typer og kode i et ølnavn og tjekker, at navn, ønskeliste og siden er i orden bagefter. Det andet tjekker, at et gyldigt navn og gyldige øl-id'er bliver taget med. Det sidste fejler på den gamle udgave af siden.
- **Fejlsiden** (`404.html`, når en adresse ikke findes) har fået en linje på engelsk.
- **Rettet: Lykkehjulet.** Blev den øl, hjulet valgte, slettet i en anden fane, mens hjulet drejede, viste siden intet resultat, og knappen hed stadig "Drej hjulet". Nu står der, at øllen lige er blevet slettet, og at man kan dreje igen. Fundet ved at køre testen 7 gange i træk, hvor den fejlede i 4.
- **Test:** Lykkehjul-testen med to faner trykker igen, hvis trykket rammer knappen, lige mens siden tegnes om.

### Morgen (08:31–08:34): uden net kunne appen vise en fejlside
- **Rettet:** Service workeren gemte enhver side, man åbnede på domænet, som den udgave af forsiden, der bruges uden net. Åbnede man en adresse, der ikke findes, blev fejlsiden ("404") gemt i stedet, og så viste appen fejlsiden næste gang, man var uden net. Nu gemmes kun selve forsiden, og kun når den er hentet uden fejl.
- **Mindre at hente på telefonen:** Service workeren hentede også de tre store forsidebilleder til pc (ca. 540 kB) på telefoner, der aldrig viser dem. De er taget ud af pakken. En pc gemmer dem i stedet første gang, de bliver vist.
- **Test:** Offline-tjekket i `test_site.py` åbner nu først en adresse, der ikke findes. Med den gamle service worker fejler det (appen viser "Error code: 404"), og med den nye består det.

### Morgen (08:24–08:31): links ud af apps er gjort sikre
- **Windows og Linux:** Et link, der fører væk fra ølrating.dk, blev åbnet af styresystemet uden at tjekke, hvilken slags link det var. Et `file:`-link eller et link til et andet program kunne dermed åbne noget på computeren. Nu åbnes kun `https:`, `http:` og `mailto:`.
- **Android:** På samme måde åbnes nu kun links med `https:`, `http:`, `mailto:`, `geo:` og `tel:`, og kun i apps, der må åbnes fra en browser (`CATEGORY_BROWSABLE`).
- Programmet til Windows og Linux var i forvejen sat rigtigt op (`contextIsolation`, `sandbox`, ingen Node i siden), og beskederne fra siden til programmet tjekker det, de får.
- Ingen af de to ændringer er prøvet på en rigtig computer eller telefon. GitHub bygger dem.

### Morgen (08:16–08:23): tilgængelighed tjekket med axe-core
- **Nyt værktøj, `tests/axe.py`:** Det kører axe-core, et udbredt værktøj til at tjekke tilgængelighed, over 25 sider på telefon og pc, på dansk og engelsk, efter WCAG 2.2 AA. Kontrast tjekkes ikke dér, fordi `tests/kontrast.py` gør det.
- **Det fandt tre ting, og de er rettet:**
  - Sprogknappen øverst blev læst op som "Sprog · Language", men der står "DA" eller "English?" på den. Navnet indeholder nu det, der står.
  - Mange sider springer fra den store overskrift direkte til mindre overskrifter i boksene. Skærmlæsere får nu det rigtige niveau gennem `aria-level`, så man kan hoppe rundt efter overskrifter. Udseendet er det samme.
  - To tomme overskriftsceller i tabellen på Sammenlign har fået en usynlig tekst til skærmlæsere.
- Nu finder axe ingen brud på nogen af siderne.
- **GitHub:** Hovedjobbet kører nu også `tests/axe.py` og `tests/layout.py` ved hver ændring.

### Morgen (08:10–08:15): sikkerhedstest og nye skærmbilleder til Store
- **Ny test:** Alle felter, som brugerne kan skrive i (navn, øl, bryggeri, stil, by, note, smagsord, tekst), får et forsøg på at køre et script. Derefter besøges 18 sider på dansk og engelsk, og lykkehjulet drejes. Intet bliver kørt. For at være sikker på, at testen virker, blev den også kørt mod en side, der med vilje satte teksten ind urenset, og der fejlede den som den skulle.
- Mail-funktionen (`supabase/functions/mails/index.ts`) er læst igennem: Den renser al tekst, før den kommer i en mail.
- **Microsoft Store:** Tre nye skærmbilleder på dansk og engelsk: Beer buddies, Lykkehjulet og Indstillinger. De syv gamle er lavet igen med siden, som den er nu. Det er de 10, Store højst tager pr. sprog.

### Morgen (07:56–08:08): gennemgang af gårsdagens kode
- **Rettet: Navne kunne få siden til at gå ned.** Hed en smager, et bryggeri, en stil eller et smagsord fx `constructor`, `toString` eller `__proto__`, gik forsiden, Venner og Beer buddies ned for alle. Det skyldtes, at navnene blev brugt som nøgler i almindelige JavaScript-objekter, hvor de navne allerede findes. 15 steder bruger nu objekter uden den slags indbyggede navne (`Object.create(null)`).
- **Rettet: Lykkehjulet.** Blev siden tegnet igen midt i et drej (fx når nye data blev hentet, eller en anden fane gemte), kunne øllene på hjulet skifte, så vinderen ikke var den, pilen pegede på. Nu står øllene stille, mens hjulet drejer, og mens resultatet vises. En øl, der er slettet imens, ryddes væk ved næste drej. Knappen er låst, mens hjulet drejer.
- **Tjekket og i orden:** To faner på samme side gemmer ingenting af sig selv, så de kan ikke skubbe hinanden i en løkke. Billeder til widgets hentes med `crossOrigin`, så de også virker fra databasen.
- **Test:** 2 nye tjek i `test_site.py`. Det ene fejler på den gamle udgave af siden, så det ses, at det fanger fejlen.

### Morgen (06:30–06:32): layout og kontrast også i Safaris motor og Firefox
- **GitHub:** Jobbene for WebKit og Firefox kører nu også `tests/layout.py` og `tests/kontrast.py`. Før blev de to tjek kun kørt i Chromium.
- `tests/kontrast.py` kan nu køre i en anden browser med `BROWSER=webkit` eller `BROWSER=firefox`, ligesom de andre test.
- Alle commits fra torsdag aften er grønne på GitHub i alle tre browsere.

## 2026-11-26

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
