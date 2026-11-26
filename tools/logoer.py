import math,os,sys,json
from types import SimpleNamespace as NS
NAVY='#0f1d36';NV3='#1d3557';SKY='#8fb6e3';SUN='#ff7a3d';PK='#f0566b';GL='#ffc85a';W='#ffffff'
def star(cx,cy,R,r=None,n=5,rot=-90):
    r=r or R*0.42;pts=[]
    for i in range(n*2):
        a=math.radians(rot+i*180/n);rad=R if i%2==0 else r
        pts.append(f'{cx+rad*math.cos(a):.2f} {cy+rad*math.sin(a):.2f}')
    return 'M'+'L'.join(pts)+'z'
def grad(id,vert=True,stops=((0,PK),(.5,SUN),(1,GL))):
    x2,y2=(0,1) if vert else (1,0)
    return f'<linearGradient id="{id}" x1="0" y1="0" x2="{x2}" y2="{y2}">'+''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o,c in stops)+'</linearGradient>'
def cap(cx,cy,R,r,n=21):
    pts=[]
    for i in range(n*2):
        a=2*math.pi*i/(n*2);rad=R if i%2==0 else r
        pts.append((cx+rad*math.cos(a),cy+rad*math.sin(a)))
    d=f'M{pts[0][0]:.2f} {pts[0][1]:.2f}'
    for i in range(1,len(pts)+1):
        p=pts[i%len(pts)];q=pts[(i-1)%len(pts)];mx,my=(p[0]+q[0])/2,(p[1]+q[1])/2
        d+=f'Q{q[0]:.2f} {q[1]:.2f} {mx:.2f} {my:.2f}'
    return d+'z'
def petal(cx,cy,w,h):
    return f'M{cx} {cy-h/2}C{cx+w*.75} {cy-h*.2} {cx+w*.6} {cy+h*.35} {cx} {cy+h/2}C{cx-w*.6} {cy+h*.35} {cx-w*.75} {cy-h*.2} {cx} {cy-h/2}z'
def P(d,fill=None,stroke=None,sw=0,x=''):
    a=f' fill="{fill}"' if fill else ' fill="none"'
    if stroke: a+=f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'
    return f'<path d="{d}"{a}{x}/>'
def C(cx,cy,r,fill=None,stroke=None,sw=0,x=''):
    a=f' fill="{fill}"' if fill else ' fill="none"'
    if stroke: a+=f' stroke="{stroke}" stroke-width="{sw}"'
    return f'<circle cx="{cx}" cy="{cy}" r="{r}"{a}{x}/>'
