import redis

from strava_extensions.strava import settings


def get_redis_client():
    return redis.Redis.from_url(settings.REDIS_URL)
