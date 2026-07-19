# Revisi Intisari & Pendahuluan

Dokumen ini menutup masukan juri untuk dua bagian awal makalah: **Intisari** dan **I.
Pendahuluan**. Struktur dokumen: (1) diagnosis rinci apa yang salah dan mengapa, dipetakan ke
komentar juri; (2) prinsip penulisan yang dipakai; (3) teks revisi siap tempel.

Judul resmi dipakai apa adanya (bukan "GEAR-TS"). Konvensi *writer*: kalimat pasif ("diusulkan",
bukan "kami mengusulkan"), istilah asing dalam *italic*, nama metode/model tegak, sitasi numerik
`[n]` di akhir klausa. Hasil eksperimen model (RQ1–RQ4) **belum selesai**; setiap tempat yang perlu
angka hasil diberi tanda `[[PLACEHOLDER — ...]]` agar tidak ada klaim palsu.

---

## Bagian 1 — Diagnosis: apa yang perlu diperbaiki

### 1.1 Peta komentar juri → tindakan

| Komentar juri | Bagian | Tindakan pada revisi |
|---|---|---|
| "Indikasi kuat hasil terjemah AI; pakai istilah aslinya" | Intisari + seluruh naskah | Ganti kalimat kalke (terjemah harfiah) dengan diksi ilmiah Indonesia; pertahankan istilah teknis asli (*grounding*, *token*, *reasoning*, *fine-tune*, LoRA, CoT) |
| "Bahasa lebih ilmiah, bukan sehari-hari" | Pendahuluan | Buang frasa kolokial ("bertaruh tinggi", "penalaran jujur", "diam-diam", "menebak") → istilah baku |
| "Tidak perlu bagi ke 3 bagian; jelaskan argumentatif & deskriptif langsung" | Pendahuluan | Hapus subbab A. Kesenjangan / B. Kontribusi / C. Rumusan Masalah; jadikan prosa mengalir |
| "Penulis perlu menghubungkan konteks antar kalimat" | Pendahuluan | Tambah konektor logis; tiap paragraf punya satu klaim dengan transisi eksplisit |
| "LoRA? Low Rank Adaptation? pakai istilah asli" | Tinjauan Pustaka (rembes ke Intisari) | Jangan terjemahkan "Adaptasi peringkat rendah"; tulis LoRA/QLoRA |
| "Analisis awal, tak ada evidence RQ1–4" | Intisari (klaim hasil) | Jangan klaim hasil model; batasi pada validasi verifikator (yang memang sudah ada) + placeholder |

### 1.2 Intisari lama — cacat spesifik per frasa

Teks lama (parafrase dari PDF) dan masalahnya:

1. **"lemah *menalar atas angka*"** — kalke dari "reasoning over numbers"; tidak baku. → "lemah
   ketika penalaran menuntut komputasi numerik".
2. **"salah menyebut ... *lokasi lonjakan*, atau besaran kenaikan"** — daftar contoh mode gagal
   dijejalkan di kalimat pembuka, memutus alur. → Pindahkan detail contoh ke Pendahuluan; Intisari
   cukup menyebut "kesimpulan dapat keliru meski kalimatnya meyakinkan".
3. **"bidang *bertaruh tinggi*"** — terjemah harfiah "high-stakes"; terdengar seperti judi. →
   "domain berisiko tinggi".
4. **"*lapisan penalaran*"**, **"*prosa bebas*"**, **"*penalaran jujur*"** — diksi terjemahan. →
   "langkah penalaran", "prosa bebas" (dipertahankan, sudah baku), "penalaran yang benar/valid".
5. **"*Adaptasi peringkat rendah* dan kuantisasi NF4"** — persis yang juri soroti. → "LoRA dan
   kuantisasi NF4 4-bit" (bila detail ini memang perlu di Intisari; sebaiknya diringkas).
6. **Kalimat penutup: "Pembeda penelitian ini adalah *penggabungan* penalaran terverifikasi dan
   hemat token."** — **cacat paling serius**: bertentangan dengan kebaruan yang sudah dipertajam.
   Kebaruan bukan penggabungan dua ide (terkesan inkremental, mudah dipatahkan), melainkan (a)
   temuan bahwa efisiensi naif mengorbankan *grounding*, dan (b) mekanisme efisiensi yang *sadar
   grounding*. → Ganti total.
7. **Klaim hasil model** — Intisari lama menyiratkan sistem sudah bekerja. Padahal RQ1–RQ4 belum
   dijalankan. → Batasi pada validasi verifikator (100% / 66,7% / 20 pengujian, sudah ada) +
   placeholder untuk hasil model.

### 1.3 Pendahuluan lama — cacat spesifik

