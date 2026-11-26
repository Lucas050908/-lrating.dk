"""Måler kontrasten mellem tekst og baggrund på de vigtigste sider i alle kombinationer af baggrund og farver
(6 × 5 = 30). Kravet er WCAG AA: mindst 4,5:1 for almindelig tekst og 3:1 for stor tekst (24 px, eller 18,7 px fed).
Tekst oven på billeder og farveforløb måles mod forløbets lyseste og mørkeste farve, når de kan læses; ellers springes den over.

Kør:  python3 -m http.server 8811 &   og derefter   python3 tests/kontrast.py        (alle 30)
                                                    python3 tests/kontrast.py nat std  (kun én kombination)
Scriptet rører ikke den rigtige database. Det ender med ALT OK eller en liste over det, der er for svagt."""
import json, os, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_supabase import Mock

URL = 'http://localhost:8811/'; HOST = 'bbcegrufmzgfgzxazldr.supabase.co'
BG = ['nat', 'fjord', 'skov', 'aften', 'stout', 'kul']; ACC = ['std', 'hav', 'skov', 'baer', 'guld']
PAGES = ['', '#toplisten', '#beer-tb1', '#profil', '#hjul', '#indstillinger', '#buddies', '#om', '#genstande', '#tilfoej', '#swipe', '#smagning', '#byttur', '#nyt']
SEED = """(()=>{const d=new Date().toISOString().slice(0,10),S=JSON.parse(localStorage.getItem('olrating-v1')||'{}');S.me='Lucas';S.langSet=1;
 S.beers=[{id:'tb1',name:'Testøl',brewery:'Bryg',style:'Pilsner',abv:4.6},{id:'tb2',name:'Mørk ale',brewery:'Bryg',style:'Stout',abv:6},{id:'tb3',name:'Fri',brewery:'Andet',style:'IPA',abv:0.5,af:true}];
 const r=(id,b,w,v)=>({id,beer:b,who:w,date:d,s:{look:v,aroma:v,taste:v,feel:v,overall:v},tags:['bitter'],again:1,text:'God øl'});
 S.reviews=[r('r1','tb1','Lucas',4),r('r2','tb2','Lucas',3.5),r('r3','tb1','Magnus',4.2),r('r4','tb2','Magnus',3),r('r5','tb3','Magnus',4.5)];S.wish=['tb1','tb3'];S.follow=['Magnus'];
 S.look=LOOK;localStorage.setItem('olrating-v1',JSON.stringify(S))})()"""
MEASURE = r"""(()=>{
 const P=s=>{const m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\/ ]+/).filter(Boolean).map(Number);return [a[0],a[1],a[2],a.length>3?a[3]:1]};
 const lum=c=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])};
 const over=(f,b)=>[0,1,2].map(i=>f[i]*f[3]+b[i]*(1-f[3])).concat(1);
 const ratio=(a,b)=>{const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
 const bgOf=el=>{const st=[];let img=null;for(let e=el;e;e=e.parentElement){const cs=getComputedStyle(e);if(cs.backgroundImage!=='none'&&!img)img=cs.backgroundImage;const c=P(cs.backgroundColor);if(c&&c[3]>0){st.push(c);if(c[3]>=1)break}}
   let b=[15,29,54,1];for(let i=st.length-1;i>=0;i--)b=over(st[i],b);return {b,img,n:st.length}};
 const out=[],seen=new Set();
 for(const el of document.querySelectorAll('body *')){
   if(['SCRIPT','STYLE','SVG','PATH','CANVAS','OPTION'].includes(el.tagName.toUpperCase())||el.closest('svg,#load,[aria-hidden=true],.ring'))continue;   /* .ring: tallet står på en mørk skive, der er tegnet med ::before */
   const t=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).map(n=>n.textContent.trim()).join(' ');if(!t)continue;
   const r=el.getBoundingClientRect();if(r.width<2||r.height<2)continue;const cs=getComputedStyle(el);if(cs.visibility==='hidden'||cs.display==='none')continue;
   let op=1;for(let e=el;e;e=e.parentElement)op*=+getComputedStyle(e).opacity;if(op<.05)continue;
   const fg=P(cs.color);if(!fg||fg[3]<.05)continue;   /* gennemsigtig tekst har farveforløb i selve bogstaverne */const {b,img}=bgOf(el);let bgs=[b];
   if(img){const cols=[...img.matchAll(/rgba?\([^)]+\)/g)].map(m=>P(m[0])).filter(c=>c&&c[3]>=.5);if(!cols.length)continue;bgs=cols.map(c=>over(c,b))}
   const size=parseFloat(cs.fontSize),big=size>=24||(size>=18.66&&+cs.fontWeight>=700),need=big?3:4.5;
   const worst=Math.min(...bgs.map(B=>ratio(over([fg[0],fg[1],fg[2],fg[3]*op],B),B)));
   if(worst<need){const k=el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.trim().split(/\s+/).slice(0,2).join('.'):'')+(el.getAttribute('aria-pressed')==='true'?'[valgt]':'');
     const key=k+'|'+cs.color+'|'+Math.round(worst*10);if(seen.has(key))continue;seen.add(key);out.push({k,t:t.slice(0,30),r:Math.round(worst*100)/100,need,fg:cs.color,op:Math.round(op*100)/100,bg:bgs.map(B=>B.slice(0,3).map(Math.round).join(',')).slice(0,2).join(' / '),px:size})}}
 return out})()"""

only = sys.argv[1:3]
combos = [(b, a) for b in BG for a in ACC] if len(only) < 2 else [(only[0], only[1])]
bad = {}
with sync_playwright() as p:
    br = p.chromium.launch(); M = Mock()
    for vw in ((390, 844), (1280, 900)):
        c = br.new_context(viewport={'width': vw[0], 'height': vw[1]}, locale='da-DK', service_workers='block', reduced_motion='reduce'); c.route(f'https://{HOST}/**', M.handle); pg = c.new_page()
        pg.goto(URL); pg.wait_for_timeout(1200)
        for b, a in combos:
            pg.evaluate(SEED.replace('LOOK', json.dumps({'bg': b, 'acc': a}))); pg.reload(); pg.wait_for_timeout(900)
            for h in PAGES:
                pg.goto(URL + h); pg.wait_for_timeout(250)
                for f in pg.evaluate(MEASURE):
                    key = (f['k'], f['fg'], f['bg']); e = bad.setdefault(key, {**f, 'hvor': set(), 'komb': set()}); e['r'] = min(e['r'], f['r']); e['hvor'].add(h or '#'); e['komb'].add(b + '+' + a)
        c.close()
    br.close()
rows = sorted(bad.values(), key=lambda e: e['r'])
for e in rows:
    print(f"SVAG {e['r']}:1 (krav {e['need']}) {e['k']} «{e['t']}» {e['px']}px tekst {e['fg']} gennemsigtighed {e['op']} på {e['bg']} | sider: {' '.join(sorted(e['hvor'])[:5])} | {len(e['komb'])} af {len(combos)} kombinationer: {' '.join(sorted(e['komb'])[:4])}")
print(f'{len(rows)} slags tekst er for svag' if rows else f'ALT OK ({len(combos)} kombinationer, {len(PAGES)} sider, 2 skærmstørrelser)')
sys.exit(1 if rows else 0)
