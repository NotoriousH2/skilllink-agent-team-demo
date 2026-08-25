# Dori Release Report — SkillLink v1 문서/릴리즈 PR

- Stage: Docs/Release (README + changelog + release report)
- Branch owner: Dori Documentation Release <dori@notolab.local>
- Branch: `agent/dori-docs` → `main`
- Branch 기반: `origin/main` (PR #4 병합 커밋 `7e3272e8bc72ec909fbf672352e6d85ca4d6281c`)
- Date: 2026-08-25 (KST)

## 1. Files created (생성 파일)

- `README.md` — 제품 목적, Golden Demo 교육 논지, 기능/non-goals, 아키텍처, 실행법,
  데모 사용자/operator/시드/상태 규칙, 결정적 검증, 공개 GitHub 워크플로우,
  공유 로그인 제약, author 귀속 주의사항, 보안 설계, 알려진 한계, 릴리스/롤백, 증거 위치, 강의 포인트
- `CHANGELOG.md` — Keep a Changelog 스타일 `0.1.0`(2026-08-25), Added/Changed-Fixed/Security/
  Verification/Agent Workflow/Known Limitations 섹션
- `agent_reports/DORI_RELEASE_REPORT.md` — 본 파일

## 2. Sources read (읽은 소스)

### 2.1 저장소 문서
- `PROJECT_BRIEF.md` — 제품 비전, user story, required surface, constraints, 공개 GitHub 프로세스, final acceptance
- `TEAM_WORKFLOW.md` — 스테이지/브랜치/PR/리뷰어 매트릭스, one-writer 규칙, CI 증거 요구
- `SPEC.md` — v1 확정 계약(데이터 모델, 시드, 권한, 전환, 라우트, XSS, 테스트/스모크, UI/browser acceptance)
- `COMMUNICATION_LOG.md` — bootstrap 컨텍스트, 단일 GitHub 계정 제약
- `agent_reports/NARI_SPEC_REPORT.md` — Nari 계약 리포트(모호성 해결, 리스크, self-checks, Coco review 반영)
- `agent_reports/KONGYI_IMPLEMENTATION_REPORT.md` — Kongyi 구현 리포트(파일, 아키텍처, 검증, contract coverage)
- `agent_reports/BORI_QA_REPORT.md` — Bori 독립 QA 리포트(7개 로컬 명령, CI, allowlist, 보안, ~150 fresh-DB probes, findings F1–F3)

### 2.2 제품 소스
- `pyproject.toml` — 의존성(FastAPI, Jinja2, uvicorn, python-multipart; dev: pytest, ruff, httpx2)
- `app/main.py` — FastAPI 앱, lifespan 시드, static mount
- `app/db.py` — `get_db_path()`(env `SKILLLINK_DB` 우선, 절대경로), `connect()`(foreign_keys=ON)
- `app/seed.py` — SPEC §3 고정 시드(users 4, listings 8, applications 3), 멱등
- `app/labels.py` — 한국어 enum 라벨
- `app/routes.py` — SPEC §7 전체 라우트, §5.1 권한, §6.1/6.2 전환, 404→403→409→422 순서
- `templates/*.html` — Jinja2 템플릿 7개
- `static/css/main.css`, `static/js/app.js` — 반응형 그리드, 최소 vanilla JS
- `scripts/golden_smoke.py` — SPEC §10.2 golden smoke
- `tests/conftest.py`, `tests/test_*.py` — 31 tests

### 2.3 CI/워크플로우
- `.github/workflows/ci.yml` — `contract` job(bootstrap 파일 존재 검증) + `quality` job
  (`uv sync --locked --group dev` / `compileall` / `ruff check` / `ruff format --check` / `pytest -q` / `golden_smoke.py`)

### 2.4 Git 히스토리
- `git log --format='%H %an <%ae> | %s' --all` — 전체 커밋 히스토리, author identity 확인

## 3. GitHub evidence (정확한 증거)

### 3.1 PR #1–#4 (전부 병합 완료)

| PR | 제목 | 브랜치 | Head SHA | 병합 커밋 | 병합일 (UTC) | 스테이지 owner | Head commit author |
|---|---|---|---|---|---|---|---|
| [#1](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/1) | docs(spec): define SkillLink acceptance contract | `agent/nari-spec` | `b438d9ed3c7905b74f064b99cfbba012b9133896` | `5c2c610a68c069a4a2a9f03b656a10ce9cefa0bc` | 2026-08-24T23:25:28Z | Nari Spec Critic | `Coco Orchestrator <coco@notolab.local>` (worktree identity drift, §6 참조) |
| [#2](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/2) | ci: make bootstrap workflow valid before implementation | `ci/fix-bootstrap-workflow` | `453fd8d121de2194ec93be8748d95f8854523185` | `414214e733bcd53f50b9676b94d44a48b68d2032` | 2026-08-24T23:22:15Z | Coco Orchestrator | `Coco Orchestrator <coco@notolab.local>` |
| [#3](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/3) | feat: implement SkillLink marketplace contract | `agent/kongyi-implementation` | `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3` | `5d70abacd26a26aa3e7defc7bf55f068f5522ea2` | 2026-08-25T00:05:42Z | Kongyi Implementation Worker | `Kongyi Implementation Worker <kongyi@notolab.local>` |
| [#4](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/4) | test: record independent Bori QA evidence | `agent/bori-qa` | `7ec4d486018afad33a00b1051678f2425c50e539` | `7e3272e8bc72ec909fbf672352e6d85ca4d6281c` | 2026-08-25T00:11:04Z | Bori Independent QA | `Bori Independent QA <bori@notolab.local>` |

### 3.2 리뷰/게이트 (COMMENTED, 명시적 verdict)

- **PR #1**: Coco — CHANGES REQUESTED(§5.1/§6.1/§7.3 충돌) → 재리뷰 ACCEPT(HEAD `b438d9ed3c7905b74f064b99cfbba012b9133896`)
- **PR #2**: Coco — ACCEPT(root cause 확인, `contract`/`quality` pass)
- **PR #3**: Bori — ACCEPT(독립, 7개 로컬 명령 exit 0, ~150 fresh-DB probes, findings F1–F3) + Coco — ACCEPT(병합 게이트, `COCO_BROWSER_PR3_PASS`)
- **PR #4**: Coco — ACCEPT(HEAD `7ec4d486018afad33a00b1051678f2425c50e539`, 단일 파일 diff, author `Bori Independent QA <bori@notolab.local>`)

### 3.3 CI (GitHub Actions)

- **PR #1**: `contract` pass, `quality` pass(run `32789228847`)
- **PR #2**: `contract` pass, `quality` pass(run `32788988410`)
- **PR #3**: `contract` pass, `quality` pass(run `32790474265`, HEAD `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3`)
  - 병합 push run `32792204444`(SHA `5d70abacd26a26aa3e7defc7bf55f068f5522ea2`): success
- **PR #4**: `contract` pass, `quality` pass(run `32792516243`)

### 3.4 병합 커밋 author

- 전부 `변형호(Hyungho Byun) <Notorioush2@snu.ac.kr>`(공유 GitHub 로그인)

## 4. Deterministic verification (실제 재실행)

아래 명령은 2026-08-25에 병합된 `main`(`7e3272e8bc72ec909fbf672352e6d85ca4d6281c`)에서
**실제로 재실행**한 결과입니다(모두 exit 0).

| # | 명령 | 실제 출력 | Exit |
|---|---|---|---|
| 1 | `uv sync --locked --group dev` | `Resolved 28 packages in 1ms` / `Checked 25 packages in 0.38ms` | 0 |
| 2 | `uv run python -m compileall app scripts tests` | clean compile | 0 |
| 3 | `uv run ruff check app scripts tests` | `All checks passed!` | 0 |
| 4 | `uv run ruff format --check app scripts tests` | `14 files already formatted` | 0 |
| 5 | `uv run pytest -q` | `31 passed in 0.58s` | 0 |
| 6 | `uv run python scripts/golden_smoke.py` | `GOLDEN SMOKE PASS` | 0 |
| 7 | `git diff --check` | clean | 0 |

## 5. Unsupported claims excluded (제외된 주장)

- **스크린샷 커밋**: 스크린샷은 저장소에 커밋되지 않음(오케스트레이터 소유 외부 증거).
  README/CHANGELOG에 "스크린샷 커밋"이라는 주장을 하지 않음.
- **형식적 APPROVE**: 단일 GitHub 로그인으로 형식적 self-approval 불가.
  "GitHub APPROVE"라는 주장을 하지 않고, "COMMENTED 리뷰(명시적 ACCEPT/CHANGES REQUESTED) + CI 게이트 + 병합 커밋"으로 대체.
- **production 배포**: production 배포 파이프라인 없음. "배포 성공"이라는 주장을 하지 않음.
- **Bori 브라우저 게이트**: Bori는 브라우저 게이트를 실행하지 않음(환경에 브라우저 없음).
  "Bori가 브라우저 검증"이라는 주장을 하지 않고, "Coco 브라우저 게이트(`COCO_BROWSER_PR3_PASS`)가 해당 증거 소유"로 명시.
- **동시 쓰기 안전성**: 명시적 non-goal(SPEC §1.1). "동시 쓰기 안전성 보장"이라는 주장을 하지 않음.
- **i18n, rate limiting, API versioning**: non-goal(SPEC §1.1). 해당 주장을 하지 않음.

## 6. Identity-attribution caveat (author 귀속 주의사항)

- **Nari 2차 수정 커밋**(`b438d9ed3c7905b74f064b99cfbba012b9133896`):
  - 지속적 Nari 세션에서 실행되었지만, repository-local identity가 worktree 간에 공유되어
    실수로 `Coco Orchestrator <coco@notolab.local>`로 author가 기록됨.
  - PR #1의 초기 커밋(`4dee1352d5f5007a24d97054c2e2ae4a644d9367`)은 `Nari Spec Critic <nari@notolab.local>`로
    올바르게 기록되었지만, 2차 수정 커밋만 identity drift가 발생.
  - 이후 에이전트들은 커밋마다 `-c user.name=... -c user.email=...`로 명시적 author를 지정하여
    이 문제를 방지(Kongyi, Bori 커밋은 각자 고유 identity).
  - 이 주의사항은 커밋 author의 불완전성을 투명하게 기록하기 위한 것.
- **Dori 커밋**: 본 PR의 커밋은 `Dori Documentation Release <dori@notolab.local>`로
  `-c user.name=... -c user.email=...` 명시적 author 지정.

## 6.1 Review correction (Coco CHANGES REQUESTED 반영)

Coco의 PR #5 리뷰(2026-08-25, CHANGES REQUESTED)를 반영:

1. **README §4.2 false port instruction**:
   - 문제: `SKILLLINK_PORT=9000` env 변수는 애플리케이션이 읽지 않으며, uvicorn 명령은 `--port 8321`을 하드코딩.
   - 수정: `SKILLLINK_PORT` env 변수 언급을 제거하고, `--port 9000` 인자를 직접 사용하는 정확한 명령으로 교체.

2. **Operator GET wording**:
   - 문제: README가 operator가 "모든 GET 페이지"에 접근 가능하다고 기술했지만, `/activity`는 명시적으로 403.
   - 수정: "공개 페이지(홈, 게시물 상세, `/health`, `/users/select/*`)와 `/admin`만 읽기 전용 접근 가능, `/activity`는 403"으로 재작성.
   - README §5.1, §5.4, CHANGELOG, DORI_RELEASE_REPORT의 모든 관련 요약 문구 정렬.

3. **Nari author attribution tables**:
   - 문제: PR #1 head `b438d9e`는 `Coco Orchestrator`가 author이지만, README/CHANGELOG/Dori report의 PR 테이블이
     head role/author를 Nari로 제시.
   - 수정: 각 테이블을 "스테이지 owner"와 "Head commit author"로 분리하여 사실대로 기록.
     - PR #1: 스테이지 owner = Nari Spec Critic, Head commit author = `Coco Orchestrator <coco@notolab.local>` (worktree identity drift)
     - PR #1 초기 커밋(`4dee135`)은 `Nari Spec Critic <nari@notolab.local>`로 올바르게 기록됨.
   - "각 스테이지 커밋이 고유 role author를 가진다"는 일반적 주장에 PR #1 head 커밋 예외를 명시.

**검증**: `git diff --check` clean, 3개 파일(README.md, CHANGELOG.md, agent_reports/DORI_RELEASE_REPORT.md)만 수정.

## 7. Known limitations (알려진 한계)

- **F1 (minor, SPEC §9)**: CSS breakpoint `1024px`/`600px` vs SPEC `768px`/`390px`
  - 관측 가능한 수용 기준(768px → 2열, 390px → 1열)은 충족
  - follow-up에서 breakpoint 값 정렬 권장
- **F2 (info)**: `app/routes.py:19-24` standalone `Environment` 생성 후 `templates.env` 재할당
  - 동작 문제 없음, `Jinja2Templates(directory=..., env=...)` 스타일이 더 예측 가능
- **F3 (info)**: `app/seed.py` DDL 문자열 중복(`app/db.py:SCHEMA` 미사용)
  - cosmetic
- **동시 쓰기 안전성**: 명시적 non-goal(SPEC §1.1)
- **브라우저 수동 검증**: Bori는 브라우저 게이트 실행하지 않음(환경에 브라우저 없음)
  - Coco 브라우저 게이트가 해당 증거 소유
- **production 배포**: 없음(로컬 데모), 롤백 = DB 파일 삭제 후 재시작
- **스크린샷**: 저장소에 커밋되지 않음(오케스트레이터 소유 외부 증거)

## 8. Recommendation (권고)

**READY WITH RISKS**

### 근거
- 7개 필수 로컬 명령 전부 exit 0(독립 재현)
- GitHub CI: PR #1–#4 전부 `contract`/`quality` pass
- Bori 독립 QA: ACCEPT(~150 fresh-DB probes, findings F1–F3 비블로킹)
- Coco 브라우저 게이트: `COCO_BROWSER_PR3_PASS`(스크린샷 5장, 예상 밖 에러 0)
- 공개 GitHub 워크플로우: PR #1–#4 전부 병합, 역할 귀속 보존

### 리스크 (비블로킹)
- **F1**: CSS breakpoint 값이 SPEC과 다름(관측 가능한 수용 기준은 충족)
- **F2/F3**: cosmetic/info level
- **author 귀속**: Nari 2차 수정 커밋의 author가 `Coco Orchestrator`로 기록됨(투명하게 기록됨)
- **브라우저 게이트**: Bori가 실행하지 않음(Coco가 소유)

### 다음 단계
- Coco 리뷰 후 병합(본 PR)
- follow-up: F1–F3 findings 처리(별도 PR)

## 9. Verdict

**READY WITH RISKS** — 7개 필수 로컬 명령 전부 exit 0(독립 재현), GitHub CI green,
Bori 독립 QA ACCEPT, Coco 브라우저 게이트 PASS, 공개 GitHub 워크플로우 완료.
비블로킹 findings(F1–F3)와 author 귀속 주의사항은 투명하게 기록됨.
