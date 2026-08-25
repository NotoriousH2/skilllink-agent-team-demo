from app.db import connect


def _titles(html: str):
    import re

    return re.findall(r'<h3 class="card-title">(.*?)</h3>', html)


def test_create_listing_success(client):
    client.cookies.set("current_user_id", "1")
    resp = client.post(
        "/listings",
        data={
            "title": "새 게시물",
            "description": "설명입니다",
            "category": "study",
            "type": "offer",
        },
    )
    assert resp.status_code == 302
    new_id = resp.headers["location"].split("/")[-1]
    detail = client.get(f"/listings/{new_id}")
    assert detail.status_code == 200
    assert "새 게시물" in detail.text
    conn = connect()
    try:
        row = conn.execute("SELECT owner_id FROM listings WHERE id=?", (new_id,)).fetchone()
    finally:
        conn.close()
    assert row["owner_id"] == 1


def test_create_listing_validation(client):
    client.cookies.set("current_user_id", "1")
    resp = client.post(
        "/listings",
        data={"title": "   ", "description": "설명", "category": "study", "type": "offer"},
    )
    assert resp.status_code == 422
    resp = client.post(
        "/listings",
        data={"title": "제목", "description": "설명", "category": "xyz", "type": "offer"},
    )
    assert resp.status_code == 422


def test_filters(client):
    resp = client.get("/?category=study")
    assert resp.status_code == 200
    titles = _titles(resp.text)
    assert titles == ["영어 회화 연습 파트너", "파이썬 기초 과외"]

    resp = client.get("/?type=request")
    titles = _titles(resp.text)
    assert titles == [
        "조립식 책장 설치",
        "영어 회화 연습 파트너",
        "노트북 점검",
        "세탁기 수리 요청",
    ]

    resp = client.get("/?status=open")
    titles = _titles(resp.text)
    assert titles == [
        "영어 회화 연습 파트너",
        "노트북 점검",
        "주말 반찬 요리",
        "세탁기 수리 요청",
        "파이썬 기초 과외",
    ]

    resp = client.get("/?q=세탁기")
    titles = _titles(resp.text)
    assert titles == ["세탁기 수리 요청"]

    resp = client.get("/?category=study&type=request")
    titles = _titles(resp.text)
    assert titles == ["영어 회화 연습 파트너"]


def test_ordering(client):
    resp = client.get("/")
    titles = _titles(resp.text)
    assert titles[0] == "카페에서 사진 촬영"


def test_pagination(client):
    resp = client.get("/?page=2&status=open")
    assert resp.status_code == 200
    assert "조건에 맞는 게시물이 없습니다." in resp.text
    resp = client.get("/?page=0")
    assert resp.status_code == 422
    resp = client.get("/?page=abc")
    assert resp.status_code == 422
