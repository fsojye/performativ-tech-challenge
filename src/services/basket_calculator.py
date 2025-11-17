from decimal import Decimal

from pandas import Series, concat
from pandas.core.groupby import DataFrameGroupBy

from entities.financial_metrics import BasketMetric, PositionMetric
from models.decimals import ONE, ZERO


class BasketCalculator:
    def __init__(self) -> None:
        self.is_open_series: list[Series[Decimal]] = []
        self.value_series: list[Series[Decimal]] = []
        self.value_start_series: list[Series[Decimal]] = []
        self.return_per_period_series: list[Series[Decimal]] = []

    def add_to_basket(self, position_metric: PositionMetric) -> None:
        self.is_open_series.append(position_metric.is_open)
        self.value_series.append(position_metric.value)
        self.value_start_series.append(position_metric.value_start)
        self.return_per_period_series.append(position_metric.return_per_period)

    def calculate(self) -> BasketMetric:
        is_open_aggregate = concat(self.is_open_series).groupby(level=0)
        value_aggregate = concat(self.value_series).groupby(level=0)
        value_start_aggregate = concat(self.value_start_series).groupby(level=0)
        return_per_period_aggregate = concat(self.return_per_period_series).groupby(level=0)
        return BasketMetric(
            is_open=self._is_open_calculate(is_open_aggregate),
            price=self._price_local_calculate(is_open_aggregate),
            value=self._value_calculate(value_aggregate),
            return_per_period=self._return_per_period_calculate(return_per_period_aggregate),
            return_per_period_percentage=self._return_per_period_percentage_calculate(
                return_per_period_aggregate, value_start_aggregate
            ),
        )

    def _is_open_calculate(self, basket_aggregate: DataFrameGroupBy) -> Series[Decimal]:
        return basket_aggregate.max()

    def _price_local_calculate(self, basket_aggregate: DataFrameGroupBy) -> Series[Decimal]:
        return basket_aggregate.all() * ZERO

    def _value_calculate(self, basket_aggregate: DataFrameGroupBy) -> Series[Decimal]:
        return basket_aggregate.sum()

    def _return_per_period_calculate(self, basket_aggregate: DataFrameGroupBy) -> Series[Decimal]:
        return basket_aggregate.sum()

    def _return_per_period_percentage_calculate(
        self,
        basket_aggregate: DataFrameGroupBy,
        value_start_aggregate: DataFrameGroupBy,
    ) -> Series[Decimal]:
        value_start_aggregate_sum = value_start_aggregate.sum()
        return_per_period_aggregate_sum = basket_aggregate.sum()

        rpp_percentage_mean = return_per_period_aggregate_sum.where(
            value_start_aggregate_sum != ZERO, ZERO
        ) / value_start_aggregate_sum.replace(ZERO, ONE)
        return rpp_percentage_mean.mask(value_start_aggregate_sum == ZERO, ZERO)
