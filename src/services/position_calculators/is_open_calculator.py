from pandas import Series

from services.position_calculators.base_metric_calculator import BaseMetricCalculator


class IsOpenCalculator(BaseMetricCalculator):
    def __init__(self) -> None:
        pass

    def calculate(self) -> Series:
        is_open = Series(0, index=self.date_index)
        return is_open.mask(self._day_is_between_inclusive_open_and_exclusive_close(), 1)
