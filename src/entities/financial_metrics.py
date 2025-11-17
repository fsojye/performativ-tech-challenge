from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import cast

from pandas import DatetimeIndex, Series, isna

from models.performativ_api import (
    BasePayload,
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
                str(position_id): position_metric.to_submit_api_payload(precision)
                for position_id, position_metric in self.positions.items()
            },
            basket=self.basket.to_submit_api_payload(precision),
            dates=self.dates.strftime("%Y-%m-%d").tolist(),
        )


@dataclass
class BaseMetric:
    is_open: Series[float]
    price: Series[float]
    value: Series[float]
    return_per_period: Series[float]
    return_per_period_percentage: Series[float]

    def to_submit_api_payload(self, precision: int) -> BasePayload:
        return BasePayload(
            IsOpen=self._truncate_fields(precision, self.is_open).tolist(),
            Price=self._truncate_fields(precision, self.price).tolist(),
            Value=self._truncate_fields(precision, self.value).tolist(),
            ReturnPerPeriod=self._truncate_fields(precision, self.return_per_period).tolist(),
            ReturnPerPeriodPercentage=self._truncate_fields(precision, self.return_per_period_percentage).tolist(),
        )

    def _truncate_fields(self, precision: int, value: Series) -> Series:
        decimal_precision = Decimal("1e-{}".format(precision))

        def safe_quantize(x: Decimal) -> Decimal | None:
            if isna(x) or x is None:
                return None

            return x.quantize(decimal_precision, rounding=ROUND_HALF_UP)

        return value.apply(safe_quantize)


@dataclass
class PositionMetric(BaseMetric):
    value_start: Series[float]

    def to_submit_api_payload(self, precision: int) -> PositionPayload:
        return cast(PositionPayload, super().to_submit_api_payload(precision))


@dataclass
class BasketMetric(BaseMetric):
    def to_submit_api_payload(self, precision: int) -> BasketPayload:
        return cast(BasketPayload, super().to_submit_api_payload(precision))
