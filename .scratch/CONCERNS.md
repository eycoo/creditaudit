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
- **Cara verifikasi (belum jalan):**
  1. **Recompute independen** — ambil N langkah random dari benchmark, hitung ulang tiap operasi lewat **jalur kedua** (pandas / rumus manual, bukan `verifier.py`), cocokin sama `expected` verifier → lapor exact-match %.
  2. **Spot-check manusia** — sampel K grounded + K ungrounded dari output model asli, manusia konfirmasi label bener → lapor agreement %.
- **Catatan:** F1-04 (done) cuma bukti **internal** (verifier cocok Lampiran B/D + tolerance sweep) — BUKAN cross-check independen.
- **Owner:** Track A (#5). **Status:** open — mulai duluan (murah, no GPU).

## C4 — test benchmark skala + generalisasi lapangan  [#4]
- **Concern:** 18 test item kekecilan buat klaim generalisasi lapangan.
- **Cara verifikasi/atasi:** skala ke 100–300 item **real**, verifier-clean, stratified (tugas × kesulitan), anti-bocor (sumber test ≠ train).
  - Termurah: +30–50 indikator WB-IDN + banyak pertanyaan per series (tren/segmen/anomali/penjelasan di window beda).
  - Lebih kuat: +≥1 sumber Indonesia frekuensi tinggi (PIHPS harga pangan harian / BMKG) walau sedikit.
- **Owner:** F4-03 + regen `curate_benchmark_uji.py`. **Status:** open.

---

## Keputusan tercatat
- **D1 (2026-07-16):** framework fine-tune = **Unsloth** (bukan LLaMA-Factory). Tetap QLoRA NF4 4-bit, Qwen2.5-7B-Instruct. F5-01 direframe; butuh converter gearts JSONL → format chat Unsloth. ADR menyusul saat F5-01 di-grill.
