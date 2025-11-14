from enum import Enum


class PositionDayValuationFields(str, Enum):
    OPEN_PRICE_TARGET = "open_price_target"
    CLOSE_PRICE_TARGET = "close_price_target"
    PRICE_LOCAL = "price_local"
    PRICE_TARGET = "price_target"
    QUANTITY = "quantity"
    IS_OPEN = "is_open"
    VALUE_LOCAL = "value_local"
    VALUE_TARGET = "value_target"
    OPEN_VALUE_TARGET = "open_value_target"
    CLOSE_VALUE_TARGET = "close_value_target"
    VALUE_START_TARGET = "value_start_target"
    VALUE_END_TARGET = "value_end_target"
    RETURN_PER_PERIOD = "return_per_period"
    RETURN_PER_PERIOD_PERCENTAGE = "return_per_period_percentage"
