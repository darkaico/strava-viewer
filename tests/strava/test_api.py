import pytest
import requests

from strava_extensions.strava.api import StravaAPI
from tests.conftest import MockResponse


@pytest.fixture
def strava_api(monkeypatch, mock_redis):
    def mock_access_token(self):
        return "access-token"

    monkeypatch.setattr(StravaAPI, "get_access_token", mock_access_token)

    return StravaAPI()


@pytest.fixture
def api_empty_result(monkeypatch):
    def mockreturn(url, params=None):
        return MockResponse(200, [])

    monkeypatch.setattr(requests, "get", mockreturn)


@pytest.fixture
def api_with_activities(monkeypatch, json_club_activities):
    def mockreturn(url, params=None):
        return MockResponse(200, json_club_activities)

    monkeypatch.setattr(requests, "get", mockreturn)


@pytest.fixture
def api_with_invalid_activities(monkeypatch, json_invalid_club_activities):
    def mockreturn(url, params=None):
        return MockResponse(200, json_invalid_club_activities)

    monkeypatch.setattr(requests, "get", mockreturn)


@pytest.fixture
def api_http_error(monkeypatch):
    def mockreturn(url, params=None):
        return MockResponse(400)

    monkeypatch.setattr(requests, "get", mockreturn)


def test_get_club_activities_empty(strava_api, api_empty_result):

    activities = strava_api.get_club_activities(4)

    assert len(activities) == 0


def test_get_club_activities(strava_api, api_with_activities):

    activities = strava_api.get_club_activities(4)

    assert len(activities) == 3


def test_get_club_activities_http_error(strava_api, api_http_error):

    with pytest.raises(requests.exceptions.HTTPError):
        strava_api.get_club_activities(4)


def test_get_club_activities_response_error(strava_api, api_with_invalid_activities):

    activities = strava_api.get_club_activities(4)

    assert len(activities) == 0
