# Issue tracker: Local Markdown

Issues and PRDs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Implementation issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- **Difficulty is recorded as a `Difficulty:` line directly under `Status:`** — one of `easy | medium | hard`. This is the routing key for sub-agents (see `workflow.md`): easy → `scout`/`data-qa`, medium → `builder`/`writer`, hard → `researcher`.
- Comments and conversation history append to the bottom of the file under a `## Comments` heading
- **The master index across all features is `.scratch/BOARD.md`** — the ordered task list (awal→akhir) with each issue's `Difficulty:`, `Depends:` (issue IDs that must be done first), and readiness. A new session reads it first, then picks a `ready-for-agent` issue whose `Depends:` are all satisfied. Issues also carry a `Depends:` line (below `Difficulty:`); use `—` when nothing blocks them.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed). Set both `Status:` and `Difficulty:` — if difficulty is unclear, default to `medium` and note why in the body.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.
