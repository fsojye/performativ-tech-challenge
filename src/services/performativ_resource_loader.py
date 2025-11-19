from asyncio import gather, run
from datetime import date
from typing import Awaitable

from numpy.typing import NDArray
from pandas import DataFrame

from models.performativ_api import FxRatesData, GetFxRatesParams, GetInstrumentPricesParams, PricesData
from models.performativ_resource import PerformativResource
from models.positions_data import PositionsData
from repositories.performativ_api_repo import PerformativApiRepo


class PerformativResourceLoader:
    def __init__(
        self,
        positions_data: PositionsData,
        performativ_api_repo: PerformativApiRepo | None = None,
    ):
        self._positions_data = positions_data
        self._performativ_api_repo = performativ_api_repo or PerformativApiRepo()

    def load_resources(self, target_currency: str, start_date: date, end_date: date):
        return run(self._load_resources(target_currency, start_date, end_date))

    async def _load_resources(self, target_currency: str, start_date: date, end_date: date) -> PerformativResource:
        positions_df = DataFrame(self._positions_data.model_dump()["positions"])
        fx_pairs = self._get_unique_fx_pairs(positions_df, target_currency)
        instrument_ids = self._get_unique_instrument_ids(positions_df)

        start_date_param = start_date.strftime("%Y%m%d")
        end_date_param = end_date.strftime("%Y%m%d")
        fx_rates_task = self._get_fx_rates_by_dates(fx_pairs, start_date_param, end_date_param)
        prices_task = self._get_prices_by_dates(instrument_ids, start_date_param, end_date_param)

        fx_rates, prices = await gather(fx_rates_task, prices_task)

        return PerformativResource(fx_rates=fx_rates, prices=prices)

    def _get_unique_fx_pairs(self, positions_df: DataFrame, target_currency: str) -> NDArray:
        return (  # type: ignore
            positions_df[positions_df["instrument_currency"] != target_currency]["instrument_currency"]
            + target_currency
        ).unique()

    def _get_unique_instrument_ids(self, positions_df: DataFrame) -> NDArray:
        return positions_df["instrument_id"].unique()  # type: ignore

    async def _get_fx_rates_by_dates(self, fx_pairs: NDArray, start_date: str, end_date: str) -> Awaitable[FxRatesData]:
        return await self._performativ_api_repo.get_fx_rates_by_dates(
            params=GetFxRatesParams(pairs=",".join(fx_pairs), start_date=start_date, end_date=end_date)
        )

    async def _get_prices_by_dates(
        self, instrument_ids: NDArray, start_date: str, end_date: str
    ) -> Awaitable[PricesData]:
        return await self._performativ_api_repo.get_instruments_prices_by_dates(
            params=[
                GetInstrumentPricesParams(instrument_id=instrument_id, start_date=start_date, end_date=end_date)
                for instrument_id in instrument_ids
            ]
        )
