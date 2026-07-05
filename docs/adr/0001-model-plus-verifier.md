# ADR-0001: Model + external verifier over a monolithic LLM

**Status:** Accepted (2026-07-04, re-scoped to GEAR-TS 2026-07-05)

## Context

The system produces reasoning over time series that must be *accountable* — a decision-maker in a high-stakes
domain (health, finance) must be able to check each step before acting. LLMs are unreliable at multi-step
arithmetic over raw numbers and, asked to reason end-to-end, fall back on language patterns and hallucinate
trends, locations, and magnitudes (`project_brief.md` §2.2, §8). A single model gives no independent check.

## Decision

Two separate components with an explicit interface, not one end-to-end model:

1. **Komponen model** — a fine-tuned LLM (Qwen2.5-7B class) that reads a series + question and emits reasoning
   as a sequence of **operations** (not free prose).
2. **Komponen program** — a deterministic verifier (NumPy, untrained) that re-executes each operation on the
   original series and checks the claimed number (see ADR-0002).

The model reasons; the program corrects. They are separate objects that work together — the program is **not**
injected into the model.

## Consequences

- Every reasoning step is independently auditable, which is what makes grounding measurable (`project_brief.md` §14).
- Error is contained: a wrong claimed number is caught by the verifier rather than propagating silently.
- A monolithic-LLM baseline (free-prose reasoning) is still built, but only as the RQ2/RQ5 comparison, never
  as the product.
- The interface between components is the JSONL reasoning schema (`src/gearts/schema.py`); changing the
  operation set or step shape is a cross-cutting event and needs an ADR.
