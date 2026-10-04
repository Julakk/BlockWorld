<script>
/* PM-GACHA v3 (v4.13) - Mesin Gacha 3D, panggung HD, skin rod 3D beraura */
(function () {
  'use strict';
  var C = window.__PMC, T = window.THREE;
  if (!C || !T || window.__pmGacha) return;
  window.__pmGacha = true;
  var PI = Math.PI;

  /* ---------- setelan ---------- */
  var COST1 = 100, COST10 = 900, PITY_MAX = 60;
  var ORDER = ['common', 'rare', 'epic', 'legendary'];
  var TIER = {
    common: { n: 'Common', c: '#9fb4bd', w: 60, d: '10-50 koin / Bait' },
    rare: { n: 'Rare', c: '#4aa8ff', w: 25, d: '100-300 koin / Skin Rod Biasa' },
    epic: { n: 'Epic', c: '#b56bff', w: 12, d: '500 koin / Skin Rod Efek Cahaya' },
    legendary: { n: 'Legendary', c: '#ffc233', w: 3, d: '2.000 koin / Skin Rod Animasi Unik' }
  };
  var COIN_CHANCE = { rare: 0.30, epic: 0.25, legendary: 0.15 };
  var DUP = { rare: 30, epic: 75, legendary: 200 };
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
  var NOSKIN = { id: 'none', n: 'Tanpa Skin', t: 'none', k: 'solid', c: '#8a929a' };
  var OP = { solid: 0.3, glow: 0.6, rainbow: 0.7, fire: 0.85, galaxy: 0.8 };
  var SPD = { solid: 0.15, glow: 0.35, rainbow: 0.5, fire: 1.1, galaxy: 0.12 };

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
  function rewardName(r) {
    if (r.kind === 'coin') return '+' + fmt(r.coins) + ' koin';
    if (r.kind === 'bait') return baitName(r.id);
    var sk = skinById(r.id); return (sk ? sk.n : 'Skin') + (r.dup ? ' (duplikat +' + r.coins + ')' : '');
  }
  function cssCol(col, m) {
    var c = new T.Color(col); c.r = Math.min(1, c.r * m); c.g = Math.min(1, c.g * m); c.b = Math.min(1, c.b * m);
    return '#' + c.getHexString();
  }
  var dotT = null, rayT = null, starT = null;
  function dotTex() {
    if (dotT) return dotT;
    var c = document.createElement('canvas'); c.width = c.height = 64;
    var g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.45, 'rgba(255,255,255,.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    dotT = new T.CanvasTexture(c); return dotT;
  }
  function rayTex() {
    if (rayT) return rayT;
    var c = document.createElement('canvas'); c.width = c.height = 256;
    var g = c.getContext('2d'); g.translate(128, 128);
    var gr = g.createRadialGradient(0, 0, 0, 0, 0, 128);
    gr.addColorStop(0, 'rgba(255,255,255,.95)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr;
    for (var i = 0; i < 14; i++) {
      g.save(); g.rotate(i * PI * 2 / 14);
      g.beginPath(); g.moveTo(0, 0); g.lineTo(-11, -128); g.lineTo(11, -128); g.closePath(); g.fill(); g.restore();
    }
    rayT = new T.CanvasTexture(c); return rayT;
  }
  function starTex() {
    if (starT) return starT;
    var c = document.createElement('canvas'); c.width = c.height = 128;
    var g = c.getContext('2d'); g.translate(64, 64);
    var gr = g.createRadialGradient(0, 0, 0, 0, 0, 64);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,255,255,.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr;
    g.beginPath(); g.moveTo(0, -62); g.quadraticCurveTo(5, -5, 62, 0); g.quadraticCurveTo(5, 5, 0, 62); g.quadraticCurveTo(-5, 5, -62, 0); g.quadraticCurveTo(-5, -5, 0, -62); g.closePath(); g.fill();
    g.beginPath(); g.arc(0, 0, 14, 0, PI * 2); g.fill();
    starT = new T.CanvasTexture(c); return starT;
  }
  var CV = {};
  function cvas(key, w, h, draw) {
    if (!CV[key]) { var c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); CV[key] = c; }
    return CV[key];
  }
  function mkTex(c, rx, ry) {
    var t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(rx || 1, ry || 1); t.needsUpdate = true; return t;
  }

  /* ---------- tekstur batang & aura per skin ---------- */
  function shaftCanvas(sk) {
    return cvas('sh_' + sk.id, 64, 256, function (g, w, h) {
      var k = sk.k, i, x, y, j, gr, rr;
      if (k === 'rainbow') {
        for (i = 0; i < h; i++) { g.fillStyle = 'hsl(' + Math.round(i / h * 360) + ',85%,58%)'; g.fillRect(0, i, w, 1); }
      } else if (k === 'fire') {
        gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#2a0e06'); gr.addColorStop(0.5, '#150805'); gr.addColorStop(1, '#0a0402');
        g.fillStyle = gr; g.fillRect(0, 0, w, h); g.lineCap = 'round';
        for (i = 0; i < 18; i++) {
          x = Math.random() * w; y = Math.random() * h;
          g.strokeStyle = 'rgba(255,' + Math.round(110 + Math.random() * 100) + ',20,' + (0.5 + Math.random() * 0.5) + ')';
          g.lineWidth = 1 + Math.random() * 2; g.beginPath(); g.moveTo(x, y);
          for (j = 0; j < 5; j++) { x += Math.random() * 14 - 7; y += Math.random() * 26 - 4; g.lineTo(x, y); }
          g.stroke();
        }
      } else if (k === 'galaxy') {
        gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#0a0b36'); gr.addColorStop(0.5, '#2b1a80'); gr.addColorStop(1, '#0a2d63');
        g.fillStyle = gr; g.fillRect(0, 0, w, h);
        for (i = 0; i < 7; i++) {
          x = Math.random() * w; y = Math.random() * h; rr = 30 + Math.random() * 40;
          gr = g.createRadialGradient(x, y, 0, x, y, rr);
          gr.addColorStop(0, i % 2 ? 'rgba(160,100,255,.55)' : 'rgba(70,210,255,.4)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
          g.fillStyle = gr; g.fillRect(x - rr, y - rr, rr * 2, rr * 2);
        }
        for (i = 0; i < 70; i++) {
          g.fillStyle = 'rgba(255,255,255,' + (0.5 + Math.random() * 0.5) + ')';
          g.beginPath(); g.arc(Math.random() * w, Math.random() * h, 0.6 + Math.random() * 1.2, 0, PI * 2); g.fill();
        }
      } else {
        gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, cssCol(sk.c, 1.35)); gr.addColorStop(1, cssCol(sk.c, 0.55));
        g.fillStyle = gr; g.fillRect(0, 0, w, h);
      }
      if (k !== 'fire' && k !== 'galaxy') {
        g.lineWidth = 2;
        for (i = -h; i < w + h; i += 14) {
          g.strokeStyle = 'rgba(255,255,255,.09)'; g.beginPath(); g.moveTo(i, 0); g.lineTo(i + 90, h); g.stroke();
          g.strokeStyle = 'rgba(0,0,0,.12)'; g.beginPath(); g.moveTo(i + 7, 0); g.lineTo(i + 97, h); g.stroke();
        }
      }
    });
  }
  function auraCanvas(sk) {
    return cvas('au_' + sk.id, 64, 256, function (g, w, h) {
      var k = sk.k, i, x, y, gr, hh, ww, len, rr;
      if (k === 'fire') {
        for (i = 0; i < 22; i++) {
          x = Math.random() * w; hh = 80 + Math.random() * 170; ww = 6 + Math.random() * 10;
          gr = g.createLinearGradient(0, h, 0, h - hh);
          gr.addColorStop(0, 'rgba(255,235,130,.95)'); gr.addColorStop(0.45, 'rgba(255,120,20,.75)'); gr.addColorStop(1, 'rgba(150,15,0,0)');
          g.fillStyle = gr; g.beginPath(); g.moveTo(x - ww, h);
          g.quadraticCurveTo(x - ww * 0.3, h - hh * 0.55, x, h - hh);
          g.quadraticCurveTo(x + ww * 0.3, h - hh * 0.55, x + ww, h); g.closePath(); g.fill();
        }
      } else if (k === 'rainbow') {
        for (i = 0; i < h; i++) { g.fillStyle = 'hsla(' + Math.round(i / h * 360) + ',100%,60%,.5)'; g.fillRect(0, i, w, 1); }
        for (i = 0; i < 24; i++) {
          x = Math.random() * w; y = Math.random() * h; len = 30 + Math.random() * 120;
          g.strokeStyle = 'rgba(255,255,255,' + (0.3 + Math.random() * 0.5) + ')'; g.lineWidth = 1 + Math.random() * 2;
          g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + len); g.stroke();
        }
      } else if (k === 'galaxy') {
        for (i = 0; i < 9; i++) {
          x = Math.random() * w; y = Math.random() * h; rr = 25 + Math.random() * 45;
          gr = g.createRadialGradient(x, y, 0, x, y, rr);
          gr.addColorStop(0, i % 2 ? 'rgba(150,90,255,.6)' : 'rgba(60,200,255,.45)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
          g.fillStyle = gr; g.fillRect(x - rr, y - rr, rr * 2, rr * 2);
        }
        for (i = 0; i < 40; i++) {
          g.fillStyle = 'rgba(255,255,255,' + (0.6 + Math.random() * 0.4) + ')';
          g.beginPath(); g.arc(Math.random() * w, Math.random() * h, 0.8 + Math.random() * 1.4, 0, PI * 2); g.fill();
        }
      } else {
        var cc = new T.Color(sk.c), rgb = [Math.round((cc.r * 0.6 + 0.4) * 255), Math.round((cc.g * 0.6 + 0.4) * 255), Math.round((cc.b * 0.6 + 0.4) * 255)];
        g.fillStyle = 'rgba(' + rgb.join(',') + ',.16)'; g.fillRect(0, 0, w, h);
        for (i = 0; i < 34; i++) {
          x = Math.random() * w; y = Math.random() * h; len = 40 + Math.random() * 170;
          g.strokeStyle = 'rgba(' + rgb.join(',') + ',' + (0.25 + Math.random() * 0.6) + ')'; g.lineWidth = 1 + Math.random() * 3;
          g.beginPath(); g.moveTo(x, y); g.lineTo(x + (Math.random() * 6 - 3), y + len); g.stroke();
        }
      }
    });
  }

  /* ---------- joran skin 3D + aura (dipakai di tangan, panggung, dan ikon) ---------- */
  function makeSkinRod(sk, full, o) {
    o = o || {};
    var noAura = !!o.noAura, k = sk.k, tier = sk.t, isL = tier === 'legendary';
    var N = k === 'solid' ? 10 : (tier === 'epic' ? 18 : (o.pN || 26)), psize = o.psize || 0.09;
    var texes = [], geos = [], mats = [], i;
    function tx(c, rx, ry) { var t = mkTex(c, rx, ry); texes.push(t); return t; }

    var shT = tx(shaftCanvas(sk), 1, 1);
    var m = new T.MeshStandardMaterial({ color: 0xffffff, map: shT, roughness: 0.28, metalness: 0.55 }); mats.push(m);
    if (k === 'solid') { m.emissive.set(sk.c); m.emissiveIntensity = 0.08; }
    else if (k === 'glow') { m.emissive.set(sk.c); m.emissiveIntensity = 0.5; m.roughness = 0.22; }
    else { m.emissive.setHex(0xffffff); m.emissiveMap = shT; m.emissiveIntensity = k === 'rainbow' ? 0.45 : (k === 'fire' ? 0.9 : 0.8); }

    var root = new T.Group(), shaft = new T.Group(), tip = new T.Group(), tipPv = new T.Group();
    root.add(shaft); tipPv.position.y = 0.55; root.add(tipPv); tipPv.add(tip);
    var gs = new T.Mesh(new T.CylinderGeometry(0.0155, 0.0325, 1.1, 18), m); gs.castShadow = true; shaft.add(gs); geos.push(gs.geometry);
    var gt = new T.Mesh(new T.CylinderGeometry(0.0095, 0.0155, 0.42, 12).translate(0, 0.21, 0), m); tip.add(gt); geos.push(gt.geometry);
    var ringM = new T.MeshStandardMaterial({ color: (isL || tier === 'epic') ? 0xd9b25a : 0xcfd6dc, metalness: 0.85, roughness: 0.28 }); mats.push(ringM);
    [-0.32, 0, 0.32].forEach(function (y) {
      var r = 0.0325 - 0.017 * (y + 0.55) / 1.1 + 0.004;
      var tr = new T.Mesh(new T.TorusGeometry(r, 0.0045, 6, 18), ringM); tr.rotation.x = PI / 2; tr.position.y = y; shaft.add(tr); geos.push(tr.geometry);
    });
    if (full) {
      var gm = new T.MeshStandardMaterial({ color: 0x2a2018, roughness: 0.9 }); mats.push(gm);
      var grip = new T.Mesh(new T.CylinderGeometry(0.038, 0.038, 0.24, 14), gm); grip.position.y = -0.4; shaft.add(grip); geos.push(grip.geometry);
      var steel = new T.MeshStandardMaterial({ color: 0xcfd6dc, metalness: 0.8, roughness: 0.28 }); mats.push(steel);
      var reel = new T.Mesh(new T.CylinderGeometry(0.055, 0.055, 0.06, 18), steel); reel.rotation.z = PI / 2; reel.position.set(0.05, -0.2, 0); shaft.add(reel); geos.push(reel.geometry);
      [0.05, 0.28, 0.48].forEach(function (y) {
        var g2 = new T.Mesh(new T.TorusGeometry(0.013, 0.003, 6, 12), steel);
        g2.position.set(0, y, 0.0325 - 0.017 * (y + 0.55) / 1.1 + 0.009); g2.rotation.x = PI / 2; shaft.add(g2); geos.push(g2.geometry);
      });
    }

    var auT = null, sleeveM = null, halos = [], flare = null, fs = isL ? 0.7 : 0.5, pg = null, pp = null, pc = null;
    var baseCol = new T.Color(sk.c), tc = new T.Color();
    if (!noAura) {
      auT = tx(auraCanvas(sk), 1, 2);
      sleeveM = new T.MeshBasicMaterial({ map: auT, transparent: true, opacity: OP[k], blending: T.AdditiveBlending, depthWrite: false, side: T.DoubleSide, fog: false }); mats.push(sleeveM);
      var s1 = new T.Mesh(new T.CylinderGeometry(0.05, 0.082, 1.1, 18, 1, true), sleeveM);
      var s2 = new T.Mesh(new T.CylinderGeometry(0.032, 0.05, 0.42, 12, 1, true).translate(0, 0.21, 0), sleeveM);
      s1.renderOrder = s2.renderOrder = 3; shaft.add(s1); tip.add(s2); geos.push(s1.geometry); geos.push(s2.geometry);
      var hc = k === 'fire' ? '#ff7a1a' : (k === 'galaxy' ? '#8a6cff' : sk.c);
      var halo = function (par, y, sz) {
        var s = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: hc, blending: T.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.8, fog: false }));
        s.position.set(0, y, 0); s.scale.set(sz, sz, 1); par.add(s); halos.push({ s: s, sz: sz, ph: Math.random() * 6 }); mats.push(s.material);
      };
      if (k === 'solid') halo(tip, 0.42, 0.3);
      else { halo(tip, 0.42, isL ? 0.75 : 0.55); halo(shaft, 0.1, isL ? 0.55 : 0.38); halo(shaft, -0.38, isL ? 0.5 : 0.34); }
      if (k !== 'solid') {
        flare = new T.Sprite(new T.SpriteMaterial({ map: starTex(), color: hc, blending: T.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.9, fog: false }));
        flare.position.set(0, 0.43, 0); flare.scale.set(fs, fs, 1); tip.add(flare); mats.push(flare.material);
      }
      pp = new Float32Array(N * 3); pc = new Float32Array(N * 3);
      pg = new T.BufferGeometry();
      pg.setAttribute('position', new T.BufferAttribute(pp, 3)); pg.setAttribute('color', new T.BufferAttribute(pc, 3));
      var pm = new T.PointsMaterial({ size: psize, map: dotTex(), vertexColors: true, transparent: true, depthWrite: false, blending: T.AdditiveBlending, sizeAttenuation: true, fog: false });
      var pts = new T.Points(pg, pm); pts.frustumCulled = false; shaft.add(pts); geos.push(pg); mats.push(pm);
    }

    function update(t, dt) {
      var i, u, a, f, p, r, tw, w, h;
      if (k === 'rainbow') shT.offset.y -= 0.25 * dt;
      else if (k === 'fire') m.emissiveIntensity = 0.7 + 0.3 * Math.sin(t * 17) * Math.sin(t * 5.3);
      else if (k === 'galaxy') { shT.offset.y -= 0.03 * dt; m.emissiveIntensity = 0.65 + 0.2 * Math.sin(t * 1.7); }
      else if (k === 'glow') m.emissiveIntensity = 0.42 + 0.3 * Math.sin(t * 3);
      if (noAura) return;
      auT.offset.y -= SPD[k] * dt;
      sleeveM.opacity = OP[k] * (0.8 + 0.2 * Math.sin(t * (k === 'fire' ? 14 : 3)));
      for (i = 0; i < halos.length; i++) {
        h = halos[i]; f = 1 + 0.15 * Math.sin(t * 3 + h.ph);
        if (k === 'fire') f = 1 + 0.25 * Math.sin(t * 13 + h.ph) * Math.sin(t * 4.1 + h.ph);
        h.s.scale.set(h.sz * f, h.sz * f, 1);
        if (k === 'rainbow') h.s.material.color.setHSL((t * 0.25 + h.ph * 0.05) % 1, 1, 0.6);
      }
      if (flare) {
        flare.material.rotation = t * (k === 'fire' ? 0.5 : 1.2);
        f = fs * (1 + 0.2 * Math.sin(t * 4)); flare.scale.set(f, f, 1);
        if (k === 'rainbow') flare.material.color.setHSL((t * 0.3) % 1, 1, 0.65);
      }
      for (i = 0; i < N; i++) {
        u = i / N; p = i * 3;
        if (k === 'rainbow') {
          a = t * 2.6 + u * PI * 4;
          pp[p] = Math.cos(a) * 0.075; pp[p + 1] = -0.5 + u * 1.45; pp[p + 2] = Math.sin(a) * 0.075;
          tc.setHSL((u + t * 0.25) % 1, 1, 0.6); pc[p] = tc.r; pc[p + 1] = tc.g; pc[p + 2] = tc.b;
        } else if (k === 'fire') {
          f = (t * 0.85 + u) % 1; w = 1 - f;
          pp[p] = Math.sin(i * 7.3 + t * 4) * 0.05 * (0.3 + f); pp[p + 1] = -0.25 + f * 1.2; pp[p + 2] = Math.cos(i * 5.1 + t * 3.1) * 0.05 * (0.3 + f);
          pc[p] = w; pc[p + 1] = 0.75 * w * w; pc[p + 2] = 0.2 * w * w * w;
        } else if (k === 'galaxy') {
          a = t * (0.6 + (i % 4) * 0.35) + u * PI * 2; r = 0.06 + (i % 5) * 0.02; tw = 0.5 + 0.5 * Math.sin(t * 5 + i * 1.7);
          pp[p] = Math.cos(a) * r; pp[p + 1] = -0.5 + ((i * 0.37 + t * 0.06) % 1) * 1.45; pp[p + 2] = Math.sin(a) * r;
          tc.setHSL(0.55 + 0.2 * ((i * 0.31) % 1), 0.8, 0.55 + 0.3 * tw);
          w = 0.3 + 0.7 * tw; pc[p] = tc.r * w; pc[p + 1] = tc.g * w; pc[p + 2] = tc.b * w;
        } else if (k === 'glow') {
          a = t * (1.2 + (i % 3) * 0.4) + u * PI * 2; r = 0.09 + (i % 3) * 0.015; tw = 0.5 + 0.5 * Math.sin(t * 4 + i * 1.3);
          pp[p] = Math.cos(a) * r; pp[p + 1] = -0.45 + ((i * 0.37 + t * 0.18) % 1) * 1.4; pp[p + 2] = Math.sin(a) * r;
          tc.copy(baseCol).multiplyScalar(0.4 + 0.9 * tw); pc[p] = tc.r; pc[p + 1] = tc.g; pc[p + 2] = tc.b;
        } else {
          f = (t * 0.22 + u) % 1; a = u * PI * 2 + t * 0.8; r = 0.08 + 0.03 * f; w = Math.sin(f * PI) * 1.2;
          pp[p] = Math.cos(a) * r; pp[p + 1] = -0.4 + f * 1.3; pp[p + 2] = Math.sin(a) * r;
          pc[p] = baseCol.r * w; pc[p + 1] = baseCol.g * w; pc[p + 2] = baseCol.b * w;
        }
      }
      pg.attributes.position.needsUpdate = true; pg.attributes.color.needsUpdate = true;
    }
    function dispose() {
      geos.forEach(function (g) { g.dispose(); }); mats.forEach(function (x) { x.dispose(); }); texes.forEach(function (x) { x.dispose(); });
    }
    return { root: root, shaft: shaft, tip: tip, update: update, dispose: dispose };
  }

  /* ---------- ikon skin 3D (dirender sekali, dicache) ---------- */
  var thumbs = {}, thumbTried = false;
  function makeThumbs() {
    if (thumbTried) return; thumbTried = true;
    var r = null;
    try {
      var W = 144, cv = document.createElement('canvas'); cv.width = cv.height = W;
      r = new T.WebGLRenderer({ canvas: cv, antialias: true, alpha: true, preserveDrawingBuffer: true });
      r.setPixelRatio(1); r.setSize(W, W, false); r.setClearColor(0x000000, 0);
      var sc = new T.Scene(); sc.add(new T.HemisphereLight(0xe6f4ff, 0x3b4650, 1.0));
      var dl = new T.DirectionalLight(0xfff0d0, 1.2); dl.position.set(2, 4, 5); sc.add(dl);
      var cam = new T.PerspectiveCamera(30, 1, 0.1, 50); cam.position.set(0.1, 0.2, 3.7); cam.lookAt(0.1, 0.17, 0);
      [null].concat(SKINS).forEach(function (sk) {
        var rod = makeSkinRod(sk || NOSKIN, true, { noAura: !sk, pN: 30, psize: 0.14 });
        rod.root.rotation.z = -0.62; rod.root.rotation.y = -0.4; sc.add(rod.root);
        rod.update(1.4, 0.016); rod.update(1.45, 0.05);
        r.render(sc, cam); thumbs[sk ? sk.id : ''] = cv.toDataURL('image/png');
        sc.remove(rod.root); rod.dispose();
      });
    } catch (e) { console.warn('ikon skin 3D gagal', e); thumbs = {}; }
    if (r) { try { r.dispose(); if (r.forceContextLoss) r.forceContextLoss(); } catch (e) {} }
  }
  function thumbHtml(sk) {
    var t = TIER[sk.t];
    if (thumbs[sk.id]) return '<img class="gcTh" alt="" src="' + thumbs[sk.id] + '" style="--rc:' + t.c + '">';
    return '<div class="gcSw" style="' + swatch(sk) + '"></div>';
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

  var busy = false, animT = 0, safeT = 0;
  var st = { tab: 'pull', anim: false, last: null, best: 'common', bestRes: null };

  function pull(n) {
    var s = C.save, cost = n === 1 ? COST1 : COST10;
    if (busy) return;
    if (s.coins < cost) { C.toast('Koin kurang, butuh ' + fmt(cost)); return; }
    s.coins -= cost;
    var g = s.gacha = s.gacha || { pity: 0, total: 0 }, out = [], best = 0, bi = 0, i;
    for (i = 0; i < n; i++) {
      g.pity++; g.total++;
      var t = g.pity >= PITY_MAX ? 'legendary' : rollTier(n === 10 && i === 9 ? 'rare' : 'common');
      if (t === 'legendary') g.pity = 0;
      var r = reward(t); apply(r); out.push(r);
      if (ORDER.indexOf(t) > best) { best = ORDER.indexOf(t); bi = i; }
    }
    C.persist(); C.refresh(); C.Sfx.tap();
    st.last = out; st.best = ORDER[best]; st.bestRes = out[bi]; st.anim = true; busy = true;
    render();
    clearTimeout(animT);
    if (!stagePlay(out[bi])) animT = setTimeout(finish, 900);
    clearTimeout(safeT); safeT = setTimeout(finish, 7000);
  }
  function finish() {
    if (!st.anim) return;
    clearTimeout(animT); clearTimeout(safeT);
    st.anim = false; busy = false;
    if (!S3.played) {
      C.Sfx.catchFish(st.best);
      C.vibe(st.best === 'legendary' ? [100, 50, 100, 50, 160] : (st.best === 'epic' ? [60, 40, 60] : [30]));
    }
    render();
  }
  function skip() {
    if (!st.anim) return;
    if (S3.mode === 'cap') S3.t = Math.max(S3.t, 2.5);
    else if (S3.mode === 'reveal') S3.fast = true;
    else finish();
  }
  function equip(id) {
    var s = C.save;
    if (id && !(s.skins && s.skins[id])) return;
    s.skin = id; C.persist(); C.Sfx.tap();
    C.toast(id ? 'Skin ' + skinById(id).n + ' dipakai' : 'Skin dilepas');
    if (st.tab === 'skin' && S3.r && !st.anim) stagePreview(id);
    render();
  }

  /* ---------- UI ---------- */
  var css = document.createElement('style');
  css.textContent = [
    '.gcBox{width:min(96vw,880px)!important;max-height:92vh;max-height:92dvh}',
    '#gcMain{display:flex;flex-direction:column;flex:1;min-height:0}',
    '#gcStageCol{flex:none;padding:6px 14px 0}',
    '#gcStage{position:relative;width:100%;padding-top:62%;border-radius:16px;overflow:hidden;background:radial-gradient(circle at 50% 38%,#2f6f8a,#0b1c28 78%);touch-action:manipulation}',
    '#gcStage canvas{position:absolute;left:0;top:0;width:100%;height:100%;display:block}',
    '.gcNo{position:absolute;left:0;top:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--text-dim);padding:10px;text-align:center}',
    '#gcRName{min-height:22px;margin-top:6px;font-size:14px;font-weight:900;letter-spacing:.5px;text-align:center;text-shadow:0 2px 0 rgba(0,0,0,.55);color:#fff}',
    '#gcSide{flex:1;min-height:0;display:flex;flex-direction:column}',
    '#gcSide .modalBody{flex:1;min-height:0}',
    '@media (min-aspect-ratio:1/1){#gcMain{flex-direction:row}#gcStageCol{flex:0 0 44%;display:flex;flex-direction:column;justify-content:center;padding:8px 6px 8px 14px;box-sizing:border-box}#gcStage{padding-top:78%}}',
    '.gcTabs{display:flex;gap:7px;padding:8px 16px 10px}',
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
    '.gcTh{display:block;width:58px;height:58px;margin:4px auto 0;flex-shrink:0;border-radius:12px;border:2px solid var(--rc);object-fit:contain;background:radial-gradient(circle at 50% 40%,rgba(255,255,255,.14),#0b1c28 78%)}',
    '.rowItem .gcTh{margin:0}',
    '.gcSw{position:relative;width:44px;height:44px;border-radius:12px;border:2px solid rgba(255,255,255,.75);flex-shrink:0;margin:4px auto 0}',
    '.gcSw::after{content:"";position:absolute;left:7px;right:7px;top:50%;height:4px;border-radius:2px;background:rgba(255,255,255,.88);transform:rotate(-35deg)}',
    '.rowItem .gcSw{margin:0}',
    '.gcLocked .gcTh,.gcLocked .gcSw{filter:grayscale(1) brightness(.4)}',
    '@keyframes gcPop{from{transform:scale(.3);opacity:0}to{transform:scale(1);opacity:1}}',
    '@media (prefers-reduced-motion:reduce){.gcCard{animation:none!important;opacity:1}}'
  ].join('');
  document.head.appendChild(css);

  var ov = document.createElement('div'); ov.className = 'modalOverlay'; ov.id = 'modalGacha';
  ov.innerHTML = '<div class="modalBox gcBox"><div class="modalHead"><h2>Mesin Gacha Rod</h2><button class="modalClose" id="gcX" type="button">\u2715</button></div>' +
    '<div id="gcMain"><div id="gcStageCol"><div id="gcStage"></div><div id="gcRName"></div></div>' +
    '<div id="gcSide"><div class="gcTabs" id="gcTabs"><button class="gcTab on" data-tab="pull" type="button">Gacha</button><button class="gcTab" data-tab="skin" type="button">Skin Saya</button></div>' +
    '<div class="modalBody" id="gcBody"></div></div></div>' +
    '<div class="modalFoot"><span id="gcFoot"></span><span id="gcCoins"></span></div></div>';
  document.body.appendChild(ov);
  var body = $('gcBody');
  $('gcX').onclick = function () { ov.classList.remove('show'); };
  $('gcStage').addEventListener('pointerdown', skip);
  $('gcTabs').addEventListener('click', function (e) {
    var b = e.target.closest('[data-tab]'); if (!b) return;
    st.tab = b.getAttribute('data-tab'); render();
    if (!S3.r || st.anim) return;
    if (st.tab === 'skin') stagePreview(C.save.skin || ''); else stageIdle();
  });
  body.addEventListener('click', function (e) {
    var b = e.target.closest('[data-act]'); if (!b || b.disabled) return;
    var a = b.getAttribute('data-act');
    if (a === 'p1') pull(1); else if (a === 'p10') pull(10);
    else if (a === 'eq') equip(b.getAttribute('data-id'));
    else if (a === 'un') equip('');
    else if (a === 'pv') {
      var id = b.getAttribute('data-id');
      if (C.save.skins && C.save.skins[id]) { if (S3.r && !st.anim) stagePreview(id); }
      else C.toast('Skin belum dimiliki');
    }
  });
  new MutationObserver(function () {
    if (ov.classList.contains('show')) return;
    if (st.anim) { st.anim = false; busy = false; clearTimeout(animT); clearTimeout(safeT); }
    s3dispose();
  }).observe(ov, { attributes: true, attributeFilter: ['class'] });

  function card(r, i) {
    var t = TIER[r.tier], big, sub, sw = '';
    if (r.kind === 'coin') { big = '+' + fmt(r.coins); sub = r.note || 'Koin'; }
    else if (r.kind === 'bait') { big = baitName(r.id); sub = 'Bait baru!'; }
    else {
      var sk = skinById(r.id);
      sw = thumbHtml(sk);
      big = sk.n; sub = r.dup ? 'Duplikat +' + r.coins + ' koin' : 'SKIN BARU!';
    }
    return '<div class="gcCard" style="--rc:' + t.c + ';animation-delay:' + (i * 0.09).toFixed(2) + 's"><div class="gcTier">' + t.n + '</div>' + sw + '<div class="gcBig">' + big + '</div><div class="gcSub">' + sub + '</div></div>';
  }

  function render() {
    var s = C.save, g = s.gacha || { pity: 0, total: 0 }, h = '', i;
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
        h += '<div class="gcInfo"><b>Mengundi...</b> ketuk panggung buat lewati</div>';
      } else if (st.last) {
        h += '<div class="gcH">Hasil terakhir</div><div class="gcGrid">';
        for (i = 0; i < st.last.length; i++) h += card(st.last[i], i);
        h += '</div>';
      }
      $('gcFoot').textContent = 'Total pull: ' + fmt(g.total);
    } else {
      var owned = 0;
      h += '<div class="gcInfo">Ketuk skin yang dimiliki buat lihat preview 3D-nya di panggung.</div>';
      h += '<button class="rowBtn" type="button" data-act="un"' + (s.skin ? '' : ' disabled') + ' style="width:100%;margin-bottom:8px">Tanpa Skin</button>';
      SKINS.forEach(function (sk) {
        var has = !!(s.skins && s.skins[sk.id]), on = s.skin === sk.id, t = TIER[sk.t];
        if (has) owned++;
        h += '<div class="rowItem' + (has ? '' : ' gcLocked') + '" data-act="pv" data-id="' + sk.id + '" style="border-color:' + t.c + '">' + thumbHtml(sk) +
          '<div class="rowInfo"><div class="rowName" style="color:' + t.c + '">' + (has ? sk.n : '???') + '</div><div class="rowSub">' + t.n + ' \u2022 ' + KIND_LABEL[sk.k] + '</div></div>' +
          '<button class="rowBtn' + (on ? ' owned' : '') + '" type="button"' + (has && !on ? ' data-act="eq" data-id="' + sk.id + '"' : ' disabled') + '>' + (on ? 'Dipakai' : (has ? 'Pakai' : 'Terkunci')) + '</button></div>';
      });
      $('gcFoot').textContent = 'Terkumpul ' + owned + '/' + SKINS.length;
    }
    $('gcCoins').textContent = 'Koin: ' + fmt(s.coins);
    body.innerHTML = h;
  }

  /* ---------- panggung 3D (canvas baru tiap dibuka, dibuang saat ditutup) ---------- */
  var S3 = {};
  function dropObj(o) {
    if (!o) return;
    if (o.parent) o.parent.remove(o);
    o.traverse(function (x) {
      if (x.geometry && !x.isSprite) x.geometry.dispose();
      var mm = x.material;
      if (mm) { if (mm.length) mm.forEach(function (q) { q.dispose(); }); else mm.dispose(); }
    });
  }
  function s3clearObjs() {
    if (!S3.root) return;
    while (S3.root.children.length) dropObj(S3.root.children[0]);
    (S3.disp || []).forEach(function (f) { try { f(); } catch (e) {} });
    S3.disp = []; S3.cap = S3.rew = null;
  }
  function setCol(col) {
    S3.col = col;
    S3.glow.material.color.copy(col); S3.rays.material.color.copy(col); S3.pl.color.copy(col);
    S3.floor.material.color.copy(col); S3.flash.material.color.copy(col); S3.shock.material.color.copy(col);
    S3.ringM.color.copy(col); S3.beam.material.color.copy(col);
  }
  function s3init() {
    if (S3.r) return true;
    if (S3.fail) return false;
    var host = $('gcStage'); if (!host) return false;
    var cv = document.createElement('canvas'); host.innerHTML = ''; host.appendChild(cv);
    try { S3.r = new T.WebGLRenderer({ canvas: cv, antialias: true, alpha: true }); }
    catch (e) { S3.r = null; S3.fail = true; host.innerHTML = '<div class="gcNo">3D tidak didukung di perangkat ini</div>'; return false; }
    cv.addEventListener('webglcontextlost', function (ev) { ev.preventDefault(); });
    var r = S3.r; S3.cv = cv; S3.w = 0; S3.h = 0;
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    r.setClearColor(0x000000, 0);
    var sc = S3.sc = new T.Scene();
    sc.add(new T.HemisphereLight(0xe6f4ff, 0x2a3a4a, 0.95));
    var dl = new T.DirectionalLight(0xfff0d8, 1.1); dl.position.set(2.5, 4, 4); sc.add(dl);
    S3.pl = new T.PointLight(0xffffff, 0, 9); S3.pl.position.set(0, 0.6, 2); sc.add(S3.pl);
    S3.cam = new T.PerspectiveCamera(36, 4 / 3, 0.1, 50);
    S3.cam.position.set(0, 0.8, 6.2); S3.cam.lookAt(0, 0.35, 0);
    S3.root = new T.Group(); sc.add(S3.root);
    var pb = new T.Mesh(new T.CylinderGeometry(1.55, 1.75, 0.22, 48), new T.MeshStandardMaterial({ color: 0x1c2b38, roughness: 0.5, metalness: 0.7 })); pb.position.y = -1.05; sc.add(pb);
    var pd = new T.Mesh(new T.CylinderGeometry(1.3, 1.35, 0.08, 48), new T.MeshStandardMaterial({ color: 0x2a3d4d, roughness: 0.35, metalness: 0.8 })); pd.position.y = -0.91; sc.add(pd);
    S3.ringM = new T.MeshBasicMaterial({ color: 0x37d1c8 });
    var rg = new T.Mesh(new T.TorusGeometry(1.28, 0.035, 8, 64), S3.ringM); rg.rotation.x = PI / 2; rg.position.y = -0.86; sc.add(rg);
    S3.beam = new T.Mesh(new T.CylinderGeometry(1.0, 1.3, 4.6, 32, 1, true), new T.MeshBasicMaterial({ color: 0x37d1c8, transparent: true, opacity: 0.1, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide }));
    S3.beam.position.y = 1.4; sc.add(S3.beam);
    S3.floor = new T.Mesh(new T.RingGeometry(0.9, 1.6, 48).rotateX(-PI / 2), new T.MeshBasicMaterial({ color: 0x37d1c8, transparent: true, opacity: 0.25, depthWrite: false, side: T.DoubleSide, blending: T.AdditiveBlending }));
    S3.floor.position.y = -0.85; sc.add(S3.floor);
    S3.rays = new T.Mesh(new T.PlaneGeometry(8, 8), new T.MeshBasicMaterial({ map: rayTex(), color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide }));
    S3.rays.position.set(0, 0.3, -1); sc.add(S3.rays);
    S3.glow = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, blending: T.AdditiveBlending }));
    S3.glow.position.set(0, 0.2, 0.3); sc.add(S3.glow);
    S3.flash = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, blending: T.AdditiveBlending }));
    S3.flash.position.set(0, 0.2, 0.9); sc.add(S3.flash);
    S3.shock = new T.Mesh(new T.RingGeometry(0.92, 1, 56), new T.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide }));
    S3.shock.position.set(0, 0.2, 0.2); sc.add(S3.shock);
    var PN = 150; S3.PN = PN;
    S3.pp = new Float32Array(PN * 3); S3.pcol = new Float32Array(PN * 3); S3.pvel = new Float32Array(PN * 3);
    S3.plife = new Float32Array(PN); S3.pmax = new Float32Array(PN); S3.pbase = new Float32Array(PN * 3);
    for (var i = 0; i < PN; i++) S3.pp[i * 3 + 1] = -999;
    S3.pgeo = new T.BufferGeometry();
    S3.pgeo.setAttribute('position', new T.BufferAttribute(S3.pp, 3));
    S3.pgeo.setAttribute('color', new T.BufferAttribute(S3.pcol, 3));
    var pts = new T.Points(S3.pgeo, new T.PointsMaterial({ size: 0.16, map: dotTex(), vertexColors: true, transparent: true, depthWrite: false, blending: T.AdditiveBlending }));
    pts.frustumCulled = false; sc.add(pts);
    S3.disp = []; S3.t = 0; S3.run = false;
    return true;
  }
  function s3dispose() {
    if (S3.raf) cancelAnimationFrame(S3.raf);
    S3.run = false;
    if (S3.r) { try { s3clearObjs(); S3.r.dispose(); if (S3.r.forceContextLoss) S3.r.forceContextLoss(); } catch (e) {} }
    var host = $('gcStage'); if (host) host.innerHTML = '';
    S3 = {};
  }
  function s3run() { if (S3.run) return; S3.run = true; S3.last = 0; S3.raf = requestAnimationFrame(s3frame); }
  function emit(x, y, z, n, spd, up, col) {
    var c = 0;
    for (var i = 0; i < S3.PN && c < n; i++) {
      if (S3.plife[i] > 0) continue;
      var a = Math.random() * PI * 2, sp = spd * (0.35 + Math.random() * 0.65), j = i * 3;
      S3.pp[j] = x; S3.pp[j + 1] = y; S3.pp[j + 2] = z;
      S3.pvel[j] = Math.cos(a) * sp; S3.pvel[j + 1] = up * (0.4 + Math.random()); S3.pvel[j + 2] = Math.sin(a) * sp * 0.6;
      S3.pmax[i] = S3.plife[i] = 0.7 + Math.random() * 0.8;
      S3.pbase[j] = col.r; S3.pbase[j + 1] = col.g; S3.pbase[j + 2] = col.b; c++;
    }
  }
  function stepP(dt) {
    var i, j, f;
    for (i = 0; i < S3.PN; i++) {
      if (S3.plife[i] <= 0) continue;
      j = i * 3; S3.plife[i] -= dt;
      if (S3.plife[i] <= 0) { S3.pp[j + 1] = -999; S3.pcol[j] = S3.pcol[j + 1] = S3.pcol[j + 2] = 0; continue; }
      S3.pvel[j + 1] -= 4 * dt;
      S3.pp[j] += S3.pvel[j] * dt; S3.pp[j + 1] += S3.pvel[j + 1] * dt; S3.pp[j + 2] += S3.pvel[j + 2] * dt;
      f = S3.plife[i] / S3.pmax[i];
      S3.pcol[j] = S3.pbase[j] * f; S3.pcol[j + 1] = S3.pbase[j + 1] * f; S3.pcol[j + 2] = S3.pbase[j + 2] * f;
    }
    S3.pgeo.attributes.position.needsUpdate = true; S3.pgeo.attributes.color.needsUpdate = true;
  }

  function mkCapsule(hex) {
    var g = new T.Group();
    var mt = new T.MeshStandardMaterial({ color: hex, roughness: 0.22, metalness: 0.15, emissive: hex, emissiveIntensity: 0.18, side: T.DoubleSide });
    var mw = new T.MeshStandardMaterial({ color: 0xf2f4f6, roughness: 0.22, metalness: 0.1, side: T.DoubleSide });
    var top = new T.Group(), bot = new T.Group();
    top.add(new T.Mesh(new T.SphereGeometry(0.5, 28, 14, 0, PI * 2, 0, PI / 2), mt));
    bot.add(new T.Mesh(new T.SphereGeometry(0.5, 28, 14, 0, PI * 2, PI / 2, PI / 2), mw));
    var band = new T.Mesh(new T.TorusGeometry(0.5, 0.03, 8, 40), new T.MeshStandardMaterial({ color: 0xd9b25a, metalness: 0.7, roughness: 0.3 }));
    band.rotation.x = PI / 2;
    g.add(top); g.add(bot); g.add(band);
    g.userData = { top: top, bot: bot, band: band };
    return g;
  }
  function buildReward(res) {
    var group = new T.Group(), spin = new T.Group(); group.add(spin);
    var o = { group: group, spin: spin, base: 1, update: null, noSpin: false, disp: null };
    if (res.kind === 'skin') {
      var sk = res.id ? skinById(res.id) : NOSKIN;
      var rod = makeSkinRod(sk, true, { noAura: !res.id, pN: 60, psize: 0.2 }), tilt = new T.Group();
      tilt.rotation.z = 0.4; rod.root.position.y = -0.22; tilt.add(rod.root); spin.add(tilt); o.base = 1.45;
      o.disp = rod.dispose; o.update = function (t, dt) { rod.update(t, dt); };
    } else if (res.kind === 'coin') {
      var gm = new T.MeshStandardMaterial({ color: 0xffd24a, roughness: 0.25, metalness: 0.6, emissive: 0x7a4a00, emissiveIntensity: 0.35 });
      var dk = new T.MeshStandardMaterial({ color: 0xc8901c, roughness: 0.35, metalness: 0.6 });
      var pivs = [];
      [[-0.6, -0.1, 0.9], [0.6, 0.05, 0.0], [0, 0.4, 1.8]].forEach(function (p) {
        var pv = new T.Group(); pv.position.set(p[0], p[1], 0); pv.rotation.y = p[2];
        var coin = new T.Mesh(new T.CylinderGeometry(0.42, 0.42, 0.09, 32), gm); coin.rotation.x = PI / 2; pv.add(coin);
        var r1 = new T.Mesh(new T.TorusGeometry(0.34, 0.025, 8, 32), dk); r1.position.z = 0.05; pv.add(r1);
        var r2 = new T.Mesh(new T.TorusGeometry(0.34, 0.025, 8, 32), dk); r2.position.z = -0.05; pv.add(r2);
        spin.add(pv); pivs.push(pv);
      });
      o.noSpin = true;
      o.update = function (t, dt) { for (var i = 0; i < pivs.length; i++) pivs[i].rotation.y += dt * (2 + i * 0.6); };
    } else {
      var bc = (C.GEAR_COLORS.bait && C.GEAR_COLORS.bait[res.id]) || '#5fd36b';
      var om = new T.MeshStandardMaterial({ color: bc, roughness: 0.2, metalness: 0.2, emissive: bc, emissiveIntensity: 0.6 });
      spin.add(new T.Mesh(new T.SphereGeometry(0.42, 24, 16), om));
      var rm = new T.MeshStandardMaterial({ color: 0xffffff, emissive: bc, emissiveIntensity: 0.8 });
      var ra = new T.Mesh(new T.TorusGeometry(0.7, 0.03, 8, 40), rm); ra.rotation.x = 1.2; spin.add(ra);
      var rb = new T.Mesh(new T.TorusGeometry(0.6, 0.025, 8, 40), rm); rb.rotation.x = -0.7; spin.add(rb);
      o.update = function (t) { om.emissiveIntensity = 0.5 + 0.3 * Math.sin(t * 4); ra.rotation.z = t * 1.5; rb.rotation.z = -t * 1.2; };
    }
    return o;
  }

  function stageReset() {
    s3clearObjs();
    S3.t = 0; S3.burst = false; S3.done = false; S3.landed = false; S3.fast = false; S3.played = false;
    S3.rays.material.opacity = 0; S3.flash.material.opacity = 0; S3.shock.material.opacity = 0; S3.glow.material.opacity = 0; S3.pl.intensity = 0;
    S3.floor.material.opacity = 0.25;
  }
  function stageIdle() {
    if (!s3init()) return;
    stageReset(); S3.mode = 'idle';
    var col = new T.Color(0x37d1c8); setCol(col);
    S3.cap = mkCapsule(col.getHex()); S3.cap.scale.setScalar(1.5); S3.root.add(S3.cap);
    var n = $('gcRName'); n.textContent = ''; n.style.color = '#fff';
    s3run();
  }
  function stagePlay(res) {
    if (!s3init()) return false;
    stageReset(); S3.mode = 'cap'; S3.res = res;
    var col = new T.Color(TIER[res.tier].c); setCol(col);
    S3.cap = mkCapsule(col.getHex()); S3.cap.scale.setScalar(1.5); S3.cap.position.set(0, 3, 0); S3.root.add(S3.cap);
    var n = $('gcRName'); n.textContent = 'Mengundi...'; n.style.color = '#fff';
    s3run();
    return true;
  }
  function stagePreview(id) {
    if (!s3init()) return;
    stageReset(); S3.mode = 'preview';
    var sk = id ? skinById(id) : null;
    setCol(new T.Color(sk ? TIER[sk.t].c : '#9fb4bd'));
    S3.pvTier = sk ? ORDER.indexOf(sk.t) : 0;
    S3.rew = buildReward({ kind: 'skin', id: id || '' });
    if (S3.rew.disp) S3.disp.push(S3.rew.disp);
    S3.rew.group.scale.setScalar(S3.rew.base); S3.root.add(S3.rew.group);
    S3.pl.intensity = 0.8;
    var n = $('gcRName'); n.textContent = sk ? sk.n + ' (' + TIER[sk.t].n + ')' : 'Tanpa Skin'; n.style.color = sk ? TIER[sk.t].c : '#cfe6ec';
    s3run();
  }
  function burst() {
    var res = S3.res, ti = ORDER.indexOf(res.tier), col = S3.col;
    S3.mode = 'reveal'; S3.bt = S3.t; S3.burst = true; S3.played = true;
    S3.vtop = new T.Vector3(-1.4, 3.2, 0.4); S3.vbot = new T.Vector3(1.0, 0.4, 0.4);
    if (S3.cap) S3.cap.userData.band.visible = false;
    S3.rew = buildReward(res); if (S3.rew.disp) S3.disp.push(S3.rew.disp);
    S3.rew.group.scale.setScalar(0.01); S3.root.add(S3.rew.group);
    emit(0, 0.1, 0, 50 + ti * 30, 3.2 + ti * 0.8, 4.5, col);
    if (ti >= 2) emit(0, 0.1, 0, 30, 4, 5, new T.Color(0xffffff));
    S3.shake = 0.15 + ti * 0.08;
    C.Sfx.catchFish(res.tier);
    C.vibe(res.tier === 'legendary' ? [100, 50, 100, 50, 160] : (res.tier === 'epic' ? [60, 40, 60] : [30]));
    var n = $('gcRName'); n.textContent = TIER[res.tier].n.toUpperCase() + ' \u2022 ' + rewardName(res); n.style.color = TIER[res.tier].c;
  }
  function backOut(u) { var c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); }

  function s3frame(ts) {
    if (!S3.run || !S3.r) return;
    S3.raf = requestAnimationFrame(s3frame);
    var dt = S3.last ? Math.min(0.05, (ts - S3.last) / 1000) : 0; S3.last = ts;
    var cw = S3.cv.clientWidth, ch = S3.cv.clientHeight;
    if (cw && ch && (cw !== S3.w || ch !== S3.h)) { S3.w = cw; S3.h = ch; S3.r.setSize(cw, ch, false); S3.cam.aspect = cw / ch; S3.cam.updateProjectionMatrix(); }
    if (!S3.w) return;
    S3.t += dt;
    var t = S3.t, m = S3.mode, cam = S3.cam, col = S3.col, u, b, y, k, ti, rw;
    cam.position.set(0, 0.8, 6.2);
    if (m === 'idle') {
      if (S3.cap) { S3.cap.position.y = 0.1 + Math.sin(t * 1.8) * 0.12; S3.cap.rotation.y += dt * 0.8; S3.cap.rotation.z = Math.sin(t * 0.9) * 0.1; }
      S3.glow.material.opacity = 0.25; S3.glow.scale.setScalar(2.2 + Math.sin(t * 2) * 0.2);
    } else if (m === 'cap') {
      var cp = S3.cap;
      if (t < 0.8) { u = t / 0.8; y = -0.08 + 3.08 * (1 - u * u); }
      else if (t < 1.5) y = -0.08 + Math.abs(Math.sin((t - 0.8) * 8)) * 0.3 * Math.exp(-(t - 0.8) * 3.5);
      else y = -0.08;
      if (t >= 0.8 && !S3.landed) { S3.landed = true; C.Sfx.tap(); emit(0, -0.8, 0, 12, 1.6, 1.2, col); }
      k = t > 1.5 ? Math.min(1, (t - 1.5) / 1.0) : 0;
      cp.position.set(Math.sin(t * 61) * 0.03 * k, y + Math.sin(t * 53) * 0.02 * k, 0);
      cp.rotation.z = Math.sin(t * 38) * 0.18 * k; cp.rotation.y += dt * (0.6 + 4 * k);
      S3.glow.material.opacity = 0.15 + 0.7 * k; S3.glow.scale.setScalar(1.6 + 1.8 * k);
      S3.pl.intensity = 2.5 * k; S3.floor.material.opacity = 0.2 + 0.4 * k;
      if (k > 0 && Math.random() < 0.4) emit((Math.random() - 0.5) * 1.4, -0.7, (Math.random() - 0.5) * 0.6, 1, 0.2, 1.6, col);
      if (t >= 2.5) burst();
    } else if (m === 'reveal') {
      b = t - S3.bt; ti = ORDER.indexOf(S3.res.tier);
      if (S3.cap) {
        var ud = S3.cap.userData, sc2 = Math.max(0, 1 - b * 1.1);
        S3.vtop.y -= 7 * dt; S3.vbot.y -= 7 * dt;
        ud.top.position.addScaledVector(S3.vtop, dt); ud.bot.position.addScaledVector(S3.vbot, dt);
        ud.top.rotation.z += dt * 5; ud.bot.rotation.z -= dt * 4;
        S3.cap.scale.setScalar(Math.max(0.0001, 1.5 * sc2));
        if (sc2 <= 0) { dropObj(S3.cap); S3.cap = null; }
      }
      rw = S3.rew;
      if (rw) {
        rw.group.scale.setScalar(Math.max(0.01, backOut(Math.min(1, b / 0.7)) * rw.base));
        rw.group.position.y = 0.2 + Math.sin(t * 2.2) * 0.08;
        if (!rw.noSpin) rw.spin.rotation.y += dt * 1.5;
        if (rw.update) rw.update(t, dt);
      }
      S3.flash.material.opacity = Math.max(0, 1 - b * 2.2); S3.flash.scale.setScalar(2 + b * 9);
      S3.shock.material.opacity = Math.max(0, 0.9 - b * 1.1); S3.shock.scale.setScalar(0.2 + b * 8);
      S3.rays.material.opacity = (0.12 + 0.12 * ti) * Math.min(1, b * 3); S3.rays.rotation.z += dt * 0.35;
      if (S3.res.tier === 'legendary') { S3.rays.material.color.setHSL((t * 0.2) % 1, 0.8, 0.6); S3.glow.material.color.setHSL((t * 0.2 + 0.1) % 1, 0.9, 0.6); }
      S3.glow.material.opacity = 0.55; S3.glow.scale.setScalar(2.8 + Math.sin(t * 3) * 0.3);
      S3.pl.intensity = Math.max(0.6, 2.5 - b * 2);
      if (b < 0.5) { var sh = (0.5 - b) * S3.shake; cam.position.x += (Math.random() - 0.5) * sh; cam.position.y += (Math.random() - 0.5) * sh; }
      if (ti >= 2 && Math.random() < 0.35) emit((Math.random() - 0.5) * 1.6, -0.3, (Math.random() - 0.5) * 0.6, 1, 0.3, 1.8, col);
      if (!S3.done && b >= (S3.fast ? 0.4 : 1.1)) { S3.done = true; finish(); }
    } else if (m === 'preview') {
      rw = S3.rew;
      if (rw) {
        rw.spin.rotation.y += dt * 0.9; rw.group.position.y = 0.2 + Math.sin(t * 1.6) * 0.06;
        if (rw.update) rw.update(t, dt);
      }
      S3.glow.material.opacity = 0.18; S3.glow.scale.setScalar(2.6);
      S3.rays.material.opacity = S3.pvTier >= 2 ? 0.1 : 0; S3.rays.rotation.z += dt * 0.25;
      if (S3.pvTier === 3) S3.rays.material.color.setHSL((t * 0.2) % 1, 0.8, 0.6);
    }
    stepP(dt);
    S3.r.render(S3.sc, cam);
  }

  function openG() {
    makeThumbs(); render(); ov.classList.add('show');
    if (st.anim) return;
    if (st.tab === 'skin') stagePreview(C.save.skin || ''); else stageIdle();
  }
  window.PMGacha = { open: openG };

  /* ---------- Mesin Gacha 3D di plaza ---------- */
  var MX = 4.5, MZ = 19;
  var mach = new T.Group(); mach.position.set(MX, C.DECK_Y, MZ);
  function MS(c, o) { o = o || {}; o.color = c; if (o.roughness === undefined) o.roughness = 0.45; return new T.MeshStandardMaterial(o); }
  function mb(geo, mat, x, y, z) { var mm = new T.Mesh(geo, mat); mm.position.set(x, y, z); mm.castShadow = true; mm.receiveShadow = true; mach.add(mm); return mm; }
  var mRed = MS(0xd8352a, { roughness: 0.35, metalness: 0.2 }), mSteel = MS(0xcfd6dc, { metalness: 0.8, roughness: 0.28 }),
      mDark = MS(0x1c1f24, { roughness: 0.7 }), mGold = MS(0xd9b25a, { metalness: 0.85, roughness: 0.3 });
  mb(new T.BoxGeometry(1.5, 1.0, 1.1), mRed, 0, 0.5, 0);
  mb(new T.BoxGeometry(1.56, 0.1, 1.16), mGold, 0, 1.03, 0);
  mb(new T.BoxGeometry(1.56, 0.1, 1.16), mGold, 0, 0.05, 0);
  mb(new T.BoxGeometry(0.46, 0.3, 0.1), mDark, 0, 0.3, 0.55);
  mb(new T.BoxGeometry(0.36, 0.2, 0.06), MS(0x050607), 0, 0.28, 0.6);
  mb(new T.BoxGeometry(0.34, 0.34, 0.05), mSteel, 0.5, 0.68, 0.55);
  mb(new T.BoxGeometry(0.2, 0.025, 0.02), mDark, 0.5, 0.74, 0.585);
  var crank = new T.Group(); crank.position.set(-0.42, 0.68, 0.58); mach.add(crank);
  var cDisc = new T.Mesh(new T.CylinderGeometry(0.2, 0.2, 0.06, 24), mSteel); cDisc.rotation.x = PI / 2; crank.add(cDisc);
  var cArm = new T.Mesh(new T.BoxGeometry(0.34, 0.07, 0.07), mGold); cArm.position.set(0.12, 0, 0.07); crank.add(cArm);
  var cKnob = new T.Mesh(new T.SphereGeometry(0.07, 12, 10), MS(0xe8432f)); cKnob.position.set(0.3, 0, 0.1); crank.add(cKnob);
  mb(new T.CylinderGeometry(0.62, 0.7, 0.14, 28), mSteel, 0, 1.15, 0);
  var dome = new T.Mesh(new T.SphereGeometry(0.8, 28, 20), new T.MeshStandardMaterial({ color: 0xbfeaff, transparent: true, opacity: 0.22, roughness: 0.05, metalness: 0.1, depthWrite: false, side: T.DoubleSide }));
  dome.position.y = 1.95; dome.renderOrder = 2; mach.add(dome);
  mb(new T.CylinderGeometry(0.3, 0.55, 0.25, 24), mGold, 0, 2.82, 0);
  mb(new T.SphereGeometry(0.1, 12, 10), mGold, 0, 3.0, 0);
  var capsIn = [], palette = [0xff5a5a, 0x4aa8ff, 0xb56bff, 0xffc233, 0x5bff7a, 0xffffff];
  for (var ci = 0; ci < 18; ci++) {
    var ca = ci * 2.4, cr = 0.12 + (ci % 5) * 0.085, cy = 1.5 + (ci % 4) * 0.12 + (ci % 3) * 0.04, pc0 = palette[ci % palette.length];
    var cm = new T.Mesh(new T.SphereGeometry(0.14, 14, 10), MS(pc0, { roughness: 0.25, emissive: pc0, emissiveIntensity: 0.12 }));
    var cx = Math.cos(ca) * cr, cz = Math.sin(ca) * cr * 0.9;
    cm.position.set(cx, cy, cz); mach.add(cm); capsIn.push({ m: cm, x: cx, y: cy, ph: ci });
  }
  var bulbs = [];
  for (var bi = 0; bi < 10; bi++) {
    var ba = bi / 10 * PI * 2, bm = MS(0xffffff, { emissive: 0xffffff, emissiveIntensity: 1 });
    var bl = new T.Mesh(new T.SphereGeometry(0.05, 10, 8), bm); bl.position.set(Math.cos(ba) * 0.68, 1.26, Math.sin(ba) * 0.68); mach.add(bl); bulbs.push(bm);
  }
  var starsM = [];
  for (var si = 0; si < 3; si++) {
    var sm = new T.Mesh(new T.OctahedronGeometry(0.1), MS(0xfff2a0, { emissive: 0xffd45a, emissiveIntensity: 1 }));
    mach.add(sm); starsM.push(sm);
  }
  var mGlow = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0xffd45a, blending: T.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.3, fog: false }));
  mGlow.scale.set(3.4, 3.4, 1); mGlow.position.set(0, 2.0, -0.1); mach.add(mGlow);
  var mSign = new T.Sprite(new T.SpriteMaterial({ map: C.makeSignTexture('GACHA ROD', '#b3262a'), fog: false }));
  mSign.scale.set(2, 0.5, 1); mSign.position.set(0, 3.55, 0); mach.add(mSign);
  C.town.add(mach);
  C.TOWN_COLLIDERS.push({ x: MX, z: MZ, r: 1.25 });
  C.TOWN_SHOPS.push({ id: 'gacha', name: 'GACHA', label: 'Main Gacha Rod', x: MX, z: MZ + 0.2, action: function () { openG(); } });
  C.hookAnim(function (t) {
    var i, c, a;
    for (i = 0; i < capsIn.length; i++) {
      c = capsIn[i];
      c.m.position.y = c.y + Math.sin(t * 1.6 + c.ph) * 0.03 + (busy ? Math.sin(t * 30 + c.ph) * 0.04 : 0);
      c.m.position.x = c.x + Math.sin(t * 0.9 + c.ph * 1.3) * 0.025;
    }
    for (i = 0; i < bulbs.length; i++) {
      bulbs[i].emissive.setHSL((t * 0.3 + i / 10) % 1, 1, 0.5);
      bulbs[i].emissiveIntensity = 0.4 + 0.8 * Math.max(0, Math.sin(t * 5 - i * 0.63));
    }
    for (i = 0; i < starsM.length; i++) {
      a = t * 0.9 + i * 2.094;
      starsM[i].position.set(Math.cos(a) * 1.15, 2.1 + Math.sin(t * 1.7 + i) * 0.2, Math.sin(a) * 1.15);
      starsM[i].rotation.y = t * 2;
    }
    mGlow.material.opacity = 0.28 + 0.1 * Math.sin(t * 2);
    crank.rotation.z = busy ? t * 9 : Math.sin(t * 0.8) * 0.12;
  });

  /* ---------- skin 3D beraura di joran yang dipegang karakter ---------- */
  var rodM = C.rodMesh, curRod = null, skinId = null, lastT = 0;
  function findTip() {
    var kids = rodM.children;
    for (var i = 0; i < kids.length; i++) {
      var gm = kids[i].geometry;
      if (gm && gm.type === 'CylinderGeometry' && gm.parameters && gm.parameters.radiusTop === 0.008) return kids[i];
    }
    return null;
  }
  function clearSkin() {
    if (!curRod) return;
    [curRod.shaft, curRod.tip].forEach(function (g) { if (g.parent) g.parent.remove(g); });
    curRod.dispose(); curRod = null;
  }
  function buildSkin(sk) {
    var tp = findTip();
    curRod = makeSkinRod(sk, false, { pN: 28, psize: 0.075 });
    rodM.add(curRod.shaft);
    if (tp) tp.add(curRod.tip); else { curRod.tip.position.y = 0.55; rodM.add(curRod.tip); }
  }
  C.hookAnim(function (t) {
    var dt = Math.min(0.1, Math.max(0.001, t - lastT)); lastT = t;
    var s = C.save, id = (s && s.skin && s.skins && s.skins[s.skin]) ? s.skin : '';
    if (id !== skinId) { skinId = id; clearSkin(); var sk = id ? skinById(id) : null; if (sk) buildSkin(sk); }
    if (curRod) curRod.update(t, dt);
  });
})();

</script>
