"""Chat — orchestrates semantic cache lookup, LLM calls, and session history."""

import time
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from semantic_ai_agent.domain.chat_message import ChatMessage
from semantic_ai_agent.domain.chat_result import ChatResult
from semantic_ai_agent.domain.protocols import CacheReader, CacheWriter


class ChatService(BaseModel):
    cache: CacheReader = Field(..., description="CacheQueryService — used for lookups.")
    store: CacheWriter = Field(..., description="CacheStoreService — used for writing new entries.")
    llm: Any = Field(..., description="The LLM to use for generating responses.")
    system_prompt: str = Field(
        ..., description="The system prompt to use for generating responses."
    )
    sessions: dict[str, list[ChatMessage]] = Field(
        default_factory=dict, description="In-memory conversation history keyed by session ID."
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _ensure_session(self, session_id: str | None) -> str:
        sid = session_id or str(uuid.uuid4())
        if sid not in self.sessions:
            self.sessions[sid] = []
        return sid

    def ask(self, message: str, session_id: str | None = None) -> ChatResult:
        """Process a chat message: check cache, call LLM on miss, return result dict.
        Returns:
            ChatResult object containing the session ID, answer, source, latency, and distance.
        """
        sid = self._ensure_session(session_id)
        start = time.perf_counter()

        result = self.cache.check(message)

        if result.matches:
            match = result.matches[0]
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._append(sid, "user", message)
            self._append(sid, "assistant", match.response)
            return ChatResult(
                session_id=sid,
                answer=match.response,
                source="cache_hit",
                latency_ms=round(elapsed_ms, 2),
                distance=round(match.vector_distance, 6),
            )

        answer = self._call_llm(sid, message)
        self.store.store(prompt=message, response=answer)
        elapsed_ms = (time.perf_counter() - start) * 1000

        self._append(sid, "user", message)
        self._append(sid, "assistant", answer)
        return ChatResult(
            session_id=sid,
            answer=answer,
            source="llm_generated",
            latency_ms=round(elapsed_ms, 2),
            distance=None,
        )

    def _call_llm(self, session_id: str, message: str) -> str:
        history = self.sessions.get(session_id, [])
        messages: list[dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
        messages.extend({"role": msg.role, "content": msg.content} for msg in history)
        messages.append({"role": "user", "content": message})
        response = self.llm.invoke(messages)
        return str(response.content)

    def _append(self, session_id: str, role: str, content: str) -> None:
        self.sessions[session_id].append(
            ChatMessage(role=role, content=content)  # type: ignore[arg-type]
        )

    def get_history(self, session_id: str) -> list[ChatMessage]:
        """Get the chat history for a given session ID.
        Returns:
            List of ChatMessage objects representing the chat history.
        """
        return self.sessions.get(session_id, [])
