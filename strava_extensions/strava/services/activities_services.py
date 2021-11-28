from strava_extensions.strava.api import StravaAPI


def get_club_activities(club_id: int):
    strava_api = StravaAPI()

    return strava_api.get_club_activities(club_id)
