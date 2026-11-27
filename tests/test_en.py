"""Den engelske version: alle sider gås igennem på dansk og på engelsk, og testen fejler, hvis en tekst ikke er oversat.
Kør: python3 -m http.server 8811 &  og derefter  python3 tests/test_en.py
Med  --dump fil.json  skrives de tekster, der mangler i js/en.js, til en fil."""
import json,re,os,sys,datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
URL=os.environ.get('SITE','http://localhost:8811/')
from mock_supabase import Mock,HOST
from playwright.sync_api import sync_playwright
res=[]
def check(n,c,x=''):
    res.append(bool(c)); print(('PASS ' if c else 'FAIL ')+n,'' if c else x)
NOW=datetime.datetime(2026,11,26,20,30)   # uret står stille, så teksterne er ens i de to gennemløb
# Indhold, som brugerne selv har skrevet. Det skal IKKE oversættes.
USER=['Ukendt Person','Findes Ikke','pasttour1','futtour01','nowtour01','emptytour','tastopen1','tastgues1','Limfjordsporter','Thisted Bryghus','Thisted','Skærgaard Pilsner','Fanø Bryghus','Fanø','Nørresundby IPA','Søgaards Bryghus','Aalborg','Fri Hvede','Svaneke Bryghus','Svaneke','Julebryg fra Skagen','Skagen Bryghus','Skagen','Havn Stout','Aalborg Bryghus','Ny og ubedømt','Lucas','Magnus','Sofie','Emil',
 'Mørk og blød med et strejf af kaffe.','Rigtig god til julefrokosten','Lidt for bitter til mig','Føtex','J-dag i Aalborg','Nytårstur','Fredagsbar','Nytorv','Husk julesweater!','John Bull Pub','Den Tatoverede Enke','Østerågade 20','Julefrokost 2026','Sommersmagning','Åben smagning','Øl fra Nordjylland','Øl fra Fyn','Øl fra Sjælland','5701234567890']
