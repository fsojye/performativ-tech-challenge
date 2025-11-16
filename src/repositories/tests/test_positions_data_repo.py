import json
from unittest.mock import mock_open, patch

import pytest

from models.positions_data import PositionsData
from repositories.positions_data_repo import (
    PositionDataRepoException,
    PositionsDataRepo,
)


@patch("builtins.open")
class TestPositionsDataRepo:
    MOCK_FILE = "path/to/positions.json"

    @pytest.fixture(autouse=True)
    def setup(self):
        self.repo = PositionsDataRepo(self.MOCK_FILE)

    def test_get_when_file_not_found_should_raise_exception_message(self, mock_file_open):
        mock_file_open.side_effect = [
            FileNotFoundError(),
            mock_open(read_data=b"dummy code").return_value,
        ]

        with pytest.raises(PositionDataRepoException) as ex:
            self.repo.get()

        assert f"Positions file not found: {self.MOCK_FILE}" in str(ex.value)

    @patch("json.load")
    def test_get_when_json_load_failed_should_raise_exception_message(self, mock_json_load, mock_file_open):
        mock_file_open.new_callable = mock_open
        mock_json_load.side_effect = json.JSONDecodeError("msg", "doc", 0)

        with pytest.raises(PositionDataRepoException) as ex:
            self.repo.get()

        assert f"Failed to load from: {self.MOCK_FILE}" in str(ex.value)

    @patch("json.load")
    def test_get_when_deserialize_failed_should_raise_exception_message(self, mock_json_load, mock_file_open):
        mock_file_open.new_callable = mock_open
        mock_json_load.return_value = {"position": []}

        with pytest.raises(PositionDataRepoException) as ex:
            self.repo.get()

        assert f"Failed to deserialize: {self.MOCK_FILE}" in str(ex.value)

    @patch("json.load")
    def test_get_when_generic_exception_should_raise_exception_message(self, mock_json_load, mock_file_open):
        mock_file_open.new_callable = mock_open
        mock_json_load.side_effect = Exception("Generic error")

        with pytest.raises(PositionDataRepoException) as ex:
            self.repo.get()

        assert "Generic error" in str(ex.value)

    @patch("json.load")
    def test_get_when_valid_file_data_should_return_expected_deserialized_object(self, mock_json_load, mock_file_open):
        mock_file_open.new_callable = mock_open
        mock_json_load.return_value = [
            {
                "id": 1,
                "open_date": "2023-01-01",
                "close_date": "2023-12-31",
                "open_price": 100.5,
                "close_price": 105.75,
                "quantity": 10,
                "instrument_id": 1001,
                "instrument_currency": "USD",
            },
            {
                "id": 2,
                "open_date": "2023-12-31",
                "close_date": "2024-01-31",
                "open_price": 105.75,
                "close_price": 100,
                "quantity": 10,
                "instrument_id": 1002,
                "instrument_currency": "EUR",
            },
        ]
        actual = self.repo.get()

        assert isinstance(actual, PositionsData)
        assert len(actual.positions) == 2
        assert set(map(lambda p: p.id, actual.positions)) == {1, 2}
        assert set(map(lambda p: p.instrument_id, actual.positions)) == {1002, 1001}
