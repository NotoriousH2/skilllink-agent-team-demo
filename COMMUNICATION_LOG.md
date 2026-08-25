# SkillLink Public Multi-Agent Communication Log

This log is maintained by Coco and records the real named-profile, Git, GitHub PR, review, CI, correction, and merge evidence for the public Golden Demo.

## Runtime and attribution model

- Public repository: <https://github.com/NotoriousH2/skilllink-agent-team-demo>
- Named profiles: Nari, Kongyi, Bori, Dori; Coco is orchestrator and merge gate.
- Local model runtime: shared llama.cpp Qwen3.8 endpoint; profile calls were sequential.
- Persistent tmux evidence:
  - `skilllink_public_nari`
  - `skilllink_public_kongyi`
  - `skilllink_public_bori_review`
  - `skilllink_public_dori`
- GitHub authentication: every profile uses the same owner login, `NotoriousH2`.
- Consequence: GitHub rejects formal self-approval. Reviews are therefore submitted as COMMENTED reviews whose bodies explicitly state `ACCEPT`, `CHANGES REQUESTED`, or the merge gate verdict; CI checks and merge commits complete the audit trail.
- Intended Git attribution rule: every role commit uses a role-specific author identity. One exception occurred on Nari’s correction head and is documented below.

## Bootstrap — Coco

- Initial main commit: `3a713a4` — `chore: bootstrap public multi-agent workflow`.
- Added the project brief, team workflow, communication-log skeleton, `.gitignore`, and GitHub Actions workflow.
- Created the public repository and pushed `main`.
- The product implementation was intentionally absent from bootstrap main.

## Infrastructure correction — PR #2

- PR: <https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/2>
- Branch: `ci/fix-bootstrap-workflow`
- Head: `453fd8d121de2194ec93be8748d95f8854523185`
- Root cause: the bootstrap workflow used `hashFiles()` in an unsupported job-level condition, so GitHub rejected the workflow before creating jobs.
- Correction: detect `pyproject.toml` after checkout and condition implementation-only steps on that output.
- GitHub Actions: `contract` PASS, `quality` PASS.
- Coco COMMENTED review: ACCEPT.
- Merge: `414214e733bcd53f50b9676b94d44a48b68d2032`.

## Nari contract stage — PR #1

- Real profile/tmux: Nari in `skilllink_public_nari`.
- PR: <https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/1>
- Branch: `agent/nari-spec`
- Initial Nari commit: `4dee1352d5f5007a24d97054c2e2ae4a644d9367`, author `Nari Spec Critic <nari@notolab.local>`.
- Outputs: `SPEC.md`, `agent_reports/NARI_SPEC_REPORT.md`.
- Initial self-check: exact two-file scope and `git diff --check` clean.

### Coco contract review and repair loop

- Coco posted CHANGES REQUESTED because matched-listing cancellation was owner-only in the permissions/route contract but owner-or-accepted-applicant in the transition table.
- The same Nari tmux/session lineage corrected the contract to owner-only everywhere: permissions, transition, route, conditional button, and mandatory tests.
- Correction head: `b438d9ed3c7905b74f064b99cfbba012b9133896`.
- Attribution caveat: this correction was executed in the persistent Nari session, but shared repository-local Git identity had been changed by a worktree operation, so the commit author was recorded as `Coco Orchestrator <coco@notolab.local>`. This is preserved rather than rewritten.
- Mitigation for later stages: every commit uses per-command `git -c user.name=... -c user.email=... commit`.
- GitHub Actions on corrected head: `contract` PASS, `quality` PASS.
- Coco re-review: ACCEPT.
- Merge: `5c2c610a68c069a4a2a9f03b656a10ce9cefa0bc`.

## Kongyi implementation stage — PR #3

- Real profile/tmux: Kongyi in `skilllink_public_kongyi`.
- PR: <https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/3>
- Branch: `agent/kongyi-implementation`
- Commits:
  - `61bdad4ec7c6aef7ca9a70921aec8fdc8c082ab5` — implementation
  - `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3` — implementation report
- Author: `Kongyi Implementation Worker <kongyi@notolab.local>`.
- Scope: 26 SPEC-allowlisted files; no contract, workflow, communication log, docs, or other-agent report modification.
- Kongyi verification: compile, lint, format-check, 31 pytest tests, golden smoke, and diff check all passed.
- GitHub Actions on exact head: `contract` PASS, `quality` PASS (run `32790474265`).

