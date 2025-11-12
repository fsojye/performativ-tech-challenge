class FinancialMetricsController:
    def calculate_metrics(
        self, positions_data: list[dict[str, str]], target_currency: str = "USD"
    ) -> str:
        return "Hello World"


class FinancialMetricsControllerException(Exception):
    pass
