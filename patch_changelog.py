#!/usr/bin/env python3
# Tambah entri v3.8 - v4.2 ke CHANGELOG.md (meniru format entri teratas)
# Pakai: python3 patch_changelog.py CHANGELOG.md index.html
import sys, re, shutil

cl_path = sys.argv[1] if len(sys.argv) > 1 else 'CHANGELOG.md'
ix_path = sys.argv[2] if len(sys.argv) > 2 else 'index.html'
raw = open(cl_path, encoding='utf-8', newline='').read()
ix = open(ix_path, encoding='utf-8').read()
nl = '\r\n' if '\r\n' in raw else '\n'
lines = raw.split(nl)

VERS = [
    ('4.2', 'PM_V42', [
        "Peringkat Online: pemain dengan tangkapan terbanyak, ikan terberat, dan prestise tertinggi.",
        "Boss Fish: boss raksasa muncul berkala untuk semua pemain online. Hadiah dibagi sesuai jumlah serangan dan MVP dapat bonus.",
        "Pasar Pemain: jual-beli ikan antar pemain, biaya pasar 5%, maksimal 5 listing per pemain, barang disimpan di server sampai terjual."
    ]),
    ('4.1', 'PM_V41', [
        "Akuarium menghasilkan koin pasif, tersimpan sampai 8 jam, diambil lewat tombol di Akuarium.",
        "16 trofi baru dan gelar berdasarkan jumlah trofi."
    ]),
    ('4.0', 'PM_V40', [
        "Rebirth: reset level dan progres untuk bonus permanen Luck, Speed, Harga Jual, dan XP, plus gelar baru.",
        "Pet pendamping: Telur Pet, 6 jenis pet, bonus naik bintang kalau dapat duplikat, slot ke-2 terbuka di Rebirth 3.",
        "Nama pulau di atas pulau dan pesan selamat datang saat tiba. Pulau pertama bernama Pulau Utama."
    ]),
    ('3.9', 'PM_V39', [
        "Tampilan ikan tangkapan dikecilkan dan dipindah ke atas.",
        "Altar Enchant tampil lebih HD: tekstur batu, lingkaran rune berputar, kristal berkilau, serpihan, dan partikel.",
        "Mode Grafis HD lebih ringan: resolusi menyesuaikan FPS otomatis, bayangan lebih hemat.",
        "Malam dan hujan lebih terang: ada cahaya bulan, redaman hujan dikurangi.",
        "Info Update lama dihapus, hanya menampilkan update terbaru."
    ]),
    ('3.8', 'ENCHANT_V38', [
        "Altar Enchant dirombak: 14 enchant dengan 5 tier (Common, Rare, Epic, Legendary, Mythic).",
        "Efek baru Harga Jual dan XP, enchant Mythic Tycoon, Godhand, dan Omniscient.",
        "Animasi undian enchant, sistem Pity tiap 20 roll, dan Roll Kunci Tier.",
        "Peluang tiap tier ditampilkan langsung di altar."
    ]),
]

hidx = None
for i, l in enumerate(lines):
    if l.lstrip().startswith('#') and re.search(r'\bv?\d+\.\d+', l):
        hidx = i; break
if hidx is None:
    print('GAGAL: heading versi tidak ketemu di ' + cl_path + '. Kirim hasil: head -30 ' + cl_path)
    sys.exit(1)
tmpl = lines[hidx]

blank_after = hidx + 1 < len(lines) and lines[hidx + 1].strip() == ''
bullet = '- '
for l in lines[hidx + 1: hidx + 25]:
    t = l.lstrip()
    if t.startswith('#'): break
    mm = re.match(r'([-*•]\s+)', t)
    if mm: bullet = mm.group(1); break

def make_heading(ver):
    h = re.sub(r'(v?)\d+\.\d+(\.\d+)?', lambda m: m.group(1) + ver, tmpl, count=1)
    def dt(m):
        mon = re.search(r'[A-Za-z]+', m.group(0)).group(0)
        return '3 Oktober 2026' if len(mon) > 4 else '3 Okt 2026'
    h = re.sub(r'\d{1,2} [A-Za-z]{3,9} \d{4}', dt, h, count=1)
    h = re.sub(r'\d{4}-\d{2}-\d{2}', '2026-10-03', h, count=1)
    return h

out, added = [], []
for ver, mark, items in VERS:
    if mark not in ix:
        continue
    if any(l.lstrip().startswith('#') and re.search(r'\bv?' + re.escape(ver) + r'\b', l) for l in lines):
        continue
    out.append(make_heading(ver))
    if blank_after: out.append('')
    out += [bullet + x for x in items]
    out.append('')
    added.append(ver)

if not added:
    print('Tidak ada entri baru, CHANGELOG sudah lengkap.')
    sys.exit(0)

new = lines[:hidx] + out + lines[hidx:]
shutil.copyfile(cl_path, cl_path + '.bak-cl')
open(cl_path, 'w', encoding='utf-8', newline='').write(nl.join(new))
print('Entri ditambah: ' + ', '.join('v' + v for v in added) + '. Backup: ' + cl_path + '.bak-cl')
print('--- 12 baris teratas dari bagian baru ---')
print('\n'.join(out[:12]))
