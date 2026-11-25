"""Efterligning af Supabase i hukommelsen (login, tabeller med ejer-regler, billedlager). Bruges af testene, så de ikke rører den rigtige database."""
import json, re, base64
from urllib.parse import urlparse, parse_qs, unquote
HOST='bbcegrufmzgfgzxazldr.supabase.co'
KEY='sb_publishable_mf5v3jp_xYx7wJj1lgCr-Q_JUFuzXOY'
JPG=base64.b64decode('/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=')
CORS={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'}
class Mock:
    def __init__(s):
        s.n=0; s.tok={}; s.ref={}; s.t={'beers':{},'reviews':{},'tours':{},'tastings':{}}; s.members={}; s.store={}; s.log=[]; s.down=False
    def sess(s,uid,n):
        return {'access_token':f'tok{n}','refresh_token':f'ref{n}','expires_in':3600,'token_type':'bearer','user':{'id':uid,'is_anonymous':True}}
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
        if m in('POST','PATCH') and not path.startswith('/storage'):
            try: body=json.loads(req.post_data or '{}')
            except Exception: body={}
        if path=='/auth/v1/signup':
            s.n+=1; uid=f'00000000-0000-4000-8000-{s.n:012d}'; se=s.sess(uid,s.n); s.tok[se['access_token']]=uid; s.ref[se['refresh_token']]=(uid,s.n); return out(200,se)
        if path=='/auth/v1/token':
            r=s.ref.get(body.get('refresh_token'))
            if not r: return out(400,{'error':'invalid_grant'})
            return out(200,s.sess(*r))
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
