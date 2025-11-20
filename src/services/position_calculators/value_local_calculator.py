from pandas import Series

from services.position_calculators.base_metric_calculator import BaseMetricCalculator
from services.position_calculators.price_local_calculator import PriceLocalCalculator
from services.position_calculators.quantity_calculator import QuantityCalculator


class ValueLocalCalculator(BaseMetricCalculator):
    def __init__(
        self,
        price_local_calculator: PriceLocalCalculator | None = None,
        quantity_calculator: QuantityCalculator | None = None,
    ):
        self.price_local_calculator = price_local_calculator or PriceLocalCalculator()
        self.quantity_calculator = quantity_calculator or QuantityCalculator()

    def calculate(self) -> Series:
        price_local = self.price_local_calculator.calculated
        quantity = self.quantity_calculator.calculated
        return price_local * quantity
