# Grounded and Verifiable Chain-of-Thought for Time-Series Reasoning

> **Status dokumen:** ini **spec kanonik / sumber Lampiran** (skema JSONL Lampiran A, pustaka operasi
> Lampiran C, contoh Lampiran B/D) yang dijadikan acuan oleh kode di `src/gearts/` dan tes.
> **Rencana riset terkini ada di [`project_brief_v2.md`](project_brief_v2.md)** (gap yang dipertajam,
> RQ1–RQ4, desain eksperimen, rencana 5 hari). Untuk *framing dan rencana kerja*, baca v2; dokumen ini
> untuk *definisi kanonik*, bukan rencana kerja lama (Tahap 1–6 di §9–§14, timeline §18). Peta tugas: [`.scratch/BOARD.md`](.scratch/BOARD.md).

| | |
|---|---|
| **Nama proyek** | GEAR-TS (Grounded, Efficient, Adaptive Reasoning for Time Series). Nama kerja, bisa diganti. |
| **Versi dokumen** | 1.0 |
| **Domain** | Time-Series Reasoning, Efficient Reasoning, Faithfulness/Trustworthy AI, Multimodal LLM, Neuro-Symbolic Reasoning |
| **Konteks** | Lomba data mining, dengan potensi jadi dataset/method paper |
| **Status** | Project brief / proposal penelitian |

---

## Daftar Isi

1. Ringkasan Eksekutif
2. Latar Belakang
3. Kenapa Ini Masalah SOTA di 2026
4. Rumusan Masalah
5. Tujuan dan Kontribusi
6. Ruang Lingkup dan Batasan
7. Posisi terhadap Karya Terkait
8. Gambaran Metodologi
9. Tahap 1 — Konstruksi Dataset
10. Tahap 2 — Pengolahan Dataset
11. Tahap 3 — Metode dan Arsitektur
12. Tahap 4 — Protokol Training
13. Tahap 5 — Desain Eksperimen
14. Tahap 6 — Evaluasi dan Metrik
15. Hasil yang Diharapkan
16. Analisis Risiko dan Mitigasi
17. Pertimbangan Etika dan Legal
18. Rencana Kerja dan Timeline
19. Kebutuhan Sumber Daya dan Stack
20. Referensi
21. Lampiran

---

## 1. Ringkasan Eksekutif

Proyek ini mengangkat masalah reasoning atas data time series, yaitu kemampuan model bahasa besar (LLM) untuk menalar langkah demi langkah atas deret angka dan menghasilkan kesimpulan yang bisa dipertanggungjawabkan. Masalahnya nyata: LLM jago mengolah bahasa tapi lemah menalar atas angka mentah, sehingga sering menghasilkan pola yang salah, misalnya mengklaim tren, lokasi lonjakan, atau besaran kenaikan yang tidak sesuai data. Kesalahan ini berbahaya karena kalimatnya rapi dan meyakinkan.

Kami mengusulkan dua kontribusi. Pertama, dataset reasoning time series terverifikasi yang kami bangun sendiri dari sumber publik nyata, tersimpan dalam format JSONL, dengan lapisan reasoning yang tiap langkahnya sudah dicek ke angka. Kedua, metode yang memasangkan LLM hasil fine-tune dengan verifikator deterministik di luar model, sehingga reasoning yang dihasilkan grounded (berpijak ke perhitungan nyata) sekaligus hemat token lewat reasoning adaptif.

Posisi kami jelas relatif terhadap karya terbaru. Verifiable reasoning untuk time series sudah mulai digarap, tetapi arah itu menghasilkan reasoning yang panjang dan mahal. Reasoning hemat token juga sudah berkembang, tetapi masih terbatas di domain soal matematika. Belum ada yang menggabungkan keduanya di time series, dan belum ada yang membangun dataset reasoning time series terverifikasi dari sumber lokal. Di titik itulah proyek ini berdiri.

---

## 2. Latar Belakang

### 2.1 Konteks

Data time series ada di hampir semua keputusan penting: kasus penyakit per minggu, harga pangan per hari, beban listrik per jam, sinyal sensor industri. Selama ini yang paling banyak digarap adalah forecasting, yaitu meramal angka berikutnya. Tetapi angka ramalan saja jarang cukup untuk mengambil keputusan. Yang dibutuhkan pengambil keputusan adalah tafsirannya, misalnya apakah sebuah lonjakan menandakan wabah yang mulai terbentuk dan perlu respons. Kemampuan menafsirkan inilah yang disebut reasoning, dan bagian ini justru tertinggal dibanding forecasting.

