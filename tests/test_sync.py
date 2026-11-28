"""To enheder (Lucas og Magnus) mod en efterligning af databasen: deling, billeder, rettigheder, offline, sletning og byttur.
Kør: python3 -m http.server 8811 &  og derefter  python3 tests/test_sync.py"""
import json,base64,re
import os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
URL=os.environ.get('SITE','http://localhost:8811/')
from mock_supabase import Mock,HOST,JPG
# Safaris motor (WebKit) melder en forespørgsel, der bliver afbrudt, fordi testen skifter side midt i en synkronisering, som "... due to access control checks".
# Det er ikke en fejl på siden (Chromium og Firefox melder intet), så den besked tæller ikke med i WebKit.
WK_NOISE=lambda t: os.environ.get('BROWSER')=='webkit' and 'due to access control checks' in t
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
    b=getattr(p,os.environ.get('BROWSER','chromium')).launch(); M=Mock(); errs=[]
    def ctx(name,vw,state=None,quiet=False):   # quiet: svar som 403, 422 og 429 er ventede (forkert kode, mailen findes, for mange mails)
        c=b.new_context(viewport={'width':vw[0],'height':vw[1]},locale='da-DK',service_workers='block'); c.route(f'https://{HOST}/**',M.handle)   # uden service worker: ellers kan kald gå uden om den efterlignede database (set i WebKit)
        pg=c.new_page(); pg.on('pageerror',lambda e:None if WK_NOISE(str(e)) else errs.append(name+': '+str(e)))
        # Browseren skriver "Failed to load resource", når databasen svarer med en fejlkode. Det er ventet, når testen fx sletter en tur, mens en tilmelding er på vej (svar 409).
        # Den besked tæller kun ikke med, når databasen faktisk har svaret med en fejl i den fane. Så opdages en manglende fil på siden stadig
        bad=[]; pg.on('response',lambda r:bad.append(r.status) if r.status>=400 and HOST in r.url else None)
        pg.on('console',lambda m:errs.append(name+' console: '+m.text) if m.type=='error' and 'Synk' not in m.text and 'ERR_FAILED' not in m.text and 'CORS request did not succeed' not in m.text and not ((quiet or bad) and 'Failed to load resource' in m.text) else None)
        init="window.__sh=[];navigator.share=async d=>{window.__sh.push(d)};window.confirm=()=>true;window.prompt=()=>'%s';"%name
        if state: init+="if(!localStorage.getItem('olrating-v1'))localStorage.setItem('olrating-v1',%s);"%json.dumps(json.dumps(state))
        pg.add_init_script(init); return pg
    A=ctx('Lucas',(1280,900),stA); A.goto(URL); A.wait_for_timeout(3500)
    check('globals reachable',A.evaluate("typeof sbSync")=='function')
    check('A: beer pushed',list(M.t['beers'])==['ub1'],M.t['beers'].get('ub1',{}).get('name'))
    check('A: review pushed',list(M.t['reviews'])==['rb1'])
    check('besøg: siden tæller ét besøg, når den åbnes',M.visits==1001 and M.visits_today==5,(M.visits,M.visits_today))
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
    A.click('#voteForm .rate[data-k="t2"] [data-step="-1"]')   # kommatal: 4,9 (ændrer ikke på, hvem der vinder)
    A.click('#voteForm button.btn'); A.wait_for_timeout(2500)
    for _ in range(12):   # langsomme browsere (Firefox på GitHub) kan være længere om at sende stemmen
        if sorted(n for (t,n) in M.votes if t==sid)==['Lucas','Magnus','Sofie']: break
        A.wait_for_timeout(500)
    check('smagning: flere kan stemme på samme telefon',sorted(n for (t,n) in M.votes if t==sid)==['Lucas','Magnus','Sofie'],list(M.votes))
    check('smagning: en stemme kan være et kommatal',M.votes.get((sid,'Sofie'),{}).get('data',{}).get('v')==[3,5,4.9],M.votes.get((sid,'Sofie')))
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
    pages=['','#alle','#beer-xss1','#beer-ok1','#toplisten','#aarets','#galleri','#stilguide','#venner','#smager-'+X.replace('"','%22').replace(' ','%20'),'#bryggeri-'+X.replace('"','%22').replace(' ','%20'),'#byttur','#byttur-xsstour1','#smagning','#smagning-xsstast1','#profil','#dagbog','#sammenlign']
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
    # --- konto: login med kode på mail, samme konto på to enheder, mailvalg, log ud og slet
    kb=lambda i,n:{"beers":[{"id":i,"name":n,"brewery":"Testbryg","style":"Pilsner","abv":5,"size":"33 cl flaske","date":"2026-11-20","addedBy":"Lucas","img":""}],"reviews":[],"me":"Lucas"}
    sb=lambda pg:json.loads(pg.evaluate("localStorage.getItem('olrating-sb')"))
    K1=ctx('Lucas',(390,844),{**kb('uk1','Kontoøl et'),'wish':['uk1'],'follow':['Sofie']},quiet=True); K1.goto(URL+'#profil'); K1.wait_for_timeout(3000)
    check('konto: skjult, indtil den er slået til',K1.query_selector('#acctBox') is None)
    K1.goto(URL+'#konto-test'); K1.wait_for_timeout(900); uid1=sb(K1)['user']['id']
    K1.fill('#acMail','Lucas@Example.dk'); K1.click('#acctForm button')
    try: K1.wait_for_selector('#acCode',timeout=8000)
    except Exception: pass
    check('konto: en kode sendes til mailen',M.mails[-1:]==[('lucas@example.dk','email_change','123456')] and K1.query_selector('#acCode') is not None,M.mails[-1:])
    K1.fill('#acCode','000000'); K1.click('#acctCode button'); K1.wait_for_timeout(1000)
    check('konto: en forkert kode afvises',K1.query_selector('#acCode') is not None and not M.users[uid1]['email'] and 'passer ikke' in K1.inner_text('#toast'),K1.inner_text('#toast'))
    K1.fill('#acCode','123456'); K1.click('#acctCode button'); K1.wait_for_timeout(2500); se=sb(K1)
    check('konto: logget ind med samme bruger-id, og øllen er stadig min',se['user']['id']==uid1 and se['user'].get('email')=='lucas@example.dk' and 'lucas@example.dk' in K1.inner_text('#acctBox') and M.t['beers']['uk1']['owner']==uid1,se['user'])
    K1.check('#mp_my_beer'); K1.wait_for_timeout(800); K1.check('#mp_friends'); K1.wait_for_timeout(800); pr=M.prefs.get(uid1,{})
    check('konto: mailvalg gemmes med navn og sprog',pr.get('my_beer') is True and pr.get('friends') is True and pr.get('news') is False and pr.get('name')=='Lucas' and pr.get('lang')=='da',pr)
    K1.evaluate("sbSync()"); K1.wait_for_timeout(1800); kd=M.kdata.get(uid1,{})
    check('konto: navn, ønskeliste og dem, man følger, gemmes på kontoen',kd.get('me')=='Lucas' and kd.get('wish')==['uk1'] and kd.get('follow')==['Sofie'],kd)
    K2=ctx('',(390,844),{**kb('uk2','Kontoøl to'),'me':'','wish':['uk2'],'follow':['Emil','sofie']},quiet=True); K2.goto(URL+'#konto-test'); K2.wait_for_timeout(3500); uid2=sb(K2)['user']['id']
    ok0=uid2!=uid1 and M.t['beers']['uk2']['owner']==uid2
    K2.fill('#acMail','lucas@example.dk'); K2.click('#acctForm button')
    try: K2.wait_for_selector('#acCode',timeout=8000)   # venter på svaret i stedet for et fast tidsrum (Firefox var en gang for langsom)
    except Exception: pass
    check('konto: findes mailen i forvejen, sendes en login-kode',ok0 and M.mails[-1:]==[('lucas@example.dk','magiclink','654321')],M.mails[-1:])
    K2.fill('#acCode','654321'); K2.click('#acctCode button'); K2.wait_for_timeout(3000); se2=sb(K2)
    check('konto: samme konto på den anden enhed, og dens øl er flyttet over på kontoen',se2['user']['id']==uid1 and M.t['beers']['uk2']['owner']==uid1 and uid2 not in M.users,(se2['user'],M.t['beers']['uk2']['owner']))
    K2.evaluate("sbSync()"); K2.wait_for_timeout(1800); l2=ls(K2); kd=M.kdata.get(uid1,{})
    check('konto: ny enhed får navn, ønskeliste og følger fra kontoen, og dens egne lægges til',l2['me']=='Lucas' and sorted(l2['wish'])==['uk1','uk2'] and sorted(x.lower() for x in l2['follow'])==['emil','sofie'] and sorted(kd.get('wish',[]))==['uk1','uk2'],(l2['me'],l2['wish'],l2['follow'],kd))
    K1.evaluate("sbSync()"); K1.wait_for_timeout(1800); l1=ls(K1)
    check('konto: den første enhed får det med, som den anden havde',sorted(l1['wish'])==['uk1','uk2'] and sorted(x.lower() for x in l1['follow'])==['emil','sofie'],(l1['wish'],l1['follow']))
    K2.goto(URL+'#beer-uk1'); K2.wait_for_timeout(1500); e1=K2.query_selector('#editBeer') is not None
    K2.goto(URL+'#beer-uk2'); K2.wait_for_timeout(900); e2=K2.query_selector('#editBeer') is not None
    check('konto: begge øl kan rettes fra den anden enhed',e1 and e2,(e1,e2))
    K2.goto(URL+'#beer-uk1'); K2.wait_for_timeout(900); K2.click('#wishBtn'); K2.wait_for_timeout(300); K2.evaluate("sbSync()"); K2.wait_for_timeout(1800)
    K1.evaluate("sbSync()"); K1.wait_for_timeout(1800); l1=ls(K1)
    check('konto: fjernes en øl fra ønskelisten på én enhed, forsvinder den også på den anden',ls(K2)['wish']==['uk2'] and l1['wish']==['uk2'] and M.kdata[uid1].get('wish')==['uk2'],(ls(K2)['wish'],l1['wish'],M.kdata[uid1]))
    K2.goto(URL+'#profil'); K2.wait_for_timeout(1800)
    check('konto: mailvalgene følger med kontoen',K2.is_checked('#mp_my_beer') and not K2.is_checked('#mp_news'))
    # afmeld-linket nederst i mails: virker uden login, men først når man trykker på knappen
    tok=M.unsub.get(uid1,''); K2.goto(URL+'#afmeld-ikke-en-noegle'); K2.wait_for_timeout(700)
    check('afmeld: et ugyldigt link siger det og har ingen knap','ikke gyldigt' in K2.inner_text('#unsubBox') and K2.query_selector('#unsubGo') is None,K2.inner_text('#unsubBox'))
    K2.goto(URL+'#afmeld-00000000-0000-4000-a000-999999999999'); K2.wait_for_timeout(700); K2.click('#unsubGo'); K2.wait_for_timeout(900)
    check('afmeld: en ukendt nøgle ændrer ingenting','virker ikke længere' in K2.inner_text('#unsubBox') and M.prefs[uid1].get('my_beer') is True,K2.inner_text('#unsubBox'))
    K2.goto(URL+'#afmeld-'+tok); K2.wait_for_timeout(700); still=M.prefs[uid1].get('my_beer') is True
    K2.click('#unsubGo'); K2.wait_for_timeout(900); pr=M.prefs[uid1]
    check('afmeld: intet sker, før man trykker, og så er alle mails slået fra',still and 'Du er afmeldt' in K2.inner_text('#unsubBox') and not any(pr.get(k) for k in('news','my_beer','friends','events')),(still,K2.inner_text('#unsubBox'),pr))
    K2.goto(URL+'#profil'); K2.wait_for_timeout(1800)
    check('afmeld: fluebenene på profilen er væk bagefter',K2.query_selector('#mp_my_beer') is not None and not K2.is_checked('#mp_my_beer') and not K2.is_checked('#mp_friends'))
    K2.click('#acOut'); K2.wait_for_timeout(3000); se3=sb(K2)
    K2.goto(URL+'#beer-uk1'); K2.wait_for_timeout(900)
    check('konto: log ud giver en ny anonym bruger, som ikke kan rette kontoens øl',se3['user']['id']!=uid1 and not se3['user'].get('email') and K2.query_selector('#editBeer') is None,se3['user'])
    M.mail_limit=True; K2.goto(URL+'#profil'); K2.wait_for_timeout(900); K2.fill('#acMail','ny@example.dk'); K2.click('#acctForm button'); K2.wait_for_timeout(1000)
    check('konto: for mange mails giver en forståelig besked','for mange mails' in K2.inner_text('#toast') and K2.query_selector('#acCode') is None,K2.inner_text('#toast')); M.mail_limit=False
    # kun denne bruger oplever en database uden tilføjelsen. Ellers får de andre åbne enheder 404-fejl, mens de synkroniserer
    M.no_konto.add(uid1); K1.goto(URL+'#profil'); K1.reload(); K1.wait_for_timeout(2500)
    check('konto: mangler databasen tilføjelsen, står der at mails ikke er slået til','ikke slået til' in K1.inner_text('#acctBox') and K1.query_selector('#mp_news') is None,K1.inner_text('#acctBox')[:120]); M.no_konto.clear()
    K1.reload(); K1.wait_for_timeout(2500); K1.click('#acDel'); K1.wait_for_timeout(3000)
    check('konto: slet konto fjerner login, mailvalg og det, der lå på kontoen','lucas@example.dk' not in M.emails and uid1 not in M.prefs and uid1 not in M.kdata and K1.query_selector('#acMail') is not None and not sb(K1)['user'].get('email'),list(M.emails))
    # --- enig eller uenig (swipe): stemmer på andres bedømmelser, tal hos den der har bedømt
    M2=Mock(); errs2=[]
    def ctx2(state):
        c=b.new_context(viewport={'width':390,'height':844},locale='da-DK',service_workers='block'); c.route(f'https://{HOST}/**',M2.handle); pg=c.new_page(); pg.on('pageerror',lambda e:None if WK_NOISE(str(e)) else errs2.append(str(e)))
        pg.add_init_script("if(!localStorage.getItem('olrating-v1'))localStorage.setItem('olrating-v1',%s);"%json.dumps(json.dumps(state))); return pg
    mk=lambda who,beers,revs:{"beers":[{"id":i,"name":n,"brewery":"Testbryg","style":"Pilsner","abv":5,"size":"33 cl flaske","date":"2026-11-20","addedBy":who,"img":""} for i,n in beers],"reviews":[{"id":i,"beer":bb,"who":who,"date":d,"s":C,"text":t} for i,bb,d,t in revs],"me":who}
    W1=ctx2(mk('Lucas',[('us1','Swipeøl et'),('us2','Swipeøl to')],[('rs1','us1','2026-11-20','Rigtig god'),('rs2','us2','2026-11-21','')])); W1.goto(URL+'#swipe'); W1.wait_for_timeout(3500)
    check('swipe: egne bedømmelser er ikke med',W1.query_selector('#swc') is None and 'ingen bedømmelser' in W1.inner_text('#app'),W1.inner_text('#app')[:120])
    W2=ctx2(mk('Magnus',[],[])); W2.goto(URL+'#swipe'); W2.wait_for_timeout(3500); u2=sb(W2)['user']['id']
    t=W2.inner_text('#swc')
    check('swipe: kort med øl, smager og karakter','Swipeøl to' in t and 'Lucas' in t and 'gav den' in t and '4,4' in t and '2 tilbage' in W2.inner_text('#app') and not W2.evaluate('document.documentElement.scrollWidth>innerWidth+1'),t[:120])
    W2.click('#swYes'); W2.wait_for_timeout(2500)
    check('swipe: Enig bliver gemt i databasen, og næste kort kommer',M2.rvotes.get(('rs2',u2))==1 and 'Swipeøl et' in W2.inner_text('#swc'),dict(M2.rvotes))
    bx=W2.eval_on_selector('#swc','e=>{const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+120]}')
    W2.mouse.move(bx[0],bx[1]); W2.mouse.down(); W2.mouse.move(bx[0]-60,bx[1]+4,steps=4); stamp=W2.evaluate("getComputedStyle(document.querySelector('#swc .stamp.n')).opacity"); W2.mouse.move(bx[0]-170,bx[1]+8,steps=6); W2.mouse.up(); W2.wait_for_timeout(2500)
    check('swipe: træk til venstre giver Uenig, og stemplet vises undervejs',M2.rvotes.get(('rs1',u2))==-1 and float(stamp)>0.5 and 'alle igennem' in W2.inner_text('#app') and 'enig i 1 af 2' in W2.inner_text('#app'),(dict(M2.rvotes),stamp,W2.inner_text('#app')[:160]))
    W2.click('#swUndo'); W2.wait_for_timeout(2500)
    check('swipe: Fortryd fjerner stemmen igen',('rs1',u2) not in M2.rvotes and W2.query_selector('#swc') is not None,dict(M2.rvotes))
    W2.keyboard.press('ArrowRight'); W2.wait_for_timeout(2500)
    check('swipe: piletasterne virker',M2.rvotes.get(('rs1',u2))==1)
    W1.evaluate("sbSync()"); W1.wait_for_timeout(1500); dot=W1.evaluate("document.getElementById('menuBtn').classList.contains('nyt')&&document.querySelector('[data-nav=profil]').classList.contains('nyt')&&getComputedStyle(document.querySelector('[data-nav=profil]')).position==='static'")
    W1.goto(URL+'#profil'); W1.wait_for_timeout(900); rb=W1.inner_text('#rvBox'); dot2=W1.evaluate("document.getElementById('menuBtn').classList.contains('nyt')")
    check('swipe: nye stemmer giver en prik på Min profil, og profilen viser hvor mange og hvilken øl',dot and not dot2 and '+2 nye stemmer siden sidst' in rb and 'Flest enige: Swipeøl' in rb and 'Flest uenige' not in rb and W1.query_selector('#rvBox a[href^="#beer-us"]') is not None,(dot,dot2,rb))
    W1.goto(URL+'#alle'); W1.wait_for_timeout(400); W1.goto(URL+'#profil'); W1.wait_for_timeout(700)
    check('swipe: næste gang er de ikke nye længere','siden sidst' not in W1.inner_text('#rvBox') and 'Flest enige' in W1.inner_text('#rvBox'),W1.inner_text('#rvBox'))
    W1.goto(URL+'#beer-us1'); W1.wait_for_timeout(900)
    check('swipe: den, der har bedømt, ser hvor mange der er enige','100 %' in rb and '2 enige' in rb and '0 uenige' in rb and '👍 1 enig' in W1.inner_text('.rv'),(rb[:120],W1.inner_text('.rv')[:120]))
    M2.has_konto_sql=False; M2.has_besoeg=False; W3=ctx2(mk('Sofie',[],[])); W3.goto(URL+'#swipe'); W3.wait_for_timeout(3500); W3.click('#swNo'); W3.wait_for_timeout(1500); s3=ls(W3)
    check('swipe: uden tabellen i databasen gemmes stemmen på enheden og venter',len(s3['rv'])==1 and len(s3['rvq'])==1 and not [k for k in M2.rvotes if k[1] not in (u2,)],s3.get('rvq'))
    W3.goto(URL+'#om'); W3.wait_for_timeout(500); v0=M2.visits
    check('besøg: uden tælleren i databasen viser Om kun øl, bedømmelser og smagere',W3.eval_on_selector_all('#omTal .ex-t','e=>e.length')==3 and 'besøg' not in W3.inner_text('#omTal'),W3.inner_text('#omTal'))
    n404=M2.visit_calls; W3.reload(); W3.wait_for_timeout(2500)
    check('besøg: uden tælleren prøves der ikke igen ved næste åbning (ingen 404 hver gang)',M2.visit_calls==n404 and W3.evaluate("+localStorage.getItem('olrating-vis404')>0"),(n404,M2.visit_calls))
    W3.evaluate("localStorage.setItem('olrating-vis404',Date.now()-36e5-1000)")   # en time senere
    M2.has_besoeg=True; M2.has_konto_sql=True; W3.reload(); W3.wait_for_timeout(3500)
    check('besøg: når tælleren findes, tælles åbningen, og Om viser tallet, men et sideskift tæller ikke',M2.visits==v0+1 and W3.eval_on_selector_all('#omTal .ex-t','e=>e.length')==5 and f'{M2.visits:,}'.replace(',','.') in W3.inner_text('#omTal'),(v0,M2.visits,W3.inner_text('#omTal')))
    W3.goto(URL+'#swipe'); W3.wait_for_timeout(400); W3.goto(URL+'#om'); W3.wait_for_timeout(400)
    check('besøg: at skifte side tæller ikke som et nyt besøg',M2.visits==v0+1,(v0,M2.visits))
    check('swipe: stemmen sendes, når tabellen findes',len(M2.rvotes)==3 and not ls(W3)['rvq'] and not errs2,(dict(M2.rvotes),errs2[:2]))
    # --- data må ikke forsvinde eller sidde fast: et billede, der afvises, en række, der afvises, og mange øl i databasen
    M3=Mock(); errs3=[]
    def ctx3(state,MM):
        c=b.new_context(viewport={'width':390,'height':844},locale='da-DK',service_workers='block'); c.route(f'https://{HOST}/**',MM.handle); pg=c.new_page()
        pg.on('pageerror',lambda e:None if WK_NOISE(str(e)) else errs3.append(str(e)))
        pg.add_init_script("if(!localStorage.getItem('olrating-v1'))localStorage.setItem('olrating-v1',%s);"%json.dumps(json.dumps(state))); return pg
    ob=lambda i,n,img='':{"id":i,"name":n,"brewery":"Testbryg","style":"Pilsner","abv":5,"size":"33 cl flaske","date":"2026-11-20","addedBy":"Lucas","img":img}
    st3={"beers":[ob('ui1','Billedøl',DATA),ob('ui2','Uden billede')],"reviews":[{"id":"ri2","beer":"ui2","who":"Lucas","date":"2026-11-21","s":C,"text":"Fin"}],"me":"Lucas"}
    M3.img_fail=413; D1=ctx3(st3,M3); D1.goto(URL+'#profil'); D1.wait_for_timeout(3500)
    check('data: et billede, databasen afviser, stopper ikke delingen af resten','ui2' in M3.t['beers'] and 'ri2' in M3.t['reviews'] and 'ui1' not in M3.t['beers'],(list(M3.t['beers']),list(M3.t['reviews'])))
    l3=ls(D1); b1=[x for x in l3['beers'] if x['id']=='ui1']
    check('data: øllen med billedet bliver på enheden, billede og det hele',b1 and b1[0]['img'].startswith(('data:image/','idb:')),[(x['id'],x['img'][:20]) for x in l3['beers']])
    st=D1.inner_text('.sbst')
    check('data: Min profil siger, at noget ikke er delt endnu',st.startswith('● Forbundet') and '1 af dine øl eller bedømmelser' in st,st)
    D1.goto(URL+'#beer-ui1'); D1.wait_for_timeout(800); n1=D1.query_selector('#notShared')
    D1.goto(URL+'#beer-ui2'); D1.wait_for_timeout(800); n2=D1.query_selector('#notShared')
    check('data: en øl, der kun er på enheden, siger det på sin side (og en delt øl gør ikke)',n1 is not None and 'kun på denne enhed' in n1.inner_text() and n2 is None,(n1 and n1.inner_text(),n2))
    M3.img_fail=0; D1.reload(); D1.wait_for_timeout(3500)
    check('data: næste gang siden åbnes, deles øllen med billedet',M3.t['beers'].get('ui1',{}).get('img','').startswith('https://') and len(M3.store)==1,M3.t['beers'].get('ui1'))
    D1.goto(URL+'#profil'); D1.wait_for_timeout(1200)
    check('data: bagefter står der ikke længere, at noget venter','af dine øl' not in D1.inner_text('.sbst'),D1.inner_text('.sbst'))
    M3.row_fail['ux1']=403; M3.row_fail['ux2']=400   # 400: som når grænsen mod spam (supabase/006) er nået
    mut(D1,"S.beers.unshift({id:'ux1',name:'Afvist øl',brewery:'Testbryg',style:'Pilsner',abv:5,size:'33 cl flaske',date:'2026-11-22',addedBy:'Lucas',img:''},{id:'ux2',name:'For mange øl',brewery:'Testbryg',style:'Pilsner',abv:5,size:'33 cl flaske',date:'2026-11-22',addedBy:'Lucas',img:''})",3000)
    for _ in range(2): D1.evaluate("sbSync()"); D1.wait_for_timeout(1500)
    lid=[x['id'] for x in ls(D1)['beers']]
    check('data: nye øl, som databasen afviser (403 og 400), forsvinder ikke fra enheden','ux1' in lid and 'ux2' in lid and 'ux1' not in M3.t['beers'] and 'ux2' not in M3.t['beers'],lid)
    M3.row_fail.clear(); D1.reload(); D1.wait_for_timeout(3500)
    check('data: og de deles, når databasen tager imod dem igen','ux1' in M3.t['beers'] and 'ux2' in M3.t['beers'],list(M3.t['beers']))
    # login: fornyes sessionen, mens Supabase har en midlertidig fejl (503), må enheden ikke få en ny bruger. Så kunne man ikke længere rette sine egne øl
    uid0=sb(D1)['user']['id']; nu0=len(M3.users)
    D1.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('olrating-sb'));s.expires_at=1;localStorage.setItem('olrating-sb',JSON.stringify(s))})()")
    M3.auth_fail=503; D1.reload(); D1.wait_for_timeout(3000); same=sb(D1)['user']['id']==uid0 and len(M3.users)==nu0
    M3.auth_fail=0; D1.evaluate("sbSync()"); D1.wait_for_timeout(1500); D1.goto(URL+'#beer-ui2'); D1.wait_for_timeout(800)
    check('login: en midlertidig fejl hos Supabase giver ikke en ny bruger, og egne øl kan stadig rettes',same and sb(D1)['user']['id']==uid0 and len(M3.users)==nu0 and D1.query_selector('#editBeer') is not None,(same,sb(D1)['user']['id'],uid0,len(M3.users),nu0))
    # login udløbet hos Supabase, før enheden tror det (fx fordi telefonens ur går forkert): svar 401 skal give et nyt login med det samme
    uid1=sb(D1)['user']['id']; M3.tok.pop(sb(D1)['access_token'],None)
    mut(D1,"S.beers.unshift({id:'u401',name:'Efter 401',brewery:'Testbryg',style:'Pilsner',abv:5,size:'33 cl flaske',date:'2026-11-23',addedBy:'Lucas',img:''})",500)
    for _ in range(14):
        if 'u401' in M3.t['beers']: break
        D1.wait_for_timeout(500)
    check('login: svarer Supabase 401, fornyes login med det samme, og øllen deles (samme bruger)','u401' in M3.t['beers'] and sb(D1)['user']['id']==uid1,(list(M3.t['beers']),sb(D1)['user']['id']==uid1))
    # to faner og login: et refresh-token kan kun bruges én gang. Har den ene fane fornyet login, må den anden ikke prøve med det gamle og få en ny bruger
    M6=Mock(); M6.exp=75; M6.rotate=True   # login gælder 75 sekunder; siden fornyer, når der er under 60 tilbage
    c6=b.new_context(viewport={'width':390,'height':844},locale='da-DK',service_workers='block'); c6.route(f'https://{HOST}/**',M6.handle)
    c6.add_init_script("if(!localStorage.getItem('olrating-v1'))localStorage.setItem('olrating-v1',%s);"%json.dumps(json.dumps({"beers":[ob('ut1','Faneøl')],"reviews":[],"me":"Lucas"})))
    F1=c6.new_page(); F1.on('pageerror',lambda e:errs3.append('F1: '+str(e))); F1.goto(URL); F1.wait_for_timeout(3000); u6=sb(F1)['user']['id']
    F2=c6.new_page(); F2.on('pageerror',lambda e:errs3.append('F2: '+str(e))); F2.goto(URL+'#beer-ut1'); F2.wait_for_timeout(2500)
    F1.wait_for_timeout(16000); F1.evaluate("sbSync()"); F1.wait_for_timeout(1500)   # fane 1 fornyer login. Det gamle refresh-token virker ikke længere
    F2.evaluate("sbSync()"); F2.wait_for_timeout(1500); F2.reload(); F2.wait_for_timeout(2000)   # fane 2 har stadig det gamle i hukommelsen
    check('to faner: når den ene fane har fornyet login, får den anden ikke en ny bruger',sb(F2)['user']['id']==u6 and len(M6.users)==1 and F2.query_selector('#editBeer') is not None,(u6,sb(F2)['user']['id'],len(M6.users)))
    c6.close()
    # langsomt net: en bedømmelse, der gemmes, mens en synkronisering venter på svar, skal ikke vente 30 sekunder på næste runde
    D1.goto(URL+'#beer-ui2'); D1.wait_for_timeout(1500); nr=len(M3.t['reviews'])
    D1.evaluate("""(()=>{const of=window.fetch;window.fetch=(u,o)=>String(u).includes('/rest/v1/beers?select')&&!window.__slow?(window.__slow=1,new Promise(r=>setTimeout(r,4000)).then(()=>of(u,o))):of(u,o);sbSync()})()""")
    for k in ['look','aroma','taste','feel','overall']: D1.click(f'#revForm .rate[data-k="{k}"] [data-star="4"]')
    D1.fill('#rText','Gemt på langsomt net'); D1.click('#revForm button[type=submit]')
    for _ in range(18):
        if len(M3.t['reviews'])>nr: break
        D1.wait_for_timeout(500)
    check('langsomt net: en bedømmelse, der gemmes midt i en synkronisering, deles lige efter',len(M3.t['reviews'])>nr and D1.evaluate('window.__slow')==1,(nr,len(M3.t['reviews'])))
    # mange øl: Supabase giver højst 1000 rækker pr. svar. Egne øl længere nede må ikke forsvinde fra enheden
    M4=Mock(); D2=ctx3({"beers":[ob('um1','Min gamle øl')],"reviews":[{"id":"rm9","beer":"um1","who":"Lucas","date":"2026-11-20","s":C,"text":""}],"me":"Lucas"},M4); D2.goto(URL); D2.wait_for_timeout(3000)
    for i in range(1150):
        M4.t['beers'][f'mb{i}']={'id':f'mb{i}','owner':'anden','created_at':f'9{i:06d}','name':f'Mængdeøl {i}','brewery':'Storbryg','img':None,'data':{'style':'Lager','abv':4.6,'date':'2026-11-20','addedBy':'Sofie'}}
        M4.t['reviews'][f'mr{i}']={'id':f'mr{i}','beer':f'mb{i}','owner':'anden','created_at':f'9{i:06d}','who':'Sofie','img':None,'data':{'s':C,'date':'2026-11-21','text':''}}
    D2.evaluate("sbSync()"); D2.wait_for_timeout(4000); l4=ls(D2)
    check('mange øl: alle 1151 øl og bedømmelser hentes, også over 1000',len(l4['beers'])==1151 and len(l4['reviews'])==1151,(len(l4['beers']),len(l4['reviews'])))
    check('mange øl: min egen øl længst nede er der stadig',any(x['id']=='um1' for x in l4['beers']) and any(x['id']=='rm9' for x in l4['reviews']))
    M4.endless='beers'; n0=len(M4.log); D2.evaluate("sbSync()"); D2.wait_for_timeout(5000); l5=ls(D2); pages=len([x for x in M4.log[n0:] if x.startswith('GET /rest/v1/beers')]); M4.endless=''
    check('mange øl: slutter listen aldrig (spam), stopper siden efter 20 sider og fjerner ikke egne øl',pages==20 and any(x['id']=='um1' for x in l5['beers']),(pages,len(l5['beers'])))
    t0=D2.evaluate("performance.now()"); D2.goto(URL+'#alle'); D2.wait_for_selector('#grid .card'); ms=D2.evaluate("performance.now()")
    D2.fill('#q','Mængdeøl 114'); D2.wait_for_timeout(500); nq=D2.eval_on_selector_all('#grid .card[href^="#beer-"]','e=>e.map(x=>x.getAttribute("href"))')
    check('mange øl: Alle øl kan vises og søges i',sorted(nq)==sorted(['#beer-mb114','#beer-mb1114']+[f'#beer-mb{i}' for i in range(1140,1150)]),(nq,round(ms-t0)))
    # datoer: dansk tid med sommertid. Et døgn kan have 23 eller 25 timer, og det må ikke give en dag for meget
    from datetime import datetime
    from zoneinfo import ZoneInfo
    def at(state,when):
        c=b.new_context(viewport={'width':390,'height':844},locale='da-DK',timezone_id='Europe/Copenhagen',service_workers='block'); c.route(f'https://{HOST}/**',Mock().handle); pg=c.new_page()
        pg.on('pageerror',lambda e:None if WK_NOISE(str(e)) else errs3.append(when+': '+str(e)))
        pg.clock.set_fixed_time(datetime.fromisoformat(when).replace(tzinfo=ZoneInfo('Europe/Copenhagen')))
        pg.add_init_script("if(!localStorage.getItem('olrating-v1'))localStorage.setItem('olrating-v1',%s);"%json.dumps(json.dumps(state))); return pg
    big=lambda pg:pg.eval_on_selector_all('.next .big','e=>e.map(x=>x.textContent)')
    P=at({"beers":[],"reviews":[],"me":"Lucas"},'2026-10-20T12:00'); P.goto(URL+'#kalender'); P.wait_for_timeout(800); k1=big(P); P.context.close()
    check('datoer: nedtælling hen over sommertidens slut (J-dag om 17 dage, nytårsaften om 72)',k1[:1]==['17 dage'] and '72 dage' in k1,k1)
    P=at({"beers":[],"reviews":[],"me":"Lucas"},'2026-11-05T09:00'); P.goto(URL+'#kalender'); P.wait_for_timeout(800); k2=big(P); P.context.close()
    check('datoer: dagen før J-dag står der "I morgen" (ikke "1 dage")',k2[:1]==['I morgen'],k2)
    sd={"beers":[ob('ud1','Dato-øl')],"reviews":[{"id":"rd1","beer":"ud1","who":"Lucas","date":"2026-10-24","s":C,"text":""}],"me":"Lucas",
        "tours":[{"id":"td1","name":"Fredagstur","date":"2026-11-28T19:30","meet":"Torvet","note":"","host":"Lucas","stops":[],"members":[{"name":"Lucas"}]}]}
    P=at(sd,'2026-10-25T23:30'); P.goto(URL+'#beer-ud1'); P.wait_for_timeout(800); a1=' '.join(P.eval_on_selector_all('.rv','e=>e.map(x=>x.innerText)')); P.context.close()
    check('datoer: en bedømmelse fra i går hedder "i går", også natten efter sommertidens slut','i går' in a1 and '2 dage' not in a1,a1[:200])
    P=at(sd,'2026-11-27T18:00'); P.goto(URL+'#byttur-td1'); P.wait_for_timeout(800); t1=P.inner_text('.thead .meta'); P.context.close()
    check('datoer: en byttur i morgen aften står som "i morgen" (ikke "om 2 dage")','i morgen' in t1 and 'om 2 dage' not in t1,t1)
    P=at(sd,'2026-11-28T00:30'); P.goto(URL+'#beer-ud1'); P.wait_for_timeout(800)
    for k in ['look','aroma','taste','feel','overall']: P.click(f'#revForm .rate[data-k="{k}"] [data-star="4"]')
    P.click('#revForm button[type=submit]'); P.wait_for_timeout(1200); nd=[r['date'] for r in ls(P)['reviews'] if r['id']!='rd1']; P.goto(URL); P.wait_for_timeout(600); home=P.inner_text('#app'); P.context.close()
    check('datoer: en bedømmelse kl. 00.30 får dagens dato (ikke gårsdagens, som i UTC), og forsiden tæller den med i dag',nd==['2026-11-28'] and '1 ny bedømmelse i dag' in home,(nd,[l for l in home.split('\n') if 'i dag' in l][:3]))
    st_dst={"beers":[],"reviews":[],"me":"Lucas","tours":[{"id":"tdst","name":"Natten med en time ekstra","date":"2026-10-24T22:00","meet":"","note":"","host":"Lucas","stops":[{"name":"Bar A","time":"22:00","addr":""},{"name":"Bar B","time":"01:00","addr":""},{"name":"Bar C","time":"03:30","addr":""}],"members":[{"name":"Lucas"}]}]}
    P=at(st_dst,'2026-10-25T03:10'); P.goto(URL+'#byttur-tdst'); P.wait_for_timeout(800); cur=P.inner_text('.route li.cur') if P.query_selector('.route li.cur') else ''; P.context.close()
    check('datoer: byttur natten, hvor sommertiden slutter: kl. 03.10 er man ved stoppet kl. 01.00, ikke ved det kl. 03.30',('Bar B' in cur),cur)
    badd=[]
    for when in ['2027-01-01T00:30','2028-02-29T12:00','2026-03-29T02:30','2026-10-25T02:30','2026-12-31T23:59']:   # nytår, skuddag, timen der ikke findes, timen der findes to gange, årets sidste minut
        P=at(sd,when)
        for h in ['','#aarets','#kalender','#toplisten','#profil','#dagbog','#beer-ud1','#byttur','#byttur-td1','#genstande']:
            P.goto(URL+h); P.wait_for_timeout(250)
            if len(P.inner_text('#app'))<30: badd.append(when+h)
        P.context.close()
    check('datoer: alle sider virker nytårsnat, på skuddagen og når sommertiden skifter',not badd,badd)
    # gamle data: sådan så det gemte ud i den allerførste udgave (6172cd8). Felter, der er kommet til siden, mangler
    old={"beers":[{"id":"b1","code":"","name":"Gammel Classic","brewery":"Gammelt Bryg","city":"Aalborg","style":"Pilsner","abv":4.6,"price":0,"place":"","size":"33 cl flaske","desc":"","img":"","addedBy":"Lucas","date":"2026-11-01"},
                    {"id":"b2","name":"Uden felter","brewery":"","style":"IPA","abv":0,"addedBy":"Lucas","date":"2026-11-02"}],
         "reviews":[{"who":"Lucas","s":{"look":4,"aroma":3,"taste":4,"feel":3,"overall":4},"prof":None,"tags":["Frisk"],"again":1,"text":"Fin","date":"2026-11-01","id":"r1","beer":"b1"},
                    {"who":"Lucas","s":{"look":5,"aroma":5,"taste":5,"feel":5,"overall":5},"prof":{"sweet":2,"bitter":3,"sour":1,"body":3,"roast":4},"tags":[],"again":0,"text":"","date":"2026-11-02","id":"r2","beer":"b2"}],
         "me":"Lucas","hideEx":True,"season":"auto","wish":["b2"],"mode":"auto"}
    M5=Mock(); O=ctx3(old,M5); O.goto(URL); O.wait_for_timeout(3500); badp=[]
    for h in ['','#alle','#beer-b1','#beer-b2','#toplisten','#aarets','#galleri','#stilguide','#venner','#smager-Lucas','#bryggeri-Gammelt%20Bryg','#byttur','#smagning','#profil','#dagbog','#sammenlign','#indstillinger','#om','#kalender','#swipe','#genstande','#hjul','#mad','#buddies','#tilfoej']:
        O.goto(URL+h); O.wait_for_timeout(400)
        if len(O.inner_text('#app'))<30: badp.append(h)
    check('gamle data: alle sider virker med data fra den første udgave, og de bliver delt',not badp and sorted(M5.t['beers'])==['b1','b2'] and sorted(M5.t['reviews'])==['r1','r2'],(badp,list(M5.t['beers']),list(M5.t['reviews'])))
    check('data: ingen fejl i siden',not errs3,errs3[:3])
    # to faner på samme enhed: begge ændringer skal overleve
    c2=b.new_context(viewport={'width':390,'height':844},locale='da-DK',service_workers='block'); c2.route(f'https://{HOST}/**',Mock().handle)
    T1=c2.new_page(); T1.goto(URL+'#profil'); T1.wait_for_timeout(2500); T2=c2.new_page(); T2.goto(URL+'#indstillinger'); T2.wait_for_timeout(2500)
    T2.click('[data-look="bg:fjord"]'); T2.wait_for_timeout(500)
    T1.goto(URL+'#indstillinger'); T1.wait_for_timeout(500); bg1=T1.evaluate("document.documentElement.dataset.bg"); T1.click('[data-look="acc:guld"]'); T1.wait_for_timeout(600)
    st=json.loads(T1.evaluate("localStorage.getItem('olrating-v1')"))
    check('to faner: den ene fanes valg bliver ikke slettet af den anden',bg1=='fjord' and st.get('look')=={'bg':'fjord','acc':'guld'} and T2.evaluate("document.documentElement.dataset.acc")=='guld',(bg1,st.get('look')))
    c2.close()
    check('no JS errors',not errs,errs[:5])
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
