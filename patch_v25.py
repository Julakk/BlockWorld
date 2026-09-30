import re, os

EXT_CSS = r"""
#evBadge{position:fixed;top:calc(104px + env(safe-area-inset-top,0px));left:50%;transform:translateX(-50%);z-index:11;display:none;padding:3px 12px;border-radius:999px;font-size:11px;font-weight:900;color:#fff;border:2px solid #fff;text-shadow:1px 1px 2px #000;white-space:nowrap;pointer-events:none}
#menuPanel{max-height:calc(100dvh - 70px);overflow-y:auto}
@media (orientation:landscape) and (max-height:520px){#evBadge{top:calc(8px + env(safe-area-inset-top,0px))}}
"""

EXT_JS = r"""
window.PMExt = function (C) {
  var T = THREE, $ = function (i) { return document.getElementById(i); }, S = function () { return C.save; };
  function hash(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function mkModal(id, title) {
    var ov = document.createElement('div'); ov.className = 'modalOverlay'; ov.id = id;
    ov.innerHTML = '<div class="modalBox"><div class="modalHead"><h2>' + title + '</h2><button class="modalClose">✕</button></div><div class="modalBody"></div><div class="modalFoot"><span></span><span></span></div></div>';
    document.body.appendChild(ov);
    ov.querySelector('.modalClose').onclick = function () { ov.classList.remove('show'); };
    return { ov: ov, body: ov.querySelector('.modalBody'), foot: ov.querySelector('.modalFoot span'), open: function () { ov.classList.add('show'); } };
  }
  function row(icon, name, sub, btn) { return '<div class="rowItem">' + icon + '<div class="rowInfo"><div class="rowName">' + name + '</div><div class="rowSub">' + sub + '</div></div>' + (btn || '') + '</div>'; }
  function lbl(e) { return (e.mutation.name ? e.mutation.name + ' ' : '') + e.fish.name; }

  /* ===== TROFI + REKOR ===== */
  function st() { var s = S(); if (!s.stats) s.stats = { catches: 0, byR: {}, mut: 0, shiny: 0, deep: 0, heavy: 0, secret: 0 }; if (!s.ach) s.ach = {}; return s.stats; }
  function rc(min) { var b = st().byR, n = 0; C.RARITY_ORDER.forEach(function (r, i) { if (i >= min) n += b[r] || 0; }); return n; }
  var D = function () { return Object.keys(S().discovered || {}).length; };
  var ACH = [
    ['Pemancing Pemula', 'Tangkap 1 ikan', 1, 50, function () { return st().catches; }],
    ['Tukang Pancing', 'Tangkap 100 ikan', 100, 300, function () { return st().catches; }],
    ['Legenda Dermaga', 'Tangkap 500 ikan', 500, 1500, function () { return st().catches; }],
    ['Mata Jeli', '10 ikan Langka atau lebih', 10, 200, function () { return rc(2); }],
    ['Epik!', 'Tangkap ikan Epik', 1, 400, function () { return rc(3); }],
    ['Legendaris', 'Tangkap ikan Legendaris', 1, 1200, function () { return rc(4); }],
    ['Mitos Hidup', 'Tangkap ikan Mitos', 1, 4000, function () { return rc(5); }],
    ['Rahasia Terbongkar', 'Tangkap ikan Rahasia', 1, 15000, function () { return st().secret; }],
    ['Ilmuwan Mutasi', 'Tangkap 20 ikan mutasi', 20, 600, function () { return st().mut; }],
    ['Berkilau', 'Tangkap ikan Shiny', 1, 800, function () { return st().shiny; }],
    ['Kolektor', 'Temukan 15 jenis ikan', 15, 500, D],
    ['Ensiklopedia', 'Lengkapi Koleksi', C.FISH_TABLE.length, 8000, D],
    ['Raksasa', 'Tangkap ikan 1.000 kg+', 1, 1000, function () { return st().heavy; }],
    ['Penjelajah', '10 ikan dari Laut Dalam', 10, 700, function () { return st().deep; }],
    ['Master Level', 'Capai Level 20', 20, 1500, function () { return S().level; }],
    ['Sultan Joran', 'Miliki Astral Rod', 1, 2000, function () { return (S().ownedRods || []).indexOf('legendaris') >= 0 ? 1 : 0; }],
    ['Aquarist', 'Pajang 6 ikan di Akuarium', 6, 600, function () { return (S().aqua || []).length; }]
  ];
  function checkAch() {
    st(); var s = S(), hit = false;
    ACH.forEach(function (a, i) {
      if (s.ach[i] || a[4]() < a[2]) return;
      s.ach[i] = 1; s.coins += a[3]; C.addXp(Math.round(a[3] / 10)); hit = true;
      C.toast('Trofi: ' + a[0] + ' (+' + a[3] + ' koin)'); C.Sfx.levelUp(); C.vibe([40, 30, 40]);
    });
    if (hit) { C.persist(); C.refresh(); }
  }
  function addRecord(c) {
    var s = S(); s.rec = s.rec || []; s.recV = s.recV || [];
    var e = { n: lbl(c), w: c.weight || 0, v: c.value, r: c.fish.rarity };
    s.rec.push(e); s.rec.sort(function (a, b) { return b.w - a.w; }); s.rec.length = Math.min(10, s.rec.length);
    s.recV.push(e); s.recV.sort(function (a, b) { return b.v - a.v; }); s.recV.length = Math.min(5, s.recV.length);
  }
  C.hookFinish(function (ok, c) {
    if (!ok || !c) return;
    var s = st(), f = c.fish;
    s.catches++; s.byR[f.rarity] = (s.byR[f.rarity] || 0) + 1;
    if (c.mutation && c.mutation.id !== 'normal') s.mut++;
    if (c.mutation && c.mutation.shiny) s.shiny++;
    if (f.zone === 'dalam') s.deep++;
    if (f.rarity === 'secret') s.secret++;
    if ((c.weight || 0) >= 1000) s.heavy++;
    addRecord(c); checkAch(); C.persist(); C.refresh();
  });
  var mT = mkModal('modalTrofi', 'Trofi');
  function renderT() {
    st(); var s = S(), n = 0;
    mT.body.innerHTML = ACH.map(function (a, i) {
      var done = !!s.ach[i]; if (done) n++;
      return row('', a[0], a[1] + ' • ' + Math.min(a[2], a[4]()) + '/' + a[2] + ' • Hadiah ' + a[3] + ' koin', '<button class="rowBtn' + (done ? ' owned' : '') + '" disabled>' + (done ? 'Selesai' : 'Berjalan') + '</button>');
    }).join('');
    mT.foot.textContent = n + '/' + ACH.length + ' trofi';
  }
  var mR = mkModal('modalRekor', 'Papan Rekor');
  function renderR() {
    var s = S(), h = '';
    if (!(s.rec || []).length) h = '<div class="rowSub" style="text-align:center;padding:16px">Belum ada rekor. Yuk mancing!</div>';
    else {
      h = '<div class="rowName">Ikan Terberat</div>';
      s.rec.forEach(function (e, i) { h += row('', (i + 1) + '. ' + e.n, C.fmtKg(e.w) + ' • ' + C.RARITY_LABEL[e.r]); });
      h += '<div class="rowName" style="margin-top:6px">Ikan Termahal</div>';
      (s.recV || []).forEach(function (e, i) { h += row('', (i + 1) + '. ' + e.n, e.v + ' koin • ' + C.RARITY_LABEL[e.r]); });
    }
    mR.body.innerHTML = h; mR.foot.textContent = 'Rekor lokal • Total ' + st().catches + ' tangkapan';
  }

  /* ===== HARGA PASAR HARIAN ===== */
  function dk() { var d = new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }
  window.PMP = function (id) { return Math.round((0.7 + (hash(dk() + id) % 1000) / 1000 * 0.9) * 100) / 100; };
  function mkt() { return C.FISH_TABLE.map(function (f) { return { f: f, m: window.PMP(f.id) }; }).sort(function (a, b) { return b.m - a.m; }); }
  var mP = mkModal('modalPasar', 'Pasar Hari Ini');
  function renderP() {
    var l = mkt(), list = l.slice(0, 8).concat(l.slice(-3));
    mP.body.innerHTML = '<div class="rowSub">Harga jual berubah tiap hari. Jual yang lagi naik!</div>' + list.map(function (o) {
      var col = o.m >= 1.3 ? '#4ce88a' : o.m <= 0.85 ? '#ff5a6a' : '#f2fbfc';
      return row('', o.f.name, 'Dasar ' + o.f.value + ' • Hari ini ' + Math.round(o.f.value * o.m) + ' koin', '<b style="color:' + col + '">' + (o.m >= 1 ? '▲' : '▼') + ' x' + o.m.toFixed(2) + '</b>');
    }).join('');
    mP.foot.textContent = 'Reset tiap ganti hari';
  }
  var sb = $('startBtn');
  if (sb) sb.addEventListener('click', function () { setTimeout(function () { var t = mkt()[0]; C.toast('Pasar hari ini: ' + t.f.name + ' x' + t.m.toFixed(2)); }, 2200); });

  /* ===== JORAN PER TIER ===== */
  var rodMat = C.rodMesh.material, lastRod = '';
  function applyRod(t) {
    var id = S().rod, idx = C.ROD_TIERS.findIndex(function (r) { return r.id === id; });
    if (id !== lastRod) { lastRod = id; var col = id === 'bambu' ? new T.Color(0x8a5a2b) : new T.Color(C.GEAR_COLORS.rod[id] || '#9fb4bd'); rodMat.color.copy(col); rodMat.emissive.copy(col); }
    if (idx >= 5) rodMat.emissive.setHSL((t * 0.2) % 1, 0.9, 0.55);
    rodMat.emissiveIntensity = idx >= 5 ? 0.7 : idx >= 3 ? 0.3 + 0.15 * Math.sin(t * 3) : idx >= 2 ? 0.12 : 0;
  }

  /* ===== KARAKTER ===== */
  var SHIRTS = { biru: ['Biru', 0x4ac0e0, 0], merah: ['Merah', 0xd8483a, 150], hijau: ['Hijau', 0x4cbf6a, 150], ungu: ['Ungu', 0x9b5be0, 300], hitam: ['Hitam', 0x22262c, 300], emas: ['Emas', 0xffc233, 1500] };
  var PANTS = { navy: ['Navy', 0x33485f, 0], krem: ['Krem', 0xcdb98a, 100], hitam: ['Hitam', 0x1d2126, 150], merah: ['Merah', 0x8a2b2b, 200], putih: ['Putih', 0xe6e9ee, 250] };
  var HATS = { jerami: ['Jerami', 0xf2e4b8, 0xd8483a, 0], hitam: ['Hitam', 0x2a2d33, 0xffc233, 200], merah: ['Merah', 0xd8483a, 0xffffff, 300], emas: ['Emas', 0xffc233, 0x8a4a00, 1500], none: ['Tanpa Topi', 0, 0, 0] };
  var GRP = { shirt: SHIRTS, pants: PANTS, hat: HATS };
  var hatM = [], strawMat = null, bandMat = null;
  C.player.children.forEach(function (m) {
    if (!m.material || !m.material.color) return;
    var h = m.material.color.getHex();
    if (h === 0xf2e4b8) { hatM.push(m); strawMat = m.material; }
    else if (h === 0xd8483a && m.geometry && m.geometry.type === 'CylinderGeometry') { hatM.push(m); bandMat = m.material; }
  });
  function cos() { var s = S(); if (!s.cos) s.cos = { shirt: 'biru', pants: 'navy', hat: 'jerami', own: {} }; return s.cos; }
  var lastCos = '';
  function applyCos() {
    var c = cos(), key = c.shirt + c.pants + c.hat; if (key === lastCos) return; lastCos = key;
    var sh = SHIRTS[c.shirt] || SHIRTS.biru, pa = PANTS[c.pants] || PANTS.navy, ha = HATS[c.hat] || HATS.jerami;
    C.body.material.color.setHex(sh[1]); C.legL.material.color.setHex(pa[1]);
    hatM.forEach(function (m) { m.visible = c.hat !== 'none'; });
    if (c.hat !== 'none') { if (strawMat) strawMat.color.setHex(ha[1]); if (bandMat) bandMat.color.setHex(ha[2]); }
  }
  var mC = mkModal('modalChar', 'Karakter');
  function renderChar() {
    var c = cos(), h = '';
    [['shirt', 'Baju'], ['pants', 'Celana'], ['hat', 'Topi']].forEach(function (g) {
      h += '<div class="rowName" style="margin-top:4px">' + g[1] + '</div>';
      Object.keys(GRP[g[0]]).forEach(function (k) {
        var it = GRP[g[0]][k], price = g[0] === 'hat' ? it[3] : it[2], own = price === 0 || c.own[g[0] + ':' + k], on = c[g[0]] === k;
        var bg = it[1] ? '#' + ('000000' + it[1].toString(16)).slice(-6) : '#33434c';
        h += row('<div class="rowIcon" style="background:' + bg + ';border:2px solid #fff"></div>', it[0], own ? 'Dimiliki' : price + ' koin',
          '<button class="rowBtn' + (on ? ' owned' : '') + '" data-c="' + g[0] + '|' + k + '"' + (on || (!own && S().coins < price) ? ' disabled' : '') + '>' + (on ? 'Dipakai' : own ? 'Pakai' : 'Beli') + '</button>');
      });
    });
    mC.body.innerHTML = h; mC.foot.textContent = 'Koin: ' + S().coins;
  }
  mC.body.addEventListener('click', function (ev) {
    var b = ev.target.closest('button'); if (!b || b.disabled) return;
    var p = b.dataset.c.split('|'), g = p[0], k = p[1], c = cos(), it = GRP[g][k], price = g === 'hat' ? it[3] : it[2];
    if (price > 0 && !c.own[g + ':' + k]) { if (S().coins < price) return; S().coins -= price; c.own[g + ':' + k] = 1; C.Sfx.sell(); C.toast('Beli ' + it[0] + '!'); }
    c[g] = k; C.persist(); C.refresh(); renderChar();
  });

  /* ===== AKUARIUM ===== */
  var AQ = { x: 4.5, z: 19, max: 6 };
  var aq = new T.Group(); aq.position.set(AQ.x, C.DECK_Y, AQ.z); C.town.add(aq);
  var wd = new T.MeshLambertMaterial({ color: 0x6b4a2b });
  var bs = new T.Mesh(new T.BoxGeometry(2.4, 0.6, 1.3), wd); bs.position.y = 0.3; aq.add(bs);
  var gl = new T.Mesh(new T.BoxGeometry(2.2, 1.1, 1.1), new T.MeshLambertMaterial({ color: 0x9fe8ff, transparent: true, opacity: 0.28, depthWrite: false })); gl.position.y = 1.15; aq.add(gl);
  var wt = new T.Mesh(new T.BoxGeometry(2.1, 0.95, 1.0), new T.MeshBasicMaterial({ color: 0x2a8fc0, transparent: true, opacity: 0.35, depthWrite: false })); wt.position.y = 1.12; aq.add(wt);
  var lid = new T.Mesh(new T.BoxGeometry(2.4, 0.12, 1.3), wd); lid.position.y = 1.76; aq.add(lid);
  var sg = new T.Sprite(new T.SpriteMaterial({ map: C.makeSignTexture('AKUARIUM', '#1f6f8f'), fog: false })); sg.scale.set(2, 0.5, 1); sg.position.y = 2.35; aq.add(sg);
  C.TOWN_COLLIDERS.push({ x: AQ.x, z: AQ.z, r: 1.5 });
  var tank = [], tankKey = '';
  function rebuildTank() {
    tank.forEach(function (o) { aq.remove(o.g); }); tank = [];
    (S().aqua || []).forEach(function (e, i) {
      var col = C.RARITY_COLOR[e.fish.rarity], mid = e.mutation.id;
      if (/emas/.test(mid)) col = '#ffd54a'; else if (/ghost/.test(mid)) col = '#c4e0ff'; else if (mid === 'shiny') col = '#78fff0';
      var mat = new T.MeshLambertMaterial({ color: col }), g = new T.Group();
      var b = new T.Mesh(new T.SphereGeometry(0.16, 10, 8), mat); b.scale.set(1.6, 1, 0.7); g.add(b);
      var t = new T.Mesh(new T.ConeGeometry(0.1, 0.22, 4), mat); t.rotation.z = -Math.PI / 2; t.position.x = -0.3; g.add(t);
      var ey = new T.Mesh(new T.SphereGeometry(0.03, 6, 6), new T.MeshBasicMaterial({ color: 0x111111 })); ey.position.set(0.19, 0.04, 0.09); g.add(ey);
      var sc = 0.8 + 0.12 * C.RARITY_ORDER.indexOf(e.fish.rarity); g.scale.set(sc, sc, sc);
      aq.add(g);
      tank.push({ g: g, mat: mat, rb: /pelangi/.test(mid), ph: i * 1.7, sp: 0.5 + (i % 3) * 0.15, y: 0.78 + (i % 3) * 0.22, z: ((i * 0.37) % 0.5) - 0.25 });
    });
  }
  function animTank(t) {
    var k = (S().aqua || []).map(function (e) { return e.fish.id + e.mutation.id; }).join(',');
    if (k !== tankKey) { tankKey = k; rebuildTank(); }
    tank.forEach(function (o) {
      var a = t * o.sp + o.ph;
      o.g.position.set(Math.sin(a) * 0.8, o.y + Math.sin(t * 1.7 + o.ph) * 0.05, o.z);
      o.g.rotation.y = Math.cos(a) > 0 ? 0 : Math.PI;
      if (o.rb) o.mat.color.setHSL((t * 0.2 + o.ph) % 1, 0.9, 0.6);
    });
  }
  var mA = mkModal('modalAqua', 'Akuarium');
  function icon(e) { return '<img class="rowIcon" src="' + C.fishIconCanvas(e.fish, e.mutation) + '">'; }
  function renderA() {
    var s = S(); s.aqua = s.aqua || [];
    var h = '<div class="rowName">Dipajang (' + s.aqua.length + '/' + AQ.max + ')</div>';
    s.aqua.forEach(function (e, i) { h += row(icon(e), lbl(e), C.RARITY_LABEL[e.fish.rarity], '<button class="rowBtn" data-take="' + i + '">Ambil</button>'); });
    h += '<div class="rowName" style="margin-top:6px">Dari Tas (Langka ke atas)</div>';
    var any = false;
    Object.keys(s.inventory).forEach(function (k) {
      var e = s.inventory[k]; if (!e || e.count <= 0 || C.RARITY_ORDER.indexOf(e.fish.rarity) < 2) return; any = true;
      h += row(icon(e), lbl(e), 'x' + e.count + ' • ' + C.RARITY_LABEL[e.fish.rarity], '<button class="rowBtn" data-put="' + k + '"' + (s.aqua.length >= AQ.max ? ' disabled' : '') + '>Pajang</button>');
    });
    if (!any) h += '<div class="rowSub">Belum ada ikan Langka+ di tas.</div>';
    mA.body.innerHTML = h; mA.foot.textContent = 'Ikan yang dipajang gak ikut kejual';
  }
  mA.body.addEventListener('click', function (ev) {
    var b = ev.target.closest('button'); if (!b || b.disabled) return; var s = S();
    if (b.dataset.put) { var e = s.inventory[b.dataset.put]; if (!e || e.count <= 0 || s.aqua.length >= AQ.max) return; e.count--; s.aqua.push({ fish: e.fish, mutation: e.mutation }); }
    else if (b.dataset.take) { var x = s.aqua.splice(+b.dataset.take, 1)[0]; if (!x) return; var k = x.fish.id + '|' + x.mutation.id; s.inventory[k] = s.inventory[k] || { fish: x.fish, mutation: x.mutation, count: 0 }; s.inventory[k].count++; }
    else return;
    C.Sfx.tap(); C.persist(); C.refresh(); renderA(); checkAch();
  });
  C.TOWN_SHOPS.push({ id: 'aqua', name: 'AKUARIUM', label: 'Buka Akuarium', x: AQ.x, z: AQ.z, action: function () { renderA(); mA.open(); } });

  /* ===== PERAHU ===== */
  var boat = C.boatMesh, sailing = false, dock = { x: boat.position.x, z: boat.position.z, r: boat.rotation.y };
  var boatE = { id: 'boat', name: 'PERAHU', label: 'Naik Perahu', x: -3.4, z: 38, action: function () {
    var p = C.player.position;
    if (!sailing) { sailing = true; p.x = dock.x; p.z = dock.z; boatE.label = 'Turun ke Dermaga'; C.toast('Berlayar! Joystick buat jalan, Laut Dalam terbuka.'); }
    else { sailing = false; p.x = 0; p.z = 36; boat.position.x = dock.x; boat.position.z = dock.z; boat.rotation.y = dock.r; boatE.x = -3.4; boatE.z = 38; boatE.label = 'Naik Perahu'; C.toast('Kembali ke dermaga'); }
    $('interactBtn').textContent = boatE.label;
  } };
  C.TOWN_SHOPS.push(boatE);
  C.setWalkable(function (o, x, z) { if (!sailing) return o(x, z); var d = Math.hypot(x, z); return d > C.ISLAND_RADIUS + 1 && d < 260 && !(Math.abs(x) < 2.7 && z > 27); });
  C.setNearWater(function (o) { return sailing || o(); });
  C.setGround(function (o, x, z) { return sailing ? 0.24 : o(x, z); });

  /* ===== EVENT ===== */
  var EV = [
    { n: 'Golden Hour', d: 'Peluang ikan Emas naik!', c: 'rgba(255,200,60,0.18)', b: '#c98a10', up: 0.35, muts: ['emas'], boost: 1.1 },
    { n: 'Blood Moon', d: 'Ikan Hantu & Pelangi bermunculan!', c: 'rgba(200,20,40,0.22)', b: '#a01828', up: 0.3, muts: ['ghost', 'pelangi'], boost: 1.25 }
  ];
  var evNow = null, evEnd = 0, evNext = performance.now() / 1000 + 150 + Math.random() * 120;
  var evO = document.createElement('div'); evO.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:7;opacity:0;transition:opacity 1.5s'; document.body.appendChild(evO);
  var evB = document.createElement('div'); evB.id = 'evBadge'; document.body.appendChild(evB);
  function evTick(now) {
    if (!evNow && now >= evNext) {
      evNow = EV[Math.floor(Math.random() * EV.length)]; evEnd = now + 100;
      evO.style.background = 'radial-gradient(ellipse at center, transparent 40%, ' + evNow.c + ' 100%)'; evO.style.opacity = 1;
      evB.style.background = evNow.b; evB.style.display = 'block';
      C.toast('EVENT: ' + evNow.n + '! ' + evNow.d); C.Sfx.levelUp(); C.vibe([60, 40, 60]);
    } else if (evNow && now >= evEnd) {
      evNow = null; evNext = now + 240 + Math.random() * 240; evO.style.opacity = 0; evB.style.display = 'none'; C.toast('Event selesai');
    }
    if (evNow) { var r = Math.max(0, Math.ceil(evEnd - now)), tx = evNow.n + ' • ' + Math.floor(r / 60) + ':' + ('0' + (r % 60)).slice(-2); if (evB.textContent !== tx) evB.textContent = tx; }
  }
  C.hookRoll(function (orig, boost) {
    var ev = evNow, r = orig(boost * (ev ? ev.boost : 1));
    if (ev && r.mutation.id === 'normal' && Math.random() < ev.up) {
      var id = ev.muts[Math.floor(Math.random() * ev.muts.length)];
      var m = C.MUTATIONS.filter(function (x) { return x.id === id; })[0];
      if (m) { r.mutation = m; r.value = Math.round(r.fish.value * m.mult); }
    }
    return r;
  });

  /* ===== LOOP + MENU ===== */
  var last = 0, lx = 0, lz = 0, achT = 0;
  C.hookAnim(function (t) {
    var dt = Math.min(0.1, t - last); last = t;
    applyRod(t); applyCos(); animTank(t); evTick(t);
    var p = C.player.position;
    if (sailing) {
      boat.position.x = p.x; boat.position.z = p.z; boatE.x = p.x; boatE.z = p.z;
      var dx = p.x - lx, dz = p.z - lz;
      if (dx * dx + dz * dz > 1e-5) { var d = Math.atan2(dx, dz) - boat.rotation.y; d = Math.atan2(Math.sin(d), Math.cos(d)); boat.rotation.y += d * Math.min(1, dt * 6); }
    }
    lx = p.x; lz = p.z;
    if (t - achT > 2) { achT = t; checkAch(); }
  });
  function addMenu() {
    var host = $('menuPanel') || $('hudPills'); if (!host) return;
    [['Trofi', renderT, mT], ['Karakter', renderChar, mC], ['Pasar', renderP, mP], ['Rekor', renderR, mR]].forEach(function (x) {
      var b = document.createElement('button'); b.className = 'hudPill'; b.textContent = x[0];
      b.onclick = function () { var mp = $('menuPanel'); if (mp) mp.classList.remove('show'); x[1](); x[2].open(); };
      host.appendChild(b);
    });
  }
  if (document.readyState === 'complete') addMenu(); else window.addEventListener('load', addMenu);
};
"""

