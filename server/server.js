// Server multiplayer Pancing Mania. Jalanin: DEV_TOKEN=rahasia DEV_NAME=Julak node server.js
const http = require('http'), crypto = require('crypto');
const { WebSocketServer } = require('ws');
const PORT = +process.env.PORT || 3000, MAX = +process.env.MAX_PLAYERS || 40;
const DEV_TOKEN = process.env.DEV_TOKEN || '', DEV_NAME = process.env.DEV_NAME || 'Developer';
const RESERVED = ['admin', 'moderator', 'mod', 'staff', 'owner', 'dev', 'developer', 'server', 'system', DEV_NAME.toLowerCase()];
const BAD = ['anjing', 'bangsat', 'kontol', 'memek', 'bajingan', 'ngentot', 'jancok', 'fuck', 'shit', 'bitch', 'pepek', 'asu'];
const SECRET_FISH = new Map([['kraken_purba', 'Kraken Purba'], ['megalodon', 'Megalodon']]), secrets = []; // riwayat 30 ikan Secret terakhir
const players = new Map(), banned = new Set(), maint = { on: false, msg: '' }; let nextId = 0, latest = 0, latestUrl = '', latestName = '';
const MIN_BUILD = +process.env.MIN_BUILD || 0; // build di bawah ini dipaksa update // ban hilang kalau server di-restart
const sha = s => crypto.createHash('sha256').update(String(s)).digest();
const isDevToken = t => DEV_TOKEN && typeof t === 'string' && crypto.timingSafeEqual(sha(t), sha(DEV_TOKEN));
const norm = s => s.toLowerCase().replace(/0/g, 'o').replace(/1/g, 'i').replace(/3/g, 'e').replace(/4/g, 'a').replace(/5/g, 's').replace(/_/g, '');
const pub = p => ({ id: p.id, name: p.name, gender: p.gender, dev: p.dev, x: p.x, y: p.y, z: p.z, ry: p.ry });
const clamp = (v, a) => Math.max(-a, Math.min(a, v));
// ---- cek ikan Secret. Gacha-nya jalan di HP pemain, jadi server cuma bisa cek yang masuk akal:
// ada lemparan, jeda waktunya wajar, mutasi & berat sesuai tabel ikan, dan dibatasi per jam.
const SECRET_W = { kraken_purba: [20000, 140000], megalodon: [25000, 150000] }, MUT_WORDS = new Set(['Shiny', 'Emas', 'Pelangi', 'Besar', 'Hantu']);
function checkSecret(p, id, mut, w, now) {
  const words = mut ? mut.split(' ') : [];
  if (words.length > 2 || !words.every(x => MUT_WORDS.has(x))) return 'mutasi tidak dikenal: ' + mut;
  const r = SECRET_W[id]; if (!r) return 'ikan tidak dikenal';
  if (!(w >= r[0] * 0.99 && w <= r[1] * 1.6 * 1.01)) return 'berat di luar batas: ' + w;
  if (p.cv >= 2) { // klien baru wajib kirim 'cast' dulu
    if (!p.castOpen) return 'tanpa lemparan';
    const dt = now - p.castAt; if (dt < 3000 || dt > 600000) return 'jeda lemparan aneh: ' + dt + 'ms';
  }
  p.sec = p.sec.filter(t => now - t < 3600000); if (p.sec.length >= 12) return 'terlalu banyak per jam';
  p.sec.push(now); return '';
}
const alertDevs = text => players.forEach(p => { if (p.dev) send(p.ws, { t: 'say', text }); });

/* PM_V42 peringkat, boss, pasar */
const LB = new Map(), MK = { list: [], pay: {}, mail: {}, nid: 1 };
const PM42_TYPES = new Set(['stat', 'lbget', 'bhit', 'mget', 'mput', 'mbuy', 'mcancel', 'mcollect']);
const okId = s => typeof s === 'string' && /^[A-Za-z0-9_\-]{1,40}$/.test(s);
const okUid = s => typeof s === 'string' && /^[A-Za-z0-9]{16,40}$/.test(s);
const nm = (v, max) => Number.isFinite(v) ? Math.max(0, Math.min(v, max)) : 0;
const MK_FEE = 0.05, MK_PER = 5, MK_ALL = 300, MK_EXP = 7 * 86400000, MK_MAXP = 5000000;

