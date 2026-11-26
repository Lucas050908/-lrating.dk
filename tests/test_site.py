"""Hele siden klikket igennem på pc og mobil: tilføj øl, bedøm, ret, søg, del, genstande, temaer, backup, slet med fortryd, offline.
Kør: python3 -m http.server 8811 &  og derefter  python3 tests/test_site.py"""
import json,re,tempfile,base64
import os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
URL=os.environ.get('SITE','http://localhost:8811/')
from mock_supabase import Mock,HOST
TMP=tempfile.mkdtemp()
from playwright.sync_api import sync_playwright
res=[]
# Et rigtigt foto (1600x1200) tegnes i browseren, så testen ikke kræver ekstra pakker
PHOTO=os.path.join(TMP,'oel.jpg')
def make_photo(b):
    pg=b.new_page();d=pg.evaluate("(()=>{const c=document.createElement('canvas');c.width=1600;c.height=1200;const x=c.getContext('2d');x.fillStyle='#284678';x.fillRect(0,0,1600,1200);x.fillStyle='#e6aa28';x.fillRect(600,200,400,900);for(let i=0;i<400;i++){x.fillStyle=`hsl(${i*7},60%,50%)`;x.fillRect((i*37)%1600,(i*53)%1200,30,30)}return c.toDataURL('image/jpeg',.92)})()");open(PHOTO,'wb').write(base64.b64decode(d.split(',')[1]));pg.close()
def check(n,c,x=''):
    res.append(bool(c)); print(('PASS ' if c else 'FAIL ')+n,'' if c else x)
