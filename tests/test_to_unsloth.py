"""Tes converter gearts -> Unsloth (F4-05).

Inti: round-trip. Teks assistant yang di-render converter, saat di-parse ULANG
oleh `parse_model_output` adapter, mengembalikan langkah (operasi+hasil) & label
yang identik dengan sampel gold. Ini menjamin format target latih persis format
yang di-verifikasi harness saat evaluasi.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "scripts"):
    sys.path.insert(0, str(p))

from gearts.adapters.qwen_vllm import answer_options, parse_model_output, snap_label  # noqa: E402
from gearts.schema import Jawaban, ReasoningStep, Sample, Series  # noqa: E402
from to_unsloth import DATASET_INFO, render_assistant, to_conversation  # noqa: E402


def _sample():
    return Sample(
        id="train_penjelasan_easy_000",
        series=Series(nama="harga_beras", satuan="rupiah per kg", freq="mingguan",
                      nilai=[10000.0, 11000.0, 12500.0, 14000.0]),
        konteks="deret sintetis-terkendali",
        pertanyaan="Jelaskan pola utama harga beras sepanjang periode beserta arah dan besar perubahannya.",
        reasoning=[
            ReasoningStep(langkah=1, operasi="slope(nilai[0:4])", hasil=1330.0, teks="tren naik"),
            ReasoningStep(langkah=2, operasi="persen_naik(nilai[0]->nilai[3])", hasil=40.0, teks="ujung ke ujung"),
        ],
        jawaban=Jawaban(label="naik_besar", keyakinan="tinggi"),
    )


def test_round_trip_langkah_dan_label():
    s = _sample()
    conv = to_conversation(s)
    assert [m["role"] for m in conv["messages"]] == ["system", "user", "assistant"]

    assistant = conv["messages"][2]["content"]
    steps, label = parse_model_output(assistant)

    assert [(x.operasi, x.hasil) for x in steps] == \
           [(x.operasi, x.hasil) for x in s.reasoning]
    assert snap_label(label, answer_options(s)) == s.jawaban.label


def test_assistant_format_grammar():
    s = _sample()
    text = render_assistant(s)
    assert text.splitlines()[0].startswith("LANGKAH 1: slope(nilai[0:4]) = ")
    assert text.strip().endswith("JAWABAN: naik_besar")


def test_user_prompt_berisi_deret_dan_pertanyaan():
    s = _sample()
    user = to_conversation(s)["messages"][1]["content"]
    assert "harga_beras" in user
    assert "10000.0" in user            # deret masuk prompt
    assert "pola utama" in user         # pertanyaan masuk prompt


def test_dataset_info_sharegpt():
    info = DATASET_INFO["gearts_train"]
    assert info["file_name"] == "train_unsloth.jsonl"
    assert info["formatting"] == "sharegpt"
    assert info["tags"]["assistant_tag"] == "assistant"
