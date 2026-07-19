# Komentar Juri yang Sering Muncul — dan Perbaikannya

Daftar ini disusun dari catatan revisi nyata seorang dosen juri GEMASTIK atas
sebuah draft. Cek draft terhadap tiap poin ini sebelum menganggap revisi
selesai — kalau reviewer feedback baru diberikan pengguna, petakan tiap
komentar mereka ke baris yang relevan di sini dan perbaiki secara spesifik.

## 1. "Indikasi kuat hasil terjemah AI"

**Gejala**: istilah teknis diterjemahkan ke Bahasa Indonesia secara harfiah,
membuat kalimat terasa asing/dipaksakan.

**Perbaikan**:
- Pertahankan istilah aslinya (Inggris) untuk konsep teknis mapan, italic
  saat pertama muncul: *fine-tuning* bukan "penalaan halus", *chunking*
  bukan "pemotongan bagian", *embedding* bukan "penyisipan", LoRA tetap
  "*Low-Rank Adaptation* (LoRA)" bukan diterjemahkan.
- Baca ulang tiap paragraf dan tanya: apakah kalimat ini terdengar seperti
  cara orang Indonesia menulis makalah ilmiah, atau seperti hasil terjemah
  mesin dari draft Inggris? Kalimat yang kaku secara struktur (subjek-objek
  dibalik secara tidak natural, klausa bertumpuk berlebihan) adalah sinyal.
- Variasikan struktur kalimat — hindari pola berulang seperti selalu
  memulai kalimat dengan struktur yang identik antar paragraf.

## 2. "Bahasanya dibuat lebih ilmiah, bukan bahasa sehari-hari"

**Gejala**: nada terlalu kasual, kalimat pendek-pendek terputus.

**Perbaikan**:
- Gunakan konektor argumentatif eksplisit: "Namun,", "Oleh karena itu,",
  "Dengan demikian,", "Sejalan dengan hal tersebut,".
- Gabungkan ide yang berkaitan dalam satu kalimat kompleks alih-alih
  banyak kalimat pendek terpisah.
- Hindari kata ganti orang pertama informal berlebihan; gunakan "penelitian
  ini" atau "kami" secukupnya dan konsisten.

## 3. "Tidak perlu membagi ke 3 bagian, pendahuluan dapat dijelaskan secara
argumentatif dan deskriptif secara langsung; penulis perlu menghubungkan
konteks antar kalimat"

**Gejala**: Pendahuluan dipecah jadi banyak `\subsection` pendek
(Kesenjangan Penelitian, Kontribusi, Rumusan Masalah masing-masing sebagai
subsection terpisah) padahal isinya bisa mengalir sebagai satu narasi.

**Perbaikan**:
- Untuk makalah 4-5 halaman, coba tulis Pendahuluan sebagai paragraf-
  paragraf yang mengalir tanpa subsection heading, dengan urutan logis:
  latar belakang → masalah spesifik → kelemahan pendekatan sebelumnya →
  celah penelitian → kontribusi kami → rumusan masalah/RQ (bisa
  disebutkan dalam kalimat, tidak harus heading terpisah) → manfaat.
- Tiap kalimat pembuka paragraf baru harus merujuk balik ke kalimat
  penutup paragraf sebelumnya (mis. "Kekeliruan seperti ini..." merujuk ke
  masalah yang baru dijelaskan) — ini yang dimaksud "menghubungkan konteks
  antar kalimat".
- Subsection di Pendahuluan hanya dipakai kalau makalah cukup panjang/
  kompleks untuk membutuhkannya (lihat pola di finalist_examples.md).

## 4. "LoRA? Low Rank Adaptation? Lebih baik menggunakan istilah aslinya"

**Gejala**: singkatan disebut tanpa definisi lengkap, atau nama metode
diterjemahkan/diparafrase alih-alih dipakai sebagai istilah baku.

**Perbaikan**:
- Definisikan lengkap sekali saat pertama disebut: "*Low-Rank Adaptation*
  (LoRA)", lalu pakai "LoRA" seterusnya.
