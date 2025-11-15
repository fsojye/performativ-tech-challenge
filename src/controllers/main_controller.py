from dataclasses import asdict
import json
from datetime import date

from models.performativ_api_params import (
    PostSubmitPayload,
)
from repositories.performativ_api_repo import PerformativApiRepo
from services.financial_metrics_calculator import FinancialMetricsCalculator
from services.positions_file_loader import PositionsFileLoader


class MainController:
    def __init__(
        self,
        path_to_positions_file: str,
        target_currency: str,
        start_date_str: str,
        end_date_str: str,
        positions_file_loader: PositionsFileLoader | None = None,
        financial_metrics_calculator: FinancialMetricsCalculator | None = None,
        performativ_api_repo: PerformativApiRepo | None = None,
    ):
        self.positions_file_loader = positions_file_loader or PositionsFileLoader()
        self._init_properties(
            path_to_positions_file, target_currency, start_date_str, end_date_str
        )
        self.financial_metrics_calculator = (
            financial_metrics_calculator
            or FinancialMetricsCalculator(self.positions_data)
        )
        self.performativ_api_repo = performativ_api_repo or PerformativApiRepo()

    def run(self) -> str:
        try:
            return self._run()
        except Exception as e:
            raise MainControllerException(str(e)) from e

    def _init_properties(
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
        financial_metrics = self.financial_metrics_calculator.calculate(
            self.target_currency, self.start_date, self.end_date
        )
        post_submit_payload = PostSubmitPayload.from_metric(financial_metrics)

        result = json.dumps(
            self.performativ_api_repo.post_submit_financial_metrics(
                post_submit_payload
            ),
            indent=4,
        )

        print(json.dumps(asdict(post_submit_payload), indent=4))
        return result


class MainControllerException(Exception):
    pass