### 2.2 Masalah Inti

LLM sekarang menjadi antarmuka universal, tetapi lemah pada angka. Ketika disuruh menalar atas deret angka yang banyak, model cenderung mengandalkan pola bahasa, bukan komputasi aktual, sehingga berhalusinasi. Contoh nyata, untuk deret kasus mingguan `12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78` dengan pertanyaan apakah ada indikasi outbreak, jawaban benar adalah ya, karena baseline sekitar 13 kasus dan empat minggu terakhir naik dari 38 ke 78 (sekitar 105 persen), dengan nilai akhir sekitar 6 kali baseline. Model sering keliru dengan tiga pola berbahaya:

1. Menutupi bahaya, misalnya menyimpulkan kasus relatif stabil padahal jelas naik ke 78.
2. Salah lokasi, misalnya menyebut lonjakan di minggu ke-6 padahal lonjakan sebenarnya di minggu 12 ke atas.
3. Salah besaran, misalnya menyebut naik sekitar 30 persen padahal aslinya ratusan persen.

### 2.3 Kenapa Reasoning Time Series Penting

Ada dua alasan yang paling kuat. Pertama, akses untuk non-ahli. Membaca deret angka dan menarik kesimpulan yang benar sekarang butuh ahli, sementara pihak yang paling perlu bertindak atas data justru sering bukan ahli, misalnya petugas kesehatan puskesmas, petani, atau aparat daerah. Model yang bisa menalar deret waktu dalam bahasa biasa menaruh kemampuan setara ahli ke tangan orang awam. Kedua, kepercayaan di ranah taruhan tinggi. Di kesehatan atau finansial, jawaban tanpa alasan yang bisa dicek tidak layak dipercaya. Reasoning yang grounded dan verifiable memungkinkan manusia memeriksa logikanya sebelum bertindak.

Secara umum, reasoning time series menjembatani dua hal yang selama ini terpisah, yaitu analisis statistik yang bisa menghitung tapi tidak bisa menjelaskan, dan LLM yang bisa menjelaskan tapi tidak bisa menghitung.

---

## 3. Kenapa Ini Masalah SOTA di 2026

1. Buktinya ada di venue top dan gerakannya baru. Reasoning time series menjadi rebutan di konferensi kelas atas, dengan beberapa submission di siklus ICLR 2026, benchmark yang baru direvisi 2026, dan survei khusus yang baru terbit di TMLR 2026.
2. Ini muncul karena lompatan reasoning model pada 2025. Setelah reasoning panjang berbasis RL menjadi standar dan sukses di matematika dan coding, orang mulai membawanya ke domain non-teks, dan time series adalah domain besar yang ketahuan belum terpecahkan.
3. Ada temuan yang membuat bidang ini panas, yaitu reasoning yang manjur di matematika tidak otomatis jalan di time series, bahkan ada bukti bahwa reasoning eksplisit tidak menaikkan analisis deret waktu.
4. Arah yang sedang dikejar sekarang punya masalah bawaan. Menambahkan reasoning panjang yang verifiable ke time series membuatnya boros token dan tetap rawan halusinasi, sementara riset hemat token masih menempel di matematika. Persis di pertemuan dua tren ini ada celah yang belum diambil.

Catatan positioning yang jujur: jangan mengklaim reasoning time series belum diteliti, karena itu salah dan mudah dipatahkan. Klaim yang benar adalah reasoning time series sedang menjadi frontier panas 2026, tetapi gabungan grounded plus hemat token belum ada yang menggarap, dan dataset reasoning time series terverifikasi dari sumber lokal belum ada.

---

## 4. Rumusan Masalah

1. Bagaimana membuat reasoning LLM atas time series grounded, yaitu tiap langkah berpijak ke perhitungan nyata atas deret, bukan tebakan bahasa?
2. Bagaimana memverifikasi kebenaran tiap langkah reasoning secara pasti dan murah?
3. Bagaimana menjaga reasoning tetap hemat token melalui alokasi panjang yang adaptif terhadap kesulitan?
4. Bagaimana membangun dataset reasoning time series terverifikasi dalam skala memadai tanpa dataset berlabel publik?

