"""Shared test fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from semantic_ai_agent.api.app import create_app
from semantic_ai_agent.injections.test import TestContainer, create_mock_chat_service
from semantic_ai_agent.services.chat.chat import ChatService


@pytest.fixture
def container() -> Iterator[TestContainer]:
    c = TestContainer()
    c.wire()
    yield c
    c.unwire()


@pytest.fixture
def chat_service() -> ChatService:
    return create_mock_chat_service()


@pytest.fixture
def client(_container: TestContainer) -> TestClient:
    app = create_app()
    return TestClient(app)
