// @ts-nocheck
// ølrating.dk – funktionen "mails" (Supabase Edge Function).
//
// Hvad den gør:
//   POST med x-cron-key   → henter det, der skal sendes (mail_hent), sender det gennem Resend og kvitterer (mail_faerdig).
//                           Databasen kalder selv funktionen hvert 10. minut (supabase/004-mails.sql).
//   POST ?unsub=<nøgle>   → afmelder alle mails med ét klik (det mailprogrammer bruger til knappen "Afmeld").
//   GET  ?unsub=<nøgle>   → sender videre til afmeld-siden på ølrating.dk.
//
// Opsætning (se docs/KONTO.md): "Verify JWT" skal være slået FRA, og hemmeligheden RESEND_API_KEY skal være sat
// under Edge Functions → Secrets. Nøglen må aldrig stå her i filen. MAIL_FROM kan sættes, hvis afsenderen skal være en anden,
// og MAIL_REPLY_TO, hvis svar på mailen skal havne i en bestemt indbakke.
// Filen bruger ingen pakker, så den kan kopieres direkte ind i Supabase.

const SITE = 'https://xn--lrating-p1a.dk';
const env = (k) => Deno.env.get(k) || '';
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'content-type, x-cron-key, apikey, authorization',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { ...CORS, 'Content-Type': 'application/json' } });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Serverens nøgle til databasen. Supabase sætter den selv; den nye slags nøgle prøves først.
function keys() {
  const out = [];
  try {
    const j = JSON.parse(env('SUPABASE_SECRET_KEYS') || '{}');
    if (j && j.default) out.push(j.default);
    for (const v of Object.values(j || {})) if (typeof v === 'string' && v && !out.includes(v)) out.push(v);
  } catch (_) { /* ingen nye nøgler */ }
  const s = env('SUPABASE_SERVICE_ROLE_KEY');
  if (s && !out.includes(s)) out.push(s);
  return out;
}
async function rpc(fn, args) {
  let status = 500, msg = 'ingen nøgle til databasen';
  for (const k of keys()) {
    const r = await fetch(env('SUPABASE_URL') + '/rest/v1/rpc/' + fn, {
      method: 'POST',
      headers: { apikey: k, Authorization: 'Bearer ' + k, 'Content-Type': 'application/json' },
      body: JSON.stringify(args),
    });
    const t = await r.text();
    if (r.ok) return t ? JSON.parse(t) : null;
    status = r.status; msg = t.slice(0, 200);
    if (r.status !== 401) break;   // 401: prøv den næste nøgle
  }
  throw Object.assign(new Error(fn + ' ' + status + ' ' + msg), { status });
}

// ---------- mailens indhold ----------
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const one = (s, n = 60) => String(s ?? '').replace(/[\u0000-\u001f\u007f\u2028\u2029]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, n);
const idOk = (s) => /^[A-Za-z0-9_-]{1,64}$/.test(String(s ?? ''));
const TXT = {
  da: {
    hi: (n) => (n ? 'Hej ' + n : 'Hej'),
    my_beer: '{who} har bedømt {x}, som du har tilføjet',
    friends: '{who}, som du følger, har bedømt {x}',
    tour: '{who} har meldt sig til din byttur {x}',
    tasting: '{who} har stemt i din smagning {x}',
    many: (n) => 'Nyt fra ølrating.dk: ' + n + ' ting siden sidst',
    lead: 'Her er det, der er sket siden sidst:',
    also: 'Og siden sidst:',
    more: (n) => 'og ' + n + ' mere',
    open: 'Åbn ølrating.dk',
    why: 'Du får denne mail, fordi du har slået mails til på din konto på ølrating.dk. Du kan ændre dine valg under Min profil → Konto.',
    unsub: 'Afmeld alle mails',
    someone: 'En smager', beer: 'en øl', tourN: 'byturen', tastN: 'smagningen',
  },
  en: {
    hi: (n) => (n ? 'Hi ' + n : 'Hi'),
    my_beer: '{who} rated {x}, which you added',
    friends: '{who}, who you follow, rated {x}',
    tour: '{who} joined your pub crawl {x}',
    tasting: '{who} voted in your tasting {x}',
    many: (n) => 'ølrating.dk: ' + n + ' new things since last time',
    lead: 'Here is what has happened since last time:',
    also: 'And since last time:',
    more: (n) => 'and ' + n + ' more',
    open: 'Open ølrating.dk',
    why: 'You get this email because you turned on emails for your account on ølrating.dk. You can change your choices under My profile → Account.',
    unsub: 'Unsubscribe from all emails',
    someone: 'A taster', beer: 'a beer', tourN: 'the pub crawl', tastN: 'the tasting',
  },
};
// Én linje pr. hændelse. Ens linjer (fx mange stemmer i samme smagning) bliver til én.
function lines(items, L) {
  const seen = new Set(), out = [];
  for (const it of items || []) {
    const d = it && it.data;
    if (!d || it.kind === 'news') continue;
    const type = it.kind === 'events' ? (d.type === 'tasting' ? 'tasting' : 'tour') : it.kind;
    if (!L[type]) continue;
    const who = one(d.who, 40) || L.someone;
    const x = one(it.kind === 'events' ? d.name : d.beer, 80) || (type === 'tour' ? L.tourN : type === 'tasting' ? L.tastN : L.beer);
    const url = !idOk(d.id) ? SITE + '/' : SITE + (type === 'tour' ? '/#byttur-' : type === 'tasting' ? '/#smagning-' : '/#beer-') + d.id;
    // samme bedømmelse kan ligge i køen både som "min øl" og som "ven": den nævnes kun én gang
    const key = (it.kind === 'events' ? type : 'beer') + '|' + who.toLowerCase() + '|' + String(d.id);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({ tpl: L[type], who, x, url });
  }
  return out;
}
const lineTxt = (l) => l.tpl.replace('{who}', l.who).replace('{x}', l.x);
const lineHtml = (l) => l.tpl.replace('{who}', '\u0001').replace('{x}', '\u0002').split(/([\u0001\u0002])/).map((p) =>
  p === '\u0001' ? '<b>' + esc(l.who) + '</b>' : p === '\u0002' ? '<a href="' + esc(l.url) + '" style="color:#c2410c;font-weight:600">' + esc(l.x) + '</a>' : esc(p)).join('');
