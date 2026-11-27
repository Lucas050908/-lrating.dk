"""Klik på alt: åbner hver side med eksempeldata, trykker på hver slags knap én gang (på en frisk side)
og melder, hvis et tryk giver en fejl i JavaScript eller i konsollen.

Fanger knapper, som ingen anden test trykker på. Rører aldrig den rigtige database (efterlignet med mock_supabase).
Kør med siden på http://localhost:8811:  python3 tests/klik.py
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from mock_supabase import Mock, HOST
from playwright.sync_api import sync_playwright

URL = 'http://localhost:8811/'
SRC = open(os.path.join(os.path.dirname(__file__), 'test_en.py'), encoding='utf-8').read()
SEED = re.search(r'SEED="""(.*?)"""', SRC, re.S).group(1)   # samme eksempeldata som den engelske test
PAGES = ['', '#alle', '#beer-a1', '#beer-a2', '#tilfoej', '#toplisten', '#aarets', '#galleri', '#sammenlign', '#byttur', '#byttur-pasttour1',
         '#smagning', '#smagning-tastdone1', '#venner', '#buddies', '#hjul', '#swipe', '#genstande', '#stilguide', '#kalender', '#mad',
         '#dagbog', '#profil', '#indstillinger', '#nyt', '#om', '#privatliv']
# Knapper, der med vilje forlader siden eller åbner noget uden for browseren
SKIP = re.compile(r'^(exportBtn|installBtn|langBtn|menuBtn|navMore)$')

KEY = """el=>{const d=Object.keys(el.dataset).filter(k=>!/^(id|v|i|n|k)$/.test(k)).sort().join(',');
  return (el.id||'')+'|'+d+'|'+(el.id||d?'':(el.textContent||'').trim().slice(0,20))}"""

def main():
    bad = []; tried = 0
    with sync_playwright() as p:
        b = getattr(p, os.environ.get('BROWSER', 'chromium')).launch()
        for h in PAGES:
            c = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
            c.route(f'https://{HOST}/**', Mock().handle); c.route('https://*.openfoodfacts.org/**', lambda r: r.abort())
            c.add_init_script("navigator.share=undefined;navigator.canShare=undefined")
            pg = c.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:200]))
            pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' else None)
            pg.on('dialog', lambda d: d.dismiss())
            pg.goto(URL + 'robots.txt'); pg.evaluate(SEED.replace('ME', json.dumps('Lucas')).replace('LANG', json.dumps('da')))   # fra en side uden sidens kode, så intet gemmes oven i
            pg.goto(URL + h); pg.reload(); pg.wait_for_timeout(1200)
            keys = []
            for k in pg.eval_on_selector_all('#app button', f"els=>els.filter(e=>e.offsetParent&&!e.disabled).map({KEY})"):
                if k not in keys and not SKIP.match(k.split('|')[0]): keys.append(k)
            for k in keys:
                errs.clear()
                if pg.evaluate('location.hash') != (h or ''): pg.goto(URL + h)
                pg.reload(); pg.wait_for_timeout(700)
                i = pg.eval_on_selector_all('#app button', f"(els)=>els.findIndex(e=>e.offsetParent&&!e.disabled&&({KEY})(e)===" + json.dumps(k) + ")")
                if i < 0: continue
                try:
                    pg.locator('#app button').nth(i).click(timeout=2500); pg.wait_for_timeout(500); tried += 1
                except Exception as e:
                    if 'Timeout' not in str(e): errs.append('klik: ' + str(e)[:120])
                if errs: bad.append((h or '#', k, errs[:2]))
            c.close()
        b.close()
    for x in bad: print('FEJL', x)
    print(f'{tried} tryk på {len(PAGES)} sider:', 'ALT OK' if not bad else f'{len(bad)} FEJL')
    return 0 if not bad else 1

if __name__ == '__main__':
    sys.exit(main())
