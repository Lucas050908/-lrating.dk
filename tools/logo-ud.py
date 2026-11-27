#!/usr/bin/env python3
"""Sætter ét af de 10.000 logoer ind alle steder: siden, Android-appen, Windows/Linux og fliserne til Microsoft Store.

Brug (fra roden af repoet):
    python3 tools/logo-ud.py 56            sætter logo nr. 56 ind
    python3 tools/logo-ud.py 56 --vis      ændrer ingenting, men lægger alle filerne i /tmp/logo-vis og et samlet billede i /tmp/logo-vis/ark.png

Nummeret er det samme som i img/logoer/200 (1 til 200) og img/logoer/1000 (1 til 1000). Nr. 1001 til 10000 findes kun på plakaten og tegnes af tools/logoer.py. Scriptet tegner logoet med tools/logoer.py og laver:
  img/favicon.svg, img/logo.svg, img/icon-192.png, img/icon-512.png, img/icon-maskable.png, img/apple-touch-icon.png,
  Android: mipmap-*/ic_launcher*.png og farven icon_bg, Windows/Linux: desktop/build/icon.png og desktop/build/appx/*.png.
Kræver Playwright og Pillow, som testene også bruger. Husk bagefter: hæv versionen i sw.js, og skriv det i CHANGELOG.md.
"""
import io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logoer import MOTIV, STIL, DEFS, nr, build  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENS = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
APPX = {'Square44x44Logo.png': (44, 44), 'StoreLogo.png': (50, 50), 'SmallTile.png': (71, 71), 'Square150x150Logo.png': (150, 150),
        'LargeTile.png': (310, 310), 'Wide310x150Logo.png': (310, 150), 'SplashScreen.png': (620, 300)}


def parts(n):
    """Motiv, stil og de stumper, logoet er bygget af."""
    if not 1 <= n <= 10000: sys.exit('Nummeret skal være mellem 1 og 10000.')
    (slug, navn, mf), st = nr(n)
    r = mf(st[5]); body, extra = r if isinstance(r, tuple) else (r, '')
    return slug, navn, st, body, extra


