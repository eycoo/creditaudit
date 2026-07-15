# Verify all citations

Status: ready-for-agent
Difficulty: easy
Depends: —

## Spec (scout + web)

Confirm every cited work **actually exists** and record its exact author / year / venue / arXiv-or-DOI.

**Priority (highest risk first):**
1. **VeriTime** — the draft cites `arXiv:2602.07830` with **no authors**. Verify it, or flag it as
   unfindable. It is the main baseline; a fake reference here sinks the paper.
2. **SelfBudgeter** (token-budget comparator).
3. **MTBench** (framing).

**Then the adopted-method citations** for Metodologi (F6-03):
- QLoRA (Dettmers et al.), LoRA (Hu et al.)
- Chain-of-Thought (Wei et al.)
- program-aided / verifier line: PAL, Program-of-Thoughts, Toolformer, GSM8K "Training Verifiers…" (Cobbe
  et al.), "Let's Verify Step by Step" (Lightman et al.), deductive / Natural-Program verification (Ling et al.)
- LLM-for-time-series: Time-LLM (Jin et al.), LLMTime (Gruver et al.)
- Qwen2.5 technical report

## Constraint

**Do not fabricate.** Any work that cannot be found is marked `not-found` — never invented. Do not guess
author/year/arXiv to fill a gap.

## Acceptance

- A bib table `key | full citation | status (confirmed / needs-check / not-found)` written to
  `paper/referensi.md` (or `.scratch/fase-6-paper/sitasi.md`).
- VeriTime resolved to a real reference **or** explicitly flagged unfindable with a recommendation
  (drop it / replace it / relabel as an honest proxy).

## Comments
