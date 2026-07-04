# Deteksi Multimodal Penyesatan Biaya pada Penawaran Kredit Digital Berbasis Penalaran Kuantitatif Bahasa Indonesia

| | |
|---|---|
| **Nama proyek** | Deteksi Multimodal Penyesatan Biaya pada Penawaran Kredit Digital Berbasis Penalaran Kuantitatif Bahasa Indonesia |
| **Versi dokumen** | 1.0 |
| **Domain** | Multimodal NLP, Financial Consumer Protection, Quantitative Reasoning |
| **Target instansi** | OJK, Satgas PASTI, IASC, ekosistem perlindungan konsumen keuangan |
| **Status** | Project brief / proposal penelitian |

---

## Daftar Isi

1. Ringkasan Eksekutif
2. Latar Belakang
3. Rumusan Masalah
4. Tujuan dan Kontribusi
5. Ruang Lingkup dan Batasan
6. Posisi terhadap Karya Terkait
7. Gambaran Metodologi
8. Tahap 1 — Konstruksi Dataset
9. Tahap 2 — Pengolahan Dataset
10. Tahap 3 — Arsitektur Model
11. Tahap 4 — Protokol Training
12. Tahap 5 — Desain Eksperimen
13. Tahap 6 — Evaluasi dan Metrik
14. Hasil yang Diharapkan
15. Analisis Risiko dan Mitigasi
16. Pertimbangan Etika dan Legal
17. Rencana Kerja dan Timeline
18. Kebutuhan Sumber Daya dan Stack
19. Referensi
20. Lampiran

---

## 1. Ringkasan Eksekutif

sistem yang kami tawarkan adalah sistem multimodal yang mengaudit penawaran kredit digital (iklan pinjol, paylater, tabel cicilan, potongan kontrak) untuk mengungkap biaya sebenarnya dan mendeteksi penyesatan dalam cara biaya itu dibingkai. Sistem menerima gambar penawaran sebagai input dan menghasilkan laporan terstruktur berisi term finansial yang terekstrak, komputasi biaya efektif sebenarnya, klasifikasi jenis penyesatan, status kepatuhan terhadap aturan OJK, skor risiko, dan penjelasan berbahasa Indonesia yang mudah dipahami awam.

Kontribusi utama proyek ada di dua sisi. Pertama, di sisi data, yaitu konstruksi dataset penalaran kuantitatif finansial berbahasa Indonesia melalui pipeline CoT distillation dan injeksi penyesatan sistematis, yang tidak dimiliki pihak lain. Kedua, di sisi metodologi, yaitu arsitektur modular yang memisahkan persepsi visual, penalaran kuantitatif dengan komputasi deterministik, klasifikasi, dan generasi penjelasan, sehingga angka yang dihasilkan dapat dipertanggungjawabkan.

Masalah yang diangkat bukan masalah sistemik yang di luar jangkauan model. Data pengaduan OJK menunjukkan bahwa akar persoalan adalah gap kemampuan berhitung konsumen, dan project ini menyelesaikan persis gap itu dengan mengerjakan matematika penawaran secara benar dan transparan.

---

## 2. Latar Belakang

### 2.1 Konteks

Layanan kredit digital di Indonesia berkembang pesat, mencakup paylater (Buy Now Pay Later), pinjaman daring legal (Pindar), dan pinjol ilegal yang terus bermunculan dengan nama baru. Regulator telah menetapkan aturan biaya yang jelas dan terukur. Berdasarkan Peta Jalan dan Surat Edaran OJK, suku bunga pinjaman konsumtif diturunkan bertahap hingga maksimal 0,1% per hari pada 2026, dengan batas total pengembalian (lock cap) sebesar 100% dari pokok pinjaman. Untuk paylater, POJK Nomor 32 Tahun 2025 mewajibkan penyelenggara menampilkan rincian bunga, biaya administrasi, dan denda keterlambatan secara transparan sejak awal transaksi.

### 2.2 Masalah Inti: Gap Penalaran Kuantitatif

Perlindungan di atas kertas tidak otomatis dipahami konsumen. Beban biaya sebuah penawaran adalah hasil dari perhitungan banyak langkah: pokok, bunga harian, tenor, denda berbasis sisa pokok, biaya admin di depan, dan syarat tersembunyi di fine print. Mayoritas konsumen tidak mampu mengerjakan rantai hitung ini, dan justru di sinilah celah penyesatannya. Framing seperti "bunga hanya 0,4% per hari" atau "cicilan ringan" terdengar kecil, padahal biaya efektif totalnya bisa jauh lebih besar.

