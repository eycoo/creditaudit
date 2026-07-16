"""Diagnostic: print the RAW model output next to what the parser/verifier see.

RQ1/RQ2 metrics were near zero and we were flying blind — the harness discards the
model's raw text. This dumps, for a few benchmark items: the exact prompt-driven
output, the parsed steps, the parsed+snapped label, and the gold label. That tells
us *why* grounding/accuracy is low (format not followed? wrong labels? hallucinated
numbers = the real RQ1 story?) before changing anything else.

Run on Kaggle after the model is available:
    python experiments/debug_dump.py            # first 4 items
    python experiments/debug_dump.py 8           # first 8 items
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "experiments"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _report import load_benchmark  # noqa: E402


def main(n: int = 4) -> int:  # pragma: no cover - needs GPU/vLLM
    from _kaggle_env import vllm_overrides

    from gearts.adapters.qwen_vllm import (
        QwenVLLMAdapter,
        answer_options,
        build_prompt,
        parse_model_output,
        snap_label,
    )
    from gearts.verifier import verify_sample
    from gearts.harness import _predicted_sample

    samples = load_benchmark()[:n]
    adapter = QwenVLLMAdapter(mode="panjang", **vllm_overrides())

    for s in samples:
        opsi = answer_options(s)
        raw = adapter._generate(build_prompt(s, mode="panjang", opsi=opsi))
        steps, label = parse_model_output(raw)
        snapped = snap_label(label, opsi)
        report = verify_sample(_predicted_sample(s, steps, snapped))

        print("=" * 72)
        print("ID        :", s.id)
        print("PERTANYAAN:", s.pertanyaan)
        print("OPSI      :", opsi)
        print("GOLD label:", s.jawaban.label)
        print("-" * 8, "RAW MODEL OUTPUT", "-" * 8)
        print(raw.strip())
        print("-" * 8, "PARSED", "-" * 8)
        print(f"label mentah={label!r} -> snapped={snapped!r}  (gold={s.jawaban.label!r}, "
              f"{'BENAR' if snapped == s.jawaban.label else 'SALAH'})")
        print(f"langkah ter-parse: {len(steps)}  | grounding_score: {report['grounding_score']}")
        for st in steps:
            print(f"  LANGKAH {st.langkah}: {st.operasi} = {st.hasil}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 4))