// ---- peringkat: nilai dari klien dibatasi laju kenaikannya (anti-curang ringan)
function lbStat(p, m, now) {
  const k = p.name.toLowerCase(); let e = LB.get(k); const first = !e;
  if (first) { e = { n: p.name, c: 0, w: 0, wf: '', rb: 0, lv: 1, tr: 0, al: 50, at: now }; LB.set(k, e); }
  e.n = p.name;
  e.al = Math.min(60, (e.al || 0) + (now - (e.at || now)) / 3000); e.at = now;
  let c = Math.floor(nm(m.c, 1e7)); const lim = first ? 100000 : e.c + Math.floor(e.al);
  if (c > lim) c = lim;
  if (c > e.c) { e.al = Math.max(0, e.al - (c - e.c)); e.c = c; }
  const w = Math.round(nm(m.w, 250000) * 10) / 10;
  if (w > e.w) { e.w = w; e.wf = typeof m.wf === 'string' ? m.wf.replace(/[^A-Za-z0-9 ]/g, '').trim().slice(0, 24) : ''; }
  const rb = Math.floor(nm(m.rb, 1000));
  e.rb = first ? Math.min(rb, 50) : Math.min(Math.max(e.rb, rb), e.rb + 1);
  e.lv = Math.floor(Math.max(1, Math.min(nm(m.lv, 9999), 9999)));
  e.tr = Math.floor(nm(m.tr, 60));
  saveData();
}
function lbTop() {
  const a = [...LB.values()];
  const top = (key, n) => a.filter(e => e[key] > 0).sort((x, y) => y[key] - x[key]).slice(0, n);
  return {
    c: top('c', 10).map(e => [e.n, e.c]),
    w: top('w', 10).map(e => [e.n, e.w, e.wf]),
    p: a.map(e => [e.n, e.rb, e.lv, e.rb * 10000 + e.lv]).sort((x, y) => y[3] - x[3]).slice(0, 10).map(r => [r[0], r[1], r[2]])
  };
}

// ---- boss fish: server yang menentukan HP, kontribusi, dan hadiah
const BOSS = { on: false, hp: 0, max: 0, end: 0, name: '', hits: new Map(), lastB: 0, next: Date.now() + 20 * 60000 };
const BOSS_NAMES = ['Raja Laut', 'Leviathan Murka', 'Hiu Kegelapan', 'Gurita Raksasa'];
function bossSpawn() {
  if (BOSS.on || !players.size) return false;
  BOSS.on = true; BOSS.max = BOSS.hp = 400 * players.size; BOSS.end = Date.now() + 120000; BOSS.hits = new Map(); BOSS.lastB = 0;
  BOSS.name = BOSS_NAMES[Math.floor(Math.random() * BOSS_NAMES.length)];
  broadcast({ t: 'boss', st: 'spawn', name: BOSS.name, hp: BOSS.hp, max: BOSS.max, left: 120000 });
  return true;
}
function bossEnd(win) {
  if (!BOSS.on) return;
  BOSS.on = false; BOSS.next = Date.now() + (30 + Math.random() * 30) * 60000;
  let total = 0, top = null, topH = 0, part = 0;
  BOSS.hits.forEach((h, id) => { total += h; if (h >= 10) part++; if (h > topH) { topH = h; top = id; } });
  const pool = 3000 + 1500 * part;
  BOSS.hits.forEach((h, id) => {
    const q = players.get(id); if (!q || h < 10) return;
    let coins = win ? Math.floor(pool * h / total) + 300 : 150;
    const mvp = win && id === top; if (mvp) coins += 1000;
    send(q.ws, { t: 'bossr', coins, hits: h, mvp, win });
  });
  const tp = players.get(top);
  broadcast({ t: 'boss', st: 'end', win, top: tp ? tp.name : '' });
}
function bossHit(p, now) {
  if (!BOSS.on) return;
  if (now - (p.bw || 0) > 1000) { p.bw = now; p.bc = 0; }
  if (++p.bc > 6) return; // maks 6 serangan per detik
  BOSS.hits.set(p.id, (BOSS.hits.get(p.id) || 0) + 1); BOSS.hp--;
  if (BOSS.hp <= 0) return bossEnd(true);
  if (now - BOSS.lastB > 500) { BOSS.lastB = now; broadcast({ t: 'boss', st: 'hp', name: BOSS.name, hp: BOSS.hp, max: BOSS.max, left: Math.max(0, BOSS.end - now) }); }
}
setInterval(() => {
  const now = Date.now();
  if (BOSS.on && now >= BOSS.end) bossEnd(false);
  else if (!BOSS.on && now >= BOSS.next && players.size > 0) bossSpawn();
}, 1000);

