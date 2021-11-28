from dataclasses import dataclass, field
from typing import Optional

import pytest
import requests

from strava_extensions.strava.utils import redis_client
from tests.fixtures import loaders


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

    def set(self, key, value, exp=None):
        self.storage[key] = value

    def get(self, key):
        return self.storage.get(key)

    def exists(self, key):
        return key in self.storage


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    """Mock Redis client during tests."""
    mocker.patch.object(redis_client, "get_redis_client", return_value=MockRedis())


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
