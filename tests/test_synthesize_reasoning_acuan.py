"""Tes sintesis reasoning acuan (F2-02).

Logika rantai diuji dengan Series buatan (tanpa network/file). Artefak acuan
JSONL, bila ada, divalidasi penuh: tiap sampel 100% grounded + rantai terpendek
(tiap langkah dikutip jawaban).
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

from curate_benchmark_uji import ANOMALI, PENJELASAN, SEGMEN, TREN  # noqa: E402
from gearts.schema import Sample, Series, read_jsonl  # noqa: E402
from gearts.verifier import verify_sample  # noqa: E402
from synthesize_reasoning_acuan import (  # noqa: E402
    TASK_OF,
    build_reference,
    synthesize,
)

ACUAN = _ROOT / "data" / "processed" / "benchmark_acuan.jsonl"

# Panjang rantai minimal yang diharapkan per jenis tugas (brief v2 §4.2).
EXPECTED_LEN = {TREN: 1, SEGMEN: 1, ANOMALI: 1, PENJELASAN: 2}


def _mk(nama, nilai, freq="tahunan", satuan="unit"):
    return Sample(id=f"buatan_{nama}", series=Series(nama=nama, satuan=satuan, freq=freq, nilai=nilai),
                  konteks="", pertanyaan="", reasoning=[],
                  jawaban=None)  # jawaban diisi build_reference


def _verify(sample, reasoning, jawaban):
    full = Sample(id=sample.id, series=sample.series, konteks=sample.konteks,
                  pertanyaan="x", reasoning=reasoning, jawaban=jawaban)
    return verify_sample(full)["grounding_score"]


def test_tren_naik_satu_langkah_grounded():
    s = _mk("naik", [1.0, 2.0, 3.0, 4.0, 5.0])
    q, r, j, cites = build_reference(s, TREN)
    assert len(r) == 1 and r[0].operasi == "slope(nilai[0:5])"
    assert j.label == "meningkat"
    assert _verify(s, r, j) == 100.0
    assert cites == [1]


def test_tren_turun_label():
    s = _mk("turun", [10.0, 8.0, 6.0, 4.0, 2.0])
    _, r, j, _ = build_reference(s, TREN)
    assert j.label == "menurun"


def test_tren_datar_label():
    s = _mk("datar", [5.0, 5.01, 4.99, 5.0, 5.0])
    _, _, j, _ = build_reference(s, TREN)
    assert j.label == "relatif_stabil"


def test_segmen_signed_diff_grounded():
    s = _mk("seg", [1.0, 1.0, 1.0, 9.0, 9.0, 9.0])  # paruh akhir lebih tinggi
    q, r, j, cites = build_reference(s, SEGMEN)
    assert len(r) == 1 and r[0].operasi.startswith("bandingkan_segmen(")
    assert j.label == "paruh_akhir_lebih_tinggi"
    assert _verify(s, r, j) == 100.0


def test_penjelasan_two_steps_both_cited():
    s = _mk("naik", [10.0, 20.0, 30.0, 40.0, 50.0])
    q, r, j, cites = build_reference(s, PENJELASAN)
    assert len(r) == 2
    assert [step.langkah for step in r] == [1, 2]
    assert cites == [1, 2]                      # kedua langkah dikutip jawaban
    assert j.label == "naik_besar"              # arah (slope) + besaran (persen)
    assert _verify(s, r, j) == 100.0


def test_penjelasan_non_monotonic_needs_both_steps():
    # naik lalu turun: slope < 0 tapi ujung akhir > awal -> tidak_monoton.
    s = _mk("bukit", [10.0, 30.0, 40.0, 25.0, 15.0, 12.0])
    _, r, j, _ = build_reference(s, PENJELASAN)
    assert j.label == "tidak_monoton"


def test_penjelasan_shortest_removing_either_step_breaks_sufficiency():
    # Rantai terpendek: label butuh slope (arah) DAN persen_naik (uji <5% datar).
    s = _mk("naik", [10.0, 20.0, 30.0, 40.0, 50.0])
    _, r, _, cites = build_reference(s, PENJELASAN)
    for step in r:
        assert step.langkah in cites  # tak ada langkah yang tak terpakai jawaban


# --- artefak yang sudah di-generate ---

def test_acuan_file_all_100_grounded_and_shortest():
    if not ACUAN.exists():
        pytest.skip(f"{ACUAN.name} belum di-generate (jalankan scripts/synthesize_reasoning_acuan.py)")
    samples = read_jsonl(ACUAN)
    assert len(samples) >= 15
    seen_tasks = set()
    for s in samples:
        task = TASK_OF[s.id]
        seen_tasks.add(task)
        assert s.validate() == [], f"{s.id}: {s.validate()}"
        assert s.reasoning, f"{s.id}: reasoning kosong (F2-02 harus mengisi)"
        assert s.jawaban.label, f"{s.id}: label gold kosong"
        assert verify_sample(s)["grounding_score"] == 100.0, f"{s.id}: tidak 100% grounded"
        assert len(s.reasoning) == EXPECTED_LEN[task], f"{s.id}: panjang rantai bukan minimal"
    assert seen_tasks == {TREN, SEGMEN, ANOMALI, PENJELASAN}


def test_acuan_regenerates_identically():
    if not ACUAN.exists():
        pytest.skip("acuan belum di-generate")
    for s in read_jsonl(ACUAN):
        # membangun ulang dari series yang sama menghasilkan reasoning identik (deterministik)
        rebuilt, _ = synthesize(Sample(id=s.id, series=s.series, konteks=s.konteks,
                                        pertanyaan="", reasoning=[], jawaban=None))
        assert [(x.operasi, x.hasil) for x in rebuilt.reasoning] == \
               [(x.operasi, x.hasil) for x in s.reasoning], f"{s.id}: non-deterministik"
