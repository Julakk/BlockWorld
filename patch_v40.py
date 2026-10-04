#!/usr/bin/env python3
# Patch v4.0 - Rebirth, Pet, Pulau Utama (nama + selamat datang)
# Pakai: python3 patch_v40.py index.html
import sys, shutil, re, os, subprocess, tempfile

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()

if 'PM_V40' in src:
    print('Patch v4.0 sudah terpasang, tidak ada yang diubah.')
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

# ---------- 1. modul Rebirth + Pet ----------
MODULE = r"""/* PM_V40 rebirth + pet */
  function pm4b() { return window.PM4 ? window.PM4.bonus() : { luck: 0, speed: 0, sell: 0, xp: 0 }; }
  (function () {
    const RB = { luck: 0.05, speed: 0.04, sell: 0.10, xp: 0.10 };
    const LBL = { luck: 'Luck', speed: 'Speed', sell: 'Harga Jual', xp: 'XP' };
    const EGG = 2500;
    const PETS = [
      { id: 'camar', name: 'Camar', w: 40, t: 'Common', c: '#9fb4bd', b: { sell: 0.03 } },
      { id: 'kepiting', name: 'Kepiting', w: 28, t: 'Rare', c: '#4aa8ff', b: { speed: 0.04 } },
      { id: 'kucing', name: 'Kucing Dermaga', w: 18, t: 'Rare', c: '#4aa8ff', b: { luck: 0.04, xp: 0.04 } },
      { id: 'penyu', name: 'Penyu', w: 9, t: 'Epic', c: '#b56bff', b: { luck: 0.06, speed: 0.05, xp: 0.05 } },
      { id: 'lumba', name: 'Lumba-lumba', w: 4, t: 'Legendary', c: '#ffc233', b: { luck: 0.10, sell: 0.08, speed: 0.06 } },
      { id: 'naga', name: 'Naga Laut', w: 1, t: 'Mythic', c: '#ff4d6d', b: { luck: 0.15, speed: 0.10, sell: 0.15, xp: 0.15 } }
    ];
    const TITLES = [[10, 'Dewa Pancing'], [5, 'Legenda Laut'], [3, 'Penakluk'], [1, 'Perantau'], [0, 'Pemula']];
    let tab = 'rb', last = null, armed = false, armT = null;
    const rbN = () => save.rebirth || 0;
    const need = n => 30 + 5 * n;
    const slots = () => (rbN() >= 3 ? 2 : 1);
    const titleOf = n => (TITLES.find(t => n >= t[0]) || TITLES[4])[1];
    const stars = id => Math.min(5, (save.pets && save.pets[id]) || 0);
    const mult = s2 => 1 + 0.2 * (s2 - 1);
    function rbOnly(n) { const o = {}; for (const k in RB) o[k] = RB[k] * n; return o; }
    function bonus() {
      const o = rbOnly(rbN());
      (save.petEq || []).slice(0, slots()).forEach(id => {
        const p = PETS.find(x => x.id === id), st = stars(id); if (!p || !st) return;
        for (const k in p.b) o[k] = (o[k] || 0) + p.b[k] * mult(st);
      });
      return { luck: o.luck || 0, speed: o.speed || 0, sell: o.sell || 0, xp: o.xp || 0 };
    }
    function fmtB(b) { const q = []; for (const k in LBL) if (b[k]) q.push(LBL[k] + ' +' + Math.round(b[k] * 100) + '%'); return q.join(' • ') || '-'; }
    function roll() { let t = 0; PETS.forEach(p => { t += p.w; }); let r = Math.random() * t; for (const p of PETS) { if (r < p.w) return p; r -= p.w; } return PETS[0]; }
    function buyEgg() {
      if (save.coins < EGG) { showToast('Koin kurang buat Telur Pet'); return; }
      save.coins -= EGG; save.pets = save.pets || {}; save.petEq = save.petEq || [];
      const p = roll(), had = save.pets[p.id] || 0;
      save.pets[p.id] = had + 1;
      if (!had && save.petEq.length < slots()) save.petEq.push(p.id);
      last = { p: p, dup: had > 0 };
      Sfx.sell(); vibe(30);
      if (p.w <= 9) { Sfx.levelUp(); vibe([40, 30, 40]); }
      persistSave(); refreshHud(); render();
    }
    function equip(id) {
      save.petEq = save.petEq || [];
      const i = save.petEq.indexOf(id);
      if (i >= 0) save.petEq.splice(i, 1);
      else { if (save.petEq.length >= slots()) save.petEq.shift(); save.petEq.push(id); }
      persistSave(); render();
    }
    function doRebirth() {
      const n = rbN(); if ((save.level || 1) < need(n)) return;
      if (!armed) { armed = true; clearTimeout(armT); armT = setTimeout(function () { armed = false; render(); }, 4000); render(); return; }
      armed = false; clearTimeout(armT);
      save.rebirth = n + 1;
      save.coins = 20 + 500 * save.rebirth; save.level = 1; save.xp = 0;
      save.rod = 'bambu'; save.ownedRods = ['bambu']; save.bait = 'biasa'; save.baitStock = { biasa: 999 };
      persistSave(); refreshHud(); Sfx.levelUp(); vibe([60, 40, 60, 40, 120]);
      showToast('REBIRTH ke-' + save.rebirth + '! Gelar: ' + titleOf(save.rebirth));
      render();
    }
    function render() {
      const body = document.getElementById('pm4Body'); if (!body) return;
      const n = rbN(), lv = save.level || 1, nd = need(n), ok = lv >= nd;
      let h = '<div class="pm4Tabs"><button data-a="tab" data-v="rb" class="' + (tab === 'rb' ? 'on' : '') + '">Rebirth</button><button data-a="tab" data-v="pet" class="' + (tab === 'pet' ? 'on' : '') + '">Pet</button></div>';
      if (tab === 'rb') {
        h += '<div class="pm4Card"><div class="pm4Big">Rebirth ke-' + n + '</div><div class="pm4Sub">Gelar: <b>' + titleOf(n) + '</b></div>' +
          '<div class="pm4Sub" style="margin-top:6px;">Bonus permanen sekarang:<br><b>' + fmtB(rbOnly(n)) + '</b></div></div>';
        h += '<div class="pm4Card"><div class="pm4Sub">Tiap Rebirth menambah:<br><b>' + fmtB(RB) + '</b></div>' +
          '<div class="pm4Sub" style="margin-top:6px;">Direset: level, XP, koin, joran, umpan.<br>Tetap: tas ikan, koleksi, enchant, pet.</div>' +
          '<div class="pm4Sub" style="margin-top:6px;">Syarat: Level <b>' + nd + '</b> (kamu Level ' + lv + ')</div></div>';
        h += '<button class="pm4Btn" data-a="rebirth" ' + (ok ? '' : 'disabled') + '>' + (ok ? (armed ? 'YAKIN? Tap lagi buat Rebirth' : 'REBIRTH SEKARANG') : 'Belum cukup level') + '</button>';
      } else {
        h += '<div class="pm4Card"><div class="pm4Sub">Slot pet: <b>' + (save.petEq || []).length + '/' + slots() + '</b> (slot ke-2 terbuka di Rebirth 3). Pet duplikat menambah bintang, bonus naik 20% per bintang (maks 5).</div></div>';
        h += '<button class="pm4Btn" data-a="egg" ' + (save.coins < EGG ? 'disabled' : '') + '>Beli Telur Pet (' + EGG + ' koin)</button>';
        if (last) h += '<div class="pm4Card" style="margin-top:10px;border:2px solid ' + last.p.c + ';"><div class="pm4Big" style="color:' + last.p.c + '">' + last.p.name + '</div><div class="pm4Sub">' + last.p.t + (last.dup ? ' • duplikat, bintang naik!' : ' • pet baru!') + '</div></div>';
        h += '<div class="pm4Card" style="margin-top:10px;">';
        let any = false;
        PETS.forEach(function (p) {
          const st = stars(p.id); if (!st) return; any = true;
          const b = {}; for (const k in p.b) b[k] = p.b[k] * mult(st);
          const on = (save.petEq || []).indexOf(p.id) >= 0;
          h += '<div class="pm4Row"><div><b style="color:' + p.c + '">' + p.name + '</b> <span class="pm4Sub">' + new Array(st + 1).join('★') + '</span><div class="pm4Sub">' + fmtB(b) + '</div></div><button data-a="equip" data-id="' + p.id + '" class="' + (on ? 'on' : '') + '">' + (on ? 'Dipakai' : 'Pakai') + '</button></div>';
        });
        if (!any) h += '<div class="pm4Sub">Belum punya pet. Beli Telur Pet dulu.</div>';
        h += '</div>';
      }
      body.innerHTML = h;
    }
    const CSS = [
      '#pm4Ov{position:fixed;left:0;top:0;right:0;bottom:0;z-index:60;display:none;align-items:center;justify-content:center;background:rgba(0,0,0,.55);padding:12px;box-sizing:border-box}',
      '#pm4Ov.show{display:flex}',
      '#pm4Box{width:100%;max-width:430px;max-height:88vh;display:flex;flex-direction:column;border-radius:20px;background:linear-gradient(160deg,#1d5068,#0a1e2c);border:3px solid #5fd0e0;box-shadow:0 8px 0 rgba(0,0,0,.35);color:#fff;overflow:hidden}',
      '#pm4Head{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:rgba(0,0,0,.25)}',
      '#pm4Head h2{margin:0;font-size:17px;font-weight:900}',
      '#pm4X{border:0;background:rgba(255,255,255,.15);color:#fff;width:30px;height:30px;border-radius:50%;font-size:15px}',
      '#pm4Body{padding:12px;overflow-y:auto;-webkit-overflow-scrolling:touch}',
      '.pm4Tabs{display:flex;gap:8px;margin-bottom:10px}',
      '.pm4Tabs button{flex:1;padding:8px;border:0;border-radius:12px;background:rgba(255,255,255,.12);color:#fff;font-weight:800;font-size:13px}',
      '.pm4Tabs button.on{background:linear-gradient(90deg,#ffc233,#ff8a3d);color:#2a1a00}',
      '.pm4Card{background:rgba(0,0,0,.25);border-radius:14px;padding:12px;margin-bottom:10px;line-height:1.5;font-size:13px}',
      '.pm4Big{font-size:20px;font-weight:900}',
      '.pm4Sub{font-size:12px;opacity:.9}',
      '.pm4Btn{width:100%;padding:12px;border:0;border-radius:14px;font-weight:900;font-size:14px;color:#2a1a00;background:linear-gradient(90deg,#ffc233,#ff8a3d)}',
      '.pm4Btn:disabled{opacity:.45}',
      '.pm4Row{display:flex;align-items:center;gap:8px;justify-content:space-between;padding:8px 0;border-top:1px solid rgba(255,255,255,.08)}',
      '.pm4Row button{padding:6px 12px;border:0;border-radius:10px;font-weight:800;font-size:12px;background:rgba(255,255,255,.18);color:#fff}',
      '.pm4Row button.on{background:#5fd36b;color:#06240c}'
    ].join('');
    function ensure() {
      if (document.getElementById('pm4Ov')) return;
      const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
      const ov = document.createElement('div'); ov.id = 'pm4Ov';
      ov.innerHTML = '<div id="pm4Box"><div id="pm4Head"><h2>Rebirth &amp; Pet</h2><button id="pm4X" data-a="close">✕</button></div><div id="pm4Body"></div></div>';
      document.body.appendChild(ov);
      ov.addEventListener('click', function (ev) {
        if (ev.target === ov) { ov.classList.remove('show'); return; }
        const b = ev.target.closest('[data-a]'); if (!b || b.disabled) return;
        const a = b.dataset.a;
        if (a === 'close') ov.classList.remove('show');
        else if (a === 'tab') { tab = b.dataset.v; render(); }
        else if (a === 'rebirth') doRebirth();
        else if (a === 'egg') buyEgg();
        else if (a === 'equip') equip(b.dataset.id);
      });
    }
    function open() { ensure(); armed = false; render(); document.getElementById('pm4Ov').classList.add('show'); }
    function addBtn() {
      const host = document.getElementById('menuPanel') || document.getElementById('hudPills');
      if (!host || document.getElementById('pm4Btn')) return;
      const b = document.createElement('button'); b.id = 'pm4Btn'; b.className = 'hudPill'; b.textContent = 'Rebirth';
      b.onclick = function () { const mp = document.getElementById('menuPanel'); if (mp) mp.classList.remove('show'); open(); };
      host.appendChild(b);
    }
    if (document.readyState === 'complete') setTimeout(addBtn, 1200); else window.addEventListener('load', function () { setTimeout(addBtn, 1200); });
    window.PM4 = { bonus: bonus, open: open, title: function () { return titleOf(rbN()); } };
  })();
  /* ENCHANT_V38 */"""
