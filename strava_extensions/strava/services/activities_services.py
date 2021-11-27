import os

from strava_extensions.strava.api import StravaAPI

STRAVA_API_ACCESS_TOKEN = os.getenv("STRAVA_API_ACCESS_TOKEN")


def get_club_activities(club_id: int = None):
    if not club_id:
        club_id = os.getenv("STRAVA_CLUB_ID")

    strava_api = StravaAPI(STRAVA_API_ACCESS_TOKEN)

    return strava_api.get_club_activities(club_id)
