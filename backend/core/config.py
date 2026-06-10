from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cygnal"
    default_page_size: int = 20
    database_url: str = "sqlite:///cygnal.db"
    jwt_secret_key: str = "cygnal-development-secret-change-me"
    jwt_issuer: str = "cygnal-api"
    jwt_audience: str = "cygnal-clients"
    access_token_expire_minutes: int = 30
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 100

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
