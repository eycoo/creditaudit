# Train/test split + stratify + anti-leakage

Status: done (on `track-d`, pending PM merge to master) — 2026-07-17, Sesi D
Difficulty: medium
Depends: F4-04 (done, track-d)

## Spec

Split into **train** (mostly semi-synthetic) and **test** (mostly real), stratified by task + difficulty,
with anti-leakage: no test source appears in train (brief §9.4). The Fase-2 benchmark is the real test core.

## Acceptance (finalize at grill time)

- Target: split manifest; leakage check passes (data-qa); distribution tables.

## Resolusi (Sesi D, 2026-07-17)

Split terwujud sebagai dua file terpisah (bukan repartition): **train** =
`data/synthetic/train_acuan.jsonl` (336, semi-sintetik F4-04), **test** =
`data/processed/benchmark_acuan.jsonl` (18, deret REAL World Bank; = benchmark_uji
tanpa reasoning, acuan dipakai karena ter-commit & series identik).

**Deliverable:**
- `scripts/split_dataset.py` — stratifikasi (tugas × kesulitan) kedua sisi + cek anti-bocor.
- `data/manifest_split.md` — tabel distribusi + laporan anti-bocor.
- `scripts/to_unsloth.py` — converter gearts→chat Unsloth (keputusan **D1**);
  user=`build_prompt(mode="pendek")`, assistant=reasoning gold (grammar LANGKAH/JAWABAN).
- `data/train_unsloth.jsonl` (336 percakapan) + `data/dataset_info.json` (sharegpt).
- `tests/test_to_unsloth.py` — round-trip converter→parser (langkah+label identik).

**Anti-bocor LOLOS:** id disjoint (`train_*`/`uji_*`), **0 tabrakan numerik** train vs
18 deret uji, sumber beda (sintetik vs WB), nama indikator train **disjoint** dari
18 nama uji (profil F4-04 di-rename agar 0 tumpang-tindih optik). `pytest` 105 passed.

## Comments
