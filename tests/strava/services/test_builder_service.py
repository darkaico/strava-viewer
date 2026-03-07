from strava_viewer.strava.services.builder_service import BuilderService


def test_club_activity_builder(json_club_activities):
    models = BuilderService.build_summary_activities(json_club_activities)

    assert len(models) == 3
    assert models[0].athlete.firstname == "Ariel"
