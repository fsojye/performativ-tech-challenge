from dataclasses import dataclass

from numpy import trunc
from pandas import DatetimeIndex, Series

from models.performativ_api import (
    BasketPayload,
    PositionPayload,
    PostSubmitPayload,
)


@dataclass
class FinancialMetrics:
    positions: dict[int, PositionMetric]
    basket: BasketMetric
    dates: DatetimeIndex

    def to_submit_api_payload(self, precision: int) -> PostSubmitPayload:
        return PostSubmitPayload(
            positions={
                str(position_id): position_metric.to_submit_api_position_payload(precision)
                for position_id, position_metric in self.positions.items()
            },
            basket=self.basket.to_submit_api_basket_payload(precision),
            dates=self.dates.strftime("%Y-%m-%d").tolist(),
        )


@dataclass
class BaseMetric:
    is_open: Series[float]
    price: Series[float]
    value: Series[float]
    return_per_period: Series[float]
    return_per_period_percentage: Series[float]

    def _to_submit_api_payload_dict(self, precision: int) -> dict:
        return {
            "IsOpen": self._truncate_fields(precision, self.is_open).tolist(),
            "Price": self._truncate_fields(precision, self.price).tolist(),
            "Value": self._truncate_fields(precision, self.value).tolist(),
            "ReturnPerPeriod": self._truncate_fields(precision, self.return_per_period).tolist(),
            "ReturnPerPeriodPercentage": self._truncate_fields(precision, self.return_per_period_percentage).tolist(),
        }

    def _truncate_fields(self, precision: int, value: Series[float]) -> Series[float]:
        return trunc(value.astype(float) * 10**precision) / 10**precision


@dataclass
class PositionMetric(BaseMetric):
    value_start: Series[float]

    def to_submit_api_position_payload(self, precision: int) -> PositionPayload:
        return PositionPayload(**self._to_submit_api_payload_dict(precision))


@dataclass
class BasketMetric(BaseMetric):
    def to_submit_api_basket_payload(self, precision: int) -> BasketPayload:
        return BasketPayload(**self._to_submit_api_payload_dict(precision))
