# Brief Penelitian v2 (Revisi Setelah Kritik Juri)

| | |
|---|---|
| **Judul resmi** | Peningkatan Keandalan dan Efisiensi Token LLM pada Data Time Series melalui Pendekatan Verifikasi Deterministik |
| **Nama kerja internal** | GEAR-TS (jangan dipakai di paper) |
| **Status** | Revisi brief lama, menutup dua kritik juri: kebaruan lemah dan kualitas teknis lemah |
| **Tenggat** | 5 hari, dengan fine-tune model dijalankan |

Catatan gaya: istilah teknis (grounding, token, reasoning, dataset, baseline, fine-tune, LLM) dibiarkan dalam bahasa Inggris. `operasi`, `langkah`, `verifikator` adalah istilah kanonik proyek.

---

## 0. Apa yang berubah dari brief lama

1. **Gap digeser.** Dari "menggabungkan penalaran terverifikasi dan hemat token" (terlihat inkremental) menjadi "menjaga reasoning tetap grounded justru ketika token dipangkas" (masalah baru yang nyata).
2. **Tambah bukti empiris.** RQ1 (model sekarang berhalusinasi) dan RQ2 (kurva tarik-menarik grounding lawan token) dijalankan lebih dulu, murah, tanpa fine-tune.
3. **Mekanisme adaptif dijelaskan konkret.** Bukan buzzword lagi: target latihnya adalah rantai operasi grounded terpendek yang cukup.
4. **Pipeline dataset dijelaskan.** Langkah scraping, sintesis, dan verifikasi label dieksplisitkan.
5. **Non-scalar grounding ditangani.** `deteksi_anomali` yang mengembalikan daftar indeks sekarang ikut diperiksa.
6. **Ketergantungan VeriTime dikurangi.** Kontribusi berdiri di atas temuan tarik-menarik dan dataset, bukan di atas klaim "VeriTime boros" yang belum dicek.

---

## 1. Masalah yang diangkat

**Konteks.** LLM pintar berbahasa, lemah berhitung. Kalau diberi sederet angka lalu diminta menyimpulkan, model cenderung menebak dari pola bahasa, bukan menghitung. Hasilnya bisa salah walau kalimatnya meyakinkan.

**Contoh.** Deret kasus DBD 16 minggu: `12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78`. Pertanyaan: apakah ada tanda outbreak? Jawaban benar: ada. Baseline awal sekitar 13 kasus, empat minggu terakhir naik dari 38 ke 78 (sekitar 105 persen), nilai akhir kira-kira 6 kali baseline. Model sekarang sering salah: bilang stabil padahal naik ke 78, salah menunjuk minggu lonjakan, atau bilang naik 30 persen padahal 105 persen.

**Masalah yang lebih dalam (inti gap baru).** Di bidang bertaruh tinggi seperti kesehatan dan pangan, reasoning harus bisa diaudit, artinya tiap angkanya bisa dicek (grounded). Tetapi ada dua kenyataan yang bertabrakan:

- Pendekatan reasoning terverifikasi yang ada membuat penalaran panjang dan boros token.
- Pendekatan reasoning hemat token yang ada hanya menjaga akurasi jawaban, dan tidak pernah mengecek apakah langkah-langkahnya jujur.

Akibatnya muncul tarik-menarik: **memangkas token bisa membuat jawaban tetap benar tetapi reasoning-nya diam-diam jadi tidak grounded.** Metode hemat token yang ada tidak menyadari ini karena hanya melihat akurasi. Belum ada yang menyelesaikan cara menjaga grounding tetap tinggi di bawah anggaran token, khususnya pada time series. Inilah masalah yang diangkat.

---

## 2. Solusi yang diberikan

Tiga bagian yang jangan tertukar: metode, dataset, metrik.

**2.1 Metode.** Dua komponen berbeda sifat:
- **Komponen model:** LLM hasil fine-tune (Qwen2.5-7B) yang menuliskan reasoning sebagai urutan `operasi` dari pustaka tetap, bukan prosa bebas.
- **Komponen program:** verifikator deterministik (Python + NumPy, tidak dilatih) yang menghitung ulang tiap operasi atas deret asli dan mengeceknya.
- **Grounding-aware adaptive reasoning:** panjang reasoning diatur agar sependek mungkin tetapi setiap langkah tetap grounded dan cukup untuk menjawab. Ini yang menjawab tarik-menarik di atas.

