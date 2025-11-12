from unittest.mock import patch

from main import main


class TestMain:
    @patch("main.FinancialMetricsController")
    def test_main_when_invoked_should_trigger_FinancialMetricsCalculator(
        self, mock_controller
    ):
        main()
        
        mock_controller.return_value.calculate_metrics.assert_called_once()