Data pengaduan OJK memperkuat diagnosis ini. Pengaduan terkait denda keterlambatan tercatat naik sekitar 35% per Januari 2026, dan sebagian besar keluhan berasal dari pengguna yang tidak mengetahui adanya batas maksimal denda serta salah dalam menghitung. Kesalahan yang umum adalah menghitung denda dari limit awal, bukan dari sisa pokok. Pada sisi ilegal, praktiknya jauh lebih parah, dengan bunga 2% hingga 4% per hari dan potongan biaya admin di depan yang bisa mencapai 40% dari nominal, semuanya disamarkan.

Poin kunci yang membedakan proyek ini: akar masalahnya adalah gap penalaran kuantitatif, bukan masalah sistemik yang tidak bisa disentuh model. Sebuah mesin yang mampu membaca penawaran dan mengerjakan matematikanya dengan benar untuk mengungkap biaya sebenarnya menyelesaikan masalah itu secara langsung.

### 2.3 Urgensi 2026

Tahun 2026 adalah momen transisi regulasi. Bunga pinjaman turun bertahap ke 0,1% per hari, POJK paylater mulai berjalan, dan OJK menekankan kewajiban transparansi biaya. Namun penegakan transparansi ini sulit di-scale secara manual, terutama menghadapi pinjol ilegal yang berganti nama hampir setiap hari dan menyamar menjadi aplikasi legal. Pada saat yang sama, penipuan berbasis penyesatan finansial menjadi persoalan nasional dengan volume pengaduan yang tinggi. Alat yang dapat secara otomatis membaca penawaran, menghitung biaya sebenarnya, dan menandai framing yang menyesatkan mengisi kebutuhan pengawasan yang nyata dan mendesak.

---

## 3. Rumusan Masalah

1. Bagaimana mengekstrak term finansial terstruktur dari gambar penawaran kredit yang bervariasi tata letaknya, termasuk informasi yang disembunyikan di fine print?
2. Bagaimana menghitung biaya efektif sebenarnya dari sebuah penawaran secara akurat dan dapat diaudit, mengingat model bahasa rawan salah aritmatika?
3. Bagaimana mendeteksi dan mengklasifikasikan jenis penyesatan biaya, serta menandai pelanggaran terhadap batas yang ditetapkan OJK?
4. Bagaimana membangun dataset penalaran kuantitatif finansial berbahasa Indonesia dalam skala memadai tanpa dataset berlabel yang tersedia publik?

---

## 4. Tujuan dan Kontribusi

**Tujuan umum.** Membangun sistem multimodal yang mengubah penawaran kredit dengan framing menyesatkan menjadi laporan biaya riil yang jujur beserta label alasan penyesatannya.

**Tujuan khusus.**

1. Menyusun taksonomi penyesatan biaya kredit digital di konteks Indonesia.
2. Membangun pipeline konstruksi dataset sintetis melalui CoT distillation dan injeksi penyesatan, dilengkapi data asli hasil scraping untuk validasi.
3. Mengembangkan arsitektur modular perception, reasoning, classification, dan explanation.
4. Melakukan evaluasi menyeluruh per modul dan end-to-end, termasuk studi ablasi.

**Kontribusi.**

1. **Dataset.** Korpus penalaran kuantitatif finansial berbahasa Indonesia dengan pasangan berlabel (penawaran, biaya sebenarnya, jenis penyesatan) yang dibangun dari kemampuan reasoning distillation yang tidak dimiliki pihak lain.
2. **Metodologi.** Desain program-of-thought dengan komputasi deterministik untuk menjamin akurasi numerik pada tugas audit finansial.
3. **Taksonomi.** Kerangka kategori penyesatan biaya yang dapat dipakai ulang untuk riset dan pengawasan.
4. **Sistem.** Prototipe end-to-end yang dapat di-deploy sebagai alat konsumen maupun mesin screening instansi.

---

## 5. Ruang Lingkup dan Batasan

**Termasuk dalam lingkup.**

- Penawaran kredit digital konsumtif: pinjol/Pindar, paylater, dan tabel cicilan.
- Modalitas input berupa gambar (screenshot, foto) dengan teks opsional.
- Bahasa Indonesia.
- Deteksi penyesatan pada dimensi biaya dan kepatuhan terhadap batas OJK.

**Di luar lingkup.**

- Penilaian kelayakan kredit atau credit scoring peminjam.
- Nasihat finansial personal (sistem bersifat decision support, bukan financial advisor).
- Deteksi penipuan non-biaya seperti phishing atau malware pada aplikasi.
- Bahasa daerah dan penawaran berbahasa asing.

**Asumsi.**

- Gambar penawaran cukup terbaca untuk OCR dan parsing.
- Aturan OJK yang dipakai sebagai acuan kepatuhan bersifat versi tertentu dan dapat diperbarui.

---

## 6. Posisi terhadap Karya Terkait