BRIDGE = r"""
  window.__PMC = {
    scene: scene, player: player, body: body, legL: legL, rodMesh: rodMesh, boatMesh: boatMesh, town: town,
    TOWN_SHOPS: TOWN_SHOPS, TOWN_COLLIDERS: TOWN_COLLIDERS, FISH_TABLE: FISH_TABLE, MUTATIONS: MUTATIONS,
    RARITY_COLOR: RARITY_COLOR, RARITY_LABEL: RARITY_LABEL, RARITY_ORDER: RARITY_ORDER, ROD_TIERS: ROD_TIERS,
    GEAR_COLORS: GEAR_COLORS, ISLAND_RADIUS: ISLAND_RADIUS, DECK_Y: DECK_Y, fmtKg: fmtKg,
    makeSignTexture: makeSignTexture, fishIconCanvas: fishIconCanvas, addXp: addXp, Sfx: Sfx, vibe: vibe,
    get save() { return save; }, persist: persistSave, refresh: refreshHud, toast: showToast,
    hookFinish: function (w) { var o = finishReel; finishReel = function (ok) { var c = currentCatch; o(ok); w(ok, c); }; },
    hookRoll: function (w) { var o = rollFish; rollFish = function (b) { return w(o, b); }; },
    hookAnim: function (w) { var o = updateTownAnim; updateTownAnim = function (t) { o(t); w(t); }; },
    setNearWater: function (f) { var o = nearWater; nearWater = function () { return f(o); }; },
    setWalkable: function (f) { var o = walkable; walkable = function (x, z) { return f(o, x, z); }; },
    setGround: function (f) { var o = groundHeightAt; groundHeightAt = function (x, z) { return f(o, x, z); }; }
  };
  if (window.PMExt) { try { window.PMExt(window.__PMC); } catch (e) { console.warn('PMExt gagal:', e); } }
"""

