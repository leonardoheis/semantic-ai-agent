"""Unit tests for ChatService logic."""

from semantic_ai_agent.injections.test import create_mock_chat_service


def test_ask_returns_llm_on_miss():
    svc = create_mock_chat_service()
    result = svc.ask("What is the PTO policy?")
    assert result["source"] == "llm_generated"
    assert result["session_id"]
    assert result["latency_ms"] >= 0


def test_ask_returns_cache_hit_after_store():
    svc = create_mock_chat_service()
    svc.store.store(prompt="What is PTO?", response="15 days.")
    result = svc.ask("What is PTO?")
    assert result["source"] == "cache_hit"
    assert result["answer"] == "15 days."
    assert result["distance"] == 0.0


def test_session_persists_across_calls():
    svc = create_mock_chat_service()
    r1 = svc.ask("Hello")
    sid = r1["session_id"]
    r2 = svc.ask("Follow-up", session_id=sid)
    assert r2["session_id"] == sid
    history = svc.get_history(sid)
    assert len(history) == 4  # 2 user + 2 assistant


def test_new_session_created_when_none():
    svc = create_mock_chat_service()
    r1 = svc.ask("Question 1")
    r2 = svc.ask("Question 2")
    assert r1["session_id"] != r2["session_id"]
