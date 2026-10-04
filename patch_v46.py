#!/usr/bin/env python3
# patch v4.6 - Perahu 3D HD + gambar perahu di Toko Pak Karto
import re, sys, shutil
F = 'index.html'
s = open(F, encoding='utf-8').read()
if 'pmBuildBoat' in s:
    print('Sudah ke-patch, skip.'); sys.exit(0)
shutil.copy(F, F + '.bak-v45')

BOAT_JS = r"""
/* === BOAT MODELS v4.6 (builder murni THREE, tanpa asset) === */
function pmBuildBoat(id) {
  var T = THREE;
  function M(c, o) { o = o || {}; o.color = c; if (o.roughness === undefined) o.roughness = 0.65; return new T.MeshStandardMaterial(o); }
  var G = new T.Group();
  function add(geo, mat, x, y, z, p) { var m = new T.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; if (p) (p.add ? p : G).add(m); else G.add(m); return m; }
  function box(w, h, d, mat, x, y, z) { return add(new T.BoxGeometry(w, h, d), mat, x, y, z); }
  function cyl(r1, r2, h, mat, x, y, z, seg) { return add(new T.CylinderGeometry(r1, r2, h, seg || 10), mat, x, y, z); }
  function wid(t, o) { var u = t > 0.5 ? (t - 0.5) * 2 : (0.5 - t) * 2; var k = t > 0.5 ? 1 - Math.pow(u, o.bow) : 1 - o.sf * Math.pow(u, o.st); return Math.max(k, 0.03); }
  function rise(t, o) { var u = t > 0.5 ? (t - 0.5) * 2 : (0.5 - t) * 2; return (t > 0.5 ? o.rb : o.rs) * Math.pow(u, 3); }
  function hull(o, mat) {
    var N = 22, K = 12, pos = [], idx = [], i, k;
    for (i = 0; i <= N; i++) {
      var t = i / N, z = (t - 0.5) * o.L, w = o.W / 2 * wid(t, o), d = o.D * (0.3 + 0.7 * wid(t, o)), r = rise(t, o);
      for (k = 0; k <= K; k++) { var a = Math.PI * k / K; pos.push(Math.cos(a) * w, -Math.pow(Math.sin(a), 0.8) * d + r, z); }
    }
    for (i = 0; i < N; i++) for (k = 0; k < K; k++) { var a0 = i * (K + 1) + k, b0 = a0 + 1, c0 = a0 + K + 1, d0 = c0 + 1; idx.push(a0, c0, b0, b0, c0, d0); }
    var g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
    mat.side = T.DoubleSide; var m = new T.Mesh(g, mat); m.castShadow = true; G.add(m); return m;
  }
  function deck(o, mat, y, shrink) {
    var sh = new T.Shape(), i, N = 22, pts = [];
    for (i = 0; i <= N; i++) { var t = i / N; pts.push([wid(t, o) * o.W / 2 * shrink, -(t - 0.5) * o.L]); }
    sh.moveTo(pts[0][0], pts[0][1]); for (i = 1; i <= N; i++) sh.lineTo(pts[i][0], pts[i][1]);
    for (i = N; i >= 0; i--) sh.lineTo(-pts[i][0], pts[i][1]);
    mat.side = T.DoubleSide; var m = new T.Mesh(new T.ShapeGeometry(sh), mat); m.rotation.x = -Math.PI / 2; m.position.y = y; G.add(m); return m;
  }
  function rail(o, mat, y, r, shrink) {
    [-1, 1].forEach(function (s) {
      var p = [], i; for (i = 0; i <= 16; i++) { var t = i / 16; p.push(new T.Vector3(s * wid(t, o) * o.W / 2 * (shrink || 1), y + rise(t, o), (t - 0.5) * o.L)); }
      var m = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(p), 40, r, 6, false), mat); m.castShadow = true; G.add(m);
    });
  }
  function sail(w, h, mat, x, y, z, bulge) {
    var g = new T.PlaneGeometry(w, h, 8, 8), P = g.attributes.position, i;
    for (i = 0; i < P.count; i++) { var u = P.getX(i) / (w / 2); P.setZ(i, bulge * (1 - u * u) * (0.4 + 0.6 * (P.getY(i) / h + 0.5))); }
    g.computeVertexNormals(); mat.side = T.DoubleSide; var m = new T.Mesh(g, mat); m.position.set(x, y, z); m.castShadow = true; G.add(m); return m;
  }
  function tri(a, b, c, mat, x, y, z) {
    var sh = new T.Shape(); sh.moveTo(a[0], a[1]); sh.lineTo(b[0], b[1]); sh.lineTo(c[0], c[1]);
    mat.side = T.DoubleSide; var m = new T.Mesh(new T.ShapeGeometry(sh), mat); m.position.set(x, y, z); G.add(m); return m;
  }
  var wood = M(0x9a6a3a), woodD = M(0x5a3a1f), white = M(0xf4f1e8, { roughness: 0.45 }), dark = M(0x23201c, { roughness: 0.8 }),
      brass = M(0xd4a73a, { metalness: 0.8, roughness: 0.3 }), glass = M(0x9fd8f0, { emissive: 0x1b3a52, roughness: 0.08, metalness: 0.3, transparent: true, opacity: 0.75 }),
      lamp = M(0xffe08a, { emissive: 0xffc04a, emissiveIntensity: 1.2 }), o, i;

  if (id === 'sampan') {
    o = { L: 3.4, W: 1.15, D: 0.42, bow: 1.5, st: 1.6, sf: 0.85, rb: 0.22, rs: 0.14 };
    hull(o, M(0xe9dfc8)); rail(o, wood, 0, 0.035);
    box(0.95, 0.04, 2.5, woodD, 0, -0.27, 0);
    [-0.7, 0.35].forEach(function (z) { box(1.0, 0.06, 0.26, wood, 0, -0.06, z); });
    [-1, 1].forEach(function (s) { var oar = cyl(0.025, 0.025, 1.9, woodD, s * 0.95, 0.12, 0.1, 6); oar.rotation.z = s * 1.1; oar.rotation.y = 0.3; var bl = box(0.12, 0.32, 0.03, wood, s * 1.62, -0.28, 0.35); bl.rotation.z = s * 0.2; });
    cyl(0.03, 0.03, 0.55, woodD, 0, 0.25, 1.45, 6); add(new T.SphereGeometry(0.08, 10, 8), lamp, 0, 0.58, 1.45);
  } else if (id === 'jukung') {
    o = { L: 4.6, W: 0.85, D: 0.5, bow: 1.4, st: 1.4, sf: 0.9, rb: 0.45, rs: 0.38 };
    hull(o, M(0xb8793c)); rail(o, woodD, 0.02, 0.04);
    box(0.62, 0.04, 3.2, M(0xd9b27a), 0, -0.3, 0);
    [-1, 1].forEach(function (s) {
      [-0.9, 0.9].forEach(function (z) { var p = cyl(0.04, 0.04, 2.0, M(0xd8c98a), s * 1.0, 0.05, z, 6); p.rotation.z = Math.PI / 2; });
      var f = cyl(0.11, 0.11, 3.3, M(0xe8d9a8), s * 1.95, -0.14, 0, 10); f.rotation.x = Math.PI / 2;
      add(new T.SphereGeometry(0.11, 10, 8), M(0xe8d9a8), s * 1.95, -0.14, 1.65); add(new T.SphereGeometry(0.11, 10, 8), M(0xe8d9a8), s * 1.95, -0.14, -1.65);
    });
    cyl(0.045, 0.06, 3.0, M(0xd8c98a), 0, 1.2, 0.3, 8);
    tri([0, 0], [0, 2.3], [1.5, 0], M(0xf08a2a), 0.05, 0.1, 0.3).rotation.y = Math.PI / 2;
    cyl(0.035, 0.035, 1.5, M(0xd8c98a), 0, 0.2, -1.0, 6).rotation.x = 1.3;
  } else if (id === 'motor') {
    o = { L: 4.7, W: 1.75, D: 0.6, bow: 1.8, st: 2, sf: 0.28, rb: 0.3, rs: 0.0 };
    hull(o, M(0x2f7fd0, { roughness: 0.4 })); deck(o, M(0xe8e4d8), -0.02, 0.97); rail(o, white, 0.04, 0.045);
    box(1.2, 0.8, 1.35, white, 0, 0.4, -0.5); box(1.3, 0.07, 1.5, M(0x2f7fd0), 0, 0.84, -0.5);
    box(1.22, 0.3, 0.04, glass, 0, 0.55, 0.19); [-1, 1].forEach(function (s) { box(0.04, 0.3, 0.7, glass, s * 0.61, 0.55, -0.5); });
    box(1.3, 0.06, 0.45, woodD, 0, 0.08, 0.95).position.z = 1.0; box(1.2, 0.06, 0.4, woodD, 0, 0.08, -1.7);
    box(0.34, 0.55, 0.3, dark, 0, 0.1, -2.5); cyl(0.04, 0.04, 0.7, dark, 0, -0.25, -2.55, 8); box(0.05, 0.22, 0.2, dark, 0, -0.62, -2.55);
    add(new T.SphereGeometry(0.1, 10, 8), lamp, 0, 0.98, -0.2); cyl(0.02, 0.02, 0.5, dark, 0, 1.12, -0.2, 6);
    [-1, 1].forEach(function (s) { for (i = 0; i < 3; i++) add(new T.SphereGeometry(0.1, 8, 8), white, s * 0.89, 0.05, -1 + i * 1.1); });
  } else if (id === 'speed') {
    o = { L: 5.5, W: 1.95, D: 0.5, bow: 1.15, st: 2, sf: 0.25, rb: 0.38, rs: 0.0 };
    hull(o, M(0xe0392b, { roughness: 0.25, metalness: 0.15 })); deck(o, M(0xf2f2f2, { roughness: 0.35 }), 0.0, 0.98); rail(o, M(0xf2f2f2), 0.0, 0.05);
    box(0.28, 0.01, 4.4, M(0xe0392b), 0, 0.012, -0.1);
    var ws = box(1.5, 0.5, 0.05, glass, 0, 0.45, 0.55); ws.rotation.x = -0.55;
    box(1.4, 0.04, 0.04, dark, 0, 0.7, 0.4);
    [[0.45, -0.6], [-0.45, -0.6], [0.45, -1.7], [-0.45, -1.7]].forEach(function (p) { box(0.7, 0.32, 0.6, dark, p[0] > 0 ? 0.5 : -0.5, 0.17, p[1]); box(0.7, 0.4, 0.15, M(0x333a44), p[0] > 0 ? 0.5 : -0.5, 0.4, p[1] - 0.28); });
    box(0.5, 0.35, 0.3, dark, 0, 0.18, 0.15);
    [-0.5, 0.5].forEach(function (x) { box(0.3, 0.55, 0.32, dark, x, 0.08, -2.82); cyl(0.04, 0.04, 0.7, dark, x, -0.27, -2.86, 8); box(0.05, 0.22, 0.22, dark, x, -0.62, -2.86); });
    cyl(0.02, 0.02, 0.8, dark, 0, 0.4, -2.2, 6); tri([0, 0], [0, 0.3], [-0.55, 0.15], M(0xe0392b), 0, 0.8, -2.2);
  } else {
    o = { L: 6.6, W: 2.3, D: 0.95, bow: 1.7, st: 1.8, sf: 0.3, rb: 0.5, rs: 0.25 };
    hull(o, M(0x5a2e16, { roughness: 0.45 })); deck(o, M(0xc79a62), -0.02, 0.97);
    rail(o, brass, 0.0, 0.05); rail(o, brass, 0.4, 0.035, 0.98);
    for (i = 0; i <= 8; i++) { var tt = i / 8; [-1, 1].forEach(function (s) { if (tt > 0.08 && tt < 0.95) cyl(0.025, 0.025, 0.4, brass, s * wid(tt, o) * 1.12 * 0.98, 0.2 + rise(tt, o), (tt - 0.5) * o.L, 6); }); }
    var cab = box(1.7, 0.85, 1.8, M(0xf3ead2), 0, 0.42, -1.9); box(1.9, 0.1, 2.0, brass, 0, 0.9, -1.9); box(1.6, 0.1, 1.7, M(0x7a1f1f), 0, 1.0, -1.9);
    [-1, 1].forEach(function (s) { for (i = 0; i < 2; i++) box(0.04, 0.3, 0.45, glass, s * 0.86, 0.55, -2.3 + i * 0.8); }); box(1.2, 0.3, 0.04, glass, 0, 0.55, -1.0);
    var wm = M(0x7a4a24);
    cyl(0.07, 0.1, 4.6, wm, 0, 2.2, 1.15, 10); cyl(0.07, 0.1, 4.0, wm, 0, 1.95, -0.55, 10);
    var cr = M(0xfff7e0, { roughness: 0.9 });
    sail(1.9, 3.0, cr, 0, 2.4, 1.28, 0.35); sail(1.6, 2.6, cr, 0, 2.15, -0.42, 0.3); tri([0, 0], [0, 1.5], [1.8, 0], cr, 0, 0.55, 0.0).rotation.y = Math.PI / 2;
    box(0.08, 0.08, 1.7, wm, 0, 4.4, 1.15).rotation.y = Math.PI / 2; box(1.7, 0.06, 0.06, wm, 0, 3.78, -0.55);
    tri([0, 0], [0, 0.34], [0.8, 0.17], M(0xffd24a, { emissive: 0x6a4a00 }), 0, 4.55, 1.15).rotation.y = Math.PI / 2;
    var bs = cyl(0.05, 0.08, 1.8, wm, 0, 0.5, 3.9, 8); bs.rotation.x = Math.PI / 2 - 0.2;
    add(new T.SphereGeometry(0.17, 12, 10), brass, 0, 0.6, 3.1 + 0.1);
    [-1, 1].forEach(function (s) { add(new T.SphereGeometry(0.1, 10, 8), lamp, s * 0.85, 1.15, -2.7); cyl(0.02, 0.02, 0.5, brass, s * 0.85, 0.95, -2.7, 6); });
    box(1.0, 0.06, 0.6, M(0x7a1f1f), 0, 0.08, 0.2);
  }
  G.userData.pmBoat = 1;
  return G;
}

"""

