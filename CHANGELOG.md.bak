# Changelog

Semua perubahan penting pada proyek ini dicatat di file ini. Diurutkan dari yang terbaru.

## 2026-09-29

- HUD kiri atas dibikin ringkas jadi satu baris (koin, level, XP mini, joran/umpan digabung), gak makan tempat lagi.
- Restyle HUD reeling & casting bergaya Fish It: bar hijau candy-stripe yang berubah warna (hijau → kuning → merah) sesuai bahaya, plus counter tap "(000)".
- Geser gradasi langit lebih dekat ke horizon supaya warna senja kelihatan sebelum ketutup dermaga/gedung.
- Upgrade kualitas render: antialias selalu aktif, resolusi tekstur (pulau, air, papan dermaga) dan ikon ikan didobelin, geometry bulat (pohon, tiang, pelampung) dihaluskan.
- Fix kota dermaga: posisi Toko Umpan/Toko Joran yang kebalik kiri-kanan, pindahkan Toko Jual Ikan biar gak nempel HUD, sesuaikan gradasi senja.

## 2026-09-28

- **Kota dermaga**: plaza kayu, dermaga yang menjorok ke laut, 3 toko (Umpan, Joran, Jual Ikan), lampu jalan, perahu kecil, pohon kelapa baru, dan langit senja.
- **HUD v3**: titik spawn dipindah menghadap laut, fitur Koleksi Ikan (index dengan siluet `???` untuk ikan belum ditemukan), animasi *reveal* kartu untuk tangkapan Epic/Legendary/Mythical, suara & getar (WebAudio + `navigator.vibrate`), Auto Mancing, info umpan aktif di HUD.
- Bersihkan file patch lama & `node_modules` dari tracking git.
- Tambah rarity **Secret** (ikan *Kraken Purba*) dengan RNG super kecil, animasi tangkapan full-screen rainbow sendiri, plus animasi "pop" pada badge koin/level dan restyle modal Tas/Toko & toast.
- Poles HUD: padding aman dari notch/status bar (`safe-area-inset`), badge koin/level yang nongol keluar dari border kartu, ikon joran di tombol PANCING.
- Update HUD ke gaya Fish It: badge bulat, tombol dengan efek 3D press.
- Ganti ikon emoji jadi custom icon (SVG).
- Update HUD & tampilan umum.
- Fitur minigame reeling gaya *tap-to-drain*.
- Fix arah drag vertikal kamera yang kebalik.
- Fix analog gerak yang kebalik & drag kamera yang tidak jalan.

## 2026-09-27

- **Rombak total jadi Pancing Mania** — proyek yang awalnya game voxel eksplorasi (BlockWorld) diubah jadi game mancing 3D bertema kota dermaga, terinspirasi Fish It (Roblox). Nama repo, package, dan pipeline CI/APK tetap dipertahankan.

## Sebelum Pancing Mania

Repo ini awalnya adalah **BlockWorld**, game voxel eksplorasi & survival ala Minecraft. Riwayat sebelum 27 September 2026 berisi pembangunan game voxel tersebut beserta pipeline build APK (Bubblewrap/TWA, lalu Capacitor) dan PWA (manifest, service worker) yang basisnya masih dipakai sampai sekarang.
