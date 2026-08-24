# SkillLink Golden Demo — Project Brief

## Product vision

SkillLink is a classroom-sized Korean neighborhood skill/help marketplace. It is a public, evidence-preserving demonstration of a real NotoLAB Hermes multi-agent development team.

## User story

A demo user can browse, search, filter, create, and edit listings; apply to another user's open listing; accept or reject received applications; and complete or cancel matched work through explicit state transitions.

## Required surface

- Korean responsive card marketplace UI.
- Four seeded demo users and eight seeded listings.
- Offer/request listing CRUD with search and category/type/status filters.
- Application submission and owner accept/reject actions.
- Activity and operator/admin views.
- Deterministic local startup, pytest suite, and non-zero-exit golden smoke.
- Safe rendering; stored XSS is a hard failure.

## Constraints

- Python 3.12, FastAPI, SQLite, Jinja2, local CSS, minimal vanilla JavaScript.
- No production authentication, payment, chat, maps, uploads, external API, CDN, or React/Node build.
- One primary branch owner at a time; no concurrent writers in one working tree.
- Agent completion claims are advisory until independently verified.

## Public GitHub process

1. **Nari** opens a specification PR.
2. **Coco** reviews and merges the accepted contract.
3. **Kongyi** opens an implementation PR with tests and smoke evidence.
4. **Bori** independently reviews the implementation PR; Coco runs the merge gate.
5. **Bori** opens a QA-evidence PR after implementation merge.
6. **Dori** opens a documentation/release PR using only verified facts.
7. **Coco** reviews, merges, and performs final acceptance.

All profiles use one GitHub account in this teaching environment, so GitHub cannot record a formal self-approval. Review evidence is therefore posted as PR review comments and gate comments, while distinct commit authors, branches, CI checks, PRs, and merge commits preserve role attribution.

## Required artifacts

- `SPEC.md`
- `agent_reports/NARI_SPEC_REPORT.md`
- product source and worker-authored tests
- `scripts/golden_smoke.py`
- `agent_reports/KONGYI_IMPLEMENTATION_REPORT.md`
- `agent_reports/BORI_QA_REPORT.md`
- `README.md`, `CHANGELOG.md`, `agent_reports/DORI_RELEASE_REPORT.md`
- `COMMUNICATION_LOG.md` maintained by Coco

## Final acceptance

The demo passes only when the approved PR chain is merged, GitHub Actions is green on the final main SHA, deterministic local checks pass, browser/security flows pass, documentation matches the implementation, and the public repository exposes the branch/commit/PR/review history.
