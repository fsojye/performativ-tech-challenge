from unittest.mock import patch

import pytest

from main import main


@patch("main.MainController")
class TestMain:
    def test_main_when_called_without_positions_file_should_raise_system_exit(
        self, mock_main_controller, capsys
    ):
        expected_error_message = (
            "the following arguments are required: --positions-file"
        )
        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert expected_error_message in captured.err
        mock_main_controller.run.assert_not_called()

    def test_main_when_called_without_optional_arguments_should_set_to_default(
        self, mock_main_controller
    ):
        main(["--positions-file", "data.json"])

        mock_main_controller.assert_called_once_with(
            "data.json", "USD", "2023-01-01", "2024-11-10"
        )
        mock_main_controller.return_value.run.assert_called_once()

    def test_main_when_called__arguments_should_set_to_expected_arguments(
        self, mock_main_controller
    ):
        args = [
            "--positions-file",
            "data.json",
            "--target-currency",
            "EUR",
            "--start-date",
            "2023-06-01",
            "--end-date",
            "2024-06-01",
        ]

        main(args)

        mock_main_controller.assert_called_once_with(
            "data.json", "EUR", "2023-06-01", "2024-06-01"
        )
        mock_main_controller.return_value.run.assert_called_once()
