// Tjekker supabase/003-konto-mails-enig.sql i en rigtig Postgres, der kører i hukommelsen (PGlite): ejer-regler, stemmer,
// flytning af data til en konto, mailvalg og køen med mails. Rører ikke den rigtige database.
// Kør:  npm install --no-save @electric-sql/pglite  og derefter  node tests/test_sql.js
const {PGlite}=require('@electric-sql/pglite');const fs=require('fs');
const path=require('path');const R=path.join(__dirname,'..','supabase')+path.sep;
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
 const U={a:'00000000-0000-4000-8000-00000000000a',b:'00000000-0000-4000-8000-00000000000b',c:'00000000-0000-4000-8000-00000000000c',p:'00000000-0000-4000-8000-0000000000aa'};
 await db.exec(`insert into auth.users values ('${U.a}',null,true),('${U.b}',null,true),('${U.c}',null,true),('${U.p}','p@example.dk',false)`);
 // kør som en bestemt bruger (som PostgREST gør det)
 const as=async(u,q,params)=>{const anon=u!=='p';await db.exec('begin');try{await db.exec(`set local role authenticated; set local "request.jwt.claim.sub"='${U[u]}'; set local "request.jwt.claims"='${JSON.stringify({sub:U[u],is_anonymous:anon})}'`);const r=await db.query(q,params);await db.exec('commit');return r}catch(e){await db.exec('rollback');return {err:e.message}}};
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
 // triggere: P ejer en øl og en tur, C (Magnus) bedømmer og melder sig til
 await as('p',`insert into beers(id,name,data) values('bp','Kontoøl','{}')`);await as('p',`insert into tours(id,data) values('t1','{"name":"Julefrokost"}')`);await as('p',`insert into tastings(id,data) values('s1','{"name":"Smagning"}')`);
 r=await as('c',`insert into reviews(id,beer,who,data) values('r3','bp','magnus','{"s":{"look":5}}')`);ok('C bedømmer kontoens øl',!r.err,r.err);
 r=await adm(`select kind,data from mail_queue where user_id='${U.p}' order by kind`);ok('kø: både "min øl" og "ven" til kontoen',r.rows.length===2&&r.rows[0].kind==='friends'&&r.rows[1].kind==='my_beer'&&r.rows[1].data.beer==='Kontoøl'&&r.rows[1].data.who==='magnus',JSON.stringify(r.rows));
 r=await as('p',`insert into reviews(id,beer,who,data) values('r4','bp','P','{}')`);r=await adm(`select count(*)::int n from mail_queue`);ok('egen bedømmelse giver ingen mail',r.rows[0].n===2,r.rows[0].n);
 await as('c',`insert into tour_members(tour,name) values('t1','Magnus')`);await as('c',`insert into tasting_votes(tasting,who,data) values('s1','Magnus','{"v":[4]}')`);await as('p',`insert into tour_members(tour,name) values('t1','P')`);
 r=await adm(`select data from mail_queue where kind='events' order by id`);ok('kø: tilmelding til tur og stemme i smagning, men ikke værtens egen',r.rows.length===2&&r.rows[0].data.type==='tour'&&r.rows[0].data.name==='Julefrokost'&&r.rows[1].data.type==='tasting',JSON.stringify(r.rows));
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
 // slet konto
 r=await as('p',`select konto_slet()`);ok('slet konto',!r.err,r.err);
 r=await adm(`select (select count(*)::int from auth.users where id='${U.p}') u,(select count(*)::int from mail_prefs) p,(select count(*)::int from mail_queue) q,(select count(*)::int from beers where owner='${U.p}') b`);
 ok('login, mailvalg og kø er væk, øllene står tilbage',r.rows[0].u===0&&r.rows[0].p===0&&r.rows[0].q===0&&r.rows[0].b===2,JSON.stringify(r.rows));
 console.log(fail?`${fail} FEJL af ${pass+fail}`:`ALT OK (${pass})`);process.exit(fail?1:0)})().catch(e=>{console.log('CRASH',e.message);process.exit(1)});