replace_once("/* ENCHANT_V38 */", MODULE, 'modul rebirth/pet')

# ---------- 2. bonus Sell & XP ikut Rebirth + Pet ----------
replace_once(
    "function enchBonus(k) { const en = save.enchants && save.enchants[save.rod]; return (en && en[k]) || 0; }",
    "function enchBonus(k) { const en = save.enchants && save.enchants[save.rod]; return ((en && en[k]) || 0) + (pm4b()[k] || 0); }",
    'enchBonus')

# ---------- 3. bonus Luck & Speed ikut Rebirth + Pet ----------
replace_once(
    "if (!en) return r;",
    "if (!en) { const bx = pm4b(); if (!bx.luck && !bx.speed) return r; return Object.assign({}, r, { rarityBoost: r.rarityBoost + bx.luck, biteSpeed: r.biteSpeed * (1 + bx.speed) }); }",
    'currentRod tanpa enchant')
replace_once(
    "rarityBoost: r.rarityBoost + (en.luck || 0), biteSpeed: r.biteSpeed * (1 + (en.speed || 0))",
    "rarityBoost: r.rarityBoost + (en.luck || 0) + pm4b().luck, biteSpeed: r.biteSpeed * (1 + (en.speed || 0) + pm4b().speed)",
    'currentRod dengan enchant')

