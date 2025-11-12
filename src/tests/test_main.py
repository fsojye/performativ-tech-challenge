from unittest.mock import Mock

import pytest

from main import Main, MainException


class TestMain:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self):
        self.mock_positions_file_loader = Mock()
        self.mock_financial_metrics_controller = Mock()
        self.mock_main = Main(
            self.mock_positions_file_loader, self.mock_financial_metrics_controller
        )

    def test_run_when_invoked_should_return_expected_value(self):
        expected_return_value = "Hello"
        self.mock_financial_metrics_controller.calculate_metrics.return_value = (
            expected_return_value
        )

        actual = self.mock_main.run("path/to/positions/file.json")

        self.mock_positions_file_loader.load.assert_called_once()
        assert actual == expected_return_value

    def test_run_when_error_encountered_should_raise_expected_exception(self):
        self.mock_positions_file_loader.load.side_effect = FileNotFoundError(
            "File not found"
        )

        with pytest.raises(MainException) as ex:
            self.mock_main.run("path/to/positions/file.json")

        assert "File not found" in str(ex)
        self.mock_financial_metrics_controller.calculate_metrics.assert_not_called()
