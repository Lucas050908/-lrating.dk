// Tjekker supabase/003-konto-mails-enig.sql og 004-mails.sql i en rigtig Postgres, der kører i hukommelsen (PGlite): ejer-regler,
// stemmer, flytning af data til en konto, mailvalg og køen med mails. Funktionen supabase/functions/mails køres også her
// mod den samme database, med en efterligning af mailtjenesten. Rører ikke den rigtige database og sender ingen mails.
// Kør:  npm install --no-save @electric-sql/pglite  og derefter  node tests/test_sql.js
const {PGlite}=require('@electric-sql/pglite');const fs=require('fs');
const path=require('path');const os=require('os');const {pathToFileURL}=require('url');const R=path.join(__dirname,'..','supabase')+path.sep;
(async()=>{const db=new PGlite();let pass=0,fail=0;const ok=(n,c,x)=>{c?pass++:fail++;console.log((c?'PASS ':'FAIL ')+n,c?'':(x??''))};
 // --- efterligning af det, Supabase selv stiller til rådighed
 await db.exec(`create role anon nologin; create role authenticated nologin; create role service_role nologin bypassrls;
  create schema auth; create table auth.users(id uuid primary key, email text, is_anonymous boolean not null default false);
  create function auth.uid() returns uuid language sql stable as $$ select nullif(current_setting('request.jwt.claim.sub', true),'')::uuid $$;
  create function auth.jwt() returns jsonb language sql stable as $$ select coalesce(nullif(current_setting('request.jwt.claims', true),''),'{}')::jsonb $$;
  grant usage on schema public, auth to anon, authenticated, service_role; grant execute on all functions in schema auth to anon, authenticated;
  alter default privileges in schema public grant all on tables to anon, authenticated, service_role;
  alter default privileges in schema public grant all on functions to anon, authenticated, service_role;
  alter default privileges in schema public grant all on sequences to anon, authenticated, service_role;`);
 const schema=fs.readFileSync(R+'schema.sql','utf8');await db.exec(schema.slice(0,schema.indexOf('-- Billeder')));
 const sql=fs.readFileSync(R+'003-konto-mails-enig.sql','utf8');
 await db.exec(sql);await db.exec(sql);ok('003 kan køres to gange',true);
 const sql5=fs.readFileSync(R+'005-besoeg.sql','utf8');
 await db.exec(sql5);await db.exec(sql5);ok('005 kan køres to gange, også før 003 og 004',true);
 const sql4=fs.readFileSync(R+'004-mails.sql','utf8');
 await db.exec(sql4);await db.exec(sql4);ok('004 kan køres to gange (det planlagte job springes over, når pg_cron ikke findes)',true);
 const U={a:'00000000-0000-4000-8000-00000000000a',b:'00000000-0000-4000-8000-00000000000b',c:'00000000-0000-4000-8000-00000000000c',p:'00000000-0000-4000-8000-0000000000aa',q:'00000000-0000-4000-8000-0000000000bb'};
 await db.exec(`insert into auth.users values ('${U.a}',null,true),('${U.b}',null,true),('${U.c}',null,true),('${U.p}','p@example.dk',false)`);
 // kør som en bestemt bruger (som PostgREST gør det)
 const as=async(u,q,params)=>{const anon=u!=='p'&&u!=='q';await db.exec('begin');try{await db.exec(`set local role authenticated; set local "request.jwt.claim.sub"='${U[u]}'; set local "request.jwt.claims"='${JSON.stringify({sub:U[u],is_anonymous:anon})}'`);const r=await db.query(q,params);await db.exec('commit');return r}catch(e){await db.exec('rollback');return {err:e.message}}};
 const adm=q=>db.query(q);
 let r;
 r=await as('a',`insert into beers(id,name,data) values('b1','Testøl','{}')`);ok('A opretter en øl',!r.err,r.err);
 r=await as('a',`insert into reviews(id,beer,who,data) values('r1','b1','Lucas','{"s":{"look":4}}')`);ok('A bedømmer den',!r.err,r.err);
 // enig/uenig
 r=await as('b',`insert into review_votes(review,v) values('r1',1)`);ok('B stemmer enig',!r.err,r.err);
 r=await as('c',`insert into review_votes(review,v) values('r1',-1)`);ok('C stemmer uenig',!r.err,r.err);
 r=await as('a',`insert into review_votes(review,v) values('r1',1)`);ok('A kan ikke stemme på sin egen bedømmelse',!!r.err&&/row-level security/.test(r.err),r.err);
 r=await as('b',`insert into review_votes(review,v) values('r1',-1) on conflict (review,owner) do update set v=excluded.v`);ok('B kan skifte mening',!r.err,r.err);
 r=await as('b',`insert into review_votes(review,v) values('r1',5)`);ok('kun 1 og -1 er gyldige',!!r.err);
 r=await as('b',`select * from review_votes`);ok('B ser kun sin egen stemme',r.rows&&r.rows.length===1&&r.rows[0].owner===U.b,JSON.stringify(r));
 r=await as('a',`select * from review_vote_counts`);ok('alle ser tallene: 0 enige, 2 uenige',r.rows&&r.rows.length===1&&r.rows[0].enig===0&&r.rows[0].uenig===2,JSON.stringify(r));
 r=await as('c',`update review_votes set owner='${U.b}' where review='r1'`);ok('man kan ikke give sin stemme til en anden',!!r.err&&/row-level security/.test(r.err),JSON.stringify(r));
 // mailvalg
 r=await as('p',`insert into mail_prefs(news,my_beer,friends,events,name,lang,follows) values(false,true,true,true,'P','da','{Magnus}') on conflict (user_id) do update set my_beer=excluded.my_beer,friends=excluded.friends,events=excluded.events,follows=excluded.follows`);ok('konto gemmer mailvalg',!r.err,r.err);
 r=await as('p',`insert into mail_prefs(news) values(true) on conflict (user_id) do update set news=excluded.news`);ok('konto retter mailvalg',!r.err,r.err);
 r=await as('p',`update mail_prefs set unsub=gen_random_uuid()`);ok('afmeld-nøglen kan ikke ændres af brugeren',!!r.err&&/permission denied/.test(r.err),r.err);
 r=await as('p',`update mail_prefs set last_sent=now()`);ok('tidspunktet for sidste mail kan ikke ændres af brugeren',!!r.err&&/permission denied/.test(r.err),r.err);
 r=await as('b',`insert into mail_prefs(news) values(true)`);ok('anonyme kan ikke få mailvalg',!!r.err&&/row-level security/.test(r.err),r.err);
 r=await as('b',`select * from mail_prefs`);ok('andre kan ikke se mine mailvalg',r.rows&&r.rows.length===0,JSON.stringify(r));
 r=await as('b',`select * from mail_queue`);ok('ingen kan læse mail-køen',r.rows&&r.rows.length===0,JSON.stringify(r));
 // det, der følger kontoen (navn, ønskeliste, følger)
 r=await as('p',`insert into konto_data(data) values('{"me":"P","wish":["b1"],"follow":["Magnus"]}')`);ok('konto gemmer navn, ønskeliste og følger',!r.err,r.err);
 r=await as('p',`insert into konto_data(data) values('{"wish":[]}') on conflict (user_id) do update set data=excluded.data,updated_at=now()`);ok('konto retter sine ting',!r.err,r.err);
 r=await as('b',`insert into konto_data(data) values('{}')`);ok('anonyme kan ikke gemme på en konto',!!r.err&&/row-level security/.test(r.err),r.err);
 r=await as('b',`select * from konto_data`);ok('andre kan ikke se det, der ligger på min konto',r.rows&&r.rows.length===0,JSON.stringify(r));
 r=await as('b',`update konto_data set data='{"hack":1}'`);ok('...og ikke rette det',!r.err&&r.affectedRows===0&&(await adm(`select data from konto_data`)).rows[0].data.hack===undefined,JSON.stringify(r));
 r=await as('p',`update konto_data set data=jsonb_build_object('x',repeat('a',70000))`);ok('en alt for stor klump afvises',!!r.err,JSON.stringify(r).slice(0,80));
 r=await as('p',`update konto_data set data='[1,2]'`);ok('kun et objekt er gyldigt',!!r.err,JSON.stringify(r).slice(0,80));
 // triggere: P ejer en øl og en tur, C (Magnus) bedømmer og melder sig til
 await as('p',`insert into beers(id,name,data) values('bp','Kontoøl','{}')`);await as('p',`insert into tours(id,data) values('t1','{"name":"Julefrokost"}')`);await as('p',`insert into tastings(id,data) values('s1','{"name":"Smagning"}')`);
 r=await as('c',`insert into reviews(id,beer,who,data) values('r3','bp','magnus','{"s":{"look":5}}')`);ok('C bedømmer kontoens øl',!r.err,r.err);
 r=await adm(`select kind,data from mail_queue where user_id='${U.p}' order by kind`);ok('kø: både "min øl" og "ven" til kontoen',r.rows.length===2&&r.rows[0].kind==='friends'&&r.rows[1].kind==='my_beer'&&r.rows[1].data.beer==='Kontoøl'&&r.rows[1].data.who==='magnus',JSON.stringify(r.rows));
 r=await as('p',`insert into reviews(id,beer,who,data) values('r4','bp','P','{}')`);r=await adm(`select count(*)::int n from mail_queue`);ok('egen bedømmelse giver ingen mail',r.rows[0].n===2,r.rows[0].n);
 await as('c',`insert into tour_members(tour,name) values('t1','Magnus')`);await as('c',`insert into tasting_votes(tasting,who,data) values('s1','Magnus','{"v":[4]}')`);await as('p',`insert into tour_members(tour,name) values('t1','P')`);
 r=await adm(`select data from mail_queue where kind='events' order by id`);ok('kø: tilmelding til tur og stemme i smagning, men ikke værtens egen',r.rows.length===2&&r.rows[0].data.type==='tour'&&r.rows[0].data.name==='Julefrokost'&&r.rows[1].data.type==='tasting',JSON.stringify(r.rows));
 // ---------- 004: udsendelsen. Funktionen "mails" køres her i Node mod den samme database ----------
 r=await as('b',`select mail_hent('${U.a}')`);ok('brugere kan ikke kalde mail_hent',!!r.err&&/permission denied/.test(r.err),JSON.stringify(r));
 r=await as('b',`select mail_faerdig('${U.a}','{1}',1)`);ok('brugere kan ikke kalde mail_faerdig',!!r.err&&/permission denied/.test(r.err),JSON.stringify(r));
 r=await as('b',`select * from mail_state`);ok('brugere kan ikke læse nøglen til udsendelsen',!!r.err||r.rows.length===0,JSON.stringify(r));
 const CK=(await adm(`select cron_key from mail_state`)).rows[0].cron_key;
 const ENV={SUPABASE_URL:'https://db.test',SUPABASE_SECRET_KEYS:'{"default":"sb_secret_test"}',SUPABASE_SERVICE_ROLE_KEY:'gammel-noegle',RESEND_API_KEY:'re_test'};
 const SIG={mail_hent:['$1::uuid,$2::int',a=>[a.k,a.n]],mail_faerdig:['$1::uuid,$2::bigint[],$3::int',a=>[a.k,'{'+a.ids.join(',')+'}',a.r]],mail_afmeld:['$1::uuid',a=>[a.u]]};
 const outbox=[];let resend=()=>200,handler=null,dbKeys=[];
 globalThis.Deno={env:{get:k=>ENV[k]},serve:h=>{handler=h}};
 globalThis.fetch=async(url,o={})=>{url=String(url);
  if(url.startsWith('https://db.test/rest/v1/rpc/')){const fn=url.split('/').pop(),a=JSON.parse(o.body||'{}');dbKeys.push(o.headers.apikey);
   if(o.headers.apikey!=='sb_secret_test'||o.headers.Authorization!=='Bearer sb_secret_test')return new Response('{}',{status:401});
   if(!SIG[fn])return new Response('{}',{status:404});
   await db.exec('begin');try{await db.exec('set local role service_role');const q=await db.query(`select public.${fn}(${SIG[fn][0]}) v`,SIG[fn][1](a));await db.exec('commit');return new Response(JSON.stringify(q.rows[0].v??null),{status:200})}
   catch(e){await db.exec('rollback');return new Response(JSON.stringify({message:e.message}),{status:/forkert/.test(e.message)?403:400})}}
  if(url==='https://api.resend.com/emails'){const b=JSON.parse(o.body),st=resend(b);if(st===200)outbox.push({...b,key:o.headers['Idempotency-Key'],auth:o.headers.Authorization});return new Response('{"id":"x"}',{status:st})}
  throw new Error('uventet kald til '+url)};
 const tmp=path.join(os.tmpdir(),'olrating-mails-'+process.pid+'.mjs');fs.writeFileSync(tmp,fs.readFileSync(R+'functions/mails/index.ts','utf8'));
 await import(pathToFileURL(tmp).href);fs.unlinkSync(tmp);
 const FN='https://db.test/functions/v1/mails';
 const run=async(key=CK)=>{const x=await handler(new Request(FN,{method:'POST',headers:key?{'x-cron-key':key,'Content-Type':'application/json'}:{},body:'{"action":"send"}'}));return {status:x.status,...(await x.json())}};
 const old=(u,what='last_sent')=>adm(`update mail_prefs set ${what}=${what==='last_sent'?"now()-interval '2 hours'":"current_date-1"} where user_id='${U[u]}'`);
 ok('funktionen kan indlæses og bruger ingen pakker',typeof handler==='function');
 r=await run('');ok('uden nøgle: afvist',r.status===401&&outbox.length===0,JSON.stringify(r));
 r=await run(U.a);ok('med forkert nøgle: afvist, og intet er sendt',r.status===403&&outbox.length===0,JSON.stringify(r));
 r=await adm(`select count(*)::int n from mail_queue where taken_at is not null or sent_at is not null`);ok('forkert nøgle rører ikke køen',r.rows[0].n===0,r.rows[0].n);
 delete ENV.RESEND_API_KEY;r=await run();ok('uden nøgle til mailtjenesten: fejl, og køen er urørt',r.status===500&&outbox.length===0&&(await adm(`select count(*)::int n from mail_queue where taken_at is not null`)).rows[0].n===0,JSON.stringify(r));ENV.RESEND_API_KEY='re_test';
 ENV.MAIL_REPLY_TO='svar@example.dk';r=await run();delete ENV.MAIL_REPLY_TO;let m=outbox[0]||{};const PU=(await adm(`select unsub from mail_prefs where user_id='${U.p}'`)).rows[0].unsub;
 ok('første kørsel: én samlet mail til kontoen',r.status===200&&r.sent===1&&outbox.length===1&&m.to[0]==='p@example.dk'&&m.auth==='Bearer re_test',JSON.stringify(r));
 ok('afsender er sidens adresse, og svar kan sendes til en valgfri indbakke',m.from==='ølrating.dk <hej@xn--lrating-p1a.dk>'&&m.reply_to==='svar@example.dk',JSON.stringify([m.from,m.reply_to]));
 ok('databasen blev kaldt med den nye slags nøgle',dbKeys.length>0&&dbKeys.every(k=>k==='sb_secret_test'),dbKeys.join());
 ok('emne og hilsen på dansk',m.subject==='Nyt fra ølrating.dk: 3 ting siden sidst'&&m.html.includes('Hej P')&&m.html.includes('lang="da"'),m.subject);
 ok('samme bedømmelse nævnes kun én gang, med link til øllen',(m.html.match(/Kontoøl/g)||[]).length===1&&m.html.includes('<b>magnus</b> har bedømt <a href="https://xn--lrating-p1a.dk/#beer-bp"')&&m.html.includes('som du har tilføjet'),m.html);
 ok('byttur og smagning er med, med links',m.html.includes('#byttur-t1')&&m.html.includes('har meldt sig til din byttur')&&m.html.includes('#smagning-s1')&&m.html.includes('har stemt i din smagning'),m.html);
 ok('afmeld-link i mailen og som knap i mailprogrammet',m.html.includes(`https://xn--lrating-p1a.dk/#afmeld-${PU}`)&&m.headers['List-Unsubscribe']===`<${FN}?unsub=${PU}>`&&m.headers['List-Unsubscribe-Post']==='List-Unsubscribe=One-Click',JSON.stringify(m.headers));
 ok('mailen findes også som ren tekst',m.text.includes('magnus har bedømt Kontoøl, som du har tilføjet: https://xn--lrating-p1a.dk/#beer-bp')&&m.text.includes('Afmeld alle mails: '),m.text);
 r=await adm(`select (select count(*)::int from mail_queue where sent_at is null) q,(select last_sent is not null and friends_sent=(now() at time zone 'Europe/Copenhagen')::date from mail_prefs where user_id='${U.p}') p`);
 ok('køen er kvitteret, og tidspunktet er husket',r.rows[0].q===0&&r.rows[0].p===true,JSON.stringify(r.rows));
 // højst én mail i timen, venner højst én gang om dagen
 await as('c',`insert into reviews(id,beer,who,data) values('r5','bp','magnus','{}')`);
 r=await run();ok('inden for en time: ingen ny mail',r.sent===0&&outbox.length===1,JSON.stringify(r));
 await old('p');r=await run();m=outbox[1]||{};
 ok('en time efter: "min øl" sendes, og emnet er selve hændelsen',r.sent===1&&m.subject==='magnus har bedømt Kontoøl, som du har tilføjet',m.subject);
 r=await adm(`select kind from mail_queue where sent_at is null`);ok('"ven" venter til i morgen (højst én om dagen)',r.rows.length===1&&r.rows[0].kind==='friends',JSON.stringify(r.rows));
 await old('p');await old('p','friends_sent');r=await run();m=outbox[2]||{};
 ok('dagen efter: mailen om vennen (uden svar-adresse, når den ikke er sat)',r.sent===1&&m.subject==='magnus, som du følger, har bedømt Kontoøl'&&!('reply_to' in m),m.subject);
 // fravalg efter at noget er lagt i kø
 await as('b',`insert into tour_members(tour,name) values('t1','Ole')`);await as('p',`update mail_prefs set events=false`);await old('p');
 r=await run();ok('slået fra siden sidst: sendes ikke og fjernes fra køen',r.sent===0&&(await adm(`select count(*)::int n from mail_queue where sent_at is null`)).rows[0].n===0,JSON.stringify(r));
 // nyheder: kladde først, flueben i "send" lægger den i kø. Q læser engelsk.
 await adm(`insert into auth.users values ('${U.q}','q@example.com',false)`);
 r=await as('q',`insert into mail_prefs(news,my_beer,name,lang) values(true,true,'Quinn <b>','en')`);ok('en engelsk konto slår nyheder til',!r.err,r.err);
 await adm(`insert into mail_news(subject_da,body_da,subject_en,body_en) values('Nyt: enig eller uenig','Hej <script>alert(1)</script>\n\nLæs mere på https://xn--lrating-p1a.dk/#nyt.\nVi ses','New: agree or disagree','Read more at https://xn--lrating-p1a.dk/#nyt.')`);
 r=await adm(`select count(*)::int n from mail_queue where kind='news'`);ok('en nyhed uden flueben er en kladde',r.rows[0].n===0,r.rows[0].n);
 await adm(`update mail_news set send=true`);r=await adm(`select count(*)::int n from mail_queue where kind='news' and sent_at is null`);ok('flueben i "send": i kø til de to, der har slået nyheder til',r.rows[0].n===2,r.rows[0].n);
 await adm(`update mail_news set body_da=body_da||'!'`);r=await adm(`select count(*)::int n from mail_queue where kind='news'`);ok('en rettelse bagefter sender den ikke igen',r.rows[0].n===2,r.rows[0].n);
 await old('p');r=await run();const nd=outbox.find((x,i)=>i>2&&x.to[0]==='p@example.dk')||{},ne=outbox.find(x=>x.to[0]==='q@example.com')||{};
 ok('nyheden er sendt til begge',r.sent===2&&outbox.length===5,JSON.stringify(r));
 ok('dansk nyhed: emne, afsnit og klikbart link',nd.subject==='Nyt: enig eller uenig'&&nd.html.includes('<a href="https://xn--lrating-p1a.dk/#nyt"')&&nd.html.includes('.<br>Vi ses!'),nd.html);
 ok('kode i en nyhed bliver vist som tekst',nd.html.includes('&lt;script&gt;')&&!nd.html.includes('<script>'),nd.html);
 ok('engelsk nyhed til den engelske konto, og navnet kan ikke indsætte kode',ne.subject==='New: agree or disagree'&&ne.html.includes('Hi Quinn &lt;b&gt;')&&!ne.html.includes('Quinn <b>')&&ne.html.includes('Unsubscribe from all emails')&&ne.html.includes('lang="en"'),ne.html);
 // mailtjenesten siger nej
 await adm(`insert into mail_queue(user_id,kind,data) values('${U.q}','my_beer','{"who":"Ib","beer":"Stout & Co","id":"b9"}')`);await old('q');
 resend=()=>429;r=await run();let q=(await adm(`select taken_at,sent_at from mail_queue where sent_at is null`)).rows;
 ok('mailtjenesten er optaget: prøves igen ved næste kørsel',r.sent===0&&r.later===1&&q.length===1&&q[0].taken_at===null,JSON.stringify([r,q]));
 resend=()=>422;r=await run();q=(await adm(`select (select count(*)::int from mail_queue where sent_at is null and taken_at is null) n,(select last_sent>now()-interval '1 minute' from mail_prefs where user_id='${U.q}') w`)).rows[0];
 ok('afvist af mailtjenesten: prøves først igen om en time',r.failed===1&&q.n===1&&q.w===true,JSON.stringify([r,q]));
 resend=()=>200;r=await run();ok('...og ikke før',r.sent===0,JSON.stringify(r));
 await old('q');await adm(`update mail_queue set taken_at=now()-interval '31 minutes' where sent_at is null`);
 r=await run();m=outbox[5]||{};ok('en udsendelse, der gik i stå, bliver taget op igen (engelsk, tegn i navnet er sikre)',r.sent===1&&m.subject==='Ib rated Stout & Co, which you added'&&m.html.includes('Stout &amp; Co'),JSON.stringify([r,m.subject]));
 // afmelding
 const QU=(await adm(`select unsub from mail_prefs where user_id='${U.q}'`)).rows[0].unsub;
 let x=await handler(new Request(FN+'?unsub='+QU));ok('link i mailen: sendes videre til afmeld-siden, intet er ændret endnu',x.status===302&&x.headers.get('location')===`https://xn--lrating-p1a.dk/#afmeld-${QU}`&&(await adm(`select news from mail_prefs where user_id='${U.q}'`)).rows[0].news===true,x.status);
 x=await handler(new Request(FN+'?unsub=ikke-en-noegle',{method:'POST'}));ok('ugyldig afmeld-nøgle: afvist',x.status===400,x.status);
 await adm(`insert into mail_queue(user_id,kind,data) values('${U.q}','my_beer','{"who":"Ib","beer":"X","id":"b9"}')`);
 x=await handler(new Request(FN+'?unsub='+QU,{method:'POST',body:'List-Unsubscribe=One-Click'}));const xj=await x.json();
 r=await adm(`select (select news or my_beer or friends or events from mail_prefs where user_id='${U.q}') any_on,(select count(*)::int from mail_queue where user_id='${U.q}' and sent_at is null) n`);
 ok('afmeld med ét klik: alt er slået fra, og køen er tømt',x.status===200&&xj.ok===true&&r.rows[0].any_on===false&&r.rows[0].n===0,JSON.stringify([xj,r.rows]));
 r=await as('b',`select mail_afmeld('${PU}') v`);ok('afmeld-siden kan afmelde uden login, når nøglen er rigtig',r.rows&&r.rows[0].v===true&&(await adm(`select news from mail_prefs where user_id='${U.p}'`)).rows[0].news===false,JSON.stringify(r));
 r=await as('b',`select mail_afmeld('${U.a}') v`);ok('en ukendt nøgle afmelder ingen',r.rows&&r.rows[0].v===false,JSON.stringify(r));
 await as('p',`update mail_prefs set news=true,my_beer=true,friends=true,events=true`);await adm(`delete from auth.users where id='${U.q}'`);
 // loft over køen: ingen kan fylde en andens kø op
 await adm(`insert into mail_queue(user_id,kind,data) select '${U.p}','events','{}' from generate_series(1,200)`);
 await as('b',`insert into tour_members(tour,name) values('t1','Spam')`);await as('c',`insert into reviews(id,beer,who,data) values('r6','bp','magnus','{}')`);
 r=await adm(`select count(*)::int n from mail_queue where user_id='${U.p}' and sent_at is null`);ok('højst 200 ventende mails pr. bruger, og bedømmelsen blev gemt alligevel',r.rows[0].n===200&&(await adm(`select count(*)::int n from reviews where id='r6'`)).rows[0].n===1,r.rows[0].n);
 await adm(`delete from mail_queue where user_id='${U.p}' and sent_at is null`);
 r=await as('b',`select mail_plads('${U.p}')`);ok('brugere kan ikke kalde hjælpefunktionen',!!r.err&&/permission denied/.test(r.err),JSON.stringify(r));
 // flyt data fra anonym enhed til kontoen
 r=await as('p',`select konto_flyt_start()`);ok('en rigtig konto kan ikke hente flyttebevis',!!r.err,JSON.stringify(r));
 r=await as('a',`select konto_flyt_start() t`);const tok=r.rows&&r.rows[0].t;ok('A henter flyttebevis',!!tok,r.err);
 r=await as('b',`select konto_flyt_slut('${tok}')`);ok('en anden anonym kan ikke bruge beviset',!!r.err,JSON.stringify(r));
 r=await as('p',`select konto_flyt_slut('00000000-0000-4000-8000-0000000000ff')`);ok('et ukendt bevis afvises',!!r.err);
 await as('p',`insert into review_votes(review,v) values('r1',1)`);   // kontoen har stemt på A's bedømmelse, som om lidt bliver kontoens egen
 r=await as('p',`select konto_flyt_slut('${tok}') n`);ok('kontoen overtager A\'s øl og bedømmelse (2 rækker)',r.rows&&r.rows[0].n===2,JSON.stringify(r));
 r=await adm(`select (select owner from beers where id='b1') b,(select owner from reviews where id='r1') r,(select count(*)::int from auth.users where id='${U.a}') u,(select count(*)::int from review_votes where review='r1' and owner='${U.p}') v`);
 ok('ejeren er skiftet, den anonyme bruger er væk, og kontoens stemme på egen bedømmelse er fjernet',r.rows[0].b===U.p&&r.rows[0].r===U.p&&r.rows[0].u===0&&r.rows[0].v===0,JSON.stringify(r.rows));
 r=await as('p',`select konto_flyt_slut('${tok}')`);ok('beviset kan kun bruges én gang',!!r.err);
 r=await as('p',`update beers set name='Rettet' where id='b1'`);ok('kontoen kan nu rette øllen',!r.err&&r.affectedRows===1,JSON.stringify(r));
 // besøgstæller (005)
 r=await as('a',`select besoeg() v`);const v1=r.rows&&r.rows[0].v;r=await as('b',`select besoeg() v`);const v2=r.rows&&r.rows[0].v;
 ok('besoeg() lægger 1 til og svarer med i alt, i dag og første dag',v1&&v2&&Number(v1.total)===1&&Number(v2.total)===2&&Number(v2.today)===2&&Number(v2.week)===2&&/^\d{4}-\d\d-\d\d$/.test(v2.since),JSON.stringify([v1,v2]));
 r=await as('c',`select besoeg_tal() v`);ok('besoeg_tal() læser uden at tælle',r.rows&&Number(r.rows[0].v.total)===2&&Number((await adm(`select sum(visits)::int n from site_visits`)).rows[0].n)===2,JSON.stringify(r));
 await adm(`insert into site_visits values (current_date-30, 40)`);r=await as('c',`select besoeg_tal() v`);ok('ældre dage tæller med i alt, men ikke i dag eller i ugen',r.rows&&Number(r.rows[0].v.total)===42&&Number(r.rows[0].v.today)===2&&Number(r.rows[0].v.week)===2,JSON.stringify(r));
 r=await as('a',`select * from site_visits`);const r2=await as('a',`update site_visits set visits=999999`);const r3=await as('a',`insert into site_visits values (current_date-1, 5)`);
 ok('tabellen kan ikke læses eller ændres direkte',!!r.err&&!!r2.err&&!!r3.err&&Number((await adm(`select sum(visits)::int n from site_visits`)).rows[0].n)===42,JSON.stringify([r.err,r2.err,r3.err]));
 // slet konto
 r=await as('p',`select konto_slet()`);ok('slet konto',!r.err,r.err);
 r=await adm(`select (select count(*)::int from auth.users where id='${U.p}') u,(select count(*)::int from mail_prefs) p,(select count(*)::int from mail_queue) q,(select count(*)::int from konto_data) k,(select count(*)::int from beers where owner='${U.p}') b`);
 ok('login, mailvalg, kø og kontoens egne ting er væk, øllene står tilbage',r.rows[0].u===0&&r.rows[0].p===0&&r.rows[0].q===0&&r.rows[0].k===0&&r.rows[0].b===2,JSON.stringify(r.rows));
 console.log(fail?`${fail} FEJL af ${pass+fail}`:`ALT OK (${pass})`);process.exit(fail?1:0)})().catch(e=>{console.log('CRASH',e.message);process.exit(1)});
