from numpy import nan
from numpy.typing import NDArray
from pandas import DataFrame, DatetimeIndex, Series, Timedelta, to_datetime

from entities.financial_metrics import PositionMetric
from models.position_metric_fields import PositionMetricFields
from models.positions_data import PositionDTO
from src.models.calculator_context import CalculatorContext
from src.services.position_calculators.calculator_factory import CalculatorFactory
from models.position_metric_fields import PositionMetricFields as pmf


class PositionCalculator:
    def load_calculation_requirements(
        self, position: PositionDTO, fx_rates: DataFrame, prices: DataFrame, date_index: DatetimeIndex
    ) -> None:
        self._calculator_factory = CalculatorFactory(
            CalculatorContext(position=position, fx_rates=fx_rates, prices=prices, date_index=date_index)
        )

    def calculate(self) -> PositionMetric:
        return PositionMetric(
            return_per_period_percentage=self._calculator_factory.calculate(pmf.RETURN_PER_PERIOD_PERCENTAGE),
            is_open=self._calculator_factory.calculate(pmf.IS_OPEN),
            price=self._calculator_factory.calculate(pmf.PRICE_LOCAL),
            value=self._calculator_factory.calculate(pmf.VALUE_TARGET),
            return_per_period=self._calculator_factory.calculate(pmf.RETURN_PER_PERIOD),
            value_start=self._calculator_factory.calculate(pmf.VALUE_START_TARGET),
        )


class PositionCalculatorException(Exception):
    pass
