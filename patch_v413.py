#!/usr/bin/env python3
# v4.13: Gacha 3D v3 (panggung HD landscape, ikon skin 3D, joran beraura) menggantikan blok PM-GACHA v2
import os, re, sys, shutil, subprocess

D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, 'index.html')
J = os.path.join(D, 'gacha_v413.js')
BAK = P + '.bak_v413'

def die(m):
    print('GAGAL:', m)
    sys.exit(1)

if not os.path.exists(P) or not os.path.exists(J):
    die('index.html atau gacha_v413.js nggak ada di ' + D)
src = open(P, encoding='utf-8').read()
js = open(J, encoding='utf-8').read().strip()
if 'PM-GACHA v3' in src:
    die('sudah pernah di-patch (PM-GACHA v3 sudah ada)')
if 'PM-GACHA v2' not in src:
    die('v4.12 belum ke-patch (PM-GACHA v2 nggak ketemu), jalanin patch_v412.py dulu')
shutil.copy(P, BAK)

g0 = src.find('<!--PM-GACHA-START-->')
g1 = src.find('<!--PM-GACHA-END-->')
if g0 < 0 or g1 < 0 or g0 > g1:
    die('penanda PM-GACHA nggak ketemu')
src = src[:g0] + '<!--PM-GACHA-START-->\n' + js + '\n' + src[g1:]

if "var VER = 'v4.12'" not in src or '["Update v4.12", [' not in src:
    shutil.copy(BAK, P); die('anchor versi v4.12 nggak ketemu, file dikembalikan')
src = src.replace("var VER = 'v4.12'", "var VER = 'v4.13'", 1)
LOG = ('["Update v4.13", ['
  '"Gacha tampil dalam panggung 3D HD: podium, kapsul jatuh dan pecah, hadiah muncul 3D. Di layar landscape panggung ada di kiri, daftar di kanan.",'
  '"Tab Skin Saya sekarang pakai ikon 3D joran, dan ketuk skin yang dimiliki buat lihat preview 3D-nya muter di podium.",'
  '"Skin rod yang dipakai tampil 3D realistis di tangan karakter dengan aura sesuai skin: Rare (aura tipis), Epic (selubung dan halo neon), Pelangi (pita warna mengalir), Api Naga (lidah api naik), Galaksi (bintang mengorbit).",'
  '"Perbaikan: panggung 3D yang tidak muncul setelah modal dibuka ulang."'
  ']],\n    ')
src = src.replace('["Update v4.12", [', LOG + '["Update v4.12", [', 1)

open(P, 'w', encoding='utf-8').write(src)

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

print('SELESAI: v4.13 ter-patch. Backup: ' + BAK)
