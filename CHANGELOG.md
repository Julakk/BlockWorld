# Changelog

Semua perubahan penting pada proyek ini dicatat di file ini. Diurutkan dari yang terbaru.

## 2026-10-04 (v4.5)

- Perahu di dermaga dihapus, diganti NPC Pak Karto di samping Rod Shop yang menjual perahu.
- 5 tipe perahu (Sampan, Jukung, Perahu Motor, Speedboat, Kapal Layar Mewah) dengan harga dan kecepatan berbeda. Sampan gratis.
- Perahu yang dibeli tersimpan di save, kecepatan berlayar mengikuti tipe perahu yang dipakai.
- Model Pak Karto dibuat 3D lebih detail dan dipindah ke samping Rod Shop.
- Info Update lama diganti dengan yang baru, versi naik ke v4.5.

## 2026-10-03 (v4.4)

- Papan Peringkat baru di samping Akuarium, menu Peringkat dihapus.
- Indeks Ikan didesain ulang: pilih lokasi di kiri, kartu ikan di kanan, plus bar progres.
- Fitur Boss Raja Laut dihapus.

## 2026-10-03 (v4.3)

- Akuarium: koin pasif dihitung server pakai jam server, ambil koin butuh online.
- Pasar Pemain: batas listing per username, nggak bisa beli barang sendiri, kotak surat penuh nggak buang barang.
- Boss Fish: batas serangan token bucket (rata-rata 6/dtk), pemain yang ditandai curang nggak dihitung.
- Peringkat: berat ikan dicek ke tabel ikan, laporan maksimal sekali per 20 detik, nilai awal pemain baru dibatasi.

## 2026-10-03 (v4.2)

- Peringkat Online: pemain dengan tangkapan terbanyak, ikan terberat, dan prestise tertinggi.
- Boss Fish: boss raksasa muncul berkala untuk semua pemain online. Hadiah dibagi sesuai jumlah serangan dan MVP dapat bonus.
- Pasar Pemain: jual-beli ikan antar pemain, biaya pasar 5%, maksimal 5 listing per pemain, barang disimpan di server sampai terjual.

## 2026-10-03 (v4.1)

- Akuarium menghasilkan koin pasif, tersimpan sampai 8 jam, diambil lewat tombol di Akuarium.
- 16 trofi baru dan gelar berdasarkan jumlah trofi.

## 2026-10-03 (v4.0)

- Rebirth: reset level dan progres untuk bonus permanen Luck, Speed, Harga Jual, dan XP, plus gelar baru.
- Pet pendamping: Telur Pet, 6 jenis pet, bonus naik bintang kalau dapat duplikat, slot ke-2 terbuka di Rebirth 3.
- Nama pulau di atas pulau dan pesan selamat datang saat tiba. Pulau pertama bernama Pulau Utama.

## 2026-10-03 (v3.9)

- Tampilan ikan tangkapan dikecilkan dan dipindah ke atas.
- Altar Enchant tampil lebih HD: tekstur batu, lingkaran rune berputar, kristal berkilau, serpihan, dan partikel.
- Mode Grafis HD lebih ringan: resolusi menyesuaikan FPS otomatis, bayangan lebih hemat.
- Malam dan hujan lebih terang: ada cahaya bulan, redaman hujan dikurangi.
- Info Update lama dihapus, hanya menampilkan update terbaru.

## 2026-10-03 (v3.8)

- Altar Enchant dirombak: 14 enchant dengan 5 tier (Common, Rare, Epic, Legendary, Mythic).
- Efek baru Harga Jual dan XP, enchant Mythic Tycoon, Godhand, dan Omniscient.
- Animasi undian enchant, sistem Pity tiap 20 roll, dan Roll Kunci Tier.
- Peluang tiap tier ditampilkan langsung di altar.

## 2026-10-02 (v3.7)

- **Cek kecepatan gerak di server**: jalan kaki 4,2 u/s dikasih ruang 1,5x ditambah cadangan 20 unit buat lag. Gerak yang melebihi itu ditahan, 10 pelanggaran dalam 10 dtk = peringatan ke developer, 25 = pemain di-kick. Developer dikecualikan. Titik dermaga/perahu/spawn boleh dituju (naik-turun perahu), posisi pertama tiap sesi diterima apa adanya (reconnect).
- **Tahan restart**: daftar ban, riwayat Info Secret, dan status maintenance disimpan di `server/data.json` (bisa diubah lewat env `DATA_FILE`). File ini di-gitignore.
- **Endpoint admin baru**: `/admin/bans` (daftar) dan `/admin/unban?name=...` (lepas ban), pakai header `x-dev-token`.
- **Layar maintenance**: latar penuh, pesan lebih besar, dicek otomatis tiap 10 dtk dan hilang sendiri saat server buka lagi.