SEED="""(()=>{const S=JSON.parse(localStorage.getItem('olrating-v1')||'{}');const d='2026-11-20',s=(a,b,c,e,f)=>({look:a,aroma:b,taste:c,feel:e,overall:f});
 S.beers=[];S.reviews=[];
 const B=(id,name,brewery,style,x={})=>S.beers.push({id,name,brewery,style,city:x.city||'Aalborg',country:x.country||'Danmark',abv:x.abv??5,ibu:x.ibu||0,color:x.color||'',price:x.price||0,place:x.place||'',size:x.size||'33 cl flaske',desc:x.desc||'',code:x.code||'',af:!!x.af,date:x.date||d,addedBy:x.by||'Magnus',img:''});
 B('a1','Limfjordsporter','Thisted Bryghus','Porter',{city:'Thisted',abv:7.9,ibu:35,color:'Sort',price:28,place:'Føtex',size:'50 cl flaske',desc:'Mørk og blød med et strejf af kaffe.',code:'5701234567890',by:'Lucas'});
 B('a2','Skærgaard Pilsner','Fanø Bryghus','Pilsner',{city:'Fanø',abv:4.6,ibu:22,color:'Lys',price:18,size:'33 cl dåse'});
 B('a3','Nørresundby IPA','Søgaards Bryghus','IPA',{abv:6.2,ibu:60,color:'Rav',size:'44 cl dåse',country:'Tyskland'});
 B('a4','Fri Hvede','Svaneke Bryghus','Hvede',{abv:0,af:true,city:'Svaneke',color:'Gylden',size:'Fadøl'});
 B('a5','Julebryg fra Skagen','Skagen Bryghus','Juleøl',{city:'Skagen',abv:9.5,color:'Rød',size:'75 cl flaske',country:'Belgien'});
 B('a6','Havn Stout','Aalborg Bryghus','Stout',{abv:3.2,color:'Brun',size:'50 cl dåse'});
 B('a7','Ny og ubedømt','Aalborg Bryghus','Sour',{abv:2.5,size:'Andet',country:'Andet land'});
 let n=0;const R=(beer,who,sc,x={})=>S.reviews.push({id:'r'+(n++),beer,who,date:x.date||d,s:sc,prof:x.prof||null,tags:x.tags||[],again:x.again??1,text:x.text||'',img:''});
 R('a1','Lucas',s(5,5,5,4,5),{tags:['Kaffe','Chokolade','Ristet'],prof:{sweet:3,bitter:4,sour:1,body:5,roast:5},text:'Rigtig god til julefrokosten'});R('a1','Magnus',s(4,4,4,4,4),{tags:['Ristet']});
 R('a2','Lucas',s(4,4,4,4,4),{tags:['Frisk','Let']});R('a2','Magnus',s(4,3,4,4,4),{again:0,text:'Lidt for bitter til mig',tags:['Bitter']});R('a2','Sofie',s(5,5,5,5,5),{date:'2025-12-20'});
 R('a3','Lucas',s(4,4,4,3,4),{tags:['Citrus','Frugtig']});R('a3','Magnus',s(3,3,3,3,3));R('a4','Magnus',s(4,4,4,4,4));R('a4','Lucas',s(3,3,3,3,3),{date:'2026-11-26'});
 R('a5','Magnus',s(3,3,3,3,3),{tags:['Krydret','Sød']});R('a5','Sofie',s(4,4,4,4,4));R('a6','Lucas',s(2,2,2,2,2));R('a6','Magnus',s(3,3,3,3,3));
 const st=[{name:'Søgaards Bryghus',time:'19:00',addr:''},{name:'John Bull Pub',time:'21:00',addr:'Østerågade 20'},{name:'Den Tatoverede Enke',time:'00:30',addr:''}];
 S.tours=[{id:'pasttour1',name:'J-dag i Aalborg',date:'2026-11-20T19:00',meet:'Nytorv',note:'Husk julesweater!',host:'Lucas',stops:st,members:[{name:'Lucas'},{name:'Magnus'}]},
  {id:'futtour01',name:'Nytårstur',date:'2026-12-31T20:00',meet:'',note:'',host:'Magnus',stops:st.slice(0,1),members:[{name:'Magnus'}]},
  {id:'nowtour01',name:'Fredagsbar',date:'2026-11-26T19:00',meet:'Nytorv',note:'',host:'Lucas',stops:st,members:[{name:'Lucas'},{name:'Emil'}]},
  {id:'emptytour',name:'Sommersmagning',date:'2026-11-10T12:00',meet:'',note:'',host:'Magnus',stops:[],members:[]}];
 S.tast=[{id:'tastopen1',name:'Julefrokost 2026',host:'Lucas',blind:true,revealed:false,beers:['Øl fra Nordjylland','Øl fra Fyn','Øl fra Sjælland'],votes:{Lucas:[4,3,5],Magnus:[5,2,4]}},
  {id:'tastdone1',name:'Sommersmagning',host:'Lucas',blind:true,revealed:true,beers:['Øl fra Nordjylland','Øl fra Fyn','Øl fra Sjælland'],votes:{Lucas:[4,3,5],Magnus:[5,2,4],Sofie:[3,3,3]}},
  {id:'tastgues1',name:'Åben smagning',host:'Magnus',blind:false,revealed:false,beers:['Øl fra Nordjylland','Øl fra Fyn'],votes:{}},
  {id:'tastgues2',name:'Åben smagning',host:'Magnus',blind:false,revealed:true,beers:['Øl fra Nordjylland','Øl fra Fyn'],votes:{Emil:[5,1]}}];
 const t=new Date(2026,10,26,19,30).getTime();S.units=[{t:t,g:1.1,n:'Skærgaard Pilsner'},{t:t+600000,g:1,n:''},{t:t-3*864e5,g:2.2,n:'Fra widget'}];
 S.wish=['a5','a7'];S.follow=['Magnus'];S.me=ME;S.lang=LANG;localStorage.setItem('olrating-v1',JSON.stringify(S))})()"""
