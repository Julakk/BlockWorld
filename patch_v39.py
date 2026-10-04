#!/usr/bin/env python3
# Patch v3.9 - HUD ikan kecil, altar HD, FPS HD adaptif, Info Update baru
# Pakai: python3 patch_v39.py index.html
import sys, shutil, re, os, subprocess, tempfile

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()

if 'PM_V39' in src:
    print('Patch v3.9 sudah terpasang, tidak ada yang diubah.')
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

# ---------- 1. HUD reveal ikan: lebih kecil + naik ----------
CSS = """<style>
/* PM_V39 reveal ikan lebih kecil */
#catchReveal { top: 26% !important; transform: translate(-50%, -50%) scale(.7) !important; }
#catchRevealCard { padding: 9px 16px 9px 11px !important; gap: 10px !important; }
#catchReveal.tier-legendary #catchRevealCard, #catchReveal.tier-mythical #catchRevealCard { padding: 10px 18px 10px 12px !important; }
#catchRevealImg, #catchReveal.tier-legendary #catchRevealImg, #catchReveal.tier-mythical #catchRevealImg { width: 56px !important; height: 56px !important; }
#catchRevealName { font-size: 16px !important; }
#catchReveal.tier-mythical #catchRevealName { font-size: 18px !important; }
</style>
</head>"""
replace_once("</head>", CSS, 'css reveal (</head>)')

# ---------- 2. FPS HD: resolusi adaptif + bayangan hemat ----------
PMQ_BLOCK = r"""/* PM_V39 resolusi adaptif */
  const PMQ = {
    base: 1, now: 1, acc: 0, frames: 0, t: 0, upOk: 0, floor: 0.75,
    adapt(raw) {
      if (raw > 0.5) return;
      if (!PMHD.isHD()) return;
      this.t += raw; if (this.t < 3) return;
      this.acc += raw; this.frames++;
      if (this.acc < 2) return;
      const fps = this.frames / this.acc;
      this.acc = 0; this.frames = 0;
      if (fps < 45 && this.now > this.floor) {
        this.now = Math.max(this.floor, this.now - 0.2); this.upOk = 0; this.applyNow();
      } else if (fps >= 58 && this.now < this.base) {
        if (++this.upOk >= 4) { this.now = Math.min(this.base, this.now + 0.1); this.upOk = 0; this.applyNow(); }
      } else { this.upOk = 0; }
    },
    applyNow() { renderer.setPixelRatio(this.now); renderer.setSize(window.innerWidth, window.innerHeight); }
  };
  const PMHD = (function () {"""
replace_once("const PMHD = (function () {", PMQ_BLOCK, 'PMQ sebelum PMHD')

replace_once(
    "renderer.setPixelRatio(on ? Math.min(dpr, 2.5) : Math.min(dpr, isMobile ? 2 : 2.5));",
    "PMQ.base = on ? Math.min(dpr, isMobile ? 1.5 : 2) : Math.min(dpr, isMobile ? 2 : 2.5); PMQ.now = PMQ.base; renderer.setPixelRatio(PMQ.now);",
    'pixel ratio HD')
replace_once(
    "sunLight.shadow.mapSize.set(2048, 2048);",
    "sunLight.shadow.mapSize.set(isMobile ? 1024 : 2048, isMobile ? 1024 : 2048);",
    'shadow map size')
replace_once(
    "sc.left = -28; sc.right = 28; sc.top = 28; sc.bottom = -28;",
    "sc.left = -22; sc.right = 22; sc.top = 22; sc.bottom = -22;",
    'shadow camera')
replace_once(
    "renderer.shadowMap.type = THREE.PCFSoftShadowMap;",
    "renderer.shadowMap.type = isMobile ? THREE.PCFShadowMap : THREE.PCFSoftShadowMap;",
    'shadow type')
replace_once(
    "const maxAniso = renderer.capabilities.getMaxAnisotropy();",
    "const maxAniso = Math.min(renderer.capabilities.getMaxAnisotropy(), isMobile ? 4 : 8);",
    'anisotropy')
replace_once("PMHD.tick(raw);", "PMHD.tick(raw); PMQ.adapt(raw);", 'loop adapt')

