# SkillLink v1 — Deterministic Acceptance Contract

이 문서는 SkillLink MVP의 확정 계약(v1)이다. 구현(Coder)은 이 문서에 없
는 추가 결정을 해서는 안 된다. 명시되지 않은 세부사항은 이 문서의 "모호
성 해결" 섹션의 결정을 따른다. 언어·프레임워크 제약은
`PROJECT_BRIEF.md`를 따른다: Python 3.12, FastAPI, SQLite, Jinja2, 로컬
CSS, 최소한의 vanilla JavaScript.

---

## 1. Product scope (요약)

동네 단위 스킬/도움 거래 마켓플레이스 데모. 데모 사용자는 게시물을 탐색·검색·
필터링하고, 생성·수정하며, 다른 사용자의 오픈 게시물에 신청하고, 소유자
가 신청을 수락/거절하며, 매칭된 일을 완료/취소한다. 인증은 없으며, 헤
더의 데모 사용자 선택기(cookie)로 현재 사용자를 전환한다.

### 1.1 Non-goals (명시적 제외)
- 실제 인증/로그인(JWT, 세션 로그인, 비밀번호) 없음 — 데모 사용자 쿠키 전환만 있음
- 결제, 채팅, 지도, 파일 업로드 없음
- 외부 API, CDN, React/Node 빌드 없음
- i18n(한국어 외) 없음, rate limiting 없음, API versioning 없음
- 동시 사용자 격보장 없음(단일 프로세스 데모). 동시 쓰기 안전성은 보장 대상 아님
- production 배포 파이프라인 없음(CI/로컬 검증만)

---

## 2. Data model

### 2.1 SQL schema (정확히 이 DDL)

```sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS listings (
  id INTEGER PRIMARY KEY,
  owner_id INTEGER NOT NULL REFERENCES users(id),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('study','repair','cooking','tech','other')),
  type TEXT NOT NULL CHECK (type IN ('offer','request')),
  status TEXT NOT NULL CHECK (status IN ('open','matched','completed','cancelled')),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY,
  listing_id INTEGER NOT NULL REFERENCES listings(id),
  applicant_id INTEGER NOT NULL REFERENCES users(id),
  message TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending','accepted','rejected','cancelled')),
  created_at TEXT NOT NULL
);
```

`created_at` 포맷: `YYYY-MM-DDTHH:MM:SS`(naive, 타임존 없음).

### 2.2 앱 레벨 불변식(DB 제약으로 표현 불가한 규칙)
- L1: `applications.applicant_id` ≠ 해당 listing의 `owner_id`(자기 게시물 신청 금지)
- L2: listing이 `matched`이면 정확히 1개의 `accepted` application을 가진다
- L3: listing이 `matched`이면 더 이상 새 신청을 받지 않는다
- L4: 동일 `(listing_id, applicant_id)`에 `pending` application은 최대 1개
- L5: seed 후 `users`는 정확히 4행, `listings`는 정확히 8행, `applications`는 정확히 3행

### 2.3 Enum 라벨(한국어, 렌더링 전용)
| key | category | type | listing.status | application.status |
|---|---|---|---|---|
| study | 학습 | offer | 스킬 제공 | open | 진행 중 | pending | 대기 중 |
| repair | 수리 | request | 도움 요청 | matched | 매칭 완료 | accepted | 수락 |
| cooking | 요리 |  |  | completed | 완료 | rejected | 거절 |
| tech | 테크 |  |  | cancelled | 취소 | cancelled | 취소 |
| other | 기타 |  |  |  |  |  |  |

---

## 3. Seeded data (정확한 값)

시드는 고정값이다. 시작 시 `users`가 비어 있으면 아래 행을 이 순서로
삽입한다(빈 DB만 시드. 비어 있지 않으면 시드 생략 — 멱등).

### 3.1 users
| id | name | email | created_at |
|---|---|---|---|
| 1 | 김민수 | minsu.kim@demo.local | 2026-08-01T08:00:00 |
| 2 | 이서연 | seoyeon.lee@demo.local | 2026-08-01T08:00:00 |
| 3 | 박준호 | junho.park@demo.local | 2026-08-01T08:00:00 |
| 4 | 최다은 | daeun.choi@demo.local | 2026-08-01T08:00:00 |

