#!/usr/bin/env python3
# v4.16: skin rod lebih redup, Gacha (tampilan + sistem) diupdate, Info Update diganti, CHANGELOG.md diupdate
import os, re, sys, shutil

D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, 'index.html')
BAK = P + '.bak_v416'
CL = os.path.join(D, 'CHANGELOG.md')


def die(m):
    print('GAGAL:', m)
    sys.exit(1)


def rep(t, old, new):
    c = t.count(old)
    if c != 1:
        die('anchor ketemu %d kali (harus 1): %s' % (c, old[:90]))
    return t.replace(old, new)


def cut(t, a, b, new):
    i = t.find(a)
    if i < 0:
        die('awal tidak ketemu: ' + a[:90])
    j = t.find(b, i)
    if j < 0:
        die('akhir tidak ketemu: ' + b[:90])
    return t[:i] + new + t[j:]


def block(t, a, b, fn):
    i = t.find(a)
    if i < 0:
        die('penanda tidak ketemu: ' + a)
    j = t.find(b, i)
    if j < 0:
        die('penanda tidak ketemu: ' + b)
    j += len(b)
    return t[:i] + fn(t[i:j]) + t[j:]


if not os.path.exists(P):
    die('index.html nggak ada di ' + D)
src = open(P, encoding='utf-8').read()
if "var VER = 'v4.15'" not in src:
    die('index.html bukan v4.15 (mungkin patch ini sudah pernah jalan)')

# ---------------------------------------------------------------- JS baru

ROLL = r"""  var SOFT_START = 45, SOFT_STEP = 4, EPIC_PITY = 20;
  function rateNow(n) { // n = pull ke-berapa sejak Legendary terakhir
    var lw = TIER.legendary.w;
    if (n >= SOFT_START) lw = Math.min(50, lw + (n - SOFT_START + 1) * SOFT_STEP);
    return { common: TIER.common.w - (lw - TIER.legendary.w), rare: TIER.rare.w, epic: TIER.epic.w, legendary: lw };
  }
  function rollTier(min, n) {
    var w = rateNow(n), r = Math.random() * 100, acc = 0, t = 'common';
    for (var i = 0; i < ORDER.length; i++) { acc += w[ORDER[i]]; if (r < acc) { t = ORDER[i]; break; } }
    if (ORDER.indexOf(t) < ORDER.indexOf(min)) t = min;
    return t;
  }
"""

PULL = r"""  function pull(n) {
    var s = C.save, cost = n === 1 ? COST1 : COST10;
    if (busy) return;
    if (s.coins < cost) { C.toast('Koin kurang, butuh ' + fmt(cost)); return; }
    s.coins -= cost;
    var g = s.gacha = s.gacha || { pity: 0, total: 0 }, out = [], best = 0, bi = 0, i;
    g.epicPity = g.epicPity || 0;
    for (i = 0; i < n; i++) {
      g.pity++; g.total++; g.epicPity++;
      var min = (n === 10 && i === 9) ? 'rare' : 'common';
      if (g.epicPity >= EPIC_PITY) min = 'epic';
      var t = g.pity >= PITY_MAX ? 'legendary' : rollTier(min, g.pity);
      if (t === 'legendary') g.pity = 0;
      if (ORDER.indexOf(t) >= 2) g.epicPity = 0;
      var r = reward(t); apply(r); out.push(r);
      if (ORDER.indexOf(t) > best) { best = ORDER.indexOf(t); bi = i; }
    }
    C.persist(); C.refresh(); C.Sfx.tap();
    st.last = out; st.best = ORDER[best]; st.bestRes = out[bi];
    if (s.gachaSkip) {
      st.anim = false; busy = false;
      C.Sfx.catchFish(st.best);
      C.vibe(st.best === 'legendary' ? [100, 50, 100, 50, 160] : (st.best === 'epic' ? [60, 40, 60] : [30]));
      stageShow(out[bi]); render();
      return;
    }
    st.anim = true; busy = true;
    render();
    clearTimeout(animT);
    if (!stagePlay(out[bi])) animT = setTimeout(finish, 900);
    clearTimeout(safeT); safeT = setTimeout(finish, 7000);
  }
"""

