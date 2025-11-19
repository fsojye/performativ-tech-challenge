import json
from unittest.mock import Mock

import pytest
from pandas import Series, date_range

from controllers.main_controller import MainController, MainControllerException
from entities.financial_metrics import BasketMetric, FinancialMetrics, PositionMetric


class TestMainController:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_positions_data_repo = Mock()
        self.mock_financial_metrics_calculator = Mock()
        self.mock_performativ_api_repo = Mock()
        self.mock_file = "/path/to/positions/file"

    def test_init_when_supplied_date_is_invalid_should_raise_expected_error_message(self):
        with pytest.raises(MainControllerException) as ex:
            MainController(
                self.mock_file,
                "USD",
                "Jan 01, 2020",
                "2020-01-01",
                self.mock_positions_data_repo,
                self.mock_financial_metrics_calculator,
                self.mock_performativ_api_repo,
            )

        assert "Supplied date is invalid isoformat" in str(ex)

    def test_init_when_get_positions_data_failed_should_raise_expected_error_message(self):
        self.mock_positions_data_repo.get.side_effect = Exception("Fake error message")

        with pytest.raises(MainControllerException) as ex:
            MainController(
                self.mock_file,
                "USD",
                "2020-01-01",
                "2020-01-01",
                self.mock_positions_data_repo,
                self.mock_financial_metrics_calculator,
                self.mock_performativ_api_repo,
            )

        assert "Failed to load positions data from file" in str(ex)

    def test_run_when_failed_should_raise_expected_error_message(self):
        controller = MainController(
            self.mock_file,
            "USD",
            "2020-01-01",
            "2020-01-01",
            self.mock_positions_data_repo,
            self.mock_financial_metrics_calculator,
            self.mock_performativ_api_repo,
        )
        self.mock_financial_metrics_calculator.calculate.side_effect = Exception("fake error message")

        with pytest.raises(MainControllerException) as ex:
            controller.run()

        assert "fake error message" in str(ex)

    def test_run_when_success_should_return_expected_value(self):
        mock_date_index = date_range("2020-01-01", "2020-01-10")
        controller = MainController(
            self.mock_file,
            "USD",
            mock_date_index[0].date().isoformat(),
            mock_date_index[-1].date().isoformat(),
            self.mock_positions_data_repo,
            self.mock_financial_metrics_calculator,
            self.mock_performativ_api_repo,
        )
        expected_financial_metrics = FinancialMetrics(
            positions={
                1: PositionMetric(
                    is_open=Series(1).reindex(index=mock_date_index),
                    price=Series(2).reindex(index=mock_date_index),
                    value=Series(3).reindex(index=mock_date_index),
                    return_per_period=Series(4).reindex(index=mock_date_index),
                    return_per_period_percentage=Series(5).reindex(index=mock_date_index),
                    value_start=Series(6).reindex(index=mock_date_index),
                )
            },
            basket=BasketMetric(
                is_open=Series(7).reindex(index=mock_date_index),
                price=Series(8).reindex(index=mock_date_index),
                value=Series(9).reindex(index=mock_date_index),
                return_per_period=Series(10).reindex(index=mock_date_index),
                return_per_period_percentage=Series(11).reindex(index=mock_date_index),
            ),
            dates=mock_date_index,
        )
        expected_submit_api_result = {
            "message": "Submission evaluated.",
            "score": "99.708111%",
            "submission_id": "019a9303-457f-7b03-90a8-39249821f67a",
        }

        self.mock_financial_metrics_calculator.calculate.return_value = expected_financial_metrics
        self.mock_performativ_api_repo.post_submit_financial_metrics.return_value = expected_submit_api_result

        actual_financial_metric_result, actual_submit_result = controller.run()
        test = json.loads(actual_financial_metric_result)
        assert json.loads(actual_submit_result) == expected_submit_api_result
        assert test == json.loads(expected_financial_metrics.to_submit_api_payload(8).model_dump_json())
