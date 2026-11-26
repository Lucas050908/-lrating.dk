"""Prøver siden mod den RIGTIGE database (køres i GitHub Actions, ikke lokalt).
Opretter en test-øl, en test-bedømmelse, en test-tur og en test-smagning med tydelige TEST-navne og sletter dem igen til sidst.
Startes ved at skrive [database-test] i en commit-besked, der ændrer noget i tests/ eller på siden."""
import json,os,sys,time,urllib.request,urllib.error,datetime
from playwright.sync_api import sync_playwright
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mock_supabase import JPG
import base64
URL=os.environ.get('SITE','http://localhost:8811/')
SB='https://bbcegrufmzgfgzxazldr.supabase.co'; KEY='sb_publishable_mf5v3jp_xYx7wJj1lgCr-Q_JUFuzXOY'
RID=format(int(time.time()),'x'); BID='utest'+RID; R1='rtest'+RID; R2='rtestb'+RID; NAME='TEST '+RID+' slettes automatisk'
DATA='data:image/jpeg;base64,'+base64.b64encode(JPG).decode()
R={}
def ok(k,v,info=''):
    R[k]=bool(v); print(('PASS ' if v else 'FAIL ')+k,'' if v else str(info)[:300],flush=True)
def api(path,method='GET',token=None,body=None,raw=False):
    h={'apikey':KEY}
    if token: h['Authorization']='Bearer '+token
    data=None
    if body is not None: data=json.dumps(body).encode(); h['Content-Type']='application/json'
    try:
        with urllib.request.urlopen(urllib.request.Request(SB+path,method=method,headers=h,data=data),timeout=25) as r:
            t=r.read(); return r.status,(t if raw else (json.loads(t) if t else None))
    except urllib.error.HTTPError as e: return e.code,e.read().decode(errors='replace')[:300]
    except Exception as e: return 0,str(e)
def wait(fn,sec=35):
    t=time.time(); v=None
    while time.time()-t<sec:
        v=fn()
        if v: return v
        time.sleep(1.5)
    return v
row=lambda tb,q: (lambda c,d: d if c==200 and isinstance(d,list) else [])(*api(f'/rest/v1/{tb}?{q}&select=*'))
sess=lambda pg: json.loads(pg.evaluate("localStorage.getItem('olrating-sb')") or 'null')
ls=lambda pg: json.loads(pg.evaluate("localStorage.getItem('olrating-v1')"))
C={"look":4,"aroma":4,"taste":5,"feel":4,"overall":5}
stA={"beers":[{"id":BID,"name":NAME,"brewery":"TEST","style":"Pilsner","abv":5,"size":"33 cl flaske","date":time.strftime('%Y-%m-%d'),"addedBy":"TestA","img":DATA}],
     "reviews":[{"id":R1,"beer":BID,"who":"TestA","date":time.strftime('%Y-%m-%d'),"s":C,"text":"Automatisk test"}],"me":"TestA"}
