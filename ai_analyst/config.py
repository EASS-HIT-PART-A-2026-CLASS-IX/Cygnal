from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    anthropic_api_key: str = ""
    backend_url: str = "http://localhost:8000"
    anthropic_model: str = "claude-sonnet-4-20250514"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = AISettings()