LOGNEW = 'var LOG = [\n    ["Trofi & Perahu", ["Menu baru: Trofi (17 achievement), Karakter (baju/celana/topi), Pasar (harga ikan berubah tiap hari), Rekor.", "Perahu di dermaga kiri buat berlayar ke Laut Dalam. Akuarium di plaza buat pajang ikan langka.", "Event acak Golden Hour dan Blood Moon: mutasi lebih sering muncul.", "Joran sekarang punya warna dan cahaya sesuai tier."]],'

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)

def patch(p):
    s = read(p)
    s = re.sub(r'<!-- pm-ext -->.*?<!-- /pm-ext -->\s*', '', s, flags=re.S)
    a = '<script src="three.min.js"></script>'
    if a not in s: print('WARN: anchor three.min.js gak ketemu di', p); return
    s = s.replace(a, '<!-- pm-ext -->\n<style>' + EXT_CSS + '</style>\n<script>' + EXT_JS + '</script>\n<!-- /pm-ext -->\n' + a, 1)
    if 'window.__PMC' not in s:
        m = re.search(r'\n  boot\(\);\n\}\)\(\);', s)
        if not m: print('WARN: anchor boot() gak ketemu di', p); return
        s = s[:m.start()] + '\n' + BRIDGE + s[m.start():]
    P = '(window.PMP ? window.PMP(%s.fish.id) : 1)'
    for old, new in [
        ('const val = Math.round(e.fish.value * e.mutation.mult);', 'const val = Math.round(e.fish.value * ' + P % 'e' + ' * e.mutation.mult);'),
        ('const val = Math.round(entry.fish.value * entry.mutation.mult);', 'const val = Math.round(entry.fish.value * ' + P % 'entry' + ' * entry.mutation.mult);'),
        ('sum += Math.round(e.fish.value * e.mutation.mult) * e.count;', 'sum += Math.round(e.fish.value * ' + P % 'e' + ' * e.mutation.mult) * e.count;')]:
        if new in s: continue
        if old in s: s = s.replace(old, new)
        else: print('WARN: harga gak ketemu:', old[:40])
    s = re.sub(r'(<div id="versionBadge">)v[\d.]+(</div>)', r'\1v2.5\2', s)
    s = re.sub(r"var VER = 'v[\d.]+'", "var VER = 'v2.5'", s)
    if 'Trofi & Perahu' not in s: s = s.replace('var LOG = [', LOGNEW, 1)
    write(p, s); print('OK :', p)

for p in ['index.html', 'www/index.html']:
    if os.path.exists(p): patch(p)
print('Selesai.')
