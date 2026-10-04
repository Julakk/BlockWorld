#!/usr/bin/env python3
# patch v4.8 - hapus tombol Grafis HD dari Menu (HD selalu aktif) + karakter duduk / mendayung di perahu
import re, sys, shutil
F = 'index.html'
s = open(F, encoding='utf-8').read()
if 'pmBoatSeat' in s:
    print('Sudah ke-patch, skip.'); sys.exit(0)
shutil.copy(F, F + '.bak-v47')

def sub1(pat, new, label, flags=re.S):
    global s
    ms = re.findall(pat, s, flags)
    assert len(ms) == 1, 'TIDAK KETEMU / ganda: ' + label
    m = re.search(pat, s, flags)
    s = s[:m.start()] + new + s[m.end():]

def rep1(old, new, label):
    global s
    assert s.count(old) == 1, 'TIDAK KETEMU / ganda: ' + label
    s = s.replace(old, new, 1)

# 1. Grafis HD: tombol dihapus dari Menu, HD selalu aktif
rep1("    let hd = true;\n    try { hd = localStorage.getItem('pm_hd') !== '0'; } catch (e) {}\n",
     "    let hd = true; // v4.8: tombol Grafis dihapus, HD selalu aktif\n", 'PMHD hd awal')
rep1("    const pills = document.getElementById('hudPills');\n    if (pills) pills.appendChild(btn);\n", "", 'PMHD tombol')
rep1("            try { localStorage.setItem('pm_hd', '0'); } catch (e) {}\n            showToast('FPS drop, grafis diturunin ke Normal (bisa balik lewat tombol Grafis)');\n",
     "            showToast('FPS drop, grafis diturunin otomatis biar tetap lancar');\n", 'PMHD fps fallback')

# 2. model perahu: bangku sampan lebih rendah, dayung bisa gerak, titik duduk tiap perahu
rep1("    [-0.7, 0.35].forEach(function (z) { box(1.0, 0.06, 0.26, wood, 0, -0.06, z); });\n",
     "    [-0.7, 0.35].forEach(function (z) { box(1.0, 0.06, 0.26, wood, 0, -0.17, z); });\n", 'bangku sampan')
sub1(r"    \[-1, 1\]\.forEach\(function \(s\) \{ var oar = cyl\(0\.025, 0\.025, 1\.9[^\n]*\n", """    G.userData.oars = [];
    [-1, 1].forEach(function (s) {
      cyl(0.018, 0.018, 0.16, brass, s * 0.46, 0.04, 0.6, 6);
      var pv = new T.Group(); pv.position.set(s * 0.46, 0.1, 0.6); G.add(pv);
      var sh = new T.Group(); sh.rotation.z = -s * 0.2; pv.add(sh);
      var oar = new T.Mesh(new T.CylinderGeometry(0.022, 0.022, 1.75, 8), woodD); oar.rotation.z = Math.PI / 2; oar.position.x = s * 0.5; oar.castShadow = true; sh.add(oar);
      var bl = new T.Mesh(new T.BoxGeometry(0.46, 0.015, 0.17), wood); bl.position.x = s * 1.15; bl.castShadow = true; sh.add(bl);
      var grip = new T.Object3D(); grip.position.set(-s * 0.3, 0, 0); sh.add(grip);
      G.userData.oars.push({ pv: pv, sh: sh, grip: grip, s: s });
    });
""", 'dayung sampan')
rep1("  G.userData.pmBoat = 1;\n", """  /* titik duduk pemain: [z di model, tinggi permukaan duduk] */
  if (id === 'jukung') box(0.6, 0.05, 0.3, wood, 0, -0.2, 0);
  if (id === 'speed') box(0.9, 0.08, 0.4, dark, 0, 0.29, -1.15);
  var SEATS = { sampan: [0.35, -0.14], jukung: [0.0, -0.175], motor: [1.0, 0.11], speed: [-1.15, 0.33], royal: [0.2, 0.11] };
  G.userData.seat = SEATS[id] || SEATS.sampan;
  G.userData.pmBoat = 1;
""", 'titik duduk')

