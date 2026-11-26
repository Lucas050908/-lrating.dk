# Funktioner

Alt hvad ølrating.dk og apps kan. Holdes opdateret ved hver ændring.

## Hjemmesiden

| Side | Adresse | Hvad |
|---|---|---|
| Forside | `#` | Ugens øl, søgning (også med stregkodescanner), filtre, sortering, "Vis flere" (24 ad gangen), seneste bedømmelser, app-sektion |
| Øl | `#beer-<id>` | Billede, oplysninger, karakterer i 5 kategorier, smagsprofil og anmeldelser. Knapperne er Del, Del som billede, Sammenlign, + Genstand, Bedøm, Ret oplysninger og Slet med fortryd |
| Tilføj øl | `#tilfoej` | Navn, bryggeri, stil, land/by, alkohol, IBU, farve, størrelse, pris, købested, servering, stregkode, billede og bedømmelse |
| Toplisten | `#toplisten` | Samlet, lyse og mørke øl |
| Galleri | `#galleri` | Alle billeder med lysboks |
| Sammenlign | `#sammenlign` | To øl side om side |
| Byttur | `#byttur` | Se [Byttur](#byttur) |
| Smagning | `#smagning` | Se [Smagning med venner](#smagning-med-venner) |
| Venner | `#venner` | Dem du følger, deres nyeste bedømmelser og forslag til andre smagere |
| Smager | `#smager-<navn>` | En persons bedømmelser, gennemsnit, yndlingsstil, enighed med dig og knappen Følg |
| Stilguide | `#stilguide` | Ølstile, kort over bryggerier og alle bryggerier |
| Bryggeri | `#bryggeri-<navn>` | Alle øl fra et bryggeri, gennemsnit og antal bedømmelser |
| Min profil | `#profil` | Navn, statistik, mærker, ønskeliste, backup og gendannelse |
| Øl-dagbog | `#dagbog` | Alt du har smagt og "Dit år i øl" |
| Ølkalender | `#kalender` | Juleøl, J-dag, påskebryg osv. |
| Øl til maden | `#mad` | Forslag til øl til forskellige retter |
| Genstand-tæller | `#genstande` | Se [Genstand-tæller](#genstand-tæller) |
| Privatliv / Om | `#privatliv`, `#om` | Privatlivspolitik, ejere og fejlrapport |

### Menuen
- Topmenuen viser Alle øl, Toplisten, Galleri, Sammenlign, Byttur, Mere, Min profil og Tilføj øl.
- Under **Mere** ligger Smagning med venner, Venner, Genstand-tæller, Stilguide og bryggerier, Ølkalender, Øl til maden og Min øl-dagbog.
- Under 1100 px bredde bliver menuen til en knap, der viser alle sider i én liste.

### Fælles database
- Alle ser de samme øl, bedømmelser og billeder. Nyt hentes, når siden åbnes, og derefter hvert 30. sekund.
- Kun den enhed, der har lavet en øl eller bedømmelse, kan rette og slette den. Knapperne vises ikke hos andre.
- Sletning har stadig fortryd. Øllen og dens billede fjernes først fra databasen efter ca. 10 sekunder.
- Backup-filen indeholder også billederne. Indlæses den igen, bliver øl, bedømmelser og billeder lagt op på ny.
- Uden net virker alt som før. Ændringer sendes, når forbindelsen er tilbage. Status ses under Min profil ("Forbundet" eller "Ikke forbundet").
- Genstand-tæller, ønskeliste, hvem du følger, og indstillinger deles **ikke**. De bliver på enheden.

### Noget for dig og enighed
- **Noget for dig** vises på forsiden og på Min profil, når du har bedømt mindst to øl. Den foreslår op til fire øl, du ikke har bedømt, med en begrundelse som "Du plejer at kunne lide pilsner".
- **Du er mest enig med** vises på Min profil. Den sammenligner dine karakterer med andres på de øl, I begge har bedømt (mindst to fælles øl), og viser enigheden i procent.

### Alkoholfri øl
- Sæt hak i "Alkoholfri (højst 0,5 %)", når øllen tilføjes. Øl med en alkoholprocent på 0,5 eller under regnes også som alkoholfri.
- Kortene viser "Alkoholfri", der er et filter "Kun alkoholfri", og toplisten har en fane kun for alkoholfri øl.

### Mærker
- Mærkerne belønner variation: forskellige øl, stilarter, bryggerier og lande, og at prøve en alkoholfri øl. Ingen mærker gives for at drikke meget.

### Kort over bryggerier
- Kortet ligger på Stilguiden. Det er et forenklet Danmarkskort, tegnet i selve siden, så der ikke hentes noget fra korttjenester.
- Hver by med et bryggeri får en prik, og tallet viser, hvor mange bryggerier der er i byen.
- En gul prik betyder, at du har bedømt en øl fra et bryggeri i byen. En orange prik betyder, at du ikke har prøvet noget derfra endnu.
- Byen findes ud fra det, der er skrevet i feltet "By", da øllen blev tilføjet. Kendes byen ikke, står bryggeriet på en liste under kortet.

### Nedtælling
- Forsiden viser, hvor mange dage der er til næste øl-dag: J-dag, påske, sankthans, jul eller nytår.

### Søgning
- Søgningen tåler æ/ø/å skrevet som ae/oe/aa, så "fano" finder Fanø.
- Den tåler også en stavefejl i ord på mindst 4 bogstaver, fx ét bogstav for meget eller for lidt, et forkert bogstav eller to bogstaver byttet om.
- Der søges i navn, bryggeri, stil, by, land, stregkode og navne på dem, der har tilføjet eller bedømt.

### Del som billede
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

### Smagning med venner
- **Opret:** Værten giver smagningen et navn og skriver 2 til 12 øl, én pr. linje. Blindsmagning er slået til som standard.
- **Vær med:** Gæster åbner linket, scanner QR-koden eller skriver koden. De giver hver øl 1 til 5 stjerner. Flere kan stemme på samme telefon ved at skrive et nyt navn.
- **Blindsmagning:** Øllene vises som "Øl A, B, C", indtil resultatet er afsløret.
- **Afsløring:** Kun værten kan afsløre. Ranglisten vises hos alle inden for få sekunder, nedefra og op, med vinderen til sidst. Hver øl viser gennemsnit, antal stemmer og din egen karakter.
- **Bagefter:** Værten kan åbne for flere stemmer eller slette smagningen for alle.
- Siden minder om, at små smagsprøver er nok, og at man ikke kører bil bagefter.

### Andet
- Sæsontemaer med partikler: jul, J-dag, nytår, fastelavn, påske, sankthans og halloween.
- Lyst og mørkt tema efter tid på dagen.
- Billeder gemmes i IndexedDB, så der er plads til mange.
- Fortryd i 7 sekunder ved sletning.
- Backup og gendannelse som fil, inkl. billeder.
- Virker offline (service worker) og kan installeres som app.

## Apps

### Android (`olrating.apk`)
- Viser siden i fuld skærm. Kamera og billedvalg virker, og stregkodescanneren virker.
- Delekort gemmes i Billeder.
- **Widgets:**

| Widget | Indhold | Tryk |
|---|---|---|
| Ugens øl | Ugens øl, top 3, antal øl og bedømmelser | Åbner appen, "+ Bedøm" åbner Tilføj øl |
| Bedøm øl (1×1) | Knap | Åbner Tilføj øl |
| Seneste bedømmelser | De 4 nyeste med navn og karakter | Åbner appen |
| Min statistik | Øl smagt, gennemsnit, yndlingsstil | Åbner Min profil |
| Genstand-tæller | Genstande i dag og på 7 dage | **+1** lægger en genstand til uden at åbne appen. Ellers åbnes tælleren |
| Noget for dig | Et forslag til en øl, du ikke har bedømt, med begrundelse, og nedtælling til næste øl-dag | Åbner øllen |

### Windows og Linux
- Programmet (Electron) viser siden i et eget vindue og har et ikon ved uret med en menu.
- En **widget** ligger i hjørnet og kan sættes til altid at være øverst. Den har fanerne **Top**, **Seneste**, **Mig** og **Genst.**, hvor **+1** lægger en genstand til. Widgettens placering huskes.
- Windows: `olrating-windows.exe`, en bærbar fil uden installation. SmartScreen-advarslen kommer, fordi filen ikke er signeret. Den forsvinder, når appen kommer i Microsoft Store.
- Linux: `olrating-linux.AppImage`.

### iPhone og iPad
- Siden kan lægges på hjemmeskærmen i Safari med Del → Føj til hjemmeskærm. Den åbner så i fuld skærm og tager højde for notch og afrundede hjørner.
- Rigtige iPhone-widgets kræver en App Store-app, og den kræver en Apple-udviklerkonto.
