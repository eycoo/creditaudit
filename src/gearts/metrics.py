"""Evaluation metrics (project_brief.md §14).

Three metrics, all deterministic: answer accuracy, grounding score (main), and
token efficiency. No LLM judge — grounding is computed by the verifier.
"""
from __future__ import annotations

from gearts.schema import Sample
from gearts.verifier import verify_sample


def answer_accuracy(preds: list[str], golds: list[str]) -> float:
    """Percent of samples whose predicted final label matches the gold label."""
    if not golds:
        return 0.0
    hits = sum(p == g for p, g in zip(preds, golds))
    return 100.0 * hits / len(golds)


def dataset_grounding(samples: list[Sample], **tol) -> float:
    """Mean grounding score over samples (percent of steps that survive recompute)."""
    if not samples:
        return 0.0
    return sum(verify_sample(s, **tol)["grounding_score"] for s in samples) / len(samples)


def count_reasoning_tokens(sample: Sample) -> int:
    """Cheap proxy for reasoning length.

    # ponytail: whitespace count; swap for the model tokenizer at real eval time.
    """
    return sum(len((step.operasi + " " + step.teks).split()) for step in sample.reasoning)
