from pydantic import BaseModel


class PositionDTO(BaseModel):
    id: int
    open_date: str
    close_date: str | None
    open_price: float
    close_price: float | None
    quantity: int
    instrument_id: int
    instrument_currency: str


class PositionsData(BaseModel):
    positions: list[PositionDTO]
