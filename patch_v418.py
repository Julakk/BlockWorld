import re, sys, os

P = sys.argv[1] if len(sys.argv) > 1 else '/root/BlockWorld/index.html'
s = open(P, encoding='utf-8').read()
if '<!--PM-CAMP-START-->' in s:
    print('Sudah ke-patch, skip.')
    sys.exit(0)
open(P + '.bak418', 'w', encoding='utf-8').write(s)

def rep(old, new):
    global s
    n = s.count(old)
    if n != 1:
        print('GAGAL: anchor ketemu ' + str(n) + 'x -> ' + old[:70])
        sys.exit(1)
    s = s.replace(old, new)

CAMP = r'''<!--PM-CAMP-START-->
<script>
/* PM-CAMP v4.18 - api unggun, jalan setapak, Rumah Nelayan + Mbok Sari, kunang-kunang, kupu-kupu, flora */
(function () {
  'use strict';
  var C = window.__PMC, T = window.THREE;
  if (!C || !T || !C.hookAnim || !C.scene || window.__pmCamp) return;
  window.__pmCamp = true;
  var PI = Math.PI, scene = C.scene, R = C.ISLAND_RADIUS;
  var seed = 90210;
  function rr() { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; }
  function rb(a, b) { return a + rr() * (b - a); }
  function gh(x, z) { return Math.sin(x * 0.15) * Math.cos(z * 0.15) * 0.7 * (1 - Math.min(1, Math.hypot(x, z) / R)); }
  function safe(n, f) { try { f(); } catch (e) { console.warn('PM-CAMP ' + n, e); } }
  var hemi = null;
  scene.children.forEach(function (o) { if (o.isHemisphereLight && !hemi) hemi = o; });
  function night() { var hi = hemi ? hemi.intensity : 1; return Math.max(0, Math.min(1, (0.75 - hi) / 0.4)); }
  var ticks = [];

  /* ---------- tekstur ---------- */
  function cv(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
  function tex(c, rx, ry) { var t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; if (rx) t.repeat.set(rx, ry); t.anisotropy = 4; return t; }
  var _dot = null, _flame = null;
  function dotTex() {
    if (_dot) return _dot;
    var c = cv(64, 64), g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.4, 'rgba(255,255,255,.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); _dot = new T.CanvasTexture(c); return _dot;
  }
  function flameTex() {
    if (_flame) return _flame;
    var c = cv(128, 192), g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, 192);
    gr.addColorStop(0, 'rgba(255,60,0,0)'); gr.addColorStop(0.3, 'rgba(255,120,10,.65)'); gr.addColorStop(0.62, 'rgba(255,196,60,.95)'); gr.addColorStop(1, 'rgba(255,255,225,1)');
    g.fillStyle = gr; g.shadowColor = 'rgba(255,140,20,.9)'; g.shadowBlur = 16;
    g.beginPath(); g.moveTo(64, 10); g.bezierCurveTo(84, 60, 112, 100, 100, 150); g.bezierCurveTo(94, 178, 34, 178, 28, 150); g.bezierCurveTo(16, 100, 44, 60, 64, 10); g.closePath(); g.fill();
    _flame = new T.CanvasTexture(c); return _flame;
  }
  function stoneTex() {
    var c = cv(128, 128), g = c.getContext('2d'), i, j, x, y, v;
    g.fillStyle = '#8d9096'; g.fillRect(0, 0, 128, 128);
    for (i = 0; i < 700; i++) { v = 100 + Math.floor(rr() * 70); g.fillStyle = 'rgba(' + v + ',' + v + ',' + (v + 6) + ',.35)'; g.fillRect(rr() * 128, rr() * 128, 2 + rr() * 6, 2 + rr() * 4); }
    g.strokeStyle = 'rgba(30,30,40,.3)';
    for (i = 0; i < 5; i++) { g.beginPath(); x = rr() * 128; y = rr() * 128; g.moveTo(x, y); for (j = 0; j < 4; j++) { x += rr() * 20 - 10; y += rr() * 20 - 10; g.lineTo(x, y); } g.stroke(); }
    return tex(c, 1, 1);
  }
  function woodTex(base, rx, ry) {
    var c = cv(128, 128), g = c.getContext('2d'), i, k;
    g.fillStyle = base; g.fillRect(0, 0, 128, 128);
    for (i = 0; i < 8; i++) {
      g.fillStyle = 'rgba(0,0,0,' + (0.12 + 0.08 * (i % 2)) + ')'; g.fillRect(i * 16, 0, 2, 128);
      for (k = 0; k < 5; k++) { g.fillStyle = 'rgba(50,25,8,.14)'; g.fillRect(i * 16 + 3 + rr() * 9, rr() * 120, 1.5, 8 + rr() * 30); }
    }
    return tex(c, rx, ry);
  }
  function thatchTex(rx, ry) {
    var c = cv(128, 128), g = c.getContext('2d'), r, i, x, y;
    g.fillStyle = '#b99a55'; g.fillRect(0, 0, 128, 128);
    for (r = 0; r < 12; r++) { g.fillStyle = r % 2 ? 'rgba(120,90,35,.3)' : 'rgba(235,205,120,.22)'; g.fillRect(0, r * 10.7, 128, 5); }
    for (i = 0; i < 260; i++) { g.strokeStyle = 'rgba(' + ((110 + rr() * 80) | 0) + ',' + ((85 + rr() * 60) | 0) + ',30,.35)'; g.beginPath(); x = rr() * 128; y = rr() * 128; g.moveTo(x, y); g.lineTo(x + rr() * 4 - 2, y + 6 + rr() * 10); g.stroke(); }
    return tex(c, rx, ry);
  }
  function tentTex() {
    var c = cv(128, 128), g = c.getContext('2d'), i;
    for (i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#e8dcc0' : '#c4452f'; g.fillRect(i * 16, 0, 16, 128); }
    for (i = 0; i < 300; i++) { g.fillStyle = 'rgba(0,0,0,' + rr() * 0.06 + ')'; g.fillRect(rr() * 128, rr() * 128, 2, 2); }
    return tex(c, 2, 1);
  }
  function netTex() {
    var c = cv(128, 96), g = c.getContext('2d'), i;
    g.strokeStyle = 'rgba(225,215,180,.95)'; g.lineWidth = 2;
    for (i = -96; i < 128; i += 16) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i + 96, 96); g.stroke(); g.beginPath(); g.moveTo(i + 96, 0); g.lineTo(i, 96); g.stroke(); }
    return tex(c, 1, 1);
  }
  function batikTex() {
    var c = cv(128, 128), g = c.getContext('2d'), x, y;
    g.fillStyle = '#6b3b1d'; g.fillRect(0, 0, 128, 128);
    for (y = 0; y < 128; y += 32) for (x = 0; x < 128; x += 32) {
      g.fillStyle = 'rgba(235,190,110,.55)'; g.beginPath(); g.moveTo(x + 16, y + 4); g.lineTo(x + 28, y + 16); g.lineTo(x + 16, y + 28); g.lineTo(x + 4, y + 16); g.closePath(); g.fill();
      g.fillStyle = 'rgba(40,18,6,.7)'; g.beginPath(); g.arc(x + 16, y + 16, 4, 0, 7); g.fill();
    }
    return tex(c, 2, 1);
  }
  function MS(c, r, o) { o = o || {}; o.color = c; o.roughness = r === undefined ? 0.8 : r; return new T.MeshStandardMaterial(o); }
  function mesh(par, geo, mat, x, y, z, cs) {
    var m = new T.Mesh(geo, mat); m.position.set(x, y, z);
    if (cs !== false) { m.castShadow = true; m.receiveShadow = true; }
    par.add(m); return m;
  }
  function gable(half, rise, len, mat) {
    var g = new T.Group(), L = Math.hypot(half, rise), th = Math.atan2(half, rise);
    [-1, 1].forEach(function (s) {
      var pv = new T.Group(); pv.position.set(s * half, 0, 0); pv.rotation.z = s * th;
      var m = new T.Mesh(new T.PlaneGeometry(len, L), mat); m.rotation.y = PI / 2; m.position.y = L / 2; m.castShadow = true; m.receiveShadow = true;
      pv.add(m); g.add(pv);
    });
    return g;
  }
  function triMesh(w, h, mat) {
    var s = new T.Shape(); s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(0, h); s.closePath();
    var m = new T.Mesh(new T.ShapeGeometry(s), mat); m.castShadow = true; return m;
  }

  /* ---------- hindari pohon & kota ---------- */
  var palms = [];
  scene.traverse(function (o) {
    if (o.isMesh && o.geometry && o.geometry.type === 'CylinderGeometry' && o.geometry.parameters.height === 3.2 && o.geometry.parameters.radiusTop === 0.18) palms.push(o.position);
  });
  function nearPalm(x, z, r) { for (var i = 0; i < palms.length; i++) if (Math.hypot(x - palms[i].x, z - palms[i].z) < r) return true; return false; }
  function inTown(x, z) { return z > 14.2 && Math.abs(x) < 18; }

  /* ---------- layout ---------- */
  var HX = -6, HZ = -6, cx = 3, cz = 3, ci;
  var cands = [[3, 3], [4, 6], [1, 5], [6, 2], [2, -1], [-1, 3], [7, 6], [5, -2]];
  for (ci = 0; ci < cands.length; ci++) {
    var q = cands[ci];
    if (!nearPalm(q[0], q[1], 4.6) && !nearPalm(q[0] + 3.4, q[1] - 3.2, 2.4)) { cx = q[0]; cz = q[1]; break; }
  }
  function curvePts(pts, step) {
    var cu = new T.CatmullRomCurve3(pts.map(function (p) { return new T.Vector3(p[0], 0, p[1]); }), false, 'centripetal');
    return cu.getSpacedPoints(Math.max(2, Math.round(cu.getLength() / step)));
  }
  var P1 = curvePts([[-3, 16.8], [-2.6, 11], [cx, cz + 3.5], [cx - 4.4, cz + 2.2], [-6, -3.4]], 0.55);
  var P2 = curvePts([[-6.2, -3.4], [-9.2, -4.4], [-9.8, -11], [-7, -19], [-3.8, -29.2]], 0.55);
  var P3 = curvePts([[cx, cz + 3.5], [cx, cz + 1.55]], 0.55);
  var lines = [P1, P2, P3];
  function segD(px, pz, ax, az, bx, bz) {
    var dx = bx - ax, dz = bz - az, l = dx * dx + dz * dz, t = l ? ((px - ax) * dx + (pz - az) * dz) / l : 0;
    t = Math.max(0, Math.min(1, t)); return Math.hypot(px - (ax + dx * t), pz - (az + dz * t));
  }
  function pathD(x, z) {
    var m = 1e9, i, j, L, d;
    for (j = 0; j < lines.length; j++) { L = lines[j]; for (i = 0; i < L.length - 1; i++) { d = segD(x, z, L[i].x, L[i].z, L[i + 1].x, L[i + 1].z); if (d < m) m = d; } }
    return m;
  }
  var TX = cx + 3.4, TZ = cz - 3.2;
  function okPos(x, z, palmR, pathR) {
    if (Math.hypot(x, z) > R - 4) return false;
    if (inTown(x, z)) return false;
    if (nearPalm(x, z, palmR)) return false;
    if (pathD(x, z) < pathR) return false;
    if (Math.hypot(x - HX, z - HZ) < 3.6) return false;
    if (Math.hypot(x - cx, z - cz) < 2.8) return false;
    if (Math.hypot(x - TX, z - TZ) < 2.4) return false;
    return true;
  }
  var stoneM = new T.MeshStandardMaterial({ color: 0xffffff, map: stoneTex(), roughness: 0.95, flatShading: true });

  /* ---------- 2. JALAN SETAPAK ---------- */
  safe('path', function () {
    var sands = [], stones = [], d = new T.Object3D(), col = new T.Color();
    lines.forEach(function (L) {
      L.forEach(function (p, i) {
        if (nearPalm(p.x, p.z, 0.8)) return;
        sands.push([p.x, p.z]);
        if (i % 2 === 0) stones.push([p.x + rb(-0.35, 0.35), p.z + rb(-0.35, 0.35)]);
      });
    });
    var sm = new T.InstancedMesh(new T.CylinderGeometry(0.85, 0.95, 0.16, 14), new T.MeshStandardMaterial({ color: 0xffffff, roughness: 1 }), sands.length);
    sands.forEach(function (p, i) {
      var sc = rb(0.85, 1.15), v = rb(0, 0.1);
      d.position.set(p[0], gh(p[0], p[1]), p[1]); d.rotation.set(0, rr() * PI, 0); d.scale.set(sc, 1, sc * rb(0.85, 1.1)); d.updateMatrix();
      sm.setMatrixAt(i, d.matrix); col.setRGB(0.82 - v, 0.72 - v, 0.5 - v * 0.8); sm.setColorAt(i, col);
    });
    sm.receiveShadow = true; sm.frustumCulled = false; scene.add(sm);
    var st = new T.InstancedMesh(new T.CylinderGeometry(0.42, 0.5, 0.22, 7), stoneM, stones.length);
    stones.forEach(function (p, i) {
      var sc = rb(0.65, 1.0);
      d.position.set(p[0], gh(p[0], p[1]) + 0.03, p[1]); d.rotation.set(0, rr() * PI, 0); d.scale.set(sc * rb(0.9, 1.3), rb(0.8, 1.2), sc); d.updateMatrix();
      st.setMatrixAt(i, d.matrix); var g = rb(0.8, 1.1); col.setRGB(g, g * 0.98, g * 0.95); st.setColorAt(i, col);
    });
    st.castShadow = true; st.receiveShadow = true; st.frustumCulled = false; scene.add(st);
    /* papan PANTAI di ujung jalan */
    var e = P2[P2.length - 1], sg = new T.Group(); sg.position.set(e.x - 1.6, gh(e.x - 1.6, e.z), e.z + 0.4); scene.add(sg);
    mesh(sg, new T.CylinderGeometry(0.06, 0.07, 1.6, 8), MS(0x5a3a1e), 0, 0.8, 0);
    var spr = new T.Sprite(new T.SpriteMaterial({ map: C.makeSignTexture('PANTAI', '#1f7d72'), fog: false }));
    spr.scale.set(1.9, 0.48, 1); spr.position.set(0, 1.9, 0); sg.add(spr);
    [[-1.0, 0.9, 0.5], [0.9, 1.0, -1.6]].forEach(function (r) {
      var rk = new T.Mesh(new T.DodecahedronGeometry(r[2] * 0.5 + 0.2, 0), stoneM);
      rk.position.set(e.x + r[0], gh(e.x + r[0], e.z + r[1]) + 0.1, e.z + r[1]); rk.scale.set(1.2, 0.7, 1); rk.rotation.y = rr() * 3; rk.castShadow = true; scene.add(rk);
    });
  });

  /* ---------- 1. AREA API UNGGUN ---------- */
  var camp = new T.Group(); camp.position.set(cx, gh(cx, cz), cz); scene.add(camp);
  function lg(lx, lz) { return gh(cx + lx, cz + lz) - gh(cx, cz); }
  var lanterns = [];

  safe('fire', function () {
    var i, a, ring = new T.Group(); camp.add(ring);
    var ash = new T.Mesh(new T.CircleGeometry(0.62, 20).rotateX(-PI / 2), new T.MeshBasicMaterial({ color: 0x15100c }));
    ash.position.y = 0.08; camp.add(ash);
    for (i = 0; i < 10; i++) {
      a = i / 10 * PI * 2;
      var s = new T.Mesh(new T.DodecahedronGeometry(0.17, 0), stoneM); s.position.set(Math.cos(a) * 0.68, 0.1, Math.sin(a) * 0.68);
      s.scale.set(rb(1, 1.4), rb(0.7, 1), rb(1, 1.3)); s.rotation.set(rr() * 3, rr() * 3, rr() * 3); s.castShadow = true; s.receiveShadow = true; camp.add(s);
    }
    var logM = new T.MeshStandardMaterial({ color: 0x4a2e18, roughness: 0.95 }), up = new T.Vector3(0, 1, 0);
    for (i = 0; i < 5; i++) {
      a = i / 5 * PI * 2 + 0.3;
      var k = new T.Vector3(-Math.sin(a), 0, Math.cos(a)), phi = 1.05, dir = new T.Vector3(-Math.cos(a) * Math.sin(phi), Math.cos(phi), -Math.sin(a) * Math.sin(phi));
      var lgm = new T.Mesh(new T.CylinderGeometry(0.07, 0.08, 0.95, 8), logM);
      lgm.quaternion.setFromAxisAngle(k, phi);
      lgm.position.set(Math.cos(a) * 0.5 + dir.x * 0.475, 0.1 + dir.y * 0.475, Math.sin(a) * 0.5 + dir.z * 0.475);
      lgm.castShadow = true; camp.add(lgm);
    }
    /* tripod + kuali */
    var apex = new T.Vector3(0, 1.7, 0), metal = MS(0x23262a, 0.45, { metalness: 0.6 });
    [90, 210, 330].forEach(function (deg) {
      var b = new T.Vector3(Math.cos(deg * PI / 180) * 0.95, 0, Math.sin(deg * PI / 180) * 0.95), v = apex.clone().sub(b), L = v.length();
      var m = new T.Mesh(new T.CylinderGeometry(0.035, 0.045, L, 6), logM);
      m.quaternion.setFromUnitVectors(up, v.clone().normalize()); m.position.copy(b).addScaledVector(v, 0.5); m.castShadow = true; camp.add(m);
    });
    mesh(camp, new T.CylinderGeometry(0.012, 0.012, 0.55, 5), metal, 0, 1.425, 0);
    mesh(camp, new T.SphereGeometry(0.3, 18, 10, 0, PI * 2, PI / 2, PI / 2), metal, 0, 1.15, 0);
    var rim = mesh(camp, new T.TorusGeometry(0.3, 0.025, 6, 20), metal, 0, 1.15, 0); rim.rotation.x = PI / 2;
    /* nyala */
    var flames = [], embers, smokes = [], steams = [];
    for (i = 0; i < 6; i++) {
      var fm = new T.SpriteMaterial({ map: flameTex(), color: i < 2 ? 0xffffff : (i < 4 ? 0xffc070 : 0xff8a30), transparent: true, depthWrite: false, blending: T.AdditiveBlending, fog: false, toneMapped: false });
      var sp = new T.Sprite(fm); a = i / 6 * PI * 2; sp.center.set(0.5, 0.05);
      sp.userData = { x: Math.cos(a) * 0.16, z: Math.sin(a) * 0.16, ph: i * 1.7, s: 0.9 - 0.08 * (i % 3) };
      sp.position.set(sp.userData.x, 0.16, sp.userData.z); camp.add(sp); flames.push(sp);
    }
    var glow = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0xff8a30, transparent: true, depthWrite: false, blending: T.AdditiveBlending, fog: false, toneMapped: false }));
    glow.position.y = 0.7; glow.scale.set(3.2, 3.2, 1); camp.add(glow);
    var gdisc = new T.Mesh(new T.CircleGeometry(4.2, 32).rotateX(-PI / 2), new T.MeshBasicMaterial({ map: dotTex(), color: 0xff8a30, transparent: true, depthWrite: false, blending: T.AdditiveBlending, opacity: 0, toneMapped: false, fog: false }));
    gdisc.position.y = 0.14; camp.add(gdisc);
    var NE = 40, ep = new Float32Array(NE * 3), ec = new Float32Array(NE * 3), eg = new T.BufferGeometry();
    eg.setAttribute('position', new T.BufferAttribute(ep, 3)); eg.setAttribute('color', new T.BufferAttribute(ec, 3));
    embers = new T.Points(eg, new T.PointsMaterial({ size: 0.1, map: dotTex(), vertexColors: true, transparent: true, depthWrite: false, blending: T.AdditiveBlending, toneMapped: false, fog: false }));
    embers.frustumCulled = false; camp.add(embers);
    for (i = 0; i < 5; i++) { var sk = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0x9a9a9a, transparent: true, depthWrite: false, opacity: 0 })); camp.add(sk); smokes.push(sk); }
    for (i = 0; i < 2; i++) { var stm = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0xffffff, transparent: true, depthWrite: false, opacity: 0 })); camp.add(stm); steams.push(stm); }
    var fl = new T.PointLight(0xff9a45, 0.3, 17, 1.5); fl.position.set(0, 1.0, 0); camp.add(fl);
    ticks.push(function (t, n) {
      var i, j, u, a2, r2, f;
      for (i = 0; i < flames.length; i++) {
        f = flames[i]; var ud = f.userData, fk = 1 + 0.22 * Math.sin(t * 11 + ud.ph) + 0.12 * Math.sin(t * 23 + ud.ph * 2);
        f.scale.set(0.55 * ud.s * (1 + 0.12 * Math.sin(t * 9 + ud.ph)), 1.15 * ud.s * fk, 1);
        f.position.x = ud.x + Math.sin(t * 7 + ud.ph) * 0.04; f.position.z = ud.z + Math.cos(t * 6 + ud.ph) * 0.04;
      }
      var fk2 = 0.9 + 0.1 * Math.sin(t * 13) + 0.06 * Math.sin(t * 29);
      fl.intensity = (0.25 + 1.7 * n) * fk2;
      glow.material.opacity = 0.25 + 0.4 * n; glow.scale.setScalar(3.0 + 0.3 * Math.sin(t * 9) + 0.8 * n);
      gdisc.material.opacity = 0.12 + 0.45 * n;
      for (i = 0; i < NE; i++) {
        j = i * 3; u = (t * (0.25 + 0.15 * (i % 5) / 5) + i * 0.137) % 1; a2 = i * 2.4 + t * 0.7; r2 = (0.18 + u * 0.5) * (0.5 + 0.5 * Math.sin(i));
        ep[j] = Math.cos(a2) * r2; ep[j + 1] = 0.5 + u * 2.6; ep[j + 2] = Math.sin(a2) * r2;
        f = (1 - u) * 1.3; ec[j] = f; ec[j + 1] = 0.6 * f * (1 - u); ec[j + 2] = 0.15 * f * (1 - u);
      }
      eg.attributes.position.needsUpdate = true; eg.attributes.color.needsUpdate = true;
      for (i = 0; i < smokes.length; i++) {
        u = (t * 0.18 + i / smokes.length) % 1;
        smokes[i].position.set(Math.sin(t * 0.6 + i) * 0.2 + u * 0.8, 1.9 + u * 2.4, Math.cos(t * 0.5 + i) * 0.2);
        smokes[i].scale.setScalar(0.6 + u * 1.9); smokes[i].material.opacity = Math.sin(u * PI) * 0.2;
      }
      for (i = 0; i < steams.length; i++) {
        u = (t * 0.3 + i * 0.5) % 1;
        steams[i].position.set(Math.sin(t + i) * 0.05, 1.3 + u * 0.7, 0); steams[i].scale.setScalar(0.3 + u * 0.5); steams[i].material.opacity = Math.sin(u * PI) * 0.35;
      }
    });
  });

  /* bangku batu */
  safe('bench', function () {
    [[-2.4, 0.3], [2.4, 0.6], [0.3, -2.4]].forEach(function (p) {
      var g = new T.Group(), y = lg(p[0], p[1]);
      g.position.set(p[0], y, p[1]); g.rotation.y = Math.atan2(-p[0], -p[1]) + rb(-0.12, 0.12); camp.add(g);
      mesh(g, new T.BoxGeometry(1.7, 0.16, 0.55), stoneM, 0, 0.4, 0);
      [-0.6, 0.6].forEach(function (x) { mesh(g, new T.BoxGeometry(0.38, 0.4, 0.5), stoneM, x, 0.15, 0); });
      C.TOWN_COLLIDERS.push({ x: cx + p[0], z: cz + p[1], r: 0.95 });
    });
    C.TOWN_COLLIDERS.push({ x: cx, z: cz, r: 0.95 });
    /* tumpukan kayu bakar */
    var wg = new T.Group(); wg.position.set(-1.6, lg(-1.6, -3.0), -3.0); camp.add(wg);
    var lm = MS(0x6a4528, 0.95), r, c2;
    for (r = 0; r < 3; r++) for (c2 = 0; c2 < 3 - r; c2++) {
      var lgn = mesh(wg, new T.CylinderGeometry(0.1, 0.1, 1.0, 8), lm, (c2 - (2 - r) / 2) * 0.22, 0.1 + r * 0.19, 0); lgn.rotation.z = PI / 2;
    }
    C.TOWN_COLLIDERS.push({ x: cx - 1.6, z: cz - 3.0, r: 0.7 });
  });

  /* tenda */
  safe('tent', function () {
    var g = new T.Group(), lx = 3.4, lz = -3.2; g.position.set(lx, lg(lx, lz) - 0.04, lz); camp.add(g);
    g.rotation.y = Math.atan2(-lx, -lz);
    var fab = new T.MeshStandardMaterial({ map: tentTex(), roughness: 0.9, side: T.DoubleSide });
    var roof = gable(1.1, 1.35, 2.3, fab); g.add(roof);
    var back = triMesh(2.2, 1.35, fab); back.position.z = -1.15; g.add(back);
    var front = triMesh(2.2, 1.35, fab); front.position.z = 1.15; g.add(front);
    var door = triMesh(0.95, 1.0, new T.MeshBasicMaterial({ color: 0x120d09, side: T.DoubleSide })); door.position.set(0, 0, 1.16); g.add(door);
    var pole = MS(0x5a3a1e);
    mesh(g, new T.CylinderGeometry(0.03, 0.03, 1.4, 6), pole, 0, 0.7, 1.2);
    [[-1.25, 1.35], [1.25, 1.35], [-1.25, -1.35], [1.25, -1.35]].forEach(function (p) {
      var pg = mesh(g, new T.CylinderGeometry(0.025, 0.025, 0.3, 5), pole, p[0], 0.1, p[1]); pg.rotation.z = p[0] > 0 ? -0.5 : 0.5;
    });
    /* lentera di depan tenda */
    var lm = new T.MeshStandardMaterial({ color: 0xf5d28a, emissive: 0xffa733, emissiveIntensity: 0.1, roughness: 0.4 });
    mesh(g, new T.CylinderGeometry(0.03, 0.04, 0.9, 6), pole, 0.95, 0.45, 1.6);
    mesh(g, new T.BoxGeometry(0.16, 0.22, 0.16), lm, 0.95, 1.0, 1.6);
    var gl = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0xffb347, transparent: true, depthWrite: false, blending: T.AdditiveBlending, opacity: 0, fog: false, toneMapped: false }));
    gl.scale.set(1.3, 1.3, 1); gl.position.set(0.95, 1.0, 1.6); g.add(gl);
    lanterns.push({ m: lm, s: gl, k: 0.55 });
    C.TOWN_COLLIDERS.push({ x: cx + lx, z: cz + lz, r: 1.45 });
  });

  /* ---------- 3. RUMAH NELAYAN + NPC ---------- */
  var npcX = -4.1, npcZ = -3.6;
  safe('hut', function () {
    scene.children.forEach(function (o) {
      if (!o.isMesh || !o.geometry) return;
      var p = o.geometry.parameters || {};
      if (o.geometry.type === 'BoxGeometry' && p.width === 2.6 && p.height === 1.8 && p.depth === 2.2) o.visible = false;
      else if (o.geometry.type === 'ConeGeometry' && p.radius === 2.1 && p.height === 1.4 && p.radialSegments === 4) o.visible = false;
    });
    var B = 0.25, H = new T.Group(); H.position.set(HX, gh(HX, HZ), HZ); scene.add(H);
    var wallM = MS(0xffffff, 0.85, { map: woodTex('#a87a4a', 2, 1) }), wallE = MS(0xffffff, 0.85, { map: woodTex('#a87a4a', 0.9, 0.9), side: T.DoubleSide });
    var dkTex = woodTex('#8a5a30', 2, 2); dkTex.center.set(0.5, 0.5); dkTex.rotation = PI / 2;
    var deckM = MS(0xffffff, 0.85, { map: dkTex }), roofM = new T.MeshStandardMaterial({ map: thatchTex(4, 2), roughness: 1, side: T.DoubleSide });
    var trim = MS(0x4a2e18), dark = MS(0x2a1a10), brass = MS(0xd4a73a, 0.3, { metalness: 0.8 });
    function bx(w, h, d, m, x, y, z) { return mesh(H, new T.BoxGeometry(w, h, d), m, x, y, z); }
    bx(4.0, 0.5, 3.6, deckM, 0, 0, 0);
    bx(3.2, 1.8, 2.4, wallM, 0, B + 0.9, -0.3);
    [[-1.6, 0.9], [1.6, 0.9], [-1.6, -1.5], [1.6, -1.5]].forEach(function (p) { bx(0.14, 1.9, 0.14, trim, p[0], B + 0.95, p[1]); });
    var roof = gable(1.75, 1.1, 4.0, roofM); roof.rotation.y = PI / 2; roof.position.set(0, B + 1.8, -0.3); H.add(roof);
    [-1, 1].forEach(function (s) { bx(4.05, 0.09, 0.09, trim, 0, B + 1.8, -0.3 + s * 1.75); });
    var ridge = mesh(H, new T.CylinderGeometry(0.07, 0.07, 4.1, 8), trim, 0, B + 2.9, -0.3); ridge.rotation.z = PI / 2;
    [-1, 1].forEach(function (s) {
      var sh = new T.Shape(), w = 1.2, h1 = 1.1 * (1 - 1.2 / 1.75);
      sh.moveTo(-w, 0); sh.lineTo(w, 0); sh.lineTo(w, h1); sh.lineTo(0, 1.1); sh.lineTo(-w, h1); sh.closePath();
      var m = new T.Mesh(new T.ShapeGeometry(sh), wallE); m.rotation.y = s * PI / 2; m.position.set(s * 1.58, B + 1.8, -0.3); m.castShadow = true; H.add(m);
    });
    /* pintu */
    bx(0.85, 1.5, 0.07, dark, -0.75, B + 0.75, 0.94); bx(1.05, 0.1, 0.1, trim, -0.75, B + 1.55, 0.95);
    bx(0.1, 1.55, 0.1, trim, -1.25, B + 0.78, 0.95); bx(0.1, 1.55, 0.1, trim, -0.25, B + 0.78, 0.95);
    mesh(H, new T.SphereGeometry(0.045, 8, 6), brass, -0.45, B + 0.75, 1.0);
    /* jendela */
    var winM = new T.MeshStandardMaterial({ color: 0xf5d28a, emissive: 0xffa733, emissiveIntensity: 0.1, roughness: 0.3 });
    bx(1.05, 0.8, 0.08, trim, 0.8, B + 1.1, 0.94);
    mesh(H, new T.PlaneGeometry(0.86, 0.6), winM, 0.8, B + 1.1, 0.99, false);
    bx(0.88, 0.05, 0.03, trim, 0.8, B + 1.1, 1.0); bx(0.05, 0.62, 0.03, trim, 0.8, B + 1.1, 1.0);
    [-1, 1].forEach(function (s) { var sh2 = bx(0.42, 0.78, 0.05, wallM, 0.8 + s * 0.74, B + 1.1, 0.98); sh2.rotation.y = s * 0.5; });
    var wglow = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0xffb347, transparent: true, depthWrite: false, blending: T.AdditiveBlending, opacity: 0, fog: false, toneMapped: false }));
    wglow.scale.set(2.2, 2.2, 1); wglow.position.set(0.8, B + 1.1, 1.3); H.add(wglow);
    lanterns.push({ m: winM, s: wglow, k: 0.6 });
    /* tiang teras + lentera */
    [-1, 1].forEach(function (s) { mesh(H, new T.CylinderGeometry(0.07, 0.08, 1.8, 8), trim, s * 1.75, B + 0.9, 1.4); });
    var lm = new T.MeshStandardMaterial({ color: 0xf5d28a, emissive: 0xffa733, emissiveIntensity: 0.1, roughness: 0.4 });
    mesh(H, new T.BoxGeometry(0.16, 0.22, 0.16), lm, -1.75, B + 1.35, 1.58);
    var lgl = new T.Sprite(new T.SpriteMaterial({ map: dotTex(), color: 0xffb347, transparent: true, depthWrite: false, blending: T.AdditiveBlending, opacity: 0, fog: false, toneMapped: false }));
    lgl.scale.set(1.2, 1.2, 1); lgl.position.set(-1.75, B + 1.35, 1.58); H.add(lgl); lanterns.push({ m: lm, s: lgl, k: 0.5 });
    /* barel, peti, bangku teras */
    var barM = MS(0x8a5a2b);
    mesh(H, new T.CylinderGeometry(0.3, 0.3, 0.8, 12), barM, -1.45, B + 0.4, 1.35);
    [0.2, 0.6].forEach(function (y) { mesh(H, new T.CylinderGeometry(0.315, 0.315, 0.06, 12), dark, -1.45, B + y, 1.35); });
    bx(0.6, 0.6, 0.6, MS(0xa87a44), 1.45, B + 0.3, 1.38);
    bx(1.3, 0.08, 0.4, trim, 0.4, B + 0.4, 1.5); bx(0.08, 0.4, 0.34, trim, -0.2, B + 0.2, 1.5); bx(0.08, 0.4, 0.34, trim, 1.0, B + 0.2, 1.5);
    /* jaring di dinding kiri */
    var net = new T.Mesh(new T.PlaneGeometry(1.7, 1.2), new T.MeshBasicMaterial({ map: netTex(), transparent: true, alphaTest: 0.1, side: T.DoubleSide }));
    net.position.set(-1.62, B + 1.15, -0.2); net.rotation.y = -PI / 2; H.add(net);
    for (var fi = 0; fi < 5; fi++) mesh(H, new T.SphereGeometry(0.07, 8, 6), MS(0xe8632a, 0.5), -1.66, B + 1.78, -0.9 + fi * 0.35, false);
    /* rak ikan kering */
    var rk = new T.Group(); rk.position.set(-3.0, 0, 0.6); H.add(rk);
    [-0.8, 0.8].forEach(function (x) { mesh(rk, new T.CylinderGeometry(0.04, 0.05, 1.5, 6), trim, x, 0.75, 0); });
    var bar = mesh(rk, new T.CylinderGeometry(0.03, 0.03, 1.8, 6), trim, 0, 1.45, 0); bar.rotation.z = PI / 2;
    for (var k2 = 0; k2 < 5; k2++) {
      var fsh = mesh(rk, new T.SphereGeometry(1, 10, 8), MS(k2 % 2 ? 0xc9d3da : 0xd9a27a, 0.4, { metalness: 0.2 }), -0.65 + k2 * 0.33, 1.15, 0, false);
      fsh.scale.set(0.05, 0.2, 0.1);
    }
    /* papan nama */
    var sg = new T.Sprite(new T.SpriteMaterial({ map: C.makeSignTexture('RUMAH NELAYAN', '#6b4a28'), fog: false }));
    sg.scale.set(2.6, 0.65, 1); sg.position.set(0, B + 3.7, 1.2); H.add(sg);
    [[-7.5, -5.6, 1.45], [-6, -5.6, 1.45], [-4.5, -5.6, 1.45], [-7, -7.3, 1.2], [-5, -7.3, 1.2]].forEach(function (c) { C.TOWN_COLLIDERS.push({ x: c[0], z: c[1], r: c[2] }); });
    C.TOWN_COLLIDERS.push({ x: HX - 3.0, z: HZ + 0.6, r: 1.0 });
  });

  safe('npc', function () {
    var npc = new T.Group(); npc.position.set(npcX, gh(npcX, npcZ), npcZ); npc.rotation.y = 0.35; scene.add(npc);
    var skin = MS(0xd9a273, 0.55), skinD = MS(0xbf8a5c, 0.6), kebaya = MS(0x1f8f86, 0.75), kain = MS(0xffffff, 0.85, { map: batikTex() });
    var hair = MS(0x1c1410, 0.9), white = MS(0xffffff, 0.3), black = MS(0x1b1b1b, 0.3), gold = MS(0xd9b34a, 0.3, { metalness: 0.8 });
    var strawT = (function () { var c = cv(128, 128), g = c.getContext('2d'), i; g.fillStyle = '#e6cf8c'; g.fillRect(0, 0, 128, 128); for (i = 0; i < 128; i += 6) { g.fillStyle = (i / 6) % 2 ? 'rgba(160,120,50,.25)' : 'rgba(255,245,200,.2)'; g.fillRect(0, i, 128, 3); } return tex(c, 2, 2); })();
    var straw = MS(0xffffff, 0.9, { map: strawT }), red = MS(0xb02a2a, 0.6);
    function add(geo, m, x, y, z, par) { var o = new T.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = true; o.receiveShadow = true; (par || npc).add(o); return o; }
    add(new T.CylinderGeometry(0.27, 0.36, 0.92, 20), kain, 0, 0.5, 0);
    var torso = add(new T.CylinderGeometry(0.22, 0.27, 0.55, 18), kebaya, 0, 1.2, 0); torso.scale.z = 0.78;
    var belt = add(new T.CylinderGeometry(0.28, 0.28, 0.08, 18), gold, 0, 0.96, 0); belt.scale.z = 0.8;
    add(new T.CylinderGeometry(0.06, 0.07, 0.12, 10), skin, 0, 1.52, 0);
    var head = new T.Group(); head.position.y = 1.7; npc.add(head);
    var hs = add(new T.SphereGeometry(0.2, 22, 16), skin, 0, 0, 0, head); hs.scale.set(1, 1.08, 1);
    add(new T.SphereGeometry(0.205, 20, 14, 0, PI * 2, 0, PI * 0.62), hair, 0, 0.02, -0.03, head);
    add(new T.SphereGeometry(0.1, 12, 10), hair, 0, 0.1, -0.2, head);
    [-1, 1].forEach(function (s) {
      var ew = add(new T.SphereGeometry(0.04, 10, 8), white, s * 0.075, 0.03, 0.17, head); ew.scale.z = 0.5;
      add(new T.SphereGeometry(0.02, 8, 6), black, s * 0.075, 0.03, 0.2, head);
      var br = add(new T.BoxGeometry(0.08, 0.015, 0.02), hair, s * 0.075, 0.095, 0.185, head); br.rotation.z = s * 0.12;
      var ear = add(new T.SphereGeometry(0.04, 8, 6), skin, s * 0.2, 0, 0, head); ear.scale.set(0.5, 1, 0.8);
    });
    var nose = add(new T.SphereGeometry(0.034, 10, 8), skinD, 0, -0.02, 0.2, head); nose.scale.set(1, 1.1, 1);
    var smile = add(new T.TorusGeometry(0.05, 0.007, 6, 14, PI), red, 0, -0.08, 0.19, head); smile.rotation.z = PI;
    add(new T.ConeGeometry(0.5, 0.26, 28), straw, 0, 0.27, 0, head);
    var strap = add(new T.TorusGeometry(0.2, 0.01, 6, 20), red, 0, -0.02, 0, head); strap.rotation.x = PI / 2; strap.scale.set(1, 1, 1.1);
    function arm(sx) {
      var pv = new T.Group(); pv.position.set(sx, 1.4, 0); npc.add(pv);
      add(new T.SphereGeometry(0.085, 12, 10), kebaya, 0, 0, 0, pv);
      add(new T.CylinderGeometry(0.075, 0.07, 0.4, 12), kebaya, 0, -0.22, 0, pv);
      add(new T.CylinderGeometry(0.058, 0.05, 0.3, 12), skin, 0, -0.55, 0, pv);
      add(new T.SphereGeometry(0.06, 10, 8), skin, 0, -0.72, 0, pv);
      return pv;
    }
    var armR = arm(0.31), armL = arm(-0.31);
    /* bakul ikan */
    var bk = new T.Group(); bk.position.set(0.62, 0, 0.35); npc.add(bk);
    add(new T.CylinderGeometry(0.24, 0.18, 0.3, 14, 1, true), new T.MeshStandardMaterial({ color: 0xb08a4a, roughness: 1, side: T.DoubleSide }), 0, 0.15, 0, bk);
    add(new T.CircleGeometry(0.18, 14).rotateX(-PI / 2), MS(0x7a5a2a), 0, 0.03, 0, bk);
    [[-0.08, 0.3, 0.05, 0xc9d3da], [0.07, 0.28, -0.04, 0xe8632a], [0, 0.32, 0.1, 0x9fb8c4]].forEach(function (f, i) {
      var fo = add(new T.SphereGeometry(1, 10, 8), MS(f[3], 0.4, { metalness: 0.2 }), f[0], f[1], f[2], bk); fo.scale.set(0.06, 0.04, 0.17); fo.rotation.y = i * 1.1;
    });
    /* label nama */
    var tc = cv(256, 64), tg = tc.getContext('2d');
    tg.fillStyle = 'rgba(10,25,40,.72)'; tg.beginPath(); tg.moveTo(22, 6); tg.arcTo(252, 6, 252, 58, 18); tg.arcTo(252, 58, 4, 58, 18); tg.arcTo(4, 58, 4, 6, 18); tg.arcTo(4, 6, 252, 6, 18); tg.closePath(); tg.fill();
    tg.strokeStyle = 'rgba(255,255,255,.55)'; tg.lineWidth = 3; tg.stroke();
    tg.font = 'bold 30px sans-serif'; tg.textAlign = 'center'; tg.textBaseline = 'middle'; tg.fillStyle = '#fff'; tg.fillText('Mbok Sari', 128, 33);
    var tag = new T.Sprite(new T.SpriteMaterial({ map: new T.CanvasTexture(tc), transparent: true, depthWrite: false })); tag.scale.set(1.5, 0.375, 1); tag.position.y = 2.55; npc.add(tag);
    C.TOWN_COLLIDERS.push({ x: npcX, z: npcZ, r: 0.7 });
    var nlast = 0;
    ticks.push(function (t) {
      var p = C.player.position, dx = p.x - npcX, dz = p.z - npcZ, near = dx * dx + dz * dz < 64;
      var tgt = near ? Math.atan2(dx, dz) : 0.35, d = Math.atan2(Math.sin(tgt - npc.rotation.y), Math.cos(tgt - npc.rotation.y));
      npc.rotation.y += d * 0.08;
      var br2 = Math.sin(t * 2.0); torso.scale.y = 1 + br2 * 0.012; head.position.y = 1.7 + br2 * 0.008; head.rotation.z = Math.sin(t * 0.9) * 0.03;
      armR.rotation.z = near ? 2.55 + Math.sin(t * 7) * 0.28 : 0.09 + Math.sin(t * 1.4) * 0.03;
      armL.rotation.z = -0.09 - Math.sin(t * 1.4 + 1) * 0.03;
    });
  });

  /* dialog Mbok Sari */
  safe('dialog', function () {
    var TIPS = ['Lepas tombol pas marker di zona Perfect, hasil tangkapanmu lebih bagus.', 'Malam hari dan hujan bikin ikan langka lebih gampang nyangkut.', 'Ikan Rahasia harus ditarik manual, Auto Mancing nggak bisa.', 'Cek Pasar tiap hari, harga ikan berubah-ubah.', 'Enchant rod di Altar buat nambah Luck dan Speed.', 'Pantai belakang sepi, cocok buat mancing tenang.'];
    var tipI = Math.floor(Math.random() * TIPS.length);
    var ov = document.createElement('div'); ov.className = 'modalOverlay'; ov.id = 'modalNelayan';
    ov.innerHTML = '<div class="modalBox"><div class="modalHead"><h2>Rumah Nelayan</h2><button class="modalClose" id="nlX" type="button">\u2715</button></div><div class="modalBody" id="nlBody"></div><div class="modalFoot"><span id="nlFoot"></span><span></span></div></div>';
    document.body.appendChild(ov);
    function dstr(d) { return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }
    function questPill() {
      var l = document.querySelectorAll('#hudPills button');
      for (var i = 0; i < l.length; i++) if ((l[i].textContent || '').trim() === 'Misi') return l[i];
      return null;
    }
    function render() {
      var s = C.save, today = dstr(new Date()), got = s.nelDay === today, lv = s.level || 1, coins = 60 + 15 * lv, xp = 25 + 6 * lv, q = s.quests, qd = 0, qt = 4, qok = false, i;
      if (q && q.v === 2 && q.day === today && q.list) { qok = true; qt = q.list.length; for (i = 0; i < q.list.length; i++) if (q.list[i].done) qd++; }
      var h = '<div class="rowItem"><div class="rowInfo"><div class="rowName">Mbok Sari</div><div class="rowSub">' + TIPS[tipI % TIPS.length] + '</div></div><button class="rowBtn" type="button" data-nl="tip">Tips lain</button></div>';
      h += '<div class="rowItem"><div class="rowInfo"><div class="rowName">Bingkisan Harian</div><div class="rowSub">' + (got ? 'Sudah diambil. Balik lagi besok!' : 'Hari ini: +' + coins + ' koin dan +' + xp + ' XP') + '</div></div><button class="rowBtn' + (got ? ' owned' : '') + '" type="button" data-nl="gift"' + (got ? ' disabled' : '') + '>' + (got ? 'Diambil' : 'Ambil') + '</button></div>';
      h += '<div class="rowItem"><div class="rowInfo"><div class="rowName">Misi Harian</div><div class="rowSub">' + (qok ? qd + '/' + qt + ' selesai' : 'Misi baru menunggu') + '</div></div><button class="rowBtn" type="button" data-nl="quest">Lihat Misi</button></div>';
      document.getElementById('nlBody').innerHTML = h;
      document.getElementById('nlFoot').textContent = 'Koin: ' + s.coins;
    }
    ov.addEventListener('click', function (e) {
      var b = e.target.closest('[data-nl]'); if (!b || b.disabled) return; var a = b.getAttribute('data-nl'), s = C.save;
      if (a === 'tip') { tipI++; render(); }
      else if (a === 'gift') {
        var today = dstr(new Date()); if (s.nelDay === today) return;
        var lv = s.level || 1, coins = 60 + 15 * lv, xp = 25 + 6 * lv;
        s.nelDay = today; s.coins += coins; C.addXp(xp); C.persist(); C.refresh(); C.Sfx.sell(); C.toast('Bingkisan dari Mbok Sari: +' + coins + ' koin'); render();
      } else if (a === 'quest') { var p = questPill(); ov.classList.remove('show'); if (p) p.click(); }
    });
    document.getElementById('nlX').onclick = function () { ov.classList.remove('show'); };
    C.TOWN_SHOPS.push({ id: 'nelayan', name: 'MBOK SARI', label: 'Bicara dengan Mbok Sari', x: npcX, z: npcZ, action: function () { render(); ov.classList.add('show'); } });
  });

  /* lentera & jendela menyala malam hari */
  ticks.push(function (t, n) {
    for (var i = 0; i < lanterns.length; i++) {
      var l = lanterns[i]; l.m.emissiveIntensity = 0.1 + 1.5 * n; l.s.material.opacity = l.k * n * (0.9 + 0.1 * Math.sin(t * 7 + i));
    }
  });

  /* ---------- 5. FLORA ---------- */
  var grass = null, grassData = [];
  safe('flora', function () {
    var pal = [0xff5a7a, 0xffd84a, 0xffffff, 0xb56bff, 0xff8a3d, 0x6ab4ff], FL = [], tries = 0, p = 0, k, i, d = new T.Object3D(), col = new T.Color();
    while (p < 16 && tries < 500) {
      tries++;
      var an = rr() * PI * 2, rd = rb(5, 26), px = Math.cos(an) * rd, pz = Math.sin(an) * rd;
      if (!okPos(px, pz, 1.4, 1.2)) continue;
      p++; var main = pal[Math.floor(rr() * pal.length)];
      for (k = 0; k < 14; k++) {
        var a2 = rr() * PI * 2, r2 = Math.sqrt(rr()) * 2.2, fx = px + Math.cos(a2) * r2, fz = pz + Math.sin(a2) * r2;
        if (!okPos(fx, fz, 0.6, 0.9)) continue;
        FL.push([fx, fz, rr() < 0.7 ? main : pal[Math.floor(rr() * pal.length)], rb(0.8, 1.3)]);
      }
    }
    var n = FL.length;
    if (n) {
      var stem = new T.InstancedMesh(new T.CylinderGeometry(0.012, 0.016, 0.4, 5).translate(0, 0.2, 0), new T.MeshLambertMaterial({ color: 0x3f9a3a }), n);
      var head = new T.InstancedMesh(new T.IcosahedronGeometry(0.085, 0), new T.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6, flatShading: true }), n);
      var core = new T.InstancedMesh(new T.SphereGeometry(0.035, 6, 5), new T.MeshStandardMaterial({ color: 0xffd23a, emissive: 0x7a5a00, roughness: 0.5 }), n);
      for (i = 0; i < n; i++) {
        var f = FL[i], y = gh(f[0], f[1]), s = f[3];
        d.position.set(f[0], y, f[1]); d.rotation.set(rb(-0.15, 0.15), 0, rb(-0.15, 0.15)); d.scale.set(1, s, 1); d.updateMatrix(); stem.setMatrixAt(i, d.matrix);
        d.position.set(f[0], y + 0.4 * s, f[1]); d.rotation.set(0, rr() * 3, 0); d.scale.set(s, 0.65 * s, s); d.updateMatrix(); head.setMatrixAt(i, d.matrix); col.setHex(f[2]); head.setColorAt(i, col);
        d.position.set(f[0], y + 0.43 * s, f[1]); d.rotation.set(0, 0, 0); d.scale.set(1, 1, 1); d.updateMatrix(); core.setMatrixAt(i, d.matrix);
      }
      [stem, head, core].forEach(function (m) { m.frustumCulled = false; scene.add(m); });
    }
    /* semak */
    var bushes = [], bt = 0;
    while (bushes.length < 44 && bt < 700) {
      bt++; var bx, bz;
      if (bt % 2) {
        var L = (bt % 4 === 1) ? P1 : P2, ix = 1 + Math.floor(rr() * (L.length - 2)), a3 = L[ix], b3 = L[ix + 1] || L[ix - 1];
        var dx = b3.x - a3.x, dz = b3.z - a3.z, dl = Math.hypot(dx, dz) || 1, off = (rr() < 0.5 ? -1 : 1) * rb(1.7, 2.8);
        bx = a3.x + (-dz / dl) * off; bz = a3.z + (dx / dl) * off;
      } else { var an2 = rr() * PI * 2, rd2 = rb(4, 27); bx = Math.cos(an2) * rd2; bz = Math.sin(an2) * rd2; }
      if (okPos(bx, bz, 1.3, 1.4)) bushes.push([bx, bz]);
    }
    var bm = new T.InstancedMesh(new T.IcosahedronGeometry(0.55, 1), new T.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, flatShading: true }), bushes.length * 3), bi = 0, gr = [0x2f8a3a, 0x3d9a44, 0x287a34, 0x4aa84a];
    bushes.forEach(function (b) {
      var base = gr[Math.floor(rr() * gr.length)], y = gh(b[0], b[1]);
      [[0, 0, 1], [0.45, 0.15, 0.75], [-0.35, 0.3, 0.65]].forEach(function (o) {
        var sc = o[2] * rb(0.8, 1.1);
        d.position.set(b[0] + o[0], y + 0.3 * sc, b[1] + o[1]); d.rotation.set(rr() * 3, rr() * 3, rr() * 3); d.scale.set(sc, sc * 0.8, sc); d.updateMatrix();
        bm.setMatrixAt(bi, d.matrix); col.setHex(base); col.offsetHSL(0, 0, rb(-0.04, 0.05)); bm.setColorAt(bi, col); bi++;
      });
    });
    bm.castShadow = false; bm.receiveShadow = true; bm.frustumCulled = false; scene.add(bm);
    /* rumput tinggi (pinggir jalan setapak, api unggun, rumah) */
    var tufts = [];
    [P1, P2].forEach(function (L, li) {
      for (var j = 2; j < L.length - 2; j += 2) {
        var a4 = L[j], b4 = L[j + 1], dx2 = b4.x - a4.x, dz2 = b4.z - a4.z, dl2 = Math.hypot(dx2, dz2) || 1;
        [-1, 1].forEach(function (sd) {
          if (rr() > 0.75) return;
          var of2 = sd * rb(1.05, 1.9), tx = a4.x + (-dz2 / dl2) * of2, tz = a4.z + (dx2 / dl2) * of2;
          if (inTown(tx, tz) || nearPalm(tx, tz, 0.7) || Math.hypot(tx - HX, tz - HZ) < 3.4 || Math.hypot(tx - cx, tz - cz) < 2.5 || Math.hypot(tx, tz) > R - 3.5) return;
          tufts.push([tx, tz]);
        });
      }
    });
    for (i = 0; i < 14; i++) { var ag = i / 14 * PI * 2, tx2 = cx + Math.cos(ag) * rb(3.3, 4.2), tz2 = cz + Math.sin(ag) * rb(3.3, 4.2); if (!nearPalm(tx2, tz2, 0.7) && pathD(tx2, tz2) > 1.0 && Math.hypot(tx2 - TX, tz2 - TZ) > 2.4) tufts.push([tx2, tz2]); }
    for (i = 0; i < 12; i++) { var ah = i / 12 * PI * 2, hx2 = HX + Math.cos(ah) * rb(3.3, 4.0), hz2 = HZ + Math.sin(ah) * rb(3.3, 4.0); if (!nearPalm(hx2, hz2, 0.7) && pathD(hx2, hz2) > 1.0 && Math.hypot(hx2 - npcX, hz2 - npcZ) > 1.2) tufts.push([hx2, hz2]); }
    var bg = new T.ConeGeometry(0.075, 1, 4, 1).translate(0, 0.5, 0), pos = bg.attributes.position, cl = new Float32Array(pos.count * 3);
    for (i = 0; i < pos.count; i++) { var fy = pos.getY(i); cl[i * 3] = 0.22 + 0.45 * fy; cl[i * 3 + 1] = 0.38 + 0.5 * fy; cl[i * 3 + 2] = 0.1 + 0.12 * fy; }
    bg.setAttribute('color', new T.BufferAttribute(cl, 3));
    grass = new T.InstancedMesh(bg, new T.MeshLambertMaterial({ vertexColors: true, side: T.DoubleSide }), tufts.length * 3);
    var gi = 0;
    tufts.forEach(function (tf) {
      for (var b = 0; b < 3; b++) {
        var gx = tf[0] + rb(-0.14, 0.14), gz = tf[1] + rb(-0.14, 0.14);
        grassData.push({ x: gx, y: gh(gx, gz), z: gz, yaw: rr() * PI, h: rb(0.6, 1.15), w: rb(0.8, 1.3), ph: rr() * 6.28 });
        var v = rb(0.85, 1.15); col.setRGB(v, v, v); grass.setColorAt(gi, col); gi++;
      }
    });
    grass.frustumCulled = false; scene.add(grass);
    var gt = -1, gd = new T.Object3D();
    ticks.push(function (t) {
      if (t - gt < 0.04) return; gt = t;
      for (var j = 0; j < grassData.length; j++) {
        var g = grassData[j];
        gd.position.set(g.x, g.y, g.z);
        gd.rotation.set(Math.sin(t * 1.7 + g.ph + g.x * 0.4) * 0.12, g.yaw, Math.cos(t * 1.3 + g.ph + g.z * 0.4) * 0.12);
        gd.scale.set(g.w, g.h, g.w); gd.updateMatrix(); grass.setMatrixAt(j, gd.matrix);
      }
      grass.instanceMatrix.needsUpdate = true;
    });
  });

  /* ---------- 4. KUNANG-KUNANG & KUPU-KUPU ---------- */
  safe('fireflies', function () {
    var NF = 64, F = [], i, fp = new Float32Array(NF * 3), fc = new Float32Array(NF * 3), fg = new T.BufferGeometry();
    for (i = 0; i < NF; i++) {
      var hx, hz;
      if (i % 2) { var sp = P1[Math.floor(rr() * P1.length)]; hx = sp.x + rb(-3, 3); hz = sp.z + rb(-3, 3); }
      else { var an = rr() * PI * 2, rd = rb(4, 27); hx = Math.cos(an) * rd; hz = Math.sin(an) * rd; }
      if (inTown(hx, hz) || Math.hypot(hx, hz) > R - 3) { hx = rb(-8, 8); hz = rb(-14, 8); }
      F.push({ hx: hx, hz: hz, hy: gh(hx, hz) + rb(0.5, 1.8), sp: rb(0.6, 1.5), ph: rr() * 6.28 });
    }
    fg.setAttribute('position', new T.BufferAttribute(fp, 3)); fg.setAttribute('color', new T.BufferAttribute(fc, 3));
    var pts = new T.Points(fg, new T.PointsMaterial({ size: 0.16, map: dotTex(), vertexColors: true, transparent: true, depthWrite: false, blending: T.AdditiveBlending, toneMapped: false, fog: false }));
    pts.frustumCulled = false; pts.visible = false; scene.add(pts);
    ticks.push(function (t, n) {
      pts.visible = n > 0.05; if (!pts.visible) return;
      for (var i = 0; i < NF; i++) {
        var f = F[i], j = i * 3, tw = 0.5 + 0.5 * Math.sin(t * 3.2 * f.sp + f.ph * 3), w = tw * tw * n * 1.2;
        fp[j] = f.hx + Math.sin(t * 0.4 * f.sp + f.ph) * 2.0 + Math.sin(t * 1.1 + f.ph * 2) * 0.4;
        fp[j + 1] = f.hy + Math.sin(t * 0.9 * f.sp + f.ph * 1.3) * 0.4;
        fp[j + 2] = f.hz + Math.cos(t * 0.35 * f.sp + f.ph * 0.7) * 2.0;
        fc[j] = 0.8 * w; fc[j + 1] = w; fc[j + 2] = 0.35 * w;
      }
      fg.attributes.position.needsUpdate = true; fg.attributes.color.needsUpdate = true;
    });
  });

  safe('butterflies', function () {
    var BC = ['#ffa23a', '#ffe14a', '#ffffff', '#6ab4ff', '#ff7ab0'], mats = [];
    BC.forEach(function (c) {
      var cc = cv(64, 64), g = cc.getContext('2d');
      g.fillStyle = c; g.beginPath(); g.ellipse(32, 32, 28, 22, 0, 0, 7); g.fill();
      g.fillStyle = 'rgba(255,255,255,.55)'; g.beginPath(); g.arc(24, 28, 7, 0, 7); g.fill();
      g.strokeStyle = 'rgba(30,20,10,.85)'; g.lineWidth = 3; g.beginPath(); g.ellipse(32, 32, 28, 22, 0, 0, 7); g.stroke();
      mats.push(new T.MeshBasicMaterial({ map: new T.CanvasTexture(cc), transparent: true, alphaTest: 0.2, side: T.DoubleSide }));
    });
    var B = [], i, root = new T.Group(); scene.add(root);
    for (i = 0; i < 14; i++) {
      var an = rr() * PI * 2, rd = rb(5, 25), hx = Math.cos(an) * rd, hz = Math.sin(an) * rd;
      if (inTown(hx, hz)) { hx = rb(-6, 8); hz = rb(-14, 6); }
      var g = new T.Group(), wm = mats[i % mats.length];
      var body = new T.Mesh(new T.CylinderGeometry(0.012, 0.012, 0.12, 5), new T.MeshBasicMaterial({ color: 0x241a10 })); body.rotation.x = PI / 2; g.add(body);
      var pl = new T.Group(), pr = new T.Group(); g.add(pl); g.add(pr);
      var wl = new T.Mesh(new T.PlaneGeometry(0.2, 0.17).translate(-0.1, 0, 0), wm), wr = new T.Mesh(new T.PlaneGeometry(0.2, 0.17).translate(0.1, 0, 0), wm);
      wl.rotation.x = wr.rotation.x = -PI / 2; pl.add(wl); pr.add(wr);
      root.add(g); B.push({ g: g, pl: pl, pr: pr, hx: hx, hz: hz, hy: rb(0.6, 1.8), r1: rb(1.5, 4), r2: rb(1.5, 4), sp: rb(0.25, 0.5), ph: rr() * 6.28 });
    }
    function at(b, t) { var a = t * b.sp + b.ph, x = b.hx + Math.cos(a) * b.r1 + Math.sin(a * 2.3) * 0.6, z = b.hz + Math.sin(a * 1.3) * b.r2; return [x, gh(x, z) + b.hy + Math.sin(a * 3) * 0.25, z]; }
    ticks.push(function (t, n) {
      root.visible = n < 0.5; if (!root.visible) return;
      for (var i = 0; i < B.length; i++) {
        var b = B[i], p1 = at(b, t), p2 = at(b, t + 0.06), fl = 0.15 + 0.95 * (0.5 + 0.5 * Math.sin(t * 16 + b.ph));
        b.g.position.set(p1[0], p1[1], p1[2]); b.g.rotation.y = Math.atan2(p2[0] - p1[0], p2[2] - p1[2]);
        b.pl.rotation.z = fl; b.pr.rotation.z = -fl;
      }
    });
  });

  /* ---------- loop ---------- */
  C.hookAnim(function (t) {
    var n = night();
    for (var i = 0; i < ticks.length; i++) { try { ticks[i](t, n); } catch (e) { ticks[i] = function () {}; console.warn('PM-CAMP tick', e); } }
  });
})();
</script>
<!--PM-CAMP-END-->'''

