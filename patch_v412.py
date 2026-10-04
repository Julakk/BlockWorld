#!/usr/bin/env python3
# v4.12: hapus Akuarium, ganti Mesin Gacha 3D, gacha HD, hapus tombol Gacha di Menu/layar utama
import os, re, sys, shutil, subprocess

D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, 'index.html')
J = os.path.join(D, 'gacha_v412.js')
BAK = P + '.bak_v412'

def die(m):
    print('GAGAL:', m)
    sys.exit(1)

if not os.path.exists(P) or not os.path.exists(J):
    die('index.html atau gacha_v412.js nggak ada di ' + D)
src = open(P, encoding='utf-8').read()
js = open(J, encoding='utf-8').read().strip()
if 'PM-GACHA v2' in src:
    die('sudah pernah di-patch (PM-GACHA v2 sudah ada)')
shutil.copy(P, BAK)

# 1) buang blok Akuarium, sisakan AQ (posisi papan peringkat), icon(), dan migrasi ikan
a = src.find('/* ===== AKUARIUM ===== */')
b = src.find('/* === BOAT MODELS v4.6')
if a < 0 or b < 0 or a > b:
    die('blok Akuarium nggak ketemu')
NEW_AQ = r"""/* ===== AKUARIUM DIHAPUS (v4.12): diganti Mesin Gacha 3D, lihat PM-GACHA ===== */
  var AQ = { x: 4.5, z: 19 };
  function icon(e) { return '<img class="rowIcon" src="' + C.fishIconCanvas(e.fish, e.mutation) + '">'; }
  (function () { /* ikan yang dulu dipajang balik ke tas */
    var done = false;
    C.hookAnim(function () {
      if (done) return;
      var s = S(); if (!s || !s.inventory) return;
      done = true;
      var a = s.aqua; if (!a || !a.length) { delete s.aqua; return; }
      var n = 0;
      a.forEach(function (e) {
        if (!e || !e.fish || !e.mutation) return;
        var k = e.fish.id + '|' + e.mutation.id;
        s.inventory[k] = s.inventory[k] || { fish: e.fish, mutation: e.mutation, count: 0 };
        s.inventory[k].count++; n++;
      });
      delete s.aqua; C.persist(); C.refresh();
      if (n) C.toast('Akuarium dihapus: ' + n + ' ikan dikembalikan ke tas');
    });
  })();

  """
src = src[:a] + NEW_AQ + src[b:]

# 2) animasi tank di loop utama
if src.count('animTank(t); ') != 1:
    die('animTank(t) di loop nggak ketemu persis 1x')
src = src.replace('animTank(t); ', '')

# 3) cabang server aqs/aqpay di PMLB
a = src.find("else if (m.t === 'aqs')")
b = src.find("else if (m.t === 'mlist')")
if a < 0 or b < 0 or a > b:
    die('cabang aqs/aqpay nggak ketemu')
src = src[:a] + src[b:]

# 4) aqPush() sisa di lbReport
src, n = re.subn(r'\n[ \t]*aqPush\(\);', '', src)
print('aqPush dibuang:', n)

# 5) trofi Akuarium -> trofi Gacha (index tetap)
src, n1 = re.subn(r"\['Aquarist',.*?\],\n",
    lambda m: "['Penarik Gacha', 'Lakukan 50 kali Gacha Rod', 50, 600, function () { return (S().gacha || {}).total || 0; }],\n",
    src, count=1, flags=re.S)
src, n2 = re.subn(r"\['Bos Akuarium',.*?\}\]",
    lambda m: "['Kolektor Skin', 'Kumpulkan 8 skin rod', 8, 4000, function () { return Object.keys(S().skins || {}).length; }]",
    src, count=1, flags=re.S)
if n1 != 1 or n2 != 1:
    shutil.copy(BAK, P); die('trofi Akuarium nggak ketemu (n1=%d n2=%d)' % (n1, n2))

# 6) tips yang nyebut Akuarium
src = src.replace('Pajang ikan langka di Akuarium biar gak ikut kejual.',
                  'Coba Mesin Gacha di plaza buat dapetin skin rod keren.')

# 7) ganti seluruh blok gacha lama
g0 = src.find('<!--PM-GACHA-START-->')
g1 = src.find('<!--PM-GACHA-END-->')
if g0 < 0 or g1 < 0 or g0 > g1:
    shutil.copy(BAK, P); die('blok PM-GACHA nggak ketemu')
src = src[:g0] + '<!--PM-GACHA-START-->\n' + js + '\n' + src[g1:]

# 8) versi + Info Update
if "var VER = 'v4.11'" not in src or '["Update v4.11", [' not in src:
    shutil.copy(BAK, P); die('anchor versi v4.11 nggak ketemu')
src = src.replace("var VER = 'v4.11'", "var VER = 'v4.12'", 1)
LOG = ('["Update v4.12", ['
  '"Akuarium dihapus dan diganti Mesin Gacha 3D di plaza (tempat Akuarium dulu). Deketin mesinnya lalu tekan Main Gacha Rod.",'
  '"Gacha sekarang pakai panggung 3D HD: kapsul jatuh, bergetar, lalu pecah dengan efek cahaya dan partikel, hadiahnya muncul 3D dan berputar. Ketuk gambar buat lewati.",'
  '"Skin Rod bisa dipreview 3D dari tab Skin Saya (ketuk skin yang dimiliki).",'
  '"Tombol Gacha di Menu dan layar utama dihapus.",'
  '"Ikan yang dulu dipajang di Akuarium otomatis dikembalikan ke tas. Trofi Akuarium diganti trofi Gacha."'
  ']],\n    ')
src = src.replace('["Update v4.11", [', LOG + '["Update v4.11", [', 1)

# 9) sisa referensi Akuarium?
for nm in ['aqPush', 'aqSrv', 'aqBusy', 'aqAccrue', 'renderA', 'mA', 'animTank', 'rebuildTank', 'tankKey']:
    if re.search(r'\b' + nm + r'\b', src):
        shutil.copy(BAK, P); die('masih ada referensi ke ' + nm + ', file dikembalikan')

open(P, 'w', encoding='utf-8').write(src)

# 10) cek sintaks pakai node kalau ada
if shutil.which('node'):
    for i, m in enumerate(re.finditer(r'<script>(.*?)</script>', src, re.S)):
        f = '/tmp/_pmchk%d.js' % i
        open(f, 'w', encoding='utf-8').write(m.group(1))
        r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy(BAK, P)
            print(r.stderr[:1500])
            die('syntax error di script #%d, index.html dikembalikan dari backup' % i)
    print('cek sintaks node: OK')
else:
    print('node nggak ada, cek sintaks dilewati')

print('SELESAI: v4.12 ter-patch. Backup: ' + BAK)
