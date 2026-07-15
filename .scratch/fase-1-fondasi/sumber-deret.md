# Inventaris sumber deret waktu publik

Terkait: [issues/03-inventaris-sumber-deret.md](fase-1-fondasi/issues/03-inventaris-sumber-deret.md) (F4-01).
Brief acuan: `project_brief.md` §9.1 (sumber data) dan §17.1 (lisensi/ToS data publik).

**Catatan:** ini inventaris (riset sumber), bukan hasil scraping — belum ada data yang diambil. URL/endpoint
di bawah perlu diverifikasi ulang (masih aktif, format response, rate limit) sesaat sebelum F4-02 mulai
scraping, karena portal pemerintah Indonesia cukup sering berubah struktur.

| # | Nama sumber | URL/endpoint | Domain | Cara akses | Frekuensi + panjang data tipikal | Catatan lisensi/ToS |
|---|---|---|---|---|---|---|
| 1 | PIHPS Nasional (Bank Indonesia) | https://www.bi.go.id/hargapangan (dashboard PIHPS Nasional) | food price | Scrape HTML/endpoint JSON internal dashboard (belum ada API publik resmi terdokumentasi) | Harian per komoditas per kota/pasar; histori tersedia beberapa tahun ke belakang (server-side date range) | Data publik pemerintah (BI); tidak ada lisensi eksplisit di halaman — perlakukan sebagai data publik non-komersial, cantumkan sumber, cek ToS BI sebelum redistribusi massal |
| 2 | Panel Harga Pangan — Badan Pangan Nasional (Bapanas) | https://panelharga.badanpangan.go.id | food price | Scrape HTML (tabel harian per provinsi/komoditas); kemungkinan ada endpoint JSON di balik dashboard — perlu inspeksi jaringan | Harian, per provinsi/kabupaten; histori tahun berjalan mudah diakses, tahun lalu via filter tanggal | Data publik lembaga pemerintah (Bapanas); ikuti aturan Satu Data Indonesia — publik untuk dilihat, cek ketentuan penggunaan ulang sebelum redistribusi |
| 3 | SP2KP — Kementerian Perdagangan | https://ews.kemendag.go.id (Sistem Pemantauan Pasokan dan Harga Pangan) | food price | Scrape HTML dashboard; alternatif/cadangan jika PIHPS/Bapanas berubah struktur | Harian per komoditas per pasar acuan; histori beberapa bulan–tahun tergantung filter | Data publik Kemendag; tidak ada lisensi terbuka eksplisit — perlakukan sebagai data publik non-komersial |
| 4 | BPS — Statistik Harga Konsumen / Harga Produsen (webAPI BPS) | https://webapi.bps.go.id (perlu API key gratis, daftar di https://webapi.bps.go.id/documentation) | food price (pelengkap) | API resmi (BPS Web API, JSON, butuh registrasi key gratis) | Bulanan (IHK/inflasi per kelompok pengeluaran termasuk pangan); histori panjang (bertahun-tahun, sejak rebasing terakhir) | Data publik BPS; BPS Web API punya ToS eksplisit (atribusi wajib, non-komersial untuk sebagian layanan) — baca `webapi.bps.go.id` ToS sebelum pakai |
| 5 | Kemenkes — SKDR (Sistem Kewaspadaan Dini dan Respon) | https://skdr.surveilans.org atau portal Satu Data Kesehatan (https://data.kemkes.go.id) | health (DBD) | Scrape HTML dashboard / unduh rekap jika tersedia; akses login-gated untuk sebagian modul (perlu cek akses publik vs internal dinkes) | Mingguan per kabupaten/kota (data surveilans W2); histori bervariasi per wilayah, umumnya tahun berjalan + 1–2 tahun lalu | Data kesehatan agregat (bukan data pasien individual) — publik terbatas; sebagian modul SKDR untuk internal dinkes, verifikasi status akses publik sebelum scrape |
| 6 | Kemenkes — Dashboard/Profil Kesehatan Indonesia (data DBD tahunan) | https://data.kemkes.go.id atau publikasi "Profil Kesehatan Indonesia" (PDF/Excel tahunan) | health (DBD) | Download file resmi (Excel/PDF) dari portal Satu Data Kesehatan — bukan scrape HTML, bukan API | Tahunan, per provinsi; histori multi-tahun (laporan diterbitkan tiap tahun sejak lama) | Data publik pemerintah, biasanya dengan lisensi terbuka Satu Data Indonesia (CC-BY sejenis) — cek lisensi spesifik per dataset di portal |
| 7 | Dinas Kesehatan DKI Jakarta — Data DBD (Jakarta Satu Data / data.jakarta.go.id) | https://data.jakarta.go.id (cari dataset "demam berdarah dengue") | health (DBD, regional) | API resmi CKAN (data.jakarta.go.id berbasis platform Open Data / CKAN dengan endpoint JSON) atau download CSV | Bulanan/mingguan per kecamatan/kelurahan; histori beberapa tahun tergantung dataset | Portal Satu Data Jakarta umumnya berlisensi terbuka (cek badge lisensi per dataset — sering CC-BY atau setara) |
| 8 | BMKG — Data Online (Pusat Database) | https://dataonline.bmkg.go.id | weather | Scrape HTML/form (permintaan data per stasiun-tanggal, kadang perlu registrasi akun gratis) | Harian per stasiun cuaca (suhu, curah hujan, kelembapan, dst.); histori bisa puluhan tahun tergantung stasiun | Data publik BMKG untuk riset/pendidikan; sebagian permintaan data historis panjang perlu registrasi/ijin — bukan data komersial |
| 9 | BMKG — API Prakiraan Cuaca | https://data.bmkg.go.id/prakiraan-cuaca (endpoint publik, format XML/JSON per wilayah kode BMKG) | weather | API resmi (JSON/XML publik, tanpa key untuk endpoint prakiraan) | Per 3 jam untuk beberapa hari ke depan (bukan histori panjang) — cocok untuk seri pendek/nowcasting, bukan histori multi-tahun | Data publik BMKG, dipublikasikan untuk penggunaan umum; cantumkan sumber "BMKG" saat redistribusi |
| 10 | PLN — Statistik Ketenagalistrikan / Laporan Kinerja | https://web.pln.co.id (bagian publikasi/laporan tahunan) atau statistik.pln.co.id jika aktif | energy load | Download laporan resmi (PDF/Excel) — bukan API, bukan scrape HTML terstruktur | Tahunan (statistik ketenagalistrikan nasional) atau bulanan untuk sebagian laporan beban sistem; histori beberapa tahun per edisi laporan | Data publik BUMN, laporan resmi untuk publik — cek halaman hak cipta laporan sebelum redistribusi ulang skala besar |
| 11 | Open Power System Data (OPSD) — cadangan energy load non-Indonesia | https://data.open-power-system-data.org (time series package) | energy load (cadangan/kalibrasi, bukan Indonesia) | API/download resmi (CSV/JSON terdokumentasi penuh) | Per jam, multi-negara Eropa; histori bertahun-tahun (2006–sekarang tergantung negara) | Lisensi terbuka eksplisit (CC-BY / MIT tergantung sub-dataset) — dipakai hanya sebagai cadangan format/kalibrasi kode karena bukan sumber Indonesia, bukan untuk klaim generalisasi lapangan |

## Ringkasan cakupan domain wajib

- **Food price:** #1 (PIHPS/BI, wajib), #2, #3, #4.
- **Health/DBD:** #5 (SKDR/Kemenkes, wajib), #6, #7.
- **Weather:** #8, #9 (BMKG, wajib).
- **Energy load:** #10 (PLN, sumber Indonesia utama), #11 (OPSD, cadangan non-Indonesia untuk kalibrasi kode
  scraper bila sumber PLN tidak dapat diakses terprogram).

## Rekomendasi urutan untuk F4-02 (scraper satu sumber)

PIHPS/Bank Indonesia (#1) — sesuai default di issue F4-02 — direkomendasikan sumber pertama karena frekuensi
harian memberi seri terpanjang dan paling relevan untuk deret waktu di brief. BPS Web API (#4) adalah
alternatif dengan API resmi paling bersih (JSON + key) jika PIHPS ternyata sulit di-scrape terprogram.
