from numpy import nan
from numpy.typing import NDArray
from pandas import DataFrame, DatetimeIndex, Series, Timedelta, to_datetime

from entities.financial_metrics import PositionMetric
from models.position_metric_fields import PositionMetricFields
from models.positions_data import PositionDTO


class PositionCalculator:
    def load_calculation_requirements(self, position: PositionDTO, fx_rates: DataFrame, prices: DataFrame) -> None:
        self._position = position
        self._fx_rates = fx_rates
        self._prices = prices
        self._open_date = to_datetime(self._position.open_date)
        self._close_date = to_datetime(self._position.close_date)

    def calculate_open_value(self) -> float:
        open_fx_rate = self._fx_rates["rate"].get(self._position.open_date)
        open_fx_rate = open_fx_rate if open_fx_rate is not None else nan
        return self._position.open_price * open_fx_rate * self._position.quantity

    def calculate_close_value(self) -> float:
        close_fx_rate = self._fx_rates["rate"].get(self._position.close_date)
        close_price = self._position.close_price if self._position.close_price is not None else nan
        close_fx_rate = close_fx_rate if close_fx_rate is not None else nan
        return close_price * close_fx_rate * self._position.quantity

    def calculate_price_local(self, date_index: DatetimeIndex) -> Series[float]:
        price = Series(0.0, index=date_index).where(self._day_is_pre_open(date_index), self._prices["price"])
        return price.mask(self._day_is_pre_open(date_index), 0)

    def calculate_price(self, date_index: DatetimeIndex, price_local: Series[float]) -> Series[float]:
        price_local = price_local.reindex(date_index)
        fx_rates = self._fx_rates["rate"].reindex(date_index)

        return price_local * fx_rates

    def calculate_is_open(self, date_index: DatetimeIndex) -> Series[float]:
        is_open = Series(0.0, index=date_index).mask(self._day_is_within_open(date_index), 1.0)
        return is_open

    def calculate_quantity(self, date_index: DatetimeIndex, is_open: Series[float]) -> Series[float]:
        is_open = is_open.reindex(date_index)
        return is_open * self._position.quantity

    def calculate_value_local(
        self, date_index: DatetimeIndex, price_local: Series[float], quantity: Series[float]
    ) -> Series[float]:
        price_local = price_local.reindex(date_index)
        quantity = quantity.reindex(date_index)
        return price_local * quantity

    def calculate_value(self, date_index: DatetimeIndex, value_local: Series[float]) -> Series[float]:
        value_local = value_local.reindex(date_index)
        fx_rates = self._fx_rates["rate"].reindex(date_index)
        return value_local * fx_rates

    def calculate_value_start(self, date_index: DatetimeIndex, value: Series[float]) -> Series[float]:
        open_value = self.calculate_open_value()
        value_start = value.reindex(date_index).shift(1, fill_value=0.0)
        value_start = value_start.mask(date_index == date_index[0].date(), value)
        value_start = value_start.mask(date_index == self._position.open_date, open_value)
        return value_start

    def calculate_value_end(self, date_index: DatetimeIndex, value: Series[float]) -> Series[float]:
        close_value = self.calculate_close_value()
        value_end = value.where(self._day_is_pre_close(date_index)).mask(
            date_index == self._position.close_date, close_value
        )
        return value_end

    def calculate_return_per_period(
        self, date_index: DatetimeIndex, value_end: Series[float], value_start: Series[float]
    ) -> Series[float]:
        return_per_period = Series(0.0, index=date_index).mask(
            self._day_is_within_open_or_is_close(date_index), value_end - value_start
        )
        return return_per_period

    def calculate_return_per_period_percentage(
        self, date_index: DatetimeIndex, value_start: Series[float], return_per_period: Series[float]
    ) -> Series[float]:
        return_per_period_percentage = Series(0.0, index=date_index).mask(
            value_start != 0, return_per_period / value_start
        )
        return return_per_period_percentage

    def calculate(self, date_index: DatetimeIndex) -> PositionMetric:
        self._date_index = date_index

        position_df = DataFrame(index=self._date_index)
        position_df[PositionMetricFields.PRICE_LOCAL] = self.calculate_price_local(date_index)
        position_df[PositionMetricFields.PRICE_TARGET] = self.calculate_price(
            date_index, position_df[PositionMetricFields.PRICE_LOCAL]
        )
        position_df[PositionMetricFields.IS_OPEN] = self.calculate_is_open(date_index)
        position_df[PositionMetricFields.QUANTITY] = self.calculate_quantity(
            date_index, position_df[PositionMetricFields.IS_OPEN]
        )
        position_df[PositionMetricFields.VALUE_LOCAL] = self.calculate_value_local(
            date_index, position_df[PositionMetricFields.PRICE_LOCAL], position_df[PositionMetricFields.QUANTITY]
        )
        position_df[PositionMetricFields.VALUE_TARGET] = self.calculate_value(
            date_index, position_df[PositionMetricFields.VALUE_LOCAL]
        )
        position_df[PositionMetricFields.VALUE_START_TARGET] = self.calculate_value_start(
            date_index, position_df[PositionMetricFields.VALUE_TARGET]
        )
        position_df[PositionMetricFields.VALUE_END_TARGET] = self.calculate_value_end(
            date_index, position_df[PositionMetricFields.VALUE_TARGET]
        )
        position_df[PositionMetricFields.RETURN_PER_PERIOD] = self.calculate_return_per_period(
            date_index,
            position_df[PositionMetricFields.VALUE_END_TARGET],
            position_df[PositionMetricFields.VALUE_START_TARGET],
        )
        position_df[PositionMetricFields.RETURN_PER_PERIOD_PERCENTAGE] = self.calculate_return_per_period_percentage(
            date_index,
            position_df[PositionMetricFields.VALUE_START_TARGET],
            position_df[PositionMetricFields.RETURN_PER_PERIOD],
        )

        return PositionMetric(
            is_open=position_df[PositionMetricFields.IS_OPEN],
            price=position_df[PositionMetricFields.PRICE_LOCAL],
            value=position_df[PositionMetricFields.VALUE_TARGET],
            return_per_period=position_df[PositionMetricFields.RETURN_PER_PERIOD],
            return_per_period_percentage=position_df[PositionMetricFields.RETURN_PER_PERIOD_PERCENTAGE],
            value_start=position_df[PositionMetricFields.VALUE_START_TARGET],
        )

    def _day_is_pre_close(self, date_index: DatetimeIndex) -> NDArray:
        close_bound = self._close_date or (to_datetime(date_index[-1].date()) + Timedelta(days=1))
        return date_index < close_bound  # type: ignore

    def _day_is_within_open(self, date_index: DatetimeIndex) -> NDArray:
        return (date_index >= self._open_date) & self._day_is_pre_close(date_index)  # type: ignore

    def _day_is_close(self, date_index: DatetimeIndex) -> NDArray:
        return date_index == self._close_date  # type: ignore

    def _day_is_pre_open(self, date_index: DatetimeIndex) -> NDArray:
        return date_index < self._open_date  # type: ignore

    def _day_is_within_open_or_is_close(self, date_index: DatetimeIndex) -> NDArray:
        return self._day_is_within_open(date_index) | self._day_is_close(date_index)  # type: ignore


class PositionCalculatorException(Exception):
    pass
