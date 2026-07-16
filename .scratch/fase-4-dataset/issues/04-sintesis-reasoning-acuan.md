# Large-scale reasoning synthesis + auto-verify

Status: done (on `track-d`, pending PM merge to master) — 2026-07-16, Sesi D
Difficulty: hard
Depends: F1-01 (done). F4-03 di-*decouple* untuk train (lihat Comments + ADR-0004).

## Spec

Automate synthesis of **shortest-grounded reference reasoning** over the scraped series at scale, with the
verifier **in the loop**: steps that don't ground are fixed or dropped, so labels are clean by construction
(brief v2 §4.3). Attach difficulty + task-type labels. This is a design task — expand via `/grill-me`
(→ `researcher`, likely an ADR on the synthesis policy).

## Acceptance (finalize at grill time)

- Target: every sample verifies at 100% grounding; distribution stratified by task + difficulty.

## Resolusi (Sesi D, 2026-07-16)

Karena F4-03 (scrape penuh) ditunda dan `data/raw/` WB = sumber **uji**, train dibangkitkan sebagai
deret **sintetis-terkendali** (brief v2 §4.3 membolehkan train terkendali), lepas total dari sumber uji.
Keputusan lengkap di **`docs/adr/0004-train-synthesis-policy.md`**.

**Deliverable:**
- `scripts/synthesize_train_acuan.py` — pembangkit; verifier **in the loop** (drop/retry sampel tak-grounded).
- `data/synthetic/train_acuan.jsonl` — **336 sampel, semua `grounding_score = 100.0`** (di-force-add;
  `data/synthetic/*` gitignored).
- `data/manifest_train_acuan.md` — tabel distribusi (12 strata tugas × kesulitan seimbang @28; label; panjang
  rantai; domain).
- `tests/test_synthesize_train_acuan.py` — 100% grounded, strata, prasyarat kesulitan, anti-bocor, determinisme.
- ADR-0004.

**Bukti acceptance:** tiap sampel `verify_sample == 100.0` (di-assert di pipeline & test); strata 4×3×28=336;
anti-bocor 18 deret uji dibandingkan → **0 tabrakan**; `pytest` 101 passed (di worktree gems-D).

**Sisa (bukan blocker fine-tune):** adaptivitas panjang rantai penuh (§4.2) & split formal train/test = **F4-05**.

## Comments
