from datetime import datetime

from aurinko_optimo.models import ControlAction, ControlDecision, PowerFlow, PricePoint


class Optimizer:
    def __init__(self, negative_price_limit_eur_mwh: float, min_export_w: int, max_export_w: int) -> None:
        self.negative_price_limit_eur_mwh = negative_price_limit_eur_mwh
        self.min_export_w = min_export_w
        self.max_export_w = max_export_w

    def decide(self, power: PowerFlow | None, price: PricePoint | None) -> ControlDecision:
        now = datetime.now().astimezone()
        if price is None:
            return ControlDecision(
                timestamp=now,
                action=ControlAction.DATA_UNAVAILABLE,
                export_limit_w=None,
                reason="Price data is unavailable.",
            )

        grid_w = power.grid_w if power else None
        if price.price_eur_mwh <= self.negative_price_limit_eur_mwh:
            return ControlDecision(
                timestamp=now,
                action=ControlAction.LIMIT_EXPORT,
                export_limit_w=self.min_export_w,
                reason="Electricity price is at or below the negative-price limit.",
                price_eur_mwh=price.price_eur_mwh,
                grid_w=grid_w,
            )

        return ControlDecision(
            timestamp=now,
            action=ControlAction.ALLOW_EXPORT,
            export_limit_w=self.max_export_w,
            reason="Electricity price is above the negative-price limit.",
            price_eur_mwh=price.price_eur_mwh,
            grid_w=grid_w,
        )
