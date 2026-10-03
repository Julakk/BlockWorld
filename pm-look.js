/* PM-LOOK v1 - warna karakter + preview 3D muter + cek username live */
(function () {
  'use strict';
  var C = window.__PMC;
  if (!C || !window.THREE || window.__pmLook) return;
  window.__pmLook = true;
  var T = THREE, P = C.player;

  var KEYS = ['hair', 'shirt', 'pants', 'skin'];
  var LABEL = { hair: 'Rambut', shirt: 'Baju', pants: 'Celana', skin: 'Kulit' };
  var DEF = { hair: '#3a2a1a', shirt: '#4ac0e0', pants: '#33485f', skin: '#f0c299' };
  var PRESET = {
    hair: ['#1b1b1b', '#3a2a1a', '#8b5a2b', '#d9b44a', '#c0392b', '#8e44ad', '#2e86de', '#ecf0f1'],
    shirt: ['#4ac0e0', '#e74c3c', '#27ae60', '#f1c40f', '#8e44ad', '#e67e22', '#ecf0f1', '#2c3e50'],
    pants: ['#33485f', '#1d2126', '#6b4423', '#1e8449', '#7f8c8d', '#e6e9ee'],
    skin: ['#f8d9b8', '#f0c299', '#d69a6b', '#a56b43', '#6b4226']
  };
  var HEX = /^#[0-9a-f]{6}$/i;
  var NAME_RE = /^[A-Za-z0-9_]{3,16}$/;

  /* ---------- cari bagian karakter ---------- */
  var hairMesh = null, headMesh = null;
  P.traverse(function (o) {
    var g = o.geometry;
    if (!o.isMesh || !g || g.type !== 'SphereGeometry' || !g.parameters) return;
    if (g.parameters.radius === 0.212) hairMesh = o;
    else if (g.parameters.radius === 0.2 && g.parameters.widthSegments === 24) headMesh = o;
  });
  function mats() {
    return {
      hair: hairMesh ? hairMesh.material : null,
      shirt: C.body.material,
      pants: C.legL.material,
      skin: headMesh ? headMesh.material : null
    };
  }

  /* ---------- warna aktif (diterapkan tiap frame, setelah sistem Karakter lama) ---------- */
  var cols = {}, on = false;
  KEYS.forEach(function (k) { cols[k] = new T.Color(DEF[k]); });
  function clean(d) {
    var o = {};
    KEYS.forEach(function (k) { o[k] = d && HEX.test(d[k]) ? d[k] : DEF[k]; });
    return o;
  }
  function use(d) { KEYS.forEach(function (k) { cols[k].set(d[k]); }); on = true; applyLook(); }
  function applyLook() {
    if (!on) return;
    var m = mats();
    for (var i = 0; i < KEYS.length; i++) { var k = KEYS[i]; if (m[k]) m[k].color.copy(cols[k]); }
  }
  if (C.save && C.save.look) use(clean(C.save.look));
  C.hookAnim(applyLook);

  /* ---------- UI ---------- */
  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }
  var css = document.createElement('style');
  css.textContent = [
    '#pmlOv{position:fixed;left:0;top:0;right:0;bottom:0;z-index:55;display:none;align-items:center;justify-content:center;background:rgba(2,8,14,.72);padding:12px;box-sizing:border-box}',
    '#pmlOv.on{display:flex}',
    '#pmlBox{width:min(94vw,400px);max-height:92vh;display:flex;flex-direction:column;background:linear-gradient(165deg,#1d5068,#0a1e2c);border:3px solid rgba(255,255,255,.9);border-radius:22px;box-shadow:0 8px 0 rgba(0,0,0,.35),0 18px 40px rgba(0,0,0,.5);color:#fff;overflow:hidden;font-family:inherit}',
    '#pmlHead{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:2px dashed rgba(255,255,255,.24)}',
    '#pmlHead h2{margin:0;font-size:16px;font-weight:800}',
    '#pmlX{border:2px solid rgba(255,255,255,.55);background:rgba(255,255,255,.16);color:#fff;width:30px;height:30px;border-radius:50%;font-size:14px}',
    '#pmlBody{overflow-y:auto;padding:10px 14px;-webkit-overflow-scrolling:touch}',
    '#pmlCv{display:block;margin:0 auto 10px;width:200px;height:240px;border-radius:14px;background:radial-gradient(circle at 50% 35%,#2f6f8a,#0b1c28 75%);touch-action:none}',
    '.pmlRow{margin-bottom:9px}',
    '.pmlLb{display:block;font-size:12px;font-weight:700;opacity:.85;margin-bottom:4px}',
    '.pmlSw{display:flex;flex-wrap:wrap;gap:6px;align-items:center}',
    '.pmlChip{width:28px;height:28px;border-radius:7px;border:2px solid rgba(255,255,255,.7);padding:0}',
    '.pmlSw input[type=color]{width:36px;height:32px;border:0;padding:0;background:none}',
    '#pmlFoot{display:flex;gap:8px;padding:10px 14px;border-top:2px dashed rgba(255,255,255,.24)}',
    '#pmlFoot button{flex:1;padding:10px 6px;border-radius:999px;border:2px solid #fff;font-weight:800;font-size:13px;color:#052730;background:linear-gradient(90deg,#37d1c8,#2f9fc9)}',
    '#pmlFoot button.alt{background:rgba(255,255,255,.14);color:#fff;border-color:rgba(255,255,255,.5)}',
    '@media (orientation:landscape) and (max-height:520px){#pmlBox{width:min(94vw,640px)}#pmlBody{display:flex;gap:14px;align-items:flex-start}#pmlCv{width:150px;height:180px;margin:0;flex:none}#pmlCtl{flex:1;min-width:0}}'
  ].join('');
  document.head.appendChild(css);

  var ov = el('div'); ov.id = 'pmlOv';
  var box = el('div'); box.id = 'pmlBox';
  var head = el('div'); head.id = 'pmlHead';
  var h2 = el('h2'); h2.textContent = 'Warna Karakter';
  var xb = el('button'); xb.id = 'pmlX'; xb.type = 'button'; xb.textContent = '\u2715';
  head.appendChild(h2); head.appendChild(xb);
  var body = el('div'); body.id = 'pmlBody';
  var cv = el('canvas'); cv.id = 'pmlCv';
  var ctl = el('div'); ctl.id = 'pmlCtl';
  body.appendChild(cv); body.appendChild(ctl);
  var foot = el('div'); foot.id = 'pmlFoot';
  var bSave = el('button'); bSave.type = 'button'; bSave.textContent = 'Simpan';
  var bReset = el('button', 'alt'); bReset.type = 'button'; bReset.textContent = 'Bawaan';
  var bCancel = el('button', 'alt'); bCancel.type = 'button'; bCancel.textContent = 'Batal';
  foot.appendChild(bSave); foot.appendChild(bReset); foot.appendChild(bCancel);
  box.appendChild(head); box.appendChild(body); box.appendChild(foot);
  ov.appendChild(box); document.body.appendChild(ov);

  KEYS.forEach(function (key) {
    var row = el('div', 'pmlRow'), lb = el('span', 'pmlLb'); lb.textContent = LABEL[key]; row.appendChild(lb);
    var sw = el('div', 'pmlSw');
    PRESET[key].forEach(function (c) {
      var b = el('button', 'pmlChip'); b.type = 'button'; b.style.background = c;
      b.onclick = function () { setColor(key, c); };
      sw.appendChild(b);
    });
    var inp = document.createElement('input'); inp.type = 'color'; inp.id = 'pmlIn-' + key;
    inp.oninput = function () { setColor(key, inp.value); };
    sw.appendChild(inp); row.appendChild(sw); ctl.appendChild(row);
  });

  /* ---------- preview 3D ---------- */
  var R = { r: null, run: false, raf: 0, last: 0, drag: false, dx: 0 };
  function ensureRenderer() {
    if (R.r) return true;
    try { R.r = new T.WebGLRenderer({ canvas: cv, antialias: true, alpha: true }); }
    catch (e) { R.r = null; return false; }
    R.r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    R.r.setSize(200, 240, false);
    R.r.setClearColor(0x000000, 0);
    R.r.toneMapping = T.ACESFilmicToneMapping; R.r.toneMappingExposure = 1.15;
    R.sc = new T.Scene();
    R.sc.add(new T.HemisphereLight(0xfff0dd, 0x3a4a5a, 1.0));
    var dl = new T.DirectionalLight(0xffe2c0, 0.9); dl.position.set(3, 5, 4); R.sc.add(dl);
    R.cam = new T.PerspectiveCamera(30, 200 / 240, 0.1, 50);
    R.cam.position.set(0, 1.2, 4.6); R.cam.lookAt(new T.Vector3(0, 0.95, 0));
    R.pivot = new T.Group(); R.sc.add(R.pivot);
    return true;
  }
  function rebuildModel() {
    while (R.pivot.children.length) R.pivot.remove(R.pivot.children[0]);
    var g = P.clone(true); // material & geometry dibagi dengan karakter asli, warna ikut live
    g.position.set(0, 0, 0); g.rotation.set(0, 0, 0); g.scale.set(1, 1, 1);
    g.traverse(function (o) {
      if (o.isSprite) { o.visible = false; return; }
      var gm = o.geometry, p = gm && gm.parameters;
      if (o.isMesh && p && gm.type === 'CylinderGeometry' && p.radiusTop === 0.014 && p.radiusBottom === 0.03) o.visible = false; // joran
    });
    g.children.forEach(function (o) { // reset pose: berdiri lurus
      var gm = o.geometry, p = gm && gm.parameters;
      if (o.isMesh && p && gm.type === 'CylinderGeometry' && (p.radiusTop === 0.105 || (p.radiusTop === 0.08 && p.radiusBottom === 0.07))) {
        o.rotation.set(0, 0, 0);
        o.children.forEach(function (c) { if (c.isGroup) c.rotation.set(0, 0, 0); });
      } else if (o.isGroup && Math.abs(o.position.y - 1.3) < 0.03) o.rotation.set(0, 0, 0); // kepala
    });
    R.pivot.add(g); R.pivot.rotation.y = 0.5;
  }
  function frame(t) {
    if (!R.run) return;
    R.raf = requestAnimationFrame(frame);
    var dt = R.last ? Math.min(0.1, (t - R.last) / 1000) : 0; R.last = t;
    if (!R.drag) R.pivot.rotation.y += dt * 0.9;
    R.r.render(R.sc, R.cam);
  }
  function startLoop() { if (R.run) return; R.run = true; R.last = 0; R.raf = requestAnimationFrame(frame); }
  function stopLoop() { R.run = false; cancelAnimationFrame(R.raf); }
  cv.addEventListener('pointerdown', function (e) { R.drag = true; R.dx = e.clientX; try { cv.setPointerCapture(e.pointerId); } catch (x) {} });
  cv.addEventListener('pointermove', function (e) { if (R.drag && R.pivot) { R.pivot.rotation.y += (e.clientX - R.dx) * 0.012; R.dx = e.clientX; } });
  function endDrag() { R.drag = false; }
  cv.addEventListener('pointerup', endDrag); cv.addEventListener('pointercancel', endDrag);

  /* ---------- buka / tutup ---------- */
  var draft = null, snap = null;
  function setColor(k, c) {
    draft[k] = c; cols[k].set(c); on = true; applyLook();
    var i = document.getElementById('pmlIn-' + k); if (i) i.value = c;
  }
  function syncInputs() {
    KEYS.forEach(function (k) { var i = document.getElementById('pmlIn-' + k); if (i) i.value = draft[k]; });
  }
  function openPanel() {
    var m = mats();
    snap = {};
    KEYS.forEach(function (k) { snap[k] = m[k] ? '#' + m[k].color.getHexString() : DEF[k]; });
    draft = Object.assign({}, snap);
    syncInputs();
    ov.className = 'on';
    if (ensureRenderer()) { rebuildModel(); startLoop(); }
  }
  function closePanel(keep) {
    ov.className = ''; stopLoop();
    if (keep) return;
    if (C.save && C.save.look) use(clean(C.save.look));
    else {
      on = false; var m = mats(); // balikin tampilan sebelum dibuka
      KEYS.forEach(function (k) { if (m[k]) m[k].color.set(snap[k]); });
    }
  }
  bSave.onclick = function () {
    C.save.look = Object.assign({}, draft); C.persist();
    C.toast('Warna karakter disimpan'); closePanel(true);
  };
  bReset.onclick = function () {
    if (!confirm('Balik ke warna bawaan game?')) return;
    delete C.save.look; C.persist(); location.reload();
  };
  bCancel.onclick = function () { closePanel(false); };
  xb.onclick = function () { closePanel(false); };

  window.PMLook = { open: openPanel, apply: applyLook };
  var host = document.getElementById('menuPanel') || document.getElementById('hudPills');
  if (host) {
    var mb = el('button', 'hudPill'); mb.textContent = 'Warna Karakter';
    mb.onclick = function () { var mp = document.getElementById('menuPanel'); if (mp) mp.classList.remove('show'); openPanel(); };
    host.appendChild(mb);
  }

  /* ---------- cek username live (layar Buat Karakter) ---------- */
  var nameIn = document.getElementById('mpName'), go = document.getElementById('mpGo');
  if (nameIn && go) {
    var cb = el('button'); cb.type = 'button'; cb.textContent = '\uD83C\uDFA8 Atur Warna Karakter';
    cb.onclick = openPanel; go.parentNode.insertBefore(cb, go);
    var st = el('div'); st.style.cssText = 'min-height:16px;font-size:13px;max-width:80vw';
    nameIn.insertAdjacentElement('afterend', st);
    var seq = 0, tm = 0;
    var setSt = function (msg, col) { st.textContent = msg; st.style.color = col || '#a9c6cd'; };
    var base = function () {
      var s = null; try { s = localStorage.getItem('pm_server'); } catch (e) {}
      return (s || 'wss://game.ahmadfivem.my.id').replace(/^ws/, 'http').replace(/\/+$/, '');
    };
    var check = function (n, my) {
      var ctl2 = ('AbortController' in window) ? new AbortController() : null;
      var to = setTimeout(function () { if (ctl2) ctl2.abort(); }, 6000);
      fetch(base() + '/check?name=' + encodeURIComponent(n), { signal: ctl2 ? ctl2.signal : undefined })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          clearTimeout(to); if (my !== seq) return;
          if (j && j.ok && typeof j.available === 'boolean') {
            if (j.available) setSt('\u2714 "' + n + '" tersedia', '#4ce88a');
            else { setSt('\u2718 "' + n + '" sudah dipakai', '#ff6b6b'); go.disabled = true; }
          } else setSt('Cek live belum aktif di server, nama dicek saat Lanjut');
        })
        .catch(function () {
          clearTimeout(to); if (my !== seq) return;
          setSt('Server tidak terjangkau, nama dicek saat Lanjut');
        });
    };
    nameIn.addEventListener('input', function () {
      var n = nameIn.value.trim(); clearTimeout(tm); seq++; go.disabled = false;
      if (!n) { setSt(''); return; }
      if (!NAME_RE.test(n)) { setSt('3-16 karakter: huruf, angka, _', '#ff8a7a'); return; }
      setSt('Mengecek...');
      var my = seq; tm = setTimeout(function () { check(n, my); }, 450);
    });
  }
})();