Agar novelty jelas dan tidak overclaim, posisi proyek dijelaskan terhadap tiga area.

**Deteksi penipuan finansial.** Sebagian besar riset dan produk berfokus pada klasifikasi legal atau ilegal, deteksi phishing, atau analisis transaksi. project ini berbeda karena fokus pada penalaran biaya, yaitu mengerjakan matematika penawaran untuk mengungkap penyesatan, bukan sekadar mengklasifikasi kanal atau domain.

**Multimodal math reasoning.** Benchmark seperti MathVista dan MathVerse menguji kemampuan model menyelesaikan soal matematika dengan gambar. project ini memakai kemampuan serupa tetapi pada domain terapan finansial in-the-wild berbahasa Indonesia, yang belum tersedia.

**Misconception dan error mining.** Kompetisi seperti Eedi "Mining Misconceptions in Mathematics" (2024) menangani miskonsepsi pada soal pilihan ganda berbahasa Inggris. project ini memindahkan gagasan deteksi kesalahan reasoning ke ranah penyesatan biaya finansial, dengan input multimodal dan target berlapis. Ini disebutkan secara eksplisit sebagai pembeda, bukan diklaim sebagai konsep yang belum pernah ada sama sekali.

Ringkasnya, kebaruan project ini terletak pada kombinasi domain (perlindungan konsumen keuangan Indonesia), aset data (reasoning kuantitatif Indonesia hasil distillation), dan desain (program-of-thought dengan komputasi deterministik untuk audit).

---

## 7. Gambaran Metodologi

Prinsip desain utama adalah pipeline modular, bukan satu model tunggal yang mengerjakan semua. Alasannya, untuk alat audit biaya, angka harus dapat dipertanggungjawabkan, sementara model bahasa rawan salah aritmatika. Tugas dipisah: persepsi visual diserahkan ke VLM, komputasi pasti diserahkan ke kalkulator deterministik, aturan diserahkan ke rule engine, dan penalaran serta verbalisasi diserahkan ke reasoning model. Pemisahan ini juga memudahkan debugging dan evaluasi per komponen.

Alur besar sistem terdiri dari empat modul berurutan.

```
Gambar penawaran
   -> Modul 1: Persepsi & Ekstraksi (VLM)            -> JSON term finansial
   -> Modul 2: Penalaran Kuantitatif (reasoning + kalkulator) -> biaya efektif sebenarnya
   -> Modul 3: Klasifikasi & Cek Kepatuhan OJK       -> label penyesatan + flag pelanggaran + skor severity
   -> Modul 4: Generasi Penjelasan                   -> ringkasan bahasa awam
   -> Laporan audit terstruktur
```

Tahapan penelitian dijalankan urut: konstruksi dataset, pengolahan dataset, pembangunan arsitektur model, training, eksperimen dan ablasi, lalu evaluasi.

---

## 8. Tahap 1 — Konstruksi Dataset

Ini adalah kontribusi inti sekaligus komponen yang paling menentukan nilai penelitian. Dataset dibangun dari dua sumber yang saling melengkapi: sintetis untuk training berskala besar dan asli untuk pengujian realisme.

### 8.1 Taksonomi Penyesatan Biaya

Taksonomi menjadi fondasi label untuk seluruh sistem. Kategori disusun berbasis praktik nyata yang terdokumentasi dari data OJK dan pelaporan lapangan. Detail lengkap beserta metode injeksi ada di Lampiran C. Ringkasannya:

| Kode | Kategori | Deskripsi singkat |
|---|---|---|
| P1 | Misrepresentasi suku bunga | Membingkai bunga harian kecil tanpa konteks total, atau menyamarkan basis flat vs efektif |
| P2 | Biaya siluman | Potongan admin di depan, provisi, atau asuransi bundling yang tidak disebut di headline |
| P3 | Salah basis perhitungan denda | Denda dihitung dari limit awal, bukan sisa pokok, atau denda beranak tanpa transparansi |
| P4 | Penyamaran struktur cicilan | "Cicilan ringan" tanpa menyebut tenor panjang sehingga total membengkak |
| P5 | Framing visual menyesatkan | Angka menarik di-highlight, biaya asli disembunyikan di fine print |
| P6 | Klaim palsu atau bait | "Bunga 0%" atau "tanpa biaya" yang tidak sepenuhnya benar |
| R1 | Indikator ilegalitas | Bunga di atas batas OJK, permintaan akses berlebihan, penawaran via WA/SMS tanpa pengajuan |

Taksonomi bersifat multi-label karena satu penawaran dapat memuat beberapa trik sekaligus, dan hierarkis karena P1 sampai P6 adalah penyesatan biaya sedangkan R1 adalah red flag legalitas.

### 8.2 Data Sintetis via CoT-Injection

