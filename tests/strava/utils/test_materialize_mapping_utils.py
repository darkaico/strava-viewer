from strava_viewer.strava.utils import materialize_mapping_utils


def test_get_icon_for_valid_activity():

    assert materialize_mapping_utils.get_icon_by_activity("Run") == "directions_run"


def test_get_default_icon_no_activity():

    assert materialize_mapping_utils.get_icon_by_activity("Alienizing") == "local_play"
