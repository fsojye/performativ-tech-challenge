from datetime import date
from numpy import nan
from pandas import DataFrame, Timedelta, date_range, to_datetime
from entities.position import PositionDayValuationFields
from models.positions_data import PositionDTO


class PositionMetricCalculator:
    fx_rates: DataFrame
    prices: DataFrame

    def calculate_metrics(
        self,
        position: PositionDTO,
        start_date: date,
        end_date: date,
    ):
        date_series = date_range(start_date, end_date)

        open_date = to_datetime(position.open_date)
        close_date = to_datetime(position.close_date)

        close_bound = close_date or (to_datetime(end_date) + Timedelta(days=1))
        after_open_mask = date_series >= open_date
        pre_close_mask = date_series < close_bound
        is_open_mask = after_open_mask & pre_close_mask
        is_close_day_mask = date_series == close_date
        is_open_day_mask = date_series == open_date
        pre_open_mask = date_series < open_date
        is_active_rpp_mask = is_open_mask | is_close_day_mask

        position_df = (
            DataFrame(index=date_series)
            .assign(
                **{
                    PositionDayValuationFields.PRICE_LOCAL: self.prices["price"].mask(
                        pre_open_mask, 0.0
                    )
                },
                **{
                    PositionDayValuationFields.OPEN_PRICE_TARGET: position.open_price
                    * self.fx_rates["rate"]
                },
                **{
                    PositionDayValuationFields.CLOSE_PRICE_TARGET: (
                        position.close_price
                        if position.close_price is not None
                        else nan
                    )
                    * self.fx_rates["rate"]
                },
                **{
                    PositionDayValuationFields.QUANTITY: is_open_mask.astype(float)
                    * position.quantity
                },
                **{PositionDayValuationFields.IS_OPEN: is_open_mask.astype(int)},
            )
            .assign(
                **{
                    PositionDayValuationFields.PRICE_TARGET: lambda df: df[
                        PositionDayValuationFields.PRICE_LOCAL
                    ]
                    * self.fx_rates["rate"]
                },
                **{
                    PositionDayValuationFields.VALUE_LOCAL: lambda df: df[
                        PositionDayValuationFields.PRICE_LOCAL
                    ]
                    * df[PositionDayValuationFields.QUANTITY]
                },
            )
            .assign(
                **{
                    PositionDayValuationFields.VALUE_TARGET: lambda df: df[
                        PositionDayValuationFields.VALUE_LOCAL
                    ]
                    * self.fx_rates["rate"]
                },
                **{
                    PositionDayValuationFields.OPEN_VALUE_TARGET: lambda df: (
                        df[PositionDayValuationFields.OPEN_PRICE_TARGET]
                        * position.quantity
                    ).mask(pre_open_mask, 0.0)
                },
                **{
                    PositionDayValuationFields.CLOSE_VALUE_TARGET: lambda df: (
                        df[PositionDayValuationFields.CLOSE_PRICE_TARGET]
                        * position.quantity
                    ).mask(pre_close_mask, 0.0)
                },
            )
            .assign(
                **{
                    PositionDayValuationFields.VALUE_END_TARGET: lambda df: df[
                        PositionDayValuationFields.VALUE_TARGET
                    ].mask(
                        is_close_day_mask,
                        df[PositionDayValuationFields.CLOSE_VALUE_TARGET],
                    )
                },
            )
            .assign(
                **{
                    PositionDayValuationFields.VALUE_START_TARGET: lambda df: df[
                        PositionDayValuationFields.VALUE_TARGET
                    ]
                    .shift(1, fill_value=0.0)
                    .mask(
                        (date_series != open_date) & (date_series == start_date),
                        df[PositionDayValuationFields.VALUE_TARGET],
                    )
                    .mask(
                        is_open_day_mask,
                        df[PositionDayValuationFields.OPEN_VALUE_TARGET],
                    )
                }
            )
            .assign(
                **{
                    PositionDayValuationFields.RETURN_PER_PERIOD: lambda df: (
                        df[PositionDayValuationFields.VALUE_END_TARGET]
                        - df[PositionDayValuationFields.VALUE_START_TARGET]
                    ).where(is_active_rpp_mask, 0.0)
                },
                **{
                    PositionDayValuationFields.RETURN_PER_PERIOD_PERCENTAGE: lambda df: (
                        df[PositionDayValuationFields.RETURN_PER_PERIOD]
                        / df[PositionDayValuationFields.VALUE_START_TARGET]
                    ).fillna(0.0)
                },
            )
        )

        return position_df
