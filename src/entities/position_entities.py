def fx_rate(instrument_currency, target_currency, date):
    if instrument_currency == target_currency:
        return 1

    fx_rates = []  # get rates from api
    fx_rates_by_date = {
        item["date"]: item["rate"]
        for item in fx_rates[f"{instrument_currency}{target_currency}"]
    }

    return fx_rates_by_date[date]


def open_price_tc(instrument_currency, target_currency, open_price, open_date):
    return _market_price_tc(instrument_currency, target_currency, open_price, open_date)


def close_price_tc(instrument_currency, target_currency, close_price, close_date):
    return _market_price_tc(
        instrument_currency, target_currency, close_price, close_date
    )


def _market_price_tc(instrument_currency, target_currency, price, date):
    return price * fx_rate(instrument_currency, target_currency, date)


def price_lc(instrument_id, date, open_date):  # price_local
    if date < open_date:
        return 0

    instrument_currency_instrument_prices = []  # get prices from api
    instrument_price_by_date = {
        item["date"]: item["price"]
        for item in instrument_currency_instrument_prices[instrument_id]
    }

    return instrument_price_by_date[date]


def price_tc(instrument_currency, target_currency, instrument_id, date, open_date):
    price_local = price_lc(instrument_id, date, open_date)
    return _market_price_tc(instrument_currency, target_currency, price_local, date)


def quantity_position(date, open_date, close_date, quantity):
    if is_open_position(date, open_date, close_date):
        return quantity

    return 0


def quantity_basket(positions, date):
    return sum(
        [
            quantity_position(
                date,
                position["open_date"],
                position["close_date"],
                position["quantity"],
            )
            for position in positions
        ]
    )


def is_open_position(date, open_date, close_date):
    if date >= open_date and date < close_date:
        return True

    return False


def is_open_basket(positions, date):
    return any(
        is_open_position(date, p["open_date"], p["close_date"]) for p in positions
    )


def value_lc(instrument_id, date, open_date, close_date, quantity):
    return price_lc(instrument_id, date, open_date) * quantity_position(
        date, open_date, close_date, quantity
    )


def value_tc_position(
    instrument_currency,
    target_currency,
    instrument_id,
    date,
    open_date,
    close_date,
    quantity,
):
    return value_lc(instrument_id, date, open_date, close_date, quantity) * fx_rate(
        instrument_currency, target_currency, date
    )


def value_tc_basket(positions, target_currency, date):
    return sum(
        [
            value_tc_position(
                position["instrument_currency"],
                target_currency,
                position["instrument_id"],
                date,
                position["open_date"],
                position["close_date"],
                position["quantity"],
            )
            for position in positions
        ]
    )


def open_value_tc_position(
    instrument_currency, target_currency, open_price, date, open_date, quantity
):
    if date < open_date:
        return 0

    return (
        _market_price_tc(instrument_currency, target_currency, open_price, open_date)
        * quantity
    )


def open_value_tc_basket(positions, target_currency, date):
    return sum(
        [
            open_value_tc_position(
                position["instrument_currency"],
                target_currency,
                position["open_price"],
                date,
                position["open_date"],
                position["quantity"],
            )
            for position in positions
        ]
    )


def close_value_tc_position(
    instrument_currency, target_currency, close_price, date, close_date, quantity
):
    if date < close_date:
        return 0

    return (
        _market_price_tc(instrument_currency, target_currency, close_price, close_date)
        * quantity
    )


def close_value_tc_basket(positions, target_currency, date):
    return sum(
        [
            close_value_tc_position(
                position["instrument_currency"],
                target_currency,
                position["close_price"],
                date,
                position["close_date"],
                position["quantity"],
            )
            for position in positions
        ]
    )


def return_per_period_position(
    instrument_currency,
    target_currency,
    instrument_id,
    open_price,
    date,
    open_date,
    close_date,
    start_date,
    quantity,
    close_price,
):
    if date < open_date or date > close_date:
        return 0

    if date < close_date:
        value_tc_end = value_tc_position(
            instrument_currency,
            target_currency,
            instrument_id,
            date,
            open_date,
            close_date,
            quantity,
        )

    elif date == close_date:
        value_tc_end = close_value_tc_position(
            instrument_currency,
            target_currency,
            close_price,
            date,
            close_date,
            quantity,
        )

    return value_tc_end - value_tc_start(
        instrument_currency,
        target_currency,
        instrument_id,
        open_price,
        date,
        open_date,
        close_date,
        start_date,
        quantity,
    )


def value_tc_start(
    instrument_currency,
    target_currency,
    instrument_id,
    open_price,
    date,
    open_date,
    close_date,
    start_date,
    quantity,
):
    if date == open_date:
        return open_value_tc_position(
            instrument_currency, target_currency, open_price, date, open_date, quantity
        )
    if date == start_date:
        return value_tc_position(
            instrument_currency,
            target_currency,
            instrument_id,
            date,
            open_date,
            close_date,
            quantity,
        )
    if date > open_date and date > start_date:
        return value_tc_position(
            instrument_currency,
            target_currency,
            instrument_id,
            date - 1,
            open_date,
            close_date,
            quantity,
        )


def return_per_period_basket(positions, target_currency, start_date, date):
    return sum(
        [
            return_per_period_position(
                position["instrument_currency"],
                target_currency,
                position["instrument_id"],
                position["open_price"],
                date,
                position["open_date"],
                position["close_date"],
                start_date,
                position["quantity"],
                position["close_price"],
            )
            for position in positions
        ]
    )


def return_per_period_percentage_position(
    instrument_currency,
    target_currency,
    instrument_id,
    open_price,
    date,
    open_date,
    close_date,
    start_date,
    quantity,
    close_price,
):
    value_tc_st = value_tc_start(
        instrument_currency,
        target_currency,
        instrument_id,
        open_price,
        date,
        open_date,
        close_date,
        start_date,
        quantity,
    )
    if value_tc_st == 0:
        return 0

    return (
        return_per_period_position(
            instrument_currency,
            target_currency,
            instrument_id,
            open_price,
            date,
            open_date,
            close_date,
            start_date,
            quantity,
            close_price,
        )
        / value_tc_st
    )


def return_per_period_percentage_basket(positions, target_currency, start_date, date):
    total_rpp = sum(
        return_per_period_position(
            p["instrument_currency"],
            target_currency,
            p["instrument_id"],
            p["open_price"],
            date,
            p["open_date"],
            p["close_date"],
            start_date,
            p["quantity"],
            p["close_price"],
        )
        for p in positions
    )

    total_value_start = sum(
        value_tc_start(
            p["instrument_currency"],
            target_currency,
            p["instrument_id"],
            p["open_price"],
            date,
            p["open_date"],
            p["close_date"],
            start_date,
            p["quantity"],
        )
        for p in positions
    )

    if total_value_start == 0:
        return 0
    return total_rpp / total_value_start