## 2026-10-02 (v3.6)

- **Anti-curang Secret**: server mengecek event Secret (butuh event `cast` sebelumnya, jeda 3 dtk sampai 10 menit, mutasi dan berat sesuai tabel ikan, maks 12 per jam). Yang ditolak dicatat di log dan 3x tolak = pemain ditandai dan developer dapat peringatan. Klien lama (tanpa `cv`) tetap dicek mutasi/berat/jam tapi tidak wajib `cast`.
- **Fix tombol Download update**: link lama `app-debug.apk` sudah tidak ada sejak APK diganti nama; sekarang server mengirim link APK asli dari release lewat `/status`.
- **Cek status berkala**: update/maintenance dicek tiap 3 menit dan saat app kembali dibuka; tombol "Nanti" tidak nagih lagi untuk build yang sama.
- **Maintenance dari terminal**: `curl -H "x-dev-token: TOKEN" "http://localhost:3010/admin/maint?on=1&msg=Teks"` (on=0 untuk mematikan).
- Kontras label waktu/cuaca, nomor versi, dan FPS. Batas berat Secret 99.999 kg di server dihapus.

## 2026-10-02 (v3.5)

- **HUD lebih ringkas**: baris joran/umpan dan statistik (Luck, Speed, Weight) digabung jadi satu baris dengan ikon, angka besar disingkat (19,6K%, 1B kg). Panel kiri atas jadi 2 baris.
- **Fix teks numpuk**: label waktu/cuaca di bawah tengah tidak lagi tertimpa badge versi (label dinaikkan, area tap badge dikecilkan).
- **Fix badge versi**: sebelumnya teks tertulis manual `v3.1`; sekarang otomatis mengikuti versi game.

## 2026-10-02 (v3.4)

- **Animasi ikan Secret lebih hidup**: badan ikan meliuk (gelombang S), ekor menyabet, kraken berdenyut seperti jet, lompatan mengikuti gravitasi dengan slow-motion di puncak, dan di fase melawan muncul sirip di permukaan air dengan percikan yang makin ganas.
- **Pamer ikan**: ikan menggantung kepala di atas, bergoyang seperti bandul, makin lemas, air menetes. Kamera bergetar saat ikan melawan dan zoom pelan saat melompat.
- **Notifikasi Secret**: toast pelangi muncul buat semua pemain termasuk diri sendiri, dan tampil di atas layar sinematik. Event yang dikirim saat koneksi putus diantri lalu dikirim ulang. Jeda server per pemain 30 detik jadi 4 detik.

## 2026-10-02 (v3.3)

- **Animasi ikan Secret**: saat dapat ikan Secret (Kraken Purba / Megalodon) ada adegan sinematik: ikan melawan tarikan, melompat dari air dengan percikan dan cincin ombak, lalu dipamerkan karakter di bawah sorot cahaya. Kamera berpindah-pindah, bisa dilewati dengan ketuk layar.
- **Notifikasi publik**: server mengumumkan ke semua pemain online kalau ada yang dapat ikan Secret (dibatasi 1x per 30 detik per pemain, cuma ID ikan Secret yang diterima).
- **Chat publik 2 tab**: Live Chat dan Info Secret. Riwayat 30 Info Secret terakhir disimpan di server dan dikirim ke pemain yang baru masuk.

## 2026-10-02

- **v3.2 - Logo baru**: logo Pancing Mania dipakai di ikon aplikasi (launcher), splash screen, ikon web, layar loading, dan layar awal.
- **v3.2 - Grafis HD realistis**: tone mapping ACES Filmic, tekstur pulau resolusi tinggi dengan bump (rumput berbercak, pasir berombak, pantai basah), air bergelombang dengan kilau matahari, air dangkal tosca, dan buih ombak. Cuma aktif di mode Grafis: HD, dan otomatis mati kalau FPS drop.
- **v3.2 - Server publik**: game langsung tersambung ke `wss://game.ahmadfivem.my.id` tanpa pemain perlu ngisi alamat server.
- **v3.2 - Nama APK**: hasil build sekarang `PancingMania-v<versi>.apk` (bukan `app-debug.apk`), artifact bernama `PancingMania-apk`, dan nama Release ikut versi game.