Masalah terbesar tugas ini adalah tidak adanya data kesalahan berlabel. Solusinya memanfaatkan pipeline CoT distillation yang sudah dikuasai (basis IndoMathReason, Qwen2.5-7B yang di-fine-tune dari distilasi DeepSeek-R1). Langkahnya:

1. **Definisikan skenario penawaran.** Susun template parametrik: pokok, rentang bunga, tenor, jenis denda, biaya admin, tenor. Sampling parameter menghasilkan ribuan skenario unik.
2. **Distilasi reasoning benar.** Untuk tiap skenario, hasilkan CoT langkah demi langkah yang benar untuk menghitung biaya efektif sebenarnya, lalu verifikasi dengan kalkulator deterministik agar dijamin akurat.
3. **Injeksi penyesatan.** Terapkan transformasi presentasi berbasis taksonomi (Lampiran C) yang membuat penawaran tampak menyesatkan sambil menjaga kebenaran yang tersembunyi tetap dapat dihitung. Label kategori penyesatan mengikuti transformasi yang diterapkan.
4. **Hasilkan tuple berlabel.** Output tiap sampel: teks penawaran, term ground truth, biaya sebenarnya ground truth, label penyesatan, status kepatuhan OJK, dan CoT referensi.

Keunggulan pendekatan ini adalah label yang otomatis dan presisi, serta skala yang tidak terbatas oleh anotasi manual. Tidak ada tim lain yang dapat mereplikasi ini tanpa kemampuan menghasilkan reasoning kuantitatif Indonesia yang faithful.

### 8.3 Data Asli via Scraping

Untuk realisme dan pengujian generalisasi, dikumpulkan penawaran asli:

- **Sumber.** Screenshot iklan dan halaman aplikasi pinjol/paylater dari Play Store, media sosial, dan grup pesan, serta materi promosi publik.
- **Anchor label.** Daftar penyelenggara legal dan ilegal OJK dipakai sebagai anchor untuk label R1 (legalitas).
- **Anotasi manual.** Sampel asli dianotasi mengikuti taksonomi dan skema JSON yang sama, oleh minimal dua anotator dengan pengukuran inter-annotator agreement (Cohen atau Fleiss kappa) untuk menjamin reliabilitas label.
- **Anonimisasi.** Semua data pribadi pada screenshot (nama, nomor, foto) di-blur sebelum diproses (lihat Bab 16).

### 8.4 Rendering Gambar Sintetis

Data sintetis pada 8.2 masih berupa teks. Untuk melatih modul persepsi, teks tersebut dirender menjadi gambar penawaran yang menyerupai aslinya:

- Bangun bank template layout iklan yang divariasikan: jenis dan ukuran font, posisi fine print, warna, tabel cicilan, dan penekanan visual.
- Tempelkan angka dari data sintetis ke template, sehingga penyesatan visual (P5) benar-benar terwujud secara spasial, misalnya angka besar di-highlight dan biaya asli dikecilkan.
- Variasikan kondisi tangkapan (resolusi, kompresi, sedikit distorsi) agar model robust terhadap foto layar nyata.

### 8.5 Skema Anotasi dan Ground Truth

Skema JSON tetap dipakai konsisten untuk data sintetis dan asli (lihat Lampiran A). Ground truth biaya sebenarnya selalu dihitung dengan kalkulator deterministik yang mengikuti aturan OJK, agar konsisten dan dapat diverifikasi. Setiap sampel menyimpan: field term, biaya sebenarnya, label penyesatan multi-label, flag kepatuhan, dan penjelasan referensi.

### 8.6 Statistik dan Pembagian Dataset

- **Komposisi.** Training didominasi data sintetis. Validasi campuran. Test didominasi data asli untuk mengukur generalisasi ke lapangan.
- **Stratifikasi.** Pembagian distratifikasi berdasarkan kategori penyesatan dan status legalitas agar tiap kelas terwakili.
- **Anti-kebocoran.** Template dan sumber pada test dipastikan tidak muncul pada training, agar hasil bukan sekadar hafalan pola sintetis.

---

## 9. Tahap 2 — Pengolahan Dataset

Preprocessing menyiapkan data mentah menjadi input siap latih.

1. **Preprocessing gambar.** Deskew, denoise, normalisasi resolusi, dan konversi format. Untuk foto layar nyata, koreksi perspektif ringan.
2. **Deteksi tata letak.** Segmentasi region teks untuk membantu VLM mengaitkan penekanan visual dengan konten.
3. **OCR fallback.** OCR (misalnya PaddleOCR) dipakai sebagai fallback dan sebagai fitur pembanding untuk eksperimen ablasi (VLM vs OCR-plus-teks).
4. **Normalisasi teks dan angka.** Standarisasi format rupiah, persen, tanda desimal, dan satuan waktu (harian, bulanan, tahunan).
5. **Validasi skema.** Semua sampel divalidasi terhadap skema JSON. Sampel cacat dibuang atau diperbaiki.
6. **Tokenisasi dan formatting ChatML.** Data reasoning diformat ke ChatML sesuai kebutuhan fine-tuning, memanfaatkan format yang sudah dikuasai.
7. **Splitting final.** Terapkan pembagian train, validation, test sesuai 8.6 dengan seed tetap untuk reprodusibilitas.

