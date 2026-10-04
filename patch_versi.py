#!/usr/bin/env python3
# Sinkron versi + Info Update (satu entri gabungan, entri lama dihapus)
# Pakai: python3 patch_versi.py index.html
import sys, shutil, re, os, subprocess, tempfile

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()
s = src
errors = []

have40 = 'PM_V40' in s
have41 = 'PM_V41' in s
have42 = 'PM_V42' in s
ver = 'v4.2' if have42 else 'v4.1' if have41 else 'v4.0' if have40 else None
if not ver:
    print('GAGAL: patch v4.0 belum terpasang, tidak ada yang diubah.')
    sys.exit(1)

lines = []
if have40:
    lines += [
        "Rebirth: reset level dan progres untuk bonus permanen Luck, Speed, Harga Jual, dan XP, plus gelar baru. Tombolnya ada di Menu.",
        "Pet pendamping: beli Telur Pet, ada 6 jenis, bonusnya naik bintang kalau dapat duplikat. Slot ke-2 terbuka di Rebirth 3.",
        "Nama pulau tampil di atas pulau dan muncul pesan selamat datang saat tiba. Pulau pertama bernama Pulau Utama."
    ]
if have41:
    lines += [
        "Akuarium sekarang menghasilkan koin pasif, tersimpan sampai 8 jam. Ambil lewat tombol di Akuarium.",
        "16 trofi baru dan gelar berdasarkan jumlah trofi, tampil di bagian bawah Trofi."
    ]
if have42:
    lines += [
        "Peringkat Online: pemain dengan tangkapan terbanyak, ikan terberat, dan prestise tertinggi.",
        "Boss Fish: boss raksasa muncul berkala untuk semua pemain online. Tap SERANG bareng-bareng, hadiah dibagi sesuai jumlah serangan dan MVP dapat bonus.",
        "Pasar Pemain: jual-beli ikan antar pemain, biaya pasar 5%, maksimal 5 listing per pemain."
    ]
lines += [
    "Malam dan hujan lebih terang, mode Grafis HD lebih ringan, dan altar enchant tampil lebih HD."
]

new_log = '  var LOG = [\n    ["Update ' + ver + '", [\n' + ',\n'.join('      "' + l + '"' for l in lines) + '\n    ]]\n  ];'

a = s.find("  var LOG = [\n")
if s.count("  var LOG = [\n") != 1:
    errors.append('awal LOG: ketemu %d kali (harus 1)' % s.count("  var LOG = [\n"))
else:
    m = re.search(r"\n  \];", s[a:])
    if not m or m.end() > 80000:
        errors.append('akhir LOG tidak ketemu')
    else:
        s = s[:a] + new_log + s[a + m.end():]

s, n1 = re.subn(r"var VER = 'v[0-9.]+', DATE = '[^']*',", "var VER = '" + ver + "', DATE = '3 Okt 2026',", s)
s, n2 = re.subn(r'<div id="versionBadge">v[0-9.]+</div>', '<div id="versionBadge">' + ver + '</div>', s)
if n1 != 1: errors.append('VER/DATE: ketemu %d kali (harus 1)' % n1)
if n2 != 1: errors.append('badge versi: ketemu %d kali (harus 1)' % n2)

if errors:
    print('GAGAL, file TIDAK diubah:')
    for e in errors: print(' -', e)
    sys.exit(1)

if s == src:
    print('Sudah sinkron, tidak ada yang diubah.')
    sys.exit(0)

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
    fresh = [x for x in js_bad(s) if x[0] not in old_bad]
    if fresh:
        print('GAGAL, error sintaks JS, file TIDAK diubah:')
        for i, msg in fresh: print(' - script #%d: %s' % (i, msg))
        sys.exit(1)
    print('Cek sintaks JS: OK')

shutil.copyfile(path, path + '.bak-ver')
open(path, 'w', encoding='utf-8').write(s)
print('Versi ' + ver + ' + Info Update terpasang (' + str(len(lines)) + ' poin). Backup: ' + path + '.bak-ver')
