# Pancing Mania v3.4: animasi Secret lebih hidup + naik versi + Info Update + changelog
import sys, io
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)
class Patch:
    def __init__(self, path): self.path, self.s = path, load(path)
    def rep(self, old, new, name):
        n = self.s.count(old)
        if n != 1:
            print('GAGAL:', name, '-> ketemu', n, 'x (harus 1). Tidak ada file yang diubah.'); sys.exit(1)
        self.s = self.s.replace(old, new); print('OK   :', name)
    def done(self): save(self.path, self.s)

h = Patch('index.html')

h.rep("const T_FIGHT = 2.2, T_LEAP = 4.0, T_REVEAL = 4.9, T_HOLD = 6.2, T_END = 6.8;",
      "const T_FIGHT = 2.6, T_LEAP = 4.8, T_REVEAL = 5.7, T_HOLD = 7.0, T_END = 7.6;", 'durasi adegan')
h.rep("let wy = 0, fov0 = 65, Lleap = 5, Lhold = 2.6, rippleT = 0, pTick = 0;",
      "let wy = 0, fov0 = 65, Lleap = 5, Lhold = 2.6, rippleT = 0, pTick = 0;\n    let fin = null, splashT = 0, wig = 1, finPx = 0, finPz = 0, finHead = 0;", 'variabel baru')
h.rep("    function animateModel(time, open) {",
"""    function undulate(time) {
      if (!inner) return;
      if (parts.tent) { // kraken: mantel berdenyut kayak jet
        const s0 = parts.s0 || 0.36, p = Math.sin(time * 5.5) * wig;
        inner.scale.set(s0 * (1 + 0.07 * p), s0 * (1 + 0.07 * p), s0 * (1 - 0.1 * p)); return;
      }
      if (!parts.kids) parts.kids = inner.children.map(c => ({ c: c, x: c.position.x, ry: c.rotation.y, z: c.position.z }));
      for (let i = 0; i < parts.kids.length; i++) {
        const k = parts.kids[i], w = Math.min(1, Math.max(0, 0.5 - k.z)), w2 = w * w, ph = time * 11 - k.z * 6;
        k.c.position.x = k.x + Math.sin(ph) * wig * 0.07 * (0.15 + w2);
        if (k.c !== parts.tail) k.c.rotation.y = k.ry + Math.cos(ph) * wig * 0.35 * w;
      }
    }
    function animateModel(time, open) {""", 'fungsi undulate')
h.rep("if (parts.tail) parts.tail.rotation.y = Math.sin(time * 13) * 0.55;",
      "if (parts.tail) parts.tail.rotation.y = Math.sin(time * 11 + 3.5) * (0.22 + 0.5 * wig);\n      undulate(time);", 'ekor ikut gelombang badan')
h.rep("inner.scale.setScalar(kind === 'kraken' ? 0.36 : 1);",
      "inner.scale.setScalar(kind === 'kraken' ? 0.36 : 1); parts.s0 = inner.scale.x;", 'skala awal')
h.rep("shadow.visible = false; root.add(shadow);",
      "shadow.visible = false; root.add(shadow);\n"
      "        fin = kind === 'kraken' ? null : new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.8, 10), new THREE.MeshStandardMaterial({ color: id === 'megalodon' ? 0x56707f : 0xd9a441, roughness: 0.5 }));\n"
      "        if (fin) { fin.rotation.order = 'YXZ'; fin.visible = false; root.add(fin); }\n"
      "        finPx = S.x; finPz = S.z; finHead = Math.atan2(A.x - S.x, A.z - S.z); splashT = 0.3; wig = 1;", 'bikin sirip')
h.rep("erupted = true; fish.position.copy(A); fpPrev.copy(A);",
      "erupted = true; fish.position.copy(A); fpPrev.copy(A); if (fin) fin.visible = false;", 'sirip hilang pas ikan loncat')
h.rep("rings.length = 0; ptsGeo = null; fish = null; line = null; shadow = null; beam = null; parts = {};",
      "rings.length = 0; ptsGeo = null; fish = null; line = null; shadow = null; beam = null; fin = null; parts = {};", 'bersihin sirip')
h.rep("line.visible = true; drawLine(fp, 0.05 + 0.25 * (1 - e));",
"""line.visible = true; drawLine(fp, 0.05 + 0.25 * (1 - e));
      splashT -= dt;
      if (splashT <= 0) {
        splashT = 0.2 + Math.random() * 0.22 - 0.12 * u;
        emit(fp.x + (Math.random() - 0.5) * L * 0.4, wy + 0.1, fp.z + (Math.random() - 0.5) * L * 0.4, 10 + Math.floor(16 * u), 2.4 + 2.2 * u, 3.5 + 3 * u, 0.85, 0.97, 1);
        if (Math.random() < 0.55) ring(fp.x, fp.z, 1 + 2.2 * u, 0.9);
        if (u > 0.45 && typeof cfxShake === 'function' && Math.random() < 0.3) cfxShake(90);
      }
      if (fin) {
        const dx = fp.x - finPx, dz = fp.z - finPz;
        if (dx * dx + dz * dz > 1e-5) finHead = Math.atan2(dx, dz);
        finPx = fp.x; finPz = fp.z;
        const fs = L * (0.28 + 0.1 * e);
        fin.visible = true; fin.scale.set(fs * 0.5, fs, fs * 0.9); fin.position.set(fp.x, wy + 0.3 * fs, fp.z);
        fin.rotation.set(-0.3, finHead + Math.sin(t * 6) * 0.25, 0);
      }""", 'fase melawan: percikan + sirip')
