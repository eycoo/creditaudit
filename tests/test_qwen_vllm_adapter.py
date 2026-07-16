"""Qwen/vLLM adapter tests — all offline (no vLLM, no GPU).

Covers the two import-safe halves: prompt construction and the forgiving parser.
The GPU path (`_generate`) is not exercised here; `predict` without vLLM must fail
with a clear, actionable error.
"""
import pytest

import dataclasses

from gearts.adapters.qwen_vllm import (
    QwenVLLMAdapter,
    answer_options,
    build_chat,
    build_prompt,
    parse_model_output,
    snap_label,
)
from gearts.schema import Sample

_S = {
    "id": "dbd_001",
    "series": {"nama": "kasus_dbd", "satuan": "kasus", "freq": "mingguan",
               "nilai": [12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78]},
    "konteks": "16 minggu",
    "pertanyaan": "Apakah ada outbreak?",
    "reasoning": [],
    "jawaban": {"label": "outbreak", "keyakinan": "tinggi"},
}
SAMPLE = Sample.from_dict(_S)

_GOOD_OUTPUT = """Berikut penalarannya:
LANGKAH 1: rata2(nilai[0:5]) = 13.0 | baseline awal
LANGKAH 2: persen_naik(nilai[11]->nilai[15]) = 105.3 | naik tajam
JAWABAN: outbreak
"""


def test_build_prompt_has_series_question_and_ops():
    p = build_prompt(SAMPLE)
    assert "kasus_dbd" in p
    assert "Apakah ada outbreak?" in p
    assert "78" in p                 # series values embedded
    assert "persen_naik" in p        # operation library listed
    assert "LANGKAH" in p            # output format specified


def test_prompt_mode_changes_length_instruction():
    assert build_prompt(SAMPLE, mode="pendek") != build_prompt(SAMPLE, mode="panjang")
    assert "3 langkah" in build_prompt(SAMPLE, max_steps=3)


def test_parse_good_output():
    steps, label = parse_model_output(_GOOD_OUTPUT)
    assert label == "outbreak"
    assert [s.langkah for s in steps] == [1, 2]
    assert steps[0].operasi == "rata2(nilai[0:5])"
    assert steps[0].hasil == 13.0
    assert steps[1].teks == "naik tajam"


def test_parse_skips_malformed_and_empty_steps():
    junk = """LANGKAH 1: rata2(nilai[0:5]) = 13.0
LANGKAH 2: tidak ada operasi di sini = bukan-angka
LANGKAH 3: ini cuma prosa tanpa kurung = 5
LANGKAH 4: max(nilai) = 78
JAWABAN: outbreak.
"""
    steps, label = parse_model_output(junk)
    # only the two well-formed operation-call steps survive, renumbered 1..2
    assert [s.operasi for s in steps] == ["rata2(nilai[0:5])", "max(nilai)"]
    assert [s.langkah for s in steps] == [1, 2]
    assert label == "outbreak"       # trailing period normalized away


def test_parse_empty_text_is_safe():
    steps, label = parse_model_output("")
    assert steps == []
    assert label == ""


def test_max_steps_caps_and_renumbers():
    adapter = QwenVLLMAdapter(max_steps=1)
    adapter._generate = lambda prompt: _GOOD_OUTPUT   # stub the GPU call
    steps, label = adapter.predict(SAMPLE)
    assert len(steps) == 1
    assert steps[0].langkah == 1
    assert label == "outbreak"


def _with_question(q: str) -> Sample:
    return dataclasses.replace(SAMPLE, pertanyaan=q)


def test_answer_options_inferred_per_task():
    assert answer_options(_with_question("Bagaimana kecenderungan (tren) X sepanjang periode?")) \
        == ["meningkat", "menurun", "relatif_stabil"]
    assert answer_options(_with_question("Bandingkan rata-rata X paruh awal versus paruh akhir?")) \
        == ["paruh_awal_lebih_tinggi", "paruh_akhir_lebih_tinggi", "setara"]
    assert answer_options(_with_question("Apakah ada tahun yang menyimpang tak biasa?")) \
        == ["ada_anomali", "tidak_ada_anomali"]
    assert answer_options(_with_question("Apakah ada outbreak?")) == []  # unknown → no menu


def test_prompt_lists_answer_options_when_known():
    p = build_prompt(_with_question("Bagaimana kecenderungan (tren) X sepanjang periode?"))
    assert "relatif_stabil" in p and "menurun" in p    # menu present
    assert "Contoh format" in p                        # worked example present


def test_snap_label_onto_option_set():
    seg = ["paruh_awal_lebih_tinggi", "paruh_akhir_lebih_tinggi", "setara"]
    assert snap_label("paruh awal lebih tinggi", seg) == "paruh_awal_lebih_tinggi"  # spacing
    assert snap_label("tren menurun", ["meningkat", "menurun"]) == "menurun"        # verbose
    assert snap_label("outbreak", []) == "outbreak"                                 # no options
    assert snap_label("entah", ["meningkat", "menurun"]) == "entah"                 # no match kept


def test_build_chat_folds_system_for_gemma():
    from gearts.adapters.qwen_vllm import _SYSTEM
    q = build_chat("Qwen/Qwen2.5-7B-Instruct", _SYSTEM, "P")
    assert [m["role"] for m in q] == ["system", "user"]     # models with system support
    g = build_chat("google/gemma-2-9b-it", _SYSTEM, "P")    # Gemma template rejects system role
    assert [m["role"] for m in g] == ["user"]
    assert _SYSTEM in g[0]["content"] and "P" in g[0]["content"]


def test_adapter_name_reflects_config():
    assert QwenVLLMAdapter(mode="pendek", max_steps=2).name == "qwen2.5-7b:pendek:<= 2"


def test_predict_without_vllm_raises_clear_error():
    # no GPU/vLLM in CI: predict must surface an actionable error, not ImportError
    with pytest.raises(RuntimeError, match="vLLM"):
        QwenVLLMAdapter().predict(SAMPLE)
