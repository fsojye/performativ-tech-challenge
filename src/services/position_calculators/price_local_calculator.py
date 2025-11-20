from pandas import Series

from services.position_calculators.base_metric_calculator import BaseMetricCalculator


class PriceLocalCalculator(BaseMetricCalculator):
    def __init__(self) -> None:
        pass

    def calculate(self) -> Series:
        price = Series(0.0, index=self.date_index)
        return price.where(self._day_is_pre_open(), self.prices["price"])
