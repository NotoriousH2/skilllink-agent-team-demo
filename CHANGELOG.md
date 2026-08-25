# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-25

### Added
- **SkillLink v1 MVP**: 동네 단위 스킬/도움 마켓플레이스 데모
  - 한국어 반응형 카드 UI(데스크톱 3열 / 태블릿 2열 / 모바일 1열, 상태 배지 색상)
  - 시드 데이터: 데모 사용자 4명, 게시물 8건, 신청 3건(고정값, 멱등 시드)
  - 게시물 CRUD(생성/수정/취소/완료)와 신청 플로우(신청/수락/거절/취소)
  - 검색/필터(`q`, `category`, `type`, `status` AND 조합), `id DESC` 정렬, 페이지당 10개
  - 활동 페이지(`/activity`)와 운영자 관리 페이지(`/admin`)
  - 데모 사용자 전환(cookie `current_user_id`, 1~4 또는 `operator`)
  - `/health` 엔드포인트
- **결정적 검증**: pytest 31개 + golden smoke(실패 시 non-zero exit)
- **CI**: `.github/workflows/ci.yml`(`contract` + `quality` job)
- **공개 에이전트 팀 워크플로우**: Nari(계약) → Coco(리뷰/게이트) → Kongyi(구현) → Bori(독립 QA) → Dori(문서/릴리즈)
  - PR #1: [docs(spec): define SkillLink acceptance contract](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/1)
    - Head `b438d9ed3c7905b74f064b99cfbba012b9133896`, 병합 `5c2c610a68c069a4a2a9f03b656a10ce9cefa0bc`
    - Nari Spec Critic <nari@notolab.local>, Coco 리뷰(CHANGES REQUESTED → ACCEPT)
  - PR #2: [ci: make bootstrap workflow valid before implementation](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/2)
    - Head `453fd8d121de2194ec93be8748d95f8854523185`, 병합 `414214e733bcd53f50b9676b94d44a48b68d2032`
    - Coco Orchestrator <coco@notolab.local>, Coco 리뷰(ACCEPT)
  - PR #3: [feat: implement SkillLink marketplace contract](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/3)
    - Head `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3`, 병합 `5d70abacd26a26aa3e7defc7bf55f068f5522ea2`
    - Kongyi Implementation Worker <kongyi@notolab.local>, Bori 독립 리뷰(ACCEPT) + Coco 병합 게이트(ACCEPT)
  - PR #4: [test: record independent Bori QA evidence](https://github.com/NotoriousH2/skilllink-agent-team-demo/pull/4)
    - Head `7ec4d486018afad33a00b1051678f2425c50e539`, 병합 `7e3272e8bc72ec909fbf672352e6d85ca4d6281c`
    - Bori Independent QA <bori@notolab.local>, Coco 리뷰(ACCEPT)

### Changed / Fixed
- **PR #2**: bootstrap CI 워크플로우의 잘못된 job-level `hashFiles` 조건을 post-checkout detector로 교체
  - `contract`/`quality` job이 정상 실행되도록 수정
- **PR #1 (2차 수정)**: `matched → cancelled` 취소 actor 계약을 owner-only로 통일
  - SPEC §5.1/§6.1/§7.3/§7.4/§10.1의 충돌 해결(Coco CHANGES REQUESTED 반영)
  - 커밋 `b438d9ed3c7905b74f064b99cfbba012b9133896`(author: Coco Orchestrator — repository-local identity 공유로 인한 귀속 주의사항, README §7.2 참조)

### Security
- **stored XSS 방지**: 모든 Jinja2 템플릿 `autoescape=True`, `|safe` 사용 0건
  - 사용자 문자열은 raw 저장, 렌더링 시 이스케이프
  - pytest(`tests/test_xss.py`) + golden smoke(단계 3) 이중 검증
- **cookie 보안**: `current_user_id`는 `HttpOnly; SameSite=Lax; Max-Age=2592000`
- **SQL 인젝션 방지**: 모든 쿼리 `?` 파라미터 바인딩
- **연결 수명**: 모든 라우트 핸들러 `try/finally: conn.close()`
- **외부 의존성**: 제품 코드에 외부 네트워크/CDN 없음

### Verification
- **로컬 결정적 검증**(2026-08-25, 병합된 `main` `7e3272e8bc72ec909fbf672352e6d85ca4d6281c`에서 재실행):
  1. `uv sync --locked --group dev` → `Resolved 28 packages in 1ms` / `Checked 25 packages in 0.38ms` (exit 0)
  2. `uv run python -m compileall app scripts tests` → clean compile (exit 0)
  3. `uv run ruff check app scripts tests` → `All checks passed!` (exit 0)
  4. `uv run ruff format --check app scripts tests` → `14 files already formatted` (exit 0)
  5. `uv run pytest -q` → `31 passed in 0.58s` (exit 0)
  6. `uv run python scripts/golden_smoke.py` → `GOLDEN SMOKE PASS` (exit 0)
  7. `git diff --check` → clean (exit 0)
- **Bori 독립 QA**(PR #3, head `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3`):
  - 7개 필수 로컬 명령 전부 exit 0(독립 재현)
  - ~150개 fresh-DB assertion(6개 fresh-DB TestClient 세션)
  - 정적 보안 리뷰: `|safe` 0건, `innerHTML`/`document.write`/`eval(` 0건, 하드코딩 자격증명 없음, 외부 네트워크/CDN 없음
- **GitHub CI**: PR #1–#4 전부 `contract`/`quality` pass
  - PR #3 head run `32790474265`(SHA `84b2af7b872563c6b5b5b8e2f2c2b62c0826bcb3`): success
  - PR #3 병합 push run `32792204444`(SHA `5d70abacd26a26aa3e7defc7bf55f068f5522ea2`): success
- **Coco 브라우저 게이트**(PR #3): `COCO_BROWSER_PR3_PASS`
  - 스크린샷 5장, 예상 밖 console/page 에러 0건
  - **참고**: 스크린샷은 저장소에 커밋되지 않음(오케스트레이터 소유 외부 증거)

### Agent Workflow
- **공개 순차 에이전트 팀**: Nari → Coco → Kongyi → Bori → Dori
- **역할 귀속**: 각 프로필은 고유 Git author identity로 커밋
  - Nari Spec Critic <nari@notolab.local>
  - Coco Orchestrator <coco@notolab.local>
  - Kongyi Implementation Worker <kongyi@notolab.local>
  - Bori Independent QA <bori@notolab.local>
  - Dori Documentation Release <dori@notolab.local>
- **공유 로그인 제약**: 단일 GitHub 계정(`NotoriousH2`) 사용으로 형식적 self-approval 불가
  - 대체 수단: COMMENTED 리뷰(명시적 ACCEPT/CHANGES REQUESTED) + CI 게이트 + 병합 커밋
- **author 귀속 주의사항**: Nari 2차 수정 커밋(`b438d9ed3c7905b74f064b99cfbba012b9133896`)은
  repository-local identity 공유로 인해 `Coco Orchestrator`로 author 기록됨
  - 이후 에이전트는 커밋마다 `-c user.name=... -c user.email=...`로 명시적 author 지정

### Known Limitations
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
