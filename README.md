# Peningkatan Keandalan dan Efisiensi Token LLM pada Data Time Series melalui Pendekatan Verifikasi Deterministik

Research project: make an LLM reason over a numeric **time series** in a way that is **grounded** (every step's number survives recomputation) and **token-efficient** (reasoning length adapts to difficulty). The LLM emits reasoning as a sequence of *operations*; a **deterministic verifier** re-runs each operation on the original series and scores how many claimed numbers actually check out. Full proposal: [`project_brief.md`](project_brief.md) (Indonesian).

Two contributions (`project_brief.md` §5): a **verified TS-reasoning dataset** (JSONL, from real Indonesian public sources) and the **model + verifier** method. Main metric: **grounding score**.

## Quickstart

```bash
pip install numpy pytest
pytest                # Phase-1 seed tests (operations, verifier, schema)
```

The grounding metric in action:

```python
from gearts.schema import Sample
from gearts.verifier import verify_sample

sample = Sample.from_dict({...})       # a Lampiran-A JSONL row
print(verify_sample(sample)["grounding_score"])   # honest reasoning -> 100.0
```

## Layout

| Path | What |
|---|---|
| `src/gearts/` | Phase-1 code: JSONL `schema`, `operations` library, deterministic `verifier`, `metrics` |
| `tests/` | Tests keyed to the brief's worked example (Lampiran B) + hallucination case (Lampiran D) |
| `data/` | `raw` (scraped series, gitignored), `synthetic`, `processed` |
| `experiments/` | Per-run configs + results |
| `notebooks/` | Colab/Kaggle training notebooks |
| `docs/agents/` | Agent workflow: issue tracker, triage labels, sub-agent routing, memory rules |
| `docs/adr/` | Architecture decision records |
| `docs/lab-notebook/` | Dated experiment/investigation entries |
| `.scratch/` | Local markdown issue tracker |
| `CONTEXT.md` | Domain glossary (ubiquitous language) |

## Working on this repo

The agent workflow (skills → sub-agents by difficulty) is in [`docs/agents/workflow.md`](docs/agents/workflow.md). Start design with `/grill-me`, break work down with `/to-prd` → `/to-issues`, implement via `/tdd`, review with `/review`.
