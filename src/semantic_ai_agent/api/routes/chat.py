"""Chat route — multi-turn conversation with semantic cache."""

from dependency_injector.wiring import inject
from fastapi import APIRouter

from semantic_ai_agent.api.dependencies import ChatServiceDependency
from semantic_ai_agent.api.schema import ChatRequest, ChatResponse
from semantic_ai_agent.services.chat.exceptions import CacheConnectionError, LLMError

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
@inject
def chat(body: ChatRequest, svc: ChatServiceDependency) -> ChatResponse:
    try:
        result = svc.ask(message=body.message, session_id=body.session_id)
    except ConnectionError as e:
        raise CacheConnectionError(detail=str(e))
    except Exception as e:
        if "openai" in (getattr(type(e), "__module__", "") or "").lower():
            raise LLMError(detail=str(e))
        raise
    return ChatResponse(**result)