### 3.2 listings
| id | owner_id | title | description | category | type | status | created_at |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 파이썬 기초 과외 | 파이썬 기초를 다루는 1:1 과외를 제공합니다. 주 2회, 1회 60분. | study | offer | open | 2026-08-01T09:00:00 |
| 2 | 2 | 세탁기 수리 요청 | 세탁기가 탈수 소리를 심하게 내요. 수리 가능한 분 요청합니다. | repair | request | open | 2026-08-02T10:00:00 |
| 3 | 3 | 주말 반찬 요리 | 주말에 만들 반찬(김치찜, 잡채)을 함께 만들어요. 재료비는 나눠요. | cooking | offer | open | 2026-08-03T11:00:00 |
| 4 | 4 | 노트북 점검 | 노트북이 자주 부팅되어요. 점검 및 소프트웨어 설정을 도와주세요. | tech | request | open | 2026-08-04T12:00:00 |
| 5 | 1 | 영어 회화 연습 파트너 | 영어 회화를 연습할 파트너를 찾습니다. 주 1회 30분, 온라인. | study | request | open | 2026-08-05T13:00:00 |
| 6 | 2 | 조립식 책장 설치 | 조립식 책장 2개를 설치해 주세요. 토요일 오전 가능. | repair | request | matched | 2026-08-06T14:00:00 |
| 7 | 3 | 카네이션 꽃다발 만들기 | 어버이날 꽃다발을 직접 만들어드려요. 예약 필요. | other | offer | completed | 2026-08-07T15:00:00 |
| 8 | 4 | 카페에서 사진 촬영 | 동네 카페에서 커플/가족 사진을 찍어드려요. | other | offer | cancelled | 2026-08-08T16:00:00 |

### 3.3 applications (불변식 L2 충족: listing 6은 accepted 1개 보유)
| id | listing_id | applicant_id | message | status | created_at |
|---|---|---|---|---|---|
| 1 | 6 | 3 | 책장 2개 설치 경험 있어요. 토요일 오전에 가능합니다. | accepted | 2026-08-06T15:00:00 |
| 2 | 2 | 4 | 세탁기 탈수 문제는 보통 드럼 균형을 확인하면 해결돼요. | pending | 2026-08-07T09:00:00 |
| 3 | 4 | 1 | 노트북 부팅 문제는 소프트웨어 점검으로 대부분 해결돼요. | pending | 2026-08-07T10:00:00 |

---

## 4. DB path / isolation rules

- 런타임 DB 경로: `data/skilllink.db`(프로젝트 루트 기준 상대경로, `data/`
  디렉토리는 자동 생성). `.gitignore`의 `*.db`가 커밋을 막는다.
- 환경변수 `SKILLLINK_DB`(절대경로)가 설정되어 있으면 그 값을 우선 사용.
  `app/db.py`의 `get_db_path()`가 **호출 때마다** env를 읽는다(테스트
  isolation을 위해).
- `get_db_path()`는 반드시 절대경로를 반환해야 한다:
  `Path(os.environ.get("SKILLLINK_DB", BASE_DIR / "data" / "skilllink.db")).resolve()`
  여기서 `BASE_DIR`은 프로젝트 루트(레포 최상위).
- 모든 연결은 `sqlite3.connect(path)` 후 `PRAGMA foreign_keys=ON`.
  연결은 사용 후 반드시 `finally`에서 close(단일 요청 단위 사용).
- 시드/스키마: `create_app()` lifespan 시작 시 `CREATE TABLE IF NOT EXISTS`
  + `users`가 0행이면 시드(3절 고정 데이터).
- DB 초기화(데모 리셋): `data/skilllink.db` 삭제 후 재시작. 다른 리셋
  API/명령은 없음.

---

## 5. Viewer model (인증 없음)

- 현재 사용자는 cookie `current_user_id`로 결정.
  - 값: `1`~`4` 또는 문자열 `operator`.
  - 미설정 시 기본값: `1`(김민수).
- 전환: `GET /users/select/{value}`(value ∈ `1`|`2`|`3`|`4`|`operator`)
  → `Set-Cookie: current_user_id=<value>; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`
  + `302` → `/`. value가 5가지 중 아니면 `422` 오류 페이지.
- `operator`는 `users` 테이블에 없는 관측 전용 페르소나다.

