# Aturan Format GEMASTIK (dari templat resmi Word)

Diekstrak dari `_Template__Makalah_Gemastik_ieee.docx`. Ini adalah aturan
yang mengikat — gunakan sebagai sumber kebenaran, bukan asumsi umum tentang
format IEEE.

## Halaman dan margin

- Kertas A4: lebar 210 mm, panjang 297 mm.
- Margin: atas 23 mm (0.90"), bawah 18 mm (0.70"), kiri = kanan 13 mm (0.51").
- Format **dua kolom**, jarak antar kolom 7.1 mm (0.28").
- Paragraf rata kiri-kanan (justified).
- **Panjang makalah: 4 sampai 5 halaman**, termasuk referensi. Ini batasan
  keras dari panitia — pantau jumlah halaman selama menulis.
- Wajib empat bab utama minimum: Pendahuluan, Metode/Inovasi, Hasil dan
  Diskusi, Kesimpulan — plus Referensi.

## Font

- Seluruh dokumen: Times New Roman (atau font Times). Font tipe 3 tidak
  boleh dipakai.
- **Judul**: Helvetica, 20pt, bold. Maksimum 12 kata per judul.
- **Nama penulis**: Helvetica, 9pt, bold. Tidak boleh mencantumkan jabatan
  (mis. "Dosen Pembimbing"), gelar akademik (mis. "Dr."), atau keanggotaan
  organisasi profesional.
- **Afiliasi**: 7pt (88900 EMU), regular. Minimal mencantumkan nama
  institusi dan negara, plus email penulis bersangkutan.
- **Intisari (abstrak) dan Kata Kunci**: 10pt (127000 EMU), body text.
- **Heading semua level**: Helvetica, 9pt (114300 EMU), huruf kapital di
  setiap kata.
- **Body text**: Times New Roman, 10pt.
- **Label gambar**: Helvetica bold, 8pt.
- **Label/judul tabel**: Times New Roman, 8pt, Small Caps.
- **Referensi**: Times New Roman, 8pt.

## Heading levels (maks. 3 tingkat, semua Helvetica 9pt, huruf kapital)

- **Level 1** (`\section`): kapital semua, bold, rata kiri, angka Romawi
  kapital + titik. Contoh: "III. STYLE HALAMAN". Pengecualian tanpa nomor:
  "REFERENSI".
- **Level 2** (`\subsection`): kapital semua, bold + italic, rata kiri,
  huruf kapital sebagai nomor (A., B., C., ...).
- **Level 3** (`\subsubsection`): kapital semua, italic (tidak bold), rata
  kiri, angka Arab + tanda kurung tutup, mis. "1)". Isi diletakkan sebagai
  paragraf baru di bawah judul, bukan di baris yang sama.

## Judul dan penulis

- Setiap kata di judul diawali huruf kapital, kecuali kata hubung/preposisi/
  partikel ("dan," "di," "oleh," "untuk," "dari," "pada," "atau").
- Hindari rumus panjang bersubskrip di judul; rumus pendek boleh (mis.
  "Nd-Fe-B").
- Nama keluarga di posisi terakhir tiap nama penulis.
- Setiap penulis diberi superskrip nomor yang merujuk ke afiliasi + email
  di bawahnya.
- Baris "Corresponding Author: [Nama]" wajib ada.

## Intisari (Abstrak)

- Bahasa Indonesia, 200–300 kata.
- **Struktur wajib 4 bagian** dalam satu paragraf mengalir:
  1. Pengantar/latar belakang (~1/4 dari total intisari)
  2. Tujuan penulisan
  3. Metodologi singkat
  4. Penjelasan hasil penelitian secara keseluruhan
- Tidak boleh berisi: persamaan, tabel, kutipan/sitasi, atau referensi.
- Diawali label "INTISARI —" dalam huruf kapital, italic-bold untuk label.

## Kata Kunci

- 4–8 kata kunci, dipisah koma, tiap kata diawali huruf kapital.
- Label "KATA KUNCI —" di atasnya.

## Gambar dan tabel

- Diposisikan di tengah (centered); boleh direntangkan ke dua kolom jika
  perlu (`figure*`/`table*` di LaTeX, atau `\begin{figure}[t]` untuk single
  column, di atas/bawah halaman).
- Grafik boleh berwarna di layar, tapi asumsikan akan dicetak hitam-putih —
  gunakan kontras yang jelas, hindari pola titik-titik/dotted patterns.
- Resolusi gambar minimal 300 ppi.
- **Label gambar**: angka Arab, Helvetica bold 8pt. Judul satu baris
  di-center; judul multi-baris di-justify. Label+judul diletakkan **setelah**
  gambar (di bawahnya) — ini standar LaTeX `\caption` untuk `figure`, jadi
  tidak perlu penyesuaian khusus.
- **Label tabel**: angka Romawi kapital (I, II, III, ...), Times New Roman
  8pt, Small Caps, center. Judul tabel: setiap kata diawali kapital kecuali
  kata hubung/preposisi. Label+judul diletakkan **sebelum** tabel (di
  atasnya) — juga standar LaTeX untuk `table`.

## Persamaan

- Persamaan dinomori berurutan dalam tanda kurung, rata kanan: `(1)`, `(2)`.
- Definisikan simbol sebelum atau segera setelah persamaan muncul.
- Simbol diketik italic.
- Merujuk persamaan: tulis "(1)" saja, bukan "Pers. (1)" atau
  "persamaan (1)" — kecuali di awal kalimat: "Persamaan (1) merupakan…"

## Singkatan dan link

- Definisikan singkatan saat pertama disebut di teks, walau sudah
  didefinisikan di intisari. Singkatan umum (IEEE, AC, DC) tidak perlu.
- Singkatan bertitik tidak dipisah spasi: "C.N.R.S." bukan "C. N. R. S."
- Hindari singkatan di judul kecuali tak terhindarkan.
- URL/email di teks: Times New Roman, italic, tanpa hyperlink aktif
  (hyperlink akan dihapus saat proses penerbitan — gunakan
  `\usepackage[hidelinks]{hyperref}` agar tetap terlihat seperti teks biasa).

## Referensi

- Judul bagian "REFERENSI" tanpa nomor heading.
- Semua item referensi font 8pt.
- Format IEEE: sitasi di teks pakai nomor saja dalam kurung siku, mis.
  "[2]" — jangan "Ref. [3]" atau "Referensi [3]" kecuali di awal kalimat:
  "Referensi [3] menunjukkan bahwa…"
- Beberapa referensi sekaligus: "[2], [3], [4]-[6]".
- Item referensi dinomori berurutan sesuai urutan kemunculan sitasi
  pertama di teks (bukan alfabetis).

## Header dan footer halaman (banner buletin)

Setiap halaman punya header di kiri atas:
```
BULETIN PAGELARAN MAHASISWA NASIONAL BIDANG TEKNOLOGI INFORMASI DAN KOMUNIKASI
ISSN: xxxxxx
```
dan footer berisi nama ketua tim + potongan judul di kiri, volume/nomor/
bulan/tahun di kanan. Lihat `assets/template.tex` untuk implementasi
`fancyhdr` yang sudah sesuai.
