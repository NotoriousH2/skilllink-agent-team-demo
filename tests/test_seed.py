from app.db import connect


def test_seed_counts(client):
    conn = connect()
    try:
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        listings = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        applications = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    finally:
        conn.close()
    assert users == 4
    assert listings == 8
    assert applications == 3


def test_seed_values(client):
    conn = connect()
    try:
        users = conn.execute("SELECT id, name, email, created_at FROM users ORDER BY id").fetchall()
        assert [tuple(u) for u in users] == [
            (1, "김민수", "minsukim@demo.local", "2026-08-01T08:00:00"),
            (2, "이서연", "seoyeonlee@demo.local", "2026-08-01T08:00:00"),
            (3, "박준호", "junhohpark@demo.local", "2026-08-01T08:00:00"),
            (4, "최다은", "daeunchoi@demo.local", "2026-08-01T08:00:00"),
        ]
        listings = conn.execute(
            "SELECT id, owner_id, title, category, type, status FROM listings ORDER BY id"
        ).fetchall()
        expected = [
            (1, 1, "파이썬 기초 과외", "study", "offer", "open"),
            (2, 2, "세탁기 수리 요청", "repair", "request", "open"),
            (3, 3, "주말 반찬 요리", "cooking", "offer", "open"),
            (4, 4, "노트북 점검", "tech", "request", "open"),
            (5, 1, "영어 회화 연습 파트너", "study", "request", "open"),
            (6, 2, "조립식 책장 설치", "repair", "request", "matched"),
            (7, 3, "카네이션 꽃다발 만들기", "other", "offer", "completed"),
            (8, 4, "카페에서 사진 촬영", "other", "offer", "cancelled"),
        ]
        assert [tuple(l) for l in listings] == expected
        apps = conn.execute(
            "SELECT id, listing_id, applicant_id, status FROM applications ORDER BY id"
        ).fetchall()
        assert [tuple(a) for a in apps] == [
            (1, 6, 3, "accepted"),
            (2, 2, 4, "pending"),
            (3, 4, 1, "pending"),
        ]
    finally:
        conn.close()