### 5.1 Permissions table (정확함)
| 액션 | 허용 |
|---|---|
| 모든 GET 페이지 | 데모 사용자 1~4, operator |
| `POST /listings`(생성) | 데모 사용자(자신). operator 금지 |
| `POST /listings/{id}`(수정) | owner만, status=open만 |
| `POST /listings/{id}/cancel` | owner만, status ∈ {open, matched} |
| `POST /listings/{id}/complete` | owner 또는 accepted 신청자, status=matched만 |
| `POST /applications`(신청) | owner가 아닌 데모 사용자, listing.status=open, L4 충족 |
| `POST /applications/{id}/accept` | listing owner만, application.status=pending, listing.status=open |
| `POST /applications/{id}/reject` | listing owner만, application.status=pending |
| `POST /applications/{id}/cancel` | applicant만, application.status=pending |
| `GET /activity` | 데모 사용자 1~4만(operator는 403) |
| `GET /admin` | operator만(나머지는 403) |
- operator의 모든 `POST`는 `403`.
- 상태코드 규칙: 검증 실패=`422`, 권한 실패=`403`, 상태 전환 불가=`409`,
  존재하지 않는 리소스=`404`. 항상 이 순서로 검사:
  존재 확인(404) → 권한(403) → 상태(409) → 필드 검증(422).

---

## 6. State transition tables (완진, 표에 없는 것은 409)

### 6.1 listings
| from | 액션 | 행위자 | to | 부수 효과 |
|---|---|---|---|---|
| open | application accept | owner | matched | L2/L3 발동, 같은 listing의 다른 pending application 전체 → rejected |
| open | cancel | owner | cancelled | 같은 listing의 pending application 전체 → rejected |
| matched | complete | owner 또는 accepted 신청자 | completed | — |
| matched | cancel | owner | cancelled | — |
- `completed`, `cancelled`는 종결 상태(어떤 액션도 409).
- `matched` listing에는 `POST /applications`가 409(L3).

### 6.2 applications
| from | 액션 | 행위자 | to |
|---|---|---|---|
| pending | accept | listing owner | accepted |
| pending | reject | listing owner | rejected |
| pending | cancel | applicant | cancelled |
- `accepted`, `rejected`, `cancelled`는 종결 상태(409).

---

## 7. Routes (완전한 계약)

공통: 모든 HTML 응답은 Jinja2 렌더링, UTF-8. POST는 `application/x-www-form-urlencoded`.
성공 시 POST 응답은 `302`(redirect)이며 대상 URL을 명시한다. 오류 응답은
Jinja 오류 페이지(한국어 메시지 + 홈 링크)를 해당 status code와 함께 반환.

### 7.1 페이지/메타
| Method+Path | 응답 |
|---|---|
| `GET /` | 200 HTML. 쿼리: `q`(선택, ≤200자, title+description 부분문자열, 대소문자 무시), `category`(선택, 2.3 enum), `type`(선택, offer/request), `status`(선택, 4 enum), `page`(선택, int ≥1, 기본 1). 필터는 AND. 정렬: `ORDER BY id DESC`. 페이지당 10개(고정, 쿼리 파라미터 없음). `page`가 마지막 페이지를 넘어면 200 + "조건에 맞는 게시물이 없습니다." 카드 없음. 각 카드: title, owner 이름, type 라벨, category 라벨, status 라벨, description 앞 60자(초과면 `…`), `/listings/{id}` 링크. 하단: 페이지 번호, 총 페이지 수, 이전/다음 링크(쿼리 보존). q/category/type/status 값이 enum 밖이면 422. `page`가 int가 아니거나 ≤0이면 422. |
| `GET /health` | 200 JSON `{"status":"ok"}` (본문 정확히 이 JSON) |
| `GET /activity` | 200 HTML. 2개 섹션: "내가 만든 게시물"(owner=viewer, id DESC), "내가 보낸 신청"(applicant=viewer, id DESC). operator는 403. |
| `GET /admin` | 200 HTML(operator만). 표시: listings 총 수, status별 수(4), category별 수(5), type별 수(2), applications status별 수(4), 최근 신청 10개(id DESC; listing title, applicant 이름, application status 라벨). |
| `GET /users/select/{value}` | 5절 계약. 성공 302 → `/`, 실패 422. |

### 7.2 listing 페이지
| Method+Path | 응답 |
|---|---|
| `GET /listings/{id}` | 200 HTML: 전체 필드 + owner 이름 + created_at + 신청 목록(id, applicant 이름, message, status 라벨) + 조건부 액션 버튼(7.4). 존재하지 않으면 404. |
| `GET /listings/new` | 200 HTML 폼(title, description, category, type). |
| `GET /listings/{id}/edit` | 200 HTML 폼(값 프리필). 404: 없음. 403: owner 아님. 409: status ≠ open. |

