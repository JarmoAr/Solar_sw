from datetime import datetime

from aurinko_optimo.models import ControlAction, PowerFlow, PricePoint
from aurinko_optimo.optimizer import Optimizer


def test_limits_export_when_price_is_negative() -> None:
    optimizer = Optimizer(negative_price_limit_eur_mwh=0, min_export_w=0, max_export_w=10000)
    decision = optimizer.decide(
        power=PowerFlow(timestamp=datetime.now().astimezone(), grid_w=-1200),
        price=PricePoint(
            timestamp=datetime.now().astimezone(),
            price_eur_mwh=-1.0,
            source="test",
        ),
    )

    assert decision.action == ControlAction.LIMIT_EXPORT
    assert decision.export_limit_w == 0


def test_allows_export_when_price_is_positive() -> None:
    optimizer = Optimizer(negative_price_limit_eur_mwh=0, min_export_w=0, max_export_w=10000)
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
