# Rewrite Kesenjangan + Kontribusi (paper, new positioning)

Status: ready-for-agent
Difficulty: medium
Depends: —

## Spec (writer)

Rewrite the paper's gap and contribution framing per `project_brief_v2.md` §1, §2, §7.

- **Kill the old "penggabungan/intersection" framing** (the judge scored novelty low because of it).
- State the **real new problem**: keeping reasoning **grounded while the token budget is cut**; efficient-
  reasoning methods optimize accuracy and are **blind to grounding**.
- **Keep the honesty hedge** — do not claim time-series reasoning is untouched; claim the sharper gap
  (grounding under a token budget is unsolved; a verified Indonesian TS-reasoning dataset does not exist)
  (brief v2 §7).
- **Do not** lean on the unverified "VeriTime is expensive" claim as the differentiator; the contribution
  stands on the RQ2 finding + the dataset.

Follow `.claude/agents/writer.md` (binding): official title only (**never** "GEAR-TS"), passive voice
("diusulkan"), numeric citations `[n]` at clause end. Where F6-02 has not yet confirmed a citation, leave a
`TODO(cite)` marker — do not assert an unverified reference.

## Acceptance

- Revised Kesenjangan + Kontribusi drafted into the makalah (or a section draft under `paper/`).
- No "GEAR-TS" in prose; positioning matches brief v2.
- Unverified citations flagged, not asserted.

## Comments
