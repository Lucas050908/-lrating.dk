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
VIEWS=['','#alle','#toplisten','#aarets','#swipe','#buddies','#hjul','#indstillinger','#galleri','#sammenlign','#byttur','#smagning','#venner','#nyt','#stilguide','#profil','#tilfoej','#kalender','#dagbog','#mad','#genstande','#privatliv','#om','#afmeld-00000000-0000-4000-a000-000000000001']
def run(b,name,vw):
    M=Mock(); errs=[]
    c=b.new_context(viewport={'width':vw[0],'height':vw[1]},accept_downloads=True,service_workers='block',locale='da-DK'); c.route(f'https://{HOST}/**',M.handle)
    pg=c.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m:errs.append('console: '+m.text[:200]) if m.type=='error' else None)
    pg.add_init_script("window.__sh=[];navigator.share=async d=>{window.__sh.push(d)};window.confirm=()=>true;window.__w=[];window.__wi=[];window.OlratingApp={updateWidget:j=>window.__w.push(j),updateImages:j=>window.__wi.push(j)};")
    T=lambda n,cnd,x='':check(f'[{name}] {n}',cnd,x)
    over=lambda: pg.evaluate('document.documentElement.scrollWidth>innerWidth+1')
    pg.goto(URL); pg.wait_for_timeout(1500)
    T('empty site loads',pg.inner_text('h1')!='' and not errs,errs[:3])
    T('sprog: dansk er standard, og sprogvælgeren og valget i sidefoden findes',pg.evaluate('document.documentElement.lang')=='da' and pg.inner_text('#langCode')=='DA' and pg.is_visible('#langBtn') and pg.evaluate("document.getElementById('langSel').value")=='da' and pg.inner_text('#nav a >> nth=0')=='Alle øl' and not over())
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
    # kommatal: minus og plus retter med 0,1. 3,9 og 4,1 giver stadig 4,0 i snit
    pg.click('#addForm .rate[data-k="look"] [data-step="-1"]'); pg.click('#addForm .rate[data-k="aroma"] [data-step="1"]')
    pg.fill('#addForm #rWho','Lucas'); pg.click('#addBtn'); pg.wait_for_timeout(4500)
    h=pg.evaluate('location.hash'); bid=h[6:] if h.startswith('#beer-') else ''
    T('add: lands on beer page',bool(bid) and 'Skærgaard Pilsner' in pg.title(),h)
    s=ls(pg); T('add: saved with shrunk image',len(s['beers'])==1 and len(s['reviews'])==1 and (s['beers'][0]['img'].startswith('idb:') or s['beers'][0]['img'].startswith('https://')),s['beers'][0].get('img','')[:30] if s['beers'] else s)
    T('beer page: score 4,0 and info',pg.inner_text('#bigScore').strip()=='4,0' and 'Fanø Bryghus' in pg.inner_text('.info') and '5,2' in pg.inner_text('.info'),pg.inner_text('#bigScore'))
    T('beer page: image visible',pg.evaluate("[...document.querySelectorAll('img')].some(i=>/^(blob:|https:\\/\\/bbc)/.test(i.src)&&i.naturalWidth>0)"))
    T('sync: beer + image reached database',len(M.t['beers'])==1 and len(M.store)==1,(list(M.t['beers']),list(M.store)))
    sc=s['reviews'][0]['s'] if s['reviews'] else {}; db=[r['data'].get('s',{}) for r in M.t['reviews'].values()]
    T('kommatal: 3,9 og 4,1 er gemt på enheden og i databasen',sc.get('look')==3.9 and sc.get('aroma')==4.1 and sc.get('taste')==4 and db and db[0].get('look')==3.9 and db[0].get('aroma')==4.1,(sc,db))
    R='#revForm .rate[data-k="look"]'; rd=lambda: pg.evaluate("(q)=>{const r=document.querySelector(q),p=r.querySelector('.part');return [r.dataset.v,r.querySelector('.rnv').textContent,[...r.querySelectorAll('[data-star]')].map(b=>b.className).join('|'),p?p.style.getPropertyValue('--f'):'',r.querySelectorAll('[aria-checked=true]').length]}",R)
    pg.click(R+' [data-step="1"]'); v0=rd()
    pg.click(R+' [data-star="4"]'); v4=rd()
    for _ in range(3): pg.click(R+' [data-step="-1"]')
    v1=rd(); T('kommatal: 4 stjerner og tre gange minus giver 3,7 med en delvist fyldt stjerne',v4[:2]==['4','4,0'] and v4[4]==1 and v1==['3.7','3,7','on|on|on|part|','70%',0],(v4,v1))
    T('kommatal: plus uden en karakter starter på 3,0',v0[:2]==['3','3,0'],v0)
    pg.click(R+' [data-star="5"]'); pg.click(R+' [data-step="1"]'); hi=rd(); pg.click(R+' [data-star="1"]'); pg.click(R+' [data-step="-1"]'); lo=rd()
    T('kommatal: kan ikke komme over 5 eller under 1',hi[:2]==['5','5,0'] and lo[:2]==['1','1,0'],(hi,lo))
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
    # --- findes den allerede? (dubletter)
    pg.goto(URL+'#tilfoej'); pg.wait_for_timeout(400)
    pg.fill('#bName','Skærgard Pilsner'); pg.wait_for_timeout(500)
    vis=pg.is_visible('#dupHint') and 'Skærgaard Pilsner' in pg.inner_text('#dupHint') and pg.get_attribute('#dupHint a','href')=='#beer-'+bid
    pg.fill('#bBrew','Et helt andet bryggeri'); pg.wait_for_timeout(500); other=not pg.is_visible('#dupHint')
    pg.fill('#bBrew',''); pg.fill('#bName','Noget helt nyt'); pg.wait_for_timeout(500)
    T('dublet: forslag ved næsten samme navn, væk ved andet bryggeri eller nyt navn',vis and other and not pg.is_visible('#dupHint') and not over(),(vis,other))
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
    pg.select_option('#seasonSel','jul'); pg.wait_for_timeout(300)
    T('tema: sæson kan skiftes, og der er intet valg af lyst tema',ls(pg)['season']=='jul' and pg.query_selector('#modeSel') is None); pg.select_option('#seasonSel','auto')
    # --- backup, wipe, restore
    pg.goto(URL+'#profil'); pg.wait_for_timeout(400)
    T('profile: shows connected','Forbundet' in pg.inner_text('.sbst') and 'Ikke' not in pg.inner_text('.sbst'),pg.inner_text('.sbst')[:30])
    with pg.expect_download(timeout=10000) as dl: pg.click('#exportBtn')
    bk=os.path.join(TMP,'backup-'+name+'.json'); dl.value.save_as(bk); B=json.load(open(bk))
    T('backup: has beers, reviews, embedded photo',len(B['beers'])==1 and len(B['reviews'])==2 and B['beers'][0]['img'].startswith('data:image/'),B['beers'][0]['img'][:30])
    # --- ret en gammel bedømmelse fra profilen
    pg.click('[data-goedit] >> nth=0'); pg.wait_for_timeout(900)
    rid=pg.get_attribute('#revForm','data-edit') or ''; old=[r for r in ls(pg)['reviews'] if r['id']==rid]
    T('profil: Ret åbner øllens side med bedømmelsen klar',pg.evaluate('location.hash').startswith('#beer-') and pg.inner_text('#rateTitle')=='Ret din anmeldelse' and old and pg.input_value('#rText')==(old[0].get('text') or ''),(pg.evaluate('location.hash'),pg.inner_text('#rateTitle'),rid))
    pg.fill('#rText','Rettet fra profilen'); pg.click('#editX'); pg.wait_for_timeout(400)
    T('profil: Fortryd ændringer gemmer ingenting',[r.get('text') for r in ls(pg)['reviews'] if r['id']==rid]==[old[0].get('text')] and pg.inner_text('#rateTitle')!='Ret din anmeldelse')
    pg.goto(URL+'#profil'); pg.wait_for_timeout(400); pg.click('[data-goedit] >> nth=0'); pg.wait_for_timeout(900)
    pg.fill('#rText','Rettet fra profilen'); pg.click('#revForm button[type=submit]'); pg.wait_for_timeout(1200)
    nw=[r for r in ls(pg)['reviews'] if r['id']==rid]
    T('profil: rettet bedømmelse er gemt med samme id og dato',nw and nw[0]['text']=='Rettet fra profilen' and nw[0].get('edited')==1 and nw[0]['date']==old[0]['date'] and len(ls(pg)['reviews'])==2,nw)
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
      S.me='Lucas';S.mode='light';localStorage.setItem('olrating-v1',JSON.stringify(S))})()""")
    pg.goto(URL+'#profil'); pg.reload(); pg.wait_for_timeout(1500)
    T('tema: altid mørkt, også når et lyst tema er gemt fra før',pg.evaluate("document.documentElement.dataset.mode===undefined&&document.querySelector('meta[name=theme-color]').content==='#0f1d36'") and pg.evaluate("getComputedStyle(document.body).backgroundColor")=='rgb(15, 29, 54)',pg.evaluate("getComputedStyle(document.body).backgroundColor"))
    T('for dig: bedste forslag er Kaj Pilsner med begrundelse',pg.inner_text('.fy .mini >> nth=0 >> b >> nth=0')=='Kaj Pilsner' and 'pilsner' in pg.inner_text('.fy .mini >> nth=0').lower() and 'Havn Stout' not in pg.inner_text('.fy'),pg.inner_text('.fy')[:200])
    T('enighed: Magnus 81 % på 4 fælles øl','Magnus' in pg.inner_text('.agr') and '81 %' in pg.inner_text('.agr') and '4 fælles' in pg.inner_text('.agr'),pg.inner_text('.agr'))
    T('mærke: Klart hoved er optjent, Globetrotter ikke',pg.evaluate("[...document.querySelectorAll('.badge.got b')].map(x=>x.textContent)").count('Klart hoved')==1 and 'Globetrotter' not in pg.evaluate("[...document.querySelectorAll('.badge.got b')].map(x=>x.textContent)"))
    T('profil: ingen vandret scroll med nye bokse',not over())
    w=json.loads(pg.evaluate("window.__w.at(-1)"))
    T('widget-data: forslag, nedtælling, seneste, mig og genstande',w['rec']['name']=='Kaj Pilsner' and w['rec']['id']=='ux2' and re.match(r'^\d{4}-\d\d-\d\d$',w['next']['date']) and len(w['latest'])==4 and w['me']['name']=='Lucas' and 'todayN' in w['units'] and len(w['top'])==3,w)
    wi=json.loads(pg.evaluate("window.__wi.at(-1)||'{}'")); used={x.get('id') for x in [w['week'] or {},w['rec'] or {}]+w['top']+w['latest']}; withimg={b['id'] for b in ls(pg)['beers'] if b.get('img')}
    T('widget-data: øl har id, og siden sender tal for hele siden',all(x.get('id') for x in w['top']+w['latest']) and (w['week'] is None or w['week'].get('id')) and w['site']['visits']==M.visits and w['site']['today']==M.visits_today and w['site']['tasters']>=2 and w['beers']==len(ls(pg)['beers']),w.get('site'))
    T('widget-billeder: små JPEG-billeder af de øl, widgets viser, og kun dem',set(wi)==(used&withimg) and all(v.startswith('data:image/jpeg;base64,') and 500<len(v)<88000 for v in wi.values()) and (len(wi)>0 or not (used&withimg)),(sorted(wi),sorted(used&withimg)))
    pg.goto(URL+'#om'); pg.wait_for_timeout(1400); ot=pg.inner_text('#omTal')   # tallene tæller op i 0,7 sekund
    T('om: siden i tal viser besøg, øl, bedømmelser og smagere',pg.eval_on_selector_all('#omTal .ex-t','e=>e.length')==5 and f'{M.visits:,}'.replace(',','.') in ot and 'besøg i alt' in ot and 'besøg i dag' in ot and 'smagere' in ot and 'talt siden 26. november 2026' in pg.inner_text('#app') and not over(),ot)
    pg.goto(URL); pg.wait_for_timeout(700)
    T('forside: nedtælling og Noget for dig',pg.query_selector('.nextev') is not None and ('dage' in pg.inner_text('.nextev') or 'I dag' in pg.inner_text('.nextev') or 'I morgen' in pg.inner_text('.nextev')) and pg.query_selector('.fy.home') is not None and not over(),pg.inner_text('.nextev') if pg.query_selector('.nextev') else None)
    pg.goto(URL+'#alle'); pg.wait_for_timeout(500); pg.evaluate("document.getElementById('fAf').closest('details').open=true"); pg.check('#fAf'); pg.wait_for_timeout(300)
    names=pg.evaluate("[...document.querySelectorAll('#grid .card h3')].map(x=>x.textContent).sort()")
    T('alkoholfri: filter viser kun de to alkoholfri',names==['Fri Hvede','Nul Komma'] and 'Alkoholfri' in pg.inner_text('#grid .card >> nth=0'),names)
    pg.goto(URL+'#toplisten'); pg.wait_for_timeout(400); pg.click('.chip:has-text("Alkoholfri")'); pg.wait_for_timeout(300)
    T('alkoholfri: egen topliste',pg.eval_on_selector_all('.toplist li','e=>e.length')==2)
    # --- del toplisten som billede, og Årets øl
    pg.evaluate("navigator.canShare=undefined")
    with pg.expect_download(timeout=10000) as dl: pg.click('#topCard')
    T('topliste: del som billede (jpg > 40 kB)',dl.value.suggested_filename=='toplisten-olrating.jpg' and os.path.getsize(dl.value.path())>40000,os.path.getsize(dl.value.path()))
    pg.goto(URL+'#aarets'); pg.wait_for_timeout(400)
    if pg.query_selector('[data-year="2026"][aria-pressed="false"]'): pg.click('[data-year="2026"]'); pg.wait_for_timeout(300)
    aw=pg.inner_text('.awards')
    T('årets øl: vinder, næste på listen og priser',pg.inner_text('.winner h2')=='Fjord IPA' and pg.inner_text('.winner b.s')=='5,0' and pg.evaluate("[...document.querySelectorAll('.toplist li a')].map(x=>x.textContent)")==['Nul Komma','Skærgaard Pilsner','Havn Stout'] and 'Testbryg ux1' in aw and 'Pilsner' in aw and 'Fri Hvede' in aw and 'nykommer' not in aw.lower(),(pg.inner_text('.winner'),aw))
    T('årets øl: tal for året og ingen vandret scroll','10 bedømmelser af 6 forskellige øl fra 6 bryggerier, givet af 2 smagere' in pg.inner_text('#yearNums') and not over(),pg.inner_text('#yearNums'))
    pg.evaluate("navigator.canShare=undefined")
    with pg.expect_download(timeout=10000) as dl: pg.click('#yearCard')
    T('årets øl: del som billede (jpg > 40 kB)',dl.value.suggested_filename=='aarets-oel-2026-olrating.jpg' and os.path.getsize(dl.value.path())>40000,dl.value.suggested_filename)
    # --- byttur som minde: en gammel tur og en kommende
    pg.evaluate("""(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1'));const st=[{name:'Søgaards Bryghus',time:'19:00',addr:''},{name:'John Bull Pub',time:'21:00',addr:'Østerågade 20'},{name:'Den Tatoverede Enke',time:'00:30',addr:''}];
      S.tours.push({id:'mem1test',name:'J-dag i Aalborg',date:'2026-11-20T19:00',meet:'Nytorv',note:'',host:'Lucas',stops:st,members:[{name:'Lucas'},{name:'Magnus'}]},{id:'fut1test',name:'Nytårstur',date:'2099-12-31T20:00',meet:'',note:'',host:'Lucas',stops:st.slice(0,1),members:[{name:'Lucas'}]});localStorage.setItem('olrating-v1',JSON.stringify(S))})()""")
    pg.goto(URL+'#byttur'); pg.reload(); pg.wait_for_timeout(1500)
    T('minde: gammel tur står under Minder, kommende tur gør ikke',pg.eval_on_selector_all('#tourOld .tcard','e=>e.length')==1 and 'J-dag i Aalborg' in pg.inner_text('#tourOld') and '5 øl bedømt' in pg.inner_text('#tourOld') and 'Nytårstur' not in pg.inner_text('#tourOld') and 'Nytårstur' in pg.inner_text('#app'),pg.inner_text('#app')[:300])
    pg.goto(URL+'#byttur-mem1test'); pg.wait_for_timeout(500); mm=pg.inner_text('#tourMemo')
    T('minde: rute, hold og turens bedste øl',"3 stop · 2 var med · 5 øl bedømt" in mm and pg.inner_text('#tourMemo .rk >> nth=0 >> b >> nth=0')=='Fjord IPA' and 'Turens bedste øl' in mm and 'bedømt af Lucas og Magnus' in mm and pg.query_selector('.safe') is None and 'Hvem var med (2)' in pg.inner_text('#app') and not over(),mm[:300])
    pg.evaluate("navigator.canShare=undefined")
    with pg.expect_download(timeout=10000) as dl: pg.click('#tourCard')
    T('minde: del som billede (jpg > 40 kB)',dl.value.suggested_filename=='J-dag-i-Aalborg-byttur-olrating.jpg' and os.path.getsize(dl.value.path())>40000,dl.value.suggested_filename)
    pg.goto(URL+'#byttur-fut1test'); pg.wait_for_timeout(500)
    T('minde: kommende tur har intet minde, men Kom sikkert hjem',pg.query_selector('#tourMemo') is None and pg.query_selector('.safe') is not None and 'Hvem er med (1)' in pg.inner_text('#app'))
    pg.goto(URL+'#beer-ux5'); pg.wait_for_timeout(500); a=pg.query_selector('[data-unit]') is None
    pg.goto(URL+'#beer-ux1'); pg.wait_for_timeout(500)
    T('alkoholfri: ingen +Genstand på 0 %, men på almindelig øl',a and pg.query_selector('[data-unit]') is not None)
    pg.goto(URL+'#tilfoej'); pg.wait_for_timeout(400); pg.fill('#bAbv','0,3'); T('tilføj: alkoholfri-felt og hint',pg.query_selector('#bAf') is not None and pg.inner_text('#abvHint')=='Alkoholfri',pg.inner_text('#abvHint'))
    # --- kort over bryggerier
    pg.goto(URL+'#stilguide'); pg.wait_for_timeout(500)
    T('kort: to byer på kortet, Aalborg med 5 bryggerier',pg.eval_on_selector_all('.bmap svg circle','e=>e.length')==2 and pg.text_content('.bmap svg text')=='5' and 'Aalborg' in pg.inner_text('.bml') and not over(),pg.inner_text('.bmap')[:200] if pg.query_selector('.bmap') else None)
    T('kort: besøgte bryggerier er markeret',pg.eval_on_selector_all('.bml a.v','e=>e.length')==4,pg.eval_on_selector_all('.bml a.v','e=>e.map(x=>x.textContent)'))
    pg.click('.bmap svg a[data-mapq]'); pg.wait_for_timeout(600)
    T('kort: tryk på en by viser byens øl',pg.evaluate('location.hash')=='#alle' and pg.eval_on_selector_all('#grid .card','e=>e.length')==5,pg.evaluate('location.hash'))
    pg.fill('#q',''); pg.goto(URL+'#stilguide'); pg.wait_for_timeout(400); pg.click('.bmap svg a:not([data-mapq])'); pg.wait_for_timeout(500)
    T('kort: tryk på et enkelt bryggeri åbner dets side',pg.evaluate('location.hash').startswith('#bryggeri-'))
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
    # --- beer buddies: match i procent ud fra de øl, begge har bedømt
    pg.goto(URL+'#buddies'); pg.wait_for_timeout(500); bt=pg.inner_text('.buds') if pg.query_selector('.buds') else ''
    T('beer buddies: Magnus er bedste match med samme procent som på hans side',pg.eval_on_selector_all('.bud','e=>e.length')==1 and '81 %' in bt and 'Bedste match' in bt and 'Magnus' in bt and '4 øl til fælles' in bt and 'Mest enige om' in bt and 'Du: ' in bt and pg.query_selector('.bud .budl a[href^="#beer-"]') is not None and not over(),bt[:220])
    was=pg.inner_text('.bud [data-follow]'); pg.click('.bud [data-follow]'); pg.wait_for_timeout(400); mid=pg.inner_text('.bud [data-follow]'); pg.click('.bud [data-follow]'); pg.wait_for_timeout(400)
    T('beer buddies: man kan følge og holde op igen fra kortet',was=='Følger ✓' and mid=='Følg' and pg.inner_text('.bud [data-follow]')=='Følger ✓' and 'Magnus' in ls(pg)['follow'],(was,mid))
    pg.goto(URL+'#tilfoej'); pg.wait_for_timeout(400); pg.click('label[for=bAf]'); af1=pg.is_checked('#bAf'); foc=pg.evaluate('document.activeElement.id'); pg.click('label[for=bAf]')
    T('tilføj: et tryk på teksten Alkoholfri krydser af og flytter ikke markøren til procentfeltet',af1 and not pg.is_checked('#bAf') and foc!='bAbv' and not over(),(af1,foc))
    pg.goto(URL+'#indstillinger'); pg.wait_for_timeout(400); pg.focus('[data-look="pat:boelger"]'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300); fk=pg.evaluate("document.activeElement.dataset.look||document.activeElement.tagName"); pg.keyboard.press('Shift+Tab'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    T('tastatur: fokus bliver på knappen, når siden tegnes igen efter et valg',fk=='pat:boelger' and pg.evaluate("document.documentElement.dataset.pat")=='bobler',(fk,pg.evaluate("document.documentElement.dataset.pat")))
    pg.click('[data-look="pat:none"]'); pg.wait_for_timeout(200)
    # --- loading screen: vises med det samme, er væk igen når siden er klar, og spærrer ikke for tryk
    pg.goto(URL+'#om'); pg.reload(wait_until='commit'); pg.wait_for_selector('#load .ldb',state='attached',timeout=4000); pe=pg.evaluate("getComputedStyle(document.getElementById('load')).pointerEvents")
    pg.wait_for_selector('#load',state='detached',timeout=6000)
    T('loading screen: vises ved start, spærrer ikke for tryk og fjerner sig selv',pe=='none' and pg.query_selector('#load') is None and pg.inner_text('h1')=='Om ølrating.dk' and not over(),pe)
    # --- design og farver: baggrund, farver og mønster skifter med det samme, gemmes på enheden og kan slås fra igen
    pg.goto(URL+'#indstillinger'); pg.wait_for_timeout(500)
    for v in ['bg:skov','acc:hav','pat:bobler']: pg.click(f'[data-look="{v}"]'); pg.wait_for_timeout(300)
    lk=pg.evaluate("[document.documentElement.dataset.bg,document.documentElement.dataset.acc,document.documentElement.dataset.pat,getComputedStyle(document.body).backgroundColor,getComputedStyle(document.documentElement).getPropertyValue('--sun').trim(),getComputedStyle(document.body).backgroundImage!=='none',document.querySelector('meta[name=theme-color]').content]")
    T('design: baggrund, farver og mønster skifter med det samme og gemmes',lk==['skov','hav','bobler','rgb(15, 36, 27)','#4cc2ff',True,'#0f241b'] and ls(pg)['look']=={'bg':'skov','acc':'hav','pat':'bobler'} and pg.get_attribute('[data-look="bg:skov"]','aria-pressed')=='true' and pg.get_attribute('[data-look="bg:nat"]','aria-pressed')=='false' and not over(),lk)
    pg.reload(); pg.wait_for_timeout(900)
    T('design: valget huskes, når siden åbnes igen',pg.evaluate("document.documentElement.dataset.bg+document.documentElement.dataset.acc+document.documentElement.dataset.pat")=='skovhavbobler' and pg.evaluate("getComputedStyle(document.body).backgroundColor")=='rgb(15, 36, 27)' and pg.evaluate("getComputedStyle(document.querySelector('.bar')).backgroundColor").startswith('rgba(15, 36, 27'),pg.evaluate("getComputedStyle(document.querySelector('.bar')).backgroundColor"))
    for v in ['bg:nat','acc:std','pat:none']: pg.click(f'[data-look="{v}"]'); pg.wait_for_timeout(250)
    T('design: tilbage til det normale',pg.evaluate("[document.documentElement.dataset.bg,document.documentElement.dataset.acc,document.documentElement.dataset.pat].every(x=>x===undefined)") and pg.evaluate("getComputedStyle(document.body).backgroundColor")=='rgb(15, 29, 54)' and pg.evaluate("document.querySelector('meta[name=theme-color]').content")=='#0f1d36')
    pg.click('[data-seas=jul]'); pg.wait_for_timeout(300); sj=pg.evaluate("[document.documentElement.dataset.season,document.getElementById('seasonSel').value,document.querySelector('[data-seas=jul]').getAttribute('aria-pressed')]"); pg.click('[data-seas=auto]'); pg.wait_for_timeout(300)
    T('indstillinger: tema efter højtid kan vælges og følger med i bunden af siden',sj==['jul','jul','true'] and ls(pg)['season']=='auto',sj)
    pg.click('[data-setlang=en]'); pg.wait_for_timeout(900); h_en=pg.inner_text('h1'); pg.click('[data-setlang=da]'); pg.wait_for_timeout(900)
    T('indstillinger: sprog kan skiftes begge veje',h_en=='Make the site your own' and pg.inner_text('h1')=='Gør siden til din egen' and pg.get_attribute('[data-setlang=da]','aria-pressed')=='true',h_en)
    pg.goto(URL+'#profil'); pg.wait_for_timeout(400)
    T('profil: link til indstillinger, og design ligger ikke på profilen',pg.query_selector('#setLink a[href="#indstillinger"]') is not None and pg.query_selector('#lookBox') is None)
    # --- lykkehjulet: hjulet vælger én øl, og resultatet er den øl, pilen peger på
    pg.goto(URL+'#hjul'); pg.wait_for_timeout(500); nseg=pg.eval_on_selector_all('#hjG text','e=>e.length'); ht=pg.inner_text('#app')
    T('lykkehjul: hjul med øl, fem grupper og en ansvarlig tekst',2<=nseg<=10 and pg.eval_on_selector_all('[data-hj]','e=>e.length')==5 and pg.eval_on_selector_all('[data-hj][aria-pressed=true]','e=>e.length')==1 and 'Alkolinjen' in ht and 'Sundhedsstyrelsen' in ht and pg.query_selector('.box a[href="#genstande"]') is not None and not over(),(nseg,ht[:120]))
    pg.click('#hjSpin'); pg.wait_for_selector('#hjRes .hjr',timeout=9000)
    hr=pg.evaluate("""(()=>{const g=document.getElementById('hjG'),rot=parseFloat(g.style.transform.match(/rotate\\(([-\\d.]+)deg/)[1]),L=[...g.querySelectorAll('text')].map(t=>t.textContent),n=L.length,i=Math.floor(((360-rot%360)%360)/(360/n))%n,nm=document.querySelector('#hjRes h2').textContent;return [nm,L[i],document.getElementById('hjSpin').textContent,document.querySelector('#hjRes a').getAttribute('href')]})()""")
    T('lykkehjul: resultatet er den øl, pilen peger på',(hr[0] if len(hr[0])<=15 else hr[0][:14]+'…')==hr[1] and hr[2]=='Drej igen' and hr[3].startswith('#beer-') and not over(),hr)
    wl=ls(pg).get('wish',[]); pg.click('[data-hj=wish]'); pg.wait_for_timeout(400); nw=pg.eval_on_selector_all('#hjG text','e=>e.length')
    T('lykkehjul: ønskelisten som gruppe viser kun de øl, eller en forklaring når den er tom',(nw==min(10,len(wl)) and pg.query_selector('#hjRes .hjr') is None) if wl else (pg.query_selector('.empty') is not None and pg.query_selector('#hjSpin') is None and 'ønskelisten' in pg.inner_text('.empty')),(len(wl),nw))
    # mens hjulet drejer, sletter en anden fane en øl: vinderen skal stadig være den øl, pilen peger på
    pg.click('[data-hj=alle]'); pg.wait_for_timeout(300); ids0=pg.evaluate("[...document.querySelectorAll('#hjG text')].map(t=>t.textContent)")
    if len(ids0)>=3:
        p2=c.new_page(); p2.goto(URL+'#om'); p2.wait_for_timeout(900); pg.wait_for_timeout(300)
        # Når den anden fane starter, gemmer den, og hjulsiden tegnes igen. Rammer trykket den gamle knap, går det tabt, så der trykkes igen, til drejet er i gang.
        for _ in range(5):
            pg.click('#hjSpin'); pg.wait_for_timeout(250)
            if pg.evaluate("!!document.getElementById('hjSpin')?.disabled"): break
        p2.evaluate("""(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1'));const n=document.querySelectorAll('x').length;S.beers=S.beers.slice(1);localStorage.setItem('olrating-v1',JSON.stringify(S))})()""")
        pg.wait_for_selector('#hjRes .hjr',timeout=9000); p2.close()
        hr2=pg.evaluate("""(()=>{const g=document.getElementById('hjG'),rot=parseFloat(g.style.transform.match(/rotate\\(([-\\d.]+)deg/)[1]),L=[...g.querySelectorAll('text')].map(t=>t.textContent),n=L.length,i=Math.floor(((360-rot%360)%360)/(360/n))%n,h=document.querySelector('#hjRes h2'),nm=h?h.textContent:(document.getElementById('hjRes').textContent.includes('slettet')?'…':'(intet)');return [nm,L[i],n]})()""")
        T('lykkehjul: en anden fane ændrer øllene midt i et drej, og vinderen er stadig den, pilen peger på (blev netop den slettet, står det i stedet)',(hr2[0] if len(hr2[0])<=15 else hr2[0][:14]+'…')==hr2[1] and not over(),(len(ids0),hr2))
        pg.click('[data-hj=ny]'); pg.wait_for_timeout(200)
    pg.goto(URL+'#beer-ux1'); pg.wait_for_timeout(500); pg.click('.rv .who >> nth=0'); pg.wait_for_timeout(400)
    T('navn i en bedømmelse fører til smagerens side',pg.evaluate('location.hash').startswith('#smager-'))
    # --- lange ord uden mellemrum (fx et ølnavn fra en anden bruger) må ikke give vandret scroll
    pg.evaluate("""(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1')),W='Etmegetlangtordudenmellemrumsomaldrigvilstoppe';
      S.beers.forEach((b,i)=>{if(i%2===0){b.name=W+b.name;b.brewery=W+'bryggeriet';b.city=W}});S.reviews.forEach((r,i)=>{if(i%3===0)r.text=W+W});
      S.tours.push({id:'langtur01',name:W+'tur',date:'2026-11-20T19:00',meet:W,note:W,host:'Lucas',stops:[{name:W+'bar',time:'19:00',addr:W+' 12'}],members:[{name:'Lucas'},{name:W.slice(0,38)}]});
      S.tast=[{id:'langsmag1',name:W,host:'Lucas',blind:false,revealed:true,beers:[W,'B'],votes:{Lucas:[5,4]}}];S.vq=[{t:'langsmag1',who:'Lucas',v:[5,4]}];localStorage.setItem('olrating-v1',JSON.stringify(S))})()""")
    pg.goto(URL+'#profil'); pg.reload(); pg.wait_for_timeout(1500); bad=[]
    for v in VIEWS+['#beer-ux1','#beer-ux2','#byttur-langtur01','#smagning-langsmag1','#smager-Lucas','#bryggeri-Etmegetlangtordudenmellemrumsomaldrigvilstoppebryggeriet']:
        pg.goto(URL+v); pg.wait_for_timeout(300)
        if over(): bad.append(v)
    T('lange ord uden mellemrum giver ikke vandret scroll',not bad,bad)
    # --- smagning som billede, smagning ud fra ønskelisten og "Vis flere" på profilen
    pg.goto(URL+'#smagning-langsmag1'); pg.wait_for_timeout(400); pg.evaluate("navigator.canShare=undefined")
    with pg.expect_download(timeout=10000) as dl: pg.click('#tastCard')
    T('smagning: del resultatet som billede (jpg > 40 kB)',dl.value.suggested_filename.endswith('-smagning-olrating.jpg') and os.path.getsize(dl.value.path())>40000,dl.value.suggested_filename)
    # En synkronisering, der er i gang, kan nå at gemme hen over det, testen skriver i lageret. Derfor prøves der igen.
    for _ in range(5):
        pg.evaluate("""(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1'));S.wish=['ux2','ux4','findesikke'];S.reviews=S.reviews.filter(r=>!String(r.id).startsWith('many'));for(let i=0;i<20;i++)S.reviews.push({id:'many'+i,beer:'ux2',who:'Lucas',date:'2026-11-2'+(i%5),s:{look:3,aroma:3,taste:3,feel:3,overall:3},tags:[],again:1,text:''});localStorage.setItem('olrating-v1',JSON.stringify(S))})()""")
        pg.goto(URL+'#smagning'); pg.reload(); pg.wait_for_timeout(1500)
        if ls(pg).get('wish')==['ux2','ux4','findesikke']: break
    lab=pg.inner_text('#wishTast'); pg.click('#wishTast'); pg.wait_for_timeout(200)
    T('smagning: ønskelisten fylder øllene ind','2 øl' in lab and pg.input_value('#sgBeers').count('\n')==1 and 'Havn Stout' in pg.input_value('#sgBeers'),(lab,pg.input_value('#sgBeers')[:80]))
    pg.goto(URL+'#profil'); pg.wait_for_timeout(500); n1=pg.eval_on_selector_all('.cols .box >> nth=1 >> .rv','e=>e.length'); more=pg.inner_text('#moreRev'); pg.click('#moreRev'); pg.wait_for_timeout(400)
    n2=pg.eval_on_selector_all('.cols .box >> nth=1 >> .rv','e=>e.length')
    T('profil: 15 bedømmelser ad gangen og Vis flere',n1==15 and 'mere' in more and n2>n1 and pg.query_selector('#moreRev') is None and not over(),(n1,more,n2))
    T('no JS or console errors',not errs,errs[:4])
    c.close()
with sync_playwright() as p:
    b=getattr(p,os.environ.get('BROWSER','chromium')).launch(); make_photo(b)
    run(b,'pc',(1280,900)); run(b,'mobil',(390,844))
    # siden må ikke hoppe, mens den indlæses (Cumulative Layout Shift under 0,1, som Google kalder god). Måles kun i Chromium.
    if os.environ.get('BROWSER','chromium')=='chromium':
        cls={}
        for vw,h in [((390,844),''),((390,844),'#alle'),((1280,900),''),((1280,900),'#alle'),((390,844),'#om')]:
            c=b.new_context(viewport={'width':vw[0],'height':vw[1]},service_workers='block'); c.route(f'https://{HOST}/**',Mock().handle); pg=c.new_page()
            c.new_cdp_session(pg).send('Emulation.setCPUThrottlingRate',{'rate':4})
            pg.goto(URL); pg.wait_for_timeout(600)
            pg.add_init_script("window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true})")
            pg.goto(URL+h); pg.wait_for_timeout(200); pg.evaluate('scrollTo(0,1200)'); pg.reload(); pg.wait_for_timeout(2000); cls[f'{vw[0]}{h or "#"}']=round(pg.evaluate('__cls'),3); c.close()
        check('siden hopper ikke, mens den indlæses (CLS under 0,1)',max(cls.values())<0.1,cls)
    # en ondsindet backup-fil må ikke ødelægge siden: forkerte typer, kode i navne, en ønskeliste, der ikke er en liste
    c=b.new_context(viewport={'width':390,'height':844},service_workers='block'); c.route(f'https://{HOST}/**',Mock().handle); pg=c.new_page(); perr=[]; pg.on('pageerror',lambda e:perr.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(1200); pg.evaluate("(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1'));S.me='';S.wish=['x9'];localStorage.setItem('olrating-v1',JSON.stringify(S))})()"); pg.reload(); pg.wait_for_timeout(800)
    bad=os.path.join(tempfile.gettempdir(),'ond-backup.json')
    json.dump({'app':'olrating','me':{'x':1},'wish':{'a':1},'beers':[{'id':'ond1','name':'<img src=x onerror=window.__ond=1>','brewery':7,'style':None,'abv':'x'},'ikke et objekt',None],'reviews':[{'id':'ondr','beer':'ond1','who':['x'],'s':'x'},7]},open(bad,'w'))
    pg.goto(URL+'#profil'); pg.wait_for_timeout(400); pg.set_input_files('#importFile',bad); pg.wait_for_timeout(1500)
    st=json.loads(pg.evaluate("localStorage.getItem('olrating-v1')"))
    for h in ['','#profil','#alle','#buddies']: pg.goto(URL+h); pg.wait_for_timeout(300)
    check('backup: en ondsindet fil ødelægger ikke navn, ønskeliste eller siden',st.get('me')=='' and st.get('wish')==['x9'] and all(isinstance(r.get('who'),str) for r in st['reviews']) and not pg.evaluate('window.__ond') and not perr and len(pg.inner_text('#app'))>100,(st.get('me'),st.get('wish'),perr[:2]))
    json.dump({'app':'olrating','me':'  Sofie  ','wish':['x9','ok-2',{'x':1},'<script>'],'beers':[],'reviews':[]},open(bad,'w')); pg.goto(URL+'#profil'); pg.wait_for_timeout(300); pg.set_input_files('#importFile',bad); pg.wait_for_timeout(1200)
    st=json.loads(pg.evaluate("localStorage.getItem('olrating-v1')"))
    check('backup: et gyldigt navn og gyldige øl-id\'er bliver taget med',st.get('me')=='Sofie' and st.get('wish')==['x9','ok-2'],(st.get('me'),st.get('wish')))
    c.close()
    # navne, der også er navne på indbyggede ting i JavaScript, må ikke få siden til at gå ned
    c=b.new_context(viewport={'width':390,'height':844},service_workers='block'); c.route(f'https://{HOST}/**',Mock().handle); pg=c.new_page(); perr=[]; pg.on('pageerror',lambda e:perr.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(1200)
    pg.evaluate("""(()=>{const d=new Date().toISOString().slice(0,10),S=JSON.parse(localStorage.getItem('olrating-v1'));S.me='Lucas';
      S.beers=[{id:'p1',name:'constructor',brewery:'constructor',style:'toString',abv:5,date:d},{id:'p2',name:'hasOwnProperty',brewery:'__proto__',style:'valueOf',abv:5,date:d}];
      const r=(id,b,w,v,t)=>({id,beer:b,who:w,date:d,s:{look:v,aroma:v,taste:v,feel:v,overall:v},tags:t,again:1,text:''});
      S.reviews=[r('q1','p1','Lucas',4,['constructor']),r('q2','p2','Lucas',3,['__proto__']),r('q3','p1','constructor',4,['toString']),r('q4','p2','constructor',3,[]),r('q5','p1','__proto__',2,[]),r('q6','p2','__proto__',5,[]),r('q7','p1','toString',4,[])];
      S.follow=['constructor'];localStorage.setItem('olrating-v1',JSON.stringify(S))})()""")
    seen={}
    for h in ['','#buddies','#venner','#aarets','#toplisten','#beer-p1','#profil','#smager-constructor','#hjul']:
        pg.goto(URL+h); pg.wait_for_timeout(350); seen[h or '#']=len(pg.inner_text('#app'))>80
    check('navne som constructor, toString og __proto__ får ikke siden til at gå ned',not perr and all(seen.values()) and 'constructor' in pg.evaluate("(location.hash='#buddies',new Promise(r=>setTimeout(()=>r(document.getElementById('app').innerText),400)))"),(perr[:3],seen))
    c.close()
    # tekst fra brugerne må aldrig blive til kode på siden: alle felter får et forsøg på at køre et script
    c=b.new_context(viewport={'width':390,'height':844},service_workers='block'); c.route(f'https://{HOST}/**',Mock().handle); pg=c.new_page(); perr=[]; pg.on('pageerror',lambda e:perr.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(1200)
    pg.evaluate("""(()=>{const X=n=>`<img src=x onerror="window.__xss=(window.__xss||[]).concat('${n}')">"'><svg onload="window.__xss=(window.__xss||[]).concat('${n}s')">`,d=new Date().toISOString().slice(0,10),S=JSON.parse(localStorage.getItem('olrating-v1'));
      S.me='Lucas';S.beers=[{id:'x1',name:X('navn'),brewery:X('bryg'),style:X('stil'),abv:5,date:d,city:X('by'),note:X('note')},{id:'x2',name:'Almindelig',brewery:'Bryg',style:'Pilsner',abv:5,date:d}];
      const r=(id,b,w,v)=>({id,beer:b,who:w,date:d,s:{look:v,aroma:v,taste:v,feel:v,overall:v},tags:[X('tag')],again:1,text:X('tekst')});
      S.reviews=[r('y1','x1','Lucas',4),r('y2','x2','Lucas',3),r('y3','x1',X('smager'),4),r('y4','x2',X('smager'),3)];S.follow=[X('foelg')];S.wish=['x1'];localStorage.setItem('olrating-v1',JSON.stringify(S))})()""")
    pg.reload(); pg.wait_for_timeout(900)
    for lang in ('da','en'):   # den engelske udgave bygger nogle tekster om, så den testes også
        if lang=='en': pg.goto(URL+'#indstillinger'); pg.wait_for_timeout(300); pg.click('[data-setlang=en]'); pg.wait_for_timeout(900)
        for h in ['','#alle','#toplisten','#aarets','#swipe','#buddies','#hjul','#venner','#profil','#beer-x1','#sammenlign','#galleri','#smagning','#nyt','#dagbog','#kalender','#stilguide','#om']:
            pg.goto(URL+h); pg.wait_for_timeout(300)
    if pg.query_selector('#hjSpin'): pg.goto(URL+'#hjul'); pg.wait_for_timeout(300); pg.click('[data-hj=alle]'); pg.wait_for_timeout(200); pg.click('#hjSpin'); pg.wait_for_timeout(5200)
    xs=pg.evaluate("window.__xss||[]")
    check('ingen tekst fra brugerne bliver kørt som kode på nogen side',not xs and not perr,(xs[:6],perr[:3]))
    c.close()
    # mindre bevægelse: lykkehjulet vælger med det samme, og der er hverken loading screen eller drys
    c=b.new_context(viewport={'width':390,'height':844},service_workers='block',reduced_motion='reduce'); c.route(f'https://{HOST}/**',Mock().handle); pg=c.new_page()
    pg.goto(URL+'#hjul'); pg.wait_for_timeout(900); ld=pg.evaluate("getComputedStyle(document.getElementById('load')||document.body).display")
    if pg.query_selector('#hjSpin'): pg.click('#hjSpin'); pg.wait_for_timeout(250)
    check('mindre bevægelse: ingen loading screen, hjulet viser resultatet med det samme og uden drys',(pg.query_selector('#load') is None or ld=='none') and (pg.query_selector('#hjSpin') is None or pg.query_selector('#hjRes .hjr') is not None) and pg.query_selector('.dot') is None,ld)
    c.close()
    # widgets uden billeder: en øl uden billede sendes ikke, og widget-data virker stadig, også uden besøgstæller
    M0=Mock(); M0.has_besoeg=False; c=b.new_context(viewport={'width':390,'height':844},service_workers='block'); c.route(f'https://{HOST}/**',M0.handle); pg=c.new_page()
    pg.add_init_script("window.__w=[];window.__wi=[];window.OlratingApp={updateWidget:j=>window.__w.push(j),updateImages:j=>window.__wi.push(j)};")
    pg.goto(URL); pg.wait_for_timeout(2500); w0=json.loads(pg.evaluate("window.__w.at(-1)||'{}'")); wi0=pg.evaluate("window.__wi.length?JSON.parse(window.__wi.at(-1)):{}")
    pg.goto(URL+'#om'); pg.wait_for_timeout(500)
    check('uden besøgstæller og billeder: widget-data har ingen besøgstal, og Om viser tre tal',w0.get('site',{}).get('visits') is None and isinstance(wi0,dict) and pg.eval_on_selector_all('#omTal .ex-t','e=>e.length')==3,(w0.get('site'),wi0))
    c.close()
    # offline via service worker
    # Her skal service workeren være med. Kald fra en side med service worker kan gå uden om den efterlignede database (set i WebKit),
    # så siden får at vide, at den er offline, og prøver slet ikke at synkronisere. Så rører testen aldrig den rigtige database.
    c=b.new_context(); c.route(f'https://{HOST}/**',Mock().handle); pg=c.new_page(); pg.add_init_script("Object.defineProperty(Navigator.prototype,'onLine',{get:()=>false})"); pg.goto(URL); pg.wait_for_timeout(3500)
    sw=pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!(r&&r.active))")
    # en adresse, der ikke findes, må ikke erstatte forsiden i service workerens lager
    try: pg.goto(URL+'findes-ikke'); pg.wait_for_timeout(500)
    except Exception: pass
    c.set_offline(True); ok=False; how=[]
    for navn,nav in (('genindlæs',lambda: pg.reload()),('åbn igen',lambda: pg.goto(URL))):   # i Firefox fejlede genindlæsning uden net i testen. Derfor prøves også at åbne siden igen, og resultatet af begge skrives ud
        try: nav(); pg.wait_for_timeout(1200); ok=len(pg.inner_text('#app'))>100; how.append((navn,ok))
        except Exception as e: ok=False; how.append((navn,str(e)[:80]))
        if ok: break
    # I Firefox afviser testværktøjet al navigation uden net (NS_ERROR_OFFLINE), før service workeren bliver spurgt. Der kan tjekket ikke bruges.
    if os.environ.get('BROWSER')=='firefox': print('SPRING OVER [offline]: kan ikke prøves i Firefox i testen. Service worker aktiv:',sw)
    else: check('[offline] service worker active and page loads without net',sw and ok,(sw,how))
    c.close(); b.close()
# static checks
root=ROOT+'/'; s=open(root+'index.html').read(); sw=open(root+'sw.js').read()
miss=[f for f in re.findall(r"'\./?([\w./-]+\.\w+)'",sw.split('SHELL=')[1].split(']')[0]) if not os.path.exists(root+f)]
check('[filer] everything the service worker caches exists',not miss,miss)
loc=set(re.findall(r'(?:src|href)="((?:img|fonts|js)/[^"#?]+)"',s))|set(re.findall(r"url\(((?:img|fonts)/[^)]+)\)",s))|set(re.findall(r"'((?:img|js)/[\w./-]+)'",s))
miss=[f for f in loc if not os.path.exists(root+f)]; check('[filer] all referenced images, fonts and scripts exist',not miss,miss)
m=json.load(open(root+'manifest.webmanifest')); miss=[i['src'] for i in m['icons'] if not os.path.exists(root+i['src'])]; check('[filer] manifest valid, icons exist',not miss,miss)
dkc=s[s.index('const DKC='):s.index('};',s.index('const DKC='))]; pts=re.findall(r'\[([\d.]+),([\d.]+)\]',dkc); out=[q for q in pts if not(8.0<=float(q[0])<=15.3 and 54.5<=float(q[1])<=57.8)]
check('[kort] over 250 byer i tabellen, og alle ligger i Danmark',len(pts)>250 and not out,(len(pts),out[:3]))
check('[links] downloads point at fixed tags, none at latest','releases/latest' not in s and s.count('releases/download/android-app/olrating.apk')>=2 and 'desktop-app/olrating-windows.exe' in s)
check('[sikkerhed] no secret keys in repo',os.system(f"cd {root} && git grep -nIE 'sb_secret_|service_role|BEGIN (RSA |EC )?PRIVATE KEY|storePassword *= *\"[^\"]' -- . ':!docs' ':!CLAUDE.md' ':!supabase' ':!tests' >/dev/null")!=0)
print('ALL PASS' if all(res) else f'{res.count(False)} FAILED of {len(res)}')
sys.exit(0 if all(res) else 1)
