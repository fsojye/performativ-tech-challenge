from pandas import Series

from models.calculator_context import CalculatorContext
from models.position_metric_fields import PositionMetricFields as pmf
from services.position_calculators.base_metric_calculator import BaseMetricCalculator
from services.position_calculators.is_open_calculator import IsOpenCalculator
from services.position_calculators.price_local_calculator import PriceLocalCalculator
from services.position_calculators.quantity_calculator import QuantityCalculator
from services.position_calculators.return_per_period_calculator import ReturnPerPeriodCalculator
from services.position_calculators.return_per_period_percentage_calculator import (
    ReturnPerPeriodPercentageCalculator,
)
from services.position_calculators.value_calculator import ValueCalculator
from services.position_calculators.value_end_calculator import ValueEndCalculator
from services.position_calculators.value_local_calculator import ValueLocalCalculator
from services.position_calculators.value_start_calculator import ValueStartCalculator


class CalculatorFactory:
    def __init__(self, calculator_context: CalculatorContext):
        self.calculator_context = calculator_context
        self._registry = {
            pmf.IS_OPEN: (IsOpenCalculator, []),
            pmf.QUANTITY: (QuantityCalculator, [pmf.IS_OPEN]),
            pmf.PRICE_LOCAL: (PriceLocalCalculator, []),
            pmf.VALUE_LOCAL: (ValueLocalCalculator, [pmf.PRICE_LOCAL, pmf.QUANTITY]),
            pmf.VALUE_TARGET: (ValueCalculator, [pmf.VALUE_LOCAL]),
            pmf.VALUE_END_TARGET: (ValueEndCalculator, [pmf.VALUE_TARGET]),
            pmf.VALUE_START_TARGET: (ValueStartCalculator, [pmf.VALUE_TARGET]),
            pmf.RETURN_PER_PERIOD: (ReturnPerPeriodCalculator, [pmf.VALUE_END_TARGET, pmf.VALUE_START_TARGET]),
            pmf.RETURN_PER_PERIOD_PERCENTAGE: (
                ReturnPerPeriodPercentageCalculator,
                [pmf.RETURN_PER_PERIOD, pmf.VALUE_START_TARGET],
            ),
        }
        self._instances: dict[pmf, BaseMetricCalculator] = {}

    def get(self, key: pmf) -> BaseMetricCalculator:
        if key in self._instances:
            return self._instances[key]

        if key not in self._registry:
            raise ValueError(f"Calculator for key {key} is not registered")
        cls, deps = self._registry.get(key)  # type: ignore

        dependencies = [self.get(dep_key) for dep_key in deps]
        instance: BaseMetricCalculator = cls(*dependencies)
        BaseMetricCalculator.__init__(instance, self.calculator_context)
        self._instances[key] = instance
        return instance

    def calculate(self, key: pmf) -> Series:
        calculator = self.get(key)
        return calculator.calculated
