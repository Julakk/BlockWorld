/* PM-START v1 - layar utama: preview karakter 3D, hadiah harian, tombol cepat, badge Discord */
(function () {
  'use strict';
  var C = window.__PMC, T = window.THREE;
  var ss = document.getElementById('startScreen'), btn = document.getElementById('startBtn');
  if (!C || !ss || !btn || window.__pmStart) return;
  window.__pmStart = true;

  var DISCORD = 'https://discord.gg/t7Y6ChGtPq';
  var SAVE_KEY = 'pancingmania_save_v1';
  var DEFAULT_SERVER = 'wss://game.ahmadfivem.my.id';
  var TIPS = [
    'Lepas tombol pas marker di zona Perfect buat peluang ikan langka naik.',
    'Malam hari dan hujan bikin ikan langka lebih gampang nyangkut.',
    'Ikan Rahasia harus ditarik manual, Auto Mancing gak bisa.',
    'Pajang ikan langka di Akuarium biar gak ikut kejual.',
    'Cek Pasar tiap hari, harga ikan berubah-ubah.',
    'Enchant rod di Altar buat nambah Luck dan Speed.',
    'Rebirth ngasih bonus permanen buat Luck, Speed, harga jual, dan XP.'
  ];
  var DC_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 6Q12 3 19.5 6L22 16.5Q19 18.8 16.5 19.5L15.5 17.8Q12 19 8.5 17.8L7.5 19.5Q5 18.8 2 16.5Z" fill="#fff"/><circle cx="8.7" cy="12.3" r="1.8" fill="#5865F2"/><circle cx="15.3" cy="12.3" r="1.8" fill="#5865F2"/></svg>';

  function $(id) { return document.getElementById(id); }
  function el(tag, cls) { var e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function safe(fn) { try { fn(); } catch (e) { console.warn('PM-START:', e); } }
  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) {} return null; }
  function fmt(n) { return String(Math.round(+n || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function dstr(d) { return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }
  function vis() { return ss.style.display === 'flex'; }

  /* ---------- CSS ---------- */
  var css = document.createElement('style');
  css.textContent = [
    '#pmsSide{position:fixed;left:0;top:0;right:0;bottom:0;z-index:21;pointer-events:none;display:none}',
    '.pmsCard{position:absolute;top:50%;transform:translateY(-50%);width:clamp(118px,19vw,176px);padding:8px;box-sizing:border-box;pointer-events:auto;background:linear-gradient(160deg,rgba(29,80,104,.93),rgba(12,40,54,.93));border:3px solid rgba(255,255,255,.92);border-radius:16px;box-shadow:0 5px 0 rgba(0,0,0,.32),0 10px 18px rgba(0,0,0,.4);color:#fff;text-align:center;font-family:inherit}',
    '#pmsL{left:calc(10px + env(safe-area-inset-left,0px))}',
    '#pmsR{right:calc(10px + env(safe-area-inset-right,0px))}',
    '#pmsCv{display:block;width:100%;height:auto;border-radius:10px;background:radial-gradient(circle at 50% 35%,#2f6f8a,#0b1c28 78%);touch-action:none}',
    '.pmsName{font-size:12.5px;font-weight:900;margin:6px 0 1px;word-break:break-word}',
    '.pmsT{font-size:10.5px;font-weight:900;letter-spacing:.5px;color:var(--gold);text-transform:uppercase;margin-bottom:3px}',
    '.pmsSub{font-size:10.5px;color:#cfe6ec;line-height:1.35}',
    '.pmsBtn{width:100%;margin-top:6px;padding:7px 6px;border-radius:999px;border:2px solid #fff;font-weight:900;font-size:11.5px;color:#052730;background:linear-gradient(90deg,#37d1c8,#2f9fc9);box-shadow:0 3px 0 rgba(0,80,90,.45);font-family:inherit}',
    '.pmsBtn.gold{background:linear-gradient(160deg,#ffcf4d,#e0982a);color:#4a2600;box-shadow:0 3px 0 rgba(120,70,0,.5)}',
    '.pmsBtn:disabled{opacity:.55;box-shadow:none}',
    '.pmsBtn:active:not(:disabled){transform:translateY(2px)}',
    '.pmsDots{display:flex;justify-content:center;gap:4px;margin:4px 0}',
    '.pmsDots i{width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,.18);border:1.5px solid rgba(255,255,255,.4)}',
    '.pmsDots i.on{background:var(--gold);border-color:#fff}',
    '.pmsBar{height:8px;border-radius:999px;background:rgba(0,0,0,.45);border:1.5px solid rgba(255,255,255,.5);overflow:hidden;margin:3px 0}',
    '.pmsBar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--accent),#7fe8ff);transition:width .3s}',
    '.pmsNet{display:inline-block;font-size:10px;font-weight:800;padding:2px 8px;border-radius:999px;background:rgba(0,0,0,.38);border:1.5px solid rgba(255,255,255,.4);margin-bottom:6px}',
    '.pmsNews{display:none;margin-top:6px;font-size:10px;line-height:1.35;color:#ffe9a8;word-break:break-word}',
    '#pmsQuick{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;max-width:min(92vw,400px)}',
    '.pmsQ{display:inline-flex;align-items:center;gap:5px;padding:5px 10px;border-radius:999px;border:2px solid #fff;background:linear-gradient(160deg,#2fb8d1,#196c81);color:#fff;font-size:10.5px;font-weight:800;text-decoration:none;box-shadow:0 2px 0 rgba(0,0,0,.35),0 4px 8px rgba(0,0,0,.3);font-family:inherit;cursor:pointer;white-space:nowrap}',
    '.pmsQ:active{transform:translateY(2px)}',
    '.pmsDc{background:linear-gradient(160deg,#7983f5,#4752c4)}',
    '.pmsDc svg{width:14px;height:14px}',
    '#startScreen{padding-bottom:28px!important}',
    '#startSub{text-shadow:0 1px 4px rgba(0,0,0,.85)!important}',
    '#startTips.pmsTip1{padding:6px 14px!important;font-size:10.5px!important;line-height:1.4!important;max-width:min(92vw,360px)!important;border-radius:999px!important}',
    '.pmsStar{position:absolute;width:2px;height:2px;border-radius:50%;background:#fff;opacity:.8;animation:pmsTw 3s ease-in-out infinite}',
    '@keyframes pmsTw{50%{opacity:.2}}',
    '@media (prefers-reduced-motion:reduce){.pmsStar{animation:none}}',
    '@media (orientation:landscape) and (max-height:520px){#startTitle img{height:min(25vh,112px)!important}#startScreen{gap:6px!important}#startSub{font-size:12px!important;line-height:1.3!important;max-width:min(92vw,420px)!important}.pmsCard{width:clamp(112px,18vw,160px);padding:6px}}',
    '@media (max-aspect-ratio:1/1){#pmsL,#pmsR{display:none}}'
  ].join('');
  document.body.appendChild(css);

  /* ---------- akses tombol asli (Menu) ---------- */
  function origBtn(id, prefix) {
    var b = id ? $(id) : null;
    if (b) return b;
    var list = document.querySelectorAll('#menuPanel button, #hudPills button');
    for (var i = 0; i < list.length; i++) if ((list[i].textContent || '').trim().indexOf(prefix) === 0) return list[i];
    return null;
  }
  function openLB() {
    if (typeof window.PMOpenLB === 'function') window.PMOpenLB();
    else C.toast('Peringkat belum tersedia');
  }

  /* ---------- kartu kiri & kanan ---------- */
  var side = el('div'); side.id = 'pmsSide';
  var L = el('div', 'pmsCard'); L.id = 'pmsL';
  L.innerHTML = '<canvas id="pmsCv" width="150" height="180"></canvas><div class="pmsName" id="pmsName"></div><div class="pmsSub" id="pmsTitle"></div><div class="pmsSub" id="pmsMeta"></div>';
  var bLook = el('button', 'pmsBtn'); bLook.type = 'button'; bLook.textContent = 'Warna Karakter';
  L.appendChild(bLook);
  var R = el('div', 'pmsCard'); R.id = 'pmsR';
  R.innerHTML = '<div class="pmsNet" id="pmsNet">Mengecek server...</div><div class="pmsT">Hadiah Harian</div><div class="pmsSub" id="pmsDay"></div><div class="pmsDots" id="pmsDots"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div><div class="pmsSub" id="pmsCoin"></div>';
  var bClaim = el('button', 'pmsBtn gold'); bClaim.type = 'button'; R.appendChild(bClaim);
  var qh = el('div', 'pmsT'); qh.style.marginTop = '8px'; qh.textContent = 'Misi Harian'; R.appendChild(qh);
  var bar = el('div', 'pmsBar'); bar.innerHTML = '<i id="pmsBarFill"></i>'; R.appendChild(bar);
  var qs = el('div', 'pmsSub'); qs.id = 'pmsQuest'; R.appendChild(qs);
  var news = el('div', 'pmsNews'); news.id = 'pmsNews'; R.appendChild(news);
  side.appendChild(L); side.appendChild(R); document.body.appendChild(side);

  bLook.onclick = function () {
    if (window.PMLook && window.PMLook.open) window.PMLook.open();
    else { var o = origBtn(null, 'Warna Karakter'); if (o) o.click(); }
  };

  /* ---------- hadiah harian (rumus sama dengan bonus login lama) ---------- */
  function daily() {
    var s = C.save, today = dstr(new Date()), yest = dstr(new Date(Date.now() - 86400000));
    var claimed = s.loginDay === today;
    var streak = claimed ? (s.loginStreak || 1) : (s.loginDay === yest ? (s.loginStreak || 0) + 1 : 1);
    return { claimed: claimed, streak: streak, coins: 40 * Math.min(streak, 7) + 10 * (s.level || 1) };
  }
  function claim() {
    var d = daily(); if (d.claimed) return;
    var s = C.save;
    s.loginStreak = d.streak; s.loginDay = dstr(new Date()); s.coins += d.coins;
    C.persist(); C.refresh();
    C.Sfx.sell(); C.toast('Bonus login hari ke-' + d.streak + ': +' + d.coins + ' koin');
    render();
  }
  bClaim.onclick = claim;
  function quests() {
    var q = C.save.quests, today = dstr(new Date());
    if (q && q.v === 2 && q.day === today && q.list) {
      var done = 0; q.list.forEach(function (m) { if (m.done) done++; });
      return { done: done, total: q.list.length, fresh: false };
    }
    return { done: 0, total: 4, fresh: true };
  }

  /* ---------- chip status di tengah ---------- */
  var stats = el('div'); stats.id = 'startStats';
  var oldStats = $('startStats');
  if (oldStats) { oldStats.id = 'startStatsOld'; oldStats.style.display = 'none'; ss.insertBefore(stats, oldStats); }
  else ss.insertBefore(stats, btn);
  function chip(text) { var s = el('span'); s.textContent = text; stats.appendChild(s); }

  function render() {
    safe(function () {
      var s = C.save, n = Object.keys(s.discovered || {}).length;
      stats.textContent = '';
      chip('Level ' + s.level); chip(fmt(s.coins) + ' koin'); chip('Koleksi ' + n + '/' + C.FISH_TABLE.length);

      var prof = null; try { prof = JSON.parse(ls('pm_profile') || 'null'); } catch (e) {}
      $('pmsName').textContent = (prof && prof.name) || 'Tamu';
      $('pmsTitle').textContent = (typeof window.PMTitle === 'function') ? window.PMTitle() : '';
      var meta = [], ct = (s.stats && s.stats.catches) || 0;
      if (s.rebirth) meta.push('Rebirth ' + s.rebirth);
      if (ct) meta.push(fmt(ct) + ' tangkapan');
      $('pmsMeta').textContent = meta.join(' \u2022 ');

      var d = daily(), q = quests(), i, dots = $('pmsDots').children, done = d.claimed ? d.streak : d.streak - 1;
      $('pmsDay').textContent = 'Login hari ke-' + d.streak;
      for (i = 0; i < dots.length; i++) dots[i].className = i < Math.min(done, 7) ? 'on' : '';
      $('pmsCoin').textContent = d.claimed ? 'Sudah diklaim. Balik lagi besok!' : 'Bonus hari ini +' + fmt(d.coins) + ' koin';
      bClaim.textContent = d.claimed ? 'Sudah diklaim' : 'Klaim +' + fmt(d.coins);
      bClaim.disabled = d.claimed;
      $('pmsBarFill').style.width = (q.total ? q.done / q.total * 100 : 0) + '%';
      $('pmsQuest').textContent = q.fresh ? 'Misi baru menunggu (0/' + q.total + ')' : q.done + '/' + q.total + ' selesai';
    });
  }

  /* ---------- baris tombol cepat + badge Discord ---------- */
  var quick = el('div'); quick.id = 'pmsQuick';
  function qbtn(label, fn) { var b = el('button', 'pmsQ'); b.type = 'button'; b.textContent = label; b.onclick = fn; quick.appendChild(b); return b; }
  var qSnd, qVib, qUp;
  function sync() {
    var o = origBtn('btnSound', 'Suara'); if (o && qSnd) qSnd.textContent = o.textContent;
    o = origBtn(null, 'Getar'); if (o && qVib) qVib.textContent = o.textContent;
    o = origBtn('btnUpdInfo', 'Info Update'); if (o && qUp) qUp.textContent = o.textContent;
  }
  qbtn('Peringkat', openLB);
  qSnd = qbtn('Suara', function () { var o = origBtn('btnSound', 'Suara'); if (o) o.click(); sync(); });
  qVib = qbtn('Getar', function () { var o = origBtn(null, 'Getar'); if (o) o.click(); sync(); });
  qbtn('Backup', function () { var o = origBtn(null, 'Backup'); if (o) o.click(); });
  qUp = qbtn('Info Update', function () { var o = origBtn('btnUpdInfo', 'Info Update'); if (o) o.click(); sync(); });
  var qDc = el('a', 'pmsQ pmsDc'); qDc.href = DISCORD; qDc.target = '_blank'; qDc.rel = 'noopener noreferrer';
  qDc.innerHTML = DC_SVG + '<span>Discord</span>'; quick.appendChild(qDc);
  var tipsEl = $('startTips');
  ss.insertBefore(quick, tipsEl || null);

  /* ---------- tambahan di Menu dalam game ---------- */
  safe(function () {
    var menu = $('menuPanel'); if (!menu) return;
    var mLb = el('button', 'hudPill'); mLb.textContent = 'Peringkat';
    mLb.onclick = function () { menu.classList.remove('show'); openLB(); };
    var mDc = el('a', 'hudPill'); mDc.textContent = 'Discord'; mDc.href = DISCORD; mDc.target = '_blank'; mDc.rel = 'noopener noreferrer';
    mDc.style.cssText = 'text-decoration:none;background:linear-gradient(160deg,#7983f5,#4752c4);color:#fff;text-shadow:none';
    menu.appendChild(mLb); menu.appendChild(mDc);
  });

  /* ---------- LANJUTKAN vs MULAI ---------- */
  safe(function () {
    var s = C.save, has = !!s && (s.level > 1 || s.xp > 0 || Object.keys(s.discovered || {}).length > 0 || ((s.stats && s.stats.catches) || 0) > 0);
    btn.textContent = has ? '\u25B6 LANJUTKAN' : '\u25B6 MULAI MANCING';
  });

  /* ---------- tips: lengkap sekali, lalu satu baris ---------- */
  var tipI = Math.floor(Math.random() * TIPS.length);
  function showTip() { if (tipsEl) tipsEl.textContent = 'Tips: ' + TIPS[tipI % TIPS.length]; }
  if (tipsEl && ls('pm_tips_seen') === '1') { tipsEl.classList.add('pmsTip1'); showTip(); }
  setInterval(function () {
    if (vis() && tipsEl && tipsEl.classList.contains('pmsTip1')) { tipI++; showTip(); }
  }, 7000);

  /* ---------- langit mengikuti jam perangkat ---------- */
  var PAL = {
    dawn: { bg: 'linear-gradient(180deg,#2b3f7c 0%,#8a79b8 28%,#ffb08a 54%,#ffe0a8 66%,#2a6a8a 66.2%,#0b3a55 100%)', l: '50%', t: '66%', half: true, sun: 'radial-gradient(circle at 40% 35%,#fffbe0,#ffe08a 55%,#ffb24a)', glow: 'rgba(255,200,120,.5)' },
    day: { bg: 'linear-gradient(180deg,#1e6fd6 0%,#5aa9ec 36%,#a9d8fa 62%,#dff2ff 66%,#2a93c4 66.2%,#0d5f8c 100%)', l: '72%', t: '20%', half: false, sun: 'radial-gradient(circle at 40% 35%,#ffffff,#fff3b0 55%,#ffd24a)', glow: 'rgba(255,240,170,.6)' },
    dusk: { bg: 'linear-gradient(180deg,#1c3f7a 0%,#6a5a9e 28%,#f08a6a 52%,#ffc98a 66%,#0f5577 66.2%,#083049 100%)', l: '50%', t: '66%', half: true, sun: 'radial-gradient(circle at 40% 35%,#fff6c9,#ffd27a 55%,#ff9e4a)', glow: 'rgba(255,190,110,.5)' },
    night: { bg: 'linear-gradient(180deg,#050a1e 0%,#0b1836 40%,#1a2a4a 62%,#24385c 66%,#0a2a40 66.2%,#04131f 100%)', l: '80%', t: '20%', half: false, sun: 'radial-gradient(circle at 38% 36%,#ffffff,#dfe8ff 60%,#aebde6)', glow: 'rgba(170,190,255,.45)' }
  };
  var todNow = '';
  function applyTod() {
    var deco = $('startDeco'); if (!deco) return;
    var h = new Date().getHours();
    var k = (h >= 5 && h < 9) ? 'dawn' : (h >= 9 && h < 16) ? 'day' : (h >= 16 && h < 19) ? 'dusk' : 'night';
    if (k === todNow) return; todNow = k;
    var p = PAL[k], sun = deco.querySelector('.sun'), sz = 'clamp(64px,24vh,120px)', i;
    deco.style.background = p.bg;
    if (sun) {
      sun.style.cssText = 'left:' + p.l + ';top:' + p.t + ';margin:0;transform:translate(-50%,-50%);width:' + sz + ';height:' + sz + ';background:' + p.sun + ';box-shadow:0 0 60px 20px ' + p.glow + ';' + (p.half ? 'clip-path:inset(-120px -120px 50% -120px);' : 'animation:none;');
    }
    var old = deco.querySelectorAll('.pmsStar'); for (i = 0; i < old.length; i++) old[i].parentNode.removeChild(old[i]);
    if (k === 'night') {
      for (i = 0; i < 26; i++) {
        var st = el('i', 'pmsStar');
        st.style.left = (Math.random() * 100).toFixed(1) + '%'; st.style.top = (Math.random() * 58).toFixed(1) + '%';
        st.style.animationDelay = '-' + (Math.random() * 3).toFixed(1) + 's';
        deco.appendChild(st);
      }
    }
  }
  safe(applyTod);
  setInterval(function () { safe(applyTod); }, 300000);

  /* ---------- status server: online / maintenance / pengumuman ---------- */
  function srvBase() { return (ls('pm_server') || DEFAULT_SERVER).replace(/^ws/, 'http').replace(/\/+$/, ''); }
  function setNet(text, color) { var n = $('pmsNet'); n.textContent = text; n.style.color = color; }
  function setNews(t) { var n = $('pmsNews'); n.textContent = t ? '\uD83D\uDCE2 ' + t : ''; n.style.display = t ? 'block' : 'none'; }
  function poll() {
    if (!vis()) return;
    var ctl = ('AbortController' in window) ? new AbortController() : null;
    var to = setTimeout(function () { if (ctl) ctl.abort(); }, 5000);
    fetch(srvBase() + '/status', { signal: ctl ? ctl.signal : undefined })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        clearTimeout(to);
        if (j && j.maint) setNet('Maintenance', '#ffd24a');
        else if (j && typeof j.online === 'number') setNet(j.online + ' online', '#7bf08a');
        else setNet('Server aktif', '#7bf08a');
        setNews(j && typeof j.news === 'string' ? j.news.slice(0, 140) : '');
      })
      .catch(function () { clearTimeout(to); setNet('Server offline', '#ff9a8a'); setNews(''); });
  }
  setInterval(poll, 30000);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) poll(); });

  /* ---------- preview karakter 3D ---------- */
  var pv = { r: null, sc: null, cam: null, pivot: null, run: false, raf: 0, last: 0, drag: false, dx: 0, failed: false };
  function pvModel() {
    var P = C.player;
    while (pv.pivot.children.length) pv.pivot.remove(pv.pivot.children[0]);
    var g = P.clone(true); // material dibagi dengan karakter asli, jadi warna ikut live
    g.position.set(0, 0, 0); g.rotation.set(0, 0, 0); g.scale.set(1, 1, 1);
    g.traverse(function (o) {
      if (o.isSprite) { o.visible = false; return; }
      var gm = o.geometry, p = gm && gm.parameters;
      if (o.isMesh && p && gm.type === 'CylinderGeometry' && p.radiusTop === 0.014 && p.radiusBottom === 0.03) o.visible = false; // joran
    });
    g.children.forEach(function (o) { // pose berdiri lurus
      var gm = o.geometry, p = gm && gm.parameters;
      if (o.isMesh && p && gm.type === 'CylinderGeometry' && (p.radiusTop === 0.105 || (p.radiusTop === 0.08 && p.radiusBottom === 0.07))) {
        o.rotation.set(0, 0, 0);
        o.children.forEach(function (c) { if (c.isGroup) c.rotation.set(0, 0, 0); });
      } else if (o.isGroup && Math.abs(o.position.y - 1.3) < 0.03) o.rotation.set(0, 0, 0); // kepala
    });
    pv.pivot.add(g); pv.pivot.rotation.y = 0.5;
  }
  function pvInit() {
    if (pv.r) return true;
    if (pv.failed || !T) return false;
    var cv = $('pmsCv');
    try { pv.r = new T.WebGLRenderer({ canvas: cv, antialias: true, alpha: true }); }
    catch (e) { pv.failed = true; cv.style.display = 'none'; return false; }
    pv.r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    pv.r.setSize(150, 180, false);
    pv.r.setClearColor(0x000000, 0);
    pv.r.toneMapping = T.NoToneMapping;
    pv.sc = new T.Scene();
    pv.sc.add(new T.HemisphereLight(0xfff0dd, 0x3a4a5a, 1.0));
    var dl = new T.DirectionalLight(0xffe2c0, 0.55); dl.position.set(3, 5, 4); pv.sc.add(dl);
    pv.cam = new T.PerspectiveCamera(30, 150 / 180, 0.1, 50);
    pv.cam.position.set(0, 1.2, 4.6); pv.cam.lookAt(new T.Vector3(0, 0.95, 0));
    pv.pivot = new T.Group(); pv.sc.add(pv.pivot);
    pvModel();
    return true;
  }
  function pvFrame(t) {
    if (!pv.run) return;
    pv.raf = requestAnimationFrame(pvFrame);
    if (t - pv.last < 33) return; // ~30 fps cukup buat preview
    var dt = pv.last ? Math.min(0.1, (t - pv.last) / 1000) : 0; pv.last = t;
    if (!pv.drag) pv.pivot.rotation.y += dt * 0.9;
    pv.r.render(pv.sc, pv.cam);
  }
  function pvStart() {
    if (pv.run || !pvInit()) return;
    if (window.PMLook && window.PMLook.apply) window.PMLook.apply();
    pv.run = true; pv.last = 0; pv.raf = requestAnimationFrame(pvFrame);
  }
  function pvDispose() {
    pv.run = false; cancelAnimationFrame(pv.raf);
    if (pv.r) { pv.r.dispose(); if (pv.r.forceContextLoss) pv.r.forceContextLoss(); pv.r = null; }
    pv.failed = true; // layar utama tidak muncul lagi, jangan bikin ulang
  }
  var cvEl = $('pmsCv');
  cvEl.addEventListener('pointerdown', function (e) { pv.drag = true; pv.dx = e.clientX; try { cvEl.setPointerCapture(e.pointerId); } catch (x) {} });
  cvEl.addEventListener('pointermove', function (e) { if (pv.drag && pv.pivot) { pv.pivot.rotation.y += (e.clientX - pv.dx) * 0.012; pv.dx = e.clientX; } });
  function pvEnd() { pv.drag = false; }
  cvEl.addEventListener('pointerup', pvEnd); cvEl.addEventListener('pointercancel', pvEnd);

  /* ---------- tampil / sembunyi ---------- */
  function onShow() {
    var v = vis();
    side.style.display = v ? 'block' : 'none';
    if (v) { safe(render); safe(sync); safe(pvStart); safe(poll); }
    else safe(pvDispose);
  }
  new MutationObserver(onShow).observe(ss, { attributes: true, attributeFilter: ['style'] });
  btn.addEventListener('click', function () {
    ls('pm_tips_seen', '1');
    safe(claim); // hadiah harian diklaim otomatis kalau belum; bonus login lama jadi no-op
  });
  onShow();
})();
