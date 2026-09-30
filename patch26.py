import sys, shutil, os

files = [f for f in ("index.html", "www/index.html") if os.path.exists(f)]
if not files:
    sys.exit("index.html gak ketemu, cd dulu ke folder repo")

BLOCK = r'''<script>
(function () {
  var KEY = 'pancingmania_save_v1';
  function C() { return window.__PMC; }
  function flush() {
    try { if (C() && C().save) localStorage.setItem(KEY, JSON.stringify(C().save)); } catch (e) {}
  }
  document.addEventListener('visibilitychange', function () { if (document.hidden) flush(); });
  window.addEventListener('pagehide', flush);
  setInterval(flush, 15000);
  var wl = null;
  function lockScreen() {
    try {
      if ('wakeLock' in navigator && !wl) {
        navigator.wakeLock.request('screen').then(function (l) {
          wl = l; l.addEventListener('release', function () { wl = null; });
        }).catch(function () {});
      }
    } catch (e) {}
  }
  document.addEventListener('visibilitychange', function () { if (!document.hidden) lockScreen(); });
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (t && t.classList && t.classList.contains('modalOverlay') && t.id !== 'modalUpdate') t.classList.remove('show');
  });
  function dstr(d) { return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }
  function dailyBonus() {
    var c = C(); if (!c) return;
    var s = c.save, today = dstr(new Date()), yest = dstr(new Date(Date.now() - 86400000));
    if (s.loginDay === today) return;
    s.loginStreak = (s.loginDay === yest) ? (s.loginStreak || 0) + 1 : 1;
    s.loginDay = today;
    var n = Math.min(s.loginStreak, 7), coins = 40 * n + 10 * (s.level || 1);
    s.coins += coins; c.persist(); c.refresh();
    c.toast('Bonus login hari ke-' + s.loginStreak + ': +' + coins + ' koin');
    c.Sfx.sell();
  }
  var sb = document.getElementById('startBtn');
  if (sb) sb.addEventListener('click', function () {
    lockScreen();
    setTimeout(dailyBonus, 1200);
  });
})();
</script>'''

LOG = '''var LOG = [
    ["Update v2.6", ["Save otomatis tiap 15 detik dan langsung tersimpan saat app di-minimize.", "Layar tidak mati lagi saat mancing.", "Game berhenti sementara saat menu terbuka.", "Tap area gelap di luar menu buat menutupnya.", "Bonus login harian dengan streak sampai 7 hari."]],
'''

EDITS = [
    ('<div id="versionBadge">v2.5</div>', '<div id="versionBadge">v2.6</div>'),
    ("var VER = 'v2.5', DATE = '30 Sep 2026'", "var VER = 'v2.6', DATE = '1 Okt 2026'"),
    ('var LOG = [\n', LOG),
    ('      updateFishing(dt);\n      updateCamera();',
     '      if (!document.querySelector(".modalOverlay.show")) updateFishing(dt);\n      updateCamera();'),
    ('</body>', BLOCK + '\n</body>'),
]

for f in files:
    src = open(f, encoding='utf-8').read()
    if 'Update v2.6' in src:
        print(f, '-> sudah v2.6, dilewati'); continue
    ok = True
    for a, b in EDITS:
        if src.count(a) != 1:
            print(f, '-> GAGAL, pola gak cocok:', a[:40].strip()); ok = False; break
        src = src.replace(a, b)
    if not ok: continue
    shutil.copy(f, f + '.bak')
    open(f, 'w', encoding='utf-8').write(src)
    print(f, '-> OK (backup:', f + '.bak)')