---

## 10. Tahap 3 — Arsitektur Model

### 10.1 Modul 1 — Persepsi dan Ekstraksi

- **Fungsi.** Membaca gambar penawaran dan mengubahnya menjadi data terstruktur.
- **Model.** Vision-Language Model, kandidat Qwen2.5-VL-7B-Instruct. Dipilih VLM, bukan OCR biasa, karena penyesatan sering berada pada tata letak, sehingga posisi dan penekanan visual perlu ditangkap.
- **Input.** Gambar penawaran (plus teks opsional).
- **Output.** JSON skema tetap: pokok, bunga (nominal dan basis), tenor, denda, biaya admin, potongan di depan, syarat tersembunyi, serta penanda elemen yang di-highlight dan yang dikecilkan.
- **Teknik kunci.** Constrained decoding atau structured output agar model dipaksa mengisi skema dan tidak mengarang format.

### 10.2 Modul 2 — Penalaran Kuantitatif

- **Fungsi.** Menghitung biaya sebenarnya dari term yang diekstrak. Ini jantung sistem dan tempat aset dataset dipakai langsung.
- **Model.** Reasoning model hasil fine-tune dari dataset CoT (basis IndoMathReason), di-fine-tune lanjut pada CoT finansial.
- **Teknik kunci.** Program-of-thought, bukan chain-of-thought biasa. Model tidak menghitung sendiri di kepala, melainkan mengeluarkan rencana perhitungan terstruktur (urutan operasi yang mereferensikan field terekstrak), lalu kalkulator Python deterministik yang mengeksekusi. Dataset mengajarkan struktur reasoning yang benar, kalkulator menjamin aritmatika benar. Keduanya diperlukan.
- **Input.** JSON term dari Modul 1.
- **Output.** Biaya efektif sebenarnya: total bayar, dana bersih diterima, biaya dalam rupiah dan persen.

### 10.3 Modul 3 — Klasifikasi dan Cek Kepatuhan

- **Fungsi.** Membandingkan framing iklan dengan hasil hitungan, memberi label jenis penyesatan (multi-label), lalu memeriksa kepatuhan OJK.
- **Model.** Classification head di atas embedding, atau LLM dengan output terstruktur, untuk label penyesatan. Cek kepatuhan bersifat rule-based dan tidak dilatih, misalnya bunga konsumtif di atas 0,1% per hari atau total denda plus bunga di atas 100% pokok langsung di-flag.
- **Input.** Hasil Modul 1 dan 2.
- **Output.** Label penyesatan, flag pelanggaran, dan skor severity.

### 10.4 Modul 4 — Generasi Penjelasan

- **Fungsi.** Menerjemahkan hasil menjadi kalimat yang dipahami awam.
- **Model.** Reasoning model yang sama, dipakai untuk verbalisasi.
- **Input.** Semua hasil modul sebelumnya.
- **Output.** Ringkasan bahasa Indonesia yang grounded ke angka kalkulator, sehingga tidak dapat mengarang.

---

## 11. Tahap 4 — Protokol Training

Semua fine-tuning memakai LoRA atau QLoRA 4-bit agar muat pada GPU T4 atau V100. Karena aritmatika di-offload ke kalkulator, model 7B sudah memadai dan tidak perlu ukuran besar.

**Konfigurasi umum (kandidat awal, akan di-tuning).**

| Parameter | Nilai kandidat |
|---|---|
| Metode | QLoRA (kuantisasi NF4 4-bit) |
| LoRA rank (r) | 16 sampai 64 |
| LoRA alpha | 32 |
| LoRA dropout | 0,05 |
| Target modules | proyeksi attention dan MLP |
| Learning rate | 1e-4 sampai 2e-4 |
| Scheduler | cosine dengan warmup |
| Precision | bf16 |
| Epoch | 2 sampai 3 |
| Batch | efektif via gradient accumulation |
| Framework | LLaMA-Factory + DeepSpeed ZeRO-2 |

**Per modul.**

- **Modul 1 (VLM).** Fine-tune pada pasangan gambar ke JSON. Perhatikan penanganan resolusi gambar dan panjang output terstruktur.
- **Modul 2 (reasoning).** Fine-tune lanjut model reasoning pada CoT finansial hasil pipeline, dengan format program-of-thought.
- **Modul 3 (classifier).** Melatih head klasifikasi ringan; komponen rule engine tidak dilatih.
- **Kalkulator dan rule engine.** Tidak ada training, murni deterministik.

