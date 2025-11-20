from pandas import Series
from services.position_calculators.base_metric_calculator import BaseMetricCalculator
from services.position_calculators.return_per_period_calculator import ReturnPerPeriodCalculator
from services.position_calculators.value_start_calculator import ValueStartCalculator


class ReturnPerPeriodPercentageCalculator(BaseMetricCalculator):
    def __init__(
        self,
        return_per_period_calculator: ReturnPerPeriodCalculator | None = None,
        value_start_calculator: ValueStartCalculator | None = None,
    ):
        self.return_per_period_calculator = return_per_period_calculator or ReturnPerPeriodCalculator()
        self.value_start_calculator = value_start_calculator or ValueStartCalculator()

    def calculate(self):
        value_start = self.value_start_calculator.calculated
        return_per_period = self.return_per_period_calculator.calculated
        return_per_period_percentage = Series(0.0, index=self.date_index)
        return return_per_period_percentage.mask(value_start != 0, return_per_period / value_start)
