import redis

from strava_viewer.strava import settings


def get_redis_client():
    return redis.Redis.from_url(settings.REDIS_URL)
