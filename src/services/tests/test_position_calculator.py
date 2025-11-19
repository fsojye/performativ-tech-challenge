from decimal import Decimal

import pytest
from numpy import nan
from pandas import DataFrame, DatetimeIndex, Series, date_range, isna, testing

from models.positions_data import PositionDTO
from services.position_calculator import PositionCalculator


class TestPositionCalculator:
    @pytest.fixture(autouse=True)
    def setup(self):
        test_start_date = "2023-01-01"
        test_end_date = "2023-01-10"
        test_date_index = date_range(test_start_date, test_end_date)
        self.test_fx_rates = DataFrame(
            {"rate": [Decimal(str(1.0 + (i * 0.01))) for i in range(len(test_date_index))]}, index=test_date_index
        )
        self.test_prices = DataFrame(
            {"price": [Decimal(str(float(100 + i))) for i in range(len(test_date_index))]}, index=test_date_index
        )
        self.test_position = PositionDTO(
            id=1,
            open_date="2023-01-02",
            close_date="2023-01-05",
            open_price=102.0,
            close_price=105.0,
            quantity=10,
            instrument_id=1,
            instrument_currency="USD",
        )
        self.calculator = PositionCalculator()

    def test_calculate_open_value_should_return_expected_series(self):
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator._calculate_open_value()

        assert float(actual) == 1030.2

    def test_calculate_close_value_should_return_expected_series(self):
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator._calculate_close_value()

        assert float(actual) == 1092

    def test_calculate_close_value_when_none_should_return_nan(self):
        self.test_position.close_price = None
        self.test_position.close_date = None
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator._calculate_close_value()

        assert isna(actual)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, 101.0, 102.0, 103.0, 104.0]),
            ("2022-12-31", "2023-01-04", [0.0, 0.0, 101.0, 102.0, 103.0]),
        ],
    )
    def test_calculate_price_local_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)
        expected_series = Series(expected, index=test_date_index)

        actual = self.calculator.calculate_price_local(test_date_index).apply(float)

        testing.assert_series_equal(actual, expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, 102.01, 104.04, 106.09, 108.16, 110.25, 112.36, 114.49, 116.64, 118.81]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, 102.01, 104.04, 106.09, 108.16]),
            ("2022-12-31", "2023-01-04", [nan, 0.0, 102.01, 104.04, 106.09]),
        ],
    )
    def test_calculate_price_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        price_local_series = self._to_decimal_series(
            [0.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0], test_date_index
        )
        expected_series = Series(expected, index=test_date_index)
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_price(test_date_index, price_local_series)

        testing.assert_series_equal(actual.astype(float), expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, 1.0, 1.0, 1.0, 0.0]),
            ("2022-12-31", "2023-01-05", [0.0, 0.0, 1.0, 1.0, 1.0, 0.0]),
        ],
    )
    def test_calculate_is_open_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        expected_series = Series(expected, index=test_date_index)
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_is_open(test_date_index)

        testing.assert_series_equal(actual.astype(float), expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, 10.0, 10.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, 10.0, 10.0, 10.0, 0.0]),
            ("2022-12-31", "2023-01-05", [nan, 0.0, 10.0, 10.0, 10.0, 0.0]),
        ],
    )
    def test_calculate_quantity_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        is_open_series = self._to_decimal_series([0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], test_date_index)
        expected_series = Series(expected, index=test_date_index)
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_quantity(test_date_index, is_open_series).apply(float)

        testing.assert_series_equal(actual, expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, 1010.0, 1020.0, 1030.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, 1010.0, 1020.0, 1030.0, 0.0]),
            ("2022-12-31", "2023-01-05", [nan, 0.0, 1010.0, 1020.0, 1030.0, 0.0]),
        ],
    )
    def test_calculate_value_local_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        price_local_series = Series(
            [0.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
            index=date_range("2023-01-01", "2023-01-10"),
        ).reindex(test_date_index)
        quantity_series = Series(
            [0.0, 10.0, 10.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], index=date_range("2023-01-01", "2023-01-10")
        ).reindex(test_date_index)
        expected_series = Series(expected, index=test_date_index)
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_value_local(test_date_index, price_local_series, quantity_series)

        testing.assert_series_equal(actual, expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, 1020.1, 1040.4, 1060.9, 0.0]),
            ("2022-12-31", "2023-01-05", [nan, 0.0, 1020.1, 1040.4, 1060.9, 0.0]),
        ],
    )
    def test_calculate_value_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        expected_series = Series(expected, index=test_date_index)
        value_local_series = self._to_decimal_series(
            [0.0, 1010.0, 1020.0, 1030.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], test_date_index
        )
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_value(test_date_index, value_local_series)

        testing.assert_series_equal(actual.astype(float), expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, 1030.2, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, 1030.2, 1020.1, 1040.4, 1060.9]),
            ("2022-12-31", "2023-01-05", [0.0, nan, 1030.2, 1020.1, 1040.4, 1060.9]),
        ],
    )
    def test_calculate_value_start_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        expected_series = Series(expected, index=test_date_index)
        value_series = self._to_decimal_series(
            [0.0, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], test_date_index
        )
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_value_start(test_date_index, value_series)

        testing.assert_series_equal(actual.astype(float), expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, 1020.1, 1040.4, 1060.9, 1092.0, nan, nan, nan, nan, nan]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, 1020.1, 1040.4, 1060.9, 1092.0]),
            ("2022-12-31", "2023-01-05", [nan, 0.0, 1020.1, 1040.4, 1060.9, 1092.0]),
        ],
    )
    def test_calculate_value_end_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        expected_series = Series(expected, index=test_date_index)
        value_series = self._to_decimal_series(
            [0.0, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], test_date_index
        )
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_value_end(test_date_index, value_series)

        testing.assert_series_equal(actual.astype(float), expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            ("2023-01-01", "2023-01-10", [0.0, -10.1, 20.3, 20.5, 31.1, 0.0, 0.0, 0.0, 0.0, 0.0]),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, -10.1, 20.3, 20.5, 31.1]),
            ("2022-12-31", "2023-01-05", [0.0, 0.0, -10.1, 20.3, 20.5, 31.1]),
        ],
    )
    def test_calculate_return_per_period_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        expected_series = Series(expected, index=test_date_index)
        value_end = self._to_decimal_series(
            [0.0, 1020.1, 1040.4, 1060.9, 1092.0, nan, nan, nan, nan, nan], test_date_index
        )
        value_start = self._to_decimal_series(
            [0.0, 1030.2, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0], test_date_index
        )
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_return_per_period(test_date_index, value_end, value_start)

        testing.assert_series_equal(actual.astype(float), expected_series, check_names=False)

    @pytest.mark.parametrize(
        "start_date, end_date, expected",
        [
            (
                "2023-01-01",
                "2023-01-10",
                [0.0, -0.009803921569, 0.019900009803, 0.019703960015, 0.029314732774, 0.0, 0.0, 0.0, 0.0, 0.0],
            ),
            ("2023-01-01", "2023-01-01", [0.0]),
            ("2023-01-01", "2023-01-05", [0.0, -0.009803921569, 0.019900009803, 0.019703960015, 0.029314732774]),
            ("2022-12-31", "2023-01-05", [nan, 0.0, -0.009803921569, 0.019900009803, 0.019703960015, 0.029314732774]),
        ],
    )
    def test_calculate_return_per_period_percentage_should_return_expected_series(self, start_date, end_date, expected):
        test_date_index = date_range(start_date, end_date)
        expected_series = Series(expected, index=test_date_index)
        return_per_period_series = self._to_decimal_series(
            [0.0, -10.1, 20.3, 20.5, 31.1, 0.0, 0.0, 0.0, 0.0, 0.0], test_date_index
        )
        value_start_series = self._to_decimal_series(
            [0.0, 1030.2, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0], test_date_index
        )
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate_return_per_period_percentage(
            test_date_index, value_start_series, return_per_period_series
        )

        testing.assert_series_equal(actual.astype(float), expected_series, check_names=False)

    def test_calculate_should_return_expected_series(self):
        test_date_index = date_range("2023-01-01", "2023-01-10")
        expected_is_open_series = Series([0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], index=test_date_index)
        expected_price_series = Series(
            [0.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0], index=test_date_index
        )
        expected_value_series = Series(
            [0.0, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], index=test_date_index
        )
        expected_return_per_period_series = Series(
            [0.0, -10.1, 20.3, 20.5, 31.1, 0.0, 0.0, 0.0, 0.0, 0.0], index=test_date_index
        )
        expected_return_per_period_percentage_series = Series(
            [0.0, -0.009803921569, 0.019900009803, 0.019703960015, 0.029314732774, 0.0, 0.0, 0.0, 0.0, 0.0],
            index=test_date_index,
        )
        self.calculator.load_calculation_requirements(self.test_position, self.test_fx_rates, self.test_prices)

        actual = self.calculator.calculate(test_date_index)

        testing.assert_series_equal(actual.is_open.astype(float), expected_is_open_series, check_names=False)
        testing.assert_series_equal(actual.price.astype(float), expected_price_series, check_names=False)
        testing.assert_series_equal(actual.value.astype(float), expected_value_series, check_names=False)
        testing.assert_series_equal(
            actual.return_per_period.astype(float), expected_return_per_period_series, check_names=False
        )
        testing.assert_series_equal(
            actual.return_per_period_percentage.astype(float),
            expected_return_per_period_percentage_series,
            check_names=False,
        )

    def _to_decimal_series(self, floats: list[float], reindex: DatetimeIndex):
        return Series([Decimal(str(f)) for f in floats], index=date_range("2023-01-01", "2023-01-10")).reindex(reindex)
