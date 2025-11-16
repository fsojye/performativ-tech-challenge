from unittest.mock import Mock

import pytest
from requests import Response, Session

from models.performativ_api_params import (
    GetFxRatesParams,
    PostSubmitPayload,
)
from repositories.performativ_api_repo import (
    PerformativApiRepo,
    PerformativApiRepoException,
)


class TestPerformativApiRepo:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_session = Mock(spec=Session)
        self.mock_session.headers = {}
        self.repo = PerformativApiRepo(session=self.mock_session)
        self.test_params = GetFxRatesParams(pairs="EURUSD", start_date="20230101", end_date="20231231")

    def test_get_fx_rates_by_dates_when_request_failed_should_raise_expected_exception_message(
        self,
    ):
        self.mock_session.get.side_effect = Exception()

        with pytest.raises(PerformativApiRepoException) as ex:
            self.repo.get_fx_rates_by_dates(self.test_params)

        assert "Failed to get fx-rates data" in str(ex.value)

    def test_get_fx_rates_by_dates_when_request_succeeded_should_return_data(
        self,
    ):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {"test": "data"}
        self.mock_session.get.return_value = mock_response

        actual = self.repo.get_fx_rates_by_dates(self.test_params)

        assert actual == {"test": "data"}

    def test_get_instrument_prices_by_dates_when_request_failed_should_raise_expected_exception_message(
        self,
    ):
        self.mock_session.get.side_effect = Exception()

        with pytest.raises(PerformativApiRepoException) as ex:
            self.repo.get_instrument_prices_by_dates(self.test_params)

        assert "Failed to get prices data" in str(ex.value)

    def test_get_instrument_prices_by_dates_when_request_succeeded_should_return_data(
        self,
    ):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {"test": "data"}
        self.mock_session.get.return_value = mock_response

        actual = self.repo.get_fx_rates_by_dates(self.test_params)

        assert actual == {"test": "data"}

    def test_post_submit_financial_metrics_when_request_failed_should_raise_expected_exception_message(
        self,
    ):
        self.mock_session.post.side_effect = Exception()

        payload = PostSubmitPayload(
            positions={},
            basket=Mock(),
            dates=["2023-01-01", "2023-01-02"],
        )

        with pytest.raises(PerformativApiRepoException) as ex:
            self.repo.post_submit_financial_metrics(payload)

        assert "Failed to post submit data" in str(ex.value)

    def test_post_submit_financial_metrics_when_request_succeeded_should_return_data(
        self,
    ):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {"test": "data"}
        self.mock_session.post.return_value = mock_response

        payload = PostSubmitPayload(
            positions={},
            basket=Mock(),
            dates=["2023-01-01", "2023-01-02"],
        )

        actual = self.repo.post_submit_financial_metrics(payload)

        assert actual == {"test": "data"}
