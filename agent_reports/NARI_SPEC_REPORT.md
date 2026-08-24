# Nari Spec Report — SkillLink v1 계약 PR

- Stage: Contract (SPEC + acceptance report)
- Branch owner: Nari Spec Critic <nari@notolab.local>
- Branch: `agent/nari-spec` → `main`
- Branch 기반: `origin/main` (bootstrap 커밋 `3a713a4`)
- Date: 2026-08-25 (KST)

## 1. Sources read (읽은 소스)
1. `PROJECT_BRIEF.md` — product vision, user story, required surface,
   constraints, public GitHub process, final acceptance.
2. `TEAM_WORKFLOW.md` — stage/branch/PR matrix, one-writer rule, CI
   evidence requirement.
3. `COMMUNICATION_LOG.md` — bootstrap context, 단일 GitHub 계정 제약
   (형식적 self-approval 불가, 리뷰 코멘트 + CI 게이트 대체).
4. `.github/workflows/ci.yml` — 기존 CI 계약: `contract` job(bootstrap
   파일 존재 검증), `quality` job은 `pyproject.toml` 존재 시
   `uv sync --locked --group dev` / `compileall` / `ruff check` /
   `ruff format --check` / `pytest -q` / `scripts/golden_smoke.py`.
5. `.gitignore` — `*.db`, `.venv/`, `.pytest_cache/` 등 무시 항목 확인
   (DB 경로를 `data/skilllink.db`로 정하는 근거).
- `/home/notorioush2/skilllink`는 미열람(명령됨).

## 2. Ambiguities resolved (모호성 해결, SPEC 13절과 1:1)
1. "operator/admin views"의 actor 성격 미정 → users 테이블에 없는
   관측 전용 `operator` 페르소나를 cookie 값으로 정의(SPEC 5절).
2. 인증 없음 조건에서 "현재 사용자" 결정 방법 공백 →
   `current_user_id` cookie 데모 전환으로 확정(SPEC 5절).
3. matched/completed 시드 게시물이 필요하면 신청 데이터가 따라와야
   함(L2) → 시드에 applications 3행 포함 확정(SPEC 3.3).
4. 페이지당 개수 미지정 → 고정 10개, 쿼리 파라미터 미공개.
5. 상태코드 체계(404/403/409/422)와 검사 순서 공백 → 404→403→409→422
   순서로 확정(SPEC 5.1).
6. 정렬 기준 미지정 → `id DESC`(seed id와 생성 순서가 동일한 결정적
   선택, SPEC 13-6).

## 3. Risks (리스크)
- R1: 단일 GitHub 로그인 → 형식적 self-approval 불가. 완화: commit
  author(`Nari Spec Critic`) + branch + PR + 리뷰 코멘트로 역할 귀속
  보존(TEAM_WORKFLOW 규칙 준수).
- R2: 스펙과 구현 사이 "신청 id 추출" 같은 세부 동작의 해석 차이.
  완화: transition을 표 기반 table-driven 테스트 + smoke 단계로
  고정(SPEC 10).
- R3: Jinja2 autoescape 누락 시 stored XSS. 완화: 8절 hard failure
  계약 + pytest + smoke 이중 검증.
- R4: `uv.lock` 누락 시 CI `uv sync --locked` 실패. 완화: allowlist에
  `pyproject.toml`, `uv.lock` 명시(SPEC 12).
- R5: operator가 users 테이블에 없는 페르소나라는 점에서 permission
  검사 코드와 시드 코드에 혼동 가능. 완화: 5.1 permissions table이
  유일한 근거.

## 4. Self-checks (실행한 검증, exact)
- [x] `gh auth status` / `gh api user --jq .login` → `NotoriousH2`
  (토큰 값 미출력)
- [x] `git fetch origin && git checkout main && git pull origin main`
  → latest `origin/main`(`3a713a4`)
- [x] `git checkout -b agent/nari-spec`
- [x] repo-local identity: `git config user.name "Nari Spec Critic"`,
  `git config user.email "nari@notolab.local"`
- [x] 생성 파일은 `SPEC.md`, `agent_reports/NARI_SPEC_REPORT.md` 2개뿐
  (`git status --short`로 확인)
- [x] `git diff --check` → clean
- [x] SPEC.md가 required surface 전체를 계약으로 커버:
  entities(2.1), seeded data(3), routes/req/res/error(7),
  permissions(5.1), listing/application transition tables(6.1/6.2),
  filtering/pagination ordering(7.1), DB path/isolation(4),
  XSS handling(8), exact test/smoke acceptance(10), UI/browser
  acceptance(9), non-goals(1.1), implementation file allowlist(12)
- [x] bootstrap 파일(`PROJECT_BRIEF.md`, `TEAM_WORKFLOW.md`,
  `COMMUNICATION_LOG.md`) 미수정 확인

## 5. Review correction (Coco blocking review 반영)
Coco의 PR #1 리뷰(2026-08-25, CHANGES REQUESTED)를 반영:
- 문제: `matched → cancelled` 취소 행위자가 §5.1(permissions, owner만)과
  §6.1(transition, "owner 또는 accepted 신청자")에서 충돌 →
  확정: **matched 취소는 owner-only**로 통일(Coco 권장안 채택).
- 수정 위치:
  - §6.1 transition table: `matched | cancel | owner | cancelled`
  - §5.1 permissions table: 기존 owner-only 유지(변경 없음, 근거 테이블)
  - §7.3 route: `POST /listings/{id}/cancel` 403: owner 아님(기존 계약
    유지 — 이번 결정의 기준)
  - §7.4 conditional buttons: `게시물 취소` 버튼 viewer=owner 조건 유지
  - §10.1 mandatory tests:
    - `tests/test_transitions.py` — `matched cancel(owner, 성공)` 명시
    - `tests/test_permissions.py` — matched listing에서 비-owner(accepted
      신청자 포함) cancel → 403, owner → 302 행 추가
  - §5.1 상태코드 규칙에서 `444가 아니라` 문구 제거(재정: `존재하지 않는
    리소스=404`)
- 재검증: `git diff --check` clean, owner-only 계약이 permissions/
  transition/route/button/test 5곳에서 일치함을 read-back으로 확인.

## 6. Verdict
PASS(self-check 기준, 권고적). 계약이 Kongyi에게 추가 결정 없이
구현을 가능하게 한다. 최종 승인/머지는 Coco가 PR 리뷰 후 결정한다
(자기 PASS는 advisory).