// ---- pasar pemain: barang disimpan server (escrow), pemilik dikenali lewat uid acak dari klien
function pm42(p, m, ws, now) {
  if (m.t === 'stat') return lbStat(p, m, now);
  if (m.t === 'lbget') { if (now - (p.lbAt || 0) < 1500) return; p.lbAt = now; return send(ws, Object.assign({ t: 'lb' }, lbTop())); }
  if (m.t === 'bhit') return bossHit(p, now);
  const rid = typeof m.rid === 'string' ? m.rid.slice(0, 24) : '';
  const fail = why => send(ws, { t: 'mfail', rid, why });
  if (!okUid(m.u)) return fail('id tidak valid');
  p.uid = m.u;
  if (m.t === 'mget') {
    return send(ws, { t: 'mlist', list: MK.list.map(l => ({ id: l.id, f: l.f, mu: l.mu, price: l.price, s: l.sn, ts: l.ts, mine: l.u === m.u })), pay: MK.pay[m.u] || 0, mail: (MK.mail[m.u] || []).length });
  }
  if (m.t === 'mput') {
    if (!okId(m.f) || !okId(m.mu)) return fail('barang tidak valid');
    const price = Math.floor(m.price);
    if (!(price >= 10 && price <= MK_MAXP)) return fail('harga harus 10 sampai 5.000.000');
    if (now - (p.mAt || 0) < 3000) return fail('terlalu cepat, tunggu sebentar');
    if (MK.list.filter(l => l.u === m.u).length >= MK_PER) return fail('maksimal ' + MK_PER + ' listing');
    if (MK.list.length >= MK_ALL) return fail('pasar penuh');
    p.mh = (p.mh || []).filter(t => now - t < 3600000); if (p.mh.length >= 20) return fail('maksimal 20 listing per jam');
    p.mh.push(now); p.mAt = now;
    MK.list.push({ id: MK.nid++, u: m.u, sn: p.name, f: m.f, mu: m.mu, price, ts: now });
    saveData(); return send(ws, { t: 'mok', rid });
  }
  if (m.t === 'mbuy') {
    if (now - (p.bAt || 0) < 600) return fail('terlalu cepat');
    p.bAt = now;
    const i = MK.list.findIndex(l => l.id === +m.id);
    if (i < 0) return fail('sudah terjual atau dibatalkan');
    const l = MK.list[i]; if (l.u === m.u) return fail('itu barangmu sendiri');
    MK.list.splice(i, 1);
    const got = Math.floor(l.price * (1 - MK_FEE));
    MK.pay[l.u] = (MK.pay[l.u] || 0) + got; saveData();
    send(ws, { t: 'mbought', rid, f: l.f, mu: l.mu, price: l.price });
    players.forEach(q => { if (q.uid === l.u) send(q.ws, { t: 'msold', f: l.f, coins: got }); });
    return;
  }
  if (m.t === 'mcancel') {
    const i = MK.list.findIndex(l => l.id === +m.id && l.u === m.u);
    if (i < 0) return fail('listing tidak ditemukan');
    const l = MK.list.splice(i, 1)[0]; saveData();
    return send(ws, { t: 'mcancelled', rid, f: l.f, mu: l.mu });
  }
  if (m.t === 'mcollect') {
    const coins = MK.pay[m.u] || 0, items = MK.mail[m.u] || [];
    delete MK.pay[m.u]; delete MK.mail[m.u]; saveData();
    return send(ws, { t: 'mpay', rid, coins, items });
  }
}
setInterval(() => { // listing kadaluarsa (7 hari) dikembalikan lewat kotak surat pemilik
  const now = Date.now(); let ch = false;
  MK.list = MK.list.filter(l => {
    if (now - l.ts < MK_EXP) return true;
    const a = MK.mail[l.u] = MK.mail[l.u] || []; if (a.length < 50) a.push({ f: l.f, mu: l.mu });
    ch = true; return false;
  });
  if (ch) saveData();
}, 3600000);

