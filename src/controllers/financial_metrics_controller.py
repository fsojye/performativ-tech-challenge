class FinancialMetricsController:
    def calculate_metrics(
        self,
        positions_data: list[dict[str, str]],
        target_currency: str = "USD",
        start_date: str = "2023-01-01",
        end_date: str = "2024-11-10",
    ) -> str:
        return "Hello World"


class FinancialMetricsControllerException(Exception):
    pass