# 3. modul duduk + dayung
SEAT_JS = r"""
(function () {
  var C = window.__PMC; if (!C || !C.player || !C.boatMesh || !C.hookAnim || !window.THREE) return;
  var T = THREE, P = C.player, boat = C.boatMesh, rod = C.rodMesh;
  var THIGH = 0.1, HIP = 0.62;
  var arms = {}, legs = {}, els = {};
  P.children.slice().forEach(function (m) {
    var p = m.geometry && m.geometry.parameters; if (!m.isMesh || !p) return;
    if (p.radiusTop === 0.08 && p.radiusBottom === 0.07 && m.position.y > 1.1) arms[m.position.x < 0 ? 'L' : 'R'] = m;
    if (p.radiusTop === 0.105) legs[m.position.x < 0 ? 'L' : 'R'] = m;
  });
  if (!arms.L || !arms.R || !legs.L || !legs.R) { console.warn('Duduk di perahu: bagian karakter tidak ketemu'); return; }
  ['L', 'R'].forEach(function (k) { els[k] = arms[k].children.filter(function (c) { return c.isGroup; })[0]; });
  if (!els.L || !els.R) { console.warn('Duduk di perahu: siku tidak ketemu'); return; }

  var V = T.Vector3, Q = T.Quaternion, DOWN = new V(0, -1, 0);
  var tmp = new V(), pv = new V(), up = new V(), ep = new V(), lo = new V(), qa = new Q(), qe = new Q(), qi = new Q(), gp = new V(), tg = new V();
  function ik(arm, el, target, side, wt) {
    var s = arm.position, d = tmp.copy(target).sub(s), len = d.length() || 1e-3, a = 0.27, b = 0.29;
    var D = Math.min(len, a + b - 0.004); d.multiplyScalar(1 / len);
    var cA = Math.max(-1, Math.min(1, (a * a + D * D - b * b) / (2 * a * D))), sA = Math.sqrt(1 - cA * cA);
    pv.set(side * 0.5, -0.6, -0.6); pv.addScaledVector(d, -pv.dot(d));
    if (pv.lengthSq() < 1e-6) pv.set(side, 0, 0); pv.normalize();
    up.copy(d).multiplyScalar(cA).addScaledVector(pv, sA);
    qa.setFromUnitVectors(DOWN, up);
    ep.copy(up).multiplyScalar(a).add(s);
    lo.copy(target).sub(ep).normalize().applyQuaternion(qi.copy(qa).invert());
    qe.setFromUnitVectors(DOWN, lo);
    arm.quaternion.slerp(qa, wt); el.quaternion.slerp(qe, wt);
  }

  var sw = 0, rw = 0, rowT = 0, last = 0, lx = 0, lz = 0, seat = [0.35, -0.14], oars = null, mdl = null, rodHid = false;
  C.hookAnim(function (t) {
    var dt = Math.min(0.1, Math.max(0.001, t - last)); last = t;
    var sail = boat.visible;
    if (sail) {
      var found = null;
      boat.children.forEach(function (c) { if (c.visible && c.userData && c.userData.pmBoat) found = c; });
      if (found) { mdl = found; seat = found.userData.seat || seat; oars = found.userData.oars || null; found.position.x = 0; found.position.z = -seat[0]; }
    }
    sw += ((sail ? 1 : 0) - sw) * Math.min(1, dt * 7);
    var dx = P.position.x - lx, dz = P.position.z - lz; lx = P.position.x; lz = P.position.z;
    if (!sail && sw < 0.004) { sw = 0; rw = 0; if (rodHid) { rod.visible = true; rodHid = false; } return; }

    var spd = Math.min(12, Math.sqrt(dx * dx + dz * dz) / dt), moving = sail && spd > 0.4, fishing = C.fishState !== 'idle';
    rw += ((moving && !fishing ? 1 : 0) - rw) * Math.min(1, dt * 8);
    if (moving) rowT += dt * (3.2 + spd * 0.45);

    // duduk di bangku, menghadap sesuai arah perahu
    var targetY = boat.position.y + (mdl ? mdl.position.y : 0.12) + seat[1] + THIGH - HIP;
    P.position.y += (targetY - P.position.y) * sw;
    var dr = boat.rotation.y - P.rotation.y; dr = Math.atan2(Math.sin(dr), Math.cos(dr)); P.rotation.y += dr * sw;
    legs.L.rotation.x += (-1.2 - legs.L.rotation.x) * sw; legs.R.rotation.x += (-1.2 - legs.R.rotation.x) * sw;
    legs.L.rotation.z += (-0.1 - legs.L.rotation.z) * sw; legs.R.rotation.z += (0.1 - legs.R.rotation.z) * sw;

    // joran disimpan waktu berlayar
    var hide = rw > 0.5; if (hide !== rodHid) { rod.visible = !hide; rodHid = hide; }

    P.updateWorldMatrix(true, false);
    if (oars) {
      oars.forEach(function (o) {
        var a = 0.6 * Math.cos(rowT) * rw - 0.1 * (1 - rw);
        var rec = rw * Math.max(0, -Math.sin(rowT)) + (1 - rw);
        o.pv.rotation.y = -o.s * a;
        o.sh.rotation.z = -o.s * (0.2 - 0.24 * rec);
      });
      if (rw * sw > 0.01) {
        oars.forEach(function (o) {
          o.grip.getWorldPosition(gp); P.worldToLocal(gp);
          var k = o.s > 0 ? 'R' : 'L';
          ik(arms[k], els[k], gp, o.s, rw * sw);
        });
      }
    } else if (rw * sw > 0.01) {
      // perahu tanpa dayung: tangan di depan, kayak pegang kemudi
      var sway = 0.03 * Math.sin(t * 0.9);
      ik(arms.R, els.R, tg.set(0.2, 0.9, 0.42 + sway), 1, rw * sw);
      ik(arms.L, els.L, tg.set(-0.2, 0.9, 0.42 - sway), -1, rw * sw);
    }
  });
})();

"""
rep1("</script>\n</body>", "</script>\n<script>\n/* === DUDUK DI PERAHU v4.8 (pmBoatSeat) === */" + SEAT_JS + "</script>\n</body>", 'penutup body')

