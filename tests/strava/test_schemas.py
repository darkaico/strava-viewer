from strava_viewer.strava.schemas import SummaryActivitySchema


def test_summary_activities_deserialize(json_club_activities):
    activities = SummaryActivitySchema(many=True).load(json_club_activities)
    assert len(activities) == 3
    assert activities[0].athlete.firstname == "Ariel"
