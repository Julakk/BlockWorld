#!/usr/bin/env python3
# Patch v4.1 - Akuarium pasif, trofi baru, gelar trofi
# Pakai: python3 patch_v41.py index.html
import sys, shutil, re, os, subprocess, tempfile

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()

if 'PM_V41' in src:
    print('Patch v4.1 sudah terpasang, tidak ada yang diubah.')
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

# ---------- 1. trofi baru (ditambah di AKHIR supaya progres lama aman) ----------
OLD_ACH = "['Aquarist', 'Pajang 6 ikan di Akuarium', 6, 600, function () { return (S().aqua || []).length; }]"
NEW_ACH = OLD_ACH + r""",
    ['Veteran Dermaga', 'Tangkap 1.000 ikan', 1000, 3000, function () { return st().catches; }],
    ['Raja Pancing', 'Tangkap 5.000 ikan', 5000, 12000, function () { return st().catches; }],
    ['Pemburu Epik', 'Tangkap 25 ikan Epik atau lebih', 25, 2500, function () { return rc(3); }],
    ['Pemburu Legenda', 'Tangkap 10 ikan Legendaris atau lebih', 10, 6000, function () { return rc(4); }],
    ['Kolektor Mitos', 'Tangkap 5 ikan Mitos', 5, 10000, function () { return rc(5); }],
    ['Pemburu Rahasia', 'Tangkap 3 ikan Rahasia', 3, 40000, function () { return st().secret; }],
    ['Ahli Mutasi', 'Tangkap 100 ikan mutasi', 100, 5000, function () { return st().mut; }],
    ['Penjelajah Samudra', 'Tangkap 50 ikan Laut Dalam', 50, 3000, function () { return st().deep; }],
    ['Level 40', 'Capai Level 40', 40, 5000, function () { return S().level; }],
    ['Level 60', 'Capai Level 60', 60, 12000, function () { return S().level; }],
    ['Kaya Raya', 'Punya 100.000 koin', 100000, 5000, function () { return S().coins; }],
    ['Sultan', 'Punya 1.000.000 koin', 1000000, 25000, function () { return S().coins; }],
    ['Terlahir Kembali', 'Lakukan 1 Rebirth', 1, 5000, function () { return S().rebirth || 0; }],
    ['Reinkarnasi', 'Lakukan 5 Rebirth', 5, 25000, function () { return S().rebirth || 0; }],
    ['Pecinta Hewan', 'Kumpulkan 3 jenis Pet', 3, 3000, function () { return Object.keys(S().pets || {}).length; }],
    ['Bos Akuarium', 'Kumpulkan 10.000 koin dari Akuarium', 10000, 4000, function () { return S().aquaEarned || 0; }]"""
replace_once(OLD_ACH, NEW_ACH, 'daftar trofi')

# ---------- 2. gelar trofi ----------
GELAR = r"""/* PM_V41 gelar trofi */
  var GELAR = [[0, 'Pemancing Baru'], [5, 'Pemancing Handal'], [10, 'Ahli Pancing'], [16, 'Pakar Laut'], [22, 'Legenda Pancing'], [28, 'Penguasa Samudra']];
  function achTitle(n) { var t = GELAR[0][1]; GELAR.forEach(function (g) { if (n >= g[0]) t = g[1]; }); if (n >= ACH.length) t = 'Maestro Samudra'; return t; }
  window.PMTitle = function () { var s = S(), n = 0; Object.keys(s.ach || {}).forEach(function (k) { if (s.ach[k]) n++; }); return achTitle(n); };
  var mT = mkModal('modalTrofi', 'Trofi');"""
replace_once("var mT = mkModal('modalTrofi', 'Trofi');", GELAR, 'blok gelar')
replace_once(
    "mT.foot.textContent = n + '/' + ACH.length + ' trofi';",
    "mT.foot.textContent = n + '/' + ACH.length + ' trofi • Gelar: ' + achTitle(n);",
    'footer trofi')

