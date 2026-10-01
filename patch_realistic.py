#!/usr/bin/env python3
# Patch grafis REALISTIS untuk BlockWorld (aktif cuma di mode "Grafis: HD").
import sys

P = 'index.html'
s = open(P, encoding='utf-8').read()

if 'window.PMReal' in s:
    print('Sudah dipatch, skip.'); sys.exit(0)

HOOK_OLD = "      btn.textContent = 'Grafis: ' + (on ? 'HD' : 'Normal');"
HOOK_NEW = HOOK_OLD + "\n      if (window.PMReal) window.PMReal.set(on);"
ANCHOR = "  const PMEnv = (function () {"

if s.count(HOOK_OLD) != 1 or s.count(ANCHOR) != 1:
    print('Anchor tidak ketemu / dobel. index.html beda dari yang diharapkan, batal.'); sys.exit(1)

MODULE = r'''  // ===== PMReal: grafis realistis (cuma aktif di mode HD) =====
  // Setelan yang bisa diubah:
  //   EXPOSURE   = terang/gelap keseluruhan (1.0 - 1.4)
  //   WATER_BUMP = kuat gelombang kecil di air (1 - 5)
  //   GLINT      = kilau matahari di air (20 - 120, makin besar makin tajam)
  window.PMReal = (function () {
    var EXPOSURE = 1.15, WATER_BUMP = 2.5, GLINT = 60;
    var TAU = Math.PI * 2, big = !isMobile;
    var on = false, raf = 0, timer = 0, ready = false, building = false, waterReady = false;
    var origImg = islandMat.map.image, origIslandMat = island.material, origWaterMat = water.material;
    var hiColor = null, realIslandMat = null, realWaterMat = null, shallows = null, foam = null;
    var maxAniso = renderer.capabilities.getMaxAnisotropy();

    function hash(x, y) {
      var h = (Math.imul(x, 374761393) + Math.imul(y, 668265263)) | 0;
      h = Math.imul(h ^ (h >>> 13), 1274126177);
      return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
    }
    function vnoise(x, y) {
      var xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
      var u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
      var a = hash(xi, yi), b = hash(xi + 1, yi), c = hash(xi, yi + 1), d = hash(xi + 1, yi + 1);
      return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
    }
    function fbm(x, y) { return (vnoise(x, y) * 0.5 + vnoise(x * 2, y * 2) * 0.25 + vnoise(x * 4, y * 4) * 0.125 + vnoise(x * 8, y * 8) * 0.0625) / 0.9375; }
    function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
    function mix(a, b, t) { return a + (b - a) * t; }

    // noise frekuensi rendah dihitung di grid kecil lalu diinterpolasi (jauh lebih cepat)
    function field(freq, off, N) {
      var W = N + 1, G = new Float32Array(W * W);
      for (var j = 0; j <= N; j++) for (var i = 0; i <= N; i++) G[j * W + i] = fbm(i / N * freq + off, j / N * freq + off);
      return function (fx, fy) {
        var x = fx * N, y = fy * N, i = Math.min(N - 1, x | 0), j = Math.min(N - 1, y | 0), u = x - i, v = y - j;
        var a = G[j * W + i], b = G[j * W + i + 1], c = G[(j + 1) * W + i], d = G[(j + 1) * W + i + 1];
        return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
      };
    }

    // tekstur pulau resolusi tinggi: rumput berbercak, pasir berombak, pantai basah + peta bump
    // dikerjakan bertahap (per ~10ms) supaya game gak nge-freeze
    function paintIsland(SZ, cb) {
      var c = document.createElement('canvas'); c.width = c.height = SZ;
      var b = document.createElement('canvas'); b.width = b.height = SZ;
      var g = c.getContext('2d'), bg = b.getContext('2d');
      var img = g.createImageData(SZ, SZ), d = img.data;
      var bimg = bg.createImageData(SZ, SZ), bd = bimg.data;
      var HALF = SZ / 2, wobF = field(6, 10, 128), patchF = field(5, 30, 128), n1F = field(14, 0, 256);
      var y = 0;
      function row(y) {
        var fy = y / SZ, cy = y - HALF;
        for (var x = 0; x < SZ; x++) {
          var cx = x - HALF, fx = x / SZ;
          var dist = Math.sqrt(cx * cx + cy * cy) / HALF;
          var wob = (wobF(fx, fy) - 0.5) * 0.10;
          var s = clamp01((dist + wob - 0.80) / 0.05); s = s * s * (3 - 2 * s);
          var n1 = n1F(fx, fy), fine = hash(x, y);
          var n2 = vnoise(fx * 60 + 50, fy * 60 + 50) * 0.6 + vnoise(fx * 120 + 50, fy * 120 + 50) * 0.4;
          var patch = clamp01((patchF(fx, fy) - 0.5) * 2.2);
          var gr = 62 + n1 * 40 + n2 * 10 + (fine - 0.5) * 16 - patch * 14;
          var gg = 135 + n1 * 70 + n2 * 15 + (fine - 0.5) * 22 - patch * 22;
          var gb = 54 + n1 * 30 + n2 * 8 + (fine - 0.5) * 10 - patch * 10;
          var sn = vnoise(fx * 40 + 90, fy * 40 + 90) * 0.6 + vnoise(fx * 80 + 90, fy * 80 + 90) * 0.4;
          var rip = 0.5 + 0.5 * Math.sin((x + y * 0.4) / SZ * 180 + sn * 6);
          var wet = clamp01((dist + wob - 0.92) / 0.07);
          var k = 1 - 0.28 * wet;
          var sr = (222 + sn * 16 + (fine - 0.5) * 14 - rip * 6) * k;
          var sg = (201 + sn * 18 + (fine - 0.5) * 14 - rip * 7) * k;
          var sb = (152 + sn * 16 + (fine - 0.5) * 12 - rip * 8) * k;
          var i = (y * SZ + x) * 4;
          d[i] = mix(gr, sr, s); d[i + 1] = mix(gg, sg, s); d[i + 2] = mix(gb, sb, s); d[i + 3] = 255;
          var hv = mix(0.55 * n1 + 0.30 * n2 + 0.15 * fine, 0.50 * sn + 0.30 * rip + 0.20 * fine, s) * 255;
          bd[i] = bd[i + 1] = bd[i + 2] = hv; bd[i + 3] = 255;
        }
      }
      function step() {
        var t0 = performance.now();
        while (y < SZ && performance.now() - t0 < 10) { row(y); y++; }
        if (y < SZ) { setTimeout(step, 0); return; }
        g.putImageData(img, 0, 0); bg.putImageData(bimg, 0, 0);
        cb({ color: c, bump: b });
      }
      step();
    }

    // gelombang kecil buat bump air (bisa di-tile)
    function paintWaterBump() {
      var SZ = 256, c = document.createElement('canvas'); c.width = c.height = SZ;
      var g = c.getContext('2d'), img = g.createImageData(SZ, SZ), d = img.data;
      for (var y = 0; y < SZ; y++) for (var x = 0; x < SZ; x++) {
        var u = x / SZ, v = y / SZ;
        var h = 0.5 + 0.22 * Math.sin(TAU * (3 * u + 2 * v)) + 0.16 * Math.cos(TAU * (5 * u - 4 * v)) +
                0.10 * Math.sin(TAU * (9 * u + 7 * v)) + 0.06 * Math.cos(TAU * (14 * u - 11 * v));
        var i = (y * SZ + x) * 4; d[i] = d[i + 1] = d[i + 2] = clamp01(h) * 255; d[i + 3] = 255;
      }
      g.putImageData(img, 0, 0);
      var t = new THREE.CanvasTexture(c);
      t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = maxAniso;
      return t;
    }

    function radialTex(inner, outer, stops) {
      var c = document.createElement('canvas'); c.width = c.height = 512;
      var g = c.getContext('2d');
      var gr = g.createRadialGradient(256, 256, 256 * inner / outer, 256, 256, 256);
      stops.forEach(function (s) { gr.addColorStop(s[0], s[1]); });
      g.fillStyle = gr; g.fillRect(0, 0, 512, 512);
      return new THREE.CanvasTexture(c);
    }
    function ringMesh(rIn, rOut, tex, y) {
      var m = new THREE.Mesh(new THREE.RingGeometry(rIn, rOut, 128, 1), new THREE.MeshLambertMaterial({
        map: tex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2
      }));
      m.rotation.x = -Math.PI / 2; m.position.y = y; m.renderOrder = 1;
      m.castShadow = false; m.receiveShadow = false;
      scene.add(m); return m;
    }

    function buildWater() {
      if (waterReady) return; waterReady = true;
      realWaterMat = new THREE.MeshPhongMaterial({
        map: waterTex, bumpMap: paintWaterBump(), bumpScale: WATER_BUMP,
        specular: 0xbfd8ee, shininess: GLINT, transparent: true, opacity: 0.88
      });
      // air dangkal tosca di sekitar pulau + buih ombak
      shallows = ringMesh(33, 58, radialTex(33, 58, [[0, 'rgba(70,215,205,0.65)'], [0.35, 'rgba(60,190,200,0.35)'], [1, 'rgba(40,150,190,0)']]), -0.32);
      foam = ringMesh(33.5, 37, radialTex(33.5, 37, [[0, 'rgba(255,255,255,0)'], [0.18, 'rgba(255,255,255,0.95)'], [0.45, 'rgba(255,255,255,0.45)'], [1, 'rgba(255,255,255,0)']]), -0.30);
      foam.position.y = -0.30;
    }

    function buildIsland() {
      if (ready || building || !on) return; building = true;
      paintIsland(big ? 1024 : 512, function (r) {
        hiColor = r.color;
        var bump = new THREE.CanvasTexture(r.bump); bump.anisotropy = maxAniso;
        realIslandMat = new THREE.MeshStandardMaterial({ map: islandMat.map, bumpMap: bump, bumpScale: 1.5, roughness: 0.95, metalness: 0 });
        building = false; ready = true;
        if (on) applyIsland(true);
      });
    }
    function applyIsland(v) {
      islandMat.map.image = v ? hiColor : origImg;
      islandMat.map.needsUpdate = true;
      island.material = v ? realIslandMat : origIslandMat;
    }

    function refreshMats() {
      scene.traverse(function (o) {
        var ms = o.material ? (Array.isArray(o.material) ? o.material : [o.material]) : [];
        ms.forEach(function (m) { m.needsUpdate = true; });
      });
    }

    function loop(ts) {
      if (!on) { raf = 0; return; }
      raf = requestAnimationFrame(loop);
      var t = ts / 1000;
      waterTex.offset.set(t * 0.012, t * 0.007);
      if (foam) {
        foam.scale.setScalar(1 + 0.012 * Math.sin(t * 1.1));
        foam.material.opacity = 0.7 + 0.3 * Math.sin(t * 1.6);
      }
    }

    return {
      set: function (v) {
        on = !!v;
        renderer.toneMapping = on ? THREE.ACESFilmicToneMapping : THREE.NoToneMapping;
        renderer.toneMappingExposure = EXPOSURE;
        buildWater();
        water.material = on ? realWaterMat : origWaterMat;
        shallows.visible = foam.visible = on;
        if (on) {
          if (ready) applyIsland(true);
          else if (!timer) timer = setTimeout(function () { timer = 0; buildIsland(); }, 400);
          if (!raf) raf = requestAnimationFrame(loop);
        } else if (ready) applyIsland(false);
        refreshMats();
      }
    };
  })();
  window.PMReal.set(PMHD.isHD());

'''

s = s.replace(HOOK_OLD, HOOK_NEW).replace(ANCHOR, MODULE + ANCHOR)
open(P, 'w', encoding='utf-8').write(s)
print('OK: grafis realistis ditambahkan ke index.html')
