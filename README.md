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
| [docs/DRIFT.md](docs/DRIFT.md) | Domæne, DNS, GitHub Pages, HTTPS, database, app-signering, Microsoft Store, huskeliste |
| [CHANGELOG.md](CHANGELOG.md) | Hvad der er lavet hvornår |

> **Regel:** Hver gang der laves noget nyt, opdateres `CHANGELOG.md` og det relevante dokument i `docs/` i samme commit.

## Kort fortalt

- **Hjemmeside:** én fil (`index.html`) uden server og byggetrin, hostet gratis på GitHub Pages.
- **Apps:**
  - Android-app (`android/`), med 6 widgets.
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
| `404.html`, `CNAME`, `robots.txt`, `sitemap.xml` | Fejlside, domæne og søgemaskiner |
| `android/` | Android-app og widgets |
| `desktop/` | Windows/Linux-program (Electron) og desktop-widget |
| `supabase/` | Database-tabeller og sikkerhedsregler |
| `tests/` | Automatiske test af siden og databasen |
| `.github/workflows/` | Automatisk bygning af Android- og desktop-app |
| `docs/` | Dokumentation |

Fotos: Lucas, Limfjorden.