---

## 5. Tujuan dan Kontribusi

**Tujuan umum.** Menghasilkan sistem yang menalar atas time series secara jujur ke angka sekaligus hemat.

**Kontribusi.**

1. **Dataset.** Korpus reasoning time series terverifikasi berbasis sumber publik nyata, dalam format JSONL, dengan reasoning yang tiap langkahnya sudah dicek. Ini kontribusi utama untuk lomba data mining karena data effort dinilai paling tinggi.
2. **Metode.** Pemasangan LLM hasil fine-tune dengan verifikator deterministik di luar model, ditambah mekanisme reasoning adaptif untuk efisiensi.
3. **Metrik.** Skor grounding sebagai ukuran kejujuran reasoning terhadap angka, yang dihitung deterministik tanpa LLM lain.

**Kejelasan penting.** Kebaruan proyek bukan pada LLM-nya, karena LLM meminjam yang sudah ada lalu di-fine-tune. Kebaruan ada pada dataset yang dibangun sendiri dan pada pasangan model plus verifikator yang membuat reasoning bisa dicek dan hemat.

---

## 6. Ruang Lingkup dan Batasan

**Termasuk lingkup.** Reasoning atas deret waktu univariat dan sederhana multivariat; input berupa deret angka plus konteks teks; tugas reasoning seperti deteksi indikasi anomali, karakterisasi tren, perbandingan segmen, dan penjelasan.

**Di luar lingkup.** Forecasting akurasi tinggi sebagai tujuan utama; nasihat medis atau finansial personal (sistem bersifat decision support); modalitas gambar.

**Asumsi.** Deret bisa diakses lengkap dalam konteks model; operasi reasoning bisa dibatasi ke pustaka operasi yang terdefinisi.

---

## 7. Posisi terhadap Karya Terkait

Positioning ini menentukan pertahanan proyek di depan juri, jadi disusun eksplisit.

**Pembanding utama.** VeriTime (Time Series Reasoning via Process-Verifiable Thinking) menggarap reasoning time series yang bisa diverifikasi. Proyek ini didefinisikan langsung relatif ke VeriTime, dengan pembeda bahwa kami menggabungkan verifiable dengan hemat token, dan datanya kami bangun sendiri dari konteks lokal.

**Sumber teknik efisiensi.** SelfBudgeter menunjukkan reasoning bisa dibuat hemat dan adaptif terhadap kesulitan, tetapi masih di domain soal matematika. Kami meminjam gagasan ini dan membawanya ke time series, yang belum pernah dilakukan.

**Framing masalah.** MTBench menunjukkan model masih gagal pada reasoning gabungan angka plus teks, dipakai untuk menaikkan masalah di pendahuluan.

**Konteks lebih luas.** Terdapat temuan bahwa LLM masih kesulitan zero-shot menalar tentang time series, dan submission lain seperti TimeOmni-1 yang mendorong reasoning kompleks. Ini menegaskan bidangnya aktif sekaligus belum terpecahkan.

Peringatan jujur: VeriTime adalah pesaing terdekat, jadi klaim bahwa arah verifiable menghasilkan reasoning yang panjang dan mahal harus dipastikan sesuai isi paper aslinya sebelum dijadikan poros pembeda.

---

## 8. Gambaran Metodologi

Ada tiga hal yang jangan tertukar.

1. **Dataset.** Bahan bakar, dipakai untuk melatih dan menguji.
2. **Metode.** Cara membuat LLM menghasilkan reasoning grounded dan hemat, terdiri dari dua komponen berbeda sifat: komponen model (LLM yang di-fine-tune) dan komponen program (verifikator deterministik yang tidak dilatih).
3. **Metrik.** Alat ukur, terutama skor grounding.

Alur inti sistem: LLM menerima deret angka plus pertanyaan, lalu mengeluarkan reasoning dalam bentuk langkah-langkah beroperasi (bukan prosa bebas), lalu verifikator deterministik di luar model menjalankan ulang tiap operasi atas deret asli dan mengecek apakah angka yang diklaim cocok. LLM yang menalar, program yang mengoreksi. Keduanya benda terpisah yang bekerja bersama, bukan program yang diinjeksikan ke dalam LLM.

