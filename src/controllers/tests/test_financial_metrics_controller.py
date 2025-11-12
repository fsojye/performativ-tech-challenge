from controllers.financial_metrics_controller import FinancialMetricsController


class TestFinancialMetricsController:
    def test_calculate_metrics_when_invoked_must_return_expected_message(self):
        controller = FinancialMetricsController()

        actual = controller.calculate_metrics("bleh")

        assert actual == "Hello World"
