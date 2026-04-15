from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("backend/.env", ".env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Amahoro Backend", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")

    database_url: str = Field(alias="DATABASE_URL")

    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    session_cookie_name: str = Field(default="amahoro_session", alias="SESSION_COOKIE_NAME")
    session_duration_hours: int = Field(default=168, alias="SESSION_DURATION_HOURS")
    session_cookie_secure: bool = Field(default=False, alias="SESSION_COOKIE_SECURE")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    chatgroq_api_key: str = Field(default="", alias="CHATGROQ_API_KEY")
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")
    tavily_timeout_seconds: float = Field(default=15.0, alias="TAVILY_TIMEOUT_SECONDS")
    tavily_max_results: int = Field(default=4, alias="TAVILY_MAX_RESULTS")
    primary_llm_timeout_seconds: float = Field(default=10.0, alias="PRIMARY_LLM_TIMEOUT_SECONDS")
    fallback_llm_timeout_seconds: float = Field(default=15.0, alias="FALLBACK_LLM_TIMEOUT_SECONDS")

    llm_retry_attempts: int = Field(default=3, alias="LLM_RETRY_ATTEMPTS")
    llm_retry_base_delay_seconds: float = Field(default=0.5, alias="LLM_RETRY_BASE_DELAY_SECONDS")
    llm_retry_max_delay_seconds: float = Field(default=6.0, alias="LLM_RETRY_MAX_DELAY_SECONDS")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def async_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgresql+asyncpg://"):
            return url
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            return "postgresql+asyncpg://" + url[len("postgresql://") :]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
