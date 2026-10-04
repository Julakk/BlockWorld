#!/usr/bin/env python3
# Patch Enchant v3.8 - Pancing Mania
# Pakai: python3 patch_enchant.py index.html
import sys, shutil, re

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()

if 'ENCHANT_V38' in src:
    print('Patch sudah pernah dipasang, tidak ada yang diubah.')
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

def replace_n(old, new, expected, label):
    global s
    n = s.count(old)
    if n != expected:
        errors.append('%s: ketemu %d kali (harus %d)' % (label, n, expected))
        return
    s = s.replace(old, new)

# ---------- 1. helper bonus enchant (sell / xp) ----------
replace_once(
    "  function currentBait() {",
    "  /* ENCHANT_V38 */\n"
    "  function enchBonus(k) { const en = save.enchants && save.enchants[save.rod]; return (en && en[k]) || 0; }\n"
    "  function currentBait() {",
    'helper enchBonus')

# ---------- 2. harga jual ikan (3 tempat) ----------
replace_once(
    "const val = Math.round(e.fish.value * (window.PMP ? window.PMP(e.fish.id) : 1) * e.mutation.mult);",
    "const val = Math.round(e.fish.value * (window.PMP ? window.PMP(e.fish.id) : 1) * e.mutation.mult * (1 + enchBonus('sell')));",
    'harga di tas')
replace_once(
    "const val = Math.round(entry.fish.value * (window.PMP ? window.PMP(entry.fish.id) : 1) * entry.mutation.mult);",
    "const val = Math.round(entry.fish.value * (window.PMP ? window.PMP(entry.fish.id) : 1) * entry.mutation.mult * (1 + enchBonus('sell')));",
    'jual satuan')
replace_once(
    "sum += Math.round(e.fish.value * (window.PMP ? window.PMP(e.fish.id) : 1) * e.mutation.mult) * e.count;",
    "sum += Math.round(e.fish.value * (window.PMP ? window.PMP(e.fish.id) : 1) * e.mutation.mult * (1 + enchBonus('sell'))) * e.count;",
    'jual semua')

# ---------- 3. XP tangkapan ----------
replace_once(
    "addXp(Math.round(currentCatch.value / 4) + 5);",
    "addXp(Math.round((Math.round(currentCatch.value / 4) + 5) * (1 + enchBonus('xp'))));",
    'xp tangkapan')

# ---------- 4. ganti seluruh blok data + logika enchant ----------
a = s.find("  const ENCHANTS = [")
b = s.find("  const ovE = document.createElement('div');")
if a < 0 or b < 0 or b < a:
    errors.append('blok ENCHANTS / ovE tidak ketemu')