def ls(pg): return json.loads(pg.evaluate("localStorage.getItem('olrating-v1')"))
VIEWS=['','#alle','#toplisten','#galleri','#sammenlign','#byttur','#smagning','#venner','#stilguide','#profil','#tilfoej','#kalender','#dagbog','#mad','#genstande','#privatliv','#om']
def run(b,name,vw):
    M=Mock(); errs=[]
    c=b.new_context(viewport={'width':vw[0],'height':vw[1]},accept_downloads=True,service_workers='block'); c.route(f'https://{HOST}/**',M.handle)
    pg=c.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m:errs.append('console: '+m.text[:200]) if m.type=='error' else None)
    pg.add_init_script("window.__sh=[];navigator.share=async d=>{window.__sh.push(d)};window.confirm=()=>true;")
    T=lambda n,cnd,x='':check(f'[{name}] {n}',cnd,x)
    over=lambda: pg.evaluate('document.documentElement.scrollWidth>innerWidth+1')
    pg.goto(URL); pg.wait_for_timeout(1500)
    T('empty site loads',pg.inner_text('h1')!='' and not errs,errs[:3])
    # --- add a beer through the form
    pg.goto(URL+'#tilfoej'); pg.wait_for_timeout(500)
    pg.click('#addBtn'); pg.wait_for_timeout(300)
    T('add: blocked without image',pg.evaluate('location.hash')=='#tilfoej')
    pg.set_input_files('#bImg',PHOTO); pg.wait_for_timeout(700)
    pg.fill('#bName','Skærgaard Pilsner'); pg.fill('#bBrew','Fanø Bryghus'); pg.fill('#bCity','Fanø')
    pg.select_option('#bStyle','Pilsner'); pg.fill('#bAbv','5,2'); pg.fill('#bIbu','30')
    pg.select_option('#bSize',index=1); pg.fill('#bPrice','25')
    T('add: abv hint updates',pg.inner_text('#abvHint')=='Normal styrke',pg.inner_text('#abvHint'))
    for k in ['look','aroma','taste','feel','overall']: pg.click(f'#addForm .rate[data-k="{k}"] [data-star="4"]')
    pg.fill('#addForm #rWho','Lucas'); pg.click('#addBtn'); pg.wait_for_timeout(4500)
    h=pg.evaluate('location.hash'); bid=h[6:] if h.startswith('#beer-') else ''
    T('add: lands on beer page',bool(bid) and 'Skærgaard Pilsner' in pg.title(),h)
    s=ls(pg); T('add: saved with shrunk image',len(s['beers'])==1 and len(s['reviews'])==1 and (s['beers'][0]['img'].startswith('idb:') or s['beers'][0]['img'].startswith('https://')),s['beers'][0].get('img','')[:30] if s['beers'] else s)
    T('beer page: score 4,0 and info',pg.inner_text('#bigScore').strip()=='4,0' and 'Fanø Bryghus' in pg.inner_text('.info') and '5,2' in pg.inner_text('.info'),pg.inner_text('#bigScore'))
    T('beer page: image visible',pg.evaluate("[...document.querySelectorAll('img')].some(i=>/^(blob:|https:\\/\\/bbc)/.test(i.src)&&i.naturalWidth>0)"))
    T('sync: beer + image reached database',len(M.t['beers'])==1 and len(M.store)==1,(list(M.t['beers']),list(M.store)))
    # --- second review
    for k in ['look','aroma','taste','feel','overall']: pg.click(f'#revForm .rate[data-k="{k}"] [data-star="2"]')
    pg.fill('#revForm #rWho','Magnus'); pg.click('#revForm button[type=submit]'); pg.wait_for_timeout(1500)
    pg.goto(URL+'#beer-'+bid); pg.wait_for_timeout(2600)
    T('review: average is 3,0 of 2',pg.inner_text('#bigScore').strip()=='3,0' and len(ls(pg)['reviews'])==2,pg.inner_text('#bigScore'))
    # --- units from beer page
    pg.click('[data-unit]'); pg.wait_for_timeout(300); T('genstand: added from beer page',len(ls(pg)['units'])==1 and abs(ls(pg)['units'][0]['g']-1.1)<0.31,ls(pg)['units'])
    # --- share + card
    pg.click('#shareBtn'); pg.wait_for_timeout(300); T('share: link shared',pg.evaluate('window.__sh.length')==1 and '#beer-' in pg.evaluate('window.__sh[0].url'))
    pg.evaluate("navigator.canShare=undefined")
    with pg.expect_download(timeout=10000) as dl: pg.click('#cardBtn')
    pth=dl.value.path(); T('share card: jpg > 30 kB',os.path.getsize(pth)>30000,os.path.getsize(pth))
    # --- edit beer (name is now Magnus, so switch back to Lucas who added it)
    pg.goto(URL+'#profil'); pg.wait_for_timeout(400); pg.fill('#meName','Lucas'); pg.click('#meForm button'); pg.wait_for_timeout(400)
    pg.goto(URL+'#beer-'+bid); pg.wait_for_timeout(600)
    T('edit: button shown to owner',pg.query_selector('#editBeer') is not None)
    pg.click('#editBeer'); pg.wait_for_timeout(600); pg.fill('#bCity','Nordby'); pg.click('#addBtn'); pg.wait_for_timeout(1200)
    T('edit: city saved, image kept',ls(pg)['beers'][0]['city']=='Nordby' and ls(pg)['beers'][0]['img']!='' and len(ls(pg)['beers'])==1,ls(pg)['beers'][0])
    # --- search
    pg.goto(URL+'#alle'); pg.wait_for_timeout(600)
    cnt=lambda:pg.eval_on_selector_all('#grid .card','e=>e.length')
    r={}
    for q in ['skaergaard','fano','Skærgard','pilsnre','xyzzy']:
        pg.fill('#q',q); pg.wait_for_timeout(250); r[q]=cnt()
    T('search: typos and ae/oe/aa',r=={'skaergaard':1,'fano':1,'Skærgard':1,'pilsnre':1,'xyzzy':0},r)
    pg.fill('#q',''); pg.wait_for_timeout(200)
    # --- every view renders without overflow or errors
    bad=[]
    for v in VIEWS+['#beer-'+bid,'#bryggeri-'+'Fan%C3%B8%20Bryghus']:
        pg.goto(URL+v); pg.wait_for_timeout(350)
        if over() or len(pg.inner_text('#app'))<40: bad.append(v)
    T('all views render, no sideways scroll',not bad,bad)
    pg.goto(URL+'#toplisten'); pg.wait_for_timeout(300); T('toplist shows beer','Skærgaard Pilsner' in pg.inner_text('#app'))
    pg.goto(URL+'#galleri'); pg.wait_for_timeout(500); T('gallery shows photo',pg.evaluate("[...document.querySelectorAll('#app img')].some(i=>i.naturalWidth>0)"))
    pg.goto(URL+'#stilguide'); pg.wait_for_timeout(300); pg.click('[data-brew]'); pg.wait_for_timeout(400); T('brewery page opens',pg.evaluate('location.hash').startswith('#bryggeri-') and 'Fanø Bryghus' in pg.inner_text('h2'))
    pg.goto(URL+'#dagbog'); pg.wait_for_timeout(300); T('diary lists my beer','Skærgaard' in pg.inner_text('#app'))
    # --- genstand-tæller
    pg.goto(URL+'#genstande'); pg.wait_for_timeout(300); pg.click('.gq button >> nth=0'); pg.wait_for_timeout(200)
    pg.fill('#uCl','50'); pg.fill('#uAbv','7,5'); pg.click('#unitForm button'); pg.wait_for_timeout(300)
    tot=round(sum(u['g'] for u in ls(pg)['units']),1); T('genstande: sum shown',pg.inner_text('.gbig .big >> nth=0').strip()==str(tot).replace('.',',').replace(',0',''),(pg.inner_text('.gbig .big >> nth=0'),tot))
    pg.click('[data-delunit] >> nth=0'); pg.wait_for_timeout(200); n=len(ls(pg)['units']); pg.click('#clearUnits'); pg.wait_for_timeout(200)
    T('genstande: remove one and reset',n==2 and len(ls(pg)['units'])==0,n)
    T('genstande: never sent to database',not any('unit' in l.lower() for l in M.log) and 'units' not in json.dumps(M.t))
    # --- themes
    pg.select_option('#seasonSel','jul'); pg.wait_for_timeout(300); pg.select_option('#modeSel','light'); pg.wait_for_timeout(300)
    T('theme switches',ls(pg)['season']=='jul' and ls(pg)['mode']=='light'); pg.select_option('#seasonSel','auto'); pg.select_option('#modeSel','auto')
    # --- backup, wipe, restore
    pg.goto(URL+'#profil'); pg.wait_for_timeout(400)
    T('profile: shows connected','Forbundet' in pg.inner_text('.sbst') and 'Ikke' not in pg.inner_text('.sbst'),pg.inner_text('.sbst')[:30])
    with pg.expect_download(timeout=10000) as dl: pg.click('#exportBtn')
    bk=os.path.join(TMP,'backup-'+name+'.json'); dl.value.save_as(bk); B=json.load(open(bk))
    T('backup: has beers, reviews, embedded photo',len(B['beers'])==1 and len(B['reviews'])==2 and B['beers'][0]['img'].startswith('data:image/'),B['beers'][0]['img'][:30])
    # --- delete review + undo, delete beer + undo
    pg.goto(URL+'#beer-'+bid); pg.wait_for_timeout(600)
    T('review actions only on my own review',pg.eval_on_selector_all('[data-delrev]','e=>e.length')==1)
    pg.click('[data-delrev]'); pg.wait_for_timeout(400); a=len(ls(pg)['reviews']); pg.click('.undo button'); pg.wait_for_timeout(500)
    T('delete review + undo',a==1 and len(ls(pg)['reviews'])==2,a)
    pg.click('#delBeer'); pg.wait_for_timeout(500); a=len(ls(pg)['beers']); pg.click('.undo button'); pg.wait_for_timeout(700)
    T('delete beer + undo',a==0 and len(ls(pg)['beers'])==1 and len(ls(pg)['reviews'])==2,a)
    pg.wait_for_timeout(11000)
    T('undo: nothing was deleted in database',len(M.t['beers'])==1 and len(M.t['reviews'])==2 and len(M.store)==1,(len(M.t['beers']),len(M.t['reviews']),len(M.store)))
    # --- wipe everything, check database, then restore from backup
    pg.goto(URL+'#profil'); pg.wait_for_timeout(400); pg.click('#wipeBtn'); pg.wait_for_timeout(200); pg.click('#wipeBtn'); pg.wait_for_timeout(14000)
    T('wipe: rows and photo removed from database',not M.t['beers'] and not M.t['reviews'] and not M.store,(list(M.t['beers']),list(M.t['reviews']),list(M.store)))
    pg.goto(URL+'#profil'); pg.wait_for_timeout(400); pg.set_input_files('#importFile',bk); pg.wait_for_timeout(4000)
    T('restore: backup brings beer, reviews and photo back',len(ls(pg)['beers'])==1 and len(ls(pg)['reviews'])==2 and len(M.t['beers'])==1 and len(M.store)==1,(len(ls(pg)['beers']),len(M.t['beers']),len(M.store)))
    # --- anbefalinger, enighed, alkoholfri, mærker og nedtælling (data lægges direkte ind)
    pg.evaluate("""(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1'));const d='2026-11-20',s=v=>({look:v,aroma:v,taste:v,feel:v,overall:v});
      const B=(id,name,style,x={})=>S.beers.push({id,name,brewery:'Testbryg '+id,style,city:'Aalborg',country:x.country||'Danmark',abv:x.abv??5,af:!!x.af,size:'33 cl flaske',date:d,addedBy:'Magnus',img:''});
      B('ux1','Fjord IPA','IPA');B('ux2','Kaj Pilsner','Pilsner');B('ux3','Nul Komma','Pilsner',{abv:0.4});B('ux4','Havn Stout','Stout',{country:'Belgien'});B('ux5','Fri Hvede','Hvede',{abv:0,af:true,country:'Tyskland'});
      const R=(id,beer,who,v,tags)=>S.reviews.push({id,beer,who,date:d,s:s(v),tags:tags||[],again:1,text:''});
      R('rx1','ux1','Lucas',5,['Citrus']);R('rx2','ux4','Lucas',2,['Ristet']);R('rx3','ux1','Magnus',5);R('rx4','ux4','Magnus',2);R('rx5','ux2','Magnus',4,['Citrus']);R('rx6','ux3','Magnus',3);R('rx7','ux5','Magnus',4);R('rx8','ux3','Lucas',4);
      S.me='Lucas';localStorage.setItem('olrating-v1',JSON.stringify(S))})()""")
    pg.goto(URL+'#profil'); pg.reload(); pg.wait_for_timeout(1500)
    T('for dig: bedste forslag er Kaj Pilsner med begrundelse',pg.inner_text('.fy .mini >> nth=0 >> b >> nth=0')=='Kaj Pilsner' and 'pilsner' in pg.inner_text('.fy .mini >> nth=0').lower() and 'Havn Stout' not in pg.inner_text('.fy'),pg.inner_text('.fy')[:200])
    T('enighed: Magnus 81 % på 4 fælles øl','Magnus' in pg.inner_text('.agr') and '81 %' in pg.inner_text('.agr') and '4 fælles' in pg.inner_text('.agr'),pg.inner_text('.agr'))
    T('mærke: Klart hoved er optjent, Globetrotter ikke',pg.evaluate("[...document.querySelectorAll('.badge.got b')].map(x=>x.textContent)").count('Klart hoved')==1 and 'Globetrotter' not in pg.evaluate("[...document.querySelectorAll('.badge.got b')].map(x=>x.textContent)"))
    T('profil: ingen vandret scroll med nye bokse',not over())
    pg.goto(URL); pg.wait_for_timeout(700)
    T('forside: nedtælling og Noget for dig',pg.query_selector('.nextev') is not None and ('dage' in pg.inner_text('.nextev') or 'I dag' in pg.inner_text('.nextev') or 'I morgen' in pg.inner_text('.nextev')) and pg.query_selector('.fy.home') is not None and not over(),pg.inner_text('.nextev') if pg.query_selector('.nextev') else None)
    pg.goto(URL+'#alle'); pg.wait_for_timeout(500); pg.evaluate("document.getElementById('fAf').closest('details').open=true"); pg.check('#fAf'); pg.wait_for_timeout(300)
    names=pg.evaluate("[...document.querySelectorAll('#grid .card h3')].map(x=>x.textContent).sort()")
    T('alkoholfri: filter viser kun de to alkoholfri',names==['Fri Hvede','Nul Komma'] and 'Alkoholfri' in pg.inner_text('#grid .card >> nth=0'),names)
    pg.goto(URL+'#toplisten'); pg.wait_for_timeout(400); pg.click('.chip:has-text("Alkoholfri")'); pg.wait_for_timeout(300)
    T('alkoholfri: egen topliste',pg.eval_on_selector_all('.toplist li','e=>e.length')==2)
    pg.goto(URL+'#beer-ux5'); pg.wait_for_timeout(500); a=pg.query_selector('[data-unit]') is None
    pg.goto(URL+'#beer-ux1'); pg.wait_for_timeout(500)
    T('alkoholfri: ingen +Genstand på 0 %, men på almindelig øl',a and pg.query_selector('[data-unit]') is not None)
    pg.goto(URL+'#tilfoej'); pg.wait_for_timeout(400); pg.fill('#bAbv','0,3'); T('tilføj: alkoholfri-felt og hint',pg.query_selector('#bAf') is not None and pg.inner_text('#abvHint')=='Alkoholfri',pg.inner_text('#abvHint'))
    # --- menuen "Mere"
    pg.goto(URL); pg.wait_for_timeout(500)
    if vw[0]>1100:
        pg.click('#navMore'); pg.wait_for_timeout(200); vis=pg.is_visible('#navdd a[data-nav="smagning"]'); pg.click('#navdd a[data-nav="venner"]'); pg.wait_for_timeout(400)
        T('menu: Mere åbner og fører til Venner',vis and pg.evaluate('location.hash')=='#venner' and not pg.is_visible('#navdd') and pg.evaluate("document.querySelector('.navmore').classList.contains('cur')"))
    else:
        pg.click('#menuBtn'); pg.wait_for_timeout(250); vis=pg.is_visible('#navdd a[data-nav="smagning"]') and pg.is_visible('#nav a[data-nav="profil"]'); pg.click('#navdd a[data-nav="genstande"]'); pg.wait_for_timeout(400)
        T('menu: mobilmenuen viser alle sider og lukker efter valg',vis and pg.evaluate('location.hash')=='#genstande' and not pg.is_visible('#nav') and not over())
    # --- venner: smagerside, følg, feed
    pg.goto(URL+'#smager-Magnus'); pg.wait_for_timeout(500)
    T('smager: side med navn, antal og enighed',pg.inner_text('h1')=='Magnus' and '6 øl bedømt' in pg.inner_text('.thead') and '81 % enige' in pg.inner_text('.thead'),pg.inner_text('.thead'))
    pg.click('[data-follow]'); pg.wait_for_timeout(400)
    T('følg: gemt og knappen skifter',ls(pg)['follow']==['Magnus'] and 'Følger' in pg.inner_text('[data-follow]'))
    pg.goto(URL+'#venner'); pg.wait_for_timeout(500)
    T('venner: feed viser Magnus, og han foreslås ikke længere',pg.eval_on_selector_all('.cols .box >> nth=0 >> .rv','e=>e.length')==6 and pg.query_selector('.frow') is None and not over(),pg.inner_text('.cols')[:160])
    T('venner: sendes ikke til databasen','follow' not in json.dumps(M.t))
    pg.goto(URL+'#beer-ux1'); pg.wait_for_timeout(500); pg.click('.rv .who >> nth=0'); pg.wait_for_timeout(400)
    T('navn i en bedømmelse fører til smagerens side',pg.evaluate('location.hash').startswith('#smager-'))
    T('no JS or console errors',not errs,errs[:4])
    c.close()
