"""Tests for POST /chat."""


def test_chat_returns_new_session(client):
    response = client.post("/chat", json={"message": "How many vacation days do I get?"})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "answer" in data
    assert data["source"] in ("cache_hit", "llm_generated")
    assert data["latency_ms"] >= 0


def test_chat_with_session_id(client):
    r1 = client.post("/chat", json={"message": "Hello"})
    sid = r1.json()["session_id"]
    r2 = client.post("/chat", json={"session_id": sid, "message": "Follow-up question"})
    assert r2.status_code == 200
    assert r2.json()["session_id"] == sid


def test_chat_cache_hit(client, container):
    svc = container.chat_service()
    svc.cache.store(prompt="What is PTO?", response="15 days per year.")
    response = client.post("/chat", json={"message": "What is PTO?"})
    data = response.json()
    assert data["source"] == "cache_hit"
    assert data["answer"] == "15 days per year."


def test_chat_cache_miss(client):
    response = client.post("/chat", json={"message": "Something totally new"})
    data = response.json()
    assert data["source"] == "llm_generated"
    assert "[Mock LLM response" in data["answer"]


def test_chat_empty_message_rejected(client):
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422
