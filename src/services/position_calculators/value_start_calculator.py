from pandas import Series

from services.position_calculators.base_metric_calculator import BaseMetricCalculator
from services.position_calculators.value_calculator import ValueCalculator


class ValueStartCalculator(BaseMetricCalculator):
    def __init__(self, value_calculator: ValueCalculator | None = None):
        self.value_calculator = value_calculator or ValueCalculator()

    def calculate(self) -> Series:
        open_value = self._calculate_open_value()
        value = self.value_calculator.calculated
        value_start = value.shift(1)
        value_start = value_start.mask(self._day_is_start(), value)
        value_start = value_start.mask(self._day_is_open(), open_value)
        return value_start
