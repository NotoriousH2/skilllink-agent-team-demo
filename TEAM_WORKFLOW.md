# SkillLink Public Agent-Team Workflow

This repository demonstrates a gated, sequential AI development team rather than an uncontrolled agent swarm.

| Stage | Branch owner | Expected PR | Reviewer/gate |
|---|---|---|---|
| Contract | Nari | SPEC + acceptance report | Coco |
| Product | Kongyi | source + worker tests + smoke | Bori, then Coco |
| Independent QA | Bori | QA evidence only | Coco |
| Docs/release | Dori | README + changelog + release report | Coco |

## Rules

- Each stage starts from the latest merged `main`.
- Each profile commits with its own Git author identity.
- Every branch is pushed and opened as a pull request.
- The implementation author is not the only verifier.
- CI and exact local command evidence are required before merge.
- Product code may not be modified by Bori or Dori.
- Coco records any intervention and owns final merge decisions.
- One shared GitHub login is used; formal GitHub self-approval is impossible, so review comments plus CI/merge gates are the auditable substitute.
