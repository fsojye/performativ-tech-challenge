from controllers.financial_metrics_controller import FinancialMetricsController


def main() -> str:
    controller = FinancialMetricsController()
    controller.calculate_metrics()


if __name__ == "__main__":
    main()
