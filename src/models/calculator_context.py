from dataclasses import dataclass

from pandas import DataFrame, DatetimeIndex

from models.positions_data import PositionDTO


@dataclass
class CalculatorContext:
    position: PositionDTO
    date_index: DatetimeIndex
    fx_rates: DataFrame
    prices: DataFrame
