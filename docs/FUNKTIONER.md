# Funktioner

Alt hvad ølrating.dk og apps kan. Holdes opdateret ved hver ændring.

## Hjemmesiden

| Side | Adresse | Hvad |
|---|---|---|
| Forside | `#` | Ugens øl, søgning (også med stregkodescanner), filtre, sortering, "Vis flere" (24 ad gangen), seneste bedømmelser, app-sektion |
| Øl | `#beer-<id>` | Billede, oplysninger, karakterer i 5 kategorier, smagsprofil og anmeldelser. Store knapper: Bedøm den, Vil smage og + Genstand. Små knapper: Del, Del som billede, Sammenlign, Ret oplysninger og Slet øl med fortryd |
| Tilføj øl | `#tilfoej` | Navn, bryggeri, stil, land/by, alkohol, IBU, farve, størrelse, pris, købested, servering, stregkode, billede og bedømmelse. Siden foreslår øl, der allerede findes, mens du skriver, så der ikke kommer dubletter. En stregkode udfylder selv felterne fra Open Food Facts |
| Toplisten | `#toplisten` | Samlet, lyse, mørke og alkoholfri øl. Knappen "Del toplisten som billede" laver et billede af de 5 bedste |
| Årets øl | `#aarets` | Årets vinder, de næste på listen, årets bryggeri, stil, alkoholfri og nykommer. Se [Årets øl](#årets-øl) |
| Galleri | `#galleri` | Alle billeder med lysboks |
| Sammenlign | `#sammenlign` | To øl side om side |
| Byttur | `#byttur` | Se [Byttur](#byttur) |
| Smagning | `#smagning` | Se [Smagning med venner](#smagning-med-venner) |
| Enig eller uenig? | `#swipe` | Swipe på andres bedømmelser. Se [Enig eller uenig?](#enig-eller-uenig-swipe) |
| Venner | `#venner` | Dem du følger, deres nyeste bedømmelser og forslag til andre smagere |
| Beer buddies | `#buddies` | Dem, der smager som dig, med match i procent. Se [Beer buddies](#beer-buddies) |
| Lykkehjulet | `#hjul` | Vælger én øl for dig. Se [Lykkehjulet](#lykkehjulet) |
| Indstillinger | `#indstillinger` | Design, farver, tema og sprog. Se [Indstillinger](#indstillinger-design-og-farver) |
| Smager | `#smager-<navn>` | En persons bedømmelser, gennemsnit, yndlingsstil, enighed med dig og knappen Følg |
| Stilguide | `#stilguide` | Ølstile, kort over bryggerier og alle bryggerier |
| Bryggeri | `#bryggeri-<navn>` | Alle øl fra et bryggeri, gennemsnit og antal bedømmelser |
| Min profil | `#profil` | Navn, statistik, mærker, ønskeliste, backup og gendannelse. Egne bedømmelser vises 15 ad gangen med "Vis flere", hver med Ret og Slet. De øl, du har tilføjet, står i en boks for sig med Ret |
| Øl-dagbog | `#dagbog` | Alt du har smagt og "Dit år i øl" |
| Ølkalender | `#kalender` | Juleøl, J-dag, påskebryg osv. |
| Øl til maden | `#mad` | Forslag til øl til forskellige retter |
| Genstand-tæller | `#genstande` | Se [Genstand-tæller](#genstand-tæller) |
| Nyt på siden | `#nyt` | Oversigt over de nyeste funktioner med links |
| Privatliv / Om | `#privatliv`, `#om` | Privatlivspolitik, ejere og fejlrapport |

### Dansk og engelsk
- Siden er dansk som standard. **Sprogvælgeren** i topmenuen viser et flag og DA eller EN. Tryk på den, og vælg Dansk eller English i den lille menu. Valget kan også ændres under "Sprog · Language" i sidefoden, og det huskes på enheden.
- **Skiftet sker med det samme.** Siden bliver ikke hentet igen, du bliver stående samme sted på siden, og overgangen er blød. Skriver du i en formular, bliver det, du har skrevet, stående.
- Har browseren et andet sprog end dansk, norsk eller svensk, viser knappen det engelske flag og "English?", indtil der er valgt et sprog.
- Hele siden er oversat: menuer, alle sider, formularer, beskeder, mærker, stilguide, privatlivspolitik og delebillederne.
- På engelsk skrives tal med punktum (4.5), datoer på engelsk, og priser som DKK.
- Det, brugerne selv har skrevet (navne på øl, anmeldelser, byture), bliver ikke oversat.
- Widgets: I Android-appen følger de telefonens sprog (engelsk, når telefonen er sat til engelsk). Widgetten i programmet til Windows og Linux følger sidens sprog. Navne på øl, stilarter og højtider kommer fra siden og står på dansk.

### Menuen
- Topmenuen viser Alle øl, Toplisten, Galleri, Sammenlign, Byttur, Mere, Min profil, Tilføj øl og sprogvælgeren.
- Under **Mere** ligger Smagning med venner, Venner, Beer buddies, Lykkehjulet, Enig eller uenig?, Genstand-tæller, Årets øl, Stilguide og bryggerier, Ølkalender, Øl til maden, Min øl-dagbog og Indstillinger.
- Under 1100 px bredde bliver menuen til en knap, der viser alle sider i én liste.

### Fælles database
- Alle ser de samme øl, bedømmelser og billeder. Nyt hentes, når siden åbnes, og derefter hvert 30. sekund.
- Kun den enhed, der har lavet en øl eller bedømmelse, kan rette og slette den. Knapperne vises ikke hos andre.
- Sletning har stadig fortryd. Øllen og dens billede fjernes først fra databasen efter ca. 10 sekunder.
- Backup-filen indeholder også billederne. Indlæses den igen, bliver øl, bedømmelser og billeder lagt op på ny.
- **Anmeld:** På øl og bedømmelser, som andre har lavet, er der et "Anmeld"-link. Det åbner en mail til ejerne med link til indholdet.
- Uden net virker alt som før. Ændringer sendes, når forbindelsen er tilbage. Status ses under Min profil ("Forbundet" eller "Ikke forbundet").
- Genstand-tæller, ønskeliste, hvem du følger, og indstillinger deles **ikke**. De bliver på enheden.

### Noget for dig og enighed
- **Noget for dig** vises på forsiden og på Min profil, når du har bedømt mindst to øl. Den foreslår op til fire øl, du ikke har bedømt, med en begrundelse som "Du plejer at kunne lide pilsner".
- **Du er mest enig med** vises på Min profil. Den sammenligner dine karakterer med andres på de øl, I begge har bedømt (mindst to fælles øl), og viser enigheden i procent.

### Beer buddies
- Siden **Beer buddies** (under Mere i menuen) finder dem, der smager som dig. Den kræver, at du har skrevet dit navn og bedømt mindst to øl, som en anden også har bedømt.
- **Match i procent:** Vi tager forskellen mellem jeres samlede karakterer på hver fælles øl. Ingen forskel giver 100 %, og den størst mulige forskel (1 mod 5) giver 0 %. Matchet er gennemsnittet over jeres fælles øl.
- Hvert kort viser antal fælles øl, den øl I er **mest enige om**, den I er **mest uenige om**, og et **tip**: den øl, din buddy har givet højest (mindst 3,5), som du ikke har bedømt.
- **Flere smagere** viser dem, du har under to øl til fælles med, og foreslår en øl, du kan bedømme, så matchet kan regnes ud.
- Knappen **Følg** lægger personen i din liste over venner.

### Lykkehjulet
- Siden **Lykkehjulet** (under Mere i menuen) vælger én øl for dig, når du ikke kan vælge.
- Du bestemmer, hvilke øl der er på hjulet: **Ikke smagt**, **Alle øl**, **Ønskelisten**, **Toppen** (4,0 og derover) eller **Alkoholfri**. Hjulet viser op til 10 øl. Er der flere i gruppen, kan du få nye øl på hjulet.
- Tryk **Drej hjulet**. Når det stopper, står øllen under hjulet med link til dens side.
- Hjulet vælger kun én øl ad gangen. Under hjulet står Sundhedsstyrelsens anbefalinger, et link til Genstand-tælleren og nummeret til Alkolinjen.

### Indstillinger, design og farver
- Siden **Indstillinger** (under Mere i menuen) samler de valg, der kun gælder ens egen enhed.
- **Design og farver:** baggrund (Nat, Fjord, Skov, Aften, Stout, Kul), farver (Solnedgang, Hav, Skov, Bær, Guld), mønster (Ingen, Bobler, Bølger, Stjerner) og bobler, der stiger op bag siden.
- **Tema efter højtid:** "Efter dato" skifter selv farver ved jul, påske og andre højtider. Man kan også vælge ét fast eller Normal.
- **Sprog:** dansk eller engelsk.
- Vælger man en anden farve end Solnedgang, gælder den også, når der er højtid.

### Loading screen
- Når siden åbnes, vises navnet og en bjælke, der fyldes som en fadøl med skum forrest. Den forsvinder, når siden er klar.
- Den vises ikke, hvis enheden er sat til mindre bevægelse.

### Små effekter
- Tal tæller op under *Siden i tal*. Fem stjerner, at følge en smager, at gemme en bedømmelse, et nyt mærke og lykkehjulets resultat giver et drys.
- Fem hurtige tryk på logoet øverst giver en hemmelig skål.
- Med "mindre bevægelse" slået til på enheden er effekterne væk.

### Siden i tal og besøgstæller
- På **Om** står *Siden i tal*: besøg i alt, besøg i dag, antal øl, bedømmelser og smagere.
- Besøg er, hvor mange gange siden er åbnet. Det er ikke antal personer. Der gemmes kun ét tal pr. dag. Svarer tælleren ikke (før fil 005 er kørt), husker enheden det i en time, så den ikke spørger ved hvert besøg.
- Tælleren starter den dag, `supabase/005-besoeg.sql` bliver kørt. Besøg før den dag kan ikke findes frem. Indtil da viser Om kun øl, bedømmelser og smagere.

### Karakterer med kommatal
- Hver kategori (udseende, duft, smag, fylde og helhed) får en karakter fra 1,0 til 5,0.
- Et tryk på en stjerne giver et helt tal. Med − og + ved siden af retter man i trin på 0,1, fx fra 4,0 til 3,7. Tallet står mellem de to knapper, og den sidste stjerne bliver kun delvist fyldt.
- Det gælder også, når man stemmer i en smagning.
- Gamle bedømmelser med hele tal virker som før.

### Alkoholfri øl
- Sæt hak i "Alkoholfri (højst 0,5 %)", når øllen tilføjes. Øl med en alkoholprocent på 0,5 eller under regnes også som alkoholfri.
- Kortene viser "Alkoholfri", der er et filter "Kun alkoholfri", og toplisten har en fane kun for alkoholfri øl.

### Mærker
- Mærkerne belønner variation: forskellige øl, stilarter, bryggerier og lande, og at prøve en alkoholfri øl. Ingen mærker gives for at drikke meget.

### Kort over bryggerier
- Kortet ligger på Stilguiden. Det er et forenklet Danmarkskort, tegnet i selve siden, så der ikke hentes noget fra korttjenester.
- Hver by med et bryggeri får en prik, og tallet viser, hvor mange bryggerier der er i byen.
- En gul prik betyder, at du har bedømt en øl fra et bryggeri i byen. En orange prik betyder, at du ikke har prøvet noget derfra endnu.
- Byen findes ud fra det, der er skrevet i feltet "By", da øllen blev tilføjet. Kortet kender omkring 310 danske byer og bydele. Kendes byen ikke, står bryggeriet på en liste under kortet.

### Nedtælling
- Forsiden viser, hvor mange dage der er til næste øl-dag: J-dag, påske, sankthans, jul eller nytår.

### Søgning
- Søgningen tåler æ/ø/å skrevet som ae/oe/aa, så "fano" finder Fanø.
- Den tåler også en stavefejl i ord på mindst 4 bogstaver, fx ét bogstav for meget eller for lidt, et forkert bogstav eller to bogstaver byttet om.
- Der søges i navn, bryggeri, stil, by, land, stregkode og navne på dem, der har tilføjet eller bedømt.
- Finder søgningen ingenting, kan øllen tilføjes direkte: med navnet udfyldt, eller med stregkoden, hvis man har søgt på en.

### Årets øl
- Kun bedømmelser fra det valgte år tæller. Er der bedømmelser fra flere år, kan året vælges øverst.
- Har mindst én øl fået 2 bedømmelser i året, skal en øl have mindst 2 for at være med på listen. Så vinder en øl ikke på en enkelt topkarakter.
- **Årets priser:** årets bryggeri (bedste gennemsnit, mindst 2 bedømmelser), årets stil (flest bedømmelser), årets alkoholfri og årets nykommer (bedste øl, der er tilføjet i året, hvis det ikke er vinderen selv).
- Nederst står årets tal: antal bedømmelser, forskellige øl, bryggerier og smagere. Der kåres ingen personer, og ingen bliver belønnet for at drikke meget.
- "Del Årets øl som billede" laver et billede af årets 5 bedste.

### Del som billede
- Toplisten og Årets øl kan deles som et billede på 1080×1350 med de 5 bedste øl, deres billeder og karakterer.
- Laver et delekort på 1080×1350 med fjordfoto, øllens billede, navn, bryggeri, stil, alkohol og karakter.
- Delekortet deles direkte på telefoner, der kan det. Ellers bliver det hentet som fil, og i Android-appen bliver det gemt i Billeder/ølrating.

### Genstand-tæller
- Regner genstande ud: cl × alkohol% × 0,789 ÷ 12 g.
- Har hurtigknapper til almindelige drikke og dine egne øl, plus fri indtastning.
- Viser **i dag** (dagen starter kl. 6, så en bytur tæller som én dag) og **seneste 7 dage**. En bjælke viser ugen i forhold til Sundhedsstyrelsens anbefaling på højst 10 om ugen og højst 4 på samme dag.
- Henviser til Alkolinjen (80 200 500) og siger klart, at tælleren ikke kan bruges til at vurdere, om man må køre.
- Alt gemmes kun på enheden. Genstande ældre end 60 dage slettes.

### Byttur
- **Opret en tur:** navn, dato og tid, mødested og en besked. Værten tilføjer stop med bar, tidspunkt og adresse, med link til Google Maps. Stop efter midnat sorteres rigtigt.
- **Del:** som link (Web Share) eller QR-kode. Linket indeholder hele turen.
- **Find med kode:** Hver tur har en kode. Den kan skrives under "Har du fået en kode til en tur?".
- **Tilmelding:**
  - Vennen åbner linket eller skriver koden og trykker "Jeg er med". Så står vennen på listen hos alle.
  - Kan databasen ikke nås, sendes i stedet et svarlink til værten, som åbner det for at få vennen på listen.
- **Slet og meld fra:** Værten kan slette turen for alle. En deltager kan fjerne turen fra sin liste og bliver så meldt fra.
- **Under turen:** "Vi er her nu" og næste stop beregnes ud fra tidspunkterne.
- **Kom sikkert hjem:** genvej til genstand-tælleren, Rejseplanen og taxa, plus 112 ved fare.
- **Minde:** 14 timer efter første stop er turen slut. Så flytter den ned under "Minder" på oversigten, og siden for turen viser "Sådan gik turen":
  - antal stop, hvem der var med, og de øl, holdet bedømte den dag, med turens bedste øl øverst.
  - En bedømmelse tæller med, når navnet på bedømmelsen står på turens liste. Starter turen kl. 16 eller senere, tæller dagen efter også med.
  - "Del mindet som billede" laver et billede med dato, rute, hold og turens bedste øl.
  - Mindet viser kun, hvad der blev smagt og bedømt. Der er ingen opgørelse over, hvor meget nogen drak.

### Enig eller uenig? (swipe)
- Ét kort ad gangen med en bedømmelse, en anden har givet: øllens billede, navn, hvem der har bedømt, karakteren, teksten og smagsordene. Har du selv bedømt øllen, står din egen karakter nederst.
- **Swipe til højre** for enig og **til venstre** for uenig. Mens du trækker, kommer stemplet ENIG eller UENIG frem. Knapperne under kortet og piletasterne gør det samme. "Spring over" gemmer kortet til senere, og "Fortryd" tager det seneste tilbage.
- Bedømmelser af øl, du selv har bedømt, kommer først. Dine egne bedømmelser er ikke med, og du kan ikke stemme på dem.
- **Den, der har bedømt, kan se tallene:** Ved hver bedømmelse står der, hvor mange der er enige og uenige, og Min profil har boksen "Er andre enige med dig?" med den samlede procent.
- **Nye stemmer:** Har nogen stemt på dine bedømmelser, siden du sidst åbnede Min profil, får Min profil (og menu-knappen på mobil) en lille gul prik. Boksen viser, hvor mange nye stemmer der er, og hvilken af dine bedømmelser flest er enige og uenige i.
- Stemmerne ligger i den fælles database. Hvem der har stemt hvad, kan ingen andre se. Kun tallene er offentlige.
- Mangler databasen tilføjelsen `supabase/003-konto-mails-enig.sql`, gemmes stemmerne på enheden og sendes, når den er kørt.

### Konto (frivillig, ikke slået til endnu)
- Siden virker som altid uden konto: man skriver bare sit fornavn. En konto er et tilvalg på Min profil.
- **Login med kode:** Man skriver sin mail og får en kode på 6 tal. Der er ingen adgangskode.
- **Samme konto på flere enheder:** Første gang bliver enhedens anonyme bruger til kontoen, så alt, der er lavet på enheden, følger med. Logger man ind på en anden enhed, flyttes den enheds øl og bedømmelser over på kontoen.
- **Det følger med kontoen:** ens navn, ønskeliste og dem, man følger. Fjerner man en øl fra ønskelisten på én enhed, forsvinder den også på de andre. Genstand-tælleren bliver på enheden og gemmes ikke på kontoen.
- **Mails, man selv slår til:** nyheder om siden, når nogen bedømmer en øl, man har tilføjet, når en, man følger, bedømmer en øl (højst én mail om dagen), og når nogen melder sig til ens byttur eller stemmer i ens smagning.
- **Mailene samler op:** Man får højst én mail i timen. Er der sket flere ting, står de i samme mail med link til øllen, turen eller smagningen. Mailen er på dansk eller engelsk efter det sprog, man bruger på siden.
- **Afmeld:** Nederst i hver mail er der et link til siden "Afmeld mails". Et tryk på knappen slår alle mails fra, også uden login. Man kan slå dem til igen på Min profil.
- **Log ud og slet konto** ligger samme sted. Sletter man kontoen, forsvinder login og mailvalg. Øl og bedømmelser bliver stående, medmindre man sletter dem først.
- Kontoen er skjult på siden, indtil mail-delen er sat op (se `docs/KONTO.md`). Den kan prøves på én enhed ved at åbne `ølrating.dk/#konto-test`.

### Smagning med venner
- **Opret:** Værten giver smagningen et navn og skriver 2 til 12 øl, én pr. linje. Blindsmagning er slået til som standard.
- **Vær med:** Gæster åbner linket, scanner QR-koden eller skriver koden. De giver hver øl en karakter fra 1 til 5, gerne med kommatal. Flere kan stemme på samme telefon ved at skrive et nyt navn.
- **Blindsmagning:** Øllene vises som "Øl A, B, C", indtil resultatet er afsløret.
- **Afsløring:** Kun værten kan afsløre. Ranglisten vises hos alle inden for få sekunder, nedefra og op, med vinderen til sidst. Hver øl viser gennemsnit, antal stemmer og din egen karakter.
- **Bagefter:** Værten kan åbne for flere stemmer eller slette smagningen for alle. "Del resultatet som billede" laver et billede med aftenens vinder og resten af ranglisten.
- **Ud fra ønskelisten:** Har du mindst to øl på din ønskeliste, kan knappen "Brug min ønskeliste" fylde dem ind, når du opretter en smagning.
- Siden minder om, at små smagsprøver er nok, og at man ikke kører bil bagefter.

### Andet
- Sæsontemaer med partikler: jul, J-dag, nytår, fastelavn, påske, sankthans og halloween.
- Siden er altid mørk.
- Billeder gemmes i IndexedDB, så der er plads til mange.
- Fortryd i 7 sekunder ved sletning.
- Backup og gendannelse som fil, inkl. billeder.
- Virker offline (service worker) og kan installeres som app.

## Apps

### Android (`olrating.apk`)
- Viser siden i fuld skærm. Kamera og billedvalg virker, og stregkodescanneren virker.
- Delekort gemmes i Billeder.
- **Genveje:** Hold fingeren på app-ikonet for at gå direkte til Bedøm en øl, Genstand-tæller, Smagning med venner eller Planlæg en bytur (Android 7.1 og nyere).
- **Widgets:**

| Widget | Indhold | Tryk |
|---|---|---|
| Ugens øl | Ugens øl med billede, top 3, antal øl og bedømmelser | Åbner appen, "+ Bedøm" åbner Tilføj øl |
| Ugens øl med billede | Et stort billede af ugens øl med navn, bryggeri og karakter | Åbner øllen |
| Bedøm øl (1×1) | Knap | Åbner Tilføj øl |
| Seneste bedømmelser | De 4 nyeste med et lille billede af øllen, navn og karakter | Åbner appen |
| Min statistik | Øl smagt, gennemsnit, yndlingsstil | Åbner Min profil |
| Genstand-tæller | Genstande i dag og på 7 dage | **+1** lægger en genstand til uden at åbne appen. Ellers åbnes tælleren |
| Noget for dig | Et forslag til en øl, du ikke har bedømt, med billede og begrundelse, og nedtælling til næste øl-dag | Åbner øllen |
| Siden i tal | Besøg i alt og i dag, antal øl, bedømmelser og smagere | Åbner Om |

Billederne i widgets er små kopier af øllenes egne billeder. En øl uden billede vises uden. Billeder og tal bliver hentet, når appen åbnes.

### Windows og Linux
- Programmet (Electron) viser siden i et eget vindue og har et ikon ved uret med en menu.
- En **widget** ligger i hjørnet og kan sættes til altid at være øverst. Den har fanerne **Top**, **Nyt**, **Mig**, **Genst.** og **Siden**. Top og Nyt viser små billeder af øllene, på Genst. lægger **+1** en genstand til, og Siden viser besøg i alt og i dag, antal øl, bedømmelser og smagere. Widgettens placering huskes.
- Windows: `olrating-windows.exe`, en bærbar fil uden installation. SmartScreen-advarslen kommer, fordi filen ikke er signeret. Den forsvinder, når appen kommer i Microsoft Store.
- Linux: `olrating-linux.AppImage`.

### iPhone og iPad
- Siden kan lægges på hjemmeskærmen i Safari med Del → Føj til hjemmeskærm. Den åbner så i fuld skærm og tager højde for notch og afrundede hjørner.
- Rigtige iPhone-widgets kræver en App Store-app, og den kræver en Apple-udviklerkonto.

## Ret dine gamle bedømmelser
Under **Min profil → Mine bedømmelser** har hver af dine bedømmelser knapperne **Ret** og **Slet**. Listen viser også de bedømmelser, du har lavet på enheden under et andet navn, fx hvis du har skiftet navn. At rette en bedømmelse ændrer ikke dit navn. Ret åbner øllens side med bedømmelsen udfyldt. Ret det, du vil, og tryk **Gem ændringer**, eller tryk **Fortryd ændringer**. En rettet bedømmelse beholder sin dato og viser "rettet". På øllens egen side kan du også trykke Ret ved din bedømmelse. Har du bedømt øllen før, står der over formularen, hvilken karakter du gav, med et link til at rette den. Har bedømmelsen et foto, vises det, når du retter, og du kan fjerne det eller vælge et nyt.

## Stregkoden udfylder selv
Scanneren virker på Android, iPhone og i de fleste browsere med kamera. Hvor browseren ikke selv kan læse stregkoder (fx iPhone), hentes en lille læser, første gang man trykker Scan.

Under **Tilføj øl** kan du scanne eller skrive stregkoden. Siden slår nummeret op i Open Food Facts (en åben, gratis database over varer) og udfylder navn, bryggeri, alkohol %, stil, størrelse og billede, hvis øllen findes der. Kun tomme felter udfyldes. Tjek altid, at det passer. Kommer billedet fra Open Food Facts, står det under øllens navn med et link (licensen kræver det). Findes øllen allerede på ølrating.dk, viser siden den i stedet. Scanner du fra forsiden, åbner øllens side direkte ved Bedøm.
