import re, sys

P = sys.argv[1] if len(sys.argv) > 1 else '/root/BlockWorld/index.html'
s = open(P, encoding='utf-8').read()
if 'PM_PIERS_V417' in s:
    print('Sudah ke-patch, skip.')
    sys.exit(0)
open(P + '.bak417', 'w', encoding='utf-8').write(s)

def rep(old, new):
    global s
    n = s.count(old)
    if n != 1:
        print('GAGAL: anchor ketemu ' + str(n) + 'x -> ' + old[:70])
        sys.exit(1)
    s = s.replace(old, new)

# 1) area jalan dermaga (utama + platform + 2 dermaga samping)
rep('function onPierWalk(x, z) { return x >= -1.95 && x <= 1.95 && z >= 27 && z <= PIER.z1 - 0.4; }',
r'''/* PM_PIERS_V417 */
  const PIER_ARM = 11.5;
  function onPierWalk(x, z) {
    if (x >= -1.95 && x <= 1.95 && z >= 27 && z <= PIER.z1 - 0.4) return true;
    if (x >= -5.2 && x <= 5.2 && z >= 46.2 && z <= 50.4) return true;
    for (let i = -1; i <= 1; i += 2) {
      const cx = i * PIER_ARM;
      if (x >= cx - 1.95 && x <= cx + 1.95 && z >= 27 && z <= 42.6) return true;
      if (x >= cx - 3.7 && x <= cx + 3.7 && z >= 38.8 && z <= 42.6) return true;
    }
    return false;
  }''')

# 2) bangun model dermaga baru (setelah lampu dermaga utama)
BUILD = r'''[30.5, 35, 39.5, 44].forEach(z => { addLamp(-2.1, z); addLamp(2.1, z); });
  (function () {
    const DK = DECK_Y;
    function bx(w, h, d, x, y, z, mat) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat || postMat);
      m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; town.add(m); return m;
    }
    function deck(cx, cz, w, d) {
      bx(w, 0.3, d, cx, DK - 0.15, cz, new THREE.MeshLambertMaterial({ map: makePlankTexture(w / 4, d / 4) }));
    }
    function piles(cx, cz, w, d) {
      for (let x = cx - w / 2 + 0.4; x <= cx + w / 2 - 0.3; x += 3.6)
        for (let z = cz - d / 2 + 0.5; z <= cz + d / 2 - 0.3; z += 3) {
          const p = new THREE.Mesh(postGeo, postMat); p.position.set(x, -0.95, z); town.add(p);
        }
    }
    function rail(x0, z0, x1, z1) {
      const len = Math.hypot(x1 - x0, z1 - z0), n = Math.max(1, Math.round(len / 2));
      for (let i = 0; i <= n; i++) {
        const k = i / n, p = new THREE.Mesh(railPostGeo, postMat);
        p.position.set(x0 + (x1 - x0) * k, DK + 0.47, z0 + (z1 - z0) * k); town.add(p);
      }
      bx(Math.abs(x1 - x0) + 0.1, 0.08, Math.abs(z1 - z0) + 0.1, (x0 + x1) / 2, DK + 0.9, (z0 + z1) / 2);
    }
    function bench(cx, z, w) {
      bx(w, 0.1, 0.5, cx, DK + 0.5, z);
      [-1, 1].forEach(function (s) { bx(0.1, 0.5, 0.45, cx + s * (w / 2 - 0.2), DK + 0.25, z); });
      TOWN_COLLIDERS.push({ x: cx, z: z, r: w / 2 });
    }
    function sign(cx, z, text, bg) {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: makeSignTexture(text, bg), fog: false }));
      sp.scale.set(2.4, 0.6, 1); sp.position.set(cx, DK + 3.2, z); town.add(sp);
    }

    /* dua dermaga samping (bentuk T) */
    [-1, 1].forEach(function (sd) {
      const cx = sd * PIER_ARM;
      deck(cx, 35.75, 4.4, 14.5); deck(cx, 40.9, 8, 4.2);
      piles(cx, 35.75, 4.4, 14.5); piles(cx, 40.9, 8, 4.2);
      rail(cx - 2.1, 28.7, cx - 2.1, 38.8); rail(cx + 2.1, 28.7, cx + 2.1, 38.8);
      rail(cx - 4, 38.8, cx - 2.1, 38.8); rail(cx + 2.1, 38.8, cx + 4, 38.8);
      rail(cx - 4, 38.8, cx - 4, 43); rail(cx + 4, 38.8, cx + 4, 43); rail(cx - 4, 43, cx + 4, 43);
      [31.5, 35.5].forEach(function (z) { addLamp(cx - 2.1, z); addLamp(cx + 2.1, z); });
      addLamp(cx - 3.55, 42.3); addLamp(cx + 3.55, 42.3);
      bench(cx, 42.2, 2.2);
      sign(cx, 29.3, sd < 0 ? 'SPOT KIRI' : 'SPOT KANAN', sd < 0 ? '#1f6f8f' : '#1f7d72');
    });

    /* platform lebar di ujung dermaga utama */
    deck(0, 48.6, 11, 4.2); piles(0, 48.6, 11, 4.2);
    rail(-5.5, 46.5, -2.1, 46.5); rail(2.1, 46.5, 5.5, 46.5);
    rail(-5.5, 46.5, -5.5, 50.7); rail(5.5, 46.5, 5.5, 50.7); rail(-5.5, 50.7, 5.5, 50.7);
    addLamp(-5, 47.2); addLamp(5, 47.2); addLamp(-5, 50.1); addLamp(5, 50.1);
    bench(-3.4, 50.1, 2.2); bench(3.4, 50.1, 2.2);
    sign(0, 46.9, 'UJUNG DERMAGA', '#9c2f2a');
  })();'''
rep("[30.5, 35, 39.5, 44].forEach(z => { addLamp(-2.1, z); addLamp(2.1, z); });", BUILD)

# 3) perahu (saat berlayar) nggak tembus dermaga baru
rep('!(Math.abs(x) < 2.7 && z > 27);',
    '!(Math.abs(x) < 2.7 && z > 27) && !(Math.abs(Math.abs(x) - 11.5) < 2.3 && z > 27 && z < 43.6) && !(Math.abs(Math.abs(x) - 11.5) < 4.2 && z > 38.5 && z < 43.6) && !(Math.abs(x) < 6 && z > 46 && z < 51.2);')

# 4) versi + Info Update
rep("var VER = 'v4.16', DATE = '4 Okt 2026', KEY = 'pm_seen_ver';",
    "var VER = 'v4.17', DATE = '4 Okt 2026', KEY = 'pm_seen_ver';")
NEWLOG = ('var LOG = [\n    ["Update v4.17", [\n'
          '      "Dermaga ditambah: 2 dermaga samping (kiri dan kanan dermaga utama), bentuk T dengan platform di ujung.",\n'
          '      "Dermaga utama dapat platform lebar di ujung, lengkap dengan bangku, pagar, dan lampu.",\n'
          '      "Semua dermaga baru bisa dipakai mancing. Perahu tidak tembus dermaga lagi."\n'
          '    ]],\n    ["Update v4.16"')
s, n = re.subn(r'var LOG = \[\s*\["Update v4\.16"', lambda m: NEWLOG, s, count=1)
if n != 1:
    print('GAGAL: blok LOG tidak ketemu'); sys.exit(1)

open(P, 'w', encoding='utf-8').write(s)
print('OK: v4.17 ter-patch -> ' + P + ' (backup: ' + P + '.bak417)')
