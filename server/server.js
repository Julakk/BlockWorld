// Server multiplayer Pancing Mania. Jalanin: DEV_TOKEN=rahasia DEV_NAME=Julak node server.js
const http = require('http'), crypto = require('crypto');
const { WebSocketServer } = require('ws');
const PORT = +process.env.PORT || 3000, MAX = +process.env.MAX_PLAYERS || 40;
const DEV_TOKEN = process.env.DEV_TOKEN || '', DEV_NAME = process.env.DEV_NAME || 'Developer';
const RESERVED = ['admin', 'moderator', 'mod', 'staff', 'owner', 'dev', 'developer', 'server', 'system', DEV_NAME.toLowerCase()];
const BAD = ['anjing', 'bangsat', 'kontol', 'memek', 'bajingan', 'ngentot', 'jancok', 'fuck', 'shit', 'bitch', 'pepek', 'asu'];
const SECRET_FISH = new Map([['kraken_purba', 'Kraken Purba'], ['megalodon', 'Megalodon']]), secrets = []; // riwayat 30 ikan Secret terakhir
const players = new Map(), banned = new Set(), maint = { on: false, msg: '' }; let nextId = 0, latest = 0;
const MIN_BUILD = +process.env.MIN_BUILD || 0; // build di bawah ini dipaksa update // ban hilang kalau server di-restart
const sha = s => crypto.createHash('sha256').update(String(s)).digest();
const isDevToken = t => DEV_TOKEN && typeof t === 'string' && crypto.timingSafeEqual(sha(t), sha(DEV_TOKEN));
const norm = s => s.toLowerCase().replace(/0/g, 'o').replace(/1/g, 'i').replace(/3/g, 'e').replace(/4/g, 'a').replace(/5/g, 's').replace(/_/g, '');
const pub = p => ({ id: p.id, name: p.name, gender: p.gender, dev: p.dev, x: p.x, y: p.y, z: p.z, ry: p.ry });
const clamp = (v, a) => Math.max(-a, Math.min(a, v));
const send = (ws, o) => { if (ws.readyState === 1) ws.send(JSON.stringify(o)); };
const broadcast = (o, except) => { const d = JSON.stringify(o); players.forEach(p => { if (p !== except && p.ws.readyState === 1) p.ws.send(d); }); };

const server = http.createServer((req, res) => {
  if (req.url === '/health') { res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(JSON.stringify({ ok: true, players: players.size })); }
  if (req.url === '/status') { res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'Cache-Control': 'no-store' }); return res.end(JSON.stringify({ maint: maint.on, msg: maint.msg, latest, min: MIN_BUILD, players: players.size })); }
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
      me = { id: ++nextId, name, gender, dev, x: 0, y: 1, z: 21.5, ry: 0, mv: 0, dirty: 0, ws };
      clearTimeout(joinTimer);
      send(ws, { t: 'welcome', id: me.id, you: pub(me), players: [...players.values()].map(pub), n: players.size + 1, maint: maint.on, secrets });
      players.set(me.id, me);
      broadcast({ t: 'join', p: pub(me), n: players.size }, me);
    } else if (m.t === 'pos' && me) {
      if (![m.x, m.y, m.z, m.ry].every(Number.isFinite)) return;
      me.x = clamp(m.x, 600); me.y = clamp(m.y, 100); me.z = clamp(m.z, 600); me.ry = m.ry; me.mv = m.mv ? 1 : 0; me.dirty = 1;
    } else if (me && me.dev && (m.t === 'kick' || m.t === 'ban')) { // perintah developer, dicek di server
      const t = players.get(+m.id); if (!t || t.dev) return;
      if (m.t === 'ban') banned.add(t.name.toLowerCase());
      send(t.ws, { t: 'kicked', msg: m.t === 'ban' ? 'Kamu di-ban dari server' : 'Kamu di-kick oleh developer' }); t.ws.close();
    } else if (me && me.dev && m.t === 'say') {
      const text = String(m.text || '').slice(0, 120); if (text) broadcast({ t: 'say', text });
    } else if (me && m.t === 'chat') {
      const t0 = Date.now(); if (t0 - (me.lastChat || 0) < 1000) return; me.lastChat = t0;
      let text = String(m.text || '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, 100); if (!text) return;
      if (me.muted) return send(ws, { t: 'say', text: 'Kamu di-mute oleh developer' });
      if (BAD.some(b => norm(text).includes(b))) text = '***';
      broadcast({ t: 'chat', id: me.id, name: me.name, dev: me.dev, text });
    } else if (me && m.t === 'secret') { // pemain dapat ikan Secret -> umumkan ke semua
      const fish = typeof m.id === 'string' ? SECRET_FISH.get(m.id) : null, t0 = Date.now();
      if (!fish || t0 - (me.lastSecret || 0) < 30000) return; me.lastSecret = t0;
      const mut = typeof m.mut === 'string' ? m.mut.replace(/[^A-Za-z0-9 ]/g, '').trim().slice(0, 20) : '';
      const w = Number.isFinite(m.w) ? Math.round(Math.max(0, Math.min(m.w, 99999)) * 10) / 10 : 0;
      const ev = { t: 'secret', id: me.id, name: me.name, dev: me.dev, fish, mut, w, ts: t0 };
      secrets.push(ev); if (secrets.length > 30) secrets.shift();
      broadcast(ev);
    } else if (me && me.dev && m.t === 'mute') {
      const t = players.get(+m.id); if (t && !t.dev) { t.muted = !t.muted; send(ws, { t: 'say', text: t.name + (t.muted ? ' di-mute' : ' di-unmute') }); }
    } else if (me && me.dev && m.t === 'maint') {
      maint.on = !!m.on; maint.msg = String(m.msg || '').slice(0, 120); broadcast({ t: 'maint', on: maint.on, msg: maint.msg });
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
  try { const r = await fetch('https://api.github.com/repos/Julakk/BlockWorld/releases/latest', { headers: { 'User-Agent': 'pancing-mania-server' } }); const j = await r.json(); const n = parseInt(String(j.tag_name).replace('build-', ''), 10); if (n) latest = n; } catch (e) {}
}
refreshLatest(); setInterval(refreshLatest, 300000);

server.listen(PORT, () => console.log('Pancing Mania server jalan di port ' + PORT + (DEV_TOKEN ? '' : ' (DEV_TOKEN belum diset!)')));