# ---------- 3. Altar enchant HD ----------
NEW_ALTAR = r"""  // ================= ALTAR ENCHANT (HD v3.9) =================
  function altStoneTexture() {
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const g = c.getContext('2d');
    g.fillStyle = '#8b8fa3'; g.fillRect(0, 0, 128, 128);
    for (let i = 0; i < 900; i++) {
      const v = 110 + Math.floor(Math.random() * 60);
      g.fillStyle = 'rgba(' + v + ',' + (v + 2) + ',' + (v + 16) + ',0.35)';
      g.fillRect(Math.random() * 128, Math.random() * 128, 2 + Math.random() * 5, 2 + Math.random() * 3);
    }
    g.strokeStyle = 'rgba(30,30,50,0.35)'; g.lineWidth = 1;
    for (let i = 0; i < 8; i++) {
      g.beginPath(); let x = Math.random() * 128, y = Math.random() * 128; g.moveTo(x, y);
      for (let j = 0; j < 5; j++) { x += Math.random() * 18 - 9; y += Math.random() * 18 - 9; g.lineTo(x, y); }
      g.stroke();
    }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2, 1); t.anisotropy = 4;
    return t;
  }
  function altRuneTexture(dense) {
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d'); g.translate(128, 128);
    g.strokeStyle = '#d9a8ff'; g.shadowColor = '#b56bff'; g.shadowBlur = 8;
    g.lineWidth = 3; g.beginPath(); g.arc(0, 0, 122, 0, Math.PI * 2); g.stroke();
    g.lineWidth = 2; g.beginPath(); g.arc(0, 0, dense ? 70 : 96, 0, Math.PI * 2); g.stroke();
    const n = dense ? 16 : 12, r0 = dense ? 76 : 102, r1 = 116;
    for (let i = 0; i < n; i++) {
      g.save(); g.rotate(i * Math.PI * 2 / n);
      g.beginPath();
      g.moveTo(0, -r0); g.lineTo(0, -r1);
      g.moveTo(0, -(r0 + (r1 - r0) * 0.35)); g.lineTo(7, -(r0 + (r1 - r0) * 0.7));
      if (i % 2) { g.moveTo(0, -(r0 + (r1 - r0) * 0.65)); g.lineTo(-7, -(r0 + (r1 - r0) * 0.9)); }
      g.stroke(); g.restore();
    }
    const t = new THREE.CanvasTexture(c); t.anisotropy = 4;
    return t;
  }
  const altar = new THREE.Group();
  const stoneMat = new THREE.MeshStandardMaterial({ map: altStoneTexture(), roughness: 0.9, metalness: 0.05 });
  const goldMat = new THREE.MeshStandardMaterial({ color: 0xd9b25a, roughness: 0.4, metalness: 0.6 });
  const altBandMat = new THREE.MeshBasicMaterial({ color: 0xb56bff });
  const altBase1 = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.7, 0.35, 32), stoneMat); altBase1.position.y = 0.17; altar.add(altBase1);
  const altBase2 = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.2, 0.3, 32), stoneMat); altBase2.position.y = 0.5; altar.add(altBase2);
  const altTrim1 = new THREE.Mesh(new THREE.TorusGeometry(1.52, 0.05, 8, 48), goldMat); altTrim1.rotation.x = Math.PI / 2; altTrim1.position.y = 0.35; altar.add(altTrim1);
  const altTrim2 = new THREE.Mesh(new THREE.TorusGeometry(1.02, 0.04, 8, 40), goldMat); altTrim2.rotation.x = Math.PI / 2; altTrim2.position.y = 0.65; altar.add(altTrim2);
  for (let k = 0; k < 4; k++) {
    const a = k * Math.PI / 2 + Math.PI / 4, px = Math.cos(a) * 1.3, pz = Math.sin(a) * 1.3;
    const pil = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.15, 1.7, 12), stoneMat); pil.position.set(px, 1.05, pz); altar.add(pil);
    const cap = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.1, 0.34), goldMat); cap.position.set(px, 1.95, pz); cap.rotation.y = a; altar.add(cap);
    const foot = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.1, 0.34), goldMat); foot.position.set(px, 0.4, pz); foot.rotation.y = a; altar.add(foot);
    const band = new THREE.Mesh(new THREE.CylinderGeometry(0.155, 0.155, 0.05, 12), altBandMat); band.position.set(px, 1.25, pz); altar.add(band);
  }
  const altPed = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.4, 0.5, 16), stoneMat); altPed.position.y = 0.9; altar.add(altPed);
  const crystal = new THREE.Mesh(new THREE.OctahedronGeometry(0.42), new THREE.MeshStandardMaterial({ color: 0xc58bff, emissive: 0x9a4dff, emissiveIntensity: 1.2, roughness: 0.15, metalness: 0.3, flatShading: true }));
  crystal.position.y = 1.65; altar.add(crystal);
  const altGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: makeGlowTexture(), color: 0xb56bff, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, fog: false }));
  altGlow.scale.set(2.8, 2.8, 1); altGlow.position.y = 1.65; altar.add(altGlow);
  const altSign = new THREE.Sprite(new THREE.SpriteMaterial({ map: makeSignTexture('ENCHANT', '#5a2a8a'), fog: false }));
  altSign.scale.set(2.0, 0.5, 1); altSign.position.y = 2.9; altar.add(altSign);
  const altRuneTop = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 2.0), new THREE.MeshBasicMaterial({ map: altRuneTexture(true), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.9 }));
  altRuneTop.rotation.x = -Math.PI / 2; altRuneTop.position.y = 0.67; altar.add(altRuneTop);
  const altRuneFloor = new THREE.Mesh(new THREE.PlaneGeometry(5.4, 5.4), new THREE.MeshBasicMaterial({ map: altRuneTexture(false), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.7 }));
  altRuneFloor.rotation.x = -Math.PI / 2; altRuneFloor.position.y = 0.04; altar.add(altRuneFloor);
  const altShards = [];
  for (let i = 0; i < 3; i++) {
    const sh = new THREE.Mesh(new THREE.OctahedronGeometry(0.11), new THREE.MeshBasicMaterial({ color: 0xe6c8ff }));
    altar.add(sh); altShards.push(sh);
  }
  const ALT_N = 36, altPPos = new Float32Array(ALT_N * 3), altPSeed = [];
  for (let i = 0; i < ALT_N; i++) altPSeed.push({ a: Math.random() * 6.283, r: 0.4 + Math.random() * 1.6, sp: 0.25 + Math.random() * 0.45, ph: Math.random() });
  const altPGeo = new THREE.BufferGeometry();
  (altPGeo.setAttribute || altPGeo.addAttribute).call(altPGeo, 'position', new THREE.BufferAttribute(altPPos, 3));
  const altPts = new THREE.Points(altPGeo, new THREE.PointsMaterial({ color: 0xe2b8ff, size: 0.09, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false }));
  altPts.frustumCulled = false; altar.add(altPts);
  const altT0 = performance.now();
  const _utaH = updateTownAnim;
  updateTownAnim = function (t) {
    _utaH(t);
    const s = (performance.now() - altT0) / 1000;
    altRuneTop.rotation.z = s * 0.6; altRuneFloor.rotation.z = -s * 0.25;
    altRuneTop.castShadow = false; altRuneFloor.castShadow = false;
    for (let i = 0; i < altShards.length; i++) {
      const sh = altShards[i], a = s * 0.9 + i * 2.094;
      sh.position.set(Math.cos(a) * 0.95, 1.65 + Math.sin(s * 1.6 + i) * 0.15, Math.sin(a) * 0.95);
      sh.rotation.y = s * 2; sh.castShadow = false;
    }
    for (let i = 0; i < ALT_N; i++) {
      const q = altPSeed[i], u = (q.ph + s * q.sp * 0.3) % 1, ang = q.a + s * 0.35, rr = q.r * (1 - 0.35 * u);
      altPPos[i * 3] = Math.cos(ang) * rr; altPPos[i * 3 + 1] = 0.7 + u * 2.6; altPPos[i * 3 + 2] = Math.sin(ang) * rr;
    }
    altPGeo.attributes.position.needsUpdate = true;
    crystal.material.emissiveIntensity = 1.0 + 0.4 * Math.sin(s * 2);
  };
"""
a = s.find("  // ================= ALTAR ENCHANT =================")
b = s.find("  altar.position.set(-10.5, DECK_Y, 19.5);")
if a < 0 or b < 0 or b < a:
    errors.append('blok altar tidak ketemu')
