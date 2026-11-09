def test_health_returns_pong(client):
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_health_rejects_post(client):
    response = client.post("/api/v1/health/")

    assert response.status_code == 405


def test_health_schema():
    from drf_spectacular.generators import SchemaGenerator

    schema = SchemaGenerator().get_schema(request=None, public=True)
    response = schema["paths"]["/api/v1/health/"]["get"]["responses"]["200"]
    assert response["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/HealthResponse"
    }
    assert (
        schema["components"]["schemas"]["HealthResponse"]["properties"]["message"][
            "type"
        ]
        == "string"
    )
    assert "message" in schema["components"]["schemas"]["HealthResponse"]["required"]
