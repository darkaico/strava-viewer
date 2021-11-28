from strava_extensions.strava.services.activities_services import get_club_activities


def test_get_club_activities(strava_api, api_with_activities):

    activities = get_club_activities(2)

    assert len(activities) == 3
    assert activities[0].name == "Workout"
    assert activities[0].athlete.firstname == "Ariel"
    assert activities[1].name == "🖐🏻"
    assert activities[1].athlete.firstname == "Jeff"
    assert activities[2].name == "Afternoon Ride"
    assert activities[2].athlete.firstname == "German"
