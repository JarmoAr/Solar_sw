from aurinko_optimo.config import settings
from aurinko_optimo.fronius import FroniusClient
from aurinko_optimo.optimizer import Optimizer
from aurinko_optimo.prices import CsvPriceProvider, PriceProvider, SimulatedPriceProvider
from aurinko_optimo.storage import Storage


def build_price_provider() -> PriceProvider:
    if settings.price_csv_path:
        return CsvPriceProvider(settings.price_csv_path)
    return SimulatedPriceProvider()


def build_optimizer() -> Optimizer:
    return Optimizer(
        negative_price_limit_eur_mwh=settings.negative_price_limit_eur_mwh,
        min_export_w=settings.min_export_w,
        max_export_w=settings.max_export_w,
    )


def build_storage() -> Storage:
    return Storage(settings.database_path)


def build_fronius_client() -> FroniusClient:
    return FroniusClient(settings.fronius_base_url)