THUMB_JS = r"""
  var BOAT_Y = { sampan: 0.12, jukung: 0.15, motor: 0.25, speed: 0.25, royal: 0.25 };
  var boatModels = {}, thumbs = {}, thumbsDone = false;
  function ensureThumbs() {
    if (thumbsDone) return; thumbsDone = true;
    try {
      var W = 320, H = 190, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
      var r = new THREE.WebGLRenderer({ canvas: cv, antialias: true, alpha: true, preserveDrawingBuffer: true });
      r.setPixelRatio(1); r.setSize(W, H, false); r.setClearColor(0x000000, 0);
      if ('outputEncoding' in r && THREE.sRGBEncoding) r.outputEncoding = THREE.sRGBEncoding;
      var sc = new THREE.Scene(); sc.add(new THREE.HemisphereLight(0xe6f4ff, 0x3b4650, 0.95));
      var dl = new THREE.DirectionalLight(0xfff0d0, 1.2); dl.position.set(5, 8, 6); sc.add(dl);
      var cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 200);
      BOATS.forEach(function (b) {
        var m = pmBuildBoat(b.id); m.rotation.y = -0.75; sc.add(m); m.updateMatrixWorld(true);
        var bb = new THREE.Box3().setFromObject(m), c = bb.getCenter(new THREE.Vector3()), rad = bb.getBoundingSphere(new THREE.Sphere()).radius;
        var dist = rad * 0.92 / Math.tan(Math.PI / 12), dir = new THREE.Vector3(0.35, 0.38, 0.86).normalize();
        cam.position.copy(c).addScaledVector(dir, dist); cam.lookAt(c);
        r.render(sc, cam); thumbs[b.id] = cv.toDataURL('image/png');
        sc.remove(m); m.traverse(function (o) { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
      });
      r.dispose(); if (r.forceContextLoss) r.forceContextLoss();
    } catch (e) { console.warn('thumb perahu gagal', e); }
  }
  function applyLook(b) {
    boat.scale.set(1, 1, 1);
    if (!boatModels[b.id]) { var m = pmBuildBoat(b.id); m.position.y = BOAT_Y[b.id] || 0.2; boatModels[b.id] = m; boat.add(m); }
    boat.children.forEach(function (c) { c.visible = false; });
    boatModels[b.id].visible = true;
  }
"""

