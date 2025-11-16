from dataclasses import asdict

from requests import Session

from models.performativ_api_params import (
    BasePerformativApiParams,
    GetFxRatesParams,
    GetInstrumentPricesParams,
    PostSubmitPayload,
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

    def get_fx_rates_by_dates(self, params: GetFxRatesParams) -> dict[str, str]:
        return self._get("fx-rates", params)

    def get_instrument_prices_by_dates(self, params: GetInstrumentPricesParams) -> dict[str, str]:
        return self._get("prices", params)

    def post_submit_financial_metrics(self, payload: PostSubmitPayload) -> dict[str, str]:
        try:
            endpoint = "submit"
            response = self.session.post(url=f"{self.url}/{endpoint}", json=asdict(payload))
            response.raise_for_status()
            return response.json()  # type: ignore
        except Exception as ex:
            raise PerformativApiRepoException("Failed to post submit data") from ex


class PerformativApiRepoException(Exception):
    pass
