"""Laver skærmbillederne til Microsoft Store (1366 x 768) på dansk (store/) og engelsk (store/en/).
Øl, bryggerier, barer og navne er opdigtede eksempler. Intet bliver sendt til den rigtige database.
Kør:  python3 -m http.server 8811 &   og derefter   python3 store/lav-skaermbilleder.py"""
import os,sys,json,datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,'tests'))
from mock_supabase import Mock,HOST
from playwright.sync_api import sync_playwright
URL=os.environ.get('SITE','http://localhost:8811/')
NOW=datetime.datetime(2026,11,22,19,30)
SEED="""(lang=>{const S={beers:[],reviews:[],me:'Lucas',lang,season:'none',wish:['b5'],follow:['Magnus'],units:[],tours:[],tast:[]};
 const B=(id,name,brewery,style,abv,x={})=>S.beers.push({id,name,brewery,style,city:x.city||'Aalborg',country:'Danmark',abv,ibu:x.ibu||0,color:x.color||'',price:x.price||0,place:x.place||'',size:x.size||'33 cl flaske',desc:x.desc||'',code:'',af:!!x.af,date:x.date||'2026-10-02',addedBy:x.by||'Lucas',img:''});
 B('b1','Mørk Fjord Stout','Fjordbryg','Stout',7.5,{ibu:40,color:'Sort',price:32,size:'50 cl flaske'});
 B('b2','Solnedgang IPA','Fjordbryg','IPA',6.2,{ibu:55,color:'Gylden',price:28,place:'Den lokale ølbutik',desc:'Tørhumlet og frisk. Brygget ved fjorden.'});
 B('b3','Bropillen Porter','Fjordbryg','Porter',6.8,{ibu:35,color:'Brun',by:'Emma'});
 B('b4','Havnepilsner','Kajens Bryghus','Pilsner',4.8,{ibu:25,color:'Lys',city:'Nørresundby',by:'Magnus'});
 B('b5','Vestenvind Pale Ale','Nordenvind','Pale Ale',5.4,{ibu:38,color:'Rav',city:'Løkken',by:'Magnus'});
 B('b6','Julebryg fra Kajen','Kajens Bryghus','Juleøl',6.0,{color:'Rød',city:'Nørresundby',date:'2026-11-06',by:'Magnus'});
 B('b7','Fri Fjord','Fjordbryg','Hvede',0.4,{af:true,color:'Lys',by:'Emma'});
 let n=0;const R=(beer,who,s,date,x={})=>S.reviews.push({id:'r'+(n++),beer,who,date,s:{look:s[0],aroma:s[1],taste:s[2],feel:s[3],overall:s[4]},prof:x.prof||null,tags:x.tags||[],again:x.again??1,text:x.text||'',img:''});
 R('b1','Lucas',[5,5,5,4,5],'2026-11-14',{tags:['Chokolade','Ristet','Kaffe'],prof:{sweet:3,bitter:3,sour:1,body:5,roast:5},text:'Blød og mørk. Smager af kaffe og mørk chokolade.'});R('b1','Magnus',[5,4,5,5,4],'2026-11-15',{tags:['Ristet']});
 R('b2','Lucas',[5,5,5,4,5],'2026-11-20',{tags:['Citrus','Bitter','Frugtig'],prof:{sweet:2,bitter:4,sour:2,body:3,roast:1},text:'Frisk og fuld af citrus. Perfekt på kajen i aftensolen.'});R('b2','Magnus',[4,5,4,4,5],'2026-11-18',{tags:['Citrus']});R('b2','Emma',[4,4,5,4,4],'2026-11-12',{tags:['Frugtig']});
 R('b3','Emma',[4,4,5,4,4],'2026-11-10',{tags:['Ristet','Kaffe']});
 R('b4','Magnus',[4,4,4,4,4],'2026-11-08',{tags:['Frisk','Let']});R('b4','Lucas',[4,4,4,3,4],'2026-11-09',{tags:['Frisk']});
 R('b5','Magnus',[4,4,4,4,3],'2026-11-05',{tags:['Frugtig']});R('b5','Emma',[4,4,4,4,4],'2026-11-07');
 R('b6','Magnus',[4,4,4,3,4],'2026-11-21',{tags:['Krydret','Karamel'],text:'Årets første juleøl. Krydret og rund.'});R('b6','Emma',[4,3,4,4,4],'2026-11-21');
 R('b7','Emma',[4,3,4,3,4],'2026-11-16',{tags:['Frisk']});
 S.tast=[{id:'julefrokost26',name:'Julefrokost 2026',host:'Lucas',blind:true,revealed:true,beers:['Julebryg fra Kajen','Solnedgang IPA','Mørk Fjord Stout','Havnepilsner'],votes:{Lucas:[4,5,4,3],Magnus:[4,4,5,4],Emma:[3,5,4,3],Oliver:[4,4,4,4]}}];
 S.tours=[{id:'julefrokosttur',name:'Julefrokost-tur i Aalborg',date:'2026-12-11T19:00',meet:'Ved havnefronten',note:'Husk julesweater!',host:'Lucas',stops:[{name:'Havnebaren',time:'19:00',addr:''},{name:'Bryggerhjørnet',time:'20:30',addr:''},{name:'Kælderen',time:'22:00',addr:''}],members:[{name:'Lucas'},{name:'Magnus'},{name:'Emma'},{name:'Oliver'}]}];
 localStorage.setItem('olrating-v1',JSON.stringify(S))})"""
