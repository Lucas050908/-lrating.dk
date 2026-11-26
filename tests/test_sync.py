"""To enheder (Lucas og Magnus) mod en efterligning af databasen: deling, billeder, rettigheder, offline, sletning og byttur.
Kør: python3 -m http.server 8811 &  og derefter  python3 tests/test_sync.py"""
import json,base64,re
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
    rh=Bp.get_attribute('#reportBtn','href') or ''
    check('B: kan anmelde andres øl og bedømmelser pr. mail',rh.startswith('mailto:') and '@' in rh and 'subject=' in rh and 'ub1' in rh and Bp.eval_on_selector_all('.rv a[href^="mailto:"]','e=>e.length')==1,rh[:60])
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
    # smagning med venner: opret blindt, stem på to enheder, afslør, slet
    A.goto(URL+'#smagning'); A.wait_for_timeout(500)
    A.fill('#sgName','Julefrokost'); A.fill('#sgBeers','Julebryg\nFjord IPA\nHavn Stout'); A.click('#tastForm button'); A.wait_for_timeout(3000)
    sid=A.evaluate('location.hash')[10:]
    check('smagning: gemt i databasen som blind',sid in M.t['tastings'] and M.t['tastings'][sid]['data']['blind'] and len(M.t['tastings'][sid]['data']['beers'])==3,list(M.t['tastings']))
    Bp.goto(URL+'#smagning-'+sid); Bp.wait_for_timeout(2500)
    txt=Bp.inner_text('#voteForm')
    check('smagning: gæst ser Øl A-C og ikke navnene','Øl A' in txt and 'Øl C' in txt and 'Julebryg' not in txt and Bp.query_selector('#tastReveal') is None,txt[:120])
    for i,v in enumerate([5,3,1]): Bp.click(f'#voteForm .rate[data-k="t{i}"] [data-star="{v}"]')
    Bp.click('#voteForm button.btn'); Bp.wait_for_timeout(2500)
    check('smagning: gæstens stemme i databasen',M.votes.get((sid,'Magnus'),{}).get('data',{}).get('v')==[5,3,1],dict(M.votes))
    A.wait_for_timeout(7000)
    check('smagning: værten ser at Magnus har stemt','Magnus' in A.inner_text('#voteForm') and A.query_selector('#tastReveal:not([disabled])') is not None)
    for i,v in enumerate([4,4,2]): A.click(f'#voteForm .rate[data-k="t{i}"] [data-star="{v}"]')
    A.click('#voteForm button.btn'); A.wait_for_timeout(2500)
    A.fill('#vWho','Sofie')
    for i,v in enumerate([3,5,5]): A.click(f'#voteForm .rate[data-k="t{i}"] [data-star="{v}"]')
    A.click('#voteForm button.btn'); A.wait_for_timeout(2500)
    check('smagning: flere kan stemme på samme telefon',sorted(n for (t,n) in M.votes if t==sid)==['Lucas','Magnus','Sofie'],list(M.votes))
    A.click('#tastReveal'); A.wait_for_timeout(2500)
    check('smagning: afsløring gemt',M.t['tastings'][sid]['data']['revealed']==True)
    Bp.wait_for_timeout(7500)
    pod=Bp.evaluate("[...document.querySelectorAll('.podium li b:first-child')].map(x=>x.textContent)") if Bp.query_selector('.podium') else None
    check('smagning: gæsten får resultatet med rigtige navne, vinderen øverst',pod and pod[0]=='Julebryg' and Bp.inner_text('.podium .win .big').strip()=='4,0' and 'var Øl A' in Bp.inner_text('.podium .win'),pod)
    check('smagning: resultatet er synligt efter animationen',Bp.evaluate("[...document.querySelectorAll('.podium li')].every(l=>getComputedStyle(l).opacity==='1')"))
    A.click('#tastDel'); A.wait_for_timeout(3000)
    check('smagning: vært sletter for alle',sid not in M.t['tastings'] and not [k for k in M.votes if k[0]==sid])
    Bp.wait_for_timeout(7500)
    check('smagning: forsvinder hos gæsten',not ls(Bp)['tast'])
    # fjendtlige data: en anden klient har lagt kode og forkerte typer i databasen
    X='<img src=x onerror="window.__xss=1">'; Q='"><script>window.__xss=1</script><svg onload=window.__xss=1>'
    M.t['beers']['xss1']={'id':'xss1','owner':'ond','created_at':'9','name':X,'brewery':X,'img':'javascript:window.__xss=1','data':{'style':Q,'abv':X,'ibu':{'a':1},'color':'" onmouseover="window.__xss=1','size':[1,2],'price':'abc','city':Q,'country':X,'date':Q,'addedBy':X,'desc':Q,'code':'<x>12','af':'ja'}}
    M.t['beers']['x" onmouseover="window.__xss=1']={'id':'x" onmouseover="window.__xss=1','owner':'ond','created_at':'9','name':'Ugyldigt id','brewery':'x','data':{}}
    M.t['beers']['ok1']={'id':'ok1','owner':'ond','created_at':'9','name':'Helt almindelig øl','brewery':'Pænt Bryggeri','img':None,'data':{'style':'Pilsner','abv':4.6,'city':'Aalborg','date':'2026-11-20','addedBy':'Sofie'}}
    M.t['reviews']['rxss1']={'id':'rxss1','beer':'xss1','owner':'ond','created_at':'9','who':X,'img':'https://evil.example/x.png','data':{'s':{'look':X,'aroma':99,'taste':None},'tags':[X,{'a':1},5],'text':Q,'prof':'x','again':X,'date':'i går'}}
    M.t['reviews']['rxss2']={'id':'rxss2','beer':'ok1','owner':'ond','created_at':'9','who':'Sofie','data':'ikke et objekt'}
    M.t['tours']['xsstour1']={'id':'xsstour1','owner':'ond','data':{'name':X,'date':Q,'meet':X,'note':Q,'host':X,'stops':[{'name':X,'time':Q,'addr':X},'tekst',None]}}
    M.members[('xsstour1',X)]='ond'
    M.t['tastings']['xsstast1']={'id':'xsstast1','owner':'ond','data':{'name':X,'host':X,'blind':'x','revealed':True,'beers':[X,Q,{'a':1}]}}
    M.votes[('xsstast1',X)]={'owner':'ond','data':{'v':[X,99,None]}}; M.votes[('xsstast1','__proto__')]={'owner':'ond','data':{'v':[5,5,5]}}
    H=ctx('Offer',(390,844)); H.goto(URL); H.wait_for_timeout(3500)
    sH=ls(H); ids=sorted(b['id'] for b in sH['beers'])
    xb=[b for b in sH['beers'] if b['id']=='xss1'][0]
    check('fjendtlig: ugyldigt id droppes, resten renses',ids==['ok1','xss1'] and isinstance(xb['abv'],(int,float)) and xb['style']=='Andet' and xb['img']=='' and xb['size']=='' and xb['af'] is False and re.match(r'^\d{4}-\d\d-\d\d$',xb['date']),(ids,xb))
    rx=[r for r in sH['reviews'] if r['id']=='rxss1'][0]
    check('fjendtlig: bedømmelse renset',rx['s']=={'look':1,'aroma':5,'taste':1,'feel':1,'overall':1} and rx['img']=='' and rx['prof'] is None and rx['again']==1 and len(rx['tags'])==1,rx)
    H.goto(URL+'#byttur'); H.wait_for_timeout(300); H.fill('#tCode','xsstour1'); H.click('#codeForm button'); H.wait_for_timeout(2000)
    H.goto(URL+'#smagning-xsstast1'); H.wait_for_timeout(4500)
    pages=['','#alle','#beer-xss1','#beer-ok1','#toplisten','#galleri','#stilguide','#venner','#smager-'+X.replace('"','%22').replace(' ','%20'),'#bryggeri-'+X.replace('"','%22').replace(' ','%20'),'#byttur','#byttur-xsstour1','#smagning','#smagning-xsstast1','#profil','#dagbog','#sammenlign']
    bad=[]
    for h in pages:
        H.goto(URL+h); H.wait_for_timeout(450)
        if H.evaluate('window.__xss') or len(H.inner_text('#app'))<30: bad.append(h)
    H.goto(URL+'#alle'); H.wait_for_timeout(500); H.fill('#q','img'); H.wait_for_timeout(300)
    check('fjendtlig: ingen kode bliver kørt på nogen side',not bad and not H.evaluate('window.__xss') and H.evaluate("document.querySelectorAll('#app script, #app [onerror], #app [onload], #app [onmouseover]').length")==0,bad)
    H.fill('#q','almindelig'); H.wait_for_timeout(300)
    check('fjendtlig: almindelige øl vises stadig',H.eval_on_selector_all('#grid .card','e=>e.length')==1)
    for k in ['xss1','x" onmouseover="window.__xss=1','ok1']: M.t['beers'].pop(k,None)
    for k in ['rxss1','rxss2']: M.t['reviews'].pop(k,None)
    check('no JS errors',not errs,errs[:5])
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
