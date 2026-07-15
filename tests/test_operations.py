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


# --- F1-06: lock finalized semantics (ADR-0003) ---

def test_z_score_uses_population_std_ddof0():
    # ddof=0 (population std), deliberately matching deteksi_anomali's np.std default.
    x = np.array([1, 2, 3, 4], dtype=float)
    assert abs(ops.z_score(4.0, x) - (4.0 - x.mean()) / x.std()) < 1e-12
    # and is NOT the sample-std (ddof=1) value — pins the choice.
    assert ops.z_score(4.0, x) != (4.0 - x.mean()) / np.std(x, ddof=1)


def test_z_score_explicit_baseline_window_differs_from_whole_series():
    trending = np.array([10, 20, 30, 40, 50, 60, 70, 80], dtype=float)
    z_whole = ops.z_score(trending[7], trending)          # whole-series population
    z_base = ops.z_score(trending[7], trending[0:4])       # explicit baseline window
    assert z_base > z_whole                                 # tighter baseline -> larger deviation
    assert abs(z_base - z_whole) > 1.0                      # genuinely different


def test_bandingkan_segmen_sign_is_seg2_minus_seg1():
    s = np.array([0, 0, 0, 0, 10, 10, 10, 10], dtype=float)
    assert ops.bandingkan_segmen(s[0:4], s[4:8]) == 10.0    # mean(seg2) - mean(seg1)
    assert ops.bandingkan_segmen(s[4:8], s[0:4]) == -10.0   # order matters, absolute difference


def test_deteksi_anomali_two_sided_and_ddof0():
    # two-sided: a LOW outlier is flagged too, not only high spikes.
    s = np.array([10, 10, 10, 10, -40], dtype=float)        # mean 0, std 20, z of -40 is -2.0
    assert ops.deteksi_anomali(1.5, s) == [4]
