"""Validasi benchmark uji (F2-03) — regresi guard, bukan generator.

Membaca artefak acuan yang sudah di-generate (`benchmark_acuan.jsonl`); tak
memodifikasi data (kontrak data-qa: verifikasi, jangan perbaiki). Skip bila
artefak belum di-generate.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

from curate_benchmark_uji import CURATION  # noqa: E402
from gearts.metrics import dataset_grounding  # noqa: E402
from gearts.schema import read_jsonl  # noqa: E402
from gearts.verifier import verify_sample  # noqa: E402

ACUAN = _ROOT / "data" / "processed" / "benchmark_acuan.jsonl"

# Host sumber train rencana (F4-01 sumber wajib) — beda host = tak ada bocor literal.
TRAIN_HOSTS = ("bi.go.id/hargapangan", "skdr.surveilans.org", "data.kemkes.go.id", "dataonline.bmkg.go.id")


def test_schema_zero_failures():
    if not ACUAN.exists():
        pytest.skip(f"{ACUAN.name} belum di-generate")
    samples = read_jsonl(ACUAN)
    fails = [(s.id, s.validate()) for s in samples if s.validate()]
    assert fails == []
    assert len(samples) >= 15


def test_dataset_grounding_is_100():
    if not ACUAN.exists():
        pytest.skip(f"{ACUAN.name} belum di-generate")
    samples = read_jsonl(ACUAN)
    assert dataset_grounding(samples) == 100.0
    assert all(verify_sample(s)["grounding_score"] == 100.0 for s in samples)


def test_distribution_covers_all_task_types_and_difficulties():
    if not ACUAN.exists():
        pytest.skip(f"{ACUAN.name} belum di-generate")
    samples = read_jsonl(ACUAN)
    task_of = {m["id"]: m["task"] for m in CURATION.values()}
    diff_of = {m["id"]: m["difficulty"] for m in CURATION.values()}
    tasks = {task_of[s.id] for s in samples}
    diffs = {diff_of[s.id] for s in samples}
    assert tasks == {"anomali", "tren", "segmen", "penjelasan"}
    assert diffs == {"easy", "medium", "hard"}


def test_no_leakage_against_planned_train_hosts():
    manifest = (_ROOT / "data" / "manifest_benchmark_uji.md").read_text(encoding="utf-8")
    assert "worldbank.org" in manifest
    for host in TRAIN_HOSTS:
        assert host not in manifest, f"sumber uji menyentuh host train rencana: {host}"
