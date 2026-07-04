# creditaudit — Deteksi Multimodal Penyesatan Biaya Kredit Digital

Research project: a multimodal system that audits Indonesian digital-credit offers (pinjol, paylater, installment tables) to compute the **true effective cost** and detect **misleading fee framing**, checked against OJK regulation. Full proposal: [`project_brief.md`](project_brief.md) (Indonesian).

## Quickstart

```bash
pip install pytest
pytest                # runs the Phase-1 seed tests (schema, calculator, rule engine)
```

## Layout

| Path | What |
|---|---|
| `src/creditaudit/` | Phase-1 code: extraction schema, deterministic cost calculator, OJK rule engine |
| `tests/` | Tests keyed to the brief's worked example (Lampiran B) |
| `data/` | `raw` (scraped, gitignored), `synthetic`, `processed`, `templates` (render bank, versioned) |
| `experiments/` | Per-run configs + results |
| `notebooks/` | Colab/Kaggle training notebooks |
| `docs/agents/` | Agent workflow: issue tracker, triage labels, sub-agent routing, memory rules |
| `docs/adr/` | Architecture decision records |
| `docs/lab-notebook/` | Dated experiment/investigation entries |
| `.scratch/` | Local markdown issue tracker |
| `CONTEXT.md` | Domain glossary (ubiquitous language) |

## Working on this repo

The agent workflow (skills → sub-agents by difficulty) is documented in [`docs/agents/workflow.md`](docs/agents/workflow.md). Start any design work with `/grill-me`, break work down with `/to-prd` → `/to-issues`, implement via `/tdd`, review with `/review`.
