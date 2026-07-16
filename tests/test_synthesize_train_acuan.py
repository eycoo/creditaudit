"""Tes sintesis TRAIN acuan (F4-04).

Menguji pembangkit deret sintetis-terkendali (tanpa network/file) dan, bila
artefak `train_acuan.jsonl` sudah di-generate, memvalidasinya penuh: 100%
grounded, stratifikasi tugas x kesulitan, prasyarat kesulitan, anti-bocor lawan
deret uji, dan determinisme.
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

from curate_benchmark_uji import ANOMALI, PENJELASAN, SEGMEN, TREN  # noqa: E402
from gearts.schema import read_jsonl  # noqa: E402
from gearts.verifier import verify_sample  # noqa: E402
from synthesize_train_acuan import (  # noqa: E402
    DIFFS,
    PER_STRATUM,
    PROFILES,
    TASKS,
    _accept,
    _build_one,
    _seed,
    check_no_leakage,
    generate,
)

TRAIN = _ROOT / "data" / "synthetic" / "train_acuan.jsonl"
TEST = _ROOT / "data" / "processed" / "benchmark_acuan.jsonl"
EXPECTED_LEN = {TREN: 1, SEGMEN: 1, ANOMALI: 1, PENJELASAN: 2}


def _one(task, diff, rep=0):
    """Bangkitkan satu sampel diterima untuk (task,diff) — meniru loop generate()."""
    rng = np.random.default_rng(_seed(task, diff, rep))
    prof = PROFILES[rep % len(PROFILES)]
    sid = f"t_{task}_{diff}_{rep}"
    for _ in range(400):
        built = _build_one(task, diff, sid, prof, rng)
        if built is not None:
            return built
    pytest.fail(f"tak bisa membangkitkan {sid}")


# --- pembangkit: tiap strata grounded penuh + label sesuai maksud kesulitan ---

@pytest.mark.parametrize("task", TASKS)
@pytest.mark.parametrize("diff", DIFFS)
def test_setiap_strata_grounded_dan_sesuai_kesulitan(task, diff):
    full, row = _one(task, diff)
    assert verify_sample(full)["grounding_score"] == 100.0
    assert full.validate() == []
    assert _accept(task, diff, full.jawaban.label, full.jawaban.keyakinan)
    assert len(full.reasoning) == EXPECTED_LEN[task]


def test_hard_itu_ambigu_bukan_asal():
    # kesulitan hard = kelas label yang menahan diri / menjebak, bukan tegas.
    assert _one(TREN, "hard")[0].jawaban.label == "relatif_stabil"
    assert _one(SEGMEN, "hard")[0].jawaban.label == "setara"
    assert _one(ANOMALI, "hard")[0].jawaban.label == "tidak_ada_anomali"
    assert _one(PENJELASAN, "hard")[0].jawaban.label == "tidak_monoton"


def test_generate_deterministik():
    a, ra, _ = generate()
    b, rb, _ = generate()
    assert [(s.id, s.series.nilai) for s in a] == [(s.id, s.series.nilai) for s in b]
    assert ra == rb


def test_generate_skala_dan_strata_seimbang():
    samples, rows, _ = generate()
    assert len(samples) >= 300
    strata = Counter((r["task"], r["difficulty"]) for r in rows)
    assert set(strata) == {(t, d) for t in TASKS for d in DIFFS}
    assert all(c == PER_STRATUM for c in strata.values())
    assert all(verify_sample(s)["grounding_score"] == 100.0 for s in samples)


def test_generate_anti_bocor_lawan_deret_uji():
    samples, _, _ = generate()
    n_test, collisions = check_no_leakage(samples, TEST)
    assert collisions == 0
    # id train terpisah namespace dari id uji (uji_*).
    assert all(s.id.startswith("train_") for s in samples)


# --- artefak yang sudah di-generate ------------------------------------------

def test_artefak_train_semua_grounded_dan_terstratifikasi():
    if not TRAIN.exists():
        pytest.skip(f"{TRAIN.name} belum di-generate (jalankan scripts/synthesize_train_acuan.py)")
    samples = read_jsonl(TRAIN)
    assert len(samples) >= 300
    seen = set()
    for s in samples:
        assert s.id.startswith("train_")
        assert s.validate() == [], f"{s.id}: {s.validate()}"
        assert s.reasoning and s.jawaban.label, f"{s.id}: reasoning/label kosong"
        assert verify_sample(s)["grounding_score"] == 100.0, f"{s.id}: tak 100% grounded"
        seen.add(s.id.split("_")[1])  # task token dari id train_<task>_<diff>_<rep>
    assert seen == {TREN, SEGMEN, ANOMALI, PENJELASAN}
    _, collisions = check_no_leakage(samples, TEST)
    assert collisions == 0