### 7.3 listing POST
| Method+Path | 필드 | 성공 | 실패 |
|---|---|---|---|
| `POST /listings` | `title`(strip 후 1~80자), `description`(1~1000자), `category`(enum), `type`(enum) | 302 → `/listings/{new_id}` (owner=viewer) | 422: 필드 위반. 403: operator |
| `POST /listings/{id}` | `title`, `description`, `category`, `type`(생성과 동일 검증) | 302 → `/listings/{id}` | 404: 없음. 403: owner 아님. 409: status ≠ open. 422: 필드 위반 |
| `POST /listings/{id}/cancel` | (없음) | 302 → `/listings/{id}` | 404 / 403: owner 아님 / 409: status ∈ {completed, cancelled} |
| `POST /listings/{id}/complete` | (없음) | 302 → `/listings/{id}` | 404 / 403: owner도 아니고 accepted 신청자도 아님 / 409: status ≠ matched |

### 7.4 상세 페이지 조건부 버튼 / application POST
상세 페이지에 표시되는 버튼(상태/권한 모두 충족 시만):
- `신청하기`: listing.status=open이고 viewer ≠ owner이고 viewer가 데모 사용자.
- `수락`/`거절`: application.status=pending이고 viewer=owner이고 listing.status=open.
- `취소`(신청): application.status=pending이고 viewer=applicant.
- `완료하기`: listing.status=matched이고 (viewer=owner 또는 viewer=accepted 신청자).
- `게시물 취소`: viewer=owner이고 listing.status ∈ {open, matched}.

| Method+Path | 필드 | 성공 | 실패 |
|---|---|---|---|
| `POST /applications` | `listing_id`(int), `message`(1~500자) | 302 → `/listings/{listing_id}` (status=pending) | 404: listing 없음. 403: viewer=owner(L1) 또는 operator. 409: status ≠ open(L3) 또는 L4 위반(이미 pending 보유). 422: 필드 위반 |
| `POST /applications/{id}/accept` | (없음) | 302 → `/listings/{listing_id}` (6.1 부수효과 포함) | 404: application 없음. 403: viewer ≠ listing owner. 409: application.status ≠ pending 또는 listing.status ≠ open |
| `POST /applications/{id}/reject` | (없음) | 302 → `/listings/{listing_id}` | 404 / 403: viewer ≠ owner / 409: status ≠ pending |
| `POST /applications/{id}/cancel` | (없음) | 302 → `/listings/{listing_id}` | 404 / 403: viewer ≠ applicant / 409: status ≠ pending |

`/listings/new` 및 수정 폼에서 viewer 이름은 숨김 필드로 전송하지 않는다.
owner는 서버가 현재 viewer로 결정한다.

---

## 8. XSS handling (stored XSS는 hard failure)

- 저장: DB에는 원문(raw)만 저장. 저장 시 이스케이프 금지.
- 렌더링: 모든 Jinja2 템플릿의 autoescape를 활성화하고(`jinja2.Environment`
  기본값 또는 `autoescape=select_autoescape` 금지 — 명시적으로
  `autoescape=True`), 사용자 생성 문자열(title, description, message,
  name)을 `|safe`로 렌더링하는 코드는 **존재하지 않아야 한다**.
- QA 기준: 어떤 페이지 HTML에서도 raw `<script>` 태그가 사용자 입력에서
  유입되면 hard failure. smoke가 이를 검증한다(10.2.d).

---

## 9. UI / browser acceptance

- 헤더: 서비스명 "SkillLink", 사용자 선택기(현재 사용자 이름 + 1~4와
  operator를 전환하는 링크/셀렉트), "게시물 만들기" 버튼.
- 카드 그리드: 데스크톱(1280px 폭 기준) 3열, 태블릿(768px) 2열,
  모바일(390px) 1열. 카드에 type/category/status 라벨 배지.