RENDER = r"""  function summary(list) {
    var coins = 0, skins = 0, dup = 0, baits = 0, p = [];
    list.forEach(function (r) {
      if (r.kind === 'coin') coins += r.coins;
      else if (r.kind === 'bait') baits++;
      else if (r.dup) { dup++; coins += r.coins; }
      else skins++;
    });
    if (skins) p.push(skins + ' skin baru');
    if (baits) p.push(baits + ' bait baru');
    if (dup) p.push(dup + ' duplikat');
    p.push('+' + fmt(coins) + ' koin');
    return p.join(' \u2022 ');
  }
  function stageShow(res) { // tampilkan hadiah terbaik di panggung tanpa animasi kapsul
    if (!s3init()) return;
    stageReset(); S3.mode = 'preview';
    setCol(new T.Color(TIER[res.tier].c));
    S3.pvTier = ORDER.indexOf(res.tier);
    S3.rew = buildReward(res); if (S3.rew.disp) S3.disp.push(S3.rew.disp);
    S3.rew.group.scale.setScalar(S3.rew.base); S3.root.add(S3.rew.group);
    S3.pl.intensity = 0.8;
    var n = $('gcRName'); n.textContent = TIER[res.tier].n.toUpperCase() + ' \u2022 ' + rewardName(res); n.style.color = TIER[res.tier].c;
    s3run();
  }
  function render() {
    var s = C.save, g = s.gacha || { pity: 0, total: 0 }, h = '', a = '', i;
    var gp = g.pity || 0, ep = g.epicPity || 0, rt = rateNow(gp + 1);
    var tp = ov.querySelectorAll('.gcTab');
    for (i = 0; i < tp.length; i++) tp[i].className = 'gcTab' + (tp[i].getAttribute('data-tab') === st.tab ? ' on' : '');
    if (st.tab === 'pull') {
      h += '<div class="gcPity">' +
        '<div class="gcPb"><span><b style="color:' + TIER.legendary.c + '">Legendary</b><em>' + gp + '/' + PITY_MAX + '</em></span><div class="bar"><i style="width:' + Math.min(100, gp / PITY_MAX * 100) + '%;background:' + TIER.legendary.c + '"></i></div></div>' +
        '<div class="gcPb"><span><b style="color:' + TIER.epic.c + '">Epic+</b><em>' + ep + '/' + EPIC_PITY + '</em></span><div class="bar"><i style="width:' + Math.min(100, ep / EPIC_PITY * 100) + '%;background:' + TIER.epic.c + '"></i></div></div></div>';
      if (st.anim) {
        h += '<div class="gcInfo"><b>Mengundi...</b> ketuk panggung buat lewati</div>';
      } else if (st.last) {
        h += '<div class="gcSum">' + summary(st.last) + '</div><div class="gcGrid">';
        for (i = 0; i < st.last.length; i++) h += card(st.last[i], i);
        h += '</div>';
      }
      h += '<div class="gcH">Peluang saat ini</div><div class="gcRates">';
      ORDER.forEach(function (key) {
        var t = TIER[key];
        h += '<div class="gcRate" style="--rc:' + t.c + '"><b>' + t.n + '</b><span class="p">' + (Math.round(rt[key] * 10) / 10) + '%</span><span class="d">' + t.d + '</span></div>';
      });
      h += '</div>';
      h += '<div class="gcInfo">Soft pity Legendary mulai pull ke-' + SOFT_START + ' (peluang naik tiap pull), dijamin di pull ke-' + PITY_MAX + '. Epic atau lebih dijamin tiap ' + EPIC_PITY + ' pull. Gacha 10x: pull ke-10 minimal Rare. Skin duplikat jadi koin (Rare ' + DUP.rare + ', Epic ' + DUP.epic + ', Legendary ' + DUP.legendary + ').</div>';
      a = '<div class="gcBtns"><button class="gcPull" type="button" data-act="p1"' + ((busy || s.coins < COST1) ? ' disabled' : '') + '>Gacha 1x<small>' + fmt(COST1) + ' koin</small></button>' +
        '<button class="gcPull gold" type="button" data-act="p10"' + ((busy || s.coins < COST10) ? ' disabled' : '') + '>Gacha 10x<small>' + fmt(COST10) + ' koin \u2022 Hemat</small></button></div>' +
        '<button class="gcSkipBtn' + (s.gachaSkip ? ' on' : '') + '" type="button" data-act="sk">Lewati animasi: ' + (s.gachaSkip ? 'ON' : 'OFF') + '</button>';
      $('gcFoot').textContent = 'Total pull: ' + fmt(g.total || 0);
    } else {
      var owned = 0;
      h += '<div class="gcInfo">Ketuk skin yang dimiliki buat lihat preview 3D-nya di panggung.</div>';
      h += '<button class="rowBtn" type="button" data-act="un"' + (s.skin ? '' : ' disabled') + ' style="width:100%;margin-bottom:8px">Tanpa Skin</button>';
      SKINS.forEach(function (sk) {
        var has = !!(s.skins && s.skins[sk.id]), on = s.skin === sk.id, t = TIER[sk.t];
        if (has) owned++;
        h += '<div class="rowItem' + (has ? '' : ' gcLocked') + '" data-act="pv" data-id="' + sk.id + '" style="border-color:' + t.c + '">' + thumbHtml(sk) +
          '<div class="rowInfo"><div class="rowName" style="color:' + t.c + '">' + (has ? sk.n : '???') + '</div><div class="rowSub">' + t.n + ' \u2022 ' + KIND_LABEL[sk.k] + '</div></div>' +
          '<button class="rowBtn' + (on ? ' owned' : '') + '" type="button"' + (has && !on ? ' data-act="eq" data-id="' + sk.id + '"' : ' disabled') + '>' + (on ? 'Dipakai' : (has ? 'Pakai' : 'Terkunci')) + '</button></div>';
      });
      $('gcFoot').textContent = 'Terkumpul ' + owned + '/' + SKINS.length;
    }
    var act = $('gcAct'); act.innerHTML = a; act.style.display = a ? 'block' : 'none';
    $('gcCoins').textContent = 'Koin: ' + fmt(s.coins);
    body.innerHTML = h;
  }

"""