GRAB="""()=>{const out=[],cl=t=>(t||'').replace(/\\s+/g,' ').trim(),A=['placeholder','aria-label','title','alt'];
 const walk=(n,f)=>{if(n.nodeType===3){const t=cl(n.nodeValue);if(t)out.push((f?'f|':'t|')+t);return}
  if(n.nodeType!==1||/^(SCRIPT|STYLE)$/.test(n.nodeName)||n.hasAttribute('data-notr'))return;
  A.forEach(a=>{const v=cl(n.getAttribute(a));if(v)out.push('t|'+v)});
  if(n.nodeName==='TEXTAREA')return;
  if(n.firstElementChild){const k=window.__tr.skel(n);if(k){out.push('s|'+k);f=true}}
  for(let c=n.firstChild;c;c=c.nextSibling)walk(c,f)};
 walk(document.body,false);out.push('t|'+cl(document.title));return out}"""
def crawl(b,lang):
    """Går alle sider og tilstande igennem og returnerer {tilstand: [tekster]}"""
    M=Mock(); errs=[]; out={}
    c=b.new_context(viewport={'width':1280,'height':900},service_workers='block',locale='da-DK'); c.route(f'https://{HOST}/**',M.handle)
    pg=c.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.set_fixed_time(NOW)
    pg.add_init_script("window.confirm=()=>true;window.prompt=()=>'Lucas';")
    def seed(me,empty=False):
        # Eksempeldata lægges ind fra en side uden sidens egen kode (robots.txt på samme adresse), så siden ikke kan nå at gemme oven i dem.
        pg.goto(URL+'robots.txt')
        if empty: pg.evaluate("(l=>{localStorage.clear();localStorage.setItem('olrating-v1',JSON.stringify({lang:l}))})",lang)
        else: pg.evaluate(SEED.replace('ME',json.dumps(me)).replace('LANG',json.dumps(lang)))
        pg.goto(URL); pg.wait_for_timeout(1300)
    def grab(k): out[k]=pg.evaluate(GRAB)
    def go(h,k=None,wait=450): pg.goto(URL+h); pg.wait_for_timeout(wait); grab(k or h)
    seed('Lucas')
    # andres bedømmelser får en anden ejer, så der er noget at swipe på, og mine egne får stemmer
    for r in M.t['reviews'].values():
        if r['who']!='Lucas': r['owner']='00000000-0000-4000-8000-00000000ffff'
    for i,k in enumerate([k for k,r in M.t['reviews'].items() if r['who']=='Lucas'][:3]):
        M.rvotes[(k,'u1')]=1; M.rvotes[(k,'u2')]=1 if i else -1
    pg.evaluate("sbSync()"); pg.wait_for_timeout(1800)
    for h in ['','#swipe','#buddies','#hjul','#indstillinger','#toplisten','#aarets','#galleri','#sammenlign','#byttur','#byttur-pasttour1','#byttur-futtour01','#byttur-nowtour01','#byttur-emptytour','#byttur-findesikke','#smagning','#smagning-tastopen1','#smagning-tastdone1','#smagning-tastgues1','#smagning-tastgues2',
              '#venner','#smager-Magnus','#smager-Sofie','#nyt','#stilguide','#bryggeri-Thisted%20Bryghus','#bryggeri-Findes%20Ikke','#profil','#tilfoej','#kalender','#dagbog','#mad','#genstande','#privatliv','#om','#beer-a1','#beer-a2','#beer-a3','#beer-a4','#beer-a5','#beer-a7','#beer-findesikke']: go(h)
    # filtre, tom søgning og sortering
    pg.goto(URL+'#alle'); pg.wait_for_timeout(400); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); grab('#alle+filtre')
    pg.fill('#q','xyzzy'); pg.wait_for_timeout(300); grab('#alle+ingen'); pg.press('#q','Enter'); pg.wait_for_timeout(300); grab('#alle+soegt')
    for i in range(4):
        pg.goto(URL+'#toplisten'); pg.wait_for_timeout(250); pg.click(f'[data-tab="{i}"]'); pg.wait_for_timeout(250); grab(f'#toplisten+{i}')
    pg.goto(URL+'#aarets'); pg.wait_for_timeout(300); pg.click('[data-year="2025"]'); pg.wait_for_timeout(300); grab('#aarets+2025')
    pg.goto(URL+'#sammenlign'); pg.wait_for_timeout(300); pg.select_option('#cmp0','a1'); pg.select_option('#cmp1','a2'); pg.wait_for_timeout(400); grab('#sammenlign+valgt')
    pg.goto(URL+'#beer-a1'); pg.wait_for_timeout(400); pg.click('#editBeer'); pg.wait_for_timeout(500); grab('#tilfoej+ret')
    pg.fill('#bAbv','0,3'); pg.wait_for_timeout(150); grab('abv1'); pg.fill('#bAbv','3'); pg.wait_for_timeout(150); grab('abv2'); pg.fill('#bAbv','7'); pg.wait_for_timeout(150); grab('abv3'); pg.fill('#bAbv','11'); pg.wait_for_timeout(150); grab('abv4')
    for v in ['5','25','45','70','110']: pg.fill('#bIbu',v); pg.wait_for_timeout(120); grab('ibu'+v)
    pg.goto(URL+'#tilfoej'); pg.wait_for_timeout(400); pg.fill('#bName','Skærgard Pilsner'); pg.wait_for_timeout(500); grab('#tilfoej+dublet')
    pg.goto(URL+'#beer-a1'); pg.wait_for_timeout(400); pg.click('#wishBtn'); pg.wait_for_timeout(200); grab('#beer+ønske'); pg.click('[data-unit]'); pg.wait_for_timeout(200); grab('#beer+genstand')
    if pg.query_selector('[data-editrev]'): pg.click('[data-editrev]'); pg.wait_for_timeout(300); grab('#beer+retanm')
    pg.goto(URL+'#beer-a1'); pg.wait_for_timeout(400)
    if pg.query_selector('[data-delrev]'): pg.click('[data-delrev]'); pg.wait_for_timeout(300); grab('#beer+fortryd'); pg.click('.undo button'); pg.wait_for_timeout(300)
    pg.goto(URL+'#smager-Ukendt%20Person'); pg.wait_for_timeout(300); grab('#smager+ukendt')
    pg.goto(URL+'#swipe'); pg.wait_for_timeout(400); pg.evaluate("document.getElementById('swYes').click()"); pg.wait_for_timeout(600); grab('#swipe+stemt')
    pg.evaluate("document.getElementById('swSkip').click()"); pg.wait_for_timeout(600)
    for i in range(12):
        if not pg.query_selector('#swNo'): break
        pg.evaluate("document.getElementById('swNo').click()"); pg.wait_for_timeout(500)
    grab('#swipe+færdig')
    # konto (skjult indtil den er sat op) og afmeld-siden fra linket i mails
    pg.goto(URL+'#konto-test'); pg.wait_for_timeout(700); grab('#konto+ny')
    pg.fill('#acMail','lucas@example.dk'); pg.evaluate("document.querySelector('#acctForm button').click()"); pg.wait_for_timeout(900); grab('#konto+kode')
    pg.fill('#acCode','123456'); pg.evaluate("document.querySelector('#acctCode button').click()"); pg.wait_for_timeout(2500); grab('#konto+logget ind')
    pg.evaluate("document.getElementById('mp_news').click()"); pg.wait_for_timeout(700); grab('#konto+mailvalg')
    go('#privatliv','#privatliv+konto'); go('#afmeld-ikke-en-noegle','#afmeld+ugyldig')
    go('#afmeld-00000000-0000-4000-a000-999999999999','#afmeld+ukendt'); pg.evaluate("document.getElementById('unsubGo').click()"); pg.wait_for_timeout(600); grab('#afmeld+ukendt+svar')
    go('#afmeld-'+next(iter(M.unsub.values()),'x'),'#afmeld'); pg.evaluate("document.getElementById('unsubGo').click()"); pg.wait_for_timeout(600); grab('#afmeld+svar')
    pg.goto(URL+'#profil'); pg.wait_for_timeout(1500); pg.evaluate("document.getElementById('acOut').click()"); pg.wait_for_timeout(2500); pg.evaluate("localStorage.removeItem('olrating-konto')")
    # uden navn
    seed('')
    for h in ['#profil','#dagbog','#venner','#byttur','#smagning','#genstande','#beer-a1','#byttur-futtour01','#smagning-tastgues1','']: go(h,h+'+ukendt')
    # helt tom side: ny browser-profil og tom database
    c.close(); M=Mock(); c=b.new_context(viewport={'width':1280,'height':900},service_workers='block',locale='da-DK'); c.route(f'https://{HOST}/**',M.handle)
    pg=c.new_page(); pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.set_fixed_time(NOW)
    seed('',empty=True)
    for h in ['','#swipe','#buddies','#hjul','#indstillinger','#toplisten','#aarets','#galleri','#sammenlign','#stilguide','#profil','#dagbog','#venner','#byttur','#smagning','#genstande','#tilfoej','#kalender']: go(h,h+'+tom')
    c.close()
    return out,errs