else:
    old = s[a:b]
    if 'const crystal' not in old or 'const altGlow' not in old or 'const altSign' not in old:
        errors.append('isi blok altar tidak sesuai dugaan')
    else:
        s = s[:a] + NEW_ALTAR + s[b:]

# ---------- 4. Info Update: hapus lama, ganti baru ----------
NEW_LOG = r"""  var LOG = [
    ["Update v3.9", [
      "Tampilan ikan tangkapan dikecilkan dan dipindah ke atas, jadi karakter dan joran tetap kelihatan.",
      "Altar Enchant tampil lebih HD: batu lebih detail, lingkaran rune bercahaya yang berputar, kristal berkilau, serpihan melayang, dan partikel cahaya.",
      "Mode Grafis HD lebih ringan: resolusi menyesuaikan FPS secara otomatis, bayangan lebih hemat, dan filter tekstur dibatasi di HP.",
      "Info Update lama dihapus, sekarang hanya menampilkan update terbaru."
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
replace_once("var VER = 'v3.8', DATE = '3 Okt 2026',", "var VER = 'v3.9', DATE = '3 Okt 2026',", 'VER')
replace_once('<div id="versionBadge">v3.8</div>', '<div id="versionBadge">v3.9</div>', 'badge versi')

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
    new_bad = js_bad(s)
    fresh = [x for x in new_bad if x[0] not in old_bad]
    if fresh:
        print('GAGAL, error sintaks JS, file TIDAK diubah:')
        for i, msg in fresh: print(' - script #%d: %s' % (i, msg))
        sys.exit(1)
    print('Cek sintaks JS: OK')
else:
    print('node tidak ada, cek sintaks dilewati.')

shutil.copyfile(path, path + '.bak-v39')
open(path, 'w', encoding='utf-8').write(s)
print('Patch v3.9 terpasang. Backup: ' + path + '.bak-v39')
