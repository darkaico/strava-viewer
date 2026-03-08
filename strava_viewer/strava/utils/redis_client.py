"""Redis client with optional no-op when REDIS_URL is unset."""

import time

import redis

from strava_viewer.strava import settings


class _NoOpRedis:
    """In-memory stub when Redis is not configured.
    Supports get/set/delete/exists for access-token usage.
    When ex is passed to set(), values expire so cache TTL works without Redis.
    """

    def __init__(self):
        self._store = {}  # key -> value (no TTL)
        self._expiry = {}  # key -> expiry timestamp (seconds since epoch)

    def get(self, key):
        if key not in self._store:
            return None
        if key in self._expiry and time.time() > self._expiry[key]:
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return None
        return self._store.get(key)

    def set(self, key, value, ex=None):
        self._store[key] = value
        if ex is not None:
            self._expiry[key] = time.time() + ex
        else:
            self._expiry.pop(key, None)

    def delete(self, *keys):
        for k in keys:
            self._store.pop(k, None)
            self._expiry.pop(k, None)

    def exists(self, key):
        if key not in self._store:
            return 0
        if key in self._expiry and time.time() > self._expiry[key]:
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return 0
        return 1

    def scan_iter(self, match=None, count=None):
        """Yield keys; match='strava:activities*' means startswith 'strava:activities'."""
        now = time.time()
        for key in list(self._store):
            if key in self._expiry and now > self._expiry[key]:
                self._store.pop(key, None)
                self._expiry.pop(key, None)
                continue
            if match is None:
                yield key
            elif match.endswith("*") and key.startswith(match[:-1]):
                yield key


def get_redis_client():
    if not settings.REDIS_URL:
        return _NoOpRedis()
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
