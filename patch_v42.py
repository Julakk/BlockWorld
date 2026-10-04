#!/usr/bin/env python3
# Patch v4.2 klien - Peringkat online, Boss Fish, Pasar Pemain
# Pakai: python3 patch_v42.py index.html
import sys, shutil, re, os, subprocess, tempfile

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()

if 'PM_V42' in src:
    print('Patch v4.2 sudah terpasang, tidak ada yang diubah.')
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

# ---------- 1. jembatan jaringan ----------
replace_once(
    "window.PMNet = { cast: function () {",
    "window.PMNet = { raw: function (o) { send(o); }, up: function () { return !!(ws && ws.readyState === 1); }, cast: function () {",
    'PMNet raw/up')
replace_once(
    "else if (m.t === 'secret') addSecret(m);",
    "else if (m.t === 'secret') addSecret(m);\n"
    "      else if (/^(lb|boss|bossr|mlist|mok|mfail|mbought|mcancelled|mpay|msold)$/.test(m.t)) { if (window.PMLB) window.PMLB.on(m); }",
    'router pesan')

# ---------- 2. modul klien ----------
MODULE = r"""/* PM_V42 peringkat + boss + pasar pemain */
  var UID = (function () {
    function rnd() { var u = ''; for (var j = 0; j < 28; j++) u += Math.floor(Math.random() * 16).toString(16); return u; }
    try {
      var u = localStorage.getItem('pm_uid');
      if (u && /^[A-Za-z0-9]{16,40}$/.test(u)) return u;
      u = '';
      if (window.crypto && crypto.getRandomValues) { var a = new Uint8Array(14); crypto.getRandomValues(a); for (var i = 0; i < a.length; i++) u += ('0' + a[i].toString(16)).slice(-2); }
      else u = rnd();
      localStorage.setItem('pm_uid', u); return u;
    } catch (e) { return rnd(); }
  })();
  function netUp() { var n = window.PMNet; return !!(n && n.up && n.up()); }
  function netSend(o) { if (window.PMNet && window.PMNet.raw) window.PMNet.raw(o); }
  function fmt(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function escH(x) { return String(x).replace(/[&<>"']/g, function (c) { return '&#' + c.charCodeAt(0) + ';'; }); }
  function fishById(id) { return C.FISH_TABLE.filter(function (f) { return f.id === id; })[0]; }
  function mutById(id) { return C.MUTATIONS.filter(function (m) { return m.id === id; })[0]; }
  function addItem(fid, mid) {
    var f = fishById(fid), mu = mutById(mid); if (!f || !mu) return false;
    var s = S(), k = fid + '|' + mid;
    s.inventory[k] = s.inventory[k] || { fish: f, mutation: mu, count: 0 };
    s.inventory[k].count++; s.discovered = s.discovered || {}; s.discovered[fid] = true; return true;
  }
  var css42 = document.createElement('style');
  css42.textContent = [
    '#pm42Boss{position:fixed;top:calc(120px + env(safe-area-inset-top,0px));left:50%;transform:translateX(-50%);z-index:56;width:min(78vw,300px);display:none;text-align:center;color:#fff;padding:8px 12px 10px;border-radius:16px;border:3px solid #ff4d6d;background:linear-gradient(160deg,#4a1020,#1a0610);box-shadow:0 4px 0 rgba(0,0,0,.4),0 0 22px rgba(255,77,109,.55)}',
    '#pm42BName{font-weight:900;font-size:15px;letter-spacing:.5px;text-shadow:0 2px 0 rgba(0,0,0,.5)}',
    '#pm42BBar{height:14px;border-radius:8px;background:rgba(0,0,0,.55);margin:6px 0;overflow:hidden}',
    '#pm42BFill{display:block;height:100%;width:100%;background:linear-gradient(90deg,#ff4d6d,#ff8a3d);transition:width .25s}',
    '#pm42BHit{width:100%;padding:12px;border:0;border-radius:12px;font-weight:900;font-size:16px;color:#2a0a00;background:linear-gradient(90deg,#ffc233,#ff8a3d)}',
    '#pm42BHit:active{transform:scale(.97)}',
    '#pm42BSub{font-size:11px;opacity:.85;margin-top:5px}',
    '.pm42Tabs{display:flex;gap:6px;margin-bottom:8px}'
  ].join('');
  document.head.appendChild(css42);

  /* --- peringkat --- */
  var mLB = mkModal('modalLB', 'Peringkat Online'), lbData = null, lbTab = 'c';
  function renderLB() {
    var h = '<div class="pm42Tabs">' + [['c', 'Tangkapan'], ['w', 'Terberat'], ['p', 'Prestise']].map(function (t) {
      return '<button class="rowBtn' + (lbTab === t[0] ? ' owned' : '') + '" data-lt="' + t[0] + '" style="flex:1">' + t[1] + '</button>';
    }).join('') + '</div>';
    if (!netUp()) h += '<div class="rowSub" style="text-align:center;padding:14px">Belum tersambung ke server.</div>';
    else if (!lbData) h += '<div class="rowSub" style="text-align:center;padding:14px">Memuat peringkat...</div>';
    else {
      var l = lbData[lbTab] || [];
      if (!l.length) h += '<div class="rowSub" style="text-align:center;padding:14px">Belum ada data.</div>';
      l.forEach(function (e, i) {
        var sub = lbTab === 'c' ? fmt(e[1]) + ' ikan' : lbTab === 'w' ? C.fmtKg(e[1]) + (e[2] ? ' • ' + e[2] : '') : 'Rebirth ' + e[1] + ' • Level ' + e[2];
        h += row('', (i + 1) + '. ' + escH(e[0]), escH(sub));
      });
    }
    mLB.body.innerHTML = h; mLB.foot.textContent = 'Data dilaporkan tiap pemain, diperbarui tiap 45 detik';
  }
  mLB.body.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-lt]'); if (!b) return; lbTab = b.dataset.lt; renderLB();
  });
  function openLB() { netSend({ t: 'lbget' }); renderLB(); }
  function lbReport() {
    if (!netUp()) return;
    var s = S(), t = st(), best = (s.rec || [])[0], tr = 0;
    Object.keys(s.ach || {}).forEach(function (k) { if (s.ach[k]) tr++; });
    netSend({ t: 'stat', c: t.catches, w: best ? best.w : 0, wf: best ? best.n : '', rb: s.rebirth || 0, lv: s.level || 1, tr: tr });
  }
  setInterval(lbReport, 45000); setTimeout(lbReport, 8000);

  /* --- boss --- */
  var bossEl = document.createElement('div'); bossEl.id = 'pm42Boss';
  bossEl.innerHTML = '<div id="pm42BName"></div><div id="pm42BBar"><i id="pm42BFill"></i></div><button id="pm42BHit">SERANG!</button><div id="pm42BSub"></div>';
  document.body.appendChild(bossEl);
  var bossLeftAt = 0, bossMax = 1, lastHit = 0;
  function bossShow(m) {
    bossEl.style.display = 'block';
    $('pm42BName').textContent = 'BOSS: ' + m.name;
    bossMax = m.max || bossMax;
    $('pm42BFill').style.width = Math.max(0, Math.min(100, m.hp / bossMax * 100)) + '%';
    if (m.left != null) bossLeftAt = Date.now() + m.left;
  }
  setInterval(function () {
    if (bossEl.style.display === 'none') return;
    var r = Math.max(0, Math.ceil((bossLeftAt - Date.now()) / 1000));
    $('pm42BSub').textContent = 'Sisa waktu ' + r + ' dtk • tap sekencang mungkin!';
  }, 500);
  $('pm42BHit').onclick = function () {
    var n = Date.now(); if (n - lastHit < 170) return; lastHit = n;
    netSend({ t: 'bhit' }); C.vibe(8);
  };

  /* --- pasar pemain --- */
  var mM = mkModal('modalMarket', 'Pasar Pemain'), mkData = null, mkTab = 'buy', mkMult = 1, pend = {}, busy = false;
  function newRid() { return 'r' + Date.now().toString(36) + Math.floor(Math.random() * 1e4).toString(36); }
  function startReq(o) {
    if (!netUp()) { C.toast('Belum tersambung ke server'); return null; }
    if (busy) { C.toast('Tunggu proses sebelumnya'); return null; }
    busy = true; setTimeout(function () { busy = false; }, 12000);
    var r = newRid(); pend[r] = o; return r;
  }
  function renderMK() {
    var s = S(), h = '<div class="pm42Tabs">' + [['buy', 'Beli'], ['sell', 'Jual'], ['me', 'Saya']].map(function (t) {
      return '<button class="rowBtn' + (mkTab === t[0] ? ' owned' : '') + '" data-mt="' + t[0] + '" style="flex:1">' + t[1] + '</button>';
    }).join('') + '</div>';
    if (!netUp()) h += '<div class="rowSub" style="text-align:center;padding:14px">Belum tersambung ke server.</div>';
    else if (!mkData) h += '<div class="rowSub" style="text-align:center;padding:14px">Memuat pasar...</div>';
    else if (mkTab === 'buy') {
      var any = false;
      mkData.list.forEach(function (l) {
        if (l.mine) return;
        var f = fishById(l.f), mu = mutById(l.mu); if (!f || !mu) return; any = true;
        var e = { fish: f, mutation: mu };
        h += row(icon(e), escH(lbl(e)), C.RARITY_LABEL[f.rarity] + ' • ' + fmt(l.price) + ' koin • oleh ' + escH(l.s),
          '<button class="rowBtn" data-buy="' + l.id + '" data-price="' + l.price + '"' + (s.coins < l.price ? ' disabled' : '') + '>Beli</button>');
      });
      if (!any) h += '<div class="rowSub" style="text-align:center;padding:14px">Belum ada barang dari pemain lain.</div>';
    } else if (mkTab === 'sell') {
      h += '<div class="rowSub" style="margin-bottom:6px">Harga jual = nilai ikan x pengali. Biaya pasar 5% dipotong dari hasil.</div><div class="pm42Tabs">' +
        [1, 1.5, 2, 3].map(function (m) { return '<button class="rowBtn' + (mkMult === m ? ' owned' : '') + '" data-mm="' + m + '" style="flex:1">x' + m + '</button>'; }).join('') + '</div>';
      var any2 = false;
      Object.keys(s.inventory).forEach(function (k) {
        var e = s.inventory[k]; if (!e || e.count <= 0 || !e.fish || !e.mutation) return; any2 = true;
        var price = Math.min(5000000, Math.max(10, Math.round(e.fish.value * (e.mutation.mult || 1) * mkMult)));
        h += row(icon(e), escH(lbl(e)), 'x' + e.count + ' • ' + C.RARITY_LABEL[e.fish.rarity] + ' • pasang ' + fmt(price) + ' koin',
          '<button class="rowBtn" data-put="' + escH(k) + '" data-price="' + price + '">Pasang</button>');
      });
      if (!any2) h += '<div class="rowSub" style="text-align:center;padding:14px">Tas kosong.</div>';
    } else {
      h += row('', 'Hasil penjualan', fmt(mkData.pay || 0) + ' koin' + (mkData.mail ? ' • ' + mkData.mail + ' barang kembali' : ''),
        '<button class="rowBtn" data-collect="1"' + ((mkData.pay || mkData.mail) ? '' : ' disabled') + '>Ambil</button>');
      h += '<div class="rowName" style="margin-top:6px">Listing kamu</div>';
      var any3 = false;
      mkData.list.forEach(function (l) {
        if (!l.mine) return;
        var f = fishById(l.f), mu = mutById(l.mu); if (!f || !mu) return; any3 = true;
        var e = { fish: f, mutation: mu };
        h += row(icon(e), escH(lbl(e)), fmt(l.price) + ' koin', '<button class="rowBtn" data-cancel="' + l.id + '">Batal</button>');
      });
      if (!any3) h += '<div class="rowSub">Belum ada listing.</div>';
    }
    mM.body.innerHTML = h; mM.foot.textContent = 'Koin: ' + fmt(s.coins);
  }
  function openMK() { netSend({ t: 'mget', u: UID }); renderMK(); }
  mM.body.addEventListener('click', function (ev) {
    var b = ev.target.closest('button'); if (!b || b.disabled) return; var s = S(), d = b.dataset, r;
    if (d.mt) { mkTab = d.mt; renderMK(); return; }
    if (d.mm) { mkMult = +d.mm; renderMK(); return; }
    if (d.put) {
      var e = s.inventory[d.put]; if (!e || e.count <= 0) return;
      r = startReq({ k: 'list', key: d.put, f: e.fish.id, mu: e.mutation.id }); if (!r) return;
      e.count--; C.persist(); C.refresh();
      netSend({ t: 'mput', rid: r, u: UID, f: e.fish.id, mu: e.mutation.id, price: +d.price });
      renderMK();
    } else if (d.buy) {
      var price = +d.price; if (s.coins < price) return;
      r = startReq({ k: 'buy', price: price }); if (!r) return;
      s.coins -= price; C.persist(); C.refresh();
      netSend({ t: 'mbuy', rid: r, u: UID, id: +d.buy });
      renderMK();
    } else if (d.cancel) {
      r = startReq({ k: 'cancel' }); if (!r) return;
      netSend({ t: 'mcancel', rid: r, u: UID, id: +d.cancel });
    } else if (d.collect) {
      r = startReq({ k: 'collect' }); if (!r) return;
      netSend({ t: 'mcollect', rid: r, u: UID });
    }
  });

  /* --- router pesan server --- */
  window.PMLB = { on: function (m) {
    var s = S(), q;
    if (m.t === 'lb') { lbData = m; if (mLB.ov.classList.contains('show')) renderLB(); }
    else if (m.t === 'boss') {
      if (m.st === 'spawn') { bossShow(m); C.toast('BOSS ' + m.name + ' muncul! Tap SERANG bareng-bareng!', 'secret'); C.Sfx.levelUp(); C.vibe([80, 40, 80]); }
      else if (m.st === 'hp') bossShow(m);
      else if (m.st === 'end') { bossEl.style.display = 'none'; C.toast(m.win ? 'Boss kalah! MVP: ' + (m.top || '-') : 'Boss kabur...'); }
    }
    else if (m.t === 'bossr') {
      s.coins += Math.max(0, Math.min(+m.coins || 0, 100000)); C.persist(); C.refresh(); C.Sfx.sell();
      C.toast((m.win ? 'Hadiah Boss: +' : 'Hadiah hiburan: +') + fmt(m.coins) + ' koin (' + m.hits + ' serangan)' + (m.mvp ? ' • MVP!' : ''));
    }
    else if (m.t === 'mlist') { mkData = m; if (mM.ov.classList.contains('show')) renderMK(); }
    else if (m.t === 'mok') { delete pend[m.rid]; busy = false; C.toast('Barang dipasang di pasar'); netSend({ t: 'mget', u: UID }); }
    else if (m.t === 'mfail') {
      q = pend[m.rid]; delete pend[m.rid]; busy = false;
      if (q && q.k === 'list') { var e = s.inventory[q.key]; if (e) e.count++; else addItem(q.f, q.mu); }
      else if (q && q.k === 'buy') s.coins += q.price;
      C.toast('Gagal: ' + (m.why || 'ditolak')); C.persist(); C.refresh(); renderMK();
    }
    else if (m.t === 'mbought') {
      q = pend[m.rid]; delete pend[m.rid]; busy = false;
      if (q && q.k === 'buy') s.coins += q.price - m.price;
      if (addItem(m.f, m.mu)) { var fb = fishById(m.f); C.toast('Dibeli: ' + (fb ? fb.name : m.f)); C.Sfx.sell(); }
      else s.coins += m.price;
      C.persist(); C.refresh(); netSend({ t: 'mget', u: UID });
    }
    else if (m.t === 'mcancelled') {
      delete pend[m.rid]; busy = false; addItem(m.f, m.mu); C.toast('Listing dibatalkan, barang kembali ke tas');
      C.persist(); C.refresh(); netSend({ t: 'mget', u: UID });
    }
    else if (m.t === 'mpay') {
      delete pend[m.rid]; busy = false; var n = 0;
      s.coins += Math.max(0, Math.min(+m.coins || 0, 1e9));
      (m.items || []).forEach(function (it) { if (addItem(it.f, it.mu)) n++; });
      C.toast((m.coins || n) ? 'Diambil: +' + fmt(m.coins || 0) + ' koin' + (n ? ' • ' + n + ' barang' : '') : 'Belum ada yang bisa diambil');
      C.persist(); C.refresh(); netSend({ t: 'mget', u: UID });
    }
    else if (m.t === 'msold') { C.toast('Barangmu terjual! Ambil ' + fmt(m.coins) + ' koin di Pasar Pemain > Saya'); C.Sfx.sell(); }
  } };

  /* ===== LOOP + MENU ===== */"""
