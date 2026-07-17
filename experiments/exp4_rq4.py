"""Experiment 4 — ablation (RQ4). F5-04.

Starts from the full method ("Kami-penuh") and turns off one component at a time,
measuring the effect on accuracy / grounding / tokens (brief v2 §5, Exp 4):

  −finetune          use the base model (no fine-tune)
  −format_operasi    free prose instead of the operation format
  −target_terpendek  verbose reasoning (drop the shortest-grounded objective)
  −adaptif           fixed 1-step budget (drop per-task length adaptation)

Each row isolates one component's contribution; the gap from "Kami-penuh" is that
component's effect. Same grounding-per-token column as RQ3 for continuity.

Offline-testable: `run()` takes `(label, adapter)` variants + samples and touches no
GPU; only `main()` builds the real vLLM/LoRA variants. Run on the GPU box — see
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

COLUMNS = ["variant", "n", "answer_accuracy", "mean_grounding", "mean_tokens", "grounding_per_token"]
OUTDIR_DEFAULT = _ROOT / "experiments" / "rq4"


def _for_display(rows: list[dict]) -> list[dict]:
    return [{**r, "grounding_per_token": "NA" if r["grounding_per_token"] is None
             else r["grounding_per_token"]} for r in rows]


def run(variants, samples, outdir: str | Path = OUTDIR_DEFAULT) -> list[dict]:
    """Run each ablation variant over `samples`; write the RQ4 table. Returns raw rows."""
    outdir = Path(outdir)
    rows = run_methods(variants, samples, label_key="variant")
    disp = _for_display(rows)
    write_csv(outdir / "tabel_rq4.csv", disp, COLUMNS)
    write_markdown_table(outdir / "tabel_rq4.md", disp, COLUMNS,
                         "RQ4 — ablasi (kontribusi tiap komponen)")
    return rows


def main() -> int:  # pragma: no cover - needs GPU/vLLM
    from _kaggle_env import vllm_overrides

    from methods import lora_engine_kwargs, rq4_variants

    ov = lora_engine_kwargs(vllm_overrides())
    samples = load_benchmark()
    rows = run(rq4_variants(**ov), samples)
    for r in rows:
        print(r)
    print(f"\nDitulis ke {OUTDIR_DEFAULT}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
