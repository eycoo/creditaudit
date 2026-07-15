# ADR-0003: Finalize operation semantics + grounding tolerance

**Status:** Accepted (2026-07-15) — user accepted all five recommendations as written (Item 1: A, Item 2: A,
Item 3: C, Item 4: A, Item 5: C) with no amendments. `CONTEXT.md` updated same day. Code/test lock tracked as
a separate follow-up issue (`.scratch/fase-1-fondasi/issues/06-lock-operasi-semantik.md`, `ready-for-agent`,
`medium`) — this ADR fixes the *decision*, not the code.

## Context

The operation library (`src/gearts/operations.py`, brief Lampiran C) and verifier (`src/gearts/verifier.py`)
are implemented, but five semantics are provisional (`# ponytail` markers in code). They must be pinned
**before** large-scale reasoning synthesis (F4-04), because the same computation produces the dataset's
ground-truth labels *and* the evaluation grounding score (ADR-0002) — an unpinned rule poisons train and
test at once. Nothing here moves arithmetic into the model; the verifier still owns all recomputation
(ADR-0002 respected).

This ADR does **not** edit `operations.py`, `verifier.py`, or the canonical brief. It records the decision;
a follow-up `medium` issue applies it after sign-off (see end).

---

## Item 1 — `deteksi_anomali`: population window, sidedness, `hasil` form

Current: `|z| > ambang` over the **whole series**, two-sided, returns `list[int]` of indices. Non-scalar →
excluded from the grounding score today (`grounded=None`).

| Option | Semantics | Trade-off |
|---|---|---|
| **A (recommended)** | Whole-series population, **two-sided** `|z|>ambang`, `hasil` = **sorted 0-based index list** into `nilai` | Matches current code; deterministic; simplest. **Anti-conservative on trending series** — a strong trend inflates std and can hide late spikes or flag early points. |
| B | **Rolling/baseline-window** population (trailing window of size `w`), **one-sided** (upward only) | Measurement-valid for outbreak detection; but adds a `w` knob → more label ambiguity and a harder-to-specify contract. |
| C | Return a **count** (scalar) instead of indices | Keeps grounding scalar (no F1-05 needed), but loses *which* points — downstream "minggu mana yang anomali?" questions can't be answered, and a count can match by coincidence. |

**Recommendation: A.** Keep whole-series, two-sided, index-list. Direction (upward-only) is expressed by the
*question framing*, not baked into the primitive; the primitive stays general. Reject C — locations are
information the tasks need (§6 anomaly/outbreak). Note B as a future per-question variant if trend-dilution
proves to hurt synthesis quality (draft issue below), **not** the default.

