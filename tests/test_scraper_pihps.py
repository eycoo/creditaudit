"""PIHPS/Bank Indonesia scraper — normalization tests (F4-02).

Tests exercise only the *pure* parse/normalize layer on a small fixture; no
network is touched. The fetch layer (urllib against the BI dashboard) is
separated out precisely so this logic is testable offline.
"""
import math

import pytest

from gearts.schema import Series, read_series_jsonl, write_series_jsonl
from gearts.scrapers.pihps import parse_id_number, records_to_series

# Small fixture mimicking rows pulled from the PIHPS daily grid: a date and a
# price string in Indonesian number format, deliberately out of order and with
# missing/malformed values that normalization must handle.
FIXTURE_ROWS = [
    {"tanggal": "2024-01-03", "harga": "12.750"},
    {"tanggal": "2024-01-01", "harga": "12.500"},
    {"tanggal": "2024-01-02", "harga": "-"},        # missing → skipped
    {"tanggal": "2024-01-04", "harga": ""},         # missing → skipped
    {"tanggal": "2024-01-05", "harga": "13.100,50"},  # thousands + decimal
    {"tanggal": "2024-01-06", "harga": None},       # missing → skipped
    {"tanggal": "2024-01-07", "harga": "bogus"},    # malformed → skipped
]


class TestParseIdNumber:
    def test_thousands_separator(self):
        assert parse_id_number("12.500") == 12500.0

    def test_thousands_and_decimal(self):
        assert parse_id_number("13.100,50") == 13100.50

    def test_plain_integer(self):
        assert parse_id_number("9000") == 9000.0

    @pytest.mark.parametrize("bad", ["", "-", None, "bogus", "  "])
    def test_missing_or_malformed_returns_none(self, bad):
        assert parse_id_number(bad) is None


class TestRecordsToSeries:
    def test_returns_series_with_unit_and_freq_set(self):
        s = records_to_series(FIXTURE_ROWS, nama="beras_medium", satuan="rupiah/kg")
        assert isinstance(s, Series)
        assert s.nama == "beras_medium"
        assert s.satuan == "rupiah/kg"      # unit standardized
        assert s.freq == "harian"           # daily frequency

    def test_missing_and_malformed_rows_dropped(self):
        s = records_to_series(FIXTURE_ROWS, nama="beras_medium", satuan="rupiah/kg")
        # 7 input rows, 4 unparseable → 3 clean values remain
        assert len(s.nilai) == 3

    def test_values_sorted_by_date(self):
        s = records_to_series(FIXTURE_ROWS, nama="beras_medium", satuan="rupiah/kg")
        assert s.nilai == [12500.0, 12750.0, 13100.50]

    def test_all_values_are_finite_floats(self):
        s = records_to_series(FIXTURE_ROWS, nama="beras_medium", satuan="rupiah/kg")
        assert all(isinstance(v, float) and math.isfinite(v) for v in s.nilai)

    def test_empty_after_cleaning_raises(self):
        with pytest.raises(ValueError, match="no valid"):
            records_to_series(
                [{"tanggal": "2024-01-01", "harga": "-"}],
                nama="kosong",
                satuan="rupiah/kg",
            )


def test_series_jsonl_roundtrip(tmp_path):
    s = records_to_series(FIXTURE_ROWS, nama="beras_medium", satuan="rupiah/kg")
    p = tmp_path / "pihps.jsonl"
    write_series_jsonl(p, [s])
    got = read_series_jsonl(p)
    assert len(got) == 1
    assert got[0] == s
