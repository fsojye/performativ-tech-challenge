import sys
from typing import Optional

from controllers.financial_metrics_controller import FinancialMetricsController
from services.positions_file_loader import PositionsFileLoader


class Main:
    def __init__(
        self,
        positions_file_loader: Optional[PositionsFileLoader] = None,
        financial_metrics_controller: Optional[FinancialMetricsController] = None,
    ):
        self.positions_file_loader = positions_file_loader or PositionsFileLoader()
        self.financial_metrics_controller = (
            financial_metrics_controller or FinancialMetricsController()
        )

    def run(self, path_to_positions_file: str) -> str:
        try:
            return self._run(path_to_positions_file)
        except Exception as e:
            raise MainException(str(e)) from e

    def _run(self, path_to_positions_file: str) -> str:
        positions_data = self.positions_file_loader.load(path_to_positions_file)
        return self.financial_metrics_controller.calculate_metrics(positions_data)


class MainException(Exception):
    pass


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(Main().run(sys.argv[1]))
        sys.exit()

    print("Invalid command supplied")
    sys.exit(1)
