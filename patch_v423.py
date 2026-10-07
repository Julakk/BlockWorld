#!/usr/bin/env python3
# v4.23: pohon di samping Jual Ikan dihapus, Mesin Gacha + Papan Peringkat dipindah ke situ
import os, sys, shutil

D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, 'index.html')
BAK = P + '.bak_v423'

def die(m):
    print('GAGAL:', m)
    sys.exit(1)

if not os.path.exists(P):
    die('index.html nggak ada di ' + D)
src = open(P, encoding='utf-8').read()
if "var VER = 'v4.23'" in src:
    die('sudah pernah di-patch (v4.23 sudah ada)')
if "var VER = 'v4.22'" not in src:
    die('versi dasar harus v4.22')
shutil.copy(P, BAK)

# koordinat baru (sisi utara Jual Ikan, hadap ke plaza). Ubah di sini kalau mau geser.
GX, GZ = 9, 14.2     # Mesin Gacha
BX, BZ = 9, 10.4     # Papan Peringkat

EDITS = [
  ("  function addPalm(x, z, lean) {\n",
   "  function addPalm(x, z, lean) {\n"
   "    if (x > 4.5 && x < 13 && z > 6.5 && z < 16.5) return; // v4.23: area samping Jual Ikan dikosongkan\n"),
  ("function inTown(x, z) { return z > 14.2 && Math.abs(x) < 18; }",
   "function inTown(x, z) { return (z > 14.2 && Math.abs(x) < 18) || (x > 4.5 && x < 13.5 && z > 6.5 && z < 16.5); }"),
  ("var MX = 4.5, MZ = 19;\n  var mach = new T.Group(); mach.position.set(MX, C.DECK_Y, MZ);",
   "var MX = %s, MZ = %s;\n"
   "  function gy423(x, z) { return Math.sin(x * 0.15) * Math.cos(z * 0.15) * 0.7 * (1 - Math.min(1, Math.sqrt(x * x + z * z) / C.ISLAND_RADIUS)) + 0.02; }\n"
   "  var mach = new T.Group(); mach.position.set(MX, gy423(MX, MZ), MZ); mach.rotation.y = -PI / 2; // hadap -x (ke plaza), sejajar Jual Ikan" % (GX, GZ)),
  ("x: MX, z: MZ + 0.2, action: function () { openG(); }",
   "x: MX - 0.2, z: MZ, action: function () { openG(); }"),
  ("var LBB = { x: AQ.x - 4.3, z: AQ.z + 0.2 };",
   "var LBB = { x: %s, z: %s };" % (BX, BZ)),
  ("lbBoard.position.set(LBB.x, C.DECK_Y, LBB.z);",
   "lbBoard.position.set(LBB.x, Math.sin(LBB.x * 0.15) * Math.cos(LBB.z * 0.15) * 0.7 * (1 - Math.min(1, Math.sqrt(LBB.x * LBB.x + LBB.z * LBB.z) / C.ISLAND_RADIUS)) + 0.02, LBB.z); lbBoard.rotation.y = -Math.PI / 2;"),
  ("x: LBB.x, z: LBB.z + 0.6, action: function () { openLB(); mLB.open(); }",
   "x: LBB.x - 0.6, z: LBB.z, action: function () { openLB(); mLB.open(); }"),
  ("var VER = 'v4.22', DATE = '5 Okt 2026'", "var VER = 'v4.23', DATE = '7 Okt 2026'"),
  ('    ["Update v4.22", [',
   '    ["Update v4.23", [\n'
   '      "Mesin Gacha Rod dan Papan Peringkat Ikan Ditangkap dipindah ke samping Jual Ikan, sejajar menghadap plaza.",\n'
   '      "Pohon palem di samping Jual Ikan dihapus untuk memberi tempat."\n'
   '    ]],\n'
   '    ["Update v4.22", ['),
]

for old, new in EDITS:
    if src.count(old) != 1:
        shutil.copy(BAK, P)
        die('anchor nggak ketemu / ganda, file dikembalikan:\n  ' + old[:90].replace('\n', ' '))
    src = src.replace(old, new, 1)

open(P, 'w', encoding='utf-8').write(src)
print('OK v4.23. Backup: index.html.bak_v423')
print('Gacha -> (%s, %s) | Papan Peringkat -> (%s, %s)' % (GX, GZ, BX, BZ))
