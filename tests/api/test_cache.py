"""Tests for cache management endpoints."""


def test_clear_cache(client):
    response = client.delete("/cache")
    assert response.status_code == 200
    assert response.json()["detail"] == "Cache cleared"


def test_hydrate_missing_file(client):
    response = client.post("/cache/hydrate", json={"faq_path": "/nonexistent/path.json"})
    assert response.status_code == 404
