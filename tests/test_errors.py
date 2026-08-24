def test_listing_404(client):
    resp = client.get("/listings/999")
    assert resp.status_code == 404


def test_select_invalid_422(client):
    resp = client.get("/users/select/99")
    assert resp.status_code == 422


def test_select_operator_302(client):
    resp = client.get("/users/select/operator")
    assert resp.status_code == 302
