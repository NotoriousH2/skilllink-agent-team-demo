from datetime import datetime

from app.db import connect

USERS = [
    (1, "김민수", "minsukim@demo.local", "2026-08-01T08:00:00"),
    (2, "이서연", "seoyeonlee@demo.local", "2026-08-01T08:00:00"),
    (3, "박준호", "junhohpark@demo.local", "2026-08-01T08:00:00"),
    (4, "최다은", "daeunchoi@demo.local", "2026-08-01T08:00:00"),
]

LISTINGS = [
    (
        1,
        1,
        "파이썬 기초 과외",
        "파이썬 기초를 다루는 1:1 과외를 제공합니다. 주 2회, 1회 60분.",
        "study",
        "offer",
        "open",
        "2026-08-01T09:00:00",
    ),
    (
        2,
        2,
        "세탁기 수리 요청",
        "세탁기가 탈수 소리를 심하게 내요. 수리 가능한 분 요청합니다.",
        "repair",
        "request",
        "open",
        "2026-08-02T10:00:00",
    ),
    (
        3,
        3,
        "주말 반찬 요리",
        "주말에 만들 반찬(김치찜, 잡채)을 함께 만들어요. 재료비는 나눠요.",
        "cooking",
        "offer",
        "open",
        "2026-08-03T11:00:00",
    ),
    (
        4,
        4,
        "노트북 점검",
        "노트북이 자주 부팅되어요. 점검 및 소프트웨어 설정을 도와주세요.",
        "tech",
        "request",
        "open",
        "2026-08-04T12:00:00",
    ),
    (
        5,
        1,
        "영어 회화 연습 파트너",
        "영어 회화를 연습할 파트너를 찾습니다. 주 1회 30분, 온라인.",
        "study",
        "request",
        "open",
        "2026-08-05T13:00:00",
    ),
    (
        6,
        2,
        "조립식 책장 설치",
        "조립식 책장 2개를 설치해 주세요. 토요일 오전 가능.",
        "repair",
        "request",
        "matched",
        "2026-08-06T14:00:00",
    ),
    (
        7,
        3,
        "카네이션 꽃다발 만들기",
        "어버이날 꽃다발을 직접 만들어드려요. 예약 필요.",
        "other",
        "offer",
        "completed",
        "2026-08-07T15:00:00",
    ),
    (
        8,
        4,
        "카페에서 사진 촬영",
        "동네 카페에서 커플/가족 사진을 찍어드려요.",
        "other",
        "offer",
        "cancelled",
        "2026-08-08T16:00:00",
    ),
]

APPLICATIONS = [
    (
        1,
        6,
        3,
        "책장 2개 설치 경험 있어요. 토요일 오전에 가능합니다.",
        "accepted",
        "2026-08-06T15:00:00",
    ),
    (
        2,
        2,
        4,
        "세탁기 탈수 문제는 보통 드럼 균형을 확인하면 해결돼요.",
        "pending",
        "2026-08-07T09:00:00",
    ),
    (
        3,
        4,
        1,
        "노트북 부팅 문제는 소프트웨어 점검으로 대부분 해결돼요.",
        "pending",
        "2026-08-07T10:00:00",
    ),
]


def now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # noqa: DTZ005


def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(
            """
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
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO users (id, name, email, created_at) VALUES (?,?,?,?)", USERS
            )
            conn.executemany(
                "INSERT INTO listings (id, owner_id, title, description, category, type, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
                LISTINGS,
            )
            conn.executemany(
                "INSERT INTO applications (id, listing_id, applicant_id, message, status, created_at) VALUES (?,?,?,?,?,?)",
                APPLICATIONS,
            )
        conn.commit()
    finally:
        conn.close()