- **Struktur bersubbab** (A. Kesenjangan, B. Kontribusi, C. Rumusan Masalah) — juri minta prosa
  argumentatif langsung. Subbab memotong alur dan membuat tiap bagian terbaca seperti daftar.
- **Permasalahan teoritis dangkal.** Naskah lama menyebut "LLM lemah berhitung" tetapi tidak
  menjelaskan *mengapa* secara teoretis (sifat *autoregressive*/prediksi *token* berikutnya atas
  pola bahasa), dan tidak menamai **celah verifikasi**: akurasi jawaban adalah proksi lemah karena
  model bisa "benar karena alasan yang salah". Tarik-menarik *grounding* lawan *token* — inti
  kebaruan — hanya disinggung, tidak dibangun sebagai masalah terbuka.
- **Dampak aplikasi nyata dangkal.** Disebut "kesehatan dan pangan" tetapi tanpa rantai sebab-akibat
  konkret: apa kerugian nyata bila model salah? Perlu skenario spesifik (wabah terlewat, salah
  besaran inflasi → salah kebijakan), kebutuhan auditabilitas untuk akuntabilitas, dimensi biaya
  *token* saat *deploy*, dan kekosongan *dataset* lokal Indonesia.
- **Bahasa kolokial**: "menebak dari pola bahasa", "salah walau kalimatnya meyakinkan", "diam-diam
  jadi tidak grounded" — perlu dinaikkan ke register ilmiah.
- **Konektivitas lemah**: kalimat berdiri sendiri tanpa transisi; pembaca harus merakit sendiri
  argumennya.

### 1.4 Prinsip penulisan yang diterapkan pada revisi

1. **Dua sumbu masalah dibangun eksplisit dan rinci** sesuai permintaan: sumbu **teoretis** (sifat
   LLM → celah verifikasi → tarik-menarik *grounding*–*token* sebagai masalah terbuka) dan sumbu
   **aplikasi nyata** (skenario kerugian konkret, auditabilitas/akuntabilitas, biaya *deploy*,
   kekosongan data lokal).
2. **Alur argumentatif**: konteks → akar teoretis → celah yang belum terpecahkan → taruhan dunia
   nyata → usulan ringkas → RQ. Tanpa subbab pemotong.
3. **Diksi ilmiah, istilah teknis asli dipertahankan**, kalke dibuang.
4. **Nihil klaim hasil model**; hanya validasi verifikator (fakta) + placeholder.

---

## Bagian 2 — Hasil revisi (siap tempel)

### 2.1 Intisari

> **INTISARI —** *Large language model* (LLM) unggul mengolah bahasa alami, tetapi keandalannya
> menurun ketika penalaran menuntut komputasi numerik atas data *time series*. Karena bekerja
> dengan memprediksi *token* berikutnya berdasarkan pola kebahasaan, model cenderung mengira-ngira
> alih-alih menghitung, sehingga kesimpulan dapat keliru meski kalimatnya meyakinkan. Pada domain
> berisiko tinggi seperti kesehatan masyarakat dan pangan, penalaran semacam ini dituntut dapat
> diaudit, yakni setiap angka pada tiap langkah dapat diperiksa ulang atau *grounded*. Namun dua
> kelompok metode yang ada saling bertolak belakang: penalaran terverifikasi bersifat boros
> *token*, sedangkan penalaran hemat *token* hanya menjaga akurasi jawaban tanpa memeriksa
> kesahihan langkah antaranya. Akibatnya, pemangkasan *token* berpotensi menurunkan *grounding*
> tanpa terdeteksi walau jawaban akhir tampak benar. Untuk menutup celah tersebut, diusulkan
> pendekatan yang memisahkan penalaran menjadi dua komponen: LLM hasil *fine-tune* yang menuliskan
> penalaran sebagai urutan *operasi* dari pustaka tetap, dan verifikator deterministik berbasis
> NumPy yang menghitung ulang serta memeriksa tiap operasi terhadap deret asli. Skor *grounding*
> dihitung tanpa penilai LLM dan dilaporkan bersama akurasi jawaban dan jumlah *token*. Validasi
> verifikator memperoleh skor *grounding* 100% pada penalaran valid dan 66,7% ketika halusinasi
> disuntikkan, serta lolos 20 pengujian otomatis. [[PLACEHOLDER — hasil eksperimen model (RQ1–RQ4)
> dilengkapi setelah pelatihan dan evaluasi selesai]]. Kebaruan penelitian terletak pada temuan
> tarik-menarik *grounding* lawan *token* dan pada mekanisme efisiensi yang sadar *grounding*, bukan
> sekadar penggabungan dua pendekatan.

