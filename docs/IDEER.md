# Idéer og ting, der venter

En liste over det, der ikke er lavet endnu, og hvorfor. Flyt et punkt til `CHANGELOG.md`, når det er lavet.

## Venter på Lucas
| Hvad | Hvad skal der til |
|---|---|
| Konto med kode på mail | Sæt mailtjenesten op (`KONTO.md`, trin 1), og prøv på `#konto-test`. Derefter slås `KONTO` til i `index.html` |
| Mails om opdateringer | Opret funktionen `mails`, og kør `supabase/004-mails.sql` (`KONTO.md`, trin 2) |
| Android-appen skal kunne opdateres uden at blive afinstalleret | Lav en fast signeringsnøgle, og læg den i GitHub-secrets (se `DRIFT.md`) |
| Microsoft Store | Reservér navnet, og send de tre værdier fra Produktidentitet (se `STORE.md`). Bygningen af pakken er klar og mangler kun værdierne |
| Ret navn og by hos Punktum/one.com | "Lucas Valentin Ottesen" og "Nørresundby" |
| Nyt logo | Vælg et nummer fra 1 til 10.000 på plakaten. Så sætter `tools/logo-ud.py` det ind alle steder |
| Loading screen | Vælg et nummer fra 1 til 12 (nr. 7 bruges nu) |
| Ølspil med point | Ja eller nej. Bygges kun med point for at gætte og smage, ikke for at drikke |
| Prøv scanneren på en rigtig telefon | Tilføj øl → Scan, og Scan på forsiden. Er kun prøvet med et falsk kamera |

## Større ting, der kræver en beslutning
| Idé | Hvorfor den ikke bare er lavet |
|---|---|
| **Scan etiketten** (appen læser navn og alkoholprocent fra et billede) | Kræver tekstgenkendelse. Det bibliotek, der kan køre i browseren, fylder flere MB og skal ligge på siden. Alternativet er en betalt tjeneste. Stregkoden henter allerede navn, bryggeri og alkohol fra Open Food Facts, når øllen findes der. |
| **Smartwatch** (genstand-tæller på uret) | Kræver en helt separat app til Wear OS, som skal bygges og testes på et rigtigt ur. |
| **iPhone-app med widgets** | Kræver en Apple-udviklerkonto og en Mac til at bygge på. |
| **Når databasen bliver stor: gem den fælles liste i IndexedDB** | Alle øl og bedømmelser fra databasen ligger i localStorage, som højst kan rumme omkring 5 MB. Målt 28-11: 2.000 øl og 8.000 bedømmelser fylder 2 MB og virker fint (alle sider tegnes på under 0,1 sekund). 6.000 øl og 24.000 bedømmelser kan ikke gemmes. Når grænsen nås, kan man ikke gemme nye øl, og beskeden siger forkert, at billedet er for stort. Løsningen er at gemme databasens kopi i IndexedDB og kun egne ting i localStorage, og at hente kun det, der er ændret siden sidst (`updated_at`), i stedet for alt hvert 30. sekund. Det er en større ombygning af synkroniseringen, og der er langt til grænsen. |
| **Google Play** | Kræver en udviklerkonto hos Google (engangsbeløb) og en fast signeringsnøgle. |

## Mindre idéer
- **Afstemning om Årets øl ("Folkets valg"):** Siden Årets øl kårer vinderen ud fra årets bedømmelser. En rigtig afstemning i december, hvor alle kan stemme på én af årets fem bedste, kunne være et tillæg. Kræver en lille tabel i databasen og en beslutning om, hvordan man undgår, at nogen stemmer flere gange.
- **Prøv siden på en rigtig iPhone:** Testene kører nu i Safaris motor på GitHub, men det er ikke det samme som en iPhone i hånden. Især swipe, deling af billeder og installation på hjemmeskærmen bør prøves.
- **Besked på telefonen når en ven bedømmer en øl** (notifikationer i appen). I dag kan man få det som mail, når kontoen er slået til.
- **Fælles ønskeliste til en smagning:** Lav en smagning ud fra de øl, gruppen har på ønskelisten.
- **Moderator-side:** En skjult side, hvor ejerne kan se anmeldt indhold og slette det uden at åbne Supabase.
- **Flere byer på kortet,** eller et kort hvor man selv kan sætte prikken.
