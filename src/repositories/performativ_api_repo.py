from asyncio import gather, run
from dataclasses import asdict
from typing import Awaitable

from httpx import AsyncClient

from models.performativ_api import (
    BasePerformativApiParams,
    FxRatesData,
    GetFxRatesParams,
    GetInstrumentPricesParams,
    PostSubmitPayload,
    PricesData,
)
from repositories.enviroment_loader import config


class PerformativApiRepo:
    def __init__(self, session: AsyncClient | None = None):
        headers = {
            "x-api-key": config.PERFORMATIV_API_KEY,
            "candidate_id": config.PERFORMATIV_CANDIDATE_ID,
        }
        self.session = session or AsyncClient(headers=headers)
        self.url = config.PERFORMATIV_API_URL

    async def _get(self, endpoint: str, params: BasePerformativApiParams) -> dict[str, str]:
        try:
            response = await self.session.get(url=f"{self.url}/{endpoint}", params=asdict(params))
            response.raise_for_status()
            data: dict[str, str] = response.json()
            return data
        except Exception as ex:
            raise PerformativApiRepoException(f"Failed to get {endpoint} data") from ex

    async def get_fx_rates_by_dates(self, params: GetFxRatesParams) -> Awaitable[FxRatesData]:
        return FxRatesData(items=await self._get("fx-rates", params))  # type: ignore

    async def get_instruments_prices_by_dates(self, params: list[GetInstrumentPricesParams]) -> Awaitable[PricesData]:
        tasks = [self._get_instrument_prices_by_dates(param) for param in params]
        results = await gather(*tasks)

        prices_data = {}
        for result in results:
            prices_data.update(result.items)

        return PricesData(items=prices_data)

    async def _get_instrument_prices_by_dates(self, params: GetInstrumentPricesParams) -> Awaitable[PricesData]:
        return PricesData(items=await self._get("prices", params))  # type: ignore

    def post_submit_financial_metrics(self, payload: PostSubmitPayload) -> dict[str, str]:
        try:
            return run(self._post_submit_financial_metrics(payload))
        except Exception as ex:
            raise PerformativApiRepoException("Failed to post submit data") from ex

    async def _post_submit_financial_metrics(self, payload: PostSubmitPayload) -> Awaitable[dict[str, str]]:
        endpoint = "submit"
        response = await self.session.post(url=f"{self.url}/{endpoint}", json=payload.model_dump())
        response.raise_for_status()
        return response.json()  # type: ignore


class PerformativApiRepoException(Exception):
    pass
