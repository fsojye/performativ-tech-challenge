from dataclasses import dataclass

from numpy import trunc

from entities.metrics import BaseMetric, FinancialMetrics


@dataclass
class BasePerformativApiParams:
    start_date: str
    end_date: str


@dataclass
class GetFxRatesParams(BasePerformativApiParams):
    pairs: str


@dataclass
class GetInstrumentPricesParams(BasePerformativApiParams):
    instrument_id: str


@dataclass
class PostSubmitPayload:
    positions: dict[int, PositionPayload]
    basket: BasketPayload
    dates: list[str]

    @classmethod
    def from_metric(cls, metrics: FinancialMetrics) -> PostSubmitPayload:
        return cls(
            positions={
                position_id: BasePayload.from_metric(position_metric)  # type: ignore
                for position_id, position_metric in metrics.positions.items()
            },
            basket=BasketPayload.from_metric(metrics.basket),  # type: ignore
            dates=metrics.dates.strftime("%Y-%m-%d").tolist(),
        )


@dataclass
class BasePayload:
    IsOpen: list[float]
    Price: list[float]
    Value: list[float]
    ReturnPerPeriod: list[float]
    ReturnPerPeriodPercentage: list[float]

    @classmethod
    def from_metric(cls, metric: BaseMetric) -> BasePayload:
        precision = 8
        truncate = lambda value: (trunc(value * 10**precision) / 10**precision)
        return cls(
            IsOpen=metric.is_open.tolist(),
            Price=truncate(metric.price).tolist(),
            Value=truncate(metric.value).tolist(),
            ReturnPerPeriod=truncate(metric.return_per_period).tolist(),
            ReturnPerPeriodPercentage=truncate(
                metric.return_per_period_percentage
            ).tolist(),
        )


@dataclass
class PositionPayload(BasePayload):
    pass


@dataclass
class BasketPayload(BasePayload):
    pass
