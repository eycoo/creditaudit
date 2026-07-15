"""Grounding-tolerance sensitivity sweep (F1-04).

Reuses the LAMPIRAN_B fixture from tests/test_verifier.py (no new data). Grid-sweeps
abs_tol x rel_tol over {0, 0.001, 0.01, 0.05, 0.1} and records verify_sample's
grounding_score for both the honest sample and its Lampiran D hallucinated variant
(step 2 claims 30 where the series actually rose ~105.26%).

Read-only w.r.t. src/: imports gearts.verifier / gearts.schema, never edits them.
Run: python experiments/tolerance-sweep/sweep.py
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from gearts.schema import Sample  # noqa: E402
from gearts.verifier import verify_sample  # noqa: E402
from test_verifier import LAMPIRAN_B  # noqa: E402

GRID = [0, 0.001, 0.01, 0.05, 0.1]

HALLUCINATED = copy.deepcopy(LAMPIRAN_B)
HALLUCINATED["reasoning"][1]["hasil"] = 30.0  # Lampiran D: "salah besaran"

honest_sample = Sample.from_dict(LAMPIRAN_B)
hallucinated_sample = Sample.from_dict(HALLUCINATED)


def run_grid():
    rows = []
    for abs_tol in GRID:
        for rel_tol in GRID:
            honest = verify_sample(honest_sample, abs_tol=abs_tol, rel_tol=rel_tol)
            bad = verify_sample(hallucinated_sample, abs_tol=abs_tol, rel_tol=rel_tol)
            rows.append({
                "abs_tol": abs_tol,
                "rel_tol": rel_tol,
                "honest_score": honest["grounding_score"],
                "hallucinated_score": bad["grounding_score"],
                "step2_grounded_honest": honest["steps"][1]["grounded"],
                "step2_grounded_bad": bad["steps"][1]["grounded"],
            })
    return rows


def print_table(rows):
    header = f"{'abs_tol':>8} {'rel_tol':>8} {'honest%':>9} {'halluc%':>9} {'step2_honest':>13} {'step2_bad':>10}"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r['abs_tol']:>8} {r['rel_tol']:>8} {r['honest_score']:>9.1f} "
              f"{r['hallucinated_score']:>9.1f} {str(r['step2_grounded_honest']):>13} "
              f"{str(r['step2_grounded_bad']):>10}")


if __name__ == "__main__":
    rows = run_grid()
    print_table(rows)

    honest_always_100 = all(r["honest_score"] == 100.0 for r in rows)
    # abs_tol=0.1 alone already exceeds |30-105.26|=75.26? no: check hallucination
    # is caught (score < 100, i.e. step2 not grounded) at every grid point.
    halluc_never_masked = all(r["step2_grounded_bad"] is False for r in rows)

    print()
    print(f"honest always 100%: {honest_always_100}")
    print(f"hallucination (30 vs 105.26) caught at every grid point: {halluc_never_masked}")
