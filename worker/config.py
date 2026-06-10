from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    database_url: str = "sqlite:///cygnal.db"
    redis_url: str = "redis://localhost:6379/0"
    abuseipdb_api_key: str = ""
    refresh_max_concurrency: int = 4
    refresh_max_attempts: int = 3
    idempotency_ttl_seconds: int = 86400

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = WorkerSettings()
