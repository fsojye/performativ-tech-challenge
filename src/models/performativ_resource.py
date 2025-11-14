from dataclasses import dataclass


@dataclass
class PerformativResource:
    fx_rates: dict[str, dict[str, str]]
    prices: dict[str, dict[str, str]]
