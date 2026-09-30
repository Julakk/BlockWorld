# 🎣 Pancing Mania

Game mancing 3D low-poly yang terinspirasi dari **Fish It** (Roblox), dibangun full di browser pakai [Three.js](https://threejs.org/) r128 (disimpan lokal di `three.min.js`, jadi jalan offline) — satu file `index.html`, tanpa build step, tanpa bundler.

Aslinya proyek ini adalah **BlockWorld**, game voxel eksplorasi ala Minecraft. Sejak akhir September 2026 direstrukturisasi total jadi game mancing bertema kota dermaga, tapi nama repo & package tetap `BlockWorld` untuk menjaga histori dan pipeline CI yang sudah ada.

## Fitur

- **Dunia 3D**: pulau prosedural dengan pasir, rumput, laut animasi, dan **kota dermaga** (plaza, dermaga menjorok ke laut, 3 toko, lampu jalan, perahu, pohon kelapa) dengan suasana langit senja.
- **Sistem mancing**: charge lempar (power bar) → tunggu sambaran → tarik cepat (reeling minigame gaya *tap-to-drain*, bar hijau bergaris ala Fish It).
- **7 tingkat rarity ikan**: Biasa → Lumayan → Langka → Epik → Legendaris → Mitos → **Rahasia** (ikan *Kraken Purba*, RNG-nya sengaja dibikin sangat kecil, dengan animasi tangkapan full-screen sendiri).
- **Progres**: level & XP, koleksi joran & umpan yang bisa dibeli, Koleksi Ikan (index ikan dengan siluet `???` untuk yang belum ditemukan).
- **Auto Mancing** (item toko): cast–strike–tarik otomatis, kecuali ikan Rahasia yang tetap harus ditarik manual.
- **Suara & getar**: seluruh SFX di-generate langsung lewat WebAudio (tanpa file audio), plus `navigator.vibrate` yang polanya beda tiap rarity.
- **HUD ringkas** bergaya Fish It: badge koin/level bulat, tombol Tas/Toko dengan notifikasi, pill Jual Semua/Koleksi/Suara/Auto.
- Dibungkus jadi APK Android lewat Capacitor, semua aset (termasuk Three.js) ikut di dalam APK sehingga bisa dimainkan offline. Game otomatis pause saat app di-minimize.

## Struktur proyek

`index.html` adalah satu-satunya file yang perlu diedit untuk mengubah gameplay atau tampilan. CI otomatis menyalin `index.html` dan `three.min.js` ke `www/` sebelum build APK (`www/index.html` di-gitignore, jangan diedit manual).

## Development

Seluruh development dilakukan langsung dari HP lewat **Termux** — tidak ada langkah build lokal. Alur kerjanya:

1. Edit `index.html`.
2. `git add`, `commit`, `push` ke `main`.
3. GitHub Actions (`build-apk.yml`) otomatis: `npm install` → sync `www/` → set versi APK → `cap sync android` → build APK → rilis sebagai GitHub Release dengan tag `build-N`.

Versi APK diisi otomatis: `versionName` diambil dari `var VER = 'vX.Y'` di `index.html`, `versionCode` dari nomor run GitHub Actions (naik terus tiap build, jadi APK baru bisa nimpa yang lama).

## Download

APK hasil build otomatis bisa diambil dari halaman **[Releases](../../releases)** repo ini (tag `build-N`, rilis terbaru selalu ditandai *Latest*).

## Lisensi

Belum ditentukan.
