# Microsoft Store

Alt, der skal bruges for at få ølrating i Microsoft Store. Teksterne kan kopieres direkte ind i Partner Center.

## Status
- [x] Udviklerkonto hos Microsoft (Lucas)
- [x] Tekster og skærmbilleder (denne fil og mappen `store/`)
- [ ] Navnet reserveret i Partner Center
- [ ] De tre værdier fra *Produktidentitet* lagt ind i `desktop/package.json`
- [ ] Pakke (.msix) bygget og uploadet
- [ ] Indsendt til godkendelse

## Trin for trin
1. **Partner Center** (partner.microsoft.com) → Apps og spil → Nyt produkt → MSIX- eller PWA-app.
2. **Reservér navnet** `ølrating`. Er det optaget, så prøv `ølrating.dk`.
3. **Produktstyring → Produktidentitet:** Kopiér de tre værdier herunder, og send dem til udvikleren. De er ikke hemmelige.
   - `Package/Identity/Name`
   - `Package/Identity/Publisher` (starter med `CN=`)
   - `Package/Properties/PublisherDisplayName`
4. Udvikleren lægger værdierne i `desktop/package.json`. Så bygger GitHub en `.msix`-pakke, som kan hentes under udgivelsen `desktop-app`.
5. **Pakker:** Upload `.msix`-filen.
6. **Egenskaber:** Kategori *Mad og spisning* (eller *Livsstil*). Privatlivspolitik: `https://ølrating.dk/#privatliv`. Support: `https://ølrating.dk/#om`.
7. **Aldersklassificering:** Udfyld spørgeskemaet. Appen handler om alkohol og har indhold, som brugerne selv skriver, så svar ja til begge. Det giver en høj aldersgrænse, og det er meningen.
8. **Butiksside:** Indsæt teksterne og skærmbillederne herunder.
9. **Indsend.** Microsoft gennemgår typisk appen på 1 til 3 hverdage.

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
• Få forslag til øl, du nok vil kunne lide, ud fra dine egne karakterer
• Holde blindsmagning med vennerne, hvor alle stemmer på deres egen telefon
• Planlægge en bytur med rute, tidspunkter og tilmelding
• Følge dine venner og se, hvem du er mest enig med
• Holde øje med dine genstande med en tæller, der bygger på Sundhedsstyrelsens anbefalinger
• Have en lille widget på skrivebordet med ugens øl og toplisten

ølrating har ingen reklamer og ingen sporing. Du skal ikke oprette en konto.

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

## Skærmbilleder
Ligger i mappen `store/` i størrelsen 1366 × 768, som Store kræver som minimum.

| Fil | Viser |
|---|---|
| `1-forside.png` | Forsiden med ugens øl |
| `2-alle-oel.png` | Listen over øl |
| `3-oel.png` | En øl med oplysninger |
| `4-smagning.png` | Resultatet af en blindsmagning |
| `5-byttur.png` | En bytur med rute og deltagere |
| `6-profil.png` | Min profil med forslag |

**Bemærk:** Øllene, bryggerierne og navnene på billederne er opdigtede eksempler, lavet kun til skærmbillederne. De findes ikke på den rigtige side. Skift dem gerne ud med rigtige skærmbilleder, når der er kommet øl på ølrating.dk.

## Logo
Store laver selv de fleste størrelser ud fra app-ikonet. Brug `img/icon-512.png`, hvis der bliver bedt om et billede.
