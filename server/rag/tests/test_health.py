def test_health_returns_pong(client):
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_health_rejects_post(client):
    response = client.post("/api/v1/health/")

    assert response.status_code == 405