**KATA KUNCI:** *grounded reasoning*, *time series*, skor *grounding*, verifikator deterministik,
efisiensi *token*, *Chain-of-Thought*, *fine-tune* LLM, QLoRA, penalaran neuro-simbolik.

*(Catatan: bila panjang Intisari melebihi batas venue, kalimat validasi verifikator dapat
diringkas menjadi satu klausa; jangan hapus kalimat kebaruan dan kalimat celah.)*

---

### 2.2 I. Pendahuluan

**I. PENDAHULUAN**

Data *time series* menempati inti banyak keputusan penting — kasus penyakit yang dilaporkan tiap
minggu, harga pangan yang dipantau tiap hari, dan beban energi yang tercatat tiap jam — sehingga
kemampuan menafsirkan deret angka secara benar bernilai tinggi. *Large language model* (LLM)
menjanjikan antarmuka yang luwes untuk penafsiran tersebut, tetapi keandalannya menurun tajam saat
persoalan bergeser dari bahasa ke bilangan. Akar persoalannya bersifat teoretis: LLM dilatih untuk
memprediksi *token* berikutnya berdasarkan pola kebahasaan, sehingga ketika diberi sederet angka ia
cenderung mereproduksi pola yang lazim menyertai angka serupa alih-alih melakukan komputasi
sebenarnya. Studi mutakhir menegaskan bahwa model masih kesulitan menalar *time series* bahkan pada
pengaturan *zero-shot* [1], [2]. Sebagai ilustrasi, pada deret kasus demam berdarah selama 16 minggu
`12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78`, model kerap menyimpulkan kondisi
stabil padahal nilai akhir mencapai sekitar enam kali garis dasar, salah menunjuk minggu terjadinya
lonjakan, atau menyebut kenaikan 30% padahal mendekati 105%.

Upaya baku mengatasi kelemahan ini adalah memperpanjang penalaran melalui *Chain-of-Thought* [6] dan
memindahkan komputasi ke program pada *Program-of-Thought* [7]. Pendekatan tersebut kerap menaikkan
akurasi jawaban, namun menyisakan celah yang lebih mendasar: akurasi jawaban adalah proksi yang
lemah bagi kualitas penalaran. Sebuah model dapat menghasilkan jawaban benar melalui langkah-langkah
antara yang keliru — benar karena alasan yang salah — dan selama langkah tersebut ditulis sebagai
prosa bebas, kekeliruannya tidak dapat diperiksa. Dengan kata lain, memperpanjang penalaran tidak
dengan sendirinya membuatnya *grounded*, yaitu membuat tiap angka pada tiap langkah dapat dihitung
ulang dan diverifikasi terhadap deret asli.

Kebutuhan akan penalaran yang *grounded* justru berbenturan dengan kebutuhan akan efisiensi, dan di
sinilah letak celah yang belum terpecahkan. Di satu sisi, metode penalaran terverifikasi untuk
*time series* seperti VeriTime [3] menjamin kesahihan langkah namun menghasilkan penalaran panjang
yang boros *token*. Di sisi lain, metode hemat *token* seperti SelfBudgeter [4] mengatur anggaran
penalaran demi efisiensi, tetapi mengoptimalkan akurasi jawaban semata tanpa pernah memeriksa
kesahihan langkah antaranya. Konsekuensinya adalah tarik-menarik yang selama ini luput: ketika
penalaran dipendekkan untuk menghemat *token*, skor *grounding* dapat menurun lebih cepat daripada
akurasi jawaban, sehingga penalaran kehilangan keterandalannya tanpa terdeteksi oleh metrik yang
hanya memantau jawaban akhir. Menjaga *grounding* tetap tinggi di bawah anggaran *token* — khususnya
pada *time series* — dengan demikian merupakan masalah terbuka, bukan sekadar penggabungan dua
pendekatan yang sudah ada. [[PLACEHOLDER — besar penurunan *grounding* relatif terhadap akurasi saat
*token* dipangkas dikuantifikasi pada Eksperimen 2 (RQ2)]].

