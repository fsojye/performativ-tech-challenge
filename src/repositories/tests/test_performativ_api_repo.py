from unittest.mock import AsyncMock, Mock

import pytest
from httpx import AsyncClient

from models.performativ_api import (
    FxRatesData,
    GetFxRatesParams,
    GetInstrumentPricesParams,
    PostSubmitPayload,
    PricesData,
)
from repositories.performativ_api_repo import (
    PerformativApiRepo,
    PerformativApiRepoException,
)


class TestPerformativApiRepo:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.repo = PerformativApiRepo()
        self.test_get_fx_params = GetFxRatesParams(pairs="EURUSD", start_date="20230101", end_date="20231231")
        self.test_get_prices_params = [
            GetInstrumentPricesParams(instrument_id=1, start_date="20230101", end_date="20231231"),
            GetInstrumentPricesParams(instrument_id=2, start_date="20230101", end_date="20231231"),
        ]
        self.mock_response = Mock(spec=AsyncClient)

    @pytest.mark.asyncio
    async def test_get_fx_rates_by_dates_when_request_failed_should_raise_expected_exception_message(
        self,
    ):
        self.mock_response.raise_for_status = Mock()
        self.mock_response.json = Exception()
        self.repo.client.get = AsyncMock(return_value=self.mock_response)

        with pytest.raises(PerformativApiRepoException) as ex:
            await self.repo.get_fx_rates_by_dates(self.test_get_fx_params)

        assert "Failed to get fx-rates data" in str(ex.value)
        self.repo.client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_fx_rates_by_dates_when_request_succeeded_should_return_data(
        self,
    ):
        expected = FxRatesData(items={"SEKUSD": [{"date": "2023-01-01", "rate": 2}]})
        self.mock_response.json = Mock(return_value=expected.model_dump()["items"])
        self.mock_response.raise_for_status = Mock()
        self.repo.client.get = AsyncMock(return_value=self.mock_response)

        actual = await self.repo.get_fx_rates_by_dates(self.test_get_fx_params)

        assert actual.model_dump() == expected.model_dump()
        self.repo.client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_instrument_prices_by_dates_when_request_failed_should_raise_expected_exception_message(
        self,
    ):
        self.mock_response.raise_for_status = Mock()
        self.mock_response.json = Exception()
        self.repo.client.get = AsyncMock(return_value=self.mock_response)

        with pytest.raises(PerformativApiRepoException) as ex:
            await self.repo.get_instruments_prices_by_dates(self.test_get_prices_params)

        assert "Failed to get prices data" in str(ex.value)
        assert self.repo.client.get.call_count == len(self.test_get_prices_params)

    @pytest.mark.asyncio
    async def test_get_instrument_prices_by_dates_when_request_succeeded_should_return_data(
        self,
    ):
        expected = PricesData(items={"1": [{"date": "2023-01-01", "price": 2}]})
        self.mock_response.json = Mock(return_value=expected.model_dump()["items"])
        self.mock_response.raise_for_status = Mock()
        self.repo.client.get = AsyncMock(return_value=self.mock_response)

        actual = await self.repo.get_instruments_prices_by_dates(self.test_get_prices_params)

        assert actual.model_dump() == expected.model_dump()
        assert self.repo.client.get.call_count == len(self.test_get_prices_params)

    def test_post_submit_financial_metrics_when_request_failed_should_raise_expected_exception_message(
        self,
    ):
        self.mock_response.raise_for_status = Mock()
        self.mock_response.json = Exception()
        self.repo.client.post = AsyncMock(return_value=self.mock_response)

        payload = PostSubmitPayload(
            positions={},
            basket=None,
            dates=["2023-01-01", "2023-01-02"],
        )

        with pytest.raises(PerformativApiRepoException) as ex:
            self.repo.post_submit_financial_metrics(payload)

        assert "Failed to post submit data" in str(ex.value)
        self.repo.client.post.assert_called_once()

    def test_post_submit_financial_metrics_when_request_succeeded_should_return_data(
        self,
    ):
        self.mock_response.json = Mock(return_value={"test": "data"})
        self.mock_response.raise_for_status = Mock()
        self.repo.client.post = AsyncMock(return_value=self.mock_response)

        payload = PostSubmitPayload(
            positions={},
            basket=None,
            dates=["2023-01-01", "2023-01-02"],
        )

        actual = self.repo.post_submit_financial_metrics(payload)

        assert actual == {"test": "data"}
        self.repo.client.post.assert_called_once()
