"""Qwen/vLLM adapter tests — all offline (no vLLM, no GPU).

Covers the two import-safe halves: prompt construction and the forgiving parser.
The GPU path (`_generate`) is not exercised here; `predict` without vLLM must fail
with a clear, actionable error.
"""
import pytest

from gearts.adapters.qwen_vllm import (
    QwenVLLMAdapter,
    build_prompt,
    parse_model_output,
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


def test_adapter_name_reflects_config():
    assert QwenVLLMAdapter(mode="pendek", max_steps=2).name == "qwen2.5-7b:pendek:<= 2"


def test_predict_without_vllm_raises_clear_error():
    # no GPU/vLLM in CI: predict must surface an actionable error, not ImportError
    with pytest.raises(RuntimeError, match="vLLM"):
        QwenVLLMAdapter().predict(SAMPLE)
