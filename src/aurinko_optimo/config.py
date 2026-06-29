from pathlib import Path

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    fronius_base_url: str = "http://192.0.2.50"
    database_path: Path = Path("./data/aurinko.db")
    control_mode: str = Field(default="simulate", pattern="^(simulate|disabled)$")
    price_csv_path: Path | None = None
    sales_margin_cents_kwh: float = 0.0
    limit_when_net_price_below_cents_kwh: float = 0.0
    limited_export_percent: float = 0.0
    max_export_w: int = 10_000

    @field_validator("price_csv_path", mode="before")
    @classmethod
    def empty_price_csv_path_is_none(cls, value: object) -> object:
        return None if value == "" else value


settings = Settings()