**Reprodusibilitas.** Seed tetap, pencatatan konfigurasi dan versi model, serta logging eksperimen (misalnya Weights & Biases) untuk semua run.

---

## 12. Tahap 5 — Desain Eksperimen

### 12.1 Pertanyaan Penelitian

- **RQ1.** Apakah VLM dapat mengekstrak term finansial terstruktur dari gambar penawaran nyata secara andal, termasuk dari fine print, lintas variasi tata letak?
- **RQ2.** Apakah program-of-thought dengan kalkulator deterministik menghasilkan komputasi biaya yang lebih akurat dibanding chain-of-thought end-to-end untuk reasoning finansial Indonesia?
- **RQ3.** Apakah data sintetis hasil CoT-injection meningkatkan generalisasi ke penawaran asli dibanding hanya melatih pada data asli yang terbatas?
- **RQ4.** Seberapa baik sistem mendeteksi dan mengklasifikasikan jenis penyesatan serta menandai pelanggaran OJK?
- **RQ5.** Bagaimana perbandingan pipeline modular dengan baseline VLM monolitik dari sisi akurasi, interpretabilitas, dan biaya komputasi?

### 12.2 Baseline

1. **OCR plus LLM teks.** Tanpa informasi tata letak visual, menguji kontribusi modalitas visual (menjawab RQ1 dan RQ5).
2. **VLM monolitik end-to-end.** Gambar langsung ke jawaban akhir tanpa pemisahan modul (menjawab RQ2 dan RQ5).
3. **Kalkulator saja.** Ekstraksi manual atau ideal lalu kalkulator, sebagai batas atas komputasi tanpa reasoning model.

### 12.3 Studi Ablasi

| Ablasi | Yang diuji | RQ terkait |
|---|---|---|
| Dengan vs tanpa kalkulator deterministik | Nilai program-of-thought | RQ2 |
| Dengan vs tanpa data sintetis | Nilai CoT-injection | RQ3 |
| VLM vs OCR-plus-teks untuk ekstraksi | Kontribusi tata letak visual | RQ1 |
| Ukuran model reasoning berbeda | Sensitivitas skala | RQ2 |
| Rule-based vs learned compliance | Nilai aturan deterministik | RQ4 |

---

## 13. Tahap 6 — Evaluasi dan Metrik

Evaluasi dilakukan per modul agar jelas kekuatan dan kelemahan tiap komponen, lalu end-to-end.

| Komponen | Metrik |
|---|---|
| Ekstraksi (Modul 1) | Field-level precision, recall, F1; exact-match pada field numerik |
| Komputasi biaya (Modul 2) | MAE dan MAPE terhadap ground truth; persentase prediksi dalam toleransi |
| Klasifikasi penyesatan (Modul 3) | Multi-label F1 (macro dan micro); hierarchical F1 |
| Flag kepatuhan (Modul 3) | Precision, recall, F1; confusion matrix |
| Penjelasan (Modul 4) | Faithfulness (konsistensi kalimat dengan angka kalkulator); human eval faktualitas |
| End-to-end | Skor komposit gabungan; analisis kualitatif kasus sulit |

Pemisahan metrik ini penting karena tiap komponen memikul risiko yang berbeda. Evaluasi juga mencakup analisis error terstruktur untuk mengidentifikasi mode kegagalan.

---

## 14. Hasil yang Diharapkan

1. Dataset penalaran kuantitatif finansial Indonesia berlabel, siap dipakai ulang.
2. Sistem end-to-end dengan performa terukur pada penawaran asli.
3. Bukti empiris bahwa program-of-thought dan data sintetis CoT-injection meningkatkan akurasi dan generalisasi (verifikasi RQ2 dan RQ3).
4. Taksonomi penyesatan biaya yang tervalidasi.
5. Prototipe deployment untuk konsumen (bot foto penawaran) dan instansi (screening batch).

---

## 15. Analisis Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Injeksi penyesatan sintetis tidak realistis | Model bagus di sintetis, jeblok di asli | Kalibrasi injeksi dengan referensi lapangan; test didominasi data asli; iterasi taksonomi |
| Ground truth biaya salah | Label komputasi tidak valid | Kalkulator deterministik mengikuti aturan OJK; verifikasi silang; review ahli |
| Ekstraksi gagal pada layout ekstrem | Error merambat ke modul berikutnya | Augmentasi variasi layout; fallback OCR; confidence gating |
| Domain gap math sekolah ke finansial | Reasoning tidak transfer | Fine-tune lanjut pada CoT finansial; jangan klaim dataset mentah langsung menyelesaikan |
| Data asli terbatas atau sulit diakses | Test kurang representatif | Perbanyak sumber; kombinasikan dengan sintetis; dokumentasikan keterbatasan |
| Salah klasifikasi merugikan penyelenggara sah | Risiko reputasi dan hukum | Threshold hati-hati; human-in-the-loop untuk penggunaan penegakan; sistem bersifat penanda, bukan penuduh |

