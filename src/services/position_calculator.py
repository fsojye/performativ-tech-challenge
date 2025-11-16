from numpy import nan
from numpy.typing import NDArray
from pandas import DataFrame, DatetimeIndex, Timedelta, Timestamp, to_datetime

from entities.financial_metrics import PositionMetric
from models.position_metric_fields import PositionMetricFields
from models.positions_data import PositionDTO


class PositionCalculator:
    def calculate(
        self,
        position: PositionDTO,
        date_index: DatetimeIndex,
        fx_rates: DataFrame,
        prices: DataFrame,
    ) -> PositionMetric:
        self._date_index = date_index
        self._fx_rates = fx_rates
        self._prices = prices

        open_date = to_datetime(position.open_date)
        close_date = to_datetime(position.close_date)

        position_df = DataFrame(index=self._date_index)

        self._price_local_calculate(position_df, open_date)
        self._price_target_calculate(position_df)
        self._open_price_target_calculate(position_df, position.open_price)
        self._close_price_target_calculate(position_df, position.close_price)
        self._is_open_calculate(position_df, open_date, close_date)
        self._quantity_calculate(position_df, position.quantity)
        self._value_local_calculate(position_df)
        self._value_target_calculate(position_df)
        self._open_value_target_calculate(position_df, position.quantity, open_date)
        self._close_value_target_calculate(position_df, position.quantity, close_date)
        self._value_end_target_calculate(position_df, close_date)
        self._value_start_target_calculate(position_df, open_date)
        self._return_per_period_calculate(position_df, open_date, close_date)
        self._return_per_period_percentage_calculate(position_df)

        return PositionMetric(
            is_open=position_df[PositionMetricFields.IS_OPEN],
            price=position_df[PositionMetricFields.PRICE_LOCAL],
            value=position_df[PositionMetricFields.VALUE_TARGET],
            return_per_period=position_df[PositionMetricFields.RETURN_PER_PERIOD],
            return_per_period_percentage=position_df[
                PositionMetricFields.RETURN_PER_PERIOD_PERCENTAGE
            ],
            value_start=position_df[PositionMetricFields.VALUE_START_TARGET],
        )

    def _day_is_pre_close(self, close_date: Timestamp) -> NDArray:
        close_bound = close_date or (
            to_datetime(self._date_index[-1].date()) + Timedelta(days=1)
        )
        return self._date_index < close_bound  # type: ignore

    def _day_is_within_open(
        self, open_date: Timestamp, close_date: Timestamp
    ) -> NDArray:
        return (self._date_index >= open_date) & self._day_is_pre_close(close_date)  # type: ignore

    def _day_is_close(self, close_date: Timestamp) -> NDArray:
        return self._date_index == close_date  # type: ignore

    def _day_is_open(self, open_date: Timestamp) -> NDArray:
        return self._date_index == open_date  # type: ignore

    def _day_is_pre_open(self, open_date: Timestamp) -> NDArray:
        return self._date_index < open_date  # type: ignore

    def _day_is_within_open_or_is_close(
        self, open_date: Timestamp, close_date: Timestamp
    ) -> NDArray:
        return self._day_is_within_open(open_date, close_date) | self._day_is_close(  # type: ignore
            close_date
        )

    def _day_is_not_open_but_is_start(self, open_date: Timestamp) -> NDArray:
        return (self._date_index != open_date) & (  # type: ignore
            self._date_index == self._date_index[0].date()
        )

    def _price_local_calculate(
        self, dataframe: DataFrame, open_date: Timestamp
    ) -> None:
        dataframe[PositionMetricFields.PRICE_LOCAL] = self._prices["price"].mask(
            self._day_is_pre_open(open_date), 0.0
        )

    def _price_target_calculate(self, dataframe: DataFrame) -> None:
        dataframe[PositionMetricFields.PRICE_TARGET] = (
            dataframe[PositionMetricFields.PRICE_LOCAL] * self._fx_rates["rate"]
        )

    def _open_price_target_calculate(
        self, dataframe: DataFrame, open_price: float
    ) -> None:
        dataframe[PositionMetricFields.OPEN_PRICE_TARGET] = (
            open_price * self._fx_rates["rate"]
        )

    def _close_price_target_calculate(
        self, dataframe: DataFrame, close_price: float | None
    ) -> None:
        dataframe[PositionMetricFields.CLOSE_PRICE_TARGET] = (
            close_price if close_price is not None else nan
        ) * self._fx_rates["rate"]

    def _is_open_calculate(
        self, dataframe: DataFrame, open_date: Timestamp, close_date: Timestamp
    ) -> None:
        dataframe[PositionMetricFields.IS_OPEN] = self._day_is_within_open(
            open_date, close_date
        ).astype(float)

    def _quantity_calculate(self, dataframe: DataFrame, quantity: float) -> None:
        dataframe[PositionMetricFields.QUANTITY] = (
            dataframe[PositionMetricFields.IS_OPEN] * quantity
        )

    def _value_local_calculate(self, dataframe: DataFrame) -> None:
        dataframe[PositionMetricFields.VALUE_LOCAL] = (
            dataframe[PositionMetricFields.PRICE_LOCAL]
            * dataframe[PositionMetricFields.QUANTITY]
        )

    def _value_target_calculate(self, dataframe: DataFrame) -> None:
        dataframe[PositionMetricFields.VALUE_TARGET] = (
            dataframe[PositionMetricFields.VALUE_LOCAL] * self._fx_rates["rate"]
        )

    def _open_value_target_calculate(
        self, dataframe: DataFrame, quantity: float, open_date: Timestamp
    ) -> None:
        dataframe[PositionMetricFields.OPEN_VALUE_TARGET] = (
            dataframe[PositionMetricFields.OPEN_PRICE_TARGET] * quantity
        ).mask(self._day_is_pre_open(open_date), 0.0)

    def _close_value_target_calculate(
        self, dataframe: DataFrame, quantity: float, close_date: Timestamp
    ) -> None:
        dataframe[PositionMetricFields.CLOSE_VALUE_TARGET] = (
            dataframe[PositionMetricFields.CLOSE_PRICE_TARGET] * quantity
        ).mask(self._day_is_pre_close(close_date), 0.0)

    def _value_end_target_calculate(
        self, dataframe: DataFrame, close_date: Timestamp
    ) -> None:
        dataframe[PositionMetricFields.VALUE_END_TARGET] = dataframe[
            PositionMetricFields.VALUE_TARGET
        ].mask(
            self._day_is_close(close_date),
            dataframe[PositionMetricFields.CLOSE_VALUE_TARGET],
        )

    def _value_start_target_calculate(
        self, dataframe: DataFrame, open_date: Timestamp
    ) -> None:
        dataframe[PositionMetricFields.VALUE_START_TARGET] = (
            dataframe[PositionMetricFields.VALUE_TARGET]
            .shift(1, fill_value=0.0)
            .mask(
                self._day_is_not_open_but_is_start(open_date),
                dataframe[PositionMetricFields.VALUE_TARGET],
            )
            .mask(
                self._day_is_open(open_date),
                dataframe[PositionMetricFields.OPEN_VALUE_TARGET],
            )
        )

    def _return_per_period_calculate(
        self, dataframe: DataFrame, open_date: Timestamp, close_date: Timestamp
    ) -> None:
        dataframe[PositionMetricFields.RETURN_PER_PERIOD] = (
            dataframe[PositionMetricFields.VALUE_END_TARGET]
            - dataframe[PositionMetricFields.VALUE_START_TARGET]
        ).where(self._day_is_within_open_or_is_close(open_date, close_date), 0.0)

    def _return_per_period_percentage_calculate(self, dataframe: DataFrame) -> None:
        dataframe[PositionMetricFields.RETURN_PER_PERIOD_PERCENTAGE] = (
            dataframe[PositionMetricFields.RETURN_PER_PERIOD]
            / dataframe[PositionMetricFields.VALUE_START_TARGET]
        ).mask(dataframe[PositionMetricFields.VALUE_START_TARGET] == 0, 0.0)