Taruhan dari celah ini nyata dan berlipat pada domain berisiko tinggi. Pada pengawasan kesehatan
masyarakat, model yang menyimpulkan tren datar padahal kasus melonjak enam kali lipat dapat menunda
respons wabah, dengan biaya kesehatan dan sosial yang tidak dapat dipulihkan. Pada pemantauan pangan,
kesalahan menaksir besaran kenaikan harga — misalnya melaporkan 30% alih-alih 105% — dapat memicu
intervensi kebijakan yang keliru sasaran. Pada konteks demikian, sebuah jawaban tidak cukup benar; ia
harus dapat dipertanggungjawabkan, artinya jejak penalarannya dapat diaudit angka demi angka oleh
pengambil keputusan. Penalaran yang tidak *grounded* tidak dapat diaudit, sehingga tidak layak
menjadi dasar keputusan meski jawabannya kebetulan benar. Persoalan efisiensi pun bukan sekadar
kenyamanan: penalaran yang panjang menaikkan biaya inferensi dan menyulitkan penerapan pada perangkat
terbatas, sehingga efisiensi *token* menjadi syarat kelayakan operasional — namun tidak boleh
ditebus dengan hilangnya *grounding* secara tidak terpantau. Persoalan ini kian mengemuka di
Indonesia, yang kaya sumber data publik seperti harga pangan Bank Indonesia [14], dasbor penyakit
Kementerian Kesehatan [15], dan data cuaca BMKG [16], tetapi belum memiliki *dataset* penalaran *time
series* terverifikasi berbahan sumber lokal sebagai landasan pengembangan dan evaluasi.

Untuk menjawab persoalan tersebut, diusulkan sebuah pendekatan yang secara arsitektural memisahkan
tanggung jawab: komponen model berupa LLM hasil *fine-tune* menuliskan penalaran sebagai urutan
*operasi* dari pustaka tetap alih-alih prosa bebas, sedangkan komponen program berupa verifikator
deterministik menghitung ulang tiap *operasi* atas deret asli dan memeriksa kesesuaiannya dalam
toleransi. Dengan pemisahan ini, model tidak pernah memegang kepemilikan atas angka; angka dihitung
dan diperiksa oleh program di luar model, sehingga penalaran tetap dapat diaudit. Di atas fondasi
tersebut dirancang mekanisme penalaran adaptif yang sadar *grounding*, yang menargetkan rantai
*operasi* ter-*grounded* terpendek yang memadai untuk tiap persoalan, sehingga efisiensi dan
*grounding* dioptimalkan bersama alih-alih dipertukarkan buta. Kontribusi penelitian ini ada tiga dan
saling menopang: pertama, temuan empiris mengenai tarik-menarik *grounding* lawan *token* yang
menjustifikasi celah; kedua, *dataset* penalaran *time series* terverifikasi dari sumber publik
Indonesia dengan label bersih *by construction* karena disaring verifikator di dalam *loop*; dan
ketiga, metrik skor *grounding* deterministik yang dihitung tanpa penilai LLM dan dilaporkan bersama
akurasi jawaban serta jumlah *token* sehingga tarik-menariknya terlihat.

Berdasarkan uraian di atas, penelitian ini menjawab empat pertanyaan penelitian. **RQ1**: seberapa
sering model yang ada saat ini menghasilkan penalaran ber-*grounding* rendah saat menalar *time
series*, walaupun jawaban akhirnya kadang benar? **RQ2**: ketika penalaran dipendekkan untuk
menghemat *token*, apakah *grounding* menurun lebih cepat daripada akurasi jawaban? **RQ3**: apakah
pendekatan yang diusulkan mempertahankan *grounding* tinggi pada anggaran *token* yang jauh lebih
hemat, yakni unggul pada rasio *grounding* per *token* dibanding *baseline* penalaran panjang maupun
*baseline* hemat yang buta *grounding*? **RQ4**: berapa sumbangan tiap komponen — format *operasi*,
target rantai ter-*grounded* terpendek, adaptivitas, dan *fine-tune* — terhadap kinerja keseluruhan?
[[PLACEHOLDER — ringkasan temuan RQ1–RQ4 ditambahkan pada kalimat penutup Pendahuluan setelah
eksperimen selesai]]. Sisa makalah tersusun sebagai berikut: Bagian II meninjau pustaka terkait,
Bagian III memaparkan usulan penelitian, Bagian IV menjabarkan metodologi, Bagian V menyajikan
rancangan eksperimen dan hasil, serta Bagian VI menutup dengan kesimpulan dan saran.

---

## Catatan pemakaian

- Placeholder `[[PLACEHOLDER — ...]]` **wajib** diisi atau dihapus sebelum submit; jangan biarkan
  muncul di naskah final.
- Bila juri tetap menilai Intisari terlalu padat, prioritas yang dipertahankan: (1) kalimat celah
  (tarik-menarik *grounding*–*token*), (2) kalimat kebaruan, (3) kalimat usulan dua komponen. Kalimat
  validasi verifikator dapat diringkas.
- Terapkan diksi yang sama (buang kalke, pertahankan istilah asli) ke Tinjauan Pustaka dan Metodologi
  pada revisi berikutnya agar naskah konsisten — juri menandai gaya terjemahan pada seluruh artikel.
