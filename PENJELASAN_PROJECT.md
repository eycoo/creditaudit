# Penjelasan Project: GEAR-TS — Penalaran Time Series yang Grounded dan Hemat Token

Dokumen ini menjelaskan project secara lengkap dan berurutan, mulai dari apa project-nya, latar belakang, masalah, solusi, cara kerja, alasan pemilihan solusi, eksperimen, sampai hal-hal yang dibandingkan. Tiap bagian diberi konteks dulu sebelum masuk ke isi, supaya mudah dipahami tanpa perlu baca dokumen teknis lain.

Sumber utama dokumen ini adalah `project_brief.md` dan `CONTEXT.md` di repo ini.

---

## 1. Project ini tentang apa

**Konteks:** Data time series (deret angka yang berurutan menurut waktu) ada di mana-mana: kasus penyakit per minggu, harga pangan per hari, beban listrik per jam, sinyal sensor. Selama ini yang paling banyak digarap adalah forecasting, yaitu meramal angka berikutnya. Padahal yang sering dibutuhkan bukan ramalan, melainkan tafsirannya: apakah lonjakan ini tanda wabah mulai terbentuk? Kemampuan menafsir inilah yang disebut reasoning (penalaran), dan bagian ini justru tertinggal.

Project ini membangun sistem yang bisa membaca sebuah deret angka lalu menalar langkah demi langkah untuk menjawab pertanyaan tentang deret itu, dengan dua sifat penting: **grounded** (tiap langkah berpijak ke perhitungan nyata, bukan tebakan bahasa) dan **hemat token** (panjang penalaran menyesuaikan tingkat kesulitan).

- **Input sistem:** deret angka plus konteks teks singkat dan satu pertanyaan.
- **Output sistem:** rangkaian langkah penalaran (tiap langkah berisi operasi dan angka hasilnya) plus jawaban akhir, di mana tiap angka bisa dicek ulang oleh program.

Sistem ini multimodal dalam arti memadukan deret angka dengan teks, bukan gambar. Modalitas gambar sengaja di luar lingkup.

---

## 2. Latar belakang

**Konteks:** LLM (model bahasa besar) sekarang jadi antarmuka universal untuk banyak hal. Tetapi ada satu kelemahan yang konsisten: model ini jago bahasa, lemah angka.

Ketika disuruh menalar atas banyak angka sekaligus, LLM cenderung mengandalkan pola bahasa, bukan komputasi sebenarnya. Akibatnya ia berhalusinasi: mengklaim tren, lokasi lonjakan, atau besaran kenaikan yang tidak sesuai data. Bahayanya, kalimat yang dihasilkan rapi dan percaya diri, sehingga salahnya tidak kelihatan.

Tahun 2025–2026 ini bidangnya sedang panas. Setelah reasoning model (yang menalar panjang) sukses di matematika dan coding, orang mulai membawanya ke domain non-teks. Time series adalah domain besar yang ternyata belum terpecahkan, dan bahkan ada temuan bahwa reasoning yang manjur di matematika tidak otomatis jalan di time series.

---

## 3. Masalah inti (dengan contoh nyata)

**Konteks:** Cara paling jelas melihat masalahnya adalah lewat satu contoh deret dan tiga cara model bisa salah.

Ambil deret kasus DBD mingguan sebuah kabupaten selama 16 minggu:

```
12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78
```

Pertanyaan: **apakah ada indikasi outbreak?** Jawaban benarnya **ya**, karena:

- baseline awal sekitar **13 kasus** (rata-rata lima minggu pertama),
- empat minggu terakhir naik dari 38 ke 78, yaitu sekitar **105%**,
- nilai akhir 78 kira-kira **6 kali** baseline.

Model sering keliru dengan tiga pola berbahaya:

1. **Menutupi bahaya** — menyimpulkan kasus "relatif stabil di kisaran belasan sampai dua puluhan", padahal jelas naik ke 78.
2. **Salah lokasi** — menyebut lonjakan utama di minggu ke-6, padahal minggu ke-6 cuma 18; lonjakan sebenarnya di minggu 12 ke atas.
3. **Salah besaran** — menyebut naik sekitar 30%, padahal aslinya sekitar 105% di empat minggu terakhir.

Ketiganya berbahaya justru karena kalimatnya meyakinkan. Inti masalah yang project ini selesaikan: **membuat penalaran atas angka bisa dicek kebenarannya, bukan sekadar terdengar benar.**

---

## 4. Solusi yang ditawarkan

**Konteks:** Solusinya punya tiga bagian yang jangan tertukar: dataset (bahan bakar), metode (cara kerja), dan metrik (alat ukur).

### 4.1 Dataset (kontribusi utama)

Korpus penalaran time series **terverifikasi**, dibangun sendiri dari sumber publik Indonesia yang nyata (bukan dataset Kaggle), disimpan dalam format JSONL. Tiap sampel: deret angka, satu pertanyaan, langkah penalaran yang **tiap angkanya sudah dicek**, dan jawaban akhir. Untuk lomba data mining, effort pembuatan data inilah yang dinilai paling tinggi.

