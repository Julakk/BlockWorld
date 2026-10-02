# Patch Pancing Mania: animasi Secret lebih realistis + notif Secret ke semua player
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

# ---------- BUG 1: animasi ikan Secret ----------
h.rep(r'''fish.position.set(lerp(A.x, H.x, e), lerp(wy, H.y, e) + Math.sin(Math.PI * u) * 2.4, lerp(A.z, H.z, e));''',
      r'''fish.position.set(lerp(A.x, H.x, u), lerp(wy, H.y, u) + 4 * (kind === 'kraken' ? 2.6 : 3.2) * u * (1 - u), lerp(A.z, H.z, u));''',
      'lompatan balistik (gravitasi, bukan ease)')
h.rep(r'''fish.rotateZ(u * Math.PI * 2 * (kind === 'kraken' ? 0.5 : 1));''',
      r'''fish.rotateZ(Math.sin(t * 15) * 0.32 * (1 - 0.5 * u) + (kind === 'kraken' ? 0 : Math.sin(t * 6) * 0.15));''',
      'hapus muter 360 -> ikan meronta')
h.rep(r'''fish.scale.setScalar(lerp(Lleap, Lhold, e));''',
      r'''fish.scale.setScalar(lerp(Lleap, Lhold, bl(u, 0.55, 1)));''',
      'ukuran ikan nggak mengecil di udara')
h.rep(r'''if (fish.position.y > wy) emit(fish.position.x, fish.position.y, fish.position.z, 2, 1.0, 0.5, 0.8, 0.95, 1);''',
      r'''if (fish.position.y > wy) emit(fish.position.x, fish.position.y, fish.position.z, 4, 1.4, 0.2, 0.8, 0.95, 1);''',
      'tetesan air lebih banyak saat melompat')
h.rep(r'''if (parts.tail) parts.tail.rotation.y = Math.sin(time * 8) * 0.5;''',
      r'''if (parts.tail) parts.tail.rotation.y = Math.sin(time * 13) * 0.55;''',
      'ekor lebih cepat')
h.rep(r'''fish.quaternion.copy(qLeap).slerp(qHold, bl(th, 0, 0.6));''',
      r'''fish.quaternion.copy(qLeap).slerp(qHold, bl(th, 0, 0.6)); fish.rotateZ(Math.sin(th * 9) * 0.22 * (1 - u));''',
      'ikan masih meronta pas dipamerkan')
h.rep(r'''pTick = 0.035; const c = Math.random() < 0.5;''',
      r'''pTick = 0.035; if (Math.random() < 0.6) emit(fish.position.x + (Math.random() - 0.5) * 0.8, fish.position.y - 0.4, fish.position.z + (Math.random() - 0.5) * 0.8, 1, 0.25, 0, 0.7, 0.9, 1); const c = Math.random() < 0.5;''',
      'air menetes dari ikan')

# ---------- BUG 2: notif Secret ----------
h.rep(r'''z-index: 30; display: flex; flex-direction: column; align-items: center; gap: 7px; pointer-events: none; }''',
      r'''z-index: 60; display: flex; flex-direction: column; align-items: center; gap: 7px; pointer-events: none; }''',
      'toast di atas layar sinematik')
h.rep(r'''if (m.id !== myId) C.toast('🌟 ' + m.name + ' dapat ' + (m.mut ? m.mut + ' ' : '') + m.fish + '!');''',
      r'''C.toast('🌟 ' + (m.id === myId ? 'Kamu' : m.name) + ' dapat ' + (m.mut ? m.mut + ' ' : '') + m.fish + (m.w ? ' (' + m.w + ' kg)' : '') + '!', 'secret');''',
      'notif pelangi buat semua (termasuk diri sendiri)')
h.rep(r'''window.PMNet = { secret: function (o) { send({ t: 'secret', id: o.id, w: Math.round((+o.w || 0) * 10) / 10, mut: o.mut ? String(o.mut).slice(0, 20) : '' }); } };''',
      r'''var pendSec = [];
    function flushSec() { while (pendSec.length && ws && ws.readyState === 1) send(pendSec.shift()); }
    window.PMNet = { secret: function (o) {
      var p = { t: 'secret', id: o.id, w: Math.round((+o.w || 0) * 10) / 10, mut: o.mut ? String(o.mut).slice(0, 20) : '' };
      if (ws && ws.readyState === 1) send(p); else { pendSec.push(p); if (pendSec.length > 3) pendSec.shift(); }
    } };''',
      'antrian kirim kalau lagi putus koneksi')
h.rep(r'''(m.secrets || []).forEach(function (x) { addSecret(x, true); }); setBadge(true, m.n); }''',
      r'''(m.secrets || []).forEach(function (x) { addSecret(x, true); }); setBadge(true, m.n); flushSec(); }''',
      'kirim antrian pas nyambung lagi')
h.done()

s = Patch('server/server.js')
s.rep(r'''t0 - (me.lastSecret || 0) < 30000''', r'''t0 - (me.lastSecret || 0) < 4000''', 'cooldown server 30 dtk -> 4 dtk')
s.done()
print('SELESAI. Restart server node di VPS, lalu build ulang APK.')
