from datetime import date
from typing import Iterator

from pandas import (
    DataFrame,
    DatetimeIndex,
    date_range,
    to_datetime,
)

from entities.metrics import FinancialMetrics, PositionMetric
from models.performativ_resource import PerformativResource
from models.positions_data import PositionsData
from services.basket_calculator import BasketCalculator
from services.performativ_resource_loader import PerformativResourceLoader
from services.position_calculator import PositionCalculator


class FinancialMetricsCalculator:
    def __init__(
        self,
        positions_data: list[dict[str, str]],
        performativ_resource_loader: PerformativResourceLoader | None = None,
        position_calculator: PositionCalculator | None = None,
        basket_calculator: BasketCalculator | None = None,
    ):
        self._positions_data = PositionsData.model_validate(
            {"positions": positions_data}
        )
        self._performativ_resource_loader = (
            performativ_resource_loader
            or PerformativResourceLoader(self._positions_data)
        )
        self._position_calculator = position_calculator or PositionCalculator()
        self._basket_calculator = basket_calculator or BasketCalculator()

    def calculate(
        self,
        target_currency: str,
        start_date: date,
        end_date: date,
    ) -> FinancialMetrics:
        # set_option("display.max_rows", None)  # Show all rows
        # set_option("display.max_columns", None)  # Show all columns
        # set_option("display.width", None)  # Use the maximum display width
        # set_option("display.max_colwidth", None)
        positions = {}
        date_index = date_range(start_date, end_date)

        for position_id, position_metric in self._calculate_position_metrics(
            target_currency, date_index
        ):
            positions[position_id] = position_metric
            self._basket_calculator.add_to_basket(position_metric)

        return FinancialMetrics(
            positions=positions,
            basket=self._basket_calculator.calculate(),
            dates=date_index,
        )

    def _calculate_position_metrics(
        self, target_currency: str, date_index: DatetimeIndex
    ) -> Iterator[tuple[int, PositionMetric]]:
        start_date = date_index[0].date()
        end_date = date_index[-1].date()

        resource_data = self._load_resource_data(target_currency, start_date, end_date)
        for pos in self._positions_data.positions:
            fx_pair = f"{pos.instrument_currency}{target_currency}"
            fx_df = self._get_fx_pair_dataframe(
                date_index, fx_pair, resource_data.fx_rates
            )
            prices_df = self._get_instrument_prices_dataframe(
                date_index, str(pos.instrument_id), resource_data.prices
            )

            yield (
                pos.id,
                self._position_calculator.calculate(pos, date_index, fx_df, prices_df),
            )

    def _load_resource_data(
        self, target_currency: str, start_date: date, end_date: date
    ) -> PerformativResource:
        return self._performativ_resource_loader.load_resources(
            target_currency, start_date, end_date
        )

    def _get_fx_pair_dataframe(
        self,
        date_series: DatetimeIndex,
        fx_pair: str,
        fx_rates_data: dict[str, dict[str, str]],
    ) -> DataFrame:
        fx_df = DataFrame(fx_rates_data.get(fx_pair, []), index=date_series)
        fx_df = fx_df.assign(
            date=to_datetime(fx_df["date"] if "date" in fx_df.columns else date_series),
            rate=fx_df["rate"] if "rate" in fx_df.columns else 1.0,
        )
        fx_df = fx_df.set_index("date").reindex(
            to_datetime(date_series), fill_value=1.0
        )
        return fx_df

    def _get_instrument_prices_dataframe(
        self,
        date_series: DatetimeIndex,
        instrument_id: str,
        prices_data: dict[str, dict[str, str]],
    ) -> DataFrame:
        prices_df = DataFrame(prices_data[instrument_id], index=date_series)
        prices_df.set_index("date").reindex(to_datetime(date_series))
        return prices_df