# ---------- 4. Pulau: papan nama + selamat datang ----------
ISLE = r"""town.add(altar);
  /* PM_V40 pulau */
  const PM_ISLES = [{ id: 'utama', name: 'Pulau Utama', x: 0, z: 0, r: ISLAND_RADIUS + 2 }];
  PM_ISLES.forEach(function (is) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: makeSignTexture(is.name.toUpperCase(), '#1f6f8f'), fog: false }));
    sp.scale.set(9, 2.25, 1); sp.position.set(is.x, 12, is.z + 8); town.add(sp);
  });
  (function () {
    const st = document.createElement('style');
    st.textContent = [
      '#pm4Welcome{position:fixed;left:50%;top:16%;transform:translateX(-50%);z-index:70;pointer-events:none;text-align:center;opacity:0}',
      '#pm4Welcome.show{animation:pm4Wel 3.4s ease forwards}',
      '#pm4Welcome small{display:block;font-size:12px;font-weight:800;letter-spacing:3px;color:#bfe9f3;text-shadow:0 2px 6px #000}',
      '#pm4Welcome b{display:block;font-size:30px;font-weight:900;color:#fff;letter-spacing:1px;text-shadow:0 3px 0 rgba(0,0,0,.45),0 0 18px #4fd0e0}',
      '@keyframes pm4Wel{0%{opacity:0;transform:translateX(-50%) translateY(-14px) scale(.9)}12%{opacity:1;transform:translateX(-50%) translateY(0) scale(1)}80%{opacity:1}100%{opacity:0;transform:translateX(-50%) translateY(-6px)}}'
    ].join('');
    document.head.appendChild(st);
  })();
  function pmWelcome(is) {
    let el = document.getElementById('pm4Welcome');
    if (!el) { el = document.createElement('div'); el.id = 'pm4Welcome'; document.body.appendChild(el); }
    el.innerHTML = '<small>SELAMAT DATANG DI</small><b></b>';
    el.querySelector('b').textContent = is.name;
    el.classList.remove('show'); void el.offsetWidth; el.classList.add('show');
    try { Sfx.levelUp(); } catch (e) {}
  }
  let pmIsleCur = null;
  function pmIsleTick() {
    try {
      if (performance.now() < 6000) return;
      const px = player.position.x, pz = player.position.z; let cur = null;
      for (const is of PM_ISLES) { if (Math.hypot(px - is.x, pz - is.z) < is.r) { cur = is; break; } }
      const id = cur ? cur.id : null;
      if (id !== pmIsleCur) { pmIsleCur = id; if (cur) pmWelcome(cur); }
    } catch (e) {}
  }
  const _utaI = updateTownAnim;
  updateTownAnim = function (t) { _utaI(t); pmIsleTick(); };"""
