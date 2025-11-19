from datetime import date
from typing import Iterator

from pandas import (
    DataFrame,
    DatetimeIndex,
    date_range,
    to_datetime,
)

from entities.financial_metrics import FinancialMetrics, PositionMetric
from models.performativ_api import FxRatesData, PricesData
from models.performativ_resource import PerformativResource
from models.positions_data import PositionsData
from services.basket_calculator import BasketCalculator
from services.performativ_resource_loader import PerformativResourceLoader
from services.position_calculator import PositionCalculator


class FinancialMetricsCalculator:
    def __init__(
        self,
        positions_data: PositionsData,
        performativ_resource_loader: PerformativResourceLoader | None = None,
        position_calculator: PositionCalculator | None = None,
        basket_calculator: BasketCalculator | None = None,
    ):
        self._positions_data = positions_data
        self._performativ_resource_loader = performativ_resource_loader or PerformativResourceLoader(
            self._positions_data
        )
        self._position_calculator = position_calculator or PositionCalculator()
        self._basket_calculator = basket_calculator or BasketCalculator()

    def calculate(self, target_currency: str, start_date: date, end_date: date) -> FinancialMetrics:
        try:
            positions = {}
            date_index = date_range(start_date, end_date)

            for position_id, position_metric in self._calculate_position_metrics(target_currency, date_index):
                positions[position_id] = position_metric
                self._basket_calculator.add_to_basket(position_metric)

            return FinancialMetrics(
                positions=positions,
                basket=self._basket_calculator.calculate(),
                dates=date_index,
            )
        except Exception as e:
            raise FinancialMetricsCalculatorException(str(e)) from e

    def _calculate_position_metrics(
        self, target_currency: str, date_index: DatetimeIndex
    ) -> Iterator[tuple[int, PositionMetric]]:
        start_date = date_index[0].date()
        end_date = date_index[-1].date()

        resource_data = self._load_resource_data(target_currency, start_date, end_date)
        for pos in self._positions_data.positions:
            fx_df = self._get_fx_pair_dataframe(date_index, pos.instrument_currency, target_currency, resource_data.fx_rates)
            prices_df = self._get_instrument_prices_dataframe(date_index, str(pos.instrument_id), resource_data.prices)

            self._position_calculator.load_calculation_requirements(pos, fx_df, prices_df)
            yield (
                pos.id,
                self._position_calculator.calculate(date_index),
            )

    def _load_resource_data(self, target_currency: str, start_date: date, end_date: date) -> PerformativResource:
        return self._performativ_resource_loader.load_resources(target_currency, start_date, end_date)

    def _get_fx_pair_dataframe(self, date_series: DatetimeIndex, local_currency: str, target_currency: str, fx_rates_data: FxRatesData) -> DataFrame:
        if local_currency == target_currency:
            fx_df = DataFrame(fx_rates_data, index=date_series)
            return fx_df.assign(
                date=date_series,
                rate=1
            )
        fx_pair =f"{local_currency}{target_currency}"
        fx_rates = fx_rates_data.model_dump()["items"].get(fx_pair)
        if fx_rates is None:
            raise FinancialMetricsCalculatorException(f"Fx rates data is not available for {fx_pair}")
        
        return DataFrame(fx_rates, index=date_series)

    def _get_instrument_prices_dataframe(
        self, date_series: DatetimeIndex, instrument_id: str, prices_data: PricesData
    ) -> DataFrame:
        prices = prices_data.model_dump()["items"].get(instrument_id)

        if prices is None:
            raise FinancialMetricsCalculatorException(f"Prices data is not available for {instrument_id}")
        
        return DataFrame(prices, index=date_series)


class FinancialMetricsCalculatorException(Exception):
    pass
