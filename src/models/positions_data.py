from typing import Optional

from pydantic import BaseModel


class PositionDTO(BaseModel):
    id: int
    open_date: str
    close_date: Optional[str]
    open_price: float
    close_price: Optional[float]
    quantity: int
    instrument_id: int
    instrument_currency: str


class PositionsData(BaseModel):
    positions: list[PositionDTO]
