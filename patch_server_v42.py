#!/usr/bin/env python3
# Patch server v4.2 - Peringkat, Boss Fish, Pasar Pemain
# Pakai: python3 patch_server_v42.py server/server.js
import sys, shutil, os, subprocess, tempfile

path = sys.argv[1] if len(sys.argv) > 1 else 'server/server.js'
src = open(path, encoding='utf-8').read()

if 'PM_V42' in src:
    print('Patch server v4.2 sudah terpasang, tidak ada yang diubah.')
    sys.exit(0)

s = src
errors = []

def replace_once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        errors.append('%s: ketemu %d kali (harus 1)' % (label, n))
        return
    s = s.replace(old, new)

BLOCK = r"""/* PM_V42 peringkat, boss, pasar */
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

// ---- simpan ban, riwayat Secret, dan status maintenance ke file biar tahan restart"""
replace_once("// ---- simpan ban, riwayat Secret, dan status maintenance ke file biar tahan restart", BLOCK, 'blok v4.2')

replace_once(
    "JSON.stringify({ v: 1, banned: [...banned], secrets, maint })",
    "JSON.stringify({ v: 1, banned: [...banned], secrets, maint, lb: [...LB.values()], mk: MK })",
    'simpan data')

replace_once(
    "if (d.maint) { maint.on = !!d.maint.on; maint.msg = String(d.maint.msg || '').slice(0, 120); }",
    "if (d.maint) { maint.on = !!d.maint.on; maint.msg = String(d.maint.msg || '').slice(0, 120); }\n"
    "    (d.lb || []).forEach(e => { if (e && typeof e.n === 'string') LB.set(e.n.toLowerCase(), Object.assign({ c: 0, w: 0, wf: '', rb: 0, lv: 1, tr: 0, al: 0, at: Date.now() }, e)); });\n"
    "    if (d.mk && typeof d.mk === 'object') { MK.list = Array.isArray(d.mk.list) ? d.mk.list : []; MK.pay = d.mk.pay || {}; MK.mail = d.mk.mail || {}; MK.nid = +d.mk.nid || 1; }",
    'muat data')

replace_once(
    "if (req.url.startsWith('/admin/bans') || req.url.startsWith('/admin/unban')) {",
    "if (req.url.startsWith('/admin/boss')) { // curl -H \"x-dev-token: TOKEN\" http://localhost:3010/admin/boss\n"
    "    if (!isDevToken(req.headers['x-dev-token'])) { res.writeHead(403); return res.end('forbidden'); }\n"
    "    const ok = bossSpawn();\n"
    "    res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(JSON.stringify({ ok, on: BOSS.on, players: players.size }));\n"
    "  }\n"
    "  if (req.url.startsWith('/admin/bans') || req.url.startsWith('/admin/unban')) {",
    'endpoint boss')

replace_once(
    "} else if (me && me.dev && m.t === 'mute') {",
    "} else if (me && PM42_TYPES.has(m.t)) { pm42(me, m, ws, Date.now());\n"
    "    } else if (me && me.dev && m.t === 'mute') {",
    'handler pesan')

if errors:
    print('GAGAL, file TIDAK diubah:')
    for e in errors: print(' -', e)
    sys.exit(1)

if shutil.which('node'):
    fn = tempfile.mktemp(suffix='.js')
    open(fn, 'w', encoding='utf-8').write(s)
    r = subprocess.run(['node', '--check', fn], capture_output=True, text=True)
    os.remove(fn)
    if r.returncode != 0:
        print('GAGAL, error sintaks, file TIDAK diubah:')
        print(r.stderr.strip()[:800])
        sys.exit(1)
    print('Cek sintaks: OK')

shutil.copyfile(path, path + '.bak-v42')
open(path, 'w', encoding='utf-8').write(s)
print('Patch server v4.2 terpasang. Backup: ' + path + '.bak-v42')
