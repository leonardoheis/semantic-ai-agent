"""Tests for cache management endpoints."""


def test_clear_cache(client):
    response = client.delete("/cache")
    assert response.status_code == 200
    assert response.json()["detail"] == "Cache cleared"


def test_hydrate_ok(client):
    response = client.post("/cache/hydrate", json={})
    assert response.status_code == 200
    data = response.json()
    assert "entriesLoaded" in data
    assert "categories" in data
