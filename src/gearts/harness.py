"""Experiment harness (F3-01) — the pipeline every model experiment runs through.

Flow (ADR-0001 / ADR-0002): a model *adapter* proposes reasoning + answer for
each benchmark item; the deterministic verifier re-executes that reasoning on the
**original** series (the model never owns the numbers); the three metrics are then
computed per model, plus the per-item ``(tokens, grounding, accuracy)`` records the
RQ2 grounding-vs-token curve (F3-03) consumes.

Model access is pluggable: an adapter is anything with a ``name`` and a
``predict(sample) -> (reasoning_steps, answer_label)`` method. ``MockModel`` ships
canned outputs so the harness is fully testable offline; real Qwen2.5-7B / API
adapters are added in F3-02 / F3-03.

Output contract (stable — F6-04 "Hasil" consumes it):
  - ``run_model`` -> ``ModelResult`` with per-item ``ItemResult`` records and the
    three aggregate metrics (``answer_accuracy``, ``mean_grounding``, ``mean_tokens``).
  - ``metrics_table(results)`` -> one dict row per model (the per-model table).
  - ``curve_records(result)`` -> per-item ``(tokens, grounding, accuracy)`` tuples.

This module does **no** series arithmetic itself — it imports the verifier and the
metrics (ADR-0002: all grounded figures come from ``verifier``/``operations``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

from gearts.metrics import answer_accuracy, count_reasoning_tokens
from gearts.schema import Jawaban, ReasoningStep, Sample
from gearts.verifier import verify_sample

# An adapter returns (reasoning_steps, answer_label). Steps may be ReasoningStep
# objects or plain dicts (canned outputs) — normalized before verification.
Prediction = tuple[list, str]


class ModelAdapter(Protocol):
    name: str

    def predict(self, sample: Sample) -> Prediction: ...


@dataclass
class ItemResult:
    """Per-item outcome — the row the RQ2 curve and error analysis key on."""
    id: str
    tokens: int
    grounding: float
    correct: bool
    jawaban_pred: str
    jawaban_gold: str


@dataclass
class ModelResult:
    """Per-model aggregate + the per-item records behind it."""
    model: str
    items: list[ItemResult] = field(default_factory=list)
    answer_accuracy: float = 0.0
    mean_grounding: float = 0.0
    mean_tokens: float = 0.0


class MockModel:
    """Adapter with canned per-id outputs, so the harness runs offline.

    ``table`` maps a sample id to ``(reasoning_steps, answer_label)``. Reasoning
    steps may be dicts or ReasoningStep objects.
    """

    def __init__(self, name: str, table: dict[str, Prediction]):
        self.name = name
        self._table = table

    def predict(self, sample: Sample) -> Prediction:
        if sample.id not in self._table:
            raise KeyError(f"MockModel {self.name!r} has no canned output for {sample.id!r}")
        return self._table[sample.id]


def _as_step(s) -> ReasoningStep:
    return s if isinstance(s, ReasoningStep) else ReasoningStep(**s)


def _predicted_sample(sample: Sample, steps: list, answer: str) -> Sample:
    """Rebuild the item with the model's reasoning + answer over the ORIGINAL series.

    keyakinan is irrelevant to grounding; a valid placeholder keeps the schema happy.
    """
    return Sample(
        id=sample.id,
        series=sample.series,
        konteks=sample.konteks,
        pertanyaan=sample.pertanyaan,
        reasoning=[_as_step(s) for s in steps],
        jawaban=Jawaban(label=answer, keyakinan="sedang"),
    )


def run_model(adapter: ModelAdapter, samples: list[Sample], **tol) -> ModelResult:
    """Run one adapter over the benchmark; return per-item + aggregate metrics.

    ``tol`` (``abs_tol``/``rel_tol``) is forwarded to the verifier.
    """
    items: list[ItemResult] = []
    preds: list[str] = []
    golds: list[str] = []

    for sample in samples:
        steps, answer = adapter.predict(sample)
        pred = _predicted_sample(sample, steps, answer)
        report = verify_sample(pred, **tol)
        gold = sample.jawaban.label
        items.append(ItemResult(
            id=sample.id,
            tokens=count_reasoning_tokens(pred),
            grounding=report["grounding_score"],
            correct=(answer == gold),
            jawaban_pred=answer,
            jawaban_gold=gold,
        ))
        preds.append(answer)
        golds.append(gold)

    n = len(items)
    return ModelResult(
        model=adapter.name,
        items=items,
        answer_accuracy=answer_accuracy(preds, golds),
        mean_grounding=sum(i.grounding for i in items) / n if n else 0.0,
        mean_tokens=sum(i.tokens for i in items) / n if n else 0.0,
    )


def curve_records(result: ModelResult) -> list[tuple[int, float, float]]:
    """Per-item ``(tokens, grounding, accuracy)`` triples for the RQ2 curve (F3-03).

    accuracy is per-item 0/1 (a single item is either right or wrong).
    """
    return [(i.tokens, i.grounding, 1.0 if i.correct else 0.0) for i in result.items]


def metrics_table(results: list[ModelResult]) -> list[dict]:
    """One row per model — the per-model table F6-04 (Hasil) renders."""
    return [
        {
            "model": r.model,
            "n": len(r.items),
            "answer_accuracy": r.answer_accuracy,
            "mean_grounding": r.mean_grounding,
            "mean_tokens": r.mean_tokens,
        }
        for r in results
    ]
