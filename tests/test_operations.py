"""Operation library tests keyed to project_brief.md Lampiran B."""
import numpy as np

from gearts import operations as ops

NILAI = np.array([12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78], dtype=float)


def test_rata2_baseline():
    assert ops.rata2(NILAI[0:5]) == 13.0


def test_persen_naik_lampiran_b():
    assert round(ops.persen_naik(NILAI[11], NILAI[15]), 1) == 105.3


def test_rasio_lampiran_b():
    assert ops.rasio(NILAI[15], 13.0) == 6.0


def test_delta():
    assert ops.delta(NILAI[0], NILAI[15]) == 66.0


def test_slope_positive_at_tail():
    assert ops.slope(NILAI[10:16]) > 0


def test_minmax():
    assert ops.max_(NILAI) == 78.0
    assert ops.min_(NILAI) == 11.0


def test_z_score_matches_definition():
    z = ops.z_score(NILAI[15], NILAI)
    expected = (78.0 - NILAI.mean()) / NILAI.std()
    assert abs(z - expected) < 1e-9


def test_persen_naik_zero_base_raises():
    import pytest
    with pytest.raises(ValueError):
        ops.persen_naik(0, 10)
