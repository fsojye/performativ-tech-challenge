from dataclasses import asdict
from requests import Session

from repositories.enviroment_loader import config
from models.performativ_api_params import (
    BasePerformativApiParams,
    GetFxRatesParams,
    GetInstrumentPricesParams,
)


class PerformativApiRepo:
    def __init__(self, session: Session = Session()):
        self.session = session
        self.url = config.PERFORMATIV_API_URL
        self.headers = {
            "x-api-key": config.PERFORMATIV_API_KEY,
            "candidate_id": config.PERFORMATIV_CANDIDATE_ID,
        }

    def _get(self, endpoint: str, params: BasePerformativApiParams) -> dict[str, str]:
        response = self.session.get(
            url=f"{self.url}/{endpoint}", headers=self.headers, params=asdict(params)
        )
        response.raise_for_status()
        return response.json()

    def get_fx_rates_by_dates(self, params: GetFxRatesParams) -> dict[str, str]:
        return self._get("fx-rates", params)

    def get_instrument_prices_by_dates(
        self, params: GetInstrumentPricesParams
    ) -> dict[str, str]:
        return self._get("prices", params)
