from datetime import date
from unittest.mock import Mock

import pytest

from models.performativ_api_params import GetFxRatesParams
from models.performativ_resource import PerformativResource
from models.positions_data import PositionDTO, PositionsData
from services.performativ_resource_loader import PerformativResourceLoader


class TestPerformativResourceLoader:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_performativ_api_repo = Mock()
        self.test_positions_data = PositionsData(
            positions=[
                PositionDTO(
                    id=1,
                    open_date="2023-01-01",
                    close_date=None,
                    instrument_id=1000,
                    instrument_currency="EUR",
                    open_price=90.0,
                    close_price=None,
                    quantity=10.0,
                ),
                PositionDTO(
                    id=2,
                    open_date="2023-02-01",
                    close_date="2023-03-01",
                    instrument_id=1001,
                    instrument_currency="USD",
                    open_price=100.0,
                    close_price=110.0,
                    quantity=5.0,
                ),
                PositionDTO(
                    id=3,
                    open_date="2023-03-15",
                    close_date=None,
                    instrument_id=1002,
                    instrument_currency="GBP",
                    open_price=80.0,
                    close_price=None,
                    quantity=8.0,
                ),
                PositionDTO(
                    id=4,
                    open_date="2023-04-01",
                    close_date=None,
                    instrument_id=1001,
                    instrument_currency="USD",
                    open_price=105.0,
                    close_price=None,
                    quantity=12.0,
                ),
            ]
        )
        self.service = PerformativResourceLoader(
            positions_data=self.test_positions_data,
            performativ_api_repo=self.mock_performativ_api_repo,
        )

    def test_load_resources_should_return_expected_performativ_resource(
        self,
    ):
        mock_response = {"test": "data"}
        self.mock_performativ_api_repo.get_fx_rates_by_dates.return_value = mock_response
        self.mock_performativ_api_repo.get_instrument_prices_by_dates.return_value = mock_response
        instrument_ids = set(map(lambda pos: pos.instrument_id, self.test_positions_data.positions))

        actual = self.service.load_resources(
            target_currency="USD",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
        )

        assert actual == PerformativResource(
            fx_rates=mock_response,
            prices=mock_response,
        )
        self.mock_performativ_api_repo.get_fx_rates_by_dates.assert_called_once_with(
            params=GetFxRatesParams(start_date="20230101", end_date="20231231", pairs="EURUSD,GBPUSD")
        )
        assert self.mock_performativ_api_repo.get_instrument_prices_by_dates.call_count == len(instrument_ids)
