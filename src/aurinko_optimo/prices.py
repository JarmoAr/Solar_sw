import csv
from datetime import datetime, timedelta
from pathlib import Path

from aurinko_optimo.models import PricePoint


class PriceProvider:
    async def current_price(self) -> PricePoint:
        raise NotImplementedError


class CsvPriceProvider(PriceProvider):
    def __init__(self, path: Path) -> None:
        self.path = path

    async def current_price(self) -> PricePoint:
        now = datetime.now().astimezone()
        best: PricePoint | None = None
        with self.path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                timestamp = datetime.fromisoformat(row["timestamp"])
                if timestamp.tzinfo is None:
                    timestamp = timestamp.astimezone()
                price = PricePoint(
                    timestamp=timestamp,
                    price_eur_mwh=float(row["price_eur_mwh"]),
                    source=f"csv:{self.path.name}",
                )
                if timestamp <= now and (best is None or timestamp > best.timestamp):
                    best = price

        if best is None:
            raise RuntimeError(f"No usable price rows found in {self.path}")
        return best


class SimulatedPriceProvider(PriceProvider):
    async def current_price(self) -> PricePoint:
        now = datetime.now().astimezone()
        quarter = now.minute // 15
        slot = now.replace(minute=quarter * 15, second=0, microsecond=0)
        daytime = 8 <= now.hour <= 18
        price = -5.0 if daytime and now.hour in {11, 12, 13} else 45.0
        return PricePoint(
            timestamp=slot,
            price_eur_mwh=price,
            source="simulated",
        )


def next_quarter_hour(now: datetime | None = None) -> datetime:
    base = now or datetime.now().astimezone()
    minute = ((base.minute // 15) + 1) * 15
    if minute == 60:
        return (base.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    return base.replace(minute=minute, second=0, microsecond=0)