else:
    NEW_BLOCK = r"""  const TIER_NAME = { 1: 'Common', 2: 'Rare', 3: 'Epic', 4: 'Legendary', 5: 'Mythic' };
  const TIER_COLOR = { 1: '#9fb4bd', 2: '#4aa8ff', 3: '#b56bff', 4: '#ffc233', 5: '#ff4d6d' };
  const ENCHANTS = [
    { id: 'luck1', name: 'Luck I', luck: 0.10, speed: 0, w: 26, t: 1, c: '#9fb4bd' },
    { id: 'swift1', name: 'Swift I', luck: 0, speed: 0.10, w: 26, t: 1, c: '#9fb4bd' },
    { id: 'luck2', name: 'Luck II', luck: 0.20, speed: 0, w: 14, t: 2, c: '#4aa8ff' },
    { id: 'swift2', name: 'Swift II', luck: 0, speed: 0.20, w: 14, t: 2, c: '#4aa8ff' },
    { id: 'merchant', name: 'Merchant', sell: 0.15, w: 9, t: 2, c: '#4aa8ff' },
    { id: 'scholar', name: 'Scholar', xp: 0.25, w: 9, t: 2, c: '#4aa8ff' },
    { id: 'fortune', name: 'Fortune', luck: 0.15, speed: 0.15, w: 10, t: 3, c: '#b56bff' },
    { id: 'prosper', name: 'Prosperity', luck: 0.20, sell: 0.20, w: 4, t: 3, c: '#b56bff' },
    { id: 'sage', name: 'Sage', speed: 0.20, xp: 0.40, w: 4, t: 3, c: '#b56bff' },
    { id: 'luck3', name: 'Luck III', luck: 0.35, speed: 0, w: 5, t: 4, c: '#ffc233' },
    { id: 'swift3', name: 'Swift III', luck: 0, speed: 0.35, w: 5, t: 4, c: '#ffc233' },
    { id: 'tycoon', name: 'Tycoon', luck: 0.20, sell: 0.50, w: 1.5, t: 5, c: '#ff4d6d' },
    { id: 'godhand', name: 'Godhand', luck: 0.50, speed: 0.50, w: 1, t: 5, c: '#ff4d6d' },
    { id: 'omni', name: 'Omniscient', luck: 0.30, speed: 0.30, sell: 0.30, xp: 0.50, w: 0.5, t: 5, c: '#ff4d6d' }
  ];
  const PITY_MAX = 20; // tiap 20 roll tanpa Epic+ , roll berikutnya dijamin Epic ke atas
  function enchDesc(e) {
    const q = [];
    if (e.luck) q.push('Luck +' + Math.round(e.luck * 100) + '%');
    if (e.speed) q.push('Speed +' + Math.round(e.speed * 100) + '%');
    if (e.sell) q.push('Harga Jual +' + Math.round(e.sell * 100) + '%');
    if (e.xp) q.push('XP +' + Math.round(e.xp * 100) + '%');
    return q.join(' • ');
  }
  function enchColor(id) { const e = ENCHANTS.find(x => x.id === id); return e ? e.c : '#9fb4bd'; }
  function enchTier(id) { const e = ENCHANTS.find(x => x.id === id); return e ? e.t : 0; }
  function rollEnchant(minTier) {
    minTier = minTier || 1;
    const pool = ENCHANTS.filter(e => e.t >= minTier);
    let tot = 0; pool.forEach(e => { tot += e.w; });
    let r = Math.random() * tot;
    for (const e of pool) { if (r < e.w) return e; r -= e.w; }
    return pool[0];
  }
  function getPendingEnchant() {
    const pp = save.pendingEnchant; if (!pp) return null;
    const e = ENCHANTS.find(x => x.id === pp.id);
    return e ? { rodId: pp.rodId, ench: e } : null;
  }
  function enchantCost(rod) { return 200 * (1 + ROD_TIERS.indexOf(rod)); }
  function enchRatesHtml() {
    let tot = 0; ENCHANTS.forEach(e => { tot += e.w; });
    let h = '<div class="rowSub" style="text-align:center;line-height:1.7;">';
    for (let t = 1; t <= 5; t++) {
      let sum = 0; ENCHANTS.forEach(e => { if (e.t === t) sum += e.w; });
      h += '<span style="color:' + TIER_COLOR[t] + ';font-weight:800;">' + TIER_NAME[t] + ' ' + (sum / tot * 100).toFixed(1) + '%</span>' + (t < 5 ? ' • ' : '');
    }
    return h + '</div>';
  }

  /* efek visual roll */
  (function () {
    const st = document.createElement('style');
    st.textContent =
      '@keyframes enPop{0%{transform:scale(.6);opacity:0}60%{transform:scale(1.12);opacity:1}100%{transform:scale(1)}}' +
      '@keyframes enShake{0%,100%{transform:translateX(0)}20%{transform:translateX(-5px)}40%{transform:translateX(5px)}60%{transform:translateX(-4px)}80%{transform:translateX(4px)}}' +
      '@keyframes enGlow{0%,100%{box-shadow:0 0 10px var(--ec)}50%{box-shadow:0 0 26px var(--ec),0 0 44px var(--ec)}}' +
      '#enSlot{font-size:26px;font-weight:900;text-align:center;padding:22px 8px;border:3px solid #fff;border-radius:18px;background:rgba(0,0,0,.35);letter-spacing:.5px;}' +
      '.enReveal{animation:enPop .55s ease-out,enGlow 1.2s ease-in-out 2;border-color:var(--ec)!important;}' +
      '.enMythic{animation:enPop .55s ease-out,enShake .5s ease-in-out .3s,enGlow .8s ease-in-out 4;}';
    document.head.appendChild(st);
  })();
  let enAnimTimer = null, enAnimating = false, enJustRevealed = false;
  function startEnchantAnim() {
    enAnimating = true; renderEnchant();
    const end = Date.now() + 1700;
    clearInterval(enAnimTimer);
    enAnimTimer = setInterval(() => {
      const el = document.getElementById('enSlot');
      if (!el || Date.now() >= end) {
        clearInterval(enAnimTimer); enAnimating = false; enJustRevealed = true;
        const pend = getPendingEnchant();
        renderEnchant();
        if (pend) {
          if (pend.ench.t >= 4) { Sfx.levelUp(); vibe([60, 40, 60, 40, 90]); }
          else if (pend.ench.t >= 3) { Sfx.levelUp(); vibe([40, 30, 40]); }
          else vibe(30);
          if (pend.ench.t === 5) showToast('MYTHIC! ' + pend.ench.name + '!');
        }
        enJustRevealed = false;
        return;
      }
      const e = ENCHANTS[Math.floor(Math.random() * ENCHANTS.length)];
      el.textContent = e.name; el.style.color = e.c; el.style.setProperty('--ec', e.c);
      vibe(6);
    }, 85);
  }

"""
    s = s[:a] + NEW_BLOCK + s[b:]