CSS2 = r"""  var css2 = document.createElement('style');
  css2.textContent = [
    '#gcAct{flex:none;display:none;padding:6px 14px 8px;border-top:2px dashed rgba(255,255,255,.2);background:rgba(0,0,0,.2)}',
    '.gcRates{grid-template-columns:1fr 1fr;gap:5px;margin-bottom:8px}',
    '.gcRate{flex-wrap:wrap;gap:1px 6px;padding:5px 9px;font-size:10px}',
    '.gcRate b{min-width:0;font-size:11.5px}',
    '.gcRate .p{margin-left:auto;font-size:12.5px}',
    '.gcRate .d{flex-basis:100%;font-size:9.5px;color:var(--text-dim);line-height:1.25}',
    '.gcBtns{margin-bottom:6px}',
    '.gcPull{padding:8px 4px;font-size:13.5px;border-width:2.5px;border-radius:16px}',
    '.gcPull small{margin-top:1px}',
    '.gcSkipBtn{width:100%;padding:5px;border-radius:999px;border:2px solid rgba(255,255,255,.3);background:rgba(255,255,255,.07);color:var(--text-dim);font-size:10.5px;font-weight:800;font-family:inherit}',
    '.gcSkipBtn.on{border-color:var(--ok);color:var(--ok);background:rgba(76,232,138,.12)}',
    '.gcPity{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}',
    '.gcPb span{display:flex;justify-content:space-between;align-items:baseline;font-size:10.5px;font-weight:900;margin-bottom:2px}',
    '.gcPb em{font-style:normal;color:var(--text-dim)}',
    '.gcPb .bar{height:7px;border-radius:999px;background:rgba(0,0,0,.45);border:1.5px solid rgba(255,255,255,.4);overflow:hidden}',
    '.gcPb .bar i{display:block;height:100%;transition:width .3s}',
    '.gcSum{font-size:11px;font-weight:800;color:var(--gold);margin:2px 0 6px;text-align:center}',
    '@media (orientation:landscape) and (max-height:520px){.gcTabs{padding:4px 12px 6px}.gcTab{padding:6px}#gcAct{padding:5px 12px 6px}.gcBox{max-height:96vh;max-height:96dvh}}'
  ].join('');
  document.head.appendChild(css2);
"""

