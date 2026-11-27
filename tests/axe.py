"""Kører tilgængelighedsværktøjet axe-core over alle sider på telefon og pc, på dansk og engelsk.
Kræver axe-core:  npm install --no-save axe-core@4   (stien kan sættes med AXE=/sti/til/axe.min.js)
Kør:  python3 -m http.server 8811 &   og derefter   python3 tests/axe.py
Ender med ALT OK eller en liste over regler, der er brudt, med de sider og elementer, det gælder.
Kontrast tjekkes ikke her, fordi tests/kontrast.py gør det grundigere i alle 30 kombinationer af baggrund og farver."""
import glob, json, os, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_supabase import Mock, HOST
from kontrast import SEED

URL = 'http://localhost:8811/'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXE = os.environ.get('AXE') or next(iter(glob.glob(os.path.join(ROOT, 'node_modules/axe-core/axe.min.js')) + glob.glob('/home/claude/work/node_modules/axe-core/axe.min.js')), None)
if not AXE: sys.exit('axe-core mangler. Kør: npm install --no-save axe-core@4')
PAGES = ['', '#alle', '#toplisten', '#aarets', '#swipe', '#buddies', '#hjul', '#indstillinger', '#galleri', '#sammenlign', '#byttur', '#smagning',
         '#venner', '#nyt', '#stilguide', '#profil', '#tilfoej', '#kalender', '#dagbog', '#mad', '#genstande', '#privatliv', '#om', '#beer-tb1', '#smager-Magnus']
RUN = """async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']},rules:{'color-contrast':{enabled:false},'region':{enabled:false}}});
 return r.violations.map(v=>({id:v.id,impact:v.impact,help:v.help,nodes:v.nodes.slice(0,4).map(n=>n.target.join(' ')+' :: '+(n.failureSummary||'').split('\\n').slice(1,2).join('').slice(0,120))}))}"""
src = open(AXE, encoding='utf-8').read()
found = {}
with sync_playwright() as p:
    br = getattr(p, os.environ.get('BROWSER', 'chromium')).launch()
    for w, h in ((390, 844), (1280, 900)):
        c = br.new_context(viewport={'width': w, 'height': h}, locale='da-DK', service_workers='block', reduced_motion='reduce'); c.route(f'https://{HOST}/**', Mock().handle); pg = c.new_page()
        pg.goto(URL); pg.wait_for_timeout(900); pg.evaluate(SEED.replace('LOOK', '{}')); pg.reload(); pg.wait_for_timeout(900)
        for lang in ('da', 'en'):
            if lang == 'en': pg.goto(URL + '#indstillinger'); pg.wait_for_timeout(300); pg.click('[data-setlang=en]'); pg.wait_for_timeout(900)
            for hh in PAGES:
                pg.goto(URL + hh); pg.wait_for_timeout(350)
                if not pg.evaluate('!!window.axe'): pg.add_script_tag(content=src)
                for v in pg.evaluate(RUN):
                    e = found.setdefault(v['id'], {**v, 'where': set(), 'nodes': set()}); e['where'].add(f'{w}px {lang} {hh or "#"}'); e['nodes'].update(v['nodes'])
        c.close()
    br.close()
order = {'critical': 0, 'serious': 1, 'moderate': 2, 'minor': 3}
for k, e in sorted(found.items(), key=lambda kv: order.get(kv[1]['impact'], 9)):
    print(f"BRUD {e['impact']} {k}: {e['help']} | {len(e['where'])} steder, fx {', '.join(sorted(e['where'])[:3])}")
    for n in sorted(e['nodes'])[:4]: print('   ', n)
print(f'{len(found)} regler er brudt' if found else f'ALT OK ({len(PAGES)} sider, telefon og pc, dansk og engelsk)')
sys.exit(1 if found else 0)
