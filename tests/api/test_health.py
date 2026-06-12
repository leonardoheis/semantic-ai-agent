"""Tests for GET /health."""

from fastapi.testclient import TestClient
from starlette import status


def test_health_returns_200(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "redisConnected" in data
    assert isinstance(data["redisConnected"], bool)
