"""RQ3/RQ4 tests — all offline (no vLLM, no GPU).

Covers the method line-ups, the pure-statistics baseline (B4), the raw-output
token accounting, grounding-per-token, the free-prose prompt, and the LoRA engine
plumbing that lets base + LoRA methods share one loaded engine. The GPU path
(`_generate`) is never exercised.
"""
import pytest

import exp3_rq3
import exp4_rq4
import methods
from gearts.adapters.qwen_vllm import QwenVLLMAdapter, build_prompt_prosa
from gearts.harness import MockModel
from gearts.schema import Sample
from methods import (
    StatBaselineAdapter,
    _output_tokens,
    _rebuild,
    grounding_per_token,
    lora_engine_kwargs,
    run_methods,
    stat_answer,
    task_of,
)

TREN_Q = "Bagaimana kecenderungan (tren) deret x sepanjang periode?"
SEG_Q = "Bandingkan rata-rata deret x paruh awal versus paruh akhir periode?"
ANOM_Q = "Apakah terdapat tahun dengan deret x yang menyimpang tak biasa?"
PENJ_Q = "Jelaskan pola utama deret x beserta arah dan besar perubahannya."


def _sample(nilai, pertanyaan, gold):
    return Sample.from_dict({
        "id": "s1",
        "series": {"nama": "deret_x", "satuan": "unit", "freq": "tahunan", "nilai": nilai},
        "konteks": "ctx",
        "pertanyaan": pertanyaan,
        "reasoning": [],
        "jawaban": {"label": gold, "keyakinan": "sedang"},
    })


TREN_UP = _sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], TREN_Q, "meningkat")


# --- task inference + B4 pure statistics ------------------------------------

def test_task_of_infers_from_question():
    assert task_of(_sample([1, 2], TREN_Q, "x")) == "tren"
    assert task_of(_sample([1, 2], SEG_Q, "x")) == "segmen"
    assert task_of(_sample([1, 2], ANOM_Q, "x")) == "anomali"
    assert task_of(_sample([1, 2], PENJ_Q, "x")) == "penjelasan"


def test_stat_answer_per_task():
    assert stat_answer(_sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], TREN_Q, "m")) == "meningkat"
    assert stat_answer(_sample([10, 9, 8, 7, 6, 5, 4, 3, 2, 1], TREN_Q, "m")) == "menurun"
    assert stat_answer(_sample([1, 1, 1, 1, 9, 9, 9, 9], SEG_Q, "x")) == "paruh_akhir_lebih_tinggi"
    assert stat_answer(_sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 20], PENJ_Q, "x")) == "naik_besar"


def test_stat_baseline_adapter_emits_no_reasoning():
    steps, ans = StatBaselineAdapter().predict(TREN_UP)
    assert steps == []
    assert ans == "meningkat"


# --- runner: rows + grounding-per-token -------------------------------------

def _honest_ops_adapter():
    steps = [{"langkah": 1, "operasi": "slope(nilai[0:10])", "hasil": 1.0, "teks": "naik linear"}]
    return MockModel("ops", {"s1": (steps, "meningkat")})


def _free_prose_adapter():
    return MockModel("prosa", {"s1": ([], "meningkat")})  # no parseable steps


def test_run_methods_grounding_tokens_and_gpt():
    rows = run_methods([
        ("ops", _honest_ops_adapter()),
        ("prosa", _free_prose_adapter()),
        ("B4", StatBaselineAdapter()),
    ], [TREN_UP])
    by = {r["method"]: r for r in rows}

    assert by["ops"]["mean_grounding"] == 100.0            # slope recomputes to 1.0
    assert by["ops"]["answer_accuracy"] == 100.0
    assert by["ops"]["mean_tokens"] > 0
    assert by["ops"]["grounding_per_token"] == pytest.approx(100.0 / by["ops"]["mean_tokens"])

    assert by["prosa"]["mean_grounding"] == 0.0            # no operations → ungrounded
    assert by["prosa"]["answer_accuracy"] == 100.0
    assert by["prosa"]["grounding_per_token"] is None      # no tokens counted → not 0/0

    assert by["B4"]["answer_accuracy"] == 100.0            # pure stats gets it right
    assert by["B4"]["mean_grounding"] == 0.0               # nothing auditable
    assert by["B4"]["mean_tokens"] == 0.0
    assert by["B4"]["grounding_per_token"] is None


