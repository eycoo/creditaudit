"""Converter gearts JSONL -> format chat Unsloth/HF (F4-05, keputusan D1).

gearts `Sample` bukan format yang bisa langsung dilatih Unsloth. Skrip ini
membangun pasangan chat per sampel:

- system    = instruksi penalar (adapter `_SYSTEM`)
- user      = `build_prompt(sample)` — prompt yang sama dipakai saat eval (RQ1/RQ2)
- assistant = reasoning gold di-serialize persis format `LANGKAH <n>: <op> = <hasil> | <teks>`
              lalu `JAWABAN: <label>` — format yang di-parse `parse_model_output`.

Model teladan = Qwen2.5-7B-Instruct (mendukung role system). Keluaran:
- data/train_unsloth.jsonl   (satu {"messages": [...]} per baris)
- data/dataset_info.json     (deskripsi untuk loader)

Jalankan: python scripts/to_unsloth.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from gearts.adapters.qwen_vllm import _SYSTEM, build_prompt  # noqa: E402
from gearts.schema import read_jsonl  # noqa: E402


def _fmt(h: float) -> str:
    """Angka -> string ringkas yang cocok dgn _STEP_RE (mis. 13.0, -2.5, 105.263)."""
    v = round(float(h), 3)
    return str(int(v)) if v == int(v) else str(v)


def serialize_reasoning(sample) -> str:
    lines = [f"LANGKAH {s.langkah}: {s.operasi} = {_fmt(s.hasil)} | {s.teks}"
             for s in sample.reasoning]
    lines.append(f"JAWABAN: {sample.jawaban.label}")
    return "\n".join(lines)


def to_messages(sample) -> dict:
    return {"messages": [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": build_prompt(sample)},
        {"role": "assistant", "content": serialize_reasoning(sample)},
    ]}


def main() -> int:
    src = _ROOT / "data" / "synthetic" / "train_acuan.jsonl"
    out = _ROOT / "data" / "train_unsloth.jsonl"
    info = _ROOT / "data" / "dataset_info.json"
    if not src.exists():
        print(f"GAGAL: {src} tak ada (jalankan scripts/synthesize_train.py dulu).", file=sys.stderr)
        return 1

    samples = read_jsonl(src)
    with open(out, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(to_messages(s), ensure_ascii=False) + "\n")

    info.write_text(json.dumps({
        "gearts_train": {
            "file_name": "train_unsloth.jsonl",
            "formatting": "sharegpt",
            "columns": {"messages": "messages"},
            "tags": {"role_tag": "role", "content_tag": "content",
                     "user_tag": "user", "assistant_tag": "assistant", "system_tag": "system"},
        }
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: {len(samples)} baris -> {out}")
    print(f"    dataset_info -> {info}")
    # tunjukkan satu contoh assistant target
    print("\n--- contoh target assistant (sampel 0) ---")
    print(to_messages(samples[0])["messages"][-1]["content"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
