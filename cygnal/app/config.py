from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Cygnal"
    default_page_size: int = 20
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()