# ---------- 5. renderEnchant baru ----------
a = s.find("  function renderEnchant() {")
b = s.find("  document.getElementById('enBody').addEventListener('click'")
if a < 0 or b < 0 or b < a:
    errors.append('blok renderEnchant tidak ketemu')
else:
    NEW_RENDER = r"""  function renderEnchant() {
    save.enchants = save.enchants || {};
    save.enPity = save.enPity || 0;
    const rod = ROD_TIERS.find(r => r.id === save.rod) || ROD_TIERS[0];
    const cur = save.enchants[rod.id];
    const cost = enchantCost(rod);
    const lockCost = cost * 2;
    const pend = getPendingEnchant();
    let h = '<div class="rowItem"><div class="rowIcon" style="' + gearIconStyle('rod', rod.id) + '"></div><div class="rowInfo"><div class="rowName">' + rod.name + '</div><div class="rowSub">' +
      (cur ? 'Enchant: <b style="color:' + enchColor(cur.id) + '">' + cur.name + '</b> • ' + enchDesc(cur) : 'Belum di-enchant') + '</div></div></div>';
    if (enAnimating) {
      h += '<div id="enSlot">...</div>';
      h += '<div class="rowSub" style="text-align:center;">Mengundi enchant...</div>';
    } else if (pend) {
      const pr = ROD_TIERS.find(r => r.id === pend.rodId);
      const cls = pend.ench.t === 5 ? 'enReveal enMythic' : (pend.ench.t >= 3 && enJustRevealed ? 'enReveal' : '');
      h += '<div class="rowItem ' + cls + '" style="--ec:' + pend.ench.c + ';border-color:' + pend.ench.c + ';"><div class="rowInfo"><div class="rowName" style="color:' + pend.ench.c + '">Hasil: ' + pend.ench.name + ' <span style="font-size:10px;opacity:.85;">[' + TIER_NAME[pend.ench.t] + ']</span></div><div class="rowSub">' + enchDesc(pend.ench) + ' • untuk ' + (pr ? pr.name : '?') + '</div></div><div class="rowBtns"><button class="rowBtn" data-en="accept">Pakai</button><button class="rowBtn" data-en="reject">Buang</button></div></div>';
    }
    const busy = !!(pend || enAnimating);
    h += '<button class="rowBtn" data-en="roll" ' + ((busy || save.coins < cost) ? 'disabled' : '') + ' style="width:100%;">Enchant ' + rod.name + ' (' + cost + ' koin)</button>';
    if (cur) {
      h += '<button class="rowBtn" data-en="lock" ' + ((busy || save.coins < lockCost) ? 'disabled' : '') + ' style="width:100%;margin-top:8px;background:linear-gradient(90deg,#ffc233,#ff8a3d);">Roll Kunci Tier (' + lockCost + ' koin) - minimal ' + TIER_NAME[enchTier(cur.id)] + '</button>';
    }
    h += '<div class="rowSub" style="text-align:center;margin-top:8px;">Pity: <b>' + save.enPity + '/' + PITY_MAX + '</b> - di roll ke-' + (PITY_MAX + 1) + ' tanpa Epic, dijamin Epic ke atas.</div>';
    h += enchRatesHtml();
    h += '<div class="rowSub" style="text-align:center;">Pilih Pakai buat ganti enchant lama. Roll Kunci Tier dijamin tidak lebih rendah dari tier enchant sekarang.</div>';
    document.getElementById('enBody').innerHTML = h;
    document.getElementById('enCoins').textContent = save.coins;
  }
"""
    s = s[:a] + NEW_RENDER + s[b:]

