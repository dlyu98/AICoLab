from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CareBridge AI Agent"
    environment: str = "local"
    model_provider: str = "local-rule-based"
    openai_api_key: str | None = None
    rate_limit_per_minute: int = 120
    audit_log_path: str = "backend/app/data/audit_logs.jsonl"
    synthetic_data_dir: str = "backend/app/data/synthetic"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
