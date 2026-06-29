from datetime import datetime

from aurinko_optimo.models import ControlAction, ControlSettings, PowerFlow, PricePoint
from aurinko_optimo.optimizer import Optimizer


def test_limits_export_when_net_price_is_at_limit() -> None:
    optimizer = Optimizer(
        ControlSettings(
            sales_margin_cents_kwh=0.5,
            limit_when_net_price_below_cents_kwh=0,
            limited_export_percent=0,
            max_export_w=10000,
        )
    )
    decision = optimizer.decide(
        power=PowerFlow(timestamp=datetime.now().astimezone(), grid_w=-1200),
        price=PricePoint(
            timestamp=datetime.now().astimezone(),
            price_eur_mwh=4.0,
            source="test",
        ),
    )

    assert decision.action == ControlAction.LIMIT_EXPORT
    assert decision.export_limit_w == 0
    assert round(decision.net_export_price_eur_mwh or 0, 3) == -1.0
    assert round(decision.net_export_price_cents_kwh or 0, 3) == -0.1


def test_allows_small_export_percent_when_limited() -> None:
    optimizer = Optimizer(
        ControlSettings(
            sales_margin_cents_kwh=0.3,
            limit_when_net_price_below_cents_kwh=0,
            limited_export_percent=5,
            max_export_w=10000,
        )
    )
    decision = optimizer.decide(
        power=PowerFlow(timestamp=datetime.now().astimezone(), grid_w=-1200),
        price=PricePoint(
            timestamp=datetime.now().astimezone(),
            price_eur_mwh=2.0,
            source="test",
        ),
    )

    assert decision.action == ControlAction.LIMIT_EXPORT
    assert decision.export_limit_w == 500


def test_allows_export_when_net_price_is_positive() -> None:
    optimizer = Optimizer(
        ControlSettings(
            sales_margin_cents_kwh=0.3,
            limit_when_net_price_below_cents_kwh=0,
            limited_export_percent=0,
            max_export_w=10000,
        )
    )
    decision = optimizer.decide(
        power=PowerFlow(timestamp=datetime.now().astimezone(), grid_w=-1200),
        price=PricePoint(
            timestamp=datetime.now().astimezone(),
            price_eur_mwh=42.0,
            source="test",
        ),
    )

    assert decision.action == ControlAction.ALLOW_EXPORT
    assert decision.export_limit_w == 10000