tokA=tokB=None; tid=None; sid=None; img=None; errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    def ctx(name,state=None):
        c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
        pg.on('pageerror',lambda e:errs.append(name+': '+str(e)))
        pg.on('console',lambda m:errs.append(name+' console: '+m.text[:200]) if m.type in('error','warning') else None)
        init="window.confirm=()=>true;window.prompt=()=>'%s';navigator.share=async()=>{};"%name
        if state: init+="if(!localStorage.getItem('olrating-v1'))localStorage.setItem('olrating-v1',%s);"%json.dumps(json.dumps(state))
        pg.add_init_script(init); return pg
    try:
        A=ctx('TestA',stA); A.goto(URL)
        sA=wait(lambda: sess(A),20); tokA=sA and sA.get('access_token'); uidA=sA and sA['user']['id']
        ok('1 anonymt login virker',tokA and sA['user'].get('is_anonymous'),sA)
        r=wait(lambda: row('beers','id=eq.'+BID)); ok('2 øl gemmes i databasen',r and r[0]['owner']==uidA and r[0]['name']==NAME,r)
        rr=wait(lambda: row('reviews','id=eq.'+R1),15); ok('3 bedømmelse gemmes',rr and rr[0]['who']=='TestA',rr)
        img=(r and r[0].get('img')) or ''; ok('4 billede uploades',img.startswith(SB+'/storage/v1/object/public/billeder/'+str(uidA)+'/'),img)
        c,d=api(img[len(SB):],raw=True) if img else (0,''); ok('5 billedet kan ses af alle',c==200 and len(d)>100,(c,str(d)[:80]))
        c,d=api('/rest/v1/beers',method='POST',body={'id':'uhack'+RID,'name':'HACK','data':{}}); ok('6 uden login kan man ikke oprette',c in(401,403),(c,d))
        Bp=ctx('TestB'); Bp.goto(URL+'#alle'); Bp.wait_for_selector('#q')
        def seen():
            Bp.fill('#q',RID); Bp.wait_for_timeout(400); return Bp.eval_on_selector_all('#grid .card','e=>e.length')==1
        ok('7 en anden enhed ser øllen',wait(seen,45))
        ok('8 billedet vises hos den anden',Bp.evaluate("(()=>{const i=document.querySelector('#grid .card img');return !!i&&i.src.includes('/storage/')&&i.naturalWidth>0})()"))
        sB=sess(Bp); tokB=sB and sB.get('access_token')
        c1,d1=api('/rest/v1/beers?id=eq.'+BID,method='PATCH',token=tokB,body={'name':'HACKET'}); c2,d2=api('/rest/v1/beers?id=eq.'+BID,method='DELETE',token=tokB)
        r=row('beers','id=eq.'+BID); ok('9 andre kan ikke rette eller slette øllen',r and r[0]['name']==NAME,(c1,d1,c2,d2,r))
        Bp.evaluate("(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1'));S.me='TestB';S.reviews.push({id:'%s',beer:'%s',who:'TestB',date:'%s',s:{look:3,aroma:3,taste:4,feel:3,overall:4},text:'Automatisk test B'});localStorage.setItem('olrating-v1',JSON.stringify(S))})()"%(R2,BID,time.strftime('%Y-%m-%d')))
        Bp.reload(); ok('10 den anden enheds bedømmelse gemmes',wait(lambda: row('reviews','id=eq.'+R2)))
        A.reload(); ok('11 første enhed henter den',wait(lambda: any(x['id']==R2 for x in ls(A)['reviews']),45))
        # enig/uenig – kun når supabase/003 er kørt i databasen
        c,d=api('/rest/v1/review_vote_counts?select=review&limit=1')
        if c==200:
            c1,d1=api('/rest/v1/review_votes',method='POST',token=tokB,body={'review':R1,'v':1}); c2,d2=api('/rest/v1/review_votes',method='POST',token=tokA,body={'review':R1,'v':1})
            c3,d3=api('/rest/v1/review_vote_counts?select=review,enig,uenig&review=eq.'+R1)
            ok('11b enig-stemme gemmes, og man kan ikke stemme på sin egen bedømmelse',c1 in(200,201) and c2 in(401,403) and c3==200 and d3 and d3[0]['enig']==1 and d3[0]['uenig']==0,(c1,d1,c2,d2,c3,d3))
            c4,d4=api('/rest/v1/review_votes?select=review&review=eq.'+R1,token=tokA); ok('11c man kan ikke se, hvem der har stemt',c4==200 and d4==[],(c4,d4))
        else: print('SPRING OVER enig/uenig: supabase/003-konto-mails-enig.sql er ikke kørt i databasen endnu (svar %s)'%c,flush=True)
        # byttur
        A.goto(URL+'#byttur'); A.wait_for_selector('#tName'); A.fill('#tName','TEST tur '+RID); A.fill('#tDate',(datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%dT20:00')); A.fill('#tMeet','Test'); A.click('#tourForm button')
        A.wait_for_selector('#stopForm'); tid=A.evaluate('location.hash')[8:]; A.fill('#sName','TEST bar'); A.fill('#sTime','20:15'); A.click('#stopForm button')
        t=wait(lambda: row('tours','id=eq.'+tid)); ok('12 byttur gemmes',t and len(t[0]['data'].get('stops',[]))==1,t)
        Bp.goto(URL+'#byttur'); Bp.wait_for_selector('#tCode'); Bp.fill('#tCode',tid); Bp.click('#codeForm button'); Bp.wait_for_selector('#tourJoin',timeout=20000); Bp.click('#tourJoin')
        ok('13 tilmelding til byttur gemmes',wait(lambda: row('tour_members','tour=eq.'+tid+'&name=eq.TestB')))
        A.reload(); ok('14 værten ser den tilmeldte',wait(lambda: any(m['name']=='TestB' for t in ls(A)['tours'] for m in t['members']),45))
        # smagning med venner
        A.goto(URL+'#smagning'); A.wait_for_selector('#sgName'); A.fill('#sgName','TEST smagning '+RID); A.fill('#sgBeers','TEST A\nTEST B'); A.click('#tastForm button')
        A.wait_for_selector('#voteForm'); sid=A.evaluate('location.hash')[10:]
        ok('14b smagning gemmes',wait(lambda: row('tastings','id=eq.'+sid)))
        Bp.goto(URL+'#smagning-'+sid); Bp.wait_for_selector('#voteForm',timeout=30000)
        for i,v in enumerate([5,2]): Bp.click(f'#voteForm .rate[data-k="t{i}"] [data-star="{v}"]')
        Bp.click('#voteForm button.btn')
        v=wait(lambda: row('tasting_votes','tasting=eq.'+sid+'&who=eq.TestB')); ok('14c stemme fra den anden enhed gemmes',v and v[0]['data'].get('v')==[5,2],v)
        A.click('#tastDel'); ok('14d slettet smagning forsvinder med stemmer',wait(lambda: not row('tastings','id=eq.'+sid),30) and not row('tasting_votes','tasting=eq.'+sid))
        # sletning
        A.goto(URL+'#beer-'+BID); A.wait_for_selector('#delBeer',timeout=20000); A.click('#delBeer')
        ok('15 slettet øl forsvinder fra databasen',wait(lambda: not row('beers','id=eq.'+BID),45) and not row('reviews','beer=eq.'+BID))
        def imgGone():
            c,_=api(img[len(SB):]+'?t='+str(time.time()),raw=True); return c!=200
        ok('16 billedet slettes også',img and wait(imgGone,25),'billedet ligger der stadig (kræver supabase/002-slet-billeder.sql)')
        A.goto(URL+'#byttur-'+tid); A.wait_for_selector('#tourDel',timeout=20000); A.click('#tourDel')
        ok('17 slettet byttur forsvinder for alle',wait(lambda: not row('tours','id=eq.'+tid),30) and not row('tour_members','tour=eq.'+tid))
        bad=[e for e in errs if 'Synk fejlede' in e or 'pageerror' in e or ': ' in e and 'console' not in e]
        ok('18 ingen fejl i browseren',not bad,bad[:4] or errs[:4])
    except Exception as e:
        ok('testen kørte til ende',False,repr(e))
    finally:
        # oprydning, uanset hvad der skete
        if tokB: api('/rest/v1/review_votes?review=eq.'+R1,method='DELETE',token=tokB); api('/rest/v1/reviews?id=eq.'+R2,method='DELETE',token=tokB); 
        if tokB and tid: api(f'/rest/v1/tour_members?tour=eq.{tid}&name=eq.TestB',method='DELETE',token=tokB)
        if tokA:
            api('/rest/v1/reviews?id=eq.'+R1,method='DELETE',token=tokA); api('/rest/v1/beers?id=eq.'+BID,method='DELETE',token=tokA)
            if tid: api('/rest/v1/tours?id=eq.'+tid,method='DELETE',token=tokA)
            if sid: api('/rest/v1/tastings?id=eq.'+sid,method='DELETE',token=tokA)
            if img: api('/storage/v1/object/billeder/'+img.split('/billeder/',1)[1],method='DELETE',token=tokA)
        left=row('beers','id=eq.'+BID)+row('reviews','id=in.(%s,%s)'%(R1,R2))+(row('tours','id=eq.'+tid) if tid else [])+(row('tastings','id=eq.'+sid) if sid else [])
        ok('19 testdata er ryddet væk',not left,left)
        if errs: print('browser-beskeder:',errs[:6])
        b.close()
# Hvad ligger der i databasen lige nu? (Alt i databasen er offentligt, så det må gerne stå i loggen.)
try:
    c,B=api('/rest/v1/beers?select=id,name,brewery,img,created_at,data&order=created_at.desc&limit=1000'); c2,RV=api('/rest/v1/reviews?select=id,who,created_at&order=created_at.desc&limit=1000')
    c3,T=api('/rest/v1/tours?select=id&limit=1000'); c4,TS=api('/rest/v1/tastings?select=id&limit=1000')
    print(f"STATUS database: {len(B)} øl, {len(RV)} bedømmelser, {len(T)} byture, {len(TS)} smagninger")
    for b in B[:5]: print('STATUS øl:',b['created_at'][:16],'|',b['name'][:40],'|',(b.get('brewery') or '')[:30],'| tilføjet af',str((b.get('data') or {}).get('addedBy',''))[:20],'| billede' if b.get('img') else '| uden billede')
    print('STATUS smagere:',sorted({r['who'][:20] for r in RV})[:12])
except Exception as e: print('STATUS database: kunne ikke læses',e)
# Er tilføjelserne til konto og mails sat op? (Kun læsning. mail_afmeld med en nøgle, der ikke findes, ændrer ingenting.)
try:
    c,_=api('/rest/v1/review_vote_counts?select=review&limit=1'); ck,_=api('/rest/v1/konto_data?select=user_id&limit=1')
    print('STATUS supabase/003 (stemmer, konto, mailvalg):','kørt' if c==200 and ck==200 else 'kørt i en ÆLDRE udgave, skal køres igen' if c==200 else 'IKKE kørt endnu (svar %s)'%c)
    c,_=api('/rest/v1/rpc/mail_afmeld',method='POST',body={'u':'00000000-0000-4000-8000-000000000000'}); print('STATUS supabase/004 (udsendelse af mails):','kørt' if c==200 else 'IKKE kørt endnu (svar %s)'%c)
    c,_=api('/functions/v1/mails',raw=True); print('STATUS funktionen mails:','oprettet' if c==200 else 'oprettet, men "Verify JWT" er slået til' if c==401 else 'IKKE oprettet endnu (svar %s)'%c)
except Exception as e: print('STATUS konto og mails: kunne ikke læses',e)
print('ALT OK' if all(R.values()) else f'{list(R.values()).count(False)} FEJL af {len(R)}')
sys.exit(0 if all(R.values()) else 1)
