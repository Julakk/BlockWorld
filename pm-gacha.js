/* PM-GACHA v1 - Gacha Rod: 1x / 10x, skin rod (biasa, cahaya, animasi), pity Legendary */
(function () {
  'use strict';
  var C = window.__PMC, T = window.THREE;
  if (!C || !T || window.__pmGacha) return;
  window.__pmGacha = true;

  /* ---------- setelan (ubah di sini kalau mau diseimbangkan) ---------- */
  var COST1 = 100, COST10 = 900, PITY_MAX = 60;
  var ORDER = ['common', 'rare', 'epic', 'legendary'];
  var TIER = {
    common: { n: 'Common', c: '#9fb4bd', w: 60, d: '10-50 koin / Bait' },
    rare: { n: 'Rare', c: '#4aa8ff', w: 25, d: '100-300 koin / Skin Rod Biasa' },
    epic: { n: 'Epic', c: '#b56bff', w: 12, d: '500 koin / Skin Rod Efek Cahaya' },
    legendary: { n: 'Legendary', c: '#ffc233', w: 3, d: '2.000 koin / Skin Rod Animasi Unik' }
  };
  var COIN_CHANCE = { rare: 0.30, epic: 0.25, legendary: 0.15 }; // sisanya jadi skin
  var DUP = { rare: 30, epic: 75, legendary: 200 };              // skin duplikat jadi koin
  var KIND_LABEL = { solid: 'Skin Biasa', glow: 'Efek Cahaya', rainbow: 'Animasi Unik', fire: 'Animasi Unik', galaxy: 'Animasi Unik' };
  var SKINS = [
    { id: 's_merah', n: 'Merah Karang', t: 'rare', k: 'solid', c: '#d8302a' },
    { id: 's_hijau', n: 'Hijau Zamrud', t: 'rare', k: 'solid', c: '#1fae5a' },
    { id: 's_ungu', n: 'Ungu Anggur', t: 'rare', k: 'solid', c: '#7a3fc4' },
    { id: 's_oranye', n: 'Oranye Senja', t: 'rare', k: 'solid', c: '#f08a2a' },
    { id: 's_hitam', n: 'Hitam Arang', t: 'rare', k: 'solid', c: '#23262b' },
    { id: 's_putih', n: 'Putih Salju', t: 'rare', k: 'solid', c: '#eef2f5' },
    { id: 'e_biru', n: 'Neon Biru', t: 'epic', k: 'glow', c: '#2fd8ff' },
    { id: 'e_pink', n: 'Neon Pink', t: 'epic', k: 'glow', c: '#ff4fd8' },
    { id: 'e_hijau', n: 'Neon Hijau', t: 'epic', k: 'glow', c: '#5bff7a' },
    { id: 'e_emas', n: 'Cahaya Emas', t: 'epic', k: 'glow', c: '#ffd45a' },
    { id: 'l_pelangi', n: 'Pelangi Abadi', t: 'legendary', k: 'rainbow', c: '#ff7ad9' },
    { id: 'l_api', n: 'Api Naga', t: 'legendary', k: 'fire', c: '#ff6a1a' },
    { id: 'l_galaksi', n: 'Galaksi', t: 'legendary', k: 'galaxy', c: '#7a5cff' }
  ];

  /* ---------- util ---------- */
  function $(id) { return document.getElementById(id); }
  function fmt(n) { return String(Math.round(+n || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function rnd(a, b) { return a + Math.floor(Math.random() * (b - a + 1)); }
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
  function skinById(id) { for (var i = 0; i < SKINS.length; i++) if (SKINS[i].id === id) return SKINS[i]; return null; }
  function baitName(id) { var b = C.BAIT_TYPES.filter(function (x) { return x.id === id; })[0]; return b ? b.name : id; }
  function swatch(sk) {
    var c = sk.c;
    if (sk.k === 'solid') return 'background:' + c;
    if (sk.k === 'glow') return 'background:radial-gradient(circle at 40% 35%,#fff,' + c + ' 55%,#0a1e2c);box-shadow:0 0 12px ' + c;
    if (sk.k === 'rainbow') return 'background:conic-gradient(#ff5a5a,#ffd45a,#5affb0,#5ab4ff,#c05aff,#ff5a5a);box-shadow:0 0 12px #ff7ad9';
    if (sk.k === 'fire') return 'background:radial-gradient(circle at 50% 70%,#ffe27a,#ff6a1a 55%,#7a1200);box-shadow:0 0 12px #ff6a1a';
    return 'background:linear-gradient(135deg,#1a1050,#7a5cff 55%,#2fd8ff);box-shadow:0 0 12px #7a5cff';
  }

  /* ---------- logika gacha ---------- */
  function rollTier(min) {
    var r = Math.random() * 100, acc = 0, t = 'common';
    for (var i = 0; i < ORDER.length; i++) { acc += TIER[ORDER[i]].w; if (r < acc) { t = ORDER[i]; break; } }
    if (ORDER.indexOf(t) < ORDER.indexOf(min)) t = min;
    return t;
  }
  function reward(tier) {
    var s = C.save, r = Math.random();
    if (tier === 'common') {
      if (r < 0.75) return { tier: tier, kind: 'coin', coins: rnd(10, 50) };
      var pool = ['luck', 'midnight'].filter(function (id) { return !(s.baitStock && s.baitStock[id] > 0); });
      if (pool.length) return { tier: tier, kind: 'bait', id: pick(pool) };
      return { tier: tier, kind: 'coin', coins: 15, note: 'Bait sudah dimiliki' };
    }
    if (r < COIN_CHANCE[tier]) return { tier: tier, kind: 'coin', coins: tier === 'rare' ? rnd(100, 300) : (tier === 'epic' ? 500 : 2000) };
    var sk = pick(SKINS.filter(function (x) { return x.t === tier; }));
    if (s.skins && s.skins[sk.id]) return { tier: tier, kind: 'skin', id: sk.id, dup: true, coins: DUP[tier] };
    return { tier: tier, kind: 'skin', id: sk.id };
  }
  function apply(res) {
    var s = C.save;
    s.skins = s.skins || {}; s.baitStock = s.baitStock || {};
    if (res.kind === 'coin') s.coins += res.coins;
    else if (res.kind === 'bait') s.baitStock[res.id] = Math.max(1, s.baitStock[res.id] || 0);
    else if (res.dup) s.coins += res.coins;
    else s.skins[res.id] = 1;
  }

  var busy = false, animT = 0, flashEl = null;
  var st = { tab: 'pull', anim: false, last: null, best: 'common', flash: false };

  function pull(n) {
    var s = C.save, cost = n === 1 ? COST1 : COST10;
    if (busy) return;
    if (s.coins < cost) { C.toast('Koin kurang, butuh ' + fmt(cost)); return; }
    s.coins -= cost;
    var g = s.gacha = s.gacha || { pity: 0, total: 0 }, out = [], best = 0, i;
    for (i = 0; i < n; i++) {
      g.pity++; g.total++;
      var t = g.pity >= PITY_MAX ? 'legendary' : rollTier(n === 10 && i === 9 ? 'rare' : 'common');
      if (t === 'legendary') g.pity = 0;
      var r = reward(t); apply(r); out.push(r);
      best = Math.max(best, ORDER.indexOf(t));
    }
    C.persist(); C.refresh(); C.Sfx.tap();
    st.last = out; st.best = ORDER[best]; st.anim = true; busy = true;
    render();
    clearTimeout(animT); animT = setTimeout(finish, 1100);
  }
  function finish() {
    if (!st.anim) return;
    clearTimeout(animT); st.anim = false; busy = false;
    var b = st.best;
    C.Sfx.catchFish(b);
    C.vibe(b === 'legendary' ? [100, 50, 100, 50, 160] : (b === 'epic' ? [60, 40, 60] : [30]));
    render();
    if (b === 'legendary' && flashEl) { flashEl.className = ''; void flashEl.offsetWidth; flashEl.className = 'on'; }
  }
  function equip(id) {
    var s = C.save;
    if (id && !(s.skins && s.skins[id])) return;
    s.skin = id; C.persist(); C.Sfx.tap();
    C.toast(id ? 'Skin ' + skinById(id).n + ' dipakai' : 'Skin dilepas');
    render();
  }

  /* ---------- UI ---------- */
  var css = document.createElement('style');
  css.textContent = [
    '#modalGacha .modalBox{position:relative}',
    '.gcTabs{display:flex;gap:7px;padding:0 16px 10px}',
    '.gcTab{flex:1;padding:9px;border-radius:14px;border:2px solid rgba(255,255,255,.22);background:rgba(255,255,255,.06);color:var(--text-dim);font-size:12px;font-weight:700;font-family:inherit}',
    '.gcTab.on{background:linear-gradient(90deg,var(--accent),var(--accent2));color:#052730;border-color:#fff;box-shadow:0 4px 0 rgba(0,80,90,.4)}',
    '.gcRates{display:grid;gap:5px;margin-bottom:10px}',
    '.gcRate{display:flex;align-items:center;gap:8px;padding:6px 10px;border-radius:12px;border:2px solid var(--rc);background:rgba(0,0,0,.25);font-size:11px;line-height:1.3}',
    '.gcRate b{color:var(--rc);min-width:76px;font-size:12px}',
    '.gcRate .p{margin-left:auto;font-weight:900;font-size:13px}',
    '.gcBtns{display:flex;gap:8px;margin-bottom:8px}',
    '.gcPull{flex:1;padding:11px 6px;border-radius:18px;border:3px solid #fff;font-family:inherit;font-weight:900;font-size:14px;line-height:1.2;color:#052730;background:linear-gradient(90deg,#37d1c8,#2f9fc9);box-shadow:0 5px 0 rgba(0,80,90,.5),0 8px 14px rgba(0,0,0,.3)}',
    '.gcPull.gold{background:linear-gradient(160deg,#ffcf4d,#e0982a);color:#4a2600;box-shadow:0 5px 0 rgba(120,70,0,.55),0 8px 14px rgba(0,0,0,.3)}',
    '.gcPull small{display:block;font-size:10.5px;font-weight:800;opacity:.85;margin-top:2px}',
    '.gcPull:active:not(:disabled){transform:translateY(4px);box-shadow:0 1px 0 rgba(0,0,0,.35)}',
    '.gcPull:disabled{opacity:.5}',
    '.gcInfo{text-align:center;font-size:11px;color:var(--text-dim);line-height:1.5;margin-bottom:8px}',
    '.gcH{font-size:12px;font-weight:900;color:var(--gold);margin:4px 0 6px}',
    '.gcGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:8px}',
    '.gcCard{border:2.5px solid var(--rc);border-radius:14px;padding:8px 4px;text-align:center;background:linear-gradient(165deg,rgba(255,255,255,.07),rgba(0,0,0,.3));box-shadow:0 0 9px var(--rc);animation:gcPop .35s both}',
    '.gcTier{font-size:10px;font-weight:900;color:var(--rc)}',
    '.gcBig{font-size:13px;font-weight:900;line-height:1.2;margin:3px 0}',
    '.gcSub{font-size:10px;color:var(--text-dim)}',
    '.gcSw{position:relative;width:44px;height:44px;border-radius:12px;border:2px solid rgba(255,255,255,.75);flex-shrink:0;margin:4px auto 0}',
    '.gcSw::after{content:"";position:absolute;left:7px;right:7px;top:50%;height:4px;border-radius:2px;background:rgba(255,255,255,.88);transform:rotate(-35deg)}',
    '.rowItem .gcSw{margin:0}',
    '.gcLocked .gcSw{filter:grayscale(1) brightness(.45)}',
    '.gcCap{width:84px;height:84px;margin:16px auto 6px;border-radius:50%;background:radial-gradient(circle at 35% 28%,#fff,var(--rc) 55%,#0a1e2c);box-shadow:0 0 24px var(--rc);animation:gcShake .5s ease-in-out infinite}',
    '.gcCapT{text-align:center;font-size:11px;color:var(--text-dim);margin-bottom:10px}',
    '#gcFlash{position:absolute;left:0;top:0;right:0;bottom:0;border-radius:inherit;pointer-events:none;opacity:0;background:radial-gradient(circle,rgba(255,224,102,.85),rgba(255,224,102,0) 70%)}',
    '#gcFlash.on{animation:gcFl 1s ease forwards}',
    '@keyframes gcPop{from{transform:scale(.3);opacity:0}to{transform:scale(1);opacity:1}}',
    '@keyframes gcShake{0%,100%{transform:rotate(0)}25%{transform:rotate(-10deg) scale(1.05)}75%{transform:rotate(10deg) scale(1.05)}}',
    '@keyframes gcFl{0%{opacity:0}20%{opacity:1}100%{opacity:0}}',
    '@media (prefers-reduced-motion:reduce){.gcCard,.gcCap,#gcFlash.on{animation:none!important}.gcCard{opacity:1}}'
  ].join('');
  document.head.appendChild(css);

  var ov = document.createElement('div'); ov.className = 'modalOverlay'; ov.id = 'modalGacha';
  ov.innerHTML = '<div class="modalBox"><div class="modalHead"><h2>Gacha Rod</h2><button class="modalClose" id="gcX" type="button">\u2715</button></div>' +
    '<div class="gcTabs" id="gcTabs"><button class="gcTab on" data-tab="pull" type="button">Gacha</button><button class="gcTab" data-tab="skin" type="button">Skin Saya</button></div>' +
    '<div class="modalBody" id="gcBody"></div><div class="modalFoot"><span id="gcFoot"></span><span id="gcCoins"></span></div><div id="gcFlash"></div></div>';
  document.body.appendChild(ov);
  var body = $('gcBody'); flashEl = $('gcFlash');
  $('gcX').onclick = function () { ov.classList.remove('show'); };
  $('gcTabs').addEventListener('click', function (e) {
    var b = e.target.closest('[data-tab]'); if (!b) return;
    st.tab = b.getAttribute('data-tab'); render();
  });
  body.addEventListener('click', function (e) {
    var b = e.target.closest('[data-act]'); if (!b || b.disabled) return;
    var a = b.getAttribute('data-act');
    if (a === 'p1') pull(1); else if (a === 'p10') pull(10); else if (a === 'skip') finish();
    else if (a === 'eq') equip(b.getAttribute('data-id')); else if (a === 'un') equip('');
  });

  function card(r, i) {
    var t = TIER[r.tier], big, sub, sw = '';
    if (r.kind === 'coin') { big = '+' + fmt(r.coins); sub = r.note || 'Koin'; }
    else if (r.kind === 'bait') { big = baitName(r.id); sub = 'Bait baru!'; }
    else {
      var sk = skinById(r.id);
      sw = '<div class="gcSw" style="' + swatch(sk) + '"></div>';
      big = sk.n; sub = r.dup ? 'Duplikat +' + r.coins + ' koin' : 'SKIN BARU!';
    }
    return '<div class="gcCard" style="--rc:' + t.c + ';animation-delay:' + (i * 0.09).toFixed(2) + 's"><div class="gcTier">' + t.n + '</div>' + sw + '<div class="gcBig">' + big + '</div><div class="gcSub">' + sub + '</div></div>';
  }

  function render() {
    var s = C.save, g = s.gacha || { pity: 0, total: 0 }, h = '', i, k;
    var tp = ov.querySelectorAll('.gcTab');
    for (i = 0; i < tp.length; i++) tp[i].className = 'gcTab' + (tp[i].getAttribute('data-tab') === st.tab ? ' on' : '');
    if (st.tab === 'pull') {
      h += '<div class="gcRates">';
      ORDER.forEach(function (key) { var t = TIER[key]; h += '<div class="gcRate" style="--rc:' + t.c + '"><b>' + t.n + '</b><span>' + t.d + '</span><span class="p">' + t.w + '%</span></div>'; });
      h += '</div>';
      h += '<div class="gcBtns"><button class="gcPull" type="button" data-act="p1"' + ((busy || s.coins < COST1) ? ' disabled' : '') + '>Gacha 1x<small>' + fmt(COST1) + ' koin</small></button>' +
        '<button class="gcPull gold" type="button" data-act="p10"' + ((busy || s.coins < COST10) ? ' disabled' : '') + '>Gacha 10x<small>' + fmt(COST10) + ' koin (Hemat!)</small><small>Garansi minimal Rare di pull ke-10</small></button></div>';
      h += '<div class="gcInfo">Pity: <b>' + g.pity + '/' + PITY_MAX + '</b> \u2022 Legendary dijamin di pull ke-' + PITY_MAX + '<br>Skin duplikat jadi koin (Rare ' + DUP.rare + ', Epic ' + DUP.epic + ', Legendary ' + DUP.legendary + '). Skin berlaku di semua rod.</div>';
      if (st.anim) {
        h += '<div class="gcCap" data-act="skip" style="--rc:' + TIER[st.best].c + '"></div><div class="gcCapT">Mengundi... ketuk buat lewati</div>';
      } else if (st.last) {
        h += '<div class="gcH">Hasil terakhir</div><div class="gcGrid">';
        for (i = 0; i < st.last.length; i++) h += card(st.last[i], i);
        h += '</div>';
      }
      $('gcFoot').textContent = 'Total pull: ' + fmt(g.total);
    } else {
      var owned = 0;
      h += '<button class="rowBtn" type="button" data-act="un"' + (s.skin ? '' : ' disabled') + ' style="width:100%;margin-bottom:8px">Tanpa Skin</button>';
      SKINS.forEach(function (sk) {
        var has = !!(s.skins && s.skins[sk.id]), on = s.skin === sk.id, t = TIER[sk.t];
        if (has) owned++;
        h += '<div class="rowItem' + (has ? '' : ' gcLocked') + '" style="border-color:' + t.c + '"><div class="gcSw" style="' + swatch(sk) + '"></div>' +
          '<div class="rowInfo"><div class="rowName" style="color:' + t.c + '">' + (has ? sk.n : '???') + '</div><div class="rowSub">' + t.n + ' \u2022 ' + KIND_LABEL[sk.k] + '</div></div>' +
          '<button class="rowBtn' + (on ? ' owned' : '') + '" type="button"' + (has && !on ? ' data-act="eq" data-id="' + sk.id + '"' : ' disabled') + '>' + (on ? 'Dipakai' : (has ? 'Pakai' : 'Terkunci')) + '</button></div>';
      });
      $('gcFoot').textContent = 'Terkumpul ' + owned + '/' + SKINS.length;
    }
    $('gcCoins').textContent = 'Koin: ' + fmt(s.coins);
    body.innerHTML = h;
  }
  function openG() { render(); ov.classList.add('show'); }

  var host = $('menuPanel') || $('hudPills');
  if (host) {
    var mb = document.createElement('button'); mb.className = 'hudPill'; mb.textContent = 'Gacha';
    mb.onclick = function () { var mp = $('menuPanel'); if (mp) mp.classList.remove('show'); openG(); };
    host.appendChild(mb);
  }
  var q = $('pmsQuick');
  if (q) {
    var qb = document.createElement('button'); qb.type = 'button'; qb.className = 'pmsQ'; qb.textContent = 'Gacha';
    qb.onclick = openG; q.insertBefore(qb, q.lastChild);
  }

  /* ---------- skin 3D di joran (overlay, tidak mengubah material rod asli) ---------- */
  var rod = C.rodMesh, roots = [], skinId = null, cur = null, skinMat = null, glow = null, pts = null, ptsPos = null, ptsCol = null;
  var N = 14, tc = new T.Color(), dotT = null;
  function dotTex() {
    if (dotT) return dotT;
    var c = document.createElement('canvas'); c.width = c.height = 32;
    var g = c.getContext('2d'), gr = g.createRadialGradient(16, 16, 0, 16, 16, 16);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.5, 'rgba(255,255,255,.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 32, 32);
    dotT = new T.CanvasTexture(c); return dotT;
  }
  function findTip() {
    var kids = rod.children;
    for (var i = 0; i < kids.length; i++) {
      var gm = kids[i].geometry;
      if (gm && gm.type === 'CylinderGeometry' && gm.parameters && gm.parameters.radiusTop === 0.008) return kids[i];
    }
    return null;
  }
  function clearSkin() {
    roots.forEach(function (r) {
      if (r.parent) r.parent.remove(r);
      r.traverse(function (o) { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
    });
    roots = []; cur = skinMat = glow = pts = ptsPos = ptsCol = null;
  }
  function buildSkin(sk) {
    var tip = findTip(), root = new T.Group(), tg = new T.Group();
    rod.add(root); (tip || rod).add(tg); if (!tip) tg.position.y = 0.55;
    roots = [root, tg]; cur = sk;
    var m = new T.MeshStandardMaterial({ color: sk.c, roughness: 0.4, metalness: 0.35 });
    if (sk.k !== 'solid') { m.emissive.set(sk.c); m.emissiveIntensity = 0.7; m.roughness = 0.25; }
    skinMat = m;
    var sh = new T.Mesh(new T.CylinderGeometry(0.0155, 0.0325, 1.1, 14), m); sh.castShadow = true; root.add(sh);
    tg.add(new T.Mesh(new T.CylinderGeometry(0.0095, 0.0155, 0.42, 10).translate(0, 0.21, 0), m));
    if (sk.k !== 'solid') {
      glow = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: sk.c, blending: T.AdditiveBlending, depthWrite: false, transparent: true, fog: false }));
      glow.position.set(0, 0.44, 0); glow.scale.set(0.2, 0.2, 1); tg.add(glow);
    }
    if (sk.t === 'legendary') {
      ptsPos = new Float32Array(N * 3); ptsCol = new Float32Array(N * 3);
      var geo = new T.BufferGeometry();
      geo.setAttribute('position', new T.BufferAttribute(ptsPos, 3));
      geo.setAttribute('color', new T.BufferAttribute(ptsCol, 3));
      pts = new T.Points(geo, new T.PointsMaterial({ size: 0.05, map: dotTex(), vertexColors: true, transparent: true, depthWrite: false, blending: T.AdditiveBlending }));
      pts.frustumCulled = false; root.add(pts);
    }
  }
  C.hookAnim(function (t) {
    var s = C.save, id = (s && s.skin && s.skins && s.skins[s.skin]) ? s.skin : '';
    if (id !== skinId) { skinId = id; clearSkin(); var sk = id ? skinById(id) : null; if (sk) buildSkin(sk); }
    if (!cur || !skinMat) return;
    var k = cur.k, i, a, u, p, f, tw;
    if (k === 'glow') skinMat.emissiveIntensity = 0.55 + 0.35 * Math.sin(t * 3);
    else if (k === 'rainbow') { skinMat.color.setHSL((t * 0.25 + 0.1) % 1, 0.7, 0.55); skinMat.emissive.setHSL((t * 0.25) % 1, 0.9, 0.5); }
    else if (k === 'fire') { skinMat.emissiveIntensity = 0.7 + 0.3 * Math.sin(t * 17) * Math.sin(t * 5.3); skinMat.emissive.setHSL(0.03 + 0.02 * Math.sin(t * 11), 1, 0.5); }
    else if (k === 'galaxy') skinMat.emissive.setHSL(0.68 + 0.1 * Math.sin(t * 1.5), 0.9, 0.5);
    if (glow) {
      var gs = 0.2 + 0.05 * Math.sin(t * 4); glow.scale.set(gs, gs, 1);
      if (k === 'rainbow') glow.material.color.setHSL((t * 0.25) % 1, 1, 0.6);
    }
    if (!pts) return;
    for (i = 0; i < N; i++) {
      u = i / N; p = i * 3;
      if (k === 'rainbow') {
        a = t * 2.2 + u * 6.283;
        ptsPos[p] = Math.cos(a) * 0.06; ptsPos[p + 1] = -0.3 + u * 1.2; ptsPos[p + 2] = Math.sin(a) * 0.06;
        tc.setHSL((u + t * 0.2) % 1, 1, 0.6); ptsCol[p] = tc.r; ptsCol[p + 1] = tc.g; ptsCol[p + 2] = tc.b;
      } else if (k === 'fire') {
        f = (t * 0.7 + u) % 1;
        ptsPos[p] = Math.sin(i * 7.3 + t * 3) * 0.035 * f; ptsPos[p + 1] = -0.15 + f * 1.0; ptsPos[p + 2] = Math.cos(i * 5.1 + t * 2.4) * 0.035 * f;
        ptsCol[p] = 1 - f; ptsCol[p + 1] = 0.45 * (1 - f) * (1 - f); ptsCol[p + 2] = 0.04 * (1 - f);
      } else {
        a = t * (0.9 + (i % 3) * 0.35) + u * 6.283; tw = 0.5 + 0.5 * Math.sin(t * 4 + i * 1.7);
        ptsPos[p] = Math.cos(a) * (0.05 + (i % 4) * 0.012); ptsPos[p + 1] = -0.35 + ((i * 0.37) % 1) * 1.25; ptsPos[p + 2] = Math.sin(a) * (0.05 + (i % 4) * 0.012);
        ptsCol[p] = 0.2 + 0.6 * tw; ptsCol[p + 1] = 0.2 + 0.7 * tw; ptsCol[p + 2] = 0.4 + 0.6 * tw;
      }
    }
    pts.geometry.attributes.position.needsUpdate = true; pts.geometry.attributes.color.needsUpdate = true;
  });
})();
