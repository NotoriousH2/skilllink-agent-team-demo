from app.db import connect


def _set_listing_status(client, listing_id, status):
    conn = connect()
    try:
        conn.execute("UPDATE listings SET status=? WHERE id=?", (status, listing_id))
        conn.commit()
    finally:
        conn.close()


def _set_app_status(client, app_id, status):
    conn = connect()
    try:
        conn.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
        conn.commit()
    finally:
        conn.close()


def test_open_cancel_owner_success(client):
    client.cookies.set("current_user_id", "1")
    resp = client.post("/listings/1/cancel")
    assert resp.status_code == 302
    conn = connect()
    try:
        row = conn.execute("SELECT status FROM listings WHERE id=1").fetchone()
    finally:
        conn.close()
    assert row["status"] == "cancelled"


def test_matched_cancel_owner_success(client):
    client.cookies.set("current_user_id", "2")
    resp = client.post("/listings/6/cancel")
    assert resp.status_code == 302
    conn = connect()
    try:
        row = conn.execute("SELECT status FROM listings WHERE id=6").fetchone()
    finally:
        conn.close()
    assert row["status"] == "cancelled"


def test_matched_complete_owner_success(client):
    client.cookies.set("current_user_id", "2")
    resp = client.post("/listings/6/complete")
    assert resp.status_code == 302
    conn = connect()
    try:
        row = conn.execute("SELECT status FROM listings WHERE id=6").fetchone()
    finally:
        conn.close()
    assert row["status"] == "completed"


def test_completed_complete_409(client):
    client.cookies.set("current_user_id", "3")
    resp = client.post("/listings/7/complete")
    assert resp.status_code == 409


def test_cancelled_cancel_409(client):
    client.cookies.set("current_user_id", "4")
    resp = client.post("/listings/8/cancel")
    assert resp.status_code == 409


def test_pending_accept_side_effects(client):
    client.cookies.set("current_user_id", "2")
    resp = client.post("/applications/2/accept")
    assert resp.status_code == 302
    conn = connect()
    try:
        listing = conn.execute("SELECT status FROM listings WHERE id=2").fetchone()
        app2 = conn.execute("SELECT status FROM applications WHERE id=2").fetchone()
    finally:
        conn.close()
    assert listing["status"] == "matched"
    assert app2["status"] == "accepted"


def test_pending_reject(client):
    client.cookies.set("current_user_id", "2")
    resp = client.post("/applications/2/reject")
    assert resp.status_code == 302
    conn = connect()
    try:
        app2 = conn.execute("SELECT status FROM applications WHERE id=2").fetchone()
    finally:
        conn.close()
    assert app2["status"] == "rejected"


def test_pending_cancel(client):
    client.cookies.set("current_user_id", "4")
    resp = client.post("/applications/2/cancel")
    assert resp.status_code == 302
    conn = connect()
    try:
        app2 = conn.execute("SELECT status FROM applications WHERE id=2").fetchone()
    finally:
        conn.close()
    assert app2["status"] == "cancelled"


def test_accepted_accept_409(client):
    client.cookies.set("current_user_id", "2")
    resp = client.post("/applications/1/accept")
    assert resp.status_code == 409


def test_matched_listing_apply_409(client):
    client.cookies.set("current_user_id", "3")
    resp = client.post("/applications", data={"listing_id": "6", "message": "신청합니다"})
    assert resp.status_code == 409


def test_duplicate_pending_apply_409(client):
    client.cookies.set("current_user_id", "3")
    resp = client.post("/applications", data={"listing_id": "1", "message": "첫 신청"})
    assert resp.status_code == 302
    resp = client.post("/applications", data={"listing_id": "1", "message": "중복 신청"})
    assert resp.status_code == 409
