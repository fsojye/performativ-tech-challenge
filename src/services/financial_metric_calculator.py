from datetime import date
from typing import Generator

from numpy import nan
from pandas import (
    DataFrame,
    DatetimeIndex,
    date_range,
    to_datetime,
)

from services.performativ_resource_loader import PerformativResourceLoader
from models.performativ_resource import PerformativResource
from models.positions_data import PositionDTO, PositionsData
from entities.position import PositionDayValuationFields
from services.position_metric_calculator import PositionMetricCalculator


class FinancialMetricsCalculator:
    def __init__(
        self,
        positions_data: list[dict[str, str]],
        performativ_resource_loader: PerformativResourceLoader = None,
        position_metric_calculator: PositionMetricCalculator = None,
    ):
        self._positions_data = PositionsData(**{"positions": positions_data})
        self._performativ_resource_loader = (
            performativ_resource_loader
            or PerformativResourceLoader(self._positions_data)
        )
        self._position_metric_calculator = (
            position_metric_calculator or PositionMetricCalculator()
        )

    def calculate_metrics(
        self,
        target_currency: str,
        start_date: date,
        end_date: date,
    ) -> str:
        # set_option("display.max_rows", None)  # Show all rows
        # set_option("display.max_columns", None)  # Show all columns
        # set_option("display.width", None)  # Use the maximum display width
        # set_option("display.max_colwidth", None)
        result = {}
        result["position"] = {}
        for position_metric in self._calculate_position_metrics(
            target_currency, start_date, end_date
        ):
            result["position"].update(position_metric)
        return result

    def _calculate_position_metrics(
        self, target_currency: str, start_date: date, end_date: date
    ) -> Generator:
        resource_data = self._load_resource_data(target_currency, start_date, end_date)
        date_series = date_range(start_date, end_date)
        for pos in self._positions_data.positions:
            fx_pair = f"{pos.instrument_currency}{target_currency}"
            fx_df = self._get_fx_pair_dataframe(
                date_series, fx_pair, resource_data.fx_rates
            )
            prices_df = self._get_instrument_prices_dataframe(
                date_series, str(pos.instrument_id), resource_data.prices
            )

            self._position_metric_calculator.fx_rates = fx_df
            self._position_metric_calculator.prices = prices_df
            pos_metrics = self._position_metric_calculator.calculate_metrics(
                pos, start_date, end_date
            )
            pos_metrics.to_csv("output.csv", mode="a")
            yield {
                pos.id: {
                    "IsOpen": pos_metrics[PositionDayValuationFields.IS_OPEN].tolist(),
                    "Price": pos_metrics[
                        PositionDayValuationFields.PRICE_LOCAL
                    ].tolist(),
                    "Value": pos_metrics[
                        PositionDayValuationFields.VALUE_TARGET
                    ].tolist(),
                    "ReturnPerPeriod": pos_metrics[
                        PositionDayValuationFields.RETURN_PER_PERIOD
                    ].tolist(),
                    "ReturnPerPeriodPercentage.": pos_metrics[
                        PositionDayValuationFields.RETURN_PER_PERIOD_PERCENTAGE
                    ].tolist(),
                }
            }

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
    ):
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
    ):
        prices_df = DataFrame(prices_data[instrument_id], index=date_series)
        prices_df.set_index("date").reindex(to_datetime(date_series))
        return prices_df
