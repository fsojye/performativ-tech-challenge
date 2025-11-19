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


class PostSubmitPayload(BaseModel):
    positions: dict[str, PositionPayload]
    basket: BasketPayload | None
    dates: list[str]


class BasePayload(BaseModel):
    IsOpen: list[float]
    Price: list[float]
    Value: list[float]
    ReturnPerPeriod: list[float]
    ReturnPerPeriodPercentage: list[float]


class PositionPayload(BasePayload):
    pass


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