---

## 16. Pertimbangan Etika dan Legal

1. **Privasi data.** Screenshot dapat memuat data pribadi. Semua data pribadi dianonimkan (blur) sebelum diproses. Tidak ada pengumpulan data pribadi peminjam. Penanganan mengikuti prinsip UU Perlindungan Data Pribadi.
2. **Kepatuhan scraping.** Pengumpulan menghormati ketentuan layanan sumber dan hanya mengambil materi promosi publik.
3. **Bukan nasihat finansial.** Sistem bersifat decision support dan diagnostik biaya, bukan financial advisor. Output menyertakan disclaimer.
4. **Menghindari pencemaran nama.** Sistem menandai indikasi pada penawaran, bukan menuduh entitas bernama secara definitif. Untuk penggunaan penegakan, hasil ditinjau manusia.
5. **Tidak memberi celah penghindaran.** Sistem tidak dirancang membantu pihak ilegal menyamarkan penyesatan.
6. **Transparansi model.** Karena memakai program-of-thought, jejak perhitungan dapat diaudit, mendukung akuntabilitas.

---

## 17. Rencana Kerja dan Timeline

Timeline indikatif berbasis fase. Durasi disesuaikan dengan sumber daya.

| Fase | Aktivitas | Estimasi |
|---|---|---|
| 1 | Finalisasi taksonomi dan skema JSON | Minggu 1 sampai 2 |
| 2 | Pipeline data sintetis dan kalkulator deterministik | Minggu 2 sampai 4 |
| 3 | Scraping dan anotasi data asli | Minggu 3 sampai 6 |
| 4 | Rendering gambar sintetis dan preprocessing | Minggu 4 sampai 6 |
| 5 | Training Modul 1 dan 2 | Minggu 6 sampai 8 |
| 6 | Training Modul 3 dan integrasi pipeline | Minggu 8 sampai 9 |
| 7 | Eksperimen, ablasi, evaluasi | Minggu 9 sampai 11 |
| 8 | Prototipe deployment dan penulisan laporan | Minggu 11 sampai 12 |

Titik paling menentukan ada di Fase 1 dan 2, karena taksonomi dan skema injeksi mendefinisikan label untuk seluruh sistem.

---

## 18. Kebutuhan Sumber Daya dan Stack

**Komputasi.** GPU T4 atau V100 (Colab atau Kaggle) dengan strategi QLoRA. Pipeline inference berjalan berurutan.

**Stack.**

| Komponen | Tools |
|---|---|
| Persepsi | Qwen2.5-VL-7B-Instruct |
| Reasoning | Qwen2.5-7B fine-tuned (basis IndoMathReason) |
| Training | LLaMA-Factory, DeepSpeed ZeRO-2, PEFT |
| Komputasi numerik | Modul kalkulator Python deterministik |
| Kepatuhan | Rule engine berbasis aturan OJK |
| OCR fallback | PaddleOCR |
| Rendering gambar | PIL/Pillow dengan bank template |
| Scraping | Playwright atau Selenium |
| Anotasi | Label Studio |
| Serving | FastAPI |
| Eksperimen logging | Weights & Biases |

---

## 19. Referensi

Sumber regulasi dan data (deskriptif, versi dapat diperbarui):

- OJK. POJK Nomor 32 Tahun 2025 tentang Penyelenggaraan Layanan Buy Now Pay Later.
- OJK. POJK Nomor 40 Tahun 2024 terkait penyelenggaraan layanan pendanaan bersama berbasis teknologi informasi (rebranding Pindar).
- OJK. SEOJK Nomor 19/SEOJK.06/2023 tentang penurunan bertahap batas manfaat ekonomi.
- OJK. Data pengaduan konsumen sektor jasa keuangan, periode Januari 2026 (kenaikan pengaduan denda keterlambatan sekitar 35%).
- Pelaporan lapangan dan pers mengenai praktik pinjol ilegal (bunga 2 sampai 4 persen per hari, potongan admin di depan hingga 40 persen).

Referensi metode:

