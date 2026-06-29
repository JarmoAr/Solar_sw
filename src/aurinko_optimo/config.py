from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    fronius_base_url: str = "http://192.0.2.50"
    database_path: Path = Path("./data/aurinko.db")
    control_mode: str = Field(default="simulate", pattern="^(simulate|disabled)$")
    price_csv_path: Path | None = None
    negative_price_limit_eur_mwh: float = 0.0
    min_export_w: int = 0
    max_export_w: int = 10_000


settings = Settings()
