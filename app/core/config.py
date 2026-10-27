from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Budget Tracker"
    database_url: str
    test_database_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()