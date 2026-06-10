from pydantic_settings import BaseSettings, SettingsConfigDict


class UISettings(BaseSettings):
    api_base_url: str = "http://127.0.0.1:8000"
    ai_analyst_url: str = "http://127.0.0.1:8001"
    trace_id: str = "ui-streamlit"

    model_config = SettingsConfigDict(env_prefix="CYGNAL_", env_file=".env", extra="ignore")


settings = UISettings()
