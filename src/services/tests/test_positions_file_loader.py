from unittest.mock import mock_open, patch

import pytest

from services.positions_file_loader import (
    PositionsFileLoader,
    PositionsFileLoaderException,
)


class TestPositionsFileLoader:
    positions_file_loader = PositionsFileLoader()

    @patch("os.path.exists")
    def test_load_when_file_does_not_exist_should_raise_expected_exception(
        self, mock_path_exists
    ):
        mock_path_exists.return_value = False

        with pytest.raises(PositionsFileLoaderException) as ex:
            self.positions_file_loader.load("path/to/positions/file")

        assert "File does not exist" in str(ex)
        assert (
            "Error encountered while loading positions file [path/to/positions/file]:"
            in str(ex)
        )

    @patch("json.load")
    @patch("builtins.open")
    @patch("os.path.exists")
    def test_load_when_json_deserialization_fails_should_raise_expected_exception(
        self, mock_path_exists, mock_file_open, mock_json_load
    ):
        mock_path_exists.return_value = True
        mock_file_open.new_callable = mock_open
        mock_json_load.side_effect = Exception("Deserialization failed")

        with pytest.raises(PositionsFileLoaderException) as ex:
            self.positions_file_loader.load("path/to/positions/file")

        assert "Deserialization failed" in str(ex)
        assert (
            "Error encountered while loading positions file [path/to/positions/file]:"
            in str(ex)
        )

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"id": 1, "name": "Alice"}]',
    )
    @patch("os.path.exists")
    def test_load_when_json_deserialization_success_should_return_expected_value(
        self, mock_path_exists, _
    ):
        mock_path_exists.return_value = True

        actual = self.positions_file_loader.load("path/to/positions/file")

        assert actual == [{"id": 1, "name": "Alice"}]
