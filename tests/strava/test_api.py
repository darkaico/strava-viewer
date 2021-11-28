from unittest.mock import patch

import pytest
import requests

from tests.conftest import MockResponse


def test_get_club_activities_empty(strava_api, api_empty_result):

    activities = strava_api.get_club_activities(4)

    assert len(activities) == 0


def test_get_club_activities(strava_api, api_with_activities):

    activities = strava_api.get_club_activities(4)

    assert len(activities) == 3


def test_get_club_activities_client_error(strava_api, api_http_error_400):

    with pytest.raises(requests.exceptions.HTTPError):
        strava_api.get_club_activities(4)


@patch("strava_extensions.strava.api.StravaAPI._refresh_token")
@patch.object(requests, "get")
def test_get_club_activities_unauthorized(mock_get, mock_refresh_token, strava_api):
    mock_get.side_effect = [MockResponse(401), MockResponse(200, [])]

    activities = strava_api.get_club_activities(0)

    mock_refresh_token.assert_called()
    assert len(activities) == 0


def test_get_club_activities_response_error(strava_api, api_with_invalid_activities):

    activities = strava_api.get_club_activities(4)

    assert len(activities) == 0


@patch.object(requests, "post")
def test_get_access_token_call_refresh_success(mock_post, strava_api_no_token):
    def mockresponse(url, data):
        return MockResponse(
            200,
            json_response={
                "token_type": "Bearer",
                "access_token": "c5c2b6c96aab27e3248c033c465aa38f6eb1bc89",
                "expires_at": 1638047169,
                "expires_in": 20363,
                "refresh_token": "ca112f576c8fc8546c7537865fca6ca71929c416",
            },
        )

    mock_post.side_effect = mockresponse

    access_token = strava_api_no_token.get_access_token()

    assert access_token == "c5c2b6c96aab27e3248c033c465aa38f6eb1bc89"


@patch.object(requests, "post")
def test_get_access_token_call_refresh_fails(mock_post, strava_api_no_token):
    def mockresponse(url, data):
        return MockResponse(400)

    mock_post.side_effect = mockresponse

    with pytest.raises(requests.exceptions.HTTPError):
        strava_api_no_token.get_access_token()
