from strava_viewer.strava.services.activities_services import (
    get_activities_for_view,
    get_club_activities,
)


def test_get_club_activities_none_returns_empty():
    assert get_club_activities(None) == []


def test_get_club_activities(strava_api, api_with_activities, mock_strava_credentials):
    activities = get_club_activities(2)

    assert len(activities) == 3
    assert activities[0].name == "Workout"
    assert activities[0].athlete.firstname == "Ariel"
    assert activities[1].name == "🖐🏻"
    assert activities[1].athlete.firstname == "Jeff"
    assert activities[2].name == "Afternoon Ride"
    assert activities[2].athlete.firstname == "German"


def test_get_activities_for_view_with_club_id(
    strava_api, api_with_activities, mock_strava_credentials
):
    activities = get_activities_for_view(club_id=2)
    assert len(activities) == 3
    assert activities[0].name == "Workout"


def test_get_activities_for_view_without_club_id(
    strava_api, api_with_activities, mock_strava_credentials
):
    activities = get_activities_for_view(club_id=None)
    assert len(activities) == 3
