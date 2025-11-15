from datetime import date
from typing import Optional

from numpy import ndarray
from pandas import DataFrame
from repositories.performativ_api_repo import PerformativApiRepo
from models.performativ_resource import PerformativResource
from models.positions_data import PositionsData
from models.performativ_api_params import GetFxRatesParams, GetInstrumentPricesParams


class PerformativResourceLoader:
    def __init__(
        self,
        positions_data: PositionsData,
        performativ_api_repo: Optional[PerformativApiRepo] = None,
    ):
        self._positions_data = positions_data
        self._performativ_api_repo = performativ_api_repo or PerformativApiRepo()

    def load_resources(
        self, target_currency: str, start_date: date, end_date: date
    ) -> PerformativResource:
        positions_df = DataFrame(self._positions_data.model_dump()["positions"])
        fx_pairs = self._get_unique_fx_pairs(positions_df, target_currency)
        instrument_ids = self._get_unique_instrument_ids(positions_df)

        start_date_param = start_date.strftime("%Y%m%d")
        end_date_param = end_date.strftime("%Y%m%d")
        return PerformativResource(
            fx_rates=self._get_fx_rates_by_dates(
                fx_pairs, start_date_param, end_date_param
            ),
            prices=self._get_prices_by_dates(
                instrument_ids, start_date_param, end_date_param
            ),
        )

    def _get_unique_fx_pairs(
        self, positions_df: DataFrame, target_currency: str
    ) -> ndarray:
        return (
            positions_df[positions_df["instrument_currency"] != target_currency][
                "instrument_currency"
            ]
            + target_currency
        ).unique()

    def _get_unique_instrument_ids(self, positions_df: DataFrame) -> ndarray:
        return positions_df["instrument_id"].unique()

    def _get_fx_rates_by_dates(
        self, fx_pairs: list[str], start_date: str, end_date: str
    ) -> dict:
        return self._performativ_api_repo.get_fx_rates_by_dates(
            params=GetFxRatesParams(
                pairs=",".join(fx_pairs), start_date=start_date, end_date=end_date
            )
        )

    def _get_prices_by_dates(
        self, instrument_ids: list[str], start_date: str, end_date: str
    ) -> dict:
        instrument_prices = {}
        for instrument_id in instrument_ids:
            instrument_prices.update(
                self._performativ_api_repo.get_instrument_prices_by_dates(
                    params=GetInstrumentPricesParams(
                        instrument_id=instrument_id,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )
            )
        return instrument_prices
