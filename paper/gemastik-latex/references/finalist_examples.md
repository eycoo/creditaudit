# Contoh Makalah yang Lolos ke Tahap Final GEMASTIK

Dua makalah referensi (Santoso et al., "MapReduce dan Klasterisasi K-Means…"
dan Firdaus et al., "Sistem Prediksi Multi-Horizon Harga Bitcoin…") lolos ke
tahap final. Gunakan keduanya untuk kalibrasi **struktur dan register**,
bukan untuk disalin isinya.

## Pola struktur yang sama-sama dipakai

Kedua makalah, meski topik beda total (NLP summarization vs. time-series
forecasting), memakai kerangka yang sama:

1. **Intisari** — mengikuti struktur wajib 4 bagian (lihat format_rules.md),
   ditutup dengan angka hasil kuantitatif konkret di kalimat terakhir
   (mis. skor ROUGE, MAPE per horizon).
2. **I. PENDAHULUAN** — ditulis sebagai argumen mengalir, bukan daftar poin:
   mulai dari skala masalah (statistik industri/global), lalu masalah
   spesifik, lalu pendekatan-pendekatan sebelumnya beserta kelemahannya
   (dengan sitasi), lalu celah penelitian, lalu kontribusi yang diusulkan,
   lalu manfaat/dampak. Firdaus menutup dengan framing kebijakan nasional
   ("early warning system bagi Bank Indonesia dan Kementerian Keuangan");
   Santoso menutup dengan framing "kemandirian bangsa". Framing dampak
   nasional/strategis di akhir Pendahuluan adalah pola yang konsisten di
   kedua makalah finalis — ini konvensi genre GEMASTIK, bukan basa-basi.
3. **II. KAJIAN TEORI / METODE** — Firdaus memakai kajian teori eksplisit
   (subsection per konsep: Bitcoin, data on/off-chain, investasi, time
   series, LSTM, attention) sebelum masuk ke usulan; Santoso langsung ke
   metode karena tinjauan pustaka sudah cukup padat di Pendahuluan. Pilih
   sesuai kompleksitas domain paper — domain yang butuh banyak istilah
   teknis baru (kripto, on-chain metrics) mendapat kajian teori terpisah.
4. **Dataset section dengan tabel variabel eksplisit** — kedua makalah
   punya tabel yang merinci: nama variabel, sumber data, metode akuisisi,
   timeframe, frekuensi. Ini bukan opsional; juri secara eksplisit menandai
   ketiadaan detail scraping (durasi, jumlah data, contoh sampel) sebagai
   kelemahan (lihat common_juri_complaints.md).
5. **Arsitektur/metodologi dengan diagram alur** — kedua makalah punya satu
   gambar (`Gambar 1`) yang merangkum alur sistem/model secara visual,
   dirujuk dari teks metodologi.
6. **Hasil dan Diskusi dengan tabel angka nyata** — Santoso: satu tabel
   perbandingan model utama + satu tabel per-dataset breakdown + satu tabel
   evaluasi kualitatif. Firdaus: satu tabel RMSE/MAPE per horizon + tabel
   norma bobot fitur + tabel SHAP top-5 per horizon. Pola: setiap klaim
   kuantitatif di prosa dirujuk balik ke satu sel spesifik di tabel
   (`Tabel~\ref{...}`), bukan angka mengambang tanpa tabel pendukung.
7. **Kesimpulan** — merangkum angka terbaik dari eksperimen, lalu diikuti
   Saran/Rekomendasi konkret dan actionable (bukan generic "penelitian
   selanjutnya dapat…"), sering dengan sub-nomor per rekomendasi.
8. **Referensi 15–35 item**, campuran jurnal, arXiv, laporan lembaga
   (Reuters, OECD, FRED, Statista/Microsoft) dan technical report.

## Register / gaya bahasa yang terlihat di kedua makalah

- Istilah teknis dipertahankan dalam bahasa Inggris dan di-italic:
  *fine-tuning*, *chunking*, *embedding*, *forward fill*, *early warning
  system*, *overfitting*, *hedging*. Padanan Indonesia dihindari.
- Akronim didefinisikan lengkap sekali lalu dipakai sebagai akronim
  seterusnya: "Low-Rank Adaptation (LoRA)", "Mean Absolute Percentage Error
  (MAPE)".
- Kalimat argumentatif-ilmiah dengan konektor eksplisit: "Namun,", "Oleh
  karena itu,", "Dengan demikian,", "Sebaliknya," — bukan gaya percakapan.
- Setiap paragraf tinjauan pustaka menyebut nama metode/model pembanding
  dan angka kinerjanya, lalu keterbatasannya, sebelum menyimpulkan celah:
  pola "[Metode X] mencapai [metrik Y], namun [keterbatasan Z] [sitasi]."
- Rasionalisasi desain arsitektur ditulis eksplisit sebagai sub-bagian
  sendiri (Firdaus: "4) Rasionalisasi desain" — tiap komponen arsitektur
  dijelaskan *mengapa* dipilih, bukan cuma *apa* itu).

## Yang TIDAK ada di kedua makalah finalis (hindari)

- Tidak ada penalaran/langkah yang tidak didukung angka — semua klaim hasil
  merujuk tabel dengan angka presisi (2-3 desimal untuk skor, persen dengan
  1-2 desimal).
- Tidak ada bagian yang mengaku hasil "awal"/belum lengkap tanpa penjelasan
  — kalau eksperimen memang belum final, itu ditulis eksplisit sebagai
  catatan fase (lihat draft `02_KrocoMasStanis.tex` milik pengguna sendiri
  sebagai contoh cara menandai ini dengan jujur: "Catatan penting.
  Penelitian masih pada Fase 1...").
- Tidak ada heading level 2 yang isinya cuma satu-dua kalimat pendek tanpa
  substansi — tiap subsection punya beberapa paragraf argumen.