- 상태별 배지 색상: open=초록, matched=파랑, completed=회색, cancelled=빨강.
- 모든 폼 오류·상태 메시지는 한국어.
- 브라우저 수동 검증(Coco/Bori가 실행, 기록은 QA 리포트에):
  1. `GET /`에서 seed 8개 카드가 2페이지가 아니라 1페이지에 모두 보임(10/페이지).
  2. `?category=study` → "파이썬 기초 과외", "영어 회화 연습 파트너"만.
  3. `?q=세탁기` → "세탁기 수리 요청"만.
  4. 모바일 폭에서 1열 그리드, 가로 스크롤 없음.
  5. 사용자 2로 전환 → listing 1에서 "신청하기" → 성공 → 사용자 1로 전환
     → listing 1에서 "수락" → 상태 배지가 "매칭 완료"로 변경.
  6. 존재하지 않는 `/listings/999` → 404 오류 페이지(한국어).

---

## 10. Test / smoke acceptance (정확한 기준)

### 10.1 pytest (`tests/`, `uv run pytest -q`)
필수 테스트 파일과 최소 커버리지(이름은 최소 기준, 추가는 허용):
- `tests/conftest.py`: `client` fixture — 매 테스트마다 `SKILLLINK_DB`를
  `tmp_path` 아래 고유 경로로 설정 후 `create_app()` + `TestClient` 반환
  (레포의 `data/skilllink.db`는 어떤 테스트도 건드리지 않는다).
- `tests/test_seed.py`: 시드 정확성 — users 4행, listings 8행,
  applications 3행, 그리고 3절 표의 값이 행별로 일치(L5).
- `tests/test_listings.py`:
  - 생성 성공: `POST /listings` → 302, 로케이터로 상세 페이지 200, owner=viewer.
  - 생성 검증 실패: title 공백 → 422, category "xyz" → 422.
  - 필터: `?category=study` → 정확히 seed 1,5번 제목만; `?type=request` →
    seed 2,4,5번만; `?status=open` → 1~5번만; `?q=세탁기` → 2번만;
    조합 `?category=study&type=request` → 5번만.
  - 정렬: 결과 첫 카드는 가장 큰 id.
  - 페이지: `?page=2&status=open` → 200, 카드 0개(총 5개 < 10/페이지).
    `?page=0` → 422, `?page=abc` → 422.
- `tests/test_transitions.py`: 표 기반(table-driven) — 6.1/6.2 표의 모든
  허용 전환이 성공(302 + DB 상태 확인)하고, 표에 없는 (상태, 액션) 조합은
  모두 409. 최소 행: open cancel(owner, 성공), matched cancel(owner, 성공),
  matched complete(owner, 성공), completed complete(409),
  cancelled cancel(409), pending accept(부수효과
  검증: 자매 pending → rejected), pending reject, pending cancel,
  accepted accept(409), matched listing에 apply(409), pending 중복 apply(409).
- `tests/test_permissions.py`: owner가 아닌 수정 → 403, self-apply → 403,
  operator 생성 → 403, operator accept → 403, matched cancel이 owner-only인
  계약 검증 — matched listing에서 accepted 신청자(또는 그 외 비-owner 데모
  사용자)가 `POST /listings/{id}/cancel` → 403, owner만 → 302,
  operator `/admin` 외 403
  케이스: 사용자 1 `/admin` → 403, operator `/activity` → 403.
- `tests/test_xss.py`: title에 `<script>alert(1)</script>` 저장 → 상세
  페이지 HTML에 raw `<script>alert(1)</script>`가 없고
  `&lt;script&gt;alert(1)&lt;/script&gt;`가 있다. description과
  application message도 동일 검증.
- `tests/test_errors.py`: `/listings/999` → 404,
  `/users/select/99` → 422, `/users/select/operator` → 302.

### 10.2 Golden smoke (`scripts/golden_smoke.py`)
`uv run python scripts/golden_smoke.py`는 0 또는 **non-zero** exit.
절차(실패 시 `GOLDEN SMOKE FAIL: <단계명>` 출력 후 exit 1):
1. 임시 디렉토리에 `SKILLLINK_DB` 지정, `uvicorn app.main:app --host 127.0.0.1 --port 8322`
   subprocess 시작. 30초 내 `GET /health`가 200 `{"status":"ok"}`가 될 때까지 폴링.
2. `GET /` → 200, 본문에 "파이썬 기초 과외"와 "카페에서 사진 촬영" 포함.
3. cookie `current_user_id=1`로 `POST /listings`(title=`<script>alert('smoke')</script>`
   포함 타이틀, description, category=other, type=offer) → 302. 상세 GET → 200,
   raw `<script>alert('smoke')</script>` **없음**, `&lt;script&gt;` 포함.
