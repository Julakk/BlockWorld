#!/usr/bin/env python3
# Patch v3.9b - malam + hujan lebih terang
# Pakai: python3 patch_malam.py index.html
import sys, shutil

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()

if 'PM_V39B' in src:
    print('Patch sudah terpasang, tidak ada yang diubah.')
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

# 1. buat cahaya bulan (sekali saja, di dalam loop cuaca)
replace_once(
    "PMHD.tick(raw); PMQ.adapt(raw);",
    "PMHD.tick(raw); PMQ.adapt(raw);\n"
    "      /* PM_V39B cahaya bulan */\n"
    "      if (!window.PM_MOON) {\n"
    "        window.PM_MOON = new THREE.AmbientLight(0x7a92d8, 0);\n"
    "        window.PM_MOONFOG = new THREE.Color(0x2a3b63);\n"
    "        scene.add(window.PM_MOON);\n"
    "      }",
    'init cahaya bulan')

# 2. hujan tidak menggelapkan sebanyak dulu
replace_once(
    "sunLight.intensity = si * (1 - 0.45 * rainLevel);",
    "sunLight.intensity = si * (1 - 0.25 * rainLevel);",
    'redaman matahari')
replace_once(
    "hemiLight.intensity = hi * (1 - 0.2 * rainLevel);",
    "hemiLight.intensity = hi * (1 - 0.08 * rainLevel);",
    'redaman hemi')

# 3. cahaya bulan + kabut diangkat saat malam
replace_once(
    "starMat.opacity = night * (1 - rainLevel); stars.visible = starMat.opacity > 0.02;",
    "starMat.opacity = night * (1 - rainLevel); stars.visible = starMat.opacity > 0.02;\n"
    "      window.PM_MOON.intensity = night * (1.0 + 0.3 * rainLevel);\n"
    "      scene.fog.color.lerp(window.PM_MOONFOG, night * 0.3);",
    'cahaya bulan + kabut')

# 4. catatan Info Update
replace_once(
    '      "Info Update lama dihapus, sekarang hanya menampilkan update terbaru."',
    '      "Malam dan hujan sekarang lebih terang: ada cahaya bulan, redaman saat hujan dikurangi, dan kabut malam tidak sepekat dulu.",\n'
    '      "Info Update lama dihapus, sekarang hanya menampilkan update terbaru."',
    'changelog')

if errors:
    print('GAGAL, file TIDAK diubah:')
    for e in errors: print(' -', e)
    sys.exit(1)

shutil.copyfile(path, path + '.bak-malam')
open(path, 'w', encoding='utf-8').write(s)
print('Patch malam terpasang. Backup: ' + path + '.bak-malam')