def segs(strings):
    o=set()
    for t in strings:
        o.add(t)
        for p in t.split(' · '): o.add(p.strip())
    return o
# Tekster, der er ens på dansk og engelsk
SAME=set('''Fjord IPA Stout Porter Sour Lager Pale Ale Brown Ale Bock Pilsner Bitter Citrus Malt Normal Halloween USA Mexico Japan England Android Windows Linux iPhone iPad Safari Chrome OK Web Share GitHub Supabase Google Maps QR Top Min Max IBU cl % ABV
ølrating ølrating.dk .dk Lucas Valentin Ottesen Magnus Birkgaard Froberg Limfjorden Start Info Tema Dansk English Sprog · Language Sprog Language'''.replace('\n',' ').split(' '))
SAME|={'Pale Ale','Brown Ale','J-dag','Web Share','Google Maps','Lucas Valentin Ottesen','Magnus Birkgaard Froberg'}
SAME|={'Beer buddies','Swipe','Scan','Linux:','Windows:','Downloads','TOP 3','+ Stop','Download backup','Snifter','Pizza','Burger','Mild','ølrating.dk logo','olrating.apk','olrating-windows.exe','olrating-linux.AppImage','andersenlucas84@gmail.com','Findes Ikke','cl','Fx mfx3k2abcd','Globetrotter','ølrating<1>.dk</1>','1 stop','Open Food Facts','CC BY-SA'}
# Mønstre for tekster, der er ens på begge sprog: mål, koder og navne med tal
SAME_RE=re.compile(r'^(\d+ cl|\d+ IBU|© \d{4} .*|[\d.,]+ ?%|[A-ZÆØÅ]|✓ .+|\d\. .+|“.*”|.+ ↗|■ .+|[^\s@]+@[^\s@]+)$')
def letters(t): return re.search(r'[A-Za-zÆØÅæøå]{2,}',t) is not None
def strip_user(t):
    for u in sorted(USER,key=len,reverse=True): t=t.replace(u,'')
    return t.replace('ølrating.dk','').replace('ølrating','').replace('Ølrating','').replace('Føtex','').replace('Ølbaren','')