**Grounding of the index list is delegated to F1-05** (non-scalar grounding via index-set / Jaccard). This
ADR only fixes the *semantics that produce* the list; F1-05 fixes how a claimed list is scored. Recommended
target for F1-05: **exact set equality** at synthesis-cleaning time (strict — drop steps that don't match),
report **Jaccard** at eval time.

## Item 2 — `bandingkan_segmen`: difference vs ratio vs percent, scalar vs struct

Current: `mean(r2) − mean(r1)`, scalar.

| Option | Semantics | Trade-off |
|---|---|---|
| **A (recommended)** | Keep **absolute difference of means**, scalar | Minimal, deterministic. **Unit-dependent** (not comparable across series), but within one sample that is fine, and percent/ratio are expressed by **composition** (Item 4): `rata2` each segment → `persen_naik`/`rasio` on the two `langkah{N}` bindings. Avoids a second non-scalar op. |
| B | **Percent change of means**: `(mean(r2)−mean(r1))/mean(r1)·100` | Scale-free, decision-relevant ("naik berapa persen"), but duplicates `persen_naik` semantics on segment means and needs a `mean(r1)≠0` guard baked in. |
| C | Return a **struct** `{selisih, persen, rasio}` | Richest, but non-scalar → same grounding complication as Item 1 for marginal gain. |

**Recommendation: A.** One primitive, one meaning; percent and ratio come from composition, keeping the
library orthogonal (no two ops computing the same thing). Trade-off accepted: cross-series comparability is
not this primitive's job. B is the main alternative if synthesis finds the compose-for-percent pattern too
verbose.

## Item 3 — `z_score` population: whole series vs baseline window; `ddof`

Current: whole series, `ddof=0` (population std). The verifier already supports an explicit population arg
(`z_score(x, nilai[0:8])`) and defaults to the full series when omitted (`NEEDS_POPULATION`).

| Option | Population | Trade-off |
|---|---|---|
| A | Always whole series | Simple, but **over-dilutes on trends** (same failure mode as Item 1 B). |
| B | Always a fixed baseline window (e.g. first *k*) | Valid on trends, but hard-codes a window that isn't always the right baseline. |
| **C (recommended)** | **Explicit population argument; default = whole series when omitted** | Already implemented. Puts the choice in the reasoning author's hands; synthesis **should** pass an explicit baseline window when the series trends. Slightly more burden on synthesis, but yields valid z. |

**Recommendation: C**, and **fix `ddof=0` (population std)** so `z_score` and `deteksi_anomali` agree
numerically (`deteksi_anomali` uses `np.std` ddof=0). Document `ddof=0` as a deliberate determinism choice,
not sample std. Guideline for synthesis: **pass an explicit baseline population on trending series**; whole
series only when the series is roughly stationary.

## Item 4 — Composite operations: how steps reference prior results

Current: the verifier binds `langkah{N} = <scalar result of step N>` and resolves the token `langkahN` from
those bindings. Only **scalar** steps create a binding. The brief's Lampiran C shows `rasio(nilai[15], baseline)`
— but `baseline` is a free identifier the verifier **cannot** resolve today.

| Option | Convention | Trade-off |
|---|---|---|
| **A (recommended)** | **`langkah{N}` references only.** A composite step cites a prior scalar result as `langkah{N}` (N = that step's `langkah` index), e.g. `rasio(nilai[15], langkah1)`. No free names. | Implemented, deterministic, no schema change. Less readable than `baseline` — but readability lives in the `teks` gloss, not the operation string. |
| B | **Named bindings** — a step declares an alias (schema field) the verifier resolves | Readable, but adds schema surface and a name-collision resolution rule for marginal gain. |
| C | Both A and B | Two ways to do one thing → inconsistent labels. |

**Recommendation: A.** Standardize on `langkah{N}` only; the `rasio(nilai[15], baseline)` example in Lampiran C
is illustrative and should be read as `rasio(nilai[15], langkah1)` in real samples. Two rules to make explicit:
(1) **only scalar steps are bindable** (a `deteksi_anomali` index list is not a valid argument); (2) a step
may only reference `langkah{N}` for **N < its own index**. B is a future issue if synthesis finds `langkah{N}`
too brittle.

## Item 5 — Grounding tolerance: global vs per-operation

Current: `grounded ⇔ |expected − claimed| ≤ max(abs_tol, rel_tol·|expected|)`, defaults `abs_tol=rel_tol=0.01`,
global (one pair for all ops).

| Option | Design | Trade-off |
|---|---|---|
| A | Keep global `0.01 / 0.01` as-is | Zero work; already separates honest rounding from magnitude errors on Lampiran B. |
| B | **Per-operation** tolerances (looser for `slope`/`z_score`, tighter for `delta`/`rasio`) | Finer control, but adds config surface and a per-op justification burden; easy to over-fit. |
| **C (recommended)** | Keep the **form** and the **single global knob** (structurally A), but **set the numbers from the F1-04 sweep** rather than by guess | Data-driven; preserves simplicity. Costs one dependency on F1-04. |

**Recommendation: C.** Keep `max(abs_tol, rel_tol·|expected|)` and one global `(abs_tol, rel_tol)` pair.
Confirm the numeric defaults against **F1-04's sensitivity sweep** before locking. The constraint the sweep
must preserve (from the existing Lampiran B / Lampiran D pair):

- honest `105.3` vs recomputed `105.26` **must ground** → needs `rel_tol ≳ 0.0004` **or** `abs_tol ≳ 0.04`;
- hallucinated `30` vs recomputed `105.26` **must fail** → needs the tolerance well below `≈0.71` relative.

The safe band is wide, so `0.01 / 0.01` sits comfortably inside — **recommend confirming `0.01 / 0.01`** unless
F1-04 surfaces an operation whose honest presentation rounding exceeds that band. Reject per-operation
tolerances (B) unless the sweep proves a single global pair cannot separate honest from hallucinated across
ops.

**F1-04 sweep result (`docs/lab-notebook/2026-07-15-tolerance-sweep.md`), confirms this:** full grid
`abs_tol × rel_tol ∈ {0, 0.001, 0.01, 0.05, 0.1}²` on the Lampiran B / D pair — the hallucination (`30` vs
recomputed `105.26`) is caught at all 25 points; the honest sample fails only where `rel_tol=0` **and**
`abs_tol<0.05` (presentation rounding `105.3` vs `105.26`, gap `≈0.037`, needs `rel_tol>0` to cover cheaply).
`0.01/0.01` sits inside the safe region with ~2000× margin between the two failure thresholds. **Confirmed as
the accepted default.**

---

## Consequences

- Library stays **orthogonal**: `bandingkan_segmen` = mean difference, percent/ratio via composition; no two
  ops compute the same number.
- `deteksi_anomali` and `z_score` share `ddof=0` and whole-series-by-default population, with an explicit
  baseline window recommended for trending series. Their **grounding** (non-scalar for `deteksi_anomali`) is
  F1-05's contract.
- Composition is `langkah{N}`-only; scalar-only bindings; forward references forbidden.
- Grounding tolerance keeps its single-knob form; numbers confirmed by F1-04, provisionally `0.01 / 0.01`.

## Follow-up issues

1. **F1-06 (filed) — Lock finalized operation semantics in code + tests**
   (`.scratch/fase-1-fondasi/issues/06-lock-operasi-semantik.md`, `ready-for-agent`, `medium`). Remove
   `# ponytail` markers in `operations.py`; add docstrings pinning: `bandingkan_segmen` = mean difference
   (scalar); `z_score`/`deteksi_anomali` `ddof=0`, explicit-population arg, whole-series default;
   `deteksi_anomali` two-sided index list. Add tests: `z_score` with explicit baseline window;
   `bandingkan_segmen` sign convention (`mean(r2)−mean(r1)`); a composite `langkah{N}` chain; forward-reference
   / non-scalar-arg rejection. Acceptance: `pytest` green, no `# ponytail` left in `operations.py`.
2. **F1-05 (exists, now `ready-for-agent`) — non-scalar grounding for `deteksi_anomali`** via index-set
   equality (clean) / Jaccard (eval). This ADR fixes the semantics that produce the index list; F1-05 scores
   it.
3. **`medium` (optional, deferred, not filed) — rolling/baseline-window variant** of `deteksi_anomali` and a
   `bandingkan_segmen` percent mode, **only if** synthesis shows whole-series dilution or compose-for-percent
   verbosity hurts label quality. Not needed for the first dataset.

## Resolution

User accepted all recommendations as-is (2026-07-15), no amendments. No open questions remain.