h.rep("fish.position.set(lerp(A.x, H.x, u), lerp(wy, H.y, u) + 4 * (kind === 'kraken' ? 2.6 : 3.2) * u * (1 - u), lerp(A.z, H.z, u));",
      "const wu = u + 0.5 * Math.sin(2 * Math.PI * u) / (2 * Math.PI); wig = 1;\n"
      "      fish.position.set(lerp(A.x, H.x, wu), lerp(wy, H.y, wu) + 4 * (kind === 'kraken' ? 2.6 : 3.2) * wu * (1 - wu), lerp(A.z, H.z, wu));", 'slow-motion puncak lompatan')
h.rep("fish.rotateZ(Math.sin(t * 15) * 0.32 * (1 - 0.5 * u) + (kind === 'kraken' ? 0 : Math.sin(t * 6) * 0.15));",
      "fish.rotateZ(Math.sin(t * 9) * 0.28 * (1 - 0.4 * u) + (kind === 'kraken' ? 0 : Math.sin(t * 5.3) * 0.12));", 'goyangan lebih lembut')
h.rep("eu.set(kind === 'kraken' ? -Math.PI / 2 : -0.28, th * 1.1, 0, 'YXZ'); qHold.setFromEuler(eu);",
      "wig = 0.18 + 0.8 * Math.exp(-th * 0.9);\n"
      "      eu.set((kind === 'kraken' ? -Math.PI / 2 : -1.0) + Math.sin(th * 2.1) * 0.12 * (1 - 0.5 * u), Math.sin(th * 0.9) * 1.0, Math.sin(th * 2.6) * 0.15 * (1 - u), 'YXZ'); qHold.setFromEuler(eu);", 'ikan menggantung & bandul')
h.rep("const sh = erupted ? 0.07 * (1 - c01((t - T_FIGHT) / 0.9)) : 0.012;",
      "const sh = erupted ? 0.07 * (1 - c01((t - T_FIGHT) / 0.9)) : 0.012 + 0.03 * c01(t / T_FIGHT);", 'getar kamera')
h.rep("const fv = fov0 + 12 * Math.sin(Math.PI * c01((t - T_FIGHT) / 1.4)) * w;",
      "const fv = fov0 + 12 * Math.sin(Math.PI * c01((t - T_FIGHT) / 1.4)) * w - 6 * Math.sin(Math.PI * c01((t - T_FIGHT - 0.5) / (T_LEAP - T_FIGHT - 0.5))) * w;", 'zoom pelan')
h.rep("var VER = 'v3.3', DATE = '2 Okt 2026', KEY = 'pm_seen_ver';",
      "var VER = 'v3.4', DATE = '2 Okt 2026', KEY = 'pm_seen_ver';", 'versi v3.4')
h.rep('["Update v3.3", [',
'''["Update v3.4", [
      "Animasi ikan Secret dibikin lebih hidup: badan ikan meliuk kayak berenang, ekornya menyabet, dan lompatannya mengikuti gravitasi dengan efek slow-motion di puncak.",
      "Pas ikan Secret melawan, sirip muncul di permukaan air, percikan makin ganas, dan layar bergetar makin kuat sebelum ikannya meloncat.",
      "Ikan Secret sekarang menggantung dari pancing dengan kepala di atas, bergoyang kayak bandul, makin lemas, dan air menetes dari badannya.",
      "Notifikasi ikan Secret sekarang muncul buat semua pemain, termasuk kamu sendiri, dan tetap terkirim walau koneksi sempat putus.",
      "Perbaikan server: jeda notifikasi Secret dipercepat jadi 4 detik per pemain."
    ]],
    ["Update v3.3", [''', 'isi Info Update v3.4')
h.done()

c = Patch('CHANGELOG.md')
c.rep("## 2026-10-02 (v3.3)",
"""## 2026-10-02 (v3.4)

- **Animasi ikan Secret lebih hidup**: badan ikan meliuk (gelombang S), ekor menyabet, kraken berdenyut seperti jet, lompatan mengikuti gravitasi dengan slow-motion di puncak, dan di fase melawan muncul sirip di permukaan air dengan percikan yang makin ganas.
- **Pamer ikan**: ikan menggantung kepala di atas, bergoyang seperti bandul, makin lemas, air menetes. Kamera bergetar saat ikan melawan dan zoom pelan saat melompat.
- **Notifikasi Secret**: toast pelangi muncul buat semua pemain termasuk diri sendiri, dan tampil di atas layar sinematik. Event yang dikirim saat koneksi putus diantri lalu dikirim ulang. Jeda server per pemain 30 detik jadi 4 detik.

## 2026-10-02 (v3.3)""", 'changelog v3.4')
c.done()
print('SELESAI. Commit & push, lalu tunggu build APK. Server VPS tidak perlu diubah.')
