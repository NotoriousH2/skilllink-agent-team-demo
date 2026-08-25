# Bori Independent QA Report — PR #3 (SkillLink Marketplace Contract)

- Reviewer: Bori (independent read-only verifier, local llama.cpp profile)
- Date: 2026-08-25 (KST)
- Verdict: **ACCEPT**

## 1. Target SHA and merge evidence

| Item | Value |
|---|---|
| Implementation head SHA (PR #3) | `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3` |
| PR #3 merge commit on `main` | `5d70abacd26a26aa3e7defc7bf55f068f5522ea2` |
| PR #3 state | MERGED at 2026-08-25T00:05:42Z |
| PR #3 URL | https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/3 |
| Bori review (COMMENTED, ACCEPT) | https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/3#pullrequestreview-5013684887 (review id 5013684887) |
| Coco browser gate | `COCO_BROWSER_PR3_PASS` — orchestrator-owned external evidence (see §7) |

Local `main` after `git pull origin main` is at `5d70abacd26a26aa3e7defc7bf55f068f5522ea2`;
`git merge-base --is-ancestor 84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3 HEAD` → yes.

## 2. Deterministic evidence — seven local verification commands

All executed on merged `main` (`5d70abacd26a26aa3e7defc7bf55f068f5522ea2`), working tree clean.

| # | Command | Observed result | Exit |
|---|---|---|---|
| 1 | `uv sync --locked --group dev` | `Resolved 28 packages in 1ms` / `Checked 25 packages in 0.34ms` | 0 |
| 2 | `uv run python -m compileall app scripts tests` | clean compile | 0 |
| 3 | `uv run ruff check app scripts tests` | `All checks passed!` | 0 |
| 4 | `uv run ruff format --check app scripts tests` | `14 files already formatted` | 0 |
| 5 | `uv run pytest -q` | `31 passed in 0.61s` | 0 |
| 6 | `uv run python scripts/golden_smoke.py` | `GOLDEN SMOKE PASS` | 0 |
| 7 | `git diff --check` | clean | 0 |

## 3. GitHub Actions runs (exact SHA)

| Run | SHA | Conclusion |
|---|---|---|
| PR #3 head run `32790474265` | `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3` | success — `contract` pass, `quality` pass |
| Merge push run `32792204444` | `5d70abacd26a26aa3e7defc7bf55f068f5522ea2` | success |

## 4. Allowlist and tracked-artifact inspection

- `git diff --name-status main...HEAD` (at review time) → 26 added files, all within SPEC §12 allowlist:
  `pyproject.toml`, `uv.lock`, `app/*` (6), `templates/*.html` (7), `static/css/main.css`, `static/js/app.js`,
  `scripts/golden_smoke.py`, `tests/*` (7), `agent_reports/KONGYI_IMPLEMENTATION_REPORT.md`.
- Forbidden files untouched: `PROJECT_BRIEF.md`, `SPEC.md`, `.github/**`, `README.md`, `CHANGELOG.md`, other agents' reports.
- `git ls-files` → no `*.db` / `*.sqlite` / `.env` committed.

## 5. Static security findings

- Jinja `|safe`: 0 occurrences in `templates/` and `app/`; `app/routes.py:19-24` builds `jinja2.Environment(autoescape=True)` and assigns to `templates.env`.
- `innerHTML` / `outerHTML` / `document.write` / `eval(`: 0 occurrences in `static/js/app.js`.
- Hard-coded credentials/tokens: none in tracked files.
- External network/CDN: none in product code (only `http://127.0.0.1:8322` in `scripts/golden_smoke.py`, local smoke server per SPEC §10.2).
- SQL: all queries use `?` parameter binding; the only string-built SQL (`app/routes.py:81` count query) reuses the same parameterized WHERE clause — no user-input interpolation.
- Connection lifetime: every route handler and `init_db()` wraps `connect()` in `try/finally: conn.close()` (all 12 mutation/query functions inspected).

## 6. Independent fresh-DB probes

Scope: ~150 assertions across six fresh-DB TestClient sessions (each session: new temp DB via `SKILLLINK_DB`, no reliance on Kongyi's tests).

Verified behavior:
- Seed exactness (SPEC §3): users 4 / listings 8 / applications 3, every row value matches SPEC tables; idempotent re-seed.
- Status-code order 404→403→409→422 per route, including ordering cases.
- Self-apply 403; operator all POSTs 403; operator `/admin` 200, user `/admin` 403, operator `/activity` 403.
- Pending duplicate 409 (L4); matched listing apply 409 (L3); accept → sibling pending rejected + listing matched (L2, DB-verified); matched cancel owner-only; terminal transitions 409.
- Literal filter/search cases (category/type/status/q, q>200 → 422, bad enum → 422, page=0/abc → 422, empty page → 200 + message).
- XSS (SPEC §8): raw `<script>` / `<img onerror>` stored raw in DB, rendered escaped in detail/home/application views.
- Activity/admin visibility and counts; DB env isolation (SPEC §4); cookie contract (`HttpOnly; SameSite=lax; Max-Age=2592000`); conditional buttons (SPEC §7.4); validation boundaries (title 1~80, description 1~1000, message 1~500).

Probe anomalies (all resolved as probe-side errors, not product defects):
1. Pagination nav absent in one session — probe card-count assumption wrong; `app/routes.py:83` + `templates/home.html:41` logic correct; empty-page case passed directly.
2. Admin "진행 중: 5" missing — probe had already created 4 open listings before reading `/admin`; fresh-DB re-run confirmed 5/1/1/1.
3. A few 403-vs-409 mismatches — probe-side actor/state tracking errors after earlier mutations in the same DB; fresh-DB re-runs matched SPEC §5.1/§6.

## 7. Browser evidence boundary

- Coco browser gate: `COCO_BROWSER_PR3_PASS` (five screenshots, zero unexpected console/page errors) is **orchestrator-owned external evidence**.
- **Bori did not run the browser gate.** Bori's browser-related verification is source inspection only (CSS grid/breakpoints, badge colors, no external CDN).

## 8. Non-blocking findings

- **F1 (minor, SPEC §9)**: `static/css/main.css:60-66` breakpoints are `1024px`/`600px`; SPEC §9 names `768px`/`390px`. Observable outcomes at the SPEC's named widths still hold (768px → 2-col, 390px → 1-col), so no contract violation of testable acceptance criteria; recommend aligning breakpoint values in a follow-up.
- **F2 (info)**: `app/routes.py:19-24` creates a standalone `Environment` and reassigns `templates.env`; works, but `Jinja2Templates(directory=..., env=...)`-style construction would be less surprising.
- **F3 (info)**: `app/seed.py` duplicates the DDL string (also in `app/db.py:SCHEMA`, unused). Cosmetic.

## 9. Limitations

- Browser manual verification (SPEC §9.1–9.6) not performed by Bori (no browser in this environment); covered by Coco gate (§7) and source inspection.
- Single shared GitHub login: formal APPROVE not possible; Bori's review is COMMENTED with explicit ACCEPT in body.
- Concurrent-write safety is a declared non-goal (SPEC §1.1).

## 10. Final verdict

**ACCEPT** — at implementation head `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3` and merge commit `5d70abacd26a26aa3e7defc7bf55f068f5522ea2`:
all seven mandatory local commands exit 0 (independently reproduced on merged `main`), GitHub CI green on both exact SHAs,
allowlist clean, security scan clean, ~150 independent fresh-DB probes confirm the SPEC §2–§8 contract.
Only non-blocking observation: CSS breakpoint values (F1).