4. cookie `current_user_id=2`로 `POST /applications`(listing_id=1, message) → 302.
   `GET /listings/1` → 200, message 본문 포함.
5. `POST /applications`(동일 listing_id=1, 동일 사용자) 재시도 → 409(L4).
6. cookie `current_user_id=1`로 `POST /applications/4/accept`(seed 3행 +
   단계 4의 신청 id — 응답 로케이터에서 추출 또는 `/listings/1`에서 신청 수
   순서로 결정) → 302. `GET /listings/1` → 200, "매칭 완료" 배지 텍스트 포함.
7. `GOLDEN SMOKE PASS` 출력, subprocess 종료, exit 0.

스모크는 항상 새로운 임시 DB에서 시작한다(시드 상태 가정).

---

## 11. Startup & verification commands

- 로컬 시작: `uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8321`
  (포트는 env `SKILLLINK_PORT`, 기본 8321. host는 항상 127.0.0.1).
- 구현 단계(Kongyi) 검증 명령(순서대로, 전부 exit 0):
  1. `uv sync --locked --group dev`
  2. `uv run python -m compileall app scripts tests`
  3. `uv run ruff check app scripts tests`
  4. `uv run ruff format --check app scripts tests`
  5. `uv run pytest -q`
  6. `uv run python scripts/golden_smoke.py`
- CI(`.github/workflows/ci.yml`, 이미 존재 — 이 스테이지에서는 수정 금지)
  는 `quality` job이 위 2~6번과 동일한 명령을 실행한다. `uv.lock`를
  커밋해야 `--locked`가 통과한다.

## 12. Implementation file allowlist (Kongyi 스테이지)

허용(생성/수정 가능):
- `pyproject.toml`, `uv.lock`
- `app/` (예: `app/main.py`, `app/db.py`, `app/seed.py`, `app/routes.py` —
  파일 분할은 구현 판단이나 전부 `app/` 아래)
- `templates/*.html`, `static/css/main.css`, `static/js/app.js`
  (static 자원은 이 2개 파일만)
- `scripts/golden_smoke.py`
- `tests/conftest.py`, `tests/test_*.py`
- `agent_reports/KONGYI_IMPLEMENTATION_REPORT.md` (자기 리포트만)

금지(이 스테이지에서 수정 불가):
- `PROJECT_BRIEF.md`, `TEAM_WORKFLOW.md`, `COMMUNICATION_LOG.md`,
  `SPEC.md`, `.github/**`
- `README.md`, `CHANGELOG.md`(Dori 스테이지 소유)
- `agent_reports/NARI_SPEC_REPORT.md`, `agent_reports/BORI_QA_REPORT.md`,
  `agent_reports/DORI_RELEASE_REPORT.md`(각자 소유)

## 13. 모호성 해결 (brief 해석 결정)
1. "operator/admin views" — 4명의 데모 사용자 외 operator 페르소나를
   비변경(관측 전용) 5번째 보기로 정의(5절). brief에 admin이 사용자인지
   명시되지 않았으므로, users 테이블을 바꾸지 않는 방향을 선택.
2. "인증 없음" 조건에서 현재 사용자 결정 — cookie 데모 전환으로
   해결(5절). 세션 저장소, 토큰 없음.
3. 시드 게시물 상태에 matched/completed가 있으면 신청 데이터가 필요
   → applications 3행을 시드에 포함(L2/L5).
4. 페이지당 개수는 고정 10(쿼리 파라미터 미공개) — "pagination"을
   결정적으로 유지하기 위한 선택.
5. 상태코드 체계(404/403/409/422)와 검사 순서(5.1)는 brief에 없던
   공백을 채운 확정.
6. `created_at` 정렬 대신 `id DESC` 정렬을 선택 — seed 값과 생성
   순서가 동일하므로 결정적이고 단순.

## 14. 보안/데이터/이중/롤백 영향
- 보안: 저장값은 로컬 SQLite. cookie는 HttpOnly+SameSite=Lax. XSS 렌더
  계약(8절)이 유일한 보안 게이트.
- 데이터: `*.db`는 gitignore. 시드 데이터만 고정. PII 없음(가명 데모 데이터).
- CI 영향: `quality` job은 `pyproject.toml` 존재 시 실행 — 구현 스테이지
 부터 실행된다.
- 배포/롤백: 없음(로컬 데모). 롤백 = DB 파일 삭제 후 재시작(4절).
