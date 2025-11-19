from decimal import Decimal

from numpy import nan
from pandas import DatetimeIndex, Series, date_range

from entities.financial_metrics import PositionMetric
from services.basket_calculator import BasketCalculator


class TestBasketCalculator:
    def test_calculate_should_return_expected(self):
        calculator = BasketCalculator()
        test_date_index = date_range("2023-01-01", "2023-01-10")
        test_is_open_series = [
            [0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
        expected_is_open_series = [0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        test_value_series = [
            [0.0, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [nan, 0.0, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
        expected_value_series = [0.0, 2040.2, 3100.9, 3162.2, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0]
        test_value_start_series = [
            [0.0, 1030.2, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1030.2, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, nan, 1030.2, 1020.1, 1040.4, 1060.9, 0.0, 0.0, 0.0, 0.0],
        ]
        test_return_per_period_series = [
            [0.0, -10.1, 20.3, 20.5, 31.1, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, -10.1, 20.3, 20.5, 31.1, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, -10.1, 20.3, 20.5, 31.1, 0.0, 0.0, 0.0, 0.0],
        ]
        expected_return_per_period_series = [0.0, -20.2, 30.5, 61.3, 82.7, 31.1, 0.0, 0.0, 0.0, 0.0]
        test_return_per_period_percentage_series = [
            [0.0, -0.009803921569, 0.019900009803, 0.019703960015, 0.029314732774, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, -0.009803921569, 0.019900009803, 0.019703960015, 0.029314732774, 0.0, 0.0, 0.0, 0.0, 0.0],
            [nan, 0.0, -0.009803921569, 0.019900009803, 0.019703960015, 0.029314732774, 0.0, 0.0, 0.0, 0.0],
        ]
        expected_return_per_period_percentage_series = [
            0.0,
            -0.00980392156862745,
            0.009933559145388224,
            0.019768454319713632,
            0.02615267851495794,
            0.02931473277405976,
            0.0,
            0.0,
            0.0,
            0.0,
        ]

        for i in range(0, 4):
            calculator.add_to_basket(
                PositionMetric(
                    is_open=self._to_decimal_series(test_is_open_series[i], test_date_index),
                    price=self._to_decimal_series([0] * 10, test_date_index),
                    value=self._to_decimal_series(test_value_series[i], test_date_index),
                    value_start=self._to_decimal_series(test_value_start_series[i], test_date_index),
                    return_per_period=self._to_decimal_series(test_return_per_period_series[i], test_date_index),
                    return_per_period_percentage=self._to_decimal_series(
                        test_return_per_period_percentage_series[i], test_date_index
                    ),
                )
            )

        actual = calculator.calculate()

        assert actual.is_open.astype(float).to_list() == expected_is_open_series
        assert actual.price.astype(float).to_list() == [0.0] * 10
        assert actual.value.astype(float).to_list() == expected_value_series
        assert actual.return_per_period.astype(float).to_list() == expected_return_per_period_series
        assert (
            actual.return_per_period_percentage.astype(float).to_list() == expected_return_per_period_percentage_series
        )

    def _to_decimal_series(self, floats: list[float], date_index: DatetimeIndex) -> Series[Decimal]:
        return Series([Decimal(str(f)) for f in floats], index=date_index)
