import pytest

from strava_viewer.strava.models.activities import SummaryActivity


@pytest.fixture
def club_activity():
    return SummaryActivity(
        athlete={},
        resource_state=0,
        name="Ariel",
        distance=0.0,
        moving_time=10,
        elapsed_time=4,
        total_elevation_gain=2.4,
        activity_type="Run",
    )


def test_materialize_icon(club_activity):
    assert club_activity.materialize_icon == "directions_run"


def test_materialize_icon_default(club_activity):
    club_activity.activity_type = "adamantium"

    assert club_activity.materialize_icon == "local_play"