rep('<!--PM-HD2-END-->', '<!--PM-HD2-END-->\n' + CAMP)

# versi
rep("var VER = 'v4.17', DATE = '4 Okt 2026', KEY = 'pm_seen_ver';",
    "var VER = 'v4.18', DATE = '4 Okt 2026', KEY = 'pm_seen_ver';")

# Info Update: hapus yang lama, ganti yang baru
ITEMS = [
    'Area api unggun di tengah pulau: api 3D HD dengan nyala, percikan, dan asap, plus kuali di tripod, 3 bangku batu, tenda bergaris, dan tumpukan kayu. Malam hari api menyala hangat dan menerangi sekitarnya.',
    'Jalan setapak batu dari plaza ke api unggun, Rumah Nelayan, sampai pantai belakang (ada papan PANTAI di ujung, bisa dipakai mancing).',
    'Gubuk jadi Rumah Nelayan 3D. Ada Mbok Sari yang kasih Bingkisan Harian (koin dan XP) dan jalan pintas ke menu Misi.',
    'Kunang-kunang muncul malam hari, kupu-kupu terbang siang hari.',
    'Bunga, semak, dan rumput tinggi yang bergoyang tersebar di pulau, terutama di pinggir jalan setapak.'
]
NEWLOG = 'var LOG = [\n    ["Update v4.18", [\n' + ',\n'.join('      "' + t + '"' for t in ITEMS) + '\n    ]]\n  ];'
s, n = re.subn(r'var LOG = \[.*?\n  \];(?=\s*var vb0)', lambda m: NEWLOG, s, count=1, flags=re.S)
if n != 1:
    print('GAGAL: blok LOG tidak ketemu'); sys.exit(1)

open(P, 'w', encoding='utf-8').write(s)

# CHANGELOG.md: isi lama dihapus, diganti yang baru
CL = os.path.join(os.path.dirname(os.path.abspath(P)), 'CHANGELOG.md')
open(CL, 'w', encoding='utf-8').write('# Update v4.18 (4 Okt 2026)\n\n' + '\n'.join('- ' + t for t in ITEMS) + '\n')
print('OK: v4.18 ter-patch -> ' + P + ' (backup: ' + P + '.bak418), ' + CL + ' ditimpa')