replace_once("/* ===== LOOP + MENU ===== */", MODULE, 'modul v4.2')

replace_once(
    "['Rekor', renderR, mR]].forEach(function (x) {",
    "['Rekor', renderR, mR], ['Peringkat', openLB, mLB], ['Pasar Pemain', openMK, mM]].forEach(function (x) {",
    'menu')

# ---------- 3. Info Update + versi ----------
NEW_LOG = r"""  var LOG = [
    ["Update v4.2", [
      "Peringkat Online: lihat pemain dengan tangkapan terbanyak, ikan terberat, dan Rebirth tertinggi.",
      "Boss Fish: boss raksasa muncul berkala untuk semua pemain online. Tap SERANG bareng-bareng, hadiah dibagi sesuai jumlah seranganmu dan MVP dapat bonus.",
      "Pasar Pemain: jual dan beli ikan antar pemain. Barang disimpan server sampai terjual, biaya pasar 5%, maksimal 5 listing per pemain."
    ]],
"""
if s.count("  var LOG = [\n") != 1:
    errors.append('awal LOG: ketemu %d kali (harus 1)' % s.count("  var LOG = [\n"))
else:
    s = s.replace("  var LOG = [\n", NEW_LOG, 1)
s, n1 = re.subn(r"var VER = 'v[0-9.]+',", "var VER = 'v4.2',", s)
s, n2 = re.subn(r'<div id="versionBadge">v[0-9.]+</div>', '<div id="versionBadge">v4.2</div>', s)
if n1 != 1: errors.append('VER: ketemu %d kali' % n1)
if n2 != 1: errors.append('badge versi: ketemu %d kali' % n2)

if errors:
    print('GAGAL, file TIDAK diubah:')
    for e in errors: print(' -', e)
    sys.exit(1)

def js_bad(html):
    bad = set()
    for i, m in enumerate(re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S)):
        code = m.group(1)
        if not code.strip(): continue
        fn = tempfile.mktemp(suffix='.js')
        open(fn, 'w', encoding='utf-8').write(code)
        r = subprocess.run(['node', '--check', fn], capture_output=True, text=True)
        os.remove(fn)
        if r.returncode != 0: bad.add((i, r.stderr.strip()[:500]))
    return bad

if shutil.which('node'):
    old_bad = {i for i, _ in js_bad(src)}
    fresh = [x for x in js_bad(s) if x[0] not in old_bad]
    if fresh:
        print('GAGAL, error sintaks JS, file TIDAK diubah:')
        for i, msg in fresh: print(' - script #%d: %s' % (i, msg))
        sys.exit(1)
    print('Cek sintaks JS: OK')
else:
    print('node tidak ada, cek sintaks dilewati.')

shutil.copyfile(path, path + '.bak-v42')
open(path, 'w', encoding='utf-8').write(s)
print('Patch v4.2 terpasang. Backup: ' + path + '.bak-v42')
