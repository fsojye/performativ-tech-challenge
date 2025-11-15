import json
import os


class PositionsFileLoader:
    def load(self, path_to_positions_file: str) -> list[dict[str, str]]:
        try:
            return self._load(path_to_positions_file)
        except Exception as e:
            raise PositionsFileLoaderException(
                f"Error encountered while loading positions file "
                f"[{path_to_positions_file}]: {str(e)}"
            ) from e

    def _load(self, path_to_positions_file: str) -> list[dict[str, str]]:
        if not os.path.exists(path_to_positions_file):
            raise PositionsFileLoaderException("File does not exist")

        with open(path_to_positions_file, "r") as f:
            positions_data: list[dict[str, str]] = json.load(f)

        return positions_data


class PositionsFileLoaderException(Exception):
    pass