LOG = r"""  var LOG = [
    ["Update v4.16", [
      "Skin rod diredupkan: aura, halo, kilau ujung, dan partikel tidak lagi menyilaukan. Warna skin tetap jelas. Glow benang juga dikurangi sedikit.",
      "Tampilan Gacha dirapikan: tombol Gacha 1x dan 10x sekarang selalu kelihatan di bawah, tidak terpotong lagi di layar landscape. Daftar peluang jadi ringkas 2 kolom.",
      "Ada penanda pity Legendary dan Epic, plus ringkasan hasil tarikan (skin baru, bait, duplikat, total koin).",
      "Soft pity Legendary: mulai pull ke-45 peluangnya naik tiap pull, tetap dijamin di pull ke-60. Daftar peluang menampilkan angka yang berlaku saat ini.",
      "Pity Epic baru: tiap 20 pull tanpa Epic atau lebih, pull berikutnya dijamin minimal Epic.",
      "Tombol Lewati animasi: hasil langsung tampil di panggung 3D tanpa nunggu kapsul pecah. Pilihanmu tersimpan di save.",
      "Progres pity lama tetap aman, tersimpan di save yang sama."
    ]]
  ];
"""

ENTRY = """## v4.16 - 4 Okt 2026

- Skin rod diredupkan: aura, halo, kilau ujung, dan partikel tidak lagi menyilaukan. Warna skin tetap jelas. Glow benang juga dikurangi sedikit.
- Tampilan Gacha dirapikan: tombol Gacha 1x dan 10x sekarang selalu kelihatan di bawah, tidak terpotong lagi di layar landscape. Daftar peluang jadi ringkas 2 kolom.
- Ada penanda pity Legendary dan Epic, plus ringkasan hasil tarikan (skin baru, bait, duplikat, total koin).
- Soft pity Legendary: mulai pull ke-45 peluangnya naik tiap pull (sampai maksimal 50%), tetap dijamin di pull ke-60. Daftar peluang menampilkan angka yang berlaku saat ini.
- Pity Epic baru: tiap 20 pull tanpa Epic atau lebih, pull berikutnya dijamin minimal Epic.
- Tombol Lewati animasi: hasil langsung tampil di panggung 3D tanpa nunggu kapsul pecah. Pilihanmu tersimpan di save.
- Progres pity lama tetap aman, tersimpan di save yang sama.
- Info Update dalam game diganti dengan catatan v4.16.

"""

# ---------------------------------------------------------------- blok Gacha


