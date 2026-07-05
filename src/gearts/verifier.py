"""Deterministic verifier — the core of GEAR-TS (ADR-0002).

Parses each reasoning step's operation string, re-executes it on the original
series, and checks the claimed number against the recomputed one. Produces the
grounding score. Not trained; pure code. Used at dataset cleaning, evaluation,
and (optionally) as an RL reward signal.
"""
from __future__ import annotations

import re

import numpy as np

from gearts.operations import NEEDS_POPULATION, REGISTRY

_OP_RE = re.compile(r"^\s*([a-zA-Z_]\w*)\s*\((.*)\)\s*$")
_SLICE_RE = re.compile(r"^nilai\[(\d+):(\d+)\]$")
_INDEX_RE = re.compile(r"^nilai\[(\d+)\]$")


def parse_operasi(s: str) -> tuple[str, list[str]]:
    """'persen_naik(nilai[11]->nilai[15])' -> ('persen_naik', ['nilai[11]', 'nilai[15]'])."""
    m = _OP_RE.match(s)
    if not m:
        raise ValueError(f"malformed operation: {s!r}")
    name, inner = m.group(1), m.group(2).strip()
    if not inner:
        tokens: list[str] = []
    elif "->" in inner:
        tokens = inner.split("->")
    else:
        tokens = inner.split(",")
    return name, [t.strip() for t in tokens]


def resolve_token(tok: str, series: np.ndarray, bindings: dict):
    """Resolve an argument token to a value against the series + prior bindings."""
    tok = tok.strip()
    m = _SLICE_RE.match(tok)
    if m:
        return series[int(m.group(1)):int(m.group(2))]
    m = _INDEX_RE.match(tok)
    if m:
        return float(series[int(m.group(1))])
    if tok == "nilai":
        return series
    if "=" in tok:  # keyword arg, e.g. deteksi_anomali(z=3)
        return float(tok.split("=", 1)[1])
    try:
        return float(tok)
    except ValueError:
        pass
    if tok in bindings:
        return bindings[tok]
    raise ValueError(f"cannot resolve token: {tok!r}")


def eval_step(operasi: str, series: np.ndarray, bindings: dict):
    op, tokens = parse_operasi(operasi)
    if op not in REGISTRY:
        raise ValueError(f"unknown operation: {op}")
    values = [resolve_token(t, series, bindings) for t in tokens]
    if op in NEEDS_POPULATION and len(values) == 1:
        values.append(series)  # implicit population = full series
    return REGISTRY[op](*values)


def _is_scalar(x) -> bool:
    return isinstance(x, (int, float, np.floating, np.integer)) and not isinstance(x, bool)


def _grounded(expected: float, claimed: float, abs_tol: float, rel_tol: float) -> bool:
    # Combined tolerance: absolute for exact results (13.0, 6.0), relative so a
    # value rounded for presentation (105.3 vs recomputed 105.26) still grounds
    # while a real magnitude error (30 vs 105) does not. rel_tol is a calibration knob.
    return abs(expected - claimed) <= max(abs_tol, rel_tol * abs(expected))


def verify_sample(sample, abs_tol: float = 0.01, rel_tol: float = 0.01) -> dict:
    """Recompute every reasoning step; return per-step report + grounding score.

    grounding_score = 100 * grounded / total, over scalar-returning steps.
    Non-scalar ops (e.g. deteksi_anomali) are reported with grounded=None and
    excluded from the score. A step whose operation fails to evaluate counts as
    not grounded (that is the point — an ungroundable claim is ungrounded).
    """
    series = np.asarray(sample.series.nilai, dtype=float)
    bindings: dict = {}
    steps: list[dict] = []
    grounded_count = 0
    scalar_count = 0

    for step in sample.reasoning:
        try:
            expected = eval_step(step.operasi, series, bindings)
        except Exception as e:  # ungroundable claim
            scalar_count += 1
            steps.append({"langkah": step.langkah, "grounded": False,
                          "expected": None, "claimed": step.hasil, "error": str(e)})
            continue

        if _is_scalar(expected):
            scalar_count += 1
            expected_f = float(expected)
            bindings[f"langkah{step.langkah}"] = expected_f
            ok = _grounded(expected_f, float(step.hasil), abs_tol, rel_tol)
            grounded_count += ok
            steps.append({"langkah": step.langkah, "grounded": bool(ok),
                          "expected": expected_f, "claimed": step.hasil})
        else:
            steps.append({"langkah": step.langkah, "grounded": None,
                          "expected": expected, "claimed": step.hasil, "note": "non-scalar"})

    score = 100.0 * grounded_count / scalar_count if scalar_count else 0.0
    return {"steps": steps, "grounding_score": score}
