import os
from unittest.mock import patch

from repositories.enviroment_loader import EnvironmentLoader


class TestEnvironmentLoader:
    @patch.dict(
        os.environ,
        {
            "PERFORMATIV_API_URL": "",
            "PERFORMATIV_CANDIDATE_ID": "",
            "PERFORMATIV_API_KEY": "",
            "VALUE_PRECISION": "",
        },
    )
    def test_environment_loader_when_env_not_set_must_return_expected(self):
        config = EnvironmentLoader()

        assert config.PERFORMATIV_API_URL == ""
        assert config.PERFORMATIV_CANDIDATE_ID == ""
        assert config.PERFORMATIV_API_KEY == ""
        assert config.VALUE_PRECISION == 8

    @patch.dict(
        os.environ,
        {
            "PERFORMATIV_API_URL": "http://test",
            "PERFORMATIV_CANDIDATE_ID": "id-1234",
            "PERFORMATIV_API_KEY": "api-1234",
            "VALUE_PRECISION": "10",
        },
    )
    def test_environment_loader_when_invoked_must_return_expected_message(self):
        config = EnvironmentLoader()

        assert config.PERFORMATIV_API_URL == "http://test"
        assert config.PERFORMATIV_CANDIDATE_ID == "id-1234"
        assert config.PERFORMATIV_API_KEY == "api-1234"
        assert config.VALUE_PRECISION == 10
