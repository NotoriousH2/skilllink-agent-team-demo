def test_xss_title(client):
    client.cookies.set("current_user_id", "1")
    resp = client.post(
        "/listings",
        data={
            "title": "<script>alert(1)</script>",
            "description": "설명",
            "category": "other",
            "type": "offer",
        },
    )
    assert resp.status_code == 302
    new_id = resp.headers["location"].split("/")[-1]
    detail = client.get(f"/listings/{new_id}")
    assert detail.status_code == 200
    assert "<script>alert(1)</script>" not in detail.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in detail.text


def test_xss_description(client):
    client.cookies.set("current_user_id", "1")
    resp = client.post(
        "/listings",
        data={
            "title": "제목",
            "description": "<script>alert(1)</script>",
            "category": "other",
            "type": "offer",
        },
    )
    assert resp.status_code == 302
    new_id = resp.headers["location"].split("/")[-1]
    detail = client.get(f"/listings/{new_id}")
    assert "<script>alert(1)</script>" not in detail.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in detail.text


def test_xss_application_message(client):
    client.cookies.set("current_user_id", "2")
    resp = client.post(
        "/applications", data={"listing_id": "1", "message": "<script>alert(1)</script>"}
    )
    assert resp.status_code == 302
    detail = client.get("/listings/1")
    assert "<script>alert(1)</script>" not in detail.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in detail.text
