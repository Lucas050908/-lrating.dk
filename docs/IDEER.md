# Idéer og ting, der venter

En liste over det, der ikke er lavet endnu, og hvorfor. Flyt et punkt til `CHANGELOG.md`, når det er lavet.

## Venter på Lucas
| Hvad | Hvad skal der til |
|---|---|
| Slettede billeder skal også forsvinde fra lageret | Kør `supabase/002-slet-billeder.sql` i Supabase → SQL Editor |
| http skal sende videre til https | Sæt hak i "Enforce HTTPS" under Settings → Pages på GitHub |
| Android-appen skal kunne opdateres uden at blive afinstalleret | Lav en fast signeringsnøgle, og læg den i GitHub-secrets (se `DRIFT.md`) |
| Microsoft Store | Reservér navnet, og send de tre værdier fra Produktidentitet (se `STORE.md`) |
| Ret navn og by hos Punktum/one.com | "Lucas Valentin Ottesen" og "Nørresundby" |

## Større ting, der kræver en beslutning
| Idé | Hvorfor den ikke bare er lavet |
|---|---|
| **Engelsk version** | Hver eneste tekst på siden skal oversættes og holdes ved lige i to sprog. En halv oversættelse ser sjusket ud, så det bør laves samlet. |
| **Scan etiketten** (appen læser navn og alkoholprocent fra et billede) | Kræver tekstgenkendelse. Det bibliotek, der kan køre i browseren, fylder flere MB og skal ligge på siden. Alternativet er en betalt tjeneste. |
| **Smartwatch** (genstand-tæller på uret) | Kræver en helt separat app til Wear OS, som skal bygges og testes på et rigtigt ur. |
| **iPhone-app med widgets** | Kræver en Apple-udviklerkonto og en Mac til at bygge på. |
| **Login med e-mail** | I dag er man "ejer" af sine øl på den enhed, de blev lavet på. Skifter man telefon, kan man ikke længere rette dem. Et rigtigt login løser det, men så skal siden gemme e-mailadresser. |
| **Google Play** | Kræver en udviklerkonto hos Google (engangsbeløb) og en fast signeringsnøgle. |

## Mindre idéer
- **Besked når en ven bedømmer en øl** (notifikationer). Kræver en lille server-funktion i Supabase.
- **Stregkode-opslag:** Foreslå navn og bryggeri ud fra stregkoden, når nogen allerede har tilføjet øllen.
- **Fælles ønskeliste til en smagning:** Lav en smagning ud fra de øl, gruppen har på ønskelisten.
- **Statistik for byture:** Gem ruten bagefter som et minde med de øl, der blev bedømt undervejs.
- **Moderator-side:** En skjult side, hvor ejerne kan se anmeldt indhold og slette det uden at åbne Supabase.
- **Flere byer på kortet,** eller et kort hvor man selv kan sætte prikken.
- **"Årets øl":** En afstemning i december blandt årets højest bedømte øl.
- **Del en topliste som billede,** ligesom delekortet for en enkelt øl.
