from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


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
    grid_w: float | None = None
