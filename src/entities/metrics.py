from dataclasses import dataclass


@dataclass
class BaseMetric:
    IsOpen: list[float]
    Price: list[float]
    Value: list[float]
    ReturnPerPeriod: list[float]
    ReturnPerPeriodPercentage: list[float]


@dataclass
class PositionMetric:
    Id: int
    Metric: BaseMetric


@dataclass
class BasketMetric(BaseMetric):
    pass
