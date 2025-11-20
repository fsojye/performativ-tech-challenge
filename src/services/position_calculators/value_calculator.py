from pandas import Series

from services.position_calculators.base_metric_calculator import BaseMetricCalculator
from services.position_calculators.value_local_calculator import ValueLocalCalculator


class ValueCalculator(BaseMetricCalculator):
    def __init__(self, value_local_calculator: ValueLocalCalculator | None = None):
        self.value_local_calculator = value_local_calculator or ValueLocalCalculator()

    def calculate(self) -> Series:
        value_local = self.value_local_calculator.calculated
        return value_local * self.fx_rates["rate"]
