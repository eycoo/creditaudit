"""Experiment 1 — baseline hallucination test (RQ1). F3-02.

Runs stock model(s) (Qwen2.5-7B-Instruct, no fine-tune) through the harness on the
acuan benchmark and writes a `model × (accuracy, grounding, tokens)` table. The
expected story (brief v2 §5, Exp 1): decent accuracy but **low grounding** — right
answers, unauditable reasoning. That gap is the RQ1 evidence.

Offline-testable: `run()` takes adapters + samples and touches no GPU; only
`main()` constructs the real vLLM adapter. Run on Kaggle — see README-kaggle.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "experiments"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _report import load_benchmark, write_csv, write_markdown_table  # noqa: E402
from gearts.harness import metrics_table, run_model  # noqa: E402

COLUMNS = ["model", "n", "answer_accuracy", "mean_grounding", "mean_tokens"]
OUTDIR_DEFAULT = _ROOT / "experiments" / "rq1"


def run(adapters, samples, outdir: str | Path = OUTDIR_DEFAULT) -> list[dict]:
    """Run each adapter over `samples`; write the RQ1 table. Returns the rows."""
    outdir = Path(outdir)
    results = [run_model(a, samples) for a in adapters]
    rows = metrics_table(results)
    write_csv(outdir / "tabel_rq1.csv", rows, COLUMNS)
    write_markdown_table(outdir / "tabel_rq1.md", rows, COLUMNS,
                         "RQ1 — akurasi vs grounding (tanpa fine-tune)")
    return rows


def main() -> int:  # pragma: no cover - needs GPU/vLLM
    from _kaggle_env import vllm_overrides

    from gearts.adapters.qwen_vllm import QwenVLLMAdapter

    ov = vllm_overrides()  # TP / AWQ / mem knobs from env (see README-kaggle.md)
    samples = load_benchmark()
    adapters = [QwenVLLMAdapter(mode="panjang", **ov)]
    rows = run(adapters, samples)
    for r in rows:
        print(r)
    print(f"\nDitulis ke {OUTDIR_DEFAULT}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