def gacha(t):
    # skin lebih redup
    t = rep(t, "m.emissiveIntensity = k === 'rainbow' ? 0.45 : (k === 'fire' ? 0.9 : 0.8);", "m.emissiveIntensity = k === 'rainbow' ? 0.3 : (k === 'fire' ? 0.55 : 0.5);")
    t = rep(t, "m.emissiveIntensity = 0.5; m.roughness = 0.22;", "m.emissiveIntensity = 0.35; m.roughness = 0.22;")
    t = rep(t, "m.emissiveIntensity = 0.7 + 0.3 * Math.sin(t * 17) * Math.sin(t * 5.3);", "m.emissiveIntensity = 0.45 + 0.15 * Math.sin(t * 17) * Math.sin(t * 5.3);")
    t = rep(t, "m.emissiveIntensity = 0.65 + 0.2 * Math.sin(t * 1.7);", "m.emissiveIntensity = 0.4 + 0.12 * Math.sin(t * 1.7);")
    t = rep(t, "m.emissiveIntensity = 0.42 + 0.3 * Math.sin(t * 3);", "m.emissiveIntensity = 0.3 + 0.18 * Math.sin(t * 3);")
    t = rep(t, "var OP = { solid: 0.3, glow: 0.6, rainbow: 0.7, fire: 0.85, galaxy: 0.8 };", "var OP = { solid: 0.22, glow: 0.4, rainbow: 0.45, fire: 0.55, galaxy: 0.5 };")
    t = rep(t, "fs = isL ? 0.7 : 0.5,", "fs = isL ? 0.45 : 0.32,")
    t = rep(t, "map: dotTex(), color: hc, blending: T.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.8, fog: false", "map: dotTex(), color: hc, blending: T.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.45, fog: false")
    t = rep(t, "map: starTex(), color: hc, blending: T.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.9, fog: false", "map: starTex(), color: hc, blending: T.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.55, fog: false")
    # sistem
    t = cut(t, "  function rollTier(min) {", "  function reward(tier) {", ROLL)
    t = cut(t, "  function pull(n) {", "  function finish() {", PULL)
    t = cut(t, "  function render() {", "  /* ---------- panggung 3D", RENDER)
    # tampilan
    t = rep(t, "'<div class=\"modalBody\" id=\"gcBody\"></div></div></div>' +", "'<div class=\"modalBody\" id=\"gcBody\"></div><div id=\"gcAct\"></div></div></div>' +")
    t = rep(t, "document.head.appendChild(css);", "document.head.appendChild(css);\n" + CSS2.rstrip('\n'))
    t, n = re.subn(r"body\.addEventListener\('click',\s*function \(e\) \{(\s*)var b = e\.target\.closest\('\[data-act\]'\);",
                   lambda m: "$('gcSide').addEventListener('click', function (e) {" + m.group(1) + "var b = e.target.closest('[data-act]');", t)
    if n != 1:
        die('listener tombol gacha tidak ketemu (%d)' % n)
    t, n = re.subn(r"if \(a === 'p1'\) pull\(1\); else if \(a === 'p10'\) pull\(10\);",
                   lambda m: m.group(0) + "\n    else if (a === 'sk') { C.save.gachaSkip = !C.save.gachaSkip; C.persist(); render(); }", t)
    if n != 1:
        die('aksi p1/p10 tidak ketemu (%d)' % n)
    return t


# ---------------------------------------------------------------- blok HD2 (skin lebih redup)


