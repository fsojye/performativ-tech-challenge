from dataclasses import dataclass


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
    positions: dict[str, PositionPayload]
    basket: BasketPayload
    dates: list[str]


@dataclass
class BasePayload:
    IsOpen: list[float]
    Price: list[float]
    Value: list[float]
    ReturnPerPeriod: list[float]
    ReturnPerPeriodPercentage: list[float]


@dataclass
class PositionPayload(BasePayload):
    pass


@dataclass
class BasketPayload(BasePayload):
    pass
