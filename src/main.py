import sys
from argparse import ArgumentParser

from controllers.main_controller import MainController


def main(arg_parser: ArgumentParser | None = None) -> str:
    parser = arg_parser or ArgumentParser(
        description="Calculate simplified financial metrics for a set of positions \
            over a specified time window."
    )

    parser.add_argument(
        "--positions-file",
        type=str,
        required=True,
        help="Path to the JSON file containing position data (e.g., \
            'tech-challenge-2025-positions.json').",
    )

    parser.add_argument(
        "--target-currency",
        type=str,
        help="The target currency (TC) for conversion (e.g., 'USD').",
        default="USD",
    )

    parser.add_argument(
        "--start-date",
        type=str,
        help="The start date of the time window (Format: YYYY-MM-DD).",
        default="2023-01-01",
    )

    parser.add_argument(
        "--end-date",
        type=str,
        help="The end date of the time window (Format: YYYY-MM-DD).",
        default="2024-11-10",
    )

    args = parser.parse_args()

    return MainController(
        args.positions_file, args.target_currency, args.start_date, args.end_date
    ).run()


if __name__ == "__main__":
    result = main()
    print(result)
    sys.exit()
    # try:
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)
