"""Experiment 2 — grounding-vs-token curve (RQ2, the novelty). F3-03.

Elicits reasoning at several **lengths** (prompt mode + step cap), and at each
length measures grounding, accuracy, and mean reasoning tokens. Emits both the
per-setting curve table and the per-item `(tokens, grounding, accuracy)` records.
Expected finding (brief v2 §5, Exp 2): as reasoning shortens, **grounding falls
faster than accuracy** — the empirical hook for the whole gap. The `researcher`
agent turns these records into the F6-04 finding.

Offline-testable: `run()` takes (label, adapter) settings + samples and touches no
GPU; only `main()` builds the real vLLM adapters. Run on Kaggle — see README-kaggle.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "experiments"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _report import load_benchmark, write_csv, write_markdown_table  # noqa: E402
from gearts.harness import curve_records, run_model  # noqa: E402

CURVE_COLUMNS = ["setting", "mean_tokens", "mean_grounding", "answer_accuracy", "n"]
RECORD_COLUMNS = ["setting", "id", "tokens", "grounding", "accuracy"]
OUTDIR_DEFAULT = _ROOT / "experiments" / "rq2"


def run(settings, samples, outdir: str | Path = OUTDIR_DEFAULT) -> tuple[list[dict], list[dict]]:
    """Run each `(label, adapter)` setting; write curve + per-item records.

    Returns `(curve_rows, record_rows)`. `settings` is an ordered list of
    `(label, adapter)`; label names the reasoning-length point on the curve.
    """
    outdir = Path(outdir)
    curve_rows: list[dict] = []
    record_rows: list[dict] = []

    for label, adapter in settings:
        result = run_model(adapter, samples)
        curve_rows.append({
            "setting": label,
            "mean_tokens": result.mean_tokens,
            "mean_grounding": result.mean_grounding,
            "answer_accuracy": result.answer_accuracy,
            "n": len(result.items),
        })
        for item, (tokens, grounding, acc) in zip(result.items, curve_records(result)):
            record_rows.append({
                "setting": label, "id": item.id,
                "tokens": tokens, "grounding": grounding, "accuracy": acc,
            })

    write_csv(outdir / "kurva_rq2.csv", curve_rows, CURVE_COLUMNS)
    write_csv(outdir / "records_rq2.csv", record_rows, RECORD_COLUMNS)
    write_markdown_table(outdir / "kurva_rq2.md", curve_rows, CURVE_COLUMNS,
                         "RQ2 — grounding & akurasi vs panjang penalaran (token)")
    return curve_rows, record_rows


def main() -> int:  # pragma: no cover - needs GPU/vLLM
    from _kaggle_env import vllm_overrides

    from gearts.adapters.qwen_vllm import QwenVLLMAdapter

    ov = vllm_overrides()  # same model+kwargs across settings → one shared engine (see adapter cache)
    samples = load_benchmark()
    # Titik kurva dari panjang penuh → makin pendek (prompt mode + cap langkah).
    settings = [
        ("panjang", QwenVLLMAdapter(name="panjang", mode="panjang", **ov)),
        ("pendek", QwenVLLMAdapter(name="pendek", mode="pendek", **ov)),
        ("cap-2", QwenVLLMAdapter(name="cap-2", mode="pendek", max_steps=2, **ov)),
        ("cap-1", QwenVLLMAdapter(name="cap-1", mode="pendek", max_steps=1, **ov)),
    ]
    curve_rows, _ = run(settings, samples)
    for r in curve_rows:
        print(r)
    print(f"\nDitulis ke {OUTDIR_DEFAULT}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
