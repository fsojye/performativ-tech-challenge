from decimal import Decimal

from pydantic import BaseModel


class PositionDTO(BaseModel):
    id: int
    open_date: str
    close_date: str | None
    open_price: Decimal
    close_price: Decimal | None
    quantity: Decimal
    instrument_id: int
    instrument_currency: str


class PositionsData(BaseModel):
    positions: list[PositionDTO]