# 4. versi + info update
rep1("var VER = 'v4.7', DATE = '4 Okt 2026'", "var VER = 'v4.8', DATE = '4 Okt 2026'", 'VER')
sub1(r'\["Update v4\.7", \[.*?\n    \]\]', """["Update v4.8", [
      "Tombol Grafis (Mode HD) di Menu dihapus. Grafis HD sekarang selalu aktif, dan turun otomatis kalau FPS drop.",
      "Karakter sekarang duduk di perahu, nggak berdiri lagi. Di Sampan karakter mendayung, di perahu lain duduk sambil pegang kemudi.",
      "Joran disimpan waktu berlayar, dan keluar lagi pas perahu berhenti buat mancing."
    ]]""", 'LOG')
open(F, 'w', encoding='utf-8').write(s)

# 5. CHANGELOG
try:
    c = open('CHANGELOG.md', encoding='utf-8').read()
    entry = """## 2026-10-04 (v4.8)

- Tombol Grafis (Mode HD) di Menu dihapus. HD selalu aktif, dan turun otomatis ke Normal kalau FPS drop (cuma selama sesi itu).
- Karakter duduk di perahu dan menghadap sesuai arah perahu. Di Sampan karakter mendayung dengan dayung yang ikut bergerak, di perahu lain duduk sambil pegang kemudi.
- Tiap perahu punya titik duduk sendiri (Jukung dan Speedboat dapat bangku baru).
- Joran disimpan waktu berlayar, keluar lagi pas perahu berhenti.
- Info Update lama diganti dengan yang baru, versi naik ke v4.8.

"""
    k = c.find('## 2026-10-04 (v4.7)')
    if k >= 0:
        open('CHANGELOG.md', 'w', encoding='utf-8').write(c[:k] + entry + c[k:])
except Exception as e:
    print('CHANGELOG dilewati:', e)
print('Patch v4.8 selesai. Backup: index.html.bak-v47')