def R(x,y,w,h,rx,fill,e=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{e}/>'
def pint(cx,top,wt,wb,h,r=3):
    x0,x1,b0,b1,y1=cx-wt/2,cx+wt/2,cx-wb/2,cx+wb/2,top+h
    return f'M{x0} {top}H{x1}L{b1} {y1-r}Q{b1} {y1} {b1-r} {y1}H{b0+r}Q{b0} {y1} {b0} {y1-r}z'
def bottle(cx,top,h,w):
    nw=w*.38;nh=h*.28;sh=h*.2;y1=top+h;r=4;a=top+nh;b=a+sh
    return f'M{cx-nw/2} {top}h{nw}V{a}C{cx+nw/2} {a+sh*.6} {cx+w/2} {a+sh*.4} {cx+w/2} {b}V{y1-r}Q{cx+w/2} {y1} {cx+w/2-r} {y1}H{cx-w/2+r}Q{cx-w/2} {y1} {cx-w/2} {y1-r}V{b}C{cx-w/2} {a+sh*.4} {cx-nw/2} {a+sh*.6} {cx-nw/2} {a}z'
def oe(cx,cy,r,sw,col,ssw=None):
    k=r+sw*.75
    return C(cx,cy,r,stroke=col,sw=sw)+P(f'M{cx-k*.62:.1f} {cy+k*.86:.1f}L{cx+k*.62:.1f} {cy-k*.86:.1f}',stroke=col,sw=ssw or sw*.85)
def drop(cx,cy,r):
    return f'M{cx} {cy-r*2.1}C{cx+r*.4} {cy-r*1.2} {cx+r} {cy-r*.6} {cx+r} {cy}a{r} {r} 0 0 1 {-2*r} 0C{cx-r} {cy-r*.6} {cx-r*.4} {cy-r*1.2} {cx} {cy-r*2.1}z'
def wave(x0,y,amp,half,n):
    d=f'M{x0} {y}C{x0+half*.35:.1f} {y-amp} {x0+half*.65:.1f} {y-amp} {x0+half} {y}';x=x0+half;s=1
    for i in range(n-1):
        d+=f'S{x+half*.65:.1f} {y+amp*s} {x+half} {y}';x+=half;s=-s
    return d,x
def blob(parts,p,ow=5):
    def sh(t,e):
        if t[0]=='c': return f'<circle cx="{t[1]}" cy="{t[2]}" r="{t[3]}"{e}/>'
        if t[0]=='r': return f'<rect x="{t[1]}" y="{t[2]}" width="{t[3]}" height="{t[4]}" rx="{t[5]}"{e}/>'
        if t[0]=='e': return f'<ellipse cx="{t[1]}" cy="{t[2]}" rx="{t[3]}" ry="{t[4]}"{e}/>'
        return f'<path d="{t[1]}"{e}/>'
    s=''
    if p.fs: s+=''.join(sh(t,f' fill="{p.fs}" stroke="{p.fs}" stroke-width="{ow+(3 if t[0]=="q" else 0)}" stroke-linejoin="round"') for t in parts)
    s+=''.join(sh(t,f' fill="{p.f}"'+(f' stroke="{p.f}" stroke-width="3" stroke-linejoin="round"' if t[0]=='q' else '')) for t in parts)
    return s
def foam(cx,y,w,n,p,ow=5):
    parts=[('r',cx-w/2,y-4,w,9,3.5)]
    for i in range(n):
        x=cx-w/2+w*(i+.5)/n;r=w/n*.62+(1 if i%2 else 0)
        parts.append(('c',round(x,1),y-4-(2 if i%2 else 0),round(r,1)))
    return blob(parts,p,ow)
OP=' stroke-opacity=".3"'
# ---------- motiver ----------
def m01(p): return P(cap(60,60,50,44),p.m)+C(60,60,35,p.c)+P(star(60,61,23),p.i)
def m02(p): return C(58,63,26,stroke=p.m,sw=13)+P('M34 93L82 33',stroke=p.m,sw=11)+P(star(96,25,9.5),p.a)
def m03(p): return '<g transform="translate(-7 2)">'+P('M82 58h7a10 10 0 0 1 10 10v8a10 10 0 0 1-10 10h-7',stroke=p.ms,sw=7)+P('M34 46h50v44a8 8 0 0 1-8 8H42a8 8 0 0 1-8-8z',p.b)+P('M46 64v22M59 64v22M72 64v22',stroke=p.c,sw=4,x=' stroke-opacity=".28"')+blob([('c',40,44,9),('c',52,38,11),('c',66,40,10),('c',77,46,8),('c',58,48,10),('p','M38 48v14a4 4 0 0 0 8 0v-14z')],p)+'</g>'
def m04(p):
    g='M33 18h54l-7 84a4 4 0 0 1-4 4H44a4 4 0 0 1-4-4z'
    return '<g clip-path="url(#c4)">'+R(20,16,80,50,0,p.m)+C(60,66,15,p.f)+R(20,66,80,44,0,p.d)+P('M40 77h40M45 85h30M50 93h20',stroke=p.ms,sw=3.2)+'</g>'+P(g,stroke=p.w,sw=4.5)+P('M33 18h54',stroke=p.w,sw=7),f'<clipPath id="c4"><path d="{g}"/></clipPath>'
def m05(p):
    s=''.join(P(star(60+38*math.sin(math.radians(a)),70-38*math.cos(math.radians(a)),8.5 if a else 11),p.a) for a in (-64,-32,0,32,64))
    return s+P('M22 78c8-6 14-6 22 0s14 6 22 0 14-6 22 0 8 4 12 2',stroke=p.w,sw=4)+P('M30 91c7-5 12-5 19 0s12 5 19 0 12-5 19 0',stroke=p.ms,sw=4)+P('M44 103c5-4 9-4 14 0s9 4 14 0',stroke=p.x,sw=4)
def m06(p):
    s=P('M60 22c2-8 8-12 16-12-1 8-6 13-16 12z',p.a)+P('M60 24V14',stroke=p.a,sw=3)
    for y,xs in [(36,[60]),(50,[47,73]),(64,[34,60,86]),(78,[47,73]),(92,[60])]:
        for x in xs: s+=P(petal(x,y,24,30),p.b,p.c,2.5)
    return s
def m07(p):
    def gl(tx,rot): return f'<g transform="translate({tx} 0) rotate({rot} 60 70)">'+P('M46 44h28l-4 48a3 3 0 0 1-3 3H53a3 3 0 0 1-3-3z',p.b)+blob([('p','M45 38h30a3 3 0 0 1 3 3v5H42v-5a3 3 0 0 1 3-3z'),('c',50,38,6),('c',60,35,7),('c',70,38,6)],p,4)+'</g>'
    return gl(-17,-14)+gl(17,14)+P(star(60,22,11,3.2,4),p.a)+P('M40 20l-5-6M80 20l5-6',stroke=p.a,sw=3)
def m08(p): return P('M60 108C40 84 26 70 26 50a34 34 0 0 1 68 0c0 20-14 34-34 58z',p.m)+C(60,50,24,p.c)+P('M50 41h20l-3 25a2 2 0 0 1-2 2H55a2 2 0 0 1-2-2z',p.i)+blob([('r',49,35,22,7,2),('c',54,35,4.5),('c',61,33,5),('c',67,35,4.5)],p,3.5)
def m09(p): return ''.join(P(star(x,y,7.5),p.a) for x,y in ((38,27),(60,20),(82,27)))+P(pint(60,54,36,27,44),p.b)+foam(60,54,38,3,p)+P('M22 76c8 3 13 9 15 18M98 76c-8 3-13 9-15 18',stroke=p.l,sw=3.5)
def m10(p): return P(bottle(60,18,90,40),p.m)+R(50,12,20,8,2.5,p.a)+C(60,80,14,p.c)+P(star(60,80.5,9),p.i)
def m11(p): return P(pint(60,36,50,38,60),p.b)+foam(60,36,52,4,p)+P(star(60,69,14),p.c)
def m12(p): return P('M29 82L22 44L43 61L60 32L77 61L98 44L91 82z',p.m,p.m,5)+R(27,88,66,10,4,p.m)+C(22,42,5.5,p.m)+C(60,29,6,p.m)+C(98,42,5.5,p.m)+P(star(60,71,9),p.c)
def m13(p):
    sh='M60 6L104 20V58C104 86 84 104 60 114C36 104 16 86 16 58V20z'
    return '<g transform="translate(60 60) scale(.9) translate(-60 -60)">'+P(sh,p.m)+f'<g transform="translate(60 61) scale(.86) translate(-60 -60)">{P(sh,p.c)}</g>'+P(pint(60,56,32,24,36),p.b)+foam(60,56,34,3,p,4)+P(star(60,30,8),p.i)+'</g>'
def m14(p): return P('M38 10H56L68 48L50 54z',p.x)+P('M82 10H64L52 48L70 54z',p.ms)+C(60,74,30,p.b)+C(60,74,24,stroke=p.c,sw=1.5,x=OP)+P(star(60,74.5,15),p.c)
def m15(p): return P(pint(60,28,58,44,76,5),p.b)+foam(60,28,60,4,p)+''.join(C(a,b,c,p.f,x=' fill-opacity=".88"') for a,b,c in ((49,90,4.5),(53,66,4),(68,54,3.5),(56,48,2.5),(46,76,2.5),(69,76,7)))
def m16(p): return P(cap(60,60,50,44),p.m)+C(60,60,35,p.c)+oe(60,60,15,7,p.i)
def m17(p): return C(42,60,18,stroke=p.m,sw=10)+P('M26.2 81.9L57.8 38.1',stroke=p.m,sw=8)+P('M77 38V82H99',stroke=p.m,sw=10)
def m18(p): return P(star(60,63,52,23),p.b)+oe(60,64,10.5,5.5,p.c)
def m19(p):
    ba='M36 24H84C96 44 96 76 84 96H36C24 76 24 44 36 24z'
    return P(ba,p.b)+'<g clip-path="url(#c19)">'+R(20,37,80,7,0,p.c)+R(20,76,80,7,0,p.c)+P('M48 24C43 46 43 74 48 96M60 24V96M72 24C77 46 77 74 72 96',stroke=p.c,sw=2,x=OP)+'</g>'+C(60,60,12,p.c)+P(star(60,60.5,7.5),p.i),f'<clipPath id="c19"><path d="{ba}"/></clipPath>'
def m20(p): return P(drop(60,74,29),p.m)+P(star(60,75,15),p.c)
def m21(p):
    gr='';aw=''
    for y in (42,56,70,84):
        gr+=f'<path d="{petal(51,y,11,20)}" fill="{p.b}" transform="rotate(-30 51 {y})"/><path d="{petal(69,y,11,20)}" fill="{p.b}" transform="rotate(30 69 {y})"/>'
        aw+=f'M45 {y-9}L35 {y-24}M75 {y-9}L85 {y-24}'
    return P('M60 108V34',stroke=p.ms,sw=3)+P(aw+'M60 18V7M56 22L50 10M64 22L70 10',stroke=p.ms,sw=1.8)+gr+P(petal(60,28,11,20),p.b)
def m22(p):
    lv=''
    for i in range(6):
        for t,rot in ((105+i*27,180-25),(75-i*27,25)):
            x=60+38*math.cos(math.radians(t));y=60+38*math.sin(math.radians(t))
            lv+=f'<path d="{petal(round(x,1),round(y,1),9,19)}" fill="{p.b}" transform="rotate({t+rot} {x:.1f} {y:.1f})"/>'
    return lv+P(star(60,59,17),p.a)
def m23(p): return C(60,60,46,stroke=p.l,sw=9,x=' stroke-opacity=".45"')+P('M60 14A46 46 0 1 1 16.25 45.8',stroke=p.m,sw=9)+P(pint(60,48,30,23,38),p.b)+foam(60,48,32,3,p,4)
def m24(p): return P(pint(30,62,22,17,36),p.b)+foam(30,62,24,3,p,4)+P(pint(60,46,24,18,52),p.b)+foam(60,46,26,3,p,4)+P(pint(90,70,22,17,28),p.b)+foam(90,70,24,3,p,4)+R(16,99,88,5,2.5,p.l)+P(star(60,21,9),p.a)
def m25(p): return P('M30 24H90A12 12 0 0 1 102 36V70A12 12 0 0 1 90 82H56L38 100V82H30A12 12 0 0 1 18 70V36A12 12 0 0 1 30 24z',p.m)+''.join(P(star(a,54,9.5),p.c) for a in (38,60,82))
def m26(p): return P('M60 102C28 80 22 62 22 50a19 19 0 0 1 38-4a19 19 0 0 1 38 4c0 12-6 30-38 52z',p.m)+P(pint(60,56,24,18,28),p.c)+foam(60,56,26,3,NS(f=p.f,fs=None))
def m27(p): return P('M73 73L97 97',stroke=p.m,sw=12)+C(52,52,28,p.c,p.w,7)+P(pint(52,47,22,17,24),p.b)+foam(52,47,24,3,p,3.5)
def m28(p): return P('M42 27l3-8h30l3 8z',p.w)+P('M42 95l3 7h30l3-7z',p.w,x=' fill-opacity=".85"')+R(38,26,44,70,6,p.m)+C(60,61,14,p.c)+P(star(60,61.5,9),p.i)
def m29(p): return '<g transform="rotate(35 60 60)">'+R(52,54,16,54,8,p.m)+C(60,36,21,stroke=p.m,sw=11)+C(60,97,4,p.c)+P(star(60,36.5,9),p.a)+'</g>'
def m30(p): return P('M20 98L60 58',stroke=p.m,sw=7)+P('M16 74L44 46',stroke=p.x,sw=4)+P('M44 104L72 76',stroke=p.ms,sw=4)+f'<path d="{star(78,40,25)}" fill="{p.a}" transform="rotate(14 78 40)"/>'+C(28,24,2,p.w)+C(100,86,2.5,p.w)+C(48,16,1.5,p.w)
def m31(p):
    d,x=wave(-40,80,13,40,5);d2,_=wave(-40,73,13,40,5)
    return P(star(60,36,16),p.a)+P(d+f'V140H-40z',p.m)+P(d2,stroke=p.f,sw=5)+P('M30 101c7-5 12-5 19 0s12 5 19 0 12-5 19 0',stroke=p.c,sw=4)
def m32(p):
    d,x=wave(-45,78,9,30,7)
    return P(cap(60,58,36,31,17),p.m)+C(60,58,24,stroke=p.c,sw=1.5,x=OP)+P(star(60,50,10),p.c)+P(d+'V140H-45z',p.d)+P(d,stroke=p.f,sw=4)+P('M42 94h36M50 104h20',stroke=p.ms,sw=3.5)
def m33(p): return R(57.5,84,5,17,0,p.w)+R(45,99,30,5,2.5,p.w)+P('M43 26H77L69 80a9 9 0 0 1-18 0z',p.b)+foam(60,26,36,3,p)+P(star(60,56,8.5),p.c)
def m34(p): return R(57.5,74,5,24,0,p.w)+R(43,96,34,5,2.5,p.w)+P('M44 30C44 42 34 50 36 60C38 72 50 77 60 77C70 77 82 72 84 60C86 50 76 42 76 30z',p.m)+foam(60,30,34,3,p)
def m35(p): return P(bottle(42,20,86,30),p.m)+R(35,14,14,8,2.5,p.a)+C(42,79,9.5,p.c)+P(star(42,79.4,6),p.i)+P(pint(83,58,30,23,48),p.b)+foam(83,58,32,3,p,4)
def m36(p): return P('M27 38C25 78 52 106 98 99C70 93 55 73 55 38z',p.m)+P('M31 62C38 60 50 58 57 54M41 82C48 78 58 74 64 68',stroke=p.c,sw=3,x=' stroke-opacity=".35"')+blob([('e',41,38,15,6.5),('c',33,33,6.5),('c',42,29,7.5),('c',50,33,6.5)],p,4)+P(star(86,42,11),p.a)
def m37(p):
    s=R(12,88,96,9,4.5,p.l)
    for x,c in zip((27,49,71,93),p.fl): s+=P(pint(x,56,17,13,32,2.5),c)+foam(x,56,18,3,p,3.5)
    return s+P(star(60,26,10),p.a)
def m38(p):
    vs=((38,32),(49,21),(60,29),(71,21),(82,32),(75,94),(45,94))
    return P('M38 32L49 21L60 29L71 21L82 32L75 94L45 94z',stroke=p.l,sw=1.8)+''.join(C(a,b,3.4,p.a) for a,b in vs)+P(star(60,64,13),p.a)+P(star(99,22,6,1.6,4),p.w)+P(star(20,72,5,1.4,4),p.w)+C(101,80,1.6,p.w)+C(21,26,1.6,p.w)
def m39(p): return '<g transform="translate(-5 0)">'+P('M84 56h6a9 9 0 0 1 9 9v8a9 9 0 0 1-9 9h-7',stroke=p.ms,sw=6)+P(pint(60,42,50,42,58,7),p.b)+foam(60,42,52,4,p)+C(51,64,4,p.c)+C(69,64,4,p.c)+P('M50 77q10 9 20 0',stroke=p.c,sw=4)+C(43,74,3.5,p.x,x=' fill-opacity=".7"')+C(77,74,3.5,p.x,x=' fill-opacity=".7"')+'</g>'
def m40(p): return P(pint(60,52,46,36,52),p.b)+blob([('q','M36 55L33 28L47 40L60 21L73 40L87 28L84 55z'),('c',33,26,4.5),('c',60,19,5),('c',87,26,4.5)],p)
MOTIV=[('stjernekapsel','Stjernekapslen',m01),('oe-maerket','Ø-mærket',m02),('kruset','Kruset',m03),('solnedgang','Solnedgangen',m04),('fem-stjerner','Fem stjerner',m05),('humlen','Humlen',m06),('skaal','Skål',m07),('oelnaalen','Ølnålen',m08),('tre-stjerner','Tre stjerner',m09),('flasken','Flasken',m10),
('stjerneglasset','Stjerneglasset',m11),('kronen','Kronen',m12),('skjoldet','Skjoldet',m13),('medaljen','Medaljen',m14),('boblerne','Boblerne',m15),('oe-kapslen','Ø-kapslen',m16),('oel-maerket','ØL-mærket',m17),('stjerne-oe','Stjerne-ø',m18),('toenden','Tønden',m19),('draaben','Dråben',m20),
('byggen','Byggen',m21),('kransen','Kransen',m22),('ringen','Ringen',m23),('podiet','Podiet',m24),('taleboblen','Taleboblen',m25),('hjertet','Hjertet',m26),('luppen','Luppen',m27),('daasen','Dåsen',m28),('oplukkeren','Oplukkeren',m29),('stjerneskuddet','Stjerneskuddet',m30),
('boelgen','Bølgen',m31),('kapselsolen','Kapselsolen',m32),('pilsnerglasset','Pilsnerglasset',m33),('tulipanen','Tulipanen',m34),('flaske-og-glas','Flaske og glas',m35),('hornet','Hornet',m36),('smagebraettet','Smagebrættet',m37),('stjernebilledet','Stjernebilledet',m38),('maskotten','Maskotten',m39),('skumkronen','Skumkronen',m40)]
G='url(#g)';H='url(#h)'
FLC=[GL,'#ffa24a',SUN,PK]
STIL=[
 ('nat','Nat','sq',NAVY,'',NS(m=G,ms=GL,b=H,a=GL,c=NAVY,i=GL,f=W,fs=None,w=W,l=SKY,x=PK,d=NV3,fl=FLC)),
 ('solnedgang','Solnedgang','sq','url(#s)','',NS(m=NAVY,ms=NAVY,b=NAVY,a=W,c=GL,i=NAVY,f=W,fs=None,w=W,l='#ffe9c2',x=W,d=GL,fl=[NAVY]*4)),
 ('lys','Lys','sq',W,' stroke="#cfd9e8" stroke-width="2"',NS(m=NAVY,ms=NAVY,b=H,a=SUN,c=W,i=SUN,f=W,fs=NAVY,w=NAVY,l='#9fb2cf',x=PK,d='#dce6f4',fl=FLC)),
 ('guld','Guld','ci',GL,'',NS(m=NAVY,ms=NAVY,b=NAVY,a=NAVY,c=GL,i=NAVY,f=W,fs=NAVY,w=NAVY,l='#d9962b',x=SUN,d='#f0ae3a',fl=[NAVY]*4)),
 ('fjord','Fjord','ci','url(#b)','',NS(m=H,ms=GL,b=H,a=W,c='#234a7d',i=W,f=W,fs=None,w=W,l=SKY,x=PK,d='#1a3256',fl=FLC)),
]
DEFS=grad('g')+grad('h',stops=((0,GL),(1,SUN)))+grad('s',stops=((0,GL),(.55,SUN),(1,PK)))+grad('b',stops=((0,'#4a82c4'),(1,'#1b3358')))
def build(mf,st):
    slug,name,shape,bg,bgx,p=st
    r=mf(p);body,extra=r if isinstance(r,tuple) else (r,'')
    if shape=='sq':
        o=1 if bgx else 0
        back=f'<rect x="{o}" y="{o}" width="{120-2*o}" height="{120-2*o}" rx="{28-o}" fill="{bg}"{bgx}/>';clip='<clipPath id="fr"><rect width="120" height="120" rx="28"/></clipPath>';inner=body
    else:
        back=f'<circle cx="60" cy="60" r="60" fill="{bg}"/>';clip='<clipPath id="fr"><circle cx="60" cy="60" r="60"/></clipPath>';inner=f'<g transform="translate(60 60) scale(.86) translate(-60 -60)">{body}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-label="ølrating.dk"><defs>{DEFS}{clip}{extra}</defs>{back}<g clip-path="url(#fr)">{inner}</g></svg>'
if __name__=='__main__':
    out=sys.argv[1];os.makedirs(out,exist_ok=True);idx=[];n=0
    for ms,mn,mf in MOTIV:
        for st in STIL:
            n+=1;fn=f'{n:03d}-{ms}-{st[0]}.svg';open(os.path.join(out,fn),'w',encoding='utf-8').write(build(mf,st));idx.append({'n':n,'file':fn,'motiv':mn,'stil':st[1]})
    json.dump(idx,open(os.path.join(out,'index.json'),'w',encoding='utf-8'),ensure_ascii=False)
    cells=''.join(f'<div><img src="{i["file"]}" style="width:100%;display:block"><div style="font:11px sans-serif">{i["n"]}</div></div>' for i in idx)
    open(os.path.join(out,'ark.html'),'w',encoding='utf-8').write(f'<!doctype html><meta charset="utf-8"><body style="margin:0;background:#e9eef7"><div style="display:grid;grid-template-columns:repeat(10,1fr);gap:8px;padding:8px;width:1300px;box-sizing:border-box">{cells}</div>')
    print(n)