def test_run_methods_scores_wrong_answer():
    wrong = MockModel("w", {"s1": ([], "menurun")})
    (row,) = run_methods([("w", wrong)], [TREN_UP])
    assert row["answer_accuracy"] == 0.0


def test_grounding_per_token_guards_zero():
    assert grounding_per_token(80.0, 16.0) == 5.0
    assert grounding_per_token(50.0, 0.0) is None


def test_output_tokens_prefers_raw_output():
    class RawAdapter:
        last_raw = "satu dua tiga empat"
    pred = _rebuild(TREN_UP, [], "meningkat")
    assert _output_tokens(RawAdapter(), pred) == 4   # raw words, not step-based


# --- LoRA engine plumbing ---------------------------------------------------

def test_lora_path_sets_engine_flags_and_name():
    a = QwenVLLMAdapter(lora_path="path/to/adapter")
    assert a._llm_kwargs.get("enable_lora") is True
    assert a._llm_kwargs.get("max_lora_rank") == 32   # ≥ our r=32
    assert a.name.endswith(":lora")


def test_base_adapter_has_no_lora_flags():
    b = QwenVLLMAdapter()
    assert "enable_lora" not in b._llm_kwargs
    assert not b.name.endswith(":lora")


def test_lora_engine_kwargs_merges_without_dropping_overrides():
    kw = lora_engine_kwargs({"model": "M", "tensor_parallel_size": 2})
    assert kw["model"] == "M" and kw["tensor_parallel_size"] == 2
    assert kw["enable_lora"] is True and kw["max_lora_rank"] == 32


def test_base_and_lora_share_engine_kwargs():
    # base + LoRA built from the same shared kwargs must key to ONE cached engine
    shared = lora_engine_kwargs({})
    base = QwenVLLMAdapter(**shared)
    kami = QwenVLLMAdapter(lora_path="p", **shared)
    assert base._llm_kwargs == kami._llm_kwargs


# --- free-prose prompt ------------------------------------------------------

def test_build_prompt_prosa_has_menu_but_no_operation_format():
    p = build_prompt_prosa(_sample([1, 2, 3], TREN_Q, "meningkat"))
    assert "LANGKAH" not in p                 # no operation format
    assert "JAWABAN" in p                     # answerable → accuracy scoreable
    assert "relatif_stabil" in p              # closed option menu present
    assert "slope" not in p                   # operation library not offered


# --- line-ups + table writers -----------------------------------------------

def test_rq3_methods_lineup():
    m = dict(methods.rq3_methods())
    assert list(m) == ["B1-prosa", "B2-veritime", "B3-selfbudget", "B4-statistik", "Kami"]
    assert m["Kami"].lora_path                # fine-tuned
    assert m["B2-veritime"].lora_path is None  # base
    assert m["B1-prosa"].prompt_style == "prosa"


def test_rq4_variants_lineup():
    v = dict(methods.rq4_variants())
    assert list(v)[0] == "Kami-penuh"
    assert {"-finetune", "-format_operasi", "-target_terpendek", "-adaptif"} <= set(v)
    assert v["-finetune"].lora_path is None
    assert v["-format_operasi"].prompt_style == "prosa"
    assert v["-adaptif"].max_steps == 1


def test_exp3_run_writes_table(tmp_path):
    rows = exp3_rq3.run([("B4-statistik", StatBaselineAdapter())], [TREN_UP], outdir=tmp_path)
    assert (tmp_path / "tabel_rq3.csv").exists()
    assert (tmp_path / "tabel_rq3.md").exists()
    assert rows[0]["method"] == "B4-statistik"


def test_exp4_run_writes_table(tmp_path):
    rows = exp4_rq4.run([("Kami-penuh", StatBaselineAdapter())], [TREN_UP], outdir=tmp_path)
    assert (tmp_path / "tabel_rq4.csv").exists()
    assert (tmp_path / "tabel_rq4.md").exists()
    assert rows[0]["variant"] == "Kami-penuh"
