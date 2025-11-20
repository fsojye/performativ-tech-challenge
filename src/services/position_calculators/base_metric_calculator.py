from numpy import nan
from numpy.typing import NDArray
from pandas import Series, Timedelta, to_datetime

from models.calculator_context import CalculatorContext


class BaseMetricCalculator:
    def __init__(self, calculator_context: CalculatorContext):
        self.position = calculator_context.position
        self.open_date = to_datetime(self.position.open_date)
        self.close_date = to_datetime(self.position.close_date)
        self.date_index = calculator_context.date_index
        self.fx_rates = calculator_context.fx_rates
        self.prices = calculator_context.prices
        self._calculated: Series | None = None

    def _day_is_start(self) -> NDArray:
        return self.date_index == self.date_index[0]  # type: ignore

    def _day_is_pre_open(self) -> NDArray:
        return self.date_index < self.open_date  # type: ignore

    def _day_is_open(self) -> NDArray:
        return self.date_index == self.open_date  # type: ignore

    def _day_is_after_open_inclusive(self) -> NDArray:
        return self.date_index >= self.open_date  # type: ignore

    def _day_is_between_inclusive_open_and_exclusive_close(self) -> NDArray:
        return self._day_is_after_open_inclusive() & self._day_is_pre_close()  # type: ignore

    def _day_is_between_inclusive_open_and_close(self) -> NDArray:
        return self._day_is_between_inclusive_open_and_exclusive_close() | self._day_is_close()  # type: ignore

    def _day_is_pre_close(self) -> NDArray:
        close_bound = self.close_date or (to_datetime(self.date_index[-1]) + Timedelta(days=1))
        return self.date_index < close_bound  # type: ignore

    def _day_is_close(self) -> NDArray:
        return self.date_index == self.close_date  # type: ignore

    def _calculate_open_value(self) -> float:
        open_fx_rate = self.fx_rates["rate"].get(self.position.open_date)
        open_fx_rate = open_fx_rate if open_fx_rate is not None else nan
        return self.position.open_price * open_fx_rate * self.position.quantity

    def _calculate_close_value(self) -> float:
        close_fx_rate = self.fx_rates["rate"].get(self.position.close_date)
        close_price = self.position.close_price if self.position.close_price is not None else nan
        close_fx_rate = close_fx_rate if close_fx_rate is not None else nan
        return close_price * close_fx_rate * self.position.quantity

    def calculate(self) -> Series:
        raise NotImplementedError()

    @property
    def calculated(self) -> Series:
        if self._calculated is None:
            self._calculated = self.calculate()
        return self._calculated
