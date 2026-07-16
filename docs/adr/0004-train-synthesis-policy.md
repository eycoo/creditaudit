# ADR-0004: Kebijakan sintesis TRAIN set (F4-04)

**Status:** Accepted (2026-07-16). **Diamandemen oleh [ADR-0005](0005-train-real-bps.md)**
(2026-07-17): train kini hibrid — deret nyata BPS ditambahkan; sintetis-terkendali di
sini tetap dipakai sebagai penyeimbang strata, bukan lagi satu-satunya sumber. Mengimplementasikan pipeline dataset brief v2 §4.3 untuk sisi *train*.
Menghasilkan `data/synthetic/train_acuan.jsonl` (336 sampel) via `scripts/synthesize_train_acuan.py`.
Tidak mengubah `operations.py`/`verifier.py`/`synthesize_reasoning_acuan.py` — memakai ulang `build_reference`
dan `verify_sample` apa adanya (semantik operasi tetap ADR-0003).

## Konteks

F4-04 butuh train set berlabel bersih untuk fine-tune (Qwen2.5-7B, QLoRA). Dua kendala nyata malam ini:
scrape penuh (F4-03) ditunda, dan **satu-satunya deret nyata yang ada di repo (`data/raw/*.json`, 18 indikator
World Bank) adalah sumber benchmark UJI**. Brief v2 §4.3 langkah 7 dan §9.4 melarang sumber uji muncul di
train (anti-bocor). Sekaligus brief membolehkan train "didominasi semi-sintetis: deret nyata **atau
terkendali** + reasoning terverifikasi".

## Keputusan

**1. Sumber train = deret sintetis-terkendali yang dibangkitkan sendiri; deret WB uji TIDAK dipakai.**
Ini menutup anti-bocor secara struktural (bukan sekadar split), memberi kendali penuh atas strata, dan bisa
jalan tanpa network. Opsi "pakai `data/raw` WB untuk train" **ditolak**: file itu justru benchmark uji;
memakainya = bocor. (Di worktree `gems-D` `data/raw` malah kosong—gitignored—jadi opsi itu juga tak
tereksekusi.) Cek anti-bocor tetap dijalankan sebagai bukti: tiap deret train dibandingkan numerik dengan 18
deret uji → **0 tabrakan**; namespace id terpisah (`train_*` vs `uji_*`).

**2. Verifier di dalam loop, label bersih by construction** (brief v2 §4.3 langkah 4–5). Tiap sampel:
deret → `build_reference` (rantai operasi **terpendek**, `hasil` tiap langkah dihitung ULANG oleh
`eval_step`) → `verify_sample` di-*assert* 100%. Sampel yang tak 100% grounded (mis. std baseline 0, base
`persen_naik` 0) **dibuang & dibangkitkan ulang** dengan tarikan rng berikut (reject-sampling). Rantai memakai
`build_reference` yang sama dengan benchmark acuan → train & test memakai definisi grounding **identik**.

**3. Kesulitan mengatur sinyal, bukan cuma label** (brief v2 §4.2). Tiap (tugas × kesulitan) punya prasyarat
penerimaan `_accept` atas (label, keyakinan); deret di-*reject-sample* sampai lolos:

| tugas | easy | medium | hard (ambigu/menahan diri) |
|---|---|---|---|
| tren | meningkat/menurun, yakin tinggi | idem, sedang | relatif_stabil |
| segmen | paruh_* lebih tinggi, tinggi | idem, sedang | setara |
| anomali | ada_anomali, \|z\|≥5 | ada_anomali, \|z\|∈[3,5) | tidak_ada_anomali (near-miss \|z\|∈[1.6,2.8)) |
| penjelasan | naik/turun_besar | naik/turun_kecil | tidak_monoton |

**4. Skala & determinisme.** 4 tugas × 3 kesulitan × 28 = **336** sampel (>300), 12 strata seimbang, 8 profil
domain (kesehatan, pangan, energi, cuaca) untuk ragam satuan/frekuensi. Seed per (task, diff, rep) via
`crc32` → regenerasi identik (diuji).

## Konsekuensi & batasan (sengaja tidak di-scope malam ini)

- **Panjang rantai ditentukan jenis tugas** (tren/segmen/anomali = 1 langkah, penjelasan = 2), bukan
  digradasi halus oleh kesulitan. Adaptivitas panjang penuh brief v2 §4.2 (deret makin ambigu → rantai makin
  panjang) menunggu pustaka operasi lebih kaya; ditandai sebagai kerja lanjutan, bukan blocker fine-tune.
- **`deteksi_anomali` (non-skalar) dihindari**; anomali diekspresikan lewat `z_score` skalar (baseline
  eksplisit, ADR-0003 Item 3C) agar 100% grounded — konsisten dengan F2-02.
- **Realisme = semi-sintetis**, bukan deret nyata. Level/satuan/frekuensi dipilih masuk akal per domain, tapi
  angkanya dibangkitkan; `konteks` menyebut "sintetis-terkendali" (jujur, tak mengklaim provenance nyata).
- **Anti-bocor kuat**: train lepas total dari sumber uji. Konsekuensinya generalisasi lapangan tetap harus
  dibuktikan di **test** (deret nyata WB); train sintetis mengajari *struktur* reasoning, test menilai transfer.
- Split train/test formal + stratifikasi lintas file = **F4-05** (memakai artefak ini + benchmark uji).

## Alternatif yang ditolak

- **Derivasi train dari deret WB uji** (sub-window/transformasi): tetap berbagi sumber & bentuk dengan test →
  risiko bocor tinggi untuk manfaat kecil. Ditolak.
- **Tunggu F4-03 (scrape PIHPS/Kemenkes/BMKG)**: benar untuk realisme maksimal, tapi memblok fine-tune malam
  ini; brief eksplisit membolehkan train terkendali. Scrape nyata menyusul memperkaya, bukan prasyarat.
