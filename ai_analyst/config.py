from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    backend_url: str = "http://localhost:8000"
    ollama_base_url: str = ""
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = AISettings()