# ---------- 6. handler klik: roll / lock / accept / reject ----------
a = s.find("  document.getElementById('enBody').addEventListener('click'")
b = s.find("  function openEnchant()")
if a < 0 or b < 0 or b < a:
    errors.append('blok handler enchant tidak ketemu')
else:
    NEW_HANDLER = r"""  function doEnchantRoll(locked) {
    const rod = ROD_TIERS.find(r => r.id === save.rod) || ROD_TIERS[0];
    const cur = save.enchants && save.enchants[rod.id];
    const cost = enchantCost(rod) * (locked ? 2 : 1);
    if (getPendingEnchant() || enAnimating || save.coins < cost) return;
    if (locked && !cur) return;
    save.coins -= cost;
    save.enPity = save.enPity || 0;
    let minTier = locked ? enchTier(cur.id) : 1;
    if (save.enPity >= PITY_MAX) minTier = Math.max(minTier, 3);
    const got = rollEnchant(minTier);
    save.enPity = got.t >= 3 ? 0 : save.enPity + 1;
    save.pendingEnchant = { rodId: rod.id, id: got.id };
    Sfx.sell(); vibe(30);
    persistSave(); refreshHud();
    startEnchantAnim();
  }
  document.getElementById('enBody').addEventListener('click', function (ev) {
    const b = ev.target.closest('[data-en]'); if (!b || b.disabled) return;
    const act = b.dataset.en;
    save.enchants = save.enchants || {};
    const pend = getPendingEnchant();
    if (act === 'roll') { doEnchantRoll(false); return; }
    if (act === 'lock') { doEnchantRoll(true); return; }
    if (enAnimating) return;
    if (act === 'accept' && pend) {
      save.enchants[pend.rodId] = { id: pend.ench.id, name: pend.ench.name, luck: pend.ench.luck || 0, speed: pend.ench.speed || 0, sell: pend.ench.sell || 0, xp: pend.ench.xp || 0 };
      save.pendingEnchant = null;
      showToast('Enchant ' + pend.ench.name + ' terpasang!'); Sfx.levelUp(); vibe([40, 30, 40]);
    } else if (act === 'reject' && pend) {
      save.pendingEnchant = null; showToast('Hasil enchant dibuang');
    }
    persistSave(); refreshHud(); renderEnchant();
  });
"""
    s = s[:a] + NEW_HANDLER + s[b:]

# ---------- 7. changelog + versi ----------
replace_once("var VER = 'v3.7', DATE = '2 Okt 2026',", "var VER = 'v3.8', DATE = '3 Okt 2026',", 'VER')
replace_once('<div id="versionBadge">v3.7</div>', '<div id="versionBadge">v3.8</div>', 'badge versi')
replace_once(
    '  var LOG = [\n    ["Update v3.7", [',
    '  var LOG = [\n'
    '    ["Update v3.8", [\n'
    '      "Altar Enchant dirombak: ada 14 enchant dengan 5 tier (Common, Rare, Epic, Legendary, Mythic).",\n'
    '      "Efek baru: Harga Jual dan XP, selain Luck dan Speed. Enchant Mythic baru: Tycoon, Godhand, dan Omniscient.",\n'
    '      "Animasi undian enchant, dengan efek khusus untuk hasil Epic ke atas dan getar untuk Mythic.",\n'
    '      "Sistem Pity: setiap 20 roll tanpa Epic, roll berikutnya dijamin Epic ke atas.",\n'
    '      "Roll Kunci Tier (2x biaya): hasil dijamin tidak lebih rendah dari tier enchant yang sedang dipakai.",\n'
    '      "Peluang tiap tier sekarang ditampilkan langsung di altar."\n'
    '    ]],\n'
    '    ["Update v3.7", [',
    'changelog')

if errors:
    print('GAGAL, file TIDAK diubah:')
    for e in errors: print(' -', e)
    sys.exit(1)

shutil.copyfile(path, path + '.bak-enchant')
open(path, 'w', encoding='utf-8').write(s)
print('Patch enchant v3.8 terpasang. Backup: ' + path + '.bak-enchant')
