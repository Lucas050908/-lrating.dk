# Microsoft Store

Alt, der skal bruges for at få ølrating i Microsoft Store. Teksterne kan kopieres direkte ind i Partner Center.

## Status
- [x] Udviklerkonto hos Microsoft (Lucas)
- [x] Tekster og skærmbilleder på dansk og engelsk (denne fil og mappen `store/`)
- [x] Bygning af pakken er sat op på GitHub (`desktop/store-build.js`), med ikoner til Store i `desktop/build/appx/`
- [ ] Navnet reserveret i Partner Center
- [ ] De tre værdier fra *Produktidentitet* lagt ind i `desktop/store.json`
- [ ] Pakke (`olrating-store.appx`) uploadet
- [ ] Indsendt til godkendelse

## Trin for trin
1. **Partner Center** (partner.microsoft.com) → Apps og spil → Nyt produkt → MSIX- eller PWA-app.
2. **Reservér navnet** `ølrating`. Er det optaget, så prøv `ølrating.dk`.
3. **Produktstyring → Produktidentitet:** Kopiér de tre værdier herunder, og send dem til udvikleren. De er ikke hemmelige.
   - `Package/Identity/Name`
   - `Package/Identity/Publisher` (starter med `CN=`)
   - `Package/Properties/PublisherDisplayName`
4. Udvikleren lægger værdierne i `desktop/store.json`. Så bygger GitHub pakken `olrating-store.appx`, som kan hentes under udgivelsen `desktop-app`.
5. **Pakker:** Upload `olrating-store.appx`. Pakken skal ikke signeres. Det gør Microsoft selv, når den bliver indsendt.
   - Bliver du spurgt om tilladelsen `runFullTrust`, så skriv: "Appen er en Electron-app, der er pakket som skrivebordsprogram, og den kræver derfor runFullTrust."

6. **Egenskaber:** Kategori *Mad og spisning* (eller *Livsstil*). Privatlivspolitik: `https://ølrating.dk/#privatliv`. Support: `https://ølrating.dk/#om`.
7. **Aldersklassificering:** Udfyld spørgeskemaet. Appen handler om alkohol og har indhold, som brugerne selv skriver, så svar ja til begge. Det giver en høj aldersgrænse, og det er meningen.
8. **Butiksside:** Indsæt teksterne og skærmbillederne herunder.
9. **Indsend.** Microsoft gennemgår typisk appen på 1 til 3 hverdage.

## Sådan bygges pakken
- `desktop/store.json` indeholder de tre værdier fra Partner Center og appens navn i Store (`displayName`). Navnet skal være præcis det, der er reserveret. Værdierne er ikke hemmelige.
- Workflowet *Desktop-app* kører `npm run dist:store` på Windows. Det bygger en `.appx`-pakke med electron-builder.
- Er `store.json` ikke udfyldt, bygges i stedet prøvepakken `olrating-store-TEST.appx` med testværdier. Den viser kun, at bygningen virker, og den bliver ikke lagt ud til download.
- **Ny version til Store:** Hæv `version` i `desktop/package.json` (fx fra 1.0.0 til 1.0.1). Store afviser en pakke med samme versionsnummer som den forrige.
- Ikonerne til Store ligger i `desktop/build/appx/` og er lavet ud fra app-ikonet.

## Tekster til butikssiden (dansk)

**Navn:** ølrating

**Kort beskrivelse (højst 200 tegn):**
Bedøm de øl, du drikker, med billede og karakter. Se toplisten, hold smagning med vennerne, planlæg bytur, og følg med i hvad de andre smager.

**Beskrivelse:**
ølrating er stedet for dig, der godt kan lide øl og gerne vil huske, hvad du har smagt.

Tag et billede af øllen, giv den karakter fra 1 til 5 for udseende, duft, smag, fylde og helhed, og se hvad andre mener om den. Alle bedømmelser samles i en fælles topliste.

