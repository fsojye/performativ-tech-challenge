from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


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
    basket: BasketPayload | None
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


class BaseData(BaseModel):
    date: date


class FxRateData(BaseData):
    rate: Decimal


class PriceData(BaseData):
    price: Decimal


class FxRatesData(BaseModel):
    items: dict[str, list[FxRateData]]


class PricesData(BaseModel):
    items: dict[str, list[PriceData]]
