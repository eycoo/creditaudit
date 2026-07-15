"""Tes kurasi benchmark uji (F2-01).

Logika build diuji tanpa network (fixture mentah inline). Artefak JSONL yang
sudah dikurasi, bila ada, ikut divalidasi; di-skip bila belum di-generate.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

from curate_benchmark_uji import (  # noqa: E402
    ANOMALI,
    CURATION,
    PENJELASAN,
    SEGMEN,
    TREN,
    build_sample,
    extract_series,
)
from gearts.schema import read_jsonl  # noqa: E402

BENCHMARK = _ROOT / "data" / "processed" / "benchmark_uji.jsonl"

# Respons World Bank tiruan: tak urut + satu null (harus dibuang & diurutkan).
FAKE_WB = [
    {"page": 1, "pages": 1, "total": 3},
    [
        {"date": "2001", "value": 45.6},
        {"date": "2000", "value": 48.1},
        {"date": "2002", "value": None},
    ],
]


def test_curation_covers_all_four_tasks():
    tasks = {m["task"] for m in CURATION.values()}
    assert tasks == {ANOMALI, TREN, SEGMEN, PENJELASAN}


def test_curation_two_domains_min_15_unique_ids():
    assert len(CURATION) >= 15
    ids = [m["id"] for m in CURATION.values()]
    assert len(set(ids)) == len(ids)
    assert {m["domain"] for m in CURATION.values()} == {"kesehatan", "pangan-pertanian"}


def test_curation_has_varied_difficulty():
    diffs = {m["difficulty"] for m in CURATION.values()}
    assert {"easy", "medium", "hard"} <= diffs


def test_extract_series_orders_and_drops_null():
    assert extract_series(FAKE_WB) == [(2000, 48.1), (2001, 45.6)]


def test_extract_series_rejects_bad_format():
    with pytest.raises(ValueError):
        extract_series([{"not": "a series"}])


def test_build_sample_is_valid_series_without_reasoning():
    sample, row = build_sample("SH.DYN.MORT", FAKE_WB)
    assert sample.series.nilai == [48.1, 45.6]        # urut menaik tahun, null dibuang
    assert sample.series.freq == "tahunan"
    assert sample.series.satuan == "per 1000 kelahiran hidup"
    assert sample.reasoning == []                     # F2-02 mengisi
    assert sample.validate() == []                    # Series valid
    assert row["n"] == 2 and row["rentang"] == "2000-2001"
    assert "worldbank.org" in row["sumber"] and row["tanggal_ambil"]


def test_curated_benchmark_file_is_valid():
    if not BENCHMARK.exists():
        pytest.skip(f"{BENCHMARK.name} belum di-generate (jalankan scripts/curate_benchmark_uji.py)")
    samples = read_jsonl(BENCHMARK)
    assert len(samples) >= 15
    for s in samples:
        assert s.validate() == [], f"{s.id}: {s.validate()}"
        assert s.series.nilai, f"{s.id}: nilai kosong"
        assert s.reasoning == [], f"{s.id}: harusnya belum ada reasoning (F2-01)"