replace_once("town.add(altar);", ISLE, 'pulau')

# ---------- 5. Info Update + versi ----------
NEW_LOG = r"""  var LOG = [
    ["Update v4.0", [
      "Fitur baru Rebirth: reset level dan progres untuk bonus permanen Luck, Speed, Harga Jual, dan XP, plus gelar baru. Tombolnya ada di Menu.",
      "Pet pendamping: beli Telur Pet, ada 6 jenis pet, dan bonusnya naik bintang kalau dapat duplikat. Slot ke-2 terbuka di Rebirth 3.",
      "Nama pulau tampil di atas pulau, dan muncul pesan selamat datang saat tiba. Pulau pertama bernama Pulau Utama."
    ]]
  ];"""
a = s.find("  var LOG = [\n")
if a < 0:
    errors.append('awal LOG tidak ketemu')
else:
    m = re.search(r"\n  \];", s[a:])
    if not m or m.end() > 60000:
        errors.append('akhir LOG tidak ketemu')
    else:
        s = s[:a] + NEW_LOG + s[a + m.end():]
replace_once("var VER = 'v3.9',", "var VER = 'v4.0',", 'VER')
replace_once('<div id="versionBadge">v3.9</div>', '<div id="versionBadge">v4.0</div>', 'badge versi')

if errors:
    print('GAGAL, file TIDAK diubah:')
    for e in errors: print(' -', e)
    sys.exit(1)

# ---------- cek sintaks JS (kalau node ada) ----------
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

shutil.copyfile(path, path + '.bak-v40')
open(path, 'w', encoding='utf-8').write(s)
print('Patch v4.0 terpasang. Backup: ' + path + '.bak-v40')