```
Deret angka + pertanyaan
   -> LLM (fine-tuned) menghasilkan langkah reasoning beroperasi
   -> Verifikator deterministik menghitung ulang tiap langkah atas deret asli
   -> Cek kecocokan angka (dalam toleransi) => skor grounding + reasoning tervalidasi
   -> Jawaban akhir
```

---

## 9. Tahap 1 — Konstruksi Dataset

Ini kontribusi utama dan komponen yang paling menentukan nilai lomba.

### 9.1 Sumber Deret Angka

Deret angka diambil dari sumber publik nyata lewat scraping atau API, sehingga bukan dataset Kaggle. Contoh sumber:

- Harga pangan harian dari PIHPS Bank Indonesia.
- Kasus penyakit dari dashboard Kementerian Kesehatan.
- Data cuaca dari BMKG.
- Konsumsi atau beban energi dari sumber terbuka.

### 9.2 Lapisan Reasoning (bagian yang nguli dan jadi moat)

Untuk tiap deret, kami menyusun pertanyaan, menghitung jawaban benar secara pasti dengan rumus, lalu menyusun langkah reasoning yang tiap angkanya dicek ke deret. Langkah reasoning dibatasi ke pustaka operasi terdefinisi (lihat Lampiran C), sehingga tiap langkah dapat dieksekusi ulang dan diverifikasi.

Untuk skala, sebagian besar data latih dapat dibuat semi-sintetis, yaitu deret nyata atau deret yang dibangkitkan terkontrol, dipasangkan dengan pertanyaan dan reasoning yang dihasilkan lalu diverifikasi otomatis oleh verifikator. Data uji memakai deret asli dari sumber di 9.1 agar terbukti model bekerja di data lapangan.

### 9.3 Bentuk Akhir Data

Format JSONL, satu baris satu sampel. Skema di Lampiran A, contoh di Lampiran B. Isi tiap sampel: deret angka plus konteks, satu pertanyaan, langkah reasoning yang tiap angkanya sudah dicek, dan jawaban akhir.

### 9.4 Pembagian Dataset

Data latih didominasi semi-sintetis untuk skala. Data uji didominasi deret asli untuk mengukur generalisasi. Pembagian distratifikasi berdasarkan jenis tugas reasoning dan tingkat kesulitan. Sumber pada uji dipastikan tidak muncul pada latih untuk mencegah kebocoran.

---

## 10. Tahap 2 — Pengolahan Dataset

1. Normalisasi deret: standarisasi satuan, frekuensi, penanganan nilai hilang, dan format angka.
2. Penyusunan pertanyaan: template pertanyaan lintas jenis tugas (tren, anomali, perbandingan, karakterisasi).
3. Sintesis reasoning: menghasilkan langkah beroperasi dari pustaka operasi, lalu menghitung hasilnya.
4. Verifikasi label: verifikator deterministik menjalankan ulang tiap langkah, sampel dengan langkah tidak lolos diperbaiki atau dibuang, sehingga label bersih.
5. Formatting: menyimpan ke JSONL sesuai skema, siap untuk fine-tuning.
6. Splitting final: seed tetap untuk reprodusibilitas.

---

## 11. Tahap 3 — Metode dan Arsitektur

### 11.1 Komponen Model

LLM hasil fine-tune yang belajar mengeluarkan reasoning dalam bentuk urutan langkah beroperasi, bukan prosa bebas. Deret angka diberikan sebagai bagian input bersama pertanyaan. Kandidat model Qwen2.5 kelas 7B. Representasi deret dapat berupa tekstualisasi angka terstruktur, atau opsional encoder deret terpisah bergaya Time-LLM untuk deret panjang.

### 11.2 Komponen Program (verifikator deterministik)

Program di luar LLM yang menjalankan ulang tiap operasi di langkah reasoning atas deret asli, lalu membandingkan hasil hitung ulang dengan angka yang diklaim model. Satu langkah dianggap grounded jika selisihnya lebih kecil dari toleransi kecil, misalnya 0,01. Program ini tidak dilatih, hanya kode. Ia dipakai di tiga tempat: saat konstruksi dataset untuk membersihkan label, saat evaluasi untuk menghitung skor grounding, dan opsional saat training sebagai sinyal reward.

### 11.3 Reasoning Adaptif (efisiensi)

