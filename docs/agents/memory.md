# Agent Memory System

Where knowledge goes so it survives sessions. Project memory lives **in the repo** (versioned, shareable, survives any agent); Claude's harness memory is only for personal/user preferences.

## Routing table

| Kind of knowledge | Destination | Format |
|---|---|---|
| Architectural / irreversible decision | `docs/adr/NNNN-<slug>.md` | Status, Context, Decision, Consequences. Numbered sequentially. |
| Experiment or investigation outcome | `docs/lab-notebook/YYYY-MM-DD-<slug>.md` | Hypothesis → Setup → Result → Conclusion → Next. Reference W&B run IDs; never duplicate metrics tables that live in `experiments/`. |
| New/changed domain term | `CONTEXT.md` | Add to the right glossary table; if a term is being *avoided*, say so in "Terms to avoid". |
| Work to do | `.scratch/` issue tracker | See `issue-tracker.md`. Never leave TODOs in prose — file an issue. |
| Session continuity | `/handoff` skill at session end | Writes to OS temp for the next session. Anything durable in it must ALSO land in one of the rows above — handoffs are transport, not storage. |
| User preferences, personal workflow notes | Claude harness memory (`~/.claude/projects/.../memory/`) | Never project facts — those belong in-repo. |

## Rules

1. **One fact, one home.** Before writing, check whether the fact already lives somewhere; update in place rather than duplicating. Wrong memories get deleted, not annotated.
2. **Experiments are append-only.** Never rewrite a lab-notebook entry to make a past result look better; add a new entry that supersedes it and link back.
3. **ADRs are immutable once accepted.** Reversing a decision = new ADR that says "supersedes ADR-NNNN".
4. **Every sub-agent reads before it writes.** `CONTEXT.md` first, then ADRs touching its area (see `domain.md`). Sub-agent outputs that contain durable knowledge must say where it was recorded.
5. **Convert relative dates to absolute** in every memory artifact (e.g., "July 2026", not "next month").
