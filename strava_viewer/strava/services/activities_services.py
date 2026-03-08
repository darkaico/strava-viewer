import json
import time

from strava_viewer.strava import settings
from strava_viewer.strava.api import StravaAPI
from strava_viewer.strava.credentials import get_strava_credentials
from strava_viewer.strava.schemas import SummaryActivitySchema
from strava_viewer.strava.utils.redis_client import get_redis_client

CACHE_KEY_ATHLETE = "strava:activities"
CACHE_KEY_CLUB_PREFIX = "strava:activities:club:"
CACHE_KEY_PATTERN = "strava:activities*"


def _parse_cached_activities(raw: str):
    """Deserialize cached JSON into list of SummaryActivity."""
    if not raw:
        return []
    data = json.loads(raw)
    return SummaryActivitySchema(many=True).load(data)


def _get_cache_key_club(club_id: int) -> str:
    return f"{CACHE_KEY_CLUB_PREFIX}{club_id}"


def get_club_activities(club_id, credentials=None):
    """Return club feed activities. Only when club_id is set and valid."""
    if club_id is None:
        return []
    creds = credentials or get_strava_credentials()
    if not creds:
        return []
    club_id_int = int(club_id)
    redis_client = get_redis_client()
    cache_key = _get_cache_key_club(club_id_int)
    if settings.STRAVA_ACTIVITIES_CACHE_ENABLED:
        cached = redis_client.get(cache_key)
        if cached is not None:
            return _parse_cached_activities(cached)
    strava_api = StravaAPI(credentials=creds)
    json_activities = strava_api.get_club_activities_raw(club_id_int)
    if settings.STRAVA_ACTIVITIES_CACHE_ENABLED and json_activities is not None:
        redis_client.set(
            cache_key,
            json.dumps(json_activities),
            ex=settings.STRAVA_ACTIVITIES_CACHE_TTL_SECONDS,
        )
    return SummaryActivitySchema(many=True).load(json_activities or [])


def get_activities_for_view(club_id=None, days=90, per_page=200, credentials=None):
    """
    Return activities for the list and dashboard.
    Uses athlete activities (last `days`) as primary so data shows without a club.
    When club_id is set, returns club activities instead for club-feed behavior.
    Requires credentials (from get_strava_credentials or passed in).
    """
    creds = credentials or get_strava_credentials()
    if not creds:
        return []
    if club_id is not None:
        return get_club_activities(club_id=club_id, credentials=creds)
    redis_client = get_redis_client()
    if settings.STRAVA_ACTIVITIES_CACHE_ENABLED:
        cached = redis_client.get(CACHE_KEY_ATHLETE)
        if cached is not None:
            return _parse_cached_activities(cached)
    strava_api = StravaAPI(credentials=creds)
    after_epoch = int(time.time()) - (days * 24 * 60 * 60)
    json_activities = strava_api.get_athlete_activities_raw(after=after_epoch, per_page=per_page)
    if settings.STRAVA_ACTIVITIES_CACHE_ENABLED and json_activities is not None:
        redis_client.set(
            CACHE_KEY_ATHLETE,
            json.dumps(json_activities),
            ex=settings.STRAVA_ACTIVITIES_CACHE_TTL_SECONDS,
        )
    return SummaryActivitySchema(many=True).load(json_activities or [])


def clear_activities_cache():
    """Delete all activities cache keys so the next request fetches fresh data."""
    redis_client = get_redis_client()
    if hasattr(redis_client, "scan_iter"):
        keys = list(redis_client.scan_iter(match=CACHE_KEY_PATTERN))
        if keys:
            redis_client.delete(*keys)
    else:
        redis_client.delete(CACHE_KEY_ATHLETE)