// ---- simpan ban, riwayat Secret, dan status maintenance ke file biar tahan restart
const fs = require('fs'), path = require('path');
const DATA_FILE = process.env.DATA_FILE || path.join(__dirname, 'data.json');
let saveT = null;
function saveData() {
  clearTimeout(saveT);
  saveT = setTimeout(() => {
    try { const tmp = DATA_FILE + '.tmp'; fs.writeFileSync(tmp, JSON.stringify({ v: 1, banned: [...banned], secrets, maint, lb: [...LB.values()], mk: MK })); fs.renameSync(tmp, DATA_FILE); }
    catch (e) { console.log('data.json gagal ditulis:', e.message); }
  }, 400);
}
(function loadData() {
  try {
    const d = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    (d.banned || []).forEach(n => { if (typeof n === 'string') banned.add(n.toLowerCase()); });
    (d.secrets || []).slice(-30).forEach(e => { if (e && typeof e === 'object') secrets.push(e); });
    if (d.maint) { maint.on = !!d.maint.on; maint.msg = String(d.maint.msg || '').slice(0, 120); }
    (d.lb || []).forEach(e => { if (e && typeof e.n === 'string') LB.set(e.n.toLowerCase(), Object.assign({ c: 0, w: 0, wf: '', rb: 0, lv: 1, tr: 0, al: 0, at: Date.now() }, e)); });
    if (d.mk && typeof d.mk === 'object') { MK.list = Array.isArray(d.mk.list) ? d.mk.list : []; MK.pay = d.mk.pay || {}; MK.mail = d.mk.mail || {}; MK.nid = +d.mk.nid || 1; }
    console.log('data.json dimuat:', banned.size, 'ban,', secrets.length, 'secret, maintenance', maint.on ? 'NYALA' : 'mati');
  } catch (e) { if (e.code !== 'ENOENT') console.log('data.json gagal dibaca:', e.message); }
})();

// ---- cek kecepatan gerak (jalan kaki 4.2 u/s; dikasih ruang 1.5x + cadangan 20 unit buat lag)
const MOVE_RATE = 6.3, MOVE_BURST = 20, SAFE_SPOTS = [[0, 36], [-3.4, 38], [0, 21.5]]; // dermaga/perahu/spawn: pindah ke sana boleh (naik-turun perahu)
function moveCheck(p, nx, nz, now) {
  if (p.pt === undefined) { p.pt = now; p.al = MOVE_BURST; return [nx, nz]; } // posisi pertama = titik awal sesi (misal habis reconnect)
  const dt = Math.min((now - p.pt) / 1000, 5); p.pt = now;
  p.al = Math.min(MOVE_BURST, p.al + MOVE_RATE * dt);
  if (SAFE_SPOTS.some(s => Math.hypot(nx - s[0], nz - s[1]) < 4)) { p.al = MOVE_BURST; return [nx, nz]; }
  const dx = nx - p.x, dz = nz - p.z, d = Math.hypot(dx, dz);
  if (d <= p.al) { p.al -= d; return [nx, nz]; }
  const k = p.al / d; p.al = 0; // terlalu jauh: ditahan di batas wajar
  p.vl = (p.vl || []).filter(t => now - t < 10000); p.vl.push(now);
  if (p.vl.length === 10 && now - (p.vAlert || 0) > 60000) { p.vAlert = now; console.log(new Date().toISOString(), 'GERAK TIDAK WAJAR', p.name); alertDevs('⚠ ' + p.name + ' gerak nggak wajar (kemungkinan speed hack)'); }
  if (p.vl.length >= 25) p.kick = true;
  return [p.x + dx * k, p.z + dz * k];
}
const send = (ws, o) => { if (ws.readyState === 1) ws.send(JSON.stringify(o)); };
const broadcast = (o, except) => { const d = JSON.stringify(o); players.forEach(p => { if (p !== except && p.ws.readyState === 1) p.ws.send(d); }); };

const server = http.createServer((req, res) => {
  if (req.url === '/health') { res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(JSON.stringify({ ok: true, players: players.size })); }
  if (req.url === '/status') { res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'Cache-Control': 'no-store' }); return res.end(JSON.stringify({ maint: maint.on, msg: maint.msg, latest, min: MIN_BUILD, url: latestUrl, name: latestName, players: players.size })); }
  if (req.url.startsWith('/admin/maint')) { // curl -H "x-dev-token: TOKEN" "http://localhost:PORT/admin/maint?on=1&msg=Lagi%20update"
    if (!isDevToken(req.headers['x-dev-token'])) { res.writeHead(403); return res.end('forbidden'); }
    const q = new URL(req.url, 'http://x').searchParams;
    maint.on = q.get('on') === '1'; maint.msg = String(q.get('msg') || '').slice(0, 120); saveData();
    broadcast({ t: 'maint', on: maint.on, msg: maint.msg });
    res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(JSON.stringify({ ok: true, maint: maint.on, msg: maint.msg }));
  }
  if (req.url.startsWith('/admin/boss')) { // curl -H "x-dev-token: TOKEN" http://localhost:3010/admin/boss
    if (!isDevToken(req.headers['x-dev-token'])) { res.writeHead(403); return res.end('forbidden'); }
    const ok = bossSpawn();
    res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(JSON.stringify({ ok, on: BOSS.on, players: players.size }));
  }
  if (req.url.startsWith('/admin/bans') || req.url.startsWith('/admin/unban')) { // daftar ban / lepas ban (butuh token developer)
    if (!isDevToken(req.headers['x-dev-token'])) { res.writeHead(403); return res.end('forbidden'); }
    const q = new URL(req.url, 'http://x').searchParams;
    if (req.url.startsWith('/admin/unban')) { const n = String(q.get('name') || '').trim().toLowerCase(); if (banned.delete(n)) saveData(); }
    res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(JSON.stringify({ ok: true, banned: [...banned] }));
  }
  res.writeHead(404); res.end();
});
const wss = new WebSocketServer({ server, maxPayload: 1024 });

