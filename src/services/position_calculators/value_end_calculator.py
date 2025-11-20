from pandas import Series

from services.position_calculators.base_metric_calculator import BaseMetricCalculator
from services.position_calculators.value_calculator import ValueCalculator


class ValueEndCalculator(BaseMetricCalculator):
    def __init__(self, value_calculator: ValueCalculator | None = None):
        self.value_calculator = value_calculator or ValueCalculator()

    def calculate(self) -> Series:
        close_value = self._calculate_close_value()
        value = self.value_calculator.calculated
        return value.where(self._day_is_pre_close()).mask(self._day_is_close(), close_value)
