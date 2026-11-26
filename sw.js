// ølrating.dk service worker: virker offline og indlæser hurtigt
const V='olrating-v54';
const SHELL=['js/qr.js','js/en.js','./','./index.html','./manifest.webmanifest','./fonts/inter-400.woff2','./fonts/inter-600.woff2','./fonts/inter-700.woff2','./fonts/sora-700.woff2','./img/fjord1.jpg','./img/fjord2.jpg','./img/fjord3.jpg','./img/fjord1-m.jpg','./img/fjord2-m.jpg','./img/fjord3-m.jpg','./img/icon-192.png','./img/favicon.svg','./img/logo.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const u=new URL(r.url);
  // Siden selv: prøv netværket først, så nye versioner kommer med det samme
  if(r.mode==='navigate'){e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(V).then(c=>c.put('./index.html',cp));return res}).catch(()=>caches.match('./index.html')));return}
  // Billeder, ikoner og skrifttyper: fra cachen først
  if(u.origin===location.origin||u.hostname.endsWith('gstatic.com')||u.hostname.endsWith('googleapis.com')){
    e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{if(res.ok||res.type==='opaque'){const cp=res.clone();caches.open(V).then(c=>c.put(r,cp))}return res})))}
});
