import json
from datetime import date

from models.positions_data import PositionsData
from repositories.enviroment_loader import config
from repositories.performativ_api_repo import PerformativApiRepo
from repositories.positions_data_repo import PositionsDataRepo
from services.financial_metrics_calculator import FinancialMetricsCalculator


class MainController:
    def __init__(
        self,
        path_to_positions_file: str,
        target_currency: str,
        start_date_str: str,
        end_date_str: str,
        positions_data_repo: PositionsDataRepo | None = None,
        financial_metrics_calculator: FinancialMetricsCalculator | None = None,
        performativ_api_repo: PerformativApiRepo | None = None,
    ):
        self._positions_data_repo = positions_data_repo or PositionsDataRepo(path_to_positions_file)
        self.start_date = self._try_parse_datestr(start_date_str)
        self.end_date = self._try_parse_datestr(end_date_str)
        self.positions_data = self._get_positions_data()
        self.target_currency = target_currency

        self.financial_metrics_calculator = financial_metrics_calculator or FinancialMetricsCalculator(
            self.positions_data
        )
        self.performativ_api_repo = performativ_api_repo or PerformativApiRepo()

    def run(self) -> tuple[str, str]:
        try:
            return self._run()
        except Exception as e:
            raise MainControllerException(str(e)) from e

    def _try_parse_datestr(self, date_str: str) -> date:
        try:
            return date.fromisoformat(date_str)
        except Exception as e:
            raise MainControllerException("Supplied date is invalid isoformat") from e

    def _get_positions_data(self) -> PositionsData:
        try:
            return self._positions_data_repo.get()
        except Exception as e:
            raise MainControllerException(str(e)) from e

    def _run(self) -> tuple[str, str]:
        financial_metrics = self.financial_metrics_calculator.calculate(
            self.target_currency, self.start_date, self.end_date
        )
        post_submit_payload = financial_metrics.to_submit_api_payload(config.VALUE_PRECISION)

        submit_result = json.dumps(
            self.performativ_api_repo.post_submit_financial_metrics(post_submit_payload),
            indent=4,
        )
        return post_submit_payload.model_dump_json(indent=4), submit_result


class MainControllerException(Exception):
    pass
