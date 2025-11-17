from dataclasses import asdict

from requests import Session

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
    def __init__(self, session: Session | None = None):
        self.session = session or Session()
        self.url = config.PERFORMATIV_API_URL
        self.session.headers.update(
            {
                "x-api-key": config.PERFORMATIV_API_KEY,
                "candidate_id": config.PERFORMATIV_CANDIDATE_ID,
            }
        )

    def _get(self, endpoint: str, params: BasePerformativApiParams) -> dict[str, str]:
        try:
            response = self.session.get(url=f"{self.url}/{endpoint}", params=asdict(params))
            response.raise_for_status()
            data: dict[str, str] = response.json()
            return data
        except Exception as ex:
            raise PerformativApiRepoException(f"Failed to get {endpoint} data") from ex

    def get_fx_rates_by_dates(self, params: GetFxRatesParams) -> FxRatesData:
        return FxRatesData(items=self._get("fx-rates", params))  # type: ignore

    def get_instruments_prices_by_dates(self, params: list[GetInstrumentPricesParams]) -> PricesData:
        response = {}
        for param in params:
            response.update(self._get_instrument_prices_by_dates(param).items)
        return PricesData(items=response)

    def _get_instrument_prices_by_dates(self, params: GetInstrumentPricesParams) -> PricesData:
        return PricesData(items=self._get("prices", params))  # type: ignore

    def post_submit_financial_metrics(self, payload: PostSubmitPayload) -> dict[str, str]:
        try:
            endpoint = "submit"
            response = self.session.post(url=f"{self.url}/{endpoint}", json=payload.model_dump())
            response.raise_for_status()
            return response.json()  # type: ignore
        except Exception as ex:
            raise PerformativApiRepoException("Failed to post submit data") from ex


class PerformativApiRepoException(Exception):
    pass