Panjang reasoning diatur menurut kesulitan. Deret dengan pola jelas mendapat reasoning pendek, deret ambigu mendapat reasoning panjang. Ini menekan token tanpa mengorbankan akurasi, mengikuti gagasan alokasi anggaran token adaptif yang dibawa ke ranah time series.

---

## 12. Tahap 4 — Protokol Training

Fine-tuning memakai LoRA atau QLoRA 4-bit agar muat di GPU T4 atau V100. Karena kekuatan proyek ada di data dan grounding, model 7B memadai dan tidak perlu skala besar.

**Konfigurasi kandidat (akan di-tuning).**

| Parameter | Nilai kandidat |
|---|---|
| Metode | QLoRA (NF4 4-bit) |
| LoRA rank | 16 sampai 64 |
| LoRA alpha | 32 |
| Learning rate | 1e-4 sampai 2e-4 |
| Scheduler | cosine dengan warmup |
| Precision | bf16 |
| Epoch | 2 sampai 3 |
| Framework | LLaMA-Factory + DeepSpeed ZeRO-2 |

**Tahap lanjutan opsional.** RL dengan verifiable reward, yaitu model diberi nilai lebih ketika langkah reasoning lolos verifikasi grounding. Ini menambah kerja, jadi ditempatkan sebagai perluasan, bukan wajib di awal.

---

## 13. Tahap 5 — Desain Eksperimen

### 13.1 Pertanyaan Penelitian

- **RQ1.** Seberapa sering model yang ada sekarang berhalusinasi saat menalar time series, terlihat dari skor grounding rendah meski jawaban kadang benar?
- **RQ2.** Apakah metode kami menaikkan skor grounding tanpa menurunkan akurasi jawaban?
- **RQ3.** Apakah reasoning adaptif kami lebih hemat token dibanding reasoning panjang, pada akurasi setara?
- **RQ4.** Komponen mana yang paling berkontribusi?

### 13.2 Eksperimen

1. **Probe halusinasi baseline.** Uji model yang ada di benchmark kami untuk membuktikan masalahnya nyata, dengan menunjukkan skor grounding rendah.
2. **Metode vs baseline.** Bandingkan metode kami dengan model tersebut untuk menunjukkan grounding naik tanpa mengorbankan akurasi.
3. **Efisiensi.** Bandingkan token reasoning adaptif kami dengan reasoning panjang pada akurasi setara.
4. **Ablation.** Matikan komponen satu per satu (verifikator saat training, reasoning adaptif, format beroperasi) untuk mengukur kontribusi masing-masing.

### 13.3 Baseline

- LLM umum tanpa fine-tune, prosa bebas.
- LLM dengan CoT panjang bergaya verifiable tanpa efisiensi (proksi arah VeriTime).
- Metode statistik murni sebagai batas atas komputasi tanpa penjelasan bahasa.

---

## 14. Tahap 6 — Evaluasi dan Metrik

Tiga metrik, dengan cara hitung eksplisit.

1. **Akurasi jawaban.** Jumlah sampel dengan label jawaban akhir benar dibagi total sampel, dikali 100 persen. Mengecek kebenaran kesimpulan.

2. **Skor grounding (metrik utama).** Jumlah langkah reasoning yang angkanya cocok saat dihitung ulang dibagi total langkah, dikali 100 persen. Satu langkah cocok jika selisih hasil model dan hasil hitung ulang lebih kecil dari toleransi, misalnya 0,01. Mengukur kejujuran reasoning terhadap angka.

3. **Efisiensi token.** Rata-rata jumlah token reasoning per sampel, dilaporkan bersama akurasi agar tradeoff terlihat. Makin kecil makin hemat, dengan syarat akurasi tidak turun.

**Cara verifikasi hasil prediksi.** Verifikator deterministik, yaitu program, bukan LLM lain, menjalankan ulang tiap operasi di langkah reasoning atas deret asli dan membandingkan hasilnya dengan angka yang diklaim model. Karena yang mengecek kalkulator, hasilnya pasti dan murah.

**Fitur yang diprediksi.** Model memprediksi dua variabel: rangkaian langkah reasoning (tiap langkah berisi operasi dan angka hasil hitungnya) dan jawaban akhir (label plus tingkat keyakinan). Ini kompleks karena keluarannya bukan satu angka atau satu label, melainkan struktur bertahap yang panjang, dan model dapat salah di banyak titik, yaitu di angka langkah manapun atau di kesimpulan akhir.

