"""Chat service — orchestrates semantic cache lookup, LLM calls, and session history."""

import time
import uuid
from typing import Optional

from langchain_openai import ChatOpenAI

from semantic_ai_agent.cache.wrapper import CacheResults, SemanticCacheWrapper
from semantic_ai_agent.domain.chat_message import ChatMessage


class ChatService:
    def __init__(
        self,
        cache: SemanticCacheWrapper,
        llm: ChatOpenAI,
        system_prompt: str,
    ):
        self.cache = cache
        self.llm = llm
        self.system_prompt = system_prompt
        self.sessions: dict[str, list[ChatMessage]] = {}

    def _ensure_session(self, session_id: Optional[str]) -> str:
        sid = session_id or str(uuid.uuid4())
        if sid not in self.sessions:
            self.sessions[sid] = []
        return sid

    def ask(self, message: str, session_id: Optional[str] = None) -> dict:
        """Process a chat message: check cache, call LLM on miss, return result dict."""
        sid = self._ensure_session(session_id)
        start = time.perf_counter()

        result = self.cache.check(message)

        if result.matches:
            match = result.matches[0]
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._append(sid, "user", message)
            self._append(sid, "assistant", match.response)
            return {
                "session_id": sid,
                "answer": match.response,
                "source": "cache_hit",
                "latency_ms": round(elapsed_ms, 2),
                "distance": round(match.vector_distance, 6),
            }

        answer = self._call_llm(sid, message)
        self.cache.store(prompt=message, response=answer)
        elapsed_ms = (time.perf_counter() - start) * 1000

        self._append(sid, "user", message)
        self._append(sid, "assistant", answer)
        return {
            "session_id": sid,
            "answer": answer,
            "source": "llm_generated",
            "latency_ms": round(elapsed_ms, 2),
            "distance": None,
        }

    def _call_llm(self, session_id: str, message: str) -> str:
        history = self.sessions.get(session_id, [])
        messages: list[dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})
        response = self.llm.invoke(messages)
        return str(response.content)

    def _append(self, session_id: str, role: str, content: str) -> None:
        self.sessions[session_id].append(
            ChatMessage(role=role, content=content)  # type: ignore[arg-type]
        )

    def get_history(self, session_id: str) -> list[ChatMessage]:
        return self.sessions.get(session_id, [])

    def check_cache(self, query: str) -> CacheResults:
        return self.cache.check(query)
