# Ændringslog

Nyeste øverst. Hver ny ting skrives her i samme commit, som den laves i.

## 2026-11-25

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
