from datetime import date
from typing import Optional

from services.financial_metric_calculator import FinancialMetricsCalculator
from services.positions_file_loader import PositionsFileLoader


class MainController:
    def __init__(
        self,
        path_to_positions_file: str,
        target_currency: str,
        start_date_str: str,
        end_date_str: str,
        positions_file_loader: Optional[PositionsFileLoader] = None,
        financial_metrics_calculator: Optional[FinancialMetricsCalculator] = None,
    ):
        self.positions_file_loader = positions_file_loader or PositionsFileLoader()
        self._load_properties(
            path_to_positions_file, target_currency, start_date_str, end_date_str
        )
        self.financial_metrics_calculator = (
            financial_metrics_calculator
            or FinancialMetricsCalculator(self.positions_data)
        )

    def run(self) -> str:
        try:
            return self._run()
        except Exception as e:
            raise MainControllerException(str(e)) from e

    def _load_properties(
        self,
        path_to_positions_file: str,
        target_currency: str,
        start_date_str: str,
        end_date_str: str,
    ) -> None:
        try:
            self.start_date = self._try_parse_datestr(start_date_str)
            self.end_date = self._try_parse_datestr(end_date_str)
            self.target_currency = target_currency
            self.positions_data = self.positions_file_loader.load(
                path_to_positions_file
            )
        except Exception as e:
            raise MainControllerException(str(e)) from e

    def _try_parse_datestr(self, date_str: str) -> date:
        try:
            return date.fromisoformat(date_str)
        except Exception as e:
            raise MainControllerException("Supplied date is invalid isoformat") from e

    def _run(self) -> str:
        return self.financial_metrics_calculator.calculate_metrics(
            self.target_currency, self.start_date, self.end_date
        )


class MainControllerException(Exception):
    pass
