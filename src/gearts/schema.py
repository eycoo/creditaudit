"""JSONL sample schema (project_brief.md Lampiran A).

Field names are Indonesian and canonical: the dataset, the LLM output, and the
verifier all key on them. One JSON object per line.

# ponytail: stdlib dataclasses + manual validate(); move to pydantic if bulk
# dataset validation becomes a bottleneck.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

from gearts.operations import REGISTRY

FREQ = {"harian", "mingguan", "bulanan", "tahunan", "jam"}
KEYAKINAN = {"rendah", "sedang", "tinggi"}


@dataclass
class Series:
    nama: str
    satuan: str
    freq: str
    nilai: list[float]


@dataclass
class ReasoningStep:
    langkah: int
    operasi: str
    hasil: float
    teks: str = ""


@dataclass
class Jawaban:
    label: str
    keyakinan: str


@dataclass
class Sample:
    id: str
    series: Series
    konteks: str
    pertanyaan: str
    reasoning: list[ReasoningStep]
    jawaban: Jawaban

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Sample":
        _reject_unknown(cls, d, skip={"series", "reasoning", "jawaban"})
        return cls(
            id=d["id"],
            series=_build(Series, d["series"]),
            konteks=d.get("konteks", ""),
            pertanyaan=d["pertanyaan"],
            reasoning=[_build(ReasoningStep, s) for s in d.get("reasoning", [])],
            jawaban=_build(Jawaban, d["jawaban"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> list[str]:
        problems: list[str] = []
        if self.series.freq not in FREQ:
            problems.append(f"series.freq invalid: {self.series.freq!r}")
        if not self.series.nilai:
            problems.append("series.nilai is empty")
        if self.jawaban.keyakinan not in KEYAKINAN:
            problems.append(f"jawaban.keyakinan invalid: {self.jawaban.keyakinan!r}")
        for step in self.reasoning:
            name = step.operasi.split("(", 1)[0].strip()
            if name not in REGISTRY:
                problems.append(f"reasoning[{step.langkah}].operasi unknown: {name!r}")
        return problems


def read_jsonl(path: str | Path) -> list[Sample]:
    with open(path, encoding="utf-8") as f:
        return [Sample.from_dict(json.loads(line)) for line in f if line.strip()]


def write_jsonl(path: str | Path, samples: list[Sample]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s.to_dict(), ensure_ascii=False) + "\n")


def _build(cls: type, d: dict[str, Any]):
    _reject_unknown(cls, d)
    return cls(**d)


def _reject_unknown(cls: type, d: dict[str, Any], skip: set[str] = frozenset()) -> None:
    known = {f.name for f in fields(cls)}
    unknown = set(d) - known
    if unknown:
        raise ValueError(f"unknown keys in {cls.__name__}: {sorted(unknown)}")
