import pytest
import requests


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
