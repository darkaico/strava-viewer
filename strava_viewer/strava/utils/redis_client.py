"""Redis client with optional no-op when REDIS_URL is unset."""

import redis

from strava_viewer.strava import settings


class _NoOpRedis:
    """In-memory stub when Redis is not configured.
    Supports get/set/delete/exists for access-token usage.
    """

    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value, ex=None):
        self._store[key] = value

    def delete(self, *keys):
        for k in keys:
            self._store.pop(k, None)

    def exists(self, key):
        return 1 if key in self._store else 0


def get_redis_client():
    if not settings.REDIS_URL:
        return _NoOpRedis()
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
