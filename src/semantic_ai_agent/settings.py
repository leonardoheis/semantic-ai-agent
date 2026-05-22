import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    OPENAI_API_KEY: str = ""
    CACHE_NAME: str = "semantic-cache"
    CACHE_DISTANCE_THRESHOLD: float = 0.3
    CACHE_TTL_SECONDS: int = 3600
    OPENAI_MODEL: str = "gpt-5.1"
    HR_SYSTEM_PROMPT: str = (
        "You are an HR policy assistant. Answer the employee's question about company policies "
        "concisely and accurately in 2-3 sentences."
    )   
    UI_PORT: int = 10000
    API_PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def UI_EXECUTABLE(self) -> Path:
        if sys.platform == "win32":
            return self.ROOT_PATH / ".venv/Scripts/streamlit.exe"
        return self.ROOT_PATH / ".venv/bin/streamlit"

Settings = _Settings()