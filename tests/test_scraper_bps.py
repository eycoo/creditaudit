"""Unit tests for the BPS scraper's PURE parts (F4-03) — no network.

Covers the composite `datacontent` key construction and the payload→`Series`
normalization, using a hand-built payload that mirrors the real BPS `data`-model
response shape (decoded from var 70). The network functions (`fetch_json`,
`list_periods`, `fetch_var_data`) are deliberately not exercised here.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from gearts.scrapers.bps import (  # noqa: E402
    _to_float,
    build_series,
    datacontent_key,
    pick_id,
)


def _payload():
    """Mirror a real BPS data payload: var 70, turvar 211, provinces 6100 & 3400."""
    return {
        "var": [{"val": 70, "label": "Akses Internet Penduduk", "unit": "persen"}],
        "turvar": [{"val": 211, "label": "Laki-laki"}],
        "turtahun": [{"val": 0, "label": "Tahun"}],
        # deliberately unsorted to prove chronological ordering by year label
        "tahun": [
            {"val": 123, "label": "2023"},
            {"val": 121, "label": "2021"},
            {"val": 122, "label": "2022"},
        ],
        "vervar": [{"val": 6100, "label": "KALIMANTAN TIMUR"}, {"val": 3400, "label": "DI YOGYAKARTA"}],
        "datacontent": {
            "6100702111210": 60.0,   # 6100|70|211|121|0
            "6100702111220": 65.05,  # 2022
            "6100702111230": 66.2,   # 2023
            "3400702111210": 77.0,
            "3400702111220": 77.92,
            # 3400 2023 intentionally MISSING → should be skipped, not crash
        },
    }


def test_datacontent_key_matches_observed_encoding():
    # Real observed: "6100702111220" = vervar 6100 | var 70 | turvar 211 | th 122 | turtahun 0
    assert datacontent_key(6100, 70, 211, 122, 0) == "6100702111220"
    assert datacontent_key(3400, 70, 211, 121, 0) == "3400702111210"


def test_build_series_orders_chronologically_and_uses_unit():
    s = build_series(_payload(), vervar=6100, turvar=211)
    assert s.nilai == [60.0, 65.05, 66.2]  # 2021, 2022, 2023 in order
    assert s.satuan == "persen"
    assert s.freq == "tahunan"
    assert "internet" in s.nama


def test_build_series_skips_missing_points():
    # province 3400 has no 2023 datacontent key → 2 points, no crash
    s = build_series(_payload(), vervar=3400, turvar=211)
    assert s.nilai == [77.0, 77.92]


def test_build_series_raises_when_no_values():
    with pytest.raises(ValueError):
        build_series(_payload(), vervar=9999, turvar=211)  # unknown province


@pytest.mark.parametrize(
    "raw,expected",
    [(65.05, 65.05), (12, 12.0), ("13,5", None), ("-", None), ("", None), (None, None), ("80.4", 80.4)],
)
def test_to_float_tolerant(raw, expected):
    assert _to_float(raw) == expected


def test_pick_id_prefers_aggregate_label():
    # var 192-style turtahun: prefer "Tahunan" over the semesters.
    turtahun = [
        {"val": 61, "label": "Semester 1 (Maret)"},
        {"val": 62, "label": "Semester 2 (September)"},
        {"val": 63, "label": "Tahunan"},
    ]
    assert pick_id(turtahun, r"tahunan") == 63
    # turvar: prefer "Jumlah" over Perkotaan/Perdesaan.
    turvar = [{"val": 432, "label": "Perkotaan"}, {"val": 433, "label": "Perdesaan"}, {"val": 434, "label": "Jumlah"}]
    assert pick_id(turvar, r"jumlah|total") == 434


def test_pick_id_falls_back_to_first():
    items = [{"val": 211, "label": "Laki-laki"}, {"val": 212, "label": "Perempuan"}]
    assert pick_id(items, r"jumlah|total") == 211  # no match → first
    assert pick_id([], r"x") == 0  # empty → 0
