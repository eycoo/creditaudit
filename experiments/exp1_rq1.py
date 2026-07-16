"""Experiment 1 — baseline hallucination test (RQ1). F3-02.

Runs stock model(s) (Qwen2.5-7B-Instruct, no fine-tune) through the harness on the
acuan benchmark and writes a `model × (accuracy, grounding, tokens)` table. The
expected story (brief v2 §5, Exp 1): decent accuracy but **low grounding** — right
answers, unauditable reasoning. That gap is the RQ1 evidence.

Offline-testable: `run()` takes adapters + samples and touches no GPU; only
`main()` constructs the real vLLM adapter. Run on Kaggle — see README-kaggle.md.
"""
from __future__ import annotations

import json
import os
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
    from gearts.harness import metrics_table, run_model

    ov = vllm_overrides()  # TP / AWQ / mem knobs from env (see README-kaggle.md)
    samples = load_benchmark()

    # Multi-model mode: run_rq1_multi.py launches one process per roster model,
    # setting GEARTS_MODEL_ID (which model) + GEARTS_ROW_OUT (where to drop its
    # one-row JSON). One process = one model loaded, so the GPU is freed between
    # models — three 7-9B models never sit in VRAM at once.
    model_id = os.environ.get("GEARTS_MODEL_ID")
    row_out = os.environ.get("GEARTS_ROW_OUT")
    if model_id:
        ov.pop("model", None)  # roster model overrides auto-detected (AWQ) model
        name = os.environ.get("GEARTS_MODEL_NAME") or model_id.split("/")[-1]
        adapter = QwenVLLMAdapter(name=name, model=model_id, mode="panjang", **ov)
    else:
        adapter = QwenVLLMAdapter(mode="panjang", **ov)

    if row_out:  # single-model worker: emit just this model's row, no table
        row = metrics_table([run_model(adapter, samples)])[0]
        Path(row_out).parent.mkdir(parents=True, exist_ok=True)
        Path(row_out).write_text(json.dumps(row), encoding="utf-8")
        print("row ->", row_out, row)
        return 0

    rows = run([adapter], samples)  # standalone: one model → full table
    for r in rows:
        print(r)
    print(f"\nDitulis ke {OUTDIR_DEFAULT}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