def svg(inner, w=120, h=120, extra=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="ølrating.dk"><defs>{DEFS}{extra}</defs>{inner}</svg>'


def logo(st, body, extra):
    """Logoet, som det er tegnet: firkant, cirkel, sekskant, ottekant eller skjold, evt. med ring (tegnes af logoer.build)."""
    return build(lambda p: (body, extra), st)


def flade(st, body, extra, w, h, k):
    """Baggrunden helt ud til kanten og motivet i midten. k = hvor meget af den korte side motivet fylder."""
    s = min(w, h) * k / 120
    return svg(f'<rect width="{w}" height="{h}" fill="{st[3]}"/><g transform="translate({w / 2} {h / 2}) scale({s:.4f}) translate(-60 -60)">{body}</g>', w, h, extra)


def mono_svg(n):
    """Motivet i hvidt på sort. Bruges til Androids ensfarvede ikon, hvor hvidt bliver til ikonets form."""
    from types import SimpleNamespace as NS
    (_, _, mf), _ = nr(n)
    W = '#ffffff'; K = '#000000'
    p = NS(m=W, ms=W, b=W, a=W, c=K, i=W, f=W, fs=None, w=W, l=W, x=W, d=K, fl=[W] * 4)
    r = mf(p); body, extra = r if isinstance(r, tuple) else (r, '')
    return svg(f'<rect width="108" height="108" fill="{K}"/><g transform="translate(54 54) scale(.5) translate(-60 -60)">{body}</g>', 108, 108, extra)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) != 1 or not a[0].isdigit(): sys.exit(__doc__)
    n = int(a[0]); vis = '--vis' in sys.argv
    out = '/tmp/logo-vis' if vis else ROOT
    slug, navn, st, body, extra = parts(n)
    from playwright.sync_api import sync_playwright
    from PIL import Image

    made = []

    def put(rel, data):
        p = os.path.join(out, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data if isinstance(data, bytes) else data.encode('utf-8')); made.append(rel)

    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page()

        def png(s, w, h, alpha=True):
            w = round(w); h = round(h); pg.set_viewport_size({'width': w, 'height': h})
            pg.set_content(f'<body style="margin:0;background:transparent">{s.replace("<svg ", f"<svg width=\'{w}\' height=\'{h}\' style=\'display:block\' ", 1)}</body>')
            raw = pg.screenshot(clip={'x': 0, 'y': 0, 'width': w, 'height': h}, omit_background=True)
            im = Image.open(io.BytesIO(raw)); im = im if alpha else im.convert('RGB')
            o = io.BytesIO(); im.save(o, 'PNG', optimize=True); return o.getvalue()

        full = logo(st, body, extra)
        put('img/favicon.svg', full); put('img/logo.svg', full)
        fl = lambda w, h, k: flade(st, body, extra, w, h, k)
        put('img/icon-192.png', png(fl(192, 192, .8), 192, 192, False)); put('img/icon-512.png', png(fl(512, 512, .8), 512, 512, False))
        put('img/icon-maskable.png', png(fl(512, 512, .62), 512, 512, False)); put('img/apple-touch-icon.png', png(fl(180, 180, .8), 180, 180, False))
        put('desktop/build/icon.png', png(fl(512, 512, .8), 512, 512, False))
        for name, (w, h) in APPX.items(): put('desktop/build/appx/' + name, png(fl(w, h, .78 if w == h else .7), w, h, False))
        rund = svg(f'<clipPath id="ru"><circle cx="60" cy="60" r="60"/></clipPath><g clip-path="url(#ru)"><rect width="120" height="120" fill="{st[3]}"/><g transform="translate(60 60) scale(.8) translate(-60 -60)">{body}</g></g>', extra=extra)
        for d, k in DENS.items():
            base = f'android/app/src/main/res/mipmap-{d}/'
            put(base + 'ic_launcher.png', png(full, 48 * k, 48 * k)); put(base + 'ic_launcher_round.png', png(rund, 48 * k, 48 * k))
            put(base + 'ic_launcher_foreground.png', png(fl(108, 108, .56), 108 * k, 108 * k, False))
            m = Image.open(io.BytesIO(png(mono_svg(n), 108 * k, 108 * k, False))).convert('L')
            im = Image.new('RGBA', m.size, (255, 255, 255, 0)); im.putalpha(m); o = io.BytesIO(); im.save(o, 'PNG', optimize=True); put(base + 'ic_launcher_mono.png', o.getvalue())
        # Baggrundsfarven bag Androids adaptive ikon: stilens farve, eller den midterste farve i et farveforløb
        bgc = st[3] if st[3].startswith('#') else {'url(#s)': '#ff7a3d', 'url(#b)': '#2f5a8e', 'url(#gk)': '#c8692e', 'url(#gt)': '#155a63', 'url(#gn)': '#24306a', 'url(#gc)': '#e8704f'}.get(st[3], '#0f1d36')
        col = os.path.join(ROOT, 'android/app/src/main/res/values/styles.xml')
        if os.path.exists(col):
            t = open(col, encoding='utf-8').read(); t2 = re.sub(r'(<color name="icon_bg">)#[0-9A-Fa-f]{6,8}(</color>)', rf'\g<1>{bgc.upper()}\g<2>', t)
            if t2 != t or vis: put('android/app/src/main/res/values/styles.xml', t2)
        if vis:
            vis_files = ['img/icon-512.png', 'img/icon-maskable.png', 'android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png', 'android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png',
                         'android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_foreground.png', 'android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_mono.png', 'desktop/build/appx/Wide310x150Logo.png', 'desktop/build/appx/Square44x44Logo.png']
            html = '<body style="margin:0;background:#8a93a6;display:flex;gap:14px;padding:14px;align-items:center;flex-wrap:wrap;width:1180px"><img src="img/favicon.svg" width="200">' + ''.join(f'<img src="{f}" style="max-height:200px">' for f in vis_files) + '</body>'
            put('ark.html', html); pg.set_viewport_size({'width': 1210, 'height': 500}); pg.goto('file://' + os.path.join(out, 'ark.html')); pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(out, 'ark.png'), full_page=True)
        b.close()
    print(f'Logo nr. {n}: {navn} i stilen {st[1]}. {len(made)} filer skrevet til {out}.')
    if not vis: print('Husk: hæv versionen i sw.js, kør testene, og skriv det i CHANGELOG.md og docs/TEKNIK.md.')


if __name__ == '__main__':
    main()
