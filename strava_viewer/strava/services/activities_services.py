import time

from strava_viewer.strava.api import StravaAPI


def get_club_activities(club_id):
    """Return club feed activities. Only when club_id is set and valid."""
    if club_id is None:
        return []
    strava_api = StravaAPI()
    return strava_api.get_club_activities(int(club_id))


def get_activities_for_view(club_id=None, days=90, per_page=200):
    """
    Return activities for the list and dashboard.
    Uses athlete activities (last `days`) as primary so data shows without a club.
    When club_id is set, returns club activities instead for club-feed behavior.
    """
    strava_api = StravaAPI()
    if club_id is not None:
        return strava_api.get_club_activities(int(club_id))
    after_epoch = int(time.time()) - (days * 24 * 60 * 60)
    return strava_api.get_athlete_activities(after=after_epoch, per_page=per_page)
