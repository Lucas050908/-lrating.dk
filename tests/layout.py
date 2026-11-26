"""Tjekker layoutet på alle sider i fire bredder (320, 360, 390 og 1280 px):
  1. ingen vandret scroll,
  2. ingen knapper eller links, der ligger oven i hinanden,
  3. ingen knap eller link, der stikker ud over skærmens kant,
  4. trykflader på telefon mindst 24 × 24 px (WCAG 2.2, 2.5.8).
Kør:  python3 -m http.server 8811 &   og derefter   python3 tests/layout.py
Rører ikke den rigtige database. Ender med ALT OK eller en liste over fejl."""
import json, os, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_supabase import Mock
from kontrast import SEED

URL = 'http://localhost:8811/'; HOST = 'bbcegrufmzgfgzxazldr.supabase.co'
PAGES = ['', '#alle', '#toplisten', '#aarets', '#swipe', '#buddies', '#hjul', '#indstillinger', '#galleri', '#sammenlign', '#byttur', '#smagning',
         '#venner', '#nyt', '#stilguide', '#profil', '#tilfoej', '#kalender', '#dagbog', '#mad', '#genstande', '#privatliv', '#om', '#beer-tb1', '#smager-Magnus']
CHECK = r"""(mobile)=>{const out=[],W=document.documentElement.clientWidth;
 if(document.documentElement.scrollWidth>W+1)out.push('vandret scroll: '+document.documentElement.scrollWidth+' > '+W);
 const vis=e=>{const r=e.getBoundingClientRect(),cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&cs.display!=='none'&&+cs.opacity>0.05&&!e.closest('[aria-hidden=true],#load,.nav:not(.open),.navdd,.langdd,details:not([open]) > :not(summary)')};
 const C=[...document.querySelectorAll('#app a[href],#app button,#app input:not([type=hidden]),#app select,#app summary,#app label.btn')].filter(vis);
 const name=e=>(e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+' «'+(e.innerText||e.value||e.getAttribute('aria-label')||'').trim().slice(0,24)+'»');
 const scroller=e=>{for(let x=e.parentElement;x&&x!==document.body;x=x.parentElement){const o=getComputedStyle(x).overflowX;if(o==='auto'||o==='scroll')return true}return false};
 const inText=e=>getComputedStyle(e).display==='inline'&&[...e.parentElement.childNodes].some(n=>n!==e&&n.nodeType===3&&n.textContent.trim().length>1);   /* et link midt i en sætning: undtaget i WCAG 2.5.8 */
 const labelled=e=>e.matches('input')&&[...(e.labels||[])].some(l=>{const r=l.getBoundingClientRect();return r.width>=24&&r.height>=24});   /* hele etiketten kan trykkes på */
 for(const e of C){const r=e.getBoundingClientRect();if(scroller(e))continue;   /* fx stilarterne, der kan swipes til siden på telefon */
   if(r.right>W+1||r.left<-1)out.push('uden for kanten: '+name(e)+' '+Math.round(r.left)+'–'+Math.round(r.right));
   if(mobile&&(r.width<24||r.height<24)&&!inText(e)&&!labelled(e)&&!e.closest('p,li,td,.meta,small,.cf,.budl,.rv,.tcard span'))out.push('for lille trykflade: '+name(e)+' '+Math.round(r.width)+'×'+Math.round(r.height))}
 for(let i=0;i<C.length;i++)for(let j=i+1;j<C.length;j++){const a=C[i],b=C[j];if(a.contains(b)||b.contains(a))continue;
   let x=0,y=0;for(const p of a.getClientRects())for(const q of b.getClientRects()){const X=Math.min(p.right,q.right)-Math.max(p.left,q.left),Y=Math.min(p.bottom,q.bottom)-Math.max(p.top,q.top);if(X>3&&Y>3&&X*Y>x*y){x=X;y=Y}}   /* hver linje for sig, så et link, der brydes over to linjer, ikke tæller som et stort felt */
   if(x>3&&y>3){if(a.control===b||b.control===a||(a.tagName==='LABEL'&&a.contains(b))||(a.type==='radio'&&b.type==='radio'))continue;out.push('overlapper: '+name(a)+' og '+name(b)+' ('+Math.round(x)+'×'+Math.round(y)+' px)')}}
 return out}"""

bad = []
with sync_playwright() as p:
    br = getattr(p, os.environ.get('BROWSER', 'chromium')).launch(); M = Mock()
    for w, h in ((320, 640), (360, 740), (390, 844), (1280, 900)):
        c = br.new_context(viewport={'width': w, 'height': h}, locale='da-DK', service_workers='block', reduced_motion='reduce'); c.route(f'https://{HOST}/**', M.handle); pg = c.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(1000); pg.evaluate(SEED.replace('LOOK', json.dumps({}))); pg.reload(); pg.wait_for_timeout(900)
        for lang in ('da', 'en'):
            if lang == 'en': pg.goto(URL + '#indstillinger'); pg.wait_for_timeout(300); pg.click('[data-setlang=en]'); pg.wait_for_timeout(900)
            for pgh in PAGES:
                pg.goto(URL + pgh); pg.wait_for_timeout(300)
                for f in pg.evaluate(CHECK, w < 600): bad.append(f'{w}px {lang} {pgh or "#"}: {f}')
        bad += [f'{w}px JS-fejl: {e}' for e in errs]
        c.close()
    br.close()
seen = set()
for b in bad:
    if b not in seen: seen.add(b); print('FEJL', b)
print(f'{len(seen)} fejl' if seen else f'ALT OK ({len(PAGES)} sider, 4 bredder, dansk og engelsk)')
sys.exit(1 if seen else 0)