### 4.2 Metode

Pemasangan **LLM hasil fine-tune** dengan **verifikator deterministik di luar model**, ditambah **reasoning adaptif** untuk hemat token. Dua komponen ini beda sifat: yang satu model yang dilatih, yang satu program murni yang tidak dilatih.

### 4.3 Metrik

**Skor grounding** sebagai ukuran kejujuran penalaran terhadap angka, dihitung secara deterministik tanpa LLM lain.

**Kejelasan penting:** kebaruan project ini bukan pada LLM-nya (LLM meminjam yang sudah ada lalu di-fine-tune). Kebaruan ada pada dataset buatan sendiri dan pada pasangan model-plus-verifikator yang membuat penalaran bisa dicek sekaligus hemat.

---

## 5. Cara kerja sistem

**Konteks:** Alurnya sederhana dan sengaja memisahkan siapa yang menalar dan siapa yang mengoreksi.

```
Deret angka + pertanyaan
   -> LLM (fine-tuned) menghasilkan langkah penalaran berbentuk operasi
   -> Verifikator deterministik menghitung ulang tiap operasi atas deret asli
   -> Cek kecocokan angka (dalam toleransi) => skor grounding + penalaran tervalidasi
   -> Jawaban akhir
```

**LLM yang menalar, program yang mengoreksi.** Model tidak menghitung sendiri di kepala; ia mengeluarkan rencana perhitungan (urutan operasi), lalu kalkulator Python deterministik yang mengeksekusi.

Untuk contoh DBD di atas, penalaran yang benar berbentuk begini (tiga langkah operasi):

| Langkah | Operasi | Hasil | Arti |
|---|---|---|---|
| 1 | `rata2(nilai[0:5])` | 13.0 | baseline awal 13 kasus |
| 2 | `persen_naik(nilai[11]->nilai[15])` | 105.3 | minggu 12 ke 16 naik 105% |
| 3 | `rasio(nilai[15], 13.0)` | 6.0 | nilai akhir 6x baseline |

Verifikator menjalankan ulang ketiga operasi atas deret asli. Kalau semua angka cocok, skor grounding 100%. Kalau model berhalusinasi (misalnya mengklaim langkah 2 hasilnya 30% padahal 105%), langkah itu ditandai tidak grounded dan skor turun (jadi 66,7%).

### Pustaka operasi

Langkah penalaran wajib memakai operasi dari pustaka yang terdefinisi, supaya tiap langkah bisa dieksekusi ulang:

`rata2` (rata-rata), `delta` (selisih), `persen_naik` (perubahan persen), `rasio` (perbandingan), `slope` (kemiringan tren), `min`/`max`, `z_score` (deviasi dalam simpangan baku), `deteksi_anomali` (titik lewat ambang), `bandingkan_segmen` (banding dua segmen waktu).

---

## 6. Kenapa solusi ini yang dipilih

**Konteks:** Tiap keputusan desain punya alasan yang bisa dipertahankan di depan juri.

1. **Kenapa dipisah model dan verifikator, bukan satu model saja?** Karena untuk alat yang jawabannya dipakai mengambil keputusan taruhan tinggi, angka harus bisa dipertanggungjawabkan. LLM rawan salah aritmatika, sementara program deterministik pasti benar dan murah. Satu model tunggal tidak memberi jejak yang bisa dicek. (Keputusan ini dicatat di ADR-0001.)

2. **Kenapa penalaran berbentuk operasi, bukan prosa bebas?** Karena prosa bebas tidak bisa diverifikasi angka per angka. Dengan operasi dari pustaka terdefinisi, verifikator bisa menjalankan ulang tiap langkah. Dataset mengajarkan struktur penalaran yang benar; verifikator menjamin aritmatikanya benar. Keduanya diperlukan. (ADR-0002.)

3. **Kenapa reasoning adaptif?** Karena menambahkan penalaran panjang yang verifiable ke time series membuatnya boros token. Deret dengan pola jelas cukup penalaran pendek; deret ambigu baru diberi penalaran panjang. Ini menekan token tanpa mengorbankan akurasi.

4. **Kenapa toleransi grounding pakai gabungan absolut dan relatif?** Karena angka yang disajikan sering dibulatkan (105,3 padahal hitung ulangnya 105,26). Toleransi `max(abs, rel × nilai)` membuat pembulatan tetap lolos, tapi kesalahan besaran nyata (30 vs 105) tetap ketahuan. Ini tombol kalibrasi, bukan kebetulan.

---

## 7. Konstruksi dataset (bagian yang paling nguli)

**Konteks:** Ini komponen paling menentukan nilai lomba, dan sengaja dibuat berat effort-nya.

1. **Sumber deret angka.** Diambil dari sumber publik nyata lewat API atau scraping: harga pangan PIHPS Bank Indonesia, kasus penyakit dashboard Kemenkes, cuaca BMKG, beban energi. Bukan dataset Kaggle.

