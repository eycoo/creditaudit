"""Harness tests — the evaluation pipeline every experiment runs through.

A model adapter emits reasoning + answer; the harness re-verifies that reasoning
against the ORIGINAL series (never trusting the model's arithmetic), then reports
the three metrics per model plus the per-item (tokens, grounding, accuracy)
records the RQ2 curve consumes.
"""
from gearts.harness import MockModel, curve_records, metrics_table, run_model
from gearts.schema import Sample

# tiny benchmark: one series, honest gold answer "outbreak"
_S1 = {
    "id": "dbd_001",
    "series": {"nama": "kasus_dbd", "satuan": "kasus", "freq": "mingguan",
               "nilai": [12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78]},
    "konteks": "16 minggu",
    "pertanyaan": "Apakah ada outbreak?",
    "reasoning": [],  # benchmark carries no reasoning; the model supplies it
    "jawaban": {"label": "outbreak", "keyakinan": "tinggi"},
}
BENCH = [Sample.from_dict(_S1)]

# honest reasoning: every step recomputes correctly on the series
_HONEST_STEPS = [
    {"langkah": 1, "operasi": "rata2(nilai[0:5])", "hasil": 13.0, "teks": "baseline 13"},
    {"langkah": 2, "operasi": "persen_naik(nilai[11]->nilai[15])", "hasil": 105.3, "teks": "naik 105%"},
    {"langkah": 3, "operasi": "rasio(nilai[15], 13.0)", "hasil": 6.0, "teks": "6x baseline"},
]


def _honest_model():
    return MockModel("honest", {"dbd_001": (_HONEST_STEPS, "outbreak")})


def _hallucinating_model():
    # step 2 claims +30% where the series rose +105% -> ungrounded; wrong answer too
    steps = [dict(s) for s in _HONEST_STEPS]
    steps[1] = {**steps[1], "hasil": 30.0}
    return MockModel("halu", {"dbd_001": (steps, "stabil")})


def test_perfect_model_scores_full():
    r = run_model(_honest_model(), BENCH)
    assert r.model == "honest"
    assert r.answer_accuracy == 100.0
    assert r.mean_grounding == 100.0
    assert r.mean_tokens > 0
    assert len(r.items) == 1
    assert r.items[0].correct is True
    assert r.items[0].grounding == 100.0


def test_hallucinating_model_flagged():
    r = run_model(_hallucinating_model(), BENCH)
    assert r.answer_accuracy == 0.0          # predicted "stabil" != gold "outbreak"
    assert round(r.mean_grounding, 1) == 66.7  # 2 of 3 steps ground
    assert r.items[0].correct is False
    assert r.items[0].jawaban_pred == "stabil"
    assert r.items[0].jawaban_gold == "outbreak"


def test_verifies_against_original_series_not_model_claim():
    # model answer is right but arithmetic is fabricated -> accuracy up, grounding down
    r = run_model(_hallucinating_model(), BENCH)
    assert r.items[0].grounding < 100.0


def test_curve_records_are_per_item_triples():
    r = run_model(_honest_model(), BENCH)
    recs = curve_records(r)
    assert len(recs) == len(r.items)
    tokens, grounding, accuracy = recs[0]
    assert tokens == r.items[0].tokens
    assert grounding == 100.0
    assert accuracy == 1.0


def test_metrics_table_one_row_per_model():
    results = [run_model(_honest_model(), BENCH), run_model(_hallucinating_model(), BENCH)]
    table = metrics_table(results)
    assert [row["model"] for row in table] == ["honest", "halu"]
    assert table[0]["answer_accuracy"] == 100.0
    assert set(table[0]) >= {"model", "answer_accuracy", "mean_grounding", "mean_tokens", "n"}


def test_empty_benchmark_is_zeroed():
    r = run_model(_honest_model(), [])
    assert r.answer_accuracy == 0.0
    assert r.mean_grounding == 0.0
    assert r.mean_tokens == 0.0
    assert r.items == []