def main():
    dump=sys.argv[sys.argv.index('--dump')+1] if '--dump' in sys.argv else None
    with sync_playwright() as p:
        b=getattr(p,os.environ.get('BROWSER','chromium')).launch()
        da,e1=crawl(b,'da'); en,e2=crawl(b,'en')
        # statiske tjek af ordbogen i en rigtig side
        M0=Mock(); c=b.new_context(service_workers='block'); c.route(f'https://{HOST}/**',M0.handle); pg=c.new_page(); pg.goto(URL); pg.wait_for_timeout(600)
        info=pg.evaluate("""async()=>{await new Promise((ok,no)=>{const s=document.createElement('script');s.src='js/en.js';s.onload=ok;s.onerror=no;document.head.appendChild(s)});const E=window.EN_DATA,x=E.x,bad=[];
          for(const k in x){const v=x[k];if(typeof v!=='string'){bad.push('ikke tekst: '+k);continue}if(v!==k&&Object.prototype.hasOwnProperty.call(x,v)&&x[v]!==v)bad.push('kæde: '+k+' -> '+v+' -> '+x[v])}
          return {n:Object.keys(x).length,r:E.r.length,bad}}""")
        # beskeder (toast, confirm, prompt) står kun i koden, så de tjekkes direkte mod ordbogen
        src=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read(); lits=[]
        for m in re.finditer(r"(?:toast|confirm|prompt)\(",src):
            i=m.end(); d=1; j=i
            while j<len(src) and d: d+=(src[j]=='(')-(src[j]==')'); j+=1
            arg=src[i:j-1]
            for q in re.finditer(r"'((?:[^'\\\n]|\\.)*)'|`((?:[^`\\]|\\.)*)`",arg):
                t=q.group(1) if q.group(1) is not None else re.sub(r'\$\{(?:[^{}]|\{[^{}]*\})*\}','7',q.group(2))
                t=t.replace("\\'","'")
                if t.startswith(' '): t='7'+t     # tekst, der sættes efter et navn
                if re.search(r'[a-zæøå]{3,}',t) and ' ' in t and t not in lits: lits.append(t)
        # --- sprogvælgeren: skift uden at siden hentes igen, og tilbage til præcis den samme danske tekst
        c2=b.new_context(service_workers='block',viewport={'width':1280,'height':900},locale='en-GB'); c2.route(f'https://{HOST}/**',M0.handle); p2=c2.new_page(); p2.clock.set_fixed_time(NOW); p2.goto(URL); p2.wait_for_timeout(1500)
        hint=p2.inner_text('#langCode')=='English?' and p2.evaluate("document.getElementById('langBtn').classList.contains('hint')") and p2.evaluate("document.documentElement.lang")=='da'
        p2.goto(URL+'robots.txt'); p2.evaluate(SEED.replace('ME',json.dumps('Lucas')).replace('LANG',json.dumps('da'))); p2.goto(URL); p2.wait_for_timeout(1500)   # se seed()
        GR="()=>{document.getElementById('toast').textContent='';return ("+GRAB+")()}"; JSCLICK="q=>document.querySelector(q).click()"
        def jsclick(q): p2.wait_for_selector(q,state='attached',timeout=8000); p2.evaluate(JSCLICK,q)   # venter, til knappen findes (Firefox kan være et øjeblik bagefter)
        trip=[]; inplace=[]
        for h in ['','#toplisten','#aarets','#profil','#byttur-pasttour1','#smagning-tastdone1','#genstande','#stilguide','#kalender','#om','#privatliv','#tilfoej','#beer-a1']:
            p2.goto(URL+h); p2.wait_for_timeout(1900 if h.startswith('#beer-') else 500); p2.evaluate("window.__mark=1;scrollTo(0,300)"); before=p2.evaluate(GR); y0=p2.evaluate('scrollY')
            # klik sendes direkte til knappen: Playwrights eget klik ruller siden, når knappen sidder i den faste topmenu
            jsclick('#langBtn'); vis=p2.is_visible('#langdd [data-lang="en"]'); jsclick('#langdd [data-lang="en"]'); p2.wait_for_timeout(700); mid=p2.evaluate(GR)
            ok_en=vis and p2.evaluate("document.documentElement.lang")=='en' and p2.inner_text('#nav a >> nth=0')=='All beers' and p2.evaluate('window.__mark')==1 and abs(p2.evaluate('scrollY')-y0)<3 and not p2.is_visible('#langdd') and p2.inner_text('#langCode')=='EN'
            jsclick('#langBtn'); jsclick('#langdd [data-lang="da"]'); p2.wait_for_timeout(700); after=p2.evaluate(GR)
            if not ok_en or mid==before: inplace.append(h)
            if after!=before:
                i=next((k for k,(x,y) in enumerate(zip(after,before)) if x!=y),min(len(after),len(before)))   # første sted, de er forskellige (også når kun rækkefølge eller antal er skiftet)
                trip.append((h,[x for x in after if x not in before][:4],[x for x in before if x not in after][:4],len(before),len(after),before[i:i+2],after[i:i+2]))
        # mens man skriver i en formular, bliver siden ikke tegnet forfra, så det skrevne bliver stående
        p2.goto(URL+'#tilfoej'); p2.wait_for_timeout(400); p2.fill('#bName','Min nye øl'); jsclick('#langBtn'); jsclick('#langdd [data-lang="en"]'); p2.wait_for_timeout(700)
        keep=p2.input_value('#bName')=='Min nye øl' and p2.get_attribute('#bName','placeholder')=='E.g. Limfjordsporter'
        p2.wait_for_timeout(600)
        untr=[t for t in lits if p2.evaluate("t=>window.__tr.s(t)===t",t)]
        # brede engelske tekster må ikke give vandret scroll på mobil
        p2.set_viewport_size({'width':390,'height':800}); wide=[]
        MOB=['','#toplisten','#aarets','#swipe','#buddies','#hjul','#indstillinger','#byttur','#smagning','#venner','#stilguide','#profil','#tilfoej','#kalender','#mad','#genstande','#privatliv','#om','#nyt','#sammenlign','#afmeld-00000000-0000-4000-a000-000000000001']
        def smal(w,ud):   # også de smalleste telefoner: 360 px er den mest almindelige Android-bredde, 320 px den mindste
            p2.set_viewport_size({'width':w,'height':740})
            for h in MOB:
                p2.goto(URL+h); p2.wait_for_timeout(250)
                if p2.evaluate('document.documentElement.scrollWidth>innerWidth+1'): ud.append(f'{h} ved {w} px')
        smal(360,wide); smal(320,wide); p2.set_viewport_size({'width':390,'height':800})
        for h in MOB:
            p2.goto(URL+h); p2.wait_for_timeout(300)
            if p2.evaluate('document.documentElement.scrollWidth>innerWidth+1'):   # skriv også, hvad der stikker ud: elementer, tekst og mål
                wide.append(h+' '+str(p2.evaluate("""(()=>{const W=innerWidth,d=e=>e.tagName+(e.id?'#'+e.id:'')+'.'+String(e.className&&e.className.baseVal!==undefined?e.className.baseVal:e.className).slice(0,30);
                  const els=[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.right>W+1&&![...e.children].some(c=>c.getBoundingClientRect().right>W+1)}).slice(0,5).map(e=>d(e)+' right='+Math.round(e.getBoundingClientRect().right)+' pos='+getComputedStyle(e).position+' "'+(e.textContent||e.value||'').trim().slice(0,30)+'"');
                  const tx=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())&&tx.length<5){if(!n.nodeValue.trim())continue;const g=document.createRange();g.selectNodeContents(n);const r=g.getBoundingClientRect();if(r.width>0&&r.right>W+1)tx.push(d(n.parentElement)+' tekst right='+Math.round(r.right)+' "'+n.nodeValue.trim().slice(0,30)+'"')}
                  const sc=[...document.querySelectorAll('body *')].filter(e=>e.scrollWidth>e.clientWidth+1&&e.clientWidth>0&&getComputedStyle(e).overflowX==='visible'&&getComputedStyle(e).display!=='inline').slice(0,5).map(e=>d(e)+' sw='+e.scrollWidth+' cw='+e.clientWidth);
                  return {W,doc:document.documentElement.scrollWidth,body:document.body.scrollWidth,client:document.documentElement.clientWidth,els,tx,sc}})()""")))
        p2.reload(); p2.wait_for_timeout(1500)
        lang_ok=p2.evaluate("document.documentElement.lang")=='en' and p2.evaluate("document.getElementById('langSel').value")=='en' and p2.is_visible('#langBtn')
        p2.select_option('#langSel','da'); p2.wait_for_timeout(800)
        back=p2.evaluate("document.documentElement.lang")=='da' and p2.inner_text('#nav a >> nth=0',timeout=3000)=='Alle øl' if p2.viewport_size['width']>1100 else p2.evaluate("document.documentElement.lang")=='da' and p2.evaluate("document.querySelector('#nav a').textContent")=='Alle øl'
        wide_da=[]; smal(320,wide_da)
        c2.close()
        c.close(); b.close()
    check(f'[en] alle beskeder i koden er oversat ({len(lits)} stk.)',not untr and len(lits)>40,untr[:8])
    check('[en] ingen vandret scroll på mobil på engelsk (390, 360 og 320 px)',not wide,wide)
    check('[da] ingen vandret scroll på de smalleste telefoner (320 px)',not wide_da,wide_da)
    check('[en] sprogvalget huskes efter genindlæsning og kan skiftes i sidefoden',lang_ok and back,(lang_ok,back))
    check('[en] sprogmenuen skifter med det samme uden genindlæsning og beholder stedet på siden',not inplace,inplace)
    check('[en] tilbage til dansk giver præcis den samme tekst som før',not trip,trip[:3])
    check('[en] tekst i en formular bliver stående, når sproget skiftes',keep)
    check('[en] browsere på andre sprog får et vink om engelsk',hint)
    check('[en] ingen fejl i konsollen på dansk eller engelsk',not e1 and not e2,(e1[:2],e2[:2]))
    check('[en] de samme sider er gennemgået i begge sprog',set(da)==set(en) and len(da)>80,len(da))
    check('[en] ordbogen er gyldig og uden kæder',not info['bad'],info['bad'][:5])
    kind={}
    for v in list(da.values())+list(en.values()):
        for i,t in enumerate(v): kind.setdefault(t[2:],t[0]); v[i]=t[2:]
    D=segs(t for v in da.values() for t in v); missing={}
    user=set(USER)
    for k,v in en.items():
        for t in segs(v):
            if ' · ' in t: continue          # delene tjekkes hver for sig
            if not letters(t) or t in SAME or t in user or SAME_RE.match(t): continue
            rest=strip_user(t)
            if not letters(rest): continue
            same=t in D                       # står præcis sådan i den danske udgave
            dk=re.search(r'[æøåÆØÅ]',rest)     # danske bogstaver uden for navne
            if same or dk: missing.setdefault(t,k)
    check(f'[en] al tekst er oversat ({info["n"]} tekster og {info["r"]} mønstre i ordbogen)',not missing,f'{len(missing)} mangler, fx '+json.dumps(list(missing.items())[:12],ensure_ascii=False))
    # brugernes eget indhold må ikke blive oversat
    lost=[u for u in USER if not any(u in t for v in en.values() for t in v)]
    check('[en] brugernes eget indhold er ikke oversat',not lost,lost)
    check('[en] tal har punktum på engelsk og komma på dansk',any(t=='4.5' for t in en['#beer-a1']) and any(t=='4,5' for t in da['#beer-a1']),[t for t in en['#beer-a1'] if re.match(r'^\d[.,]\d$',t)][:5])
    if dump:
        json.dump({'missing':missing,'kind':kind,'da':da},open(dump,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
        print('skrev',dump,len(missing),'mangler')
    print('ALL PASS' if all(res) else f'{res.count(False)} FAILED of {len(res)}')
    sys.exit(0 if all(res) else 1)
if __name__=='__main__': main()