2. **Lapisan penalaran (moat-nya).** Untuk tiap deret, disusun pertanyaan, dihitung jawaban benar dengan rumus, lalu disusun langkah penalaran yang tiap angkanya dicek ke deret. Langkah dibatasi ke pustaka operasi, sehingga bisa dieksekusi ulang.

3. **Semi-sintetis untuk skala, asli untuk uji.** Data latih didominasi semi-sintetis (deret nyata atau terkontrol, dipasangkan penalaran yang diverifikasi otomatis). Data uji didominasi deret asli agar terbukti model bekerja di data lapangan.

4. **Verifikator membersihkan label.** Sampel yang langkahnya tidak lolos verifikasi diperbaiki atau dibuang, sehingga label bersih **by construction**.

5. **Anti-kebocoran.** Sumber pada uji dipastikan tidak muncul di latih, agar hasil bukan hafalan pola.

Format akhir JSONL, satu baris satu sampel (skema di Lampiran A brief).

---

## 8. Eksperimen dan evaluasi

**Konteks:** Eksperimen dirancang untuk membuktikan masalahnya nyata dan solusinya bekerja.

**Pertanyaan penelitian:**

- **RQ1** — Seberapa sering model sekarang berhalusinasi saat menalar time series (skor grounding rendah meski jawaban kadang benar)?
- **RQ2** — Apakah metode kami menaikkan skor grounding tanpa menurunkan akurasi jawaban?
- **RQ3** — Apakah reasoning adaptif kami lebih hemat token dibanding reasoning panjang, pada akurasi setara?
- **RQ4** — Komponen mana yang paling berkontribusi (ablation)?

**Baseline pembanding:** LLM umum tanpa fine-tune (prosa bebas); LLM dengan CoT panjang verifiable tanpa efisiensi (proksi arah VeriTime); metode statistik murni (batas atas komputasi tanpa penjelasan).

**Tiga metrik, semuanya deterministik (tanpa LLM juri):**

1. **Akurasi jawaban** — persen sampel yang label jawaban akhirnya benar.
2. **Skor grounding (metrik utama)** — persen langkah penalaran yang angkanya cocok saat dihitung ulang (toleransi kecil). Mengukur kejujuran penalaran.
3. **Efisiensi token** — rata-rata token penalaran per sampel, dilaporkan bersama akurasi agar tradeoff-nya terlihat.

---

## 9. Posisi terhadap karya terkait

**Konteks:** Positioning ini menentukan pertahanan project di depan juri, jadi disusun jujur dan eksplisit.

- **VeriTime** (pembanding utama) — sudah menggarap reasoning time series yang bisa diverifikasi, tetapi arah itu menghasilkan penalaran panjang dan mahal. Pembeda kami: menggabungkan verifiable **dengan hemat token**, dan data dibangun sendiri dari konteks lokal.
- **SelfBudgeter** — menunjukkan reasoning bisa dibuat hemat dan adaptif terhadap kesulitan, tapi masih di domain matematika. Kami membawa gagasan ini ke time series.
- **MTBench** — menunjukkan model masih gagal pada reasoning gabungan angka plus teks; dipakai untuk menaikkan masalah di pendahuluan.

**Peringatan jujur (dari brief §3):** jangan mengklaim reasoning time series belum diteliti, karena itu salah dan mudah dipatahkan. Klaim yang benar: reasoning time series sedang jadi frontier panas 2026, tetapi **gabungan grounded plus hemat token belum ada yang menggarap**, dan **dataset reasoning time series terverifikasi dari sumber lokal belum ada**.

---

## 10. Etika dan legal

**Konteks:** Karena menyentuh domain kesehatan dan keuangan, ada rambu yang dijaga.

1. Sumber data publik; pengumpulan menghormati ketentuan layanan; tidak mengumpulkan data pribadi.
2. Sistem bersifat **decision support**, bukan nasihat medis atau finansial personal, dengan disclaimer jelas.
3. Penalaran yang grounded justru mendukung akuntabilitas, karena jejak perhitungannya bisa diaudit.
4. Untuk penggunaan taruhan tinggi, hasil model ditinjau manusia, bukan dijadikan keputusan otomatis.

---

## 11. Ringkasan satu paragraf

GEAR-TS membuat LLM menalar atas deret angka secara jujur ke angka sekaligus hemat token. Model mengeluarkan penalaran berbentuk operasi, verifikator deterministik menghitung ulang tiap operasi atas deret asli dan memberi skor grounding, dan panjang penalaran menyesuaikan kesulitan agar hemat. Kontribusi utamanya adalah dataset penalaran time series terverifikasi dari sumber publik Indonesia (nilai lomba data mining), ditambah metode model-plus-verifikator yang membuat penalaran bisa dicek. Kebaruannya bukan di modelnya, melainkan di data buatan sendiri dan di pasangan model-verifikator yang menutup celah "verifiable sekaligus hemat token" yang belum diambil orang di 2026.
