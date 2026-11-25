"""To enheder (Lucas og Magnus) mod en efterligning af databasen: deling, billeder, rettigheder, offline, sletning og byttur.
Kør: python3 -m http.server 8811 &  og derefter  python3 tests/test_sync.py"""
import json,base64
import os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
URL=os.environ.get('SITE','http://localhost:8811/')
from mock_supabase import Mock,HOST,JPG
from playwright.sync_api import sync_playwright
DATA='data:image/jpeg;base64,'+base64.b64encode(JPG).decode()
C={"look":4,"aroma":4,"taste":5,"feel":4,"overall":5}
stA={"beers":[{"id":"ub1","name":"Skærgaard Pilsner","brewery":"Fanø Bryghus","style":"Pilsner","city":"Fanø","abv":5,"size":"33 cl flaske","date":"2026-11-20","addedBy":"Lucas","img":DATA}],
     "reviews":[{"id":"rb1","beer":"ub1","who":"Lucas","date":"2026-11-20","s":C,"text":"God"}],"me":"Lucas"}
ok=True
def check(name,cond,extra=''):
    global ok; ok=ok and bool(cond); print(('PASS ' if cond else 'FAIL ')+name,extra)
def ls(pg): return json.loads(pg.evaluate("localStorage.getItem('olrating-v1')"))
def mut(pg,js,wait=3000):
    pg.evaluate("(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1'));"+js+";localStorage.setItem('olrating-v1',JSON.stringify(S))})()")
    pg.reload(); pg.wait_for_timeout(wait)
