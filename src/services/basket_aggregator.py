from pandas import DataFrame, concat

from pandas.core.groupby import DataFrameGroupBy

from entities.position import PositionDayValuationFields
from entities.metrics import BasketMetric


class BasketAggregator:
    def __init__(self):
        self.basket_dataframes = []

    def add_to_basket(self, position: DataFrame):
        self.basket_dataframes.append(position)

    def aggregate(self) -> BasketMetric:
        basket_aggregate = concat(self.basket_dataframes).groupby(level=0)
        return BasketMetric(
            IsOpen=self._is_open_aggregate(basket_aggregate),
            Price=self._price_local_aggreagate(basket_aggregate),
            Value=self._value_aggregate(basket_aggregate),
            ReturnPerPeriod=self._return_per_period_aggregate(basket_aggregate),
            ReturnPerPeriodPercentage=self._return_per_period_percentage_aggregate(
                basket_aggregate
            ),
        )

    def _is_open_aggregate(self, basket_aggregate: DataFrameGroupBy) -> list[float]:
        return basket_aggregate[PositionDayValuationFields.IS_OPEN].max().to_list()

    def _price_local_aggreagate(
        self, basket_aggregate: DataFrameGroupBy
    ) -> list[float]:
        return (
            basket_aggregate[PositionDayValuationFields.PRICE_LOCAL].all() * 0.0
        ).to_list()

    def _value_aggregate(self, basket_aggregate: DataFrameGroupBy) -> list[float]:
        return (
            basket_aggregate[PositionDayValuationFields.VALUE_TARGET]
            .sum()
            .round(8)
            .to_list()
        )

    def _return_per_period_aggregate(
        self, basket_aggregate: DataFrameGroupBy
    ) -> list[float]:
        return (
            basket_aggregate[PositionDayValuationFields.RETURN_PER_PERIOD]
            .sum()
            .round(8)
            .to_list(),
        )

    def _return_per_period_percentage_aggregate(
        self, basket_aggregate: DataFrameGroupBy
    ) -> list[float]:
        return (
            (
                basket_aggregate[
                    PositionDayValuationFields.RETURN_PER_PERIOD_PERCENTAGE
                ].sum()
                / basket_aggregate[PositionDayValuationFields.VALUE_START_TARGET].sum()
            )
            .round(8)
            .to_list()
        )