**2.2 Dataset.** Korpus reasoning time series terverifikasi dari sumber publik Indonesia, dibangun dengan verifikator di dalam loop (label bersih by construction), dan sengaja dibuat tidak sepele (ada ambiguitas, distraktor, dan kasus yang menjebak tiga pola gagal model).

**2.3 Metrik.** Skor grounding (deterministik, tanpa LLM penilai), selalu dilaporkan bersama akurasi jawaban dan jumlah token, supaya tarik-menariknya terlihat.

**Kebaruan.** Bukan penggabungan dua ide, melainkan (a) menemukan bahwa efisiensi naif mengorbankan grounding, dan (b) merancang mekanisme efisiensi yang sadar grounding untuk menyelesaikannya.

---

## 3. Pertanyaan penelitian (RQ)

- **RQ1 — Apakah masalahnya nyata?** Seberapa sering model yang ada sekarang berhalusinasi (skor grounding rendah) saat menalar time series, walau jawaban akhirnya kadang benar?
- **RQ2 — Apakah tarik-menariknya nyata? (RQ inti, kebaruan)** Ketika reasoning dipendekkan (token dikurangi), apakah grounding turun lebih cepat daripada akurasi jawaban?
- **RQ3 — Apakah solusinya bekerja?** Apakah metode kami menjaga grounding tetap tinggi pada token yang jauh lebih hemat, yaitu menang pada rasio grounding-per-token dibanding baseline reasoning panjang maupun baseline hemat yang buta grounding?
- **RQ4 — Komponen mana yang berperan? (ablation)** Berapa sumbangan tiap bagian: format operasi, target rantai grounded-terpendek, adaptivitas, dan fine-tune.

---

## 4. Metode step by step

### 4.1 Alur sistem saat menjawab (inference)

1. **Input:** deret angka + konteks singkat + satu pertanyaan.
2. **LLM menulis reasoning sebagai urutan operasi.** Tiap langkah: string operasi + angka hasil yang diklaim. Contoh DBD:
   - Langkah 1: `rata2(nilai[0:5])` = 13
   - Langkah 2: `persen_naik(nilai[11], nilai[15])` = 105,3
   - Langkah 3: `rasio(nilai[15], 13)` = 6,0
3. **Verifikator menghitung ulang tiap operasi** atas deret asli, lalu membandingkan hasil hitung ulang dengan angka yang diklaim, dalam toleransi. Menghasilkan skor grounding.
4. **Jawaban akhir:** label + tingkat keyakinan, disertai reasoning yang sudah tervalidasi.

### 4.2 Mekanisme reasoning adaptif yang sadar grounding (konkret)

Ini menjawab kritik "mekanisme adaptif kosong". Mekanismenya berbasis data, bukan RL, supaya muat 5 hari.

- **Target latih tiap sampel = rantai operasi grounded terpendek yang cukup.** Untuk tiap sampel, reasoning acuan dibuat sebagai urutan operasi paling pendek yang (a) tiap langkahnya lolos verifikator, dan (b) bersama-sama cukup untuk membenarkan jawaban. Tidak ada langkah mubazir.
- **Kesulitan menentukan panjang alami.** Deret berpola jelas menghasilkan rantai pendek; deret ambigu menghasilkan rantai lebih panjang. Tiap sampel diberi label kesulitan.
- **Model dilatih meniru rantai grounded-terpendek ini,** sehingga saat inference ia mengeluarkan reasoning yang panjangnya menyesuaikan kesulitan, tetapi tiap langkah tetap grounded.
- **Kendali opsional saat inference:** menambahkan tanda kesulitan atau anggaran maksimal langkah di prompt.
- **Kenapa ini menyelesaikan tarik-menarik:** tujuan latihnya secara harfiah adalah "reasoning terpendek yang tetap sepenuhnya grounded dan cukup", jadi efisiensi dan grounding dioptimalkan bersama, bukan ditukar buta.
- **Perluasan opsional (kalau waktu sisa):** RL dengan imbalan dari verifikator, misalnya `reward = skor_grounding − λ·jumlah_token`.

### 4.3 Pipeline konstruksi dataset (eksplisit)

