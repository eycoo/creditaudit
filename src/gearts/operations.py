"""Operation library (project_brief.md Lampiran C).

Every reasoning step names an operation from this registry, so the verifier
can re-execute it deterministically over the original series. Pure functions,
NumPy only. Operation names (registry keys) are canonical — the dataset and
the LLM output key on them.
"""
from __future__ import annotations

import numpy as np

Number = float
Seq = np.ndarray


def rata2(seg: Seq) -> Number:
    return float(np.mean(seg))


def delta(a: Number, b: Number) -> Number:
    return float(b - a)


def persen_naik(a: Number, b: Number) -> Number:
    if a == 0:
        raise ValueError("persen_naik undefined when base a == 0")
    return float((b - a) / a * 100)


def rasio(a: Number, b: Number) -> Number:
    if b == 0:
        raise ValueError("rasio undefined when denominator b == 0")
    return float(a / b)


def slope(seg: Seq) -> Number:
    seg = np.asarray(seg, dtype=float)
    x = np.arange(len(seg))
    return float(np.polyfit(x, seg, 1)[0])


def min_(seg: Seq) -> Number:
    return float(np.min(seg))


def max_(seg: Seq) -> Number:
    return float(np.max(seg))


def z_score(x: Number, pop: Seq) -> Number:
    """Deviation of `x` from `pop` in population standard deviations (ADR-0003 Item 3).

    `pop` is an explicit argument: the verifier passes the whole series when the
    step omits it, but reasoning over a trending series should pass a baseline
    window (e.g. `z_score(nilai[15], nilai[0:8])`). `ddof=0` (population std, not
    sample std) is deliberate — it must match `deteksi_anomali` numerically.
    """
    pop = np.asarray(pop, dtype=float)
    sd = np.std(pop)  # ddof=0 (population std) — deliberate; must agree with deteksi_anomali
    if sd == 0:
        raise ValueError("z_score undefined when population std == 0")
    return float((x - np.mean(pop)) / sd)


def deteksi_anomali(ambang: Number, pop: Seq) -> list[int]:
    """Indices whose `|z| > ambang` over `pop` — two-sided (ADR-0003 Item 1).

    Two-sided so low outliers are flagged as well as high spikes; direction
    (upward-only outbreak framing) is expressed in the question, not here.
    Population defaults to the whole series (verifier appends it). Returns a
    sorted 0-based index list — a non-scalar result graded by index-set / Jaccard
    in `verifier.verify_sample` (F1-05). `ddof=0` matches `z_score`.
    """
    pop = np.asarray(pop, dtype=float)
    sd = np.std(pop)  # ddof=0 — must agree with z_score
    if sd == 0:
        return []
    z = (pop - np.mean(pop)) / sd
    return [int(i) for i in np.where(np.abs(z) > ambang)[0]]


def bandingkan_segmen(r1: Seq, r2: Seq) -> Number:
    """Absolute difference of segment means: `mean(r2) - mean(r1)` (ADR-0003 Item 2).

    Scalar, absolute difference only — no percent/ratio mode. Percent or ratio
    between segments is expressed by composition (`rata2` each segment, then
    `persen_naik`/`rasio` on the two `langkah{N}` bindings), keeping the library
    orthogonal. Order matters: `r2` minus `r1`.
    """
    return float(np.mean(r2) - np.mean(r1))


REGISTRY = {
    "rata2": rata2,
    "delta": delta,
    "persen_naik": persen_naik,
    "rasio": rasio,
    "slope": slope,
    "min": min_,
    "max": max_,
    "z_score": z_score,
    "deteksi_anomali": deteksi_anomali,
    "bandingkan_segmen": bandingkan_segmen,
}

# operations that need the full series appended as an implicit population arg
NEEDS_POPULATION = {"z_score", "deteksi_anomali"}
