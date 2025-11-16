import json

from pydantic import ValidationError

from models.positions_data import PositionsData


class PositionsDataRepo:
    def __init__(self, path_to_positions_file: str):
        self.path_to_positions_file = path_to_positions_file

    def get(self) -> PositionsData:
        try:
            with open(self.path_to_positions_file, "r", encoding="utf-8") as file:
                return PositionsData.model_validate({"positions": json.load(file)})
        except FileNotFoundError as e:
            raise PositionDataRepoException(f"Positions file not found: {self.path_to_positions_file}") from e
        except json.JSONDecodeError as e:
            raise PositionDataRepoException(f"Failed to load from: {self.path_to_positions_file}") from e
        except ValidationError as e:
            raise PositionDataRepoException(f"Failed to deserialize: {self.path_to_positions_file}") from e
        except Exception as e:
            raise PositionDataRepoException(str(e)) from e


class PositionDataRepoException(Exception):
    pass