# ---------- 3. akuarium pasif ----------
AQ_HELP = r"""/* PM_V41 akuarium pasif */
  var AQ_RATE = 0.005, AQ_CAP_MIN = 480;
  function aqRate() { var r = 0; (S().aqua || []).forEach(function (e) { r += Math.max(1, Math.round(e.fish.value * ((e.mutation && e.mutation.mult) || 1) * AQ_RATE)); }); return r; }
  function aqAccrue() {
    var s = S(), now = Date.now(), rate = aqRate(), cap = rate * AQ_CAP_MIN, bank = s.aquaBank || 0;
    if (!s.aquaT || s.aquaT > now) s.aquaT = now;
    var el = (now - s.aquaT) / 60000; s.aquaT = now;
    s.aquaBank = bank + Math.max(0, Math.min(rate * el, cap - bank));
    return { rate: rate, cap: cap, bank: Math.floor(s.aquaBank) };
  }
  function aqHtml() {
    var a = aqAccrue();
    return '<div class="rowItem"><div class="rowInfo"><div class="rowName">Pemasukan Akuarium</div><div class="rowSub">' + a.rate + ' koin/menit • Tersimpan ' + a.bank + '/' + a.cap + ' (maks 8 jam)</div></div><button class="rowBtn" data-collect="1"' + (a.bank < 1 ? ' disabled' : '') + '>Ambil ' + a.bank + '</button></div>';
  }
  var mA = mkModal('modalAqua', 'Akuarium');"""
replace_once("var mA = mkModal('modalAqua', 'Akuarium');", AQ_HELP, 'helper akuarium')
replace_once(
    "var h = '<div class=\"rowName\">Dipajang (' + s.aqua.length + '/' + AQ.max + ')</div>';",
    "var h = aqHtml() + '<div class=\"rowName\" style=\"margin-top:6px\">Dipajang (' + s.aqua.length + '/' + AQ.max + ')</div>';",
    'render akuarium')
COLLECT = r"""if (!b || b.disabled) return; var s = S(); aqAccrue();
    if (b.dataset.collect) {
      var g = Math.floor(s.aquaBank || 0); if (g < 1) return;
      s.aquaBank -= g; s.coins += g; s.aquaEarned = (s.aquaEarned || 0) + g;
      C.Sfx.sell(); C.toast('+' + g + ' koin dari Akuarium'); C.persist(); C.refresh(); renderA(); checkAch(); return;
    }"""
replace_once("if (!b || b.disabled) return; var s = S();", COLLECT, 'klik ambil koin')

# ---------- 4. Info Update + versi ----------
NEW_LOG = r"""  var LOG = [
    ["Update v4.1", [
      "Akuarium sekarang menghasilkan koin pasif. Makin mahal ikan yang dipajang, makin besar pemasukannya. Tersimpan sampai 8 jam, ambil lewat tombol di Akuarium.",
      "16 trofi baru, mulai dari Veteran Dermaga sampai Bos Akuarium.",
      "Gelar baru berdasarkan jumlah trofi, dari Pemancing Baru sampai Maestro Samudra, tampil di bagian bawah Trofi."
    ]],
"""
if s.count("  var LOG = [\n") != 1:
    errors.append('awal LOG: ketemu %d kali (harus 1)' % s.count("  var LOG = [\n"))
else:
    s = s.replace("  var LOG = [\n", NEW_LOG, 1)
s, n1 = re.subn(r"var VER = 'v[0-9.]+',", "var VER = 'v4.1',", s)
s, n2 = re.subn(r'<div id="versionBadge">v[0-9.]+</div>', '<div id="versionBadge">v4.1</div>', s)
if n1 != 1: errors.append('VER: ketemu %d kali' % n1)
if n2 != 1: errors.append('badge versi: ketemu %d kali' % n2)

if errors:
    print('GAGAL, file TIDAK diubah:')
    for e in errors: print(' -', e)
    sys.exit(1)

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
else:
    print('node tidak ada, cek sintaks dilewati.')

s = s.replace('/* PM_V41 gelar trofi */', '/* PM_V41 gelar trofi */', 1)
shutil.copyfile(path, path + '.bak-v41')
open(path, 'w', encoding='utf-8').write(s)
print('Patch v4.1 terpasang. Backup: ' + path + '.bak-v41')