with sync_playwright() as p:
    b=p.chromium.launch(); make_photo(b)
    run(b,'pc',(1280,900)); run(b,'mobil',(390,844))
    # offline via service worker
    c=b.new_context(); pg=c.new_page(); pg.goto(URL); pg.wait_for_timeout(3500)
    sw=pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!(r&&r.active))")
    c.set_offline(True); 
    try: pg.reload(); pg.wait_for_timeout(1200); ok=len(pg.inner_text('#app'))>100
    except Exception as e: ok=False
    check('[offline] service worker active and page loads without net',sw and ok,(sw,ok)); c.close(); b.close()
# static checks
root=ROOT+'/'; s=open(root+'index.html').read(); sw=open(root+'sw.js').read()
miss=[f for f in re.findall(r"'\./?([\w./-]+\.\w+)'",sw.split('SHELL=')[1].split(']')[0]) if not os.path.exists(root+f)]
check('[filer] everything the service worker caches exists',not miss,miss)
loc=set(re.findall(r'(?:src|href)="((?:img|fonts|js)/[^"#?]+)"',s))|set(re.findall(r"url\(((?:img|fonts)/[^)]+)\)",s))|set(re.findall(r"'((?:img|js)/[\w./-]+)'",s))
miss=[f for f in loc if not os.path.exists(root+f)]; check('[filer] all referenced images, fonts and scripts exist',not miss,miss)
m=json.load(open(root+'manifest.webmanifest')); miss=[i['src'] for i in m['icons'] if not os.path.exists(root+i['src'])]; check('[filer] manifest valid, icons exist',not miss,miss)
check('[links] downloads point at fixed tags, none at latest','releases/latest' not in s and s.count('releases/download/android-app/olrating.apk')>=2 and 'desktop-app/olrating-windows.exe' in s)
check('[sikkerhed] no secret keys in repo',os.system(f"cd {root} && git grep -nIE 'sb_secret_|service_role|BEGIN (RSA |EC )?PRIVATE KEY|storePassword *= *\"[^\"]' -- . ':!docs' ':!CLAUDE.md' ':!supabase' ':!tests' >/dev/null")!=0)
print('ALL PASS' if all(res) else f'{res.count(False)} FAILED of {len(res)}')
sys.exit(0 if all(res) else 1)
