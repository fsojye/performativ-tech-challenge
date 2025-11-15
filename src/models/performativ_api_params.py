from dataclasses import dataclass

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
        return cls(
            IsOpen=metric.is_open.round(precision).tolist(),
            Price=metric.price.round(precision).tolist(),
            Value=metric.value.round(precision).tolist(),
            ReturnPerPeriod=metric.return_per_period.round(precision).tolist(),
            ReturnPerPeriodPercentage=metric.return_per_period_percentage.round(
                precision
            ).tolist(),
        )


@dataclass
class PositionPayload(BasePayload):
    pass


@dataclass
class BasketPayload(BasePayload):
    pass
