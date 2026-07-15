# 2026-07-15 — Grounding tolerance sensitivity sweep (F1-04)

## Hypothesis

The verifier's grounding tolerance `max(abs_tol, rel_tol·|expected|)` (ADR-0002 default `0.01/0.01`) is not
just a guess: the honest Lampiran B sample should ground at **100%** and the Lampiran D hallucination (step 2
claims `30` where the series actually rose `~105.26%`) should stay caught **across a wide range of settings**
— not only at the exact default. A single global tolerance pair should be able to separate presentation
rounding from a real magnitude error over a broad grid, which is what justifies keeping it a global knob
(brief v2 §4.4 kritik 2b) rather than per-operation.

## Setup

Reused the existing `LAMPIRAN_B` fixture from `tests/test_verifier.py` — no new data. Two samples:
honest (as-is) and hallucinated (`copy.deepcopy` with `reasoning[1].hasil` forced to `30.0`, matching
`test_hallucinated_magnitude_flagged`). Full grid `abs_tol × rel_tol`, `{0, 0.001, 0.01, 0.05, 0.1}` each
(25 combinations), calling `gearts.verifier.verify_sample` directly — no verifier code changed.
Script: `experiments/tolerance-sweep/sweep.py`.

Ground truth for step 2 (`persen_naik(nilai[11]->nilai[15])`): recomputed `= (78−38)/38·100 = 105.263...`;
honest claim `105.3` (presentation rounding, diff `≈0.037`); hallucinated claim `30.0` (diff `≈75.26`).

## Result

Full grid (`honest%` / `halluc%` = `grounding_score`; `step2_honest` / `step2_bad` = step 2's `grounded`):

| abs_tol \ rel_tol | 0 | 0.001 | 0.01 | 0.05 | 0.1 |
|---|---|---|---|---|---|
| **0** | 66.7 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 |
| **0.001** | 66.7 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 |
| **0.01** | 66.7 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 |
| **0.05** | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 |
| **0.1** | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 | 100.0 / 66.7 |

(cell = `honest_score / hallucinated_score`; full 25-row detail incl. per-step `grounded` in the script output.)

- **Hallucination caught at all 25 grid points** — `hallucinated_score` is `66.7%` and step 2's `grounded`
  is `False` everywhere, including the loosest setting tested (`abs_tol=0.1, rel_tol=0.1`, i.e. tolerance up
  to `10.5`). Expected: the diff is `≈75.26`, far outside any tested tolerance. Robust.
- **Honest is *not* 100% everywhere** — it drops to `66.7%` at the 9 cells where `rel_tol=0` **and**
  `abs_tol<0.05` (i.e. `abs_tol ∈ {0, 0.001, 0.01}`). At those points the absolute tolerance alone
  (`≤0.01`) is smaller than the presentation-rounding gap (`≈0.037`), so step 2 (`105.3` vs recomputed
  `105.26`) is wrongly flagged as ungrounded. Steps 1 and 3 are exact integer ratios (`13.0`, `6.0`) so they
  ground even at `abs_tol=rel_tol=0`.
- The **default `0.01/0.01`** sits inside the region that scores honest `100%` and hallucinated `66.7%` —
  confirmed safe, and by a comfortable margin (gap between the two failure thresholds spans `0.037` to
  `75.26`, roughly 2000×).
- `pytest`: 20/20 green (no `src/` changes).

## Conclusion

The relative term is **necessary, not decorative**: `abs_tol` alone at the tested granularity (`≤0.01`)
cannot both (a) tolerate `105.3`-style presentation rounding and (b) stay tight enough to be interesting —
you'd need `abs_tol≈0.04+` to cover rounding with `rel_tol=0`, at which point it's a fixed number rather
than scaling with the claim's magnitude. `rel_tol=0.01` alone already covers the rounding gap (`0.01×105.26
≈1.05 > 0.037`) with room to spare before it would risk masking a real error (`75.26` is still `~72×` that
margin). This validates keeping `max(abs_tol, rel_tol·|expected|)` as a **single global knob** rather than
per-operation tolerances (ADR-0003 Item 5, option C) — the default `0.01/0.01` is not an arbitrary choice,
it sits in the middle of a wide safe band on this fixture.

Caveat: this is one fixture (one operation mix, one magnitude regime). It confirms the *default is not
obviously wrong*; it does not prove the band holds for operations with very different typical magnitudes
(e.g. `slope` on near-zero series). That is exactly the residual risk ADR-0003 Item 5 flags before locking
the number for good.

## Next

- Feeds **ADR-0003** (F1-01, Proposed) Item 5 — recommend confirming `abs_tol=rel_tol=0.01` as the accepted
  default; this sweep is the empirical justification the ADR cites.
- Feeds **F6-04** (Hasil section) — this table is the "verifier validation" result the brief v2 §5 asks for.
- If/when F1-05 (non-scalar grounding) lands, repeat a similar sweep for the Jaccard threshold on
  `deteksi_anomali` — untested here (scope was scalar steps only, per the existing fixture).
