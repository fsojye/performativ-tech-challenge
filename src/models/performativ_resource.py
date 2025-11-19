from dataclasses import dataclass

from models.performativ_api import FxRatesData, PricesData


@dataclass
class PerformativResource:
    fx_rates: FxRatesData
    prices: PricesData
