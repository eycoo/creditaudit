# ADR-0001: Modular pipeline over monolithic VLM

**Status:** Accepted (2026-07-04)

## Context

The system produces audited cost figures for credit offers. Those figures must be accountable — a regulator or consumer must be able to trace how a number was produced. LLMs/VLMs are unreliable at multi-step arithmetic, and a monolithic image→answer model gives no per-step audit trail. (`project_brief.md` §7, §10.)

## Decision

Four sequential modules with explicit interfaces, not one end-to-end model:

1. **M1 Perception** — VLM (Qwen2.5-VL-7B) extracts a fixed-schema JSON of financial terms from the offer image (constrained decoding).
2. **M2 Quantitative Reasoning** — fine-tuned reasoning model emits a calculation plan; a deterministic Python calculator executes it (see ADR-0002).
3. **M3 Classification & Compliance** — learned classifier for misleading labels (P1–P6, R1); **untrained rule engine** for OJK compliance flags.
4. **M4 Explanation** — same reasoning model verbalizes results, grounded to calculator output.

## Consequences

- Each module gets its own metrics (brief §13) and can be debugged/ablated independently.
- Error propagates forward (bad extraction poisons everything downstream) — mitigated by confidence gating and OCR fallback (brief §15).
- A monolithic VLM baseline is still built, but only as the RQ5 comparison, never as the product.
- Interfaces between modules are JSON with the schema in `src/creditaudit/schema.py`; changing that schema is a cross-module event and needs an ADR.