## Bori independent review of PR #3

- Real profile/tmux: Bori in `skilllink_public_bori_review`.
- Review: <https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/3#pullrequestreview-5013684887>
- Bori remained read-only in the repository.
- Independently reproduced all seven deterministic commands: 31 tests, golden smoke, lint/format/compile/diff all PASS.
- Executed approximately 150 assertions across six fresh temporary-DB sessions covering seed exactness, status-code order, permissions, transitions, duplicate/matched rules, filtering, XSS, activity/admin, DB isolation, cookie contract, and validation boundaries.
- Static security findings: no Jinja `|safe`, unsafe DOM sinks, hard-coded credentials, external product network dependency, unparameterized SQL, or committed DB/secret artifacts.
- Probe-side anomalies were re-run on fresh DBs and recorded separately from product defects.
- Bori verdict: ACCEPT on exact implementation head `84b2af7...`.

## Coco browser and merge gate for PR #3

- Fresh temporary DB and live uvicorn server.
- Playwright result: `COCO_BROWSER_PR3_PASS`.
- Covered: 8-card home, study filter, 390px one-column/no horizontal scroll, user switch, apply, owner accept, matched UI, Korean 404, and stored-XSS text rendering.
- Screenshots: five external evidence files; they are not committed to the repository.
- Unexpected console/page errors: zero. The expected top-level 404 resource message was isolated after the 404 status/UI assertion.
- Coco COMMENTED review: ACCEPT FOR MERGE.
- Merge: `5d70abacd26a26aa3e7defc7bf55f068f5522ea2`.
- Main push CI run `32792204444`: success.

## Bori QA evidence stage — PR #4

- Real profile/tmux: continued Bori lineage in `skilllink_public_bori_review`.
- PR: <https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/4>
- Branch: `agent/bori-qa`
- Commit: `7ec4d486018afad33a00b1051678f2425c50e539`
- Author: `Bori Independent QA <bori@notolab.local>`.
- Only output: `agent_reports/BORI_QA_REPORT.md`.
- Report separates Bori-owned deterministic/probe evidence from Coco-owned browser evidence.
- GitHub Actions: `contract` PASS, `quality` PASS.
- Coco review: ACCEPT.
- Merge: `7e3272e8bc72ec909fbf672352e6d85ca4d6281c`.

## Dori documentation/release stage — PR #5

- Real profile/tmux: Dori in `skilllink_public_dori`.
- PR: <https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/5>
- Branch: `agent/dori-docs`
- Outputs only: `README.md`, `CHANGELOG.md`, `agent_reports/DORI_RELEASE_REPORT.md`.
- Commits, all authored `Dori Documentation Release <dori@notolab.local>`:
  - `4d7d411f17902cdfa1a24b45e9e2cae713f28651` — initial docs
  - `21e4a35e7db2e2e550e9ea5d5aa9f53f88db37f2` — runtime/access/attribution corrections
  - `690a448773af54f3fa3e540ec6faf3f05493066b` — final role-attribution qualification

### Coco documentation review loops

- First CHANGES REQUESTED:
  1. remove false `SKILLLINK_PORT` instruction and show a truthful uvicorn `--port` command;
  2. correct operator GET wording because `/activity` is 403;
  3. separate PR #1 stage ownership from the correction-head commit author.
- Re-review found one remaining unqualified generic author-attribution claim.
- The same Dori session corrected it and recorded both review rounds in the release report.
- Final head CI: `contract` PASS, `quality` PASS.
- Coco final review: ACCEPT FOR MERGE.
- Merge: `717f38b651242f4c05ceb62ca68190ab277087b0`.

## Non-blocking findings carried forward

- F1: CSS breakpoint values are `1024px`/`600px` while the spec names `768px`/`390px`; observable acceptance at 768px and 390px passes.
- F2: Jinja environment construction works but is less conventional than passing the environment directly.
- F3: schema DDL is duplicated and one copy is unused.
- Concurrent-write safety and production deployment are explicit non-goals.
- Formal GitHub APPROVE remains unavailable while all profiles share one owner login.

## Final acceptance rule

The public demo is complete only after this Coco-owned audit log is reviewed and merged, final main CI is green on the exact final SHA, deterministic local checks pass, the live browser gate remains reproducible, the repository is public, all named PRs are merged, and the final Git working tree is clean.