SHOTS=[('1-forside','',0),('2-alle-oel','#alle',-1),('3-oel','#beer-b2',0),('4-smagning','#smagning-julefrokost26',0),('5-byttur','#byttur-julefrokosttur',0),('6-profil','#profil',0),('7-aarets-oel','#aarets',0),('8-beer-buddies','#buddies',0),('9-lykkehjul','#hjul',2),('10-indstillinger','#indstillinger',3)]
with sync_playwright() as p:
    b=p.chromium.launch()
    for lang,folder in [('da',''),('en','en')]:
        out=os.path.join(ROOT,'store',folder); os.makedirs(out,exist_ok=True)
        c=b.new_context(viewport={'width':1366,'height':768},service_workers='block',reduced_motion='reduce'); c.route(f'https://{HOST}/**',Mock().handle)
        pg=c.new_page(); pg.add_init_script("(()=>{let x=7;Math.random=()=>((x=(x*16807)%2147483647)-1)/2147483646})()"); pg.clock.set_fixed_time(NOW); pg.goto(URL); pg.wait_for_timeout(600); pg.evaluate(SEED,lang); pg.reload(); pg.wait_for_timeout(1500)
        for name,h,scroll in SHOTS:
            pg.goto(URL+h); pg.wait_for_timeout(900)
            if scroll==-1: pg.evaluate("window.scrollTo(0,document.getElementById('alle').getBoundingClientRect().top+scrollY-90)"); pg.wait_for_timeout(300)
            if scroll==2: pg.click('[data-hj=alle]'); pg.wait_for_timeout(300); pg.click('#hjSpin'); pg.wait_for_timeout(600); pg.add_style_tag(content='.hjw{max-width:330px}'); pg.wait_for_timeout(100); pg.evaluate("window.scrollTo(0,document.querySelector('.hjw').getBoundingClientRect().top+scrollY-84)"); pg.wait_for_timeout(300)
            if scroll==3: pg.click('[data-look="bg:aften"]'); pg.wait_for_timeout(200); pg.click('[data-look="acc:guld"]'); pg.wait_for_timeout(200); pg.click('[data-look="pat:stjerner"]'); pg.wait_for_timeout(400)
            pg.screenshot(path=os.path.join(out,name+'.png')); print(lang,name)
        c.close()
    b.close()
