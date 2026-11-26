"""Efterligning af Supabase i hukommelsen (login, tabeller med ejer-regler, billedlager). Bruges af testene, så de ikke rører den rigtige database."""
import json, re, base64
from urllib.parse import urlparse, parse_qs, unquote
HOST='bbcegrufmzgfgzxazldr.supabase.co'
KEY='sb_publishable_mf5v3jp_xYx7wJj1lgCr-Q_JUFuzXOY'
JPG=base64.b64decode('/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIfIiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAAQABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCaiiivlT6Y/9k=')   # et lille, gyldigt JPEG-billede (16 x 16). Firefox melder fejl ved et afkortet billede
CORS={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'}
class Mock:
    def __init__(s):
        s.n=0; s.tok={}; s.ref={}; s.t={'beers':{},'reviews':{},'tours':{},'tastings':{}}; s.members={}; s.votes={}; s.store={}; s.log=[]; s.down=False
        # konto: brugere, mails der "sendes" (koden er altid 123456 for ny konto og 654321 for login), mailvalg og flytning af data
        s.users={}; s.emails={}; s.mails=[]; s.prefs={}; s.unsub={}; s.kdata={}; s.has_kdata=True; s.flyt={}; s.mail_limit=False; s.has_konto_sql=True; s.no_konto=set()   # no_konto: brugere, der skal opleve en database uden 003
        s.rvotes={}   # enig/uenig: (bedømmelse, bruger) -> 1 eller -1
        s.has_besoeg=True; s.visits=1000; s.visits_today=4   # besøgstæller (supabase/005)
    def user(s,uid):
        u=s.users.get(uid,{}); return {'id':uid,'is_anonymous':not u.get('email'),**({'email':u['email']} if u.get('email') else {})}
    def sess(s,uid,n):
        return {'access_token':f'tok{n}','refresh_token':f'ref{n}','expires_in':3600,'token_type':'bearer','user':s.user(uid)}
    def new_sess(s,uid):
        s.n+=1; se=s.sess(uid,s.n); s.tok[se['access_token']]=uid; s.ref[se['refresh_token']]=(uid,s.n); return se
    def handle(s,route,req):
        u=urlparse(req.url); path=u.path; q={k:v[0] for k,v in parse_qs(u.query).items()}; m=req.method
        def out(code,body=None,ct='application/json',raw=None):
            route.fulfill(status=code,headers={**CORS,'content-type':ct},body=raw if raw is not None else ('' if body is None else json.dumps(body)))
        if s.down: return route.abort()
        if m=='OPTIONS': return out(204)
        s.log.append(f'{m} {path}?{u.query}'[:140])
        if req.headers.get('apikey')!=KEY and not path.startswith('/storage/v1/object/public/'): return out(401,{'message':'No API key'})
        bearer=(req.headers.get('authorization') or '').replace('Bearer ','')
        uid=s.tok.get(bearer)
        body=None
        if m in('POST','PATCH','PUT') and not path.startswith('/storage'):
            try: body=json.loads(req.post_data or '{}')
            except Exception: body={}
        if path=='/auth/v1/signup':
            s.n+=1; uid=f'00000000-0000-4000-8000-{s.n:012d}'; s.users[uid]={'email':None,'pending':None}; se=s.sess(uid,s.n); s.tok[se['access_token']]=uid; s.ref[se['refresh_token']]=(uid,s.n); return out(200,se)
        if path=='/auth/v1/token':
            r=s.ref.get(body.get('refresh_token'))
            if not r or r[0] not in s.users: return out(400,{'error':'invalid_grant'})
            return out(200,s.sess(*r))
        # --- konto: mail på den anonyme bruger, login med kode, log ud
        if path=='/auth/v1/user' and m=='PUT':
            if not uid: return out(401,{'msg':'no session'})
            em=(body.get('email') or '').lower()
            if s.mail_limit: return out(429,{'code':429,'error_code':'over_email_send_rate_limit','msg':'email rate limit exceeded'})
            if em in s.emails and s.emails[em]!=uid: return out(422,{'code':422,'error_code':'email_exists','msg':'A user with this email address has already been registered'})
            s.users[uid]['pending']=em; s.mails.append((em,'email_change','123456')); return out(200,s.user(uid))
        if path=='/auth/v1/otp' and m=='POST':
            em=(body.get('email') or '').lower()
            if s.mail_limit: return out(429,{'code':429,'error_code':'over_email_send_rate_limit','msg':'email rate limit exceeded'})
            if em not in s.emails: return out(422,{'code':422,'error_code':'otp_disabled','msg':'Signups not allowed for otp'})
            s.mails.append((em,'magiclink','654321')); return out(200,{})
        if path=='/auth/v1/verify' and m=='POST':
            em=(body.get('email') or '').lower(); bad=lambda: out(403,{'code':403,'error_code':'otp_expired','msg':'Token has expired or is invalid'})
            if body.get('type')=='email_change':
                u=[k for k,v in s.users.items() if v.get('pending')==em]
                if not u or body.get('token')!='123456': return bad()
                s.users[u[0]].update(email=em,pending=None); s.emails[em]=u[0]; return out(200,s.new_sess(u[0]))
            if body.get('type')=='email':
                if em not in s.emails or body.get('token')!='654321': return bad()
                return out(200,s.new_sess(s.emails[em]))
            return bad()
        if path=='/auth/v1/logout' and m=='POST':
            s.tok.pop(bearer,None); return out(204)
        mr=re.match(r'^/rest/v1/rpc/(\w+)$',path)
        if mr:
            fn=mr.group(1); anon=bool(uid) and not s.users.get(uid,{}).get('email')
            if fn in ('besoeg','besoeg_tal'):   # kræver ikke login og afhænger ikke af 003
                if not s.has_besoeg: return out(404,{'code':'PGRST202','message':'Could not find the function'})
                if fn=='besoeg': s.visits+=1; s.visits_today+=1
                return out(200,{'total':s.visits,'today':s.visits_today,'week':s.visits_today,'since':'2026-11-26'})
            if not s.has_konto_sql or uid in s.no_konto: return out(404,{'code':'PGRST202','message':'Could not find the function'})
            if fn=='mail_afmeld':   # kræver ikke login: nøglen i linket er adgangen
                who=[u for u,t in s.unsub.items() if t==body.get('u') and u in s.prefs]
                for u in who: s.prefs[u].update(news=False,my_beer=False,friends=False,events=False)
                return out(200,bool(who))
            if not uid: return out(401,{'code':'42501'})
            if fn=='konto_flyt_start':
                if not anon: return out(400,{'message':'kun anonyme brugere'})
                t=f'00000000-0000-4000-9000-{len(s.flyt)+1:012d}'; s.flyt[t]=uid; return out(200,t)
            if fn=='konto_flyt_slut':
                f=s.flyt.pop(body.get('t'),None)
                if anon or not f: return out(400,{'message':'ukendt eller udløbet'})
                n=0
                for T in s.t.values():
                    for r in T.values():
                        if r['owner']==f: r['owner']=uid; n+=1
                for k,o in list(s.members.items()):
                    if o==f: s.members[k]=uid
                for v in s.votes.values():
                    if v['owner']==f: v['owner']=uid
                for (r,o),v in list(s.rvotes.items()):
                    if o==f:
                        del s.rvotes[(r,o)]
                        if (r,uid) not in s.rvotes and s.t['reviews'].get(r,{}).get('owner')!=uid: s.rvotes[(r,uid)]=v
                s.users.pop(f,None); return out(200,n)
            if fn=='konto_slet':
                em=s.users.get(uid,{}).get('email'); s.emails.pop(em,None); s.users.pop(uid,None); s.prefs.pop(uid,None); s.kdata.pop(uid,None); return out(204)
            return out(404,{'message':'no function'})
        if path in('/rest/v1/review_votes','/rest/v1/review_vote_counts'):
            if not s.has_konto_sql or uid in s.no_konto: return out(404,{'code':'PGRST205','message':'Could not find the table'})
            if path.endswith('counts'):
                c={}
                for (r,o),v in s.rvotes.items(): c.setdefault(r,[0,0])[0 if v==1 else 1]+=1
                return out(200,[{'review':r,'enig':a,'uenig':d} for r,(a,d) in c.items()])
            if m=='GET': return out(200,[{'review':r,'v':v} for (r,o),v in s.rvotes.items() if o==uid])
            if m=='POST':
                r=body.get('review'); rv=s.t['reviews'].get(r)
                if not uid: return out(401,{'code':'42501'})
                if not rv: return out(409,{'code':'23503'})
                if rv['owner']==uid or body.get('v') not in(1,-1): return out(403,{'code':'42501','message':'new row violates row-level security policy'})
                s.rvotes[(r,uid)]=body['v']; return out(201)
            if m=='DELETE':
                s.rvotes.pop((q.get('review','')[3:],uid),None); return out(204)
        if path=='/rest/v1/konto_data':
            if not s.has_konto_sql or uid in s.no_konto or not s.has_kdata: return out(404,{'code':'PGRST205','message':'Could not find the table'})
            if m=='GET': return out(200,[{'data':s.kdata[uid]}] if uid in s.kdata else [])
            if m=='POST':
                if not uid or not s.users.get(uid,{}).get('email'): return out(403,{'code':'42501','message':'rls'})
                s.kdata[uid]=body.get('data') or {}; return out(201)
        if path=='/rest/v1/mail_prefs':
            if not s.has_konto_sql or uid in s.no_konto: return out(404,{'code':'PGRST205','message':'Could not find the table'})
            if m=='GET': return out(200,[s.prefs[uid]] if uid in s.prefs else [])
            if m=='POST':
                if not uid or not s.users.get(uid,{}).get('email'): return out(403,{'code':'42501','message':'rls'})
                s.prefs[uid]={**s.prefs.get(uid,{}),**body}; s.unsub.setdefault(uid,f'00000000-0000-4000-a000-{len(s.unsub)+1:012d}'); return out(201)
        mt=re.match(r'^/rest/v1/(\w+)$',path)
        if mt:
            tb=mt.group(1)
            def flt(rows):
                for k,v in q.items():
                    if k in('select','order','limit','on_conflict'): continue
                    if v.startswith('eq.'): rows=[r for r in rows if str(r.get(k))==v[3:]]
                    elif v.startswith('in.('): vals=v[4:-1].split(','); rows=[r for r in rows if str(r.get(k)) in vals]
                return rows
            if tb=='tour_members':
                if m=='DELETE':
                    for (t,n),o in list(s.members.items()):
                        if str(t)==q.get('tour','')[3:] and n==q.get('name','')[3:] and (o==uid or s.t['tours'].get(t,{}).get('owner')==uid): del s.members[(t,n)]
                    return out(204)
                rows=[{'tour':t,'name':n,'owner':o} for (t,n),o in s.members.items()]
                if m=='GET': return out(200,flt(rows))
                if m=='POST':
                    if not uid: return out(401,{'code':'42501'})
                    if body['tour'] not in s.t['tours']: return out(409,{'code':'23503'})
                    s.members.setdefault((body['tour'],body['name']),uid); return out(201)
            if tb=='tasting_votes':
                rows=[{'tasting':t,'who':w,**v} for (t,w),v in s.votes.items()]
                if m=='GET': return out(200,flt(rows))
                if m=='POST':
                    if not uid: return out(401,{'code':'42501'})
                    if body['tasting'] not in s.t['tastings']: return out(409,{'code':'23503'})
                    k=(body['tasting'],body['who']); ex=s.votes.get(k)
                    if ex and ex['owner']!=uid: return out(403,{'code':'42501'})
                    s.votes[k]={'owner':uid,'data':body.get('data',{})}; return out(201)
                if m=='DELETE':
                    for r in flt(rows):
                        if r['owner']==uid: del s.votes[(r['tasting'],r['who'])]
                    return out(204)
            if tb not in s.t: return out(404,{'message':'no table'})
            T=s.t[tb]
            if m=='GET': return out(200,flt(list(T.values())))
            if m=='POST':
                if not uid: return out(401,{'code':'42501','message':'rls'})
                ex=T.get(body['id'])
                if ex and ex['owner']!=uid: return out(403,{'code':'42501','message':'new row violates row-level security policy'})
                if tb=='reviews' and body['beer'] not in s.t['beers']: return out(409,{'code':'23503'})
                row={**(ex or {'owner':uid,'created_at':f'{len(T):06d}'}),**body}; T[body['id']]=row; return out(201)
            if m=='DELETE':
                for r in flt(list(T.values())):
                    if r['owner']==uid:
                        del T[r['id']]
                        if tb=='tastings':
                            for k in [k for k in s.votes if k[0]==r['id']]: del s.votes[k]
                        if tb=='tours':
                            for k in [k for k in s.members if k[0]==r['id']]: del s.members[k]
                        if tb=='beers':
                            for k in [k for k,v in s.t['reviews'].items() if v['beer']==r['id']]: del s.t['reviews'][k]
                return out(204)
        if path.startswith('/storage/v1/object/public/billeder/'):
            k=unquote(path.split('/billeder/',1)[1])
            return out(200,raw=s.store[k],ct='image/jpeg') if k in s.store else out(404,{})
        if path.startswith('/storage/v1/object/billeder/') and m=='POST':
            k=unquote(path.split('/billeder/',1)[1])
            if not uid or not k.startswith(uid+'/'): return out(403,{'message':'rls'})
            if 'x-upsert' in req.headers: return out(403,{'message':'upsert needs update policy'})
            if k in s.store: return out(400,{'statusCode':'409','error':'Duplicate','message':'The resource already exists'})
            s.store[k]=JPG; return out(200,{'Key':'billeder/'+k})
        if path.startswith('/storage/v1/object/billeder/') and m=='DELETE':
            k=unquote(path.split('/billeder/',1)[1])
            if uid and k.startswith(uid+'/') and k in s.store: del s.store[k]; return out(200,{'message':'Successfully deleted'})
            return out(400,{'error':'not_found'})
        return out(404,{'message':'unhandled '+path})
