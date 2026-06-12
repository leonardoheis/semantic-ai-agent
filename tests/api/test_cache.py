"""Tests for cache management endpoints."""

from fastapi.testclient import TestClient
from starlette import status


def test_clear_cache(client: TestClient) -> None:
    response = client.delete("/cache")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Cache cleared"


def test_hydrate_ok(client: TestClient) -> None:
    response = client.post("/cache/hydrate", json={})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "entriesLoaded" in data
    assert "categories" in data
