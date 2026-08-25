def test_non_owner_edit_403(client):
    client.cookies.set("current_user_id", "2")
    resp = client.post(
        "/listings/1",
        data={"title": "변경", "description": "설명", "category": "study", "type": "offer"},
    )
    assert resp.status_code == 403


def test_self_apply_403(client):
    client.cookies.set("current_user_id", "1")
    resp = client.post("/applications", data={"listing_id": "1", "message": "자기 신청"})
    assert resp.status_code == 403


def test_operator_create_403(client):
    client.cookies.set("current_user_id", "operator")
    resp = client.post(
        "/listings",
        data={"title": "운영자", "description": "설명", "category": "study", "type": "offer"},
    )
    assert resp.status_code == 403


def test_operator_accept_403(client):
    client.cookies.set("current_user_id", "operator")
    resp = client.post("/applications/2/accept")
    assert resp.status_code == 403


def test_matched_cancel_non_owner_403(client):
    client.cookies.set("current_user_id", "3")
    resp = client.post("/listings/6/cancel")
    assert resp.status_code == 403
    client.cookies.set("current_user_id", "2")
    resp = client.post("/listings/6/cancel")
    assert resp.status_code == 302


def test_user_admin_403(client):
    client.cookies.set("current_user_id", "1")
    resp = client.get("/admin")
    assert resp.status_code == 403


def test_operator_activity_403(client):
    client.cookies.set("current_user_id", "operator")
    resp = client.get("/activity")
    assert resp.status_code == 403
