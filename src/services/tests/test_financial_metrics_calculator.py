from unittest.mock import Mock

import pytest
from pandas import DataFrame, date_range

from entities.financial_metrics import FinancialMetrics
from models.performativ_api import FxRateData, FxRatesData, PriceData, PricesData
from models.performativ_resource import PerformativResource
from models.positions_data import PositionDTO, PositionsData
from services.financial_metrics_calculator import FinancialMetricsCalculator, FinancialMetricsCalculatorException


class TestFinancialMetricsCalculator:
    @pytest.fixture(autouse=True)
    def setup(self):
        mock_positions_data = PositionsData(
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
            ]
        )
        self.mock_perfomativ_resource_loader = Mock()
        mock_position_calculator = Mock()
        mock_basket_calculator = Mock()
        self.calculator = FinancialMetricsCalculator(
            mock_positions_data, self.mock_perfomativ_resource_loader, mock_position_calculator, mock_basket_calculator
        )

    def test_calculate_when_error_must_raise_expected_exception_message(self):
        self.mock_perfomativ_resource_loader.load_resources.side_effect = Exception("Fake error message")

        with pytest.raises(FinancialMetricsCalculatorException) as ex:
            self.calculator.calculate("USD", "2000-01-01", "2001-01-01")

        assert "Fake error message" in str(ex)

    def test_calculate_when_successful_should_return_expected_object(self):
        self.mock_perfomativ_resource_loader.load_resources.return_value = PerformativResource(
            fx_rates=FxRatesData(items={"EURUSD": [FxRateData(date="2023-01-01", rate=1.1)]}),
            prices=PricesData(items={"1000": [PriceData(date="2023-01-01", price=1001)]}),
        )

        actual = self.calculator.calculate("USD", "2000-01-01", "2001-01-01")

        assert isinstance(actual, FinancialMetrics)

    def test_get_fx_pair_dataframe_when_fx_pair_not_in_resource_should_raise_expected_exception_message(self):
        test_fx_rates_data = FxRatesData(items={})

        with pytest.raises(FinancialMetricsCalculatorException) as ex:
            self.calculator._get_fx_pair_dataframe(
                date_range("2023-01-01", "2023-01-01"), "EUR", "USD", test_fx_rates_data
            )

        assert "Fx rates data is not available for EURUSD" in str(ex)

    def test_get_fx_pair_dataframe_when_same_local_target_should_return_value_one(self):
        test_fx_rates_data = FxRatesData(items={})
        test_date_index = date_range("2023-01-01", "2023-01-10")

        actual = self.calculator._get_fx_pair_dataframe(test_date_index, "EUR", "EUR", test_fx_rates_data)

        assert isinstance(actual, DataFrame)
        assert actual["rate"].to_list() == [1] * len(test_date_index)

    def test_get_instrument_prices_dataframe_when_fx_pair_not_in_resource_should_raise_expected_exception_message(self):
        test_fx_rates_data = FxRatesData(items={})

        with pytest.raises(FinancialMetricsCalculatorException) as ex:
            self.calculator._get_instrument_prices_dataframe(
                date_range("2023-01-01", "2023-01-01"), "1001", test_fx_rates_data
            )

        assert "Prices data is not available for 1001" in str(ex)
