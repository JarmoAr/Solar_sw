from datetime import datetime

from aurinko_optimo.models import ControlAction, ControlDecision, ControlSettings, PowerFlow, PricePoint


class Optimizer:
    def __init__(self, settings: ControlSettings) -> None:
        self.settings = settings

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
        price_cents_kwh = price.price_eur_mwh / 10
        net_export_price_cents_kwh = price_cents_kwh - self.settings.sales_margin_cents_kwh
        net_export_price_eur_mwh = net_export_price_cents_kwh * 10
        if net_export_price_cents_kwh <= self.settings.limit_when_net_price_below_cents_kwh:
            export_limit_w = round(self.settings.max_export_w * (self.settings.limited_export_percent / 100))
            return ControlDecision(
                timestamp=now,
                action=ControlAction.LIMIT_EXPORT,
                export_limit_w=export_limit_w,
                reason="Net export price is at or below the configured limit.",
                price_eur_mwh=price.price_eur_mwh,
                price_cents_kwh=price_cents_kwh,
                net_export_price_eur_mwh=net_export_price_eur_mwh,
                net_export_price_cents_kwh=net_export_price_cents_kwh,
                grid_w=grid_w,
            )

        return ControlDecision(
            timestamp=now,
            action=ControlAction.ALLOW_EXPORT,
            export_limit_w=self.settings.max_export_w,
            reason="Net export price is above the configured limit.",
            price_eur_mwh=price.price_eur_mwh,
            price_cents_kwh=price_cents_kwh,
            net_export_price_eur_mwh=net_export_price_eur_mwh,
            net_export_price_cents_kwh=net_export_price_cents_kwh,
            grid_w=grid_w,
        )