Ini menjawab kritik "sintesis data tidak jelas".

1. **Kumpulkan deret nyata** dari sumber publik lewat scraping atau API (Tabel sumber di bawah).
2. **Buat pertanyaan** untuk tiap deret, mencakup empat jenis tugas: indikasi anomali/outbreak, karakterisasi tren, perbandingan segmen, dan penjelasan. Pertanyaan sengaja dibuat menuntut pemilihan operasi yang tidak langsung jelas, dan sebagian deret dibuat ambigu dengan distraktor.
3. **Hitung jawaban benar dengan rumus.**
4. **Sintesis reasoning acuan** sebagai rantai operasi grounded-terpendek (lihat 4.2); hitung nilai sebenarnya tiap langkah.
5. **Jalankan verifikator pada reasoning acuan.** Langkah yang tidak grounded diperbaiki atau dibuang. Label jadi bersih by construction.
6. **Beri label jenis tugas dan tingkat kesulitan,** lalu stratifikasi.
7. **Bagi data:** latih didominasi semi-sintetis (deret nyata atau terkendali + reasoning terverifikasi), uji didominasi deret asli. Anti-kebocoran: sumber pada uji tidak muncul di latih.

Sumber deret yang direncanakan: harga pangan PIHPS Bank Indonesia (harian), kasus penyakit dashboard Kemenkes (mingguan), cuaca BMKG (harian/jam), beban energi (jam). Untuk 5 hari, prioritaskan 1–2 domain yang matang dulu, bukan keempatnya setengah jadi.

### 4.4 Verifikator, skor grounding, dan operasi non-skalar

- **Grounding satu langkah skalar:** grounded bila `|hitung_ulang − klaim| ≤ max(abs_tol, rel_tol·|hitung_ulang|)`, default keduanya 0,01. Suku relatif menyesuaikan skala data antar-domain (harga 15000 vs z-score 2), jadi bedanya besaran sudah tertangani.
- **Justifikasi toleransi (kritik 2b):** jalankan uji sensitivitas kecil, variasikan `rel_tol` di {0,005; 0,01; 0,02; 0,05}, tunjukkan skor stabil dan halusinasi 30-vs-105 tetap tertangkap. Pertimbangkan toleransi lebih ketat untuk operasi berbasis bilangan bulat (kasus penyakit).
- **Operasi non-skalar (kritik 2c):** `deteksi_anomali` mengembalikan himpunan indeks. Grounding-nya dinilai dengan mencocokkan himpunan indeks hitung-ulang lawan yang diklaim (cocok persis, atau kemiripan Jaccard di atas ambang). Dengan ini operasi deteksi anomali, yang jadi inti contoh outbreak, ikut masuk metrik utama.
- **Semantik operasi yang masih provisional** (`deteksi_anomali`, `bandingkan_segmen`) difinalisasi lebih dulu (issue 01) karena menentukan kebenaran seluruh label.

### 4.5 Protokol fine-tune

QLoRA NF4 4-bit (rank 16–64, alpha 32, lr 1e-4–2e-4, cosine+warmup, bf16, 2–3 epoch), LLaMA-Factory + ZeRO-2, muat di GPU T4/V100. Model kelas 7B (Qwen2.5) dinilai cukup karena kekuatan proyek ada di data dan grounding.

---

## 5. Eksperimen dan hasil

Semua metrik deterministik: **akurasi jawaban**, **skor grounding** (utama), **jumlah token reasoning**.

### Eksperimen 1 — Uji halusinasi dasar (menjawab RQ1)

Uji model yang ada (Qwen2.5-7B tanpa fine-tune, dan bila memungkinkan satu model kelas GPT) pada benchmark uji. Ukur grounding dan akurasi.
**Hasil diharapkan:** akurasi lumayan tetapi grounding rendah, membuktikan model benar untuk alasan yang salah.
**Masuk ke Hasil:** tabel model × (akurasi, grounding).

### Eksperimen 2 — Kurva tarik-menarik grounding lawan token (menjawab RQ2, ini kebaruannya)

Pada model yang ada, minta reasoning dengan panjang berbeda-beda (lewat prompt pendek/panjang atau batas langkah). Ukur grounding dan akurasi di tiap panjang, lalu plot terhadap jumlah token.
**Hasil diharapkan:** saat reasoning dipendekkan, grounding turun lebih cepat daripada akurasi.
**Masuk ke Hasil:** satu grafik kurva. Ini temuan empiris yang membenarkan gap.

