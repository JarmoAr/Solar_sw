from aurinko_optimo.config import settings
from aurinko_optimo.fronius import FroniusClient
from aurinko_optimo.models import ControlSettings
from aurinko_optimo.optimizer import Optimizer
from aurinko_optimo.prices import CsvPriceProvider, PriceProvider, SimulatedPriceProvider
from aurinko_optimo.storage import Storage


def build_price_provider() -> PriceProvider:
    if settings.price_csv_path:
        return CsvPriceProvider(settings.price_csv_path)
    return SimulatedPriceProvider()


def default_control_settings() -> ControlSettings:
    return ControlSettings(
        sales_margin_cents_kwh=settings.sales_margin_cents_kwh,
        limit_when_net_price_below_cents_kwh=settings.limit_when_net_price_below_cents_kwh,
        limited_export_percent=settings.limited_export_percent,
        max_export_w=settings.max_export_w,
    )


def build_optimizer(control_settings: ControlSettings | None = None) -> Optimizer:
    return Optimizer(control_settings or default_control_settings())


def build_storage() -> Storage:
    return Storage(settings.database_path)


def build_fronius_client() -> FroniusClient:
    return FroniusClient(settings.fronius_base_url)
