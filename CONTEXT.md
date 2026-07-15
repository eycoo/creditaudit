# CONTEXT.md — Domain Glossary

Ubiquitous language for GEAR-TS. Use these exact terms in issues, tests, ADRs, and code. Indonesian terms are canonical (they key into the JSONL schema and the brief); English descriptions for clarity.

## Core concepts

| Term | Meaning |
|---|---|
| **time series / deret** | Ordered sequence of numeric values over time — the system's input unit |
| **reasoning grounded** | Each reasoning step's claimed number is backed by an actual computation over the series, not a language guess |
| **verifikator deterministik** | The external program (NumPy, untrained) that re-runs each operation on the original series and checks the claimed number. Single source of grounding truth (`src/gearts/verifier.py`) |
| **grounding score** | Main metric: % of reasoning steps whose numbers survive recomputation within tolerance. Deterministic — never an LLM judge |
| **operasi** | An operation from the fixed library (below); reasoning steps must use these so each is re-executable |
| **reasoning adaptif** | Reasoning length allocated by difficulty — clear series get short reasoning, ambiguous series get long. The token-efficiency mechanism |
| **efisiensi token** | Average reasoning tokens per sample, reported alongside accuracy so the tradeoff is visible |
| **program-of-thought** | The model emits an operation plan; the verifier executes/checks it. The model never owns the arithmetic (ADR-0002) |

## JSONL schema fields (Lampiran A — names are law, see `src/gearts/schema.py`)

| Field | Meaning |
|---|---|
| **series.nama / satuan / freq / nilai** | Series name, unit, frequency (`harian`/`mingguan`/`bulanan`/`tahunan`/`jam`), and the numeric values |
| **konteks** | Short natural-language description of the series |
| **pertanyaan** | The reasoning question asked of the series |
| **reasoning[].langkah / operasi / hasil / teks** | Step index, the operation string, the claimed numeric result, and the plain-language gloss |
| **jawaban.label / keyakinan** | Final answer label and confidence (`rendah`/`sedang`/`tinggi`) |

## Operation library (Lampiran C — `src/gearts/operations.py`, semantics finalized ADR-0003)

| Operation | Semantics | `hasil` shape | Grounding |
|---|---|---|---|
| **rata2** | mean of a range | scalar | tolerance |
| **delta** | `b − a` | scalar | tolerance |
| **persen_naik** | `(b−a)/a·100` | scalar | tolerance |
| **rasio** | `a/b` | scalar | tolerance |
| **slope** | linear-trend slope over a range | scalar | tolerance |
| **min / max** | extreme value over a range | scalar | tolerance |
| **z_score** | `(x−mean(pop))/std(pop)`, `ddof=0` (population std, not sample). `pop` = **explicit argument if given, else the whole series** — pass an explicit baseline window (e.g. `z_score(nilai[15], nilai[0:8])`) on a trending series; whole-series default is for roughly stationary series | scalar | tolerance |
| **deteksi_anomali** | `\|z\|>ambang` over the **whole series** (not rolling), **two-sided**, `ddof=0` — matches `z_score`. Direction (upward-only outbreak framing) is expressed in the *question*, not the primitive | `list[int]`, sorted 0-based indices into `nilai` | non-scalar — F1-05 (index-set exact match at clean, Jaccard at eval) |
| **bandingkan_segmen** | `mean(r2) − mean(r1)`, absolute difference only. Percent/ratio between segments is expressed by **composition**: `rata2` each segment, then `persen_naik`/`rasio` on the two `langkah{N}` bindings — not a separate op | scalar | tolerance |

**Composite steps** reference a prior step's scalar result as `langkah{N}` (N = that step's `langkah` index),
e.g. `rasio(nilai[15], langkah1)` — not a free name like `baseline`. Only **scalar**-returning steps are
bindable; a step may only reference `langkah{N}` for `N` less than its own index (no forward references).

Operation-string forms: `rata2(nilai[0:5])`, `persen_naik(nilai[11]->nilai[15])`, `rasio(nilai[15], langkah1)`.

## Reasoning tasks (scope — `project_brief.md` §6)

Anomaly/outbreak indication · trend characterization · segment comparison · explanation. Univariate and simple multivariate series.

## Architecture (see `docs/adr/`)

| Term | Meaning |
|---|---|
| **komponen model** | The fine-tuned LLM (Qwen2.5-7B class) that emits operation-form reasoning |
| **komponen program** | The deterministic verifier — used at dataset cleaning, evaluation, and optional RL reward |
| **grounding tolerance** | A step grounds if `|recomputed − claimed| ≤ max(abs_tol, rel_tol·|recomputed|)`. Relative term lets a rounded 105.3 pass while a 30-vs-105 error fails. A calibration knob (`verifier.verify_sample`) |

## Terms to avoid

- Don't say **forecasting** — predicting future values is out of scope; the task is *reasoning over* an existing series.
- Don't call grounding an "estimate" or an "LLM check" — it is deterministic recomputation.
- Don't say "the model computes" — the model *proposes* operations; the *verifier* computes (ADR-0002).