- Hu et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models.
- Dettmers et al. (2023). QLoRA: Efficient Finetuning of Quantized LLMs.
- Wei et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models.
- Gao et al. (2023). PAL: Program-aided Language Models.
- Qwen Team (2025). Qwen2.5-VL Technical Report.
- DeepSeek-AI (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.
- Analisis kompetisi Eedi (2024), Mining Misconceptions in Mathematics, sebagai pembanding gagasan deteksi kesalahan reasoning.

---

## 20. Lampiran

### Lampiran A — Skema JSON Ekstraksi

```json
{
  "produk": {
    "jenis": "pinjol | paylater | cicilan | lainnya",
    "nama_penyelenggara": "string | null",
    "status_legalitas_klaim": "legal | ilegal | tidak diketahui"
  },
  "term_finansial": {
    "pokok": "number | null",
    "bunga_nominal": "number | null",
    "bunga_basis": "harian | bulanan | tahunan | flat | null",
    "tenor_hari": "number | null",
    "biaya_admin": "number | null",
    "biaya_admin_basis": "persen | nominal | null",
    "potongan_di_depan": "number | null",
    "denda": "number | null",
    "denda_basis": "sisa_pokok | limit_awal | harian | null",
    "syarat_tersembunyi": ["string"]
  },
  "penanda_visual": {
    "teks_di_highlight": ["string"],
    "teks_fine_print": ["string"]
  }
}
```

### Lampiran B — Contoh Data (Input ke Output)

**Input (teks penawaran).** "Pinjam Rp1.000.000, bunga cuma 0,4% per hari, cair cepat." Fine print: potongan admin 10% di depan, tenor 30 hari.

**Output laporan (ringkas).**

```json
{
  "term_finansial": {
    "pokok": 1000000,
    "bunga_nominal": 0.4,
    "bunga_basis": "harian",
    "tenor_hari": 30,
    "biaya_admin": 10,
    "biaya_admin_basis": "persen",
    "potongan_di_depan": 100000
  },
  "biaya_sebenarnya": {
    "dana_bersih_diterima": 900000,
    "total_bunga": 120000,
    "total_bayar": 1120000,
    "biaya_efektif_persen_bulan": 24.4
  },
  "penyesatan": ["P2", "P1"],
  "kepatuhan_ojk": {
    "melebihi_batas_bunga": true,
    "catatan": "Bunga harian 0,4% di atas batas konsumtif 0,1% per hari"
  },
  "severity": "tinggi",
  "penjelasan": "Kamu terima Rp900 ribu tapi harus balikin Rp1,12 juta. Biaya sebenarnya sekitar 24% dalam sebulan, bukan cuma 0,4%. Penawaran ini menyembunyikan potongan admin dan melebihi batas bunga OJK."
}
```

### Lampiran C — Detail Taksonomi dan Metode Injeksi

Untuk tiap kategori, injeksi dimulai dari skenario benar dengan CoT dan biaya sebenarnya, lalu menerapkan transformasi presentasi yang membuat penawaran tampak menyesatkan sementara kebenaran tetap dapat dihitung. Label mengikuti transformasi yang diterapkan.

**P1 Misrepresentasi suku bunga.** Ambil bunga efektif benar, sajikan sebagai angka harian kecil tanpa konteks total, atau ubah label menjadi flat sambil menyembunyikan basis efektif. Injeksi: sembunyikan biaya efektif tahunan, tonjolkan angka harian.

**P2 Biaya siluman.** Pindahkan potongan admin, provisi, atau asuransi dari headline ke fine print, sehingga dana cair lebih kecil dari nominal. Injeksi: headline menyebut nominal pinjaman, fine print memuat potongan.

**P3 Salah basis perhitungan denda.** Sajikan denda seolah dihitung dari limit awal, bukan sisa pokok, atau tampilkan denda beranak tanpa keterangan. Injeksi: ganti basis denda pada teks presentasi, pertahankan basis benar pada ground truth.

**P4 Penyamaran struktur cicilan.** Tonjolkan "cicilan ringan" tanpa menyebut tenor panjang, sehingga total membengkak. Injeksi: tampilkan angka cicilan per periode, sembunyikan total dan tenor.

**P5 Framing visual menyesatkan.** Saat rendering gambar, highlight angka menarik dan kecilkan biaya asli di fine print. Injeksi bersifat visual pada tahap rendering (8.4).

**P6 Klaim palsu atau bait.** Tambahkan klaim "bunga 0%" atau "tanpa biaya" yang tidak sepenuhnya benar karena ada biaya lain. Injeksi: sisipkan klaim yang bertentangan dengan term sebenarnya.

**R1 Indikator ilegalitas.** Set parameter bunga di atas batas OJK, atau tambahkan sinyal permintaan akses berlebihan dan penawaran via kanal pribadi tanpa pengajuan. Injeksi: sampling parameter di luar batas legal dan tambahkan atribut red flag.

---

*Dokumen ini adalah brief penelitian dan dapat direvisi seiring perkembangan eksperimen dan pembaruan regulasi OJK.*
