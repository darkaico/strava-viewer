import os

# Ensure production SECRET_KEY check does not run during tests
os.environ.setdefault("FLASK_DEBUG", "true")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key")

from dataclasses import dataclass, field  # noqa: E402
from typing import Optional  # noqa: E402

import pytest  # noqa: E402
import redis  # noqa: E402
import requests  # noqa: E402

from strava_viewer.strava.api import StravaAPI  # noqa: E402
from tests.fixtures import loaders  # noqa: E402


@dataclass
class MockResponse:

    status_code: int
    json_response: Optional[dict] = field(default_factory=dict)

    def json(self):
        return self.json_response

    def raise_for_status(self):
        raise requests.exceptions.HTTPError()


class MockRedis:
    def __init__(self):
        self.storage = {}

    def set(self, key, value, ex=None):
        self.storage[key] = value

    def get(self, key):
        return self.storage.get(key)

    def exists(self, key):
        return key in self.storage

    def delete(self, key):
        self.storage.pop(key, None)


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    """Mock Redis client during tests."""
    mocker.patch.object(redis.Redis, "from_url", return_value=MockRedis())


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """No requests allowed during tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture
def json_club_activities():
    return loaders.load_club_activities()


@pytest.fixture
def json_invalid_club_activities():
    return loaders.load_invalid_club_activities()


@pytest.fixture
def json_club_activity():
    return loaders.load_valid_club_activity()


@pytest.fixture
def strava_api(monkeypatch, mock_redis):
    def mock_access_token(self):
        return "access-token"

    monkeypatch.setattr(StravaAPI, "get_access_token", mock_access_token)

    return StravaAPI()


@pytest.fixture
def strava_api_no_token(monkeypatch, mock_redis):

    return StravaAPI()


@pytest.fixture
def api_empty_result(mocker):
    def mockreturn(url, params=None):
        return MockResponse(200, [])

    mocker.patch.object(requests, "get", mockreturn)


@pytest.fixture
def api_with_activities(mocker, json_club_activities):
    def mockreturn(url, params=None):
        return MockResponse(200, json_club_activities)

    mocker.patch.object(requests, "get", mockreturn)


@pytest.fixture
def api_with_invalid_activities(mocker, json_invalid_club_activities):
    def mockreturn(url, params=None):
        return MockResponse(200, json_invalid_club_activities)

    mocker.patch.object(requests, "get", mockreturn)


@pytest.fixture
def api_http_error_400(mocker):
    def mockreturn(url, params=None):
        return MockResponse(400)

    mocker.patch.object(requests, "get", mockreturn)


@pytest.fixture
def api_http_error_401(mocker):
    def mockreturn(url, params=None):
        return MockResponse(401)

    mocker.patch.object(requests, "get", mockreturn)
