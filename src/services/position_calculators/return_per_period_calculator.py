from pandas import Series

from services.position_calculators.base_metric_calculator import BaseMetricCalculator
from services.position_calculators.value_end_calculator import ValueEndCalculator
from services.position_calculators.value_start_calculator import ValueStartCalculator


class ReturnPerPeriodCalculator(BaseMetricCalculator):
    def __init__(
        self,
        value_end_calculator: ValueEndCalculator | None = None,
        value_start_calculator: ValueStartCalculator | None = None,
    ):
        self.value_end_calculator = value_end_calculator or ValueEndCalculator()
        self.value_start_calculator = value_start_calculator or ValueStartCalculator()

    def calculate(self) -> Series:
        value_end = self.value_end_calculator.calculated
        value_start = self.value_start_calculator.calculated

        return (value_end - value_start).where(self._day_is_between_inclusive_open_and_close(), 0)
