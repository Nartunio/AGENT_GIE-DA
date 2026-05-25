from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AGENT_GIE-DA"
    app_env: str = "local"
    log_level: str = "INFO"
    x_bearer_token: str | None = None
    x_recent_search_max_results: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
