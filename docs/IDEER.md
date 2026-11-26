# Idéer og ting, der venter

En liste over det, der ikke er lavet endnu, og hvorfor. Flyt et punkt til `CHANGELOG.md`, når det er lavet.

## Venter på Lucas
| Hvad | Hvad skal der til |
|---|---|
| "Enig eller uenig?" skal deles mellem telefoner | Kør `supabase/003-konto-mails-enig.sql` i Supabase → SQL Editor |
| Konto med kode på mail | Sæt mailtjenesten op (`KONTO.md`, trin 1), og prøv på `#konto-test`. Derefter slås `KONTO` til i `index.html` |
| Mails om opdateringer | Opret funktionen `mails`, og kør `supabase/004-mails.sql` (`KONTO.md`, trin 2) |
| Android-appen skal kunne opdateres uden at blive afinstalleret | Lav en fast signeringsnøgle, og læg den i GitHub-secrets (se `DRIFT.md`) |
| Microsoft Store | Reservér navnet, og send de tre værdier fra Produktidentitet (se `STORE.md`). Bygningen af pakken er klar og mangler kun værdierne |
| Ret navn og by hos Punktum/one.com | "Lucas Valentin Ottesen" og "Nørresundby" |

## Større ting, der kræver en beslutning
| Idé | Hvorfor den ikke bare er lavet |
|---|---|
| **Scan etiketten** (appen læser navn og alkoholprocent fra et billede) | Kræver tekstgenkendelse. Det bibliotek, der kan køre i browseren, fylder flere MB og skal ligge på siden. Alternativet er en betalt tjeneste. |
| **Smartwatch** (genstand-tæller på uret) | Kræver en helt separat app til Wear OS, som skal bygges og testes på et rigtigt ur. |
| **iPhone-app med widgets** | Kræver en Apple-udviklerkonto og en Mac til at bygge på. |
| **Google Play** | Kræver en udviklerkonto hos Google (engangsbeløb) og en fast signeringsnøgle. |

## Mindre idéer
- **Engelske widgets:** Siden er oversat til engelsk, men widgets i Android-appen og på skrivebordet er kun på dansk.
- **Afstemning om Årets øl:** Siden Årets øl kårer vinderen ud fra årets bedømmelser. En rigtig afstemning i december kunne være et tillæg.
- **Besked på telefonen når en ven bedømmer en øl** (notifikationer i appen). I dag kan man få det som mail, når kontoen er slået til.
- **Fælles ønskeliste til en smagning:** Lav en smagning ud fra de øl, gruppen har på ønskelisten.
- **Moderator-side:** En skjult side, hvor ejerne kan se anmeldt indhold og slette det uden at åbne Supabase.
- **Flere byer på kortet,** eller et kort hvor man selv kan sætte prikken.