## 2026-09-30

- **Fix build & APK**: Three.js sekarang disimpan lokal (`three.min.js`) dan ikut di dalam APK, jadi game jalan tanpa internet (CDN cuma jadi cadangan). `versionCode` otomatis naik tiap build dan `versionName` ngikutin versi game, jadi APK baru bisa nimpa yang lama. Game dan audio otomatis pause saat app di-minimize. Workflow pakai JDK 17. `sw.js` dan workflow auto-bump dihapus karena nggak dipakai, `www/index.html` sekarang di-gitignore.
- **v2.3 - Ikan baru & Koleksi**: 17 ikan baru, jadi total 30 ikan di Koleksi. Koleksi sekarang nunjukin zona tiap ikan. Ada ikan Perairan Dangkal (Kerapu, Ubur-ubur Bening, Kuda Laut Kristal, Penyu Hijau, dan lainnya) dan ikan Laut Dalam.
- **v2.3 - Zona Laut Dalam**: Air gelap di kejauhan adalah Laut Dalam. Lempar dari ujung dermaga dengan Carbon Rod ke atas buat sampai ke sana. Isinya Ikan Lentera, Todak, Pari Manta, Hiu Martil, Cumi Raksasa, Ikan Bulan, Paus Biru, dan Megalodon (Secret). Peluang ikan langka lebih tinggi, tapi ikannya lebih kuat narik.
- **v2.3 - Shiny dan mutasi baru**: Mutasi baru: Besar (lebih berat, harga x2.5) dan Hantu (harga x6). Shiny punya peluang sendiri 4% dan bisa nempel ke mutasi lain, harga x3.
- **v2.3 - Altar Enchant**: Altar baru di plaza sisi kiri. Enchant rod lu buat bonus Luck atau Speed, dari Luck I sampai Swift III dan Fortune. Hasil enchant bisa dipilih dulu: Pakai atau Buang. Biayanya makin mahal buat rod yang lebih bagus.
- **v2.2 - Reel tap-tap ala Fish It**: Sistem TAHAN dan TARIK dihapus, sekarang cukup tap terus. Bar terisi tiap tap dan turun sendiri kalau berhenti. Penuh berarti ikan naik, kosong berarti ikan lepas. Ikan yang lebih langka dan lebih berat bikin bar turun lebih cepat. Rod yang lebih bagus ngisi bar lebih banyak per tap. Tali nggak bisa putus lagi. Ikan yang kelewat berat buat rod lu tetap bakal lepas.
- **v2.2 - Auto Mancing**: Auto tap terus sampai ikan naik, tapi ikan langka butuh rod yang cukup bagus. Ikan Rahasia tetap harus manual.
- **v2.0 - Mekanik mancing ala Fish It**: luck meter saat lempar dengan zona Good, Amazing, dan Perfect yang ngasih bonus Luck. Ikan sekarang punya berat dan tiap rod punya batas berat, jadi ikan yang kelewat berat bikin tali putus.
- **Bait permanen**: bait dibeli sekali dan nggak habis per lempar. Luck rod dan bait sekarang dijumlah (bukan dikali), sesuai Fish It.
- **Rod & Bait disamain dengan Fish It**: rod jadi Starter, Carbon, Damascus, Lucky, Chrome, dan Astral. Bait jadi Starter, Midnight, Nature, Chroma, dan Dark Matter. Tab dan toko diganti ke istilah Rod/Bait, ikon berwarna sesuai rarity.
- **Minigame reel**: bar ngisi tiap tap lengkap dengan counter "(000)", ditambah bar tegangan tali yang berubah hijau, kuning, lalu merah. Auto Mancing disesuaikan: lemparnya mentok di GOOD dan Ikan Rahasia tetap harus manual.
- **HUD**: chip rod & bait dengan border warna rarity, baris stat Luck/Speed/Weight, bar lempar dengan zona warna, dan popup hasil tangkapan untuk semua rarity (berat, harga, tag Mutasi). Tampilan Tas jadi grid kartu.
- **Info Update**: popup daftar perubahan di dalam game. Muncul otomatis sekali tiap ada versi baru dan bisa dibuka lagi dari Menu.

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