def hd2(t):
    R = [
        ("return vivid(out, 0.58); }", "return vivid(out, 0.5); }"),
        ("glowT = makeTube(0.06, true, 0.5);", "glowT = makeTube(0.05, true, 0.4);"),
        ("glowT.mesh.material.opacity = 0.42 + 0.14 * Math.sin(t * 5);", "glowT.mesh.material.opacity = 0.3 + 0.1 * Math.sin(t * 5);"),
        ("(sk.k === 'glow' ? 1.5 : 2.1)) : 0.9;", "(sk.k === 'glow' ? 1.2 : 1.6)) : 0.9;"),
        ("new T.PointsMaterial({ size: 0.17,", "new T.PointsMaterial({ size: 0.12,"),
        ("rimMat.opacity = 0.16 + 0.025 * idx + 0.07 * Math.sin(t * 2.4);", "rimMat.opacity = 0.08 + 0.012 * idx + 0.035 * Math.sin(t * 2.4);"),
        ("m.emissiveIntensity = 0.2 + 0.1 * Math.sin(t * 2.2) + 0.015 * idx; }", "m.emissiveIntensity = 0.1 + 0.05 * Math.sin(t * 2.2) + 0.008 * idx; }"),
        ("else m.emissiveIntensity *= 1.45;", "else m.emissiveIntensity *= 0.9;"),
        ("tGlow = mkSprite(0.85); tGlow.scale.set(0.5, 0.5, 1);", "tGlow = mkSprite(0.5); tGlow.scale.set(0.35, 0.35, 1);"),
        ("gs = (sk ? 0.85 : 0.4 + 0.02 * idx)", "gs = (sk ? 0.45 : 0.3 + 0.015 * idx)"),
        ("var s = mkSprite(0.7); s.position.y = y; s.scale.set(0.75, 0.75, 1);", "var s = mkSprite(0.4); s.position.y = y; s.scale.set(0.5, 0.5, 1);"),
        ("gs = (1.05 + 0.2 * Math.sin(t * 3 + i * 2))", "gs = (0.6 + 0.12 * Math.sin(t * 3 + i * 2))"),
        ("swarm = new T.Points(swGeo, new T.PointsMaterial({ size: 0.13,", "swarm = new T.Points(swGeo, new T.PointsMaterial({ size: 0.09,"),
        ("swGeo.attributes.position.needsUpdate = true; swGeo.attributes.color.needsUpdate = true;",
         "for (i = 0; i < SWN * 3; i++) swCol[i] *= 0.65;\n    swGeo.attributes.position.needsUpdate = true; swGeo.attributes.color.needsUpdate = true;"),
        ("o.material.size *= 2.4;", "o.material.size *= 1.3;"),
        ("o.scale.x *= 1.8; o.scale.z *= 1.8;", "o.scale.x *= 1.3; o.scale.z *= 1.3;"),
        ("if (o.scale.x < 2.2) { o.scale.x *= 1.9; o.scale.y *= 1.9; }", "if (o.scale.x < 2.2) { o.scale.x *= 1.1; o.scale.y *= 1.1; }"),
        ("m.opacity = Math.min(1, m.opacity * 2.1);", "m.opacity = Math.min(0.5, m.opacity);"),
    ]
    for a, b in R:
        t = rep(t, a, b)
    return t


new = block(src, '<!--PM-GACHA-START-->', '<!--PM-GACHA-END-->', gacha)
new = block(new, '<!--PM-HD2-START-->', '<!--PM-HD2-END-->', hd2)
new = rep(new, "var VER = 'v4.15', DATE = '4 Okt 2026', KEY = 'pm_seen_ver';", "var VER = 'v4.16', DATE = '4 Okt 2026', KEY = 'pm_seen_ver';")
new = cut(new, "  var LOG = [", "  var vb0 = document.getElementById('versionBadge');", LOG)

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
open(P, 'w', encoding='utf-8').write(new)
print('index.html -> v4.16 (backup: ' + os.path.basename(BAK) + ')')

# ---------------------------------------------------------------- CHANGELOG.md
if os.path.exists(CL):
    c = open(CL, encoding='utf-8').read()
    if '## v4.16' in c:
        print('CHANGELOG.md sudah punya v4.16, dilewati')
    else:
        m = re.search(r'^## ', c, re.M)
        c = (c[:m.start()] + ENTRY + c[m.start():]) if m else (c.rstrip('\n') + '\n\n' + ENTRY)
        open(CL, 'w', encoding='utf-8').write(c)
        print('CHANGELOG.md diupdate')
else:
    open(CL, 'w', encoding='utf-8').write('# Changelog\n\nSemua perubahan penting pada proyek ini dicatat di file ini. Diurutkan dari yang terbaru.\n\n' + ENTRY)
    print('CHANGELOG.md dibuat')

# ---------------------------------------------------------------- www (kalau ada salinan lama yang sama persis)
W = os.path.join(D, 'www', 'index.html')
if os.path.exists(W):
    if open(W, encoding='utf-8').read() == src:
        shutil.copyfile(P, W)
        print('www/index.html ikut diupdate')
    else:
        print('PERINGATAN: www/index.html beda dari index.html lama, tidak disentuh')
