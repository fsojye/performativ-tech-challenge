from dataclasses import dataclass

from pandas import DatetimeIndex, Series


@dataclass
class BaseMetric:
    is_open: Series[float]
    price: Series[float]
    value: Series[float]
    return_per_period: Series[float]
    return_per_period_percentage: Series[float]


@dataclass
class PositionMetric(BaseMetric):
    value_start: Series[float]


@dataclass
class BasketMetric(BaseMetric):
    pass


@dataclass
class FinancialMetrics:
    positions: dict[int, PositionMetric]
    basket: BasketMetric
    dates: DatetimeIndex