// Nyhedens tekst: almindelig tekst med linjeskift. Links, der starter med https://, bliver klikbare.
const para = (t) => String(t).split(/\n{2,}/).map((p) => '<p style="margin:0 0 14px">' +
  p.split(/(https:\/\/[^\s<>"']+[^\s<>"'.,;:!?)])/).map((x, i) => (i % 2 ? '<a href="' + esc(x) + '" style="color:#c2410c">' + esc(x) + '</a>' : esc(x))).join('').replace(/\n/g, '<br>') +
  '</p>').join('');

function build(m, fnUrl) {
  const L = TXT[m.lang === 'en' ? 'en' : 'da'];
  const news = (m.items || []).filter((i) => i && i.kind === 'news' && i.data && i.data.subject && i.data.body).map((i) => i.data);
  const all = lines(m.items, L), ls = all.slice(0, 12), extra = all.length - ls.length;
  if (!news.length && !ls.length) return null;
  const subject = one(news.length ? news[0].subject : ls.length === 1 && !extra ? lineTxt(ls[0]) : L.many(all.length), 120);
  const hi = L.hi(one(m.name, 40)), unsubPage = SITE + '/#afmeld-' + m.unsub;
  const list = ls.length ? '<ul style="margin:0 0 14px;padding:0 0 0 20px">' + ls.map((l) => '<li style="margin:0 0 8px">' + lineHtml(l) + '.</li>').join('') +
    (extra > 0 ? '<li style="margin:0 0 8px">' + esc(L.more(extra)) + '</li>' : '') + '</ul>' : '';
  const html = '<!doctype html><html lang="' + (m.lang === 'en' ? 'en' : 'da') + '"><body style="margin:0;padding:0;background:#f3f5f9">' +
    '<div style="max-width:560px;margin:0 auto;padding:24px 14px;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.55;color:#0f1d36">' +
    '<div style="background:#0f1d36;border-radius:14px 14px 0 0;padding:18px 22px;border-bottom:4px solid #ff7a3d"><a href="' + SITE + '/" style="color:#ffffff;font-size:22px;font-weight:800;text-decoration:none">ølrating<span style="color:#ffc85a">.dk</span></a></div>' +
    '<div style="background:#ffffff;border-radius:0 0 14px 14px;padding:22px">' +
    '<p style="margin:0 0 14px">' + esc(hi) + '</p>' +
    news.map((n) => '<h1 style="margin:0 0 12px;font-size:21px;line-height:1.25">' + esc(one(n.subject, 120)) + '</h1>' + para(String(n.body).slice(0, 4000))).join('') +
    (ls.length ? '<p style="margin:0 0 10px">' + esc(news.length ? L.also : L.lead) + '</p>' + list : '') +
    '<p style="margin:18px 0 0"><a href="' + SITE + '/" style="display:inline-block;background:#ff7a3d;color:#0f1d36;font-weight:700;text-decoration:none;padding:11px 18px;border-radius:999px">' + esc(L.open) + '</a></p>' +
    '</div><p style="margin:16px 6px 0;font-size:13px;line-height:1.5;color:#5b6b85">' + esc(L.why) + ' <a href="' + esc(unsubPage) + '" style="color:#5b6b85">' + esc(L.unsub) + '</a></p></div></body></html>';
  const text = [hi, ...news.map((n) => one(n.subject, 120) + '\n\n' + String(n.body).slice(0, 4000)),
    ls.length ? (news.length ? L.also : L.lead) + '\n' + ls.map((l) => '- ' + lineTxt(l) + ': ' + l.url).join('\n') + (extra > 0 ? '\n- ' + L.more(extra) : '') : '',
    L.open + ': ' + SITE + '/', L.why + '\n' + L.unsub + ': ' + unsubPage].filter(Boolean).join('\n\n');
  return {
    from: env('MAIL_FROM') || 'ølrating.dk <hej@xn--lrating-p1a.dk>',
    to: [m.email], subject, html, text,
    ...(env('MAIL_REPLY_TO') ? { reply_to: env('MAIL_REPLY_TO') } : {}),   // hvor svar på mailen skal havne (valgfri)
    headers: { 'List-Unsubscribe': '<' + fnUrl + '?unsub=' + m.unsub + '>', 'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click' },
  };
}

// ---------- udsendelsen ----------
async function send(k, fnUrl) {
  const key = env('RESEND_API_KEY');
  if (!key) return json({ error: 'RESEND_API_KEY mangler under Edge Functions → Secrets' }, 500);
  const batch = (await rpc('mail_hent', { k, n: 20 })) || [];
  let sent = 0, failed = 0, later = 0, stop = false, inRow = 0;
  for (const m of batch) {
    if (stop) { later++; await rpc('mail_faerdig', { k, ids: m.ids, r: 0 }); continue; }
    const mail = UUID.test(String(m.unsub)) && /^[^\s@]+@[^\s@]+$/.test(String(m.email)) ? build(m, fnUrl) : null;
    if (!mail) { await rpc('mail_faerdig', { k, ids: m.ids, r: 1 }); continue; }   // intet at sende (fx en slettet nyhed)
    let status = 0;
    try {
      const r = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json', 'Idempotency-Key': 'olrating-' + m.ids[0] + '-' + m.ids[m.ids.length - 1] + '-' + m.ids.length },
        body: JSON.stringify(mail),
      });
      status = r.status;
      await r.text();
    } catch (_) { status = 0; }
    // Idempotency-Key: bliver den samme mail forsøgt sendt igen (fx efter en afbrydelse), sender Resend den ikke to gange.
    if (status >= 200 && status < 300) { sent++; inRow = 0; await rpc('mail_faerdig', { k, ids: m.ids, r: 1 }); }
    else if (status === 409) { later++; await rpc('mail_faerdig', { k, ids: m.ids, r: 0 }); }   // samme mail er ved at blive sendt
    else if (status === 0 || status === 429 || status >= 500) { later++; stop = true; await rpc('mail_faerdig', { k, ids: m.ids, r: 0 }); }
    else {
      failed++; inRow++;
      console.error('mail afvist', status);
      await rpc('mail_faerdig', { k, ids: m.ids, r: -1 });
      if (status === 401 || status === 403 || inRow >= 3) stop = true;   // forkert nøgle eller domæne: ingen grund til at fortsætte
    }
    await sleep(150);
  }
  return json({ sent, failed, later });
}

Deno.serve(async (req) => {
  try {
    const u = new URL(req.url);
    const fnUrl = env('SUPABASE_URL') + '/functions/v1/mails';
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    const un = u.searchParams.get('unsub');
    if (un !== null) {
      if (!UUID.test(un)) return json({ error: 'ugyldigt link' }, 400);
      if (req.method === 'POST') { const ok = await rpc('mail_afmeld', { u: un }); return json({ ok: ok === true }); }
      return new Response(null, { status: 302, headers: { ...CORS, Location: SITE + '/#afmeld-' + un } });
    }
    if (req.method !== 'POST') return json({ ok: true, about: 'ølrating.dk mails' });
    const k = req.headers.get('x-cron-key') || '';
    if (!UUID.test(k)) return json({ error: 'nøgle mangler' }, 401);
    return await send(k, fnUrl);
  } catch (e) {
    const s = e && (e.status === 401 || e.status === 403) ? 403 : 500;
    console.error('mails fejl', e && e.message);
    return json({ error: s === 403 ? 'forkert nøgle' : 'fejl' }, s);
  }
});