- Jangan parafrase nama metode/algoritma yang sudah punya nama baku di
  literatur — sebut nama aslinya persis seperti di paper sumber.

## 5. "Metode scraping tidak dijelaskan — berapa lama, berapa banyak data;
contoh sampel data tidak dijelaskan; kejelasan tulisan sangat minim"

**Gejala**: bagian metodologi/dataset menyebut proses pengumpulan data
secara abstrak tanpa angka konkret.

**Perbaikan**:
- Selalu sertakan: rentang waktu pengumpulan data (tanggal/durasi), jumlah
  baris/sampel yang terkumpul, sumber persis (nama situs/API), dan minimal
  satu contoh konkret satu baris/sampel data (bisa sebagai contoh singkat
  di teks atau baris contoh di tabel).
- Ikuti pola tabel "Jenis Data, Variabel, Sumber Data, Metode Akuisisi,
  Timeframe, Frekuensi" seperti di kedua makalah finalis referensi.
- Kalau user belum tahu angka pastinya, tandai eksplisit dengan
  `[ISI: jumlah baris data]` sebagai placeholder yang jelas terlihat,
  jangan tulis kalimat vague yang menyamarkan info yang hilang.

## 6. "Apakah berarti belum ada eksperimen aslinya? Analisis sangat awal,
tidak ada evidence/bukti kuat dari RQ1-4"

**Gejala**: bagian Hasil menyiratkan eksperimen selesai padahal belum, atau
hasil yang ada tidak ditautkan balik ke rumusan masalah (RQ) yang diajukan
di Pendahuluan.

**Perbaikan**:
- **Kejujuran status eksperimen wajib eksplisit.** Kalau masih fase awal,
  buat pernyataan status yang jelas di awal bagian Hasil (contoh dari
  draft pengguna sendiri: "Catatan penting. Penelitian masih pada Fase 1
  atau fondasi... Tidak ada angka hasil model terlatih yang diklaim pada
  draf ini."). Ini justru dihargai juri sebagai kejujuran ilmiah — yang
  jadi masalah adalah *ambiguitas*, bukan hasil yang belum lengkap.
- Setiap RQ yang dirumuskan di Pendahuluan harus punya jawaban eksplisit
  di Hasil/Kesimpulan — kalau RQ3 dan RQ4 belum bisa dijawab karena
  eksperimen belum jalan, katakan itu ("RQ3 dan RQ4 akan dijawab pada
  rancangan eksperimen Fase 5, dipaparkan pada bagian V.D") daripada
  membiarkan RQ itu menggantung tanpa disebut lagi.
- Bukti/evidence yang ada, sekecil apapun (studi kasus tunggal, hasil
  pengujian unit, prototipe fondasi), harus ditampilkan sebagai tabel/
  angka konkret, bukan diklaim secara umum ("verifikator bekerja dengan
  baik") tanpa data pendukung.

## 7. "Ide cukup relevan namun perlu dikaji dan dibandingkan dengan lebih
banyak sumber"

**Gejala**: tinjauan pustaka terlalu tipis, kurang dari ~8-10 sitasi, atau
posisi penelitian relatif ke karya lain tidak dijelaskan.

**Perbaikan**:
- Targetkan minimal 10-15 sitasi berkualitas untuk makalah kompetitif,
  diutamakan 2023-2026.
- Untuk tiap karya terkait yang disitasi, sebutkan metrik/hasil konkretnya
  dan keterbatasannya sebelum menyimpulkan celah penelitian — pola
  "[Metode] mencapai [angka], namun [keterbatasan] [sitasi]" seperti di
  kedua makalah finalis.
- Pertimbangkan tabel perbandingan posisi (seperti Tabel "Posisi Penelitian
  Ini terhadap Karya Terkait" di draft pengguna) untuk merangkum
  perbandingan multi-dimensi secara visual, bukan cuma prosa.