wss.on('connection', ws => {
  let me = null, cnt = 0, win = Date.now();
  ws.isAlive = true; ws.on('pong', () => { ws.isAlive = true; });
  const joinTimer = setTimeout(() => { if (!me) ws.close(); }, 10000);
  const fail = (code, msg) => { send(ws, { t: 'err', code, msg }); ws.close(); };

  ws.on('message', raw => {
    const now = Date.now(); if (now - win > 1000) { win = now; cnt = 0; }
    if (++cnt > 40) return ws.terminate(); // spam
    let m; try { m = JSON.parse(raw); } catch (e) { return; }
    if (!m || typeof m !== 'object') return;

    if (m.t === 'join' && !me) {
      const dev = isDevToken(m.token);
      if (m.token && !dev) return fail('bad_token', 'Kode developer salah');
      let name, gender;
      if (dev) { name = DEV_NAME; gender = 'm'; }
      else {
        name = String(m.name || '').trim(); gender = m.gender === 'f' ? 'f' : m.gender === 'm' ? 'm' : null;
        if (!gender || !/^[A-Za-z0-9_]{3,16}$/.test(name)) return fail('bad_name', 'Username 3-16 karakter (huruf/angka/_) & pilih karakter');
        if (RESERVED.includes(name.toLowerCase()) || BAD.some(b => norm(name).includes(b))) return fail('bad_name', 'Username ini nggak boleh dipakai');
      }
      if (banned.has(name.toLowerCase())) return fail('banned', 'Kamu di-ban dari server ini');
      if (maint.on && !dev) return fail('maint', maint.msg || 'Server sedang maintenance');
      if (players.size >= MAX && !dev) return fail('full', 'Server penuh, coba lagi nanti');
      for (const p of players.values()) {
        if (p.name.toLowerCase() !== name.toLowerCase()) continue;
        if (!dev) return fail('name_taken', 'Username sudah dipakai, ganti yang lain');
        players.delete(p.id); p.ws.terminate(); broadcast({ t: 'leave', id: p.id, n: players.size }); // dev reconnect
      }
      me = { id: ++nextId, name, gender, dev, x: 0, y: 1, z: 21.5, ry: 0, mv: 0, dirty: 0, ws, cv: +m.cv || 0, strikes: 0, sec: [] };
      clearTimeout(joinTimer);
      send(ws, { t: 'welcome', id: me.id, you: pub(me), players: [...players.values()].map(pub), n: players.size + 1, maint: maint.on, secrets });
      players.set(me.id, me);
      broadcast({ t: 'join', p: pub(me), n: players.size }, me);
    } else if (m.t === 'pos' && me) {
      if (![m.x, m.y, m.z, m.ry].every(Number.isFinite)) return;
      let nx = clamp(m.x, 600), nz = clamp(m.z, 600);
      if (!me.dev) { const r = moveCheck(me, nx, nz, Date.now()); nx = r[0]; nz = r[1]; }
      me.x = nx; me.y = clamp(m.y, 100); me.z = nz; me.ry = m.ry; me.mv = m.mv ? 1 : 0; me.dirty = 1;
      if (me.kick) { console.log(new Date().toISOString(), 'KICK speed hack', me.name); send(ws, { t: 'kicked', msg: 'Terdeteksi gerak nggak wajar (speed hack)' }); ws.close(); }
    } else if (me && me.dev && (m.t === 'kick' || m.t === 'ban')) { // perintah developer, dicek di server
      const t = players.get(+m.id); if (!t || t.dev) return;
      if (m.t === 'ban') { banned.add(t.name.toLowerCase()); saveData(); }
      send(t.ws, { t: 'kicked', msg: m.t === 'ban' ? 'Kamu di-ban dari server' : 'Kamu di-kick oleh developer' }); t.ws.close();
    } else if (me && me.dev && m.t === 'say') {
      const text = String(m.text || '').slice(0, 120); if (text) broadcast({ t: 'say', text });
    } else if (me && m.t === 'chat') {
      const t0 = Date.now(); if (t0 - (me.lastChat || 0) < 1000) return; me.lastChat = t0;
      let text = String(m.text || '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, 100); if (!text) return;
      if (me.muted) return send(ws, { t: 'say', text: 'Kamu di-mute oleh developer' });
      if (BAD.some(b => norm(text).includes(b))) text = '***';
      broadcast({ t: 'chat', id: me.id, name: me.name, dev: me.dev, text });
    } else if (me && m.t === 'cast') { // pemain melempar pancing
      const t0 = Date.now(); if (t0 - (me.castAt || 0) < 600) return; me.castAt = t0; me.castOpen = true;
    } else if (me && m.t === 'secret') { // pemain dapat ikan Secret -> umumkan ke semua
      const fish = typeof m.id === 'string' ? SECRET_FISH.get(m.id) : null, t0 = Date.now();
      if (!fish || me.flagged || t0 - (me.lastSecret || 0) < 4000) return;
      const mut = typeof m.mut === 'string' ? m.mut.replace(/[^A-Za-z0-9 ]/g, '').trim().slice(0, 20) : '';
      const w = Number.isFinite(m.w) ? Math.round(Math.max(0, Math.min(m.w, 1e10)) * 10) / 10 : 0;
      const why = me.dev ? '' : checkSecret(me, m.id, mut, w, t0);
      if (why) {
        console.log(new Date().toISOString(), 'SECRET DITOLAK', me.name, m.id, why);
        if (++me.strikes >= 3) { me.flagged = true; alertDevs('⚠ ' + me.name + ' dicurigai curang (Secret palsu 3x: ' + why + ')'); }
        return;
      }
      me.lastSecret = t0; me.castOpen = false;
      const ev = { t: 'secret', id: me.id, name: me.name, dev: me.dev, fish, mut, w, ts: t0 };
      secrets.push(ev); if (secrets.length > 30) secrets.shift(); saveData();
      broadcast(ev);
    } else if (me && PM42_TYPES.has(m.t)) { pm42(me, m, ws, Date.now());
    } else if (me && me.dev && m.t === 'mute') {
      const t = players.get(+m.id); if (t && !t.dev) { t.muted = !t.muted; send(ws, { t: 'say', text: t.name + (t.muted ? ' di-mute' : ' di-unmute') }); }
    } else if (me && me.dev && m.t === 'maint') {
      maint.on = !!m.on; maint.msg = String(m.msg || '').slice(0, 120); saveData(); broadcast({ t: 'maint', on: maint.on, msg: maint.msg });
    }
  });
  ws.on('close', () => {
    clearTimeout(joinTimer);
    if (me && players.get(me.id) === me) { players.delete(me.id); broadcast({ t: 'leave', id: me.id, n: players.size }); }
  });
  ws.on('error', () => {});
});

setInterval(() => { // kirim posisi yang berubah, 10x per detik
  const s = []; players.forEach(p => { if (p.dirty) { p.dirty = 0; s.push([p.id, p.x, p.y, p.z, p.ry, p.mv]); } });
  if (s.length) broadcast({ t: 'state', s });
}, 100);
setInterval(() => wss.clients.forEach(c => { if (!c.isAlive) return c.terminate(); c.isAlive = false; c.ping(); }), 30000);

async function refreshLatest() { // nomor build terbaru dari GitHub Releases
  try { const r = await fetch('https://api.github.com/repos/Julakk/BlockWorld/releases/latest', { headers: { 'User-Agent': 'pancing-mania-server' } }); const j = await r.json(); const n = parseInt(String(j.tag_name).replace('build-', ''), 10); if (n) { latest = n; latestName = String(j.name || ''); const a = (j.assets || []).find(x => /\.apk$/i.test(x.name)); latestUrl = a ? a.browser_download_url : ''; } } catch (e) {}
}
refreshLatest(); setInterval(refreshLatest, 300000);

server.listen(PORT, () => console.log('Pancing Mania server jalan di port ' + PORT + (DEV_TOKEN ? '' : ' (DEV_TOKEN belum diset!)')));
