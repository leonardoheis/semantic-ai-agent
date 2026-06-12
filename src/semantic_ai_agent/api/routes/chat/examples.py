"""OpenAPI request body examples for chat routes."""

from fastapi.openapi.models import Example

from .schema import ChatRequest

CHAT_EXAMPLES: dict[str, Example] = {
    "new_session": {
        "summary": "New session",
        "description": "Start a **new** conversation session — no \
        `session_id` required.",
        "value": ChatRequest.create_example().model_dump(),
    },
    "continue_session": {
        "summary": "Continue session",
        "description": "Continue an **existing** session by passing the \
        `session_id` returned by a prior call.",
        "value": ChatRequest.create_example(
            message="Does that apply to part-time employees too?"
        ).model_dump()
        | {"session_id": "550e8400-e29b-41d4-a716-446655440000"},
    },
    "leave_policy": {
        "summary": "Leave of absence",
        "description": "Ask about **parental or medical leave** entitlements.",
        "value": ChatRequest.create_example(
            message="How many weeks of parental leave am I entitled to?"
        ).model_dump(),
    },
}
