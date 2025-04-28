from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Budgets Map API"
    version: str = "0.1.0-beta"
    HOST: str
    DATABASE_URL: str
    ALLOWED_HOSTS: list[str]
    SECRET_KEY: str
    ALGORITHM: str
    OPENAI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    model_config = SettingsConfigDict(env_file="./.env")


@lru_cache()
def get_settings():
    return Settings()
