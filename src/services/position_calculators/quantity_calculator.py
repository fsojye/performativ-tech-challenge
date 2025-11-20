from pandas import Series

from services.position_calculators.base_metric_calculator import BaseMetricCalculator
from services.position_calculators.is_open_calculator import IsOpenCalculator


class QuantityCalculator(BaseMetricCalculator):
    def __init__(self, is_open_calculator: IsOpenCalculator | None = None):
        self.is_open_calculator = is_open_calculator or IsOpenCalculator()

    def calculate(self) -> Series:
        is_open = self.is_open_calculator.calculated
        return is_open * self.position.quantity
