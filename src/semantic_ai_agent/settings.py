"""Application settings loaded from environment variables."""

import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    CACHE_NAME: str = "semantic-cache"
    CACHE_DISTANCE_THRESHOLD: float = 0.3
    CACHE_TTL_SECONDS: int = 3600
    OPENAI_MODEL: str = "gpt-4o-mini"
    USE_MOCK_LLM: bool = False
    HR_SYSTEM_PROMPT: str = (
        "You are an HR policy assistant. Answer the employee's question about company policies "
        "concisely and accurately in 2-3 sentences."
    )
    UI_PORT: int = 10000
    API_PORT: int = 8000
    REDIS_PORT: int = 6379
    HOST: str = "0.0.0.0"  # noqa: S104
    REDIS_HOST: str = "0.0.0.0"  # noqa: S104

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def DEFAULT_FAQ_PATH(self) -> Path:
        return self.ROOT_PATH / "data/raw/faq_data.json"

    @property
    def APP_PATH(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def ROOT_PATH(self) -> Path:
        return self.APP_PATH.parent.parent

    @property
    def SOCKET_URL(self) -> str:
        return f"http://{self.HOST}:{{port}}"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{{port}}"

    @property
    def UI_EXECUTABLE(self) -> Path:
        if sys.platform == "win32":
            return self.ROOT_PATH / ".venv/Scripts/streamlit.exe"
        return self.ROOT_PATH / ".venv/bin/streamlit"

    @property
    def API_PATH(self) -> Path:
        return self.APP_PATH / "api"

    @property
    def API_HOST(self) -> str:
        return self.SOCKET_URL.format(port=self.API_PORT)


Settings = _Settings()
