# CONCERNS — pertanyaan penting user + cara verifikasi (living register)

Daftar concern/pertanyaan penting user **beserta cara membuktikannya**. Tiap sesi cek di sini biar
concern tak hilang antar-sesi. Update `Status:` saat ditangani, kaitkan ke issue di [`BOARD.md`](BOARD.md).

Status: `open` · `in-progress` · `resolved`

---

## C1 — n benchmark kecil (18) → daya statistik lemah
- **Concern:** klaim RQ1/RQ2 disandarkan pada n=18; error bar lebar, non-monotone (gemma cap-2, llama panjang outlier).
- **Cara verifikasi/atasi:** skala test → 100–300 item real (lihat C4). Di paper laporkan n + sebar per tugas/kesulitan; jangan klaim keras dari n kecil.
- **Owner:** F4-03 / F4-05. **Status:** open.

## C2 — grounding rendah: hallucination asli atau artefak verifier?
- **Concern:** grounding stock 2–16% — model beneran ngarang angka, atau verifier kepedean nolak sintaks index?
- **Cara verifikasi:** audit sintaks — neg-index (`nilai[-1]`) dulu ditolak → **fixed commit `5c5a38c`**; item-1 langkah pakai slice yang didukung → 0% grounding = hallucination **asli**. Nested-call tetap ditolak by design (ADR-0003, flat-op).
- **Status:** resolved.

## C3 — verifier = pembersih data + juri eval (sirkular?)  [#5]
- **Concern:** verifier bikin label train **dan** nilai eval. Reviewer bisa bilang "skor grounding = apa kata kodemu sendiri".
- **Cara verifikasi:**
  1. **Recompute independen** — hitung ulang tiap langkah ter-skor lewat **jalur kedua** (`experiments/verifier-crosscheck/independent.py`, NumPy murni, nol impor `gearts`; parser + semantik index/slice + rumus ditulis ulang tangan, mis. `slope` OLS bukan `np.polyfit`), cocokin sama `expected` verifier. **Hasil (2026-07-17, train di-scale ke 600): 771/771 = 100.00% match, 0 mismatch** atas `benchmark_acuan` (21) + `train_acuan` (750, data yang dibersihkan verifier); `benchmark_uji` reasoning kosong (0 langkah). Bug verifier: nihil. Runner `crosscheck.py`, notebook `docs/lab-notebook/2026-07-16-verifier-crosscheck.md` (dicatat saat 336; angka kini 771 di 600), pytest 110 passed.
  2. **Spot-check manusia** — `experiments/verifier-crosscheck/spotcheck.csv` (10 grounded nyata + 10 ungrounded perturbasi) siap diaudit; agreement label pada output model **asli** menunggu keluaran track eval.
- **Catatan:** F1-04 (done) cuma bukti **internal** (verifier cocok Lampiran B/D + tolerance sweep) — BUKAN cross-check independen; item ini yang independen. Cross-check **mencakup train** (label train juga verifier-made, by construction) — jadi kekhawatiran sirkularitas sisi-train ikut tertutup, bukan cuma sisi-eval.
- **Owner:** Track A (#5). **Status:** in-progress — aritmetik terbukti tak sirkular (100% match); sisa: agreement manusia pada output model asli.

## C4 — test benchmark skala + generalisasi lapangan  [#4]
- **Concern:** 18 test item kekecilan buat klaim generalisasi lapangan.
- **Cara verifikasi/atasi:** skala ke 100–300 item **real**, verifier-clean, stratified (tugas × kesulitan), anti-bocor (sumber test ≠ train).
  - Termurah: +30–50 indikator WB-IDN + banyak pertanyaan per series (tren/segmen/anomali/penjelasan di window beda).
  - Lebih kuat: +≥1 sumber Indonesia frekuensi tinggi (PIHPS harga pangan harian / BMKG) walau sedikit.
- **Owner:** F4-03 + regen `curate_benchmark_uji.py`. **Status:** open.

## C5 — series TRAIN sintetik, bukan real (kualitas data untuk lomba data-mining)  [F4-03]
- **Concern (user, 2026-07-17):** ini lomba **data mining** → kualitas & pemrosesan data real berbobot nilai. 600 train saat ini = deret **sintetik-terkendali**; kenapa bukan sumber asli? Catatan: **label reasoning selalu disintesis+verify** (kontribusi utama, tak terhindar); yang bisa di-"real"-kan hanya **series (angka deret)**.
- **Keputusan:** upgrade series train ke **real, sumber ke-2** (bukan WB test → anti-bocor bersih).
- **Probe kelayakan (2026-07-17, live curl dari box):**
  - **PIHPS/BI** `GetGridDataDaily` → balas kosong; tak ada API resmi. **Mati/rapuh, di-skip.**
  - **Bapanas Panel Harga v2** (`api-panelhargav2.badanpangan.go.id`) → **harian**, tapi key-gated keras. Key frontend publik (`x-api-key`, 160-char, di `main.*.js`) **tetap ditolak** walau + Referer/Origin → kemungkinan interceptor tanda-tangani per-request/recaptcha. **Defer** (butuh Playwright/analisis lebih dalam).
  - **BMKG** forecast `data.bmkg.go.id` hidup tapi **jangka-pendek** (bukan histori panjang); `dataonline` histori butuh registrasi/form.
  - **BPS Web API** (`webapi.bps.go.id`) → **DIPILIH**: JSON resmi, docs `/documentation/` + register `/developer/` (200), key gratis, TOS jelas, bulanan histori panjang, provider ≠ WB.
- **Implikasi desain (jujur, harus di-disclose):** dgn series **real**, kesulitan=label **muncul dari data** (`build_reference` hitung label jujur per window) — tak bisa dipaksa seimbang via reject-sampling spt generator sintetik. Strata jadi **best-effort**; laporkan distribusi nyata; sintetik jadi backfill strata tipis.
- **HASIL (2026-07-17, key BPS didapat user):** adapter `src/gearts/scrapers/bps.py` (network di-isolasi, konstruksi-key + normalisasi pure, 13 unit-test). `scripts/synthesize_train_real.py` → **143 deret nyata BPS** (5 indikator: miskin P0/jumlah, garis kemiskinan, pengangguran, gini; per-provinsi) → **572 sampel, 100% grounded, anti-bocor 0**. Label emergent jujur; ANOMALI auto-detect (baseline jendela-awal) → `ada_anomali` 62 / `tidak` 81 (guncangan COVID-2020 nyata). Digabung sintetik 600 (penyeimbang sel tipis) → `data/train_unsloth.jsonl` **1172** (572 real + 600 sintetik). ADR-0005. pytest 123 passed. Key via env, tak di-commit.
- **Owner:** F4-03. **Status:** resolved — train kini mengandung deret nyata BPS. Sisa pengayaan (opsional): BPS bulanan (`turth`) + Bapanas harian via Playwright.

---

## Keputusan tercatat
- **D1 (2026-07-16):** framework fine-tune = **Unsloth** (bukan LLaMA-Factory). Tetap QLoRA NF4 4-bit, Qwen2.5-7B-Instruct. F5-01 direframe; butuh converter gearts JSONL → format chat Unsloth. ADR menyusul saat F5-01 di-grill.
  - **Update (Sesi D, F4-05, 2026-07-17):** converter **sudah ada** — `scripts/to_unsloth.py` → `data/train_unsloth.jsonl` (sharegpt `messages`) + `data/dataset_info.json`. user=`build_prompt(mode="pendek")`, assistant=reasoning gold. Round-trip converter→`parse_model_output` diuji identik. Siap dipakai F5-01.
