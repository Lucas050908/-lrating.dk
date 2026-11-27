# ølrating.dk

Danske øl, bedømt af dem der drikker dem.

**Adresse:** https://ølrating.dk (teknisk navn `xn--lrating-p1a.dk`)
**Ejere:** Lucas Valentin Ottesen og Magnus Birkgaard Froberg
**Fejl og forslag:** andersenlucas84@gmail.com

## Dokumentation

| Dokument | Indhold |
|---|---|
| [docs/FUNKTIONER.md](docs/FUNKTIONER.md) | Alt hvad siden og apps kan, side for side |
| [docs/TEKNIK.md](docs/TEKNIK.md) | Hvordan det er bygget: filer, data, sider, bro til apps, widgets, byggeprocesser |
| [docs/STORE.md](docs/STORE.md) | Microsoft Store: trin for trin, tekster og skærmbilleder |
| [docs/KONTO.md](docs/KONTO.md) | Konto og mails: opsætning trin for trin (mailtjeneste, Supabase, test) |
| [docs/DRIFT.md](docs/DRIFT.md) | Domæne, DNS, GitHub Pages, HTTPS, database, app-signering, Microsoft Store, huskeliste |
| [docs/IDEER.md](docs/IDEER.md) | Det, der venter, og idéer til senere |
| [CHANGELOG.md](CHANGELOG.md) | Hvad der er lavet hvornår |

> **Regel:** Hver gang der laves noget nyt, opdateres `CHANGELOG.md` og det relevante dokument i `docs/` i samme commit.

## Kort fortalt

- **Hjemmeside:** én fil (`index.html`) uden server og byggetrin, hostet gratis på GitHub Pages. Dansk som standard, og engelsk med flaget øverst på siden. Design og farver vælges under Indstillinger.
- **Apps:**
  - Android-app (`android/`), med 8 widgets (to af dem med billeder af øllene, én med tal for hele siden).
  - Program til Windows og Linux (`desktop/`), med en widget der ligger øverst på skærmen.
  - På iPhone kan siden lægges på hjemmeskærmen.
- **Data:** øl, bedømmelser, billeder og byture ligger i en fælles database (Supabase, EU), så alle ser det samme. Genstand-tæller og indstillinger bliver på enheden. Se [docs/DRIFT.md](docs/DRIFT.md#fælles-database-supabase).
- **Downloads:**
  - Android: https://github.com/Lucas050908/-lrating.dk/releases/download/android-app/olrating.apk
  - Windows: https://github.com/Lucas050908/-lrating.dk/releases/download/desktop-app/olrating-windows.exe
  - Linux: https://github.com/Lucas050908/-lrating.dk/releases/download/desktop-app/olrating-linux.AppImage

## Mapper

| Sti | Hvad |
|---|---|
| `index.html` | Hele hjemmesiden: design, sider og logik |
| `sw.js`, `manifest.webmanifest` | Installerbar app (PWA) og offline |
| `img/`, `fonts/`, `js/qr.js` | Billeder, ikoner, skrifttyper, QR-kode-bibliotek (MIT) |
| `img/logoer/` | 200 logo-forslag (SVG). Det valgte sættes ind alle steder med `tools/logo-ud.py` |
| `tools/` | `logoer.py` laver de 200 logoer, `logo-ud.py` skifter logo på siden og i apps |
| `js/en.js` | Den engelske ordbog. Hentes kun, når man vælger English |
| `404.html`, `CNAME`, `robots.txt`, `sitemap.xml` | Fejlside, domæne og søgemaskiner |
| `android/` | Android-app og widgets |
| `desktop/` | Windows/Linux-program (Electron) og desktop-widget |
| `supabase/` | Database-tabeller og sikkerhedsregler, og funktionen der sender mails (`functions/mails`) |
| `tests/` | Automatiske test af siden og databasen, og tjek af layout, kontrast og tilgængelighed (`layout.py`, `kontrast.py`, `axe.py`) |
| `.github/workflows/` | Automatisk bygning af Android- og desktop-app (også pakken til Microsoft Store) og automatiske test |
| `docs/` | Dokumentation |
| `store/` | Skærmbilleder til Microsoft Store (opdigtede eksempler) |

Fotos: Lucas, Limfjorden.
