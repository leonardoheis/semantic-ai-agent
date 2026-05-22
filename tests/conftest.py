"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient

from semantic_ai_agent.api.app import create_app
from semantic_ai_agent.injections.test import TestContainer, create_mock_chat_service


@pytest.fixture()
def container():
    c = TestContainer()
    c.wire()
    yield c
    c.unwire()


@pytest.fixture()
def chat_service():
    return create_mock_chat_service()


@pytest.fixture()
def client(container):
    app = create_app()
    return TestClient(app)