Det kan du:
• Bedømme øl med billede, smagsord og smagsprofil
• Se toplisten, også kun for lyse, mørke eller alkoholfri øl
• Se årets øl, årets bryggeri og årets stil
• Få forslag til øl, du nok vil kunne lide, ud fra dine egne karakterer
• Holde blindsmagning med vennerne, hvor alle stemmer på deres egen telefon
• Planlægge en bytur med rute, tidspunkter og tilmelding, og gemme den som et minde bagefter
• Følge dine venner og se, hvem du er mest enig med
• Holde øje med dine genstande med en tæller, der bygger på Sundhedsstyrelsens anbefalinger
• Have en lille widget på skrivebordet med ugens øl og toplisten

ølrating har ingen reklamer og ingen sporing. Du skal ikke oprette en konto. Appen findes på dansk og engelsk.

Nyd øl med omtanke. Appen er for voksne.

**Nyheder i denne version:**
Første version i Microsoft Store.

**Søgeord (højst 7):** øl, ølbedømmelse, bryggeri, smagning, topliste, bytur, craft beer

**Funktioner (korte punkter):**
- Bedøm øl med billede og karakter
- Fælles topliste
- Blindsmagning med venner
- Byttur med rute og tilmelding
- Widget med ugens øl
- Genstand-tæller

## Tekster til butikssiden (engelsk)
Appen findes nu også på engelsk. Tilføj sproget **English** under butikssider i Partner Center, og brug teksterne her.

**Name:** ølrating

**Short description (max. 200 characters):**
Rate the beers you drink with a photo and a score. See the top list, hold tastings with friends, plan a pub crawl, and follow what the others are tasting.

**Description:**
ølrating is the place for people who like beer and want to remember what they have tasted.

Take a photo of the beer, rate it from 1 to 5 for look, aroma, taste, body and overall, and see what others think of it. All ratings are gathered in a shared top list.

What you can do:
• Rate beers with a photo, tasting notes and a flavour profile
• See the top list, also for pale, dark or alcohol-free beers only
• See the beer, brewery and style of the year
• Get suggestions for beers you will probably like, based on your own ratings
• Hold a blind tasting with friends, where everyone votes on their own phone
• Plan a pub crawl with a route, times and sign-up, and keep it as a memory afterwards
• Follow your friends and see who you agree with the most
• Keep track of your units with a counter based on the Danish Health Authority's recommendations
• Keep a small widget on the desktop with the beer of the week and the top list

ølrating has no ads and no tracking. You don't need to create an account. The app is available in Danish and English.

Enjoy beer responsibly. The app is for adults.

**What's new in this version:**
First version in Microsoft Store.

**Search terms (max. 7):** beer, beer rating, brewery, tasting, top list, pub crawl, craft beer

**Features (short points):**
- Rate beers with a photo and a score
- Shared top list and Beer of the year
- Blind tasting with friends
- Pub crawl with route and sign-up
- Widget with the beer of the week
- Unit counter

## Skærmbilleder
Ligger i mappen `store/` (dansk) og `store/en/` (engelsk) i størrelsen 1366 × 768, som Store kræver som minimum. De laves med `python3 store/lav-skaermbilleder.py`, så de kan laves om, når siden ændrer sig.

| Fil | Viser |
|---|---|
| `1-forside.png` | Forsiden med ugens øl |
| `2-alle-oel.png` | Listen over øl og toplisten |
| `3-oel.png` | En øl med oplysninger |
| `4-smagning.png` | Resultatet af en blindsmagning |
| `5-byttur.png` | En bytur med rute og deltagere |
| `6-profil.png` | Min profil |
| `7-aarets-oel.png` | Årets øl |

**Bemærk:** Øllene, bryggerierne, barerne og navnene på billederne er opdigtede eksempler, lavet kun til skærmbillederne. De findes ikke på den rigtige side. Skift dem gerne ud med rigtige skærmbilleder, når der er kommet øl på ølrating.dk.

## Logo
Store laver selv de fleste størrelser ud fra app-ikonet. Brug `img/icon-512.png`, hvis der bliver bedt om et billede.
