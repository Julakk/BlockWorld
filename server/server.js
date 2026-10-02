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

// ---- simpan ban, riwayat Secret, dan status maintenance ke file biar tahan restart
const fs = require('fs'), path = require('path');
const DATA_FILE = process.env.DATA_FILE || path.join(__dirname, 'data.json');
let saveT = null;
function saveData() {
  clearTimeout(saveT);
  saveT = setTimeout(() => {
    try { const tmp = DATA_FILE + '.tmp'; fs.writeFileSync(tmp, JSON.stringify({ v: 1, banned: [...banned], secrets, maint })); fs.renameSync(tmp, DATA_FILE); }
    catch (e) { console.log('data.json gagal ditulis:', e.message); }
  }, 400);
}
(function loadData() {
  try {
    const d = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    (d.banned || []).forEach(n => { if (typeof n === 'string') banned.add(n.toLowerCase()); });
    (d.secrets || []).slice(-30).forEach(e => { if (e && typeof e === 'object') secrets.push(e); });
    if (d.maint) { maint.on = !!d.maint.on; maint.msg = String(d.maint.msg || '').slice(0, 120); }
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
