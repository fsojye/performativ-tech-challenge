import os

from dotenv import load_dotenv

load_dotenv(override=False)


class EnvironmentLoader:
    def __init__(self) -> None:
        self.PERFORMATIV_API_URL = os.environ.get("PERFORMATIV_API_URL", "")
        self.PERFORMATIV_CANDIDATE_ID = os.environ.get("PERFORMATIV_CANDIDATE_ID", "")
        self.PERFORMATIV_API_KEY = os.environ.get("PERFORMATIV_API_KEY", "")
        self.VALUE_PRECISION = int(os.environ.get("VALUE_PRECISION") or 8)


config = EnvironmentLoader()