# 1. builder + thumbs sebelum blok PERAHU
anchor = "  /* ===== PERAHU (v4.5"
assert anchor in s, 'anchor PERAHU tidak ketemu'
s = s.replace(anchor, BOAT_JS + "\n" + anchor, 1)

# 2. ganti applyLook lama
old = re.search(r"  function applyLook\(b\) \{.*?\n  \}\n", s, re.S)
assert old and 'children[0]' in old.group(0), 'applyLook lama tidak ketemu'
s = s.replace(old.group(0), THUMB_JS, 1)

# 3. toko: buat thumbnail + tampilkan gambar perahu
o2 = "  function renderBoatShop() {\n    var s = bsave();"
assert o2 in s, 'renderBoatShop tidak ketemu'
s = s.replace(o2, o2 + "\n    ensureThumbs();", 1)
sw = re.search(r"'<div style=\"width:14px;height:34px;border-radius:4px;background:#' \+ \('000000' \+ b\.color\.toString\(16\)\)\.slice\(-6\) \+ '\"></div>' \+", s)
assert sw, 'kotak warna perahu tidak ketemu'
new_img = ("(thumbs[b.id] ? '<img src=\"' + thumbs[b.id] + '\" alt=\"' + b.name + '\" style=\"width:96px;height:57px;flex-shrink:0;object-fit:contain;border-radius:10px;"
           "background:linear-gradient(180deg,#2f86a8,#123b52);box-shadow:0 3px 8px rgba(0,0,0,.35)\">' "
           ": '<div style=\"width:14px;height:34px;border-radius:4px;background:#' + ('000000' + b.color.toString(16)).slice(-6) + '\"></div>') +")