---

## 15. Hasil yang Diharapkan

1. Dataset reasoning time series terverifikasi yang siap dipakai ulang.
2. Bukti empiris bahwa model yang ada sekarang berhalusinasi (grounding rendah) pada reasoning time series.
3. Bukti bahwa metode kami menaikkan grounding tanpa menurunkan akurasi, dan lebih hemat token dari reasoning panjang.
4. Prototipe end-to-end yang dapat menjawab pertanyaan atas deret dengan reasoning yang bisa dicek.

---

## 16. Analisis Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Overlap dengan VeriTime | Pembeda dipertanyakan | Baca VeriTime teliti, tekankan gabungan verifiable plus hemat dan data lokal buatan sendiri |
| Kualitas label reasoning | Data tidak valid | Verifikator deterministik membersihkan label; buang langkah tidak lolos |
| Realisme data semi-sintetis | Bagus di sintetis, jeblok di asli | Uji didominasi deret asli dari sumber publik |
| LLM lemah encode deret panjang | Ekstraksi angka salih | Batasi panjang, opsi encoder deret terpisah, tekankan operasi beroperasi |
| Pustaka operasi terlalu sempit | Tidak menutup pertanyaan kompleks | Rancang pustaka bertingkat, mulai dari operasi dasar lalu komposit |

---

## 17. Pertimbangan Etika dan Legal

1. Sumber data publik, pengumpulan menghormati ketentuan layanan sumber, dan tidak mengumpulkan data pribadi.
2. Sistem bersifat decision support, bukan nasihat medis atau finansial personal, dengan disclaimer jelas terutama di domain kesehatan dan keuangan.
3. Reasoning yang grounded justru mendukung akuntabilitas karena jejak perhitungannya dapat diaudit.
4. Untuk penggunaan taruhan tinggi, hasil model ditinjau manusia, bukan dijadikan keputusan otomatis.

---

## 18. Rencana Kerja dan Timeline

| Fase | Aktivitas | Estimasi |
|---|---|---|
| 1 | Finalisasi pustaka operasi dan skema JSONL, bangun verifikator | Minggu 1 sampai 2 |
| 2 | Scraping deret dari sumber publik | Minggu 2 sampai 4 |
| 3 | Sintesis dan verifikasi lapisan reasoning | Minggu 3 sampai 6 |
| 4 | Fine-tune model dan integrasi pipeline | Minggu 6 sampai 8 |
| 5 | Eksperimen, ablation, evaluasi | Minggu 8 sampai 10 |
| 6 | Prototipe dan penulisan laporan | Minggu 10 sampai 12 |

Titik paling menentukan ada di Fase 1 dan 3, karena pustaka operasi dan verifikasi label mendefinisikan seluruh data.

---

## 19. Kebutuhan Sumber Daya dan Stack

**Komputasi.** GPU T4 atau V100 (Colab atau Kaggle) dengan QLoRA.

| Komponen | Tools |
|---|---|
| Model | Qwen2.5 kelas 7B, di-fine-tune |
| Training | LLaMA-Factory, DeepSpeed ZeRO-2, PEFT |
| Verifikator | Modul Python deterministik, NumPy |
| Encoder deret (opsional) | Pendekatan bergaya Time-LLM untuk deret panjang |
| Scraping | Playwright atau Selenium, plus API resmi sumber |
| Logging eksperimen | Weights & Biases |

---

## 20. Referensi

Paper rujukan inti:

- **VeriTime** (judul asli: Time Series Reasoning via Process-Verifiable Thinking Data Synthesis and Scheduling for Tailored LLM Reasoning). Status: under review ICLR 2026. arXiv: 2602.07830. **Pembanding utama.**
- **MTBench**: A Multimodal Time Series Benchmark for Temporal Reasoning and Question Answering. Status: arXiv preprint (v1 Maret 2025, v2 Februari 2026). arXiv: 2503.16858. Dipakai untuk framing masalah.
- **SelfBudgeter**: Adaptive Token Allocation for Efficient LLM Reasoning. Status: arXiv preprint, di OpenReview. arXiv: 2505.11274. Sumber teknik efisiensi.

Rujukan pendukung dan metode:

- Merrill et al. (2024). Language models still struggle to zero-shot reason about time series. Findings of EMNLP 2024.
- TimeOmni-1: incentivizing complex reasoning with time series in LLMs (ICLR 2026).
- Wei et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models.
- Gao et al. (2023). PAL: Program-aided Language Models.
- Hu et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models.
- Dettmers et al. (2023). QLoRA: Efficient Finetuning of Quantized LLMs.
- DeepSeek-AI (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.

---

## 21. Lampiran

### Lampiran A — Skema JSONL

```json
{
  "id": "string",
  "series": {
    "nama": "string",
    "satuan": "string",
    "freq": "harian | mingguan | bulanan | ...",
    "nilai": [".. deret angka .."]
  },
  "konteks": "string, deskripsi singkat deret",
  "pertanyaan": "string",
  "reasoning": [
    {"langkah": "int", "operasi": "string operasi dari pustaka", "hasil": "number", "teks": "string penjelasan"}
  ],
  "jawaban": {"label": "string", "keyakinan": "rendah | sedang | tinggi"}
}
```

### Lampiran B — Contoh Data (satu baris JSONL)

```json
{
  "id": "dbd_kabX_001",
  "series": {"nama": "kasus_dbd_mingguan", "satuan": "kasus", "freq": "mingguan",
             "nilai": [12,15,11,14,13,18,22,19,25,31,29,38,45,52,61,78]},
  "konteks": "Kasus DBD mingguan Kabupaten X, 16 minggu",
  "pertanyaan": "Apakah ada indikasi outbreak?",
  "reasoning": [
    {"langkah": 1, "operasi": "rata2(nilai[0:5])", "hasil": 13.0, "teks": "baseline awal 13 kasus"},
    {"langkah": 2, "operasi": "persen_naik(nilai[11]->nilai[15])", "hasil": 105.3, "teks": "minggu 12 ke 16 naik 105%"},
    {"langkah": 3, "operasi": "rasio(nilai[15], 13.0)", "hasil": 6.0, "teks": "nilai akhir 6x baseline"}
  ],
  "jawaban": {"label": "outbreak", "keyakinan": "tinggi"}
}
```

### Lampiran C — Pustaka Operasi (dasar)

Pustaka ini mendefinisikan operasi yang boleh dipakai di langkah reasoning, sehingga tiap langkah dapat dieksekusi ulang oleh verifikator.

| Operasi | Arti | Contoh |
|---|---|---|
| rata2(rentang) | rata-rata pada rentang | rata2(nilai[0:5]) |
| delta(a -> b) | selisih dua titik | delta(nilai[0] -> nilai[15]) |
| persen_naik(a -> b) | perubahan persen | persen_naik(nilai[11] -> nilai[15]) |
| rasio(a, b) | perbandingan | rasio(nilai[15], baseline) |
| slope(rentang) | kemiringan tren linear | slope(nilai[10:16]) |
| min / max(rentang) | nilai ekstrem | max(nilai) |
| z_score(titik) | deviasi dari rata-rata dalam simpangan baku | z_score(nilai[15]) |
| deteksi_anomali(ambang) | titik melewati ambang | deteksi_anomali(z=3) |
| bandingkan_segmen(r1, r2) | banding dua segmen waktu | bandingkan_segmen(nilai[0:8], nilai[8:16]) |

Operasi komposit dapat disusun dari operasi dasar. Verifikator menjalankan tiap operasi ini secara deterministik atas deret asli untuk mengecek grounding.

### Lampiran D — Contoh Jawaban Halusinasi (untuk motivasi)

Untuk deret pada Lampiran B, contoh jawaban salah yang meyakinkan:

- Menutupi bahaya: menyimpulkan kasus stabil di kisaran belasan sampai dua puluhan, padahal naik ke 78.
- Salah lokasi: menyebut lonjakan utama di minggu ke-6, padahal minggu 6 hanya 18.
- Salah besaran: menyebut naik sekitar 30 persen, padahal aslinya sekitar 105 persen pada empat minggu terakhir.

Ketiganya berbahaya justru karena kalimatnya rapi dan percaya diri. Grounding yang diverifikasi dirancang untuk menangkap kesalahan seperti ini.

---

*Dokumen ini adalah brief penelitian dan dapat direvisi seiring perkembangan eksperimen serta pendalaman paper pembanding.*
