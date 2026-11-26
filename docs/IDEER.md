# Idéer og ting, der venter

En liste over det, der ikke er lavet endnu, og hvorfor. Flyt et punkt til `CHANGELOG.md`, når det er lavet.

## Venter på Lucas
| Hvad | Hvad skal der til |
|---|---|
| Android-appen skal kunne opdateres uden at blive afinstalleret | Lav en fast signeringsnøgle, og læg den i GitHub-secrets (se `DRIFT.md`) |
| Microsoft Store | Reservér navnet, og send de tre værdier fra Produktidentitet (se `STORE.md`). Bygningen af pakken er klar og mangler kun værdierne |
| Ret navn og by hos Punktum/one.com | "Lucas Valentin Ottesen" og "Nørresundby" |

## Større ting, der kræver en beslutning
| Idé | Hvorfor den ikke bare er lavet |
|---|---|
| **Scan etiketten** (appen læser navn og alkoholprocent fra et billede) | Kræver tekstgenkendelse. Det bibliotek, der kan køre i browseren, fylder flere MB og skal ligge på siden. Alternativet er en betalt tjeneste. |
| **Smartwatch** (genstand-tæller på uret) | Kræver en helt separat app til Wear OS, som skal bygges og testes på et rigtigt ur. |
| **iPhone-app med widgets** | Kræver en Apple-udviklerkonto og en Mac til at bygge på. |
| **Login med e-mail** | I dag er man "ejer" af sine øl på den enhed, de blev lavet på. Skifter man telefon, kan man ikke længere rette dem. Et rigtigt login løser det, men så skal siden gemme e-mailadresser. |
| **Google Play** | Kræver en udviklerkonto hos Google (engangsbeløb) og en fast signeringsnøgle. |

## Mindre idéer
- **Engelske widgets:** Siden er oversat til engelsk, men widgets i Android-appen og på skrivebordet er kun på dansk.
- **Afstemning om Årets øl:** Siden Årets øl kårer vinderen ud fra årets bedømmelser. En rigtig afstemning i december kunne være et tillæg.
- **Besked når en ven bedømmer en øl** (notifikationer). Kræver en lille server-funktion i Supabase.
- **Fælles ønskeliste til en smagning:** Lav en smagning ud fra de øl, gruppen har på ønskelisten.
- **Moderator-side:** En skjult side, hvor ejerne kan se anmeldt indhold og slette det uden at åbne Supabase.
- **Flere byer på kortet,** eller et kort hvor man selv kan sætte prikken.
