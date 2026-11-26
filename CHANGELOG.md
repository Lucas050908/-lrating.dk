# Ændringslog

Nyeste øverst. Hver ny ting skrives her i samme commit, som den laves i.

## 2026-11-26

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
