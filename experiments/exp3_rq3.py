"""Experiment 3 — our method vs baselines B1–B4 (RQ3). F5-03.

Headline metric: **grounding-per-token**. Writes a `method × (accuracy, grounding,
tokens, grounding-per-token)` table. Expected story (brief v2 §5, Exp 3): the
fine-tuned method ("Kami") holds high grounding at low tokens — the best
grounding-per-token — while free prose (B1) grounds ~0, verbose operations (B2)
pay many tokens, brief stock prompting (B3) sheds grounding, and pure statistics
(B4) answers with nothing auditable.

Offline-testable: `run()` takes `(label, adapter)` methods + samples and touches no
GPU; only `main()` builds the real vLLM/LoRA methods. Run on the GPU box — see
README-kaggle.md. The fine-tuned adapter path comes from `GEARTS_LORA_PATH`.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "experiments"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _report import load_benchmark, write_csv, write_markdown_table  # noqa: E402
from methods import run_methods  # noqa: E402

COLUMNS = ["method", "n", "answer_accuracy", "mean_grounding", "mean_tokens", "grounding_per_token"]
OUTDIR_DEFAULT = _ROOT / "experiments" / "rq3"


def _for_display(rows: list[dict]) -> list[dict]:
    """None grounding-per-token (compute-only B4) → 'NA' for the written tables."""
    return [{**r, "grounding_per_token": "NA" if r["grounding_per_token"] is None
             else r["grounding_per_token"]} for r in rows]


def run(methods, samples, outdir: str | Path = OUTDIR_DEFAULT) -> list[dict]:
    """Run each method over `samples`; write the RQ3 table. Returns the raw rows."""
    outdir = Path(outdir)
    rows = run_methods(methods, samples)
    disp = _for_display(rows)
    write_csv(outdir / "tabel_rq3.csv", disp, COLUMNS)
    write_markdown_table(outdir / "tabel_rq3.md", disp, COLUMNS,
                         "RQ3 — metode kami vs baseline (grounding-per-token)")
    return rows


def main() -> int:  # pragma: no cover - needs GPU/vLLM
    from _kaggle_env import vllm_overrides

    from methods import lora_engine_kwargs, rq3_methods

    ov = lora_engine_kwargs(vllm_overrides())  # base + LoRA share one engine
    samples = load_benchmark()
    rows = run(rq3_methods(**ov), samples)
    for r in rows:
        print(r)
    print(f"\nDitulis ke {OUTDIR_DEFAULT}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
