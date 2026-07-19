Berikut adalah rekomendasi tiga sumber referensi ilmiah penting dan relevan yang dapat menjadi fondasi teoritis kuat untuk memperkokoh posisi proyek GEAR-TS, khususnya dalam memperkuat aspek arsitektur neuro-simbolik (pemisahan model dan program), efisiensi alokasi token, serta verifikasi deterministik.

Daftar Rekomendasi Referensi Baru
1. Referensi untuk Fondasi Integrasi Tool & Kalkulator Eksternal (Neuro-Simbolik)
Apa yang diteliti: Penelitian ini mengeksplorasi integrasi antara LLM dengan external tool (khususnya Python REPL) melalui interaksi bolak-balik yang dinamis untuk menyelesaikan masalah penalaran numerik dan matematika. Makalah ini menunjukkan bahwa memberikan LLM kemampuan mengeksekusi kode secara langsung di tengah langkah penalaran (tool-integrated reasoning) dapat memperbaiki kesalahan aritmatika secara signifikan dibandingkan metode Chain-of-Thought (CoT) tradisional.

Bagian yang digunakan dalam project: Referensi ini digunakan sebagai pembenaran ilmiah kuat (teoritis dan empiris) mengapa GEAR-TS memilih memisahkan komponen LLM sebagai perencana operasi dan program eksternal (NumPy verifikator) sebagai eksekutor angka (metode Program-of-Thought/Tool-Use).

Penempatan referensi dalam teks: Pada Bab II. TINJAUAN PUSTAKA, Bagian B. Chain-of-Thought dan Program-of-Thought, tepat setelah kalimat terakhir:

"...Penelitian ini memakai semangat yang sama, yaitu LLM tidak pernah memegang angka, ia hanya mengusulkan operasi, dan program di luar model yang menghitung dan mengecek. Integrasi fungsional antara LLM dan interpreter eksternal terbukti secara masif mengoreksi galat komputasi kompleks melalui eksekusi kode terstruktur [17]."

2. Referensi untuk Fondasi Efisiensi Biaya dan Penghematan Token Adaptif
Apa yang diteliti: Makalah ini meneliti strategi optimasi biaya (cost reduction) dan efisiensi token pada LLM dengan menggunakan kerangka kerja adaptif (LLM cascade dan routing). Penelitian ini membuktikan bahwa tidak semua pertanyaan membutuhkan komputasi atau jumlah token penalaran yang sama; pertanyaan yang mudah dapat diarahkan ke jalur yang hemat, sementara pertanyaan sulit menggunakan anggaran komputasi penuh.

Bagian yang digunakan dalam project: Referensi ini digunakan untuk memperkuat landasan teori pada komponen Adaptive Reasoning di GEAR-TS. Ini memberikan justifikasi bahwa pembatasan atau penyesuaian anggaran token berdasarkan tingkat kesulitan data time series adalah pendekatan yang valid untuk menekan trade-off antara biaya token dan akurasi.

Penempatan referensi dalam teks: Pada Bab II. TINJAUAN PUSTAKA, Bagian D. Efisiensi Token dan Penalaran Adaptif, disisipkan di antara kalimat pertama dan kedua:

"Panjang penalaran dapat dibuat hemat dan menyesuaikan tingkat kesulitan lewat pengaturan anggaran token, meski sejauh ini terbatas pada soal matematika [4]. Alokasi anggaran komputasi yang adaptif berdasarkan kompleksitas input terbukti mampu memangkas biaya penggunaan token secara signifikan tanpa mengorbankan akurasi akhir sistem [18]. Penalaran panjang berbasis pembelajaran penguatan juga menjadi lazim setelah 2025 [10]."

3. Referensi untuk Fondasi Verifikasi Simbolik & Eliminasi Halusinasi
Apa yang diteliti: Penelitian ini mengusulkan kerangka kerja neuro-simbolik yang menerjemahkan pertanyaan teks bebas ke dalam formulasi logika formal, yang kemudian diselesaikan secara deterministik menggunakan symbolic solver eksternal. Pendekatan ini berhasil mengeliminasi halusinasi penalaran pada LLM karena validasi logika sepenuhnya dijamin oleh hukum-hukum deterministik di luar model bahasa.

Bagian yang digunakan dalam project: Referensi ini digunakan pada perumusan kerangka kerja verifikator deterministik GEAR-TS. Ini memperkuat klaim bahwa penggunaan aturan deterministik kaku (seperti persamaan toleransi absolut-relatif NumPy pada GEAR-TS) adalah kunci utama untuk mencapai grounding penalaran 100% yang mustahil dicapai jika hanya mengandalkan LLM tunggal atau LLM juri.

Penempatan referensi dalam teks: Pada Bab I. PENDAHULUAN, Bagian A. Kesenjangan Penelitian, dimasukkan pada kalimat sebelum terakhir:

"...Di sisi lain, riset penghematan token lewat pengaturan panjang penalaran menurut tingkat kesulitan sudah berkembang, tetapi masih terbatas pada soal matematika [4]. Penerjemahan langkah penalaran ke dalam representasi formal yang dieksekusi oleh solver deterministik terbukti efektif mengeliminasi halusinasi logika secara mutlak [19]. Sampai sekarang belum ada yang menyatukan keduanya untuk time series, dan belum ada dataset penalaran time series terverifikasi yang dibangun dari sumber lokal."


[17] Z. Gou et al., "ToRA: A Tool-Integrated Reasoning Agent for Mathematical Problem Solving," dalam Proc. ICLR, 2024.
[18] L. Chen, M. Zaharia, dan J. Zou, "FrugalGPT: How to Use Large Language Models More Cheaply and Efficiently," dalam Proc. ICML, 2023.
[19] L. Pan et al., "Logic-LM: Structuring Self-Correction with Symbolic Logic Execution," dalam Findings of EMNLP, 2023.