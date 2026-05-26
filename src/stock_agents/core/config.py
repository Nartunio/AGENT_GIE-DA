from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AGENT_GIE-DA"
    app_env: str = "local"
    log_level: str = "INFO"
    market_data_provider: str = "mock"
    stooq_api_key: str | None = None
    x_bearer_token: str | None = None
    x_recent_search_max_results: int = 20
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_bull_model: str = "llama3.1:8b"
    ollama_bear_model: str = "llama3.1:8b"
    ollama_judge_model: str = "llama3.1:8b"
    ollama_timeout_seconds: int = 120

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