with sync_playwright() as p:
    b=p.chromium.launch(); M=Mock(); errs=[]
    def ctx(name,vw,state=None):
        c=b.new_context(viewport={'width':vw[0],'height':vw[1]}); c.route(f'https://{HOST}/**',M.handle)
        pg=c.new_page(); pg.on('pageerror',lambda e:errs.append(name+': '+str(e)))
        pg.on('console',lambda m:errs.append(name+' console: '+m.text) if m.type=='error' and 'Synk' not in m.text and 'ERR_FAILED' not in m.text else None)
        init="window.__sh=[];navigator.share=async d=>{window.__sh.push(d)};window.confirm=()=>true;window.prompt=()=>'%s';"%name
        if state: init+="if(!localStorage.getItem('olrating-v1'))localStorage.setItem('olrating-v1',%s);"%json.dumps(json.dumps(state))
        pg.add_init_script(init); return pg
    A=ctx('Lucas',(1280,900),stA); A.goto(URL); A.wait_for_timeout(3500)
    check('globals reachable',A.evaluate("typeof sbSync")=='function')
    check('A: beer pushed',list(M.t['beers'])==['ub1'],M.t['beers'].get('ub1',{}).get('name'))
    check('A: review pushed',list(M.t['reviews'])==['rb1'])
    check('A: image uploaded',len(M.store)==1 and (M.t['beers']['ub1'].get('img') or '').startswith('https://'+HOST+'/storage/v1/object/public/billeder/'),M.t['beers']['ub1'].get('img'))
    check('A: data column has no image/owner',not any(k in M.t['beers']['ub1']['data'] for k in('img','owner','rs','avg','id','name')),list(M.t['beers']['ub1']['data']))
    sA=ls(A); check('A: local img switched to URL',sA['beers'][0]['img'].startswith('https://'),sA['beers'][0]['img'][:60])
    n=len(M.log); A.evaluate("sbSync()"); A.wait_for_timeout(1500)
    check('A: second sync sends no writes',not [l for l in M.log[n:] if l.startswith(('POST /rest','DELETE','POST /storage'))],[l for l in M.log[n:] if not l.startswith('GET')])
    Bp=ctx('Magnus',(390,844)); Bp.goto(URL+'#alle'); Bp.wait_for_timeout(3500)
    check('B: sees the beer',Bp.eval_on_selector_all('#grid .card','e=>e.length')==1)
    check('B: image loads from storage',Bp.evaluate("(()=>{const i=document.querySelector('#grid .card img');return !!i&&i.src.includes('/storage/v1/object/public/')&&i.naturalWidth>0})()"))
    Bp.goto(URL+'#beer-ub1'); Bp.wait_for_timeout(800)
    check('B: cannot delete or edit others',Bp.query_selector('#delBeer') is None and Bp.query_selector('#editBeer') is None and Bp.query_selector('[data-delrev]') is None)
    # B adds a review and tries to tamper with A's beer
    mut(Bp,"S.me='Magnus';S.reviews.push({id:'rm1',beer:'ub1',who:'Magnus',date:'2026-11-25',s:{look:3,aroma:3,taste:4,feel:3,overall:4},text:'Fin'});S.beers[0].name='HACKET'")
    check('B: review pushed',sorted(M.t['reviews'])==['rb1','rm1'])
    check('B: tamper rejected, name unchanged in db',M.t['beers']['ub1']['name']=='Skærgaard Pilsner')
    check('B: local name restored',ls(Bp)['beers'][0]['name']=='Skærgaard Pilsner')
    A.evaluate("sbSync()"); A.wait_for_timeout(1500)
    check('A: got Magnus review',len(ls(A)['reviews'])==2)
    # share card with a cross-origin image must not taint the canvas
    A.goto(URL+'#beer-ub1'); A.wait_for_timeout(700)
    with A.expect_download(timeout=8000) as dl: A.click('#cardBtn')
    check('A: share card works with remote image',dl.value.suggested_filename.endswith('.jpg'))
    # offline: edits queue and sync later
    M.down=True
    mut(Bp,"S.reviews.find(r=>r.id==='rm1').text='Rettet offline'",2500); Bp.goto(URL+'#profil'); Bp.wait_for_timeout(1500)
    check('B: offline shows not connected','Ikke forbundet' in Bp.inner_text('.sbst') and M.t['reviews']['rm1']['data'].get('text')=='Fin',Bp.inner_text('.sbst')[:40])
    M.down=False; Bp.evaluate("sbSync()"); Bp.wait_for_timeout(1500)
    check('B: edit synced after reconnect',M.t['reviews']['rm1']['data'].get('text')=='Rettet offline')
    # no surprise re-render while typing
    Bp.goto(URL+'#beer-ub1'); Bp.wait_for_timeout(600)
    ta=Bp.query_selector('#revForm textarea, #revForm input[type=text]'); 
    if ta: ta.fill('halvt skrevet'); 
    mut(A,"S.reviews.find(r=>r.id==='rb1').text='Ny tekst'",2500)
    Bp.evaluate("sbSync()"); Bp.wait_for_timeout(1200)
    check('B: form text kept during sync',(not ta) or Bp.evaluate("(document.querySelector('#revForm textarea, #revForm input[type=text]')||{}).value")=='halvt skrevet')
    check('B: data still updated underneath',[r for r in ls(Bp)['reviews'] if r['id']=='rb1'][0]['text']=='Ny tekst')
    # tours
    A.goto(URL+'#byttur'); A.wait_for_timeout(500)
    A.fill('#tName','J-dag i Aalborg'); A.fill('#tDate','2026-11-27T20:00'); A.fill('#tMeet','Jomfru Ane Gade'); A.click('#tourForm button'); A.wait_for_timeout(500)
    A.fill('#sName','Søgaards Bryghus'); A.fill('#sTime','20:15'); A.click('#stopForm button'); A.wait_for_timeout(3000)
    tid=list(M.t['tours'])[0] if M.t['tours'] else None
    check('A: tour pushed with stop',tid and len(M.t['tours'][tid]['data']['stops'])==1 and (tid,'Lucas') in M.members,tid)
    Bp.goto(URL+'#byttur'); Bp.wait_for_timeout(500); Bp.fill('#tCode',tid or 'x'); Bp.click('#codeForm button'); Bp.wait_for_timeout(1500)
    check('B: found tour by code',Bp.evaluate('location.hash')=='#byttur-'+str(tid) and Bp.inner_text('h1')=='J-dag i Aalborg')
    Bp.click('#tourJoin'); Bp.wait_for_timeout(2500)
    check('B: join stored in db, no share fallback',(tid,'Magnus') in M.members and Bp.evaluate('window.__sh.length')==0)
    A.fill('#sName','Irish House'); A.fill('#sTime','22:00'); A.click('#stopForm button'); A.wait_for_timeout(3000)
    check('A: sees Magnus on the list','Magnus' in A.inner_text('.mem'))
    Bp.evaluate("sbSync()"); Bp.wait_for_timeout(1500)
    check('B: got new stop',Bp.eval_on_selector_all('.route li','e=>e.length')==2)
    # delete with undo window
    A.goto(URL+'#beer-ub1'); A.wait_for_timeout(600); A.click('#delBeer'); A.wait_for_timeout(3000)
    check('A: delete waits for undo window','ub1' in M.t['beers'] and len(ls(A)['beers'])==0)
    A.wait_for_timeout(10500)
    check('A: beer and reviews deleted from db',not M.t['beers'] and not M.t['reviews'],(list(M.t['beers']),list(M.t['reviews'])))
    check('A: image deleted from storage',len(M.store)==0,list(M.store))
    Bp.evaluate("sbSync()"); Bp.wait_for_timeout(1500)
    check('B: beer gone locally',len(ls(Bp)['beers'])==0 and len(ls(Bp)['reviews'])==0)
    # tours: participant leaves, host deletes for everyone
    Bp.goto(URL+'#byttur-'+tid); Bp.wait_for_timeout(600)
    check('B: is not host, sees leave button',Bp.inner_text('#tourDel')=='Fjern turen fra min liste' and Bp.query_selector('#stopForm') is None)
    Bp.click('#tourDel'); Bp.wait_for_timeout(3000)
    check('B: left the tour in db',(tid,'Magnus') not in M.members and (tid,'Lucas') in M.members,list(M.members))
    Bp.goto(URL+'#byttur'); Bp.wait_for_timeout(400); Bp.fill('#tCode',tid); Bp.click('#codeForm button'); Bp.wait_for_timeout(1500); Bp.click('#tourJoin'); Bp.wait_for_timeout(2500)
    A.goto(URL+'#byttur-'+tid); A.wait_for_timeout(600); A.click('#tourDel'); A.wait_for_timeout(3000)
    check('A: host deleted tour for everyone',not M.t['tours'] and not M.members,(list(M.t['tours']),list(M.members)))
    Bp.evaluate("sbSync()"); Bp.wait_for_timeout(1500)
    check('B: deleted tour disappears',len(ls(Bp)['tours'])==0)
    check('no JS errors',not errs,errs[:5])
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
