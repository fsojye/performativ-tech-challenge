from datetime import date
from numpy import nan
from pandas import DataFrame, Timedelta, Timestamp, date_range, to_datetime
from entities.position import PositionDayValuationFields
from models.positions_data import PositionDTO


class PositionMetricCalculator:
    fx_rates: DataFrame
    prices: DataFrame

    def calculate_metrics(
        self, position: PositionDTO, start_date: date, end_date: date
    ) -> DataFrame:
        self._date_series_index = date_range(start_date, end_date)
        open_date = to_datetime(position.open_date)
        close_date = to_datetime(position.close_date)
        position_df = DataFrame(index=self._date_series_index)

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
        self._value_start_target_calculate(
            position_df, open_date, self._date_series_index[0].date()
        )
        self._return_per_period_calculate(position_df, open_date, close_date)
        self._return_per_period_percentage_calculate(position_df)

        return position_df

    def _day_is_pre_close(self, close_date: Timestamp):
        close_bound = close_date or (
            to_datetime(self._date_series_index[-1].date()) + Timedelta(days=1)
        )
        return self._date_series_index < close_bound

    def _day_is_within_open(self, open_date: Timestamp, close_date: Timestamp):
        return (self._date_series_index >= open_date) & self._day_is_pre_close(
            close_date
        )

    def _day_is_close(self, close_date: Timestamp):
        return self._date_series_index == close_date

    def _day_is_open(self, open_date: Timestamp):
        return self._date_series_index == open_date

    def _day_is_pre_open(self, open_date: Timestamp):
        return self._date_series_index < open_date

    def _day_is_within_open_or_is_close(
        self, open_date: Timestamp, close_date: Timestamp
    ):
        return self._day_is_within_open(open_date, close_date) | self._day_is_close(
            close_date
        )

    def _day_is_not_open_but_is_start(self, open_date: Timestamp, start_date: date):
        return (self._date_series_index != open_date) & (
            self._date_series_index == start_date
        )

    def _price_local_calculate(self, dataframe: DataFrame, open_date: Timestamp):
        dataframe[PositionDayValuationFields.PRICE_LOCAL] = self.prices["price"].mask(
            self._day_is_pre_open(open_date), 0.0
        )

    def _price_target_calculate(self, dataframe: DataFrame):
        dataframe[PositionDayValuationFields.PRICE_TARGET] = (
            dataframe[PositionDayValuationFields.PRICE_LOCAL] * self.fx_rates["rate"]
        )

    def _open_price_target_calculate(self, dataframe: DataFrame, open_price: float):
        dataframe[PositionDayValuationFields.OPEN_PRICE_TARGET] = (
            open_price * self.fx_rates["rate"]
        )

    def _close_price_target_calculate(self, dataframe: DataFrame, close_price: float):
        dataframe[PositionDayValuationFields.CLOSE_PRICE_TARGET] = (
            close_price if close_price is not None else nan
        ) * self.fx_rates["rate"]

    def _is_open_calculate(
        self, dataframe: DataFrame, open_date: Timestamp, close_date: Timestamp
    ):
        dataframe[PositionDayValuationFields.IS_OPEN] = self._day_is_within_open(
            open_date, close_date
        ).astype(float)

    def _quantity_calculate(self, dataframe: DataFrame, quantity: float):
        dataframe[PositionDayValuationFields.QUANTITY] = (
            dataframe[PositionDayValuationFields.IS_OPEN] * quantity
        )

    def _value_local_calculate(self, dataframe: DataFrame):
        dataframe[PositionDayValuationFields.VALUE_LOCAL] = (
            dataframe[PositionDayValuationFields.PRICE_LOCAL]
            * dataframe[PositionDayValuationFields.QUANTITY]
        )

    def _value_target_calculate(self, dataframe: DataFrame):
        dataframe[PositionDayValuationFields.VALUE_TARGET] = (
            dataframe[PositionDayValuationFields.VALUE_LOCAL] * self.fx_rates["rate"]
        )

    def _open_value_target_calculate(
        self, dataframe: DataFrame, quantity: float, open_date: Timestamp
    ):
        dataframe[PositionDayValuationFields.OPEN_VALUE_TARGET] = (
            dataframe[PositionDayValuationFields.OPEN_PRICE_TARGET] * quantity
        ).mask(self._day_is_pre_open(open_date), 0.0)

    def _close_value_target_calculate(
        self, dataframe: DataFrame, quantity: float, close_date: Timestamp
    ):
        dataframe[PositionDayValuationFields.CLOSE_VALUE_TARGET] = (
            dataframe[PositionDayValuationFields.CLOSE_PRICE_TARGET] * quantity
        ).mask(self._day_is_pre_close(close_date), 0.0)

    def _value_end_target_calculate(self, dataframe: DataFrame, close_date: Timestamp):
        dataframe[PositionDayValuationFields.VALUE_END_TARGET] = dataframe[
            PositionDayValuationFields.VALUE_TARGET
        ].mask(
            self._day_is_close(close_date),
            dataframe[PositionDayValuationFields.CLOSE_PRICE_TARGET],
        )

    def _value_start_target_calculate(
        self, dataframe: DataFrame, open_date: Timestamp, start_date: date
    ):
        dataframe[PositionDayValuationFields.VALUE_START_TARGET] = (
            dataframe[PositionDayValuationFields.VALUE_TARGET]
            .shift(1, fill_value=0.0)
            .mask(
                self._day_is_not_open_but_is_start(open_date, start_date),
                dataframe[PositionDayValuationFields.VALUE_TARGET],
            )
            .mask(
                self._day_is_open(open_date),
                dataframe[PositionDayValuationFields.OPEN_VALUE_TARGET],
            )
        )

    def _return_per_period_calculate(
        self, dataframe: DataFrame, open_date: Timestamp, close_date: Timestamp
    ):
        dataframe[PositionDayValuationFields.RETURN_PER_PERIOD] = (
            dataframe[PositionDayValuationFields.VALUE_END_TARGET]
            - dataframe[PositionDayValuationFields.VALUE_START_TARGET]
        ).where(self._day_is_within_open_or_is_close(open_date, close_date), 0.0)

    def _return_per_period_percentage_calculate(self, dataframe: DataFrame):
        dataframe[PositionDayValuationFields.RETURN_PER_PERIOD_PERCENTAGE] = (
            dataframe[PositionDayValuationFields.RETURN_PER_PERIOD]
            / dataframe[PositionDayValuationFields.VALUE_START_TARGET]
        ).fillna(0.0)
