import os
from dotenv import load_dotenv


load_dotenv()


class EnvironmentLoader:
    PERFORMATIV_API_URL = os.environ.get("PERFORMATIV_API_URL", "")
    PERFORMATIV_CANDIDATE_ID = os.environ.get("PERFORMATIV_CANDIDATE_ID", "")
    PERFORMATIV_API_KEY = os.environ.get("PERFORMATIV_API_KEY", "")


config = EnvironmentLoader()
