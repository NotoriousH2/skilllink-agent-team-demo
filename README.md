# SkillLink — 동네 스킬/도움 마켓플레이스 Golden Demo

SkillLink는 NotoLAB Hermes 멀티 에이전트 개발팀의 **공개·증거 보존 데모**입니다.
교실 규모의 한국어 동네 스킬/도움 거래 마켓플레이스 MVP를,
**Nari(계약) → Coco(리뷰/머지 게이트) → Kongyi(구현) → Bori(독립 QA) → Dori(문서/릴리즈)**
순서의 게이트형 에이전트 팀이 공개 GitHub PR 체인으로 만들어가는 과정을 그대로 보여줍니다.

이 README는 2026-08-25 시점의 병합된 `main`(merge 커밋 `7e3272e8bc72ec909fbf672352e6d85ca4d6281c`,
PR #1–#4 전부 병합 완료)에 대해, 실제로 재실행한 검증 결과만 기록합니다.

---

## 1. 목적과 Golden Demo 교육 논지

- **제품 목적**: 데모 사용자는 게시물을 탐색·검색·필터링하고, 생성·수정하며, 다른 사용자의
  오픈 게시물에 신청하고, 소유자가 신청을 수락/거절하며, 매칭된 일을 완료/취소하는
  동네 단위 스킬/도움 마켓플레이스를 경험합니다.
- **Golden Demo 논지**: "에이전트가 코드를 쓴다"가 아니라, **게이트된 순차적 에이전트 팀이
  어떻게 공개 감사 흔적(branch, commit author, PR, 리뷰, CI, 병합 커밋)을 남기며
  계약 → 구현 → 독립 검증 → 문서/릴리즈를 진행하는가**를 보여주는 것이 본 데모의 핵심입니다.
  - 각 스테이지는 최신 병합 `main`에서 시작하고, 각 프로필은 고유 Git author identity로 커밋합니다.
  - 구현자(Kongyi)가 유일한 검증자가 아닙니다: Bori가 독립 fresh-DB 검증과 정적 보안 리뷰를 수행하고,
    Coco가 CI + 브라우저 게이트를 통과시킨 뒤에만 병합합니다.
  - 단일 GitHub 로그인 제약 때문에 형식적 self-approval은 불가능하며,
    **COMMENTED 리뷰(명시적 ACCEPT/CHANGES REQUESTED) + CI 게이트 + 병합 커밋**이 감사 가능한 대체 수단입니다.

## 2. 기능 범위 (실제 구현)

### 2.1 구현된 기능
- 한국어 반응형 카드 마켓플레이스 UI(데스크톱 3열 / 태블릿 2열 / 모바일 1열, 상태 배지 색상)
- 시드 데이터: 데모 사용자 4명, 게시물 8건, 신청 3건(고정값, 멱등 시드)
- 게시물 CRUD: 생성/수정(owner만, open만), 취소(owner만, open/matched), 완료(matched, owner 또는 accepted 신청자)
- 검색/필터: `q`(title+description 부분문자열, ≤200자), `category`, `type`, `status` AND 조합, `id DESC` 정렬, 페이지당 10개 고정
- 신청 플로우: 신청(owner 제외, open만, 중복 pending 금지) → 수락/거절(owner만, pending만) → 신청 취소(applicant만, pending만)
- 수락 부수효과: 같은 게시물의 다른 pending 신청 전체 → rejected, 게시물 → matched
- 활동 페이지(`/activity`, 데모 사용자만)와 운영자 관리 페이지(`/admin`, operator만)
- 데모 사용자 전환: 헤더 선택기 + `current_user_id` cookie(1~4 또는 `operator`, 기본 1)
- `/health` 엔드포인트(`{"status":"ok"}`)
- 결정적 검증: pytest 31개 + golden smoke(실패 시 non-zero exit)

### 2.2 Non-goals (명시적 제외, SPEC §1.1)
- 실제 인증/로그인(JWT, 세션, 비밀번호) 없음 — 데모 사용자 cookie 전환만
- 결제, 채팅, 지도, 파일 업로드 없음
- 외부 API, CDN, React/Node 빌드 없음
- i18n(한국어 외), rate limiting, API versioning 없음
- 동시 사용자 격리/동시 쓰기 안전성 보장 없음(단일 프로세스 데모)
- production 배포 파이프라인 없음(CI/로컬 검증만)

## 3. 아키텍처와 디렉터리 구조

```
skilllink-agent-team-demo/
├── PROJECT_BRIEF.md            # 제품 비전, 제약, 공개 GitHub 프로세스
├── TEAM_WORKFLOW.md            # 스테이지/브랜치/PR/리뷰어 매트릭스와 규칙
├── SPEC.md                     # v1 확정 계약(데이터 모델, 시드, 권한, 전환, 라우트, XSS, 테스트/스모크)
├── COMMUNICATION_LOG.md        # Coco 유지 관리 통신 로그
├── pyproject.toml / uv.lock    # 의존성(FastAPI, Jinja2, uvicorn, python-multipart; dev: pytest, ruff, httpx2)
├── app/
│   ├── main.py                 # FastAPI 앱, lifespan 시드, static mount
│   ├── db.py                   # get_db_path()(SKILLLINK_DB env 우선, 절대경로), connect()(foreign_keys=ON)
│   ├── seed.py                 # SPEC §3 고정 시드(users 4, listings 8, applications 3), 멱등
│   ├── labels.py               # 한국어 enum 라벨
│   └── routes.py               # SPEC §7 전체 라우트, §5.1 권한, §6.1/6.2 전환, 404→403→409→422 순서
├── templates/                  # Jinja2 템플릿 7개(base, home, listing_detail, listing_form, activity, admin, error)
├── static/
│   ├── css/main.css            # 반응형 그리드, 상태 배지
│   └── js/app.js               # 최소 vanilla JS
├── scripts/golden_smoke.py     # SPEC §10.2 golden smoke(임시 DB, 127.0.0.1:8322)
├── tests/                      # conftest + test_seed/listings/transitions/permissions/xss/errors (31 tests)
├── agent_reports/              # NARI_SPEC_REPORT, KONGYI_IMPLEMENTATION_REPORT, BORI_QA_REPORT, DORI_RELEASE_REPORT
└── .github/workflows/ci.yml    # contract job + quality job(uv sync/compileall/ruff/pytest/smoke)
```

- 단일 FastAPI 앱(`app.main:app`), SQLite(`data/skilllink.db` 또는 `SKILLLINK_DB` env), Jinja2 서버 렌더링.
- `get_db_path()`가 호출마다 env를 읽어 테스트 격리(tmp_path DB)를 보장.
- 상태 전환은 SPEC §6.1/6.2 표만 허용, 나머지는 409.
- 모든 사용자 문자열은 raw 저장, 렌더링 시 Jinja2 `autoescape=True`로 이스케이프(stored XSS 방지).

## 4. 실행 방법

### 4.1 사전 요구사항
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- 브라우저(로컬 데모 확인용)

### 4.2 설치/실행/리셋 (정확한 명령)

```bash
# 의존성 설치(로크드)
uv sync --locked --group dev

# 로컬 시작(기본 포트 8321, host 항상 127.0.0.1)
uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8321

# 다른 포트(예: 9000)로 시작하려면 --port 인자를 직접 변경
uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 9000

# 브라우저에서 열기
# http://127.0.0.1:8321/  (또는 --port로 지정한 포트)
```

- **데모 리셋**: `data/skilllink.db` 삭제 후 재시작(다른 리셋 API/명령 없음).
- **테스트 격리**: `SKILLLINK_DB` env(절대경로)가 설정되면 그 값을 우선 사용.

## 5. 데모 사용자, operator 모드, 시드, 상태 규칙

### 5.1 데모 사용자 (시드, SPEC §3.1)
| id | 이름 | email |
|---|---|---|
| 1 | 김민수 | minsukim@demo.local |
| 2 | 이서연 | seoyeonlee@demo.local |
| 3 | 박준호 | junhohpark@demo.local |
| 4 | 최다은 | daeunchoi@demo.local |

- 현재 사용자는 cookie `current_user_id`(값: `1`~`4` 또는 `operator`, 미설정 시 기본 `1`)로 결정.
- 전환: `GET /users/select/{value}` → `Set-Cookie: current_user_id=<value>; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000` + `302` → `/`.
- **operator**는 `users` 테이블에 없는 관측 전용 페르소나: 공개 페이지(홈, 게시물 상세, `/health`, `/users/select/*`)와 `/admin`만 읽기 전용 접근 가능, 모든 POST는 403, `/activity`는 403.

### 5.2 시드 데이터 (고정값, SPEC §3)
- **listings 8건**: id 1~8, owner 1~4, category study/repair/cooking/tech/other, type offer/request,
  status open(1~5), matched(6), completed(7), cancelled(8).
- **applications 3건**: id 1(listing 6, accepted), id 2(listing 2, pending), id 3(listing 4, pending).
- 시드는 `users`가 0행일 때만 실행(멱등).

### 5.3 게시물/신청 상태 규칙 (SPEC §6)
- **listings**: `open → matched`(accept, owner), `open → cancelled`(cancel, owner), `matched → completed`(complete, owner 또는 accepted 신청자), `matched → cancelled`(cancel, owner-only).
  `completed`/`cancelled`는 종결 상태(어떤 액션도 409). `matched`에는 새 신청 409(L3).
- **applications**: `pending → accepted`(accept, owner), `pending → rejected`(reject, owner), `pending → cancelled`(cancel, applicant).
  `accepted`/`rejected`/`cancelled`는 종결 상태(409).
- **불변식**: L1 자기 게시물 신청 금지, L2 matched는 accepted 1개만, L3 matched는 새 신청 불가, L4 동일 (listing, applicant) pending 최대 1개, L5 시드 후 users 4/listings 8/applications 3.

### 5.4 권한 경계 (SPEC §5.1)
- 공개 GET(홈, 게시물 상세, `/health`, `/users/select/*`): 데모 사용자 1~4, operator.
- `GET /activity`: 데모 사용자 1~4만(operator 403).
- `GET /admin`: operator만(나머지 403).
- `POST /listings`(생성): 데모 사용자만(operator 금지).
- `POST /listings/{id}`(수정): owner만, status=open만.
- `POST /listings/{id}/cancel`: owner만, status ∈ {open, matched}.
- `POST /listings/{id}/complete`: owner 또는 accepted 신청자, status=matched만.
- `POST /applications`(신청): owner가 아닌 데모 사용자, listing.status=open, L4 충족.
- `POST /applications/{id}/accept|reject`: listing owner만, application.status=pending.
- `POST /applications/{id}/cancel`: applicant만, application.status=pending.
- **상태코드 순서**: 존재 확인(404) → 권한(403) → 상태(409) → 필드 검증(422).

## 6. 결정적 검증 (실제 재실행 결과)

아래 명령은 2026-08-25에 병합된 `main`(`7e3272e8bc72ec909fbf672352e6d85ca4d6281c`)에서
**실제로 재실행**한 결과입니다(모두 exit 0).

| # | 명령 | 실제 출력 |
|---|---|---|
| 1 | `uv sync --locked --group dev` | `Resolved 28 packages in 1ms` / `Checked 25 packages in 0.38ms` |
| 2 | `uv run python -m compileall app scripts tests` | clean compile |
| 3 | `uv run ruff check app scripts tests` | `All checks passed!` |
| 4 | `uv run ruff format --check app scripts tests` | `14 files already formatted` |
| 5 | `uv run pytest -q` | `31 passed in 0.58s` |
| 6 | `uv run python scripts/golden_smoke.py` | `GOLDEN SMOKE PASS` |
| 7 | `git diff --check` | clean |

### 6.1 Bori 독립 QA (PR #3, head `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3`)
- 7개 필수 로컬 명령 전부 exit 0(독립 재현).
- GitHub CI: head SHA `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3`에서 `contract`/`quality` pass(run `32790474265`),
  병합 커밋 `5d70abacd26a26aa3e7defc7bf55f068f5522ea2`에서 run `32792204444` success.
- **~150개 fresh-DB assertion**(6개 fresh-DB TestClient 세션): 시드 정확성, 상태코드 순서, 권한,
  전환, 필터/검색, XSS, DB 격리, cookie 계약, 조건부 버튼, 검증 경계 전부 확인.
- 정적 보안: Jinja `|safe` 0건, `innerHTML`/`document.write`/`eval(` 0건, 하드코딩 자격증명 없음,
  외부 네트워크/CDN 없음, SQL 전부 `?` 파라미터 바인딩, 연결 전부 `try/finally: conn.close()`.
- 비블로킹 findings: F1(CSS breakpoint 1024/600 vs SPEC 768/390 — 관측 가능한 수용 기준은 충족),
  F2(standalone Environment 재할당 — 동작 문제 없음), F3(seed.py DDL 중복 — cosmetic).

### 6.2 Coco 브라우저 게이트 (PR #3)
- `COCO_BROWSER_PR3_PASS` — **오케스트레이터 소유의 외부 증거**(브라우저 게이트는 Bori가 실행하지 않음).
- 커버리지: 8카드 홈, study 필터, 390px 1열/가로 스크롤 없음, 사용자 전환, 신청, 수락, matched UI,
  한국어 404, 저장 XSS가 텍스트로 렌더링.
- **스크린샷 5장, 예상 밖 console/page 에러 0건**.
- **참고**: 스크린샷은 이 저장소에 커밋되지 않았습니다. 오케스트레이터가 소유한 외부 증거입니다.

## 7. 공개 순차 GitHub 워크플로우 (PR #1–#4)

| PR | 제목 | 브랜치 | Head SHA | 병합 커밋 | 병합일 (UTC) | 스테이지 owner | Head commit author | 리뷰/게이트 | CI |
|---|---|---|---|---|---|---|---|---|---|
| [#1](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/1) | docs(spec): define SkillLink acceptance contract | `agent/nari-spec` | `b438d9ed3c7905b74f064b99cfbba012b9133896` | `5c2c610a68c069a4a2a9f03b656a10ce9cefa0bc` | 2026-08-24T23:25:28Z | Nari Spec Critic | `Coco Orchestrator <coco@notolab.local>` (worktree identity drift, §7.2 참조) | Coco: CHANGES REQUESTED → 재리뷰 ACCEPT | contract/quality pass |
| [#2](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/2) | ci: make bootstrap workflow valid before implementation | `ci/fix-bootstrap-workflow` | `453fd8d121de2194ec93be8748d95f8854523185` | `414214e733bcd53f50b9676b94d44a48b68d2032` | 2026-08-24T23:22:15Z | Coco Orchestrator | `Coco Orchestrator <coco@notolab.local>` | Coco: ACCEPT | contract/quality pass |
| [#3](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/3) | feat: implement SkillLink marketplace contract | `agent/kongyi-implementation` | `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3` | `5d70abacd26a26aa3e7defc7bf55f068f5522ea2` | 2026-08-25T00:05:42Z | Kongyi Implementation Worker | `Kongyi Implementation Worker <kongyi@notolab.local>` | Bori: ACCEPT(독립) + Coco: ACCEPT(병합 게이트) | contract/quality pass |
| [#4](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/4) | test: record independent Bori QA evidence | `agent/bori-qa` | `7ec4d486018afad33a00b1051678f2425c50e539` | `7e3272e8bc72ec909fbf672352e6d85ca4d6281c` | 2026-08-25T00:11:04Z | Bori Independent QA | `Bori Independent QA <bori@notolab.local>` | Coco: ACCEPT | contract/quality pass |

- **병합 커밋 author**: 전부 `변형호(Hyungho Byun) <Notorioush2@snu.ac.kr>`(공유 GitHub 로그인).
- **역할 커밋 author**: 각 스테이지 프로필의 고유 identity(`nari@notolab.local`, `coco@notolab.local`,
  `kongyi@notolab.local`, `bori@notolab.local`) — 단, PR #1의 head 커밋(`b438d9ed3c7905b74f064b99cfbba012b9133896`)은
  worktree identity drift로 인해 `Coco Orchestrator`로 기록됨(§7.2 참조).
- **CI**: `.github/workflows/ci.yml`의 `contract`(bootstrap 파일 존재 검증)와 `quality`
  (`uv sync --locked --group dev` / `compileall` / `ruff check` / `ruff format --check` / `pytest -q` / `golden_smoke.py`)
  job이 모든 PR에서 pass.

### 7.1 공유 로그인 제약과 리뷰 대체 수단
- 모든 프로필이 동일한 GitHub 계정(`NotoriousH2`)으로 인증하므로 **형식적 self-approval은 불가능**합니다.
- 따라서 리뷰 증거는 **COMMENTED 리뷰(명시적 ACCEPT/CHANGES REQUESTED 본문) + CI 게이트 + 병합 커밋**으로 보존됩니다.
- 역할 귀속은 **고유 commit author, 브랜치, PR, 리뷰 본문, CI 체크, 병합 커밋**으로 유지됩니다.

### 7.2 Nari 2차 수정 커밋의 author 귀속 주의사항
- Nari의 2차 수정(취소 actor 계약 통일, `b438d9ed3c7905b74f064b99cfbba012b9133896`)은
  **지속적 Nari 세션에서 실행**되었지만, repository-local identity가 worktree 간에 공유되어
  실수로 `Coco Orchestrator <coco@notolab.local>`로 author가 기록되었습니다.
- PR #1의 초기 커밋(`4dee1352d5f5007a24d97054c2e2ae4a644d9367`)은 `Nari Spec Critic <nari@notolab.local>`로
  올바르게 기록되었지만, 2차 수정 커밋만 identity drift가 발생했습니다.
- 이후 에이전트들은 **커밋마다 `-c user.name=... -c user.email=...`로 명시적 author를 지정**하여
  이 문제를 방지합니다(예: Kongyi, Bori 커밋은 각자 고유 identity).
- 이 주의사항은 커밋 author의 불완전성을 투명하게 기록하기 위한 것입니다.

## 8. 보안 설계

- **저장**: 사용자 문자열(title, description, message, name)은 DB에 raw로만 저장(저장 시 이스케이프 금지).
- **렌더링**: 모든 Jinja2 템플릿은 `autoescape=True`(`app/routes.py:19-24`에서 `jinja2.Environment(autoescape=True)` 생성 후 `templates.env`에 할당). `|safe` 사용 0건.
- **stored XSS**: 어떤 페이지 HTML에서도 raw `<script>`가 사용자 입력에서 유입되면 hard failure.
  pytest(`tests/test_xss.py`)와 golden smoke(단계 3)가 이중 검증.
- **cookie**: `current_user_id`는 `HttpOnly; SameSite=Lax; Max-Age=2592000`.
- **SQL**: 모든 쿼리는 `?` 파라미터 바인딩. 유일한 문자열 조립 SQL(`app/routes.py:81` count 쿼리)은
  동일한 파라미터화 WHERE 절을 재사용 — 사용자 입력 보간 없음.
- **연결 수명**: 모든 라우트 핸들러와 `init_db()`가 `connect()`를 `try/finally: conn.close()`로 감쌈.
- **외부 의존성**: 제품 코드에 외부 네트워크/CDN 없음(단일 로컬 SQLite).
- **자격증명**: 추적 파일에 하드코딩된 자격증명/토큰 없음.

## 9. 알려진 한계와 findings

- **F1 (minor, SPEC §9)**: `static/css/main.css:60-66`의 breakpoint가 `1024px`(2열)/`600px`(1열)인데,
  SPEC §9는 `768px`(2열)/`390px`(1열)을 명시. 관측 가능한 수용 기준(768px → 2열, 390px → 1열)은 충족되므로
  테스트 가능한 수용 기준 위반은 아니지만, follow-up에서 breakpoint 값을 SPEC에 정렬하는 것이 권장됨.
- **F2 (info)**: `app/routes.py:19-24`가 standalone `Environment`를 생성하고 `templates.env`를 재할당.
  동작 문제는 없지만 `Jinja2Templates(directory=..., env=...)` 스타일이 더 예측 가능.
- **F3 (info)**: `app/seed.py`가 DDL 문자열을 중복(`app/db.py:SCHEMA`는 미사용). cosmetic.
- **동시 쓰기 안전성**: 명시적 non-goal(SPEC §1.1).
- **브라우저 수동 검증**: Bori는 브라우저 게이트를 실행하지 않음(환경에 브라우저 없음).
  Coco 브라우저 게이트(`COCO_BROWSER_PR3_PASS`)가 해당 증거를 소유.
- **production 배포**: 없음(로컬 데모). 롤백 = DB 파일 삭제 후 재시작.

## 10. 릴리스/롤백 가이드

- **배포**: production 배포 파이프라인 없음. 로컬 데모만.
- **롤백**: `data/skilllink.db` 삭제 후 재시작(SPEC §4, §14).
- **CI 영향**: `quality` job은 `pyproject.toml` 존재 시 실행(구현 스테이지부터).
- **데이터**: `*.db`는 `.gitignore`로 커밋 차단. 시드 데이터만 고정, PII 없음(가명 데모 데이터).

## 11. 증거 위치

- **SPEC**: `SPEC.md`(v1 확정 계약)
- **Nari 계약 리포트**: `agent_reports/NARI_SPEC_REPORT.md`
- **Kongyi 구현 리포트**: `agent_reports/KONGYI_IMPLEMENTATION_REPORT.md`
- **Bori 독립 QA 리포트**: `agent_reports/BORI_QA_REPORT.md`
- **Dori 릴리스 리포트**: `agent_reports/DORI_RELEASE_REPORT.md`
- **CI 워크플로우**: `.github/workflows/ci.yml`
- **GitHub PR 체인**: PR #1–#4(위 표 참조)
- **Coco 브라우저 게이트**: `COCO_BROWSER_PR3_PASS`(오케스트레이터 소유 외부 증거, 스크린샷 5장/예상 밖 에러 0)

## 12. 강의 포인트

1. **게이트형 에이전트 팀**: 단일 에이전트가 아니라 계약 → 구현 → 독립 QA → 문서의 순차적 게이트가
   어떻게 감사 가능한 증거를 생성하는지.
2. **역할 귀속**: 공유 GitHub 로그인에서도 commit author, 브랜치, PR, 리뷰, CI, 병합 커밋으로
   역할별 기여를 분리하는 방법.
3. **독립 검증**: 구현자(Kongyi)가 아닌 Bori가 fresh-DB ~150 assertion과 정적 보안 리뷰를 수행.
4. **형식적 approval 대체**: self-approval이 불가능한 환경에서 COMMENTED 리뷰 + CI 게이트 + 병합 커밋이
   어떻게 감사 가능한 대체 수단이 되는지.
5. **결정적 검증**: 7개 로컬 명령(uv sync/compileall/ruff/pytest/smoke/git diff --check)이
   CI와 동일한 명령으로 로컬/CI 양쪽에서 재현 가능.
6. **stored XSS 계약**: raw 저장 + autoescape 렌더링 + pytest/smoke 이중 검증.
7. **투명한 한계 기록**: F1–F3 findings, 브라우저 게이트 소유권, author 귀속 주의사항을
   문서에 명시적으로 기록.

## 13. 다음 과제 (follow-up)

- F1: CSS breakpoint를 SPEC §9의 768px/390px으로 정렬(또는 SPEC 명확화).
- F2: `Jinja2Templates(directory=..., env=...)` 스타일 생성으로 리팩터링.
- F3: `app/seed.py`의 DDL 중복 제거(`app/db.py:SCHEMA` 사용 또는 삭제).
- (선택) 브라우저 게이트를 Bori 환경에서도 재현 가능하도록 도구 추가.
- (선택) 동시 쓰기 안전성(non-goal)에 대한 명시적 테스트/문서화.
