from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field


class ControlAction(StrEnum):
    ALLOW_EXPORT = "allow_export"
    LIMIT_EXPORT = "limit_export"
    DATA_UNAVAILABLE = "data_unavailable"


class PowerFlow(BaseModel):
    timestamp: datetime
    production_w: float | None = None
    consumption_w: float | None = None
    grid_w: float | None = None
    battery_w: float | None = None


class PricePoint(BaseModel):
    timestamp: datetime
    price_eur_mwh: float
    source: str


class ControlDecision(BaseModel):
    timestamp: datetime
    action: ControlAction
    export_limit_w: int | None
    reason: str
    price_eur_mwh: float | None = None
    price_cents_kwh: float | None = None
    net_export_price_eur_mwh: float | None = None
    net_export_price_cents_kwh: float | None = None
    grid_w: float | None = None


class ControlSettings(BaseModel):
    sales_margin_cents_kwh: float = Field(default=0.0, ge=0.0)
    limit_when_net_price_below_cents_kwh: float = 0.0
    limited_export_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    max_export_w: int = Field(default=10_000, ge=0)
