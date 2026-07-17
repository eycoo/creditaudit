"""Methods + runner for RQ3 (our method vs baselines) and RQ4 (ablation). F5-03/04.

RQ3/RQ4 compare *approaches*, not just base models, so each "method" is a
`ModelAdapter` and the headline is **grounding-per-token**. Two things differ from
RQ1/RQ2:

- **Tokens are counted from the model's RAW output** (whitespace words), not from
  the parsed operation steps. RQ3 includes a FREE-PROSE method whose output has no
  parseable steps at all; a step-based count would score it as "free" (0 tokens),
  which is absurd. Raw-output length is the honest cost and is fair across prose
  and operation form alike. (Offline/mock adapters with no `last_raw` fall back to
  the step-based proxy so the harness stays testable without a GPU.)
- **B4 (pure statistics)** runs no model: it computes the answer deterministically
  from the series and emits **no** reasoning — 0 tokens, 0 grounding. It is the
  compute-only floor: it can answer, but offers nothing auditable.

Method line-ups (brief v2 §5, Experiments 3 & 4):

  RQ3  B1-prosa      base  · free prose, no operations        → ~0 grounding
       B2-veritime   base  · operation form, verbose          → grounded but costly
       B3-selfbudget base  · operation form, brief            → cheap, less grounded
       B4-statistik  —     · pure compute, no reasoning       → answers only
       Kami          LoRA  · operation form, shortest-grounded→ best grounding/token

  RQ4  Kami-penuh    LoRA  · operation + shortest-grounded (full method)
       −finetune     base  · same prompt, no fine-tune
       −format_operasi LoRA· free prose instead of operations
       −target_terpendek LoRA · verbose (drop the shortest-grounded objective)
       −adaptif      LoRA  · fixed 1-step budget (drop per-task length adaptation)

Everything is GPU-free at import; the vLLM adapters load lazily on first predict.
"""
from __future__ import annotations

import os

import numpy as np

from gearts.adapters.qwen_vllm import QwenVLLMAdapter
from gearts.metrics import count_reasoning_tokens
from gearts.schema import Jawaban, ReasoningStep, Sample
from gearts.verifier import verify_sample

# Default fine-tuned adapter location (override with GEARTS_LORA_PATH). This is
# where the F5-02 run saves the LoRA; upload that folder to the GPU box.
LORA_PATH_DEFAULT = os.environ.get("GEARTS_LORA_PATH", "notebooks/lora_qwen_penalaran_ts")


# --- task inference + the pure-statistics answer (B4) -----------------------

def task_of(sample: Sample) -> str:
    """Infer task from the templated question (mirrors qwen_vllm.answer_options).

    # ponytail: infer from question text; move to an explicit `task` field when the
    # benchmark is regenerated.
    """
    q = sample.pertanyaan.lower()
    if "paruh awal" in q or "paruh akhir" in q:
        return "segmen"
    if "menyimpang" in q or "anomali" in q:
        return "anomali"
    if "pola utama" in q or "arah dan besar" in q:
        return "penjelasan"
    return "tren"  # "kecenderungan"/"tren", and the default


def stat_answer(sample: Sample) -> str:
    """Deterministic label from the series via the operation formulas — no LLM.

    The same statistics the gold reasoning uses (slope sign, segment-mean diff,
    max |z|, end-to-end percent), with the synthesize thresholds (5% stable band,
    |z|>3 anomaly, 20% "besar"). Anomaly uses the whole series as the population —
    a naive choice that can miss a trend-diluted outlier, which is exactly the
    honest limitation of a compute-only baseline.
    """
    v = np.asarray(sample.series.nilai, dtype=float)
    n = len(v)
    task = task_of(sample)
    mean = float(np.mean(v)) if n else 0.0

    if task == "tren":
        slope = float(np.polyfit(np.arange(n), v, 1)[0])
        frac = abs(slope * (n - 1)) / abs(mean) if mean else 0.0
        if frac < 0.05:
            return "relatif_stabil"
        return "meningkat" if slope > 0 else "menurun"

    if task == "segmen":
        h = n // 2
        diff = float(np.mean(v[h:]) - np.mean(v[:h]))
        first = float(np.mean(v[:h])) if h else 0.0
        frac = abs(diff) / abs(first) if first else 0.0
        if frac < 0.05:
            return "setara"
        return "paruh_akhir_lebih_tinggi" if diff > 0 else "paruh_awal_lebih_tinggi"

    if task == "anomali":
        sd = float(np.std(v))
        if sd == 0:
            return "tidak_ada_anomali"
        z = np.abs((v - mean) / sd)
        return "ada_anomali" if float(np.max(z)) > 3 else "tidak_ada_anomali"

    # penjelasan: direction (slope) + magnitude class (end-to-end percent)
    slope = float(np.polyfit(np.arange(n), v, 1)[0])
    pct = float((v[-1] - v[0]) / v[0] * 100) if v[0] != 0 else 0.0
    if (slope > 0) != (pct > 0):
        return "tidak_monoton"
    arah = "naik" if slope > 0 else "turun"
    besar = "besar" if abs(pct) >= 20 else "kecil"
    return f"{arah}_{besar}"


class StatBaselineAdapter:
    """B4 — pure statistics: deterministic label from the series, **no** reasoning.

    A `ModelAdapter` that emits zero reasoning steps (grounding 0, tokens 0) and a
    computed answer. The compute-only floor for the grounding-per-token table.
    """

    def __init__(self, name: str = "B4-statistik"):
        self.name = name
        self.last_raw = ""  # no model output → runner counts 0 tokens

    def predict(self, sample: Sample):
        return [], stat_answer(sample)


