from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NOC Network Quality Monitoring API"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./database/noc.db"
    monitor_interval_seconds: int = 30
    monitor_probe_count: int = 4
    monitor_timeout_seconds: float = 1.0
    simulation_mode_default: str = "normal"

    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_parse_mode: str = "HTML"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
