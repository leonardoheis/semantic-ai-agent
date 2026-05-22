"""Tests for GET /health."""


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "redis_connected" in data
    assert isinstance(data["redis_connected"], bool)