# --- runner: one row per method, with grounding-per-token -------------------

def _as_step(s) -> ReasoningStep:
    return s if isinstance(s, ReasoningStep) else ReasoningStep(**s)


def _rebuild(sample: Sample, steps: list, answer: str) -> Sample:
    """Rebuild the item with the model's reasoning + answer over the ORIGINAL
    series (the model never owns the numbers — ADR-0001)."""
    return Sample(
        id=sample.id, series=sample.series, konteks=sample.konteks,
        pertanyaan=sample.pertanyaan, reasoning=[_as_step(s) for s in steps],
        jawaban=Jawaban(label=answer, keyakinan="sedang"),
    )


def _output_tokens(adapter, pred: Sample) -> int:
    """Honest reasoning length: raw model output words when available (fair to
    free prose), else the step-based proxy (offline/mock adapters, compute-only)."""
    raw = getattr(adapter, "last_raw", "") or ""
    if raw.strip():
        return len(raw.split())
    return count_reasoning_tokens(pred)


def grounding_per_token(mean_grounding: float, mean_tokens: float):
    """Headline metric: grounded reasoning per token spent. None when no tokens
    were emitted (the compute-only baseline), so the ratio isn't a fake 0/0."""
    return (mean_grounding / mean_tokens) if mean_tokens > 0 else None


def run_methods(methods, samples, label_key: str = "method", **tol) -> list[dict]:
    """Run each ``(label, adapter)`` over the benchmark; one aggregate row per
    method: accuracy, grounding, tokens, grounding-per-token. Offline-testable —
    no GPU is touched here (the adapters own that). ``tol`` forwards to the verifier.
    """
    n = len(samples)
    rows: list[dict] = []
    for label, adapter in methods:
        hits = grounds = toks = 0.0
        for s in samples:
            steps, answer = adapter.predict(s)
            pred = _rebuild(s, steps, answer)
            grounds += verify_sample(pred, **tol)["grounding_score"]
            toks += _output_tokens(adapter, pred)
            hits += 1.0 if answer == s.jawaban.label else 0.0
        mg = grounds / n if n else 0.0
        mt = toks / n if n else 0.0
        rows.append({
            label_key: label,
            "n": n,
            "answer_accuracy": 100.0 * hits / n if n else 0.0,
            "mean_grounding": mg,
            "mean_tokens": mt,
            "grounding_per_token": grounding_per_token(mg, mt),
        })
    return rows


# --- engine kwargs + method line-ups ----------------------------------------

def lora_engine_kwargs(overrides: dict) -> dict:
    """Add the flags a LoRA engine needs (``enable_lora`` + max rank ≥ our r=32) to
    the auto-detected vLLM overrides, and pass the SAME dict to every method so the
    base-model and LoRA methods share ONE loaded engine (the LoRA is per request)."""
    kw = dict(overrides)
    kw["enable_lora"] = True
    kw["max_lora_rank"] = max(32, int(kw.get("max_lora_rank", 0)))
    return kw


def rq3_methods(base_model: str | None = None, lora_path: str | None = None, **vllm_kwargs):
    """The five RQ3 methods as ``(label, adapter)``. ``vllm_kwargs`` (from
    ``lora_engine_kwargs(vllm_overrides())``) is shared so base + LoRA share an engine."""
    lora_path = lora_path or LORA_PATH_DEFAULT
    if base_model:
        vllm_kwargs["model"] = base_model
    return [
        ("B1-prosa", QwenVLLMAdapter(name="B1-prosa", prompt_style="prosa", mode="panjang", **vllm_kwargs)),
        ("B2-veritime", QwenVLLMAdapter(name="B2-veritime", mode="panjang", **vllm_kwargs)),
        ("B3-selfbudget", QwenVLLMAdapter(name="B3-selfbudget", mode="pendek", **vllm_kwargs)),
        ("B4-statistik", StatBaselineAdapter()),
        ("Kami", QwenVLLMAdapter(name="Kami", mode="pendek", lora_path=lora_path, **vllm_kwargs)),
    ]


def rq4_variants(base_model: str | None = None, lora_path: str | None = None, **vllm_kwargs):
    """The full method + four ablations as ``(label, adapter)`` — each turns off one
    component (fine-tune, operation format, shortest-grounded objective, adaptivity)."""
    lora_path = lora_path or LORA_PATH_DEFAULT
    if base_model:
        vllm_kwargs["model"] = base_model
    return [
        ("Kami-penuh", QwenVLLMAdapter(name="Kami-penuh", mode="pendek", lora_path=lora_path, **vllm_kwargs)),
        ("-finetune", QwenVLLMAdapter(name="-finetune", mode="pendek", **vllm_kwargs)),
        ("-format_operasi", QwenVLLMAdapter(name="-format_operasi", prompt_style="prosa", mode="pendek", lora_path=lora_path, **vllm_kwargs)),
        ("-target_terpendek", QwenVLLMAdapter(name="-target_terpendek", mode="panjang", lora_path=lora_path, **vllm_kwargs)),
        ("-adaptif", QwenVLLMAdapter(name="-adaptif", mode="pendek", max_steps=1, lora_path=lora_path, **vllm_kwargs)),
    ]