s = s.replace(sw.group(0), new_img, 1)

# 4. versi + info update
assert "var VER = 'v4.5', DATE = '4 Okt 2026'" in s
s = s.replace("var VER = 'v4.5', DATE = '4 Okt 2026'", "var VER = 'v4.6', DATE = '4 Okt 2026'", 1)
lg = re.search(r'\["Update v4\.5", \[.*?\n    \]\]', s, re.S)
assert lg, 'LOG v4.5 tidak ketemu'
s = s.replace(lg.group(0), '''["Update v4.6", [
      "Semua perahu sekarang model 3D HD: Sampan, Jukung bercadik, Perahu Motor, Speedboat, dan Kapal Layar Mewah punya bentuk lambung sendiri.",
      "Gambar perahu di Toko Pak Karto sekarang render 3D asli, bukan kotak warna lagi.",
      "Detail baru: dayung, cadik dan layar jukung, mesin tempel, kaca depan, tiang layar, lampu, dan pagar kuningan."
    ]]''', 1)
open(F, 'w', encoding='utf-8').write(s)

# 5. CHANGELOG
try:
    c = open('CHANGELOG.md', encoding='utf-8').read()
    entry = """## 2026-10-04 (v4.6)

- Semua perahu dibuat model 3D HD dengan bentuk lambung, dek, dan detail masing-masing (dayung, cadik, layar, mesin tempel, tiang, lampu, pagar).
- Gambar perahu di Toko Pak Karto diganti render 3D asli (dibuat otomatis saat toko dibuka).
- Info Update lama diganti dengan yang baru, versi naik ke v4.6.

"""
    k = c.find('## 2026-10-04 (v4.5)')
    if k >= 0:
        open('CHANGELOG.md', 'w', encoding='utf-8').write(c[:k] + entry + c[k:])
except Exception as e:
    print('CHANGELOG dilewati:', e)
print('Patch v4.6 selesai. Backup: index.html.bak-v45')
