# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

This is a **single-context repo**: one `CONTEXT.md` at the root, ADRs in `docs/adr/`.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root — the domain glossary (ubiquitous language). Indonesian domain terms are canonical.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in. ADR-0001 (modular pipeline) and ADR-0002 (program-of-thought + deterministic calculator) constrain almost all code in `src/`.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids (see its "Terms to avoid" section).

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/grill-with-docs`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0002 (deterministic calculator) — but worth reopening because…_