### Eksperimen 3 — Metode kami lawan baseline (menjawab RQ3)

Baseline:
- **B1:** LLM umum, prosa bebas, tanpa operasi.
- **B2:** reasoning operasi panjang tanpa kendali panjang (proksi arah VeriTime, diberi label jujur sebagai proksi).
- **B3:** reasoning pendek yang diatur panjangnya tetapi buta grounding (proksi arah SelfBudgeter di time series).
- **B4:** metode statistik murni (batas atas hitungan, tanpa penjelasan; menunjukkan kenapa LLM tetap perlu).
- **Kami:** model fine-tune + verifikator + adaptivitas sadar grounding.

**Hasil diharapkan:** grounding kami mendekati B2 tetapi token jauh lebih hemat, dan grounding kami di atas B3 pada token setara. Inilah kemenangan grounding-per-token.
**Masuk ke Hasil:** tabel semua metode × (akurasi, grounding, token), plus perbandingan grounding-per-token.

### Eksperimen 4 — Ablation (menjawab RQ4)

Matikan satu per satu: format operasi (ganti prosa bebas), target rantai grounded-terpendek (ganti panjang sembarang), adaptivitas, dan fine-tune. Ukur efeknya.
**Masuk ke Hasil:** tabel ablation.

### Hasil fondasi (sanity check, bukan hasil utama)

Verifikator mereproduksi reasoning jujur DBD (grounding 100 persen) dan menandai halusinasi (turun ke 66,7 persen), serta lolos 20 pengujian. **Sebut ini sebagai validasi verifikator, bukan "uji awal" hasil model.**

### Isi bagian Hasil (ringkas)

1. Statistik dataset: ukuran, distribusi tugas, strata kesulitan, sumber.
2. Tabel RQ1: grounding model tanpa fine-tune (bukti masalah).
3. Grafik RQ2: kurva grounding lawan token (temuan baru).
4. Tabel RQ3: metode lawan baseline (akurasi, grounding, token).
5. Tabel RQ4: ablation.
6. Validasi verifikator + uji sensitivitas toleransi.

---

## 6. Rencana kerja 5 hari

- **Hari 1:** siapkan benchmark uji kecil dari beberapa deret nyata; jalankan Eksperimen 1 dan 2 pada model tanpa fine-tune. Dua hasil pertama (RQ1, RQ2) sudah di tangan, tanpa fine-tune.
- **Hari 1–3:** bangun dataset (bagian terberat). Fokus 1–2 domain matang. Sintesis + verifikasi label.
- **Hari 3–4:** fine-tune Qwen2.5-7B dengan QLoRA di dataset.
- **Hari 4:** jalankan Eksperimen 3 (metode lawan baseline) dan Eksperimen 4 (ablation).
- **Hari 5:** tulis hasil, revisi bagian Kesenjangan, Kontribusi, Metodologi, dan Hasil pada paper.

**Rencana cadangan:** kalau dataset molor, RQ1 + RQ2 + dataset + verifikator sudah jadi kontribusi utuh, dengan RQ3/RQ4 sebagai hasil fine-tune yang menyusul. Jadi ada hasil pasti walau fine-tune tersendat.

---

## 7. Positioning dan etika

- **Positioning jujur:** jangan mengklaim reasoning time series belum tersentuh (mudah dipatahkan). Klaim yang benar: reasoning time series sedang jadi frontier 2026, tetapi menjaga grounding di bawah anggaran token belum digarap, dan dataset reasoning time series terverifikasi dari sumber lokal belum ada. Pertahankan kalimat kejujuran ini, pertegas klaim setelahnya.
- **Kurangi ketergantungan VeriTime:** bandingkan sebagai proksi yang diberi label jujur; kontribusi berdiri di atas temuan RQ2 dan dataset.
- **Etika:** sumber publik; sistem adalah penunjang keputusan, bukan nasihat medis atau finansial pribadi, dengan disclaimer; keluaran taruhan tinggi ditinjau manusia; reasoning yang grounded justru mendukung akuntabilitas karena jejaknya bisa diaudit.
